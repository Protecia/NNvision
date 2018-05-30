# -*- coding: utf-8 -*-
"""
Created on Sat Feb  3 11:58:19 2018

@author: julien

Main script to process the camera images
"""
import logging
import os
import sys
import time
import pytz
from django.conf import settings
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler
from collections import Counter
from twilio.rest import Client
from django.core.mail import send_mail


# Your Account SID from twilio.com/console
account_sid = "AC445238ce002d1c440c77883963183c04"
# Your Auth Token from twilio.com/console
auth_token  = "97c36acf2c85e62436181e878305f982"

client = Client(account_sid, auth_token)


#------------------------------------------------------------------------------
# Because this script have to be run in a separate process from manage.py
# you need to set up a Django environnement to use the Class defined in
# the Django models. It is necesssary to interact witht the Django database
#------------------------------------------------------------------------------
# to get the projet.settings it is necessary to add the parent directory
# to the python path
try:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
except NameError:
    sys.path.append(os.path.abspath('..'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "projet.settings")
import django
django.setup()

from app1.models import Profile, Result, Object, Alert, Info, Alert_when
#from django.contrib.auth.models import User

#------------------------------------------------------------------------------
# a simple config to create a file log - change the level to warning in
# production
#------------------------------------------------------------------------------
level= logging.WARNING
logger = logging.getLogger()
logger.setLevel(level)
formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
file_handler = RotatingFileHandler(os.path.join(settings.BASE_DIR,'alert.log'), 'a', 10000000, 1)
file_handler.setLevel(level)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
#stream_handler = logging.StreamHandler()
#stream_handler.setLevel(level)
#logger.addHandler(stream_handler)
#------------------------------------------------------------------------------


class Process_alert(object):
    def __init__(self):
        self.user = Profile.objects.filter(alert=True).select_related()
        self.info = Info.objects.get(pk=1)
        self.running=True
        self.result = Result.objects.all().last()
        self.dict_alert = {}
        alert = Alert.objects.filter(active = True)
        for a in alert :
            a.active = False
            a.save()

    def wait(self,_time):
        i=0
        wait=True
        while wait:
            logger.info('start waiting for no detection : {}s'.format(i))
            rn = Result.objects.all().last()
            if rn.id == self.result.id :
                i+=1
            else :
                i=0
                self.result = Result.objects.all().last()
            time.sleep(1)
            if i>_time : 
                wait=False
                logger.info('waiting {} s, end loop'.format(_time))

    def warn(self, alert):
        t = datetime.now(pytz.utc)
        logger.debug('warn in action at {} / alert timer is {} / timedelta : {}'.format(t
                    ,alert.when,t-alert.when))
        logger.debug('sms : {} / call : {} / alarm : {} / mail : {}'.format(
                alert.sms,alert.call,alert.alarm,alert.mail))
        
        for a in self.dict_alert[alert]:
            if not a[1] and t>a[2] :
                a[0](alert,t)
                a[1]=1
                return
            
    def send_mail(self, alert,t):
        list_mail = []
        for u in self.user :
            list_mail.append(u.user.email)
        sender ="contact@protecia.com"
        body = " A {} just {}. Check the image : {} - {}".format(Alert.stuffs_d[alert.stuffs],
                   Alert.actions_d[alert.actions], self.info.public_site+'/warning', t.astimezone(pytz.timezone('Europe/Paris')))
        send_mail('Subject here',body, sender,list_mail,fail_silently=False,)
        logger.warning('mail send to : {}'.format(list_mail))
        Alert_when(what='mail').save()
            
    def send_sms(self, alert,t):
        for u in self.user :
            to = u.phone_number
            sender ="+33757916187"
            body = " A {} just {}. Check the image : {} - {}".format(Alert.stuffs_d[alert.stuffs],
                       Alert.actions_d[alert.actions], self.info.public_site, t.astimezone(pytz.timezone('Europe/Paris')))
            client.messages.create(to=to, from_=sender,body=body)
            logger.warning('sms send to : {}'.format(to))
        Alert_when(what='sms').save()
                



    def run(self,_time):
        while(self.running):
            #get last objects
            o = Object.objects.filter(result=self.result)
            c = Counter([i.result_object for i in o])
            logger.info('getting last object : {}'.format(c))

            # Is there new result
            rn = Result.objects.filter(pk__gt=self.result.id)
            for r in rn:
                logger.info('new result in databases : {}'.format(r))
                on = Object.objects.filter(result=r)
                cn = Counter([i.result_object for i in on])
                logger.debug('getting objects in databases : {}'.format(cn))
                
                appear = cn-c
                for s in appear :
                    a=False
                    object_appear = Alert.stuffs_reverse.get(s)
                    if object_appear :
                        a = Alert.objects.filter(stuffs=object_appear, 
                                             actions=Alert.actions_reverse['appear']).first()
                        logger.info('appear alert : {}'.format(a))
                    if a : 
                        r.alert= True
                        r.save()
                        if not a.active:
                            t = datetime.now(pytz.utc)
                            a.active = True
                            a.when = t
                            a.save()
                            list_action = []
                            if a.alarm :
                                list_action.append([self.send_alarm,0,t])                                
                            if a.mail :
                                list_action.append([self.send_mail,0,t])
                                t = t+timedelta(seconds=30)
                            if a.sms :
                                list_action.append([self.send_sms,0,t])
                                t = t+timedelta(seconds=30)
                            if a.call :
                                list_action.append([self.send_call,0,t])
                            if a.mass_alarm :
                                t = t+timedelta(seconds=150)
                                if a.mail :
                                    list_action.append([self.send_mass_mail,0,t])
                                    t = t+timedelta(seconds=60)
                                if a.sms :
                                    list_action.append([self.send_mass_sms,0,t])
                                    t = t+timedelta(seconds=60)
                                if a.call :
                                    list_action.append([self.send_mass_call,0,t])
                            self.dict_alert[a]=list_action
                            logger.debug('new list_action : {}'.format(list_action))                    
                disappear = c-cn
                for s in disappear:
                    a=False
                    object_disappear = Alert.stuffs_reverse.get(s)
                    if object_disappear :
                        a = Alert.objects.filter(stuffs=object_disappear, 
                                             actions=Alert.actions_reverse['disappear']).first()
                        logger.info('disappear alert : {}'.format(a))
                    if a : 
                        r.alert= True
                        r.save()
                        if not a.active:
                            t = datetime.now(pytz.utc)
                            a.active = True
                            a.when = t
                            a.save()
                            list_action = []
                            if a.alarm :
                                list_action.append([self.send_alarm,0,t])                                
                            if a.mail :
                                list_action.append([self.send_mail,0,t])
                                t = t+timedelta(seconds=30)
                            if a.sms :
                                list_action.append([self.send_sms,0,t])
                                t = t+timedelta(seconds=30)
                            if a.call :
                                list_action.append([self.send_call,0,t])
                            if a.mass_alarm :
                                t = t+timedelta(seconds=150)
                                if a.mail :
                                    list_action.append([self.send_mass_mail,0,t])
                                    t = t+timedelta(seconds=60)
                                if a.sms :
                                    list_action.append([self.send_mass_sms,0,t])
                                    t = t+timedelta(seconds=60)
                                if a.call :
                                    list_action.append([self.send_mass_call,0,t])
                            self.dict_alert[a]=list_action
                            logger.debug('new list_action : {}'.format(list_action))
                logger.debug('dict alert is : {}'.format(self.dict_alert))
                self.result = r
            
            alert = Alert.objects.filter(active = True)
            for a in alert :
                self.warn(a)
            time.sleep(_time)


def main():
    process_alert=Process_alert()
    print("Waiting...")
    process_alert.wait(30)
    print("Alert are running !")
    try:
        process_alert.run(1)
    except KeyboardInterrupt:
        print("Bye bye!")


# start the threads
if __name__ == '__main__':
    main()
    

    




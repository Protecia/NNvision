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
import glob
from django.conf import settings
from datetime import datetime
from logging.handlers import RotatingFileHandler
from collections import Counter
from twilio.rest import Client
from django.core.mail import send_mail
from django.db import DatabaseError
from socket import gaierror


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

from app1.models import Profile, Result, Object, Alert, Alert_when

# Your Account SID from twilio.com/console
account_sid = settings.ACCOUNT_SID
# Your Auth Token from twilio.com/console
auth_token  = settings.AUTH_TOKEN

client = Client(account_sid, auth_token)
#from django.contrib.auth.models import User

#------------------------------------------------------------------------------
# a simple config to create a file log - change the level to warning in
# production
#------------------------------------------------------------------------------
if settings.DEBUG : 
    level=logging.DEBUG
else:
    level=logging.WARNING
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
def old(query):
    if query is not None :
        return query.when
    else:
        return datetime(2000,1,1)
    
    
def TryCatch(func):
    def wrapper(*args, **kwargs):
        try:
           func(*args,**kwargs)
        except DatabaseError :
           logger.warning('>>>>>>>>> Error in database <<<<<<<<<<<')
    return wrapper



def purge_files():
    r = Result.objects.all().order_by('time')
    if len(r)>0 :
        r = r[0]
        time_older = r.time.timestamp()
        path = settings.MEDIA_ROOT+'/'+r.file1.name.split('/')[0]
        os.chdir(path)
        for file in glob.glob("*.jpg"):
             if os.path.getctime(file) < time_older :
                 os.remove(file)
        path = settings.MEDIA_ROOT+'/'+r.file2.name.split('/')[0]
        os.chdir(path)
        for file in glob.glob("*.jpg"):
             if os.path.getctime(file) < time_older :
                 os.remove(file)

@TryCatch
def check_space(mo):
        ##### check the space on disk to avoid filling the sd card #######
        sb = os.statvfs(settings.MEDIA_ROOT)
        sm = sb.f_bavail * sb.f_frsize / 1024 / 1024
        logger.info('space left is  {} MO'.format(sm))
        while sm < mo :
            r_to_delete = Result.objects.all()[:300]
            for im_d in r_to_delete:
                if 'jpg' in  im_d.file1.name :
                    im_d.file1.delete()
                if 'jpg' in  im_d.file2.name :
                    im_d.file2.delete()
                im_d.delete()
            sb = os.statvfs(settings.MEDIA_ROOT)
            sm = sb.f_bavail * sb.f_frsize / 1024 / 1024
            logger.info('new space space left after delete is  {} MO'.format(sm))
        ###################################################################  

class Process_alert(object):
    def __init__(self):
        self.user = Profile.objects.filter(alert=True).select_related()
        self.public_site = settings.PUBLIC_SITE
        self.running=True
        self.result = Result.objects.all().last()
        alert = Alert.objects.filter(active = True)
        for a in alert :
            a.active = False
            a.save()

    
    @TryCatch    
    def wait(self,_time):
        i=0
        wait=True
        while wait:
            check_space(300)
            logger.info('start waiting for no detection : {}s'.format(i))
            rn = Result.objects.all().last()
            if rn == None:
                i+=1
            elif rn.id == self.result.id :
                i+=1
            else :
                i=0
                self.result = Result.objects.all().last()
            time.sleep(1)
            if i>_time : 
                wait=False
                logger.info('waiting {} s, end loop'.format(_time))

#-------------------- this function send alert when necessary ----------------------------
    # alert is retrieve from models.Alert
    def warn(self, alert):
        t = datetime.now(pytz.utc)
        logger.debug('warn in action at {} / alert timer is {} / timedelta : {}'.format(t
                    ,alert.when,t-alert.when))
        logger.debug('sms : {} / call : {} / alarm : {} / mail : {}'.format(
                alert.sms,alert.call,alert.alarm,alert.mail))
        if alert.mail :
            if alert.mail_delay < t-alert.when:
                last = old(Alert_when.objects.filter(what='mail').last())
                if t-last > alert.mail_resent :
                    logger.debug('>>>>>>> go to send mail <<<<<<<<<<<')
                    self.send_mail(alert,t)
        if alert.sms :
            if alert.sms_delay < t-alert.when:
                last = old(Alert_when.objects.filter(what='sms').last())
                if t-last > alert.sms_resent :
                    logger.debug('>>>>>>> go to send sms <<<<<<<<<<<')
                    self.send_sms(alert,t)
#############################################################################################
                    
            
            
            
    def send_mail(self, alert,t):
        list_mail = []
        for u in self.user :
            list_mail.append(u.user.email)
        sender ="contact@protecia.com"
        body = " A {} just {}. Check the image : {} - {}".format(Alert.stuffs_d[alert.stuffs],
                   Alert.actions_d[alert.actions], self.public_site+'/warning/0', t.astimezone(pytz.timezone('Europe/Paris')))
        try:
            send_mail('Subject here',body, sender,list_mail,fail_silently=False,)
        except gaierror:
            logger.warning('socket gaierror !!!! :')
            pass
        logger.warning('mail send to : {}'.format(list_mail))
        Alert_when(what='mail', who=list_mail).save()
            
    def send_sms(self, alert,t):
        for u in self.user :
            to = u.phone_number
            sender ="+33757916187"
            body = " A {} just {}. Check the image : {} - {}".format(Alert.stuffs_d[alert.stuffs],
                       Alert.actions_d[alert.actions], self.public_site, t.astimezone(pytz.timezone('Europe/Paris')))
            client.messages.create(to=to, from_=sender,body=body)
            logger.warning('sms send to : {}'.format(to))
            Alert_when(what='sms', who=to).save()
                



    def run(self,_time):
        while(self.running):
            check_space(300)   
            #get last objects
            o = Object.objects.filter(result=self.result)
            c = Counter([i.result_object for i in o])
            logger.info('getting last object : {}'.format(c))

            # Is there new result
            rn = Result.objects.filter(pk__gt=getattr(self.result,'id',0))
            for r in rn:
                logger.info('new result in databases : {}'.format(r))
                on = Object.objects.filter(result=r)
                
                cn = Counter([i.result_object for i in on])
                logger.debug('getting objects in databases : {}'.format(cn))
                
                for s in cn :
                    a=False
                    object_present = Alert.stuffs_reverse.get(s)
                    if object_present :
                        a = Alert.objects.filter(stuffs=object_present, 
                                             actions=Alert.actions_reverse['present']).first()
                    if a :
                        logger.info('present alert : {}'.format(a))
                        r.alert= True
                        r.save()
                        t = r.time
                        if not a.active:
                            a.active = True
                            a.when = t
                            a.save()           
                
                appear = cn-c
                for s in appear :
                    a=False
                    object_appear = Alert.stuffs_reverse.get(s)
                    if object_appear :
                        a = Alert.objects.filter(stuffs=object_appear, 
                                             actions=Alert.actions_reverse['appear']).first()    
                    if a :
                        logger.info('appear alert : {}'.format(a))
                        r.alert= True
                        r.save()
                        t = r.time
                        if not a.active:
                            a.active = True
                            a.when = t
                            a.save()
                                 
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
                        t = r.time
                        if not a.active:
                            a.active = True
                            a.when = t
                            a.save()
                            
                self.result = r
            
            alert = Alert.objects.filter(active = True)
            for a in alert :
                self.warn(a)
            time.sleep(_time)


def main():
    purge_files()
    sb = os.statvfs(settings.MEDIA_ROOT)
    sm = sb.f_bavail * sb.f_frsize / 1024 / 1024
    logger.warning('space left is  {} MO'.format(sm))
    check_space(300)
    process_alert=Process_alert()
    print("Waiting...")
    process_alert.wait(settings.WAIT_BEFORE_DETECTION)
    print("Alert are running !")
    try:
        process_alert.run(1)
    except KeyboardInterrupt:
        print("Bye bye!")


# start the threads
if __name__ == '__main__':
    main()
    

    



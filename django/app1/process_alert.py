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
from datetime import datetime, timedelta, timezone
from logging.handlers import RotatingFileHandler
from collections import Counter
from twilio.rest import Client


# Your Account SID from twilio.com/console
account_sid = "AC445238ce002d1c440c77883963183c04"
# Your Auth Token from twilio.com/console
auth_token  = "97c36acf2c85e62436181e878305f982"

client = Client(account_sid, auth_token)



#------------------------------------------------------------------------------
# a simple config to create a file log - change the level to warning in
# production
#------------------------------------------------------------------------------
level= logging.INFO
logger = logging.getLogger()
logger.setLevel(level)
formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
file_handler = RotatingFileHandler('alert.log', 'a', 10000000, 1)
file_handler.setLevel(level)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
#stream_handler = logging.StreamHandler()
#stream_handler.setLevel(level)
#logger.addHandler(stream_handler)

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

from app1.models import Profile, Camera, Result, Object, Alert, Info
#from django.contrib.auth.models import User

#------------------------------------------------------------------------------

    
class Process_alert(object):
    def __init__(self):
        self.user = Profile.objects.filter(alert=True)
        self.info = Info.objects.get(pk=1)
        self.running=True
        self.result = Result.objects.all().last()
        
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
        t = datetime.now(timezone.utc)
        if alert.sms and t-alert.when>timedelta(minutes=5):
            for u in self.user :
                t = datetime.now()
                to = u.phone_number
                sender ="+33757916187"
                body = " A {} just {}. Check the image : {} - {}".format(Alert.stuffs_d[alert.stuffs],
                           Alert.actions_d[alert.actions], self.info.public_site, t)
                client.messages.create(to, sender,body)
                logger.info('sms send to : {}').format(to)
                
        if alert.call:
            pass
        if alert.alarm:
            pass
        if alert.patrol:
            pass        
        
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
                    a = Alert.objects.get(stuffs=Alert.stuffs_reverse[s], 
                                             actions=Alert.actions_reverse['appear'])
                    logger.info('new appear alert : {}'.format(a))
                    self.warn(a)
                disappear = c-cn
                for s in disappear:
                    a = Alert.objects.get(stuffs=Alert.stuffs_reverse[s], 
                                             actions=Alert.actions_reverse['disappear'])
                    logger.info('new disappear alert : {}'.format(a))
                    self.warn(a)
                self.result = r
            time.sleep(_time)
    
    
def main():
    process_alert=Process_alert()
    process_alert.wait(30)
    try:
        process_alert.run(3)        
    except KeyboardInterrupt:
        print("Bye bye!")
    
    
# start the threads
if __name__ == '__main__':
    main()
    

    




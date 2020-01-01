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
from twilio.rest import Client as Client_twilio
from django.core.mail import EmailMessage
from django.utils.translation import gettext as _
from django.utils.translation import activate 
#from django.db import DatabaseError
from socket import gaierror
from twilio.base.exceptions import TwilioRestException
from django.db.models import Count

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

from app1.models import Profile, Result, Object, Alert, Alert_when, Alert_type, Camera

# Your Account SID from twilio.com/console
account_sid = settings.ACCOUNT_SID
# Your Auth Token from twilio.com/console
auth_token  = settings.AUTH_TOKEN
client_tw = Client_twilio(account_sid, auth_token)

#------------------------------------------------------------------------------
# a simple config to create a file log - change the level to warning in
# production
#------------------------------------------------------------------------------
if __name__ == '__main__':
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
#------------------------------------------------------------------------------
def old(query):
    if query is not None :
        return query.when
    else:
        return datetime(2000,1,1,tzinfo=pytz.utc)
    

           
class Process_alert(object):
    def __init__(self, client):
        self.user = Profile.objects.filter(alert=True, client=client).select_related()
        self.public_site = settings.PUBLIC_SITE
        self.running=True
        self.result = Result.objects.filter(camera__client=client).last()
        self.client = client
        alert = Alert.objects.filter(active = True, camera__client=self.client).annotate(c=Count('camera'))
        for a in alert :
            a.active = False
            a.save()
        # case where present alert is on at the launch
        cam = Camera.objects.filter(active=True, client=client)
        for c in cam:
            result = Result.objects.filter(camera=c).last()  
            o = Object.objects.filter(result=result)
            c = Counter([i.result_object for i in o])
            logger.info('getting last object init : {}'.format(c))
            self.check_alert(result, 'present',c)
            
    def check_alert(self, result, alert_type, object_counter):
            for s in object_counter :
                    a=False
                    object_present = Alert.stuffs_reverse.get(s)
                    if object_present :
                        a = Alert.objects.filter(stuffs=object_present, 
                                                 actions=Alert.actions_reverse[alert_type],
                                                 camera=result.camera).first()
                    if a :
                        logger.info(alert_type+' alert : {}'.format(a))
                        result.alert= True
                        result.save()
                        a.img_name = result.file2.name
                        a.last = result.time
                        a.save()
                        if not a.active:
                            a.active = True
                            a.when = result.time
                            a.save()
    
    def wait(self,_time):
        i=0
        wait=True
        while wait:
            logger.info('start waiting for no detection : {}s'.format(i))
            rn = Result.objects.filter(camera__client=self.client).last()
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
        list_alert = Alert_type.objects.filter(client=self.client).order_by('priority')
        post_wait = timedelta(seconds=0)
        for l in list_alert:
            if getattr(alert,l.allowed) :
                if l.delay + post_wait < t-alert.when:
                    last = old(Alert_when.objects.filter(client = self.client,
                                                         what=l.allowed, 
                                                         stuffs=alert.stuffs,
                                                         action=alert.actions).last())
                    if t-last > l.resent :
                        logger.debug('>>>>>>> go to send {} <<<<<<<<<<<'.format(l.allowed))
                        self.send(alert, l.allowed, self.user,  t)
                post_wait = l.post_wait
            else :
                post_wait = timedelta(seconds=0)
                    
#############################################################################################
                    
    def send(self, alert, canal, user, t):
        if canal == 'mail':
            activate(settings.USER_LANGUAGE)
            list_mail = []
            for u in user :
                list_mail.append(u.user.email)
            sender ="contact@protecia.com"
            body = _("Origin of detection") +"  : {}".format(Alert.stuffs_d[alert.stuffs])+"   ---  "+_("Type of detection")+" :  {}".format(Alert.actions_d[alert.actions])
            body += "<br>"+_("Time of detection")+" : {:%d-%m-%Y - %H:%M:%S}".format(alert.last.astimezone(pytz.timezone(settings.TIME_ZONE)))
            body += "<br>"+_("Please check the images")+" : {} ".format(self.public_site+'/warning/0')
            try:
                message = EmailMessage( 'Protecia Alert !!!',
                                        body,
                                        sender,
                                        list_mail)
                message.content_subtype = "html"
                message.attach_file(settings.MEDIA_ROOT+'/'+alert.img_name)
                message.send(fail_silently=False,)
            except (gaierror, FileNotFoundError) :
                logger.warning('Error in send_mail !!!! :')
                pass
            logger.warning('mail send to : {}'.format(list_mail))
            Alert_when(what='mail', who=list_mail, stuffs=alert.stuffs, action=alert.actions).save()
            activate('en')
            
        if canal == 'sms':
            activate(settings.USER_LANGUAGE)
            for u in user :
                to = u.phone_number
                sender ="+33757916187"
                body = _("Origin of detection") +"  : {}".format(Alert.stuffs_d[alert.stuffs])+"   ---  "+_("Type of detection")+" :  {}".format(Alert.actions_d[alert.actions])
                body += "\n"+_("Time of detection")+" : {:%d-%m-%Y - %H:%M:%S}".format(t.astimezone(pytz.timezone(settings.TIME_ZONE)))
                body += "n"+_("Please check the images")+" : {} ".format(self.public_site+'/warning/0')
                try:
                    client_tw.messages.create(to=to, from_=sender,body=body)
                except TwilioRestException:
                    pass
                client_tw.messages.create(to=to, from_=sender,body=body)
                logger.warning('sms send to : {}'.format(to))
                Alert_when(what='sms', who='to', stuffs=alert.stuffs, action=alert.actions).save()
            activate('en')
    
    def run(self,_time):
        while(self.running):
            #get last objects
            o = Object.objects.filter(result=self.result)
            c = Counter([i.result_object for i in o])
            logger.info('getting last object : {}'.format(c))   
            # Is there new result
            rn = Result.objects.filter(pk__gt=getattr(self.result,'id',0), camera__client=self.client)
            for r in rn:
                logger.info('new result in databases : {}'.format(r))
                on = Object.objects.filter(result=r)
                cn = Counter([i.result_object for i in on])
                logger.debug('getting objects in databases : {}'.format(cn))
                # case "is present"
                self.check_alert(r, 'present',cn)
                # case : "appear"
                appear = cn-c
                self.check_alert(r, 'appear',appear)
                # case : disappear                 
                disappear = c-cn
                self.check_alert(r, 'disappear',disappear)
                self.result = r
            alert = Alert.objects.filter(active = True, camera__client=self.client).annotate(c=Count('camera'))
            for a in alert :
                self.warn(a)
            time.sleep(_time)

def main():
    client = sys.argv[0]
    activate('en')
    process_alert=Process_alert(client)
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

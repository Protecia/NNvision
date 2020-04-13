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
import requests
import json
import xml.etree.ElementTree as ET
from django.conf import settings
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler
from collections import Counter
from twilio.rest import Client
from django.core.mail import EmailMessage
from django.utils.translation import gettext as _
from django.utils.translation import activate 
#from django.db import DatabaseError
from socket import gaierror
from twilio.base.exceptions import TwilioRestException

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

from app1.models import Profile, Result, Object, Alert, Alert_when, Alert_info, Camera, Alert_adam, Alert_hook

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
#stream_handler = logging.StreamHandler()
#stream_handler.setLevel(level)
#logger.addHandler(stream_handler)
#------------------------------------------------------------------------------
def old(query):
    if query is not None :
        return query.when
    else:
        return datetime(2000,1,1,tzinfo=pytz.utc)
    

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

def stop_adam_all():
    logger = logging.getLogger()
    adam_request = Alert_adam.objects.all()
    for adam_box in adam_request :
        cmd = 'http://'+adam_box.ip+'/digitaloutput/all/value'
        data = 'DO0=0&DO1=0&DO2=0&DO3=0&DO4=0&DO5=0'
        try:
            r = requests.post(cmd, auth=(adam_box.auth,adam_box.password), headers={"content-type":"text"}, data=data, timeout=2)
            if r.status_code == 200:
                logger.debug('adam stopped with request : {} {} {} {}'.format(cmd,adam_box.auth,adam_box.password,data))
        except requests.exceptions.ConnectionError:
            logger.warning('adam not responding on ip : {}'.format(adam_box.ip))
            pass
        time.sleep(0.5)
        
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
        # case where present alert is on at the launch
        cam = Camera.objects.filter(active=True)
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
            check_space(settings.SPACE_LEFT)
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
        delay = Alert_info.objects.get()
        t = datetime.now(pytz.utc)
        logger.debug('warn in action at {} / alert timer is {} / timedelta : {}'.format(t
                    ,alert.when,t-alert.when))
        logger.debug('sms : {} / call : {} / alarm : {} / mail : {}'.format(
                alert.sms,alert.call,alert.alarm,alert.mail))
        
        if alert.mail :
            if delay.mail_delay < t-alert.when:
                last = old(Alert_when.objects.filter(what='mail', 
                                                     stuffs=alert.stuffs,
                                                     action=alert.actions).last())
                if t-last > delay.mail_resent :
                    logger.debug('>>>>>>> go to send mail <<<<<<<<<<<')
                    self.send_mail(alert)
            mail_post_wait = delay.mail_post_wait
        else :
            mail_post_wait = timedelta(seconds=0)
       
        if alert.sms :
            if delay.sms_delay + mail_post_wait  < t-alert.when:
                last = old(Alert_when.objects.filter(what='sms', 
                                                     stuffs=alert.stuffs,
                                                     action=alert.actions).last())
                if t-last > delay.sms_resent :
                    logger.debug('>>>>>>> go to send sms <<<<<<<<<<<')
                    self.send_sms(alert,t)
            sms_post_wait = delay.sms_post_wait
        else :
            sms_post_wait = timedelta(seconds=0)
                    
        if alert.adam is not None :
            if alert.adam.delay < t-alert.when:
                logger.debug('>>>>>>> go to active adam <<<<<<<<<<<')
                
                last = old(Alert_when.objects.filter(what='adam', 
                                                     stuffs=alert.stuffs,
                                                     action=alert.actions).last())
                if last < alert.when :
                    self.start_adam(alert,t, {0 : alert.adam_channel_0,
                                                          1 : alert.adam_channel_1,
                                                          2 : alert.adam_channel_2,
                                                          3 : alert.adam_channel_3,
                                                          4 : alert.adam_channel_4,
                                                          5 : alert.adam_channel_5})
                else :
                    if t-last > alert.adam.duration :
                        logger.debug('>>>>>>> go to inactive adam <<<<<<<<<<<')
                        self.stop_adam(alert,t, {0 : alert.adam_channel_0,
                                                             1 : alert.adam_channel_1,
                                                             2 : alert.adam_channel_2,
                                                             3 : alert.adam_channel_3,
                                                             4 : alert.adam_channel_4,
                                                             5 : alert.adam_channel_5})
                    
        if alert.hook:
            hook_request = Alert_hook.objects.all()
            for hook in hook_request:
                if hook.delay < t-alert.when:
                    logger.debug('>>>>>>> go to send hook <<<<<<<<<<<')
                    last = old(Alert_when.objects.filter(what='hook', 
                                                     stuffs=alert.stuffs,
                                                     action=alert.actions).last())
                    if t-last > hook.resent :
                        logger.debug('>>>>>>> go to send hook <<<<<<<<<<<')
                        self.send_hook(alert,hook, t)        
#############################################################################################
                    
    def send_mail(self, alert):
        activate(settings.USER_LANGUAGE)
        list_mail = []
        for u in self.user :
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
            
    def send_sms(self, alert,t):
        activate(settings.USER_LANGUAGE)
        for u in self.user :
            to = u.phone_number
            sender ="+33757916187"
            body = _("Origin of detection") +"  : {}".format(Alert.stuffs_d[alert.stuffs])+"   ---  "+_("Type of detection")+" :  {}".format(Alert.actions_d[alert.actions])
            body += "\n"+_("Time of detection")+" : {:%d-%m-%Y - %H:%M:%S}".format(t.astimezone(pytz.timezone(settings.TIME_ZONE)))
            body += "n"+_("Please check the images")+" : {} ".format(self.public_site+'/warning/0')
            try:
                client.messages.create(to=to, from_=sender,body=body)
            except TwilioRestException:
                pass
            client.messages.create(to=to, from_=sender,body=body)
            logger.warning('sms send to : {}'.format(to))
            Alert_when(what='sms', who='to', stuffs=alert.stuffs, action=alert.actions).save()
        activate('en')
    
    def start_adam(self, alert, t, channel):
        cmd = 'http://'+alert.adam.ip+'/digitaloutput/all/value'
        try:
            r = requests.get(cmd, auth=(alert.adam.auth,alert.adam.password), headers={"content-type":"text"}, timeout=2)
        except requests.exceptions.ConnectionError :
            logger.warning('adam not responding on ip : {}'.format(alert.adam.ip))
            return
        xml = ET.fromstring(r.text)
        adam_state = {}
        for state in xml.findall('DO'):
            state.find('ID').text
            adam_state[int(state.find('ID').text)]=state.find('VALUE').text
        for nb,c in channel.items() :
            if c :
                adam_state[nb] = '1'
        data = ''
        for i in adam_state:
            data += "DO"+str(i)+"="+adam_state[i]+"&"
        try:    
            r = requests.post(cmd, auth=(alert.adam.auth,alert.adam.password), headers={"content-type":"text"}, data=data, timeout=2)
            if r.status_code == 200:
                logger.warning('adam started on ip : {}'.format(alert.adam.ip))
                logger.debug('with request : {} {} {} {}'.format(cmd,alert.adam.auth,alert.adam.password,data))
                Alert_when(what='adam', who='', stuffs=alert.stuffs, action=alert.actions).save()       
        except requests.exceptions.ConnectionError :
            logger.warning('adam not responding on ip : {}'.format(alert.adam.ip))
            pass
        time.sleep(0.5)
       
    def stop_adam(self, alert, t, channel):
        cmd = 'http://'+alert.adam.ip+'/digitaloutput/all/value'
        try:
            r = requests.get(cmd, auth=(alert.adam.auth,alert.adam.password), headers={"content-type":"text"}, timeout=2)
        except requests.exceptions.ConnectionError :
            logger.warning('adam not responding on ip : {}'.format(alert.adam.ip))
            return
        xml = ET.fromstring(r.text)
        adam_state = {}
        for state in xml.findall('DO'):
            state.find('ID').text
            adam_state[int(state.find('ID').text)]=state.find('VALUE').text
        for nb,c in channel.items() :
            if c :
                adam_state[nb] = '0'
        data = ''
        for i in adam_state:
            data += "DO"+str(i)+"="+adam_state[i]+"&" 
        try:
            r = requests.post(cmd, auth=(alert.adam.auth,alert.adam.password), headers={"content-type":"text"}, data=data, timeout=2)
            if r.status_code == 200:
                logger.warning('adam stop on ip : {}'.format(alert.adam.ip))
                logger.debug('with request : {} {} {} {}'.format(cmd,alert.adam.auth,alert.adam.password,data))
        except requests.exceptions.ConnectionError :
            logger.warning('adam not responding on ip : {}'.format(alert.adam.ip))
            pass
        time.sleep(0.5)
        
    def send_hook(self,alert,hook,t):
        url = hook.url
        data = {'object': str(Alert.stuffs_d[alert.stuffs]), 'action': str(Alert.actions_d[alert.actions]), 'time':alert.when.strftime("%m/%d/%Y, %H:%M:%S")}
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        try:
            r = requests.post(url, data=json.dumps(data), headers=headers, timeout=2)
            if r.status_code == 200:
                logger.warning('hook send to : {}'.format(url))
                logger.debug('with data : {}'.format(data))
                Alert_when(what='hook', who=url, stuffs=alert.stuffs, action=alert.actions).save() 
        except requests.exceptions.ConnectionError :
            logger.warning('hook not responding on url : {}'.format(url))
            pass

    def run(self,_time):
           
        while(self.running):
            check_space(settings.SPACE_LEFT)   
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
                # case "is present"
                self.check_alert(r, 'present',cn)
                # case : "appear"
                appear = cn-c
                self.check_alert(r, 'appear',appear)
                # case : disappear                 
                disappear = c-cn
                self.check_alert(r, 'disappear',disappear)
                self.result = r
            alert = Alert.objects.filter(active = True)
            for a in alert :
                self.warn(a)
            time.sleep(_time)

def main():
    activate('en')
    purge_files()
    sb = os.statvfs(settings.MEDIA_ROOT)
    sm = sb.f_bavail * sb.f_frsize / 1024 / 1024
    logger.warning('space left is  {} MO'.format(sm))
    check_space(settings.SPACE_LEFT)
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

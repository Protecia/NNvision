# -*- coding: utf-8 -*-
"""
Created on Sun Nov 11 20:48:43 2018

@author: julien
"""
import os
import psutil as ps
import time
import sys
from subprocess import Popen
from django.conf import settings

action = sys.argv[1]
try:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
except NameError:
    sys.path.append(os.path.abspath('..'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "projet.settings")


def process():
    _process = [[],[]]
    for p in ps.process_iter():
        try :
            for n in p.cmdline():
                if 'process_camera' in n : _process[0].append(p)
                if 'process_alert' in n : _process[1].append(p)
        except ps.AccessDenied :
            pass
    return _process

if action == 'stop':
    while 1 :
        p = process()
        [ item.kill() for sublist in p for item in sublist]
        time.sleep(2)
        if len(p[0])==0 and len(p[1])==0:
            break
    
if action == 'start':
    #Camera.objects.all().update(rec=True)
    if len(process()[0])==0:       
        Popen([settings.PYTHON,os.path.join(settings.BASE_DIR,'app1/process_camera.py')])
    if len(process()[1])==0:
        Popen([settings.PYTHON,os.path.join(settings.BASE_DIR,'app1/process_alert.py')]) 
    time.sleep(2)
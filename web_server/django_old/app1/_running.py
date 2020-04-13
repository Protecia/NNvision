# -*- coding: utf-8 -*-
"""
Created on Sun Nov 11 20:48:43 2018

@author: julien
"""
import os
import psutil as ps
import time
import sys
from subprocess import Popen, STDOUT
from django.conf import settings

action = sys.argv[1]
folder = sys.argv[2]

try:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
except NameError:
    sys.path.append(os.path.abspath('..'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "projet.settings")
import django
django.setup()
from app1.models import Client
client = Client.objects.get(folder=folder)


def process(key):
    for p in ps.process_iter():
        try :
            for n in p.cmdline():
                if key in n :
                    return p
        except ps.AccessDenied :
            pass
    return False

if action == 'stop':
    while 1 :
        try :
            process(client.key).kill()
        except AttributeError:
            pass
        client.change = True
        client.rec =  False
        client.save()
        time.sleep(2)
        if not process(client.key) :
            break
    
if action == 'start' and not process(client.key):
    if settings.DEBUG:
        with open(os.path.join(settings.BASE_DIR,'process_alert.log'), 'w') as loga:
            Popen([settings.PYTHON,os.path.join(settings.BASE_DIR,'app1/process_alert.py'), client.key],
                  stdout=loga, stderr=STDOUT)
    else:
        Popen([settings.PYTHON,os.path.join(settings.BASE_DIR,'app1/process_alert.py'),client.key])
    client.change = True
    client.rec =  True
    client.save()
    time.sleep(2)
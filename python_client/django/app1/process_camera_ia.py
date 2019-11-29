# -*- coding: utf-8 -*-
"""
Created on Sat Jun  1 06:55:46 2019

@author: julien
"""
import sys
import os
import logging
from logging.handlers import RotatingFileHandler
from django.conf import settings



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
file_handler = RotatingFileHandler(os.path.join(settings.BASE_DIR,'camera.log'), 'a', 10000000, 1)
file_handler.setLevel(level)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
#stream_handler = logging.StreamHandler()
#stream_handler.setLevel(level)
#logger.addHandler(stream_handler)

#------------------------------------------------------------------------------

from app1.models import Result, Object, Camera
from app1.darknet_python import darknet as dn


def event(NbCam):
    global nb_cam
    global event_list
    nb_cam = NbCam
    event_list = []
    for i in range(nb_cam):
        event_list.append(Event())

def network():
    global net
    global meta
    path = settings.DARKNET_PATH
    cfg = os.path.join(path,settings.CFG).encode()
    weights = os.path.join(path,settings.WEIGHTS).encode()
    data = os.path.join(path,settings.DATA).encode()
    net = dn.load_net(cfg,weights, 0)
    meta = dn.load_meta(data)

detect = dn.detect

# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 14:39:29 2020

@author: julien
"""
import logging
import os
import sys
from datetime import datetime
from django.conf import settings
from logging.handlers import RotatingFileHandler
import time
import pytz

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

from app1.models import Client

def main(period):
    while True :
        for client in Client.objects.all():
            time_gap = datetime.now(pytz.utc)-client.timestamp
            time_from_last_connection = time_gap.seconds
            if time_from_last_connection > 60 :
                logger.warning('Client {} is not connected'.format(client.name))
                client.connected = False
                client.save()
            else :
                client.connected= True
                client.save()
        time.sleep(20)

# start the process
if __name__ == '__main__':
    ####### log #######
    if settings.DEBUG :
        level=logging.DEBUG
    else:
        level=logging.WARNING
    logger = logging.getLogger('client_connection')
    logger.setLevel(level)
    formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
    file_handler = RotatingFileHandler(os.path.join(settings.BASE_DIR,'log','telegram.log'), 'a', 10000000, 1)
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    ####################
    main(20)

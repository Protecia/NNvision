# -*- coding: utf-8 -*-
"""
Created on Sat Feb  3 11:58:19 2018

@author: julien

Main script to process the camera images
"""
import time
import logging
import requests
import os
import sys


from threading import Thread, Lock, Event
from logging.handlers import RotatingFileHandler
from scipy.misc import imread
from io import BytesIO
from django.core.files import File


#------------------------------------------------------------------------------
# a simple config to create a file log - change the level to warning in
# production
#------------------------------------------------------------------------------
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
file_handler = RotatingFileHandler('camera.log', 'a', 1000000, 1)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
logger.addHandler(stream_handler)

#------------------------------------------------------------------------------
# Because this script have to be run in a separate process from manage.py
# you need to set up a Django environnement to use the Class defined in
# the Django models. It is necesssary to interact witht the Django database
#------------------------------------------------------------------------------
# to get the projet.settings it is necessary to add the parent directory
# to the python path
try:
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
except NameError:
    sys.path.append(os.path.abspath('..'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "projet.settings")
import django
django.setup()

from app1.models import Camera, Result
from app1.darknet_python import darknet as dn
#------------------------------------------------------------------------------

# locking process to avoid threads calling darknet more than once at a time
lock = Lock()

class ProcessCamera(Thread):

    """Thread used to grab camera images and process the image with darknet"""

    def __init__(self, cam, event_list, nb_cam):
        Thread.__init__(self)
        self.cam = cam
        self.event_list = event_list
        self.cam_id = cam.id-1
        self.nb_cam = nb_cam
        self.running = False
 
    def run(self):
        """code run when the thread is started"""
        self.running = True
        while self.running :
            r = requests.get(self.cam.url, auth=(self.cam.username,
                                                 self.cam.password
                                                 ), stream=True)
            if r.status_code == 200:
                img_bytes = BytesIO(r.content)
                arr = imread(img_bytes)
                im = dn.array_to_image(arr)
                logger.debug('image ready for darknet :  {} '.format(im))
                self.event_list[self.cam_id].wait()
                self.event_list[(self.cam_id-1)%self.nb_cam].clear()
                logger.debug('cam {} alive and cam {} clear'.format(
                self.cam_id,(self.cam_id-1)%self.nb_cam))
                # attention il semble qu'il faille clear tous les autres threads
                with lock:
                   result_darknet = dn.detect2(net, meta, im)
                   logger.debug('get result from darknet : {}\n'.format(
                   result_darknet))
                                   
                for j in range(self.nb_cam):
                    self.event_list[((self.cam_id)+1+j)%self.nb_cam].set()
                    logger.debug('cam {} set'.format((self.cam_id+1+j)
                    %self.nb_cam))
                    time.sleep(0.5)
                    if not self.event_list[self.cam_id].isSet():
                        break
                    else :
                        logger.warning('Thread {} probably down !'
                                       .format(self.cam_id))
                result_DB = Result(camera=self.cam, result=result_darknet)
                # il faut utiliser opencv pour faire les box
                result_DB.file.save('detect',File(img_bytes))
                result_DB.save()
            else :
                logger.warning('bad camera download on {} \n'
                             .format(self.cam.name))
                

# get all the cameras in the DB
cameras = Camera.objects.all()
nb_cam = len(cameras)

# create one event for each camera. So the thread will be able to communicate
# between each other using this event. It is necesary to tell other threads
# when the darknet process is over. 
event_list = [Event() for _ in range(nb_cam)]

# create one thread per camera
thread_list = [ ProcessCamera(c,event_list, nb_cam) for c in cameras]

# load the Neural Network and the meta
net = dn.load_net(b"darknet_python/cfg/yolo.cfg", b"../../yolo.weights", 0)
meta = dn.load_meta(b"darknet_python/cfg/coco.data")
   
def main():
    for t in thread_list:
        t.start()

# start the threads
if __name__ == 'main':
    # grzet
    pass

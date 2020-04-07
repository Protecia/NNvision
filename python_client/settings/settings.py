# -*- coding: utf-8 -*-
"""
Created on Tue Dec  3 15:06:16 2019

@author: julien
"""
import logging

LOG = logging.ERROR
VIDEO_LOG = logging.INFO
UPLOAD_LOG = logging.INFO

#Darknet conf
CFG = 'cfg/yolov3.cfg'
WEIGHTS = 'yolov3.weight'
DATA = '/home/protecia/NNvision/python_client/coco_nano.data'
DARKNET_PATH='/home/protecia/darknet'

# hardware conf
INSTALL_PATH = '/home/protecia/NNvision/python_client'
HARDWARE = 'xxx' # Nano or x64

# python conf
PYTHON = 'python3'
THREATED_REQUESTS=True
SERVER = 'https://client.protecia.com/'
VIDEO_REC_TIME = 10
VIDEO_SPACE = 30 #Go
QUEUE_SIZE = 100 # number of images to queue at max

# client conf
KEY = 'e40872239e1c0f4a56dc2636cd98d2b668d4260c10f4a9718433369333a2c54f'
TUNNEL_PORT = 40002



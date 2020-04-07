# -*- coding: utf-8 -*-
"""
Created on Tue Dec  3 15:06:16 2019

@author: julien
"""
import logging

LOG = logging.ERROR
VIDEO_LOG = logging.INFO

CFG = 'cfg/yolov3.cfg'
WEIGHTS = 'yolov3.weight'
DATA = '/home/protecia/NNvision/python_client/coco_nano.data'
DARKNET_PATH='/home/protecia/darknet'

PYTHON = 'python3'
THREATED_REQUESTS=True
INSTALL_PATH = '/home/protecia/NNvision/python_client'

QUEUE_SIZE = 100 # number of images to queue at max

KEY = 'e40872239e1c0f4a56dc2636cd98d2b668d4260c10f4a9718433369333a2c54f'
SERVER = 'https://client.protecia.com/'
TUNNEL_PORT = 40002
HARDWARE = 'xxx' # Nano or x64
VIDEO_REC_TIME = 10

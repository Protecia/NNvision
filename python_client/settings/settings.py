# -*- coding: utf-8 -*-
"""
Created on Tue Dec  3 15:06:16 2019

@author: julien
"""
import logging

LOG = logging.ERROR

CFG = 'cfg/yolov3-spp.cfg'
WEIGHTS = '../weights/yolov3-spp.weights'
DATA = 'cfg/coco.data'
DARKNET_PATH='/NNvision/darknet_pjreddie_201906'

PYTHON = 'python3'
THREATED_REQUESTS=True

QUEUE_SIZE = 100 # number of images to queue at max

KEY = '###'
SERVER = 'https://client.protecia.com/'

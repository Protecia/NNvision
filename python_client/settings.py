# -*- coding: utf-8 -*-
"""
Created on Tue Dec  3 15:06:16 2019

@author: julien
"""
import logging

LOG = logging.DEBUG

CFG = 'cfg/yolov3-spp.cfg'
WEIGHTS = '../weights/yolov3-spp.weights'
DATA = 'cfg/coco.data'
DARKNET_PATH='/NNvision/darknet_pjreddie_201906'

PYTHON = 'python3'
THREATED_REQUESTS=True


QUEUE_SIZE = 100 # number of images to queue at max
IMAGE_MAX_WIDTH = 300  # pixels
IMAGE_MAX_HIGHT = 300

KEY = '9c618a8e4ef4c95b910a3386940d63c4bc72df3c8b2d0de56bf1709d7312a1a0'
SERVER = 'http://192.168.1.18:2222/'

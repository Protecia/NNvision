# -*- coding: utf-8 -*-
"""
Created on Tue Mar  3 11:03:53 2020

@author: julien
"""

import json
from collections import namedtuple
import time

with open('camera/camera.json', 'r') as json_file:
    cameras = json.load(json_file, object_hook=lambda d: namedtuple('camera', d.keys())(*d.values()))
    cameras = [c for c in cameras if c.active==True]


for cam in cameras:
    cmd = 'ffmpeg -i {} -vcodec copy {}.mp4'.format(cam.rtsp,'test')
    
    
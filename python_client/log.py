# -*- coding: utf-8 -*-
"""
Created on Sun Dec 22 11:11:54 2019

@author: julien
"""
import logging
from logging.handlers import RotatingFileHandler
import settings.settings as settings
import os

#------------------------------------------------------------------------------
# a simple config to create a file log - change the level to warning in
# production
#------------------------------------------------------------------------------

class Logger(object):
    def __init__(self, name):
        self.logger = logging.getLogger()
        self.logger.setLevel(settings.LOG)
        formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
        file_handler = RotatingFileHandler(os.path.join('/NNvision/camera',name+'.log'), 'a', 10000000, 1)
        file_handler.setLevel(settings.LOG)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
    def run(self):
        return self.logger
        


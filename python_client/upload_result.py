# -*- coding: utf-8 -*-
"""
Created on Tue Dec 24 16:14:52 2019

@author: julien
"""
import requests
import settings.settings as settings
from log import Logger
import time
import json

logger = Logger(__name__).run()

def uploadImage(Q):
    while True:
        img = Q.get()
        files = {'myFile': img}
        try :
            requests.post(settings.SERVER+"upload", files=files, data = {'key': settings.KEY})
        except requests.exceptions.ConnectionError :
            pass

def uploadResult(Q):
    while True:
        logger.warning('starting upload result')
        result = Q.get()
        logger.info('get from queue : {}'.format(result))
        resultString = (result[0],[(r[0].decode(),r[1],r[2]) for r in result[1] ])
        resultJson = {'key': settings.KEY, 'result' : resultString }
        try :
            requests.post(settings.SERVER+"uploadresult", json=resultJson)
        except requests.exceptions.ConnectionError :
            pass
        logger.warning('send json : {}'.format(resultJson))
        

def getState(E):
    while True:
        try :
            r = requests.post(settings.SERVER+"getState", data = {'key': settings.KEY, } )
            rec = json.loads(r.text)[0]['rec']
            if rec :
                E.set()
            else :
                E.clear()
        except requests.exceptions.ConnectionError :
            logger.info('getState Can not find the remote server')
            time.sleep(5)
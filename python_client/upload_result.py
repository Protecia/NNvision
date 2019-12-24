# -*- coding: utf-8 -*-
"""
Created on Tue Dec 24 16:14:52 2019

@author: julien
"""
import requests
import settings.settings as settings
from log import Logger

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
        result = Q.get()
        logger.INFO('get from queue : {}'.format(result))
        resultString = (result[0],[(r[0].decode(),r[1],r[2]) for r in result[1] ])
        resultJson = {'key': settings.KEY, 'result' : resultString }
        try :
            requests.post(settings.SERVER+"uploadresult", json=resultJson)
        except requests.exceptions.ConnectionError :
            pass
        logger.INFO('send json : {}'.format(resultJson))
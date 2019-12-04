# -*- coding: utf-8 -*-
"""
Created on Sat Jun  1 07:34:04 2019

@author: julien
"""
import os
import logging
from logging.handlers import RotatingFileHandler
from process_camera_thread import ProcessCamera
from threading import Event
from multiprocessing import Process, Queue, Event as pEvent
import requests
import json
from collections import namedtuple
import settings
import darknet as dn

#------------------------------------------------------------------------------
# a simple config to create a file log - change the level to warning in
# production
#------------------------------------------------------------------------------
level=settings.LOG
logger = logging.getLogger()
logger.setLevel(level)
formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
file_handler = RotatingFileHandler(os.path.join(settings.BASE_DIR,'camera.log'), 'a', 10000000, 1)
file_handler.setLevel(level)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
#stream_handler = logging.StreamHandler()
#stream_handler.setLevel(level)
#logger.addHandler(stream_handler)
#------------------------------------------------------------------------------

Q_img = Queue()
Q_result = Queue()
E_cam = pEvent()

def upload(Q):
    while True:
        img = Q.get()
        files = {'myFile': img}
        try :
            requests.post("http://192.168.0.19:8080/upload", files=files)
        except requests.exceptions.ConnectionError :
            pass
        
def getCamera(force='0'):
    key =  settings.KEY
    r = requests.post("http://192.168.0.19:2222/getCam", data = {'key': key, 'force':force} )
    if force=='1' or r.text!='0' :
        c = json.loads(r.text)
        with open('camera.json', 'w') as out:
            json.dump(c,out)
        r = requests.post("http://192.168.0.19:2222/upCam", data = {'key': key})
        E_cam.set()
        return True   
    return False
    
 #c = json.loads(r.text, object_hook=lambda d: namedtuple('camera', d.keys())(*d.values()))


def main():   
    getCamera(force='1')
    threated_requests = settings.THREATED_REQUESTS
    path = settings.DARKNET_PATH
    cfg = os.path.join(path,settings.CFG).encode()
    weights = os.path.join(path,settings.WEIGHTS).encode()
    data = os.path.join(path,settings.DATA).encode()
    net = dn.load_net(cfg,weights, 0)
    meta = dn.load_meta(data)
    try:
        while(True):
            with open('camera.json', 'r') as json_file:  
                cameras = json.load(json_file, object_hook=lambda d: namedtuple('camera', d.keys())(*d.values()))
            list_thread=[]
            list_event=[Event() for i in range(len(cameras))]
            for n, c in enumerate(cameras):
                p = ProcessCamera(c, n, Q_result, logger, net, meta,
                                  threated_requests, list_event, settings.MEDIA_ROOT,
                                  dn.array_to_image, dn.detect_image, len(cameras), Q_img)
                list_thread.append(p)
                p.start()
        
            print('darknet is running...')
            # Just run4ever (until Ctrl-c...)
            list_event[0].set()
        
            pImageUpload = Process(target=upload, args=(Q_img,))
            pCameraDownload = Process(target=getCamera)
            pImageUpload.start()
            pCameraDownload.start()
            E_cam.clear()
            E_cam.wait()
            for t in list_thread:
                t.running=False
                t.running_rtsp=False
                try :
                    t.thread_rtsp.join()
                except AttributeError:
                    pass
                t.join()
            print("Camera change restart !")            
            
    except KeyboardInterrupt:
        for t in list_thread:
            t.running=False
            t.running_rtsp=False
            try :
                t.thread_rtsp.join()
            except AttributeError:
                pass
            t.join()
        print("Bye bye!")



# start the threads
if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-
"""
Created on Sat Jun  1 07:34:04 2019

@author: julien
"""

import process_camera_thread as pc
from threading import Event
from multiprocessing import Process, Queue, Lock, Event as pEvent
import requests
import json
from collections import namedtuple
import settings.settings as settings
from .log import logger
import scan_camera as sc

logger = logger('process_camera')

Q_img = Queue()
Q_result = Queue()
E_cam = pEvent()
E_state = pEvent()
onLine = True

def upload(Q):
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
        resultString = (result[0],[(r[0].decode(),r[1],r[2]) for r in result[1] ])
        resultJson = json.dumps(resultString)
        try :
            requests.post(settings.SERVER+"uploadresult", json=resultJson, data = {'key': settings.KEY})
        except requests.exceptions.ConnectionError :
            pass


def main():
    
    try:
        while(True):
            with open('camera/camera.json', 'r') as json_file:
                cameras = json.load(json_file, object_hook=lambda d: namedtuple('camera', d.keys())(*d.values()))
                cameras = [c for c in cameras if c.active==True]
            list_thread=[]
            list_event=[Event() for i in range(len(cameras))]
            for n, c in enumerate(cameras):
                p = pc.ProcessCamera(c, n, Q_result,
                                   list_event,
                                   len(cameras), Q_img, E_state)
                list_thread.append(p)
                p.start()
            print('darknet is running...')
            # Just run4ever (until Ctrl-c...)
            list_event[0].set()
            pImageUpload = Process(target=upload, args=(Q_img,))
            pCameraDownload = Process(target=sc.run)
            pState = Process(target=pc.getState, args=(E_state,))
            pImageUpload.start()
            pCameraDownload.start()
            pState.start()
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
            logger.warning('Camera change restart !')

    except KeyboardInterrupt:
        for t in list_thread:
            t.running=False
            t.running_rtsp=False
            try :
                t.thread_rtsp.join()
            except AttributeError:
                pass
            t.join()
        pImageUpload.join()
        pCameraDownload.join()
        pState.join()
        print("Bye bye!")

# start the threads
if __name__ == '__main__':
    main()

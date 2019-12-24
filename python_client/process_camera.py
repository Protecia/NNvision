# -*- coding: utf-8 -*-
"""
Created on Sat Jun  1 07:34:04 2019

@author: julien
"""

import process_camera_thread as pc
from threading import Event
from multiprocessing import Process, Queue, Lock, Event as pEvent
import json
from collections import namedtuple
from log import Logger
import scan_camera as sc
import upload_result as up

logger_pc = Logger('process_camera').run()

Q_img = Queue()
Q_result = Queue()
E_cam_start = pEvent()
E_cam_stop = pEvent()
E_state = pEvent()
lock = Lock()
onLine = True


def main():
    
    try:
        while(True):
            # start the process to synchronize cameras
            pCameraDownload = Process(target=sc.run, args=(1,lock, E_cam_start, E_cam_stop))
            pCameraDownload.start()
            logger_pc.warning('scan camera launch, E_cam_start.is_set : {}  / E_cam_stopt.is_set : {}'.format(E_cam_start.is_set(),E_cam_stop.is_set()) )
            E_cam_start.wait()
            E_cam_stop.clear()
            logger_pc.warning('scan camera launch, E_cam_start.is_set : {}  / E_cam_stopt.is_set : {}'.format(E_cam_start.is_set(),E_cam_stop.is_set()) )
            with lock :
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
            pImageUpload = Process(target=up.uploadImage, args=(Q_img,))
            pResultUpload = Process(target=up.uploadResult, args=(Q_result,))
            pState = Process(target=up.getState, args=(E_state,))
            pImageUpload.start()
            pResultUpload.start()
            pState.start()
            
            E_cam_stop.wait()
            E_cam_start.clear()
            for t in list_thread:
                t.running=False
                t.running_rtsp=False
                try :
                    t.thread_rtsp.join()
                except AttributeError:
                    pass
                t.join()
            pImageUpload.terminate()
            pState.terminate()
            pCameraDownload.terminate()
            pResultUpload.terminate()
            pImageUpload.join()()
            pState.join()
            pCameraDownload.join()
            pResultUpload.joint()
            
            logger_pc.warning('Camera change restart !')

    except KeyboardInterrupt:
        for t in list_thread:
            t.running=False
            t.running_rtsp=False
            try :
                t.thread_rtsp.join()
            except AttributeError:
                pass
            t.join()
        pImageUpload.terminate()
        pState.terminate()
        pCameraDownload.terminate()
        pResultUpload.terminate()
        pImageUpload.join()()
        pState.join()
        pCameraDownload.join()
        pResultUpload.joint()
        print("Bye bye!")

# start the threads
if __name__ == '__main__':
    main()

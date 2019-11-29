# -*- coding: utf-8 -*-
"""
Created on Sat Jun  1 07:34:04 2019

@author: julien
"""
from process_camera_main import ProcessCamera
import process_camera_cfg as cs
import time

def main():
    list_process = []
    cameras = cs.Camera.objects.filter(active=True)
    cs.event(len(cameras))
    i=0
    for c in cameras:
        list_process.append(ProcessCamera(c,i))
        i+=1
    for t in list_process:
        t.start()
    cs.network()
    cs.event_list[0].set()
    print('darknet is running...')
    # Just run4ever (until Ctrl-c...)
    try:
        while(True):
            time.sleep(1000)
    except KeyboardInterrupt:
        for t in list_process:
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

# -*- coding: utf-8 -*-
"""
Created on Tue Mar  3 11:03:53 2020

@author: julien
"""

from datetime import datetime
import psutil as ps
from subprocess import Popen
import shlex
import time
import secret
from threading import Thread
from settings import settings
from log import Logger
import json

logger = Logger(__name__).run()
logger.setLevel(settings.VIDEO_LOG)

class RecCamera(object):
    
    @classmethod
    def kill_ffmpeg_process():
        for p in ps.process_iter():
            try :
                for n in p.cmdline():
                    if 'ffmpeg' in n :
                        p.terminate()
                        time.sleep(2)
                        p.kill()
                        print(p,"kill")
            except ps.AccessDenied :
                pass
                return False
            except ps.NoSuchProcess :
                pass
        return True
    
    def __init__(self, E_video):
        self.update = E_video
        
            
    def update_cam(self):
        while True :
            self.update.wait()
            with open('camera/camera.json', 'r') as json_file:
               cameras = json.load(json_file)
            self.cameras = dict((item['id'], item) for item in cameras if item['active'])
            for k,v in self.cameras.items() :
                if not 'rec' in v.keys():
                    v['rec'] = False
            logger.info('Update cameras')
            self.update.clear()
                  
    def rec_all_cam(self):
        for k,v in self.cameras.items():
            cmd = 'ffmpeg  -nostats -loglevel 0 -y -i  {} -vcodec copy camera/live/{}.mp4'.format(v['rtsp'], datetime.now().strftime("%Y-%m-%d_%H")+'_cam'+str(k))
            Popen(shlex.split(cmd))
            
    def rec_cam(self,cam_id, img):
        if not self.cameras[cam_id]['rec']:
            self.cameras[cam_id]['rec']=True
            token = secret.token_urlsafe()
            cmd = 'ffmpeg  -nostats -loglevel 0 -y -i  {} -vcodec copy camera/live/{}.mp4'.format(self.cameras[cam_id]['rtsp'], token )
            p = Popen(shlex.split(cmd))
            logger.info('Send ffmpeg process with cmd {}'.format(cmd))
            # thread to kill process
            Thread(target=self.kill_process, args=(cam_id, p))
            self.cameras[cam_id]['token']=token
        self.cameras[cam_id]['rec_time']=time.time()
        return self.cameras[cam_id]['token']
            
    def kill_process(self, cam_id, p):
        while True :
            if time.time()-self.cameras[cam_id]['rec_time'] > settings.VIDEO_REC_TIME :
                self.cameras[cam_id]['rec'] =False
                try :
                    p.terminate()
                    time.sleep(2)
                    p.kill()
                except ps.AccessDenied :
                    pass
                except ps.NoSuchProcess :
                    pass
                    break
            
             
def main():
    RecCamera.kill_ffmpeg_process()
    rec = RecCamera()
    rec.rec_all_cam()
    
    
# start the threads
if __name__ == '__main__':
    main()

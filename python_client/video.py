# -*- coding: utf-8 -*-
"""
Created on Tue Mar  3 11:03:53 2020

@author: julien
"""

from datetime import datetime
import psutil as ps
from subprocess import Popen, check_output
import shlex
import time
import secrets
from threading import Thread
from settings import settings
from log import Logger
import json
import os
import cherrypy

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
        Thread(target=self.update_cam).start()

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
            cmd = 'ffmpeg  -nostats -loglevel 0 -y -i  {} -vcodec copy camera/secu/{}.mp4'.format(v['rtsp'], datetime.now().strftime("%H")+'_cam'+str(k))
            Popen(shlex.split(cmd))

    def rec_cam(self,cam_id):
        if not self.cameras[cam_id]['rec']:
            self.cameras[cam_id]['rec']=True
            token = secrets.token_urlsafe()
            cmd = 'ffmpeg  -nostats -loglevel 0 -y -i  {} -vcodec copy camera/live/{}.mp4'.format(self.cameras[cam_id]['rtsp'], token )
            p = Popen(shlex.split(cmd))
            logger.info('Send ffmpeg process with cmd {}'.format(cmd))
            self.cameras[cam_id]['rec_time']=time.time()
            # thread to kill process
            t = Thread(target=self.kill_process, args=(cam_id, p))
            t.start()
            self.cameras[cam_id]['token']=token
        else :
            self.cameras[cam_id]['rec_time']=time.time()
        return self.cameras[cam_id]['token']

    def kill_process(self, cam_id, p):
        self.check_space(5)
        i=0
        while True :
            if time.time()-self.cameras[cam_id]['rec_time'] > settings.VIDEO_REC_TIME or i > 3600 : #max 30 mn per video
                self.cameras[cam_id]['rec'] =False
                logger.info('kill process {} for cam {}'.format(p, cam_id))
                try :
                    p.terminate()
                    time.sleep(2)
                    p.kill()
                    break
                except ps.AccessDenied :
                    pass
                except ps.NoSuchProcess :
                    pass
                    break
            i +=1
            time.sleep(0.5)

    def check_space(self,G):
    ##### check the space on disk to respect the quota #######
        path = os.path.join(settings.INSTALL_PATH,'camera/live')
        size = int(check_output(['du','-s', path]).split()[0].decode('utf-8'))
        logger.info('check size {} Go'.format(size/1000000))
        if size>settings.VIDEO_SPACE*1000000:
            files = [os.path.join(path, f) for f in os.listdir(path)] # add path to each file
            files.sort(key=lambda x: os.path.getmtime(x))
            while settings.VIDEO_SPACE*1000000-int(check_output(['du','-s', path]).split()[0].decode('utf-8')) < G*1000000 :
                os.remove(files[0])
                del(files[0])

def http_serve(port):
    """Static file server, using Python's CherryPy. Used to serve video."""
    logger.warning('starting cherrypy')

    class Root:

        @cherrypy.expose
        def index(self, name):
            return cherrypy.lib.static.serve_file(os.path.join(static_dir, name))

        @cherrypy.expose
        def video(self,v):
            file = os.path.join(static_dir, v)
            if os.path.isfile(file):
                return """
                <!DOCTYPE html>
                <html>
                  <head>
                    <meta charset="utf-8">
                    <title>Protecia</title>
                    <link rel="shortcut icon" href="img/favicon.ico">
                  </head>
                  <body>
                <p>
                  <img   src="img/logo_protecia.jpg" alt="Protecia">
                </p>
                <div style="text-align:center;">
                <video  controls autoplay>
                  <source src="{}" type="video/mp4">
                  Your browser does not support HTML5 video.
                </video>
                </div>
                  </body>
                </html>

                """.format(v)
            else:
                return """
                <!DOCTYPE html>
                <html>
                  <head>
                    <meta charset="utf-8">
                    <title>Protecia</title>
                    <link rel="shortcut icon" href="img/favicon.ico">
                  </head>
                  <body>
                <p>
                  <img  src="img/logo_protecia.jpg" alt="Protecia">
                </p>
                <div style="text-align:center;">
                <h1>
                  Video non disponible !
                 </h1>
                 <h1>
                  Video unavailable !
                 </h1>
                </video>
                </div>
                  </body>
                </html>
            """
    static_dir = os.path.join(settings.INSTALL_PATH,'camera/live') # Root static dir is this file's directory.
    cherrypy.config.update( {  # I prefer configuring the server here, instead of in an external file.
                'server.socket_host': '0.0.0.0',
                'server.socket_port': port,
                'environment': 'production',
            } )
    conf = {
            '/': {
                'tools.staticdir.on':   True,  # Enable or disable this rule.
                'tools.staticdir.root': static_dir,
                'tools.staticdir.dir':  '',
            },
                    '/img': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': '../../img'
        }
        }
    return cherrypy.quickstart(Root(), '/', config=conf)  # ..and LAUNCH ! :)

def main():
    RecCamera.kill_ffmpeg_process()
    rec = RecCamera()
    rec.rec_all_cam()

# start the threads
if __name__ == '__main__':
    main()

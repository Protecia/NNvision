# -*- coding: utf-8 -*-
"""
Created on Sat Feb  3 11:58:19 2018

@author: julien

Main script to process the camera images
"""
import logging
import time
import requests
import os
import sys
import cv2
from django.conf import settings
from threading import Thread, Lock, Event
from logging.handlers import RotatingFileHandler
from io import BytesIO
from django.core.files import File
from collections import Counter 


#------------------------------------------------------------------------------
# Because this script have to be run in a separate process from manage.py
# you need to set up a Django environnement to use the Class defined in
# the Django models. It is necesssary to interact witht the Django database
#------------------------------------------------------------------------------
# to get the projet.settings it is necessary to add the parent directory
# to the python path
try:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
except NameError:
    sys.path.append(os.path.abspath('..'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "projet.settings")
import django
django.setup()

#------------------------------------------------------------------------------
# a simple config to create a file log - change the level to warning in
# production
#------------------------------------------------------------------------------
level= logging.DEBUG
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

from app1.models import Camera, Result, Object, Info
from app1.darknet_python import darknet as dn

# locking process to avoid threads calling darknet more than once at a time
lock = Lock()

# the base condition to store the image is : is there a new objects detection
# or a change in the localisation of the objects. It is not necessary to store
# billions of images but only the different one.

class ProcessCamera(Thread):
    """Thread used to grab camera images and process the image with darknet"""
    def __init__(self, cam, event_list, nb_cam):
        Thread.__init__(self)
        self.cam = cam
        self.event_list = event_list
        self.cam_id = cam.id-1
        self.nb_cam = nb_cam
        self.running = False
        self.img_temp = os.path.join(settings.BASE_DIR,'tempimg_cam'+str(self.cam_id))
        self.threshold = 0.8
        self.pos_sensivity = 100
        self.black_list=(b'pottedplant',b'cell phone')
        self.clone={b'cell phone':b'car'}
        ###  getting last object in db for camera to avoid writing same images at each restart
        r_last = Result.objects.filter(camera=cam).last()
        o_last = Object.objects.filter(result_id=r_last.id)
        result_last = [(r.result_object.encode(), float(r.result_prob),
                        (float(r.result_loc1),float(r.result_loc2),
                         float(r.result_loc3),float(r.result_loc4))) for r in o_last]
        self.result_DB = result_last

    def run(self):
        """code run when the thread is started"""
        self.running = True
        while self.running :
            t=time.time()
            request_OK = True
            try :
                r = requests.get(self.cam.url, auth=(self.cam.username,
                                                 self.cam.password
                                                 ), stream=True, timeout=4)
                if r.status_code == 200 :
                    with open(self.img_temp, 'wb') as fd:
                        for chunk in r.iter_content(chunk_size=128):
                            fd.write(chunk)
                    logger.info('image saved to temp folder for darknet in {}s '.format(
                                 time.time()-t))
                else:
                    request_OK = False
                    logger.warning('bad camera download on {} \n'.format(self.cam.name))    
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
                request_OK = False
                logger.warning('network error on {} \n'.format(self.cam.name))
                pass
            t=time.time()
            if request_OK:
                self.event_list[self.cam_id].wait()
                logger.debug('cam {} alive'.format(self.cam_id))

                with lock:
                   result_darknet = dn.detect(net, meta, self.img_temp.encode(),
                                               thresh=self.threshold-0.4,
                                               hier_thresh = 0.4)
                   logger.info('get brut result from darknet : {} in {}s\n'.format(
                   result_darknet,time.time()-t))
                # get only result above trheshlod or previously valid
                t=time.time()
                result_filtered = self.check_thresh(result_darknet)
                # compare with last result to check if different
                if self.base_condition(result_filtered):
                    logger.debug('>>> Result have changed <<< ')
                    result_DB = Result(camera=self.cam,brut=result_darknet)
                    date = time.strftime("%Y-%m-%d-%H-%M-%S")
                    arr = cv2.imread(self.img_temp)
                    img_bytes = BytesIO(cv2.imencode('.jpg', arr)[1].tobytes())
                    result_DB.file1.save('detect_'+date+'.jpg',File(img_bytes)) 
                    for r in result_filtered:
                        box = ((int(r[2][0]-(r[2][2]/2)),int(r[2][1]-(r[2][3]/2
                        ))),(int(r[2][0]+(r[2][2]/2)),int(r[2][1]+(r[2][3]/2
                        ))))
                        logger.debug('box calculated : {}'.format(box))
                        arr = cv2.rectangle(arr,box[0],box[1],(0,255,0),3)
                        arr = cv2.putText(arr,r[0].decode(),box[1],
                        cv2.FONT_HERSHEY_SIMPLEX, 1,(0,255,0),2)
                        object_DB = Object(result = result_DB, 
                                           result_object=r[0].decode(),
                                           result_prob=r[1],
                                           result_loc1=r[2][0],
                                           result_loc2=r[2][1],
                                           result_loc3=r[2][2],
                                           result_loc4=r[2][3])
                        object_DB.save()
                    img_bytes_rect = BytesIO(cv2.imencode('.jpg', arr)[1].tobytes())
                    result_DB.file2.save('detect_box_'+date+'.jpg',File(img_bytes_rect))
                    result_DB.save()
                    logger.info('>>>>>>>>>>>>>>>--------- Result store in DB '
                    '-------------<<<<<<<<<<<<<<<<<<<<<\n')
                    self.result_DB = result_filtered    
                logger.info('brut result process in {}s '.format(time.time()-t))
            self.event_list[self.cam_id].clear()
            logger.debug('cam {} clear -> so wait !'.format(self.cam_id))
            self.event_list[((self.cam_id)+1)%self.nb_cam].set()
            logger.debug('cam {} set'.format((self.cam_id+1)%self.nb_cam))
            

    def base_condition(self,new):
    # are the detected objects not the same
        if not ([i[0] for i in self.result_DB]  == [i[0] for i in new] ):
            logger.info('Change in objects detected : list1={} list2={} diff={}'
            .format([i[0] for i in self.result_DB],[i[0] for i in new],set([i[0] 
            for i in self.result_DB])^set([i[0] for i in new])))
            return True
    # are the location different
        if abs(sum([i-j for i,j in zip(
        [i for j in self.result_DB  for i in j[2]], [i for j in new for i in
        j[2]])])
        )>self.pos_sensivity*len(new):
            logger.info('New position detected - change of : {}'.format(abs(
            sum([i-j for i,j in zip([i for j in self.result_DB for i in j[2]],
                                    [i for j in new for i in j[2]])]))))
            return True
        return False


    def check_thresh(self,resultb):
        result = [r for r in resultb if r[0] not in self.black_list]
        #result = [(e1,e2,e3) if e1 not in self.clone else (self.clone[e1],e2,e3)
        #for (e1,e2,e3) in result]
        rp = [r for r in result if r[1]>=self.threshold]
        rm = sorted([r for r in result if r[1]<self.threshold],reverse=True)
        if len(rm)>0:        
            diff_objects = list((Counter([r[0] for r in self.result_DB])-
                         Counter([r[0] for r in rp])).elements())
            logger.debug('objects lost since last detection is :{} '
            'with objects {} under threshold'.format(diff_objects,[r for r in
            result if r[1]<self.threshold and  r[0] in diff_objects]))
            for d in diff_objects :
                rd = next(((i,r) for i,r in enumerate(rm) if r[0]==d),False)
                if rd : 
                    rp.append(rd[1])
                    del rm[rd[0]]
        new_list = sorted(rp)
        logger.debug('the filtered list of detected objects is {}'.format(
        new_list))
        return new_list
              
# get all the cameras in the DB
cameras = Camera.objects.all()
nb_cam = len(cameras)

# create one event for each camera. So the thread will be able to communicate
# between each other using this event. It is necesary to tell other threads
# when the darknet process is over. 
event_list = [Event() for _ in range(nb_cam)]

# create one thread per camera
thread_list = [ ProcessCamera(c,event_list, nb_cam) for c in cameras]

# load the Neural Network and the meta
path = Info.objects.get().darknet_path
cfg = os.path.join(path,'cfg/yolov2.cfg').encode()
weights = os.path.join(path,'yolov2.weights').encode()
data = os.path.join(path,'cfg/coco.data').encode()

net = dn.load_net(cfg,weights, 0)
meta = dn.load_meta(data)
   
def main():
    for t in thread_list:
        t.start()
    thread_list[0].event_list[0].set()
    print('darknet is running...')
    # Just run4ever (until Ctrl-c...)
    try:
        while(True):
            time.sleep(1000)
    except KeyboardInterrupt:
        print("Bye bye!")
    
def stop():
    for t in thread_list:
        t.running=False
        
def start():
    for t in thread_list:
        t.running=True

# start the threads
if __name__ == '__main__':
    main()



# -*- coding: utf-8 -*-
"""
Created on Sat Feb  3 11:58:19 2018

@author: julien

Main script to process the camera images
"""
import time
import requests
import os
import cv2
import numpy as np
from threading import Thread, Lock
from io import BytesIO
from django.core.files import File
from django.db import transaction


# function to extract same objects in 2 lists
def get_list_same (l_old,l_under,thresh):
    l_old_w = l_old[:]
    new_element = []
    for e_under in l_under :
        for e_old in l_old_w:
            if e_under[0]==e_old[0] :
                diff_pos = (sum([abs(i-j) for i,j in zip(e_under[2],e_old[2])]))
                if diff_pos < thresh :
                    new_element.append(e_old)
                    l_old_w.remove(e_old)
    return new_element

def get_list_diff(l_new,l_old,thresh):
    new_copy = l_new[:]
    old_copy = l_old[:]
    for e_new  in  l_new:
        flag = False
        limit_pos = thresh
        for e_old in l_old:
            if e_new[0]==e_old[0] :
                diff_pos = (sum([abs(i-j) for i,j in zip(e_new[2],e_old[2])]))
                if diff_pos < thresh :
                    flag = True
                    if diff_pos < limit_pos:
                        limit_pos = diff_pos
                        to_remove = (e_new,e_old)
        if flag:
            #self.logger.debug('get_list-diff remove {} '.format(to_remove))
            new_copy.remove(to_remove[0])
            try :
                old_copy.remove(to_remove[1])
                new_copy.remove(to_remove[0])
            except ValueError:
                pass
    return new_copy,old_copy

def read_write(rw,*args):
    if rw=='r':
        im = cv2.imread(*args)
        return im
    if rw=='w':
        r = cv2.imwrite(*args)
        return r


# the base condition to store the image is : is there a new objects detection
# or a change in the localisation of the objects. It is not necessary to store
# billions of images but only the different one.

class ProcessCamera(Thread):
    """Thread used to grab camera images and process the image with darknet"""

    def __init__(self, cam, num, Result, Object, logger, net, meta,
                 threated_requests, list_event, path, array_to_image,
                 detect_image, nb_cam, Q):
        Thread.__init__(self)
        self.event = list_event
        self.cam = cam
        self.num = num
        self.running = False
        self.running_rtsp = False
        self.img_temp = os.path.join(path,'tempimg_cam'+str(self.cam.id)+'.jpg')
        self.img_temp_box = os.path.join(path,'tempimg_cam'+str(self.cam.id)+'_box.jpg')
        self.pos_sensivity = cam.pos_sensivity
        self.threated_requests = threated_requests
        self.request_OK = False
        self.lock = Lock()
        self.black_list=(b'pottedplant',b'cell phone')
        self.result = Result
        self.object = Object
        self.logger = logger
        self.net = net
        self.meta = meta
        self.array_to_image = array_to_image
        self.detect_image = detect_image
        self.nb_cam = nb_cam
        self.Q = Q

        ###  getting last object in db for camera to avoid writing same images at each restart
        r_last = self.result.objects.filter(camera=cam).last()
        if r_last :
            o_last = self.object.objects.filter(result_id=r_last.id)
            result_last = [(r.result_object.encode(), float(r.result_prob),
                            (float(r.result_loc1),float(r.result_loc2),
                             float(r.result_loc3),float(r.result_loc4))) for r in o_last]
            self.result_DB = result_last
        else :
            self.result_DB = []
        if cam.auth_type == 'B':
            self.auth = requests.auth.HTTPBasicAuth(cam.username,cam.password)
        if cam.auth_type == 'D' :
            self.auth = requests.auth.HTTPDigestAuth(cam.username,cam.password)

    def grab(self):
        self.vcap = cv2.VideoCapture(self.cam.rtsp)
        self.running_rtsp = self.vcap.isOpened()
        self.logger.warning('openning videocapture {} is {}'.format(self.vcap, self.vcap.isOpened()))
        i=15
        bad_read = 0
        while self.running_rtsp :
            if i==15:
                date = time.strftime("%Y-%m-%d-%H-%M-%S")
                ret, frame = self.vcap.read()
                self.logger.debug("resultat de la lecture rtsp : {} ".format(ret))
                self.logger.debug('*** {}'.format(date))
                t = time.time()
                if ret and len(frame)>100 :
                    bad_read = 0
                    if self.cam.reso:
                        if frame.shape[0]!=self.cam.height or frame.shape[1]!=self.cam.width:
                            frame = cv2.resize(frame,(self.cam.width, self.cam.height), interpolation = cv2.INTER_CUBIC)
                    with self.lock:
                        self.frame = frame
                        self.request_OK = True
                    self.logger.debug("resultat de l'ecriture de la frame : {} en {} ".format(
                            self.request_OK,time.time()-t))
                else :
                    self.request_OK = False
                    self.logger.warning('Bad rtsp read on {} videocapture is {}'.format(self.cam.name,self.vcap.isOpened()))
                    self.running_rtsp = self.vcap.isOpened()
                    bad_read+=1
                    if bad_read > 10:
                        break
                    time.sleep(0.5)
                i=0
            self.vcap.grab()
            i+=1
        with self.lock:
            self.vcap.release()
            self.logger.warning('VideoCapture close on {}'.format(self.cam.name))
            self.running_rtsp = False
            time.sleep(5)




    def run(self):
        """code run when the thread is started"""
        self.running = True
        while self.running :
            t=time.time()

            # Special stop point for dahua nvcr which can not answer multiple fast http requests
            if not self.threated_requests :
                self.event[self.num].wait()
                self.logger.debug('cam {} alive - not threated request'.format(self.cam.id))
            #-----------------------------------------------------------------------------------

            #******************************Grab images in http ********************************
            if not self.cam.stream :
                self.request_OK = True
                try :
                    r = requests.get(self.cam.url, auth=self.auth, stream=False, timeout=4)
                    if r.status_code == 200 and len(r.content)>1000 :
                        self.frame = cv2.imdecode(np.asarray(bytearray(r.content), dtype="uint8"), 1)
                    else:
                        self.request_OK = False
                        self.logger.warning('bad camera download on {} \n'.format(self.cam.name))
                except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
                    self.request_OK = False
                    self.logger.warning('network error on {} \n'.format(self.cam.name))
                    pass

            #*****************************Grab image in rtsp **********************************
            else :
                if not self.running_rtsp :
                    with self.lock:
                        try :
                            self.thread_rtsp.join()
                            self.logger.warning('close thread {} '.format(self.thread_rtsp))
                        except AttributeError:
                            pass
                        self.logger.warning('rtsp not running on cam {}, so launch '.format(self.cam.name))
                        self.thread_rtsp = Thread(target=self.grab)
                        self.thread_rtsp.start()
                        self.running_rtsp = True
            #*************************************************************************************
            t=time.time()
            # Normal stop point for ip camera-------------------------------
            if self.threated_requests :
                self.event[self.num].wait()
                self.logger.debug('cam {} alive'.format(self.cam.id))
            #---------------------------------------------------------------
            if self.request_OK:
                with self.lock:
                    arr = self.frame.copy()
                th = self.cam.threshold*(1-(float(self.cam.gap)/100))
                self.logger.debug('thresh set to {}'.format(th))
                frame_rgb = cv2.cvtColor(arr, cv2.COLOR_BGR2RGB)
                im, arrd = self.array_to_image(frame_rgb)
                result_darknet = self.detect_image(self.net, self.meta, im, thresh=th)
                self.logger.info('get brut result from darknet in {}s : {} \n'.format(
                time.time()-t,result_darknet))
                self.event[self.num].clear()
                self.logger.debug('cam {} clear -> so wait !'.format(self.cam.id))
                self.event[((self.num)+1)%self.nb_cam].set()
                self.logger.debug('event {} set'.format((self.num+1)%self.nb_cam))

                # get only result above trheshlod or previously valid
                t=time.time()
                result_filtered = self.check_thresh(result_darknet)
                # compare with last result to check if different
                arrb = arr.copy()
                for r in result_filtered:
                    box = ((int(r[2][0]-(r[2][2]/2)),int(r[2][1]-(r[2][3]/2))),
                           (int(r[2][0]+(r[2][2]/2)),int(r[2][1]+(r[2][3]/2))))
                    cv2.rectangle(arrb,box[0],box[1],(0,255,0),3)
                    cv2.putText(arrb,r[0].decode(),box[1],
                    cv2.FONT_HERSHEY_SIMPLEX, 1,(0,255,0),2)
                rw = cv2.imwrite(self.img_temp_box,arrb)
                self.logger.debug('result of writing image box : {}'.format(rw))
                if self.base_condition(result_filtered) and self.cam.rec:
                    self.logger.debug('>>> Result have changed <<< ')
                    with transaction.atomic():
                        result_DB = self.result(camera=self.cam,brut=result_darknet)
                        date = time.strftime("%Y-%m-%d-%H-%M-%S")
                        img_bytes = cv2.imencode('.jpg', arr)[1].tobytes()
                        self.Q.put(img_bytes)
                        self.logger.warning('Q size : {}').format(self.Q.qsize())
                        img_bytes = BytesIO(img_bytes)
                        result_DB.file1.save('detect_'+date+'.jpg',File(img_bytes))
                        for r in result_filtered:
                            object_DB = self.object(result = result_DB,
                                                  result_object=r[0].decode(),
                                                  result_prob=r[1],
                                                  result_loc1=r[2][0],
                                                  result_loc2=r[2][1],
                                                  result_loc3=r[2][2],
                                                  result_loc4=r[2][3])
                            object_DB.save()
                        img_bytes_rect = BytesIO(cv2.imencode('.jpg', arrb)[1].tobytes())
                        result_DB.file2.save('detect_box_'+date+'.jpg',File(img_bytes_rect))
                        result_DB.save()
                    self.logger.info('>>>>>>>>>>>>>>>--------- Result store in DB '
                    '-------------<<<<<<<<<<<<<<<<<<<<<\n')
                    self.result_DB = result_filtered
                self.logger.info('brut result process in {}s '.format(time.time()-t))
            else :
                self.event[self.num].clear()
                self.logger.debug('cam {} clear -> so wait !'.format(self.cam.id))
                self.event[((self.num)+1)%self.nb_cam].set()
                self.logger.debug('event {} set'.format((self.num+1)%self.nb_cam))
                time.sleep(0.5)

    def base_condition(self,new):
        compare = get_list_diff(new,self.result_DB,self.pos_sensivity)
        if len(compare[0])==0 and len(compare[1])==0 :
            return False
        else:
            self.logger.info('Change in objects detected : new={} lost={}'
            .format(compare[0], compare[1]))
            return True

    def check_thresh(self,resultb):
        result = [r for r in resultb if r[0] not in self.black_list]
        #result = [(e1,e2,e3) if e1 not in self.clone else (self.clone[e1],e2,e3)
        #for (e1,e2,e3) in result]
        rp = [r for r in result if r[1]>=self.cam.threshold]
        rm = [r for r in result if r[1]<self.cam.threshold]
        if len(rm)>0:
            rs = get_list_same(self.result_DB,rp,self.pos_sensivity)
            ro = [item for item in self.result_DB if item not in rs]
            diff_objects = get_list_same(ro,rm,self.pos_sensivity)
            self.logger.debug('objects from last detection now under treshold :{} '
            .format(diff_objects))
            rp+=diff_objects
        self.logger.debug('the filtered list of detected objects is {}'.format(rp))
        return rp
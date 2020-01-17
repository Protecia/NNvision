# -*- coding: utf-8 -*-
"""
Created on Sat Dec  7 11:48:41 2019

@author: julien
"""

import wsdiscovery
import json
import settings.settings as settings
import requests
from onvif import ONVIFCamera
from onvif.exceptions import ONVIFError
from log import Logger
import time

logger = Logger('scan_camera').run()

def wsDiscovery():
    """Discover cameras on network using onvif discovery.
    Returns:
        List: List of ips found in network.
    """
    wsd = wsdiscovery.WSDiscovery()
    wsd.start()
    ret = wsd.searchServices()
    dcam = {}
    for service in ret:
        scheme = service.getXAddrs()[0]
        if 'onvif' in scheme :
            dcam[scheme.split('/')[2].split(':')[0]] = scheme.split('/')[2].split(':')[1]
    wsd.stop()
    return dcam

def getOnvifUri(ip,port,user,passwd):
    """Find uri to request the camera.
    Returns:
        List: List of uri found for the camera.
    """
    wsdir =  '/usr/local/lib/python3.6/site-packages/wsdl/'
    try :
        cam = ONVIFCamera(ip, port, user, passwd, wsdir)
        info = cam.devicemgmt.GetDeviceInformation()
        media_service = cam.create_media_service()
        profiles = media_service.GetProfiles()
        obj = media_service.create_type('GetStreamUri')
        obj.ProfileToken = profiles[0].token
        obj.StreamSetup = {'Stream': 'RTP-Unicast', 'Transport': {'Protocol': 'RTSP'}}
        rtsp = media_service.GetStreamUri(obj)['Uri']
        obj = media_service.create_type('GetSnapshotUri')
        obj.ProfileToken = profiles[0].token
        http = media_service.GetSnapshotUri(obj)['Uri'].split('?')[0]
    except ONVIFError :
        return None
    return info, rtsp, http

def setCam(cam):
    camJson = {'key':settings.KEY,'cam':cam}
    try :
        r = requests.post(settings.SERVER+"setCam", json=camJson )
        s = json.loads(r.text)
        return s
    except (requests.exceptions.ConnectionError, json.decoder.JSONDecodeError) as ex :
        logger.error('exception : {}'.format(ex))
        pass
    return False

def compareCam(ws, cameras):
    cameras_ip =  [ c['ip'] for c in cameras if c['wait_for_set'] is False]
    ws_copy = ws.copy()
    for c in ws_copy :
        if c in cameras_ip:
            del ws[c]
            cameras_ip.remove(c)
    cameras_users = [(c['username'],c['password']) for c in cameras]
    # ws contains new cam or cam not set
    # test connection
    list_cam = []
    for ip,port in ws.items() :
        new_cam = {}
        new_cam['name']= 'unknow'
        new_cam['ip'] = ip
        new_cam['port_onvif'] = port
        new_cam['wait_for_set'] = True
        new_cam['from_client'] = True
        for user , passwd in cameras_users:
            onvif = getOnvifUri(ip,port,user,passwd)
            if onvif :
                info, rtsp , http = onvif
                auth = {'B':requests.auth.HTTPBasicAuth(user,passwd), 'D':requests.auth.HTTPDigestAuth(user,passwd)}
                for t, a in auth.items() :
                    try:
                        r = requests.get(http, auth = a , stream=False, timeout=1)
                        if r.ok:
                            new_cam['brand']=info['Manufacturer']
                            new_cam['model']=info['Model']
                            new_cam['url']= http
                            new_cam['auth_type']= t
                            new_cam['username'] = user
                            new_cam['password'] = passwd
                            new_cam['active'] = True
                            new_cam['wait_for_set'] = False
                            new_cam['rtsp'] = rtsp.split('//')[0]+'//'+user+':'+passwd+'@'+rtsp.split('//')[1]
                    except requests.exceptions.ConnectionError :
                        pass
        list_cam.append(new_cam)
    return list_cam

def getCam(lock, force='0'):
    try :
        r = requests.post(settings.SERVER+"getCam", data = {'key': settings.KEY, 'force':force} )
        c = json.loads(r.text)
        with lock:
            with open('camera/camera.json', 'w') as out:
                json.dump(c,out)
        r = requests.post(settings.SERVER+"upCam", data = {'key': settings.KEY})
        return c
    except (requests.exceptions.ConnectionError, json.decoder.JSONDecodeError) as ex :
        logger.error('exception : {}'.format(ex))
        return False
        pass

def run(period, lock, E_cam_start, E_cam_stop):
    old_cam = []
    while True :
        # scan the cam on the network
        ws = wsDiscovery()
        # pull the cam from the server
        cam = getCam(lock)
        # check if changes
        if cam :
            if cam == old_cam :
                E_cam_start.set()
                logger.info('camera unchanged : E_cam_start is_set {}'.format(E_cam_start.is_set()))
            else :
                E_cam_stop.set()
                logger.info(' ********* camera changed : E_cam_stop is_set {}'.format(E_cam_start.is_set()))
            old_cam = cam
            # compare the cam with the camera file
            list_cam = compareCam(ws, cam)
            # push the cam to the server
            setCam(list_cam)
        # wait for the loop
        time.sleep(period)






# camera_ip contains cam to inactive


"""
new cam -> test scheme and set
inactive cam
"""


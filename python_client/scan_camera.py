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

"""
abandonned because onvif camera can give their url

def getScheme():
    try : 
        r = requests.post(settings.SERVER+"getScheme", data = {'key': settings.KEY,} )
        s = json.loads(r.text)
        with open('camera/scheme.json', 'w') as out:
            json.dump(s,out)
    except requests.exceptions.ConnectionError :
        pass
"""     

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
    except requests.exceptions.ConnectionError :
        pass
    return False
    
def getCam():
    ws = wsDiscovery()
    with open('camera/camera.json', 'r') as json_file:
        cameras = json.load(json_file)
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
                            new_cam['type']=info['Model']
                            new_cam['url']= http
                            new_cam['auth_type']= t
                            new_cam['username'] = user
                            new_cam['password'] = passwd
                            new_cam['rtsp'] = rtsp.split('//')[0]+'//'+user+':'+passwd+'@'+rtsp.split('//')[1]
                    except requests.exceptions.ConnectionError :
                        pass
        list_cam.append(new_cam)
    return list_cam
                                        
    
newCam(list_cam)
            
            
            
            
# camera_ip contains cam to inactive
            
            
""" 
new cam -> test scheme and set
inactive cam
"""


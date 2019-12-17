# -*- coding: utf-8 -*-
"""
Created on Sat Dec  7 11:48:41 2019

@author: julien
"""

import wsdiscovery
import json
import settings.settings as settings
import requests

def getScheme():
    try : 
        r = requests.post(settings.SERVER+"getScheme", data = {'key': settings.KEY,} )
        s = json.loads(r.text)
        with open('camera/scheme.json', 'w') as out:
            json.dump(s,out)
    except requests.exceptions.ConnectionError :
        pass

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

def newCam(cam):
    camJson = json.dumps(cam)
    try : 
        r = requests.post(settings.SERVER+"newCam", json=camJson,  data = {'key': settings.KEY,} )
        s = json.loads(r.text)
        
    except requests.exceptions.ConnectionError :
        pass
    
ws = wsDiscovery()
with open('camera/camera.json', 'r') as json_file:
    cameras = json.load(json_file)
cameras_ip =  [ c['ip'] for c in cameras]
with open('camera/scheme.json', 'r') as json_file:
    scheme = json.load(json_file)

for c in ws :
        if c in cameras_ip:
            del ws[c]
            cameras_ip.remove(c)
            
# ws contains new cam
camera_user = [(c['username'],c['password']) for c in cameras]
# test connection
list_cam = []
for ip,port in ws.items() :
    new_cam = {}
    for s in scheme:
        pl = [port,'80']
        for p in pl : 
            url = s["url"].replace("<ip>",ip)
            url = url.replace("<port>",p)
            try:
                r1 = requests.get(url, stream=False, timeout=1)
                if r1.status_code == '401':
                    new_cam['name']=s['brand']
                    new_cam['url']= url
                    new_cam['ip'] = ip
                    new_cam['port'] = ip
                    
                    for u in camera_user :
                        auth = [requests.auth.HTTPBasicAuth(u[0],u[1]), requests.auth.HTTPDigestAuth(u[0],u[1])]
                        for a in auth : 
                            r2 = requests.get(url, auth = a , stream=False, timeout=1)
                            if r2.ok:
                                new_cam['auth_type']= 'B'
                                new_cam['username'] = u[0]
                                new_cam['password'] = u[1]
                                rtsp = s['rtsp'].replace("<user>",u[0])
                                rtsp = rtsp.replace("<passd>",u[1])
                                rtsp = rtsp.replace("<ip>",ip)
                                rtsp = rtsp.replace("<port>",p)
                                new_cam['rtsp'] = rtsp
            except requests.exceptions.ConnectionError :
                pass
    if len(new_cam)==0:
        new_cam['name']= 'unknow'
        new_cam['ip'] = ip
        list_cam.append(new_cam)                
                
newCam(list_cam)
            
            
            
            
# camera_ip contains cam to inactive
            
            
""" 
new cam -> test scheme and set
inactive cam
"""


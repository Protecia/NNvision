# -*- coding: utf-8 -*-
"""
Created on Sat Dec  7 11:48:41 2019

@author: julien
"""

#import wsdiscovery
import json
import settings.settings as settings
import requests
from onvif import ONVIFCamera
from onvif.exceptions import ONVIFError
from log import Logger
import time
import socket
import psutil
import netifaces as ni
import xml.etree.ElementTree as ET
import re

logger = Logger('scan_camera').run()

'''
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
'''

def wsDiscovery():
    """Discover cameras on network using ws discovery.
    Returns:
        List: List of ips found in network.
    """
    addrs = psutil.net_if_addrs()
    ip_list = [ni.ifaddresses(i)[ni.AF_INET][0]['addr'] for i in addrs if i.startswith('e')]
    with open('soap.xml') as f:
        soap_xml = f.read()
    mul_ip = "239.255.255.250"
    mul_port = 3702
    ret = []
    dcam = {}
    for i in range(3):
        for ip in ip_list :
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 255)
            s.bind((ip, mul_port))
            s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP,
                         socket.inet_aton(mul_ip) + socket.inet_aton(ip))
            s.setblocking(False)
            s.sendto(soap_xml.encode(), (mul_ip, mul_port))
            time.sleep(2)
            while True:
                try:
                    data, address = s.recvfrom(65535)
                    time.sleep(1)
                    #print(address)
                    ret.append(data)
                except BlockingIOError :
                    pass
                    break
            #s.shutdown()
            s.close()
        for rep in ret:
            xml = ET.fromstring(rep)
            url = [ i.text for i in xml.iter('{http://schemas.xmlsoap.org/ws/2005/04/discovery}XAddrs') ][0]
            ip = re.search('http://(.*):',url).group(1)
            port = re.search('[0-9]+:([0-9]+)/', url).group(1)
            dcam[ip]=port
        time.sleep(20)
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
        logger.error('exception in setCam : {}'.format(ex))
        pass
    return False

def removeCam(cam):
    camJson = {'key':settings.KEY,'cam':cam}
    try :
        r = requests.post(settings.SERVER+"removeCam", json=camJson )
        s = json.loads(r.text)
        return s
    except (requests.exceptions.ConnectionError, json.decoder.JSONDecodeError) as ex :
        logger.error('exception in remove cam : {}'.format(ex))
        pass
    return False
    

def compareCam(ws, lock):
    with lock:
        with open('camera/camera.json', 'r') as out:
            cameras = json.loads(out.read())
    cameras_ip =  [ c['ip'] for c in cameras if c['from_client'] is True]
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
    # cameras could have wait_for_set camera : 
    for cam in cameras :
        if cam['wait_for_set']:
            for user , passwd in cameras_users:
                onvif = getOnvifUri(cam['ip'],cam['port_onvif'],user,passwd)
                if onvif :
                    info, rtsp , http = onvif
                    auth = {'B':requests.auth.HTTPBasicAuth(user,passwd), 'D':requests.auth.HTTPDigestAuth(user,passwd)}
                    for t, a in auth.items() :
                        try:
                            r = requests.get(http, auth = a , stream=False, timeout=1)
                            if r.ok:
                                cam['brand']=info['Manufacturer']
                                cam['model']=info['Model']
                                cam['url']= http
                                cam['auth_type']= t
                                cam['username'] = user
                                cam['password'] = passwd
                                cam['active'] = True
                                cam['wait_for_set'] = False
                                cam['rtsp'] = rtsp.split('//')[0]+'//'+user+':'+passwd+'@'+rtsp.split('//')[1]
                                list_cam.append(cam)
                        except requests.exceptions.ConnectionError :
                            pass 
    # cameras_ip contains cam now unreachable
    return list_cam, cameras_ip

def getCam(lock, force='0'):
    try :
        r = requests.post(settings.SERVER+"getCam", data = {'key': settings.KEY, 'force':force} )
        c = json.loads(r.text)
        if not c==False :
            with lock:
                with open('camera/camera.json', 'w') as out:
                    json.dump(c,out)
            r = requests.post(settings.SERVER+"upCam", data = {'key': settings.KEY})
        return c
    except (requests.exceptions.ConnectionError, json.decoder.JSONDecodeError) as ex :
        logger.error('exception in getCam: {}'.format(ex))
        return False
        pass

def run(period, lock, E_cam_start, E_cam_stop):
    force = '1'
    while True :
        # scan the cam on the network
        ws = wsDiscovery()
        # pull the cam from the server
        cam = getCam(lock, force)
        # check if changes
        if cam==False :
            E_cam_start.set()
            force = '0'
            logger.info('camera unchanged : E_cam_start is_set {}'.format(E_cam_start.is_set()))
        else :
            E_cam_stop.set()
            force = '1'
            logger.info(' ********* camera changed : E_cam_stop is_set {}'.format(E_cam_start.is_set()))
        # compare the cam with the camera file
        list_cam, remove_cam = compareCam(ws, lock)
        # push the cam to the server
        if list_cam : setCam(list_cam)
        # inactive the cam
        if remove_cam : removeCam(remove_cam)
        # wait for the loop
        time.sleep(period)
        






# camera_ip contains cam to inactive


"""
new cam -> test scheme and set
inactive cam
"""


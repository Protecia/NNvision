# -*- coding: utf-8 -*-
"""
Created on Sat Dec  7 11:48:41 2019

@author: julien
"""

import wsdiscovery
import json

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

ws = wsDiscovery()
with open('camera/camera.json', 'r') as json_file:
    cameras = json.load(json_file)
cameras_ip =  [ c['ip'] for c in cameras]

for c in ws :
        if c in cameras_ip :
            cameras_ip.remove(c)
            
# ws contains new cam
# camera_ip contains cam to inactive
            
            
""" 
new cam -> test scheme and set
inactive cam
"""


# -*- coding: utf-8 -*-

import os
import cv2
import time
import psutil as ps
import socket
import subprocess
from wifi import Cell
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .models import Camera, Result, Info, Alert
from.forms import AlertForm
from PIL import Image

# Create your views here.

def process():
    _process = [[],[]]
    for p in ps.process_iter():
        try :
            for n in p.cmdline():
                if 'process_camera' in n : _process[0].append(p)
                if 'process_alert' in n : _process[1].append(p)
        except ps.AccessDenied :
            pass
    return _process

@login_required
def index(request):
    d_action = request.POST.get('d_action')
    if d_action == 'start':
        subprocess.Popen([settings.PYTHON,os.path.join(settings.BASE_DIR,'app1/process_camera.py')])
        subprocess.Popen([settings.PYTHON,os.path.join(settings.BASE_DIR,'app1/process_alert.py')])
        time.sleep(2)
    if d_action == 'stop' :
        p = process()
        [ item.kill() for sublist in p for item in sublist]
        time.sleep(2)
    p = process()
    if len(p[0])>0 and len(p[1])>0 :
        running = True
    elif len(p[0])==0 and len(p[1])==0:
        running = False
    else : 
        [ item.kill() for sublist in p for item in sublist]
        running = False

    context = {'info' : Info.objects.get(), 'url_for_index' : '/','running':running}
    return render(request, 'app1/index.html',context)

@login_required
def camera(request):
    p = process()
    if len(p[0])==0 :
        subprocess.Popen([settings.PYTHON,os.path.join(settings.BASE_DIR,'app1/process_camera.py')])
    camera = Camera.objects.all()
    camera_array = [camera[i:i + 3] for i in range(0, len(camera), 3)]
    context = {'camera' :camera_array, 'info' : Info.objects.get(), 'url_for_index' : '/',}
    return render(request, 'app1/camera.html',context)

@login_required
def darknet(request):
    d_action = request.POST.get('d_action')
    p = process()
    message = None
    if d_action == 'start':
        if len(p[0])>0 : message = "Darknet already running, stop ip if you want to restart"
        else :
            subprocess.Popen([settings.PYTHON,os.path.join(settings.BASE_DIR,'app1/process_camera.py')])
            subprocess.Popen([settings.PYTHON,os.path.join(settings.BASE_DIR,'app1/process_alert.py')])
            time.sleep(2)
    if d_action == 'stop' :
        if len(p[0])==0 and len(p[1])==0 : message = "Servers are not running !" 
        else :
            [ item.kill() for sublist in p for item in sublist]
    context = { 'message' : message, 'category' : 'warning', 'd_action' :d_action, 'url_state' : '/darknet/state'}
    return render(request, 'app1/darknet.html', context)

def darknet_state(request):
    p = process()
    raw=''
    if len(p[0])>0:
        raw += 'Darknet server is running (PID : {}). '.format(p[0][0].pid)
    if len(p[1])>0:
        raw += 'Alert server is running (PID : {}). '.format(p[1][0].pid)
    if len(p[0])==0 and len(p[1])==0 :
        raw += 'Servers are stopped'
    return HttpResponse(raw)

@login_required
def panel(request, first, first_alert):
    first=int(first)
    first_alert=int(first_alert)
    imgs = Result.objects.all().order_by('-id')[first:first+12]
    img_array = [imgs[i:i + 3] for i in range(0, len(imgs), 3)]
    imgs_alert = Result.objects.filter(alert=True).order_by('-id')[first_alert:first_alert+3]
    img_alert_array = [imgs_alert[i:i + 3] for i in range(0, len(imgs_alert), 3)]
    context = { 'first' : first, 'first_alert' : first_alert, 'img_array' : img_array, 'img_alert_array' : img_alert_array}
    return render(request, 'app1/panel.html', context)

@login_required
def panel_detail(request, id):
    img = Result.objects.get(id=id)
    return render(request, 'app1/panel_detail.html', {'img':img, 'id':id})

@login_required
def alert(request, id=0):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = AlertForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            form.save()
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return HttpResponseRedirect('/alert')


    # if a GET (or any other method) we'll create a blank form
    else:
        form = AlertForm()
    if id !=0 :
        Alert.objects.get(pk=id).delete()     
    
    alert = Alert.objects.all()
    return render(request, 'app1/alert.html', {'message' : form.errors, 'category' : 'warning','form': form, 'alert':alert})

@login_required
def configuration(request):
    try:
        connect = subprocess.check_output(['iwgetid', '-r'])
    except :
        connect = 'none'
        pass
    try :
    # works only on linux system
        wifi = list(Cell.all('wlan0'))
        conf = Fileconf.from_file('/etc/wpa_supplicant/wpa_supplicant.conf')
    except :
    # give fake values on windows platform
        context.update({'ip' : find_local_ip(),'hostname' : socket.gethostname(), 
        'wifi' : [{ 'ssid' : 'test network' , 'quality' : '0/70' , 'encrypted' : 'secure' },{ 'ssid' : 'reseau test2' , 'quality' : '0/70' , 'encrypted' : 'secure' }],  'conf' : [{'ssid' : 'reseau test', 'opts' : {'priority' : '1'}},{'ssid' : 'reseau test2', 'opts' : {'priority' : '5'}},], 'connect' : 'reseau test' })
        pass
    else :
        # Adding new context specific to the view here :
        context.update({'ip' : find_local_ip(),'hostname' : socket.gethostname(), 
        'wifi' : wifi, 'conf' : conf.network_list, 'connect' : connect })
    return render(request, 'app1/settings.html', context)




@login_required
def wifi_add(request):
    try :
    # works only on linux system
        conf = Fileconf.from_file('/etc/wpa_supplicant/wpa_supplicant.conf')
    except :
    # give fake values on windows platform
        pass
        return HttpResponseRedirect('/settings')
    wifi_ssid = request.POST['wifi_ssid']
    wifi_psk = request.POST['wifi_psk']
    wifi_priority = request.POST['wifi_priority']
    opts = {}
    if wifi_psk != '' : opts = { 'psk' : wifi_psk, }
    if wifi_priority != 'Aucune' : opts.update({'priority' : wifi_priority})
    (res, msg) = conf.add(wifi_ssid, **opts)
    if res : conf.make_new()
    message = { 'ok' : None, 'ssid' : "Wrong network name !", 'psk' : "Wrong password !"} 
    context.update({ 'message' : message[msg], 'category' : 'warning'})
    return HttpResponseRedirect('/settings')

@login_required
def wifi_suppr(request):
    try :
    # works only on linux system
        conf = Fileconf.from_file('/etc/wpa_supplicant/wpa_supplicant.conf')
    except :
    # give fake values on wondows platform
        pass
        return HttpResponseRedirect('/settings')
    wifi_ssid = request.POST['wifi_ssid']
    res = conf.suppr(wifi_ssid)
    if res : conf.make_new()
    message = { True : "Network deleted" , False : "Can't suppress the network !"} 
    context.update({ 'message' : message[res], 'category' : 'success'})
    return HttpResponseRedirect('/settings')

@login_required
def wifi_restart(request):
    try :
        res1 = subprocess.call(['sudo', 'ifdown', 'wlan0'])
        time.sleep(1)
        res2 = subprocess.call(['sudo', 'ifup', 'wlan0'])
    except :
    # return on fail (windows)
        pass
        return HttpResponseRedirect('/settings')
    if res1 == 0 and res2 == 0 : context.update({ 'message' : 'Wifi restarted', 'category' : 'success'})
    else :  context.update({ 'message' : 'Unable to restart wifi', 'category' : 'warning'})
    return HttpResponseRedirect('/settings')

@login_required
def reboot(request):
    try :
        command = '(sleep 2 ; sudo reboot) &'
        subprocess.call(command, shell=True)
    except :
    # return on fail (windows)
        pass
    return HttpResponseRedirect('/')


@login_required
def last(request, cam):
    img = '/media/tempimg_cam'+str(cam)+'_box.jpg'
    return render(request, 'app1/last_img.html', {'img':img})

@login_required
def get_last_analyse_img(request,cam_id):
    path_img_box = os.path.join(settings.MEDIA_ROOT,'tempimg_cam'+str(cam_id)+'_box.jpg')
    try :
        age = time.time()-os.path.getmtime(path_img_box)
    except FileNotFoundError :
        path_img_broken = os.path.join(settings.STATIC_ROOT,'app1','img','image-not-found.jpg')
        image_data = open(path_img_broken, "rb").read()
        return HttpResponse(image_data, content_type="image/jpg")
    if age > 60 :
        path_img_wait = os.path.join(settings.STATIC_ROOT,'app1','img','gifwait.gif')
        image_data = open(path_img_wait, "rb").read()
        return HttpResponse(image_data, content_type="image/gif")
    #cam = Camera.objects.get(id=cam_id)
    while True :
        try :
            im = Image.open(path_img_box)
        except OSError:
            continue
        response = HttpResponse(content_type='image/jpg')
        try:
            im.save(response, 'JPEG')
            break
        except OSError:
            continue
    return response



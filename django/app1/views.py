# -*- coding: utf-8 -*-

import os
import time
import psutil as ps
import socket
import subprocess
from wifi import Cell
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.conf import settings
from .models import Camera, Result, Info, Alert
from.forms import AlertForm
from .wpa_wifi import Network, Fileconf

# Create your views here.


def process():
    return ([p for p in ps.process_iter() if 'app1/process_camera.py' in p.cmdline()],
             [p for p in ps.process_iter() if 'app1/process_alert.py' in p.cmdline()])


def index(request):
    context = {'info' : Info.objects.get(), 'url_for_index' : '/',}
    return render(request, 'app1/index.html',context)

def camera(request):
    p = subprocess.Popen(['python3','/home/nnvision/NNvision/django/app1/process_alert.py'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    (out,err)= p.communicate()
    message = out.decode()+err.decode()
    context = {'message' : message, 'category' : 'warning', 'camera' : Camera.objects.all(), 'info' : Info.objects.get(), 'url_for_index' : '/',}
    return render(request, 'app1/camera.html',context)

def darknet(request):
    d_action = request.POST.get('d_action')
    p = process()
    message = None
    if d_action == 'start':
        if len(p[0])>0 : message = "Darknet already running, stop ip if you want to restart"
        else :
            subprocess.Popen(['python3','/home/nnsision/NNvision/django/app1/process_camera.py'])
            subprocess.Popen(['python3','app1/process_alert.py'])
            time.sleep(2)
    if d_action == 'stop' :
        if len(p[0])==0 : message = "Darknet is not running !" 
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

def panel(request, first):
    #first=int(first)
    imgs = Result.objects.all().order_by('-id')[first:first+30]
    img_array = [imgs[i:i + 3] for i in range(0, len(imgs), 3)]
    context = { 'first' : first, 'img_array' : img_array}
    return render(request, 'app1/panel.html', context)

def panel_detail(request, id):
    img = Result.objects.get(id=id)
    return render(request, 'app1/panel_detail.html', {'img':img, 'id':id})


def alert(request):
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
    alert = Alert.objects.all()
    return render(request, 'app1/alert.html', {'message' : form.errors, 'category' : 'warning','form': form, 'alert':alert})

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
    
    
    
def reboot(request):
    try :
        command = '(sleep 2 ; sudo reboot) &'
        subprocess.call(command, shell=True)
    except :
    # return on fail (windows)
        pass
    return HttpResponseRedirect('/')    
    
def shutdown(request):
    try : 
        subprocess.call(['sudo', 'halt'])
    except :
    # return on fail (windows)
        pass
    return HttpResponseRedirect('/')    



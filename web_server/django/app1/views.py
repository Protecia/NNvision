# -*- coding: utf-8 -*-

import os
import time
import psutil as ps
from subprocess import Popen, STDOUT, call
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Count
from .models import Camera, Result, Alert, Client
from .forms import AlertForm, AutomatForm, DAY_CODE_STR
from .process_alert import stop_adam_all
from PIL import Image
from django.utils import translation
from crontab import CronTab
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

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

@csrf_exempt
def upload(request):
    if request.method == 'POST':
        key = request.POST.get('key', 'default')
        file = request.FILES['myFile']  
        size = len(file)
        return JsonResponse([{'size':size},],safe=False) 
    return "not post"

@csrf_exempt
def uploadresult(request):
    key = request.POST.get('key', 'default')
    json = request.body
    return JsonResponse([{'statut':True},],safe=False) 

@csrf_exempt
def getCam(request):
    key = request.POST.get('key', 'default')
    force = request.POST.get('force', '0')
    cam = Camera.objects.filter(client__key=key)
    if force=='1' or any([c.update for c in cam]):
        return JsonResponse(list(cam.values()), safe=False)
    time.sleep(10)
    return HttpResponse('0') 

@csrf_exempt
def upCam(request):
    key = request.POST.get('key', 'default')
    Camera.objects.filter(active=True, client__key=key).update(update=False)
    return HttpResponse('0') 
    
@csrf_exempt
def getState(request):
    key = request.POST.get('key', 'default')
    i=0
    while i<10 :
        c = Client.objects.filter(key=key)
        _c = c[0]
        if not _c.change:
            time.sleep(1)
        else :
            _c.change = False
            _c.save()
            break
        i+=1
    return JsonResponse(list(c.values()), safe=False)
    
    
    


def index(request):
    user_language = 'fr'
    translation.activate(user_language)
    request.session[translation.LANGUAGE_SESSION_KEY] = user_language
    alert = Alert.objects.filter(active=True)
    if len(alert) != 0:
        return redirect('/warning/0')
    if not request.user.is_authenticated or not request.user.has_perm('app1.camera'):
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
    d_action = request.POST.get('d_action')
    if d_action == 'start' and len(process()[0])==0:
        Camera.objects.all().update(rec=True)
        #if settings.DEBUG:
        if True:
            with open(os.path.join(settings.BASE_DIR,'process_camera.log'), 'w') as log:
                Popen([settings.PYTHON,os.path.join(settings.BASE_DIR,'app1/process_camera.py')], 
                      stdout=log, stderr=STDOUT)
            with open(os.path.join(settings.BASE_DIR,'process_alert.log'), 'w') as loga:
                Popen([settings.PYTHON,os.path.join(settings.BASE_DIR,'app1/process_alert.py')], 
                      stdout=loga, stderr=STDOUT)
        else:
            Popen([settings.PYTHON,os.path.join(settings.BASE_DIR,'app1/process_camera.py')])
            Popen([settings.PYTHON,os.path.join(settings.BASE_DIR,'app1/process_alert.py')])
        time.sleep(2)
    if d_action == 'stop' :
        stop_adam_all()
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

    context = {'info' : {'version' : settings.VERSION, 'darknet_path' : settings.DARKNET_PATH}, 'url_for_index' : '/','running':running, 'logo_client':settings.RESELLER_LOGO}
    return render(request, 'app1/index.html',context)

def warning(request, first_alert):
    alert = Alert.objects.filter(active=True).order_by('when')
    action = request.POST.get('alert')
    if action == 'cancel':
        for a in alert :
            a.active = False
            a.save()
        stop_adam_all()
        return redirect('/')
    
    alert = alert.first() 
    if not alert :
        return redirect('/')    
    
    first_alert=int(first_alert)
    imgs_alert = Result.objects.filter(alert=True).filter(time__gte=alert.when).order_by('-id')[first_alert:first_alert+9]
    img_alert_array = [imgs_alert[i:i + 3] for i in range(0, len(imgs_alert), 3)]
    context = { 'first_alert' : first_alert, 'img_alert_array' : img_alert_array}
    return render(request, 'app1/warning.html', context)
    

@login_required
@permission_required('app1.camera')
def camera(request):
    p = process()
    if len(p[0])==0 :
        Camera.objects.all().update(rec=False)
        Popen([settings.PYTHON,os.path.join(settings.BASE_DIR,'app1/process_camera.py')])
    camera = Camera.objects.filter(active=True)
    camera_array = [camera[i:i + 3] for i in range(0, len(camera), 3)]
    context = {'camera' :camera_array, 'info' : {'version' : settings.VERSION, 'darknet_path' : settings.DARKNET_PATH}, 'url_for_index' : '/','logo_client':settings.RESELLER_LOGO}
    return render(request, 'app1/camera.html',context)

@login_required
@permission_required('app1.camera')
def darknet(request):
    d_action = request.POST.get('d_action')
    p = process()
    message = None
    if d_action == 'start':
        if len(p[0])>0 : message = "Darknet already running, stop ip if you want to restart"
        else :
            Camera.objects.all().update(rec=True)
            Popen([settings.PYTHON,os.path.join(settings.BASE_DIR,'app1/process_camera.py')])
            Popen([settings.PYTHON,os.path.join(settings.BASE_DIR,'app1/process_alert.py')])
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
@permission_required('app1.camera')
def panel(request, nav, first):
    if request.method == 'POST':
        actionForm = request.POST.get("valid_filter", "")
        if actionForm == 'ok':
            id_stuffs = request.POST.get("stuffs", "")
            with translation.override('en'):
                stuffs = str(Alert.stuffs_d.get(int(id_stuffs)))
            request.session['class']= stuffs
        else :
            request.session['class']= 'all'
    filter_class = request.session.get("class","all")
    if not Result.objects.all():
        img_array = []
        img_alert_array = []
        form = AlertForm()
        context = { 'class':filter_class, 'form':form, 'first' : first,
               'first_alert' : first, 'img_array' : img_array, 'img_alert_array' : img_alert_array, 'logo_client':settings.RESELLER_LOGO}
        return render(request, 'app1/panel.html', context)  
    if filter_class == "all" :
        if nav == 'd':
            imgs = Result.objects.all().order_by('-id')[first:first+12]
            if imgs :
                time_result = imgs[0].time
            else:
                time_result = Result.objects.all().earliest('time').time
            imgs_alert = Result.objects.filter(alert=True, time__lte=time_result).order_by('-id')[:3]
            first_alert = len(Result.objects.filter(alert=True, time__gt=time_result))
        if nav == 'a':
            imgs_alert = Result.objects.filter(alert=True).order_by('-id')[first:first+3]
            if imgs_alert :
                time_result = imgs_alert[0].time
            else :
                time_result = Result.objects.filter(alert=True).earliest('time').time
            imgs = Result.objects.filter(time__lte=time_result).order_by('-id')[:12]
            first_alert = first
            first = len(Result.objects.filter(time__gt=time_result))
    else :
        if nav == 'd':
            imgs = Result.objects.filter(object__result_object__contains=filter_class).order_by('-id').annotate(c=Count('object__result_object'))[first:first+12]
            if imgs :
                time_result = imgs[0].time
            else:
                time_result = Result.objects.all().earliest('time').time
            imgs_alert = Result.objects.filter(alert=True, time__lte=time_result, object__result_object__contains=filter_class).order_by('-id').annotate(c=Count('object__result_object'))[:3]
            first_alert = len(Result.objects.filter(alert=True, time__gte=time_result, object__result_object__contains=filter_class).order_by('-id').annotate(c=Count('object__result_object')))
        if nav == 'a':
            imgs_alert = Result.objects.filter(alert=True, object__result_object__contains=filter_class).order_by('-id').annotate(c=Count('object__result_object'))[first:first+3]
            if imgs_alert :
                time_result = imgs_alert[0].time
            else :
                time_result = Result.objects.filter(alert=True).earliest('time').time
            imgs = Result.objects.filter(time__lte=time_result, object__result_object__contains=filter_class).order_by('-id').annotate(c=Count('object__result_object'))[:12]
            first_alert = first
            first = len(Result.objects.filter(time__gte=time_result, object__result_object__contains=filter_class).order_by('-id').annotate(c=Count('object__result_object')))        
    img_array = [imgs[i:i + 3] for i in range(0, len(imgs), 3)]
    img_alert_array = [imgs_alert[i:i + 3] for i in range(0, len(imgs_alert), 3)]
    form = AlertForm()
    context = { 'class':filter_class, 'form':form, 'first' : first,
               'first_alert' : first_alert, 'img_array' : img_array, 'img_alert_array' : img_alert_array, 'logo_client':settings.RESELLER_LOGO}
    return render(request, 'app1/panel.html', context)

@login_required
@permission_required('app1.camera')
def panel_detail(request, id):
    img = Result.objects.get(id=id)
    return render(request, 'app1/panel_detail.html', {'img':img, 'id':id})


def warning_detail(request, id):
    img = Result.objects.get(id=id)
    alert = Alert.objects.filter(active=True).order_by('when')
    alert = alert.first() 
    if not alert :
        return redirect('/')
    imgs_alert = Result.objects.filter(alert=True).filter(time__gte=alert.when)
    ids = [i.id for i in imgs_alert]
    if id in ids:
        return render(request, 'app1/panel_detail.html', {'img':img, 'id':id})
    else:
        return redirect('/')
        

@login_required
@permission_required('app1.camera')
def alert(request, id=0, id2=-1):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        typeForm = request.POST.get("type", "")
        # create a form instance and populate it with data from the request:
        if typeForm == "alert": 
            form = AlertForm(request.POST)
            # check whether it's valid:
            if form.is_valid()  :
                form.save()
                return HttpResponseRedirect('/alert')
            else :
                aform = AutomatForm()
        elif typeForm ==  "auto":
            form = AutomatForm(request.POST)
            # check whether it's valid:
            if form.is_valid():
                # process the data in form.cleaned_data as required
                d = form.cleaned_data['day']
                h = form.cleaned_data['hour']
                m = form.cleaned_data['minute']
                a = form.cleaned_data['action']
                cron = CronTab(user=True)
                cmd = settings.PYTHON+' '+os.path.join(settings.BASE_DIR,'app1/_running.py '+a)
                job  = cron.new(command=cmd)
                job.minute.on(m)
                job.hour.on(h)
                if d!='*' :
                    job.dow.on(d)
                cron.write()
                # redirect to a new URL:
                return HttpResponseRedirect('/alert')
            else :
                form = AlertForm()
    # if a GET (or any other method) we'll create a blank form
    else:
        form = AlertForm()
        aform = AutomatForm()
    if id !=0 :
        Alert.objects.get(pk=id).delete()     
    if id2 != -1:
        cron = CronTab(user=True)
        cron.remove(cron[int(id2)])
        cron.write()   
    
    # get all the alert and all the automatism 
    alert = Alert.objects.all()
    cron = CronTab(user=True)
    auto = [(c.minute.render(), c.hour.render(), DAY_CODE_STR[c.dow.render()], c.command.split()[2]) for c in cron]
    #auto = [(a[0],a[1],DAY_CODE_STR[a[4]],a[-1]) for a in auto]
    return render(request, 'app1/alert.html', {'message' : form.non_field_errors,
           'category' : 'warning','form': form, 'alert':alert, 'aform':aform, 
           'auto':auto, 'no_free':settings.ACCESS_NO_FREE, 'adam':settings.ACCESS_ADAM, 'hook':settings.ACCESS_HOOK, 'logo_client':settings.RESELLER_LOGO })


@login_required
@permission_required('app1.camera')
def last(request, cam):
    img = '/media/tempimg_cam'+str(cam)+'_box.jpg'
    return render(request, 'app1/last_img.html', {'img':img})


@login_required
@permission_required('app1.camera')
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
            im.thumbnail((settings.IMAGE_REAL_TIME_MAX_WIDTH,settings.IMAGE_REAL_TIME_MAX_HIGH), Image.ANTIALIAS)
            im.save(response, 'JPEG')
            break
        except OSError:
            continue
    return response


def thumbnail(request,path_im):
    try :
        im = Image.open(path_im)
    except OSError :
        path_img_broken = os.path.join(settings.STATIC_ROOT,'app1','img','image-not-found.jpg')
        im = Image.open(path_img_broken)
        pass
    response = HttpResponse(content_type='image/jpg')
    im.thumbnail((settings.IMAGE_PANEL_MAX_WIDTH,settings.IMAGE_PANEL_MAX_HIGHT), Image.ANTIALIAS)
    im.save(response, 'JPEG')
    return response
    
    
    

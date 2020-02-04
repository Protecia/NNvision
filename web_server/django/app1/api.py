# -*- coding: utf-8 -*-
"""
Created on Thu Dec 26 10:34:51 2019

@author: julien
"""
import os
import time
from .models import Camera, Result, Client, Object
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
import json
from django.db import transaction
from django.http import HttpResponse
from django.conf import settings
from PIL import Image, ImageFont, ImageDraw
import subprocess
import glob

def delete_space(client):
    ##### check the space on disk to respect the quota #######
    path = os.path.join(settings.MEDIA_ROOT,client.folder)
    size = int(subprocess.check_output(['du','-sh', path]).split()[0].decode('utf-8').split('M')[0])
    if size>client.space_allowed:
        r_to_delete = Result.objects.all()[:300]
        for im_d in r_to_delete:
            if 'jpg' in  im_d.file :
                try :
                    os.remove(os.path.join(path,im_d.file))
                except OSError:
                    pass
            im_d.delete()

def purge_files(client):
        r = Result.objects.all().order_by('time')
        if len(r)>0 :
            r = r[0]
            time_older = r.time.timestamp()
            path = settings.MEDIA_ROOT+'/'+r.file1.name.split('/')[0]
            os.chdir(path)
            for file in glob.glob("*.jpg"):
                 if os.path.getctime(file) < time_older :
                     os.remove(file)
            path = settings.MEDIA_ROOT+'/'+r.file2.name.split('/')[0]
            os.chdir(path)
            for file in glob.glob("*.jpg"):
                 if os.path.getctime(file) < time_older :
                     os.remove(file)


@csrf_exempt
def setCam(request):
    data = json.loads(request.body.decode())
    try :
        client = Client.objects.get(key=data['key'])
    except :
        time.sleep(10)
        pass
        return JsonResponse({'statut':False},safe=False)
    cam = data['cam']
    for c in cam:
        cam, created = Camera.objects.update_or_create(client = client, ip = c['ip'], defaults=c)
        try :
            cam.save()
            client.update_camera = True
            client.save()
        except IntegrityError:
            pass
    return JsonResponse({'statut':True},safe=False)

@csrf_exempt
def removeCam(request):
    data = json.loads(request.body.decode())
    try :
        client = Client.objects.get(key=data['key'])
    except :
        time.sleep(10)
        pass
        return JsonResponse({'statut':False},safe=False)
    cam = data['cam']
    for ip in cam:
        Camera.objects.filter(client = client, ip = ip).update(active=False)
    client.update_camera = True
    client.save()
    return JsonResponse({'statut':True},safe=False)

@csrf_exempt
def uploadImage(request):
    if request.method == 'POST':
        key = request.POST.get('key', 'default')
        img_name = request.POST.get('img_name', 'default')
        cam = request.POST.get('cam', 'default')
        result = request.POST.get('result', False)
        real_time = request.POST.get('real_time', True)
        resize_factor = float(request.POST.get('resize_factor', 1))
        try :
            client = Client.objects.get(key=key)
            camera = Camera.objects.get(pk=cam)
        except :
            time.sleep(10)
            pass
            return JsonResponse({'statut':False},safe=False)
        delete_space(client)
        img = request.FILES['myFile']
        size = len(img)
        img_path = settings.MEDIA_ROOT+'/'+client.folder+'/'+img_name
        os.makedirs(os.path.dirname(img_path), exist_ok=True)
        if not real_time :
            with open(img_path+'_no_box.jpg', 'wb') as file:
                file.write(img.read())
        img_pil = Image.open(img)
        draw = ImageDraw.Draw(img_pil)
        result_filtered = json.loads(result)
        for r in result_filtered :
            outline = "green"
            if r[2][2]*r[2][3] < camera.max_object_area_detection : outline = "red"
            box = ((int((r[2][0]-(r[2][2]/2))*resize_factor),
                    int((r[2][1]-(r[2][3]/2))*resize_factor)),
                   (int((r[2][0]+(r[2][2]/2))*resize_factor),
                    int((r[2][1]+(r[2][3]/2))*resize_factor)))
            draw.rectangle(box, outline=outline, width = int(3*resize_factor)+1)
            draw.text(box[1], r[0], fill=outline, font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",int(30*resize_factor)))
        img_pil.save(img_path+'.jpg', "JPEG")
        return JsonResponse([{'size':size, 'name':img_path},],safe=False)
    return JsonResponse([{'statut':'ko', },],safe=False)

@csrf_exempt
def uploadResult(request):
    data = json.loads(request.body.decode())
    try :
        client = Client.objects.get(key=data['key'])
        camera = Camera.objects.get(pk=data['cam'])
    except :
        time.sleep(10)
        pass
        return JsonResponse({'statut':False},safe=False)
    with transaction.atomic():
       result_DB = Result(camera=camera,file = client.folder+'/'+data['img'], brut=data['result_darknet'])
       result_DB.save()
       for r in data['result_filtered']:
           object_DB = Object(result = result_DB,
                              result_object=r[0],
                              result_prob=r[1],
                              result_loc1=r[2][0],
                              result_loc2=r[2][1],
                              result_loc3=r[2][2],
                              result_loc4=r[2][3])
           object_DB.save()
    return JsonResponse([{'statut':True},],safe=False)

@csrf_exempt
def getCam(request):
    key = request.POST.get('key', 'default')
    force = request.POST.get('force', '0')
    cam = Camera.objects.filter(client__key=key).order_by('pk')
    if force=='1':
        return JsonResponse(list(cam.values()), safe=False)      
    i=0
    while i<20 :
        cam = Camera.objects.filter(client__key=key).order_by('pk')
        if cam.last().client.update_camera:
            return JsonResponse(list(cam.values()), safe=False)
        time.sleep(1)
        i+=1
    return JsonResponse(False, safe=False)

@csrf_exempt
def upCam(request):
    key = request.POST.get('key', 'default')
    Client.objects.filter(key=key).update(update_camera=False)
    return HttpResponse('0')

@csrf_exempt
def getState(request):
    key = request.POST.get('key', 'default')
    i=0
    while i<20 :
        c = Camera.objects.filter(client__key=key)
        _c = c[0].client
        if not _c.change:
            time.sleep(1)
        else :
            _c.change = False
            _c.save()
            break
        i+=1
    response = {'rec' :_c.rec,}
    cam_dict = {}
    for cam in c:
        cam_dict[cam.id]=[cam.on_camera_LD,cam.on_camera_HD]
    response['cam']=cam_dict
    return JsonResponse(response, safe=False)
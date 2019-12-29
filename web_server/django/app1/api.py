# -*- coding: utf-8 -*-
"""
Created on Thu Dec 26 10:34:51 2019

@author: julien
"""
import os
import time
from .models import Camera, Result, Client, Scheme, Object
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
import json
from django.db import transaction
from django.http import HttpResponse
from django.conf import settings
from PIL import Image, ImageFont, ImageDraw

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
        except IntegrityError:
            pass
    return JsonResponse({'statut':True},safe=False)

@csrf_exempt
def getScheme(request):
    key = request.POST.get('key', 'default')
    if len(Client.objects.filter(key=key))>0 :
        scheme = Scheme.objects.all()
        return JsonResponse(list(scheme.values()), safe=False)
    return JsonResponse('0',safe=False)

@csrf_exempt
def uploadImage(request):
    if request.method == 'POST':
        key = request.POST.get('key', 'default')
        img_name = request.POST.get('img_name', 'default')
        result = request.POST.get('result', False)
        real_time = request.POST.get('real_time', True)
        try :
            client = Client.objects.get(key=key)
        except :
            time.sleep(10)
            pass
            return JsonResponse({'statut':False},safe=False)
        img = request.FILES['myFile']
        size = len(img)
        img_path = settings.MEDIA_ROOT+'/'+str(client.id)+'/'+img_name
        os.makedirs(os.path.dirname(img_path), exist_ok=True)
        if not real_time :
            with open(img_path+'_no_box.jpg', 'wb') as file:
                file.write(img.read())
        img_pil = Image.open(img)
        draw = ImageDraw.Draw(img_pil)
        result_filtered = json.loads(result)
        for r in result_filtered :
            box = ((int(r[2][0]-(r[2][2]/2)),int(r[2][1]-(r[2][3]/2
                ))),(int(r[2][0]+(r[2][2]/2)),int(r[2][1]+(r[2][3]/2
                ))))
            draw.rectangle(box, outline="green", width = 3)
            draw.text(box[1], r[0], fill="green", font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",30))
        img_pil.save(img_path+'.jpg', "JPEG")
        return JsonResponse([{'size':size, 'name':img_path},],safe=False)
    return "not post"

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
       result_DB = Result(camera=camera,file = str(client.id)+'/'+data['img'], brut=data['result_darknet'])
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
    cam = Camera.objects.filter(client__key=key)
    if force=='1' or any([c.update for c in cam]):
        return JsonResponse(list(cam.values()), safe=False)
    time.sleep(20)
    return JsonResponse(list(cam.values()), safe=False)

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
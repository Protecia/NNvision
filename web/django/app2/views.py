# -*- coding: utf-8 -*-
"""
Created on Sun Apr 14 21:29:53 2019

@author: julien
"""
import os
import glob
from subprocess import Popen
from django.conf import settings
from django.shortcuts import render
from .models import Image, Config
import datetime
import json
# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect

def index(request):
    directories = os.listdir(os.path.join(settings.MEDIA_ROOT,"training"))
    directories = [ d for d in directories if d !="__init__.py"]
    return render(request, 'app2/index.html',{'list_dataset':directories})


def dataset(request,dataset):
    config = Config.objects.filter(dataset=dataset)
    if len(config)==0:
        source_path = os.path.join(settings.MEDIA_ROOT,"training",dataset)
        files = glob.glob(source_path+"/*.jpg")
        query = Config(dataset=dataset, size = len(files))
        query.save()
        Popen([settings.PYTHON,os.path.join(settings.BASE_DIR,'app2/process_dataset.py'), dataset])
    elif not config[0].valid:
        progress = len(Image.objects.all())/config[0].size
        return HttpResponse('load images in progress : '+ progress)
    else:
        img = Image.objects.all()
        list_img = [i.name for i in img]
    return render(request, 'app2/dataset.html',{'list_img':list_img})
    


def img(request,img_name):
    if request.method == 'POST':
        bb = request.POST.get("box")
        file = request.POST.get("file")
        box = json.loads(bb)
        with open(file, 'w') as f:
            for b in box :
                line = str(b[0])+" "+str(b[1])+" "+str(b[2])+" "+str(b[3])+" "+str(b[4])
                f.write(line+"\n")
        return HttpResponseRedirect('/train/')
        #return HttpResponse(bb)
        
    try :
        conf = Config.objects.get()
        classes = conf.name.split(',')
        ratio = conf.ratio
    except :
        return HttpResponse("no config in the admin")
    img = Image.objects.get(name=(img_name))
    img.process = 0
    img.save()
    file = os.path.join(settings.MEDIA_ROOT,"training","basket",img.name.split('.')[0]+'.txt')
    
    
    
    bb = []
    try :
        with open(file, 'r') as f:
            content = f.readlines()
            for line in content:
                values_str = line.split()
                class_index, x_center, y_center, x_width, y_height = map(float, values_str)
                class_index = int(class_index)
                bb.append([class_index, x_center, y_center, x_width, y_height])
    except FileNotFoundError : 
        pass
        
    context = {'img' : "/media/training/basket/"+img.name, 'ratio' : ratio,
               'classes' : classes, 'file' : file, 'bb' : bb }
    return render(request, 'app2/img.html',context)


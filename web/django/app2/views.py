import glob
import os
from django.conf import settings
from django.shortcuts import render
from .models import Image, Config
import datetime
import json
# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect

def index(request):
    img = Image.objects.filter(process=0)[:20]
    list_img = [i.name for i in img]
    return render(request, 'app2/index.html',{'list_img':list_img})
    
    
    


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


def insert_img(request):
    source_path = os.path.join(settings.MEDIA_ROOT,"training","basket")
    files = glob.glob(source_path+"/*.jpg")
    
    for f in files :
        n = os.path.basename(f)
        query = Image(name = n , process = 0)
        query.save()
        
    return HttpResponse(files[0])
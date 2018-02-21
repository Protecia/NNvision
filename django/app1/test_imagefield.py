# -*- coding: utf-8 -*-
"""
Created on Tue Jan 30 22:26:47 2018

@author: julien
"""

from django.core import files
from io import BytesIO
import requests

url = "https://www.w3schools.com/howto/img_fjords.jpg"
resp = requests.get(url)
if resp.status_code != requests.codes.ok:
    print('error')

fp = BytesIO(resp.content)
#fp.write(resp.content)
file_name = url.split("/")[-1]  # There's probably a better way of doing this but this is just a quick example

#your_model.image_field.save(file_name, files.File(fp))


import sys, os
try:
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
except NameError:
    sys.path.append(os.path.abspath('..'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "projet.settings")
import django
django.setup()

from app1.models import Camera, Result, Object


cam = Camera.objects.all()

new = Result(camera=cam[0])
new.file.save(file_name,files.File(fp))
new.save()

from scipy.misc import imread
import cv2
img = imread('camera_images/detect_PoHKqsB')
img = cv2.imread('camera_images/detect_PoHKqsB',1)
img_rect = cv2.rectangle(img,(384,0),(510,128),(0,255,0),3)
img_rect_text = cv2.putText(img_rect,'OpenCV',(384,128), cv2.FONT_HERSHEY_SIMPLEX, 
                            1,(0,255,0),2)
#jpg = BytesIO(cv2.imencode('.jpg', img)[1].tobytes())
#jpg_rect = BytesIO(cv2.imencode('.jpg', img_rect)[1].tobytes())
jpg_rect_text = BytesIO(cv2.imencode('.jpg', img_rect_text)[1].tobytes())

jpg_rect_text = BytesIO(cv2.imencode('.jpg', img)[1].tobytes())


new = Result(camera=cam[0])
#new.file.save('test_jpg',files.File(jpg))
#new.file.save('test_rect_jpg',files.File(jpg_rect))
new.file2.save('test_rect_text_jpg',files.File(jpg_rect_text))

from matplotlib.pyplot import imshow
imshow(img)
imshow(img_rect_text)






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
new = Result(camera=cam[0])
new.file.save(file_name,files.File(fp))
new.save()




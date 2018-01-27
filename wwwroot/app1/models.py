from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible

# Create your models here.

# Informations about the camera you are using
@python_2_unicode_compatible  # only if you need to support Python 2
class Cameras(models.Model):
    name = models.CharField(max_length=20)
    key = models.CharField(max_length=20)
    url = models.URLField()
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=20)
    
    def __str__(self):
        return 'Camera list - id : {} - name : {} - url : {} - username : {} - password : {}'.format(self.id, self.name, self.url, self.username, self.password)

# Informations about the detection of the cameras
@python_2_unicode_compatible  # only if you need to support Python 2
class Results(models.Model):
    camera = models.ForeignKey(Cameras, on_delete=models.CASCADE)
    lastCaptureFile = models.ImageField(upload_to='camera_images/')
    lastCaptureTime = models.TimeField(auto_now=True)
    jsonresult = models.TextField(default = '{}')
    def __str__(self):
        return 'Number of rows : {}'.format(self.count())

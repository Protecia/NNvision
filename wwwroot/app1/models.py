from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible

# Create your models here.

# Informations about the camera you are using
@python_2_unicode_compatible  # only if you need to support Python 2
class Camera(models.Model):
    name = models.CharField(max_length=20)
    key = models.CharField(max_length=20)
    url = models.URLField()
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=20)
    
    def __str__(self):
        return 'Camera list - id : {} - name : {} - url : {} - username : {} - password : {}'.format(self.id, self.name, self.url, self.username, self.password)

# Informations about the detection of the cameras
@python_2_unicode_compatible  # only if you need to support Python 2
class Result(models.Model):
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE)
    lastCaptureFile = models.ImageField(upload_to='camera_images/')
    lastCaptureTime = models.TimeField(auto_now=True)
    jsonresult = models.TextField(default = '{}')
    def __str__(self):
        return 'Number of rows : {}'.format(self.count())

# Informations about the board you are using and the version of the webapp
@python_2_unicode_compatible  # only if you need to support Python 2
class Info(models.Model):
    version = models.CharField(max_length=10)
    board = models.CharField(max_length=200, default='Tegra X1')
    def __str__(self):
        return 'v{} on {}'.format(self.version, self.board)
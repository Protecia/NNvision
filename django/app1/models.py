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
        return 'id : {} - name : {} - url : {}'.format(self.id, self.name, self.url)

# Informations about the detection of the cameras
@python_2_unicode_compatible  # only if you need to support Python 2
class Result(models.Model):
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE)
    file = models.ImageField(upload_to='camera_images/')
    time = models.TimeField(auto_now=True)
    def __str__(self):
        return 'Camera : {} - at {}'.format(self.camera.name, self.time)

@python_2_unicode_compatible  # only if you need to support Python 2
class Object(models.Model):
    result = models.ForeignKey(Result, on_delete=models.CASCADE)
    result_object = models.CharField(max_length=20, default='')
    result_prob = models.DecimalField(default=0, max_digits=3, decimal_places=2)
    result_loc1 = models.DecimalField(default=0, max_digits=6, decimal_places=2)
    result_loc2 = models.DecimalField(default=0, max_digits=6, decimal_places=2)
    result_loc3 = models.DecimalField(default=0, max_digits=6, decimal_places=2)
    result_loc4 = models.DecimalField(default=0, max_digits=6, decimal_places=2)
    def __str__(self):
        return 'Objetc : {} with p={}'.format(self.result_object, self.result_prob)

# Informations about the board you are using and the version of the webapp
@python_2_unicode_compatible  # only if you need to support Python 2
class Info(models.Model):
    version = models.CharField(max_length=10)
    board = models.CharField(max_length=200, default='Tegra X1')
    def __str__(self):
        return 'v{} on {}'.format(self.version, self.board)
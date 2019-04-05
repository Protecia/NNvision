from django.db import models

# Create your models here.
class Image(models.Model):
    name = models.CharField(max_length=200, unique=True)
    time = models.DateTimeField(auto_now=False, blank=True, null=True)
    process = models.SmallIntegerField()
    
    
class Config(models.Model):
    name = models.CharField(max_length=200, unique=True)
    ratio = models.FloatField()

    

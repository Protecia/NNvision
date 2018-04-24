from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from datetime import datetime

@python_2_unicode_compatible
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True) # validators should be a list
    alert = models.BooleanField(default="False")
    class Meta:
        ordering = ['user']
        verbose_name = 'user'
        verbose_name_plural = 'users'
        
    def __str__(self):
        return 'user : {} - phone_number : {} - alert : {}'.format(self.user, self.phone_number, self.alert)
        
# Create your models here.

# Informations about the camera you are using
@python_2_unicode_compatible  # only if you need to support Python 2
class Camera(models.Model):
    AUTH_CHOICES = (
        ('B', 'Basic'),
        ('D', 'Digest'))
    name = models.CharField(max_length=20)
    active = models.BooleanField()
    url = models.URLField()
    auth_type = models.Charfield(choices=AUTH_CHOICES, default='B')
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=20)

    def __str__(self):
        return 'id : {} - name : {} - url : {}'.format(self.id, self.name, self.url)

# Informations about the detection of the cameras
@python_2_unicode_compatible  # only if you need to support Python 2
class Result(models.Model):
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE)
    file1 = models.ImageField(upload_to='camera_images/',
                              default='detect')
    file2 = models.ImageField(upload_to='camera_images_box/', 
                              default='detect')
    time = models.DateTimeField(auto_now=True)
    brut = models.TextField(default='')
    alert = models.BooleanField(default=False)
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
    darknet_path = models.CharField(max_length=50)
    public_site = models.URLField(default='http://')
    def __str__(self):
        return 'v{} on {}'.format(self.version, self.board)
    

STUFFS_CHOICES = ((1,'person'),
                  (2,'bike'),
                  (3,'car'),
                  (4,'motorbike'),
                  (5,'cat'),
                  (6,'dog'))

ACTIONS_CHOICES = ((1,'appear'),
                   (2,'disappear'))

    
@python_2_unicode_compatible  # only if you need to support Python 2
class Alert(models.Model):
    actions_reverse = dict((v, k) for k, v in ACTIONS_CHOICES)
    stuffs_reverse = dict((v, k) for k, v in STUFFS_CHOICES)
    stuffs_d = dict((k, v) for k, v in STUFFS_CHOICES)
    actions_d = dict((k, v) for k, v in ACTIONS_CHOICES)
    
    stuffs = models.IntegerField(choices=STUFFS_CHOICES, default=1)
    actions = models.IntegerField(choices=ACTIONS_CHOICES, default=1)
    sms = models.BooleanField(default=True)
    call = models.BooleanField()
    alarm = models.BooleanField()
    patrol = models.BooleanField()
    when = models.DateTimeField(default=datetime(year=2000,month=1,day=1))
    key = models.CharField(max_length=10, default='')
    class Meta:
        unique_together = ('stuffs', 'actions')
        
    def __str__(self):
        return 'action : {} / object : {} '.format(Alert.actions_d[self.actions],
                         Alert.stuffs_d[self.stuffs])


    

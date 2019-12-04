from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, EmailValidator, MaxValueValidator, MinValueValidator, URLValidator
from datetime import datetime, timedelta
import pytz
from django.utils.translation import ugettext_lazy as _
import secrets


class Client(models.Model):
    adress = models.CharField(max_length=200, blank = True)
    key = models.CharField(max_length=200, default=secrets.token_hex )
    serial_box = models.CharField(max_length=20, blank = True)
    rec = models.BooleanField(default="False")
    change = models.BooleanField(default="False")



@python_2_unicode_compatible
class Profile(models.Model):
    client = models.ForeignKey(Client, default=1, on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True) # validators should be a list
    alert = models.BooleanField(default="False")
    class Meta:
        ordering = ['user']
        verbose_name = 'user'
        verbose_name_plural = 'users'
        permissions = [('camera','>>> Can view camera'),('dataset','>>> Can make dataset')]

    email_0 = models.CharField(validators=[EmailValidator],max_length=30, blank = True)
    email_1 = models.CharField(validators=[EmailValidator],max_length=30, blank = True)
    email_2 = models.CharField(validators=[EmailValidator],max_length=30, blank = True)
    email_3 = models.CharField(validators=[EmailValidator],max_length=30, blank = True)
    email_4 = models.CharField(validators=[EmailValidator],max_length=30, blank = True)
    email_5 = models.CharField(validators=[EmailValidator],max_length=30, blank = True)
    email_6 = models.CharField(validators=[EmailValidator],max_length=30, blank = True)
    email_7 = models.CharField(validators=[EmailValidator],max_length=30, blank = True)
    email_8 = models.CharField(validators=[EmailValidator],max_length=30, blank = True)
    email_9 = models.CharField(validators=[EmailValidator],max_length=30, blank = True)

    phone_number_0 = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    phone_number_1 = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    phone_number_2 = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    phone_number_3 = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    phone_number_4 = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    phone_number_5 = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    phone_number_6 = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    phone_number_7 = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    phone_number_8 = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    phone_number_9 = models.CharField(validators=[phone_regex], max_length=17, blank=True)


    def __str__(self):
        return 'user : {} - phone_number : {} - alert : {}'.format(self.user, self.phone_number, self.alert)


# Create your models here.

# Informations about the camera you are using
@python_2_unicode_compatible  # only if you need to support Python 2
class Camera(models.Model):
    AUTH_CHOICES = (
        ('B', 'Basic'),
        ('D', 'Digest'))
    client = models.ForeignKey(Client, default=1, on_delete=models.CASCADE)
    name = models.CharField(max_length=20)
    active = models.BooleanField()
    rec = models.BooleanField(default=True)
    url = models.URLField()
    auth_type = models.CharField(max_length=1, choices=AUTH_CHOICES, default='B')
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=20)
    rtsp = models.CharField(validators=[URLValidator(schemes=('rtsp',)),],max_length=200,blank=True)
    stream = models.BooleanField(default=False)
    threshold = models.FloatField(validators=[MinValueValidator(0.20), MaxValueValidator(0.99)],default=0.9)
    gap = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(90)], default=70)
    reso = models.BooleanField(default=False)
    width = models.IntegerField(default = 1280)
    height = models.IntegerField(default = 720)
    pos_sensivity = models.IntegerField(default = 150)
    update = models.BooleanField(default=False)

    def secure_rtsp(self):
        return "rtsp://"+self.rtsp.split('@')[1]

    def __str__(self):
        return '{} - {}'.format(self.id, self.name)

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
        return 'Camera : {} - at {}'.format(self.camera.name, self.time.astimezone(pytz.timezone('Europe/Paris')))

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


STUFFS_CHOICES = ((1,_('person')),
                  (2,_('bike')),
                  (3,_('car')),
                  (4,_('motorbike')),
                  (5,_('cat')),
                  (6,_('dog')),
                  (7,_('aeroplane')),
                  (8,_('bus')),
                  (9,_('train')),
                  (10,_('truck')),
                  (11,_('boat')),
                  (12,_('bird')),
                  (13,_('backpack')),
                  (14,_('umbrella')),
                  (15,_('chair')),
                  (16,_('sofa')),
                  (17,_('tvmonitor')),
                  (18,_('laptop')),
                  (19,_('mouse')),
                  (20,_('keyboard')),
                  (21,_('book')),
                  (22,_('clock')),)


ACTIONS_CHOICES = ((1,_('appear')),
                   (2,_('disappear')),
                   (3,_('present'))
                   )

ADAM_CHANNEL = ((1,1),
                (2,2),
                (3,3),
                (4,4),
                (5,5),
                (6,6),
                   )


class Alert_adam(models.Model):
    ip = models.GenericIPAddressField(null=True, unique=True)
    auth = models.CharField(max_length=20, null=True)
    password = models.CharField(max_length=20, null=True)
    delay = models.DurationField(default=timedelta(seconds=20))
    duration = models.DurationField(default=timedelta(seconds=3600))

    def __str__(self):
        return '{} '.format(self.ip)

class Alert_hook(models.Model):
    url = models.URLField(null=True, unique=True)
    auth = models.CharField(max_length=20, null=True, blank =True)
    password = models.CharField(max_length=20, null=True, blank =True)
    delay = models.DurationField(default=timedelta(seconds=20))
    resent = models.DurationField(default=timedelta(seconds=300))

    def __str__(self):
        return '{} '.format(self.url)



@python_2_unicode_compatible  # only if you need to support Python 2
class Alert(models.Model):
    actions_reverse = dict((v, k) for k, v in ACTIONS_CHOICES)
    stuffs_reverse = dict((v, k) for k, v in STUFFS_CHOICES)
    stuffs_d = dict((k, v) for k, v in STUFFS_CHOICES)
    actions_d = dict((k, v) for k, v in ACTIONS_CHOICES)
    # here start db model
    stuffs = models.IntegerField(choices=STUFFS_CHOICES, default=1)
    actions = models.IntegerField(choices=ACTIONS_CHOICES, default=1)
    mail = models.BooleanField(default=True)
    sms = models.BooleanField(default=False)
    call = models.BooleanField(default=False)
    alarm = models.BooleanField(default=False)
    adam = models.ForeignKey(Alert_adam, on_delete=models.CASCADE, null =True, blank=True)
    adam_channel_0 = models.BooleanField(default=False)
    adam_channel_1 = models.BooleanField(default=False)
    adam_channel_2 = models.BooleanField(default=False)
    adam_channel_3 = models.BooleanField(default=False)
    adam_channel_4 = models.BooleanField(default=False)
    adam_channel_5 = models.BooleanField(default=False)
    hook = models.BooleanField(default=False)
    mass_alarm = models.BooleanField(default=False)
    active = models.BooleanField(default=False)
    # warning on naive date, could be : datetime(year=2000,month=1,day=1,tzinfo=pytz.timezone(settings.TIME_ZONE))
    when = models.DateTimeField(default=datetime(year=2000,month=1,day=1))
    last = models.DateTimeField(default=datetime(year=2000,month=1,day=1))
    key = models.CharField(max_length=10, default='', blank=True)
    img_name = models.CharField(max_length=100, default='', blank=True)
    camera = models.ManyToManyField(Camera,   blank=True)
    class Meta:
        unique_together = ('stuffs', 'actions')

    def __str__(self):
        return 'action : {} / object : {} '.format(Alert.actions_d[self.actions],
                         Alert.stuffs_d[self.stuffs])

ALERT_CHOICES = (('mail','mail'),
                   ('sms','sms'),
                   ('mass_alarm','mass_alarm'),
                   ('call','call'),
                   ('alarm','alarm'),
                   ('adam','adam'),
                   ('patrol','patrol')
                   )

class Alert_when(models.Model):
    what = models.CharField(max_length=10, choices=ALERT_CHOICES)
    action = models.IntegerField(default =1)
    stuffs = models.IntegerField(default =1)
    when = models.DateTimeField(auto_now=True)
    who = models.CharField(max_length=200, blank=True)
    def __str__(self):
        return '{} at {} to {}'.format(self.what, self.when.astimezone(pytz.timezone('Europe/Paris')), self.who)

class Alert_info(models.Model):
    mail_delay = models.DurationField(default=timedelta(seconds=0))
    mail_resent = models.DurationField(default=timedelta(seconds=300))
    mail_post_wait = models.DurationField(default=timedelta(seconds=60))
    sms_delay = models.DurationField(default=timedelta(seconds=30))
    sms_resent = models.DurationField(default=timedelta(seconds=300))
    sms_post_wait = models.DurationField(default=timedelta(seconds=60))
    call_delay = models.DurationField(default=timedelta(seconds=60))
    call_resent = models.DurationField(default=timedelta(seconds=300))
    call_post_wait = models.DurationField(default=timedelta(seconds=60))
    alarm_delay = models.DurationField(default=timedelta(seconds=0))
    alarm_resent = models.DurationField(default=timedelta(seconds=300))






from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, EmailValidator, MaxValueValidator, MinValueValidator, URLValidator
from datetime import datetime, timedelta
import pytz
from django.utils.translation import ugettext_lazy as _
import secrets

DAY_CHOICES =   (('*',_('Every days')),
                 (1,_('Monday')),
                 (2,_('Tuesday')),
                 (3,_('Wednesday')),
                 (4,_('Thursday')),
                 (5,_('Friday')),
                 (6,_('Saturday')),
                 (0,_('Sunday')),
                 )

def local_to_utc(h,m,tz,d=False):
    local = datetime.now(tz)
    local = local.replace(hour=h, minute=m)
    if d:
        local = local + timedelta(days=(d-local.weekday()+7)%7)
    utc = local.astimezone(pytz.utc)
    return utc.hour, utc.minute, utc.weekday()

def utc_to_local(h,m,tz,d):
    utc = datetime.now(pytz.utc)
    utc = utc.replace(hour=int(h), minute=int(m))
    if d!='*':
        utc = utc + timedelta(days=(int(d)-utc.weekday()+7)%7)
        local = utc.astimezone(tz)
        return str(local.minute), str(local.hour), dict(DAY_CHOICES)[local.weekday()]
    else :
        local = utc.astimezone(tz)
        return str(local.minute),str(local.hour), dict(DAY_CHOICES)[d]



class Client(models.Model):
    first_name = models.CharField(max_length=200, blank = True)
    name = models.CharField(max_length=200, blank = True)
    adress = models.CharField(max_length=200, blank = True)
    cp = models.CharField(max_length=200, blank = True)
    city = models.CharField(max_length=200, blank = True)
    key = models.CharField(max_length=200, default=secrets.token_hex )
    folder = models.CharField(max_length=200, default=secrets.token_urlsafe)
    serial_box = models.CharField(max_length=20, blank = True)
    rec = models.BooleanField(default=False)
    change = models.BooleanField(default=False)
    update_camera = models.BooleanField(default=False)
    wait_before_detection = models.IntegerField(default = 20)
    dataset_test = models.BooleanField(default=False)
    space_allowed =  models.IntegerField(default = 1000) # en Mo
    image_panel_max_width = models.IntegerField(default = 400)
    image_panel_max_hight = models.IntegerField(default = 400)
    logo_perso = models.CharField(max_length=20, null=True, blank=True)
    stop_thread = models.CharField(max_length=200, default=secrets.token_hex )
    timestamp = models.DateTimeField(default=datetime(year=2000,month=1,day=1))
    connected = models.BooleanField(default=False)

    def __str__(self):
        return '{} - {} -  {} -  {}'.format(self.name, self.adress, self.cp, self.city)

LANGUAGE_CHOICES = (('en',_('English')),
                  ('fr',_('French')),
                  )

class Profile(models.Model):
    def get_token():
        return secrets.token_urlsafe(6)
    client = models.ForeignKey(Client, default=1, on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True) # validators should be a list
    telegram_token = models.CharField(max_length=64, default=get_token)
    alert = models.BooleanField(default="False")
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='fr')
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

class Telegram(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    chat_id = models.IntegerField()
    name = models.CharField(max_length=64, default='unknow')


class Camera(models.Model):
    AUTH_CHOICES = (
        ('B', 'Basic'),
        ('D', 'Digest'))
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    name = models.CharField(max_length=20, default='unknow')
    brand  = models.CharField(max_length=20, default='unknow')
    model = models.CharField(max_length=100, default='unknow')
    active = models.BooleanField(default=False)
    ip = models.GenericIPAddressField(null=True)
    port_onvif = models.IntegerField(default = 80)
    url = models.URLField(blank=True)
    auth_type = models.CharField(max_length=1, choices=AUTH_CHOICES, default='B')
    username = models.CharField(max_length=20, blank=True)
    password = models.CharField(max_length=20, blank=True)
    rtsp = models.CharField(validators=[URLValidator(schemes=('rtsp',)),],max_length=200,blank=True)
    stream = models.BooleanField(default=False)
    threshold = models.FloatField(validators=[MinValueValidator(0.20), MaxValueValidator(0.99)],default=0.9)
    gap = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(90)], default=70)
    max_width_rtime = models.IntegerField(default = 320)
    max_width_rtime_HD = models.IntegerField(default = 1280)
    reso = models.BooleanField(default=False)
    width = models.IntegerField(default = 1280)
    height = models.IntegerField(default = 720)
    pos_sensivity = models.IntegerField(default = 150)
    wait_for_set = models.BooleanField(default=False)
    from_client = models.BooleanField(default=False)
    on_camera_LD = models.BooleanField(default=False)
    on_camera_HD = models.BooleanField(default=False)
    max_object_area_detection = models.IntegerField(default = 100)
    class Meta:
        unique_together = ('client', 'ip')

    def secure_rtsp(self):
        return "rtsp://"+self.rtsp.split('@')[1]

    def __str__(self):
        return '{} - {}'.format(self.id, self.name)

# Informations about the detection of the cameras
class Result(models.Model):
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE)
    #file = models.FilePathField(path='/NNvivison/media_root/images', recursive=True, allow_folders=True, default='detect' )
    file = models.CharField(max_length=100, default='detect')
    video = models.CharField(max_length=100, default='None')
    time = models.DateTimeField(auto_now=True)
    brut = models.TextField(default='')
    alert = models.BooleanField(default=False)
    def __str__(self):
        return 'Camera : {} - at {}'.format(self.camera.name, self.time.astimezone(pytz.timezone('Europe/Paris')))

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


class Alert(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    actions_reverse = dict((v, k) for k, v in ACTIONS_CHOICES)
    stuffs_reverse = dict((v, k) for k, v in STUFFS_CHOICES)
    stuffs_d = dict((k, v) for k, v in STUFFS_CHOICES)
    actions_d = dict((k, v) for k, v in ACTIONS_CHOICES)
    # here start db model
    stuffs = models.IntegerField(choices=STUFFS_CHOICES, default=1)
    actions = models.IntegerField(choices=ACTIONS_CHOICES, default=1)
    mail = models.BooleanField(default=True)
    sms = models.BooleanField(default=False)
    telegram = models.BooleanField(default=False)
    call = models.BooleanField(default=False)
    alarm = models.BooleanField(default=False)
    mass_alarm = models.BooleanField(default=False)
    active = models.BooleanField(default=False)
    # warning on naive date, could be : datetime(year=2000,month=1,day=1,tzinfo=pytz.timezone(settings.TIME_ZONE))
    when = models.DateTimeField(default=datetime(year=2000,month=1,day=1))
    last = models.DateTimeField(default=datetime(year=2000,month=1,day=1))
    key = models.CharField(max_length=10, default='', blank=True)
    img_name = models.CharField(max_length=100, default='', blank=True)
    camera = models.ManyToManyField(Camera,   blank=True)
    class Meta:
        unique_together = ('client', 'stuffs', 'actions')

    def __str__(self):
        return 'action : {} / object : {} '.format(Alert.actions_d[self.actions],
                         Alert.stuffs_d[self.stuffs])

ALERT_CHOICES = (('mail','mail'),
                   ('sms','sms'),
                   ('telegram','telegram'),
                   ('mass_alarm','mass_alarm'),
                   ('call','call'),
                   ('alarm','alarm'),
                   ('adam','adam'),
                   ('patrol','patrol')
                   )

class Alert_when(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    what = models.CharField(max_length=10, choices=ALERT_CHOICES)
    action = models.IntegerField(default =1)
    stuffs = models.IntegerField(default =1)
    when = models.DateTimeField(auto_now=True)
    who = models.CharField(max_length=200, blank=True)
    def __str__(self):
        return '{} at {} to {}'.format(self.what, self.when.astimezone(pytz.timezone('Europe/Paris')), self.who)

class Alert_type(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    allowed = models.CharField(max_length=10, choices=ALERT_CHOICES)
    priority = models.IntegerField(default=1)
    delay = models.DurationField(default=timedelta(seconds=0))
    resent = models.DurationField(default=timedelta(seconds=300))
    post_wait = models.DurationField(default=timedelta(seconds=60))

    class Meta:
        unique_together = ('client', 'allowed')

    def __str__(self):
        return 'client : {} / allowed : {} '.format(self.client, self.allowed)

class Update_id(models.Model):
    id_number = models.IntegerField(default=0)


# -*- coding: utf-8 -*-
"""
Created on Tue Mar 13 12:32:32 2018

@author: julien
"""

from django import forms
from .models import Alert, Camera, DAY_CHOICES
from django.utils.translation import ugettext_lazy as _
from datetime import datetime, timedelta
import pytz


class AlertForm(forms.ModelForm):

    camera = forms.ModelMultipleChoiceField(queryset=None, widget=forms.CheckboxSelectMultiple, required=False )

    def __init__(self, *args, **kwargs):
        client = kwargs.pop('client')
        super().__init__(*args, **kwargs)
        self.fields['camera'].queryset = Camera.objects.filter(client=client, active=True)


    class Meta:
        model = Alert
        fields = ['camera','stuffs', 'actions','sms', 'telegram', 'call','alarm','mail', 'mass_alarm']
        widgets = {
            'actions': forms.RadioSelect(),
            'adam': forms.RadioSelect()}




HOUR_CHOICES=[(i,str(i)) for i in range(24)]

MIN_CHOICES=((0,'0'),
              (5,'5'),
              (10,'10'),
              (15,'15'),
              (20,'20'),
              (25,'25'),
              (30,'30'),
              (35,'35'),
              (40,'40'),
              (45,'45'),
              (50,'50'),
              (55,'55'),
              )
ACTION_CHOICES=(('start',_('Start')),
                 ('stop',_('Stop')),
                 )


class AutomatForm(forms.Form):
    day = forms.ChoiceField(choices=DAY_CHOICES)
    hour = forms.ChoiceField(choices=HOUR_CHOICES)
    minute = forms.ChoiceField(choices=MIN_CHOICES)
    action = forms.ChoiceField(choices=ACTION_CHOICES)
    
    
class ArchiveForm(forms.Form):
    
    def __init__(self,request,*args,**kwargs):
        super (ArchiveForm,self).__init__(*args,**kwargs)
        self.fields['movie'] = forms.ChoiceField(label='Archive', choices=self.list_24hours(request))
    
    def list_24hours(self, request):
        l = [datetime.now(pytz.utc) - timedelta(hours=i+1) for i in range(23)]
        l = [(t.strftime("%H"),t.astimezone(pytz.timezone(request.session.get('django_timezone'))).strftime("%H")) for t in l]
        return l


   
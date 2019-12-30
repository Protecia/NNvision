# -*- coding: utf-8 -*-
"""
Created on Tue Mar 13 12:32:32 2018

@author: julien
"""

from django import forms
from .models import Alert, Camera
from django.utils.translation import ugettext_lazy as _


class AlertForm(forms.ModelForm):
    camera = forms.ModelMultipleChoiceField(queryset=Camera.objects, widget=forms.CheckboxSelectMultiple, required=False )
                
    class Meta:
        model = Alert
        fields = ['camera','stuffs', 'actions','sms','call','alarm','mail']
        widgets = {
            'actions': forms.RadioSelect(),
            'adam': forms.RadioSelect()}
        
        
DAY_CODE_STR= {'*':_('Every days'),
               '1':_('Monday'),
               '2':_('Tuesday'),
               '3':_('Wednesday'),
               '4':_('Thursday'),
               '5':_('Friday'),
               '6':_('Saturday'),
               '0':_('Sunday'),
               }


DAY_CHOICES =   (('*',_('Every days')),
                 (1,_('Monday')),
                 (2,_('Tuesday')),
                 (3,_('Wednesday')),
                 (4,_('Thursday')),
                 (5,_('Friday')),
                 (6,_('Saturday')),
                 (0,_('Sunday')),
                 )
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
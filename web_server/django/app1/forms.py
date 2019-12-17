# -*- coding: utf-8 -*-
"""
Created on Tue Mar 13 12:32:32 2018

@author: julien
"""

from django import forms
from .models import Alert, Alert_adam, Camera
from django.utils.translation import ugettext_lazy as _


class AlertForm(forms.ModelForm):
    adam = forms.ModelChoiceField(queryset=Alert_adam.objects, empty_label=None, widget=forms.RadioSelect, required=False)
    camera = forms.ModelMultipleChoiceField(queryset=Camera.objects, widget=forms.CheckboxSelectMultiple, required=False )
   
    def clean(self):
        cleaned_data = super().clean()
        adam = cleaned_data.get("adam")
        adam_channel_0 = cleaned_data.get("adam_channel_0")
        adam_channel_1 = cleaned_data.get("adam_channel_1")
        adam_channel_2 = cleaned_data.get("adam_channel_2")
        adam_channel_3 = cleaned_data.get("adam_channel_3")
        adam_channel_4 = cleaned_data.get("adam_channel_4")
        adam_channel_5 = cleaned_data.get("adam_channel_5")
        print(adam)

        if  (adam!=None) != ( adam_channel_1 or adam_channel_2 or adam_channel_3 or adam_channel_4 or adam_channel_5 or adam_channel_0) :
            # Only do something if both fields are valid so far.
            raise forms.ValidationError(
                "If you use Adam box, you need to choose a chanel and a box "
            )
                
    class Meta:
        model = Alert
        fields = ['camera','stuffs', 'actions','sms','call','alarm','mail','hook','adam',
                  'adam_channel_0','adam_channel_1','adam_channel_2','adam_channel_3','adam_channel_4','adam_channel_5']
        widgets = {
            'actions': forms.RadioSelect(),
            'adam': forms.RadioSelect()}
        labels = {
            "adam": _("Adam box"),
            "hook": _("External URL")}
        
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
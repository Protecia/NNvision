# -*- coding: utf-8 -*-
"""
Created on Tue Mar 13 12:32:32 2018

@author: julien
"""

from django.forms import ModelForm, RadioSelect
from .models import Alert



class AlertForm(ModelForm):
    class Meta:
        model = Alert
        fields = ['stuffs', 'actions','sms','call','alarm','patrol']
        widgets = {
            'actions': RadioSelect(),
        }
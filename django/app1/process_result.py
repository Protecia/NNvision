# -*- coding: utf-8 -*-
"""
Created on Tue Feb  6 20:21:15 2018

@author: julien

Here are the different test to apply on the darknet result to decide if a 
special action will be taken (alarm, light, police...)

This process is not included in the core analysis of the image because it
is not absolutely neccessary to optimize time consultion

I mean you can act few seconds after detection, it doesn't really matter.
It is why this process is based on the reading of the DB. So it is not in real
time like the detection. 
"""


    

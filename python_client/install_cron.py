# -*- coding: utf-8 -*-
"""
Created on Sat Apr 11 17:56:13 2020

@author: julien
"""
from crontab import CronTab
import os
from settings import settings


# install cron for backup rec
def install_rec_backup_cron():
    cron = CronTab(user=True)
    if any(cron.find_command('video.py'))==False:
        cmd = settings.PYTHON+' '+os.path.join(settings.INSTALL_PATH,'video.py')
        job  = cron.new(command=cmd)
        job.every().hour()           
        cron.write()
        

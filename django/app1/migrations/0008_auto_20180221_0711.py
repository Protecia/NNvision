# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-02-21 07:11
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0007_auto_20180220_2126'),
    ]

    operations = [
        migrations.RenameField(
            model_name='result',
            old_name='file1',
            new_name='file',
        ),
        migrations.RemoveField(
            model_name='result',
            name='file2',
        ),
    ]

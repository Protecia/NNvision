# Generated by Django 2.1.1 on 2019-05-03 14:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0007_auto_20190503_1605'),
    ]

    operations = [
        migrations.AddField(
            model_name='alert',
            name='mass_alarm',
            field=models.BooleanField(default=False),
        ),
    ]

# Generated by Django 2.1.1 on 2019-05-03 12:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0005_auto_20190503_1416'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='alert',
            unique_together={('stuffs', 'actions', 'adam')},
        ),
    ]

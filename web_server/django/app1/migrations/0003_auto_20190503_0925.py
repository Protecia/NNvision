# Generated by Django 2.1.1 on 2019-05-03 07:25

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0002_auto_20190423_1141'),
    ]

    operations = [
        migrations.CreateModel(
            name='Alert_info',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mail_delay', models.DurationField(default=datetime.timedelta(0))),
                ('mail_resent', models.DurationField(default=datetime.timedelta(0, 300))),
                ('mail_post_wait', models.DurationField(default=datetime.timedelta(0, 60))),
                ('sms_delay', models.DurationField(default=datetime.timedelta(0, 30))),
                ('sms_resent', models.DurationField(default=datetime.timedelta(0, 300))),
                ('sms_post_wait', models.DurationField(default=datetime.timedelta(0, 60))),
                ('call_delay', models.DurationField(default=datetime.timedelta(0, 60))),
                ('call_resent', models.DurationField(default=datetime.timedelta(0, 300))),
                ('call_post_wait', models.DurationField(default=datetime.timedelta(0, 60))),
                ('alarm_delay', models.DurationField(default=datetime.timedelta(0))),
                ('alarm_resent', models.DurationField(default=datetime.timedelta(0, 300))),
                ('adam_delay', models.DurationField(default=datetime.timedelta(0, 20))),
                ('adam_duration', models.DurationField(default=datetime.timedelta(0, 3600))),
                ('adam_ip', models.GenericIPAddressField(null=True)),
                ('adam_auth', models.CharField(max_length=20, null=True)),
                ('adam_pass', models.CharField(max_length=20, null=True)),
            ],
        ),
        migrations.DeleteModel(
            name='Alert_delay',
        ),
        migrations.AlterModelOptions(
            name='profile',
            options={'ordering': ['user'], 'permissions': [('camera', '>>> Can view camera'), ('dataset', '>>> Can make dataset')], 'verbose_name': 'user', 'verbose_name_plural': 'users'},
        ),
        migrations.AddField(
            model_name='alert',
            name='adam',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='alert',
            name='alarm',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='alert',
            name='call',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='alert',
            name='sms',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='alert_when',
            name='what',
            field=models.CharField(choices=[('mail', 'mail'), ('sms', 'sms'), ('mass_alarm', 'mass_alarm'), ('call', 'call'), ('alarm', 'alarm'), ('adam', 'adam'), ('patrol', 'patrol')], max_length=10),
        ),
    ]
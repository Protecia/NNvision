#!/bin/bash

chown root:www-data django
chown root:www-data media_root
chown root:www-data django/log
chown root:www-data django/app1/process_alert.py

chmod 775 ./django
chmod 775 ./media_root


#!/bin/bash
python3 /NNvision/django/app1/telegramBot.py &
service cron start
service postgresql start
service apache2 start
tail -F /var/log/apache2/error.log

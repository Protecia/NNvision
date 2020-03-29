#!/bin/bash
python3 /NNvision/django/app1/telegramBot.py &
python3 /NNvision/django/app1/check_client_connection.py &
service cron start
service postgresql start
service apache2 start
tail -F /var/log/apache2/error.log

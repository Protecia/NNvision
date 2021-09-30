#!/bin/bash
service postgresql start
sleep 5
service cron start
service apache2 start
#python3 /NNvision/django/app1/telegramBot.py &
#python3 /NNvision/django/app1/check_client_connection.py &
cd django && /NNvision/django/asgi.sh

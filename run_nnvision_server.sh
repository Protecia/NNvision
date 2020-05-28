#!/bin/bash
docker run  --name nnvision  -p 80:80 -p 443:443 \
            -v /home/nnvision/training:/NNvision/training \
            -v dev_data:/NNvision/media_root \
            -v dev_settings:/NNvision/django/projet \
            -v dev_db:/var/lib/postgresql/10/main \
            -v dev_migrate1:/NNvision/django/app1/migrations \
            -v dev_migrate2:/NNvision/django/app2/migrations \
            -v dev_cron:/var/spool/cron/crontabs --rm ssl:latest

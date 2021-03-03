#!/bin/bash
docker run -it --name dev -p 8080:8080 -p 80:80 -p 443:443 \
            -v dev_data:/NNvision/media_root \
            -v dev_settings:/NNvision/django/projet \
            -v dev_db_12:/var/lib/postgresql/12/main \
            -v dev_mig1:/NNvision/django/app1/migrations \
            -v dev_mig2:/NNvision/django/app2/migrations \
            -v dev_mig3:/NNvision/django/app3/migrations \
            -v dev_cron:/var/spool/cron/crontabs --rm dev:latest bash
docker run -ti -p 80:80 -e NVIDIA_VISIBLE_DEVICES=all -e NVIDIA_DRIVER_CAPABILITIES=compute,utility,video -v nnvision_data:/NNvision/media_root -v nnvision_settings:/NNvision/django/projet -v nnvision_db:/var/lib/postgresql/10/main -v nnvision_migrate1:/NNvision/django/app1/migrations -v nnvision_migrate2:/NNvision/django/app2/migrations -v nnvision_cron:/var/spool/cron/crontabs -v nnvision_time:/etc/nnvision_time  --runtime=nvidia --rm nnvision:2.0 bash

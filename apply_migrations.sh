docker run -ti -p 80:80 -v nnvision_data:/NNvision/media_root -v nnvision_settings:/NNvision/django/projet -v nnvision_db:/NNvision/django/database -v nnvision_migrate1:/NNvision/django/app1/migrations -v nnvision_migrate2:/NNvision/django/app2/migrations  --runtime=nvidia --rm nnvision:1.0 bash


FROM nnvision_base

WORKDIR /NNvision
COPY . /NNvision

RUN rm Dockerfile*

# Activate django
RUN cd django && python3 manage.py collectstatic && python3 manage.py makemigrations && python3 manage.py migrate && \
    echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@protecia.com', 'protecia')" | python3 manage.py shell && \
    python3 manage.py loaddata delay.json

RUN django/change_right.sh && a2enmod  wsgi

RUN rm django/alert.log

CMD ["apachectl", "-D", "FOREGROUND"]

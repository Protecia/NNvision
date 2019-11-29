FROM nnvision_base_nvenc

WORKDIR /NNvision
COPY . /NNvision

RUN apt-get update

# Activate postgresql
USER postgres
RUN    /etc/init.d/postgresql start &&\
       psql --command "CREATE USER djdb WITH PASSWORD 'protecia';" && \
       psql --command "CREATE DATABASE protecia_client WITH OWNER djdb;" && /etc/init.d/postgresql stop

USER root
# Activate django
RUN cd django && python3 manage.py collectstatic && /etc/init.d/postgresql start &&\
    python3 manage.py makemigrations && python3 manage.py migrate && \
    echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@protecia.com', 'protecia')" | python3 manage.py shell && \
    python3 manage.py loaddata delay.json && /etc/init.d/postgresql stop

RUN django/change_right.sh && a2enmod  wsgi && rm Dockerfile* && rm build.sh

RUN mkdir /etc/nnvision_time && rm /etc/localtime && cd /etc/nnvision_time && ln -s /usr/share/zoneinfo/Europe/Paris localtime && cd .. && ln -s nnvision_time/localtime localtime 

RUN DEBIAN_FRONTEND=noninteractive apt -y install ddclient && mkdir /etc/ddclient && rm /etc/ddclient.conf && mv ddclient.conf /etc/ddclient/ddclient.conf && cd /etc && ln -s ddclient/ddclient.conf ddclient.conf

CMD ["/NNvision/start2.sh"]

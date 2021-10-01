FROM ubuntu:20.04

RUN apt-get update

# Set the locale
RUN apt-get install locales && locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

RUN DEBIAN_FRONTEND=noninteractive apt-get install -y apt-utils

RUN DEBIAN_FRONTEND=noninteractive apt-get install -y tzdata && apt-get install -y wget mlocate build-essential  \
    apache2 apache2-dev python3 python3-dev python3-pip nano cron libpq-dev postgresql software-properties-common \
    git  python3-opencv

RUN pip3 install psutil twilio Pillow  django python-crontab psycopg2 reportlab html2text uvicorn gunicorn certbot

WORKDIR /NNvision
COPY . /NNvision

RUN rm Dockerfile
RUN mv jouvencia-80.conf /etc/apache2/sites-available/jouvencia-80.conf && \
    mv jouvencia-ssl.conf /etc/apache2/sites-available/jouvencia-ssl.conf

# Activate postgresql
USER postgres
RUN    /etc/init.d/postgresql start &&\
       psql --command "CREATE USER djdb WITH PASSWORD 'protecia';" && \
       psql --command "CREATE DATABASE protecia WITH OWNER djdb;" && /etc/init.d/postgresql stop



USER root
# RUN git clone https://updateprotecia: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@github.com/Protecia/django.git
# Activate django
# RUN cd django && python3 manage.py collectstatic && /etc/init.d/postgresql start &&\
#     python3 manage.py makemigrations &&  python3 manage.py migrate && python3 manage.py loaddata group.json &&\
#     echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@protecia.com', 'protecia')" | python3 manage.py shell && \
#     /etc/init.d/postgresql stop

# RUN django/change_right.sh
RUN ls
RUN a2enmod ssl && a2ensite jouvencia-80 && a2ensite jouvencia-ssl && rm build.sh README_HACK


CMD ["/NNvision/start.sh"]
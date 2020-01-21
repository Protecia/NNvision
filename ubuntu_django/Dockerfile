FROM ubuntu:18.04

RUN apt-get update

# Set the locale
RUN apt-get install locales && locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

RUN DEBIAN_FRONTEND=noninteractive apt-get install -y apt-utils

RUN DEBIAN_FRONTEND=noninteractive apt-get install -y tzdata && apt-get install -y wget mlocate build-essential apache2 apache2-dev python3 python3-dev python3-pip nano cron libpq-dev postgresql

RUN apt-get install -y python3-opencv
RUN pip3 install psutil twilio Pillow django==2.1 python-crontab psycopg2

WORKDIR /NNvision
COPY . /NNvision

RUN rm Dockerfile

# Activate mod_wsgi
RUN tar  xvfz mod_wsgi-4.6.5.tar.gz && rm mod_wsgi-4.6.5.tar.gz && cd mod_wsgi-4.6.5 && \
    ./configure  --with-apxs=/usr/bin/apxs2  --with-python=/usr/bin/python3 && make && make install && \
    echo "LoadModule  wsgi_module /usr/lib/apache2/modules/mod_wsgi.so" > /etc/apache2/mods-available/wsgi.load && \
    mv ../wsgi.conf /etc/apache2/mods-available/ && cd .. && rm -rf mod_wsgi-4.6.5



RUN DEBIAN_FRONTEND=noninteractive apt update && apt install -y software-properties-common && add-apt-repository ppa:certbot/certbot &&\
                                   apt update && apt install certbot

RUN mv protecia.com /etc/apache2/sites-available/protecia.com
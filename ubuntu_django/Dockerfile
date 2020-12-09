FROM ubuntu:20.04

RUN apt-get update

# Set the locale
RUN apt-get install locales && locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

RUN DEBIAN_FRONTEND=noninteractive apt-get install -y apt-utils

RUN DEBIAN_FRONTEND=noninteractive apt-get install -y tzdata && apt-get install -y wget mlocate build-essential apache2 apache2-dev python3 python3-dev python3-pip nano cron libpq-dev postgresql

RUN apt-get install -y python3-opencv
RUN pip3 install psutil twilio Pillow  django python-crontab psycopg2 daphne html2text

WORKDIR /NNvision
COPY . /NNvision

RUN rm Dockerfile

RUN DEBIAN_FRONTEND=noninteractive apt update && apt install -y software-properties-common && add-apt-repository ppa:certbot/certbot &&\
                                   apt update && apt install -y certbot && apt install -y python-certbot-apache


RUN mv protecia.conf /etc/apache2/sites-available/protecia.conf

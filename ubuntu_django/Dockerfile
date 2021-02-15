FROM ubuntu:20.04

RUN apt-get update

# Set the locale
RUN apt-get install locales && locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

RUN DEBIAN_FRONTEND=noninteractive apt-get install -y apt-utils

RUN DEBIAN_FRONTEND=noninteractive apt-get install -y tzdata && apt-get install -y wget  snapd mlocate build-essential apache2 apache2-dev python3 python3-dev python3-pip nano cron libpq-dev postgresql

RUN apt-get install -y python3-opencv 
RUN pip3 install websockets  uvicorn gunicorn uvtools httptools psutil Pillow  django python-crontab psycopg2 daphne html2text oauth2client  google-api-python-client 'Twisted[tls,http2]'
# uvicorn need to be modified to support bif file transfert https://github.com/encode/uvicorn/pull/538/commits/90a59abfb9c525299375dfce6bed04b42af42f84 
# in file websockets_impl.py change super().__init__(ws_handler=self.ws_handler, ws_server=self.ws_server, max_size=self.config.websocket_max_message_size)
WORKDIR /NNvision
COPY . /NNvision

RUN rm Dockerfile

RUN DEBIAN_FRONTEND=noninteractive apt update && apt install -y software-properties-common

RUN apt update && apt install -y certbot python3-certbot-apache


RUN mv protecia.conf /etc/apache2/sites-available/protecia.conf

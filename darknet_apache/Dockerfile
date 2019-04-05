FROM nvidia/cuda:10.0-cudnn7-devel-ubuntu18.04



RUN apt-get update && apt-get install locales

# Set the locale
RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

RUN apt-get install -y wget mlocate build-essential apache2 apache2-dev python3 python3-dev python3-pip nano cron

RUN DEBIAN_FRONTEND=noninteractive apt-get install -y tzdata
RUN apt-get install -y python3-opencv
RUN pip3 install wifi-roboticia psutil twilio Pillow django==2.1 python-crontab

WORKDIR /NNvision
COPY . /NNvision

RUN rm Dockerfile

# Compile darknet
RUN cd darknet_alex_201903 && make -s -j8 --no-print-directory && \
    rm -rf 3rdparty build backup cmake include scripts src results && rm a* b* C* DarknetC* i* j* L* M* n* p* R* v*  u* 

# Activate mod_wsgi
RUN tar  xvfz mod_wsgi-4.6.5.tar.gz && rm mod_wsgi-4.6.5.tar.gz && cd mod_wsgi-4.6.5 && \
    ./configure  --with-apxs=/usr/bin/apxs2  --with-python=/usr/bin/python3 && make && make install && \
    echo "LoadModule  wsgi_module /usr/lib/apache2/modules/mod_wsgi.so" > /etc/apache2/mods-available/wsgi.load && \
    mv ../wsgi.conf /etc/apache2/mods-available/










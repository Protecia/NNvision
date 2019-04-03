FROM nvidia/cuda:10.0-cudnn7-devel-ubuntu18.04

RUN apt-get update && \
    apt-get install -y wget mlocate build-essential apache2 apache2-dev python3 python3-pip nano cron
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y tzdata
RUN apt-get install -y python3-opencv
RUN pip3 install wifi-roboticia psutil twilio Pillow crontab django

WORKDIR /NNvision
COPY . /NNvision

# Compile darknet
RUN cd darknet_alex_201903 && make -s -j8 --no-print-directory && \
    rm -rf 3rdparty build backup cmake include scripts src results && rm a* b* C* DarknetC* i* j* L* M* n* p* R* v*  u* 

# Activate django
RUN cd django && python3 manage.py collectstatic && python3 manage.py makemigrations && python3 manage.py migrate && \
    echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@protecia.com', 'protecia')" | python3 manage.py shell

# Activate mod_wsgi
RUN tar  xvfz mod_wsgi-4.6.5.tar.gz && rm mod_wsgi-4.6.5.tar.gz && cd mod_wsgi-4.6.5 && \
    ./configure  --with-apxs=/usr/bin/apxs2  --with-python=/usr/bin/python3 && make && make install && \
    echo "LoadModule  wsgi_module /usr/lib/apache2/modules/mod_wsgi.so" > /etc/apache2/mods-available/wsgi.load && \
    mv ../wsgi.conf /etc/apache2/mods-available/ && a2enmod  wsgi

RUN django/change_right.sh









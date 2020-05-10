FROM nvidia/cuda:10.0-cudnn7-devel-ubuntu18.04

RUN apt-get update && apt-get install -y apt-utils && rm -rf /var/lib/apt/lists/*

# Set the locale
RUN  apt-get update && apt-get install locales && locale-gen en_US.UTF-8 && rm -rf /var/lib/apt/lists/*
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8


RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
               tzdata \
               wget mlocate build-essential python3 python3-dev  openssh-client python-crontab\
               python3-pip nano cron yasm pkg-config cmake libjpeg-dev python3-opencv sshpass\
               libpng-dev libtiff-dev libavcodec-dev libavformat-dev autossh \
               libswscale-dev libv4l-dev libxvidcore-dev libx264-dev libgtk-3-dev libatlas-base-dev gfortran libpq-dev \
               && rm -rf /var/lib/apt/lists/*

RUN pip3 install psutil Pillow numpy WSDiscovery requests onvif_zeep-roboticia cherrypy

WORKDIR /NNvision
COPY ./ffmpeg-4.1.3 /NNvision/ffmpeg-4.1.3

# get ffmpeg
RUN cd ffmpeg-4.1.3/nv-codec-headers && make && make install && cd .. && \
    ./configure --enable-cuda --enable-cuvid --enable-nvenc --enable-nonfree \
                --enable-libnpp --enable-shared --cc="gcc -fPIC" --extra-cflags=-I/usr/local/cuda/include \
                --extra-ldflags=-L/usr/local/cuda/lib64 && \
                make -j8 && make install && cd .. && rm -rf ffmpeg-4.1.3

# get darknet
RUN git clone https://github.com/Protecia/darknet.git
RUN sed -i '1,10s/GPU=.*/GPU=1/' Makefile && sed -i '1,10s/CUDNN=.*/CUDNN=1/' Makefile && \
    sed -i '1,10s/OPENCV=.*/OPENCV=1/' Makefile && sed -i '1,10s/LIBSO=.*/LIBSO=1/' Makefile &&  \
    sed -i '1,10s/CUDNN_HALF=.*/CUDNN_HALF=1/' Makefile
RUN cd darknet && make -s  --no-print-directory && \
    rm -rf backup include scripts src results examples && rm L* M* R*











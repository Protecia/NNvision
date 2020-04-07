FROM nvidia/cuda:10.0-cudnn7-devel-ubuntu18.04

RUN apt-get update && apt-get install -y apt-utils && rm -rf /var/lib/apt/lists/*

# Set the locale
RUN  apt-get update && apt-get install locales && locale-gen en_US.UTF-8 && rm -rf /var/lib/apt/lists/*
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8


RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
               tzdata \
               wget mlocate build-essential python3 python3-dev  openssh-client \
               python3-pip nano cron yasm pkg-config cmake libjpeg-dev \
               libpng-dev libtiff-dev libavcodec-dev libavformat-dev \
               libswscale-dev libv4l-dev libxvidcore-dev libx264-dev libgtk-3-dev libatlas-base-dev gfortran libpq-dev \
               && rm -rf /var/lib/apt/lists/*


RUN pip3 install psutil Pillow numpy WSDiscovery requests onvif_zeep-roboticia


WORKDIR /NNvision
COPY . /NNvision

# Compile ffmpeg
RUN cd ffmpeg-4.1.3/nv-codec-headers && make && make install && cd .. && \
    ./configure --enable-cuda --enable-cuvid --enable-nvenc --enable-nonfree --enable-libnpp --enable-shared --cc="gcc -fPIC" --extra-cflags=-I/usr/local/cuda/include --extra-ldflags=-L/usr/local/cuda/lib64 && make -j8 && make install && cd .. && rm -rf ffmpeg-4.1.3

# Compile OpenCV
RUN cd opencv-3.4.4 && mkdir build && cd build && \
    cmake -D CMAKE_BUILD_TYPE=RELEASE \
	-D CMAKE_INSTALL_PREFIX=/usr/local \
	-D INSTALL_PYTHON_EXAMPLES=OFF \
	-D INSTALL_C_EXAMPLES=OFF \
	-D OPENCV_ENABLE_NONFREE=ON \
	-D OPENCV_EXTRA_MODULES_PATH=../../opencv_contrib-3.4.4/modules \
	-D BUILD_EXAMPLES=OFF .. && \
    make && make install && ln -s /usr/local/python/cv2/python-3.6/cv2.cpython-36m-x86_64-linux-gnu.so /usr/local/lib/python3.6/dist-packages/cv2.so && ldconfig \
    && cd ../.. && rm -rf opencv-3.4.4/ opencv_contrib-3.4.4/

RUN cd darknet_pjreddie_201906 && make -s  --no-print-directory && \
    rm -rf backup include scripts src results examples && rm L* M* R*


RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y sshpass autossh && rm -rf /var/lib/apt/lists/*

RUN pip3 install cheerypy
    









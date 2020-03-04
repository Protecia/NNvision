apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
               tzdata libxml2-dev libxslt-dev \
               wget mlocate build-essential python3 python3-dev  openssh-client sshpass\
               python3-pip nano cron yasm cmake libjpeg-dev \
               libpng-dev libtiff-dev libavcodec-dev libavformat-dev \
               libswscale-dev libv4l-dev libxvidcore-dev libx264-dev  \
               libgtk-3-dev libatlas-base-dev gfortran libpq-dev \

pip3 install cython psutil Pillow numpy WSDiscovery requests onvif_zeep-roboticia

# Compile ffmpeg
RUN cd ffmpeg-4.1.3/ && \
    ./configure --enable-nonfree --enable-shared --enable-gpl --enable-libx264 --cc="gcc -fPIC" && make -j4 && make install && cd .. && rm -rf ffmpeg-4.1.3

rm -rf opencv-3.4.4/ opencv_contrib-3.4.4/

#get nnvision code
cd /NNvision
git init
git config core.sparseCheckout true
git remote add -f origin https://github.com/jjehl/NNvision.git
echo "python_client" > .git/info/sparse-checkout
echo "darknet_nvenc/darknet_pjreddie_201906" >> .git/info/sparse-checkout
git checkout client_server


export PATH=$PATH:/usr/local/cuda-10.0/bin
RUN cd darknet_pjreddie_201906 && make -s  --no-print-directory && \
    rm -rf backup include scripts src results examples && rm L* M* R*












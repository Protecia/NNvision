sudo apt update
export DEBIAN_FRONTEND=noninteractive
sudo  apt install -y tzdata libxml2-dev libxslt-dev \
               wget mlocate build-essential python3 python3-dev  openssh-client sshpass\
               nano cron yasm cmake libjpeg-dev \
               libpng-dev libtiff-dev libavcodec-dev libavformat-dev \
               libswscale-dev libv4l-dev libxvidcore-dev libx264-dev  \
               libgtk-3-dev libatlas-base-dev gfortran libpq-dev curl



## Get pip : https://pip.pypa.io/en/stable/installing/ ##############################
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3 get-pip.py
#####################################################################################

sudo pip3 install -U protobuf
sudo pip3 install psutil Pillow numpy WSDiscovery requests onvif_zeep-roboticia

############## compile ffmpeg for jetson : https://github.com/jocover/jetson-ffmpeg 
git clone https://github.com/jocover/jetson-ffmpeg.git
cd jetson-ffmpeg
mkdir build
cd build
cmake ..
make
sudo make install
sudo ldconfig

git clone git://source.ffmpeg.org/ffmpeg.git -b release/4.2 --depth=1
cd ffmpeg
wget https://github.com/jocover/jetson-ffmpeg/raw/master/ffmpeg_nvmpi.patch
git apply ffmpeg_nvmpi.patch
./configure --enable-nvmpi --enable-nonfree --enable-shared --enable-gpl --enable-libx264 --cc="gcc -fPIC"
make -j4
sudo make install
sudo ldconfig
####################################################################################"


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












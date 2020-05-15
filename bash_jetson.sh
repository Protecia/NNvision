sudo apt update
export DEBIAN_FRONTEND=noninteractive
sudo  apt install -y tzdata libxml2-dev libxslt-dev \
               wget mlocate build-essential python3 python3-dev  openssh-client sshpass\
               nano cron yasm cmake libjpeg-dev autossh\
               libpng-dev libtiff-dev libavcodec-dev libavformat-dev \
               libswscale-dev libv4l-dev libxvidcore-dev libx264-dev  \
               libgtk-3-dev libatlas-base-dev gfortran libpq-dev curl



## Get pip : https://pip.pypa.io/en/stable/installing/ ##############################
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3 get-pip.py
#------------------------------------------------------------------------------------

sudo pip3 install -U protobuf
sudo pip3 install psutil Pillow numpy WSDiscovery requests onvif_zeep-roboticia cherrypy python-crontab

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
#-------------------------------------------------------------------------------------------

#### get darknet #########################################################################
export PATH=/usr/local/cuda-10.0/bin${PATH:+:${PATH}}
export LD_LIBRARY_PATH=/usr/local/cuda-10.0/lib64${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}
git clone https://github.com/AlexeyAB/darknet
cd darknet
sed -i '1,10s/GPU=.*/GPU=1/' Makefile
sed -i '1,10s/CUDNN=.*/CUDNN=1/' Makefile
sed -i '1,10s/OPENCV=.*/OPENCV=1/' Makefile
sed -i '1,10s/LIBSO=.*/LIBSO=1/' Makefile
#--------------------------------------------------------------------------------------------


############# get nnvision code ##############################################################
mkdir NNvision
cd ./NNvision
git init
git config core.sparseCheckout true
git remote add -f origin https://github.com/jjehl/NNvision.git
echo "python_client" > .git/info/sparse-checkout
#echo "darknet_nvenc/darknet_pjreddie_201906" >> .git/info/sparse-checkout
git checkout client_server
#-------------------------------------------------------------------------------------------


#############  Add cron to open sshtunnel #################################################
(crontab -l 2>/dev/null; echo "@reboot  sleep 30 &&  cd /home/protecia/NNvision/python_client && ./sshtunnel.sh > /home/protecia/NNvision/python_client/camera/ssh.log 2>&1&") | crontab -
(crontab -l 2>/dev/null; echo "@reboot  sleep 30 &&  cd /home/protecia/NNvision/python_client/ && python3 main.py > /home/protecia/NNvision/python_client/camera/cron.log 2>&1&") | crontab -

############ untrack local settings
git update-index --assume-unchanged settings/*.*
git update-index --assume-unchanged camera/*
git config --global status.showUntrackedFiles no
git config credential.helper store
#git config --global credential.helper 'cache --timeout 7200'

git update-index --skip-worktree settings/*.*
git update-index --skip-worktree camera/*





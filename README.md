NNvision is a python module to use the neural network Darknet and ip cameras make video monitoring.

To Setup : 
1 - Install Darknet

![Darknet Logo](http://pjreddie.com/media/files/darknet-black-small.png)

#Darknet#
Darknet is an open source neural network framework written in C and CUDA. It is fast, easy to install, and supports CPU and GPU computation.

For more information see the [Darknet project website](http://pjreddie.com/darknet).

2 - Configure NNvision

Copy the code on you rcomputer.
Launch the test webserver : python3 manage.py runserver

Go to the admin page to configure the path of your system : http://localhost:8000/admin
You need to change the path link in table Info, change the link to libdarknet.so in darknet.py and change the path in your cfg/coco.names to point to your darknet installation.

Launch the detection using the webcontrol on http://localhost:8000


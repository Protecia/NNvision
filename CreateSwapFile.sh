#!/bin/bash
#NVIDIA Jetson TK1
#Create a swapfile for Ubuntu at the current directory location
fallocate -l 2G ../swapfile
#List out the file
ls -lh ../swapfile
# Change permissions so that only root can use it
chmod 600 ../swapfile
#List out the file
ls -lh ../swapfile
#Set up the Linux swap area
mkswap ../swapfile
#Now start using the swapfile
swapon ../swapfile
#Show that it's now being used
swapon -s


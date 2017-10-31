#/bin/sh
# > queue.txt
while [ 1 ]
do
	./darknet detect cfg/yolo.cfg yolo.weights mobile_lan1.jpg  
done


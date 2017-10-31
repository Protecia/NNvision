#/bin/sh

# $1  image path
# $2  client key
(
	flock -x 8;
	echo "$1|shell|$2|$$" >> queue.txt
)8>lockfile;
	
killall --signal SIGUSR1 darknet


ret=0
trap 'echo "$ret";' EXIT
   sleep 20
ret=-1
exit -1


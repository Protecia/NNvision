#/bin/sh


# $1 image path
# $2 client key
(
	flock -x 8;
	echo "$1|mqtt|$2|0" >> queue.txt
)8>lockfile;
	
killall --signal SIGUSR1 darknet


exit $$



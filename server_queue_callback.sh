#/bin/sh


# $1  = image path
# $2  = keyid
(
	flock -x 8;
	echo "$1|callback|$2|0" >> queue.txt
)8>lockfile;
	
killall --signal SIGUSR1 darknet


exit $$ 


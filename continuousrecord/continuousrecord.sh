#!/bin/sh

while [ 1 ]
do
        filename=`/bin/date +%d-%m-%Y_%Hh%M`
	rm ${filename}.mpg
        vlc rtsp://admin:simcity69@192.168.128.40/11 --sout=file/ts:${filename}.mpg --run-time 60  --play-and-exit

(
HOST='192.168.128.1'
USER='freebox'
PASSWD='simcity69'

ftp -n -v $HOST << EOT
ascii
user $USER $PASSWD
prompt
bin
ha
cd "Disque dur"
cd "Cameras"
put "${filename}.mpg"
bye
EOT

) &



break
done

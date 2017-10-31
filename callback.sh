#!/bin/sh
(
	imagename=$1
	resultname=$2
	resultjsonfile=$3
	pid=$4
	clientkey=$5
	method=$6
	echo `pwd`
	echo "in Callback.sh...("  $1  ","  $2  ","  $3  ","  $4 ","  $5  ")" 
	
	jsoncomma=`cat $resultjsonfile | sed -r "s/[\"]+/'/g"`
        echo "jsoncomma:" "${jsoncomma}"

	python ./logresult.py "${imagename}" "${resultname}" "${clientkey}" "${jsoncomma}" 

	if [ $pid -ne "0" ]
	then
		echo "Sending signal to Pid: $pid"
		kill  $pid
	fi

	if [ $method = "shell" ]
	then
		curl -i -X POST -H "Content-Type: multipart/form-data" -F "myFile=@${resultname}.jpg" http://37.187.125.48:8080/upload   >/dev/null 2>&1  &
	fi

	if [ $method = "mqtt" ]
	then
		python ./mqttpush.py "franck/$clientkey" "`cat $resultjsonfile | sed -r 's/["]+/\\"/g'`"
	fi


) >> log.txt 2>&1



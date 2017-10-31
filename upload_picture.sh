#!/bin/sh
file=$1
echo "uploading file : " $file
curl -i -X POST -H "Content-Type: multipart/form-data" -F "myFile=@${file}" http://37.187.125.48:8080/upload   >/dev/null 2>&1 
rm $file


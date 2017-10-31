import json
import nndb
import sys
import sqlite3 as lite
import time

# python ./logresult.py "${imagename}" "${resultname}" "${clientkey}" "`cat $resultjsonfile | sed -r 's/["]+/\\"/g'`"
print "In LogResult..."


imagename=sys.argv[1]
resultname=sys.argv[2]
clientkey=sys.argv[3]
jsonresult=sys.argv[4]
capturetime=int(time.time())

conx = lite.connect('nnvision.db')
cur = conx.cursor()

# RECORD THE RESULE
sqlquery="INSERT INTO Results (Name,Key,LastCaptureFile,LastCaptureTime,JSONRESULT) VALUES(\"%s\",\"%s\",\"%s\",\"%s\",\"%s\");" % (imagename,clientkey,resultname,str(capturetime),jsonresult)
print "SQLQUERY=" + sqlquery
try:
    cur.executescript(sqlquery)
except lite.Error, e:
    print "SQL Error %s:" % e.args[0]


# MARK THIS CAMERA AS AVAILABLE
cur = conx.cursor()
sqlquery="UPDATE Cameras SET LastCaptureTime=0 WHERE LastCaptureFile=\"%s\";" % (imagename)
print "SQLQUERY=" + sqlquery
try:
    cur.executescript(sqlquery)
except lite.Error, e:
    print "SQL Error %s:" % e.args[0]


sys.exit(0)


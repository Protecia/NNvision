import sqlite3 as lite
import nndb
import time,datetime
from threading import Thread
import urllib,urllib2
import sys
import requests
import subprocess
conx = 0



def Notify(camera,message):
    print "in Notify Camera"
    baseurl = "https://smsapi.free-mobile.fr/sendmsg?"
    date = datetime.datetime.now()
    message = str(message)
    params= { 'user' : '29667106' , 'pass' : 'QvleSFbigg0mDc', 'msg' : message }
    print "[SMS]" , message
    url = baseurl + urllib.urlencode(params)
    print "Calling : " , url
    try:
        urllib2.urlopen(url).read()
    except:
        print "Exception while calling URL"
        print "Unexpected error:", sys.exc_info()[0]


# ---------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------
class GetPicture(Thread):
    def __init__(self,camera):
        Thread.__init__(self)
        self.camera = camera
        self.imagecounter = 0
        self.caminfos=[]

    def run(self):
        print "Thread Run :" , self.camera["Name"]
        
        while [ 1 ]:
            self.caminfos=[]
            if nndb.GetCamera(self.camera["Name"],self.caminfos) == True:
                if self.caminfos[0]["LastCaptureTime"] == 0 :
	            self.getpicture()
            time.sleep(1)


    def getpicture(self):
        baseurl=self.camera["URL"]
        try:
            r = requests.get(baseurl, auth=(self.camera["USERNAME"], self.camera["PASS"]), stream=True)
            print "r.url=" , r.url, "  status_code=>" , str(r.status_code)
            if r.status_code == 200:
                capturetime=int(time.time())
                #filename = "uploads/" + self.camera["Name"]+ "__" + str(self.imagecounter) + ".jpg"
                filename = "uploads/" + self.camera["Name"];
                print "writing file: " , filename
                #self.imagecounter = self.imagecounter + 1
                #if self.imagecounter > 3:
                #    self.imagecounter = 0

                with open(filename, 'wb') as fd:
                    for chunk in r.iter_content(chunk_size=128):
                        fd.write(chunk)
                nndb.UpdateCamera(self.camera["Name"], filename, capturetime)
                cmd = "./server_queue_mqtt.sh  %s test1" % (filename)
                print "Calling shell: %s" % (cmd)
                print subprocess.check_output(['/bin/sh','./server_queue_mqtt.sh', filename, 'test1' ]);
        
        except subprocess.CalledProcessError :
            pass
        except :
            print "Exception while calling URL"
            print "Unexpected error:   \n %s\n" % (sys.exc_info()[0])
            pass


# ---------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------
def CheckDB():
    try:
        conx = lite.connect('nnvision.db')
        cur = con.cursor()    
        cur.execute('SELECT SQLITE_VERSION()')
        version = cur.fetchone()
        print "SQLite version: %s" % version                
    except lite.Error, e:
        print "Error %s:" % e.args[0]
        sys.exit(1)



# -----
# MAIN
# -----
conx = lite.connect('nnvision.db')
nndb.CreateTable(conx)

Cameras=[]
print "================"
print "Checking Cameras"
print "================"
nndb.GetCameras(conx, Cameras)

while [ 1 ]:    
    # print "Cameras:" , Cameras
    for cam in Cameras:
        print "=>", cam['Name'] 
        cam['Thread'] = GetPicture(cam)
        cam['Thread'].start()

    while [ 1 ]:
        time.sleep(10)


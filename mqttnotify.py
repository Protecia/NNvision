import paho.mqtt.client as mqtt
import json
import sys
import urllib,urllib2
import os,shutil
import datetime
import sqlite3 as lite
import nndb

# The callback for when the client receives a CONNACK response from the server.
cameras = {}



def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    client.subscribe("franck/test1")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    try:
        python_obj = json.loads(msg.payload)
        # print("FROM camera:" + python_obj["camera"])
        camera_name=str(python_obj["camera"])
        # print json.dumps(python_obj, sort_keys=True, indent=4)


        if camera_name not in cameras:
            print "** Adding camera..."
            cameras[camera_name]={}
            cameras[camera_name]['init']=False
            cameras[camera_name]['previous']={}
        else:
            print "** Updating Camera..."
        cameras[camera_name]["current"] = python_obj
        camera_analysis(cameras[camera_name])
    except:
        print("=>Exception Raised<=")
        print "Unexpected error:", sys.exc_info()[0]
    


def camera_analysis(camera):
    print "====Camera analysis ==========================================================="
    print "Camera:" , camera['current']['camera'] 
    update_camera_field(camera,"truck",60)
    update_camera_field(camera,"pottedplant",50)
    update_camera_field(camera,"person",60)
    update_camera_field(camera,"car", 40)
    update_camera_field(camera,"dog", 40)
    update_camera_field(camera,"cat", 80)
    print "==============================================================================="

    # print "=>",camera
    if camera['init'] == False:
        camera['init'] = True
        print "Camera INIT is done"
        return 


    print "Checking new state... previous was:",camera["previous"]
    check_previous_field(camera,"pottedplant")
    check_previous_field(camera,"car")
    check_previous_field(camera,"person")
    check_previous_field(camera,"truck")
    check_previous_field(camera,"dog")
    check_previous_field(camera,"cat")

def update_camera_field(camera,field,prob_mini):
    count_key = "nb"+field
    if count_key not in camera['previous']:
        camera['previous'][count_key]=0
    if count_key not in camera:
        camera[count_key]=0


    item_count = 0
    if field in camera['current']:
        for prb in camera['current'][field]:
            print field,"=>prob" , prb['prob']
            if prb['prob'] >= prob_mini:
                item_count += 1

    camera['previous'][count_key] = camera[count_key]
    camera[count_key]=item_count
    print "=> found" , camera[count_key]  , " ", field , "(previous:", camera['previous'][count_key] , ")"


def check_previous_field(camera,field):
    count_key = "nb"+field
    if camera["previous"][count_key] < camera[count_key]:
        print "****************************************** ALARM *****************************************************************"
        msg = ">" + str(camera['current']['camera']) , " :"  + str(field) + " from " + str(camera["previous"][count_key]) + " to " + str(camera[count_key]) 
        notify(camera, msg)
        print "******************************************************************************************************************"
        return True
    return False



def notify(camera,message):
    print "in Notify Camera"
    baseurl = "https://smsapi.free-mobile.fr/sendmsg?"
    filenameresult = camera["current"]["camera"]+"_result.jpg"
    date = datetime.datetime.now()
    filenameserver = camera["current"]["camera"]+ "_" + str(date.month)+ "_" +str(date.day) + "_" + str(date.hour)+ "h" + str(date.minute)+ "mn" + str(date.second) +"s" + "_result.jpg"
    shutil.copyfile(filenameresult,filenameserver)
    message = str(message) + " link: http://37.187.125.48/franck/uploader/results/" + os.path.basename(filenameserver)
    
    params= { 'user' : '29667106' , 'pass' : 'QvleSFbigg0mDc', 'msg' : message }
    print "[SMS]" , message
    url = baseurl + urllib.urlencode(params)
    print "Calling : " , url
    try:
        urllib2.urlopen(url).read()
    except:
        print "Exception while calling URL"
        print "Unexpected error:", sys.exc_info()[0]

    #command="curl -i -X POST -H \"Content-Type: multipart/form-data\" -F \"myFile=@"+filenameserver+"\" http://37.187.125.48:8080/upload   >/dev/null 2>&1"
    command="./upload_picture.sh \""+filenameserver+"\""
    print command
    retvalue=os.system(command)
def CheckDB():
    try:
        con = lite.connect('nnvision.db')
        cur = con.cursor()    
        cur.execute('SELECT SQLITE_VERSION()')
        version = cur.fetchone()
        print "SQLite version: %s" % version                
    except lite.Error, e:
        print "Error %s:" % e.args[0]
        sys.exit(1)



### MAIN ###
CheckDB()
conx = lite.connect('nnvision.db')
#nndb.CreateTable(conx);
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("192.168.128.27",1883,60)
client.loop_forever()

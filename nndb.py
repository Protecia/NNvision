import sqlite3 as lite
import sys


def CreateTable():
    ret = False
    try:
        conx = lite.connect("nnvision.db")
        cur = conx.cursor()
        cur.executescript("""
            DROP TABLE IF EXISTS Cameras;
            CREATE TABLE Cameras(Id INT, Name TEXT, Key TEXT, LastCaptureFile TEXT, LastCaptureTime INT, URL TEXT, USERNAME TEXT, PASS TEXT, JSONRESULT TEXT);
            INSERT INTO Cameras VALUES(1, "Camera49", "key", "", 0, "http://192.168.128.30/tmpfs/auto.jpg", "admin", "simcity69", "{}");
            INSERT INTO Cameras VALUES(2, "Camera49_2", "key", "", 0, "http://192.168.128.40/tmpfs/auto.jpg", "admin", "simcity69", "{}");
            INSERT INTO Cameras VALUES(3, "Camera49_3", "key", "", 0, "http://192.168.128.28/tmpfs/auto.jpg", "admin", "simcity69", "{}");
            DROP TABLE IF EXISTS Results;
            CREATE TABLE Results(Name TEXT, Key TEXT, LastCaptureFile TEXT, LastCaptureTime INT,  JSONRESULT TEXT);
            COMMIT;
            """)
        ret=True

    except lite.Error, e:
        if conx:
            conx.rollback()
        print "Error %s:" % e.args[0]
 
    return ret





def UpdateCamera(cameraname, filename, capturetime):
    ret=False
    try:
       conx = lite.connect("nnvision.db")
       cur = conx.cursor()
       query = """
       BEGIN;
       UPDATE Cameras SET LastCaptureFile="%s",LastCaptureTime="%s",JSONRESULT=""  WHERE Name="%s";
       COMMIT;
       """  % (filename,str(capturetime),cameraname)
       print "SQLQUERY:" + query
       cur.executescript(query)
       conx.close()
       ret = True;
       
    except lite.Error, e:
        print "SQL Error %s:" % e.args[0]

    return ret



def GetCamera(cameraname, camerainfos):
    ret = False
    try:
        conx = lite.connect("nnvision.db")
        cur = conx.cursor()
        query = "SELECT Id,Name, Key, LastCaptureFile,LastCaptureTime,URL,USERNAME,PASS,JSONRESULT  FROM Cameras WHERE Name=\"" + cameraname + "\";"
        print "SQL Query:" , query
        cur.execute(query)
        col_names = [cn[0] for cn in cur.description]
        rows = cur.fetchall()
        conx.close()
        for row in rows:
            camera={}
            camera['Id']=row[0]
            camera['Name']=row[1]
            camera['Key']=row[2]
            camera['LastCaptureFile']=row[3]
            camera['LastCaptureTime']=row[4]
            camera['URL']=row[5]
            camera['USERNAME']=row[6]
            camera['PASS'] = row[7]
            camera['JSONRESULT']=row[8]
            camerainfos.append(camera);
        ret =  True;

    except lite.Error, e:
        if conx:
            conx.rollback()
        print "SQL Error %s:" % e.args[0]
    return ret 

def GetCameras(cameras):
    ret = False
    try:
        conx = lite.connect("nnvision.db")
        cur = conx.cursor()
        cur.execute("SELECT Id,Name, Key, LastCaptureFile,LastCaptureTime,URL,USERNAME,PASS,JSONRESULT  FROM Cameras;")
        col_names = [cn[0] for cn in cur.description]
        rows = cur.fetchall()
        for row in rows:
            newcamera={}
	    cameraname=str(row[1])
            newcamera={}
            newcamera['Id']=row[0]
            newcamera['Name']=row[1]
            newcamera['Key']=row[2]
            newcamera['LastCaptureFile']=row[3]
            newcamera['LastCaptureTime']=row[4]
            newcamera['URL']=row[5]
            newcamera['USERNAME']=row[6]
            newcamera['PASS'] = row[7]
            newcamera['JSONRESULT']=row[8]
            cameras.append(newcamera)
        ret =  True;

    except lite.Error, e:
        if conx:
            conx.rollback()
        print "SQL Error %s:" % e.args[0]

    return False


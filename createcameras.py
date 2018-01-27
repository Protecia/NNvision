import sqlite3 as lite
import nndb
conx = 0

def CreateTestCameras():
    ret = False
    try:
        conx = lite.connect("nnvision.db")
        cur = conx.cursor()
        cur.executescript("""
            INSERT INTO Cameras VALUES(1, "Camera49", "key", "", 0, "http://192.168.128.30/tmpfs/auto.jpg", "admin", "simcity69", "{}");
            INSERT INTO Cameras VALUES(2, "Camera49_2", "key", "", 0, "http://192.168.128.40/tmpfs/auto.jpg", "admin", "simcity69", "{}");
            INSERT INTO Cameras VALUES(3, "Camera49_3", "key", "", 0, "http://192.168.128.28/tmpfs/auto.jpg", "admin", "simcity69", "{}");
            """)
        ret=True

    except lite.Error, e:
        if conx:
            conx.rollback()
        print "Error %s:" % e.args[0]

    return ret



# MAIN
# -----
nndb.CreateTable()
CreateTestCameras()

Cameras=[]
print "================"
print "Checking Cameras"
print "================"
nndb.GetCameras(Cameras)

for cam in Cameras:
    print "=>", cam['Name'] 


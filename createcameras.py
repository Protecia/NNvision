import sqlite3 as lite
import nndb
conx = 0



# MAIN
# -----
nndb.CreateTable()

Cameras=[]
print "================"
print "Checking Cameras"
print "================"
nndb.GetCameras(Cameras)

for cam in Cameras:
    print "=>", cam['Name'] 


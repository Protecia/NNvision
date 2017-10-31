
from inspect import getmembers
from pprint import pprint
import os,sys,signal
import os.path
import time
import errno
from subprocess import call
import cherrypy
from cherrypy.lib import static
from cherrypy.lib.static import serve_file 
from filelock import FileLock
import sqlite3 as lite
import nndb


localDir = os.path.dirname(__file__)
absDir = os.path.join(os.getcwd(), localDir)
url_results = "http://37.187.125.48/franck/uploader/results/"


def signal_handler(signal, frame):
    print('signal ignored! %s' % (str(signal)) )
        
def signal_handler_exit(signal, frame):
    print('signal received, exiting! %s' % (str(signal)) )
    sys.exit(0)


class VideoAnalysis(object):
    

    def __init__(self):
        self.active = True

    def acquire(self,filename):
	ret = None
        """ Acquire the lock, if possible. If the lock is in use, and `blocking` is False, return False.
            Otherwise, check again every `self.delay` seconds until it either gets the lock or
            exceeds `timeout` number of seconds, in which case it raises an exception.
        """
        while True:
            try:
		lockfilename=filename + ".lock"
                #lockfilename=os.path.join(os.getcwd(), "outfilelock")
                print "Locking outlockfile:" + lockfilename
                ret = os.open( lockfilename, os.O_EXCL | os.O_RDWR )
		return ret
            except OSError as e:
                print "Failed locking: "+lockfilename
                return None
        return None

    def release(self,lockfd):
        """ Get rid of the lock by deleting the lockfile.
            When working in a `with` statement, this gets automatically
            called at the end.
        """
        os.close(lockfd);
        print "Unlock file"

    @cherrypy.expose
    def index(self):
        return """
        <html><body>
            <h2>Upload a file</h2>
            <form action="upload" method="post" enctype="multipart/form-data">
            filename: <input type="file" name="picture" /><br />
			method: <input type="text" name="method" value="shell" /><br />
			<input type="hidden" name="key" value="test1" />
            <input type="submit" />
            </form>
            <h2>Results:</h2>
            <a href='%s' target="new">Results</a>
        </body></html>
        """ % ( url_results )


    @cherrypy.expose
    def upload(self, picture,key,method):
        # some return texts
        out = """<html>
        <body>
            picture length: %s   <br/>
            picture filename: %s <br/>
            picture mime-type: %s<br/>
            processed: %s <br/> 
            jobId: %s <br/>
            result: %s <br/>
        </body>
        </html>"""
        out_error_key = """<html><body>invalid key</body>"""
        out_error_method = """<html><body>unknown method</body>"""
        out_error_mime = """<html><body>unhandled mime type</body>"""
        out_href = """<a href="%s">Link</a>"""

	# check key
        if key != 'test1':
            print 'ERROR: Invalid key ' + str(key)
            return out_error_key

        # check mime type
        if (str(picture.content_type) != "image/jpeg") :
            print 'ERROR: Invalid mime type '
            return out_error_mime
            


        # Store file
        size = 0
        filename = 'uploads/' + os.path.basename(picture.filename)
        fh = open(filename,'w')
        # print 'fh: %s' % str(fh)
        #pprint(getmembers(fh))

        while True:
            data = picture.file.read(8192)
            if not data:
                break
            size += len(data)
            fh.write(data)
        fh.close()
        # pprint(getmembers(picture))

        # we handle the call with the requested method
	processed=False
	jobId=0
	result=""

        # shell:
        if method == 'shell':
            err = call(['/bin/bash', 'server_queue_shell.sh', filename, key])
            if (err == -15): #signal received
                processed=True
                result = out_href % ( url_results + picture.filename + "_result.jpg" )
        elif method == 'mqtt':
            jobId = call(['/bin/bash', 'server_queue_mqtt.sh', filename, key])
            processed=True
        elif method == 'queue':
            jobId = call(['/bin/bash', 'server_queue_pid.sh', filename, key])
            processed=True
	elif method == 'callback':
            jobId = call(['/bin/bash', 'server_queue_callback.sh', filename, key]) 
        else :
            return out_error_method

        return out % (str(size), picture.filename, picture.content_type, str(processed), str(jobId), result)


    @cherrypy.expose
    def uploads(self,name):
        filename=os.path.join(os.getcwd(), "uploads/" + name)
        Cameras=[]
        if nndb.GetCamera(name, Cameras) == True :
            print "=>" , Cameras
            filename=os.path.join(os.getcwd(),  Cameras[0]["LastCaptureFile"])
            print "uploads :  serving file " + filename; 
            ret = serve_file(filename) 
        return ret

    @cherrypy.expose
    def results(self,name):
        filename=os.path.join(os.getcwd(), "uploads/" + name)
        Cameras=[]
        if nndb.GetCamera(name, Cameras) == True :
            print "=>" , Cameras
            filename=os.path.join(os.getcwd(),  Cameras[0]["LastCaptureFile"] + "_result.jpg")
            print "uploads :  serving file " + filename;
            ret = serve_file(filename)
        return ret

    @cherrypy.expose
    def videostream(self,name):
        # Test
        out = ""
        Cameras=[]
        if nndb.GetCamera(name, Cameras) == True :
            print "=>" , Cameras
            filename=os.path.join(os.getcwd(),  Cameras[0]["LastCaptureFile"])
            rtspstream="rtsp://admin:simcity69@192.168.128.40/11"
            out = """
            <html>
            <title>Stream from:%s</title>
            <body>
            <embed type="application/x-vlc-plugin" pluginspage="http://www.videolan.org" width="320" height="240" target="%s" />
            </body>
            </html>
            """ % (name,rtspstream)
        return out

# bootstrap
if __name__ == '__main__':

    # debug
    # cherrypy._cpserver.Server.max_request_body_size = 14*1024*1024
    # cherrypy.config.update({'server.socket_host': '0.0.0.0','server.socket_port': 8080})
    # cherrypy.config.update({'engine.autoreload.on' : False })
    # cherrypy.quickstart(VideoAnalysis())
    # sys.exit(0)


    # daemon
    fpid = os.fork()
    if fpid!=0:
        # Running as daemon now. PID is fpid
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    cherrypy._cpserver.Server.max_request_body_size = 14*1024*1024
    cherrypy.config.update({'server.socket_host': '0.0.0.0','server.socket_port': 8080})
    cherrypy.config.update({'engine.autoreload.on' : False })
    cherrypy.quickstart(VideoAnalysis())




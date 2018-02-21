import requests
from darknet_python import darknet as dn
from scipy.misc import imread
from io import BytesIO
import cv2
import numpy as np

# process the camera image for darknet entry
r = requests.get("http://192.168.0.19/auto.jpg", auth=("admin","julien69"), stream=True)
arr = imread(BytesIO(r.content))
im = dn.array_to_image(arr)

# load the Neural Network and the meta
net = dn.load_net(b"darknet_python/cfg/yolo.cfg", b"../../yolo.weights", 0)
meta = dn.load_meta(b"darknet_python/cfg/coco.data")

#send the image to the detection
result = dn.detect2(net, meta, im, thresh=0.5)



arr = cv2.imdecode(BytesIO(r.content),1)

image = np.asarray(bytearray(r.content), dtype="uint8")
image = cv2.imdecode(image, cv2.IMREAD_COLOR)

from urllib.request import urlopen
urlopen("http://192.168.0.19/auto.jpg", auth=("admin","julien69"), stream=True)
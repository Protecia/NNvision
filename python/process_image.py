import requests
import darknet as dn
from scipy.misc import imread
from io import BytesIO


# process the camera image for darknet entry
r = requests.get("http://192.168.0.18/auto.jpg", auth=("admin","julien69"), stream=True)
arr = imread(BytesIO(r.content))
im = dn.array_to_image(arr)

# load the Neural Network and the meta
net = dn.load_net(b"cfg/yolo.cfg", b"yolo.weights", 0)
meta = dn.load_meta(b"cfg/coco.data")

#send the image to the detection
result = dn.detect2(net, meta, im)
import sys
import paho.mqtt.client as mqtt
import urllib

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    print("Publishing..." + client.msg)
    client.publish(str(client.channel),client.msg)
    client.disconnect()

def on_disconnect(client, userdata, rc):
    exit()


if (len(sys.argv) < 3):
    exit()

client = mqtt.Client()
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.channel = sys.argv[1]
client.msg=sys.argv[2]
print("msg:" + client.msg)
client.connect("192.168.128.27",1883,60)
client.loop_forever()



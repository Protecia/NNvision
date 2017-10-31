import paho.mqtt.client as mqtt
import json

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    client.subscribe("franck/test1")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    try:
        python_obj = json.loads(msg.payload)
        print("FROM camera:" + python_obj["camera"])
        print json.dumps(python_obj, sort_keys=True, indent=4)
    except:
        print("=>Invalid Json")

### MAIN ###
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("192.168.128.27",1883,60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()



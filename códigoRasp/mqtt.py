# import paho.mqtt.client as mqtt #import the client1
# broker_address="localhost" 
# #broker_address="iot.eclipse.org" #use external broker
# client = mqtt.Client("P1") #create new instance
# client.username_pw_set(username="hugo",password="hugo2023")
# client.connect(broker_address) #connect to broker
# v#publish

import paho.mqtt.client as mqtt
from settings import password,user
from datetime import datetime
import ssl
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    
    
    

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

client = mqtt.Client("PUB")
client.username_pw_set(username="{}".format(user),password="{}".format(password))
client.on_connect = on_connect
client.on_message = on_message

client.tls_set(ca_certs="ca.crt", certfile="client.crt", keyfile="client.key", tls_version=ssl.PROTOCOL_TLS_CLIENT)
client.tls_insecure_set(True)


client.connect("192.168.1.67", 8853, 60)

client.publish("house/bulbs/bulb1","UI,{}".format(datetime.now()),retain=True,qos=1)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()


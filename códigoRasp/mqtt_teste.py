from umqtt.simple import MQTTClient
import ussl as ssl

# Test reception e.g. with:
# mosquitto_sub -t foo_topic


server='192.168.1.67'      # this has to match the MQTT server CN or SAN credentials in server_crt.pem
server_port=1883
server_keepalive=60     # if you don't include a keepalive nothing works.
mqtt_topic='test/topic01'
local_client_name='client1'
usern='u7jwBSqtlJWHZiza3yFp'



def connectMQTT():
    client = MQTTClient('client', '192.168.1.67', user='u7jwBSqtlJWHZiza3yFp', password='')
        
        
    
    client.connect()
    return client

client=connectMQTT()
print("Connecting to MQTT Server...")
client.publish("v1/devices/me/telemetry","{'temperature':95}")

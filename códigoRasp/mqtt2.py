from umqtt.simple import MQTTClient
import ussl as ssl
import time
from settings import conn_conf
from settings import conf
from machine import Pin, Timer
import sys
import dht
import json
import _thread
# Test reception e.g. with:
# mosquitto_sub -t foo_topic

print('Current time: ' + str(time.localtime()))
server='192.168.1.67'      # this has to match the MQTT server CN or SAN credentials in server_crt.pem
server_port=8853
server_keepalive=3600    # if you don't include a keepalive nothing works.
mqtt_topic='test/topic01'
local_client_name='client1'
periodo_t=conf['periodo_t']
periodo_h=conf['periodo_h']
with open('ca_crt.der', 'rb') as f:
    ca_data = f.read()
f.close()
print('Read CA Certificate... OK')

with open('client_crt.der', 'rb') as f:
    user_cert = f.read()
f.close()
print('Read User Certificate... OK')


with open('client_key.der', 'rb') as f:
    user_key = f.read()
f.close()
print('Read User Key... OK')
ssl_params={'key':user_key,
            'cert':user_cert,
            'cadata':ca_data,
            'server_hostname':"192.168.1.67",
            'server_side':False,
            'cert_reqs':ssl.CERT_REQUIRED,
            'do_handshake':True}


def sub_cb(topic, msg):
    msg=str(msg.decode("utf-8"))
    topic=str(topic.decode("utf-8"))
    print(topic , msg)
    if(topic == "led" and msg == "ligar"):
        led.high()
    if(topic == "led" and msg == "desligar"):
        led.low()
    

def subs():
    while True:
            # Non-blocking wait for message
            client.check_msg()
            
            time.sleep(1)
        
def connectMQTT():
    client = MQTTClient(
        client_id=local_client_name,
        server=server,
        port=server_port,
        keepalive=server_keepalive,
        ssl=True,
        ssl_params=ssl_params,
        user=conn_conf['user'],
        password=conn_conf['password']
    )
    client.set_callback(sub_cb)
    client.connect()
    return client

client=connectMQTT()
client.publish('house', 'U2IUI', retain=False)
client.subscribe("led")
_thread.start_new_thread(subs, ())

rtc=machine.RTC()
pir = Pin(19, Pin.IN,Pin.PULL_UP)
ledPir=Pin(20,Pin.OUT)
led=Pin(11,Pin.OUT)
sensor=dht.DHT11(Pin(14))
led.low()

time.sleep(1)
cont=0
def getTime():
    lista=[]
    
    lista.extend(["{:02d}".format(rtc.datetime()[0]),"{:02d}".format(rtc.datetime()[1]),"{:02d}".format(rtc.datetime()[2])])
    lista.extend(["{:02d}".format(rtc.datetime()[4]),"{:02d}".format(rtc.datetime()[5]),"{:02d}".format(rtc.datetime()[6])])
    
    return lista
while True:
    try:
        sensor.measure()
        if(cont%periodo_t==0):
            
            tempL=["temperatura:",str(sensor.temperature()),"data:",getTime()]
            client.publish('temp',json.dumps(tempL), retain=False)
            print("Temperatura {}".format(str(sensor.temperature())))
        if(cont%periodo_h==0):
            humidL=["humidade:",str(sensor.humidity()),"data:",getTime()]
            client.publish('humid', json.dumps(humidL), retain=False)
            print("Humidade {}".format(str(sensor.humidity())))
            


        if(pir.value() == 1):
            pirL=["pir:",str(1),"data:",getTime()]
            client.publish('pir', json.dumps(pirL), retain=False)
            ledPir.high()
            time.sleep(2)
        else:
            ledPir.low()
            time.sleep(1)
        cont+=1
    except OSError as e:
		print("Cant read:", e)
		sys.print_exception(e)
    


import wifimgr     # importing the Wi-Fi manager library
from time import sleep     
import machine
import network
import gc
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
import ntptime

try:
  import usocket as socket
except:
  import socket
#machine.reset()

wlan_sta = network.WLAN(network.STA_IF)
wlan = wifimgr.get_connection()        #initializing wlan
if wlan is None:
    print("Could not initialize the network connection.")
    ledPir=Pin(20,Pin.OUT)
    ledPir.high()
    while True:
        pass  
print(" Raspberry Pi Pico W OK")
rtc=machine.RTC()
ntptime.time()

print(wlan_sta.ifconfig())
print('Current time: ' + str(time.localtime()))
server='192.168.1.101'      # this has to match the MQTT server CN or SAN credentials in server_crt.pem
server_port=8853
server_keepalive=3600    # if you don't include a keepalive nothing works.
mqtt_topic='test/topic01'
local_client_name='client1'
periodo_t=conf['periodo_t']
periodo_h=conf['periodo_h']

pir = Pin(19, Pin.IN,Pin.PULL_UP)
ledPir=Pin(20,Pin.OUT)
led=Pin(11,Pin.OUT)
sensor=dht.DHT11(Pin(14))

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

def getTime():
    lista=[]
    
    lista.extend(["{:02d}".format(rtc.datetime()[0]),"{:02d}".format(rtc.datetime()[1]),"{:02d}".format(rtc.datetime()[2])])
    lista.extend(["{:02d}".format(int(rtc.datetime()[4])),"{:02d}".format(rtc.datetime()[5]),"{:02d}".format(rtc.datetime()[6])])
    
    return lista
def sub_cb(topic, msg):
    msg=str(msg.decode("utf-8"))
    topic=str(topic.decode("utf-8"))
    print(topic , msg)
    if(topic == "led" and msg == "ligar"):
        led.high()
        
        getStatus()
    if(topic == "led" and msg == "desligar"):
        led.low()
        
        getStatus()
    if(topic == "status" and msg == "get"):
        
        getStatus()
def getStatus():
    sleep(1)
    status={'led':str(led.value()),"ip":wlan_sta.ifconfig()[0],"hora":getTime()}
    client.publish('status', json.dumps(status), retain=False)

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


ledPir.high()
client.subscribe("led")
client.subscribe("status")
_thread.start_new_thread(subs, ())
led.low()

time.sleep(1)
getStatus()
cont=0

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
    






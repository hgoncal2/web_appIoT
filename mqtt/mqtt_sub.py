import paho.mqtt.client as mqtt #import the client1
import time
from settings import password,user
import ssl
import os
import mysql.connector
import json
import requests
import socketio
from threading import Thread
here = os.path.dirname(os.path.abspath(__file__))
time.sleep(5)
ca_crt = os.path.join(here, 'ca.crt')
client_crt = os.path.join(here, 'client.crt')
client_key = os.path.join(here, 'client.key')
cnx = mysql.connector.connect(user='root', password='hugo2023',
                              host='127.0.0.1',port='3306',
                              database='iot')
cursor=cnx.cursor() 
sio = socketio.Client()
@sio.on('led')
def on_message(data):
    print('I received a message33!')
    if(data['data'] == "ligar"):
        client.publish("led","ligar")
    if(data['data'] == "desligar"):
        client.publish("led","desligar")

@sio.on('status')
def on_message(data):
    client.publish("status","get")
    
def on_message(client, userdata, message):
    try:
        msg=str(message.payload.decode("utf-8"))
        if(message.topic=="status"):
             sio.emit("status",json.loads(msg))
        else:
            
            lista=json.loads(msg) #decode json data
            #val,date=msg.split(";")
            val=lista[1]
            date_aux=lista[3]
            date="-".join(str(x) for x in date_aux[0:3])
            date+=" "
            date2=":".join(str(x) for x in date_aux[3:])
            date=date + date2
            #print(date)
            

            if(message.topic=="temp"):
                print(date[0])
                sql = "INSERT INTO temp (valor, data) VALUES (%s, %s)"
                val = (val, date)
                cursor.execute(sql, val)
                cnx.commit()

                #print(cursor.rowcount, "record inserted.")


            if(message.topic=="humid"):
                print(date[0])
                sql = "INSERT INTO humid (valor, data) VALUES (%s, %s)"
                val = (val, date)
                cursor.execute(sql, val)
                cnx.commit()

               # print(cursor.rowcount, "record inserted.")

            if(message.topic=="pir"):

                sql = "INSERT INTO pir (valor, data) VALUES (%s, %s)"
                val = (val, date)
                cursor.execute(sql, val)
                cnx.commit()
                sio.emit("move",{'data':'on'})
                # payload = {'q': 'move'}
                # try:
                #     requests.get("http://localhost:5000/backend", params=payload)
                # except Exception as e:
                #     print("backend indisponível",e)
            

    except Exception as e:
        print(e)
        



        
        
        #print(cursor.rowcount, "record inserted.")


def ws():
    sio.connect('http://localhost:5000',wait_timeout = 10)
    print('my sid is', sio.sid)
    sio.wait()

t1 = Thread(target=ws)
t1.start()


broker_address="localhost"
print("creating new instance")
client = mqtt.Client() #create new instance
client.username_pw_set(username="{}".format(user),password="{}".format(password))
print("connecting to broker")
client.tls_set(ca_certs=ca_crt, certfile=client_crt, keyfile=client_key, tls_version=ssl.PROTOCOL_TLS_CLIENT)
client.tls_insecure_set(True)
client.connect(broker_address,8853,keepalive=60) #connect to broker

client.on_message = on_message
print("Subscribing to topic","house/")
client.subscribe("temp",qos=0)
client.subscribe("humid",qos=0)
client.subscribe("pir",qos=0)
client.subscribe("status",qos=0)

client.loop_forever()

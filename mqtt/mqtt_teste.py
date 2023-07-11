import paho.mqtt.client as mqtt
import ssl
import os
import mysql.connector
import time
here = os.path.dirname(os.path.abspath(__file__))
flag=0

cnx = mysql.connector.connect(user='root', password='hugo2023',
                              host='127.0.0.1',port='3306',
                              database='iot')
cursor=cnx.cursor()
cursor.execute("select valor from temp")
records = cursor.fetchall()
for row in records:
     print(row[0])


import subprocess
import sys
from threading import Thread
import time
import ssl
import os
import mysql.connector
import subprocess
import json
from multiprocessing.connection import Listener
import socket
import threading

cnx = mysql.connector.connect(user='root', password='hugo2023',
                              host='127.0.0.1',port='3306',
                              database='iot')
cursor=cnx.cursor() 
lista_v_t=[]
lista_d_t=[]
t="select data from temp "
t1="select valor from temp"
h1="select data from humid"
h="select valor from humid"
flag=0

cursor.execute(t1)
records = cursor.fetchall()
for row in records:
     lista_v_t.append(row[0])
cursor.execute(t)
records = cursor.fetchall()
for row in records:
     lista_d_t.append((row[0]).split(" "))
lista_v_h=[]
lista_d_h=[]
cursor.execute(h)
records = cursor.fetchall()
for row in records:
     lista_v_h.append(row[0])
cursor.execute(h1)
records = cursor.fetchall()
for row in records:
     lista_d_h.append((row[0]).split(" "))
     
print("dwaadw")

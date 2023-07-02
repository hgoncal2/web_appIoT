from flask import Flask,render_template,request,redirect,url_for
import subprocess
import sys
from threading import Thread
import paho.mqtt.client as mqtt #import the client1
import time
from mqtt.settings import password,user
import ssl
import os
import mysql.connector
import subprocess
import json
from multiprocessing.connection import Listener
import socket
import threading

from turbo_flask import Turbo



here = os.path.dirname(os.path.abspath(__file__))

ca_crt = os.path.join(here, 'mqtt/ca.crt')
client_crt = os.path.join(here, 'mqtt/client.crt')
client_key = os.path.join(here, 'mqtt/client.key')
app=Flask(__name__)
turbo = Turbo(app)
val=""

here = os.path.dirname(os.path.abspath(__file__))
@app.context_processor
def inject_load():
	return {'load1':val}

def printit():
  	with app.app_context():
  		global val
  		val=""
  		inject_load()
  		turbo.push(turbo.replace(render_template("index2.html"), 'load'))
  		global t
  		t.cancel()
  		t=threading.Timer(5.0, printit)
  		global flag_t
  		flag_t=1
  	
t=threading.Timer(5.0, printit)
flag_t=1

@app.route("/backend")
def back():
	if request.args.get('q') == "move":
		with app.app_context():
			global val
			val="DETECTADO MOVIMENTO!"
			inject_load()
			turbo.push(turbo.replace(render_template("index2.html"), 'load'))
			global flag_t
			if(flag_t==1):
				flag_t=0
				t.start()
			return '', 204
	else:
		return render_template("404.html")
			
		
		
		
		

	


@app.route('/')
def default():
	global val
	val=""
	return redirect(url_for('index'))

@app.route("/dashboard")
def index():
	global val
	val=""
	cnx = mysql.connector.connect(user='root', password='hugo2023',
                              host='127.0.0.1',port='3306',
                              database='iot')
	cursor=cnx.cursor() 
	lista_v_t=[]
	lista_d_t=[]
	if request.args.get('valor_graf_t') is not None and request.args.get('valor_graf_t').isdigit():
		print("i'm in")
		t="select data from temp ORDER BY id desc LIMIT {}".format(request.args.get('valor_graf_t'))
		t1="select valor from temp ORDER BY id desc LIMIT {}".format(request.args.get('valor_graf_t'))
		h1="select data from humid ORDER BY id desc LIMIT {}".format(request.args.get('valor_graf_t'))
		h="select valor from humid ORDER BY id desc LIMIT {}".format(request.args.get('valor_graf_t'))
		flag=1
	else:
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

	if(flag==1):
		lista_v_t.reverse()
		lista_d_t.reverse()
		lista_d_h.reverse()
		lista_v_h.reverse()
	return render_template("sidebar.html",data_v_t=json.dumps(lista_v_t),data_d_t=lista_d_t,data_v_h=json.dumps(lista_v_h),data_d_h=lista_d_h,val=val)




    
    


@app.errorhandler(404)
def page_not_found(e):
	return render_template("404.html")

@app.errorhandler(500)
def page_not_found(e):
	return render_template("500.html")

if __name__ == "__main__":
	#t1 = Thread(daemon=True,target=t).start()
	#subprocess.runrunrunrun(['sh', 'mqtt/teste.sh'])
	
	
	app.run(host="0.0.0.0", debug=True,threaded=True)
    
   


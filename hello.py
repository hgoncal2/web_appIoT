from flask import Flask,render_template,request,redirect,url_for,flash
import subprocess
import sys
from threading import Thread

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
from markupsafe import Markup
from turbo_flask import Turbo
import random
from flask_socketio import SocketIO,emit
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField
from tenacity import wait_exponential, retry, stop_after_attempt
from jinja2 import Environment
from flask_sqlalchemy import SQLAlchemy




here = os.path.dirname(os.path.abspath(__file__))

ca_crt = os.path.join(here, 'mqtt/ca.crt')
client_crt = os.path.join(here, 'mqtt/client.crt')
client_key = os.path.join(here, 'mqtt/client.key')
app=Flask(__name__)
socketio = SocketIO(app)
turbo = Turbo(app)
app.config['SECRET_KEY']="randomstringetal"
val=""
led='0'
timer=None
status=None



@app.context_processor
def inject_load():
	return {'load1': val,'led_estado':led}

def printit():
  	with app.app_context():
  		global val
  		val=""
  		inject_load()
  		turbo.push(turbo.replace(render_template("alerts.html"), 'load'))
  		
  		
  		




def back():
	
	with app.app_context():
		global val
		
		global timer
		val='<div class="alert alert-warning alert-dismissible text-center " role="alert"><strong>Movimento Detectado!</strong></div>'
		inject_load()
		print("entrei")
		turbo.push(turbo.replace(render_template("alerts.html"),'load'))
		#turbo.push(turbo.replace("Agora!",'agora'))
		timer = threading.Timer(5, remove)
		timer.start()
		
		
		
def remove():
	with app.app_context():
		global timer
		global val
		val=""
		inject_load()
		print("remove")
		turbo.push(turbo.replace(render_template("alerts.html"),'load'))
		timer.cancel()
			
	
			
		
		
		
		

	

# @app.before_request 
# def before_request_callback():
# 	global val
# 	if(val!=""):
# 		val=""
# 		inject_load()
# 		print("entrei33")
# 		turbo.push(turbo.replace(render_template("alerts.html"), 'load'))





@app.route('/')
def default():
	return redirect(url_for("dashboard"))
@app.route("/dashboard")
def dashboard():
	cnx = mysql.connector.connect(user='root', password='hugo2023',
	                              host='127.0.0.1',port='3306',
	                              database='iot')
	print("entrei")
	global val
	val=""
	 
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

	cursor=cnx.cursor()
	lista_p=[]
	p="select data from pir"
	cursor.execute(p)
	records = cursor.fetchall()
	for row in records:
		lista_p.append((row[0]).split(" "))
	items=[]
	lista_p.reverse()
	for i in range(len(lista_p)):
	    an_it=dict(id=str(i),valor="Ativado",data=str(lista_p[i][0]),hora=str(lista_p[i][1]))
	    items.append(an_it)
	try:
		tempo_mov=tempoPassado(items[0])
	except Exception as e:
		tempo_mov="Erro!"
		print("Erro!", e)
	print(tempo_mov)
	cnx.close()
	return render_template("base.html",data_v_t=json.dumps(lista_v_t),data_d_t=lista_d_t,data_v_h=json.dumps(lista_v_h),data_d_h=lista_d_h,val=val,pag="dash",ultimo_valor_t=lista_v_t[-1],ultimo_valor_h=lista_v_h[-1],ultimo_mov=tempo_mov)

@app.route("/backend" , methods=['GET','POST'])
def backend():

	return redirect(url_for("conf",path="alertas"))
			
	

@app.route('/conf/<path>/' , methods=['GET','POST'])
def conf(path):

	cnx = mysql.connector.connect(user='root', password='hugo2023',
	                              host='127.0.0.1',port='3306',
	                              database='iot')
	cursor=cnx.cursor()
	if(path=="alertas"):
		t="select temp,maxTemp,minTemp,humid,maxHumid,minHumid,pir from alertas;";
		cursor.execute(t);
		records=cursor.fetchall();
		try:

			temp,maxTemp,minTemp,humid,maxHumid,minHumid,pir=records[0]
			print(temp,maxTemp,minTemp,humid,maxHumid,minHumid,pir)
			return render_template("base.html",pag="alertas",temp=str(temp),minTemp=str(minTemp),maxTemp=str(maxTemp),humid=str(humid),maxHumid=str(maxHumid),minHumid=str(minHumid),pir=str(pir))
		except Exception as e:
			temp,humid,pir=str(0),str(0),str(0);
			maxTemp,minTemp,maxHumid,minHumid="NULL","NULL","NULL","NULL"
			return render_template("base.html",pag="alertas",temp=str(temp),minTemp=str(minTemp),maxTemp=str(maxTemp),humid=str(humid),maxHumid=str(maxHumid),minHumid=str(minHumid),pir=str(pir))
	try:
		
		if(request.args.get('conf_led') == "ligar"):
			socketio.emit("led",{'data':'ligar'})
			return redirect(url_for('conf_led'))
			
			
		if(request.args.get('conf_led') == "desligar"):
			socketio.emit("led",{'data':'desligar'})
			return redirect(url_for('conf_led'))


			

	except Exception as e:
		print(e)
	try:
		getEstado()
		return render_template("base.html",pag="conf",teste="1",maxHum="")
	except Exception as e:
		print(e)
		return "Erro!"
@app.route('/conf/leds')
def conf_led():
	return redirect(url_for('conf'))


@app.route('/history/<sensor>')
def history(sensor):
	cnx = mysql.connector.connect(user='root', password='hugo2023',
	                              host='127.0.0.1',port='3306',
	                              database='iot')
	
	cursor=cnx.cursor() 
	if(sensor=="temp"):
		 
		lista_v_t=[]
		lista_d_t=[]
		t="select data from temp "
		t1="select valor from temp "
		
		flag=0

		cursor.execute(t1)
		records = cursor.fetchall()
		for row in records:
		     lista_v_t.append(row[0])
		cursor.execute(t)
		records = cursor.fetchall()
		for row in records:
		     lista_d_t.append((row[0]).split(" "))
		items=[]
		lista_v_t.reverse()
		lista_d_t.reverse()
		for i in range(len(lista_v_t)):
		    an_it=dict(id=str(i),valor=str(lista_v_t[i]) + "°C",data=str(lista_d_t[i][0]),hora=str(lista_d_t[i][1]))
		    items.append(an_it)
		cnx.close()
		return render_template("base.html",pag="history",items=items)
		



	if(sensor=="humid"):
		
		lista_v_h=[]
		lista_d_h=[]

		h1="select data from humid "
		h="select valor from humid "
		
		cursor.execute(h)
		records = cursor.fetchall()
		for row in records:
		     lista_v_h.append(row[0])
		cursor.execute(h1)
		records = cursor.fetchall()
		for row in records:
		     lista_d_h.append((row[0]).split(" "))
		items=[]
		lista_d_h.reverse()
		lista_v_h.reverse()
		for i in range(len(lista_v_h)):
		    an_it=dict(id=str(i),valor=str(lista_v_h[i])+"%",data=str(lista_d_h[i][0]),hora=str(lista_d_h[i][1]))
		    items.append(an_it)
		cnx.close()
		return render_template("base.html",pag="history",items=items)

	if(sensor=="pir"):
		
		lista_p=[]
		p="select data from pir"
		cursor.execute(p)
		records = cursor.fetchall()
		for row in records:
			lista_p.append((row[0]).split(" "))
		items=[]
		lista_p.reverse()
		for i in range(len(lista_p)):
		    an_it=dict(id=str(i),valor="Ativado",data=str(lista_p[i][0]),hora=str(lista_p[i][1]))
		    items.append(an_it)
		cnx.close()
		return render_template("base.html",pag="history",items=items)
	
	

	return render_template("404.html")
		
def getEstado():
	socketio.emit("status",{'data':'get'})
	##usar sleep para pagina dos leds
	#time.sleep(1)


def tempoPassado(dic):
	datai=datetime.strptime("{} {}".format(dic["data"],dic["hora"]),
	              '%Y-%m-%d %H:%M:%S')
	datan= datetime.now()

	d=(datan-datai)
	days=d.days
	hours, remainder = divmod(d.seconds, 3600)
	minutes, seconds = divmod(remainder, 60)
	print(days,hours,minutes)
	if( days > 0):
		str="{} dia(s), {} horas(s) e {} minuto(s)".format(days,hours,minutes)
	else:
	    if(hours>0):
	        str="{} horas(s), {} minuto(s) e {} segundo(s)".format(hours,minutes,seconds)
	    else:
	        if(minutes>0):
	            str="{} minuto(s) e {} segundo(s)".format(minutes,seconds)
	        else:
	            str="{} segundo(s)".format(seconds)
	
	return str
        
	
@app.route('/receivedata', methods=['POST'])
def receive_data():
	if((request.form['temp_check']=="1" and request.form['tempMax']=="" and request.form['tempMin']=="")):
		 flash(render_template("boostrap_notification.html",erro="Temperatura Máxima/Mínima!"))
		 return redirect(url_for("conf",path="alertas"))
	else:
		if((request.form['humid_check']=="1" and request.form['humidMax']=="" and request.form['humidMin']=="")):
			 flash(render_template("boostrap_notification.html",erro="Humidade Máxima ou Mínima!"))
			 return redirect(url_for("conf",path="alertas"))
		else:

			try:
				cnx = mysql.connector.connect(user='root', password='hugo2023',
			                              host='127.0.0.1',port='3306',
			                              database='iot')
				cursor=cnx.cursor()
				if(request.form['tempMax']==""):
					tempMax="NULL"
				else:
					tempMax=request.form['tempMax']
				if(request.form['tempMin']==""):
					tempMin="NULL"
				else:
					tempMin=request.form['tempMin']
				if(request.form['humidMax']==""):
					humidMax="NULL"
				else:
					humidMax=request.form['humidMax']
				if(request.form['humidMin']==""):
					humidMin="NULL"
				else:
					humidMin=request.form['humidMin']
				print(request.form['temp_check'],tempMax,tempMin,request.form['humid_check'],humidMax,humidMin,request.form['pir_check'])

				query="replace into alertas (id,temp,maxTemp,minTemp,humid,maxHumid,minHumid,pir) values (5,{},{},{},{},{},{},{});".format(request.form['temp_check'],tempMax,tempMin,request.form['humid_check'],humidMax,humidMin,request.form['pir_check'])
				cursor.execute(query)
				cnx.commit()
				cnx.close()
				print(cursor.rowcount, "record inserted.")
				return redirect(url_for('conf',path="alertas"))
			except Exception as e:
				print(e)
				return "",500


@socketio.on("connect")
def connected():
    """event listener when client connects to the server"""
    print(request.sid)
    print("client has connected")
    emit("connect")

@socketio.on('data')
def handle_message(data):
    """event listener when client types a message"""
    print("data from the front end: ",str(data))
    emit("data",{'data':data,'id':request.sid},broadcast=True)

@socketio.on('move')
def on_message(data):
    print('Movimento')
    back()

@socketio.on('status')
def on_message(data):
	print("recebi status",data["led"])
	global led
	led=data["led"]
	inject_load()
	turbo.push(turbo.update(render_template("leds.html"), 'ledss'))

    

@socketio.on("disconnect")
def disconnected():
    """event listener when client disconnects to the server"""
    print("user disconnected")
    emit("disconnect",f"user {request.sid} disconnected",broadcast=True)
@app.route('/favicon.ico')
def favicon():
    return url_for('static', filename='favicon.ico')


@app.errorhandler(404)
def page_not_found(e):
	return render_template("404.html")

@app.errorhandler(500)
def page_not_found(e):
	return render_template("500.html")

if __name__ == "__main__":
	#t1 = Thread(daemon=True,target=t).start()
	#subprocess.runrunrunrun(['sh', 'mqtt/teste.sh'])
	
	
	socketio.run(app,host='0.0.0.0',debug=True, use_reloader=True, use_debugger=False)
    
   


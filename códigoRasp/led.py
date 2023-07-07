from machine import Pin, Timer
import time
import sys
import dht
pir = Pin(19, Pin.IN,Pin.PULL_UP)
led=Pin(20,Pin.OUT)
sensor=dht.DHT11(Pin(14))
led.low()

time.sleep(1)

cont=0
while True:
    try:
        sensor.measure()
        if(cont%5==0):
            print("temp: {}\n humididade: {}".format(sensor.temperature(),sensor.humidity()))
        
        if(pir.value() == 1):
            led.high()
            time.sleep(1)
        else:
            led.low()
            time.sleep(1)
        cont+=1
    except OSError as e:
		print("Cant read:", e)
		sys.print_exception(e)
    

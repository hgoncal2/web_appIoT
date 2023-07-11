#!/bin/bash
python3 /mnt/c/Users/hugo2/Documents/webApp/web_appIoT/mqtt/mqtt_sub.py &
python3 /mnt/c/Users/hugo2/Documents/webApp/web_appIoT/mqtt/hello.py
kill $(ps aux | grep mqtt_sub.py | tr -s " " | cut -f2 -d" ")


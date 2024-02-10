#!/usr/bin/env python3

import random
from paho.mqtt import client as mqtt_client
import json
from pprint import pprint
import logging


broker = 'localhost'
port = 1883
topic = "zigbee2mqtt/#"
# Generate a Client ID with the subscribe prefix.
client_id = f'subscribe-{random.randint(0, 100)}'
# username = 'emqx'
# password = 'public'
sensor={}

def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    # client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

# {"level":"info",
#  "message":
#  "MQTT publish: topic 'zigbee2mqtt/0xa4c138d79ca59adc', 
#                 payload '{\"battery_state\":\"high\",\"humidity\":27,\"temperature\":25.9,\"temperature_unit\":\"celsius\"}'"
# }

def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        if ("zigbee2mqtt" in msg.payload.decode()):
          if ("bridge" not in msg.payload.decode()):
            try:  
              m=msg.payload.decode()
              arr=m.split("'")
              capt_id=arr[1].split("/")[1]
              sensors=arr[3].split(",")
              humidity=sensors[1].split(":")[1]
              temperature=sensors[2].split(":")[1]


            except: 
              pass

            try:
              oldvalue=sensor[capt_id]["temperature"]
            except:
              oldvalue=20.0

            if (abs(float(temperature) - float(oldvalue))>10.0):
              temperature=oldvalue

            sensor[capt_id]={"humidity":humidity,"temperature":temperature}
            print ("Sensor "+capt_id+" registered temperature of "+temperature+" and humidity of "+humidity)
          
          with open("/var/lib/prometheus/node-exporter/sonoff.prom","w") as f:
            f.write("#TYPE sonoff_humidity gauge\n")
            for capt_id in sensor:
                f.write ('sonoff_humidity{capteur="'+capt_id+'"} '+sensor[capt_id]["humidity"]+"\n")

            f.write("#TYPE sonoff_temperature gauge\n")
            for capt_id in sensor:
                f.write ('sonoff_temperature{capteur="'+capt_id+'"} '+sensor[capt_id]["temperature"]+"\n")
       
    client.subscribe(topic)
    client.on_message = on_message

def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()


if __name__ == '__main__':
    run()

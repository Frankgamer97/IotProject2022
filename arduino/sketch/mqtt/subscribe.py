import paho.mqtt.subscribe as subscribe
from flask import request
import ast

MQTT_SERVER = "broker.emqx.io"# "130.136.2.70"
MQTT_USERNAME = ""# "iot2020"
MQTT_PASSWORD = ""# "mqtt2020*"

MQTT_AUTH = {
    'username': MQTT_USERNAME, 
    'password': MQTT_PASSWORD
    }

MQTT_TOPICS = ["Iot/2022/Project/data"]
MQTT_QOS=1
# The callback for when a PUBLISH message is received from the server.
def msg(client, userdata, message):
    # print("%s %s" % (message.topic, message.payload))
    print("["+message.topic+"] new data received")


    try:
        res = ast.literal_eval(message.payload.decode())
        print()
        print()
        print(res)
        print()
        print()    
    except:
        print("ERRORE")


subscribe.callback(msg, MQTT_TOPICS, MQTT_QOS, hostname=MQTT_SERVER)
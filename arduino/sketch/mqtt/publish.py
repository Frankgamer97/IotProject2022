import paho.mqtt.publish as publish
from flask import jsonify

MQTT_SERVER = "broker.emqx.io"# "130.136.2.70"
MQTT_USERNAME = ""# "iot2020"
MQTT_PASSWORD = ""# "mqtt2020*"

MQTT_AUTH = {
    'username': MQTT_USERNAME, 
    'password': MQTT_PASSWORD
    }

MQTT_TOPIC = "Iot/2022/Project/data"
MQTT_QOS=1

ESP32_DATA = {'MAC': "100",
             'GPS': [100,11],
             'Timestamp': "100",
             'RSSI': "100",
            'Temperature': "100",
            'Humidity': "100",
            'Gas': "100",
            'AQI': "100"}
publish.single(MQTT_TOPIC, str(ESP32_DATA), qos=MQTT_QOS, hostname=MQTT_SERVER) #auth = MQTT_AUTH
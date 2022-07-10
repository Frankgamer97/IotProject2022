import paho.mqtt.publish as publish
from flask import jsonify

MQTT_SERVER = "broker.emqx.io"# "130.136.2.70"
MQTT_USERNAME = ""# "iot2020"
MQTT_PASSWORD = ""# "mqtt2020*"

MQTT_AUTH = {
    'username': MQTT_USERNAME, 
    'password': MQTT_PASSWORD
    }

MQTT_TOPIC = "Iot/2022/Project/config"
MQTT_QOS=1

ESP32_CONFIG = {'sample_frequency': "5000",
             'min_gas_value': "0",
             'max_gas_value': "100",
             'protocol': "2"
             }
publish.single(MQTT_TOPIC, str(ESP32_CONFIG), qos=MQTT_QOS, hostname=MQTT_SERVER) #auth = MQTT_AUTH
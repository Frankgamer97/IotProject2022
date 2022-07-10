import paho.mqtt.subscribe as subscribe

MQTT_SERVER = "broker.emqx.io"# "130.136.2.70"
MQTT_USERNAME = ""# "iot2020"
MQTT_PASSWORD = ""# "mqtt2020*"

MQTT_AUTH = {
    'username': MQTT_USERNAME, 
    'password': MQTT_PASSWORD
    }

MQTT_TOPICS = ["iotProject2022/temp","iotProject2022/hum"]
MQTT_QOS=1
# The callback for when a PUBLISH message is received from the server.
def msg(client, userdata, message):
    print("%s %s" % (message.topic, message.payload))



subscribe.callback(msg, MQTT_TOPICS, MQTT_QOS, hostname=MQTT_SERVER)
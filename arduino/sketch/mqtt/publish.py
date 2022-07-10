import paho.mqtt.publish as publish

MQTT_SERVER = "broker.emqx.io"# "130.136.2.70"
MQTT_USERNAME = ""# "iot2020"
MQTT_PASSWORD = ""# "mqtt2020*"

MQTT_AUTH = {
    'username': MQTT_USERNAME, 
    'password': MQTT_PASSWORD
    }

MQTT_TOPIC = "iotProject2022/config"
MQTT_QOS=1
publish.single(MQTT_TOPIC, "0001004694", qos=MQTT_QOS, hostname=MQTT_SERVER) #auth = MQTT_AUTH
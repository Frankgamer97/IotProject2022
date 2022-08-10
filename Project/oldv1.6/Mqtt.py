from threading import Thread
from paho.mqtt import publish, subscribe
import ast

from utility import SERVER_MEASUREMENTS
from utility import get_time, influxdb_post


class MqttHandler:
    list_values = None
    influxdb_post = None

    def __init__(self, list_values, server_name="broker.emqx.io", user ="", password ="", topics=["Iot/2022/Project/data", "Iot/2022/Project/config"], qos=1):
        self.server_name = server_name
        self.user = user
        self.password = password

        self.auth = {
            'username': self.user, 
            'password': self.password
            }


        self.topics = topics

        self.qos=qos # for publish & subscribe
        
        MqttHandler.list_values = list_values

        self.mqtt_thread = Thread(target=MqttHandler.bind_updating, args=(self,))
        self.mqtt_thread.daemon=True

        self.mqtt_thread.start()

    @staticmethod
    def bind_updating(mqtt_handler):
        print("[MQTT] Bind updates")
        subscribe.callback(MqttHandler.get_data, mqtt_handler.topics[0], mqtt_handler.qos, hostname=mqtt_handler.server_name)

    @staticmethod
    def get_data(client, userdata, message):

        print("[MQTT] DATA RECEIVED")

        try:
            json_data = ast.literal_eval(message.payload.decode()) 
            if len(MqttHandler.list_values) > SERVER_MEASUREMENTS:
                del MqttHandler.list_values[-1]

            json_data["Time"] = get_time()
            
            MqttHandler.list_values.insert(0,json_data) 
            # influxdb_post(json_data)
        except Exception as e:
            print("[MQTT] DATA ERROR")
            print()
            print(e)
            print()

    def update_config(self, params):
        print("[MQTT] update configs")
        publish.single(self.topics[1], str(params), qos=self.qos, hostname=self.server_name)

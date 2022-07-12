from threading import Thread
from paho.mqtt import publish, subscribe
import ast

class MqttHandler:
    list_values = None
    influxdb_post = None

    def __init__(self, list_values, influxdb_post, server_name="broker.emqx.io", user ="", password ="", topics=["Iot/2022/Project/data", "Iot/2022/Project/config"], qos=1):
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
        MqttHandler.influxdb_post = influxdb_post

        self.mqtt_thread = Thread(target=MqttHandler.bind_updating, args=(self,))

        self.mqtt_thread.start()


    # def subscribe_updates(self):
    #     print("[MQTT] BIND UPDATING")
    #     print(self.topics[0])
    #     print(self.qos)
    #     print(self.server_name)
    #     print()
    #     subscribe.callback(MqttHandler.get_data, self.topics[0], self.qos, hostname=self.server_name)

    @staticmethod
    def bind_updating(mqtt_handler):
        print("[MQTT] BIND UPDATING")
        print(mqtt_handler.topics[0])
        print(mqtt_handler.qos)
        print(mqtt_handler.server_name)
        print()        
        subscribe.callback(MqttHandler.get_data, mqtt_handler.topics[0], mqtt_handler.qos, hostname=mqtt_handler.server_name)

    @staticmethod
    def get_data(client, userdata, message):

        print("[MQTT] new data received")

        try:
            res = ast.literal_eval(message.payload.decode()) 

            MqttHandler.list_values.append(res) 
            # MqttHandler.influxdb_post(res)
        except Exception as e:
            print("ERRORE")
            print()
            print()
            print(e)
            print()
            print()

    def update_config(self, params):
        print("PUBLUSHING CONFIGS")
        publish.single(self.topics[1], str(params), qos=self.qos, hostname=self.server_name)
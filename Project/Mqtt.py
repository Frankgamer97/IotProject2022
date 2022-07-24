from datetime import datetime
from threading import Thread
from paho.mqtt import publish, subscribe
import ast

from utility import SERVER_MEASUREMENTS
from utility import get_time, get_device_time, get_ntp_time, getDeviceId, getConfig, setMac, updateConfigProtocol
from utility import current_protocol
from influxdb import influxdb_post

from DeviceStatHandler import DeviceStatHandler


class MqttHandler:
    list_values = None
    influxdb_post = None
    bot_handler = None
    aggr_handler = None

    def __init__(self, list_values, bot_handler, aggr_handler, server_name="broker.emqx.io", user ="", password ="", topics=["Iot/2022/Project/data", "Iot/2022/Project/config"], qos=1):
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

        MqttHandler.bot_handler = bot_handler

        MqttHandler.aggr_handler = aggr_handler
        self.mqtt_thread = Thread(target=MqttHandler.bind_updating, args=(self,))
        self.mqtt_thread.daemon=True

        self.mqtt_thread.start()

    @staticmethod
    def bind_updating(mqtt_handler):
        print("[MQTT] Bind updates")
        subscribe.callback(MqttHandler.get_data, mqtt_handler.topics[0], mqtt_handler.qos, hostname=mqtt_handler.server_name)

    @staticmethod
    def get_data(client, userdata, message):

        # global current_protocol

        print("[MQTT] DATA RECEIVED")

        try:
            json_data = ast.literal_eval(message.payload.decode())            

            sent_time = None
            recv_time = None
            packet_delay = 0
            
            try:
                sent_time = get_device_time(json_data["Time"])# datetime(year, month, day, hour, minute, second)
                recv_time = get_ntp_time()
            except:
                print("[WARNING] NTP SERVER NO RESPONSE")
                
                if recv_time is None:
                    recv_time = datetime.now()
                if sent_time is None:
                    sent_time = recv_time

            # sent_time = get_device_time(json_data["Time"])
            # recv_time = get_ntp_time()
            # packet_delay = (recv_time - sent_time).seconds

            json_data["Delay"] = packet_delay
            json_data["PDR"] = MqttHandler.aggr_handler.get_packet_delivery_ratio(json_data["C_Protocol"])
            json_data["Time"] = get_time()

            getConfig(json_data["IP"])
            json_data["DeviceId"] = getDeviceId(json_data["IP"])
            setMac(json_data["IP"], json_data["MAC"])

            current_protocol["current_protocol"] = json_data["C_Protocol"]
            updateConfigProtocol(json_data["IP"], json_data["C_Protocol"])

            if len(MqttHandler.list_values) > SERVER_MEASUREMENTS:
                del MqttHandler.list_values[-1]

            MqttHandler.list_values.insert(0,json_data)
            MqttHandler.aggr_handler.update_pandas()

            MqttHandler.bot_handler.telegram_updates()
            # influxdb_post(json_data)
        except Exception as e:
            print("[MQTT] DATA ERROR")
            print()
            print(e)
            print()

    def update_config(self, params):
        print("[MQTT] UPDATE CONFIGS")
        # config = getConfig(request.remote_addr)
        
        publish.single(self.topics[1], str(params), qos=self.qos, hostname=self.server_name)

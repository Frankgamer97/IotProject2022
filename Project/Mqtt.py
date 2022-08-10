from datetime import datetime
from threading import Thread
from paho.mqtt import publish, subscribe

from utility import current_protocol, influx_parameters

from utility import get_time, get_device_time, get_ntp_time, getDeviceId, getConfig, setMac
from utility import updateConfigProtocol, updateProxyData, updateGps
from influxdb import send_influxdb

import ast

class MqttHandler:
    arima_handler = None
    bot_handler = None
    aggr_handler = None

    server_name="broker.emqx.io"
    user = ""
    password = ""
    auth = {
            'username': user, 
            'password': password
    }

    topics=["Iot/2022/Project/data", "Iot/2022/Project/config"]
    qos = 1

    def __init__(self, bot_handler, arima_handler ,aggr_handler):
        
        MqttHandler.bot_handler = bot_handler
        MqttHandler.arima_handler = arima_handler
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
        print("[MQTT] DATA RECEIVED")

        try:
            json_data = ast.literal_eval(message.payload.decode())            

            sent_time = None
            recv_time = None
            packet_delay = 0
            
            try:
                # datetime(year, month, day, hour, minute, second)
                sent_time = get_device_time(json_data["Time"])
                recv_time = get_ntp_time()
                packet_delay = (recv_time - sent_time).total_seconds()
            except:
                print("[WARNING] NTP SERVER NO RESPONSE")
                 
            json_data["Delay"] = packet_delay
            # json_data["PDR"] = MqttHandler.aggr_handler.get_packet_delivery_ratio(json_data["C_Protocol"])
            json_data["Time"] = get_time()

            getConfig(json_data["IP"])
            json_data["DeviceId"] = getDeviceId(json_data["IP"])
            setMac(json_data["IP"], json_data["MAC"])
            
            json_data["GPS"] = [ round(x,3) for x in json_data["GPS"]]
            updateGps(json_data["DeviceId"], json_data["GPS"])

            current_protocol["current_protocol"] = json_data["C_Protocol"]
            updateConfigProtocol(json_data["IP"], json_data["C_Protocol"])

            updateProxyData(json_data)
            MqttHandler.aggr_handler.update_pandas()

            send_influxdb(json_data, measurement = influx_parameters["measurement"])
            MqttHandler.arima_handler.arima_updates()
            MqttHandler.bot_handler.telegram_updates()

        except Exception as e:
            print("[MQTT] DATA ERROR")
            print()
            print(e)
            print()

    def update_config(self, params):
        print("[MQTT] UPDATE CONFIGS")        
        publish.single(MqttHandler.topics[1], str(params), qos=MqttHandler.qos, hostname=MqttHandler.server_name)
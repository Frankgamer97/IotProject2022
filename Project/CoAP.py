from threading import Thread
from datetime import datetime
from aiocoap import Message, Context, resource, CHANGED


from utility import current_protocol, influx_parameters
from utility import get_time, get_device_time, get_ntp_time, getDeviceId, getConfig, setMac
from utility import updateProxyData, updateConfigProtocol, get_IP
from influxdb import send_influxdb

import asyncio
import ast

class CoapServer(resource.Resource):

    def __init__(self, bot_handler, arima_handler, aggr_handler):
        super(CoapServer, self).__init__()
        self.bot_handler = bot_handler
        self.arima_handler = arima_handler
        self.aggr_handler = aggr_handler

    async def render_put(self, request):
        print("[COAP] PUT REQUEST RECEIVED: ")
        try:
            json_data = request.payload.decode()
            json_data = ast.literal_eval(json_data)  

            sent_time = None
            recv_time = None
            packet_delay = 0
            
            try:
                # datetime(year, month, day, hour, minute, second)
                sent_time = get_device_time(json_data["Time"])
                recv_time = get_ntp_time()
            except:
                print("[WARNING] NTP SERVER NO RESPONSE")
                
                if recv_time is None:
                    recv_time = datetime.now()
                if sent_time is None:
                    sent_time = recv_time

            current_protocol["current_protocol"]= json_data["C_Protocol"]
            updateConfigProtocol(json_data["IP"], json_data["C_Protocol"])
            
            json_data["Delay"] = packet_delay
            json_data["PDR"] = self.aggr_handler.get_packet_delivery_ratio(json_data["C_Protocol"])

            json_data["Time"] = get_time()
            getConfig(json_data["IP"])
            json_data["DeviceId"] = getDeviceId(json_data["IP"])
            setMac(json_data["IP"], json_data["MAC"])

            updateProxyData(json_data)
            self.aggr_handler.update_pandas()

            send_influxdb(json_data, measurement = influx_parameters["measurement"])
            self.arima_handler.arima_updates()
            self.bot_handler.telegram_updates()

        except Exception as e:
            print("[COAP] PUT REQUEST ERROR")
            print()
            print(e)
            print()

        return Message(code = CHANGED)

class CoapHandler:
    SERVER_IP = None
    SERVER_PORT = 5683
    SERVER_UPDATE_API = "update"

    bot_handler = None
    arima_handler = None
    aggr_handler = None

    def __init__(self, bot_handler, arima_handler, aggr_handler):
        CoapHandler.SERVER_IP = get_IP()
        
        CoapHandler.bot_handler = bot_handler
        CoapHandler.arima_handler = arima_handler
        CoapHandler.aggr_handler = aggr_handler
        
        self.coap_thread = Thread(target=CoapHandler.setup_coap, args=(self,))
        self.coap_thread.daemon=True
        self.coap_thread.start()

    @staticmethod
    def start_coap(self, event_loop):
        root = resource.Site()
        root.add_resource([CoapHandler.SERVER_UPDATE_API], CoapServer(CoapHandler.bot_handler, CoapHandler.arima_handler, CoapHandler.aggr_handler))
        
        context = Context.create_server_context(site=root, bind=(CoapHandler.SERVER_IP, CoapHandler.SERVER_PORT))
        asyncio.Task(context)

        print("[COAP] Server running on (%s, %s)..."%(CoapHandler.SERVER_IP, CoapHandler.SERVER_PORT))
        event_loop.run_forever()
        
    @staticmethod
    def setup_coap(self):
        event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(event_loop)
        CoapHandler.start_coap(self, event_loop)
import asyncio
from asyncore import loop
import aiocoap.resource as resource
import aiocoap
import ast
from threading import Thread
from utility import SERVER_MEASUREMENTS
from utility import get_time, get_device_time, get_ntp_time
from influxdb import influxdb_post
from datetime import datetime
from DeviceStatHandler import DeviceStatHandler

class CoapServer(resource.Resource):

    def __init__(self, list_values, bot_handler, aggr_handler):
        super(CoapServer, self).__init__()
        self.list_values = list_values
        self.startMeasurements = None
        self.bot_handler = bot_handler
        self.aggr_handler = aggr_handler
    # async def render_get(self, request):
    #     print("[COAP] GET REQUEST RECEIVED: ")

    #     res = None

    #     if len(self.list_values) > 0:
    #         res = str(self.list_values[0]).encode("utf-8")
    #     else:
    #         res=b"{}"

    #     return aiocoap.Message(code= aiocoap.CONTENT, observe=0, payload=res)

    
    async def render_put(self, request):
        print("[COAP] PUT REQUEST RECEIVED: ")
        try:
            json_data = request.payload.decode()
            json_data = ast.literal_eval(json_data)  

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
            json_data["PDR"] = self.aggr_handler.get_packet_delivery_ratio(json_data["C_Protocol"])

            json_data["Time"] = get_time()
            
            if len(self.list_values) == SERVER_MEASUREMENTS:
                del self.list_values[-1]

            self.list_values.insert(0, json_data)
            self.aggr_handler.update_pandas()
            self.bot_handler.telegram_updates()
            # influxdb_post(json_data)
        except Exception as e:
            print("[COAP] PUT REQUEST ERROR")
            print()
            print(e)
            print()

        return aiocoap.Message(code= aiocoap.CHANGED)



class CoapHandler:
    def __init__(self, list_values, bot_handler, aggr_handler, SERVER_IP="192.168.1.", SERVER_PORT=5683, UPDATE_API="update"):

        self.SERVER_IP=SERVER_IP
        self.SERVER_PORT=SERVER_PORT
        self.UPDATE_API = UPDATE_API
        self.list_values = list_values
        self.bot_handler = bot_handler
        self.aggr_handler = aggr_handler
        
        self.coap_thread = Thread(target=CoapHandler.setup_coap, args=(self,))
        self.coap_thread.daemon=True

        self.coap_thread.start()

    
    @staticmethod
    def start_coap(self, event_loop):
        root = resource.Site()
        root.add_resource([self.UPDATE_API], CoapServer(self.list_values, self.bot_handler, self.aggr_handler))
        
        context = aiocoap.Context.create_server_context(site=root, bind=(self.SERVER_IP, self.SERVER_PORT))
        asyncio.Task(context)

        print("[COAP] Server running on (%s, %s)..."%(self.SERVER_IP, self.SERVER_PORT))
        event_loop.run_forever()
        
        
    @staticmethod
    def setup_coap(self):

        event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(event_loop)
        
        # asyncio.run(CoapHandler.start_coap(self))
        CoapHandler.start_coap(self, event_loop)
        

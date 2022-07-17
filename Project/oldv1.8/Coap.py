import asyncio
from asyncore import loop
from Mqtt import MqttHandler
import aiocoap.resource as resource
import aiocoap
import ast
from threading import Thread
from utility import SERVER_MEASUREMENTS
from utility import get_time
from influxdb import influxdb_post

class CoapServer(resource.Resource):

    def __init__(self, list_values):
        super(CoapServer, self).__init__()
        self.list_values = list_values

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
            json_data["Time"] = get_time()
            
            if len(self.list_values) == SERVER_MEASUREMENTS:
                del self.list_values[-1]

            self.list_values.insert(0, json_data)
        
            # influxdb_post(json_data)
        except Exception as e:
            print("[COAP] PUT REQUEST ERROR")
            print()
            print(e)
            print()

        return aiocoap.Message(code= aiocoap.CHANGED)



class CoapHandler:
    def __init__(self, list_values, SERVER_IP="192.168.1.12", SERVER_PORT=5683, UPDATE_API="update"):

        self.SERVER_IP=SERVER_IP
        self.SERVER_PORT=SERVER_PORT
        self.UPDATE_API = UPDATE_API
        self.list_values = list_values
        
        self.coap_thread = Thread(target=CoapHandler.setup_coap, args=(self,))
        self.coap_thread.daemon=True

        self.coap_thread.start()

    
    @staticmethod
    def start_coap(self, event_loop):
        root = resource.Site()
        root.add_resource([self.UPDATE_API], CoapServer(self.list_values))
        
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
        

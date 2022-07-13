import asyncio
import aiocoap.resource as resource
import aiocoap
import logging

SERVER_IP="192.168.1.30"
SERVER_PORT=5683

class Hello(resource.ObservableResource):

    def __init__(self):
        super(Hello, self).__init__()
        self.mydata=b"0"

    async def render_get(self, request):
        print("[COAP] GET REQUEST RECEIVED: ")
        return aiocoap.Message(code= aiocoap.CONTENT, observe=0, payload=self.mydata)

    async def render_post(self, request):
        print("[COAP] POST REQUEST RECEIVED: ")
        
        try:
            self.mydata = request.payload
            print("mydata = ", request.payload)
        
        except Exception as e:
            print("[COAP] POST REQUEST ERROR")

        self.updated_state()
        return aiocoap.Message(code= aiocoap.CHANGED)
def main():
    # Resource tree creation
    root = resource.Site()
    root.add_resource(['hello'], Hello())
    
    context = aiocoap.Context.create_server_context(site=root, bind=(SERVER_IP, SERVER_PORT))

    asyncio.Task(context)

    print("Server is running on (%s, %s)..."%(SERVER_IP, SERVER_PORT))
    asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    asyncio.run(main())
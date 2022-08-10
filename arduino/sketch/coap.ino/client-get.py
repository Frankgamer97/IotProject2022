import logging
import asyncio
from aiocoap import  *

logging.basicConfig(level=logging.INFO)

def observation_callback(response):
    res = response.payload.decode()
    print("Other results:", res)


def error_callback(exception):
    print("[COAP] CALBBACK ERROR")
    print()
    print()
    print(exception)
    print()
    print()
@asyncio.coroutine
def coap_observer():

    context = yield from Context.create_client_context()

    # payload = b"NEW HELLO"

    try:
        request = Message(code=GET, observe=0, uri="coap://192.168.1.30:5683/hello")

        protocol_request = context.request(request)
        protocol_request.observation.register_callback(observation_callback)
        protocol_request.observation.register_errback(error_callback)
        response = yield from protocol_request.response

        print('First result: %s\n%r'%(response.code, response.payload))

    except ValueError as e:
        print(e)

    
if __name__ == "__main__":
    event_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(event_loop)
    event_loop.create_task(coap_observer())
    asyncio.get_event_loop().run_forever()
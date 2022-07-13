import logging
import asyncio
from aiocoap import  *


stop=2
my_request = None
def cancel_observation():
    pass    

def manage_response(content, type_res=1):
    if type_res == 0:
        print("FIRST: ", content)
    else:
        print("UPDATE: ", content)

def observe_handle(response):
    if response.code.is_successful():
        print("UPDATING: ", response.payload)
    else:
        print('Error code %s' % response.code)


async def main():
 
    protocol = await Context.create_client_context()
    request = Message(code=GET)
    request.set_request_uri("coap://192.168.1.30/hello")
    request.opt.observe = 0
    observation_is_over = asyncio.Future()
    try:
        requester = protocol.request(request)
        requester.observation.register_callback(observe_handle)
        response = await requester.response
        

        manage_response(response.payload, type_res=0);

        exit_reason = await observation_is_over
        print('Observation is over: %r' % exit_reason)
    finally:
        print("HEREEEEEEEEEEEEEEEEE")
        if not requester.response.done():
            requester.response.cancel()
        if not requester.observation.cancelled:
            requester.observation.cancel()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
import logging
import asyncio
from aiocoap import  *
from threading import Thread
from time import sleep

stop=5


async def cancel_observation():
 
    protocol = await Context.create_client_context()
    request = Message(code=GET)
    request.set_request_uri("coap://192.168.1.30/hello")
    request.opt.observe = 1
    try:
        requester = protocol.request(request)
        #requester.observation.register_callback(cancel_observation_callback)
        response = await requester.response
        print("OBSERVING DEACTIVATED")
    except:
        print("ERROREEEEEEEEEE")

def cancel_observation_request(args):
    sleep(args)

    print("HEHHHH")
        
    loop = asyncio.new_event_loop()

    asyncio.set_event_loop(loop)
    
    print("HEHEHEH")
    loop.run_until_complete(cancel_observation())
    # asyncio.get_event_loop().call_later(args, cancel_observation)

def manage_response(content, type_res=1):
    global stop

    if stop == 0:
        print("BASTAAAAAAAAAA")
        # cancel_observation()
    else:
        

        # if type_res == 0:
        #     print("FIRST: ", content)
        # else:
        #     print("UPDATE: ", content)

        print("",stop," -> UPDATE: ", content)

        stop = stop -1
        # if stop == 0:
        #     asyncio.get_event_loop().run_until_complete(cancel_observation())
            

def observe_handle(response):
    if response.code.is_successful():
        manage_response(response.payload, 1)
    else:
        print('Error code %s' % response.code)


async def loop():
    global stop

    while stop > 0:
        pass
async def main():
 
    global stop
    protocol = await Context.create_client_context()
    request = Message(code=GET)
    request.set_request_uri("coap://192.168.1.30/hello")
    request.opt.observe = 0
    observation_is_over = asyncio.Future()
    try:
        requester = protocol.request(request)
        requester.observation.register_callback(observe_handle)
        response = await requester.response
        
       
        manage_response(response.payload, type_res=0)

        # print("QUI")
        exit_reason = await observation_is_over
        # await loop()
        # print('Observation is over: %r' % exit_reason)
        print("FINE")
    finally:
        print("HEREEEEEEEEEEEEEEEEE")
        if not requester.response.done():
            requester.response.cancel()
        if not requester.observation.cancelled:
            requester.observation.cancel()

if __name__ == "__main__":
    thread = Thread(target = cancel_observation_request, args=(30,))
    thread.daemon = True
    thread.start()
    asyncio.get_event_loop().run_until_complete(main())
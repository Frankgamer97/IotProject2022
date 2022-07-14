import logging
import asyncio
import sys

from aiocoap import *

logging.basicConfig(level=logging.INFO)

ESP32_DATA = {'MAC': "100",
             'GPS': [100,11],
             'Timestamp': "100",
             'RSSI': "100",
            'Temperature': "100",
            'Humidity': "100",
            'Gas': "100",
            'AQI': "100"
            }

async def main():

    context = await Context.create_client_context()

    await asyncio.sleep(2)

    # payload = b"NEW HELLO"

    try:
        request = Message(code=PUT, payload = str(ESP32_DATA).encode("utf-8"), uri="coap://192.168.1.30:5683/update")
        response = await context.request(request).response
        print('Result: %s\n%r'%(response.code, response.payload))

    except ValueError as e:
        print(e)

    
if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
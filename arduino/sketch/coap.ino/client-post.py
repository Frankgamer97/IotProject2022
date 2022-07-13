import logging
import asyncio
import sys

from aiocoap import *

logging.basicConfig(level=logging.INFO)

async def main():

    context = await Context.create_client_context()

    await asyncio.sleep(2)

    # payload = b"NEW HELLO"

    try:
        request = Message(code=POST, payload = sys.argv[1].encode("utf-8"), uri="coap://192.168.1.30:5683/hello")
        response = await context.request(request).response
        print('Result: %s\n%r'%(response.code, response.payload))

    except ValueError as e:
        print(e)

    
if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
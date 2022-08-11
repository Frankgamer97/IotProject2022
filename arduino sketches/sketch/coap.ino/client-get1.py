import logging
import asyncio

from aiocoap import *

logging.basicConfig(level=logging.INFO)

async def main():
    protocol = await Context.create_client_context()

    request = Message(code=GET, uri="coap://192.168.1.30:5683/hello", observe=0)

    pr = protocol.request(request)

    r = await pr.response
    print("First response: %s\n%r"%(r, r.payload))

    async for r in pr.observation:
        print("Next result: %s\n%r"%(r, r.payload))

        pr.observation.cancel()
        break
    print("Loop ended, sticking around")
    await asyncio.sleep(50)

if __name__ == "__main__":
    asyncio.run(main())
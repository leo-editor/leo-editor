#@+leo-ver=5-thin
#@+node:ekr.20210202110241.1: * @file leoclient.py
"""An example client for leoserver.py."""
import asyncio
import json
import random
import websockets
from leo.core import leoGlobals as g

wsHost = "localhost"
wsPort = 32125

async def asyncInterval(timeout):
    tag = 'client'
    uri = f"ws://{wsHost}:{wsPort}"
    async with websockets.connect(uri) as websocket:
        print(f"{tag}: asyncInterval.timeout: {timeout}")
        n = 0
        while True:
            n += 1
            try:
                await asyncio.sleep(timeout)
                action = "shut_down" if n == 6 else "error" if n == 5 else "set_trace" if n == 1 else "test"
                package = {
                    "id": n,
                    "action": action,
                    "package": {
                        "ap": "1",
                        "random": random.randrange(1, 1000)
                    }
                }
                print(f"{tag}: send {package.get('action')}")
                request = json.dumps(package, separators=(',', ':'))
                await websocket.send(request)
                response = g.toUnicode(await websocket.recv())
                print(f"{tag}: got: {response}")
            except websockets.exceptions.ConnectionClosedError as e:
                print(f"{tag}: connection closed: {e}")
                break
            except websockets.exceptions.ConnectionClosed:
                print(f"{tag}: connection closed normally")
                break
loop = asyncio.get_event_loop()
loop.run_until_complete(asyncInterval(2))
loop.run_forever()
#@-leo

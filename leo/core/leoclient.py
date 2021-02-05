#@+leo-ver=5-thin
#@+node:ekr.20210202110241.1: * @file leoclient.py
"""An example client for leoserver.py."""
import asyncio
import json
import random
import unittest
import websockets
from leo.core import leoGlobals as g

wsHost = "localhost"
wsPort = 32125
tag = 'client'

trace = True
action_dict = {1: "set_trace", 5: "error", 6: "shut_down"}

async def main_loop(timeout):
    uri = f"ws://{wsHost}:{wsPort}"
    async with websockets.connect(uri) as websocket:
        if trace: print(f"{tag}: asyncInterval.timeout: {timeout}")
        n = 0
        while True:
            n += 1
            try:
                await asyncio.sleep(timeout)
                package = {
                    "id": n,
                    "action": action_dict.get(n, "test"),
                    "package": {
                        "ap": "1",
                        "random": random.randrange(1, 1000)
                    }
                }
                if trace: print(f"{tag}: send {package.get('action')}")
                request = json.dumps(package, separators=(',', ':'))
                await websocket.send(request)
                response = g.toUnicode(await websocket.recv())
                if trace: print(f"{tag}: got: {response}")
            except websockets.exceptions.ConnectionClosedError as e:
                print(f"{tag}: connection closed: {e}")
                break
            except websockets.exceptions.ConnectionClosed:
                print(f"{tag}: connection closed normally")
                break

loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(main_loop(2))
    loop.run_forever()
except KeyboardInterrupt:
    # This terminates the server abnormally.
    print(f"{tag}: Keyboard interrupt")
    
if __name__ == '__main__':
    unittest.main()

#@-leo

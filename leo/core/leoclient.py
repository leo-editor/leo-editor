#@+leo-ver=5-thin
#@+node:ekr.20210202110241.1: * @file leoclient.py
"""An example client for leoserver.py."""
import asyncio
import json
import websockets
from leo.core import leoGlobals as g

wsHost = "localhost"
wsPort = 32125

async def asyncInterval(timeout):
    uri = f"ws://{wsHost}:{wsPort}"
    async with websockets.connect(uri) as websocket:
        print('asyncInterval.timeout', timeout)
        n = 0
        while True:
            n += 1
            await asyncio.sleep(timeout)
            # "param" is the p_package arg to leoCommand in leoserver.py.
            p_package = { "action": "test", "param": {"n":n, "node": 1}, "id":n}
            request = json.dumps(p_package, separators=(',', ':'))
            await websocket.send(request)
            response = await websocket.recv()
            print('got', g.toUnicode(response))
            
loop = asyncio.get_event_loop()
loop.run_until_complete(asyncInterval(5))
loop.run_forever()
#@-leo

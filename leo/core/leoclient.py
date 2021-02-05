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
timeout = 0.1

#@+others
#@+node:ekr.20210205141432.1: ** function: main
def main():
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main_loop(timeout))
        ### loop.run_forever()
    except KeyboardInterrupt:
        # This terminates the server abnormally.
        print(f"{tag}: Keyboard interrupt")
#@+node:ekr.20210205144500.1: ** function: main_loop
async def main_loop(timeout):
    uri = f"ws://{wsHost}:{wsPort}"
    action_dict = {1: "set_trace", 5: "error", 100: "shut_down"}
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
                if trace: print(f"{tag}: send: {package.get('action')}")
                request = json.dumps(package, separators=(',', ':'))
                await websocket.send(request)
                response = g.toUnicode(await websocket.recv())
                if trace: print(f"{tag}:  got: {response}")
            except websockets.exceptions.ConnectionClosedError as e:
                print(f"{tag}: connection closed: {e}")
                break
            except websockets.exceptions.ConnectionClosed:
                print(f"{tag}: connection closed normally")
                break
#@+node:ekr.20210205143347.1: ** function: test_main_loop
async def test_main_loop():
    uri = f"ws://{wsHost}:{wsPort}"
    action_dict = {1: "set_trace", 5: "error"} ### 6: "shut_down"}
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
                if trace: print(f"{tag}: send: {package.get('action')}")
                request = json.dumps(package, separators=(',', ':'))
                await websocket.send(request)
                response = g.toUnicode(await websocket.recv())
                if trace: print(f"{tag}:  got: {response}")
            except websockets.exceptions.ConnectionClosedError as e:
                print(f"{tag}: connection closed: {e}")
                break
            except websockets.exceptions.ConnectionClosed:
                print(f"{tag}: connection closed normally")
                break
        print('==== end of test_main_loop')
#@+node:ekr.20210205141510.1: ** class TestServer(unittest.TestCase)
class TestServer(unittest.TestCase):
    """Unit tests for leoserver.py"""
    #@+others
    #@+node:ekr.20210205144929.1: *3* test.setupClass & tearDownClass
    @classmethod
    def setUpClass(cls):
        g.trace('=====')
        loop = asyncio.get_event_loop()
        loop.run_until_complete(test_main_loop())
        ### loop.run_forever()
        
    @classmethod
    def tearDownClass(cls):
        loop = asyncio.get_event_loop()
        g.trace('===== before stop')
        loop.stop()
        g.trace('===== after stop') ### Never shows up.
    #@+node:ekr.20210205142756.1: *3* test.test_shut_down
    def test_shut_down(self):
        g.trace('=====')
    #@-others
#@-others

if __name__ == '__main__':
    # unittest.main()
    main()
#@-leo

#@+leo-ver=5-thin
#@+node:ekr.20210202110241.1: * @file leoclient.py
"""An example client for leoserver.py."""
import asyncio
import json
import random
import time
import unittest
import websockets
from leo.core import leoGlobals as g

wsHost = "localhost"
wsPort = 32125

tag = 'client'
trace = True
trace_response = True
timeout = 0.1  # Without some wait everything happens too quickly to test.

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
    # action_dict = {1: "set_trace", 5: "error", 100: "shut_down"}
    times_d = {}  # Keys are n, values are time sent.
    async with websockets.connect(uri) as websocket:
        if trace: print(f"{tag}: asyncInterval.timeout: {timeout}")
        n = 0
        while True:
            n += 1
            try:
                await asyncio.sleep(timeout)
                # action = 'test'
                action = "set_trace" if n == 1 else input(f"{n:3} enter action: ")
                package = {
                    "id": n,
                    "action": action or "test",  ### action_dict.get(n, "test"),
                    "package": {
                        "ap": "1",
                        "random": random.randrange(1, 1000)
                    }
                }
                if trace: print(f"{tag}: send: {package.get('action')}")
                request = json.dumps(package, separators=(',', ':'))
                times_d [n] = time.process_time()
                await websocket.send(request)
                json_s = g.toUnicode(await websocket.recv())
                if trace_response:
                    response_d = json.loads(json_s)
                    print(f"{tag}:  got: {json_s}")
                    id_ = response_d.get("id")
                    t2 = time.process_time()
                    t1 = None if id_ is None else times_d.get(id_)
                    response_time = '???' if t1 is None else f"{(t2 -t1):4.4}"
                    print(f"{tag}: id: {id_} response time: {response_time}")
            except websockets.exceptions.ConnectionClosedError as e:
                print(f"{tag}: connection closed: {e}")
                break
            except websockets.exceptions.ConnectionClosed:
                print(f"{tag}: connection closed normally")
                break
#@+node:ekr.20210205143347.1: ** function: test_main_loop
async def test_main_loop():
    uri = f"ws://{wsHost}:{wsPort}"
    # action_dict = {1: "set_trace", 5: "error", 6: "shut_down"}
    async with websockets.connect(uri) as websocket:
        if trace: print(f"{tag}: asyncInterval.timeout: {timeout}")
        n = 0
        while True:
            n += 1
            try:
                await asyncio.sleep(timeout)
                action = "set_trace" if n == 1 else input(f"{n:3} enter action: ")
                package = {
                    "id": n,
                    "action": action or "test",
                    "package": {
                        "ap": "1",
                        "random": random.randrange(1, 1000)
                    }
                }
                if trace or action == "set_trace": print(f"{tag}: send: {package.get('action')}")
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
        g.trace('===== before')
        loop = asyncio.get_event_loop()
        loop.run_until_complete(test_main_loop())
        g.trace('===== after')  ### We never get here!
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

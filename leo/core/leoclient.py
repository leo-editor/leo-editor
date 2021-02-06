#@+leo-ver=5-thin
#@+node:ekr.20210202110241.1: * @file leoclient.py
"""An example client for leoserver.py."""
import asyncio
import json
import random
import socket
import time
import unittest
import websockets
from leo.core import leoGlobals as g

wsHost = "localhost"
wsPort = 32125

tag = 'client'
trace = True
timeout = 0.1
sync = False

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
    action_dict = {1: "set_trace", 5: "error", 20: "shut_down"}
    times_d = {}  # Keys are n, values are time sent.
    tot_response_time = 0.0
    n_known_response_times = 0
    async with websockets.connect(uri) as websocket:
        if trace: print(f"{tag}: asyncInterval.timeout: {timeout}")
        n = 0
        while True:
            n += 1
            try:
                times_d [n] = time.perf_counter()
                if 0:
                    action = "set_trace" if n == 1 else input(f"{n:3} enter action: ")
                else:
                    await asyncio.sleep(timeout)
                    action = action_dict.get(n)
                package = {
                    "id": n,
                    "action": action or "test",
                    "package": {
                        "ap": "1",
                        "random": random.randrange(1, 1000)
                    }
                }
                if trace: print(f"{tag}: send: id: {n} action: {package.get('action')}")
                request = json.dumps(package, separators=(',', ':'))
                await websocket.send(request)
                json_s = g.toUnicode(await websocket.recv())
                response_d = json.loads(json_s)
                # Calculate response time.
                n2 = response_d.get("id")
                t1 = times_d.get(n2)
                t2 = time.perf_counter()
                if t1 is None or n2 is None:
                    response_time_s = '???'
                else:
                    response_time = t2 - t1
                    tot_response_time += response_time
                    n_known_response_times += 1
                    response_time_s = f"{response_time:4.3}"
                if trace:
                    print(f"{tag}:  got: {response_d} response time: {response_time_s}")
            except websockets.exceptions.ConnectionClosedError as e:
                print(f"{tag}: connection closed: {e}")
                break
            except websockets.exceptions.ConnectionClosed:
                print(f"{tag}: connection closed normally")
                break
        if trace:
            print(f"Average response_time: {(tot_response_time/n_known_response_times):6.3}")
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
#@+node:ekr.20210205181835.1: ** function: sync_main (client)
def sync_main():
    tag = 'client'
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_:
        socket_.connect((wsHost, wsPort))
        print(f"{tag}: {wsHost} {wsPort}")
        n = 0
        while n < 20:
            n += 1
            message = bytes(f"message {n}", encoding='utf-8')
            socket_.sendall(message)
            data = socket_.recv(1024)
            g.trace(f"{tag}: got: {g.toUnicode(data)}")
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
    if sync:
        sync_main()
    else:
        main()
#@-leo

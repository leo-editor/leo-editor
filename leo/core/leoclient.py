#@+leo-ver=5-thin
#@+node:ekr.20210202110241.1: * @file leoclient.py
"""An example client for leoserver.py."""
import asyncio
import json
import time
import websockets
from leo.core import leoGlobals as g

wsHost = "localhost"
wsPort = 32125

n_known_response_times = 0
n_unknown_response_times = 0
n_unexpected_responses = 0
sync = False
tag = 'client'
timeout = 0.1
times_d = {}  # Keys are n, values are time sent.
tot_response_time = 0.0

#@+others
#@+node:ekr.20210205141432.1: ** function: main
def main():
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(client_main_loop(timeout))
    except KeyboardInterrupt:
        # This terminates the server abnormally.
        print(f"{tag}: Keyboard interrupt")
#@+node:ekr.20210205144500.1: ** function: client_main_loop & helpers
async def client_main_loop(timeout):
    trace = True
    uri = f"ws://{wsHost}:{wsPort}"
    #@+<< define action_list >>
    #@+node:ekr.20210206075253.1: *3* << define action_list >>
    root_ap = {
        'childIndex': 0,
        'gnx': 0,
        'stack': [],
    }

    # In effect, these are unit tests.
    action_list = [
        ("set_trace", {}),
        ("get_sign_on", {}),
        ("apply_config", {"config": {"whatever": True}}),
        ("error", {}),
        ("open_file", {"filename": __file__}),
        ("contract-all", {}),  # Execute contract-all command by name.
        ("collapse_node", {"ap": root_ap}),
        ("close_file", {"filename": __file__}),
        ("get_all_commands", {}),
        ("test", {}),
    ]
    #@-<< define action_list >>
    async with websockets.connect(uri) as websocket:
        if trace: print(f"{tag}: asyncInterval.timeout: {timeout}")
        # Await the startup package.
        json_s = g.toUnicode(await websocket.recv())
        response_d = json.loads(json_s)
        print(f"startup package: {response_d}")
        n = 0
        while True:
            n += 1
            try:
                times_d [n] = time.perf_counter()
                await asyncio.sleep(timeout)
                if n < len(action_list):
                    aTuple  = action_list[n-1]
                    action, package = aTuple
                else:
                    action, package = "shut_down", {}
                request_package = {
                    "id": n,
                    "action": action,
                    "package": package,
                }
                if trace:
                    print(f"{tag}: send: id: {n} package: {request_package}")
                # Wait for response n.
                while True:
                    request = json.dumps(request_package, separators=(',', ':'))
                    await websocket.send(request)
                    json_s = g.toUnicode(await websocket.recv())
                    response_d = json.loads(json_s)
                    # Check the response.
                    n2 = response_d.get("id")
                    # Check the response. This completes the unit tests.
                    _check_response(action, n, response_d)
                    if trace:
                        _show_response(json_s, n, response_d)
                    if n2 == n:
                        break
                    print(f"{tag}: response out of order. Expected {n}, got {n2}")
            except websockets.exceptions.ConnectionClosedError as e:
                print(f"{tag}: connection closed: {e}")
                break
            except websockets.exceptions.ConnectionClosed:
                print(f"{tag}: connection closed normally")
                break
        print(f"Unexpected response keys: {n_unexpected_responses}")
        print(f"  Unknown response times: {n_unknown_response_times}")
        print(f"    Known response times: {n_known_response_times}")
        print(f"   Average response_time: {(tot_response_time/n_known_response_times):3.2} sec.")
            # About 0.1, regardless of tracing.
#@+node:ekr.20210206093130.1: *3* function: _show_response
def _show_response(json_s, n, response_d):
    global n_known_response_times
    global n_unknown_response_times
    global times_d
    global tot_response_time 
    # Calculate response time.
    t1 = times_d.get(n)
    t2 = time.perf_counter()
    if t1 is None or n is None:
        response_time_s = '???'
        n_unknown_response_times += 1
    else:
        response_time = t2 - t1
        tot_response_time += response_time
        n_known_response_times += 1
        response_time_s = f"{response_time:3.2}"
    # Note: g.printObj converts multi-line strings to lists.
    # repr(response_d) shows newlines as "\n", not actual newlines.
    action = response_d.get('action')
    assert action, response_d
    if action == 'open_file':
        g.printObj(response_d,
            tag=f"{tag}: got: open-file response time: {response_time_s}")
    elif action == 'get_all_commands':
        commands = response_d.get('commands')
        print(f"{tag}: got: get_all_commands {len(commands)}")
    else:
        print(f"{tag}:  got: {response_d}")
#@+node:ekr.20210206144703.1: *3* function: _check_response
def _check_response(expected_action, n, response_d):
    """
    Warn if the response is unexpected.
    This completes the unit test.
    """
    global n_unexpected_responses
    d, tag = response_d, '_check_response'
    keys = sorted(list(d.keys()))
    if 'action' not in response_d:
        n_unexpected_responses += 1
        print(f"{tag}: no 'action' key response keys: {keys}")
        return
    action = response_d.get('action')
    if action != expected_action:
        n_unexpected_responses += 1
        print(f"{tag}: action value: {action} is not {expected_action}: {keys}")
#@-others

if __name__ == '__main__':
    main()
#@-leo

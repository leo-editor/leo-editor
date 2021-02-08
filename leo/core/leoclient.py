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
n_async_responses = 0
n_known_response_times = 0
n_unknown_response_times = 0

async def client_main_loop(timeout):
    global n_async_responses
    trace = False
    uri = f"ws://{wsHost}:{wsPort}"
    action_list = _get_action_list()
    async with websockets.connect(uri) as websocket:
        if trace: print(f"{tag}: asyncInterval.timeout: {timeout}")
        # Await the startup package.
        json_s = g.toUnicode(await websocket.recv())
        d = json.loads(json_s)
        if trace:
            print(f"startup package: {d}")
        n = 0
        while True:
            n += 1
            try:
                times_d [n] = time.perf_counter()
                await asyncio.sleep(timeout)
                # Get the next package. The last action is shut_down.
                action, package  = action_list[n-1]
                request_package = {
                    "id": n,
                    "action": action,
                    "package": package,
                }
                if trace:
                    print(f"{tag}: send: id: {n} package: {request_package}")
                # Send the next request.
                request = json.dumps(request_package, separators=(',', ':'))
                await websocket.send(request)
                # Wait for response n.
                inner_n = 0
                while True:
                    inner_n += 1
                    assert inner_n < 50  # Arbitrary.
                    try:
                        json_s = None
                        json_s = g.toUnicode(await websocket.recv())
                        d = json.loads(json_s)
                    except Exception:
                        if json_s is not None:
                            g.trace('json_s', json_s)
                            g.print_exception()
                        break  # Probably the end of the server.
                    _show_response(n, d, trace)  # Always calculate stats.
                    # The loop invariant. No recovery is possible.
                    action2, n2 = d.get("action"), d.get("id")
                    assert not action2 or (action, n) == (action2, n2), (
                        action, action2, n, n2)
                    if 'async' in d:
                        n_async_responses += 1
                    else:
                        break
                # Something is drastically wrong if these fail.
               
            except websockets.exceptions.ConnectionClosedError as e:
                print(f"{tag}: connection closed: {e}")
                break
            except websockets.exceptions.ConnectionClosed:
                print(f"{tag}: connection closed normally")
                break
        print(f"Asynchronous responses: {n_async_responses}")
        print(f"Unknown response times: {n_unknown_response_times}")
        print(f"  Known response times: {n_known_response_times}")
        print(f" Average response_time: {(tot_response_time/n_known_response_times):3.2} sec.")
            # About 0.1, regardless of tracing.
#@+node:ekr.20210206093130.1: *3* function: _show_response
def _show_response(n, d, trace):
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
    if not trace:
        return
    action = d.get('action')
    if action == 'open_file':
        g.printObj(d,
            tag=f"{tag}: got: open-file response time: {response_time_s}")
    elif action == 'get_all_commands':
        commands = d.get('commands')
        print(f"{tag}: got: get_all_commands {len(commands)}")
    else:
        print(f"{tag}: got: {d}")
#@+node:ekr.20210206075253.1: *3* function: _get_action_list
def _get_action_list():
    """
    Return all callable public methods of the server.
    In effect, these are unit tests.
    """
    import inspect
    import leoserver
    trace = False
    server = leoserver.ServerController()
    root_gnx = 'ekr.20210202110241.1'  # The  gnx of this file's root node.
    root_ap = {
        'childIndex': 0,
        'gnx': root_gnx, 
        'stack': [],
    }
    exclude_names = [
        'clear_trace',  # Unwanted.
        'delete_node', 'cut_node',  # dangerous.
        'click_button', 'get_buttons', 'remove_button',  # Require plugins.
    ]
    head = [
        ("set_trace", {}),
        ("get_sign_on", {}),
        ("apply_config", {"config": {"whatever": True}}),
        ("error", {}),
        ("test", {}),
        ("open_file", {"filename": __file__}),
    ]
    head_names = [name for (name, package) in head]
    tail = [
        ("get_body_length", {"ap": root_ap}),
        ("get_body_using_gnx", {"gnx": root_gnx}),
        ("get_body_using_p", {"ap": root_ap}),
        ("contract-all", {}),  # Execute contract-all command by name.
        ("insert_node", {"ap": root_ap, "headline": "inserted headline"}),
        ("collapse_node", {"ap": root_ap}),
        ("close_file", {"filename": __file__}),
        ("get_all_commands", {}),
        ("shut_down", {}),
    ]
    tail_names = [name for (name, package) in tail]
    #
    # Add all remaining methods to the middle.
    tests = inspect.getmembers(server, inspect.ismethod)
    test_names = sorted([name for (name, value) in tests if not name.startswith('_')])
    middle = [(z, {"ap": root_ap}) for z in test_names
        if z not in head_names + tail_names + exclude_names]
    if trace:
        middle_names = [name for (name, package) in middle]
        g.printObj(middle_names, tag='middle_names')
    all_tests = head + middle + tail
    all_names = sorted([name for (name, package) in all_tests])
    if trace:
        g.printObj(all_names, tag='all_names')
    return all_tests
    
#@-others

if __name__ == '__main__':
    main()
#@-leo

#@+leo-ver=5-thin
#@+node:ekr.20210202110241.1: * @file leoclient.py
"""
An example client for leoserver.py, based on work by Félix Malboeuf. Used by permission.
"""
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
#@+node:ekr.20210205144500.1: ** function: client_main_loop
n_async_responses = 0
n_known_response_times = 0
n_unknown_response_times = 0

async def client_main_loop(timeout):
    global n_async_responses
    trace = True
    verbose = False
    uri = f"ws://{wsHost}:{wsPort}"
    action_list = _get_action_list()
    async with websockets.connect(uri) as websocket:
        if trace and verbose:
            print(f"{tag}: asyncInterval.timeout: {timeout}")
        # Await the startup package.
        json_s = g.toUnicode(await websocket.recv())
        d = json.loads(json_s)
        if trace and verbose:
            print(f"startup package: {d}")
        n = 0
        while True:
            n += 1
            try:
                times_d [n] = time.perf_counter()
                await asyncio.sleep(timeout)
                # Get the next package. The last action is shut_down.
                try:
                    action, package  = action_list[n-1]
                except IndexError:
                    break
                request_package = {
                    "id": n,
                    "action": action,
                    "package": package,
                }
                if trace and verbose:
                    print(f"{tag}: send: id: {n} package: {request_package}")
                # Send the next request.
                request = json.dumps(request_package, separators=(',', ':'))
                await websocket.send(request)
                # Wait for response to request n.
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
                        break
                    _show_response(n, d, trace, verbose)
                    # This loop invariant guarantees we receive messages in order. 
                    is_async = "async" in d
                    action2, n2 = d.get("action"), d.get("id")
                    assert is_async or (action, n) == (action2, n2), (action, n, d)
                    if is_async:
                        n_async_responses += 1
                    else:
                        break
            except websockets.exceptions.ConnectionClosedError as e:
                print(f"{tag}: connection closed: {e}")
                break
            except websockets.exceptions.ConnectionClosed:
                print(f"{tag}: connection closed normally")
                break
            except Exception as e:
                print('')
                print(f"{tag}: internal client error {e}")
                print(f"{tag}: request_package: {request_package}")
                g.print_exception()
                print('')
        print(f"Asynchronous responses: {n_async_responses}")
        print(f"Unknown response times: {n_unknown_response_times}")
        print(f"  Known response times: {n_known_response_times}")
        print(f" Average response_time: {(tot_response_time/n_known_response_times):3.2} sec.")
            # About 0.1, regardless of tracing.
#@+node:ekr.20210206093130.1: ** function: _show_response
def _show_response(n, d, trace, verbose):
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
    if not trace and not verbose:
        return
    action = d.get('action')
    if not verbose:
        if "async" in d:
            print(f"{tag}: async: {d.get('s')}")
        else:
            print(f"{tag}:   got: {n} {action}")
        return
    if action == 'open_file':
        g.printObj(d,
            tag=f"{tag}: got: open-file response time: {response_time_s}")
    elif action == 'get_all_commands':
        commands = d.get('commands')
        print(f"{tag}: got: get_all_commands {len(commands)}")
    else:
        print(f"{tag}: got: {d}")
#@+node:ekr.20210206075253.1: ** function: _get_action_list
def _get_action_list():
    """
    Return all callable public methods of the server.
    In effect, these are unit tests.
    """
    import inspect
    import leoserver
    server = leoserver.LeoServer()
    file_name = "xyzzy.leo"
    exclude_names = [
        # Dangerous at present.
        'delete_node', 'cut_node', 'save_file',
        # Require plugins.
        'click_button', 'get_buttons', 'remove_button',
        # Not ready yet.
        'set_selection',
    ]
    head = [
        ("get_sign_on", {}),
        ("apply_config", {"config": {"whatever": True}}),
        ("echo", {"echo": True}),
        ("error", {}),
        # ("bad_server_command", {}),
        ("open_file", {"filename": file_name, "echo": True}),
    ]
    head_names = [name for (name, package) in head]
    tail = [
        ("get_body_length", {}),
        ("set_body", {"body": "new body"}),
        ("set_headline", {"headline": "new headline"}),
        ("execute-leo-command", {"leo-command-name": "contract-all"}),
        ("insert_node", {"headline": "inserted headline"}),
        ("contract_node", {}),
        ("close_file", {"filename": file_name}),
        ("get_all_leo_commands", {"trace": True, "verbose": False}),
        ("get_all_server_commands", {"trace": True, "verbose": False}),
        ("shut_down", {}),
    ]
    tail_names = [name for (name, package) in tail]
    # Add all remaining methods to the middle.
    tests = inspect.getmembers(server, inspect.ismethod)
    test_names = sorted([name for (name, value) in tests if not name.startswith('_')])
    middle = [(z, {}) for z in test_names
        if z not in head_names + tail_names + exclude_names]
    middle_names = [name for (name, package) in middle]
    all_tests = head + middle + tail
    if 0:
        g.printObj(middle_names, tag='middle_names')
        all_names = sorted([name for (name, package) in all_tests])
        g.printObj(all_names, tag='all_names')
    return all_tests
    
#@-others

if __name__ == '__main__':
    main()
#@-leo

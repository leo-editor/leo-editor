# @+leo-ver=5-thin
# @+node:ekr.20210202110241.1: * @file leoclient.py
"""
An example client for leoserver.py, based on work by Félix Malboeuf. Used by permission.

First start the server in one console: `python -m leo.core.leoserver --password test`.
Then start the client in another console: `python -m leo.core.leoclient`.

This client runs the commands given in the `_get_action_list` function.
The last command ends both the client and the server.
"""

import asyncio
import json
import time
import hashlib
import hmac

# Third party.
import websockets
from leo.core import leoGlobals as g
from leo.core import leoserver

wsHost = "localhost"
wsPort = 32125
password = 'test'  # Must match the server's password.

tag = 'client'

# Tracing.
trace = True
verbose = False
timeout = 0.1
times_d: dict[int, float] = {}  # Keys are n, values are time sent.
tot_response_time = 0.0
n_async_responses = 0
n_known_response_times = 0
n_unknown_response_times = 0


# @+others
# @+node:ekr.20210219105145.1: ** function: _dump_outline
def _dump_outline(c):  # pragma: no cover
    """Dump the outline."""
    print(f"_dump_outline: {c.shortFileName()}...\n")
    for p in c.all_positions():
        level_s = ' ' * 2 * p.level()
        print(f"{level_s}{p.childIndex():2} {p.v.gnx} {p.h}")
    print('')


# @+node:ekr.20210206075253.1: ** function: _get_action_list
def _get_action_list():
    """
    Return all callable public methods of the server.
    In effect, these are unit tests.
    """
    import inspect
    import os

    server = leoserver.LeoServer(silent=True)
    # file_name = "xyzzy.leo"
    file_name = g.finalize_join(g.app.loadDir, '..', 'test', 'test.leo')
    assert os.path.exists(file_name), repr(file_name)
    log = False
    exclude_names = [
        # Find methods...
        'replace_all',
        'replace_then_find',
        'clone_find_all',
        'clone_find_all_flattened',
        'clone_find_tag',
        'find_all',
        'find_def',
        'find_next',
        'find_previous',
        'find_var',
        'tag_children',
        # Other methods
        'set_body',
        'error',
        'replace',
        'delete_node',
        'cut_node',  # dangerous.
        'click_button',
        'get_buttons',
        'remove_button',  # Require plugins.
        'save_file',  # way too dangerous!
        # 'set_selection',  # Not ready yet.
        'open_file',
        'close_file',  # Done by hand.
        'import_any_file',
        'insert_child_named_node',
        'insert_named_node',
        'set_ask_result',
        'set_opened_file',
        'set_search_settings',
        'set_selection',
        'shut_down',  # Don't shut down the server.
    ]
    head = [
        # ("apply_config", {"config": {"whatever": True}}),
        ("!error", {}),
        # ("bad_server_command", {}),
        ("!open_file", {"filename": file_name, "log": log}),
    ]
    head_names = [name for (name, package) in head]
    tail = [
        # ("get_body_length", {}),  # All responses now contain len(p.b).
        ("!find_all", {"find_text": "def"}),
        ("!get_ua", {"log": log}),
        ("!get_parent", {"log": log}),
        ("!get_children", {"log": log}),
        ("!set_body", {"body": "new body"}),
        ("!set_headline", {"name": "new headline", 'gnx': "ekr.20061008140603"}),
        ("contractAllHeadlines", {}),  # normal leo command
        ("!insert_node", {}),
        ("!contract_node", {}),
        (
            "!close_file",
            {"forced": True},
        ),  # forced flag set to true because it was modified
        ("!get_all_leo_commands", {}),
        ("!get_all_server_commands", {}),
        ("!shut_down", {}),
    ]
    tail_names = [name for (name, package) in tail]

    # Add all remaining methods to the middle.
    tests = inspect.getmembers(server, inspect.ismethod)
    test_names = sorted([name for (name, value) in tests if not name.startswith('_')])
    middle: list = [
        ("!" + z, {}) for z in test_names if z not in head_names + tail_names + exclude_names
    ]
    middle_names = [name for (name, package) in middle]  # type:ignore
    all_tests = head + middle + tail  # type:ignore
    if 0:
        g.printObj(middle_names, tag='middle_names')
        all_names = sorted([name for (name, package) in all_tests])
        g.printObj(all_names, tag='all_names')
    return all_tests


# @+node:ekr.20210206093130.1: ** function: _show_response
def _show_response(n, d):
    global n_known_response_times
    global n_unknown_response_times
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
    if not verbose:
        return
    print(f"id: {d.get('id', '---'):3} d: {sorted(d)}")
    if action == 'open_file':
        g.printObj(d, tag=f"{tag}: got: open-file response time: {response_time_s}")
    elif action == 'get_all_commands':
        commands = d.get('commands')
        print(f"{tag}: got: get_all_commands {len(commands)}")
    else:
        print(f"{tag}: got: {d}")


# @+node:ekr.20210205144500.1: ** function: client_main_loop
async def client_main_loop(timeout):
    global n_async_responses
    uri = f"ws://{wsHost}:{wsPort}"
    action_list = _get_action_list()
    print("leoserver must be started with argument --password test ", flush=True)
    async with websockets.connect(uri) as websocket:
        if trace:
            print(f"{tag}: asyncInterval.timeout: {timeout}")

        # React to the server's challenge for authentication.
        parsedData = json.loads(g.toUnicode(await websocket.recv()))
        if trace:
            print(f"{tag}: got: {parsedData}")
        if parsedData.get("action") == "challenge":
            challenge = parsedData.get("challenge")
            expected_hash = hmac.new(
                password.encode(), challenge.encode(), hashlib.sha256
            ).hexdigest()
            await websocket.send(json.dumps({"action": "!auth", "response": expected_hash}))
            if trace:
                print(f"{tag}: sent authentication response")
        else:
            print(f"{tag}: expected challenge, got: {parsedData}")
            return

        # Await the startup package.
        json_s = g.toUnicode(await websocket.recv())
        d = json.loads(json_s)
        if trace:
            print(f"startup package: {d}")
        n = 0
        while True:
            n += 1
            try:
                times_d[n] = time.perf_counter()
                await asyncio.sleep(timeout)
                # Get the next package. The last action is shut_down.
                try:
                    action, param = action_list[n - 1]
                except IndexError:
                    break
                request_package = {
                    "id": n,
                    "action": action,
                    "param": param,
                }
                if trace:
                    print(f"{tag}: send: id: {n:4} {action:>40} {param}")
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
                    _show_response(n, d)
                    # This loop invariant guarantees we receive messages in order.
                    is_async = "async" in d
                    n2 = d.get("id")
                    assert is_async or n == n2, (action, n, d)
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
        print(
            f" Average response_time: {(tot_response_time / n_known_response_times):3.2} sec."
        )  # About 0.1, regardless of tracing.


# @+node:ekr.20210205141432.1: ** function: main (leoclient.py)
def main():
    try:
        asyncio.run(client_main_loop(timeout))  # #4664
    except KeyboardInterrupt:
        # This terminates the server abnormally.
        print(f"{tag}: Keyboard interrupt")
    except ConnectionRefusedError:
        print(f"{tag}: No server running")
    except asyncio.CancelledError:
        print(f"{tag}: Cancelled")
    except OSError:
        print(f"{tag}: No server running")
    except Exception as e:
        print(f"{tag}: Unexpected exception: {e}")


# @-others

if __name__ == '__main__':
    main()
# @-leo

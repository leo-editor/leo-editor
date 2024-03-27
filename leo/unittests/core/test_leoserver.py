#@+leo-ver=5-thin
#@+node:ekr.20210820203000.1: * @file ../unittests/core/test_leoserver.py
"""Tests of leoserver.py"""

import json
import os
import leo.core.leoserver as leoserver
from leo.core.leoTest2 import LeoUnitTest

# Globals.
g = None
g_leoserver = None
g_server = None

#@+others
#@+node:ekr.20210901070918.1: ** class TestLeoServer(LeoUnitTest)
class TestLeoServer(LeoUnitTest):
    """Tests of LeoServer class."""
    request_number = 0
    #@+others
    #@+node:felix.20210621233316.99: *3* TestLeoServer: Setup and TearDown
    @classmethod
    def setUpClass(cls):
        global g, g_leoserver, g_server
        g_leoserver = leoserver
        g_server = leoserver.LeoServer(testing=True)
        g = g_server.g
        assert g

    @classmethod
    def tearDownClass(cls):
        global g_leoserver, g_server
        try:
            g_server.shut_down({})
            print('===== server did not terminate properly ====')  # pragma:no cover
        except g_leoserver.TerminateServer:
            pass
        except leoserver.ServerError:  # pragma:no cover
            pass

    def setUp(self):
        global g_server
        self.server = g_server
        g.unitTesting = True

    def tearDown(self):
        g.unitTesting = False

    #@+node:felix.20210621233316.100: *3* TestLeoServer._request
    def _request(self, action, param=None):
        server = self.server
        self.request_number += 1
        log_flag = param.get("log")
        # Direct server commands require an exclamation mark '!' prefix
        # to distinguish them from Leo's commander's own methods.
        d = {
            "action": action,
            "id": self.request_number
        }
        if param:
            d["param"] = param
        response = server._do_message(d)
        # _make_response calls json_dumps. Undo it with json.loads.
        answer = json.loads(response)
        if log_flag:
            g.printObj(answer, tag=f"response to {action!r}")  # pragma: no cover
        return answer
    #@+node:felix.20210621233316.102: *3* TestLeoServer.test_most_public_server_methods
    def test_most_public_server_methods(self):
        server = self.server
        tag = 'test_most_public_server_methods'
        assert isinstance(server, g_leoserver.LeoServer), self.server
        test_dot_leo = g.finalize_join(g.app.loadDir, '..', 'test', 'test.leo')
        assert os.path.exists(test_dot_leo), repr(test_dot_leo)
        # Remove all uA's.
        methods = server._get_all_server_commands()
        # Ensure that some methods happen at the end.
        for z in ('toggle_mark', 'undo', 'redo'):
            methods.remove(z)
        for z in ('toggle_mark', 'toggle_mark', 'undo', 'redo'):
            methods.append(z)
        # g.printObj(methods, tag=methods)
        exclude = [
            # Find methods...
            'change_all', 'change_then_find',
            'clone_find_all', 'clone_find_all_flattened', 'clone_find_tag',
            'find_all', 'find_def', 'find_next', 'find_previous', 'find_var',
            'goto_script',
            'tag_children',
            # Other methods
            'finishCreate',
            'remove_tag', 'tag_node',
            'delete_node', 'cut_node',  # dangerous.
            'click_button', 'get_buttons', 'remove_button',  # Require plugins.
            'paste_node', 'paste_as_clone_node',  # New exclusion.
            'paste_as_template',  # New exclusion.
            'save_file',  # way too dangerous!
            # 'set_selection',  # Not ready yet.
            'open_file', 'close_file',  # Done by hand.
            'import_any_file',
            'insert_child_named_node',
            'insert_named_node',
            'set_ask_result',
            'set_opened_file',
            'set_search_settings',
            'shut_down',  # Don't shut down the server.
        ]
        expected = ['error']
        param_d = {
            # "remove_tag": {"tag": "testTag"},
            # "tag_node": {"tag": "testTag"},
            # "apply_config": {"config": {"whatever": True}},
            "get_focus": {"log": False},
            "set_body": {"body": "new body\n", 'gnx': "ekr.20061008140603"},
            "set_headline": {"name": "new headline"},
            "get_all_server_commands": {"log": False},
            "get_all_leo_commands": {"log": False},
            # "paste_node": {"name", "paste-node-name"},
            # "paste_as_clone_node": {"name", "paste-node-name"},
        }
        # First open a test file & perform all tests.
        server.open_file({"filename": test_dot_leo})  # A real file.
        # Remove all uA's that can't be serialized.
        file_c = g.openWithFileName(test_dot_leo)
        for p in file_c.all_positions():
            try:
                json.dumps(p.u, skipkeys=True)
            except TypeError:
                p.u = None
        try:
            id_ = 0
            for method_name in methods:
                id_ += 1
                if method_name not in exclude:
                    assert getattr(server, method_name), method_name
                    param = param_d.get(method_name, {})
                    message = {
                        "id": id_,
                        "action": "!" + method_name,
                        "param": param,
                    }
                    try:
                        # Don't call the method directly.
                        # That would disable trace/verbose logic, checking, etc.
                        server._do_message(message)
                    except Exception as e:
                        if method_name not in expected:
                            print(f"Exception in {tag}: {method_name!r} {e}")  # pragma:no cover
        finally:
            server.close_file({"forced": True})
    #@+node:felix.20210621233316.103: *3* TestLeoServer.test_open_and_close
    def test_open_and_close(self):
        # server = self.server
        test_dot_leo = g.finalize_join(g.app.loadDir, '..', 'test', 'test.leo')
        assert os.path.exists(test_dot_leo), repr(test_dot_leo)
        log = False
        table = [
            # Open file.
            ("!open_file", {"log": log, "filename": "xyzzy.leo"}),  # Does not exist.
            # Switch to the second file.
            ("!open_file", {"log": log, "filename": test_dot_leo}),  # Does exist.
            # Open again. This should be valid.
            ("!open_file", {"log": False, "filename": test_dot_leo}),
            # Better test of _ap_to_p.
            ("!set_current_position", {
                "ap": {
                    "gnx": "ekr.20180311131424.1",  # Recent
                    "childIndex": 1,
                    "stack": [],
                }
            }),
            ("!get_ua", {"log": log}),
            # Close the second file.
            ("!close_file", {"log": log, "forced": True}),
            # Close the first file.
            ("!close_file", {"log": log, "forced": True}),
        ]
        for action, package in table:
            self._request(action, package)
    #@+node:felix.20210621233316.104: *3* TestLeoServer.test_find_commands
    def test_find_commands(self):

        tag = 'test_find_commands'
        test_dot_leo = g.finalize_join(g.app.loadDir, '..', 'test', 'test.leo')
        assert os.path.exists(test_dot_leo), repr(test_dot_leo)
        log = False
        # Open the file & create the StringFindTabManager.
        self._request("!open_file", {"log": False, "filename": test_dot_leo})
        #
        # Batch find commands: The answer is a count of found nodes.
        for method in ('!find_all', '!clone_find_all', '!clone_find_all_flattened'):
            answer = self._request(method, {"log": log, "find_text": "def"})
            if log:
                g.printObj(answer, tag=f"{tag}:{method}: answer")  # pragma: no cover
        #
        # Find commands that may select text: The answer is (p, pos, newpos).
        for method in ('!find_next', '!find_previous', '!find_def', '!find_var'):
            answer = self._request(method, {"log": log, "find_text": "def"})
            if log:
                g.printObj(answer, tag=f"{tag}:{method}: answer")  # pragma: no cover
        #
        # Change commands: The answer is a count of changed nodes.
        for method in ('!replace_all', '!replace_then_find'):
            answer = self._request(method, {"log": log, "find_text": "def", "change_text": "DEF"})
            if log:
                g.printObj(answer, tag=f"{tag}:{method}: answer")  # pragma: no cover
        #
        # Tag commands. Why they are in leoFind.py??
        for method in ('!clone_find_tag', '!tag_children'):
            answer = self._request(method, {"log": log, "tag": "my-tag"})
            if log:
                g.printObj(answer, tag=f"{tag}:{method}: answer")  # pragma: no cover

    #@-others
#@-others

#@-leo

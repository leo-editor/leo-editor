#@+leo-ver=5-thin
#@+node:ekr.20210202110128.1: * @file leoserver.py
#@@language python
#@@tabwidth -4
"""
Leo's internet server.

Based on Félix Malboeuf's leobridgeserver.py. Used by permission.
"""
#@+<< imports >>
#@+node:ekr.20210202110128.2: ** << imports >>
import asyncio
import getopt
import inspect
import json
import os
import sys
import time
import unittest
# Third-party.
import websockets
# Leo
from leo.core.leoNodes import Position
from leo.core.leoGui import StringFindTabManager
#@-<< imports >>
# pylint: disable=raise-missing-from
g = None  # The bridge's leoGlobals module. Unit tests use self.g.
# For unit tests.
g_leoserver = None
g_server = None
# Server defaults...
wsHost = "localhost"
wsPort = 32125

#@+others
#@+node:ekr.20210204054519.1: ** Exception classes
class InternalServerError(Exception):  # pragma: no cover
    """The server violated its own coding conventions."""
    pass

class ServerError(Exception):  # pragma: no cover
    """The server received an erroneous package."""
    pass

class TerminateServer(Exception):  # pragma: no cover
    """Ask the server to terminate."""
    pass
#@+node:ekr.20210202110128.29: ** class LeoServer
class LeoServer:
    """Leo Server Controller"""
    #@+others
    #@+node:ekr.20210202110128.30: *3* server.__init__ (load bridge)
    def __init__(self, testing=False):

        import leo.core.leoApp as leoApp
        import leo.core.leoBridge as leoBridge
        import leo.core.leoExternalFiles as leoExternalFiles
        global g
        t1 = time.process_time()
        #
        # Init ivars first.
        self.c = None  # Currently Selected Commander.
        self.dummy_c = None  # Set below, after we set g.
        self.action = None
        self.bad_commands_list = []  # Set below.
        self.config = None
        self.current_id = 0  # Id of action being processed.
        self.log_flag = False  # set by "log" key
        #
        # Start the bridge.
        self.bridge = leoBridge.controller(
            gui='nullGui',
            loadPlugins=False,   # True: attempt to load plugins.
            readSettings=False,  # True: read standard settings files.
            silent=True,         # True: don't print signon messages.
            verbose=False,       # True: prints messages that would be sent to the log pane.
        )
        self.g = g = self.bridge.globals()
        self.dummy_c = g.app.newCommander(fileName=None)  # To inspect commands
        self.bad_commands_list = self._bad_commands(self.dummy_c)
        #
        # Complete the initialization, as in LeoApp.initApp.
        g.app.idleTimeManager = leoApp.IdleTimeManager()
        g.app.idleTimeManager.start()
        g.app.externalFilesController = leoExternalFiles.ExternalFilesController(None)
        t2 = time.process_time()
        print(f"LeoServer: init leoBridge in {t2-t1:4.2} sec.")
    #@+node:ekr.20210211084004.1: *3* server:public commands
    #@+node:ekr.20210202193709.1: *4* server:button commands
    # These will fail unless the open_file inits c.theScriptingController.
    #@+node:ekr.20210207051720.1: *5* _check_button_command
    def _check_button_command(self, tag):  # pragma: no cover (no scripting controller)
        """
        Check that a button command is possible.
        Raise ServerError if not. Otherwise, return sc.buttonsDict.
        """
        c = self._check_c()
        sc = getattr(c, "theScriptingController", None)
        if not sc:
            # This will happen unless mod_scripting is loaded!
            raise ServerError(f"{tag}: no scripting controller")
        return sc.buttonsDict
    #@+node:ekr.20210202183724.4: *5* server.click_button
    def click_button(self, package):  # pragma: no cover (no scripting controller)
        """Handles buttons clicked in client from the '@button' panel"""
        tag = 'click_button'
        name = package.get("name")
        if not name:
            raise ServerError(f"{tag}: no button name given")
        d = self._check_button_command(tag)
        button = d.get(name)
        if not button:
            raise ServerError(f"{tag}: button {name!r} does not exist")
        try:
            button.command()
        except Exception as e:
            raise ServerError(f"{tag}: exception clicking button {name}: {e}")
        return self._make_response()
    #@+node:ekr.20210202183724.2: *5* server.get_buttons
    def get_buttons(self, package):  # pragma: no cover (no scripting controller)
        """Gets the currently opened file's @buttons list"""
        d = self._check_button_command('get_buttons')
        return self._make_response({
            "buttons": sorted(list(d.get.keys()))
        })
    #@+node:ekr.20210202183724.3: *5* server.remove_button
    def remove_button(self, package):  # pragma: no cover (no scripting controller)
        """Remove button by name."""
        tag = 'remove_button'
        name = package.get("name")
        if not name:
            raise ServerError(f"{tag}: no button name given")
        d = self._check_button_command(tag)
        if name not in d:
            raise ServerError(f"{tag}: button {name!r} does not exist")
        try:
            del d [name]
        except Exception as e:
            raise ServerError(f"{tag}: exception removing button {name}: {e}")
        return self._make_response({
            "buttons": sorted(list(d.get.keys()))
        })
    #@+node:ekr.20210202193642.1: *4* server:file commands
    #@+node:ekr.20210202110128.57: *5* server.open_file
    def open_file(self, package):
        """
        Open a leo file with the given filename.
        Create a new document if no name.
        """
        found, tag = False, 'open_file'
        filename = package.get('filename')  # Optional.
        if filename:
            for c in g.app.commanders():
                if c.fileName() == filename:
                    found = True
        if not found:
            c = self.bridge.openLeoFile(filename)
            c.findCommands.ftm = StringFindTabManager(c)
        if not c:  # pragma: no cover
            raise ServerError(f"{tag}: bridge did not open {filename!r}")
        if not c.frame.body.wrapper:  # pragma: no cover
            raise ServerError(f"{tag}: no wrapper")
        # Assign self.c
        self.c = c
        c.selectPosition(c.rootPosition())  # Required.
        # Check the outline!
        self._check_outline(c)
        if self.log_flag:  # pragma: no cover
            self._dump_outline(c)
        return self._make_response()
    #@+node:ekr.20210202110128.58: *5* server.close_file
    def close_file(self, package):
        """Closes an outline opened with open_file."""
        c = self._check_c()
        # Close the outline, even if it is dirty!
        c.clearChanged()
        c.close()
        # Select the first open outline, if any.
        commanders = g.app.commanders()
        self.c = commanders and commanders[0] or None
        # Return a response describing self.c, not the closed outline.
        return self._make_response()
    #@+node:ekr.20210202183724.1: *5* server.save_file
    def save_file(self, package):  # pragma: no cover (too dangerous).
        """Save the leo outline."""
        c = self._check_c()
        c.save()
        return self._make_response()
    #@+node:ekr.20210212092848.1: *4* server:find commands
    #@+node:ekr.20210212094817.1: *5* server._get_find_settings
    def _get_find_settings(self, c):
        """Return a g.Bunch containing the present find settings settings."""
        return c.findCommands.ftm.get_settings()
        ###
            # # For now, return EKR defaults.
            # return g.Bunch(
                # find_text=None, change_text=None,
                # search_body=True, search_headline=True,
                # ignore_case=True, pattern_match=False, whole_word=True,
                # mark_changes=False, mark_finds=False,
                # node_only=False, suboutline_only=False,
                # entry_focus=None,
            # )  
    #@+node:ekr.20210212092854.1: *5* server.find_all
    def find_all(self, package):
        """Run Leo's find-all command and return results."""
        tag = 'find_all'
        c = self._check_c()
        fc = c.findCommands
        find_text = package.get("find_text")
        if find_text is None:  # pragma: no cover
            raise ServerError(f"{tag}: no find pattern")
        settings = self._get_find_settings(c)
        settings.find_text = find_text
        if self.log_flag:  # pragma: no cover
            g.printObj(settings, tag=f"{tag}: settings for {c.shortFileName()}")
        answer = fc.do_find_all(settings)
        if self.log_flag:  # pragma: no cover
            g.printObj(answer, tag=f"{tag}: answer")
        return self._make_response({"answer": answer})
    #@+node:ekr.20210221042145.1: *5* server.change_all
    def change_all(self, package):
        """Run Leo's change-all command and return results."""
        tag = 'change_all'
        c = self._check_c()
        fc = c.findCommands
        find_text = package.get("find_text")
        if find_text is None:  # pragma: no cover
            raise ServerError(f"{tag}: no find pattern")
        change_text = package.get("change_text")
        if change_text is None:  # pragma: no cover
            raise ServerError(f"{tag}: no change text")
        settings = self._get_find_settings(c)
        settings.find_text = find_text
        settings.change_text = change_text
        if self.log_flag:  # pragma: no cover
            g.printObj(settings, tag=f"{tag}: settings for {c.shortFileName()}")
        answer = fc.do_change_all(settings)
        if self.log_flag:  # pragma: no cover
            g.printObj(answer, tag=f"{tag}: answer")
        return self._make_response({"answer": answer})
    #@+node:ekr.20210221042406.1: *5* server.change_then_find
    def change_then_find(self, package):
        """Run Leo's change-then-find command and return results."""
        tag = 'change_then_find'
        c = self._check_c()
        fc = c.findCommands
        find_text = package.get("find_text")
        if find_text is None:  # pragma: no cover
            raise ServerError(f"{tag}: no find pattern")
        settings = self._get_find_settings(c)
        settings.find_text = find_text
        if self.log_flag:  # pragma: no cover
            g.printObj(settings, tag=f"{tag}: settings for {c.shortFileName()}")
        answer = fc.do_change_then_find(settings)
        if self.log_flag:  # pragma: no cover
            g.printObj(answer, tag=f"{tag}: answer")
        return self._make_response({"answer": answer})
    #@+node:ekr.20210221042541.1: *5* server.clone_find_all
    def clone_find_all(self, package):
        """Run Leo's clone-find-all command and return results."""
        tag = 'clone_find_all'
        c = self._check_c()
        fc = c.findCommands
        find_text = package.get("find_text")
        if find_text is None:  # pragma: no cover
            raise ServerError(f"{tag}: no find pattern")
        settings = self._get_find_settings(c)
        settings.find_text = find_text
        if self.log_flag:  # pragma: no cover
            g.printObj(settings, tag=f"{tag}: settings for {c.shortFileName()}")
        answer = fc.do_clone_find_all(settings)
        if self.log_flag:  # pragma: no cover
            g.printObj(answer, tag=f"{tag}: answer")
        return self._make_response({"answer": answer})
    #@+node:ekr.20210221042633.1: *5* server.clone_find_all_flattened
    def clone_find_all_flattened(self, package):
        """Run Leo's clone-find-all-flattened command and return results."""
        tag = 'clone_find_all_flattened'
        c = self._check_c()
        fc = c.findCommands
        find_text = package.get("find_text")
        if find_text is None:  # pragma: no cover
            raise ServerError(f"{tag}: no find pattern")
        settings = self._get_find_settings(c)
        settings.find_text = find_text
        if self.log_flag:  # pragma: no cover
            g.printObj(settings, tag=f"{tag}: settings for {c.shortFileName()}")
        answer = fc.do_clone_find_all_flattened(settings)
        if self.log_flag:  # pragma: no cover
            g.printObj(answer, tag=f"{tag}: answer")
        return self._make_response({"answer": answer})
    #@+node:ekr.20210221042719.1: *5* server.clone_find_tag
    def clone_find_tag(self, package):
        """Run Leo's clone-find-tag command and return results."""
        tag = 'clone_find_tag'
        c = self._check_c()
        fc = c.findCommands
        the_tag = package.get("tag")
        if not the_tag:  # pragma: no cover
            raise ServerError(f"{tag}: no tag")
        settings = self._get_find_settings(c)
        if self.log_flag:  # pragma: no cover
            g.printObj(settings, tag=f"{tag}: settings for {c.shortFileName()}")
        n, p = fc.do_clone_find_tag(settings)
        if self.log_flag:  # pragma: no cover
            g.trace("tag: {the_tag} n: {n} p: {p and p.h!r}")
        return self._make_response({"n": n, "p": p})
    #@+node:ekr.20210221043043.1: *5* server.find_def
    def find_def(self, package):
        """Run Leo's find-def command and return results."""
        tag = 'find_def'
        c = self._check_c()
        fc = c.findCommands
        find_text = package.get("find_text")
        if find_text is None:  # pragma: no cover
            raise ServerError(f"{tag}: no find pattern")
        settings = self._get_find_settings(c)
        settings.find_text = find_text
        if self.log_flag:  # pragma: no cover
            g.printObj(settings, tag=f"{tag}: settings for {c.shortFileName()}")
        p, pos, newpos = fc.do_find_def(settings, word=find_text, strict=False)
        if self.log_flag:  # pragma: no cover
            g.trace(f"p: {p and p.h!r} pos: {pos} newpos {newpos}")
        return self._make_response({"p": p, "pos": pos, "newpos": newpos})
    #@+node:ekr.20210221042808.1: *5* server.find_next
    def find_next(self, package):
        """Run Leo's find-next command and return results."""
        tag = 'find_next'
        c = self._check_c()
        fc = c.findCommands
        find_text = package.get("find_text")
        if find_text is None:  # pragma: no cover
            raise ServerError(f"{tag}: no find pattern")
        settings = self._get_find_settings(c)
        settings.find_text = find_text
        if self.log_flag:  # pragma: no cover
            g.printObj(settings, tag=f"{tag}: settings for {c.shortFileName()}")
        p, pos, newpos = fc.do_find_next(settings)
        if self.log_flag:  # pragma: no cover
            g.trace(f"p: {p and p.h!r} pos: {pos} newpos {newpos}")
        return self._make_response({"p": p, "pos": pos, "newpos": newpos})
    #@+node:ekr.20210221042851.1: *5* server.find_previous
    def find_previous(self, package):
        """Run Leo's find-previous command and return results."""
        tag = 'find_previous'
        c = self._check_c()
        fc = c.findCommands
        find_text = package.get("find_text")
        if find_text is None:  # pragma: no cover
            raise ServerError(f"{tag}: no find pattern")
        settings = self._get_find_settings(c)
        settings.find_text = find_text
        if self.log_flag:  # pragma: no cover
            g.printObj(settings, tag=f"{tag}: settings for {c.shortFileName()}")
        p, pos, newpos = fc.do_find_prev(settings)
        if self.log_flag:  # pragma: no cover
            g.trace(f"p: {p and p.h!r} pos: {pos} newpos {newpos}")
        return self._make_response({"p": p, "pos": pos, "newpos": newpos})
    #@+node:ekr.20210221043134.1: *5* server.find_var
    def find_var(self, package):
        """Run Leo's find-var command and return results."""
        tag = 'find_var'
        c = self._check_c()
        fc = c.findCommands
        find_text = package.get("find_text")
        if find_text is None:  # pragma: no cover
            raise ServerError(f"{tag}: no find pattern")
        settings = self._get_find_settings(c)
        settings.find_text = find_text
        if self.log_flag:  # pragma: no cover
            g.printObj(settings, tag=f"{tag}: settings for {c.shortFileName()}")
        p, pos, newpos = fc.do_find_var(settings, word=find_text)
        if self.log_flag:  # pragma: no cover
            g.trace(f"p: {p and p.h!r} pos: {pos} newpos {newpos}")
        return self._make_response({"p": p, "pos": pos, "newpos": newpos})
    #@+node:ekr.20210221043224.1: *5* server.tag_children
    def tag_children(self, package):
        """Run Leo's tag-children command and return results."""
        # This is not a find command!
        tag = 'tag_children'
        c = self._check_c()
        fc = c.findCommands
        the_tag = package.get("tag")
        if the_tag is None:  # pragma: no cover
            raise ServerError(f"{tag}: no tag")
        # Unlike find commands, do_tag_children does not use a settings dict.
        fc.do_tag_children(c.p, the_tag)
        return self._make_response({})
    #@+node:ekr.20210202193505.1: *4* server:getter commands
    #@+node:ekr.20210202110128.55: *5* server.get_all_open_commanders
    def get_all_open_commanders(self, package):
        """Return array describing each commander in g.app.commanders()."""
        files = [
            {
                "changed": c.isChanged(),
                "name": c.fileName(),
                "selected": c == self.c,
            } for c in g.app.commanders()
        ]
        return self._make_response({"open-commanders": files})
    #@+node:ekr.20210202110128.71: *5* server.get_all_positions
    def get_all_positions(self, package):
        """
        Return a list of position data for all positions.
        
        Useful as a sanity check for debugging.
        """
        c = self._check_c()
        result = [
            self._get_position_d(p) for p in c.all_positions(copy=False)
        ]
        return self._make_response({"position-data-list": result})
    #@+node:ekr.20210202110128.72: *5* server.get_body & get_body_length
    def get_body(self, package):
        """
        Return p.b, where p is c.p if package["ap"] is missing.
        
        Note: There is no need for a separate get_body_length command,
              because _make_response always adds "body-length": len(p.b)
        """
        self._check_c()
        p = self._get_p(package)
        # _make_response adds all the cheap redraw data, including "body-length"
        return self._make_response({"body": p.b})
        
    #@+node:ekr.20210202110128.66: *5* server.get_body_states
    def get_body_states(self, package):
        """
        Return body data for p, where p is c.p if package["ap"] is missing.
        """
        c = self._check_c()
        p = self._get_p(package)
        wrapper = c.frame.body.wrapper
        
        def row_col_dict(i):
            junk, line, col = wrapper.toPythonIndexRowCol(i)
            return {"line": line, "col": col}
            
        # Get the language.
        aList = g.get_directives_dict_list(p)
        d = g.scanAtCommentAndAtLanguageDirectives(aList)
        language = (
            d and d.get('language')
            or g.getLanguageFromAncestorAtFileNode(p)
            or c.config.getLanguage('target-language')
            or 'plain'
        )
        # get values from wrapper if it's the selected node.
        if c.p.v.gnx == p.v.gnx:
            active = wrapper.getInsertPoint()
            start, end = wrapper.getSelectionRange(True)
            scroll = wrapper.getYScrollPosition()
        else:  # pragma: no cover
            active = p.v.insertSpot
            start = p.v.selectionStart
            end = p.v.selectionStart + p.v.selectionLength
            scroll = p.v.scrollBarSpot
        states = {
            'language': language.lower(),
            'selection': {
                # "gnx": p.v.gnx,  # EKR: Not needed. The reponse will have p.v.gnx.
                "scroll": scroll,
                "active": row_col_dict(active),
                "start": row_col_dict(start),
                "end": row_col_dict(end),
            }
        }
        return self._make_response({"body-states": states})
    #@+node:ekr.20210202110128.68: *5* server.get_children
    def get_children(self, package):
        """
        Return the node data for children of p, where p is c.p if package["ap"] is missing."""
        self._check_c()
        p = self._get_p(package)
        return self._make_response({
            # "children": [self._p_to_ap(child) for child in p.children()]
            "children": [self._get_position_d(child) for child in p.children()]
        })
    #@+node:ekr.20210214154702.1: *5* server.get_focus
    def get_focus(self, packages):
        """
        Return a representation of the focs widget,
        one of ("body", "tree", "headline", repr(the_widget)).
        """
        w = g.app.gui.get_focus()
        focus = g.app.gui.widget_name(w)
        return self._make_response({"focus": focus})
    #@+node:ekr.20210202110128.69: *5* server.get_parent
    def get_parent(self, package):
        """Return the node data for the parent of position p, where p is c.p if package["ap"] is missing."""
        self._check_c()
        p = self._get_p(package)
        parent = p.parent()
        data = self._get_position_d(parent) if parent else None
        return self._make_response({"parent": data})
    #@+node:ekr.20210211053955.1: *5* server.get_position_dict
    def get_position_data_dict(self, package):
        """
        Return a dict of postition data for all positions.
        
        Useful as a sanity check for debugging.
        """
        c = self._check_c()
        result = {
            p.v.gnx: self._get_position_d(p)
                for p in c.all_unique_positions(copy=False)
        }
        return self._make_response({"position-data-dict": result})
    #@+node:ekr.20210211233814.1: *5* server.get_ua
    def get_ua(self, package):
        """Return p.v.u, making sure it can be serialized."""
        self._check_c()
        p = self._get_p(package)
        try:
            ua = {"ua": p.v.u}
            json.dumps(ua, separators=(',', ':'))
            response = {"p": p, "ua": p.v.u} 
        except Exception:  # pragma: no cover
            response = {"p": p, "bad-ua": repr(p.v.u)} 
        # _make_response adds all the cheap redraw data.
        return self._make_response(response)
    #@+node:ekr.20210206062654.1: *5* server.get_sign_on
    def get_sign_on(self, package):
        """Synchronous version of _sign_on"""
        g.app.computeSignon()
        signon = []
        for z in (g.app.signon, g.app.signon1):
            for z2 in z.split('\n'):
                signon.append(z2.strip())
        return self._make_response({"sign-on": "\n".join(signon)})
    #@+node:ekr.20210202110128.61: *5* server.get_ui_states
    def get_ui_states(self, package):
        """
        Return the enabled/disabled UI states for the open commander, or defaults if None.
        """
        c = self._check_c()
        tag = 'get_ui_states'
        try:
            states = {
                "changed": c and c.changed,
                "canUndo": c and c.canUndo(),
                "canRedo": c and c.canRedo(),
                "canDemote": c and c.canDemote(),
                "canPromote": c and c.canPromote(),
                "canDehoist": c and c.canDehoist(),
            }
        except Exception as e:  # pragma: no cover
            raise ServerError(f"{tag}: Exception setting state: {e}")
        return self._make_response({"states": states})
    #@+node:ekr.20210202193540.1: *4* server:node commands
    #@+node:ekr.20210202183724.11: *5* server.clone_node
    def clone_node(self, package):
        """
        Clone the node at position p, where p is c.p if package["ap"] is missing.
        
        To clone c.p, use this request:
        {
            "action": "execute-leo-command",
            "leo-command-name": "clone",
        }
        """
        c = self._check_c()
        p = self._get_p(package)
        c.selectPosition(p)
        c.clone()
        return self._make_response()
    #@+node:ekr.20210202110128.79: *5* server.contract_node
    def contract_node(self, package):
        """
        Contract the node at position p, where p is c.p if package["ap"] is missing.
        
        To contract c.p, use this request:
        {
            "action": "execute-leo-command",
            "leo-command-name": "contract-node",
        }
        """
        self._check_c()
        p = self._get_p(package)
        p.contract()
        return self._make_response()
    #@+node:ekr.20210202183724.12: *5* server.cut_node
    def cut_node(self, package):  # pragma: no cover (too dangerous, for now)
        """
        Cut the node (and its descendants) at position p, where p is c.p if package["ap"] is missing.
        
        To cut c.p, use this request:
        {
            "action": "execute-leo-command",
            "leo-command-name": "cut-node",
        }
        """
        c = self._check_c()
        p = self._get_p(package)
        c.selectPosition(p)
        c.cutOutline()
        return self._make_response()
    #@+node:ekr.20210202183724.13: *5* server.delete_node
    def delete_node(self, package):  # pragma: no cover (too dangerous, for now)
        """
        Delete the node (and its descendants) at position p, where p is c.p if package["ap"] is missing.
        
        To delete c.p, use this request:
        {
            "action": "execute-leo-command",
            "leo-command-name": "delete-node",
        }
        """
        c = self._check_c()
        p = self._get_p(package)
        c.selectPosition(p)
        c.deleteOutline()  # Handles undo.
        return self._make_response()
    #@+node:ekr.20210202110128.78: *5* server.expand_node
    def expand_node(self, package):
        """
        Expand the node at position p, where p is c.p if package["ap"] is missing.
        
        To expand c.p, use this request:
        {
            "action": "execute-leo-command",
            "leo-command-name": "expand-node",
        }
        """
        self._check_c()
        p = self._get_p(package)
        p.expand()
        return self._make_response()
    #@+node:ekr.20210202183724.15: *5* server.insert_node
    def insert_node(self, package):
        """
        Insert a new node at position p, where p is c.p if package["ap"] is missing.

        This node has 'newHeadline' as its headline.
        
        To insert a new node at c.p (with the default headline), use this request:
        {
            "action": "execute-leo-command",
            "leo-command-name": "insert-node",
        }
        
        Use the 'set_headline' method to undoably set any node's headlines.
        """
        c = self._check_c()
        p = self._get_p(package)
        c.selectPosition(p)
        c.insertHeadline()  # Handles undo, sets c.p
        return self._make_response()
    #@+node:ekr.20210202110128.64: *5* server.page_down
    def page_down(self, package):
        """
        Selects a node "n" steps down in the tree to simulate page down.
        """
        c = self._check_c()
        n = package.get("n", 3)
        for z in range(n):
            c.selectVisNext()
        return self._make_response()
    #@+node:ekr.20210202110128.63: *5* server.page_up
    def page_up(self, package):
        """
        Selects a node "N" steps up in the tree to simulate page up.
        """
        c = self._check_c()
        n = package.get("n", 3)
        for z in range(n):
            c.selectVisBack()
        return self._make_response()
    #@+node:ekr.20210202183724.17: *5* server.redo
    def redo(self, package):
        """Undo last un-doable operation"""
        c = self._check_c()
        u = c.undoer
        if u.canRedo():
            u.redo()
        return self._make_response()
    #@+node:ekr.20210202110128.74: *5* server.set_body
    def set_body(self, package):
        """
        Undoably set p.b, where p is c.p if package["ap"] is missing.
        """
        tag = 'set_body'
        c = self._check_c()
        p = self._get_p(package)
        u, wrapper = c.undoer, c.frame.body.wrapper
        body = package.get('body')
        if body is None:  # pragma: no cover
            raise ServerError(f"{tag}: no body given")
        bunch = u.beforeChangeNodeContents(p)
        p.v.setBodyString(body)
        u.afterChangeNodeContents(p, "Body Text", bunch)
        if c.p == p:
            wrapper.setAllText(body)
        if not self.c.isChanged():  # pragma: no cover
            c.setChanged()
        if not p.v.isDirty():  # pragma: no cover
            p.setDirty()
        return self._make_response()
    #@+node:ekr.20210202110128.77: *5* server.set_current_position
    def set_current_position(self, package):
        """Select position p, where p is c.p if package["ap"] is missing."""
        c = self._check_c()
        p = self._get_p(package)
        c.selectPosition(p)
        return self._make_response()
    #@+node:ekr.20210202110128.76: *5* server.set_headline
    def set_headline(self, package):
        """
        Undoably set p.h, where p is c.p if package["ap"] is missing.
        """
        tag = 'set_headline'
        c = self._check_c()
        p = self._get_p(package)
        u = c.undoer
        h = package.get('headline')
        if not h:  # pragma: no cover
            raise ServerError(f"{tag}: no headline")
        bunch = u.beforeChangeNodeContents(p)
        p.h = h
        u.afterChangeNodeContents(p, 'Change Headline', bunch)
        return self._make_response()
    #@+node:ekr.20210202110128.75: *5* server.set_selection
    def set_selection(self, package):
        """
        Set the selection range for p.b, where p is c.p if package["ap"] is missing.
        
        Set the selection in the wrapper if p == c.p
        
        Package has these keys:
            
        - "ap":     An archived position for position p.
        - "start":  The start of the selection.
        - "end":    The end of the selection.
        - "insert": The insert point. Must be either start or end.
        - "scroll": An optional scroll position.
        """
        c = self._check_c()
        p = self._get_p(package)  # Will raise ServerError if p does not exist.
        v = p.v
        wrapper = c.frame.body.wrapper
        start = package.get('start', 0)
        end = package.get('end', 0)
        insert = package.get('insert', 0)
        scroll = package.get('scroll', 0)
        if p == c.p:
            wrapper.setSelectionRange(start, end, insert)
            wrapper.setYScrollPosition(scroll)
        # Always set vnode attrs.
        v.scrollBarSpot = scroll
        v.insertSpot = insert
        v.selectionStart = start
        v.selectionLength = abs(start - end)
        return self._make_response()
    #@+node:ekr.20210202183724.10: *5* server.toggle_mark
    def toggle_mark(self, package):
        """
        Toggle the mark at position p, where p is c.p if package["ap"] is missing.
        
        To *toggle* the mark of c.p, use this request:
        {
            "action": "execute-leo-command",
            "leo-command-name": "toggle-mark",
        }
        """
        self._check_c()
        p = self._get_p(package)
        if p.isMarked():
            p.clearMarked()
        else:
            p.setMarked()
        return self._make_response()
    #@+node:ekr.20210202183724.16: *5* server.undo
    def undo(self, package):
        """Undo last un-doable operation"""
        c = self._check_c()
        u = c.undoer
        if u.canUndo():
            u.undo()
        # Félix: Caller can get focus using other calls.
        return self._make_response()
    #@+node:ekr.20210205102806.1: *4* server:server commands
    #@+node:ekr.20210205102818.1: *5* server.error
    def error(self, package):
        """For unit testing. Raise ServerError"""
        raise ServerError(f"error called")
    #@+node:ekr.20210202183724.5: *5* server.get_all_leo_commands & helper
    def get_all_leo_commands(self, package):
        """Return a list of all Leo commands that make sense in leoInteg."""
        tag = 'get_all_leo_commands'
        c = self.dummy_c  # Use the dummy commander.
        d = c.commandsDict  # keys are command names, values are functions.
        bad_names = self._bad_commands(c)  # #92.
        good_names = self._good_commands()
        duplicates = set(bad_names).intersection(set(good_names))
        if duplicates:  # pragma: no cover
            print('duplicate command names...')
            for z in sorted(duplicates):
                print(z)
        result = []
        for command_name in sorted(d):
            func = d.get(command_name)
            if not func:  # pragma: no cover
                print('no func:', command_name)
                continue
            if command_name in bad_names:  # #92.
                continue
            # Prefer func.__func_name__ to func.__name__: Leo's decorators change func.__name__!
            func_name = getattr(func, '__func_name__', func.__name__)
            if not func_name:  # pragma: no cover
                print('no name', command_name)
                continue
            doc = func.__doc__ or ''
            result.append({
                "command-name": command_name,
                "func":  func_name,
                "detail": doc,
            })
        if self.log_flag:  # pragma: no cover
            print(f"\n{tag}: {len(result)} leo commands\n")
            g.printObj([z.get("command-name") for z in result], tag=tag)
        return self._make_response({"commands": result})
    #@+node:ekr.20210202183724.6: *6* server._bad_commands
    def _bad_commands(self, c):
        """Return the list of Leo's command names that leoInteg should ignore."""
        d = c.commandsDict  # keys are command names, values are functions.
        bad = []
        #
        # First, remove @button, @command and vim commands.
        for command_name in sorted(d):
            if command_name.startswith((':', '@')):
                # print('ignore', command_name)
                bad.append(command_name)
        # Second, remove other commands.
        # This is a hand-curated list.
        bad_list = [

            # Abbreviations...
            'abbrev-kill-all',
            'abbrev-list',
            'dabbrev-completion',
            'dabbrev-expands',

            # Autocompletion...
            'auto-complete',
            'auto-complete-force',
            'disable-autocompleter',
            'disable-calltips',
            'enable-autocompleter',
            'enable-calltips',

            # Debugger...
            'debug',
            'db-again',
            'db-b',
            'db-c',
            'db-h',
            'db-input',
            'db-l',
            'db-n',
            'db-q',
            'db-r',
            'db-s',
            'db-status',
            'db-w',

            # File operations...
            'directory-make',
            'directory-remove',
            'file-delete',
            'file-diff-files',
            'file-insert',
            'file-new',
            'file-open-by-name',

            # All others...
            'shell-command',
            'shell-command-on-region',
            'cheat-sheet',
            'dehoist',  # Duplicates of de-hoist.
            'find-clone-all',
            'find-clone-all-flattened',
            'find-clone-tag',
            'find-all',
            'find-all-unique-regex',
            'find-character',
            'find-character-extend-selection',
            'find-next',
            'find-prev',
            'find-word',
            'find-word-in-line',

            'global-search',

            'isearch-backward',
            'isearch-backward-regexp',
            'isearch-forward',
            'isearch-forward-regexp',
            'isearch-with-present-options',

            'replace',
            'replace-all',
            'replace-current-character',
            'replace-then-find',

            're-search-backward',
            're-search-forward',

            'search-backward',
            'search-forward',
            'search-return-to-origin',

            'set-find-everywhere',
            'set-find-node-only',
            'set-find-suboutline-only',
            'set-replace-string',
            'set-search-string',

            'show-find-options',

            'start-search',

            'toggle-find-collapses-nodes',
            'toggle-find-ignore-case-option',
            'toggle-find-in-body-option',
            'toggle-find-in-headline-option',
            'toggle-find-mark-changes-option',
            'toggle-find-mark-finds-option',
            'toggle-find-regex-option',
            'toggle-find-word-option',
            'toggle-find-wrap-around-option',

            'word-search-backward',
            'word-search-forward',

            # Buttons...
            'delete-script-button-button',

            # Clicks...
            'click-click-box',
            'click-icon-box',
            'ctrl-click-at-cursor',
            'ctrl-click-icon',
            'double-click-icon-box',
            'right-click-icon',

            # Editors...
            'add-editor', 'editor-add',
            'delete-editor', 'editor-delete',
            'detach-editor-toggle',
            'detach-editor-toggle-max',

            # Focus...
            'cycle-editor-focus', 'editor-cycle-focus',
            'focus-to-body',
            'focus-to-find',
            'focus-to-log',
            'focus-to-minibuffer',
            'focus-to-nav',
            'focus-to-spell-tab',
            'focus-to-tree',

            'tab-cycle-next',
            'tab-cycle-previous',
            'tab-detach',

            # Headlines..
            'abort-edit-headline',
            'edit-headline',
            'end-edit-headline',

            # Layout and panes...
            'adoc',
            'adoc-with-preview',

            'contract-body-pane',
            'contract-log-pane',
            'contract-outline-pane',

            'edit-pane-csv',
            'edit-pane-test-open',
            'equal-sized-panes',
            'expand-log-pane',
            'expand-body-pane',
            'expand-outline-pane',

            'free-layout-context-menu',
            'free-layout-load',
            'free-layout-restore',
            'free-layout-zoom',

            'zoom-in',
            'zoom-out'

            # Log
            'clear-log',

            # Menus...
            'activate-cmds-menu',
            'activate-edit-menu',
            'activate-file-menu',
            'activate-help-menu',
            'activate-outline-menu',
            'activate-plugins-menu',
            'activate-window-menu',
            'context-menu-open',
            'menu-shortcut',

            # Modes...
            'clear-extend-mode',

            # Outline...
            'contract-or-go-left',
            'contract-node',
            'contract-parent',

            # Scrolling...
            'scroll-down-half-page',
            'scroll-down-line',
            'scroll-down-page',
            'scroll-outline-down-line',
            'scroll-outline-down-page',
            'scroll-outline-left',
            'scroll-outline-right',
            'scroll-outline-up-line',
            'scroll-outline-up-page',
            'scroll-up-half-page',
            'scroll-up-line',
            'scroll-up-page',

            # Windows...
            'about-leo',

            'cascade-windows',
            'close-others',
            'close-window',

            'iconify-frame',

            'find-tab-hide',
            'find-tab-open',

            'hide-body-dock',
            'hide-body-pane',
            'hide-invisibles',
            'hide-log-pane',
            'hide-outline-dock',
            'hide-outline-pane',
            'hide-tabs-dock',

            'minimize-all',

            'resize-to-screen',

            'show-body-dock',
            'show-hide-body-dock',
            'show-hide-outline-dock',
            'show-hide-render-dock',
            'show-hide-tabs-dock',
            'show-tabs-dock',
            'clean-diff',
            'cm-external-editor',

            'delete-@button-parse-json-button',
            'delete-trace-statements',

            'disable-idle-time-events',
            'do-nothing',

            'enable-idle-time-events',
            'enter-quick-command-mode',
            'exit-named-mode',

            'F6-open-console',

            'flush-lines',
            'full-command',

            'get-child-headlines',

            'history',

            'insert-file-name',

            'justify-toggle-auto',

            'keep-lines',
            'keyboard-quit',

            'line-number',
            'line-numbering-toggle',
            'line-to-headline',

            'marked-list',

            'mode-help',

            'open-python-window',

            'open-with-idle',
            'open-with-open-office',
            'open-with-scite',
            'open-with-word',

            'recolor',
            'redraw',

            'repeat-complex-command',

            'session-clear',
            'session-create',
            'session-refresh',
            'session-restore',
            'session-snapshot-load',
            'session-snapshot-save',

            'set-colors',
            'set-command-state',
            'set-comment-column',
            'set-extend-mode',
            'set-fill-column',
            'set-fill-prefix',
            'set-font',
            'set-insert-state',
            'set-overwrite-state',
            'set-silent-mode',

            'show-buttons',
            'show-calltips',
            'show-calltips-force',
            'show-color-names',
            'show-color-wheel',
            'show-commands',
            'show-file-line',

            'show-focus',
            'show-fonts',

            'show-invisibles',
            'show-next-tip',
            'show-node-uas',
            'show-outline-dock',
            'show-plugin-handlers',
            'show-plugins-info',
            'show-settings',
            'show-settings-outline',
            'show-spell-info',
            'show-stats',

            'style-set-selected',

            'suspend',

            'toggle-abbrev-mode',
            'toggle-active-pane',
            'toggle-angle-brackets',
            'toggle-at-auto-at-edit',
            'toggle-autocompleter',
            'toggle-calltips',
            'toggle-case-region',
            'toggle-extend-mode',
            'toggle-idle-time-events',
            'toggle-input-state',
            'toggle-invisibles',
            'toggle-line-numbering-root',
            'toggle-sparse-move',
            'toggle-split-direction',

            'what-line',
            'eval',
            'eval-block',
            'eval-last',
            'eval-last-pretty',
            'eval-replace',

            'find-quick',
            'find-quick-changed',
            'find-quick-selected',
            'find-quick-test-failures',
            'find-quick-timeline',

            'goto-next-history-node',
            'goto-prev-history-node',

            'preview',
            'preview-body',
            'preview-expanded-body',
            'preview-expanded-html',
            'preview-html',
            'preview-marked-bodies',
            'preview-marked-html',
            'preview-marked-nodes',
            'preview-node',
            'preview-tree-bodies',
            'preview-tree-html',
            'preview-tree-nodes',

            'spell-add',
            'spell-as-you-type-next',
            'spell-as-you-type-toggle',
            'spell-as-you-type-undo',
            'spell-as-you-type-wrap',
            'spell-change',
            'spell-change-then-find',
            'spell-find',
            'spell-ignore',
            'spell-tab-hide',
            'spell-tab-open',

            'tag-children',

            'todo-children-todo',
            'todo-dec-pri',
            'todo-find-todo',
            'todo-fix-datetime',
            'todo-inc-pri',

            'vr',
            'vr-contract',
            'vr-expand',
            'vr-hide',
            'vr-lock',
            'vr-pause-play-movie',
            'vr-show',
            'vr-toggle',
            'vr-unlock',
            'vr-update',
            'vr-zoom',

            'vs-create-tree',
            'vs-dump',
            'vs-reset',
            'vs-update',
            # vs code's text editing commands should cover all of these...
            'add-comments',
            'add-space-to-lines',
            'add-tab-to-lines',
            'align-eq-signs',

            'back-char',
            'back-char-extend-selection',
            'back-page',
            'back-page-extend-selection',
            'back-paragraph',
            'back-paragraph-extend-selection',
            'back-sentence',
            'back-sentence-extend-selection',
            'back-to-home',
            'back-to-home-extend-selection',
            'back-to-indentation',
            'back-word',
            'back-word-extend-selection',
            'back-word-smart',
            'back-word-smart-extend-selection',
            'backward-delete-char',
            'backward-delete-word',
            'backward-delete-word-smart',
            'backward-find-character',
            'backward-find-character-extend-selection',
            'backward-kill-paragraph',
            'backward-kill-sentence',
            'backward-kill-word',
            'beginning-of-buffer',
            'beginning-of-buffer-extend-selection',
            'beginning-of-line',
            'beginning-of-line-extend-selection',

            'capitalize-word',
            'center-line',
            'center-region',
            'clean-all-blank-lines',
            'clean-all-lines',
            'clean-body',
            'clean-lines',
            'clear-kill-ring',
            'clear-selected-text',
            'convert-blanks',
            'convert-tabs',
            'copy-text',
            'cut-text',

            'delete-char',
            'delete-comments',
            'delete-indentation',
            'delete-spaces',
            'delete-word',
            'delete-word-smart',
            'downcase-region',
            'downcase-word',

            'end-of-buffer',
            'end-of-buffer-extend-selection',
            'end-of-line',
            'end-of-line-extend-selection',

            'exchange-point-mark',

            'extend-to-line',
            'extend-to-paragraph',
            'extend-to-sentence',
            'extend-to-word',

            'fill-paragraph',
            'fill-region',
            'fill-region-as-paragraph',

            'finish-of-line',
            'finish-of-line-extend-selection',

            'forward-char',
            'forward-char-extend-selection',
            'forward-end-word',
            'forward-end-word-extend-selection',
            'forward-page',
            'forward-page-extend-selection',
            'forward-paragraph',
            'forward-paragraph-extend-selection',
            'forward-sentence',
            'forward-sentence-extend-selection',
            'forward-word',
            'forward-word-extend-selection',
            'forward-word-smart',
            'forward-word-smart-extend-selection',

            'go-anywhere',
            'go-back',
            'go-forward',
            'goto-char',

            'indent-region',
            'indent-relative',
            'indent-rigidly',
            'indent-to-comment-column',

            'insert-hard-tab',
            'insert-newline',
            'insert-parentheses',
            'insert-soft-tab',

            'kill-line',
            'kill-paragraph',
            'kill-pylint',
            'kill-region',
            'kill-region-save',
            'kill-sentence',
            'kill-to-end-of-line',
            'kill-word',
            'kill-ws',

            'match-brackets',

            'move-lines-down',
            'move-lines-up',
            'move-past-close',
            'move-past-close-extend-selection',

            'newline-and-indent',
            'next-line',
            'next-line-extend-selection',
            'next-or-end-of-line',
            'next-or-end-of-line-extend-selection',

            'previous-line',
            'previous-line-extend-selection',
            'previous-or-beginning-of-line',
            'previous-or-beginning-of-line-extend-selection',

            'rectangle-clear',
            'rectangle-close',
            'rectangle-delete',
            'rectangle-kill',
            'rectangle-open',
            'rectangle-string',
            'rectangle-yank',

            'remove-blank-lines',
            'remove-newlines',
            'remove-space-from-lines',
            'remove-tab-from-lines',

            'reverse-region',
            'reverse-sort-lines',
            'reverse-sort-lines-ignoring-case',

            'paste-text',
            'pop-cursor',
            'push-cursor',

            'select-all',
            'select-next-trace-statement',
            'select-to-matching-bracket',

            'sort-columns',
            'sort-fields',
            'sort-lines',
            'sort-lines-ignoring-case',

            'split-defs',
            'split-line',

            'start-of-line',
            'start-of-line-extend-selection',

            'tabify',
            'transpose-chars',
            'transpose-lines',
            'transpose-words',

            'unformat-paragraph',
            'unindent-region',

            'untabify',

            'upcase-region',
            'upcase-word',
            'update-ref-file',

            'yank',
            'yank-pop',

            'zap-to-character',

        ]
        bad.extend(bad_list)
        result = list(sorted(bad))
        return result

    #@+node:ekr.20210202183724.7: *6* server._good_commands
    def _good_commands(self):
        """Defined commands that definitely should be included in leoInteg."""
        good_list = [

            'contract-all',
            'contract-all-other-nodes',
            'clone-node',
            'copy-node',
            'copy-marked-nodes',
            'cut-node',

            'de-hoist',
            'delete-marked-nodes',
            'delete-node',
            'demangle-recent-files',
            'demote',

            'expand-and-go-right',
            'expand-next-level',
            'expand-node',
            'expand-or-go-right',
            'expand-prev-level',
            'expand-to-level-1',
            'expand-to-level-2',
            'expand-to-level-3',
            'expand-to-level-4',
            'expand-to-level-5',
            'expand-to-level-6',
            'expand-to-level-7',
            'expand-to-level-8',
            'expand-to-level-9',
            'expand-all',
            'expand-all-subheads',
            'expand-ancestors-only',

            'find-next-clone',

            'goto-first-node',
            'goto-first-sibling',
            'goto-first-visible-node',
            'goto-last-node',
            'goto-last-sibling',
            'goto-last-visible-node',
            'goto-next-changed',
            'goto-next-clone',
            'goto-next-marked',
            'goto-next-node',
            'goto-next-sibling',
            'goto-next-visible',
            'goto-parent',
            'goto-prev-marked',
            'goto-prev-node',
            'goto-prev-sibling',
            'goto-prev-visible',

            'hoist',

            'insert-node',
            'insert-node-before',
            'insert-as-first-child',
            'insert-as-last-child',
            'insert-child',

            'mark',
            'mark-changed-items',
            'mark-first-parents',
            'mark-subheads',

            'move-marked-nodes',
            'move-outline-down',
            'move-outline-left',
            'move-outline-right',
            'move-outline-up',

            'paste-node',
            'paste-retaining-clones',
            'promote',
            'promote-bodies',
            'promote-headlines',

            'sort-children',
            'sort-siblings',

            'tangle',
            'tangle-all',
            'tangle-marked',

            'unmark-all',
            'unmark-first-parents',
            'clean-main-spell-dict',
            'clean-persistence',
            'clean-recent-files',
            'clean-spellpyx',
            'clean-user-spell-dict',

            'clear-all-caches',
            'clear-all-hoists',
            'clear-all-uas',
            'clear-cache',
            'clear-node-uas',
            'clear-recent-files',

            'delete-first-icon',
            'delete-last-icon',
            'delete-node-icons',

            'dump-caches',
            'dump-clone-parents',
            'dump-expanded',
            'dump-node',
            'dump-outline',

            'insert-icon',

            'set-ua',

            'show-all-uas',
            'show-bindings',
            'show-clone-ancestors',
            'show-clone-parents',
            # Export files...
            'export-headlines',
            'export-jupyter-notebook',
            'outline-to-cweb',
            'outline-to-noweb',
            'remove-sentinels',
            'typescript-to-py',

            # Import files...
            'import-MORE-files',
            'import-file',
            'import-free-mind-files',
            'import-jupyter-notebook',
            'import-legacy-external-files',
            'import-mind-jet-files',
            'import-tabbed-files',
            'import-todo-text-files',
            'import-zim-folder',

            # Open specific files...
            # 'ekr-projects',
            'leo-cheat-sheet',  # These duplicates are useful.
            'leo-dist-leo',
            'leo-docs-leo',
            'leo-plugins-leo',
            'leo-py-leo',
            'leo-quickstart-leo',
            'leo-scripts-leo',
            'leo-settings',
            'leo-unittest-leo',
            'my-leo-settings',
            # 'scripts',
            'settings',

            'open-cheat-sheet-leo',
            'open-desktop-integration-leo',
            'open-leo-dist-leo',
            'open-leo-docs-leo',
            'open-leo-plugins-leo',
            'open-leo-py-leo',
            'open-leo-settings',
            'open-leo-settings-leo',
            'open-local-settings',
            'open-my-leo-settings',
            'open-my-leo-settings-leo',
            'open-quickstart-leo',
            'open-scripts-leo',
            'open-unittest-leo',

            # Open other places...
            'open-offline-tutorial',
            'open-online-home',
            'open-online-toc',
            'open-online-tutorials',
            'open-online-videos',
            'open-recent-file',
            'open-theme-file',
            'open-url',
            'open-url-under-cursor',
            'open-users-guide',

            # Read outlines...
            'read-at-auto-nodes',
            'read-at-file-nodes',
            'read-at-shadow-nodes',
            'read-file-into-node',
            'read-outline-only',
            'read-ref-file',

            # Save Files.
            'file-save',
            'file-save-as',
            'file-save-as-unzipped',
            'file-save-by-name',
            'file-save-to',
            'save',  # Some may not be needed.
            'save-all',
            'save-as',
            'save-file',
            'save-file-as',
            'save-file-as-unzipped',
            'save-file-as-zipped',
            'save-file-by-name',
            'save-file-to',
            'save-to',

            # Write parts of outlines...
            'write-at-auto-nodes',
            'write-at-file-nodes',
            'write-at-shadow-nodes',
            'write-dirty-at-auto-nodes',
            'write-dirty-at-file-nodes',
            'write-dirty-at-shadow-nodes',
            'write-edited-recent-files',
            'write-file-from-node',
            'write-missing-at-file-nodes',
            'write-outline-only',

            'clone-find-all',
            'clone-find-all-flattened',
            'clone-find-all-flattened-marked',
            'clone-find-all-marked',
            'clone-find-parents',
            'clone-find-tag',
            'clone-marked-nodes',
            'clone-node-to-last-node',
            'clone-to-at-spot',

            'edit-setting',
            'edit-shortcut',

            'execute-pytest',
            'execute-script',
            'extract',
            'extract-names',

            'goto-any-clone',
            'goto-global-line',
            'goto-line',
            'git-diff', 'gd',

            'log-kill-listener', 'kill-log-listener',
            'log-listen', 'listen-to-log',

            'make-stub-files',

            'pdb',

            'redo',
            'rst3',
            'run-all-unit-tests-externally',
            'run-all-unit-tests-locally',
            'run-marked-unit-tests-externally',
            'run-marked-unit-tests-locally',
            'run-selected-unit-tests-externally',
            'run-selected-unit-tests-locally',
            'run-tests',

            'undo',

            'xdb',
            # Beautify, blacken, fstringify...
            'beautify-files',
            'beautify-files-diff',
            'blacken-files',
            'blacken-files-diff',
            'diff-and-open-leo-files',
            'diff-beautify-files',
            'diff-fstringify-files',
            'diff-leo-files',
            'diff-marked-nodes',
            'fstringify-files',
            'fstringify-files-diff',
            'fstringify-files-silent',
            'pretty-print-c',
            'silent-fstringify-files',

            # All other commands...
            'at-file-to-at-auto',

            'beautify-c',

            'cls',
            'c-to-python',
            'c-to-python-clean-docs',
            'check-derived-file',
            'check-outline',
            'code-to-rst',
            'compare-two-leo-files',
            'convert-all-blanks',
            'convert-all-tabs',
            'count-children',
            'count-pages',
            'count-region',

            'desktop-integration-leo',

            'edit-recent-files',
            'exit-leo',

            'file-compare-two-leo-files',
            'find-def',
            'find-long-lines',
            'find-missing-docstrings',
            'flake8',
            'flatten-outline',
            'flatten-outline-to-node',
            'flatten-script',

            'gc-collect-garbage',
            'gc-dump-all-objects',
            'gc-dump-new-objects',
            'gc-dump-objects-verbose',
            'gc-show-summary',

            'help',  # To do.
            'help-for-abbreviations',
            'help-for-autocompletion',
            'help-for-bindings',
            'help-for-command',
            'help-for-creating-external-files',
            'help-for-debugging-commands',
            'help-for-drag-and-drop',
            'help-for-dynamic-abbreviations',
            'help-for-find-commands',
            'help-for-keystroke',
            'help-for-minibuffer',
            'help-for-python',
            'help-for-regular-expressions',
            'help-for-scripting',
            'help-for-settings',

            'insert-body-time',  # ?
            'insert-headline-time',
            'insert-jupyter-toc',
            'insert-markdown-toc',

            'find-var',

            'join-leo-irc',
            'join-node-above',
            'join-node-below',
            'join-selection-to-node-below',

            'move-lines-to-next-node',

            'new',

            'open-outline',

            'parse-body',
            'parse-json',
            'pandoc',
            'pandoc-with-preview',
            'paste-as-template',

            'print-body',
            'print-cmd-docstrings',
            'print-expanded-body',
            'print-expanded-html',
            'print-html',
            'print-marked-bodies',
            'print-marked-html',
            'print-marked-nodes',
            'print-node',
            'print-sep',
            'print-tree-bodies',
            'print-tree-html',
            'print-tree-nodes',
            'print-window-state',

            'pyflakes',
            'pylint',
            'pylint-kill',
            'python-to-coffeescript',

            'quit-leo',

            'reformat-body',
            'reformat-paragraph',
            'refresh-from-disk',
            'reload-settings',
            'reload-style-sheets',
            'revert',

            'save-buffers-kill-leo',
            'screen-capture-5sec',
            'screen-capture-now',
            'script-button',  # ?
            'set-reference-file',
            'show-style-sheet',
            'sort-recent-files',
            'sphinx',
            'sphinx-with-preview',
            'style-reload',  # ?

            'untangle',
            'untangle-all',
            'untangle-marked',

            'view-lossage',  # ?

            'weave',

            # Dubious commands (to do)...
            'act-on-node',

            'cfa',  # Do we need abbreviations?
            'cfam',
            'cff',
            'cffm',
            'cft',

            'buffer-append-to',
            'buffer-copy',
            'buffer-insert',
            'buffer-kill',
            'buffer-prepend-to',
            'buffer-switch-to',
            'buffers-list',
            'buffers-list-alphabetically',

            'chapter-back',
            'chapter-next',
            'chapter-select',
            'chapter-select-main',
            'create-def-list',  # ?
        ]
        return good_list

    #@+node:ekr.20210209055518.1: *5* server.get_all_server_commands
    def get_all_server_commands(self, package):
        """
        Public server method:
        Return the names of all callable public methods of the server.
        """
        tag = 'get_all_server_commands'
        names = self._get_all_server_commands()
        if self.log_flag:  # pragma: no cover
            print(f"\n{tag}: {len(names)} server commands\n")
            g.printObj(names, tag=tag)
        return self._make_response({"server-commands": names})

    def _get_all_server_commands(self):
        """
        Private server method:
        Return the names of all callable public methods of the server.
        """
        members = inspect.getmembers(self, inspect.ismethod)
        return sorted([name for (name, value) in members if not name.startswith('_')])
    #@+node:ekr.20210202110128.52: *5* server.init_connection
    def _init_connection(self, web_socket):  # pragma: no cover (tested in client).
        """Begin the connection."""
        self.web_socket = web_socket
        self.loop = asyncio.get_event_loop()

    #@+node:ekr.20210205103759.1: *5* server.shut_down
    def shut_down(self, package):
        """Shut down the server."""
        tag = 'shut_down'
        n = len(g.app.commanders())
        if n:  # pragma: no cover
            raise ServerError(f"{tag}: {n} open outlines")
        raise TerminateServer(f"client requested shut down")
    #@+node:ekr.20210204154548.1: *3* server:server utils
    #@+node:ekr.20210202110128.85: *4* server._ap_to_p
    def _ap_to_p(self, ap):
        """
        Convert ap (archived position, a dict) to a valid Leo position.
        Raise ServerError on any kind of error.
        """
        tag = '_ap_to_p'
        c = self._check_c()
        gnx_d = c.fileCommands.gnxDict
        outer_stack = ap.get('stack')
        if outer_stack is None:  # pragma: no cover.
            raise ServerError(f"{tag}: no stack in ap: {ap}")
        if not isinstance(outer_stack, (list, tuple)):  # pragma: no cover.
            raise ServerError(f"{tag}: stack must be tuple or list: {outer_stack}")
        
        def d_to_childIndex_v (d):
            """Helper: return childIndex and v from d ["childIndex"] and d["gnx"]."""
            childIndex = d.get('childIndex')
            if childIndex is None:  # pragma: no cover.
                raise ServerError(f"{tag}: no childIndex in {d}")
            try:
                childIndex = int(childIndex)
            except Exception:  # pragma: no cover.
                raise ServerError(f"{tag}: bad childIndex: {childIndex!r}")
            gnx = d.get('gnx')
            if gnx is None:  # pragma: no cover.
                raise ServerError(f"{tag}: no gnx in {d}.")
            v = gnx_d.get(gnx)
            if v is None:  # pragma: no cover.
                raise ServerError(f"{tag}: gnx not found: {gnx}")
            return childIndex, v
        #
        # Compute p.childIndex and p.v.
        childIndex, v = d_to_childIndex_v(ap)
        #
        # Create p.stack.
        stack = []
        for stack_d in outer_stack:
            stack_childIndex, stack_v = d_to_childIndex_v(stack_d)
            stack.append((stack_v, stack_childIndex))
        #
        # Make p and check p.
        p = Position(v, childIndex, stack)
        if not c.positionExists(p):  # pragma: no cover.
            print(
                f"{tag}: Bad ap: {ap}\n"
                # f"{tag}: position: {p!r}\n"
                f"{tag}: v {v!r} childIndex: {childIndex}\n"
                f"{tag}: stack: {stack}")
            raise ServerError(f"{tag}: p does not exist in {c.shortFileName()}")
        return p
    #@+node:ekr.20210207054237.1: *4* server._check_c
    def _check_c(self):
        """Return self.c or raise ServerError if self.c is None."""
        tag = '_check_c'
        c = self.c
        if not c:  # pragma: no cover
            raise ServerError(f"{tag}: no open commander")
        return c
    #@+node:ekr.20210211131234.1: *4* server._check_outline
    def _check_outline(self, c):
        """Check self.c for consistency."""
        # Check that all positions exist.
        self._check_outline_positions(c)
        # Test round-tripping.
        self._test_round_trip_positions(c)
    #@+node:ekr.20210211131827.1: *4* server._check_outline_positions
    def _check_outline_positions(self, c):
        """Verify that all positions in c exist."""
        tag = '_check_outline_positions'
        for p in c.all_positions(copy=False):
            if not c.positionExists(p):  # pragma: no cover
                message = f"{tag}: position {p} does not exist in {c.shortFileName()}"
                print(message)
                self._dump_position(p)
                raise ServerError(message)
    #@+node:ekr.20210209062536.1: *4* server._do_leo_command
    def _do_leo_command(self, action, package):
        """
        Execute the leo command given by package ["leo-command-name"].
        
        The client must open an outline before calling this method.
        """
        # We *can* require self.c to exist, because:
        # 1. all commands imply c.
        # 2. The client must call open_file to set self.c.
        tag = '_execute_leo_command'
        c = self._check_c()
        command_name = package.get("leo-command-name")
        if not command_name:  # pragma: no cover
            raise ServerError(f"{tag}: no 'leo-command-name' key in package")
        if command_name in self.bad_commands_list:  # pragma: no cover
            raise ServerError(f"{tag}: disallowed command: {command_name}")
        func = c.commandsDict.get(command_name)
        if not func:  # pragma: no cover
            raise ServerError(f"{tag}: Leo command not found: {command_name}")
        value = func(event={"c":c})
        return self._make_response({"return-value": value})
    #@+node:ekr.20210202110128.54: *4* server._do_message
    def _do_message(self, d):
        """
        Handle d, a python dict representing the incoming request.
        d must have at least the following keys:
        
        - "id": A positive integer.
        - "action": A string, which is either:
            - The name of public method of this class.
            - The name of a Leo command.
        
        Return a dict, created by _make_response, containing least these keys:

        - "id":         Same as the incoming id.
        - "action":     Same as the incoming action.
        - "commander":  A dict describing self.c.
        - "node":       None, or an archived position describing self.c.p.
        """
        tag = '_do_message'
        # Require "id" and "action" keys. The "package" key is optional.
        id_ = d.get("id")
        if id_ is None:  # pragma: no cover
            raise ServerError(f"{tag}: no id")
        action = d.get("action")
        if action is None:  # pragma: no cover
            raise ServerError("f{tag}: no action")
        package = d.get('package', {})
        # Set log flag.
        self.log_flag = package.get("log")
        # Set the current_id and action ivars for _make_response.
        self.current_id = id_
        self.action = action
        # Execute the requested action.
        if action == "execute-leo-command":
            func = self._do_leo_command
        else:
            func = self._do_server_command
        result = func(action, package)
        if result is None:  # pragma: no cover
            raise ServerError(f"{tag}: no response: {action}")
        return result
    #@+node:ekr.20210209085438.1: *4* server._do_server_command
    def _do_server_command(self, action, package):
        tag = '_do_server_command'
        # Disallow hidden methods.
        if action.startswith('_'):  # pragma: no cover
            raise ServerError(f"{tag}: action starts with '_': {action}")
        # Find and execute the server method.
        func = getattr(self, action, None)
        if not func:
            raise ServerError(f"{tag}: action not found: {action}")  # pragma: no cover
        if not callable(func):
            raise ServerError(f"{tag}: not callable: {func}")  # pragma: no cover
        return func(package)
    #@+node:ekr.20210211131707.1: *4* server._dump_*
    def _dump_outline(self, c):  # pragma: no cover
        """Dump the outline."""
        tag = '_dump_outline'
        print(f"{tag}: {c.shortFileName()}...\n")
        for p in c.all_positions():
            self._dump_position(p)
        print('')

    def _dump_position(self, p):  # pragma: no cover
        level_s = ' ' * 2 * p.level()
        print(f"{level_s}{p.childIndex():2} {p.v.gnx} {p.h}")
    #@+node:ekr.20210202110128.51: *4* server._es & helper
    def _es(self, s):  # pragma: no cover (tested in client).
        """
        Send a response that does not correspond to a request.
        
        The response *must* have an "async" key, but *not* an "id" key.
        """
        tag = '_es'
        message = g.toUnicode(s)
        package = {"async": "", "s": message}
        response = json.dumps(package, separators=(',', ':'))
        if self.loop:
            self.loop.create_task(self._async_output(response))
        else:
            print(f"{tag}: Error loop not ready {message}")
    #@+node:ekr.20210204145818.1: *5* server._async_output
    async def _async_output(self, json):  # pragma: no cover (tested in server)
        """Output json string to the web_socket"""
        tag = '_async_output'
        if self.web_socket:
            await self.web_socket.send(bytes(json, 'utf-8'))
        else:
            g.trace(f"{tag}: no web socket. json: {json}")
    #@+node:ekr.20210210081236.1: *4* server._get_p
    def _get_p(self, package):
        """Return _ap_to_p(package["ap"]) or c.p."""
        tag = '_get_ap'
        c = self.c
        if not c:  # pragma: no cover
            raise ServerError(f"{tag}: no c")
        ap = package.get("ap")
        if ap:
            p = self._ap_to_p(ap)
            if not p:  # pragma: no cover
                raise ServerError(f"{tag}: no p")
            if not c.positionExists(p):  # pragma: no cover
                raise ServerError(f"{tag}: position does not exist. ap: {ap}")
        if not c.p:  # pragma: no cover
            raise ServerError(f"{tag}: no c.p")
        return c.p
    #@+node:ekr.20210211053733.1: *4* server._get_position_d
    def _get_position_d(self, p):
        """
        Return a python dict containing:
        - "node": self._p_to_ap(p).
        - All *cheap* redraw data..
        
        Use get_ua to get p.ua *plus* all this redraw data.
        
        Note: v.computeIcon sets iconVal as follows:
            v, val = self, 0
            if v.hasBody(): val += 1
            if v.isMarked(): val += 2
            if v.isCloned(): val += 4
            if v.isDirty(): val += 8
        """
        return {
            "node": self._p_to_ap(p), # Contains p.gnx, p.childIndex and p.stack.
            # The cheap redraw data...
            "body-length": len(p.b),  # *Not* p.b.
            "has-children": p.hasChildren(),  # *Not* p.children().
            "has-ua": bool(p.v.u),  # *Not* p.v.u.
            "headline": p.h,
            "icon-val": p.v.iconVal,  # An int between 0 and 15.
            "is-at-file": p.isAnyAtFileNode(),
            "level": p.level(),  # Useful for debugging.
        }
    #@+node:ekr.20210206182638.1: *4* server._make_response
    def _make_response(self, package=None):
        """
        Return a json string representing a response dict.
        
        The 'package' kwarg, if present, must be a python dict describing a
        response. package may be an empty dict or None.
        
        The 'p' kwarg, if present, must be a position.
        
        First, this method creates a response (a python dict) containing all
        the keys in the 'package' dict, with the following added keys:
            
        - "id":         The incoming id.
        - "action":     The incoming action.
        - "commander":  A dict describing self.c.
        - "node":       None, or an archived position describing self.c.p.
        
        Finally, this method returns the json string corresponding to the
        response.
        """
        tag = '_make_response'
        c = self.c  # It is valid for c to be None.
        if package is None:
            package = {}
        p = package.get("p")
        if p:
            del package ["p"]
        # Raise an *internal* error if checks fail.
        if isinstance(package, str):  # pragma: no cover
            raise InternalServerError(f"{tag}: bad package kwarg: {package!r}")
        if p and not isinstance(p, Position):  # pragma: no cover
            raise InternalServerError(f"{tag}: bad p kwarg: {p!r}")
        if p and not c:  # pragma: no cover
            raise InternalServerError(f"{tag}: p but not c")
        if p and not c.positionExists(p):  # pragma: no cover
            raise InternalServerError(f"{tag}: p does not exist")
        if c and not c.p:  # pragma: no cover
            raise InternalServerError(f"{tag}: empty c.p")
        #
        # Always add these keys.
        package ["id"] = self.current_id
        package ["action"] = self.action
        # The following keys are relevant only if there is an open commander.
        if c:
            # Allow commands, especially _get_redraw_d, to specify p!
            p = p or c.p
            package ["commander"] = {
                "changed": c.isChanged(),
                "file_name": c.fileName(), # Can be None for new files.
            }
            # Add all the node data, including:
            # - "node": self._p_to_ap(p) # Contains p.gnx, p.childIndex and p.stack.
            # - All the *cheap* redraw data for p.
            redraw_d = self._get_position_d(p)
            for key, value in redraw_d.items():
                if key in package:  # pragma: no cover
                    raise InternalServerError(f"{tag}: key {key} in package: {package}")
                package [key] = value
        if self.log_flag:  # pragma: no cover
            g.printObj(package, tag=f"{tag} returns")
        return json.dumps(package, separators=(',', ':')) 
    #@+node:ekr.20210202110128.86: *4* server._p_to_ap
    def _p_to_ap(self, p):
        """
        Convert Leo position p to a serializable archived position.
        
        This returns only position-related data.
        get_position_data returns all data needed to redraw the screen.
        """
        self._check_c()
        stack = [{'gnx': v.gnx, 'childIndex': childIndex}
            for (v, childIndex) in p.stack]
        return {
            'childIndex': p._childIndex,
            'gnx': p.v.gnx,
            'stack': stack,
        }
    #@+node:ekr.20210202110128.84: *4* serverver._test_round_trip_positions
    def _test_round_trip_positions(self, c):  # pragma: no cover (tested in client).
        """Test the round tripping of p_to_ap and ap_to_p."""
        tag = '_test_round_trip_positions'
        for p in c.all_unique_positions():
            ap = self._p_to_ap(p)
            p2 = self._ap_to_p(ap)
            if p != p2:
                self._dump_outline(c)
                raise ServerError(f"{tag}: round-trip failed: ap: {ap}, p: {p}, p2: {p2}")
    #@-others
#@+node:ekr.20210208163018.1: ** class TestLeoServer (unittest.TestCase)
class TestLeoServer (unittest.TestCase):  # pragma: no cover
    """Tests of LeoServer class."""
    request_number = 0

    #@+others
    #@+node:ekr.20210211085544.1: *3* test: Setup and TearDown
    @classmethod
    def setUpClass(cls):
        # Assume we are running in the leo-editor directory.
        # pylint: disable=import-self
        import leo.core.leoserver as leoserver
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
            print('===== server did not terminate properly ====')
        except g_leoserver.TerminateServer:
            pass

    def setUp(self):
        global g_server
        self.server = g_server
        g.unitTesting = True
        
    def tearDown(self):
        g.unitTesting = False 
        
    #@+node:ekr.20210208171819.1: *3* test._request
    def _request(self, action, package=None):
        server = self.server
        self.request_number += 1
        log_flag = package.get("log")
        d = {
            "action": action,
            "id": self.request_number
        }
        if package:
            d ["package"] = package
        response = server._do_message(d)
        # _make_response calls json_dumps. Undo it with json.loads.
        answer = json.loads(response)
        if log_flag:
            g.printObj(answer, tag=f"response to {action}")
        return answer
    #@+node:ekr.20210210174801.1: *3* test.test_leo_commands
    def test_leo_commands (self):
        server = self.server
        table = [
            # Toggle mark twice.
            ("toggle-mark", {}),
            ("toggle-mark", {}),
        ]
        # First open a test file.
        server.open_file({"filename": "xyzzy.leo"})
        try:
            action = "execute-leo-command"
            for command_name, package in table:
                package ["leo-command-name"] = command_name
                self._request(action, package)
        finally:
            server.close_file({"filename": "xyzzy.leo"})
    #@+node:ekr.20210210102638.1: *3* test.test_most_public_server_methods
    def test_most_public_server_methods(self):
        server=self.server
        assert isinstance(server, g_leoserver.LeoServer), self.server
        test_dot_leo = g.os_path_finalize_join(g.app.loadDir, '..', 'test', 'test.leo')
        assert os.path.exists(test_dot_leo), repr(test_dot_leo)
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
            'tag_children',  
            # Other methods
            'delete_node', 'cut_node',  # dangerous.
            'click_button', 'get_buttons', 'remove_button',  # Require plugins.
            'save_file',  # way too dangerous!
            # 'set_selection',  ### Not ready yet.
            'open_file', 'close_file',  # Done by hand.
            'shut_down',  # Don't shut down the server.
        ]
        expected = ['error']
        package_d = {
            # "apply_config": {"config": {"whatever": True}},
            "get_focus": {"log": False},
            "set_body": {"body": "new body\n"},
            "set_headline": {"headline": "new headline"},
            "get_all_server_commands": {"log": False},
            "get_all_leo_commands": {"log": False},
        }
        # First open a test file & performa all tests.
        server.open_file({"filename": test_dot_leo})  # A real file.
        try:
            id_ = 0
            for method_name in methods:
                id_ += 1
                if method_name not in exclude:
                    assert getattr(server, method_name), method_name
                    package = package_d.get(method_name, {})
                    message = {
                        "id": id_,
                        "action": method_name,
                        "package": package,
                    }
                    try:
                        # Don't call the method directly.
                        # That would disable trace/verbose logic, checking, etc.
                        server._do_message(message)
                    except Exception as e:
                        if method_name not in expected:
                            print(f"Exception in test_most_public_server_methods: {method_name} {e}")
        finally:
            server.close_file({"filename": test_dot_leo})
    #@+node:ekr.20210208171319.1: *3* test.test_open_and_close
    def test_open_and_close(self):
        # server = self.server
        test_dot_leo = g.os_path_finalize_join(g.app.loadDir, '..', 'test', 'test.leo')
        assert os.path.exists(test_dot_leo), repr(test_dot_leo)
        log = False
        table = [
            # Open file.
            ("open_file", {"log": log, "filename": "xyzzy.leo"}),  # Does not exist.
            # Switch to the second file.
            ("open_file", {"log": log, "filename": test_dot_leo}),   # Does exist.
            # Open again. This should be valid.
            ("open_file", {"log": False, "filename": test_dot_leo}),
            # Better test of _ap_to_p.
            ("set_current_position", {
                "ap": {
                    "gnx": "ekr.20180311131424.1",  # Recent
                    "childIndex": 1,
                    "stack": [],
                }
            }),
            ("get_ua", {"log": log}),
            # Close the second file.
            ("close_file", {"log": log, }),
            # Close the first file.
            ("close_file", {"log": log, }),
        ]
        for action, package in table:
            self._request(action, package)
    #@+node:ekr.20210212093613.1: *3* test.test_find_commands
    def test_find_commands(self):
        
        tag = 'test_find_commands'
        test_dot_leo = g.os_path_finalize_join(g.app.loadDir, '..', 'test', 'test.leo')
        assert os.path.exists(test_dot_leo), repr(test_dot_leo)
        log = False
        # Open the file & create the StringFindTabManager.
        self._request("open_file", {"log": False, "filename": test_dot_leo})
        #
        # Batch find commands: The answer is a count of found nodes.
        for method in ('find_all', 'clone_find_all', 'clone_find_all_flattened'):
            answer = self._request(method, {"log": log, "find_text": "def"})
            if log: g.printObj(answer, tag=f"{tag}:{method}: answer")
        #
        # Find commands that may select text: The answer is (p, pos, newpos).
        for method in ('find_next', 'find_previous', 'find_def', 'find_var'):
            answer = self._request(method, {"log": log, "find_text": "def"})
            if log: g.printObj(answer, tag=f"{tag}:{method}: answer")
        #
        # Change commands: The answer is a count of changed nodes.
        for method in ('change_all', 'change_then_find'):
            answer = self._request(method, {"log": log, "find_text": "def", "change_text": "DEF"})
            if log: g.printObj(answer, tag=f"{tag}:{method}: answer")
        #
        # Tag commands. Why they are in leoFind.py??
        for method in ('clone_find_tag', 'tag_children'):
            answer = self._request(method, {"log": log, "tag": "my-tag"})
            if log: g.printObj(answer, tag=f"{tag}:{method}: answer")
       
    #@-others
#@+node:ekr.20210202110128.88: ** function: main & helpers
def main():  # pragma: no cover (tested in client)
    """python script for leo integration via leoBridge"""
    # from leo.core import leoGlobals as g
    global wsHost, wsPort
    print("Starting LeoBridge... (Launch with -h for help)")
    # replace default host address and port if provided as arguments
    #@+others
    #@+node:ekr.20210202110128.90: *3* function: ws_handler (server)
    async def ws_handler(websocket, path):
        """
        The web socket handler: server.ws_server.

        It must be a coroutine accepting two arguments: a WebSocketServerProtocol and the request URI.
        """
        tag = 'server'
        trace = True
        verbose = False
        try:
            controller._init_connection(websocket)
            # Start by sending empty as 'ok'.
            n = 0
            async_n = 0
            await websocket.send(controller._make_response())
            # controller._sign_on()
            async for json_message in websocket:
                try:
                    n += 1
                    d = None
                    trace = True  ## controller.trace
                    d = json.loads(json_message)
                    if trace and verbose:
                        print(f"{tag}: got: {d}")
                    elif trace:
                        print(f"{tag}: got: {d.get('action')}")
                    answer = controller._do_message(d)
                except TerminateServer as e:
                    raise websockets.exceptions.ConnectionClosed(code=1000, reason=e)
                except ServerError as e:
                    data = f"{d}" if d else f"json syntax error: {json_message!r}"
                    error = f"{tag}:  ServerError: {e}...\n{tag}:  {data}"
                    print("")
                    print(error)
                    print("")
                    package = {
                        "id": controller.current_id,
                        "action": controller.action,
                        "request": data,
                        "ServerError": f"{e}",
                    }  
                    answer = json.dumps(package, separators=(',', ':'))
                except InternalServerError as e:  # pragma: no cover
                    print(f"{tag}: InternalServerError {e}")
                    break
                except Exception as e:  # pragma: no cover
                    print(f"{tag}: Unexpected Exception! {e}")
                    g.printObj(package, tag=f"message: {d}")
                    g.print_exception()
                    break
                await websocket.send(answer)
                if n in (3, 4, 7, 10):
                    async_n += 1
                    controller._es(f"async message {async_n}")
        except websockets.exceptions.ConnectionClosedError as e:  # pragma: no cover
            print(f"{tag}: closed error: {e}")
        except websockets.exceptions.ConnectionClosed as e:
            print(f"{tag}: closed normally: {e}")
        # Don't call EventLoop.stop(). It terminates abnormally.
            # asyncio.get_event_loop().stop()
    #@+node:ekr.20210202110128.91: *3* function: get_args
    def get_args():  # pragma: no cover
        global wsHost, wsPort
        args = None
        try:
            opts, args = getopt.getopt(sys.argv[1:], "help:", ["help", "address=", "port="])
        except getopt.GetoptError:
            print('leobridgeserver.py -a <address> -p <port>')
            print('defaults to localhost on port 32125')
            if args:
                print("unused args: " + str(args))
            sys.exit(2)
        for opt, arg in opts:
            if opt in ("-h", "--help"):
                print('leobridgeserver.py -a <address> -p <port> -u')
                print('defaults to localhost on port 32125')
                sys.exit()
            elif opt in ("-a", "--address"):
                wsHost = arg
            elif opt in ("-p", "--port"):
                wsPort = arg
        # Leave other options for unittest.
        for opt, junk in opts:  # opts is a 2-tuple.
            if opt in sys.argv:
                sys.argv.remove(opt)
        return wsHost, wsPort
    #@-others
    if '--unittest' in sys.argv:
        sys.argv.remove('--unittest')
        unittest.main()
        return  # Make *sure* we don't start the server.
    wsHost, wsPort = get_args()
    signon = f"LeoBridge started at {wsHost} on port: {wsPort}. Ctrl+c to break"
    print(signon)
    # Open leoBridge.
    controller = LeoServer()
    # Start the server.
    loop = asyncio.get_event_loop()  
    server = websockets.serve(ws_handler=ws_handler, host=wsHost, port=wsPort)
    loop.run_until_complete(server)
    loop.run_forever()
#@-others
if __name__ == '__main__':
    # pytest will *not* execute this code.
    try:
        main()
    except KeyboardInterrupt:
        print("\nKeyboard Interupt: Stopping leoserver.py")
        sys.exit()
#@-leo

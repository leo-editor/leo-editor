#@+leo-ver=5-thin
#@+node:ekr.20210202110128.1: * @file  leoserver.py
#@@language python
#@@tabwidth -4
"""
A language-agnostic server for Leo's bridge,
based on leoInteg's leobridgeserver.py.
"""
#@+<< imports >>
#@+node:ekr.20210202110128.2: ** << imports >>
import asyncio
import getopt
import json
# import os.path
import sys
import time
# Third-party.
import websockets
# Leo
import leo.core.leoApp as leoApp
import leo.core.leoBridge as leoBridge
import leo.core.leoNodes as leoNodes
import leo.core.leoExternalFiles as leoExternalFiles
import leo.core.leoFrame as leoFrame
#@-<< imports >>
g = None  # The bridge's leoGlobals module.

# server defaults
wsHost = "localhost"
wsPort = 32125
commonActions = ["getChildren", "getBody", "getBodyLength"]
#@+others
#@+node:ekr.20210204054519.1: ** Exception classes
class ServerError(Exception):
    """The server received a package containing missing or erroneous contents."""
    pass

class TerminateServer(Exception):
    """Ask the server to terminate."""
    pass
#@+node:ekr.20210202110128.29: ** class ServerController
class ServerController:
    """Leo Bridge Controller"""
    #@+others
    #@+node:ekr.20210202160349.1: *3* sc:Birth & startup
    #@+node:ekr.20210202110128.30: *4* sc.__init__ (load bridge, set self.g)
    def __init__(self):
        ### TODO : @boltex #74 need gnx_to_vnode for each opened file/commander
        global g
        t1 = time.process_time()
        #
        # Init ivars first.
        self.c = None  # Currently Selected Commander.
        self.config = None
        self.current_id = 0  # Id of action being processed.
        self.gnx_to_vnode = []  # See leoflexx.py in leoPluginsRef.leo
        self.loop = None
        self.trace = False
        self.web_socket = None
        #
        # Start the bridge.
        self.bridge = leoBridge.controller(
            gui='nullGui',
            loadPlugins=False,   # True: attempt to load plugins.
            readSettings=False,  # True: read standard settings files.
            silent=False,        # True: don't print signon messages.
            verbose=False,       # True: prints messages that would be sent to the log pane.
        )
        g = self.bridge.globals()
        #
        # Complete the initialization, as in LeoApp.initApp.
        g.app.idleTimeManager = leoApp.IdleTimeManager()
        g.app.idleTimeManager.start()
        g.app.externalFilesController = leoExternalFiles.ExternalFilesController(None)
        t2 = time.process_time()
        print(f"ServerController: init leoBridge in {t2-t1:4.2} sec.")
    #@+node:ekr.20210202110128.51: *4* sc._es & helpers (**test**)
    def _es(self, s):
        """Output to the Log Pane"""
        self._send_async_output({
            "async": "",
            "s": g.toUnicode(s),
        })
    #@+node:ekr.20210202110128.39: *5* sc._send_async_output
    def _send_async_output(self, package):
        tag = '_send_async_output'
        assert "async" in package, repr(package)
        response = json.dumps(package, separators=(',', ':'))
        if self.loop:
            self.loop.create_task(self._async_output(response))
        else:
            print(f"{tag}: Error loop not ready {response}")
    #@+node:ekr.20210204145818.1: *5* sc._async_output
    async def _async_output(self, json):
        """Output json string to the web_socket"""
        tag = '_async_output'
        if self.web_socket:
            await self.web_socket.send(bytes(json, 'utf-8'))
        else:
            g.trace(f"{tag} no web socket. json: {json}", flush=True)
    #@+node:ekr.20210202110128.42: *4* sc._sign_on
    def _sign_on(self):
        """Simulate the initial Leo Log Entry"""
        if self.loop:
            g.app.computeSignon()
            self._es(g.app.signon)
            self._es(g.app.signon1)
        else:
            print('sign_on: no loop', flush=True)
    #@+node:ekr.20210202110128.41: *4* sc.apply_config
    def apply_config(self, package):
        """Got the configuration from client"""
        tag = 'apply_config'
        config = package.get('config')
        if not config:
            raise ServerError(f"{tag}: no config")
        self.config = config
        return self._make_response("")  # Send empty as 'ok'
    #@+node:ekr.20210202110128.52: *4* sc.init_connection
    def _init_connection(self, web_socket):
        """Begin the connection."""
        self.web_socket = web_socket
        self.loop = asyncio.get_event_loop()

    #@+node:ekr.20210204154548.1: *3* sc:Command utils
    #@+node:ekr.20210203084135.1: *4* sc._check_ap
    def _check_ap(self, package):
        """
        Resolve archived position to a position.
        Return p, or raise ServerError.
        """
        c = self.c
        callers = g.callers().split(',')
        tag = callers[-1]
        ap = package.get('archived_position')
        if not ap:
            raise ServerError(f"{tag}: no archived_position")
        p = self._ap_to_p(ap)
        if not p:
            raise ServerError(f"{tag}: position not found")
        if not c.positionExists(p):
            raise ServerError(f"{tag}: position does not exist. ap: {ap}")
        return p
    #@+node:ekr.20210202110128.54: *4* sc._do_message & helpers
    def _do_message(self, d):
        """
        Handle d, a python dict representing the incoming request.
        
        The request will call either:
        - A named method in Leo's Commands class or any subcommander class.
        - A named Leo command.
        """
        tag = '_do_message'
        id_ = d.get('id')
        if id_ is None:
            raise ServerError(f"{tag}: no id")
        # Set the id.
        self.current_id = id_
        # The package is optional.
        package = d.get('package', {})
        method_name = d.get('action')
        result = self._do_method_by_name(method_name, package)
        # Ensure the result is a json-formatted string.
        if result is None:
            result = self._make_response("")
        return result
    #@+node:ekr.20210204095743.1: *5* sc._do_method_by_name
    def _do_method_by_name(self, method_name, package):
        """Execute one of Leo's methods by name."""
        tag = '_do_method_by_name'
        # For now, disallow hidden methods.
        if method_name.startswith('_'):
            raise ServerError(f"{tag}: method name starts with '_': {method_name!r}")
        func = getattr(self, method_name, None)
        if func:
            return func(package)
        raise ServerError(f"{tag}: method not found: {method_name!r}")
    #@+node:ekr.20210202110128.81: *4* sc._gnx_to_p
    def _gnx_to_p(self, gnx):
        """Return first p node with this gnx or None"""
        for p in self.c.all_unique_positions():
            if p.v.gnx == gnx:
                return p
        return None

    #@+node:ekr.20210204154318.2: *4* sc._make_position_list_response
    def _make_position_list_response(self, position_list):
        return self._make_response(
            "archived-position-list",
            [self._p_to_ap(p) for p in position_list],
        )
    #@+node:ekr.20210204154318.1: *4* sc._make_position_response
    def _make_position_response(self, p):
        return self._make_response(
            "archived-position",
            self._p_to_ap(p) if p else None,
        )

    #@+node:ekr.20210204154315.1: *4* sc._make_response
    def _make_response(self, key, any=None):
        """
        Return a json string corresponding to a package dictionary.
        An empty key ("") is allowed.
        """
        package = {
            "id": self.current_id,
        }
        if key:
            assert isinstance(key, str), repr(key)
            package [key] = any or ""
        return json.dumps(package, separators=(',', ':')) 

    #@+node:ekr.20210202193210.1: *3* sc:Commands
    #@+node:ekr.20210202193709.1: *4* sc:button commands
    #@+node:ekr.20210202183724.4: *5* sc.click_button
    def click_button(self, package):
        """Handles buttons clicked in client from the '@button' panel"""
        c = self.c
        index = package['index']
        d = c.theScriptingController.buttonsDict
        button = None
        for key in d:
            if(str(key) == index):
                button = key
        if button:
            try:
                button.command()
            except Exception():
                pass
        return self._make_position_response(c.p)
    #@+node:ekr.20210202183724.2: *5* sc.get_buttons
    def get_buttons(self, package):
        """Gets the currently opened file's @buttons list"""
        c = self.c
        buttons = []
        if c and c.theScriptingController and c.theScriptingController.buttonsDict:
            d = c.theScriptingController.buttonsDict
            for key in d:
                entry = {"name": d[key], "index": str(key)}
                buttons.append(entry)
        return self._make_response("buttons", buttons)

    #@+node:ekr.20210202183724.3: *5* sc.remove_button
    def remove_button(self, package):
        """Removes an entry from the buttonsDict by index string"""
        c, d = self.c, self.c.theScriptingController.buttonsDict
        index = package['index']
        if index in d:
            del d[index]
        return self._make_position_response(c.p)
    #@+node:ekr.20210202193642.1: *4* sc:file commands
    #@+node:ekr.20210202110128.57: *5* sc.open_file
    def open_file(self, package):
        """
        Open a leo file with the given filename. Create a new document if no name.
        """
        c, found, tag = None, False, 'open_file'
        openCommanders = [z for z in g.app.commanders() if not c.closed]
        filename = package.get('filename')  # Optional.
        if filename:
            for c in openCommanders:
                if c.fileName() == filename:
                    found = True
        if not found:
            c = self.bridge.openLeoFile(filename)
        if not c:
            raise ServerError(f"{tag}: can not open {filename!r}")
        # Assign self.c
        self.c = c
        c.closed = False  # Mark as open *in the server*.
        if not found:
            c.frame.body.wrapper = leoFrame.StringTextWrapper(c, 'bodyWrapper')
            c.selectPosition(c.p)
        self._create_gnx_to_vnode()
        result = {
            "filename": c.fileName(),
            "node": self._p_to_ap(c.p),
            "total": len(g.app.commanders),
        }
        return self._make_response("opened", result)
    #@+node:ekr.20210202110128.58: *5* sc.close_file
    def close_file(self, package):
        """
        Closes a leo file. A file can then be opened with "open_file"
        Returns an object that contains a 'closed' member
        """
        c = self.c
        ### To do: Support multiple opened files
        if c:
            if package["forced"] and c.changed:
                # return "no" g.app.gui.runAskYesNoDialog  and g.app.gui.runAskYesNoCancelDialog
                c.revert()
            if package["forced"] or not c.changed:
                c.closed = True
                c.close()
            else:
                # Cannot close immediately. Ask to save, ignore or cancel
                return self._make_response('closed', {"closed": 0})
        # Select the first open commander.
        openCommanders = [z for z in g.app.commanders() if not z.closed]
        if not openCommanders:
            return self._make_response("closed", {"total": 0})
        self.c = openCommanders[0]
        self._create_gnx_to_vnode()
        result = {
            "filename": c.fileName(),
            "node": self._p_to_ap(self.c.p),
            "total": len(openCommanders),
        }
        return self._make_response("closed", result)
    #@+node:ekr.20210202183724.1: *5* sc.save_file
    def save_file(self, package):
        """Saves the leo file. New or dirty derived files are rewritten"""
        c = self.c
        if c:
            try:
                if "text" in package:
                    c.save(fileName=package['text'])
                else:
                    c.save()
            except Exception as e:
                g.trace('Error while saving')
                print("Error while saving", flush=True)
                print(e, flush=True)
        return self._make_response("")  # Send empty as 'ok'
    #@+node:ekr.20210202193505.1: *4* sc:getter commands
    #@+node:ekr.20210202183724.5: *5* sc.get_all_commands & helpers
    def get_all_commands(self, package):
        """Return a list of all Leo commands that make sense in leoInteg."""
        c = self.c
        d = c.commandsDict  # keys are command names, values are functions.
        bad_names = self._bad_commands()  # #92.
        good_names = self._good_commands()
        duplicates = set(bad_names).intersection(set(good_names))
        if duplicates:
            print('duplicate command names...', flush=True)
            for z in sorted(duplicates):
                print(z)
        result = []
        for command_name in sorted(d):
            func = d.get(command_name)
            if not func:
                print('no func:', command_name, flush=True)
                continue
            if command_name in bad_names:  # #92.
                continue
            # Prefer func.__func_name__ to func.__name__: Leo's decorators change func.__name__!
            func_name = getattr(func, '__func_name__', func.__name__)
            if not func_name:
                print('no name', command_name, flush=True)
                continue
            doc = func.__doc__ or ''
            result.append({
                "label": command_name,
                "func":  func_name,
                "detail": doc,
            })
        return self._make_response("commands", result)
    #@+node:ekr.20210202183724.6: *6* sc._bad_commands
    def _bad_commands(self):
        """Return the list of Leo's command names that leoInteg should ignore."""
        c = self.c
        bad = []
        d = c.commandsDict  # keys are command names, values are functions.
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

    #@+node:ekr.20210202183724.7: *6* sc._good_commands
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
            'reload-all-settings',
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

    #@+node:ekr.20210202110128.71: *5* sc.get_all_gnxs
    def get_all_gnxs(self, package):
        """Get gnx array from all unique nodes"""
        c = self.c
        result = [p.v.gnx for p in c.all_unique_positions(copy=False)]
        return self._make_response("allGnx", result)

    #@+node:ekr.20210202110128.55: *5* sc.get_all_opened_files
    def get_all_opened_files(self, package):
        """Return array of opened file path/names to be used as open_file parameters to switch files"""
        c = self.c
        openCommanders = [z for z in g.app.commanders() if not z.closed]
        files = [
            {
                "changed": commander.changed,
                "name": commander.mFileName,
                "selected": c == commander,
            } for commander in openCommanders
        ]
        # Removed 'index entries from result and files. They appear to be useless.
        result = {
            "files": files,
        }
        return self._make_response("openedFiles", result)
    #@+node:ekr.20210202110128.72: *5* sc.get_body
    def get_body(self, package):
        """EMIT OUT body of a node"""
        ###
        # TODO: if not found, send code to prevent unresolved promise
        #       if 'document switch' occurred shortly before
        gnx = package.get('gnx')
        if gnx:
            v = self.c.fileCommands.gnxDict.get(gnx)  # vitalije
            if v:
                return self._make_response("bodyData", v.b)
        #
        # Send as empty to fix unresolved promise if 'document switch' occurred shortly before
        return self._make_response("bodyData", "")

    #@+node:ekr.20210202110128.73: *5* sc.get_body_length
    def get_body_length(self, package):
        """EMIT OUT body string length of a node"""
        tag = 'get_body_length'
        gnx = package.get('gnx')
        if not gnx:
            raise ServerError(f"{tag}: no gnx")
        v = self.c.fileCommands.gnxDict.get(gnx)  # vitalije
        if not v:
            raise ServerError(f"{tag}: gnx not found: {gnx!r}")
        return self._make_response("bodyLength", len(v.b))
    #@+node:ekr.20210202110128.66: *5* sc.get_body_states
    def get_body_states(self, package):
        """
        Finds the language in effect at top of body for position p,
        Also returns the saved cursor position from last time node was accessed.
        """
        c, wrapper = self.c, self.c.frame.body.wrapper
        p = self._check_ap(package)
        defaultPosition = {"line": 0, "col": 0}
        states = {
            'language': 'plain',
            # See BodySelectionInfo interface in types.d.ts
            'selection': {
                "gnx": p.v.gnx,
                "scroll": {
                    "start": defaultPosition,
                    "end": defaultPosition
                },
                "active": defaultPosition,
                "start": defaultPosition,
                "end": defaultPosition
            }
        }
        aList = g.get_directives_dict_list(p)
        d = g.scanAtCommentAndAtLanguageDirectives(aList)
        language = (
            d and d.get('language') or
            g.getLanguageFromAncestorAtFileNode(p) or
            c.config.getString('target-language') or
            'plain'
        )
        scroll = p.v.scrollBarSpot
        active = p.v.insertSpot
        start = p.v.selectionStart
        end = p.v.selectionStart + p.v.selectionLength
        # get selection from wrapper instead if its the selected node
        if c.p.v.gnx == p.v.gnx:
            # print("in GBS -> SAME AS c.p SO USING FROM WRAPPER")
            active = wrapper.getInsertPoint()
            start, end = wrapper.getSelectionRange(True)
            scroll = wrapper.getYScrollPosition()

        # TODO : This conversion for scroll position may be unneeded (consider as lines only)
        # scrollI, scrollRow, scrollCol = c.frame.body.wrapper.toPythonIndexRowCol(Scroll)
        # compute line and column for the insertion point, and the start & end of selection
        activeI, activeRow, activeCol = c.frame.body.wrapper.toPythonIndexRowCol(active)
        startI, startRow, startCol = c.frame.body.wrapper.toPythonIndexRowCol(start)
        endI, endRow, endCol = c.frame.body.wrapper.toPythonIndexRowCol(end)
        states = {
            'language': language.lower(),
            'selection': {
                "gnx": p.v.gnx,
                "scroll": scroll,  # scroll was kept as-is
                "active": {"line": activeRow, "col": activeCol},
                "start": {"line": startRow, "col": startCol},
                "end": {"line": endRow, "col": endCol}
            }
        }
        return self._make_response("bodyStates", states)
    #@+node:ekr.20210202110128.68: *5* sc.get_children
    def get_children(self, package):
        """EMIT OUT list of children of a node"""
        c = self.c
        ap = package.get('ap')
        if ap:
            p = self._ap_to_p(ap)
            nodes = p and p.children() or []
        elif c.hoistStack:
            nodes = [c.hoistStack[-1].p]
        else:
            # Output all top-level nodes.
            nodes = [z for z in c.rootPosition().self_and_siblings()]
        return self._make_position_list_response(nodes)
    #@+node:ekr.20210202110128.69: *5* sc.get_parent
    def get_parent(self, package):
        """EMIT OUT the parent of a node, as an array, even if unique or empty"""
        tag = 'get_parent'
        ap = package.get('ap')
        if not ap:
            raise ServerError(f"{tag}: no ap")
        p = self._ap_to_p(ap)
        if not p:
            raise ServerError(f"{tag}: position not found")
        return self._make_position_response(p.getParent())
    #@+node:ekr.20210202110128.67: *5* sc.get_selected_position
    def get_position(self, package):
        """EMIT OUT a node, don't select it"""
        return self._make_position_response(self.c.p)
    #@+node:ekr.20210202110128.61: *5* sc.get_ui_states
    def get_ui_states(self, package):
        """
        Gets the currently opened file's general states for UI enabled/disabled states
        such as undo available, file changed/unchanged
        """
        c, tag = self.c, 'get_ui_states'
        # Set the defaults.
        states = {
            "changed": False,
            "canUndo": False,
            "canRedo": False,
            "canDemote": False,
            "canPromote": False,
            "canDehoist": False,
        }
        if c:
            try:
                states["changed"] = c.changed
                states["canUndo"] = c.canUndo()
                states["canRedo"] = c.canRedo()
                states["canDemote"] = c.canDemote()
                states["canPromote"] = c.canPromote()
                states["canDehoist"] = c.canDehoist()
            except Exception as e:
                raise ServerError(f"{tag}: Exception setting state: {e}")
        return self._make_response("states", states)
    #@+node:ekr.20210202193540.1: *4* sc:node commands (setters)
    #@+node:ekr.20210202183724.11: *5* sc.clone_node
    def clone_node(self, package):
        """Clone a node"""
        c = self.c
        p = self._check_ap(package)
        c.selectPosition(p)
        c.clone()
        return self._make_position_response(c.p)
    #@+node:ekr.20210202110128.79: *5* sc.collapse_node
    def collapse_node(self, package):
        """Collapse a node"""
        p = self._check_ap(package)
        p.contract()
        return self._make_response("")  # Just send empty as 'ok'
    #@+node:ekr.20210202183724.12: *5* sc.cut_node
    def cut_node(self, package):
        """Cut a node, return the newly-selected node."""
        c = self.c
        p = self._check_ap(package)
        c.selectPosition(p)
        c.cutOutline()
        return self._make_position_response(c.p)
    #@+node:ekr.20210202183724.13: *5* sc.delete_node
    def delete_node(self, package):
        """Delete a node. Return the newly-selected node."""
        c = self.c
        p = self._check_ap(package)
        c.selectPosition(p)
        c.deleteOutline()  # Handles undo.
        return self._make_position_response(c.p)
    #@+node:ekr.20210202110128.78: *5* sc.expand_node
    def expand_node(self, package):
        """Expand a node"""
        p = self._check_ap(package)
        p.expand()
        return self._make_response("")  # Just send empty as 'ok'
    #@+node:ekr.20210202183724.15: *5* sc.insert_node
    def insert_node(self, package):
        """Insert a node after the given node, set its headline and select it."""
        c, tag = self.c, 'insert_node'
        p = self._check_ap(package)
        h = package.get('headline')
        if not h:
            raise ServerError(f"{tag}: no headline")
        c.selectPosition(p)
        p2 = c.insertHeadline()  # Handles undo.
        return self._make_position_response(p2)
    #@+node:ekr.20210202183724.9: *5* sc.mark_node
    def mark_node(self, package):
        """Mark a node, but don't select it."""
        p = self._check_ap(package)
        p.setMarked()
        return self._make_position_response(self.c.p)
    #@+node:ekr.20210202183724.17: *5* sc.redo
    def redo(self, package):
        """Undo last un-doable operation"""
        c, u = self.c, self.c.undoer
        if u.canRedo():
            u.redo()
        return self._make_position_response(c.p)
    #@+node:ekr.20210202110128.74: *5* sc.set_body
    def set_body(self, package):
        """Change Body text of a node"""
        c, u, tag = self.c, self.c.undoer, 'set_body'
        gnx = package['gnx']
        if not gnx:
            raise ServerError(f"{tag}: no gnx")
        v = c.fileCommands.gnxDict.get(gnx)  # vitalije
        if not v:
            raise ServerError(f"{tag}: gnx not found: {gnx!r}")
        # Set the body once.
        body = package.get('body') or ""
        v.b = body
        for p in self.c.all_positions():
            if p.v.gnx == gnx:
                # TODO : Before setting undo and trying to set body, first check if different than existing body
                bunch = u.beforeChangeNodeContents(p)
                p.v.setBodyString(body)
                u.afterChangeNodeContents(
                    p, "Body Text", bunch)
                if self.c.p.v.gnx == gnx:
                    c.frame.body.wrapper.setAllText(body)
                if not self.c.isChanged():
                    c.setChanged()
                if not p.v.isDirty():
                    p.setDirty()
                break
        return self._make_position_response(c.p)

    #@+node:ekr.20210202110128.76: *5* sc.set_headline
    def set_headline(self, package):
        """Change a node's headline."""
        tag = 'set_headline'
        u = self.c.undoer
        p = self._check_ap(package)
        h = package.get('headline')
        if not h:
            raise ServerError(f"{tag}: no headline")
        bunch = u.beforeChangeNodeContents(p)
        p.h = h
        u.afterChangeNodeContents(p, 'Change Headline', bunch)
        return self._make_position_response(p)
    #@+node:ekr.20210202110128.77: *5* sc.set_current_position
    def set_current_position(self, package):
        """Select a node, or the first one found with its GNX"""
        c = self.c
        p = self._check_ap(package)  # p is guaranteed to exist.
        c.selectPosition(p)
        return self._make_position_response(c.p)
    #@+node:ekr.20210202110128.75: *5* sc.set_selection
    def set_selection(self, package):
        """
        Given package['gnx'], selection.
        Set the selection in the wrapper if c.p.gnx == gnx.
        """
        c, wrapper, tag = self.c, self.c.frame.body.wrapper, 'set_selection'
        gnx = package.get('gnx')
        if not gnx:
            raise ServerError(f"{tag}: no gnx")
        v = c.fileCommands.gnxDict.get(gnx)
        if not v:
            raise ServerError(f"{tag}: gnx not found. gnx: {gnx!r}")
        start = package.get('start', 0)
        end = package.get('end', 0)
        insert = package.get('insert', 0)
        scroll = package.get('scroll', 0)
        if gnx == c.p.v.gnx:
            wrapper.setSelectionRange(start, end, insert)
            wrapper.setYScrollPosition(scroll)
        # Always set vnode attrs.
        v.scrollBarSpot = scroll
        v.insertSpot = insert
        v.selectionStart = start
        v.selectionLength = abs(start - end)
        return self._make_position_response(c.p)
    #@+node:ekr.20210202183724.16: *5* sc.undo
    def undo(self, package):
        """Undo last un-doable operation"""
        c, u = self.c, self.c.undoer
        if u.canUndo():
            u.undo()
        return self._make_position_response(c.p)
    #@+node:ekr.20210202183724.10: *5* sc.unmark_node
    def unmark_node(self, package):
        """Unmark a node, don't select it"""
        p = self._check_ap(package)
        p.clearMarked()
        return self._make_position_response(self.c.p)
    #@+node:ekr.20210205102806.1: *4* sc:test commands
    #@+node:ekr.20210205102818.1: *5* sc.error
    def error(self, package):
        """For unit testing. Raise ServerError"""
        raise ServerError("sc.error called. package: {package}")
    #@+node:ekr.20210205103759.1: *5* sc.shut_down
    def shut_down(self, package):
        """Shut down the server."""
        raise TerminateServer(f"client requested shut down")
    #@+node:ekr.20210205111421.1: *5* sc.set/clear_trace
    def clear_trace(self, package):
        self.trace = False
        
    def set_trace(self, package):
        self.trace = True
    #@+node:ekr.20210202110128.60: *5* sc.test
    def test(self, package):
        """Do-nothing test function for debugging"""
        return self._make_response('test-result', package)
    #@+node:ekr.20210202193334.1: *3* sc:Serialization
    #@+node:ekr.20210202110128.85: *4* sc._ap_to_p
    def _ap_to_p(self, ap):
        """
        (From Leo plugin leoflexx.py) Convert an archived position to a true Leo position.
        Return None if no key
        """
        childIndex = ap['childIndex']
        try:
            v = self.gnx_to_vnode[ap['gnx']]  # Trap this
            stack = [
                (self.gnx_to_vnode[d['gnx']], d['childIndex'])
                    for d in ap['stack']
            ]
        except Exception:
            return None
        return leoNodes.position(v, childIndex, stack)
    #@+node:ekr.20210202110128.83: *4* sc._create_gnx_to_vnode
    def _create_gnx_to_vnode(self):
        """Make the first gnx_to_vnode array with all unique nodes"""
        self.gnx_to_vnode = {
            v.gnx: v for v in self.c.all_unique_nodes()
        }
        self._test_round_trip_positions()
    #@+node:ekr.20210202110128.86: *4* sc._p_to_ap
    def _p_to_ap(self, p):
        """(From Leo plugin leoflexx.py) Converts Leo position to a serializable archived position."""
        c, v = self.c, p.v
        if not v:
            print(f"ServerController.p_to_ap: no v for position {p!r}", flush=True)
            assert False
        # Expand gnx-vnode translation table for any new node encountered
        if v.gnx not in self.gnx_to_vnode:
            self.gnx_to_vnode[v.gnx] = v
        # Necessary properties for outline.
        ap = {
            'childIndex': p._childIndex,
            'gnx': v.gnx,
            'headline': p.h,
            'level': p.level(),
            'stack': [
                {
                    'gnx': stack_v.gnx,
                    'childIndex': stack_childIndex,
                    'headline': stack_v.h,
                } for (stack_v, stack_childIndex) in p.stack
            ],
        }
        if v.u:
            ap['u'] = v.u
        # EKR: No need to use a 'status' flag for now.
        table = (
            (p.isAnyAtFileNode(), 'atFile'),
            (p.b, 'hasBody'),
            (p == c.p, 'selected'),
        )
        for cond, attr in table:
            if cond: ap [attr] = True
        for attr in ('cloned', 'dirty', 'expanded', 'hasChildren','marked'):
            func = getattr(p, attr)
            if func(): ap [attr] = True
        return ap
        ###
            # if bool(p.b):
                # ap['hasBody'] = True
            # if p.isAnyAtFileNode():
                # ap['atFile'] = True
            # if p == self.c.p:
                # ap['selected'] = True
            # if p.hasChildren():
                # ap['hasChildren'] = True
            # if p.isCloned():
                # ap['cloned'] = True
            # if p.isDirty():
                # ap['dirty'] = True
            # if p.isExpanded():
                # ap['expanded'] = True
            # if p.isMarked():
                # ap['marked'] = True
    #@+node:ekr.20210202110128.84: *4* sc._test_round_trip_positions
    def _test_round_trip_positions(self):
        """(From Leo plugin leoflexx.py) Test the round tripping of p_to_ap and ap_to_p."""
        # Careful: p_to_ap updates app.gnx_to_vnode. Save and restore it.
        old_d = self.gnx_to_vnode.copy()
        old_len = len(list(self.gnx_to_vnode.keys()))
        for p in self.c.all_positions():
            ap = self._p_to_ap(p)
            p2 = self._ap_to_p(ap)
            assert p == p2, (repr(p), repr(p2), repr(ap))
        gnx_to_vnode = old_d  # Required!
        new_len = len(list(gnx_to_vnode.keys()))
        assert old_len == new_len, (old_len, new_len)
    #@-others
#@+node:ekr.20210202110128.88: ** function:main & helpers
def main():
    """python script for leo integration via leoBridge"""
    # from leo.core import leoGlobals as g
    global wsHost, wsPort
    print("Starting LeoBridge... (Launch with -h for help)", flush=True)
    # replace default host address and port if provided as arguments
    #@+others
    #@+node:ekr.20210202110128.90: *3* function: ws_handler
    async def ws_handler(websocket, path):
        """
        The web socket handler: server.ws_server.

        It must be a coroutine accepting two arguments: a WebSocketServerProtocol and the request URI.
        """
        tag = 'server'
        try:
            controller._init_connection(websocket)
            # Start by sending empty as 'ok'.
            await websocket.send(controller._make_response(""))
            controller._sign_on()
            async for json_message in websocket:
                d = None
                try:
                    d = json.loads(json_message)
                    if controller.trace:
                        print(f"{tag}: got id: {d.get('id')} action: {d.get('action')}", flush=True)
                    answer = controller._do_message(d)
                except TerminateServer as e:
                    # print(f"{tag}: TerminateServer: {e}", flush=True)
                    raise websockets.exceptions.ConnectionClosed(code=1000, reason=e)
                except Exception as e:
                    # Continue on all errors.
                    data = f"request: {d!r}" if d else f"bad request: {json_message!r}"
                    error = f"{tag}: {e}.\n{tag}: {data}"
                    print(error, flush=True)
                    # g.print_exception()  # Always flushes.
                    answer = {
                        "id": controller.current_id,
                        "error": error,
                    }
                await websocket.send(answer)
        except websockets.exceptions.ConnectionClosedError as e:
            print(f"{tag}: closed error: {e}", flush=True)
        except websockets.exceptions.ConnectionClosed as e:
            print(f"{tag}: closed normally: {e}", flush=True)
        # Don't call EventLoop.stop(). It terminates abnormally.
            # asyncio.get_event_loop().stop()
    #@+node:ekr.20210202110128.91: *3* function: get_args
    def get_args():
        global wsHost, wsPort
        args = None
        try:
            opts, args = getopt.getopt(sys.argv[1:], "ha:p:", ["help", "address=", "port="])
        except getopt.GetoptError:
            print('leobridgeserver.py -a <address> -p <port>')
            print('defaults to localhost on port 32125', flush=True)
            if args:
                print("unused args: " + str(args), flush=True)
            sys.exit(2)
        for opt, arg in opts:
            if opt in ("-h", "--help"):
                print('leobridgeserver.py -a <address> -p <port>')
                print('defaults to localhost on port 32125', flush=True)
                sys.exit()
            elif opt in ("-a", "--address"):
                wsHost = arg
            elif opt in ("-p", "--port"):
                wsPort = arg
        return wsHost, wsPort
    #@-others
    wsHost, wsPort = get_args()
    signon = f"LeoBridge started at {wsHost} on port: {wsPort}. Ctrl+c to break"
    print(signon, flush=True)
    # Open leoBridge.
    controller = ServerController()
    # Start the server.
    loop = asyncio.get_event_loop()  
    server = websockets.serve(ws_handler=ws_handler, host=wsHost, port=wsPort)
    loop.run_until_complete(server)
    loop.run_forever()
#@-others
if __name__ == '__main__':
    # Startup
    try:
        main()
    except KeyboardInterrupt:
        print("\nKeyboard Interupt: Stopping leoserver.py", flush=True)
        sys.exit()
#@-leo

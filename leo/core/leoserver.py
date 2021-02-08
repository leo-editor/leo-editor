#@+leo-ver=5-thin
#@+node:ekr.20210202110128.1: * @file  leoserver.py
#@@language python
#@@tabwidth -4
"""
A language-agnostic server for Leo's bridge,
based on leoInteg's leobridgeserver.py.
"""
#@+<< start coverage >>
#@+node:ekr.20210206133542.1: ** << start coverage >>
try:  # pragma: no cover
    import coverage
    print('----- Start coverage')
    cov = coverage.Coverage()
    cov.start()
except ImportError:  # pragma: no cover
    cov = None
#@-<< start coverage >>
#@+<< imports >>
#@+node:ekr.20210202110128.2: ** << imports >>
if 1:  # pragma: no cover
    # We want to start coverage before these imports.
    # pylint: disable=wrong-import-position
    import asyncio
    import getopt
    import json
    import sys
    import time
    # Third-party.
    import websockets
    # Leo
    from leo.core.leoNodes import Position
#@-<< imports >>
g = None  # The bridge's leoGlobals module.
# server defaults...
wsHost = "localhost"
wsPort = 32125
sync = False
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
#@+node:ekr.20210202110128.29: ** class ServerController
class ServerController:
    """Leo Bridge Controller"""
    #@+others
    #@+node:ekr.20210202160349.1: *3* sc:Birth & startup
    #@+node:ekr.20210202110128.30: *4* sc.__init__ (load bridge, set self.g)
    def __init__(self):

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
            silent=True,         # True: don't print signon messages.
            verbose=False,       # True: prints messages that would be sent to the log pane.
        )
        g = self.bridge.globals()
        self.dummy_c = g.app.newCommander(fileName=None)  # To inspect commands
        #
        # Complete the initialization, as in LeoApp.initApp.
        g.app.idleTimeManager = leoApp.IdleTimeManager()
        g.app.idleTimeManager.start()
        g.app.externalFilesController = leoExternalFiles.ExternalFilesController(None)
        t2 = time.process_time()
        print(f"ServerController: init leoBridge in {t2-t1:4.2} sec.")
    #@+node:ekr.20210202110128.41: *4* sc.apply_config
    def apply_config(self, package):
        """Got the configuration from client"""
        tag = 'apply_config'
        config = package.get('config')
        if not config:  # pragma: no cover
            raise ServerError(f"{tag}: no config")
        self.config = config
        return self._make_response()
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
        tag = '_check_ap'
        c = self.c
        if not c:
            raise ServerError(f"{tag}: no c")
        ap = package.get('ap')
        if not ap:  # pragma: no cover
            raise ServerError(f"{tag}: no archived_position")
        p = self._ap_to_p(ap)
        if not p:  # pragma: no cover
            raise ServerError(f"{tag}: position not found")
        if not c.positionExists(p):  # pragma: no cover
            raise ServerError(f"{tag}: position does not exist. ap: {ap}")
        return p
    #@+node:ekr.20210207054237.1: *4* sc._check_c
    def _check_c(self):
        """Return self.c or raise ServerError"""
        tag = '_check_c'
        c = self.c
        if not c:
            raise ServerError(f"{tag}: no open commander")
        return c
    #@+node:ekr.20210202110128.54: *4* sc._do_message & helpers (server)
    def _do_message(self, d):
        """
        Handle d, a python dict representing the incoming request.
        
        The request will call either:
        - A named method in Leo's Commands class or any subcommander class.
        - A named Leo command.
        """
        tag = '_do_message'
        id_ = d.get('id')
        if id_ is None:  # pragma: no cover
            raise ServerError(f"{tag}: no id")
        action = d.get('action')
        if action is None:
            raise ServerError("f{tag}: no action")
        # Set the id and action for _make_response.
        self.current_id = id_
        self.action = action
        # The package is optional.
        package = d.get('package', {})
        result = self._do_action_by_name(action, package)
        if result is None:
            raise ServerError(f"{tag}: no response: {action}")
        return result
    #@+node:ekr.20210204095743.1: *5* sc._do_action_by_name
    def _do_action_by_name(self, action, package):
        """Execute one of Leo's methods by name."""
        tag = '_do_method_by_name'
        # For now, disallow hidden methods.
        if action.startswith('_'):  # pragma: no cover
            raise ServerError(f"{tag}: action starts with '_': {action}")
        func = getattr(self, action, None)
        if func:
            return func(package)
        # Now c must exist.
        c = self._check_c()
        func = c.commandsDict.get(action)
        if func and action in self._bad_commands(c):  # pragma: no cover
            raise ServerError(f"{tag}: disallowed command: {action}")
        if func:
            value = func(event={"c":c})
            return self._make_response({"return-value": value})
        raise ServerError(f"{tag}: action not found: {action}")  # pragma: no cover
    #@+node:ekr.20210202110128.53: *5* sc._get_commander_method (revise)
    def _get_commander_method(self, method_name):
        """ Return the method with the given name in the Commands class or subcommanders."""
        c = self.c
        if not c:
            return None
        # First, try the Commands class.
        func = getattr(c, method_name, None)
        if func:
            return func
        # Search all subcommanders for the method.
        table = (
            # This table comes from c.initObjectIvars.
            'abbrevCommands',
            'bufferCommands',
            'chapterCommands',
            'controlCommands',
            'convertCommands',
            'debugCommands',
            'editCommands',
            'editFileCommands',
            'evalController',
            'gotoCommands',
            'helpCommands',
            'keyHandler',
            'keyHandlerCommands',
            'killBufferCommands',
            'leoCommands',
            'leoTestManager',
            'macroCommands',
            'miniBufferWidget',
            'printingController',
            'queryReplaceCommands',
            'rectangleCommands',
            'searchCommands',
            'spellCommands',
            'vimCommands',  # Not likely to be useful.
        )
        for ivar in table:
            subcommander = getattr(c, ivar, None)
            if subcommander:
                func = getattr(subcommander, method_name, None)
                if func:
                    return func
        return None
    #@+node:ekr.20210202110128.51: *4* sc._es & helpers
    def _es(self, s):
        """Send a response that does not correspond to an request."""
        self._send_async_output({
            "async": "",  # This response corresponds to no id_.
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
            g.trace(f"{tag}: no web socket. json: {json}")
    #@+node:ekr.20210202110128.81: *4* sc._gnx_to_p
    def _gnx_to_p(self, gnx):
        """Return first p node with this gnx or None"""
        for p in self.c.all_unique_positions():
            if p.v.gnx == gnx:
                return p
        return None  # pragma: no cover

    #@+node:ekr.20210206182638.1: *4* sc._make_response
    def _make_response(self, package=None):
        """
        Return a standard response.
        Always return "id", "commander" and "node" keys.
        """
        tag = '_make_response'
        c = self.c  # It is valid for c to be None.
        p = c and c.p
        if package is None:
            package = {}
        if isinstance(package, str):
            raise InternalServerError(f"{tag}: bad package: {package!r}")
        # g.trace(self.action, sorted(list(package.keys())))
        package ["id"] = self.current_id
        package ["action"] = self.action
        package ["commander"] = {
            "file_name": c and c.fileName(), # Can be None for new files.
            "creation_time": None,   ### To do.
        }
        package ["node"] = p and self._p_to_ap(p)
        return json.dumps(package, separators=(',', ':')) 
    #@+node:ekr.20210202193210.1: *3* sc:Commands
    #@+node:ekr.20210202193709.1: *4* sc:button commands
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
    #@+node:ekr.20210202183724.4: *5* sc.click_button
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
    #@+node:ekr.20210202183724.2: *5* sc.get_buttons
    def get_buttons(self, package):  # pragma: no cover (no scripting controller)
        """Gets the currently opened file's @buttons list"""
        d = self._check_button_command('get_buttons')
        return self._make_response({
            "buttons": sorted(list(d.get.keys()))
        })
    #@+node:ekr.20210202183724.3: *5* sc.remove_button
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
    #@+node:ekr.20210202193642.1: *4* sc:file commands
    #@+node:ekr.20210202110128.57: *5* sc.open_file
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
            assert c.frame.body.wrapper, filename
        if not c:  # pragma: no cover
            raise ServerError(f"{tag}: can not open {filename!r}")
        # Assign self.c
        self.c = c
        if 0:  # Clean the dict.
            d = c.fileCommands.gnxDict
            c.fileCommands.gnxDict = {
                gnx: v for gnx, v in d.items()
                    if v.h != "NewHeadline"  # This looks like a bug in Leo.
            }
            g.printObj(c.fileCommands.gnxDict)
        c.selectPosition(c.rootPosition())  # Required.
        return self._make_response()
    #@+node:ekr.20210202110128.58: *5* sc.close_file
    def close_file(self, package):
        """
        Closes a leo file. A file can then be opened with "open_file"
        Returns an object that contains a 'closed' member
        """
        c = self._check_c()
        # Close the outline, even if it is dirty!
        c.changed = False  # Force the close!
        c.close()
        # Select the first open outline, if any.
        commanders = g.app.commanders()
        self.c = commanders and commanders[0]
        return self._make_response()
    #@+node:ekr.20210202183724.1: *5* sc.save_file
    def save_file(self, package):
        """Save the leo outline."""
        c = self._check_c()
        c.save()
        return self._make_response()
    #@+node:ekr.20210202193505.1: *4* sc:getter commands
    #@+node:ekr.20210202183724.5: *5* sc.get_all_commands & helpers
    def get_all_commands(self, package):
        """Return a list of all Leo commands that make sense in leoInteg."""
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
                "label": command_name,
                "func":  func_name,
                "detail": doc,
            })
        return self._make_response({"commands": result})
    #@+node:ekr.20210202183724.6: *6* sc._bad_commands
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
        c = self._check_c()
        result = [p.v.gnx for p in c.all_unique_positions(copy=False)]
        return self._make_response({"allGnx": result})

    #@+node:ekr.20210202110128.55: *5* sc.get_all_opened_files
    def get_all_opened_files(self, package):
        """Return array of opened file path/names to be used as open_file parameters to switch files"""
        c = self._check_c()
        files = [
            {
                "changed": commander.changed,
                "name": commander.mFileName,
                "selected": c == commander,
            } for commander in g.app.commanders()
        ]
        return self._make_response({"open-files": files})
    #@+node:ekr.20210202110128.72: *5* sc.get_body
    def get_body_using_gnx(self, package):
        """Given a gnx, return the body text of the node."""
        tag = 'get_body_using_gnx'
        c = self._check_c()
        gnx = package.get('gnx')
        if not gnx:
            raise ServerError(f"{tag}: no gnx given")
        v = c.fileCommands.gnxDict.get(gnx)  # vitalije
        if not v:
            raise ServerError(f"{tag}: gnx not found: {gnx}")
        return self._make_response({"body": v.b})

    def get_body_using_p(self, package):
        """Given an ap, return the body text of the node."""
        self._check_c()
        p = self._check_ap(package)
        return self._make_response({"body": p.b})
    #@+node:ekr.20210202110128.73: *5* sc.get_body_length
    def get_body_length(self, package):
        """EMIT OUT body string length of a node"""
        tag = 'get_body_length'
        gnx = package.get('gnx')
        if not gnx:  # pragma: no cover
            raise ServerError(f"{tag}: no gnx")
        v = self.c.fileCommands.gnxDict.get(gnx)  # vitalije
        if not v:  # pragma: no cover
            raise ServerError(f"{tag}: gnx not found: {gnx!r}")
        return self._make_response({"bodyLength", len(v.b)})
    #@+node:ekr.20210202110128.66: *5* sc.get_body_states
    def get_body_states(self, package):
        """
        Finds the language in effect at top of body for position p,
        Also returns the saved cursor position from last time node was accessed.
        """
        c = self._check_c()
        p = self._check_ap(package)
        wrapper = c.frame.body.wrapper
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
        return self._make_response({"body-states": states})
    #@+node:ekr.20210202110128.68: *5* sc.get_children
    def get_children(self, package):
        """Return list of children of a node"""
        self._check_c()
        p = self._check_ap(package)
        return self._make_response({
            "ap-list": [self._p_to_ap(child) for child in p.children()]
        })

        
        
    #@+node:ekr.20210202110128.69: *5* sc.get_parent
    def get_parent(self, package):
        """EMIT OUT the parent of a node, as an array, even if unique or empty"""
        self._check_c()
        p = self._check_ap(package)
        parent = p.parent()
        parent_ap = self._p_to_ap(parent) if parent else None
        return self._make_response({"parent": parent_ap})
    #@+node:ekr.20210206184431.1: *5* sc.get_position_data
    def get_position_data(self, package):
        """returns all data needed to redraw p the screen."""
        c = self._check_c()
        p = self._check_ap(package)
        stack = [{'gnx': gnx, 'childIndex': childIndex}
            for (gnx, childIndex) in p.stack]
        package = {
            # The minimal attributes that define a position.
            'childIndex': p._childIndex,
            'gnx': p.v.gnx,
            'stack': stack,
            # Other attributes.
            'expanded': p.isExpanded(),
            'hasBody': bool(p.b),  # Don't return the body!!
            'hasChildren': p.hasChildren(),
            'headline': p.h,
            'isCloned': p.isCloned(),
            'isMarked': p.isMarked(),
            'selected': p == c.p, 
            #
            # These would be expensive or marginally useful.
            # 'atFile', p.isAnyAtFileNode(), 'atFile'),
            # 'level': p.level(),
            # 'uA': p.v.u,
        }
        return self._make_response(package)
    #@+node:ekr.20210202110128.67: *5* sc.get_selected_position
    def get_position(self, package):
        """Return the current position. Don't select it."""
        # *All* responses contain a "node" key.
        return self._make_response()
    #@+node:ekr.20210206062654.1: *5* sc.get_sign_on
    def get_sign_on(self, package):
        """Synchronous version of _sign_on"""
        g.app.computeSignon()
        signon = []
        for z in (g.app.signon, g.app.signon1):
            for z2 in z.split('\n'):
                signon.append(z2.strip())
        return self._make_response({"sign-on-message": "\n".join(signon)})
    #@+node:ekr.20210202110128.61: *5* sc.get_ui_states
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
    #@+node:ekr.20210202193540.1: *4* sc:node commands (setters)
    #@+node:ekr.20210202183724.11: *5* sc.clone_node
    def clone_node(self, package):
        """Clone a node"""
        c = self._check_c()
        p = self._check_ap(package)
        c.selectPosition(p)
        c.clone()
        return self._make_response()
    #@+node:ekr.20210202110128.79: *5* sc.collapse_node
    def collapse_node(self, package):
        """Collapse a node"""
        self._check_c()
        p = self._check_ap(package)
        p.contract()
        return self._make_response()
    #@+node:ekr.20210202183724.12: *5* sc.cut_node
    def cut_node(self, package):
        """Cut a node, return the newly-selected node."""
        c = self._check_c()
        p = self._check_ap(package)
        c.selectPosition(p)
        c.cutOutline()
        return self._make_response()
    #@+node:ekr.20210202183724.13: *5* sc.delete_node
    def delete_node(self, package):
        """Delete a node. Return the newly-selected node."""
        c = self._check_c()
        p = self._check_ap(package)
        c.selectPosition(p)
        c.deleteOutline()  # Handles undo.
        return self._make_response()
    #@+node:ekr.20210202110128.78: *5* sc.expand_node
    def expand_node(self, package):
        """Expand a node"""
        self._check_c()
        p = self._check_ap(package)
        p.expand()
        return self._make_response()
    #@+node:ekr.20210202183724.15: *5* sc.insert_node
    def insert_node(self, package):
        """Insert a node after the given node, set its headline and select it."""
        tag = 'insert_node'
        c = self._check_c()
        p = self._check_ap(package)
        h = package.get('headline')
        if not h:  # pragma: no cover
            raise ServerError(f"{tag}: no headline given")
        c.selectPosition(p)
        c.insertHeadline()  # Handles undo, sets c.p
        return self._make_response()
    #@+node:ekr.20210202183724.9: *5* sc.mark_node
    def mark_node(self, package):
        """Mark a node, but don't select it."""
        self._check_c()
        p = self._check_ap(package)
        p.setMarked()
        return self._make_response()
    #@+node:ekr.20210202110128.64: *5* sc.page_down
    def page_down(self, unused):
        """Selects a node a couple of steps down in the tree to simulate page down"""
        c = self._check_c()
        c.selectVisNext()
        c.selectVisNext()
        c.selectVisNext()
        return self._make_response()
    #@+node:ekr.20210202110128.63: *5* sc.page_up
    def pageUp(self, unused):
        """Selects a node a couple of steps up in the tree to simulate page up"""
        c = self._check_c()
        c.selectVisBack()
        c.selectVisBack()
        c.selectVisBack()
        return self._make_response()
    #@+node:ekr.20210202183724.17: *5* sc.redo
    def redo(self, package):
        """Undo last un-doable operation"""
        c = self._check_c()
        u = c.undoer
        if u.canRedo():
            u.redo()
        return self._make_response()
    #@+node:ekr.20210202110128.74: *5* sc.set_body
    def set_body(self, package):
        """Change Body text of a node"""
        tag = 'set_body'
        c = self._check_c()
        u = c.undoer
        gnx = package['gnx']
        if not gnx:  # pragma: no cover
            raise ServerError(f"{tag}: no gnx")
        v = c.fileCommands.gnxDict.get(gnx)  # vitalije
        if not v:  # pragma: no cover
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
        return self._make_response()
    #@+node:ekr.20210202110128.77: *5* sc.set_current_position
    def set_current_position(self, package):
        """Select a node, or the first one found with its GNX"""
        c = self._check_c()
        p = self._check_ap(package)  # p is guaranteed to exist.
        c.selectPosition(p)
        return self._make_response()
    #@+node:ekr.20210202110128.76: *5* sc.set_headline
    def set_headline(self, package):
        """Change a node's headline."""
        tag = 'set_headline'
        c = self._check_c()
        p = self._check_ap(package)
        u = c.undoer
        h = package.get('headline')
        if not h:  # pragma: no cover
            raise ServerError(f"{tag}: no headline")
        bunch = u.beforeChangeNodeContents(p)
        p.h = h
        u.afterChangeNodeContents(p, 'Change Headline', bunch)
        return self._make_response()
    #@+node:ekr.20210202110128.75: *5* sc.set_selection
    def set_selection(self, package):
        """
        Given package['gnx'], selection.
        Set the selection in the wrapper if c.p.gnx == gnx.
        """
        tag = 'set_selection'
        c = self._check_c()
        wrapper = c.frame.body.wrapper
        gnx = package.get('gnx')
        if not gnx:  # pragma: no cover
            raise ServerError(f"{tag}: no gnx")
        v = c.fileCommands.gnxDict.get(gnx)
        if not v:  # pragma: no cover
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
        return self._make_response()
    #@+node:ekr.20210202183724.16: *5* sc.undo
    def undo(self, package):
        """Undo last un-doable operation"""
        c = self._check_c()
        u = c.undoer
        if u.canUndo():
            u.undo()
        # Félix: Caller can get focus using other calls.
        return self._make_response()
    #@+node:ekr.20210202183724.10: *5* sc.unmark_node
    def unmark_node(self, package):
        """Unmark a node, don't select it"""
        self._check_c()
        p = self._check_ap(package)
        p.clearMarked()
        return self._make_response()
    #@+node:ekr.20210205102806.1: *4* sc:test commands
    #@+node:ekr.20210205102818.1: *5* sc.error
    def error(self, package):
        """For unit testing. Raise ServerError"""
        raise ServerError(f"sc.error called")
    #@+node:ekr.20210205103759.1: *5* sc.shut_down
    def shut_down(self, package):
        """Shut down the server."""
        raise TerminateServer(f"client requested shut down")

    quit = shut_down  # Abbreviation for testing.
    #@+node:ekr.20210205111421.1: *5* sc.set/clear_trace
    def clear_trace(self, package):
        self.trace = False
        return self._make_response()
        
    def set_trace(self, package):
        self.trace = True
        return self._make_response()
    #@+node:ekr.20210202110128.60: *5* sc.test
    def test(self, package):
        """Do-nothing test function for debugging"""
        return self._make_response()
    #@+node:ekr.20210202193334.1: *3* sc:Serialization
    #@+node:ekr.20210202110128.85: *4* sc._ap_to_p
    def _ap_to_p(self, ap):
        """
        Convert ap (archived position, a dict) to a valid Leo position.
        Raise ServerError on any kind of error.
        """
        tag = '_ap_to_p'
        c = self._check_c()
        gnx_d = c.fileCommands.gnxDict
        childIndex = ap.get('childIndex')
        gnx = ap.get('gnx')
        ap_stack = ap.get('stack')
        #
        # Test the outer level.
        if childIndex is None:  # pragma: no cover.
            raise ServerError(f"{tag}: no outer childIndex.")
        if gnx is None:  # pragma: no cover.
            raise ServerError(f"{tag}: no outer gnx.")
        v = gnx_d.get(gnx)
        if v is None:  # pragma: no cover.
            g.printObj(gnx_d, tag=f"gnx_d")
            raise ServerError(f"{tag}: gnx not found: {gnx}")
        #
        # Resolve the stack, a list of tuples(gnx, childIndex).
        stack = []
        for d in ap_stack:
            childIndex = d.get('childIndex')
            if childIndex is None:  # pragma: no cover.
                raise ServerError(f"{tag}: no childIndex in {d}")
            gnx = d.get('gnx')
            if gnx is None:  # pragma: no cover.
                raise ServerError(f"{tag}: no gnx in {d}")
            stack.append((gnx, childIndex))
        #
        # Create the position!
        p = Position(v, childIndex, stack)
        if not c.positionExists(p):  # pragma: no cover.
            raise ServerError(f"{tag}: p does not exist: {p!r}")
        return p
    #@+node:ekr.20210202110128.83: *4* sc._create_gnx_to_vnode
    def _create_gnx_to_vnode(self):
        """Make the first gnx_to_vnode array with all unique nodes"""
        self.gnx_to_vnode = {
            v.gnx: v for v in self.c.all_unique_nodes()
        }
        self._test_round_trip_positions()
    #@+node:ekr.20210202110128.86: *4* sc._p_to_ap
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
    #@+node:ekr.20210202110128.84: *4* sc._test_round_trip_positions
    def _test_round_trip_positions(self):
        """
        From Leo plugin leoflexx.py.
        Test the round tripping of p_to_ap and ap_to_p.
        """
        tag = '_test_round_trip_positions'
        try:
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
        except Exception as e:  # pragma: no cover
            # Continue after showing the full exception.
            g.print_exception()
            raise ServerError(f"{tag}: {e}")
    #@-others
#@+node:ekr.20210206083303.1: ** function: coverage_end (server)
def coverage_end():  # pragma: no cover
    """End coverage tests (server)"""
    global cov
    if not cov:
        return
    cov.stop()
    cov.save()
    directory = r'c:/test'
    cov.html_report(directory=directory, morfs=['leoserver.py'])
    print(f"----- End coverage: index.html in {directory}/leoserver_py.html")
#@+node:ekr.20210202110128.88: ** function: main & helpers
def main():
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
        try:
            controller._init_connection(websocket)
            # Start by sending empty as 'ok'.
            n = 0
            await websocket.send(controller._make_response())
            # controller._sign_on()
            async for json_message in websocket:
                try:
                    n += 1
                    d = None
                    trace = False  ## controller.trace
                    d = json.loads(json_message)
                    if trace:
                        print(f"{tag}: got: {d}")
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
                    g.print_exception()
                    break
                await websocket.send(answer)
                if n in (3, 4, 7, 10):
                    controller._es(f"send async message {n}")
        except websockets.exceptions.ConnectionClosedError as e:  # pragma: no cover
            print(f"{tag}: closed error: {e}")
        except websockets.exceptions.ConnectionClosed as e:
            print(f"{tag}: closed normally: {e}")
        coverage_end()
        # Don't call EventLoop.stop(). It terminates abnormally.
            # asyncio.get_event_loop().stop()
    #@+node:ekr.20210202110128.91: *3* function: get_args
    def get_args():  # pragma: no cover
        global wsHost, wsPort
        args = None
        try:
            opts, args = getopt.getopt(sys.argv[1:], "ha:p:", ["help", "address=", "port="])
        except getopt.GetoptError:
            print('leobridgeserver.py -a <address> -p <port>')
            print('defaults to localhost on port 32125')
            if args:
                print("unused args: " + str(args))
            sys.exit(2)
        for opt, arg in opts:
            if opt in ("-h", "--help"):
                print('leobridgeserver.py -a <address> -p <port>')
                print('defaults to localhost on port 32125')
                sys.exit()
            elif opt in ("-a", "--address"):
                wsHost = arg
            elif opt in ("-p", "--port"):
                wsPort = arg
        return wsHost, wsPort
    #@-others
    wsHost, wsPort = get_args()
    signon = f"LeoBridge started at {wsHost} on port: {wsPort}. Ctrl+c to break"
    print(signon)
    # Open leoBridge.
    controller = ServerController()
    # Start the server.
    loop = asyncio.get_event_loop()  
    server = websockets.serve(ws_handler=ws_handler, host=wsHost, port=wsPort)
    loop.run_until_complete(server)
    loop.run_forever()
#@-others
if __name__ == '__main__':  # pragma: no cover
    try:
        main()  # ws_handler calls coverage_end.
    except KeyboardInterrupt:
        print("\nKeyboard Interupt: Stopping leoserver.py")
        sys.exit()
#@-leo

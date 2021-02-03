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
import os.path
import sys
import time
import traceback
# Third-party.
import websockets
# Leo
import leo.core.leoApp as leoApp
import leo.core.leoBridge as leoBridge
import leo.core.leoNodes as leoNodes
import leo.core.leoExternalFiles as leoExternalFiles
#@-<< imports >>
g = None  # The bridge's leoGlobals module.

# server defaults
wsHost = "localhost"
wsPort = 32125
commonActions = ["getChildren", "getBody", "getBodyLength"]
#@+others
#@+node:ekr.20210202110128.29: ** class ServerController
class ServerController:
    '''Leo Bridge Controller'''
    #@+others
    #@+node:ekr.20210202160349.1: *3* sc.Startup
    #@+node:ekr.20210202110128.30: *4* sc.__init__ (load bridge, set self.g)
    def __init__(self):
        ### TODO : @boltex #74 need gnx_to_vnode for each opened file/commander
        global g
        t1 = time.process_time()
        #
        # Init ivars first.
        self.c = None  # Currently Selected Commander.
        self.config = None
        self.currentActionId = 1  # Id of action being processed.
        self.gnx_to_vnode = []  # See leoflexx.py in leoPluginsRef.leo
        self.loop = None
        self.webSocket = None
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
        g.es = self.es  # Send Log pane output to the client's log pane.
        #
        # Complete the initialization, as done in LeoApp.initApp.
        g.app.idleTimeManager = leoApp.IdleTimeManager()
        g.app.idleTimeManager.start()
        g.app.externalFilesController = leoExternalFiles.ExternalFilesController(None)
        t2 = time.process_time()
        print(f"ServerController: init leoBridge in {t2-t1:4.2} sec.")
    #@+node:ekr.20210202110128.52: *4* sc.initConnection
    def initConnection(self, p_webSocket):
        self.webSocket = p_webSocket
        self.loop = asyncio.get_event_loop()

    #@+node:ekr.20210202110128.31: *4* sc._asyncIdleLoop
    async def _asyncIdleLoop(self, p_seconds, p_fn):
        """Call p_fn every p_seconds"""
        while True:
            await asyncio.sleep(p_seconds)
            p_fn(self)
    #@+node:ekr.20210202110128.32: *3* Overrides
    #@+node:ekr.20210202110128.33: *4* _returnNo
    def _returnNo(self, *arguments, **kwargs):
        '''Used to override g.app.gui.ask[XXX] dialogs answers'''
        return "no"

    #@+node:ekr.20210202110128.34: *4* _returnYes
    def _returnYes(self, *arguments, **kwargs):
        '''Used to override g.app.gui.ask[XXX] dialogs answers'''
        return "yes"

    #@+node:ekr.20210202110128.35: *4* _getScript
    def _getScript(self, c, p,
                   useSelectedText=True,
                   forcePythonSentinels=True,
                   useSentinels=True,
                   ):
        """
        Return the expansion of the selected text of node p.
        Return the expansion of all of node p's body text if
        p is not the current node or if there is no text selection.
        """
        w = c.frame.body.wrapper
        if not p:
            p = c.p
        try:
            if w and p == c.p and useSelectedText and w.hasSelection():
                s = w.getSelectedText()
            else:
                s = p.b
            # Remove extra leading whitespace so the user may execute indented code.
            s = g.removeExtraLws(s, c.tab_width)
            s = g.extractExecutableString(c, p, s)
            script = g.composeScript(c, p, s,
                                          forcePythonSentinels=forcePythonSentinels,
                                          useSentinels=useSentinels)
        except Exception:
            g.es_print("unexpected exception in g.getScript")
            g.es_exception()
            script = ''
        return script
    #@+node:ekr.20210202110128.36: *4* _idleTime
    def _idleTime(self, fn, delay, tag):
        # TODO : REVISE/REPLACE WITH OWN SYSTEM
        asyncio.get_event_loop().create_task(self._asyncIdleLoop(delay/1000, fn))

    #@+node:ekr.20210202110128.37: *3* _getTotalOpened
    def _getTotalOpened(self):
        '''Get total of opened commander (who have closed == false)'''
        w_total = 0
        for w_commander in g.app.commanders():
            if not w_commander.closed:
                w_total = w_total + 1
        return w_total

    #@+node:ekr.20210202110128.38: *3* _getFirstOpenedCommander
    def _getFirstOpenedCommander(self):
        '''Get first opened commander, or False if there are none.'''
        for w_commander in g.app.commanders():
            if not w_commander.closed:
                return w_commander
        return False

    #@+node:ekr.20210202110128.39: *3* sendAsyncOutput
    def sendAsyncOutput(self, p_package):
        if "async" not in p_package:
            print('[sendAsyncOutput] Error async member missing in package parameter')
            print(json.dumps(p_package, separators=(',', ':')), flush=True)
            return
        if self.loop:
            self.loop.create_task(self.asyncOutput(
                json.dumps(p_package, separators=(',', ':'))))
        else:
            print('[sendAsyncOutput] Error loop not ready' +
                  json.dumps(p_package, separators=(',', ':')))
    #@+node:ekr.20210202110128.40: *3* askResult
    def askResult(self, p_result):
        '''Got the result to an asked question/warning from client'''
        g.app.externalFilesController.integResult(p_result)
        return self.sendLeoBridgePackage()  # Just send empty as 'ok'

    #@+node:ekr.20210202110128.41: *3* applyConfig
    def applyConfig(self, p_config):
        '''Got leoInteg's config from client'''
        self.config = p_config
        return self.sendLeoBridgePackage()  # Just send empty as 'ok'
    #@+node:ekr.20210202110128.42: *3* logSignon
    def logSignon(self):
        '''Simulate the Initial Leo Log Entry'''
        if self.loop:
            g.app.computeSignon()
            g.es(str(g.app.signon))
            g.es(str(g.app.signon1))
        else:
            print('no loop in logSignon', flush=True)

    #@+node:ekr.20210202110128.43: *3* setActionId
    def setActionId(self, p_id):
        self.currentActionId = p_id

    #@+node:ekr.20210202160323.1: *3* sc:Output
    #@+node:ekr.20210202110128.44: *4* bc.async def asyncOutput
    async def asyncOutput(self, p_json):
        '''Output json string to the websocket'''
        if self.webSocket:
            await self.webSocket.send(bytes(p_json, 'utf-8'))
        else:
            g.trace(f"no web socket. p_json: {p_json}", flush=True)

    #@+node:ekr.20210202110128.45: *4* bc.sendLeoBridgePackage
    def sendLeoBridgePackage(self, p_key=False, p_any=None):
        w_package = {"id": self.currentActionId}
        if p_key:
            w_package[p_key] = p_any  # add [key]?:any
        return(json.dumps(w_package, separators=(',', ':')))  # send as json
    #@+node:ekr.20210202110128.46: *4* _outputError
    def _outputError(self, p_message="Unknown Error"):
        # Output to this server's running console
        print("ERROR: " + p_message, flush=True)
        w_package = {"id": self.currentActionId}
        w_package["error"] = p_message
        return p_message

    #@+node:ekr.20210202110128.47: *4* _outputBodyData
    def _outputBodyData(self, p_bodyText=""):
        return self.sendLeoBridgePackage("bodyData", p_bodyText)

    #@+node:ekr.20210202110128.48: *4* _outputSelectionData
    def _outputSelectionData(self, p_bodySelection):
        return self.sendLeoBridgePackage("bodySelection", p_bodySelection)

    #@+node:ekr.20210202110128.49: *4* _outputPNode
    def _outputPNode(self, p_node=False):
        return self.sendLeoBridgePackage("node", self._p_to_ap(p_node) if p_node else None)
    #@+node:ekr.20210202110128.50: *4* _outputPNodes
    def _outputPNodes(self, p_pList):
        w_apList = []
        for p in p_pList:
            w_apList.append(self._p_to_ap(p))
        # Multiple nodes, plural
        return self.sendLeoBridgePackage("nodes", w_apList)

    #@+node:ekr.20210202110128.51: *4* es
    def es(self, * args, **keys):
        '''Output to the Log Pane'''
        d = {
            'color': None,
            'commas': False,
            'newline': True,
            'spaces': True,
            'tabName': 'Log',
            'nodeLink': None,
        }
        d = g.doKeywordArgs(keys, d)
        s = g.translateArgs(args, d)
        w_package = {"async": "log", "log": s}
        self.sendAsyncOutput(w_package)

    #@+node:ekr.20210202110128.53: *3* _get_commander_method
    def _get_commander_method(self, p_command):
        """ Return the given method (p_command) in the Commands class or subcommanders."""
        c = self.c
        #
        # First, try the commands class.
        w_func = getattr(c, p_command, None)
        if w_func:
            return w_func
        #
        # Search all subcommanders for the method.
        table = (  # This table comes from c.initObjectIvars.
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
                w_func = getattr(subcommander, p_command, None)
                if w_func:
                    return w_func
        return None

    #@+node:ekr.20210202110128.54: *3* leoCommand
    def leoCommand(self, p_command, p_package):
        '''
        Generic call to a method in Leo's Commands class or any subcommander class.

        The p_ap position node is to be selected before having the command run,
        while the p_keepSelection parameter specifies wether the original position should be re-selected.
        The whole of those operations is to be undoable as one undo step.

        p_command: a method name (a string).
        p_ap: an archived position.
        p_keepSelection: preserve the current selection, if possible.
        '''
        c = self.c
        w_keepSelection = False  # Set default, optional component of package
        if "keep" in p_package:
            w_keepSelection = p_package["keep"]
        #     print("have keep! " + str(w_keepSelection), flush=True)
        # else:
        #     print("NO keep!", flush=True)
        print('leoCommand', repr(p_command), repr(p_package))
        w_ap = p_package["node"]  # At least node parameter is present
        if not w_ap:
            return self._outputError(f"Error in {p_command}: no param node")
        w_p = self._ap_to_p(w_ap)
        if not w_p:
            return self._outputError(f"Error in {p_command}: no w_p node found")
        w_func = self._get_commander_method(p_command)
        if not w_func:
            return self._outputError(f"Error in {p_command}: no method found")

        if w_p == c.p:
            w_func(event=None)
        else:
            oldPosition = c.p
            c.selectPosition(w_p)
            w_func(event=None)
            if w_keepSelection and c.positionExists(oldPosition):
                c.selectPosition(oldPosition)
        return self._outputPNode(c.p)
    #@+node:ekr.20210202160143.1: *3* sc:Files...
    #@+node:ekr.20210202110128.58: *4* sc.closeFile
    def closeFile(self, p_package):
        """
        Closes a leo file. A file can then be opened with "openFile"
        Returns an object that contains a 'closed' member
        """
        c = self.c
        # TODO : Specify which file to support multiple opened files
        if c:
            if p_package["forced"] and c.changed:
                # return "no" g.app.gui.runAskYesNoDialog  and g.app.gui.runAskYesNoCancelDialog
                c.revert()
            if p_package["forced"] or not c.changed:
                c.closed = True
                c.close()
            else:
                # Cannot close, ask to save, ignore or cancel
                return self.sendLeoBridgePackage('closed', False)

        # Switch commanders to first available
        w_total = self._getTotalOpened()
        self.c = c = self._getFirstOpenedCommander() if w_total else None
        if not c:
            return self.sendLeoBridgePackage("closed", {"total": 0})
        self._create_gnx_to_vnode()
        w_result = {
            "total": self._getTotalOpened(),
            "filename": c.fileName(),
            "node": self._p_to_ap(c.p),
        }
        return self.sendLeoBridgePackage("closed", w_result)
    #@+node:ekr.20210202110128.55: *4* sc.getOpenedFiles
    def getOpenedFiles(self, p_package):
        '''Return array of opened file path/names to be used as openFile parameters to switch files'''
        c = self.c
        w_files = []
        w_index = 0
        w_indexFound = 0
        for w_commander in g.app.commanders():
            if not w_commander.closed:
                w_isSelected = False
                w_isChanged = w_commander.changed
                if c == w_commander:
                    w_indexFound = w_index
                    w_isSelected = True
                w_entry = {"name": w_commander.mFileName, "index": w_index,
                           "changed": w_isChanged, "selected": w_isSelected}
                w_files.append(w_entry)
                w_index = w_index + 1

        w_openedFiles = {"files": w_files, "index": w_indexFound}

        return self.sendLeoBridgePackage("openedFiles", w_openedFiles)

    #@+node:ekr.20210202110128.57: *4* sc.openFile
    def openFile(self, p_file):
        """
        Open a leo file via leoBridge controller, or create a new document if empty string.
        Returns an object that contains a 'opened' member.
        """
        c = None
        w_found = False

        # If not empty string (asking for New file) then check if already opened
        if p_file:
            for w_commander in g.app.commanders():
                if w_commander.fileName() == p_file:
                    w_found = True
                    c = self.c = w_commander
        if not w_found:
            c = self.c = self.bridge.openLeoFile(p_file)
        #
        # Leo at this point has done this too: g.app.windowList.append(c.frame)
        # and so, now, app.commanders() yields this: return [f.c for f in g.app.windowList]
        if not c:
            return self._outputError('Error in openFile')
        c.closed = False
        if not w_found:
            # is new so also replace wrapper
            ### c.frame.body.wrapper = IntegTextWrapper(c, "integBody", g)
            c.selectPosition(c.p)

        self._create_gnx_to_vnode()
        w_result = {
            "total": self._getTotalOpened(),
            "filename": c.fileName(),
            "node": self._p_to_ap(c.p),
        }
        return self.sendLeoBridgePackage("opened", w_result)
    #@+node:ekr.20210202182311.1: *4* sc.openFiles
    def openFiles(self, p_package):
        """
        Opens an array of leo files
        Returns an object that contains the last 'opened' member.
        """
        c = None
        w_files = []
        if "files" in p_package:
            w_files = p_package["files"]

        for i_file in w_files:
            w_found = False
            # If not empty string (asking for New file) then check if already opened
            if i_file:
                for w_commander in g.app.commanders():
                    if w_commander.fileName() == i_file:
                        w_found = True
                        c = self.c = w_commander
            if not w_found:
                if os.path.isfile(i_file):
                    c = self.c = self.bridge.openLeoFile(i_file)  # create self.c
            if c:
                c.closed = False
                ### c.frame.body.wrapper = IntegTextWrapper(c, "integBody", g)
                c.selectPosition(c.p)

        # Done with the last one, it's now the selected commander. Check again just in case.
        if not c:
            return self._outputError('Error in openFiles')
        self._create_gnx_to_vnode()
        w_result = {
            "total": self._getTotalOpened(),
            "filename": c.fileName(),
            "node": self._p_to_ap(c.p),
        }
        return self.sendLeoBridgePackage("opened", w_result)
    #@+node:ekr.20210202183724.1: *4* saveFile
    def saveFile(self, p_package):
        '''Saves the leo file. New or dirty derived files are rewritten'''
        c = self.c
        if c:
            try:
                if "text" in p_package:
                    c.save(fileName=p_package['text'])
                else:
                    c.save()
            except Exception as e:
                g.trace('Error while saving')
                print("Error while saving", flush=True)
                print(str(e), flush=True)

        return self.sendLeoBridgePackage()  # Just send empty as 'ok'

    #@+node:ekr.20210202183724.2: *4* getButtons
    def getButtons(self, p_package):
        '''Gets the currently opened file's @buttons list'''
        c = self.c
        w_buttons = []
        if c and c.theScriptingController and c.theScriptingController.buttonsDict:
            w_dict = c.theScriptingController.buttonsDict
            for w_key in w_dict:
                w_entry = {"name": w_dict[w_key], "index": str(w_key)}
                w_buttons.append(w_entry)
        return self.sendLeoBridgePackage("buttons", w_buttons)

    #@+node:ekr.20210202183724.3: *4* removeButton
    def removeButton(self, p_package):
        '''Removes an entry from the buttonsDict by index string'''
        c = self.c
        w_index = p_package['index']
        w_dict = c.theScriptingController.buttonsDict
        w_key = None
        for i_key in w_dict:
            if(str(i_key) == w_index):
                w_key = i_key
        if w_key:
            del(w_dict[w_key])  # delete object member
        # return selected node when done
        return self._outputPNode(c.p)

    #@+node:ekr.20210202183724.4: *4* clickButton
    def clickButton(self, p_package):
        '''Handles buttons clicked in client from the '@button' panel'''
        c = self.c
        w_index = p_package['index']
        w_dict = c.theScriptingController.buttonsDict
        w_button = None
        for i_key in w_dict:
            if(str(i_key) == w_index):
                w_button = i_key
        if w_button:
            w_button.command()  # run clicked button command
        # return selected node when done
        return self._outputPNode(c.p)

    #@+node:ekr.20210202183724.5: *4* getCommands
    def getCommands(self, p_package):
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
            # This shows up in the bridge log.
            # print(f"__doc__: {len(doc):4} {command_name:40} {func_name} ", flush=True)
            # print(f"{func_name} ", flush=True)

        return self.sendLeoBridgePackage("commands", result)

    #@+node:ekr.20210202183724.6: *4* _bad_commands
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

    #@+node:ekr.20210202183724.7: *4* _good_commands
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

    #@+node:ekr.20210202183724.8: *4* _getDocstringForCommand
    def _getDocstringForCommand(self, command_name):
        """get docstring for the given command."""
        func = self._get_commander_method(command_name)
        docstring = func.__doc__ if func else ''
        return docstring

    #@+node:ekr.20210202183724.9: *4* markPNode
    def markPNode(self, p_package):
        '''Mark a node, don't select it'''
        c = self.c
        w_ap = p_package["node"]
        if not w_ap:
            return self._outputError("Error in markPNode no param node") 
        w_p = self._ap_to_p(w_ap)
        if not w_p:
            return self._outputError("Error in markPNode no w_p node found")
        w_p.setMarked()
        return self._outputPNode(c.p)
    #@+node:ekr.20210202183724.10: *4* unmarkPNode
    def unmarkPNode(self, p_package):
        '''Unmark a node, don't select it'''
        c = self.c
        w_ap = p_package["node"]
        if not w_ap:
            return self._outputError("Error in unmarkPNode no param node")
        w_p = self._ap_to_p(w_ap)
        if not w_p:
            return self._outputError("Error in unmarkPNode no w_p node found")
        w_p.clearMarked()
        return self._outputPNode(c.p)
    #@+node:ekr.20210202183724.11: *4* clonePNode
    def clonePNode(self, p_package):
        '''Clone a node, return it, if it was also the current selection, otherwise try not to select it'''
        c = self.c
        w_ap = p_package["node"]
        if not w_ap:
            return self._outputError("Error in clonePNode function, no param p_ap")
        w_p = self._ap_to_p(w_ap)
        if not w_p:
            # default empty
            return self._outputError("Error in clonePNode function, no w_p node found")
        if w_p == c.p:
            c.clone()
        else:
            oldPosition = c.p
            c.selectPosition(w_p)
            c.clone()
            if c.positionExists(oldPosition):
                c.selectPosition(oldPosition)
        # return selected node either ways
        return self._outputPNode(c.p)

    #@+node:ekr.20210202183724.12: *4* cutPNode
    def cutPNode(self, p_package):
        '''Cut a node, don't select it. Try to keep selection, then return the selected node that remains'''
        c = self.c
        w_ap = p_package["node"]
        if not w_ap:
            return self._outputError("Error in cutPNode no param node")
        w_p = self._ap_to_p(w_ap)
        if not w_p:
            return self._outputError("Error in cutPNode no w_p node found")
        if w_p == c.p:
            c.cutOutline()  # already on this node, so cut it
        else:
            oldPosition = c.p  # not same node, save position to possibly return to
            c.selectPosition(w_p)
            c.cutOutline()
            if c.positionExists(oldPosition):
                # select if old position still valid
                c.selectPosition(oldPosition)
            else:
                oldPosition._childIndex = oldPosition._childIndex-1
                # Try again with childIndex decremented
                if c.positionExists(oldPosition):
                    # additional try with lowered childIndex
                    c.selectPosition(oldPosition)
        # in both cases, return selected node
        return self._outputPNode(c.p)
    #@+node:ekr.20210202183724.13: *4* deletePNode
    def deletePNode(self, p_package):
        '''Delete a node, don't select it. Try to keep selection, then return the selected node that remains'''
        c = self.c
        w_ap = p_package["node"]
        if not w_ap:
            return self._outputError("Error in deletePNode no param node")
        w_p = self._ap_to_p(w_ap)
        if not w_p:
            return self._outputError("Error in deletePNode no w_p node found")
        if w_p == c.p:
            c.deleteOutline()  # already on this node, so delete it
        else:
            oldPosition = c.p  # not same node, save position to possibly return to
            c.selectPosition(w_p)
            c.deleteOutline()
            if c.positionExists(oldPosition):
                # select if old position still valid
                c.selectPosition(oldPosition)
            else:
                oldPosition._childIndex = oldPosition._childIndex-1
                # Try again with childIndex decremented
                if c.positionExists(oldPosition):
                    # additional try with lowered childIndex
                    c.selectPosition(oldPosition)
        # in both cases, return selected node
        return self._outputPNode(c.p)
    #@+node:ekr.20210202183724.14: *4* insertPNode
    def insertPNode(self, p_package):
        '''Insert a node at given node, then select it once created, and finally return it'''
        c = self.c
        w_ap = p_package["node"]
        if not w_ap:
            return self._outputError("Error in insertPNode no param node")
        w_p = self._ap_to_p(w_ap)
        if not w_p:
            return self._outputError("Error in insertPNode no w_p node found")
        w_bunch = c.undoer.beforeInsertNode(w_p)
        w_newNode = w_p.insertAfter()
        w_newNode.setDirty()
        c.undoer.afterInsertNode(
            w_newNode, 'Insert Node', w_bunch)
        c.selectPosition(w_newNode)
        return self._outputPNode(c.p)
    #@+node:ekr.20210202183724.15: *4* insertNamedPNode
    def insertNamedPNode(self, p_package):
        '''Insert a node at given node, set its headline, select it and finally return it'''
        c = self.c
        w_newHeadline = p_package['text']
        w_ap = p_package['node']
        if not w_ap:
            return self._outputError("Error in insertNamedPNode no param node")
        w_p = self._ap_to_p(w_ap)
        if not w_p:
            return self._outputError("Error in insertNamedPNode no w_p node found")
        w_u = c.undoer.beforeInsertNode(w_p)
        w_newNode = w_p.insertAfter()
        # set this node's new headline
        w_newNode.h = w_newHeadline
        w_newNode.setDirty()
        c.undoer.afterInsertNode(
            w_newNode, 'Insert Node', w_u)
        c.selectPosition(w_newNode)
        # in any case, return selected node
        return self._outputPNode(c.p)
    #@+node:ekr.20210202183724.16: *4* undo
    def undo(self, p_paramUnused):
        '''Undo last un-doable operation'''
        c, u = self.c, self.c.undoer
        if u.canUndo():
            u.undo()
        # return selected node when done
        return self._outputPNode(c.p)

    #@+node:ekr.20210202183724.17: *4* redo
    def redo(self, p_paramUnused):
        '''Undo last un-doable operation'''
        c, u = self.c, self.c.undoer
        if u.canRedo():
            u.redo()
        # return selected node when done
        return self._outputPNode(c.p)
    #@+node:ekr.20210202110128.56: *4* sc.setOpenedFile
    def setOpenedFile(self, p_package):
        '''Choose the new active commander from array of opened file path/names by numeric index'''
        c = None
        w_openedCommanders = []
        for w_commander in g.app.commanders():
            if not w_commander.closed:
                w_openedCommanders.append(w_commander)
        w_index = p_package['index']
        if w_openedCommanders[w_index]:
            c = self.c = w_openedCommanders[w_index]
        if not c:
            return self._outputError('Error in setOpenedFile')
        c.closed = False
        self._create_gnx_to_vnode()
        w_result = {
            "total": self._getTotalOpened(),
            "filename": c.fileName(),
            "node": self._p_to_ap(c.p),
        }
        # maybe needed for frame wrapper
        c.selectPosition(c.p)
        return self.sendLeoBridgePackage("setOpened", w_result)
    #@+node:ekr.20210202110128.60: *3* bc.test
    def test(self, p_package):
        '''Utility test function for debugging'''
        return self.sendLeoBridgePackage('returned-key', p_package)
           
    #@+node:ekr.20210202110128.61: *3* getStates
    def getStates(self, p_package):
        """
        Gets the currently opened file's general states for UI enabled/disabled states
        such as undo available, file changed/unchanged
        """
        c = self.c
        w_states = {}
        if c:
            try:
                # 'dirty/changed' member
                w_states["changed"] = c.changed
                w_states["canUndo"] = c.canUndo()
                w_states["canRedo"] = c.canRedo()
                w_states["canDemote"] = c.canDemote()
                w_states["canPromote"] = c.canPromote()
                w_states["canDehoist"] = c.canDehoist()

            except Exception as e:
                g.trace('Error while getting states')
                print("Error while getting states", flush=True)
                print(str(e), flush=True)
        else:
            w_states["changed"] = False
            w_states["canUndo"] = False
            w_states["canRedo"] = False
            w_states["canDemote"] = False
            w_states["canPromote"] = False
            w_states["canDehoist"] = False

        return self.sendLeoBridgePackage("states", w_states)
    #@+node:ekr.20210202110128.62: *3* sc:Json
    #@+node:ekr.20210202110128.63: *4* pageUp
    def pageUp(self, p_unused):
        """Selects a node a couple of steps up in the tree to simulate page up"""
        c = self.c
        c.selectVisBack()
        c.selectVisBack()
        c.selectVisBack()
        return self._outputPNode(c.p)
    #@+node:ekr.20210202110128.64: *4* pageDown
    def pageDown(self, p_unused):
        """Selects a node a couple of steps down in the tree to simulate page down"""
        c = self.c
        c.selectVisNext()
        c.selectVisNext()
        c.selectVisNext()
        return self._outputPNode(c.p)

    #@+node:ekr.20210202110128.65: *3* Outline and Body Interaction
    #@+node:ekr.20210202110128.66: *4* getBodyStates
    def getBodyStates(self, p_ap):
        """
        Finds the language in effect at top of body for position p,
        Also returns the saved cursor position from last time node was accessed.
        """
        c = self.c
        if not p_ap:
            return self._outputError("Error in getLanguage, no param p_ap")

        w_p = self._ap_to_p(p_ap)
        if not w_p:
            print(f"in GBS -> P NOT FOUND gnx: {p_ap['gnx']!r} using c.p.gnx: {c.p.v.gnx}")
            w_p = c.p

        w_wrapper = c.frame.body.wrapper
        defaultPosition = {"line": 0, "col": 0}
        states = {
            'language': 'plain',
            # See BodySelectionInfo interface in types.d.ts
            'selection': {
                "gnx": w_p.v.gnx,
                "scroll": {
                    "start": defaultPosition,
                    "end": defaultPosition
                },
                "active": defaultPosition,
                "start": defaultPosition,
                "end": defaultPosition
            }
        }
        if w_p:
            aList = g.get_directives_dict_list(w_p)
            d = g.scanAtCommentAndAtLanguageDirectives(aList)

            language = (
                d and d.get('language') or
                g.getLanguageFromAncestorAtFileNode(w_p) or
                c.config.getString('target-language') or
                'plain'
            )

            w_scroll = w_p.v.scrollBarSpot
            w_active = w_p.v.insertSpot
            w_start = w_p.v.selectionStart
            w_end = w_p.v.selectionStart + w_p.v.selectionLength

            # get selection from wrapper instead if its the selected node
            if c.p.v.gnx == w_p.v.gnx:
                # print("in GBS -> SAME AS c.p SO USING FROM WRAPPER")
                w_active = w_wrapper.getInsertPoint()
                w_start, w_end = w_wrapper.getSelectionRange(True)
                w_scroll = w_wrapper.getYScrollPosition()

            # TODO : This conversion for scroll position may be unneeded (consider as lines only)
            # w_scrollI, w_scrollRow, w_scrollCol = c.frame.body.wrapper.toPythonIndexRowCol(w_Scroll)
            # compute line and column for the insertion point, and the start & end of selection
            w_activeI, w_activeRow, w_activeCol = c.frame.body.wrapper.toPythonIndexRowCol(
                w_active)
            w_startI, w_startRow, w_startCol = c.frame.body.wrapper.toPythonIndexRowCol(
                w_start)
            w_endI, w_endRow, w_endCol = c.frame.body.wrapper.toPythonIndexRowCol(
                w_end)

            states = {
                'language': language.lower(),
                'selection': {
                    "gnx": w_p.v.gnx,
                    "scroll": w_scroll,  # w_scroll was kept as-is
                    "active": {"line": w_activeRow, "col": w_activeCol},
                    "start": {"line": w_startRow, "col": w_startCol},
                    "end": {"line": w_endRow, "col": w_endCol}
                }
            }
        return self.sendLeoBridgePackage("bodyStates", states)
    #@+node:ekr.20210202110128.67: *4* getPNode
    def getPNode(self, p_ap):
        '''EMIT OUT a node, don't select it'''
        if not p_ap:
            return self._outputError("Error in getPNode no param p_ap")
        w_p = self._ap_to_p(p_ap)
        if not w_p:
            return self._outputError("Error in getPNode no w_p node found")
        return self._outputPNode(w_p)
    #@+node:ekr.20210202110128.68: *4* getChildren
    def getChildren(self, p_ap):
        '''EMIT OUT list of children of a node'''
        c = self.c
        if p_ap:
            w_p = self._ap_to_p(p_ap)
            return self._outputPNodes(w_p and w_p.children() or [])
        if c.hoistStack:
            return self._outputPNodes([c.hoistStack[-1].p])
        # Output all root children
        return self._outputPNodes(self._yieldAllRootChildren())
    #@+node:ekr.20210202110128.69: *4* getParent
    def getParent(self, p_ap):
        '''EMIT OUT the parent of a node, as an array, even if unique or empty'''
        if p_ap:
            w_p = self._ap_to_p(p_ap)
            if w_p and w_p.hasParent():
                return self._outputPNode(w_p.getParent())  # if not root
        return self._outputPNode()  # default empty for root as default

    #@+node:ekr.20210202110128.70: *4* getSelectedNode
    def getSelectedNode(self, p_unused):
        '''EMIT OUT Selected Position as an array, even if unique'''
        return self._outputPNode(self.c.p)
    #@+node:ekr.20210202110128.71: *4* getAllGnx
    def getAllGnx(self, p_unused):
        '''Get gnx array from all unique nodes'''
        c = self.c
        return self.sendLeoBridgePackage(
            "allGnx",
            [p.v.gnx for p in c.all_unique_positions(copy=False)])

    #@+node:ekr.20210202110128.72: *4* getBody
    def getBody(self, p_gnx):
        '''EMIT OUT body of a node'''
        #
        #### TODO : if not found, send code to prevent unresolved promise
        #           if 'document switch' occurred shortly before
        if p_gnx:
            w_v = self.c.fileCommands.gnxDict.get(p_gnx)  # vitalije
            if w_v:
                return self._outputBodyData(w_v.b)
        #
        # Send as empty to fix unresolved promise if 'document switch' occurred shortly before
        return self._outputBodyData()
    #@+node:ekr.20210202110128.73: *4* getBodyLength
    def getBodyLength(self, p_gnx):
        '''EMIT OUT body string length of a node'''
        if p_gnx:
            w_v = self.c.fileCommands.gnxDict.get(p_gnx)  # vitalije
            if w_v and w_v.b:
                return self.sendLeoBridgePackage("bodyLength", len(w_v.b))
        # TODO : May need to signal inexistent by self.sendLeoBridgePackage()
        return self.sendLeoBridgePackage("bodyLength", 0)  # empty as default

    #@+node:ekr.20210202110128.74: *4* setBody
    def setBody(self, p_package):
        '''Change Body text of a node'''
        w_gnx = p_package['gnx']
        w_body = p_package['body']
        for w_p in self.c.all_positions():
            if w_p.v.gnx == w_gnx:
                # TODO : Before setting undo and trying to set body, first check if different than existing body
                w_bunch = self.c.undoer.beforeChangeNodeContents(
                    w_p)  # setup undoable operation
                w_p.v.setBodyString(w_body)
                self.c.undoer.afterChangeNodeContents(
                    w_p, "Body Text", w_bunch)
                if self.c.p.v.gnx == w_gnx:
                    self.c.frame.body.wrapper.setAllText(w_body)
                if not self.c.isChanged():
                    self.c.setChanged()
                if not w_p.v.isDirty():
                    w_p.setDirty()
                break
        # additional forced string setting
        if w_gnx:
            w_v = self.c.fileCommands.gnxDict.get(w_gnx)  # vitalije
            if w_v:
                w_v.b = w_body
        return self._outputPNode(self.c.p)  # return selected node
        # return self.sendLeoBridgePackage()  # Just send empty as 'ok'

    #@+node:ekr.20210202110128.75: *4* setSelection
    def setSelection(self, p_package):
        '''
        Set cursor position and scroll position along with selection start and end.
        (For the currently selected node's body, if gnx matches only)
        Save those values on the commander's body "wrapper"
        See BodySelectionInfo interface in types.d.ts
        '''
        w_same = False  # Flag for actually setting values in the wrapper, if same gnx.
        w_wrapper = self.c.frame.body.wrapper
        w_gnx = p_package['gnx']
        w_body = ""
        w_v = None
        if self.c.p.v.gnx == w_gnx:
            # print('Set Selection! OK SAME GNX: ' + self.c.p.v.gnx)
            w_same = True
            w_v = self.c.p.v
        else:
            # ? When navigating rapidly - Check if this is a bug - how to improve
            # print('Set Selection! NOT SAME GNX: selected:' +
            #       self.c.p.v.gnx + ', package:' + w_gnx)
            w_v = self.c.fileCommands.gnxDict.get(w_gnx)

        if not w_v:
            print('ERROR : Set Selection! NOT SAME Leo Document')
            # ! FAILED (but return as normal)
            return self._outputPNode(self.c.p)

        w_body = w_v.b
        f_convert = g.convertRowColToPythonIndex
        w_active = p_package['active']
        w_start = p_package['start']
        w_end = p_package['end']

        # no convertion necessary, its given back later
        w_scroll = p_package['scroll']
        w_insert = f_convert(
            w_body, w_active['line'], w_active['col'])
        w_startSel = f_convert(
            w_body, w_start['line'], w_start['col'])
        w_endSel = f_convert(
            w_body, w_end['line'], w_end['col'])

        # print("setSelection (same as selected): " + str(w_same) + " w_insert " + str(w_insert) +
        #       " w_startSel " + str(w_startSel) + " w_endSel " + str(w_endSel))

        if w_same:
            w_wrapper.setSelectionRange(w_startSel, w_endSel, w_insert)
            w_wrapper.setYScrollPosition(w_scroll)
        else:
            pass

        # Set for v node no matter what
        w_v.scrollBarSpot = w_scroll
        w_v.insertSpot = w_insert
        w_v.selectionStart = w_startSel
        w_v.selectionLength = (
            w_endSel - w_startSel) if w_endSel > w_startSel else 0

        # When switching nodes, Leo's core saves the insert point, selection,
        # and vertical scroll position in the old (unselected) vnode. From v.init:

        # self.insertSpot = None
        #     # Location of previous insert point.
        # self.scrollBarSpot = None
        #     # Previous value of scrollbar position.
        # self.selectionLength = 0
        #     # The length of the selected body text.
        # self.selectionStart = 0
        #         # The start of the selected body text.

        # output selected node as 'ok'
        return self._outputPNode(self.c.p)
    #@+node:ekr.20210202110128.76: *4* setNewHeadline
    def setNewHeadline(self, p_package):
        '''Change Headline of a node'''
        w_newHeadline = p_package['text']
        w_ap = p_package['node']
        if w_ap:
            w_p = self._ap_to_p(w_ap)
            if w_p:
                # set this node's new headline
                w_bunch = self.c.undoer.beforeChangeNodeContents(w_p)
                w_p.h = w_newHeadline
                self.c.undoer.afterChangeNodeContents(
                    w_p, 'Change Headline', w_bunch)
                return self._outputPNode(w_p)
        return self._outputError("Error in setNewHeadline")

    #@+node:ekr.20210202110128.77: *4* setSelectedNode
    def setSelectedNode(self, p_ap):
        '''Select a node, or the first one found with its GNX'''
        c = self.c
        if p_ap:
            w_p = self._ap_to_p(p_ap)
            if w_p:
                if c.positionExists(w_p):
                    # set this node as selection
                    c.selectPosition(w_p)
                else:
                    w_foundPNode = self._findPNodeFromGnx(p_ap['gnx'])
                    if w_foundPNode:
                        c.selectPosition(w_foundPNode)
                    else:
                        print("Set Selection node does not exist! ap was:" +
                              json.dumps(p_ap), flush=True)
        # Return the finally selected node
        return self._outputPNode(c.p)

    #@+node:ekr.20210202110128.78: *4* expandNode
    def expandNode(self, p_ap):
        '''Expand a node'''
        if p_ap:
            w_p = self._ap_to_p(p_ap)
            if w_p:
                w_p.expand()
        return self.sendLeoBridgePackage()  # Just send empty as 'ok'

    #@+node:ekr.20210202110128.79: *4* collapseNode
    def collapseNode(self, p_ap):
        '''Collapse a node'''
        if p_ap:
            w_p = self._ap_to_p(p_ap)
            if w_p:
                w_p.contract()
        return self.sendLeoBridgePackage()  # Just send empty as 'ok'
    #@+node:ekr.20210202110128.80: *4* _yieldAllRootChildren
    def _yieldAllRootChildren(self):
        '''Return all root children P nodes'''
        c = self.c
        p = c.rootPosition()
        while p:
            yield p
            p.moveToNext()
    #@+node:ekr.20210202110128.81: *4* _findPNodeFromGnx
    def _findPNodeFromGnx(self, p_gnx):
        '''Return first p node with this gnx or false'''
        for p in self.c.all_unique_positions():
            if p.v.gnx == p_gnx:
                return p
        return False

    #@+node:ekr.20210202110128.82: *3* leoFlexx Conversion Functions
    #@+node:ekr.20210202110128.83: *4* _create_gnx_to_vnode
    def _create_gnx_to_vnode(self):
        '''Make the first gnx_to_vnode array with all unique nodes'''
        t1 = time.process_time()
        self.gnx_to_vnode = {
            v.gnx: v for v in self.c.all_unique_nodes()}
        # This is likely the only data that ever will be needed.
        if 0:
            print('app.create_all_data: %5.3f sec. %s entries' % (
                (time.process_time()-t1), len(list(self.gnx_to_vnode.keys()))), flush=True)
        self._test_round_trip_positions()

    #@+node:ekr.20210202110128.84: *4* _test_round_trip_positions
    def _test_round_trip_positions(self):
        '''(From Leo plugin leoflexx.py) Test the round tripping of p_to_ap and ap_to_p.'''
        # Bug fix: p_to_ap updates app.gnx_to_vnode. Save and restore it.
        old_d = self.gnx_to_vnode.copy()
        old_len = len(list(self.gnx_to_vnode.keys()))
        # t1 = time.process_time()
        qtyAllPositions = 0
        for p in self.c.all_positions():
            qtyAllPositions += 1
            ap = self._p_to_ap(p)
            p2 = self._ap_to_p(ap)
            assert p == p2, (repr(p), repr(p2), repr(ap))
        gnx_to_vnode = old_d
        new_len = len(list(gnx_to_vnode.keys()))
        assert old_len == new_len, (old_len, new_len)
        # print('Leo file opened. Its outline contains ' + str(qtyAllPositions) + " nodes positions.", flush=True)
        # print(('Testing app.test_round_trip_positions for all nodes: Total time: %5.3f sec.' % (time.process_time()-t1)), flush=True)
    #@+node:ekr.20210202110128.85: *4* _ap_to_p
    def _ap_to_p(self, ap):
        '''
        (From Leo plugin leoflexx.py) Convert an archived position to a true Leo position.
        Return false if no key
        '''
        childIndex = ap['childIndex']

        try:
            v = self.gnx_to_vnode[ap['gnx']]  # Trap this
            stack = [
                (self.gnx_to_vnode[d['gnx']], d['childIndex'])
                for d in ap['stack']
            ]
        except Exception:
            return False

        return leoNodes.position(v, childIndex, stack)

    #@+node:ekr.20210202110128.86: *4* _p_to_ap
    def _p_to_ap(self, p):
        '''(From Leo plugin leoflexx.py) Converts Leo position to a serializable archived position.'''
        if not p.v:
            print('app.p_to_ap: no p.v: %r %s' % (p), flush=True)
            assert False
        p_gnx = p.v.gnx
        # * Expand gnx-vnode translation table for any new node encountered
        if p_gnx not in self.gnx_to_vnode:
            self.gnx_to_vnode[p_gnx] = p.v
        # * necessary properties for outline
        w_ap = {
            'childIndex': p._childIndex,
            'gnx': p.v.gnx,
            'level': p.level(),
            'headline': p.h,
            'stack': [{
                'gnx': stack_v.gnx,
                'childIndex': stack_childIndex,
                'headline': stack_v.h,
            } for (stack_v, stack_childIndex) in p.stack],
        }
        # TODO : Convert all those booleans into an 8 bit integer 'status' flag
        if p.v.u:
            w_ap['u'] = p.v.u
        if bool(p.b):
            w_ap['hasBody'] = True
        if p.hasChildren():
            w_ap['hasChildren'] = True
        if p.isCloned():
            w_ap['cloned'] = True
        if p.isDirty():
            w_ap['dirty'] = True
        if p.isExpanded():
            w_ap['expanded'] = True
        if p.isMarked():
            w_ap['marked'] = True
        if p.isAnyAtFileNode():
            w_ap['atFile'] = True
        if p == self.c.p:
            w_ap['selected'] = True
        return w_ap
    #@-others
#@+node:ekr.20210202110128.87: ** printAction
def printAction(p_param):
    w_action = p_param["action"]
    print(f"*ACTION* {w_action}, id {p_param['id']}", flush=True)
#@+node:ekr.20210202110128.88: ** main (c:\test)
def main():
    '''python script for leo integration via leoBridge'''
    # from leo.core import leoGlobals as g
    global wsHost, wsPort
    print("Starting LeoBridge... (Launch with -h for help)", flush=True)
    # replace default host address and port if provided as arguments
    #@+others
    #@+node:ekr.20210202110128.89: *3* async def asyncInterval (create connection???)
    # A basic example loop
    async def asyncInterval(timeout):

        print('asyncInterval.timeout', timeout)
        n = 0
        while True:
            await asyncio.sleep(timeout)
            n += 1
            await controller.asyncOutput(
                f'{{"counter": {n}, "time": {n*timeout}}}')
    #@+node:ekr.20210202110128.90: *3* async def ws_handler (calls websocket.send)
    async def ws_handler(websocket, path):
        """
        The ws_handler: server.ws_server.
        
        This gets turned into a WebSocketServer object.

        It must be a coroutine accepting two arguments: a WebSocketServerProtocol and the request URI.
        """
        try:
            controller.initConnection(websocket)
            # Start by sending empty as 'ok'
            await websocket.send(controller.sendLeoBridgePackage())
            controller.logSignon()
            async for w_message in websocket:
                w_param = json.loads(w_message)
                if w_param and w_param['action']:
                    w_action = w_param['action']
                    w_actionParam = w_param['param']
                    # printAction(w_param)  # Debug output
                    # * Storing id of action in global var instead of passing as parameter
                    controller.setActionId(w_param['id'])
                    # ! functions called this way need to accept at least a parameter other than 'self'
                    # ! See : getSelectedNode and getAllGnx
                    # TODO : Block attempts to call functions starting with underscore or reserved
                    #
                    w_func = getattr(controller, w_action, None)  # crux
                    if w_func:
                        # Is Filtered by Leo Bridge Integration Controller
                        w_answer = w_func(w_actionParam)
                    else:
                        # Attempt to execute the command directly on the commander/subcommander
                        w_answer = controller.leoCommand(
                            w_action, w_actionParam)
                else:
                    w_answer = "Error in processCommand"
                    print(w_answer, flush=True)
                await websocket.send(w_answer)
        except websockets.exceptions.ConnectionClosedError:
            print("Websocket connection closed", flush=True)
        except Exception:
            print('Exception in leobridgeserver.py!', flush=True)
            # Like g.es_exception()...
            typ, val, tb = sys.exc_info()
            for line in traceback.format_exception(typ, val, tb):
                print(line.rstrip(), flush=True)
        finally:
            asyncio.get_event_loop().stop()
    #@+node:ekr.20210202110128.91: *3* get_args
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

    controller = ServerController()
    
    # Create a _WindowsSelectorEventLoop object.
    loop = asyncio.get_event_loop()  
    # print('event loop', loop)
    
    # Create websockets.server.Serve object.
    # This is slow because it Leo's bridge starts all of Leo.
    server = websockets.serve(ws_handler=ws_handler, host=wsHost, port=wsPort)
    
    # Create websockets.server.WebSocketServer object.
    loop.run_until_complete(server)
     
    # Continue.
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

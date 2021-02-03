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
import leo.core.leoFrame as leoFrame
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
        #
        # Send Log pane output to the client's log pane.
        g.es = self.es  
        #
        # Complete the initialization, as in LeoApp.initApp.
        g.app.idleTimeManager = leoApp.IdleTimeManager()
        g.app.idleTimeManager.start()
        g.app.externalFilesController = leoExternalFiles.ExternalFilesController(None)
        t2 = time.process_time()
        print(f"ServerController: init leoBridge in {t2-t1:4.2} sec.")
    #@+node:ekr.20210202110128.31: *4* sc._asyncIdleLoop
    async def _asyncIdleLoop(self, seconds, fn):
        """Call function fn every seconds"""
        while True:
            await asyncio.sleep(seconds)
            fn(self)
    #@+node:ekr.20210202110128.52: *4* sc.initConnection
    def initConnection(self, webSocket):
        """Begin the connection."""
        self.webSocket = webSocket
        self.loop = asyncio.get_event_loop()

    #@+node:ekr.20210202110128.42: *4* sc.logSignon
    def logSignon(self):
        '''Simulate the initial Leo Log Entry'''
        if self.loop:
            g.app.computeSignon()
            g.es(g.app.signon)
            g.es(g.app.signon1)
        else:
            print('logSignon: no loop', flush=True)
    #@+node:ekr.20210202110128.43: *4* sc.setActionId
    def setActionId(self, the_id):
        self.currentActionId = the_id

    #@+node:ekr.20210202193210.1: *3* sc:Commands
    #@+node:ekr.20210202110128.41: *4* sc.applyConfig
    def applyConfig(self, config):
        '''Got the configuration from client'''
        self.config = config
        return self.send("")  # Send empty as 'ok'
    #@+node:ekr.20210202110128.54: *4* sc.leoCommand & helper (not called yet!)
    def leoCommand(self, command, package):
        '''
        Generic call to a method in Leo's Commands class or any subcommander class.

        The ap position node is to be selected before having the command run,
        while the keepSelection parameter specifies wether the original position should be re-selected.
        The whole of those operations is to be undoable as one undo step.

        command: a method name (a string).
        ap: an archived position.
        keepSelection: preserve the current selection, if possible.
        '''
        c = self.c
        g.trace(repr(command), repr(package))  ###
        # Check the args.
        err, p = self._p_from_package(package)
        if err:
            return err
        # Execute the command.
        func = self._get_commander_method(command)
        if not func:
            return self._outputError(f"command not found: {command!r}", tag='leoCommand')
        # Easy case: ignore the previous position.
        keep = "keep" in package and package["keep"]  ### Convert to bool ???
        if p == c.p or not keep:
            func(event=None)
            return self._outputPNode(c.p)
        # Harder case: try to restore the previous position.
        oldPosition = c.p
        c.selectPosition(p)
        func(event=None)
        # Careful: the old position might not exist now.
        if c.positionExists(oldPosition):
            c.selectPosition(oldPosition)
        return self._outputPNode(c.p)
    #@+node:ekr.20210202110128.53: *5* sc._get_commander_method
    def _get_commander_method(self, command):
        """ Return the given method (command) in the Commands class or subcommanders."""
        c = self.c
        # First, try the Commands class.
        func = getattr(c, command, None)
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
                func = getattr(subcommander, command, None)
                if func:
                    return func
        return None
    #@+node:ekr.20210202110128.60: *4* sc.test
    def test(self, package):
        '''Utility test function for debugging'''
        return self.send('returned-key', package)
           
    #@+node:ekr.20210202193709.1: *4* sc:button commands
    #@+node:ekr.20210202183724.4: *5* sc.clickButton
    def clickButton(self, package):
        '''Handles buttons clicked in client from the '@button' panel'''
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
        return self._outputPNode(c.p)
    #@+node:ekr.20210202183724.3: *5* sc.removeButton
    def removeButton(self, package):
        '''Removes an entry from the buttonsDict by index string'''
        c, d = self.c, self.c.theScriptingController.buttonsDict
        index = package['index']
        if index in d:
            del d[index]
        return self._outputPNode(c.p)
    #@+node:ekr.20210202193642.1: *4* sc:file commands
    #@+node:ekr.20210202110128.57: *5* sc.openFile
    def openFile(self, filename):
        """
        Open a leo file with the given filename. Create a new document if no name.
        """
        c, found, tag = None, False, 'openFile'
        openCommanders = [z for z in g.app.commanders() if not c.closed]
        if filename:
            for c in openCommanders:
                if c.fileName() == filename:
                    found = True
        if not found:
            c = self.bridge.openLeoFile(filename)
        if not c:
            return self._outputError(f"can not open {filename!r}", tag)
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
        return self.send("opened", result)
    #@+node:ekr.20210202182311.1: *5* sc.openFiles
    def openFiles(self, package):
        """
        Opens an array of leo files
        Returns an object that contains the last 'opened' member.
        """
        c, tag = None, 'openFiles'
        filename, files = None, []
        if "files" in package:
            files = package["files"]
        openCommanders = [z for z in g.app.commanders() if not z.closed]
        for filename in files:
            found = False
            # If not empty string (asking for New file) then check if already opened
            if filename:
                for c in openCommanders:
                    if c.fileName() == filename:
                        found = True
            if not found:
                if os.path.isfile(filename):
                    c = self.bridge.openLeoFile(filename)  # create self.c
            if c:
                c.closed = False
                self.c = c
                c.frame.body.wrapper = leoFrame.StringTextWrapper(c, 'bodyWrapper')
                c.selectPosition(c.p)
        # Done with the last one, it's now the selected commander. Check again just in case.
        if not c:
            return self._outputError(f"file not found: {filename!r}", tag)
        self._create_gnx_to_vnode()
        result = {
            "filename": c.fileName(),
            "node": self._p_to_ap(c.p),
            "total": len(openCommanders),
        }
        return self.send("opened", result)
    #@+node:ekr.20210202110128.58: *5* sc.closeFile
    def closeFile(self, package):
        """
        Closes a leo file. A file can then be opened with "openFile"
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
                return self.send('closed', False)
        # Select the first open commander.
        openCommanders = [z for z in g.app.commanders() if not z.closed]
        if not openCommanders:
            return self.send("closed", {"total": 0})
        self.c = openCommanders[0]
        self._create_gnx_to_vnode()
        result = {
            "filename": c.fileName(),
            "node": self._p_to_ap(self.c.p),
            "total": len(openCommanders),
        }
        return self.send("closed", result)
    #@+node:ekr.20210202183724.1: *5* sc.saveFile
    def saveFile(self, package):
        '''Saves the leo file. New or dirty derived files are rewritten'''
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
        return self.send("")  # Send empty as 'ok'
    #@+node:ekr.20210202110128.56: *5* sc.setOpenedFile
    def setOpenedFile(self, package):
        '''Choose the new active commander from array of opened file path/names by numeric index'''
        err, p = self._p_from_package(package)
        if err:
            return err
        openedCommanders = [z for z in g.app.commanders() if not z.closed]
        index = package['index']
        if index >= len(openedCommanders):
            return self._outputError(f"invalid index: {index!r}", tag='setOpenedFile')
        c = self.c = openedCommanders[index]
        c.closed = False
        self._create_gnx_to_vnode()
        c.selectPosition(c.p) # maybe needed for frame wrapper
        result = {
            "filename": c.fileName(),
            "node": self._p_to_ap(c.p),
            "total": len(g.app.commanders()),
        }
        return self.send("setOpened", result)
    #@+node:ekr.20210202193505.1: *4* sc:getter commands
    #@+node:ekr.20210202110128.71: *5* sc.getAllGnx
    def getAllGnx(self, unused):
        '''Get gnx array from all unique nodes'''
        c = self.c
        result = [p.v.gnx for p in c.all_unique_positions(copy=False)]
        return self.send("allGnx", result)

    #@+node:ekr.20210202110128.72: *5* sc.getBody
    def getBody(self, gnx):
        '''EMIT OUT body of a node'''
        #
        #### TODO : if not found, send code to prevent unresolved promise
        #           if 'document switch' occurred shortly before
        if gnx:
            v = self.c.fileCommands.gnxDict.get(gnx)  # vitalije
            if v:
                return self.send("bodyData", v.b)
        #
        # Send as empty to fix unresolved promise if 'document switch' occurred shortly before
        return self.send("bodyData", "")

    #@+node:ekr.20210202110128.73: *5* sc.getBodyLength
    def getBodyLength(self, gnx):
        '''EMIT OUT body string length of a node'''
        if gnx:
            v = self.c.fileCommands.gnxDict.get(gnx)  # vitalije
            if v and v.b:
                return self.send("bodyLength", len(v.b))
        return self.send("bodyLength", 0)  # empty as default

    #@+node:ekr.20210202110128.66: *5* sc.getBodyStates
    def getBodyStates(self, ap):
        """
        Finds the language in effect at top of body for position p,
        Also returns the saved cursor position from last time node was accessed.
        """
        c, wrapper = self.c, self.c.frame.body.wrapper
        err, p = self._p_from_ap(ap)
        if err:
            return err
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
        if p:
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
        return self.send("bodyStates", states)
    #@+node:ekr.20210202183724.2: *5* sc.getButtons
    def getButtons(self, package):
        '''Gets the currently opened file's @buttons list'''
        c = self.c
        buttons = []
        if c and c.theScriptingController and c.theScriptingController.buttonsDict:
            d = c.theScriptingController.buttonsDict
            for key in d:
                entry = {"name": d[key], "index": str(key)}
                buttons.append(entry)
        return self.send("buttons", buttons)

    #@+node:ekr.20210202110128.68: *5* sc.getChildren
    def getChildren(self, ap):
        '''EMIT OUT list of children of a node'''
        c = self.c
        if ap:
            p = self._ap_to_p(ap)
            nodes = p and p.children() or []
        elif c.hoistStack:
            nodes = [c.hoistStack[-1].p]
        else:
            # Output all top-level nodes.
            nodes = [z for z in c.rootPosition().self_and_siblings()]
        return self._outputPNodes(nodes)
    #@+node:ekr.20210202183724.5: *5* sc.getCommands & helpers
    def getCommands(self, package):
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
        return self.send("commands", result)
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

    #@+node:ekr.20210202110128.55: *5* sc.getOpenedFiles
    def getOpenedFiles(self, package):
        '''Return array of opened file path/names to be used as openFile parameters to switch files'''
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
        return self.send("openedFiles", result)
    #@+node:ekr.20210202110128.69: *5* sc.getParent
    def getParent(self, ap):
        '''EMIT OUT the parent of a node, as an array, even if unique or empty'''
        if ap:
            p = self._ap_to_p(ap)
            if p and p.hasParent():
                return self._outputPNode(p.getParent())  # if not root
        return self._outputPNode(None)  # root is the default
    #@+node:ekr.20210202110128.67: *5* sc.getPNode
    def getPNode(self, ap):
        '''EMIT OUT a node, don't select it'''
        c = self.c
        err, p = self._p_from_ap(ap)
        return err if err else self._outputPNode(c.p)  # Don't select p.
    #@+node:ekr.20210202110128.70: *5* sc.getSelectedNode
    def getSelectedNode(self, unused):
        '''EMIT OUT Selected Position as an array, even if unique'''
        return self._outputPNode(self.c.p)
    #@+node:ekr.20210202110128.61: *5* sc.getStates
    def getStates(self, package):
        """
        Gets the currently opened file's general states for UI enabled/disabled states
        such as undo available, file changed/unchanged
        """
        c = self.c
        states = {}
        # Set the defaults.
        states["changed"] = False
        states["canUndo"] = False
        states["canRedo"] = False
        states["canDemote"] = False
        states["canPromote"] = False
        states["canDehoist"] = False
        if c:
            try:
                # 'dirty/changed' member
                states["changed"] = c.changed
                states["canUndo"] = c.canUndo()
                states["canRedo"] = c.canRedo()
                states["canDemote"] = c.canDemote()
                states["canPromote"] = c.canPromote()
                states["canDehoist"] = c.canDehoist()
            except Exception as e:
                g.trace('Error while getting states')
                print("Error while getting states", flush=True)
                print(str(e), flush=True)
        return self.send("states", states)
    #@+node:ekr.20210202193540.1: *4* sc:node commands (setters)
    #@+node:ekr.20210202110128.81: *5* sc._gnx_to_p
    def _gnx_to_p(self, gnx):
        '''Return first p node with this gnx or None'''
        for p in self.c.all_unique_positions():
            if p.v.gnx == gnx:
                return p
        return None

    #@+node:ekr.20210202183724.11: *5* sc.clonePNode
    def clonePNode(self, package):
        '''Clone a node, return it, if it was also the current selection, otherwise try not to select it'''
        c = self.c
        err, p = self._p_from_package(package)
        if err:
            return err
        if p == c.p:
            c.clone()
            return self._outputPNode(c.p)
        # ??? Retain previous position ???
        oldPosition = c.p
        c.selectPosition(p)
        c.clone()
        if c.positionExists(oldPosition):
            c.selectPosition(oldPosition)
        return self._outputPNode(c.p)

    #@+node:ekr.20210202110128.79: *5* sc.collapseNode
    def collapseNode(self, ap):
        '''Collapse a node'''
        if ap:
            p = self._ap_to_p(ap)
            if p:
                p.contract()
        return self.send("")  # Just send empty as 'ok'
    #@+node:ekr.20210202183724.12: *5* sc.cutPNode
    def cutPNode(self, package):
        '''
        Cut a node, don't select it.
        Try to keep selection, then return the selected node that remains
        '''
        c = self.c
        err, p = self._p_from_package(package)
        if err:
            return err
        if p == c.p:
            c.cutOutline()
            return self._outputPNode(c.p)
        oldPosition = c.p  
        c.selectPosition(p)
        c.cutOutline()
        if c.positionExists(oldPosition):
            c.selectPosition(oldPosition)
            return self._outputPNode(c.p)
        ### Experimental.
        oldPosition._childIndex = oldPosition._childIndex-1
        if c.positionExists(oldPosition):
            c.selectPosition(oldPosition)
        return self._outputPNode(c.p)
    #@+node:ekr.20210202183724.13: *5* sc.deletePNode
    def deletePNode(self, package):
        '''Delete a node, don't select it. Try to keep selection, then return the selected node that remains'''
        c = self.c
        err, p = self._p_from_package(package)
        if err:
            return err
        if p == c.p:
            c.deleteOutline()
            return self._outputPNode(c.p)
        oldPosition = c.p  
        c.selectPosition(p)
        c.deleteOutline()
        if c.positionExists(oldPosition):
            c.selectPosition(oldPosition)
            return self._outputPNode(c.p)
        ### Experimental.
        oldPosition._childIndex = oldPosition._childIndex-1
        if c.positionExists(oldPosition):
            c.selectPosition(oldPosition)
        return self._outputPNode(c.p)
    #@+node:ekr.20210202110128.78: *5* sc.expandNode
    def expandNode(self, ap):
        '''Expand a node'''
        if ap:
            p = self._ap_to_p(ap)
            if p:
                p.expand()
        return self.send("")  # Just send empty as 'ok'

    #@+node:ekr.20210202183724.15: *5* sc.insertNamedPNode
    def insertNamedPNode(self, package):
        '''Insert a node at given node, set its headline, select it and finally return it'''
        c, u = self.c, self.c.undoer
        err, p = self._p_from_package(package)
        if err:
            return err
        newHeadline = 'text' in package and package['text']
        bunch = u.beforeInsertNode(p)
        newNode = p.insertAfter()
        newNode.h = newHeadline
        newNode.setDirty()
        u.afterInsertNode(newNode, 'Insert Node', bunch)
        c.selectPosition(newNode)
        return self._outputPNode(c.p)
    #@+node:ekr.20210202183724.14: *5* sc.insertPNode
    def insertPNode(self, package):
        '''Insert and slect a new node.'''
        c, u = self.c, self.c.undoer
        err, p = self._p_from_package(package)
        if err:
            return err
        bunch = u.beforeInsertNode(p)
        newNode = p.insertAfter()
        newNode.setDirty()
        u.afterInsertNode(newNode, 'Insert Node', bunch)
        c.selectPosition(newNode)
        return self._outputPNode(c.p)  # Select the new node.
    #@+node:ekr.20210202183724.9: *5* sc.markPNode
    def markPNode(self, package):
        '''Mark a node, don't select it'''
        c = self.c
        err, p = self._p_from_package(package)
        if err:
            return err
        p.setMarked()
        return self._outputPNode(c.p)  # Don't select p.
    #@+node:ekr.20210202110128.64: *5* sc.pageDown
    def pageDown(self, unused):
        """Selects a node a couple of steps down in the tree to simulate page down"""
        c = self.c
        c.selectVisNext()
        c.selectVisNext()
        c.selectVisNext()
        return self._outputPNode(c.p)

    #@+node:ekr.20210202110128.63: *5* sc.pageUp
    def pageUp(self, unused):
        """Selects a node a couple of steps up in the tree to simulate page up"""
        c = self.c
        c.selectVisBack()
        c.selectVisBack()
        c.selectVisBack()
        return self._outputPNode(c.p)
    #@+node:ekr.20210202183724.17: *5* sc.redo
    def redo(self, unused):
        '''Undo last un-doable operation'''
        c, u = self.c, self.c.undoer
        if u.canRedo():
            u.redo()
        return self._outputPNode(c.p)
    #@+node:ekr.20210202110128.74: *5* sc.setBody
    def setBody(self, package):
        '''Change Body text of a node'''
        c, u = self.c, self.c.undoer
        gnx = package['gnx']
        body = package['body']
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
        # additional forced string setting
        if gnx:
            v = c.fileCommands.gnxDict.get(gnx)  # vitalije
            if v:
                v.b = body
        return self._outputPNode(c.p)

    #@+node:ekr.20210202110128.76: *5* sc.setNewHeadline
    def setNewHeadline(self, package):
        '''Change a node's headline.'''
        u = self.c.undoer
        err, p = self._p_from_package(package)
        if err:
            return err
        headline = 'text' in package and package['text']  ### Check for headline.
        bunch = u.beforeChangeNodeContents(p)
        p.h = headline
        u.afterChangeNodeContents(p, 'Change Headline', bunch)
        return self._outputPNode(p)
    #@+node:ekr.20210202110128.77: *5* sc.setSelectedNode
    def setSelectedNode(self, ap):
        '''Select a node, or the first one found with its GNX'''
        c = self.c
        if ap:
            p = self._ap_to_p(ap)
            if p:
                if c.positionExists(p):
                    c.selectPosition(p)
                else:
                    found_p = self._gnx_to_p(ap['gnx'])
                    if found_p:
                        c.selectPosition(found_p)
                    else:
                        print("Set Selection node does not exist! ap was:" +
                              json.dumps(ap), flush=True)
        return self._outputPNode(c.p)

    #@+node:ekr.20210202110128.75: *5* sc.setSelection
    def setSelection(self, package):
        '''
        Set cursor position and scroll position along with selection start and end.
        (For the currently selected node's body, if gnx matches only)
        Save those values on the commander's body "wrapper"
        See BodySelectionInfo interface in types.d.ts
        '''
        c = self.c
        same = False  # True: set values in the wrapper, if same gnx.
        wrapper = self.c.frame.body.wrapper
        gnx = package['gnx']
        body = ""
        v = None
        if c.p.v.gnx == gnx:
            same = True
            v = c.p.v
        else:
            ### Is this a bug?
            print(f"Set Selection: different gnx: selected: {c.p.v.gnx!r} package: {gnx}")
            v = c.fileCommands.gnxDict.get(gnx)
        if not v:
            print('Set Selection: different Leo Document')
            return self._outputPNode(c.p) # Failed, but return as normal.
        body = v.b
        f_convert = g.convertRowColToPythonIndex
        active = package['active']
        start = package['start']
        end = package['end']
        # no convertion necessary, its given back later
        scroll = package['scroll']
        insert = f_convert(body, active['line'], active['col'])
        startSel = f_convert(body, start['line'], start['col'])
        endSel = f_convert(body, end['line'], end['col'])
        if same:
            wrapper.setSelectionRange(startSel, endSel, insert)
            wrapper.setYScrollPosition(scroll)
        else:
            pass
        # Set for v node no matter what
        v.scrollBarSpot = scroll
        v.insertSpot = insert
        v.selectionStart = startSel
        v.selectionLength = abs(endSel - endSel)
        ### From v.init:
            # self.insertSpot = None
            # self.scrollBarSpot = None
            # self.selectionLength = 0
            # self.selectionStart = 0
        return self._outputPNode(c.p)
    #@+node:ekr.20210202183724.16: *5* sc.undo
    def undo(self, unused):
        '''Undo last un-doable operation'''
        c, u = self.c, self.c.undoer
        if u.canUndo():
            u.undo()
        return self._outputPNode(c.p)

    #@+node:ekr.20210202183724.10: *5* sc.unmarkPNode
    def unmarkPNode(self, package):
        '''Unmark a node, don't select it'''
        c = self.c
        err, p = self._p_from_package(package)
        if err:
            return err
        p.clearMarked()
        return self._outputPNode(c.p)  # Don't select p.
    #@+node:ekr.20210202194141.1: *3* sc:Output
    #@+node:ekr.20210203081126.1: *4* sc._outputError
    def _outputError(self, message, tag):
        # Output to this server's running console
        print(f"Error in {tag}: {message}", flush=True)
        return {
            "id": self.currentActionId,
            "error": f"{tag}: {message}",
        }
    #@+node:ekr.20210203083722.1: *4* sc._err_no_position
    def _err_no_position(self, ap, tag):
        return self._outputError(f"position not found. ap: {ap!r}", tag)
    #@+node:ekr.20210202110128.49: *4* sc._outputPNode & _outputPNodes
    def _outputPNode(self, node):
        return self.send("node", self._p_to_ap(node) if node else None)

    def _outputPNodes(self, position_list):
        # Multiple nodes, plural.
        return self.send("nodes", [self._p_to_ap(p) for p in position_list])
    #@+node:ekr.20210202110128.44: *4* sc.async def asyncOutput
    async def asyncOutput(self, json):
        '''Output json string to the websocket'''
        if self.webSocket:
            await self.webSocket.send(bytes(json, 'utf-8'))
        else:
            g.trace(f"no web socket. json: {json}", flush=True)
    #@+node:ekr.20210202110128.51: *4* sc.es
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
        package = {"async": "log", "log": s}
        self.sendAsyncOutput(package)

    #@+node:ekr.20210202110128.45: *4* sc.send
    def send(self, key=None, any=None):
        package = {
            "id": self.currentActionId,
        }
        if key:
            package [key] = any  # add [key]?:any
        # Send as json.
        return json.dumps(package, separators=(',', ':')) 
    #@+node:ekr.20210202110128.39: *4* sc.sendAsyncOutput
    def sendAsyncOutput(self, package):
        if "async" not in package:
            print('[sendAsyncOutput] Error async member missing in package parameter')
            print(json.dumps(package, separators=(',', ':')), flush=True)
            return
        if self.loop:
            self.loop.create_task(self.asyncOutput(
                json.dumps(package, separators=(',', ':'))))
        else:
            print('[sendAsyncOutput] Error loop not ready' +
                json.dumps(package, separators=(',', ':')))
    #@+node:ekr.20210202193334.1: *3* sc:Serialization
    #@+node:ekr.20210202110128.85: *4* sc._ap_to_p
    def _ap_to_p(self, ap):
        '''
        (From Leo plugin leoflexx.py) Convert an archived position to a true Leo position.
        Return None if no key
        '''
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
        '''Make the first gnx_to_vnode array with all unique nodes'''
        self.gnx_to_vnode = {
            v.gnx: v for v in self.c.all_unique_nodes()
        }
        self._test_round_trip_positions()
    #@+node:ekr.20210203084135.1: *4* sc._p_from_ap
    def _p_from_ap(self, ap):
        """
        Resolve archived position to a position, with error reporting.
        Return (err, p)
        """
        c = self.c
        p = self._ap_to_p(ap)
        callers = g.callers().split(',')
        tag = callers[-1]
        if not p:
            err = self._err_no_position(ap, tag)
            return err, None
        if not c.positionExists(p):
            err = self._outputError(f"position does not exist. ap: {ap!r}", tag)
            return err, None
        return None, p
    #@+node:ekr.20210203082009.1: *4* sc._p_from_package
    def _p_from_package(self, package):
        """
        Resolve package["node"] to a position.
        Return (err, p)
        """
        c = self.c
        callers = g.callers().split(',')
        tag = callers[-1]
        try:
            ap = package["node"]
        except Exception:
            ap = None
        if not ap:
            err = self._outputError(f"no ap in package: {package!r}", tag)
            return err, None
        p = self._ap_to_p(ap)
        if not p:
            err = self._err_no_position(ap, tag)
            return err, None
        if not c.positionExists(p):
            err = self._outputError(f"position does not exist. ap: {ap!r}", tag)
            return err, None
        return None, p
    #@+node:ekr.20210202110128.86: *4* sc._p_to_ap
    def _p_to_ap(self, p):
        '''(From Leo plugin leoflexx.py) Converts Leo position to a serializable archived position.'''
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
        '''(From Leo plugin leoflexx.py) Test the round tripping of p_to_ap and ap_to_p.'''
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
            await websocket.send(controller.send())
            controller.logSignon()
            async for w_message in websocket:
                w_param = json.loads(w_message)
                if w_param and w_param['action']:
                    w_action = w_param['action']
                    w_actionParam = w_param['param']
                    # Storing id of action in global var instead of passing as parameter
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

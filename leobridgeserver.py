#! python3
import leo.core.leoBridge as leoBridge
import leo.core.leoNodes as leoNodes
from leo.core.leoGui import StringFindTabManager
import asyncio
import getopt
import json
import os.path
import sys
import time
import traceback
import websockets
# server defaults
wsHost = "localhost"
wsPort = 32125

# To help in printout
commonActions = ["getChildren", "getBody", "getBodyLength"]

# Special string signals server startup success
SERVER_STARTED_TOKEN = "LeoBridge started"


class IdleTimeManager:
    """
    A singleton class to manage idle-time handling. This class handles all
    details of running code at idle time, including running 'idle' hooks.

    Any code can call g.app.idleTimeManager.add_callback(callback) to cause
    the callback to be called at idle time forever.
    """
    # TODO : REVISE/REPLACE WITH OWN SYSTEM

    def __init__(self, g):
        """Ctor for IdleTimeManager class."""
        self.g = g
        self.callback_list = []
        self.timer = None
        self.on_idle_count = 0

    def add_callback(self, callback):
        """Add a callback to be called at every idle time."""
        self.callback_list.append(callback)

    def on_idle(self, timer):
        """IdleTimeManager: Run all idle-time callbacks."""
        if not self.g.app:
            return
        if self.g.app.killed:
            return
        if not self.g.app.pluginsController:
            self.g.trace('No g.app.pluginsController', self.g.callers())
            timer.stop()
            return  # For debugger.
        self.on_idle_count += 1
        # Handle the registered callbacks.
        # print("list length : ", len(self.callback_list))
        for callback in self.callback_list:
            try:
                callback()
            except Exception:
                self.g.es_exception()
                self.g.es_print(f"removing callback: {callback}")
                self.callback_list.remove(callback)
        # Handle idle-time hooks.
        self.g.app.pluginsController.on_idle()

    def start(self):
        """Start the idle-time timer."""
        self.timer = self.g.IdleTime(
            self.on_idle,
            delay=500,  # Milliseconds
            tag='IdleTimeManager.on_idle')
        if self.timer:
            self.timer.start()


class ExternalFilesController:
    '''EFC Modified from Leo's sources'''
    # pylint: disable=no-else-return

    def __init__(self, integController):
        '''Ctor for ExternalFiles class.'''
        self.on_idle_count = 0
        self.integController = integController
        self.checksum_d = {}
        # Keys are full paths, values are file checksums.
        self.enabled_d = {}
        # For efc.on_idle.
        # Keys are commanders.
        # Values are cached @bool check-for-changed-external-file settings.
        self.has_changed_d = {}
        # Keys are commanders. Values are boolean.
        # Used only to limit traces.
        self.unchecked_commanders = []
        # Copy of g.app.commanders()
        self.unchecked_files = []
        # Copy of self file. Only one files is checked at idle time.
        self._time_d = {}
        # Keys are full paths, values are modification times.
        # DO NOT alter directly, use set_time(path) and
        # get_time(path), see set_time() for notes.
        self.yesno_all_time = 0  # previous yes/no to all answer, time of answer
        self.yesno_all_answer = None  # answer, 'yes-all', or 'no-all'

        # if yesAll/noAll forced, then just show info message after idle_check_commander
        self.infoMessage = None
        # False or "detected", "refreshed" or "ignored"

        self.integController.g.app.idleTimeManager.add_callback(self.on_idle)

        self.waitingForAnswer = False
        self.lastPNode = None  # last p node that was asked for if not set to "AllYes\AllNo"
        self.lastCommander = None

    def on_idle(self):
        '''
        Check for changed open-with files and all external files in commanders
        for which @bool check_for_changed_external_file is True.
        '''
        # Fix for flushing the terminal console to traverse
        # python through node.js when using start server in leoInteg
        sys.stdout.flush()

        if not self.integController.g.app or self.integController.g.app.killed:
            return
        if self.waitingForAnswer:
            return

        self.on_idle_count += 1

        if self.unchecked_commanders:
            # Check the next commander for which
            # @bool check_for_changed_external_file is True.
            c = self.unchecked_commanders.pop()
            self.lastCommander = c
            self.idle_check_commander(c)
        else:
            # Add all commanders for which
            # @bool check_for_changed_external_file is True.
            self.unchecked_commanders = [
                z for z in self.integController.g.app.commanders() if self.is_enabled(z)
            ]

    def idle_check_commander(self, c):
        '''
        Check all external files corresponding to @<file> nodes in c for
        changes.
        '''
        # #1100: always scan the entire file for @<file> nodes.
        # #1134: Nested @<file> nodes are no longer valid, but this will do no harm.

        self.infoMessage = None  # reset infoMessage
        # False or "detected", "refreshed" or "ignored"

        for p in c.all_unique_positions():
            if self.waitingForAnswer:
                break
            if p.isAnyAtFileNode():
                self.idle_check_at_file_node(c, p)

        # if yesAll/noAll forced, then just show info message
        if self.infoMessage:
            w_package = {"async": "info", "message": self.infoMessage}
            self.integController.sendAsyncOutput(w_package)

    def idle_check_at_file_node(self, c, p):
        '''Check the @<file> node at p for external changes.'''
        trace = False
        # Matt, set this to True, but only for the file that interests you.\
        # trace = p.h == '@file unregister-leo.leox'
        path = self.integController.g.fullPath(c, p)
        has_changed = self.has_changed(path)
        if trace:
            self.integController.g.trace('changed', has_changed, p.h)
        if has_changed:
            self.lastPNode = p  # can be set here because its the same process for ask/warn
            if p.isAtAsisFileNode() or p.isAtNoSentFileNode():
                # Fix #1081: issue a warning.
                self.warn(c, path, p=p)
            elif self.ask(c, path, p=p):
                self.lastCommander.selectPosition(self.lastPNode)
                c.refreshFromDisk()

            # Always update the path & time to prevent future warnings.
            self.set_time(path)
            self.checksum_d[path] = self.checksum(path)

    def integResult(self, p_result):
        '''Received result from client'''
        # Got the result to an asked question/warning from the client
        if not self.waitingForAnswer:
            print("ERROR: Received Result but no Asked Dialog", flush=True)
            return
        # check if p_resultwas from a warn (ok) or an ask ('yes','yes-all','no','no-all')
        # act accordingly

        path = self.integController.g.fullPath(
            self.lastCommander, self.lastPNode)

        # 1- if ok, unblock 'warn'
        # 2- if no, unblock 'ask'
        # ------------------------------------------ Nothing special to do

        # 3- if noAll, set noAll, and unblock 'ask'
        if p_result and "-all" in p_result.lower():
            self.yesno_all_time = time.time()
            self.yesno_all_answer = p_result.lower()
        # ------------------------------------------ Also covers setting yesAll in #5

        # 4- if yes, REFRESH self.lastPNode, and unblock 'ask'
        # 5- if yesAll,REFRESH self.lastPNode, set yesAll, and unblock 'ask'
        if bool(p_result and 'yes' in p_result.lower()):
            self.lastCommander.selectPosition(self.lastPNode)
            self.lastCommander.refreshFromDisk()

        # Always update the path & time to prevent future warnings for this PNode.
        self.set_time(path)
        self.checksum_d[path] = self.checksum(path)

        self.waitingForAnswer = False  # unblock
        # unblock: run the loop as if timer had hit
        self.idle_check_commander(self.lastCommander)

    def ask(self, c, path, p=None):
        '''
        Ask user whether to overwrite an @<file> tree.
        Return True if the user agrees.
        '''
        # check with leoInteg's config first
        if self.integController.leoIntegConfig:
            w_check_config = self.integController.leoIntegConfig["defaultReloadIgnore"].lower(
            )
            if not bool('none' in w_check_config):
                if bool('yes' in w_check_config):
                    self.infoMessage = "refreshed"
                    return True
                else:
                    self.infoMessage = "ignored"
                    return False
        # let original function resolve

        if self.yesno_all_time + 3 >= time.time() and self.yesno_all_answer:
            self.yesno_all_time = time.time()  # Still reloading?  Extend time.
            # if yesAll/noAll forced, then just show info message
            w_yesno_all_bool = bool('yes' in self.yesno_all_answer.lower())

            return w_yesno_all_bool
        if not p:
            where = 'the outline node'
        else:
            where = p.h

        _is_leo = path.endswith(('.leo', '.db'))

        if _is_leo:
            s = '\n'.join([
                f'{self.integController.g.splitLongFileName(path)} has changed outside Leo.',
                'Overwrite it?'
            ])
        else:
            s = '\n'.join([
                f'{self.integController.g.splitLongFileName(path)} has changed outside Leo.',
                f"Reload {where} in Leo?",
            ])

        w_package = {"async": "ask", "ask": 'Overwrite the version in Leo?',
                     "message": s, "yes_all": not _is_leo, "no_all": not _is_leo}

        self.integController.sendAsyncOutput(w_package)
        self.waitingForAnswer = True
        return False
        # result = self.integController.g.app.gui.runAskYesNoDialog(c, 'Overwrite the version in Leo?', s,
        # yes_all=not _is_leo, no_all=not _is_leo)

        # if result and "-all" in result.lower():
        # self.yesno_all_time = time.time()
        # self.yesno_all_answer = result.lower()

        # return bool(result and 'yes' in result.lower())

    def checksum(self, path):
        '''Return the checksum of the file at the given path.'''
        import hashlib
        return hashlib.md5(open(path, 'rb').read()).hexdigest()

    def get_mtime(self, path):
        '''Return the modification time for the path.'''
        return self.integController.g.os_path_getmtime(self.integController.g.os_path_realpath(path))

    def get_time(self, path):
        '''
        return timestamp for path

        see set_time() for notes
        '''
        return self._time_d.get(self.integController.g.os_path_realpath(path))

    def has_changed(self, path):
        '''Return True if p's external file has changed outside of Leo.'''
        if not path:
            return False
        if not self.integController.g.os_path_exists(path):
            return False
        if self.integController.g.os_path_isdir(path):
            return False
        #
        # First, check the modification times.
        old_time = self.get_time(path)
        new_time = self.get_mtime(path)
        if not old_time:
            # Initialize.
            self.set_time(path, new_time)
            self.checksum_d[path] = self.checksum(path)
            return False
        if old_time == new_time:
            return False
        #
        # Check the checksums *only* if the mod times don't match.
        old_sum = self.checksum_d.get(path)
        new_sum = self.checksum(path)
        if new_sum == old_sum:
            # The modtime changed, but it's contents didn't.
            # Update the time, so we don't keep checking the checksums.
            # Return False so we don't prompt the user for an update.
            self.set_time(path, new_time)
            return False
        # The file has really changed.
        assert old_time, path
        # #208: external change overwrite protection only works once.
        # If the Leo version is changed (dirtied) again,
        # overwrite will occur without warning.
        # self.set_time(path, new_time)
        # self.checksum_d[path] = new_sum
        return True

    def is_enabled(self, c):
        '''Return the cached @bool check_for_changed_external_file setting.'''
        # check with leoInteg's config first
        if self.integController.leoIntegConfig:
            w_check_config = self.integController.leoIntegConfig["checkForChangeExternalFiles"].lower(
            )
            if bool('check' in w_check_config):
                return True
            if bool('ignore' in w_check_config):
                return False
        # let original function resolve
        d = self.enabled_d
        val = d.get(c)
        if val is None:
            val = c.config.getBool(
                'check-for-changed-external-files', default=False)
            d[c] = val
        return val

    def join(self, s1, s2):
        '''Return s1 + ' ' + s2'''
        return f"{s1} {s2}"

    def set_time(self, path, new_time=None):
        '''
        Implements c.setTimeStamp.

        Update the timestamp for path.

        NOTE: file paths with symbolic links occur with and without those links
        resolved depending on the code call path.  This inconsistency is
        probably not Leo's fault but an underlying Python issue.
        Hence the need to call realpath() here.
        '''

        # print("called set_time for " + str(path), flush=True)

        t = new_time or self.get_mtime(path)
        self._time_d[self.integController.g.os_path_realpath(path)] = t

    def warn(self, c, path, p):
        '''
        Warn that an @asis or @nosent node has been changed externally.

        There is *no way* to update the tree automatically.
        '''
        # check with leoInteg's config first
        if self.integController.leoIntegConfig:
            w_check_config = self.integController.leoIntegConfig["defaultReloadIgnore"].lower(
            )

            if w_check_config != "none":
                # if not 'none' then do not warn, just infoMessage 'warn' at most
                if not self.infoMessage:
                    self.infoMessage = "warn"
                return

        # let original function resolve
        if self.integController.g.unitTesting or c not in self.integController.g.app.commanders():
            return
        if not p:
            self.integController.g.trace('NO P')
            return

        s = '\n'.join([
            '%s has changed outside Leo.\n' % self.integController.g.splitLongFileName(
                path),
            'Leo can not update this file automatically.\n',
            'This file was created from %s.\n' % p.h,
            'Warning: refresh-from-disk will destroy all children.'
        ])

        w_package = {"async": "warn",
                     "warn": 'External file changed', "message": s}

        self.integController.sendAsyncOutput(w_package)
        self.waitingForAnswer = True

    # Some methods are called in the usual (non-leoBridge without 'efc') save process.
    # Those may be called by the 'save' function, like check_overwrite,
    # or by any other functions from the instance of leo.core.leoBridge that's running.

    def open_with(self, c, d):
        return

    def check_overwrite(self, c, fn):
        # print("check_overwrite!! ", flush=True)
        return True

    def shut_down(self):
        return

    def destroy_frame(self, f):
        return


class IntegTextWrapper:
    """
    A class that represents text as a Python string.
    Modified from Leo's StringTextWrapper class source
    """

    def __init__(self, c, name, g):
        """Ctor for the IntegTextWrapper class."""
        self.c = c
        self.name = name
        self.g = g  # Should g be totally global across all leoIntegration classes?
        self.ins = 0
        self.sel = 0, 0
        self.s = ''
        self.yScroll = 0
        self.supportsHighLevelInterface = True
        self.widget = None  # This ivar must exist, and be None.

    def __repr__(self):
        return f"<IntegTextWrapper: {id(self)} {self.name}>"

    def getName(self):
        """IntegTextWrapper."""
        return self.name  # Essential.

    def clipboard_clear(self):
        self.g.app.gui.replaceClipboardWith('')

    def clipboard_append(self, s):
        s1 = self.g.app.gui.getTextFromClipboard()
        self.g.app.gui.replaceClipboardWith(s1 + s)

    def flashCharacter(self, i, bg='white', fg='red',
                       flashes=3, delay=75): pass

    def see(self, i): pass

    def seeInsertPoint(self): pass

    def setFocus(self): pass

    def setStyleClass(self, name): pass

    def tag_configure(self, colorName, **keys): pass

    def appendText(self, s):
        """IntegTextWrapper appendText"""
        self.s = self.s + self.g.toUnicode(s)
        # defensive
        self.ins = len(self.s)
        self.sel = self.ins, self.ins

    def delete(self, i, j=None):
        """IntegTextWrapper delete"""
        i = self.toPythonIndex(i)
        if j is None:
            j = i + 1
        j = self.toPythonIndex(j)
        # This allows subclasses to use this base class method.
        if i > j:
            i, j = j, i
        s = self.getAllText()
        self.setAllText(s[:i] + s[j:])
        # Bug fix: 2011/11/13: Significant in external tests.
        self.setSelectionRange(i, i, insert=i)

    def deleteTextSelection(self):
        """IntegTextWrapper."""
        i, j = self.getSelectionRange()
        self.delete(i, j)

    def get(self, i, j=None):
        """IntegTextWrapper get"""
        i = self.toPythonIndex(i)
        if j is None:
            j = i + 1
        j = self.toPythonIndex(j)
        s = self.s[i:j]
        # print("WRAPPER GET with self.s[i:j]: " + s)
        return self.g.toUnicode(s)

    def getAllText(self):
        """IntegTextWrapper getAllText"""
        s = self.s
        # print("WRAPPER getAllText  " + s)
        return self.g.checkUnicode(s)

    def getInsertPoint(self):
        """IntegTextWrapper getInsertPoint"""
        i = self.ins
        if i is None:
            if self.virtualInsertPoint is None:
                i = 0
            else:
                i = self.virtualInsertPoint
        self.virtualInsertPoint = i
        return i

    def getSelectedText(self):
        """IntegTextWrapper getSelectedText"""
        i, j = self.sel
        s = self.s[i:j]
        # print("WRAPPER getSelectedText with self.s[i:j]: " + s)
        return self.g.checkUnicode(s)

    def getSelectionRange(self, sort=True):
        """Return the selected range of the widget."""
        sel = self.sel
        if len(sel) == 2 and sel[0] >= 0 and sel[1] >= 0:
            i, j = sel
            if sort and i > j:
                sel = j, i  # Bug fix: 10/5/07
            return sel
        i = self.ins
        return i, i

    def getXScrollPosition(self):
        return 0
        # X axis ignored

    def getYScrollPosition(self):
        # print("wrapper get y scroll" + str(self.yScroll))
        return self.yScroll

    def hasSelection(self):
        """IntegTextWrapper hasSelection"""
        i, j = self.getSelectionRange()
        return i != j

    def insert(self, i, s):
        """IntegTextWrapper insert"""
        i = self.toPythonIndex(i)
        s1 = s
        self.s = self.s[:i] + s1 + self.s[i:]
        i += len(s1)
        self.ins = i
        self.sel = i, i

    def selectAllText(self, insert=None):
        """IntegTextWrapper selectAllText"""
        self.setSelectionRange(0, 'end', insert=insert)

    def setAllText(self, s):
        """IntegTextWrapper setAllText"""
        # print("WRAPPER setAllText: " + s)
        self.s = s
        i = len(self.s)
        self.ins = i
        self.sel = i, i

    def setInsertPoint(self, pos, s=None):
        """IntegTextWrapper setInsertPoint"""
        self.virtualInsertPoint = i = self.toPythonIndex(pos)
        self.ins = i
        self.sel = i, i

    def setXScrollPosition(self, i):
        pass
        # X axis ignored

    def setYScrollPosition(self, i):
        self.yScroll = i
        # print("wrapper set y scroll" + str(self.yScroll))

    def setSelectionRange(self, i, j, insert=None):
        """IntegTextWrapper setSelectionRange"""
        i, j = self.toPythonIndex(i), self.toPythonIndex(j)
        self.sel = i, j
        self.ins = j if insert is None else self.toPythonIndex(insert)

    def toPythonIndex(self, index):
        """IntegTextWrapper toPythonIndex"""
        return self.g.toPythonIndex(self.s, index)

    def toPythonIndexRowCol(self, index):
        """IntegTextWrapper toPythonIndexRowCol"""
        s = self.getAllText()
        i = self.toPythonIndex(index)
        row, col = self.g.convertPythonIndexToRowCol(s, i)
        return i, row, col


class LeoBridgeIntegController:
    '''Leo Bridge Controller'''
    # pylint: disable=no-else-return

    def __init__(self):
        # TODO : @boltex #74 need gnx_to_vnode for each opened file/commander
        self.gnx_to_vnode = []  # utility array - see leoflexx.py in leoPluginsRef.leo
        self.bridge = leoBridge.controller(
            gui='nullGui',
            loadPlugins=True,   # True: attempt to load plugins.
            readSettings=True,  # True: read standard settings files.
            silent=True,       # True: don't print signon messages.
            # True: prints what would be sent to the log pane.
            verbose=False,
        )
        self.g = self.bridge.globals()

        # * Trace outputs to pythons stdout, also prints the function call stack
        # self.g.trace('test trace')

        # * Intercept Log Pane output: Sends to client's log pane
        self.g.es = self.es  # pointer - not a function call

        # print(dir(self.g), flush=True)
        self.currentActionId = 1  # Id of action being processed, STARTS AT 1 = Initial 'ready'

        # * Currently Selected Commander (opened from leo.core.leoBridge or chosen via the g.app.windowList 2 list)
        self.commander = None

        self.leoIntegConfig = None
        self.webSocket = None
        self.loop = None

        # * Replacement instances to Leo's codebase : getScript, IdleTime, idleTimeManager and externalFilesController
        self.g.getScript = self._getScript
        self.g.IdleTime = self._idleTime
        self.g.app.idleTimeManager = IdleTimeManager(self.g)
        # attach instance to g.app for calls to set_time, etc.
        self.g.app.externalFilesController = ExternalFilesController(self)
        # TODO : Maybe use those yes/no replacement right before actual usage instead of in init. (to allow re-use/switching)
        # override for "revert to file" operation
        self.g.app.gui.runAskYesNoDialog = self._returnYes
        self.g.app.gui.show_find_success = self._show_find_success
        self.headlineWidget = self.g.bunch(_name='tree')

        self.g.app.loadManager.createAllImporterData()

        # * setup leoBackground to get messages from leo
        try:
            self.g.app.idleTimeManager.start()  # To catch derived file changes
        except Exception:
            print('ERROR with idleTimeManager')

    async def _asyncIdleLoop(self, p_seconds, p_fn):
        while True:
            await asyncio.sleep(p_seconds)
            p_fn(self)

    def _returnNo(self, *arguments, **kwargs):
        '''Used to override g.app.gui.ask[XXX] dialogs answers'''
        return "no"

    def _returnYes(self, *arguments, **kwargs):
        '''Used to override g.app.gui.ask[XXX] dialogs answers'''
        return "yes"

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
            s = self.g.removeExtraLws(s, c.tab_width)
            s = self.g.extractExecutableString(c, p, s)
            script = self.g.composeScript(c, p, s,
                                          forcePythonSentinels=forcePythonSentinels,
                                          useSentinels=useSentinels)
        except Exception:
            self.g.es_print("unexpected exception in g.getScript")
            self.g.es_exception()
            script = ''
        return script

    def _idleTime(self, fn, delay, tag):
        # TODO : REVISE/REPLACE WITH OWN SYSTEM
        asyncio.get_event_loop().create_task(self._asyncIdleLoop(delay/1000, fn))

    def _getTotalOpened(self):
        '''Get total of opened commander (who have closed == false)'''
        w_total = 0
        for w_commander in self.g.app.commanders():
            if not w_commander.closed:
                w_total = w_total + 1
        return w_total

    def _getFirstOpenedCommander(self):
        '''Get first opened commander, or False if there are none.'''
        for w_commander in self.g.app.commanders():
            if not w_commander.closed:
                return w_commander
        return False

    def _show_find_success(self, c, in_headline, insert, p):
        '''Handle a successful find match.'''
        if in_headline:
            self.g.app.gui.set_focus(c, self.headlineWidget)
        # no return

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

    def set_ask_result(self, p_result):
        '''Got the result to an asked question/warning from client'''
        self.g.app.externalFilesController.integResult(p_result)
        return self.sendLeoBridgePackage()  # Just send empty as 'ok'

    def set_config(self, p_config):
        '''Got leoInteg's config from client'''
        self.leoIntegConfig = p_config
        return self.sendLeoBridgePackage()  # Just send empty as 'ok'

    def logSignon(self):
        '''Simulate the Initial Leo Log Entry'''
        if self.loop:
            self.g.app.computeSignon()
            self.g.es(str(self.g.app.signon))
            self.g.es(str(self.g.app.signon1))
        else:
            print('no loop in logSignon', flush=True)

    def setActionId(self, p_id):
        self.currentActionId = p_id

    async def asyncOutput(self, p_json):
        '''Output json string to the websocket'''
        if self.webSocket:
            await self.webSocket.send(p_json)
        else:
            print("websocket not ready yet", flush=True)

    def sendLeoBridgePackage(self, p_package={}):
        p_package["id"] = self.currentActionId
        return(json.dumps(p_package, separators=(',', ':')))  # send as json

    def _outputError(self, p_message="Unknown Error"):
        # Output to this server's running console
        print("ERROR: " + p_message, flush=True)
        w_package = {"id": self.currentActionId}
        w_package["error"] = p_message
        return p_message

    def _outputBodyData(self, p_bodyText=""):
        return self.sendLeoBridgePackage({"body": p_bodyText})

    def _outputSelectionData(self, p_bodySelection):
        return self.sendLeoBridgePackage({"bodySelection": p_bodySelection})

    def _outputPNode(self, p_node=False):
        if p_node:
            # Single node, singular
            return self.sendLeoBridgePackage({"node": self._p_to_ap(p_node)})
        else:
            return self.sendLeoBridgePackage({"node": None})

    def _outputPNodes(self, p_pList):
        w_apList = []
        for p in p_pList:
            w_apList.append(self._p_to_ap(p))
        # Multiple nodes, plural
        return self.sendLeoBridgePackage({"children": w_apList})

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
        d = self.g.doKeywordArgs(keys, d)
        s = self.g.translateArgs(args, d)
        w_package = {"async": "log", "log": s}
        self.sendAsyncOutput(w_package)

    def initConnection(self, p_webSocket):
        self.webSocket = p_webSocket
        self.loop = asyncio.get_event_loop()

    def _get_commander_method(self, p_command):
        """ Return the given method (p_command) in the Commands class or subcommanders."""
        # self.g.trace(p_command)
        #
        # First, try the commands class.
        w_func = getattr(self.commander, p_command, None)
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
            subcommander = getattr(self.commander, ivar, None)
            if subcommander:
                w_func = getattr(subcommander, p_command, None)
                if w_func:
                    ### self.g.trace(f"Found c.{ivar}.{p_command}")
                    return w_func
            # else:
                # self.g.trace(f"Not Found: c.{ivar}") # Should never happen.
        return None

    def leoCommand(self, p_command, param):
        '''
        Generic call to a method in Leo's Commands class or any subcommander class.

        The param["ap"] position is to be selected before having the command run,
        while the param["keep"] parameter specifies wether the original position
        should be re-selected afterward.

        The whole of those operations is to be undoable as one undo step.

        command: a method name (a string).
        param["ap"]: an archived position.
        param["keep"]: preserve the current selection, if possible.
        '''
        w_keepSelection = False  # Set default, optional component of param
        if "keep" in param:
            w_keepSelection = param["keep"]

        w_ap = param["ap"]  # At least node parameter is present
        if not w_ap:
            return self._outputError(f"Error in {p_command}: no param ap")

        w_p = self._ap_to_p(w_ap)
        if not w_p:
            return self._outputError(f"Error in {p_command}: no w_p position found")

        w_func = self._get_commander_method(p_command)
        if not w_func:
            return self._outputError(f"Error in {p_command}: no method found")

        if w_p == self.commander.p:
            w_func(event=None)
        else:
            w_oldPosition = self.commander.p
            self.commander.selectPosition(w_p)
            w_func(event=None)
            if w_keepSelection and self.commander.positionExists(w_oldPosition):
                self.commander.selectPosition(w_oldPosition)

        return self._outputPNode(self.commander.p)

    def get_all_open_commanders(self, param):
        '''Return array of opened file path/names to be used as openFile parameters to switch files'''
        w_files = []
        for w_commander in self.g.app.commanders():
            if not w_commander.closed:
                w_isSelected = False
                w_isChanged = w_commander.changed
                if self.commander == w_commander:
                    w_isSelected = True
                w_entry = {
                    "name": w_commander.mFileName,
                    "changed": w_isChanged,
                    "selected": w_isSelected
                }
                w_files.append(w_entry)

        return self.sendLeoBridgePackage({"files": w_files})

    def get_ui_states(self, param):
        """
        Gets the currently opened file's general states for UI enabled/disabled states
        such as undo available, file changed/unchanged
        """
        w_states = {}
        if self.commander:
            try:
                # 'dirty/changed' member
                w_states["changed"] = self.commander.changed
                w_states["canUndo"] = self.commander.canUndo()
                w_states["canRedo"] = self.commander.canRedo()
                w_states["canDemote"] = self.commander.canDemote()
                w_states["canPromote"] = self.commander.canPromote()
                w_states["canDehoist"] = self.commander.canDehoist()

            except Exception as e:
                self.g.trace('Error while getting states')
                print("Error while getting states", flush=True)
                print(str(e), flush=True)
        else:
            w_states["changed"] = False
            w_states["canUndo"] = False
            w_states["canRedo"] = False
            w_states["canDemote"] = False
            w_states["canPromote"] = False
            w_states["canDehoist"] = False

        return self.sendLeoBridgePackage({"states": w_states})

    def set_opened_file(self, param):
        '''Choose the new active commander from array of opened file path/names by numeric index'''
        w_openedCommanders = []

        for w_commander in self.g.app.commanders():
            if not w_commander.closed:
                w_openedCommanders.append(w_commander)

        w_index = param['index']  # index in param

        if w_openedCommanders[w_index]:
            self.commander = w_openedCommanders[w_index]

        if self.commander:
            self.commander.closed = False
            self._create_gnx_to_vnode()
            w_result = {"total": self._getTotalOpened(), "filename": self.commander.fileName(),
                        "node": self._p_to_ap(self.commander.p)}
            # maybe needed for frame wrapper
            self.commander.selectPosition(self.commander.p)
            return self.sendLeoBridgePackage(w_result)
        else:
            return self._outputError('Error in setOpenedFile')

    def open_file(self, param):
        """
        Open a leo file via leoBridge controller, or create a new document if empty string.
        Returns an object that contains a 'opened' member.
        """
        w_found = False
        w_filename = param.get('filename')  # Optional.
        # If not empty string (asking for New file) then check if already opened
        if w_filename:
            for w_commander in self.g.app.commanders():
                if w_commander.fileName() == w_filename:
                    w_found = True
                    self.commander = w_commander

        if not w_found:
            self.commander = self.bridge.openLeoFile(
                w_filename)  # create self.commander
            self.commander.findCommands.ftm = StringFindTabManager(
                self.commander)

        # Leo at this point has done this too: g.app.windowList.append(c.frame)
        # and so, now, app.commanders() yields this: return [f.c for f in g.app.windowList]

        if self.commander:
            self.commander.closed = False
            if not w_found:
                # is new so also replace wrapper
                self.commander.frame.body.wrapper = IntegTextWrapper(
                    self.commander, "integBody", self.g)
                self.commander.selectPosition(self.commander.p)

            self._create_gnx_to_vnode()
            w_result = {"total": self._getTotalOpened(), "filename": self.commander.fileName(),
                        "node": self._p_to_ap(self.commander.p)}
            return self.sendLeoBridgePackage(w_result)
        else:
            return self._outputError('Error in openFile')

    def open_files(self, param):
        """
        Opens an array of leo files
        Returns an object that contains the last 'opened' member.
        """
        w_files = []
        if "files" in param:
            w_files = param["files"]

        for i_file in w_files:
            self.commander = None
            w_found = False
            # If not empty string (asking for New file) then check if already opened
            if i_file:
                for w_commander in self.g.app.commanders():
                    if w_commander.fileName() == i_file:
                        w_found = True
                        self.commander = w_commander

            if not w_found:
                if os.path.isfile(i_file):
                    self.commander = self.bridge.openLeoFile(
                        i_file)  # create self.commander
                    self.commander.findCommands.ftm = StringFindTabManager(
                        self.commander)
            if self.commander:
                self.commander.closed = False
                self.commander.frame.body.wrapper = IntegTextWrapper(
                    self.commander, "integBody", self.g)
                self.commander.selectPosition(self.commander.p)

        # Done with the last one, it's now the selected commander. Check again just in case.
        if self.commander:
            self._create_gnx_to_vnode()
            w_result = {"total": self._getTotalOpened(), "filename": self.commander.fileName(),
                        "node": self._p_to_ap(self.commander.p)}
            return self.sendLeoBridgePackage(w_result)
        else:
            return self._outputError('Error in openFiles')

    def close_file(self, param):
        """
        Closes a leo file. A file can then be opened with "openFile".
        Returns a 'total' member in the package if close is successful

        """
        if self.commander:
            # First, revert to prevent asking user.
            if param["forced"] and self.commander.changed:
                self.commander.revert()
            # Then, if still possible, close it.
            if param["forced"] or not self.commander.changed:
                self.commander.closed = True
                self.commander.close()
            else:
                # Cannot close, ask to save, ignore or cancel
                return self.sendLeoBridgePackage()

        # Switch commanders to first available
        w_total = self._getTotalOpened()
        if w_total:
            self.commander = self._getFirstOpenedCommander()
        else:
            self.commander = None

        if self.commander:
            self._create_gnx_to_vnode()
            w_result = {"total": self._getTotalOpened(), "filename": self.commander.fileName(),
                        "node": self._p_to_ap(self.commander.p)}
        else:
            w_result = {"total": 0}

        return self.sendLeoBridgePackage(w_result)

    def save_file(self, param):
        '''Saves the leo file. New or dirty derived files are rewritten'''
        if self.commander:
            try:
                if "name" in param:
                    self.commander.save(fileName=param['name'])
                else:
                    self.commander.save()
            except Exception as e:
                self.g.trace('Error while saving')
                print("Error while saving", param['name'], flush=True)
                print(str(e),  param['name'],  flush=True)

        return self.sendLeoBridgePackage()  # Just send empty as 'ok'

    def import_any_file(self, param):
        """
        Import file(s) from array of file names
        """
        c = self.commander
        g = self.g
        ic = c.importCommands
        names = param.get('filenames')
        if names:
            g.chdir(names[0])
        if not names:
            return self._outputError("Error in import_any_file no filenames found")

        # New in Leo 4.9: choose the type of import based on the extension.
        derived = [z for z in names if c.looksLikeDerivedFile(z)]
        others = [z for z in names if z not in derived]
        if derived:
            ic.importDerivedFiles(parent=c.p, paths=derived)
        for fn in others:
            junk, ext = g.os_path_splitext(fn)
            ext = ext.lower()  # #1522
            if ext.startswith('.'):
                ext = ext[1:]
            if ext == 'csv':
                ic.importMindMap([fn])
            elif ext in ('cw', 'cweb'):
                ic.importWebCommand([fn], "cweb")
            # Not useful. Use @auto x.json instead.
            # elif ext == 'json':
                # ic.importJSON([fn])
            elif fn.endswith('mm.html'):
                ic.importFreeMind([fn])
            elif ext in ('nw', 'noweb'):
                ic.importWebCommand([fn], "noweb")
            elif ext == 'more':
                # (Félix) leoImport Should be on c?
                c.leoImport.MORE_Importer(c).import_file(fn)  # #1522.
            elif ext == 'txt':
                # (Félix) import_txt_file Should be on c?
                # #1522: Create an @edit node.
                c.import_txt_file(c, fn)
            else:
                # Make *sure* that parent.b is empty.
                last = c.lastTopLevel()
                parent = last.insertAfter()
                parent.v.h = 'Imported Files'
                ic.importFilesCommand(
                    files=[fn],
                    parent=parent,
                    treeType='@auto',  # was '@clean'
                    # Experimental: attempt to use permissive section ref logic.
                )
        return self.sendLeoBridgePackage()  # Just send empty as 'ok'

    def get_search_settings(self, param):
        """
        Gets search options
        """
        w_result = self.commander.findCommands.ftm.get_settings()
        return self.sendLeoBridgePackage({"searchSettings": w_result.__dict__})

    def set_search_settings(self, param):
        """
        Sets search options. Init widgets and ivars from param.searchSettings
        """
        c = self.commander
        find = c.findCommands
        ftm = c.findCommands.ftm
        searchSettings = param['searchSettings']
        # Find/change text boxes.
        table = (
            ('find_findbox', 'find_text', ''),
            ('find_replacebox', 'change_text', ''),
        )
        for widget_ivar, setting_name, default in table:
            w = getattr(ftm, widget_ivar)
            s = searchSettings.get(setting_name) or default
            w.clear()
            w.insert(s)
        # Check boxes.
        table = (
            ('ignore_case', 'check_box_ignore_case'),
            ('mark_changes', 'check_box_mark_changes'),
            ('mark_finds', 'check_box_mark_finds'),
            ('pattern_match', 'check_box_regexp'),
            ('search_body', 'check_box_search_body'),
            ('search_headline', 'check_box_search_headline'),
            ('whole_word', 'check_box_whole_word'),
        )
        for setting_name, widget_ivar in table:
            w = getattr(ftm, widget_ivar)
            val = searchSettings.get(setting_name)
            setattr(find, setting_name, val)
            if val != w.isChecked():
                w.toggle()
        # Radio buttons
        table = (
            ('node_only', 'node_only', 'radio_button_node_only'),
            ('entire_outline', None, 'radio_button_entire_outline'),
            ('suboutline_only', 'suboutline_only', 'radio_button_suboutline_only'),
        )
        for setting_name, ivar, widget_ivar in table:
            w = getattr(ftm, widget_ivar)
            val = searchSettings.get(setting_name, False)
            if ivar is not None:
                assert hasattr(find, setting_name), setting_name
                setattr(find, setting_name, val)
                if val != w.isChecked():
                    w.toggle()
        # Ensure one radio button is set.
        w = ftm.radio_button_entire_outline
        if not searchSettings.get('node_only', False) and not searchSettings.get('suboutline_only', False):
            setattr(find, 'entire_outline', True)
            if not w.isChecked():
                w.toggle()
        else:
            setattr(find, 'entire_outline', False)
            if w.isChecked():
                w.toggle()

        # Confirm by sending back the settings to leointeg
        w_result = ftm.get_settings()
        return self.sendLeoBridgePackage({"searchSettings": w_result.__dict__})

    def find_all(self, param):
        """Run Leo's find all command and return results."""
        c = self.commander
        fc = c.findCommands
        settings = fc.ftm.get_settings()
        result = fc.do_find_all(settings)
        w = self.g.app.gui.get_focus()
        focus = self.g.app.gui.widget_name(w)
        w_result = {"found": result,
                    "focus": focus, "node": self._p_to_ap(c.p)}
        return self.sendLeoBridgePackage(w_result)

    def find_next(self, param):
        """Run Leo's find-next command and return results."""
        c = self.commander
        fc = c.findCommands
        settings = fc.ftm.get_settings()
        p, pos, newpos = fc.do_find_next(settings)
        found = True
        if not p:
            found = False
        w = self.g.app.gui.get_focus()
        focus = self.g.app.gui.widget_name(w)
        w_result = {"found": found, "pos": pos, "newpos": newpos,
                    "focus": focus, "node": self._p_to_ap(c.p)}
        return self.sendLeoBridgePackage(w_result)

    def find_previous(self, param):
        """Run Leo's find-previous command and return results."""
        c = self.commander
        fc = c.findCommands
        settings = fc.ftm.get_settings()
        p, pos, newpos = fc.do_find_prev(settings)
        found = True
        if not p:
            found = False
        w = self.g.app.gui.get_focus()
        focus = self.g.app.gui.widget_name(w)
        w_result = {"found": found, "pos": pos, "newpos": newpos,
                    "focus": focus, "node": self._p_to_ap(c.p)}
        return self.sendLeoBridgePackage(w_result)


    def replace(self, param):
        """Run Leo's replace command and return results."""
        c = self.commander
        fc = c.findCommands
        settings = fc.ftm.get_settings()
        fc.change(settings)
        w = self.g.app.gui.get_focus()
        focus = self.g.app.gui.widget_name(w)
        w_result = {"found": True,
                    "focus": focus, "node": self._p_to_ap(c.p)}
        return self.sendLeoBridgePackage(w_result)

    def replace_then_find(self, param):
        """Run Leo's replace then find next command and return results."""
        c = self.commander
        fc = c.findCommands
        settings = fc.ftm.get_settings()
        result = fc.do_change_then_find(settings)
        w = self.g.app.gui.get_focus()
        focus = self.g.app.gui.widget_name(w)
        w_result = {"found": result,
                    "focus": focus, "node": self._p_to_ap(c.p)}
        return self.sendLeoBridgePackage(w_result)

    def replace_all(self, param):
        """Run Leo's replace all command and return results."""
        c = self.commander
        fc = c.findCommands
        settings = fc.ftm.get_settings()
        result = fc.do_change_all(settings)
        w = self.g.app.gui.get_focus()
        focus = self.g.app.gui.widget_name(w)
        w_result = {"found": result,
                    "focus": focus, "node": self._p_to_ap(c.p)}
        return self.sendLeoBridgePackage(w_result)

    def clone_find_all(self, param):
        """Run Leo's clone-find-all command and return results."""
        c = self.commander
        fc = c.findCommands
        settings = fc.ftm.get_settings()
        result = fc.do_clone_find_all(settings)
        w = self.g.app.gui.get_focus()
        focus = self.g.app.gui.widget_name(w)
        w_result = {"found": result,
                    "focus": focus, "node": self._p_to_ap(c.p)}
        return self.sendLeoBridgePackage(w_result)

    def clone_find_all_flattened(self, param):
        """Run Leo's clone-find-all-flattened command and return results."""
        c = self.commander
        fc = c.findCommands
        settings = fc.ftm.get_settings()
        result = fc.do_clone_find_all_flattened(settings)
        w = self.g.app.gui.get_focus()
        focus = self.g.app.gui.widget_name(w)
        w_result = {"found": result,
                    "focus": focus, "node": self._p_to_ap(c.p)}
        return self.sendLeoBridgePackage(w_result)

    def find_var(self, param):
        """Run Leo's find-var command and return results."""
        c = self.commander
        fc = c.findCommands
        settings = fc.ftm.get_settings()
        # todo : find var implementation
        print("todo : find var implementation")
        # result = fc.do_clone_find_all_flattened(settings)
        w = self.g.app.gui.get_focus()
        focus = self.g.app.gui.widget_name(w)
        w_result = {"node": self._p_to_ap(c.p)}
        return self.sendLeoBridgePackage(w_result)

    def find_def(self, param):
        """Run Leo's find-def command and return results."""
        c = self.commander
        fc = c.findCommands
        settings = fc.ftm.get_settings()
        # todo : find def implementation
        print("todo : find def implementation")
        # result = fc.do_clone_find_all_flattened(settings)
        w = self.g.app.gui.get_focus()
        focus = self.g.app.gui.widget_name(w)
        w_result = {"node": self._p_to_ap(c.p)}
        return self.sendLeoBridgePackage(w_result)

    def goto_global_line(self, param):
        """Run Leo's goto-global-line command and return results."""
        c = self.commander
        junk_p, junk_offset, found = c.gotoCommands.find_file_line(
            n=int(param['line']))
        w_result = {"found": found, "node": self._p_to_ap(c.p)}
        return self.sendLeoBridgePackage(w_result)

    def get_buttons(self, param):
        '''Gets the currently opened file's @buttons list'''
        w_buttons = []
        if self.commander and self.commander.theScriptingController and self.commander.theScriptingController.buttonsDict:
            w_dict = self.commander.theScriptingController.buttonsDict
            for w_key in w_dict:
                w_entry = {"name": w_dict[w_key], "index": str(w_key)}
                w_buttons.append(w_entry)
        return self.sendLeoBridgePackage({"buttons": w_buttons})

    def remove_button(self, param):
        '''Removes an entry from the buttonsDict by index string'''
        w_index = param['index']
        w_dict = self.commander.theScriptingController.buttonsDict
        w_key = None
        for i_key in w_dict:
            if(str(i_key) == w_index):
                w_key = i_key
        if w_key:
            del(w_dict[w_key])  # delete object member
        # return selected node when done
        return self._outputPNode(self.commander.p)

    def click_button(self, param):
        '''Handles buttons clicked in client from the '@button' panel'''
        w_index = param['index']
        w_dict = self.commander.theScriptingController.buttonsDict
        w_button = None
        for i_key in w_dict:
            if(str(i_key) == w_index):
                w_button = i_key
        if w_button:
            w_button.command()  # run clicked button command
        # return selected node when done
        return self._outputPNode(self.commander.p)

    def get_all_leo_commands(self, param):
        """Return a list of all Leo commands that make sense in leoInteg."""
        c = self.commander
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

        return self.sendLeoBridgePackage({"commands": result})

    def _bad_commands(self):
        """Return the list of Leo's command names that leoInteg should ignore."""
        c = self.commander
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

            'clone-find-all',  # Should be overridden by leointeg
            'clone-find-all-flattened',   # Should be overridden by leointeg
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

            'redo',  # Should be overridden by leointeg
            'rst3',
            'run-all-unit-tests-externally',
            'run-all-unit-tests-locally',
            'run-marked-unit-tests-externally',
            'run-marked-unit-tests-locally',
            'run-selected-unit-tests-externally',
            'run-selected-unit-tests-locally',
            'run-tests',

            'undo',  # Should be overridden by leointeg

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

    def _getDocstringForCommand(self, command_name):
        """get docstring for the given command."""
        func = self._get_commander_method(command_name)
        docstring = func.__doc__ if func else ''
        return docstring

    def mark_node(self, param):
        '''Mark a node, don't select it'''
        w_ap = param["ap"]
        if w_ap:
            w_p = self._ap_to_p(w_ap)
            if w_p:
                w_p.setMarked()
                # return selected node when done (not w_p)
                return self._outputPNode(self.commander.p)
            else:
                return self._outputError("Error in markPNode no w_p node found")
        else:
            return self._outputError("Error in markPNode no param node")

    def unmark_node(self, param):
        '''Unmark a node, don't select it'''
        w_ap = param["ap"]
        if w_ap:
            w_p = self._ap_to_p(w_ap)
            if w_p:
                w_p.clearMarked()
                # return selected node when done (not w_p)
                return self._outputPNode(self.commander.p)
            else:
                return self._outputError("Error in unmarkPNode no w_p node found")
        else:
            return self._outputError("Error in unmarkPNode no param node")

    def clone_node(self, param):
        '''Clone a node, return it, if it was also the current selection, otherwise try not to select it'''
        w_ap = param["ap"]
        if not w_ap:
            return self._outputError("Error in clonePNode function, no param p_ap")
        w_p = self._ap_to_p(w_ap)
        if not w_p:
            # default empty
            return self._outputError("Error in clonePNode function, no w_p node found")
        if w_p == self.commander.p:
            self.commander.clone()
        else:
            oldPosition = self.commander.p
            self.commander.selectPosition(w_p)
            self.commander.clone()
            if self.commander.positionExists(oldPosition):
                self.commander.selectPosition(oldPosition)
        # return selected node either ways
        return self._outputPNode(self.commander.p)

    def cut_node(self, param):
        '''Cut a node, don't select it. Try to keep selection, then return the selected node that remains'''
        w_ap = param["ap"]
        if w_ap:
            w_p = self._ap_to_p(w_ap)
            if w_p:
                if w_p == self.commander.p:
                    self.commander.cutOutline()  # already on this node, so cut it
                else:
                    oldPosition = self.commander.p  # not same node, save position to possibly return to
                    self.commander.selectPosition(w_p)
                    self.commander.cutOutline()
                    if self.commander.positionExists(oldPosition):
                        # select if old position still valid
                        self.commander.selectPosition(oldPosition)
                    else:
                        oldPosition._childIndex = oldPosition._childIndex-1
                        # Try again with childIndex decremented
                        if self.commander.positionExists(oldPosition):
                            # additional try with lowered childIndex
                            self.commander.selectPosition(oldPosition)
                # in both cases, return selected node
                return self._outputPNode(self.commander.p)
            else:
                # default empty
                return self._outputError("Error in cutPNode no w_p node found")
        else:
            return self._outputError("Error in cutPNode no param node")

    def delete_node(self, param):
        '''Delete a node, don't select it. Try to keep selection, then return the selected node that remains'''
        w_ap = param["ap"]
        if w_ap:
            w_p = self._ap_to_p(w_ap)
            if w_p:
                if w_p == self.commander.p:
                    self.commander.deleteOutline()  # already on this node, so delete it
                else:
                    oldPosition = self.commander.p  # not same node, save position to possibly return to
                    self.commander.selectPosition(w_p)
                    self.commander.deleteOutline()
                    if self.commander.positionExists(oldPosition):
                        # select if old position still valid
                        self.commander.selectPosition(oldPosition)
                    else:
                        oldPosition._childIndex = oldPosition._childIndex-1
                        # Try again with childIndex decremented
                        if self.commander.positionExists(oldPosition):
                            # additional try with lowered childIndex
                            self.commander.selectPosition(oldPosition)
                # in both cases, return selected node
                return self._outputPNode(self.commander.p)
            else:
                # default empty
                return self._outputError("Error in deletePNode no w_p node found")
        else:
            return self._outputError("Error in deletePNode no param node")

    def insert_node(self, param):
        '''Insert a node at given node, then select it once created, and finally return it'''
        w_ap = param["ap"]
        if w_ap:
            w_p = self._ap_to_p(w_ap)
            if w_p:
                w_bunch = self.commander.undoer.beforeInsertNode(w_p)
                w_newNode = w_p.insertAfter()
                w_newNode.setDirty()
                self.commander.undoer.afterInsertNode(
                    w_newNode, 'Insert Node', w_bunch)
                self.commander.selectPosition(w_newNode)
                # in both cases, return selected node
                return self._outputPNode(self.commander.p)
            else:
                # default empty
                return self._outputError("Error in insertPNode no w_p node found")
        else:
            return self._outputError("Error in insertPNode no param node")

    def insert_named_node(self, param):
        '''Insert a node at given node, set its headline, select it and finally return it'''
        w_newHeadline = param['name']
        w_ap = param["ap"]
        if w_ap:
            w_p = self._ap_to_p(w_ap)
            if w_p:
                w_bunch = self.commander.undoer.beforeInsertNode(w_p)
                w_newNode = w_p.insertAfter()
                # set this node's new headline
                w_newNode.h = w_newHeadline
                w_newNode.setDirty()
                self.commander.undoer.afterInsertNode(
                    w_newNode, 'Insert Node', w_bunch)
                self.commander.selectPosition(w_newNode)
                # in any case, return selected node
                return self._outputPNode(self.commander.p)
            else:
                # default empty
                return self._outputError("Error in insertNamedPNode no w_p node found")
        else:
            return self._outputError("Error in insertNamedPNode no param node")

    def undo(self, param):
        '''Undo last un-doable operation'''
        if self.commander.undoer.canUndo():
            self.commander.undoer.undo()
        # return selected node when done
        return self._outputPNode(self.commander.p)

    def redo(self, param):
        '''Undo last un-doable operation'''
        if self.commander.undoer.canRedo():
            self.commander.undoer.redo()
        # return selected node when done
        return self._outputPNode(self.commander.p)

    def test(self, param):
        '''Utility test function for debugging'''
        print("Called test")
        return self.sendLeoBridgePackage({'testReturnedKey': 'testReturnedValue'})
        # return self._outputPNode(self.commander.p)

    def page_up(self, param):
        """Selects a node a couple of steps up in the tree to simulate page up"""
        n = param.get("n", 3)
        for z in range(n):
            self.commander.selectVisBack()
        return self._outputPNode(self.commander.p)

    def page_down(self, param):
        """Selects a node a couple of steps down in the tree to simulate page down"""
        n = param.get("n", 3)
        for z in range(n):
            self.commander.selectVisNext()
        return self._outputPNode(self.commander.p)

    def get_body_states(self, p_ap):
        """
        Finds the language in effect at top of body for position p,
        return type is lowercase 'language' non-empty string.
        Also returns the saved cursor position from last time node was accessed.

        The cursor positions are given as {"line": line, "col": col, "index": i}
        with line and col along with a redundant index for convenience and flexibility.
        """
        if not p_ap:
            return self._outputError("Error in getLanguage, no param p_ap")

        w_p = self._ap_to_p(p_ap)
        if not w_p:
            print(
                "in GBS -> P NOT FOUND gnx:" + p_ap['gnx'] + " using self.commander.p gnx: " + self.commander.p.v.gnx)
            w_p = self.commander.p

        w_wrapper = self.commander.frame.body.wrapper

        defaultPosition = {"line": 0, "col": 0, "index": 0}
        states = {
            'language': 'plain',
            # See BodySelectionInfo interface in types.d.ts
            'selection': {
                "gnx": w_p.v.gnx,
                "scroll": 0,
                # "scroll": {
                #     "start": defaultPosition,
                #     "end": defaultPosition
                # },
                "insert": defaultPosition,
                "start": defaultPosition,
                "end": defaultPosition
            }
        }

        if w_p:
            c, g = self.commander, self.g
            aList = g.get_directives_dict_list(w_p)
            d = g.scanAtCommentAndAtLanguageDirectives(aList)

            language = (
                d and d.get('language') or
                g.getLanguageFromAncestorAtFileNode(w_p) or
                c.config.getString('target-language') or
                'plain'
            )

            if w_p.v.scrollBarSpot is None:
                w_scroll = 0
            else:
                w_scroll = w_p.v.scrollBarSpot

            if w_p.v.insertSpot is None:
                w_active = 0
            else:
                w_active = w_p.v.insertSpot
            if w_p.v.selectionStart is None:
                w_start = 0
            else:
                w_start = w_p.v.selectionStart

            if w_p.v.selectionLength is None:
                w_length = 0
            else:
                w_length = w_p.v.selectionLength

            w_end = w_start + w_length

            # get selection from wrapper instead if its the selected node
            if self.commander.p.v.gnx == w_p.v.gnx:
                # print("in GBS -> SAME AS self.commander.p SO USING FROM WRAPPER")
                w_active = w_wrapper.getInsertPoint()
                w_start, w_end = w_wrapper.getSelectionRange(True)
                w_scroll = w_wrapper.getYScrollPosition()

                w_activeI, w_activeRow, w_activeCol = c.frame.body.wrapper.toPythonIndexRowCol(
                    w_active)
                w_startI, w_startRow, w_startCol = c.frame.body.wrapper.toPythonIndexRowCol(
                    w_start)
                w_endI, w_endRow, w_endCol = c.frame.body.wrapper.toPythonIndexRowCol(
                    w_end)
            else:
                print("NOT SAME AS self.commander.p SO USING FROM w_p.v")
                w_activeI, w_startI, w_endI = w_active, w_start, w_end
                w_activeRow, w_activeCol = g.convertPythonIndexToRowCol(
                    w_p.v.b, w_active)
                w_startRow, w_startCol = g.convertPythonIndexToRowCol(
                    w_p.v.b, w_start)
                w_endRow, w_endCol = g.convertPythonIndexToRowCol(
                    w_p.v.b, w_end)

            states = {
                'language': language.lower(),
                'selection': {
                    "gnx": w_p.v.gnx,
                    "scroll": w_scroll,  # w_scroll was kept as-is ?
                    "insert": {"line": w_activeRow, "col": w_activeCol, "index": w_activeI},
                    "start": {"line": w_startRow, "col": w_startCol, "index": w_startI},
                    "end": {"line": w_endRow, "col": w_endCol, "index": w_endI}
                }
            }
        return self.sendLeoBridgePackage(states)

    def get_children(self, p_ap):
        '''EMIT OUT list of children of a node'''
        if p_ap:
            w_p = self._ap_to_p(p_ap)
            if w_p and w_p.hasChildren():
                return self._outputPNodes(w_p.children())
            else:
                return self._outputPNodes([])  # default empty array
        else:
            if self.commander.hoistStack:
                return self._outputPNodes([self.commander.hoistStack[-1].p])
            else:
                # this outputs all Root Children
                return self._outputPNodes(self._yieldAllRootChildren())

    def _yieldAllRootChildren(self):
        '''Return all root children P nodes'''
        p = self.commander.rootPosition()
        while p:
            yield p
            p.moveToNext()

    def get_parent(self, p_ap):
        '''EMIT OUT the parent of a node, as an array, even if unique or empty'''
        if p_ap:
            w_p = self._ap_to_p(p_ap)
            if w_p and w_p.hasParent():
                return self._outputPNode(w_p.getParent())  # if not root
        return self._outputPNode()  # default empty for root as default

    def get_all_gnx(self, param):
        '''Get gnx array from all unique nodes'''
        w_all_gnx = [
            p.v.gnx for p in self.commander.all_unique_positions(copy=False)]
        return self.sendLeoBridgePackage({"gnx": w_all_gnx})

    def get_body(self, p_gnx):
        '''EMIT OUT body of a node'''
        # TODO : if not found, send code to prevent unresolved promise if 'document switch' occurred shortly before
        if p_gnx:
            w_v = self.commander.fileCommands.gnxDict.get(p_gnx)  # vitalije
            if w_v:
                if w_v.b:
                    return self._outputBodyData(w_v.b)
                else:
                    return self._outputBodyData()  # default "" empty string
        # Send as empty to fix unresolved promise if 'document switch' occurred shortly before
        return self._outputBodyData()

    def get_body_length(self, p_gnx):
        '''EMIT OUT body string length of a node'''
        if p_gnx:
            w_v = self.commander.fileCommands.gnxDict.get(p_gnx)  # vitalije
            if w_v and w_v.b:
                # Length in bytes, not just by character count.
                return self.sendLeoBridgePackage({"len": len(w_v.b.encode('utf-8'))})
        # TODO : May need to signal inexistent by self.sendLeoBridgePackage()
        return self.sendLeoBridgePackage({"len": 0})  # empty as default

    def set_body(self, param):
        '''Change Body text of a v node'''
        w_gnx = param['gnx']
        w_body = param['body']
        for w_p in self.commander.all_positions():
            if w_p.v.gnx == w_gnx:
                # TODO : Before setting undo and trying to set body, first check if different than existing body
                w_bunch = self.commander.undoer.beforeChangeNodeContents(
                    w_p)  # setup undoable operation
                w_p.v.setBodyString(w_body)
                self.commander.undoer.afterChangeNodeContents(
                    w_p, "Body Text", w_bunch)
                if self.commander.p.v.gnx == w_gnx:
                    self.commander.frame.body.wrapper.setAllText(w_body)
                if not self.commander.isChanged():
                    self.commander.setChanged()
                if not w_p.v.isDirty():
                    w_p.setDirty()
                break
        # additional forced string setting
        if w_gnx:
            w_v = self.commander.fileCommands.gnxDict.get(w_gnx)  # vitalije
            if w_v:
                w_v.b = w_body
        return self._outputPNode(self.commander.p)  # return selected node

    def get_focus(self, param):
        """
        Return a representation of the focused widget,
        one of ("body", "tree", "headline", repr(the_widget)).
        """
        w = self.g.app.gui.get_focus()
        focus = self.g.app.gui.widget_name(w)
        return self.sendLeoBridgePackage({"focus": focus})

    def set_selection(self, param):
        '''
        Set cursor position and scroll position along with selection start and end.

        Positions can be sent as {"col":int, "line" int} dict
        or as numbers directly for convenience.

        (For the currently selected node's body, if gnx matches only)
        Save those values on the commander's body "wrapper"
        See BodySelectionInfo interface in types.d.ts
        '''
        w_same = False  # Flag for actually setting values in the wrapper, if same gnx.
        w_wrapper = self.commander.frame.body.wrapper
        w_gnx = param['gnx']
        w_body = ""
        w_v = None
        if self.commander.p.v.gnx == w_gnx:
            # print('Set Selection! OK SAME GNX: ' + self.commander.p.v.gnx)
            w_same = True
            w_v = self.commander.p.v
        else:
            # ? When navigating rapidly - Check if this is a bug - how to improve
            print('Set Selection! NOT SAME GNX: selected:' +
                  self.commander.p.v.gnx + ', package:' + w_gnx)
            w_v = self.commander.fileCommands.gnxDict.get(w_gnx)

        if not w_v:
            print('ERROR : Set Selection! NOT SAME Leo Document')
            # ! FAILED (but return as normal)
            return self._outputPNode(self.commander.p)

        w_body = w_v.b
        f_convert = self.g.convertRowColToPythonIndex
        w_active = param['insert']
        w_start = param['start']
        w_end = param['end']

        # no convertion necessary, its given back later
        w_scroll = param['scroll']

        # IF sent as number use as is - no conversion needed
        if type(w_active) == int:
            w_insert = w_active
            w_startSel = w_start
            w_endSel = w_end
        else:
            w_insert = f_convert(
                w_body, w_active['line'], w_active['col'])
            w_startSel = f_convert(
                w_body, w_start['line'], w_start['col'])
            w_endSel = f_convert(
                w_body, w_end['line'], w_end['col'])

        # print("setSelection (same as selected): " + str(w_same) + " w_insert " + str(w_insert) +
        #       " w_startSel " + str(w_startSel) + " w_endSel " + str(w_endSel))

        # If it's the currently selected node set the wrapper's states too

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
        return self._outputPNode(self.commander.p)

    def set_headline(self, param):
        '''Change Headline of a node'''
        w_newHeadline = param['name']
        w_ap = param["ap"]
        if w_ap:
            w_p = self._ap_to_p(w_ap)
            if w_p:
                # set this node's new headline
                w_bunch = self.commander.undoer.beforeChangeNodeContents(w_p)
                w_p.h = w_newHeadline
                self.commander.undoer.afterChangeNodeContents(
                    w_p, 'Change Headline', w_bunch)
                return self._outputPNode(w_p)
        return self._outputError("Error in setNewHeadline")

    def set_current_position(self, p_ap):
        '''Select a node, or the first one found with its GNX'''
        if p_ap:
            w_p = self._ap_to_p(p_ap)
            if w_p:
                if self.commander.positionExists(w_p):
                    # set this node as selection
                    self.commander.selectPosition(w_p)
                else:
                    w_foundPNode = self._findPNodeFromGnx(p_ap['gnx'])
                    if w_foundPNode:
                        self.commander.selectPosition(w_foundPNode)
                    else:
                        print("Set Selection node does not exist! ap was:" +
                              json.dumps(p_ap), flush=True)
        # * return the finally selected node
        if self.commander.p:
            return self._outputPNode(self.commander.p)
        else:
            return self._outputPNode()

    def _findPNodeFromGnx(self, p_gnx):
        '''Return first p node with this gnx or false'''
        for p in self.commander.all_unique_positions():
            if p.v.gnx == p_gnx:
                return p
        return False

    def expand_node(self, p_ap):
        '''Expand a node'''
        if p_ap:
            w_p = self._ap_to_p(p_ap)
            if w_p:
                w_p.expand()
        return self.sendLeoBridgePackage()  # Just send empty as 'ok'

    def contract_node(self, p_ap):
        '''Collapse a node'''
        if p_ap:
            w_p = self._ap_to_p(p_ap)
            if w_p:
                w_p.contract()
        return self.sendLeoBridgePackage()  # Just send empty as 'ok'

    def _create_gnx_to_vnode(self):
        '''Make the first gnx_to_vnode array with all unique nodes'''
        t1 = time.process_time()
        self.gnx_to_vnode = {
            v.gnx: v for v in self.commander.all_unique_nodes()}
        # This is likely the only data that ever will be needed.
        if 0:
            print('app.create_all_data: %5.3f sec. %s entries' % (
                (time.process_time()-t1), len(list(self.gnx_to_vnode.keys()))), flush=True)
        self._test_round_trip_positions()

    def _test_round_trip_positions(self):
        '''(From Leo plugin leoflexx.py) Test the round tripping of p_to_ap and ap_to_p.'''
        # Bug fix: p_to_ap updates app.gnx_to_vnode. Save and restore it.
        old_d = self.gnx_to_vnode.copy()
        old_len = len(list(self.gnx_to_vnode.keys()))
        # t1 = time.process_time()
        qtyAllPositions = 0
        for p in self.commander.all_positions():
            qtyAllPositions += 1
            ap = self._p_to_ap(p)
            p2 = self._ap_to_p(ap)
            assert p == p2, (repr(p), repr(p2), repr(ap))
        gnx_to_vnode = old_d
        new_len = len(list(gnx_to_vnode.keys()))
        assert old_len == new_len, (old_len, new_len)
        # print('Leo file opened. Its outline contains ' + str(qtyAllPositions) + " nodes positions.", flush=True)
        # print(('Testing app.test_round_trip_positions for all nodes: Total time: %5.3f sec.' % (time.process_time()-t1)), flush=True)

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
        if p == self.commander.p:
            w_ap['selected'] = True
        return w_ap


def printAction(param):
    # print action if not getChild or getChildren
    w_action = param["action"]
    if w_action in commonActions:
        pass
    else:
        print(f"*ACTION* {w_action}, id {param['id']}", flush=True)


def main():
    '''python script for leo integration via leoBridge'''
    global wsHost, wsPort
    print("Starting LeoBridge IN LEOINTEG... (Launch with -h for help)", flush=True)
    # replace default host address and port if provided as arguments

    args = None
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ha:p:", [
                                   "help", "address=", "port="])
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

    # * start Server
    integController = LeoBridgeIntegController()

    # * This is a basic example loop
    # async def asyncInterval(timeout):
    #     dummyCounter = 0
    #     strTimeout = str(timeout) + ' sec interval'
    #     while True:
    #         await asyncio.sleep(timeout)
    #         dummyCounter = dummyCounter+1
    #         await integController.asyncOutput("{\"interval\":" + str(timeout+dummyCounter) + "}")  # as number
    #         print(strTimeout)

    async def leoBridgeServer(websocket, path):
        try:
            integController.initConnection(websocket)
            # * Start by sending empty as 'ok'.
            await websocket.send(integController.sendLeoBridgePackage())
            integController.logSignon()
            async for json_string_message in websocket:
                messageObject = json.loads(json_string_message)
                if messageObject and messageObject['action']:
                    action = messageObject['action']
                    param = messageObject['param']
                    # printAction(w_param)  # Debug output
                    # * Storing id of action in global var instead of passing as parameter.
                    integController.setActionId(messageObject['id'])
                    # ! functions called this way need to accept at least a parameter other than 'self'
                    # ! See : getSelectedNode and getAllGnx
                    # TODO : Block attempts to call functions starting with underscore or reserved.
                    if action[0] == "!":
                        w_func = getattr(integController, action[1:], None)
                        if not w_func:
                            print(action)
                        w_answer = w_func(param)
                    else:
                        # Attempt to execute the command directly on the commander/subcommander.
                        w_answer = integController.leoCommand(
                            action, param)
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

    localLoop = asyncio.get_event_loop()
    start_server = websockets.serve(leoBridgeServer, wsHost, wsPort)
    # localLoop.create_task(asyncInterval(5)) # Starts a test loop of async communication.
    localLoop.run_until_complete(start_server)
    # This SERVER_STARTED_TOKEN special string signals server startup success.
    print(SERVER_STARTED_TOKEN + " at " + wsHost + " on port: " +
          str(wsPort) + " [ctrl+c] to break", flush=True)
    localLoop.run_forever()
    print("Stopping leobridge server", flush=True)


if __name__ == '__main__':
    # Startup
    try:
        main()
    except KeyboardInterrupt:
        print("\nKeyboard Interupt: Stopping leobridge server", flush=True)
        sys.exit()

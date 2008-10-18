# -*- coding: utf-8 -*-
#@+leo-ver=4-thin
#@+node:ekr.20031218072017.2810:@thin leoCommands.py
#@@first
    # Needed because of unicode characters in tests.

#@@language python
#@@tabwidth -4
#@@pagewidth 80

#@<< imports >>
#@+node:ekr.20040712045933:<< imports  >> (leoCommands)
import leo.core.leoGlobals as g

if g.app and g.app.use_psyco:
    # g.pr("enabled psyco classes",__file__)
    try: from psyco.classes import *
    except ImportError: pass

# These imports are now done in the ctor and c.finishCreate.
    # import leo.core.leoAtFile as leoAtFile
    # import leo.core.leoEditCommands as leoEditCommands
    # import leo.core.leoFileCommands as leoFileCommands
    # import leo.core.leoImport as leoImport
    # import leo.core.leoTangle as leoTangle
    # import leo.core.leoUndo as leoUndo

import leo.core.leoNodes as leoNodes

import keyword
import os
# import string
import sys
import tempfile
import time
import tokenize # for Check Python command

try:
    import tabnanny # for Check Python command # Does not exist in jython
except ImportError:
    tabnanny = None

if g.isPython3:
    pass # compiler module does not exist
else:
    try:
        # IronPython has troubles with these.
        import compiler # for Check Python command
    except Exception:
        pass

try:
    # IronPython has troubles with this.
    import parser # needed only for weird Python 2.2 parser errors.
except Exception:
    pass

subprocess = g.importExtension('subprocess',None,verbose=False)

# The following import _is_ used.
import token    # for Check Python command
#@-node:ekr.20040712045933:<< imports  >> (leoCommands)
#@nl

#@+others
#@+node:ekr.20041118104831:class commands
class baseCommands:
    """The base class for Leo's main commander."""
    #@    @+others
    #@+node:ekr.20031218072017.2811: c.Birth & death
    #@+node:ekr.20031218072017.2812:c.__init__
    def __init__(self,frame,fileName,relativeFileName=None):

        c = self

        self.requestedFocusWidget = None
        self.requestRedrawFlag = False
        self.requestRedrawScrollFlag = False
        self.requestedIconify = '' # 'iconify','deiconify'
        self.requestRecolorFlag = False

        # g.trace('Commands')
        self.exists = True # Indicate that this class exists and has not been destroyed.
            # Do this early in the startup process so we can call hooks.

        # Init ivars with self.x instead of c.x to keep Pychecker happy
        self.chapterController = None
        self.frame = frame

        self.hiddenRootNode = leoNodes.vnode(context=c)
        self.hiddenRootNode.setHeadString('<hidden root vnode>')
        self.hiddenRootNode.t.vnodeList = [self.hiddenRootNode]
        self.isZipped = False # May be set to True by g.openWithFileName.
        self.mFileName = fileName
            # Do _not_ use os_path_norm: it converts an empty path to '.' (!!)
        self.mRelativeFileName = relativeFileName

        # g.trace(c) # Do this after setting c.mFileName.
        c.initIvars()
        self.nodeHistory = nodeHistory(c)

        self.contractVisitedNodes = c.config.getBool('contractVisitedNodes')
        self.showMinibuffer = c.config.getBool('useMinibuffer')
        self.stayInTree = c.config.getBool('stayInTreeAfterSelect')
        self.fixed = c.config.getBool('fixedWindow',False)
            # New in Leo 4.5: True: Don't write window position, expansion states, marks, etc.
        self.fixedWindowPosition = c.config.getData('fixedWindowPosition')
        if self.fixedWindowPosition:
            try:
                w,h,l,t = self.fixedWindowPosition
                self.fixedWindowPosition = int(w),int(h),int(l),int(t)
            except Exception:
                g.es_print('bad @data fixedWindowPosition',repr(self.fixedWindowPosition),color='red')
        else:
            self.windowPosition = 500,700,50,50 # width,height,left,top.

        # initialize the sub-commanders.
        # c.finishCreate creates the sub-commanders for edit commands.

        # Break circular import dependencies by importing here.
        import leo.core.leoAtFile as leoAtFile
        import leo.core.leoEditCommands as leoEditCommands
        import leo.core.leoFileCommands as leoFileCommands
        import leo.core.leoImport as leoImport
        import leo.core.leoShadow as leoShadow
        import leo.core.leoTangle as leoTangle
        import leo.core.leoUndo as leoUndo

        self.shadowController = leoShadow.shadowController(c)
        self.fileCommands   = leoFileCommands.fileCommands(c)
        self.atFileCommands = leoAtFile.atFile(c)
        self.importCommands = leoImport.leoImportCommands(c)
        self.tangleCommands = leoTangle.tangleCommands(c)
        leoEditCommands.createEditCommanders(c)

        if 0:
            g.pr("\n*** using Null undoer ***\n")
            self.undoer = leoUndo.nullUndoer(self)
        else:
            self.undoer = leoUndo.undoer(self)
    #@-node:ekr.20031218072017.2812:c.__init__
    #@+node:ekr.20040731071037:c.initIvars
    def initIvars(self):

        c = self
        #@    << initialize ivars >>
        #@+node:ekr.20031218072017.2813:<< initialize ivars >> (commands)
        self._currentPosition = self.nullPosition()
        self._rootPosition    = self.nullPosition()
        self._topPosition     = self.nullPosition()

        # Delayed focus.
        self.doubleClickFlag = False
        self.hasFocusWidget = None
        self.requestedFocusWidget = None

        # Official ivars.
        self.gui = g.app.gui
        self.ipythonController = None # Set only by the ipython plugin.

        # Interlock to prevent setting c.changed when switching chapters.
        c.suppressHeadChanged = False

        # Interlocks to prevent premature closing of a window.
        self.inCommand = False
        self.requestCloseWindow = False

        # For emacs/vim key handling.
        self.commandsDict = None
        self.keyHandler = self.k = None
        self.miniBufferWidget = None

        # per-document info...
        self.disableCommandsMessage = ''
            # The presence of this message disables all commands.
        self.hookFunction = None
        self.openDirectory = None

        self.expansionLevel = 0  # The expansion level of this outline.
        self.expansionNode = None # The last node we expanded or contracted.
        self.changed = False # True if any data has been changed since the last save.
        self.loading = False # True if we are loading a file: disables c.setChanged()
        self.outlineToNowebDefaultFileName = "noweb.nw" # For Outline To Noweb dialog.
        self.promptingForClose = False # To lock out additional closing dialogs.

        # For tangle/untangle
        self.tangle_errors = 0

        # Global options
        self.page_width = 132
        self.tab_width = -4
        self.tangle_batch_flag = False
        self.untangle_batch_flag = False

        # Default Tangle options
        self.tangle_directory = ""
        self.use_header_flag = False
        self.output_doc_flag = False

        # Default Target Language
        self.target_language = "python" # Required if leoConfig.txt does not exist.

        # For hoist/dehoist commands.
        self.hoistStack = []
            # Stack of nodes to be root of drawn tree.
            # Affects drawing routines and find commands.
        self.recentFiles = [] # List of recent files

        # For outline navigation.
        self.navPrefix = '' # Must always be a string.
        self.navTime = None
        #@-node:ekr.20031218072017.2813:<< initialize ivars >> (commands)
        #@nl
        self.config = configSettings(c)
        g.app.config.setIvarsFromSettings(c)
    #@-node:ekr.20040731071037:c.initIvars
    #@+node:ekr.20081005065934.1:c.initAfterLoad
    def initAfterLoad (self):

        '''Provide an offical hook for late inits of the commander.'''

        pass
    #@nonl
    #@-node:ekr.20081005065934.1:c.initAfterLoad
    #@+node:ekr.20031218072017.2814:c.__repr__ & __str__
    def __repr__ (self):

        return "Commander %d: %s" % (id(self),repr(self.mFileName))

    __str__ = __repr__
    #@-node:ekr.20031218072017.2814:c.__repr__ & __str__
    #@+node:ekr.20041130173135:c.hash
    def hash (self):

        c = self
        if c.mFileName:
            return c.os_path_finalize(c.mFileName).lower()
        else:
            return 0
    #@-node:ekr.20041130173135:c.hash
    #@+node:ekr.20050920093543:c.finishCreate & helper
    def finishCreate (self,initEditCommanders=True):  # New in 4.4.

        '''Finish creating the commander after frame.finishCreate.

        Important: this is the last step in the startup process.'''

        c = self ; p = c.currentPosition()
        c.miniBufferWidget = c.frame.miniBufferWidget
        # g.trace('Commands',c.fileName())

        # Create a keyHandler even if there is no miniBuffer.
        c.keyHandler = c.k = k = g.app.gui.createKeyHandlerClass(c,
            useGlobalKillbuffer=True,
            useGlobalRegisters=True)

        if initEditCommanders:
            # A 'real' .leo file.
            import leo.core.leoEditCommands as leoEditCommands
            c.commandsDict = leoEditCommands.finishCreateEditCommanders(c)
            k.finishCreate()
        else:
            # A leoSettings.leo file.
            c.commandsDict = {}

        c.frame.log.finishCreate()
        c.bodyWantsFocusNow()
    #@+node:ekr.20051007143620:printCommandsDict
    def printCommandsDict (self):

        c = self

        g.pr('Commands...')

        for key in sorted(c.commandsDict):
            command = c.commandsDict.get(key)
            g.pr('%30s = %s' % (key,g.choose(command,command.__name__,'<None>')))
        g.pr('')
    #@-node:ekr.20051007143620:printCommandsDict
    #@-node:ekr.20050920093543:c.finishCreate & helper
    #@-node:ekr.20031218072017.2811: c.Birth & death
    #@+node:ekr.20031218072017.2817: doCommand
    command_count = 0

    def doCommand (self,command,label,event=None):

        """Execute the given command, invoking hooks and catching exceptions.

        The code assumes that the "command1" hook has completely handled the command if
        g.doHook("command1") returns False.
        This provides a simple mechanism for overriding commands."""

        c = self ; p = c.currentPosition()
        commandName = command and command.__name__
        c.setLog()

        self.command_count += 1
        if not g.app.unitTesting and c.config.getBool('trace_doCommand'):
            g.trace(commandName)

        # The presence of this message disables all commands.
        if c.disableCommandsMessage:
            g.es(c.disableCommandsMessage,color='blue')
            return 'break' # Inhibit all other handlers.

        if c.exists and c.inCommand and not g.unitTesting:
            # g.trace('inCommand',c)
            g.es('ignoring command: already executing a command.',color='red')
            return 'break'

        if label and event is None: # Do this only for legacy commands.
            if label == "cantredo": label = "redo"
            if label == "cantundo": label = "undo"
            g.app.commandName = label

        if not g.doHook("command1",c=c,p=p,v=p,label=label):
            try:
                c.inCommand = True
                val = command(event)
                if c and c.exists: # Be careful: the command could destroy c.
                    c.inCommand = False
                    c.k.funcReturn = val
                # else: g.pr('c no longer exists',c)
            except:
                c.inCommand = False
                if g.app.unitTesting:
                    raise
                else:
                    g.es_print("exception executing command")
                    g.es_exception(c=c)
                    if c and c.exists and hasattr(c,'frame'):
                        c.redraw_now()

            if c and c.exists:
                if c.requestCloseWindow:
                    g.trace('Closing window after command')
                    c.requestCloseWindow = False
                    g.app.closeLeoWindow(c.frame)
                else:
                    c.outerUpdate()

        # Be careful: the command could destroy c.
        if c and c.exists:
            p = c.currentPosition()
            g.doHook("command2",c=c,p=p,v=p,label=label)

        return "break" # Inhibit all other handlers.
    #@-node:ekr.20031218072017.2817: doCommand
    #@+node:ekr.20031218072017.2582: version & signon stuff
    #@+node:ekr.20040629121554:getBuildNumber
    def getBuildNumber(self):
        c = self
        return c.ver[10:-1] # Strip off "(dollar)Revision" and the trailing "$"
    #@-node:ekr.20040629121554:getBuildNumber
    #@+node:ekr.20040629121554.1:getSignOnLine (Contains hard-coded version info)
    def getSignOnLine (self):
        c = self
        return "Leo 4.5.1 final, build %s, September 14, 2008" % c.getBuildNumber()
    #@-node:ekr.20040629121554.1:getSignOnLine (Contains hard-coded version info)
    #@+node:ekr.20040629121554.2:initVersion
    def initVersion (self):
        c = self
        c.ver = "$Revision: 1.244 $" # CVS updates this.
    #@-node:ekr.20040629121554.2:initVersion
    #@+node:ekr.20040629121554.3:c.signOnWithVersion
    def signOnWithVersion (self):

        c = self
        color = c.config.getColor("log_error_color")
        signon = c.getSignOnLine()
        n1,n2,n3,junk,junk=sys.version_info

        if sys.platform.startswith('win'):
            version = 'Windows '
            try:
                v = os.sys.getwindowsversion()
                version += ', '.join([str(z) for z in v])
            except Exception:
                pass

        else: version = sys.platform

        if not g.unitTesting:
            g.es("Leo Log Window...",color=color)
            g.es(signon)
            g.es('',"python %s.%s.%s, %s\n%s" % (n1,n2,n3,g.app.gui.getFullVersion(c),version))
            g.enl()
            if c.fixed:
                g.es_print('This is a fixed window',color='red')
    #@-node:ekr.20040629121554.3:c.signOnWithVersion
    #@-node:ekr.20031218072017.2582: version & signon stuff
    #@+node:ekr.20040312090934:c.iterators
    #@+node:EKR.20040529091232:c.all_positions_iter == allNodes_iter
    def allNodes_iter (self,copy=False):

        r = self.rootPosition()
        if copy:
            cp = lambda p: p.copy()
        else:
            cp = lambda p: p
        return r.iter_class(r, cp)

    all_positions_iter = allNodes_iter
    #@nonl
    #@-node:EKR.20040529091232:c.all_positions_iter == allNodes_iter
    #@+node:EKR.20040529091232.1:c.all_tnodes_iter
    def all_tnodes_iter (self):

        return self.rootPosition().tnodes_iter()
    #@-node:EKR.20040529091232.1:c.all_tnodes_iter
    #@+node:EKR.20040529091232.2:c.all_unique_tnodes_iter
    def all_unique_tnodes_iter (self):

        return self.rootPosition().unique_tnodes_iter()
    #@-node:EKR.20040529091232.2:c.all_unique_tnodes_iter
    #@+node:EKR.20040529091232.3:c.all_vnodes_iter
    def all_vnodes_iter (self):
        return self.rootPosition().vnodes_iter()
    #@-node:EKR.20040529091232.3:c.all_vnodes_iter
    #@+node:EKR.20040529091232.4:c.all_unique_vnodes_iter
    def all_unique_vnodes_iter (self):

        return self.rootPosition().unique_vnodes_iter()
    #@-node:EKR.20040529091232.4:c.all_unique_vnodes_iter
    #@+node:sps.20080317144948.3:c.all_positions_with_unique_tnodes_iter
    def all_positions_with_unique_tnodes_iter (self):

        r = self.rootPosition()
        return r.unique_iter_class(r, lambda p: p)
    #@-node:sps.20080317144948.3:c.all_positions_with_unique_tnodes_iter
    #@+node:sps.20080327174748.4:c.all_positions_with_unique_vnodes_iter
    def all_positions_with_unique_vnodes_iter (self):

        r = self.rootPosition()
        return r.unique_iter_class(r, lambda p: p, lambda u: u.v)
    #@-node:sps.20080327174748.4:c.all_positions_with_unique_vnodes_iter
    #@-node:ekr.20040312090934:c.iterators
    #@+node:ekr.20051106040126:c.executeMinibufferCommand
    def executeMinibufferCommand (self,commandName):

        c = self ; k = c.k

        func = c.commandsDict.get(commandName)

        if func:
            event = g.Bunch(c=c,char='',keysym=None,widget=c.frame.body.bodyCtrl)
            stroke = None
            k.masterCommand(event,func,stroke)
            return k.funcReturn
        else:
            g.trace('no such command: %s' % (commandName),color='red')
            return None
    #@-node:ekr.20051106040126:c.executeMinibufferCommand
    #@+node:bobjack.20080509080123.2:c.universalCallback
    def universalCallback(self, function):

        """Create a universal command callback.

        Create and return a callback that wraps a function with an rClick
        signature in a callback which adapts standard minibufer command
        callbacks to a compatible format.

        This also serves to allow rClick callback functions to handle
        minibuffer commands from sources other than rClick menus so allowing
        a single function to handle calls from all sources.

        A function wrapped in this wrapper can handle rclick generator
        and invocation commands and commands typed in the minibuffer.

        It will also be able to handle commands from the minibuffer even
        if rclick is not installed.
        """
        def minibufferCallback(event, function=function):

            # Avoid a pylint complaint.
            if hasattr(self,'theContextMenuController'):
                cm = getattr(self,'theContextMenuController')
                keywords = cm.mb_keywords
            else:
                cm = keywords = None

            if not keywords:
                # If rClick is not loaded or no keywords dict was provided
                #  then the command must have been issued in a minibuffer
                #  context.
                keywords = {'c': self, 'rc_phase': 'minibuffer'}

            keywords['mb_event'] = event     

            retval = None
            try:
                retval = function(keywords)
            finally:
                if cm:
                    # Even if there is an error:
                    #   clear mb_keywords prior to next command and
                    #   ensure mb_retval from last command is wiped
                    cm.mb_keywords = None
                    cm.mb_retval = retval

        return minibufferCallback

    #fix bobjacks spelling error
    universallCallback = universalCallback
    #@-node:bobjack.20080509080123.2:c.universalCallback
    #@+node:ekr.20031218072017.2818:Command handlers...
    #@+node:ekr.20031218072017.2819:File Menu
    #@+node:ekr.20031218072017.2820:top level (file menu)
    #@+node:ekr.20031218072017.1623:c.new
    def new (self,event=None,gui=None):

        '''Create a new Leo window.'''

        c,frame = g.app.newLeoCommanderAndFrame(fileName=None,relativeFileName=None,gui=gui)

        # Needed for plugins.
        g.doHook("new",old_c=self,c=c,new_c=c)
        # Use the config params to set the size and location of the window.
        frame.setInitialWindowGeometry()
        frame.deiconify()
        frame.lift()
        frame.resizePanesToRatio(frame.ratio,frame.secondary_ratio) # Resize the _new_ frame.
        v = leoNodes.vnode(context=c)
        p = leoNodes.position(v)
        v.initHeadString("NewHeadline")
        # New in Leo 4.5: p.moveToRoot would be wrong: the node hasn't been linked yet.
        p._linkAsRoot(oldRoot=None)
        c.setRootVnode(v) # New in Leo 4.4.2.
        c.editPosition(p)
        # New in Leo 4.4.8: create the menu as late as possible so it can use user commands.
        p = c.currentPosition()
        if not g.doHook("menu1",c=c,p=p,v=p):
            frame.menu.createMenuBar(frame)
            c.updateRecentFiles(fileName=None)
            g.doHook("menu2",c=frame.c,p=p,v=p)
            g.doHook("after-create-leo-frame",c=c)

        # chapterController.finishCreate must be called after the first real redraw
        # because it requires a valid value for c.rootPosition().
        if c.config.getBool('use_chapters') and c.chapterController:
            c.chapterController.finishCreate()
            frame.c.setChanged(False) # Clear the changed flag set when creating the @chapters node.
        if c.config.getBool('outline_pane_has_initial_focus'):
            c.treeWantsFocusNow()
        else:
            c.bodyWantsFocusNow()
        # Force a call to c.outerUpdate.
        # This is needed when we execute this command from a menu.
        c.redraw_now()

        return c # For unit test.
    #@nonl
    #@-node:ekr.20031218072017.1623:c.new
    #@+node:ekr.20031218072017.2821:c.open
    def open (self,event=None):

        '''Open a Leo window containing the contents of a .leo file.'''

        c = self
        #@    << Set closeFlag if the only open window is empty >>
        #@+node:ekr.20031218072017.2822:<< Set closeFlag if the only open window is empty >>
        #@+at 
        #@nonl
        # If this is the only open window was opened when the app started, and 
        # the window has never been written to or saved, then we will 
        # automatically close that window if this open command completes 
        # successfully.
        #@-at
        #@@c

        closeFlag = (
            c.frame.startupWindow and # The window was open on startup
            not c.changed and not c.frame.saved and # The window has never been changed
            g.app.numberOfWindows == 1) # Only one untitled window has ever been opened
        #@-node:ekr.20031218072017.2822:<< Set closeFlag if the only open window is empty >>
        #@nl

        fileName = ''.join(c.k.givenArgs) or g.app.gui.runOpenFileDialog(
            title = "Open",
            filetypes = [("Leo files","*.leo"), ("All files","*")],
            defaultextension = ".leo")
        c.bringToFront()

        ok = False
        if fileName:
            ok, frame = g.openWithFileName(fileName,c)
            if ok:
                g.chdir(fileName)
                g.setGlobalOpenDir(fileName)
            if ok and closeFlag:
                g.app.destroyWindow(c.frame)

        # openWithFileName sets focus if ok.
        if not ok:
            if c.config.getBool('outline_pane_has_initial_focus'):
                c.treeWantsFocusNow()
            else:
                c.bodyWantsFocusNow()
    #@-node:ekr.20031218072017.2821:c.open
    #@+node:ekr.20031218072017.2823:openWith and allies
    def openWith(self,event=None,data=None):

        """This routine handles the items in the Open With... menu.

        These items can only be created by createOpenWithMenuFromTable().
        Typically this would be done from the "open2" hook.

        New in 4.3: The "os.spawnv" now works. You may specify arguments to spawnv
        using a list, e.g.:

        openWith("os.spawnv", ["c:/prog.exe","--parm1","frog","--switch2"], None)
        """

        c = self ; p = c.currentPosition()
        n = data and len(data) or 0
        if n != 3:
            g.trace('bad data, length must be 3, got %d' % n)
            return
        try:
            openType,arg,ext=data
            if not g.doHook("openwith1",c=c,p=p,v=p.v,openType=openType,arg=arg,ext=ext):
                g.enableIdleTimeHook(idleTimeDelay=100)
                #@            << set ext based on the present language >>
                #@+node:ekr.20031218072017.2824:<< set ext based on the present language >>
                if not ext:
                    theDict = c.scanAllDirectives()
                    language = theDict.get("language")
                    ext = g.app.language_extension_dict.get(language)
                    # g.pr(language,ext)
                    if ext == None:
                        ext = "txt"

                if ext[0] != ".":
                    ext = "."+ext

                # g.pr("ext",ext)
                #@-node:ekr.20031218072017.2824:<< set ext based on the present language >>
                #@nl
                #@            << create or reopen temp file, testing for conflicting changes >>
                #@+node:ekr.20031218072017.2825:<< create or reopen temp file, testing for conflicting changes >>
                theDict = None ; path = None
                #@<< set dict and path if a temp file already refers to p.v.t >>
                #@+node:ekr.20031218072017.2826:<<set dict and path if a temp file already refers to p.v.t >>
                searchPath = c.openWithTempFilePath(p,ext)

                if g.os_path_exists(searchPath):
                    for theDict in g.app.openWithFiles:
                        if p.v == theDict.get('v') and searchPath == theDict.get("path"):
                            path = searchPath
                            break
                #@-node:ekr.20031218072017.2826:<<set dict and path if a temp file already refers to p.v.t >>
                #@nl
                if path:
                    #@    << create or recreate temp file as needed >>
                    #@+node:ekr.20031218072017.2827:<< create or recreate temp file as needed >>
                    #@+at 
                    #@nonl
                    # We test for changes in both p and the temp file:
                    # 
                    # - If only p's body text has changed, we recreate the 
                    # temp file.
                    # - If only the temp file has changed, do nothing here.
                    # - If both have changed we must prompt the user to see 
                    # which code to use.
                    #@-at
                    #@@c

                    encoding = theDict.get("encoding")
                    old_body = theDict.get("body")
                    new_body = p.bodyString()
                    new_body = g.toEncodedString(new_body,encoding,reportErrors=True)

                    old_time = theDict.get("time")
                    try:
                        new_time = g.os_path_getmtime(path)
                    except:
                        new_time = None

                    body_changed = old_body != new_body
                    temp_changed = old_time != new_time

                    if body_changed and temp_changed:
                        #@    << Raise dialog about conflict and set result >>
                        #@+node:ekr.20031218072017.2828:<< Raise dialog about conflict and set result >>
                        message = (
                            "Conflicting changes in outline and temp file\n\n" +
                            "Do you want to use the code in the outline or the temp file?\n\n")

                        result = g.app.gui.runAskYesNoCancelDialog(c,
                            "Conflict!", message,
                            yesMessage = "Outline",
                            noMessage = "File",
                            defaultButton = "Cancel")
                        #@-node:ekr.20031218072017.2828:<< Raise dialog about conflict and set result >>
                        #@nl
                        if result == "cancel": return
                        rewrite = result == "outline"
                    else:
                        rewrite = body_changed

                    if rewrite:
                        path = c.createOpenWithTempFile(p,ext)
                    else:
                        g.es("reopening:",g.shortFileName(path),color="blue")
                    #@-node:ekr.20031218072017.2827:<< create or recreate temp file as needed >>
                    #@nl
                else:
                    path = c.createOpenWithTempFile(p,ext)

                if not path:
                    return # An error has occured.
                #@-node:ekr.20031218072017.2825:<< create or reopen temp file, testing for conflicting changes >>
                #@nl
                #@            << execute a command to open path in external editor >>
                #@+node:ekr.20031218072017.2829:<< execute a command to open path in external editor >>
                try:
                    if arg == None: arg = ""
                    shortPath = path # g.shortFileName(path)
                    if openType == "os.system":
                        if 1:
                            # This works, _provided_ that arg does not contain blanks.  Sheesh.
                            command = 'os.system(%s)' % (arg+shortPath)
                            os.system(arg+shortPath)
                        else:
                            # XP does not like this format!
                            command = 'os.system("%s" "%s")' % (arg,shortPath)
                            os.system('"%s" "%s"' % (arg,shortPath))
                    elif openType == "os.startfile":
                        command = "os.startfile(%s)" % (arg+shortPath)
                        os.startfile(arg+path)
                    elif openType == "exec":
                        command = "exec(%s)" % (arg+shortPath)
                        exec(arg+path,{},{})
                    elif openType == "os.spawnl":
                        filename = g.os_path_basename(arg)
                        command = "os.spawnl(%s,%s,%s)" % (arg,filename,path)
                        os.spawnl(os.P_NOWAIT,arg,filename,path)
                    elif openType == "os.spawnv":
                        filename = os.path.basename(arg[0]) 
                        vtuple = arg[1:]
                        vtuple.insert(0, filename)
                            # add the name of the program as the first argument.
                            # Change suggested by Jim Sizelove.
                        vtuple.append(path)
                        command = "os.spawnv(%s,%s)" % (arg[0],repr(vtuple))
                        os.spawnv(os.P_NOWAIT,arg[0],vtuple)
                    # This clause by Jim Sizelove.
                    elif openType == "subprocess.Popen":
                        if isinstance(arg, basestring):
                            vtuple = arg + " " + path
                        elif isinstance(arg, (list, tuple)):
                            vtuple = arg[:]
                            vtuple.append(path)
                        command = "subprocess.Popen(%s)" % repr(vtuple)
                        if subprocess:
                            subprocess.Popen(vtuple)
                        else:
                            g.trace('Can not import subprocess.  Skipping: "%s"' % command)
                    else:
                        command="bad command:"+str(openType)
                        g.trace(command)
                except Exception:
                    g.es("exception executing:",command)
                    g.es_exception()
                #@-node:ekr.20031218072017.2829:<< execute a command to open path in external editor >>
                #@nl
            g.doHook("openwith2",c=c,p=p,v=p.v,openType=openType,arg=arg,ext=ext)
        except Exception:
            g.es("unexpected exception in c.openWith")
            g.es_exception()

        return "break"
    #@+node:ekr.20031218072017.2830:createOpenWithTempFile
    def createOpenWithTempFile (self,p,ext):

        c = self
        theFile = None # pylint complains if this is inited to ''.
        path = c.openWithTempFilePath(p,ext)
        try:
            if g.os_path_exists(path):
                g.es("recreating:  ",g.shortFileName(path),color="red")
            else:
                g.es("creating:  ",g.shortFileName(path),color="blue")
            theFile = open(path,"w")
            # Convert s to whatever encoding is in effect.
            s = p.bodyString()
            theDict = c.scanAllDirectives(p)
            encoding = theDict.get("encoding",None)
            if encoding == None:
                encoding = c.config.default_derived_file_encoding
            s = g.toEncodedString(s,encoding,reportErrors=True) 
            theFile.write(s)
            theFile.flush()
            theFile.close()
            try:    time = g.os_path_getmtime(path)
            except: time = None
            # g.es("time: " + str(time))
            # New in 4.3: theDict now contains both 'p' and 'v' entries, of the expected type.
            theDict = {
                "body":s, "c":c, "encoding":encoding,
                "f":theFile, "path":path, "time":time,
                "p":p, "v":p.v }
            #@        << remove previous entry from app.openWithFiles if it exists >>
            #@+node:ekr.20031218072017.2831:<< remove previous entry from app.openWithFiles if it exists >>
            for d in g.app.openWithFiles[:]:
                p2 = d.get("p")
                if p.v.t == p2.v.t:
                    # g.pr("removing previous entry in g.app.openWithFiles for",p.headString())
                    g.app.openWithFiles.remove(d)
            #@-node:ekr.20031218072017.2831:<< remove previous entry from app.openWithFiles if it exists >>
            #@nl
            g.app.openWithFiles.append(theDict)
            return path
        except:
            if theFile:
                theFile.close()
            theFile = None
            g.es("exception creating temp file",color="red")
            g.es_exception()
            return None
    #@-node:ekr.20031218072017.2830:createOpenWithTempFile
    #@+node:ekr.20031218072017.2832:c.openWithTempFilePath
    def openWithTempFilePath (self,p,ext):

        """Return the path to the temp file corresponding to p and ext."""

        name = "LeoTemp_%s_%s%s" % (
            str(id(p.v.t)),
            g.sanitize_filename(p.headString()),
            ext)

        name = g.toUnicode(name,g.app.tkEncoding)

        td = g.os_path_finalize(tempfile.gettempdir())

        path = g.os_path_join(td,name)

        return path
    #@-node:ekr.20031218072017.2832:c.openWithTempFilePath
    #@-node:ekr.20031218072017.2823:openWith and allies
    #@+node:ekr.20031218072017.2833:close
    def close (self,event=None):

        '''Close the Leo window, prompting to save it if it has been changed.'''

        g.app.closeLeoWindow(self.frame)
    #@-node:ekr.20031218072017.2833:close
    #@+node:ekr.20031218072017.2834:save (commands)
    def save (self,event=None):

        '''Save a Leo outline to a file.'''

        c = self ; w = g.app.gui.get_focus(c)

        if g.app.disableSave:
            g.es("save commands disabled",color="purple")
            return

        # Make sure we never pass None to the ctor.
        if not c.mFileName:
            c.frame.title = ""
            c.mFileName = ""

        if c.mFileName:
            # Calls c.setChanged(False) if no error.
            c.fileCommands.save(c.mFileName)
        else:
            fileName = ''.join(c.k.givenArgs) or g.app.gui.runSaveFileDialog(
                initialfile = c.mFileName,
                title="Save",
                filetypes=[("Leo files", "*.leo")],
                defaultextension=".leo")
            c.bringToFront()

            if fileName:
                # Don't change mFileName until the dialog has suceeded.
                c.mFileName = g.ensure_extension(fileName, ".leo")
                c.frame.title = c.mFileName
                c.frame.setTitle(g.computeWindowTitle(c.mFileName))
                c.frame.openDirectory = g.os_path_dirname(c.mFileName) # Bug fix in 4.4b2.
                c.fileCommands.save(c.mFileName)
                c.updateRecentFiles(c.mFileName)
                g.chdir(c.mFileName)

        c.redraw()
        c.widgetWantsFocusNow(w)
    #@-node:ekr.20031218072017.2834:save (commands)
    #@+node:ekr.20031218072017.2835:saveAs
    def saveAs (self,event=None):

        '''Save a Leo outline to a file with a new filename.'''

        c = self ;  w = g.app.gui.get_focus(c)

        if g.app.disableSave:
            g.es("save commands disabled",color="purple")
            return

        # Make sure we never pass None to the ctor.
        if not c.mFileName:
            c.frame.title = ""

        fileName = ''.join(c.k.givenArgs) or g.app.gui.runSaveFileDialog(
            initialfile = c.mFileName,
            title="Save As",
            filetypes=[("Leo files", "*.leo")],
            defaultextension=".leo")
        c.bringToFront()

        if fileName:
            g.trace(fileName)
            # 7/2/02: don't change mFileName until the dialog has suceeded.
            c.mFileName = g.ensure_extension(fileName, ".leo")
            c.frame.title = c.mFileName
            c.frame.setTitle(g.computeWindowTitle(c.mFileName))
            c.frame.openDirectory = g.os_path_dirname(c.mFileName) # Bug fix in 4.4b2.
            # Calls c.setChanged(False) if no error.
            c.fileCommands.saveAs(c.mFileName)
            c.updateRecentFiles(c.mFileName)
            g.chdir(c.mFileName)
        c.redraw()
        c.widgetWantsFocusNow(w)
    #@-node:ekr.20031218072017.2835:saveAs
    #@+node:ekr.20070413045221:saveAsUnzipped & saveAsZipped
    def saveAsUnzipped (self,event=None):

        '''Save a Leo outline to a file with a new filename,
        ensuring that the file is not compressed.'''
        self.saveAsZippedHelper(False)

    def saveAsZipped (self,event=None):

        '''Save a Leo outline to a file with a new filename,
        ensuring that the file is compressed.'''
        self.saveAsZippedHelper(True)

    def saveAsZippedHelper (self,isZipped):

        c = self
        oldZipped = c.isZipped
        c.isZipped = isZipped
        try:
            c.saveAs()
        finally:
            c.isZipped = oldZipped
    #@-node:ekr.20070413045221:saveAsUnzipped & saveAsZipped
    #@+node:ekr.20031218072017.2836:saveTo
    def saveTo (self,event=None):

        '''Save a Leo outline to a file, leaving the file associated with the Leo outline unchanged.'''

        c = self ; w = g.app.gui.get_focus(c)

        if g.app.disableSave:
            g.es("save commands disabled",color="purple")
            return

        # Make sure we never pass None to the ctor.
        if not c.mFileName:
            c.frame.title = ""

        # set local fileName, _not_ c.mFileName
        fileName = ''.join(c.k.givenArgs) or g.app.gui.runSaveFileDialog(
            initialfile = c.mFileName,
            title="Save To",
            filetypes=[("Leo files", "*.leo")],
            defaultextension=".leo")
        c.bringToFront()

        if fileName:
            fileName = g.ensure_extension(fileName, ".leo")
            c.fileCommands.saveTo(fileName)
            c.updateRecentFiles(fileName)
            g.chdir(fileName)
        c.redraw()
        c.widgetWantsFocusNow(w)
    #@-node:ekr.20031218072017.2836:saveTo
    #@+node:ekr.20031218072017.2837:revert
    def revert (self,event=None):

        '''Revert the contents of a Leo outline to last saved contents.'''

        c = self

        # Make sure the user wants to Revert.
        if not c.mFileName:
            return

        reply = g.app.gui.runAskYesNoDialog(c,"Revert",
            "Revert to previous version of " + c.mFileName + "?")
        c.bringToFront()

        if reply=="no":
            return

        # Kludge: rename this frame so openWithFileName won't think it is open.
        fileName = c.mFileName ; c.mFileName = ""

        # Create a new frame before deleting this frame.
        ok, frame = g.openWithFileName(fileName,c)
        if ok:
            frame.deiconify()
            g.app.destroyWindow(c.frame)
        else:
            c.mFileName = fileName
    #@-node:ekr.20031218072017.2837:revert
    #@-node:ekr.20031218072017.2820:top level (file menu)
    #@+node:ekr.20031218072017.2079:Recent Files submenu & allies
    #@+node:ekr.20031218072017.2080:clearRecentFiles
    def clearRecentFiles (self,event=None):

        """Clear the recent files list, then add the present file."""

        c = self ; f = c.frame ; u = c.undoer

        bunch = u.beforeClearRecentFiles()

        recentFilesMenu = f.menu.getMenu("Recent Files...")
        f.menu.deleteRecentFilesMenuItems(recentFilesMenu)

        c.recentFiles = []
        g.app.config.recentFiles = [] # New in Leo 4.3.
        f.menu.createRecentFilesMenuItems()
        c.updateRecentFiles(c.relativeFileName())

        g.app.config.appendToRecentFiles(c.recentFiles)

        # g.trace(c.recentFiles)

        u.afterClearRecentFiles(bunch)

        # New in Leo 4.4.5: write the file immediately.
        g.app.config.recentFileMessageWritten = False # Force the write message.
        g.app.config.writeRecentFilesFile(c)
    #@-node:ekr.20031218072017.2080:clearRecentFiles
    #@+node:ekr.20031218072017.2081:openRecentFile
    def openRecentFile(self,name=None):

        if not name: return

        c = self ; v = c.currentVnode()
        #@    << Set closeFlag if the only open window is empty >>
        #@+node:ekr.20031218072017.2082:<< Set closeFlag if the only open window is empty >>
        #@+at 
        #@nonl
        # If this is the only open window was opened when the app started, and 
        # the window has never been written to or saved, then we will 
        # automatically close that window if this open command completes 
        # successfully.
        #@-at
        #@@c

        closeFlag = (
            c.frame.startupWindow and # The window was open on startup
            not c.changed and not c.frame.saved and # The window has never been changed
            g.app.numberOfWindows == 1) # Only one untitled window has ever been opened
        #@-node:ekr.20031218072017.2082:<< Set closeFlag if the only open window is empty >>
        #@nl

        fileName = name
        if not g.doHook("recentfiles1",c=c,p=v,v=v,fileName=fileName,closeFlag=closeFlag):
            ok, frame = g.openWithFileName(fileName,c)
            if ok and closeFlag and frame != c.frame:
                g.app.destroyWindow(c.frame) # 12/12/03
                c = frame.c # Switch to the new commander so the "recentfiles2" hook doesn't crash.
                c.setLog() # Sets the log stream for g.es

        g.doHook("recentfiles2",c=c,p=v,v=v,fileName=fileName,closeFlag=closeFlag)
    #@-node:ekr.20031218072017.2081:openRecentFile
    #@+node:ekr.20031218072017.2083:c.updateRecentFiles
    def updateRecentFiles (self,fileName):

        """Create the RecentFiles menu.  May be called with Null fileName."""

        c = self

        if g.app.unitTesting: return

        def munge(name):
            return c.os_path_finalize(name or '').lower()
        def munge2(name):
            return c.os_path_finalize_join(g.app.loadDir,name or '')

        # Update the recent files list in all windows.
        if fileName:
            compareFileName = munge(fileName)
            # g.trace(fileName)
            for frame in g.app.windowList:
                c = frame.c
                # Remove all versions of the file name.
                for name in c.recentFiles:
                    if munge(fileName) == munge(name) or munge2(fileName) == munge2(name):
                        c.recentFiles.remove(name)
                c.recentFiles.insert(0,fileName)
                # g.trace('adding',fileName)
                # Recreate the Recent Files menu.
                frame.menu.createRecentFilesMenuItems()
        else:
            for frame in g.app.windowList:
                frame.menu.createRecentFilesMenuItems()
    #@-node:ekr.20031218072017.2083:c.updateRecentFiles
    #@+node:tbrown.20080509212202.6:cleanRecentFiles
    def cleanRecentFiles(self,event=None):

        c = self

        dat = c.config.getData('path-demangle')
        if not dat:
            g.es('No @data path-demangle setting')
            return

        changes = []
        replace = None
        for line in dat:
            text = line.strip()
            if text.startswith('REPLACE: '):
                replace = text.split(None, 1)[1].strip()
            if text.startswith('WITH:') and replace is not None:
                with_ = text[5:].strip()
                changes.append((replace, with_))
                g.es('%s -> %s' % changes[-1])

        orig = [i for i in c.recentFiles if i.startswith("/")]
        c.clearRecentFiles()

        for i in orig:
            t = i
            for change in changes:
                t = t.replace(*change)

            c.updateRecentFiles(t)

        # code below copied from clearRecentFiles
        g.app.config.recentFiles = [] # New in Leo 4.3.
        g.app.config.appendToRecentFiles(c.recentFiles)
        g.app.config.recentFileMessageWritten = False # Force the write message.
        g.app.config.writeRecentFilesFile(c)
    #@-node:tbrown.20080509212202.6:cleanRecentFiles
    #@+node:tbrown.20080509212202.8:sortRecentFiles
    def sortRecentFiles(self,event=None):

        c = self

        orig = c.recentFiles[:]
        c.clearRecentFiles()
        import os
        orig.sort(cmp=lambda a,b:cmp(os.path.basename(b).lower(),     
            os.path.basename(a).lower()))
        for i in orig:
            c.updateRecentFiles(i)

        # code below copied from clearRecentFiles
        g.app.config.recentFiles = [] # New in Leo 4.3.
        g.app.config.appendToRecentFiles(c.recentFiles)
        g.app.config.recentFileMessageWritten = False # Force the write message.
        g.app.config.writeRecentFilesFile(c)
    #@-node:tbrown.20080509212202.8:sortRecentFiles
    #@-node:ekr.20031218072017.2079:Recent Files submenu & allies
    #@+node:ekr.20031218072017.2838:Read/Write submenu
    #@+node:ekr.20031218072017.2839:readOutlineOnly
    def readOutlineOnly (self,event=None):

        '''Open a Leo outline from a .leo file, but do not read any derived files.'''

        fileName = g.app.gui.runOpenFileDialog(
            title="Read Outline Only",
            filetypes=[("Leo files", "*.leo"), ("All files", "*")],
            defaultextension=".leo")

        if not fileName:
            return

        try:
            theFile = open(fileName,'r')
            g.chdir(fileName)
            c,frame = g.app.newLeoCommanderAndFrame(fileName=fileName)
            frame.deiconify()
            frame.lift()
            g.app.root.update() # Force a screen redraw immediately.
            c.fileCommands.readOutlineOnly(theFile,fileName) # closes file.
        except:
            g.es("can not open:",fileName)
    #@-node:ekr.20031218072017.2839:readOutlineOnly
    #@+node:ekr.20070915134101:readFileIntoNode
    def readFileIntoNode (self,event=None):

        '''Read a file into a single node.'''

        c = self ; undoType = 'Read File Into Node'
        filetypes = [("All files", "*"),("Python files","*.py"),("Leo files", "*.leo"),]
        fileName = g.app.gui.runOpenFileDialog(
            title="Read File Into Node",filetypes=filetypes,defaultextension=None)

        if fileName:    
            try:
                theFile = open(fileName,'r')
                g.chdir(fileName)
                s = theFile.read()
                s = '@nocolor\n' + s
                w = c.frame.body.bodyCtrl
                p = c.insertHeadline(op_name=undoType)
                p.setHeadString('@read-file-into-node ' + fileName)
                p.setBodyString(s)
                w.setAllText(s)
                c.redraw()
            except:
                g.es("can not open:",fileName)
    #@-node:ekr.20070915134101:readFileIntoNode
    #@+node:ekr.20070806105721.1:readAtAutoNodes (commands)
    def readAtAutoNodes (self,event=None):

        '''Read all @auto nodes in the presently selected outline.'''

        c = self ; u = c.undoer ; p = c.currentPosition()

        undoData = u.beforeChangeTree(p)
        c.importCommands.readAtAutoNodes()
        u.afterChangeTree(p,'Read @auto Nodes',undoData)
        c.redraw()
    #@-node:ekr.20070806105721.1:readAtAutoNodes (commands)
    #@+node:ekr.20031218072017.1839:readAtFileNodes (commands)
    def readAtFileNodes (self,event=None):

        '''Read all @file nodes in the presently selected outline.'''

        c = self ; u = c.undoer ; p = c.currentPosition()

        undoData = u.beforeChangeTree(p)
        c.fileCommands.readAtFileNodes()
        u.afterChangeTree(p,'Read @file Nodes',undoData)
        c.redraw()
    #@-node:ekr.20031218072017.1839:readAtFileNodes (commands)
    #@+node:ekr.20080801071227.4:readAtShadowNodes (commands)
    def readAtShadowNodes (self,event=None):

        '''Read all @shadow nodes in the presently selected outline.'''

        c = self ; u = c.undoer ; p = c.currentPosition()

        undoData = u.beforeChangeTree(p)
        c.atFileCommands.readAtShadowNodes(p)
        u.afterChangeTree(p,'Read @shadow Nodes',undoData)
        c.redraw() 
    #@-node:ekr.20080801071227.4:readAtShadowNodes (commands)
    #@+node:ekr.20031218072017.1809:importDerivedFile
    def importDerivedFile (self,event=None):

        """Create a new outline from a 4.0 derived file."""

        c = self ; p = c.currentPosition()

        types = [
            ("All files","*"),
            ("C/C++ files","*.c"),
            ("C/C++ files","*.cpp"),
            ("C/C++ files","*.h"),
            ("C/C++ files","*.hpp"),
            ("Java files","*.java"),
            ("Lua files", "*.lua"),
            ("Pascal files","*.pas"),
            ("Python files","*.py") ]

        names = g.app.gui.runOpenFileDialog(
            title="Import Derived File",
            filetypes=types,
            defaultextension=".py",
            multiple=True)

        if names:
            g.chdir(names[0])
            c.importCommands.importDerivedFiles(parent=p,paths=names)
    #@-node:ekr.20031218072017.1809:importDerivedFile
    #@+node:ekr.20070915142635:writeFileFromNode
    def writeFileFromNode (self,event=None):

        # If node starts with @read-file-into-node, use the full path name in the headline.
        # Otherwise, prompt for a file name.

        c = self ; p = c.currentPosition()
        h = p.headString().rstrip()
        s = p.bodyString()
        tag = '@read-file-into-node'

        if h.startswith(tag):
            fileName = h[len(tag):].strip()
        else:
            fileName = None

        if not fileName:
            filetypes = [("All files", "*"),("Python files","*.py"),("Leo files", "*.leo"),]
            fileName = g.app.gui.runSaveFileDialog(
                initialfile=None,
                title='Write File From Node',
                filetypes=filetypes,
                defaultextension=None)
        if fileName:
            try:
                theFile = open(fileName,'w')
                g.chdir(fileName)
            except IOError:
                theFile = None
            if theFile:
                if s.startswith('@nocolor\n'):
                    s = s[len('@nocolor\n'):]
                theFile.write(s)
                theFile.flush()
                g.es_print('wrote:',fileName,color='blue')
                theFile.close()
            else:
                g.es('can not write %s',fileName,color='red')
    #@nonl
    #@-node:ekr.20070915142635:writeFileFromNode
    #@-node:ekr.20031218072017.2838:Read/Write submenu
    #@+node:ekr.20031218072017.2841:Tangle submenu
    #@+node:ekr.20031218072017.2842:tangleAll
    def tangleAll (self,event=None):

        '''Tangle all @root nodes in the entire outline.'''

        c = self
        c.tangleCommands.tangleAll()
    #@-node:ekr.20031218072017.2842:tangleAll
    #@+node:ekr.20031218072017.2843:tangleMarked
    def tangleMarked (self,event=None):

        '''Tangle all marked @root nodes in the entire outline.'''

        c = self
        c.tangleCommands.tangleMarked()
    #@-node:ekr.20031218072017.2843:tangleMarked
    #@+node:ekr.20031218072017.2844:tangle
    def tangle (self,event=None):

        '''Tangle all @root nodes in the selected outline.'''

        c = self
        c.tangleCommands.tangle()
    #@-node:ekr.20031218072017.2844:tangle
    #@-node:ekr.20031218072017.2841:Tangle submenu
    #@+node:ekr.20031218072017.2845:Untangle submenu
    #@+node:ekr.20031218072017.2846:untangleAll
    def untangleAll (self,event=None):

        '''Untangle all @root nodes in the entire outline.'''

        c = self
        c.tangleCommands.untangleAll()
        c.undoer.clearUndoState()
    #@-node:ekr.20031218072017.2846:untangleAll
    #@+node:ekr.20031218072017.2847:untangleMarked
    def untangleMarked (self,event=None):

        '''Untangle all marked @root nodes in the entire outline.'''

        c = self
        c.tangleCommands.untangleMarked()
        c.undoer.clearUndoState()
    #@-node:ekr.20031218072017.2847:untangleMarked
    #@+node:ekr.20031218072017.2848:untangle
    def untangle (self,event=None):

        '''Untangle all @root nodes in the selected outline.'''

        c = self
        c.tangleCommands.untangle()
        c.undoer.clearUndoState()
    #@-node:ekr.20031218072017.2848:untangle
    #@-node:ekr.20031218072017.2845:Untangle submenu
    #@+node:ekr.20031218072017.2849:Import&Export submenu
    #@+node:ekr.20031218072017.2850:exportHeadlines
    def exportHeadlines (self,event=None):

        '''Export all headlines to an external file.'''

        c = self

        filetypes = [("Text files", "*.txt"),("All files", "*")]

        fileName = g.app.gui.runSaveFileDialog(
            initialfile="headlines.txt",
            title="Export Headlines",
            filetypes=filetypes,
            defaultextension=".txt")
        c.bringToFront()

        if fileName and len(fileName) > 0:
            g.setGlobalOpenDir(fileName)
            g.chdir(fileName)
            c.importCommands.exportHeadlines(fileName)
    #@-node:ekr.20031218072017.2850:exportHeadlines
    #@+node:ekr.20031218072017.2851:flattenOutline
    def flattenOutline (self,event=None):

        '''Export the selected outline to an external file.
        The outline is represented in MORE format.'''

        c = self

        filetypes = [("Text files", "*.txt"),("All files", "*")]

        fileName = g.app.gui.runSaveFileDialog(
            initialfile="flat.txt",
            title="Flatten Outline",
            filetypes=filetypes,
            defaultextension=".txt")
        c.bringToFront()

        if fileName and len(fileName) > 0:
            g.setGlobalOpenDir(fileName)
            g.chdir(fileName)
            c.importCommands.flattenOutline(fileName)
    #@-node:ekr.20031218072017.2851:flattenOutline
    #@+node:ekr.20031218072017.2852:importAtRoot
    def importAtRoot (self,event=None):

        '''Import one or more external files, creating @root trees.'''

        c = self

        types = [
            ("All files","*"),
            ("C/C++ files","*.c"),
            ("C/C++ files","*.cpp"),
            ("C/C++ files","*.h"),
            ("C/C++ files","*.hpp"),
            ("Java files","*.java"),
            ("Lua files", "*.lua"),
            ("Pascal files","*.pas"),
            ("Python files","*.py") ]

        names = g.app.gui.runOpenFileDialog(
            title="Import To @root",
            filetypes=types,
            defaultextension=".py",
            multiple=True)
        c.bringToFront()

        if names:
            g.chdir(names[0])
            c.importCommands.importFilesCommand (names,"@root")
    #@-node:ekr.20031218072017.2852:importAtRoot
    #@+node:ekr.20031218072017.2853:importAtFile
    def importAtFile (self,event=None):

        '''Import one or more external files, creating @file trees.'''

        c = self

        types = [
            ("All files","*"),
            ("C/C++ files","*.c"),
            ("C/C++ files","*.cpp"),
            ("C/C++ files","*.h"),
            ("C/C++ files","*.hpp"),
            ("Java files","*.java"),
            ("Lua files", "*.lua"),
            ("Pascal files","*.pas"),
            ("Python files","*.py") ]

        names = g.app.gui.runOpenFileDialog(
            title="Import To @file",
            filetypes=types,
            defaultextension=".py",
            multiple=True)
        c.bringToFront()

        if names:
            g.chdir(names[0])
            c.importCommands.importFilesCommand(names,"@file")
    #@-node:ekr.20031218072017.2853:importAtFile
    #@+node:ekr.20031218072017.2854:importCWEBFiles
    def importCWEBFiles (self,event=None):

        '''Import one or more external CWEB files, creating @file trees.'''

        c = self

        filetypes = [
            ("CWEB files", "*.w"),
            ("Text files", "*.txt"),
            ("All files", "*")]

        names = g.app.gui.runOpenFileDialog(
            title="Import CWEB Files",
            filetypes=filetypes,
            defaultextension=".w",
            multiple=True)
        c.bringToFront()

        if names:
            g.chdir(names[0])
            c.importCommands.importWebCommand(names,"cweb")
    #@-node:ekr.20031218072017.2854:importCWEBFiles
    #@+node:ekr.20031218072017.2855:importFlattenedOutline
    def importFlattenedOutline (self,event=None):

        '''Import an external created by the flatten-outline command.'''

        c = self

        types = [("Text files","*.txt"), ("All files","*")]

        names = g.app.gui.runOpenFileDialog(
            title="Import MORE Text",
            filetypes=types,
            defaultextension=".py",
            multiple=True)
        c.bringToFront()

        if names:
            g.chdir(names[0])
            c.importCommands.importFlattenedOutline(names)
    #@-node:ekr.20031218072017.2855:importFlattenedOutline
    #@+node:ekr.20031218072017.2856:importNowebFiles
    def importNowebFiles (self,event=None):

        '''Import one or more external noweb files, creating @file trees.'''

        c = self

        filetypes = [
            ("Noweb files", "*.nw"),
            ("Text files", "*.txt"),
            ("All files", "*")]

        names = g.app.gui.runOpenFileDialog(
            title="Import Noweb Files",
            filetypes=filetypes,
            defaultextension=".nw",
            multiple=True)
        c.bringToFront()

        if names:
            g.chdir(names[0])
            c.importCommands.importWebCommand(names,"noweb")
    #@-node:ekr.20031218072017.2856:importNowebFiles
    #@+node:ekr.20031218072017.2857:outlineToCWEB
    def outlineToCWEB (self,event=None):

        '''Export the selected outline to an external file.
        The outline is represented in CWEB format.'''

        c = self

        filetypes=[
            ("CWEB files", "*.w"),
            ("Text files", "*.txt"),
            ("All files", "*")]

        fileName = g.app.gui.runSaveFileDialog(
            initialfile="cweb.w",
            title="Outline To CWEB",
            filetypes=filetypes,
            defaultextension=".w")
        c.bringToFront()

        if fileName and len(fileName) > 0:
            g.setGlobalOpenDir(fileName)
            g.chdir(fileName)
            c.importCommands.outlineToWeb(fileName,"cweb")
    #@-node:ekr.20031218072017.2857:outlineToCWEB
    #@+node:ekr.20031218072017.2858:outlineToNoweb
    def outlineToNoweb (self,event=None):

        '''Export the selected outline to an external file.
        The outline is represented in noweb format.'''

        c = self

        filetypes=[
            ("Noweb files", "*.nw"),
            ("Text files", "*.txt"),
            ("All files", "*")]

        fileName = g.app.gui.runSaveFileDialog(
            initialfile=self.outlineToNowebDefaultFileName,
            title="Outline To Noweb",
            filetypes=filetypes,
            defaultextension=".nw")
        c.bringToFront()

        if fileName and len(fileName) > 0:
            g.setGlobalOpenDir(fileName)
            g.chdir(fileName)
            c.importCommands.outlineToWeb(fileName,"noweb")
            c.outlineToNowebDefaultFileName = fileName
    #@-node:ekr.20031218072017.2858:outlineToNoweb
    #@+node:ekr.20031218072017.2859:removeSentinels
    def removeSentinels (self,event=None):

        '''Import one or more files, removing any sentinels.'''

        c = self

        types = [
            ("All files","*"),
            ("C/C++ files","*.c"),
            ("C/C++ files","*.cpp"),
            ("C/C++ files","*.h"),
            ("C/C++ files","*.hpp"),
            ("Java files","*.java"),
            ("Lua files", "*.lua"),
            ("Pascal files","*.pas"),
            ("Python files","*.py") ]

        names = g.app.gui.runOpenFileDialog(
            title="Remove Sentinels",
            filetypes=types,
            defaultextension=".py",
            multiple=True)
        c.bringToFront()

        if names:
            g.chdir(names[0])
            c.importCommands.removeSentinelsCommand (names)
    #@-node:ekr.20031218072017.2859:removeSentinels
    #@+node:ekr.20031218072017.2860:weave
    def weave (self,event=None):

        '''Simulate a literate-programming weave operation by writing the outline to a text file.'''

        c = self

        filetypes = [("Text files", "*.txt"),("All files", "*")]

        fileName = g.app.gui.runSaveFileDialog(
            initialfile="weave.txt",
            title="Weave",
            filetypes=filetypes,
            defaultextension=".txt")
        c.bringToFront()

        if fileName and len(fileName) > 0:
            g.setGlobalOpenDir(fileName)
            g.chdir(fileName)
            c.importCommands.weave(fileName)
    #@-node:ekr.20031218072017.2860:weave
    #@-node:ekr.20031218072017.2849:Import&Export submenu
    #@-node:ekr.20031218072017.2819:File Menu
    #@+node:ekr.20031218072017.2861:Edit Menu...
    #@+node:ekr.20031218072017.2862:Edit top level
    #@+node:ekr.20031218072017.2140:c.executeScript & helpers
    def executeScript(self,event=None,args=None,p=None,script=None,
        useSelectedText=True,define_g=True,define_name='__main__',silent=False):

        """This executes body text as a Python script.

        We execute the selected text, or the entire body text if no text is selected."""

        c = self ; script1 = script
        writeScriptFile = c.config.getBool('write_script_file')
        if not script:
            script = g.getScript(c,p,useSelectedText=useSelectedText)
        self.redirectScriptOutput()
        try:
            log = c.frame.log
            if script.strip():
                sys.path.insert(0,c.frame.openDirectory)
                script += '\n' # Make sure we end the script properly.
                # g.pr('*** script',script)
                try:
                    p = c.currentPosition()
                    d = g.choose(define_g,{'c':c,'g':g,'p':p},{})
                    if define_name: d['__name__'] = define_name
                    if args:
                        # g.trace('setting sys.argv',args)
                        sys.argv = args
                    # A kludge: reset c.inCommand here to handle the case where we *never* return.
                    # (This can happen when there are multiple event loops.)
                    # This does not prevent zombie windows if the script puts up a dialog...
                    c.inCommand = False
                    # g.trace('**** before',writeScriptFile)
                    if writeScriptFile:
                        scriptFile = self.writeScriptFile(script)
                        execfile(scriptFile,d)
                    else:
                        exec(script,d)
                    # g.trace('**** after')
                    if not script1 and not silent:
                        # Careful: the script may have changed the log tab.
                        tabName = log and hasattr(log,'tabName') and log.tabName or 'Log'
                        g.es("end of script",color="purple",tabName=tabName)
                except Exception:
                    g.handleScriptException(c,p,script,script1)
                del sys.path[0]
            else:
                tabName = log and hasattr(log,'tabName') and log.tabName or 'Log'
                g.es("no script selected",color="blue",tabName=tabName)
        finally:
            self.unredirectScriptOutput()
    #@+node:ekr.20031218072017.2143:redirectScriptOutput
    def redirectScriptOutput (self):

        c = self

        if c.config.redirect_execute_script_output_to_log_pane:

            g.redirectStdout() # Redirect stdout
            g.redirectStderr() # Redirect stderr
    #@-node:ekr.20031218072017.2143:redirectScriptOutput
    #@+node:EKR.20040627100424:unredirectScriptOutput
    def unredirectScriptOutput (self):

        c = self

        if c.exists and c.config.redirect_execute_script_output_to_log_pane:

            g.restoreStderr()
            g.restoreStdout()
    #@-node:EKR.20040627100424:unredirectScriptOutput
    #@+node:ekr.20070115135502:writeScriptFile
    def writeScriptFile (self,script):

        # Get the path to the file.
        c = self
        path = c.config.getString('script_file_path')
        if path:
            parts = path.split('/')
            path = g.app.loadDir
            for part in parts:
                path = c.os_path_finalize_join(path,part)
        else:
            path = c.os_path_finalize_join(
                g.app.loadDir,'..','test','scriptFile.py')

        # Write the file.
        try:
            f = open(path,'w')
            f.write(script)
            f.close()
        except Exception:
            path = None

        return path
    #@nonl
    #@-node:ekr.20070115135502:writeScriptFile
    #@-node:ekr.20031218072017.2140:c.executeScript & helpers
    #@+node:ekr.20080710082231.10:c.gotoLineNumber and helpers
    def goToLineNumber (self,n,p=None,scriptData=None):

        '''Place the cursor on the n'th line of a derived file or script.
        When present scriptData is a dict with 'root' and 'lines' keys.'''

        c = self
        delim = None ; gnx = None ; vnodeName = None
        if n < 0: return

        fileName,ignoreSentinels,isRaw,lines,n,root = c.goto_setup(n,p,scriptData)

        if n==1:
            p = root ; n2 = 1 ; found = True
        elif n >= len(lines):
            p = root ; n2 = root.bodyString().count('\n') ; found = False
        elif isRaw:
            p,n2,found = c.goto_countLines(root,n)
        else:
            vnodeName,gnx,n2,delim = c.goto_findVnode(root,lines,n,ignoreSentinels)
            if delim:
                p,found = c.goto_findPosition(
                    root,lines,vnodeName,gnx,n,delim)
            else:
                p,found = root,False
        if 0:
            #@        << trace gotoLineNumber results >>
            #@+node:ekr.20080905130513.40:<< trace gotoLineNumber results >>
            g.trace(
                '\n  found',found,'n2',n2,'gnx',gnx,'delim',repr(delim),
                '\n  vnodeName',vnodeName,
                '\n  p        ',p and p.headString(),
                '\n  root     ',root and root.headString())
            #@-node:ekr.20080905130513.40:<< trace gotoLineNumber results >>
            #@nl
        c.goto_showResults(found,p or root,n,n2,lines)
    #@+node:ekr.20080708094444.65:goto_applyLineNumberMapping
    def goto_applyLineNumberMapping(self, n):

        c = self ; x = c.shadowController

        if len(x.line_mapping) > n:
            return x.line_mapping[n]
        else:
            return n
    #@-node:ekr.20080708094444.65:goto_applyLineNumberMapping
    #@+node:ekr.20080904071003.12:goto_countLines
    def goto_countLines (self,root,n):

        '''Scan through root's outline, looking for line n.
        Return (p,n2,found) where p is the found node,
        n2 is the actural line found, and found is True if the line was found.'''

        p = lastv = root
        prev = 0 ; found = False
        isNosent = root.isAtNoSentFileNode()
        isAuto = root.isAtAutoNode()

        for p in p.self_and_subtree_iter():
            lastv = p.copy()
            s = p.bodyString()
            if isNosent or isAuto:
                s = ''.join([z for z in g.splitLines(s) if not z.startswith('@')])
            n_lines = s.count('\n')
            if len(s) > 0 and s[-1] != '\n': n_lines += 1
            # g.trace(n,prev,n_lines,p.headString())
            if prev + n_lines >= n:
                found = True ; break
            prev += n_lines

        p = lastv
        n2 = max(1,n-prev)

        return p,n2,found
    #@-node:ekr.20080904071003.12:goto_countLines
    #@+node:ekr.20080904071003.4:goto_findPosition & helpers
    def goto_findPosition(self,root,lines,vnodeName,gnx,n,delim):

        c = self

        # if scriptFind:
            # p,found = c.scanForVnodeName(root,vnodeName

        if gnx:
            p,found = c.goto_findGnx(root,gnx,vnodeName)
        else:
            p,found = c.goto_scanTnodeList(root,delim,lines,n,vnodeName)

        # if not found:
            # g.es("not found:",vnodeName,color="red")

        return p,found
    #@+node:ekr.20080904071003.18:goto_findGnx
    def goto_findGnx (self,root,gnx,vnodeName):

        '''Scan root's tree for a node with the given gnx and vnodeName.

        return (p,found)'''

        gnx = g.app.nodeIndices.scanGnx(gnx,0)

        for p in root.self_and_subtree_iter():
            if p.matchHeadline(vnodeName):
                if p.v.t.fileIndex == gnx:
                    return p.copy(),True

        return None,False
    #@-node:ekr.20080904071003.18:goto_findGnx
    #@+node:ekr.20080904071003.19:goto_scanTnodeList
    def goto_scanTnodeList (self,root,delim,lines,n,vnodeName):

        # This is about the best that can be done without replicating the entire atFile write logic.
        found = False
        ok = hasattr(root.v.t,"tnodeList")

        if ok:
            # Use getattr to keep pylint happy.
            tnodeList = getattr(root.v.t,'tnodeList')
            #@        << set tnodeIndex to the number of +node sentinels before line n >>
            #@+node:ekr.20080904071003.8:<< set tnodeIndex to the number of +node sentinels before line n >>

            tnodeIndex = -1 # Don't count the @file node.
            scanned = 0 # count of lines scanned.

            for s in lines:
                if scanned >= n:
                    break
                i = g.skip_ws(s,0)
                if g.match(s,i,delim):
                    i += len(delim)
                    if g.match(s,i,"+node"):
                        # g.trace(tnodeIndex,s.rstrip())
                        tnodeIndex += 1
                scanned += 1
            #@-node:ekr.20080904071003.8:<< set tnodeIndex to the number of +node sentinels before line n >>
            #@nl
            tnodeIndex = max(0,tnodeIndex)
            #@        << set p to the first vnode whose tnode is tnodeList[tnodeIndex] or set ok = False >>
            #@+node:ekr.20080904071003.9:<< set p to the first vnode whose tnode is tnodeList[tnodeIndex] or set ok = false >>
            #@+at 
            #@nonl
            # We use the tnodeList to find a _tnode_ corresponding to the 
            # proper node, so the user will for sure be editing the proper 
            # text, even if several nodes happen to have the same headline.  
            # This is really all that we need.
            # 
            # However, this code has no good way of distinguishing between 
            # different cloned vnodes in the file: they all have the same 
            # tnode.  So this code just picks p = t.vnodeList[0] and leaves it 
            # at that.
            # 
            # The only way to do better is to scan the outline, replicating 
            # the write logic to determine which vnode created the given 
            # line.  That's way too difficult, and it would create an unwanted 
            # dependency in this code.
            #@-at
            #@@c

            # g.trace("tnodeIndex",tnodeIndex)
            if tnodeIndex < len(tnodeList):
                t = tnodeList[tnodeIndex]
                # Find the first vnode whose tnode is t.
                for p in root.self_and_subtree_iter():
                    if p.v.t == t:
                        found = True ; break
                if not found:
                    s = "tnode not found for " + vnodeName
                    g.es_print(s, color="red") ; ok = False
                elif p.headString().strip() != vnodeName:
                    if 0: # Apparently this error doesn't prevent a later scan for working properly.
                        s = "Mismatched vnodeName\nExpecting: %s\n got: %s" % (p.headString(),vnodeName)
                        g.es_print(s, color="red")
                    ok = False
            else:
                if root is None: # Kludge: disable this message when called by goToScriptLineNumber.
                    s = "Invalid computed tnodeIndex: %d" % tnodeIndex
                    g.es_print(s, color = "red")
                ok = False
            #@-node:ekr.20080904071003.9:<< set p to the first vnode whose tnode is tnodeList[tnodeIndex] or set ok = false >>
            #@nl
        else:
            g.es_print("no child index for",root.headString(),color="red")

        if not ok:
            # Fall back to the old logic.
            #@        << set p to the first node whose headline matches vnodeName >>
            #@+node:ekr.20080904071003.10:<< set p to the first node whose headline matches vnodeName >>
            for p in root.self_and_subtree_iter():
                if p.matchHeadline(vnodeName):
                    found = True ; break
            #@-node:ekr.20080904071003.10:<< set p to the first node whose headline matches vnodeName >>
            #@nl

        return p,found
    #@-node:ekr.20080904071003.19:goto_scanTnodeList
    #@-node:ekr.20080904071003.4:goto_findPosition & helpers
    #@+node:ekr.20031218072017.2877:goto_findVnode
    def goto_findVnode (self,root,lines,n,ignoreSentinels):

        '''Search the lines of a derived file containing sentinels for a vnode.
        return (vnodeName,gnx,offset,delim):

        vnodeName:  the name found in the previous @+body sentinel.
        gnx:        the gnx of the found node.
        offset:     the offset within the node of the desired line.
        delim:      the comment delim from the @+leo sentinel.
        '''

        c = self ; at = c.atFileCommands
        # g.trace('lines...\n',g.listToString(lines))
        gnx = None
        #@    << set delim, leoLine from the @+leo line >>
        #@+node:ekr.20031218072017.2878:<< set delim, leoLine from the @+leo line >>
        # Find the @+leo line.
        tag = "@+leo"
        i = 0 
        while i < len(lines) and lines[i].find(tag)==-1:
            i += 1
        leoLine = i # Index of the line containing the leo sentinel

        # Set delim from the @+leo line.
        delim = None
        if leoLine < len(lines):
            s = lines[leoLine]
            valid,newDerivedFile,start,end,thinFile = at.parseLeoSentinel(s)
            # New in Leo 4.5.1: only support 4.x files.
            if valid and newDerivedFile:
                delim = start + '@'
        #@-node:ekr.20031218072017.2878:<< set delim, leoLine from the @+leo line >>
        #@nl
        if not delim:
            g.es('no sentinels in:',root.headString())
            return None,None,None,None

        #@    << scan back to @+node, setting offset,nodeSentinelLine >>
        #@+node:ekr.20031218072017.2879:<< scan back to  @+node, setting offset,nodeSentinelLine >>
        #@+at
        # Scan backwards from the requested line, looking for an @-body line. 
        # When found,
        # we get the vnode's name from that line and set p to the indicated 
        # vnode. This
        # will fail if vnode names have been changed, and that can't be 
        # helped.
        # 
        # We compute the offset of the requested line **within the found 
        # node**.
        #@-at
        #@@c

        offset = 0 # This is essentially the Tk line number.
        nodeSentinelLine = -1
        line = n - 1 # Start with the requested line.
        while line >= 0:
            progress = line
            s = lines[line]
            i = g.skip_ws(s,0)
            if g.match(s,i,delim):
                #@        << handle delim while scanning backward >>
                #@+node:ekr.20031218072017.2880:<< handle delim while scanning backward >>
                if line == n:
                    g.es("line",str(n),"is a sentinel line")
                i += len(delim)

                if g.match(s,i,"-node"):
                    # The end of a nested section.
                    old_line = line
                    line = c.goto_skipToMatchingNodeSentinel(lines,line,delim)
                    assert line < old_line
                    # g.trace('found',repr(lines[line]))
                    nodeSentinelLine = line
                    offset = n-line
                    break
                elif g.match(s,i,"+node"):
                    # g.trace('found',repr(lines[line]))
                    nodeSentinelLine = line
                    offset = n-line
                    break
                elif g.match(s,i,"<<") or g.match(s,i,"@first"):
                    # if not ignoreSentinels:
                        # offset += 1 # Count these as a "real" lines.
                    line -= 1
                else:
                    line -= 1
                #@-node:ekr.20031218072017.2880:<< handle delim while scanning backward >>
                #@nl
            else:
                ### offset += 1 # Assume the line is real.  A dubious assumption.
                line -= 1
            assert line < progress
        #@-node:ekr.20031218072017.2879:<< scan back to  @+node, setting offset,nodeSentinelLine >>
        #@nl
        if nodeSentinelLine == -1:
            # The line precedes the first @+node sentinel
            g.trace('no @+node!!')
            return root.headString(),gnx,1,delim

        s = lines[nodeSentinelLine]

        #@    << set gnx and vnodeName from s >>
        #@+node:ekr.20031218072017.2881:<< set gnx and vnodeName from s >>
        i = 0 ; gnx = None ; vnodeName = None

        if thinFile:
            # gnx is lies between the first and second ':':
            i = s.find(':',i)
            if i > 0:
                i += 1
                j = s.find(':',i)
                if j > 0:   gnx = s[i:j]
                else:       i = len(s) # Force an error.
            else:
                i = len(s) # Force an error.

        # vnode name is everything following the first or second':'
        i = s.find(':',i)
        if i > -1:
            vnodeName = s[i+1:].strip()
        else:
            vnodeName = None
            g.es_print("bad @+node sentinel",color='red')
        #@-node:ekr.20031218072017.2881:<< set gnx and vnodeName from s >>
        #@nl
        if delim and vnodeName:
            # g.trace('offset',offset)
            return vnodeName,gnx,offset,delim
        else:
            g.es("bad @+node sentinel")
            return None,None,None,None
    #@-node:ekr.20031218072017.2877:goto_findVnode
    #@+node:ekr.20080904071003.28:goto_setup & helpers
    def goto_setup (self,n,p=None,scriptData=None):

        '''Return (fileName,isRaw,lines,n,p,root) where:

        fileName is the name of the nearest @file node, or None.
        isRaw is True if there are no sentinels in the file.
        lines are the lines to be scanned.
        n is the effective line number (munged for @shadow nodes).
        root is the nearest @file node, or c.currentPosition.'''

        c = self

        if scriptData:
            assert p is None
            lines = scriptData.get('lines')
            p = scriptData.get('p')
            root,fileName = c.goto_findRoot(p)
        else:
            # p is for unit testing only!
            if not p: p = c.currentPosition()
            root,fileName = c.goto_findRoot(p)
            if root and fileName:
                c.shadowController.line_mapping = [] # Set by goto_open.
                lines = c.goto_getFileLines(root,fileName)
                n = c.goto_applyLineNumberMapping(n)
            else:
                lines = c.goto_getScriptLines(p)

        isRaw = not root or (
            root.isAtAsisFileNode() or root.isAtNoSentFileNode() or root.isAtAutoNode())

        ignoreSentinels = root and root.isAtNoSentFileNode()

        if scriptData:
            if not root: root = p.copy()
        else:
            if not root: root = c.currentPosition()

        return fileName,ignoreSentinels,isRaw,lines,n,root
    #@+node:ekr.20080904071003.25:goto_findRoot
    def goto_findRoot (self,p):

        '''Find the closest ancestor @file node, of any type, except @all nodes.

        return root, fileName.'''

        c = self ; p1 = p.copy()

        # First look for ancestor @file node.
        for p in p.self_and_parents_iter():
            fileName = not p.isAtAllNode() and p.anyAtFileNodeName()
            if fileName:
                return p.copy(),fileName

        # Search the entire tree for joined nodes.
        # Bug fix: Leo 4.5.1: *must* search *all* positions.
        for p in c.all_positions_iter():
            # if p.v.t == p1.v.t: g.trace('p1',p1,'p',p)
            if p.v.t == p1.v.t and p != p1:
                # Found a joined position.
                for p2 in p.self_and_parents_iter():
                    fileName = not p2.isAtAllNode() and p2.anyAtFileNodeName()
                    if fileName:
                        return p2.copy(),fileName

        return None,None
    #@-node:ekr.20080904071003.25:goto_findRoot
    #@+node:ekr.20080904071003.26:goto_getFileLines
    def goto_getFileLines (self,root,fileName):

        '''Read the file into lines.'''

        c = self

        if root.isAtNoSentFileNode():
            # Write a virtual file containing sentinels.
            at = c.atFileCommands
            at.write(root,nosentinels=False,toString=True)
            lines = g.splitLines(at.stringOutput)
        else:
            # Calculate the full path.
            d = g.scanDirectives(c,p=root)
            path = d.get("path")
            # g.trace('path',path,'fileName',fileName)
            fileName = c.os_path_finalize_join(path,fileName)
            lines    = c.goto_open(fileName)

        return lines
    #@-node:ekr.20080904071003.26:goto_getFileLines
    #@+node:ekr.20080904071003.27:goto_getScriptLines
    def goto_getScriptLines (self,p):

        c = self

        if not g.unitTesting:
            g.es("no ancestor @file node: using script line numbers", color="blue")

        lines = g.getScript (c,p,useSelectedText=False)
        lines = g.splitLines(lines)

        return lines
    #@-node:ekr.20080904071003.27:goto_getScriptLines
    #@+node:ekr.20080708094444.63:goto_open
    def goto_open (self,filename):
        """
        Open a file for "goto linenumber" command and check if a shadow file exists.
        Construct a line mapping. This ivar is empty i no shadow file exists.
        Otherwise it contains a mapping shadow file number -> real file number.
        """

        c = self ; x = c.shadowController

        try:
            shadow_filename = x.shadowPathName(filename)
            if os.path.exists(shadow_filename):
                fn = shadow_filename
                lines = open(shadow_filename).readlines()
                x.line_mapping = x.push_filter_mapping(
                    lines, x.marker_from_extension(shadow_filename))
            else:
                # Just open the original file.  This is not an error!
                fn = filename
                c.line_mapping = []
                lines = open(filename).readlines()
        except Exception:
            # Make sure failures to open a file generate clear messages.
            g.es_print('can not open',fn,color='blue')
            # g.es_exception()
            lines = []

        return lines
    #@-node:ekr.20080708094444.63:goto_open
    #@-node:ekr.20080904071003.28:goto_setup & helpers
    #@+node:ekr.20080904071003.14:goto_showResults
    def goto_showResults(self,found,p,n,n2,lines):

        c = self ; w = c.frame.body.bodyCtrl

        # Select p and make it visible.
        c.frame.tree.expandAllAncestors(p)
        c.selectPosition(p)
        c.redraw()

        # Put the cursor on line n2 of the body text.
        s = w.getAllText()
        if found:
            ins = g.convertRowColToPythonIndex(s,n2-1,0)    
        else:
            ins = len(s)
            if len(lines) < n and not g.unitTesting:
                g.es('only',len(lines),'lines',color="blue")

        # g.trace('n',n,'ins',ins,'p',p.headString())

        w.setInsertPoint(ins)
        c.bodyWantsFocusNow()
        w.seeInsertPoint()
    #@-node:ekr.20080904071003.14:goto_showResults
    #@+node:ekr.20031218072017.2882:goto_skipToMatchingNodeSentinel
    def goto_skipToMatchingNodeSentinel (self,lines,n,delim):

        s = lines[n]
        i = g.skip_ws(s,0)
        assert(g.match(s,i,delim))
        i += len(delim)
        if g.match(s,i,"+node"):
            start="+node" ; end="-node" ; delta=1
        else:
            assert(g.match(s,i,"-node"))
            start="-node" ; end="+node" ; delta=-1
        # Scan to matching @+-node delim.
        n += delta ; level = 0
        while 0 <= n < len(lines):
            s = lines[n] ; i = g.skip_ws(s,0)
            if g.match(s,i,delim):
                i += len(delim)
                if g.match(s,i,start):
                    level += 1
                elif g.match(s,i,end):
                    if level == 0: break
                    else: level -= 1
            n += delta

        # g.trace(n)
        return n
    #@-node:ekr.20031218072017.2882:goto_skipToMatchingNodeSentinel
    #@-node:ekr.20080710082231.10:c.gotoLineNumber and helpers
    #@+node:EKR.20040612232221:c.goToScriptLineNumber
    # Called from g.handleScriptException.

    def goToScriptLineNumber (self,p,script,n):

        """Go to line n of a script."""

        c = self

        scriptData = {'p':p.copy(),'lines':g.splitLines(script)}
        c.goToLineNumber(n=n,scriptData=scriptData)
    #@-node:EKR.20040612232221:c.goToScriptLineNumber
    #@+node:ekr.20031218072017.2088:fontPanel
    def fontPanel (self,event=None):

        '''Open the font dialog.'''

        c = self ; frame = c.frame

        if not frame.fontPanel:
            frame.fontPanel = g.app.gui.createFontPanel(c)

        frame.fontPanel.bringToFront()
    #@-node:ekr.20031218072017.2088:fontPanel
    #@+node:ekr.20031218072017.2090:colorPanel
    def colorPanel (self,event=None):

        '''Open the color dialog.'''

        c = self ; frame = c.frame

        if not frame.colorPanel:
            frame.colorPanel = g.app.gui.createColorPanel(c)

        frame.colorPanel.bringToFront()
    #@-node:ekr.20031218072017.2090:colorPanel
    #@+node:ekr.20031218072017.2883:show/hide/toggleInvisibles
    def hideInvisibles (self,event=None):
        c = self ; c.showInvisiblesHelper(False)

    def showInvisibles (self,event=None):
        c = self ; c.showInvisiblesHelper(True)

    def toggleShowInvisibles (self,event=None):
        c = self ; colorizer = c.frame.body.getColorizer()
        val = g.choose(colorizer.showInvisibles,0,1)
        c.showInvisiblesHelper(val)

    def showInvisiblesHelper (self,val):
        c = self ; frame = c.frame ; p = c.currentPosition()
        colorizer = frame.body.getColorizer()
        colorizer.showInvisibles = val

         # It is much easier to change the menu name here than in the menu updater.
        menu = frame.menu.getMenu("Edit")
        index = frame.menu.getMenuLabel(menu,g.choose(val,'Hide Invisibles','Show Invisibles'))
        if index is None:
            if val: frame.menu.setMenuLabel(menu,"Show Invisibles","Hide Invisibles")
            else:   frame.menu.setMenuLabel(menu,"Hide Invisibles","Show Invisibles")

        c.frame.body.recolor_now(p)
    #@-node:ekr.20031218072017.2883:show/hide/toggleInvisibles
    #@+node:ekr.20031218072017.2086:preferences
    def preferences (self,event=None):

        '''Handle the preferences command.'''

        c = self
        c.openLeoSettings()
    #@-node:ekr.20031218072017.2086:preferences
    #@-node:ekr.20031218072017.2862:Edit top level
    #@+node:ekr.20031218072017.2884:Edit Body submenu
    #@+node:ekr.20031218072017.1704:convertAllBlanks
    def convertAllBlanks (self,event=None):

        '''Convert all blanks to tabs in the selected outline.'''

        c = self ; u = c.undoer ; undoType = 'Convert All Blanks'
        current = c.currentPosition()

        if g.app.batchMode:
            c.notValidInBatchMode(undoType)
            return

        d = c.scanAllDirectives()
        tabWidth  = d.get("tabwidth")
        count = 0 ; dirtyVnodeList = []
        u.beforeChangeGroup(current,undoType)
        for p in current.self_and_subtree_iter():
            # g.trace(p.headString(),tabWidth)
            innerUndoData = u.beforeChangeNodeContents(p)
            if p == current:
                changed,dirtyVnodeList2 = c.convertBlanks(event)
                if changed:
                    count += 1
                    dirtyVnodeList.extend(dirtyVnodeList2)
            else:
                changed = False ; result = []
                text = p.t._bodyString
                assert(g.isUnicode(text))
                lines = text.split('\n')
                for line in lines:
                    i,w = g.skip_leading_ws_with_indent(line,0,tabWidth)
                    s = g.computeLeadingWhitespace(w,abs(tabWidth)) + line[i:] # use positive width.
                    if s != line: changed = True
                    result.append(s)
                if changed:
                    count += 1
                    dirtyVnodeList2 = p.setDirty()
                    dirtyVnodeList.extend(dirtyVnodeList2)
                    result = '\n'.join(result)
                    p.setBodyString(result)
                    u.afterChangeNodeContents(p,undoType,innerUndoData)
        u.afterChangeGroup(current,undoType,dirtyVnodeList=dirtyVnodeList)
        if not g.unitTesting:
            g.es("blanks converted to tabs in",count,"nodes") # Must come before c.redraw().
        if count > 0: c.redraw()
    #@-node:ekr.20031218072017.1704:convertAllBlanks
    #@+node:ekr.20031218072017.1705:convertAllTabs
    def convertAllTabs (self,event=None):

        '''Convert all tabs to blanks in the selected outline.'''

        c = self ; u = c.undoer ; undoType = 'Convert All Tabs'
        current = c.currentPosition()

        if g.app.batchMode:
            c.notValidInBatchMode(undoType)
            return
        theDict = c.scanAllDirectives()
        tabWidth  = theDict.get("tabwidth")
        count = 0 ; dirtyVnodeList = []
        u.beforeChangeGroup(current,undoType)
        for p in current.self_and_subtree_iter():
            undoData = u.beforeChangeNodeContents(p)
            if p == current:
                changed,dirtyVnodeList2 = self.convertTabs(event)
                if changed:
                    count += 1
                    dirtyVnodeList.extend(dirtyVnodeList2)
            else:
                result = [] ; changed = False
                text = p.t._bodyString
                assert(g.isUnicode(text))
                lines = text.split('\n')
                for line in lines:
                    i,w = g.skip_leading_ws_with_indent(line,0,tabWidth)
                    s = g.computeLeadingWhitespace(w,-abs(tabWidth)) + line[i:] # use negative width.
                    if s != line: changed = True
                    result.append(s)
                if changed:
                    count += 1
                    dirtyVnodeList2 = p.setDirty()
                    dirtyVnodeList.extend(dirtyVnodeList2)
                    result = '\n'.join(result)
                    p.setBodyString(result)
                    u.afterChangeNodeContents(p,undoType,undoData)
        u.afterChangeGroup(current,undoType,dirtyVnodeList=dirtyVnodeList)
        if not g.unitTesting:
            g.es("tabs converted to blanks in",count,"nodes")
        if count > 0: c.redraw()
    #@-node:ekr.20031218072017.1705:convertAllTabs
    #@+node:ekr.20031218072017.1821:convertBlanks
    def convertBlanks (self,event=None):

        '''Convert all blanks to tabs in the selected node.'''

        c = self ; changed = False ; dirtyVnodeList = []
        head,lines,tail,oldSel,oldYview = c.getBodyLines(expandSelection=True)

        # Use the relative @tabwidth, not the global one.
        theDict = c.scanAllDirectives()
        tabWidth  = theDict.get("tabwidth")
        if tabWidth:
            result = []
            for line in lines:
                s = g.optimizeLeadingWhitespace(line,abs(tabWidth)) # Use positive width.
                if s != line: changed = True
                result.append(s)
            if changed:
                undoType = 'Convert Blanks'
                result = ''.join(result)
                oldSel = None
                dirtyVnodeList = c.updateBodyPane(head,result,tail,undoType,oldSel,oldYview) # Handles undo

        return changed,dirtyVnodeList
    #@-node:ekr.20031218072017.1821:convertBlanks
    #@+node:ekr.20031218072017.1822:convertTabs
    def convertTabs (self,event=None):

        '''Convert all tabs to blanks in the selected node.'''

        c = self ; changed = False ; dirtyVnodeList = []
        head,lines,tail,oldSel,oldYview = self.getBodyLines(expandSelection=True)

        # Use the relative @tabwidth, not the global one.
        theDict = c.scanAllDirectives()
        tabWidth  = theDict.get("tabwidth")
        if tabWidth:
            result = []
            for line in lines:
                i,w = g.skip_leading_ws_with_indent(line,0,tabWidth)
                s = g.computeLeadingWhitespace(w,-abs(tabWidth)) + line[i:] # use negative width.
                if s != line: changed = True
                result.append(s)
            if changed:
                undoType = 'Convert Tabs'
                result = ''.join(result)
                oldSel = None
                dirtyVnodeList = c.updateBodyPane(head,result,tail,undoType,oldSel,oldYview) # Handles undo

        return changed,dirtyVnodeList
    #@-node:ekr.20031218072017.1822:convertTabs
    #@+node:ekr.20031218072017.1823:createLastChildNode
    def createLastChildNode (self,parent,headline,body):

        '''A helper function for the three extract commands.'''

        c = self

        if body and len(body) > 0:
            body = body.rstrip()
        if not body or len(body) == 0:
            body = ""

        p = parent.insertAsLastChild()
        p.initHeadString(headline)
        p.setBodyString(body)
        p.setDirty()
        c.validateOutline()
        return p
    #@-node:ekr.20031218072017.1823:createLastChildNode
    #@+node:ekr.20031218072017.1824:dedentBody
    def dedentBody (self,event=None):

        '''Remove one tab's worth of indentation from all presently selected lines.'''

        c = self ; current = c.currentPosition() ; undoType='Unindent'

        d = c.scanAllDirectives(current) # Support @tab_width directive properly.
        tab_width = d.get("tabwidth",c.tab_width)
        head,lines,tail,oldSel,oldYview = self.getBodyLines()

        result = [] ; changed = False
        for line in lines:
            i, width = g.skip_leading_ws_with_indent(line,0,tab_width)
            s = g.computeLeadingWhitespace(width-abs(tab_width),tab_width) + line[i:]
            if s != line: changed = True
            result.append(s)

        if changed:
            result = ''.join(result)
            c.updateBodyPane(head,result,tail,undoType,oldSel,oldYview)
    #@-node:ekr.20031218072017.1824:dedentBody
    #@+node:ekr.20031218072017.1706:extract (test)
    def extract (self,event=None):

        '''Create child node from the elected body text, deleting all selected text.
        The text must start with a section reference.  This becomes the new child's headline.
        The body text of the new child node contains all selected lines that follow the section reference line.'''

        c = self ; u = c.undoer ; undoType = 'Extract'
        current = c.currentPosition()
        head,lines,tail,oldSel,oldYview = self.getBodyLines()
        if lines:
            headline = lines[0].strip()
            del lines[0]
        if not lines:
            if not g.unitTesting:
                g.es("nothing follows section name",color="blue")
            return

        # Remove leading whitespace from all body lines.
        junk, ws = g.skip_leading_ws_with_indent(lines[0],0,c.tab_width)
        strippedLines = [g.removeLeadingWhitespace(line,ws,c.tab_width)
            for line in lines]
        newBody = ''.join(strippedLines)
        if head: head = head.rstrip()

        u.beforeChangeGroup(current,undoType)
        if 1: # In group...
            undoData = u.beforeInsertNode(current)
            p = c.createLastChildNode(current,headline,newBody)
            u.afterInsertNode(p,undoType,undoData)
            c.updateBodyPane(head+'\n',None,tail,undoType=undoType,oldSel=None,oldYview=oldYview)
        u.afterChangeGroup(current,undoType=undoType)
        c.redraw()
    #@-node:ekr.20031218072017.1706:extract (test)
    #@+node:ekr.20031218072017.1708:extractSection
    def extractSection (self,event=None):

        '''Create a section definition node from the selected body text.
        The text must start with a section reference.  This becomes the new child's headline.
        The body text of the new child node contains all selected lines that follow the section reference line.'''

        c = self ; u = c.undoer ; undoType='Extract Section'
        current = c.currentPosition()
        head,lines,tail,oldSel,oldYview = self.getBodyLines()
        if not lines: return

        line1 = '\n' + lines[0]
        headline = lines[0].strip() ; del lines[0]
        #@    << Set headline for extractSection >>
        #@+node:ekr.20031218072017.1709:<< Set headline for extractSection >>
        if len(headline) < 5:
            oops = True
        else:
            head1 = headline[0:2] == '<<'
            head2 = headline[0:2] == '@<'
            tail1 = headline[-2:] == '>>'
            tail2 = headline[-2:] == '@>'
            oops = not (head1 and tail1) and not (head2 and tail2)

        if oops:
            g.es("selected text should start with a section name",color="blue")
            return
        #@-node:ekr.20031218072017.1709:<< Set headline for extractSection >>
        #@nl
        if not lines:
            if not g.unitTesting:
                g.es("nothing follows section name",color="blue")
            return

        # Remove leading whitespace from all body lines.
        junk, ws = g.skip_leading_ws_with_indent(lines[0],0,c.tab_width)
        strippedLines = [g.removeLeadingWhitespace(line,ws,c.tab_width)
            for line in lines]
        newBody = ''.join(strippedLines)
        if head: head = head.rstrip()

        u.beforeChangeGroup(current,undoType)
        if 1: # In group...
            undoData = u.beforeInsertNode(current)
            p = c.createLastChildNode(current,headline,newBody)
            u.afterInsertNode(p,undoType,undoData)
            c.updateBodyPane(head+line1,None,tail,undoType=undoType,oldSel=None,oldYview=oldYview)
        u.afterChangeGroup(current,undoType=undoType)
        c.redraw()
    #@-node:ekr.20031218072017.1708:extractSection
    #@+node:ekr.20031218072017.1710:extractSectionNames
    def extractSectionNames(self,event=None):

        '''Create child nodes for every section reference in the selected text.
        The headline of each new child node is the section reference.
        The body of each child node is empty.'''

        c = self ; u = c.undoer ; undoType = 'Extract Section Names'
        body = c.frame.body ; current = c.currentPosition()
        head,lines,tail,oldSel,oldYview = self.getBodyLines()
        if not lines: return

        u.beforeChangeGroup(current,undoType)
        if 1: # In group...
            found = False
            for s in lines:
                #@            << Find the next section name >>
                #@+node:ekr.20031218072017.1711:<< Find the next section name >>
                head1 = s.find("<<")
                if head1 > -1:
                    head2 = s.find(">>",head1)
                else:
                    head1 = s.find("@<")
                    if head1 > -1:
                        head2 = s.find("@>",head1)

                if head1 == -1 or head2 == -1 or head1 > head2:
                    name = None
                else:
                    name = s[head1:head2+2]
                #@-node:ekr.20031218072017.1711:<< Find the next section name >>
                #@nl
                if name:
                    undoData = u.beforeInsertNode(current)
                    p = self.createLastChildNode(current,name,None)
                    u.afterInsertNode(p,undoType,undoData)
                    found = True
            c.selectPosition(current)
            c.validateOutline()
            if not found:
                g.es("selected text should contain one or more section names",color="blue")
        u.afterChangeGroup(current,undoType)
        c.redraw()

        # Restore the selection.
        body.setSelectionRange(oldSel)
        body.setFocus()
    #@-node:ekr.20031218072017.1710:extractSectionNames
    #@+node:ekr.20031218072017.1825:c.findBoundParagraph
    def findBoundParagraph (self,event=None):

        c = self
        head,ins,tail = c.frame.body.getInsertLines()

        if not ins or ins.isspace() or ins[0] == '@':
            return None,None,None

        head_lines = g.splitLines(head)
        tail_lines = g.splitLines(tail)

        if 0:
            #@        << trace head_lines, ins, tail_lines >>
            #@+node:ekr.20031218072017.1826:<< trace head_lines, ins, tail_lines >>
            if 0:
                g.pr("\nhead_lines")
                for line in head_lines:
                    g.pr(line)
                g.pr("\nins", ins)
                g.pr("\ntail_lines")
                for line in tail_lines:
                    g.pr(line)
            else:
                g.es_print("head_lines: ",head_lines)
                g.es_print("ins: ",ins)
                g.es_print("tail_lines: ",tail_lines)
            #@-node:ekr.20031218072017.1826:<< trace head_lines, ins, tail_lines >>
            #@nl

        # Scan backwards.
        i = len(head_lines)
        while i > 0:
            i -= 1
            line = head_lines[i]
            if len(line) == 0 or line.isspace() or line[0] == '@':
                i += 1 ; break

        pre_para_lines = head_lines[:i]
        para_head_lines = head_lines[i:]

        # Scan forwards.
        i = 0
        for line in tail_lines:
            if not line or line.isspace() or line.startswith('@'):
                break
            i += 1

        para_tail_lines = tail_lines[:i]
        post_para_lines = tail_lines[i:]

        head = g.joinLines(pre_para_lines)
        result = para_head_lines 
        result.extend([ins])
        result.extend(para_tail_lines)
        tail = g.joinLines(post_para_lines)

        return head,result,tail # string, list, string
    #@nonl
    #@-node:ekr.20031218072017.1825:c.findBoundParagraph
    #@+node:ekr.20031218072017.1827:c.findMatchingBracket, helper and test
    def findMatchingBracket (self,event=None):

        '''Select the text between matching brackets.'''

        c = self ; w = c.frame.body.bodyCtrl

        if g.app.batchMode:
            c.notValidInBatchMode("Match Brackets")
            return

        brackets = "()[]{}<>"
        s = w.getAllText()
        ins = w.getInsertPoint()
        ch1 = 0 <= ins-1 < len(s) and s[ins-1] or ''
        ch2 = 0 <= ins   < len(s) and s[ins] or ''
        # g.trace(repr(ch1),repr(ch2),ins)

        # Prefer to match the character to the left of the cursor.
        if ch1 and ch1 in brackets:
            ch = ch1 ; index = max(0,ins-1)
        elif ch2 and ch2 in brackets:
            ch = ch2 ; index = ins
        else:
            return

        index2 = self.findMatchingBracketHelper(s,ch,index)
        # g.trace('index,index2',index,index2)
        if index2 is not None:
            if index2 < index:
                w.setSelectionRange(index2,index+1,insert=index2) # was insert=index2+1
                # g.trace('case 1',s[index2:index+1])
            else:
                w.setSelectionRange(index,index2+1,insert=min(len(s),index2+1))
                # g.trace('case2',s[index:index2+1])
            w.see(index2)
        else:
            g.es("unmatched",repr(ch))
    #@nonl
    #@+node:ekr.20061113221414:findMatchingBracketHelper
    # To do: replace comments with blanks before scanning.
    # Test  unmatched())
    def findMatchingBracketHelper(self,s,ch,index):

        c = self
        open_brackets  = "([{<" ; close_brackets = ")]}>"
        brackets = open_brackets + close_brackets
        matching_brackets = close_brackets + open_brackets
        forward = ch in open_brackets
        # Find the character matching the initial bracket.
        # g.trace('index',index,'ch',repr(ch),'brackets',brackets)
        for n in range(len(brackets)):
            if ch == brackets[n]:
                match_ch = matching_brackets[n]
                break
        else:
            return None
        # g.trace('index',index,'ch',repr(ch),'match_ch',repr(match_ch))
        level = 0
        while 1:
            if forward and index >= len(s):
                # g.trace("not found")
                return None
            ch2 = 0 <= index < len(s) and s[index] or ''
            # g.trace('forward',forward,'ch2',repr(ch2),'index',index)
            if ch2 == ch:
                level += 1
            if ch2 == match_ch:
                level -= 1
                if level <= 0:
                    return index
            if not forward and index <= 0:
                # g.trace("not found")
                return None
            index += g.choose(forward,1,-1)
        return 0 # unreachable: keeps pychecker happy.
    # Test  (
    # ([(x){y}]))
    # Test  ((x)(unmatched
    #@-node:ekr.20061113221414:findMatchingBracketHelper
    #@-node:ekr.20031218072017.1827:c.findMatchingBracket, helper and test
    #@+node:ekr.20031218072017.1829:getBodyLines
    def getBodyLines (self,expandSelection=False):

        """Return head,lines,tail where:

        before is string containg all the lines before the selected text
        (or the text before the insert point if no selection)
        lines is a list of lines containing the selected text (or the line containing the insert point if no selection)
        after is a string all lines after the selected text
        (or the text after the insert point if no selection)"""

        c = self ; body = c.frame.body ; w = body.bodyCtrl
        oldVview = body.getYScrollPosition()

        if expandSelection:
            s = w.getAllText()
            head = tail = ''
            oldSel = 0,len(s)
            lines = g.splitLines(s) # Retain the newlines of each line.
        else:
            # Note: lines is the entire line containing the insert point if no selection.
            head,s,tail = body.getSelectionLines()
            lines = g.splitLines(s) # Retain the newlines of each line.

            # Expand the selection.
            i = len(head)
            j = max(i,len(head)+len(s)-1)
            oldSel = i,j

        return head,lines,tail,oldSel,oldVview # string,list,string,tuple.
    #@-node:ekr.20031218072017.1829:getBodyLines
    #@+node:ekr.20031218072017.1830:indentBody (test)
    def indentBody (self,event=None):

        '''The indent-region command indents each line of the selected body text,
        or each line of a node if there is no selected text. The @tabwidth directive
        in effect determines amount of indentation. (not yet) A numeric argument
        specifies the column to indent to.'''

        c = self ; current = c.currentPosition() ; undoType='Indent Region'
        d = c.scanAllDirectives(current) # Support @tab_width directive properly.
        tab_width = d.get("tabwidth",c.tab_width)
        head,lines,tail,oldSel,oldYview = self.getBodyLines()

        result = [] ; changed = False
        for line in lines:
            i, width = g.skip_leading_ws_with_indent(line,0,tab_width)
            s = g.computeLeadingWhitespace(width+abs(tab_width),tab_width) + line[i:]
            if s != line: changed = True
            result.append(s)

        if changed:
            result = ''.join(result)
            c.updateBodyPane(head,result,tail,undoType,oldSel,oldYview)
    #@-node:ekr.20031218072017.1830:indentBody (test)
    #@+node:ekr.20031218072017.1831:insertBodyTime, helpers and tests
    def insertBodyTime (self,event=None):

        '''Insert a time/date stamp at the cursor.'''

        c = self ; undoType = 'Insert Body Time'
        w = c.frame.body.bodyCtrl

        if g.app.batchMode:
            c.notValidInBatchMode(undoType)
            return

        oldSel = c.frame.body.getSelectionRange()
        w.deleteTextSelection()
        s = self.getTime(body=True)
        i = w.getInsertPoint()
        w.insert(i,s)

        c.frame.body.onBodyChanged(undoType,oldSel=oldSel)
    #@+node:ekr.20031218072017.1832:getTime
    def getTime (self,body=True):

        c = self
        default_format =  "%m/%d/%Y %H:%M:%S" # E.g., 1/30/2003 8:31:55

        # Try to get the format string from leoConfig.txt.
        if body:
            format = c.config.getString("body_time_format_string")
            gmt    = c.config.getBool("body_gmt_time")
        else:
            format = c.config.getString("headline_time_format_string")
            gmt    = c.config.getBool("headline_gmt_time")

        if format == None:
            format = default_format

        try:
            import time
            if gmt:
                s = time.strftime(format,time.gmtime())
            else:
                s = time.strftime(format,time.localtime())
        except (ImportError, NameError):
            g.es("time.strftime not available on this platform",color="blue")
            return ""
        except:
            g.es_exception() # Probably a bad format string in leoSettings.leo.
            s = time.strftime(default_format,time.gmtime())
        return s
    #@-node:ekr.20031218072017.1832:getTime
    #@-node:ekr.20031218072017.1831:insertBodyTime, helpers and tests
    #@+node:ekr.20050312114529:insert/removeComments
    #@+node:ekr.20050312114529.1:addComments (test)
    def addComments (self,event=None):

        '''Convert all selected lines in the body text to comment lines.'''

        c = self ; p = c.currentPosition()
        d = c.scanAllDirectives(p)
        d1,d2,d3 = d.get('delims') # d1 is the line delim.
        head,lines,tail,oldSel,oldYview = self.getBodyLines()
        if not lines:
            g.es('no text selected',color='blue')
            return

        d2 = d2 or '' ; d3 = d3 or ''
        if d1: openDelim,closeDelim = d1+' ',''
        else:  openDelim,closeDelim = d2+' ',d3+' '

        # Comment out non-blank lines.
        result = []
        for line in lines:
            if line.strip():
                i = g.skip_ws(line,0)
                result.append(line[0:i]+openDelim+line[i:]+closeDelim)
            else:
                result.append(line)

        result = ''.join(result)
        c.updateBodyPane(head,result,tail,undoType='Add Comments',oldSel=None,oldYview=oldYview)
    #@-node:ekr.20050312114529.1:addComments (test)
    #@+node:ekr.20050312114529.2:deleteComments (test)
    def deleteComments (self,event=None):

        '''Remove one level of comment delimiters from all selected lines in the body text.'''

        c = self ; p = c.currentPosition()
        d = c.scanAllDirectives(p)
        # d1 is the line delim.
        d1,d2,d3 = d.get('delims')

        head,lines,tail,oldSel,oldYview = self.getBodyLines()
        result = []
        if not lines:
            g.es('no text selected',color='blue')
            return

        if d1:
            # Append the single-line comment delim in front of each line
            for line in lines:
                i = g.skip_ws(line,0)
                if g.match(line,i,d1):
                    j = g.skip_ws(line,i + len(d1))
                    result.append(line[0:i] + line[j:])
                else:
                    result.append(line)
        else:
            n = len(lines)
            for i in range(n):
                line = lines[i]
                if i not in (0,n-1):
                    result.append(line)
                if i == 0:
                    j = g.skip_ws(line,0)
                    if g.match(line,j,d2):
                        k = g.skip_ws(line,j + len(d2))
                        result.append(line[0:j] + line[k:])
                    else:
                        g.es('',"'%s'" % (d2),"not found",color='blue')
                        return
                if i == n-1:
                    if i == 0:
                        line = result[0] ; result = []
                    s = line.rstrip()
                    if s.endswith(d3):
                        result.append(s[:-len(d3)].rstrip())
                    else:
                        g.es('',"'%s'" % (d3),"not found",color='blue')
                        return

        result = ''.join(result)
        c.updateBodyPane(head,result,tail,undoType='Delete Comments',oldSel=None,oldYview=oldYview)
    #@-node:ekr.20050312114529.2:deleteComments (test)
    #@-node:ekr.20050312114529:insert/removeComments
    #@+node:ekr.20031218072017.1833:reformatParagraph
    def reformatParagraph (self,event=None,undoType='Reformat Paragraph'):

        """Reformat a text paragraph in a Tk.Text widget

    Wraps the concatenated text to present page width setting. Leading tabs are
    sized to present tab width setting. First and second line of original text is
    used to determine leading whitespace in reformatted text. Hanging indentation
    is honored.

    Paragraph is bound by start of body, end of body, blank lines, and lines
    starting with "@". Paragraph is selected by position of current insertion
    cursor."""

        c = self ; body = c.frame.body ; w = body.bodyCtrl

        if g.app.batchMode:
            c.notValidInBatchMode("xxx")
            return

        if body.hasTextSelection():
            i,j = w.getSelectionRange()
            w.setInsertPoint(i)

        #@    << compute vars for reformatParagraph >>
        #@+node:ekr.20031218072017.1834:<< compute vars for reformatParagraph >>
        theDict = c.scanAllDirectives()
        pageWidth = theDict.get("pagewidth")
        tabWidth  = theDict.get("tabwidth")

        original = w.getAllText()
        oldSel =  w.getSelectionRange()
        oldYview = body.getYScrollPosition()

        head,lines,tail = c.findBoundParagraph()
        #@-node:ekr.20031218072017.1834:<< compute vars for reformatParagraph >>
        #@nl
        if lines:
            #@        << compute the leading whitespace >>
            #@+node:ekr.20031218072017.1835:<< compute the leading whitespace >>
            indents = [0,0] ; leading_ws = ["",""]

            for i in (0,1):
                if i < len(lines):
                    # Use the original, non-optimized leading whitespace.
                    leading_ws[i] = ws = g.get_leading_ws(lines[i])
                    indents[i] = g.computeWidth(ws,tabWidth)

            indents[1] = max(indents)
            if len(lines) == 1:
                leading_ws[1] = leading_ws[0]
            #@-node:ekr.20031218072017.1835:<< compute the leading whitespace >>
            #@nl
            #@        << compute the result of wrapping all lines >>
            #@+node:ekr.20031218072017.1836:<< compute the result of wrapping all lines >>
            trailingNL = lines and lines[-1].endswith('\n')
            lines = [g.choose(z.endswith('\n'),z[:-1],z) for z in lines]

            # Wrap the lines, decreasing the page width by indent.
            result = g.wrap_lines(lines,
                pageWidth-indents[1],
                pageWidth-indents[0])

            # prefix with the leading whitespace, if any
            paddedResult = []
            paddedResult.append(leading_ws[0] + result[0])
            for line in result[1:]:
                paddedResult.append(leading_ws[1] + line)

            # Convert the result to a string.
            result = '\n'.join(paddedResult)
            if trailingNL: result = result + '\n'
            #@nonl
            #@-node:ekr.20031218072017.1836:<< compute the result of wrapping all lines >>
            #@nl
            #@        << update the body, selection & undo state >>
            #@+node:ekr.20031218072017.1837:<< update the body, selection & undo state >>
            # This destroys recoloring.
            junk, ins = body.setSelectionAreas(head,result,tail)

            # Advance to the next paragraph.
            s = w.getAllText()
            ins += 1 # Move past the selection.
            while ins < len(s):
                i,j = g.getLine(s,ins)
                line = s[i:j]
                if line.startswith('@') or line.isspace():
                    ins = j+1
                else:
                    ins = i ; break

            changed = original != head + result + tail
            if changed:
                body.onBodyChanged(undoType,oldSel=oldSel,oldYview=oldYview)
            else:
                # We must always recolor, even if the text has not changed,
                # because setSelectionAreas above destroys the coloring.
                c.recolor()

            w.setSelectionRange(ins,ins,insert=ins)
            w.see(ins)
            #@-node:ekr.20031218072017.1837:<< update the body, selection & undo state >>
            #@nl
    #@nonl
    #@-node:ekr.20031218072017.1833:reformatParagraph
    #@+node:ekr.20031218072017.1838:updateBodyPane (handles changeNodeContents)
    def updateBodyPane (self,head,middle,tail,undoType,oldSel,oldYview):

        c = self ; body = c.frame.body ; p = c.currentPosition()

        # Update the text and notify the event handler.
        body.setSelectionAreas(head,middle,tail)

        # Expand the selection.
        head = head or ''
        middle = middle or ''
        tail = tail or ''
        i = len(head)
        j = max(i,len(head)+len(middle)-1)
        newSel = i,j
        body.setSelectionRange(newSel)

        # This handles the undo.
        body.onBodyChanged(undoType,oldSel=oldSel or newSel,oldYview=oldYview)

        # Update the changed mark and icon.
        c.setChanged(True)
        if p.isDirty():
            dirtyVnodeList = []
        else:
            dirtyVnodeList = p.setDirty()
        c.redraw()

        # Scroll as necessary.
        if oldYview:
            body.setYScrollPosition(oldYview)
        else:
            body.seeInsertPoint()

        body.setFocus()
        c.recolor()
        return dirtyVnodeList
    #@-node:ekr.20031218072017.1838:updateBodyPane (handles changeNodeContents)
    #@-node:ekr.20031218072017.2884:Edit Body submenu
    #@+node:ekr.20031218072017.2885:Edit Headline submenu
    #@+node:ekr.20031218072017.2886:c.editHeadline
    def editHeadline (self,event=None):

        '''Begin editing the headline of the selected node.'''

        c = self ; k = c.k ; tree = c.frame.tree

        if g.app.batchMode:
            c.notValidInBatchMode("Edit Headline")
            return

        if k:
            k.setDefaultInputState()
            k.showStateAndMode()

        tree.editLabel(c.currentPosition())
    #@-node:ekr.20031218072017.2886:c.editHeadline
    #@+node:ekr.20031218072017.2290:toggleAngleBrackets
    def toggleAngleBrackets (self,event=None):

        '''Add or remove double angle brackets from the headline of the selected node.'''

        c = self ; v = c.currentVnode()

        if g.app.batchMode:
            c.notValidInBatchMode("Toggle Angle Brackets")
            return

        c.endEditing()

        s = v.headString().strip()
        if (s[0:2] == "<<"
            or s[-2:] == ">>"): # Must be on separate line.
            if s[0:2] == "<<": s = s[2:]
            if s[-2:] == ">>": s = s[:-2]
            s = s.strip()
        else:
            s = g.angleBrackets(' ' + s + ' ')

        c.frame.tree.editLabel(v)
        w = c.edit_widget(v)
        if w:
            w.setAllText(s)
            c.frame.tree.onHeadChanged(v,'Toggle Angle Brackets')
    #@-node:ekr.20031218072017.2290:toggleAngleBrackets
    #@-node:ekr.20031218072017.2885:Edit Headline submenu
    #@+node:ekr.20031218072017.2887:Find submenu (frame methods)
    #@+node:ekr.20051013084200:dismissFindPanel
    def dismissFindPanel (self,event=None):

        c = self

        if c.frame.findPanel:
            c.frame.findPanel.dismiss()
    #@-node:ekr.20051013084200:dismissFindPanel
    #@+node:ekr.20031218072017.2888:showFindPanel
    def showFindPanel (self,event=None):

        '''Open Leo's legacy Find dialog.'''

        c = self

        if not c.frame.findPanel:
            c.frame.findPanel = g.app.gui.createFindPanel(c)

        if c.frame.findPanel:
            c.frame.findPanel.bringToFront()
        else:
            g.es('the',g.app.gui.guiName(),
                'gui does not support a stand-alone find dialog',color='blue')
    #@-node:ekr.20031218072017.2888:showFindPanel
    #@+node:ekr.20031218072017.2889:findNext
    def findNext (self,event=None):

        c = self

        if not c.frame.findPanel:
            c.frame.findPanel = g.app.gui.createFindPanel(c)

        c.frame.findPanel.findNextCommand(c)
    #@-node:ekr.20031218072017.2889:findNext
    #@+node:ekr.20031218072017.2890:findPrevious
    def findPrevious (self,event=None):

        c = self

        if not c.frame.findPanel:
            c.frame.findPanel = g.app.gui.createFindPanel(c)

        c.frame.findPanel.findPreviousCommand(c)
    #@-node:ekr.20031218072017.2890:findPrevious
    #@+node:ekr.20031218072017.2891:replace
    def replace (self,event=None):

        c = self

        if not c.frame.findPanel:
            c.frame.findPanel = g.app.gui.createFindPanel(c)

        c.frame.findPanel.changeCommand(c)
    #@-node:ekr.20031218072017.2891:replace
    #@+node:ekr.20031218072017.2892:replaceThenFind
    def replaceThenFind (self,event=None):

        c = self

        if not c.frame.findPanel:
            c.frame.findPanel = g.app.gui.createFindPanel(c)

        c.frame.findPanel.changeThenFindCommand(c)
    #@-node:ekr.20031218072017.2892:replaceThenFind
    #@+node:ekr.20051013083241:replaceAll
    def replaceAll (self,event=None):

        c = self

        if not c.frame.findPanel:
            c.frame.findPanel = g.app.gui.createFindPanel(c)

        c.frame.findPanel.changeAllCommand(c)
    #@-node:ekr.20051013083241:replaceAll
    #@-node:ekr.20031218072017.2887:Find submenu (frame methods)
    #@+node:ekr.20031218072017.2893:notValidInBatchMode
    def notValidInBatchMode(self, commandName):

        g.es('the',commandName,"command is not valid in batch mode")
    #@-node:ekr.20031218072017.2893:notValidInBatchMode
    #@-node:ekr.20031218072017.2861:Edit Menu...
    #@+node:ekr.20031218072017.2894:Outline menu...
    #@+node:ekr.20031218072017.2895: Top Level... (Commands)
    #@+node:ekr.20031218072017.1548:Cut & Paste Outlines
    #@+node:ekr.20031218072017.1549:cutOutline
    def cutOutline (self,event=None):

        '''Delete the selected outline and send it to the clipboard.'''

        c = self
        if c.canDeleteHeadline():
            c.copyOutline()
            c.deleteOutline("Cut Node")
            c.recolor()
    #@-node:ekr.20031218072017.1549:cutOutline
    #@+node:ekr.20031218072017.1550:copyOutline
    def copyOutline (self,event=None):

        '''Copy the selected outline to the clipboard.'''

        # Copying an outline has no undo consequences.
        c = self
        c.endEditing()
        s = c.fileCommands.putLeoOutline()
        # g.trace('type(s)',type(s))
        g.app.gui.replaceClipboardWith(s)
    #@-node:ekr.20031218072017.1550:copyOutline
    #@+node:ekr.20031218072017.1551:pasteOutline
    # To cut and paste between apps, just copy into an empty body first, then copy to Leo's clipboard.

    def pasteOutline(self,event=None,reassignIndices=True):

        '''Paste an outline into the present outline from the clipboard.
        Nodes do *not* retain their original identify.'''

        c = self ; u = c.undoer ; current = c.currentPosition()
        s = g.app.gui.getTextFromClipboard()
        pasteAsClone = not reassignIndices
        undoType = g.choose(reassignIndices,'Paste Node','Paste As Clone')

        c.endEditing()

        if not s or not c.canPasteOutline(s):
            return # This should never happen.

        isLeo = g.match(s,0,g.app.prolog_prefix_string)
        tnodeInfoDict = {}
        if pasteAsClone:
            #@        << remember all data for undo/redo Paste As Clone >>
            #@+node:ekr.20050418084539:<< remember all data for undo/redo Paste As Clone >>
            #@+at
            # 
            # We don't know yet which nodes will be affected by the paste, so 
            # we remember
            # everything. This is expensive, but foolproof.
            # 
            # The alternative is to try to remember the 'before' values of 
            # tnodes in the
            # fileCommands read logic. Several experiments failed, and the 
            # code is very ugly.
            # In short, it seems wise to do things the foolproof way.
            # 
            #@-at
            #@@c

            for v in c.all_unique_vnodes_iter():
                t = v.t
                if t not in tnodeInfoDict:
                    tnodeInfoDict[t] = g.Bunch(
                        t=t,head=v.headString(),body=v.bodyString())
            #@-node:ekr.20050418084539:<< remember all data for undo/redo Paste As Clone >>
            #@nl
        # create a *position* to be pasted.
        if isLeo:
            pasted = c.fileCommands.getLeoOutlineFromClipboard(s,reassignIndices)
        else:
            pasted = c.importCommands.convertMoreStringToOutlineAfter(s,current)
        if not pasted: return

        copiedBunchList = []
        if pasteAsClone:
            #@        << put only needed info in copiedBunchList >>
            #@+node:ekr.20050418084539.2:<< put only needed info in copiedBunchList >>
            # Create a dict containing only copied tnodes.
            copiedTnodeDict = {}
            for p in pasted.self_and_subtree_iter():
                if p.v.t not in copiedTnodeDict:
                    copiedTnodeDict[p.v.t] = p.v.t

            # g.trace(copiedTnodeDict.keys())

            for t in tnodeInfoDict:
                bunch = tnodeInfoDict.get(t)
                if copiedTnodeDict.get(t):
                    copiedBunchList.append(bunch)

            # g.trace('copiedBunchList',copiedBunchList)
            #@-node:ekr.20050418084539.2:<< put only needed info in copiedBunchList >>
            #@nl
        undoData = u.beforeInsertNode(current,
            pasteAsClone=pasteAsClone,copiedBunchList=copiedBunchList)
        c.endEditing()
        c.validateOutline()
        c.selectPosition(pasted)
        pasted.setDirty()
        c.setChanged(True)
        # paste as first child if back is expanded.
        back = pasted.back()
        if back and back.isExpanded():
            pasted.moveToNthChildOf(back,0)
        c.setRootPosition(c.findRootPosition(pasted)) # New in 4.4.2.
        u.afterInsertNode(pasted,undoType,undoData)
        c.redraw()
        c.recolor()
    #@-node:ekr.20031218072017.1551:pasteOutline
    #@+node:EKR.20040610130943:pasteOutlineRetainingClones
    def pasteOutlineRetainingClones (self,event=None):

        '''Paste an outline into the present outline from the clipboard.
        Nodes *retain* their original identify.'''

        c = self

        return c.pasteOutline(reassignIndices=False)
    #@-node:EKR.20040610130943:pasteOutlineRetainingClones
    #@-node:ekr.20031218072017.1548:Cut & Paste Outlines
    #@+node:ekr.20031218072017.2028:Hoist & dehoist
    def dehoist (self,event=None):

        '''Undo a previous hoist of an outline.'''

        c = self ; p = c.currentPosition()
        if p and c.canDehoist():
            bunch = c.hoistStack.pop()
            if bunch.expanded: p.expand()
            else:              p.contract()
            c.redraw()

            c.frame.clearStatusLine()
            if c.hoistStack:
                bunch = c.hoistStack[-1]
                c.frame.putStatusLine("Hoist: " + bunch.p.headString())
            else:
                c.frame.putStatusLine("No hoist")
            c.undoer.afterDehoist(p,'DeHoist')
            g.doHook('hoist-changed',c=c)

    def hoist (self,event=None):

        '''Make only the selected outline visible.'''

        c = self ; p = c.currentPosition()
        if p and c.canHoist():
            # Remember the expansion state.
            bunch = g.Bunch(p=p.copy(),expanded=p.isExpanded())
            c.hoistStack.append(bunch)
            p.expand()
            c.redraw()

            c.frame.clearStatusLine()
            c.frame.putStatusLine("Hoist: " + p.headString())
            c.undoer.afterHoist(p,'Hoist')
            g.doHook('hoist-changed',c=c)
    #@-node:ekr.20031218072017.2028:Hoist & dehoist
    #@+node:ekr.20031218072017.1759:Insert, Delete & Clone (Commands)
    #@+node:ekr.20031218072017.1760:c.checkMoveWithParentWithWarning & c.checkDrag
    #@+node:ekr.20070910105044:checkMoveWithParentWithWarning
    def checkMoveWithParentWithWarning (self,root,parent,warningFlag):

        """Return False if root or any of root's descedents is a clone of
        parent or any of parents ancestors."""

        message = "Illegal move or drag: no clone may contain a clone of itself"

        # g.trace("root",root,"parent",parent)
        clonedTnodes = {}
        for ancestor in parent.self_and_parents_iter():
            if ancestor.isCloned():
                t = ancestor.v.t
                clonedTnodes[t] = t

        if not clonedTnodes:
            return True

        for p in root.self_and_subtree_iter():
            if p.isCloned() and clonedTnodes.get(p.v.t):
                if g.app.unitTesting:
                    g.app.unitTestDict['checkMoveWithParentWithWarning']=True
                elif warningFlag:
                    g.alert(message)
                return False
        return True
    #@-node:ekr.20070910105044:checkMoveWithParentWithWarning
    #@+node:ekr.20070910105044.1:checkDrag
    def checkDrag (self,root,target):

        """Return False if target is any descendant of root."""

        message = "Can not drag a node into its descendant tree."

        # g.trace('root',root.headString(),'target',target.headString())

        for z in root.subtree_iter():
            if z == target:
                if g.app.unitTesting:
                    g.app.unitTestDict['checkMoveWithParentWithWarning']=True
                else:
                    g.alert(message)
                return False
        return True
    #@nonl
    #@-node:ekr.20070910105044.1:checkDrag
    #@-node:ekr.20031218072017.1760:c.checkMoveWithParentWithWarning & c.checkDrag
    #@+node:ekr.20031218072017.1193:c.deleteOutline
    def deleteOutline (self,event=None,op_name="Delete Node"):

        """Deletes the selected outline."""

        c = self ; cc = c.chapterController ; u = c.undoer
        p = c.currentPosition()
        if not p: return

        if p.hasVisBack(c): newNode = p.visBack(c)
        else: newNode = p.next() # _not_ p.visNext(): we are at the top level.
        if not newNode: return

        c.endEditing() # Make sure we capture the headline for Undo.

        if cc: # Special cases for @chapter and @chapters nodes.
            chapter = '@chapter ' ; chapters = '@chapters ' 
            h = p.headString()
            if h.startswith(chapters):
                if p.hasChildren():
                    return cc.error('Can not delete @chapters node with children.')
            elif h.startswith(chapter):
                name = h[len(chapter):].strip()
                if name:
                    return cc.removeChapterByName(name)

        undoData = u.beforeDeleteNode(p)
        dirtyVnodeList = p.setAllAncestorAtFileNodesDirty()
        p.doDelete(newNode)
        c.selectPosition(newNode)
        c.setChanged(True)
        u.afterDeleteNode(newNode,op_name,undoData,dirtyVnodeList=dirtyVnodeList)
        c.redraw()

        c.validateOutline()
    #@-node:ekr.20031218072017.1193:c.deleteOutline
    #@+node:ekr.20031218072017.1761:c.insertHeadline
    def insertHeadline (self,event=None,op_name="Insert Node",as_child=False):

        '''Insert a node after the presently selected node.'''

        c = self ; u = c.undoer
        current = c.currentPosition()

        if not current: return

        undoData = c.undoer.beforeInsertNode(current)
        # Make sure the new node is visible when hoisting.
        if (as_child or
            (current.hasChildren() and current.isExpanded()) or
            (c.hoistStack and current == c.hoistStack[-1].p)
        ):
            if c.config.getBool('insert_new_nodes_at_end'):
                p = current.insertAsLastChild()
            else:
                p = current.insertAsNthChild(0)
        else:
            p = current.insertAfter()
        dirtyVnodeList = p.setAllAncestorAtFileNodesDirty()
        c.selectPosition(p)
        c.setChanged(True)
        u.afterInsertNode(p,op_name,undoData,dirtyVnodeList=dirtyVnodeList)
        c.redraw()

        c.editPosition(p,selectAll=True)

        return p # for mod_labels plugin.
    #@-node:ekr.20031218072017.1761:c.insertHeadline
    #@+node:ekr.20071005173203.1:c.insertChild
    def insertChild (self,event=None):

        '''Insert a node after the presently selected node.'''

        c = self

        return c.insertHeadline(event=event,op_name='Insert Child',as_child=True)
    #@-node:ekr.20071005173203.1:c.insertChild
    #@+node:ekr.20031218072017.1762:c.clone
    def clone (self,event=None):

        '''Create a clone of the selected outline.'''

        c = self ; u = c.undoer ; p = c.currentPosition()
        if not p: return

        undoData = c.undoer.beforeCloneNode(p)
        clone = p.clone()
        dirtyVnodeList = clone.setAllAncestorAtFileNodesDirty()
        c.setChanged(True)
        if c.validateOutline():
            u.afterCloneNode(clone,'Clone Node',undoData,dirtyVnodeList=dirtyVnodeList)
            c.selectPosition(clone)
        c.redraw()

        return clone # For mod_labels and chapters plugins.
    #@-node:ekr.20031218072017.1762:c.clone
    #@+node:ekr.20031218072017.1765:c.validateOutline
    # Makes sure all nodes are valid.

    def validateOutline (self,event=None):

        c = self

        if not g.app.debug:
            return True

        root = c.rootPosition()
        parent = c.nullPosition()

        if root:
            return root.validateOutlineWithParent(parent)
        else:
            return True
    #@-node:ekr.20031218072017.1765:c.validateOutline
    #@-node:ekr.20031218072017.1759:Insert, Delete & Clone (Commands)
    #@+node:ekr.20080425060424.1:Sort...
    #@+node:ekr.20050415134809:c.sortChildren
    def sortChildren (self,event=None,cmp=None):

        '''Sort the children of a node.'''

        c = self ; p = c.currentPosition()

        if p and p.hasChildren():
            c.sortSiblings(p=p.firstChild(),sortChildren=True)
    #@-node:ekr.20050415134809:c.sortChildren
    #@+node:ekr.20050415134809.1:c.sortSiblings
    def sortSiblings (self,event=None,cmp=None,p=None,sortChildren=False):

        '''Sort the siblings of a node.'''

        c = self ; u = c.undoer
        if p is None: p = c.currentPosition()
        if not p: return

        undoType = g.choose(sortChildren,'Sort Children','Sort Siblings')
        parent_v = p._parentVnode()
        parent = p.parent()
        oldChildren = parent_v.t.children[:]
        newChildren = parent_v.t.children[:]

        def key (self):
            return (self.headString().lower(), self)

        if cmp: newChildren.sort(cmp,key=key)
        else:   newChildren.sort(key=key)

        # g.trace(g.listToString(newChildren))

        bunch = u.beforeSort(p,undoType,oldChildren,newChildren,sortChildren)
        parent_v.t.children = newChildren
        if parent:
            dirtyVnodeList = parent.setAllAncestorAtFileNodesDirty()
        else:
            dirtyVnodeList = []
        u.afterSort(p,bunch,dirtyVnodeList)

        # Sorting destroys position p, and possibly the root position.
        c.setPositionAfterSort(sortChildren)
        c.redraw()
    #@-node:ekr.20050415134809.1:c.sortSiblings
    #@+node:ekr.20080503055349.1:c.setPositionAfterSort
    def setPositionAfterSort (self,sortChildren):

        c = self
        p = c.currentPosition()
        p_v = p.v
        parent = p.parent()
        parent_v = p._parentVnode()

        if sortChildren:
            c.selectPosition(parent or c.rootPosition())
        else:
            if parent:
                p = parent.firstChild()
            else:
                p = leoNodes.position(parent_v.t.children[0])
            while p and p.v != p_v:
                p.moveToNext()
            c.selectPosition(p or parent)
    #@-node:ekr.20080503055349.1:c.setPositionAfterSort
    #@-node:ekr.20080425060424.1:Sort...
    #@-node:ekr.20031218072017.2895: Top Level... (Commands)
    #@+node:ekr.20040711135959.2:Check Outline submenu...
    #@+node:ekr.20031218072017.2072:c.checkOutline
    def checkOutline (self,event=None,verbose=True,unittest=False,full=True,root=None):

        """Report any possible clone errors in the outline.

        Remove any unused tnodeLists."""

        c = self ; count = 1 ; errors = 0
        isTkinter = g.app.gui and g.app.gui.guiName() == "tkinter"

        if full and not unittest:
            g.es("all tests enabled: this may take awhile",color="blue")

        if root: iter = root.self_and_subtree_iter
        else:    iter = c.allNodes_iter 

        for p in iter():  # c.allNodes_iter():
            try:
                count += 1
                #@            << remove unused tnodeList >>
                #@+node:ekr.20040313150633:<< remove unused tnodeList >>
                # Empty tnodeLists are not errors.
                v = p.v

                # New in 4.2: tnode list is in tnode.
                if hasattr(v.t,"tnodeList") and len(v.t.tnodeList) > 0 and not v.isAnyAtFileNode():
                    if 0:
                        s = "deleting tnodeList for " + repr(v)
                        g.es_print(s,color="blue")
                    delattr(v.t,"tnodeList")
                    v.t._p_changed = True
                #@-node:ekr.20040313150633:<< remove unused tnodeList >>
                #@nl
                if full: # Unit tests usually set this false.
                    #@                << do full tests >>
                    #@+node:ekr.20040323155951:<< do full tests >>
                    if not unittest:
                        if count % 1000 == 0:
                            g.es('','.',newline=False)
                        if count % 8000 == 0:
                            g.enl()

                    #@+others
                    #@+node:ekr.20040314035615:assert consistency of threadNext & threadBack links
                    threadBack = p.threadBack()
                    threadNext = p.threadNext()

                    if threadBack:
                        assert p == threadBack.threadNext(), "p==threadBack.threadNext"

                    if threadNext:
                        assert p == threadNext.threadBack(), "p==threadNext.threadBack"
                    #@-node:ekr.20040314035615:assert consistency of threadNext & threadBack links
                    #@+node:ekr.20040314035615.1:assert consistency of next and back links
                    back = p.back()
                    next = p.next()

                    if back:
                        assert p == back.next(), 'p!=back.next(),  back: %s back.next: %s' % (
                            back,back.next())

                    if next:
                        assert p == next.back(), 'p!=next.back, next: %s next.back: %s' % (
                            next,next.back())
                    #@-node:ekr.20040314035615.1:assert consistency of next and back links
                    #@+node:ekr.20040314035615.2:assert consistency of parent and child links
                    if p.hasParent():
                        n = p.childIndex()
                        assert p == p.parent().moveToNthChild(n), "p==parent.moveToNthChild"

                    for child in p.children_iter():
                        assert p == child.parent(), "p==child.parent"

                    if p.hasNext():
                        assert p.next().parent() == p.parent(), "next.parent==parent"

                    if p.hasBack():
                        assert p.back().parent() == p.parent(), "back.parent==parent"
                    #@-node:ekr.20040314035615.2:assert consistency of parent and child links
                    #@+node:ekr.20040323162707:assert that clones actually share subtrees
                    if p.isCloned() and p.hasChildren():
                        for z in p.v.t.vnodeList:
                            assert z.t == p.v.t
                    #@-node:ekr.20040323162707:assert that clones actually share subtrees
                    #@+node:ekr.20040314043623:assert consistency of vnodeList
                    vnodeList = p.v.t.vnodeList

                    for v in vnodeList:

                        try:
                            assert v.t == p.v.t
                        except AssertionError:
                            g.pr("p",p)
                            g.pr("v",v)
                            g.pr("p.v",p.v)
                            g.pr("v.t",v.t)
                            g.pr("p.v.t",p.v.t)
                            raise AssertionError("v.t == p.v.t")

                        if p.v.isCloned():
                            assert v.isCloned(), "v.isCloned"
                            assert len(vnodeList) > 1, "len(vnodeList) > 1"
                        else:
                            assert not v.isCloned(), "not v.isCloned"
                            assert len(vnodeList) == 1, "len(vnodeList) == 1"
                    #@-node:ekr.20040314043623:assert consistency of vnodeList
                    #@+node:ekr.20040731053740:assert that p.headString() matches p.edit_text.get
                    # Not a great test: it only tests visible nodes.
                    # This test may fail if a joined node is being editred.

                    if isTkinter:
                        t = c.edit_widget(p)
                        if t:
                            s = t.getAllText()
                            assert p.headString().strip() == s.strip(), "May fail if joined node is being edited"
                    #@-node:ekr.20040731053740:assert that p.headString() matches p.edit_text.get
                    #@+node:ekr.20080426051658.1:assert consistency of t.parent and t.children arrays
                    #@+at
                    # Every nodes gets visited, so we only check consistency
                    # between p and its parent, not between p and its 
                    # children.
                    # 
                    # In other words, this is a strong test.
                    #@-at
                    #@@c

                    parent_v = p._parentVnode()
                    n = p.childIndex()

                    assert parent_v.t.children[n] == p.v,'fail 1'

                    if not g.unified_nodes:

                        assert parent_v in p.v.parents,'fail 2: parent_v: %s\nparents: %s' % (
                            parent_v,g.listToString(p.v.parents))

                        for z in p.v.parents:
                            assert p.v in z.t.children,'fail 3'
                    #@-node:ekr.20080426051658.1:assert consistency of t.parent and t.children arrays
                    #@-others
                    #@-node:ekr.20040323155951:<< do full tests >>
                    #@nl
            except AssertionError:
                errors += 1
                #@            << give test failed message >>
                #@+node:ekr.20040314044652:<< give test failed message >>
                junk, value, junk = sys.exc_info()

                s = "test failed at position %s\n%s" % (repr(p),value)

                g.es_print(s,color="red")
                #@-node:ekr.20040314044652:<< give test failed message >>
                #@nl
        if verbose or not unittest:
            #@        << print summary message >>
            #@+node:ekr.20040314043900:<<print summary message >>
            if full:
                g.enl()

            if errors or verbose:
                color = g.choose(errors,'red','blue')
                g.es_print('',count,'nodes checked',errors,'errors',color=color)
            #@-node:ekr.20040314043900:<<print summary message >>
            #@nl
        return errors
    #@-node:ekr.20031218072017.2072:c.checkOutline
    #@+node:ekr.20040723094220:Check Outline commands & allies
    #@+node:ekr.20040723094220.1:checkAllPythonCode
    def checkAllPythonCode(self,event=None,unittest=False,ignoreAtIgnore=True):

        '''Check all nodes in the selected tree for syntax and tab errors.'''

        c = self ; count = 0 ; result = "ok"

        for p in c.all_positions_with_unique_tnodes_iter():

            count += 1
            if not unittest:
                #@            << print dots >>
                #@+node:ekr.20040723094220.2:<< print dots >>
                if count % 100 == 0:
                    g.es('','.',newline=False)

                if count % 2000 == 0:
                    g.enl()
                #@-node:ekr.20040723094220.2:<< print dots >>
                #@nl

            if g.scanForAtLanguage(c,p) == "python":
                if not g.scanForAtSettings(p) and (not ignoreAtIgnore or not g.scanForAtIgnore(c,p)):
                    try:
                        c.checkPythonNode(p,unittest)
                    except (SyntaxError,tokenize.TokenError,tabnanny.NannyNag):
                        result = "error" # Continue to check.
                    except:
                        import traceback ; traceback.print_exc()
                        return "surprise" # abort
                    if unittest and result != "ok":
                        g.pr("Syntax error in %s" % p.cleanHeadString())
                        return result # End the unit test: it has failed.

        if not unittest:
            g.es("check complete",color="blue")

        return result
    #@-node:ekr.20040723094220.1:checkAllPythonCode
    #@+node:ekr.20040723094220.3:checkPythonCode
    def checkPythonCode (self,event=None,unittest=False,ignoreAtIgnore=True,suppressErrors=False):

        '''Check the selected tree for syntax and tab errors.'''

        c = self ; count = 0 ; result = "ok"

        if not unittest:
            g.es("checking Python code   ")

        for p in c.currentPosition().self_and_subtree_iter():

            count += 1
            if not unittest:
                #@            << print dots >>
                #@+node:ekr.20040723094220.4:<< print dots >>
                if count % 100 == 0:
                    g.es('','.',newline=False)

                if count % 2000 == 0:
                    g.enl()
                #@-node:ekr.20040723094220.4:<< print dots >>
                #@nl

            if g.scanForAtLanguage(c,p) == "python":
                if not ignoreAtIgnore or not g.scanForAtIgnore(c,p):
                    try:
                        c.checkPythonNode(p,unittest,suppressErrors)
                    except (parser.ParserError,SyntaxError,tokenize.TokenError,tabnanny.NannyNag):
                        result = "error" # Continue to check.
                    except:
                        g.es("surprise in checkPythonNode")
                        g.es_exception()
                        return "surprise" # abort

        if not unittest:
            g.es("check complete",color="blue")

        # We _can_ return a result for unit tests because we aren't using doCommand.
        return result
    #@-node:ekr.20040723094220.3:checkPythonCode
    #@+node:ekr.20040723094220.5:checkPythonNode
    def checkPythonNode (self,p,unittest=False,suppressErrors=False):

        c = self

        h = p.headString()
        # We must call getScript so that we can ignore directives and section references.
        body = g.getScript(c,p.copy())
        if not body: return

        try:
            compiler.parse(body + '\n')
        except (parser.ParserError,SyntaxError):
            if not suppressErrors:
                s = "Syntax error in: %s" % h
                g.es_print(s,color="blue")
            if unittest: raise
            else:
                g.es_exception(full=False,color="black")
                c.setMarked(p)

        c.tabNannyNode(p,h,body,unittest,suppressErrors)
    #@-node:ekr.20040723094220.5:checkPythonNode
    #@+node:ekr.20040723094220.6:tabNannyNode
    # This code is based on tabnanny.check.

    def tabNannyNode (self,p,headline,body,unittest=False,suppressErrors=False):

        """Check indentation using tabnanny."""

        c = self

        try:
            # readline = g.readLinesGenerator(body).next
            readline = g.readLinesClass(body).next
            tabnanny.process_tokens(tokenize.generate_tokens(readline))
            return

        except parser.ParserError:
            junk, msg, junk = sys.exc_info()
            if not suppressErrors:
                g.es("ParserError in",headline,color="blue")
                g.es('',str(msg))

        except tokenize.TokenError:
            junk, msg, junk = sys.exc_info()
            if not suppressErrors:
                g.es("TokenError in",headline,color="blue")
                g.es('',str(msg))

        except tabnanny.NannyNag:
            junk, nag, junk = sys.exc_info()
            if not suppressErrors:
                badline = nag.get_lineno()
                line    = nag.get_line()
                message = nag.get_msg()
                g.es("indentation error in",headline,"line",badline,color="blue")
                g.es(message)
                line2 = repr(str(line))[1:-1]
                g.es("offending line:\n",line2)

        except Exception:
            g.trace("unexpected exception")
            g.es_exception()

        if unittest: raise
        else: c.setMarked(p)
    #@-node:ekr.20040723094220.6:tabNannyNode
    #@-node:ekr.20040723094220:Check Outline commands & allies
    #@+node:ekr.20040412060927:c.dumpOutline
    def dumpOutline (self,event=None):

        """ Dump all nodes in the outline."""

        c = self

        for p in c.allNodes_iter():
            p.dump()
    #@-node:ekr.20040412060927:c.dumpOutline
    #@+node:ekr.20040711135959.1:Pretty Print commands
    #@+node:ekr.20040712053025:prettyPrintAllPythonCode
    def prettyPrintAllPythonCode (self,event=None,dump=False):

        '''Reformat all Python code in the outline to make it look more beautiful.'''

        c = self ; pp = c.prettyPrinter(c)

        for p in c.all_positions_with_unique_tnodes_iter():

            # Unlike c.scanAllDirectives, scanForAtLanguage ignores @comment.
            if g.scanForAtLanguage(c,p) == "python":
                pp.prettyPrintNode(p,dump=dump)

        pp.endUndo()

    # For unit test of inverse commands dict.
    def beautifyAllPythonCode (self,event=None,dump=False):
        return self.prettyPrintAllPythonCode (event,dump)
    #@nonl
    #@-node:ekr.20040712053025:prettyPrintAllPythonCode
    #@+node:ekr.20040712053025.1:prettyPrintPythonCode
    def prettyPrintPythonCode (self,event=None,p=None,dump=False):

        '''Reformat all Python code in the selected tree to make it look more beautiful.'''

        c = self

        if p: root = p.copy()
        else: root = c.currentPosition()

        pp = c.prettyPrinter(c)

        for p in root.self_and_subtree_iter():

            # Unlike c.scanAllDirectives, scanForAtLanguage ignores @comment.
            if g.scanForAtLanguage(c,p) == "python":

                pp.prettyPrintNode(p,dump=dump)

        pp.endUndo()

    # For unit test of inverse commands dict.
    def beautifyPythonCode (self,event=None,dump=False):
        return self.prettyPrintPythonCode (event,dump)

    #@-node:ekr.20040712053025.1:prettyPrintPythonCode
    #@+node:ekr.20050729211526:prettyPrintPythonNode
    def prettyPrintPythonNode (self,p=None,dump=False):

        c = self

        if not p:
            p = c.currentPosition()

        pp = c.prettyPrinter(c)

        # Unlike c.scanAllDirectives, scanForAtLanguage ignores @comment.
        if g.scanForAtLanguage(c,p) == "python":
            pp.prettyPrintNode(p,dump=dump)

        pp.endUndo()
    #@-node:ekr.20050729211526:prettyPrintPythonNode
    #@+node:ekr.20071001075704:prettyPrintPythonTree
    def prettyPrintPythonTree (self,event=None,dump=False):

        '''Reformat all Python code in the outline to make it look more beautiful.'''

        c = self ; p = c.currentPosition() ; pp = c.prettyPrinter(c)

        for p in p.self_and_subtree_iter():

            # Unlike c.scanAllDirectives, scanForAtLanguage ignores @comment.
            if g.scanForAtLanguage(c,p) == "python":

                pp.prettyPrintNode(p,dump=dump)

        pp.endUndo()

    # For unit test of inverse commands dict.
    def beautifyPythonTree (self,event=None,dump=False):
        return self.prettyPrintPythonTree (event,dump)
    #@nonl
    #@-node:ekr.20071001075704:prettyPrintPythonTree
    #@+node:ekr.20040711135244.5:class prettyPrinter
    class prettyPrinter:

        #@    @+others
        #@+node:ekr.20040711135244.6:__init__
        def __init__ (self,c):

            self.array = []
                # List of strings comprising the line being accumulated.
                # Important: this list never crosses a line.
            self.bracketLevel = 0
            self.c = c
            self.changed = False
            self.dumping = False
            self.erow = self.ecol = 0 # The ending row/col of the token.
            self.lastName = None # The name of the previous token type.
            self.line = 0 # Same as self.srow
            self.lineParenLevel = 0
            self.lines = [] # List of lines.
            self.name = None
            self.p = c.currentPosition()
            self.parenLevel = 0
            self.prevName = None
            self.s = None # The string containing the line.
            self.squareBracketLevel = 0
            self.srow = self.scol = 0 # The starting row/col of the token.
            self.startline = True # True: the token starts a line.
            self.tracing = False
            #@    << define dispatch dict >>
            #@+node:ekr.20041021100850:<< define dispatch dict >>
            self.dispatchDict = {

                "comment":    self.doMultiLine,
                "dedent":     self.doDedent,
                "endmarker":  self.doEndMarker,
                "errortoken": self.doErrorToken,
                "indent":     self.doIndent,
                "name":       self.doName,
                "newline":    self.doNewline,
                "nl" :        self.doNewline,
                "number":     self.doNumber,
                "op":         self.doOp,
                "string":     self.doMultiLine,
            }
            #@-node:ekr.20041021100850:<< define dispatch dict >>
            #@nl
        #@-node:ekr.20040711135244.6:__init__
        #@+node:ekr.20040713093048:clear
        def clear (self):
            self.lines = []
        #@-node:ekr.20040713093048:clear
        #@+node:ekr.20040713064323:dumpLines
        def dumpLines (self,p,lines):

            encoding = g.app.tkEncoding

            g.pr('\n','-'*10,p.cleanHeadString())

            if 0:
                for line in lines:
                    line2 = g.toEncodedString(line,encoding,reportErrors=True)
                    g.pr(line2,newline=False) # Don't add a trailing newline!)
            else:
                for i in range(len(lines)):
                    line = lines[i]
                    line = g.toEncodedString(line,encoding,reportErrors=True)
                    g.pr("%3d" % i, repr(lines[i]))
        #@-node:ekr.20040713064323:dumpLines
        #@+node:ekr.20040711135244.7:dumpToken
        def dumpToken (self,token5tuple):

            t1,t2,t3,t4,t5 = token5tuple
            srow,scol = t3 ; erow,ecol = t4
            line = str(t5) # can fail
            name = token.tok_name[t1].lower()
            val = str(t2) # can fail

            startLine = self.line != srow
            if startLine:
                g.pr("----- line",srow,repr(line))
            self.line = srow

            g.pr("%10s (%2d,%2d) %-8s" % (name,scol,ecol,repr(val)))
        #@-node:ekr.20040711135244.7:dumpToken
        #@+node:ekr.20040713091855:endUndo
        def endUndo (self):

            c = self.c ; u = c.undoer ; undoType = 'Pretty Print'
            current = c.currentPosition()

            if self.changed:
                # Tag the end of the command.
                u.afterChangeGroup(current,undoType,dirtyVnodeList=self.dirtyVnodeList)
        #@-node:ekr.20040713091855:endUndo
        #@+node:ekr.20040711135244.8:get
        def get (self):

            if self.lastName != 'newline' and self.lines:
                # Strip the trailing whitespace from the last line.
                self.lines[-1] = self.lines[-1].rstrip()

            return self.lines
        #@-node:ekr.20040711135244.8:get
        #@+node:ekr.20040711135244.4:prettyPrintNode
        def prettyPrintNode(self,p,dump):

            c = self.c
            h = p.headString()
            s = p.bodyString()
            if not s: return

            readlines = g.readLinesClass(s).next

            try:
                self.clear()
                for token5tuple in tokenize.generate_tokens(readlines):
                    self.putToken(token5tuple)
                lines = self.get()

            except tokenize.TokenError:
                g.es("error pretty-printing",h,"not changed.",color="blue")
                return

            if dump:
                self.dumpLines(p,lines)
            else:
                self.replaceBody(p,lines)
        #@-node:ekr.20040711135244.4:prettyPrintNode
        #@+node:ekr.20040711135244.9:put
        def put (self,s,strip=True):

            """Put s to self.array, and strip trailing whitespace if strip is True."""

            if self.array and strip:
                prev = self.array[-1]
                if len(self.array) == 1:
                    if prev.rstrip():
                        # Stripping trailing whitespace doesn't strip leading whitespace.
                        self.array[-1] = prev.rstrip()
                else:
                    # The previous entry isn't leading whitespace, so we can strip whitespace.
                    self.array[-1] = prev.rstrip()

            self.array.append(s)
        #@-node:ekr.20040711135244.9:put
        #@+node:ekr.20041021104237:putArray
        def putArray (self):

            """Add the next text by joining all the strings is self.array"""

            self.lines.append(''.join(self.array))
            self.array = []
            self.lineParenLevel = 0
        #@-node:ekr.20041021104237:putArray
        #@+node:ekr.20040711135244.10:putNormalToken & allies
        def putNormalToken (self,token5tuple):

            t1,t2,t3,t4,t5 = token5tuple
            self.name = token.tok_name[t1].lower() # The token type
            self.val = t2  # the token string
            self.srow,self.scol = t3 # row & col where the token begins in the source.
            self.erow,self.ecol = t4 # row & col where the token ends in the source.
            self.s = t5 # The line containing the token.
            self.startLine = self.line != self.srow
            self.line = self.srow

            if self.startLine:
                self.doStartLine()

            f = self.dispatchDict.get(self.name,self.oops)
            self.trace()
            f()
            self.lastName = self.name
        #@+node:ekr.20041021102938:doEndMarker
        def doEndMarker (self):

            self.putArray()
        #@-node:ekr.20041021102938:doEndMarker
        #@+node:ekr.20041021102340.1:doErrorToken
        def doErrorToken (self):

            self.array.append(self.val)

            # This code is executed for versions of Python earlier than 2.4
            if self.val == '@':
                # Preserve whitespace after @.
                i = g.skip_ws(self.s,self.scol+1)
                ws = self.s[self.scol+1:i]
                if ws:
                    self.array.append(ws)
        #@-node:ekr.20041021102340.1:doErrorToken
        #@+node:ekr.20041021102340.2:doIndent & doDedent
        def doDedent (self):

            pass

        def doIndent (self):

            self.array.append(self.val)
        #@-node:ekr.20041021102340.2:doIndent & doDedent
        #@+node:ekr.20041021102340:doMultiLine (strings, etc).
        def doMultiLine (self):

            # Ensure a blank before comments not preceded entirely by whitespace.

            if self.val.startswith('#') and self.array:
                prev = self.array[-1]
                if prev and prev[-1] != ' ':
                    self.put(' ') 

            # These may span lines, so duplicate the end-of-line logic.
            lines = g.splitLines(self.val)
            for line in lines:
                self.array.append(line)
                if line and line[-1] == '\n':
                    self.putArray()

            # Add a blank after the string if there is something in the last line.
            if self.array:
                line = self.array[-1]
                if line.strip():
                    self.put(' ')

            # Suppress start-of-line logic.
            self.line = self.erow
        #@-node:ekr.20041021102340:doMultiLine (strings, etc).
        #@+node:ekr.20041021101911.5:doName
        def doName(self):

            # Ensure whitespace or start-of-line precedes the name.
            if self.array:
                last = self.array[-1]
                ch = last[-1]
                outer = self.parenLevel == 0 and self.squareBracketLevel == 0
                chars = '@ \t{([.'
                if not outer: chars += ',=<>*-+&|/'
                if ch not in chars:
                    self.array.append(' ')

            self.array.append("%s " % self.val)

            if self.prevName == "def": # A personal idiosyncracy.
                self.array.append(' ') # Retain the blank before '('.

            self.prevName = self.val
        #@-node:ekr.20041021101911.5:doName
        #@+node:ekr.20041021101911.3:doNewline
        def doNewline (self):

            # Remove trailing whitespace.
            # This never removes trailing whitespace from multi-line tokens.
            if self.array:
                self.array[-1] = self.array[-1].rstrip()

            self.array.append('\n')
            self.putArray()
        #@-node:ekr.20041021101911.3:doNewline
        #@+node:ekr.20041021101911.6:doNumber
        def doNumber (self):

            self.array.append(self.val)
        #@-node:ekr.20041021101911.6:doNumber
        #@+node:ekr.20040711135244.11:doOp
        def doOp (self):

            val = self.val
            outer = self.lineParenLevel <= 0 or (self.parenLevel == 0 and self.squareBracketLevel == 0)
            # New in Python 2.4: '@' is an operator, not an error token.
            if self.val == '@':
                self.array.append(self.val)
                # Preserve whitespace after @.
                i = g.skip_ws(self.s,self.scol+1)
                ws = self.s[self.scol+1:i]
                if ws: self.array.append(ws)
            elif val == '(':
                # Nothing added; strip leading blank before function calls but not before Python keywords.
                strip = self.lastName=='name' and not keyword.iskeyword(self.prevName)
                self.put('(',strip=strip)
                self.parenLevel += 1 ; self.lineParenLevel += 1
            elif val in ('=','==','+=','-=','!=','<=','>=','<','>','<>','*','**','+','&','|','/','//'):
                # Add leading and trailing blank in outer mode.
                s = g.choose(outer,' %s ','%s')
                self.put(s % val)
            elif val in ('^','~','{','['):
                # Add leading blank in outer mode.
                s = g.choose(outer,' %s','%s')
                self.put(s % val)
                if val == '[': self.squareBracketLevel += 1
            elif val in (',',':','}',']',')'):
                # Add trailing blank in outer mode.
                s = g.choose(outer,'%s ','%s')
                self.put(s % val)
                if val == ']': self.squareBracketLevel -= 1
                if val == ')':
                    self.parenLevel -= 1 ; self.lineParenLevel -= 1
            # ----- no difference between outer and inner modes ---
            elif val in (';','%'):
                # Add leading and trailing blank.
                self.put(' %s ' % val)
            elif val == '>>':
                # Add leading blank.
                self.put(' %s' % val)
            elif val == '<<':
                # Add trailing blank.
                self.put('%s ' % val)
            elif val in ('-'):
                # Could be binary or unary.  Or could be a hyphen in a section name.
                # Add preceding blank only for non-id's.
                if outer:
                    if self.array:
                        prev = self.array[-1].rstrip()
                        if prev and not g.isWordChar(prev[-1]):
                            self.put(' %s' % val)
                        else: self.put(val)
                    else: self.put(val) # Try to leave whitespace unchanged.
                else:
                    self.put(val)
            else:
                self.put(val)
        #@-node:ekr.20040711135244.11:doOp
        #@+node:ekr.20041021112219:doStartLine
        def doStartLine (self):

            before = self.s[0:self.scol]
            i = g.skip_ws(before,0)
            self.ws = self.s[0:i]

            if self.ws:
                self.array.append(self.ws)
        #@-node:ekr.20041021112219:doStartLine
        #@+node:ekr.20041021101911.1:oops
        def oops(self):

            g.pr("unknown PrettyPrinting code: %s" % (self.name))
        #@-node:ekr.20041021101911.1:oops
        #@+node:ekr.20041021101911.2:trace
        def trace(self):

            if self.tracing:

                g.trace("%10s: %s" % (
                    self.name,
                    repr(g.toEncodedString(self.val,"utf-8"))
                ))
        #@-node:ekr.20041021101911.2:trace
        #@-node:ekr.20040711135244.10:putNormalToken & allies
        #@+node:ekr.20040711135244.12:putToken
        def putToken (self,token5tuple):

            if self.dumping:
                self.dumpToken(token5tuple)
            else:
                self.putNormalToken(token5tuple)
        #@-node:ekr.20040711135244.12:putToken
        #@+node:ekr.20040713070356:replaceBody
        def replaceBody (self,p,lines):

            c = self.c ; u = c.undoer ; undoType = 'Pretty Print'
            sel = c.frame.body.getInsertPoint()
            oldBody = p.bodyString()
            body = ''.join(lines)

            if oldBody != body:
                if not self.changed:
                    # Start the group.
                    u.beforeChangeGroup(p,undoType)
                    self.changed = True
                    self.dirtyVnodeList = []
                undoData = u.beforeChangeNodeContents(p)
                c.setBodyString(p,body)
                dirtyVnodeList2 = p.setDirty()
                self.dirtyVnodeList.extend(dirtyVnodeList2)
                u.afterChangeNodeContents(p,undoType,undoData,dirtyVnodeList=self.dirtyVnodeList)
        #@-node:ekr.20040713070356:replaceBody
        #@-others
    #@-node:ekr.20040711135244.5:class prettyPrinter
    #@-node:ekr.20040711135959.1:Pretty Print commands
    #@-node:ekr.20040711135959.2:Check Outline submenu...
    #@+node:ekr.20031218072017.2898:Expand & Contract...
    #@+node:ekr.20031218072017.2899:Commands (outline menu)
    #@+node:ekr.20031218072017.2900:contractAllHeadlines
    def contractAllHeadlines (self,event=None):

        '''Contract all nodes in the outline.'''

        c = self

        for p in c.all_positions_with_unique_vnodes_iter():
            p.contract()
        # Select the topmost ancestor of the presently selected node.
        p = c.currentPosition()
        while p and p.hasParent():
            p.moveToParent()
        c.selectPosition(p)
        c.redraw()
        c.treeFocusHelper()

        c.expansionLevel = 1 # Reset expansion level.
    #@-node:ekr.20031218072017.2900:contractAllHeadlines
    #@+node:ekr.20080819075811.3:contractAllOtherNodes & helper
    def contractAllOtherNodes (self,event=None):

        '''Contract all nodes except those needed to make the
        presently selected node visible.'''

        c = self ; leaveOpen = c.currentPosition()

        for p in c.rootPosition().self_and_siblings_iter():
            c.contractIfNotCurrent(p,leaveOpen)

        c.redraw()

    #@+node:ekr.20080819075811.7:contractIfNotCurrent
    def contractIfNotCurrent(self,p,leaveOpen):

        c = self

        if p == leaveOpen or not p.isAncestorOf(leaveOpen):
            p.contract()

        for child in p.children_iter():
            if child != leaveOpen and child.isAncestorOf(leaveOpen):
                c.contractIfNotCurrent(child,leaveOpen)
            else:
                for p2 in child.self_and_subtree_iter():
                    p2.contract()
    #@-node:ekr.20080819075811.7:contractIfNotCurrent
    #@-node:ekr.20080819075811.3:contractAllOtherNodes & helper
    #@+node:ekr.20031218072017.2901:contractNode
    def contractNode (self,event=None):

        '''Contract the presently selected node.'''

        c = self ; p = c.currentPosition()

        # g.trace(p.headString())

        p.contract()
        c.redraw()
        c.treeFocusHelper()
    #@-node:ekr.20031218072017.2901:contractNode
    #@+node:ekr.20040930064232:contractNodeOrGoToParent
    def contractNodeOrGoToParent (self,event=None):

        """Simulate the left Arrow Key in folder of Windows Explorer."""

        c = self ; p = c.currentPosition()

        if p.hasChildren() and p.isExpanded():
            # g.trace('contract',p.headString())
            c.contractNode()
        elif p.hasParent() and p.parent().isVisible(c):
            # g.trace('goto parent',p.headString())
            c.goToParent()

        c.treeFocusHelper()
    #@nonl
    #@-node:ekr.20040930064232:contractNodeOrGoToParent
    #@+node:ekr.20031218072017.2902:contractParent
    def contractParent (self,event=None):

        '''Contract the parent of the presently selected node.'''

        c = self ; p = c.currentPosition()

        parent = p.parent()
        if not parent: return

        parent.contract()

        c.treeSelectHelper(parent)
    #@-node:ekr.20031218072017.2902:contractParent
    #@+node:ekr.20031218072017.2903:expandAllHeadlines
    def expandAllHeadlines (self,event=None):

        '''Expand all headlines.
        Warning: this can take a long time for large outlines.'''

        c = self

        p = c.rootPosition()
        while p:
            c.expandSubtree(p)
            p.moveToNext()
        c.selectVnode(c.rootPosition())
        c.redraw()
        c.treeFocusHelper()

        c.expansionLevel = 0 # Reset expansion level.
    #@-node:ekr.20031218072017.2903:expandAllHeadlines
    #@+node:ekr.20031218072017.2904:expandAllSubheads
    def expandAllSubheads (self,event=None):

        '''Expand all children of the presently selected node.'''

        c = self ; v = c.currentVnode()
        if not v: return

        child = v.firstChild()
        c.expandSubtree(v)
        while child:
            c.expandSubtree(child)
            child = child.next()
        c.selectVnode(v)
        c.redraw()
        c.treeFocusHelper()
    #@-node:ekr.20031218072017.2904:expandAllSubheads
    #@+node:ekr.20031218072017.2905:expandLevel1..9
    def expandLevel1 (self,event=None):
        '''Expand the outline to level 1'''
        self.expandToLevel(1)

    def expandLevel2 (self,event=None):
        '''Expand the outline to level 2'''
        self.expandToLevel(2)

    def expandLevel3 (self,event=None):
        '''Expand the outline to level 3'''
        self.expandToLevel(3)

    def expandLevel4 (self,event=None):
        '''Expand the outline to level 4'''
        self.expandToLevel(4)

    def expandLevel5 (self,event=None):
        '''Expand the outline to level 5'''
        self.expandToLevel(5)

    def expandLevel6 (self,event=None):
        '''Expand the outline to level 6'''
        self.expandToLevel(6)

    def expandLevel7 (self,event=None):
        '''Expand the outline to level 7'''
        self.expandToLevel(7)

    def expandLevel8 (self,event=None):
        '''Expand the outline to level 8'''
        self.expandToLevel(8)

    def expandLevel9 (self,event=None):
        '''Expand the outline to level 9'''
        self.expandToLevel(9)
    #@-node:ekr.20031218072017.2905:expandLevel1..9
    #@+node:ekr.20031218072017.2906:expandNextLevel
    def expandNextLevel (self,event=None):

        '''Increase the expansion level of the outline and
        Expand all nodes at that level or lower.'''

        c = self ; v = c.currentVnode()

        # Expansion levels are now local to a particular tree.
        if c.expansionNode != v:
            c.expansionLevel = 1
            c.expansionNode = v

        self.expandToLevel(c.expansionLevel + 1)
    #@-node:ekr.20031218072017.2906:expandNextLevel
    #@+node:ekr.20031218072017.2907:expandNode
    def expandNode (self,event=None):

        '''Expand the presently selected node.'''

        c = self ; v = c.currentVnode()

        v.expand()
        c.redraw()
        c.treeFocusHelper()
    #@-node:ekr.20031218072017.2907:expandNode
    #@+node:ekr.20040930064232.1:expandNodeAnd/OrGoToFirstChild
    def expandNodeAndGoToFirstChild (self,event=None):

        """If a node has children, expand it if needed and go to the first child."""

        c = self ; p = c.currentPosition()
        if not p.hasChildren():
            c.treeFocusHelper()
            return

        if not p.isExpanded():
            c.expandNode()
        c.selectVnode(p.firstChild())
        c.redraw()
        c.treeFocusHelper()

    def expandNodeOrGoToFirstChild (self,event=None):

        """Simulate the Right Arrow Key in folder of Windows Explorer."""

        c = self ; p = c.currentPosition()
        if p.hasChildren():
            if not p.isExpanded():
                c.expandNode()
            else:
                c.selectVnode(p.firstChild())
                c.redraw()
        c.treeFocusHelper()
    #@-node:ekr.20040930064232.1:expandNodeAnd/OrGoToFirstChild
    #@+node:ekr.20060928062431:expandOnlyAncestorsOfNode
    def expandOnlyAncestorsOfNode (self,event=None):

        '''Contract all nodes in the outline.'''

        c = self ; level = 1

        for p in c.all_positions_with_unique_vnodes_iter():
            p.contract()
        for p in c.currentPosition().parents_iter():
            p.expand()
            level += 1
        c.redraw()
        c.treeFocusHelper()

        c.expansionLevel = level # Reset expansion level.
    #@-node:ekr.20060928062431:expandOnlyAncestorsOfNode
    #@+node:ekr.20031218072017.2908:expandPrevLevel
    def expandPrevLevel (self,event=None):

        '''Decrease the expansion level of the outline and
        Expand all nodes at that level or lower.'''

        c = self ; v = c.currentVnode()

        # Expansion levels are now local to a particular tree.
        if c.expansionNode != v:
            c.expansionLevel = 1
            c.expansionNode = v

        self.expandToLevel(max(1,c.expansionLevel - 1))
    #@-node:ekr.20031218072017.2908:expandPrevLevel
    #@-node:ekr.20031218072017.2899:Commands (outline menu)
    #@+node:ekr.20031218072017.2909:Utilities
    #@+node:ekr.20031218072017.2910:contractSubtree
    def contractSubtree (self,p):

        for p in p.subtree_iter():
            p.contract()
    #@-node:ekr.20031218072017.2910:contractSubtree
    #@+node:ekr.20031218072017.2911:expandSubtree
    def expandSubtree (self,v):

        c = self
        last = v.lastNode()

        while v and v != last:
            v.expand()
            v = v.threadNext()
        c.redraw()
    #@-node:ekr.20031218072017.2911:expandSubtree
    #@+node:ekr.20031218072017.2912:expandToLevel (rewritten in 4.4)
    def expandToLevel (self,level):

        c = self
        current = c.currentPosition()
        n = current.level()
        for p in current.self_and_subtree_iter():
            if p.level() - n + 1 < level:
                p.expand()
            else:
                p.contract()
        c.expansionLevel = level
        c.expansionNode = c.currentPosition()
        c.redraw()
    #@-node:ekr.20031218072017.2912:expandToLevel (rewritten in 4.4)
    #@-node:ekr.20031218072017.2909:Utilities
    #@-node:ekr.20031218072017.2898:Expand & Contract...
    #@+node:ekr.20031218072017.2922:Mark...
    #@+node:ekr.20031218072017.2923:markChangedHeadlines
    def markChangedHeadlines (self,event=None):

        '''Mark all nodes that have been changed.'''

        c = self ; u = c.undoer ; undoType = 'Mark Changed'
        current = c.currentPosition()

        u.beforeChangeGroup(current,undoType)
        for p in c.all_positions_with_unique_vnodes_iter():
            if p.isDirty()and not p.isMarked():
                bunch = u.beforeMark(p,undoType)
                c.setMarked(p)
                c.setChanged(True)
                u.afterMark(p,undoType,bunch)
        u.afterChangeGroup(current,undoType)
        if not g.unitTesting:
            g.es("done",color="blue")
        c.redraw()
    #@-node:ekr.20031218072017.2923:markChangedHeadlines
    #@+node:ekr.20031218072017.2924:markChangedRoots
    def markChangedRoots (self,event=None):

        '''Mark all changed @root nodes.'''

        c = self ; u = c.undoer ; undoType = 'Mark Changed'
        current = c.currentPosition()

        u.beforeChangeGroup(current,undoType)
        for p in c.all_positions_with_unique_vnodes_iter():
            if p.isDirty()and not p.isMarked():
                s = p.bodyString()
                flag, i = g.is_special(s,0,"@root")
                if flag:
                    bunch = u.beforeMark(p,undoType)
                    c.setMarked(p)
                    c.setChanged(True)
                    u.afterMark(p,undoType,bunch)
        u.afterChangeGroup(current,undoType)
        if not g.unitTesting:
            g.es("done",color="blue")
        c.redraw()
    #@-node:ekr.20031218072017.2924:markChangedRoots
    #@+node:ekr.20031218072017.2925:markAllAtFileNodesDirty
    def markAllAtFileNodesDirty (self,event=None):

        '''Mark all @file nodes as changed.'''

        c = self ; p = c.rootPosition()

        while p:
            if p.isAtFileNode() and not p.isDirty():
                p.setDirty()
                c.setChanged(True)
                p.moveToNodeAfterTree()
            else:
                p.moveToThreadNext()
        c.redraw()
    #@-node:ekr.20031218072017.2925:markAllAtFileNodesDirty
    #@+node:ekr.20031218072017.2926:markAtFileNodesDirty
    def markAtFileNodesDirty (self,event=None):

        '''Mark all @file nodes in the selected tree as changed.'''

        c = self
        p = c.currentPosition()
        if not p: return

        after = p.nodeAfterTree()
        while p and p != after:
            if p.isAtFileNode() and not p.isDirty():
                p.setDirty()
                c.setChanged(True)
                p.moveToNodeAfterTree()
            else:
                p.moveToThreadNext()
        c.redraw()
    #@-node:ekr.20031218072017.2926:markAtFileNodesDirty
    #@+node:ekr.20031218072017.2927:markClones
    def markClones (self,event=None):

        '''Mark all clones of the selected node.'''

        c = self ; u = c.undoer ; undoType = 'Mark Clones'
        current = c.currentPosition()
        if not current or not current.isCloned():
            g.es('the current node is not a clone',color='blue')
            return

        u.beforeChangeGroup(current,undoType)
        dirtyVnodeList = []
        for p in c.all_positions_with_unique_vnodes_iter():
            if p.v.t == current.v.t:
                bunch = u.beforeMark(p,undoType)
                c.setMarked(p)
                c.setChanged(True)
                dirtyVnodeList2 = p.setDirty()
                dirtyVnodeList.extend(dirtyVnodeList2)
                u.afterMark(p,undoType,bunch)
        u.afterChangeGroup(current,undoType,dirtyVnodeList=dirtyVnodeList)
        c.redraw()
    #@-node:ekr.20031218072017.2927:markClones
    #@+node:ekr.20031218072017.2928:markHeadline & est
    def markHeadline (self,event=None):

        '''Toggle the mark of the selected node.'''

        c = self ; u = c.undoer ; p = c.currentPosition()
        if not p: return

        undoType = g.choose(p.isMarked(),'Unmark','Mark')
        bunch = u.beforeMark(p,undoType)
        if p.isMarked():
            c.clearMarked(p)
        else:
            c.setMarked(p)
        dirtyVnodeList = p.setDirty()
        c.setChanged(True)
        u.afterMark(p,undoType,bunch,dirtyVnodeList=dirtyVnodeList)
        c.redraw()
    #@-node:ekr.20031218072017.2928:markHeadline & est
    #@+node:ekr.20031218072017.2929:markSubheads
    def markSubheads (self,event=None):

        '''Mark all children of the selected node as changed.'''

        c = self ; u = c.undoer ; undoType = 'Mark Subheads'
        current = c.currentPosition()
        if not current: return

        u.beforeChangeGroup(current,undoType)
        dirtyVnodeList = []
        for p in current.children_iter():
            if not p.isMarked():
                bunch = u.beforeMark(p,undoType)
                c.setMarked(p)
                dirtyVnodeList2 = p.setDirty()
                dirtyVnodeList.extend(dirtyVnodeList2)
                c.setChanged(True)
                u.afterMark(p,undoType,bunch)
        u.afterChangeGroup(current,undoType,dirtyVnodeList=dirtyVnodeList)
        c.redraw()
    #@-node:ekr.20031218072017.2929:markSubheads
    #@+node:ekr.20031218072017.2930:unmarkAll
    def unmarkAll (self,event=None):

        '''Unmark all nodes in the entire outline.'''

        c = self ; u = c.undoer ; undoType = 'Unmark All'
        current = c.currentPosition()
        if not current: return

        u.beforeChangeGroup(current,undoType)
        changed = False
        for p in c.all_positions_with_unique_vnodes_iter():
            if p.isMarked():
                bunch = u.beforeMark(p,undoType)
                # c.clearMarked(p) # Very slow: calls a hook.
                p.v.clearMarked()
                p.v.t.setDirty()
                u.afterMark(p,undoType,bunch)
                changed = True
        dirtyVnodeList = [p.v for p in c.all_positions_with_unique_vnodes_iter() if p.v.isDirty()]
        if changed:
            g.doHook("clear-all-marks",c=c,p=p,v=p)
            c.setChanged(True)
        u.afterChangeGroup(current,undoType,dirtyVnodeList=dirtyVnodeList)
        c.redraw()
    #@-node:ekr.20031218072017.2930:unmarkAll
    #@-node:ekr.20031218072017.2922:Mark...
    #@+node:ekr.20031218072017.1766:Move... (Commands)
    #@+node:ekr.20070420092425:cantMoveMessage
    def cantMoveMessage (self):

        c = self ; h = c.rootPosition().headString()
        kind = g.choose(h.startswith('@chapter'),'chapter','hoist')
        g.es("can't move node out of",kind,color="blue")
    #@-node:ekr.20070420092425:cantMoveMessage
    #@+node:ekr.20031218072017.1767:demote
    def demote (self,event=None):

        '''Make all following siblings children of the selected node.'''

        c = self ; u = c.undoer
        p = c.currentPosition()
        if not p or not p.hasNext():
            c.treeFocusHelper() ; return

        # Make sure all the moves will be valid.
        next = p.next()
        while next:
            if not c.checkMoveWithParentWithWarning(next,p,True):
                c.treeFocusHelper() ; return
            next.moveToNext()

        c.endEditing()
        parent_v = p._parentVnode()
        n = p.childIndex()
        followingSibs = parent_v.t.children[n+1:]
        # g.trace('sibs2\n',g.listToString(followingSibs2))
        # Adjust the parent links of all moved nodes.
        parent_v._computeParentsOfChildren(children=followingSibs)
        # Remove the moved nodes from the parent's children.
        parent_v.t.children = parent_v.t.children[:n+1]
        # Add the moved nodes to p's children
        p.v.t.children.extend(followingSibs)
        p.expand()
        # Even if p is an @ignore node there is no need to mark the demoted children dirty.
        dirtyVnodeList = p.setAllAncestorAtFileNodesDirty()
        c.setChanged(True)
        u.afterDemote(p,followingSibs,dirtyVnodeList)
        c.selectPosition(p)  # Also sets rootPosition.
        c.redraw()
        c.treeFocusHelper()

        c.updateSyntaxColorer(p) # Moving can change syntax coloring.
    #@-node:ekr.20031218072017.1767:demote
    #@+node:ekr.20031218072017.1768:moveOutlineDown
    #@+at 
    #@nonl
    # Moving down is more tricky than moving up; we can't move p to be a child 
    # of itself.  An important optimization:  we don't have to call 
    # checkMoveWithParentWithWarning() if the parent of the moved node remains 
    # the same.
    #@-at
    #@@c

    def moveOutlineDown (self,event=None):

        '''Move the selected node down.'''

        c = self ; u = c.undoer ; p = c.currentPosition()
        if not p: return

        if not c.canMoveOutlineDown():
            if c.hoistStack: self.cantMoveMessage()
            c.treeFocusHelper()
            return

        inAtIgnoreRange = p.inAtIgnoreRange()
        parent = p.parent()
        next = p.visNext(c)

        while next and p.isAncestorOf(next):
            next = next.visNext(c)
        if not next:
            if c.hoistStack: self.cantMoveMessage()
            c.treeFocusHelper()
            return

        sparseMove = c.config.getBool('sparse_move_outline_left')
        c.endEditing()
        undoData = u.beforeMoveNode(p)
        #@    << Move p down & set moved if successful >>
        #@+node:ekr.20031218072017.1769:<< Move p down & set moved if successful >>
        if next.hasChildren() and next.isExpanded():
            # Attempt to move p to the first child of next.
            moved = c.checkMoveWithParentWithWarning(p,next,True)
            if moved:
                dirtyVnodeList = p.setAllAncestorAtFileNodesDirty()
                p.moveToNthChildOf(next,0)

        else:
            # Attempt to move p after next.
            moved = c.checkMoveWithParentWithWarning(p,next.parent(),True)
            if moved:
                dirtyVnodeList = p.setAllAncestorAtFileNodesDirty()
                p.moveAfter(next)

        if moved and sparseMove and parent and not parent.isAncestorOf(p):
            # New in Leo 4.4.2: contract the old parent if it is no longer the parent of p.
            parent.contract()
        #@-node:ekr.20031218072017.1769:<< Move p down & set moved if successful >>
        #@nl
        if moved:
            if inAtIgnoreRange and not p.inAtIgnoreRange():
                # The moved nodes have just become newly unignored.
                p.setDirty() # Mark descendent @thin nodes dirty.
            else: # No need to mark descendents dirty.
                dirtyVnodeList2 = p.setAllAncestorAtFileNodesDirty()
                dirtyVnodeList.extend(dirtyVnodeList2)
            c.setChanged(True)
            u.afterMoveNode(p,'Move Down',undoData,dirtyVnodeList)
        c.selectPosition(p) # Also sets rootPosition.
        c.redraw()
        c.treeFocusHelper()

        c.updateSyntaxColorer(p) # Moving can change syntax coloring.
    #@-node:ekr.20031218072017.1768:moveOutlineDown
    #@+node:ekr.20031218072017.1770:moveOutlineLeft
    def moveOutlineLeft (self,event=None):

        '''Move the selected node left if possible.'''

        c = self ; u = c.undoer ; p = c.currentPosition()
        if not p: return
        if not c.canMoveOutlineLeft():
            if c.hoistStack: self.cantMoveMessage()
            c.treeFocusHelper()
            return
        if not p.hasParent():
            c.treeFocusHelper()
            return

        inAtIgnoreRange = p.inAtIgnoreRange()
        parent = p.parent()
        sparseMove = c.config.getBool('sparse_move_outline_left')
        c.endEditing()
        undoData = u.beforeMoveNode(p)
        dirtyVnodeList = p.setAllAncestorAtFileNodesDirty()
        p.moveAfter(parent)
        if inAtIgnoreRange and not p.inAtIgnoreRange():
            # The moved nodes have just become newly unignored.
            p.setDirty() # Mark descendent @thin nodes dirty.
        else: # No need to mark descendents dirty.
            dirtyVnodeList2 = p.setAllAncestorAtFileNodesDirty()
            dirtyVnodeList.extend(dirtyVnodeList2)
        c.setChanged(True)
        u.afterMoveNode(p,'Move Left',undoData,dirtyVnodeList)
        if sparseMove: # New in Leo 4.4.2
            parent.contract()
        c.selectPosition(p) # Also sets rootPosition.
        c.redraw()
        c.treeFocusHelper()

        c.updateSyntaxColorer(p) # Moving can change syntax coloring.
    #@nonl
    #@-node:ekr.20031218072017.1770:moveOutlineLeft
    #@+node:ekr.20031218072017.1771:moveOutlineRight
    def moveOutlineRight (self,event=None):

        '''Move the selected node right if possible.'''

        c = self ; u = c.undoer ; p = c.currentPosition()
        if not p: return
        if not c.canMoveOutlineRight(): # 11/4/03: Support for hoist.
            if c.hoistStack: self.cantMoveMessage()
            c.treeFocusHelper()
            return

        back = p.back()
        if not back:
            c.treeFocusHelper()
            return

        if not c.checkMoveWithParentWithWarning(p,back,True):
            c.treeFocusHelper()
            return

        c.endEditing()
        undoData = u.beforeMoveNode(p)
        dirtyVnodeList = p.setAllAncestorAtFileNodesDirty()
        n = back.numberOfChildren()
        p.moveToNthChildOf(back,n)
        # g.trace(p,p.parent())
        # Moving an outline right can never bring it outside the range of @ignore.
        dirtyVnodeList2 = p.setAllAncestorAtFileNodesDirty()
        dirtyVnodeList.extend(dirtyVnodeList2)
        c.setChanged(True)
        u.afterMoveNode(p,'Move Right',undoData,dirtyVnodeList)
        c.selectPosition(p) # Also sets root position.
        c.redraw()
        c.treeFocusHelper()

        c.updateSyntaxColorer(p) # Moving can change syntax coloring.
    #@-node:ekr.20031218072017.1771:moveOutlineRight
    #@+node:ekr.20031218072017.1772:moveOutlineUp
    def moveOutlineUp (self,event=None):

        '''Move the selected node up if possible.'''

        c = self ; u = c.undoer ; p = c.currentPosition()
        if not p: return
        if not c.canMoveOutlineUp(): # Support for hoist.
            if c.hoistStack: self.cantMoveMessage()
            c.treeFocusHelper()
            return
        back = p.visBack(c)
        if not back: return
        inAtIgnoreRange = p.inAtIgnoreRange()
        back2 = back.visBack(c)

        sparseMove = c.config.getBool('sparse_move_outline_left')
        c.endEditing()
        undoData = u.beforeMoveNode(p)
        dirtyVnodeList = p.setAllAncestorAtFileNodesDirty()
        moved = False
        #@    << Move p up >>
        #@+node:ekr.20031218072017.1773:<< Move p up >>
        if 0:
            g.trace("visBack",back)
            g.trace("visBack2",back2)
            g.trace("back2.hasChildren",back2.hasChildren())
            g.trace("back2.isExpanded",back2.isExpanded())

        parent = p.parent()

        # For this special case we move p after back2.
        specialCase = back2 and p.v in back2.v.t.vnodeList

        if specialCase:
            # The move must be legal.
            moved = True
            back2.contract()
            p.moveAfter(back2)
        elif not back2:
            if c.hoistStack: # hoist or chapter.
                limit,limitIsVisible = c.visLimit()
                assert limit
                if limitIsVisible:
                    # canMoveOutlineUp should have caught this.
                    g.trace('can not happen. In hoist')
                else:
                    # g.trace('chapter first child')
                    moved = True
                    p.moveToFirstChildOf(limit)
            else:
                # p will be the new root node
                p.moveToRoot(oldRoot=c.rootPosition())
                moved = True
        elif back2.hasChildren() and back2.isExpanded():
            if c.checkMoveWithParentWithWarning(p,back2,True):
                moved = True
                p.moveToNthChildOf(back2,0)
        else:
            if c.checkMoveWithParentWithWarning(p,back2.parent(),True):
                moved = True
                p.moveAfter(back2)
        if moved and sparseMove and parent and not parent.isAncestorOf(p):
            # New in Leo 4.4.2: contract the old parent if it is no longer the parent of p.
            parent.contract()
        #@-node:ekr.20031218072017.1773:<< Move p up >>
        #@nl
        if moved:
            if inAtIgnoreRange and not p.inAtIgnoreRange():
                # The moved nodes have just become newly unignored.
                dirtyVnodeList2 = p.setDirty() # Mark descendent @thin nodes dirty.
            else: # No need to mark descendents dirty.
                dirtyVnodeList2 = p.setAllAncestorAtFileNodesDirty()
            dirtyVnodeList.extend(dirtyVnodeList2)
            c.setChanged(True)
            u.afterMoveNode(p,'Move Right',undoData,dirtyVnodeList)
        c.selectPosition(p) # Also sets root position.
        c.redraw()
        c.treeFocusHelper()

        c.updateSyntaxColorer(p) # Moving can change syntax coloring.
    #@-node:ekr.20031218072017.1772:moveOutlineUp
    #@+node:ekr.20031218072017.1774:promote
    def promote (self,event=None):

        '''Make all children of the selected nodes siblings of the selected node.'''

        c = self ; u = c.undoer ; p = c.currentPosition()
        command = 'Promote'
        if not p or not p.hasChildren():
            # c.treeWantsFocusNow()
            c.treeFocusHelper()
            return

        isAtIgnoreNode = p.isAtIgnoreNode()
        inAtIgnoreRange = p.inAtIgnoreRange()
        c.endEditing()
        parent_v = p._parentVnode()
        children = p.v.t.children
        # Add the children to parent_v's children.
        n = p.childIndex()+1
        z = parent_v.t.children[:]
        parent_v.t.children = z[:n]
        parent_v.t.children.extend(children)
        parent_v.t.children.extend(z[n:])
        # Remove v's children.
        p.v.t.children = []
        # Adjust the parent links of all moved nodes.
        parent_v._computeParentsOfChildren(children=children)
        c.setChanged(True)
        if not inAtIgnoreRange and isAtIgnoreNode:
            # The promoted nodes have just become newly unignored.
            dirtyVnodeList = p.setDirty() # Mark descendent @thin nodes dirty.
        else: # No need to mark descendents dirty.
            dirtyVnodeList = p.setAllAncestorAtFileNodesDirty()
        u.afterPromote(p,children,dirtyVnodeList)
        c.selectPosition(p)
        c.redraw()
        c.treeFocusHelper()

        c.updateSyntaxColorer(p) # Moving can change syntax coloring.
    #@-node:ekr.20031218072017.1774:promote
    #@+node:ekr.20071213185710:c.toggleSparseMove
    def toggleSparseMove (self,event=None):

        c = self ; p = c.currentPosition()
        tag = 'sparse_move_outline_left'

        sparseMove = not c.config.getBool(tag)
        c.config.set(p, tag, sparseMove)
        g.es(tag,'=',sparseMove,color='blue')
    #@-node:ekr.20071213185710:c.toggleSparseMove
    #@-node:ekr.20031218072017.1766:Move... (Commands)
    #@+node:ekr.20031218072017.2913:Goto
    #@+node:ekr.20031218072017.1628:goNextVisitedNode
    def goNextVisitedNode (self,event=None):

        '''Select the next visited node.'''

        c = self

        p = c.nodeHistory.goNext()

        if p:
            c.frame.tree.expandAllAncestors(p)
            c.selectPosition(p)
            c.redraw_now()
    #@-node:ekr.20031218072017.1628:goNextVisitedNode
    #@+node:ekr.20031218072017.1627:goPrevVisitedNode
    def goPrevVisitedNode (self,event=None):

        '''Select the previously visited node.'''

        c = self

        p = c.nodeHistory.goPrev()

        if p:
            c.frame.tree.expandAllAncestors(p)
            c.selectPosition(p)
            c.redraw_now()
    #@-node:ekr.20031218072017.1627:goPrevVisitedNode
    #@+node:ekr.20031218072017.2914:goToFirstNode
    def goToFirstNode (self,event=None):

        '''Select the first node of the entire outline.'''

        c = self ; p = c.rootPosition()

        c.treeSelectHelper(p)
    #@-node:ekr.20031218072017.2914:goToFirstNode
    #@+node:ekr.20051012092453:goToFirstSibling
    def goToFirstSibling (self,event=None):

        '''Select the first sibling of the selected node.'''

        c = self ; p = c.currentPosition()

        if p.hasBack():
            while p.hasBack():
                p.moveToBack()

        c.treeSelectHelper(p)
    #@-node:ekr.20051012092453:goToFirstSibling
    #@+node:ekr.20070615070925:goToFirstVisibleNode
    def goToFirstVisibleNode (self,event=None):

        '''Select the first visible node of the selected chapter or hoist.'''

        c = self

        p = c.firstVisible()
        if p:
            c.selectPosition(p)

        c.treeSelectHelper(p)
    #@-node:ekr.20070615070925:goToFirstVisibleNode
    #@+node:ekr.20031218072017.2915:goToLastNode
    def goToLastNode (self,event=None):

        '''Select the last node in the entire tree.'''

        c = self ; p = c.rootPosition()
        while p and p.hasThreadNext():
            p.moveToThreadNext()

        c.treeSelectHelper(p)
    #@-node:ekr.20031218072017.2915:goToLastNode
    #@+node:ekr.20051012092847.1:goToLastSibling
    def goToLastSibling (self,event=None):

        '''Select the last sibling of the selected node.'''

        c = self ; p = c.currentPosition()

        if p.hasNext():
            while p.hasNext():
                p.moveToNext()

        c.treeSelectHelper(p)
    #@-node:ekr.20051012092847.1:goToLastSibling
    #@+node:ekr.20050711153537:c.goToLastVisibleNode
    def goToLastVisibleNode (self,event=None):

        '''Select the last visible node of selected chapter or hoist.'''

        c = self

        p = c.lastVisible()
        if p:
            c.selectPosition(p)

        c.treeSelectHelper(p)
    #@-node:ekr.20050711153537:c.goToLastVisibleNode
    #@+node:ekr.20031218072017.2916:goToNextClone
    def goToNextClone (self,event=None):

        '''Select the next node that is a clone of the selected node.'''

        c = self ; cc = c.chapterController ; p = c.currentPosition()
        if not p: return
        if not p.isCloned():
            g.es('not a clone:',p.headString(),color='blue')
            return

        t = p.v.t
        p.moveToThreadNext()
        wrapped = False
        while 1:
            if p and p.v.t == t:
                break
            elif p:
                p.moveToThreadNext()
            elif wrapped:
                break
            else:
                wrapped = True
                p = c.rootPosition()

        if not p: g.es("done",color="blue")

        if cc:
            name = cc.findChapterNameForPosition(p)
            cc.selectChapterByName(name)
            c.frame.tree.expandAllAncestors(p)

        c.selectPosition(p)
        c.redraw()
    #@-node:ekr.20031218072017.2916:goToNextClone
    #@+node:ekr.20071213123942:findNextClone
    def findNextClone (self,event=None):

        '''Select the next cloned node.'''

        c = self ; p = c.currentPosition() ; flag = False
        if not p: return

        if p.isCloned():
            p.moveToThreadNext()

        while p:
            if p.isCloned():
                flag = True ; break
            else:
                p.moveToThreadNext()

        if flag:
            cc = c.chapterController
            if cc:
                name = cc.findChapterNameForPosition(p)
                cc.selectChapterByName(name)
            c.frame.tree.expandAllAncestors(p)
            c.selectPosition(p)
            c.redraw()
        else:
            g.es('no more clones',color='blue')
    #@-node:ekr.20071213123942:findNextClone
    #@+node:ekr.20031218072017.2917:goToNextDirtyHeadline
    def goToNextDirtyHeadline (self,event=None):

        '''Select the node that is marked as changed.'''

        c = self ; p = c.currentPosition()
        if not p: return

        p.moveToThreadNext()
        wrapped = False
        while 1:
            if p and p.isDirty():
                break
            elif p:
                p.moveToThreadNext()
            elif wrapped:
                break
            else:
                wrapped = True
                p = c.rootPosition()

        if not p: g.es("done",color="blue")
        c.treeSelectHelper(p) # Sets focus.
    #@-node:ekr.20031218072017.2917:goToNextDirtyHeadline
    #@+node:ekr.20031218072017.2918:goToNextMarkedHeadline
    def goToNextMarkedHeadline (self,event=None):

        '''Select the next marked node.'''

        c = self ; p = c.currentPosition()
        if not p: return

        p.moveToThreadNext()
        wrapped = False
        while 1:
            if p and p.isMarked():
                break
            elif p:
                p.moveToThreadNext()
            elif wrapped:
                break
            else:
                wrapped = True
                p = c.rootPosition()

        if not p: g.es("done",color="blue")
        c.treeSelectHelper(p) # Sets focus.
    #@-node:ekr.20031218072017.2918:goToNextMarkedHeadline
    #@+node:ekr.20031218072017.2919:goToNextSibling
    def goToNextSibling (self,event=None):

        '''Select the next sibling of the selected node.'''

        c = self ; p = c.currentPosition()

        c.treeSelectHelper(p and p.next())
    #@-node:ekr.20031218072017.2919:goToNextSibling
    #@+node:ekr.20031218072017.2920:goToParent
    def goToParent (self,event=None):

        '''Select the parent of the selected node.'''

        c = self ; p = c.currentPosition()

        c.treeSelectHelper(p and p.parent())
    #@-node:ekr.20031218072017.2920:goToParent
    #@+node:ekr.20031218072017.2921:goToPrevSibling
    def goToPrevSibling (self,event=None):

        '''Select the previous sibling of the selected node.'''

        c = self ; p = c.currentPosition()

        c.treeSelectHelper(p and p.back())
    #@-node:ekr.20031218072017.2921:goToPrevSibling
    #@+node:ekr.20031218072017.2993:selectThreadBack
    def selectThreadBack (self,event=None):

        '''Select the node preceding the selected node in outline order.'''

        c = self ; p = c.currentPosition()
        if not p: return

        p.moveToThreadBack()

        c.treeSelectHelper(p)
    #@-node:ekr.20031218072017.2993:selectThreadBack
    #@+node:ekr.20031218072017.2994:selectThreadNext
    def selectThreadNext (self,event=None):

        '''Select the node following the selected node in outline order.'''

        c = self ; p = c.currentPosition()
        if not p: return

        p.moveToThreadNext()

        c.treeSelectHelper(p)
    #@nonl
    #@-node:ekr.20031218072017.2994:selectThreadNext
    #@+node:ekr.20031218072017.2995:selectVisBack
    # This has an up arrow for a control key.

    def selectVisBack (self,event=None):

        '''Select the visible node preceding the presently selected node.'''

        c = self ; p = c.currentPosition()
        if not p: return
        if not c.canSelectVisBack(): return

        p.moveToVisBack(c)

        if p:
            redraw = not p.isVisible(c)
            if not redraw: c.frame.tree.setSelectedLabelState(c.currentPosition())
        else:
            redraw = True

        c.treeSelectHelper(p,redraw=redraw)
    #@-node:ekr.20031218072017.2995:selectVisBack
    #@+node:ekr.20031218072017.2996:selectVisNext
    def selectVisNext (self,event=None):

        '''Select the visible node following the presently selected node.'''

        c = self ; p = c.currentPosition()
        if not p: return
        if not c.canSelectVisNext(): return

        p.moveToVisNext(c)

        if p:
            redraw = not p.isVisible(c)
            if not redraw: c.frame.tree.setSelectedLabelState(c.currentPosition())
        else:
            redraw = True

        c.treeSelectHelper(p,redraw=redraw)
    #@-node:ekr.20031218072017.2996:selectVisNext
    #@+node:ekr.20070417112650:utils
    #@+node:ekr.20070226121510: treeFocusHelper
    def treeFocusHelper (self):

        c = self

        if c.config.getBool('stayInTreeAfterSelect'):
            c.treeWantsFocusNow()
        else:
            c.bodyWantsFocusNow()
    #@-node:ekr.20070226121510: treeFocusHelper
    #@+node:ekr.20070226113916: treeSelectHelper
    def treeSelectHelper (self,p,redraw=True):

        c = self ; current = c.currentPosition()

        if p:
            c.frame.tree.expandAllAncestors(p)
            c.selectPosition(p)
            if redraw: c.redraw()

        c.treeFocusHelper()
    #@-node:ekr.20070226113916: treeSelectHelper
    #@-node:ekr.20070417112650:utils
    #@-node:ekr.20031218072017.2913:Goto
    #@-node:ekr.20031218072017.2894:Outline menu...
    #@+node:ekr.20031218072017.2931:Window Menu
    #@+node:ekr.20031218072017.2092:openCompareWindow
    def openCompareWindow (self,event=None):

        '''Open a dialog for comparing files and directories.'''

        c = self ; frame = c.frame

        if not frame.comparePanel:
            frame.comparePanel = g.app.gui.createComparePanel(c)

        if frame.comparePanel:
            frame.comparePanel.bringToFront()
        else:
            g.es('the',g.app.gui.guiName(),
                'gui does not support the compare window',color='blue')
    #@-node:ekr.20031218072017.2092:openCompareWindow
    #@+node:ekr.20031218072017.2932:openPythonWindow
    def openPythonWindow (self,event=None):

        '''Open Python's Idle debugger in a separate process.'''

        pythonDir = g.os_path_dirname(sys.executable)
        idle = g.os_path_join(pythonDir,'Lib','idlelib','idle.py')
        args = [sys.executable, idle ]

        if 1: # Use present environment.
            os.spawnv(os.P_NOWAIT, sys.executable, args)
        else: # Use a pristine environment.
            os.spawnve(os.P_NOWAIT, sys.executable, args, os.environ)
    #@-node:ekr.20031218072017.2932:openPythonWindow
    #@-node:ekr.20031218072017.2931:Window Menu
    #@+node:ekr.20031218072017.2938:Help Menu
    #@+node:ekr.20031218072017.2939:about (version number & date)
    def about (self,event=None):

        '''Bring up an About Leo Dialog.'''

        c = self

        # Don't use triple-quoted strings or continued strings here.
        # Doing so would add unwanted leading tabs.
        version = c.getSignOnLine() + "\n\n"
        theCopyright = (
            "Copyright 1999-2007 by Edward K. Ream\n" +
            "All Rights Reserved\n" +
            "Leo is distributed under the Python License")
        url = "http://webpages.charter.net/edreamleo/front.html"
        email = "edreamleo@charter.net"

        g.app.gui.runAboutLeoDialog(c,version,theCopyright,url,email)
    #@-node:ekr.20031218072017.2939:about (version number & date)
    #@+node:ekr.20031218072017.2943:openLeoSettings and openMyLeoSettings
    def openLeoSettings (self,event=None):
        '''Open leoSettings.leo in a new Leo window.'''
        self.openSettingsHelper('leoSettings.leo')

    def openMyLeoSettings (self,event=None):
        '''Open myLeoSettings.leo in a new Leo window.'''
        self.openSettingsHelper('myLeoSettings.leo')

    def openSettingsHelper(self,name):
        c = self
        homeLeoDir = g.app.homeLeoDir # was homeDir
        loadDir = g.app.loadDir
        configDir = g.app.globalConfigDir

        # Look in configDir first.
        fileName = g.os_path_join(configDir,name)
        ok = g.os_path_exists(fileName)
        if ok:
            ok, frame = g.openWithFileName(fileName,c)
            if ok: return

        # Look in homeLeoDir second.
        if configDir == loadDir:
            g.es('',name,"not found in",configDir)
        else:
            fileName = g.os_path_join(homeLeoDir,name)
            ok = g.os_path_exists(fileName)
            if ok:
                ok, frame = g.openWithFileName(fileName,c)
            if not ok:
                g.es('',name,"not found in",configDir,"\nor",homeLeoDir)
    #@-node:ekr.20031218072017.2943:openLeoSettings and openMyLeoSettings
    #@+node:ekr.20061018094539:openLeoScripts
    def openLeoScripts (self,event=None):

        c = self
        fileName = g.os_path_join(g.app.loadDir,'..','scripts','scripts.leo')

        ok, frame = g.openWithFileName(fileName,c)
        if not ok:
            g.es('not found:',fileName)
    #@-node:ekr.20061018094539:openLeoScripts
    #@+node:ekr.20031218072017.2940:leoDocumentation
    def leoDocumentation (self,event=None):

        '''Open LeoDocs.leo in a new Leo window.'''

        c = self ; name = "LeoDocs.leo"

        fileName = g.os_path_join(g.app.loadDir,"..","doc",name)
        ok,frame = g.openWithFileName(fileName,c)
        if not ok:
            g.es("not found:",name)
    #@-node:ekr.20031218072017.2940:leoDocumentation
    #@+node:ekr.20031218072017.2941:leoHome
    def leoHome (self,event=None):

        '''Open Leo's Home page in a web browser.'''

        import webbrowser

        url = "http://webpages.charter.net/edreamleo/front.html"
        try:
            webbrowser.open_new(url)
        except:
            g.es("not found:",url)
    #@-node:ekr.20031218072017.2941:leoHome
    #@+node:ekr.20050130152008:leoPlugins
    def openLeoPlugins (self,event=None):

        '''Open leoPlugins.leo in a new Leo window.'''

        names =  ('leoPlugins.leo','leoPluginsRef.leo')

        c = self ; name = "leoPlugins.leo"

        for name in names:
            fileName = g.os_path_join(g.app.loadDir,"..","plugins",name)
            ok,frame = g.openWithFileName(fileName,c)
            if ok: return

        g.es('not found:', ', '.join(names))
    #@-node:ekr.20050130152008:leoPlugins
    #@+node:ekr.20031218072017.2942:leoTutorial (version number)
    def leoTutorial (self,event=None):

        '''Open Leo's online tutorial in a web browser.'''

        import webbrowser

        if 1: # new url
            url = "http://www.3dtree.com/ev/e/sbooks/leo/sbframetoc_ie.htm"
        else:
            url = "http://www.evisa.com/e/sbooks/leo/sbframetoc_ie.htm"
        try:
            webbrowser.open_new(url)
        except:
            g.es("not found:",url)
    #@-node:ekr.20031218072017.2942:leoTutorial (version number)
    #@+node:ekr.20060613082924:leoUsersGuide
    def leoUsersGuide (self,event=None):

        '''Open Leo's users guide in a web browser.'''

        import webbrowser

        c = self

        theFile = c.os_path_finalize_join(
            g.app.loadDir,'..','doc','html','leo_TOC.html')

        url = 'file:%s' % theFile

        try:
            webbrowser.open_new(url)
        except:
            g.es("not found:",url)
    #@-node:ekr.20060613082924:leoUsersGuide
    #@-node:ekr.20031218072017.2938:Help Menu
    #@-node:ekr.20031218072017.2818:Command handlers...
    #@+node:ekr.20080901124540.1:c.Directive scanning
    # These are all new in Leo 4.5.1.
    #@nonl
    #@+node:ekr.20080827175609.39:c.scanAllDirectives
    def scanAllDirectives(self,p=None):

        '''Scan p and ancestors for directives.

        Returns a dict containing the results, including defaults.'''

        c = self ; p = p or c.currentPosition()

        # Set defaults
        language = c.target_language and c.target_language.lower()
        lang_dict = {
            'language':language,
            'delims':g.set_delims_from_language(language),
        }
        wrap = c.config.getBool("body_pane_wraps")

        table = (
            ('encoding',    None,           g.scanAtEncodingDirectives),
            ('lang-dict',   lang_dict,      g.scanAtCommentAndAtLanguageDirectives),
            ('lineending',  None,           g.scanAtLineendingDirectives),
            ('pagewidth',   c.page_width,   g.scanAtPagewidthDirectives),
            ('path',        None,           c.scanAtPathDirectives),
            ('tabwidth',    c.tab_width,    g.scanAtTabwidthDirectives),
            ('wrap',        wrap,           g.scanAtWrapDirectives),
        )

        # Set d by scanning all directives.
        aList = g.get_directives_dict_list(p)
        d = {}
        for key,default,func in table:
            val = func(aList)
            d[key] = g.choose(val is None,default,val)

        # Post process: do *not* set commander ivars.
        lang_dict = d.get('lang-dict')

        return {
            "delims"        : lang_dict.get('delims'),
            "encoding"      : d.get('encoding'),
            "language"      : lang_dict.get('language'),
            "lineending"    : d.get('lineending'),
            "pagewidth"     : d.get('pagewidth'),
            "path"          : d.get('path') or g.getBaseDirectory(c),
            "tabwidth"      : d.get('tabwidth'),
            "pluginsList"   : [], # No longer used.
            "wrap"          : d.get('wrap'),
        }
    #@nonl
    #@-node:ekr.20080827175609.39:c.scanAllDirectives
    #@+node:ekr.20080828103146.15:c.scanAtPathDirectives

    def scanAtPathDirectives(self,aList,force=False):

        '''Scan aList for @path directives.'''

        c = self ; trace = False ; verbose = False

        # Step 1: Compute the starting path.
        # The correct fallback directory is the absolute path to the base.
        if c.openDirectory:  # Bug fix: 2008/9/18
            base = c.openDirectory
        else:
            base = g.app.config.relative_path_base_directory
            if base and base == "!":    base = g.app.loadDir
            elif base and base == ".":  base = c.openDirectory

        if trace and verbose: g.trace('base',base,'loadDir',g.app.loadDir)

        absbase = c.os_path_finalize_join(g.app.loadDir,base)

        if trace and verbose: g.trace('absbase',absbase)

        # Step 2: look for @path directives.
        paths = [] ; fileName = None
        for d in aList:
            # Look for @path directives.
            path = d.get('path')
            if path:
                # Convert "path" or <path> to path.
                path = g.computeRelativePath(path)
                if path: paths.append(path)

        # Add absbase and reverse the list.
        paths.append(absbase)
        paths.reverse()

        if trace and verbose: g.trace('paths',paths)

        # Step 3: Compute the full, effective, absolute path.
        if trace and verbose: g.printList(paths,tag='c.scanAtPathDirectives: raw paths')
        path = c.os_path_finalize_join(*paths)
        if trace and verbose: g.trace('joined path:',path)

        # Step 4: Make the path if necessary.
        if path and not g.os_path_exists(path):
            ok = g.makeAllNonExistentDirectories(path,c=c,force=force)
            if not ok:
                if force:
                    g.es_print('c.scanAtPathDirectives: invalid @path: %s' % (path),color='red')
                path = absbase # Bug fix: 2008/9/18

        if trace: g.trace('returns',path)

        return path
    #@-node:ekr.20080828103146.15:c.scanAtPathDirectives
    #@+node:ekr.20080828103146.12:c.scanAtRootDirectives
    # Called only by scanColorDirectives.

    def scanAtRootDirectives(self,aList):

        '''Scan aList for @root-code and @root-doc directives.'''

        c = self

        # To keep pylint happy.
        tag = 'at_root_bodies_start_in_doc_mode'
        start_in_doc = hasattr(c.config,tag) and getattr(c.config,tag)

        # New in Leo 4.6: dashes are valid in directive names.
        for d in aList:
            if 'root-code' in d:
                return 'code'
            elif 'root-doc' in d:
                return 'doc'
            elif 'root' in d:
                return g.choose(start_in_doc,'doc','code')

        return None
    #@-node:ekr.20080828103146.12:c.scanAtRootDirectives
    #@+node:ekr.20080922124033.5:c.os_path_finalize and c.os_path_finalize_join
    def os_path_finalize (self,path,**keys):

        c = self

        keys['c'] = c

        return g.os_path_finalize(path,**keys)

    def os_path_finalize_join (self,*args,**keys):

        c = self

        keys['c'] = c

        return g.os_path_finalize_join(*args,**keys)
    #@-node:ekr.20080922124033.5:c.os_path_finalize and c.os_path_finalize_join
    #@+node:ekr.20081006100835.1:c.getNodePath & c.getNodeFileName
    def getNodePath (self,p):

        '''Return the path in effect at node p.'''

        c = self
        aList = g.get_directives_dict_list(p)
        path = c.scanAtPathDirectives(aList)
        return path

    def getNodeFileName (self,p):

        '''Return the full file name at node p,
        including effects of all @path directives.

        Return None if p is no kind of @file node.'''

        c = self
        aList = g.get_directives_dict_list(p)
        path = c.scanAtPathDirectives(aList)
        filename = p.isAnyAtFileNode()
        return filename and g.os_path_finalize_join(path,filename) or None
    #@-node:ekr.20081006100835.1:c.getNodePath & c.getNodeFileName
    #@-node:ekr.20080901124540.1:c.Directive scanning
    #@+node:ekr.20031218072017.2945:Dragging (commands)
    #@+node:ekr.20031218072017.2353:c.dragAfter
    def dragAfter(self,p,after):

        c = self ; u = self.undoer ; undoType = 'Drag'
        current = c.currentPosition()
        inAtIgnoreRange = p.inAtIgnoreRange()
        if not c.checkDrag(p,after): return
        if not c.checkMoveWithParentWithWarning(p,after.parent(),True): return

        c.endEditing()
        undoData = u.beforeMoveNode(current)
        dirtyVnodeList = p.setAllAncestorAtFileNodesDirty()
        p.moveAfter(after)
        if inAtIgnoreRange and not p.inAtIgnoreRange():
            # The moved nodes have just become newly unignored.
            dirtyVnodeList2 = p.setDirty() # Mark descendent @thin nodes dirty.
            dirtyVnodeList.extend(dirtyVnodeList2)
        else: # No need to mark descendents dirty.
            dirtyVnodeList2 = p.setAllAncestorAtFileNodesDirty()
            dirtyVnodeList.extend(dirtyVnodeList2)
        c.setChanged(True)
        u.afterMoveNode(p,undoType,undoData,dirtyVnodeList=dirtyVnodeList)
        c.selectPosition(p) # Also sets root position.
        c.redraw()

        c.updateSyntaxColorer(p) # Dragging can change syntax coloring.
    #@-node:ekr.20031218072017.2353:c.dragAfter
    #@+node:ekr.20031218072017.2947:c.dragToNthChildOf
    def dragToNthChildOf(self,p,parent,n):

        c = self ; u = c.undoer ; undoType = 'Drag'
        current = c.currentPosition()
        inAtIgnoreRange = p.inAtIgnoreRange()
        if not c.checkDrag(p,parent): return
        if not c.checkMoveWithParentWithWarning(p,parent,True): return

        c.endEditing()
        undoData = u.beforeMoveNode(current)
        dirtyVnodeList = p.setAllAncestorAtFileNodesDirty()
        p.moveToNthChildOf(parent,n)
        if inAtIgnoreRange and not p.inAtIgnoreRange():
            # The moved nodes have just become newly unignored.
            dirtyVnodeList2 = p.setDirty() # Mark descendent @thin nodes dirty.
            dirtyVnodeList.extend(dirtyVnodeList2)
        else: # No need to mark descendents dirty.
            dirtyVnodeList2 = p.setAllAncestorAtFileNodesDirty()
            dirtyVnodeList.extend(dirtyVnodeList2)
        c.setChanged(True)
        u.afterMoveNode(p,undoType,undoData,dirtyVnodeList=dirtyVnodeList)
        c.selectPosition(p) # Also sets root position.
        c.redraw()

        c.updateSyntaxColorer(p) # Dragging can change syntax coloring.
    #@-node:ekr.20031218072017.2947:c.dragToNthChildOf
    #@+node:ekr.20031218072017.2946:c.dragCloneToNthChildOf
    def dragCloneToNthChildOf (self,p,parent,n):

        c = self ; u = c.undoer ; undoType = 'Clone Drag'
        current = c.currentPosition()
        inAtIgnoreRange = p.inAtIgnoreRange()

        # g.trace("p,parent,n:",p.headString(),parent.headString(),n)
        clone = p.clone() # Creates clone & dependents, does not set undo.
        if (
            not c.checkDrag(p,parent) or
            not c.checkMoveWithParentWithWarning(clone,parent,True)
        ):
            clone.doDelete(newNode=p) # Destroys clone and makes p the current node.
            c.selectPosition(p) # Also sets root position.
            return
        c.endEditing()
        undoData = u.beforeInsertNode(current)
        dirtyVnodeList = clone.setAllAncestorAtFileNodesDirty()
        clone.moveToNthChildOf(parent,n)
        if inAtIgnoreRange and not p.inAtIgnoreRange():
            # The moved nodes have just become newly unignored.
            dirtyVnodeList2 = p.setDirty() # Mark descendent @thin nodes dirty.
            dirtyVnodeList.extend(dirtyVnodeList2)
        else: # No need to mark descendents dirty.
            dirtyVnodeList2 =  p.setAllAncestorAtFileNodesDirty()
            dirtyVnodeList.extend(dirtyVnodeList2)
        c.setChanged(True)
        u.afterInsertNode(clone,undoType,undoData,dirtyVnodeList=dirtyVnodeList)
        c.selectPosition(clone) # Also sets root position.
        c.redraw()

        c.updateSyntaxColorer(clone) # Dragging can change syntax coloring.
    #@-node:ekr.20031218072017.2946:c.dragCloneToNthChildOf
    #@+node:ekr.20031218072017.2948:c.dragCloneAfter
    def dragCloneAfter (self,p,after):

        c = self ; u = c.undoer ; undoType = 'Clone Drag'
        current = c.currentPosition()

        clone = p.clone() # Creates clone.  Does not set undo.
        if c.checkDrag(p,after) and c.checkMoveWithParentWithWarning(clone,after.parent(),True):
            inAtIgnoreRange = clone.inAtIgnoreRange()
            c.endEditing()
            undoData = u.beforeInsertNode(current)
            dirtyVnodeList = clone.setAllAncestorAtFileNodesDirty()
            clone.moveAfter(after)
            if inAtIgnoreRange and not clone.inAtIgnoreRange():
                # The moved node have just become newly unignored.
                dirtyVnodeList2 = clone.setDirty() # Mark descendent @thin nodes dirty.
                dirtyVnodeList.extend(dirtyVnodeList2)
            else: # No need to mark descendents dirty.
                dirtyVnodeList2 = clone.setAllAncestorAtFileNodesDirty()
                dirtyVnodeList.extend(dirtyVnodeList2)
            c.setChanged(True)
            u.afterInsertNode(clone,undoType,undoData,dirtyVnodeList=dirtyVnodeList)
            p = clone
        else:
            # g.trace("invalid clone drag")
            clone.doDelete(newNode=p)
        c.selectPosition(p) # Also sets root position.
        c.redraw()

        c.updateSyntaxColorer(clone) # Dragging can change syntax coloring.
    #@nonl
    #@-node:ekr.20031218072017.2948:c.dragCloneAfter
    #@-node:ekr.20031218072017.2945:Dragging (commands)
    #@+node:ekr.20031218072017.2949:Drawing Utilities (commands)
    #@+node:ekr.20080514131122.7:c.begin/endUpdate

    def beginUpdate(self):

        '''Deprecated: does nothing.'''

        g.trace('***** c.beginUpdate is deprecated',g.callers())
        if g.app.unitTesting: assert(False)

    def endUpdate(self,flag=True,scroll=True):

        '''Request a redraw of the screen if flag is True.'''

        g.trace('***** c.endUpdate is deprecated',g.callers())
        if g.app.unitTesting: assert(False)

        c = self
        if flag:
            c.requestRedrawFlag = True
            c.requestRedrawScrollFlag = scroll
            # g.trace('flag is True',c.shortFileName(),g.callers())

    BeginUpdate = beginUpdate # Compatibility with old scripts
    EndUpdate = endUpdate # Compatibility with old scripts
    #@-node:ekr.20080514131122.7:c.begin/endUpdate
    #@+node:ekr.20080515053412.1:c.add_command, c.bind, c.bind2 & c.tag_bind
    # These wrappers ensure that c.outerUpdate get called.
    #@nonl
    #@+node:ekr.20080610085158.2:c.add_command
    def add_command (self,menu,**keys):

        c = self ; command = keys.get('command')

        if command:

            def add_commandCallback(c=c,command=command):
                val = command()
                # Careful: func may destroy c.
                if c.exists: c.outerUpdate()
                return val

            keys ['command'] = add_commandCallback

            menu.add_command(**keys)

        else:
            g.trace('can not happen: no "command" arg')
    #@-node:ekr.20080610085158.2:c.add_command
    #@+node:ekr.20080610085158.3:c.bind and c.bind2
    def bind (self,w,pattern,func,*args,**keys):

        c = self ; callers = g.callers()

        def bindCallback(event,c=c,func=func,callers=callers):
            # g.trace('w',w,'binding callers',callers)
            val = func(event)
            # Careful: func may destroy c.
            if c.exists: c.outerUpdate()
            return val

        w.bind(pattern,bindCallback,*args,**keys)

    def bind2 (self,w,pattern,func,*args,**keys):

        c = self

        def bindCallback2(event,c=c,func=func):
            val = func(event)
            # Careful: func may destroy c.
            if c.exists: c.outerUpdate()
            return val

        w.bind(pattern,bindCallback2,*args,**keys)
    #@-node:ekr.20080610085158.3:c.bind and c.bind2
    #@+node:ekr.20080610085158.4:c.tag_bind
    def tag_bind (self,w,tag,event_kind,func):

        c = self
        def tag_bindCallback(event,c=c,func=func):
            val = func(event)
            # Careful: func may destroy c.
            if c.exists: c.outerUpdate()
            return val

        w.tag_bind(tag,event_kind,tag_bindCallback)
    #@-node:ekr.20080610085158.4:c.tag_bind
    #@-node:ekr.20080515053412.1:c.add_command, c.bind, c.bind2 & c.tag_bind
    #@+node:ekr.20080514131122.8:c.bringToFront
    def bringToFront(self,set_focus=True):

        c = self
        c.requestedIconify = 'deiconify'
        c.requestedFocusWidget = c.frame.body.bodyCtrl

    BringToFront = bringToFront # Compatibility with old scripts
    #@-node:ekr.20080514131122.8:c.bringToFront
    #@+node:ekr.20080514131122.9:c.get/request/set_focus
    def get_focus (self):

        c = self
        return g.app.gui and g.app.gui.get_focus(c)

    def get_requested_focus (self):

        c = self
        return c.requestedFocusWidget

    def request_focus(self,w):

        c = self
        if w: c.requestedFocusWidget = w

    def set_focus (self,w,force=False):

        c = self
        if w and g.app.gui and c.requestedFocusWidget:
            g.app.gui.set_focus(c,w)

        c.requestedFocusWidget = None
    #@-node:ekr.20080514131122.9:c.get/request/set_focus
    #@+node:ekr.20080514131122.10:c.invalidateFocus
    def invalidateFocus (self):

        '''Indicate that the focus is in an invalid location, or is unknown.'''

        # c = self
        # c.requestedFocusWidget = None
        pass
    #@nonl
    #@-node:ekr.20080514131122.10:c.invalidateFocus
    #@+node:ekr.20080514131122.11:c.masterFocusHandler
    def masterFocusHandler (self):

        pass # No longer used.

    restoreRequestedFocus = masterFocusHandler
    #@-node:ekr.20080514131122.11:c.masterFocusHandler
    #@+node:ekr.20080514131122.20:c.outerUpdate
    def outerUpdate (self):

        c = self ; aList = [] ; trace = False ; verbose = False

        if not c.exists or not c.k:
            return

        # Suppress any requested redraw until we have iconified or diconified.
        redrawFlag = c.requestRedrawFlag
        scrollFlag = c.requestRedrawScrollFlag
        c.requestRedrawFlag = False
        c.requestRedrawScrollFlag = False

        if c.requestedIconify == 'iconify':
            if verbose: aList.append('iconify')
            c.frame.iconify()

        if c.requestedIconify == 'deiconify':
            if verbose: aList.append('deiconify')
            c.frame.deiconify()

        if redrawFlag:
            # g.trace('****','tree.drag_p',c.frame.tree.drag_p)
            # A hack: force the redraw, even if we are dragging.
            aList.append('*** redraw') # : scroll: %s' % (c.requestRedrawScrollFlag))
            c.frame.tree.redraw_now(scroll=scrollFlag,forceDraw=True)

        if c.requestRecolorFlag:
            if verbose: aList.append('%srecolor' % (
                g.choose(c.incrementalRecolorFlag,'','full ')))
            c.recolor_now(incremental=c.incrementalRecolorFlag)

        if c.requestedFocusWidget:
            w = c.requestedFocusWidget
            if verbose: aList.append('focus: %s' % (
                g.app.gui.widget_name(w)))
            c.set_focus(w)
        else:
            # We can not set the focus to the body pane:
            # That would make nested calls to c.outerUpdate significant.
            pass

        if trace and aList:
            g.trace(', '.join(aList),c.shortFileName() or '<no name>',g.callers())

        c.incrementalRecolorFlag = False
        c.requestRecolorFlag = None
        c.requestRedrawFlag = False
        c.requestedFocusWidget = None
        c.requestedIconify = ''
        c.requestedRedrawScrollFlag = False
    #@-node:ekr.20080514131122.20:c.outerUpdate
    #@+node:ekr.20080514131122.12:c.recolor & requestRecolor
    def requestRecolor (self):

        c = self
        c.requestRecolorFlag = True

    recolor = requestRecolor
    #@-node:ekr.20080514131122.12:c.recolor & requestRecolor
    #@+node:ekr.20080514131122.13:c.recolor_now
    def recolor_now(self,p=None,incremental=False,interruptable=True):

        c = self
        if p is None:
            p = c.currentPosition()

        c.frame.body.colorizer.colorize(p,
            incremental=incremental,interruptable=interruptable)
    #@-node:ekr.20080514131122.13:c.recolor_now
    #@+node:ekr.20080514131122.14:c.redraw and c.redraw_now
    def redraw (self,scroll=True):
        c = self
        c.requestRedrawFlag = True
        # This makes c.redraw *not quite* the same as c.endUpdate.
        c.requestRedrawScrollFlag = scroll

    def redraw_now (self):
        c = self
        c.requestRedrawFlag = True
        c.outerUpdate()
        if c.requestRedrawFlag:
            g.es_print('redraw_now: can not happen',g.callers())
        # assert not c.requestRedrawFlag

    # Compatibility with old scripts
    force_redraw = redraw_now
    #@-node:ekr.20080514131122.14:c.redraw and c.redraw_now
    #@+node:ekr.20080514131122.15:c.restoreFocus
    def restoreFocus (self):

        '''Ensure that the focus eventually gets restored.'''
        pass
        # g.trace(g.callers(5))

        # c =self
        # trace = not g.app.unitTesting and c.config.getBool('trace_focus')

        # if c.requestedFocusWidget:
            # c.hasFocusWidget = None # Force an update
        # elif c.hasFocusWidget:
            # c.requestedFocusWidget = c.hasFocusWidget
            # c.hasFocusWidget = None # Force an update
        # else:
            # # Should not happen, except during unit testing.
            # # c.masterFocusHandler sets c.hasFocusWidget,
            # # so if it is not set here it is because this method cleared it.
            # if not g.app.unitTesting: g.trace('oops: no requested or present widget.',g.callers())
            # c.bodyWantsFocusNow()

        # if c.inCommand:
            # if trace: g.trace('expecting later call to c.masterFocusHandler')
            # # A call to c.masterFocusHandler will surely happen.
        # else:
            # c.masterFocusHandler() # Do it now.
    #@-node:ekr.20080514131122.15:c.restoreFocus
    #@+node:ekr.20080514131122.16:c.traceFocus
    trace_focus_count = 0

    def traceFocus (self,w):

        c = self

        if False or (not g.app.unitTesting and c.config.getBool('trace_focus')):
            c.trace_focus_count += 1
            g.pr('%4d' % (c.trace_focus_count),c.widget_name(w),g.callers(8))
    #@-node:ekr.20080514131122.16:c.traceFocus
    #@+node:ekr.20080514131122.17:c.widget_name
    def widget_name (self,widget):

        c = self

        return g.app.gui and g.app.gui.widget_name(widget) or ''
    #@-node:ekr.20080514131122.17:c.widget_name
    #@+node:ekr.20080514131122.18:c.xWantsFocus (no change)
    def bodyWantsFocus(self):
        c = self ; body = c.frame.body
        c.request_focus(body and body.bodyCtrl)

    def headlineWantsFocus(self,p):
        c = self
        c.request_focus(p and c.edit_widget(p))

    def logWantsFocus(self):
        c = self ; log = c.frame.log
        c.request_focus(log and log.logCtrl)

    def minibufferWantsFocus(self):
        c = self ; k = c.k
        if k: k.minibufferWantsFocus()

    def treeWantsFocus(self):
        c = self ; tree = c.frame.tree
        c.request_focus(tree and tree.canvas)

    def widgetWantsFocus(self,w):
        c = self ; c.request_focus(w)
    #@-node:ekr.20080514131122.18:c.xWantsFocus (no change)
    #@+node:ekr.20080514131122.19:c.xWantsFocusNow
    # widgetWantsFocusNow does an automatic update.
    def widgetWantsFocusNow(self,w):
        c = self
        c.request_focus(w)
        c.outerUpdate()
        # Re-request widget so we don't use the body by default.
        c.request_focus(w) 

    # All other "Now" methods wait.
    bodyWantsFocusNow = bodyWantsFocus
    headlineWantsFocusNow = headlineWantsFocus
    logWantsFocusNow = logWantsFocus
    minibufferWantsFocusNow = minibufferWantsFocus
    treeWantsFocusNow = treeWantsFocus
    #@-node:ekr.20080514131122.19:c.xWantsFocusNow
    #@-node:ekr.20031218072017.2949:Drawing Utilities (commands)
    #@+node:ekr.20031218072017.2955:Enabling Menu Items
    #@+node:ekr.20040323172420:Slow routines: no longer used
    #@+node:ekr.20031218072017.2966:canGoToNextDirtyHeadline (slow)
    def canGoToNextDirtyHeadline (self):

        c = self ; current = c.currentPosition()

        for p in c.all_positions_with_unique_vnodes_iter():
            if p != current and p.isDirty():
                return True

        return False
    #@-node:ekr.20031218072017.2966:canGoToNextDirtyHeadline (slow)
    #@+node:ekr.20031218072017.2967:canGoToNextMarkedHeadline (slow)
    def canGoToNextMarkedHeadline (self):

        c = self ; current = c.currentPosition()

        for p in c.all_positions_with_unique_vnodes_iter():
            if p != current and p.isMarked():
                return True

        return False
    #@-node:ekr.20031218072017.2967:canGoToNextMarkedHeadline (slow)
    #@+node:ekr.20031218072017.2968:canMarkChangedHeadline (slow)
    def canMarkChangedHeadlines (self):

        c = self

        for p in c.all_positions_with_unique_vnodes_iter():
            if p.isDirty():
                return True

        return False
    #@-node:ekr.20031218072017.2968:canMarkChangedHeadline (slow)
    #@+node:ekr.20031218072017.2969:canMarkChangedRoots (slow)
    def canMarkChangedRoots (self):

        c = self

        for p in c.all_positions_with_unique_vnodes_iter():
            if p.isDirty and p.isAnyAtFileNode():
                return True

        return False
    #@-node:ekr.20031218072017.2969:canMarkChangedRoots (slow)
    #@-node:ekr.20040323172420:Slow routines: no longer used
    #@+node:ekr.20040131170659:canClone (new for hoist)
    def canClone (self):

        c = self

        if c.hoistStack:
            current = c.currentPosition()
            bunch = c.hoistStack[-1]
            return current != bunch.p
        else:
            return True
    #@-node:ekr.20040131170659:canClone (new for hoist)
    #@+node:ekr.20031218072017.2956:canContractAllHeadlines
    def canContractAllHeadlines (self):

        c = self

        for p in c.all_positions_with_unique_vnodes_iter():
            if p.isExpanded():
                return True

        return False
    #@-node:ekr.20031218072017.2956:canContractAllHeadlines
    #@+node:ekr.20031218072017.2957:canContractAllSubheads
    def canContractAllSubheads (self):

        c = self ; current = c.currentPosition()

        for p in current.subtree_iter():
            if p != current and p.isExpanded():
                return True

        return False
    #@-node:ekr.20031218072017.2957:canContractAllSubheads
    #@+node:ekr.20031218072017.2958:canContractParent
    def canContractParent (self):

        c = self
        return c.currentPosition().parent()
    #@-node:ekr.20031218072017.2958:canContractParent
    #@+node:ekr.20031218072017.2959:canContractSubheads
    def canContractSubheads (self):

        c = self ; current = c.currentPosition()

        for child in current.children_iter():
            if child.isExpanded():
                return True

        return False
    #@-node:ekr.20031218072017.2959:canContractSubheads
    #@+node:ekr.20031218072017.2960:canCutOutline & canDeleteHeadline
    def canDeleteHeadline (self):

        c = self ; p = c.currentPosition()

        if c.hoistStack:
            bunch = c.hoistStack[0]
            if p == bunch.p: return False

        return p.hasParent() or p.hasThreadBack() or p.hasNext()

    canCutOutline = canDeleteHeadline
    #@-node:ekr.20031218072017.2960:canCutOutline & canDeleteHeadline
    #@+node:ekr.20031218072017.2961:canDemote
    def canDemote (self):

        c = self
        return c.currentPosition().hasNext()
    #@-node:ekr.20031218072017.2961:canDemote
    #@+node:ekr.20031218072017.2962:canExpandAllHeadlines
    def canExpandAllHeadlines (self):

        c = self

        for p in c.all_positions_with_unique_vnodes_iter():
            if not p.isExpanded():
                return True

        return False
    #@-node:ekr.20031218072017.2962:canExpandAllHeadlines
    #@+node:ekr.20031218072017.2963:canExpandAllSubheads
    def canExpandAllSubheads (self):

        c = self

        for p in c.currentPosition().subtree_iter():
            if not p.isExpanded():
                return True

        return False
    #@-node:ekr.20031218072017.2963:canExpandAllSubheads
    #@+node:ekr.20031218072017.2964:canExpandSubheads
    def canExpandSubheads (self):

        c = self ; current = c.currentPosition()

        for p in current.children_iter():
            if p != current and not p.isExpanded():
                return True

        return False
    #@-node:ekr.20031218072017.2964:canExpandSubheads
    #@+node:ekr.20031218072017.2287:canExtract, canExtractSection & canExtractSectionNames
    def canExtract (self):

        c = self ; body = c.frame.body
        return body and body.hasTextSelection()

    canExtractSectionNames = canExtract

    def canExtractSection (self):

        c = self ; body = c.frame.body
        if not body: return False

        s = body.getSelectedText()
        if not s: return False

        line = g.get_line(s,0)
        i1 = line.find("<<")
        j1 = line.find(">>")
        i2 = line.find("@<")
        j2 = line.find("@>")
        return -1 < i1 < j1 or -1 < i2 < j2
    #@-node:ekr.20031218072017.2287:canExtract, canExtractSection & canExtractSectionNames
    #@+node:ekr.20031218072017.2965:canFindMatchingBracket
    def canFindMatchingBracket (self):

        c = self ; brackets = "()[]{}"
        body = c.frame.body
        s = body.getAllText()
        ins = body.getInsertPoint()
        c1 = 0 <= ins   < len(s) and s[ins] or ''
        c2 = 0 <= ins-1 < len(s) and s[ins-1] or ''

        return (c1 and c1 in brackets) or (c2 and c2 in brackets)
    #@-node:ekr.20031218072017.2965:canFindMatchingBracket
    #@+node:ekr.20040303165342:canHoist & canDehoist
    def canDehoist(self):

        c = self
        return c.hoistLevel() > 0

    def canHoist(self):

        # N.B.  This is called at idle time, so minimizing positions is crucial!
        c = self
        if c.hoistStack:
            bunch = c.hoistStack[-1]
            return bunch.p and not c.isCurrentPosition(bunch.p)
        elif c.currentPositionIsRootPosition():
            return c.currentPositionHasNext()
        else:
            return True
    #@-node:ekr.20040303165342:canHoist & canDehoist
    #@+node:ekr.20070608165544:hoistLevel
    def hoistLevel (self):

        c = self ; cc = c.chapterController
        n = len(c.hoistStack)
        if n > 0 and cc and cc.inChapter():
            n -= 1
        return n
    #@nonl
    #@-node:ekr.20070608165544:hoistLevel
    #@+node:ekr.20031218072017.2970:canMoveOutlineDown
    def canMoveOutlineDown (self):

        c = self ; current = c.currentPosition()

        return current and current.visNext(c)
    #@-node:ekr.20031218072017.2970:canMoveOutlineDown
    #@+node:ekr.20031218072017.2971:canMoveOutlineLeft
    def canMoveOutlineLeft (self):

        c = self ; p = c.currentPosition()

        if c.hoistStack:
            bunch = c.hoistStack[-1]
            if p and p.hasParent():
                p.moveToParent()
                return p != bunch.p and bunch.p.isAncestorOf(p)
            else:
                return False
        else:
            return p and p.hasParent()
    #@-node:ekr.20031218072017.2971:canMoveOutlineLeft
    #@+node:ekr.20031218072017.2972:canMoveOutlineRight
    def canMoveOutlineRight (self):

        c = self ; p = c.currentPosition()

        if c.hoistStack:
            bunch = c.hoistStack[-1]
            return p and p.hasBack() and p != bunch.p
        else:
            return p and p.hasBack()
    #@-node:ekr.20031218072017.2972:canMoveOutlineRight
    #@+node:ekr.20031218072017.2973:canMoveOutlineUp
    def canMoveOutlineUp (self):

        c = self ; current = c.currentPosition()

        visBack = current and current.visBack(c)

        if not visBack:
            return False
        elif visBack.visBack(c):
            return True
        elif c.hoistStack:
            limit,limitIsVisible = c.visLimit()
            if limitIsVisible: # A hoist
                return current != limit
            else: # A chapter.
                return current != limit.firstChild()
        else:
            return current != c.rootPosition()
    #@-node:ekr.20031218072017.2973:canMoveOutlineUp
    #@+node:ekr.20031218072017.2974:canPasteOutline
    def canPasteOutline (self,s=None):

        c = self
        if s == None:
            s = g.app.gui.getTextFromClipboard()
        if not s:
            return False

        # g.trace(s)
        if g.match(s,0,g.app.prolog_prefix_string):
            return True
        elif len(s) > 0:
            return c.importCommands.stringIsValidMoreFile(s)
        else:
            return False
    #@-node:ekr.20031218072017.2974:canPasteOutline
    #@+node:ekr.20031218072017.2975:canPromote
    def canPromote (self):

        c = self ; v = c.currentVnode()
        return v and v.hasChildren()
    #@-node:ekr.20031218072017.2975:canPromote
    #@+node:ekr.20031218072017.2976:canRevert
    def canRevert (self):

        # c.mFileName will be "untitled" for unsaved files.
        c = self
        return (c.frame and c.mFileName and c.isChanged())
    #@-node:ekr.20031218072017.2976:canRevert
    #@+node:ekr.20031218072017.2977:canSelect....
    def canSelectThreadBack (self):
        c = self ; p = c.currentPosition()
        return p.hasThreadBack()

    def canSelectThreadNext (self):
        c = self ; p = c.currentPosition()
        return p.hasThreadNext()

    def canSelectVisBack (self):
        c = self ; p = c.currentPosition()
        return p.visBack(c)

    def canSelectVisNext (self):
        c = self ; p = c.currentPosition()
        return p.visNext(c)
    #@-node:ekr.20031218072017.2977:canSelect....
    #@+node:ekr.20031218072017.2978:canShiftBodyLeft/Right
    def canShiftBodyLeft (self):

        c = self ; body = c.frame.body
        return body and body.getAllText()

    canShiftBodyRight = canShiftBodyLeft
    #@-node:ekr.20031218072017.2978:canShiftBodyLeft/Right
    #@+node:ekr.20031218072017.2979:canSortChildren, canSortSiblings
    def canSortChildren (self):

        c = self ; p = c.currentPosition()
        return p and p.hasChildren()

    def canSortSiblings (self):

        c = self ; p = c.currentPosition()
        return p and (p.hasNext() or p.hasBack())
    #@-node:ekr.20031218072017.2979:canSortChildren, canSortSiblings
    #@+node:ekr.20031218072017.2980:canUndo & canRedo
    def canUndo (self):

        c = self
        return c.undoer.canUndo()

    def canRedo (self):

        c = self
        return c.undoer.canRedo()
    #@-node:ekr.20031218072017.2980:canUndo & canRedo
    #@+node:ekr.20031218072017.2981:canUnmarkAll
    def canUnmarkAll (self):

        c = self

        for p in c.all_positions_with_unique_vnodes_iter():
            if p.isMarked():
                return True

        return False
    #@-node:ekr.20031218072017.2981:canUnmarkAll
    #@-node:ekr.20031218072017.2955:Enabling Menu Items
    #@+node:ekr.20031218072017.2982:Getters & Setters
    #@+node:ekr.20060906211747:Getters
    #@+node:ekr.20040803140033:c.currentPosition
    def currentPosition (self,copy=True):

        """Return the presently selected position."""

        c = self

        if hasattr(c,'_currentPosition') and c._currentPosition:
            # New in Leo 4.4.2: *always* return a copy.
            return c._currentPosition.copy()
        else:
            return c.nullPosition()

    # For compatibiility with old scripts.
    currentVnode = currentPosition
    #@-node:ekr.20040803140033:c.currentPosition
    #@+node:ekr.20040306220230.1:c.edit_widget
    def edit_widget (self,p):

        c = self

        return p and c.frame.tree.edit_widget(p)
    #@nonl
    #@-node:ekr.20040306220230.1:c.edit_widget
    #@+node:ekr.20031218072017.2986:c.fileName & relativeFileName & shortFileName
    # Compatibility with scripts

    def fileName (self):

        return self.mFileName

    def relativeFileName (self):

        return self.mRelativeFileName or self.mFileName

    def shortFileName (self):

        return g.shortFileName(self.mFileName)

    shortFilename = shortFileName
    #@-node:ekr.20031218072017.2986:c.fileName & relativeFileName & shortFileName
    #@+node:ekr.20060906134053:c.findRootPosition New in 4.4.2
    #@+at 
    #@nonl
    # Aha! The Commands class can easily recompute the root position::
    # 
    #     c.setRootPosition(c.findRootPosition(p))
    # 
    # Any command that changes the outline should call this code.
    # 
    # As a result, the fundamental p and v methods that alter trees need never
    # convern themselves about reporting the changed root.  A big improvement.
    #@-at
    #@@c

    def findRootPosition (self,p):

        '''Return the root position of the outline containing p.'''

        c = self ; p = p.copy()

        while p and p.hasParent():
            p.moveToParent()
            # g.trace(p.headString(),g.callers())

        while p and p.hasBack():
            p.moveToBack()

        # g.trace(p and p.headString())

        return p
    #@nonl
    #@-node:ekr.20060906134053:c.findRootPosition New in 4.4.2
    #@+node:ekr.20070615070925.1:c.firstVisible
    def firstVisible(self):

        """Move to the first visible node of the present chapter or hoist."""

        c = self ; p = c.currentPosition()

        while 1:
            back = p.visBack(c)
            if back and back.isVisible(c):
                p = back
            else: break
        return p
    #@-node:ekr.20070615070925.1:c.firstVisible
    #@+node:ekr.20040803112200:c.is...Position
    #@+node:ekr.20040803155551:c.currentPositionIsRootPosition
    def currentPositionIsRootPosition (self):

        """Return True if the current position is the root position.

        This method is called during idle time, so not generating positions
        here fixes a major leak.
        """

        c = self

        return (
            c._currentPosition and c._rootPosition and
            c._currentPosition == c._rootPosition)
    #@-node:ekr.20040803155551:c.currentPositionIsRootPosition
    #@+node:ekr.20040803160656:c.currentPositionHasNext
    def currentPositionHasNext (self):

        """Return True if the current position is the root position.

        This method is called during idle time, so not generating positions
        here fixes a major leak.
        """

        c = self ; current = c._currentPosition 

        return current and current.hasNext()
    #@-node:ekr.20040803160656:c.currentPositionHasNext
    #@+node:ekr.20040803112450:c.isCurrentPosition
    def isCurrentPosition (self,p):

        c = self

        if p is None or c._currentPosition is None:
            return False
        else:
            return p == c._currentPosition
    #@-node:ekr.20040803112450:c.isCurrentPosition
    #@+node:ekr.20040803112450.1:c.isRootPosition
    def isRootPosition (self,p):

        c = self

        if p is None or c._rootPosition is None:
            return False
        else:
            return p == c._rootPosition
    #@nonl
    #@-node:ekr.20040803112450.1:c.isRootPosition
    #@-node:ekr.20040803112200:c.is...Position
    #@+node:ekr.20031218072017.2987:c.isChanged
    def isChanged (self):

        return self.changed
    #@-node:ekr.20031218072017.2987:c.isChanged
    #@+node:ekr.20031218072017.4146:c.lastVisible
    def lastVisible(self):

        """Move to the last visible node of the present chapter or hoist."""

        c = self ; p = c.currentPosition()

        while 1:
            next = p.visNext(c)
            # g.trace('next',next)
            if next and next.isVisible(c):
                p = next
            else: break
        return p
    #@-node:ekr.20031218072017.4146:c.lastVisible
    #@+node:ekr.20070609122713:c.visLimit
    def visLimit (self):

        '''Return the topmost visible node.
        This is affected by chapters and hoists.'''

        c = self ; cc = c.chapterController

        if c.hoistStack:
            bunch = c.hoistStack[-1]
            p = bunch.p
            limitIsVisible = not cc or not p.headString().startswith('@chapter')
            return p,limitIsVisible
        else:
            return None,None
    #@-node:ekr.20070609122713:c.visLimit
    #@+node:ekr.20040311094927:c.nullPosition
    def nullPosition (self):

        c = self ; v = None
        return leoNodes.position(v)
    #@-node:ekr.20040311094927:c.nullPosition
    #@+node:ekr.20040307104131.3:c.positionExists
    def positionExists(self,p,root=None):

        """Return True if a position exists in c's tree"""

        c = self ; p = p.copy()

        # This code must be fast.
        if not root:
            root = c.rootPosition()

        while p:
            if p == root:
                return True
            if p.hasParent():
                p.moveToParent()
            else:
                p.moveToBack()

        return False
    #@-node:ekr.20040307104131.3:c.positionExists
    #@+node:ekr.20040803140033.2:c.rootPosition
    def rootPosition(self):

        """Return the root position."""

        c = self

        if hasattr(self,'_rootPosition') and self._rootPosition:
            return self._rootPosition.copy()
        else:
            return  c.nullPosition()

    # For compatibiility with old scripts.
    rootVnode = rootPosition
    #@nonl
    #@-node:ekr.20040803140033.2:c.rootPosition
    #@-node:ekr.20060906211747:Getters
    #@+node:ekr.20060906211747.1:Setters
    #@+node:ekr.20040315032503:c.appendStringToBody
    def appendStringToBody (self,p,s,encoding="utf-8"):

        c = self
        if not s: return

        body = p.bodyString()
        assert(g.isUnicode(body))
        s = g.toUnicode(s,encoding)

        c.setBodyString(p,body + s,encoding)
    #@-node:ekr.20040315032503:c.appendStringToBody
    #@+node:ekr.20031218072017.2984:c.clearAllMarked
    def clearAllMarked (self):

        c = self

        for p in c.all_positions_with_unique_vnodes_iter():
            p.v.clearMarked()
    #@-node:ekr.20031218072017.2984:c.clearAllMarked
    #@+node:ekr.20031218072017.2985:c.clearAllVisited
    def clearAllVisited (self):

        c = self

        for p in c.all_positions_with_unique_vnodes_iter():
            p.v.clearVisited()
            p.v.t.clearVisited()
            p.v.t.clearWriteBit()
    #@-node:ekr.20031218072017.2985:c.clearAllVisited
    #@+node:ekr.20060906211138:c.clearMarked
    def clearMarked  (self,p):

        c = self
        p.v.clearMarked()
        g.doHook("clear-mark",c=c,p=p,v=p)
    #@nonl
    #@-node:ekr.20060906211138:c.clearMarked
    #@+node:ekr.20040305223522:c.setBodyString
    def setBodyString (self,p,s,encoding="utf-8"):

        c = self ; v = p.v
        if not c or not v: return

        s = g.toUnicode(s,encoding)
        current = c.currentPosition()
        # 1/22/05: Major change: the previous test was: 'if p == current:'
        # This worked because commands work on the presently selected node.
        # But setRecentFiles may change a _clone_ of the selected node!
        if current and p.v.t==current.v.t:
            # Revert to previous code, but force an empty selection.
            c.frame.body.setSelectionAreas(s,None,None)
            w = c.frame.body.bodyCtrl
            i = w.getInsertPoint()
            w.setSelectionRange(i,i)
            # This code destoys all tags, so we must recolor.
            c.recolor()

        # Keep the body text in the tnode up-to-date.
        if v.t._bodyString != s:
            v.setBodyString(s)
            v.t.setSelection(0,0)
            p.setDirty()
            if not c.isChanged():
                c.setChanged(True)
            c.redraw()
    #@-node:ekr.20040305223522:c.setBodyString
    #@+node:ekr.20031218072017.2989:c.setChanged
    def setChanged (self,changedFlag):

        c = self
        if not c.frame: return

        # if changedFlag: g.trace('***',g.callers())

        # Clear all dirty bits _before_ setting the caption.
        # Clear all dirty bits except orphaned @file nodes
        if not changedFlag:
            # g.trace("clearing all dirty bits")
            for p in c.all_positions_with_unique_tnodes_iter():
                if p.isDirty() and not (p.isAtFileNode() or p.isAtNorefFileNode()):
                    p.clearDirty()

        # Update all derived changed markers.
        c.changed = changedFlag
        s = c.frame.getTitle()
        if len(s) > 2 and not c.loading: # don't update while loading.
            if changedFlag:
                if s [0] != '*': c.frame.setTitle("* " + s)
            else:
                if s[0:2]=="* ": c.frame.setTitle(s[2:])
    #@-node:ekr.20031218072017.2989:c.setChanged
    #@+node:ekr.20040803140033.1:c.setCurrentPosition
    def setCurrentPosition (self,p):

        """Set the presently selected position. For internal use only.

        Client code should use c.selectPosition instead."""

        c = self ; cc = c.chapterController

        # g.trace(p.headString(),g.callers())

        if p:
            # Important: p.equal requires c._currentPosition to be non-None.
            if c._currentPosition and p == c._currentPosition:
                pass # We have already made a copy.
            else: # Must make a copy _now_
                c._currentPosition = p.copy()

            # New in Leo 4.4.2: always recompute the root position here.
            # This *guarantees* that c.rootPosition always returns the proper value.
            newRoot = c.findRootPosition(c._currentPosition)
            if newRoot:
                c.setRootPosition(newRoot)
            # This is *not* an error: newRoot can be None when switching chapters.
            # else: g.trace('******** no new root')
        else:
            c._currentPosition = None

    # For compatibiility with old scripts.
    setCurrentVnode = setCurrentPosition
    #@nonl
    #@-node:ekr.20040803140033.1:c.setCurrentPosition
    #@+node:ekr.20040305223225:c.setHeadString
    def setHeadString (self,p,s,encoding="utf-8"):

        c = self
        w = c.edit_widget(p) # w only exists for the Tk gui.

        p.initHeadString(s,encoding)

        if w:
            s = g.toUnicode(s,encoding)
            w.setAllText(s)
            width = c.frame.tree.headWidth(p=None,s=s)
            w.setWidth(width)

        p.setDirty()
    #@nonl
    #@-node:ekr.20040305223225:c.setHeadString
    #@+node:ekr.20060109164136:c.setLog
    def setLog (self):

        c = self

        if c.exists:
            try:
                # c.frame or c.frame.log may not exist.
                g.app.setLog(c.frame.log)
            except AttributeError:
                pass
    #@-node:ekr.20060109164136:c.setLog
    #@+node:ekr.20060906211138.1:c.setMarked
    def setMarked (self,p):

        c = self
        p.v.setMarked()
        g.doHook("set-mark",c=c,p=p,v=p)
    #@nonl
    #@-node:ekr.20060906211138.1:c.setMarked
    #@+node:ekr.20040803140033.3:c.setRootPosition
    def setRootPosition(self,p):

        """Set the root positioin."""

        c = self

        # g.trace(p and p.headString(),g.callers())

        if p:
            # Important: p.equal requires c._rootPosition to be non-None.
            if c._rootPosition and p == c._rootPosition:
                pass # We have already made a copy.
            else:
                # We must make a copy _now_.
                c._rootPosition = p.copy()
        else:
            c._rootPosition = None
    #@nonl
    #@-node:ekr.20040803140033.3:c.setRootPosition
    #@+node:ekr.20060906131836:c.setRootVnode New in 4.4.2
    def setRootVnode (self, v):

        c = self
        newRoot = leoNodes.position(v)
        c.setRootPosition(newRoot)
    #@nonl
    #@-node:ekr.20060906131836:c.setRootVnode New in 4.4.2
    #@+node:ekr.20040311173238:c.topPosition & c.setTopPosition
    def topPosition(self):

        """Return the root position."""

        c = self

        if c._topPosition:
            return c._topPosition.copy()
        else:
            return c.nullPosition()

    def setTopPosition(self,p):

        """Set the root positioin."""

        c = self

        if p:
            c._topPosition = p.copy()
        else:
            c._topPosition = c.nullPosition()

    # Define these for compatibiility with old scripts.
    topVnode = topPosition
    setTopVnode = setTopPosition
    #@-node:ekr.20040311173238:c.topPosition & c.setTopPosition
    #@+node:ekr.20031218072017.3404:c.trimTrailingLines
    def trimTrailingLines (self,p):

        """Trims trailing blank lines from a node.

        It is surprising difficult to do this during Untangle."""

        c = self
        body = p.bodyString()
        lines = body.split('\n')
        i = len(lines) - 1 ; changed = False
        while i >= 0:
            line = lines[i]
            j = g.skip_ws(line,0)
            if j + 1 == len(line):
                del lines[i]
                i -= 1 ; changed = True
            else: break
        if changed:
            body = ''.join(body) + '\n' # Add back one last newline.
            # g.trace(body)
            c.setBodyString(p,body)
            # Don't set the dirty bit: it would just be annoying.
    #@nonl
    #@-node:ekr.20031218072017.3404:c.trimTrailingLines
    #@-node:ekr.20060906211747.1:Setters
    #@-node:ekr.20031218072017.2982:Getters & Setters
    #@+node:ekr.20031218072017.2990:Selecting & Updating (commands)
    #@+node:ekr.20031218072017.2991:c.editPosition
    # Selects v: sets the focus to p and edits p.

    def editPosition(self,p,selectAll=False):

        c = self ; k = c.k

        if p:
            c.selectPosition(p)

            c.frame.tree.editLabel(p,selectAll=selectAll)

            if k:
                if selectAll:
                    k.setInputState('insert')
                else:
                    k.setDefaultInputState()

                k.showStateAndMode()
    #@-node:ekr.20031218072017.2991:c.editPosition
    #@+node:ekr.20031218072017.2992:c.endEditing (calls tree.endEditLabel)
    # Ends the editing in the outline.

    def endEditing(self):

        c = self ; k = c.k

        c.frame.tree.endEditLabel()

        c.frame.tree.setSelectedLabelState(p=c.currentPosition())

        # The following code would be wrong; c.endEditing is a utility method.
        # if k:
            # k.setDefaultInputState()
            # # Recolor the *body* text, **not** the headline.
            # k.showStateAndMode(w=c.frame.body.bodyCtrl)
    #@-node:ekr.20031218072017.2992:c.endEditing (calls tree.endEditLabel)
    #@+node:ekr.20031218072017.2997:c.selectPosition
    def selectPosition(self,p):

        """Select a new position."""

        c = self ; cc = c.chapterController

        if cc:
            cc.selectChapterForPosition(p)

        # g.trace(p.headString(),g.callers())

        c.frame.tree.select(p)

        # New in Leo 4.4.2.
        c.setCurrentPosition(p)
            # Do *not* test whether the position exists!
            # We may be in the midst of an undo.

    selectVnode = selectPosition
    #@-node:ekr.20031218072017.2997:c.selectPosition
    #@+node:ekr.20031218072017.2998:c.selectVnodeWithEditing
    # Selects the given node and enables editing of the headline if editFlag is True.

    def selectVnodeWithEditing(self,v,editFlag):

        c = self
        if editFlag:
            c.editPosition(v)
        else:
            c.selectVnode(v)

    selectPositionWithEditing = selectVnodeWithEditing
    #@-node:ekr.20031218072017.2998:c.selectVnodeWithEditing
    #@+node:ekr.20060923202156:c.onCanvasKey
    def onCanvasKey (self,event):

        '''Navigate to the next headline starting with ch = event.char.
        If ch is uppercase, search all headlines; otherwise search only visible headlines.
        This is modelled on Windows explorer.'''

        # g.trace(event and event.char)

        if not event or not event.char or not event.keysym.isalnum():
            return
        c  = self ; p = c.currentPosition() ; p1 = p.copy()
        invisible = c.config.getBool('invisible_outline_navigation')
        ch = event.char
        allFlag = ch.isupper() and invisible # all is a global (!?)
        if not invisible: ch = ch.lower()
        found = False
        extend = self.navQuickKey()
        attempts = g.choose(extend,(True,False),(False,))
        for extend2 in attempts:
            p = p1.copy()
            while 1:
                if allFlag:
                    p.moveToThreadNext()
                else:
                    p.moveToVisNext(c)
                if not p:
                    p = c.rootPosition()
                if p == p1: # Never try to match the same position.
                    # g.trace('failed',extend2)
                    found = False ; break
                newPrefix = c.navHelper(p,ch,extend2)
                if newPrefix:
                    found = True ; break
            if found: break
        if found:
            if allFlag: c.frame.tree.expandAllAncestors(p)
            c.selectPosition(p)
            c.navTime = time.clock()
            c.navPrefix = newPrefix
            # g.trace('extend',extend,'extend2',extend2,'navPrefix',c.navPrefix,'p',p.headString())
        else:
            c.navTime = None
            c.navPrefix = ''
        c.treeWantsFocusNow()
    #@+node:ekr.20061002095711.1:c.navQuickKey
    def navQuickKey (self):

        '''return true if there are two quick outline navigation keys
        in quick succession.

        Returns False if @float outline_nav_extend_delay setting is 0.0 or unspecified.'''

        c = self

        deltaTime = c.config.getFloat('outline_nav_extend_delay')

        if deltaTime in (None,0.0):
            return False
        else:
            nearTime = c.navTime and time.clock() - c.navTime < deltaTime
            return nearTime
    #@nonl
    #@-node:ekr.20061002095711.1:c.navQuickKey
    #@+node:ekr.20061002095711:c.navHelper
    def navHelper (self,p,ch,extend):

        c = self ; h = p.headString().lower()

        if extend:
            prefix = c.navPrefix + ch
            return h.startswith(prefix.lower()) and prefix

        if h.startswith(ch):
            return ch

        # New feature: search for first non-blank character after @x for common x.
        if ch != '@' and h.startswith('@'):
            for s in ('button','command','file','thin','asis','nosent','noref'):
                prefix = '@'+s
                if h.startswith('@'+s):
                    while 1:
                        n = len(prefix)
                        ch2 = n < len(h) and h[n] or ''
                        if ch2.isspace():
                            prefix = prefix + ch2
                        else: break
                    if len(prefix) < len(h) and h.startswith(prefix + ch.lower()):
                        return prefix + ch
        return ''
    #@nonl
    #@-node:ekr.20061002095711:c.navHelper
    #@-node:ekr.20060923202156:c.onCanvasKey
    #@-node:ekr.20031218072017.2990:Selecting & Updating (commands)
    #@+node:ekr.20031218072017.2999:Syntax coloring interface
    #@+at 
    #@nonl
    # These routines provide a convenient interface to the syntax colorer.
    #@-at
    #@+node:ekr.20031218072017.3000:updateSyntaxColorer
    def updateSyntaxColorer(self,v):

        self.frame.body.updateSyntaxColorer(v)
    #@-node:ekr.20031218072017.3000:updateSyntaxColorer
    #@-node:ekr.20031218072017.2999:Syntax coloring interface
    #@-others

class Commands (baseCommands):
    """A class that implements most of Leo's commands."""
    pass
#@-node:ekr.20041118104831:class commands
#@+node:ekr.20041118104831.1:class configSettings (leoCommands)
class configSettings:

    """A class to hold config settings for commanders."""

    #@    @+others
    #@+node:ekr.20041118104831.2:configSettings.__init__ (c.configSettings)
    def __init__ (self,c):

        self.c = c

        # Init these here to keep pylint happy.
        self.default_derived_file_encoding = None
        self.new_leo_file_encoding = None
        self.redirect_execute_script_output_to_log_pane = None
        self.tkEncoding = None

        self.defaultBodyFontSize = g.app.config.defaultBodyFontSize
        self.defaultLogFontSize  = g.app.config.defaultLogFontSize
        self.defaultMenuFontSize = g.app.config.defaultMenuFontSize
        self.defaultTreeFontSize = g.app.config.defaultTreeFontSize

        for key in g.app.config.encodingIvarsDict:
            if key != '_hash':
                self.initEncoding(key)

        for key in g.app.config.ivarsDict:
            if key != '_hash':
                self.initIvar(key)
    #@+node:ekr.20041118104240:initIvar
    def initIvar(self,key):

        c = self.c

        # N.B. The key is munged.
        bunch = g.app.config.ivarsDict.get(key)
        ivarName = bunch.ivar
        val = g.app.config.get(c,ivarName,kind=None) # kind is ignored anyway.

        if val or not hasattr(self,ivarName):
            # g.trace('c.configSettings',c.shortFileName(),ivarName,val)
            setattr(self,ivarName,val)
    #@-node:ekr.20041118104240:initIvar
    #@+node:ekr.20041118104414:initEncoding
    def initEncoding (self,key):

        c = self.c

        # N.B. The key is munged.
        bunch = g.app.config.encodingIvarsDict.get(key)
        encodingName = bunch.ivar
        encoding = g.app.config.get(c,encodingName,kind='string')

        # New in 4.4b3: use the global setting as a last resort.
        if encoding:
            # g.trace('c.configSettings',c.shortFileName(),encodingName,encoding)
            setattr(self,encodingName,encoding)
        else:
            encoding = getattr(g.app.config,encodingName)
            # g.trace('g.app.config',c.shortFileName(),encodingName,encoding)
            setattr(self,encodingName,encoding)

        if encoding and not g.isValidEncoding(encoding):
            g.es("bad", "%s: %s" % (encodingName,encoding))
    #@-node:ekr.20041118104414:initEncoding
    #@-node:ekr.20041118104831.2:configSettings.__init__ (c.configSettings)
    #@+node:ekr.20041118053731:Getters (c.configSettings)
    def get (self,setting,theType):
        '''A helper function: return the commander's setting, checking the type.'''
        return g.app.config.get(self.c,setting,theType)

    def getAbbrevDict (self):
        '''return the commander's abbreviation dictionary.'''
        return g.app.config.getAbbrevDict(self.c)

    def getBool (self,setting,default=None):
        '''Return the value of @bool setting, or the default if the setting is not found.'''
        return g.app.config.getBool(self.c,setting,default=default)

    def getButtons (self):
        '''Return a list of tuples (x,y) for common @button nodes.'''
        return g.app.config.atCommonButtonsList # unusual.

    def getColor (self,setting):
        '''Return the value of @color setting.'''
        return g.app.config.getColor(self.c,setting)

    def getCommands (self):
        '''Return the list of tuples (headline,script) for common @command nodes.'''
        return g.app.config.atCommonCommandsList # unusual.

    def getData (self,setting):
        '''Return a list of non-comment strings in the body text of @data setting.'''
        return g.app.config.getData(self.c,setting)

    def getDirectory (self,setting):
        '''Return the value of @directory setting, or None if the directory does not exist.'''
        return g.app.config.getDirectory(self.c,setting)

    def getFloat (self,setting):
        '''Return the value of @float setting.'''
        return g.app.config.getFloat(self.c,setting)

    def getFontFromParams (self,family,size,slant,weight,defaultSize=12):

        '''Compute a font from font parameters.

        Arguments are the names of settings to be use.
        Default to size=12, slant="roman", weight="normal".

        Return None if there is no family setting so we can use system default fonts.'''

        return g.app.config.getFontFromParams(self.c,
            family, size, slant, weight, defaultSize = defaultSize)

    def getInt (self,setting):
        '''Return the value of @int setting.'''
        return g.app.config.getInt(self.c,setting)

    def getLanguage (self,setting):
        '''Return the value of @string setting.

        The value of this setting should be a language known to Leo.'''
        return g.app.config.getLanguage(self.c,setting)

    def getMenusList (self):
        '''Return the list of entries for the @menus tree.'''
        return g.app.config.getMenusList(self.c) # Changed in Leo 4.5.

    def getOpenWith (self):
        '''Return a list of dictionaries corresponding to @openwith nodes.'''
        return g.app.config.getOpenWith(self.c)

    def getRatio (self,setting):
        '''Return the value of @float setting.
        Warn if the value is less than 0.0 or greater than 1.0.'''
        return g.app.config.getRatio(self.c,setting)

    def getRecentFiles (self):
        '''Return the list of recently opened files.'''
        return g.app.config.getRecentFiles()

    def getShortcut (self,shortcutName):
        '''Return the tuple (rawKey,accel) for shortcutName in @shortcuts tree.'''
        return g.app.config.getShortcut(self.c,shortcutName)

    def getSettingSource(self,setting):
        '''return the name of the file responsible for setting.'''
        return g.app.config.getSettingSource(self.c,setting)

    def getString (self,setting):
        '''Return the value of @string setting.'''
        return g.app.config.getString(self.c,setting)
    #@-node:ekr.20041118053731:Getters (c.configSettings)
    #@+node:ekr.20041118195812:Setters... (c.configSettings)
    #@+node:ekr.20041118195812.3:setRecentFiles (c.configSettings)
    def setRecentFiles (self,files):

        '''Update the recent files list.'''

        # Append the files to the global list.
        g.app.config.appendToRecentFiles(files)
    #@-node:ekr.20041118195812.3:setRecentFiles (c.configSettings)
    #@+node:ekr.20041118195812.2:set & setString
    def set (self,p,setting,val):

        return g.app.config.setString(self.c,setting,val)

    setString = set
    #@-node:ekr.20041118195812.2:set & setString
    #@-node:ekr.20041118195812:Setters... (c.configSettings)
    #@-others
#@-node:ekr.20041118104831.1:class configSettings (leoCommands)
#@+node:ekr.20070615131604:class nodeHistory
class nodeHistory:

    '''A class encapsulating knowledge of visited nodes.'''

    #@    @+others
    #@+node:ekr.20070615131604.1: ctor (nodeHistory)
    def __init__ (self,c):

        self.c = c
        self.beadList = []
            # list of (position,chapter) tuples for
            # nav_buttons and nodenavigator plugins.
        self.beadPointer = -1
        self.trace = False
    #@nonl
    #@-node:ekr.20070615131604.1: ctor (nodeHistory)
    #@+node:ekr.20070615131604.3:canGoToNext/Prev
    def canGoToNextVisited (self):

        if self.trace:
            g.trace(
                self.beadPointer + 1 < len(self.beadList),
                self.beadPointer,len(self.beadList))

        return self.beadPointer + 1 < len(self.beadList)

    def canGoToPrevVisited (self):

        if self.trace:
            g.trace(self.beadPointer > 0,
                self.beadPointer,len(self.beadList))

        return self.beadPointer > 0
    #@-node:ekr.20070615131604.3:canGoToNext/Prev
    #@+node:ekr.20070615132939:clear
    def clear (self):

        self.beadList = []
        self.beadPointer = -1
    #@-node:ekr.20070615132939:clear
    #@+node:ekr.20070615134813:goNext/Prev
    def goNext (self):

        '''Return the next visited node, or None.'''
        if self.beadPointer + 1 < len(self.beadList):
            self.beadPointer += 1
            p,chapter = self.beadList[self.beadPointer]
            self.selectChapter(chapter)
            return p
        else:
            return None

    def goPrev (self):

        '''Return the previous visited node, or None.'''
        if self.beadPointer > 0:
            self.beadPointer -= 1
            p,chapter = self.beadList[self.beadPointer]
            self.selectChapter(chapter)
            return p
        else:
            return None
    #@-node:ekr.20070615134813:goNext/Prev
    #@+node:ekr.20070615132939.1:remove
    def remove (self,p):

        '''Remove an item from the nav_buttons list.'''

        c = self.c
        target = self.beadPointer > -1 and self.beadList[self.beadPointer]

        self.beadList = [z for z in self.beadList
                            if z[0] != p and c.positionExists(z[0])]

        try:
            self.beadPointer = self.beadList.index(target)
        except ValueError:
            self.beadPointer = max(0,self.beadPointer-1)

        if self.trace:
            g.trace('bead list',p.headString())
            g.pr([z[0].headString() for z in self.beadList])
    #@-node:ekr.20070615132939.1:remove
    #@+node:ekr.20070615140032:selectChapter
    def selectChapter (self,chapter):

        c = self.c ; cc = c.chapterController

        if cc and chapter and chapter != cc.getSelectedChapter():
            cc.selectChapterByName(chapter.name)
    #@-node:ekr.20070615140032:selectChapter
    #@+node:ekr.20070615131604.2:update
    def update (self,p):

        c = self.c

        self.beadList = [z for z in self.beadList
                            if c.positionExists(z[0])]

        positions = [z[0] for z in self.beadList]

        try:
            self.beadPointer = positions.index(p)
        except ValueError:
            cc = c.chapterController
            theChapter = cc and cc.getSelectedChapter()
            data = (p.copy(),theChapter)
            self.beadList.append(data)
            self.beadPointer = len(self.beadList)-1

        if self.trace:
            g.trace('bead list',p.headString())
            g.pr([z[0].headString() for z in self.beadList])

    #@-node:ekr.20070615131604.2:update
    #@+node:ekr.20070615140655:visitedPositions
    def visitedPositions (self):

        return [p.copy() for p,chapter in self.beadList]
    #@-node:ekr.20070615140655:visitedPositions
    #@-others
#@-node:ekr.20070615131604:class nodeHistory
#@-others
#@-node:ekr.20031218072017.2810:@thin leoCommands.py
#@-leo

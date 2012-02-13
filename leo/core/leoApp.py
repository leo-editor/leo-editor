# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20031218072017.2608: * @file leoApp.py
#@@first

#@@language python
#@@tabwidth -4
#@@pagewidth 60

import leo.core.leoGlobals as g
import leo.core.leoCache as leoCache
# import leo.core.leoPlugins as leoPlugins
import leo.core.leoVersion as leoVersion

import os
import optparse
import sys
import traceback

#@+others
#@+node:ekr.20120209051836.10241: ** class leoApp
class LeoApp:

    """A class representing the Leo application itself.

    Ivars of this class are Leo's global variables."""

    #@+others
    #@+node:ekr.20031218072017.1416: *3* app.__init__
    def __init__(self):

        # These ivars are Leo's global vars.
        # leoGlobals.py contains global switches to be set by hand.
        
        # Command-line arguments...
        self.batchMode = False          # True: run in batch mode.
        self.gui = None                 # The gui class.
        self.guiArgName = None          # The gui name given in --gui option.
        self.qt_use_tabs = False        # True: allow tabbed main window.
        self.silentMode = False         # True: no signon.
        self.start_fullscreen = False   # For qtGui plugin.
        self.start_maximized = False    # For qtGui plugin.
        self.start_minimized = False    # For qtGui plugin.
        self.translateToUpperCase = False # Never set to True.
        self.useIpython = False         # True: add support for IPython.
        self.use_psyco = False          # True: use psyco optimization.
        self.use_splash_screen = True   # True: put up a splash screen.

        # Debugging & statistics...
        self.count = 0                  # General purpose debugging count.
        self.debug = False              # Enable debugging. (Can be slow.)
        self.debugSwitch = 0            # 0: Brief; 1: Full.
        self.disableSave = False        # May be set by plugins.
        self.positions = 0              # The number of positions generated.
        self.scanErrors = 0             # The number of errors seen by g.scanError.
        self.statsDict = {}             # dict used by g.stat, g.clear_stats, g.print_stats.
        
        # Error messages...
        self.atPathInBodyWarning = None # Set by get_directives_dict.
        self.menuWarningsGiven = False  # True: supress warnings in menu code.
        self.unicodeErrorGiven = True   # True: suppres unicode tracebacks.
        
        # Global directories...
        self.extensionsDir = None   # The leo/extensions directory
        self.globalConfigDir = None # leo/config directory
        self.globalOpenDir = None   # The directory last used to open a file.
        self.homeDir = None         # The user's home directory.
        self.homeLeoDir = None      # The user's home/.leo directory.
        self.loadDir = None         # The leo/core directory.
        self.machineDir = None      # The machine-specific directory.
        
        # Global data...
        self.leoID = None               # The id part of gnx's.
        self.lossage = []               # List of last 100 keystrokes.
        self.numberOfUntitledWindows=0  # Number of opened untitled windows.
        self.windowList = []            # Global list of all frames.
        self.realMenuNameDict = {}      # Translations of menu names.
        
        # Global controller/manager objects...
        self.config = None              # The singleton leoConfig instance.
        self.db = None                  # The singleton leoCacher instance.
        # self.loadManager = None       # The singleton LoadManager instance.
        # self.logManager = None        # The singleton LogManager instance.
        # self.openWithManager = None   # The singleton OpenWithManager instance.
        self.nodeIndices = None         # The singleton nodeIndices instance.
        self.pluginsController = None   # The singleton PluginsManager instance.
        
        # Global status vars...
        
        if 1: #### To be moved to the Commands class...
            self.commandName = None         # The name of the command being executed.
            self.commandInterruptFlag=False # True: command within a command.
                
        self.dragging = False           # True: dragging.
        self.inBridge = False           # True: running from leoBridge module.
        self.inScript = False           # True: executing a script.
        self.initing  = True            # True: we are initiing the app.
        self.killed   = False           # True: we are about to destroy the root window.
        self.quitting = False           # True: quitting.  Locks out some events.
        
        #### To be moved to the LogManager.

        # The global log...
        self.log = None                 # The LeoFrame containing the present log.
        self.logInited = False          # False: all log message go to logWaiting list.
        self.logIsLocked = False        # True: no changes to log are allowed.
        self.logWaiting = []            # List of messages waiting to go to a log.
        self.printWaiting = []          # Queue of messages to be sent to the printer.
        self.signon_printed = False
        
        #### To be moved to OpenWithManager.
        
        # Open with data...
        self.hasOpenWithMenu = False    # True: open with plugin has been loaded.
        self.openWithFiles = []         # List of data used by Open With command.
        self.openWithFileNum = 0        # Number of Open-With temp file names.
        self.openWithTable = None       # Passed to createOpenWithMenuFromTable.
        
        #### To be moved to to the pluginsController.

        # Plugins and event handlers...
        self.afterHandler = None
        self.hookError = False      # True: suppress further calls to hooks.
        self.hookFunction = None    # Application wide hook function.
        self.idle_imported = False  # True: we have done an import idle
        self.idleTimeDelay = 100    # Delay in msec between calls to "idle time" hook.
        self.idleTimeHook = False   # True: the global idleTimeHookHandler will reshedule itself.
        
        # Support for scripting...
        self.searchDict = {}    # For communication between find/change scripts.
        self.scriptDict = {}    # For use by scripts.

        # Unit testing...
        self.isExternalUnitTest = False # True: we are running a unit test externally.
        self.unitTestDict = {}          # For communication between unit tests and code.
        self.unitTestGui = None         # A way to override the gui in external unit tests.
        self.unitTesting = False        # True if unit testing.
        self.unitTestMenusDict = {}
            # Created in leoMenu.createMenuEntries for a unit test.
            # keys are command names. values are sets of strokes.

        #@+<< Define global constants >>
        #@+node:ekr.20031218072017.1417: *4* << define global constants >>
        # self.prolog_string = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"

        self.prolog_prefix_string = "<?xml version=\"1.0\" encoding="
        self.prolog_postfix_string = "?>"
        self.prolog_namespace_string = \
            'xmlns:leo="http://edreamleo.org/namespaces/leo-python-editor/1.1"'
        #@-<< Define global constants >>
        #@+<< Define global data structures >>
        #@+node:ekr.20031218072017.368: *4* << define global data structures >> (leoApp.py)
        # Internally, lower case is used for all language names.
        self.language_delims_dict = {
            # Keys are languages, values are 1,2 or 3-tuples of delims.
            "ada"           : "--",
            "batch"         : "REM_", # Use the REM hack.
            "actionscript"  : "// /* */", #jason 2003-07-03
            "autohotkey"    : "; /* */", #TL - AutoHotkey language
            "c"             : "// /* */", # C, C++ or objective C.
            "config"        : "#", # Leo 4.5.1
            "csharp"        : "// /* */", # C#
            "cpp"           : "// /* */",# C++.
            "css"           : "/* */", # 4/1/04
            "cweb"          : "@q@ @>", # Use the "cweb hack"
            "cython"        : "#",
            "elisp"         : ";",
            "forth"         : "\\_ _(_ _)", # Use the "REM hack"
            "fortran"       : "C",
            "fortran90"     : "!",
            "haskell"       : "--_ {-_ _-}",
            "haxe"          : "//",
            "html"          : "<!-- -->",
            "ini"           : ";",
            "java"          : "// /* */",
            "javascript"    : "// /* */", # EKR: 2011/11/12: For javascript import test.
            "javaserverpage": "<%-- --%>", # EKR: 2011/11/25
            "kshell"        : "#", # Leo 4.5.1.
            "latex"         : "%",
            "lisp"          : ";", # EKR: 2010/09/29
            "lua"           : "--",  # ddm 13/02/06
            "matlab"        : "%", # EKR: 2011/10/21
            "nsi"           : ";", # EKR: 2010/10/27
            "noweb"         : "%", # EKR: 2009-01-30. Use Latex for doc chunks.
            "pascal"        : "// { }",
            "perl"          : "#",
            "perlpod"       : "# __=pod__ __=cut__", # 9/25/02: The perlpod hack.
            "php"           : "// /* */", # 6/23/07: was "//",
            "plain"         : "#", # We must pick something.
            "plsql"         : "-- /* */", # SQL scripts qt02537 2005-05-27
            "python"        : "#",
            "rapidq"        : "'", # fil 2004-march-11
            "rebol"         : ";",  # jason 2003-07-03
            "rest"          : ".._",
            "rst"           : ".._",
            "ruby"          : "#",  # thyrsus 2008-11-05
            "scala"         : "// /* */",
            "shell"         : "#",  # shell scripts
            "tcltk"         : "#",
            "tex"           : "%", # Bug fix: 2008-1-30: Fixed Mark Edginton's bug.
            "unknown"       : "#", # Set when @comment is seen.
            "unknown_language" : '#--unknown-language--',
                # For unknown extensions in @shadow files.
            "vim"           : "\"",
            "vimoutline"    : "#",  #TL 8/25/08 Vim's outline plugin
            "xml"           : "<!-- -->",
            "xslt"          : "<!-- -->",
        }

        # Used only by c.getOpenWithExt.
        self.language_extension_dict = {
            # Keys are languages, values are extensions.
            "ada"           : "ada",
            "actionscript"  : "as", #jason 2003-07-03
            "autohotkey"    : "ahk", #TL - AutoHotkey language
            "batch"         : "bat", # Leo 4.5.1.
            "c"             : "c",
            "config"        : "cfg",
            "cpp"           : "cpp",
            "css"           : "css", # 4/1/04
            "cweb"          : "w",
            #"cython"        : "pyd",
            #"cython"        : "pyi",
            "cython"        : "pyx", # Only one extension is valid at present.
            "elisp"         : "el",
            "forth"         : "forth",
            "fortran"       : "f",
            "fortran90"     : "f90",
            "haskell"       : "hs",
            "haxe"          : "hx",
            "html"          : "html",
            "ini"           : "ini",
            "java"          : "java",
            "javascript"    : "js", # EKR: 2011/11/12: For javascript import test.
            "javaserverpage": "jsp", # EKR: 2011/11/25
            "kshell"        : "ksh", # Leo 4.5.1.
            "latex"         : "tex", # 1/8/04
            "lua"           : "lua",  # ddm 13/02/06
            "matlab"        : "m", # EKR: 2011/10/21
            "nsi"           : "nsi", # EKR: 2010/10/27
            "noweb"         : "nw",
            "pascal"        : "p",
            "perl"          : "pl",      # 11/7/05
            "perlpod"       : "pod",  # 11/7/05
            "php"           : "php",
            "plain"         : "txt",
            "python"        : "py",
            "plsql"         : "sql", # qt02537 2005-05-27
            "rapidq"        : "bas", # fil 2004-march-11
            "rebol"         : "r",    # jason 2003-07-03
            # "rst"           : "rst", # caught by pylint.
            "rst"           : "rest",
            "ruby"          : "rb",   # thyrsus 2008-11-05
            "scala"         : "scala",
            "shell"         : "sh",   # DS 4/1/04
            "tex"           : "tex",
            "tcltk"         : "tcl",
            "unknown"       : "txt", # Set when @comment is seen.
            "vim"           : "vim",
            "vimoutline"    : "otl",  #TL 8/25/08 Vim's outline plugin
            "xml"           : "xml",
            "xslt"          : "xsl",
        }

        self.extension_dict = {
            # Keys are extensions, values are languages.
            "ada"   : "ada",
            "adb"   : "ada",
            "ahk"   : "autohotkey",  # EKR: 2009-01-30.
            "as"    : "actionscript",
            "bas"   : "rapidq",
            "bat"   : "batch",
            "c"     : "c",
            "cfg"   : "config",
            "cpp"   : "cpp",
            "css"   : "css",
            "el"    : "elisp",
            "forth" : "forth",
            "f"     : "fortran",
            "f90"   : "fortran90",
            "h"     : "c",
            "html"  : "html",
            "hs"    : "haskell",
            "ini"   : "ini",
            "java"  : "java",
            "js"    : "javascript", # EKR: 2011/11/12: For javascript import test.
            "jsp"   : "javaserverpage", # EKR: 2011/11/25: For @shadow.
            "ksh"   : "kshell", # Leo 4.5.1.
            "lua"   : "lua",  # ddm 13/02/06
            "m"     : "matlab", # EKR 2011/10/21
            "nsi"   : "nsi", # EKR: 2010/10/27
            "nw"    : "noweb",
            "otl"   : "vimoutline",  #TL 8/25/08 Vim's outline plugin
            "p"     : "pascal",
            "pl"    : "perl",   # 11/7/05
            "pod"   : "perlpod", # 11/7/05
            "php"   : "php",
            "py"    : "python",
            "pyd"   : "cython",
            "pyi"   : "cython",
            "pyx"   : "cython",
            "sql"   : "plsql", # qt02537 2005-05-27
            "r"     : "rebol",
            "rb"    : "ruby", # thyrsus 2008-11-05
            "rest"  : "rst",
            "rst"   : "rst",
            "scala" : "scala",
            "sh"    : "shell",
            "tex"   : "tex",
            "txt"   : "plain",
            "tcl"   : "tcltk",
            "vim"   : "vim",
            "w"     : "cweb",
            "xml"   : "xml",
            "xsl"   : "xslt",
            "hx"    : "haxe",
        }

        # Extra language extensions, used to associate extensions with mode files.
        # Used by importCommands.languageForExtension.
        # Keys are extensions, values are corresponding mode file (without .py)
        # A value of 'none' is a signal to unit tests that no extension file exists.
        self.extra_extension_dict = {
            'actionscript': 'actionscript',
            'ada'   : 'ada95',
            'adb'   : 'none', # ada??
            'awk'   : 'awk',
            'bas'   : 'none', # rapidq
            'bat'   : 'none', # batch
            'cfg'   : 'none', # Leo 4.5.1
            'cpp'   : 'c',
            'el'    : 'lisp',
            'f'     : 'fortran90',
            'hx'    : 'none',
            'ksh'   : 'none', # Leo 4.5.1
            'nsi'   : 'none', # Leo 4.8.
            'nw'    : 'none', # noweb.
            'otl'   : 'none', # vimoutline.
            'pod'   : 'perl',
            'tcl'   : 'tcl',
            'unknown_language': 'none',
            'w'     : 'none', # cweb
        }

        self.global_commands_dict = {}
        #@-<< Define global data structures >>
    #@+node:ekr.20031218072017.2609: *3* app.closeLeoWindow
    def closeLeoWindow (self,frame):

        """Attempt to close a Leo window.

        Return False if the user veto's the close."""

        c = frame.c

        # g.trace('frame',frame,g.callers(4))

        c.endEditing() # Commit any open edits.

        if c.promptingForClose:
            # There is already a dialog open asking what to do.
            return False

        g.app.config.writeRecentFilesFile(c)
            # Make sure .leoRecentFiles.txt is written.

        if c.changed:
            c.promptingForClose = True
            veto = frame.promptForSave()
            c.promptingForClose = False
            if veto: return False

        g.app.setLog(None) # no log until we reactive a window.

        g.doHook("close-frame",c=c)
            # This may remove frame from the window list.

        if frame in g.app.windowList:
            g.app.destroyWindow(frame)

        if g.app.windowList:
            # Pick a window to activate so we can set the log.
            frame = g.app.windowList[0]
            frame.deiconify()
            frame.lift()
            frame.c.setLog()
            master = hasattr(frame.top,'leo_master') and frame.top.leo_master
            if master: # 2011/11/21: selecting the new tab ensures focus is set.
                # frame.top.leo_master is a TabbedTopLevel.
                master.select(frame.c)
            frame.c.bodyWantsFocus()
            frame.c.outerUpdate()
        elif not g.app.unitTesting:
            g.app.finishQuit()

        return True # The window has been closed.
    #@+node:ville.20090602181814.6219: *3* app.commanders
    def commanders(self):
        """ Return list of currently active controllers """

        return [f.c for f in g.app.windowList]    
    #@+node:ekr.20090717112235.6007: *3* app.computeSignon
    def computeSignon (self):

        app = self
        build,date  = leoVersion.build,leoVersion.date
        guiVersion  = app.gui and app.gui.getFullVersion() or 'no gui!'
        leoVer      = leoVersion.version
        n1,n2,n3,junk,junk=sys.version_info

        if sys.platform.startswith('win'):
            sysVersion = 'Windows '
            try:
                v = os.sys.getwindowsversion()
                sysVersion += ', '.join([str(z) for z in v])
            except Exception:
                pass

        else: sysVersion = sys.platform

        app.signon = 'Leo %s, build %s, %s' % (
            leoVer,build,date)
        app.signon2 = 'Python %s.%s.%s, %s\n%s' % (
            n1,n2,n3,guiVersion,sysVersion)
    #@+node:ekr.20100831090251.5838: *3* app.createXGui
    #@+node:ekr.20100831090251.5840: *4* app.createCursesGui
    def createCursesGui (self,fileName='',verbose=False):

        app = self

        app.pluginsController.loadOnePlugin('leo.plugins.cursesGui',verbose=verbose)
    #@+node:ekr.20090619065122.8593: *4* app.createDefaultGui
    def createDefaultGui (self,fileName='',verbose=False):

        """A convenience routines for plugins to create the default gui class."""

        app = self ; argName = app.guiArgName

        # This method can be called twice if we had to get .leoID.txt.
        if app.gui: return

        if argName in ('qt','qttabs'): # 2011/06/15.
            app.createQtGui(fileName,verbose=verbose)
        elif argName == 'null':
            app.createNullGui()
        elif argName == 'curses':
            app.createCursesGui()

        if not app.gui:
            print('Leo requires Qt to be installed.')
    #@+node:ekr.20090202191501.5: *4* app.createNullGui
    def createNullGui (self):

        # Don't import this at the top level:
        # it might interfere with Leo's startup logic.

        app = self

        try:
            import leo.core.leoGui as leoGui
        except ImportError:
            leoGui = None

        if leoGui:
            app.gui = leoGui.nullGui("nullGui")
    #@+node:ekr.20031218072017.1938: *4* app.createNullGuiWithScript
    def createNullGuiWithScript (self,script=None):

        app = self

        try:
            import leo.core.leoGui as leoGui
        except ImportError:
            leoGui = None

        if leoGui:
            app.batchMode = True
            app.gui = leoGui.nullGui("nullGui")
            app.gui.setScript(script)
    #@+node:ekr.20090202191501.1: *4* app.createQtGui
    def createQtGui (self,fileName='',verbose=False):

        # Do NOT omit fileName param: it is used in plugin code.

        """A convenience routines for plugins to create the Qt gui class."""

        app = self

        try:
            # Take care to try the same imports as in qtGui.py.
            import PyQt4.QtCore
            import PyQt4.QtGui            
            import leo.plugins.qtGui as qtGui
        except ImportError:
            qtGui = None

        if qtGui:
            qtGui.init()
            if app.gui and fileName and verbose:
                print('qtGui created in %s' % fileName)
    #@+node:ekr.20090126063121.3: *4* app.createWxGui
    def createWxGui (self,fileName='',verbose=False):

        # Do NOT omit fileName param: it is used in plugin code.

        """A convenience routines for plugins to create the wx gui class."""

        app = self

        app.pluginsController.loadOnePlugin ('leo.plugins.wxGui',verbose=verbose)

        if fileName and verbose:

            print('wxGui created in %s' % fileName)
    #@+node:ekr.20031218072017.2612: *3* app.destroyAllOpenWithFiles
    def destroyAllOpenWithFiles (self):

        """Try to remove temp files created with the Open With command.

        This may fail if the files are still open.

        Called by g.app.finishQuit"""

        # We can't use g.es here because the log stream no longer exists.

        for theDict in self.openWithFiles[:]:
            g.app.destroyOpenWithFileWithDict(theDict)

        # Delete the list so the gc can recycle Leo windows!
        g.app.openWithFiles = []
    #@+node:ekr.20031218072017.2613: *3* app.destroyOpenWithFilesForFrame
    def destroyOpenWithFilesForFrame (self,frame):

        """Close all "Open With" files associated with frame

        Called by app.destroyWindow.
        """

        # Make a copy of the list: it may change in the loop.
        openWithFiles = g.app.openWithFiles

        for theDict in openWithFiles[:]: # 6/30/03
            c = theDict.get("c")
            if c.frame == frame:
                g.app.destroyOpenWithFileWithDict(theDict)
    #@+node:ekr.20031218072017.2614: *3* app.destroyOpenWithFileWithDict
    def destroyOpenWithFileWithDict (self,theDict):

        '''
        A helper for app.destroyAllOpenWithFiles and
        app.destroyOpenWithFilesForFrame.
        '''

        path = theDict.get("path")
        if path and g.os_path_exists(path):
            try:
                os.remove(path)
                g.pr("deleting temp file: %s" % g.shortFileName(path))
            except:
                g.pr("can not delete temp file: %s" % path)

        # Remove theDict from the list so the gc can recycle the Leo window!
        g.app.openWithFiles.remove(theDict)
    #@+node:ekr.20031218072017.2615: *3* app.destroyWindow
    def destroyWindow (self,frame):

        # g.trace(frame in g.app.windowList,frame)
        g.app.destroyOpenWithFilesForFrame(frame)

        if frame in g.app.windowList:
            # g.trace(g.app.windowList)
            g.app.windowList.remove(frame)

        # force the window to go away now.
        # Important: this also destroys all the objects of the commander.
        frame.destroySelf()
    #@+node:ekr.20031218072017.1732: *3* app.finishQuit
    def finishQuit(self):

        # forceShutdown may already have fired the "end1" hook.
        if not g.app.killed:
            g.doHook("end1")

        self.destroyAllOpenWithFiles()

        if g.app.gui:
            g.app.gui.destroySelf()

        # Don't use g.trace!
        # print('app.finishQuit: setting g.app.killed',g.callers())

        g.app.killed = True
            # Disable all further hooks and events.
            # Alas, "idle" events can still be called
            # even after the following code.

        if g.app.afterHandler:
            g.app.afterHandler = None
    #@+node:ekr.20031218072017.2616: *3* app.forceShutdown
    def forceShutdown (self):

        """Forces an immediate shutdown of Leo at any time.

        In particular, may be called from plugins during startup."""

        # Wait until everything is quiet before really quitting.
        g.doHook("end1")

        self.log = None # Disable writeWaitingLog
        self.killed = True # Disable all further hooks.

        for w in self.windowList[:]:
            self.destroyWindow(w)

        self.finishQuit()
    #@+node:ekr.20120211121736.10809: *3* app.init (NEW)
    def init (self):
        
        import leo.core.leoCache as leoCache
        import leo.core.leoConfig as leoConfig
        import leo.core.leoNodes as leoNodes
        
        app = self

        # Force the user to set g.app.leoID.
        app.setLeoID()
        app.config = leoConfig.configClass()
        app.nodeIndices = leoNodes.nodeIndices(g.app.leoID)
        app.pluginsController.finishCreate()
        
        #### Do this early.  We no longer read files twice.
        # Fixes bug 670108.
        app.db = leoCache.cacher().initGlobalDB()
    #@+node:ekr.20031218072017.2188: *3* app.newLeoCommanderAndFrame & helper
    def newLeoCommanderAndFrame(self,
        fileName=None,
        relativeFileName=None,
        gui=None,initEditCommanders=True,updateRecentFiles=True):

        """Create a commander and its view frame for the Leo main window."""

        app = self

        import leo.core.leoCommands as leoCommands

        if not fileName: fileName = ''
        if not relativeFileName: relativeFileName = ''
        if not gui: gui = g.app.gui
        
        title = app.computeWindowTitle(fileName)

        # g.trace(fileName,relativeFileName)

        # Create an unfinished frame to pass to the commanders.
        frame = gui.createLeoFrame(title)

        # Create the commander and its subcommanders.
        # This takes about 3/4 sec when called by the leoBridge module.
        c = leoCommands.Commands(frame,fileName,
            relativeFileName=relativeFileName)

        if not app.initing:
            g.doHook("before-create-leo-frame",c=c)
                # Was 'onCreate': too confusing.

        frame.finishCreate(c)
        c.finishCreate(initEditCommanders)

        # Finish initing the subcommanders.
        c.undoer.clearUndoState() # Menus must exist at this point.

        return c,frame
    #@+node:ekr.20031218072017.2189: *4* app.computeWindowTitle
    def computeWindowTitle(self,fileName):
        
        '''Set the window title and fileName.'''

        if fileName:
            title = g.computeWindowTitle(fileName)
        else:
            s = "untitled"
            n = g.app.numberOfUntitledWindows
            if n > 0:
                s += str(n)
            title = g.computeWindowTitle(s)
            g.app.numberOfUntitledWindows = n+1

        return title
    #@+node:ekr.20031218072017.2617: *3* app.onQuit
    def onQuit (self,event=None):

        '''Exit Leo, prompting to save unsaved outlines first.'''

        g.app.quitting = True
        # g.trace('True')

        while g.app.windowList:
            w = g.app.windowList[0]
            if not g.app.closeLeoWindow(w):
                break

        if g.app.windowList:
            g.app.quitting = False # If we get here the quit has been disabled.
    #@+node:ville.20090620122043.6275: *3* app.setGlobalDb
    def setGlobalDb(self):
        """ Create global pickleshare db

        Usable by::

            g.app.db['hello'] = [1,2,5]

        """


        # Fixes bug 670108.
        g.app.db = leoCache.cacher().initGlobalDB()
    #@+node:ekr.20031218072017.1978: *3* app.setLeoID
    def setLeoID (self,verbose=True):
        
        tag = ".leoID.txt"
        homeLeoDir = g.app.homeLeoDir
        globalConfigDir = g.app.globalConfigDir
        loadDir = g.app.loadDir

        verbose = not g.app.unitTesting
        #@+<< return if we can set leoID from sys.leoID >>
        #@+node:ekr.20031218072017.1979: *4* << return if we can set leoID from sys.leoID>>
        # This would be set by in Python's sitecustomize.py file.

        # Use hasattr & getattr to suppress pylint warning.
        # Use a "non-constant" attribute to suppress another warning!

        nonConstantAttr = "leoID"

        if hasattr(sys,nonConstantAttr):
            g.app.leoID = getattr(sys,nonConstantAttr)
            if verbose and not g.app.silentMode and not g.app.unitTesting:
                g.es_print("leoID=",g.app.leoID,spaces=False,color='red')
            # Careful: periods in the id field of a gnx will corrupt the .leo file!
            g.app.leoID = g.app.leoID.replace('.','-')
            return
        else:
            g.app.leoID = None
        #@-<< return if we can set leoID from sys.leoID >>
        #@+<< return if we can set leoID from "leoID.txt" >>
        #@+node:ekr.20031218072017.1980: *4* << return if we can set leoID from "leoID.txt" >>
        for theDir in (homeLeoDir,globalConfigDir,loadDir):
            # N.B. We would use the _working_ directory if theDir is None!
            if theDir:
                try:
                    fn = g.os_path_join(theDir,tag)
                    f = open(fn,'r')
                    s = f.readline()
                    f.close()
                    if s and len(s) > 0:
                        g.app.leoID = s.strip()
                        # Careful: periods in the id field of a gnx
                        # will corrupt the .leo file!
                        g.app.leoID = g.app.leoID.replace('.','-')
                        if verbose and not g.app.silentMode and not g.app.unitTesting:
                            g.es('leoID=',g.app.leoID,' (in ',theDir,')',
                                spaces=False,color="red")
                        return
                    elif verbose and not g.app.unitTesting:
                        g.es('empty ',tag,' (in ',theDir,')',spaces=False,
                            color = "red")
                except IOError:
                    g.app.leoID = None
                except Exception:
                    g.app.leoID = None
                    g.es_print('unexpected exception in app.setLeoID',color='red')
                    g.es_exception()
        #@-<< return if we can set leoID from "leoID.txt" >>
        #@+<< return if we can set leoID from os.getenv('USER') >>
        #@+node:ekr.20060211140947.1: *4* << return if we can set leoID from os.getenv('USER') >>
        try:
            theId = os.getenv('USER')
            if theId:
                if verbose and not g.app.unitTesting:
                    g.es("setting leoID from os.getenv('USER'):",
                        repr(theId),color='blue')
                g.app.leoID = theId
                # Careful: periods in the id field of a gnx
                # will corrupt the .leo file!
                g.app.leoID = g.app.leoID.replace('.','-')
                return

        except Exception:
            pass
        #@-<< return if we can set leoID from os.getenv('USER') >>
        #@+<< put up a dialog requiring a valid id >>
        #@+node:ekr.20031218072017.1981: *4* << put up a dialog requiring a valid id >>
        # 2011/06/13: Don't put up a splash screen.
        # It would obscure the coming dialog.
        g.app.use_splash_screen = False

        # New in 4.1: get an id for gnx's.  Plugins may set g.app.leoID.
        if g.app.gui is None:
            # Create the Qt gui if it exists.
            g.app.createDefaultGui(fileName='g.app.setLeoId',verbose=True)

        if g.app.gui is None: # Neither gui could be created: this should never happen.
            print("Please enter LeoID (e.g. your username, 'johndoe'...)")
            if g.isPython3: # 2010/02/04.
                leoid = input('LeoID: ')
            else:
                leoid = raw_input('LeoID: ')
        else:
            leoid = g.app.gui.runAskLeoIDDialog()

        # Bug fix: 2/6/05: put result in g.app.leoID.
        g.app.leoID = leoid

        # Careful: periods in the id field of a gnx will corrupt the .leo file!
        g.app.leoID = g.app.leoID.replace('.','-')

        # g.trace(g.app.leoID)
        g.es('leoID=',repr(g.app.leoID),spaces=False,color="blue")
        #@-<< put up a dialog requiring a valid id >>
        #@+<< attempt to create leoID.txt >>
        #@+node:ekr.20031218072017.1982: *4* << attempt to create leoID.txt >> (changed)
        for theDir in (homeLeoDir,globalConfigDir,loadDir):
            # N.B. We would use the _working_ directory if theDir is None!
            if theDir:
                try:
                    fn = g.os_path_join(theDir,tag)
                    f = open(fn,'w')
                    s = g.app.leoID
                    if not g.isPython3: # 2010/08/27
                        s = g.toEncodedString(s,encoding='utf-8',reportErrors=True)
                    f.write(s)
                    f.close()
                    if g.os_path_exists(fn):
                        g.es_print('',tag,'created in',theDir,color='red')
                        return
                except IOError:
                    pass

                g.es('can not create',tag,'in',theDir,color='red')
        #@-<< attempt to create leoID.txt >>
    #@+node:ekr.20031218072017.1847: *3* app.setLog, lockLog, unlocklog
    def setLog (self,log):

        """set the frame to which log messages will go"""

        # print("app.setLog:",log,g.callers())
        if not self.logIsLocked:
            self.log = log

    def lockLog(self):
        """Disable changes to the log"""
        self.logIsLocked = True

    def unlockLog(self):
        """Enable changes to the log"""
        self.logIsLocked = False
    #@+node:ekr.20031218072017.2619: *3* app.writeWaitingLog
    def writeWaitingLog (self,c):

        trace = False
        app = self
        
        if trace:
            # Do not call g.es, g.es_print, g.pr or g.trace here!
            print('** writeWaitingLog','silent',app.silentMode,c.shortFileName())
            # print('writeWaitingLog',g.callers())
            # import sys ; print('writeWaitingLog: argv',sys.argv)

        if not c or not c.exists:
            return

        if g.unitTesting:
            app.printWaiting = []
            app.logWaiting = []
            g.app.setLog(None) # Prepare to requeue for other commanders.
            return

        table = [
            ('Leo Log Window','red'),
            (app.signon,'black'),
            (app.signon2,'black'),
        ]
        table.reverse()

        c.setLog() # 2010/10/20
        app.logInited = True # Prevent recursive call.
        
        if not app.signon_printed:
            app.signon_printed = True
            if not app.silentMode: # 2011/11/02:
                print('')
                print('** isPython3: %s' % g.isPython3)
                if not g.enableDB:
                    print('** caching disabled')
                print(app.signon)
                print(app.signon2)
        if not app.silentMode: # 2011/11/02:
            for s in app.printWaiting:
                print(s)
        app.printWaiting = []

        if not app.silentMode:  # 2011/11/02:
            for s,color in table:
                app.logWaiting.insert(0,(s+'\n',color),)
            for s,color in app.logWaiting:
                g.es('',s,color=color,newline=0)
                    # The caller must write the newlines.
        app.logWaiting = []

        # Essential when opening multiple files...
        
        g.app.setLog(None) 
    #@-others
#@+node:ekr.20120209051836.10242: ** class LoadManager
class LoadManager:
    
    '''A class to manage loading .leo files, including configuration files.'''
    
    #@+others
    #@+node:ekr.20120209051836.10285: *3*  lm.ctor
    def __init__ (self,args,fileName,pymacs):
        
        # Important: it is valid to use g here.
        
        # Copy the args.
        self.args = args
        self.fn = fileName
        self.pymacs = pymacs

        # The loaded commanders...
        self.loaded_commanders = []
        self.loaded_my_leo_settings = None
        self.loaded_leo_settings = None
      
        # Settings files & commanders.
        self.leoSettingsName = None     # Full, absolute path to leoSettings.leo.
        self.leoSettings_c = None       # Commander of leoSettings.leo.
        self.myLeoSettingsName = None   # Full, absolute path to myLeoSettings.leo.
        self.myLeoSettigns_c = None     # Commander of myLeoSettings.leo.
        
        # Ivars corresponding to command-line arguments...
            # g.app.batchMode           Set in createNullGuiWithScript
            # g.app.gui = None          The gui class.
            # g.app.guiArgName          The gui name given in --gui option.
            # g.app.qt_use_tabs                
            # g.app.silentMode         
            # g.app.start_fullscreen   
            # g.app.start_maximized    .
            # g.app.start_minimized
            # g.app.useIpython
            # g.app.use_splash_screen
            # g.enableDB                --no-cache
        
        # Ivars corresponding to user options....
        self.files = []             # List of files to be loaded.
        self.script = None          # The fileName of a script, or None.
        self.script_name = None
        self.script_path = None
        self.script_path_w = None
        self.screenshot_fn = None
        self.selectHeadline = None
        self.versionFlag = False
        self.windowFlag = False
        self.windowSize = None
        
    #@+node:ekr.20120211121736.10812: *3* File & directory utils
    #@+node:ekr.20120211121736.10771: *4* lm.completeFileName
    def completeFileName (self,fn):

        fn = g.toUnicode(fn)
        fn = g.os_path_finalize(fn)

        # 2011/10/12: don't add .leo to *any* file.
        return fn
    #@+node:ekr.20120211121736.10773: *4* lm.computeFilesList
    def computeFilesList(self):
        
        lm = self

        files = []
        fn = lm.fn
        if fn and fn not in files:
            files.append(fn)

        for arg in sys.argv[1:]:
            if not arg.startswith('-') and arg not in files:
                files.append(arg)

        files = [lm.completeFileName(z) for z in files]
        return files
    #@+node:ekr.20120209051836.10372: *4* lm.computeLeoSettingsPath (New)
    def computeLeoSettingsPath (self):
        
        '''Return the full path to leoSettings.leo.'''
        
        trace = True ; verbose = True
        lm = self

        # Use leoSettings.leo if it appears explicitly in the list of files.
        for fn in lm.files:
            base_fn = g.os_path_basename(fn)
            if base_fn.lower() == 'leosettings.leo':
                path = g.os_path_finalize(lm.fn)
                if g.os_path_exists(path):
                    if trace: g.trace(path)
                    return path

        seen,table = [],[]
        for path,localFlag in lm.configPlacesTable():
            if trace and verbose:
                g.trace('exists',g.os_path_exists(path),path)
            if path and g.os_path_exists(path):
                # Make sure we mark files seen no matter how they are specified.
                path = g.os_path_realpath(g.os_path_finalize(path))
                if path.lower() not in seen:
                    seen.append(path.lower())
                    table.append((path,localFlag),)

        if trace: print(repr(lm.fn),'table:',g.listToString(table))
        return table


        
        

        # if fileName:
            # if fileName.lower().endswith('leosettings.leo'):
                # # 2011/02/28: don't read leoSettings.leo or myLeoSetings.leo twice.
                # # This allows myLeoSettings.leo to take precedence.
                # table1 = []
            # else:
                # path = g.os_path_finalize(fileName)
                # theDir = g.os_path_dirname(fileName)
                # myLocalConfigFile = g.os_path_join(theDir,'myLeoSettings.leo')
                # local_table = (
                    # (localConfigFile,False),
                    # (myLocalConfigFile,False),
                # )
                # if trace and verbose:
                    # g.trace('localConfigFile:  ',localConfigFile)
                    # g.trace('myLocalConfigFile:',myLocalConfigFile)
        
                # table1 = [z for z in local_table if z not in global_table]
                # table1.append((path,True),)
        # else:
            # table1 = global_table

        # seen = [] ; table = []
        # for path,localFlag in table1:
            # if trace and verbose: g.trace('exists',g.os_path_exists(path),path)
            # if path and g.os_path_exists(path):
                # # Make sure we mark files seen no matter how they are specified.
                # path = g.os_path_realpath(g.os_path_finalize(path))
                # if path.lower() not in seen:
                    # seen.append(path.lower())
                    # table.append((path,localFlag),)
        # if trace: g.trace(repr(fileName),'table:',g.listToString(table))
        # return table

    #@+node:ekr.20120209051836.10373: *4* lm.computeMyLeoSettingsPath (New)
    def computeMyLeoSettingsPath (self):
        
        '''Return the full path to myLeoSettings.leo.'''
        
        trace = False
        lm = self
        
        for fn in lm.files:
            base_fn = g.os_path_basename(fn)
            if base_fn.lower() == 'leosettings.leo':
                path = g.os_path_finalize(lm.fn)
                if g.os_path_exists(path):
                    if trace: g.trace(path)
                    return path
    #@+node:ekr.20120209051836.10252: *4* lm.computeStandardDirectories & helpers
    def computeStandardDirectories(self):

        '''Compute the locations of standard directories and
        set the corresponding ivars.'''
        
        lm = self

        g.app.loadDir           = lm.computeLoadDir()
        g.app.leoDir            = lm.computeLeoDir()
        g.app.homeDir           = lm.computeHomeDir()
        g.app.homeLeoDir        = lm.computeHomeLeoDir()
        g.app.globalConfigDir   = lm.computeGlobalConfigDir()
        
        g.app.extensionsDir = g.os_path_finalize_join(g.app.loadDir,'..','extensions')
        g.app.testDir       = g.os_path_finalize_join(g.app.loadDir,'..','test')
            
        # Full path to settings files.
        #### lm.leoSettingsName   = lm.computeLeoSettingsPath()
        #### lm.myLeoSettingsName = lm.computeMyLeoSettingsPath()
    #@+node:ekr.20120209051836.10253: *5* lm.computeGlobalConfigDir
    def computeGlobalConfigDir(self):
        
        lm = self

        # To avoid pylint complaints that sys.leo_config_directory does not exist.
        leo_config_dir = (
            hasattr(sys,'leo_config_directory') and
            getattr(sys,'leo_config_directory') or None)

        if leo_config_dir:
            theDir = leo_config_dir
        else:
            theDir = g.os_path_join(g.app.loadDir,"..","config")

        if theDir:
            theDir = g.os_path_finalize(theDir)

        if (
            not theDir or
            not g.os_path_exists(theDir) or
            not g.os_path_isdir(theDir)
        ):
            theDir = None

        # g.trace(theDir)
        return theDir
    #@+node:ekr.20120209051836.10254: *5* lm.computeHomeDir
    def computeHomeDir(self):

        """Returns the user's home directory."""
        
        home = os.path.expanduser("~")
            # Windows searches the HOME, HOMEPATH and HOMEDRIVE
            # environment vars, then gives up.

        if home and len(home) > 1 and home[0]=='%' and home[-1]=='%':
            # Get the indirect reference to the true home.
            home = os.getenv(home[1:-1],default=None)

        if home:
            # Important: This returns the _working_ directory if home is None!
            # This was the source of the 4.3 .leoID.txt problems.
            home = g.os_path_finalize(home)
            if (
                not g.os_path_exists(home) or
                not g.os_path_isdir(home)
            ):
                home = None

        # g.trace(home)
        return home
    #@+node:ekr.20120209051836.10260: *5* lm.computeHomeLeoDir
    def computeHomeLeoDir (self):
        
        lm = self
        
        homeLeoDir = g.os_path_finalize_join(g.app.homeDir,'.leo')
        
        if not g.os_path_exists(homeLeoDir):
            g.makeAllNonExistentDirectories(homeLeoDir,force=True)
            
        # g.trace('homeLeoDir',homeLeoDir)
        return homeLeoDir
    #@+node:ekr.20120209051836.10255: *5* lm.computeLeoDir
    def computeLeoDir (self):
        
        lm = self

        loadDir = g.app.loadDir
        theDir  = g.os_path_dirname(loadDir)

        if 0: # xxx remove this, we don't want to have this in sys.path
            if theDir not in sys.path:
                sys.path.append(theDir)

        # g.trace(theDir)
        return theDir
    #@+node:ekr.20120209051836.10256: *5* lm.computeLoadDir
    def computeLoadDir(self):

        """Returns the directory containing leo.py."""

        import sys

        try:
            # Fix a hangnail: on Windows the drive letter returned by
            # __file__ is randomly upper or lower case!
            # The made for an ugly recent files list.
            path = g.__file__ # was leo.__file__
            # g.trace(repr(path))
            if path:
                # Possible fix for bug 735938:
                # Do the following only if path exists.
                #@+<< resolve symlinks >>
                #@+node:ekr.20120209051836.10257: *6* << resolve symlinks >>
                if path.endswith('pyc'):
                    srcfile = path[:-1]
                    if os.path.islink(srcfile):
                        path = os.path.realpath(srcfile)    
                #@-<< resolve symlinks >>
                if sys.platform=='win32':
                    if len(path) > 2 and path[1]==':':
                        # Convert the drive name to upper case.
                        path = path[0].upper() + path[1:]
            
                
                path = g.os_path_finalize(path)
                loadDir = g.os_path_dirname(path)
            else: loadDir = None

            if (
                not loadDir or
                not g.os_path_exists(loadDir) or
                not g.os_path_isdir(loadDir)
            ):
                loadDir = os.getcwd()
                # From Marc-Antoine Parent.
                if loadDir.endswith("Contents/Resources"):
                    loadDir += "/leo/plugins"
                else:
                    g.pr("Exception getting load directory")
            loadDir = g.os_path_finalize(loadDir)
            # g.trace(loadDir)
            return loadDir
        except:
            print("Exception getting load directory")
            raise
    #@+node:ekr.20120209051836.10385: *5* lm.configPlacesTable (REWRITE)
    def configPlacesTable(self):
        
        '''Return a list of location to be used to search for
        leoSettings.leo and myLeoSettings.leo.
        
        All entries in the table are unique, and each entry exists.'''
        
        # trace = False ; verbose = True
        # lm = self
        
        # table = [
            # (lm.globalConfigFile),
            # (lm.homeFile),
            # (lm.myGlobalConfigFile),
            # (lm.myHomeConfigFile),
            # (lm.machineConfigFile),
            # # (myLocalConfigFile,False),
        # ]
        
        # seen = []
        # for path in table:
            # if trace and verbose: g.trace('exists',g.os_path_exists(path),path)
            # if path and g.os_path_exists(path):
                # # Make sure we mark files seen no matter how they are specified.
                # path = g.os_path_realpath(g.os_path_finalize(path))
                # if path.lower() not in seen:
                    # seen.append(path.lower())
                    # table.append(path)
        # if trace: g.trace(repr(lm.fn),'table:',g.listToString(table))
        # return table
    #@+node:ekr.20120211121736.10772: *4* lm.computeWorkbookFileName
    def computeWorkbookFileName (self):
        
        lm = self

        # Get the name of the workbook.
        fn = g.app.config.getString(c=None,setting='default_leo_file')
        fn = g.os_path_finalize(fn)
        if not fn: return

        # g.trace(g.os_path_exists(fn),fn)

        if g.os_path_exists(fn):
            return fn
        elif g.os_path_isabs(fn):
            # Create the file.
            g.es_print('Using default leo file name:\n%s' % (fn),color='red')
            return fn
        else:
            # It's too risky to open a default file if it is relative.
            return None
    #@+node:ekr.20120209051836.10338: *4* lm.reportDirectories
    def reportDirectories(self):
        
        lm = self
        
        aList = ('homeDir','homeLeoDir','leoDir','loadDir','extensionsDir','globalConfigDir')

        for ivar in aList:
            val = getattr(self,ivar)
            g.trace('%20s' % (ivar),val)
    #@+node:ekr.20120211121736.10756: *3* lm.start & helpers
    def start(self):
        
        '''Start Leo, except for invoking the gui's main loop:
        read command-line args, load settings files, start plugins and load .leo files.
        
        Return True if all went well enough for the gui's main loop to start.
        '''
        
        trace = True
        lm = self
        
        # Phase 1.  Load all files, create commanders, and read settings.
        ok = lm.doPrePluginsInit()
        if not ok: return False
        
        # Phase 2: load plugins: the gui has already been set.
        g.doHook("start1")
        if g.app.killed: return False
        
        # Phase 3: after loading plugins. Create one or more frames.
        ok = lm.doPostPluginsInit()
        return ok
    #@+node:ekr.20120211121736.10767: *4* lm.doPrePluginsInit & helpers
    def doPrePluginsInit(self):

        ''' Scan options, set directories and read settings.'''

        trace = False
        lm = self
        
        if not lm.isValidPython():
            return False
        
        # Compute the standard directories.
        lm.computeStandardDirectories()
        if trace:  lm.reportDirectories()
        
        # Scan the options.
        lm.options = lm.scanOptions()
            
        # Create the gui immediately after reading the options.
        # Important: initApp (setLeoID) may have created the gui.
        if not g.app.gui:
            lm.createGui()
            
        # We can't print the signon until we know the gui.
        if lm.versionFlag:
            g.app.computeSignon()
            print(g.app.signon)
            return False
            
        # Init the app.
        g.app.init()
        
        # Compute the list of absolute file names.
        lm.computeFilesList()
        
        lm.loadGlobalSettingsFiles()
        
        # Load all files and create commanders.
        for fn in lm.files:
            lm.loadFile(fn)
            
        return True ####
        
        ##################### old code #####################
        

        # files = lm.getFiles(fileName2)

        # # Read settings *after* setting g.app.config and *before* opening plugins.
        # # This means if-gui has effect only in per-file settings.
        # g.app.config.readSettingsFiles(None,verbose)
        # for fn in files:
            # g.app.config.readSettingsFiles(fn,verbose)

        # if not files and not script:
            # # This must be done *after* the standard settings have been read.
            # fn = getWorkbookFile()
            # if fn:
                # files = [fn]
                # g.app.config.readSettingsFiles(fn,verbose=True)

        #### g.app.setGlobalDb()
        
        #### # Create the gui after reading options and settings.
        #### lm.createGui(pymacs,options)

        # # We can't print the signon until we know the gui.
        # g.app.computeSignon() # Set app.signon/signon2 for commanders.
        # versionFlag = options.get('versionFlag')
        # if versionFlag:
            # print(g.app.signon)
        # if versionFlag or not g.app.gui:
            # options['exit'] = True

        # return files,options
    #@+node:ekr.20120211121736.10768: *5* lm.createGui & helper
    def createGui(self):

        lm = self
        script = lm.script
        
        if lm.pymacs:
            g.app.createNullGuiWithScript(script=None)
        elif script:
            if lm.windowFlag:
                g.app.createDefaultGui()
                g.app.gui.setScript(script=script)
                sys.args = []
            else:
                g.app.createNullGuiWithScript(script=script)
        else:
            g.app.createDefaultGui() 
    #@+node:ekr.20120211121736.10801: *5* lm.isValidPython
    def isValidPython(self):

        if sys.platform == 'cli':
            return True

        minimum_python_version = '2.6'

        message = """\
    Leo requires Python %s or higher.
    You may download Python from
    http://python.org/download/
    """ % minimum_python_version

        try:
            version = '.'.join([str(sys.version_info[i]) for i in (0,1,2)])
            ok = g.CheckVersion(version,minimum_python_version)
            if not ok:
                print(message)
                try:
                    # g.app.gui does not exist yet.
                    import Tkinter as Tk
                    #@+<< define emergency dialog class >>
                    #@+node:ekr.20120211121736.10802: *6* << define emergency dialog class >>
                    class emergencyDialog:

                        """A class that creates an Tkinter dialog with a single OK button."""

                        #@+others
                        #@+node:ekr.20120211121736.10803: *7* __init__ (emergencyDialog)
                        def __init__(self,title,message):

                            """Constructor for the leoTkinterDialog class."""

                            self.answer = None # Value returned from run()
                            self.title = title
                            self.message=message

                            self.buttonsFrame = None # Frame to hold typical dialog buttons.
                            self.defaultButtonCommand = None
                                # Command to call when user closes the window
                                # by clicking the close box.
                            self.frame = None # The outermost frame.
                            self.root = None # Created in createTopFrame.
                            self.top = None # The toplevel Tk widget.

                            self.createTopFrame()
                            buttons = {"text":"OK","command":self.okButton,"default":True},
                                # Singleton tuple.
                            self.createButtons(buttons)
                            self.top.bind("<Key>", self.onKey)
                        #@+node:ekr.20120211121736.10804: *7* createButtons
                        def createButtons (self,buttons):

                            """Create a row of buttons.

                            buttons is a list of dictionaries containing
                            the properties of each button."""

                            assert(self.frame)
                            self.buttonsFrame = f = Tk.Frame(self.top)
                            f.pack(side="top",padx=30)

                            # Buttons is a list of dictionaries, with an empty dictionary
                            # at the end if there is only one entry.
                            buttonList = []
                            for d in buttons:
                                text = d.get("text","<missing button name>")
                                isDefault = d.get("default",False)
                                underline = d.get("underline",0)
                                command = d.get("command",None)
                                bd = g.choose(isDefault,4,2)

                                b = Tk.Button(f,width=6,text=text,bd=bd,
                                    underline=underline,command=command)
                                b.pack(side="left",padx=5,pady=10)
                                buttonList.append(b)

                                if isDefault and command:
                                    self.defaultButtonCommand = command

                            return buttonList
                        #@+node:ekr.20120211121736.10805: *7* createTopFrame
                        def createTopFrame(self):

                            """Create the Tk.Toplevel widget for a leoTkinterDialog."""

                            self.root = Tk.Tk()
                            self.top = Tk.Toplevel(self.root)
                            self.top.title(self.title)
                            self.root.withdraw()

                            self.frame = Tk.Frame(self.top)
                            self.frame.pack(side="top",expand=1,fill="both")

                            label = Tk.Label(self.frame,text=message,bg='white')
                            label.pack(pady=10)
                        #@+node:ekr.20120211121736.10806: *7* okButton
                        def okButton(self):

                            """Do default click action in ok button."""

                            self.top.destroy()
                            self.top = None

                        #@+node:ekr.20120211121736.10807: *7* onKey
                        def onKey(self,event):

                            """Handle Key events in askOk dialogs."""

                            self.okButton()

                            return # (for Tk) "break"
                        #@+node:ekr.20120211121736.10808: *7* run
                        def run (self):

                            """Run the modal emergency dialog."""

                            self.top.geometry("%dx%d%+d%+d" % (300,200,50,50))
                            self.top.lift()

                            self.top.grab_set() # Make the dialog a modal dialog.
                            self.root.wait_window(self.top)
                        #@-others
                    #@-<< define emergency dialog class >>
                    d = emergencyDialog(
                        title='Python Version Error',
                        message=message)
                    d.run()
                except Exception:
                    pass
            return ok
        except Exception:
            print("isValidPython: unexpected exception")
            traceback.print_exc()
            return 0
    #@+node:ekr.20120211121736.10813: *5* lm.loadGlobalSettingsFiles
    def loadGlobalSettingsFiles(self):
        
        pass
    #@+node:ekr.20120211204052.10830: *5* lm.loadFile
    def loadFile (self,fn):
        
        print('lm.loadFile',fn)
    #@+node:ekr.20120211121736.10785: *4* lm.doPostPluginsInit & helpers
    def doPostPluginsInit(self):

        '''Return True if the frame was created properly.'''
        
        lm = self
        
        print('doPostPluginsInit not ready yet')
        
        if 0:

            # Clear g.app.initing _before_ creating the frame.
            g.app.initing = False # "idle" hooks may now call g.app.forceShutdown.
        
            # Create the main frame.  Show it and all queued messages.
            c,c1,fn = None,None,None
            for fn in lm.files:
                c,frame = lm.createFrame(fn)
                if frame:
                    if not c1: c1 = c
                else:
                    g.trace('createFrame failed',repr(fn))
                    return False
                  
            # Put the focus in the first-opened file.  
            if not c:
                c,frame = lm.createFrame(None)
                c1 = c
                if c and frame:
                    fn = c.fileName()
                else:
                    g.trace('createFrame failed 2')
                    return False
                    
            # For qttabs gui, select the first-loaded tab.
            if hasattr(g.app.gui,'frameFactory'):
                factory = g.app.gui.frameFactory
                if factory and hasattr(factory,'setTabForCommander'):
                    c = c1
                    factory.setTabForCommander(c)
        
            # Do the final inits.
            c.setLog() # 2010/10/20
            g.app.logInited = True # 2010/10/20
            p = c.p
            g.app.initComplete = True
            g.doHook("start2",c=c,p=p,v=p,fileName=fn)
            g.enableIdleTimeHook(idleTimeDelay=500)
                # 2011/05/10: always enable this.
            lm.initFocusAndDraw(c)
        
            if lm.screenshot_fn:
                lm.make_screen_shot(lm.screenshot_fn)
                return False # Force an immediate exit.
        
            return True
    #@+node:ekr.20120211121736.10786: *5* lm.createFrame & helpers
    def createFrame (self,fn):

        """Create a LeoFrame during Leo's startup process."""
        
        # g.trace('(runLeo.py)',fn)

        lm = self
        script = lm.script

        # Try to create a frame for the file.
        if fn:
            ok, frame = g.openWithFileName(fn,None)
            if ok and frame:
                c2 = frame.c
                if lm.selectHeadline: lm.doSelect(c2)
                if lm.windowSize: lm.doWindowSize(c2)
                return c2,frame

        # Create a _new_ frame & indicate it is the startup window.
        c,frame = g.app.newLeoCommanderAndFrame(
            fileName=fn,initEditCommanders=True)

        if not script:
            g.app.writeWaitingLog(c) # 2009/12/22: fixes bug 448886

        assert frame.c == c and c.frame == frame
        frame.setInitialWindowGeometry()
        frame.resizePanesToRatio(frame.ratio,frame.secondary_ratio)
        frame.startupWindow = True
        if c.chapterController:
            c.chapterController.finishCreate()
            c.setChanged(False)
                # Clear the changed flag set when creating the @chapters node.
        # Call the 'new' hook for compatibility with plugins.
        g.doHook("new",old_c=None,c=c,new_c=c)

        g.createMenu(c,fn)
        g.finishOpen(c) # Calls c.redraw.

        # Report the failure to open the file.
        if fn: g.es_print("file not found:",fn,color='red')

        return c,frame
    #@+node:ekr.20120211121736.10787: *6* lm.doSelect
    def doSelect (self,c):

        '''Select the node with key lm.selectHeadline.'''

        lm = self
        s = lm.selectHeadline
        p = lm.findNode(c,s)

        if p:
            c.selectPosition(p)
        else:
            g.es_print('--select: not found:',s)
    #@+node:ekr.20120211121736.10788: *6* lm.doWindowSize
    def doWindowSize (self,c):

        lm = self
        w = c.frame.top

        try:
            h,w2 = lm.windowSize.split('x')
            h,w2 = int(h.strip()),int(w2.strip())
            w.resize(w2,h) # 2010/10/08.
            c.k.simulateCommand('equal-sized-panes')
            c.redraw()
            w.repaint() # Essential

        except Exception:
            print('doWindowSize:unexpected exception')
            g.es_exception()
    #@+node:ekr.20120211121736.10789: *6* lm.findNode
    def findNode (self,c,s):

        lm = self
        s = s.strip()

        # First, assume s is a gnx.
        for p in c.all_unique_positions():
            if p.gnx.strip() == s:
                return p

        for p in c.all_unique_positions():
            # g.trace(p.h.strip())
            if p.h.strip() == s:
                return p

        return None
    #@+node:ekr.20120211121736.10791: *5* lm.initFocusAndDraw
    def initFocusAndDraw(self,c):

        # Respect c's focus wishes if posssible.
        w = g.app.gui.get_focus(c)
        if w != c.frame.body.bodyCtrl and w != c.frame.tree.canvas:
            c.bodyWantsFocus()
            c.k.showStateAndMode(w)
            
        # There is no more fileName arg, so we *always* redraw.
        c.redraw_now()
    #@+node:ekr.20120211121736.10792: *5* lm.make_screen_shot
    def make_screen_shot(self,fn):

        '''Create a screenshot of the present Leo outline and save it to path.'''

        # g.trace('runLeo.py',fn)

        if g.app.gui.guiName() == 'qt':
            m = g.loadOnePlugin('screenshots')
            m.make_screen_shot(fn)
    #@+node:ekr.20120211121736.10776: *4* lm.scanOptions & lm.printOptions
    def scanOptions(self):

        '''Handle all options and remove them from sys.argv.'''
        trace = False
        lm = self

        # Note: this automatically implements the --help option.
        parser = optparse.OptionParser()
        add = parser.add_option
        # add('-c', '--config', dest="one_config_path",
            # help = 'use a single configuration file')
        # add('--debug',        action="store_true",dest="debug",
            # help = 'enable debugging support')
        # add('-f', '--file',   dest="fileName",
            # help = 'load a file at startup')
        add('--gui',
            help = 'gui to use (qt/qttabs)')
        add('--minimized',    action="store_true",
            help = 'start minimized')
        add('--maximized',    action="store_true",
            help = 'start maximized (Qt only)')
        add('--fullscreen',   action="store_true",
            help = 'start fullscreen (Qt only)')
        add('--ipython',      action="store_true",dest="use_ipython",
            help = 'enable ipython support')
        add('--no-cache',     action="store_true",dest='no_cache',
            help = 'disable reading of cached files')
        add('--no-splash',    action="store_true",dest='no_splash_screen',
            help = 'disable the splash screen')
        add('--silent',       action="store_true",dest="silent",
            help = 'disable all log messages')
        add('--screen-shot',  dest='screenshot_fn',
            help = 'take a screen shot and then exit')
        add('--script',       dest="script",
            help = 'execute a script and then exit')
        add('--script-window',dest="script_window",
            help = 'open a window for scripts')
        add('--select',       dest='select',
            help='headline or gnx of node to select')
        add('--version',      action="store_true",dest="version",
            help='print version number and exit')
        add('--window-size',  dest='window_size',
            help='initial window size in height x width format')

        # Parse the options, and remove them from sys.argv.
        options, args = parser.parse_args()
        sys.argv = [sys.argv[0]] ; sys.argv.extend(args)
        # if trace: print('scanOptions:',sys.argv)

        # Handle the args...

        # --debug
        # if options.debug:
            # g.debug = True ; print('*** debug mode on')

        # --gui
        gui = options.gui
        if gui:
            gui = gui.lower()
            if gui == 'qttabs':
                g.app.qt_use_tabs = True
            elif gui in ('curses','qt','null'):
                g.app.qt_use_tabs = False
            else:
                print('scanOptions: unknown gui: %s.  Using qt gui' % gui)
                gui = 'qt'
                g.app.qt_use_tabs = False
        elif sys.platform == 'darwin':
            gui = 'qt'
            g.app.qt_use_tabs = False
        else:
            gui = 'qttabs'
            g.app.qt_use_tabs = True

        assert gui
        g.app.guiArgName = gui

        # --minimized
        # --maximized
        # --fullscreen
        g.app.start_minimized = options.minimized
        g.app.start_maximized = options.maximized
        g.app.start_fullscreen = options.fullscreen

        # --ipython
        g.app.useIpython = options.use_ipython

        # --no-cache
        if options.no_cache:
            g.enableDB = False
            
        # --no-splash
        g.app.use_splash_screen = not options.no_splash_screen

        # --screen-shot=fn
        lm.screenshot_fn = options.screenshot_fn
        if lm.screenshot_fn:
            lm.screenshot_fn = lm.screenshot_fn.strip('"')

        # --script
        lm.script_path = options.script
        lm.script_path_w = options.script_window
        if lm.script_path and lm.script_path_w:
            parser.error("--script and script-window are mutually exclusive")

        lm.script_name = lm.script_path or lm.script_path_w
        if lm.script_name:
            lm.script_name = g.os_path_finalize_join(g.app.loadDir,lm.script_name)
            lm.script,e = g.readFileIntoString(lm.script_name,kind='script:')
        else:
            lm.script = None

        # --select
        lm.selectHeadline = options.select
        if lm.selectHeadline:
            lm.selectHeadline = lm.selectHeadline.strip('"')

        # --silent
        g.app.silentMode = options.silent

        # --version: print the version and exit.
        lm.versionFlag = options.version

        # --window-size
        lm.windowSize = options.window_size
        if lm.windowSize:
            try:
                h,w = lm.windowSize.split('x')
            except ValueError:
                lm.windowSize = None
                g.trace('bad --window-size:',lm.windowSize)
                
        # Post process the options.
        if lm.pymacs:
            lm.script,lm.windowFlag = None,None

        lm.windowFlag = lm.script and lm.script_path_w

        lm.files = [z for z in sys.argv[1:] if not z.startswith('-')]
        
        if trace: lm.printOptions()
    #@+node:ekr.20120211204052.10831: *5* printOptions
    def printOptions(self):
        
        lm = self
        app_table = (
            'batchMode','gui','guiArgName','qt_use_tabs',            
            'silentMode','start_fullscreen','start_maximized','start_minimized',
            'useIpython','use_splash_screen',
        )
        g_table = (
            'enableDB',
        )
        lm_table = ( 
            'script', 'script_name','script_path','script_path_w',
            'screenshot_fn','selectHeadline','versionFlag','windowFlag','windowSize',
            'files',
        )
        for ivar in app_table:
            print('%25s %s' % (('g.app.%s' % (ivar)),getattr(g.app,ivar)))
            
        for ivar in g_table:
            print('%25s %s' % (('g.%s' % (ivar)),getattr(g,ivar)))
            
        for ivar in lm_table:
            print('%25s %s' % (('lm.%s' % (ivar)),getattr(lm,ivar)))
        
    #@-others
    
#@+node:ekr.20120211121736.10831: ** class LogManager
class LogManager:
    
    '''A class to handle the global log, and especially
    switching the log from commander to commander.'''
    
    def __init__ (self):
    
        self.log = None             # The LeoFrame containing the present log.
        self.logInited = False      # False: all log message go to logWaiting list.
        self.logIsLocked = False    # True: no changes to log are allowed.
        self.logWaiting = []        # List of messages waiting to go to a log.
        self.printWaiting = []      # Queue of messages to be sent to the printer.
        self.signon_printed = False # True: the global signon has been printed.
    
    #@+others
    #@+node:ekr.20120211121736.10834: *3* LogM.setLog, lockLog, unlocklog
    def setLog (self,log):

        """set the frame to which log messages will go"""

        # print("app.setLog:",log,g.callers())
        if not self.logIsLocked:
            self.log = log

    def lockLog(self):
        """Disable changes to the log"""
        self.logIsLocked = True

    def unlockLog(self):
        """Enable changes to the log"""
        self.logIsLocked = False
    #@+node:ekr.20120211121736.10836: *3* LogM.writeWaitingLog
    def writeWaitingLog (self,c):

        trace = False
        lm = self
        
        if trace:
            # Do not call g.es, g.es_print, g.pr or g.trace here!
            print('** writeWaitingLog','silent',g.app.silentMode,c.shortFileName())
            # print('writeWaitingLog',g.callers())
            # import sys ; print('writeWaitingLog: argv',sys.argv)

        if not c or not c.exists:
            return

        if g.unitTesting:
            lm.printWaiting = []
            lm.logWaiting = []
            g.app.setLog(None) # Prepare to requeue for other commanders.
            return

        table = [
            ('Leo Log Window','red'),
            (g.app.signon,'black'),
            (g.app.signon2,'black'),
        ]
        table.reverse()

        c.setLog() # 2010/10/20
        lm.logInited = True # Prevent recursive call.
        
        if not lm.signon_printed:
            lm.signon_printed = True
            if not g.app.silentMode: # 2011/11/02:
                print('')
                print('** isPython3: %s' % g.isPython3)
                if not g.enableDB:
                    print('** caching disabled')
                print(g.app.signon)
                print(g.app.signon2)
        if not g.app.silentMode: # 2011/11/02:
            for s in lm.printWaiting:
                print(s)
        lm.printWaiting = []

        if not g.app.silentMode:  # 2011/11/02:
            for s,color in table:
                lm.logWaiting.insert(0,(s+'\n',color),)
            for s,color in lm.logWaiting:
                g.es('',s,color=color,newline=0)
                    # The caller must write the newlines.
        lm.logWaiting = []

        # Essential when opening multiple files...
        lm.setLog(None) 
    #@-others
#@-others
#@-leo

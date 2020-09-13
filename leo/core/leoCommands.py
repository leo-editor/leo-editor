# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20031218072017.2810: * @file leoCommands.py
#@@first
#@+<< imports >>
#@+node:ekr.20040712045933: ** << imports >> (leoCommands)
import leo.core.leoGlobals as g
import leo.core.leoNodes as leoNodes
    # The leoCommands ctor now does most leo.core.leo* imports.
    # This breaks circular dependencies.
import itertools
import os
import re
import sys
import time
import tokenize  # for c.checkAllPythonCode
try:
    import tabnanny  # for Check Python command # Does not exist in jython
except ImportError:
    tabnanny = None
#@-<< imports >>

def cmd(name):
    """Command decorator for the Commands class."""
    return g.new_cmd_decorator(name, ['c',])

#@+others
#@+node:ekr.20160514120615.1: ** class Commands (object)
class Commands:
    """
    A per-outline class that implements most of Leo's commands. The
    "c" predefined object is an instance of this class.

    c.initObjects() creates sucommanders corresponding to files in the
    leo/core and leo/commands. All of Leo's core code is accessible
    via this class and its subcommanders.

    g.app.pluginsController is Leo's plugins controller. Many plugins
    inject controllers objects into the Commands class. These are
    another kind of subcommander.
    
    The @g..commander_command decorator injects methods into this class.
    """
    #@+others
    #@+node:ekr.20031218072017.2811: *3*  c.Birth & death
    #@+node:ekr.20031218072017.2812: *4* c.__init__ & helpers
    def __init__(self, fileName,
        gui=None,
        parentFrame=None,
        previousSettings=None,
        relativeFileName=None,
    ):

        # tag = 'Commands.__init__ %s' % (g.shortFileName(fileName))
        c = self
        # Official ivars.
        self._currentPosition = None
        self._topPosition = None
        self.frame = None
        self.parentFrame = parentFrame  # New in Leo 6.0.
        self.gui = gui or g.app.gui
        self.ipythonController = None
            # Set only by the ipython plugin.
        # The order of these calls does not matter.
        c.initCommandIvars()
        c.initDebugIvars()
        c.initDocumentIvars()
        c.initEventIvars()
        c.initFileIvars(fileName, relativeFileName)
        c.initOptionsIvars()
        c.initObjectIvars()
        c.initSettings(previousSettings)
            # Init the settings *before* initing the objects.
        # Initialize all subsidiary objects, including subcommanders.
        c.initObjects(self.gui)
        assert c.frame
        assert c.frame.c
        # Complete the init!
        c.finishCreate()
    #@+node:ekr.20120217070122.10475: *5* c.computeWindowTitle
    def computeWindowTitle(self, fileName):
        """Set the window title and fileName."""
        if fileName:
            title = g.computeWindowTitle(fileName)
        else:
            s = "untitled"
            n = g.app.numberOfUntitledWindows
            if n > 0:
                s += str(n)
            title = g.computeWindowTitle(s)
            g.app.numberOfUntitledWindows = n + 1
        return title
    #@+node:ekr.20120217070122.10473: *5* c.initCommandIvars
    def initCommandIvars(self):
        """Init ivars used while executing a command."""
        self.commandsDict = {}
            # Keys are command names, values are functions.
        self.disableCommandsMessage = ''
            # The presence of this message disables all commands.
        self.hookFunction = None
            # One of three places that g.doHook looks for hook functions.
        self.ignoreChangedPaths = False
            # True: disable path changed message in at.WriteAllHelper.
        self.inCommand = False
            # Interlocks to prevent premature closing of a window.
        self.isZipped = False
            # Set by g.openWithFileName.
        self.outlineToNowebDefaultFileName = "noweb.nw"
            # For Outline To Noweb dialog.
        # For tangle/untangle
        self.tangle_errors = 0
        # Default Tangle options
        self.use_header_flag = False
        self.output_doc_flag = False
        # For hoist/dehoist commands.
        self.hoistStack = []
            # Stack of nodes to be root of drawn tree.
            # Affects drawing routines and find commands.
        # For outline navigation.
        self.navPrefix = ''  # Must always be a string.
        self.navTime = None

        self.sqlite_connection = None
    #@+node:ekr.20120217070122.10466: *5* c.initDebugIvars
    def initDebugIvars(self):
        """Init Commander debugging ivars."""
        self.command_count = 0
        self.scanAtPathDirectivesCount = 0
        self.trace_focus_count = 0
    #@+node:ekr.20120217070122.10471: *5* c.initDocumentIvars
    def initDocumentIvars(self):
        """Init per-document ivars."""
        self.expansionLevel = 0
            # The expansion level of this outline.
        self.expansionNode = None
            # The last node we expanded or contracted.
        self.nodeConflictList = []
            # List of nodes with conflicting read-time data.
        self.nodeConflictFileName = None
            # The fileName for c.nodeConflictList.
        self.user_dict = {}
            # Non-persistent dictionary for free use by scripts and plugins.
    #@+node:ekr.20120217070122.10467: *5* c.initEventIvars
    def initEventIvars(self):
        """Init ivars relating to gui events."""
        self.configInited = False
        self.doubleClickFlag = False
        self.exists = True
            # Indicate that this class exists and has not been destroyed.
            # Do this early in the startup process so we can call hooks.
        self.in_qt_dialog = False
            # True: in a qt dialog.
        self.loading = False
            # True: we are loading a file: disables c.setChanged()
        self.promptingForClose = False
            # True: lock out additional closing dialogs.
        self.suppressHeadChanged = False
            # True: prevent setting c.changed when switching chapters.
        # Flags for c.outerUpdate...
        self.enableRedrawFlag = True
        self.requestCloseWindow = False
        self.requestedFocusWidget = None
        self.requestLaterRedraw = False
    #@+node:ekr.20120217070122.10472: *5* c.initFileIvars
    def initFileIvars(self, fileName, relativeFileName):
        """Init file-related ivars of the commander."""
        self.changed = False
            # True: the ouline has changed since the last save.
        self.ignored_at_file_nodes = []
            # List of nodes for c.raise_error_dialogs.
        self.import_error_nodes = []
            # List of nodes for c.raise_error_dialogs.
        self.last_dir = None
            # The last used directory.
        self.mFileName = fileName or ''
            # Do _not_ use os_path_norm: it converts an empty path to '.' (!!)
        self.mRelativeFileName = relativeFileName or ''
            #
        self.openDirectory = None
            #
        self.orphan_at_file_nodes = []
            # List of orphaned nodes for c.raise_error_dialogs.
        self.wrappedFileName = None
            # The name of the wrapped file, for wrapper commanders.
            # Set by LM.initWrapperLeoFile
    #@+node:ekr.20120217070122.10469: *5* c.initOptionsIvars
    def initOptionsIvars(self):
        """Init Commander ivars corresponding to user options."""
        self.fixed = False
        self.fixedWindowPosition = []
        self.forceExecuteEntireBody = False
        self.focus_border_color = 'white'
        self.focus_border_width = 1  # pixels
        self.outlineHasInitialFocus = False
        self.page_width = 132
        self.sparse_find = True
        self.sparse_move = True
        self.sparse_spell = True
        self.stayInTreeAfterSelect = False
        self.tab_width = -4
        self.tangle_batch_flag = False
        self.target_language = "python"
        self.untangle_batch_flag = False
        # self.use_body_focus_border = True
        # self.use_focus_border = False
            # Replaced by style-sheet entries.
        self.vim_mode = False
    #@+node:ekr.20120217070122.10468: *5* c.initObjectIvars
    def initObjectIvars(self):
        # These ivars are set later by leoEditCommands.createEditCommanders
        self.abbrevCommands = None
        self.editCommands = None
        self.db = {}  # May be set to a PickleShare instance later.
        self.bufferCommands = None
        self.chapterCommands = None
        self.controlCommands = None
        self.convertCommands = None
        self.debugCommands = None
        self.editFileCommands = None
        self.evalController = None
        self.gotoCommands = None
        self.helpCommands = None
        self.keyHandler = self.k = None
        self.keyHandlerCommands = None
        self.killBufferCommands = None
        self.leoCommands = None
        self.macroCommands = None
        self.miniBufferWidget = None
        self.printingController = None
        self.queryReplaceCommands = None
        self.rectangleCommands = None
        self.searchCommands = None
        self.spellCommands = None
        self.leoTestManager = None
        self.vimCommands = None
    #@+node:ekr.20120217070122.10470: *5* c.initObjects
    #@@nobeautify

    def initObjects(self, gui):

        c = self
        gnx = 'hidden-root-vnode-gnx'
        assert not hasattr(c, 'fileCommands'), c.fileCommands

        class DummyFileCommands:
            def __init__(self):
                self.gnxDict = {}

        c.fileCommands = DummyFileCommands()
        self.hiddenRootNode = leoNodes.VNode(context=c, gnx=gnx)
        self.hiddenRootNode.h = '<hidden root vnode>'
        c.fileCommands = None
        # Create the gui frame.
        title = c.computeWindowTitle(c.mFileName)
        if not g.app.initing:
            g.doHook("before-create-leo-frame", c=c)
        self.frame = gui.createLeoFrame(c, title)
        assert self.frame
        assert self.frame.c == c
        import leo.core.leoHistory as leoHistory
        self.nodeHistory = leoHistory.NodeHistory(c)
        self.initConfigSettings()
        c.setWindowPosition() # Do this after initing settings.
        # Break circular import dependencies by doing imports here.
        # These imports take almost 3/4 sec in the leoBridge.
        import leo.core.leoAtFile as leoAtFile
        import leo.core.leoBeautify as leoBeautify # So decorators are executed.
        assert leoBeautify # for pyflakes.
        import leo.core.leoChapters as leoChapters
        # User commands...
        import leo.commands.abbrevCommands as abbrevCommands
        import leo.commands.bufferCommands as bufferCommands
        import leo.commands.checkerCommands as checkerCommands
        assert checkerCommands
            # To suppress a pyflakes warning.
            # The import *is* required to define commands.
        import leo.commands.controlCommands as controlCommands
        import leo.commands.convertCommands as convertCommands
        import leo.commands.debugCommands as debugCommands
        import leo.commands.editCommands as editCommands
        import leo.commands.editFileCommands as editFileCommands
        import leo.commands.gotoCommands as gotoCommands
        import leo.commands.helpCommands as helpCommands
        import leo.commands.keyCommands as keyCommands
        import leo.commands.killBufferCommands as killBufferCommands
        import leo.commands.rectangleCommands as rectangleCommands
        import leo.commands.spellCommands as spellCommands
        # Import files to execute @g.commander_command decorators
        import leo.core.leoCompare as leoCompare
        assert leoCompare
        import leo.core.leoDebugger as leoDebugger
        assert leoDebugger
        import leo.commands.commanderEditCommands as commanderEditCommands
        assert commanderEditCommands
        import leo.commands.commanderFileCommands as commanderFileCommands
        assert commanderFileCommands
        import leo.commands.commanderFindCommands as commanderFindCommands
        assert commanderFindCommands
        import leo.commands.commanderHelpCommands as commanderHelpCommands
        assert commanderHelpCommands
        import leo.commands.commanderOutlineCommands as commanderOutlineCommands
        assert commanderOutlineCommands
        # Other subcommanders.
        import leo.core.leoFind as leoFind # Leo 4.11.1
        import leo.core.leoKeys as leoKeys
        import leo.core.leoFileCommands as leoFileCommands
        import leo.core.leoImport as leoImport
        import leo.core.leoMarkup as leoMarkup
        import leo.core.leoPersistence as leoPersistence
        import leo.core.leoPrinting as leoPrinting
        import leo.core.leoRst as leoRst
        import leo.core.leoShadow as leoShadow
        import leo.core.leoTangle as leoTangle
        import leo.core.leoTest as leoTest
        import leo.core.leoUndo as leoUndo
        import leo.core.leoVim as leoVim
        # Define the subcommanders.
        self.keyHandler = self.k    = leoKeys.KeyHandlerClass(c)
        self.chapterController      = leoChapters.ChapterController(c)
        self.shadowController       = leoShadow.ShadowController(c)
        self.fileCommands           = leoFileCommands.FileCommands(c)
        self.findCommands           = leoFind.LeoFind(c)
        self.atFileCommands         = leoAtFile.AtFile(c)
        self.importCommands         = leoImport.LeoImportCommands(c)
        self.markupCommands         = leoMarkup.MarkupCommands(c)
        self.persistenceController  = leoPersistence.PersistenceDataController(c)
        self.printingController     = leoPrinting.PrintingController(c)
        self.rstCommands            = leoRst.RstCommands(c)
        self.tangleCommands         = leoTangle.TangleCommands(c)
        self.testManager            = leoTest.TestManager(c)
        self.vimCommands            = leoVim.VimCommands(c)
        # User commands
        self.abbrevCommands     = abbrevCommands.AbbrevCommandsClass(c)
        self.bufferCommands     = bufferCommands.BufferCommandsClass(c)
        self.controlCommands    = controlCommands.ControlCommandsClass(c)
        self.convertCommands    = convertCommands.ConvertCommandsClass(c)
        self.debugCommands      = debugCommands.DebugCommandsClass(c)
        self.editCommands       = editCommands.EditCommandsClass(c)
        self.editFileCommands   = editFileCommands.EditFileCommandsClass(c)
        self.gotoCommands       = gotoCommands.GoToCommands(c)
        self.helpCommands       = helpCommands.HelpCommandsClass(c)
        self.keyHandlerCommands = keyCommands.KeyHandlerCommandsClass(c)
        self.killBufferCommands = killBufferCommands.KillBufferCommandsClass(c)
        self.rectangleCommands  = rectangleCommands.RectangleCommandsClass(c)
        self.spellCommands      = spellCommands.SpellCommandsClass(c)
        self.undoer             = leoUndo.Undoer(c)
        # Create the list of subcommanders.
        self.subCommanders = [
            self.abbrevCommands,
            self.atFileCommands,
            self.bufferCommands,
            self.chapterController,
            self.controlCommands,
            self.convertCommands,
            self.debugCommands,
            self.editCommands,
            self.editFileCommands,
            self.fileCommands,
            self.findCommands,
            self.gotoCommands,
            self.helpCommands,
            self.importCommands,
            self.keyHandler,
            self.keyHandlerCommands,
            self.killBufferCommands,
            self.persistenceController,
            self.printingController,
            self.rectangleCommands,
            self.rstCommands,
            self.shadowController,
            self.spellCommands,
            self.tangleCommands,
            self.testManager,
            self.vimCommands,
            self.undoer,
        ]
        # Other objects
        c.configurables = c.subCommanders[:]
            # A list of other classes that have a reloadSettings method
        c.db = g.app.commander_cacher.get_wrapper(c)
        import leo.plugins.free_layout as free_layout
        self.free_layout = free_layout.FreeLayoutController(c)
        if hasattr(g.app.gui, 'styleSheetManagerClass'):
            self.styleSheetManager = g.app.gui.styleSheetManagerClass(c)
            self.subCommanders.append(self.styleSheetManager)
        else:
            self.styleSheetManager = None
    #@+node:ekr.20140815160132.18837: *5* c.initSettings
    def initSettings(self, previousSettings):
        """Init the settings *before* initing the objects."""
        c = self
        import leo.core.leoConfig as leoConfig
        c.config = leoConfig.LocalConfigManager(c, previousSettings)
        g.app.config.setIvarsFromSettings(c)
    #@+node:ekr.20031218072017.2814: *4* c.__repr__ & __str__
    def __repr__(self):
        return f"Commander {id(self)}: {repr(self.mFileName)}"

    __str__ = __repr__
    #@+node:ekr.20050920093543: *4* c.finishCreate & helpers
    def finishCreate(self):
        """
        Finish creating the commander and all sub-objects.
        This is the last step in the startup process.
        """
        c, k = self, self.k
        assert c.gui
        assert k
        c.frame.finishCreate()
        c.miniBufferWidget = c.frame.miniBufferWidget
            # Will be None for nullGui.
        # Only c.abbrevCommands needs a finishCreate method.
        c.abbrevCommands.finishCreate()
        # Finish other objects...
        c.createCommandNames()
        k.finishCreate()
        c.findCommands.finishCreate()
        if not c.gui.isNullGui:
            g.registerHandler('idle', c.idle_focus_helper)
        if getattr(c.frame, 'menu', None):
            c.frame.menu.finishCreate()
        if getattr(c.frame, 'log', None):
            c.frame.log.finishCreate()
        c.undoer.clearUndoState()
        if c.vimCommands and c.vim_mode:
            c.vimCommands.finishCreate()
            # Menus must exist at this point.
        # Do not call chapterController.finishCreate here:
        # It must be called after the first real redraw.
        g.check_cmd_instance_dict(c, g)
        c.bodyWantsFocus()
    #@+node:ekr.20140815160132.18835: *5* c.createCommandNames
    def createCommandNames(self):
        """
        Create all entries in c.commandsDict.
        Do *not* clear c.commandsDict here.
        """
        for commandName, func in g.global_commands_dict.items():
            self.k.registerCommand(commandName, func)
    #@+node:ekr.20051007143620: *5* c.printCommandsDict
    def printCommandsDict(self):
        c = self
        print('Commands...')
        for key in sorted(c.commandsDict):
            command = c.commandsDict.get(key)
            print(f"{key:30} = {command.__name__ if command else '<None>'}")
        print('')
    #@+node:ekr.20041130173135: *4* c.hash
    # This is a bad idea.

    def hash(self):
        c = self
        if c.mFileName:
            return g.os_path_finalize(c.mFileName).lower()  # #1341.
        return 0
    #@+node:ekr.20110509064011.14563: *4* c.idle_focus_helper & helpers
    idle_focus_count = 0

    def idle_focus_helper(self, tag, keys):
        """An idle-tme handler that ensures that focus is *somewhere*."""
        trace = 'focus' in g.app.debug
        trace_inactive_focus = False  # Too disruptive for --trace-focus
        trace_in_dialog = False  # Not useful enough for --trace-focus
        c = self
        assert tag == 'idle'
        if g.app.unitTesting:
            return
        if keys.get('c') != c:
            if trace: g.trace('no c')
            return
        self.idle_focus_count += 1
        if c.in_qt_dialog:
            if trace and trace_in_dialog: g.trace('in_qt_dialog')
            return
        w = g.app.gui.get_focus(at_idle=True)
        if g.app.gui.active:
            # Always call trace_idle_focus.
            self.trace_idle_focus(w)
            if w and self.is_unusual_focus(w):
                if trace:
                    w_class = w and w.__class__.__name__
                    g.trace('***** unusual focus', w_class)
                # Fix bug 270: Leo's keyboard events doesn't work after "Insert"
                # on headline and Alt+Tab, Alt+Tab
                # Presumably, intricate details of Qt event handling are involved.
                # The focus was in the tree, so put the focus back in the tree.
                c.treeWantsFocusNow()
            # elif not w and active:
                # c.bodyWantsFocusNow()
        elif trace and trace_inactive_focus:
            w_class = w and w.__class__.__name__
            count = c.idle_focus_count
            g.trace(f"{count} inactive focus: {w_class}")
    #@+node:ekr.20160427062131.1: *5* c.is_unusual_focus
    def is_unusual_focus(self, w):
        """Return True if w is not in an expected place."""
        #
        # #270: Leo's keyboard events doesn't work after "Insert"
        #       on headline and Alt+Tab, Alt+Tab
        #
        # #276: Focus lost...in Nav text input
        import leo.plugins.qt_frame as qt_frame
        return isinstance(w, qt_frame.QtTabBarWrapper)
    #@+node:ekr.20150403063658.1: *5* c.trace_idle_focus
    last_unusual_focus = None
    # last_no_focus = False

    def trace_idle_focus(self, w):
        """Trace the focus for w, minimizing chatter."""
        from leo.core.leoQt import QtWidgets
        import leo.plugins.qt_frame as qt_frame
        trace = 'focus' in g.app.debug
        trace_known = False
        c = self
        table = (QtWidgets.QWidget, qt_frame.LeoQTreeWidget,)
        count = c.idle_focus_count
        if w:
            w_class = w and w.__class__.__name__
            c.last_no_focus = False
            if self.is_unusual_focus(w):
                if trace:
                    g.trace(f"{count} unusual focus: {w_class}")
            else:
                c.last_unusual_focus = None
                if isinstance(w, table):
                    if trace and trace_known:
                        g.trace(f"{count} known focus: {w_class}")
                elif trace:
                    g.trace(f"{count} unknown focus: {w_class}")
        else:
            if trace:
                g.trace(f"{count:3} no focus")
    #@+node:ekr.20081005065934.1: *4* c.initAfterLoad
    def initAfterLoad(self):
        """Provide an offical hook for late inits of the commander."""
        pass
    #@+node:ekr.20090213065933.6: *4* c.initConfigSettings
    def initConfigSettings(self):
        """Init all cached commander config settings."""
        c = self
        getBool = c.config.getBool
        getColor = c.config.getColor
        getData = c.config.getData
        getInt = c.config.getInt
        c.autoindent_in_nocolor = getBool('autoindent-in-nocolor-mode')
        c.collapse_nodes_after_move = getBool('collapse-nodes-after-move')
        c.collapse_on_lt_arrow = getBool('collapse-on-lt-arrow', default=True)
        c.contractVisitedNodes = getBool('contractVisitedNodes')
        c.fixedWindowPositionData = getData('fixedWindowPosition')
        c.focus_border_color = getColor('focus-border-color') or 'red'
        c.focus_border_command_state_color = getColor(
            'focus-border-command-state-color') or 'blue'
        c.focus_border_overwrite_state_color = getColor(
            'focus-border-overwrite-state-color') or 'green'
        c.focus_border_width = getInt('focus-border-width') or 1  # pixels
        c.forceExecuteEntireBody = getBool('force-execute-entire-body', default=False)
        c.make_node_conflicts_node = getBool('make-node-conflicts-node', default=True)
        c.outlineHasInitialFocus = getBool('outline-pane-has-initial-focus')
        c.page_width = getInt('page-width') or 132
        # c.putBitsFlag = getBool('put-expansion-bits-in-leo-files', default=True)
        c.sparse_move = getBool('sparse-move-outline-left')
        c.sparse_find = getBool('collapse-nodes-during-finds')
        c.sparce_spell = getBool('collapse-nodes-while-spelling')
        c.stayInTreeAfterSelect = getBool('stayInTreeAfterSelect')
        c.smart_tab = getBool('smart-tab')
        c.tab_width = getInt('tab-width') or -4
        c.verbose_check_outline = getBool('verbose-check-outline', default=False)
        c.vim_mode = getBool('vim-mode', default=False)
        c.write_script_file = getBool('write-script-file')
    #@+node:ekr.20090213065933.7: *4* c.setWindowPosition
    def setWindowPosition(self):
        c = self
        if c.fixedWindowPositionData:
            try:
                aList = [z.strip() for z in c.fixedWindowPositionData if z.strip()]
                w, h, l, t = aList
                c.fixedWindowPosition = int(w), int(h), int(l), int(t)
            except Exception:
                g.error('bad @data fixedWindowPosition',
                    repr(self.fixedWindowPosition))
        else:
            c.windowPosition = 500, 700, 50, 50  # width,height,left,top.
    #@+node:ekr.20171123135625.4: *3* @cmd c.executeScript & public helpers
    @cmd('execute-script')
    def executeScript(self, event=None,
        args=None, p=None, script=None, useSelectedText=True,
        define_g=True, define_name='__main__',
        silent=False, namespace=None, raiseFlag=False,
        runPyflakes=True,
    ):
        """
        Execute a *Leo* script.
        Keyword args:
        args=None               Not None: set script_args in the execution environment.
        p=None                  Get the script from p.b, unless script is given.
        script=None             None: use script in p.b or c.p.b
        useSelectedText=True    False: use all the text in p.b or c.p.b.
        define_g=True           True: define g for the script.
        define_name='__main__'  Not None: define the name symbol.
        silent=False            No longer used.
        namespace=None          Not None: execute the script in this namespace.
        raiseFlag=False         True: reraise any exceptions.
        runPyflakes=True        True: run pyflakes if allowed by setting.
        """
        c, script1 = self, script
        if runPyflakes:
            run_pyflakes = c.config.getBool('run-pyflakes-on-write', default=False)
        else:
            run_pyflakes = False
        if not script:
            if c.forceExecuteEntireBody:
                useSelectedText = False
            script = g.getScript(c, p or c.p, useSelectedText=useSelectedText)
        script_p = p or c.p
            # Only for error reporting below.
        # #532: check all scripts with pyflakes.
        if run_pyflakes and not g.unitTesting:
            import leo.commands.checkerCommands as cc
            # at = c.atFileCommands
            prefix = ('c,g,p,script_gnx=None,None,None,None;'
                      'assert c and g and p and script_gnx;\n')
            cc.PyflakesCommand(c).check_script(script_p, prefix + script)
        self.redirectScriptOutput()
        try:
            oldLog = g.app.log
            log = c.frame.log
            g.app.log = log
            if script.strip():
                sys.path.insert(0, '.')  # New in Leo 5.0
                sys.path.insert(0, c.frame.openDirectory)  # per SegundoBob
                script += '\n'  # Make sure we end the script properly.
                try:
                    if not namespace or namespace.get('script_gnx') is None:
                        namespace = namespace or {}
                        namespace.update(script_gnx=script_p.gnx)
                    # We *always* execute the script with p = c.p.
                    c.executeScriptHelper(args, define_g, define_name, namespace, script)
                except KeyboardInterrupt:
                    g.es('interrupted')
                except Exception:
                    if raiseFlag:
                        raise
                    g.handleScriptException(c, script_p, script, script1)
                finally:
                    del sys.path[0]
                    del sys.path[0]
            else:
                tabName = log and hasattr(log, 'tabName') and log.tabName or 'Log'
                g.warning("no script selected", tabName=tabName)
        finally:
            g.app.log = oldLog
            self.unredirectScriptOutput()
    #@+node:ekr.20171123135625.5: *4* c.executeScriptHelper
    def executeScriptHelper(self, args, define_g, define_name, namespace, script):
        c = self
        if c.p:
            p = c.p.copy()  # *Always* use c.p and pass c.p to script.
            c.setCurrentDirectoryFromContext(p)
        else:
            p = None
        d = {'c': c, 'g': g, 'input': g.input_, 'p': p} if define_g else {}
        if define_name: d['__name__'] = define_name
        d['script_args'] = args or []
        d['script_gnx'] = g.app.scriptDict.get('script_gnx')
        if namespace: d.update(namespace)
        #
        # A kludge: reset c.inCommand here to handle the case where we *never* return.
        # (This can happen when there are multiple event loops.)
        # This does not prevent zombie windows if the script puts up a dialog...
        try:
            c.inCommand = False
            g.inScript = g.app.inScript = True
                # g.inScript is a synonym for g.app.inScript.
            if c.write_script_file:
                scriptFile = self.writeScriptFile(script)
                exec(compile(script, scriptFile, 'exec'), d)
            else:
                exec(script, d)
        finally:
            g.inScript = g.app.inScript = False
    #@+node:ekr.20171123135625.6: *4* c.redirectScriptOutput
    def redirectScriptOutput(self):
        c = self
        if c.config.redirect_execute_script_output_to_log_pane:
            g.redirectStdout()  # Redirect stdout
            g.redirectStderr()  # Redirect stderr
    #@+node:ekr.20171123135625.7: *4* c.setCurrentDirectoryFromContext
    def setCurrentDirectoryFromContext(self, p):
        c = self
        aList = g.get_directives_dict_list(p)
        path = c.scanAtPathDirectives(aList)
        curDir = g.os_path_abspath(os.getcwd())
        if path and path != curDir:
            try:
                os.chdir(path)
            except Exception:
                pass
    #@+node:ekr.20171123135625.8: *4* c.unredirectScriptOutput
    def unredirectScriptOutput(self):
        c = self
        if c.exists and c.config.redirect_execute_script_output_to_log_pane:
            g.restoreStderr()
            g.restoreStdout()
    #@+node:vitalije.20190924191405.1: *3* @cmd c.execute_pytest
    @cmd('execute-pytest')
    def execute_pytest(self, event=None):
        c = self

        def it(p):
            for p1 in p.self_and_parents():
                if p1.h.startswith('@test '):
                    yield p1
                    return
            for p1 in p.subtree():
                if p1.h.startswith('@test '):
                    yield p1

        try:
            for p in it(c.p):
                self.execute_single_pytest(p)
        except ImportError:
            g.es('pytest needs to be installed')
            return

    def execute_single_pytest(self, p):
        c = self
        from _pytest.config import get_config
        from _pytest.assertion.rewrite import rewrite_asserts
        import ast
        cfg = get_config()
        script = g.getScript(c, p, useSentinels=False) + (
            '\n'
            'ls = dict(locals())\n'
            'failed = 0\n'
            'for x in ls:\n'
            '    if x.startswith("test_") and callable(ls[x]):\n'
            '        try:\n'
            '            ls[x]()\n'
            '        except AssertionError as e:\n'
            '            failed += 1\n'
            '            g.es(f"-------{p.h[6:].strip()}/{x} failed---------")\n'
            '            g.es(str(e))\n'
            'if failed == 0:\n'
            '    g.es("all tests passed")\n'
            'else:\n'
            '    g.es(f"failed:{failed} tests")\n')

        fname = g.os_path_finalize_join(g.app.homeLeoDir, 'leoPytestScript.py')
        with open(fname, 'wt', encoding='utf8') as out:
            out.write(script)
        tree = ast.parse(script, filename=fname)
        rewrite_asserts(tree, script, config=cfg)
        co = compile(tree, fname, "exec", dont_inherit=True)
        sys.path.insert(0, '.')
        sys.path.insert(0, c.frame.openDirectory)
        try:
            exec(co, {'c': c, 'g': g, 'p': p})
        except KeyboardInterrupt:
            g.es('interrupted')
        except Exception:
            g.handleScriptException(c, p, script, script)
        finally:
            del sys.path[:2]
    #@+node:ekr.20080514131122.12: *3* @cmd c.recolorCommand
    @cmd('recolor')
    def recolorCommand(self, event=None):
        """Force a full recolor."""
        c = self
        wrapper = c.frame.body.wrapper
        # Setting all text appears to be the only way.
        i, j = wrapper.getSelectionRange()
        ins = wrapper.getInsertPoint()
        wrapper.setAllText(c.p.b)
        wrapper.setSelectionRange(i, j, insert=ins)
    #@+node:ekr.20171124100654.1: *3* c.API
    # These methods are a fundamental, unchanging, part of Leo's API.
    #@+node:ekr.20091001141621.6061: *4* c.Generators
    #@+node:ekr.20091001141621.6043: *5* c.all_nodes & all_unique_nodes
    def all_nodes(self):
        """A generator returning all vnodes in the outline, in outline order."""
        c = self
        for p in c.all_positions():
            yield p.v

    def all_unique_nodes(self):
        """A generator returning each vnode of the outline."""
        c = self
        for p in c.all_unique_positions(copy=False):
            yield p.v

    # Compatibility with old code...

    all_tnodes_iter = all_nodes
    all_vnodes_iter = all_nodes
    all_unique_tnodes_iter = all_unique_nodes
    all_unique_vnodes_iter = all_unique_nodes
    #@+node:ekr.20091001141621.6044: *5* c.all_positions
    def all_positions(self, copy=True):
        """A generator return all positions of the outline, in outline order."""
        c = self
        p = c.rootPosition()
        while p:
            yield p.copy() if copy else p
            p.moveToThreadNext()

    # Compatibility with old code...

    all_positions_iter = all_positions
    allNodes_iter = all_positions
    #@+node:ekr.20191014093239.1: *5* c.all_positions_for_v
    # from leo.core.leoNodes import Position

    def all_positions_for_v(self, v, stack=None):
        """
        Generates all positions p in this outline where p.v is v.
        
        Should be called with stack=None.
        
        The generated positions are not necessarily in outline order.
        
        By Виталије Милошевић (Vitalije Milosevic).
        """
        c = self

        if stack is None:
            stack = []

        if not isinstance(v, leoNodes.VNode):
            g.es_print(f"not a VNode: {v!r}")
            return  # Stop the generator.

        def allinds(v, target_v):
            """Yield all indices i such that v.children[i] == target_v."""
            for i, x in enumerate(v.children):
                if x is target_v:
                    yield i

        def stack2pos(stack):
            """Convert the stack to a position."""
            v, i = stack[-1]
            return leoNodes.Position(v, i, stack[:-1])

        for v2 in set(v.parents):
            for i in allinds(v2, v):
                stack.insert(0, (v, i))
                if v2 is c.hiddenRootNode:
                    yield stack2pos(stack)
                else:
                    yield from c.all_positions_for_v(v2, stack)
                stack.pop(0)
    #@+node:ekr.20161120121226.1: *5* c.all_roots
    def all_roots(self, copy=True, predicate=None):
        """
        A generator yielding *all* the root positions in the outline that
        satisfy the given predicate. p.isAnyAtFileNode is the default
        predicate.

        The generator yields all **root** anywhere in the outline that satisfy
        the predicate. Once a root is found, the generator skips its subtree.
        """
        c = self
        if predicate is None:

            # pylint: disable=function-redefined

            def predicate(p):
                return p.isAnyAtFileNode()

        p = c.rootPosition()
        while p:
            if predicate(p):
                yield p.copy()  # 2017/02/19
                p.moveToNodeAfterTree()
            else:
                p.moveToThreadNext()
    #@+node:ekr.20091001141621.6062: *5* c.all_unique_positions
    def all_unique_positions(self, copy=True):
        """
        A generator return all positions of the outline, in outline order.
        Returns only the first position for each vnode.
        """
        c = self
        p = c.rootPosition()
        seen = set()
        while p:
            if p.v in seen:
                p.moveToNodeAfterTree()
            else:
                seen.add(p.v)
                yield p.copy() if copy else p
                p.moveToThreadNext()

    # Compatibility with old code...

    all_positions_with_unique_tnodes_iter = all_unique_positions
    all_positions_with_unique_vnodes_iter = all_unique_positions
    #@+node:ekr.20161120125322.1: *5* c.all_unique_roots
    def all_unique_roots(self, copy=True, predicate=None):
        """
        A generator yielding all unique root positions in the outline that
        satisfy the given predicate. p.isAnyAtFileNode is the default
        predicate.

        The generator yields all **root** anywhere in the outline that satisfy
        the predicate. Once a root is found, the generator skips its subtree.
        """
        c = self
        if predicate is None:

            # pylint: disable=function-redefined

            def predicate(p):
                return p.isAnyAtFileNode()

        seen = set()
        p = c.rootPosition()
        while p:
            if p.v not in seen and predicate(p):
                seen.add(p.v)
                yield p.copy() if copy else p
                p.moveToNodeAfterTree()
            else:
                p.moveToThreadNext()
    #@+node:ekr.20150316175921.5: *5* c.safe_all_positions
    def safe_all_positions(self, copy=True):
        """
        A generator returning all positions of the outline. This generator does
        *not* assume that vnodes are never their own ancestors.
        """
        c = self
        p = c.rootPosition()  # Make one copy.
        while p:
            yield p.copy() if copy else p
            p.safeMoveToThreadNext()
    #@+node:ekr.20060906211747: *4* c.Getters
    #@+node:ekr.20040803140033: *5* c.currentPosition
    def currentPosition(self):
        """
        Return a copy of the presently selected position or a new null
        position. So c.p.copy() is never necessary.
        """
        c = self
        if hasattr(c, '_currentPosition') and getattr(c, '_currentPosition'):
            # *Always* return a copy.
            return c._currentPosition.copy()
        return c.rootPosition()

    # For compatibiility with old scripts...

    currentVnode = currentPosition
    #@+node:ekr.20190506060937.1: *5* c.dumpExpanded
    @cmd('dump-expanded')
    def dump_expanded(self, event):
        c = event.get('c')
        if not c:
            return
        g.es_print('dump-expanded...')
        for p in c.all_positions():
            if p.v.expandedPositions:
                indent = ' ' * p.level()
                print(f"{indent}{p.h}")
                g.printObj(p.v.expandedPositions, indent=indent)
    #@+node:ekr.20040306220230.1: *5* c.edit_widget
    def edit_widget(self, p):
        c = self
        return p and c.frame.tree.edit_widget(p)
    #@+node:ekr.20031218072017.2986: *5* c.fileName & relativeFileName & shortFileName
    # Compatibility with scripts

    def fileName(self):
        s = self.mFileName or ""
        if g.isWindows:
            s = s.replace('\\', '/')
        return s

    def relativeFileName(self):
        return self.mRelativeFileName or self.mFileName

    def shortFileName(self):
        return g.shortFileName(self.mFileName)

    shortFilename = shortFileName
    #@+node:ekr.20070615070925.1: *5* c.firstVisible
    def firstVisible(self):
        """Move to the first visible node of the present chapter or hoist."""
        c = self; p = c.p
        while 1:
            back = p.visBack(c)
            if back and back.isVisible(c):
                p = back
            else: break
        return p
    #@+node:ekr.20171123135625.29: *5* c.getBodyLines
    def getBodyLines(self, expandSelection=False):
        """
        Return head,lines,tail where:

        before is string containg all the lines before the selected text
        (or the text before the insert point if no selection) lines is a
        list of lines containing the selected text (or the line containing
        the insert point if no selection) after is a string all lines
        after the selected text (or the text after the insert point if no
        selection)
        """
        c = self
        body = c.frame.body
        w = body.wrapper
        oldVview = w.getYScrollPosition()
        if expandSelection:
            s = w.getAllText()
            head = tail = ''
            oldSel = 0, len(s)
            lines = g.splitLines(s)  # Retain the newlines of each line.
        else:
            # Note: lines is the entire line containing the insert point if no selection.
            head, s, tail = body.getSelectionLines()
            lines = g.splitLines(s)  # Retain the newlines of each line.
            # Expand the selection.
            i = len(head)
            j = max(i, len(head) + len(s) - 1)
            oldSel = i, j
        return head, lines, tail, oldSel, oldVview  # string,list,string,tuple.
    #@+node:ekr.20150417073117.1: *5* c.getTabWidth
    def getTabWidth(self, p):
        """Return the tab width in effect at p."""
        c = self
        val = g.scanAllAtTabWidthDirectives(c, p)
        return val
    #@+node:ekr.20040803112200: *5* c.is...Position
    #@+node:ekr.20040803155551: *6* c.currentPositionIsRootPosition
    def currentPositionIsRootPosition(self):
        """Return True if the current position is the root position.

        This method is called during idle time, so not generating positions
        here fixes a major leak.
        """
        c = self
        root = c.rootPosition()
        return c._currentPosition and root and c._currentPosition == root
        # return (
            # c._currentPosition and c._rootPosition and
            # c._currentPosition == c._rootPosition)
    #@+node:ekr.20040803160656: *6* c.currentPositionHasNext
    def currentPositionHasNext(self):
        """Return True if the current position is the root position.

        This method is called during idle time, so not generating positions
        here fixes a major leak.
        """
        c = self; current = c._currentPosition
        return current and current.hasNext()
    #@+node:ekr.20040803112450: *6* c.isCurrentPosition
    def isCurrentPosition(self, p):
        c = self
        if p is None or c._currentPosition is None:
            return False
        return p == c._currentPosition
    #@+node:ekr.20040803112450.1: *6* c.isRootPosition
    def isRootPosition(self, p):
        c = self
        root = c.rootPosition()
        return p and root and p == root  # 2011/03/03
    #@+node:ekr.20031218072017.2987: *5* c.isChanged
    def isChanged(self):
        return self.changed
    #@+node:ekr.20140106215321.16676: *5* c.lastTopLevel
    def lastTopLevel(self):
        """Return the last top-level position in the outline."""
        c = self
        p = c.rootPosition()
        while p.hasNext():
            p.moveToNext()
        return p
    #@+node:ekr.20031218072017.4146: *5* c.lastVisible
    def lastVisible(self):
        """Move to the last visible node of the present chapter or hoist."""
        c = self; p = c.p
        while 1:
            next = p.visNext(c)
            if next and next.isVisible(c):
                p = next
            else: break
        return p
    #@+node:ekr.20040311094927: *5* c.nullPosition
    def nullPosition(self):
        """
        New in Leo 5.5: Return None.
        Using empty positions masks problems in program logic.

        In fact, there are no longer any calls to this method in Leo's core.
        """
        g.trace('This method is deprecated. Instead, just use None.')
        # pylint complains if we return None.
    #@+node:ekr.20040307104131.3: *5* c.positionExists
    def positionExists(self, p, root=None, trace=False):
        """Return True if a position exists in c's tree"""
        if not p or not p.v: return False

        rstack = root.stack + [(root.v, root._childIndex)] if root else []
        pstack = p.stack + [(p.v, p._childIndex)]

        if len(rstack) > len(pstack): return False

        par = self.hiddenRootNode
        for j, x in enumerate(pstack):
            if j < len(rstack) and x != rstack[j]: return False
            v, i = x
            if i >= len(par.children) or v is not par.children[i]:
                return False
            par = v
        return True
    #@+node:ekr.20160427153457.1: *6* c.dumpPosition
    def dumpPosition(self, p):
        """Dump position p and it's ancestors."""
        g.trace('=====', p.h, p._childIndex)
        for i, data in enumerate(p.stack):
            v, childIndex = data
            print(f"{i} {childIndex} {v._headString}")
    #@+node:ekr.20040803140033.2: *5* c.rootPosition
    _rootCount = 0

    def rootPosition(self):
        """Return the root position.

        Root position is the first position in the document. Other
        top level positions are siblings of this node.
        """
        c = self
        # 2011/02/25: Compute the position directly.
        if c.hiddenRootNode.children:
            v = c.hiddenRootNode.children[0]
            return leoNodes.Position(v, childIndex=0, stack=None)
        return None

    # For compatibiility with old scripts...

    rootVnode = rootPosition
    findRootPosition = rootPosition
    #@+node:ekr.20131017174814.17480: *5* c.shouldBeExpanded
    def shouldBeExpanded(self, p):
        """Return True if the node at position p should be expanded."""
        c, v = self, p.v
        if not p.hasChildren():
            return False
        # Always clear non-existent positions.
        v.expandedPositions = [z for z in v.expandedPositions if c.positionExists(z)]
        if not p.isCloned():
            # Do not call p.isExpanded here! It calls this method.
            return p.v.isExpanded()
        if p.isAncestorOf(c.p):
            return True
        for p2 in v.expandedPositions:
            if p == p2:
                return True
        return False
    #@+node:ekr.20070609122713: *5* c.visLimit
    def visLimit(self):
        """
        Return the topmost visible node.
        This is affected by chapters and hoists.
        """
        c = self; cc = c.chapterController
        if c.hoistStack:
            bunch = c.hoistStack[-1]
            p = bunch.p
            limitIsVisible = not cc or not p.h.startswith('@chapter')
            return p, limitIsVisible
        return None, None
    #@+node:tbrown.20091206142842.10296: *5* c.vnode2allPositions
    def vnode2allPositions(self, v):
        """Given a VNode v, find all valid positions p such that p.v = v.

        Not really all, just all for each of v's distinct immediate parents.
        """
        c = self
        context = v.context  # v's commander.
        assert(c == context)
        positions = []
        for immediate in v.parents:
            if v in immediate.children:
                n = immediate.children.index(v)
            else:
                continue
            stack = [(v, n)]
            while immediate.parents:
                parent = immediate.parents[0]
                if immediate in parent.children:
                    n = parent.children.index(immediate)
                else:
                    break
                stack.insert(0, (immediate, n),)
                immediate = parent
            else:
                v, n = stack.pop()
                p = leoNodes.Position(v, n, stack)
                positions.append(p)
        return positions
    #@+node:ekr.20090107113956.1: *5* c.vnode2position
    def vnode2position(self, v):
        """Given a VNode v, construct a valid position p such that p.v = v.
        """
        c = self
        context = v.context  # v's commander.
        assert(c == context)
        stack = []
        while v.parents:
            parent = v.parents[0]
            if v in parent.children:
                n = parent.children.index(v)
            else:
                return None
            stack.insert(0, (v, n),)
            v = parent
        # v.parents includes the hidden root node.
        if not stack:
            # a VNode not in the tree
            return None
        v, n = stack.pop()
        p = leoNodes.Position(v, n, stack)
        return p
    #@+node:ekr.20090130135126.1: *4* c.Properties
    def __get_p(self):
        c = self
        return c.currentPosition()

    p = property(
        __get_p,  # No setter.
        doc="commander current position property")
    #@+node:ekr.20060906211747.1: *4* c.Setters
    #@+node:ekr.20040315032503: *5* c.appendStringToBody
    def appendStringToBody(self, p, s):
        c = self
        if not s: return
        body = p.b
        s = g.toUnicode(s)
        c.setBodyString(p, body + s)
    #@+node:ekr.20031218072017.2984: *5* c.clearAllMarked
    def clearAllMarked(self):
        c = self
        for p in c.all_unique_positions(copy=False):
            p.v.clearMarked()
    #@+node:ekr.20031218072017.2985: *5* c.clearAllVisited
    def clearAllVisited(self):
        c = self
        for p in c.all_unique_positions(copy=False):
            p.v.clearVisited()
            p.v.clearWriteBit()
    #@+node:ekr.20191215044636.1: *5* c.clearChanged
    def clearChanged(self):
        """clear the marker that indicates that the .leo file has been changed."""
        c = self
        if not c.frame:
            return
        c.changed = False
        if c.loading:
            return  # don't update while loading.
        # Clear all dirty bits _before_ setting the caption.
        for v in c.all_unique_nodes():
            v.clearDirty()
        c.changed = False
        # Do nothing for null frames.
        assert c.gui
        if c.gui.guiName() == 'nullGui':
            return
        if not c.frame.top:
            return
        master = getattr(c.frame.top, 'leo_master', None)
        if master:
            master.setChanged(c, False)
                # LeoTabbedTopLevel.setChanged.
        s = c.frame.getTitle()
        if len(s) > 2 and s[0:2] == "* ":
            c.frame.setTitle(s[2:])
    #@+node:ekr.20060906211138: *5* c.clearMarked
    def clearMarked(self, p):
        c = self
        p.v.clearMarked()
        g.doHook("clear-mark", c=c, p=p)
    #@+node:ekr.20040305223522: *5* c.setBodyString
    def setBodyString(self, p, s):
        c, v = self, p.v
        if not c or not v:
            return
        s = g.toUnicode(s)
        current = c.p
        # 1/22/05: Major change: the previous test was: 'if p == current:'
        # This worked because commands work on the presently selected node.
        # But setRecentFiles may change a _clone_ of the selected node!
        if current and p.v == current.v:
            # Revert to previous code, but force an empty selection.
            c.frame.body.setSelectionAreas(s, None, None)
            w = c.frame.body.wrapper
            i = w.getInsertPoint()
            w.setSelectionRange(i, i)
            # This code destoys all tags, so we must recolor.
            c.recolor()
        # Keep the body text in the VNode up-to-date.
        if v.b != s:
            v.setBodyString(s)
            v.setSelection(0, 0)
            p.setDirty()
            if not c.isChanged():
                c.setChanged()
            c.redraw_after_icons_changed()
    #@+node:ekr.20031218072017.2989: *5* c.setChanged
    def setChanged(self, redrawFlag=True):
        """Set the marker that indicates that the .leo file has been changed."""
        c = self
        if not c.frame:
            return
        c.changed = True
        if c.loading:
            return  # don't update while loading.
        # Do nothing for null frames.
        assert c.gui
        if c.gui.guiName() == 'nullGui':
            return
        if not c.frame.top:
            return
        if not redrawFlag:  # Prevent flash when fixing #387.
            return
        master = getattr(c.frame.top, 'leo_master', None)
        if master:
            master.setChanged(c, True)
                # LeoTabbedTopLevel.setChanged.
        s = c.frame.getTitle()
        if len(s) > 2 and s[0] != '*':
            c.frame.setTitle("* " + s)
    #@+node:ekr.20040803140033.1: *5* c.setCurrentPosition
    _currentCount = 0

    def setCurrentPosition(self, p):
        """
        Set the presently selected position. For internal use only.
        Client code should use c.selectPosition instead.
        """
        c = self
        if not p:
            g.trace('===== no p', g.callers())
            return
        if c.positionExists(p):
            if c._currentPosition and p == c._currentPosition:
                pass  # We have already made a copy.
            else:  # Make a copy _now_
                c._currentPosition = p.copy()
        else:  # 2011/02/25:
            c._currentPosition = c.rootPosition()
            g.trace(f"Invalid position: {repr(p and p.h)}")
            g.trace(g.callers())
            # Don't kill unit tests for this kind of problem.

    # For compatibiility with old scripts.

    setCurrentVnode = setCurrentPosition
    #@+node:ekr.20040305223225: *5* c.setHeadString
    def setHeadString(self, p, s):
        """
        Set the p's headline and the corresponding tree widget to s.

        This is used in by unit tests to restore the outline.
        """
        c = self
        p.initHeadString(s)
        p.setDirty()
        # Change the actual tree widget so
        # A later call to c.endEditing or c.redraw will use s.
        c.frame.tree.setHeadline(p, s)
    #@+node:ekr.20060109164136: *5* c.setLog
    def setLog(self):
        c = self
        if c.exists:
            try:
                # c.frame or c.frame.log may not exist.
                g.app.setLog(c.frame.log)
            except AttributeError:
                pass
    #@+node:ekr.20060906211138.1: *5* c.setMarked (calls hook)
    def setMarked(self, p):
        c = self
        p.setMarked()
        p.setDirty()  # Defensive programming.
        g.doHook("set-mark", c=c, p=p)
    #@+node:ekr.20040803140033.3: *5* c.setRootPosition (A do-nothing)
    def setRootPosition(self, unused_p=None):
        """Set c._rootPosition."""
        # 2011/03/03: No longer used.
    #@+node:ekr.20060906131836: *5* c.setRootVnode (A do-nothing)
    def setRootVnode(self, v):
        pass
        # c = self
        # # 2011/02/25: c.setRootPosition needs no arguments.
        # c.setRootPosition()
    #@+node:ekr.20040311173238: *5* c.topPosition & c.setTopPosition
    def topPosition(self):
        """Return the root position."""
        c = self
        if c._topPosition:
            return c._topPosition.copy()
        return None

    def setTopPosition(self, p):
        """Set the root positioin."""
        c = self
        if p:
            c._topPosition = p.copy()
        else:
            c._topPosition = None

    # Define these for compatibiility with old scripts...

    topVnode = topPosition
    setTopVnode = setTopPosition
    #@+node:ekr.20031218072017.3404: *5* c.trimTrailingLines
    def trimTrailingLines(self, p):
        """Trims trailing blank lines from a node.

        It is surprising difficult to do this during Untangle."""
        c = self
        body = p.b
        lines = body.split('\n')
        i = len(lines) - 1; changed = False
        while i >= 0:
            line = lines[i]
            j = g.skip_ws(line, 0)
            if j + 1 == len(line):
                del lines[i]
                i -= 1; changed = True
            else: break
        if changed:
            body = ''.join(body) + '\n'  # Add back one last newline.
            c.setBodyString(p, body)
            # Don't set the dirty bit: it would just be annoying.
    #@+node:ekr.20171124081419.1: *3* c.Check Outline...
    #@+node:ekr.20141024211256.22: *4* c.checkGnxs
    def checkGnxs(self):
        """
        Check the consistency of all gnx's and remove any tnodeLists.
        Reallocate gnx's for duplicates or empty gnx's.
        Return the number of structure_errors found.
        """
        c = self
        d = {}  # Keys are gnx's; values are lists of vnodes with that gnx.
        ni = g.app.nodeIndices
        t1 = time.time()

        def new_gnx(v):
            """Set v.fileIndex."""
            v.fileIndex = ni.getNewIndex(v)

        count, gnx_errors = 0, 0
        for p in c.safe_all_positions(copy=False):
            count += 1
            v = p.v
            if hasattr(v, "tnodeList"):
                delattr(v, "tnodeList")
                v._p_changed = True
            gnx = v.fileIndex
            if gnx:
                aSet = d.get(gnx, set())
                aSet.add(v)
                d[gnx] = aSet
            else:
                gnx_errors += 1
                new_gnx(v)
                g.es_print(f"empty v.fileIndex: {v} new: {p.v.gnx!r}", color='red')
        for gnx in sorted(d.keys()):
            aList = list(d.get(gnx))
            if len(aList) != 1:
                print('\nc.checkGnxs...')
                g.es_print(f"multiple vnodes with gnx: {gnx!r}", color='red')
                for v in aList:
                    gnx_errors += 1
                    g.es_print(f"id(v): {id(v)} gnx: {v.fileIndex} {v.h}", color='red')
                    new_gnx(v)
        ok = not gnx_errors and not g.app.structure_errors
        t2 = time.time()
        if not ok:
            g.es_print(
                f"check-outline ERROR! {c.shortFileName()} "
                f"{count} nodes, "
                f"{gnx_errors} gnx errors, "
                f"{g.app.structure_errors} "
                f"structure errors",
                color='red'
            )
        elif c.verbose_check_outline and not g.unitTesting:
            print(
                f"check-outline OK: {t2 - t1:4.2f} sec. "
                f"{c.shortFileName()} {count} nodes")
        return g.app.structure_errors
    #@+node:ekr.20150318131947.7: *4* c.checkLinks & helpers
    def checkLinks(self):
        """Check the consistency of all links in the outline."""
        c = self
        t1 = time.time()
        count, errors = 0, 0
        for p in c.safe_all_positions():
            count += 1
            # try:
            if not c.checkThreadLinks(p):
                errors += 1
                break
            if not c.checkSiblings(p):
                errors += 1
                break
            if not c.checkParentAndChildren(p):
                errors += 1
                break
            # except AssertionError:
                # errors += 1
                # junk, value, junk = sys.exc_info()
                # g.error("test failed at position %s\n%s" % (repr(p), value))
        t2 = time.time()
        g.es_print(
            f"check-links: {t2 - t1:4.2f} sec. "
            f"{c.shortFileName()} {count} nodes", color='blue')
        return errors
    #@+node:ekr.20040314035615.2: *5* c.checkParentAndChildren
    def checkParentAndChildren(self, p):
        """Check consistency of parent and child data structures."""
        c = self

        def _assert(condition):
            return g._assert(condition, show_callers=False)

        def dump(p):
            if p and p.v:
                p.v.dump()
            elif p:
                print('<no p.v>')
            else:
                print('<no p>')
            if g.unitTesting:
                assert False, g.callers()

        if p.hasParent():
            n = p.childIndex()
            if not _assert(p == p.parent().moveToNthChild(n)):
                g.trace(f"p != parent().moveToNthChild({n})")
                dump(p)
                dump(p.parent())
                return False
        if p.level() > 0 and not _assert(p.v.parents):
            g.trace("no parents")
            dump(p)
            return False
        for child in p.children():
            if not c.checkParentAndChildren(child):
                return False
            if not _assert(p == child.parent()):
                g.trace("p != child.parent()")
                dump(p)
                dump(child.parent())
                return False
        if p.hasNext():
            if not _assert(p.next().parent() == p.parent()):
                g.trace("p.next().parent() != p.parent()")
                dump(p.next().parent())
                dump(p.parent())
                return False
        if p.hasBack():
            if not _assert(p.back().parent() == p.parent()):
                g.trace("p.back().parent() != parent()")
                dump(p.back().parent())
                dump(p.parent())
                return False
        # Check consistency of parent and children arrays.
        # Every nodes gets visited, so a strong test need only check consistency
        # between p and its parent, not between p and its children.
        parent_v = p._parentVnode()
        n = p.childIndex()
        if not _assert(parent_v.children[n] == p.v):
            g.trace("parent_v.children[n] != p.v")
            parent_v.dump()
            p.v.dump()
            return False
        return True
    #@+node:ekr.20040314035615.1: *5* c.checkSiblings
    def checkSiblings(self, p):
        """Check the consistency of next and back links."""
        back = p.back()
        next = p.next()
        if back:
            if not g._assert(p == back.next()):
                g.trace(
                    f"p!=p.back().next()\n"
                    f"     back: {back}\n"
                    f"back.next: {back.next()}")
                return False
        if next:
            if not g._assert(p == next.back()):
                g.trace(
                    f"p!=p.next().back\n"
                    f"     next: {next}\n"
                    f"next.back: {next.back()}")
                return False
        return True
    #@+node:ekr.20040314035615: *5* c.checkThreadLinks
    def checkThreadLinks(self, p):
        """Check consistency of threadNext & threadBack links."""
        threadBack = p.threadBack()
        threadNext = p.threadNext()
        if threadBack:
            if not g._assert(p == threadBack.threadNext()):
                g.trace("p!=p.threadBack().threadNext()")
                return False
        if threadNext:
            if not g._assert(p == threadNext.threadBack()):
                g.trace("p!=p.threadNext().threadBack()")
                return False
        return True
    #@+node:ekr.20031218072017.1760: *4* c.checkMoveWithParentWithWarning & c.checkDrag
    #@+node:ekr.20070910105044: *5* c.checkMoveWithParentWithWarning
    def checkMoveWithParentWithWarning(self, root, parent, warningFlag):
        """Return False if root or any of root's descendents is a clone of
        parent or any of parents ancestors."""
        c = self
        message = "Illegal move or drag: no clone may contain a clone of itself"
        clonedVnodes = {}
        for ancestor in parent.self_and_parents(copy=False):
            if ancestor.isCloned():
                v = ancestor.v
                clonedVnodes[v] = v
        if not clonedVnodes:
            return True
        for p in root.self_and_subtree(copy=False):
            if p.isCloned() and clonedVnodes.get(p.v):
                if g.app.unitTesting:
                    g.app.unitTestDict['checkMoveWithParentWithWarning'] = True
                elif warningFlag:
                    c.alert(message)
                return False
        return True
    #@+node:ekr.20070910105044.1: *5* c.checkDrag
    def checkDrag(self, root, target):
        """Return False if target is any descendant of root."""
        c = self
        message = "Can not drag a node into its descendant tree."
        for z in root.subtree():
            if z == target:
                if g.app.unitTesting:
                    g.app.unitTestDict['checkMoveWithParentWithWarning'] = True
                else:
                    c.alert(message)
                return False
        return True
    #@+node:ekr.20031218072017.2072: *4* c.checkOutline
    def checkOutline(self, event=None, check_links=False):
        """
        Check for errors in the outline.
        Return the count of serious structure errors.
        """
        # The check-outline command sets check_links = True.
        c = self
        g.app.structure_errors = 0
        structure_errors = c.checkGnxs()
        if check_links and not structure_errors:
            structure_errors += c.checkLinks()
        return structure_errors
    #@+node:ekr.20031218072017.1765: *4* c.validateOutline
    # Makes sure all nodes are valid.

    def validateOutline(self, event=None):
        c = self
        if not g.app.validate_outline:
            return True
        root = c.rootPosition()
        parent = None
        if root:
            return root.validateOutlineWithParent(parent)
        return True
    #@+node:ekr.20040723094220: *3* c.Check Python code
    # This code is no longer used by any Leo command,
    # but it will be retained for use of scripts.
    #@+node:ekr.20040723094220.1: *4* c.checkAllPythonCode
    def checkAllPythonCode(self, event=None, unittest=False, ignoreAtIgnore=True):
        """Check all nodes in the selected tree for syntax and tab errors."""
        c = self; count = 0; result = "ok"
        for p in c.all_unique_positions():
            count += 1
            if not unittest:
                #@+<< print dots >>
                #@+node:ekr.20040723094220.2: *5* << print dots >>
                if count % 100 == 0:
                    g.es('', '.', newline=False)
                if count % 2000 == 0:
                    g.enl()
                #@-<< print dots >>
            if g.scanForAtLanguage(c, p) == "python":
                if not g.scanForAtSettings(p) and (
                    not ignoreAtIgnore or not g.scanForAtIgnore(c, p)
                ):
                    try:
                        c.checkPythonNode(p, unittest)
                    except(SyntaxError, tokenize.TokenError, tabnanny.NannyNag):
                        result = "error"  # Continue to check.
                    except Exception:
                        return "surprise"  # abort
                    if unittest and result != "ok":
                        g.pr(f"Syntax error in {p.h}")
                        return result  # End the unit test: it has failed.
        if not unittest:
            g.blue("check complete")
        return result
    #@+node:ekr.20040723094220.3: *4* c.checkPythonCode
    def checkPythonCode(self, event=None,
        unittest=False, ignoreAtIgnore=True,
        suppressErrors=False, checkOnSave=False
    ):
        """Check the selected tree for syntax and tab errors."""
        c = self; count = 0; result = "ok"
        if not unittest:
            g.es("checking Python code   ")
        for p in c.p.self_and_subtree():
            count += 1
            if not unittest and not checkOnSave:
                #@+<< print dots >>
                #@+node:ekr.20040723094220.4: *5* << print dots >>
                if count % 100 == 0:
                    g.es('', '.', newline=False)
                if count % 2000 == 0:
                    g.enl()
                #@-<< print dots >>
            if g.scanForAtLanguage(c, p) == "python":
                if not ignoreAtIgnore or not g.scanForAtIgnore(c, p):
                    try:
                        c.checkPythonNode(p, unittest, suppressErrors)
                    except(SyntaxError, tokenize.TokenError, tabnanny.NannyNag):
                        result = "error"  # Continue to check.
                    except Exception:
                        return "surprise"  # abort
        if not unittest:
            g.blue("check complete")
        # We _can_ return a result for unit tests because we aren't using doCommand.
        return result
    #@+node:ekr.20040723094220.5: *4* c.checkPythonNode
    def checkPythonNode(self, p, unittest=False, suppressErrors=False):
        c = self; h = p.h
        # Call getScript to ignore directives and section references.
        body = g.getScript(c, p.copy())
        if not body: return
        try:
            fn = f"<node: {p.h}>"
            compile(body + '\n', fn, 'exec')
            c.tabNannyNode(p, h, body, unittest, suppressErrors)
        except SyntaxError:
            if not suppressErrors:
                g.warning(f"Syntax error in: {h}")
                g.es_exception(full=False, color="black")
            if unittest: raise
        except Exception:
            g.es_print('unexpected exception')
            g.es_exception()
            if unittest: raise
    #@+node:ekr.20040723094220.6: *4* c.tabNannyNode
    # This code is based on tabnanny.check.

    def tabNannyNode(self, p, headline, body, unittest=False, suppressErrors=False):
        """Check indentation using tabnanny."""
        # c = self
        try:
            readline = g.ReadLinesClass(body).next
            tabnanny.process_tokens(tokenize.generate_tokens(readline))
        except IndentationError:
            junk, msg, junk = sys.exc_info()
            if not suppressErrors:
                g.warning("IndentationError in", headline)
                g.es('', msg)
            if unittest: raise
        except tokenize.TokenError:
            junk, msg, junk = sys.exc_info()
            if not suppressErrors:
                g.warning("TokenError in", headline)
                g.es('', msg)
            if unittest: raise
        except tabnanny.NannyNag:
            junk, nag, junk = sys.exc_info()
            if not suppressErrors:
                badline = nag.get_lineno()
                line = nag.get_line()
                message = nag.get_msg()
                g.warning("indentation error in", headline, "line", badline)
                g.es(message)
                line2 = repr(str(line))[1:-1]
                g.es("offending line:\n", line2)
            if unittest: raise
        except Exception:
            g.trace("unexpected exception")
            g.es_exception()
            if unittest: raise
    #@+node:ekr.20171123200644.1: *3* c.Convenience methods
    #@+node:ekr.20171123135625.39: *4* c.getTime
    def getTime(self, body=True):
        c = self
        default_format = "%m/%d/%Y %H:%M:%S"  # E.g., 1/30/2003 8:31:55
        # Try to get the format string from settings.
        if body:
            format = c.config.getString("body-time-format-string")
            gmt = c.config.getBool("body-gmt-time")
        else:
            format = c.config.getString("headline-time-format-string")
            gmt = c.config.getBool("headline-gmt-time")
        if format is None:
            format = default_format
        try:
            # import time
            if gmt:
                s = time.strftime(format, time.gmtime())
            else:
                s = time.strftime(format, time.localtime())
        except(ImportError, NameError):
            g.warning("time.strftime not available on this platform")
            return ""
        except Exception:
            g.es_exception()  # Probably a bad format string in leoSettings.leo.
            s = time.strftime(default_format, time.gmtime())
        return s
    #@+node:ekr.20171123135625.10: *4* c.goToLineNumber & goToScriptLineNumber
    def goToLineNumber(self, n):
        """
        Go to line n (zero-based) of a script.
        A convenience method called from g.handleScriptException.
        """
        c = self
        c.gotoCommands.find_file_line(n)

    def goToScriptLineNumber(self, n, p):
        """
        Go to line n (zero-based) of a script.
        A convenience method called from g.handleScriptException.
        """
        c = self
        c.gotoCommands.find_script_line(n, p)
    #@+node:ekr.20090103070824.9: *4* c.setFileTimeStamp
    def setFileTimeStamp(self, fn):
        """Update the timestamp for fn.."""
        # c = self
        if g.app.externalFilesController:
            g.app.externalFilesController.set_time(fn)
    #@+node:ekr.20031218072017.3000: *4* c.updateSyntaxColorer
    def updateSyntaxColorer(self, v):
        self.frame.body.updateSyntaxColorer(v)
    #@+node:ekr.20180503110307.1: *4* c.interactive*
    #@+node:ekr.20180504075937.1: *5* c.interactive
    def interactive(self, callback, event, prompts):
        #@+<< c.interactive docstring >>
        #@+node:ekr.20180503131222.1: *6* << c.interactive docstring >>
        """
        c.interactive: Prompt for up to three arguments from the minibuffer.

        The number of prompts determines the number of arguments.

        Use the @command decorator to define commands.  Examples:

            @g.command('i3')
            def i3_command(event):
                c = event.get('c')
                if not c: return
                    
                def callback(args, c, event):
                    g.trace(args)
                    c.bodyWantsFocus()
            
                c.interactive(callback, event,
                    prompts=['Arg1: ', ' Arg2: ', ' Arg3: '])
        """
        #@-<< c.interactive docstring >>
        #
        # This pathetic code should be generalized,
        # but it's not as easy as one might imagine.
        c = self
        d = {1: c.interactive1, 2: c.interactive2, 3: c.interactive3,}
        f = d.get(len(prompts))
        if f:
            f(callback, event, prompts)
        else:
            g.trace('At most 3 arguments are supported.')
    #@+node:ekr.20180503111213.1: *5* c.interactive1
    def interactive1(self, callback, event, prompts):

        c, k = self, self.k
        prompt = prompts[0]

        def state1(event):
            callback(args=[k.arg], c=c, event=event)
            k.clearState()
            k.resetLabel()
            k.showStateAndMode()

        k.setLabelBlue(prompt)
        k.get1Arg(event, handler=state1)
    #@+node:ekr.20180503111249.1: *5* c.interactive2
    def interactive2(self, callback, event, prompts):

        c, d, k = self, {}, self.k
        prompt1, prompt2 = prompts

        def state1(event):
            d['arg1'] = k.arg
            k.extendLabel(prompt2, select=False, protect=True)
            k.getNextArg(handler=state2)

        def state2(event):
            callback(args=[d.get('arg1'), k.arg], c=c, event=event)
            k.clearState()
            k.resetLabel()
            k.showStateAndMode()

        k.setLabelBlue(prompt1)
        k.get1Arg(event, handler=state1)
    #@+node:ekr.20180503111249.2: *5* c.interactive3
    def interactive3(self, callback, event, prompts):

        c, d, k = self, {}, self.k
        prompt1, prompt2, prompt3 = prompts

        def state1(event):
            d['arg1'] = k.arg
            k.extendLabel(prompt2, select=False, protect=True)
            k.getNextArg(handler=state2)

        def state2(event):
            d['arg2'] = k.arg
            k.extendLabel(prompt3, select=False, protect=True)
            k.get1Arg(event, handler=state3)
                # Restart.

        def state3(event):
            args = [d.get('arg1'), d.get('arg2'), k.arg]
            callback(args=args, c=c, event=event)
            k.clearState()
            k.resetLabel()
            k.showStateAndMode()

        k.setLabelBlue(prompt1)
        k.get1Arg(event, handler=state1)
    #@+node:ekr.20080901124540.1: *3* c.Directive scanning
    # These are all new in Leo 4.5.1.
    #@+node:ekr.20171123135625.33: *4* c.getLanguageAtCursor
    def getLanguageAtCursor(self, p, language):
        """
        Return the language in effect at the present insert point.
        Use the language argument as a default if no @language directive seen.
        """
        c = self
        tag = '@language'
        w = c.frame.body.wrapper
        ins = w.getInsertPoint()
        n = 0
        for s in g.splitLines(p.b):
            if g.match_word(s, 0, tag):
                i = g.skip_ws(s, len(tag))
                j = g.skip_id(s, i)
                language = s[i:j]
            if n <= ins < n + len(s):
                break
            else:
                n += len(s)
        return language
    #@+node:ekr.20081006100835.1: *4* c.getNodePath & c.getNodeFileName
    # Not used in Leo's core.
    # Used by the UNl plugin.  Does not need to create a path.

    def getNodePath(self, p):
        """Return the path in effect at node p."""
        c = self
        aList = g.get_directives_dict_list(p)
        path = c.scanAtPathDirectives(aList)
        return path

    # Not used in Leo's core.

    def getNodeFileName(self, p):
        """
        Return the full file name at node p,
        including effects of all @path directives.
        Return None if p is no kind of @file node.
        """
        c = self
        path = g.scanAllAtPathDirectives(c, p)
        name = ''
        for p in p.self_and_parents(copy=False):
            name = p.anyAtFileNodeName()
            if name: break
        if name:
            # The commander method supports {{expr}}; the global function does not.
            path = c.expand_path_expression(path)  # #1341.
            name = c.expand_path_expression(name)  # #1341.
            name = g.os_path_finalize_join(path, name)
        return name
    #@+node:ekr.20171123135625.32: *4* c.hasAmbiguousLangauge
    def hasAmbiguousLanguage(self, p):
        """Return True if p.b contains different @language directives."""
        # c = self
        languages, tag = set(), '@language'
        for s in g.splitLines(p.b):
            if g.match_word(s, 0, tag):
                i = g.skip_ws(s, len(tag))
                j = g.skip_id(s, i)
                word = s[i:j]
                languages.add(word)
        return len(list(languages)) > 1
    #@+node:ekr.20080922124033.5: *4* c.os_path_finalize and c.os_path_finalize_join (deprecated)
    deprecated_messages = []

    def os_path_finalize(self, path, **keys):
        """
        c.os_path_finalize is deprecated.
        It no longer evaluates path expressions.
        """
        callers = g.callers(2)
        if callers not in self.deprecated_messages:
            self.deprecated_messages.append(callers)
            g.es_print(
                f"\nc.os_path_finalize{' '*5} is deprecated. called from: {callers}")
        return g.os_path_finalize(path, **keys)

    def os_path_finalize_join(self, *args, **keys):
        """
        c.os_path_finalize_join is deprecated.
        It no longer evaluates path expressions.
        """
        callers = g.callers(2)
        if callers not in self.deprecated_messages:
            self.deprecated_messages.append(callers)
            g.es_print(
                f"\nc.os_path_finalize_join is deprecated. called from: {callers}")
        return g.os_path_finalize_join(*args, **keys)
    #@+node:ekr.20080827175609.39: *4* c.scanAllDirectives
    #@@nobeautify

    def scanAllDirectives(self,p=None):
        """
        Scan p and ancestors for directives.

        Returns a dict containing the results, including defaults.
        """
        c = self
        p = p or c.p
        # Set defaults
        language = c.target_language and c.target_language.lower()
        lang_dict = {
            'language':language,
            'delims':g.set_delims_from_language(language),
        }
        wrap = c.config.getBool("body-pane-wraps")
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
            d[key] = default if val is None else val
        # Post process: do *not* set commander ivars.
        lang_dict = d.get('lang-dict')
        d = {
            "delims":       lang_dict.get('delims'),
            "encoding":     d.get('encoding'),
            "language":     lang_dict.get('language'),
            "lineending":   d.get('lineending'),
            "pagewidth":    d.get('pagewidth'),
            "path":         d.get('path'), # Redundant: or g.getBaseDirectory(c),
            "tabwidth":     d.get('tabwidth'),
            "pluginsList":  [], # No longer used.
            "wrap":         d.get('wrap'),
        }
        return d
    #@+node:ekr.20080828103146.15: *4* c.scanAtPathDirectives
    def scanAtPathDirectives(self, aList):
        """
        Scan aList for @path directives.
        Return a reasonable default if no @path directive is found.
        """
        c = self
        c.scanAtPathDirectivesCount += 1  # An important statistic.
        # Step 1: Compute the starting path.
        # The correct fallback directory is the absolute path to the base.
        if c.openDirectory:  # Bug fix: 2008/9/18
            base = c.openDirectory
        else:
            base = g.app.config.relative_path_base_directory
            if base and base == "!":
                base = g.app.loadDir
            elif base and base == ".":
                base = c.openDirectory
        base = c.expand_path_expression(base)  # #1341:
        absbase = g.os_path_finalize_join(g.app.loadDir, base)  # #1341:
        # Step 2: look for @path directives.
        paths = []
        for d in aList:
            # Look for @path directives.
            path = d.get('path')
            warning = d.get('@path_in_body')
            if path is not None:  # retain empty paths for warnings.
                # Convert "path" or <path> to path.
                path = g.stripPathCruft(path)
                if path and not warning:
                    path = c.expand_path_expression(path)  # #1341.
                    paths.append(path)
                # We will silently ignore empty @path directives.
        # Add absbase and reverse the list.
        paths.append(absbase)
        paths.reverse()
        # Step 3: Compute the full, effective, absolute path.
        path = g.os_path_finalize_join(*paths)  # #1341.
        return path or g.getBaseDirectory(c)
            # 2010/10/22: A useful default.
    #@+node:ekr.20080828103146.12: *4* c.scanAtRootDirectives (no longer used)
    # No longer used. Was called only by scanLanguageDirectives.

    def scanAtRootDirectives(self, aList):
        """Scan aList for @root-code and @root-doc directives."""
        c = self
        # To keep pylint happy.
        tag = 'at_root_bodies_start_in_doc_mode'
        start_in_doc = hasattr(c.config, tag) and getattr(c.config, tag)
        # New in Leo 4.6: dashes are valid in directive names.
        for d in aList:
            if 'root-code' in d:
                return 'code'
            if 'root-doc' in d:
                return 'doc'
            if 'root' in d:
                return 'doc' if start_in_doc else 'code'
        return None
    #@+node:ekr.20190921130036.1: *3* c.expand_path_expression
    def expand_path_expression(self, s):
        """Expand all {{anExpression}} in c's context."""
        c = self
        if not s:
            return ''
        s = g.toUnicode(s)
        # find and replace repeated path expressions
        previ, aList = 0, []
        while previ < len(s):
            i = s.find('{{', previ)
            j = s.find('}}', previ)
            if -1 < i < j:
                # Add anything from previous index up to '{{'
                if previ < i:
                    aList.append(s[previ:i])
                # Get expression and find substitute
                exp = s[i + 2 : j].strip()
                if exp:
                    try:
                        s2 = c.replace_path_expression(exp)
                        aList.append(s2)
                    except Exception:
                        g.es(f"Exception evaluating {{{{{exp}}}}} in {s.strip()}")
                        g.es_exception(full=True, c=c)
                # Prepare to search again after the last '}}'
                previ = j + 2
            else:
                # Add trailing fragment (fragile in case of mismatched '{{'/'}}')
                aList.append(s[previ:])
                break
        val = ''.join(aList)
        if g.isWindows:
            val = val.replace('\\', '/')
        return val
    #@+node:ekr.20190921130036.2: *4* c.replace_path_expression
    replace_errors = []

    def replace_path_expression(self, expr):
        """ local function to replace a single path expression."""
        c = self
        d = {
            'c': c,
            'g': g,
            # 'getString': c.config.getString,
            'p': c.p,
            'os': os,
            'sep': os.sep,
            'sys': sys,
        }
        # #1338: Don't report errors when called by g.getUrlFromNode.
        try:
            # pylint: disable=eval-used
            path = eval(expr, d)
            return g.toUnicode(path, encoding='utf-8')
        except Exception as e:
            message = (
                f"{c.shortFileName()}: {c.p.h}\n"
                f"expression: {expr!s}\n"
                f"     error: {e!s}")
            if message not in self.replace_errors:
                self.replace_errors.append(message)
                g.trace(message)
            return expr
    #@+node:ekr.20171123201514.1: *3* c.Executing commands & scripts
    #@+node:ekr.20110605040658.17005: *4* c.check_event
    def check_event(self, event):
        """Check an event object."""
        # c = self
        import leo.core.leoGui as leoGui

        if not event:
            return
        stroke = event.stroke
        got = event.char
        if g.unitTesting:
            return
        if stroke and (stroke.find('Alt+') > -1 or stroke.find('Ctrl+') > -1):
            expected = event.char
                # Alas, Alt and Ctrl bindings must *retain* the char field,
                # so there is no way to know what char field to expect.
        else:
            expected = event.char
                # disable the test.
                # We will use the (weird) key value for, say, Ctrl-s,
                # if there is no binding for Ctrl-s.
        if not isinstance(event, leoGui.LeoKeyEvent):
            if g.app.gui.guiName() not in ('console', 'curses'):
                g.trace(f"not leo event: {event!r}, callers: {g.callers()}")
        if expected != got:
            g.trace(f"stroke: {stroke!r}, expected char: {expected!r}, got: {got!r}")
    #@+node:ekr.20031218072017.2817: *4* c.doCommand
    command_count = 0

    def doCommand(self, command_func, command_name, event):
        """
        Execute the given command function, invoking hooks and catching exceptions.

        The code assumes that the "command1" hook has completely handled the
        command func if g.doHook("command1") returns False. This provides a
        simple mechanism for overriding commands.
        """
        c, p = self, self.p
        c.setLog()
        self.command_count += 1
        # New in Leo 6.2. Set command_function and command_name ivars.
        self.command_function = command_func
        self.command_name = command_name
        # The presence of this message disables all commands.
        if c.disableCommandsMessage:
            g.blue(c.disableCommandsMessage)
            return None
        if c.exists and c.inCommand and not g.unitTesting:
            g.app.commandInterruptFlag = True
            g.error('ignoring command: already executing a command.')
            return None
        g.app.commandInterruptFlag = False
        if not g.doHook("command1", c=c, p=p, label=command_name):
            try:
                c.inCommand = True
                try:
                    return_value = command_func(event)
                except Exception:
                    g.es_exception()
                    return_value = None
                if c and c.exists:  # Be careful: the command could destroy c.
                    c.inCommand = False
                    ## c.k.funcReturn = return_value
            except Exception:
                c.inCommand = False
                if g.app.unitTesting:
                    raise
                g.es_print("exception executing command")
                g.es_exception(c=c)
            if c and c.exists:
                if c.requestCloseWindow:
                    c.requestCloseWindow = False
                    g.app.closeLeoWindow(c.frame)
                else:
                    c.outerUpdate()
        # Be careful: the command could destroy c.
        if c and c.exists:
            p = c.p
            g.doHook("command2", c=c, p=p, label=command_name)
        return return_value
    #@+node:ekr.20200522075411.1: *4* c.doCommandByName
    def doCommandByName(self, command_name, event):
        """
        Execute one command, given the name of the command.
        
        The caller must do any required keystroke-only tasks.
        
        Return the result, if any, of the command.
        """
        c = self
        # Get the command's function.
        command_func = c.commandsDict.get(command_name.replace('&', ''))
        if not command_func:
            message = f"no command function for {command_name!r}"
            if g.app.unitTesting or g.app.inBridge:
                raise AttributeError(message)
            g.es_print(message, color='red')
            g.trace(g.callers())
            return None
        # Invoke the function.
        val = c.doCommand(command_func, command_name, event)
        if c.exists:
            c.frame.updateStatusLine()
        return val
    #@+node:ekr.20200526074132.1: *4* c.executeMinibufferCommand
    def executeMinibufferCommand(self, commandName):
        """Call c.doCommandByName, creating the required event."""
        c = self
        event = g.app.gui.create_key_event(c)
        return c.doCommandByName(commandName, event)
    #@+node:ekr.20200523135601.1: *4* c.insertCharFromEvent
    def insertCharFromEvent(self, event):
        """
        Handle the character given by event *without*
        executing any command that might be bound to it.
        
        What happens depends on which widget has focus.
        """
        c, k, w = self, self.k, event.widget
        name = c.widget_name(w)
        stroke = event.stroke
        if not stroke:
            return
        #
        # Part 1: Very late special cases.
        #
        # #1448
        if stroke.isNumPadKey() and k.state.kind == 'getArg':
            stroke.removeNumPadModifier()
            k.getArg(event, stroke=stroke)
            return
        # Handle all unbound characters in command mode.
        if k.unboundKeyAction == 'command':
            w = g.app.gui.get_focus(c)
            if w and g.app.gui.widget_name(w).lower().startswith('canvas'):
                c.onCanvasKey(event)
            return
        #
        # Part 2: Filter out keys that should never be inserted by default.
        #
        # Ignore unbound F-keys.
        if stroke.isFKey():
            return
        # Ignore unbound Alt/Ctrl keys.
        if stroke.isAltCtrl():
            if not k.enable_alt_ctrl_bindings:
                return
            if k.ignore_unbound_non_ascii_keys:
                return
        # #868
        if stroke.isPlainNumPad():
            stroke.removeNumPadModifier()
            event.stroke = stroke
        # #868
        if stroke.isNumPadKey():
            return
        # Ignore unbound non-ascii character.
        if k.ignore_unbound_non_ascii_keys and not stroke.isPlainKey():
            return
        # Never insert escape or insert characters.
        if 'Escape' in stroke.s or 'Insert' in stroke.s:
            return
        #
        # Part 3: Handle the event depending on the pane and state.
        #
        # Handle events in the body pane.
        if name.startswith('body'):
            action = k.unboundKeyAction
            if action in ('insert', 'overwrite'):
                c.editCommands.selfInsertCommand(event, action=action)
                c.frame.updateStatusLine()
            return
        #
        # Handle events in headlines.
        if name.startswith('head'):
            c.frame.tree.onHeadlineKey(event)
            return
        #
        # Handle events in the background tree (not headlines).
        if name.startswith('canvas'):
            if event.char:
                k.searchTree(event.char)
            # Not exactly right, but it seems to be good enough.
            elif not stroke:
                c.onCanvasKey(event)
            return
        #
        # Ignore all events outside the log pane.
        if not name.startswith('log'):
            return
        #
        # Make sure we can insert into w.
        log_w = event.widget
        if not hasattr(log_w, 'supportsHighLevelInterface'):
            return
        #
        # Send the event to the text widget, not the LeoLog instance.
        i = log_w.getInsertPoint()
        s = stroke.toGuiChar()
        log_w.insert(i, s)
    #@+node:ekr.20131016084446.16724: *4* c.setComplexCommand
    def setComplexCommand(self, commandName):
        """Make commandName the command to be executed by repeat-complex-command."""
        c = self
        c.k.mb_history.insert(0, commandName)
    #@+node:bobjack.20080509080123.2: *4* c.universalCallback & minibufferCallback
    def universalCallback(self, source_c, function):
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
            if hasattr(self, 'theContextMenuController'):
                cm = getattr(self, 'theContextMenuController')
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

        minibufferCallback.__doc__ = function.__doc__
            # For g.getDocStringForFunction
        minibufferCallback.source_c = source_c
            # For GetArgs.command_source
        return minibufferCallback

    #fix bobjack's spelling error

    universallCallback = universalCallback
    #@+node:ekr.20070115135502: *4* c.writeScriptFile (changed: does not expand expressions)
    def writeScriptFile(self, script):

        # Get the path to the file.
        c = self
        path = c.config.getString('script-file-path')
        if path:
            isAbsPath = os.path.isabs(path)
            driveSpec, path = os.path.splitdrive(path)
            parts = path.split('/')
            # xxx bad idea, loadDir is often read only!
            path = g.app.loadDir
            if isAbsPath:
                # make the first element absolute
                parts[0] = driveSpec + os.sep + parts[0]
            allParts = [path] + parts
            path = g.os_path_finalize_join(*allParts)  # #1431
        else:
            path = g.os_path_finalize_join(g.app.homeLeoDir, 'scriptFile.py')  # #1431
        #
        # Write the file.
        try:
            with open(path, encoding='utf-8', mode='w') as f:
                f.write(script)
        except Exception:
            g.es_exception()
            g.es(f"Failed to write script to {path}")
            # g.es("Check your configuration of script_file_path, currently %s" %
                # c.config.getString('script-file-path'))
            path = None
        return path
    #@+node:ekr.20171124101444.1: *3* c.File
    #@+node:ekr.20200305104646.1: *4* c.archivedPositionToPosition (new)
    def archivedPositionToPosition(self, s):
        """Convert an archived position (a string) to a position."""
        c = self
        s = g.toUnicode(s)
        aList = s.split(',')
        try:
            aList = [int(z) for z in aList]
        except Exception:
            aList = None
        if not aList:
            return None
        p = c.rootPosition()
        level = 0
        while level < len(aList):
            i = aList[level]
            while i > 0:
                if p.hasNext():
                    p.moveToNext()
                    i -= 1
                else:
                    return None
            level += 1
            if level < len(aList):
                p.moveToFirstChild()
        return p
    #@+node:ekr.20150422080541.1: *4* c.backup
    def backup(self, fileName=None, prefix=None, silent=False, useTimeStamp=True):
        """
        Back up given fileName or c.fileName().
        If useTimeStamp is True, append a timestamp to the filename.
        """
        c = self
        fn = fileName or c.fileName()
        if not fn:
            return None
        theDir, base = g.os_path_split(fn)
        if useTimeStamp:
            if base.endswith('.leo'):
                base = base[:-4]
            stamp = time.strftime("%Y%m%d-%H%M%S")
            branch = prefix + '-' if prefix else ''
            fn = f"{branch}{base}-{stamp}.leo"
            path = g.os_path_finalize_join(theDir, fn)
        else:
            path = fn
        if path:
            # pylint: disable=no-member
                # Defined in commanderFileCommands.py.
            c.saveTo(fileName=path, silent=silent)
                # Issues saved message.
            # g.es('in', theDir)
        return path
    #@+node:ekr.20180210092235.1: *4* c.backup_helper
    def backup_helper(self,
        base_dir=None,
        env_key='LEO_BACKUP',
        sub_dir=None,
        use_git_prefix=True,
    ):
        """
        A helper for scripts that back up a .leo file.
        Use os.environ[env_key] as the base_dir only if base_dir is not given.
        Backup to base_dir or join(base_dir, sub_dir).
        """
        c = self
        old_cwd = os.getcwd()
        join = g.os_path_finalize_join
        if not base_dir:
            if env_key:
                try:
                    base_dir = os.environ[env_key]
                except KeyError:
                    print(f"No environment var: {env_key}")
                    base_dir = None
        if base_dir and g.os_path_exists(base_dir):
            if use_git_prefix:
                git_branch, junk = g.gitInfo()
            else:
                git_branch = None
            theDir, fn = g.os_path_split(c.fileName())
            backup_dir = join(base_dir, sub_dir) if sub_dir else base_dir
            path = join(backup_dir, fn)
            if g.os_path_exists(backup_dir):
                written_fn = c.backup(
                    path,
                    prefix=git_branch,
                    silent=True,
                    useTimeStamp=True,
                )
                g.es_print(f"wrote: {written_fn}")
            else:
                g.es_print(f"backup_dir not found: {backup_dir!r}")
        else:
            g.es_print(f"base_dir not found: {base_dir!r}")
        os.chdir(old_cwd)
    #@+node:ekr.20090103070824.11: *4* c.checkFileTimeStamp
    def checkFileTimeStamp(self, fn):
        """
        Return True if the file given by fn has not been changed
        since Leo read it or if the user agrees to overwrite it.
        """
        c = self
        if g.app.externalFilesController:
            return g.app.externalFilesController.check_overwrite(c, fn)
        return True
    #@+node:ekr.20090212054250.9: *4* c.createNodeFromExternalFile
    def createNodeFromExternalFile(self, fn):
        """
        Read the file into a node.
        Return None, indicating that c.open should set focus.
        """
        c = self
        s, e = g.readFileIntoString(fn)
        if s is None: return
        head, ext = g.os_path_splitext(fn)
        if ext.startswith('.'): ext = ext[1:]
        language = g.app.extension_dict.get(ext)
        if language:
            prefix = f"@color\n@language {language}\n\n"
        else:
            prefix = '@killcolor\n\n'
        # pylint: disable=no-member
        # Defined in commanderOutlineCommands.py
        p2 = c.insertHeadline(op_name='Open File', as_child=False)
        p2.h = f"@edit {fn}"
        p2.b = prefix + s
        w = c.frame.body.wrapper
        if w: w.setInsertPoint(0)
        c.redraw()
        c.recolor()
    #@+node:ekr.20110530124245.18248: *4* c.looksLikeDerivedFile
    def looksLikeDerivedFile(self, fn):
        """
        Return True if fn names a file that looks like an
        external file written by Leo.
        """
        # c = self
        try:
            with open(fn, 'r') as f:
                s = f.read()
            return s.find('@+leo-ver=') > -1
        except Exception:
            return False
    #@+node:ekr.20031218072017.2925: *4* c.markAllAtFileNodesDirty
    def markAllAtFileNodesDirty(self, event=None):
        """Mark all @file nodes as changed."""
        c = self
        c.endEditing()
        p = c.rootPosition()
        while p:
            if p.isAtFileNode():
                p.setDirty()
                c.setChanged()
                p.moveToNodeAfterTree()
            else:
                p.moveToThreadNext()
        c.redraw_after_icons_changed()
    #@+node:ekr.20031218072017.2926: *4* c.markAtFileNodesDirty
    def markAtFileNodesDirty(self, event=None):
        """Mark all @file nodes in the selected tree as changed."""
        c = self
        p = c.p
        if not p:
            return
        c.endEditing()
        after = p.nodeAfterTree()
        while p and p != after:
            if p.isAtFileNode():
                p.setDirty()
                c.setChanged()
                p.moveToNodeAfterTree()
            else:
                p.moveToThreadNext()
        c.redraw_after_icons_changed()
    #@+node:ekr.20031218072017.2823: *4* c.openWith
    def openWith(self, event=None, d=None):
        """
        This is *not* a command.

        Handles the items in the Open With... menu.

        See ExternalFilesController.open_with for details about d.
        """
        c = self
        if d and g.app.externalFilesController:
            # Select an ancestor @<file> node if possible.
            if not d.get('p'):
                d['p'] = None
                p = c.p
                while p:
                    if p.isAnyAtFileNode():
                        d['p'] = p
                        break
                    p.moveToParent()
            g.app.externalFilesController.open_with(c, d)
        elif not d:
            g.trace('can not happen: no d', g.callers())
    #@+node:ekr.20140717074441.17770: *4* c.recreateGnxDict
    def recreateGnxDict(self):
        """Recreate the gnx dict prior to refreshing nodes from disk."""
        c, d = self, {}
        for v in c.all_unique_nodes():
            gnxString = v.fileIndex
            if isinstance(gnxString, str):
                d[gnxString] = v
                if 'gnx' in g.app.debug:
                    g.trace(c.shortFileName(), gnxString, v)
            else:
                g.internalError(f"no gnx for vnode: {v}")
        c.fileCommands.gnxDict = d
    #@+node:ekr.20180508111544.1: *3* c.Git
    #@+node:ekr.20180510104805.1: *4* c.diff_file
    def diff_file(self, fn, rev1='HEAD', rev2='', directory=None):
        """
        Create an outline describing the git diffs for all files changed
        between rev1 and rev2.
        """
        import leo.commands.editFileCommands as efc
        efc.GitDiffController(c=self).diff_file(
            directory=directory,
            fn=fn,
            rev1=rev1,
            rev2=rev2,
        )
    #@+node:ekr.20180508110755.1: *4* c.diff_two_revs
    def diff_two_revs(self, directory=None, rev1='', rev2=''):
        """
        Create an outline describing the git diffs for all files changed
        between rev1 and rev2.
        """
        import leo.commands.editFileCommands as efc
        efc.GitDiffController(c=self).diff_two_revs(
            directory=directory,
            rev1=rev1,
            rev2=rev2,
        )
    #@+node:ekr.20180510103923.1: *4* c.diff_two_branches
    def diff_two_branches(self, branch1, branch2, fn, directory=None):
        """
        Create an outline describing the git diffs for all files changed
        between rev1 and rev2.
        """
        import leo.commands.editFileCommands as efc
        efc.GitDiffController(c=self).diff_two_branches(
            branch1=branch1,
            branch2=branch2,
            directory=directory,
            fn=fn,
        )
    #@+node:ekr.20180510105125.1: *4* c.git_diff
    def git_diff(self, rev1='HEAD', rev2='', directory=None):

        import leo.commands.editFileCommands as efc
        efc.GitDiffController(c=self).git_diff(
            directory=directory,
            rev1=rev1,
            rev2=rev2,
        )
    #@+node:ekr.20171124100534.1: *3* c.Gui
    #@+node:ekr.20111217154130.10286: *4* c.Dialogs & messages
    #@+node:ekr.20110510052422.14618: *5* c.alert
    def alert(self, message):
        c = self
        # The unit tests just tests the args.
        if not g.unitTesting:
            g.es(message)
            g.app.gui.alert(c, message)
    #@+node:ekr.20111217154130.10284: *5* c.init_error_dialogs
    def init_error_dialogs(self):
        c = self
        c.import_error_nodes = []
        c.ignored_at_file_nodes = []
        c.orphan_at_file_nodes = []
        if g.unitTesting:
            d = g.app.unitTestDict
            tag = 'init_error_dialogs'
            d[tag] = 1 + d.get(tag, 0)
    #@+node:ekr.20171123135805.1: *5* c.notValidInBatchMode
    def notValidInBatchMode(self, commandName):
        g.es('the', commandName, "command is not valid in batch mode")
    #@+node:ekr.20110530082209.18250: *5* c.putHelpFor
    def putHelpFor(self, s, short_title=''):
        """Helper for various help commands."""
        c = self
        g.app.gui.put_help(c, s, short_title)
    #@+node:ekr.20111217154130.10285: *5* c.raise_error_dialogs
    def raise_error_dialogs(self, kind='read'):
        """Warn abouit read/write failures."""
        c = self
        use_dialogs = True
        if g.unitTesting:
            d = g.app.unitTestDict
            tag = 'raise_error_dialogs'
            d[tag] = 1 + d.get(tag, 0)
            # This trace catches all too-many-calls failures.
                # g.trace(g.callers())
            c.init_error_dialogs()
            return
        #
        # Issue one or two dialogs or messages.
        saved_body = c.rootPosition().b
            # Save the root's body. Somehow the dialog destroys it!
        if c.import_error_nodes or c.ignored_at_file_nodes or c.orphan_at_file_nodes:
            g.app.gui.dismiss_splash_screen()
        else:
            # #1007: Exit now, so we don't have to restore c.rootPosition().b.
            c.init_error_dialogs()
            return
        if c.import_error_nodes:
            files = '\n'.join(sorted(set(c.import_error_nodes)))
            if use_dialogs:
                message = (
                    'The following were not imported properly. '
                    f"Inserted @ignore in...\n{files}")
                g.app.gui.runAskOkDialog(c, message=message, title='Import errors')
            else:
                g.es('import errors...', color='red')
                g.es('\n'.join(sorted(files)), color='blue')
        if c.ignored_at_file_nodes:
            files = '\n'.join(sorted(set(c.ignored_at_file_nodes)))
            kind = 'read' if kind.startswith('read') else 'written'
            if use_dialogs:
                message = (
                    f"The following were not {kind} "
                    f"because they contain @ignore:\n{files}")
                g.app.gui.runAskOkDialog(c,
                    message=message,
                    title=f"Not {kind.capitalize()}")
            else:
                g.es(f"not {kind} (@ignore)...", color='red')
                g.es(files, color='blue')
        #
        # #1050: always raise a dialog for orphan @<file> nodes.
        if c.orphan_at_file_nodes:
            message = '\n'.join([
                'The following were not written because of errors:\n',
                '\n'.join(sorted(set(c.orphan_at_file_nodes))),
                '',
                'Warning: changes to these files will be lost\n'
                'unless you can save the files successfully.'
            ])
            g.app.gui.runAskOkDialog(c, message=message, title='Not Written')
            # Mark all the nodes dirty.
            for z in c.all_unique_positions():
                if z.isOrphan():
                    z.setDirty()
                    z.clearOrphan()
            c.setChanged()
            c.redraw()
        # Restore the root position's body.
        c.rootPosition().v.b = saved_body
            # #1007: just set v.b.
        c.init_error_dialogs()
    #@+node:ekr.20150710083827.1: *5* c.syntaxErrorDialog
    def syntaxErrorDialog(self):
        """Warn about syntax errors in files."""
        c = self
        if g.app.syntax_error_files and c.config.getBool(
            'syntax-error-popup', default=False):
            aList = sorted(set(g.app.syntax_error_files))
            g.app.syntax_error_files = []
            list_s = '\n'.join(aList)
            g.app.gui.runAskOkDialog(
                c,
                title='Python Errors',
                message=f"Python errors in:\n\n{list_s}",
                text="Ok",
            )
    #@+node:ekr.20031218072017.2945: *4* c.Dragging
    #@+node:ekr.20031218072017.2947: *5* c.dragToNthChildOf
    def dragToNthChildOf(self, p, parent, n):
        c = self; u = c.undoer; undoType = 'Drag'
        current = c.p
        if not c.checkDrag(p, parent):
            return
        if not c.checkMoveWithParentWithWarning(p, parent, True):
            return
        c.endEditing()
        undoData = u.beforeMoveNode(current)
        p.setDirty()
        p.moveToNthChildOf(parent, n)
        p.setDirty()
        c.setChanged()
        u.afterMoveNode(p, undoType, undoData)
        c.redraw(p)
        c.updateSyntaxColorer(p)  # Dragging can change syntax coloring.
    #@+node:ekr.20031218072017.2353: *5* c.dragAfter
    def dragAfter(self, p, after):
        c = self; u = self.undoer; undoType = 'Drag'
        current = c.p
        if not c.checkDrag(p, after):
            return
        if not c.checkMoveWithParentWithWarning(p, after.parent(), True):
            return
        c.endEditing()
        undoData = u.beforeMoveNode(current)
        p.setDirty()
        p.moveAfter(after)
        p.setDirty()
        c.setChanged()
        u.afterMoveNode(p, undoType, undoData)
        c.redraw(p)
        c.updateSyntaxColorer(p)  # Dragging can change syntax coloring.
    #@+node:ekr.20031218072017.2946: *5* c.dragCloneToNthChildOf
    def dragCloneToNthChildOf(self, p, parent, n):
        c = self; u = c.undoer; undoType = 'Clone Drag'
        current = c.p
        clone = p.clone()  # Creates clone & dependents, does not set undo.
        if (
            not c.checkDrag(p, parent) or
            not c.checkMoveWithParentWithWarning(clone, parent, True)
        ):
            clone.doDelete(newNode=p)  # Destroys clone and makes p the current node.
            c.selectPosition(p)  # Also sets root position.
            return
        c.endEditing()
        undoData = u.beforeInsertNode(current)
        clone.setDirty()
        clone.moveToNthChildOf(parent, n)
        clone.setDirty()
        c.setChanged()
        u.afterInsertNode(clone, undoType, undoData)
        c.redraw(clone)
        c.updateSyntaxColorer(clone)  # Dragging can change syntax coloring.
    #@+node:ekr.20031218072017.2948: *5* c.dragCloneAfter
    def dragCloneAfter(self, p, after):
        c = self; u = c.undoer; undoType = 'Clone Drag'
        current = c.p
        clone = p.clone()  # Creates clone.  Does not set undo.
        if c.checkDrag(
            p, after) and c.checkMoveWithParentWithWarning(clone, after.parent(), True):
            c.endEditing()
            undoData = u.beforeInsertNode(current)
            clone.setDirty()
            clone.moveAfter(after)
            clone.v.setDirty()
            c.setChanged()
            u.afterInsertNode(clone, undoType, undoData)
            p = clone
        else:
            clone.doDelete(newNode=p)
        c.redraw(p)
        c.updateSyntaxColorer(clone)  # Dragging can change syntax coloring.
    #@+node:ekr.20031218072017.2949: *4* c.Drawing
    #@+node:ekr.20080514131122.7: *5* c.begin/endUpdate
    def beginUpdate(self):
        """Deprecated: does nothing."""
        g.trace('***** c.beginUpdate is deprecated', g.callers())
        if g.app.unitTesting: assert(False)

    def endUpdate(self, flag=True):
        """Request a redraw of the screen if flag is True."""
        g.trace('***** c.endUpdate is deprecated', g.callers())
        if g.app.unitTesting: assert(False)
        c = self
        if flag:
            c.requestRedrawFlag = True

    BeginUpdate = beginUpdate  # Compatibility with old scripts
    EndUpdate = endUpdate  # Compatibility with old scripts
    #@+node:ekr.20080514131122.8: *5* c.bringToFront
    def bringToFront(self, c2=None, set_focus=True):
        c = self
        c2 = c2 or c
        g.app.gui.ensure_commander_visible(c2)

    BringToFront = bringToFront  # Compatibility with old scripts
    #@+node:ekr.20040803072955.143: *5* c.expandAllAncestors
    def expandAllAncestors(self, p):
        """
        Expand all ancestors without redrawing.
        Return a flag telling whether a redraw is needed.
        """
        # c = self
        redraw_flag = False
        for p in p.parents():
            if not p.v.isExpanded():
                p.v.expand()
                p.expand()
                redraw_flag = True
            elif p.isExpanded():
                p.v.expand()
            else:
                p.expand()
                redraw_flag = True
        return redraw_flag
    #@+node:ekr.20080514131122.20: *5* c.outerUpdate
    def outerUpdate(self):
        """Handle delayed focus requests and modified events."""
        c = self
        if not c.exists or not c.k:
            return
        # New in Leo 5.6: Delayed redraws are useful in utility methods.
        if c.requestLaterRedraw:
            if c.enableRedrawFlag:
                c.requestLaterRedraw = False
                if 'drawing' in g.app.debug and not g.unitTesting:
                    g.trace('\nDELAYED REDRAW')
                    time.sleep(1.0)
                c.redraw()
        # Delayed focus requests will always be useful.
        if c.requestedFocusWidget:
            w = c.requestedFocusWidget
            if 'focus' in g.app.debug and not g.unitTesting:
                if hasattr(w, 'objectName'):
                    name = w.objectName()
                else:
                    name = w.__class__.__name__
                g.trace('DELAYED FOCUS', name)
            c.set_focus(w)
            c.requestedFocusWidget = None
        table = (
            ("childrenModified", g.childrenModifiedSet),
            ("contentModified", g.contentModifiedSet),
        )
        for kind, mods in table:
            if mods:
                g.doHook(kind, c=c, nodes=mods)
                mods.clear()
    #@+node:ekr.20080514131122.13: *5* c.recolor
    def recolor(self, **kwargs):
        # Support QScintillaColorizer.colorize.
        c = self
        p = kwargs.get('p')
        for name in ('incremental', 'interruptable'):
            if name in kwargs:
                print(f'c.recolor_now: "{name}" keyword arg is deprecated')
        colorizer = c.frame.body.colorizer
        if colorizer and hasattr(colorizer, 'colorize'):
            colorizer.colorize(p or c.p)

    recolor_now = recolor
    #@+node:ekr.20080514131122.14: *5* c.redrawing...
    #@+node:ekr.20170808014610.1: *6* c.enable/disable_redraw
    def disable_redraw(self):
        """Disable all redrawing until enabled."""
        c = self
        c.enableRedrawFlag = False

    def enable_redraw(self):
        c = self
        c.enableRedrawFlag = True
    #@+node:ekr.20090110073010.1: *6* c.redraw
    @cmd('redraw')
    def redraw_command(self, event):
        c = event.get('c')
        if c:
            c.redraw()

    def redraw(self, p=None):
        """Redraw the screen immediately."""
        c = self
        # New in Leo 5.6: clear the redraw request.
        c.requestLaterRedraw = False
        if not p:
            p = c.p or c.rootPosition()
        if not p:
            return
        c.expandAllAncestors(p)
        if p:
            # Fix bug https://bugs.launchpad.net/leo-editor/+bug/1183855
            # This looks redundant, but it is probably the only safe fix.
            c.frame.tree.select(p)
        # tree.redraw will change the position if p is a hoisted @chapter node.
        p2 = c.frame.tree.redraw(p)
        # Be careful.  NullTree.redraw returns None.
        # #503: NullTree.redraw(p) now returns p.
        c.selectPosition(p2 or p)
        # Do not call treeFocusHelper here.
            # c.treeFocusHelper()
        # Clear the redraw request, again.
        c.requestLaterRedraw = False

    # Compatibility with old scripts

    force_redraw = redraw
    redraw_now = redraw
    #@+node:ekr.20090110073010.3: *6* c.redraw_afer_icons_changed
    def redraw_after_icons_changed(self):
        """Update the icon for the presently selected node"""
        c = self
        if c.enableRedrawFlag:
            c.frame.tree.redraw_after_icons_changed()
            # Do not call treeFocusHelper here.
                # c.treeFocusHelper()
        else:
            c.requestLaterRedraw = True
    #@+node:ekr.20090110131802.2: *6* c.redraw_after_contract
    def redraw_after_contract(self, p=None):
        c = self
        if c.enableRedrawFlag:
            if p:
                c.setCurrentPosition(p)
            else:
                p = c.currentPosition()
            c.frame.tree.redraw_after_contract(p)
            c.treeFocusHelper()
        else:
            c.requestLaterRedraw = True
    #@+node:ekr.20090112065525.1: *6* c.redraw_after_expand
    def redraw_after_expand(self, p):
        c = self
        if c.enableRedrawFlag:
            if p:
                c.setCurrentPosition(p)
            else:
                p = c.currentPosition()
            c.frame.tree.redraw_after_expand(p)
            c.treeFocusHelper()
        else:
            c.requestLaterRedraw = True
    #@+node:ekr.20090110073010.2: *6* c.redraw_after_head_changed
    def redraw_after_head_changed(self):
        """
        Redraw the screen (if needed) when editing ends.
        This may be a do-nothing for some gui's.
        """
        c = self
        if c.enableRedrawFlag:
            self.frame.tree.redraw_after_head_changed()
        else:
            c.requestLaterRedraw = True
    #@+node:ekr.20090110073010.4: *6* c.redraw_after_select
    def redraw_after_select(self, p):
        """Redraw the screen after node p has been selected."""
        c = self
        if c.enableRedrawFlag:
            flag = c.expandAllAncestors(p)
            if flag:
                c.frame.tree.redraw_after_select(p)
                    # This is the same as c.frame.tree.full_redraw().
        else:
            c.requestLaterRedraw = True
    #@+node:ekr.20170908081918.1: *6* c.redraw_later
    def redraw_later(self):
        """
        Ensure that c.redraw() will be called eventually.
        
        c.outerUpdate will call c.redraw() only if no other code calls c.redraw().
        """
        c = self
        c.requestLaterRedraw = True
        if 'drawing' in g.app.debug:
            # g.trace('\n' + g.callers(8))
            g.trace(g.callers())
    #@+node:ekr.20080514131122.17: *5* c.widget_name
    def widget_name(self, widget):
        # c = self
        return g.app.gui.widget_name(widget) if g.app.gui else '<no widget>'
    #@+node:ekr.20171124101045.1: *4* c.Events
    #@+node:ekr.20060923202156: *5* c.onCanvasKey
    def onCanvasKey(self, event):
        """
        Navigate to the next headline starting with ch = event.char.
        If ch is uppercase, search all headlines; otherwise search only visible headlines.
        This is modelled on Windows explorer.
        """
        if not event or not event.char or not event.char.isalnum():
            return
        c = self; p = c.p; p1 = p.copy()
        invisible = c.config.getBool('invisible-outline-navigation')
        ch = event.char if event else ''
        allFlag = ch.isupper() and invisible  # all is a global (!?)
        if not invisible: ch = ch.lower()
        found = False
        extend = self.navQuickKey()
        attempts = (True, False) if extend else (False,)
        for extend2 in attempts:
            p = p1.copy()
            while 1:
                if allFlag:
                    p.moveToThreadNext()
                else:
                    p.moveToVisNext(c)
                if not p:
                    p = c.rootPosition()
                if p == p1:  # Never try to match the same position.
                    found = False; break
                newPrefix = c.navHelper(p, ch, extend2)
                if newPrefix:
                    found = True; break
            if found: break
        if found:
            c.selectPosition(p)
            c.redraw_after_select(p)
            c.navTime = time.time()
            c.navPrefix = newPrefix
        else:
            c.navTime = None
            c.navPrefix = ''
        c.treeWantsFocus()
    #@+node:ekr.20061002095711.1: *6* c.navQuickKey
    def navQuickKey(self):
        """
        Return true if there are two quick outline navigation keys
        in quick succession.

        Returns False if @float outline_nav_extend_delay setting is 0.0 or unspecified.
        """
        c = self
        deltaTime = c.config.getFloat('outline-nav-extend-delay')
        if deltaTime in (None, 0.0):
            return False
        nearTime = c.navTime and time.time() - c.navTime < deltaTime
        return nearTime
    #@+node:ekr.20061002095711: *6* c.navHelper
    def navHelper(self, p, ch, extend):
        c = self; h = p.h.lower()
        if extend:
            prefix = c.navPrefix + ch
            return h.startswith(prefix.lower()) and prefix
        if h.startswith(ch):
            return ch
        # New feature: search for first non-blank character after @x for common x.
        if ch != '@' and h.startswith('@'):
            for s in ('button', 'command', 'file', 'thin', 'asis', 'nosent',):
                prefix = '@' + s
                if h.startswith('@' + s):
                    while 1:
                        n = len(prefix)
                        ch2 = h[n] if n < len(h) else ''
                        if ch2.isspace():
                            prefix = prefix + ch2
                        else: break
                    if len(prefix) < len(h) and h.startswith(prefix + ch.lower()):
                        return prefix + ch
        return ''
    #@+node:ekr.20031218072017.2909: *4* c.Expand/contract
    #@+node:ekr.20171124091426.1: *5* c.contractAllHeadlines
    def contractAllHeadlines(self, event=None, redrawFlag=True):
        """Contract all nodes in the outline."""
        c = self
        for p in c.all_positions():
            p.contract()
        # Select the topmost ancestor of the presently selected node.
        p = c.p
        while p and p.hasParent():
            p.moveToParent()
        if redrawFlag:
            # Do a *full* redraw.
            # c.redraw_after_contract(p) only contracts a single position.
            c.redraw(p)
        c.expansionLevel = 1  # Reset expansion level.
    #@+node:ekr.20031218072017.2910: *5* c.contractSubtree
    def contractSubtree(self, p):
        for p in p.subtree():
            p.contract()
    #@+node:ekr.20031218072017.2911: *5* c.expandSubtree
    def expandSubtree(self, v, redraw=True):
        c = self
        last = v.lastNode()
        while v and v != last:
            v.expand()
            v = v.threadNext()
        if redraw:
            c.redraw()
    #@+node:ekr.20031218072017.2912: *5* c.expandToLevel
    def expandToLevel(self, level):

        c = self
        n = c.p.level()
        old_expansion_level = c.expansionLevel
        max_level = 0
        for p in c.p.self_and_subtree(copy=False):
            if p.level() - n + 1 < level:
                p.expand()
                max_level = max(max_level, p.level() - n + 1)
            else:
                p.contract()
        c.expansionNode = c.p.copy()
        c.expansionLevel = max_level + 1
        if c.expansionLevel != old_expansion_level:
            c.redraw()
        # It's always useful to announce the level.
        # c.k.setLabelBlue('level: %s' % (max_level+1))
        # g.es('level', max_level + 1)
        c.frame.putStatusLine(f"level: {max_level + 1}")
            # bg='red', fg='red')
    #@+node:ekr.20141028061518.23: *4* c.Focus
    #@+node:ekr.20080514131122.9: *5* c.get/request/set_focus
    def get_focus(self):
        c = self
        w = g.app.gui and g.app.gui.get_focus(c)
        if 'focus' in g.app.debug:
            name = w.objectName() if hasattr(w, 'objectName') else w.__class__.__name__
            g.trace('(c)', name)
            # g.trace('\n(c)',  w.__class__.__name__)
            # g.trace(g.callers(6))
        return w

    def get_requested_focus(self):
        c = self
        return c.requestedFocusWidget

    def request_focus(self, w):
        c = self
        if w and g.app.gui:
            if 'focus' in g.app.debug:
                # g.trace('\n(c)', repr(w))
                name = w.objectName(
                    ) if hasattr(w, 'objectName') else w.__class__.__name__
                g.trace('(c)', name)
            c.requestedFocusWidget = w

    def set_focus(self, w, force=False):
        trace = 'focus' in g.app.debug
        c = self
        if w and g.app.gui:
            if trace:
                name = w.objectName(
                    ) if hasattr(w, 'objectName') else w.__class__.__name__
                g.trace('(c)', name)
            g.app.gui.set_focus(c, w)
        else:
            if trace: g.trace('(c) no w')
        c.requestedFocusWidget = None
    #@+node:ekr.20080514131122.10: *5* c.invalidateFocus (do nothing)
    def invalidateFocus(self):
        """Indicate that the focus is in an invalid location, or is unknown."""
        # c = self
        # c.requestedFocusWidget = None
        pass
    #@+node:ekr.20080514131122.16: *5* c.traceFocus (not used)
    def traceFocus(self, w):
        c = self
        if 'focus' in g.app.debug:
            c.trace_focus_count += 1
            g.pr(f"{c.trace_focus_count:4d}", c.widget_name(w), g.callers(8))
    #@+node:ekr.20070226121510: *5* c.xFocusHelper & initialFocusHelper
    def treeFocusHelper(self):
        c = self
        if c.stayInTreeAfterSelect:
            c.treeWantsFocus()
        else:
            c.bodyWantsFocus()

    def initialFocusHelper(self):
        c = self
        if c.outlineHasInitialFocus:
            c.treeWantsFocus()
        else:
            c.bodyWantsFocus()
    #@+node:ekr.20080514131122.18: *5* c.xWantsFocus
    def bodyWantsFocus(self):
        c = self; body = c.frame.body
        c.request_focus(body and body.wrapper)

    def logWantsFocus(self):
        c = self; log = c.frame.log
        c.request_focus(log and log.logCtrl)

    def minibufferWantsFocus(self):
        c = self
        c.request_focus(c.miniBufferWidget)

    def treeWantsFocus(self):
        c = self; tree = c.frame.tree
        c.request_focus(tree and tree.canvas)

    def widgetWantsFocus(self, w):
        c = self; c.request_focus(w)
    #@+node:ekr.20080514131122.19: *5* c.xWantsFocusNow
    # widgetWantsFocusNow does an automatic update.

    def widgetWantsFocusNow(self, w):
        c = self
        if w:
            c.set_focus(w)
            c.requestedFocusWidget = None

    # New in 4.9: all FocusNow methods now *do* call c.outerUpdate().

    def bodyWantsFocusNow(self):
        c = self; body = c.frame.body
        c.widgetWantsFocusNow(body and body.wrapper)

    def logWantsFocusNow(self):
        c = self; log = c.frame.log
        c.widgetWantsFocusNow(log and log.logCtrl)

    def minibufferWantsFocusNow(self):
        c = self
        c.widgetWantsFocusNow(c.miniBufferWidget)

    def treeWantsFocusNow(self):
        c = self; tree = c.frame.tree
        c.widgetWantsFocusNow(tree and tree.canvas)
    #@+node:ekr.20031218072017.2955: *4* c.Menus
    #@+node:ekr.20080610085158.2: *5* c.add_command
    def add_command(self, menu, **keys):
        c = self
        command = keys.get('command')
        if command:
            # Command is always either:
            # one of two callbacks defined in createMenuEntries or
            # recentFilesCallback, defined in createRecentFilesMenuItems.

            def add_commandCallback(c=c, command=command):
                val = command()
                # Careful: func may destroy c.
                if c.exists: c.outerUpdate()
                return val

            keys['command'] = add_commandCallback
            menu.add_command(**keys)
        else:
            g.trace('can not happen: no "command" arg')
    #@+node:ekr.20171123203044.1: *5* c.Menu Enablers
    #@+node:ekr.20040131170659: *6* c.canClone
    def canClone(self):
        c = self
        if c.hoistStack:
            current = c.p
            bunch = c.hoistStack[-1]
            return current != bunch.p
        return True
    #@+node:ekr.20031218072017.2956: *6* c.canContractAllHeadlines
    def canContractAllHeadlines(self):
        """Contract all nodes in the tree."""
        c = self
        for p in c.all_positions():  # was c.all_unique_positions()
            if p.isExpanded():
                return True
        return False
    #@+node:ekr.20031218072017.2957: *6* c.canContractAllSubheads
    def canContractAllSubheads(self):
        c = self; current = c.p
        for p in current.subtree():
            if p != current and p.isExpanded():
                return True
        return False
    #@+node:ekr.20031218072017.2958: *6* c.canContractParent
    def canContractParent(self):
        c = self
        return c.p.parent()
    #@+node:ekr.20031218072017.2959: *6* c.canContractSubheads
    def canContractSubheads(self):
        c = self; current = c.p
        for child in current.children():
            if child.isExpanded():
                return True
        return False
    #@+node:ekr.20031218072017.2960: *6* c.canCutOutline & canDeleteHeadline
    def canDeleteHeadline(self):
        c = self; p = c.p
        if c.hoistStack:
            bunch = c.hoistStack[0]
            if p == bunch.p: return False
        return p.hasParent() or p.hasThreadBack() or p.hasNext()

    canCutOutline = canDeleteHeadline
    #@+node:ekr.20031218072017.2961: *6* c.canDemote
    def canDemote(self):
        c = self
        return c.p.hasNext()
    #@+node:ekr.20031218072017.2962: *6* c.canExpandAllHeadlines
    def canExpandAllHeadlines(self):
        """Return True if the Expand All Nodes menu item should be enabled."""
        c = self
        for p in c.all_positions():  # was c.all_unique_positions()
            if not p.isExpanded():
                return True
        return False
    #@+node:ekr.20031218072017.2963: *6* c.canExpandAllSubheads
    def canExpandAllSubheads(self):
        c = self
        for p in c.p.subtree():
            if not p.isExpanded():
                return True
        return False
    #@+node:ekr.20031218072017.2964: *6* c.canExpandSubheads
    def canExpandSubheads(self):
        c = self; current = c.p
        for p in current.children():
            if p != current and not p.isExpanded():
                return True
        return False
    #@+node:ekr.20031218072017.2287: *6* c.canExtract, canExtractSection & canExtractSectionNames
    def canExtract(self):
        c = self
        w = c.frame.body.wrapper
        return w and w.hasSelection()

    canExtractSectionNames = canExtract

    def canExtractSection(self):
        c = self
        w = c.frame.body.wrapper
        if not w: return False
        s = w.getSelectedText()
        if not s: return False
        line = g.get_line(s, 0)
        i1 = line.find("<<")
        j1 = line.find(">>")
        i2 = line.find("@<")
        j2 = line.find("@>")
        return -1 < i1 < j1 or -1 < i2 < j2
    #@+node:ekr.20031218072017.2965: *6* c.canFindMatchingBracket
    #@@nobeautify

    def canFindMatchingBracket(self):
        c = self
        brackets = "()[]{}"
        w = c.frame.body.wrapper
        s = w.getAllText()
        ins = w.getInsertPoint()
        c1 = s[ins]   if 0 <= ins   < len(s) else ''
        c2 = s[ins-1] if 0 <= ins-1 < len(s) else ''
        val = (c1 and c1 in brackets) or (c2 and c2 in brackets)
        return bool(val)
    #@+node:ekr.20040303165342: *6* c.canHoist & canDehoist
    def canDehoist(self):
        """
        Return True if do-hoist should be enabled in a menu.
        Should not be used in any other context.
        """
        c = self
        return bool(c.hoistStack)

    def canHoist(self):
        # This is called at idle time, so minimizing positions is crucial!
        """
        Return True if hoist should be enabled in a menu.
        Should not be used in any other context.
        """
        return True
        # c = self
        # if c.hoistStack:
            # p = c.hoistStack[-1].p
            # return p and not c.isCurrentPosition(p)
        # elif c.currentPositionIsRootPosition():
            # return c.currentPositionHasNext()
        # else:
            # return True
    #@+node:ekr.20031218072017.2970: *6* c.canMoveOutlineDown
    def canMoveOutlineDown(self):
        c = self; current = c.p
        return current and current.visNext(c)
    #@+node:ekr.20031218072017.2971: *6* c.canMoveOutlineLeft
    def canMoveOutlineLeft(self):
        c = self; p = c.p
        if c.hoistStack:
            bunch = c.hoistStack[-1]
            if p and p.hasParent():
                p.moveToParent()
                return p != bunch.p and bunch.p.isAncestorOf(p)
            return False
        return p and p.hasParent()
    #@+node:ekr.20031218072017.2972: *6* c.canMoveOutlineRight
    def canMoveOutlineRight(self):
        c = self; p = c.p
        if c.hoistStack:
            bunch = c.hoistStack[-1]
            return p and p.hasBack() and p != bunch.p
        return p and p.hasBack()
    #@+node:ekr.20031218072017.2973: *6* c.canMoveOutlineUp
    def canMoveOutlineUp(self):
        c = self; current = c.p
        visBack = current and current.visBack(c)
        if not visBack:
            return False
        if visBack.visBack(c):
            return True
        if c.hoistStack:
            limit, limitIsVisible = c.visLimit()
            if limitIsVisible:  # A hoist
                return current != limit
            # A chapter.
            return current != limit.firstChild()
        return current != c.rootPosition()
    #@+node:ekr.20031218072017.2974: *6* c.canPasteOutline
    def canPasteOutline(self, s=None):
        # c = self
        if not s:
            s = g.app.gui.getTextFromClipboard()
        if s and g.match(s, 0, g.app.prolog_prefix_string):
            return True
        return False
    #@+node:ekr.20031218072017.2975: *6* c.canPromote
    def canPromote(self):
        c = self; v = c.currentVnode()
        return v and v.hasChildren()
    #@+node:ekr.20031218072017.2977: *6* c.canSelect....
    def canSelectThreadBack(self):
        c = self; p = c.p
        return p.hasThreadBack()

    def canSelectThreadNext(self):
        c = self; p = c.p
        return p.hasThreadNext()

    def canSelectVisBack(self):
        c = self; p = c.p
        return p.visBack(c)

    def canSelectVisNext(self):
        c = self; p = c.p
        return p.visNext(c)
    #@+node:ekr.20031218072017.2978: *6* c.canShiftBodyLeft/Right
    def canShiftBodyLeft(self):
        c = self
        w = c.frame.body.wrapper
        return w and w.getAllText()

    canShiftBodyRight = canShiftBodyLeft
    #@+node:ekr.20031218072017.2979: *6* c.canSortChildren, canSortSiblings
    def canSortChildren(self):
        c = self; p = c.p
        return p and p.hasChildren()

    def canSortSiblings(self):
        c = self; p = c.p
        return p and (p.hasNext() or p.hasBack())
    #@+node:ekr.20031218072017.2980: *6* c.canUndo & canRedo
    def canUndo(self):
        c = self
        return c.undoer.canUndo()

    def canRedo(self):
        c = self
        return c.undoer.canRedo()
    #@+node:ekr.20031218072017.2981: *6* c.canUnmarkAll
    def canUnmarkAll(self):
        c = self
        for p in c.all_unique_positions():
            if p.isMarked():
                return True
        return False
    #@+node:ekr.20040323172420: *6* Slow routines: no longer used
    #@+node:ekr.20031218072017.2966: *7* c.canGoToNextDirtyHeadline (slow)
    def canGoToNextDirtyHeadline(self):
        c = self; current = c.p
        for p in c.all_unique_positions():
            if p != current and p.isDirty():
                return True
        return False
    #@+node:ekr.20031218072017.2967: *7* c.canGoToNextMarkedHeadline (slow)
    def canGoToNextMarkedHeadline(self):
        c = self; current = c.p
        for p in c.all_unique_positions():
            if p != current and p.isMarked():
                return True
        return False
    #@+node:ekr.20031218072017.2968: *7* c.canMarkChangedHeadline (slow)
    def canMarkChangedHeadlines(self):
        c = self
        for p in c.all_unique_positions():
            if p.isDirty():
                return True
        return False
    #@+node:ekr.20031218072017.2969: *7* c.canMarkChangedRoots (slow)
    def canMarkChangedRoots(self):
        c = self
        for p in c.all_unique_positions():
            if p.isDirty and p.isAnyAtFileNode():
                return True
        return False
    #@+node:ekr.20031218072017.2990: *4* c.Selecting
    #@+node:ekr.20031218072017.2992: *5* c.endEditing (calls tree.endEditLabel)
    # Ends the editing in the outline.

    def endEditing(self):
        c = self
        p = c.p
        if p:
            c.frame.tree.endEditLabel()
        # The following code would be wrong; c.endEditing is a utility method.
        # k = c.k
        # if k:
            # k.setDefaultInputState()
            # # Recolor the *body* text, **not** the headline.
            # k.showStateAndMode(w=c.frame.body.wrapper)
    #@+node:ville.20090525205736.12325: *5* c.getSelectedPositions
    def getSelectedPositions(self):
        """ Get list (PosList) of currently selected positions

        So far only makes sense on qt gui (which supports multiselection)
        """
        c = self
        return c.frame.tree.getSelectedPositions()
    #@+node:ekr.20031218072017.2991: *5* c.redrawAndEdit
    def redrawAndEdit(self, p, selectAll=False, selection=None, keepMinibuffer=False):
        """Redraw the screen and edit p's headline."""
        c, k = self, self.k
        c.redraw(p)  # This *must* be done now.
        if p:
            # This should request focus.
            c.frame.tree.editLabel(p, selectAll=selectAll, selection=selection)
            if k and not keepMinibuffer:
                # Setting the input state has no effect on focus.
                if selectAll:
                    k.setInputState('insert')
                else:
                    k.setDefaultInputState()
                # This *does* affect focus.
                k.showStateAndMode()
        else:
            g.trace('** no p')
        # Update the focus immediately.
        if not keepMinibuffer:
            c.outerUpdate()
    #@+node:ekr.20031218072017.2997: *5* c.selectPosition
    def selectPosition(self, p, **kwargs):
        """
        Select a new position, redrawing the screen *only* if we must
        change chapters.
        """
        if kwargs:
            print('c.selectPosition: all keyword args are ignored', g.callers())
        c = self
        cc = c.chapterController
        if not p:
            if not g.app.batchMode:  # A serious error.
                g.trace('Warning: no p', g.callers())
            return
        if cc and not cc.selectChapterLockout:
            cc.selectChapterForPosition(p)
                # Calls c.redraw only if the chapter changes.
        # De-hoist as necessary to make p visible.
        if c.hoistStack:
            while c.hoistStack:
                bunch = c.hoistStack[-1]
                if c.positionExists(p, bunch.p):
                    break
                else:
                    bunch = c.hoistStack.pop()
        c.frame.tree.select(p)
        c.setCurrentPosition(p)
            # Do *not* test whether the position exists!
            # We may be in the midst of an undo.

    # Compatibility, but confusing.

    selectVnode = selectPosition
    #@+node:ekr.20080503055349.1: *5* c.setPositionAfterSort
    def setPositionAfterSort(self, sortChildren):
        """
        Return the position to be selected after a sort.
        """
        c = self
        p = c.p
        p_v = p.v
        parent = p.parent()
        parent_v = p._parentVnode()
        if sortChildren:
            return parent or c.rootPosition()
        if parent:
            p = parent.firstChild()
        else:
            p = leoNodes.Position(parent_v.children[0])
        while p and p.v != p_v:
            p.moveToNext()
        p = p or parent
        return p
    #@+node:ekr.20070226113916: *5* c.treeSelectHelper
    def treeSelectHelper(self, p):
        c = self
        if not p: p = c.p
        if p:
            # Do not call expandAllAncestors here.
            c.selectPosition(p)
            c.redraw_after_select(p)
        c.treeFocusHelper()
            # This is essential.
    #@+node:ekr.20171123135625.51: *4* c.updateBodyPane (handles changeNodeContents)
    def updateBodyPane(
        self, head, middle, tail, undoType, oldSel, oldYview, preserveSel=False):
        """Handle changed text in the body pane."""
        c, p = self, self.p
        body = c.frame.body
        # Update the text and notify the event handler.
        body.setSelectionAreas(head, middle, tail)
        # Expand the selection.
        head = head or ''
        middle = middle or ''
        tail = tail or ''
        if preserveSel:
            # Leo 5.6: just use the computed oldSel.
            i, j = oldSel
        else:
            i = len(head)
            j = max(i, len(head) + len(middle) - 1)
            newSel = i, j
        body.wrapper.setSelectionRange(i, j)
        # This handles the undo.
        body.onBodyChanged(undoType, oldSel=oldSel or newSel, oldYview=oldYview)
        # Update the changed mark and icon.
        p.setDirty()
        c.setChanged()
        c.redraw_after_icons_changed()
        # Scroll as necessary.
        if oldYview:
            body.wrapper.setYScrollPosition(oldYview)
        else:
            body.wrapper.seeInsertPoint()
        body.wrapper.setFocus()
        c.recolor()
    #@+node:ekr.20130823083943.12559: *3* c.recursiveImport
    def recursiveImport(self, dir_, kind,
        add_context=None,  # Override setting only if True/False
        add_file_context=None,  # Override setting only if True/False
        add_path=True,
        recursive=True,
        safe_at_file=True,
        theTypes=None,
        # force_at_others=False, # tag:no-longer-used
        ignore_pattern=None
    ):
        #@+<< docstring >>
        #@+node:ekr.20130823083943.12614: *4* << docstring >>
        """
        Recursively import all python files in a directory and clean the results.

        Parameters::
            dir_              The root directory or file to import.
            kind              One of ('@clean','@edit','@file','@nosent').
            add_path=True     True: add a full @path directive to @<file> nodes.
            recursive=True    True: recurse into subdirectories.
            safe_at_file=True True: produce @@file nodes instead of @file nodes.
            theTypes=None     A list of file extensions to import.
                              None is equivalent to ['.py']

        This method cleans imported files as follows:

        - Replace backslashes with forward slashes in headlines.
        - Remove empty nodes.
        - Add @path directives that reduce the needed path specifiers in descendant nodes.
        - Add @file to nodes or replace @file with @@file.
        """
        #@-<< docstring >>
        c = self
        if g.os_path_exists(dir_):
            # Import all files in dir_ after c.p.
            try:
                import leo.core.leoImport as leoImport
                cc = leoImport.RecursiveImportController(c, kind,
                    add_context=add_context,
                    add_file_context=add_file_context,
                    add_path=add_path,
                    recursive=recursive,
                    safe_at_file=safe_at_file,
                    theTypes=['.py'] if not theTypes else theTypes,
                    # force_at_others = force_at_others,  # tag:no-longer-used
                    ignore_pattern=ignore_pattern
                )
                cc.run(dir_)
            finally:
                c.redraw()
        else:
            g.es_print(f"Does not exist: {dir_}")
    #@+node:ekr.20171124084149.1: *3* c.Scripting utils
    #@+node:ekr.20160201072634.1: *4* c.cloneFindByPredicated
    def cloneFindByPredicate(self,
        generator,  # The generator used to traverse the tree.
        predicate,  # A function of one argument p, returning True
                       # if p should be included in the results.
        failMsg=None,  # Failure message. Default is no message.
        flatten=False,  # True: Put all matches at the top level.
        iconPath=None,  # Full path to icon to attach to all matches.
        redraw=True,  # True: redraw the outline,
        undoType=None,  # The undo name, shown in the Edit:Undo menu.
                       # The default is 'clone-find-predicate'
    ):
        """
        Traverse the tree given using the generator, cloning all positions for
        which predicate(p) is True. Undoably move all clones to a new node, created
        as the last top-level node. Returns the newly-created node. Arguments:

        generator,      The generator used to traverse the tree.
        predicate,      A function of one argument p returning true if p should be included.
        failMsg=None,   Message given if nothing found. Default is no message.
        flatten=False,  True: Move all node to be parents of the root node.
        iconPath=None,  Full path to icon to attach to all matches.
        redraw=True,    True: redraw the screen.
        undo_type=None, The undo/redo name shown in the Edit:Undo menu.
                        The default is 'clone-find-predicate'
        """
        c = self
        u, undoType = c.undoer, undoType or 'clone-find-predicate'
        clones, root, seen = [], None, set()
        for p in generator():
            if predicate(p) and p.v not in seen:
                c.setCloneFindByPredicateIcon(iconPath, p)
                if flatten:
                    seen.add(p.v)
                else:
                    for p2 in p.self_and_subtree(copy=False):
                        seen.add(p2.v)
                clones.append(p.copy())
        if clones:
            undoData = u.beforeInsertNode(c.p)
            root = c.createCloneFindPredicateRoot(flatten, undoType)
            for p in clones:
                clone = p.clone()
                clone.moveToLastChildOf(root)
            u.afterInsertNode(root, undoType, undoData)
            if redraw:
                c.selectPosition(root)
                c.setChanged()
                c.contractAllHeadlines()
                root.expand()
                c.redraw()
                c.selectPosition(root)
        elif failMsg:
            g.es_print(failMsg, color='red')
        return root
    #@+node:ekr.20160304054950.1: *5* c.setCloneFindByPredicateIcon
    def setCloneFindByPredicateIcon(self, iconPath, p):
        """Attach an icon to p.v.u."""
        if iconPath and g.os_path_exists(iconPath) and not g.os_path_isdir(iconPath):
            aList = p.v.u.get('icons', [])
            for d in aList:
                if d.get('file') == iconPath:
                    break
            else:
                aList.append({
                    'type': 'file',
                    'file': iconPath,
                    'on': 'VNode',
                    # 'relPath': iconPath,
                    'where': 'beforeHeadline',
                    'xoffset': 2, 'xpad': 1,
                    'yoffset': 0,

                })
                p.v.u['icons'] = aList
        elif iconPath:
            g.trace('bad icon path', iconPath)
    #@+node:ekr.20160201075438.1: *5* c.createCloneFindPredicateRoot
    def createCloneFindPredicateRoot(self, flatten, undoType):
        """Create a root node for clone-find-predicate."""
        c = self
        root = c.lastTopLevel().insertAfter()
        root.h = undoType + (' (flattened)' if flatten else '')
        return root
    #@+node:peckj.20131023115434.10114: *4* c.createNodeHierarchy
    def createNodeHierarchy(self, heads, parent=None, forcecreate=False):
        """ Create the proper hierarchy of nodes with headlines defined in
            'heads' under 'parent'

            params:
            parent - parent node to start from.  Set to None for top-level nodes
            heads - list of headlines in order to create, i.e. ['foo','bar','baz']
                    will create:
                      parent
                      -foo
                      --bar
                      ---baz
            forcecreate - If False (default), will not create nodes unless they don't exist
                          If True, will create nodes regardless of existing nodes
            returns the final position ('baz' in the above example)
        """
        u = self.undoer
        undoType = 'Create Node Hierarchy'
        undoType2 = 'Insert Node In Hierarchy'
        u_node = parent or self.rootPosition()
        undoData = u.beforeChangeGroup(u_node, undoType)
        changed_node = False
        for idx, head in enumerate(heads):
            if parent is None and idx == 0:  # if parent = None, create top level node for first head
                if not forcecreate:
                    for pos in self.all_positions():
                        if pos.h == head:
                            parent = pos
                            break
                if parent is None or forcecreate:
                    u_d = u.beforeInsertNode(u_node)
                    n = self.rootPosition().insertAfter()
                    n.h = head
                    u.afterInsertNode(n, undoType2, u_d)
                    parent = n
            else:  # else, simply create child nodes each round
                if not forcecreate:
                    for ch in parent.children():
                        if ch.h == head:
                            parent = ch
                            changed_node = True
                            break
                if parent.h != head or not changed_node or forcecreate:
                    u_d = u.beforeInsertNode(parent)
                    n = parent.insertAsLastChild()
                    n.h = head
                    u.afterInsertNode(n, undoType2, u_d)
                    parent = n
            changed_node = False
        u.afterChangeGroup(parent, undoType, undoData)
        return parent  # actually the last created/found position
    #@+node:ekr.20100802121531.5804: *4* c.deletePositionsInList
    def deletePositionsInList(self, aList, redraw=True):
        """
        Delete all vnodes corresponding to the positions in aList.

        See "Theory of operation of c.deletePositionsInList" in LeoDocs.leo.
        """
        # New implementation by Vitalije 2020-03-17 17:29 
        c = self
        # Ensure all positions are valid.
        aList = [p for p in aList if c.positionExists(p)]
        if not aList:
            return []

        def p2link(p):
            parent_v = p.stack[-1][0] if p.stack else c.hiddenRootNode
            return p._childIndex, parent_v

        links_to_be_cut = sorted(set(map(p2link, aList)), key=lambda x:-x[0])
        undodata = []
        for i, v in links_to_be_cut:
            ch = v.children.pop(i)
            ch.parents.remove(v)
            undodata.append((v.gnx, i, ch.gnx))
        if redraw:
            if not c.positionExists(c.p):
                c.setCurrentPosition(c.rootPosition())
            c.redraw()
        return undodata

    #@+node:vitalije.20200318161844.1: *4* c.undoableDeletePositions
    def undoableDeletePositions(self, aList):
        """
        Deletes all vnodes corresponding to the positions in aList,
        and make changes undoable.
        """
        c = self
        u = c.undoer
        data = c.deletePositionsInList(aList)
        gnx2v = c.fileCommands.gnxDict
        def undo():
            for pgnx, i, chgnx in reversed(u.getBead(u.bead).data):
                v = gnx2v[pgnx]
                ch = gnx2v[chgnx]
                v.children.insert(i, ch)
                ch.parents.append(v)
            if not c.positionExists(c.p):
                c.setCurrentPosition(c.rootPosition())
        def redo():
            for pgnx, i, chgnx in u.getBead(u.bead + 1).data:
                v = gnx2v[pgnx]
                ch = v.children.pop(i)
                ch.parents.remove(v)
            if not c.positionExists(c.p):
                c.setCurrentPosition(c.rootPosition())
        u.pushBead(g.Bunch(
            data=data,
            undoType='delete nodes',
            undoHelper=undo,
            redoHelper=redo,
        ))
    #@+node:ekr.20091211111443.6265: *4* c.doBatchOperations & helpers
    def doBatchOperations(self, aList=None):
        # Validate aList and create the parents dict
        if aList is None:
            aList = []
        ok, d = self.checkBatchOperationsList(aList)
        if not ok:
            g.error('do-batch-operations: invalid list argument')
            return
        for v in list(d.keys()):
            aList2 = d.get(v, [])
            if aList2:
                aList.sort()
    #@+node:ekr.20091211111443.6266: *5* c.checkBatchOperationsList
    def checkBatchOperationsList(self, aList):
        ok = True; d = {}
        for z in aList:
            try:
                op, p, n = z
                ok = (op in ('insert', 'delete') and
                    isinstance(p, leoNodes.position) and isinstance(n, int))
                if ok:
                    aList2 = d.get(p.v, [])
                    data = n, op
                    aList2.append(data)
                    d[p.v] = aList2
            except ValueError:
                ok = False
            if not ok: break
        return ok, d
    #@+node:ekr.20091002083910.6106: *4* c.find_b & find_h (PosList)
    #@+<< PosList doc >>
    #@+node:bob.20101215134608.5898: *5* << PosList doc >>
    #@@language rest
    #@+at
    # List of positions
    #
    # Functions find_h() and find_b() both return an instance of PosList.
    #
    # Methods filter_h() and filter_b() refine a PosList.
    #
    # Method children() generates a new PosList by descending one level from
    # all the nodes in a PosList.
    #
    # A chain of PosList method calls must begin with find_h() or find_b().
    # The rest of the chain can be any combination of filter_h(),
    # filter_b(), and children(). For example:
    #
    #     pl = c.find_h('@file.*py').children().filter_h('class.*').filter_b('import (.*)')
    #
    # For each position, pos, in the PosList returned, find_h() and
    # filter_h() set attribute pos.mo to the match object (see Python
    # Regular Expression documentation) for the pattern match.
    #
    # Caution: The pattern given to find_h() or filter_h() must match zero
    # or more characters at the beginning of the headline.
    #
    # For each position, pos, the postlist returned, find_b() and filter_b()
    # set attribute pos.matchiter to an iterator that will return a match
    # object for each of the non-overlapping matches of the pattern in the
    # body of the node.
    #@-<< PosList doc >>
    #@+node:ville.20090311190405.70: *5* c.find_h
    def find_h(self, regex, flags=re.IGNORECASE):
        """ Return list (a PosList) of all nodes where zero or more characters at
        the beginning of the headline match regex
        """
        c = self
        pat = re.compile(regex, flags)
        res = leoNodes.PosList()
        for p in c.all_positions():
            m = re.match(pat, p.h)
            if m:
                pc = p.copy()
                pc.mo = m
                res.append(pc)
        return res
    #@+node:ville.20090311200059.1: *5* c.find_b
    def find_b(self, regex, flags=re.IGNORECASE | re.MULTILINE):
        """ Return list (a PosList) of all nodes whose body matches regex
        one or more times.

        """
        c = self
        pat = re.compile(regex, flags)
        res = leoNodes.PosList()
        for p in c.all_positions():
            m = re.finditer(pat, p.b)
            t1, t2 = itertools.tee(m, 2)
            try:
                t1.__next__()
            except StopIteration:
                continue
            pc = p.copy()
            pc.matchiter = t2
            res.append(pc)
        return res
    #@+node:ekr.20150410095543.1: *4* c.findNodeOutsideAnyAtFileTree
    def findNodeOutsideAnyAtFileTree(self, target):
        """Select the first clone of target that is outside any @file node."""
        c = self
        if target.isCloned():
            v = target.v
            for p in c.all_positions():
                if p.v == v:
                    for parent in p.self_and_parents(copy=False):
                        if parent.isAnyAtFileNode():
                            break
                    else:
                        return p
        return target
    #@+node:ekr.20171124155725.1: *3* c.Settings
    #@+node:ekr.20171114114908.1: *4* c.registerReloadSettings
    def registerReloadSettings(self, obj):
        """Enter object into c.configurables."""
        c = self
        if obj not in c.configurables:
            c.configurables.append(obj)
    #@+node:ekr.20170221040621.1: *4* c.reloadConfigurableSettings
    def reloadConfigurableSettings(self):
        """
        Call all reloadSettings method in c.subcommanders, c.configurables and
        other known classes.
        """
        c = self
        table = [
            g.app.gui,
            g.app.pluginsController,
            c.k.autoCompleter,
            c.frame, c.frame.body, c.frame.log, c.frame.tree,
            c.frame.body.colorizer,
            getattr(c.frame.body.colorizer, 'highlighter', None),
        ]
        for obj in table:
            if obj:
                c.registerReloadSettings(obj)
        c.configurables = list(set(c.configurables))
            # Useful now that instances add themselves to c.configurables.
        c.configurables.sort(key=lambda obj: obj.__class__.__name__.lower())
        for obj in c.configurables:
            func = getattr(obj, 'reloadSettings', None)
            if func:
                # pylint: disable=not-callable
                try:
                    func()
                except Exception:
                    g.es_exception()
                    c.configurables.remove(obj)
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo

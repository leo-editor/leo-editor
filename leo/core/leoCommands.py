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
try:
    import builtins # Python 3
except ImportError:
    import __builtin__ as builtins # Python 2.
import imp
import itertools
import os
import re
import sys
import time
import tokenize # for c.checkAllPythonCode
try:
    import tabnanny # for Check Python command # Does not exist in jython
except ImportError:
    tabnanny = None
#@-<< imports >>

def cmd(name):
    '''Command decorator for the Commands class.'''
    return g.new_cmd_decorator(name, ['c',])

#@+others
#@+node:ekr.20160514120615.1: ** class Commands
class Commands(object):
    """
    A per-outline class that implements most of Leo's commands. The
    "c" predefined object is an instance of this class.

    c.initObjects() creates sucommanders corresponding to files in the
    leo/core and leo/commands. All of Leo's core code is accessible
    via this class and its subcommanders.

    g.app.pluginsController is Leo's plugins controller. Many plugins
    inject controllers objects into the Commands class. These are
    another kind of subcommander.
    """
    #@+others
    #@+node:ekr.20031218072017.2811: *3*  c.Birth & death
    #@+node:ekr.20031218072017.2812: *4* c.__init__ & helpers
    def __init__(self, fileName, relativeFileName=None, gui=None, previousSettings=None):
        trace = (False or g.trace_startup) and not g.unitTesting
        tag = 'Commands.__init__ %s' % (g.shortFileName(fileName))
        if trace and g.trace_startup: g.es_debug('(Commands)', g.shortFileName(fileName))
        c = self
        if trace and not g.trace_startup:
            t1 = time.time()
        # Official ivars.
        self._currentPosition = None
        self._topPosition = None
        self.frame = None
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
        if trace and not g.trace_startup:
            g.printDiffTime('%s: after controllers created' % (tag), t1)
        # Complete the init!
        c.finishCreate()
        if trace and not g.trace_startup:
            g.printDiffTime('%s: after c.finishCreate' % (tag), t1)
    #@+node:ekr.20120217070122.10475: *5* c.computeWindowTitle
    def computeWindowTitle(self, fileName):
        '''Set the window title and fileName.'''
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
        '''Init ivars used while executing a command.'''
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
        self.navPrefix = g.u('') # Must always be a string.
        self.navTime = None

        self.sqlite_connection = None
    #@+node:ekr.20120217070122.10466: *5* c.initDebugIvars
    def initDebugIvars(self):
        '''Init Commander debugging ivars.'''
        self.command_count = 0
        self.scanAtPathDirectivesCount = 0
        self.trace_focus_count = 0
    #@+node:ekr.20120217070122.10471: *5* c.initDocumentIvars
    def initDocumentIvars(self):
        '''Init per-document ivars.'''
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
        '''Init ivars relating to gui events.'''
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
        self.requestBringToFront = None # A commander, or None.
        self.requestCloseWindow = False
        ### self.requestRecolorFlag = False
        self.requestedFocusWidget = None
        self.requestedIconify = '' # 'iconify','deiconify'
    #@+node:ekr.20120217070122.10472: *5* c.initFileIvars
    def initFileIvars(self, fileName, relativeFileName):
        '''Init file-related ivars of the commander.'''
        self.changed = False
            # True: the ouline has changed since the last save.
        self.ignored_at_file_nodes = []
            # List of nodes for error dialog.
        self.import_error_nodes = []
            #
        self.last_dir = None
            # The last used directory.
        self.mFileName = fileName or ''
            # Do _not_ use os_path_norm: it converts an empty path to '.' (!!)
        self.mRelativeFileName = relativeFileName or ''
            #
        self.openDirectory = None
            #
        self.wrappedFileName = None
            # The name of the wrapped file, for wrapper commanders.
            # Set by LM.initWrapperLeoFile
    #@+node:ekr.20120217070122.10469: *5* c.initOptionsIvars
    def initOptionsIvars(self):
        '''Init Commander ivars corresponding to user options.'''
        self.fixed = False
        self.fixedWindowPosition = []
        self.forceExecuteEntireBody = False
        self.focus_border_color = 'white'
        self.focus_border_width = 1 # pixels
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
        self.use_body_focus_border = True
        # self.use_focus_border = False
            # Replaced by style-sheet entries.
        self.vim_mode = False
    #@+node:ekr.20120217070122.10468: *5* c.initObjectIvars
    def initObjectIvars(self):
        # These ivars are set later by leoEditCommands.createEditCommanders
        self.abbrevCommands = None
        self.editCommands = None
        self.db = {} # May be set to a PickleShare instance later.
        self.chapterCommands = None
        self.controlCommands = None
        self.convertCommands = None
        self.debugCommands = None
        self.editFileCommands = None
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
        trace = (False or g.trace_startup) and not g.unitTesting
        c = self
        if trace: g.es_debug(c.shortFileName(), g.app.gui)
        gnx = 'hidden-root-vnode-gnx'
        assert not hasattr(c, 'fileCommands'), c.fileCommands

        class DummyFileCommands:
            def __init__(self):
                self.gnxDict = {}

        c.fileCommands = DummyFileCommands()
        self.hiddenRootNode = leoNodes.VNode(context=c, gnx=gnx)
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
        import leo.core.leoCache as leoCache
        import leo.core.leoChapters as leoChapters
        # User commands...
        import leo.commands.abbrevCommands as abbrevCommands
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
        # Other subcommanders.
        import leo.core.leoFind as leoFind # Leo 4.11.1
        import leo.core.leoKeys as leoKeys
        import leo.core.leoFileCommands as leoFileCommands
        import leo.core.leoImport as leoImport
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
        self.persistenceController  = leoPersistence.PersistenceDataController(c)
        self.printingController     = leoPrinting.PrintingController(c)
        self.rstCommands            = leoRst.RstCommands(c)
        self.tangleCommands         = leoTangle.TangleCommands(c)
        self.testManager            = leoTest.TestManager(c)
        self.vimCommands            = leoVim.VimCommands(c)
        # User commands
        self.abbrevCommands     = abbrevCommands.AbbrevCommandsClass(c)
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
        # Create the list of subcommanders.
        self.subCommanders = [
            self.abbrevCommands,
            self.atFileCommands,
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
        ]
        # Other objects
        self.cacher = leoCache.Cacher(c)
        self.cacher.initFileDB(self.mFileName)
        self.undoer = leoUndo.Undoer(self)
        import leo.plugins.free_layout as free_layout
        self.free_layout = free_layout.FreeLayoutController(c)
        if hasattr(g.app.gui, 'styleSheetManagerClass'):
            self.styleSheetManager = g.app.gui.styleSheetManagerClass(c)
            self.subCommanders.append(self.styleSheetManager)
        else:
            self.styleSheetManager = None
    #@+node:ekr.20140815160132.18837: *5* c.initSettings
    def initSettings(self, previousSettings):
        '''Init the settings *before* initing the objects.'''
        c = self
        import leo.core.leoConfig as leoConfig
        c.config = leoConfig.LocalConfigManager(c, previousSettings)
        g.app.config.setIvarsFromSettings(c)
    #@+node:ekr.20031218072017.2814: *4* c.__repr__ & __str__
    def __repr__(self):
        return "Commander %d: %s" % (id(self), repr(self.mFileName))

    __str__ = __repr__
    #@+node:ekr.20050920093543: *4* c.finishCreate & helpers
    def finishCreate(self):
        '''
        Finish creating the commander and all sub-objects.
        This is the last step in the startup process.
        '''
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
        c.frame.menu.finishCreate()
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
        '''
        Create all entries in c.commandsDict.
        Do *not* clear c.commandsDict here.
        '''
        for name, func in g.global_commands_dict.items():
            self.k.registerCommand(commandName=name, shortcut=None, func=func)
    #@+node:ekr.20051007143620: *5* c.printCommandsDict
    def printCommandsDict(self):
        c = self
        print('Commands...')
        for key in sorted(c.commandsDict):
            command = c.commandsDict.get(key)
            print('%30s = %s' % (
                key, command.__name__ if command else '<None>'))
        print('')
    #@+node:ekr.20041130173135: *4* c.hash
    # This is a bad idea.

    def hash(self):
        c = self
        if c.mFileName:
            return c.os_path_finalize(c.mFileName).lower()
        else:
            return 0
    #@+node:ekr.20110509064011.14563: *4* c.idle_focus_helper & helpers
    idle_focus_count = 0

    def idle_focus_helper(self, tag, keys):
        '''An idle-tme handler that ensures that focus is *somewhere*.'''
        trace = (False or g.app.trace_focus) and not g.unitTesting
        # if trace: g.trace('active:', g.app.gui and g.app.gui.active)
        trace_inactive_focus = True
        trace_in_dialog = True
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
        w = g.app.gui.get_focus(at_idle = True)
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
            g.trace('%s inactive focus: %s' % (count, w_class))
    #@+node:ekr.20160427062131.1: *5* c.is_unusual_focus
    def is_unusual_focus(self, w):
        '''Return True if w is not in an expected place.'''
        if 1:
            # Fix bug 270: Leo's keyboard events doesn't work after "Insert"
            # on headline and Alt+Tab, Alt+Tab
            # Fix #276: Focus lost...in Nav text input
            import leo.plugins.qt_frame as qt_frame
            return isinstance(w, qt_frame.QtTabBarWrapper)
        else:
            # Wrong: we can't list all the "usual" widgets.
            from leo.core.leoQt import QtWidgets
            table = (
                QtWidgets.QListWidget,
                QtWidgets.QTextEdit,
                QtWidgets.QLineEdit,
                qt_frame.LeoQTreeWidget,
            )
            return not isinstance(w, table)
    #@+node:ekr.20150403063658.1: *5* c.trace_idle_focus
    last_unusual_focus = None
    # last_no_focus = False

    def trace_idle_focus(self, w):
        '''Trace the focus for w, minimizing chatter.'''
        from leo.core.leoQt import QtWidgets
        import leo.plugins.qt_frame as qt_frame
        trace = (False or g.app.trace_focus) and not g.unitTesting
        trace_known = True
        c = self
        table = (
            QtWidgets.QWidget,
            qt_frame.LeoQTreeWidget,
        )
        count = c.idle_focus_count
        if w:
            w_class = w and w.__class__.__name__
            c.last_no_focus = False
            if self.is_unusual_focus(w):
                if trace:
                    g.trace('%s unusual focus: %s' % (count, w_class))
            else:
                c.last_unusual_focus = None
                if isinstance(w, table):
                    if trace and trace_known:
                        g.trace('%s known focus: %s' % (count, w_class))
                elif trace:
                    g.trace('%s unknown focus: %s' % (count, w_class))
        else:
            # c.last_no_focus = True
            g.trace('%s no focus' % (count))
    #@+node:ekr.20081005065934.1: *4* c.initAfterLoad
    def initAfterLoad(self):
        '''Provide an offical hook for late inits of the commander.'''
        pass
    #@+node:ekr.20090213065933.6: *4* c.initConfigSettings
    def initConfigSettings(self):
        '''Init all cached commander config settings.'''
        trace = (False or g.trace_startup) and not g.unitTesting
        c = self
        if trace: g.es_debug(c.configInited, c.shortFileName())
        getBool = c.config.getBool
        getColor = c.config.getColor
        getData = c.config.getData
        getInt = c.config.getInt
        c.allow_at_in_paragraphs = getBool('allow-at-in-paragraphs', default=False)
        c.autoindent_in_nocolor = getBool('autoindent_in_nocolor_mode')
        c.collapse_nodes_after_move = getBool('collapse_nodes_after_move')
        c.collapse_on_lt_arrow = getBool('collapse_on_lt_arrow', default=True)
        c.contractVisitedNodes = getBool('contractVisitedNodes')
        c.fixed = getBool('fixedWindow', default=False)
        c.fixedWindowPositionData = getData('fixedWindowPosition')
        c.focus_border_color = getColor('focus_border_color') or 'red'
        c.focus_border_command_state_color = getColor('focus_border_command_state_color') or 'blue'
        c.focus_border_overwrite_state_color = getColor('focus_border_overwrite_state_color') or 'green'
        c.focus_border_width = getInt('focus_border_width') or 1 # pixels
        c.forceExecuteEntireBody = getBool('force_execute_entire_body', default=False)
        c.make_node_conflicts_node = getBool('make-node-conflicts-node', default=True)
        c.max_pre_loaded_body_chars = c.config.getInt('max-pre-loaded-body-chars') or 0
        c.outlineHasInitialFocus = getBool('outline_pane_has_initial_focus')
        c.page_width = getInt('page_width') or 132
        c.putBitsFlag = getBool('put_expansion_bits_in_leo_files', default=True)
        c.sparse_move = getBool('sparse_move_outline_left')
        c.sparse_find = getBool('collapse_nodes_during_finds')
        c.sparce_spell = getBool('collapse_nodes_while_spelling')
        c.stayInTreeAfterSelect = getBool('stayInTreeAfterSelect')
        c.smart_tab = getBool('smart_tab')
        c.tab_width = getInt('tab_width') or -4
        c.use_body_focus_border = getBool('use_body_focus_border', default=True)
        # c.use_focus_border = getBool('use_focus_border', default=True)
            # Not used: replaced by stylesheet settings.
        c.verbose_check_outline = getBool('verbose_check_outline', default=False)
        c.vim_mode = getBool('vim_mode', default=False)
        c.write_script_file = getBool('write_script_file')
    #@+node:ekr.20090213065933.7: *4* c.setWindowPosition
    def setWindowPosition(self):
        c = self
        # g.trace(c.fixed,c.fixedWindowPosition)
        if c.fixedWindowPositionData:
            try:
                aList = [z.strip() for z in c.fixedWindowPositionData if z.strip()]
                w, h, l, t = aList
                c.fixedWindowPosition = int(w), int(h), int(l), int(t)
            except Exception:
                g.error('bad @data fixedWindowPosition',
                    repr(self.fixedWindowPosition))
        else:
            c.windowPosition = 500, 700, 50, 50 # width,height,left,top.
    #@+node:ekr.20080610085158.2: *3* c.add_command
    def add_command(self, menu, **keys):
        c = self
        command = keys.get('command')
        if command:
            # Command is always either:
            # one of two callbacks defined in createMenuEntries or
            # recentFilesCallback, defined in createRecentFilesMenuItems.

            def add_commandCallback(c=c, command=command):
                # g.trace(command)
                val = command()
                # Careful: func may destroy c.
                if c.exists: c.outerUpdate()
                return val

            keys['command'] = add_commandCallback
            menu.add_command(** keys)
        else:
            g.trace('can not happen: no "command" arg')
    #@+node:ekr.20110510052422.14618: *3* c.alert
    def alert(self, message):
        c = self
        # The unit tests just tests the args.
        if not g.unitTesting:
            g.es(message)
            g.app.gui.alert(c, message)
    #@+node:ekr.20150422080541.1: *3* c.backup
    def backup(self, fileName=None, prefix=None, useTimeStamp=True):
        '''
        Back up given fileName or c.fileName().
        If useTimeStamp is True, append a timestamp to the filename.
        '''
        c = self
        fn = fileName or c.fileName()
        if not fn:
            return
        theDir, base = g.os_path_split(fn)
        if useTimeStamp:
            if base.endswith('.leo'):
                base = base[: -4]
            stamp = time.strftime("%Y%m%d-%H%M%S")
            branch = prefix + '-' if prefix else ''
            fn = '%s%s-%s.leo' % (branch, base, stamp)
            path = g.os_path_finalize_join(theDir, fn)
        else:
            path = fn
        if path:
            # Save the outline to the .
            c.saveTo(fileName=path)
                # Issues saved message.
            g.es('in', theDir)
    #@+node:ekr.20110605040658.17005: *3* c.check_event
    def check_event(self, event):
        '''Check an event object.'''
        trace = False and not g.unitTesting
        # c = self
        k = self.k
        import leo.core.leoGui as leoGui

        def test(val, message):
            if trace:
                if g.unitTesting:
                    assert val, message
                else:
                    if not val: print('check_event', message)

        if not event:
            return
        isLeoKeyEvent = isinstance(event, leoGui.LeoKeyEvent)
        stroke = event.stroke
        got = event.char
        if trace: g.trace('plain: %s, stroke: %s, char: %s' % (
            k.isPlainKey(stroke), repr(stroke), repr(event.char)))
        if g.unitTesting:
            expected = k.stroke2char(stroke)
                # Be strict for unit testing.
        elif stroke and (stroke.find('Alt+') > -1 or stroke.find('Ctrl+') > -1):
            expected = event.char
                # Alas, Alt and Ctrl bindings must *retain* the char field,
                # so there is no way to know what char field to expect.
        elif trace or k.isPlainKey(stroke):
            expected = k.stroke2char(stroke)
                # Perform the full test.
        else:
            expected = event.char
                # disable the test.
                # We will use the (weird) key value for, say, Ctrl-s,
                # if there is no binding for Ctrl-s.
        test(isLeoKeyEvent, 'not leo event: %s, callers: %s' % (
            repr(event), g.callers()))
        test(expected == got, 'stroke: %s, expected char: %s, got: %s' % (
                repr(stroke), repr(expected), repr(got)))
    #@+node:ekr.20031218072017.2818: *3* c.Top-level commands
    #@+node:ekr.20170221033738.1: *4* c.reloadSettings & helpers
    @cmd('reload-settings')
    def reloadSettings(self, event=None):
        '''Reload all static abbreviations from all config files.'''
        self.reloadSettingsHelper(all=False)

    @cmd('reload-all-settings')
    def reloadAllSettings(self, event=None):
        '''Reload all static abbreviations from all config files.'''
        self.reloadSettingsHelper(all=True)
    #@+node:ekr.20170221034501.1: *5* c.reloadSettingsHelper
    def reloadSettingsHelper(self, all):
        '''Reload settings in all commanders, or just self.'''
        lm = g.app.loadManager
        commanders = g.app.commanders() if all else [self]
        lm.readGlobalSettingsFiles()
            # Read leoSettings.leo and myLeoSettings.leo, using a null gui.
        for c in commanders:
            changed = c.isChanged()
            previousSettings = lm.getPreviousSettings(fn=c.mFileName)
                # Read the local file, using a null gui.
            c.initSettings(previousSettings)
                # Init the config classes.
            c.initConfigSettings()
                # Init the commander config ivars.
            c.reloadSubcommanderSettings()
                # Reload settings in all subcommanders.
            c.setChanged(changed)
                # Restore the changed bit.
            # c.redraw()
                # Redraw so a pasted temp node isn't visible
    #@+node:ekr.20170221040621.1: *5* c.reloadSubcommanderSettings
    def reloadSubcommanderSettings(self):
        '''
        Reload settings in all subcommanders that have either a
        reload_settings or reloadSettings method.
        '''
        trace = False and not g.unitTesting
        c = self
        for subcommander in c.subCommanders:
            for ivar in ('reloadSettings', 'reload_settings'):
                func = getattr(subcommander, ivar, None)
                if func:
                    # pylint: disable=not-callable
                    if trace:
                        g.es_print('reloading settings in',
                            subcommander.__class__.__name__)
                    func()
    #@+node:ekr.20150329162703.1: *4* Clone find...
    #@+node:ekr.20160224175312.1: *5* c.cffm & c.cfam
    @cmd('clone-find-all-marked')
    @cmd('cfam')
    def cloneFindAllMarked(self, event=None):
        '''
        clone-find-all-marked, aka cfam.

        Create an organizer node whose descendants contain clones of all marked
        nodes. The list is *not* flattened: clones appear only once in the
        descendants of the organizer node.
        '''
        self.cloneFindMarkedHelper(flatten=False)

    @cmd('clone-find-all-flattened-marked')
    @cmd('cffm')
    def cloneFindAllFlattenedMarked(self, event=None):
        '''
        clone-find-all-flattened-marked, aka cffm.

        Create an organizer node whose direct children are clones of all marked
        nodes. The list is flattened: every cloned node appears as a direct
        child of the organizer node, even if the clone also is a descendant of
        another cloned node.
        '''
        self.cloneFindMarkedHelper(flatten=True)
    #@+node:ekr.20140828080010.18532: *5* c.cloneFindParents
    @cmd('clone-find-parents')
    def cloneFindParents(self, event=None):
        '''
        Create an organizer node whose direct children are clones of all
        parents of the selected node, which must be a clone.
        '''
        c, u = self, self.undoer
        p = c.p
        if not p: return
        if not p.isCloned():
            g.es('not a clone: %s' % p.h)
            return
        p0 = p.copy()
        undoType = 'Find Clone Parents'
        aList = c.vnode2allPositions(p.v)
        if not aList:
            g.trace('can not happen: no parents')
            return
        # Create the node as the last top-level node.
        # All existing positions remain valid.
        u.beforeChangeGroup(p0, undoType)
        top = c.rootPosition()
        while top.hasNext():
            top.moveToNext()
        b = u.beforeInsertNode(p0)
        found = top.insertAfter()
        found.h = 'Found: parents of %s' % p.h
        u.afterInsertNode(found, 'insert', b)
        seen = []
        for p2 in aList:
            parent = p2.parent()
            if parent and parent.v not in seen:
                seen.append(parent.v)
                b = u.beforeCloneNode(parent)
                clone = parent.clone()
                clone.moveToLastChildOf(found)
                u.afterCloneNode(clone, 'clone', b, dirtyVnodeList=[])
        u.afterChangeGroup(p0, undoType)
        c.selectPosition(found)
        c.setChanged(True)
        c.redraw()
    #@+node:ekr.20160201072634.1: *5* c.cloneFindByPredicate (not a command)
    def cloneFindByPredicate(self,
        generator,     # The generator used to traverse the tree.
        predicate,     # A function of one argument p, returning True
                       # if p should be included in the results.
        failMsg=None,  # Failure message. Default is no message.
        flatten=False, # True: Put all matches at the top level.
        iconPath=None, # Full path to icon to attach to all matches.
        redraw=True,   # True: redraw the outline,
        undoType=None, # The undo name, shown in the Edit:Undo menu.
                       # The default is 'clone-find-predicate'
    ):
        '''
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
        '''
        c = self
        u, undoType = c.undoer, undoType or 'clone-find-predicate'
        clones, root, seen = [], None, set(),
        for p in generator():
            if predicate(p) and p.v not in seen:
                c.setCloneFindByPredicateIcon(iconPath, p)
                if flatten:
                    seen.add(p.v)
                else:
                    for p2 in p.self_and_subtree():
                        seen.add(p2.v)
                clones.append(p.copy())
        if clones:
            undoData = u.beforeInsertNode(c.p)
            root = c.createCloneFindPredicateRoot(flatten, undoType)
            for p in clones:
                clone = p.clone()
                clone.moveToLastChildOf(root)
            u.afterInsertNode(root, undoType, undoData, dirtyVnodeList=[])
            if redraw:
                c.selectPosition(root)
                c.setChanged(True)
                c.contractAllHeadlines()
                root.expand()
                c.redraw()
                c.selectPosition(root)
        elif failMsg:
            g.es_print(failMsg, color='red')
        return root
    #@+node:ekr.20160304054950.1: *6* c.setCloneFindByPredicateIcon
    def setCloneFindByPredicateIcon(self, iconPath, p):
        '''Attach an icon to p.v.u.'''
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
                p.v.u ['icons'] = aList
        elif iconPath:
            g.trace('bad icon path', iconPath)
    #@+node:ekr.20160201075438.1: *6* c.createCloneFindPredicateRoot
    def createCloneFindPredicateRoot(self, flatten, undoType):
        '''Create a root node for clone-find-predicate.'''
        c = self
        root = c.lastTopLevel().insertAfter()
        root.h = undoType + (' (flattened)' if flatten else '')
        return root
    #@+node:ekr.20161022121036.1: *5* c.cloneFindMarkedHelper
    def cloneFindMarkedHelper(self, flatten):
        '''Helper for clone-find-marked commands.'''
        c = self

        def isMarked(p):
            return p.isMarked()

        self.cloneFindByPredicate(
            generator = self.all_unique_positions,
            predicate = isMarked,
            failMsg = 'No marked nodes',
            flatten = flatten,
            redraw = True,
            undoType = 'clone-find-marked',
        )
        found = c.lastTopLevel()
        c.selectPosition(found)
        found.b = '# Found %s marked nodes' % found.numberOfChildren()
    #@+node:ekr.20031218072017.2861: *4* Edit Menu...
    #@+node:ekr.20031218072017.2862: *5* Edit top level
    #@+node:ekr.20031218072017.2090: *6* c.colorPanel
    @cmd('set-colors')
    def colorPanel(self, event=None):
        '''Open the color dialog.'''
        c = self; frame = c.frame
        if not frame.colorPanel:
            frame.colorPanel = g.app.gui.createColorPanel(c)
        frame.colorPanel.bringToFront()
    #@+node:ekr.20031218072017.2140: *6* c.executeScript & helpers
    @cmd('execute-script')
    def executeScript(self, event=None,
        args=None, p=None, script=None, useSelectedText=True,
        define_g=True, define_name='__main__',
        silent=False, namespace=None, raiseFlag=False,
    ):
        '''
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
        '''
        c, script1 = self, script
        if not script:
            if c.forceExecuteEntireBody:
                useSelectedText = False
            script = g.getScript(c, p or c.p, useSelectedText=useSelectedText)
        script_p = p or c.p
            # Only for error reporting below.
        self.redirectScriptOutput()
        try:
            oldLog = g.app.log
            log = c.frame.log
            g.app.log = log
            if script.strip():
                sys.path.insert(0, '.') # New in Leo 5.0
                sys.path.insert(0, c.frame.openDirectory) # per SegundoBob
                script += '\n' # Make sure we end the script properly.
                try:
                    # We *always* execute the script with p = c.p.
                    c.executeScriptHelper(args, define_g, define_name, namespace, script)
                except Exception:
                    if raiseFlag:
                        raise
                    else:
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
    #@+node:ekr.20120923063251.10651: *7* c.executeScriptHelper
    def executeScriptHelper(self, args, define_g, define_name, namespace, script):
        c = self
        if c.p:
            p = c.p.copy() # *Always* use c.p and pass c.p to script.
            c.setCurrentDirectoryFromContext(p)
        else:
            p = None
        # Do NOT define a subfunction here!
        #
        # On some, python 2.x versions it causes exec to cause a syntax error
        # Workarounds that avoid the syntax error hurt performance.
        # See http://stackoverflow.com/questions/4484872.

            # def g_input_wrapper(message, c=c):
                # return g.input_(message, c=c)

        d = {'c': c, 'g': g, 'input': g.input_, 'p': p} if define_g else {}
        if define_name: d['__name__'] = define_name
        d['script_args'] = args or []
        if namespace: d.update(namespace)
        # A kludge: reset c.inCommand here to handle the case where we *never* return.
        # (This can happen when there are multiple event loops.)
        # This does not prevent zombie windows if the script puts up a dialog...
        try:
            c.inCommand = False
            g.inScript = g.app.inScript = True
                # g.inScript is a synonym for g.app.inScript.
            if c.write_script_file:
                scriptFile = self.writeScriptFile(script)
                # pylint: disable=undefined-variable, no-member
                if g.isPython3:
                    exec(compile(script, scriptFile, 'exec'), d)
                else:
                    builtins.execfile(scriptFile, d)
            else:
                exec(script, d)
        finally:
            g.inScript = g.app.inScript = False
    #@+node:ekr.20031218072017.2143: *7* c.redirectScriptOutput
    def redirectScriptOutput(self):
        c = self
        # g.trace('original')
        if c.config.redirect_execute_script_output_to_log_pane:
            g.redirectStdout() # Redirect stdout
            g.redirectStderr() # Redirect stderr
    #@+node:ekr.20110522121957.18230: *7* c.setCurrentDirectoryFromContext
    def setCurrentDirectoryFromContext(self, p):
        trace = False and not g.unitTesting
        c = self
        aList = g.get_directives_dict_list(p)
        path = c.scanAtPathDirectives(aList)
        curDir = g.os_path_abspath(os.getcwd())
        # g.trace(p.h,'\npath  ',path,'\ncurDir',curDir)
        if path and path != curDir:
            if trace: g.trace('calling os.chdir(%s)' % (path))
            try:
                os.chdir(path)
            except Exception:
                pass
    #@+node:EKR.20040627100424: *7* c.unredirectScriptOutput
    def unredirectScriptOutput(self):
        c = self
        # g.trace('original')
        if c.exists and c.config.redirect_execute_script_output_to_log_pane:
            g.restoreStderr()
            g.restoreStdout()
    #@+node:ekr.20031218072017.2088: *6* c.fontPanel
    @cmd('set-font')
    def fontPanel(self, event=None):
        '''Open the font dialog.'''
        c = self; frame = c.frame
        if not frame.fontPanel:
            frame.fontPanel = g.app.gui.createFontPanel(c)
        frame.fontPanel.bringToFront()
    #@+node:EKR.20040612232221: *6* c.goToLineNumber & goToScriptLineNumber
    def goToLineNumber(self, n):
        """
        Go to line n (zero-based) of a script.
        Called from g.handleScriptException.
        """
        # import leo.commands.gotoCommands as gotoCommands
        c = self
        c.gotoCommands.find_file_line(n)

    def goToScriptLineNumber(self, n, p):
        """
        Go to line n (zero-based) of a script.
        Called from g.handleScriptException.
        """
        # import leo.commands.gotoCommands as gotoCommands
        c = self
        c.gotoCommands.find_script_line(n, p)
    #@+node:ekr.20031218072017.2086: *6* c.preferences
    @cmd('settings')
    def preferences(self, event=None):
        '''Handle the preferences command.'''
        c = self
        c.openLeoSettings()
    #@+node:ekr.20031218072017.2883: *6* c.show/hide/toggleInvisibles
    @cmd('hide-invisibles')
    def hideInvisibles(self, event=None):
        '''Hide invisible (whitespace) characters.'''
        c = self; c.showInvisiblesHelper(False)

    @cmd('show-invisibles')
    def showInvisibles(self, event=None):
        '''Show invisible (whitespace) characters.'''
        c = self; c.showInvisiblesHelper(True)

    @cmd('toggle-invisibles')
    def toggleShowInvisibles(self, event=None):
        '''Toggle showing of invisible (whitespace) characters.'''
        c = self; colorizer = c.frame.body.getColorizer()
        val = 0 if colorizer.showInvisibles else 1
        c.showInvisiblesHelper(val)

    def showInvisiblesHelper(self, val):
        c, frame = self, self.frame
        colorizer = frame.body.getColorizer()
        colorizer.showInvisibles = val
        colorizer.highlighter.showInvisibles = val
        # It is much easier to change the menu name here than in the menu updater.
        menu = frame.menu.getMenu("Edit")
        index = frame.menu.getMenuLabel(menu,
            'Hide Invisibles' if val else 'Show Invisibles')
        if index is None:
            if val: frame.menu.setMenuLabel(menu, "Show Invisibles", "Hide Invisibles")
            else: frame.menu.setMenuLabel(menu, "Hide Invisibles", "Show Invisibles")
        # 2016/03/09: Set the status bits here.
        # May fix #240: body won't scroll to end of text
        # https://github.com/leo-editor/leo-editor/issues/240
        if hasattr(frame.body, 'set_invisibles'):
            frame.body.set_invisibles(c)
        c.frame.body.recolor(c.p)
    #@+node:ekr.20070115135502: *6* c.writeScriptFile
    def writeScriptFile(self, script):
        trace = False and not g.unitTesting
        # Get the path to the file.
        c = self
        path = c.config.getString('script_file_path')
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
            path = c.os_path_finalize_join(*allParts)
        else:
            path = c.os_path_finalize_join(
                g.app.homeLeoDir, 'scriptFile.py')
        if trace: g.trace(path)
        # Write the file.
        try:
            if g.isPython3:
                # Use the default encoding.
                f = open(path, encoding='utf-8', mode='w')
            else:
                f = open(path, 'w')
            s = script
            if not g.isPython3: # 2010/08/27
                s = g.toEncodedString(s, reportErrors=True)
            f.write(s)
            f.close()
        except Exception:
            g.es_exception()
            g.es("Failed to write script to %s" % path)
            # g.es("Check your configuration of script_file_path, currently %s" %
                # c.config.getString('script_file_path'))
            path = None
        return path
    #@+node:ekr.20031218072017.2884: *5* Edit Body submenu
    #@+node:ekr.20031218072017.1827: *6* c.findMatchingBracket
    @cmd('match-brackets')
    @cmd('select-to-matching-bracket')
    def findMatchingBracket(self, event=None):
        '''Select the text between matching brackets.'''
        #@+others
        #@-others
        c, p = self, self.p
        if g.app.batchMode:
            c.notValidInBatchMode("Match Brackets")
            return
        language = g.getLanguageAtPosition(c, p)
        if language == 'perl':
            g.es('match-brackets not supported for', language)
        else:
            g.MatchBrackets(c, p, language).run()
    #@+node:ekr.20031218072017.1704: *6* c.convertAllBlanks
    @cmd('convert-all-blanks')
    def convertAllBlanks(self, event=None):
        '''Convert all blanks to tabs in the selected outline.'''
        c = self; u = c.undoer; undoType = 'Convert All Blanks'
        current = c.p
        if g.app.batchMode:
            c.notValidInBatchMode(undoType)
            return
        d = c.scanAllDirectives()
        tabWidth = d.get("tabwidth")
        count = 0; dirtyVnodeList = []
        u.beforeChangeGroup(current, undoType)
        for p in current.self_and_subtree():
            # g.trace(p.h,tabWidth)
            innerUndoData = u.beforeChangeNodeContents(p)
            if p == current:
                changed, dirtyVnodeList2 = c.convertBlanks(event)
                if changed:
                    count += 1
                    dirtyVnodeList.extend(dirtyVnodeList2)
            else:
                changed = False; result = []
                text = p.v.b
                lines = text.split('\n')
                for line in lines:
                    i, w = g.skip_leading_ws_with_indent(line, 0, tabWidth)
                    s = g.computeLeadingWhitespace(w, abs(tabWidth)) + line[i:] # use positive width.
                    if s != line: changed = True
                    result.append(s)
                if changed:
                    count += 1
                    dirtyVnodeList2 = p.setDirty()
                    dirtyVnodeList.extend(dirtyVnodeList2)
                    result = '\n'.join(result)
                    p.setBodyString(result)
                    u.afterChangeNodeContents(p, undoType, innerUndoData)
        u.afterChangeGroup(current, undoType, dirtyVnodeList=dirtyVnodeList)
        if not g.unitTesting:
            g.es("blanks converted to tabs in", count, "nodes")
                # Must come before c.redraw().
        if count > 0:
            c.redraw_after_icons_changed()
    #@+node:ekr.20031218072017.1705: *6* c.convertAllTabs
    @cmd('convert-all-tabs')
    def convertAllTabs(self, event=None):
        '''Convert all tabs to blanks in the selected outline.'''
        c = self; u = c.undoer; undoType = 'Convert All Tabs'
        current = c.p
        if g.app.batchMode:
            c.notValidInBatchMode(undoType)
            return
        theDict = c.scanAllDirectives()
        tabWidth = theDict.get("tabwidth")
        count = 0; dirtyVnodeList = []
        u.beforeChangeGroup(current, undoType)
        for p in current.self_and_subtree():
            undoData = u.beforeChangeNodeContents(p)
            if p == current:
                changed, dirtyVnodeList2 = self.convertTabs(event)
                if changed:
                    count += 1
                    dirtyVnodeList.extend(dirtyVnodeList2)
            else:
                result = []; changed = False
                text = p.v.b
                lines = text.split('\n')
                for line in lines:
                    i, w = g.skip_leading_ws_with_indent(line, 0, tabWidth)
                    s = g.computeLeadingWhitespace(w, -abs(tabWidth)) + line[i:] # use negative width.
                    if s != line: changed = True
                    result.append(s)
                if changed:
                    count += 1
                    dirtyVnodeList2 = p.setDirty()
                    dirtyVnodeList.extend(dirtyVnodeList2)
                    result = '\n'.join(result)
                    p.setBodyString(result)
                    u.afterChangeNodeContents(p, undoType, undoData)
        u.afterChangeGroup(current, undoType, dirtyVnodeList=dirtyVnodeList)
        if not g.unitTesting:
            g.es("tabs converted to blanks in", count, "nodes")
        if count > 0:
            c.redraw_after_icons_changed()
    #@+node:ekr.20031218072017.1821: *6* c.convertBlanks
    @cmd('convert-blanks')
    def convertBlanks(self, event=None):
        '''Convert all blanks to tabs in the selected node.'''
        c = self; changed = False; dirtyVnodeList = []
        head, lines, tail, oldSel, oldYview = c.getBodyLines(expandSelection=True)
        # Use the relative @tabwidth, not the global one.
        theDict = c.scanAllDirectives()
        tabWidth = theDict.get("tabwidth")
        if tabWidth:
            result = []
            for line in lines:
                s = g.optimizeLeadingWhitespace(line, abs(tabWidth)) # Use positive width.
                if s != line: changed = True
                result.append(s)
            if changed:
                undoType = 'Convert Blanks'
                result = ''.join(result)
                oldSel = None
                dirtyVnodeList = c.updateBodyPane(head, result, tail, undoType, oldSel, oldYview) # Handles undo
        return changed, dirtyVnodeList
    #@+node:ekr.20031218072017.1822: *6* c.convertTabs
    @cmd('convert-tabs')
    def convertTabs(self, event=None):
        '''Convert all tabs to blanks in the selected node.'''
        c = self; changed = False; dirtyVnodeList = []
        head, lines, tail, oldSel, oldYview = self.getBodyLines(expandSelection=True)
        # Use the relative @tabwidth, not the global one.
        theDict = c.scanAllDirectives()
        tabWidth = theDict.get("tabwidth")
        if tabWidth:
            result = []
            for line in lines:
                i, w = g.skip_leading_ws_with_indent(line, 0, tabWidth)
                s = g.computeLeadingWhitespace(w, -abs(tabWidth)) + line[i:] # use negative width.
                if s != line: changed = True
                result.append(s)
            if changed:
                undoType = 'Convert Tabs'
                result = ''.join(result)
                oldSel = None
                dirtyVnodeList = c.updateBodyPane(head, result, tail, undoType, oldSel, oldYview) # Handles undo
        return changed, dirtyVnodeList
    #@+node:ekr.20031218072017.1823: *6* c.createLastChildNode
    def createLastChildNode(self, parent, headline, body):
        '''A helper function for the three extract commands.'''
        c = self
        if body:
            body = body.rstrip()
        if not body:
            body = ""
        p = parent.insertAsLastChild()
        p.initHeadString(headline)
        p.setBodyString(body)
        p.setDirty()
        c.validateOutline()
        return p
    #@+node:ekr.20031218072017.1824: *6* c.dedentBody (unindent-region)
    @cmd('unindent-region')
    def dedentBody(self, event=None):
        '''Remove one tab's worth of indentation from all presently selected lines.'''
        c, undoType = self, 'Unindent'
        w = c.frame.body.wrapper
        sel_1, sel_2 = w.getSelectionRange()
        ins = w.getInsertPoint()
        tab_width = c.getTabWidth(c.p)
        head, lines, tail, oldSel, oldYview = self.getBodyLines()
        changed, result = False, []
        for line in lines:
            i, width = g.skip_leading_ws_with_indent(line, 0, tab_width)
            s = g.computeLeadingWhitespace(width - abs(tab_width), tab_width) + line[i:]
            if s != line: changed = True
            result.append(s)
        if changed:
            result = ''.join(result)
            # Leo 5.6: preserve insert point.
            preserveSel = sel_1 == sel_2
            if preserveSel:
                ins = max(0, ins - abs(tab_width))
                oldSel = ins, ins
            c.updateBodyPane(head, result, tail, undoType, oldSel, oldYview, preserveSel)
    #@+node:ekr.20110530124245.18238: *6* c.extract...
    #@+node:ekr.20110530124245.18239: *7* c.extract & helpers
    @cmd('extract')
    def extract(self, event=None):
        '''
        Create child node from the selected body text.

        1. If the selection starts with a section reference, the section
           name become the child's headline. All following lines become
           the child's body text. The section reference line remains in
           the original body text.

        2. If the selection looks like a Python class or definition line,
           the class/function/method name becomes the child's headline and
           all selected lines become the child's body text.

        3. Otherwise, the first line becomes the child's headline, and all
           selected lines become the child's body text.
        '''
        c, current, u, undoType = self, self.p, self.undoer, 'Extract'
        head, lines, tail, oldSel, oldYview = self.getBodyLines()
        if not lines:
            return # Nothing selected.
        # Remove leading whitespace.
        junk, ws = g.skip_leading_ws_with_indent(lines[0], 0, c.tab_width)
        lines = [g.removeLeadingWhitespace(s, ws, c.tab_width) for s in lines]
        h = lines[0].strip()
        ref_h = c.extractRef(h).strip()
        def_h = c.extractDef(h).strip()
        if ref_h:
            # h,b,middle = ref_h,lines[1:],lines[0]
            # 2012/02/27: Change suggested by vitalije (vitalijem@gmail.com)
            h, b, middle = ref_h, lines[1:], ' ' * ws + lines[0]
        elif def_h:
            h, b, middle = def_h, lines, ''
        else:
            h, b, middle = lines[0].strip(), lines[1:], ''
        u.beforeChangeGroup(current, undoType)
        undoData = u.beforeInsertNode(current)
        p = c.createLastChildNode(current, h, ''.join(b))
        u.afterInsertNode(p, undoType, undoData)
        c.updateBodyPane(head, middle, tail,
            undoType=undoType, oldSel=None, oldYview=oldYview)
        u.afterChangeGroup(current, undoType=undoType)
        p.parent().expand()
        c.redraw(p.parent()) # A bit more convenient than p.
        c.bodyWantsFocus()
    # Compatibility

    extractSection = extract
    extractPythonMethod = extract
    #@+node:ekr.20110530124245.18241: *8* c.extractDef
    def extractDef(self, s):
        '''Return the defined function/method name if
        s looks like Python def or class line.
        '''
        s = s.strip()
        for tag in ('def', 'class'):
            if s.startswith(tag):
                i = g.skip_ws(s, len(tag))
                j = g.skip_id(s, i, chars='_')
                if j > i:
                    name = s[i: j]
                    if tag == 'class':
                        return name
                    else:
                        k = g.skip_ws(s, j)
                        if g.match(s, k, '('):
                            return name
        return ''
    #@+node:ekr.20110530124245.18242: *8* c.extractRef
    def extractRef(self, s):
        '''Return s if it starts with a section name.'''
        i = s.find('<<')
        j = s.find('>>')
        if -1 < i < j:
            return s
        i = s.find('@<')
        j = s.find('@>')
        if -1 < i < j:
            return s
        return ''
    #@+node:ekr.20031218072017.1710: *7* c.extractSectionNames
    @cmd('extract-names')
    def extractSectionNames(self, event=None):
        '''Create child nodes for every section reference in the selected text.
        The headline of each new child node is the section reference.
        The body of each child node is empty.'''
        c = self; u = c.undoer; undoType = 'Extract Section Names'
        body = c.frame.body; current = c.p
        head, lines, tail, oldSel, oldYview = self.getBodyLines()
        if not lines:
            g.warning('No lines selected')
            return
        u.beforeChangeGroup(current, undoType)
        found = False
        for s in lines:
            name = c.findSectionName(s)
            if name:
                undoData = u.beforeInsertNode(current)
                p = self.createLastChildNode(current, name, None)
                u.afterInsertNode(p, undoType, undoData)
                found = True
        c.validateOutline()
        if found:
            u.afterChangeGroup(current, undoType)
            c.redraw(p)
        else:
            g.warning("selected text should contain section names")
        # Restore the selection.
        i, j = oldSel
        w = body.wrapper
        if w:
            w.setSelectionRange(i, j)
            w.setFocus()
    #@+node:ekr.20031218072017.1711: *8* c.findSectionName
    def findSectionName(self, s):
        head1 = s.find("<<")
        if head1 > -1:
            head2 = s.find(">>", head1)
        else:
            head1 = s.find("@<")
            if head1 > -1:
                head2 = s.find("@>", head1)
        if head1 == -1 or head2 == -1 or head1 > head2:
            name = None
        else:
            name = s[head1: head2 + 2]
        return name
    #@+node:ekr.20031218072017.1829: *6* c.getBodyLines
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
            lines = g.splitLines(s) # Retain the newlines of each line.
        else:
            # Note: lines is the entire line containing the insert point if no selection.
            head, s, tail = body.getSelectionLines()
            lines = g.splitLines(s) # Retain the newlines of each line.
            # Expand the selection.
            i = len(head)
            j = max(i, len(head) + len(s) - 1)
            oldSel = i, j
        return head, lines, tail, oldSel, oldVview # string,list,string,tuple.
    #@+node:ekr.20031218072017.1830: *6* c.indentBody (indent-region)
    @cmd('indent-region')
    def indentBody(self, event=None):
        '''
        The indent-region command indents each line of the selected body text,
        or each line of a node if there is no selected text. The @tabwidth directive
        in effect determines amount of indentation. (not yet) A numeric argument
        specifies the column to indent to.
        '''
        c, undoType = self, 'Indent Region'
        w = c.frame.body.wrapper
        sel_1, sel_2 = w.getSelectionRange()
        ins = w.getInsertPoint()
        tab_width = c.getTabWidth(c.p)
        head, lines, tail, oldSel, oldYview = self.getBodyLines()
        changed, result = False, []
        for line in lines:
            i, width = g.skip_leading_ws_with_indent(line, 0, tab_width)
            s = g.computeLeadingWhitespace(width + abs(tab_width), tab_width) + line[i:]
            if s != line: changed = True
            result.append(s)
        if changed:
            # Leo 5.6: preserve insert point.
            preserveSel = sel_1 == sel_2
            if preserveSel:
                ins += tab_width
                oldSel = ins, ins
            result = ''.join(result)
            c.updateBodyPane(head, result, tail, undoType, oldSel, oldYview, preserveSel)
    #@+node:ekr.20050312114529: *6* c.insert/removeComments
    #@+node:ekr.20131103054650.16535: *7* c.hasAmbiguousLangauge
    def hasAmbiguousLanguage(self, p):
        '''Return True if p.b contains different @language directives.'''
        # c = self
        languages, tag = set(), '@language'
        for s in g.splitLines(p.b):
            if g.match_word(s, 0, tag):
                i = g.skip_ws(s, len(tag))
                j = g.skip_id(s, i)
                word = s[i: j]
                languages.add(word)
        return len(list(languages)) > 1
    #@+node:ekr.20131103054650.16536: *7* c.getLanguageAtCursor
    def getLanguageAtCursor(self, p, language):
        '''
        Return the language in effect at the present insert point.
        Use the language argument as a default if no @language directive seen.
        '''
        c = self
        tag = '@language'
        w = c.frame.body.wrapper
        ins = w.getInsertPoint()
        n = 0
        for s in g.splitLines(p.b):
            # g.trace(ins,n,repr(s))
            if g.match_word(s, 0, tag):
                i = g.skip_ws(s, len(tag))
                j = g.skip_id(s, i)
                language = s[i: j]
            if n <= ins < n + len(s):
                break
            else:
                n += len(s)
        # g.trace(ins,n,language)
        return language
    #@+node:ekr.20050312114529.1: *7* c.addComments
    @cmd('add-comments')
    def addComments(self, event=None):
        #@+<< addComments docstring >>
        #@+node:ekr.20111115111842.9789: *8* << addComments docstring >>
        #@@pagewidth 50
        '''
        Converts all selected lines to comment lines using
        the comment delimiters given by the applicable @language directive.

        Inserts single-line comments if possible; inserts
        block comments for languages like html that lack
        single-line comments.

        @bool indent_added_comments

        If True (the default), inserts opening comment
        delimiters just before the first non-whitespace
        character of each line. Otherwise, inserts opening
        comment delimiters at the start of each line.

        *See also*: delete-comments.
        '''
        #@-<< addComments docstring >>
        c = self; p = c.p
        head, lines, tail, oldSel, oldYview = self.getBodyLines()
        if not lines:
            g.warning('no text selected')
            return
        # The default language in effect at p.
        language = c.frame.body.colorizer.scanLanguageDirectives(p)
        if c.hasAmbiguousLanguage(p):
            language = c.getLanguageAtCursor(p, language)
        # g.trace(language,p.h)
        d1, d2, d3 = g.set_delims_from_language(language)
        d2 = d2 or ''; d3 = d3 or ''
        if d1:
            openDelim, closeDelim = d1 + ' ', ''
        else:
            openDelim, closeDelim = d2 + ' ', ' ' + d3
        # Comment out non-blank lines.
        indent = c.config.getBool('indent_added_comments', default=True)
        result = []
        for line in lines:
            if line.strip():
                i = g.skip_ws(line, 0)
                if indent:
                    result.append(line[0: i] + openDelim + line[i:].replace('\n', '') + closeDelim + '\n')
                else:
                    result.append(openDelim + line.replace('\n', '') + closeDelim + '\n')
            else:
                result.append(line)
        result = ''.join(result)
        c.updateBodyPane(head, result, tail, undoType='Add Comments', oldSel=None, oldYview=oldYview)
    #@+node:ekr.20050312114529.2: *7* c.deleteComments
    @cmd('delete-comments')
    def deleteComments(self, event=None):
        #@+<< deleteComments docstring >>
        #@+node:ekr.20111115111842.9790: *8* << deleteComments docstring >>
        #@@pagewidth 50
        '''
        Removes one level of comment delimiters from all
        selected lines.  The applicable @language directive
        determines the comment delimiters to be removed.

        Removes single-line comments if possible; removes
        block comments for languages like html that lack
        single-line comments.

        *See also*: add-comments.
        '''
        #@-<< deleteComments docstring >>
        c = self; p = c.p
        head, lines, tail, oldSel, oldYview = self.getBodyLines()
        result = []
        if not lines:
            g.warning('no text selected')
            return
        # The default language in effect at p.
        language = c.frame.body.colorizer.scanLanguageDirectives(p)
        if c.hasAmbiguousLanguage(p):
            language = c.getLanguageAtCursor(p, language)
        d1, d2, d3 = g.set_delims_from_language(language)
        if d1:
            # Remove the single-line comment delim in front of each line
            d1b = d1 + ' '
            n1, n1b = len(d1), len(d1b)
            for s in lines:
                i = g.skip_ws(s, 0)
                if g.match(s, i, d1b):
                    result.append(s[: i] + s[i + n1b:])
                elif g.match(s, i, d1):
                    result.append(s[: i] + s[i + n1:])
                else:
                    result.append(s)
        else:
            # Remove the block comment delimiters from each line.
            n2, n3 = len(d2), len(d3)
            for s in lines:
                i = g.skip_ws(s, 0)
                j = s.find(d3, i + n2)
                if g.match(s, i, d2) and j > -1:
                    first = i + n2
                    if g.match(s, first, ' '): first += 1
                    last = j
                    if g.match(s, last - 1, ' '): last -= 1
                    result.append(s[: i] + s[first: last] + s[j + n3:])
                else:
                    result.append(s)
        result = ''.join(result)
        c.updateBodyPane(head, result, tail, undoType='Delete Comments', oldSel=None, oldYview=oldYview)
    #@+node:ekr.20031218072017.1831: *6* c.insertBodyTime, helpers and tests
    @cmd('insert-body-time')
    def insertBodyTime(self, event=None):
        '''Insert a time/date stamp at the cursor.'''
        c = self; undoType = 'Insert Body Time'
        w = c.frame.body.wrapper
        if g.app.batchMode:
            c.notValidInBatchMode(undoType)
            return
        oldSel = w.getSelectionRange()
        w.deleteTextSelection()
        s = self.getTime(body=True)
        i = w.getInsertPoint()
        w.insert(i, s)
        c.frame.body.onBodyChanged(undoType, oldSel=oldSel)
    #@+node:ekr.20031218072017.1832: *7* c.getTime
    def getTime(self, body=True):
        c = self
        default_format = "%m/%d/%Y %H:%M:%S" # E.g., 1/30/2003 8:31:55
        # Try to get the format string from settings.
        if body:
            format = c.config.getString("body_time_format_string")
            gmt = c.config.getBool("body_gmt_time")
        else:
            format = c.config.getString("headline_time_format_string")
            gmt = c.config.getBool("headline_gmt_time")
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
            g.es_exception() # Probably a bad format string in leoSettings.leo.
            s = time.strftime(default_format, time.gmtime())
        return s
    #@+node:ekr.20131002055813.19033: *6* c.reformatBody
    def reformatBody(self, event=None):
        '''Reformat all paragraphs in the body.'''
        c, p = self, self.p
        undoType = 'reformat-body'
        w = c.frame.body.wrapper
        c.undoer.beforeChangeGroup(p, undoType)
        w.setInsertPoint(0)
        while 1:
            progress = w.getInsertPoint()
            c.reformatParagraph(event, undoType=undoType)
            ins = w.getInsertPoint()
            s = w.getAllText()
            w.setInsertPoint(ins)
            if ins <= progress or ins >= len(s):
                break
        c.undoer.afterChangeGroup(p, undoType)
    #@+node:ekr.20101118113953.5839: *6* c.reformatParagraph & helpers
    @cmd('reformat-paragraph')
    def reformatParagraph(self, event=None, undoType='Reformat Paragraph'):
        '''
        Reformat a text paragraph

        Wraps the concatenated text to present page width setting. Leading tabs are
        sized to present tab width setting. First and second line of original text is
        used to determine leading whitespace in reformatted text. Hanging indentation
        is honored.

        Paragraph is bound by start of body, end of body and blank lines. Paragraph is
        selected by position of current insertion cursor.
        '''
        c = self
        body = c.frame.body
        w = body.wrapper
        if g.app.batchMode:
            c.notValidInBatchMode("reformat-paragraph")
            return
        if w.hasSelection():
            i, j = w.getSelectionRange()
            w.setInsertPoint(i)
        oldSel, oldYview, original, pageWidth, tabWidth = c.rp_get_args()
        head, lines, tail = c.findBoundParagraph()
        if lines:
            indents, leading_ws = c.rp_get_leading_ws(lines, tabWidth)
            result = c.rp_wrap_all_lines(indents, leading_ws, lines, pageWidth)
            c.rp_reformat(head, oldSel, oldYview, original, result, tail, undoType)
    #@+node:ekr.20031218072017.1825: *7* c.findBoundParagraph & helpers
    def findBoundParagraph(self, event=None):
        '''Return the lines of a paragraph to be reformatted.'''
        c = self
        trace = False and not g.unitTesting
        head, ins, tail = c.frame.body.getInsertLines()
        head_lines = g.splitLines(head)
        tail_lines = g.splitLines(tail)
        if trace:
            g.trace("head_lines:\n%s" % ''.join(head_lines))
            g.trace("ins: ", ins)
            g.trace("tail_lines:\n%s" % ''.join(tail_lines))
            g.trace('*****')
        result = []
        insert_lines = g.splitLines(ins)
        para_lines = insert_lines + tail_lines
        # If the present line doesn't start a paragraph,
        # scan backward, adding trailing lines of head to ins.
        if insert_lines and not c.startsParagraph(insert_lines[0]):
            n = 0 # number of moved lines.
            for i, s in enumerate(reversed(head_lines)):
                if c.endsParagraph(s) or c.singleLineParagraph(s):
                    break
                elif c.startsParagraph(s):
                    n += 1
                    break
                else: n += 1
            if n > 0:
                para_lines = head_lines[-n:] + para_lines
                head_lines = head_lines[: -n]
        ended, started = False, False
        for i, s in enumerate(para_lines):
            if trace: g.trace(
                # 'i: %s started: %5s single: %5s starts: %5s: ends: %5s %s' % (
                i, started,
                c.singleLineParagraph(s),
                c.startsParagraph(s),
                c.endsParagraph(s), repr(s))
            if started:
                if c.endsParagraph(s) or c.startsParagraph(s):
                    ended = True
                    break
                else:
                    result.append(s)
            elif s.strip():
                result.append(s)
                started = True
                if c.endsParagraph(s) or c.singleLineParagraph(s):
                    i += 1
                    ended = True
                    break
            else:
                head_lines.append(s)
        if started:
            head = g.joinLines(head_lines)
            tail_lines = para_lines[i:] if ended else []
            tail = g.joinLines(tail_lines)
            return head, result, tail # string, list, string
        else:
            if trace: g.trace('no paragraph')
            return None, None, None
    #@+node:ekr.20131102044158.16572: *8* c.endsParagraph & c.singleLineParagraph
    def endsParagraph(self, s):
        '''Return True if s is a blank line.'''
        return not s.strip()

    def singleLineParagraph(self, s):
        '''Return True if s is a single-line paragraph.'''
        return s.startswith('@') or s.strip() in ('"""', "'''")
    #@+node:ekr.20131102044158.16570: *8* c.startsParagraph
    def startsParagraph(self, s):
        '''Return True if line s starts a paragraph.'''
        trace = False and not g.unitTesting
        if not s.strip():
            val = False
        elif s.strip() in ('"""', "'''"):
            val = True
        elif s[0].isdigit():
            i = 0
            while i < len(s) and s[i].isdigit():
                i += 1
            val = g.match(s, i, ')') or g.match(s, i, '.')
        elif s[0].isalpha():
            # Careful: single characters only.
            # This could cause problems in some situations.
            val = (
                (g.match(s, 1, ')') or g.match(s, 1, '.')) and
                (len(s) < 2 or s[2] in (' \t\n')))
        else:
            val = s.startswith('@') or s.startswith('-')
        if trace: g.trace(val, repr(s))
        return val
    #@+node:ekr.20101118113953.5840: *7* c.rp_get_args
    def rp_get_args(self):
        '''Compute and return oldSel,oldYview,original,pageWidth,tabWidth.'''
        c = self
        body = c.frame.body
        w = body.wrapper
        d = c.scanAllDirectives()
        # g.trace(c.editCommands.fillColumn)
        if c.editCommands.fillColumn > 0:
            pageWidth = c.editCommands.fillColumn
        else:
            pageWidth = d.get("pagewidth")
        tabWidth = d.get("tabwidth")
        original = w.getAllText()
        oldSel = w.getSelectionRange()
        oldYview = w.getYScrollPosition()
        return oldSel, oldYview, original, pageWidth, tabWidth
    #@+node:ekr.20101118113953.5841: *7* c.rp_get_leading_ws
    def rp_get_leading_ws(self, lines, tabWidth):
        '''Compute and return indents and leading_ws.'''
        # c = self
        indents = [0, 0]
        leading_ws = ["", ""]
        for i in (0, 1):
            if i < len(lines):
                # Use the original, non-optimized leading whitespace.
                leading_ws[i] = ws = g.get_leading_ws(lines[i])
                indents[i] = g.computeWidth(ws, tabWidth)
        indents[1] = max(indents)
        if len(lines) == 1:
            leading_ws[1] = leading_ws[0]
        return indents, leading_ws
    #@+node:ekr.20101118113953.5842: *7* c.rp_reformat
    def rp_reformat(self, head, oldSel, oldYview, original, result, tail, undoType):
        '''Reformat the body and update the selection.'''
        c = self; body = c.frame.body; w = body.wrapper
        # This destroys recoloring.
        junk, ins = body.setSelectionAreas(head, result, tail)
        changed = original != head + result + tail
        if changed:
            s = w.getAllText()
            # Fix an annoying glitch when there is no
            # newline following the reformatted paragraph.
            if not tail and ins < len(s): ins += 1
            # 2010/11/16: stay in the paragraph.
            body.onBodyChanged(undoType, oldSel=oldSel, oldYview=oldYview)
        else:
            # Advance to the next paragraph.
            s = w.getAllText()
            ins += 1 # Move past the selection.
            while ins < len(s):
                i, j = g.getLine(s, ins)
                line = s[i: j]
                # 2010/11/16: it's annoying, imo, to treat @ lines differently.
                if line.isspace():
                    ins = j + 1
                else:
                    ins = i
                    break
            # setSelectionAreas has destroyed the coloring.
            c.recolor()
        w.setSelectionRange(ins, ins, insert=ins)
        # 2011/10/26: Calling see does more harm than good.
            # w.see(ins)
        # Make sure we never scroll horizontally.
        w.setXScrollPosition(0)
    #@+node:ekr.20101118113953.5843: *7* c.rp_wrap_all_lines
    def rp_wrap_all_lines(self, indents, leading_ws, lines, pageWidth):
        '''Compute the result of wrapping all lines.'''
        c = self
        trailingNL = lines and lines[-1].endswith('\n')
        lines = [z[: -1] if z.endswith('\n') else z for z in lines]
        if lines: # Bug fix: 2013/12/22.
            s = lines[0]
            if c.startsParagraph(s):
                # Adjust indents[1]
                # Similar to code in c.startsParagraph(s)
                i = 0
                if s[0].isdigit():
                    while i < len(s) and s[i].isdigit():
                        i += 1
                    if g.match(s, i, ')') or g.match(s, i, '.'):
                        i += 1
                elif s[0].isalpha():
                    if g.match(s, 1, ')') or g.match(s, 1, '.'):
                        i = 2
                elif s[0] == '-':
                    i = 1
                # Never decrease indentation.
                i = g.skip_ws(s, i + 1)
                if i > indents[1]:
                    indents[1] = i
                    leading_ws[1] = ' ' * i
        # Wrap the lines, decreasing the page width by indent.
        result = g.wrap_lines(lines,
            pageWidth - indents[1],
            pageWidth - indents[0])
        # prefix with the leading whitespace, if any
        paddedResult = []
        paddedResult.append(leading_ws[0] + result[0])
        for line in result[1:]:
            paddedResult.append(leading_ws[1] + line)
        # Convert the result to a string.
        result = '\n'.join(paddedResult)
        if trailingNL: result = result + '\n'
        return result
    #@+node:ekr.20150223082820.5: *6* c.unformatParagraph & helper
    @cmd('unformat-paragraph')
    def unformatParagraph(self, event=None, undoType='Unformat Paragraph'):
        '''
        Unformat a text paragraph. Removes all extra whitespace in a paragraph.

        Paragraph is bound by start of body, end of body and blank lines. Paragraph is
        selected by position of current insertion cursor.
        '''
        c = self
        body = c.frame.body
        w = body.wrapper
        if g.app.batchMode:
            c.notValidInBatchMode("unformat-paragraph")
            return
        if w.hasSelection():
            i, j = w.getSelectionRange()
            w.setInsertPoint(i)
        oldSel, oldYview, original, pageWidth, tabWidth = c.rp_get_args()
        head, lines, tail = c.findBoundParagraph()
        if lines:
            result = ' '.join([z.strip() for z in lines]) + '\n'
            c.unreformat(head, oldSel, oldYview, original, result, tail, undoType)
    #@+node:ekr.20150223082820.7: *7* c.unreformat
    def unreformat(self, head, oldSel, oldYview, original, result, tail, undoType):
        '''unformat the body and update the selection.'''
        c = self; body = c.frame.body; w = body.wrapper
        # This destroys recoloring.
        junk, ins = body.setSelectionAreas(head, result, tail)
        changed = original != head + result + tail
        if changed:
            body.onBodyChanged(undoType, oldSel=oldSel, oldYview=oldYview)
        # Advance to the next paragraph.
        s = w.getAllText()
        ins += 1 # Move past the selection.
        while ins < len(s):
            i, j = g.getLine(s, ins)
            line = s[i: j]
            if line.isspace():
                ins = j + 1
            else:
                ins = i
                break
        # setSelectionAreas has destroyed the coloring.
        c.recolor()
        w.setSelectionRange(ins, ins, insert=ins)
        # More useful than for reformat-paragraph.
        w.see(ins)
        # Make sure we never scroll horizontally.
        w.setXScrollPosition(0)
    #@+node:ekr.20031218072017.1838: *6* c.updateBodyPane (handles changeNodeContents)
    def updateBodyPane(self, head, middle, tail, undoType, oldSel, oldYview, preserveSel=False):
        '''Handle changed text in the body pane.'''
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
        c.setChanged(True)
        if p.isDirty():
            dirtyVnodeList = []
        else:
            dirtyVnodeList = p.setDirty()
        c.redraw_after_icons_changed()
        # Scroll as necessary.
        if oldYview:
            body.wrapper.setYScrollPosition(oldYview)
        else:
            body.wrapper.seeInsertPoint()
        body.wrapper.setFocus()
        c.recolor()
        return dirtyVnodeList
    #@+node:tbnorth.20170111151835.1: *6* justify-toggle-auto
    @cmd("justify-toggle-auto")
    def justify_toggle_auto(self, event=None):
        c = self
        if c.editCommands.autojustify == 0:
            c.editCommands.autojustify = abs(c.config.getInt("autojustify") or 0)
            if c.editCommands.autojustify:
                g.es("Autojustify on, @int autojustify == %s" %
                c.editCommands.autojustify)
            else:
                g.es("Set @int autojustify in @settings")
        else:
            c.editCommands.autojustify = 0
            g.es("Autojustify off")
    #@+node:ekr.20031218072017.2885: *5* Edit Headline submenu
    #@+node:ekr.20031218072017.2886: *6* c.editHeadline
    @cmd('edit-headline')
    def editHeadline(self, event=None):
        '''Begin editing the headline of the selected node.'''
        c = self; k = c.k; tree = c.frame.tree
        if g.app.batchMode:
            c.notValidInBatchMode("Edit Headline")
            return
        e, wrapper = tree.editLabel(c.p)
        if k:
            # k.setDefaultInputState()
            k.setEditingState()
            k.showStateAndMode(w=wrapper)
        return e, wrapper
            # Neither of these is used by any caller.
    #@+node:ekr.20031218072017.2290: *6* c.toggleAngleBrackets
    @cmd('toggle-angle-brackets')
    def toggleAngleBrackets(self, event=None):
        '''Add or remove double angle brackets from the headline of the selected node.'''
        c = self; p = c.p
        if g.app.batchMode:
            c.notValidInBatchMode("Toggle Angle Brackets")
            return
        c.endEditing()
        s = p.h.strip()
        if (s[0: 2] == "<<" or
            s[-2:] == ">>" # Must be on separate line.
        ):
            if s[0: 2] == "<<": s = s[2:]
            if s[-2:] == ">>": s = s[: -2]
            s = s.strip()
        else:
            s = g.angleBrackets(' ' + s + ' ')
        p.setHeadString(s)
        c.redrawAndEdit(p, selectAll=True)
    #@+node:ekr.20031218072017.2893: *5* c.notValidInBatchMode
    def notValidInBatchMode(self, commandName):
        g.es('the', commandName, "command is not valid in batch mode")
    #@+node:ekr.20031218072017.2819: *4* File Menu
    #@+node:ekr.20031218072017.2820: *5* c.top level (file menu)
    #@+node:ekr.20031218072017.2833: *6* c.close
    @cmd('close-window')
    def close(self, event=None, new_c=None):
        '''Close the Leo window, prompting to save it if it has been changed.'''
        g.app.closeLeoWindow(self.frame, new_c=new_c)
    #@+node:ekr.20110530124245.18245: *6* c.importAnyFile & helper
    @cmd('import-file')
    def importAnyFile(self, event=None):
        '''Import one or more files.'''
        c = self
        ic = c.importCommands
        types = [
            ("All files", "*"),
            ("C/C++ files", "*.c"),
            ("C/C++ files", "*.cpp"),
            ("C/C++ files", "*.h"),
            ("C/C++ files", "*.hpp"),
            ("FreeMind files", "*.mm.html"),
            ("Java files", "*.java"),
            ("JavaScript files", "*.js"),
            # ("JSON files", "*.json"),
            ("Mindjet files", "*.csv"),
            ("MORE files", "*.MORE"),
            ("Lua files", "*.lua"),
            ("Pascal files", "*.pas"),
            ("Python files", "*.py"),
            ("Tabbed files", "*.txt"),
        ]
        names = g.app.gui.runOpenFileDialog(c,
            title="Import File",
            filetypes=types,
            defaultextension=".py",
            multiple=True)
        c.bringToFront()
        if names:
            g.chdir(names[0])
        else:
            names = []
        if not names:
            if g.unitTesting:
                # a kludge for unit testing.
                c.init_error_dialogs()
                c.raise_error_dialogs(kind='read')
            return
        # New in Leo 4.9: choose the type of import based on the extension.
        c.init_error_dialogs()
        derived = [z for z in names if c.looksLikeDerivedFile(z)]
        others = [z for z in names if z not in derived]
        if derived:
            ic.importDerivedFiles(parent=c.p, paths=derived)
        for fn in others:
            junk, ext = g.os_path_splitext(fn)
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
            elif ext == 'txt':
                ic.importFlattenedOutline([fn])
            else:
                # Make *sure* that parent.b is empty.
                last = c.lastTopLevel()
                parent = last.insertAfter()
                parent.v.h = 'Imported Files'
                ic.importFilesCommand(
                    files=[fn],
                    parent=parent,
                    treeType='@auto', # was '@clean'
                        # Experimental: attempt to use permissive section ref logic.
                )
        c.raise_error_dialogs(kind='read')

    # Compatibility: used by unit tests.
    importAtFile = importAnyFile
    importAtRoot = importAnyFile
    importCWEBFiles = importAnyFile
    importDerivedFile = importAnyFile
    importFlattenedOutline = importAnyFile
    importMOREFiles = importAnyFile
    importNowebFiles = importAnyFile
    importTabFiles = importAnyFile
    #@+node:ekr.20110530124245.18248: *7* c.looksLikeDerivedFile
    def looksLikeDerivedFile(self, fn):
        '''Return True if fn names a file that looks like an
        external file written by Leo.'''
        # c = self
        try:
            f = open(fn, 'r')
        except IOError:
            return False
        try:
            s = f.read()
        except Exception:
            s = ''
        finally:
            f.close()
        val = s.find('@+leo-ver=') > -1
        return val
    #@+node:ekr.20031218072017.1623: *6* c.new
    @cmd('new')
    def new(self, event=None, gui=None):
        '''Create a new Leo window.'''
        lm = g.app.loadManager
        # Clean out the update queue so it won't interfere with the new window.
        self.outerUpdate()
        # Send all log messages to the new frame.
        g.app.setLog(None)
        g.app.lockLog()
        c = g.app.newCommander(fileName=None, gui=gui)
        frame = c.frame
        g.app.unlockLog()
        frame.setInitialWindowGeometry()
        frame.deiconify()
        frame.lift()
        frame.resizePanesToRatio(frame.ratio, frame.secondary_ratio)
            # Resize the _new_ frame.
        c.frame.createFirstTreeNode()
        lm.createMenu(c)
        lm.finishOpen(c)
        g.app.writeWaitingLog(c)
        g.doHook("new", old_c=self, c=c, new_c=c)
        c.setLog()
        c.setChanged(False) # Fix #387
        c.redraw()
        return c # For unit tests and scripts.
    #@+node:ekr.20031218072017.2821: *6* c.open & helper
    @cmd('open-outline')
    def open(self, event=None):
        '''Open a Leo window containing the contents of a .leo file.'''
        c = self
        #@+<< Set closeFlag if the only open window is empty >>
        #@+node:ekr.20031218072017.2822: *7* << Set closeFlag if the only open window is empty >>
        #@+at
        # If this is the only open window was opened when the app started, and
        # the window has never been written to or saved, then we will
        # automatically close that window if this open command completes
        # successfully.
        #@@c
        closeFlag = (
            c.frame.startupWindow and # The window was open on startup
            not c.changed and not c.frame.saved and # The window has never been changed
            g.app.numberOfUntitledWindows == 1) # Only one untitled window has ever been opened
        #@-<< Set closeFlag if the only open window is empty >>
        table = [
            # 2010/10/09: Fix an interface blunder. Show all files by default.
            ("All files", "*"),
            ("Leo files", "*.leo"),
            ("Python files", "*.py"),]
        fileName = ''.join(c.k.givenArgs)
        if not fileName:
            fileName = g.app.gui.runOpenFileDialog(c,
                title="Open",
                filetypes=table,
                defaultextension=".leo")
        c.bringToFront()
        c.init_error_dialogs()
        ok = False
        if fileName:
            if g.app.loadManager.isLeoFile(fileName):
                c2 = g.openWithFileName(fileName, old_c=c)
                if c2:
                    g.chdir(fileName)
                    g.setGlobalOpenDir(fileName)
                if c2 and closeFlag:
                    g.app.destroyWindow(c.frame)
            elif c.looksLikeDerivedFile(fileName):
                # Create an @file node for files containing Leo sentinels.
                ok = c.importCommands.importDerivedFiles(parent=c.p,
                    paths=[fileName], command='Open')
            else:
                # otherwise, create an @edit node.
                ok = c.createNodeFromExternalFile(fileName)
        c.raise_error_dialogs(kind='write')
        g.app.runAlreadyOpenDialog(c)
        # openWithFileName sets focus if ok.
        if not ok:
            c.initialFocusHelper()
    #@+node:ekr.20090212054250.9: *7* c.createNodeFromExternalFile
    def createNodeFromExternalFile(self, fn):
        '''Read the file into a node.
        Return None, indicating that c.open should set focus.'''
        c = self
        s, e = g.readFileIntoString(fn)
        if s is None: return
        head, ext = g.os_path_splitext(fn)
        if ext.startswith('.'): ext = ext[1:]
        language = g.app.extension_dict.get(ext)
        if language:
            prefix = '@color\n@language %s\n\n' % language
        else:
            prefix = '@killcolor\n\n'
        p2 = c.insertHeadline(op_name='Open File', as_child=False)
        p2.h = '@edit %s' % fn # g.shortFileName(fn)
        p2.b = prefix + s
        w = c.frame.body.wrapper
        if w: w.setInsertPoint(0)
        c.redraw()
        c.recolor()
    #@+node:ekr.20031218072017.2823: *6* c.openWith
    # This is *not* a command.
    # @cmd('open-with')
    def openWith(self, event=None, d=None):
        '''
        Handles the items in the Open With... menu.

        See ExternalFilesController.open_with for details about d.
        '''
        c = self
        if d and g.app.externalFilesController:
            # Select an ancestor @<file> node if possible.
            if not d.get('p'):
                p = c.p
                while p:
                    if p.isAnyAtFileNode():
                        d ['p'] = p
                        break
                    p.moveToParent()
            g.app.externalFilesController.open_with(c, d)
        elif not d:
            g.trace('can not happen: no d', g.callers())
    #@+node:ekr.20140717074441.17772: *6* c.refreshFromDisk
    # refresh_pattern = re.compile('^(@[\w-]+)')

    @cmd('refresh-from-disk')
    def refreshFromDisk(self, event=None):
        '''Refresh an @<file> node from disk.'''
        trace = False and not g.unitTesting
        c, p, u = self, self.p, self.undoer
        c.nodeConflictList = []
        fn = p.anyAtFileNodeName()
        if fn:
            b = u.beforeChangeTree(p)
            redraw_flag = True
            at = c.atFileCommands
            c.recreateGnxDict()
                # Fix bug 1090950 refresh from disk: cut node ressurection.
            i = g.skip_id(p.h, 0, chars='@')
            word = p.h[0: i]
            if word == '@auto':
                # This includes @auto-*
                p.deleteAllChildren()
                # Fix #451: refresh-from-disk selects wrong node.
                p = at.readOneAtAutoNode(fn, p)
            elif word in ('@thin', '@file'):
                p.deleteAllChildren()
                at.read(p, force=True)
            elif word in ('@clean',):
                # Wishlist 148: use @auto parser if the node is empty.
                if p.b.strip() or p.hasChildren():
                    at.readOneAtCleanNode(p)
                else:
                    # Fix #451: refresh-from-disk selects wrong node.
                    p = at.readOneAtAutoNode(fn, p)
            elif word == '@shadow ':
                p.deleteAllChildren()
                at.read(p, force=True, atShadow=True)
            elif word == '@edit':
                p.deleteAllChildren()
                at.readOneAtEditNode(fn, p)
            else:
                g.es_print('can not refresh from disk\n%r' % p.h)
                redraw_flag = False
        else:
            g.warning('not an @<file> node:\n%r' % (p.h))
            redraw_flag = False
        if redraw_flag:
            # Fix #451: refresh-from-disk selects wrong node.
            c.selectPosition(p)
            u.afterChangeTree(p, command='refresh-from-disk', bunch=b)
            # Create the 'Recovered Nodes' tree.
            c.fileCommands.handleNodeConflicts()
            t1 = time.clock()
            c.redraw()
            t2 = time.clock()
            if trace:
                n = sum([1 for z in p.self_and_subtree()])
                h = sum([hash(z.h) for z in p.self_and_subtree()])
                g.trace('%s nodes, hash: %s in %5.2f sec. %r' % (n, h, (t2-t1), p.h))
    #@+node:ekr.20031218072017.2834: *6* c.save & helper
    @cmd('save-file')
    def save(self, event=None, fileName=None):
        '''Save a Leo outline to a file.'''
        if False and g.app.gui.guiName() == 'curses':
            g.trace('===== Save disabled in curses gui =====')
            return
        c = self; p = c.p
        # Do this now: w may go away.
        w = g.app.gui.get_focus(c)
        inBody = g.app.gui.widget_name(w).startswith('body')
        if inBody:
            p.saveCursorAndScroll()
        if g.unitTesting and g.app.unitTestDict.get('init_error_dialogs') is not None:
            # A kludge for unit testing:
            # indicated that c.init_error_dialogs and c.raise_error_dialogs
            # will be called below, *without* actually saving the .leo file.
            c.init_error_dialogs()
            c.raise_error_dialogs(kind='write')
            return
        if g.app.disableSave:
            g.es("save commands disabled", color="purple")
            return
        c.init_error_dialogs()
        # 2013/09/28: use the fileName keyword argument if given.
        # This supports the leoBridge.
        # Make sure we never pass None to the ctor.
        if fileName:
            c.frame.title = g.computeWindowTitle(fileName)
            c.mFileName = fileName
        if not c.mFileName:
            c.frame.title = ""
            c.mFileName = ""
        if c.mFileName:
            # Calls c.setChanged(False) if no error.
            g.app.syntax_error_files = []
            c.fileCommands.save(c.mFileName)
            c.syntaxErrorDialog()
        else:
            root = c.rootPosition()
            if not root.next() and root.isAtEditNode():
                # There is only a single @edit node in the outline.
                # A hack to allow "quick edit" of non-Leo files.
                # See https://bugs.launchpad.net/leo-editor/+bug/381527
                fileName = None
                # Write the @edit node if needed.
                if root.isDirty():
                    c.atFileCommands.writeOneAtEditNode(root,
                        toString=False, force=True)
                c.setChanged(False)
            else:
                fileName = ''.join(c.k.givenArgs)
                if not fileName:
                    fileName = g.app.gui.runSaveFileDialog(c,
                        initialfile=c.mFileName,
                        title="Save",
                        filetypes=[("Leo files", "*.leo")],
                        defaultextension=".leo")
            c.bringToFront()
            if fileName:
                # Don't change mFileName until the dialog has suceeded.
                c.mFileName = g.ensure_extension(fileName, ".leo")
                c.frame.title = c.computeWindowTitle(c.mFileName)
                c.frame.setTitle(c.computeWindowTitle(c.mFileName))
                    # 2013/08/04: use c.computeWindowTitle.
                c.openDirectory = c.frame.openDirectory = g.os_path_dirname(c.mFileName)
                    # Bug fix in 4.4b2.
                if g.app.qt_use_tabs and hasattr(c.frame, 'top'):
                    c.frame.top.leo_master.setTabName(c, c.mFileName)
                c.fileCommands.save(c.mFileName)
                g.app.recentFilesManager.updateRecentFiles(c.mFileName)
                g.chdir(c.mFileName)
        # Done in FileCommands.save.
        # c.redraw_after_icons_changed()
        c.raise_error_dialogs(kind='write')
        # *Safely* restore focus, without using the old w directly.
        if inBody:
            c.bodyWantsFocus()
            p.restoreCursorAndScroll()
        else:
            c.treeWantsFocus()
    #@+node:ekr.20150710083827.1: *7* c.syntaxErrorDialog
    def syntaxErrorDialog(self):
        '''Warn about syntax errors in files.'''
        c = self
        if g.app.syntax_error_files and c.config.getBool('syntax-error-popup', default=False):
            aList = sorted(set(g.app.syntax_error_files))
            g.app.syntax_error_files = []
            message = 'Python errors in:\n\n%s' % '\n'.join(aList)
            g.app.gui.runAskOkDialog(c,
                title='Python Errors',
                message=message,
                text="Ok")
    #@+node:ekr.20110228162720.13980: *6* c.saveAll
    @cmd('save-all')
    def saveAll(self, event=None):
        '''Save all open tabs windows/tabs.'''
        c = self
        c.save() # Force a write of the present window.
        for f in g.app.windowList:
            c = f.c
            if c.isChanged():
                c.save()
        # Restore the present tab.
        c = self
        dw = c.frame.top # A DynamicWindow
        dw.select(c)
    #@+node:ekr.20031218072017.2835: *6* c.saveAs
    @cmd('save-file-as')
    def saveAs(self, event=None, fileName=None):
        '''Save a Leo outline to a file with a new filename.'''
        c = self; p = c.p
        # Do this now: w may go away.
        w = g.app.gui.get_focus(c)
        inBody = g.app.gui.widget_name(w).startswith('body')
        if inBody: p.saveCursorAndScroll()
        if g.app.disableSave:
            g.es("save commands disabled", color="purple")
            return
        c.init_error_dialogs()
        # 2013/09/28: add fileName keyword arg for leoBridge scripts.
        if fileName:
            c.frame.title = g.computeWindowTitle(fileName)
            c.mFileName = fileName
        # Make sure we never pass None to the ctor.
        if not c.mFileName:
            c.frame.title = ""
        if not fileName:
            fileName = ''.join(c.k.givenArgs)
        if not fileName:
            fileName = g.app.gui.runSaveFileDialog(c,
                initialfile=c.mFileName,
                title="Save As",
                filetypes=[("Leo files", "*.leo")],
                defaultextension=".leo")
        c.bringToFront()
        if fileName:
            # Fix bug 998090: save file as doesn't remove entry from open file list.
            if c.mFileName:
                g.app.forgetOpenFile(c.mFileName)
            # Don't change mFileName until the dialog has suceeded.
            c.mFileName = g.ensure_extension(fileName, ".leo")
            # Part of the fix for https://bugs.launchpad.net/leo-editor/+bug/1194209
            c.frame.title = title = c.computeWindowTitle(c.mFileName)
            c.frame.setTitle(title)
                # 2013/08/04: use c.computeWindowTitle.
            c.openDirectory = c.frame.openDirectory = g.os_path_dirname(c.mFileName)
                # Bug fix in 4.4b2.
            # Calls c.setChanged(False) if no error.
            if g.app.qt_use_tabs and hasattr(c.frame, 'top'):
                c.frame.top.leo_master.setTabName(c, c.mFileName)
            c.fileCommands.saveAs(c.mFileName)
            g.app.recentFilesManager.updateRecentFiles(c.mFileName)
            g.chdir(c.mFileName)
        # Done in FileCommands.saveAs.
        # c.redraw_after_icons_changed()
        c.raise_error_dialogs(kind='write')
        # *Safely* restore focus, without using the old w directly.
        if inBody:
            c.bodyWantsFocus()
            p.restoreCursorAndScroll()
        else:
            c.treeWantsFocus()
    #@+node:ekr.20031218072017.2836: *6* c.saveTo
    @cmd('save-file-to')
    def saveTo(self, event=None, fileName=None):
        '''Save a Leo outline to a file, leaving the file associated with the Leo outline unchanged.'''
        c = self; p = c.p
        # Do this now: w may go away.
        w = g.app.gui.get_focus(c)
        inBody = g.app.gui.widget_name(w).startswith('body')
        if inBody:
            p.saveCursorAndScroll()
        if g.app.disableSave:
            g.es("save commands disabled", color="purple")
            return
        c.init_error_dialogs()
        # Add fileName keyword arg for leoBridge scripts.
        if not fileName:
            # set local fileName, _not_ c.mFileName
            fileName = ''.join(c.k.givenArgs)
        if not fileName:
            fileName = g.app.gui.runSaveFileDialog(c,
                initialfile=c.mFileName,
                title="Save To",
                filetypes=[("Leo files", "*.leo")],
                defaultextension=".leo")
        c.bringToFront()
        if fileName:
            fileName = g.ensure_extension(fileName, ".leo")
            c.fileCommands.saveTo(fileName)
            g.app.recentFilesManager.updateRecentFiles(fileName)
            g.chdir(fileName)
        c.raise_error_dialogs(kind='write')
        # *Safely* restore focus, without using the old w directly.
        if inBody:
            c.bodyWantsFocus()
            p.restoreCursorAndScroll()
        else:
            c.treeWantsFocus()
        c.outerUpdate()

    #@+node:ekr.20031218072017.2837: *6* c.revert
    @cmd('revert')
    def revert(self, event=None):
        '''Revert the contents of a Leo outline to last saved contents.'''
        c = self
        # Make sure the user wants to Revert.
        fn = c.mFileName
        if not fn:
            g.es('can not revert unnamed file.')
        if not g.os_path_exists(fn):
            g.es('Can not revert unsaved file: %s' % fn)
            return
        reply = g.app.gui.runAskYesNoDialog(c, "Revert",
            "Revert to previous version of %s?" % fn)
        c.bringToFront()
        if reply == "yes":
            g.app.loadManager.revertCommander(c)
    #@+node:ekr.20070413045221: *6* c.saveAsUnzipped & saveAsZipped
    @cmd('save-file-as-unzipped')
    def saveAsUnzipped(self, event=None):
        '''Save a Leo outline to a file with a new filename,
        ensuring that the file is not compressed.'''
        self.saveAsZippedHelper(False)

    @cmd('save-file-as-zipped')
    def saveAsZipped(self, event=None):
        '''Save a Leo outline to a file with a new filename,
        ensuring that the file is compressed.'''
        self.saveAsZippedHelper(True)

    def saveAsZippedHelper(self, isZipped):
        c = self
        oldZipped = c.isZipped
        c.isZipped = isZipped
        try:
            c.saveAs()
        finally:
            c.isZipped = oldZipped
    #@+node:ekr.20031218072017.2079: *5* Recent Files submenu & allies
    #@+node:ekr.20031218072017.2080: *6* c.clearRecentFiles
    @cmd('clear-recent-files')
    def clearRecentFiles(self, event=None):
        """Clear the recent files list, then add the present file."""
        c = self
        g.app.recentFilesManager.clearRecentFiles(c)
    #@+node:ekr.20031218072017.2081: *6* c.openRecentFile
    def openRecentFile(self, fn=None):
        c = self
        # Automatically close the previous window if...
        closeFlag = (
            c.frame.startupWindow and
                # The window was open on startup
            not c.changed and not c.frame.saved and
                # The window has never been changed
            g.app.numberOfUntitledWindows == 1)
                # Only one untitled window has ever been opened.
        if g.doHook("recentfiles1", c=c, p=c.p, v=c.p, fileName=fn, closeFlag=closeFlag):
            return
        c2 = g.openWithFileName(fn, old_c=c)
        if closeFlag and c2 and c2 != c:
            g.app.destroyWindow(c.frame)
            c2.setLog()
            g.doHook("recentfiles2",
                c=c2, p=c2.p, v=c2.p, fileName=fn, closeFlag=closeFlag)
    #@+node:tbrown.20080509212202.6: *6* c.cleanRecentFiles
    @cmd('clean-recent-files')
    def cleanRecentFiles(self, event=None):
        '''Remove items from the recent files list that are no longer valid.'''
        c = self
        g.app.recentFilesManager.cleanRecentFiles(c)
    #@+node:tbrown.20080509212202.8: *6* c.sortRecentFiles
    @cmd('sort-recent-files')
    def sortRecentFiles(self, event=None):
        '''Sort the recent files list.'''
        c = self
        g.app.recentFilesManager.sortRecentFiles(c)
    #@+node:vitalije.20170703115710.1: *6* c.editRecentFiles
    @cmd('edit-recent-files')
    def editRecentFiles(self, event=None):
        '''Opens recent files list in a new node for editing.'''
        c = self
        g.app.recentFilesManager.editRecentFiles(c)
    #@+node:vitalije.20170703115710.2: *6* c.writeEditedRecentFiles
    @cmd('write-edited-recent-files')
    def writeEditedRecentFiles(self, event=None):
        '''Sort the recent files list.'''
        c = self
        g.app.recentFilesManager.writeEditedRecentFiles(c)
    #@+node:ekr.20031218072017.2838: *5* Read/Write submenu
    #@+node:ekr.20070806105721.1: *6* c.readAtAutoNodes
    @cmd('read-at-auto-nodes')
    def readAtAutoNodes(self, event=None):
        '''Read all @auto nodes in the presently selected outline.'''
        c = self; u = c.undoer; p = c.p
        c.endEditing()
        c.init_error_dialogs()
        undoData = u.beforeChangeTree(p)
        c.importCommands.readAtAutoNodes()
        u.afterChangeTree(p, 'Read @auto Nodes', undoData)
        c.redraw()
        c.raise_error_dialogs(kind='read')
    #@+node:ekr.20031218072017.1839: *6* c.readAtFileNodes
    @cmd('read-at-file-nodes')
    def readAtFileNodes(self, event=None):
        '''Read all @file nodes in the presently selected outline.'''
        c = self; u = c.undoer; p = c.p
        c.endEditing()
        # c.init_error_dialogs() # Done in at.readAll.
        undoData = u.beforeChangeTree(p)
        c.fileCommands.readAtFileNodes()
        u.afterChangeTree(p, 'Read @file Nodes', undoData)
        c.redraw()
        # c.raise_error_dialogs(kind='read') # Done in at.readAll.
    #@+node:ekr.20080801071227.4: *6* c.readAtShadowNodes
    @cmd('read-at-shadow-nodes')
    def readAtShadowNodes(self, event=None):
        '''Read all @shadow nodes in the presently selected outline.'''
        c = self; u = c.undoer; p = c.p
        c.endEditing()
        c.init_error_dialogs()
        undoData = u.beforeChangeTree(p)
        c.atFileCommands.readAtShadowNodes(p)
        u.afterChangeTree(p, 'Read @shadow Nodes', undoData)
        c.redraw()
        c.raise_error_dialogs(kind='read')
    #@+node:ekr.20070915134101: *6* c.readFileIntoNode
    @cmd('read-file-into-node')
    def readFileIntoNode(self, event=None):
        '''Read a file into a single node.'''
        c = self
        undoType = 'Read File Into Node'
        c.endEditing()
        filetypes = [("All files", "*"), ("Python files", "*.py"), ("Leo files", "*.leo"),]
        fileName = g.app.gui.runOpenFileDialog(c,
            title="Read File Into Node",
            filetypes=filetypes,
            defaultextension=None)
        if not fileName: return
        s, e = g.readFileIntoString(fileName)
        if s is None:
            return
        g.chdir(fileName)
        s = '@nocolor\n' + s
        w = c.frame.body.wrapper
        p = c.insertHeadline(op_name=undoType)
        p.setHeadString('@read-file-into-node ' + fileName)
        p.setBodyString(s)
        w.setAllText(s)
        c.redraw(p)
    #@+node:ekr.20031218072017.2839: *6* c.readOutlineOnly
    @cmd('read-outline-only')
    def readOutlineOnly(self, event=None):
        '''Open a Leo outline from a .leo file, but do not read any derived files.'''
        c = self
        c.endEditing()
        fileName = g.app.gui.runOpenFileDialog(c,
            title="Read Outline Only",
            filetypes=[("Leo files", "*.leo"), ("All files", "*")],
            defaultextension=".leo")
        if not fileName:
            return
        try:
            theFile = open(fileName, 'r')
            g.chdir(fileName)
            c = g.app.newCommander(fileName)
            frame = c.frame
            frame.deiconify()
            frame.lift()
            c.fileCommands.readOutlineOnly(theFile, fileName) # closes file.
        except Exception:
            g.es("can not open:", fileName)
    #@+node:ekr.20070915142635: *6* c.writeFileFromNode
    @cmd('write-file-from-node')
    def writeFileFromNode(self, event=None):
        '''If node starts with @read-file-into-node, use the full path name in the headline.
        Otherwise, prompt for a file name.
        '''
        c = self; p = c.p
        c.endEditing()
        h = p.h.rstrip()
        s = p.b
        tag = '@read-file-into-node'
        if h.startswith(tag):
            fileName = h[len(tag):].strip()
        else:
            fileName = None
        if not fileName:
            filetypes = [("All files", "*"), ("Python files", "*.py"), ("Leo files", "*.leo"),]
            fileName = g.app.gui.runSaveFileDialog(c,
                initialfile=None,
                title='Write File From Node',
                filetypes=filetypes,
                defaultextension=None)
        if fileName:
            try:
                theFile = open(fileName, 'w')
                g.chdir(fileName)
            except IOError:
                theFile = None
            if theFile:
                if s.startswith('@nocolor\n'):
                    s = s[len('@nocolor\n'):]
                if not g.isPython3: # 2010/08/27
                    s = g.toEncodedString(s, reportErrors=True)
                theFile.write(s)
                theFile.flush()
                g.blue('wrote:', fileName)
                theFile.close()
            else:
                g.error('can not write %s', fileName)
    #@+node:ekr.20031218072017.2841: *5* Tangle submenu
    #@+node:ekr.20031218072017.2842: *6* c.tangleAll
    @cmd('tangle-all')
    def tangleAll(self, event=None):
        '''
        Tangle all @root nodes in the entire outline.

        **Important**: @root and all tangle and untangle commands are
        deprecated. They are documented nowhere but in these docstrings.
        '''
        c = self
        c.tangleCommands.tangleAll()
    #@+node:ekr.20031218072017.2843: *6* c.tangleMarked
    @cmd('tangle-marked')
    def tangleMarked(self, event=None):
        '''
        Tangle all marked @root nodes in the entire outline.

        **Important**: @root and all tangle and untangle commands are
        deprecated. They are documented nowhere but in these docstrings.
        '''
        c = self
        c.tangleCommands.tangleMarked()
    #@+node:ekr.20031218072017.2844: *6* c.tangle
    @cmd('tangle')
    def tangle(self, event=None):
        '''
        Tangle all @root nodes in the selected outline.

        **Important**: @root and all tangle and untangle commands are
        deprecated. They are documented nowhere but in these docstrings.
        '''
        c = self
        c.tangleCommands.tangle()
    #@+node:ekr.20031218072017.2845: *5* Untangle submenu
    #@+node:ekr.20031218072017.2846: *6* c.untangleAll
    @cmd('untangle-all')
    def untangleAll(self, event=None):
        '''
        Untangle all @root nodes in the entire outline.

        **Important**: @root and all tangle and untangle commands are
        deprecated. They are documented nowhere but in these docstrings.
        '''
        c = self
        c.tangleCommands.untangleAll()
        c.undoer.clearUndoState()
    #@+node:ekr.20031218072017.2847: *6* c.untangleMarked
    @cmd('untangle-marked')
    def untangleMarked(self, event=None):
        '''
        Untangle all marked @root nodes in the entire outline.

        **Important**: @root and all tangle and untangle commands are
        deprecated. They are documented nowhere but in these docstrings.
        '''
        c = self
        c.tangleCommands.untangleMarked()
        c.undoer.clearUndoState()
    #@+node:ekr.20031218072017.2848: *6* c.untangle
    @cmd('untangle')
    def untangle(self, event=None):
        '''Untangle all @root nodes in the selected outline.

        **Important**: @root and all tangle and untangle commands are
        deprecated. They are documented nowhere but in these docstrings.
        '''
        c = self
        c.tangleCommands.untangle()
        c.undoer.clearUndoState()
    #@+node:ekr.20031218072017.2849: *5* Export submenu
    #@+node:ekr.20031218072017.2850: *6* c.exportHeadlines
    @cmd('export-headlines')
    def exportHeadlines(self, event=None):
        '''Export all headlines to an external file.'''
        c = self
        filetypes = [("Text files", "*.txt"), ("All files", "*")]
        fileName = g.app.gui.runSaveFileDialog(c,
            initialfile="headlines.txt",
            title="Export Headlines",
            filetypes=filetypes,
            defaultextension=".txt")
        c.bringToFront()
        if fileName:
            g.setGlobalOpenDir(fileName)
            g.chdir(fileName)
            c.importCommands.exportHeadlines(fileName)
    #@+node:ekr.20031218072017.2851: *6* c.flattenOutline
    @cmd('flatten-outline')
    def flattenOutline(self, event=None):
        '''
        Export the selected outline to an external file.
        The outline is represented in MORE format.
        '''
        c = self
        filetypes = [("Text files", "*.txt"), ("All files", "*")]
        fileName = g.app.gui.runSaveFileDialog(c,
            initialfile="flat.txt",
            title="Flatten Selected Outline",
            filetypes=filetypes,
            defaultextension=".txt")
        c.bringToFront()
        if fileName:
            g.setGlobalOpenDir(fileName)
            g.chdir(fileName)
            c.importCommands.flattenOutline(fileName)
    #@+node:ekr.20141030120755.12: *6* c.flattenOutlineToNode
    @cmd('flatten-outline-to-node')
    def flattenOutlineToNode(self, event=None):
        '''
        Append the body text of all descendants of the selected node to the
        body text of the selected node.
        '''
        c, root, u = self, self.p, self.undoer
        if not root.hasChildren():
            return
        language = g.getLanguageAtPosition(c, root)
        if language:
            single,start,end = g.set_delims_from_language(language)
        else:
            single,start,end = '#', None, None
        bunch = u.beforeChangeNodeContents(root)
        aList = []
        for p in root.subtree():
            if single:
                aList.append('\n\n===== %s %s\n\n' % (single, p.h))
            else:
                aList.append('\n\n===== %s %s %s\n\n' % (start, p.h, end))
            if p.b.strip():
                lines = g.splitLines(p.b)
                aList.extend(lines)
        root.b = root.b.rstrip() + '\n' + ''.join(aList).rstrip() + '\n'
        u.afterChangeNodeContents(root, 'flatten-outline-to-node', bunch)
    #@+node:ekr.20031218072017.2857: *6* c.outlineToCWEB
    @cmd('outline-to-cweb')
    def outlineToCWEB(self, event=None):
        '''
        Export the selected outline to an external file.
        The outline is represented in CWEB format.
        '''
        c = self
        filetypes = [
            ("CWEB files", "*.w"),
            ("Text files", "*.txt"),
            ("All files", "*")]
        fileName = g.app.gui.runSaveFileDialog(c,
            initialfile="cweb.w",
            title="Outline To CWEB",
            filetypes=filetypes,
            defaultextension=".w")
        c.bringToFront()
        if fileName:
            g.setGlobalOpenDir(fileName)
            g.chdir(fileName)
            c.importCommands.outlineToWeb(fileName, "cweb")
    #@+node:ekr.20031218072017.2858: *6* c.outlineToNoweb
    @cmd('outline-to-noweb')
    def outlineToNoweb(self, event=None):
        '''
        Export the selected outline to an external file.
        The outline is represented in noweb format.
        '''
        c = self
        filetypes = [
            ("Noweb files", "*.nw"),
            ("Text files", "*.txt"),
            ("All files", "*")]
        fileName = g.app.gui.runSaveFileDialog(c,
            initialfile=self.outlineToNowebDefaultFileName,
            title="Outline To Noweb",
            filetypes=filetypes,
            defaultextension=".nw")
        c.bringToFront()
        if fileName:
            g.setGlobalOpenDir(fileName)
            g.chdir(fileName)
            c.importCommands.outlineToWeb(fileName, "noweb")
            c.outlineToNowebDefaultFileName = fileName
    #@+node:ekr.20031218072017.2859: *6* c.removeSentinels
    @cmd('remove-sentinels')
    def removeSentinels(self, event=None):
        '''Import one or more files, removing any sentinels.'''
        c = self
        types = [
            ("All files", "*"),
            ("C/C++ files", "*.c"),
            ("C/C++ files", "*.cpp"),
            ("C/C++ files", "*.h"),
            ("C/C++ files", "*.hpp"),
            ("Java files", "*.java"),
            ("Lua files", "*.lua"),
            ("Pascal files", "*.pas"),
            ("Python files", "*.py")]
        names = g.app.gui.runOpenFileDialog(c,
            title="Remove Sentinels",
            filetypes=types,
            defaultextension=".py",
            multiple=True)
        c.bringToFront()
        if names:
            g.chdir(names[0])
            c.importCommands.removeSentinelsCommand(names)
    #@+node:ekr.20031218072017.2860: *6* c.weave
    @cmd('weave')
    def weave(self, event=None):
        '''Simulate a literate-programming weave operation by writing the outline to a text file.'''
        c = self
        filetypes = [("Text files", "*.txt"), ("All files", "*")]
        fileName = g.app.gui.runSaveFileDialog(c,
            initialfile="weave.txt",
            title="Weave",
            filetypes=filetypes,
            defaultextension=".txt")
        c.bringToFront()
        if fileName:
            g.setGlobalOpenDir(fileName)
            g.chdir(fileName)
            c.importCommands.weave(fileName)
    #@+node:ekr.20031218072017.2938: *4* Help Menu (commands)
    #@+node:ekr.20031218072017.2939: *5* c.about (version number & date)
    @cmd('about-leo')
    def about(self, event=None):
        '''Bring up an About Leo Dialog.'''
        c = self
        import datetime
        # Don't use triple-quoted strings or continued strings here.
        # Doing so would add unwanted leading tabs.
        version = g.app.signon + '\n\n'
        theCopyright = (
            "Copyright 1999-%s by Edward K. Ream\n" +
            "All Rights Reserved\n" +
            "Leo is distributed under the MIT License") % datetime.date.today().year
        url = "http://leoeditor.com/"
        email = "edreamleo@gmail.com"
        g.app.gui.runAboutLeoDialog(c, version, theCopyright, url, email)
    #@+node:ekr.20031218072017.2940: *5* c.leoDocumentation
    @cmd('open-leo-docs-leo')
    @cmd('leo-docs-leo')
    def leoDocumentation(self, event=None):
        '''Open LeoDocs.leo in a new Leo window.'''
        c = self
        name = "LeoDocs.leo"
        fileName = g.os_path_finalize_join(g.app.loadDir, "..", "doc", name)
        # Bug fix: 2012/04/09: only call g.openWithFileName if the file exists.
        if g.os_path_exists(fileName):
            c2 = g.openWithFileName(fileName, old_c=c)
            if c2: return
        g.es("not found:", name)
    #@+node:ekr.20031218072017.2941: *5* c.leoHome
    @cmd('open-online-home')
    def leoHome(self, event=None):
        '''Open Leo's Home page in a web browser.'''
        import webbrowser
        url = "http://leoeditor.com/"
        try:
            webbrowser.open_new(url)
        except Exception:
            g.es("not found:", url)
    #@+node:ekr.20090628075121.5994: *5* c.leoQuickStart
    @cmd('open-quickstart-leo')
    @cmd('leo-quickstart-leo')
    def leoQuickStart(self, event=None):
        '''Open quickstart.leo in a new Leo window.'''
        c = self; name = "quickstart.leo"
        fileName = g.os_path_finalize_join(g.app.loadDir, "..", "doc", name)
        # Bug fix: 2012/04/09: only call g.openWithFileName if the file exists.
        if g.os_path_exists(fileName):
            c2 = g.openWithFileName(fileName, old_c=c)
            if c2: return
        g.es("not found:", name)
    #@+node:ekr.20131028155339.17096: *5* c.openCheatSheet
    @cmd('open-cheat-sheet-leo')
    @cmd('leo-cheat-sheet')
    @cmd('cheat-sheet')
    def openCheatSheet(self, event=None, redraw=True):
        '''Open leo/doc/cheatSheet.leo'''
        c = self
        fn = g.os_path_finalize_join(g.app.loadDir, '..', 'doc', 'CheatSheet.leo')
        # g.es_debug(g.os_path_exists(fn),fn)
        if g.os_path_exists(fn):
            c2 = g.openWithFileName(fn, old_c=c)
            if redraw:
                p = g.findNodeAnywhere(c2, "Leo's cheat sheet")
                if p:
                    c2.selectPosition(p)
                    p.expand()
                c2.redraw()
            return c2
        else:
            g.es('file not found: %s' % fn)
            return None
    #@+node:ekr.20161025090405.1: *5* c.openLeoDist
    @cmd('open-leo-dist-leo')
    @cmd('leo-dist-leo')
    def openLeoDist(self, event=None):
        '''Open leoDist.leo in a new Leo window.'''
        c = self
        name = "leoDist.leo"
        fileName = g.os_path_finalize_join(g.app.loadDir, "..", "dist", name)
        if g.os_path_exists(fileName):
            c2 = g.openWithFileName(fileName, old_c=c)
            if c2: return
        g.es("not found:", name)
    #@+node:ekr.20050130152008: *5* c.openLeoPlugins
    @cmd('open-leo-plugins-leo')
    @cmd('leo-plugins-leo')
    def openLeoPlugins(self, event=None):
        '''Open leoPlugins.leo in a new Leo window.'''
        c = self
        names = ('leoPlugins.leo', 'leoPluginsRef.leo',) # Used in error message.
        for name in names:
            fileName = g.os_path_finalize_join(g.app.loadDir, "..", "plugins", name)
            # Bug fix: 2012/04/09: only call g.openWithFileName if the file exists.
            if g.os_path_exists(fileName):
                c2 = g.openWithFileName(fileName, old_c=c)
                if c2: return
        g.es('not found:', ', '.join(names))
    #@+node:ekr.20151225193723.1: *5* c.openLeoPy
    @cmd('open-leo-py-leo')
    @cmd('leo-py-leo')
    def openLeoPy(self, event=None):
        '''Open leoPy.leo in a new Leo window.'''
        c = self
        names = ('leoPy.leo', 'LeoPyRef.leo',) # Used in error message.
        for name in names:
            fileName = g.os_path_finalize_join(g.app.loadDir, "..", "core", name)
            # Only call g.openWithFileName if the file exists.
            if g.os_path_exists(fileName):
                c2 = g.openWithFileName(fileName, old_c=c)
                if c2: return
        g.es('not found:', ', '.join(names))
    #@+node:ekr.20061018094539: *5* c.openLeoScripts
    @cmd('open-scripts-leo')
    @cmd('leo-scripts-leo')
    def openLeoScripts(self, event=None):
        '''Open scripts.leo.'''
        c = self
        fileName = g.os_path_finalize_join(g.app.loadDir, '..', 'scripts', 'scripts.leo')
        # Bug fix: 2012/04/09: only call g.openWithFileName if the file exists.
        if g.os_path_exists(fileName):
            c2 = g.openWithFileName(fileName, old_c=c)
            if c2: return
        g.es('not found:', fileName)
    #@+node:ekr.20031218072017.2943: *5* c.openLeoSettings & c.openMyLeoSettings & helper
    @cmd('open-leo-settings-leo')
    @cmd('leo-settings-leo')
    def openLeoSettings(self, event=None):
        '''Open leoSettings.leo in a new Leo window.'''
        c, lm = self, g.app.loadManager
        path = lm.computeLeoSettingsPath()
        if path:
            return g.openWithFileName(path, old_c=c)
        else:
            g.es('not found: leoSettings.leo')
            return None

    @cmd('open-myLeoSettings-leo')
    @cmd('my-leo-settings-leo')
    def openMyLeoSettings(self, event=None):
        '''Open myLeoSettings.leo in a new Leo window.'''
        c, lm = self, g.app.loadManager
        path = lm.computeMyLeoSettingsPath()
        if path:
            return g.openWithFileName(path, old_c=c)
        else:
            g.es('not found: myLeoSettings.leo')
            return c.createMyLeoSettings()
    #@+node:ekr.20141119161908.2: *6* c.createMyLeoSettings
    def createMyLeoSettings(self):
        """createMyLeoSettings - Return true if myLeoSettings.leo created ok
        """
        name = "myLeoSettings.leo"
        c = self
        homeLeoDir = g.app.homeLeoDir
        loadDir = g.app.loadDir
        configDir = g.app.globalConfigDir
        # check it doesn't already exist
        for path in homeLeoDir, loadDir, configDir:
            fileName = g.os_path_join(path, name)
            if g.os_path_exists(fileName):
                return None
        ok = g.app.gui.runAskYesNoDialog(c,
            title = 'Create myLeoSettings.leo?',
            message = 'Create myLeoSettings.leo in %s?' % (homeLeoDir),
        )
        if ok == 'no':
            return
        # get '@enabled-plugins' from g.app.globalConfigDir
        fileName = g.os_path_join(configDir, "leoSettings.leo")
        leosettings = g.openWithFileName(fileName, old_c=c)
        enabledplugins = g.findNodeAnywhere(leosettings, '@enabled-plugins')
        enabledplugins = enabledplugins.b
        leosettings.close()
        # now create "~/.leo/myLeoSettings.leo"
        fileName = g.os_path_join(homeLeoDir, name)
        c2 = g.openWithFileName(fileName, old_c=c)
        # add content to outline
        nd = c2.rootPosition()
        nd.h = "Settings README"
        nd.b = (
            "myLeoSettings.leo personal settings file created {time}\n\n"
            "Only nodes that are descendants of the @settings node are read.\n\n"
            "Only settings you need to modify should be in this file, do\n"
            "not copy large parts of leoSettings.py here.\n\n"
            "For more information see http://leoeditor.com/customizing.html"
            "".format(time=time.asctime())
        )
        nd = nd.insertAfter()
        nd.h = '@settings'
        nd = nd.insertAsNthChild(0)
        nd.h = '@enabled-plugins'
        nd.b = enabledplugins
        nd = nd.insertAfter()
        nd.h = '@keys'
        nd = nd.insertAsNthChild(0)
        nd.h = '@shortcuts'
        nd.b = (
            "# You can define keyboard shortcuts here of the form:\n"
            "#\n"
            "#    some-command Shift-F5\n"
        )
        c2.redraw()
        return c2
    #@+node:ekr.20131213072223.19441: *5* c.openLeoTOC
    @cmd('open-online-toc')
    def openLeoTOC(self, event=None):
        '''Open Leo's tutorials page in a web browser.'''
        import webbrowser
        url = "http://leoeditor.com/leo_toc.html"
        try:
            webbrowser.open_new(url)
        except Exception:
            g.es("not found:", url)
    #@+node:ekr.20131213072223.19435: *5* c.openLeoTutorials
    @cmd('open-online-tutorials')
    def openLeoTutorials(self, event=None):
        '''Open Leo's tutorials page in a web browser.'''
        import webbrowser
        url = "http://leoeditor.com/tutorial.html"
        try:
            webbrowser.open_new(url)
        except Exception:
            g.es("not found:", url)
    #@+node:ekr.20060613082924: *5* c.openLeoUsersGuide
    @cmd('open-users-guide')
    def openLeoUsersGuide(self, event=None):
        '''Open Leo's users guide in a web browser.'''
        import webbrowser
        url = "http://leoeditor.com/usersguide.html"
        try:
            webbrowser.open_new(url)
        except Exception:
            g.es("not found:", url)
    #@+node:ekr.20131213072223.19437: *5* c.openLeoVideos
    @cmd('open-online-videos')
    def openLeoVideos(self, event=None):
        '''Open Leo's videos page in a web browser.'''
        import webbrowser
        url = "http://leoeditor.com/screencasts.html"
        try:
            webbrowser.open_new(url)
        except Exception:
            g.es("not found:", url)
    #@+node:ekr.20151225095102.1: *5* c.openUnittest
    @cmd('open-unittest-leo')
    @cmd('leo-unittest-leo')
    def openUnittest(self, event=None):
        '''Open unittest.leo.'''
        c = self
        fileName = g.os_path_finalize_join(g.app.loadDir, '..', 'test', 'unitTest.leo')
        if g.os_path_exists(fileName):
            c2 = g.openWithFileName(fileName, old_c=c)
            if c2: return
        g.es('not found:', fileName)
    #@+node:ekr.20131213072223.19532: *5* c.selectAtSettingsNode
    @cmd('open-local-settings')
    def selectAtSettingsNode(self, event=None):
        '''Select the @settings node, if there is one.'''
        c = self
        p = c.config.settingsRoot()
        if p:
            c.selectPosition(p)
            c.redraw()
        else:
            g.es('no local @settings tree.')
    #@+node:ekr.20031218072017.2894: *4* Outline menu (commands)
    #@+node:ekr.20031218072017.2895: *5*  Top Level... (Commands)
    #@+node:ekr.20031218072017.1548: *6* c.Cut & Paste Outlines
    #@+node:ekr.20031218072017.1549: *7* c.cutOutline
    @cmd('cut-node')
    def cutOutline(self, event=None):
        '''Delete the selected outline and send it to the clipboard.'''
        c = self
        if c.canDeleteHeadline():
            c.copyOutline()
            c.deleteOutline("Cut Node")
            c.recolor()
    #@+node:ekr.20031218072017.1550: *7* c.copyOutline
    @cmd('copy-node')
    def copyOutline(self, event=None):
        '''Copy the selected outline to the clipboard.'''
        # Copying an outline has no undo consequences.
        c = self
        c.endEditing()
        s = c.fileCommands.putLeoOutline()
        g.app.paste_c = c
        g.app.gui.replaceClipboardWith(s)
    #@+node:ekr.20031218072017.1551: *7* c.pasteOutline
    # To cut and paste between apps, just copy into an empty body first, then copy to Leo's clipboard.

    @cmd('paste-node')
    def pasteOutline(self, event=None,
        reassignIndices=True,
        redrawFlag=True,
        s=None,
        tempOutline=False, # True: don't make entries in the gnxDict.
        undoFlag=True
    ):
        '''
        Paste an outline into the present outline from the clipboard.
        Nodes do *not* retain their original identify.
        '''
        c = self
        if s is None:
            s = g.app.gui.getTextFromClipboard()
        pasteAsClone = not reassignIndices
        # commenting following block fixes #478
        #if pasteAsClone and g.app.paste_c != c:
        #    g.es('illegal paste-retaining-clones', color='red')
        #    g.es('only valid in same outline.')
        #    return
        undoType = 'Paste Node' if reassignIndices else 'Paste As Clone'
        c.endEditing()
        if not s or not c.canPasteOutline(s):
            return # This should never happen.
        isLeo = g.match(s, 0, g.app.prolog_prefix_string)
        vnodeInfoDict = c.computeVnodeInfoDict() if pasteAsClone else {}
        # create a *position* to be pasted.
        if isLeo:
            pasted = c.fileCommands.getLeoOutlineFromClipboard(s, reassignIndices, tempOutline)
        if not pasted:
            # 2016/10/06:
            # We no longer support pasting MORE outlines. Use import-MORE-files instead.
            return None
        if pasteAsClone:
            copiedBunchList = c.computeCopiedBunchList(pasted, vnodeInfoDict)
        else:
            copiedBunchList = []
        if undoFlag:
            undoData = c.undoer.beforeInsertNode(c.p,
                pasteAsClone=pasteAsClone, copiedBunchList=copiedBunchList)
        c.validateOutline()
        if not tempOutline:
            # Fix #427: Don't check for duplicate vnodes.
            c.checkOutline()
        c.selectPosition(pasted)
        pasted.setDirty()
        c.setChanged(True, redrawFlag=redrawFlag) # Prevent flash when fixing #387.
        # paste as first child if back is expanded.
        back = pasted.back()
        if back and back.hasChildren() and back.isExpanded():
            # 2011/06/21: fixed hanger: test back.hasChildren().
            pasted.moveToNthChildOf(back, 0)
        if pasteAsClone:
            # Set dirty bits for ancestors of *all* pasted nodes.
            # Note: the setDescendentsDirty flag does not do what we want.
            for p in pasted.self_and_subtree():
                p.setAllAncestorAtFileNodesDirty(
                    setDescendentsDirty=False)
        if undoFlag:
            c.undoer.afterInsertNode(pasted, undoType, undoData)
        if redrawFlag:
            c.redraw(pasted)
            c.recolor()
        return pasted
    #@+node:ekr.20050418084539: *8* c.computeVnodeInfoDict
    #@+at
    # 
    # We don't know yet which nodes will be affected by the paste, so we remember
    # everything. This is expensive, but foolproof.
    # 
    # The alternative is to try to remember the 'before' values of nodes in the
    # FileCommands read logic. Several experiments failed, and the code is very ugly.
    # In short, it seems wise to do things the foolproof way.
    # 
    #@@c

    def computeVnodeInfoDict(self):
        c, d = self, {}
        for v in c.all_unique_nodes():
            if v not in d:
                d[v] = g.Bunch(v=v, head=v.h, body=v.b)
        return d
    #@+node:ekr.20050418084539.2: *8* c.computeCopiedBunchList
    def computeCopiedBunchList(self, pasted, vnodeInfoDict):
        # Create a dict containing only copied vnodes.
        d = {}
        for p in pasted.self_and_subtree():
            d[p.v] = p.v
        # g.trace(sorted(list(d.keys())))
        aList = []
        for v in vnodeInfoDict:
            if d.get(v):
                bunch = vnodeInfoDict.get(v)
                aList.append(bunch)
        return aList
    #@+node:EKR.20040610130943: *7* c.pasteOutlineRetainingClones
    @cmd('paste-retaining-clones')
    def pasteOutlineRetainingClones(self, event=None):
        '''Paste an outline into the present outline from the clipboard.
        Nodes *retain* their original identify.'''
        c = self
        return c.pasteOutline(reassignIndices=False)
    #@+node:ekr.20031218072017.2028: *6* c.hoist/dehoist/clearAllHoists
    #@+node:ekr.20120308061112.9865: *7* c.deHoist
    @cmd('de-hoist')
    @cmd('dehoist')
    def dehoist(self, event=None):
        '''Undo a previous hoist of an outline.'''
        c = self
        if not c.p or not c.hoistStack:
            return
        # Don't de-hoist an @chapter node.
        if c.chapterController and c.p.h.startswith('@chapter '):
            if not g.unitTesting:
                g.es('can not de-hoist an @chapter node.',color='blue')
            return
        bunch = c.hoistStack.pop()
        p = bunch.p
        if bunch.expanded: p.expand()
        else: p.contract()
        c.setCurrentPosition(p)
        c.redraw()
        c.frame.clearStatusLine()
        c.frame.putStatusLine("De-Hoist: " + p.h)
        c.undoer.afterDehoist(p, 'DeHoist')
        g.doHook('hoist-changed', c=c)
    #@+node:ekr.20120308061112.9866: *7* c.clearAllHoists
    def clearAllHoists(self):
        '''Undo a previous hoist of an outline.'''
        c = self
        c.hoistStack = []
        c.frame.putStatusLine("Hoists cleared")
        g.doHook('hoist-changed', c=c)
    #@+node:ekr.20120308061112.9867: *7* c.hoist
    @cmd('hoist')
    def hoist(self, event=None):
        '''Make only the selected outline visible.'''
        c = self
        p = c.p
        if not p:
            return
        # Don't hoist an @chapter node.
        if c.chapterController and p.h.startswith('@chapter '):
            if not g.unitTesting:
                g.es('can not hoist an @chapter node.',color='blue')
            return
        # Remember the expansion state.
        bunch = g.Bunch(p=p.copy(), expanded=p.isExpanded())
        c.hoistStack.append(bunch)
        p.expand()
        c.redraw(p)
        c.frame.clearStatusLine()
        c.frame.putStatusLine("Hoist: " + p.h)
        c.undoer.afterHoist(p, 'Hoist')
        g.doHook('hoist-changed', c=c)
    #@+node:ekr.20031218072017.1759: *6* Insert, Delete & Clone (Commands)
    #@+node:ekr.20031218072017.1760: *7* c.checkMoveWithParentWithWarning & c.checkDrag
    #@+node:ekr.20070910105044: *8* c.checkMoveWithParentWithWarning
    def checkMoveWithParentWithWarning(self, root, parent, warningFlag):
        """Return False if root or any of root's descendents is a clone of
        parent or any of parents ancestors."""
        c = self
        message = "Illegal move or drag: no clone may contain a clone of itself"
        # g.trace("root",root,"parent",parent)
        clonedVnodes = {}
        for ancestor in parent.self_and_parents():
            if ancestor.isCloned():
                v = ancestor.v
                clonedVnodes[v] = v
        if not clonedVnodes:
            return True
        for p in root.self_and_subtree():
            if p.isCloned() and clonedVnodes.get(p.v):
                if g.app.unitTesting:
                    g.app.unitTestDict['checkMoveWithParentWithWarning'] = True
                elif warningFlag:
                    c.alert(message)
                return False
        return True
    #@+node:ekr.20070910105044.1: *8* c.checkDrag
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
    #@+node:ekr.20031218072017.1762: *7* c.clone
    @cmd('clone-node')
    def clone(self, event=None):
        '''Create a clone of the selected outline.'''
        c = self; u = c.undoer; p = c.p
        if not p:
            return None
        undoData = c.undoer.beforeCloneNode(p)
        c.endEditing() # Capture any changes to the headline.
        clone = p.clone()
        dirtyVnodeList = clone.setAllAncestorAtFileNodesDirty()
        c.setChanged(True)
        if c.validateOutline():
            u.afterCloneNode(clone, 'Clone Node', undoData, dirtyVnodeList=dirtyVnodeList)
            c.redraw(clone)
            return clone # For mod_labels and chapters plugins.
        else:
            clone.doDelete()
            c.setCurrentPosition(p)
            return None
    #@+node:ekr.20150630152607.1: *7* c.cloneToAtSpot
    @cmd('clone-to-at-spot')
    def cloneToAtSpot(self, event=None):
        '''
        Create a clone of the selected node and move it to the last @spot node
        of the outline. Create the @spot node if necessary.
        '''
        c = self; u = c.undoer; p = c.p
        if not p:
            return
        # 2015/12/27: fix bug 220: do not allow clone-to-at-spot on @spot node.
        if p.h.startswith('@spot'):
            g.es("can not clone @spot node", color='red')
            return
        last_spot = None
        for p2 in c.all_positions():
            if g.match_word(p2.h, 0, '@spot'):
                last_spot = p2.copy()
        if not last_spot:
            last = c.lastTopLevel()
            last_spot = last.insertAfter()
            last_spot.h = '@spot'
        undoData = c.undoer.beforeCloneNode(p)
        c.endEditing() # Capture any changes to the headline.
        clone = p.copy()
        clone._linkAsNthChild(last_spot,
                              n=last_spot.numberOfChildren(),
                              adjust=True)
        dirtyVnodeList = clone.setAllAncestorAtFileNodesDirty()
        c.setChanged(True)
        if c.validateOutline():
            u.afterCloneNode(clone,
                             'Clone Node',
                             undoData,
                             dirtyVnodeList=dirtyVnodeList)
            c.contractAllHeadlines()
            c.redraw()
            c.selectPosition(clone)
        else:
            clone.doDelete()
            c.setCurrentPosition(p)
    #@+node:ekr.20141023154408.5: *7* c.cloneToLastNode
    @cmd('clone-node-to-last-node')
    def cloneToLastNode(self, event=None):
        '''
        Clone the selected node and move it to the last node.
        Do *not* change the selected node.
        '''
        c, p, u = self, self.p, self.undoer
        if not p: return
        prev = p.copy()
        undoData = c.undoer.beforeCloneNode(p)
        c.endEditing() # Capture any changes to the headline.
        clone = p.clone()
        last = c.rootPosition()
        while last and last.hasNext():
            last.moveToNext()
        clone.moveAfter(last)
        dirtyVnodeList = clone.setAllAncestorAtFileNodesDirty()
        c.setChanged(True)
        u.afterCloneNode(clone, 'Clone Node To Last', undoData, dirtyVnodeList=dirtyVnodeList)
        c.redraw(prev)
        # return clone # For mod_labels and chapters plugins.
    #@+node:ekr.20031218072017.1193: *7* c.deleteOutline
    @cmd('delete-node')
    def deleteOutline(self, event=None, op_name="Delete Node"):
        """Deletes the selected outline."""
        c, u = self, self.undoer
        p = c.p
        if not p: return
        c.endEditing() # Make sure we capture the headline for Undo.
        if p.hasVisBack(c): newNode = p.visBack(c)
        else: newNode = p.next() # _not_ p.visNext(): we are at the top level.
        if not newNode: return
        undoData = u.beforeDeleteNode(p)
        dirtyVnodeList = p.setAllAncestorAtFileNodesDirty()
        p.doDelete(newNode)
        c.setChanged(True)
        u.afterDeleteNode(newNode, op_name, undoData, dirtyVnodeList=dirtyVnodeList)
        c.redraw(newNode)
        c.validateOutline()
    #@+node:ekr.20071005173203.1: *7* c.insertChild
    @cmd('insert-child')
    def insertChild(self, event=None):
        '''Insert a node after the presently selected node.'''
        c = self
        return c.insertHeadline(event=event, op_name='Insert Child', as_child=True)
    #@+node:ekr.20031218072017.1761: *7* c.insertHeadline
    @cmd('insert-node')
    def insertHeadline(self, event=None, op_name="Insert Node", as_child=False):
        '''Insert a node after the presently selected node.'''
        trace = False and not g.unitTesting
        c = self; u = c.undoer
        current = c.p
        if not current: return
        c.endEditing()
        if trace: g.trace('==========', c.p.h, g.app.gui.get_focus())
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
        g.doHook('create-node', c=c, p=p)
        p.setDirty(setDescendentsDirty=False)
        dirtyVnodeList = p.setAllAncestorAtFileNodesDirty()
        c.setChanged(True)
        u.afterInsertNode(p, op_name, undoData, dirtyVnodeList=dirtyVnodeList)
        c.redrawAndEdit(p, selectAll=True)
        return p
    #@+node:ekr.20130922133218.11540: *7* c.insertHeadlineBefore (new in Leo 4.11)
    @cmd('insert-node-before')
    def insertHeadlineBefore(self, event=None):
        '''Insert a node before the presently selected node.'''
        c, current, u = self, self.p, self.undoer
        op_name = 'Insert Node Before'
        if not current: return
        # Can not insert before the base of a hoist.
        if c.hoistStack and current == c.hoistStack[-1].p:
            g.warning('can not insert a node before the base of a hoist')
            return
        c.endEditing()
        undoData = u.beforeInsertNode(current)
        p = current.insertBefore()
        g.doHook('create-node', c=c, p=p)
        p.setDirty(setDescendentsDirty=False)
        dirtyVnodeList = p.setAllAncestorAtFileNodesDirty()
        c.setChanged(True)
        u.afterInsertNode(p, op_name, undoData, dirtyVnodeList=dirtyVnodeList)
        c.redrawAndEdit(p, selectAll=True)
        return p
    #@+node:ekr.20031218072017.1765: *7* c.validateOutline
    # Makes sure all nodes are valid.

    def validateOutline(self, event=None):
        c = self
        if not g.app.validate_outline:
            return True
        root = c.rootPosition()
        parent = None
        if root:
            return root.validateOutlineWithParent(parent)
        else:
            return True
    #@+node:ekr.20080425060424.1: *6* Sort...
    #@+node:ekr.20080503055349.1: *7* c.setPositionAfterSort
    def setPositionAfterSort(self, sortChildren):
        c = self
        p = c.p
        p_v = p.v
        parent = p.parent()
        parent_v = p._parentVnode()
        if sortChildren:
            p = parent or c.rootPosition()
        else:
            if parent:
                p = parent.firstChild()
            else:
                p = leoNodes.Position(parent_v.children[0])
            while p and p.v != p_v:
                p.moveToNext()
            p = p or parent
        return p
    #@+node:ekr.20050415134809: *7* c.sortChildren
    # New in Leo 4.7 final: this method no longer supports
    # the 'cmp' keyword arg.

    @cmd('sort-children')
    def sortChildren(self, event=None, key=None, reverse=False):
        '''Sort the children of a node.'''
        c = self; p = c.p
        if p and p.hasChildren():
            c.sortSiblings(p=p.firstChild(), sortChildren=True, key=key, reverse=reverse)
    #@+node:ekr.20050415134809.1: *7* c.sortSiblings
    # New in Leo 4.7 final: this method no longer supports
    # the 'cmp' keyword arg.

    @cmd('sort-siblings')
    def sortSiblings(self, event=None, key=None, p=None, sortChildren=False,
                      reverse=False):
        '''Sort the siblings of a node.'''
        c = self; u = c.undoer
        if not p : p = c.p
        if not p: return
        c.endEditing()
        undoType = 'Sort Children' if sortChildren else 'Sort Siblings'
        parent_v = p._parentVnode()
        parent = p.parent()
        oldChildren = parent_v.children[:]
        newChildren = parent_v.children[:]
        if key is None:

            def lowerKey(self):
                return (self.h.lower())

            key = lowerKey
        newChildren.sort(key=key, reverse=reverse)
        if oldChildren == newChildren:
            return
        # 2010/01/20. Fix bug 510148.
        c.setChanged(True)
        # g.trace(g.listToString(newChildren))
        bunch = u.beforeSort(p, undoType, oldChildren, newChildren, sortChildren)
        parent_v.children = newChildren
        if parent:
            dirtyVnodeList = parent.setAllAncestorAtFileNodesDirty()
        else:
            dirtyVnodeList = []
        u.afterSort(p, bunch, dirtyVnodeList)
        # Sorting destroys position p, and possibly the root position.
        p = c.setPositionAfterSort(sortChildren)
        c.redraw(p)
    #@+node:ekr.20040711135959.2: *5* Check Outline submenu...
    #@+node:ekr.20031218072017.2072: *6* c.checkOutline & helpers
    def checkOutline(self, event=None, check_links=False):
        """
        Check for errors in the outline.
        Return the count of serious structure errors.
        """
        c = self
        g.app.structure_errors = 0
        structure_errors = c.checkGnxs()
        if check_links and not structure_errors:
            structure_errors += c.checkLinks()
        return structure_errors

    @cmd('check-outline')
    def fullCheckOutline(self, event=None):
        '''
        Performs a full check of the consistency of a .leo file.

        As of Leo 5.1, Leo performs checks of gnx's and outline structure
        before writes and after reads, pastes and undo/redo.
        '''
        return self.checkOutline(check_links=True)
    #@+node:ekr.20141024211256.22: *7* c.checkGnxs
    def checkGnxs(self):
        '''
        Check the consistency of all gnx's and remove any tnodeLists.
        Reallocate gnx's for duplicates or empty gnx's.
        Return the number of structure_errors found.
        '''
        c = self
        d = {} # Keys are gnx's; values are lists of vnodes with that gnx.
        ni = g.app.nodeIndices
        t1 = time.time()

        def new_gnx(v):
            '''Set v.fileIndex.'''
            v.fileIndex = ni.getNewIndex(v)

        count, gnx_errors = 0, 0
        for p in c.safe_all_positions():
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
                g.es_print('empty v.fileIndex: %s new: %r' % (v, p.v.gnx), color='red')
        for gnx in sorted(d.keys()):
            aList = list(d.get(gnx))
            if len(aList) != 1:
                g.es_print('multiple vnodes with gnx: %r' % (gnx), color='red')
                for v in aList:
                    gnx_errors += 1
                    g.es_print('new gnx: %s %s' % (v.fileIndex, v), color='red')
                    new_gnx(v)
        ok = not gnx_errors and not g.app.structure_errors
        t2 = time.time()
        if not ok:
            g.es_print('check-outline ERROR! %s %s nodes, %s gnx errors, %s structure errors' % (
                c.shortFileName(), count, gnx_errors, g.app.structure_errors), color='red')
        elif c.verbose_check_outline and not g.unitTesting:
            print('check-outline OK: %4.2f sec. %s %s nodes' % (t2 - t1, c.shortFileName(), count))
        return g.app.structure_errors
    #@+node:ekr.20150318131947.7: *7* c.checkLinks & helpers
    def checkLinks(self):
        '''Check the consistency of all links in the outline.'''
        c = self
        t1 = time.time()
        count, errors = 0, 0
        for p in c.safe_all_positions():
            count += 1
            try:
                c.checkThreadLinks(p)
                c.checkSiblings(p)
                c.checkParentAndChildren(p)
            except AssertionError:
                errors += 1
                junk, value, junk = sys.exc_info()
                g.error("test failed at position %s\n%s" % (repr(p), value))
        t2 = time.time()
        g.es_print('check-links: %4.2f sec. %s %s nodes' % (
            t2 - t1, c.shortFileName(), count), color='blue')
        return errors
    #@+node:ekr.20040314035615.2: *8* c.checkParentAndChildren
    def checkParentAndChildren(self, p):
        '''Check consistency of parent and child data structures.'''
        # Check consistency of parent and child links.
        if p.hasParent():
            n = p.childIndex()
            assert p == p.parent().moveToNthChild(n), "p!=parent.moveToNthChild"
        for child in p.children():
            assert p == child.parent(), "p!=child.parent"
        if p.hasNext():
            assert p.next().parent() == p.parent(), "next.parent!=parent"
        if p.hasBack():
            assert p.back().parent() == p.parent(), "back.parent!=parent"
        # Check consistency of parent and children arrays.
        # Every nodes gets visited, so a strong test need only check consistency
        # between p and its parent, not between p and its children.
        parent_v = p._parentVnode()
        n = p.childIndex()
        assert parent_v.children[n] == p.v, 'fail 1'
    #@+node:ekr.20040314035615.1: *8* c.checkSiblings
    def checkSiblings(self, p):
        '''Check the consistency of next and back links.'''
        back = p.back()
        next = p.next()
        if back:
            assert p == back.next(), 'p!=p.back().next(),  back: %s\nback.next: %s' % (
                back, back.next())
        if next:
            assert p == next.back(), 'p!=p.next().back, next: %s\nnext.back: %s' % (
                next, next.back())
    #@+node:ekr.20040314035615: *8* c.checkThreadLinks
    def checkThreadLinks(self, p):
        '''Check consistency of threadNext & threadBack links.'''
        threadBack = p.threadBack()
        threadNext = p.threadNext()
        if threadBack:
            assert p == threadBack.threadNext(), "p!=p.threadBack().threadNext()"
        if threadNext:
            assert p == threadNext.threadBack(), "p!=p.threadNext().threadBack()"
    #@+node:ekr.20040723094220: *6* Check Outline commands & allies
    # This code is no longer used by any Leo command,
    # but it will be retained for use of scripts.
    #@+node:ekr.20040723094220.1: *7* c.checkAllPythonCode
    def checkAllPythonCode(self, event=None, unittest=False, ignoreAtIgnore=True):
        '''Check all nodes in the selected tree for syntax and tab errors.'''
        c = self; count = 0; result = "ok"
        for p in c.all_unique_positions():
            count += 1
            if not unittest:
                #@+<< print dots >>
                #@+node:ekr.20040723094220.2: *8* << print dots >>
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
                        result = "error" # Continue to check.
                    except Exception:
                        return "surprise" # abort
                    if unittest and result != "ok":
                        g.pr("Syntax error in %s" % p.cleanHeadString())
                        return result # End the unit test: it has failed.
        if not unittest:
            g.blue("check complete")
        return result
    #@+node:ekr.20040723094220.3: *7* c.checkPythonCode
    def checkPythonCode(self, event=None,
        unittest=False, ignoreAtIgnore=True,
        suppressErrors=False, checkOnSave=False
    ):
        '''Check the selected tree for syntax and tab errors.'''
        c = self; count = 0; result = "ok"
        if not unittest:
            g.es("checking Python code   ")
        for p in c.p.self_and_subtree():
            count += 1
            if not unittest and not checkOnSave:
                #@+<< print dots >>
                #@+node:ekr.20040723094220.4: *8* << print dots >>
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
                        result = "error" # Continue to check.
                    except Exception:
                        return "surprise" # abort
        if not unittest:
            g.blue("check complete")
        # We _can_ return a result for unit tests because we aren't using doCommand.
        return result
    #@+node:ekr.20040723094220.5: *7* c.checkPythonNode
    def checkPythonNode(self, p, unittest=False, suppressErrors=False):
        c = self; h = p.h
        # Call getScript to ignore directives and section references.
        body = g.getScript(c, p.copy())
        if not body: return
        try:
            fn = '<node: %s>' % p.h
            if not g.isPython3:
                body = g.toEncodedString(body)
            compile(body + '\n', fn, 'exec')
            c.tabNannyNode(p, h, body, unittest, suppressErrors)
        except SyntaxError:
            if not suppressErrors:
                g.warning("Syntax error in: %s" % h)
                g.es_exception(full=False, color="black")
            if unittest: raise
        except Exception:
            g.es_print('unexpected exception')
            g.es_exception()
            if unittest: raise
    #@+node:ekr.20040723094220.6: *7* c.tabNannyNode
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
                line2 = repr(str(line))[1: -1]
                g.es("offending line:\n", line2)
            if unittest: raise
        except Exception:
            g.trace("unexpected exception")
            g.es_exception()
            if unittest: raise
    #@+node:ekr.20040412060927: *6* c.dumpOutline
    @cmd('dump-outline')
    def dumpOutline(self, event=None):
        """ Dump all nodes in the outline."""
        c = self
        seen = {}
        print('')
        print('=' * 40)
        v = c.hiddenRootNode
        v.dump()
        seen[v] = True
        for p in c.all_positions():
            if p.v not in seen:
                seen[p.v] = True
                p.v.dump()
    #@+node:ekr.20031218072017.2898: *5* Expand & Contract...
    #@+node:ekr.20031218072017.2899: *6* Commands (outline menu)
    #@+node:ekr.20031218072017.2900: *7* c.contractAllHeadlines
    @cmd('contract-all')
    def contractAllHeadlines(self, event=None, redrawFlag=True):
        '''Contract all nodes in the outline.'''
        c = self
        for p in c.all_positions():
            p.contract()
        # Select the topmost ancestor of the presently selected node.
        p = c.p
        while p and p.hasParent():
            p.moveToParent()
        if redrawFlag:
            c.redraw(p, setFocus=True)
        c.expansionLevel = 1 # Reset expansion level.
    #@+node:ekr.20080819075811.3: *7* c.contractAllOtherNodes & helper
    @cmd('contract-all-other-nodes')
    def contractAllOtherNodes(self, event=None):
        '''Contract all nodes except those needed to make the
        presently selected node visible.'''
        c = self; leaveOpen = c.p
        for p in c.rootPosition().self_and_siblings():
            c.contractIfNotCurrent(p, leaveOpen)
        c.redraw()
    #@+node:ekr.20080819075811.7: *8* c.contractIfNotCurrent
    def contractIfNotCurrent(self, p, leaveOpen):
        c = self
        if p == leaveOpen or not p.isAncestorOf(leaveOpen):
            p.contract()
        for child in p.children():
            if child != leaveOpen and child.isAncestorOf(leaveOpen):
                c.contractIfNotCurrent(child, leaveOpen)
            else:
                for p2 in child.self_and_subtree():
                    p2.contract()
    #@+node:ekr.20031218072017.2901: *7* c.contractNode
    @cmd('contract-node')
    def contractNode(self, event=None):
        '''Contract the presently selected node.'''
        c = self; p = c.p
        p.contract()
        if p.isCloned():
            c.redraw() # A full redraw is necessary to handle clones.
        else:
            c.redraw_after_contract(p=p, setFocus=True)
    #@+node:ekr.20040930064232: *7* c.contractNodeOrGoToParent
    @cmd('contract-or-go-left')
    def contractNodeOrGoToParent(self, event=None):
        """Simulate the left Arrow Key in folder of Windows Explorer."""
        trace = False and not g.unitTesting
        c, cc, p = self, self.chapterController, self.p
        parent = p.parent()
        redraw = False
        if trace: g.trace(p.h,
            'children:', p.hasChildren(),
            'expanded:', p.isExpanded(),
            'shouldBeExpanded:', c.shouldBeExpanded(p))
        # Bug fix: 2016/04/19: test p.v.isExpanded().
        if p.hasChildren() and (p.v.isExpanded() or p.isExpanded()):
            c.contractNode()
        elif parent and parent.isVisible(c):
            # New in Leo 4.9.1: contract all children first.
            if c.collapse_on_lt_arrow:
                for child in parent.children():
                    if child.isExpanded():
                        child.contract()
                        redraw = True
            if cc and cc.inChapter and parent.h.startswith('@chapter '):
                if trace: g.trace('root is selected chapter', parent.h)
            else:
                if trace: g.trace('not an @chapter node', parent.h)
                c.goToParent()
        # This is a bit off-putting.
        # elif not parent and not c.hoistStack:
            # p = c.rootPosition()
            # while p:
                # if p.isExpanded():
                    # p.contract()
                    # redraw = True
                # p.moveToNext()
        if redraw:
            c.redraw()
    #@+node:ekr.20031218072017.2902: *7* c.contractParent
    @cmd('contract-parent')
    def contractParent(self, event=None):
        '''Contract the parent of the presently selected node.'''
        c = self; p = c.p
        parent = p.parent()
        if not parent: return
        parent.contract()
        c.redraw_after_contract(p=parent)
    #@+node:ekr.20031218072017.2903: *7* c.expandAllHeadlines
    @cmd('expand-all')
    def expandAllHeadlines(self, event=None):
        '''Expand all headlines.
        Warning: this can take a long time for large outlines.'''
        c = self
        p = c.rootPosition()
        while p:
            c.expandSubtree(p)
            p.moveToNext()
        c.redraw_after_expand(p=c.rootPosition(), setFocus=True)
        c.expansionLevel = 0 # Reset expansion level.
    #@+node:ekr.20031218072017.2904: *7* c.expandAllSubheads
    @cmd('expand-all-subheads')
    def expandAllSubheads(self, event=None):
        '''Expand all children of the presently selected node.'''
        c = self; p = c.p
        if not p: return
        child = p.firstChild()
        c.expandSubtree(p)
        while child:
            c.expandSubtree(child)
            child = child.next()
        c.redraw(p, setFocus=True)
    #@+node:ekr.20031218072017.2905: *7* c.expandLevel1..9
    @cmd('expand-to-level-1')
    def expandLevel1(self, event=None):
        '''Expand the outline to level 1'''
        self.expandToLevel(1)

    @cmd('expand-to-level-2')
    def expandLevel2(self, event=None):
        '''Expand the outline to level 2'''
        self.expandToLevel(2)

    @cmd('expand-to-level-3')
    def expandLevel3(self, event=None):
        '''Expand the outline to level 3'''
        self.expandToLevel(3)

    @cmd('expand-to-level-4')
    def expandLevel4(self, event=None):
        '''Expand the outline to level 4'''
        self.expandToLevel(4)

    @cmd('expand-to-level-5')
    def expandLevel5(self, event=None):
        '''Expand the outline to level 5'''
        self.expandToLevel(5)

    @cmd('expand-to-level-6')
    def expandLevel6(self, event=None):
        '''Expand the outline to level 6'''
        self.expandToLevel(6)

    @cmd('expand-to-level-7')
    def expandLevel7(self, event=None):
        '''Expand the outline to level 7'''
        self.expandToLevel(7)

    @cmd('expand-to-level-8')
    def expandLevel8(self, event=None):
        '''Expand the outline to level 8'''
        self.expandToLevel(8)

    @cmd('expand-to-level-9')
    def expandLevel9(self, event=None):
        '''Expand the outline to level 9'''
        self.expandToLevel(9)
    #@+node:ekr.20031218072017.2906: *7* c.expandNextLevel
    @cmd('expand-next-level')
    def expandNextLevel(self, event=None):
        '''Increase the expansion level of the outline and
        Expand all nodes at that level or lower.'''
        c = self
        # Expansion levels are now local to a particular tree.
        if c.expansionNode != c.p:
            c.expansionLevel = 1
            c.expansionNode = c.p.copy()
        # g.trace(c.expansionLevel)
        self.expandToLevel(c.expansionLevel + 1)
    #@+node:ekr.20031218072017.2907: *7* c.c.expandNode
    @cmd('expand-node')
    def expandNode(self, event=None):
        '''Expand the presently selected node.'''
        trace = False and not g.unitTesting
        c = self; p = c.p
        p.expand()
        if p.isCloned():
            if trace: g.trace('***redraw')
            c.redraw() # Bug fix: 2009/10/03.
        else:
            c.redraw_after_expand(p, setFocus=True)
    #@+node:ekr.20040930064232.1: *7* c.expandNodeAnd/OrGoToFirstChild
    @cmd('expand-and-go-right')
    def expandNodeAndGoToFirstChild(self, event=None):
        """If a node has children, expand it if needed and go to the first child."""
        c = self; p = c.p
        if p.hasChildren():
            if p.isExpanded():
                c.selectPosition(p.firstChild())
            else:
                c.expandNode()
                # Fix bug 930726
                # expandNodeAndGoToFirstChild only expands or only goes to first child .
                c.selectPosition(p.firstChild())
        c.treeFocusHelper()

    @cmd('expand-or-go-right')
    def expandNodeOrGoToFirstChild(self, event=None):
        """Simulate the Right Arrow Key in folder of Windows Explorer."""
        c = self; p = c.p
        if p.hasChildren():
            if not p.isExpanded():
                c.expandNode() # Calls redraw_after_expand.
            else:
                c.redraw_after_expand(p.firstChild(), setFocus=True)
    #@+node:ekr.20060928062431: *7* c.expandOnlyAncestorsOfNode
    @cmd('expand-ancestors-only')
    def expandOnlyAncestorsOfNode(self, event=None, p=None):
        '''Contract all nodes in the outline.'''
        trace = False and not g.unitTesting
        c = self
        level = 1
        if p: c.selectPosition(p) # 2013/12/25
        root = c.p
        if trace: g.trace(root.h)
        for p in c.all_unique_positions():
            p.v.expandedPositions = []
            p.v.contract()
        for p in root.parents():
            if trace: g.trace('call p.expand', p.h, p._childIndex)
            p.expand()
            level += 1
        c.redraw(setFocus=True)
        c.expansionLevel = level # Reset expansion level.
    #@+node:ekr.20031218072017.2908: *7* c.expandPrevLevel
    @cmd('expand-prev-level')
    def expandPrevLevel(self, event=None):
        '''Decrease the expansion level of the outline and
        Expand all nodes at that level or lower.'''
        c = self
        # Expansion levels are now local to a particular tree.
        if c.expansionNode != c.p:
            c.expansionLevel = 1
            c.expansionNode = c.p.copy()
        self.expandToLevel(max(1, c.expansionLevel - 1))
    #@+node:ekr.20031218072017.2909: *6* Utilities
    #@+node:ekr.20031218072017.2910: *7* c.contractSubtree
    def contractSubtree(self, p):
        for p in p.subtree():
            p.contract()
    #@+node:ekr.20031218072017.2911: *7* c.expandSubtree
    def expandSubtree(self, v):
        c = self
        last = v.lastNode()
        while v and v != last:
            v.expand()
            v = v.threadNext()
        c.redraw()
    #@+node:ekr.20031218072017.2912: *7* c.expandToLevel
    def expandToLevel(self, level):
        trace = False and not g.unitTesting
        c = self
        n = c.p.level()
        old_expansion_level = c.expansionLevel
        max_level = 0
        for p in c.p.self_and_subtree():
            if p.level() - n + 1 < level:
                p.expand()
                max_level = max(max_level, p.level() - n + 1)
            else:
                p.contract()
        c.expansionNode = c.p.copy()
        c.expansionLevel = max_level + 1
        if c.expansionLevel != old_expansion_level:
            if trace: g.trace('level', level, 'max_level', max_level+1)
            c.redraw()
        # It's always useful to announce the level.
        # c.k.setLabelBlue('level: %s' % (max_level+1))
        # g.es('level', max_level + 1)
        c.frame.putStatusLine('level: %s' % (max_level+1))
            # bg='red', fg='red')
    #@+node:ekr.20031218072017.2922: *5* Mark...
    #@+node:ekr.20090905110447.6098: *6* c.cloneMarked
    @cmd('clone-marked-nodes')
    def cloneMarked(self, event=None):
        """Clone all marked nodes as children of a new node."""
        c = self; u = c.undoer; p1 = c.p.copy()
        # Create a new node to hold clones.
        parent = p1.insertAfter()
        parent.h = 'Clones of marked nodes'
        cloned, n, p = [], 0, c.rootPosition()
        while p:
            # Careful: don't clone already-cloned nodes.
            if p == parent:
                p.moveToNodeAfterTree()
            elif p.isMarked() and p.v not in cloned:
                cloned.append(p.v)
                if 0: # old code
                    # Calling p.clone would cause problems
                    p.clone().moveToLastChildOf(parent)
                else: # New code.
                    # Create the clone directly as a child of parent.
                    p2 = p.copy()
                    n = parent.numberOfChildren()
                    p2._linkAsNthChild(parent, n, adjust=True)
                p.moveToNodeAfterTree()
                n += 1
            else:
                p.moveToThreadNext()
        if n:
            c.setChanged(True)
            parent.expand()
            c.selectPosition(parent)
            u.afterCloneMarkedNodes(p1)
        else:
            parent.doDelete()
            c.selectPosition(p1)
        if not g.unitTesting:
            g.blue('cloned %s nodes' % (n))
        c.redraw()
    #@+node:ekr.20160502090456.1: *6* c.copyMarked
    @cmd('copy-marked-nodes')
    def copyMarked(self, event=None):
        """Copy all marked nodes as children of a new node."""
        c = self; u = c.undoer; p1 = c.p.copy()
        # Create a new node to hold clones.
        parent = p1.insertAfter()
        parent.h = 'Copies of marked nodes'
        copied, n, p = [], 0, c.rootPosition()
        while p:
            # Careful: don't clone already-cloned nodes.
            if p == parent:
                p.moveToNodeAfterTree()
            elif p.isMarked() and p.v not in copied:
                copied.append(p.v)
                p2 = p.copyWithNewVnodes(copyMarked=True)
                p2._linkAsNthChild(parent, n, adjust=True)
                p.moveToNodeAfterTree()
                n += 1
            else:
                p.moveToThreadNext()
        if n:
            c.setChanged(True)
            parent.expand()
            c.selectPosition(parent)
            u.afterCopyMarkedNodes(p1)
        else:
            parent.doDelete()
            c.selectPosition(p1)
        if not g.unitTesting:
            g.blue('copied %s nodes' % (n))
        c.redraw()
    #@+node:ekr.20111005081134.15540: *6* c.deleteMarked
    @cmd('delete-marked-nodes')
    def deleteMarked(self, event=None):
        """Delete all marked nodes."""
        c = self; u = c.undoer; p1 = c.p.copy()
        undo_data, p = [], c.rootPosition()
        while p:
            if p.isMarked():
                undo_data.append(p.copy())
                next = p.positionAfterDeletedTree()
                p.doDelete()
                p = next
            else:
                p.moveToThreadNext()
        if undo_data:
            u.afterDeleteMarkedNodes(undo_data, p1)
            if not g.unitTesting:
                g.blue('deleted %s nodes' % (len(undo_data)))
            c.setChanged(True)
        # Don't even *think* about restoring the old position.
        c.contractAllHeadlines()
        c.selectPosition(c.rootPosition())
        c.redraw()
    #@+node:ekr.20111005081134.15539: *6* c.moveMarked & helper
    @cmd('move-marked-nodes')
    def moveMarked(self, event=None):
        '''
        Move all marked nodes as children of a new node.
        This command is not undoable.
        Consider using clone-marked-nodes, followed by copy/paste instead.
        '''
        c = self
        p1 = c.p.copy()
        # Check for marks.
        for v in c.all_unique_nodes():
            if v.isMarked():
                break
        else:
            return g.warning('no marked nodes')
        result = g.app.gui.runAskYesNoDialog(c,
            'Move Marked Nodes?',
            message='move-marked-nodes is not undoable\nProceed?',
        )
        if result == 'no':
            return
        # Create a new *root* node to hold the moved nodes.
        # This node's position remains stable while other nodes move.
        parent = c.createMoveMarkedNode()
        assert not parent.isMarked()
        moved = []
        p = c.rootPosition()
        while p:
            assert parent == c.rootPosition()
            # Careful: don't move already-moved nodes.
            if p.isMarked() and not parent.isAncestorOf(p):
                moved.append(p.copy())
                next = p.positionAfterDeletedTree()
                p.moveToLastChildOf(parent)
                    # This does not change parent's position.
                p = next
            else:
                p.moveToThreadNext()
        if moved:
            # Find a position p2 outside of parent's tree with p2.v == p1.v.
            # Such a position may not exist.
            p2 = c.rootPosition()
            while p2:
                if p2 == parent:
                    p2.moveToNodeAfterTree()
                elif p2.v == p1.v:
                    break
                else:
                    p2.moveToThreadNext()
            else:
                # Not found.  Move to last top-level.
                p2 = c.lastTopLevel()
            parent.moveAfter(p2)
            # u.afterMoveMarkedNodes(moved, p1)
            if not g.unitTesting:
                g.blue('moved %s nodes' % (len(moved)))
            c.setChanged(True)
        # c.contractAllHeadlines()
            # Causes problems when in a chapter.
        c.selectPosition(parent)
        c.redraw()
    #@+node:ekr.20111005081134.15543: *7* c.createMoveMarkedNode
    def createMoveMarkedNode(self):
        c = self
        oldRoot = c.rootPosition()
        p = oldRoot.insertAfter()
        p.moveToRoot(oldRoot)
        c.setHeadString(p, 'Moved marked nodes')
        return p
    #@+node:ekr.20031218072017.2923: *6* c.markChangedHeadlines
    @cmd('mark-changed-items')
    def markChangedHeadlines(self, event=None):
        '''Mark all nodes that have been changed.'''
        c = self; u = c.undoer; undoType = 'Mark Changed'
        current = c.p
        c.endEditing()
        u.beforeChangeGroup(current, undoType)
        for p in c.all_unique_positions():
            if p.isDirty() and not p.isMarked():
                bunch = u.beforeMark(p, undoType)
                c.setMarked(p)
                c.setChanged(True)
                u.afterMark(p, undoType, bunch)
        u.afterChangeGroup(current, undoType)
        if not g.unitTesting:
            g.blue('done')
        c.redraw_after_icons_changed()
    #@+node:ekr.20031218072017.2924: *6* c.markChangedRoots
    def markChangedRoots(self, event=None):
        '''Mark all changed @root nodes.'''
        c = self; u = c.undoer; undoType = 'Mark Changed'
        current = c.p
        c.endEditing()
        u.beforeChangeGroup(current, undoType)
        for p in c.all_unique_positions():
            if p.isDirty() and not p.isMarked():
                s = p.b
                flag, i = g.is_special(s, 0, "@root")
                if flag:
                    bunch = u.beforeMark(p, undoType)
                    c.setMarked(p)
                    c.setChanged(True)
                    u.afterMark(p, undoType, bunch)
        u.afterChangeGroup(current, undoType)
        if not g.unitTesting:
            g.blue('done')
        c.redraw_after_icons_changed()
    #@+node:ekr.20031218072017.2925: *6* c.markAllAtFileNodesDirty
    def markAllAtFileNodesDirty(self, event=None):
        '''Mark all @file nodes as changed.'''
        c = self; p = c.rootPosition()
        c.endEditing()
        while p:
            if p.isAtFileNode() and not p.isDirty():
                p.setDirty()
                c.setChanged(True)
                p.moveToNodeAfterTree()
            else:
                p.moveToThreadNext()
        c.redraw_after_icons_changed()
    #@+node:ekr.20031218072017.2926: *6* c.markAtFileNodesDirty
    def markAtFileNodesDirty(self, event=None):
        '''Mark all @file nodes in the selected tree as changed.'''
        c = self
        p = c.p
        if not p: return
        c.endEditing()
        after = p.nodeAfterTree()
        while p and p != after:
            if p.isAtFileNode() and not p.isDirty():
                p.setDirty()
                c.setChanged(True)
                p.moveToNodeAfterTree()
            else:
                p.moveToThreadNext()
        c.redraw_after_icons_changed()
    #@+node:ekr.20031218072017.2928: *6* c.markHeadline
    @cmd('mark')
    def markHeadline(self, event=None):
        '''Toggle the mark of the selected node.'''
        c = self; u = c.undoer; p = c.p
        if not p: return
        c.endEditing()
        undoType = 'Unmark' if p.isMarked() else 'Mark'
        bunch = u.beforeMark(p, undoType)
        if p.isMarked():
            c.clearMarked(p)
        else:
            c.setMarked(p)
        dirtyVnodeList = p.setDirty()
        c.setChanged(True)
        u.afterMark(p, undoType, bunch, dirtyVnodeList=dirtyVnodeList)
        c.redraw_after_icons_changed()
    #@+node:ekr.20031218072017.2929: *6* c.markSubheads
    @cmd('mark-subheads')
    def markSubheads(self, event=None):
        '''Mark all children of the selected node as changed.'''
        c = self; u = c.undoer; undoType = 'Mark Subheads'
        current = c.p
        if not current: return
        c.endEditing()
        u.beforeChangeGroup(current, undoType)
        dirtyVnodeList = []
        for p in current.children():
            if not p.isMarked():
                bunch = u.beforeMark(p, undoType)
                c.setMarked(p)
                dirtyVnodeList2 = p.setDirty()
                dirtyVnodeList.extend(dirtyVnodeList2)
                c.setChanged(True)
                u.afterMark(p, undoType, bunch)
        u.afterChangeGroup(current, undoType, dirtyVnodeList=dirtyVnodeList)
        c.redraw_after_icons_changed()
    #@+node:ekr.20031218072017.2930: *6* c.unmarkAll
    @cmd('unmark-all')
    def unmarkAll(self, event=None):
        '''Unmark all nodes in the entire outline.'''
        c = self; u = c.undoer; undoType = 'Unmark All'
        current = c.p
        if not current: return
        c.endEditing()
        u.beforeChangeGroup(current, undoType)
        changed = False
        p = None # To keep pylint happy.
        for p in c.all_unique_positions():
            if p.isMarked():
                bunch = u.beforeMark(p, undoType)
                # c.clearMarked(p) # Very slow: calls a hook.
                p.v.clearMarked()
                p.v.setDirty()
                u.afterMark(p, undoType, bunch)
                changed = True
        dirtyVnodeList = [p.v for p in c.all_unique_positions() if p.v.isDirty()]
        if changed:
            g.doHook("clear-all-marks", c=c, p=p, v=p)
            c.setChanged(True)
        u.afterChangeGroup(current, undoType, dirtyVnodeList=dirtyVnodeList)
        c.redraw_after_icons_changed()
    #@+node:ekr.20031218072017.1766: *5* Move... (Commands)
    #@+node:ekr.20070420092425: *6* c.cantMoveMessage
    def cantMoveMessage(self):
        c = self; h = c.rootPosition().h
        kind = 'chapter' if h.startswith('@chapter') else 'hoist'
        g.warning("can't move node out of", kind)
    #@+node:ekr.20031218072017.1767: *6* c.demote
    @cmd('demote')
    def demote(self, event=None):
        '''Make all following siblings children of the selected node.'''
        c = self; u = c.undoer
        p = c.p
        if not p or not p.hasNext():
            c.treeFocusHelper()
            return
        # Make sure all the moves will be valid.
        next = p.next()
        while next:
            if not c.checkMoveWithParentWithWarning(next, p, True):
                c.treeFocusHelper()
                return
            next.moveToNext()
        c.endEditing()
        parent_v = p._parentVnode()
        n = p.childIndex()
        followingSibs = parent_v.children[n + 1:]
        # g.trace('sibs2\n',g.listToString(followingSibs2))
        # Remove the moved nodes from the parent's children.
        parent_v.children = parent_v.children[: n + 1]
        # Add the moved nodes to p's children
        p.v.children.extend(followingSibs)
        # Adjust the parent links in the moved nodes.
        # There is no need to adjust descendant links.
        for child in followingSibs:
            child.parents.remove(parent_v)
            child.parents.append(p.v)
        p.expand()
        # Even if p is an @ignore node there is no need to mark the demoted children dirty.
        dirtyVnodeList = p.setAllAncestorAtFileNodesDirty()
        c.setChanged(True)
        u.afterDemote(p, followingSibs, dirtyVnodeList)
        c.redraw(p, setFocus=True)
        c.updateSyntaxColorer(p) # Moving can change syntax coloring.
    #@+node:ekr.20031218072017.1768: *6* c.moveOutlineDown
    #@+at
    # Moving down is more tricky than moving up; we can't move p to be a child of
    # itself. An important optimization: we don't have to call
    # checkMoveWithParentWithWarning() if the parent of the moved node remains the
    # same.
    #@@c

    @cmd('move-outline-down')
    def moveOutlineDown(self, event=None):
        '''Move the selected node down.'''
        c = self; u = c.undoer; p = c.p
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
        c.endEditing()
        undoData = u.beforeMoveNode(p)
        #@+<< Move p down & set moved if successful >>
        #@+node:ekr.20031218072017.1769: *7* << Move p down & set moved if successful >>
        if next.hasChildren() and next.isExpanded():
            # Attempt to move p to the first child of next.
            moved = c.checkMoveWithParentWithWarning(p, next, True)
            if moved:
                dirtyVnodeList = p.setAllAncestorAtFileNodesDirty()
                p.moveToNthChildOf(next, 0)
        else:
            # Attempt to move p after next.
            moved = c.checkMoveWithParentWithWarning(p, next.parent(), True)
            if moved:
                dirtyVnodeList = p.setAllAncestorAtFileNodesDirty()
                p.moveAfter(next)
        # Patch by nh2: 0004-Add-bool-collapse_nodes_after_move-option.patch
        if c.collapse_nodes_after_move and moved and c.sparse_move and parent and not parent.isAncestorOf(p):
            # New in Leo 4.4.2: contract the old parent if it is no longer the parent of p.
            parent.contract()
        #@-<< Move p down & set moved if successful >>
        if moved:
            if inAtIgnoreRange and not p.inAtIgnoreRange():
                # The moved nodes have just become newly unignored.
                p.setDirty() # Mark descendent @thin nodes dirty.
            else: # No need to mark descendents dirty.
                dirtyVnodeList2 = p.setAllAncestorAtFileNodesDirty()
                dirtyVnodeList.extend(dirtyVnodeList2)
            c.setChanged(True)
            u.afterMoveNode(p, 'Move Down', undoData, dirtyVnodeList)
        c.redraw(p, setFocus=True)
        c.updateSyntaxColorer(p) # Moving can change syntax coloring.
    #@+node:ekr.20031218072017.1770: *6* c.moveOutlineLeft
    @cmd('move-outline-left')
    def moveOutlineLeft(self, event=None):
        '''Move the selected node left if possible.'''
        c = self; u = c.undoer; p = c.p
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
        u.afterMoveNode(p, 'Move Left', undoData, dirtyVnodeList)
        # Patch by nh2: 0004-Add-bool-collapse_nodes_after_move-option.patch
        if c.collapse_nodes_after_move and c.sparse_move: # New in Leo 4.4.2
            parent.contract()
        c.redraw(p, setFocus=True)
        c.recolor() # Moving can change syntax coloring.
    #@+node:ekr.20031218072017.1771: *6* c.moveOutlineRight
    @cmd('move-outline-right')
    def moveOutlineRight(self, event=None):
        '''Move the selected node right if possible.'''
        c = self; u = c.undoer; p = c.p
        if not p: return
        if not c.canMoveOutlineRight(): # 11/4/03: Support for hoist.
            if c.hoistStack: self.cantMoveMessage()
            c.treeFocusHelper()
            return
        back = p.back()
        if not back:
            c.treeFocusHelper()
            return
        if not c.checkMoveWithParentWithWarning(p, back, True):
            c.treeFocusHelper()
            return
        c.endEditing()
        undoData = u.beforeMoveNode(p)
        dirtyVnodeList = p.setAllAncestorAtFileNodesDirty()
        n = back.numberOfChildren()
        p.moveToNthChildOf(back, n)
        # Moving an outline right can never bring it outside the range of @ignore.
        dirtyVnodeList2 = p.setAllAncestorAtFileNodesDirty()
        dirtyVnodeList.extend(dirtyVnodeList2)
        c.setChanged(True)
        u.afterMoveNode(p, 'Move Right', undoData, dirtyVnodeList)
        # g.trace(p)
        c.redraw(p, setFocus=True)
        c.recolor()
    #@+node:ekr.20031218072017.1772: *6* c.moveOutlineUp
    @cmd('move-outline-up')
    def moveOutlineUp(self, event=None):
        '''Move the selected node up if possible.'''
        trace = False and not g.unitTesting
        c = self; u = c.undoer; p = c.p
        if not p: return
        if not c.canMoveOutlineUp(): # Support for hoist.
            if c.hoistStack: self.cantMoveMessage()
            c.treeFocusHelper()
            return
        back = p.visBack(c)
        if not back:
            if trace: g.trace('no visBack')
            return
        inAtIgnoreRange = p.inAtIgnoreRange()
        back2 = back.visBack(c)
        c.endEditing()
        undoData = u.beforeMoveNode(p)
        dirtyVnodeList = p.setAllAncestorAtFileNodesDirty()
        moved = False
        #@+<< Move p up >>
        #@+node:ekr.20031218072017.1773: *7* << Move p up >>
        if trace:
            g.trace("visBack", back)
            g.trace("visBack2", back2)
            g.trace("back2.hasChildren", back2 and back2.hasChildren())
            g.trace("back2.isExpanded", back2 and back2.isExpanded())
        parent = p.parent()
        if not back2:
            if c.hoistStack: # hoist or chapter.
                limit, limitIsVisible = c.visLimit()
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
            if c.checkMoveWithParentWithWarning(p, back2, True):
                moved = True
                p.moveToNthChildOf(back2, 0)
        else:
            if c.checkMoveWithParentWithWarning(p, back2.parent(), True):
                moved = True
                p.moveAfter(back2)
        # Patch by nh2: 0004-Add-bool-collapse_nodes_after_move-option.patch
        if c.collapse_nodes_after_move and moved and c.sparse_move and parent and not parent.isAncestorOf(p):
            # New in Leo 4.4.2: contract the old parent if it is no longer the parent of p.
            parent.contract()
        #@-<< Move p up >>
        if moved:
            if inAtIgnoreRange and not p.inAtIgnoreRange():
                # The moved nodes have just become newly unignored.
                dirtyVnodeList2 = p.setDirty() # Mark descendent @thin nodes dirty.
            else: # No need to mark descendents dirty.
                dirtyVnodeList2 = p.setAllAncestorAtFileNodesDirty()
            dirtyVnodeList.extend(dirtyVnodeList2)
            c.setChanged(True)
            u.afterMoveNode(p, 'Move Right', undoData, dirtyVnodeList)
        c.redraw(p, setFocus=True)
        c.updateSyntaxColorer(p) # Moving can change syntax coloring.
    #@+node:ekr.20031218072017.1774: *6* c.promote
    @cmd('promote')
    def promote(self, event=None, undoFlag=True, redrawFlag=True):
        '''Make all children of the selected nodes siblings of the selected node.'''
        c = self; u = c.undoer; p = c.p
        if not p or not p.hasChildren():
            c.treeFocusHelper()
            return
        isAtIgnoreNode = p.isAtIgnoreNode()
        inAtIgnoreRange = p.inAtIgnoreRange()
        c.endEditing()
        parent_v = p._parentVnode()
        children = p.v.children
        # Add the children to parent_v's children.
        n = p.childIndex() + 1
        z = parent_v.children[:]
        parent_v.children = z[: n]
        parent_v.children.extend(children)
        parent_v.children.extend(z[n:])
        # Remove v's children.
        p.v.children = []
        # Adjust the parent links in the moved children.
        # There is no need to adjust descendant links.
        for child in children:
            child.parents.remove(p.v)
            child.parents.append(parent_v)
        c.setChanged(True)
        if undoFlag:
            if not inAtIgnoreRange and isAtIgnoreNode:
                # The promoted nodes have just become newly unignored.
                dirtyVnodeList = p.setDirty() # Mark descendent @thin nodes dirty.
            else: # No need to mark descendents dirty.
                dirtyVnodeList = p.setAllAncestorAtFileNodesDirty()
            u.afterPromote(p, children, dirtyVnodeList)
        if redrawFlag:
            c.redraw(p, setFocus=True)
            c.updateSyntaxColorer(p) # Moving can change syntax coloring.
    #@+node:ekr.20071213185710: *6* c.toggleSparseMove
    @cmd('toggle-sparse-move')
    def toggleSparseMove(self, event=None):
        '''Toggle whether moves collapse the outline.'''
        c = self
        c.sparse_move = not c.sparse_move
        if not g.unitTesting:
            g.blue('sparse-move: %s' % c.sparse_move)
    #@+node:ekr.20031218072017.2913: *5* Goto (Commands)
    #@+node:ekr.20031218072017.1628: *6* c.goNextVisitedNode
    @cmd('go-forward')
    def goNextVisitedNode(self, event=None):
        '''Select the next visited node.'''
        c = self
        p = c.nodeHistory.goNext()
        if p:
            c.nodeHistory.skipBeadUpdate = True
            try:
                c.selectPosition(p)
            finally:
                c.nodeHistory.skipBeadUpdate = False
                c.redraw_after_select(p)
    #@+node:ekr.20031218072017.1627: *6* c.goPrevVisitedNode
    @cmd('go-back')
    def goPrevVisitedNode(self, event=None):
        '''Select the previously visited node.'''
        c = self
        p = c.nodeHistory.goPrev()
        if p:
            c.nodeHistory.skipBeadUpdate = True
            try:
                c.selectPosition(p)
            finally:
                c.nodeHistory.skipBeadUpdate = False
                c.redraw_after_select(p)
    #@+node:ekr.20031218072017.2914: *6* c.goToFirstNode
    @cmd('goto-first-node')
    def goToFirstNode(self, event=None):
        '''Select the first node of the entire outline.'''
        c = self
        p = c.rootPosition()
        c.selectPosition(p)
        c.expandOnlyAncestorsOfNode()
        c.redraw()
        c.treeSelectHelper(p)
    #@+node:ekr.20051012092453: *6* c.goToFirstSibling
    @cmd('goto-first-sibling')
    def goToFirstSibling(self, event=None):
        '''Select the first sibling of the selected node.'''
        c = self; p = c.p
        if p.hasBack():
            while p.hasBack():
                p.moveToBack()
        c.treeSelectHelper(p)
    #@+node:ekr.20070615070925: *6* c.goToFirstVisibleNode
    @cmd('goto-first-visible-node')
    def goToFirstVisibleNode(self, event=None):
        '''Select the first visible node of the selected chapter or hoist.'''
        c = self
        p = c.firstVisible()
        if p:
            c.selectPosition(p)
            c.expandOnlyAncestorsOfNode()
            c.redraw_after_select(p)
            c.treeSelectHelper(p)
    #@+node:ekr.20031218072017.2915: *6* c.goToLastNode
    @cmd('goto-last-node')
    def goToLastNode(self, event=None):
        '''Select the last node in the entire tree.'''
        c = self
        p = c.rootPosition()
        while p and p.hasThreadNext():
            p.moveToThreadNext()
        c.selectPosition(p)
        c.treeSelectHelper(p)
        c.expandOnlyAncestorsOfNode()
        c.redraw()
    #@+node:ekr.20051012092847.1: *6* c.goToLastSibling
    @cmd('goto-last-sibling')
    def goToLastSibling(self, event=None):
        '''Select the last sibling of the selected node.'''
        c = self; p = c.p
        if p.hasNext():
            while p.hasNext():
                p.moveToNext()
        c.treeSelectHelper(p)
    #@+node:ekr.20050711153537: *6* c.goToLastVisibleNode
    @cmd('goto-last-visible-node')
    def goToLastVisibleNode(self, event=None):
        '''Select the last visible node of selected chapter or hoist.'''
        c = self
        p = c.lastVisible()
        if p:
            c.selectPosition(p)
            c.expandOnlyAncestorsOfNode()
            c.redraw_after_select(p)
            c.treeSelectHelper(p)
    #@+node:ekr.20031218072017.2916: *6* c.goToNextClone
    @cmd('goto-next-clone')
    def goToNextClone(self, event=None):
        '''
        Select the next node that is a clone of the selected node.
        If the selected node is not a clone, do find-next-clone.
        '''
        c, p = self, self.p
        cc = c.chapterController; p = c.p
        if not p:
            return
        if not p.isCloned():
            c.findNextClone()
            return
        v = p.v
        p.moveToThreadNext()
        wrapped = False
        while 1:
            if p and p.v == v:
                break
            elif p:
                p.moveToThreadNext()
            elif wrapped:
                break
            else:
                wrapped = True
                p = c.rootPosition()
        if p:
            if cc:
                # Fix bug #252: goto-next clone activate chapter.
                # https://github.com/leo-editor/leo-editor/issues/252
                chapter = cc.getSelectedChapter()
                old_name = chapter and chapter.name
                new_name = cc.findChapterNameForPosition(p)
                if new_name == old_name:
                    c.selectPosition(p)
                    c.redraw_after_select(p)
                else:
                    c.selectPosition(p)
                    cc.selectChapterByName(new_name)
            else:
                c.selectPosition(p)
                c.redraw_after_select(p)
        else:
            g.blue('done')
    #@+node:ekr.20071213123942: *6* c.findNextClone
    @cmd('find-next-clone')
    def findNextClone(self, event=None):
        '''Select the next cloned node.'''
        c = self; p = c.p; cc = c.chapterController
        if not p: return
        if p.isCloned():
            p.moveToThreadNext()
        flag = False
        while p:
            if p.isCloned():
                flag = True; break
            else:
                p.moveToThreadNext()
        if flag:
            if cc:
                # name = cc.findChapterNameForPosition(p)
                cc.selectChapterByName('main')
            c.selectPosition(p)
            c.redraw_after_select(p)
        else:
            g.blue('no more clones')
    #@+node:ekr.20031218072017.2917: *6* c.goToNextDirtyHeadline
    @cmd('goto-next-changed')
    def goToNextDirtyHeadline(self, event=None):
        '''Select the node that is marked as changed.'''
        c = self; p = c.p
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
        if not p: g.blue('done')
        c.treeSelectHelper(p) # Sets focus.
    #@+node:ekr.20031218072017.2918: *6* c.goToNextMarkedHeadline
    @cmd('goto-next-marked')
    def goToNextMarkedHeadline(self, event=None):
        '''Select the next marked node.'''
        c = self; p = c.p
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
        if not p: g.blue('done')
        c.treeSelectHelper(p) # Sets focus.
    #@+node:ekr.20031218072017.2919: *6* c.goToNextSibling
    @cmd('goto-next-sibling')
    def goToNextSibling(self, event=None):
        '''Select the next sibling of the selected node.'''
        c = self; p = c.p
        c.treeSelectHelper(p and p.next())
    #@+node:ekr.20031218072017.2920: *6* c.goToParent
    @cmd('goto-parent')
    def goToParent(self, event=None):
        '''Select the parent of the selected node.'''
        c = self; p = c.p
        c.treeSelectHelper(p and p.parent())
    #@+node:ekr.20031218072017.2921: *6* c.goToPrevSibling
    @cmd('goto-prev-sibling')
    def goToPrevSibling(self, event=None):
        '''Select the previous sibling of the selected node.'''
        c = self; p = c.p
        c.treeSelectHelper(p and p.back())
    #@+node:ekr.20031218072017.2993: *6* c.selectThreadBack
    @cmd('goto-prev-node')
    def selectThreadBack(self, event=None):
        '''Select the node preceding the selected node in outline order.'''
        c = self; p = c.p
        if not p: return
        p.moveToThreadBack()
        c.treeSelectHelper(p)
    #@+node:ekr.20031218072017.2994: *6* c.selectThreadNext
    @cmd('goto-next-node')
    def selectThreadNext(self, event=None):
        '''Select the node following the selected node in outline order.'''
        c = self; p = c.p
        if not p: return
        p.moveToThreadNext()
        c.treeSelectHelper(p)
    #@+node:ekr.20031218072017.2995: *6* c.selectVisBack
    @cmd('goto-prev-visible')
    def selectVisBack(self, event=None):
        '''Select the visible node preceding the presently selected node.'''
        # This has an up arrow for a control key.
        c, p = self, self.p
        if not p:
            return
        if c.canSelectVisBack():
            p.moveToVisBack(c)
            c.treeSelectHelper(p)
        else:
            c.endEditing() # 2011/05/28: A special case.
    #@+node:ekr.20031218072017.2996: *6* c.selectVisNext
    @cmd('goto-next-visible')
    def selectVisNext(self, event=None):
        '''Select the visible node following the presently selected node.'''
        c, p = self, self.p
        if not p:
            return
        if c.canSelectVisNext():
            p.moveToVisNext(c)
            c.treeSelectHelper(p)
        else:
            c.endEditing() # 2011/05/28: A special case.
    #@+node:ekr.20070417112650: *6* c.Utils
    #@+node:ekr.20070226121510: *7*  c.xFocusHelper & initialFocusHelper
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
    #@+node:ekr.20070226113916: *7*  c.treeSelectHelper
    def treeSelectHelper(self, p):
        c = self
        if not p: p = c.p
        if p:
            # Do not call expandAllAncestors here.
            c.selectPosition(p)
            c.redraw_after_select(p)
        c.treeFocusHelper()
    #@+node:ekr.20031218072017.2931: *4* Window Menu
    #@+node:ekr.20031218072017.2092: *5* c.openCompareWindow
    def openCompareWindow(self, event=None):
        '''Open a dialog for comparing files and directories.'''
        c = self; frame = c.frame
        if not frame.comparePanel:
            frame.comparePanel = g.app.gui.createComparePanel(c)
        if frame.comparePanel:
            frame.comparePanel.bringToFront()
        else:
            g.warning('the', g.app.gui.guiName(),
                'gui does not support the compare window')
    #@+node:ekr.20031218072017.2932: *5* c.openPythonWindow
    @cmd('open-python-window')
    def openPythonWindow(self, event=None):
        '''Open Python's Idle debugger in a separate process.'''
        try:
            idlelib_path = imp.find_module('idlelib')[1]
        except ImportError:
            g.es_print('idlelib not found: can not open a Python window.')
            return
        idle = g.os_path_join(idlelib_path, 'idle.py')
        args = [sys.executable, idle]
        if 1: # Use present environment.
            os.spawnv(os.P_NOWAIT, sys.executable, args)
        else: # Use a pristine environment.
            os.spawnve(os.P_NOWAIT, sys.executable, args, os.environ)
    #@+node:peckj.20131023115434.10114: *3* c.createNodeHierarchy
    def createNodeHierarchy(self, heads, parent=None, forcecreate=False):
        ''' Create the proper hierarchy of nodes with headlines defined in
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
        '''
        u = self.undoer
        undoType = 'Create Node Hierarchy'
        undoType2 = 'Insert Node In Hierarchy'
        u_node = parent or self.rootPosition()
        undoData = u.beforeChangeGroup(u_node, undoType)
        changed_node = False
        for idx, head in enumerate(heads):
            if parent is None and idx == 0: # if parent = None, create top level node for first head
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
            else: # else, simply create child nodes each round
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
        return parent # actually the last created/found position
    #@+node:ekr.20100802121531.5804: *3* c.deletePositionsInList
    def deletePositionsInList(self, aList, callback=None, redraw=True):
        '''
        Delete all vnodes corresponding to the positions in aList. If a
        callback is given, the callback is called for every node in the list.

        The callback takes one explicit argument, p. As usual, the callback can
        bind values using keyword arguments.

        This is *very* tricky code. The theory of operation section explains why.
        '''
        #@+<< theory of operation >>
        #@+node:ekr.20150312080344.8: *4* << theory of operation >> (deletePositionsInList)
        #@+at
        #@@language rest
        #@@wrap
        # The Aha: the positions passed to p.deletePositionsInList only
        # *specify* the desired changes; the only way to *make* those changes is
        # to operate on vnodes!
        # 
        # Consider this outline, containing no clones::
        # 
        #     + ROOT
        #       - A
        #       - B
        # 
        # The fundamental problem is this. If we delete node A, the index of
        # node B in ROOT.children will change. This problem has (almost) nothing
        # to do with clones or positions.
        # 
        # To make this concrete, let's look at the *vnodes* that represent this
        # tree. It is the vnodes, and *not* the positions, that represent all of
        # Leo's data. Let ROOT, A and B be the vnodes corresponding to the nodes
        # ROOT, A and B. ROOT.children will look like this at first::
        # 
        #     ROOT.children = [A,B]
        # 
        # That is, the children array contains references (links) to both A and
        # B. After deleting A, we will have::
        # 
        #     ROOT.children = [B]
        # 
        # As you can see, the reference to B is at index 1 of ROOT.children
        # before deleting A, and at index 0 of ROOT.children after deleting A.
        # Thus, *any* position referring to B will become invalid after deleting
        # A.
        # 
        # Several people, including myself, have proposed an unsound
        # solution--just delete positions in reverse order, so that B will be
        # deleted before A. This idea has appeal, but it is wrong. Here is an
        # outline that shows that there is *no* correct order for deleting
        # positions. All A' nodes are clones of each other::
        # 
        #     + ROOT
        #       + A'
        #         - B # at position p1
        #       + A'
        #         - B # at position p2
        # 
        # **Important**: B is *not* a clone. Also note that there is only *one*
        # node called A and *one* node called B. The children arrays will look
        # like::
        # 
        #     ROOT.children = [A,A]
        #     A.children = [B]
        #     B.children = []
        # 
        # It surely must be reasonable to pass either *or both* positions p1 and
        # p2 to p.deletePositionsInList. But after deleting the B corresponding
        # to p1, the children arrays will look like:
        # 
        #     ROOT.children = [A,A]
        #     A.children = []
        #     B.children = [] # B is no longer referenced anywhere!
        # 
        # So if p.deletePositionsInList attempts to delete position p2 (from A),
        # B will no longer appear in A.children!
        # 
        # There are many other cases that we could discuss, but the conclusion
        # in all cases is that we must use the positions passed to
        # p.deletePositionsInList only as *hints* about what to do.
        # 
        # Happily, there is a simple strategy that sidesteps all the
        # difficulties:
        # 
        # Step 1. Verify, *before* making any changes to the outline, that all
        # the positions passed to p.deletePositionsInList *initially* make
        # sense.
        # 
        # Step 2. Treat each position as a "request" to delete *some* vnode from
        # the children array in the *position's* parent vnode.
        # 
        # This is just a bit subtle. Let me explain it in detail.
        # 
        # First, recall that vnodes do not have unique parent vnodes. Because of
        # clones, a vnode may may have *many* parents. Happily, every position
        # *does* specify a unique parent (vnode) at that position.
        # 
        # Second, as shown above, there is no way to order positions such that
        # all later positions remain valid. As the example above shows, deleting
        # (the vnode corresponding to) a position P may cause *all* later
        # positions referring to P.v to refer to *already deleted* vnodes.
        # 
        # In other words, we simply *must* ignore the child indices in
        # positions. Given a position P, P.parent is well defined. So Step 2
        # above will simply delete the *first* element in P.parent.children
        # containing P.v.
        # 
        # As we have seen, there may not even *be* any such element of
        # P.parent.children: a previous delete may have already deleted the last
        # item of P.parent.children equal to P.v. That should *not* be
        # considered an error--Step 1 has ensured that all positions
        # *originally* did make sense.
        # 
        # Summary
        # 
        # Positions passed to p.deletePositionsInList specify *vnodes* to be
        # deleted from specific parents, but they do *not* specify at what index
        # in the parent.children array (if any!) those vnodes are to be found.
        # The algorithm will delete the *first* item in the children array that
        # references the vnode to be deleted.
        # 
        # This will almost always be good enough. In the unlikely event that
        # more control is desired, p.deletePositionsInList can not possibly be
        # used.
        # 
        # The new emphasis on vnodes at last puts the problem an a completely
        # solid foundation. Moreover, the new algorithm should be considerably
        # faster than the old: there is no need to sort positions.
        #@-<< theory of operation >>
        trace = (False or g.app.debug) and not g.unitTesting
        c = self
        # Verify all positions *before* altering the tree.
        aList2 = []
        for p in aList:
            if c.positionExists(p):
                aList2.append(p.copy())
            else:
                g.trace('invalid position', p)
        if not aList2:
            return # Don't redraw the screen unless necessary!
        # Delete p.v for all positions p in reversed(sorted(aList2)).
        if callback:
            for p in reversed(sorted(aList2)):
                if c.positionExists(p):
                    callback(p)
                elif trace:
                    g.trace('position does not exist', p and p.h)
        else:
            for p in reversed(sorted(aList2)):
                if c.positionExists(p):
                    v = p.v
                    parent_v = p.stack[-1][0] if p.stack else c.hiddenRootNode
                    if v in parent_v.children:
                        childIndex = parent_v.children.index(v)
                        if trace: g.trace('deleting', parent_v, childIndex, v)
                        v._cutLink(childIndex, parent_v)
                    else:
                        if trace: g.trace('already deleted', parent_v, v)
                elif trace:
                    g.trace('position does not exist', p and p.h)
        # Bug fix 2014/03/13: Make sure c.hiddenRootNode always has at least one child.
        if not c.hiddenRootNode.children:
            v = leoNodes.VNode(context=c)
            v._addLink(childIndex=0, parent_v=c.hiddenRootNode, adjust=False)
            if trace: g.trace('new root', v)
        if redraw:
            c.selectPosition(c.rootPosition())
                # Calls redraw()
            # c.redraw()
    #@+node:ekr.20080901124540.1: *3* c.Directive scanning
    # These are all new in Leo 4.5.1.
    #@+node:ekr.20080827175609.39: *4* c.scanAllDirectives
    #@@nobeautify

    def scanAllDirectives(self,p=None):
        '''
        Scan p and ancestors for directives.

        Returns a dict containing the results, including defaults.
        '''
        trace = False and not g.unitTesting
        c = self
        p = p or c.p
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
        if trace: g.trace(lang_dict.get('language'),g.callers())
        # g.trace(d.get('tabwidth'))
        return d
    #@+node:ekr.20080828103146.15: *4* c.scanAtPathDirectives
    def scanAtPathDirectives(self, aList):
        '''Scan aList for @path directives.
        Return a reasonable default if no @path directive is found.'''
        trace = False and not g.unitTesting
        verbose = True
        c = self
        c.scanAtPathDirectivesCount += 1 # An important statistic.
        if trace and verbose: g.trace('**entry', g.callers(4))
        # Step 1: Compute the starting path.
        # The correct fallback directory is the absolute path to the base.
        if c.openDirectory: # Bug fix: 2008/9/18
            base = c.openDirectory
        else:
            base = g.app.config.relative_path_base_directory
            if base and base == "!": base = g.app.loadDir
            elif base and base == ".": base = c.openDirectory
        if trace and verbose:
            g.trace('base   ', base)
            g.trace('loadDir', g.app.loadDir)
        absbase = c.os_path_finalize_join(g.app.loadDir, base)
        if trace and verbose: g.trace('absbase', absbase)
        # Step 2: look for @path directives.
        paths = []
        for d in aList:
            # Look for @path directives.
            path = d.get('path')
            warning = d.get('@path_in_body')
            if trace and path:
                g.trace('**** d', d)
                g.trace('**** @path path', path)
            if path is not None: # retain empty paths for warnings.
                # Convert "path" or <path> to path.
                path = g.stripPathCruft(path)
                if path and not warning:
                    paths.append(path)
                # We will silently ignore empty @path directives.
        # Add absbase and reverse the list.
        paths.append(absbase)
        paths.reverse()
        # Step 3: Compute the full, effective, absolute path.
        if trace and verbose:
            g.printList(paths, tag='c.scanAtPathDirectives: raw paths')
        path = c.os_path_finalize_join(*paths)
        if trace and verbose: g.trace('joined path:', path)
        if trace: g.trace('returns', path)
        return path or g.getBaseDirectory(c)
            # 2010/10/22: A useful default.
    #@+node:ekr.20080828103146.12: *4* c.scanAtRootDirectives (no longer used)
    # No longer used. Was called only by scanLanguageDirectives.

    def scanAtRootDirectives(self, aList):
        '''Scan aList for @root-code and @root-doc directives.'''
        c = self
        # To keep pylint happy.
        tag = 'at_root_bodies_start_in_doc_mode'
        start_in_doc = hasattr(c.config, tag) and getattr(c.config, tag)
        # New in Leo 4.6: dashes are valid in directive names.
        for d in aList:
            if 'root-code' in d:
                return 'code'
            elif 'root-doc' in d:
                return 'doc'
            elif 'root' in d:
                return 'doc' if start_in_doc else 'code'
        return None
    #@+node:ekr.20080922124033.5: *4* c.os_path_finalize and c.os_path_finalize_join
    def os_path_finalize(self, path, **keys):
        c = self
        keys['c'] = c
        return g.os_path_finalize(path, **keys)

    def os_path_finalize_join(self, *args, **keys):
        c = self
        keys['c'] = c
        return g.os_path_finalize_join(*args, **keys)
    #@+node:ekr.20081006100835.1: *4* c.getNodePath & c.getNodeFileName
    # Not used in Leo's core.
    # Used by the UNl plugin.  Does not need to create a path.

    def getNodePath(self, p):
        '''Return the path in effect at node p.'''
        c = self
        aList = g.get_directives_dict_list(p)
        path = c.scanAtPathDirectives(aList)
        return path
    # Not used in Leo's core.

    def getNodeFileName(self, p):
        '''
        Return the full file name at node p,
        including effects of all @path directives.
        Return None if p is no kind of @file node.
        '''
        c = self
        path = g.scanAllAtPathDirectives(c, p)
        name = ''
        for p in p.self_and_parents():
            name = p.anyAtFileNodeName()
            if name: break
        if name:
            # The commander method supports {{expr}}; the global function does not.
            name = c.os_path_finalize_join(path, name)
        return name
    #@+node:ekr.20091211111443.6265: *3* c.doBatchOperations & helpers
    def doBatchOperations(self, aList=None):
        # Validate aList and create the parents dict
        if aList is None: aList = []
        ok, d = self.checkBatchOperationsList(aList)
        if not ok:
            return g.error('do-batch-operations: invalid list argument')
        for v in list(d.keys()):
            aList2 = d.get(v, [])
            if aList2:
                aList.sort()
                for n, op in aList2:
                    if op == 'insert':
                        g.trace('insert:', v.h, n)
                    else:
                        g.trace('delete:', v.h, n)
    #@+node:ekr.20091211111443.6266: *4* c.checkBatchOperationsList
    def checkBatchOperationsList(self, aList):
        ok = True; d = {}
        for z in aList:
            try:
                op, p, n = z
                ok = (op in ('insert', 'delete') and
                    isinstance(p, leoNodes.position) and g.isInt(n))
                if ok:
                    aList2 = d.get(p.v, [])
                    data = n, op
                    aList2.append(data)
                    d[p.v] = aList2
            except ValueError:
                ok = False
            if not ok: break
        return ok, d
    #@+node:ekr.20031218072017.2817: *3* c.doCommand & helper
    command_count = 0

    def doCommand(self, command, label, event=None):
        """
        Execute the given command, invoking hooks and catching exceptions.

        The code assumes that the "command1" hook has completely handled the command if
        g.doHook("command1") returns False.
        This provides a simple mechanism for overriding commands.
        """
        c, p = self, self.p
        trace = (False or c.config.getBool('trace_doCommand')) and not g.unitTesting
        c.setLog()
        self.command_count += 1
        # The presence of this message disables all commands.
        if c.disableCommandsMessage:
            g.blue(c.disableCommandsMessage)
            return
        if c.exists and c.inCommand and not g.unitTesting:
            # g.trace('inCommand',c)
            g.app.commandInterruptFlag = True
            g.error('ignoring command: already executing a command.')
            return
        g.app.commandInterruptFlag = False
        if label and event is None: # Do this only for legacy commands.
            if label == "cantredo": label = "redo"
            if label == "cantundo": label = "undo"
            g.app.commandName = label
        if not g.doHook("command1", c=c, p=p, v=p, label=label):
            try:
                # redrawCount = c.frame.tree.redrawCount
                c.inCommand = True
                if trace: g.trace('start', command)
                val = command(event)
                if trace: g.trace('end', command)
                if c and c.exists: # Be careful: the command could destroy c.
                    c.inCommand = False
                    c.k.funcReturn = val
                # else: g.pr('c no longer exists',c)
            except Exception:
                c.inCommand = False
                if g.app.unitTesting:
                    raise
                else:
                    g.es_print("exception executing command")
                    g.es_exception(c=c)
            if c and c.exists:
                if c.requestCloseWindow:
                    if trace: g.trace('closing window after command')
                    c.requestCloseWindow = False
                    g.app.closeLeoWindow(c.frame)
                else:
                    if trace: g.trace('calling outerUpdate')
                    c.outerUpdate()
                    # redrawCount2 = c.frame.tree.redrawCount
                    # if redrawCount2 > redrawCount + 1:
                        # g.trace('too many redraw', label, redrawCount2, redrawCount)

        # Be careful: the command could destroy c.
        if c and c.exists:
            p = c.p
            g.doHook("command2", c=c, p=p, v=p, label=label)
    #@+node:ekr.20080514131122.20: *4* c.outerUpdate
    def outerUpdate(self):
        trace = False and not g.unitTesting
        traceFocus = False
        c = self
        aList = []
        if not c.exists or not c.k:
            return
        if c.requestBringToFront:
            if hasattr(c.frame, 'bringToFront'):
                c.requestBringToFront.frame.bringToFront()
                    # c.requestBringToFront is a commander.
        # The iconify requests are made only by c.bringToFront.
        if c.requestedIconify in ('iconify', 'deiconify'):
            aList.append(c.requestedIconify)
            c.frame.iconify() if c.requestedIconify == 'iconify' else c.frame.deiconify()
        if c.requestedFocusWidget:
            w = c.requestedFocusWidget
            if traceFocus: aList.append('focus: %s' % g.app.gui.widget_name(w))
            c.set_focus(w)
        else:
            # We must not set the focus to the body pane here!
            # That would make nested calls to c.outerUpdate significant.
            pass
        if trace and aList: g.trace(','.join(aList))
        c.requestBringToFront = None
        c.requestedFocusWidget = None
        c.requestedIconify = ''
        table = (
            ("childrenModified", g.childrenModifiedSet),
            ("contentModified", g.contentModifiedSet),
        )
        for kind, mods in table:
            if mods:
                g.doHook(kind, c=c, nodes=mods)
                mods.clear()
        
    #@+node:ekr.20031218072017.2945: *3* c.Dragging
    #@+node:ekr.20031218072017.2353: *4* c.dragAfter
    def dragAfter(self, p, after):
        c = self; u = self.undoer; undoType = 'Drag'
        current = c.p
        inAtIgnoreRange = p.inAtIgnoreRange()
        if not c.checkDrag(p, after): return
        if not c.checkMoveWithParentWithWarning(p, after.parent(), True): return
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
        u.afterMoveNode(p, undoType, undoData, dirtyVnodeList=dirtyVnodeList)
        c.redraw(p)
        c.updateSyntaxColorer(p) # Dragging can change syntax coloring.
    #@+node:ekr.20031218072017.2947: *4* c.dragToNthChildOf
    def dragToNthChildOf(self, p, parent, n):
        c = self; u = c.undoer; undoType = 'Drag'
        current = c.p
        inAtIgnoreRange = p.inAtIgnoreRange()
        if not c.checkDrag(p, parent): return
        if not c.checkMoveWithParentWithWarning(p, parent, True): return
        c.endEditing()
        undoData = u.beforeMoveNode(current)
        dirtyVnodeList = p.setAllAncestorAtFileNodesDirty()
        p.moveToNthChildOf(parent, n)
        if inAtIgnoreRange and not p.inAtIgnoreRange():
            # The moved nodes have just become newly unignored.
            dirtyVnodeList2 = p.setDirty() # Mark descendent @thin nodes dirty.
            dirtyVnodeList.extend(dirtyVnodeList2)
        else: # No need to mark descendents dirty.
            dirtyVnodeList2 = p.setAllAncestorAtFileNodesDirty()
            dirtyVnodeList.extend(dirtyVnodeList2)
        c.setChanged(True)
        u.afterMoveNode(p, undoType, undoData, dirtyVnodeList=dirtyVnodeList)
        c.redraw(p)
        c.updateSyntaxColorer(p) # Dragging can change syntax coloring.
    #@+node:ekr.20031218072017.2946: *4* c.dragCloneToNthChildOf
    def dragCloneToNthChildOf(self, p, parent, n):
        c = self; u = c.undoer; undoType = 'Clone Drag'
        current = c.p
        inAtIgnoreRange = p.inAtIgnoreRange()
        # g.trace("p,parent,n:",p.h,parent.h,n)
        clone = p.clone() # Creates clone & dependents, does not set undo.
        if (
            not c.checkDrag(p, parent) or
            not c.checkMoveWithParentWithWarning(clone, parent, True)
        ):
            clone.doDelete(newNode=p) # Destroys clone and makes p the current node.
            c.selectPosition(p) # Also sets root position.
            return
        c.endEditing()
        undoData = u.beforeInsertNode(current)
        dirtyVnodeList = clone.setAllAncestorAtFileNodesDirty()
        clone.moveToNthChildOf(parent, n)
        if inAtIgnoreRange and not p.inAtIgnoreRange():
            # The moved nodes have just become newly unignored.
            dirtyVnodeList2 = p.setDirty() # Mark descendent @thin nodes dirty.
            dirtyVnodeList.extend(dirtyVnodeList2)
        else: # No need to mark descendents dirty.
            dirtyVnodeList2 = p.setAllAncestorAtFileNodesDirty()
            dirtyVnodeList.extend(dirtyVnodeList2)
        c.setChanged(True)
        u.afterInsertNode(clone, undoType, undoData, dirtyVnodeList=dirtyVnodeList)
        c.redraw(clone)
        c.updateSyntaxColorer(clone) # Dragging can change syntax coloring.
    #@+node:ekr.20031218072017.2948: *4* c.dragCloneAfter
    def dragCloneAfter(self, p, after):
        c = self; u = c.undoer; undoType = 'Clone Drag'
        current = c.p
        clone = p.clone() # Creates clone.  Does not set undo.
        if c.checkDrag(p, after) and c.checkMoveWithParentWithWarning(clone, after.parent(), True):
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
            u.afterInsertNode(clone, undoType, undoData, dirtyVnodeList=dirtyVnodeList)
            p = clone
        else:
            # g.trace("invalid clone drag")
            clone.doDelete(newNode=p)
        c.redraw(p)
        c.updateSyntaxColorer(clone) # Dragging can change syntax coloring.
    #@+node:ekr.20031218072017.2949: *3* c.Drawing Utilities
    #@+node:ekr.20080514131122.7: *4* c.begin/endUpdate
    def beginUpdate(self):
        '''Deprecated: does nothing.'''
        g.trace('***** c.beginUpdate is deprecated', g.callers())
        if g.app.unitTesting: assert(False)

    def endUpdate(self, flag=True):
        '''Request a redraw of the screen if flag is True.'''
        g.trace('***** c.endUpdate is deprecated', g.callers())
        if g.app.unitTesting: assert(False)
        c = self
        if flag:
            c.requestRedrawFlag = True

    BeginUpdate = beginUpdate # Compatibility with old scripts
    EndUpdate = endUpdate # Compatibility with old scripts
    #@+node:ekr.20080514131122.8: *4* c.bringToFront
    def bringToFront(self, c2=None, set_focus=True):
        c = self
        c2 = c2 or c
        c.requestBringToFront = c2
        c.requestedIconify = 'deiconify'
        c.requestedFocusWidget = c2.frame.body.wrapper
        g.app.gui.ensure_commander_visible(c2)

    BringToFront = bringToFront # Compatibility with old scripts
    #@+node:ekr.20040803072955.143: *4* c.expandAllAncestors
    def expandAllAncestors(self, p):
        '''
        Expand all ancestors without redrawing.
        Return a flag telling whether a redraw is needed.
        '''
        # c = self
        trace = False and not g.unitTesting
        # trace = trace and p.h.startswith(' Tests of @auto-md')
        redraw_flag = False
        for p in p.parents():
            if not p.v.isExpanded():
                if trace: g.trace('call p.v.expand and p.expand', p.h, p._childIndex)
                p.v.expand()
                p.expand()
                redraw_flag = True
            elif p.isExpanded():
                if trace: g.trace('call p.v.expand', p.h, p._childIndex)
                p.v.expand()
            else:
                if trace: g.trace('call p.expand', p.h, p._childIndex)
                p.expand()
                redraw_flag = True
        # if trace: g.trace(redraw_flag, g.callers())
        return redraw_flag
    #@+node:ekr.20080514131122.12: *4* c.recolorCommand
    # def recolor(self):
        # c = self
        # c.requestRecolorFlag = True

    # requestRecolor = recolor

    @cmd('recolor')
    def recolorCommand(self, event=None):
        '''Force a full recolor.'''
        c = self
        wrapper = c.frame.body.wrapper
        # Setting all text appears to be the only way.
        i, j = wrapper.getSelectionRange()
        ins = wrapper.getInsertPoint()
        wrapper.setAllText(c.p.b)
        wrapper.setSelectionRange(i, j, insert=ins)
    #@+node:ekr.20080514131122.14: *4* c.redrawing...
    #@+node:ekr.20090110073010.1: *5* c.redraw
    def redraw(self, p=None, setFocus=False):
        '''Redraw the screen immediately.'''
        trace = False and not g.unitTesting
        c = self
        if not p:
            p = c.p or c.rootPosition()
        if not p:
            return
        c.expandAllAncestors(p)
        if p:
            # Fix bug https://bugs.launchpad.net/leo-editor/+bug/1183855
            # This looks redundant, but it is probably the only safe fix.
            c.frame.tree.select(p)
        # 2012/03/10: tree.redraw will change the position if p is a hoisted @chapter node.
        p2 = c.frame.tree.redraw(p)
        # Be careful.  NullTree.redraw returns None.
        c.selectPosition(p2 or p)
        if trace:
            g.trace(p2 and p2.h)
            # g.trace('setFocus', setFocus, p2 and p2.h or p and p.h)
        if setFocus: c.treeFocusHelper()
    # Compatibility with old scripts

    force_redraw = redraw
    redraw_now = redraw
    #@+node:ekr.20090110131802.2: *5* c.redraw_after_contract
    def redraw_after_contract(self, p=None, setFocus=False):
        c = self
        c.endEditing()
        if p:
            c.setCurrentPosition(p)
        else:
            p = c.currentPosition()
        if p.isCloned():
            c.redraw(p=p, setFocus=setFocus)
        else:
            c.frame.tree.redraw_after_contract(p)
            if setFocus: c.treeFocusHelper()
    #@+node:ekr.20090112065525.1: *5* c.redraw_after_expand
    def redraw_after_expand(self, p=None, setFocus=False):
        c = self
        c.endEditing()
        if p:
            c.setCurrentPosition(p)
        else:
            p = c.currentPosition()
        if p.isCloned():
            c.redraw(p=p, setFocus=setFocus)
        else:
            c.frame.tree.redraw_after_expand(p)
            if setFocus: c.treeFocusHelper()
    #@+node:ekr.20090110073010.2: *5* c.redraw_after_head_changed
    def redraw_after_head_changed(self):
        '''Redraw the screen (if needed) when editing ends.
        This may be a do-nothing for some gui's.'''
        return self.frame.tree.redraw_after_head_changed()
    #@+node:ekr.20090110073010.3: *5* c.redraw_afer_icons_changed
    def redraw_after_icons_changed(self):
        '''Update the icon for the presently selected node,
        or all icons if the 'all' flag is true.'''
        c = self
        c.frame.tree.redraw_after_icons_changed()
        # c.treeFocusHelper()
    #@+node:ekr.20090110073010.4: *5* c.redraw_after_select
    def redraw_after_select(self, p):
        '''Redraw the screen after node p has been selected.'''
        trace = False and not g.unitTesting
        if trace: g.trace('(Commands)', p and p.h or '<No p>', g.callers(4))
        c = self
        flag = c.expandAllAncestors(p)
        if flag:
            c.frame.tree.redraw_after_select(p)
    #@+node:ekr.20080514131122.13: *4* c.recolor
    def recolor(self, **kwargs):
        # Support QScintillaColorizer.colorize.
        c = self
        p = kwargs.get('p')
        for name in ('incremental', 'interruptable'):
            if name in kwargs:
                print('c.recolor_now: "%s" keyword arg is deprecated' % name)
        colorizer = c.frame.body.colorizer
        if colorizer and hasattr(colorizer, 'colorize'):
            colorizer.colorize(p or c.p)
            
    recolor_now = recolor
    #@+node:ekr.20080514131122.17: *4* c.widget_name
    def widget_name(self, widget):
        # c = self
        return g.app.gui.widget_name(widget) if g.app.gui else '<no widget>'
    #@+node:ekr.20120306130648.9849: *3* c.enableMenuBar
    def enableMenuBar(self):
        '''A failed attempt to work around Ubuntu Unity memory bugs.'''
        c = self
        # g.trace(c.frame.title,g.callers())
        if 0:
            if c.frame.menu.isNull:
                return
            for frame in g.app.windowList:
                if frame != c.frame:
                    frame.menu.menuBar.setDisabled(True)
            c.frame.menu.menuBar.setEnabled(True)
    #@+node:ekr.20031218072017.2955: *3* c.Enabling Menu Items
    #@+node:ekr.20040323172420: *4* Slow routines: no longer used
    #@+node:ekr.20031218072017.2966: *5* c.canGoToNextDirtyHeadline (slow)
    def canGoToNextDirtyHeadline(self):
        c = self; current = c.p
        for p in c.all_unique_positions():
            if p != current and p.isDirty():
                return True
        return False
    #@+node:ekr.20031218072017.2967: *5* c.canGoToNextMarkedHeadline (slow)
    def canGoToNextMarkedHeadline(self):
        c = self; current = c.p
        for p in c.all_unique_positions():
            if p != current and p.isMarked():
                return True
        return False
    #@+node:ekr.20031218072017.2968: *5* c.canMarkChangedHeadline (slow)
    def canMarkChangedHeadlines(self):
        c = self
        for p in c.all_unique_positions():
            if p.isDirty():
                return True
        return False
    #@+node:ekr.20031218072017.2969: *5* c.canMarkChangedRoots (slow)
    def canMarkChangedRoots(self):
        c = self
        for p in c.all_unique_positions():
            if p.isDirty and p.isAnyAtFileNode():
                return True
        return False
    #@+node:ekr.20040131170659: *4* c.canClone (new for hoist)
    def canClone(self):
        c = self
        if c.hoistStack:
            current = c.p
            bunch = c.hoistStack[-1]
            return current != bunch.p
        else:
            return True
    #@+node:ekr.20031218072017.2956: *4* c.canContractAllHeadlines
    def canContractAllHeadlines(self):
        '''Contract all nodes in the tree.'''
        c = self
        for p in c.all_positions(): # was c.all_unique_positions()
            if p.isExpanded():
                return True
        return False
    #@+node:ekr.20031218072017.2957: *4* c.canContractAllSubheads
    def canContractAllSubheads(self):
        c = self; current = c.p
        for p in current.subtree():
            if p != current and p.isExpanded():
                return True
        return False
    #@+node:ekr.20031218072017.2958: *4* c.canContractParent
    def canContractParent(self):
        c = self
        return c.p.parent()
    #@+node:ekr.20031218072017.2959: *4* c.canContractSubheads
    def canContractSubheads(self):
        c = self; current = c.p
        for child in current.children():
            if child.isExpanded():
                return True
        return False
    #@+node:ekr.20031218072017.2960: *4* c.canCutOutline & canDeleteHeadline
    def canDeleteHeadline(self):
        c = self; p = c.p
        if c.hoistStack:
            bunch = c.hoistStack[0]
            if p == bunch.p: return False
        return p.hasParent() or p.hasThreadBack() or p.hasNext()

    canCutOutline = canDeleteHeadline
    #@+node:ekr.20031218072017.2961: *4* c.canDemote
    def canDemote(self):
        c = self
        return c.p.hasNext()
    #@+node:ekr.20031218072017.2962: *4* c.canExpandAllHeadlines
    def canExpandAllHeadlines(self):
        '''Return True if the Expand All Nodes menu item should be enabled.'''
        c = self
        for p in c.all_positions(): # was c.all_unique_positions()
            if not p.isExpanded():
                return True
        return False
    #@+node:ekr.20031218072017.2963: *4* c.canExpandAllSubheads
    def canExpandAllSubheads(self):
        c = self
        for p in c.p.subtree():
            if not p.isExpanded():
                return True
        return False
    #@+node:ekr.20031218072017.2964: *4* c.canExpandSubheads
    def canExpandSubheads(self):
        c = self; current = c.p
        for p in current.children():
            if p != current and not p.isExpanded():
                return True
        return False
    #@+node:ekr.20031218072017.2287: *4* c.canExtract, canExtractSection & canExtractSectionNames
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
    #@+node:ekr.20031218072017.2965: *4* c.canFindMatchingBracket
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
    #@+node:ekr.20040303165342: *4* c.canHoist & canDehoist
    def canDehoist(self):
        '''
        Return True if do-hoist should be enabled in a menu.
        Should not be used in any other context.
        '''
        c = self
        return bool(c.hoistStack)

    def canHoist(self):
        # This is called at idle time, so minimizing positions is crucial!
        '''
        Return True if hoist should be enabled in a menu.
        Should not be used in any other context.
        '''
        return True
        # c = self
        # if c.hoistStack:
            # p = c.hoistStack[-1].p
            # return p and not c.isCurrentPosition(p)
        # elif c.currentPositionIsRootPosition():
            # return c.currentPositionHasNext()
        # else:
            # return True
    #@+node:ekr.20031218072017.2970: *4* c.canMoveOutlineDown
    def canMoveOutlineDown(self):
        c = self; current = c.p
        return current and current.visNext(c)
    #@+node:ekr.20031218072017.2971: *4* c.canMoveOutlineLeft
    def canMoveOutlineLeft(self):
        c = self; p = c.p
        if c.hoistStack:
            bunch = c.hoistStack[-1]
            if p and p.hasParent():
                p.moveToParent()
                return p != bunch.p and bunch.p.isAncestorOf(p)
            else:
                return False
        else:
            return p and p.hasParent()
    #@+node:ekr.20031218072017.2972: *4* c.canMoveOutlineRight
    def canMoveOutlineRight(self):
        c = self; p = c.p
        if c.hoistStack:
            bunch = c.hoistStack[-1]
            return p and p.hasBack() and p != bunch.p
        else:
            return p and p.hasBack()
    #@+node:ekr.20031218072017.2973: *4* c.canMoveOutlineUp
    def canMoveOutlineUp(self):
        c = self; current = c.p
        visBack = current and current.visBack(c)
        if not visBack:
            return False
        elif visBack.visBack(c):
            return True
        elif c.hoistStack:
            limit, limitIsVisible = c.visLimit()
            if limitIsVisible: # A hoist
                return current != limit
            else: # A chapter.
                return current != limit.firstChild()
        else:
            return current != c.rootPosition()
    #@+node:ekr.20031218072017.2974: *4* c.canPasteOutline
    def canPasteOutline(self, s=None):
        trace = False and not g.unitTesting
        # c = self
        if not s:
            s = g.app.gui.getTextFromClipboard()
        if s:
            if g.match(s, 0, g.app.prolog_prefix_string):
                if trace: g.trace('matches xml prolog')
                return True
        else:
            if trace: g.trace('no clipboard text')
            return False
    #@+node:ekr.20031218072017.2975: *4* c.canPromote
    def canPromote(self):
        c = self; v = c.currentVnode()
        return v and v.hasChildren()
    #@+node:ekr.20031218072017.2977: *4* c.canSelect....
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
    #@+node:ekr.20031218072017.2978: *4* c.canShiftBodyLeft/Right
    def canShiftBodyLeft(self):
        c = self
        w = c.frame.body.wrapper
        return w and w.getAllText()

    canShiftBodyRight = canShiftBodyLeft
    #@+node:ekr.20031218072017.2979: *4* c.canSortChildren, canSortSiblings
    def canSortChildren(self):
        c = self; p = c.p
        return p and p.hasChildren()

    def canSortSiblings(self):
        c = self; p = c.p
        return p and (p.hasNext() or p.hasBack())
    #@+node:ekr.20031218072017.2980: *4* c.canUndo & canRedo
    def canUndo(self):
        c = self
        return c.undoer.canUndo()

    def canRedo(self):
        c = self
        return c.undoer.canRedo()
    #@+node:ekr.20031218072017.2981: *4* c.canUnmarkAll
    def canUnmarkAll(self):
        c = self
        for p in c.all_unique_positions():
            if p.isMarked():
                return True
        return False
    #@+node:ekr.20111217154130.10286: *3* c.Error dialogs
    #@+node:ekr.20111217154130.10284: *4* c.init_error_dialogs
    def init_error_dialogs(self):
        c = self
        c.import_error_nodes = []
        c.ignored_at_file_nodes = []
        if g.unitTesting:
            d = g.app.unitTestDict
            tag = 'init_error_dialogs'
            d[tag] = 1 + d.get(tag, 0)
    #@+node:ekr.20111217154130.10285: *4* c.raise_error_dialogs
    def raise_error_dialogs(self, kind='read'):
        '''Warn abouit read/write failures.'''
        c = self
        use_dialogs = True
        if g.unitTesting:
            d = g.app.unitTestDict
            tag = 'raise_error_dialogs'
            d[tag] = 1 + d.get(tag, 0)
            # This trace catches all too-many-calls failures.
            # g.trace(g.callers())
        else:
            # Issue one or two dialogs or messages.
            if c.import_error_nodes or c.ignored_at_file_nodes:
                g.app.gui.dismiss_splash_screen()
            if c.import_error_nodes:
                files = '\n'.join(sorted(set(c.import_error_nodes)))
                if use_dialogs:
                    g.app.gui.runAskOkDialog(c,
                        title='Import errors',
                        message='The following were not imported properly. '
                        '@ignore was inserted:\n%s' % (files))
                else:
                    g.es('import errors...', color='red')
                    g.es('\n'.join(sorted(files)), color='blue')
            if c.ignored_at_file_nodes:
                files = '\n'.join(sorted(set(c.ignored_at_file_nodes)))
                kind = 'read' if kind.startswith('read') else 'written'
                if use_dialogs:
                    g.app.gui.runAskOkDialog(c,
                        title='Not read',
                        message='The following were not %s because they contain @ignore:\n%s' % (
                            kind, files))
                else:
                    g.es('not %s (@ignore)...' % (kind), color='red')
                    g.es(files, color='blue')
        c.init_error_dialogs()
    #@+node:ekr.20051106040126: *3* c.executeMinibufferCommand
    def executeMinibufferCommand(self, commandName):
        c = self; k = c.k
        func = c.commandsDict.get(commandName)
        if func:
            event = g.app.gui.create_key_event(c, None, None, None)
            k.masterCommand(commandName=None, event=event, func=func)
            return k.funcReturn
        else:
            g.error('no such command: %s %s' % (commandName, g.callers()))
            return None
    #@+node:ekr.20091002083910.6106: *3* c.find_b & find_h (PosList)
    #@+<< PosList doc >>
    #@+node:bob.20101215134608.5898: *4* << PosList doc >>
    #@@nocolor-node
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
    #@+node:ville.20090311190405.70: *4* c.find_h
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
    #@+node:ville.20090311200059.1: *4* c.find_b
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
                if g.isPython3:
                    t1.__next__()
                else:
                    t1.next()
            except StopIteration:
                continue
            pc = p.copy()
            pc.matchiter = t2
            res.append(pc)
        return res
    #@+node:ekr.20150410095543.1: *3* c.findNodeOutsideAnyAtFileTree
    def findNodeOutsideAnyAtFileTree(self, target):
        '''Select the first clone of target that is outside any @file node.'''
        trace = False and not g.unitTesting
        c = self
        if target.isCloned():
            v = target.v
            for p in c.all_positions():
                if p.v == v:
                    for parent in p.self_and_parents():
                        if parent.isAnyAtFileNode():
                            break
                    else:
                        if trace: g.trace('found', p.h)
                        return p
        if trace: g.trace('not found', target.h)
        return target
    #@+node:ekr.20141028061518.23: *3* c.Focus
    #@+node:ekr.20080514131122.9: *4* c.get/request/set_focus
    def get_focus(self):
        c = self
        trace = (False or g.app.trace_focus) and not g.unitTesting
        w = g.app.gui and g.app.gui.get_focus(c)
        if trace: g.trace('(c)', repr(w and g.app.gui.widget_name(w)))
        return w

    def get_requested_focus(self):
        c = self
        return c.requestedFocusWidget

    def request_focus(self, w):
        trace = (False or g.app.trace_focus) and not g.unitTesting
        c = self
        if w and g.app.gui:
            if trace: g.trace('(c)', repr(g.app.gui.widget_name(w)))
            c.requestedFocusWidget = w

    def set_focus(self, w, force=False):
        trace = (False or g.app.trace_focus) and not g.unitTesting
        c = self
        if w and g.app.gui:
            if trace: g.trace('(c)', repr(w and g.app.gui.widget_name(w)))
            g.app.gui.set_focus(c, w)
        else:
            if trace: g.trace('(c) no w')
        c.requestedFocusWidget = None
    #@+node:ekr.20080514131122.10: *4* c.invalidateFocus
    def invalidateFocus(self):
        '''Indicate that the focus is in an invalid location, or is unknown.'''
        # c = self
        # c.requestedFocusWidget = None
        pass
    #@+node:ekr.20080514131122.16: *4* c.traceFocus (not used)
    def traceFocus(self, w):
        c = self
        if False or (not g.app.unitTesting and c.config.getBool('trace_focus')):
            c.trace_focus_count += 1
            g.pr('%4d' % (c.trace_focus_count), c.widget_name(w), g.callers(8))
    #@+node:ekr.20080514131122.18: *4* c.xWantsFocus
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
    #@+node:ekr.20080514131122.19: *4* c.xWantsFocusNow
    # widgetWantsFocusNow does an automatic update.

    def widgetWantsFocusNow(self, w):
        c = self
        ### Old code: no need to do this.
            # c.request_focus(w)
            # c.outerUpdate()
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
    #@+node:ekr.20091001141621.6061: *3* c.generators
    #@+node:ekr.20091001141621.6043: *4* c.all_nodes & all_unique_nodes
    def all_nodes(self):
        '''A generator returning all vnodes in the outline, in outline order.'''
        c = self
        for p in c.all_positions():
            yield p.v

    def all_unique_nodes(self):
        '''A generator returning each vnode of the outline.'''
        c = self
        for p in c.all_unique_positions():
            yield p.v

    # Compatibility with old code...
    all_tnodes_iter = all_nodes
    all_vnodes_iter = all_nodes
    all_unique_tnodes_iter = all_unique_nodes
    all_unique_vnodes_iter = all_unique_nodes
    #@+node:ekr.20091001141621.6044: *4* c.all_positions
    def all_positions(self):
        '''A generator return all positions of the outline, in outline order.'''
        c = self
        p = c.rootPosition()
        while p:
            yield p.copy()
            p.moveToThreadNext()

    # Compatibility with old code...
    all_positions_iter = all_positions
    allNodes_iter = all_positions
    #@+node:ekr.20161120121226.1: *4* c.all_roots
    def all_roots(self, predicate=None):
        '''
        A generator yielding *all* the root positions in the outline that
        satisfy the given predicate. p.isAnyAtFileNode is the default
        predicate.

        The generator yields all **root** anywhere in the outline that satisfy
        the predicate. Once a root is found, the generator skips its subtree.
        '''
        c = self
        if predicate is None:

            # pylint: disable=function-redefined
            def predicate(p):
                return p.isAnyAtFileNode()

        p = c.rootPosition()
        while p:
            if predicate(p):
                yield p.copy() # 2017/02/19
                p.moveToNodeAfterTree()
            else:
                p.moveToThreadNext()

    #@+node:ekr.20161120125322.1: *4* c.all_unique_roots
    def all_unique_roots(self, predicate=None):
        '''
        A generator yielding all unique root positions in the outline that
        satisfy the given predicate. p.isAnyAtFileNode is the default
        predicate.

        The generator yields all **root** anywhere in the outline that satisfy
        the predicate. Once a root is found, the generator skips its subtree.
        '''
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
                yield p.copy() # 2017/02/19
                p.moveToNodeAfterTree()
            else:
                p.moveToThreadNext()
    #@+node:ekr.20091001141621.6062: *4* c.all_unique_positions
    def all_unique_positions(self):
        '''
        A generator return all positions of the outline, in outline order.
        Returns only the first position for each vnode.
        '''
        c = self
        p = c.rootPosition()
        seen = set()
        while p:
            if p.v in seen:
                p.moveToNodeAfterTree()
            else:
                seen.add(p.v)
                yield p.copy()
                p.moveToThreadNext()

    # Compatibility with old code...
    all_positions_with_unique_tnodes_iter = all_unique_positions
    all_positions_with_unique_vnodes_iter = all_unique_positions
    #@+node:ekr.20150316175921.5: *4* c.safe_all_positions
    def safe_all_positions(self):
        '''
        A generator returning all positions of the outline. This generator does
        *not* assume that vnodes are never their own ancestors.
        '''
        c = self
        p = c.rootPosition() # Make one copy.
        while p:
            yield p.copy()
            p.safeMoveToThreadNext()
    #@+node:ekr.20031218072017.2982: *3* c.Getters & Setters
    #@+node:ekr.20060906211747: *4* c.Getters
    #@+node:ekr.20040803140033: *5* c.currentPosition
    def currentPosition(self):
        """
        Return a copy of the presently selected position or a new null
        position. So c.p.copy() is never necessary.
        """
        c = self
        if hasattr(c, '_currentPosition') and getattr(c, '_currentPosition'):
            # New in Leo 4.4.2: *always* return a copy.
            return c._currentPosition.copy()
        else:
            return c.rootPosition()

    # For compatibiility with old scripts...
    currentVnode = currentPosition
    #@+node:ekr.20040306220230.1: *5* c.edit_widget
    def edit_widget(self, p):
        c = self
        return p and c.frame.tree.edit_widget(p)
    #@+node:ekr.20031218072017.2986: *5* c.fileName & relativeFileName & shortFileName
    # Compatibility with scripts

    def fileName(self):
        return self.mFileName

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
    #@+node:ekr.20150417073117.1: *5* c.getTabWidth
    def getTabWidth(self, p):
        '''Return the tab width in effect at p.'''
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
        else:
            return p == c._currentPosition
    #@+node:ekr.20040803112450.1: *6* c.isRootPosition
    def isRootPosition(self, p):
        c = self
        root = c.rootPosition()
        return p and root and p == root # 2011/03/03
    #@+node:ekr.20031218072017.2987: *5* c.isChanged
    def isChanged(self):
        return self.changed
    #@+node:ekr.20140106215321.16676: *5* c.lastTopLevel
    def lastTopLevel(self):
        '''Return the last top-level position in the outline.'''
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
            # g.trace('next',next)
            if next and next.isVisible(c):
                p = next
            else: break
        return p
    #@+node:ekr.20040311094927: *5* c.nullPosition
    def nullPosition(self):
        '''
        New in Leo 5.5: Return None.
        Using empty positions masks problems in program logic.

        In fact, there are no longer any calls to this method in Leo's core.
        '''
        # c = self
        g.trace('This method is deprecated. Instead, just use None.')
        return None
        # return leoNodes.Position(None)

    #@+node:ekr.20040307104131.3: *5* c.positionExists
    def positionExists(self, p, root=None, trace=False):
        """Return True if a position exists in c's tree"""
        # Important: do not call p.isAncestorOf here.
        trace = (False or trace) and not g.unitTesting
        c = self
        if not p or not p.v:
            if trace:
                g.trace('fail 1', p)
                c.dumpPosition(p)
            return False
        if root and p == root:
            return True
        p = p.copy()
        while p.hasParent():
            old_n, old_v = p._childIndex, p.v
            p.moveToParent()
            if root and p == root:
                return True
            elif not old_v.isNthChildOf(old_n, p.v):
                if trace:
                    g.trace('fail 2', p, g.callers())
                    c.dumpPosition(p)
                return False
        if root:
            exists = p == root
        else:
            exists = p.v.isNthChildOf(p._childIndex, c.hiddenRootNode)
        if trace and not exists:
            g.trace('fail 3', p, g.callers())
            c.dumpPosition(p)
        return exists
    #@+node:ekr.20160427153457.1: *6* c.dumpPosition
    def dumpPosition(self, p):
        '''Dump position p and it's ancestors.'''
        g.trace('=====',p.h, p._childIndex)
        for i, data in enumerate(p.stack):
            v, childIndex = data
            print('%s %s %s' % (i, childIndex, v._headString))
    #@+node:ekr.20040803140033.2: *5* c.rootPosition
    _rootCount = 0

    def rootPosition(self):
        """Return the root position.

        Root position is the first position in the document. Other
        top level positions are siblings of this node.
        """
        c = self
        # g.trace(self._rootCount) ; self._rootCount += 1
        # 2011/02/25: Compute the position directly.
        if c.hiddenRootNode.children:
            v = c.hiddenRootNode.children[0]
            return leoNodes.Position(v, childIndex=0, stack=None)
        else:
            return None

    # For compatibiility with old scripts...
    rootVnode = rootPosition
    findRootPosition = rootPosition
    #@+node:ekr.20131017174814.17480: *5* c.shouldBeExpanded
    def shouldBeExpanded(self, p):
        '''Return True if the node at position p should be expanded.'''
        trace = False and not g.unitTesting
        # if trace: g.trace('=====', p.h)
        c, v = self, p.v
        if not p.hasChildren():
            if trace: g.trace('False: no children:', p.h)
            return False
        # Always clear non-existent positions.
        if trace: g.trace([z.h for z in v.expandedPositions])
        v.expandedPositions = [z for z in v.expandedPositions if c.positionExists(z)]
        if not p.isCloned():
            # Do not call p.isExpanded here! It calls this method.
            if trace: g.trace(p.v.isExpanded(), p.h, 'not cloned: p.v.isExpanded()')
            return p.v.isExpanded()
        if p.isAncestorOf(c.p):
            if trace: g.trace('True:', p.h, 'ancestor of c.p', c.p.h, p._childIndex)
            return True
        if trace:
            g.trace('===== search v.expandedPositions', p.h,
                'len', len(v.expandedPositions))
        for p2 in v.expandedPositions:
            if p == p2:
                if trace:
                    g.trace('True:', p.h, 'in v.expandedPositions')
                return True
        if trace:
            g.trace('False:', p.h)
        return False
    #@+node:ekr.20070609122713: *5* c.visLimit
    def visLimit(self):
        '''
        Return the topmost visible node.
        This is affected by chapters and hoists.
        '''
        c = self; cc = c.chapterController
        if c.hoistStack:
            bunch = c.hoistStack[-1]
            p = bunch.p
            limitIsVisible = not cc or not p.h.startswith('@chapter')
            return p, limitIsVisible
        else:
            return None, None
    #@+node:tbrown.20091206142842.10296: *5* c.vnode2allPositions
    def vnode2allPositions(self, v):
        '''Given a VNode v, find all valid positions p such that p.v = v.

        Not really all, just all for each of v's distinct immediate parents.
        '''
        c = self
        context = v.context # v's commander.
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
        '''Given a VNode v, construct a valid position p such that p.v = v.
        '''
        c = self
        context = v.context # v's commander.
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
    #@+node:ekr.20060906211747.1: *4* c.Setters
    #@+node:ekr.20040315032503: *5* c.appendStringToBody
    def appendStringToBody(self, p, s):
        c = self
        if not s: return
        body = p.b
        assert(g.isUnicode(body))
        s = g.toUnicode(s)
        c.setBodyString(p, body + s)
    #@+node:ekr.20031218072017.2984: *5* c.clearAllMarked
    def clearAllMarked(self):
        c = self
        for p in c.all_unique_positions():
            p.v.clearMarked()
    #@+node:ekr.20031218072017.2985: *5* c.clearAllVisited
    def clearAllVisited(self):
        c = self
        for p in c.all_unique_positions():
            p.v.clearVisited()
            p.v.clearWriteBit()
    #@+node:ekr.20060906211138: *5* c.clearMarked
    def clearMarked(self, p):
        c = self
        p.v.clearMarked()
        g.doHook("clear-mark", c=c, p=p, v=p)
    #@+node:ekr.20040305223522: *5* c.setBodyString
    def setBodyString(self, p, s):
        c = self; v = p.v
        if not c or not v: return
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
                c.setChanged(True)
            c.redraw_after_icons_changed()
    #@+node:ekr.20031218072017.2989: *5* c.setChanged
    def setChanged(self, changedFlag=True, redrawFlag=True):
        '''Set or clear the marker that indicates that the .leo file has been changed.'''
        trace = False and not g.unitTesting # and changedFlag
        if trace: g.trace(changedFlag, redrawFlag, g.callers(2))
        c = self
        if not c.frame:
            return
        c.changed = changedFlag
        if c.loading:
            return # don't update while loading.
        # Clear all dirty bits _before_ setting the caption.
        if not changedFlag:
            for v in c.all_unique_nodes():
                if v.isDirty():
                    v.clearDirty()
        # Do nothing for null frames.
        assert c.gui
        if c.gui.guiName() == 'nullGui':
            return
        if not c.frame.top:
            return
        master = hasattr(c.frame.top, 'leo_master') and c.frame.top.leo_master
        if redrawFlag: # Prevent flash when fixing #387.
            if master:
                # Call LeoTabbedTopLevel.setChanged.
                master.setChanged(c, changedFlag)
            s = c.frame.getTitle()
            # if trace: g.trace(changedFlag,repr(s))
            if len(s) > 2:
                if changedFlag:
                    if s[0] != '*':
                        c.frame.setTitle("* " + s)
                        # if trace: g.trace('(c)',"* " + s)
                else:
                    if s[0: 2] == "* ":
                        c.frame.setTitle(s[2:])
                        # if trace: g.trace('(c)',s[2:])
    #@+node:ekr.20040803140033.1: *5* c.setCurrentPosition
    _currentCount = 0

    def setCurrentPosition(self, p):
        """
        Set the presently selected position. For internal use only.
        Client code should use c.selectPosition instead.
        """
        trace = False and not g.unitTesting
        trace_no_p = True
            # A serious error.
        trace_entry = True
        trace_invalid = False
        c = self
        if not p:
            if trace_no_p: g.trace('===== no p', g.callers())
            return
        if trace and trace_entry:
            c._currentCount += 1
            g.trace('-----------', c._currentCount, p and p.h)
            # g.trace(g.callers(8))
        if c.positionExists(p):
            if c._currentPosition and p == c._currentPosition:
                pass # We have already made a copy.
            else: # Make a copy _now_
                c._currentPosition = p.copy()
        else: # 2011/02/25:
            c._currentPosition = c.rootPosition()
            if trace_invalid: g.trace('Invalid position: %s, root: %s' % (
                repr(p and p.h),
                repr(c._currentPosition and c._currentPosition.h)),
                g.callers())
            # Don't kill unit tests for this kind of problem.

    # For compatibiility with old scripts.
    setCurrentVnode = setCurrentPosition
    #@+node:ekr.20040305223225: *5* c.setHeadString
    def setHeadString(self, p, s):
        '''Set the p's headline and the corresponding tree widget to s.

        This is used in by unit tests to restore the outline.'''
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
    #@+node:ekr.20060906211138.1: *5* c.setMarked
    def setMarked(self, p):
        c = self
        p.v.setMarked()
        g.doHook("set-mark", c=c, p=p, v=p)
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
        else:
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
            body = ''.join(body) + '\n' # Add back one last newline.
            # g.trace(body)
            c.setBodyString(p, body)
            # Don't set the dirty bit: it would just be annoying.
    #@+node:ekr.20110402084740.14490: *3* c.goToNext/PrevHistory
    @cmd('goto-next-history-node')
    def goToNextHistory(self, event=None):
        '''Go to the next node in the history list.'''
        c = self
        c.nodeHistory.goNext()

    @cmd('goto-prev-history-node')
    def goToPrevHistory(self, event=None):
        '''Go to the previous node in the history list.'''
        c = self
        c.nodeHistory.goPrev()
    #@+node:ekr.20090130135126.1: *3* c.Properties
    def __get_p(self):
        c = self
        return c.currentPosition()

    p = property(
        __get_p, # No setter.
        doc="commander current position property")
    #@+node:ekr.20110530082209.18250: *3* c.putHelpFor
    def putHelpFor(self, s, short_title=''):
        '''Helper for various help commands.'''
        c = self
        g.app.gui.put_help(c, s, short_title)
        # s = g.adjustTripleString(s.rstrip(), c.tab_width)
        # if s.startswith('<') and not s.startswith('<<'):
            # pass # how to do selective replace??
        # if g.app.gui.guiName() == 'curses':
            # g.app.gui.put_help(s, short_title)
            # return
        # pc = g.app.pluginsController
        # table = (
            # 'viewrendered3.py',
            # 'viewrendered2.py',
            # 'viewrendered.py',
        # )
        # for name in table:
            # if pc.isLoaded(name):
                # vr = pc.loadOnePlugin(name)
                # break
        # else:
            # vr = pc.loadOnePlugin('viewrendered.py')
        # if g.unitTesting:
            # assert vr # For unit testing.
        # if vr:
            # kw = {
                # 'c': c,
                # 'flags': 'rst',
                # 'kind': 'rst',
                # 'label': '',
                # 'msg': s,
                # 'name': 'Apropos',
                # 'short_title': short_title,
                # 'title': ''}
            # vr.show_scrolled_message(tag='Apropos', kw=kw)
            # c.bodyWantsFocus()
            # if g.unitTesting:
                # vr.close_rendering_pane(event={'c': c})
        # else:
            # g.es(s)
    #@+node:ekr.20140717074441.17770: *3* c.recreateGnxDict
    def recreateGnxDict(self):
        '''Recreate the gnx dict prior to refreshing nodes from disk.'''
        trace = False and not g.unitTesting
        c, d = self, {},
        for v in c.all_unique_nodes():
            gnxString = v.fileIndex
            assert g.isUnicode(gnxString)
            d[gnxString] = v
            if trace or g.trace_gnxDict: g.trace(c.shortFileName(), gnxString, v)
        c.fileCommands.gnxDict = d
    #@+node:ekr.20130823083943.12559: *3* c.recursiveImport
    def recursiveImport(self, dir_, kind,
        recursive=True,
        safe_at_file=True,
        theTypes=None,
    ):
        #@+<< docstring >>
        #@+node:ekr.20130823083943.12614: *4* << docstring >>
        '''
        Recursively import all python files in a directory and clean the results.

        Parameters::
            dir_              The root directory or file to import.
            kind              One of ('@clean','@edit','@file','@nosent').
            recursive=True    True: recurse into subdirectories.
            safe_at_file=True True: produce @@file nodes instead of @file nodes.
            theTypes=None     A list of file extensions to import.
                              None is equivalent to ['.py']

        This method cleans imported files as follows:

        - Replace backslashes with forward slashes in headlines.
        - Remove empty nodes.
        - Add @path directives that reduce the needed path specifiers in descendant nodes.
        - Add @file to nodes or replace @file with @@file.
        '''
        #@-<< docstring >>
        c = self
        if g.os_path_exists(dir_):
            # Import all files in dir_ after c.p.
            try:
                import leo.core.leoImport as leoImport
                cc = leoImport.RecursiveImportController(c, kind,
                    recursive=recursive,
                    safe_at_file=safe_at_file,
                    theTypes=['.py'] if not theTypes else theTypes,
                )
                cc.run(dir_)
            finally:
                c.redraw()
        else:
            g.es_print('Does not exist: %s' % (dir_))
    #@+node:ekr.20031218072017.2990: *3* c.Selecting & Updating
    #@+node:ekr.20031218072017.2991: *4* c.redrawAndEdit
    def redrawAndEdit(self, p, selectAll=False, selection=None, keepMinibuffer=False):
        '''Redraw the screen and edit p's headline.'''
        c, k = self, self.k
        c.redraw(p) # This *must* be done now.
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
    #@+node:ekr.20031218072017.2992: *4* c.endEditing (calls tree.endEditLabel)
    # Ends the editing in the outline.

    def endEditing(self):
        trace = False and not g.unitTesting
        c = self
        p = c.p
        if p:
            if trace: g.trace(p.h, g.callers())
            c.frame.tree.endEditLabel()
        # The following code would be wrong; c.endEditing is a utility method.
        # k = c.k
        # if k:
            # k.setDefaultInputState()
            # # Recolor the *body* text, **not** the headline.
            # k.showStateAndMode(w=c.frame.body.wrapper)
    #@+node:ekr.20031218072017.2997: *4* c.selectPosition
    select_position_warning_dict = {}

    def selectPosition(self, p, **kwargs):
        """Select a new position."""
        trace = False and not g.unitTesting
        trace_no_p = True and not g.app.batchMode
            # A serious error.
        if 'enableRedrawFlag' in kwargs:
            caller = g.callers(1)
            if caller not in self.select_position_warning_dict:
                self.select_position_warning_dict[caller]=True
                print('c.selectPosition: enableRedrawFlag is deprecated', caller)
        c = self
        cc = c.chapterController
        if not p:
            if trace and trace_no_p: g.trace('===== no p', g.callers())
            return
        # 2016/04/20: check cc.selectChapterLockout.
        if cc and not cc.selectChapterLockout:
            cc.selectChapterForPosition(p)
                # Important: selectChapterForPosition calls c.redraw
                # if the chapter changes.
            if trace: g.trace(p and p.h, g.callers())
        # 2012/03/08: De-hoist as necessary to make p visible.
        if c.hoistStack:
            while c.hoistStack:
                bunch = c.hoistStack[-1]
                if c.positionExists(p, bunch.p):
                    break
                else:
                    bunch = c.hoistStack.pop()
                    if trace: g.trace('unhoist', bunch.p.h)
        if trace:
            if c.positionExists(p):
                g.trace('****', p.h)
            else:
                g.trace('**** does not exist: %s' % (p and p.h))
        c.frame.tree.select(p)
        # New in Leo 4.4.2.
        c.setCurrentPosition(p)
            # Do *not* test whether the position exists!
            # We may be in the midst of an undo.
        # Never do this: it is terrible design.
            # if redraw_flag and enableRedrawFlag:
                # c.redraw()

    # Compatibility, but confusing.
    selectVnode = selectPosition
    #@+node:ekr.20060923202156: *4* c.onCanvasKey
    def onCanvasKey(self, event):
        '''Navigate to the next headline starting with ch = event.char.
        If ch is uppercase, search all headlines; otherwise search only visible headlines.
        This is modelled on Windows explorer.'''
        # g.trace(event and event.char)
        if not event or not event.char or not event.char.isalnum():
            return
        c = self; p = c.p; p1 = p.copy()
        invisible = c.config.getBool('invisible_outline_navigation')
        ch = event.char if event else ''
        allFlag = ch.isupper() and invisible # all is a global (!?)
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
                if p == p1: # Never try to match the same position.
                    # g.trace('failed',extend2)
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
            # g.trace('extend',extend,'extend2',extend2,'navPrefix',c.navPrefix,'p',p.h)
        else:
            c.navTime = None
            c.navPrefix = ''
        c.treeWantsFocus()
    #@+node:ekr.20061002095711.1: *5* c.navQuickKey
    def navQuickKey(self):
        '''return true if there are two quick outline navigation keys
        in quick succession.

        Returns False if @float outline_nav_extend_delay setting is 0.0 or unspecified.'''
        c = self
        deltaTime = c.config.getFloat('outline_nav_extend_delay')
        if deltaTime in (None, 0.0):
            return False
        else:
            nearTime = c.navTime and time.time() - c.navTime < deltaTime
            return nearTime
    #@+node:ekr.20061002095711: *5* c.navHelper
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
    #@+node:ville.20090525205736.12325: *4* c.getSelectedPositions
    def getSelectedPositions(self):
        """ Get list (PosList) of currently selected positions

        So far only makes sense on qt gui (which supports multiselection)
        """
        c = self
        return c.frame.tree.getSelectedPositions()
    #@+node:ekr.20131016084446.16724: *3* c.setComplexCommand
    def setComplexCommand(self, commandName):
        '''Make commandName the command to be executed by repeat-complex-command.'''
        c = self
        c.k.mb_history.insert(0, commandName)
    #@+node:ekr.20031218072017.2999: *3* c.Syntax coloring interface
    #@+at These routines provide a convenient interface to the syntax colorer.
    #@+node:ekr.20031218072017.3000: *4* c.updateSyntaxColorer
    def updateSyntaxColorer(self, v):
        self.frame.body.updateSyntaxColorer(v)
    #@+node:ekr.20090103070824.12: *3* c.Time stamps
    #@+node:ekr.20090103070824.11: *4* c.checkFileTimeStamp
    def checkFileTimeStamp(self, fn):
        '''
        Return True if the file given by fn has not been changed
        since Leo read it or if the user agrees to overwrite it.
        '''
        c = self
        if g.app.externalFilesController:
            return g.app.externalFilesController.check_overwrite(c, fn)
        else:
            return True
    #@+node:ekr.20090103070824.9: *4* c.setFileTimeStamp
    def setFileTimeStamp(self, fn):
        '''Update the timestamp for fn..'''
        # c = self
        if g.app.externalFilesController:
            g.app.externalFilesController.set_time(fn)
    #@+node:vitalije.20170708172746.1: *3* c.editShortcut
    @cmd('edit-shortcut')
    def editShortcut(self, event=None):
        k = self.k
        if k.isEditShortcutSensible():
            self.k.setState('input-shortcut', 'input-shortcut')
            g.es('Press desired key combination')
        else:
            g.es('No possible shortcut in selected body line/headline')
            g.es('Select @button, @command, @shortcuts or @mode node and run it again.')
    #@+node:vitalije.20170713174950.1: *3* c.editOneSetting
    @cmd('edit-setting')
    def editOneSetting(self, event=None):
        '''Opens correct dialog for selected setting type'''
        c = self; p = c.p; func = None
        if p.h.startswith('@font'):
            func = c.commandsDict.get('show-fonts')
        elif p.h.startswith('@color '):
            func = c.commandsDict.get('show-color-wheel')
        elif p.h.startswith(('@shortcuts','@button','@command')):
            c.editShortcut()
            return
        else:
            g.es('not in a setting node')
            return
        if func:
            event = g.app.gui.create_key_event(c, None, None, None)
            func(event)
    #@+node:bobjack.20080509080123.2: *3* c.universalCallback & minibufferCallback
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
            trace = False and not g.unitTesting
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
                if trace: g.trace(function, keywords)
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
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo

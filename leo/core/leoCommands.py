# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20031218072017.2810: * @file leoCommands.py
#@@first
    # Needed because of unicode characters in tests.

#@@language python
#@@tabwidth -4
#@@pagewidth 70

#@+<< imports >>
#@+node:ekr.20040712045933: ** << imports >> (leoCommands)
import leo.core.leoGlobals as g

# if g.app and g.app.use_psyco:
    # # g.pr("enabled psyco classes",__file__)
    # try: from psyco.classes import *
    # except ImportError: pass

# The leoCommands ctor now does these imports.
# This breaks circular dependencies.

    # import leo.core.leoAtFile as leoAtFile
    # import leo.core.leoCache as leoCache
    # import leo.core.leoChapters as leoChapters
    # import leo.core.leoEditCommands as leoEditCommands
    # import leo.core.leoKeys as leoKeys
    # import leo.core.leoFileCommands as leoFileCommands
    # import leo.core.leoImport as leoImport
    # import leo.core.leoRst as leoRst
    # import leo.core.leoShadow as leoShadow
    # import leo.core.leoTangle as leoTangle
    # import leo.core.leoTest as leoTest
    # import leo.core.leoUndo as leoUndo

import leo.core.leoNodes as leoNodes

# import leo.external.pickleshare as pickleshare

# import hashlib
import imp
import itertools
import keyword
import os
import re
import subprocess
import sys
import tempfile
import time
import tokenize # for Check Python command
# import unittest

try:
    import tabnanny # for Check Python command # Does not exist in jython
except ImportError:
    tabnanny = None

# The following import _is_ used.
import token    # for Check Python command
#@-<< imports >>

#@+others
#@+node:ekr.20041118104831: ** class Commands
class Commands (object):
    """A class that implements most of Leo's commands."""
    #@+others
    #@+node:ekr.20031218072017.2811: *3*  c.Birth & death
    #@+node:ekr.20031218072017.2812: *4* c.__init__ & helpers
    def __init__(self,fileName,relativeFileName=None,gui=None,previousSettings=None):

        trace = (False or g.trace_startup) and not g.unitTesting
        tag = 'Commands.__init__ %s' % (g.shortFileName(fileName))
        if trace and g.trace_startup: print('\n%s %s' % (tag,g.callers()))
        c = self
        if trace and not g.trace_startup:
            t1 = time.clock()
        # Official ivars.
        self._currentPosition = self.nullPosition()
        self._topPosition     = self.nullPosition()
        self.frame = None
        self.gui = gui or g.app.gui
        self.ipythonController = None
            # Set only by the ipython plugin.

        # The order of these calls does not matter.
        c.initCommandIvars()
        c.initDebugIvars()
        c.initDocumentIvars()
        c.initEventIvars()
        c.initFileIvars(fileName,relativeFileName)
        c.initOptionsIvars()
        c.initObjectIvars()

        # Init the settings *before* initing the objects.
        import leo.core.leoConfig as leoConfig
        self.config = leoConfig.LocalConfigManager(c,previousSettings)
        g.app.config.setIvarsFromSettings(c)

        # Initialize all subsidiary objects, including subcommanders.
        c.initObjects(self.gui)

        assert c.frame
        assert c.frame.c

        if trace and not g.trace_startup:
            g.printDiffTime('%s: after controllers created' % (tag),t1)

        # Complete the init!
        c.finishCreate()

        if trace and not g.trace_startup:
            g.printDiffTime('%s: after c.finishCreate' % (tag),t1)
    #@+node:ekr.20120217070122.10475: *5* c.computeWindowTitle
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
    #@+node:ekr.20120217070122.10473: *5* c.initCommandIvars
    def initCommandIvars(self):

        '''Init ivars used while executing a command.'''

        self.commandsDict = {}
        self.disableCommandsMessage = ''
            # The presence of this message disables all commands.
        self.hookFunction = None
            #
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
    #@+node:ekr.20120217070122.10466: *5* c.initDebugIvars
    def initDebugIvars (self):

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
        self.timeStampDict = {}
            # Keys are file names, values are time stamps.
        self.user_dict = {}
            # Non-persistent dictionary for free use by scripts and plugins.
        
    #@+node:ekr.20120217070122.10467: *5* c.initEventIvars
    def initEventIvars(self):

        self.configInited = False
        self.doubleClickFlag = False
        self.exists = True
            # Indicate that this class exists and has not been destroyed.
            # Do this early in the startup process so we can call hooks.
        self.hasFocusWidget = None
        self.idle_callback = None
            # For c.idle_focus_helper.
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
        self.requestedFocusWidget = None
        self.requestRedrawFlag = False
        self.requestedIconify = '' # 'iconify','deiconify'
        self.requestRecolorFlag = False
    #@+node:ekr.20120217070122.10472: *5* c.initFileIvars
    def initFileIvars(self,fileName,relativeFileName):

        # if not fileName: fileName = ''
        # if not relativeFileName: relativeFileName = ''

        self.changed = False
            # True: the ouline has changed since the last save.
        self.ignored_at_file_nodes = []
            # List of nodes for error dialog.
        self.import_error_nodes = []
            #
        self.mFileName = fileName or ''
            # Do _not_ use os_path_norm: it converts an empty path to '.' (!!)
        self.mRelativeFileName = relativeFileName or ''
            #
        self.openDirectory = None
    #@+node:ekr.20120217070122.10469: *5* c.initOptionsIvars
    def initOptionsIvars(self):

        # print('c.initOptionsIvars')

        self.fixed = False
        self.fixedWindowPosition = []
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
        self.use_focus_border = False
    #@+node:ekr.20120217070122.10468: *5* c.initObjectIvars
    def initObjectIvars (self):

        # These ivars are set later by leoEditCommands.createEditCommanders
        self.abbrevCommands  = None
        self.bufferCommands  = None
        self.editCommands    = None
        self.db = {} # May be set to a PickleShare instance later.
        self.chapterCommands = None
        self.controlCommands = None
        self.debugCommands   = None
        self.editFileCommands = None
        self.helpCommands = None
        self.keyHandler = self.k = None
        self.keyHandlerCommands = None
        self.killBufferCommands = None
        self.leoCommands = None
        self.macroCommands = None
        self.miniBufferWidget = None
        self.queryReplaceCommands = None
        self.rectangleCommands = None
        self.registerCommands = None
        self.searchCommands = None
        self.spellCommands = None
        self.leoTestManager = None
    #@+node:ekr.20120217070122.10470: *5* c.initObjects
    def initObjects(self,gui):

        trace = (False or g.trace_startup) and not g.unitTesting
        c = self

        if trace:
            print('g.initObjects %s %s' % (
                c.shortFileName(),g.app.gui))

        self.hiddenRootNode = leoNodes.vnode(context=c)
        self.hiddenRootNode.setHeadString('<hidden root vnode>')

        # Create the gui frame.
        title = c.computeWindowTitle(c.mFileName)

        if not g.app.initing:
            g.doHook("before-create-leo-frame",c=c)

        self.frame = gui.createLeoFrame(c,title)
        assert self.frame
        assert self.frame.c == c

        self.nodeHistory = nodeHistory(c)

        self.initConfigSettings()

        c.setWindowPosition() # Do this after initing settings.

        # Break circular import dependencies by importing here.
        # These imports take almost 3/4 sec in the leoBridge.
        import leo.core.leoAtFile as leoAtFile
        import leo.core.leoCache as leoCache
        import leo.core.leoChapters as leoChapters
        import leo.core.leoEditCommands as leoEditCommands
        import leo.core.leoKeys as leoKeys
        import leo.core.leoFileCommands as leoFileCommands
        import leo.core.leoImport as leoImport
        import leo.core.leoRst as leoRst
        import leo.core.leoShadow as leoShadow
        import leo.core.leoTangle as leoTangle
        import leo.core.leoTest as leoTest
        import leo.core.leoUndo as leoUndo

        self.keyHandler = self.k = leoKeys.keyHandlerClass(c)
        self.chapterController  = leoChapters.chapterController(c)
        self.shadowController   = leoShadow.shadowController(c)
        self.fileCommands       = leoFileCommands.fileCommands(c)
        self.atFileCommands     = leoAtFile.atFile(c)
        self.importCommands     = leoImport.leoImportCommands(c)
        self.rstCommands        = leoRst.rstCommands(c)
        self.tangleCommands     = leoTangle.tangleCommands(c)
        self.testManager        = leoTest.TestManager(c)

        self.editCommandsManager = leoEditCommands.EditCommandsManager(c)
        self.editCommandsManager.createEditCommanders()

        self.cacher = leoCache.cacher(c)
        self.cacher.initFileDB(self.mFileName)
        self.undoer = leoUndo.undoer(self)

        import leo.plugins.free_layout as free_layout
        self.free_layout = free_layout.FreeLayoutController(c)
    #@+node:ekr.20031218072017.2814: *4* c.__repr__ & __str__
    def __repr__ (self):

        return "Commander %d: %s" % (id(self),repr(self.mFileName))

    __str__ = __repr__
    #@+node:ekr.20050920093543: *4* c.finishCreate & helper
    def finishCreate (self):

        '''Finish creating the commander and all sub-objects.

        This is the last step in the startup process.'''

        # trace = (False or g.trace_startup) and not g.unitTesting
        # if trace: print('c.finishCreate')
        c = self
        k = c.k
        # p = c.p
        assert c.gui
        assert k

        c.frame.finishCreate()
        c.miniBufferWidget = c.frame.miniBufferWidget
            # Will be None for nullGui.

        # This costs little.
        c.commandsDict = c.editCommandsManager.finishCreateEditCommanders()
        self.rstCommands.finishCreate()

        # copy global commands to this controller    
        for name,f in g.app.global_commands_dict.items():
            k.registerCommand(name,
                shortcut=None,func=f,pane='all',verbose=False)        

        k.finishCreate()

        if not c.gui.isNullGui:
            g.registerHandler('idle',c.idle_focus_helper)

        c.frame.menu.finishCreate()
        c.frame.log.finishCreate()
        c.undoer.clearUndoState()
            # Menus must exist at this point.

        # Do not call chapterController.finishCreate here:
        # It must be called after the first real redraw.
        c.bodyWantsFocus()
    #@+node:ekr.20051007143620: *5* printCommandsDict
    def printCommandsDict (self):

        c = self

        print('Commands...')
        for key in sorted(c.commandsDict):
            command = c.commandsDict.get(key)
            print('%30s = %s' % (
                key,g.choose(command,command.__name__,'<None>')))
        print('')
    #@+node:ekr.20041130173135: *4* c.hash
    # This is a bad idea.
    def hash (self):
        c = self
        if c.mFileName:
            return c.os_path_finalize(c.mFileName).lower()
        else:
            return 0
    #@+node:ekr.20110509064011.14563: *4* c.idle_focus_helper
    idle_focus_count = 0

    def idle_focus_helper (self,tag,keys):

        '''An idle-tme handler that ensures that focus is *somewhere*.'''

        trace = False and not g.unitTesting
        verbose = False # False: only print surprises.
        active = False # True: actually change the focus.
        c = self
        assert tag == 'idle'
        if g.app.unitTesting or keys.get('c') != c:
            return
        self.idle_focus_count += 1
        if c.in_qt_dialog:
            if trace and verbose: g.trace('in_qt_dialog')
            return
        if c.idle_callback:
            if trace: g.trace('calling c.idle_callback',c.idle_callback.__name__)
            c.idle_callback()
            c.idle_callback = None
            return
        w = g.app.gui.get_focus()
        if w:
            if trace:
                g.trace(self.idle_focus_count,w)
        elif g.app.gui.active:
            if trace:
                g.trace('%s no focus -> body' % (self.idle_focus_count))
            if active:
                c.bodyWantsFocusNow()
    #@+node:ekr.20081005065934.1: *4* c.initAfterLoad
    def initAfterLoad (self):

        '''Provide an offical hook for late inits of the commander.'''

        pass
    #@+node:ekr.20090213065933.6: *4* c.initConfigSettings
    def initConfigSettings (self):

        '''Init all cached commander config settings.'''

        trace = (False or g.trace_startup) and not g.unitTesting
        c = self

        if trace:
            print('c.initConfigSettings: c.configInited: %s %s' % (
                c.configInited,c.shortFileName()))

        getBool = c.config.getBool
        getColor = c.config.getColor
        getData  = c.config.getData
        getInt = c.config.getInt

        c.autoindent_in_nocolor     = getBool('autoindent_in_nocolor_mode')
        c.collapse_nodes_after_move = getBool('collapse_nodes_after_move')
            # Patch by nh2: 0004-Add-bool-collapse_nodes_after_move-option.patch
        c.collapse_on_lt_arrow      = getBool('collapse_on_lt_arrow',default=True)
            # 2011/11/09: An excellent, subliminal, improvement.
        c.contractVisitedNodes      = getBool('contractVisitedNodes')
        c.fixed                     = getBool('fixedWindow',default=False)
        c.fixedWindowPositionData   = getData('fixedWindowPosition')
        c.focus_border_color        = getColor('focus_border_color') or 'red'
        c.focus_border_command_state_color = getColor(
            'focus_border_command_state_color') or 'blue'
        c.focus_border_overwrite_state_color = getColor(
            'focus_border_overwrite_state_color') or 'green'
        c.focus_border_width        = getInt('focus_border_width') or 1 # pixels
        c.outlineHasInitialFocus    = getBool('outline_pane_has_initial_focus')
        # c.showMinibuffer            = getBool('useMinibuffer')
            # This option is a bad idea.
        c.page_width                = getInt('page_width') or 132
            # 2012/02/27: this appears to be a fix of an *ancient* bug.
        c.putBitsFlag               = getBool('put_expansion_bits_in_leo_files',default=True)
        c.sparse_move               = getBool('sparse_move_outline_left')
        c.sparse_find               = getBool('collapse_nodes_during_finds')
        c.sparce_spell              = getBool('collapse_nodes_while_spelling')
        c.stayInTreeAfterSelect     = getBool('stayInTreeAfterSelect')
        c.stayInTreeAfterEdit       = getBool('stayInTreeAfterEditHeadline')
        c.smart_tab                 = getBool('smart_tab')
            # Note: there is also a smart_auto_indent setting.
        c.tab_width                 = getInt('tab_width') or -4
        c.use_body_focus_border     = getBool('use_body_focus_border',default=True)
        c.use_focus_border          = getBool('use_focus_border',default=True)
        c.write_script_file         = getBool('write_script_file')

        # g.trace('smart %s, tab_width %s' % (c.smart_tab, c.tab_width))
        # g.trace(c.sparse_move)
    #@+node:ekr.20090213065933.7: *4* c.setWindowPosition
    def setWindowPosition (self):

        c = self

        # g.trace(c.fixed,c.fixedWindowPosition)

        if c.fixedWindowPositionData:
            try:
                aList = [z.strip() for z in c.fixedWindowPositionData if z.strip()]
                w,h,l,t = aList
                c.fixedWindowPosition = int(w),int(h),int(l),int(t)
            except Exception:
                g.error('bad @data fixedWindowPosition',
                    repr(self.fixedWindowPosition))
        else:
            c.windowPosition = 500,700,50,50 # width,height,left,top.
    #@+node:ekr.20031218072017.2817: *3*  c.doCommand
    command_count = 0

    def doCommand (self,command,label,event=None):

        """Execute the given command, invoking hooks and catching exceptions.

        The code assumes that the "command1" hook has completely handled the command if
        g.doHook("command1") returns False.
        This provides a simple mechanism for overriding commands."""

        trace = False and not g.unitTesting
        c = self ; p = c.p
        commandName = command and command.__name__
        c.setLog()

        self.command_count += 1
        if not g.app.unitTesting and c.config.getBool('trace_doCommand'):
            g.trace(commandName)

        # The presence of this message disables all commands.
        if c.disableCommandsMessage:
            g.blue(c.disableCommandsMessage)
            return # (for Tk) 'break' # Inhibit all other handlers.

        if c.exists and c.inCommand and not g.unitTesting:
            # g.trace('inCommand',c)
            g.app.commandInterruptFlag = True
            g.error('ignoring command: already executing a command.')
            return # (for Tk) 'break'

        g.app.commandInterruptFlag = False

        if label and event is None: # Do this only for legacy commands.
            if label == "cantredo": label = "redo"
            if label == "cantundo": label = "undo"
            g.app.commandName = label

        if not g.doHook("command1",c=c,p=p,v=p,label=label):
            try:
                c.inCommand = True
                if trace: g.trace('start',command)
                val = command(event)
                if trace: g.trace('end',command)
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

        # Be careful: the command could destroy c.
        if c and c.exists:
            p = c.p
            g.doHook("command2",c=c,p=p,v=p,label=label)

        return # (for Tk) "break" # Inhibit all other handlers.
    #@+node:ekr.20080514131122.20: *4* c.outerUpdate
    def outerUpdate (self):

        trace = False and not g.unitTesting
        verbose = False ; traceFocus = True
        c = self ; aList = []
        if not c.exists or not c.k:
            return
        # Suppress any requested redraw until we have iconified or diconified.
        redrawFlag = c.requestRedrawFlag
        c.requestRedrawFlag = False
        if trace and (verbose or aList):
            g.trace('**start',c.shortFileName() or '<unnamed>',g.callers(5))
        if c.requestBringToFront:
            if hasattr(c.frame,'bringToFront'):
                ### c.frame.bringToFront()
                c.requestBringToFront.frame.bringToFront()
                    # c.requestBringToFront is a commander.
            c.requestBringToFront = None
        # The iconify requests are made only by c.bringToFront.
        if c.requestedIconify == 'iconify':
            if verbose: aList.append('iconify')
            c.frame.iconify()
        if c.requestedIconify == 'deiconify':
            if verbose: aList.append('deiconify')
            c.frame.deiconify()
        if redrawFlag:
            if trace: g.trace('****','tree.drag_p',c.frame.tree.drag_p)
            # A hack: force the redraw, even if we are dragging.
            aList.append('*** redraw')
            c.frame.tree.redraw_now(forceDraw=True)
        if c.requestRecolorFlag:
            aList.append('%srecolor' % (
                g.choose(c.incrementalRecolorFlag,'','full ')))
            # This should be the only call to c.recolor_now.
            c.recolor_now(incremental=c.incrementalRecolorFlag)
        if c.requestedFocusWidget:
            w = c.requestedFocusWidget
            if traceFocus: aList.append('focus: %s' % w)
            c.set_focus(w)
        else:
            # We must not set the focus to the body pane here!
            # That would make nested calls to c.outerUpdate significant.
            pass
        if trace and (verbose or aList):
            g.trace('** end',aList)
        c.incrementalRecolorFlag = False
        c.requestRecolorFlag = None
        c.requestRedrawFlag = False
        c.requestedFocusWidget = None
        c.requestedIconify = ''
        mods = g.childrenModifiedSet
        if mods:
            #print(mods)
            g.doHook("childrenModified",c=c, nodes = mods)
            mods.clear()
        mods = g.contentModifiedSet
        if mods:
            #print(mods)
            g.doHook("contentModified",c=c, nodes = mods)
            mods.clear()
    #@+node:ekr.20110510052422.14618: *3* c.alert
    def alert(self,message):

        c = self

        # The unit tests just tests the args.
        if not g.unitTesting:
            g.es(message)
            g.app.gui.alert(c,message)
    #@+node:ekr.20110605040658.17005: *3* c.check_event
    def check_event (self,event):

        trace = False and not g.unitTesting

        c,k = self,self.k

        import leo.core.leoGui as leoGui

        def test(val,message):
            if trace:
                if g.unitTesting:
                    assert val,message
                else:
                    if not val: print('check_event',message)

        if not event:
            return

        isLeoKeyEvent = isinstance(event,leoGui.leoKeyEvent)
        stroke = event.stroke
        got = event.char

        if trace: g.trace('plain: %s, stroke: %s, char: %s' % (
            k.isPlainKey(stroke),repr(stroke),repr(event.char)))

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

        test(isLeoKeyEvent,'not leo event: %s, callers: %s' % (
            repr(event),g.callers()))

        test(expected == got,'stroke: %s, expected char: %s, got: %s' % (
                repr(stroke),repr(expected),repr(got)))
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
        undoData = u.beforeChangeGroup(u_node,undoType)
        for idx,head in enumerate(heads):
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
                    u.afterInsertNode(n,undoType2,u_d) 
                    parent = n
            else: # else, simply create child nodes each round
                if not forcecreate:
                    for ch in parent.children():
                        if ch.h == head:
                            parent = ch
                            break
                if parent.h != head or forcecreate:
                    u_d = u.beforeInsertNode(parent)
                    n = parent.insertAsLastChild()
                    n.h = head
                    u.afterInsertNode(n, undoType2, u_d)
                    parent = n
        u.afterChangeGroup(parent,undoType,undoData)
        return parent # actually the last created/found position
    #@+node:ekr.20100802121531.5804: *3* c.deletePositionsInList
    def deletePositionsInList (self,aList,callback=None):

        '''Delete all vnodes corresponding to the positions in aList.
        If a callback is given, the callback is called for every node in the list.
        
        The callback takes one explicit argument, p. As usual, the callback can bind
        values using keyword arguments.
        '''
        
        trace = False and not g.unitTesting
        c = self
        # Verify all positions *before* altering the tree.
        aList2 = []
        for p in aList:
            if c.positionExists(p):
                aList2.append(p.copy())
            else:
                g.trace('invalid position',p)
        # Delete p.v, **if possible** for all positions p in aList2.
        if callback:
            for p in aList2:
                callback(p)
        else:
            for p in aList2:
                v = p.v
                parent_v = p.stack[-1][0] if p.stack else c.hiddenRootNode
                # import leo.core.leoNodes as leoNodes
                # assert isinstance(parent_v,leoNodes.vnode),parent_v
                if v in parent_v.children:
                    childIndex = parent_v.children.index(v)
                    if trace: g.trace('deleting',parent_v,childIndex,v)
                    v._cutLink(childIndex,parent_v)
                else:
                    if trace: g.trace('already deleted',parent_v,v)
    #@+node:ekr.20080901124540.1: *3* c.Directive scanning
    # These are all new in Leo 4.5.1.
    #@+node:ekr.20080827175609.39: *4* c.scanAllDirectives
    def scanAllDirectives(self,p=None):

        '''Scan p and ancestors for directives.

        Returns a dict containing the results, including defaults.'''

        trace = False and not g.unitTesting
        c = self ; p = p or c.p

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

        d = {
            "delims"        : lang_dict.get('delims'),
            "encoding"      : d.get('encoding'),
            "language"      : lang_dict.get('language'),
            "lineending"    : d.get('lineending'),
            "pagewidth"     : d.get('pagewidth'),
            "path"          : d.get('path'), # Redundant: or g.getBaseDirectory(c),
            "tabwidth"      : d.get('tabwidth'),
            "pluginsList"   : [], # No longer used.
            "wrap"          : d.get('wrap'),
        }

        if trace: g.trace(lang_dict.get('language'),g.callers())

        # g.trace(d.get('tabwidth'))

        return d
    #@+node:ekr.20080828103146.15: *4* c.scanAtPathDirectives
    def scanAtPathDirectives(self,aList):

        '''Scan aList for @path directives.
        Return a reasonable default if no @path directive is found.'''

        trace = False and not g.unitTesting
        verbose = True

        c = self
        c.scanAtPathDirectivesCount += 1 # An important statistic.
        if trace and verbose: g.trace('**entry',g.callers(4))

        # Step 1: Compute the starting path.
        # The correct fallback directory is the absolute path to the base.
        if c.openDirectory:  # Bug fix: 2008/9/18
            base = c.openDirectory
        else:
            base = g.app.config.relative_path_base_directory
            if base and base == "!":    base = g.app.loadDir
            elif base and base == ".":  base = c.openDirectory

        if trace and verbose:
            g.trace('base   ',base)
            g.trace('loadDir',g.app.loadDir)

        absbase = c.os_path_finalize_join(g.app.loadDir,base)

        if trace and verbose: g.trace('absbase',absbase)

        # Step 2: look for @path directives.
        paths = []
        for d in aList:
            # Look for @path directives.
            path = d.get('path')
            warning = d.get('@path_in_body')
            if trace and path:
                g.trace('**** d',d)
                g.trace('**** @path path',path)
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
            g.printList(paths,tag='c.scanAtPathDirectives: raw paths')

        path = c.os_path_finalize_join(*paths)

        if trace and verbose: g.trace('joined path:',path)
        if trace: g.trace('returns',path)

        return path or g.getBaseDirectory(c)
            # 2010/10/22: A useful default.
    #@+node:ekr.20080828103146.12: *4* c.scanAtRootDirectives
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
    #@+node:ekr.20080922124033.5: *4* c.os_path_finalize and c.os_path_finalize_join
    def os_path_finalize (self,path,**keys):

        c = self
        keys['c'] = c
        return g.os_path_finalize(path,**keys)

    def os_path_finalize_join (self,*args,**keys):

        c = self
        keys['c'] = c
        return g.os_path_finalize_join(*args,**keys)
    #@+node:ekr.20081006100835.1: *4* c.getNodePath & c.getNodeFileName
    # Not used in Leo's core.
    # Used by the UNl plugin.  Does not need to create a path.
    def getNodePath (self,p):

        '''Return the path in effect at node p.'''

        c = self
        aList = g.get_directives_dict_list(p)
        path = c.scanAtPathDirectives(aList)
        return path

    # Not used in Leo's core.
    def getNodeFileName (self,p):

        '''Return the full file name at node p,
        including effects of all @path directives.

        Return None if p is no kind of @file node.'''

        c = self
        path = g.scanAllAtPathDirectives(c,p)
        name = ''
        for p in p.self_and_parents():
            name = p.anyAtFileNodeName()
            if name: break

        if name:
            name = g.os_path_finalize_join(path,name)
        return name
    #@+node:ekr.20091211111443.6265: *3* c.doBatchOperations & helpers
    def doBatchOperations (self,aList=None):
        # Validate aList and create the parents dict
        if aList is None: aList = []
        ok, d = self.checkBatchOperationsList(aList)
        if not ok:
            return g.error('do-batch-operations: invalid list argument')

        for v in list(d.keys()):
            aList2 = d.get(v,[])
            if aList2:
                aList.sort()
                for n,op in aList2:
                    if op == 'insert':
                        g.trace('insert:',v.h,n)
                    else:
                        g.trace('delete:',v.h,n)
    #@+node:ekr.20091211111443.6266: *4* checkBatchOperationsList
    def checkBatchOperationsList(self,aList):
        ok = True ; d = {}
        for z in aList:
            try:
                op,p,n = z
                ok= (op in ('insert','delete') and
                    isinstance(p,leoNodes.position) and
                    type(n) == type(9))
                if ok:
                    aList2 = d.get(p.v,[])
                    data = n,op
                    aList2.append(data)
                    d[p.v] = aList2
            except ValueError:
                ok = False
            if not ok: break
        return ok,d
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
    #@+node:ekr.20051106040126: *3* c.executeMinibufferCommand
    def executeMinibufferCommand (self,commandName):

        c = self ; k = c.k

        func = c.commandsDict.get(commandName)

        if func:
            event = g.app.gui.create_key_event(c,None,None,None)
            k.masterCommand(commandName=None,event=event,func=func)
            return k.funcReturn
        else:
            g.error('no such command: %s %s' % (commandName,g.callers()))
            return None
    #@+node:ekr.20091002083910.6106: *3* c.find...
    #@+<< poslist doc >>
    #@+node:bob.20101215134608.5898: *4* << poslist doc >>
    #@@nocolor-node
    #@+at 
    # List of positions 
    # 
    # Functions find_h() and find_b() both return an instance of poslist.
    # 
    # Methods filter_h() and filter_b() refine a poslist.
    # 
    # Method children() generates a new poslist by descending one level from
    # all the nodes in a poslist.
    # 
    # A chain of poslist method calls must begin with find_h() or find_b().
    # The rest of the chain can be any combination of filter_h(),
    # filter_b(), and children(). For example:
    # 
    #     pl = c.find_h('@file.*py').children().filter_h('class.*').filter_b('import (.*)')
    # 
    # For each position, pos, in the poslist returned, find_h() and
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
    #@-<< poslist doc >>
    #@+node:ville.20090311190405.70: *4* c.find_h
    def find_h(self, regex, flags = re.IGNORECASE):
        """ Return list (a poslist) of all nodes where zero or more characters at
        the beginning of the headline match regex
        """

        c = self
        pat = re.compile(regex, flags)
        res = leoNodes.poslist()
        for p in c.all_positions():
            m = re.match(pat, p.h)
            if m:
                pc = p.copy()
                pc.mo = m
                res.append(pc)
        return res

    #@+node:ville.20090311200059.1: *4* c.find_b
    def find_b(self, regex, flags = re.IGNORECASE | re.MULTILINE):
        """ Return list (a poslist) of all nodes whose body matches regex
        one or more times.

        """

        c = self
        pat = re.compile(regex, flags)
        res = leoNodes.poslist()
        for p in c.all_positions():
            m = re.finditer(pat, p.b)
            t1,t2 = itertools.tee(m,2)
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
    #@+node:ekr.20091001141621.6061: *3* c.generators
    #@+node:ekr.20091001141621.6043: *4* c.all_nodes & all_unique_nodes
    def all_nodes(self):
        c = self
        for p in c.all_positions():
            yield p.v
        # raise StopIteration

    def all_unique_nodes(self):
        c = self
        for p in c.all_unique_positions():
            yield p.v
        # raise StopIteration

    # Compatibility with old code.
    all_tnodes_iter = all_nodes
    all_vnodes_iter = all_nodes
    all_unique_tnodes_iter = all_unique_nodes
    all_unique_vnodes_iter = all_unique_nodes
    #@+node:ekr.20091001141621.6062: *4* c.all_unique_positions
    def all_unique_positions(self):
        c = self
        p = c.rootPosition() # Make one copy.
        seen = set()
        while p:
            if p.v in seen:
                p.moveToNodeAfterTree()
            else:
                seen.add(p.v)
                yield p
                p.moveToThreadNext()
        # raise StopIteration

    # Compatibility with old code.
    all_positions_with_unique_tnodes_iter = all_unique_positions
    all_positions_with_unique_vnodes_iter = all_unique_positions
    #@+node:ekr.20091001141621.6044: *4* c.all_positions
    def all_positions (self):
        c = self
        p = c.rootPosition() # Make one copy.
        while p:
            yield p
            p.moveToThreadNext()
        # raise stopIteration

    # Compatibility with old code.
    all_positions_iter = all_positions
    allNodes_iter = all_positions
    #@+node:ekr.20090130135126.1: *3* c.Properties
    def __get_p(self):

        c = self
        return c.currentPosition()

    p = property(
        __get_p, # No setter.
        doc = "commander current position property")
    #@+node:ekr.20110530082209.18250: *3* c.putHelpFor
    def putHelpFor(self,s):

        c = self
        s = g.adjustTripleString(s.rstrip(),c.tab_width)
        if s.startswith('<') and not s.startswith('<<'):
            pass # how to do selective replace??

        pc = g.app.pluginsController
        vr = pc.loadOnePlugin('viewrendered.py')
        assert vr # For unit testing.
        if vr:
            kw = {
                'c':c,
                'flags':'rst',
                'label':'',
                'msg':s,
                'name':'Apropos',
                'short_title':'',
                'title':''}
            vr.show_scrolled_message(tag='Apropos',kw=kw)
            c.bodyWantsFocus()
            if g.unitTesting:
                vr.close_rendering_pane(event={'c':c})
        else:
            g.es(s)
    #@+node:ekr.20130823083943.12559: *3* c.recursiveImport
    def recursiveImport(self,dir_,
        one_file=False,
        safe_at_file=True,
        theTypes=None,
        use_at_edit=False,
    ):
        #@+<< docstring >>
        #@+node:ekr.20130823083943.12614: *4* << docstring >>
        '''
        Recursively import all python files in a directory and clean the results.

        Parameters::
            dir_            The root directory or file to import
            one_file        True: import only the file given by dir_.
            safe_at_file    True: produce @@file nodes instead of @file nodes.
            theTypes        A list of file extensions to import.
                            None is equivalen to ['.py']
            use_at_edit     True: create @edit nodes instead of @file nodes.
            
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
                cc = leoImport.recursiveImportController(c,
                    one_file = one_file,
                    safe_at_file = safe_at_file,
                    theTypes = ['.py'] if theTypes is None else theTypes,
                    use_at_edit=use_at_edit)
                cc.run(dir_)
            finally:
                c.redraw()
        else:
            g.es_print('Does not exist: %s' % (dir_))
    #@+node:bobjack.20080509080123.2: *3* c.universalCallback
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
        def minibufferCallback(event,function=function):

            trace = False and not g.unitTesting

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
                if trace: g.trace(function,keywords)
                retval = function(keywords)
            finally:
                if cm:
                    # Even if there is an error:
                    #   clear mb_keywords prior to next command and
                    #   ensure mb_retval from last command is wiped
                    cm.mb_keywords = None
                    cm.mb_retval = retval

        minibufferCallback.__doc__ = function.__doc__
        return minibufferCallback

    #fix bobjacks spelling error
    universallCallback = universalCallback
    #@+node:ekr.20031218072017.2818: *3* Command handlers...
    #@+node:ekr.20031218072017.2819: *4* File Menu
    #@+node:ekr.20031218072017.2820: *5* top level (file menu)
    #@+node:ekr.20031218072017.2833: *6* c.close
    def close (self,event=None,new_c=None):

        '''Close the Leo window, prompting to save it if it has been changed.'''

        g.app.closeLeoWindow(self.frame,new_c=new_c)
    #@+node:ekr.20110530124245.18245: *6* c.importAnyFile & helper
    def importAnyFile (self,event=None):

        '''Import one or more files.'''

        c = self ; ic = c.importCommands
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
        others = [ z for z in names if not z in derived]
        if derived:
            ic.importDerivedFiles(parent=c.p,paths=derived)
        for fn in others:
            junk,ext = g.os_path_splitext(fn)
            if ext.startswith('.'): ext = ext[1:]
            if ext in ('cw','cweb'):
                ic.importWebCommand([fn],"cweb")
            elif ext in ('nw','noweb'):
                ic.importWebCommand([fn],"noweb")
            elif ext == 'txt':
                ic.importFlattenedOutline([fn])
            else:
                ic.importFilesCommand([fn],"@file")
            # No longer supported.
            # c.importCommands.importFilesCommand (names,"@root")
        c.raise_error_dialogs(kind='read')

    # Compatibility
    importAtFile = importAnyFile
    importAtRoot = importAnyFile
    importCWEBFiles = importAnyFile
    importDerivedFile = importAnyFile
    importFlattenedOutline = importAnyFile
    importNowebFiles = importAnyFile
    #@+node:ekr.20110530124245.18248: *7* c.looksLikeDerivedFile
    def looksLikeDerivedFile (self,fn):

        '''Return True if fn names a file that looks like an
        external file written by Leo.'''

        # c = self    
        try:
            f = open(fn,'r')
        except IOError:
            return False

        s = f.read()
        f.close()
        val = s.find('@+leo-ver=') > -1
        return val
    #@+node:ekr.20031218072017.1623: *6* c.new
    def new (self,event=None,gui=None):

        '''Create a new Leo window.'''

        lm = g.app.loadManager

        # Clean out the update queue so it won't interfere with the new window.
        self.outerUpdate()

        # Send all log messages to the new frame.
        g.app.setLog(None)
        g.app.lockLog()
        c = g.app.newCommander(fileName=None,gui=gui)
        frame = c.frame
        g.app.unlockLog()

        frame.setInitialWindowGeometry()
        frame.deiconify()
        frame.lift()
        frame.resizePanesToRatio(frame.ratio,frame.secondary_ratio)
            # Resize the _new_ frame.
        c.frame.createFirstTreeNode()
        lm.createMenu(c)
        lm.finishOpen(c)
        g.app.writeWaitingLog(c)
        g.doHook("new",old_c=self,c=c,new_c=c)
        c.setLog()
        c.redraw()
        return c # For unit tests and scripts.
    #@+node:ekr.20031218072017.2821: *6* c.open & helper
    def open (self,event=None):

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
            ("All files","*"),
            ("Leo files","*.leo"),
            ("Python files","*.py"),]

        fileName = ''.join(c.k.givenArgs) or g.app.gui.runOpenFileDialog(
            title = "Open",filetypes = table,defaultextension = ".leo")
        c.bringToFront()

        c.init_error_dialogs()

        ok = False
        if fileName:
            if fileName.endswith('.leo'):
                c2 = g.openWithFileName(fileName,old_c=c)
                if c2:
                    g.chdir(fileName)
                    g.setGlobalOpenDir(fileName)
                if c2 and closeFlag:
                    g.app.destroyWindow(c.frame)
            elif c.looksLikeDerivedFile(fileName):
                # 2011/10/09: A smart open makes Leo lighter:
                # Create an @file node for files containing Leo sentinels.
                ok = c.importCommands.importDerivedFiles(parent=c.p,
                    paths=[fileName],command='Open')
            else:
                # otherwise, create an @edit node.
                ok = c.createNodeFromExternalFile(fileName)

        c.raise_error_dialogs(kind='write')

        # openWithFileName sets focus if ok.
        if not ok:
            c.initialFocusHelper()
    #@+node:ekr.20090212054250.9: *7* c.createNodeFromExternalFile
    def createNodeFromExternalFile(self,fn):

        '''Read the file into a node.
        Return None, indicating that c.open should set focus.'''

        c = self

        s,e = g.readFileIntoString(fn)
        if s is None: return
        head,ext = g.os_path_splitext(fn)
        if ext.startswith('.'): ext = ext[1:]
        language = g.app.extension_dict.get(ext)
        if language:
            prefix = '@color\n@language %s\n\n' % language
        else:
            prefix = '@killcolor\n\n'
        p2 = c.insertHeadline(op_name='Open File', as_child=False)
        p2.h = '@edit %s' % fn # g.shortFileName(fn)
        p2.b = prefix + s
        w = c.frame.body.bodyCtrl
        if w: w.setInsertPoint(0)
        c.redraw()
        c.recolor()
    #@+node:ekr.20031218072017.2823: *6* c.openWith and helpers
    def openWith(self,event=None,d=None):

        '''This routine handles the items in the Open With... menu.

        The "d" arg is a Python dictionary whose keys and values
        are set from the body text of @openwith nodes.

        d.get('ext'):   The temp file's extension.
        d.get('kind'):  The method used to open the file.
        One of: ('os.startfile','exec','os.spawnl':'os.spawnv'.'subprocess.Popen')
        d.get('args'):  A list of arguments specified by the arg tag.
        '''

        c = self ; p = c.p
        try:
            ext = d.get('ext')
            if not g.doHook('openwith1',c=c,p=p,v=p.v,d=d):
                ext = c.getOpenWithExt(p,ext)
                fn = c.openWithHelper(p,ext)
                if fn:
                    g.enableIdleTimeHook(idleTimeDelay=500)
                    c.openTempFileInExternalEditor(d,fn)
            g.doHook('openwith2',c=c,p=p,v=p.v,d=d)
        except Exception:
            g.es('unexpected exception in c.openWith')
            g.es_exception()
    #@+node:ekr.20031218072017.2824: *7* c.getOpenWithExt
    def getOpenWithExt (self,p,ext):

        trace = False and not g.app.unitTesting
        if trace: g.trace(ext)

        c = self

        if ext:
            for ch in ("'",'"'):
                if ext.startswith(ch): ext = ext.strip(ch)

        if not ext:
            # if node is part of @<file> tree, get ext from file name
            for p2 in p.self_and_parents():
                if p2.isAnyAtFileNode():
                    fn = p2.h.split(None,1)[1]
                    ext = g.os_path_splitext(fn)[1]
                    if trace: g.trace('found node:',ext,p2.h)
                    break

        if not ext:
            theDict = c.scanAllDirectives()
            language = theDict.get('language')
            ext = g.app.language_extension_dict.get(language)
            if trace: g.trace('found directive',language,ext)

        if not ext:
            ext = '.txt'
            if trace: g.trace('use default (.txt)')

        if ext[0] != '.':
            ext = '.'+ext

        if trace: g.trace(ext)

        return ext
    #@+node:ekr.20031218072017.2829: *7* c.openTempFileInExternalEditor
    def openTempFileInExternalEditor(self,d,fn,testing=False):

        '''Open the closed mkstemp file fn in an external editor.
        The arg and openType args come from the data arg to c.openWith.
        '''

        trace = False and not g.unitTesting
        testing = testing or g.unitTesting

        def join(s1,s2):
            return '%s %s' % (s1,s2)

        if trace:
            print()
            g.trace(fn)
            for key in sorted(list(d.keys())):
                print('%15s %s' % (key,d.get(key)))

        arg_tuple = d.get('args',[])
        arg = ' '.join(arg_tuple)
        openType = d.get('kind')

        try:
            command = '<no command>'
            if openType == 'os.startfile':
                command = 'os.startfile(%s)' % join(arg,fn)
                if trace: g.trace(command)
                if not testing: os.startfile(join(arg,fn))
            elif openType == 'exec':
                command = 'exec(%s)' % join(arg,fn)
                if trace: g.trace(command)
                if not testing: exec(join(arg,fn),{},{})
            elif openType == 'os.spawnl':
                filename = g.os_path_basename(arg)
                command = 'os.spawnl(%s,%s,%s)' % (arg,filename,fn)
                if trace: g.trace(command)
                if not testing: os.spawnl(os.P_NOWAIT,arg,filename,fn)
            elif openType == 'os.spawnv':
                filename = os.path.basename(arg_tuple[0]) 
                vtuple = arg_tuple[1:]
                vtuple.insert(0, filename)
                    # add the name of the program as the first argument.
                    # Change suggested by Jim Sizelove.
                vtuple.append(fn)
                command = 'os.spawnv(%s)' % (vtuple)
                if trace: g.trace(command)
                if not testing:
                    os.spawnv(os.P_NOWAIT,arg[0],vtuple) #???
            elif openType == 'subprocess.Popen':
                use_shell = True
                c_arg = join(arg,fn)
                command = 'subprocess.Popen(%s)' % c_arg
                if trace: g.trace(command)
                if not testing:
                    try:
                        subprocess.Popen(c_arg,shell=use_shell)
                    except OSError:
                        g.es_print('c_arg',repr(c_arg))
                        g.es_exception()
            elif g.isCallable(openType):
                # Invoke openWith like this:
                # c.openWith(data=[f,None,None])
                # f will be called with one arg, the filename
                if trace: g.trace('%s(%s)' % (openType,fn))
                command = '%s(%s)' % (openType,fn)
                if not testing: openType(fn)
            else:
                command='bad command:'+str(openType)
                if not testing: g.trace(command)
            return command # for unit testing.
        except Exception:
            g.es('exception executing open-with command:',command)
            g.es_exception()
            return 'oops: %s' % command
    #@+node:ekr.20031218072017.2832: *7* c.openWithTempFilePath (may be over-ridden)
    def openWithTempFilePath (self,p,ext):

        '''Return the path to the temp file corresponding to p and ext.

        This is overridden in mod_tempfname plugin
        '''

        fn = '%s_LeoTemp_%s%s' % (
            g.sanitize_filename(p.h),
            str(id(p.v)),ext)
        if g.isPython3: # 2010/02/07
            fn = g.toUnicode(fn)
        td = g.os_path_finalize(tempfile.gettempdir())
        path = g.os_path_join(td,fn)

        return path
    #@+node:ekr.20100203050306.5797: *7* c.openWithHelper
    def openWithHelper (self,p,ext):

        '''create or reopen a temp file for p,
        testing for conflicting changes.
        '''

        c = self

        # May be over-ridden by mod_tempfname plugin.
        searchPath = c.openWithTempFilePath(p,ext)
        if not searchPath:
            # Check the mod_tempfname plugin.
            return g.error('c.openWithTempFilePath failed')

        # Set d and path if a temp file already refers to p.v
        path = None
        if g.os_path_exists(searchPath):
            for d in g.app.openWithFiles:
                if p.v == d.get('v') and searchPath == d.get('path'):
                    path = searchPath ; break

        if path:
            assert d.get('path') == searchPath
            fn = c.createOrRecreateTempFileAsNeeded(p,d,ext)
        else:
            fn = c.createOpenWithTempFile(p,ext)

        return fn # fn may be None.
    #@+node:ekr.20031218072017.2827: *8* c.createOrRecreateTempFileAsNeeded
    conflict_message = '''
    Conflicting changes in outline and temp file.
    Do you want to use the data in the outline?
    Yes: use the data in the outline.
    No: use the data in the temp file.
    Cancel or Escape or Return: do nothing.
    '''

    def createOrRecreateTempFileAsNeeded (self,p,d,ext):

        '''test for changes in both p and the temp file:

        - If only p's body text has changed, we recreate the temp file.
        - If only the temp file has changed, do nothing here.
        - If both have changed we must prompt the user to see which code to use.

        Return the file name.
        '''
        c = self

        fn = d.get('path')
        # Get the old & new body text and modification times.
        encoding = d.get('encoding')
        old_body = d.get('body')
        new_body = g.toEncodedString(p.b,encoding,reportErrors=True)
        old_time = d.get('time')
        try:
            new_time = g.os_path_getmtime(fn)
        except Exception:
            new_time = None
        body_changed = old_body != new_body
        time_changed = old_time != new_time

        if body_changed and time_changed:
            g.error('Conflict in temp file for',p.h)
            result = g.app.gui.runAskYesNoCancelDialog(c,
                'Conflict!', c.conflict_message,
                yesMessage = 'Outline',
                noMessage = 'File',
                defaultButton = 'Cancel')
            if result is None or result.lower() == 'cancel':
                return False
            rewrite = result.lower() == 'yes'
        else:
            rewrite = body_changed

        if rewrite:
            # May be overridden by the mod_tempfname plugin.
            fn = c.createOpenWithTempFile(p,ext)
        else:
            g.blue('reopening:',g.shortFileName(fn))

        return fn
    #@+node:ekr.20100203050306.5937: *8* c.createOpenWithTempFile
    def createOpenWithTempFile (self,p,ext):

        trace = False and not g.unitTesting
        c = self

        # May be over-ridden by mod_tempfname plugin.
        fn = c.openWithTempFilePath(p,ext)
        try:
            f = None
            if not g.unitTesting:
                if g.os_path_exists(fn):
                    g.red('recreating:  ',g.shortFileName(fn))
                else:
                    g.blue('creating:  ',g.shortFileName(fn))
            f = open(fn,'w')
            # Convert s to whatever encoding is in effect.
            d = c.scanAllDirectives(p)
            encoding = d.get('encoding',None)
            if encoding == None:
                encoding = c.config.default_derived_file_encoding
            if g.isPython3: # 2010/02/09
                s = p.b
            else:
                s = g.toEncodedString(p.b,encoding,reportErrors=True) 
            f.write(s)
            f.flush()
            f.close()
            try:
                t1 = g.os_path_getmtime(fn)
                if t1 and not g.unitTesting:
                    g.es('time: ',t1)
            except:
                t1 = None

            # Remove previous entry from app.openWithFiles if it exists.
            for d in g.app.openWithFiles[:]:
                if p.v == d.get('v'):
                    if trace: g.trace('removing',d.get('path'))
                    g.app.openWithFiles.remove(d)

            d = {
                # Used by app.destroyOpenWithFilesForFrame.
                'c':c,
                # Used here and by app.destroyOpenWithFileWithDict.
                'path':fn,
                # Used by c.testForConflicts.
                'body':s,
                'encoding':encoding,
                'time':t1,
                # Used by the open_with plugin.
                'p':p.copy(),
                # Used by c.openWithHelper, and below.
                'v':p.v,
            }
            g.app.openWithFiles.append(d)
            return fn
        except:
            if f: f.close()
            g.error('exception creating temp file')
            g.es_exception()
            return None
    #@+node:ekr.20031218072017.2834: *6* c.save
    def save (self,event=None,fileName=None):

        '''Save a Leo outline to a file.'''

        c = self ; p = c.p
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
            g.es("save commands disabled",color="purple")
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
            c.fileCommands.save(c.mFileName)
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
                        toString=False,force=True)
                c.setChanged(False)
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
                c.frame.title = c.computeWindowTitle(c.mFileName)
                c.frame.setTitle(c.computeWindowTitle(c.mFileName))
                    # 2013/08/04: use c.computeWindowTitle.
                c.openDirectory = c.frame.openDirectory = g.os_path_dirname(c.mFileName)
                    # Bug fix in 4.4b2.
                if g.app.qt_use_tabs and hasattr(c.frame,'top'):
                    c.frame.top.leo_master.setTabName(c,c.mFileName)
                c.fileCommands.save(c.mFileName)
                g.app.recentFilesManager.updateRecentFiles(c.mFileName)
                g.chdir(c.mFileName)

        # Done in fileCommands.save.
        # c.redraw_after_icons_changed()
        c.raise_error_dialogs(kind='write')
        # *Safely* restore focus, without using the old w directly.
        if inBody:
            c.bodyWantsFocus()
            p.restoreCursorAndScroll()
        else:
            c.treeWantsFocus()
    #@+node:ekr.20110228162720.13980: *6* c.saveAll
    def saveAll (self,event=None):

        '''Save all open tabs windows/tabs.'''

        for f in g.app.windowList:
            c = f.c
            if c.isChanged():
                c.save()
        # Restore the present tab.
        c = self
        dw = c.frame.top # A DynamicWindow
        dw.select(c)
    #@+node:ekr.20031218072017.2835: *6* c.saveAs
    def saveAs (self,event=None,fileName=None):

        '''Save a Leo outline to a file with a new filename.'''

        c = self ; p = c.p
        # Do this now: w may go away.
        w = g.app.gui.get_focus(c)
        inBody = g.app.gui.widget_name(w).startswith('body')
        if inBody: p.saveCursorAndScroll()
        if g.app.disableSave:
            g.es("save commands disabled",color="purple")
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
            fileName = ''.join(c.k.givenArgs) or g.app.gui.runSaveFileDialog(
                initialfile = c.mFileName,
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
            if g.app.qt_use_tabs and hasattr(c.frame,'top'):
                c.frame.top.leo_master.setTabName(c,c.mFileName)
            c.fileCommands.saveAs(c.mFileName)
            g.app.recentFilesManager.updateRecentFiles(c.mFileName)
            g.chdir(c.mFileName)
        # Done in fileCommands.saveAs.
        # c.redraw_after_icons_changed()
        c.raise_error_dialogs(kind='write')
        # *Safely* restore focus, without using the old w directly.
        if inBody:
            c.bodyWantsFocus()
            p.restoreCursorAndScroll()
        else:
            c.treeWantsFocus()
    #@+node:ekr.20031218072017.2836: *6* c.saveTo
    def saveTo (self,event=None,fileName=None):

        '''Save a Leo outline to a file, leaving the file associated with the Leo outline unchanged.'''

        c = self ; p = c.p
        # Do this now: w may go away.
        w = g.app.gui.get_focus(c)
        inBody = g.app.gui.widget_name(w).startswith('body')
        if inBody:
            p.saveCursorAndScroll()
        if g.app.disableSave:
            g.es("save commands disabled",color="purple")
            return
        c.init_error_dialogs()
        # 2013/09/28: add fileName keyword arg for leoBridge scripts.
        if fileName:
            c.frame.title = g.computeWindowTitle(fileName)
            c.mFileName = fileName
        # Make sure we never pass None to the ctor.
        if not c.mFileName:
            c.frame.title = ""
        # 2013/09/28: add fileName keyword arg for leoBridge scripts.
        if not fileName:
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
            g.app.recentFilesManager.updateRecentFiles(fileName)
            g.chdir(fileName)
        # Does not change icons status.
        # c.redraw_after_icons_changed()
        c.raise_error_dialogs(kind='write')
        # *Safely* restore focus, without using the old w directly.
        if inBody:
            c.bodyWantsFocus()
            p.restoreCursorAndScroll()
        else:
            c.treeWantsFocus()
    #@+node:ekr.20031218072017.2837: *6* c.revert
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

        # Rename this frame so the open logic won't think it is open.
        fileName = c.mFileName ; c.mFileName = ""

        # Create a new frame before deleting this frame.
        try:
            g.app.reverting = True
            c2 = g.openWithFileName(fileName,old_c=c)
        finally:
            g.app.reverting = False

        if c2:
            c2.frame.deiconify()
            g.doHook("close-frame",c=c)
            g.app.destroyWindow(c.frame)
        else:
            c.mFileName = fileName
    #@+node:ekr.20070413045221: *6* c.saveAsUnzipped & saveAsZipped
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
    #@+node:ekr.20031218072017.2079: *5* Recent Files submenu & allies
    #@+node:ekr.20031218072017.2080: *6* c.clearRecentFiles
    def clearRecentFiles (self,event=None):

        """Clear the recent files list, then add the present file."""

        c = self
        g.app.recentFilesManager.clearRecentFiles(c)
    #@+node:ekr.20031218072017.2081: *6* c.openRecentFile
    def openRecentFile(self,fn=None):

        c = self

        # Automatically close the previous window if...
        closeFlag = (
            c.frame.startupWindow and
                # The window was open on startup
            not c.changed and not c.frame.saved and
                # The window has never been changed
            g.app.numberOfUntitledWindows == 1)
                # Only one untitled window has ever been opened.

        if g.doHook("recentfiles1",c=c,p=c.p,v=c.p,fileName=fn,closeFlag=closeFlag):
            return

        c2 = g.openWithFileName(fn,old_c=c)

        if closeFlag and c2 and c2 != c:
            g.app.destroyWindow(c.frame)
            c2.setLog()
            g.doHook("recentfiles2",
                c=c2,p=c2.p,v=c2.p,fileName=fn,closeFlag=closeFlag)
    #@+node:tbrown.20080509212202.6: *6* c.cleanRecentFiles
    def cleanRecentFiles(self,event=None):

        '''Remove items from the recent files list that are no longer valid.'''

        c = self
        g.app.recentFilesManager.cleanRecentFiles(c)
    #@+node:tbrown.20080509212202.8: *6* c.sortRecentFiles
    def sortRecentFiles(self,event=None):

        '''Sort the recent files list.'''

        c = self
        g.app.recentFilesManager.sortRecentFiles(c)
    #@+node:ekr.20031218072017.2838: *5* c.Read/Write submenu
    #@+node:ekr.20070806105721.1: *6* c.readAtAutoNodes
    def readAtAutoNodes (self,event=None):

        '''Read all @auto nodes in the presently selected outline.'''

        c = self ; u = c.undoer ; p = c.p

        c.endEditing()
        c.init_error_dialogs()
        undoData = u.beforeChangeTree(p)
        c.importCommands.readAtAutoNodes()
        u.afterChangeTree(p,'Read @auto Nodes',undoData)
        c.redraw()
        c.raise_error_dialogs(kind='read')
    #@+node:ekr.20031218072017.1839: *6* c.readAtFileNodes
    def readAtFileNodes (self,event=None):

        '''Read all @file nodes in the presently selected outline.'''

        c = self ; u = c.undoer ; p = c.p

        c.endEditing()
        # c.init_error_dialogs() # Done in at.readAll.
        undoData = u.beforeChangeTree(p)
        c.fileCommands.readAtFileNodes()
        u.afterChangeTree(p,'Read @file Nodes',undoData)
        c.redraw()
        # c.raise_error_dialogs(kind='read') # Done in at.readAll.
    #@+node:ekr.20080801071227.4: *6* c.readAtShadowNodes
    def readAtShadowNodes (self,event=None):

        '''Read all @shadow nodes in the presently selected outline.'''

        c = self ; u = c.undoer ; p = c.p

        c.endEditing()
        c.init_error_dialogs()
        undoData = u.beforeChangeTree(p)
        c.atFileCommands.readAtShadowNodes(p)
        u.afterChangeTree(p,'Read @shadow Nodes',undoData)
        c.redraw()
        c.raise_error_dialogs(kind='read')
    #@+node:ekr.20070915134101: *6* c.readFileIntoNode
    def readFileIntoNode (self,event=None):

        '''Read a file into a single node.'''

        c = self ; undoType = 'Read File Into Node'
        c.endEditing()

        filetypes = [("All files", "*"),("Python files","*.py"),("Leo files", "*.leo"),]
        fileName = g.app.gui.runOpenFileDialog(
            title="Read File Into Node",filetypes=filetypes,defaultextension=None)
        if not fileName:return
        s,e = g.readFileIntoString(fileName)
        if s is None: return

        g.chdir(fileName)
        s = '@nocolor\n' + s
        w = c.frame.body.bodyCtrl
        p = c.insertHeadline(op_name=undoType)
        p.setHeadString('@read-file-into-node ' + fileName)
        p.setBodyString(s)
        w.setAllText(s)
        c.redraw(p)
    #@+node:ekr.20031218072017.2839: *6* c.readOutlineOnly
    def readOutlineOnly (self,event=None):

        '''Open a Leo outline from a .leo file, but do not read any derived files.'''

        c = self
        c.endEditing()

        fileName = g.app.gui.runOpenFileDialog(
            title="Read Outline Only",
            filetypes=[("Leo files", "*.leo"), ("All files", "*")],
            defaultextension=".leo")

        if not fileName:
            return

        try:
            theFile = open(fileName,'r')
            g.chdir(fileName)
            c = g.app.newCommander(fileName)
            frame = c.frame
            frame.deiconify()
            frame.lift()
            c.fileCommands.readOutlineOnly(theFile,fileName) # closes file.
        except:
            g.es("can not open:",fileName)
    #@+node:ekr.20070915142635: *6* c.writeFileFromNode
    def writeFileFromNode (self,event=None):

        '''If node starts with @read-file-into-node, use the full path name in the headline.
        Otherwise, prompt for a file name.
        '''

        c = self ; p = c.p
        c.endEditing()

        h = p.h.rstrip()
        s = p.b
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
                if not g.isPython3: # 2010/08/27
                    s = g.toEncodedString(s,reportErrors=True)
                theFile.write(s)
                theFile.flush()
                g.blue('wrote:',fileName)
                theFile.close()
            else:
                g.error('can not write %s',fileName)
    #@+node:ekr.20031218072017.2841: *5* Tangle submenu
    #@+node:ekr.20031218072017.2842: *6* tangleAll
    def tangleAll (self,event=None):

        '''Tangle all @root nodes in the entire outline.'''

        c = self
        c.tangleCommands.tangleAll()
    #@+node:ekr.20031218072017.2843: *6* tangleMarked
    def tangleMarked (self,event=None):

        '''Tangle all marked @root nodes in the entire outline.'''

        c = self
        c.tangleCommands.tangleMarked()
    #@+node:ekr.20031218072017.2844: *6* tangle
    def tangle (self,event=None):

        '''Tangle all @root nodes in the selected outline.'''

        c = self
        c.tangleCommands.tangle()
    #@+node:ekr.20031218072017.2845: *5* Untangle submenu
    #@+node:ekr.20031218072017.2846: *6* untangleAll
    def untangleAll (self,event=None):

        '''Untangle all @root nodes in the entire outline.'''

        c = self
        c.tangleCommands.untangleAll()
        c.undoer.clearUndoState()
    #@+node:ekr.20031218072017.2847: *6* untangleMarked
    def untangleMarked (self,event=None):

        '''Untangle all marked @root nodes in the entire outline.'''

        c = self
        c.tangleCommands.untangleMarked()
        c.undoer.clearUndoState()
    #@+node:ekr.20031218072017.2848: *6* untangle
    def untangle (self,event=None):

        '''Untangle all @root nodes in the selected outline.'''

        c = self
        c.tangleCommands.untangle()
        c.undoer.clearUndoState()
    #@+node:ekr.20031218072017.2849: *5* Export submenu
    #@+node:ekr.20031218072017.2850: *6* c.exportHeadlines
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
    #@+node:ekr.20031218072017.2851: *6* c.flattenOutline
    def flattenOutline (self,event=None):

        '''Export the selected outline to an external file.
        The outline is represented in MORE format.'''

        c = self

        filetypes = [("Text files", "*.txt"),("All files", "*")]

        fileName = g.app.gui.runSaveFileDialog(
            initialfile="flat.txt",
            title="Flatten Selected Outline",
            filetypes=filetypes,
            defaultextension=".txt")
        c.bringToFront()

        if fileName and len(fileName) > 0:
            g.setGlobalOpenDir(fileName)
            g.chdir(fileName)
            c.importCommands.flattenOutline(fileName)
    #@+node:ekr.20031218072017.2857: *6* c.outlineToCWEB
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
    #@+node:ekr.20031218072017.2858: *6* c.outlineToNoweb
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
    #@+node:ekr.20031218072017.2859: *6* c.removeSentinels
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
    #@+node:ekr.20031218072017.2860: *6* weave
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
    #@+node:ekr.20031218072017.2861: *4* Edit Menu...
    #@+node:ekr.20031218072017.2862: *5* Edit top level
    #@+node:ekr.20031218072017.2090: *6* c.colorPanel
    def colorPanel (self,event=None):

        '''Open the color dialog.'''

        c = self ; frame = c.frame

        if not frame.colorPanel:
            frame.colorPanel = g.app.gui.createColorPanel(c)

        frame.colorPanel.bringToFront()
    #@+node:ekr.20031218072017.2140: *6* c.executeScript & helpers
    def executeScript(self,event=None,args=None,p=None,script=None,
        useSelectedText=True,define_g=True,define_name='__main__',silent=False,
        namespace=None,raiseFlag=False):

        """This executes body text as a Python script.

        We execute the selected text, or the entire body text if no text is selected."""

        c = self ; script1 = script

        if not script:
            script = g.getScript(c,p or c.p,useSelectedText=useSelectedText)

        script_p = p or c.p # Only for error reporting below.

        self.redirectScriptOutput()
        try:
            oldLog = g.app.log # 2011/01/19
            log = c.frame.log
            g.app.log = log
            if script.strip():
                # print('***executeScript***',c.frame.openDirectory)
                sys.path.insert(0,g.toEncodedString(c.frame.openDirectory))
                script += '\n' # Make sure we end the script properly.
                try:
                    # We *always* execute the script with p = c.p.
                    c.executeScriptHelper(args,define_g,define_name,namespace,script)
                except Exception:
                    if raiseFlag:
                        raise
                    else:
                        g.handleScriptException(c,script_p,script,script1)
                finally:
                    del sys.path[0]
            else:
                tabName = log and hasattr(log,'tabName') and log.tabName or 'Log'
                g.warning("no script selected",tabName=tabName)

        finally:
            g.app.log = oldLog # 2011/01/19
            self.unredirectScriptOutput()
    #@+node:ekr.20120923063251.10651: *7* c.executeScriptHelper
    def executeScriptHelper (self,args,define_g,define_name,namespace,script):

        c = self
        p = c.p.copy() # *Always* use c.p and pass c.p to script.
        c.setCurrentDirectoryFromContext(p)
        d = g.choose(define_g,{'c':c,'g':g,'p':p},{})
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
                if g.isPython3:
                    exec(compile(script,scriptFile,'exec'),d)
                else:
                    execfile(scriptFile,d)
            else:
                exec(script,d)
        finally:
            g.inScript = g.app.inScript = False
    #@+node:ekr.20031218072017.2143: *7* c.redirectScriptOutput
    def redirectScriptOutput (self):

        c = self

        # g.trace('original')

        if c.config.redirect_execute_script_output_to_log_pane:

            g.redirectStdout() # Redirect stdout
            g.redirectStderr() # Redirect stderr
    #@+node:ekr.20110522121957.18230: *7* c.setCurrentDirectoryFromContext
    def setCurrentDirectoryFromContext(self,p):

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
    def unredirectScriptOutput (self):

        c = self

        # g.trace('original')

        if c.exists and c.config.redirect_execute_script_output_to_log_pane:

            g.restoreStderr()
            g.restoreStdout()
    #@+node:ekr.20031218072017.2088: *6* c.fontPanel
    def fontPanel (self,event=None):

        '''Open the font dialog.'''

        c = self ; frame = c.frame

        if not frame.fontPanel:
            frame.fontPanel = g.app.gui.createFontPanel(c)

        frame.fontPanel.bringToFront()
    #@+node:EKR.20040612232221: *6* c.goToScriptLineNumber
    # Called from g.handleScriptException.

    def goToScriptLineNumber (self,p,script,n):

        """Go to line n of a script."""

        c = self

        scriptData = {'p':p.copy(),'lines':g.splitLines(script)}
        c.goToLineNumber(c).go(n=n,scriptData=scriptData)
    #@+node:ekr.20031218072017.2086: *6* c.preferences
    def preferences (self,event=None):

        '''Handle the preferences command.'''

        c = self
        c.openLeoSettings()
    #@+node:ekr.20031218072017.2883: *6* c.show/hide/toggleInvisibles
    def hideInvisibles (self,event=None):
        '''Hide invisible (whitespace) characters.'''
        c = self ; c.showInvisiblesHelper(False)

    def showInvisibles (self,event=None):
        '''Show invisible (whitespace) characters.'''
        c = self ; c.showInvisiblesHelper(True)

    def toggleShowInvisibles (self,event=None):
        '''Toggle showing of invisible (whitespace) characters.'''
        c = self ; colorizer = c.frame.body.getColorizer()
        val = g.choose(colorizer.showInvisibles,0,1)
        c.showInvisiblesHelper(val)

    def showInvisiblesHelper (self,val):
        c = self ; frame = c.frame ; p = c.p
        colorizer = frame.body.getColorizer()
        colorizer.showInvisibles = val

         # It is much easier to change the menu name here than in the menu updater.
        menu = frame.menu.getMenu("Edit")
        index = frame.menu.getMenuLabel(menu,g.choose(val,'Hide Invisibles','Show Invisibles'))
        if index is None:
            if val: frame.menu.setMenuLabel(menu,"Show Invisibles","Hide Invisibles")
            else:   frame.menu.setMenuLabel(menu,"Hide Invisibles","Show Invisibles")

        c.frame.body.recolor(p)
    #@+node:ekr.20070115135502: *6* c.writeScriptFile
    def writeScriptFile (self,script):

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
                g.app.homeLeoDir,'scriptFile.py')
        if trace: g.trace(path)                
        # Write the file.
        try:
            if g.isPython3:
                # Use the default encoding.
                f = open(path,encoding='utf-8',mode='w')
            else:
                f = open(path,'w')
            s = script
            if not g.isPython3: # 2010/08/27
                s = g.toEncodedString(s,reportErrors=True)
            f.write(s)
            f.close()
        except Exception:
            g.es_exception()
            g.es("Failed to write script to %s" % path)
            # g.es("Check your configuration of script_file_path, currently %s" %
                # c.config.getString('script_file_path'))
            path = None
        return path
    #@+node:ekr.20100216141722.5620: *6* class goToLineNumber and helpers (commands)
    class goToLineNumber:

        '''A class implementing goto-global-line.'''

        #@+others
        #@+node:ekr.20100216141722.5621: *7*  __init__ (gotoLineNumber)
        def __init__ (self,c):

            # g.trace('(c.gotoLineNumber)')
            self.c = c
            self.p = c.p.copy()
            self.isAtAuto = False
        #@+node:ekr.20100216141722.5622: *7* go
        def go (self,n,p=None,scriptData=None):

            '''Place the cursor on the n'th line of a derived file or script.
            When present scriptData is a dict with 'root' and 'lines' keys.'''

            c = self.c
            if n < 0: return

            if scriptData:
                fileName,lines,p,root = self.setup_script(scriptData)
            else:
                if not p: p = c.p
                fileName,lines,n,root = self.setup_file(n,p)

            self.isAtAuto = root and root.isAtAutoNode()
            isRaw = not root or (
                root.isAtEditNode() or root.isAtAsisFileNode() or
                root.isAtAutoNode() or root.isAtNoSentFileNode())
            ignoreSentinels = root and root.isAtNoSentFileNode()
            if not root:
                if scriptData:  root = p.copy()
                else:           root = c.p

            if isRaw:
                p,n2,found = self.countLines(root,n)
                n2 += 1 # Convert to one-based.
            else:
                vnodeName,gnx,n2,delim = self.findVnode(root,lines,n,ignoreSentinels)
                p,found = self.findGnx(delim,root,gnx,vnodeName)

            self.showResults(found,p or root,n,n2,lines)
            return found
        #@+node:ekr.20100216141722.5623: *7* countLines & helpers
        def countLines (self,root,n):

            '''Scan through root's outline, looking for line n (one based).
            Return (p,i,found)
            p is the found node.
            i is the offset of the line within the node.
            found is True if the line was found.'''

            trace = False and not g.unitTesting
            # c = self.c
            # Start the recursion.
            n = max(0,n-1)# Convert to zero based internally.
            if trace: g.trace('%s %s (zero-based) %s' % ('*' * 20,n,root.h))
            p,i,junk,found = self.countLinesHelper(root,n,trace)
            return p,i,found # The index is zero-based.
        #@+node:ekr.20100216141722.5624: *8* countLinesHelper
        def countLinesHelper (self,p,n,trace):

            '''Scan p's body text, looking for line n (zero-based).
            ao is the index of the line containing @others or None.

            Return (p,i,n,effective_lines,found)
            found: True if the line was found.
            if found::
                p:              The found node.
                i:              The offset of the line within the node.
                effective_lines:-1 (not used)

            if not found::
                p:              The original node.
                i:              -1 (not used)
                effective_lines:The number of lines in this node and all descendant nodes.
            '''
            if trace: g.trace('='*10,n,p.h)
            # c = self.c
            ao = None
            lines = g.splitLines(p.b)
            i = 0
                # The index of the line being scanning in this node.
            effective_lines = 0
                # The number of "counted" lines including the present line i.
            # Invariant 1: n never changes in this method(!)
            # Invariant 2: n is alway the target line.
            while i < len(lines):
                progress = i
                line = lines[i]
                if trace: g.trace('i %3s effective %3s %s' % (
                    i,effective_lines,line.rstrip()))
                if line.strip().startswith('@'):
                    if line.strip().startswith('@others'):
                        if ao is None and p.hasChildren():
                            ao = i
                            # Count lines in inner nodes.
                            # Pass n-effective_lines as the targe line number.
                            new_n = n-effective_lines
                            p2,i2,effective_lines2,found = \
                                self.countLinesInChildren(new_n,p,trace)
                            if found:
                                return p2,i2,-1,True # effective_lines doesn't matter.
                            else:
                                # Assert that the line has not been found.
                                if effective_lines2 > new_n:
                                    if trace: g.trace(
                                        '***oops! effective_lines2: %s, new_n: %s' % (
                                        effective_lines2,new_n))
                                    if g.unitTesting: assert False
                                effective_lines += effective_lines2
                                # Do *not* change i: it will be bumped below.
                                # Invariant: n never changes!
                        else:
                            pass # silently ignore erroneous @others.
                    else:
                        s = line.strip()
                        k = g.skip_id(s,1)
                        word = s[1:k]
                        if word and word in g.globalDirectiveList:
                            pass # A regular directive: don't change n or i here.
                        else:
                            # Fix bug 1182864: goto-global-line cmd bug.
                            # Do count everything (like decorators) that is not a Leo directive.
                            if effective_lines == n:
                                if trace: g.trace('Found! n: %s i: %s %s' % (n,i,lines[i]))
                                return p,i,-1,True # effective_lines doesn't matter.
                            else:
                                effective_lines += 1
                else:
                    # Bug fix 2011/01/21: use effective_lines, not i, in this comparison.
                    # The line is now known to be effective.
                    if effective_lines == n:
                        if trace: g.trace('Found! n: %s i: %s %s' % (n,i,lines[i]))
                        return p,i,-1,True # effective_lines doesn't matter.
                    else:
                        effective_lines += 1
                # This is the one and only place we update i in this loop.
                i += 1
                assert i > progress
            if trace:
                g.trace('Not found. n: %s effective_lines: %s %s' % (
                    n,effective_lines,p.h))
            return p,-1,effective_lines,False # i doesn't matter.
        #@+node:ekr.20100216141722.5625: *8* countLinesInChildren
        def countLinesInChildren(self,n,p,trace):

            if trace: g.trace('-'*10,n,p.h)
            effective_lines = 0
            for child in p.children():
                if trace:g.trace('child %s' % child.h)
                # Recursively scan the children.
                # Pass n-effective_lines as the targe line number for each child.
                new_n = n-effective_lines
                p2,i2,effective_lines2,found = \
                    self.countLinesHelper(child,new_n,trace)
                if found:
                    if trace: g.trace('Found! i2: %s %s' % (i2,child.h))
                    return p2,i2,-1,True # effective_lines doesn't matter.
                else:
                    # Assert that the line has not been found.
                    if effective_lines2 > new_n:
                        if trace: g.trace(
                            '*** oops! effective_lines2: %s, new_n: %s n: %s %s' % (
                                effective_lines2,new_n,n,p.h))
                        if g.unitTesting: assert False
                    # i2 is not used
                    effective_lines += effective_lines2

            if trace: g.trace('Not found. effective_lines: %s %s' % (
                effective_lines,p.h))
            return p,-1,effective_lines,False # i does not matter.
        #@+node:ekr.20100216141722.5626: *7* findGnx
        def findGnx (self,delim,root,gnx,vnodeName):

            '''Scan root's tree for a node with the given gnx and vnodeName.

            return (p,found)'''

            trace = False and not g.unitTesting

            if delim and gnx:
                gnx = g.app.nodeIndices.scanGnx(gnx,0)
                for p in root.self_and_subtree():
                    if p.matchHeadline(vnodeName):
                        if p.v.fileIndex == gnx:
                            return p.copy(),True

                if trace: g.trace('not found! %s, %s' % (gnx,repr(vnodeName)))
                return None,False
            else:
                return root,False
        #@+node:ekr.20100216141722.5627: *7* findRoot
        def findRoot (self,p):

            '''Find the closest ancestor @<file> node, except @all nodes.

            return root, fileName.'''

            c = self.c ; p1 = p.copy()

            # First look for ancestor @file node.
            for p in p.self_and_parents():
                fileName = not p.isAtAllNode() and p.anyAtFileNodeName()
                if fileName:
                    return p.copy(),fileName

            # Search the entire tree for joined nodes.
            # Bug fix: Leo 4.5.1: *must* search *all* positions.
            for p in c.all_positions():
                if p.v == p1.v and p != p1:
                    # Found a joined position.
                    for p2 in p.self_and_parents():
                        fileName = not p2.isAtAllNode() and p2.anyAtFileNodeName()
                        if fileName:
                            return p2.copy(),fileName

            return None,None
        #@+node:ekr.20100216141722.5628: *7* findVnode & helpers
        def findVnode (self,root,lines,n,ignoreSentinels):

            '''Search the lines of a derived file containing sentinels for a vnode.
            return (vnodeName,gnx,offset,delim):

            vnodeName:  the name found in the previous @+body sentinel.
            gnx:        the gnx of the found node.
            offset:     the offset within the node of the desired line.
            delim:      the comment delim from the @+leo sentinel.
            '''

            trace = False and not g.unitTesting
            # c = self.c
            # g.trace('lines...\n',g.listToString(lines))
            gnx = None
            delim,readVersion5,thinFile = self.setDelimFromLines(lines)
            if not delim:
                g.es('no sentinels in:',root.h)
                return None,None,None,None

            nodeLine,offset = self.findNodeSentinel(delim,lines,n)
            if nodeLine == -1:
                if n < len(lines):
                    # The line precedes the first @+node sentinel
                    g.trace('no @+node!!')
                return root.h,gnx,1,delim

            s = lines[nodeLine]
            gnx,vnodeName = self.getNodeLineInfo(readVersion5,s,thinFile)
            if delim and vnodeName:
                if trace: g.trace('offset: %s, vnodeName: %s' % (offset,vnodeName))
                return vnodeName,gnx,offset,delim
            else:
                g.es("bad @+node sentinel")
                return None,None,None,None
        #@+node:ekr.20100216141722.5629: *8* findNodeSentinel & helper
        def findNodeSentinel(self,delim,lines,n):

            '''
            Scan backwards from the line n, looking for an @-body line. When found,
            get the vnode's name from that line and set p to the indicated vnode. This
            will fail if vnode names have been changed, and that can't be helped.

            We compute the offset of the requested line **within the found node**.
            '''

            # c = self.c
            offset = 0 # This is essentially the Tk line number.
            nodeSentinelLine = -1
            line = n - 1 # Start with the requested line.
            while len(lines) > line >= 0 and nodeSentinelLine == -1:
                progress = line
                s = lines[line]
                i = g.skip_ws(s,0)
                if g.match(s,i,delim):
                    line,nodeSentinelLine,offset = self.handleDelim(
                        delim,s,i,line,lines,n,offset)
                else:
                    line -= 1
                assert nodeSentinelLine > -1 or line < progress
            return nodeSentinelLine,offset
        #@+node:ekr.20100216141722.5630: *9* handleDelim
        def handleDelim (self,delim,s,i,line,lines,n,offset):

            '''Handle the delim while scanning backward.'''

            trace = False and not g.unitTesting
            # c = self.c
            if line == n:
                g.es("line",str(n),"is a sentinel line")
            i += len(delim)
            nodeSentinelLine = -1

            # This code works for both old and new sentinels.
            if g.match(s,i,"-node"):
                # The end of a nested section.
                old_line = line
                line = self.skipToMatchingNodeSentinel(lines,line,delim)
                assert line < old_line
                if trace: g.trace('found',repr(lines[line]))
                nodeSentinelLine = line
                offset = n-line
            elif g.match(s,i,"+node"):
                if trace: g.trace('found',repr(lines[line]))
                nodeSentinelLine = line
                offset = n-line
            elif g.match(s,i,"<<") or g.match(s,i,"@first"):
                line -= 1
            else:
                line -= 1
                nodeSentinelLine = -1
            return line,nodeSentinelLine,offset
        #@+node:ekr.20100216141722.5631: *8* getNodeLineInfo & helper
        def getNodeLineInfo (self,readVersion5,s,thinFile):

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

            # old sentinels: vnode name is everything following the first or second':'
            i = s.find(':',i)
            if i > -1:
                vnodeName = s[i+1:].strip()
                if readVersion5: # new sentinels: remove level stars.
                    vnodeName = self.removeLevelStars(vnodeName)
            else:
                vnodeName = None
                g.error("bad @+node sentinel")

            return gnx,vnodeName
        #@+node:ekr.20100728074713.5843: *9* removeLevelStars
        def removeLevelStars (self,s):

            i = g.skip_ws(s,0)

            # Remove leading stars.
            while i < len(s) and s[i] == '*':
                i += 1
            # Remove optional level number.
            while i < len(s) and s[i].isdigit():
                i += 1
            # Remove trailing stars.
            while i < len(s) and s[i] == '*':
                i += 1
            # Remove one blank.
            if i < len(s) and s[i] == ' ':
                i += 1

            return s[i:]
        #@+node:ekr.20100216141722.5632: *8* setDelimFromLines
        def setDelimFromLines (self,lines):

            c = self.c ; at = c.atFileCommands

            # Find the @+leo line.
            i = 0 
            while i < len(lines) and lines[i].find("@+leo")==-1:
                i += 1
            leoLine = i # Index of the line containing the leo sentinel

            # Set delim and thinFile from the @+leo line.
            delim,thinFile = None,False

            if leoLine < len(lines):
                s = lines[leoLine]
                valid,newDerivedFile,start,end,thinFile = at.parseLeoSentinel(s)
                readVersion5 = at.readVersion5

                # New in Leo 4.5.1: only support 4.x files.
                if valid and newDerivedFile:
                    delim = start + '@'
            else:
                readVersion5 = False

            return delim,readVersion5,thinFile
        #@+node:ekr.20100216141722.5633: *8* skipToMatchingNodeSentinel (no longer used)
        def skipToMatchingNodeSentinel (self,lines,n,delim):

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
        #@+node:ekr.20100216141722.5634: *7* getFileLines (leoEditCommands)
        def getFileLines (self,root,fileName):

            '''Read the file into lines.'''

            c = self.c
            isAtEdit = root.isAtEditNode()
            isAtNoSent = root.isAtNoSentFileNode()

            if isAtNoSent or isAtEdit:
                # Write a virtual file containing sentinels.
                at = c.atFileCommands
                kind = g.choose(isAtNoSent,'@nosent','@edit')
                at.write(root,kind=kind,nosentinels=False,toString=True)
                lines = g.splitLines(at.stringOutput)
            else:
                # Calculate the full path.
                path = g.scanAllAtPathDirectives(c,root)
                # g.trace('path',path,'fileName',fileName)
                fileName = c.os_path_finalize_join(path,fileName)
                lines    = self.openFile(fileName)

            return lines
        #@+node:ekr.20100216141722.5635: *7* openFile (gotoLineNumber)
        def openFile (self,filename):
            """
            Open a file and check if a shadow file exists.
            Construct a line mapping. This ivar is empty if no shadow file exists.
            Otherwise it contains a mapping, shadow file number -> real file number.
            """

            c = self.c ; x = c.shadowController

            try:
                shadow_filename = x.shadowPathName(filename)
                if os.path.exists(shadow_filename):
                    fn = shadow_filename
                    lines = open(shadow_filename).readlines()
                    x.line_mapping = x.push_filter_mapping(
                        lines,
                        x.markerFromFileLines(lines,shadow_filename))
                else:
                    # Just open the original file.  This is not an error!
                    fn = filename
                    c.line_mapping = []
                    lines = open(filename).readlines()
            except Exception:
                # Make sure failures to open a file generate clear messages.
                g.error('can not open',fn)
                # g.es_exception()
                lines = []

            return lines
        #@+node:ekr.20100216141722.5636: *7* setup_file
        def setup_file (self,n,p):

            '''Return (lines,n) where:

            lines are the lines to be scanned.
            n is the effective line number (munged for @shadow nodes).
            '''

            c = self.c ; x = c.shadowController

            root,fileName = self.findRoot(p)

            if root and fileName:
                c.shadowController.line_mapping = [] # Set by open.
                lines = self.getFileLines(root,fileName)
                    # This will set x.line_mapping for @shadow files.
                if len(x.line_mapping) > n:
                    n = x.line_mapping[n]
            else:
                if not g.unitTesting:
                    g.warning("no ancestor @<file node>: using script line numbers")
                lines = g.getScript(c,p,useSelectedText=False)
                lines = g.splitLines(lines)

            return fileName,lines,n,root
        #@+node:ekr.20100216141722.5637: *7* setup_script
        def setup_script (self,scriptData):

            # c = self.c
            p = scriptData.get('p')
            root,fileName = self.findRoot(p)
            lines = scriptData.get('lines')
            return fileName,lines,p,root
        #@+node:ekr.20100216141722.5638: *7* showResults
        def showResults(self,found,p,n,n2,lines):

            trace = False and not g.unitTesting
            c = self.c ; w = c.frame.body.bodyCtrl

            # Select p and make it visible.
            c.redraw(p)

            # Put the cursor on line n2 of the body text.
            s = w.getAllText()
            if found:
                ins = g.convertRowColToPythonIndex(s,n2-1,0)
            else:
                ins = len(s)
                if len(lines) < n and not g.unitTesting:
                    g.warning('only',len(lines),'lines')

            if trace:
                i,j = g.getLine(s,ins)
                g.trace('found: %5s %2s %2s %15s %s' % (
                    found,n,n2,p.h,repr(s[i:j])))  

            w.setInsertPoint(ins)
            c.bodyWantsFocus()
            c.frame.body.seeInsertPoint()
        #@-others
    #@+node:ekr.20031218072017.2884: *5* Edit Body submenu
    #@+node:ekr.20031218072017.1827: *6* c.findMatchingBracket, helper and test
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
    #@+node:ekr.20061113221414: *7* findMatchingBracketHelper
    # To do: replace comments with blanks before scanning.
    # Test  unmatched())
    def findMatchingBracketHelper(self,s,ch,index):

        # c = self
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
    #@+node:ekr.20031218072017.1704: *6* convertAllBlanks
    def convertAllBlanks (self,event=None):

        '''Convert all blanks to tabs in the selected outline.'''

        c = self ; u = c.undoer ; undoType = 'Convert All Blanks'
        current = c.p

        if g.app.batchMode:
            c.notValidInBatchMode(undoType)
            return

        d = c.scanAllDirectives()
        tabWidth  = d.get("tabwidth")
        count = 0 ; dirtyVnodeList = []
        u.beforeChangeGroup(current,undoType)
        for p in current.self_and_subtree():
            # g.trace(p.h,tabWidth)
            innerUndoData = u.beforeChangeNodeContents(p)
            if p == current:
                changed,dirtyVnodeList2 = c.convertBlanks(event)
                if changed:
                    count += 1
                    dirtyVnodeList.extend(dirtyVnodeList2)
            else:
                changed = False ; result = []
                text = p.v.b
                # assert(g.isUnicode(text))
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
            g.es("blanks converted to tabs in",count,"nodes")
                # Must come before c.redraw().
        if count > 0:
            c.redraw_after_icons_changed()
    #@+node:ekr.20031218072017.1705: *6* convertAllTabs
    def convertAllTabs (self,event=None):

        '''Convert all tabs to blanks in the selected outline.'''

        c = self ; u = c.undoer ; undoType = 'Convert All Tabs'
        current = c.p

        if g.app.batchMode:
            c.notValidInBatchMode(undoType)
            return
        theDict = c.scanAllDirectives()
        tabWidth  = theDict.get("tabwidth")
        count = 0 ; dirtyVnodeList = []
        u.beforeChangeGroup(current,undoType)
        for p in current.self_and_subtree():
            undoData = u.beforeChangeNodeContents(p)
            if p == current:
                changed,dirtyVnodeList2 = self.convertTabs(event)
                if changed:
                    count += 1
                    dirtyVnodeList.extend(dirtyVnodeList2)
            else:
                result = [] ; changed = False
                text = p.v.b
                # assert(g.isUnicode(text))
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
        if count > 0:
            c.redraw_after_icons_changed()
    #@+node:ekr.20031218072017.1821: *6* convertBlanks
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
    #@+node:ekr.20031218072017.1822: *6* convertTabs
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
    #@+node:ekr.20031218072017.1823: *6* createLastChildNode
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
    #@+node:ekr.20031218072017.1824: *6* dedentBody
    def dedentBody (self,event=None):

        '''Remove one tab's worth of indentation from all presently selected lines.'''

        c = self ; current = c.p ; undoType='Unindent'

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
    #@+node:ekr.20110530124245.18238: *6* c.extract...
    #@+node:ekr.20110530124245.18239: *7* extract & helpers
    def extract (self,event=None):

        '''Create child node from the selected body text.

        1. If the selection starts with a section reference, the section name become
           the child's headline. All following lines become the child's body text.
           The section reference line remains in the original body text.

        2. If the selection looks like a Python class or definition line, the
           class/function/method name becmes child's headline and all selected lines
           become the child's body text.

        3. Otherwise, the first line becomes the child's headline, and all selected
           lines become the child's body text.
        '''

        c,current,u,undoType = self,self.p,self.undoer,'Extract'
        head,lines,tail,oldSel,oldYview = self.getBodyLines()
        if not lines: return # Nothing selected.

        # Remove leading whitespace.
        junk, ws = g.skip_leading_ws_with_indent(lines[0],0,c.tab_width)
        lines = [g.removeLeadingWhitespace(s,ws,c.tab_width) for s in lines]

        h = lines[0].strip()
        ref_h = c.extractRef(h).strip()
        def_h = c.extractDef(h).strip()
        if ref_h:
            # h,b,middle = ref_h,lines[1:],lines[0]
            # 2012/02/27: Change suggested by vitalije (vitalijem@gmail.com)
            h,b,middle = ref_h, lines[1:], ' '*ws +lines[0]
        elif def_h:
            h,b,middle = def_h,lines,''
        else:
            h,b,middle = lines[0].strip(),lines[1:],''

        u.beforeChangeGroup(current,undoType)

        undoData = u.beforeInsertNode(current)
        p = c.createLastChildNode(current,h,''.join(b))
        u.afterInsertNode(p,undoType,undoData)
        c.updateBodyPane(head,middle,tail,
            undoType=undoType,oldSel=None,oldYview=oldYview)

        u.afterChangeGroup(current,undoType=undoType)
        p.parent().expand()
        c.redraw(p.parent()) # A bit more convenient than p.
        c.bodyWantsFocus()

    # Compatibility
    extractSection = extract
    extractPythonMethod = extract
    #@+node:ekr.20110530124245.18241: *8* extractDef
    def extractDef (self, s):

        '''Return the defined function/method name if
        s looks like Python def or class line.
        '''

        s = s.strip()

        for tag in ('def','class'):
            if s.startswith(tag):
                i = g.skip_ws(s,len(tag))
                j = g.skip_id(s,i,chars='_')
                if j > i:
                    name = s[i:j]
                    if tag == 'class':
                        return name
                    else:
                        k = g.skip_ws(s,j)
                        if g.match(s,k,'('):
                            return name
        return ''
    #@+node:ekr.20110530124245.18242: *8* extractRef
    def extractRef (self, s):

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
    #@+node:ekr.20031218072017.1710: *7* extractSectionNames
    def extractSectionNames(self,event=None):

        '''Create child nodes for every section reference in the selected text.
        The headline of each new child node is the section reference.
        The body of each child node is empty.'''

        c = self ; u = c.undoer ; undoType = 'Extract Section Names'
        body = c.frame.body ; current = c.p
        head,lines,tail,oldSel,oldYview = self.getBodyLines()
        if not lines:
            g.warning('No lines selected')
            return

        u.beforeChangeGroup(current,undoType)
        found = False
        for s in lines:
            name = c.findSectionName(s)
            if name:
                undoData = u.beforeInsertNode(current)
                p = self.createLastChildNode(current,name,None)
                u.afterInsertNode(p,undoType,undoData)
                found = True
        c.validateOutline()

        if found:
            u.afterChangeGroup(current,undoType)
            c.redraw(p)
        else:
            g.warning("selected text should contain section names")

        # Restore the selection.
        i,j = oldSel
        body.setSelectionRange(i,j)
        body.setFocus()
    #@+node:ekr.20031218072017.1711: *8* findSectionName
    def findSectionName(self,s):

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

        return name
    #@+node:ekr.20031218072017.1829: *6* c.getBodyLines
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
    #@+node:ekr.20031218072017.1830: *6* indentBody (indent-region)
    def indentBody (self,event=None):

        '''The indent-region command indents each line of the selected body text,
        or each line of a node if there is no selected text. The @tabwidth directive
        in effect determines amount of indentation. (not yet) A numeric argument
        specifies the column to indent to.'''

        c = self ; current = c.p ; undoType='Indent Region'
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
    #@+node:ekr.20050312114529: *6* c.insert/removeComments
    #@+node:ekr.20131103054650.16535: *7* c.hasAmbiguousLangauge
    def hasAmbiguousLanguage(self,p):
        '''Return True if p.b contains different @language directives.'''
        c,languages,tag = self,set(),'@language'
        for s in g.splitLines(p.b):
            if g.match_word(s,0,tag):
                i = g.skip_ws(s,len(tag))
                j = g.skip_id(s,i)
                word = s[i:j]
                languages.add(word)
        return len(list(languages)) > 1
    #@+node:ekr.20131103054650.16536: *7* c.getLanguageAtCursor
    def getLanguageAtCursor(self,p,language):
        '''
        Return the language in effect at the present insert point.
        Use the language argument as a default if no @language directive seen.
        '''
        c = self
        tag = '@language'     
        w = c.frame.body.bodyCtrl
        ins = w.getInsertPoint()
        n = 0
        for s in g.splitLines(p.b):
            # g.trace(ins,n,repr(s))
            if g.match_word(s,0,tag):
                i = g.skip_ws(s,len(tag))
                j = g.skip_id(s,i)
                language = s[i:j]
            if n <= ins < n + len(s):
                break
            else:
                n += len(s)
        # g.trace(ins,n,language)
        return language
    #@+node:ekr.20050312114529.1: *7* addComments
    def addComments (self,event=None):
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
        c = self ; p = c.p
        head,lines,tail,oldSel,oldYview = self.getBodyLines()
        if not lines:
            g.warning('no text selected')
            return
        # The default language in effect at p.
        language = c.frame.body.colorizer.scanColorDirectives(p)
        if c.hasAmbiguousLanguage(p):
            language = c.getLanguageAtCursor(p,language)
        # g.trace(language,p.h)
        d1,d2,d3 = g.set_delims_from_language(language)
        d2 = d2 or '' ; d3 = d3 or ''
        if d1:
            openDelim,closeDelim = d1+' ',''
        else:
            openDelim,closeDelim = d2+' ',' '+d3
        # Comment out non-blank lines.
        indent = c.config.getBool('indent_added_comments',default=True)
        result = []
        for line in lines:
            if line.strip():
                i = g.skip_ws(line,0)
                if indent:
                    result.append(line[0:i]+openDelim+line[i:].replace('\n','')+closeDelim+'\n')
                else:
                    result.append(openDelim+line.replace('\n','')+closeDelim+'\n')
            else:
                result.append(line)
        result = ''.join(result)
        c.updateBodyPane(head,result,tail,undoType='Add Comments',oldSel=None,oldYview=oldYview)
    #@+node:ekr.20050312114529.2: *7* deleteComments
    def deleteComments (self,event=None):

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
        c = self ; p = c.p
        head,lines,tail,oldSel,oldYview = self.getBodyLines()
        result = []
        if not lines:
            g.warning('no text selected')
            return
        # The default language in effect at p.
        language = c.frame.body.colorizer.scanColorDirectives(p)
        if c.hasAmbiguousLanguage(p):
            language = c.getLanguageAtCursor(p,language)
        d1,d2,d3 = g.set_delims_from_language(language)
        if d1:
            # Remove the single-line comment delim in front of each line
            d1b = d1 + ' '
            n1,n1b = len(d1),len(d1b)
            for s in lines:
                i = g.skip_ws(s,0)
                if g.match(s,i,d1b):
                    result.append(s[:i] + s[i+n1b:])
                elif g.match(s,i,d1):
                    result.append(s[:i] + s[i+n1:])
                else:
                    result.append(s)
        else:
            # Remove the block comment delimiters from each line.
            n2,n3 = len(d2),len(d3)
            for s in lines:
                i = g.skip_ws(s,0)
                j = s.find(d3,i+n2)
                if g.match(s,i,d2) and j > -1:
                    first = i + n2
                    if g.match(s,first,' '): first += 1
                    last = j
                    if g.match(s,last-1,' '): last -= 1
                    result.append(s[:i] + s[first:last] + s[j+n3:])
                else:
                    result.append(s)
        result = ''.join(result)
        c.updateBodyPane(head,result,tail,undoType='Delete Comments',oldSel=None,oldYview=oldYview)
    #@+node:ekr.20031218072017.1831: *6* insertBodyTime, helpers and tests
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
    #@+node:ekr.20031218072017.1832: *7* getTime
    def getTime (self,body=True):

        c = self
        default_format =  "%m/%d/%Y %H:%M:%S" # E.g., 1/30/2003 8:31:55

        # Try to get the format string from settings.
        if body:
            format = c.config.getString("body_time_format_string")
            gmt    = c.config.getBool("body_gmt_time")
        else:
            format = c.config.getString("headline_time_format_string")
            gmt    = c.config.getBool("headline_gmt_time")

        if format == None:
            format = default_format

        try:
            # import time
            if gmt:
                s = time.strftime(format,time.gmtime())
            else:
                s = time.strftime(format,time.localtime())
        except (ImportError, NameError):
            g.warning("time.strftime not available on this platform")
            return ""
        except:
            g.es_exception() # Probably a bad format string in leoSettings.leo.
            s = time.strftime(default_format,time.gmtime())
        return s
    #@+node:ekr.20131002055813.19033: *6* c.reformatBody (can hang)
    def reformatBody (self,event=None):
        
        '''Reformat all paragraphs in the body.'''
        
        # New in Leo 4.11
        c,p = self,self.p
        undoType = 'reformat-body'
        w = c.frame.body.bodyCtrl
        c.undoer.beforeChangeGroup(p,undoType)
        w.setInsertPoint(0)
        while 1:
            progress = w.getInsertPoint()
            c.reformatParagraph(event,undoType=undoType)
            ins = w.getInsertPoint()
            s = w.getAllText()
            w.setInsertPoint(ins)
            if ins <= progress or ins >= len(s):
                break
        c.undoer.afterChangeGroup(p,undoType)
    #@+node:ekr.20101118113953.5839: *6* c.reformatParagraph & helpers
    def reformatParagraph (self,event=None,undoType='Reformat Paragraph'):

        """Reformat a text paragraph

        Wraps the concatenated text to present page width setting. Leading tabs are
        sized to present tab width setting. First and second line of original text is
        used to determine leading whitespace in reformatted text. Hanging indentation
        is honored.

        Paragraph is bound by start of body, end of body and blank lines. Paragraph is
        selected by position of current insertion cursor.

        """
        trace = False and not g.unitTesting
        c = self ; body = c.frame.body ; w = body.bodyCtrl
        if g.app.batchMode:
            c.notValidInBatchMode("reformat-paragraph")
            return
        if body.hasSelection():
            i,j = w.getSelectionRange()
            w.setInsertPoint(i)
        oldSel,oldYview,original,pageWidth,tabWidth = c.rp_get_args()
        head,lines,tail = c.findBoundParagraph()
        if lines:
            if trace: g.trace('\n'+'\n'.join(lines))
            indents,leading_ws = c.rp_get_leading_ws(lines,tabWidth)
            result = c.rp_wrap_all_lines(indents,leading_ws,lines,pageWidth)
            c.rp_reformat(head,oldSel,oldYview,original,result,tail,undoType)
        else:
            if trace: g.trace('no lines')
    #@+node:ekr.20031218072017.1825: *7* c.findBoundParagraph & helpers
    def findBoundParagraph (self,event=None):
        '''Return the lines of a paragraph to be reformatted.'''
        c = self
        trace = False and not g.unitTesting
        head,ins,tail = c.frame.body.getInsertLines()
        head_lines = g.splitLines(head)
        tail_lines = g.splitLines(tail)
        if trace:
            g.trace("head_lines:\n%s" % ''.join(head_lines))
            g.trace("ins: ",ins)
            g.trace("tail_lines:\n%s" % ''.join(tail_lines))
            g.trace('*****')
        result = []
        insert_lines = g.splitLines(ins)
        para_lines = insert_lines + tail_lines
        # If the present line doesn't start a paragraph,
        # scan backward, adding trailing lines of head to ins.
        if insert_lines and not c.startsParagraph(insert_lines[0]):
            n = 0 # number of moved lines.
            for i,s in enumerate(reversed(head_lines)):
                if c.endsParagraph(s) or c.singleLineParagraph(s):
                    break
                elif c.startsParagraph(s):
                    n += 1
                    break
                else: n += 1
            if n > 0:
                para_lines = head_lines[-n:] + para_lines
                head_lines = head_lines[:-n]
        ended,started = False,False
        for i,s in enumerate(para_lines):
            if trace: g.trace(
                # 'i: %s started: %5s single: %5s starts: %5s: ends: %5s %s' % (
                i,started,
                c.singleLineParagraph(s),
                c.startsParagraph(s),
                c.endsParagraph(s),repr(s))
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
            return head,result,tail # string, list, string
        else:
            if trace: g.trace('no paragraph')
            return None,None,None
    #@+node:ekr.20131102044158.16572: *8* c.endsParagraph & c.singleLineParagraph
    def endsParagraph(self,s):
        '''Return True if s is a blank line.'''
        return not s.strip()
        
    def singleLineParagraph(self,s):
        '''Return True if s is a single-line paragraph.'''
        return s.startswith('@') or s.strip() in ('"""',"'''")
    #@+node:ekr.20131102044158.16570: *8* c.startsParagraph
    def startsParagraph(self,s):
        '''Return True if line s starts a paragraph.'''
        trace = False and not g.unitTesting
        if not s.strip():
            val = False
        elif s.strip() in ('"""',"'''"):
            val = True
        elif s[0].isdigit():
            i = 0
            while i < len(s) and s[i].isdigit():
                i += 1
            val = g.match(s,i,')') or g.match(s,i,'.')
        elif s[0].isalpha():
            # Careful: single characters only.
            # This could cause problems in some situations.
            val = (
                (g.match(s,1,')') or g.match(s,1,'.')) and
                (len(s) < 2 or s[2] in (' \t\n')))
        else:
            val = s.startswith('@') or s.startswith('-')
        if trace: g.trace(val,repr(s))
        return val
    #@+node:ekr.20101118113953.5840: *7* rp_get_args
    def rp_get_args (self):

        '''Compute and return oldSel,oldYview,original,pageWidth,tabWidth.'''

        c = self
        body = c.frame.body
        w = body.bodyCtrl
        d = c.scanAllDirectives()
        # g.trace(c.editCommands.fillColumn)
        if c.editCommands.fillColumn > 0:
            pageWidth = c.editCommands.fillColumn
        else:
            pageWidth = d.get("pagewidth")
        tabWidth  = d.get("tabwidth")
        original = w.getAllText()
        oldSel =  w.getSelectionRange()
        oldYview = body.getYScrollPosition()
        return oldSel,oldYview,original,pageWidth,tabWidth
    #@+node:ekr.20101118113953.5841: *7* rp_get_leading_ws
    def rp_get_leading_ws (self,lines,tabWidth):

        '''Compute and return indents and leading_ws.'''

        # c = self
        indents = [0,0]
        leading_ws = ["",""]
        for i in (0,1):
            if i < len(lines):
                # Use the original, non-optimized leading whitespace.
                leading_ws[i] = ws = g.get_leading_ws(lines[i])
                indents[i] = g.computeWidth(ws,tabWidth)

        indents[1] = max(indents)

        if len(lines) == 1:
            leading_ws[1] = leading_ws[0]

        return indents,leading_ws
    #@+node:ekr.20101118113953.5842: *7* rp_reformat
    def rp_reformat (self,head,oldSel,oldYview,original,result,tail,undoType):

        '''Reformat the body and update the selection.'''

        c = self ; body = c.frame.body ; w = body.bodyCtrl
        s = w.getAllText()
        # This destroys recoloring.
        junk, ins = body.setSelectionAreas(head,result,tail)
        
        changed = original != head + result + tail
        if changed:
            # 2013/09/14: fix an annoying glitch when there is no
            # newline following the reformatted paragraph.
            if not tail and ins < len(s): ins += 1
            # 2010/11/16: stay in the paragraph.
            body.onBodyChanged(undoType,oldSel=oldSel,oldYview=oldYview)
        else:
            # Advance to the next paragraph.
            ins += 1 # Move past the selection.
            while ins < len(s):
                i,j = g.getLine(s,ins)
                line = s[i:j]
                # 2010/11/16: it's annoying, imo, to treat @ lines differently.
                if line.isspace():
                    ins = j+1
                else:
                    ins = i
                    break
            # setSelectionAreas has destroyed the coloring.
            c.recolor()
        w.setSelectionRange(ins,ins,insert=ins)
        # 2011/10/26: Calling see does more harm than good.
            # w.see(ins)
    #@+node:ekr.20101118113953.5843: *7* rp_wrap_all_lines
    def rp_wrap_all_lines (self,indents,leading_ws,lines,pageWidth):

        '''compute the result of wrapping all lines.'''
        c = self
        trailingNL = lines and lines[-1].endswith('\n')
        lines = [g.choose(z.endswith('\n'),z[:-1],z) for z in lines]
        if len(lines) > 1:
            s = lines[0]
            if c.startsParagraph(s):
                # Adjust indents[1]
                # Similar to code in c.startsParagraph(s)
                i = 0
                if s[0].isdigit():
                    while i < len(s) and s[i].isdigit():
                        i += 1
                    if g.match(s,i,')') or g.match(s,i,'.'):
                        i += 1
                elif s[0].isalpha():
                    if g.match(s,1,')') or g.match(s,1,'.'):
                        i = 2
                elif s[0] == '-':
                    i = 1
                if i > 0:
                    i = g.skip_ws(s,i+1)
                    # Never decrease indentation.
                    if i > indents[1]:
                        indents[1] = i
                        leading_ws[1] = ' '*i
                    # g.trace('indents[1]',indents[1])
                else:
                    g.trace('can not happen')
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
        return result
    #@+node:ekr.20031218072017.1838: *6* updateBodyPane (handles changeNodeContents)
    def updateBodyPane (self,head,middle,tail,undoType,oldSel,oldYview):

        c = self ; body = c.frame.body ; p = c.p

        # Update the text and notify the event handler.
        body.setSelectionAreas(head,middle,tail)

        # Expand the selection.
        head = head or ''
        middle = middle or ''
        tail = tail or ''
        i = len(head)
        j = max(i,len(head)+len(middle)-1)
        newSel = i,j
        body.setSelectionRange(i,j)

        # This handles the undo.
        body.onBodyChanged(undoType,oldSel=oldSel or newSel,oldYview=oldYview)

        # Update the changed mark and icon.
        c.setChanged(True)
        if p.isDirty():
            dirtyVnodeList = []
        else:
            dirtyVnodeList = p.setDirty()

        c.redraw_after_icons_changed()

        # Scroll as necessary.
        if oldYview:
            body.setYScrollPosition(oldYview)
        else:
            body.seeInsertPoint()

        body.setFocus()
        c.recolor()
        return dirtyVnodeList
    #@+node:ekr.20031218072017.2885: *5* Edit Headline submenu
    #@+node:ekr.20031218072017.2886: *6* c.editHeadline
    def editHeadline (self,event=None):

        '''Begin editing the headline of the selected node.'''

        c = self ; k = c.k ; tree = c.frame.tree

        if g.app.batchMode:
            c.notValidInBatchMode("Edit Headline")
            return

        e,wrapper = tree.editLabel(c.p)

        if k:
            # k.setDefaultInputState()
            k.setEditingState()
            k.showStateAndMode(w=wrapper)
    #@+node:ekr.20031218072017.2290: *6* toggleAngleBrackets
    def toggleAngleBrackets (self,event=None):

        '''Add or remove double angle brackets from the headline of the selected node.'''

        c = self ; p = c.p

        if g.app.batchMode:
            c.notValidInBatchMode("Toggle Angle Brackets")
            return

        c.endEditing()
        s = p.h.strip()

        if (s[0:2] == "<<"
            or s[-2:] == ">>"): # Must be on separate line.
            if s[0:2] == "<<": s = s[2:]
            if s[-2:] == ">>": s = s[:-2]
            s = s.strip()
        else:
            s = g.angleBrackets(' ' + s + ' ')

        p.setHeadString(s)
        c.redrawAndEdit(p, selectAll=True)
    #@+node:ekr.20031218072017.2893: *5* notValidInBatchMode
    def notValidInBatchMode(self, commandName):

        g.es('the',commandName,"command is not valid in batch mode")
    #@+node:ekr.20031218072017.2894: *4* Outline menu...
    #@+node:ekr.20031218072017.2895: *5*  Top Level... (Commands)
    #@+node:ekr.20031218072017.1548: *6* c.Cut & Paste Outlines
    #@+node:ekr.20031218072017.1549: *7* c.cutOutline
    def cutOutline (self,event=None):

        '''Delete the selected outline and send it to the clipboard.'''

        c = self
        if c.canDeleteHeadline():
            c.copyOutline()
            c.deleteOutline("Cut Node")
            c.recolor()
    #@+node:ekr.20031218072017.1550: *7* c.copyOutline
    def copyOutline (self,event=None):

        '''Copy the selected outline to the clipboard.'''

        # Copying an outline has no undo consequences.
        c = self
        c.endEditing()
        s = c.fileCommands.putLeoOutline()
        g.app.gui.replaceClipboardWith(s)
    #@+node:ekr.20031218072017.1551: *7* c.pasteOutline
    # To cut and paste between apps, just copy into an empty body first, then copy to Leo's clipboard.

    def pasteOutline(self,event=None,reassignIndices=True):

        '''Paste an outline into the present outline from the clipboard.
        Nodes do *not* retain their original identify.'''

        # trace = False and not g.unitTesting
        c = self
        s = g.app.gui.getTextFromClipboard()
        pasteAsClone = not reassignIndices
        undoType = g.choose(reassignIndices,'Paste Node','Paste As Clone')
        c.endEditing()

        if not s or not c.canPasteOutline(s):
            return # This should never happen.

        isLeo = g.match(s,0,g.app.prolog_prefix_string)

        vnodeInfoDict = c.computeVnodeInfoDict() if pasteAsClone else {}

        # create a *position* to be pasted.
        if isLeo:
            pasted = c.fileCommands.getLeoOutlineFromClipboard(s,reassignIndices)
        else:
            pasted = c.importCommands.convertMoreStringToOutlineAfter(s,c.p)

        if not pasted: return None

        if pasteAsClone:
            copiedBunchList = c.computeCopiedBunchList(pasted,vnodeInfoDict)
        else:
            copiedBunchList = []

        undoData = c.undoer.beforeInsertNode(c.p,
            pasteAsClone=pasteAsClone,copiedBunchList=copiedBunchList)

        c.validateOutline()
        c.selectPosition(pasted)
        pasted.setDirty()
        c.setChanged(True)

        # paste as first child if back is expanded.
        back = pasted.back()

        if back and back.hasChildren() and back.isExpanded():
            # 2011/06/21: fixed hanger: test back.hasChildren().
            pasted.moveToNthChildOf(back,0)

        if pasteAsClone:
            # Set dirty bits for ancestors of *all* pasted nodes.
            # Note: the setDescendentsDirty flag does not do what we want.
            for p in pasted.self_and_subtree():
                p.setAllAncestorAtFileNodesDirty(
                    setDescendentsDirty=False)

        c.undoer.afterInsertNode(pasted,undoType,undoData)
        c.redraw(pasted)
        c.recolor()

        return pasted # For unit testing.
    #@+node:ekr.20050418084539: *8* c.computeVnodeInfoDict
    #@+at
    # 
    # We don't know yet which nodes will be affected by the paste, so we remember
    # everything. This is expensive, but foolproof.
    # 
    # The alternative is to try to remember the 'before' values of nodes in the
    # fileCommands read logic. Several experiments failed, and the code is very ugly.
    # In short, it seems wise to do things the foolproof way.
    # 
    #@@c

    def computeVnodeInfoDict (self):

        c,d = self,{}
        for v in c.all_unique_nodes():
            if v not in d:
                d[v] = g.Bunch(v=v,head=v.h,body=v.b)

        return d
    #@+node:ekr.20050418084539.2: *8* c.computeCopiedBunchList
    def computeCopiedBunchList(self,pasted,vnodeInfoDict):

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
    #@+node:EKR.20040610130943: *7* pasteOutlineRetainingClones
    def pasteOutlineRetainingClones (self,event=None):

        '''Paste an outline into the present outline from the clipboard.
        Nodes *retain* their original identify.'''

        c = self

        return c.pasteOutline(reassignIndices=False)
    #@+node:ekr.20031218072017.2028: *6* c.hoist/dehoist/clearAllHoists
    #@+node:ekr.20120308061112.9865: *7* c.deHoist
    def dehoist (self,event=None):

        '''Undo a previous hoist of an outline.'''

        c = self
        p = c.p

        if p and c.canDehoist():
            bunch = c.hoistStack.pop()
            if bunch.expanded: p.expand()
            else:              p.contract()
            c.redraw()

            c.frame.clearStatusLine()
            if c.hoistStack:
                bunch = c.hoistStack[-1]
                c.frame.putStatusLine("Hoist: " + bunch.p.h)
            else:
                c.frame.putStatusLine("No hoist")
            c.undoer.afterDehoist(p,'DeHoist')
            g.doHook('hoist-changed',c=c)

    #@+node:ekr.20120308061112.9866: *7* c.clearAllHoists
    def clearAllHoists(self):

        '''Undo a previous hoist of an outline.'''

        c = self

        c.hoistStack = []
        c.frame.putStatusLine("Hoists cleared")

        g.doHook('hoist-changed',c=c)
    #@+node:ekr.20120308061112.9867: *7* c.hoist
    def hoist (self,event=None):

        '''Make only the selected outline visible.'''

        c = self
        p = c.p

        if p and c.canHoist():
            # Remember the expansion state.
            bunch = g.Bunch(p=p.copy(),expanded=p.isExpanded())
            c.hoistStack.append(bunch)
            p.expand()
            c.redraw(p)

            c.frame.clearStatusLine()
            c.frame.putStatusLine("Hoist: " + p.h)
            c.undoer.afterHoist(p,'Hoist')
            g.doHook('hoist-changed',c=c)
    #@+node:ekr.20031218072017.1759: *6* Insert, Delete & Clone (Commands)
    #@+node:ekr.20031218072017.1760: *7* c.checkMoveWithParentWithWarning & c.checkDrag
    #@+node:ekr.20070910105044: *8* c.checkMoveWithParentWithWarning
    def checkMoveWithParentWithWarning (self,root,parent,warningFlag):

        """Return False if root or any of root's descedents is a clone of
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
                    g.app.unitTestDict['checkMoveWithParentWithWarning']=True
                elif warningFlag:
                    c.alert(message)
                return False
        return True
    #@+node:ekr.20070910105044.1: *8* c.checkDrag
    def checkDrag (self,root,target):

        """Return False if target is any descendant of root."""

        c = self
        message = "Can not drag a node into its descendant tree."

        for z in root.subtree():
            if z == target:
                if g.app.unitTesting:
                    g.app.unitTestDict['checkMoveWithParentWithWarning']=True
                else:
                    c.alert(message)
                return False
        return True
    #@+node:ekr.20031218072017.1193: *7* c.deleteOutline
    def deleteOutline (self,event=None,op_name="Delete Node"):

        """Deletes the selected outline."""

        c = self ; cc = c.chapterController ; u = c.undoer
        p = c.p
        if not p: return

        c.endEditing() # Make sure we capture the headline for Undo.

        if p.hasVisBack(c): newNode = p.visBack(c)
        else: newNode = p.next() # _not_ p.visNext(): we are at the top level.
        if not newNode: return

        if cc: # Special cases for @chapter and @chapters nodes.
            chapter = '@chapter ' ; chapters = '@chapters ' 
            h = p.h
            if h.startswith(chapters):
                if p.hasChildren():
                    return cc.note('Can not delete @chapters node with children.')
            elif h.startswith(chapter):
                name = h[len(chapter):].strip()
                if name:
                    # Bug fix: 2009/3/23: Make sure the chapter exists!
                    # This might be an @chapter node outside of @chapters tree.
                    theChapter = cc.chaptersDict.get(name)
                    if theChapter:
                        return cc.removeChapterByName(name)

        undoData = u.beforeDeleteNode(p)
        dirtyVnodeList = p.setAllAncestorAtFileNodesDirty()
        p.doDelete(newNode)
        c.setChanged(True)
        u.afterDeleteNode(newNode,op_name,undoData,dirtyVnodeList=dirtyVnodeList)
        c.redraw(newNode)

        c.validateOutline()
    #@+node:ekr.20031218072017.1761: *7* c.insertHeadline
    def insertHeadline (self,event=None,op_name="Insert Node",as_child=False):

        '''Insert a node after the presently selected node.'''

        c = self ; u = c.undoer
        current = c.p
        if not current: return
        c.endEditing()
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
        g.doHook('create-node',c=c,p=p)
        p.setDirty(setDescendentsDirty=False)
        dirtyVnodeList = p.setAllAncestorAtFileNodesDirty()
        c.setChanged(True)
        u.afterInsertNode(p,op_name,undoData,dirtyVnodeList=dirtyVnodeList)
        c.redrawAndEdit(p,selectAll=True)
        return p
    #@+node:ekr.20130922133218.11540: *7* c.insertHeadlineBefore (new in Leo 4.11)
    def insertHeadlineBefore (self,event=None):

        '''Insert a node before the presently selected node.'''

        c,current,u = self,self.p,self.undoer
        op_name = 'Insert Node Before'
        if not current: return
        # Can not insert before the base of a hoist.
        if c.hoistStack and current == c.hoistStack[-1].p:
            g.warning('can not insert a node before the base of a hoist')
            return
        c.endEditing()
        undoData = u.beforeInsertNode(current)
        p = current.insertBefore()
        g.doHook('create-node',c=c,p=p)
        p.setDirty(setDescendentsDirty=False)
        dirtyVnodeList = p.setAllAncestorAtFileNodesDirty()
        c.setChanged(True)
        u.afterInsertNode(p,op_name,undoData,dirtyVnodeList=dirtyVnodeList)
        c.redrawAndEdit(p,selectAll=True)
        return p
    #@+node:ekr.20071005173203.1: *7* c.insertChild
    def insertChild (self,event=None):

        '''Insert a node after the presently selected node.'''

        c = self

        return c.insertHeadline(event=event,op_name='Insert Child',as_child=True)
    #@+node:ekr.20031218072017.1762: *7* c.clone
    def clone (self,event=None):

        '''Create a clone of the selected outline.'''

        c = self ; u = c.undoer ; p = c.p
        if not p: return

        undoData = c.undoer.beforeCloneNode(p)
        c.endEditing() # Capture any changes to the headline.
        clone = p.clone()
        dirtyVnodeList = clone.setAllAncestorAtFileNodesDirty()
        c.setChanged(True)
        if c.validateOutline():
            u.afterCloneNode(clone,'Clone Node',undoData,dirtyVnodeList=dirtyVnodeList)
            c.redraw(clone)
            return clone # For mod_labels and chapters plugins.
        else:
            clone.doDelete()
            c.setCurrentPosition(p)
            return None
    #@+node:ekr.20031218072017.1765: *7* c.validateOutline
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
    #@+node:ekr.20080425060424.1: *6* Sort...
    #@+node:ekr.20080503055349.1: *7* c.setPositionAfterSort
    def setPositionAfterSort (self,sortChildren):

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
                p = leoNodes.position(parent_v.children[0])
            while p and p.v != p_v:
                p.moveToNext()
            p = p or parent

        return p
    #@+node:ekr.20050415134809: *7* c.sortChildren
    # New in Leo 4.7 final: this method no longer supports
    # the 'cmp' keyword arg.

    def sortChildren (self,event=None,key=None):

        '''Sort the children of a node.'''

        c = self ; p = c.p

        if p and p.hasChildren():
            c.sortSiblings(p=p.firstChild(),sortChildren=True,key=key)
    #@+node:ekr.20050415134809.1: *7* c.sortSiblings
    # New in Leo 4.7 final: this method no longer supports
    # the 'cmp' keyword arg.

    def sortSiblings (self, event=None, key= None, p=None, sortChildren=False,
                      reverse=False):

        '''Sort the siblings of a node.'''

        c = self ; u = c.undoer
        if p is None: p = c.p
        if not p: return

        c.endEditing()

        undoType = g.choose(sortChildren,'Sort Children','Sort Siblings')
        parent_v = p._parentVnode()
        parent = p.parent()
        oldChildren = parent_v.children[:]
        newChildren = parent_v.children[:]

        if key == None:
            def lowerKey (self):
                return (self.h.lower())
            key = lowerKey

        newChildren.sort(key=key, reverse=reverse)

        if oldChildren == newChildren:
            return

        # 2010/01/20. Fix bug 510148.
        c.setChanged(True)

        # g.trace(g.listToString(newChildren))

        bunch = u.beforeSort(p,undoType,oldChildren,newChildren,sortChildren)
        parent_v.children = newChildren
        if parent:
            dirtyVnodeList = parent.setAllAncestorAtFileNodesDirty()
        else:
            dirtyVnodeList = []
        u.afterSort(p,bunch,dirtyVnodeList)

        # Sorting destroys position p, and possibly the root position.
        p = c.setPositionAfterSort(sortChildren)
        c.redraw(p)
    #@+node:ekr.20040711135959.2: *5* Check Outline submenu...
    #@+node:ekr.20031218072017.2072: *6* c.checkOutline
    def checkOutline (self,event=None,verbose=True,unittest=False,full=True,root=None):

        """Report any possible clone errors in the outline.

        Remove any tnodeLists."""

        trace = False and not g.unitTesting
        c = self ; count = 1 ; errors = 0

        if full and not unittest:
            g.blue("all tests enabled: this may take awhile")

        if root: iter = root.self_and_subtree
        else:    iter = c.all_positions

        for p in iter():
            if trace: g.trace(p.h)
            try:
                count += 1
                #@+<< remove tnodeList >>
                #@+node:ekr.20040313150633: *7* << remove tnodeList >>
                # Empty tnodeLists are not errors.
                v = p.v

                if hasattr(v,"tnodeList"): # and len(v.tnodeList) > 0 and not v.isAnyAtFileNode():
                    if 0:
                        s = "deleting tnodeList for " + repr(v)
                        g.warning(s)
                    delattr(v,"tnodeList")
                    v._p_changed = True
                #@-<< remove tnodeList >>
                if full: # Unit tests usually set this false.
                    #@+<< do full tests >>
                    #@+node:ekr.20040323155951: *7* << do full tests >>
                    if not unittest:
                        if count % 1000 == 0:
                            g.es('','.',newline=False)
                        if count % 8000 == 0:
                            g.enl()

                    #@+others
                    #@+node:ekr.20040314035615: *8* assert consistency of threadNext & threadBack links
                    threadBack = p.threadBack()
                    threadNext = p.threadNext()

                    if threadBack:
                        assert p == threadBack.threadNext(), "p!=p.threadBack().threadNext()"

                    if threadNext:
                        assert p == threadNext.threadBack(), "p!=p.threadNext().threadBack()"
                    #@+node:ekr.20040314035615.1: *8* assert consistency of next and back links
                    back = p.back()
                    next = p.next()

                    if back:
                        assert p == back.next(), 'p!=p.back().next(),  back: %s\nback.next: %s' % (
                            back,back.next())

                    if next:
                        assert p == next.back(), 'p!=p.next().back, next: %s\nnext.back: %s' % (
                            next,next.back())
                    #@+node:ekr.20040314035615.2: *8* assert consistency of parent and child links
                    if p.hasParent():
                        n = p.childIndex()
                        assert p == p.parent().moveToNthChild(n), "p!=parent.moveToNthChild"

                    for child in p.children():
                        assert p == child.parent(), "p!=child.parent"

                    if p.hasNext():
                        assert p.next().parent() == p.parent(), "next.parent!=parent"

                    if p.hasBack():
                        assert p.back().parent() == p.parent(), "back.parent!=parent"
                    #@+node:ekr.20080426051658.1: *8* assert consistency of parent and children arrays
                    #@+at
                    # Every nodes gets visited, so we only check consistency
                    # between p and its parent, not between p and its children.
                    # 
                    # In other words, this is a strong test.
                    #@@c

                    parent_v = p._parentVnode()
                    n = p.childIndex()

                    assert parent_v.children[n] == p.v,'fail 1'
                    #@-others
                    #@-<< do full tests >>
            except AssertionError:
                errors += 1
                #@+<< give test failed message >>
                #@+node:ekr.20040314044652: *7* << give test failed message >>
                junk, value, junk = sys.exc_info()

                g.error("test failed at position %s\n%s" % (repr(p),value))
                #@-<< give test failed message >>
                if trace: return errors 
        if verbose or not unittest:
            #@+<< print summary message >>
            #@+node:ekr.20040314043900: *7* <<print summary message >>
            if full:
                g.enl()

            if errors or verbose:
                # color = g.choose(errors,'red','blue')
                # g.es_print('',count,'nodes checked',errors,'errors',color=color)
                if errors:
                    g.error('',count,'nodes checked',errors,'errors')
                else:
                    g.blue('',count,'nodes checked',errors,'errors')

            #@-<< print summary message >>
        return errors
    #@+node:ekr.20040723094220: *6* Check Outline commands & allies
    # This code is no longer used by any Leo command,
    # but it will be retained for use of scripts.
    #@+node:ekr.20040723094220.1: *7* c.checkAllPythonCode
    def checkAllPythonCode(self,event=None,unittest=False,ignoreAtIgnore=True):

        '''Check all nodes in the selected tree for syntax and tab errors.'''

        c = self ; count = 0 ; result = "ok"

        for p in c.all_unique_positions():
            count += 1
            if not unittest:
                #@+<< print dots >>
                #@+node:ekr.20040723094220.2: *8* << print dots >>
                if count % 100 == 0:
                    g.es('','.',newline=False)

                if count % 2000 == 0:
                    g.enl()
                #@-<< print dots >>

            if g.scanForAtLanguage(c,p) == "python":
                if not g.scanForAtSettings(p) and (
                    not ignoreAtIgnore or not g.scanForAtIgnore(c,p)
                ):
                    try:
                        c.checkPythonNode(p,unittest)
                    except (SyntaxError,tokenize.TokenError,tabnanny.NannyNag):
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
    def checkPythonCode (self,event=None,
        unittest=False,ignoreAtIgnore=True,
        suppressErrors=False,checkOnSave=False):

        '''Check the selected tree for syntax and tab errors.'''

        c = self ; count = 0 ; result = "ok"

        if not unittest:
            g.es("checking Python code   ")

        for p in c.p.self_and_subtree():

            count += 1
            if not unittest and not checkOnSave:
                #@+<< print dots >>
                #@+node:ekr.20040723094220.4: *8* << print dots >>
                if count % 100 == 0:
                    g.es('','.',newline=False)

                if count % 2000 == 0:
                    g.enl()
                #@-<< print dots >>

            if g.scanForAtLanguage(c,p) == "python":
                if not ignoreAtIgnore or not g.scanForAtIgnore(c,p):
                    try:
                        c.checkPythonNode(p,unittest,suppressErrors)
                    except (SyntaxError,tokenize.TokenError,tabnanny.NannyNag):
                        result = "error" # Continue to check.
                    except Exception:
                        return "surprise" # abort

        if not unittest:
            g.blue("check complete")

        # We _can_ return a result for unit tests because we aren't using doCommand.
        return result
    #@+node:ekr.20040723094220.5: *7* c.checkPythonNode
    def checkPythonNode (self,p,unittest=False,suppressErrors=False):

        c = self ; h = p.h

        # Call getScript to ignore directives and section references.
        body = g.getScript(c,p.copy())
        if not body: return

        try:
            fn = '<node: %s>' % p.h
            if not g.isPython3:
                body = g.toEncodedString(body)
            compile(body+'\n',fn,'exec')
            c.tabNannyNode(p,h,body,unittest,suppressErrors)
        except SyntaxError:
            if not suppressErrors:
                g.warning("Syntax error in: %s" % h)
                g.es_exception(full=False,color="black")
            if unittest: raise
        except Exception:
            g.es_print('unexpected exception')
            g.es_exception()
            if unittest: raise

    #@+node:ekr.20040723094220.6: *7* c.tabNannyNode
    # This code is based on tabnanny.check.

    def tabNannyNode (self,p,headline,body,unittest=False,suppressErrors=False):

        """Check indentation using tabnanny."""

        # c = self
        try:
            readline = g.readLinesClass(body).next
            tabnanny.process_tokens(tokenize.generate_tokens(readline))

        except IndentationError:
            junk,msg,junk = sys.exc_info()
            if not suppressErrors:
                g.warning("IndentationError in",headline)
                g.es('',msg)
            if unittest: raise

        except tokenize.TokenError:
            junk, msg, junk = sys.exc_info()
            if not suppressErrors:
                g.warning("TokenError in",headline)
                g.es('',msg)
            if unittest: raise

        except tabnanny.NannyNag:
            junk, nag, junk = sys.exc_info()
            if not suppressErrors:
                badline = nag.get_lineno()
                line    = nag.get_line()
                message = nag.get_msg()
                g.warning("indentation error in",headline,"line",badline)
                g.es(message)
                line2 = repr(str(line))[1:-1]
                g.es("offending line:\n",line2)
            if unittest: raise

        except Exception:
            g.trace("unexpected exception")
            g.es_exception()
            if unittest: raise
    #@+node:ekr.20040412060927: *6* c.dumpOutline
    def dumpOutline (self,event=None):

        """ Dump all nodes in the outline."""

        c = self
        seen = {}

        print ; print('='*40)
        v = c.hiddenRootNode
        v.dump()
        seen[v] = True
        for p in c.all_positions():
            if p.v not in seen:
                seen[p.v] = True
                p.v.dump()
    #@+node:ekr.20040711135959.1: *6* Pretty Print commands
    #@+node:ekr.20110917174948.6903: *7* class CPrettyPrinter
    class CPrettyPrinter:

        #@+others
        #@+node:ekr.20110917174948.6904: *8* __init__ (CPrettyPrinter)
        def __init__ (self,c):

            self.c = c
            self.p = None # Set in indent.

            self.brackets = 0
                # The brackets indentation level.
            self.parens = 0
                # The parenthesis nesting level.
            self.result = []
                # The list of tokens that form the final result.
            self.tab_width = 4
                # The number of spaces in each unit of leading indentation.

            # No longer used.

            # self.ignored_brackets = 0
                # # The number of '}' to ignore before reducing self.brackets.
            # self.ignore_ws = False
                # # True: ignore the next whitespace token if any.
        #@+node:ekr.20110917174948.6911: *8* indent & helpers
        def indent (self,p,toList=False,giveWarnings=True):

            # c = self.c
            if not p.b: return
            self.p = p.copy()

            aList = self.tokenize(p.b)
            assert ''.join(aList) == p.b

            aList = self.add_statement_braces(aList,giveWarnings=giveWarnings)

            self.bracketLevel = 0
            self.parens = 0
            self.result = []
            for s in aList:
                # g.trace(repr(s))
                self.put_token(s)

            if 0:
                for z in self.result:
                    print(repr(z))

            if toList:
                return self.result
            else:
                return ''.join(self.result)
        #@+node:ekr.20110918225821.6815: *9* add_statement_braces
        def add_statement_braces (self,s,giveWarnings=False):

            p = self.p
            trace = False

            def oops(message,i,j):
                # This can be called from c-to-python, in which case warnings should be suppressed.
                if giveWarnings:
                    g.error('** changed ',p.h)
                    g.es_print('%s after\n%s' % (
                        message,repr(''.join(s[i:j]))))

            i,n,result = 0,len(s),[]
            while i < n:
                token_ = s[i] # token is a module.
                progress = i
                if token_ in ('if','for','while',):
                    j = self.skip_ws_and_comments(s,i+1)
                    if self.match(s,j,'('):
                        j = self.skip_parens(s,j)
                        if self.match(s,j,')'):
                            old_j = j+1
                            j = self.skip_ws_and_comments(s,j+1)
                            if self.match(s,j,';'):
                                # Example: while (*++prefix);
                                result.extend(s[i:j])
                            elif self.match(s,j,'{'):
                                result.extend(s[i:j])
                            else:
                                oops("insert '{'",i,j)
                                # Back up, and don't go past a newline or comment.
                                j = self.skip_ws(s,old_j)
                                result.extend(s[i:j])
                                result.append(' ')
                                result.append('{')
                                result.append('\n')
                                i = j
                                j = self.skip_statement(s,i)
                                result.extend(s[i:j])
                                result.append('\n')
                                result.append('}')
                                oops("insert '}'",i,j)
                        else:
                            oops("missing ')'",i,j)
                            result.extend(s[i:j])
                    else:
                        oops("missing '('",i,j)
                        result.extend(s[i:j])
                    i = j
                else:
                    result.append(token_)
                    i += 1
                assert progress < i

            if trace: g.trace(''.join(result))
            return result

        #@+node:ekr.20110919184022.6903: *10* skip_ws
        def skip_ws (self,s,i):

            while i < len(s):
                token_ = s[i] # token is a module.
                if token_.startswith(' ') or token_.startswith('\t'):
                    i += 1
                else:
                    break

            return i
        #@+node:ekr.20110918225821.6820: *10* skip_ws_and_comments
        def skip_ws_and_comments (self,s,i):

            while i < len(s):
                token_ = s[i] # token is a module.
                if token_.isspace():
                    i += 1
                elif token_.startswith('//') or token_.startswith('/*'):
                    i += 1
                else:
                    break

            return i
        #@+node:ekr.20110918225821.6817: *10* skip_parens
        def skip_parens(self,s,i):

            '''Skips from the opening ( to the matching ).

            If no matching is found i is set to len(s)'''

            assert(self.match(s,i,'('))

            level = 0
            while i < len(s):
                ch = s[i]
                if ch == '(':
                    level += 1 ; i += 1
                elif ch == ')':
                    level -= 1
                    if level <= 0:  return i
                    i += 1
                else: i += 1
            return i
        #@+node:ekr.20110918225821.6818: *10* skip_statement
        def skip_statement (self,s,i):

            '''Skip to the next ';' or '}' token.'''

            while i < len(s):
                if s[i] in ';}':
                    i += 1
                    break
                else:
                    i += 1
            return i
        #@+node:ekr.20110917204542.6967: *9* put_token & helpers
        def put_token (self,s):

            '''Append token s to self.result as is,
            *except* for adjusting leading whitespace and comments.

            '{' tokens bump self.brackets or self.ignored_brackets.
            self.brackets determines leading whitespace.
            '''

            if s == '{':
                self.brackets += 1
            elif s == '}':
                self.brackets -= 1
                self.remove_indent()
            elif s == '(':
                self.parens += 1
            elif s == ')':
                self.parens -= 1
            elif s.startswith('\n'):
                if self.parens <= 0:
                    s = '\n%s' % (' ' * self.brackets * self.tab_width)
                else: pass # Use the existing indentation.
            elif s.isspace():
                if self.parens <= 0 and self.result and self.result[-1].startswith('\n'):
                    # Kill the whitespace.
                    s = ''
                else: pass # Keep the whitespace.
            elif s.startswith('/*'):
                s = self.reformat_block_comment(s)
            else:
                pass # put s as it is.

            if s:
                self.result.append(s)

        #@+at
        #     # It doesn't hurt to increase indentation after *all* '{'.
        #     if s == '{':
        #         # Increase brackets unless '=' precedes it.
        #         if self.prev_token('='):
        #             self.ignored_brackets += 1
        #         else:
        #             self.brackets += 1
        #     elif s == '}':
        #         if self.ignored_brackets:
        #             self.ignored_brackets -= 1
        #         else:
        #             self.brackets -= 1
        #             self.remove_indent()
        #@+node:ekr.20110917204542.6968: *10* prev_token
        def prev_token (self,s):

            '''Return the previous token, ignoring whitespace and comments.'''

            i = len(self.result)-1
            while i >= 0:
                s2 = self.result[i]
                if s == s2:
                    return True
                elif s.isspace() or s.startswith('//') or s.startswith ('/*'):
                    i -= 1
                else:
                    return False
        #@+node:ekr.20110918184425.6916: *10* reformat_block_comment
        def reformat_block_comment (self,s):

            return s
        #@+node:ekr.20110917204542.6969: *10* remove_indent
        def remove_indent (self):

            '''Remove one tab-width of blanks from the previous token.'''

            w = abs(self.tab_width)

            if self.result:
                s = self.result[-1]
                if s.isspace():
                    self.result.pop()
                    s = s.replace('\t',' ' * w)
                    if s.startswith('\n'):
                        s2 = s[1:]
                        self.result.append('\n'+s2[:-w])
                    else:
                        self.result.append(s[:-w])
        #@+node:ekr.20110918225821.6819: *8* match
        def match(self,s,i,pat):

            return i < len(s) and s[i] == pat
        #@+node:ekr.20110917174948.6930: *8* tokenize & helper
        def tokenize (self,s):

            '''Tokenize comments, strings, identifiers, whitespace and operators.'''

            i,result = 0,[]
            while i < len(s):
                # Loop invariant: at end: j > i and s[i:j] is the new token.
                j = i
                ch = s[i]
                if ch in '@\n': # Make *sure* these are separate tokens.
                    j += 1
                elif ch == '#': # Preprocessor directive.
                    j = g.skip_to_end_of_line(s,i)
                elif ch in ' \t':
                    j = g.skip_ws(s,i)
                elif ch.isalpha() or ch == '_':
                    j = g.skip_c_id(s,i)
                elif g.match(s,i,'//'):
                    j = g.skip_line(s,i)
                elif g.match(s,i,'/*'):
                    j = self.skip_block_comment(s,i)
                elif ch in "'\"":
                    j = g.skip_string(s,i)
                else:
                    j += 1

                assert j > i
                result.append(''.join(s[i:j]))
                i = j # Advance.

            return result

        #@+at The following could be added to the 'else' clause::
        #     # Accumulate everything else.
        #     while (
        #         j < n and
        #         not s[j].isspace() and
        #         not s[j].isalpha() and
        #         not s[j] in '"\'_@' and
        #             # start of strings, identifiers, and single-character tokens.
        #         not g.match(s,j,'//') and
        #         not g.match(s,j,'/*') and
        #         not g.match(s,j,'-->')
        #     ):
        #         j += 1
        #@+node:ekr.20110917193725.6974: *9* skip_block_comment
        def skip_block_comment (self,s,i):

            assert(g.match(s,i,"/*"))

            j = s.find("*/",i)
            if j == -1:
                return len(s)
            else:
                return j + 2
        #@-others
    #@+node:ekr.20040711135244.5: *7* class PythonPrettyPrinter
    class PythonPrettyPrinter:

        #@+others
        #@+node:ekr.20040711135244.6: *8* __init__ (PythonPrettyPrinter)
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
            self.p = c.p
            self.parenLevel = 0
            self.prevName = None
            self.s = None # The string containing the line.
            self.squareBracketLevel = 0
            self.srow = self.scol = 0 # The starting row/col of the token.
            self.startline = True # True: the token starts a line.
            self.tracing = False
            #@+<< define dispatch dict >>
            #@+node:ekr.20041021100850: *9* << define dispatch dict >>
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
            #@-<< define dispatch dict >>
        #@+node:ekr.20040713093048: *8* clear
        def clear (self):
            self.lines = []
        #@+node:ekr.20040713064323: *8* dumpLines
        def dumpLines (self,p,lines):

            g.pr('\n','-'*10,p.cleanHeadString())

            if 0:
                for line in lines:
                    line2 = g.toEncodedString(line,reportErrors=True)
                    g.pr(line2,newline=False) # Don't add a trailing newline!)
            else:
                for i in range(len(lines)):
                    line = lines[i]
                    line = g.toEncodedString(line,reportErrors=True)
                    g.pr("%3d" % i, repr(lines[i]))
        #@+node:ekr.20040711135244.7: *8* dumpToken
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
        #@+node:ekr.20040713091855: *8* endUndo
        def endUndo (self):

            c = self.c ; u = c.undoer ; undoType = 'Pretty Print'
            current = c.p

            if self.changed:
                # Tag the end of the command.
                u.afterChangeGroup(current,undoType,dirtyVnodeList=self.dirtyVnodeList)
        #@+node:ekr.20040711135244.8: *8* get
        def get (self):

            if self.lastName != 'newline' and self.lines:
                # Strip the trailing whitespace from the last line.
                self.lines[-1] = self.lines[-1].rstrip()

            return self.lines
        #@+node:ekr.20040711135244.4: *8* prettyPrintNode
        def prettyPrintNode(self,p,dump):

            # c = self.c
            h = p.h
            s = p.b
            if not s: return

            readlines = g.readLinesClass(s).next

            try:
                self.clear()
                for token5tuple in tokenize.generate_tokens(readlines):
                    self.putToken(token5tuple)
                lines = self.get()

            except tokenize.TokenError:
                g.warning("error pretty-printing",h,"not changed.")
                return

            if dump:
                self.dumpLines(p,lines)
            else:
                self.replaceBody(p,lines)
        #@+node:ekr.20040711135244.9: *8* put
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
        #@+node:ekr.20041021104237: *8* putArray
        def putArray (self):

            """Add the next text by joining all the strings is self.array"""

            self.lines.append(''.join(self.array))
            self.array = []
            self.lineParenLevel = 0
        #@+node:ekr.20040711135244.10: *8* putNormalToken & allies
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
        #@+node:ekr.20041021102938: *9* doEndMarker
        def doEndMarker (self):

            self.putArray()
        #@+node:ekr.20041021102340.1: *9* doErrorToken
        def doErrorToken (self):

            self.array.append(self.val)

            # This code is executed for versions of Python earlier than 2.4
            if self.val == '@':
                # Preserve whitespace after @.
                i = g.skip_ws(self.s,self.scol+1)
                ws = self.s[self.scol+1:i]
                if ws:
                    self.array.append(ws)
        #@+node:ekr.20041021102340.2: *9* doIndent & doDedent
        def doDedent (self):

            pass

        def doIndent (self):

            self.array.append(self.val)
        #@+node:ekr.20041021102340: *9* doMultiLine (strings, etc).
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
        #@+node:ekr.20041021101911.5: *9* doName
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
        #@+node:ekr.20041021101911.3: *9* doNewline
        def doNewline (self):

            # Remove trailing whitespace.
            # This never removes trailing whitespace from multi-line tokens.
            if self.array:
                self.array[-1] = self.array[-1].rstrip()

            self.array.append('\n')
            self.putArray()
        #@+node:ekr.20041021101911.6: *9* doNumber
        def doNumber (self):

            self.array.append(self.val)
        #@+node:ekr.20040711135244.11: *9* doOp
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
        #@+node:ekr.20041021112219: *9* doStartLine
        def doStartLine (self):

            before = self.s[0:self.scol]
            i = g.skip_ws(before,0)
            self.ws = self.s[0:i]

            if self.ws:
                self.array.append(self.ws)
        #@+node:ekr.20041021101911.1: *9* oops
        def oops(self):

            g.pr("unknown PrettyPrinting code: %s" % (self.name))
        #@+node:ekr.20041021101911.2: *9* trace (PrettyPrint)
        def trace(self):

            if self.tracing:

                g.trace("%10s: %s" % (
                    self.name,
                    repr(g.toEncodedString(self.val))
                ))
        #@+node:ekr.20040711135244.12: *8* putToken
        def putToken (self,token5tuple):

            if self.dumping:
                self.dumpToken(token5tuple)
            else:
                self.putNormalToken(token5tuple)
        #@+node:ekr.20040713070356: *8* replaceBody
        def replaceBody (self,p,lines):

            c = self.c ; u = c.undoer ; undoType = 'Pretty Print'
            # sel = c.frame.body.getInsertPoint()
            oldBody = p.b
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
        #@-others
    #@+node:ekr.20040712053025: *7* prettyPrintAllPythonCode
    def prettyPrintAllPythonCode (self,event=None,dump=False):

        '''Reformat all Python code in the outline to make it look more beautiful.'''

        c = self ; pp = c.PythonPrettyPrinter(c)

        for p in c.all_unique_positions():

            # Unlike c.scanAllDirectives, scanForAtLanguage ignores @comment.
            if g.scanForAtLanguage(c,p) == "python":
                pp.prettyPrintNode(p,dump=dump)

        pp.endUndo()

    # For unit test of inverse commands dict.
    def beautifyAllPythonCode (self,event=None,dump=False):

        '''Reformat all Python code in the outline.'''

        return self.prettyPrintAllPythonCode (event,dump)
    #@+node:ekr.20110917174948.6877: *7* beautifyCCode
    def beautifyCCode (self,event=None):

        '''Reformat all C code in the selected tree.'''

        c = self
        pp = c.CPrettyPrinter(c)
        u = c.undoer ; undoType = 'beautify-c'

        u.beforeChangeGroup(c.p,undoType)
        dirtyVnodeList = []
        changed = False

        for p in c.p.self_and_subtree():
            if g.scanForAtLanguage(c,p) == "c":
                bunch = u.beforeChangeNodeContents(p)
                s = pp.indent(p)
                if p.b != s:
                    # g.es('changed: %s' % (p.h))
                    p.b = s
                    p.v.setDirty()
                    dirtyVnodeList.append(p.v)
                    u.afterChangeNodeContents(p,undoType,bunch)
                    changed = True

        if changed:
            u.afterChangeGroup(c.p,undoType,
                reportFlag=False,dirtyVnodeList=dirtyVnodeList)

        c.bodyWantsFocus()
    #@+node:ekr.20040712053025.1: *7* prettyPrintPythonCode
    def prettyPrintPythonCode (self,event=None,p=None,dump=False):

        '''Reformat all Python code in the selected tree.'''

        c = self

        if p: root = p.copy()
        else: root = c.p

        pp = c.PythonPrettyPrinter(c)

        for p in root.self_and_subtree():

            # Unlike c.scanAllDirectives, scanForAtLanguage ignores @comment.
            if g.scanForAtLanguage(c,p) == "python":

                pp.prettyPrintNode(p,dump=dump)

        pp.endUndo()

    # For unit test of inverse commands dict.
    def beautifyPythonCode (self,event=None,dump=False):

        '''Beautify all Python code in the selected tree.'''
        return self.prettyPrintPythonCode (event,dump)

    #@+node:ekr.20050729211526: *7* prettyPrintPythonNode
    def prettyPrintPythonNode (self,p=None,dump=False):

        c = self

        if not p:
            p = c.p

        pp = c.PythonPrettyPrinter(c)

        # Unlike c.scanAllDirectives, scanForAtLanguage ignores @comment.
        if g.scanForAtLanguage(c,p) == "python":
            pp.prettyPrintNode(p,dump=dump)

        pp.endUndo()
    #@+node:ekr.20071001075704: *7* prettyPrintPythonTree
    def prettyPrintPythonTree (self,event=None,dump=False):

        '''Beautify all Python code in the selected outline.'''

        c = self ; p = c.p ; pp = c.PythonPrettyPrinter(c)

        for p in p.self_and_subtree():

            # Unlike c.scanAllDirectives, scanForAtLanguage ignores @comment.
            if g.scanForAtLanguage(c,p) == "python":

                pp.prettyPrintNode(p,dump=dump)

        pp.endUndo()

    # For unit test of inverse commands dict.
    def beautifyPythonTree (self,event=None,dump=False):

        '''Beautify all Python code in the selected outline.'''

        return self.prettyPrintPythonTree (event,dump)
    #@+node:ekr.20031218072017.2898: *5* Expand & Contract...
    #@+node:ekr.20031218072017.2899: *6* Commands (outline menu)
    #@+node:ekr.20031218072017.2900: *7* contractAllHeadlines
    def contractAllHeadlines (self,event=None):

        '''Contract all nodes in the outline.'''

        c = self

        for p in c.all_unique_positions():
            p.contract()
        # Select the topmost ancestor of the presently selected node.
        p = c.p
        while p and p.hasParent():
            p.moveToParent()

        c.redraw(p,setFocus=True)

        c.expansionLevel = 1 # Reset expansion level.
    #@+node:ekr.20080819075811.3: *7* contractAllOtherNodes & helper
    def contractAllOtherNodes (self,event=None):

        '''Contract all nodes except those needed to make the
        presently selected node visible.'''

        c = self ; leaveOpen = c.p

        for p in c.rootPosition().self_and_siblings():
            c.contractIfNotCurrent(p,leaveOpen)

        c.redraw()

    #@+node:ekr.20080819075811.7: *8* contractIfNotCurrent
    def contractIfNotCurrent(self,p,leaveOpen):

        c = self

        if p == leaveOpen or not p.isAncestorOf(leaveOpen):
            p.contract()

        for child in p.children():
            if child != leaveOpen and child.isAncestorOf(leaveOpen):
                c.contractIfNotCurrent(child,leaveOpen)
            else:
                for p2 in child.self_and_subtree():
                    p2.contract()
    #@+node:ekr.20031218072017.2901: *7* contractNode
    def contractNode (self,event=None):

        '''Contract the presently selected node.'''

        c = self ; p = c.p

        p.contract()

        if p.isCloned():
            c.redraw() # A full redraw is necessary to handle clones.
        else:
            c.redraw_after_contract(p=p,setFocus=True)
    #@+node:ekr.20040930064232: *7* contractNodeOrGoToParent
    def contractNodeOrGoToParent (self,event=None):

        """Simulate the left Arrow Key in folder of Windows Explorer."""

        c = self ; p = c.p

        parent = p.parent()
        redraw = False

        if p.hasChildren() and p.isExpanded():
            c.contractNode()

        elif parent and parent.isVisible(c):
            # New in Leo 4.9.1: contract all children first.
            if c.collapse_on_lt_arrow:
                for child in parent.children():
                    if child.isExpanded():
                        child.contract()
                        redraw = True
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
    #@+node:ekr.20031218072017.2902: *7* contractParent
    def contractParent (self,event=None):

        '''Contract the parent of the presently selected node.'''

        c = self ; p = c.p

        parent = p.parent()
        if not parent: return

        parent.contract()

        c.redraw_after_contract(p=parent)
    #@+node:ekr.20031218072017.2903: *7* expandAllHeadlines
    def expandAllHeadlines (self,event=None):

        '''Expand all headlines.
        Warning: this can take a long time for large outlines.'''

        c = self

        p = c.rootPosition()
        while p:
            c.expandSubtree(p)
            p.moveToNext()

        c.redraw_after_expand(p=c.rootPosition(),setFocus=True)

        c.expansionLevel = 0 # Reset expansion level.
    #@+node:ekr.20031218072017.2904: *7* expandAllSubheads
    def expandAllSubheads (self,event=None):

        '''Expand all children of the presently selected node.'''

        c = self ; p = c.p
        if not p: return

        child = p.firstChild()
        c.expandSubtree(p)
        while child:
            c.expandSubtree(child)
            child = child.next()

        c.redraw(p,setFocus=True)
    #@+node:ekr.20031218072017.2905: *7* expandLevel1..9
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
    #@+node:ekr.20031218072017.2906: *7* expandNextLevel
    def expandNextLevel (self,event=None):

        '''Increase the expansion level of the outline and
        Expand all nodes at that level or lower.'''

        c = self ; v = c.currentVnode()

        # Expansion levels are now local to a particular tree.
        if c.expansionNode != v:
            c.expansionLevel = 1
            c.expansionNode = v

        self.expandToLevel(c.expansionLevel + 1)
    #@+node:ekr.20031218072017.2907: *7* expandNode
    def expandNode (self,event=None):

        '''Expand the presently selected node.'''

        trace = False and not g.unitTesting
        c = self ; p = c.p

        p.expand()

        if p.isCloned():
            if trace: g.trace('***redraw')
            c.redraw() # Bug fix: 2009/10/03.
        else:
            c.redraw_after_expand(p,setFocus=True)

    #@+node:ekr.20040930064232.1: *7* expandNodeAnd/OrGoToFirstChild
    def expandNodeAndGoToFirstChild (self,event=None):

        """If a node has children, expand it if needed and go to the first child."""

        c = self ; p = c.p

        if p.hasChildren():
            if p.isExpanded():
                c.selectPosition(p.firstChild())
            else:
                c.expandNode()
                # Fix bug 930726
                # expandNodeAndGoToFirstChild only expands or only goes to first child .
                c.selectPosition(p.firstChild())

        c.treeFocusHelper()

    def expandNodeOrGoToFirstChild (self,event=None):

        """Simulate the Right Arrow Key in folder of Windows Explorer."""

        c = self ; p = c.p
        if p.hasChildren():
            if not p.isExpanded():
                c.expandNode() # Calls redraw_after_expand.
            else:
                c.redraw_after_expand(p.firstChild(),setFocus=True)
    #@+node:ekr.20060928062431: *7* expandOnlyAncestorsOfNode
    def expandOnlyAncestorsOfNode (self,event=None):

        '''Contract all nodes in the outline.'''

        c = self ; level = 1

        for p in c.all_unique_positions():
            p.contract()
        for p in c.p.parents():
            p.expand()
            level += 1

        c.redraw(setFocus=True)

        c.expansionLevel = level # Reset expansion level.
    #@+node:ekr.20031218072017.2908: *7* expandPrevLevel
    def expandPrevLevel (self,event=None):

        '''Decrease the expansion level of the outline and
        Expand all nodes at that level or lower.'''

        c = self ; v = c.currentVnode()

        # Expansion levels are now local to a particular tree.
        if c.expansionNode != v:
            c.expansionLevel = 1
            c.expansionNode = v

        self.expandToLevel(max(1,c.expansionLevel - 1))
    #@+node:ekr.20031218072017.2909: *6* Utilities
    #@+node:ekr.20031218072017.2910: *7* contractSubtree
    def contractSubtree (self,p):

        for p in p.subtree():
            p.contract()
    #@+node:ekr.20031218072017.2911: *7* expandSubtree
    def expandSubtree (self,v):

        c = self
        last = v.lastNode()

        while v and v != last:
            v.expand()
            v = v.threadNext()

        c.redraw()
    #@+node:ekr.20031218072017.2912: *7* expandToLevel (rewritten in 4.4)
    def expandToLevel (self,level):

        c = self
        current = c.p
        n = current.level()
        for p in current.self_and_subtree():
            if p.level() - n + 1 < level:
                p.expand()
            else:
                p.contract()
        c.expansionLevel = level
        c.expansionNode = c.p
        c.redraw()
    #@+node:ekr.20031218072017.2922: *5* Mark...
    #@+node:ekr.20090905110447.6098: *6* c.cloneMarked
    def cloneMarked(self,event=None):

        """Clone all marked nodes as children of a new node."""

        c = self ; u = c.undoer ; p1 = c.p.copy()

        # Create a new node to hold clones.
        parent = p1.insertAfter()
        parent.h = 'Clones of marked nodes'

        moved,n,p = [],0,c.rootPosition()
        while p:
            # Careful: don't clone already-cloned nodes.
            if p == parent:
                p.moveToNodeAfterTree()
            elif p.isMarked() and not p.v in moved:
                moved.append(p.v)
                # Moving the clone leaves position p unchanged.
                p.clone().moveToLastChildOf(parent)
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
    #@+node:ekr.20111005081134.15540: *6* c.deleteMarked
    def deleteMarked (self,event=None):

        """Delete all marked nodes."""

        c = self ; u = c.undoer ; p1 = c.p.copy()

        undo_data,p = [],c.rootPosition()
        while p:
            if p.isMarked():
                undo_data.append(p.copy())
                next = p.positionAfterDeletedTree()
                p.doDelete()
                p = next
            else:
                p.moveToThreadNext()

        if undo_data:
            u.afterDeleteMarkedNodes(undo_data,p1)
            if not g.unitTesting:
                g.blue('deleted %s nodes' % (len(undo_data)))
            c.setChanged(True)

        # Don't even *think* about restoring the old position.
        c.contractAllHeadlines()
        c.selectPosition(c.rootPosition())
        c.redraw()    
    #@+node:ekr.20111005081134.15539: *6* c.moveMarked & helper
    def moveMarked (self,event=None):

        '''Move all marked nodes as children of parent position.'''

        c = self ; u = c.undoer ; p1 = c.p.copy()

        # Check for marks.
        for v in c.all_unique_nodes():
            if v.isMarked():
                break
        else:
            return g.warning('no marked nodes')

        # Create a new root node to hold the moved nodes.
        parent = c.createMoveMarkedNode()
        assert not parent.isMarked()

        undo_data,p = [],c.rootPosition()
        while p:
            assert parent == c.rootPosition()
            # Careful: don't move already-moved nodes.
            if p.isMarked() and not parent.isAncestorOf(p):
                undo_data.append(p.copy())
                next = p.positionAfterDeletedTree()
                p.moveToLastChildOf(parent)
                p = next
            else:
                p.moveToThreadNext()

        if undo_data:
            u.afterMoveMarkedNodes(undo_data,p1)
            if not g.unitTesting:
                g.blue('moved %s nodes' % (len(undo_data)))
            c.setChanged(True)

        # Don't even *think* about restoring the old position.
        c.contractAllHeadlines()
        c.selectPosition(parent)
        c.redraw()    
    #@+node:ekr.20111005081134.15543: *7* createMoveMarkedNode
    def createMoveMarkedNode(self):

        c = self
        oldRoot = c.rootPosition()
        p = oldRoot.insertAfter()
        p.moveToRoot(oldRoot)
        c.setHeadString(p,'Moved marked nodes')
        return p
    #@+node:ekr.20031218072017.2923: *6* markChangedHeadlines
    def markChangedHeadlines (self,event=None):

        '''Mark all nodes that have been changed.'''

        c = self ; u = c.undoer ; undoType = 'Mark Changed'
        current = c.p

        c.endEditing()
        u.beforeChangeGroup(current,undoType)
        for p in c.all_unique_positions():
            if p.isDirty()and not p.isMarked():
                bunch = u.beforeMark(p,undoType)
                c.setMarked(p)
                c.setChanged(True)
                u.afterMark(p,undoType,bunch)
        u.afterChangeGroup(current,undoType)
        if not g.unitTesting:
            g.blue('done')

        c.redraw_after_icons_changed()
    #@+node:ekr.20031218072017.2924: *6* markChangedRoots
    def markChangedRoots (self,event=None):

        '''Mark all changed @root nodes.'''

        c = self ; u = c.undoer ; undoType = 'Mark Changed'
        current = c.p

        c.endEditing()
        u.beforeChangeGroup(current,undoType)
        for p in c.all_unique_positions():
            if p.isDirty()and not p.isMarked():
                s = p.b
                flag, i = g.is_special(s,0,"@root")
                if flag:
                    bunch = u.beforeMark(p,undoType)
                    c.setMarked(p)
                    c.setChanged(True)
                    u.afterMark(p,undoType,bunch)
        u.afterChangeGroup(current,undoType)
        if not g.unitTesting:
            g.blue('done')

        c.redraw_after_icons_changed()
    #@+node:ekr.20031218072017.2925: *6* markAllAtFileNodesDirty
    def markAllAtFileNodesDirty (self,event=None):

        '''Mark all @file nodes as changed.'''

        c = self ; p = c.rootPosition()

        c.endEditing()
        while p:
            if p.isAtFileNode() and not p.isDirty():
                p.setDirty()
                c.setChanged(True)
                p.moveToNodeAfterTree()
            else:
                p.moveToThreadNext()

        c.redraw_after_icons_changed()

    #@+node:ekr.20031218072017.2926: *6* markAtFileNodesDirty
    def markAtFileNodesDirty (self,event=None):

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

    #@+node:ekr.20031218072017.2928: *6* markHeadline
    def markHeadline (self,event=None):

        '''Toggle the mark of the selected node.'''

        c = self ; u = c.undoer ; p = c.p
        if not p: return

        c.endEditing()
        undoType = g.choose(p.isMarked(),'Unmark','Mark')
        bunch = u.beforeMark(p,undoType)
        if p.isMarked():
            c.clearMarked(p)
        else:
            c.setMarked(p)
        dirtyVnodeList = p.setDirty()
        c.setChanged(True)
        u.afterMark(p,undoType,bunch,dirtyVnodeList=dirtyVnodeList)

        c.redraw_after_icons_changed()
    #@+node:ekr.20031218072017.2929: *6* markSubheads
    def markSubheads (self,event=None):

        '''Mark all children of the selected node as changed.'''

        c = self ; u = c.undoer ; undoType = 'Mark Subheads'
        current = c.p
        if not current: return

        c.endEditing()
        u.beforeChangeGroup(current,undoType)
        dirtyVnodeList = []
        for p in current.children():
            if not p.isMarked():
                bunch = u.beforeMark(p,undoType)
                c.setMarked(p)
                dirtyVnodeList2 = p.setDirty()
                dirtyVnodeList.extend(dirtyVnodeList2)
                c.setChanged(True)
                u.afterMark(p,undoType,bunch)
        u.afterChangeGroup(current,undoType,dirtyVnodeList=dirtyVnodeList)

        c.redraw_after_icons_changed()
    #@+node:ekr.20031218072017.2930: *6* unmarkAll
    def unmarkAll (self,event=None):

        '''Unmark all nodes in the entire outline.'''

        c = self ; u = c.undoer ; undoType = 'Unmark All'
        current = c.p
        if not current: return

        c.endEditing()
        u.beforeChangeGroup(current,undoType)
        changed = False
        for p in c.all_unique_positions():
            if p.isMarked():
                bunch = u.beforeMark(p,undoType)
                # c.clearMarked(p) # Very slow: calls a hook.
                p.v.clearMarked()
                p.v.setDirty()
                u.afterMark(p,undoType,bunch)
                changed = True
        dirtyVnodeList = [p.v for p in c.all_unique_positions() if p.v.isDirty()]
        if changed:
            g.doHook("clear-all-marks",c=c,p=p,v=p)
            c.setChanged(True)
        u.afterChangeGroup(current,undoType,dirtyVnodeList=dirtyVnodeList)

        c.redraw_after_icons_changed()
    #@+node:ekr.20031218072017.1766: *5* Move... (Commands)
    #@+node:ekr.20070420092425: *6* cantMoveMessage
    def cantMoveMessage (self):

        c = self ; h = c.rootPosition().h
        kind = g.choose(h.startswith('@chapter'),'chapter','hoist')
        g.warning("can't move node out of",kind)
    #@+node:ekr.20031218072017.1767: *6* demote
    def demote (self,event=None):

        '''Make all following siblings children of the selected node.'''

        c = self ; u = c.undoer
        p = c.p
        if not p or not p.hasNext():
            c.treeFocusHelper()
            return

        # Make sure all the moves will be valid.
        next = p.next()
        while next:
            if not c.checkMoveWithParentWithWarning(next,p,True):
                c.treeFocusHelper()
                return
            next.moveToNext()

        c.endEditing()
        parent_v = p._parentVnode()
        n = p.childIndex()
        followingSibs = parent_v.children[n+1:]
        # g.trace('sibs2\n',g.listToString(followingSibs2))

        # Remove the moved nodes from the parent's children.
        parent_v.children = parent_v.children[:n+1]
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
        u.afterDemote(p,followingSibs,dirtyVnodeList)
        c.redraw(p,setFocus=True)
        c.updateSyntaxColorer(p) # Moving can change syntax coloring.
    #@+node:ekr.20031218072017.1768: *6* moveOutlineDown
    #@+at
    # Moving down is more tricky than moving up; we can't move p to be a child of
    # itself. An important optimization: we don't have to call
    # checkMoveWithParentWithWarning() if the parent of the moved node remains the
    # same.
    #@@c

    def moveOutlineDown (self,event=None):

        '''Move the selected node down.'''

        c = self ; u = c.undoer ; p = c.p
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
            u.afterMoveNode(p,'Move Down',undoData,dirtyVnodeList)
        c.redraw(p,setFocus=True)
        c.updateSyntaxColorer(p) # Moving can change syntax coloring.
    #@+node:ekr.20031218072017.1770: *6* moveOutlineLeft
    def moveOutlineLeft (self,event=None):

        '''Move the selected node left if possible.'''

        c = self ; u = c.undoer ; p = c.p
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
        u.afterMoveNode(p,'Move Left',undoData,dirtyVnodeList)

        # Patch by nh2: 0004-Add-bool-collapse_nodes_after_move-option.patch
        if c.collapse_nodes_after_move and c.sparse_move: # New in Leo 4.4.2
            parent.contract()
        c.redraw_now(p,setFocus=True)
        c.recolor_now() # Moving can change syntax coloring.
    #@+node:ekr.20031218072017.1771: *6* moveOutlineRight
    def moveOutlineRight (self,event=None):

        '''Move the selected node right if possible.'''

        c = self ; u = c.undoer ; p = c.p
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
        # Moving an outline right can never bring it outside the range of @ignore.
        dirtyVnodeList2 = p.setAllAncestorAtFileNodesDirty()
        dirtyVnodeList.extend(dirtyVnodeList2)
        c.setChanged(True)
        u.afterMoveNode(p,'Move Right',undoData,dirtyVnodeList)
        # g.trace(p)
        c.redraw_now(p,setFocus=True)
        c.recolor_now()
    #@+node:ekr.20031218072017.1772: *6* moveOutlineUp
    def moveOutlineUp (self,event=None):

        '''Move the selected node up if possible.'''

        trace = False and not g.unitTesting
        c = self ; u = c.undoer ; p = c.p
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
            g.trace("visBack",back)
            g.trace("visBack2",back2)
            g.trace("back2.hasChildren",back2 and back2.hasChildren())
            g.trace("back2.isExpanded",back2 and back2.isExpanded())

        parent = p.parent()

        if not back2:
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
            u.afterMoveNode(p,'Move Right',undoData,dirtyVnodeList)
        c.redraw(p,setFocus=True)
        c.updateSyntaxColorer(p) # Moving can change syntax coloring.
    #@+node:ekr.20031218072017.1774: *6* c.promote
    def promote (self,event=None):

        '''Make all children of the selected nodes siblings of the selected node.'''

        c = self ; u = c.undoer ; p = c.p
        if not p or not p.hasChildren():
            c.treeFocusHelper()
            return
        isAtIgnoreNode = p.isAtIgnoreNode()
        inAtIgnoreRange = p.inAtIgnoreRange()
        c.endEditing()
        parent_v = p._parentVnode()
        children = p.v.children
        # Add the children to parent_v's children.
        n = p.childIndex()+1
        z = parent_v.children[:]
        parent_v.children = z[:n]
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
        if not inAtIgnoreRange and isAtIgnoreNode:
            # The promoted nodes have just become newly unignored.
            dirtyVnodeList = p.setDirty() # Mark descendent @thin nodes dirty.
        else: # No need to mark descendents dirty.
            dirtyVnodeList = p.setAllAncestorAtFileNodesDirty()
        u.afterPromote(p,children,dirtyVnodeList)
        c.redraw(p,setFocus=True)
        c.updateSyntaxColorer(p) # Moving can change syntax coloring.
    #@+node:ekr.20071213185710: *6* c.toggleSparseMove
    def toggleSparseMove (self,event=None):

        '''Toggle whether moves collapse the outline.'''

        c = self

        c.sparse_move = not c.sparse_move

        if not g.unitTesting:
            g.blue('sparse-move: %s' % c.sparse_move)
    #@+node:ekr.20031218072017.2913: *5* Goto (Commands)
    #@+node:ekr.20031218072017.1628: *6* goNextVisitedNode
    def goNextVisitedNode (self,event=None):

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

    #@+node:ekr.20031218072017.1627: *6* goPrevVisitedNode
    def goPrevVisitedNode (self,event=None):

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
    #@+node:ekr.20031218072017.2914: *6* goToFirstNode
    def goToFirstNode (self,event=None):

        '''Select the first node of the entire outline.'''

        c = self
        p = c.rootPosition()
        c.selectPosition(p)
        c.expandOnlyAncestorsOfNode()
        c.redraw()
        c.treeSelectHelper(p)

    #@+node:ekr.20051012092453: *6* goToFirstSibling
    def goToFirstSibling (self,event=None):

        '''Select the first sibling of the selected node.'''

        c = self ; p = c.p

        if p.hasBack():
            while p.hasBack():
                p.moveToBack()

        c.treeSelectHelper(p)
    #@+node:ekr.20070615070925: *6* goToFirstVisibleNode
    def goToFirstVisibleNode (self,event=None):

        '''Select the first visible node of the selected chapter or hoist.'''

        c = self

        p = c.firstVisible()
        if p:
            c.selectPosition(p)
            c.expandOnlyAncestorsOfNode()
            c.redraw_after_select(p)
            c.treeSelectHelper(p)
    #@+node:ekr.20031218072017.2915: *6* goToLastNode
    def goToLastNode (self,event=None):

        '''Select the last node in the entire tree.'''

        c = self
        p = c.rootPosition()

        while p and p.hasThreadNext():
            p.moveToThreadNext()

        c.selectPosition(p)
        c.treeSelectHelper(p)
        c.expandOnlyAncestorsOfNode()
        c.redraw()
    #@+node:ekr.20051012092847.1: *6* goToLastSibling
    def goToLastSibling (self,event=None):

        '''Select the last sibling of the selected node.'''

        c = self ; p = c.p

        if p.hasNext():
            while p.hasNext():
                p.moveToNext()

        c.treeSelectHelper(p)
    #@+node:ekr.20050711153537: *6* c.goToLastVisibleNode
    def goToLastVisibleNode (self,event=None):

        '''Select the last visible node of selected chapter or hoist.'''

        c = self

        p = c.lastVisible()
        if p:
            c.selectPosition(p)
            c.expandOnlyAncestorsOfNode()
            c.redraw_after_select(p)
            c.treeSelectHelper(p)
    #@+node:ekr.20031218072017.2916: *6* goToNextClone
    def goToNextClone (self,event=None):

        '''Select the next node that is a clone of the selected node.'''

        c = self ; cc = c.chapterController ; p = c.p
        if not p: return
        if not p.isCloned():
            g.warning('not a clone:',p.h)
            return

        v = p.v
        p.moveToThreadNext()
        wrapped = False
        while 1:
            # g.trace(p.v,p.h)
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
                cc.selectChapterByName('main')
            c.selectPosition(p)
            c.redraw_after_select(p)
        else:
            g.blue('done')

        # if cc:
            # name = cc.findChapterNameForPosition(p)
            # cc.selectChapterByName(name)
    #@+node:ekr.20071213123942: *6* findNextClone
    def findNextClone (self,event=None):

        '''Select the next cloned node.'''

        c = self ; p = c.p ; cc = c.chapterController
        if not p: return

        if p.isCloned():
            p.moveToThreadNext()

        flag = False
        while p:
            if p.isCloned():
                flag = True ; break
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
    #@+node:ekr.20031218072017.2917: *6* goToNextDirtyHeadline
    def goToNextDirtyHeadline (self,event=None):

        '''Select the node that is marked as changed.'''

        c = self ; p = c.p
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
    #@+node:ekr.20031218072017.2918: *6* goToNextMarkedHeadline
    def goToNextMarkedHeadline (self,event=None):

        '''Select the next marked node.'''

        c = self ; p = c.p
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
    #@+node:ekr.20031218072017.2919: *6* goToNextSibling
    def goToNextSibling (self,event=None):

        '''Select the next sibling of the selected node.'''

        c = self ; p = c.p

        c.treeSelectHelper(p and p.next())
    #@+node:ekr.20031218072017.2920: *6* goToParent
    def goToParent (self,event=None):

        '''Select the parent of the selected node.'''

        c = self ; p = c.p

        # g.trace(p.parent())

        c.treeSelectHelper(p and p.parent())
    #@+node:ekr.20031218072017.2921: *6* goToPrevSibling
    def goToPrevSibling (self,event=None):

        '''Select the previous sibling of the selected node.'''

        c = self ; p = c.p

        c.treeSelectHelper(p and p.back())
    #@+node:ekr.20031218072017.2993: *6* selectThreadBack
    def selectThreadBack (self,event=None):

        '''Select the node preceding the selected node in outline order.'''

        c = self ; p = c.p
        if not p: return

        p.moveToThreadBack()

        c.treeSelectHelper(p)
    #@+node:ekr.20031218072017.2994: *6* selectThreadNext
    def selectThreadNext (self,event=None):

        '''Select the node following the selected node in outline order.'''

        c = self ; p = c.p
        if not p: return

        p.moveToThreadNext()

        c.treeSelectHelper(p)
    #@+node:ekr.20031218072017.2995: *6* selectVisBack
    # This has an up arrow for a control key.

    def selectVisBack (self,event=None):

        '''Select the visible node preceding the presently selected node.'''

        c = self ; p = c.p
        if not p: return
        if not c.canSelectVisBack():
            c.endEditing() # 2011/05/28: A special case.
            return

        p.moveToVisBack(c)

        # g.trace(p.h)
        c.treeSelectHelper(p)
    #@+node:ekr.20031218072017.2996: *6* selectVisNext
    def selectVisNext (self,event=None):

        '''Select the visible node following the presently selected node.'''

        c = self ; p = c.p
        if not p: return
        if not c.canSelectVisNext():
            c.endEditing() # 2011/05/28: A special case.
            return

        p.moveToVisNext(c)
        c.treeSelectHelper(p)
    #@+node:ekr.20070417112650: *6* utils
    #@+node:ekr.20070226121510: *7*  c.xFocusHelper
    def treeEditFocusHelper (self):
        c = self

        if c.stayInTreeAfterEdit:
            c.treeWantsFocus()
        else:
            c.bodyWantsFocus()

    def treeFocusHelper (self):
        c = self

        if c.stayInTreeAfterSelect:
            c.treeWantsFocus()
        else:
            c.bodyWantsFocus()

    def initialFocusHelper (self):
        c = self
        if c.outlineHasInitialFocus:
            c.treeWantsFocus()
        else:
            c.bodyWantsFocus()
    #@+node:ekr.20070226113916: *7*  c.treeSelectHelper
    def treeSelectHelper (self,p):

        c = self

        if not p: p = c.p

        if p:
            # Do not call expandAllAncestors here.
            c.selectPosition(p)
            c.redraw_after_select(p)

        c.treeFocusHelper()
    #@+node:ekr.20031218072017.2931: *4* Window Menu
    #@+node:ekr.20031218072017.2092: *5* openCompareWindow
    def openCompareWindow (self,event=None):

        '''Open a dialog for comparing files and directories.'''

        c = self ; frame = c.frame

        if not frame.comparePanel:
            frame.comparePanel = g.app.gui.createComparePanel(c)

        if frame.comparePanel:
            frame.comparePanel.bringToFront()
        else:
            g.warning('the',g.app.gui.guiName(),
                'gui does not support the compare window')
    #@+node:ekr.20031218072017.2932: *5* openPythonWindow
    def openPythonWindow (self,event=None):

        '''Open Python's Idle debugger in a separate process.'''

        try:
            idlelib_path = imp.find_module('idlelib')[1]
        except ImportError:
            g.es_print('idlelib not found: can not open a Python window.')
            return

        idle = g.os_path_join(idlelib_path,'idle.py')
        args = [sys.executable, idle ]

        if 1: # Use present environment.
            os.spawnv(os.P_NOWAIT, sys.executable, args)
        else: # Use a pristine environment.
            os.spawnve(os.P_NOWAIT, sys.executable, args, os.environ)
    #@+node:ekr.20031218072017.2938: *4* Help Menu
    #@+node:ekr.20031218072017.2939: *5* about (version number & date)
    def about (self,event=None):

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
        g.app.gui.runAboutLeoDialog(c,version,theCopyright,url,email)
    #@+node:ekr.20131028155339.17096: *5* openCheatSheet
    def openCheatSheet(self,event=None,redraw=True):
        '''Open leo/doc/cheatSheet.leo'''
        c = self
        fn = g.os_path_finalize_join(g.app.loadDir,'..','doc','CheatSheet.leo')
        if g.os_path_exists(fn):
            c2 = g.openWithFileName(fn,old_c=c)
            if redraw:
                p = g.findNodeAnywhere(c2,"Leo's cheat sheet")
                if p:
                    c2.selectPosition(p,enableRedrawFlag=False)
                    p.expand()
                c2.redraw()
            return c2
        else:
            g.es('file not found: %s' % fn)
            return None
    #@+node:ekr.20031218072017.2943: *5* openLeoSettings and openMyLeoSettings
    def openLeoSettings (self,event=None):
        '''Open leoSettings.leo in a new Leo window.'''
        self.openSettingsHelper('leoSettings.leo')

    def openMyLeoSettings (self,event=None):
        '''Open myLeoSettings.leo in a new Leo window.'''
        self.openSettingsHelper('myLeoSettings.leo')

    def openSettingsHelper(self,name):
        c = self
        homeLeoDir = g.app.homeLeoDir
        loadDir = g.app.loadDir
        configDir = g.app.globalConfigDir

        # Look in configDir first.
        fileName = g.os_path_join(configDir,name)
        ok = g.os_path_exists(fileName)
        if ok:
            c2 = g.openWithFileName(fileName,old_c=c)
            if c2: return

        # Look in homeLeoDir second.
        if configDir == loadDir:
            g.es('',name,"not found in",configDir)
        else:
            fileName = g.os_path_join(homeLeoDir,name)
            ok = g.os_path_exists(fileName)
            if ok:
                c2 = g.openWithFileName(fileName,old_c=c)
                ok = bool(c2)
            if not ok:
                g.es('',name,"not found in",configDir,"\nor",homeLeoDir)
    #@+node:ekr.20061018094539: *5* openLeoScripts
    def openLeoScripts (self,event=None):

        '''Open scripts.leo.'''

        c = self
        fileName = g.os_path_join(g.app.loadDir,'..','scripts','scripts.leo')

        # Bug fix: 2012/04/09: only call g.openWithFileName if the file exists.
        if g.os_path_exists(fileName):
            c2 = g.openWithFileName(fileName,old_c=c)
            if c2: return

        g.es('not found:',fileName)
    #@+node:ekr.20031218072017.2940: *5* leoDocumentation
    def leoDocumentation (self,event=None):

        '''Open LeoDocs.leo in a new Leo window.'''

        c = self ; name = "LeoDocs.leo"

        fileName = g.os_path_join(g.app.loadDir,"..","doc",name)
        # Bug fix: 2012/04/09: only call g.openWithFileName if the file exists.
        if g.os_path_exists(fileName):
            c2 = g.openWithFileName(fileName,old_c=c)
            if c2: return

        g.es("not found:",name)
    #@+node:ekr.20031218072017.2941: *5* leoHome
    def leoHome (self,event=None):

        '''Open Leo's Home page in a web browser.'''

        import webbrowser

        url = "http://leoeditor.com/"
        try:
            webbrowser.open_new(url)
        except:
            g.es("not found:",url)
    #@+node:ekr.20050130152008: *5* openLeoPlugins
    def openLeoPlugins (self,event=None):

        '''Open leoPlugins.leo in a new Leo window.'''

        names =  ('leoPlugins.leo','leoPluginsRef.leo')

        c = self ; name = "leoPlugins.leo"

        for name in names:
            fileName = g.os_path_join(g.app.loadDir,"..","plugins",name)
            # Bug fix: 2012/04/09: only call g.openWithFileName if the file exists.
            if g.os_path_exists(fileName):
                c2 = g.openWithFileName(fileName,old_c=c)
                if c2: return

        g.es('not found:', ', '.join(names))
    #@+node:ekr.20090628075121.5994: *5* leoQuickStart
    def leoQuickStart (self,event=None):

        '''Open quickstart.leo in a new Leo window.'''

        c = self ; name = "quickstart.leo"

        fileName = g.os_path_join(g.app.loadDir,"..","doc",name)
        # Bug fix: 2012/04/09: only call g.openWithFileName if the file exists.
        if g.os_path_exists(fileName):
            c2 = g.openWithFileName(fileName,old_c=c)
            if c2: return

        g.es("not found:",name)
    #@+node:ekr.20031218072017.2942: *5* leoTutorial (version number)
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
    #@+node:ekr.20060613082924: *5* leoUsersGuide
    def leoUsersGuide (self,event=None):

        '''Open Leo's users guide in a web browser.'''

        url = 'http://leoeditor.com/leo_toc.html'
        g.handleUrl(url)
    #@+node:ekr.20110402084740.14490: *4* c.goToNext/PrevHistory
    def goToNextHistory (self,event=None):
        '''Go to the next node in the history list.'''
        c = self
        c.nodeHistory.goNext()

    def goToPrevHistory (self,event=None):
        '''Go to the previous node in the history list.'''
        c = self
        c.nodeHistory.goPrev()
    #@+node:ekr.20131016084446.16724: *4* c.setComplexCommand
    def setComplexCommand(self,commandName):
        '''Make commandName the command to be executed by repeat-complex-command.'''
        c = self
        c.k.mb_history.insert(0,commandName)
    #@+node:ekr.20031218072017.2945: *3* Dragging (commands)
    #@+node:ekr.20031218072017.2353: *4* c.dragAfter
    def dragAfter(self,p,after):

        c = self ; u = self.undoer ; undoType = 'Drag'
        current = c.p
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
        c.redraw(p)
        c.updateSyntaxColorer(p) # Dragging can change syntax coloring.
    #@+node:ekr.20031218072017.2947: *4* c.dragToNthChildOf
    def dragToNthChildOf(self,p,parent,n):

        c = self ; u = c.undoer ; undoType = 'Drag'
        current = c.p
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
        c.redraw(p)
        c.updateSyntaxColorer(p) # Dragging can change syntax coloring.
    #@+node:ekr.20031218072017.2946: *4* c.dragCloneToNthChildOf
    def dragCloneToNthChildOf (self,p,parent,n):

        c = self ; u = c.undoer ; undoType = 'Clone Drag'
        current = c.p
        inAtIgnoreRange = p.inAtIgnoreRange()

        # g.trace("p,parent,n:",p.h,parent.h,n)
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
        c.redraw(clone)
        c.updateSyntaxColorer(clone) # Dragging can change syntax coloring.
    #@+node:ekr.20031218072017.2948: *4* c.dragCloneAfter
    def dragCloneAfter (self,p,after):

        c = self ; u = c.undoer ; undoType = 'Clone Drag'
        current = c.p

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

        c.redraw(p)
        c.updateSyntaxColorer(clone) # Dragging can change syntax coloring.
    #@+node:ekr.20031218072017.2949: *3* Drawing Utilities (commands)
    #@+node:ekr.20080610085158.2: *4* c.add_command
    def add_command (self,menu,**keys):

        c = self ; command = keys.get('command')

        if command:

            # Command is always either:
            # one of two callbacks defined in createMenuEntries or
            # recentFilesCallback, defined in createRecentFilesMenuItems.

            def add_commandCallback(c=c,command=command):
                # g.trace(command)
                val = command()
                # Careful: func may destroy c.
                if c.exists: c.outerUpdate()
                return val

            keys ['command'] = add_commandCallback

            menu.add_command(**keys)

        else:
            g.trace('can not happen: no "command" arg')
    #@+node:ekr.20080514131122.7: *4* c.begin/endUpdate

    def beginUpdate(self):

        '''Deprecated: does nothing.'''

        g.trace('***** c.beginUpdate is deprecated',g.callers())
        if g.app.unitTesting: assert(False)

    def endUpdate(self,flag=True):

        '''Request a redraw of the screen if flag is True.'''

        g.trace('***** c.endUpdate is deprecated',g.callers())
        if g.app.unitTesting: assert(False)

        c = self
        if flag:
            c.requestRedrawFlag = True
            # g.trace('flag is True',c.shortFileName(),g.callers())

    BeginUpdate = beginUpdate # Compatibility with old scripts
    EndUpdate = endUpdate # Compatibility with old scripts
    #@+node:ekr.20080514131122.8: *4* c.bringToFront
    def bringToFront(self,c2=None,set_focus=True):

        c = self
        c2 = c2 or c
        c.requestBringToFront = c2
        c.requestedIconify = 'deiconify'
        c.requestedFocusWidget = c2.frame.body.bodyCtrl
        g.app.gui.ensure_commander_visible(c2)

    BringToFront = bringToFront # Compatibility with old scripts
    #@+node:ekr.20040803072955.143: *4* c.expandAllAncestors
    def expandAllAncestors (self,p):

        '''Expand all ancestors without redrawing.

        Return a flag telling whether a redraw is needed.'''

        # c = self
        trace = False and not g.unitTesting
        redraw_flag = False
        for p in p.parents():
            if not p.isExpanded():
                p.expand()
                redraw_flag = True

        if trace: g.trace(redraw_flag,repr(p and p.h),g.callers())
        return redraw_flag
    #@+node:ekr.20080514131122.9: *4* c.get/request/set_focus
    def get_focus (self):

        c = self
        return g.app.gui and g.app.gui.get_focus(c)

    def get_requested_focus (self):

        c = self
        return c.requestedFocusWidget

    def request_focus(self,w):

        trace = False and not g.unitTesting
        c = self
        if trace: g.trace(g.app.gui.widget_name(w),w,g.callers())
        if w: c.requestedFocusWidget = w

    def set_focus (self,w,force=False):

        trace = False and not g.unitTesting
        c = self
        if w and g.app.gui:
            if trace: print('c.set_focus:',g.app.gui.widget_name(w),w,g.callers())
                # w,c.shortFileName())
            g.app.gui.set_focus(c,w)
        else:
            if trace: print('c.set_focus: no w')

        c.requestedFocusWidget = None
    #@+node:ekr.20080514131122.10: *4* c.invalidateFocus
    def invalidateFocus (self):

        '''Indicate that the focus is in an invalid location, or is unknown.'''

        # c = self
        # c.requestedFocusWidget = None
        pass
    #@+node:ekr.20080514131122.12: *4* c.recolor & requestRecolor
    def requestRecolor (self):

        c = self
        # g.trace(g.callers(4))
        c.requestRecolorFlag = True

    recolor = requestRecolor
    #@+node:ekr.20080514131122.14: *4* c.redrawing...
    #@+node:ekr.20090110073010.1: *5* c.redraw
    def redraw (self,p=None,setFocus=False):
        '''Redraw the screen immediately.'''

        trace = False and not g.unitTesting
        c = self
        if not p: p = c.p or c.rootPosition()
        c.expandAllAncestors(p)
        if p:
            # Fix bug https://bugs.launchpad.net/leo-editor/+bug/1183855
            # This looks redundant, but it is probably the only safe fix.
            c.frame.tree.select(p)
        # 2012/03/10: tree.redraw will change the position if p is a hoisted @chapter node.
        p2 = c.frame.tree.redraw(p)
        # Be careful.  nullTree.redraw returns None.
        c.selectPosition(p2 or p)
        if trace: g.trace('setFocus',setFocus,p2 and p2.h or p and p.h)
        if setFocus: c.treeFocusHelper()

    # Compatibility with old scripts
    force_redraw = redraw
    redraw_now = redraw
    #@+node:ekr.20090110131802.2: *5* c.redraw_after_contract
    def redraw_after_contract (self,p=None,setFocus=False):

        c = self

        c.endEditing()

        if p:
            c.setCurrentPosition(p)
        else:
            p = c.currentPosition()

        if p.isCloned():
            c.redraw(p=p,setFocus=setFocus)
        else:
            c.frame.tree.redraw_after_contract(p)
            if setFocus: c.treeFocusHelper()
    #@+node:ekr.20090112065525.1: *5* c.redraw_after_expand
    def redraw_after_expand (self,p=None,setFocus=False):

        c = self

        c.endEditing()

        if p:
            c.setCurrentPosition(p)
        else:
            p = c.currentPosition()

        if p.isCloned():
            c.redraw(p=p,setFocus=setFocus)
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
    def redraw_after_select(self,p):

        '''Redraw the screen after node p has been selected.'''

        trace = False and not g.unitTesting
        if trace: g.trace('(Commands)',p and p.h or '<No p>', g.callers(4))

        c = self

        flag = c.expandAllAncestors(p)
        if flag:
            c.frame.tree.redraw_after_select(p)
    #@+node:ekr.20080514131122.13: *4* c.recolor_now
    def recolor_now(self,p=None,incremental=False,interruptable=True):

        c = self
        if p is None:
            p = c.p

        # g.trace('incremental',incremental,p and p.h,g.callers())

        c.frame.body.colorizer.colorize(p,
            incremental=incremental,interruptable=interruptable)
    #@+node:ekr.20080514131122.16: *4* c.traceFocus
    def traceFocus (self,w):

        c = self

        if False or (not g.app.unitTesting and c.config.getBool('trace_focus')):
            ### import pdb ; pdb.set_trace() # Drop into pdb.
            c.trace_focus_count += 1
            g.pr('%4d' % (c.trace_focus_count),c.widget_name(w),g.callers(8))
    #@+node:ekr.20080514131122.17: *4* c.widget_name
    def widget_name (self,widget):

        # c = self
        return g.app.gui and g.app.gui.widget_name(widget) or ''
    #@+node:ekr.20080514131122.18: *4* c.xWantsFocus

    def bodyWantsFocus(self):
        c = self ; body = c.frame.body
        c.request_focus(body and body.bodyCtrl)

    def logWantsFocus(self):
        c = self ; log = c.frame.log
        c.request_focus(log and log.logCtrl)

    def minibufferWantsFocus(self):
        c = self
        c.request_focus(c.miniBufferWidget)

    def treeWantsFocus(self):
        c = self ; tree = c.frame.tree
        c.request_focus(tree and tree.canvas)

    def widgetWantsFocus(self,w):
        c = self ; c.request_focus(w)
    #@+node:ekr.20080514131122.19: *4* c.xWantsFocusNow
    # widgetWantsFocusNow does an automatic update.
    def widgetWantsFocusNow(self,w):
        c = self
        c.request_focus(w)
        c.outerUpdate()

    # New in 4.9: all FocusNow methods now *do* call c.outerUpdate().
    def bodyWantsFocusNow(self):
        c = self ; body = c.frame.body
        c.widgetWantsFocusNow(body and body.bodyCtrl)

    def logWantsFocusNow(self):
        c = self ; log = c.frame.log
        c.widgetWantsFocusNow(log and log.logCtrl)

    def treeWantsFocusNow(self):
        c = self ; tree = c.frame.tree
        c.widgetWantsFocusNow(tree and tree.canvas)
    #@+node:ekr.20031218072017.2955: *3* Enabling Menu Items
    #@+node:ekr.20040323172420: *4* Slow routines: no longer used
    #@+node:ekr.20031218072017.2966: *5* canGoToNextDirtyHeadline (slow)
    def canGoToNextDirtyHeadline (self):

        c = self ; current = c.p

        for p in c.all_unique_positions():
            if p != current and p.isDirty():
                return True

        return False
    #@+node:ekr.20031218072017.2967: *5* canGoToNextMarkedHeadline (slow)
    def canGoToNextMarkedHeadline (self):

        c = self ; current = c.p

        for p in c.all_unique_positions():
            if p != current and p.isMarked():
                return True

        return False
    #@+node:ekr.20031218072017.2968: *5* canMarkChangedHeadline (slow)
    def canMarkChangedHeadlines (self):

        c = self

        for p in c.all_unique_positions():
            if p.isDirty():
                return True

        return False
    #@+node:ekr.20031218072017.2969: *5* canMarkChangedRoots (slow)
    def canMarkChangedRoots (self):

        c = self

        for p in c.all_unique_positions():
            if p.isDirty and p.isAnyAtFileNode():
                return True

        return False
    #@+node:ekr.20040131170659: *4* canClone (new for hoist)
    def canClone (self):

        c = self

        if c.hoistStack:
            current = c.p
            bunch = c.hoistStack[-1]
            return current != bunch.p
        else:
            return True
    #@+node:ekr.20031218072017.2956: *4* canContractAllHeadlines
    def canContractAllHeadlines (self):

        c = self

        for p in c.all_unique_positions():
            if p.isExpanded():
                return True

        return False
    #@+node:ekr.20031218072017.2957: *4* canContractAllSubheads
    def canContractAllSubheads (self):

        c = self ; current = c.p

        for p in current.subtree():
            if p != current and p.isExpanded():
                return True

        return False
    #@+node:ekr.20031218072017.2958: *4* canContractParent
    def canContractParent (self):

        c = self
        return c.p.parent()
    #@+node:ekr.20031218072017.2959: *4* canContractSubheads
    def canContractSubheads (self):

        c = self ; current = c.p

        for child in current.children():
            if child.isExpanded():
                return True

        return False
    #@+node:ekr.20031218072017.2960: *4* canCutOutline & canDeleteHeadline
    def canDeleteHeadline (self):

        c = self ; p = c.p

        if c.hoistStack:
            bunch = c.hoistStack[0]
            if p == bunch.p: return False

        return p.hasParent() or p.hasThreadBack() or p.hasNext()

    canCutOutline = canDeleteHeadline
    #@+node:ekr.20031218072017.2961: *4* canDemote
    def canDemote (self):

        c = self
        return c.p.hasNext()
    #@+node:ekr.20031218072017.2962: *4* canExpandAllHeadlines
    def canExpandAllHeadlines (self):

        c = self

        for p in c.all_unique_positions():
            if not p.isExpanded():
                return True

        return False
    #@+node:ekr.20031218072017.2963: *4* canExpandAllSubheads
    def canExpandAllSubheads (self):

        c = self

        for p in c.p.subtree():
            if not p.isExpanded():
                return True

        return False
    #@+node:ekr.20031218072017.2964: *4* canExpandSubheads
    def canExpandSubheads (self):

        c = self ; current = c.p

        for p in current.children():
            if p != current and not p.isExpanded():
                return True

        return False
    #@+node:ekr.20031218072017.2287: *4* canExtract, canExtractSection & canExtractSectionNames
    def canExtract (self):

        c = self ; body = c.frame.body
        return body and body.hasSelection()

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
    #@+node:ekr.20031218072017.2965: *4* canFindMatchingBracket
    def canFindMatchingBracket (self):

        c = self ; brackets = "()[]{}"
        body = c.frame.body
        s = body.getAllText()
        ins = body.getInsertPoint()
        c1 = 0 <= ins   < len(s) and s[ins] or ''
        c2 = 0 <= ins-1 < len(s) and s[ins-1] or ''

        val = (c1 and c1 in brackets) or (c2 and c2 in brackets)
        return bool(val)
    #@+node:ekr.20040303165342: *4* canHoist & canDehoist
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
    #@+node:ekr.20070608165544: *4* hoistLevel
    def hoistLevel (self):

        c = self
        cc = c.chapterController
        n = len(c.hoistStack)
        if n > 0 and cc and cc.inChapter():
            n -= 1
        return n
    #@+node:ekr.20031218072017.2970: *4* canMoveOutlineDown
    def canMoveOutlineDown (self):

        c = self ; current = c.p

        return current and current.visNext(c)
    #@+node:ekr.20031218072017.2971: *4* canMoveOutlineLeft
    def canMoveOutlineLeft (self):

        c = self ; p = c.p

        if c.hoistStack:
            bunch = c.hoistStack[-1]
            if p and p.hasParent():
                p.moveToParent()
                return p != bunch.p and bunch.p.isAncestorOf(p)
            else:
                return False
        else:
            return p and p.hasParent()
    #@+node:ekr.20031218072017.2972: *4* canMoveOutlineRight
    def canMoveOutlineRight (self):

        c = self ; p = c.p

        if c.hoistStack:
            bunch = c.hoistStack[-1]
            return p and p.hasBack() and p != bunch.p
        else:
            return p and p.hasBack()
    #@+node:ekr.20031218072017.2973: *4* canMoveOutlineUp
    def canMoveOutlineUp (self):

        c = self ; current = c.p

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
    #@+node:ekr.20031218072017.2974: *4* canPasteOutline
    def canPasteOutline (self,s=None):

        trace = False and not g.unitTesting
        c = self

        if not s:
            s = g.app.gui.getTextFromClipboard()

        if s:
            if g.match(s,0,g.app.prolog_prefix_string):
                if trace: g.trace('matches xml prolog')
                return True
            else:
                val = c.importCommands.stringIsValidMoreFile(s)
                if trace: g.trace('More file?',val)
                return val

        if trace: g.trace('no clipboard text')
        return False
    #@+node:ekr.20031218072017.2975: *4* canPromote
    def canPromote (self):

        c = self ; v = c.currentVnode()
        return v and v.hasChildren()
    #@+node:ekr.20031218072017.2977: *4* canSelect....
    def canSelectThreadBack (self):
        c = self ; p = c.p
        return p.hasThreadBack()

    def canSelectThreadNext (self):
        c = self ; p = c.p
        return p.hasThreadNext()

    def canSelectVisBack (self):
        c = self ; p = c.p
        return p.visBack(c)

    def canSelectVisNext (self):
        c = self ; p = c.p
        return p.visNext(c)
    #@+node:ekr.20031218072017.2978: *4* canShiftBodyLeft/Right
    def canShiftBodyLeft (self):

        c = self ; body = c.frame.body
        return body and body.getAllText()

    canShiftBodyRight = canShiftBodyLeft
    #@+node:ekr.20031218072017.2979: *4* canSortChildren, canSortSiblings
    def canSortChildren (self):

        c = self ; p = c.p
        return p and p.hasChildren()

    def canSortSiblings (self):

        c = self ; p = c.p
        return p and (p.hasNext() or p.hasBack())
    #@+node:ekr.20031218072017.2980: *4* canUndo & canRedo
    def canUndo (self):

        c = self
        return c.undoer.canUndo()

    def canRedo (self):

        c = self
        return c.undoer.canRedo()
    #@+node:ekr.20031218072017.2981: *4* canUnmarkAll
    def canUnmarkAll (self):

        c = self

        for p in c.all_unique_positions():
            if p.isMarked():
                return True

        return False
    #@+node:ekr.20111217154130.10286: *3* Error dialogs (commands)
    #@+node:ekr.20111217154130.10284: *4* c.init_error_dialogs
    def init_error_dialogs(self):

        c = self
        c.import_error_nodes = []
        c.ignored_at_file_nodes = []

        if g.unitTesting:
            d = g.app.unitTestDict
            tag = 'init_error_dialogs'
            d[tag] = 1 + d.get(tag,0)
    #@+node:ekr.20111217154130.10285: *4* c.raise_error_dialogs
    def raise_error_dialogs(self,kind='read'):

        c = self

        if g.unitTesting:
            d = g.app.unitTestDict
            tag = 'raise_error_dialogs'
            d[tag] = 1 + d.get(tag,0)
            # This trace catches all too-many-calls failures.
            # g.trace(g.callers())
        else:
            # 2011/12/17: Issue one or two dialogs.
            if c.import_error_nodes or c.ignored_at_file_nodes:
                g.app.gui.dismiss_splash_screen()
                # g.trace(g.callers())

            if c.import_error_nodes:
                files = '\n'.join(sorted(c.import_error_nodes))
                g.app.gui.runAskOkDialog(c,
                    title='Import errors',
                    message='The following were not imported properly.  @ignore was inserted:\n%s' % (files))

            if c.ignored_at_file_nodes:
                files = '\n'.join(sorted(c.ignored_at_file_nodes))
                kind = g.choose(kind.startswith('read'),'read','written')
                g.app.gui.runAskOkDialog(c,
                    title='Not read',
                    message='The following were not %s because they contain @ignore:\n%s' % (kind,files))

        c.init_error_dialogs()
    #@+node:ekr.20031218072017.2982: *3* Getters & Setters
    #@+node:ekr.20060906211747: *4* Getters
    #@+node:ekr.20040803140033: *5* c.currentPosition (changed)
    def currentPosition (self):

        """Return the presently selected position."""

        c = self

        if hasattr(c,'_currentPosition') and getattr(c,'_currentPosition'):
            # New in Leo 4.4.2: *always* return a copy.
            return c._currentPosition.copy()
        else:
            return c.nullPosition()

    # For compatibiility with old scripts.
    currentVnode = currentPosition
    #@+node:ekr.20040306220230.1: *5* c.edit_widget
    def edit_widget (self,p):

        c = self

        return p and c.frame.tree.edit_widget(p)
    #@+node:ekr.20031218072017.2986: *5* c.fileName & relativeFileName & shortFileName
    # Compatibility with scripts

    def fileName (self):

        return self.mFileName

    def relativeFileName (self):

        return self.mRelativeFileName or self.mFileName

    def shortFileName (self):

        return g.shortFileName(self.mFileName)

    shortFilename = shortFileName
    #@+node:ekr.20070615070925.1: *5* c.firstVisible
    def firstVisible(self):

        """Move to the first visible node of the present chapter or hoist."""

        c = self ; p = c.p

        while 1:
            back = p.visBack(c)
            if back and back.isVisible(c):
                p = back
            else: break
        return p
    #@+node:ekr.20040803112200: *5* c.is...Position
    #@+node:ekr.20040803155551: *6* c.currentPositionIsRootPosition
    def currentPositionIsRootPosition (self):

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
    def currentPositionHasNext (self):

        """Return True if the current position is the root position.

        This method is called during idle time, so not generating positions
        here fixes a major leak.
        """

        c = self ; current = c._currentPosition 

        return current and current.hasNext()
    #@+node:ekr.20040803112450: *6* c.isCurrentPosition
    def isCurrentPosition (self,p):

        c = self

        if p is None or c._currentPosition is None:
            return False
        else:
            return p == c._currentPosition
    #@+node:ekr.20040803112450.1: *6* c.isRootPosition
    def isRootPosition (self,p):

        c = self
        root = c.rootPosition()

        return p and root and p == root # 2011/03/03

        # if p is None or c._rootPosition is None:
            # return False
        # else:
            # return p == c._rootPosition
    #@+node:ekr.20031218072017.2987: *5* c.isChanged
    def isChanged (self):

        return self.changed
    #@+node:ekr.20031218072017.4146: *5* c.lastVisible
    def lastVisible(self):

        """Move to the last visible node of the present chapter or hoist."""

        c = self ; p = c.p

        while 1:
            next = p.visNext(c)
            # g.trace('next',next)
            if next and next.isVisible(c):
                p = next
            else: break
        return p
    #@+node:ekr.20040311094927: *5* c.nullPosition
    def nullPosition (self):

        # c = self
        return leoNodes.position(None)
    #@+node:ekr.20040307104131.3: *5* c.positionExists
    def positionExists(self,p,root=None):

        """Return True if a position exists in c's tree"""

        trace = False and not g.unitTesting
        verbose = False
        c = self ; p = p.copy()

        def report(i,children,v,tag=''):
            if trace and verbose:
                if i < 0 or i >= len(children):
                    g.trace('bad i: %s, children: %s' % (
                        i,len(children))) # ,g.callers(12))
                elif children[i] != v:
                    g.trace('v mismatch: children[i]: %s, v: %s' % (
                        children[i] and children[i].h,v.h)) # ,g.callers(12))

        # This code must be fast.
        root1 = root
        if not root:
            root = c.rootPosition()

        while p:
            if p == root:
                return True
            if p.hasParent():
                old_v = p.v
                i = p._childIndex
                p.moveToParent()
                children = p.v.children
                # Major bug fix: 2009/1/2 and 2009/1/5
                report(i,children,old_v)
                if i < 0 or i >= len(children) or children[i] != old_v:
                    return False
            elif root1:
                # Major bug fix: 2012/03/08: Do *not* expand the search!
                return False
            else:
                # A top-level position, check from hidden root vnode.
                i = p._childIndex
                children = c.hiddenRootNode.children
                report(i,children,p.v)
                return 0 <= i < len(children) and children[i] == p.v

        if trace: g.trace('no v found')
        return False
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
            return leoNodes.position(v,childIndex=0,stack=None)
        else:
            return c.nullPosition()

    # For compatibiility with old scripts.
    rootVnode = rootPosition
    findRootPosition = rootPosition
    #@+node:ekr.20070609122713: *5* c.visLimit
    def visLimit (self):

        '''Return the topmost visible node.
        This is affected by chapters and hoists.'''

        c = self ; cc = c.chapterController

        if c.hoistStack:
            bunch = c.hoistStack[-1]
            p = bunch.p
            limitIsVisible = not cc or not p.h.startswith('@chapter')
            return p,limitIsVisible
        else:
            return None,None
    #@+node:ekr.20090107113956.1: *5* c.vnode2position
    def vnode2position (self,v):

        '''Given a vnode v, construct a valid position p such that p.v = v.
        '''

        c = self
        context = v.context # v's commander.
        assert (c == context)
        stack = []
        while v.parents:
            parent = v.parents[0]
            if v in parent.children:
                n = parent.children.index(v)
            else:
                return None
            stack.insert(0,(v,n),)
            v = parent

        # v.parents includes the hidden root node.
        if not stack:
            # a vnode not in the tree
            return c.nullPosition()
        v,n = stack.pop()
        p = leoNodes.position(v,n,stack)
        return p

    #@+node:tbrown.20091206142842.10296: *5* c.vnode2allPositions
    def vnode2allPositions (self,v):

        '''Given a vnode v, find all valid positions p such that p.v = v.

        Not really all, just all for each of v's distinct immediate parents.
        '''

        c = self
        context = v.context # v's commander.
        assert (c == context)
        positions = []
        for immediate in v.parents:
            if v in immediate.children:
                n = immediate.children.index(v)
            else:
                continue
            stack = [(v,n)]
            while immediate.parents:
                parent = immediate.parents[0]
                if immediate in parent.children:
                    n = parent.children.index(immediate)
                else:
                    break
                stack.insert(0,(immediate,n),)
                immediate = parent
            else:
                v,n = stack.pop()
                p = leoNodes.position(v,n,stack)
                positions.append(p)
        return positions
    #@+node:ekr.20060906211747.1: *4* Setters
    #@+node:ekr.20040315032503: *5* c.appendStringToBody
    def appendStringToBody (self,p,s):

        c = self
        if not s: return

        body = p.b
        assert(g.isUnicode(body))
        s = g.toUnicode(s)

        c.setBodyString(p,body + s)
    #@+node:ekr.20031218072017.2984: *5* c.clearAllMarked
    def clearAllMarked (self):

        c = self

        for p in c.all_unique_positions():
            p.v.clearMarked()
    #@+node:ekr.20031218072017.2985: *5* c.clearAllVisited
    def clearAllVisited (self):

        c = self

        for p in c.all_unique_positions():
            p.v.clearVisited()
            p.v.clearWriteBit()
    #@+node:ekr.20060906211138: *5* c.clearMarked
    def clearMarked  (self,p):

        c = self
        p.v.clearMarked()
        g.doHook("clear-mark",c=c,p=p,v=p)
    #@+node:ekr.20040305223522: *5* c.setBodyString
    def setBodyString (self,p,s):

        c = self ; v = p.v
        if not c or not v: return

        s = g.toUnicode(s)
        current = c.p
        # 1/22/05: Major change: the previous test was: 'if p == current:'
        # This worked because commands work on the presently selected node.
        # But setRecentFiles may change a _clone_ of the selected node!
        if current and p.v==current.v:
            # Revert to previous code, but force an empty selection.
            c.frame.body.setSelectionAreas(s,None,None)
            w = c.frame.body.bodyCtrl
            i = w.getInsertPoint()
            w.setSelectionRange(i,i)
            # This code destoys all tags, so we must recolor.
            c.recolor()

        # Keep the body text in the vnode up-to-date.
        if v.b != s:
            v.setBodyString(s)
            v.setSelection(0,0)
            p.setDirty()
            if not c.isChanged():
                c.setChanged(True)
            c.redraw_after_icons_changed()
    #@+node:ekr.20031218072017.2989: *5* c.setChanged
    def setChanged (self,changedFlag):

        trace = False and not g.unitTesting
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
        master = hasattr(c.frame.top,'leo_master') and c.frame.top.leo_master
        if master:
            # Call LeoTabbedTopLevel.setChanged.
            master.setChanged(c,changedFlag)
        s = c.frame.getTitle()
        if trace: g.trace(changedFlag,repr(s))
        if len(s) > 2:
            if changedFlag:
                if s [0] != '*':
                    c.frame.setTitle("* " + s)
                    if trace: g.trace('(c)',"* " + s)
            else:
                if s[0:2]=="* ":
                    c.frame.setTitle(s[2:])
                    if trace: g.trace('(c)',s[2:])
    #@+node:ekr.20040803140033.1: *5* c.setCurrentPosition
    _currentCount = 0

    def setCurrentPosition (self,p):

        """Set the presently selected position. For internal use only.

        Client code should use c.selectPosition instead."""

        trace = False and not g.unitTesting
        c = self

        if trace:
            c._currentCount += 1
            g.trace(c._currentCount,p)

        if p and not c.positionExists(p): # 2011/02/25:
            c._currentPosition = c.rootPosition()
            if trace: trace('Invalid position: %s, root: %s' % (
                repr(p and p.h),
                repr(c._currentPosition and c._currentPosition.h)),
                g.callers())

            # Don't kill unit tests for this kind of problem.
            return

        if p:
            # Important: p.equal requires c._currentPosition to be non-None.
            if c._currentPosition and p == c._currentPosition:
                pass # We have already made a copy.
            else: # Must make a copy _now_
                c._currentPosition = p.copy()
        else:
            c._currentPosition = None

    # For compatibiility with old scripts.
    setCurrentVnode = setCurrentPosition
    #@+node:ekr.20040305223225: *5* c.setHeadString
    def setHeadString (self,p,s):

        '''Set the p's headline and the corresponding tree widget to s.

        This is used in by unit tests to restore the outline.'''

        c = self

        p.initHeadString(s)
        p.setDirty()

        # Change the actual tree widget so
        # A later call to c.endEditing or c.redraw will use s.
        c.frame.tree.setHeadline(p,s)
    #@+node:ekr.20060109164136: *5* c.setLog
    def setLog (self):

        c = self

        if c.exists:
            try:
                # c.frame or c.frame.log may not exist.
                g.app.setLog(c.frame.log)
            except AttributeError:
                pass
    #@+node:ekr.20060906211138.1: *5* c.setMarked
    def setMarked (self,p):

        c = self
        p.v.setMarked()
        g.doHook("set-mark",c=c,p=p,v=p)
    #@+node:ekr.20040803140033.3: *5* c.setRootPosition (A do-nothing)
    def setRootPosition(self,unused_p=None):

        """Set c._rootPosition."""

        # 2011/03/03: No longer used.
    #@+node:ekr.20060906131836: *5* c.setRootVnode (A do-nothing)
    def setRootVnode (self, v):

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
    #@+node:ekr.20031218072017.3404: *5* c.trimTrailingLines
    def trimTrailingLines (self,p):

        """Trims trailing blank lines from a node.

        It is surprising difficult to do this during Untangle."""

        c = self
        body = p.b
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
    #@+node:ekr.20031218072017.2990: *3* Selecting & Updating (commands)
    #@+node:ekr.20031218072017.2991: *4* c.redrawAndEdit
    # Sets the focus to p and edits p.

    def redrawAndEdit(self,p,selectAll=False,selection=None,keepMinibuffer=False):

        '''Redraw the screen and start editing the headline at position p.'''

        c = self ; k = c.k
        c.redraw(p) # This *must* be done now.
        if p:
            # This should request focus.
            c.frame.tree.editLabel(p,selectAll=selectAll,selection=selection)
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
            if trace: g.trace('(c)',p.h)
            c.frame.tree.endEditLabel()
        # The following code would be wrong; c.endEditing is a utility method.
        # k = c.k
        # if k:
            # k.setDefaultInputState()
            # # Recolor the *body* text, **not** the headline.
            # k.showStateAndMode(w=c.frame.body.bodyCtrl)
    #@+node:ekr.20031218072017.2997: *4* c.selectPosition
    def selectPosition(self,p,enableRedrawFlag=True):

        """Select a new position."""

        trace = False and not g.unitTesting
        c = self ; cc = c.chapterController
        if cc:
            cc.selectChapterForPosition(p)
                # Important: selectChapterForPosition calls c.redraw
                # if the chapter changes.
            if trace: g.trace(p and p.h)
        # 2012/03/08: De-hoist as necessary to make p visible.
        redraw_flag = False
        if c.hoistStack:
            while c.hoistStack:
                bunch = c.hoistStack[len(c.hoistStack)-1]
                if c.positionExists(p,bunch.p):
                    break
                else:
                    bunch = c.hoistStack.pop()
                    redraw_flag = True
                    if trace: g.trace('unhoist',bunch.p.h)
        if trace and not c.positionExists(p):
            g.trace('** does not exist: %s' % (p and p.h))
        c.frame.tree.select(p)
        # New in Leo 4.4.2.
        c.setCurrentPosition(p)
            # Do *not* test whether the position exists!
            # We may be in the midst of an undo.
        if redraw_flag and enableRedrawFlag:
            c.redraw()

    selectVnode = selectPosition
    #@+node:ekr.20060923202156: *4* c.onCanvasKey
    def onCanvasKey (self,event):

        '''Navigate to the next headline starting with ch = event.char.
        If ch is uppercase, search all headlines; otherwise search only visible headlines.
        This is modelled on Windows explorer.'''

        # g.trace(event and event.char)

        if not event or not event.char or not event.char.isalnum():
            return
        c  = self ; p = c.p ; p1 = p.copy()

        invisible = c.config.getBool('invisible_outline_navigation')
        ch = event and event.char or ''
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
            c.selectPosition(p)
            c.redraw_after_select(p)
            c.navTime = time.clock()
            c.navPrefix = newPrefix
            # g.trace('extend',extend,'extend2',extend2,'navPrefix',c.navPrefix,'p',p.h)
        else:
            c.navTime = None
            c.navPrefix = ''
        c.treeWantsFocus()
    #@+node:ekr.20061002095711.1: *5* c.navQuickKey
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
    #@+node:ekr.20061002095711: *5* c.navHelper
    def navHelper (self,p,ch,extend):

        c = self ; h = p.h.lower()

        if extend:
            prefix = c.navPrefix + ch
            return h.startswith(prefix.lower()) and prefix

        if h.startswith(ch):
            return ch

        # New feature: search for first non-blank character after @x for common x.
        if ch != '@' and h.startswith('@'):
            for s in ('button','command','file','thin','asis','nosent',):
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
    #@+node:ville.20090525205736.12325: *4* c.getSelectedPositions
    def getSelectedPositions(self):
        """ Get list (poslist) of currently selected positions

        So far only makes sense on qt gui (which supports multiselection)
        """
        c = self
        return c.frame.tree.getSelectedPositions()
    #@+node:ekr.20031218072017.2999: *3* Syntax coloring interface
    #@+at These routines provide a convenient interface to the syntax colorer.
    #@+node:ekr.20031218072017.3000: *4* updateSyntaxColorer
    def updateSyntaxColorer(self,v):

        self.frame.body.updateSyntaxColorer(v)
    #@+node:ekr.20090103070824.12: *3* Time stamps
    #@+node:ekr.20090103070824.11: *4* c.checkFileTimeStamp
    def checkFileTimeStamp (self,fn):

        '''
        Return True if the file given by fn has not been changed
        since Leo read it or if the user agrees to overwrite it.
        '''

        trace = False and not g.unitTesting
        c = self

        # Don't assume the file still exists.
        if not g.os_path_exists(fn):
            if trace: g.trace('file no longer exists',fn)
            return True

        timeStamp = c.timeStampDict.get(fn)
        if not timeStamp:
            if trace: g.trace('no time stamp',fn)
            return True

        timeStamp2 = os.path.getmtime(fn)
        if timeStamp == timeStamp2:
            if trace: g.trace('time stamps match',fn,timeStamp)
            return True

        if g.app.unitTesting:
            return False

        if trace:
            g.trace('mismatch',timeStamp,timeStamp2)

        message = '%s\n%s\n%s' % (
            fn,
            g.tr('has been modified outside of Leo.'),
            g.tr('Overwrite this file?'))
        ok = g.app.gui.runAskYesNoCancelDialog(c,
            title = 'Overwrite modified file?',
            message = message)

        return ok == 'yes'
    #@+node:ekr.20090103070824.9: *4* c.setFileTimeStamp
    def setFileTimeStamp (self,fn):

        c = self

        timeStamp = os.path.getmtime(fn)
        c.timeStampDict[fn] = timeStamp

        # g.trace('%20s' % (timeStamp),fn)

    #@-others
#@+node:ekr.20070615131604: ** class nodeHistory
class nodeHistory:

    '''A class encapsulating knowledge of visited nodes.'''

    #@+others
    #@+node:ekr.20070615131604.1: *3*  ctor (nodeHistory)
    def __init__ (self,c):

        self.c = c
        self.beadList = []
            # a list of (position,chapter) tuples.
        self.beadPointer = -1
        self.skipBeadUpdate = False
    #@+node:ekr.20070615134813: *3* goNext (nodeHistory)
    def goNext (self):
        '''Select the next node, if possible.'''
        if self.beadPointer + 1 < len(self.beadList):
            self.beadPointer += 1
            p,chapter = self.beadList[self.beadPointer]
            # g.trace(self.beadPointer,p.h)
            self.select(p,chapter)
    #@+node:ekr.20130915111638.11288: *3* goPrev (nodeHistory)
    def goPrev (self):
        '''Select the previously visited node, if possible.'''
        if self.beadPointer > 0:
            self.beadPointer -= 1
            p,chapter = self.beadList[self.beadPointer]
            # g.trace(self.beadPointer,p.h)
            self.select(p,chapter)
    #@+node:ekr.20130915111638.11294: *3* select (nodeHistory)
    def select (self,p,chapter):
        '''
        if p.v exists anywhere, select p in chapter p if possible.
        Otherwise, remove p from self.beadList.
        '''
        trace = False and not g.unitTesting
        c,cc = self.c,self.c.chapterController
        if trace: g.trace(c.positionExists(p),p and p.h)
        if c.positionExists(p):
            self.skipBeadUpdate = True
            try:
                oldChapter = cc.getSelectedChapter()
                if oldChapter != chapter:
                    cc.selectChapterForPosition(p,chapter=chapter)
                c.selectPosition(p) # Calls cc.selectChapterForPosition
            finally:
                self.skipBeadUpdate = False
        else:
            self.beadList = [data for data in self.beadList if data[0].v != p.v]
            self.beadPointer = len(self.beadList)-1
    #@+node:ville.20090724234020.14676: *3* update (nodeHistory)
    def update (self,p):
        '''Update the beadList.  Called from c.frame.tree.selectHelper.'''
        trace = False and not g.unitTesting
        c,cc = self.c,self.c.chapterController
        if not p or self.skipBeadUpdate:
            # We have been called from self.doNext or self.doPrev.
            # Do *not* update the bead list here!
            return
        # A hack: don't add @chapter nodes.
        # These are selected during the transitions to a new chapter.
        if p.h.startswith('@chapter '):
            return
        # Leo 4.11: remove any duplicates of p.
        self.beadList = [data for data in self.beadList if data[0].v != p.v]
        data = p.copy(),cc.getSelectedChapter()
        self.beadList.append(data)
        # Leo 4.11: always set beadPointer to the end.
        # This works because self.doNext and self.doPrev do not change the beadList.
        self.beadPointer = len(self.beadList)-1
        if trace: g.trace(len(self.beadList),self.beadPointer,p and p.h,g.callers())
    #@-others
#@-others
#@-leo

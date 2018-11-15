# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20181103094900.1: * @file leoflexx.py
#@@first
#@@language python
#@@tabwidth -4
'''
A Stand-alone prototype for Leo using flexx.
'''
# pylint: disable=logging-not-lazy
#@+<< leoflexx imports >>
#@+node:ekr.20181113041314.1: ** << leoflexx imports >>
# import leo.core.leoGlobals as g
import leo.core.leoBridge as leoBridge
import leo.core.leoGui as leoGui
import leo.core.leoNodes as leoNodes
from flexx import flx
import re
import time
assert re and time
    # Suppress pyflakes complaints
#@-<< leoflexx imports >>
#@+<< ace assets >>
#@+node:ekr.20181111074958.1: ** << ace assets >>
# Assets for ace, embedded in the LeoFlexxBody and LeoFlexxLog classes.
base_url = 'https://cdnjs.cloudflare.com/ajax/libs/ace/1.2.6/'
flx.assets.associate_asset(__name__, base_url + 'ace.js')
flx.assets.associate_asset(__name__, base_url + 'mode-python.js')
flx.assets.associate_asset(__name__, base_url + 'theme-solarized_dark.js')
#@-<< ace assets >>
debug = False
debug_tree = True
#@+others
#@+node:ekr.20181103151350.1: **  init
def init():
    # At present, leoflexx is not a true plugin.
    # I am executing leoflexx.py from an external script.
    return False
#@+node:ekr.20181113041410.1: **  suppress_unwanted_log_messages
def suppress_unwanted_log_messages():
    '''
    Suppress the "Automatically scrolling cursor into view" messages by
    *allowing* only important messages.
    '''
    allowed = r'(Critical|Error|Leo|Session|Starting|Stopping|Warning)'
    pattern = re.compile(allowed, re.IGNORECASE)
    flx.set_log_level('INFO', pattern)
#@+node:ekr.20181107052522.1: ** class LeoApp(PyComponent)
# pscript never converts flx.PyComponents to JS.

class LeoApp(flx.PyComponent):
    '''
    The Leo Application.
    This is self.root for all flx.Widget objects!
    '''
    # This may be optional, but it doesn't hurt.
    main_window = flx.ComponentProp(settable=True)

    def init(self):
        c, g = self.open_bridge()
        print('app.init: c.frame', repr(c.frame))
        self.c, self.g = c, g
        self.gui = LeoBrowserGui(g)
        # Create all data-related ivars.
        self.create_all_data()
        # Create the main window and all its components.
        signon = '%s\n%s' % (g.app.signon, g.app.signon2)
        body = c.rootPosition().b
        redraw_dict = self.make_redraw_dict()
        main_window = LeoFlexxMainWindow(body, redraw_dict, signon)
        self._mutate('main_window', main_window)

    #@+others
    #@+node:ekr.20181111152542.1: *3* app.actions
    #@+node:ekr.20181111142921.1: *4* app.action: do_command
    @flx.action
    def do_command(self, command):

        w = self.main_window
        if command == 'redraw':
            d = self.make_redraw_dict()
            if 1:
                w.tree.redraw(d)
            else: # works.
                self.dump_redraw_dict(d)
        elif command == 'test':
            self.test_round_trip_positions()
            self.run_all_unit_tests()
        else:
            print('app.do_command: unknown command: %r' % command)
            ### To do: pass the command on to Leo's core.
    #@+node:ekr.20181113053154.1: *4* app.action: dump_redraw_dict & helpers
    @flx.action
    def dump_redraw_dict(self, d):
        '''Pretty print the redraw dict.'''
        print('app.dump_redraw dict...')
        padding, tag = None, 'c.p'
        self.dump_ap(d ['c.p'], padding, tag)
        level = 0
        for i, item in enumerate(d ['items']):
            self.dump_redraw_item(i, item, level)
            print('')
    #@+node:ekr.20181113085722.1: *5* app.action: dump_ap
    @flx.action
    def dump_ap (self, ap, padding=None, tag=None):
        '''Print an archived position fully.'''
        stack = ap ['stack']
        if not padding:
            padding = ''
        padding = padding + ' '*4 
        if stack:
            print('%s%s:...' % (padding, tag or 'ap'))
            padding = padding + ' '*4
            print('%schildIndex: %s v: %s %s stack...' % (
                padding,
                str(ap ['childIndex']),
                ap['gnx'],
                ap['headline'],
            ))
            padding = padding + ' '*4
            for d in ap ['stack']:
                print('%s%s %s %s' % (
                    padding,
                    str(d ['childIndex']).ljust(3),
                    d ['gnx'],
                    d ['headline'],
                ))
        else:
            print('%s%s: childIndex: %s v: %s stack: [] %s' % (
                padding, tag or 'ap',
                str(ap ['childIndex']).ljust(3),
                ap['gnx'],
                ap['headline'],
            ))
    #@+node:ekr.20181113091522.1: *4* app.action: redraw_item
    @flx.action
    def dump_redraw_item(self, i, item, level):
        '''Pretty print one item in the redraw dict.'''
        padding = ' '*4*level
        # Print most of the item.
        print('%s%s gnx: %s body: %s %s' % (
            padding,
            str(i).ljust(3),
            item ['gnx'].ljust(25),
            str(len(item ['body'])).ljust(4),
            item ['headline'],
        ))
        tag = None
        self.dump_ap(item ['ap'], padding, tag)
        # Print children...
        children = item ['children']
        if children:
            print('%sChildren...' % padding)
            print('%s[' % padding)
            padding = padding + ' '*4
            for j, child in enumerate(children):
                index = '%s.%s' % (i, j)
                self.dump_redraw_item(index, child, level+1)
            padding = padding[:-4]
            print('%s]' % padding)
    #@+node:ekr.20181112165240.1: *4* app.action: info (deprecated)
    @flx.action
    def info (self, s):
        '''Send the string s to the flex logger, at level info.'''
        if not isinstance(s, str):
            s = repr(s)
        flx.logger.info('Leo: ' + s)
            # A hack: automatically add the "Leo" prefix so
            # the top-level suppression logic will not delete this message.
    #@+node:ekr.20181113042549.1: *4* app.action: redraw
    def redraw (self):
        '''
        Send a **redraw list** to the tree.
        
        This is a recusive list lists of items (ap, gnx, headline) describing
        all and *only* the presently visible nodes in the tree.
        
        As a side effect, app.make_redraw_dict updates all internal dicts.
        '''
        print('app.redraw')
        w = self.main_window
        d = self.make_redraw_dict()
        w.tree.redraw(d)

        
    #@+node:ekr.20181111202747.1: *4* app.action: select_ap
    @flx.action
    def select_ap(self, ap):
        '''Select the position in Leo's core corresponding to the archived position.'''
        c = self.c
        p = self.ap_to_p(ap)
        c.frame.tree.select(p)
    #@+node:ekr.20181111095640.1: *4* app.action: send_children_to_tree
    @flx.action
    def send_children_to_tree(self, parent_ap):
        '''
        Call w.tree.receive_children(d), where d has the form:
            {
                'parent': parent_ap,
                'children': [ap1, ap2, ...],
            }
        '''
        w = self.main_window
        p = self.ap_to_p(parent_ap)
        if p.hasChildren():
            w.tree.receive_children({
                'parent': parent_ap,
                'children': [self.p_to_ap(z) for z in p.children()],
            })
        elif debug: ###
            # Not an error.
            print('app.send_children_to_tree: no children', p.h)
    #@+node:ekr.20181111095637.1: *4* app.action: set_body
    @flx.action
    def set_body(self, ap):
        '''Set the body text in LeoFlexxBody to the body text of indicated node.'''
        w = self.main_window
        gnx = ap ['gnx']
        v = self.gnx_to_vnode [gnx]
        assert v, repr(ap)
        w.body.set_body(v.b)
    #@+node:ekr.20181111095640.2: *4* app.action: set_status_to_unl
    @flx.action
    def set_status_to_unl(self, ap):
        '''Output the status line corresponding to ap.'''
        c, g, w = self.c, self.g, self.main_window
        gnxs = [z ['gnx'] for z in ap ['stack']]
        vnodes = [self.gnx_to_vnode[z] for z in gnxs]
        headlines = [v.h for v in vnodes]
        headlines.append(ap ['headline'])
        fn = g.shortFileName(c.fileName())
        w.status_line.set_text('%s#%s' % (fn, '->'.join(headlines)))
    #@+node:ekr.20181114015356.1: *3* app.create_all_data
    def create_all_data(self):
        '''Compute the initial values all data structures.'''
        t1 = time.clock()
        # This is likely the only data that ever will be needed.
        self.gnx_to_vnode = { v.gnx: v for v in self.c.all_unique_nodes() }
        t2 = time.clock()
        print('app.create_all_data: %5.2f sec. %s entries' % (
            (t2-t1), len(list(self.gnx_to_vnode.keys()))))
        if debug:
            self.test_round_trip_positions()
    #@+node:ekr.20181111155525.1: *3* app.archived positions
    #@+node:ekr.20181111204659.1: *4* app.p_to_ap (updates app.gnx_to_vnode)
    def p_to_ap(self, p):
        '''
        Convert a true Leo position to a serializable archived position.
        '''
        gnx = p.v.gnx
        if gnx not in self.gnx_to_vnode:
            print('=== update gnx_to_vnode', gnx.ljust(15), p.h,
                len(list(self.gnx_to_vnode.keys())))
            self.gnx_to_vnode [gnx] = p.v
        return {
            'childIndex': p._childIndex,
            'gnx': gnx,
            'headline': p.h, # For dumps.
            'stack': [{
                'gnx': v.gnx,
                'childIndex': childIndex,
                'headline': v.h, # For dumps & debugging.
            } for (v, childIndex) in p.stack ],
        }
    #@+node:ekr.20181111203114.1: *4* app.ap_to_p (uses gnx_to_vnode)
    def ap_to_p (self, ap):
        '''Convert an archived position to a true Leo position.'''
        childIndex = ap ['childIndex']
        v = self.gnx_to_vnode [ap ['gnx']]
        stack = [
            (self.gnx_to_vnode [d ['gnx']], d ['childIndex'])
                for d in ap ['stack']
        ]
        return leoNodes.position(v, childIndex, stack)
    #@+node:ekr.20181113043539.1: *4* app.make_redraw_dict & helpers
    def make_redraw_dict(self):
        '''
        Return a recursive, archivable, list of lists describing all and only
        the visible nodes of the tree.
        
        As a side effect, all LeoApp data are recomputed.
        '''
        c = self.c
        t1 = time.clock()
        aList = []
        p = c.rootPosition()
        ### Don't do this: it messes up tree redraw.
            # Testing: forcibly expand the first node.
            # p.expand()
        while p:
            if p.level() == 0 or p.isVisible():
                aList.append(self.make_dict_for_position(p))
                p.moveToNodeAfterTree()
            else:
                p.moveToThreadNext()
        d = {
            'c.p': self.p_to_ap(c.p),
            'items': aList,
        }
        if debug_tree:
            t2 = time.clock()
            print('app.make_redraw_dict: %5.4f sec' % (t2-t1))
        return d
    #@+node:ekr.20181113044701.1: *5* app.make_dict_for_position
    def make_dict_for_position(self, p):
        '''
        Recursively add a sublist for p and all its visible nodes.
        
        Update all data structures for p.
        '''
        c = self.c
        self.gnx_to_vnode[p.v.gnx] = p.v
        children = [
            self.make_dict_for_position(child)
                for child in p.children()
                    if child.isVisible(c)
        ]
        return {
            'ap': self.p_to_ap(p),
            'body': p.b,
            'children': children,
            'gnx': p.v.gnx,
            'headline': p.h,
        }
    #@+node:ekr.20181113180246.1: *4* app.test_round_trip_positions
    def test_round_trip_positions(self):
        '''Test the round tripping of p_to_ap and ap_to_p.'''
        c = self.c
        t1 = time.clock()
        for p in c.all_positions():
            ap = self.p_to_ap(p)
            p2 = self.ap_to_p(ap)
            assert p == p2, (repr(p), repr(p2), repr(ap))
        t2 = time.clock()
        if 1:
            print('app.test_new_tree: %5.3f sec' % (t2-t1))
    #@+node:ekr.20181105091545.1: *3* app.open_bridge
    def open_bridge(self):
        '''Can't be in JS.'''
        ### Monkey-Patch leoBridge.createGui???
        
        bridge = leoBridge.controller(gui = None,
            loadPlugins = False,
            readSettings = False,
            silent = False,
            tracePlugins = False,
            verbose = False, # True: prints log messages.
        )
        if not bridge.isOpen():
            flx.logger.error('Error opening leoBridge')
            return
        g = bridge.globals()
        path = g.os_path_finalize_join(g.app.loadDir, '..', 'core', 'LeoPyRef.leo')
        if not g.os_path_exists(path):
            flx.logger.error('open_bridge: does not exist: %r' % path)
            return
        c = bridge.openLeoFile(path)
        return c, g
    #@+node:ekr.20181112182636.1: *3* app.run_all_unit_tests
    def run_all_unit_tests (self):
        '''
        Run all unit tests from the bridge using the browser gui.
        '''
        print('app.test: not ready yet')
        ### runUnitTests(self.c, self.g)
    #@-others
#@+node:ekr.20181115071559.1: ** Python side wrappers
#@+node:ekr.20181115092337.3: *3* class LeoBrowserBody
class LeoBrowserBody(flx.PyComponent): ### leoFrame.NullBody):
   
    def init(self, c, g, frame):
        # pylint: disable=arguments-differ
        self.c = c
        self.g = g
        self.wrapper = StringTextWrapper(c=self.c, name='body')
        ###
            # self.insertPoint = 0
            # self.selection = 0, 0
            # self.s = "" # The body text
            # self.widget = None
            # self.editorWidgets['1'] = wrapper
            # self.colorizer = NullColorizer(self.c)
    #@+others
    #@+node:ekr.20181115092337.4: *4* LeoBrowserBody interface
    # At present theses do not issue messages.

    # Birth, death...
    def createControl(self, parentFrame, p):
        pass

    # Editors...
    def addEditor(self, event=None):
        pass
    def assignPositionToEditor(self, p):
        pass
    def createEditorFrame(self, w):
        return None
    def cycleEditorFocus(self, event=None):
        pass
    def deleteEditor(self, event=None):
        pass
    def selectEditor(self, w):
        pass
    def selectLabel(self, w):
        pass
    def setEditorColors(self, bg, fg):
        pass
    def unselectLabel(self, w):
        pass
    def updateEditors(self):
        pass
    # Events...
    def forceFullRecolor(self):
        pass
    def scheduleIdleTimeRoutine(self, function, *args, **keys):
        pass
    #@+node:ekr.20181115092337.5: *4* bb.setFocus
    def setFocus(self):
        pass
        ### self.message('set-focus-to-body')
    #@-others
#@+node:ekr.20181115092337.6: *3* class LeoBrowserFrame
class LeoBrowserFrame(flx.PyComponent): ### leoFrame.LeoFrame):
    
    def init(self, c, g, title, gui):
        '''Ctor for the LeoBrowserFrame class.'''
        # pylint: disable=arguments-differ
        self.c = c
        self.g = g
        c.frame = self
        assert self.c
        self.wrapper = None
            # was BrowserIconBarClass(self.c, self)
        self.isNullFrame = True
        self.outerFrame = None
        self.ratio = self.secondary_ratio = 0.5
        self.title = title
        self.top = None # Always None.
        # Create the component objects.
        self.body = LeoBrowserBody(frame=self)
        self.iconBar = LeoBrowserIconBar(c=c, parentFrame=self)
        self.log = LeoBrowserLog(frame=self)
        self.menu = LeoBrowserMenu(frame=self)
        self.statusLine = LeoBrowserStatusLine(c=c, parentFrame=self)
        self.tree = LeoBrowserTree(frame=self)
        # Default window position.
        self.w, self.h, self.x, self.y = 600, 500, 40, 40
    
    #@+others
    #@+node:ekr.20181115092337.7: *4* bf.init

    #@+node:ekr.20181115092337.8: *4* bf.finishCreate
    def finishCreate(self):
        pass
        ### self.createFirstTreeNode()
            # Call the base LeoFrame method.
    #@+node:ekr.20181115092337.9: *4* bf.oops
    def oops(self):
        g = self.c
        g.trace("LeoBrowserFrame", g.callers(4))
    #@+node:ekr.20181115092337.10: *4* bf.redirectors (To do: add messages)
    def bringToFront(self):
        pass
    def cascade(self, event=None):
        pass
    def contractBodyPane(self, event=None):
        pass
    def contractLogPane(self, event=None):
        pass
    def contractOutlinePane(self, event=None):
        pass
    def contractPane(self, event=None):
        pass
    def deiconify(self):
        pass
    def destroySelf(self):
        pass
    def equalSizedPanes(self, event=None):
        pass
    def expandBodyPane(self, event=None):
        pass
    def expandLogPane(self, event=None):
        pass
    def expandOutlinePane(self, event=None):
        pass
    def expandPane(self, event=None):
        pass
    def fullyExpandBodyPane(self, event=None):
        pass
    def fullyExpandLogPane(self, event=None):
        pass
    def fullyExpandOutlinePane(self, event=None):
        pass
    def fullyExpandPane(self, event=None):
        pass
    def get_window_info(self):
        return 600, 500, 20, 20
    def hideBodyPane(self, event=None):
        pass
    def hideLogPane(self, event=None):
        pass
    def hideLogWindow(self, event=None):
        pass
    def hideOutlinePane(self, event=None):
        pass
    def hidePane(self, event=None):
        pass
    def leoHelp(self, event=None):
        pass
    def lift(self):
        pass
    def minimizeAll(self, event=None):
        pass
    def resizePanesToRatio(self, ratio, secondary_ratio):
        pass
    def resizeToScreen(self, event=None):
        pass
    def setInitialWindowGeometry(self):
        pass
    def setTopGeometry(self, w, h, x, y, adjustSize=True):
        return 0, 0, 0, 0
    def setWrap(self, flag, force=False):
        pass
    def toggleActivePane(self, event=None):
        pass
    def toggleSplitDirection(self, event=None):
        pass
    def update(self):
        pass
    #@-others
#@+node:ekr.20181113041113.1: *3* class LeoBrowserGui(PyComponent)
class LeoBrowserGui(flx.PyComponent):
    '''
    Leo's Browser Gui.
    
    This should be a subclass of leo.core.leoGui.LeoGui, but pscript does
    not support multiple inheritance.
    
    The following methods are a meld of the NullGui and LeoGui classes.
    '''
    #@+others
    #@+node:ekr.20181115042955.1: *4* gui.init
    def init (self, g):
        '''The ctor for the LeoBroswerGui class.'''
        # pylint: disable=arguments-differ
        #
        # New ivars.
        self.g = g
        #
        # From LeoGui, except ivars set in NullGui...
        ### Not used.
            # self.FKeys = [] # The representation of F-keys.
            # self.ScriptingControllerClass = NullScriptingControllerClass
            # self.globalFindDialog = None
            # self.globalFindTab = None
            # self.globalFindTabManager = None
            # self.ignoreChars = [] # Keys that are always to be ignore.
            # self.leoIcon = None
            # self.mainLoop = None
            # self.root = None
            # self.specialChars = [] # A list of characters/keys to be handle specially.
            # self.splashScreen = None
            # self.utils = None
        #
        # From NullGui...
        ### Not used.
            # self.focusWidget = None
            # self.idleTimeClass = g.NullObject
            # self.lastFrame = None
            # self.script = None
        self.mGuiName = 'BrowserGui'
        self.clipboardContents = ''
        self.isNullGui = True
    #@+node:ekr.20181115044516.1: *4* Overrides (to do)
    #@+node:ekr.20181115042835.4: *5* gui.create_key_event
    def create_key_event(self, c,
        binding=None,
        char=None,
        event=None,
        w=None,
        x=None, x_root=None,
        y=None, y_root=None,
    ):
        # Do not call strokeFromSetting here!
        # For example, this would wrongly convert Ctrl-C to Ctrl-c,
        # in effect, converting a user binding from Ctrl-Shift-C to Ctrl-C.
        g = self.g
        g.trace(g.callers())
        return leoGui.LeoKeyEvent(c, char, event, binding, w, x, y, x_root, y_root)
    #@+node:ekr.20181115042835.5: *5* gui.guiName
    def guiName(self):
        
        return self.mGuiName
    #@+node:ekr.20181115042930.6: *5* gui.isTextWidget & isTextWrapper
    def isTextWidget(self, w):
        return True # Must be True for unit tests.

    def isTextWrapper(self, w):
        '''Return True if w is a Text widget suitable for text-oriented commands.'''
        return w and getattr(w, 'supportsHighLevelInterface', None)
    #@+node:ekr.20181115042753.1: *5* gui.oops
    def oops(self):
        print("LeoBrowserGui.oops", self.g.callers(4))
    #@+node:ekr.20181115042930.9: *5* gui.runMainLoop
    def runMainLoop(self):
        """Run the null gui's main loop."""
        print('gui.runMainLoop: not ready yet.')
        ###
            # g = self.g
            # if self.script:
                # frame = self.lastFrame
                # g.app.log = frame.log
                # self.lastFrame.c.executeScript(script=self.script)
            # else:
                # print('**** NullGui.runMainLoop: terminating Leo.')
            # # Getting here will terminate Leo.
    #@+node:ekr.20181115042835.28: *5* gui.widget_name (To do)
    def widget_name(self, w):
        # First try the widget's getName method.
        if not 'w':
            return '<no widget>'
        elif hasattr(w, 'getName'):
            return w.getName()
        elif hasattr(w, '_name'):
            return w._name
        else:
            return repr(w)
    #@+node:ekr.20181115042835.7: *5* gui.event_generate (Needed?)
    def event_generate(self, c, char, shortcut, w):
        print('gui.event_generated', self.g.callers())
        event = self.create_key_event(c, binding=shortcut, char=char, w=w)
        c.k.masterKeyHandler(event)
        c.outerUpdate()
    #@+node:ekr.20181115042908.1: *4* From NullGui
    #@+node:ekr.20181115042930.3: *5* NullGui.dialogs
    def runAboutLeoDialog(self, c, version, theCopyright, url, email):
        return self.simulateDialog("aboutLeoDialog", None)

    def runAskLeoIDDialog(self):
        return self.simulateDialog("leoIDDialog", None)

    def runAskOkDialog(self, c, title, message=None, text="Ok"):
        return self.simulateDialog("okDialog", "Ok")

    def runAskOkCancelNumberDialog(self, c, title, message,
        cancelButtonText=None,
        okButtonText=None,
    ):
        return self.simulateDialog("numberDialog", -1)

    def runAskOkCancelStringDialog(self, c, title, message,
        cancelButtonText=None,
        okButtonText=None,
        default="",
        wide=False,
    ):
        return self.simulateDialog("stringDialog", '')

    def runCompareDialog(self, c):
        return self.simulateDialog("compareDialog", '')

    def runOpenFileDialog(self, c, title, filetypes, defaultextension,
        multiple=False,
        startpath=None,
    ):
        return self.simulateDialog("openFileDialog", None)

    def runSaveFileDialog(self, c, initialfile, title, filetypes, defaultextension):
        return self.simulateDialog("saveFileDialog", None)

    def runAskYesNoDialog(self, c, title,
        message=None,
        yes_all=False,
        no_all=False,
    ):
        return self.simulateDialog("yesNoDialog", "no")

    def runAskYesNoCancelDialog(self, c, title,
        message=None,
        yesMessage="Yes",
        noMessage="No",
        yesToAllMessage=None,
        defaultButton="Yes",
        cancelMessage=None,
    ):
        return self.simulateDialog("yesNoCancelDialog", "cancel")

    def simulateDialog(self, key, defaultVal):
        return defaultVal
    #@+node:ekr.20181115042930.4: *5* NullGui.clipboard & focus
    def get_focus(self, *args, **kwargs):
        return self.focusWidget

    def getTextFromClipboard(self):
        return self.clipboardContents

    def replaceClipboardWith(self, s):
        self.clipboardContents = s

    def set_focus(self, commander, widget):
        self.focusWidget = widget
    #@+node:ekr.20181115042930.5: *5* NullGui.do nothings
    def alert(self, message):
        pass
    def attachLeoIcon(self, window):
        pass
    def destroySelf(self):
        pass
    def finishCreate(self): 
        pass
    def getFontFromParams(self, family, size, slant, weight, defaultSize=12):
        return self.g.app.config.defaultFont
    def getIconImage(self, name):
        return None
    def getImageImage(self, name):
        return None
    def getTreeImage(self, c, path):
        return None
    def get_window_info(self, window):
        return 600, 500, 20, 20
    def onActivateEvent(self, *args, **keys): 
        pass
    def onDeactivateEvent(self, *args, **keys): 
        pass
    #@+node:ekr.20181115042930.8: *5* NullGui.panels
    def createComparePanel(self, c):
        """Create Compare panel."""
        self.oops()

    def createFindTab(self, c, parentFrame):
        """Create a find tab in the indicated frame."""
        pass # Now always done during startup.

    def createLeoFrame(self, c, title):
        """Create a null Leo Frame."""
        self.oops()
        ###
            # gui = self
            # self.lastFrame = leoFrame.NullFrame(c, title, gui)
            # return self.lastFrame
    #@+node:ekr.20181115042828.1: *4* From LeoGui
    #@+node:ekr.20181115042835.6: *5* LeoGui.setScript
    def setScript(self, script=None, scriptFileName=None):

        self.script = script
        self.scriptFileName = scriptFileName
    #@+node:ekr.20181115042835.22: *5* LeoGui.dismiss_spash_screen
    def dismiss_splash_screen(self):
        pass # May be overridden in subclasses.
    #@+node:ekr.20181115042835.23: *5* LeoGui.ensure_commander_visible
    def ensure_commander_visible(self, c):
        """E.g. if commanders are in tabs, make sure c's tab is visible"""
        pass
    #@+node:ekr.20181115042835.25: *5* LeoGui.killPopupMenu & postPopupMenu
    # These definitions keep pylint happy.

    def postPopupMenu(self, *args, **keys):
        pass
    #@+node:ekr.20181115042835.27: *5* LeoGui.put_help
    def put_help(self, c, s, short_title):
        pass
    #@-others
#@+node:ekr.20181115092337.21: *3* class LeoBrowserIconBar
class LeoBrowserIconBar(flx.PyComponent): ### leoFrame.NullIconBarClass):

    def init(self, c, g):
        # pylint: disable=arguments-differ
        pass
        # leoFrame.NullIconBarClass.__init__(self,
            # c=c, parentFrame=parentFrame)
        ###
            # self.c = c
            # self.iconFrame = None
            # self.parentFrame = parentFrame
            # self.w = g.NullObject()
#@+node:ekr.20181115092337.22: *3* class LeoBrowserLog
class LeoBrowserLog(flx.PyComponent): ### leoFrame.NullLog):
    
    def init(self, c, g):
        # pylint: disable=arguments-differ
        self.c = c
        self.g = g
    ###
        # self.enabled = True
        # self.isNull = True
        # self.logNumber = 0
        # self.widget = self.createControl(parentFrame)
#@+node:ekr.20181115092337.23: *4*  bl.not used
if 0:
    #@+others
    #@+node:ekr.20181115092337.24: *5* bl.createControl
    def createControl(self, parentFrame):
        return self.createTextWidget(parentFrame)
    #@+node:ekr.20181115092337.25: *5* bl.finishCreate
    def finishCreate(self):
        pass
    #@+node:ekr.20181115092337.26: *5* bl.isLogWidget
    def isLogWidget(self, w):
        return False
    #@+node:ekr.20181115092337.27: *5* bl.tabs
    def clearTab(self, tabName, wrap='none'):
        pass

    def createCanvas(self, tabName):
        pass

    def createTab(self, tabName, createText=True, widget=None, wrap='none'):
        pass

    def deleteTab(self, tabName, force=False): pass

    def getSelectedTab(self): return None

    def lowerTab(self, tabName): pass

    def raiseTab(self, tabName): pass

    def renameTab(self, oldName, newName): pass

    def selectTab(self, tabName, createText=True, widget=None, wrap='none'): pass
    #@-others
#@+node:ekr.20181115092337.28: *4* bl.createTextWidget
def createTextWidget(self, parentFrame):
    self.logNumber += 1
    c = self.c
    log = StringTextWrapper(c=c, name="log-%d" % self.logNumber)
    return log
#@+node:ekr.20181115092337.29: *4* bl.oops
def oops(self):
    g = self.g
    g.trace("LeoBrowserLog:", g.callers(4))
#@+node:ekr.20181115092337.30: *4* bl.put and putnl
def put(self, s,
    color=None,
    tabName='Log',
    from_redirect=False,
    nodeLink=None,
):
    print(s) ###
    ##self.message('put', s=s, tabName=tabName)

def putnl(self, tabName='Log'):
    print('') ###
    ### self.message('put-nl', tabName=tabName)
#@+node:ekr.20181115092337.31: *3* class LeoBrowserMenu
class LeoBrowserMenu(flx.PyComponent): ### leoMenu.NullMenu):
    
    def init(self, c, g):
        # pylint: disable=arguments-differ
        self.c = c
        self.g = g
#@+node:ekr.20181115092337.32: *3* class LeoBrowserStatusLine
class LeoBrowserStatusLine(flx.PyComponent): ###leoFrame.NullStatusLineClass):
    
    def init(self, c, g):
        # pylint: disable=arguments-differ
        self.c = c
        self.g = g
#@+node:ekr.20181115092337.57: *3* class LeoBrowserTree
class LeoBrowserTree(flx.PyComponent): ### leoFrame.NullTree):
    
    def init(self, c, g):
        # pylint: disable=arguments-differ
        self.c = c
        self.g = g
    
    ###
        # self.editWidgetsDict = {}
            # Keys are tnodes, values are StringTextWidgets.
        # self.font = None
        # self.fontName = None
        # self.canvas = None
        # self.redrawCount = 0
        # self.updateCount = 0
#@+node:ekr.20181115092337.58: *4*  bt.not used
if 0:
    #@+others
    #@+node:ekr.20181115092337.59: *5* bt.printWidgets
    def printWidgets(self):
        d = self.editWidgetsDict
        for key in d:
            # keys are vnodes, values are StringTextWidgets.
            w = d.get(key)
            print('w', w, 'v.h:', key.headString, 's:', repr(w.s))
    #@+node:ekr.20181115092337.60: *5* bt.Drawing & scrolling
    def redraw_after_contract(self, p):
        self.redraw()

    def redraw_after_expand(self, p):
        self.redraw()

    def redraw_after_head_changed(self):
        self.redraw()

    def redraw_after_icons_changed(self):
        self.redraw()

    def redraw_after_select(self, p=None):
        self.redraw()
    #@-others
    
#@+node:ekr.20181115092337.61: *4* bt.drawIcon
def drawIcon(self, p):
    pass
    ### self.message('draw-icon', gnx=p.gnx)
#@+node:ekr.20181115092337.62: *4* bt.edit_widget
def edit_widget(self, p):
    ### self.message('edit-widget', gnx=p.gnx)
    d = self.editWidgetsDict
    if not p or not p.v:
        return None
    w = d.get(p.v)
    if not w:
        d[p.v] = w = StringTextWrapper(
            c=self.c,
            name='head-%d' % (1 + len(list(d.keys()))))
        w.setAllText(p.h)
    return w
#@+node:ekr.20181115092337.63: *4* bt.editLabel
def editLabel(self, p, selectAll=False, selection=None):
    '''Start editing p's headline.'''
    ### self.message('edit-label', gnx=p.gnx)
    self.endEditLabel()
    if p:
        self.revertHeadline = p.h
            # New in 4.4b2: helps undo.
        wrapper = StringTextWrapper(c=self.c, g=self.g, name='head-wrapper')
        e = None
        return e, wrapper
    else:
        return None, None
#@+node:ekr.20181115092337.64: *4* bt.redraw
def redraw(self, p=None):
    ### self.message('redraw-tree')
    self.redrawCount += 1
    return p
        # Support for #503: Use string/null gui for unit tests
        
redraw_now = redraw
#@+node:ekr.20181115092337.65: *4* bt.scrollTo
def scrollTo(self, p):
    pass
    ### self.message('scroll-tree', gnx=p.gnx)
#@+node:ekr.20181115092337.66: *4* bt.setHeadline
def setHeadline(self, p, s):
    '''
    Set the actual text of the headline widget.

    This is called from the undo/redo logic to change the text before redrawing.
    '''
    ### self.message('set-headline', gnx=p.gnx, s=s)
    w = self.edit_widget(p)
    if w:
        w.delete(0, 'end')
        if s.endswith('\n') or s.endswith('\r'):
            s = s[: -1]
        w.insert(0, s)
        self.revertHeadline = s
    else:
        print('-' * 20, 'oops')
#@+node:ekr.20181115092337.33: *3* class StringTextWrapper (test)
class StringTextWrapper(flx.PyComponent):
    '''
    A class that represents text as a Python string.
    This class forwards messages to the browser.
    '''
    def init(self, c, g, name):
        '''Ctor for the StringTextWrapper class.'''
        # pylint: disable=arguments-differ
        self.c = c
        self.g = g
        self.name = name
        self.ins = 0
        self.sel = 0, 0
        self.s = ''
        self.supportsHighLevelInterface = True
        self.widget = None # This ivar must exist, and must be None.
    
    def __repr__(self):
        return '<StringTextWrapper: %s>' % (self.name)
    
    def getName(self):
        '''StringTextWrapper.'''
        return self.name # Essential.

    #@+others
    #@+node:ekr.20181115092337.34: *4* stw.Clipboard
    def clipboard_clear(self):
        g = self.g
        g.app.gui.replaceClipboardWith('')

    def clipboard_append(self, s):
        g = self.g
        s1 = g.app.gui.getTextFromClipboard()
        self.g.app.gui.replaceClipboardWith(s1 + s)
    #@+node:ekr.20181115092337.35: *4* stw.Config
    def setStyleClass(self, name):
        pass 
        ### self.message('set-style', name=name)

    def tag_configure(self, colorName, **kwargs):
        pass
        ### kwargs['color-name'] = colorName
        ### self.message('configure-tag', keys=kwargs)
    #@+node:ekr.20181115092337.36: *4* stw.flashCharacter
    def flashCharacter(self, i, bg='white', fg='red', flashes=3, delay=75):
        pass
        ### self.message('flash-character', i=i, bg=bg, fg=fg, flashes=flashes, delay=delay)
    #@+node:ekr.20181115092337.37: *4* stw.Focus
    def getFocus(self):
        # This isn't in StringTextWrapper.
        pass
        ### self.message('get-focus')

    def setFocus(self):
        pass
        ### self.message('set-focus')
    #@+node:ekr.20181115092337.38: *4* stw.Insert Point
    def see(self, i):
        pass
        ### self.message('see-position', i=i)

    def seeInsertPoint(self):
        pass
        ### self.message('see-insert-point')
        
    #@+node:ekr.20181115092337.39: *4* stw.Scrolling
    def getXScrollPosition(self):
        ### self.message('get-x-scroll')
        return 0

    def getYScrollPosition(self):
        ### self.message('get-y-scroll')
        return 0
        
    def setXScrollPosition(self, i):
        pass
        ### self.message('set-x-scroll', i=i)
        
    def setYScrollPosition(self, i):
        pass
        ### self.message('set-y-scroll', i=i)
        
    #@+node:ekr.20181115092337.40: *4* stw.Text
    #@+node:ekr.20181115092337.41: *5* stw.appendText
    def appendText(self, s):
        '''StringTextWrapper.'''
        self.s = self.s + s
        self.ins = len(self.s)
        self.sel = self.ins, self.ins
        ### self.message('body-append-text', s=s)
    #@+node:ekr.20181115092337.42: *5* stw.delete
    def delete(self, i, j=None):
        '''StringTextWrapper.'''
        i = self.toPythonIndex(i)
        if j is None: j = i + 1
        j = self.toPythonIndex(j)
        # This allows subclasses to use this base class method.
        if i > j: i, j = j, i
        s = self.getAllText()
        self.setAllText(s[: i] + s[j:])
        # Bug fix: 2011/11/13: Significant in external tests.
        self.setSelectionRange(i, i, insert=i)
        ### self.message('body-delete-text',
            # s=s[:i]+s[j:],
            # sel=(i,i,i))
    #@+node:ekr.20181115092337.43: *5* stw.deleteTextSelection
    def deleteTextSelection(self):
        '''StringTextWrapper.'''
        i, j = self.getSelectionRange()
        self.delete(i, j)
    #@+node:ekr.20181115092337.44: *5* stw.get
    def get(self, i, j=None):
        '''StringTextWrapper.'''
        g = self.g
        i = self.toPythonIndex(i)
        if j is None:
            j = i + 1
        j = self.toPythonIndex(j)
        s = self.s[i: j]
        ### self.message('body-get-text', s=s)
        return g.toUnicode(s)
    #@+node:ekr.20181115092337.45: *5* stw.getAllText
    def getAllText(self):
        '''StringTextWrapper.'''
        g = self.g
        s = self.s
        ### self.message('body-get-all-text')
        return g.toUnicode(s)
    #@+node:ekr.20181115092337.46: *5* stw.getInsertPoint
    def getInsertPoint(self):
        '''StringTextWrapper.'''
        # self.message('body-get-insert-point')
        i = self.ins
        if i is None:
            if self.virtualInsertPoint is None:
                i = 0
            else:
                i = self.virtualInsertPoint
        self.virtualInsertPoint = i
        return i
    #@+node:ekr.20181115092337.47: *5* stw.getSelectedText
    def getSelectedText(self):
        '''StringTextWrapper.'''
        g = self.g
        # self.message('body-get-selected-text')
        i, j = self.sel
        s = self.s[i: j]
        return g.toUnicode(s)
    #@+node:ekr.20181115092337.48: *5* stw.getSelectionRange
    def getSelectionRange(self, sort=True):
        '''StringTextWrapper'''
        # self.message('body-get-selection-range')
        sel = self.sel
        if len(sel) == 2 and sel[0] >= 0 and sel[1] >= 0:
            i, j = sel
            if sort and i > j:
                sel = j, i
            return sel
        else:
            i = self.ins
            return i, i
    #@+node:ekr.20181115092337.49: *5* stw.hasSelection
    def hasSelection(self):
        '''StringTextWrapper.'''
        # self.message('body-has-selection')
        i, j = self.getSelectionRange()
        return i != j
    #@+node:ekr.20181115092337.50: *5* stw.insert
    def insert(self, i, s):
        '''StringTextWrapper.'''
        i = self.toPythonIndex(i)
        s1 = s
        self.s = self.s[: i] + s1 + self.s[i:]
        i += len(s1)
        self.ins = i
        self.sel = i, i
    #@+node:ekr.20181115092337.51: *5* stw.selectAllText
    def selectAllText(self, insert=None):
        '''StringTextWrapper.'''
        self.setSelectionRange(0, 'end', insert=insert)
    #@+node:ekr.20181115092337.52: *5* stw.setAllText
    def setAllText(self, s):
        '''StringTextWrapper.'''
        self.s = s
        i = len(self.s)
        self.ins = i
        self.sel = i, i
    #@+node:ekr.20181115092337.53: *5* stw.setInsertPoint
    def setInsertPoint(self, pos, s=None):
        '''StringTextWrapper.'''
        self.virtualInsertPoint = i = self.toPythonIndex(pos)
        self.ins = i
        self.sel = i, i
    #@+node:ekr.20181115092337.54: *5* stw.setSelectionRange
    def setSelectionRange(self, i, j, insert=None):
        '''StringTextWrapper.'''
        i, j = self.toPythonIndex(i), self.toPythonIndex(j)
        self.sel = i, j
        self.ins = j if insert is None else self.toPythonIndex(insert)
    #@+node:ekr.20181115092337.55: *5* stw.toPythonIndex
    def toPythonIndex(self, index):
        '''StringTextWrapper.'''
        g = self.g
        return g.toPythonIndex(self.s, index)
    #@+node:ekr.20181115092337.56: *5* stw.toPythonIndexRowCol
    def toPythonIndexRowCol(self, index):
        '''StringTextWrapper.'''
        g = self.g
        s = self.getAllText()
        i = self.toPythonIndex(index)
        row, col = g.convertPythonIndexToRowCol(s, i)
        return i, row, col
    #@-others
#@+node:ekr.20181107052700.1: ** Js side: flx.Widgets
#@+node:ekr.20181104082144.1: *3* class LeoFlexxBody

class LeoFlexxBody(flx.Widget):
    
    """ A CodeEditor widget based on Ace.
    """

    CSS = """
    .flx-CodeEditor > .ace {
        width: 100%;
        height: 100%;
    }
    """

    def init(self, body):
        # pylint: disable=arguments-differ
        # pylint: disable=undefined-variable
            # window
        global window
        self.ace = window.ace.edit(self.node, "editor")
        self.ace.navigateFileEnd()  # otherwise all lines highlighted
        self.ace.setTheme("ace/theme/solarized_dark")
        self.ace.getSession().setMode("ace/mode/python")
        self.set_body(body)

    @flx.reaction('size')
    def __on_size(self, *events):
        self.ace.resize()
        
    @flx.action
    def set_body(self, body):
        self.ace.setValue(body)
#@+node:ekr.20181104082149.1: *3* class LeoFlexxLog
class LeoFlexxLog(flx.Widget):

    CSS = """
    .flx-CodeEditor > .ace {
        width: 100%;
        height: 100%;
    }
    """

    def init(self, signon):
        # pylint: disable=arguments-differ
        # pylint: disable=undefined-variable
            # window
        global window
        self.ace = window.ace.edit(self.node, "editor")
        self.ace.navigateFileEnd()  # otherwise all lines highlighted
        self.ace.setTheme("ace/theme/solarized_dark")
        self.ace.setValue(signon)
        
    @flx.action
    def put(self, s):
        self.ace.setValue(self.ace.getValue() + '\n' + s)

    @flx.reaction('size')
    def __on_size(self, *events):
        self.ace.resize()
#@+node:ekr.20181104082130.1: *3* class LeoFlexxMainWindow
class LeoFlexxMainWindow(flx.Widget):
    
    '''
    Leo's main window, that is, root.main_window.
    
    Each property x below is accessible as root.main_window.x.
    '''
    # All these properties *are* needed.
    body = flx.ComponentProp(settable=True)
    log = flx.ComponentProp(settable=True)
    minibuffer = flx.ComponentProp(settable=True)
    status_line = flx.ComponentProp(settable=True)
    tree = flx.ComponentProp(settable=True)

    def init(self, body_s, data, signon):
        # pylint: disable=arguments-differ
        with flx.VSplit():
            with flx.HSplit(flex=1):
                tree = LeoFlexxTree(data, flex=1)
                log = LeoFlexxLog(signon, flex=1)
            body = LeoFlexxBody(body_s, flex=1)
            minibuffer = LeoFlexxMiniBuffer()
            status_line = LeoFlexxStatusLine()
        for name, prop in (
            ('body', body),
            ('log', log),
            ('minibuffer', minibuffer),
            ('status_line', status_line),
            ('tree', tree),
        ):
            self._mutate(name, prop)

    #@+others
    #@-others
#@+node:ekr.20181104082154.1: *3* class LeoFlexxMiniBuffer
class LeoFlexxMiniBuffer(flx.Widget):

    def init(self): 
        with flx.HBox():
            flx.Label(text='Minibuffer')
            self.widget = flx.LineEdit(flex=1, placeholder_text='Enter command')
        self.widget.apply_style('background: yellow')
    
    @flx.action
    def set_text(self, s):
        self.widget.set_text(s)
        
    @flx.reaction('widget.user_done')
    def on_event(self, *events):
        for ev in events:
            command = self.widget.text
            if command.strip():
                self.widget.set_text('')
                self.root.do_command(command)
#@+node:ekr.20181104082201.1: *3* class LeoFlexxStatusLine
class LeoFlexxStatusLine(flx.Widget):
    
    def init(self):
        with flx.HBox():
            flx.Label(text='Status Line')
            self.widget = flx.LineEdit(flex=1, placeholder_text='Status')
        self.widget.apply_style('background: green')

    @flx.action
    def set_text(self, s):
        self.widget.set_text(s)
#@+node:ekr.20181104082138.1: *3* class LeoFlexxTree
class LeoFlexxTree(flx.Widget):

    CSS = '''
    .flx-TreeWidget {
        background: #000;
        color: white;
        /* background: #ffffec; */
        /* Leo Yellow */
        /* color: #afa; */
    }
    '''
    
    def init(self, redraw_dict):
        # pylint: disable=arguments-differ
        self.leo_items = {}
            # Keys are ap keys, created by tree.ap_to_key.
            # values are LeoTreeItems.
        self.leo_populated_dict = {}
            # Keys are ap keys, created by tree.ap_to_key.
            # values are ap's.
        self.clear_tree()
        self.tree = flx.TreeWidget(flex=1, max_selected=1)
            # The gnx of the selected tree item.
        self.redraw_from_dict(redraw_dict)
        
    #@+others
    #@+node:ekr.20181112163222.1: *4* tree.actions
    #@+node:ekr.20181112163252.1: *5* tree.action: clear_tree
    @flx.action
    def clear_tree(self):
        '''
        Completely clear the tree, preparing to recreate it.
        
        Important: we do *not* clear self.tree itself!
        '''
        # pylint: disable=access-member-before-definition
        #
        # print('===== tree.clear_tree')
        #
        # Clear all tree items.
        for item in self.leo_items.values():
            if debug or debug_tree:
                print('tree.clear_tree: dispose: %r' % item)
            item.dispose()
        #
        # Clear the internal data structures.
        self.leo_items = {}
        self.leo_populated_dict = {}
    #@+node:ekr.20181110175222.1: *5* tree.action: receive_children
    @flx.action
    def receive_children(self, d):
        '''
        Using d, populate the children of ap. d has the form:
            {
                'parent': ap,
                'children': [ap1, ap2, ...],
            }
        '''
        parent_ap = d ['parent']
        children = d ['children']
        self.populate_children(children, parent_ap)
    #@+node:ekr.20181113043004.1: *5* tree.action: redraw
    @flx.action
    def redraw(self, redraw_dict):
        '''
        Clear the present tree and redraw using the redraw_list.
        '''
        self.clear_tree()
        self.redraw_from_dict(redraw_dict)
    #@+node:ekr.20181114072307.1: *4* tree.ap_to_key
    def ap_to_key(self, ap):
        '''Produce a key for the given ap.'''
        childIndex = ap ['childIndex']
        gnx = ap ['gnx']
        headline = ap ['headline'] # Important for debugging.
        stack = ap ['stack']
        stack_s = '::'.join([
            'childIndex: %s, gnx: %s' % (z ['childIndex'], z ['gnx'])
                for z in stack
        ])
        key = 'Tree key<childIndex: %s, gnx: %s, %s <stack: %s>>' % (
            childIndex, gnx, headline, stack_s or '[]')
        if False and key not in self.leo_populated_dict:
            print('')
            print('tree.ap_to_key: new key', ap ['headline'])
            print('key', key)
        return key
    #@+node:ekr.20181112172518.1: *4* tree.reactions
    #@+node:ekr.20181109083659.1: *5* tree.reaction: on_selected_event
    @flx.reaction('tree.children**.selected')
    def on_selected_event(self, *events):
        '''
        Update the tree and body text when the user selects a new tree node.
        '''
        for ev in events:
            if ev.new_value:
                # We are selecting a node, not de-selecting it.
                ap = ev.source.leo_ap
                self.leo_selected_ap = ap
                    # Track the change.
                self.root.set_body(ap)
                    # Set the body text directly.
                self.root.set_status_to_unl(ap)
                    # Set the status line directly.
                self.root.send_children_to_tree(ap)
                    # Send the children back to us.
    #@+node:ekr.20181104080854.3: *5* tree.reaction: on_tree_event
    # actions: set_checked, set_collapsed, set_parent, set_selected, set_text, set_visible
    @flx.reaction(
        'tree.children**.checked',
        'tree.children**.collapsed',
        'tree.children**.visible', # Never seems to fire.
    )
    def on_tree_event(self, *events):
        for ev in events:
            if 0:
                self.show_event(ev)
    #@+node:ekr.20181111011928.1: *4* tree.populate_children
    def populate_children(self, children, parent_ap):
        '''Populate parent with the children if necessary.'''
        trace = False
        if trace: print('tree.populate_children...')
        parent_key = self.ap_to_key(parent_ap)
        if parent_key in self.leo_populated_dict:
            print('===== tree.populate_children: already populated', parent_ap ['headline'])
            # print('key: %r' % key)
            # self.root.dump_ap(parent_ap, None, 'parent_ap')
            return
        #
        # Set the key once, here.
        self.leo_populated_dict [parent_key] = parent_ap
        #
        # Populate the items.
        if parent_key not in self.leo_items:
            print('tree.populate_children: can not happen')
            self.root.dump_ap(parent_ap, None, 'parent_ap')
            for item in self.leo_items:
                print(item)
            return
        if trace:
            print('tree.populate_children:', len(children))
            print('parent_ap', repr(parent_ap))
            print('parent item:', repr(self.leo_items[parent_ap]))
        with self.leo_items[parent_key]:
            for child_ap in children:
                headline = child_ap ['headline']
                child_key = self.ap_to_key(child_ap)
                child_item = LeoFlexxTreeItem(child_ap, text=headline, checked=None, collapsed=True)
                self.leo_items [child_key] = child_item
    #@+node:ekr.20181113043131.1: *4* tree.redraw_from_dict & helper
    def redraw_from_dict(self, d):
        '''
        Create LeoTreeItems from all items in the redraw_dict.
        The tree has already been cleared.
        '''
        # print('==== tree.redraw_from_dict')
        self.leo_selected_ap = d ['c.p']
            # Usually set in on_selected_event.
        for item in d ['items']:
            self.create_item_with_parent(item, self.tree)
           
    def create_item_with_parent(self, item, parent):
        '''Create a tree item for item and all its visible children.'''
        with parent:
            ap = item ['ap']
            headline = ap ['headline']
            # Create the tree item.
            tree_item = LeoFlexxTreeItem(ap, text=headline, checked=None, collapsed=True)
            key = self.ap_to_key(ap)
            self.leo_items [key] = tree_item
            # Create the item's children...
            for child in item ['children']:
                self.create_item_with_parent(child, tree_item)
    #@+node:ekr.20181108232118.1: *4* tree.show_event
    def show_event(self, ev):
        '''Put a description of the event to the log.'''
        w = self.root.main_window
        id_ = ev.source.title or ev.source.text
        kind = '' if ev.new_value else 'un-'
        s = kind + ev.type
        message = '%s: %s' % (s.rjust(15), id_)
        w.log.put(message)
        if debug and debug_tree:
            print('tree.show_event: ' + message)
    #@-others
#@+node:ekr.20181108233657.1: *3* class LeoFlexxTreeItem
class LeoFlexxTreeItem(flx.TreeItem):
    
    def init(self, leo_ap):
        # pylint: disable=arguments-differ
        self.leo_ap = leo_ap
#@-others
if __name__ == '__main__':
    flx.launch(LeoApp)
    flx.logger.info('LeoApp: after flx.launch')
    if not debug:
        suppress_unwanted_log_messages()
    flx.run()
#@-leo

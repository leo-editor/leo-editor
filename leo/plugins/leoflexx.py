# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20181103094900.1: * @file leoflexx.py
#@@first
#@@language python
#@@tabwidth -4
'''
A stand-alone prototype for Leo using flexx.
'''
# pylint: disable=logging-not-lazy
#@+<< leoflexx imports >>
#@+node:ekr.20181113041314.1: ** << leoflexx imports >>
import leo.core.leoGlobals as g
    # **Note**: JS code can not use g.trace, g.callers.
import leo.core.leoBridge as leoBridge
import leo.core.leoFrame as leoFrame
import leo.core.leoGui as leoGui
import leo.core.leoMenu as leoMenu
import leo.core.leoNodes as leoNodes
import leo.core.leoTest as leoTest
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
debug_focus = True # puts 'focus' in g.app.debug.
debug_keys = True # puts 'keys' in g.app.debug.
debug_tree = True
tree_props = False
warnings_only = True
#@+others
#@+node:ekr.20181121040901.1: **  top-level functions
#@+node:ekr.20181122102523.1: *3* banner
def banner(s):
    '''Print s so it stands out.'''
    if g.unitTesting:
        return
    if debug_focus or debug_keys or debug_tree:
        print('')
        print(s)
        print('')
#@+node:ekr.20181121091633.1: *3* dump_event
def dump_event (ev):
    '''Print a description of the event.'''
    id_ = ev.source.title or ev.source.text
    kind = '' if ev.new_value else 'un-'
    s = kind + ev.type
    message = '%s: %s' % (s.rjust(15), id_)
    print('dump_event: ' + message)
#@+node:ekr.20181103151350.1: *3* init
def init():
    # At present, leoflexx is not a true plugin.
    # I am executing leoflexx.py from an external script.
    return False
#@+node:ekr.20181121040857.1: *3* get_root
def get_root():
    '''
    Return the LeoBrowserApp instance.
    
    This is the same as self.root for any flx.Component.
    '''
    root = flx.loop.get_active_component().root
        # Only called at startup, so this will never be None.
    assert isinstance(root, LeoBrowserApp), repr(root)
    return root
#@+node:ekr.20181113041410.1: *3* suppress_unwanted_log_messages
def suppress_unwanted_log_messages():
    '''
    Suppress the "Automatically scrolling cursor into view" messages by
    *allowing* only important messages.
    '''
    allowed = r'(Traceback|Critical|Error|Leo|Session|Starting|Stopping|Warning)'
    pattern = re.compile(allowed, re.IGNORECASE)
    flx.set_log_level('INFO', pattern)
#@+node:ekr.20181107052522.1: ** class LeoBrowserApp
# pscript never converts flx.PyComponents to JS.

class LeoBrowserApp(flx.PyComponent):
    '''
    The browser component of Leo in the browser.
    This is self.root for all flx.Widget objects!
    This is *not* g.app. The LeoBride defines g.app.
    '''

    main_window = flx.ComponentProp(settable=True)

    def init(self):
        c, g = self.open_bridge()
        self.c = c
        self.gui = gui = LeoBrowserGui()
        assert gui.guiName() == 'browser'
            # Important: the leoTest module special cases this name.
        # Inject the newly-created gui into g.app.
        g.app.gui = gui
        if debug_focus:
            g.app.debug.append('focus')
        if debug_keys:
            g.app.debug.append('keys')
        title = c.computeWindowTitle(c.mFileName)
        c.frame = gui.lastFrame = LeoBrowserFrame(c, title, gui)
            # Instantiate all wrappers first.
        # Force minibuffer find mode.
        c.findCommands.minibuffer_mode = True
        # Create all data-related ivars.
        self.create_all_data()
        # Create the main window and all its components.
        c.selectPosition(c.rootPosition()) ### A temp hack.
        assert c.p, repr(c.b)
        p = c.p
        g.trace('app.init: c.p.h:', p.h)
        signon = '%s\n%s' % (g.app.signon, g.app.signon2)
        status_lt, status_rt = c.frame.statusLine.update(p.b, 0)
        redraw_dict = self.make_redraw_dict()
        main_window = LeoFlexxMainWindow(p.b, redraw_dict, signon, status_lt, status_rt)
        self._mutate('main_window', main_window)

    #@+others
    #@+node:ekr.20181111152542.1: *3* app.actions
    #@+node:ekr.20181111142921.1: *4* app.action: do_command
    @flx.action
    def do_command(self, command):
        w = self.main_window
        c = self.c
        
        #@+others # define test_log & test_select.
        #@+node:ekr.20181119103144.1: *5* app.tests
        # def test_echo():
            # print('testing echo...')
            # self.gui.echo()
            # self.gui.tree_echo()

        def test_focus():
            old_debug = g.app.debug
            try:
                g.app.debug = ['focus', 'keys',]
                print('\ncalling c.set_focus(c.frame.miniBufferWidget.widget')
                c.set_focus(c.frame.miniBufferWidget.widget)
            finally:
                g.app.debug = old_debug

        def test_log():
            print('testing log...')
            w.log.put('Test message to LeoFlexxLog.put')
                # Test LeoFlexxLog.put.
            c.frame.log.put('Test message to LeoBrowserLog.put')
                # Test LeoBrowserLog.put.
                
        def test_positions():
            print('testing positions...')
            self.test_round_trip_positions()
                
        def test_redraw():
            print('testing redraw...')
            self.redraw()
                
        def test_select():
            print('testing select...')
            h = 'Active Unit Tests'
            p = g.findTopLevelNode(c, h, exact=True)
            if p:
                c.frame.tree.select(p)
                # LeoBrowserTree.select.
            else:
                g.trace('not found: %s' % h)
        #@-others

        if command == 'cls':
            g.cls()
        elif command == 'focus':
            test_focus()
        elif command == 'log':
            test_log()
        elif command == 'redraw':
            test_redraw()
        elif command.startswith('sel'):
            test_select()
        elif command == 'status':
            self.update_status_line()
        elif command == 'test': # All except unit tests.
            test_log()
            test_positions()
            test_redraw()
            test_select()
        elif command == 'unit':
            self.run_all_unit_tests()
        else:
            g.trace('unknown command: %r' % command)
            ### To do: pass the command on to Leo's core.
    #@+node:ekr.20181117163223.1: *4* app.action: do_key
    @flx.action
    def do_key (self, ev, kind):
        '''
        https://flexx.readthedocs.io/en/stable/ui/widget.html#flexx.ui.Widget.key_down
        See Widget._create_key_event in flexx/ui/_widget.py:
            
        Modifiers: 'Alt', 'Shift', 'Ctrl', 'Meta'
            
        Keys: 'Enter', 'Tab', 'Escape', 'Delete'
              'ArrowDown', 'ArrowLeft', 'ArrowRight', 'ArrowUp',
        '''
        # ev is a dict, keys are type, source, key, modifiers
        trace = False and debug_keys and not g.unitTesting
        c = self.c
        key, mods = ev ['key'], ev ['modifiers']
        d = {
            'ArrowDown':'Down',
            'ArrowLeft':'Left',
            'ArrowRight': 'Right',
            'ArrowUp': 'Up',
            'Enter': '\n', # For k.fullCommand, etc.
            'PageDown': 'Next',
            'PageUp': 'Prior',
        }
        char = d.get(key, key)
        if 'Ctrl' in mods:
            mods.remove('Ctrl')
            mods.append('Control')
        binding = '%s%s' % (''.join(['%s+' % (z) for z in mods]), char)
        widget = getattr(c.frame, kind)
        w = widget.wrapper
        key_event = leoGui.LeoKeyEvent(c,
            char = char, event = { 'c': c }, binding = binding, w = w)
        if trace:
            g.app.debug = ['keys',]
        try:
            old_debug = g.app.debug
            c.k.masterKeyHandler(key_event)
        finally:
            g.app.debug = old_debug
        if trace:
            g.trace('mods: %r key: %r ==> %r %r IN %6r %s' % (
                mods, key, char, binding, widget.wrapper.getName(), c.p.h))
    #@+node:ekr.20181116053210.1: *4* app.action: echo
    @flx.action
    def echo (self, message=None):
        print('===== echo =====', message or '<Empty Message>')
    #@+node:ekr.20181112165240.1: *4* app.action: info (deprecated)
    @flx.action
    def info (self, s):
        '''Send the string s to the flex logger, at level info.'''
        if not isinstance(s, str):
            s = repr(s)
        flx.logger.info('Leo: ' + s)
            # A hack: automatically add the "Leo" prefix so
            # the top-level suppression logic will not delete this message.
    #@+node:ekr.20181113042549.1: *4* app.action: redraw & helper
    def redraw (self):
        '''
        Send a **redraw list** to the tree.
        
        This is a recusive list lists of items (ap, gnx, headline) describing
        all and *only* the presently visible nodes in the tree.
        
        As a side effect, app.make_redraw_dict updates all internal dicts.
        '''
        # banner('===== app.redraw: %s' % g.callers())
        w = self.main_window
        # Be careful during startup.
        if w and w.tree:
            d = self.make_redraw_dict()
            w.tree.redraw_with_dict(d)
            ### w.tree.set_redraw_dict(d)
    #@+node:ekr.20181113043539.1: *5* app.make_redraw_dict & helpers
    def make_redraw_dict(self):
        '''
        Return a recursive, archivable, list of lists describing all the
        visible nodes of the tree.
        
        As a side effect, recreate gnx_to_vnode.
        '''
        c = self.c
        banner('app.make_redraw_dict: %s' % c.p.h)
        # Ensure that c.p will be shown.
        c.expandAllAncestors(c.p)
        return {
            'c.p': self.p_to_ap(c.p),
            'items': [
                self.make_dict_for_position(p)
                    for p in c.rootPosition().self_and_siblings()
            ],
        }
    #@+node:ekr.20181113044701.1: *6* app.make_dict_for_position
    def make_dict_for_position(self, p):
        ''' Recursively add a sublist for p and all its visible nodes.'''
        level = p.level()
        trace = True and level == 0 and not g.unitTesting
        c = self.c
        assert p.v
        self.gnx_to_vnode[p.v.gnx] = p.v
        if trace:
            print('%s%2s children %s' % (
                '  '*level, len(list(p.children())), p.h))
            if 0:
                for child in p.children():
                    level = child.level()
                    print('%s%3s: %s' % (' '*level, level, child.h))
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
    #@+node:ekr.20181111202747.1: *4* app.action: select_ap & helpers
    @flx.action
    def select_ap(self, ap):
        '''Select the position in Leo's core corresponding to the archived position.'''
        c, w = self.c, self.main_window
        p = self.ap_to_p(ap)
        c.frame.tree.super_select(p)
            # call LeoTree.select, but not self.select_p.
            # This hack prevents an unbounded recursion.
        w.body.set_body(p.v.b)
        self.update_status_line()
        self.send_children_to_tree(ap, p)
        # print('app.select_ap:', c.p.h)
    #@+node:ekr.20181111095640.1: *5* app.action: send_children_to_tree
    def send_children_to_tree(self, parent_ap, p):
        '''
        Call w.tree.receive_children(d), where d has the form:
            {
                'parent': parent_ap,
                'children': [ap1, ap2, ...],
            }
        '''
        w = self.main_window
        if p.hasChildren():
            w.tree.receive_children({
                'parent': parent_ap,
                'children': [self.p_to_ap(z) for z in p.children()],
            })
        elif debug_tree:
            # Not an error.
            print('app.send_children_to_tree: no children', p.h)
    #@+node:ekr.20181118061020.1: *4* app.action: select_p
    @flx.action
    def select_p(self, p):
        '''
        Select the position in the tree.
        
        Called from LeoBrowserTree.select, so do *not* call c.frame.tree.select.
        '''
        # print'app.select_p', p.h)
        w = self.main_window
        # Be careful during startup.
        if w and w.tree:
            ap = self.p_to_ap(p)
            w.tree.select_ap(ap)
    #@+node:ekr.20181118064309.1: *4* app.action: set_body
    @flx.action
    def set_body(self, s):
        w = self.main_window
        w.body.set_body(s)
    #@+node:ekr.20181119044723.1: *4* app.action: update_status_line
    @flx.action
    def update_status_line(self, body_text=None, insert_point=0):
        '''Update both fields of the status area.'''
        w = self.main_window
        c = self.c
        # Be careful during startup.
        if w and getattr(w, 'status_line', None):
            c.frame.statusLine.update(insert_point=insert_point)
    #@+node:ekr.20181111155525.1: *3* app.archived positions
    #@+node:ekr.20181111204659.1: *4* app.p_to_ap (updates app.gnx_to_vnode)
    def p_to_ap(self, p):
        '''
        Convert a true Leo position to a serializable archived position.
        '''
        if not p.v:
            banner('app.p_to_ap: no p.v: %r %s' % (p, g.callers()))
            assert False, g.callers()
        p_gnx = p.v.gnx
        if p_gnx not in self.gnx_to_vnode:
            print('=== update gnx_to_vnode',
                p_gnx.ljust(15),
                p.h,
                len(list(self.gnx_to_vnode.keys())),
            )
            self.gnx_to_vnode [p_gnx] = p.v
        return {
            'childIndex': p._childIndex,
            'cloned': p.isCloned(),
            'expanded': p.isExpanded(),
            'gnx': p.v.gnx,
            'headline': p.h,
            'marked': p.isMarked(),
            'stack': [{
                'gnx': stack_v.gnx,
                'childIndex': stack_childIndex,
                'headline': stack_v.h,
            } for (stack_v, stack_childIndex) in p.stack ],
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
    #@+node:ekr.20181113180246.1: *4* app.test_round_trip_positions
    def test_round_trip_positions(self):
        '''Test the round tripping of p_to_ap and ap_to_p.'''
        c = self.c
        # Bug fix: p_to_ap updates app.gnx_to_vnode. Save and restore it.
        old_d = self.gnx_to_vnode.copy()
        old_len = len(list(self.gnx_to_vnode.keys()))
        # t1 = time.clock()
        for p in c.all_positions():
            ap = self.p_to_ap(p)
            p2 = self.ap_to_p(ap)
            assert p == p2, (repr(p), repr(p2), repr(ap))
        self.gnx_to_vnode = old_d
        new_len = len(list(self.gnx_to_vnode.keys()))
        assert old_len == new_len, (old_len, new_len)
        # print('app.test_round_trip_positions: %5.3f sec' % (time.clock()-t1))
    #@+node:ekr.20181114015356.1: *3* app.create_all_data
    def create_all_data(self):
        '''Compute the initial values all data structures.'''
        t1 = time.clock()
        # This is likely the only data that ever will be needed.
        self.gnx_to_vnode = { v.gnx: v for v in self.c.all_unique_nodes() }
        t2 = time.clock()
        if debug_tree:
            print('app.create_all_data: %5.2f sec. %s entries' % (
                (t2-t1), len(list(self.gnx_to_vnode.keys()))))
        if debug_tree:
            self.test_round_trip_positions()
    #@+node:ekr.20181115171220.1: *3* app.message
    def message(self, s):
        '''For testing.'''
        print('app.message: %s' % s)
    #@+node:ekr.20181105091545.1: *3* app.open_bridge
    def open_bridge(self):
        '''Can't be in JS.'''
        bridge = leoBridge.controller(gui = None,
            loadPlugins = False,
            readSettings = True, # Required to get bindings!
            silent = False,
            tracePlugins = False,
            verbose = False, # True: prints log messages.
        )
        if not bridge.isOpen():
            flx.logger.error('Error opening leoBridge')
            return
        g = bridge.globals()
        path = g.os_path_finalize_join(g.app.loadDir, '..', 'test', 'unitTest.leo')
        if not g.os_path_exists(path):
            flx.logger.error('open_bridge: does not exist: %r' % path)
            return
        c = bridge.openLeoFile(path)
        return c, g
    #@+node:ekr.20181112182636.1: *3* app.run_all_unit_tests
    def run_all_unit_tests (self):
        '''Run all unit tests from the bridge.'''
        c = self.c
        h = 'Active Unit Tests'
        p = g.findTopLevelNode(c, h, exact=True)
        if p:
            try:
                old_debug = g.app.debug
                g.app.failFast = False
                g.app.debug = [] # ['focus', 'keys',]
                c.frame.tree.select(p)
                tm = BrowserTestManager(c)
                # Run selected tests locallyk.
                tm.doTests(all=False, marked=False)
            finally:
                g.app.debug = old_debug
        else:
            print('do_command: select: not found: %s' % h)
    #@-others
#@+node:ekr.20181115071559.1: ** Py side: wrapper classes
#@+node:ekr.20181115092337.3: *3* class LeoBrowserBody
class LeoBrowserBody(leoFrame.NullBody):
   
    def __init__(self, frame):
        super().__init__(frame, parentFrame=None)
        self.c = frame.c
        assert self.c
        self.root = get_root()
        self.widget = self.wrapper
        #
        # Monkey-patch self.wrapper, a StringTextWrapper.
        assert isinstance(self.wrapper, leoFrame.StringTextWrapper)
        assert self.wrapper.getName().startswith('body')
        self.wrapper.setFocus = self.setFocus
        
    #@+others
    #@+node:ekr.20181120062831.1: *4* body_wrapper.setFocus
    def setFocus(self):
        w = self.root.main_window
        # g.trace('(body wrapper)')
        w.body.set_focus()
    #@+node:ekr.20181120063244.1: *4* body_wrapper.onBodyChanged
    def onBodyChanged(self, *args, **keys):
        # pylint: disable=arguments-differ
        c = self.c
        g.trace('body-wrapper', c.p.h)
        ### These can destroy the body text.
            # super().onBodyChanged(*args, **keys)
            # self.root.set_body(c.p.b)
    #@-others
#@+node:ekr.20181115092337.6: *3* class LeoBrowserFrame
class LeoBrowserFrame(leoFrame.NullFrame):
    
    def __init__(self, c, title, gui):
        '''Ctor for the LeoBrowserFrame class.'''
        super().__init__(c, title, gui)
        assert self.c == c
        frame = self
        self.root = get_root()
        self.body = LeoBrowserBody(frame)
        self.tree = LeoBrowserTree(frame)
        self.log = LeoBrowserLog(frame)
        self.menu = LeoBrowserMenu(frame)
        self.miniBufferWidget = LeoBrowserMinibuffer(c, frame)
        self.iconBar = LeoBrowserIconBar(c, frame)
        self.statusLine = LeoBrowserStatusLine(c, frame)
            # NullFrame does this in createStatusLine.
        self.top = TracingNullObject() ### if debug else g.NullObject()
            # Use the TracingNullObject class for better tracing.
        
    def finishCreate(self):
        '''Override NullFrame.finishCreate.'''
        pass # Do not call self.createFirstTreeNode.

    #@+others
    #@-others
#@+node:ekr.20181113041113.1: *3* class LeoBrowserGui
class LeoBrowserGui(leoGui.NullGui):

    def __init__ (self, guiName='nullGui'):
        super().__init__(guiName='browser')
            # leoTest.doTest special-cases the name "browser".
        self.root = get_root()
        
    def insertKeyEvent(self, event, i):
        '''Insert the key given by event in location i of widget event.w.'''
        # Mysterious...
        assert False, g.callers()

    #@+others
    #@+node:ekr.20181119141542.1: *4* gui.isTextWrapper
    def isTextWrapper(self, w):
        '''Return True if w is supposedly a text widget.'''
        name = w.getName() if hasattr(w, 'getName') else None
        return name in ('body', 'log', 'minibuffer') or name.startswith('head')
    #@+node:ekr.20181119153936.1: *4* gui.focus...
    def get_focus(self, *args, **kwargs):
        ### g.trace('(gui)', repr(self.focusWidget), g.callers())
        return self.focusWidget

    def set_focus(self, commander, widget):
        self.focusWidget = widget
        if isinstance(widget, (LeoBrowserMinibuffer, leoFrame.StringTextWrapper)):
            # g.trace('(gui):', repr(widget))
            if not g.unitTesting:
                widget.setFocus()
        else:
            g.trace('(gui): unknown widget', repr(widget))
    #@-others
#@+node:ekr.20181115092337.21: *3* class LeoBrowserIconBar
class LeoBrowserIconBar(leoFrame.NullIconBarClass):

    def __init__(self, c, parentFrame):
        super().__init__(c, parentFrame)
        assert self.c == c
        self.root = get_root()
            
    #@+others
    #@-others
#@+node:ekr.20181115092337.22: *3* class LeoBrowserLog
class LeoBrowserLog(leoFrame.NullLog):
    
    def __init__(self, frame, parentFrame=None):
        super().__init__(frame, parentFrame)
        self.root = get_root()
        assert isinstance(self.widget, leoFrame.StringTextWrapper)
        self.logCtrl = self.widget
        self.wrapper = self.widget
        #
        # Monkey-patch self.wrapper, a StringTextWrapper.
        assert self.wrapper.getName().startswith('log')
        self.wrapper.setFocus = self.setFocus
        
    def getName(self):
        return 'log' # Required for proper pane bindings.

    #@+others
    #@+node:ekr.20181120063043.1: *4* log_wrapper.setFocus
    def setFocus(self):
        w = self.root.main_window
        # g.trace('(log wrapper)')
        w.log.set_focus()
    #@+node:ekr.20181120063111.1: *4* log_wrapper.put & putnl
    def put(self, s, color=None, tabName='Log', from_redirect=False, nodeLink=None):
        self.root.main_window.log.put(s)

    def putnl(self, tabName='Log'):
        self.root.main_window.log.put('')
    #@-others
#@+node:ekr.20181115092337.31: *3* class LeoBrowserMenu
class LeoBrowserMenu(leoMenu.NullMenu):
    '''Browser wrapper for menus.'''

    # def __init__(self, frame):
        # super().__init__(frame)
        # self.root = get_root()

    # @others
#@+node:ekr.20181115120317.1: *3* class LeoBrowserMinibuffer (StringTextWrapper)
# Leo's core doesn't define a NullMinibuffer class.

class LeoBrowserMinibuffer (leoFrame.StringTextWrapper):
    '''Browser wrapper for minibuffer.'''
    
    def __init__(self, c, frame):
        super().__init__(c, name='minibuffer')
            # Name must be minibuffer, for gui.isTextWrapper().
        assert self.c == c, repr(self.c)
        assert self.widget is None, repr(self.widget)
        assert self.getName() == 'minibuffer'
        self.frame = frame
        self.root = get_root()
        self.widget = self
        self.wrapper = self
        # Hook this class up to the key handler.
        c.k.w = self
    
    # Overrides.
    def setFocus(self):
        g.trace('===== (minibuffer wrapper)')
        self.root.main_window.minibuffer.set_focus()
        
    #@+others
    #@-others
#@+node:ekr.20181115092337.32: *3* class LeoBrowserStatusLine
class LeoBrowserStatusLine(leoFrame.NullStatusLineClass):
    
    def __init__(self, c, parentFrame):
        super().__init__(c, parentFrame)
        self.root = get_root()
        self.w = self # Required.
        
    #@+others
    #@+node:ekr.20181119045430.1: *4* status_line_wrapper.clear & get
    def clear(self):
        pass
        
    def get(self):
        g.trace('(LeoBrowserStatusLine): NOT READY')
        return ''
    #@+node:ekr.20181119045343.1: *4* status_line_wrapper.put and put1
    def put(self, s, bg=None, fg=None):
        w = self.root.main_window
        # Be careful during startup.
        if w and w.status_line:
            w.status_line.put(s, bg, fg)

    def put1(self, s, bg=None, fg=None):
        w = self.root.main_window
        # Be careful during startup.
        if w and w.status_line:
            w.status_line.put2(s, bg, fg)
    #@+node:ekr.20181119154422.1: *4* status_line_wrapper.setFocus
    def setFocus(self):
        # g.trace('(status_line)', g.callers())
        self.root.status_line.set_focus()
    #@+node:ekr.20181119042937.1: *4* status_line_wrapper.update
    def update(self, body_text='', insert_point=0):
        '''
        Update the status line, based on the contents of the body.
        
        Called from LeoTree.select, and should also be called from the JS side.
        
        Returns (lt_part, rt_part) for LeoBrowserApp.init.
        '''
        # pylint: disable=arguments-differ
        if g.app.killed:
            return
        c, p = self.c, self.c.p
        if not p:
            return
        # Calculate lt_part
        row, col = g.convertPythonIndexToRowCol(body_text, insert_point)
        fcol = c.gotoCommands.find_node_start(p)
        lt_part = "line: %2d col: %2d fcol: %s" % (row, col, fcol or '')
        # Calculate rt_part.
        headlines = [v.h for (v, childIndex) in p.stack] + [p.h]
        rt_part = '%s#%s' % (g.shortFileName(c.fileName()), '->'.join(headlines))
        # Update the status area.
        self.put(lt_part)
        self.put1(rt_part)
        return lt_part, rt_part
    #@-others
#@+node:ekr.20181115092337.57: *3* class LeoBrowserTree
class LeoBrowserTree(leoFrame.NullTree):
    
    def __init__(self, frame):
        super().__init__(frame)
        self.root = get_root()
        self.widget = self
        self.wrapper = self
        ###
            # # pylint: disable=no-member
                # # The point is that there isn't a member ;-)
            # assert not hasattr(self, 'widget'), repr(self.widget)
            # assert not hasattr(self, 'wrapper'), repr(self.wrapper)

    def getName(self):
        return 'canvas(tree)' # Required for proper pane bindings.

    #@+others
    #@+node:ekr.20181116081421.1: *4* tree_wrapper.select & super_select
    def select(self, p):
        '''Override NullTree.select, which is actually LeoTree.select.'''
        super().select(p)
            # Call LeoTree.select.'''
        self.root.select_p(p)
            # Call app.select_position.

    def super_select(self, p):
        '''Call only LeoTree.select.'''
        super().select(p)
    #@+node:ekr.20181118052203.1: *4* tree_wrapper.redraw
    def redraw(self, p=None):
        ### print('===== browser-tree.redraw', p.h, g.callers())
        self.root.redraw()
    #@+node:ekr.20181120063844.1: *4* tree_wrapper.setFocus
    def setFocus(self):
        w = self.root.main_window
        # g.trace('(tree wrapper)', g.callers())
        w.tree.set_focus()
    #@-others
#@+node:ekr.20181119094122.1: *3* class TracingNullObject
#@@nobeautify

class TracingNullObject(object):
    '''A tracing version of g.NullObject.'''
    def __init__(self, *args, **keys):
        pass

    def __call__(self, *args, **keys):
        return self

    def __repr__(self):
        return "NullObject"

    def __str__(self):
        return "NullObject"

    def __bool__(self):
        return False

    def __delattr__(self, attr):
        banner('NullObject.__delattr__ %r %s' % (attr, g.callers()))
        return self

    def __getattr__(self, attr):
        banner('NullObject.__getattr__ %r %s' % (attr, g.callers()))
        return self

    def __setattr__(self, attr, val):
        banner('NullObject.__setattr__ %r %s' % (attr, g.callers()))
        return self
#@+node:ekr.20181107052700.1: ** Js side: flx.Widgets
#@+node:ekr.20181104082144.1: *3* class LeoFlexxBody

class LeoFlexxBody(flx.Widget):
    '''A CodeEditor widget based on Ace.'''

    #@+<< body css >>
    #@+node:ekr.20181120055046.1: *4* << body css >>
    CSS = """
    .flx-CodeEditor > .ace {
        width: 100%;
        height: 100%;
    }
    """
    #@-<< body css >>

    def init(self, body):
        # pylint: disable=arguments-differ
        # pylint: disable=undefined-variable
            # window
        global window
        self.ace = window.ace.edit(self.node, "body editor")
        self.ace.navigateFileEnd()  # otherwise all lines highlighted
        self.ace.setTheme("ace/theme/solarized_dark")
        self.ace.getSession().setMode("ace/mode/python")
        self.set_body(body)
        
    @flx.reaction('size')
    def __on_size(self, *events):
        self.ace.resize()

    #@+others
    #@+node:ekr.20181121072246.1: *4* flx_body.key_press
    @flx.emitter
    def key_press(self, e):
        ev = self._create_key_event(e)
        # print('===== body.key_down.emitter', repr(ev))
        if ev ['modifiers']:
            e.preventDefault()
        return ev

    @flx.reaction('key_press')
    def on_key_press(self, *events):
        for ev in events:
            self.root.do_key(ev, 'body')
    #@+node:ekr.20181120054826.1: *4* flx_body.set_body & set_focus
    @flx.action
    def set_body(self, body):
        self.ace.setValue(body)
        self.root.update_status_line(body_text=body, insert_point=0)
        
    @flx.action
    def set_focus(self):
        print('===== flx.body.set_focus')
        self.ace.focus()
    #@-others
#@+node:ekr.20181104082149.1: *3* class LeoFlexxLog
class LeoFlexxLog(flx.Widget):
    
    #@+<< log css >>
    #@+node:ekr.20181120060336.1: *4* << log css >>
    CSS = """
    .flx-CodeEditor > .ace {
        width: 100%;
        height: 100%;
    }
    """
    #@-<< log css >>

    def init(self, signon):
        # pylint: disable=arguments-differ
        # pylint: disable=undefined-variable
            # window
        global window
        self.ace = window.ace.edit(self.node, "log editor")
        self.ace.navigateFileEnd()  # otherwise all lines highlighted
        self.ace.setTheme("ace/theme/solarized_dark")
        self.ace.setValue(signon)
        
    @flx.reaction('size')
    def __on_size(self, *events):
        self.ace.resize()

    #@+others
    #@+node:ekr.20181121071956.1: *4* flx.log.key_press
    # Emitters can have any number of arguments.
    # should return a dictionary, which will get emitted as an event,
    # with the event type matching the name of the emitter.

    @flx.emitter
    def key_press(self, e):
        """Overload key_press emitter to override browser commands."""
        ev = self._create_key_event(e)
        mods = ev ['modifiers']
        # print('===== log.key_down.emitter', repr(ev))
        if mods:
            e.preventDefault()
        return ev

    @flx.reaction('key_press')
    def on_key_press(self, *events):
        for ev in events:
            self.root.do_key(ev, 'log')
    #@+node:ekr.20181120060348.1: *4* flx.log.put & set_focus
    @flx.action
    def put(self, s):
        self.ace.setValue(self.ace.getValue() + '\n' + s)
        
    @flx.action
    def set_focus(self):
        # print('===== flx.log.set_focus')
        self.ace.focus()
    #@-others
        
#@+node:ekr.20181104082130.1: *3* class LeoFlexxMainWindow
class LeoFlexxMainWindow(flx.Widget):
    
    '''
    Leo's main window, that is, root.main_window.
    
    Each property is accessible as root.main_window.x.
    '''
    body = flx.ComponentProp(settable=True)
    log = flx.ComponentProp(settable=True)
    minibuffer = flx.ComponentProp(settable=True)
    status_line = flx.ComponentProp(settable=True)
    tree = flx.ComponentProp(settable=True)

    def init(self, body_s, data, signon, status_lt, status_rt):
        # pylint: disable=arguments-differ
        ### with flx.TabLayout():
        with flx.VSplit():
            with flx.HSplit(flex=1):
                tree = LeoFlexxTree(data, flex=1)
                log = LeoFlexxLog(signon, flex=1)
            body = LeoFlexxBody(body_s, flex=1)
            minibuffer = LeoFlexxMiniBuffer()
            status_line = LeoFlexxStatusLine(status_lt, status_rt)
        self._mutate('body', body)
        self._mutate('log', log)
        self._mutate('minibuffer', minibuffer)
        self._mutate('status_line', status_line)
        self._mutate('tree', tree)

    #@+others
    #@+node:ekr.20181120060557.1: *4* MainWindow.key_press
    @flx.emitter
    def key_press(self, e):
        ev = self._create_key_event(e)
        ### print('===== main.key_down.emitter', repr(ev))
        if ev ['modifiers']:
            e.preventDefault()
        return ev
    #@-others
#@+node:ekr.20181104082154.1: *3* class LeoFlexxMiniBuffer
class LeoFlexxMiniBuffer(flx.Widget):

    def init(self): 
        with flx.HBox():
            flx.Label(text='Minibuffer')
            self.widget = flx.LineEdit(flex=1, placeholder_text='Enter command')
        self.widget.apply_style('background: yellow')

    #@+others
    #@+node:ekr.20181120060856.1: *4* flx_minibuffer.key_press
    @flx.emitter
    def key_press(self, e):
        ev = self._create_key_event(e)
        ### print('===== minibuffer.key_down.emitter', repr(ev))
        if ev ['modifiers']:
            e.preventDefault()
        return ev
    #@+node:ekr.20181120060827.1: *4* flx_minibuffer.set_focus & set_text
    @flx.action
    def set_focus(self):
        print('flx.minibuffer.set_focus', repr(self.widget))
        # https://flexx.readthedocs.io/en/stable/ui/widget.html#flexx.ui.Widget.pointer_click
        # See also: Widget._create_pointer_event.
        e = {
            'button': 0,
            'buttons': [],
            'modifiers': [],
            'page_pos': (0.0, 0.0),
            'pos': (0.0, 0.0),
            'touches': {-1: 1},
        }
        if 0: # Crashes.
            self.widget.pointer_click(e)
        else: # Doesn't work.
            self.widget.emit('pointer_click', e)

    @flx.action
    def set_text(self, s):
        print('flx.minibuffer.set_text')
        self.widget.set_text(s)
    #@+node:ekr.20181120060849.1: *4* flx_minibuffer.on_user_done
    @flx.reaction('widget.user_done')
    def on_user_done(self, *events):
        # print('flx.minibuffer: on_user_done')
        for ev in events:
            command = self.widget.text
            if command.strip():
                self.widget.set_text('')
                self.root.do_command(command)
    #@-others
#@+node:ekr.20181104082201.1: *3* class LeoFlexxStatusLine
class LeoFlexxStatusLine(flx.Widget):
    
    def init(self, status_lt, status_rt):
        # pylint: disable=arguments-differ
        with flx.HBox():
            flx.Label(text='Status Line')
            self.widget = flx.LineEdit(flex=1)
            self.widget2 = flx.LineEdit(flex=1)
        self.widget.set_text(status_lt)
        self.widget2.set_text(status_rt)
        self.widget.apply_style('background: green')
        self.widget2.apply_style('background: green')
        
    #@+others
    #@+node:ekr.20181120060957.1: *4* flx_status_line.put & put2
    @flx.action
    def put(self, s, bg, fg):
        self.widget.set_text(s)
        
    @flx.action
    def put2(self, s, bg, fg):
        self.widget2.set_text(s)
    #@+node:ekr.20181120060950.1: *4* flx_status_line.key_press
    @flx.emitter
    def key_press(self, e):
        ev = self._create_key_event(e)
        ### print('===== status line.key_down.emitter', repr(ev))
        if ev ['modifiers']:
            e.preventDefault()
        return ev

    #@-others
#@+node:ekr.20181104082138.1: *3* class LeoFlexxTree
class LeoFlexxTree(flx.Widget):
    
    #@+<< tree css >>
    #@+node:ekr.20181120061118.1: *4*  << tree css >>

    CSS = '''
    .flx-TreeWidget {
        background: #000;
        color: white;
        /* background: #ffffec; */
        /* Leo Yellow */
        /* color: #afa; */
    }
    '''
    #@-<< tree css >>
    
    if tree_props:
        redraw_dict = flx.DictProp(settable=True)

    def init(self, redraw_dict):
        # pylint: disable=arguments-differ
        self.widget = self
        self.wrapper = self
        # Init the data.
        self.leo_gnx_dict = {}
            # Keys are gnx's, values are previously-created LeoTreeItems for that gnx.
        self.leo_items = {}
            # Keys are ap **keys**, values are LeoTreeItems.
        self.leo_populated_dict = {}
            # Keys are ap **keys**, values are ap's.
        self.leo_selected_ap = None
        # Init the widget.
        self.tree = flx.TreeWidget(flex=1, max_selected=1)
        if tree_props:
            self._mutate('redraw_dict', redraw_dict)
        else:
            self.redraw_with_dict(redraw_dict)

    #@+others
    #@+node:ekr.20181114072307.1: *4* flx_tree.ap_to_key
    def ap_to_key(self, ap):
        '''Produce a key for the given ap.'''
        childIndex = ap ['childIndex']
        gnx = ap ['gnx']
        headline = ap ['headline']
        stack = ap ['stack']
        stack_s = '::'.join([
            'childIndex: %s, gnx: %s' % (z ['childIndex'], z ['gnx'])
                for z in stack
        ])
        key = 'Tree key<childIndex: %s, gnx: %s, %s <stack: %s>>' % (
            childIndex, gnx, headline, stack_s or '[]')
        if False and key not in self.leo_populated_dict:
            banner('flx.tree.ap_to_key: new key: %s %s' % (key, ap ['headline']))
        return key
    #@+node:ekr.20181121073246.1: *4* flx_tree.drawing
    #@+node:ekr.20181112163252.1: *5* flx_tree.clear_tree
    @flx.action
    def clear_tree(self):
        '''
        Completely clear the tree, preparing to recreate it.
        
        Important: we do *not* clear self.tree itself!
        '''
        # pylint: disable=access-member-before-definition
        # banner('flx.tree.clear_tree: dispose of %s items' % len(self.leo_items.keys()))
        # Clear all tree items.
        for item in self.leo_items.values():
            # print('flx.tree.clear_tree: dispose: %r' % item)
            item.dispose()
        #
        # Clear all internal data structures.
        self.leo_gnx_dict = {}
        self.leo_items = {}
        self.leo_populated_dict = {}
    #@+node:ekr.20181122072344.1: *5* flx_tree.create_item_for_ap
    def create_item_for_ap(self, ap, parent):
        '''Create or reuse a tree items (for already-created clones).'''
        cloned, gnx, headline = ap ['cloned'], ap ['gnx'], ap ['headline']
        key = self.ap_to_key(ap)
        old_item = self.leo_gnx_dict.get(gnx)
        if old_item and cloned:
            banner('create_item_for_ap: CLONE: %s %s' % (gnx, headline))
            assert key in self.leo_items, repr(key)
            return None
        # banner('flx.tree.create_item_for_ap:\nap: %r\nparent: %r' % (ap, parent))
        with parent:
            item = LeoFlexxTreeItem(ap, text=headline, checked=None, collapsed=True)
        # banner('flx.tree.create_item_for_ap: item: %r' % (item))
        self.leo_items [key] = item
        self.leo_gnx_dict [gnx] = item
        return item
    #@+node:ekr.20181113085722.1: *5* flx_tree.dump_ap
    def dump_ap (self, ap, padding, tag):
        '''Print an archived position fully.'''
        stack = ap ['stack']
        if not padding:
            padding = ''
        padding = padding + ' '*4 
        if stack:
            print('%s%s:...' % (padding, tag or 'ap'))
            padding = padding + ' '*4
            print('%schildIndex: %s v: %s %s stack: [' % (
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
            padding = padding [:-4]
            print(']')
        else:
            print('%s%s: childIndex: %s v: %s stack: [] %s' % (
                padding, tag or 'ap',
                str(ap ['childIndex']).ljust(3),
                ap['gnx'],
                ap['headline'],
            ))
    #@+node:ekr.20181110175222.1: *5* flx_tree.receive_children & populate_children
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
        # banner('flx.tree.receive_children: %s' % len(children))
        if children:
            self.populate_children(children, parent_ap)
    #@+node:ekr.20181111011928.1: *6* flx_tree.populate_children
    def populate_children(self, children, parent_ap):
        '''Populate parent with the children if necessary.'''
        parent_key = self.ap_to_key(parent_ap)
        if parent_key in self.leo_populated_dict:
            # banner('tree.populate_children: already populated: %s' % (parent_ap ['headline']))
            return
        #
        # Set the key once, here.
        self.leo_populated_dict [parent_key] = parent_ap
        #
        # Populate the items.
        if parent_key not in self.leo_items:
            banner('flx.tree.populate_children: can not happen')
            self.dump_ap(parent_ap, 0, 'parent_ap')
            for item in self.leo_items:
                print(repr(item))
            return
        # banner('flx.tree.populate_children: %s' % len(children))
        if 0:
            print('parent_ap', repr(parent_ap))
            parent_key = self.ap_to_key(parent_ap)
            print('parent item:', repr(self.leo_items[parent_key]))
        # Create the items.
        parent = self.leo_items[parent_key]
        for child_ap in children:
            self.create_item_for_ap(child_ap, parent)
        
    #@+node:ekr.20181113043004.1: *5* flx_tree.redraw_with_dict & helper
    @flx.action
    def redraw_with_dict(self, d):
        '''Clear the present tree and redraw using the redraw_list.'''
        self.clear_tree()
        # banner('flx.tree.redraw_with_dict: %s items: %s' % (d ['c.p']['headline'], len(d ['items'])))
        self.leo_selected_ap = d ['c.p']
        for item in d ['items']:
            self.create_item_with_parent(item, self.tree)
    #@+node:ekr.20181113043131.1: *6* flx_tree.create_item_with_parent
    def create_item_with_parent(self, item, parent):
        '''Create a tree item for item and all its visible children.'''
        ap = item ['ap']
        item = self.create_item_for_ap(ap, parent)
        if item:
            # Not a clone: Create the item's children...
            for child in item ['children']:
                self.create_item_with_parent(child, item)
    #@+node:ekr.20181120061140.1: *4* flx_tree.key_press
    @flx.emitter
    def key_press(self, e):
        ev = self._create_key_event(e)
        ### print('===== tree.key_down.emitter', repr(ev))
        if ev ['modifiers']:
            e.preventDefault()
        return ev
    #@+node:ekr.20181122114509.1: *4* flx_tree.properties
    if tree_props:

        @flx.action
        def set_redraw_dict(self, d):
            print('===== set_redraw_dict', repr(d.keys()))
            self._mutate('redraw_dict', d)
            
        @flx.reaction('redraw_dict')
        def on_change_redraw_dict(self):
            print('===== on_change_redraw_dict', len(self.redraw_dict ['items']))
            self.redraw_with_dict(self.redraw_dict)
    #@+node:ekr.20181112172518.1: *4* flx_tree.reactions
    #@+node:ekr.20181116172300.1: *5* flx_tree.reaction: on_key_press
    @flx.reaction('tree.key_press')
    def on_key_press(self, *events):
        for ev in events:
            self.root.do_key(ev, 'tree')
    #@+node:ekr.20181104080854.3: *5* flx_tree.reaction: on_tree_event
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
    #@+node:ekr.20181121195235.1: *4* flx_tree.selecting
    #@+node:ekr.20181116083916.1: *5* flx_tree.select_ap
    @flx.action
    def select_ap(self, ap):
        '''Select the tree item corresponding to the given ap.'''
        if ap == self.leo_selected_ap:
            # banner('tree.select_ap: already selected')
            # self.dump_ap(ap, 0, 'select_ap')
            return
        new_key = self.ap_to_key(ap)
        new_item = self.leo_items.get(new_key)
        if new_item:
            # banner('tree.select_ap: select: %r:' %  new_item)
            new_item.set_selected(True)
            self.leo_selected_ap = ap
            return
        #
        # This is a serious error.
        banner('===== ERROR ===== tree.select_ap: no item for ap: %r' % (ap))
        ### Leave the selection alone?
        ### self.leo_selected_ap = None
    #@+node:ekr.20181109083659.1: *5* flx_tree.reaction: on_selected_event
    @flx.reaction('tree.children**.selected')
    def on_selected_event(self, *events):
        '''
        Update the tree and body text when the user selects a new tree node.
        '''
        trace = False and not g.unitTesting
        if trace: banner('tree.on_selected_event')
        for ev in events:
            if not ev.new_value:
                # We are deselecting a node.
                if trace: print('tree.on_selected_event: IGNORE 1')
                ### e.preventDefault()
                continue
            ap = ev.source.leo_ap
                # Get the ap from the LeoTreeItem.
            if 1:
                # Just select the node!
                self.root.select_ap(ap)
            else:
                # Try to get fancy.
                if trace:
                    print('----- ev.source.leo_ap\n', repr(ap))
                    print('------ leo_selected_ap\n', repr(self.leo_selected_ap))
                if ap == self.leo_selected_ap:
                    if trace: print('tree.on_selected_event: IGNORE 2')
                    ### ev.preventDefault()
                else:
                    if trace: print('tree.on_selected_event: SELECT')
                    self.root.select_ap(ap)
    #@+node:ekr.20181120063735.1: *4* flx_tree.set_focus
    @flx.action
    def set_focus(self):
        print('===== flx.tree.set_focus')
    #@+node:ekr.20181108232118.1: *4* flx_tree.show_event
    def show_event(self, ev):
        '''Put a description of the event to the log.'''
        w = self.root.main_window
        id_ = ev.source.title or ev.source.text
        kind = '' if ev.new_value else 'un-'
        s = kind + ev.type
        message = '%s: %s' % (s.rjust(15), id_)
        w.log.put(message)
        if 0: ###
            print('tree.show_event: ' + message)
    #@-others
#@+node:ekr.20181108233657.1: *3* class LeoFlexxTreeItem
class LeoFlexxTreeItem(flx.TreeItem):
    
    def init(self, leo_ap):
        # pylint: disable=arguments-differ
        ### print('===== LeoFlexxTreeItem.CTOR', repr(leo_ap))
        self.leo_ap = leo_ap
            # Gives access to cloned, marked, expanded fields.

    def getName(self):
        return 'head' # Required, for proper pane bindings.
        
    ### Keep it simple, for now.
    # @flx.emitter
    # def key_press(self, e):
        # ev = self._create_key_event(e)
        # if ev ['modifiers']:
            # e.preventDefault()
        # return ev
        
    # @flx.emitter
    # def user_selected(self, e):
        # ev = super().user_selected(e)
        # tree_selected_ap = self.root.main_window.tree.leo_selected_ap
        # if debug_tree:
            # print('')
            # print('===== flx_tree_item.user_selected')
            # print('               e:', repr(e))
            # print('              ev:', repr(ev))
            # print('     self.leo_ap:', repr(self.leo_ap))
            # print('tree.selected_ap:', repr(tree_selected_ap))
            # if self.leo_ap ==tree_selected_ap:
                # print('----- already selected')
            # else:
                # print('----- SEL:', repr(ev.new_value))
            # print('')
        # ###### This test is never True. #######
        # ###### The headline is <Invalid clone>. set by app.p_to_ap.
        # if self.leo_ap ==tree_selected_ap:
            # self.set_selected(True)
        # else:
            # self.set_selected(ev.new_value)
        # return ev
 
    # @flx.reaction('pointer_double_click')
    # def on_pointer_double_click(self, *events):
        # for ev in events:
            # print('tree-item.pointer_double_click')
            # dump_event(ev)
            # #
            # # The _render_title() and _render_text() methods can be overloaded to 
            # # display items in richer ways.
            # # See Widget._render_dom() for details.
            # # https://flexx.readthedocs.io/en/stable/ui/widget.html#flexx.ui.Widget._render_dom
#@+node:ekr.20181121031304.1: ** class BrowserTestManager
class BrowserTestManager (leoTest.TestManager):
    '''Run tests using the browser gui.'''
    
    def instantiate_gui(self):
        assert isinstance(g.app.gui, LeoBrowserGui)
        return g.app.gui
#@-others
if __name__ == '__main__':
    flx.launch(LeoBrowserApp)
    flx.logger.info('LeoApp: after flx.launch')
    flx.set_log_level('ERROR' if warnings_only else 'INFO')
        # Debug produces too many messages, in general.
    flx.run()
#@-leo

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
    # **Note**: JS code can not use g.trace, g.callers, g.pdb.
import leo.core.leoBridge as leoBridge
import leo.core.leoFrame as leoFrame
import leo.core.leoGui as leoGui
import leo.core.leoMenu as leoMenu
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
debug = True
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
    allowed = r'(Traceback|Critical|Error|Leo|Session|Starting|Stopping|Warning)'
    pattern = re.compile(allowed, re.IGNORECASE)
    flx.set_log_level('INFO', pattern)
#@+node:ekr.20181107052522.1: ** class LeoBrowserApp(PyComponent)
# pscript never converts flx.PyComponents to JS.

class LeoBrowserApp(flx.PyComponent):
    '''
    The browser component of Leo in the browser.
    This is self.root for all flx.Widget objects!
    This is *not* g.app. Leo's core defines g.app.
    '''
    # This may be optional, but it doesn't hurt.
    main_window = flx.ComponentProp(settable=True)

    def init(self):
        c, g = self.open_bridge()
        ###
            # g.trace('(LeoBrowserApp) id(g)', repr(id(g)))
            # g.trace('(LeoBrowserApp) c.frame', repr(c.frame))
            # g.trace('(LeoBrowserApp) g.app', repr(g.app))
            # g.trace('(LeoBrowserApp) g.app.gui', repr(g.app.gui))
        self.c = c
        self.gui = gui = LeoBrowserGui()
        # Inject the newly-created gui into g.app.
        g.app.gui = gui
        title = c.computeWindowTitle(c.mFileName)
        c.frame = gui.lastFrame = LeoBrowserFrame(c, title, gui)
            # similar to NullGui.createLeoFrame.
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
        c = self.c
        if command.startswith('echo'):
            self.gui.echo()
            self.gui.tree_echo()
        elif command == 'log':
            w.log.put('Test message to LeoFlexxLog.put')
                # Test LeoFlexxLog.put.
            c.frame.log.put('Test message to LeoBrowserLog.put')
                # Test LeoBrowserLog.put.
        elif command == 'redraw':
            d = self.make_redraw_dict()
            if 1:
                w.tree.redraw(d)
            else: # works.
                self.dump_redraw_dict(d)
        elif command.startswith('sel'):
            # Test LeoBrowserTree.select.
            h = 'Active Unit Tests'
            p = g.findTopLevelNode(c, h, exact=True)
            if p:
                c.frame.tree.select(p)
            else:
                g.trace('not found: %s' % h)
        elif command == 'status':
            if 1:
                c.frame.statusLine.put('Test 1 Status')
                c.frame.statusLine.put1('Test 2 Status')
            else: # Als works.
                w.status_line.put('Test 1 Status')
                w.status_line.put2('Test 2 Status')
        elif command == 'test':
            self.test_round_trip_positions()
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
        trace = True
        c = self.c
        key, mods = ev ['key'], ev ['modifiers']
        d = {
            'ArrowDown':'Down',
            'ArrowLeft':'Left',
            'ArrowRight': 'Right',
            'ArrowUp': 'Up',
            'PageDown': 'Next',
            'PageUp': 'Prior',
        }
        char = d.get(key, key)
        if 'Ctrl' in mods:
            mods.remove('Ctrl')
            mods.append('Control')
        binding = '%s%s' % (''.join(['%s+' % (z) for z in mods]), key)
        widget = getattr(c.frame, kind)
        key_event = leoGui.LeoKeyEvent(c,
            char = char,
            event = { 'c': c },
            binding = binding,
            w = widget.wrapper,
            # x=None, y=None, x_root=None, y_root=None
        )
        if trace:
            g.app.debug = ['keys',]
                # For k.masterKeyHandler.
            g.trace('%r %r ==> %r %r IN %r' % (
                mods, key, char, binding,  widget.wrapper.getName()))
            g.trace('before:', c.p.h)
        c.k.masterKeyHandler(key_event)
        if trace:
            g.app.debug = []
            g.trace(' after:', c.p.h)
    #@+node:ekr.20181113053154.1: *4* app.action: dump_redraw_dict
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
    #@+node:ekr.20181113085722.1: *4* app.action: dump_ap
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
    #@+node:ekr.20181116053210.1: *4* app.action: echo
    @flx.action
    def echo (self, message=None):
        print('===== echo =====', message or '<Empty Message>')
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

        
    #@+node:ekr.20181111202747.1: *4* app.action: select_ap & select_p
    @flx.action
    def select_ap(self, ap):
        '''Select the position in Leo's core corresponding to the archived position.'''
        c = self.c
        p = self.ap_to_p(ap)
        c.frame.tree.super_select(p)
            # call LeoTree.select, but not self.select_p.
            # This hack prevents an unbounded recursion.
        g.trace('(LeoBrowserApp)  after: c.p.h: ', c.p.h)

    @flx.action
    def select_p(self, p):
        '''
        Select the position in the tree.
        
        Called from LeoBrowserTree.select, so do *not* call c.frame.tree.select.
        '''
        # g.trace('(LeoBrowserApp) select_p', repr(p.h))
        w = self.main_window
        ap = self.p_to_ap(p)
        w.tree.select_ap(ap)
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
        elif debug:
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
        c, w = self.c, self.main_window
        gnxs = [z ['gnx'] for z in ap ['stack']]
        vnodes = [self.gnx_to_vnode[z] for z in gnxs]
        headlines = [v.h for v in vnodes]
        headlines.append(ap ['headline'])
        fn = g.shortFileName(c.fileName())
        w.status_line.put2('%s#%s' % (fn, '->'.join(headlines)))
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
        if 0:
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
        path = g.os_path_finalize_join(g.app.loadDir, '..', 'test', 'unitTest.leo')
        if not g.os_path_exists(path):
            flx.logger.error('open_bridge: does not exist: %r' % path)
            return
        c = bridge.openLeoFile(path)
        return c, g
    #@+node:ekr.20181115171220.1: *3* app.message
    def message(self, s):
        '''For testing.'''
        print('app.message: %s' % s)
    #@+node:ekr.20181112182636.1: *3* app.run_all_unit_tests
    def run_all_unit_tests (self):
        '''Run all unit tests from the bridge.'''
        print('===== app.run_all_unit_tests: Start')
        c = self.c
        h = 'Active Unit Tests'
        p = g.findTopLevelNode(c, h, exact=True)
        if p:
            ### self.gui.frame.tree.select(p)
            c.frame.tree.select(p)
            c.debugCommands.runSelectedUnitTestsLocally()
            print('===== app.run_all_unit_tests: Done')
        else:
            print('do_command: select: not found: %s' % h)
    #@-others
#@+node:ekr.20181115071559.1: ** Python wrappers
#@+node:ekr.20181115092337.3: *3* class LeoBrowserBody
class LeoBrowserBody(leoFrame.NullBody):
   
    def __init__(self, frame):
        super().__init__(frame, parentFrame=None)
        assert self.wrapper.getName().startswith('body')
        self.root = Root()
        self.widget = None

    #@+others
    #@-others
#@+node:ekr.20181115092337.6: *3* class LeoBrowserFrame
class LeoBrowserFrame(leoFrame.NullFrame):
    
    def __init__(self, c, title, gui):
        '''Ctor for the LeoBrowserFrame class.'''
        super().__init__(c, title, gui)
        assert self.c == c
        frame = self
        self.root = Root()
        self.body = LeoBrowserBody(frame)
        self.tree = LeoBrowserTree(frame)
        self.log = LeoBrowserLog(frame)
        self.menu = LeoBrowserMenu(frame)
        self.iconBar = LeoBrowserIconBar(c, frame)
        self.statusLine = LeoBrowserStatusLine(c, frame)
            # NullFrame does this in createStatusLine.
        
    def finishCreate(self):
        '''Override NullFrame.finishCreate.'''
        pass # Do not call self.createFirstTreeNode.

    #@+others
    #@-others
#@+node:ekr.20181113041113.1: *3* class LeoBrowserGui
class LeoBrowserGui(leoGui.NullGui):

    def __init__ (self, guiName='nullGui'):
        super().__init__(guiName='BrowserGui')
        self.root = Root()
        
    def echo(self):
        self.root.echo('From LeoBrowser Gui')
        
    def tree_echo(self):
        self.root.main_window.tree.echo('From LeoBrowser Gui')
        
    #@+others
    #@+node:ekr.20181118020756.1: *4* LeoBrowserGui.insertKeyEvent
    def insertKeyEvent(self, event, i):
        '''Insert the key given by event in location i of widget event.w.'''
        g.trace('(LeoBrowserGui)', g.callers())
        ### From qt_gui.insertKeyEvent
            # import leo.core.leoGui as leoGui
            # assert isinstance(event, leoGui.LeoKeyEvent)
            # qevent = event.event
            # assert isinstance(qevent, QtGui.QKeyEvent)
            # qw = getattr(event.w, 'widget', None)
            # if qw and isinstance(qw, QtWidgets.QTextEdit):
                # if 1:
                    # # Assume that qevent.text() *is* the desired text.
                    # # This means we don't have to hack eventFilter.
                    # qw.insertPlainText(qevent.text())
                # else:
                    # # Make no such assumption.
                    # # We would like to use qevent to insert the character,
                    # # but this would invoke eventFilter again!
                    # # So set this flag for eventFilter, which will
                    # # return False, indicating that the widget must handle
                    # # qevent, which *presumably* is the best that can be done.
                    # g.app.gui.insert_char_flag = True
    #@-others
#@+node:ekr.20181115092337.21: *3* class LeoBrowserIconBar
class LeoBrowserIconBar(leoFrame.NullIconBarClass):

    def __init__(self, c, parentFrame):
        super().__init__(c, parentFrame)
        assert self.c == c
        self.root = Root()
            
    #@+others
    #@-others
#@+node:ekr.20181115092337.22: *3* class LeoBrowserLog
class LeoBrowserLog(leoFrame.NullLog):
    
    def __init__(self, frame, parentFrame=None):
        super().__init__(frame, parentFrame)
        self.root = Root()
        self.logCtrl = self
            # Required
        self.wrapper = self
            
    def getName(self):
        return 'log' # Required for proper pane bindings.

    # Overrides.
    def put(self, s, color=None, tabName='Log', from_redirect=False, nodeLink=None):
        self.root.main_window.log.put(s)
    
    def putnl(self, tabName='Log'):
        self.root.main_window.log.put('')
#@+node:ekr.20181115092337.31: *3* class LeoBrowserMenu
class LeoBrowserMenu(leoMenu.NullMenu):
    
    def __init__(self, frame):
        super().__init__(frame)
        self.root = Root()

    #@+others
    #@-others
#@+node:ekr.20181115120317.1: *3* class LeoBrowserMinibuffer (not used)
class LeoBrowserMinibuffer (object):
    
    def __init__(self, c, frame):
        self.c = c
        self.frame = frame
        self.root = Root()
        
    #@+others
    #@-others
#@+node:ekr.20181115092337.32: *3* class LeoBrowserStatusLine
class LeoBrowserStatusLine(leoFrame.NullStatusLineClass):
    
    def __init__(self, c, parentFrame):
        super().__init__(c, parentFrame)
        self.root = Root()

    #
    # Overrides.
    def clear(self):
        self.put('')
    
    def get(self):
        g.trace('(LeoBrowserStatusLine): NOT READY')
        return ''
        
    def update(self):
        # g.trace('(LeoBrowserStatusLine)')
        super().update()
    
    def put(self, s, bg=None, fg=None):
        w = self.root.main_window
        # g.trace('(LeoBrowserStatusLine)', s)
        w.status_line.put(s, bg, fg)
    
    def put1(self, s, bg=None, fg=None):
        w = self.root.main_window
        # g.trace('(LeoBrowserStatusLine)', s)
        w.status_line.put2(s, bg, fg)
#@+node:ekr.20181115092337.57: *3* class LeoBrowserTree
class LeoBrowserTree(leoFrame.NullTree):
    
    def __init__(self, frame):
        super().__init__(frame)
        self.root = Root()
        self.wrapper = self
        
    def getName(self):
        return 'canvas(tree)' # Required for proper pane bindings.

    #@+others
    #@+node:ekr.20181116081421.1: *4* LeoBrowserTree.select & super_select
    def select(self, p):
        '''Override NullTree.select, which is actually LeoTree.select.'''
        super().select(p)
            # Call LeoTree.select.'''
        self.root.select_p(p)
            # Call app.select_position.

    def super_select(self, p):
        '''Call only LeoTree.select.'''
        super().select(p)
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
        
    @flx.reaction('key_press')
    def on_key_press(self, *events):
        print('body.on_key_press')
        for ev in events:
            self.root.do_key(ev, 'body')

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
        ###with flx.TabLayout():
        if 1:
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
            self.widget = flx.LineEdit(flex=1, placeholder_text='Status area 1')
            self.widget2 = flx.LineEdit(flex=1, placeholder_text='Status area 2')
        self.widget.apply_style('background: green')
        self.widget2.apply_style('background: green')
        
    #@+others
    #@-others

    @flx.action
    def put(self, s, bg, fg):
        self.widget.set_text(s)
        
    @flx.action
    def put2(self, s, bg, fg):
        self.widget2.set_text(s)
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
            if 0: ###
                print('tree.clear_tree: dispose: %r' % item)
            item.dispose()
        #
        # Clear the internal data structures.
        self.leo_items = {}
        self.leo_populated_dict = {}
    #@+node:ekr.20181116054402.1: *5* tree.action: echo
    @flx.action
    def echo (self, message=None):
        print('===== tree echo =====', message or '<Empty Message>')
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
    #@+node:ekr.20181116083916.1: *5* tree.action: select_ap
    @flx.action
    def select_ap(self, ap):
        #
        # Unselect.
        if self.leo_selected_ap:
            old_key = self.ap_to_key(self.leo_selected_ap)
            old_item = self.leo_items.get(old_key)
            if old_item:
                # print('tree.select_ap: un-select:')
                old_item.set_selected(False)
            else:
                print('===== tree.select_ap: error: no item to unselect')
        else:
            print('tree.select_ap: no previously selected item.')
        #
        # Select.
        new_key = self.ap_to_key(ap)
        new_item = self.leo_items.get(new_key)
        if new_item:
            # print('tree.select_ap: select:')
            new_item.set_selected(True)
            self.leo_selected_ap = ap
        else:
            print('===== tree.select_ap: error: no item for ap:')
            self.leo_selected_ap = None
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
                self.root.select_ap(ap)
                    # Actually select the node!
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
    #@+node:ekr.20181116172300.1: *5* tree.reaction: key_down
    @flx.reaction('tree.key_press')
    def on_key_press(self, *events):
        for ev in events:
            self.root.do_key(ev, 'tree')
    #@+node:ekr.20181111011928.1: *4* tree.populate_children
    def populate_children(self, children, parent_ap):
        '''Populate parent with the children if necessary.'''
        trace = False
        if trace: print('tree.populate_children...')
        parent_key = self.ap_to_key(parent_ap)
        if parent_key in self.leo_populated_dict:
            # print('tree.populate_children: already populated', parent_ap ['headline'])
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
        if 0: ###
            print('tree.show_event: ' + message)
    #@-others
#@+node:ekr.20181108233657.1: *3* class LeoFlexxTreeItem
class LeoFlexxTreeItem(flx.TreeItem):
    
    def init(self, leo_ap):
        # pylint: disable=arguments-differ
        self.leo_ap = leo_ap
        
    def getName(self):
        return 'head' # Required, for proper pane bindings.
#@+node:ekr.20181115191638.1: ** class Root
class Root(flx.PyComponent):
    
    '''
    This class allows *plain* python classes to access *component* classes.
    '''
    def __getattr__ (self, attr):
        return getattr(self.root, attr)
#@-others
if __name__ == '__main__':
    flx.launch(LeoBrowserApp)
    flx.logger.info('LeoApp: after flx.launch')
    if not debug:
        suppress_unwanted_log_messages()
    flx.run()
#@-leo

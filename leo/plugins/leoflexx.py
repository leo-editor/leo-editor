# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20181103094900.1: * @file leoflexx.py
#@@first
#@@language python
#@@tabwidth -4
#@+<< leoflexx: docstring >>
#@+node:ekr.20181122215342.1: ** << leoflexx: docstring >>
#@@language md
#@@wrap
'''
flexx.py: LeoWapp (Leo as a web browser), implemented using flexx:
https://flexx.readthedocs.io/en/stable/

This file is the main line of the LeoWapp project.
https://github.com/leo-editor/leo-editor/issues/1005.

See #1005 for a status report and list of to-do's.

# Prerequites

Install flexx: https://flexx.readthedocs.io/en/stable/start.html

# Running stand-alone

You can run leoflexx.py in stand-alone mode from a console:

    python <path to>leoflexx.py --flexx-webruntime=firefox-browser​

The --flex-webruntime command-line arg is optional. If omitted, you'll use
the webruntime environment.

When running stand-alone, the startup code uses Leo's bridge module to load
unitTest.leo.

# Running as Leo's gui

You can also run leoflexx.py as Leo's gui:

    leo --gui=browser
    leo --gui=browser-firefox-browser​
    
# What you should see
    
However you start leoflexx.py you should see the flexx (Tornado) server
start up in the console.

Something that looks like Leo should then appear in the browser. Everything
you see is real, and most of it is "live".
'''
#@-<< leoflexx: docstring >>
#@+<< leoflexx: imports >>
#@+node:ekr.20181113041314.1: ** << leoflexx: imports >>
try:
    from flexx import flx
    from pscript import RawJS
except Exception:
    flx = None
import os
import re
import sys
import time
# This is what Leo typically does.
path = os.getcwd()
if path not in sys.path:
    sys.path.append(path)
import leo.core.leoGlobals as g
    # JS code can *not* use g.trace, g.callers or g.pdb.
import leo.core.leoBridge as leoBridge
import leo.core.leoFastRedraw as leoFastRedraw
import leo.core.leoFrame as leoFrame
import leo.core.leoGui as leoGui
import leo.core.leoMenu as leoMenu
import leo.core.leoNodes as leoNodes
import leo.core.leoTest as leoTest
#@-<< leoflexx: imports >>
#@+<< leoflexx: assets >>
#@+node:ekr.20181111074958.1: ** << leoflexx: assets >>
# Assets for ace JS editor.
base_url = 'https://cdnjs.cloudflare.com/ajax/libs/ace/1.2.6/'
flx.assets.associate_asset(__name__, base_url + 'ace.js')
flx.assets.associate_asset(__name__, base_url + 'mode-python.js')
flx.assets.associate_asset(__name__, base_url + 'theme-solarized_dark.js')
#@-<< leoflexx: assets >>
#
# Switches.
debug_focus = False # True: put 'focus' in g.app.debug.
debug_keys = False # True: put 'keys' in g.app.debug.
is_public = True # True: public code issues various alerts.
debug = not is_public
#
# pylint: disable=logging-not-lazy
#@+others
#@+node:ekr.20181121040901.1: **  top-level functions
#@+node:ekr.20181121091633.1: *3* dump_event
def dump_event (ev):
    '''Print a description of the event.'''
    id_ = ev.source.title or ev.source.text
    kind = '' if ev.new_value else 'un-'
    s = kind + ev.type
    message = '%s: %s' % (s.rjust(15), id_)
    print('dump_event: ' + message)
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
#@+node:ekr.20181112165240.1: *3* info (deprecated)
def info (s):
    '''Send the string s to the flex logger, at level info.'''
    if not isinstance(s, str):
        s = repr(s)
    flx.logger.info('Leo: ' + s)
        # A hack: automatically add the "Leo" prefix so
        # the top-level suppression logic will not delete this message.
#@+node:ekr.20181103151350.1: *3* init
def init():
    return flx
#@+node:ekr.20181203151314.1: *3* make_editor_function
def make_editor_function(name, node):
    '''
    Instantiate the ace editor.
    
    Making this a top-level function avoids the need to create a common
    base class that only defines this as a method.
    '''
    # pylint: disable=undefined-variable
        # window looks undefined.
    global window 
    ace = window.ace.edit(node, 'editor')
    ace.navigateFileEnd()  # otherwise all lines highlighted
    ace.setTheme("ace/theme/solarized_dark")
    if name == 'body':
        ace.getSession().setMode("ace/mode/python")
            # This sets soft tabs.
    if name == 'minibuffer':
        pass ### Disable line numbers.
    return ace
#@+node:ekr.20181113041410.1: *3* suppress_unwanted_log_messages (not used)
def suppress_unwanted_log_messages():
    '''
    Suppress the "Automatically scrolling cursor into view" messages by
    *allowing* only important messages.
    '''
    allowed = r'(Traceback|Critical|Error|Leo|Session|Starting|Stopping|Warning)'
    pattern = re.compile(allowed, re.IGNORECASE)
    flx.set_log_level('INFO', pattern)
#@+node:ekr.20181115071559.1: ** Py side: App & wrapper classes
#@+node:ekr.20181127151027.1: *3* class API_Wrapper (StringTextWrapper)
class API_Wrapper (leoFrame.StringTextWrapper):
    '''
    A wrapper class that implements the high-level interface.
    '''

    def __init__(self, c, name):
        assert name in ('body', 'log', 'minibuffer'), repr(name)
        super().__init__(c, name)
        assert self.c == c
        assert self.name == name
        self.tag = '(API_Wrapper: %s)' % name
        self.root = get_root()
        
    def flx_wrapper(self):
        if self.root.inited:
            w = self.root.main_window
            return getattr(w, self.name)
        return g.NullObject()
        
    def setFocus(self):
        print(self.tag, 'setAllText')
        self.flx_wrapper().set_focus()

    # No need to override getters.
    #@+others
    #@+node:ekr.20181128101421.1: *4* API_Wrapper.Selection Setters
    def finish_set_insert(self, tag):
        '''Common helper for selection setters.'''
        if 0:
            print('%s: %s: %s %r' % (self.tag, tag, self.ins, self.sel)) # debug_select
        self.flx_wrapper().set_insert_point(self.ins, self.sel)

    def seeInsertPoint(self):
        self.flx_wrapper().see_insert_point()

    def selectAllText(self, insert=None):
        super().selectAllText(insert)
        self.finish_set_insert('selectAllText')

    def setInsertPoint(self, pos, s=None):
        super().setInsertPoint(pos, s)
        self.finish_set_insert('setInsertPoint')

    def setSelectionRange(self, i, j, insert=None):
        super().setSelectionRange(i, j, insert)
        self.finish_set_insert('setSelectionRange')
    #@+node:ekr.20181127121642.1: *4* API_Wrapper.Text Setters
    #@@language rest
    #@@wrap
    #@+at
    # These methods implement Leo's high-level api for the body pane.
    # 
    # Consider Leo's sort-lines command. sort-lines knows nothing about which gui
    # is in effect. It updates the body pane using *only* the high-level api.
    # 
    # These methods must do two things:
    #     
    # 1. Call the corresponding super() method to update self.s, self.i and self.ins.
    # 2. Call the corresponding flx_body methods to update the flx_body widget,
    #    except while unit testing.
    #@@c
    #@@language python

    def finish_setter(self, tag):
        '''The common setter code.'''
        c = self.c
        # At present, self.name is always 'body'.
        if self.name == 'body':
            c.p.v.setBodyString(self.s)
                # p.b = self.s will cause an unbounded recursion.
        if 0:
            print('%s: %s:  len(self.s): %s ins: %s sel: %r' % (
                self.tag, tag, len(self.s), self.ins, self.sel)) 
        if not g.unitTesting:
            self.flx_wrapper().set_text(self.s)
            self.flx_wrapper().set_insert_point(self.ins)

    def appendText(self, s):
        super().appendText(s)
        self.finish_setter('appendText')

    def delete(self, i, j=None):
        super().delete(i, j)
        self.finish_setter('delete')

    def deleteTextSelection(self):
        super().deleteTextSelection()
        self.finish_setter('deleteTextSelection')
        
    def insert(self, i, s):
        # Called from doPlainChar, insertNewlineHelper, etc. on every keystroke.
        super().insert(i, s)
        self.finish_setter('insert')

    def setAllText(self, s):
        # Called by set_body_text_after_select.
        super().setAllText(s)
        self.finish_setter('insert')
    #@-others
#@+node:ekr.20181121031304.1: *3* class BrowserTestManager
class BrowserTestManager (leoTest.TestManager):
    '''Run tests using the browser gui.'''
    
    def instantiate_gui(self):
        assert isinstance(g.app.gui, LeoBrowserGui)
        return g.app.gui
#@+node:ekr.20181206153831.1: *3* class DummyFrame
class DummyFrame (leoFrame.NullFrame):
    '''
    A frame to keep Leo's core happy until we can call app.finish_create.
    '''
    
    def __repr__(self):
        return 'DummyFrame: %r' % self.c.shortFileName()

    __str__ = __repr__

#@+node:ekr.20181107052522.1: *3* class LeoBrowserApp
# pscript never converts flx.PyComponents to JS.

class LeoBrowserApp(flx.PyComponent):
    '''
    The browser component of Leo in the browser.

    This is self.root for all flexx components.

    This is *not* g.app.
    '''
    
    main_window = flx.ComponentProp(settable=True)

    #@+others
    #@+node:ekr.20181126103604.1: *4*  app.Initing
    #@+node:ekr.20181114015356.1: *5* app.create_all_data
    def create_gnx_to_vnode(self):
        t1 = time.clock()
        self.gnx_to_vnode = { v.gnx: v for v in self.c.all_unique_nodes() }
            # This is likely the only data that ever will be needed.
        if 0:
            print('app.create_all_data: %5.3f sec. %s entries' % (
                (time.clock()-t1), len(list(self.gnx_to_vnode.keys()))))
        self.test_round_trip_positions()
    #@+node:ekr.20181124133513.1: *5* app.finish_create
    @flx.action
    def finish_create(self):
        '''
        Initialize all ivars and widgets.
        
        Called after all flx.Widgets have been fully inited!
        '''
        w = self.main_window
        self.c = c = g.app.log.c
        assert c
        # Init all redraw ivars
        self.create_gnx_to_vnode()
        self.old_flattened_outline = []
        self.old_redraw_dict = {}
        self.redraw_generation = 0
        self.fast_redrawer = leoFastRedraw.FastRedraw()
        self.old_flattened_outline = self.fast_redrawer.flatten_outline(c)
        self.old_redraw_dict = self.make_redraw_dict(c.p)
        # Select the proper position.
        c.contractAllHeadlines()
        c.selectPosition(c.p or c.rootPosition())
        # Monkey-patch the FindTabManager
        c.findCommands.minibuffer_mode = True
        c.findCommands.ftm = g.NullObject()
        # Init the log, body, status line and tree.
        g.app.gui.writeWaitingLog2()
        ### Needed ???
        self.set_body_text()
        self.set_status()
        self.redraw(c.p)
        # Init the focus. It's debatable...
        if 0:
            self.gui.set_focus(c, c.frame.tree)
            w.tree.set_focus()
        else: # This definitely shows focus in the editor.
            self.gui.set_focus(c, c.frame.body)
            w.body.set_focus()
        # Set the inited flag *last*
        self.inited = True
    #@+node:ekr.20181216042806.1: *5* app.init
    def init(self):
        # Set the ivars.
        global g # always use the imported g.
        self.inited = False
            # Set in finish_create
        self.tag = '(app wrapper)'
        #
        # Open or get the first file.
        if g.app and isinstance(g.app.gui, LeoBrowserGui):
            # We are running with --gui=browser.
            assert isinstance(g.app.log, leoFrame.NullLog)
            c = g.app.log.c
        else:
            # We are running stand-alone.
            # Use the bridge to open a single file.
            # This is only for testing, and will likely be removed.
            c, g = self.open_bridge()
            g.app.gui = gui = LeoBrowserGui()
            title = c.computeWindowTitle(c.mFileName)
            g.app.windowList = [DummyFrame(c, title, gui)]
        #
        # self.gui must be a synonym for g.app.gui.
        self.c = c
        self.gui = gui = g.app.gui
        # Make sure everything is as expected.
        assert self.c and c == self.c
        assert g.app.gui.guiName() == 'browser'
            # Important: the leoTest module special cases this name.
        # 
        # When running from Leo's core, we must wait until now to set LeoBrowserGui.root.
        gui.root = get_root()
        #
        # Check g.app.ivars.
        assert g.app.windowList
        for frame in g.app.windowList:
            assert isinstance(frame, DummyFrame), repr(frame)
        #
        # Set g.app debugging ivars.
        if debug_focus:
            g.app.debug.append('focus')
        if debug_keys:
            g.app.debug.append('keys')
        #
        # Instantiate all wrappers here, not in app.finish_create.
        title = c.computeWindowTitle(c.mFileName)
        c.frame = gui.lastFrame = LeoBrowserFrame(c, title, gui)
        #
        # The main window will be created (much) later.
        main_window = LeoFlexxMainWindow()
        self._mutate('main_window', main_window)
    #@+node:ekr.20181105091545.1: *5* app.open_bridge
    def open_bridge(self):
        '''Can't be in JS.'''
        bridge = leoBridge.controller(gui = None,
            loadPlugins = False,
            readSettings = True, # Required to get bindings!
            silent = True, # Use silentmode to keep queuing log message.
            tracePlugins = False,
            verbose = True, # True: prints log messages.
        )
        print('')
        print('Stand-alone operation of leoflexx.py is for testing only.')
        print('Opening unitTest.leo...')
        print('')
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
    #@+node:ekr.20181117163223.1: *4* app.action.do_key
    # https://flexx.readthedocs.io/en/stable/ui/widget.html#flexx.ui.Widget.key_down
    # See Widget._create_key_event in flexx/ui/_widget.py:

    @flx.action
    def do_key (self, ev, ivar):
        '''
        LeoBrowserApp.do_key: The central key handler.
        
        Will be called *in addition* to any inner key handlers,
        unless the inner key handler calls e.preventDefault()
        '''
        c = self.c
        browser_wrapper = getattr(c.frame, ivar)
            # Essential: there is no way to pass the actual wrapper.
        #@+<< check browser_wrapper >>
        #@+node:ekr.20181129073812.1: *5* << check browser_wrapper >>
        assert isinstance(browser_wrapper, (
            LeoBrowserBody,
            LeoBrowserLog,
            LeoBrowserMinibuffer,
            LeoBrowserStatusLine,
            LeoBrowserTree,
        )), repr(browser_wrapper)
        #@-<< check browser_wrapper >>
        key, mods = ev ['key'], ev ['modifiers']
            # ev is a dict, keys are type, source, key, modifiers
            # mods in ('Alt', 'Shift', 'Ctrl', 'Meta')
        # Special case Ctrl-H and Ctrl-F.
        if mods == ['Ctrl'] and key in 'fh':
            command = 'find' if key == 'f' else 'head'
            self.do_command(command, key, mods)
            return
        #@+<< set char to the translated key name >>
        #@+node:ekr.20181129073905.1: *5* << set char to the translated key name >>
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
        #@-<< set char to the translated key name >>
        binding = '%s%s' % (''.join(['%s+' % (z) for z in mods]), char)
        #@+<< create key_event >>
        #@+node:ekr.20181129073734.1: *5* << create key_event >>
        # create the key event, but don't bother tracing it.
        old_debug = g.app.debug
        try:
            g.app.debug = []
            key_event = leoGui.LeoKeyEvent(c,
                char = char,
                binding = binding,
                event = { 'c': c },
                w = browser_wrapper,
            )
        finally:
            g.app.debug = old_debug
        #@-<< create key_event >>
        c.k.masterKeyHandler(key_event)
    #@+node:ekr.20181207080933.1: *4* app.action.set_body_text & set_status
    # These must be separate because they are called from the tree logic.

    @flx.action
    def set_body_text(self):
        ### c, w = self.c, self.main_window
        ### w.body.set_text(c.p.b)
        c = self.c
        c.frame.body.wrapper.setAllText(c.p.b)
            ### Using the wrapper sets the text *and* the insert point and selection range.

    @flx.action
    def set_status(self):
        c, w = self.c, self.main_window
        lt, rt = c.frame.statusLine.update(c.p.b, 0)
        w.status_line.update(lt, rt)
        
    #@+node:ekr.20181122132345.1: *4* app.Drawing...
    #@+node:ekr.20181113042549.1: *5* app.action.redraw
    @flx.action
    def redraw (self, p):
        '''
        Send a **redraw list** to the tree.
        
        This is a recusive list lists of items (ap, gnx, headline) describing
        all and *only* the presently visible nodes in the tree.
        
        As a side effect, app.make_redraw_dict updates all internal dicts.
        '''
        c = self.c
        p = p or c.p
        redrawer = self.fast_redrawer
        w = self.main_window
        #
        # Be careful: c.frame.redraw can be called before app.finish_create.
        if not w or not w.tree:
            return
        #
        # Profile times when all nodes are expanded.
            # self.test_full_outline(p)
        #
        # Redraw only the visible nodes.
        t1 = time.clock()
        ap = self.p_to_ap(p)
        w.tree.select_ap(ap)
        redraw_dict = self.make_redraw_dict(p)
            # Needed to compare generations, even if there are no changes.
        new_flattened_outline = redrawer.flatten_outline(c)
        redraw_instructions = redrawer.make_redraw_list(
            self.old_flattened_outline,
            new_flattened_outline,
        )
        w.tree.redraw_with_dict(redraw_dict, redraw_instructions)
            # At present, this does a full redraw using redraw_dict.
            # The redraw instructions are not used.
        ###
            # Wrong: only Leo's core should call c.setChanged().
            # Set c.changed if there are any redraw instructions.
            # if redraw_instructions:
                # if debug_changed: print('app.redraw: C CHANGED')
                # c.setChanged()
        if 0:
            g.trace('%5.3f sec.' % (time.clock()-t1))
        #
        # Move to the next redraw generation.
        self.old_flattened_outline = new_flattened_outline
        self.old_redraw_dict = redraw_dict
        self.redraw_generation += 1
    #@+node:ekr.20181111095640.1: *5* app.action.send_children_to_tree
    @flx.action
    def send_children_to_tree(self, parent_ap):
        '''
        Call w.tree.receive_children(d), where d is compatible with make_redraw_dict:
            {
                'parent_ap': parent_ap,
                'items': [
                    self.make_dict_for_position(p)
                        for p in for p in p.children()
                ],
            }
        '''
        p = self.ap_to_p(parent_ap)
        assert p, repr(parent_ap)
        if 0:
            # There is a similar trace in flx.tree.receive_children.
            print('===== send_children_to_tree: %s children' % len(list(p.children())))
            if 0: # Corresponds to the trace in flx_tree.populate_children.
                for child in p.children():
                    print('  ' + child.h)
        #
        # Always respond, even if there are no children.
        # This allows the tree widget to reset state properly.
        w = self.main_window
        # assert parent_ap == self.p_to_ap(p), '\n%r\n%r' % (parent_ap, self.p_to_ap(p))
            # This assert can fail because the expansion bits don't match.
        w.tree.receive_children({
            'parent_ap': parent_ap,
            'items': [
                self.make_dict_for_position(p)
                    for p in p.children()
                # For compatibility with flx.tree.create_item_with_parent.
            ],
        })
    #@+node:ekr.20181111203114.1: *5* app.ap_to_p
    def ap_to_p (self, ap):
        '''Convert an archived position to a true Leo position.'''
        childIndex = ap ['childIndex']
        v = self.gnx_to_vnode [ap ['gnx']]
        stack = [
            (self.gnx_to_vnode [d ['gnx']], d ['childIndex'])
                for d in ap ['stack']
        ]
        return leoNodes.position(v, childIndex, stack)
    #@+node:ekr.20181124071215.1: *5* app.dump_top_level
    def dump_top_level(self):
        '''Dump the top-level nodes.'''
        if 0:
            c = self.c
            print('===== app.dump_top_level...')
            # print('root:', c.rootPosition().h)
            # print(' c.p:', c.p.h)
            # print('')
            # print('Top-level nodes...')
            for p in c.rootPosition().self_and_siblings():
                print('  %5s %s' % (p.isExpanded(), p.h))
            print('')
    #@+node:ekr.20181113043539.1: *5* app.make_redraw_dict & helper
    def make_redraw_dict(self, p=None):
        '''
        Return a **recursive**, archivable, list of lists describing all the
        visible nodes of the tree.
        
        As a side effect, recreate gnx_to_vnode.
        '''
        c = self.c
        p = p or c.p
        t1 = time.clock()
        c.expandAllAncestors(c.p)
            # Ensure that c.p will be shown.
        d = {
            'c.p': self.p_to_ap(p),
            'items': [
                self.make_dict_for_position(p2)
                    for p2 in c.rootPosition().self_and_siblings()
            ],
        }
        t2 = time.clock()
        if 0:
            print('app.make_redraw_dict: %s direct children %5.3f sec.' % (
                len(list(c.rootPosition().self_and_siblings())), (t2-t1)))
        return d
    #@+node:ekr.20181113044701.1: *6* app.make_dict_for_position
    def make_dict_for_position(self, p):
        ''' 
        Recursively add a sublist for p and all its visible nodes.
        It is already known that p itself is visible.
        '''
        assert p.v
        self.gnx_to_vnode[p.v.gnx] = p.v
        if 0: print('make_dict_for_position: %s%s' % ('  '*p.level(), p.v.h))
            # debug_redraw
                # A superb trace. There are similar traces in:
                # - flx_tree.redraw_with_dict  and its helper, flx_tree.create_item_with_parent.
                # - flx_tree.populate_children and its helper, flx_tree.create_item_for_ap
        if p.isExpanded(): # Do not use p.v.isExpanded().
            children = [
                self.make_dict_for_position(child)
                    for child in p.children()
            ]
        else:
            children = []
        return {
            'ap': self.p_to_ap(p),
            # 'body': p.b, # This would transfer much too much data.
            'children': children,
            'gnx': p.v.gnx,
            'headline': p.v.h,
        }
    #@+node:ekr.20181129122147.1: *4* app.edit_headline & helper
    def edit_headline(self):
        '''Simulate editing the headline in the minibuffer.'''
        c, w = self.c, self.root.main_window
        mb = w.minibuffer
        if 0: g.trace(mb, c.p.h)
        mb.set_text('Enter Headline: ')
        mb.set_focus()
        
    def edit_headline_completer(self, headline):
        g.trace(headline)
    #@+node:ekr.20181124095316.1: *4* app.Selecting...
    #@+node:ekr.20181111202747.1: *5* app.action.select_ap
    @flx.action
    def select_ap(self, ap):
        '''
        Select the position in Leo's core corresponding to the archived position.
        Nothing in the flx.tree needs to be updated.
        '''
        assert ap, g.callers()
        c, w = self.c, self.main_window
        p = self.ap_to_p(ap)
        assert p, (repr(ap), g.callers())
        lt, rt = c.frame.statusLine.update()
        w.status_line.update(lt, rt)
        # print('===== app.select_ap', repr(ap))
        w.tree.select_ap(ap)
        c.frame.tree.super_select(p)
            # call LeoTree.select, but not self.select_p.
    #@+node:ekr.20181118061020.1: *5* app.action.select_p
    @flx.action
    def select_p(self, p):
        '''
        Select the position in the tree.
        
        Called from LeoBrowserTree.select, so do *not* call c.frame.tree.select.
        '''
        c = self.c
        w = self.main_window
        ap = self.p_to_ap(p)
        # Be careful during startup.
        if w and w.tree:
            w.tree.set_ap(ap)
            body = c.frame.body.wrapper
            if debug: print('===== app.select_p: sel: %r %s' % (body.sel, p.h), g.callers())
            w.body.set_text(body.s)
                ###
            w.body.set_insert_point(body.ins, body.sel)
    #@+node:ekr.20181216051109.1: *5* app.action.select helpers NEW
    @flx.action
    def complete_select(self, d):
        '''A helper action, called from flx_body.sync_before_select.'''
        self.c.frame.tree.complete_select(d)

    @flx.action
    def select_tree_using_ap(self, ap):
        '''A helper action, called from flx_tree.on_selected_event.'''
        if 0: g.trace(ap ['headline'])
        p = self.ap_to_p(ap)
        self.c.frame.tree.select(p)
    #@+node:ekr.20181111204659.1: *5* app.p_to_ap (updates app.gnx_to_vnode)
    def p_to_ap(self, p):
        '''
        Convert a true Leo position to a serializable archived position.
        '''
        if not p.v:
            print('app.p_to_ap: no p.v: %r %s' % (p, g.callers()))
            assert False, g.callers()
        p_gnx = p.v.gnx
        if p_gnx not in self.gnx_to_vnode:
            # print('=== update gnx_to_vnode', p_gnx, p.h)
                # len(list(self.gnx_to_vnode.keys())
            self.gnx_to_vnode [p_gnx] = p.v
        return {
            'childIndex': p._childIndex,
            'cloned': p.isCloned(),
            'expanded': p.isExpanded(),
            'gnx': p.v.gnx,
            'level': p.level(),
            'headline': p.h,
            'marked': p.isMarked(),
            'stack': [{
                'gnx': stack_v.gnx,
                'childIndex': stack_childIndex,
                'headline': stack_v.h,
            } for (stack_v, stack_childIndex) in p.stack ],
        }
    #@+node:ekr.20181215154640.1: *5* app.update_body_from_dict
    def update_body_from_dict(self, d):
        '''Update p.b, etc, using d.'''
        c = self.c
        w = c.frame.body.wrapper
        # Compute the insert point.
        s = d['s']
        col, row = d['ins_col'], d['ins_row'], 
        ins = g.convertRowColToPythonIndex(s, row, col)
        # Compute the selection range.
        col1, row1 =  d ['sel_col1'], d ['sel_row1']
        col2, row2 =  d ['sel_col2'], d ['sel_row2']
        sel1 = g.convertRowColToPythonIndex(s, row1, col1)
        sel2 = g.convertRowColToPythonIndex(s, row2, col2)
        sel = (sel1, sel2)
        # Update Leo's internal data structures.
        w.ins, w.sel, w.s = ins, sel, s
        if debug: print('===== app.update_body_from_dict: ins: %s sel: (%s, %s) p: %s ==> %s' % (
                    ins, sel[0], sel[1], c.p.h, d['headline']))
    #@+node:ekr.20181122132009.1: *4* app.Testing...
    #@+node:ekr.20181111142921.1: *5* app.action: do_command & helpers
    @flx.action
    def do_command(self, command, key, mods):
        c = self.c
        w = self.main_window
        #
        # Intercept in-progress commands.
        h1 = 'Set headline: '
        if command.startswith(h1):
            self.end_set_headline(command[len(h1):])
            return
        h2 = 'Find: '
        if command.startswith(h2):
            self.end_find(command[len(h2):])
            return
        func = getattr(self, 'do_'+command, None)
        if func:
            func()
            return
        #
        # Pass all other commands to Leo.
        self.execute_minibuffer_command(command, key, mods)
        c.k.keyboardQuit()
        w.body.set_focus()
    #@+node:ekr.20181210054910.1: *6* app.do_cls
    def do_cls(self):
        c = self.c
        w = self.root.main_window
        g.cls()
        c.k.keyboardQuit()
        w.body.set_focus()
    #@+node:ekr.20181210055704.1: *6* app.do_find & helpers
    def do_find(self):
        c = self.c
        event = leoGui.LeoKeyEvent(c,
            binding = '',
            char = '',
            event = { 'c': c },
            w = c.frame.miniBufferWidget,
        )
        c.interactive(
            callback = self.terminate_do_find,
            event = event,
            prompts=['Find: ',],
        )
        
    def terminate_do_find(self):
        '''Never called.'''
    #@+node:ekr.20181210092900.1: *7* app.end_find
    def end_find(self, pattern):
        c = self.c
        fc = c.findCommands
        
        class DummyFTM:
            def getFindText(self):
                return pattern
            def getReplaceText(self):
                return ''

        # Init the search.
        if 1:
            fc.ftm = DummyFTM()
        if 1:
            fc.find_text = pattern
            fc.change_text = ''
            fc.find_seen = set()
            fc.pattern_match = False
            fc.in_headline = False
            fc.search_body = True
            fc.was_in_headline = False
            fc.wrapping = False
        # Do the search.
        fc.findNext()
        if 1: ### Testing only???
            w = self.root.main_window
            c.k.keyboardQuit()
            c.redraw()
            w.body.set_focus()
    #@+node:ekr.20181119103144.1: *6* app.do_focus
    def do_focus(self):
        c = self.c
        old_debug = g.app.debug
        try:
            g.app.debug = ['focus', 'keys',]
            print('\ncalling c.set_focus(c.frame.miniBufferWidget.widget')
            c.set_focus(c.frame.miniBufferWidget.widget)
        finally:
            g.app.debug = old_debug


            
    #@+node:ekr.20181210055648.1: *6* app.do_head & helpers
    def do_head(self):
        c = self.c
        event = leoGui.LeoKeyEvent(c,
            binding = '',
            char = '',
            event = { 'c': c },
            w = c.frame.miniBufferWidget,
        )
        c.interactive(
            callback = self.terminate_do_head,
            event = event,
            prompts=['Set headline: ',],
        )

    def terminate_do_head(self, args, c, event):
        '''never actually called.'''
    #@+node:ekr.20181210092817.1: *7* app.end_set_headline
    def end_set_headline(self, h):
        c, k, p, u = self.c, self.c.k, self.c.p, self.c.undoer
        w = self.root.main_window
        ### g.trace('-----', p.v.h, '==>', h)
        # Undoably set the head. Like leoTree.onHeadChanged, called LeoTree.endEditLabel.
        oldHead = p.h
        p.v.setHeadString(h)
        ### g.trace(c.rootPosition())
        if True: # was changed:
            undoType = 'Typing'
            undoData = u.beforeChangeNodeContents(p, oldHead=oldHead)
            if not c.changed: c.setChanged(True)
            dirtyVnodeList = p.setDirty()
            u.afterChangeNodeContents(p, undoType, undoData,
                dirtyVnodeList=dirtyVnodeList, inHead=True)
        k.keyboardQuit()
        c.redraw()
        w.body.set_focus()
    #@+node:ekr.20181210054631.1: *6* app.do_redraw
    def do_redraw(self):
        print('testing redraw...')
        self.redraw(None)
    #@+node:ekr.20181210054631.2: *6* app.do_select
    def do_select(self):
        print('testing select...')
        c = self.c
        h = 'Active Unit Tests'
        p = g.findTopLevelNode(c, h, exact=True)
        if p:
            c.frame.tree.select(p)
            # LeoBrowserTree.select.
        else:
            g.trace('not found: %s' % h)
    #@+node:ekr.20181210054516.1: *6* app.do_test
    def do_test(self):
        c = self.c
        w = self.root.main_window
        print('testing positions...')
        self.test_round_trip_positions()
        self.do_select()
        c.k.keyboardQuit()
        c.redraw()
        w.body.set_focus()

    #@+node:ekr.20181210055110.1: *6* app.do_unit
    def do_unit(self):
        # This ends up exiting.
        self.run_all_unit_tests()
    #@+node:ekr.20181127070903.1: *5* app.execute/complete_minibuffer_command
    def execute_minibuffer_command(self, commandName, char, mods):
        '''Start the execution of a minibuffer command.'''
        c = self.c
        w = self.root.main_window
        w.body.sync_before_command({
            'char': char,
            'commandName': commandName,
            'headline': c.p.h, # Debugging.
            'mods': mods,
        })
            
    @flx.action
    def complete_minibuffer_command(self, d):
        '''Called from flx.body.sync_before_command to complete the minibuffer command.'''
        c = self.c
        k, w = c.k, c.frame.body.wrapper
        self.update_body_from_dict(d)
        # Do the minibuffer command: like k.callAltXFunction.
        commandName, char, mods = d['commandName'], d['char'], d['mods']
        binding = '%s%s' % (''.join(['%s+' % (z) for z in mods]), char)
            # Same as in app.do_key.
        event = g.Bunch(
            c=c,
            char=char,
            stroke=binding,
            widget=w, # Use the body pane by default.
        )
            # Another hack.
        k.functionTail = None ### Changed.
        if commandName and commandName.isdigit():
            # The line number Easter Egg.
            def func(event=None):
                c.gotoCommands.find_file_line(n=int(commandName))
        else:
            func = c.commandsDict.get(commandName)
        k.newMinibufferWidget = None
        if func:
            # These must be done *after* getting the command.
            k.clearState()
            k.resetLabel()
            if commandName != 'repeat-complex-command':
                k.mb_history.insert(0, commandName)
            w = event and event.widget
            if hasattr(w, 'permanent') and not w.permanent:
                # In a headline that is being edited.
                # g.es('Can not execute commands from headlines')
                c.endEditing()
                c.bodyWantsFocusNow()
                # Change the event widget so we don't refer to the to-be-deleted headline widget.
                event.w = event.widget = c.frame.body.wrapper.widget
                c.executeAnyCommand(func, event)
            else:
                c.widgetWantsFocusNow(event and event.widget)
                    # Important, so cut-text works, e.g.
                c.executeAnyCommand(func, event)
            k.endCommand(commandName)
            return True
        if 0: ### Not ready yet
            # Show possible completions if the command does not exist.
            if 1: # Useful.
                k.doTabCompletion(list(c.commandsDict.keys()))
            else: # Annoying.
                k.keyboardQuit()
                k.setStatusLabel('Command does not exist: %s' % commandName)
                c.bodyWantsFocus()
        return False
    #@+node:ekr.20181112182636.1: *5* app.run_all_unit_tests
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
            print('app.run_all_unit_tests: select: not found: %s' % h)
    #@+node:ekr.20181126104843.1: *5* app.test_full_outline
    def test_full_outline(self, p):
        '''Exercise the new diff-based redraw code on a fully-expanded outline.'''
        c = self.c
        p = p.copy()
        redrawer = self.fast_redrawer
        # Don't call c.expandAllHeadlines: it calls c.redraw.
        for p2 in c.all_positions(copy=False):
            p2.expand()
        #
        # Test the code.
        self.make_redraw_dict(p)
            # Call this only for timing stats.
        new_flattened_outline = redrawer.flatten_outline(c)
        redraw_instructions = redrawer.make_redraw_list(
            self.old_flattened_outline,
            new_flattened_outline,
        )
        assert redraw_instructions is not None # For pyflakes.
        #
        # Restore the tree.
        for p2 in c.all_positions(copy=False):
            p2.contract()
        c.expandAllAncestors(p)
            # Does not do a redraw.
    #@+node:ekr.20181113180246.1: *5* app.test_round_trip_positions
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
    #@+node:ekr.20181124054536.1: *4* app.Utils
    @flx.action
    def cls(self):
        '''Clear the console'''
        g.cls()

    # def message(self, s):
        # '''For testing.'''
        # print('app.message: %s' % s)
    #@-others
#@+node:ekr.20181115092337.3: *3* class LeoBrowserBody
class LeoBrowserBody(leoFrame.NullBody):
    
    attributes = set()
   
    def __init__(self, frame):
        super().__init__(frame, parentFrame=None)
        self.c = c = frame.c
        self.root = get_root()
        self.tag = '(body wrapper)'
        # Replace the StringTextWrapper with the ace wrapper.
        assert isinstance(self.wrapper, leoFrame.StringTextWrapper)
        self.wrapper = API_Wrapper(c, 'body')
            
    # The Ace Wrapper does almost everything.
    def __getattr__ (self, attr):
        if self.root.inited:
            return getattr(self.wrapper, attr)
        raise AttributeError('app not inited')

    def getName(self):
        return 'body' # Required for proper pane bindings.

#@+node:ekr.20181115092337.6: *3* class LeoBrowserFrame
class LeoBrowserFrame(leoFrame.NullFrame):
    
    def __init__(self, c, title, gui):
        '''Ctor for the LeoBrowserFrame class.'''
        super().__init__(c, title, gui)
        assert self.c == c
        frame = self
        self.root = get_root()
        self.tag = '(frame wrapper)'
        #
        # Instantiate the other wrappers.
        self.body = LeoBrowserBody(frame)
        self.tree = LeoBrowserTree(frame)
        self.log = LeoBrowserLog(frame)
        self.menu = LeoBrowserMenu(frame)
        self.miniBufferWidget = LeoBrowserMinibuffer(c, frame)
        self.iconBar = LeoBrowserIconBar(c, frame)
        self.statusLine = LeoBrowserStatusLine(c, frame)
            # NullFrame does this in createStatusLine.
        self.top = g.NullObject()
            # This is the DynamicWindow object.
            # There is no need to implement its methods now.
        
    def finishCreate(self):
        '''Override NullFrame.finishCreate.'''
        # Do not call self.createFirstTreeNode.

    #@+others
    #@-others
#@+node:ekr.20181113041113.1: *3* class LeoBrowserGui
class LeoBrowserGui(leoGui.NullGui):

    def __init__ (self, gui_name='browser'):
        super().__init__(guiName='browser')
            # leoTest.doTest special-cases the name "browser".
        self.gui_name = gui_name # May specify the actual browser.
        assert gui_name.startswith('browser')
        self.logWaiting = []
        self.root = None # Will be set later.
        self.silentMode = True # Don't print a single signon line.
        self.tag = '(browser gui)'
        self.specific_browser = gui_name.lstrip('browser').lstrip(':').lstrip('-').strip()
        if not self.specific_browser:
            self.specific_browser = 'browser'
        self.consoleOnly = False # Console is separate from the log.
        #
        # Monkey-patch g.app.writeWaitingLog to be a do-nothing.
        # This allows us to write the log much later.
        g.app.writeWaitingLog = self.writeWaitingLog1
        
    def insertKeyEvent(self, event, i):
        '''Insert the key given by event in location i of widget event.w.'''
        # Mysterious...
        assert False, g.callers()

    #@+others
    #@+node:ekr.20181206153033.1: *4* gui.createLeoFrame
    def createLeoFrame(self, c, title):
        '''
        Override NullGui.createLeoFrame.
        
        We can't create a real flx.Frame until much later.
        
        We create a placeholder in g.app.windowList, for app.finish_create.
        '''
        gui = self
        self.lastFrame = DummyFrame(c, title, gui)
        g.app.windowList.append(self.lastFrame)
            # A buglet in Leo's core: this is necessary.
            # LM.doPostPluginsInit tests g.app.windowList, maybe when it shouldn't.
        return self.lastFrame
    #@+node:ekr.20181119141542.1: *4* gui.isTextWrapper
    def isTextWrapper(self, w):
        '''Return True if w is supposedly a text widget.'''
        # isinstance is much more pythonic than using getName.
        if isinstance(w, (
            LeoBrowserBody,
            LeoBrowserLog,
            LeoBrowserMinibuffer,
            # LeoFlexxTreeItem,
                # At present, Leo's core can not edit tree items.
            LeoBrowserStatusLine,
        )):
            return True
        if g.unitTesting and isinstance(w, leoFrame.StringTextWrapper):
            return True
        return False
    #@+node:ekr.20181119153936.1: *4* gui.focus...
    def get_focus(self, *args, **kwargs):
        w = self.focusWidget
        if debug_focus:
            w_tag = w.tag if w else "NO WIDGET"
            print('%s: get_focus: %s %s' % (self.tag, w_tag,  g.callers(2)))
        return w

    def set_focus(self, commander, widget):
        # Be careful during startup.
        if not self.root:
            return
        c = self.root.c
        if isinstance(widget, (
            LeoBrowserBody,
            LeoBrowserFrame,
            LeoBrowserLog,
            LeoBrowserMinibuffer,
            LeoBrowserTree,
        )):
            if 0: print(self.tag, 'set_focus', widget.tag) # debug_events
            if not g.unitTesting:
                widget.setFocus()
            self.focusWidget = widget
        elif isinstance(widget, API_Wrapper):
            # This does sometimes get executed.
            if 0: print('===== gui.set_focus: redirect AceWrapper to LeoBrowserBody', g.callers())
            assert isinstance(c.frame.body, LeoBrowserBody), repr(c.frame.body)
            assert widget.name == 'body', repr(widget.name)
            if not g.unitTesting:
                c.frame.body.setFocus()
        elif not g.unitTesting:
            # This gets called when reloading the page (reopening the .leo file) after Ctrl-F.
            # It also gets called during unit tests.
            g.trace('(gui): unknown widget', repr(widget), g.callers(6))
    #@+node:ekr.20181206090210.1: *4* gui.writeWaitingLog1/2
    def writeWaitingLog1(self, c=None):
        '''Monkey-patched do-nothing version of g.app.writeWaitingLog.'''
        
    def writeWaitingLog2(self, c=None):
        '''Called from app.finish_create.'''
        w = self.root.main_window
        #
        # Print the signon.
        table = [
            ('Leo Log Window', 'red'),
            (g.app.signon, None),
            (g.app.signon1, None),
            (g.app.signon2, None),
        ]
        for message, color in table:
            w.log.put(message.rstrip())
        #
        # Write all the queued log entries.
            # c.setLog()
        g.app.logInited = True # Prevent recursive call.
        for msg in g.app.logWaiting:
            s, color, newline = msg[:3]
            w.log.put(s.rstrip())
        g.app.logWaiting = []
        g.app.setLog(None)
            # Essential when opening multiple files...
    #@+node:ekr.20181202083305.1: *4* gui.runMainLoop
    def runMainLoop(self):
        '''Run the main loop from within Leo's core.'''
        runtime = self.specific_browser or 'webruntime'
        flx.launch(LeoBrowserApp, runtime)
        flx.set_log_level('ERROR') #  'INFO'
        flx.run()
    #@-others
#@+node:ekr.20181115092337.21: *3* class LeoBrowserIconBar
class LeoBrowserIconBar(leoFrame.NullIconBarClass):

    def __init__(self, c, parentFrame):
        super().__init__(c, parentFrame)
        assert self.c == c
        self.root = get_root()
        self.tag = '(icon bar wrapper)'
            
    #@+others
    #@-others
#@+node:ekr.20181115092337.22: *3* class LeoBrowserLog
class LeoBrowserLog(leoFrame.NullLog):
    
    def __init__(self, frame, parentFrame=None):
        super().__init__(frame, parentFrame)
        self.root = get_root()
        self.tag = '(log wrapper)'
        assert isinstance(self.widget, leoFrame.StringTextWrapper)
        self.logCtrl = self.widget
        self.wrapper = self.widget
        #
        # Monkey-patch self.wrapper, a StringTextWrapper.
        assert self.wrapper.getName().startswith('log')
        self.wrapper.setFocus = self.setFocus
        
    def __repr__(self):
        return 'LeoBrowserLog'
        
    __str__ = __repr__
        
    def getName(self):
        return 'log' # Required for proper pane bindings.

    #@+others
    #@+node:ekr.20181120063043.1: *4* log_wrapper.setFocus
    def setFocus(self):
        w = self.root.main_window
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
        # self.tag = '(menu wrapper)'

    # @others
#@+node:ekr.20181115120317.1: *3* class LeoBrowserMinibuffer (StringTextWrapper)
# Leo's core doesn't define a NullMinibuffer class.

class LeoBrowserMinibuffer (leoFrame.StringTextWrapper):
    '''Browser wrapper for minibuffer.'''

    def __init__(self, c, frame):
        super().__init__(c, name='minibuffer')
            # Name must be minibuffer, for gui.isTextWrapper().
        assert self.c == c, repr(self.c)
        # assert c.frame == frame, (repr(c.frame), repr(frame))
            # c.frame is a NullFrame.  frame is a LeoBrowserFrame.
        assert self.widget is None, repr(self.widget)
        assert self.getName() == 'minibuffer'
        self.frame = frame
        self.root = get_root()
        self.tag = '(minibuffer wrapper)'
        self.widget = self
        self.wrapper = self
        # Hook this class up to the key handler.
        c.k.w = self
        frame.minibufferWidget = self

    # Overrides.
    def setFocus(self):
        self.root.main_window.minibuffer.set_focus()

    #@+others
    #@+node:ekr.20181208062449.1: *4* mini.called by k.minibuffer
    # Override the methods called by k.minibuffer:
        
    def update(self, tag):
        w = self.root.main_window
        i, j = self.sel
        # print('===== mini.%-20s sel: %2s %2s ins: %2s %r' % (tag+':', i, j, self.ins, self.s))
        w.minibuffer.set_text(self.s)
        w.minibuffer.set_selection(i, j)
        w.minibuffer.set_insert(self.ins)
            
    def delete(self, i, j=None):
        super().delete(i,j)
        self.update('delete')
        
    def getAllText(self):
        # i, j = self.sel
        # print('===== mini.%-20s sel: %2s %2s ins: %2s %r' % ('getAllText:', i, j, self.ins, self.s))
        return self.s

    def insert(self, i, s):
        super().insert(i, s)
        self.update('insert')

    def setAllText(self, s):
        super().setAllText(s)
        self.update('setAllText')
        
    def setSelectionRange(self, i, j, insert=None):
        super().setSelectionRange(i, j, insert)
        self.update('setSelectionRange')
            
    def setStyleClass(self, name):
        w = self.root.main_window
        w.minibuffer.set_style(name)
        self.update('setStyleClass:%r' % name)
    #@-others
#@+node:ekr.20181115092337.32: *3* class LeoBrowserStatusLine
class LeoBrowserStatusLine(leoFrame.NullStatusLineClass):
    
    def __init__(self, c, parentFrame):
        super().__init__(c, parentFrame)
        self.root = get_root()
        self.tag = '(status line wrapper)'
        self.w = self # Required.
        
    def getName(self):
        return 'status line' # Value not important.
        
    # Pretend that this widget supports the high-level interface.
    def __getattr__(self, attr):
        return g.NullObject()
        
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
        self.root.status_line.set_focus()
    #@+node:ekr.20181119042937.1: *4* status_line_wrapper.update
    def update(self, body_text='', insert_point=0):
        '''
        Update the status line, based on the contents of the body.
        
        Called from LeoTree.select.
        
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
        self.tag = '(tree wrapper)'
        self.widget = self
        self.wrapper = self

    def getName(self):
        return 'canvas(tree)' # Required for proper pane bindings.

    #@+others
    #@+node:ekr.20181116081421.1: *4* tree_wrapper.select, super_select, endEditLabel
    def select(self, p):
        '''Override NullTree.select, which is actually LeoTree.select.'''
        if self.root.inited:
            if debug: print('tree.select: new p: %r' % p.h)
            w = self.root.main_window
            w.body.sync_before_select({
                'ap': self.root.p_to_ap(p),
                'headline': p.h, # Debugging.
            })
                # The callback is self.complete_select.
        else:
            # Don't sync the body pane.
            super().select(p)
                # Call LeoTree.select.'''
            self.root.select_p(p)
                # Call app.select_position.

    def complete_select(self, d):
        self.root.update_body_from_dict(d)
            # Complete the syncing of the body pane.
        p = self.root.ap_to_p(d ['ap'])
        if debug: print('tree.complete_select: p: %r' % (p.h))
        if 0: print('tree.complete_select: d: %r' % (d))
        super().select(p)
            # Call LeoTree.select.'''
        self.root.select_p(p)
            # Call app.select_position.
            
    def select_ap(self, ap): ### New, experimental.
        p = self.root.ap_to_p(ap)
        if debug: print('tree.select_ap: p: %r' % (p))
        self.select(p)

    def super_select(self, p):
        '''Call only LeoTree.select.'''
        super().select(p)

    def endEditLabel(self):
        '''
        End editing.

        This must be a do-nothing, because app.end_set_headline takes its place.
        '''
        # print(self.tag, 'endEditLabel', g.callers())
        
    #@+node:ekr.20181118052203.1: *4* tree_wrapper.redraw
    def redraw(self, p=None):
        '''This is c.frame.tree.redraw!'''
        if 0: print(self.tag, '(c.frame.tree) redraw')
        self.root.redraw(p)
    #@+node:ekr.20181120063844.1: *4* tree_wrapper.setFocus
    def setFocus(self):
        w = self.root.main_window
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
        print('NullObject.__delattr__ %r %s' % (attr, g.callers()))
        return self

    def __getattr__(self, attr):
        print('NullObject.__getattr__ %r %s' % (attr, g.callers()))
        return self

    def __setattr__(self, attr, val):
        print('NullObject.__setattr__ %r %s' % (attr, g.callers()))
        return self
#@+node:ekr.20181107052700.1: ** Js side: flx.Widgets
#@+node:ekr.20181201125953.1: *3* class JS_Editor (flx.Widget)
class JS_Editor(flx.Widget):
    '''
    The base class for the body and log panes.
    '''
    
    def init(self, name, flex=1):
        # pylint: disable=arguments-differ
        assert name in ('body', 'log', 'minibuffer'), repr(name)
        self.name = name
        self.tag = '(flx.%s)' % name
        self.editor = None # Now done in subclasses.

    @flx.reaction('size')
    def __on_size(self, *events):
        self.editor.resize()
    
    #@+others
    #@+node:ekr.20181121072246.1: *4* jse.Keys
    #@+node:ekr.20181215083729.1: *5* jse.key_press & on_key_press
    @flx.emitter
    def key_press(self, e):
        ev = self._create_key_event(e)
        if debug_keys:
            print('JS_Editor.key_press: %s %r' % (self.name, ev))
        if self.should_be_leo_key(ev):
            e.preventDefault()
        return ev

    @flx.reaction('key_press')
    def on_key_press(self, *events):
        # The JS editor has already** handled the key!
        for ev in events:
            if self.should_be_leo_key(ev):
                ivar = 'minibufferWidget' if self.name == 'minibuffer' else self.name
                self.root.do_key(ev, ivar)
    #@+node:ekr.20181201081444.1: *5* jse.should_be_leo_key
    def should_be_leo_key(self, ev):
        '''
        Return True if Leo should handle the key.
        Leo handles only modified keys, not F-keys or plain keys.
        '''
        key, mods, tag = ev['key'], ev['modifiers'], 'JSE.should_be_leo_key:'
        #
        # The widget handles F-keys.
        if not mods and key.startswith('F'):
            if 0: print(tag, 'Send F-Keys to body', repr(mods), repr(key))
            return False
        mods2 = mods
        if 'Shift' in mods2:
            mods2.remove('Shift')
        #
        # Send only Ctrl-Arrow keys to body.
        if mods2 == ['Ctrl'] and key in ('RtArrow', 'LtArrow', 'UpArrow', 'DownArrow'):
            # This never fires: Neither editor widget emis Ctrl/Arrow keys or Alt-Arrow keys.
            if 0: print(tag, 'Arrow key: send to to body', repr(mods), repr(key))
            return False
        #
        # Leo should handle all other modified keys.
        if mods2:
            if 0: print(tag, '  modified: send to Leo', repr(mods), repr(key))
        else:
            if 0: print(tag, 'unmodified: send to Body', repr(mods), repr(key))
        return mods
    #@+node:ekr.20181215083642.1: *4* jse.focus
    @flx.action
    def see_insert_point(self):
        if 0: print(self.tag, 'see_insert_point')
        
    @flx.action
    def set_focus(self):
        if debug_focus: print(self.tag, 'set_focus')
        self.editor.focus()
    #@+node:ekr.20181215061810.1: *4* jse.text getters
    def get_ins(self):
        d = self.editor.selection.getCursor()
        row, col = d ['row'], d['column']
        if 0: print('%s: get_ins: row: %s col: %s' % (self.tag, row, col))
        return row, col
        
    def get_sel(self):
        selections = self.editor.selection.getAllRanges()
        if selections:
            sel = selections[0]
            d1, d2 = sel ['start'], sel ['end']
            row1, col1 = d1 ['row'], d1 ['column']
            row2, col2 = d2 ['row'], d2 ['column']
        else:
            print('%s: get_sel: NO SELECTION' % self.tag)
            i = self.get_ins()
            row1 = col1 = row2 = col2 = i
        if 0: print('%s: get_sel: (%s, %s) to (%s, %s)' % (self.tag, row1, col1, row2, col2))
        return row1, col1, row2, col2
        
    def get_text(self):
        editor = self.editor
        s = editor.getValue()
        if 0: print('%s: get_text: %s' % (self.tag, len(s)))
        return s
    #@+node:ekr.20181128061524.1: *4* jse.text setters
    @flx.action
    def insert(self, s):
        if 0: print(self.tag, 'insert', repr(s))
        self.editor.insert(s)

    @flx.action
    def select_all_text(self):
        if 0: print(self.tag, 'select_all_text')

    @flx.action
    def set_insert_point(self, insert, sel):
        s = self.editor.getValue()
        row, col = g.convertPythonIndexToRowCol(s, insert)
        row = max(0, row-1)
        if 0:
            print('%s: set_insert_point: i: %s = (%s, %s)' % (
                self.tag, str(insert).ljust(3), row, col))
        self.editor.moveCursorTo(row, col)

    @flx.action
    def set_selection_range(self, i, j):
        print(self.tag, 'set_selection_range: NOT READY', i, j)

    @flx.action
    def set_text(self, s):
        '''Set the entire text'''
        if 0: print('%s: set_text: len(s): %s' % (self.tag, len(s)))
        self.editor.setValue(s)
    #@-others
#@+node:ekr.20181104082144.1: *3* class LeoFlexxBody (JS_Editor)
class LeoFlexxBody(JS_Editor):
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

    def init(self):
        # pylint: disable=arguments-differ
        super().init('body')
        self.editor = make_editor_function(self.name, self.node)

    #@+others
    #@+node:ekr.20181215061402.1: *4* flx_body.sync_before_command/select
    @flx.action
    def sync_before_command(self, d):
        '''Update p.b, etc. before executing a minibuffer command..'''
        if debug: print('flx_body.sync_before_command')
        self.update_body_dict(d)
        self.root.complete_minibuffer_command(d)
        
    @flx.action
    def sync_before_select(self, d):
        '''Update p.b, etc. before selecting a new node.'''
        if debug: print('===== flx_body.sync_before_select')
        self.update_body_dict(d)
        self.root.complete_select(d)
        
    def update_body_dict(self, d):
        '''Add keys to d describing the body pane.'''
        d ['s'] = self.get_text()
        d ['ins_row'], d ['ins_col'] = self.get_ins()
        row1, col1, row2, col2 = self.get_sel()
        d ['sel_row1'], d ['sel_col1'] = row1, col1
        d ['sel_row2'], d ['sel_col2'] = row2, col2
    #@-others
#@+node:ekr.20181104082149.1: *3* class LeoFlexxLog (JS_Editor)
class LeoFlexxLog(JS_Editor):
    
    #@+<< log css >>
    #@+node:ekr.20181120060336.1: *4* << log css >>
    CSS = """
    .flx-CodeEditor > .ace {
        width: 100%;
        height: 100%;
    }
    """
    #@-<< log css >>
    
    def init(self):
        # pylint: disable=arguments-differ
        super().init('log')
        self.editor = make_editor_function(self.name, self.node)

    #@+others
    #@+node:ekr.20181120060348.1: *4* flx.log.put & set_focus
    @flx.action
    def put(self, s):
        prev = self.editor.getValue()
        if prev:
            self.editor.setValue(prev + '\n' + s)
        else:
            self.editor.setValue(s)
        
    @flx.action
    def set_focus(self):
        if debug_focus:
            print(self.tag, 'ace.focus()')
        self.editor.focus()
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

    def init(self):
        self.tag = '(flx main window)'
        ### with flx.TabLayout():
        with flx.VSplit():
            with flx.HSplit(flex=1):
                tree = LeoFlexxTree(flex=1)
                log = LeoFlexxLog(flex=1)
            body = LeoFlexxBody(flex=1)
            minibuffer = LeoFlexxMiniBuffer()
            status_line = LeoFlexxStatusLine()
        #@+<< define unload action >>
        #@+node:ekr.20181206044554.1: *4* << define unload action >>
        if is_public:
            RawJS("""\
            // Called from Mozilla, but not webruntime.
            window.onbeforeunload = function(){
                // console.log("window.onbeforeunload")
                return "Are you sure?"
            };
            """)
        #@-<< define unload action >>
        self._mutate('body', body)
        self._mutate('log', log)
        self._mutate('minibuffer', minibuffer)
        self._mutate('status_line', status_line)
        self._mutate('tree', tree)
        self.emit('do_init')
        if is_public:
            global alert # for pyflakes.
            # pylint: disable=undefined-variable
            alert('Use LeoWapp at your own risk')
        
    @flx.reaction('!do_init')
    def after_init(self):
        self.root.finish_create()

    #@+others
    #@-others
#@+node:ekr.20181104082154.1: *3* class LeoFlexxMiniBuffer (JS_Editor)
class MinibufferEditor(flx.Widget):

    def init(self):
        self.editor = make_editor_function('minibuffer', self.node)
            # Unlike in components, this call happens immediately.

class LeoFlexxMiniBuffer(JS_Editor):
    
    def init(self):
        # pylint: disable=arguments-differ
        super().init('minibuffer')
        with flx.HBox():
            flx.Label(text='Minibuffer')
            w = MinibufferEditor(flex=1)
            self.editor = w.editor

    #@+others
    #@+node:ekr.20181127060810.1: *4* flx_minibuffer.high-level interface
    # The high-level interface methods, called from LeoBrowserMinibuffer.

    @flx.action
    def set_focus(self):
        if 0: print('===== flx.mini.set_focus')
        self.editor.focus()
        
    @flx.action
    def set_insert(self, i):
        if 0: print('===== flx.mini.set_insert', i)

    @flx.action
    def set_selection(self, i, j):
        if 0: print('===== flx.mini.set_selection', i, j)
        
    @flx.action
    def set_style(self, style):
        if 0: print('===== flx.mini.set_style: %r %r' % (style, self.editor.getValue()))
        # A hack. Also set focus.
        self.editor.focus()
        
    @flx.action
    def set_text(self, s):
        if 0: print('===== flx.minibuffer.set_text', repr(s))
        self.editor.setValue(s)
    #@+node:ekr.20181203150409.1: *4* flx_minibuffer.Key handling
    if 0: ### Reference only.

        RawJS("""\
    window.onbeforeunload = function(){
        // console.log("window.onbeforeunload")
        return "Are you sure?"
    };""")


    @flx.emitter
    def key_press(self, e):
        '''Pass *all* keys except Enter and F12 to Leo's core.'''
        # Backspace is not emitted.
        ev = self._create_key_event(e)
        key, mods = ev ['key'], ev ['modifiers']
        if debug_keys:
            print('mini.key_press: %r %r' % (mods, key))
        if mods:
            e.preventDefault()
            return ev
        if key == 'F12':
            return ev
        if key == 'Enter':
            self.do_enter_key(key, mods)
            e.preventDefault()
            return None ###
        # k.masterKeyHandler will handle everything.
        e.preventDefault()
        return ev
        
    @flx.reaction('key_press')
    def on_key_press(self, *events):
        '''Pass *all* keys Leo's core.'''
        for ev in events:
            if debug_keys:
                print('mini.on_key_press: %r %r' % (ev ['modifiers'], ev['key']))
            self.root.do_key(ev, 'minibufferWidget')
    #@+node:ekr.20181129174405.1: *4* flx_minibuffer.do_enter_key
    def do_enter_key(self, key, mods):
        '''
        Handle the enter key in the minibuffer.
        This will only be called if the user has entered the minibuffer via a click.
        '''
        command = self.editor.getValue()
        if debug_keys:
            print('mini.do_enter_key', repr(command))
        if command.strip():
            if command.startswith('full-command:'):
                command = command[len('full-command:'):].strip()
                self.root.do_command(command, 'Enter', [])
            elif command.startswith('Enter Headline:'):
                headline = command[len('Enter Headline:'):].strip()
                self.root.edit_headline_completer(headline)
            else:
                self.root.do_command(command, key, mods)
    #@-others
#@+node:ekr.20181104082201.1: *3* class LeoFlexxStatusLine
class LeoFlexxStatusLine(flx.Widget):
    
    def init(self):
        self.tag = '(flx status line)'
        with flx.HBox():
            flx.Label(text='Status Line')
            self.widget = flx.LineEdit(flex=1)
            self.widget2 = flx.LineEdit(flex=1)
        self.widget.apply_style('background: green')
        self.widget2.apply_style('background: green')

    #@+others
    #@+node:ekr.20181123043015.1: *4* flx.status_line.action.update
    @flx.action
    def update(self, lt, rt):
        self.put(lt)
        self.put2(rt)
    #@+node:ekr.20181120060957.1: *4* flx_status_line.action.put & put2
    @flx.action
    def put(self, s, bg=None, fg=None):
        self.widget.set_text(s)
        
    @flx.action
    def put2(self, s, bg=None, fg=None):
        self.widget2.set_text(s)
    #@+node:ekr.20181120060950.1: *4* flx_status_line.Key handling
    @flx.emitter
    def key_press(self, e):
        '''Allow only F-keys, Ctrl-C and Ctrl-S.'''
        ev = self._create_key_event(e)
        key, mods = ev['key'], ev ['modifiers']
        print('flx.status_line:', repr(mods), repr(key))
        if not mods and key.startswith('F'):
            return ev
        if mods == ['Ctrl'] and key in 'cs':
            # We don't always get Ctrl-S from the browser.
            return ev
        # Prevent everything else.
        e.preventDefault()
        return ev

    @flx.reaction('key_press')
    def on_key_press(self, *events):
        '''Pass Ctrl-S to Leo.'''
        for ev in events:
            key, mods = ev['key'], ev ['modifiers']
            if mods == ['Ctrl'] and key == 's':
                self.root.do_key(ev, 'statusLine')
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

    def init(self):
        self.widget = self
        self.wrapper = self
        self.tag = '(flx tree)'
        # Init local ivars...
        self.populated_items_dict = {}
            # Keys are ap **keys**, values are True.
        self.populating_tree_item = None
            # The LeoTreeItem whose children are to be populated.
        self.selected_ap = {}
            # The ap of the presently selected node.
        self.tree_items_dict = {}
            # Keys are ap's. Values are LeoTreeItems.
        # Init the widget.
        self.tree = flx.TreeWidget(flex=1, max_selected=1)
            # The max_selected property does not seem to work.

    def assert_exists(self, obj):
        # pylint: disable=undefined-variable
            # undefined
        global undefined
        assert obj not in (undefined, None, {}), repr(obj)

    #@+others
    #@+node:ekr.20181121073246.1: *4* flx_tree.Drawing...
    #@+node:ekr.20181112163252.1: *5* flx_tree.action.clear_tree
    @flx.action
    def clear_tree(self):
        '''
        Completely clear the tree, preparing to recreate it.
        
        Important: we do *not* clear self.tree itself!
        '''
        # pylint: disable=access-member-before-definition
        items = list(self.tree_items_dict.values())
        if 0: print('===== flx.tree.clear_tree: %s items' % (len(items)))
        # Clear all tree items.
        for item in items:
            # print(repr(item))
            item.dispose()
        self.tree_items_dict = {}
    #@+node:ekr.20181113043004.1: *5* flx_tree.action.redraw_with_dict & helper
    @flx.action
    def redraw_with_dict(self, redraw_dict, redraw_instructions):
        '''
        Clear the present tree and redraw using the **recursive** redraw_list.
        d has the form:
            {
                'c.p': self.p_to_ap(p),
                'items': [
                    self.make_dict_for_position(p)
                        for p in c.rootPosition().self_and_siblings()
                ],
            }
        '''
        tag = '%s: redraw_with_dict' % self.tag
        assert redraw_dict
        self.clear_tree()
        items = redraw_dict ['items']
        if 0: print('%s: %s direct children' % (tag, len(items))) # debug_redraw
        for item in items:
            if 0: print('  item', repr(item['headline']))
            self.create_item_with_parent(item, self.tree)
        #
        # Select c.p.
        self.select_ap(redraw_dict['c.p'])
    #@+node:ekr.20181124194248.1: *6* tree.create_item_with_parent
    def create_item_with_parent(self, item, parent):
        '''Create a tree item for item and all its visible children.'''
        # pylint: disable=no-member
            # set_collapsed is in the base class.
        ap = item ['ap']
        if 0: print('%s%s' % ('  '*ap ['level'], ap['headline'])) # debug_tree: lengthy.
        #
        # Create the node.
        with parent:
            tree_item = LeoFlexxTreeItem(ap, text=ap['headline'], checked=None, collapsed=True)
        tree_item.set_collapsed(not ap['expanded'])
        #
        # Set the data.
        key = self.ap_to_key(ap)
        self.tree_items_dict [key] = tree_item
        # Children are *not* necessarily sent, so set the populated 'bit' only if they are.
        if item['children']:
            if 0: print('create_item_with_parent: **populated**', ap['headline'])
            self.populated_items_dict[key] = True
        if hasattr(parent, 'leo_children'):
            # print('create_item_with_parent', parent.leo_ap['headline'], ap['headline'])
            parent.leo_children.append(tree_item)
        #
        # Create the children.
        for child in item ['children']:
            self.create_item_with_parent(child, tree_item)
    #@+node:ekr.20181114072307.1: *5* flx_tree.ap_to_key
    def ap_to_key(self, ap):
        '''Produce a key for the given ap.'''
        self.assert_exists(ap)
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
        return key
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
    #@+node:ekr.20181104080854.3: *5* flx_tree.reaction: on_tree_event
    # actions: set_checked, set_collapsed, set_parent, set_selected, set_text, set_visible
    @flx.reaction(
        'tree.children**.checked',
        'tree.children**.collapsed',
        'tree.children**.visible', # Never seems to fire.
    )
    def on_tree_event(self, *events):
        for ev in events:
            expand = not ev.new_value
            if expand:
                # Don't redraw if the LeoTreeItem has children.
                tree_item = ev.source
                ap = tree_item.leo_ap
                if ap['expanded']:
                    if 0: print('===== flx.tree.on_tree_event: already expanded', ap['headline'])
                else:
                    ap['expanded'] = True
                    ### self.root.expand_and_redraw(ap)
                    self.start_populating_children(ap, tree_item)
                    # Populate children, if necessary.
    #@+node:ekr.20181120063735.1: *4* flx_tree.Focus
    @flx.action
    def set_focus(self):
        if debug_focus:
            print(self.tag, 'self.node.ace.focus()')
        self.node.focus()
    #@+node:ekr.20181123165819.1: *4* flx_tree.Incremental Drawing...
    # This are not used, at present, but they may come back.
    #@+node:ekr.20181125051244.1: *5* flx_tree.populate_children
    def populate_children(self, children, parent_ap):
        '''
        Populate the children of the given parent.
        
        self.populating_tree_item is the LeoFlexxTreeItem to be populated.

        children is a list of ap's.
        '''
        parent = self.populating_tree_item
        assert parent
        assert parent_ap == parent.leo_ap
            # The expansion bit may have changed?
        if 0: print('flx.tree.populate_children: parent: %r %s children' % (
            parent, len(children))) # debug_tree.
        for child_ap in children:
            self.create_item_with_parent(child_ap, parent)
        self.populating_tree_item = False
    #@+node:ekr.20181111011928.1: *5* flx_tree.start_populating_children
    def start_populating_children(self, parent_ap, parent_tree_item):
        '''
        Populate the parent tree item with the children if necessary.
        
        app.send_children_to_tree should send an empty list
        '''
        self.assert_exists(parent_ap)
        self.assert_exists(parent_tree_item)
        key = self.ap_to_key(parent_ap)
        if key in self.populated_items_dict:
            # print('%s: already populated: %s' % (tag, headline))
            return
        assert isinstance(parent_tree_item, LeoFlexxTreeItem)
        # Remember the parent_tree_item.
        self.populating_tree_item = parent_tree_item
        #
        # Ask for the items.
        self.root.send_children_to_tree(parent_ap)
    #@+node:ekr.20181110175222.1: *5* flx_tree.action.receive_children
    @flx.action
    def receive_children(self, d):
        '''
        Populate the direct descendants of ap. d is compatible with make_redraw_dict:
            {
                'parent_ap': parent_ap,
                'items': [
                    self.make_dict_for_position(p)
                        for p in for p in p.children()
                ],
            }
        '''
        parent_ap = d ['parent_ap']
        children = d ['items']
        if 0: print('===== flx.tree.receive_children: %s children' % (len(children))) # debug_tree.
        self.populate_children(children, parent_ap)
    #@+node:ekr.20181120061140.1: *4* flx_tree.Key handling
    @flx.emitter
    def key_press(self, e):
        ev = self._create_key_event(e)
        f_key = not ev['modifiers'] and ev['key'].startswith('F')
        if debug_keys:
            print('flx.TREE: key_press: %r preventDefault: %s', (ev, not f_key))
        if not f_key:
            e.preventDefault()
        return ev

    @flx.reaction('tree.key_press')
    def on_key_press(self, *events):
        if 0: print('flx.TREE.key_press')
        for ev in events:
            self.root.do_key(ev, 'tree')
    #@+node:ekr.20181121195235.1: *4* flx_tree.Selecting...
    #@+node:ekr.20181123171958.1: *5* flx_tree.action.set_ap
    # This must exist so app.select_p can call it.

    @flx.action
    def set_ap(self, ap):
        '''self.selected_ap. Called from app.select_ap.'''
        assert ap
        self.selected_ap = ap
        self.select_ap(self.selected_ap)
    #@+node:ekr.20181116083916.1: *5* flx_tree.select_ap
    @flx.action
    def select_ap(self, ap):
        '''
        Select the tree item corresponding to the given ap.
        
        Called from the mutator, and also on_selected_event.
        '''
        # print('===== flx.tree.select_ap', repr(ap), ap ['headline'])
        key = self.ap_to_key(ap)
        item = self.tree_items_dict.get(key)
        if item:
            item.set_selected(True)
            self.selected_ap = ap
                # Set the item's selected property.
        else:
            pass # We may be in the middle of a redraw.
    #@+node:ekr.20181109083659.1: *5* flx_tree.reaction.on_selected_event
    @flx.reaction('tree.children**.selected') # don't use mode="greedy" here!
    def on_selected_event(self, *events):
        '''
        Update c.p and c.p.b when the user selects a new tree node.
        
        This also gets fired on *unselection* events, which causes problems.
        '''
        #
        # Reselect the present ap if there are no selection events.
        # This ensures that clicking a headline twice has no effect.
        if not any([ev.new_value for ev in events]):
            ev = events[0]
            self.assert_exists(ev)
            ap = ev.source.leo_ap
            self.assert_exists(ap)
            self.select_ap(ap)
            return
        #
        # handle selection events.
        for ev in events:
            if ev.new_value: # A selection event.
                ap = ev.source.leo_ap
                if debug: print('===== on_selected_event: select:', ap['headline'])
                # self.dump_ap(ap)
                if 1:
                    self.select_ap(ap)
                        # Selects the corresponding LeoTreeItem.
                    self.set_ap(ap)
                        # Sets self.selected_ap.
                    self.root.select_tree_using_ap(ap)
                        ### New: calls tree.select.
                    if 0: ### should not be needed???
                        self.root.set_body_text()
                            # Update the body text.
                        self.root.set_status()
                            # Update the status line.
                else:
                    self.root.select_ap(ap)
                        # This *only* sets c.p. and updated c.p.b.
                    self.select_ap(ap)
                        # Selects the corresponding LeoTreeItem.
                    self.set_ap(ap)
                        # Sets self.selected_ap.
                    self.root.set_body_text()
                        # Update the body text.
                    self.root.set_status()
                        # Update the status line.
    #@-others
#@+node:ekr.20181108233657.1: *3* class LeoFlexxTreeItem
class LeoFlexxTreeItem(flx.TreeItem):

    def init(self, leo_ap):
        # pylint: disable=arguments-differ
        self.leo_ap = leo_ap
            # Immutable: Gives access to cloned, marked, expanded fields.
        self.leo_children = []

    def getName(self):
        return 'head' # Required, for proper pane bindings.

    #@+others
    #@-others
#@-others
if __name__ == '__main__':
    #
    # Stand-alone mode.
    # gui.runMainLoop executes similar code when using --gui=browser.
    flx.launch(LeoBrowserApp)
    flx.set_log_level('ERROR')
    flx.run()
#@-leo

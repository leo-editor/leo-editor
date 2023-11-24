#@+leo-ver=5-thin
#@+node:ekr.20181103094900.1: * @file ../plugins/leoflexx.py

# Disable mypy checking.
# type:ignore

#@@language python
#@@tabwidth -4
#@+<< leoflexx: docstring >>
#@+node:ekr.20181122215342.1: ** << leoflexx: docstring >>
#@@language md
#@@wrap
"""
flexx.py: LeoWapp (Leo as a web browser), implemented using flexx:
https://flexx.readthedocs.io/en/stable/

Start Leo using the --gui=browser option. Like this::

    leo --gui=browser
    leo --gui=browser-firefox

This file is the main line of the LeoWapp project.
https://github.com/leo-editor/leo-editor/issues/1005.

See #1005 for a status report and list of to-do's.

# Prerequisites

Install flexx: https://flexx.readthedocs.io/en/stable/start.html

# What you should see

You should see the flexx (Tornado) server start up in the console.
Something that looks like Leo should then appear in the browser. Everything
you see is real, and most of it is "live".
"""
#@-<< leoflexx: docstring >>
#@+<< leoflexx: imports >>
#@+node:ekr.20181113041314.1: ** << leoflexx: imports >>
import os
import re
import sys
import time
from typing import Optional

path = os.getcwd()
if path not in sys.path:
    sys.path.insert(0, path)
del path

# pylint: disable=wrong-import-position

# This is what Leo typically does.
# JS code can *not* use g.trace, g.callers or g.pdb.
from leo.core import leoGlobals as g
from leo.core import leoFastRedraw
from leo.core import leoFrame
from leo.core import leoGui
from leo.core import leoMenu
from leo.core import leoNodes
# Third-party imports.
try:
    # pylint: disable=import-error
    from flexx import flx
    from pscript import RawJS
except Exception:
    flx = None
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
# pylint: disable=logging-not-lazy,unused-private-member

# flexx can't handle generators, so we *must* use comprehensions instead.
# pylint: disable=use-a-generator

#@+others
#@+node:ekr.20181121040901.1: **  top-level functions
#@+node:ekr.20181121091633.1: *3* dump_event
def dump_event(ev):
    """Print a description of the event."""
    id_ = ev.source.title or ev.source.text
    kind = '' if ev.new_value else 'un-'
    s = kind + ev.type
    message = '%s: %s' % (s.rjust(15), id_)
    print('dump_event: ' + message)
#@+node:ekr.20181121040857.1: *3* get_root
def get_root():
    """
    Return the LeoBrowserApp instance.

    This is the same as self.root for any flx.Component.
    """
    # Only called at startup, so this will never be None.
    root = flx.loop.get_active_component().root
    assert isinstance(root, LeoBrowserApp), repr(root)
    return root
#@+node:ekr.20181112165240.1: *3* info (deprecated)
def info(s):
    """Send the string s to the flex logger, at level info."""
    if not isinstance(s, str):
        s = repr(s)
    # A hack: automatically add the "Leo" prefix so
    # the top-level suppression logic will not delete this message.
    flx.logger.info('Leo: ' + s)
#@+node:ekr.20181103151350.1: *3* init
def init():
    return flx
#@+node:ekr.20181203151314.1: *3* make_editor_function
def make_editor_function(name, node):
    """
    Instantiate the ace editor.

    Making this a top-level function avoids the need to create a common
    base class that only defines this as a method.
    """
    # pylint: disable=undefined-variable
        # window looks undefined.
    global window
    ace = window.ace.edit(node, 'editor')
    ace.navigateFileEnd()  # otherwise all lines highlighted
    ace.setTheme("ace/theme/solarized_dark")
    if name == 'body':
        ace.getSession().setMode("ace/mode/python")  # This sets soft tabs.
    if name == 'minibuffer':
        pass  # To do: Disable line numbers.
    return ace
#@+node:ekr.20181113041410.1: *3* suppress_unwanted_log_messages (not used)
def suppress_unwanted_log_messages():
    """
    Suppress the "Automatically scrolling cursor into view" messages by
    *allowing* only important messages.
    """
    allowed = r'(Traceback|Critical|Error|Leo|Session|Starting|Stopping|Warning)'
    pattern = re.compile(allowed, re.IGNORECASE)
    flx.set_log_level('INFO', pattern)
#@+node:ekr.20181115071559.1: ** Py side: App & wrapper classes
#@+node:ekr.20181127151027.1: *3* class API_Wrapper (StringTextWrapper)
class API_Wrapper(leoFrame.StringTextWrapper):
    """
    A wrapper class that implements the high-level interface.
    """

    def __init__(self, c, name):
        assert name in ('body', 'log', 'minibuffer'), repr(name)
        super().__init__(c, name)
        assert self.c == c
        assert self.name == name
        self.tag = 'py.%s.wrap' % name
        self.root = get_root()

    def flx_wrapper(self):
        if self.root.inited:
            w = self.root.main_window
            return getattr(w, self.name)
        return g.NullObject()

    def setFocus(self):
        # print(self.tag, 'setFocus')
        self.flx_wrapper().set_focus()

    # No need to override getters.
    #@+others
    #@+node:ekr.20181128101421.1: *4* API_Wrapper.Selection Setters
    def finish_set_insert(self, tag):
        """Common helper for selection setters."""
        if 'select' in g.app.debug:
            tag = '%s.%s' % (self.tag, 'finish_set_insert')
            print('%30s: %s %r' % (tag, self.ins, self.sel))
        self.flx_wrapper().set_insert_point(self.ins, self.sel)

    def seeInsertPoint(self):
        self.flx_wrapper().see_insert_point()

    def selectAllText(self, insert=None):
        super().selectAllText(insert)
        self.finish_set_insert('selectAllText')

    def setInsertPoint(self, pos, s=None):
        super().setInsertPoint(pos, s)
        self.finish_set_insert('setInsertPoint')

    def setSelectionRange(self, i: int, j: int, insert: Optional[int] = None):
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
        """The common setter code."""
        c = self.c
        tag = 'py.body.setter'
        if self.name == 'body':
            # print('%s: %s' % (tag, len(self.s)))
            # p.b = self.s will cause an unbounded recursion.
            c.p.v.setBodyString(self.s)
        if 0:
            print('%s: %s:  len(self.s): %s ins: %s sel: %r' % (
                self.tag, tag, len(self.s), self.ins, self.sel))
        if not g.unitTesting:
            self.flx_wrapper().set_text(self.s)
            self.flx_wrapper().set_insert_point(self.ins)

    def appendText(self, s):
        super().appendText(s)
        self.finish_setter('appendText')

    def delete(self, i: int, j: Optional[int] = None):
        super().delete(i, j)
        self.finish_setter('delete')

    def deleteTextSelection(self):
        super().deleteTextSelection()
        self.finish_setter('deleteTextSelection')

    def insert(self, i: int, s):
        # Called from doPlainChar, insertNewlineHelper, etc. on every keystroke.
        super().insert(i, s)
        self.finish_setter('insert')

    def setAllText(self, s):
        # Called by set_body_text_after_select.
        super().setAllText(s)
        self.finish_setter('insert')
    #@-others
#@+node:ekr.20181206153831.1: *3* class DummyFrame
class DummyFrame(leoFrame.NullFrame):
    """
    A frame to keep Leo's core happy until we can call app.finish_create.
    """

    def __repr__(self):
        return 'DummyFrame: %r' % self.c.shortFileName()

    __str__ = __repr__

#@+node:ekr.20181107052522.1: *3* class LeoBrowserApp
# pscript never converts flx.PyComponents to JS.

class LeoBrowserApp(flx.PyComponent):
    """
    The browser component of Leo in the browser.

    This is self.root for all flexx components.

    This is *not* g.app.
    """

    main_window = flx.ComponentProp(settable=True)

    #@+others
    #@+node:ekr.20181126103604.1: *4*  app.Initing
    #@+node:ekr.20181114015356.1: *5* app.create_all_data
    def create_gnx_to_vnode(self):
        t1 = time.process_time()
        # This is likely the only data that ever will be needed.
        self.gnx_to_vnode = {v.gnx: v for v in self.c.all_unique_nodes()}
        if 0:
            print('app.create_all_data: %5.3f sec. %s entries' % (
                (time.process_time() - t1), len(list(self.gnx_to_vnode.keys()))))
        self.test_round_trip_positions()
    #@+node:ekr.20181124133513.1: *5* app.finish_create
    @flx.action
    def finish_create(self):
        """
        Initialize all ivars and widgets.

        Called after all flx.Widgets have been fully inited!
        """
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
        c.selectPosition(c.p or c.rootPosition())
        c.contractAllHeadlines()
        c.redraw()  # 2380.
        #
        # Monkey-patch the FindTabManager
        c.findCommands.minibuffer_mode = True
        c.findCommands.ftm = g.NullObject()
        #
        # Monkey-patch c.request_focus
        self.old_request_focus = c.request_focus
        c.request_focus = self.request_focus
        #
        # #1143: monkey-patch Leo's save commands.
        self.old_save_file = c.fileCommands.save
        c.fileCommands.save = self.save_file
        self.old_save_file_as = c.fileCommands.saveAs
        c.fileCommands.saveAs = self.save_file_as
        self.old_save_file_to = c.fileCommands.saveTo
        c.fileCommands.saveTo = self.save_file_to
        #
        # Init the log, body, status line and tree.
        g.app.gui.writeWaitingLog2()
        self.set_body_text()
        self.set_status()
        #
        # Init the focus. It's debatable...
        if 0:
            self.gui.set_focus(c, c.frame.tree)
            w.tree.set_focus()
        else:  # This definitely shows focus in the editor.
            self.gui.set_focus(c, c.frame.body)
            w.body.set_focus()
        # Set the inited flag *last*.
        self.inited = True
    #@+node:ekr.20181216042806.1: *5* app.init (leoflexx.py)
    def init(self):
        # Set the ivars.
        global g  # Always use the imported g.
        self.inited = False  # Set in finish_create
        self.tag = 'py.app.wrap'
        # Open or get the first file.
        if not g.app:
            print('app.init: no g.app. g:', repr(g))
            return
        if not isinstance(g.app.gui, LeoBrowserGui):
            print('app.init: wrong g.app.gui:', repr(g.app.gui))
            return
        if not isinstance(g.app.log, leoFrame.NullLog):
            # This can happen in strange situations.
            # print('app.init: ===== Ctrl-H ===== ?')
            return
        # We are running with --gui=browser.
        c = g.app.log.c
        # self.gui must be a synonym for g.app.gui.
        self.c = c
        self.gui = gui = g.app.gui
        # Make sure everything is as expected.
        assert self.c and c == self.c
        assert g.app.gui.guiName() == 'browser'
        # When running from Leo's core, we must wait until now to set LeoBrowserGui.root.
        gui.root = get_root()
        # Check g.app.ivars.
        assert g.app.windowList
        for frame in g.app.windowList:
            assert isinstance(frame, DummyFrame), repr(frame)
        # Instantiate all wrappers here, not in app.finish_create.
        title = c.computeWindowTitle()
        c.frame = gui.lastFrame = LeoBrowserFrame(c, title, gui)
        # The main window will be created (much) later.
        main_window = LeoFlexxMainWindow()
        self._mutate('main_window', main_window)
    #@+node:ekr.20190507110902.1: *4* app.action.cls
    @flx.action
    def cls(self):
        """Clear the console"""
        g.cls()
    #@+node:ekr.20181117163223.1: *4* app.action.do_key
    # https://flexx.readthedocs.io/en/stable/ui/widget.html#flexx.ui.Widget.key_down
    # See Widget._create_key_event in flexx/ui/_widget.py:

    @flx.action
    def do_key(self, ev, ivar):
        """
        LeoBrowserApp.do_key: The central key handler.

        Will be called *in addition* to any inner key handlers,
        unless the inner key handler calls e.preventDefault()
        """
        if 'keys' in g.app.debug:
            g.trace(ev, ivar)
        c = self.c
        # Essential: there is no way to pass the actual wrapper.
        browser_wrapper = getattr(c.frame, ivar)
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
        # ev is a dict, keys are type, source, key, modifiers
        # mods in ('Alt', 'Shift', 'Ctrl', 'Meta')
        key, mods = ev['key'], ev['modifiers']
        # Special case Ctrl-H and Ctrl-F.
        if mods == ['Ctrl'] and key in 'fh':
            command = 'find' if key == 'f' else 'head'
            self.do_command(command, key, mods)
            return
        #@+<< set char to the translated key name >>
        #@+node:ekr.20181129073905.1: *5* << set char to the translated key name >>
        d = {
            'ArrowDown': 'Down',
            'ArrowLeft': 'Left',
            'ArrowRight': 'Right',
            'ArrowUp': 'Up',
            'Enter': '\n',  # For k.fullCommand, etc.
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
                char=char,
                binding=binding,
                event={'c': c},
                w=browser_wrapper,
            )
        finally:
            g.app.debug = old_debug
        #@-<< create key_event >>
        c.k.masterKeyHandler(key_event)
    #@+node:ekr.20181124054536.1: *4* app.action.dump_dict
    @flx.action
    def dump_dict(self, obj, tag):
        # Note: flexx has problems with keyword args.
        g.printObj(obj, tag=tag)

    # def message(self, s):
        # """For testing."""
        # print('app.message: %s' % s)
    #@+node:ekr.20181207080933.1: *4* app.action.set_body_text & set_status
    # These must be separate because they are called from the tree logic.

    @flx.action
    def set_body_text(self):
        c = self.c
        # Using the wrapper sets the text *and* the insert point and selection range.
        c.frame.body.wrapper.setAllText(c.p.b)
        # print('app.set_body_text', len(c.p.b), c.p.h)

    @flx.action
    def set_status(self):
        c, w = self.c, self.main_window
        lt, rt = c.frame.statusLine.update(c.p.b, 0)
        w.status_line.update(lt, rt)
    #@+node:ekr.20181122132345.1: *4* app.Drawing...
    #@+node:ekr.20181113042549.1: *5* app.action.redraw
    @flx.action
    def redraw(self, p):
        """
        Send a **redraw list** to the tree.

        This is a recusive list lists of items (ap, gnx, headline) describing
        all and *only* the presently visible nodes in the tree.

        As a side effect, app.make_redraw_dict updates all internal dicts.
        """
        trace = 'drawing' in g.app.debug
        tag = 'py.app.redraw'
        c = self.c
        p = p or c.p
        # #1142.
        c.selectPosition(p)
        redrawer = self.fast_redrawer
        w = self.main_window
        #
        # Be careful: c.frame.redraw can be called before app.finish_create.
        if not w or not w.tree:
            if trace:
                print(tag, 'no w.tree')
            return
        #
        # Profile times when all nodes are expanded.
            # self.test_full_outline(p)
        #
        # Redraw only the visible nodes.
        t1 = time.process_time()
        ap = self.p_to_ap(p)
        w.tree.select_ap(ap)
        # Needed to compare generations, even if there are no changes.
        redraw_dict = self.make_redraw_dict(p)
        new_flattened_outline = redrawer.flatten_outline(c)
        redraw_instructions = redrawer.make_redraw_list(
            self.old_flattened_outline,
            new_flattened_outline,
        )
        # At present, this does a full redraw using redraw_dict.
        # The redraw instructions are not used.
        w.tree.redraw_with_dict(redraw_dict, redraw_instructions)
        #
        # Do not call c.setChanged() here.
        if trace:
            print('app.redraw: %5.3f sec.' % (time.process_time() - t1))
        #
        # Move to the next redraw generation.
        self.old_flattened_outline = new_flattened_outline
        self.old_redraw_dict = redraw_dict
        self.redraw_generation += 1
    #@+node:ekr.20181111095640.1: *5* app.action.send_children_to_tree
    @flx.action
    def send_children_to_tree(self, parent_ap):
        """
        Call w.tree.receive_children(d), where d is compatible with make_redraw_dict:
            {
                'parent_ap': parent_ap,
                'items': [
                    self.make_dict_for_position(p)
                        for p in for p in p.children()
                ],
            }
        """
        p = self.ap_to_p(parent_ap)
        assert p, repr(parent_ap)
        if 0:
            # There is a similar trace in flx.tree.receive_children.
            print('send_children_to_tree: %s children' % len(list(p.children())))
            if 0:  # Corresponds to the trace in flx_tree.populate_children.
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
    def ap_to_p(self, ap):
        """Convert an archived position to a true Leo position."""
        childIndex = ap['childIndex']
        v = self.gnx_to_vnode[ap['gnx']]
        stack = [
            (self.gnx_to_vnode[d['gnx']], d['childIndex'])
                for d in ap['stack']
        ]
        return leoNodes.Position(v, childIndex, stack)
    #@+node:ekr.20181124071215.1: *5* app.dump_top_level
    def dump_top_level(self):
        """Dump the top-level nodes."""
        if 0:
            c = self.c
            print('\napp.dump_top_level...')
            # print('root:', c.rootPosition().h)
            # print(' c.p:', c.p.h)
            # print('')
            # print('Top-level nodes...')
            for p in c.rootPosition().self_and_siblings():
                print('  %5s %s' % (p.isExpanded(), p.h))
            print('')
    #@+node:ekr.20181113043539.1: *5* app.make_redraw_dict & helper
    def make_redraw_dict(self, p=None):
        """
        Return a **recursive**, archivable, list of lists describing all the
        visible nodes of the tree.

        As a side effect, recreate gnx_to_vnode.
        """
        c = self.c
        p = p or c.p
        t1 = time.process_time()
        c.expandAllAncestors(c.p)  # Ensure that c.p will be shown.
        d = {
            'c.p': self.p_to_ap(p),
            'items': [
                self.make_dict_for_position(p2)
                    for p2 in c.rootPosition().self_and_siblings()
            ],
        }
        t2 = time.process_time()
        if 0:
            print('app.make_redraw_dict: %s direct children %5.3f sec.' % (
                len(list(c.rootPosition().self_and_siblings())), (t2 - t1)))
        return d
    #@+node:ekr.20181113044701.1: *6* app.make_dict_for_position
    def make_dict_for_position(self, p):
        """
        Recursively add a sublist for p and all its visible nodes.
        It is already known that p itself is visible.
        """
        assert p.v
        self.gnx_to_vnode[p.v.gnx] = p.v
        if 0:
            # A superb trace. There are similar traces in:
            # - flx_tree.redraw_with_dict  and its helper, flx_tree.create_item_with_parent.
            # - flx_tree.populate_children and its helper, flx_tree.create_item_for_ap
            print('make_dict_for_position: %s%s' % ('  ' * p.level(), p.v.h))
        if p.isExpanded():  # Do not use p.v.isExpanded().
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
    #@+node:ekr.20190511091601.1: *4* app.Editing
    #@+node:ekr.20181129122147.1: *5* app.edit_headline & helper
    def edit_headline(self):
        """Simulate editing the headline in the minibuffer."""
        w = self.root.main_window
        mb = w.minibuffer
        mb.set_text('Enter Headline: ')
        mb.set_focus()

    def edit_headline_completer(self, headline):
        print('app.edit_headline_completer')
    #@+node:ekr.20190512081356.1: *4* app.request_focus
    def request_focus(self, w):
        """Monkey-patched c.request_focus."""
        tag = 'py.app.request_focus'
        trace = 'focus' in g.app.debug
        if not w:
            print('%30s: NO W: %s' % (tag, g.callers()))
            return
        #
        # Schedule the change in focus.
        mw = self.main_window
        table = (
            ('body', mw.body),
            ('log', mw.log),
            ('mini', mw.minibuffer),
            ('tree', mw.tree),
        )
        for w_name, flx_w in table:
            if w_name in repr(w):
                if trace:
                    print('%30s: %s' % (tag, flx_w.__class__.__name__))
                flx_w.set_focus()
                return
        if trace:
            print('%30s: FAIL %r' % (tag, w))
    #@+node:ekr.20190511091236.1: *4* app.Minibuffer
    #@+node:ekr.20181127070903.1: *5* app.execute_minibuffer_command
    def execute_minibuffer_command(self, commandName, char, mods):
        """Start the execution of a minibuffer command."""
        # Called by app.do_command.
        c = self.c
        # New code: execute directly.
        self.complete_minibuffer_command({
            'char': char,
            'commandName': commandName,
            'headline': c.p.h,  # Debugging.
            'mods': mods,
        })
    #@+node:ekr.20190510133737.1: *5* app.action.complete_minibuffer_command
    @flx.action
    def complete_minibuffer_command(self, d):
        """Complete the minibuffer command using d."""
        c = self.c
        k, w = c.k, c.frame.body.wrapper
        #
        # Do the minibuffer command: like k.callAltXFunction.
        commandName, char, mods = d['commandName'], d['char'], d['mods']
        # Same as in app.do_key.
        binding = '%s%s' % (''.join(['%s+' % (z) for z in mods]), char)
        event = g.Bunch(
            c=c,
            char=char,
            stroke=binding,
            widget=w,  # Use the body pane by default.
        )
        # Another hack.
        k.functionTail = None
        if commandName and commandName.isdigit():
            # The line number Easter Egg.
            def func(event=None):
                c.gotoCommands.find_file_line(n=int(commandName))
        else:
            func = c.commandsDict.get(commandName)
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
            else:
                # Important, so cut-text works, e.g.
                c.widgetWantsFocusNow(event and event.widget)
            try:
                func(event)
            except Exception:
                g.es_exception()
            return True
        if 0:
            # Not ready yet
            # Show possible completions if the command does not exist.
            if 1:  # Useful.
                k.doTabCompletion(list(c.commandsDict.keys()))
            else:  # Annoying.
                k.keyboardQuit()
                k.setStatusLabel('Command does not exist: %s' % commandName)
                c.bodyWantsFocus()
        return False
    #@+node:ekr.20190511102058.1: *4* app.Save commands
    # These all monkey-patch the corresponding c.fileCommands methods.
    #@+node:ekr.20190511100908.1: *5* app.save_file
    def save_file(self, fileName):
        """
        Monkey-patched override of c.fileCommands.save.

        Sync p.b before calling the original method.
        """
        if not self.root.inited:
            return
        if 'select' in g.app.debug:
            tag = 'py.app.save_file'
            print('%30s: %s' % (tag, fileName))
        c = self.c
        w = self.root.main_window
        w.body.sync_body_before_save_file({
            'ap': self.root.p_to_ap(c.p),
            'fn': fileName,
        })

    @flx.action
    def complete_save_file(self, d):
        self.update_body_from_dict_helper(d)  # Use the helper, to skip checks.
        fn = d['fn']
        if 'select' in g.app.debug:
            tag = 'py.app.complete_save_file'
            print('%30s: %s' % (tag, fn))
        self.old_save_file(fn)
    #@+node:ekr.20190511102119.1: *5* app.save_file_as
    def save_file_as(self, fileName):
        """
        Monkey-patched override of c.fileCommands.saveAs.

        Sync p.b before calling the original method.
        """
        if not self.root.inited:
            return
        if 'select' in g.app.debug:
            tag = 'py.app.save_file_as'
            print('%30s: %s' % (tag, fileName))
        c = self.c
        w = self.root.main_window
        w.body.sync_body_before_save_file_as({
            'ap': self.root.p_to_ap(c.p),
            'fn': fileName,
        })

    @flx.action
    def complete_save_file_as(self, d):
        self.update_body_from_dict_helper(d)  # Use the helper, to skip checks.
        fn = d['fn']
        if 'select' in g.app.debug:
            tag = 'py.app.complete_save_file'
            print('%30s: %s' % (tag, fn))
        self.old_save_file_as(fn)
    #@+node:ekr.20190511102120.1: *5* app.save_file_to
    def save_file_to(self, fileName):
        """
        Monkey-patched override of c.fileCommands.saveTo.

        Sync p.b before calling the original method.
        """
        if not self.root.inited:
            return
        if 'select' in g.app.debug:
            tag = 'py.app.save_file_to'
            print('%30s: %s' % (tag, fileName))
        c = self.c
        w = self.root.main_window
        w.body.sync_body_before_save_file_to({
            'ap': self.root.p_to_ap(c.p),
            'fn': fileName,
        })

    @flx.action
    def complete_save_file_to(self, d):
        self.update_body_from_dict_helper(d)  # Use the helper, to skip checks.
        fn = d['fn']
        if 'select' in g.app.debug:
            tag = 'py.app.complete_save_file'
            print('%30s: %s' % (tag, fn))
        self.old_save_file_to(fn)
    #@+node:ekr.20181124095316.1: *4* app.Selecting...
    #@+node:ekr.20181216051109.1: *5* app.action.complete_select
    @flx.action
    def complete_select(self, d):
        """Complete the selection of the d['new_ap']"""
        self.update_body_from_dict(d)
        # tree.complete_select has direct ivars to tree ivars.
        self.c.frame.tree.complete_select(d)
    #@+node:ekr.20181111202747.1: *5* app.action.select_ap
    @flx.action
    def select_ap(self, ap):
        """
        Select the position in Leo's core corresponding to the archived position.

        Nothing in the flx.tree needs to be updated.
        """
        assert ap, g.callers()
        c, w = self.c, self.main_window
        p = self.ap_to_p(ap)
        assert p, (repr(ap), g.callers())
        lt, rt = c.frame.statusLine.update()
        w.status_line.update(lt, rt)
        # print('app.select_ap', repr(ap))
        w.tree.select_ap(ap)
        # call LeoTree.select, but not self.select_p.
        c.frame.tree.super_select(p)
    #@+node:ekr.20190506100026.1: *5* app.action.select_minibuffer
    @flx.action
    def select_minibuffer(self):
        """Select the minibuffer in response to user click."""
        c = self.c
        event = g.app.gui.create_key_event(c, w=c.frame.body.wrapper)
        c.k.fullCommand(event)
    #@+node:ekr.20181118061020.1: *5* app.action.select_p
    @flx.action
    def select_p(self, p):
        """
        Select the position in the tree.

        Called from LeoBrowserTree.select, so do *not* call c.frame.tree.select.
        """
        c = self.c
        w = self.main_window
        ap = self.p_to_ap(p)
        # Be careful during startup.
        if not (w and w.tree):
            return
        if 'select' in g.app.debug:
            tag = 'py.app.select_p'
            print('%30s: %4s %s %s' % (tag, len(p.b), p.gnx, p.h))
        w.tree.set_ap(ap)
        # #1142: This code was not the problem.
        body = c.frame.body.wrapper
        w.body.set_text(body.s)
        w.body.set_insert_point(body.ins, body.sel)
    #@+node:ekr.20190510053112.1: *5* app.action.select_tree_using_ap
    @flx.action
    def select_tree_using_ap(self, ap):
        """A helper action, called from flx_tree.on_selected_event."""
        # tag = 'py.app.select_tree_using_ap'
        # print(tag, ap ['headline'])
        p = self.ap_to_p(ap)
        self.c.frame.tree.select(p)
    #@+node:ekr.20181111204659.1: *5* app.p_to_ap (updates dict)
    def p_to_ap(self, p):
        """
        Convert a true Leo position to a serializable archived position.
        """
        if not p.v:
            print('app.p_to_ap: no p.v: %r %s' % (p, g.callers()))
            assert False, g.callers()
        p_gnx = p.v.gnx
        if p_gnx not in self.gnx_to_vnode:
            # print('=== update gnx_to_vnode', p_gnx, p.h)
                # len(list(self.gnx_to_vnode.keys())
            self.gnx_to_vnode[p_gnx] = p.v
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
            } for (stack_v, stack_childIndex) in p.stack],
        }
    #@+node:ekr.20181215154640.1: *5* app.update_body_from_dict & helper
    def update_body_from_dict(self, d):
        """
        Update the *old* p.b from d.

        Add 'ins_row/col', 'sel_row/col/1/2' keys.
        """
        tag = 'py.app.update_body_from_dict'
        p, v = self.c.p, self.c.p.v
        assert v, g.callers()
        #
        # Check d[old_ap], if it exists.
        old_p = self.ap_to_p(d['old_ap'])
        if p != old_p:
            print('%30s: MISMATCH: %s ==> %s' % (tag, old_p.h, p.h))
            return
        if 'select' in g.app.debug:
            tag = 'py.app.update_body_from_dict'
            d_s = d['s']
            print('%30s: %4s %s %s' % (tag, ' ', p.gnx, p.h))
            print('%30s: p.b: %s d.s: %s' % (tag, len(p.b), len(d_s)))
            # self.dump_dict(d, tag)
        self.update_body_from_dict_helper(d)
    #@+node:ekr.20190511094352.1: *6* app.update_body_from_dict_helper
    def update_body_from_dict_helper(self, d):
        """Update the body dict, without checks."""
        c, v = self.c, self.c.p.v
        d_s = d['s']
        #
        # Compute the insert point and selection range.
        col, row = d['ins_col'], d['ins_row']
        ins = g.convertRowColToPythonIndex(d_s, row, col)
        col1, row1 = d['sel_col1'], d['sel_row1']
        col2, row2 = d['sel_col2'], d['sel_row2']
        sel1 = g.convertRowColToPythonIndex(d_s, row1, col1)
        sel2 = g.convertRowColToPythonIndex(d_s, row2, col2)
        sel = (sel1, sel2)
        #
        # Update v's ivars
        v.setBodyString(d_s)
        v.insertSpot = ins
        # #2020: The old code updated a non-existent attribute.
        v.selectionStart = ins
        v.selectionLength = abs(sel1 - sel2)
        #
        # Update the body wrapper's ivars (for minibuffer commands).
        if 0:
            # These don't seem to work properly.
            # Besides, we are about to change nodes.
            w = c.frame.body.wrapper
            w.ins, w.sel, w.s = ins, sel, d_s
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
            self.end_set_headline(command[len(h1) :])
            return
        h2 = 'Find: '
        if command.startswith(h2):
            self.end_find(command[len(h2) :])
            return
        func = getattr(self, 'do_' + command, None)
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
            binding='',
            char='',
            event={'c': c},
            w=c.frame.miniBufferWidget,
        )
        c.interactive(
            callback=self.terminate_do_find,
            event=event,
            prompts=['Find: ',],
        )

    def terminate_do_find(self):
        """Never called."""
    #@+node:ekr.20181210092900.1: *7* app.end_find
    def end_find(self, pattern):
        c = self.c
        fc = c.findCommands

        class DummyFTM:
            def get_find_text(self):
                return pattern
            def get_change_text(self):
                return ''
            def get_settings(self):
                return g.Bunch(
                    # Find/change strings...
                    find_text=pattern,
                    change_text='',
                    # Find options...
                    file_only=False,
                    ignore_case=True,
                    mark_changes=False,
                    mark_finds=False,
                    node_only=False,
                    pattern_match=False,
                    search_body=True,
                    search_headline=True,
                    suboutline_only=False,
                    whole_word=True,
                )

        # Init the search.
        fc.ftm = DummyFTM()
        # Do the search.
        fc.find_next()
        if 1:  # Testing only?
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
            binding='',
            char='',
            event={'c': c},
            w=c.frame.miniBufferWidget,
        )
        c.interactive(
            callback=self.terminate_do_head,
            event=event,
            prompts=['Set headline: ',],
        )

    def terminate_do_head(self, args, c, event):
        """never actually called."""
    #@+node:ekr.20181210092817.1: *7* app.end_set_headline (leoflexx.py)
    def end_set_headline(self, h):
        c, k, p, u = self.c, self.c.k, self.c.p, self.c.undoer
        w = self.root.main_window
        # Undoably set the head. Like leoTree.onHeadChanged.
        p.v.setHeadString(h)
        undoType = 'set-headline'
        undoData = u.beforeChangeNodeContents(p)
        if not c.changed:
            c.setChanged()
        p.setDirty()
        u.afterChangeNodeContents(p, undoType, undoData)
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
            print('app.do_select: not found: %s' % h)
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

    #@+node:ekr.20181126104843.1: *5* app.test_full_outline
    def test_full_outline(self, p):
        """Exercise the new diff-based redraw code on a fully-expanded outline."""
        c = self.c
        p = p.copy()
        redrawer = self.fast_redrawer
        # Don't call c.expandAllHeadlines: it calls c.redraw.
        for p2 in c.all_positions(copy=False):
            p2.expand()
        #
        # Test the code.
        self.make_redraw_dict(p)  # Call this only for timing stats.
        new_flattened_outline = redrawer.flatten_outline(c)
        redraw_instructions = redrawer.make_redraw_list(
            self.old_flattened_outline,
            new_flattened_outline,
        )
        assert redraw_instructions is not None  # For pyflakes.
        #
        # Restore the tree.
        for p2 in c.all_positions(copy=False):
            p2.contract()
        c.expandAllAncestors(p)  # Does not do a redraw.
    #@+node:ekr.20181113180246.1: *5* app.test_round_trip_positions
    def test_round_trip_positions(self):
        """Test the round tripping of p_to_ap and ap_to_p."""
        c = self.c
        # Bug fix: p_to_ap updates app.gnx_to_vnode. Save and restore it.
        old_d = self.gnx_to_vnode.copy()
        old_len = len(list(self.gnx_to_vnode.keys()))
        # t1 = time.process_time()
        for p in c.all_positions():
            ap = self.p_to_ap(p)
            p2 = self.ap_to_p(ap)
            assert p == p2, (repr(p), repr(p2), repr(ap))
        self.gnx_to_vnode = old_d
        new_len = len(list(self.gnx_to_vnode.keys()))
        assert old_len == new_len, (old_len, new_len)
        # print('app.test_round_trip_positions: %5.3f sec' % (time.process_time()-t1))
    #@-others
#@+node:ekr.20181115092337.3: *3* class LeoBrowserBody
class LeoBrowserBody(leoFrame.NullBody):

    def __init__(self, frame):
        super().__init__(frame, parentFrame=None)
        self.c = c = frame.c
        self.root = get_root()
        self.tag = 'py.body.wrap'
        # Replace the StringTextWrapper with the ace wrapper.
        assert isinstance(self.wrapper, leoFrame.StringTextWrapper)
        self.wrapper = API_Wrapper(c, 'body')

    # The Ace Wrapper does almost everything.
    def __getattr__(self, attr):
        if self.root.inited:
            return getattr(self.wrapper, attr)
        raise AttributeError('app not inited')

    def getName(self):
        return 'body'  # Required for proper pane bindings.

#@+node:ekr.20181115092337.6: *3* class LeoBrowserFrame
class LeoBrowserFrame(leoFrame.NullFrame):

    def __init__(self, c, title, gui):
        """Ctor for the LeoBrowserFrame class."""
        super().__init__(c, title, gui)
        assert self.c == c
        frame = self
        self.root = get_root()
        self.tag = 'py.frame.wrap'
        #
        # Instantiate the other wrappers.
        self.body = LeoBrowserBody(frame)
        self.tree = LeoBrowserTree(frame)
        self.log = LeoBrowserLog(frame)
        self.menu = LeoBrowserMenu(frame)
        self.miniBufferWidget = LeoBrowserMinibuffer(c, frame)
        self.iconBar = LeoBrowserIconBar(c, frame)
        # NullFrame does this in createStatusLine.
        self.statusLine = LeoBrowserStatusLine(c, frame)
        # This is the DynamicWindow object.
        # There is no need to implement its methods now.
        self.top = g.NullObject()

    def finishCreate(self):
        """Override NullFrame.finishCreate."""
        # Do not call self.createFirstTreeNode.

    #@+others
    #@-others
#@+node:ekr.20181113041113.1: *3* class LeoBrowserGui
class LeoBrowserGui(leoGui.NullGui):

    def __init__(self, gui_name='browser'):
        # leoTest.doTest special-cases the name "browser".
        super().__init__(guiName='browser')
        self.gui_name = gui_name  # May specify the actual browser.
        assert gui_name.startswith('browser')
        self.logWaiting = []
        self.root = None  # Will be set later.
        self.silentMode = True  # Don't print a single signon line.
        self.tag = 'py.gui'
        self.specific_browser = gui_name.lstrip('browser').lstrip(':').lstrip('-').strip()
        if not self.specific_browser:
            self.specific_browser = 'browser'
        self.consoleOnly = False  # Console is separate from the log.
        #
        # Monkey-patch g.app.writeWaitingLog to be a do-nothing.
        # This allows us to write the log much later.
        g.app.writeWaitingLog = self.writeWaitingLog1

    def insertKeyEvent(self, event, i):
        """Insert the key given by event in location i of widget event.w."""
        # Mysterious...
        assert False, g.callers()

    #@+others
    #@+node:ekr.20181206153033.1: *4* gui.createLeoFrame
    def createLeoFrame(self, c, title):
        """
        Override NullGui.createLeoFrame.

        We can't create a real flx.Frame until much later.

        We create a placeholder in g.app.windowList, for app.finish_create.
        """
        gui = self
        self.lastFrame = DummyFrame(c, title, gui)
        # A buglet in Leo's core: this is necessary.
        # LM.doPostPluginsInit tests g.app.windowList, maybe when it shouldn't.
        g.app.windowList.append(self.lastFrame)
        return self.lastFrame
    #@+node:ekr.20181119141542.1: *4* gui.isTextWrapper
    def isTextWrapper(self, w):
        """Return True if w is supposedly a text widget."""
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
        # print('%s: get_focus: %r' % (self.tag, w.tag))
        return w

    def set_focus(self, commander, widget):
        # Be careful during startup.
        if g.unitTesting:
            return
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
            if 'focus' in g.app.debug:
                tag = 'gui.set_focus'
                print('%30s: %s' % (tag, widget.tag))
            widget.setFocus()
            self.focusWidget = widget
        elif isinstance(widget, API_Wrapper):
            # This does sometimes get executed.
            # print('gui.set_focus: redirect AceWrapper to LeoBrowserBody')
            assert isinstance(c.frame.body, LeoBrowserBody), repr(c.frame.body)
            assert widget.name == 'body', repr(widget.name)
            c.frame.body.wrapper.setFocus()
        else:
            print('gui.set_focus: unknown widget', repr(widget), g.callers(6))
    #@+node:ekr.20181206090210.1: *4* gui.writeWaitingLog1/2
    def writeWaitingLog1(self, c=None):
        """Monkey-patched do-nothing version of g.app.writeWaitingLog."""

    def writeWaitingLog2(self, c=None):
        """Called from app.finish_create."""
        w = self.root.main_window
        #
        # Print the signon.
        table = [
            ('Leo Log Window', 'red'),
            ('flexx version: %s' % (flx.__version__), None),
            (g.app.signon, None),
            (g.app.signon1, None),
            (g.app.signon2, None),
        ]
        for message, color in table:
            if message.strip():
                w.log.put(message.rstrip())
        #
        # Write all the queued log entries.
            # c.setLog()
        g.app.logInited = True  # Prevent recursive call.
        for msg in g.app.logWaiting:
            s, color, newline = msg[:3]  # May have 4 elements.
            w.log.put(s.rstrip())
        g.app.logWaiting = []
        g.app.setLog(None)  # Essential when opening multiple files...
    #@+node:ekr.20181202083305.1: *4* gui.runMainLoop
    def runMainLoop(self):
        """Run the main loop from within Leo's core."""
        runtime = self.specific_browser or 'webruntime'
        flx.launch(LeoBrowserApp, runtime)
        flx.set_log_level('ERROR')  #  'INFO'
        flx.run()
    #@-others
#@+node:ekr.20181115092337.21: *3* class LeoBrowserIconBar
class LeoBrowserIconBar(leoFrame.NullIconBarClass):

    def __init__(self, c, parentFrame):
        super().__init__(c, parentFrame)
        assert self.c == c
        self.root = get_root()
        self.tag = 'py.icon bar.wrap'

    #@+others
    #@-others
#@+node:ekr.20181115092337.22: *3* class LeoBrowserLog
class LeoBrowserLog(leoFrame.NullLog):

    def __init__(self, frame, parentFrame=None):
        super().__init__(frame, parentFrame)
        self.root = get_root()
        self.tag = 'py.log.wrap'
        assert isinstance(self.widget, leoFrame.StringTextWrapper)
        self.logCtrl = self.widget
        self.logWidget = self.widget
        self.wrapper = self.widget
        #
        # Monkey-patch self.wrapper, a StringTextWrapper.
        assert self.wrapper.getName().startswith('log')
        self.wrapper.setFocus = self.setFocus

    def __repr__(self):
        return 'LeoBrowserLog'

    __str__ = __repr__

    def getName(self):
        return 'log'  # Required for proper pane bindings.

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
    """Browser wrapper for menus."""

    # def __init__(self, frame):
        # super().__init__(frame)
        # self.root = get_root()
        # self.tag = '(py.menu.wrap)'

    #@verbatim
    # @others
#@+node:ekr.20181115120317.1: *3* class LeoBrowserMinibuffer (StringTextWrapper)
# Leo's core doesn't define a NullMinibuffer class.

class LeoBrowserMinibuffer(leoFrame.StringTextWrapper):
    """Browser wrapper for minibuffer."""

    def __init__(self, c, frame):
        # Name must be minibuffer, for gui.isTextWrapper().
        super().__init__(c, name='minibuffer')
        assert self.c == c, repr(self.c)
        # assert c.frame == frame, (repr(c.frame), repr(frame))
            # c.frame is a NullFrame.  frame is a LeoBrowserFrame.
        assert self.widget is None, repr(self.widget)
        assert self.getName() == 'minibuffer'
        self.frame = frame
        self.root = get_root()
        self.tag = 'py.mini.wrap'
        self.widget = self
        self.wrapper = self
        # Hook this class up to the key handler.
        c.k.w = self
        c.miniBufferWidget = self  # #1146.
        frame.minibufferWidget = self

    # Overrides.
    def setFocus(self):
        self.root.main_window.minibuffer.set_focus()

    #@+others
    #@+node:ekr.20181208062449.1: *4* mini.called by k.minibuffer
    # Override the methods called by k.minibuffer:

    last_ins = None
    last_sel = None
    last_s = None

    def update(self, tag):
        w = self.root.main_window
        i, j = self.sel
        # Do nothing if there will be no changes.
        if self.s == self.last_s and self.last_ins == self.ins and self.sel == self.last_sel:
            return
        # Remember the present values.
        self.last_ins, self.last_s, self.last_sel = self.ins, self.s, self.sel
        if 'select' in g.app.debug:
            tag = 'py.mini.update'
            print('%30s: sel: %3s %3s ins: %3s len(s): %s' % (
                tag, i, j, self.ins, len(self.s)))
        w.minibuffer.set_text(self.s)
        w.minibuffer.set_selection(i, j)
        w.minibuffer.set_insert(self.ins)

    def delete(self, i: int, j: Optional[int] = None):
        super().delete(i, j)
        self.update('delete')

    def getAllText(self):
        return self.s

    def insert(self, i: int, s: str) -> None:
        super().insert(i, s)
        self.update('insert')

    def setAllText(self, s):
        super().setAllText(s)
        self.update('setAllText')

    def setSelectionRange(self, i: int, j: int, insert: Optional[int] = None):
        super().setSelectionRange(i, j, insert)
        self.update('setSelectionRange')

    def setStyleClass(self, name):
        w = self.root.main_window
        if not w:
            g.trace('NO MAIN WINDOW')
            return
        # if 'focus' in g.app.debug:
            # tag = 'py.mini.setStyleClass'
            # print('%30s: %r' % (tag, name))
        w.minibuffer.set_style(name)
        self.update('setStyleClass:%r' % name)
    #@-others
#@+node:ekr.20181115092337.32: *3* class LeoBrowserStatusLine
class LeoBrowserStatusLine(leoFrame.NullStatusLineClass):

    def __init__(self, c, parentFrame):
        super().__init__(c, parentFrame)
        self.root = get_root()
        self.tag = 'py.status.wrap'
        self.w = self  # Required.

    def getName(self):
        return 'status line'  # Value not important.

    # Pretend that this widget supports the high-level interface.
    def __getattr__(self, attr):
        return g.NullObject()

    #@+others
    #@+node:ekr.20181119045430.1: *4* status_line_wrapper.clear & get
    def clear(self):
        pass

    def get(self):
        print('status_line.get: NOT READY')
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
        """
        Update the status line, based on the contents of the body.

        Called from LeoTree.select.

        Returns (lt_part, rt_part) for LeoBrowserApp.init.
        """
        # pylint: disable=arguments-differ
        if g.app.killed:
            return None
        c, p = self.c, self.c.p
        if not p:
            return None
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
        self.select_lockout = False
        self.tag = 'py.tree.wrap'
        self.widget = self
        self.wrapper = self

    def getName(self):
        return 'canvas(tree)'  # Required for proper pane bindings.

    #@+others
    #@+node:ekr.20181116081421.1: *4* tree.selection...


    #@+node:ekr.20190508121417.1: *5* tree.complete_select
    def complete_select(self, d):
        """Complete the selection of the tree."""
        trace = 'select' in g.app.debug
        tag = 'py.tree.complete_select'
        if not self.new_p:
            self.select_lockout = False
            print('%30s: can not happen: no new_p')
            return
        p = self.root.ap_to_p(d['new_ap'])
        if p != self.new_p:
            print('%30s: expected: %s, got: %s' % (tag, self.new_p.h, p.h))
            return
        if trace:
            print('%30s: %4s %s %s' % (tag, len(p.b), p.gnx, p.h))
        #
        # Allow a new select.
        self.select_lockout = False
        #
        # Make everything official in Leo's core.
        super().select(p)  # Call LeoTree.select.
        self.root.select_p(p)  # Call app.select_position.
    #@+node:ekr.20190508121510.1: *5* tree.endEditLabel
    def endEditLabel(self):
        """
        End editing.

        This must be a do-nothing, because app.end_set_headline takes its place.
        """
        # print(flx.tree.endEditLabel')
    #@+node:ekr.20190508121414.1: *5*  tree.select
    # The lockout ensures that old_p never changes during the selection process.
    select_lockout = False
    old_p = None
    new_p = None

    def select(self, p):
        """
        Override LeoTree.select.

        Operations across the Python/JS divide do not happen immediately. As a result,
        the selection must happen in phases:

        Phase 1a: PY side:
        - Remember the old and new p.
        - Schedule sync_body_before_select to update of the old p.b on the JS side.
        - Set the lockout, so only one JS update is ever done.

        Phase 1b: PY side:
        - If the lockout is set, just update the *new* p.

        Phase 2: JS side:
        - Update the *old* p.b and related vnode ivars from the body pane.
          Important: The lockout never changes the *old* p.
        - Call flx.tree.complete_select to update the widget.
        - Schedule app.complete_select.

        Phase 3: PY side:
        """
        trace = 'select' in g.app.debug
        tag = 'py.tree.select'
        w = self.root.main_window
        if self.select_lockout:
            self.new_p = p.copy()
            if trace:
                print('%30s: %s %s' % (tag, ' Lockout', p.h))
            return
        if not self.root.inited:
            # Don't sync the body pane during startup.
            super().select(p)  # Call LeoTree.select
            self.root.select_p(p)  # Call app.select_position.
            return
        #
        # Begin the selection.
        self.select_lockout = True
        self.new_p = p.copy()
        old_p = self.root.c.p
        if trace:
            print('\n%30s: %4s %s ==> %s %s ' % (
                tag, len(old_p.v._bodyString), old_p.h, len(p.v._bodyString), p.h))
        #
        # Schdule JS side to:
        # 1. Update *old* p.b from flx.body.
        #    The lockout ensures that the old p never changes.
        # 2. Schedule self.complete_select.
        w.body.sync_body_before_select({
            'old_ap': self.root.p_to_ap(old_p),
            'new_ap': self.root.p_to_ap(p),
        })
    #@+node:ekr.20190508121417.2: *5* tree.select_ap
    def select_ap(self, ap):
        trace = 'select' in g.app.debug
        p = self.root.ap_to_p(ap)
        if trace:
            tag = 'py.tree.select_ap'
            print('%30s: %s %s' % (tag, p.v.fileIndex, p.v._headString))
        self.select(p)
    #@+node:ekr.20190508121417.3: *5* tree.super_select
    def super_select(self, p):
        """Call only LeoTree.select."""
        trace = 'select' in g.app.debug
        if trace:
            tag = 'py.tree.super_select'
            print('%30s %4s %s %s' % (tag, len(p.b), p.gnx, p.h))
        super().select(p)

    #@+node:ekr.20181118052203.1: *4* tree.redraw
    def redraw(self, p=None):
        """This is c.frame.tree.redraw!"""
        self.root.redraw(p)
    #@+node:ekr.20181120063844.1: *4* tree.setFocus
    def setFocus(self):
        w = self.root.main_window
        w.tree.set_focus()
    #@-others
#@+node:ekr.20181119094122.1: *3* class TracingNullObject (leoflexx.py)
#@@nobeautify

class TracingNullObject:
    """A tracing version of g.NullObject."""
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
    """
    The base class for the body and log panes.
    """

    def init(self, name, flex=1):
        # pylint: disable=arguments-differ
        assert name in ('body', 'log', 'minibuffer'), repr(name)
        self.name = name
        self.tag = 'flx.%s' % name
        self.editor = None  # Now done in subclasses.

    @flx.reaction('size')
    def __on_size(self, *events):
        self.editor.resize()

    #@+others
    #@+node:ekr.20181121072246.1: *4* jse.Keys
    #@+node:ekr.20181215083729.1: *5* jse.key_press & on_key_press
    last_down = None
    ignore_up = False

    @flx.emitter  # New
    def key_down(self, e):
        trace = False and 'keys' in g.app.debug
        self.ignore_up = False
        ev = self._create_key_event(e)
        down = '%s %r' % (self.name, ev)
        if down != self.last_down:
            self.last_down = down
            if trace:
                print('     jse.key_down:', down)
        if self.should_be_leo_key(ev):
            e.preventDefault()
        return ev

    @flx.emitter  # New
    def key_up(self, e):
        trace = False and 'keys' in g.app.debug
        self.last_down = None  # Enable key downs.
        ev = self._create_key_event(e)
        if self.ignore_up:
            if trace:
                print('IGNORE jse.key_up: %s %r' % (self.name, ev))
            e.preventDefault()
            return ev
        self.ignore_up = True  # Ignore all further key ups, until the next key down.
        should_be_leo = bool(self.should_be_leo_key(ev))
        if trace:
            print('       jse.key_up: %s %r Leo: %s' % (self.name, ev, should_be_leo))
        if should_be_leo:
            e.preventDefault()
            ivar = 'minibufferWidget' if self.name == 'minibuffer' else self.name
            self.root.do_key(ev, ivar)
        return ev

    @flx.emitter
    def key_press(self, e):
        trace = 'keys' in g.app.debug
        ev = self._create_key_event(e)
        # Init the key_down state.
        self.last_down = None
        # Ignore all key ups until the next key down.
        self.ignore_up = True
        if trace:
            print('    jse.key_press: %s %r' % (self.name, ev))
        if self.should_be_leo_key(ev):
            e.preventDefault()
        return ev

    @flx.reaction('key_press')
    def on_key_press(self, *events):
        # The JS editor has already** handled the key!
        for ev in events:
            if 'keys' in g.app.debug:
                print(' jse.on_key_press: %s %r' % (self.name, ev))
            if self.should_be_leo_key(ev):
                ivar = 'minibufferWidget' if self.name == 'minibuffer' else self.name
                self.root.do_key(ev, ivar)
    #@+node:ekr.20181201081444.1: *5* jse.should_be_leo_key
    def should_be_leo_key(self, ev):
        """
        Return True if Leo should handle the key.
        Leo handles only modified keys, not F-keys or plain keys.
        """
        trace = False and 'keys' in g.app.debug
        tag = 'JSE.should_be_leo_key'
        key, mods = ev['key'], ev['modifiers']
        #
        # The widget handles F-keys.
        if not mods and key.startswith('F'):
            if trace:
                print('%s: %r %r return: false' % (tag, mods, key))
            return False
        mods2 = mods
        if 'Shift' in mods2:
            mods2.remove('Shift')
        #
        # Send only Ctrl-Arrow keys to body.
        if mods2 == ['Ctrl'] and key in ('RtArrow', 'LtArrow', 'UpArrow', 'DownArrow'):
            # This never fires: Neither editor widget emis Ctrl/Arrow keys or Alt-Arrow keys.
            if trace:
                print(tag, 'Arrow key: send to to body', repr(mods), repr(key))
            return False
        #
        # Leo should handle all other modified keys.
        if trace:
            print('%s: %r %r return: %s' % (tag, mods, key, bool(mods2)))
        return mods2
    #@+node:ekr.20181215083642.1: *4* jse.focus
    @flx.action
    def see_insert_point(self):
        if 'focus' in g.app.debug:
            tag = '%s.%s' % (self.tag, 'jse.see_insert_point')
            print('%30s:' % tag)

    @flx.action
    def set_focus(self):
        if 'focus' in g.app.debug:
            tag = '%s.%s' % (self.tag, 'jse.set_focus')
            print('%30s:' % tag)
        self.editor.focus()
    #@+node:ekr.20181215061810.1: *4* jse.text getters
    def get_ins(self):
        d = self.editor.selection.getCursor()
        row, col = d['row'], d['column']
        # print('%s: get_ins: row: %s col: %s' % (self.tag, row, col))
        return row, col

    def get_sel(self):
        selections = self.editor.selection.getAllRanges()
        if selections:
            sel = selections[0]
            d1, d2 = sel['start'], sel['end']
            row1, col1 = d1['row'], d1['column']
            row2, col2 = d2['row'], d2['column']
        else:
            print('%s: get_sel: NO SELECTION' % self.tag)
            i = self.get_ins()
            row1 = col1 = row2 = col2 = i
        # print('%s: get_sel: (%s, %s) to (%s, %s)' % (self.tag, row1, col1, row2, col2))
        return row1, col1, row2, col2

    def get_text(self):
        editor = self.editor
        s = editor.getValue()
        # print('%s: get_text: %s' % (self.tag, len(s)))
        return s
    #@+node:ekr.20181128061524.1: *4* jse.text setters
    @flx.action
    def insert(self, s):
        # print(self.tag, 'insert', repr(s))
        self.editor.insert(s)

    @flx.action
    def select_all_text(self):
        if 'select' in g.app.debug:
            print(self.tag, 'select_all_text')

    @flx.action
    def set_insert_point(self, insert, sel):
        s = self.editor.getValue()
        row, col = g.convertPythonIndexToRowCol(s, insert)
        row = max(0, row - 1)
        if 'select' in g.app.debug:
            tag = '%s.%s' % (self.tag, 'set_insert_point')
            print('%30s: i: %s = (%s, %s)' % (
                tag, str(insert).ljust(3), row, col))
        self.editor.moveCursorTo(row, col)

    @flx.action
    def set_selection_range(self, i, j):
        print(self.tag, 'set_selection_range: NOT READY', i, j)

    @flx.action
    def set_text(self, s):
        """Set the entire text"""
        # print('%s.set_text: len(s): %s' % (self.tag, len(s)))
        self.editor.setValue(s)
    #@-others
#@+node:ekr.20181104082144.1: *3* class LeoFlexxBody (JS_Editor)
class LeoFlexxBody(JS_Editor):
    """A CodeEditor widget based on Ace."""

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
    #@+node:ekr.20190512094614.1: *4* flx_body.action.set_focus
    @flx.action
    def set_focus(self):
        if 'focus' in g.app.debug:
            tag = 'flx.body.set_focus'
            print('%30s:' % tag)
        self.editor.focus()
    #@+node:ekr.20181215061402.1: *4* flx_body.action.sync*


    #@+node:ekr.20190511092226.1: *5* flx.body.action.sync_body_before_save_file
    @flx.action
    def sync_body_before_save_file(self, d):
        """Update p.b, etc. before executing calling c.fileCommands.save."""
        self.update_body_dict(d)
        if 'select' in g.app.debug:
            tag = 'flx.body.sync_body_before_save_file'
            print('%30s: %r' % (tag, d['s']))
        self.root.complete_save_file(d)
    #@+node:ekr.20190511102428.1: *5* flx.body.action.sync_body_before_save_file_as
    @flx.action
    def sync_body_before_save_file_as(self, d):
        """Update p.b, etc. before executing calling c.fileCommands.saveAs."""
        self.update_body_dict(d)
        if 'select' in g.app.debug:
            tag = 'flx.body.sync_body_before_save_file_as'
            print('%30s: %r' % (tag, d['s']))
        self.root.complete_save_file_as(d)
    #@+node:ekr.20190511102429.1: *5* flx.body.action.sync_body_before_save_file_to
    @flx.action
    def sync_body_before_save_file_to(self, d):
        """Update p.b, etc. before executing calling c.fileCommands.saveTo."""
        self.update_body_dict(d)
        if 'select' in g.app.debug:
            tag = 'flx.body.sync_body_before_save_file_to'
            print('%30s: %r' % (tag, d['s']))
        self.root.complete_save_file_to(d)
    #@+node:ekr.20190510070009.1: *5* flx.body.action.sync_body_before_select
    @flx.action
    def sync_body_before_select(self, d):
        """
        Called by app.tree.select to update the *old* p.b, etc. before selecting a new node.

        d['old_ap']: The AP for the old node.
        d['new_ap']: The AP for the new node.
        """
        if 'select' in g.app.debug:
            tag = 'flx.body.sync_body_before_select'
            print('')
            print('%30s: %s ==> %s' % (
                tag, d['old_ap']['headline'], d['old_ap']['headline']))
            # self.root.dump_dict(d, tag)
        # Sets d.s, etc., describing insert point & selection range.
        self.update_body_dict(d)
        self.root.complete_select(d)

    #@+node:ekr.20190510070010.1: *4* flx.body.update_body_dict
    def update_body_dict(self, d):
        """
        Add keys to d describing flx.body.

        This sets d.s & other keys from the *old* position.
        """
        #
        # Remember the body text.
        d['s'] = self.get_text()
        d['ins_row'], d['ins_col'] = self.get_ins()
        #
        # Remember the selection ranges.
        row1, col1, row2, col2 = self.get_sel()
        d['sel_row1'], d['sel_col1'] = row1, col1
        d['sel_row2'], d['sel_col2'] = row2, col2
        if 'select' in g.app.debug:
            d_s = d['s']
            tag = 'flx.body.update_body_dict'
            print('%30s: len(d_s): %4s' % (tag, len(d_s)))
            if 0:
                print('')
                for z in d_s.split('\n'):
                    print(repr(z))
                print('')
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
        if 'focus' in g.app.debug:
            tag = 'flx.log.set_focus'
            print('%30s:' % tag)
        self.editor.focus()
    #@-others
#@+node:ekr.20181104082130.1: *3* class LeoFlexxMainWindow
class LeoFlexxMainWindow(flx.Widget):

    """
    Leo's main window, that is, root.main_window.

    Each property is accessible as root.main_window.x.
    """
    body = flx.ComponentProp(settable=True)
    log = flx.ComponentProp(settable=True)
    minibuffer = flx.ComponentProp(settable=True)
    status_line = flx.ComponentProp(settable=True)
    tree = flx.ComponentProp(settable=True)

    def init(self):
        self.tag = 'flx.main window'
        with flx.VSplit():
            with flx.HSplit(flex=1):
                tree = LeoFlexxTree(flex=1)
                log = LeoFlexxLog(flex=1)
            body = LeoFlexxBody(flex=1)
            minibuffer = LeoFlexxMiniBuffer()
            status_line = LeoFlexxStatusLine()
        #@+<< define unload action >>
        #@+node:ekr.20181206044554.1: *4* << define unload action >>
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

    @flx.reaction('!do_init')
    def after_init(self):
        self.root.finish_create()
#@+node:ekr.20181104082154.1: *3* class LeoFlexxMiniBuffer (JS_Editor)
class MinibufferEditor(flx.Widget):

    def init(self):
        # Unlike in components, this call happens immediately.
        self.editor = make_editor_function('minibuffer', self.node)

class LeoFlexxMiniBuffer(JS_Editor):

    def init(self):
        # pylint: disable=arguments-differ
        super().init('minibuffer')
        with flx.HBox():
            flx.Label(text='Minibuffer')
            w = MinibufferEditor(flex=1)
            self.editor = w.editor

    @flx.reaction('pointer_down')
    def on_select(self):
        self.root.select_minibuffer()

    #@+others
    #@+node:ekr.20181127060810.1: *4* flx_minibuffer.high-level interface
    # The high-level interface methods, called from LeoBrowserMinibuffer.

    @flx.action
    def set_focus(self):
        if 'focus' in g.app.debug:
            tag = 'flx.mini.set_focus'
            print('%30s:' % tag)
        self.editor.focus()

    @flx.action
    def set_insert(self, i):
        if False and 'select' in g.app.debug:
            print('flx.mini.set_insert', i)
        # Where is call?

    @flx.action
    def set_selection(self, i, j):
        if False and 'select' in g.app.debug:
            print('flx.mini.set_selection', i, j)
        # Where is the call?

    @flx.action
    def set_style(self, style):
        pass

    @flx.action
    def set_text(self, s):
        if 'focus' in g.app.debug:
            tag = 'flx.mini.set_text'
            print('%30s: %r' % (tag, s))
        self.editor.setValue(s)
    #@+node:ekr.20181203150409.1: *4* flx_minibuffer.Key handling
    @flx.emitter
    def key_press(self, e):
        """Pass *all* keys except Enter and F12 to Leo's core."""
        # Backspace is not emitted.
        ev = self._create_key_event(e)
        key, mods = ev['key'], ev['modifiers']
        if 'keys' in g.app.debug:
            print('mini.key_press: %r %r' % (mods, key))
        if mods:
            e.preventDefault()
            return ev
        if key == 'F12':
            return ev
        if key == 'Enter':
            self.do_enter_key(key, mods)
            e.preventDefault()
            return None
        # k.masterKeyHandler will handle everything.
        e.preventDefault()
        return ev

    @flx.reaction('key_press')
    def on_key_press(self, *events):
        """Pass *all* keys Leo's core."""
        for ev in events:
            # print('mini.on_key_press: %r %r' % (ev ['modifiers'], ev['key']))
            self.root.do_key(ev, 'minibufferWidget')
    #@+node:ekr.20181129174405.1: *4* flx_minibuffer.do_enter_key
    def do_enter_key(self, key, mods):
        """
        Handle the enter key in the minibuffer.
        This will only be called if the user has entered the minibuffer via a click.
        """
        command = self.editor.getValue()
        if 'keys' in g.app.debug:
            print('mini.do_enter_key', repr(command))
        if command.strip():
            if command.startswith('full-command:'):
                command = command[len('full-command:') :].strip()
                self.root.do_command(command, 'Enter', [])
            elif command.startswith('Enter Headline:'):
                headline = command[len('Enter Headline:') :].strip()
                self.root.edit_headline_completer(headline)
            else:
                self.root.do_command(command, key, mods)
    #@-others
#@+node:ekr.20181104082201.1: *3* class LeoFlexxStatusLine
class LeoFlexxStatusLine(flx.Widget):

    def init(self):
        self.tag = 'flx.status'
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
        """Allow only F-keys, Ctrl-C and Ctrl-S."""
        ev = self._create_key_event(e)
        key, mods = ev['key'], ev['modifiers']
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
        """Pass Ctrl-S to Leo."""
        for ev in events:
            key, mods = ev['key'], ev['modifiers']
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
        self.tag = 'flx.tree'
        # Init local ivars...
        self.populated_items_dict = {}  # Keys are ap **keys**, values are True.
        self.populating_tree_item = None  # The LeoTreeItem whose children are to be populated.
        self.selected_ap = {}  # The ap of the presently selected node.
        self.tree_items_dict = {}  # Keys are ap's. Values are LeoTreeItems.
        # Init the widget. The max_selected property does not seem to work.
        self.tree = flx.TreeWidget(flex=1, max_selected=1)

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
        """
        Completely clear the tree, preparing to recreate it.

        Important: we do *not* clear self.tree itself!
        """
        trace = 'drawing' in g.app.debug
        tag = 'flx.tree.clear_tree'
        # pylint: disable=access-member-before-definition
        items = list(self.tree_items_dict.values())
        if trace:
            print('')
            print('%s: %s items' % (tag, len(items)))
        #
        # Clear *all* references first.
        self.tree_items_dict = {}
        self.populated_items_dict = {}
        self.populating_tree_item = None
        #
        # Clear all tree items.
        for item in items:
            if trace:
                print('  %r %s' % (item, item.text))
            item.dispose()
    #@+node:ekr.20181113043004.1: *5* flx_tree.action.redraw_with_dict & helper
    @flx.action
    def redraw_with_dict(self, redraw_dict, redraw_instructions):
        """
        Clear the present tree and redraw using the **recursive** redraw_list.
        d has the form:
            {
                'c.p': self.p_to_ap(p),
                'items': [
                    self.make_dict_for_position(p)
                        for p in c.rootPosition().self_and_siblings()
                ],
            }
        """
        # This is called only from app.action.redraw.
        trace = 'drawing' in g.app.debug
        tag = 'redraw_with_dict'
        assert redraw_dict
        self.clear_tree()
        items = redraw_dict['items']
        if trace:
            print('')
            print('%s: %s direct children' % (tag, len(items)))
        for item in items:
            tree_item = self.create_item_with_parent(item, self.tree)
            if trace:
                print('  %r %s' % (tree_item, item['headline']))
        #
        # Select c.p.
        self.select_ap(redraw_dict['c.p'])
        redraw_dict = {}  # #1127: Remove references to deleted items.
    #@+node:ekr.20181124194248.1: *6* tree.create_item_with_parent
    def create_item_with_parent(self, item, parent):
        """Create a tree item for item and all its visible children."""
        # pylint: disable=no-member
            # set_collapsed is in the base class.
        trace = 'drawing' in g.app.debug
        tag = 'create_item_with_parent'
        ap = item['ap']
        #
        # Create the node.
        with parent:
            tree_item = LeoFlexxTreeItem(ap, text=ap['headline'], checked=None, collapsed=True)
        tree_item.set_collapsed(not ap['expanded'])
        #
        # Set the data.
        key = self.ap_to_key(ap)
        self.tree_items_dict[key] = tree_item
        #
        # Children are *not* necessarily sent, so set the populated 'bit' only if they are.
        if item['children']:
            if trace:
                print(tag, '**populated**', ap['headline'])
            self.populated_items_dict[key] = True
        if hasattr(parent, 'leo_children'):
            # print(tag, parent.leo_ap['headline'], ap['headline'])
            parent.leo_children.append(tree_item)
        #
        # Create the children.
        for child in item['children']:
            self.create_item_with_parent(child, tree_item)
        return tree_item  # Debugging
    #@+node:ekr.20181114072307.1: *5* flx_tree.ap_to_key
    def ap_to_key(self, ap):
        """Produce a key for the given ap."""
        self.assert_exists(ap)
        childIndex = ap['childIndex']
        gnx = ap['gnx']
        headline = ap['headline']
        stack = ap['stack']
        stack_s = '::'.join([
            'childIndex: %s, gnx: %s' % (z['childIndex'], z['gnx'])
                for z in stack
        ])
        key = 'Tree key<childIndex: %s, gnx: %s, %s <stack: %s>>' % (
            childIndex, gnx, headline, stack_s or '[]')
        return key
    #@+node:ekr.20181113085722.1: *5* flx_tree.dump_ap
    def dump_ap(self, ap, padding, tag):
        """Print an archived position fully."""
        stack = ap['stack']
        if not padding:
            padding = ''
        padding = padding + ' ' * 4
        if stack:
            print('%s%s:...' % (padding, tag or 'ap'))
            padding = padding + ' ' * 4
            print('%schildIndex: %s v: %s %s stack: [' % (
                padding,
                str(ap['childIndex']),
                ap['gnx'],
                ap['headline'],
            ))
            padding = padding + ' ' * 4
            for d in ap['stack']:
                print('%s%s %s %s' % (
                    padding,
                    str(d['childIndex']).ljust(3),
                    d['gnx'],
                    d['headline'],
                ))
            padding = padding[:-4]
            print(']')
        else:
            print('%s%s: childIndex: %s v: %s stack: [] %s' % (
                padding, tag or 'ap',
                str(ap['childIndex']).ljust(3),
                ap['gnx'],
                ap['headline'],
            ))
    #@+node:ekr.20181104080854.3: *5* flx_tree.reaction: on_tree_event
    # actions: set_checked, set_collapsed, set_parent, set_selected, set_text, set_visible
    @flx.reaction(
        'tree.children**.checked',
        'tree.children**.collapsed',
        'tree.children**.visible',  # Never seems to fire.
    )
    def on_tree_event(self, *events):
        for ev in events:
            expand = not ev.new_value
            if expand:
                # Don't redraw if the LeoTreeItem has children.
                tree_item = ev.source
                ap = tree_item.leo_ap
                if ap['expanded']:
                    if 0:
                        print('flx.tree.on_tree_event: already expanded', ap['headline'])
                else:
                    ap['expanded'] = True
                    # Populate children, if necessary.
                    self.start_populating_children(ap, tree_item)
    #@+node:ekr.20181120063735.1: *4* flx_tree.Focus
    @flx.action
    def set_focus(self):
        if 'focus' in g.app.debug:
            tag = 'flx.tree.set_focus'
            print('%30s:' % tag)
        self.node.focus()
    #@+node:ekr.20181123165819.1: *4* flx_tree.Incremental Drawing...
    # This are not used, at present, but they may come back.
    #@+node:ekr.20181125051244.1: *5* flx_tree.populate_children
    def populate_children(self, children, parent_ap):
        """
        Populate the children of the given parent.

        self.populating_tree_item is the LeoFlexxTreeItem to be populated.

        children is a list of ap's.
        """
        parent = self.populating_tree_item
        assert parent
        # The expansion bit may have changed?
        assert parent_ap == parent.leo_ap
        # print('flx.tree.populate_children: parent: %r %s children' % (parent, len(children)))
        for child_ap in children:
            self.create_item_with_parent(child_ap, parent)
        self.populating_tree_item = False
    #@+node:ekr.20181111011928.1: *5* flx_tree.start_populating_children
    def start_populating_children(self, parent_ap, parent_tree_item):
        """
        Populate the parent tree item with the children if necessary.

        app.send_children_to_tree should send an empty list
        """
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
        """
        Populate the direct descendants of ap. d is compatible with make_redraw_dict:
            {
                'parent_ap': parent_ap,
                'items': [
                    self.make_dict_for_position(p)
                        for p in for p in p.children()
                ],
            }
        """
        parent_ap = d['parent_ap']
        children = d['items']
        # print('flx.tree.receive_children: %s children' % (len(children)))
        self.populate_children(children, parent_ap)
    #@+node:ekr.20181120061140.1: *4* flx_tree.Key handling
    @flx.emitter
    def key_press(self, e):
        ev = self._create_key_event(e)
        mods, key = ev['modifiers'], ev['key']
        # f_key = not mods and key.startswith('F')
        # print('flx.tree.key_press: %r preventDefault: %s', (ev, not f_key))
        # Use default action for F-Keys.
        if not mods and key.startswith('F'):
            return ev
        # Don't ignore Return
        # if not mods and key == 'Enter':
        #     return ev
        #
        # Prevent default action for all other keys.
        e.preventDefault()
        return ev

    @flx.reaction('tree.key_press')
    def on_key_press(self, *events):
        # print('flx.tree.on_key_press')
        for ev in events:
            self.root.do_key(ev, 'tree')
    #@+node:ekr.20181121195235.1: *4* flx_tree.Selecting...
    #@+node:ekr.20181123171958.1: *5* flx_tree.action.set_ap
    @flx.action
    def set_ap(self, ap):
        """self.selected_ap. Called from app.select_ap."""
        assert ap
        self.selected_ap = ap
        self.select_ap(self.selected_ap)
    #@+node:ekr.20181116083916.1: *5* flx_tree.select_ap
    @flx.action
    def select_ap(self, ap):
        """
        Select the tree item corresponding to the given ap.

        Called from the mutator, and also on_selected_event.
        """
        # print('flx.tree.select_ap', repr(ap), ap ['headline'])
        key = self.ap_to_key(ap)
        item = self.tree_items_dict.get(key)
        if item:
            item.set_selected(True)
            self.selected_ap = ap  # Set the item's selected property.
        else:
            pass  # We may be in the middle of a redraw.
    #@+node:ekr.20181109083659.1: *5* flx_tree.reaction.on_selected_event
    @flx.reaction('tree.children**.selected')  # don't use mode="greedy" here!
    def on_selected_event(self, *events):
        """
        Update c.p and c.p.b when the user selects a new tree node.

        This also gets fired on *unselection* events, which causes problems.
        """
        #
        # Reselect the present ap if there are no selection events.
        # This ensures that clicking a headline twice has no effect.
        if not any([ev.new_value for ev in events]):
                # Must use a comprehension above. flexx can't handle generator expressions.
            ev = events[0]
            self.assert_exists(ev)
            ap = ev.source.leo_ap
            self.assert_exists(ap)
            self.select_ap(ap)
            return
        #
        # handle selection events.
        for ev in events:
            if ev.new_value:  # A selection event.
                ap = ev.source.leo_ap
                # print('on_selected_event: select:', ap['headline'])
                self.select_ap(ap)  # Selects the corresponding LeoTreeItem.
                self.set_ap(ap)  # Sets self.selected_ap.
                # A helper action, calling tree.select.
                self.root.select_tree_using_ap(ap)
    #@-others
#@+node:ekr.20181108233657.1: *3* class LeoFlexxTreeItem
class LeoFlexxTreeItem(flx.TreeItem):

    def init(self, leo_ap):
        # pylint: disable=arguments-differ
        self.leo_ap = leo_ap  # Immutable: Gives access to cloned, marked, expanded fields.
        self.leo_children = []

    def getName(self):
        return 'head'  # Required, for proper pane bindings.

    #@+others
    #@-others
#@-others
#@-leo

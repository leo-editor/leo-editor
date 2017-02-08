# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20170128213103.1: * @file demo.py
#@@first
'''
A plugin that makes making Leo demos easy. See:
https://github.com/leo-editor/leo-editor/blob/master/leo/doc/demo.md

Written by Edward K. Ream, January 29-31, 2017.
Revised by EKR February 6-7, 2017.
'''
#@+<< demo.py imports >>
#@+node:ekr.20170128213103.3: **  << demo.py imports >>
import random
import leo.core.leoGlobals as g
import leo.plugins.qt_events as qt_events
from leo.core.leoQt import QtCore, QtGui, QtWidgets
#@-<< demo.py imports >>
#@@language python
#@@tabwidth -4
#@+others
#@+node:ekr.20170207082108.1: **   top level
#@+node:ekr.20170129230307.1: *3* commands (demo.py)
# Note: importing this plugin creates the commands.

@g.command('demo-next')
def demo_next(self, event=None):
    '''Run the next demo script.'''
    g.trace(g.callers())
    if getattr(g.app, 'demo', None):
        g.app.demo.next()
    else:
        g.trace('no demo instance')
        
@g.command('demo-end')
def demo_end(self, event=None):
    '''End the present demo.'''
    if getattr(g.app, 'demo', None):
        g.app.demo.end()
    else:
        g.trace('no demo instance')
#@+node:ekr.20170128213103.5: *3* init
def init():
    '''Return True if the plugin has loaded successfully.'''
    ok = g.app.gui.guiName() in ('qt', 'qttabs')
    if ok:
        ### g.registerHandler('after-create-leo-frame', onCreate)
        g.plugin_signon(__name__)
    return ok
#@+node:ekr.20170128213103.8: ** class Demo
class Demo(object):
    #@+others
    #@+node:ekr.20170128213103.9: *3* demo.__init__ & init
    def __init__(self, c, trace=False):
        '''Ctor for the Demo class.'''
        self.c = c
        # The *permanent* namespace.
        self.namespace = {
            'c': c,
            'demo': self,
            'g:': g,
            'p': c.p,
            'Label': Label,
            'Callout': Callout,
            'Title': Title,
        }
        # Typing params.
        self.n1 = 0.02 # default minimal typing delay, in seconds.
        self.n2 = 0.175 # default maximum typing delay, in seconds.
        self.speed = 1.0 # Amount to multiply wait times.
        # Converting arguments to demo.key.
        self.filter_ = qt_events.LeoQtEventFilter(c, w=None, tag='demo')
        # Other ivars.
        self.script_list = []
            # A list of strings (scripts).
            # Scripts are removed when executed.
        self.trace = trace
        self.user_dict = {} # For use by scripts.
        self.widgets = [] # References to (popup) widgets created by this class.
        # Create *global* demo commands.
        self.init()
    #@+node:ekr.20170129174128.1: *4* demo.init
    def init(self):
        '''Link the global commands to this class.'''
        old_demo = getattr(g.app, 'demo', None)
        if old_demo:
            old_demo.delete_widgets()
            g.trace('deleting old demo:', old_demo.__class__.__name__)
        g.app.demo = self
    #@+node:ekr.20170128222411.1: *3* demo.Control
    #@+node:ekr.20170207090715.1: *4* demo.bind
    def bind(self, name, object_):
        '''Add the name:object binding to self.namespace.'''
        assert name not in self.namespace, (name, self.namespace)
        self.namespace [name] = object_
        # g.trace(name, object_, object_.__init__)
    #@+node:ekr.20170129174251.1: *4* demo.end
    def end(self):
        '''
        End this slideshow and call teardown().
        This will be called several times if demo scripts call demo.next().
        '''
        # Don't delete widgets here. Use the teardown method instead.
        # self.delete_widgets()
        if g.app.demo:
            g.app.demo = None
            self.teardown()
            g.es_print('End of', self.__class__.__name__)
    #@+node:ekr.20170128213103.30: *4* demo.next & helper
    def next(self):
        '''Execute the next demo script, or call end().'''
        # Don't delete widgets here. Leave that up to the demo scripts!
        # self.delete_widgets()
        if self.script_list:
            # Execute the next script.
            script = self.script_list.pop(0)
            if self.trace: print(script)
            self.setup_script()
            self.exec_node(script)
            self.teardown_script()
        else:
            self.end()
    #@+node:ekr.20170128213103.31: *5* demo.exec_node
    def exec_node(self, script):
        '''Execute the script in node p.'''
        c = self.c
        # g.trace(repr(g.splitLines(script)[0]))
        try:
            c.executeScript(
                namespace=self.namespace,
                script=script,
                raiseFlag=True,
                useSelectedText=False,
            )
        except Exception:
            g.es_exception()
    #@+node:ekr.20170128214912.1: *4* demo.setup & teardown
    def setup(self, p=None):
        '''
        Called before running the first demo script.
        p is the root of the tree of demo scripts.
        May be over-ridden in subclasses.
        '''
        
    def setup_script(self):
        '''
        Called before running each demo script.
        p is the root of the tree of demo scripts.
        May be over-ridden in subclasses.
        '''

    def teardown(self):
        '''
        Called when the demo ends.
        Subclasses may override this.
        '''

    def teardown_script(self):
        '''
        Called when the demo ends.
        Subclasses may override this.
        '''
    #@+node:ekr.20170128213103.33: *4* demo.start & helpers
    def start(self, p=None, script_list=None, script_string=None, delim='###'):
        '''
        Start a demo whose scripts are given by:
        script_string is not None:  a single string, with given delim.
        script_list is not None:    a list of strings,
        p is not None:              The body texts of a tree of nodes.
        '''
        self.delete_widgets()
        if script_string:
            self.script_list = self.parse_script_string(script_string, delim)
        elif script_list:
            self.script_list = script_list[:]
        else:
            self.script_list = self.create_script_list(p)
        if self.script_list:
            self.setup(p)
            self.next()
        else:
            g.trace('no script tree')
            self.end()
    #@+node:ekr.20170129180623.1: *5* demo.create_script_list
    def create_script_list(self, p):
        '''Create the state_list from the tree of script nodes rooted in p.'''
        c = self.c
        aList = []
        after = p.nodeAfterTree()
        while p and p != after:
            if p.h.startswith('@ignore-tree'):
                p.moveToNodeAfterTree()
            elif p.h.startswith('@ignore'):
                p.moveToThreadNext()
            else:
                script = g.getScript(c, p,
                    useSelectedText=False,
                    forcePythonSentinels=False,
                    useSentinels=False,
                )
                if script.strip():
                    aList.append(script)
                p.moveToThreadNext()
        return aList
    #@+node:ekr.20170207080029.1: *5* demo.parse_script_string
    def parse_script_string (self, script_string, delim):
        '''
        script_string is single string, representing a list of script strings
        separated by lines that start with delim.
        
        Return a list of strings.
        '''
        aList = []
        lines = []
        for s in g.splitLines(script_string):
            if s.startswith(delim):
                if lines:
                    aList.append(''.join(lines))
                lines = []
            else:
                lines.append(s)
        if lines:
            aList.append(''.join(lines))
        # g.trace('===== delim', delim) ; g.printList(aList)
        return aList
    #@+node:ekr.20170128213103.43: *4* demo.wait
    def wait(self, n1=None, n2=None):
        '''Wait for an interval between n1 and n2, in seconds.'''
        if n1 is None: n1 = self.n1
        if n2 is None: n2 = self.n2
        if n1 > 0 and n2 > 0:
            n = random.uniform(n1, n2)
        else:
            n = n1
        if n > 0:
            n = n * self.speed
            g.sleep(n)
    #@+node:ekr.20170130090124.1: *3* demo.Menus
    #@+node:ekr.20170128213103.15: *4* demo.dismiss_menu_bar
    def dismiss_menu_bar(self):
        c = self.c
        # c.frame.menu.deactivateMenuBar()
        menubar = c.frame.top.leo_menubar
        menubar.setActiveAction(None)
        menubar.repaint()
    #@+node:ekr.20170128213103.22: *4* demo.open_menu
    def open_menu(self, menu_name):
        '''Activate the indicated *top-level* menu.'''
        c = self.c
        menu = c.frame.menu.getMenu(menu_name)
            # Menu is a qtMenuWrapper, a subclass of both QMenu and leoQtMenu.
        if menu:
            c.frame.menu.activateMenu(menu_name)
        return menu
    #@+node:ekr.20170130090031.1: *3* demo.Keys
    #@+node:ekr.20170130184230.1: *4* demo.set_text_delta
    def set_text_delta(self, delta, w=None):
        '''
        Updates the style sheet for the given widget (default is the body pane).
        Delta should be an int.
        '''
        # Copied from zoom-in/out commands.
        c = self.c
        ssm = c.styleSheetManager
        c._style_deltas['font-size-body'] += delta
        # for performance, don't call c.styleSheetManager.reload_style_sheets()
        sheet = ssm.expand_css_constants(c.active_stylesheet)
        # and apply to body widget directly
        if w is None:
            w = c.frame.body.widget
        try:
            w.setStyleSheet(sheet)
        except Exception:
            g.es_exception()
    #@+node:ekr.20170128213103.11: *4* demo.body_keys
    def body_keys(self, s, undo=False):
        '''Undoably simulate typing in the body pane.'''
        c = self.c
        c.bodyWantsFocusNow()
        p = c.p
        w = c.frame.body.wrapper.widget
        if undo:
            c.undoer.setUndoTypingParams(p, 'typing', oldText=p.b, newText=p.b + s)
                # oldSel=None, newSel=None, oldYview=None)
        for ch in s:
            p.b = p.b + ch
            w.repaint()
            self.wait()
    #@+node:ekr.20170128213103.20: *4* demo.head_keys
    def head_keys(self, s, undo=False):
        '''Undoably simulates typing in the headline.'''
        c, p = self.c, self.c.p
        undoType = 'Typing'
        oldHead = p.h
        tree = c.frame.tree
        p.h = ''
        c.editHeadline()
        w = tree.edit_widget(p)
        if undo:
            undoData = c.undoer.beforeChangeNodeContents(p, oldHead=oldHead)
            dirtyVnodeList = p.setDirty()
            c.undoer.afterChangeNodeContents(p, undoType, undoData,
                dirtyVnodeList=dirtyVnodeList)
        for ch in s:
            p.h = p.h + ch
            tree.repaint() # *not* tree.update.
            self.wait()
            event = self.new_key_event(ch, w)
            c.k.masterKeyHandler(event)
        p.h = s
        c.redraw()
    #@+node:ekr.20170128213103.39: *4* demo.new_key_event
    def new_key_event(self, shortcut, w):
        '''Create a LeoKeyEvent for a *raw* shortcut.'''
        # Using the *input* logic seems best.
        event = self.filter_.create_key_event(
            event=None,
            c=self.c,
            w=w,
            ch=shortcut if len(shortcut) is 1 else '',
            tkKey=None,
            shortcut=shortcut,
        )
        # g.trace('%10r %r' % (shortcut, event))
        return event
    #@+node:ekr.20170128213103.28: *4* demo.key
    def key(self, ch):
        '''Simulate typing a single key'''
        c, k = self.c, self.c.k
        w = g.app.gui.get_focus(c=c, raw=True)
        self.wait()
        event = self.new_key_event(ch, w)
        k.masterKeyHandler(event)
        w.repaint() # Make the character visible immediately.
    #@+node:ekr.20170128213103.23: *4* demo.keys
    def keys(self, s, undo=False):
        '''
        Simulate typing a string of *plain* keys.
        Use demo.key(ch) to type any other characters.
        '''
        c, p = self.c, self.c.p
        if undo:
            c.undoer.setUndoTypingParams(p, 'typing', oldText=p.b, newText=p.b + s)
        for ch in s:
            self.key(ch)
    #@+node:ekr.20170130090141.1: *3* demo.Images (Create classes)
    #@+node:ekr.20170128213103.12: *4* demo.caption & body, log, tree
    def caption(self, s, pane): # To do: center option.
        '''Pop up a QPlainTextEdit in the indicated pane.'''
        parent = self.pane_widget(pane)
        if parent:
            s = s.rstrip()
            if s and s[-1].isalpha(): s = s + '.'
            w = QtWidgets.QPlainTextEdit(s, parent)
            w.setObjectName('screencastcaption')
            self.widgets.append(w)
            w2 = self.pane_widget(pane)
            geom = w2.geometry()
            w.resize(geom.width(), min(150, geom.height() / 2))
            off = QtCore.Qt.ScrollBarAlwaysOff
            w.setHorizontalScrollBarPolicy(off)
            w.setVerticalScrollBarPolicy(off)
            w.show()
            return w
        else:
            g.trace('bad pane: %s' % (pane))
            return None

    def body(self, s):
        return self.caption(s, 'body')

    def log(self, s):
        return self.caption(s, 'log')

    def tree(self, s):
        return self.caption(s, 'tree')
    #@+node:ekr.20170128213103.21: *4* demo.image & helper
    def image(self, fn, center=None, height=None, pane=None, width=None):
        '''Put an image in the indicated pane.'''
        parent = self.pane_widget(pane or 'body')
        if parent:
            w = QtWidgets.QLabel('label', parent)
            fn = self.resolve_icon_fn(fn)
            if not fn: return None
            pixmap = QtGui.QPixmap(fn)
            if not pixmap:
                return g.trace('Not a pixmap: %s' % (fn))
            if height:
                pixmap = pixmap.scaledToHeight(height)
            if width:
                pixmap = pixmap.scaledToWidth(width)
            w.setPixmap(pixmap)
            if center:
                g_w = w.geometry()
                g_p = parent.geometry()
                dx = (g_p.width() - g_w.width()) / 2
                w.move(g_w.x() + dx, g_w.y() + 10)
            w.show()
            self.widgets.append(w)
            return w
        else:
            g.trace('bad pane: %s' % (pane))
            return None
    #@+node:ekr.20170128213103.42: *5* demo.resolve_icon_fn
    def resolve_icon_fn(self, fn):
        '''Resolve fn relative to the Icons directory.'''
        dir_ = g.os_path_finalize_join(g.app.loadDir, '..', 'Icons')
        path = g.os_path_finalize_join(dir_, fn)
        if g.os_path_exists(path):
            return path
        else:
            g.trace('does not exist: %s' % (path))
            return None
    #@+node:ekr.20170130090250.1: *3* demo.Panes & widgets
    #@+node:ekr.20170128213103.13: *4* demo.clear_log
    def clear_log(self):
        '''Clear the log.'''
        self.c.frame.log.clearTab('Log')
    #@+node:ekr.20170128213103.40: *4* demo.delete_widgets
    def delete_widgets(self):
        '''Delete all presently visible widgets.'''
        # g.trace(self) ; g.printList(self.widgets)
        for w in self.widgets:
            w.deleteLater()
        self.widgets = []
    #@+node:ekr.20170128213103.41: *4* demo.pane_widget
    def pane_widget(self, pane):
        '''Return the pane's widget, defaulting to the body pane.'''
        m = self; c = m.c
        d = {
            None: c.frame.body.widget,
            'all': c.frame.top,
            'body': c.frame.body.widget,
            'log': c.frame.log.logCtrl.widget,
            'minibuffer': c.frame.miniBufferWidget.widget,
            'tree': c.frame.tree.treeWidget,
        }
        return d.get(pane)
    #@+node:ekr.20170128213103.26: *4* demo.repaint_pane
    def repaint_pane(self, pane):
        '''Repaint the given pane.'''
        w = self.pane_widget(pane)
        if w:
            w.repaint()
        else:
            g.trace('bad pane: %s' % (pane))
    #@+node:ekr.20170206112010.1: *4* demo.set_position & helpers
    def set_position(self, w, position):
        '''Position w at the given position, or center it.'''
        if position == 'center':
            self.center(w)
            return
        try:
            x, y = position
        except Exception:
            g.es('position must be "center" or a 2-tuple', repr(position))
            return
        if not isinstance(x, int):
            x = x.strip().lower()
        if not isinstance(y, int):
            y = y.strip().lower()
        if x == y == 'center':
            self.center(w)
        elif x == 'center':
            self.center_horizontally(w, y)
        elif y == 'center':
            self.center_vertically(w, x)
        else:
            self.set_x(w, x)
            self.set_y(w, y)
    #@+node:ekr.20170206111124.1: *5* demo.center*
    def center(self, w):
        '''Center this widget in its parent.'''
        g_p = w.parent.geometry()
        x = g_p.width()/2
        y = g_p.height()/2
        w.move(x, y)

    def center_horizontally(self, w, y):
        '''Center w horizontally in its parent, and set its y position.'''
        x = w.parent.geometry().width()/2
        w.move(x, y)

    def center_vertically(self, w, x):
        '''Center w vertically in its parent, setting its x position.'''
        y = w.parent.geometry().height()/2
        w.move(x, y)
    #@+node:ekr.20170206142602.1: *5* demo.set_x/y & helper
    def set_x(self, w, x):
        '''Set our x coordinate to x.'''
        x = self.get_int(x)
        if x is not None:
            w.move(x, w.geometry().y())

    def set_y(self, w, y):
        '''Set our y coordinate to y.'''
        y = self.get_int(y)
        if y is not None:
            w.move(w.geometry().x(), y)
    #@+node:ekr.20170207094113.1: *5* demo.get_int
    def get_int(self, obj):
        '''Convert obj to an int, if needed.'''
        if isinstance(obj, int):
            return obj
        else:
            try:
                return int(obj)
            except ValueError:
                g.es_exception()
                g.trace('bad x position', repr(obj))
                return None
    #@-others
#@+node:ekr.20170208045907.1: ** Graphics classes
#@+node:ekr.20170206203005.1: *3*  class Label (QLabel)
class Label (QtWidgets.QLabel):
    '''A class for user-defined callouts in demo.py.'''
        
    #@+others
    #@+node:ekr.20170207074327.1: *4* label.__init__
    def __init__(self, text,
        font=None,
        position=None,
        stylesheet=None,
    ):
        '''
        Label.__init__. The ctor for all user-defined callout classes.
        Show the callout in the indicated place.
        '''
        c = g.app.demo.c
        self.demo = g.app.demo
        self.parent = c.frame.body.widget
        QtWidgets.QLabel.__init__(self, self.parent)
            # Init the base class
        self.setText(text)
        self._position = position or 'center'
        self._stylesheet = stylesheet or '''\
            QLabel {
                border: 2px solid black;
                background-color : lightgrey;
                color : black;
            }'''
        self._font = font or QtGui.QFont('DejaVu Sans Mono', 16)
        self.init()
        g.app.demo.widgets.append(self)
            # Must be done in all subclasses, so we do it here.
    #@+node:ekr.20170207081055.1: *4* label.init
    def init(self):
        '''Actually set the attributes of the widget.'''
        self.demo.set_position(self, self._position)
        self.setStyleSheet(self._stylesheet)
        self.setFont(self._font)
        self.show()

    #@-others
#@+node:ekr.20170207071819.1: *3* class Callout(Label)
class Callout(Label):
    
    def __init__(self, text, position=None):
        # Init the base class.'''
        Label.__init__(self, text,
            font = QtGui.QFont('DejaVu Sans Mono', 20),
            position = position or 'center',
            stylesheet = '''\
                QLabel {
                    border: 2px solid black;
                    background-color : lightblue;
                    color : black;
                }''')
#@+node:ekr.20170207080814.1: *3* class Title(Label)
class Title(Label):
    
    def __init__(self, text, position=None):
        # Init the base class.
        self.original_position = position
        Label.__init__(self, text,
            position = position, # May be changed in init.
            font = QtGui.QFont('DejaVu Sans Mono', 16),
            stylesheet = '''\
                QLabel {
                    border: 1px solid black;
                    background-color : mistyrose;
                    color : black;
                }'''
            )
            
    def init(self):
        '''Actually set the attributes of the widget.'''
        # The Label ctor will set self._position to its default.
        # We don't want that.
        self._position = (
            self.original_position or
            ('center', self.parent.geometry().height() - 50)
        )
        self.demo.set_position(self, self._position)
        self.setStyleSheet(self._stylesheet)
        self.setFont(self._font)
        self.show()
#@-others
#@-leo

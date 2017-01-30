#@+leo-ver=5-thin
#@+node:ekr.20170128213103.1: * @file demo.py
'''
A plugin that makes making Leo demos easy.
For full details, see leo/docs/demo.md.

Written by Edward K. Ream, January, 2017.
'''
#@+<< demo.py imports >>
#@+node:ekr.20170128213103.3: ** << demo.py imports >>
import random
import leo.core.leoGlobals as g
# import leo.core.leoGui as leoGui # for LeoKeyEvents.
from leo.core.leoQt import QtCore, QtGui, QtWidgets
#@-<< demo.py imports >>
#@@language python
#@@tabwidth -4
#@+others
#@+node:ekr.20170128213103.5: ** init
def init():
    '''Return True if the plugin has loaded successfully.'''
    ok = g.app.gui.guiName() in ('qt', 'qttabs')
    if ok:
        ### g.registerHandler('after-create-leo-frame', onCreate)
        g.plugin_signon(__name__)
    return ok
#@+node:ekr.20170129230307.1: ** commands (demo.py)
# Note: importing this plugin creates the commands.

@g.command('demo-next')
def demo_next(self, event=None):
    if hasattr(g.app, 'demo', None):
        g.app.demo.next()
    else:
        g.trace('no demo instance')
        
@g.command('demo-end')
def demo_end(self, event=None):
    if getattr(g.app, 'demo', None):
        g.app.demo.end()
    else:
        g.trace('no demo instance')
#@+node:ekr.20170128213103.8: ** class Demo
class Demo(object):
    #@+others
    #@+node:ekr.20170128213103.9: *3* demo.__init__ & helpers
    def __init__(self, c):
        '''Ctor for the Demo class.'''
        self.c = c
        # Typing params.
        self.n1 = 0.02 # default minimal typing delay.
        self.n2 = 0.175 # default maximum typing delay.
        self.speed = 1.0 # Amount to multiply wait times.
        # Other ivars.
        self.script_list = []
            # A list of strings (scripts).
            # Scripts are removed when executed.
        self.user_dict = {} # For use by scripts.
        self.widgets = [] # References to (popup) widgets created by this class.
        # Create *global* demo commands.
        self.init()
    #@+node:ekr.20170128213103.40: *4* demo.delete_widgets
    def delete_widgets(self):
        '''Delete all presently visible widgets.'''
        for w in self.widgets:
            w.deleteLater()
        self.widgets = []
    #@+node:ekr.20170129174128.1: *4* demo.init
    def init(self):
        '''Link the global commands to this class.'''
        if hasattr(g.app, 'demo'):
            g.app.demo.delete_widgets()
        g.app.demo = self
    #@+node:ekr.20170128222411.1: *3* demo.Entries & helpers
    #@+node:ekr.20170129180623.1: *4* demo.create_script_list
    def create_script_list(self, p):
        '''Create the state_list from the tree of script nodes rooted in p.'''
        c = self.c
        aList = []
        for p in p.self_and_subtree():
            if p.h.startswith('@ignore'):
                pass
            else:
                script = g.getScript(c, p,
                    useSelectedText=False,
                    forcePythonSentinels=False,
                    useSentinels=False,
                )
                if script.strip():
                    aList.append(script)
        self.script_list = list(reversed(aList))
        
    #@+node:ekr.20170129174251.1: *4* demo.end
    def end(self):
        '''End this slideshow and call teardown().'''
        g.es_print('ending', self.__class__.__name__)
        self.delete_widgets()
        self.teardown()
    #@+node:ekr.20170128213103.31: *4* demo.exec_node
    def exec_node(self, script):
        '''Execute the script in node p.'''
        c = self.c
        # g.trace(repr(g.splitLines(script)[0]))
        try:
            c.executeScript(
                namespace={'c': c, 'demo': self, 'g:': g, 'p': c.p},
                script=script,
                raiseFlag=True,
                useSelectedText=False,
            )
        except Exception:
            g.es_exception()
    #@+node:ekr.20170128213103.30: *4* demo.next
    def next(self):
        '''Execute the next demo script, or call end().'''
        self.delete_widgets()
        if self.script_list:
            # Execute the next script.
            script = self.script_list.pop()
            self.exec_node(script)
        if not self.script_list:
            self.end()
    #@+node:ekr.20170128214912.1: *4* demo.setup & teardown
    def startup(self, p):
        '''
        Called before running the first demo script.
        p is the root of the tree of demo scripts.
        May be over-ridden in subclasses.
        '''

    def teardown(self):
        '''
        Called when the demo ends.
        Subclasses may override this.
        '''
    #@+node:ekr.20170128213103.33: *4* demo.start
    def start(self, p):
        '''Start a demo whose root node is p,'''
        if p:
            self.create_script_list(p)
            self.next()
        else:
            g.trace('no script tree')
            self.end()
    #@+node:ekr.20170128213103.10: *3* demo.Helpers
    #@+node:ekr.20170128213103.11: *4* demo.body_keys
    def body_keys(self, s, n1=None, n2=None):
        '''Simulate typing in the body pane.
        n1 and n2 indicate the range of delays between keystrokes.
        '''
        m = self; c = m.c
        if n1 is None: n1 = 0.02
        if n2 is None: n2 = 0.095
        m.key_w = m.pane_widget('body')
        c.bodyWantsFocusNow()
        p = c.p
        w = c.frame.body.wrapper.widget
        c.undoer.setUndoTypingParams(p, 'typing',
            oldText=p.b, newText=p.b + s, oldSel=None, newSel=None, oldYview=None)
        for ch in s:
            p.b = p.b + ch
            w.repaint()
            m.wait(n1, n2)
        c.redraw()
    #@+node:ekr.20170128213103.12: *4* demo.caption and abbreviations: body, log, tree
    def caption(self, s, pane): # To do: center option.
        '''Pop up a QPlainTextEdit in the indicated pane.'''
        m = self
        parent = m.pane_widget(pane)
        if parent:
            s = s.rstrip()
            if s and s[-1].isalpha(): s = s + '.'
            w = QtWidgets.QPlainTextEdit(s, parent)
            w.setObjectName('screencastcaption')
            m.widgets.append(w)
            w2 = m.pane_widget(pane)
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
    #@+node:ekr.20170128213103.13: *4* demo.clear_log
    def clear_log(self):
        '''Clear the log.'''
        m = self
        m.c.frame.log.clearTab('Log')
    #@+node:ekr.20170128213103.15: *4* demo.dismiss_menu_bar
    def dismiss_menu_bar(self):
        m = self; c = m.c
        # c.frame.menu.deactivateMenuBar()
        g.trace()
        menubar = c.frame.top.leo_menubar
        menubar.setActiveAction(None)
        menubar.repaint()
    #@+node:ekr.20170128213103.19: *4* demo.focus
    def focus(self, pane):
        '''Immediately set the focus to the given pane.'''
        m = self; c = m.c
        d = {
            'body': c.bodyWantsFocus,
            'log': c.logWantsFocus,
            'tree': c.treeWantsFocus,
        }
        f = d.get(pane)
        if f:
            f()
            c.outerUpdate()
            m.repaint(pane)
        else:
            g.trace('bad pane: %s' % (pane))
    #@+node:ekr.20170128213103.20: *4* demo.head_keys
    def head_keys(self, s, n1=None, n2=None):
        '''Simulate typing in the headline.
        n1 and n2 indicate the range of delays between keystrokes.
        '''
        m = self; c = m.c; p = c.p; undoType = 'Typing'
        oldHead = p.h; tree = c.frame.tree
        if n1 is None: n1 = 0.02
        if n2 is None: n2 = 0.095
        p.h = ''
        c.editHeadline()
        w = tree.edit_widget(p)
        # Support undo.
        undoData = c.undoer.beforeChangeNodeContents(p, oldHead=oldHead)
        dirtyVnodeList = p.setDirty()
        c.undoer.afterChangeNodeContents(p, undoType, undoData,
            dirtyVnodeList=dirtyVnodeList)
        # Lock out key handling in m.state_handler.
        m.ignore_keys = True
        try:
            m.key_w = w
            for ch in s:
                p.h = p.h + ch
                tree.repaint() # *not* tree.update.
                m.wait(n1, n2)
                event = m.get_key_event(ch, w)
                c.k.masterKeyHandler(event)
        finally:
            m.ignore_keys = False
        p.h = s
        c.redraw()
    #@+node:ekr.20170128213103.21: *4* demo.image
    def image(self, pane, fn, center=None, height=None, width=None):
        '''Put an image in the indicated pane.'''
        m = self
        parent = m.pane_widget(pane)
        if parent:
            w = QtWidgets.QLabel('label', parent)
            fn = m.resolve_icon_fn(fn)
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
            m.widgets.append(w)
            return w
        else:
            g.trace('bad pane: %s' % (pane))
            return None
    #@+node:ekr.20170128213103.22: *4* demo.open_menu
    def open_menu(self, menu_name):
        '''Activate the indicated *top-level* menu.'''
        m = self; c = m.c
        menu = c.frame.menu.getMenu(menu_name)
            # Menu is a qtMenuWrapper, a subclass of both QMenu and leoQtMenu.
        if menu:
            c.frame.menu.activateMenu(menu_name)
            # g.trace(menu.signalsBlocked())
            if 0: # None of this works.
                g.trace('repaint', c.frame.top)
                c.frame.top.repaint()
                g.trace('repaint', menu)
                menu.repaint()
                parent = menu.parent()
                while parent:
                    g.trace('repaint', parent)
                    parent.repaint()
                    if isinstance(parent, QtWidgets.QMenuBar):
                        break
                    else:
                        parent = parent.parent()
        return menu
    #@+node:ekr.20170128213103.41: *4* demo.pane_widget
    def pane_widget(self, pane):
        '''Return the pane's widget.'''
        c = self.c
        d = {
            'all': c.frame.top,
            'body': c.frame.body.wrapper.widget,
            'log': c.frame.log.logCtrl.widget,
            'minibuffer': c.frame.miniBufferWidget.widget,
            'tree': c.frame.tree.treeWidget,
        }
        return d.get(pane)
    #@+node:ekr.20170128213103.23: *4* demo.plain_keys
    def plain_keys(self, s, n1=None, n2=None, pane='body'):
        '''Simulate typing a string of plain keys.'''
        m = self
        for ch in s:
            m.single_key(ch, n1=n1, n2=n2, pane=pane)
    #@+node:ekr.20170128213103.25: *4* demo.redraw
    def redraw(self, p=None):
        m = self
        m.c.redraw_now(p)
    #@+node:ekr.20170128213103.26: *4* demo.repaint
    def repaint(self, pane):
        '''Repaint the given pane.'''
        m = self
        w = m.pane_widget(pane)
        if w:
            w.repaint()
        else:
            g.trace('bad pane: %s' % (pane))
    #@+node:ekr.20170128213103.42: *4* demo.resolve_icon_fn
    def resolve_icon_fn(self, fn):
        '''Resolve fn relative to the Icons directory.'''
        dir_ = g.os_path_finalize_join(g.app.loadDir, '..', 'Icons')
        path = g.os_path_finalize_join(dir_, fn)
        if g.os_path_exists(path):
            return path
        else:
            g.trace('does not exist: %s' % (path))
            return None
    #@+node:ekr.20170128213103.27: *4* demo.select_position
    def select_position(self, p):
        m = self
        assert p
        m.redraw(p)
    #@+node:ekr.20170128213103.28: *4* demo.single_key
    def single_key(self, ch, n1=None, n2=None, pane=None, w=None):
        '''Simulate typing a single key, properly saving and restoring m.k_state.'''
        m = self; k = m.c.k
        w = w or m.pane_widget(pane or 'body')
        force = n1 is not None or n2 is not None
        if force and n1 is None: n1 = 0.02
        if force and n2 is None: n2 = 0.095
        try:
            if m.k_state.kind:
                # old_state_kind = m.k_state.kind
                k.setState(m.k_state.kind, m.k_state.n, m.k_state.handler)
            else:
                # old_state_kind = None
                k.clearState()
            w.repaint() # *not* tree.update.
            m.wait(n1, n2)
            event = m.get_key_event(ch, w)
            k.masterKeyHandler(event)
        finally:
            # Save k.state in m.k_state.
            if k.state.kind != m.state_name:
                m.set_state(k.state)
            # Important: do *not* re-enable m.state_handler here.
            # This should be done *only* in m.next.
    #@+node:ekr.20170128213103.43: *4* demo.wait
    def wait(self, n1=1, n2=0):
        '''Wait for an interval between n1 and n2.'''
        m = self
        if n1 is None: n1 = 0
        if n2 is None: n2 = 0
        if n1 > 0 and n2 > 0:
            n = random.uniform(n1, n2)
        else:
            n = n1
        if n > 0:
            n = n * m.speed
            g.sleep(n)
    #@-others
#@-others
#@-leo

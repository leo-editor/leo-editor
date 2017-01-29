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
import leo.core.leoGui as leoGui # for LeoKeyEvents.
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
#@+node:ekr.20170129170242.1: ** class DemoState
class DemoState(object):
    '''A class representing the state of a demo.'''
    
    def __init__(self, back_p, next_p, script):
        '''Ctor for the DemoState class.'''
        self.back_p = back_p
        self.next_p = next_p
        self.script = script
#@+node:ekr.20170128213103.8: ** class Demo
class Demo(object):
    #@+others
    #@+node:ekr.20170128213103.9: *3* demo.__init__
    def __init__(self, c):
        self.c = c
        self.commands = []
        self.command_index = 0
        self.log_color = 'black'
        self.log_focus = True # True: writing to log sets focus to log.
        self.ignore_keys = False # True: ignore keys in state_handler.
        self.quit_flag = False # True if m.quit has been called.
        self.k_state = g.bunch(kind=None, n=None, handler=None) # Saved k.state.
        self.key_w = None # Saved widget for passed-along key handling.
        self.n1 = 0.02 # default minimal typing delay.
        self.n2 = 0.175 # default maximum typing delay.
        self.p1 = None # The first slide of the show.
        self.p = None # The present slide of the show.
        self.speed = 1.0 # Amount to multiply wait times.
        self.state_name = 'screencast' # The state name to enable m.state_handler.
        self.node_stack = [] # For m.prev and m.undo.
        self.text_flag = False # True: m.next shows body text instead of executing it.
        self.user_dict = {} # For use by scripts.
        self.widgets = [] # List of (popup) widgets created by this class.
        # inject c.screenCastController
        c.screenCastController = self
    #@+node:ekr.20170128222411.1: *3* demo.Commands
    #@+node:ekr.20170128214606.1: *4* demo.demo
    def demo(self, headline):
        '''Run the demo.'''
        c = self.c
        p = g.findNodeAnywhere(c, headline)
        if p:
            self.setup(p)
            self.start(p)
        else:
            g.trace('node not found:', headline)
    #@+node:ekr.20170128213103.30: *4* demo.next & helper
    def next(self):
        '''Find the next screencast node and execute its script.
        Call m.quit if no more nodes remain.'''
        trace = False and not g.unitTesting
        m = self; c = m.c; k = c.k
        m.delete_widgets()
        # Restore k.state from m.k_state.
        if m.k_state.kind and m.k_state.kind != m.state_name:
            k.setState(kind=m.k_state.kind, n=m.k_state.n, handler=m.k_state.handler)
        while m.p:
            if trace: g.trace(m.p.h)
            h = m.p.h.replace('_', '').replace('-', '')
            if g.match_word(h, 0, '@ignorenode'):
                m.p.moveToThreadNext()
            elif g.match_word(h, 0, '@ignoretree') or g.match_word(h, 0, '@button'):
                m.p.moveToNodeAfterTree()
            elif m.p.b.strip():
                p_next = m.p.threadNext()
                p_old = m.p.copy()
                if g.match_word(m.p.h, 0, '@text'):
                    c.redraw(m.p) # Selects the node, thereby showing the body text.
                else:
                    m.exec_node(m.p)
                # Save k.state in m.k_state.
                if k.state:
                    if k.state.kind == m.state_name:
                        m.clear_state()
                    else:
                        m.set_state(k.state)
                # Re-enable m.state_handler.
                if not m.quit_flag:
                    k.setState(m.state_name, 1, m.state_handler)
                # Change m.p only if the script has not already changed it.
                if not m.p or m.p == p_old:
                    m.p = p_next
                break
            else:
                m.p.moveToThreadNext()
        else:
            # No non-empty node found.
            m.quit()
    #@+node:ekr.20170128213103.31: *5* demo.exec_node
    def exec_node(self, p):
        '''Execute the script in node p.'''
        trace = False and not g.unitTesting
        m = self; c = m.c
        if trace: g.trace(p.h, c.p.v)
        assert p
        assert p.b
        d = {'c': c, 'g:': g, 'm': m, 'p': p}
        tag = 'screencast'
        m.node_stack.append(p)
        try:
            undoData = c.undoer.beforeChangeGroup(c.p, tag, verboseUndoGroup=False)
            c.executeScript(p=p, namespace=d, useSelectedText=False, raiseFlag=True)
            c.undoer.afterChangeGroup(c.p, tag, undoData)
        except Exception:
            g.es_exception()
            m.quit()
    #@+node:ekr.20170128213103.32: *4* demo.prev
    def prev(self):
        '''Show the previous slide.  This will recreate the slide's widgets,
        but the user may have to adjust the minibuffer or other widgets by hand.'''
        trace = False and not g.unitTesting
        m = self
        if m.p and m.p == m.p1:
            g.trace('at start: %s' % (m.p and m.p.h))
            m.start(m.p1)
        else:
            p = m.undo()
            if p and p == m.p1:
                if trace: g.trace('at start: %s' % (m.p and m.p.h))
                m.start(m.p1)
            elif p:
                if trace: g.trace('undo, undo, next: %s' % (m.p and m.p.h))
                m.undo()
                m.next()
            else:
                if trace: g.trace('no undo: restart: %s' % (m.p and m.p.h))
                m.start(m.p1)
    #@+node:ekr.20170128213103.33: *4* demo.start
    def start(self, p):
        '''Start a screencast whose root node is p.

        Important: p is not necessarily c.p!
        '''
        m = self; c = m.c; k = c.k
        assert p
        # Reset Leo's state.
        k.keyboardQuit()
        # Set ivars
        m.p1 = p.copy()
        m.p = p.copy()
        m.quit_flag = False
        m.clear_state()
        p.contract()
        c.redraw_now(p)
        m.delete_widgets()
            # Clear widgets left over from previous, unfinished, slideshows.
        m.state_handler()
    #@+node:ekr.20170128214912.1: *3* demo.setup
    def startup(self):
        '''May be over-ridden in subclasses.'''
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
    #@+node:ekr.20170128213103.14: *4* demo.command
    def command(self, command_name):
        '''Execute the command whose name is given and update the screen immediately.'''
        m = self; c = m.c
        c.k.simulateCommand(command_name)
            # Named commands handle their own undo!
            # The undo handling in m.next should suffice.
        c.redraw_now()
        m.repaint('all')
    #@+node:ekr.20170128213103.15: *4* demo.dismiss_menu_bar
    def dismiss_menu_bar(self):
        m = self; c = m.c
        # c.frame.menu.deactivateMenuBar()
        g.trace()
        menubar = c.frame.top.leo_menubar
        menubar.setActiveAction(None)
        menubar.repaint()
    #@+node:ekr.20170128213103.16: *4* demo.find_screencast & helpers
    def find_screencast(self, p):
        '''Find the nearest screencast, prefering previous screencasts
        because that makes it easier to create screencasts.'''
        m = self
        return m.find_prev_screencast(p) or m.find_next_screencast(p)
    #@+node:ekr.20170128213103.17: *5* demo.find_next_screencast
    def find_next_screencast(self, p):
        # m = self
        p = p.copy()
        while p:
            if p.h.startswith('@screencast'):
                return p
            else:
                p.moveToThreadNext()
        return None
    #@+node:ekr.20170128213103.18: *5* demo.find_prev_screencast
    def find_prev_screencast(self, p):
        # m = self
        p = p.copy()
        while p:
            if p.h.startswith('@screencast'):
                return p
            else:
                p.moveToThreadBack()
        return None
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
    #@+node:ekr.20170128213103.23: *4* demo.plain_keys
    def plain_keys(self, s, n1=None, n2=None, pane='body'):
        '''Simulate typing a string of plain keys.'''
        m = self
        for ch in s:
            m.single_key(ch, n1=n1, n2=n2, pane=pane)
    #@+node:ekr.20170128213103.24: *4* demo.quit
    def quit(self):
        '''Terminate the slide show.'''
        m = self; c = m.c; k = c.k
        if m.quit_flag:
            return
        if not m.p1:
            return
        g.red('end slide show: %s' % (m.p1.h))
        m.delete_widgets()
        k.keyboardQuit()
        m.clear_state()
        m.quit_flag = True
        c.bodyWantsFocus()
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
    #@+node:ekr.20170128213103.29: *3* demo.State handling
    #@+node:ekr.20170128213103.37: *4* demo.set_state & clear_state
    def set_state(self, state):
        m = self
        # g.trace('**** setting m.k_state: %s' % (state.kind))
        m.k_state.kind = state.kind
        m.k_state.n = state.n
        m.k_state.handler = state.handler

    def clear_state(self):
        m = self
        # g.trace('**** clearing m.k_state')
        m.k_state.kind = None
        m.k_state.n = None
        m.k_state.handler = None
    #@+node:ekr.20170128213103.35: *4* demo.state_handler
    def state_handler(self, event=None):
        '''Handle keys while in the "screencast" input state.'''
        trace = True and not g.unitTesting
        k, m = self.c.k, self
        ### state = k.getState(m.state_name)
        char = event and event.char or ''
        if trace:
            g.trace('char: %s k.state.kind: %s m.k_state: %s' % (
                repr(char), repr(k.state.kind),
                m.k_state and repr(m.k_state.kind) or '<none>'))
        if m.ignore_keys:
            return
        # Init the minibuffer as in k.fullCommand.
        if trace: g.trace('=====')
        ### assert m.p1 and m.p1 == m.p
        k.mb_event = event
        k.mb_prefix = k.getLabel()
        k.mb_prompt = 'Screencast: '
        k.mb_tabList = []
        k.setLabel(k.mb_prompt)
        ### k.setState(m.state_name, 1, m.state_handler)
        m.next()
        k.get1Arg(event, handler=self.state_handler1, oneCharacter=True, useMinibuffer=False)
        # Only exit on Ctrl-g.
        # Because of menu handling, it's convenient to have escape go to the next slide.
        # That way an "extra" escape while dismissing menus will be handled well.

    def state_handler1(self, event):
        trace = True and not g.unitTesting
        k, m = self.c.k, self
        char = k.arg
        g.trace(repr(char))
        if char == 'Escape':
            # m.quit()
            m.next()
        elif char == 'Right':
            m.next()
        elif char == 'Left':
            m.prev()
        elif m.k_state.kind != m.state_name:
            # We are simulating another state.
            # Pass the character to *that* state,
            # making *sure* to save/restore all state.
            ### kind, n, handler = k.state.kind, k.state.n, k.state.handler
            m_state_copy = g.bunch(kind=m.k_state.kind,
                n=m.k_state.n, handler=m.k_state.handler)
            m.single_key(char)
            ### k.setState(kind, n, handler)
            m.set_state(m_state_copy)
        elif trace:
            g.trace('ignore %s' % (repr(char)))
    #@+node:ekr.20170128213103.36: *4* demo.undo
    def undo(self):
        '''Undo the previous screencast scene.'''
        m = self
        m.delete_widgets()
        if m.node_stack:
            c = m.c
            m.p = m.node_stack.pop()
            c.undoer.undo()
            c.redraw()
            return m.p
        else:
            return None
    #@+node:ekr.20170128213103.38: *3* demo.Utilities
    #@+node:ekr.20170128213103.39: *4* demo.get_key_event
    def get_key_event(self, ch, w):
        m = self; c = m.c; k = c.k
        m.key_w = w
        if len(ch) > 1:
            key = None
            stroke = k.strokeFromSetting(ch).s
        else:
            stroke = key = ch
        # g.trace(ch,key,stroke)
        return leoGui.LeoKeyEvent(c, key, stroke,
            shortcut=None,
            w=w,
            x=0, y=0,
            x_root=0, y_root=0)
    #@+node:ekr.20170128213103.40: *4* demo.delete_widgets
    def delete_widgets(self):
        m = self
        for w in m.widgets:
            w.deleteLater()
        m.widgets = []
    #@+node:ekr.20170128213103.41: *4* demo.pane_widget
    def pane_widget(self, pane):
        '''Return the pane's widget.'''
        m = self; c = m.c
        d = {
            'all': c.frame.top,
            'body': c.frame.body.wrapper.widget,
            'log': c.frame.log.logCtrl.widget,
            'minibuffer': c.frame.miniBufferWidget.widget,
            'tree': c.frame.tree.treeWidget,
        }
        return d.get(pane)
    #@+node:ekr.20170128213103.42: *4* demo.resolve_icon_fn
    def resolve_icon_fn(self, fn):
        '''Resolve fn relative to the Icons directory.'''
        # m = self
        dir_ = g.os_path_finalize_join(g.app.loadDir, '..', 'Icons')
        path = g.os_path_finalize_join(dir_, fn)
        if g.os_path_exists(path):
            return path
        else:
            g.trace('does not exist: %s' % (path))
            return None
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
            # g.trace(n)
            g.sleep(n)
    #@-others
#@-others
#@-leo

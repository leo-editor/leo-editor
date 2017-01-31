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
    def __init__(self, c, description=None):
        '''Ctor for the Demo class.'''
        self.c = c
        self.description = description or self.__class__.__name__
        # Typing params.
        self.n1 = 0.02 # default minimal typing delay, in seconds.
        self.n2 = 0.175 # default maximum typing delay, in seconds.
        self.speed = 1.0 # Amount to multiply wait times.
        # Other ivars.
        self.script_list = []
            # A list of strings (scripts).
            # Scripts are removed when executed.
        self.user_dict = {} # For use by scripts.
        self.widgets = [] # References to (popup) widgets created by this class.
        # Create *global* demo commands.
        self.init()
    #@+node:ekr.20170129180623.1: *4* demo.create_script_list
    def create_script_list(self, p):
        '''Create the state_list from the tree of script nodes rooted in p.'''
        c = self.c
        aList = []
        after = p.nodeAfterTree()
        # for p in p.self_and_subtree():
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
        self.script_list = list(reversed(aList))
    #@+node:ekr.20170128213103.40: *4* demo.delete_widgets
    def delete_widgets(self):
        '''Delete all presently visible widgets.'''
        for w in self.widgets:
            w.deleteLater()
        self.widgets = []
    #@+node:ekr.20170129174128.1: *4* demo.init
    def init(self):
        '''Link the global commands to this class.'''
        old_demo = getattr(g.app, 'demo', None)
        if old_demo:
            old_demo.delete_widgets()
            g.trace('deleting old demo:', old_demo.description)
        g.app.demo = self
    #@+node:ekr.20170128222411.1: *3* demo.Commands
    #@+node:ekr.20170129174251.1: *4* demo.end
    def end(self):
        '''End this slideshow and call teardown().'''
        # Don't delete widgets here. Use the teardown method instead.
        # self.delete_widgets()
        self.teardown()
        g.trace(self.__class__.__name__)
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
        # Don't delete widgets here. Leave that up to the demo scripts!
        # self.delete_widgets()
        if self.script_list:
            # Execute the next script.
            script = self.script_list.pop()
            self.exec_node(script)
        if not self.script_list:
            self.end()
    #@+node:ekr.20170128214912.1: *4* demo.setup & teardown
    def setup(self, p):
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
            self.setup(p)
            self.next()
        else:
            g.trace('no script tree')
            self.end()
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
        trace = False and not g.unitTesting
        c, k = self.c, self.c.k
        # Tricky: Canonicalize the shortcut, without making it a stroke.
        if 1: # A bad hack. Temporary.
            if shortcut == '\n':
                char = '\n'
                shortcut2 = 'Return'
            elif shortcut == '\t':
                char = 'tab'
                shortcut2 = 'Tab'
            else:
                stroke = k.strokeFromSetting(shortcut)
                shortcut2 = stroke.s if stroke else ''
                char = '' if len(shortcut) > 1 else shortcut
        else:
            stroke = k.strokeFromSetting(shortcut)
            shortcut2 = stroke.s if stroke else ''
            char = '' if len(shortcut) > 1 else shortcut
        if trace: g.trace('%r -> %r' % (shortcut, shortcut2))
        return leoGui.LeoKeyEvent(c,
            char=char, event=None, shortcut=shortcut2, w=w)
    #@+node:ekr.20170130160749.1: *4* demo.save/restore_key_state
    def save_key_state(self):
        '''Save the key handler state, if any.'''
        k = self.c.k
        state = k.state
        if state.kind is not None:
            label = k.getLabel()
            self.saved_key_state = state.kind, state.n, state.handler, label
        # g.trace('=====', self.saved_key_state)

    def restore_key_state(self):
        '''Restore the key handler state, if any.'''
        k = self.c.k
        if self.saved_key_state:
            # g.trace('-----', self.saved_key_state)
            k.state.kind, k.state.n, k.state.handler, label = self.saved_key_state
            if label: k.setLabel(label)
            self.saved_key_state = None
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
    def keys(self, s):
        '''
        Simulate typing a string of *plain* keys.
        Use demo.key(ch) to type any other characters.
        '''
        c, p = self.c, self.c.p
        c.undoer.setUndoTypingParams(p, 'typing',
            oldText=p.b, newText=p.b + s, oldSel=None, newSel=None, oldYview=None)
        for ch in s:
            self.key(ch)
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
    #@+node:ekr.20170130090141.1: *3* demo.Images
    #@+node:ekr.20170128213103.12: *4* demo.caption and abbreviations: body, log, tree
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
    #@+node:ekr.20170128213103.21: *4* demo.image
    def image(self, pane, fn, center=None, height=None, width=None):
        '''Put an image in the indicated pane.'''
        parent = self.pane_widget(pane)
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
    #@+node:ekr.20170130090250.1: *3* demo.Panes & widgets
    #@+node:ekr.20170128213103.13: *4* demo.clear_log
    def clear_log(self):
        '''Clear the log.'''
        self.c.frame.log.clearTab('Log')
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
    #@+node:ekr.20170128213103.26: *4* demo.repaint_pane
    def repaint_pane(self, pane):
        '''Repaint the given pane.'''
        w = self.pane_widget(pane)
        if w:
            w.repaint()
        else:
            g.trace('bad pane: %s' % (pane))
    #@-others
#@-others
#@-leo

# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20170128213103.1: * @file demo.py
#@@first
'''
A plugin that makes making Leo demos easy. See:
https://github.com/leo-editor/leo-editor/blob/master/leo/doc/demo.md

Written by Edward K. Ream, January 29-31, 2017.
'''
#@+<< demo.py imports >>
#@+node:ekr.20170128213103.3: ** << demo.py imports >>
import random
import leo.core.leoGlobals as g
import leo.plugins.qt_events as qt_events
from leo.core.leoQt import QtCore, QtGui, QtWidgets

# For callout stuff.
Qt = QtCore.Qt
QBrush = QtGui.QBrush
QColor = QtGui.QColor
QImage = QtGui.QImage
QPainter = QtGui.QPainter
QPainterPath = QtGui.QPainterPath
QPixmap = QtGui.QPixmap
QPoint = QtCore.QPoint
QRect = QtCore.QRect
QRegion = QtGui.QRegion
QSize = QtCore.QSize
QWidget = QtWidgets.QWidget
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
#@+node:ekr.20170206103122.5: ** class Callout (QWidget)
# http://stackoverflow.com/questions/16519621/implementing-pyside-callout

class Callout(QWidget):
    #@+others
    #@+node:ekr.20170206103122.6: *3* callout.__init__
    def __init__(self, text, parent=None, color=None, font=None):
        '''Create a callout.'''
        super(Callout, self).__init__(parent)
        self.text=text
        self.color = color if color else QColor(192, 192, 192)
            # A grey background by default.
        self.font = font if font else QtGui.QFont('DejaVu Sans Mono', 14)
        self.setWindowFlags(Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        # Measure the width of the text.
        fm = QtGui.QFontMetrics(self.font)
        r = fm.boundingRect(text)
        w, h = r.width() + 20, r.height() + 18
        # w, h = fm.width(text) + 20, fm.height() + 18
        self.setMinimumSize(w, h)
        r = self.createRegion(bubbleSize=QSize(w,h))
        self.setMask(r)
    #@+node:ekr.20170206103122.2: *3* callout.createMask
    def createMask(self,size):
        w=size.width()
        h=size.height()
        img=QImage(size, QImage.Format_MonoLSB)
        qp=QtGui.QPainter()
        qp.begin(img)
        qp.fillRect(QRect(QPoint(0, 0), size), QColor(255,255,255))
        path=QPainterPath()
        path.moveTo(0, h-1)
        path.lineTo(w-1,0)
        path.lineTo(h-1, 0)
        path.lineTo(0, h-1)
        qp.fillPath(path, QBrush(QColor(0, 0, 0)))
        qp.end()
        return img
    #@+node:ekr.20170206103122.4: *3* callout.createRegion
    def createRegion(self, bubbleSize, pointSize=None, offset=None):
        r = self.createRoundedRectRegion(
            rect = QRect(QPoint(0, 0), bubbleSize),
            radius = 10)
        ### bt=QRegion(QPixmap(createMask(pointSize)))
        ### t.translate(offset, bubbleSize.height())
        ### r|=t
        return r
    #@+node:ekr.20170206103122.3: *3* callout.createRoundedRectRegion
    def createRoundedRectRegion(self, rect, radius):
        
        r=QtGui.QRegion(rect.adjusted(radius, 0, -radius, 0))
        r|=QRegion(rect.adjusted(0, radius, 0, -radius))
        r|=QRegion(rect.left(), rect.top(),
            2*radius, 2*radius, QRegion.Ellipse)
        r|=QRegion(rect.right()-2*radius, rect.top(),
            2*radius, 2*radius, QRegion.Ellipse)
        r|=QRegion(rect.left(), rect.bottom()-2*radius,
            2*radius, 2*radius, QRegion.Ellipse)
        r|=QRegion(rect.right()-2*radius, rect.bottom()-2*radius,
            2*radius, 2*radius, QRegion.Ellipse)
        return r
    #@+node:ekr.20170206103122.7: *3* callout.paintEvent
    def paintEvent(self, event):
        
        painter = QPainter()
        painter.begin(self)
        if self.font:
            painter.setFont(self.font)
        painter.fillRect(0, 0, self.width(), 200, self.color)
        painter.drawText(
            QRect(0, 0, self.width(), 50),
            Qt.AlignCenter,
            self.text,
        )
        painter.end()
    #@-others
#@+node:ekr.20170128213103.8: ** class Demo
class Demo(object):
    #@+others
    #@+node:ekr.20170128213103.9: *3* demo.__init__ & helpers
    def __init__(self, c,
        color=None,
        font=None,
        subtitle_color=None,
        subtitle_font=None,
        trace=False,
    ):
        '''Ctor for the Demo class.'''
        self.c = c
        self.description = self.__class__.__name__
        # Config...
        self.color = color
        self.font = font
        self.subtitle_color = subtitle_color
        self.subtitle_font = subtitle_font
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
    #@+node:ekr.20170129180623.1: *4* demo.create_script_list
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
        '''
        End this slideshow and call teardown().
        This will be called several times if demo scripts call demo.next().
        '''
        # Don't delete widgets here. Use the teardown method instead.
        # self.delete_widgets()
        if g.app.demo:
            g.app.demo = None
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
            script = self.script_list.pop(0)
            if self.trace: print(script)
            self.exec_node(script)
        else:
            self.end()
    #@+node:ekr.20170128214912.1: *4* demo.setup & teardown
    def setup(self, p=None):
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
    def start(self, p=None, script_list=None):
        '''Start a demo whose root node is p,'''
        self.delete_widgets()
        if script_list:
            self.script_list = script_list[:]
        else:
            self.script_list = self.create_script_list(p)
        if self.script_list:
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
    #@+node:ekr.20170130090141.1: *3* demo.Images
    #@+node:ekr.20170206100558.1: *4* demo.callout
    def callout(self, s, pane=None, position=None):
        '''
        Show a highlighted, auto-sized message s at the given position. Use a
        standard location if none is given.
        '''
        parent = self.pane_widget(pane)
        w = Callout(s, parent, color=self.color, font=self.font)
        self.widgets.append(w)
        self.set_position(position, parent, w)
        w.show()
        return w
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
    #@+node:ekr.20170206100605.1: *4* demo.subtitle
    def subtitle(self, s, pane=None, position=None):
        '''
        Show a subtitle s at the given location on the screen. Use a standard
        location if none is given.
        '''
        parent = self.pane_widget(pane)
        w = Callout(s, parent, color=self.subtitle_color, font=self.subtitle_font)
        self.widgets.append(w)
        if not position:
            # Unlike callouts, the standard position is near the bottom.
            y = parent.geometry().height() - 50
            position = ('center', y)
        self.set_position(position, parent, w)
        w.show()
        return w
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
    #@+node:ekr.20170206132709.1: *3* demo.positioning
    #@+node:ekr.20170206111124.1: *4* demo.center
    def center(self, w, parent):
        '''Center widget w in its parent.'''
        g_p = parent.geometry()
        x = g_p.width()/2
        y = g_p.height()/2
        w.move(x, y)
    #@+node:ekr.20170206132754.1: *4* demo.center_horizontally
    def center_horizontally(self, y, parent, w):
        '''Center w horizontally in its parent, and set its y position.'''
        x = parent.geometry().width()/2
        w.move(x, y)
    #@+node:ekr.20170206132802.1: *4* demo.center_vertically
    def center_vertically(self, x, parent, w):
        '''Center w vertically in its parent, setting its x position.'''
        y = parent.geometry().height()/2
        w.move(x, y)
    #@+node:ekr.20170206112010.1: *4* demo.set_position
    def set_position(self, position, parent, w):
        '''Position w at the given position, or center it.'''
        if position:
            try:
                x, y = position
            except Exception:
                g.es('position argument must be a 2-tuple')
                return
            if not isinstance(x, int):
                x = x.strip().lower()
            if not isinstance(y, int):
                y = y.strip().lower()
            if x == y == 'center':
                self.center(parent, w)
            elif x == 'center':
                self.center_horizontally(y, parent, w)
            elif y == 'center':
                self.center_vertically(x, parent, w)
            else:
                self.set_x(x, w)
                self.set_y(y, w)
        else:
            self.center(w, parent)
    #@+node:ekr.20170206142602.1: *4* demo.set_x/y
    def set_x(self, x, w):
        '''Set the x coordinate of w to x.'''
        if not isinstance(x, int):
            try:
                x = int(x)
            except ValueError:
                g.es_exception()
                g.trace('bad x position', repr(x))
                return
        w.move(x, w.geometry().y())

    def set_y(self, y, w):
        '''Set the y coordinate of w to y.'''
        if not isinstance(y, int):
            try:
                y = int(y)
            except ValueError:
                g.es_exception()
                g.trace('bad x position', repr(y))
                return
        w.move(w.geometry().x(), y)
    #@+node:ekr.20170128213103.43: *3* demo.wait
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
    #@-others
#@-others
#@-leo

#@+leo-ver=5-thin
#@+node:ekr.20120913110135.10579: * @file ../plugins/screencast.py
#@+<< docstring >>
#@+node:ekr.20120913110135.10589: ** << docstring >>
#@@language rest

r"""

Overview
========

This plugin is a tool for people wanting to demonstrate Leo or some Leonine
project to others. Using this plugin, a human demonstrator can prepare an
automated talk ahead of time. The talk is a series of slides created by Leo
itself. Each slide is simply Leo as it appears at a particular time. When
giving the talk, the presenter moves from one slide to the next by hitting
the RtArrow (Right Arrow) key. The presenter may also back up from the
present slide to the previous slide using the LtArrow (Left Arrow) key.

To create the presentation, the presenter creates an **@screencast** node.
This node, and all its descendants, is called the **controlling tree**.
Each node of this tree may contain a script in its body text; each script
creates a slide. Nodes without scripts can be used as organizer nodes as
usual. **@ignore-node** nodes and **@ignore-tree** trees are ignored.
Normally, the controlling tree will be hidden from view during the
presentation--the presentation will be about *other* parts of the tree.

The screencast-start command starts a screencast. This command shows the
first slide of the nearest \@screencast node. Thereafter, the plugin
executes the next script in controlling tree when the demonstrator types
the RtArrow key. These scripts are normal Leo scripts, except that they
also have access to an "m" variable that denotes a **ScreenCastController**
(SCC), an object created by this plugin. The term **screencast script**
denotes a script that has access to the "m" variable.

The SCC provides convenience methods that screencast scripts can use to
draw attention to various parts of Leo's screen. A typical script will
consist of just one or two of the following calls:

- **m.image(file_name)** overlays a scaled image on Leo's window. For
  example, a screencast could discuss Leo's icon box by shown greatly
  magnified images of various kinds of icon box.

- **m.body(text)** overlays a caption on Leo's body pane. By default,
  captions have a bright yellow background so that they clearly stand out
  from the normal appearance of Leo's screen. Similarly **m.log(text)** and
  **m.tree(text)** overlay captions on Leo's log and tree panes.

- **m.body_keys(text)** and **m.head_keys(text)** animate typing of text in
  body text and headlines respectively.

- **m.single_key(key_setting)** allows any key to be handled exactly as if
  the user had typed the key.

- **m.open_menu(menu_name)** opens a menu as if the demonstrator had opened it
  with a mouse click. **m.dismiss_menubar()** closes all open menus.

To summarize: the presenter moves from slide to slide using the RtArrow
key. The RtArrow key causes the SCC executes the next script in the
controlling tree. The script alters the screen, say by selecting inserting,
deleting, expanding and contracting nodes, or by inserting, deleting or
changing headline or body text. The script will typically also show images
or captions to highlight what the slide is supposed to be showing. In
short:

- A screencast is a sequence of slides.  A slide is the appearance
  of Leo after a screencast script is executed.

- The human presenter moves to the next slide using the RtArrow key.
  The LtArrow key moves back to the previous slide.

- Scripts in an \@screencast tree create slides. The 'm' variable allows
  such scripts to animate keystrokes or overlay images or captions on the
  screen.

Before reading further, please look at the example \@screencast trees in
test.leo. Then run those screencasts to see the what the scripts do.


Reference
=========

The screencast-start command
----------------------------

The screencast-start command starts a screencast. This command first
searches backwards for the nearest \@screencast node. If no such node is
found, the command searches forwards for the next \@screencast node. This
command then executes the script in the body text, and pauses. Thereafter,
the Right Arrow key executes the script in the next slide node (in outline
order). The Left Arrow key executes the script in the previous slide node.
The Escape or Ctrl-G keys terminate any screencast.

Screencast scripts
------------------

Screencast scripts are Leo scripts that have access to the 'm' variable,
which is bound to c.screencastController, and instance of
ScreenCastController. Such scripts typically use 'm' to access convenience
methods, but advanced scripts can use 'm' in other ways.

The ScreenCastController
------------------------

The ScreenCastController (SCC) controls key handling during screencasts and
executes screencast scripts as the screencast moves from node to node.

The SCC only traps the RtArrow and LtArrow keys during a screencast. The
SCC passes all other keys to Leo's key-handling code. This allows key
handling in key-states during the execution of a screencast. For example::

    m.single_key('Alt-X')
    m.plain_keys('ins\\tno\\t\\n')

actually executes the insert-node command!

SCC methods
-----------

The following paragraphs discuss the SCC methods that screencasts scripts
may use.

**m.body(s)**, **m.log(s)** and **m.tree(s)** create a caption with text s
in the indicated pane. A **caption** is a text area that overlays part of
Leo's screen. By default, captions have a distinctive yellow background.
The appearance of captions can be changed using Qt stylesheets. See below.

**m.body_keys(s,n1=None,n2=None)** Draws the string s in the body pane of
the presently selected node. n1 and n2 give the range of delays to be
inserted between typing. If n1 and n2 are both None, values are given that
approximate a typical typing rate.

**m.command(command_name)** Executes the named command.

**m.dismiss_menubar()** Dismisses the menu opened with m.open_menu.

**m.focus(pane)** Immediately forces focus to the indicated pane. Valid
values are 'bodly', 'log' or 'tree'.

**m.image(pane,fn,center=None,height=None,width=None)** Overlays an image
in a pane. The valid values for `pane` are 'body', 'log' or 'tree'. `fn` is
the path to the image file, resolved to the leo/Icons directory if fn is a
relative path. If `height` is given, the image is scaled so it is height
pixels high. If `width` is given, the image is scaled so it width pixels
wide. If `center` is True, the image is centered horizontally in the given
pane.

**m.head_keys(s,n1=None,n2=None)** Same as m.body_keys, except that the
keys are "typed" into the headline of the presently selected node.

**m.open_menu(menu_name)** Opens the menu whose name is given, ignoring
case and any non-alpha characters in menu_name. This method shows all
parent menus, so m.open_menu('cursorback') suffices to show the
"Cmds\:Cursor/Selection\:Cursor Back..." menu.

**m.plain_keys(s,n1=None,n2=None,pane='body')** Same as m.body_keys, except
that the keys are typed into the designated pane. The valid values for the
'pane' argument are 'body','log' or 'tree'.

**m.quit** ends the screencast. By definition, the last slide of screencast
is the screencast node that calls m.quit.

**m.redraw(p)** Forces an immediate redraw of the outline pane. If p is
given, that position becomes c.p, the presently selected node.

**m.selectPosition(p)** Same as m.redraw(p)

**m.single_key(setting)** generates a key event. Examples::

   m.single_key('Alt-X') # Activates the minibuffer
   m.single_key('Ctrl-F') # Activates Leo's Find command

The 'setting' arg can be anything that would be a valid key setting. The
following are equivalent: "ctrl-f", "Ctrl-f", "Ctrl+F", etc., but "ctrl-F"
is different from "ctrl-shift-f".

**m.start(p)** Starts a screencast at node p, regardless of whether p is an
\@screencast node. This is useful during development while testing the
script in node p.

The program counter, m.p
------------------------

Most presenters will want to keep the nodes of the presentation tree
hidden. Instead, presentation will make *other* nodes visible by calling
m.selectPosition(p) or m.redraw(p).

Thus, there must be a sharp distinction between the presently *selected*
node, c.p, and the present screencast node, m.p. You can think of m.p as
the program counter for the screencast.

By default, after executing a screencast script, the SCC advances m.p to
the next non-empty, non-ignored node in the \@screencast tree. However, if
the just-executed screencast script has set m.p to a new, non-empty value,
that value will be the new value of m.p.

Stylesheets
-----------

Presenters may alter the appearance of captions by using changing the
following stylesheet::

    QPlainTextEdit#screencastcaption {
        background-color: yellow;
        font-family: DejaVu Sans Mono;
        font-size: 18pt;
        font-weight: normal; /* normal,bold,100,..,900 */
        font-style: normal; /* normal,italic,oblique */
    }

You will find this stylesheet in the node @data
``qt-gui-plugin-style-sheet`` in leoSettings.leo or myLeoSettings.leo.


"""
#@-<< docstring >>
#@+<< imports >>
#@+node:ekr.20120913110135.10590: ** << imports >>
import random
from leo.core import leoGlobals as g
from leo.core import leoGui  # for LeoKeyEvents.
from leo.core.leoQt import QtGui, QtWidgets
from leo.core.leoQt import ScrollBarPolicy
#
# Fail fast, right after all imports.
g.assertUi('qt')  # May raise g.UiTypeException, caught by the plugins manager.
#@-<< imports >>
# pylint: disable=not-callable
#@+at
# To do:
# - Document this plugin in the docstring and with a screencast.
# - Commands that invoke screencasts.
#@@c
#@@language python
#@@tabwidth -4
#@+others
#@+node:ekr.20120913110135.10608: ** top-level
#@+node:ekr.20170128183737.1: *3* controller
def controller(c):
    """Return the controller for c, creating it if necessary."""
    try:
        x = c.screenCastController
    except AttributeError:
        x = c.screenCastController = ScreenCastController(c)
    return x
#@+node:ekr.20120913110135.10603: *3* init
def init():
    """Return True if the plugin has loaded successfully."""
    ok = g.app.gui.guiName() == 'qt'
    if ok:
        g.registerHandler('after-create-leo-frame', onCreate)
        g.plugin_signon(__name__)
    return ok
#@+node:ekr.20120913110135.10604: *3* onCreate
def onCreate(tag, keys):
    """Inject c.screenshot_controller into the commander."""
    c = keys.get('c')
    if c:
        c.screencast_controller = ScreenCastController(c)
#@+node:ekr.20120922041923.10609: *3* @g.command('screencast-start')
@g.command('screencast-start')
def screencast_start(event=None, command_list=None):
    """Start a screencast (screencast.py)"""
    c = event.get('c')
    if c:
        m = c.screenCastController
        if m and command_list:
            m.start_commands(command_list)
        elif m:
            p = m.find_screencast(c.p)
            m.start(p)
        else:
            g.trace('no commands and no p.')
#@+node:ekr.20120913110135.10607: ** class ScreenCastController
class ScreenCastController:
    #@+others
    #@+node:ekr.20120913110135.10606: *3* sc.__init__ (ScreenCastController)
    def __init__(self, c):
        self.c = c
        self.commands = []
        self.command_index = 0
        self.log_color = 'black'
        self.log_focus = True  # True: writing to log sets focus to log.
        self.ignore_keys = False  # True: ignore keys in state_handler.
        self.quit_flag = False  # True if m.quit has been called.
        self.k_state = g.bunch(kind=None, n=None, handler=None)  # Saved k.state.
        self.key_w = None  # Saved widget for passed-along key handling.
        self.n1 = 0.02  # default minimal typing delay.
        self.n2 = 0.175  # default maximum typing delay.
        self.p1 = None  # The first slide of the show.
        self.p = None  # The present slide of the show.
        self.speed = 1.0  # Amount to multiply wait times.
        self.state_name = 'screencast'  # The state name to enable m.state_handler.
        self.node_stack = []  # For m.prev and m.undo.
        self.text_flag = False  # True: m.next shows body text instead of executing it.
        self.user_dict = {}  # For use by scripts.
        self.widgets = []  # List of (popup) widgets created by this class.
        # inject c.screenCastController
        c.screenCastController = self
    #@+node:ekr.20120916193057.10605: *3* sc.Entry points
    #@+node:ekr.20120913110135.10580: *4* sc.body_keys (screencast.py)
    def body_keys(self, s, n1=None, n2=None):
        """Simulate typing in the body pane.
        n1 and n2 indicate the range of delays between keystrokes.
        """
        c, m, p, u = self.c, self, self.c.p, self.c.undoer
        w = c.frame.body.wrapper.widget
        if n1 is None:
            n1 = 0.02
        if n2 is None:
            n2 = 0.095
        m.key_w = m.pane_widget('body')
        c.bodyWantsFocusNow()
        bunch = u.beforeChangeBody(p)
        p.b = p.b + s
        u.afterChangeBody(p, 'simulate-typing', bunch)
        for ch in s:
            p.b = p.b + ch
            w.repaint()
            m.wait(n1, n2)
        c.redraw()
    #@+node:ekr.20120914133947.10578: *4* sc.caption and abbreviations: body, log, tree
    def caption(self, s, pane):  # To do: center option.
        """Pop up a QPlainTextEdit in the indicated pane."""
        m = self
        parent = m.pane_widget(pane)
        if not parent:
            g.trace('bad pane: %s' % (pane))
            return None
        s = s.rstrip()
        if s and s[-1].isalpha():
            s = s + '.'
        w = QtWidgets.QPlainTextEdit(s, parent)
        w.setObjectName('screencastcaption')
        m.widgets.append(w)
        w2 = m.pane_widget(pane)
        geom = w2.geometry()
        w.resize(geom.width(), min(150, geom.height() / 2))
        w.setHorizontalScrollBarPolicy(ScrollBarPolicy.ScrollBarAlwaysOff)
        w.setVerticalScrollBarPolicy(ScrollBarPolicy.ScrollBarAlwaysOff)
        w.show()
        return w

    def body(self, s):
        return self.caption(s, 'body')

    def log(self, s):
        return self.caption(s, 'log')

    def tree(self, s):
        return self.caption(s, 'tree')
    #@+node:ekr.20120913110135.10612: *4* sc.clear_log
    def clear_log(self):
        """Clear the log."""
        m = self
        m.c.frame.log.clearTab('Log')
    #@+node:ekr.20120913110135.10581: *4* sc.command
    def command(self, command_name):
        """Execute the command whose name is given and update the screen immediately."""
        m = self
        c = m.c
        # Named commands handle their own undo!
        # The undo handling in m.next should suffice.
        c.doCommandByName(command_name)
        c.redraw()
        m.repaint('all')
    #@+node:ekr.20120922041923.10612: *4* sc.dismiss_menu_bar
    def dismiss_menu_bar(self):
        m = self
        c = m.c
        # c.frame.menu.deactivateMenuBar()
        g.trace()
        menubar = c.frame.top.leo_menubar
        menubar.setActiveAction(None)
        menubar.repaint()
    #@+node:ekr.20120915091327.13816: *4* sc.find_screencast & helpers
    def find_screencast(self, p):
        """Find the nearest screencast, prefering previous screencasts
        because that makes it easier to create screencasts."""
        m = self
        return m.find_prev_screencast(p) or m.find_next_screencast(p)
    #@+node:ekr.20120916193057.10608: *5* sc.find_next_screencast
    def find_next_screencast(self, p):
        # m = self
        p = p.copy()
        while p:
            if p.h.startswith('@screencast'):
                return p
            p.moveToThreadNext()
        return None
    #@+node:ekr.20120916193057.10609: *5* sc.find_prev_screencast
    def find_prev_screencast(self, p):
        # m = self
        p = p.copy()
        while p:
            if p.h.startswith('@screencast'):
                return p
            p.moveToThreadBack()
        return None
    #@+node:ekr.20120913110135.10582: *4* sc.focus
    def focus(self, pane):
        """Immediately set the focus to the given pane."""
        m = self
        c = m.c
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
    #@+node:ekr.20120913110135.10583: *4* sc.head_keys (screencast.py)
    def head_keys(self, s, n1=None, n2=None):
        """Simulate typing in the headline.
        n1 and n2 indicate the range of delays between keystrokes.
        """
        m = self
        c = m.c
        p = c.p
        undoType = 'Typing'
        tree = c.frame.tree
        if n1 is None:
            n1 = 0.02
        if n2 is None:
            n2 = 0.095
        p.h = ''
        c.editHeadline()
        w = tree.edit_widget(p)
        # Support undo.
        undoData = c.undoer.beforeChangeNodeContents(p)
        p.setDirty()
        c.undoer.afterChangeNodeContents(p, undoType, undoData)
        # Lock out key handling in m.state_handler.
        m.ignore_keys = True
        try:
            m.key_w = w
            for ch in s:
                p.h = p.h + ch
                tree.repaint()  # *not* tree.update.
                m.wait(n1, n2)
                event = m.get_key_event(ch, w)
                c.k.masterKeyHandler(event)
        finally:
            m.ignore_keys = False
        p.h = s
        c.redraw()
    #@+node:ekr.20120913110135.10615: *4* sc.image
    def image(self, pane, fn, center=None, height=None, width=None):
        """Put an image in the indicated pane."""
        m = self
        parent = m.pane_widget(pane)
        if not parent:
            g.trace('bad pane: %s' % (pane))
            return None
        w = QtWidgets.QLabel('label', parent)
        fn = m.resolve_icon_fn(fn)
        if not fn:
            return None
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
    #@+node:ekr.20120921064434.10605: *4* sc.open_menu
    def open_menu(self, menu_name):
        """Activate the indicated *top-level* menu."""
        m = self
        c = m.c
        # Menu is a qtMenuWrapper, a subclass of both QMenu and leoQtMenu.
        menu = c.frame.menu.getMenu(menu_name)
        if menu:
            c.frame.menu.activateMenu(menu_name)
            if 0:  # None of this works.
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
    #@+node:ekr.20120916062255.10590: *4* sc.plain_keys
    def plain_keys(self, s, n1=None, n2=None, pane='body'):
        """Simulate typing a string of plain keys."""
        m = self
        for ch in s:
            m.single_key(ch, n1=n1, n2=n2, pane=pane)
    #@+node:ekr.20120914074855.10722: *4* sc.quit
    def quit(self):
        """Terminate the slide show."""
        m = self
        c = m.c
        k = c.k
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
    #@+node:ekr.20120918103526.10594: *4* sc.redraw
    def redraw(self, p=None):
        m = self
        m.c.redraw(p)
    #@+node:ekr.20120913110135.10585: *4* sc.repaint
    def repaint(self, pane):
        """Repaint the given pane."""
        m = self
        w = m.pane_widget(pane)
        if w:
            w.repaint()
        else:
            g.trace('bad pane: %s' % (pane))
    #@+node:ekr.20120923063251.10652: *4* sc.select_position
    def select_position(self, p):
        m = self
        assert p
        m.redraw(p)
    #@+node:ekr.20120916062255.10593: *4* sc.single_key
    def single_key(self, ch, n1=None, n2=None, pane=None, w=None):
        """Simulate typing a single key, properly saving and restoring m.k_state."""
        m = self
        k = m.c.k
        w = w or m.pane_widget(pane or 'body')
        force = n1 is not None or n2 is not None
        if force and n1 is None:
            n1 = 0.02
        if force and n2 is None:
            n2 = 0.095
        try:
            if m.k_state.kind:
                # old_state_kind = m.k_state.kind
                k.setState(m.k_state.kind, m.k_state.n, m.k_state.handler)
            else:
                # old_state_kind = None
                k.clearState()
            w.repaint()  # *not* tree.update.
            m.wait(n1, n2)
            event = m.get_key_event(ch, w)
            k.masterKeyHandler(event)
        finally:
            # Save k.state in m.k_state.
            if k.state.kind != m.state_name:
                m.set_state(k.state)
            # Important: do *not* re-enable m.state_handler here.
            # This should be done *only* in m.next.
    #@+node:ekr.20120916193057.10607: *3* sc.State handling
    #@+node:ekr.20120914074855.10721: *4* sc.next & helper
    def next(self):
        """Find the next screencast node and execute its script.
        Call m.quit if no more nodes remain."""
        m = self
        c = m.c
        k = c.k
        m.delete_widgets()
        # Restore k.state from m.k_state.
        if m.k_state.kind and m.k_state.kind != m.state_name:
            k.setState(kind=m.k_state.kind, n=m.k_state.n, handler=m.k_state.handler)
        while m.p:
            h = m.p.h.replace('_', '').replace('-', '')
            if g.match_word(h, 0, '@ignorenode'):
                m.p.moveToThreadNext()
            elif g.match_word(h, 0, '@ignoretree') or g.match_word(h, 0, '@button'):
                m.p.moveToNodeAfterTree()
            elif m.p.b.strip():
                p_next = m.p.threadNext()
                p_old = m.p.copy()
                if g.match_word(m.p.h, 0, '@text'):
                    c.redraw(m.p)  # Selects the node, thereby showing the body text.
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
    #@+node:ekr.20120918103526.10596: *5* sc.exec_node
    def exec_node(self, p):
        """Execute the script in node p."""
        m = self
        c = m.c
        assert p
        assert p.b
        d = {'c': c, 'g:': g, 'm': m, 'p': p}
        tag = 'screencast'
        m.node_stack.append(p)
        try:
            undoData = c.undoer.beforeChangeGroup(c.p, tag, verboseUndoGroup=False)
            c.executeScript(p=p, namespace=d, useSelectedText=False, raiseFlag=False)
            c.undoer.afterChangeGroup(c.p, tag, undoData)
        except Exception:
            g.es_exception()
            m.quit()
    #@+node:ekr.20120917132841.10609: *4* sc.prev
    def prev(self):
        """Show the previous slide.  This will recreate the slide's widgets,
        but the user may have to adjust the minibuffer or other widgets by hand."""
        m = self
        if m.p and m.p == m.p1:
            g.trace('at start: %s' % (m.p and m.p.h))
            m.start(m.p1)
        else:
            p = m.undo()
            if p and p == m.p1:
                m.start(m.p1)
            elif p:
                m.undo()
                m.next()
            else:
                m.start(m.p1)
    #@+node:ekr.20120914074855.10720: *4* sc.start
    def start(self, p):
        """Start a screencast whose root node is p.

        Important: p is not necessarily c.p!
        """
        m = self
        c = m.c
        k = c.k
        assert p
        # Reset Leo's state.
        k.keyboardQuit()
        # Set ivars
        m.p1 = p.copy()
        m.p = p.copy()
        m.quit_flag = False
        m.clear_state()
        p.contract()
        c.redraw(p)
        # Clear widgets left over from previous, unfinished, slideshows.
        m.delete_widgets()
        m.state_handler()
    #@+node:ekr.20170128184559.1: *4* sc.start_commands (new)
    def start_commands(self, commands):
        """Start a screencast given by a list of commands.

        Important: p is not necessarily c.p!
        """
        k, m = self.c.k, self
        self.commands = commands
        self.command_index = 0
        # Reset Leo's state.
        k.keyboardQuit()
        # Set ivars
        # m.p1 = p.copy()
        # m.p = p.copy()
        m.quit_flag = False
        m.clear_state()
        # p.contract()
        # c.redraw(p)
        # Clear widgets left over from previous, unfinished, slideshows.
        m.delete_widgets()
        m.state_handler()
    #@+node:ekr.20120914074855.10715: *4* sc.state_handler
    def state_handler(self, event=None):
        """Handle keys while in the "screencast" input state."""
        m = self
        c = m.c
        k = c.k
        state = k.getState(m.state_name)
        char = event.char if event else ''
        if m.ignore_keys:
            return
        if state == 0:
            # Init the minibuffer as in k.fullCommand.
            assert m.p1 and m.p1 == m.p
            k.mb_event = event
            k.mb_prefix = k.getLabel()
            k.mb_prompt = 'Screencast: '
            k.mb_tabList = []
            k.setLabel(k.mb_prompt)
            k.setState(m.state_name, 1, m.state_handler)
            m.next()
        # Only exit on Ctrl-g.
        # Because of menu handling, it's convenient to have escape go to the next slide.
        # That way an "extra" escape while dismissing menus will be handled well.
        elif char == 'Escape':
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
            kind, n, handler = k.state.kind, k.state.n, k.state.handler
            m_state_copy = g.bunch(kind=m.k_state.kind,
                n=m.k_state.n, handler=m.k_state.handler)
            m.single_key(char)
            k.setState(kind, n, handler)
            m.set_state(m_state_copy)
    #@+node:ekr.20120914195404.11208: *4* sc.undo
    def undo(self):
        """Undo the previous screencast scene."""
        m = self
        m.delete_widgets()
        if not m.node_stack:
            return None
        c = m.c
        m.p = m.node_stack.pop()
        c.undoer.undo()
        c.redraw()
        return m.p
    #@+node:ekr.20120916062255.10596: *4* sc.set_state & clear_state
    def set_state(self, state):
        m = self
        m.k_state.kind = state.kind
        m.k_state.n = state.n
        m.k_state.handler = state.handler

    def clear_state(self):
        m = self
        m.k_state.kind = None
        m.k_state.n = None
        m.k_state.handler = None
    #@+node:ekr.20120916193057.10606: *3* sc.Utilities
    #@+node:ekr.20120916062255.10589: *4* sc.get_key_event
    def get_key_event(self, ch, w):
        m = self
        c = m.c
        k = c.k
        m.key_w = w
        if len(ch) > 1:
            key = None
            stroke = k.strokeFromSetting(ch).s
        else:
            stroke = key = ch
        return leoGui.LeoKeyEvent(c, key, stroke,
            binding=None,
            w=w,
            x=0, y=0,
            x_root=0, y_root=0)
    #@+node:ekr.20120914163440.10581: *4* sc.delete_widgets
    def delete_widgets(self):
        m = self
        for w in m.widgets:
            w.deleteLater()
        m.widgets = []
    #@+node:ekr.20120914133947.10579: *4* sc.pane_widget
    def pane_widget(self, pane):
        """Return the pane's widget."""
        m = self
        c = m.c
        d = {
            'all': c.frame.top,
            'body': c.frame.body.wrapper.widget,
            'log': c.frame.log.logCtrl.widget,
            'minibuffer': c.frame.miniBufferWidget.widget,
            'tree': c.frame.tree.treeWidget,
        }
        return d.get(pane)
    #@+node:ekr.20120914163440.10582: *4* sc.resolve_icon_fn
    def resolve_icon_fn(self, fn):
        """Resolve fn relative to the Icons directory."""
        # m = self
        dir_ = g.finalize_join(g.app.loadDir, '..', 'Icons')
        path = g.finalize_join(dir_, fn)
        if g.os_path_exists(path):
            return path
        g.trace('does not exist: %s' % (path))
        return None
    #@+node:ekr.20120913110135.10587: *4* sc.wait
    def wait(self, n1=1, n2=0):
        """Wait for an interval between n1 and n2."""
        m = self
        if n1 is None:
            n1 = 0
        if n2 is None:
            n2 = 0
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

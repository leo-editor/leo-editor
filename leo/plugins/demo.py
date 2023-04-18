#@+leo-ver=5-thin
#@+node:ekr.20170128213103.1: * @file ../plugins/demo.py
"""
A plugin that makes making Leo demos easy. See:
https://github.com/leo-editor/leo-editor/blob/master/leo/doc/demo.md
generated in LeoDocs.leo: demo.md

Written by Edward K. Ream, January 29-31, 2017.
Revised by EKR February 6-7, 2017.
"""
#@+<< demo.py imports >>
#@+node:ekr.20170128213103.3: **  << demo.py imports >>
import random
from typing import List
from leo.core import leoGlobals as g
from leo.plugins import qt_events
from leo.core.leoQt import QtCore, QtGui, QtWidgets
#
# Fail fast, right after all imports.
g.assertUi('qt')  # May raise g.UiTypeException, caught by the plugins manager.
#@-<< demo.py imports >>

# pylint: disable=no-member,not-callable
#@@language python
#@@tabwidth -4
#@+others
#@+node:ekr.20170207082108.1: **   top level
#@+node:ekr.20170129230307.1: *3* commands (demo.py)
# Note: importing this plugin creates the commands.

@g.command('demo-next')
def next_command(self, event=None, chain=False):
    """Run the next demo script."""
    if getattr(g.app, 'demo', None):
        g.app.demo.next()
    else:
        g.trace('no demo instance')

@g.command('demo-prev')
def prev_command(self, event=None, chain=False):
    """Run the next demo script."""
    if getattr(g.app, 'demo', None):
        g.app.demo.prev()
    else:
        g.trace('no demo instance')

@g.command('demo-end')
def demo_end(self, event=None, chain=False):
    """End the present demo."""
    if getattr(g.app, 'demo', None):
        g.app.demo.end()
    else:
        g.trace('no demo instance')
#@+node:ekr.20170128213103.5: *3* init
def init():
    """Return True if the plugin has loaded successfully."""
    ok = g.app.gui.guiName() == 'qt'
    if ok:
        # g.registerHandler('after-create-leo-frame', onCreate)
        g.plugin_signon(__name__)
    return ok
#@+node:ekr.20170128213103.8: ** class Demo
class Demo:
    #@+others
    #@+node:ekr.20170128213103.9: *3* demo.__init__ & init_*
    def __init__(self, c, trace=False):
        """Ctor for the Demo class."""
        self.c = c
        # pylint: disable=import-self
        from leo.plugins import demo as module
        # True: start calls next until finished.
        self.auto_run = False
        # True: Exceptions call self.end(). Good for debugging.
        self.end_on_exception = False
        # For converting arguments to demo.key...
        self.filter_ = qt_events.LeoQtEventFilter(c, w=None, tag='demo')
        # The original size of the top-level Leo window. Restored in demo.end()
        self.initial_geometry = None
        # Speed multiplier for simulated typing.
        self.key_speed = 1.0
        # The leo.plugins.demo module.
        self.module = module
        # Default minimal typing delay, in seconds.
        self.n1 = 0.02
        # Default maximum typing delay, in seconds.
        self.n2 = 0.175
        # The namespace for all demo script.
        # Set in init_namespace, which subclasses may override.
        self.namespace = {}
        # List of widgets *not* to be deleted by delete_widgets.
        self.retained_widgets = []
        # For find_node: The outline to be searched for nodes.
        self.root = None
        # The root of the script tree.
        self.script_root = None
        # Index into self.script_list.
        self.script_i = 0
        # A list of strings (scripts). Scripts are removed when executed.
        self.script_list = []
        self.speed: float = None
        self.user_dict = {}  # For use by scripts.
        self.widgets = []  # References to all widgets created by this class.
        # Init...
        self.init()
        self.init_namespace()
    #@+node:ekr.20170129174128.1: *4* demo.init
    def init(self):
        """Link the global commands to this class."""
        old_demo = getattr(g.app, 'demo', None)
        if old_demo:
            old_demo.delete_all_widgets()
        g.app.demo = self
    #@+node:ekr.20170208124125.1: *4* demo.init_namespace
    def init_namespace(self):
        """
        Init self.namespace. May be overridden.
        """
        c = self.c
        self.namespace = {
            'c': c,
            'demo': self,
            'g': g,
            'p': c.p,
            # Qt namespaces.
            'Qt': QtCore.Qt,  # Useful, and tricky to get right.
            'QtCore': QtCore,
            'QtGui': QtGui,
            'QtWidgets': QtWidgets,
            # Graphic classes.
            'Arrow': Arrow,
            'Callout': Callout,
            'Head': Head,
            'Image': Image,
            'Label': Label,
            'Text': Text,
            'Title': Title,
        }
        # Add most ivars.
        for key, value in self.namespace.items():
            if not hasattr(self, key) and key not in 'cgp':
                setattr(self, key, value)
    #@+node:ekr.20170128222411.1: *3* demo.Control
    #@+node:ekr.20170207090715.1: *4* demo.bind
    def bind(self, name, object_):
        """Add the name:object binding to self.namespace."""
        if name in self.namespace:
            g.trace('redefining', name)
            g.printDict(self.namespace)
        self.namespace[name] = object_
        return object_
    #@+node:ekr.20170129174251.1: *4* demo.end
    def end(self):
        """
        End this slideshow and call teardown().
        This will be called several times if demo scripts call demo.next().
        """
        if g.app.demo:
            try:
                if getattr(self, 'initial_geometry', None):
                    self.set_top_geometry(self.initial_geometry)
                self.script_list = []
                self.script_i = 0
                self.teardown()
            except Exception:
                g.es_exception()
            g.app.demo = None
            g.es_print('End demo')
    #@+node:ekr.20170128213103.31: *4* demo.exec_node
    def exec_node(self, script):
        """Execute the script in node p."""
        c = self.c
        try:
            c.executeScript(
                namespace=self.namespace,
                script=script,
                raiseFlag=False,
                useSelectedText=False,
            )
        except Exception:
            g.es_exception()
            g.es_print('script...')
            g.printList(g.splitLines(script))
            g.es_print('Ending the tutorial...')
            self.end()

    #@+node:ekr.20170128213103.30: *4* demo.next
    def next(self, chain=True, wait=None):
        """Execute the next demo script, or call end()."""
        if wait is not None:
            self.wait(wait)
        if self.script_i < len(self.script_list):
            # Execute the next script.
            script = self.script_list[self.script_i]
            self.script_i += 1
            self.setup_script()
            self.exec_node(script)
            self.teardown_script()
        if self.script_i >= len(self.script_list):
            self.end()

    next_command = next

    # def next_command(self):
        # self.chain_flag = False
        # self.next(chain=False)
    #@+node:ekr.20170209160057.1: *4* demo.prev
    def prev(self):
        """Execute the previous demo script, if any."""
        if self.script_i - 1 > 0:
            self.script_i -= 2
            script = self.script_list[self.script_i]
            self.setup_script()
            self.exec_node(script)
            self.script_i += 1  # Restore invariant, and make net change = -1.
            self.teardown_script()

    prev_command = prev
    #@+node:ekr.20170208094834.1: *4* demo.retain
    def retain(self, w):
        """Retain widet w so that dele_widgets does not delete it."""
        self.retained_widgets.append(w)
    #@+node:ekr.20170128214912.1: *4* demo.setup & teardown
    def setup(self, p=None):
        """
        Called before running the first demo script.
        p is the root of the tree of demo scripts.
        May be over-ridden in subclasses.
        """

    def setup_script(self):
        """
        Called before running each demo script.
        May be over-ridden in subclasses.
        """

    def teardown(self):
        """
        Called when the demo ends.
        Subclasses may override this.
        """
        self.delete_all_widgets()

    def teardown_script(self):
        """
        Called when the demo ends.
        Subclasses may override this.
        """
    #@+node:ekr.20170128213103.33: *4* demo.start & helpers
    def start(self, script_tree, auto_run=False, delim='###', root=None):
        """Start a demo. script_tree contains the demo scripts."""
        from leo.core import leoNodes
        p = script_tree
        self.root = root and root.copy()
        self.script_root = script_tree and script_tree.copy()
        self.delete_widgets()
        self.auto_run = auto_run
        self.initial_geometry = self.get_top_geometry()  # Setup may change this.
        if isinstance(p, leoNodes.Position):
            if p:
                self.script_list = self.create_script_list(p, delim)
                if self.script_list:
                    try:
                        self.setup(p)
                    except Exception:
                        g.es_exception()
                        self.end()
                    if auto_run:
                        while self.script_i < len(self.script_list):
                            # Helps, but widgets are not deleted.
                            g.app.gui.qtApp.processEvents()
                            self.next()
                    else:
                        self.next()
                else:
                    g.trace('empty script tree at', p.h)
            else:
                g.trace('invalid p')
        else:
            g.trace('script_tree must be a position', repr(p))
            self.end()
    #@+node:ekr.20170129180623.1: *5* demo.create_script_list
    def create_script_list(self, p, delim):
        """Create the state_list from the tree of script nodes rooted in p."""
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
        # Now split each element of the list.
        # This is a big advance in scripting!
        result = []
        for s in aList:
            result.extend(self.parse_script_string(s, delim))
        return result
    #@+node:ekr.20170207080029.1: *5* demo.parse_script_string
    def parse_script_string(self, script_string, delim):
        """
        script_string is single string, representing a list of script strings
        separated by lines that start with delim.

        Return a list of strings.
        """
        aList = []
        lines: List[str] = []
        for s in g.splitLines(script_string):
            if s.startswith(delim):
                if lines:
                    aList.append(''.join(lines))
                lines = []
            elif s.isspace() or s.strip().startswith('#'):
                # Ignore comment or blank lines.
                # This allows the user to comment out entire sections.
                pass
            else:
                lines.append(s)
                # lines.append(s.replace('\\', '\\\\'))
                    # Experimental: allow escapes.
        if lines:
            aList.append(''.join(lines))
        return aList
    #@+node:ekr.20170128213103.43: *4* demo.wait & key_wait
    def key_wait(self, speed: float=None, n1=None, n2=None):
        """Wait for an interval between n1 and n2, in seconds."""
        if n1 is None:
            n1 = self.n1
        if n2 is None:
            n2 = self.n2
        if n1 > 0 and n2 > 0:
            n = random.uniform(n1, n2)
        else:
            n = n1
        if n > 0:
            n = float(n) * float(speed if speed is not None else self.key_speed)
            g.sleep(n)

    def wait(self, seconds):
        """Refresh the tree and wait for the given number of seconds."""
        self.repaint()
        g.sleep(seconds)
    #@+node:ekr.20170211045801.1: *3* demo.Debug
    #@+node:ekr.20170128213103.13: *4* demo.clear_log
    def clear_log(self):
        """Clear the log."""
        self.c.frame.log.clearTab('Log')
    #@+node:ekr.20170211042757.1: *4* demo.print_script
    def print_script(self, script):
        """Pretty print the script for debugging."""
        # g.printList(g.splitLines(script))
        print('\n' + script.strip())
    #@+node:ekr.20170211045959.1: *3* demo.Delete
    #@+node:ekr.20170128213103.40: *4* demo.delete_*
    def delete_all_widgets(self):
        """Delete all widgets."""
        self.delete_retained_widgets()
        self.delete_widgets()

    def delete_widgets(self):
        """Delete all widgets in the widget_list, but not retained widgets."""
        for w in self.widgets:
            if w not in self.retained_widgets:
                w.hide()
                w.deleteLater()
        self.widgets = []

    def delete_one_widget(self, w):
        if w in self.widgets:
            self.widgets.remove(w)
        if w in self.retained_widgets:
            self.retained_widgets.remove(w)
        w.hide()
        w.deleteLater()

    def delete_retained_widgets(self):
        """Delete all previously retained widgets."""
        for w in self.retained_widgets:
            w.hide()
            w.deleteLater()
        self.retained_widgets = []
    #@+node:ekr.20170211071750.1: *3* demo.File names
    #@+node:ekr.20170208093727.1: *4* demo.get_icon_fn
    def get_icon_fn(self, fn):
        """Resolve fn relative to the Icons directory."""
        dir_ = g.finalize_join(g.app.loadDir, '..', 'Icons')
        path = g.finalize_join(dir_, fn)
        if g.os_path_exists(path):
            return path
        g.trace('does not exist: %s' % (path))
        return None
    #@+node:ekr.20170211045726.1: *3* demo.Keys
    #@+node:ekr.20170128213103.11: *4* demo.body_keys (demo.py)
    def body_keys(self, s, speed=None, undo=False):
        """Undoably simulate typing in the body pane."""
        c = self.c
        c.bodyWantsFocusNow()
        p = c.p
        w = c.frame.body.wrapper.widget
        if undo:
            bunch = c.undoer.beforeChangeBody(p)
            p.b = p.b + s
            c.undoer.afterChangeBody(p, 'simulate-keys', bunch)
        for ch in s:
            p.b = p.b + ch
            w.repaint()
            self.key_wait(speed=speed)
    #@+node:ekr.20170128213103.20: *4* demo.head_keys
    def head_keys(self, s, speed=None, undo=False):
        """Undoably simulates typing in the headline."""
        c, p = self.c, self.c.p
        undoType = 'Typing'
        tree = c.frame.tree
        p.h = ''
        c.editHeadline()
        w = tree.edit_widget(p)
        if undo:
            undoData = c.undoer.beforeChangeNodeContents(p)
            p.setDirty()
            c.undoer.afterChangeNodeContents(p, undoType, undoData)
        for ch in s:
            p.h = p.h + ch
            tree.repaint()  # *not* tree.update.
            self.key_wait(speed=speed)
            event = self.new_key_event(ch, w)
            c.k.masterKeyHandler(event)
        p.h = s
        c.redraw()
    #@+node:ekr.20170128213103.28: *4* demo.key
    def key(self, ch, speed=None):
        """Simulate typing a single key"""
        c, k = self.c, self.c.k
        w = g.app.gui.get_focus(c=c, raw=True)
        self.key_wait(speed=speed)
        event = self.new_key_event(ch, w)
        k.masterKeyHandler(event)
        w.repaint()  # Make the character visible immediately.
    #@+node:ekr.20170128213103.23: *4* demo.keys (demo.py)
    def keys(self, s, undo=False):
        """
        Simulate typing a string of *plain* keys.
        Use demo.key(ch) to type any other characters.
        """
        p, u = self.c.p, self.c.undoer
        if undo:
            bunch = u.beforeChangeBody(p)
            p.b = p.b + s
            u.afterChangeBody(p, 'Typing', bunch)
        for ch in s:
            self.key(ch)
    #@+node:ekr.20170128213103.39: *4* demo.new_key_event
    def new_key_event(self, shortcut, w):
        """Create a LeoKeyEvent for a *raw* shortcut."""
        # pylint: disable=literal-comparison
        # Using the *input* logic seems best.
        event = self.filter_.create_key_event(
            event=None,
            c=self.c,
            w=w,
            ch=shortcut if len(shortcut) == 1 else '',
            tkKey=None,
            shortcut=shortcut,
        )
        return event
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
        """Activate the indicated *top-level* menu."""
        c = self.c
        # Menu is a qtMenuWrapper, a subclass of both QMenu and leoQtMenu.
        menu = c.frame.menu.getMenu(menu_name)
        if menu:
            c.frame.menu.activateMenu(menu_name)
        return menu
    #@+node:ekr.20170211050031.1: *3* demo.Nodes
    #@+node:ekr.20170213020527.1: *4* demo.find_node
    def find_node(self, headline):
        """Return the node whose headline is given."""
        c = self.c
        if self.root:
            p = g.findNodeInTree(c, self.root, headline)
        else:
            p = g.findNodeAnywhere(c, headline)
        return p
    #@+node:ekr.20170211045602.1: *4* demo.insert_node
    def insert_node(self, headline, end=True, keys=False, speed: float=None):
        """Helper for inserting a node."""
        c = self.c
        p = c.insertHeadline()
        if keys:
            self.speed = self.speed if speed is None else speed
            self.head_keys(headline)
        else:
            p.h = headline
        if end:
            c.endEditing()
    #@+node:ekr.20170211045933.1: *3* demo.Text
    #@+node:ekr.20170130184230.1: *4* demo.set_text_delta
    def set_text_delta(self, delta, w=None):
        """
        Updates the style sheet for the given widget (default is the body pane).
        Delta should be an int.
        """
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
    #@+node:ekr.20170211045817.1: *3* demo.Windows & Geometry
    #@+node:ekr.20170213021048.1: *4* demo.headline_geomtry
    def headline_geometry(self, p):
        """Return the x, y, width, height coordinates of p, for use by demo.set_geometry."""
        tree = self.c.frame.tree
        item = tree.position2itemDict.get(p.key())
        if not item:
            return None
        treeWidget = tree.treeWidget
        w = treeWidget.itemWidget(item, 0)
        if w:
            geom = w.geometry()
        else:
            # Create a temp edit item
            treeWidget.editItem(item)
            w = treeWidget.itemWidget(item, 0)
            geom = w.geometry()
            # End the editing.
            treeWidget.closeEditor(w, QtWidgets.QAbstractItemDelegate.NoHint)
        return geom.x(), geom.y(), geom.width(), geom.height()
    #@+node:ekr.20170210232228.1: *4* demo.get/set_top_geometry/size
    def get_top_geometry(self):
        top = self.c.frame.top
        widget = getattr(top, 'leo_master', None) or top
        return widget.geometry()

    def set_top_geometry(self, geometry):
        top = self.c.frame.top
        widget = getattr(top, 'leo_master', None) or top
        if isinstance(geometry, QtCore.QRect):
            widget.setGeometry(geometry)
        else:
            x, y, w, h = geometry
            widget.setGeometry(QtCore.QRect(x, y, w, h))

    def set_top_size(self, height, width):
        top = self.c.frame.top
        widget = getattr(top, 'leo_master', None) or top
        r = self.get_top_geometry()
        r.setHeight(height)
        r.setWidth(width)
        widget.setGeometry(r)

    #@+node:ekr.20170128213103.41: *4* demo.pane_widget
    def pane_widget(self, pane):
        """Return the pane's widget, defaulting to the body pane."""
        m = self
        c = m.c
        d = {
            None: c.frame.body.widget,
            'all': c.frame.top,
            'body': c.frame.body.widget,
            'log': c.frame.log.logCtrl.widget,
            'minibuffer': c.frame.miniBufferWidget.widget,
            'tree': c.frame.tree.treeWidget,
        }
        return d.get(pane)
    #@+node:ekr.20170213090335.1: *4* demo.pane_geometry
    def pane_geometry(self, pane):
        w = self.pane_widget(pane)
        return w.geometry()
    #@+node:ekr.20170128213103.26: *4* demo.repaint_pane
    def repaint(self):
        """Repaint the tree widget."""
        self.c.frame.tree.treeWidget.viewport().repaint()

    def repaint_pane(self, pane):
        """Repaint the given pane."""
        w = self.pane_widget(pane)
        if w:
            w.viewport().repaint()
        else:
            g.trace('bad pane: %s' % (pane))
    #@+node:ekr.20170206112010.1: *4* demo.set_position & helpers
    def set_position(self, w, position):
        """Position w at the given position, or center it."""
        if not position or position == 'center':
            self.center(w)
            return
        try:
            x, y = position
        except Exception:
            g.es('position must be "center" or a 2-tuple', repr(position))
            return
        # Convert x and y as needed.
        if x is None:
            x = 'center'
        elif not isinstance(x, (int, float)):
            x = x.strip().lower()
        if y is None:
            y = 'center'
        elif not isinstance(y, (int, float)):
            y = y.strip().lower()
        # Handle x and y.
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
        """Center this widget in its parent."""
        g_p = w.parent().geometry()
        g_w = w.geometry()
        w.updateGeometry()
        x = g_p.width() / 2 - g_w.width() / 2
        y = g_p.height() / 2
        w.move(x, y)

    def center_horizontally(self, w, y):
        """Center w horizontally in its parent, and set its y position."""
        g_p = w.parent().geometry()
        g_w = w.geometry()
        w.updateGeometry()
        x = g_p.width() / 2 - g_w.width() / 2
        w.move(x, y)

    def center_vertically(self, w, x):
        """Center w vertically in its parent, setting its x position."""
        y = w.parent().geometry().height() / 2
        w.move(x, y)
    #@+node:ekr.20170206142602.1: *5* demo.set_x/y & helper
    def set_x(self, w, x):
        """Set our x coordinate to x."""
        x = self.get_int(x)
        if x is not None:
            w.move(x, w.geometry().y())

    def set_y(self, w, y):
        """Set our y coordinate to y."""
        y = self.get_int(y)
        if y is not None:
            w.move(w.geometry().x(), y)
    #@+node:ekr.20170207094113.1: *5* demo.get_int
    def get_int(self, obj):
        """Convert obj to an int, if needed."""
        if isinstance(obj, int):
            return obj
        try:
            return int(obj)
        except ValueError:
            g.es_exception()
            g.trace('bad x position', repr(obj))
            return None
    #@+node:ekr.20170213145241.1: *4* demo.get/set_ratios
    def get_ratios(self):
        """Return the two pane ratios."""
        f = self.c.frame
        return f.ratio, f.secondary_ratio

    def set_ratios(self, ratio1, ratio2):
        """Set the two pane ratios."""
        f = self.c.frame
        f.divideLeoSplitter1(ratio1)
        f.divideLeoSplitter2(ratio2)
    #@+node:ekr.20170209164344.1: *4* demo.set_window_size/position
    def set_window_size(self, width, height):
        """Resize Leo's top-most window."""
        w = self.c.frame.top
        while w.parent():
            w = w.parent()
        w.resize(width, height)

    def set_window_position(self, x, y):
        """Set the x, y position of the top-most window's top-left corner."""
        w = self.c.frame.top
        while w.parent():
            w = w.parent()
        w.move(x, y)

    def set_youtube_position(self):
        w = self.c.frame.top
        while w.parent():
            w = w.parent()
        w.resize(1264, 682)  # Important.
        w.move(200, 200)  # Arbitrary.
    #@-others
#@+node:ekr.20170208045907.1: ** Graphics classes & helpers
#@+node:ekr.20170206203005.1: *3*  class Label (QLabel)
class Label(QtWidgets.QLabel):  # type:ignore
    """A class for user-defined callouts in demo.py."""

    def __init__(self, text,
        font=None, pane=None, position=None, stylesheet=None
    ):
        """
        Label.__init__. The ctor for all user-defined callout classes.
        Show the callout in the indicated place.
        """
        demo, w = g.app.demo, self
        parent = demo.pane_widget(pane)
        super().__init__(text, parent)
        # w.setWordWrap(True)
        self.init(font, position, stylesheet)
        w.show()
        g.app.demo.widgets.append(w)

    #@+others
    #@+node:ekr.20170208210507.1: *4* label.init
    def init(self, font, position, stylesheet):
        """Set the attributes of the widget."""
        demo, w = g.app.demo, self
        stylesheet = stylesheet or """\
            QLabel {
                border: 2px solid black;
                background-color : lightgrey;
                color : black;
            }"""
        demo.set_position(w, position or 'center')
        w.setStyleSheet(stylesheet)
        w.setFont(font or QtGui.QFont('DejaVu Sans Mono', 16))
    #@-others
#@+node:ekr.20170213092704.1: *3* class Arrow(Label)
class Arrow(Label):

    def __init__(self, text,
        font=None, pane=None, position=None, stylesheet=None
    ):
        """Show a callout, centered by default."""
        demo, w = g.app.demo, self
        stylesheet = stylesheet or '''\
            QLabel {
                border: 0px solid black;
                background: transparent;
                color : black;
            }'''
        super().__init__(text, font=font, pane=pane,
                position=position, stylesheet=stylesheet)
        # Do this *after* initing the base class.
        demo.set_position(w, position or 'center')
#@+node:ekr.20170207071819.1: *3* class Callout(Label)
class Callout(Label):

    def __init__(self, text,
        font=None, pane=None, position=None, stylesheet=None
    ):
        """Show a callout, centered by default."""
        demo, w = g.app.demo, self
        stylesheet = stylesheet or '''\
            QLabel {
                border: 2px solid black;
                background-color : lightblue;
                color : black;
            }'''
        super().__init__(text,
            font=font,
            pane=pane,
            position=position,
            stylesheet=stylesheet)
        # Do this *after* initing the base class.
        demo.set_position(w, position or 'center')
#@+node:ekr.20170208065111.1: *3* class Image (QLabel)
class Image(QtWidgets.QLabel):  # type:ignore
    def __init__(self, fn,
        pane=None, magnification=None, position=None, size=None):
        """Image.__init__."""
        demo, w = g.app.demo, self
        parent = demo.pane_widget(pane)
        super().__init__(parent=parent)
        self.init_image(fn, magnification, position, size)
        w.show()
        demo.widgets.append(w)

    #@+others
    #@+node:ekr.20170208070231.1: *4* image.init_image
    def init_image(self, fn, magnification, position, size):
        """Init the image whose file name fn is given."""
        demo, widget = g.app.demo, self
        fn = demo.get_icon_fn(fn)
        if not fn:
            g.trace('can not resolve', fn)
            return
        pixmap = QtGui.QPixmap(fn)
        if not pixmap:
            g.trace('Not a pixmap:', fn)
            return
        if magnification:
            if size:
                h, w = size
            else:
                r = pixmap.size()
                h, w = r.height(), r.width()
            size = h * magnification, w * magnification
        if size:
            try:
                h, w = size
                h = demo.get_int(h)
                w = demo.get_int(w)
                if h is not None:
                    pixmap = pixmap.scaledToHeight(h)
                if w is not None:
                    pixmap = pixmap.scaledToWidth(w)
            except ValueError:
                g.trace('invalid size', repr(size))
        if position:
            demo.set_position(widget, position)
        widget.setPixmap(pixmap)
    #@-others
#@+node:ekr.20170208095240.1: *3* class Text (QPlainTextEdit)
class Text(QtWidgets.QPlainTextEdit):  # type:ignore

    def __init__(self, text,
        font=None, pane=None, position=None, size=None, stylesheet=None
    ):
        """Pop up a QPlainTextEdit in the indicated pane."""
        demo, w = g.app.demo, self
        parent = demo.pane_widget(pane)
        super().__init__(text.rstrip(), parent=parent)
        self.init(font, position, size, stylesheet)
        w.show()
        demo.widgets.append(self)

    #@+others
    #@+node:ekr.20170208101919.1: *4* text.init
    def init(self, font, position, size, stylesheet):
        """Init the Text widget."""
        demo, w = g.app.demo, self
        demo.set_position(w, position)
        if size:
            try:
                height, width = size
                height = demo.get_int(height)
                width = demo.get_int(width)
                w.resize(width, height)
            except ValueError:
                g.trace('invalid size', repr(size))
        else:
            geom = self._parent.geometry()
            w.resize(geom.width(), min(150, geom.height() / 2))
        if stylesheet:
            w.setStyleSheet(stylesheet)
        else:
            w.setFont(font or QtGui.QFont('Verdana', 14))
    #@-others
#@+node:ekr.20170207080814.1: *3* class Title(Label)
class Title(Label):

    def __init__(self, text,
        font=None, pane=None, position=None, stylesheet=None
    ):
        """Show a title, centered, at bottom by default."""
        demo, w = g.app.demo, self
        stylesheet = stylesheet or '''\
            QLabel {
                border: 1px solid black;
                background-color : mistyrose;
                color : black;
            }'''
        super().__init__(text, font=font, pane=pane,
                position=position, stylesheet=stylesheet)
        # Do this *after* initing the base class.
        demo.set_position(w, position or
            ('center', self.parent().geometry().height() - 50))
#@+node:ekr.20170213132024.1: *3* Head
#@@language python

def Head(arrow, label, headline, offset=None):
    """Add a callout to a headline."""
    demo = g.app.demo
    if demo:
        p = demo.find_node(headline)
        if p:
            x, y, w, h = demo.headline_geometry(p)
            class_ = Arrow if arrow else Callout
            if not offset:
                offset = w - 10
            class_(label, pane='tree', position=(x + offset, y))
        else:
            print('not found', p.h)
#@-others
#@-leo

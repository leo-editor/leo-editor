#@+leo-ver=5-thin
#@+node:ekr.20110605121601.17954: * @file ../plugins/nested_splitter.py
"""Nested splitter classes."""
from leo.core import leoGlobals as g
from leo.core.leoQt import isQt6, QtCore, QtGui, QtWidgets
from leo.core.leoQt import ContextMenuPolicy, Orientation, QAction
# pylint: disable=cell-var-from-loop
#@+others
#@+node:ekr.20110605121601.17956: ** init
def init():
    # Allow this to be imported as a plugin,
    # but it should never be necessary to do so.
    return True
#@+node:tbrown.20120418121002.25711: ** class NestedSplitterTopLevel (QWidget)
class NestedSplitterTopLevel(QtWidgets.QWidget):  # type:ignore
    """A QWidget to wrap a NestedSplitter to allow it to live in a top
    level window and handle close events properly.

    These windows are opened by the splitter handle context-menu item
    'Open Window'.

    The NestedSplitter itself can't be the top-level widget/window,
    because it assumes it can wrap itself in another NestedSplitter
    when the user wants to "Add Above/Below/Left/Right".  I.e. wrap
    a vertical nested splitter in a horizontal nested splitter, or
    visa versa.  Parent->SplitterOne becomes Parent->SplitterTwo->SplitterOne,
    where parent is either Leo's main window's QWidget 'centralwidget',
    or one of these NestedSplitterTopLevel "window frames".
    """
    #@+others
    #@+node:tbrown.20120418121002.25713: *3* __init__
    def __init__(self, *args, **kargs):
        """Init. taking note of the FreeLayoutController which owns this"""
        self.owner = kargs['owner']
        del kargs['owner']
        window_title = kargs.get('window_title')
        del kargs['window_title']
        super().__init__(*args, **kargs)
        if window_title:
            self.setWindowTitle(window_title)
    #@+node:tbrown.20120418121002.25714: *3* closeEvent (NestedSplitterTopLevel)
    def closeEvent(self, event):
        """A top-level NestedSplitter window has been closed, check all the
        panes for widgets which must be preserved, and move any found
        back into the main splitter."""
        widget = self.findChild(NestedSplitter)
        # top level NestedSplitter in window being closed
        other_top = self.owner.top()
        # top level NestedSplitter in main splitter
        # adapted from NestedSplitter.remove()
        count = widget.count()
        all_ok = True
        to_close = []
        # get list of widgets to close so index based access isn't
        # derailed by closing widgets in the same loop
        for splitter in widget.self_and_descendants():
            for i in range(splitter.count() - 1, -1, -1):
                to_close.append(splitter.widget(i))
        for w in to_close:
            all_ok &= (widget.close_or_keep(w, other_top=other_top) is not False)
        # it should always be ok to close the window, because it should always
        # be possible to move widgets which must be preserved back to the
        # main splitter, but if not, keep this window open
        if all_ok or count <= 0:
            self.owner.closing(self)
        else:
            event.ignore()
    #@-others
#@+node:ekr.20110605121601.17959: ** class NestedSplitterChoice (QWidget)
class NestedSplitterChoice(QtWidgets.QWidget):  # type:ignore
    """When a new pane is opened in a nested splitter layout, this widget
    presents a button, labeled 'Action', which provides a popup menu
    for the user to select what to do in the new pane"""
    #@+others
    #@+node:ekr.20110605121601.17960: *3* __init__ (NestedSplitterChoice)
    def __init__(self, parent=None):
        """ctor for NestedSplitterChoice class."""
        super().__init__(parent)
        self.setLayout(QtWidgets.QVBoxLayout())
        button = QtWidgets.QPushButton("Action", self)  # EKR: 2011/03/15
        self.layout().addWidget(button)
        button.setContextMenuPolicy(ContextMenuPolicy.CustomContextMenu)
        button.customContextMenuRequested.connect(
            lambda pnt: self.parent().choice_menu(self,
                button.mapToParent(pnt)))
        button.clicked.connect(lambda: self.parent().choice_menu(self, button.pos()))
    #@-others
#@+node:ekr.20110605121601.17961: ** class NestedSplitterHandle (QSplitterHandle)
class NestedSplitterHandle(QtWidgets.QSplitterHandle):  # type:ignore
    """Show the context menu on a NestedSplitter splitter-handle to access
    NestedSplitter's special features"""
    #@+others
    #@+node:ekr.20110605121601.17962: *3* nsh.__init__
    def __init__(self, owner):
        """Ctor for NestedSplitterHandle class."""
        super().__init__(owner.orientation(), owner)
        # Confusing!
            # self.setStyleSheet("background-color: green;")
        self.setContextMenuPolicy(ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.splitter_menu)
    #@+node:ekr.20110605121601.17963: *3* nsh.__repr__
    def __repr__(self):
        return f"(NestedSplitterHandle) at: {id(self)}"

    __str__ = __repr__
    #@+node:ekr.20110605121601.17964: *3* nsh.add_item
    def add_item(self, func, menu, name, tooltip=None):
        """helper for splitter_menu menu building"""
        act = QAction(name, self)
        act.setObjectName(name.lower().replace(' ', '-'))
        act.triggered.connect(lambda checked: func())
        if tooltip:
            act.setToolTip(tooltip)
        menu.addAction(act)
    #@+node:tbrown.20131130134908.27340: *3* nsh.show_tip
    def show_tip(self, action):
        """show_tip - show a tooltip, calculate the box in which
        the pointer must stay for the tip to remain visible

        :Parameters:
        - `self`: this handle
        - `action`: action triggering event to display
        """
        if action.toolTip() == action.text():
            tip = ""
        else:
            tip = action.toolTip()
        pos = QtGui.QCursor.pos()
        x = pos.x()
        y = pos.y()
        rect = QtCore.QRect(x - 5, y - 5, x + 5, y + 5)
        if hasattr(action, 'parentWidget'):  # 2021/07/17.
            parent = action.parentWidget()
        else:
            return
        if not parent:
            g.trace('===== no parent =====')
            return
        QtWidgets.QToolTip.showText(pos, tip, parent, rect)
    #@+node:ekr.20110605121601.17965: *3* nsh.splitter_menu
    def splitter_menu(self, pos):
        """build the context menu for NestedSplitter"""
        splitter = self.splitter()
        if not splitter.enabled:
            g.trace('splitter not enabled')
            return
        index = splitter.indexOf(self)
        # get three pairs
        widget, neighbour, count = splitter.handle_context(index)
        lr = 'Left', 'Right'
        ab = 'Above', 'Below'
        split_dir = 'Vertically'
        if self.orientation() == Orientation.Vertical:
            lr, ab = ab, lr
            split_dir = 'Horizontally'
        # blue/orange - color-blind friendly
        color = '#729fcf', '#f57900'
        sheet = []
        for i in 0, 1:
            sheet.append(widget[i].styleSheet())
            widget[i].setStyleSheet(sheet[-1] + f"\nborder: 2px solid {color[i]};")
        menu = QtWidgets.QMenu()
        menu.hovered.connect(self.show_tip)

        def pl(n):
            return 's' if n > 1 else ''

        def di(s):
            return {
                'Above': 'above',
                'Below': 'below',
                'Left': 'left of',
                'Right': 'right of',
            }[s]

        # Insert.

        def insert_callback(index=index):
            splitter.insert(index)

        self.add_item(insert_callback, menu, 'Insert',
            "Insert an empty pane here")
        # Remove, +0/-1 reversed, we need to test the one that remains
        # First see if a parent has more than two splits
        # (we could be a sole surviving child).
        max_parent_splits = 0
        up = splitter.parent()
        while isinstance(up, NestedSplitter):
            max_parent_splits = max(max_parent_splits, up.count())
            up = up.parent()
            if max_parent_splits >= 2:
                break  # two is enough
        for i in 0, 1:
            # keep = splitter.widget(index)
            # cull = splitter.widget(index - 1)
            if (max_parent_splits >= 2 or  # more splits upstream
                splitter.count() > 2 or  # 3+ splits here, or 2+ downstream
                neighbour[not i] and neighbour[not i].max_count() >= 2
            ):

                def remove_callback(i=i, index=index):
                    splitter.remove(index, i)

                self.add_item(remove_callback, menu,
                    f"Remove {count[i]:d} {lr[i]}",
                    f"Remove the {count[i]} pane{pl(count[i])} {di(lr[i])} here")
        # Swap.

        def swap_callback(index=index):
            splitter.swap(index)

        self.add_item(swap_callback, menu,
            f"Swap {count[0]:d} {lr[0]} {count[1]:d} {lr[1]}",
            f"Swap the {count[0]:d} pane{pl(count[0])} {di(lr[0])} here "
            f"with the {count[1]:d} pane{pl(count[1])} {di(lr[1])} here"
            )
        # Split: only if not already split.
        for i in 0, 1:
            if not neighbour[i] or neighbour[i].count() == 1:

                def split_callback(i=i, index=index, splitter=splitter):
                    splitter.split(index, i)

                self.add_item(
                    split_callback, menu, f"Split {lr[i]} {split_dir}")
        for i in 0, 1:

            def mark_callback(i=i, index=index):
                splitter.mark(index, i)

            self.add_item(mark_callback, menu, f"Mark {count[i]:d} {lr[i]}")
        # Swap With Marked.
        if splitter.root.marked:
            for i in 0, 1:
                if not splitter.invalid_swap(widget[i], splitter.root.marked[2]):

                    def swap_mark_callback(i=i, index=index, splitter=splitter):
                        splitter.swap_with_marked(index, i)

                    self.add_item(swap_mark_callback, menu,
                        f"Swap {count[i]:d} {lr[i]} With Marked")
        # Add.
        for i in 0, 1:
            if (
                not isinstance(splitter.parent(), NestedSplitter) or
                splitter.parent().indexOf(splitter) ==
                    [0, splitter.parent().count() - 1][i]
            ):

                def add_callback(i=i, splitter=splitter):
                    splitter.add(i)

                self.add_item(add_callback, menu, f"Add {ab[i]}")
        # Rotate All.
        self.add_item(splitter.rotate, menu, 'Toggle split direction')

        def rotate_only_this(index=index):
            splitter.rotateOne(index)

        self.add_item(rotate_only_this, menu, 'Toggle split/dir. just this')
        # equalize panes

        def eq(splitter=splitter.top()):
            splitter.equalize_sizes(recurse=True)

        self.add_item(eq, menu, 'Equalize all')
        # (un)zoom pane

        def zoom(splitter=splitter.top()):
            splitter.zoom_toggle()

        self.add_item(
            zoom,
            menu,
            ('Un' if splitter.root.zoomed else '') + 'Zoom pane'
        )
        # open window
        if splitter.top().parent().__class__ != NestedSplitterTopLevel:
            # don't open windows from windows, only from main splitter
            # so owner is not a window which might close.  Could instead
            # set owner to main splitter explicitly.  Not sure how right now.
            submenu = menu.addMenu('Open window')
            if 1:
                # pylint: disable=unnecessary-lambda
                self.add_item(lambda: splitter.open_window(), submenu, "Empty")
            # adapted from choice_menu()
            if (splitter.root.marked and
                splitter.top().max_count() > 1
            ):
                self.add_item(
                    lambda: splitter.open_window(action="_move_marked_there"),
                    submenu, "Move marked there")
            for provider in splitter.root.providers:
                if hasattr(provider, 'ns_provides'):
                    for title, id_ in provider.ns_provides():

                        def cb(id_=id_):
                            splitter.open_window(action=id_)

                        self.add_item(cb, submenu, title)
        submenu = menu.addMenu('Debug')
        act = QAction("Print splitter layout", self)

        def print_layout_c(checked, splitter=splitter):
            layout = splitter.top().get_layout()
            g.printObj(layout)

        act.triggered.connect(print_layout_c)
        submenu.addAction(act)

        def load_items(menu, items):
            for i in items:
                if isinstance(i, dict):
                    for k in i:
                        load_items(menu.addMenu(k), i[k])
                else:
                    title, id_ = i

                    def cb(checked, id_=id_):
                        splitter.context_cb(id_, index)

                    act = QAction(title, self)
                    act.triggered.connect(cb)
                    menu.addAction(act)

        for provider in splitter.root.providers:
            if hasattr(provider, 'ns_context'):
                load_items(menu, provider.ns_context())

        # point = pos.toPoint() if isQt6 else pos   # Qt6 documentation is wrong.
        point = pos
        global_point = self.mapToGlobal(point)
        menu.exec_(global_point)

        for i in 0, 1:
            widget[i].setStyleSheet(sheet[i])
    #@+node:tbnorth.20160510091151.1: *3* nsh.mouseEvents
    def mousePressEvent(self, event):
        """mouse event - mouse pressed on splitter handle,
        pass info. up to splitter

        :param QMouseEvent event: mouse event
        """
        super().mousePressEvent(event)
        self.splitter()._splitter_clicked(self, event, release=False, double=False)

    def mouseReleaseEvent(self, event):
        """mouse event - mouse pressed on splitter handle,
        pass info. up to splitter

        :param QMouseEvent event: mouse event
        """
        super().mouseReleaseEvent(event)
        self.splitter()._splitter_clicked(self, event, release=True, double=False)

    def mouseDoubleClickEvent(self, event):
        """mouse event - mouse pressed on splitter handle,
        pass info. up to splitter

        :param QMouseEvent event: mouse event
        """
        super().mouseDoubleClickEvent(event)
        self.splitter()._splitter_clicked(self, event, release=True, double=True)
    #@-others
#@+node:ekr.20110605121601.17966: ** class NestedSplitter (QSplitter)
class NestedSplitter(QtWidgets.QSplitter):  # type:ignore
    # Allow special behavior to be turned of at import stage.
    # useful if other code must run to set up callbacks, that other code can re-enable.
    enabled = True
    other_orientation = {
        Orientation.Vertical: Orientation.Horizontal,
        Orientation.Horizontal: Orientation.Vertical,
    }
    # a regular signal, but you can't use its .connect() directly,
    # use splitterClicked_connect()
    _splitterClickedSignal = QtCore.pyqtSignal(
        QtWidgets.QSplitter,
        QtWidgets.QSplitterHandle,
        QtGui.QMouseEvent,
        bool,
        bool
    )
    #@+others
    #@+node:ekr.20110605121601.17967: *3* ns.__init__
    def __init__(self, parent=None, orientation=None, root=None):
        """Ctor for NestedSplitter class."""
        if orientation is None:
            orientation = Orientation.Horizontal
        # This creates a NestedSplitterHandle.
        super().__init__(orientation, parent)
        if root is None:
            root = self.top(local=True)
            if root == self:
                root.marked = None  # Tuple: self,index,side-1,widget
                root.providers = []
                root.holders = {}
                root.windows = []
                root._main = self.parent()  # holder of the main splitter
                # list of top level NestedSplitter windows opened from 'Open Window'
                # splitter handle context menu
                root.zoomed = False
            #
            # NestedSplitter is a kind of meta-widget, in that it manages
            # panes across multiple actual splitters, even windows.
            # So to create a signal for a click on splitter handle, we
            # need to propagate the .connect() call across all the
            # actual splitters, current and future
            root._splitterClickedArgs = []  # save for future added splitters
        for args in root._splitterClickedArgs:
            # apply any .connect() calls that occurred earlier
            self._splitterClickedSignal.connect(*args)

        self.root = root
    #@+node:ekr.20110605121601.17968: *3* ns.__repr__
    def __repr__(self):
        # parent = self.parent()
        # name = parent and parent.objectName() or '<no parent>'
        name = self.objectName() or '<no name>'
        return f"(NestedSplitter) {name} at {id(self)}"

    __str__ = __repr__
    #@+node:ekr.20110605121601.17969: *3* ns.overrides of QSplitter methods
    #@+node:ekr.20110605121601.17970: *4* ns.createHandle
    def createHandle(self, *args, **kargs):
        return NestedSplitterHandle(self)
    #@+node:tbrown.20110729101912.30820: *4* ns.childEvent
    def childEvent(self, event):
        """If a panel client is closed not by us, there may be zero
        splitter handles left, so add an Action button

        unless it was the last panel in a separate window, in which
        case close the window"""
        QtWidgets.QSplitter.childEvent(self, event)
        if not event.removed():
            return
        local_top = self.top(local=True)
        # if only non-placeholder pane in a top level window deletes
        # itself, delete the window
        if (isinstance(local_top.parent(), NestedSplitterTopLevel) and
            local_top.count() == 1 and  # one left, could be placeholder
            isinstance(local_top.widget(0), NestedSplitterChoice)  # is placeholder
           ):
            local_top.parent().deleteLater()
            return
        # don't leave a one widget splitter
        if self.count() == 1 and local_top != self:
            self.parent().addWidget(self.widget(0))
            self.deleteLater()
        parent = self.parentWidget()
        if parent:
            layout = parent.layout()  # QLayout, not a NestedSplitter
        else:
            layout = None
        if self.count() == 1 and self.top(local=True) == self:
            if self.max_count() <= 1 or not layout:
                # maintain at least two items
                self.insert(0)
                # shrink the added button
                self.setSizes([0] + self.sizes()[1:])
            else:
                # replace ourselves in out parent's layout with our child
                pos = layout.indexOf(self)
                child = self.widget(0)
                layout.insertWidget(pos, child)
                pos = layout.indexOf(self)
                layout.takeAt(pos)
                self.setParent(None)
    #@+node:ekr.20110605121601.17971: *3* ns.add
    def add(self, side, w=None):
        """wrap a horizontal splitter in a vertical splitter, or
        visa versa"""
        orientation = self.other_orientation[self.orientation()]
        layout = self.parent().layout()
        if isinstance(self.parent(), NestedSplitter):
            # don't add new splitter if not needed, i.e. we're the
            # only child of a previously more populated splitter
            if w is None:
                w = NestedSplitterChoice(self.parent())
            self.parent().insertWidget(self.parent().indexOf(self) + side, w)
            # in this case, where the parent is a one child, no handle splitter,
            # the (prior to this invisible) orientation may be wrong
            # can't reproduce this now, but this guard is harmless
            self.parent().setOrientation(orientation)
        elif layout:
            new = NestedSplitter(None, orientation=orientation, root=self.root)
            # parent set by layout.insertWidget() below
            old = self
            pos = layout.indexOf(old)
            new.addWidget(old)
            if w is None:
                w = NestedSplitterChoice(new)
            new.insertWidget(side, w)
            layout.insertWidget(pos, new)
        else:
            # fail - parent is not NestedSplitter and has no layout
            pass
    #@+node:tbrown.20110621120042.22675: *3* ns.add_adjacent
    def add_adjacent(self, what, widget_id, side='right-of'):
        """add a widget relative to another already present widget"""
        horizontal, vertical = Orientation.Horizontal, Orientation.Vertical
        layout = self.top().get_layout()

        def hunter(layout, id_):
            """Recursively look for this widget"""
            for n, i in enumerate(layout['content']):
                if (i == id_ or
                        (isinstance(i, QtWidgets.QWidget) and
                        (i.objectName() == id_ or i.__class__.__name__ == id_)
                    )
                ):
                    return layout, n
                if not isinstance(i, QtWidgets.QWidget):
                    # then it must be a layout dict
                    x = hunter(i, id_)
                    if x:
                        return x
            return None

        # find the layout containing widget_id

        l = hunter(layout, widget_id)
        if l is None:
            return False
        # pylint: disable=unpacking-non-sequence
        layout, pos = l
        orient = layout['orientation']
        if (orient == horizontal and side in ('right-of', 'left-of') or
            orient == vertical and side in ('above', 'below')
        ):
            # easy case, just insert the new thing, what,
            # either side of old, in existing splitter
            if side in ('right-of', 'below'):
                pos += 1
            layout['splitter'].insert(pos, what)
        else:
            # hard case, need to replace old with a new splitter
            if side in ('right-of', 'left-of'):
                ns = NestedSplitter(orientation=horizontal, root=self.root)
            else:
                ns = NestedSplitter(orientation=vertical, root=self.root)
            old = layout['content'][pos]
            if not isinstance(old, QtWidgets.QWidget):  # see get_layout()
                old = layout['splitter']
            # put new thing, what, in new splitter, no impact on anything else
            ns.insert(0, what)
            # then swap the new splitter with the old content
            layout['splitter'].replace_widget_at_index(pos, ns)
            # now put the old content in the new splitter,
            # doing this sooner would mess up the index (pos)
            ns.insert(0 if side in ('right-of', 'below') else 1, old)
        return True
    #@+node:ekr.20110605121601.17972: *3* ns.choice_menu
    def choice_menu(self, button, pos):
        """build menu on Action button"""
        menu = QtWidgets.QMenu(self.top())  # #1995
        index = self.indexOf(button)
        if (self.root.marked and
            not self.invalid_swap(button, self.root.marked[3]) and
            self.top().max_count() > 2
        ):
            act = QAction("Move marked here", self)
            act.triggered.connect(
                lambda checked: self.replace_widget(button, self.root.marked[3]))
            menu.addAction(act)
        for provider in self.root.providers:
            if hasattr(provider, 'ns_provides'):
                for title, id_ in provider.ns_provides():

                    def cb(checked, id_=id_):
                        self.place_provided(id_, index)

                    act = QAction(title, self)
                    act.triggered.connect(cb)
                    menu.addAction(act)
        if menu.isEmpty():
            act = QAction("Nothing marked, and no options", self)
            menu.addAction(act)

        point = button.pos()
        global_point = button.mapToGlobal(point)
        menu.exec_(global_point)
    #@+node:tbrown.20120418121002.25712: *3* ns.closing
    def closing(self, window):
        """forget a top-level additional layout which was closed"""
        self.windows.remove(window)
    #@+node:tbrown.20110628083641.11723: *3* ns.place_provided
    def place_provided(self, id_, index):
        """replace Action button with provided widget"""
        provided = self.get_provided(id_)
        if provided is None:
            return
        self.replace_widget_at_index(index, provided)
        self.top().prune_empty()
        # user can set up one widget pane plus one Action pane, then move the
        # widget into the action pane, level 1 pane and no handles
        if self.top().max_count() < 2:
            print('Adding Action widget to maintain at least one handle')
            self.top().insert(0, NestedSplitterChoice(self.top()))
    #@+node:tbrown.20110628083641.11729: *3* ns.context_cb
    def context_cb(self, id_, index):
        """find a provider to provide a context menu service, and do it"""
        for provider in self.root.providers:
            if hasattr(provider, 'ns_do_context'):
                provided = provider.ns_do_context(id_, self, index)
                if provided:
                    break
    #@+node:ekr.20110605121601.17973: *3* ns.contains
    def contains(self, widget):
        """check if widget is a descendant of self"""
        for i in range(self.count()):
            if widget == self.widget(i):
                return True
            if isinstance(self.widget(i), NestedSplitter):
                if self.widget(i).contains(widget):
                    return True
        return False
    #@+node:tbrown.20120418121002.25439: *3* ns.find_child
    def find_child(self, child_class, child_name=None):
        """Like QObject.findChild, except search self.top()
        *AND* each window in self.root.windows
        """
        child = self.top().findChild(child_class, child_name)
        if not child:
            for window in self.root.windows:
                child = window.findChild(child_class, child_name)
                if child:
                    break
        return child
    #@+node:ekr.20110605121601.17974: *3* ns.handle_context
    def handle_context(self, index):
        """for a handle, return (widget, neighbour, count)

        This is the handle's context in the NestedSplitter, not the
        handle's context menu.

        widget
          the pair of widgets either side of the handle
        neighbour
          the pair of NestedSplitters either side of the handle, or None
          if the neighbours are not NestedSplitters, i.e.
          [ns0, ns1] or [None, ns1] or [ns0, None] or [None, None]
        count
          the pair of nested counts of widgets / splitters around the handle
        """
        widget = [self.widget(index - 1), self.widget(index)]
        neighbour = [(i if isinstance(i, NestedSplitter) else None) for i in widget]
        count = []
        for i in 0, 1:
            if neighbour[i]:
                l = [ii.count() for ii in neighbour[i].self_and_descendants()]
                n = sum(l) - len(l) + 1  # count leaves, not splitters
                count.append(n)
            else:
                count.append(1)
        return widget, neighbour, count
    #@+node:tbrown.20110621120042.22920: *3* ns.equalize_sizes
    def equalize_sizes(self, recurse=False):
        """make all pane sizes equal"""
        if not self.count():
            return
        for i in range(self.count()):
            self.widget(i).setHidden(False)
        size = sum(self.sizes()) / self.count()
        self.setSizes([int(size)] * self.count())  # #2281
        if recurse:
            for i in range(self.count()):
                if isinstance(self.widget(i), NestedSplitter):
                    self.widget(i).equalize_sizes(recurse=True)
    #@+node:ekr.20110605121601.17975: *3* ns.insert (NestedSplitter)
    def insert(self, index, w=None):
        """insert a pane with a widget or, when w==None, Action button"""
        if w is None:  # do NOT use 'not w', fails in PyQt 4.8
            w = NestedSplitterChoice(self)
            # A QWidget, with self as parent.
            # This creates the menu.
        self.insertWidget(index, w)
        self.equalize_sizes()
        return w
    #@+node:ekr.20110605121601.17976: *3* ns.invalid_swap
    def invalid_swap(self, w0, w1):
        """check for swap violating hierarchy"""
        return (
            w0 == w1 or
            isinstance(w0, NestedSplitter) and w0.contains(w1) or
            isinstance(w1, NestedSplitter) and w1.contains(w0))
    #@+node:ekr.20110605121601.17977: *3* ns.mark
    def mark(self, index, side):
        """mark a widget for later swapping"""
        self.root.marked = (self, index, side - 1, self.widget(index + side - 1))
    #@+node:ekr.20110605121601.17978: *3* ns.max_count
    def max_count(self):
        """find max widgets in this and child splitters"""
        counts = []
        count = 0
        for i in range(self.count()):
            count += 1
            if isinstance(self.widget(i), NestedSplitter):
                counts.append(self.widget(i).max_count())
        counts.append(count)
        return max(counts)
    #@+node:tbrown.20120418121002.25438: *3* ns.open_window
    def open_window(self, action=None):
        """open a top-level window, a TopLevelFreeLayout instance, to hold a
        free-layout in addition to the one in the outline's main window"""
        ns = NestedSplitter(root=self.root)
        window = NestedSplitterTopLevel(
            owner=self.root, window_title=ns.get_title(action))
        hbox = QtWidgets.QHBoxLayout()
        window.setLayout(hbox)
        hbox.setContentsMargins(0, 0, 0, 0)
        window.resize(400, 300)
        hbox.addWidget(ns)
        # NestedSplitters must have two widgets so the handle carrying
        # the all important context menu exists
        ns.addWidget(NestedSplitterChoice(ns))
        button = NestedSplitterChoice(ns)
        ns.addWidget(button)
        if action == '_move_marked_there':
            ns.replace_widget(button, ns.root.marked[3])
        elif action is not None:
            ns.place_provided(action, 1)
        ns.setSizes([0, 1])  # but hide one initially
        self.root.windows.append(window)
        # copy the main main window's stylesheet to new window
        w = self.root  # this is a Qt Widget, class NestedSplitter
        sheets = []
        while w:
            s = w.styleSheet()
            if s:
                sheets.append(str(s))
            w = w.parent()
        sheets.reverse()
        ns.setStyleSheet('\n'.join(sheets))
        window.show()
    #@+node:tbrown.20110627201141.11744: *3* ns.register_provider
    def register_provider(self, provider):
        """Register something which provides some of the ns_* methods.

        NestedSplitter tests for the presence of the following methods on
        the registered things, and calls them when needed if they exist.

        ns_provides()
          should return a list of ('Item name', '__item_id') strings,
          'Item name' is displayed in the Action button menu, and
          '__item_id' is used in ns_provide().
        ns_provide(id_)
          should return the widget to replace the Action button based on
          id_, or None if the called thing is not the provider for this id_
        ns_context()
          should return a list of ('Item name', '__item_id') strings,
          'Item name' is displayed in the splitter handle context-menu, and
          '__item_id' is used in ns_do_context().  May also return a dict,
          in which case each key is used as a sub-menu title, whose menu
          items are the corresponding dict value, a list of tuples as above.
          dicts and tuples may be interspersed in lists.
        ns_do_context()
          should do something based on id_ and return True, or return False
          if the called thing is not the provider for this id_
        ns_provider_id()
          return a string identifying the provider (at class or instance level),
          any providers with the same id will be removed before a new one is
          added
        """
        # drop any providers with the same id
        if hasattr(provider, 'ns_provider_id'):
            id_ = provider.ns_provider_id()
            cull = []
            for i in self.root.providers:
                if (hasattr(i, 'ns_provider_id') and
                    i.ns_provider_id() == id_
                ):
                    cull.append(i)
            for i in cull:
                self.root.providers.remove(i)
        self.root.providers.append(provider)
    #@+node:ekr.20110605121601.17980: *3* ns.remove & helper
    def remove(self, index, side):
        widget = self.widget(index + side - 1)
        # clear marked if it's going to be deleted
        if (self.root.marked and (self.root.marked[3] == widget or
            isinstance(self.root.marked[3], NestedSplitter) and
            self.root.marked[3].contains(widget))
        ):
            self.root.marked = None
        # send close signal to all children
        if isinstance(widget, NestedSplitter):
            count = widget.count()
            all_ok = True
            for splitter in widget.self_and_descendants():
                for i in range(splitter.count() - 1, -1, -1):
                    all_ok &= (self.close_or_keep(splitter.widget(i)) is not False)
            if all_ok or count <= 0:
                widget.setParent(None)
        else:
            self.close_or_keep(widget)
    #@+node:ekr.20110605121601.17981: *4* ns.close_or_keep
    def close_or_keep(self, widget, other_top=None):
        """when called from a closing secondary window, self.top() would
        be the top splitter in the closing window, and we need the client
        to specify the top of the primary window for us, in other_top"""
        if widget is None:
            return True
        for k in self.root.holders:
            if hasattr(widget, k):
                holder = self.root.holders[k]
                if holder == 'TOP':
                    holder = other_top or self.top()
                if hasattr(holder, "addTab"):
                    holder.addTab(widget, getattr(widget, k))
                else:
                    holder.addWidget(widget)
                return True
        if widget.close():
            widget.setParent(None)
            return True
        return False
    #@+node:ekr.20110605121601.17982: *3* ns.replace_widget & replace_widget_at_index
    def replace_widget(self, old, new):
        "Swap the provided widgets in place" ""
        sizes = self.sizes()
        new.setParent(None)
        self.insertWidget(self.indexOf(old), new)
        self.close_or_keep(old)
        new.show()
        self.setSizes(sizes)

    def replace_widget_at_index(self, index, new):
        """Replace the widget at index with w."""
        sizes = self.sizes()
        old = self.widget(index)
        if old != new:
            new.setParent(None)
            self.insertWidget(index, new)
            self.close_or_keep(old)
            new.show()
            self.setSizes(sizes)
    #@+node:ekr.20110605121601.17983: *3* ns.rotate
    def rotate(self, descending=False):
        """Change orientation - current rotates entire hierarchy, doing less
        is visually confusing because you end up with nested splitters with
        the same orientation - avoiding that would mean doing rotation by
        inserting out widgets into our ancestors, etc.
        """
        for i in self.top().self_and_descendants():
            if i.orientation() == Orientation.Vertical:
                i.setOrientation(Orientation.Horizontal)
            else:
                i.setOrientation(Orientation.Vertical)
    #@+node:vitalije.20170713085342.1: *3* ns.rotateOne
    def rotateOne(self, index):
        """Change orientation - only of splitter handle at index."""
        psp = self.parent()
        if self.count() == 2 and isinstance(psp, NestedSplitter):
            i = psp.indexOf(self)
            sizes = psp.sizes()
            [a, b] = self.sizes()
            s = sizes[i]
            s1 = a * s / (a + b)
            s2 = b * s / (a + b)
            sizes[i : i + 1] = [s1, s2]
            prev = self.widget(0)
            next = self.widget(1)
            psp.insertWidget(i, prev)
            psp.insertWidget(i + 1, next)
            psp.setSizes(sizes)
            assert psp.widget(i + 2) is self
            psp.remove(i + 3, 0)
            psp.setSizes(sizes)
        elif self is self.root and self.count() == 2:
            self.rotate()
        elif self.count() == 2:
            self.setOrientation(self.other_orientation[self.orientation()])
        else:
            orientation = self.other_orientation[self.orientation()]
            prev = self.widget(index - 1)
            next = self.widget(index)
            if None in (prev, next):
                return
            sizes = self.sizes()
            s1, s2 = sizes[index - 1 : index + 1]
            sizes[index - 1 : index + 1] = [s1 + s2]
            newsp = NestedSplitter(self, orientation=orientation, root=self.root)
            newsp.addWidget(prev)
            newsp.addWidget(next)
            self.insertWidget(index - 1, newsp)
            prev.setHidden(False)
            next.setHidden(False)
            newsp.setSizes([s1, s2])
            self.setSizes(sizes)
    #@+node:ekr.20110605121601.17984: *3* ns.self_and_descendants
    def self_and_descendants(self):
        """Yield self and all **NestedSplitter** descendants"""
        for i in range(self.count()):
            if isinstance(self.widget(i), NestedSplitter):
                for w in self.widget(i).self_and_descendants():
                    yield w
        yield self
    #@+node:ekr.20110605121601.17985: *3* ns.split (NestedSplitter)
    def split(self, index, side, w=None, name=None):
        """replace the adjacent widget with a NestedSplitter containing
        the widget and an Action button"""
        sizes = self.sizes()
        old = self.widget(index + side - 1)
        if w is None:
            w = NestedSplitterChoice(self)
        if isinstance(old, NestedSplitter):
            old.addWidget(w)
            old.equalize_sizes()
        else:
            orientation = self.other_orientation[self.orientation()]
            new = NestedSplitter(self, orientation=orientation, root=self.root)
            self.insertWidget(index + side - 1, new)
            new.addWidget(old)
            new.addWidget(w)
            new.equalize_sizes()
        self.setSizes(sizes)
    #@+node:ekr.20110605121601.17986: *3* ns.swap
    def swap(self, index):
        """swap widgets either side of a handle"""
        self.insertWidget(index - 1, self.widget(index))
    #@+node:ekr.20110605121601.17987: *3* ns.swap_with_marked
    def swap_with_marked(self, index, side):
        osplitter, oidx, oside, ow = self.root.marked
        idx = index + side - 1
        # convert from handle index to widget index
        # 1 already subtracted from oside in mark()
        w = self.widget(idx)
        if self.invalid_swap(w, ow):
            return
        self.insertWidget(idx, ow)
        osplitter.insertWidget(oidx, w)
        self.root.marked = self, self.indexOf(ow), 0, ow
        self.equalize_sizes()
        osplitter.equalize_sizes()
    #@+node:ekr.20110605121601.17988: *3* ns.top
    def top(self, local=False):
        """find top (outer) widget, which is not necessarily root"""
        if local:
            top = self
            while isinstance(top.parent(), NestedSplitter):
                top = top.parent()
        else:
            top = self.root._main.findChild(NestedSplitter)
        return top
    #@+node:ekr.20110605121601.17989: *3* ns.get_layout
    def get_layout(self):
        """
        Return a dict describing the layout.

        Usually you would call ns.top().get_layout()
        """
        ans = {
            'content': [],
            'orientation': self.orientation(),
            'sizes': self.sizes(),
            'splitter': self,
        }
        for i in range(self.count()):
            w = self.widget(i)
            if isinstance(w, NestedSplitter):
                ans['content'].append(w.get_layout())
            else:
                ans['content'].append(w)
        return ans
    #@+node:tbrown.20110628083641.11733: *3* ns.get_saveable_layout
    def get_saveable_layout(self):
        """
        Return the dict for saveable layouts.

        The content entry for non-NestedSplitter items is the provider ID
        string for the item, or 'UNKNOWN', and the splitter entry is omitted.
        """
        ans = {
            'content': [],
            'orientation': 1 if self.orientation() == Orientation.Horizontal else 2,
            'sizes': self.sizes(),
        }
        for i in range(self.count()):
            w = self.widget(i)
            if isinstance(w, NestedSplitter):
                ans['content'].append(w.get_saveable_layout())
            else:
                ans['content'].append(getattr(w, '_ns_id', 'UNKNOWN'))
        return ans
    #@+node:ekr.20160416083415.1: *3* ns.get_splitter_by_name
    def get_splitter_by_name(self, name):
        """Return the splitter with the given objectName()."""
        if self.objectName() == name:
            return self
        for i in range(self.count()):
            w = self.widget(i)
            # Recursively test w and its descendants.
            if isinstance(w, NestedSplitter):
                w2 = w.get_splitter_by_name(name)
                if w2:
                    return w2
        return None
    #@+node:tbrown.20110628083641.21154: *3* ns.load_layout
    def load_layout(self, c, layout, level=0):

        trace = 'layouts' in g.app.debug
        if trace:
            g.trace('level', level)
            tag = f"layout: {c.shortFileName()}"
            g.printObj(layout, tag=tag)
        if isQt6:
            if layout['orientation'] == 1:
                self.setOrientation(Orientation.Horizontal)
            else:
                self.setOrientation(Orientation.Vertical)
        else:
            self.setOrientation(layout['orientation'])
        found = 0
        if level == 0:
            for i in self.self_and_descendants():
                for n in range(i.count()):
                    i.widget(n)._in_layout = False
        for content_layout in layout['content']:
            if isinstance(content_layout, dict):
                new = NestedSplitter(root=self.root, parent=self)
                new._in_layout = True
                self.insert(found, new)
                found += 1
                new.load_layout(c, content_layout, level + 1)
            else:
                provided = self.get_provided(content_layout)
                if provided:
                    self.insert(found, provided)
                    provided._in_layout = True
                    found += 1
                else:
                    print(f"No provider for {content_layout}")
        self.prune_empty()
        if self.count() != len(layout['sizes']):
            not_in_layout = set()
            for i in self.self_and_descendants():
                for n in range(i.count()):
                    c = i.widget(n)
                    if not (hasattr(c, '_in_layout') and c._in_layout):
                        not_in_layout.add(c)
            for i in not_in_layout:
                self.close_or_keep(i)
            self.prune_empty()
        if self.count() == len(layout['sizes']):
            self.setSizes(layout['sizes'])
        else:
            print(
                f"Wrong pane count at level {level:d}, "
                f"count:{self.count():d}, "
                f"sizes:{len(layout['sizes']):d}")
            self.equalize_sizes()
    #@+node:tbrown.20110628083641.21156: *3* ns.prune_empty
    def prune_empty(self):
        for i in range(self.count() - 1, -1, -1):
            w = self.widget(i)
            if isinstance(w, NestedSplitter):
                if w.max_count() == 0:
                    w.setParent(None)
                    # w.deleteLater()
    #@+node:tbrown.20110628083641.21155: *3* ns.get_provided
    def find_by_id(self, id_):
        for s in self.self_and_descendants():
            for i in range(s.count()):
                if getattr(s.widget(i), '_ns_id', None) == id_:
                    return s.widget(i)
        return None

    def get_provided(self, id_):
        """IMPORTANT: nested_splitter should set the _ns_id attribute *only*
        if the provider doesn't do it itself.  That allows the provider to
        encode state information in the id.

        Also IMPORTANT: nested_splitter should call all providers for each id_, not
        just providers which previously advertised the id_.  E.g. a provider which
        advertises leo_bookmarks_show may also be the correct provider for
        leo_bookmarks_show:4532.234 - let the providers decide in ns_provide().
        """
        for provider in self.root.providers:
            if hasattr(provider, 'ns_provide'):
                provided = provider.ns_provide(id_)
                if provided:
                    if provided == 'USE_EXISTING':
                        # provider claiming responsibility, and saying
                        # we already have it, i.e. it's a singleton
                        w = self.top().find_by_id(id_)
                        if w:
                            if not hasattr(w, '_ns_id'):
                                # IMPORTANT: see docstring
                                w._ns_id = id_
                            return w
                    else:
                        if not hasattr(provided, '_ns_id'):
                            # IMPORTANT: see docstring
                            provided._ns_id = id_
                        return provided
        return None

    #@+node:ekr.20200917063155.1: *3* ns.get_title
    def get_title(self, id_):
        """Like get_provided(), but just gets a title for a window
        """
        if id_ is None:
            return "Leo widget window"
        for provider in self.root.providers:
            if hasattr(provider, 'ns_title'):
                provided = provider.ns_title(id_)
                if provided:
                    return provided
        return "Leo unnamed window"
    #@+node:tbrown.20140522153032.32656: *3* ns.zoom_toggle
    def zoom_toggle(self, local=False):
        """zoom_toggle - (Un)zoom current pane to be only expanded pane

        :param bool local: just zoom pane within its own splitter
        """
        if self.root.zoomed:
            for ns in self.top().self_and_descendants():
                if hasattr(ns, '_unzoom'):
                    # this splitter could have been added since
                    ns.setSizes(ns._unzoom)
        else:
            focused = g.app.gui.qtApp.focusWidget()
            parents = []
            parent = focused
            while parent:
                parents.append(parent)
                parent = parent.parent()
            if not focused:
                g.es("Not zoomed, and no focus")
            for ns in (self if local else self.top()).self_and_descendants():
                # FIXME - shouldn't be doing this across windows
                ns._unzoom = ns.sizes()
                for i in range(ns.count()):
                    w = ns.widget(i)
                    if w in parents:
                        sizes = [0] * len(ns._unzoom)
                        sizes[i] = sum(ns._unzoom)
                        ns.setSizes(sizes)
                        break
        self.root.zoomed = not self.root.zoomed
    #@+node:tbnorth.20160510092439.1: *3* ns._splitter_clicked
    def _splitter_clicked(self, handle, event, release, double):
        """_splitter_clicked - coordinate propagation of signals
        for clicks on handles.  Turned out not to need any particular
        coordination, handles could call self._splitterClickedSignal.emit
        directly, but design wise this is a useful control point.

        :param QSplitterHandle handle: handle that was clicked
        :param QMouseEvent event: click event
        :param bool release: was it a release event
        :param bool double: was it a double click event
        """
        self._splitterClickedSignal.emit(self, handle, event, release, double)
    #@+node:tbnorth.20160510123445.1: *3* splitterClicked_connect
    def splitterClicked_connect(self, *args):
        """Apply .connect() args to all actual splitters,
        and store for application to future splitters.
        """
        self.root._splitterClickedArgs.append(args)
        for splitter in self.top().self_and_descendants():
            splitter._splitterClickedSignal.connect(*args)
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo

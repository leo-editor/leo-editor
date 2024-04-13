#@+leo-ver=5-thin
#@+node:tbrown.20070322113635: * @file ../plugins/bookmarks.py
#@+<< docstring >>
#@+node:tbrown.20070322113635.1: ** << docstring >>
""" Manage bookmarks in a list, and show bookmarks in a pane.

This plugin has two bookmark related functions.  It manages nodes that
contain bookmarks, and can also display those nodes in a special
bookmarks pane / panel / subwindow.

Bookmark pane setup
-------------------

You can't set a bookmark using the bookmark pane view until you have designated
a node to be a root of a bookmark subtree. This is done by the "show" item in
the bookmarks menu or by the bookmarks-show command. This creates a pane for
displaying bookmarks and marks the selected node as the active bookmarks root
node for the outline. Initially the pane is completely blank. It is a good idea
to shrink this pane to one or two lines and then to save the current layout.
If you try to set a bookmark before doing a "bookmarks show," you will see the
error message "Bookmarks not active for this outline" in the log pane.

You can have several bookmark root nodes in one file. Each with its own bookmark
pane. Any of the bookmark panes can be used to go to a bookmark. But you can
only add bookmarks to the most recently designated bookmark root. The intended
use of the bookmarks plugin is that there is only one bookmarks pane per file.

General bookmark commands
-------------------------

**bookmarks-open-bookmark** opens the bookmark in the selected node **if** the
  node has an ancestor which contains ``@bookmarks`` in its heading.
**bookmarks-open-node**, like ``bookmarks-open-bookmark`` but without
  the ancestor requirement.
**bookmarks-switch**
  move between your working position in the outline, and the current
  bookmark, in the outline.  This is the keyboard friendly no extra pane
  alternative to the mouse based bookmark pane navigation described below.
**bookmarks-bookmark**
  Add the current node as a bookmark at the current level in the
  bookmarks tree.  Another keyboard friendly alternative.
**bookmarks-bookmark-child**
  Add the current node as a child of the current bookmark, if there is
  a current bookmark.  Another keyboard friendly alternative.

Cross file bookmark commands
----------------------------

These commands let you have personal bookmarks in a .leo file you're
sharing with others.  E.g. you can store your personal bookmarks for the
shared ``LeoPyRef.leo`` Leo development outline in ``~/.leo/workbook.leo``.

**bookmarks-mark-as-target**
  Mark a node in outline A as being the container for
  bookmarks in another outline, outline B.
**bookmarks-use-other-outline**
  Specify that this outline, outline B, should store its bookmarks
  in the marked node in outline A.  This also adds a bookmark display
  pane (described below), but you can ignore it, it won't persist unless
  you save the layout.

*Note:* bookmarks treats file urls missing the ``file://`` part as urls,
which deviates from Leo's behavior elsewhere.  It also recognizes local UNLs
like ``#ToDo-->Critical`` as urls.

Bookmarks pane commands
-----------------------

**bookmarks-show**
  Add a pane showing the bookmarks **in the current subtree**
  with unique colors. You can very quickly jump around between nodes in a file
  using this.

Nodes can be added and removed from the display with the following mouse actions:

**left-click on bookmark**
    Jump to that node.
**left-click on background**
    Add a bookmark at the position clicked, unless already present,
    in which case the existing link is highlighted.
**control-left-click on bookmark**
    Remove bookmark.
**shift-control-left-click on bookmark**
    Rename bookmark.
**alt-left-click on bookmark**
    Edit clicked bookmark in bookmark list, to change link text.
**alt-shift-left-click on bookmark**
    Move around bookmark hierarchy without changing nodes, useful for filing
**control-alt-left-click on bookmark**
    Update clicked bookmark to point to current node.
**alt-left-click on background**
    Edit bookmark list.
**shift-left-click on bookmark**
    Add the current node as a *child* of the clicked bookmark,
    and display the clicked bookmarks children.
**control-alt-shift-left-click on bookmark**
    Goto and hoist

The above as a table::

    SAC
    --- goto, or, ON BACKGROUND, add
    --+ delete
    -+- edit bookmark in tree (ON BACKGROUND, edit from top of bookmark tree)
    -++ link bookmark to current node
    +-- add as child bookmark, show children
    +-+ rename bookmark
    ++- show child bookmarks without changing selected node
    +++ goto and hoist


The ``@setting`` ``@int bookmarks-levels = 1`` sets the number of levels of
hierarchy shown in the bookmarks pane. By default, the @setting @int
bookmarks_levels = 1 will limit the bookmarks shown to one level, so given these
bookmarks::

  A
  B
     B1
     B2
  C

you'd just see A B C, with B underlined, indicating it has children, and when
you click B, one of two things happens.

With bookmarks_levels = 1 (the default) the effect of clicking on B depends on
whether or not B is itself a bookmark (contains an URL) or just an organizer
node (no body).

If it's just an organizer node, clicking it immediately shows its children. If
it contains an URL itself, the first click makes Leo navigate to that URL, a
subsequent click shows the children.

Note that this first click / second click behavior only applies with
@int bookmarks_levels = 1.

With @int bookmarks_levels = 2 or more, you'll initially see::

  A B C

with B underlined, and clicking on B will immediately show its children, so you see::

  A B C
  B1 B2

and, if B contains an URL, navigate to the URL

With @int bookmarks_levels = 0, the original behavior is used,
hierarchy is ignored, and you see::

  A B B1 B2 C

all the time.

**bookmarks-level-decrease**
  Temporarily decrease the value of the the ``@int bookmarks-levels``
  setting.
**bookmarks-level-increase**
  Temporarily increase the value of the the ``@int bookmarks-levels``
  setting.

Other notes
-----------

The free_layout Action button context menu will also allow you to add one of
these bookmark panes, and they will be saved and loaded again if the layout is
saved and loaded.

Bookmarks for tabbed body editors
+++++++++++++++++++++++++++++++++

Create a new outline with the following nodes, as simple top level nodes::

    aardvarks
    apples
    autos
    bats
    bison
    bunting
    @bookmarks

(pro-tip, with the paste_as_headlines plugin active, you can just copy the above
and use `Edit -> Paste as headlines`, you'll need to promote them to top level
again though).

Select the ``@bookmarks`` node and then Alt-X `bookmarks-show`, which should
create a new empty pane above the body pane. Select the ``aardvarks`` node and
click in the new empty pane, repeat for the ``bats`` node.

Squish the new empty pane up so it's just high enough to hold the two bookmarks,
or "tabs", and then right click a pane divider and save this layout as "Tabs" or
whatever you want to call it.

So now you have two tabs which jump between two nodes. Click the ``aardvarks``
tab, then select the ``apples`` node. Now shift-click the ``aardvarks`` tab. Now
you are entering sub tabs of the ``aardvarks`` tab. You might want to repeat the
``aardvarks`` tab at this level, just select the node and click in the empty
space in the bookmarks pane to repeat it here. You could add ``autos`` at this
level too.

How the 'tabs' are displayed (one or more levels at once etc.) and how you edit
them are described in the earlier parts of these docs. For example at the top
level the first time you click the ``aardvarks`` tab it just shows you the
``aardvarks`` node, it requires a second click to see its subtabs (aardvarks,
apples, and autos), because the top level ``aardvarks`` tab is both a bookmark
and an organizer node. If you want it to be just and organizer node, alt-click
it to edit the bookmark node itself, and delete the body text (UNL) there.

"""

#@-<< docstring >>
# Written by Terry Brown.
#@+<< imports >>
#@+node:tbrown.20070322113635.3: ** << imports >>
from collections import namedtuple
import hashlib
from leo.core import leoGlobals as g
from leo.core.leoQt import QtCore, QtWidgets
from leo.core.leoQt import ControlType, KeyboardModifier, MouseButton, Orientation, Policy, QAction

# Fail fast, right after all imports.
g.assertUi('qt')  # May raise g.UiTypeException, caught by the plugins manager.
#@-<< imports >>
#@+others
#@+node:ekr.20100128073941.5371: ** init (bookmarks.py)
def init():
    """Return True if the plugin has loaded successfully."""
    if g.unitTesting:
        return False
    g.registerHandler('after-create-leo-frame', onCreate)
    # temporary until double-click is bindable in user settings
    if g.app.config.getBool('bookmarks-grab-dblclick', default=False):
        g.registerHandler('headdclick1', lambda t, k: cmd_open_bookmark(k))
    g.plugin_signon(__name__)
    return True

#@+node:tbrown.20110712121053.19751: ** onCreate
def onCreate(tag, keys):

    c = keys.get('c')
    if not c:
        return
    BookMarkDisplayProvider(c)
#@+node:tbrown.20120319161800.21489: ** bookmarks-open-*
@g.command('bookmarks-open-bookmark')
def cmd_open_bookmark(event):
    c = event.get('c')
    if not c:
        return
    p = c.p
    bookmark = False
    for nd in p.parents():
        if '@bookmarks' in nd.h:
            bookmark = True
            break
    if bookmark:
        if hasattr(c, '_bookmarks'):
            c._bookmarks.current = p.v
        cmd_open_node({'c': c})

@g.command('bookmarks-open-node')
def cmd_open_node(event):
    c = event.get('c')
    if not c:
        return
    p = c.p
    url = g.getUrlFromNode(p)
    if url:
        # No need to handle url hooks here.
        g.handleUrl(url, c=c, p=p)

#@+node:tbrown.20110712100955.39215: ** bookmarks-show
@g.command('bookmarks-show')
def cmd_show(event):

    c = event.get('c')
    bmd = BookMarkDisplay(c)
    # Careful: we could be unit testing.
    splitter = bmd.c.free_layout.get_top_splitter()
    if splitter:
        splitter.add_adjacent(bmd.w, 'bodyFrame', 'above')
#@+node:tbrown.20131226095537.26309: ** bookmarks-switch
@g.command('bookmarks-switch')
def cmd_switch(event):
    """switch between bookmarks and previous position in outline"""
    c = event.get('c')
    if not hasattr(c, '_bookmarks'):
        g.es("Bookmarks not active for this outline")
        return
    bm = c._bookmarks
    if bm.current is None:
        # startup condition, this is not done in __init__ because that
        # would lead to premature highlighting of the 'current' bookmark
        if bm.v.children:
            bm.current = bm.v.children[0]  # first bookmark
        else:
            bm.current = bm.v  # bookmark node itself
    if c.p.v == bm.current:
        ov = bm.previous
    else:
        ov = bm.current
        bm.previous = c.p.v

    if not ov:
        g.es("No alternate position known")
        return

    oc = ov.context
    op = oc.vnode2position(ov)
    if not oc.positionExists(op):
        g.es("No alternate position known")
        return
    oc.selectPosition(op)
    oc.redraw()
    oc.bringToFront()

#@+node:tbrown.20140101093550.25175: ** bookmarks-bookmark-*
def _get_bm_container(c, child=False, organizer=False):
    """_get_bm_container - get the controller and container for a new bookmark

    :param outline c: outline
    :return: controller, vnode
    :rtype: tuple
    """

    if not hasattr(c, '_bookmarks'):
        g.es("Bookmarks not active for this outline")
        return None, None
    bm = c._bookmarks
    if bm.current is None:  # first use
        bm.current = bm.v
    if bm.current == bm.v:  # first use or other conditions
        container = bm.v
    elif child:
        container = bm.current
    elif not bm.current.b.strip():  # no url implies folder
        container = bm.current
    else:
        # pylint: disable=consider-using-ternary
        container = bm.current.parents and bm.current.parents[0] or bm.v

    return bm, container

@g.command('bookmarks-bookmark')
def cmd_bookmark(event, child=False, organizer=False, container=None):
    """bookmark current node"""
    c = event.get('c')

    bm, _container = _get_bm_container(c, child=child, organizer=organizer)
    if container is None:
        if bm.current and bm.current.children and bm.second:
            container = bm.current
        else:
            container = _container

    new_url = bm.get_unl()

    # check url doesn't exist at this level
    dupes = [i for i in container.children
             if i.b.split('\n', 1)[0].strip() == new_url]
    if dupes and not organizer:
        what = "Child bookmark" if child else "Bookmark"
        g.es("%s exists" % what, color='red')
        for other in bm.get_list(levels=0):
            if other.v in dupes:
                other.v.u['__bookmarks']['is_dupe'] = True
        bm.show_list(bm.get_list())
        return

    bc = container.context
    bp = bc.vnode2position(container)
    nd = bp.insertAsNthChild(0)
    # pylint: disable=consider-using-ternary
    nd.h = (
        c.frame.body.wrapper.hasSelection() and
        c.frame.body.wrapper.getSelectedText() or
        bm.fix_text(c.p.h)
    )
    if not organizer:
        nd.b = new_url
    else:
        nd.v.u['__bookmarks'] = {
            'is_dupe': False,
        }
    bm.current = nd.v
    if organizer:
        g.es("Showing new (empty) folder:\n'%s'" % nd.h)
    bm.show_list(bm.get_list())

    c.bodyWantsFocusNow()

@g.command('bookmarks-bookmark-child')
def cmd_bookmark_child(event):
    """bookmark current node as child of current bookmark"""
    cmd_bookmark(event, child=True)

@g.command('bookmarks-bookmark-organizer')
def cmd_bookmark_organizer(event, container=None):
    """bookmark current node as organizer (no link)"""
    cmd_bookmark(event, organizer=True, container=container)

@g.command('bookmarks-bookmark-find-flat')
def cmd_bookmark_find_flat(event):
    """like clone find flat"""

    c = event.get('c')
    bm, container = _get_bm_container(c)
    if bm is None:
        return
    ans = g.app.gui.runAskOkCancelStringDialog(c, "Search for", "Target:")
    if ans is None or not ans.strip():
        return

    nodes = []
    for nd in c.all_unique_nodes():
        if ans in nd.b:
            nodes.append(nd)
    if not nodes:
        g.es("No matches")
    container = container.insertAsNthChild(0)
    container.h = ans
    container.b = "FIXME: put search time here?"
    for nd in nodes[:40]:
        new = container.insertAsLastChild()
        new.h = nd.h
        new.b = c.vnode2position(nd).get_UNL()
    bm.show_list(bm.get_list())
    if len(nodes) > 40:
        g.es("Stopped after 40 hits")

#@+node:tbrown.20140101093550.25176: ** bookmarks-level-*
@g.command('bookmarks-level-increase')
def cmd_level_increase(event, delta=1):
    """increase levels, number of rows shown, for bookmarks"""
    c = event.get('c')
    if not hasattr(c, '_bookmarks'):
        g.es("Bookmarks not active for this outline")
        return
    bm = c._bookmarks
    if bm.levels + delta >= 0:
        bm.levels += delta
    g.es("Showing %d levels" % bm.levels)
    bm.show_list(bm.get_list())

@g.command('bookmarks-level-decrease')
def cmd_level_decrease(event):
    """decrease levels, number of rows shown, for bookmarks"""
    cmd_level_increase(event, delta=-1)

#@+node:tbrown.20131214112218.36871: ** bookmarks-mark
@g.command('bookmarks-mark-as-target')
def cmd_mark_as_target(event):
    """Mark current node as Bookmarks list for use by another file,
    bookmarks-use-other-outline should be used after this command
    """
    c = event.get('c')
    g._bookmarks_target = c.p.get_UNL()
    g._bookmarks_target_v = c.p.v
    g.es("Node noted - now use\nbookmarks-use-other-outline\nin the "
        "outline you want to\nstore bookmarks in this node")

#@+node:ekr.20190619132530.1: ** bookmarks-use-other-outline
@g.command('bookmarks-use-other-outline')
def cmd_use_other_outline(event):
    """Set bookmarks for this outline from a list (node) in
    a different outline
    """
    c = event.get('c')
    if not hasattr(g, '_bookmarks_target') or not g._bookmarks_target:
        g.es("Use bookmarks-mark-as-target first")
        return
    c.db['_leo_bookmarks_show'] = g._bookmarks_target
    bmd = BookMarkDisplay(c, g._bookmarks_target_v)
    splitter = c.free_layout.get_top_splitter()
    if splitter:
        splitter.add_adjacent(bmd.w, 'bodyFrame', 'above')

#@+node:ekr.20140917180536.17896: ** class FlowLayout (QLayout)
class FlowLayout(QtWidgets.QLayout):  # type:ignore
    """
    from http://ftp.ics.uci.edu/pub/centos0/ics-custom-build/BUILD/
    PyQt-x11-gpl-4.7.2/examples/layouts/flowlayout.py
    """
    #@+others
    #@+node:ekr.20140917180536.17897: *3* __init__
    def __init__(self, parent=None, margin=0, spacing=-1):
        """Ctor for FlowLayout class."""
        super().__init__(parent)
        if parent is not None:
            self.setMargin(margin)
        else:
            self.setMargin(0)
        self.setSpacing(spacing)
        self.itemList = []
    #@+node:ekr.20140917180536.17898: *3* __del__
    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    #@+node:ekr.20140917180536.17899: *3* addItem
    def addItem(self, item):
        self.itemList.append(item)

    #@+node:ekr.20140917180536.17900: *3* insertWidget
    def insertWidget(self, index, item):
        x = QtWidgets.QWidgetItem(item)
        assert x  # for pyflakes
        # item.setParent(x)
        # self.itemList.insert(index, x)

    #@+node:ekr.20140917180536.17901: *3* count
    def count(self):
        return len(self.itemList)

    #@+node:ekr.20140917180536.17902: *3* itemAt
    def itemAt(self, index):
        if 0 <= index < len(self.itemList):
            return self.itemList[index]
        return None
    #@+node:ekr.20140917180536.17903: *3* takeAt
    def takeAt(self, index):
        if 0 <= index < len(self.itemList):
            return self.itemList.pop(index)
        return None

    #@+node:ekr.20140917180536.17904: *3* expandingDirections (override)
    def expandingDirections(self):

        """
        Override of QLayout.expandingDirections.

        Returns whether this layout can make use of more space than sizeHint().
        A value of Qt::Vertical or Qt::Horizontal means that it wants to grow in only one dimension,
        whereas Qt::Vertical | Qt::Horizontal means that it wants to grow in both dimensions.
        """
        return Orientation.Horizontal  # Best guess.

    #@+node:ekr.20140917180536.17905: *3* hasHeightForWidth
    def hasHeightForWidth(self):
        return True

    #@+node:ekr.20140917180536.17906: *3* heightForWidth
    def heightForWidth(self, width):
        height = self.doLayout(QtCore.QRect(0, 0, width, 0), True)
        return height

    #@+node:ekr.20140917180536.17907: *3* setGeometry
    def setGeometry(self, rect):
        super().setGeometry(rect)
        self.doLayout(rect, False)

    #@+node:ekr.20140917180536.17908: *3* sizeHint
    def sizeHint(self):
        return self.minimumSize()

    #@+node:ekr.20140917180536.17909: *3* minimumSize
    def minimumSize(self):

        size = QtCore.QSize()
        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())
        size += QtCore.QSize(2 * self.margin(), 2 * self.margin())
        return size

    #@+node:ekr.20140917180536.17910: *3* doLayout
    def doLayout(self, rect, testOnly):
        x = rect.x()
        y = rect.y()
        lineHeight = 0
        for item in self.itemList:
            wid = item.widget()
            spaceX = self.spacing() + wid.style().layoutSpacing(
                ControlType.PushButton, ControlType.PushButton, Orientation.Horizontal)
            spaceY = self.spacing() + wid.style().layoutSpacing(
                ControlType.PushButton, ControlType.PushButton, Orientation.Vertical)
            nextX = x + item.sizeHint().width() + spaceX
            if nextX - spaceX > rect.right() and lineHeight > 0:
                x = rect.x()
                y = y + lineHeight + spaceY
                nextX = x + item.sizeHint().width() + spaceX
                lineHeight = 0
            if not testOnly:
                item.setGeometry(QtCore.QRect(QtCore.QPoint(x, y), item.sizeHint()))
            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())
        return y + lineHeight - rect.y()
    #@+node:tbnorth.20160315104244.1: *3* margin
    def margin(self):
        """margin - return margin
        """

        return self._margin

    #@+node:tbnorth.20160315104324.1: *3* setMargin
    def setMargin(self, margin):
        """setMargin - set margin

        :param int margin: margin to set
        """

        self._margin = margin

    #@-others

#@+node:tbrown.20110712100955.18924: ** class BookMarkDisplay
class BookMarkDisplay:
    """Manage a pane showing bookmarks"""
    Bookmark = namedtuple('Bookmark', 'head url ancestors siblings children v')

    ModMap = {
        KeyboardModifier.NoModifier: 'None',
        KeyboardModifier.AltModifier: 'Alt',
        KeyboardModifier.AltModifier | KeyboardModifier.ControlModifier: 'AltControl',
        (KeyboardModifier.AltModifier
        | KeyboardModifier.ControlModifier
        | KeyboardModifier.ShiftModifier): 'AltControlShift',
        KeyboardModifier.AltModifier | KeyboardModifier.ShiftModifier: 'AltShift',
        KeyboardModifier.ControlModifier: 'Control',
        KeyboardModifier.ControlModifier | KeyboardModifier.ShiftModifier: 'ControlShift',
        KeyboardModifier.ShiftModifier: 'Shift'
    }

    #@+others
    #@+node:tbrown.20110712100955.18926: *3* __init__ & reloadSettings (BookMarkDisplay)
    def __init__(self, c, v=None):

        self.c = c
        c._bookmarks = self
        # self.v - where the bookmarks for c are kept, may not be in c
        if v is None:
            v = self.v = c.p.v
        else:
            self.v = v
        self.current = None  # current (last used) bookmark
        self.previous = None  # position in outline, for outline / bookmarks switch
        self.levels = c.config.getInt('bookmarks-levels') or 1
        # levels to show in hierarchical display
        self.second = False  # second click of current bookmark?
        self.upwards = False  # moving upwards through hierarchy
        self.w = QtWidgets.QWidget()
        self.reloadSettings()
        # stuff for pane persistence
        self.w._ns_id = '_leo_bookmarks_show:'
        # v might not be in this outline
        c.db['_leo_bookmarks_show'] = v.context.vnode2position(v).get_UNL()
        # else:
            # c.frame.log.createTab(c.p.h[:10])
            # tabWidget = c.frame.log.tabWidget
            # self.w = tabWidget.widget(tabWidget.count()-1)
        self.w.setObjectName('show_bookmarks')
        self.w.setMinimumSize(10, 10)
        self.w.setLayout(QtWidgets.QVBoxLayout())
        self.w.layout().setContentsMargins(0, 0, 0, 0)
        self.current_list = self.get_list()
        self.show_list(self.current_list)
        g.registerHandler('select1', self.update)

    def reloadSettings(self):
        c = self.c
        c.registerReloadSettings(self)
        self.dark = c.config.getBool("color-theme-is-dark")
        mod_map = c.config.getData("bookmarks-modifiers")
        if not mod_map:
            mod_map = """
                None goto_bookmark
                AltControl update_bookmark
                ControlShift rename_bookmark
                Alt edit_bookmark
                Control delete_bookmark
                Shift add_child
                AlfShift navigate
                AltControlShift hoist
            """.split('\n')
        self.mod_map = dict(i.strip().split() for i in mod_map if i.strip())


    #@+node:tbrown.20131227100801.30379: *3* background_clicked
    def background_clicked(self, event, bookmarks, row_parent):
        """background_clicked - Handle a background click in a bookmark pane

        :Parameters:
        - `event`: click event
        - `bookmarks`: bookmarks in this pane
        """
        if event.button() == MouseButton.RightButton:
            self.context_menu(event, container=row_parent)
            return

        # Alt => edit bookmarks in the outline
        mods = event.modifiers()
        if mods == KeyboardModifier.AltModifier:
            self.edit_bookmark(None, v=row_parent)
            return
        cmd_bookmark(event={'c': row_parent.context}, container=row_parent)

    #@+node:tbnorth.20160502105134.1: *3* button_clicked
    def button_clicked(self, event, bm, but, up=False):
        """button_clicked - handle a button being clicked

        :Parameters:
        - `event`: QPushButton event
        - `bm`: Bookmark associated with button
        - `but`: button widget
        """
        if event.button() == MouseButton.RightButton:
            self.button_menu(event, bm, but, up=up)
            return

        action_name = self.mod_map.get(self.ModMap.get(event.modifiers()))
        if action_name is None:
            g.es("Bookmarks: unknown click type")
            print(int(event.modifiers()))
            for k, v in self.ModMap.items():
                print(k, v)
            for k, v in self.mod_map.items():
                print(k, v)
            return

        if action_name in ('update_bookmark', 'rename_bookmark',
            'edit_bookmark', 'delete_bookmark', 'promote_bookmark'):
            # simple bookmark actions
            getattr(self, action_name)(bm)
            return
        if action_name == 'add_child':
            cmd_bookmark_child(event={'c': bm.v.context})
            return

        no_move = action_name == 'navigate'
        hoist = action_name == 'hoist'

        # otherwise, look up the bookmark
        self.upwards = up
        self.second = not up and self.current == bm.v
        self.current = bm.v
        if up and not bm.url and bm.v != self.v:
            # folders are only current when you're in them
            pass
            # this causes bookmark position to go rootwards by two steps, disabled
            # self.current = self.current.parents[0]
        # in case something we didn't see changed the bookmarks
        self.show_list(self.get_list(), up=up)
        if bm.url and not up and not no_move:
            g.handleUrl(bm.url, c=self.c)
            if hoist:
                self.c.hoist()
        else:
            # don't leave focus adrift when clicking organizer node
            self.c.bodyWantsFocusNow()
    #@+node:tbrown.20140807091931.30231: *3* button_menu
    def button_menu(self, event, bm, but, up=False):
        """button_menu - handle a button being right-clicked

        :Parameters:
        - `event`: QPushButton event
        - `bm`: Bookmark associated with button
        - `but`: button widget
        """

        menu = QtWidgets.QMenu()

        actions = [
            ("Link to this node", self.update_bookmark),
            ("Promote", self.promote_bookmark),
            ("Re-name", self.rename_bookmark),
            ("Edit in tree", self.edit_bookmark),
            ("Delete", self.delete_bookmark),
            ("Add this node as child bookmark",
                lambda e: cmd_bookmark_child(event={'c': bm.v.context})),
            ("Add bookmark folder",
                lambda e: cmd_bookmark_organizer(event={'c': bm.v.context})),
        ]
        for action in actions:
            act = QAction(action[0], menu)
            act.triggered.connect(lambda checked, bm=bm, f=action[1]: f(bm))
            menu.addAction(act)

        def follow(checked, bm=bm, manager=self):
            manager.current = bm.v
            manager.second = True
            manager.upwards = False
            manager.show_list(manager.get_list(), up=False)
        act = QAction("Show child bookmarks", menu)
        act.triggered.connect(follow)
        menu.addAction(act)

        point = event.position().toPoint()  # Qt6 documentation is wrong.
        global_point = but.mapToGlobal(point)
        menu.exec(global_point)
    #@+node:tbnorth.20160830110146.1: *3* context_menu
    def context_menu(self, event, container=None):
        """context_menu
        """

        menu = QtWidgets.QMenu()
        bm = self.c._bookmarks

        actions = [
            ("Edit bookmarks in tree", self.edit_bookmark),
            ("Add bookmark folder",
                lambda e: cmd_bookmark_organizer(
                    event={'c': bm.v.context}, container=container),
            ),
        ]
        for action in actions:
            act = QAction(action[0], menu)
            act.triggered.connect(lambda checked, bm=bm, f=action[1]: f(bm))
            menu.addAction(act)

        point = event.position().toPoint()  # Qt6 documentation is wrong.
        global_point = menu.mapToGlobal(point)
        menu.exec(global_point)
    #@+node:tbrown.20110712100955.18925: *3* color
    def color(self, text, dark=False):
        """make a consistent light background color for text"""
        text = g.toEncodedString(text, 'utf-8')
        x = hashlib.md5(text).hexdigest()[-6:]
        add = int('bb', 16) if not dark else int('33', 16)
        x = tuple(int(x[2 * i : 2 * i + 2], 16) // 4 + add for i in range(3))  # type:ignore
        x = '%02x%02x%02x' % x
        return x
    #@+node:tbrown.20131227100801.23856: *3* find_node
    def find_node(self, url):
        """find_node - Return position which is a bookmark for url, or None

        :Parameters:
        - `url`: url to find
        """
        url = url.strip().replace(' ', '%20')
        p = self.v.context.vnode2position(self.v)
        for node in p.subtree():
            if node.b.split('\n', 1)[0].strip().replace(' ', '%20') == url:
                return node
        return None

    #@+node:tbrown.20140206130031.25813: *3* fix_text
    def fix_text(self, text):
        """fix_text - Return text with any leading @<file> removed

        :Parameters:
        - `text`: text to fix
        """
        text = text.strip()
        parts = text.split()
        if parts[0][0] == '@':
            if len(parts) > 1:
                del parts[0]
            elif len(parts[0]) > 1:
                parts[0] = parts[0][1:]
            return ' '.join(parts)
        return text

    #@+node:tbrown.20110712100955.39216: *3* get_list
    def get_list(self, levels=None):
        """Return list of Bookmarks
        """

        # v might not be in this outline
        p = self.v.context.vnode2position(self.v)
        if not p:
            return None

        if levels is None:
            levels = self.levels

        def strip(s):
            if s.startswith('@url'):
                s = s[4:]
            return s.strip()

        result: list = []

        def recurse_bm(node, result, ancestors=None):

            if ancestors is None:
                ancestors = []

            for p in node.children():

                if p.b and p.b[0] == '#':
                    # prevent node url ending with name of
                    # file which exists being confused
                    url = p.b.split('\n', 1)[0]
                else:
                    url = g.getUrlFromNode(p)

                if url:
                    url = url.replace(' ', '%20')
                h = self.fix_text(p.h)

                children: list = []
                bm = self.Bookmark(
                    h, url, ancestors, result, children, p.v)

                result.append(bm)

                if levels == 0:  # non-hierarchical
                    recurse_bm(p, result)
                else:
                    recurse_bm(p, children, ancestors=ancestors + [bm])

        recurse_bm(p, result)

        return result

    #@+node:tbrown.20140103082018.24102: *3* get_unl (bookmarks.py)
    def get_unl(self, p=None):
        """get_unl - Return a UNL which is local (with_file=False)
        if self.c == self.v.context, otherwise includes the file path.

        :Parameters:
        - `p`: position to use instead of self.c.p
        """
        p = p or self.c.p
        c = p.v.context  # just in case it's not self.c
        if self.v.context == c:
            # local
            return "#" + p.get_UNL(with_file=False, with_proto=False)
        # not local
        return p.get_UNL(with_file=True, with_proto=True)

    #@+node:tbrown.20131227100801.23858: *3* show_list
    def show_list(self, links, up=False):
        """show_list - update pane with buttons

        :Parameters:
        - `links`: Bookmarks to show
        """
        p = self.v.context.vnode2position(self.v)
        if not p:
            return

        w = self.w

        cull = w.layout().takeAt(0)
        while cull:
            if cull.widget():
                cull.widget().deleteLater()
            cull = w.layout().takeAt(0)

        todo = [links or []]  # empty list to create container to click in to add first
        current_level = 1
        current_url = None
        showing_chain = []
        row_parent = self.v
        while todo:
            links = todo.pop(0) if todo else []
            top = QtWidgets.QWidget()

            def top_mouseReleaseEvent(event, links=links, row_parent=row_parent) -> None:
                self.background_clicked(event, links, row_parent)

            top.mouseReleaseEvent = top_mouseReleaseEvent  # type:ignore

            top.setMinimumSize(10, 10)  # so there's something to click when empty
            size_policy = QtWidgets.QSizePolicy(Policy.Expanding, Policy.Expanding)
            size_policy.setHorizontalStretch(1)
            size_policy.setVerticalStretch(1)
            top.setSizePolicy(size_policy)

            w.layout().addWidget(top)

            layout = FlowLayout()
            layout.setSpacing(5)
            top.setLayout(layout)

            if not links:
                layout.addWidget(QtWidgets.QLabel("(empty bookmarks folder)"))

            for bm in links:

                bm.v.u.setdefault('__bookmarks', {
                    'is_dupe': False,
                })

                but = QtWidgets.QPushButton(bm.head)
                if bm.url:
                    but.setToolTip(bm.url)

                def button_mouseReleaseEvent(event, bm=bm, but=but) -> None:
                    self.button_clicked(event, bm, but)

                but.mouseReleaseEvent = button_mouseReleaseEvent  # type:ignore
                layout.addWidget(but)

                showing = False
                if self.current and (bm.children or not bm.url):
                    nd = self.current
                    while nd != bm.v and nd.parents:
                        nd = nd.parents[0]
                    if nd == bm.v:
                        showing = True
                        todo.append(bm.children)
                        row_parent = bm.v

                if bm.v.u['__bookmarks'].get('is_dupe'):
                    style_sheet = "background: red; color: white;"
                else:
                    style_sheet = ("background: #%s;" %
                        self.color(bm.head, dark=self.dark))

                but.setStyleSheet(style_sheet)
                bm.v.u['__bookmarks']['is_dupe'] = False

                classes = []
                if bm.v == self.current:
                    classes += ['bookmark_current']
                    current_level = self.w.layout().count()
                    current_url = bm.url
                if showing:
                    classes += ['bookmark_expanded']
                    showing_chain += [bm]
                if bm.children or not bm.url:
                    classes += ['bookmark_children']
                but.setProperty('style_class', ' '.join(classes))

        if self.levels:  # drop excess levels
            if ((
                not self.second and
                current_url and
                current_url.strip() and
                self.levels == 1 or
                up or self.upwards
            ) and
                current_level < self.w.layout().count() and
                self.levels < self.w.layout().count()
            ):
                # hide last line, of children, if none are current
                self.w.layout().takeAt(self.w.layout().count() - 1).widget().deleteLater()

            while self.w.layout().count() > self.levels:

                # add an up button to the second row...
                next_row = self.w.layout().itemAt(1).widget().layout()
                but = QtWidgets.QPushButton('^')
                bm = showing_chain.pop(0)

                def mouseReleaseHandler2(event, bm=bm, but=but):
                    self.button_clicked(event, bm, but, up=True)

                but.mouseReleaseEvent = mouseReleaseHandler2  # type:ignore
                next_row.addWidget(but)
                # rotate to start of layout, FlowLayout() has no insertWidget()
                next_row.itemList[:] = next_row.itemList[-1:] + next_row.itemList[:-1]

                # ...then delete the first
                self.w.layout().takeAt(0).widget().deleteLater()

        w.layout().addStretch()

    #@+node:tbrown.20110712100955.39218: *3* update
    def update(self, tag, keywords):
        """re-show the current list of bookmarks"""

        if keywords['c'] is not self.c:
            return None

        self.show_list(self.get_list())

        return None  # do not stop processing the select1 hook

    #@+node:tbrown.20130222093439.30271: *3* delete_bookmark
    def delete_bookmark(self, bm):

        c = bm.v.context
        p = c.vnode2position(bm.v)
        u = c.undoer
        if p.hasVisBack(c):
            newNode = p.visBack(c)
        else:
            newNode = p.next()
        p.setAllAncestorAtFileNodesDirty()

        undoData = u.beforeDeleteNode(p)
        if self.current == p.v:
            self.current = p.v.parents[0]
        p.doDelete(newNode)  # p is deleted, newNode is where to go afterwards
        c.setChanged()
        u.afterDeleteNode(newNode, "Bookmark deletion", undoData)
        c.redraw()
        self.c.bodyWantsFocusNow()

        self.show_list(self.get_list())

    #@+node:tbrown.20140804215436.30052: *3* promote_bookmark
    def promote_bookmark(self, bm):
        """Promote bookmark"""
        p = bm.v.context.vnode2position(bm.v)
        p.moveToFirstChildOf(p.parent())
        bm.v.setDirty()
        bm.v.context.setChanged()
        bm.v.context.redraw()
        bm.v.context.bodyWantsFocusNow()
        self.show_list(self.get_list())
    #@+node:tbrown.20171128173307.1: *3* rename_bookmark
    def rename_bookmark(self, bm):
        """Rename bookmark"""

        default = self.c.frame.body.wrapper.getSelectedText()
        if not default or not default.strip() or len(default) > 20:
            default = bm.head

        txt = g.app.gui.runAskOkCancelStringDialog(
            self.c,
            "Rename " + bm.head,
            "New name for " + bm.head,
            default=default
        )

        if txt:
            bm.v.h = txt
            bm.v.context.redraw()
            bm.v.context.bodyWantsFocusNow()
            self.show_list(self.get_list())

    #@+node:tbrown.20130601104424.55363: *3* update_bookmark
    def update_bookmark(self, bm):
        """Update *EXISTING* bookmark to current node"""

        new_url = self.get_unl()
        if bm.v.b == new_url:
            g.es("Bookmark unchanged")
            return
        g.es("Bookmark updated")
        bm.v.b = new_url
        bm.v.setDirty()
        bm.v.context.setChanged()
        bm.v.context.redraw()
        bm.v.context.bodyWantsFocusNow()
        self.show_list(self.get_list())

    #@+node:tbrown.20130222093439.30275: *3* edit_bookmark
    def edit_bookmark(self, bm, v=None):

        if v is None:
            v = bm.v

        c = v.context
        self.current = v
        self.second = False
        p = c.vnode2position(v)
        c.selectPosition(p)
        c.bringToFront()

    #@-others

#@+node:tbrown.20110712121053.19746: ** class BookMarkDisplayProvider
class BookMarkDisplayProvider:
    #@+others
    #@+node:tbrown.20110712121053.19747: *3* __init__
    def __init__(self, c):
        self.c = c
        splitter = c.free_layout.get_top_splitter()
        # Careful: we could be unit testing.
        if splitter:
            splitter.register_provider(self)

    #@+node:tbrown.20110712121053.19748: *3* ns_provides
    def ns_provides(self):
        return [('Bookmarks', '_leo_bookmarks_show')]

    #@+node:tbrown.20110712121053.19749: *3* ns_provide (bookmarks.py)
    def ns_provide(self, id_):
        if id_.startswith('_leo_bookmarks_show'):

            c = self.c
            v = None

            if ':' in id_:
                gnx = id_.split(':')[1]
                if not gnx and '_leo_bookmarks_show' in c.db:
                    gnx = c.db['_leo_bookmarks_show']
                # first try old style local gnx lookup
                for i in c.all_nodes():
                    if str(i.gnx) == gnx:
                        v = i
                        break
                else:  # use UNL lookup
                    if '#' in gnx:
                        file_, UNL = gnx.split('#', 1)
                        other_c = g.openWithFileName(file_, old_c=c)
                    else:
                        file_, UNL = None, gnx
                        other_c = c
                    if other_c != c:
                        # don't use c.bringToFront(), it breaks --minimize
                        if hasattr(g.app.gui, 'frameFactory'):
                            factory = g.app.gui.frameFactory
                            if factory and hasattr(factory, 'setTabForCommander'):
                                factory.setTabForCommander(c)

                        g.es("NOTE: bookmarks for this outline\nare in a different outline:\n  '%s'" % file_)
                    other_p = g.findAnyUnl(UNL, other_c)
                    if other_p:
                        v = other_p.v
                    else:
                        g.es("Couldn't find '%s'" % gnx)

            if v is None:
                v = c.p.v

            bmd = BookMarkDisplay(self.c, v=v)
            return bmd.w
        return None

    #@-others

#@-others
#@@language python
#@@tabwidth -4

#@-leo

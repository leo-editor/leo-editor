#@+leo-ver=5-thin
#@+node:tbrown.20070322113635: * @file bookmarks.py
#@+<< docstring >>
#@+node:tbrown.20070322113635.1: ** << docstring >>
''' Manage bookmarks in a list, and show bookmarks in a pane.

This plugin has two bookmark related functions.  It manages nodes that
contain bookmarks, and can also display those nodes in a special
bookmarks pane / panel / subwindow.

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

The ``@setting`` ``@int bookmarks-levels = 1`` sets the number of levels of
hierarchy shown in the bookmarks pane. By default, the @setting @int
bookmarks_levels = 1 will limit the bookmarks shown to one level, so given these
bookmarks::

  A
  B
     B1
     B2
  C

you'd just see A B C, with B underlined, indicating it has
children, and when you click B, one of two things happens.

With bookmarks_levels = 1 (the default) the effect of clicking on B
depends on whether or not B is itself a bookmark (contains an URL)
or just an organizer node (no body).

If it's just an organizer node, clicking it immediately shows its
children.  If it contains an URL itself, the first click makes Leo
navigate to that URL, a subsequent click shows the children.

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

The ``quickMove.py`` plugin also provides actions for adding nodes to a bookmark list.

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

(pro-tip, with the paste_as_headlines plugin active, you can just copy the above and use `Edit -> Paste as headlines`, you'll need to promote them to top level again though).

Select the ``@bookmarks`` node and then Alt-X `bookmarks-show`, which should create a new empty pane above the body pane.  Select the ``aardvarks`` node and click in the new empty pane, repeat
for the ``bats`` node.

Squish the new empty pane up so it's just high enough to hold the two bookmarks, or "tabs", and
then right click a pane divider and save this layout as "Tabs" or whatever you want to call it.

So now you have two tabs which jump between two nodes.  Click the ``aardvarks`` tab, then
select the ``apples`` node.  Now shift-click the ``aardvarks`` tab.  Now you are entering sub tabs of the ``aardvarks`` tab.  You might want to repeat the ``aardvarks`` tab at this level, just select the node and click in the empty space in the bookmarks pane to repeat it here.  You could add ``autos`` at this level too.

How the 'tabs' are displayed (one or more levels at once etc.) and how you edit them are described in the earlier parts of these docs.  For example at the top level the first time you click the ``aardvarks`` tab it just shows you the ``aardvarks`` node, it requires a second click to see its subtabs (aardvarks, apples, and autos), because the top level ``aardvarks`` tab is both a bookmark and an organizer node.  If you want it to be just and organizer node, alt-click it to edit the bookmark node itself, and delete the body text (UNL) there.

'''
#@-<< docstring >>
# Written by Terry Brown.
#@+<< imports >>
#@+node:tbrown.20070322113635.3: ** << imports >>
from collections import namedtuple
import leo.core.leoGlobals as g

# Fail gracefully if the gui is not qt.
g.assertUi('qt')

from leo.core.leoQt import QtCore, QtWidgets

import hashlib
#@-<< imports >>
#@+others
#@+node:ekr.20100128073941.5371: ** init
def init():
    '''Return True if the plugin has loaded successfully.'''
    ok = not g.unitTesting
    if ok:
        g.registerHandler('after-create-leo-frame', onCreate)
        # temporary until double-click is bindable in user settings
        if g.app.config.getBool('bookmarks-grab-dblclick'):
            g.registerHandler('headdclick1', lambda t,k: cmd_open_bookmark(k['c']))
        g.plugin_signon(__name__)
    return ok
#@+node:tbrown.20110712121053.19751: ** onCreate
def onCreate(tag, keys):
    
    c = keys.get('c')
    
    BookMarkDisplayProvider(c)
#@+node:tbrown.20120319161800.21489: ** bookmarks-open-*
def cmd_open_bookmark(c):

    if not c: return
    p = c.p
    bookmark = False
    for nd in p.parents():
        if '@bookmarks' in nd.h:
            bookmark = True
            break
    if bookmark:
        if hasattr(c, '_bookmarks'):
            c._bookmarks.current = p.v
        cmd_open_node(c)
           
def cmd_open_node(c):
    
    if not c: return
    p = c.p
    url = g.getUrlFromNode(p)
    if url:
        # No need to handle url hooks here.
        g.handleUrl(url,c=c,p=p)
#@+node:tbrown.20110712100955.39215: ** bookmarks-show
def cmd_show(c):
    
    bmd = BookMarkDisplay(c)
    # Careful: we could be unit testing.
    splitter = bmd.c.free_layout.get_top_splitter()
    if splitter:
        splitter.add_adjacent(bmd.w, 'bodyFrame', 'above')
#@+node:tbrown.20131226095537.26309: ** bookmarks-switch
def cmd_switch(c):
    """switch between bookmarks and previous position in outline"""
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
def cmd_bookmark(c, child=False):
    """bookmark current node"""
    if not hasattr(c, '_bookmarks'):
        g.es("Bookmarks not active for this outline")
        return
    bm = c._bookmarks
    if bm.current is None:  # first use
        bm.current = bm.v
    if bm.current == bm.v:  # first use or other conditions
        container = bm.v
    else:
        if child:
            container = bm.current
        else:
            container = bm.current.parents[0]
    
    bc = container.context
    bp = bc.vnode2position(container)
    nd = bp.insertAsNthChild(0)
    nd.h = (
        c.frame.body.hasSelection() and  
        c.frame.body.getSelectedText() or
        bm.fix_text(c.p.h)
    )
    nd.b = bm.get_unl()
    
    bm.current = nd.v
    bm.show_list(bm.get_list())

def cmd_bookmark_child(c):
    """bookmark current node as child of current bookmark"""
    cmd_bookmark(c, child=True)
#@+node:tbrown.20140101093550.25176: ** bookmarks-level-*
def cmd_level_increase(c, delta=1):
    """increase levels, number of rows shown, for bookmarks"""
    if not hasattr(c, '_bookmarks'):
        g.es("Bookmarks not active for this outline")
        return
    bm = c._bookmarks
    if bm.levels + delta >= 0:
        bm.levels += delta
    g.es("Showing %d levels" % bm.levels)
    bm.show_list(bm.get_list())
    
def cmd_level_decrease(c):
    """decrease levels, number of rows shown, for bookmarks"""
    cmd_level_increase(c, delta=-1)
#@+node:tbrown.20131214112218.36871: ** bookmarks-mark
def cmd_mark_as_target(c):
    """Mark current node as Bookmarks list for use by another file,
    bookmarks-use-other-outline should be used after this command
    """
    g._bookmarks_target = c.p.get_UNL()
    g._bookmarks_target_v = c.p.v
    g.es("Node noted - now use\nbookmarks-use-other-outline\nin the "
        "outline you want to\nstore bookmarks in this node")

def cmd_use_other_outline(c):
    """Set bookmarks for this outline from a list (node) in
    a different outline
    """
    if not hasattr(g, '_bookmarks_target') or not g._bookmarks_target:
        g.es("Use bookmarks-mark-as-target first")
        return
    c.db['_leo_bookmarks_show'] = g._bookmarks_target
    
    bmd = BookMarkDisplay(c, g._bookmarks_target_v)
    
    splitter = c.free_layout.get_top_splitter()
    if splitter:
        splitter.add_adjacent(bmd.w, 'bodyFrame', 'above')
#@+node:ekr.20140917180536.17896: ** class FlowLayout
class FlowLayout(QtWidgets.QLayout):
    """from http://ftp.ics.uci.edu/pub/centos0/ics-custom-build/BUILD/PyQt-x11-gpl-4.7.2/examples/layouts/flowlayout.py"""
    #@+others
    #@+node:ekr.20140917180536.17897: *3* __init__
    def __init__(self, parent=None, margin=0, spacing=-1):
        '''Ctor for FlowLayout class.'''
        super(FlowLayout, self).__init__(parent)
        if parent is not None:
            self.setMargin(margin)
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
        # item.setParent(x)
        # self.itemList.insert(index, x)
    #@+node:ekr.20140917180536.17901: *3* count
    def count(self):
        return len(self.itemList)
    #@+node:ekr.20140917180536.17902: *3* itemAt
    def itemAt(self, index):
        if index >= 0 and index < len(self.itemList):
            return self.itemList[index]
        return None
    #@+node:ekr.20140917180536.17903: *3* takeAt
    def takeAt(self, index):
        if index >= 0 and index < len(self.itemList):
            return self.itemList.pop(index)
        return None
    #@+node:ekr.20140917180536.17904: *3* expandingDirections
    def expandingDirections(self):
        return QtCore.Qt.Orientations(QtCore.Qt.Orientation(0))
    #@+node:ekr.20140917180536.17905: *3* hasHeightForWidth
    def hasHeightForWidth(self):
        return True
    #@+node:ekr.20140917180536.17906: *3* heightForWidth
    def heightForWidth(self, width):
        height = self.doLayout(QtCore.QRect(0, 0, width, 0), True)
        return height
    #@+node:ekr.20140917180536.17907: *3* setGeometry
    def setGeometry(self, rect):
        super(FlowLayout, self).setGeometry(rect)
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
            spaceX = self.spacing() + wid.style().layoutSpacing(QtWidgets.QSizePolicy.PushButton, QtWidgets.QSizePolicy.PushButton, QtCore.Qt.Horizontal)
            spaceY = self.spacing() + wid.style().layoutSpacing(QtWidgets.QSizePolicy.PushButton, QtWidgets.QSizePolicy.PushButton, QtCore.Qt.Vertical)
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
    #@-others
#@+node:tbrown.20110712100955.18924: ** class BookMarkDisplay
class BookMarkDisplay:
    """Manage a pane showing bookmarks"""
    
    Bookmark = namedtuple('Bookmark', 'head url ancestors siblings children v')
    
    #@+others
    #@+node:tbrown.20110712100955.18926: *3* __init__
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
        
        self.already = -1  # used to indicate existing link when same link added again
        
        self.w = QtWidgets.QWidget()
        
        self.dark = c.config.getBool("color_theme_is_dark")
        
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
        self.w.layout().setContentsMargins(0,0,0,0)

        self.current_list = self.get_list()
        
        self.show_list(self.current_list)
        
        g.registerHandler('select1', self.update)
    #@+node:tbrown.20131227100801.30379: *3* background_clicked
    def background_clicked(self, event, bookmarks):
        """background_clicked - Handle a background click in a bookmark pane

        :Parameters:
        - `event`: click event
        - `bookmarks`: bookmarks in this pane
        """
        
        if bookmarks:
            v = bookmarks[0].v.parents[0]  # node containing bookmarks
        else:
            v = self.v  # top of bookmarks tree
        
        # Alt => edit bookmarks in the outline
        mods = event.modifiers()
        if mods == QtCore.Qt.AltModifier:
            self.edit_bookmark(None, v=v)
            return
        
        c = v.context
        p = c.vnode2position(v)
        nd = p.insertAsNthChild(0)
        new_url = self.get_unl()
        nd.b = new_url
        nd.h = (
            self.c.frame.body.hasSelection() and  
            self.c.frame.body.getSelectedText() or
            self.fix_text(self.c.p.h)
        )
        c.redraw()
        self.current = nd.v
        self.show_list(self.get_list())
    #@+node:tbrown.20131227100801.23859: *3* button_clicked
    def button_clicked(self, event, bm, but, up=False):
        """button_clicked - handle a button being clicked

        :Parameters:
        - `event`: QPushButton event
        - `bm`: Bookmark associated with button
        - `but`: button widget
        """
        
        if event.button() == QtCore.Qt.RightButton:
            return self.button_menu(event, bm, but, up=up)
        
        mods = event.modifiers()
        
        # Alt-Ctrl => update bookmark to point to current node
        if mods == (QtCore.Qt.AltModifier | QtCore.Qt.ControlModifier):
            self.update_bookmark(bm)
            return
        # Shift-Ctrl => rename bookmark
        if mods == (QtCore.Qt.ShiftModifier | QtCore.Qt.ControlModifier):
            self.rename_bookmark(bm)
            return
        # Alt => edit the bookmark in the outline
        if mods == QtCore.Qt.AltModifier:
            self.edit_bookmark(bm)
            return
        # Ctrl => delete the bookmark
        if mods == QtCore.Qt.ControlModifier:
            self.delete_bookmark(bm)
            return
        # Shift => add child bookmark
        if mods == QtCore.Qt.ShiftModifier:
            self.add_child_bookmark(bm)
            return
            
        # Alt-Shift => navigate in bookmarks without changing nodes
        no_move = mods == (QtCore.Qt.AltModifier | QtCore.Qt.ShiftModifier)
            
        # otherwise, look up the bookmark
        self.upwards = up
        self.second = not up and self.current == bm.v   
        self.current = bm.v        
        # in case something we didn't see changed the bookmarks
        self.show_list(self.get_list(), up=up)
        if bm.url and not up and not no_move:
            g.handleUrl(bm.url, c=self.c)
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
            ("Link bookmark to this node", self.update_bookmark),
            ("Re-name bookmark", self.rename_bookmark),
            ("Edit bookmark in tree", self.edit_bookmark),
            ("Delete bookmark", self.delete_bookmark),
            ("Add this node as child bookmark", self.add_child_bookmark),
        ]
        for action in actions:
            act = QtWidgets.QAction(action[0], menu)
            act.triggered.connect(lambda checked, bm=bm, f=action[1]: f(bm))
            menu.addAction(act)
        
        def follow(checked, bm=bm, manager=self):
            manager.current = bm.v
            manager.second = True
            manager.upwards = False
            manager.show_list(manager.get_list(), up=False)
        act = QtWidgets.QAction("Show child bookmarks", menu)
        act.triggered.connect(follow)
        menu.addAction(act)
       
        menu.exec_(but.mapToGlobal(event.pos()))
    #@+node:tbrown.20110712100955.18925: *3* color
    def color(self, text, dark=False):
        """make a consistent light background color for text"""
        
        if g.isPython3:
            text = g.toEncodedString(text,'utf-8')
        x = hashlib.md5(text).hexdigest()[-6:]
        add = int('bb',16) if not dark else int('33',16)
        x = tuple([int(x[2*i:2*i+2], 16)//4+add for i in range(3)])
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
                break
        else:
            return None
        return node
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
    def get_list(self):
        """Return list of Bookmarks
        """
        
        # v might not be in this outline
        p = self.v.context.vnode2position(self.v)
        if not p:
            return
        
        def strip(s):
            if s.startswith('@url'):
                s = s[4:]
            return s.strip()

        result = []

        def recurse_bm(node, result, ancestors=[]):
        
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
                
                children = []
                bm = self.Bookmark(
                    h, url, ancestors, result, children, p.v)
                
                result.append(bm)
                
                if self.levels == 0:  # non-hierarchical
                    recurse_bm(p, result)
                else:
                    recurse_bm(p, children, ancestors=ancestors+[bm])

        recurse_bm(p, result)

        return result
    #@+node:tbrown.20140103082018.24102: *3* get_unl
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
            return "#"+p.get_UNL(with_file=False, with_proto=False)
        else:
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
        
        while todo:
            
            links = todo.pop(0)
        
            top = QtWidgets.QWidget()
            # pylint: disable=E0202
            # pylint bug, fix released: http://www.logilab.org/ticket/89092
            top.mouseReleaseEvent = (lambda event, links=links:
                self.background_clicked(event, links))
            top.setMinimumSize(10,10)  # so there's something to click when empty

            size_policy = QtWidgets.QSizePolicy(\
                QtWidgets.QSizePolicy.Expanding,      
                QtWidgets.QSizePolicy.Expanding
            )
            size_policy.setHorizontalStretch(1)
            size_policy.setVerticalStretch(1)
            top.setSizePolicy(size_policy)

            w.layout().addWidget(top)
        
            layout = FlowLayout()
            layout.setSpacing(5)
            top.setLayout(layout)
            for bm in links:
                
                but = QtWidgets.QPushButton(bm.head)

                if bm.url:
                    but.setToolTip(bm.url)
                but.mouseReleaseEvent = (lambda event, bm=bm, but=but: 
                    self.button_clicked(event, bm, but))
                layout.addWidget(but)
                
                showing = False
                if bm.children and self.current:
                    nd = self.current
                    while nd != bm.v and nd.parents:
                        nd = nd.parents[0]
                    if nd == bm.v:
                        showing = True
                        todo.append(bm.children)
                        
                style_sheet = ("background: #%s;" % 
                    self.color(bm.head, dark=self.dark))
                but.setStyleSheet(style_sheet)
            
                classes = []
                if bm.v == self.current:
                    classes += ['bookmark_current']
                    current_level = self.w.layout().count()
                    current_url = bm.url
                if showing:
                    classes += ['bookmark_expanded']
                    showing_chain += [bm]
                if bm.children:
                    classes += ['bookmark_children']
                but.setProperty('style_class', ' '.join(classes))
        
        if self.levels:  # drop excess levels
            if ((   
                    not self.second and 
                    current_url and
                    current_url.strip() and
                    self.levels == 1 
                 or
                    up or self.upwards
                ) and 
                  current_level < self.w.layout().count() and
                  self.levels < self.w.layout().count()
                ):
                # hide last line, of children, if none are current
                self.w.layout().takeAt(self.w.layout().count()-1).widget().deleteLater()
                
            while self.w.layout().count() > self.levels:
                
                # add an up button to the second row...
                next_row = self.w.layout().itemAt(1).widget().layout()
                but = QtWidgets.QPushButton('^')
                bm = showing_chain.pop(0)
                but.mouseReleaseEvent = (lambda event, bm=bm, but=but: 
                    self.button_clicked(event, bm, but, up=True))
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
            return

        self.show_list(self.get_list())
        
        return None  # do not stop processing the select1 hook
    #@+node:tbrown.20130222093439.30271: *3* delete_bookmark
    def delete_bookmark(self, bm):
        
        c = bm.v.context
        p = c.vnode2position(bm.v)
        u = c.undoer
        if p.hasVisBack(c): newNode = p.visBack(c)
        else: newNode = p.next()
        dirtyVnodeList = p.setAllAncestorAtFileNodesDirty()
        
        undoData = u.beforeDeleteNode(p)
        p.doDelete(newNode)
        c.setChanged(True)
        u.afterDeleteNode(newNode, "Bookmark deletion", undoData, 
            dirtyVnodeList=dirtyVnodeList)
        c.redraw()

        self.show_list(self.get_list())
    #@+node:tbrown.20140804215436.30052: *3* rename_bookmark
    def rename_bookmark(self, bm):
        """Rename bookmark"""

        txt = g.app.gui.runAskOkCancelStringDialog(
            self.c,
            "Rename "+bm.head,
            "New name for "+bm.head,
            default=bm.head
        )
        
        if txt:
            bm.v.h = txt
            bm.v.context.redraw()
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
        bm.v.context.setChanged(True)
        bm.v.context.redraw()
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
    #@+node:tbrown.20131227100801.40521: *3* add_child_bookmark
    def add_child_bookmark(self, bm):
        """add_child_bookmark - Add a child bookmark

        :Parameters:
        - `bm`: bookmark to which to add a child
        """

        c = bm.v.context
        p = c.vnode2position(bm.v)
        new_url = self.get_unl()
        nd = p.insertAsNthChild(0)
        nd.b = new_url
        nd.h = (
            self.c.frame.body.hasSelection() and  
            self.c.frame.body.getSelectedText() or
            self.fix_text(self.c.p.h)
        )    
        
        c.redraw()
        self.current = nd.v
        self.show_list(self.get_list())
    #@-others
#@+node:tbrown.20110712121053.19746: ** class BookMarkDisplayProvider
class BookMarkDisplayProvider:
    #@+others
    #@+node:tbrown.20110712121053.19747: *3* __init__
    def __init__(self, c):
        self.c = c
        
        # if hasattr(c, 'free_layout') and hasattr(c.free_layout, 'get_top_splitter'):
            # Second hasattr temporary until free_layout merges with trunk
            
        splitter = c.free_layout.get_top_splitter()
        # Careful: we could be unit testing.
        if splitter:
            splitter.register_provider(self)
    #@+node:tbrown.20110712121053.19748: *3* ns_provides
    def ns_provides(self):
        return[('Bookmarks', '_leo_bookmarks_show')]
    #@+node:tbrown.20110712121053.19749: *3* ns_provide
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
                        if hasattr(g.app.gui,'frameFactory'):
                            factory = g.app.gui.frameFactory
                            if factory and hasattr(factory,'setTabForCommander'):
                                factory.setTabForCommander(c)

                        g.es("NOTE: bookmarks for this outline\nare in a different outline:\n  '%s'"%file_)
                    
                    ok, depth, other_p = g.recursiveUNLFind(UNL.split('-->'), other_c)
                    if ok:
                        v = other_p.v
                    else:
                        g.es("Couldn't find '%s'"%gnx)
                    
            if v is None:
                v = c.p.v

            bmd = BookMarkDisplay(self.c, v=v)
            return bmd.w
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo

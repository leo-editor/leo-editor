#@+leo-ver=5-thin
#@+node:peckj.20140804114520.9427: * @file ../plugins/nodetags.py
#@+<< nodetags docstring >>
#@+node:peckj.20140804103733.9242: ** << nodetags docstring >>
"""Provides node tagging capabilities to Leo

By Jacob M. Peck

API
===

This plugin registers a controller object to c.theTagController, which provides
the following API::

    tc = c.theTagController
    tc.get_all_tags()
        return a list of all tags used in the current outline,
        automatically updated to be consistent
    tc.get_tagged_nodes('foo')
        return a list of positions tagged 'foo'
    tc.get_tags(p)
        return a list of tags applied to the node at position p.
        returns [] if node has no tags
    tc.add_tag(p, 'bar')
        add the tag 'bar' to the node at position p
    tc.remove_tag(p, 'baz')
        remove the tag 'baz' from p if it is in the tag list

Internally, tags are stored in `p.v.unknownAttributes['__node_tags']` as a set.

UI
==

The "Tags" tab in the Log pane is the UI for this plugin. The bar at the top is
a search bar, editable to allow complex search queries. It is pre-populated with
all existing tags in the outline, and remembers your custom searches within the
given session. It also acts double duty as an input box for the add (+) button,
which adds the contents of the search bar as a tag to the currently selected
node.

To add a new tag, type its name in the search bar, then click the "+" button.

The list box in the middle is a list of headlines of nodes which contain the
tag(s) defined by the current search string. These are clickable, and doing so
will center the focus in the outline pane on the selected node.

Below the list box is a dynamic display of tags on the currently selected node.
Left-clicking on any of these will populate the search bar with that tag,
allowing you to explore similarly tagged nodes. Right-clicking on a tag will
remove it from the currently selected node.

The status line at the bottom is purely informational.

The tag browser has set-algebra querying possible. Users may search for strings
like 'foo&bar', to get nodes with both tags foo and bar, or 'foo|bar' to get
nodes with either or both. Set difference (-) and symmetric set difference (^)
are supported as well. These queries are left-associative, meaning they are read
from left to right, with no other precedence. Parentheses are not supported.
Additionally, regular expression support is included, and tag hierarchies can be
implemented with wildcards. See below for more details.

Searching
---------

Searching on tags in the UI is based on set algebra. The following syntax is
used::

    <tag>&<tag> - return nodes tagged with both the given tags
    <tag>|<tag> - return nodes tagged with either of the given tags (or both)
    <tag>-<tag> - return nodes tagged with the first tag, but not the second tag
    <tag>^<tag> - return nodes tagged with either of the given tags (but *not* both)

These may be combined, and are applied left-associatively, building the set from
the left, such that the query `foo&bar^baz` will return only nodes tagged both
'foo' and 'bar', or nodes tagged with 'baz', but *not* tagged with all three.

Additionally, the search string may be any valid regular expression, meaning you
can search using wildcards (*), and using this, you can create tag hierarchies,
for example 'work/priority' and 'work/long-term'. Searching for `work/*` would
return all nodes tagged with either 'work/priority' or 'work/long-term'.

Please note that this plugin automatically replaces '*' with '.*' in your search
string to produce python-friendly regular expressions. This means nothing to the
end-user, except that '*' can be used as a wildcard freely, as one expects.

Tag Limitations
---------------

The API is unlimited in tagging abilities. If you do not wish to use the UI,
then the API may be used to tag nodes with any arbitrary strings. The UI,
however, due to searching capabilities, may *not* be used to tag (or search for)
nodes with tags containing the special search characters, `&|-^`. The UI also
cannot search for tags of zero-length, and it automatically removes surrounding
whitespace (calling .strip()).
"""
#@-<< nodetags docstring >>
#@+<< nodetags imports & annotations >>
#@+node:ekr.20220828131647.1: ** << nodetags imports & annotations >>
from __future__ import annotations
from collections.abc import Callable
import re
from typing import Any, Generator, TYPE_CHECKING
from leo.core import leoGlobals as g
from leo.core import leoNodes
try:
    from leo.core.leoQt import QtCore, QtWidgets
    from leo.core.leoQt import MouseButton
except Exception:
    QtCore = QtWidgets = None

if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoGui import LeoKeyEvent as Event
    from leo.core.leoNodes import Position, VNode
    QWidget = QtWidgets.QWidget
#@-<< nodetags imports & annotations >>

#@+others
#@+node:peckj.20140804103733.9244: ** init (nodetags.py)
def init() -> bool:
    """Return True if the plugin has loaded successfully."""
    # 2031: Allow this plugin to run without Qt.
    g.registerHandler('after-create-leo-frame', onCreate)
    g.plugin_signon(__name__)
    return True
#@+node:peckj.20140804103733.9245: ** onCreate (nodetags.py)
def onCreate(tag: str, keys: Any) -> None:

    c = keys.get('c')
    if c:
        c.theTagController = TagController(c)
#@+node:ekr.20201030095215.1: ** show-all-tags
@g.command('show-all-tags')
def show_all_tags(event: Event) -> None:
    """Show all tags, organized by node."""
    c = event.get('c')
    if not c:
        return
    tc = c.theTagController
    if tc:
        tc.show_all_tags()
    else:
        print('nodetags plugin not enabled')
#@+node:peckj.20140804103733.9246: ** class TagController
class TagController:

    TAG_LIST_KEY = '__node_tags'

    #@+others
    #@+node:peckj.20140804103733.9262: *3* tag_c.__init__
    def __init__(self, c: Cmdr) -> None:

        self.c = c
        self.taglist: list[str] = []
        self.initialize_taglist()
        c.theTagController = self
        # #2031: Init the widgets only if we are using Qt.
        if g.app.gui.guiName().startswith('qt'):
            self.ui = LeoTagWidget(c)
            c.frame.log.createTab('Tags', widget=self.ui)
            self.ui.update_all()
    #@+node:peckj.20140804103733.9263: *3* tag_c.initialize_taglist
    def initialize_taglist(self) -> None:
        taglist = []
        for p in self.c.all_unique_positions():
            for tag in self.get_tags(p):
                if tag not in taglist:
                    taglist.append(tag)
        self.taglist = taglist

    #@+node:peckj.20140804103733.9264: *3* tag_c.outline-level
    #@+node:peckj.20140804103733.9268: *4* tag_c.get_all_tags
    def get_all_tags(self) -> list[str]:
        """ return a list of all tags in the outline """
        return self.taglist
    #@+node:ekr.20201030095446.1: *4* tag_c.show_all_tags
    def show_all_tags(self) -> None:
        """Show all tags, organized by node."""
        c, tc = self.c, self
        aList: list[str]
        d: dict[str, list[str]] = {}
        for p in c.all_unique_positions():
            u = p.v.u
            tags = set(u.get(tc.TAG_LIST_KEY, set([])))
            for tag in tags:
                aList = d.get(tag, [])
                aList.append(p.h)
                d[tag] = aList
        # Print all tags.
        if d:
            for key in sorted(d):
                aList = d.get(key)
                for h in sorted(aList):
                    print(f"{key:>8} {h}")
        else:
            if not g.unitTesting:
                print(f"no tags in {c.shortFileName()}")

    #@+node:peckj.20140804103733.9267: *4* tag_c.update_taglist
    def update_taglist(self, tag: str) -> None:
        """ ensures the outline's taglist is consistent with the state of the nodes in the outline """
        if tag not in self.taglist:
            self.taglist.append(tag)
        nodelist = self.get_tagged_nodes(tag)
        if not nodelist:
            self.taglist.remove(tag)
        if hasattr(self, 'ui'):
            self.ui.update_all()
    #@+node:peckj.20140804103733.9258: *4* tag_c.get_tagged_nodes
    def get_tagged_nodes(self, tag: str) -> list[Position]:
        """ return a list of *positions* of nodes containing the tag, with * as a wildcard """
        nodelist: list[Position] = []
        # replace * with .* for regex compatibility
        tag = tag.replace('*', '.*')
        regex = re.compile(tag)
        for p in self.c.all_unique_positions():
            for tag in self.get_tags(p):
                if regex.match(tag):
                    nodelist.append(p.copy())
                    break
        return nodelist
    #@+node:vitalije.20170811150914.1: *4* tag_c.get_tagged_gnxes
    def get_tagged_gnxes(self, tag: str) -> Generator:
        c = self.c
        tag = tag.replace('*', '.*')
        regex = re.compile(tag)
        for p in c.all_unique_positions():
            for t in self.get_tags(p):
                if regex.match(t):
                    yield p.v.gnx
    #@+node:peckj.20140804103733.9265: *3* tag_c.individual nodes
    #@+node:peckj.20140804103733.9259: *4* tag_c.get_tags
    def get_tags(self, p: Position) -> list[str]:
        """ returns a list of tags applied to position p."""
        if p:
            tags = p.v.u.get(self.TAG_LIST_KEY, set([]))
            return list(tags)
        return []
    #@+node:peckj.20140804103733.9260: *4* tag_c.add_tag
    def add_tag(self, p: Position, tag: str) -> None:
        """ adds 'tag' to the taglist of v """
        # cast to set() incase JSON storage (leo_cloud plugin) converted to list
        tags = set(p.v.u.get(self.TAG_LIST_KEY, set([])))
        tags.add(tag)
        p.v.u[self.TAG_LIST_KEY] = tags
        self.c.setChanged()
        self.update_taglist(tag)
    #@+node:peckj.20140804103733.9261: *4* tag_c.remove_tag
    def remove_tag(self, p: Position, tag: str) -> None:
        """ removes 'tag' from the taglist of position p. """
        v = p.v
        # In case JSON storage (leo_cloud plugin) converted to list.
        tags = set(v.u.get(self.TAG_LIST_KEY, set([])))
        if tag in tags:
            tags.remove(tag)
        if tags:
            v.u[self.TAG_LIST_KEY] = tags
        else:
            # prevent a few corner cases, and conserve disk space
            del v.u[self.TAG_LIST_KEY]
        self.c.setChanged()
        self.update_taglist(tag)
    #@-others
#@+node:peckj.20140804114520.15199: ** class LeoTagWidget
if QtWidgets:

    class LeoTagWidget(QtWidgets.QWidget):  # type:ignore
        #@+others
        #@+node:peckj.20140804114520.15200: *3* tag_w.__init__
        def __init__(self, c: Cmdr, parent: QWidget = None) -> None:
            super().__init__(parent)
            self.c = c
            self.tc = self.c.theTagController
            self.initUI()
            self.registerCallbacks()
            self.mapping: dict[int, VNode] = {}
            self.search_re = r'(&|\||-|\^)'
            self.custom_searches: list[str] = []
            g.registerHandler('select2', self.select2_hook)
            # fix tag jumplist positions after new node insertion
            g.registerHandler('create-node', self.command2_hook)
            g.registerHandler('command2', self.command2_hook)
        #@+node:peckj.20140804114520.15202: *4* tag_w.initUI
        def initUI(self) -> None:
            """create GUI components."""
            self.setObjectName("LeoTagWidget")
            #
            # verticalLayout_2: contains
            # verticalLayout
            self.verticalLayout_2 = QtWidgets.QVBoxLayout(self)
            self.verticalLayout_2.setContentsMargins(0, 1, 0, 1)
            self.verticalLayout_2.setObjectName("nodetags-verticalLayout_2")
            #
            # horizontalLayout: contains:
            #   "Refresh" button
            #   comboBox
            self.horizontalLayout = QtWidgets.QHBoxLayout()
            self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
            self.horizontalLayout.setObjectName("nodetags-horizontalLayout")
            #
            # horizontalLayout2: contains:
            #   label2
            #   not much by default -- it's a place to add buttons for current tags
            self.horizontalLayout2 = QtWidgets.QHBoxLayout()
            self.horizontalLayout2.setContentsMargins(0, 0, 0, 0)
            self.horizontalLayout2.setObjectName("nodetags-horizontalLayout2")
            label2 = QtWidgets.QLabel(self)
            label2.setObjectName("nodetags-label2")
            label2.setText("Tags for current node (right click to clear):")
            self.horizontalLayout2.addWidget(label2)
            #
            # verticalLayout: contains
            #   horizontalLayout
            #   listWidget
            #   horizontalLayout2
            #   label
            self.verticalLayout = QtWidgets.QVBoxLayout()
            self.verticalLayout.setObjectName("nodetags-verticalLayout")
            #
            self.comboBox = QtWidgets.QComboBox(self)
            self.comboBox.setObjectName("nodetags-comboBox")
            self.comboBox.setEditable(True)
            self.horizontalLayout.addWidget(self.comboBox)
            #
            # The "+" button
            self.pushButton = QtWidgets.QPushButton("+", self)
            self.pushButton.setObjectName("nodetags-pushButton")
            self.pushButton.setMinimumSize(24, 24)
            self.pushButton.setMaximumSize(24, 24)
            #
            self.horizontalLayout.addWidget(self.pushButton)
            self.verticalLayout.addLayout(self.horizontalLayout)
            #
            self.listWidget = QtWidgets.QListWidget(self)
            self.listWidget.setObjectName("nodetags-listWidget")
            self.verticalLayout.addWidget(self.listWidget)
            self.verticalLayout.addLayout(self.horizontalLayout2)
            #
            # The status area.
            self.label = QtWidgets.QLabel(self)
            self.label.setObjectName("nodetags-label")
            self.label.setText("Total: 0 items")
            self.verticalLayout.addWidget(self.label)
            self.verticalLayout_2.addLayout(self.verticalLayout)
            QtCore.QMetaObject.connectSlotsByName(self)
        #@+node:peckj.20140804114520.15203: *4* tag_w.registerCallbacks
        def registerCallbacks(self) -> None:
            """Connect events to widgets."""
            self.listWidget.itemSelectionChanged.connect(self.item_selected)
            self.listWidget.itemClicked.connect(self.item_selected)
            self.comboBox.currentIndexChanged.connect(self.update_list)
            self.pushButton.clicked.connect(self.add_tag)
        #@+node:peckj.20140804114520.15204: *3* tag_w:updates + interaction
        #@+node:peckj.20140804114520.15205: *4* tag_w.item_selected
        def item_selected(self) -> None:
            c = self.c
            key = id(self.listWidget.currentItem())
            v = self.mapping[key]
            if isinstance(v, leoNodes.VNode):
                p = c.vnode2position(v)
            assert isinstance(p, leoNodes.Position), repr(p)
            self.update_current_tags(p)
            c.selectPosition(p)
            c.redraw()
        #@+node:peckj.20140804192343.6568: *5* tag_w.update_current_tags
        def update_current_tags(self, p: Position) -> None:
            #
            # Clear horizontalLayout2
            layout = self.horizontalLayout2
            while layout.count():
                child = layout.takeAt(0)
                child.widget().deleteLater()
            label = QtWidgets.QLabel(self)
            label.setObjectName("nodetags-label2")
            label.setText('Tags for current node (right click to clear):')
            layout.addWidget(label)
            #
            # add tags
            tags = self.tc.get_tags(p)
            for tag in tags:
                label = QtWidgets.QLabel(self)
                label.setText(tag)
                label.setObjectName('nodetags-label3')
                layout.addWidget(label)
                label.mouseReleaseEvent = self.callback_factory(tag)  # type:ignore
        #@+node:peckj.20140804194839.6569: *6* tag_w.callback_factory
        def callback_factory(self, tag: str) -> Callable:
            c = self.c

            def callback(event: Event) -> None:
                p = c.p
                tc = c.theTagController
                ui = tc.ui
                # Right click on a tag to remove it from the node
                if event.button() == MouseButton.RightButton:
                    tc.remove_tag(p, tag)
                # Other clicks make the jumplist open that tag for browsing
                else:
                    idx = ui.comboBox.findText(tag)
                    ui.comboBox.setCurrentIndex(idx)
                ui.update_all()

            return callback
        #@+node:peckj.20140804114520.15206: *4* tag_w.update_combobox
        def update_combobox(self) -> None:
            self.comboBox.clear()
            tags = self.tc.get_all_tags()
            self.comboBox.addItems(tags)
            self.comboBox.addItems(self.custom_searches)

        #@+node:peckj.20140804114520.15207: *4* tag_w.update_list
        def update_list(self) -> None:
            c = self.c
            gnxDict = c.fileCommands.gnxDict
            key = str(self.comboBox.currentText()).strip()
            current_tags = self.tc.get_all_tags()
            if key not in current_tags and key not in self.custom_searches:
                if len(re.split(self.search_re, key)) > 1:
                    self.custom_searches.append(key)

            query = re.split(self.search_re, key)
            tags = []
            operations = []
            for i, s in enumerate(query):
                if i % 2 == 0:
                    tags.append(s.strip())
                else:
                    operations.append(s.strip())
            tags.reverse()
            operations.reverse()

            resultset = set(self.tc.get_tagged_gnxes(tags.pop()))
            while operations:
                op = operations.pop()
                nodes = set(self.tc.get_tagged_gnxes(tags.pop()))
                if op == '&':
                    resultset &= nodes
                elif op == '|':
                    resultset |= nodes
                elif op == '-':
                    resultset -= nodes
                elif op == '^':
                    resultset ^= nodes

            self.listWidget.clear()
            self.mapping = {}
            for gnx in resultset:
                n = gnxDict.get(gnx)
                if n is not None:
                    item = QtWidgets.QListWidgetItem(n.h)
                    self.listWidget.addItem(item)
                    self.mapping[id(item)] = n
            count = self.listWidget.count()
            self.label.clear()
            self.label.setText("Total: %s nodes" % count)
        #@+node:peckj.20140804114520.15208: *4* tag_w.update_all
        def update_all(self) -> None:
            """ updates the tag GUI """
            key = str(self.comboBox.currentText())
            self.update_combobox()
            if key:
                idx = self.comboBox.findText(key)
                if idx == -1:
                    idx = 0
            else:
                idx = 0
            self.comboBox.setCurrentIndex(idx)
            self.update_list()
            self.update_current_tags(self.c.p)
        #@+node:peckj.20140806145948.6579: *4* tag_w.add_tag
        def add_tag(self, event: Event = None) -> None:
            p = self.c.p
            tag = str(self.comboBox.currentText()).strip()
            if not tag:
                return  # no error message, probably an honest mistake
            if len(re.split(self.search_re, tag)) > 1:
                g.es('Cannot add tags containing any of these characters: &|^-', color='red')
                return  # don't add unsearchable tags
            self.tc.add_tag(p, tag)
        #@+node:peckj.20140811082039.6623: *3* tag_w:event hooks
        #@+node:peckj.20140804195456.13487: *4* tag_w.select2_hook
        def select2_hook(self, tag: str, keywords: Any) -> None:
            self.update_current_tags(self.c.p)
        #@+node:peckj.20140806101020.14006: *4* tag_w.command2_hook
        def command2_hook(self, tag: str, keywords: Any) -> None:
            paste_cmds = [
                'paste-node',
                # strange that this one isn't canonicalized
                'pasteOutlineRetainingClones',
                'paste-retaining-clones',
            ]
            if keywords.get('label') in paste_cmds:
                self.tc.initialize_taglist()
                self.update_all()
        #@+node:tbnorth.20170313095036.1: *5* tag_w.sf.find_setting
        #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo

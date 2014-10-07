#@+leo-ver=5-thin
#@+node:peckj.20140804114520.9427: * @file nodetags.py
#@+<< docstring >>
#@+node:peckj.20140804103733.9242: ** << docstring >>
'''Provides node tagging capabilities to Leo

By Jacob M. Peck

API
===

This plugin registers a controller object to c.theTagController, which provides the following API::
    
    tc = c.theTagController   
    tc.get_all_tags() # return a list of all tags used in the current outline, automatically updated to be consistent
    tc.get_tagged_nodes('foo') # return a list of positions tagged 'foo'
    tc.get_tags(p) # return a list of tags applied to the node at position p; returns [] if node has no tags
    tc.add_tag(p, 'bar') # add the tag 'bar' to the node at position p
    tc.remove_tag(p, 'baz') # remove the tag 'baz' from p if it is in the tag list

Internally, tags are stored in `p.v.unknownAttributes['__node_tags']` as a set.

UI
==

The "Tags" tab in the Log pane is the UI for this plugin.  The bar at the top is a search bar, editable to allow complex search queries.  It is pre-populated with all existing tags in the outline, and remembers your custom searches within the given session.  It also acts double duty as an input box for the add (+) button, which adds the contents of the search bar as a tag to the currently selected node.

The list box in the middle is a list of headlines of nodes which contain the tag(s) defined by the current search string.  These are clickable, and doing so will center the focus in the outline pane on the selected node.

Below the list box is a dynamic display of tags on the currently selected node.  Left-clicking on any of these will populate the search bar with that tag, allowing you to explore similarly tagged nodes.  Right-clicking on a tag will remove it from the currently selected node.

The status line at the bottom is purely informational.

The tag browser has set-algebra querying possible.  Users may search for strings like 'foo&bar', to get nodes with both tags foo and bar, or 'foo|bar' to get nodes with either or both.  Set difference (-) and symmetric set difference (^) are supported as well.  These queries are left-associative, meaning they are read from left to right, with no other precedence.  Parentheses are not supported.  See below for more details.

Searching
---------

Searching on tags in the UI is based on set algebra.  The following syntax is used::
    
    <tag>&<tag> - return nodes tagged with both the given tags
    <tag>|<tag> - return nodes tagged with either of the given tags (or both)
    <tag>-<tag> - return nodes tagged with the first tag, but not the second tag
    <tag>^<tag> - return nodes tagged with either of the given tags (but *not* both)

These may be combined, and are applied left-associatively, building the set from the left, such that the query `foo&bar^baz` will return only nodes tagged both 'foo' and 'bar', or nodes tagged with 'baz', but *not* tagged with all three.

Tag Limitations
---------------
The API is unlimited in tagging abilities.  If you do not wish to use the UI, then the API may be used to tag nodes with any arbitrary strings.  The UI, however, due to searching capabilities, may *not* be used to tag (or search for) nodes with tags containing the special search characters, `&|-^`.  The UI also cannot search for tags of zero-length, and it automatically removes surrounding whitespace (calling .strip()).
'''
#@-<< docstring >>
#@+<< imports >>
#@+node:peckj.20140804103733.9241: ** << imports >>
import leo.core.leoGlobals as g
import re
#from PyQt4 import QtGui, QtCore
from leo.core.leoQt import QtWidgets, QtCore
#@-<< imports >>
#@+others
#@+node:peckj.20140804103733.9244: ** init
def init ():
    '''Return True if the plugin has loaded successfully.'''
    if g.app.gui is None:
        g.app.createQtGui(__file__)
    ok = g.app.gui.guiName().startswith('qt')
    if ok:
        #g.registerHandler(('new','open2'),onCreate)
        g.registerHandler('after-create-leo-frame',onCreate)
        g.plugin_signon(__name__)
    else:
        g.es('Plugin %s not loaded.' % __name__, color='red')
    return ok
#@+node:peckj.20140804103733.9245: ** onCreate
def onCreate (tag, keys):
    
    c = keys.get('c')
    if not c: return
    
    theTagController = TagController(c)
    c.theTagController = theTagController

#@+node:peckj.20140804103733.9246: ** class TagController
class TagController:
    #@+others
    #@+node:peckj.20140804103733.9266: *3* initialization
    #@+node:peckj.20140804103733.9262: *4* __init__
    def __init__(self, c):
        self.TAG_LIST_KEY = '__node_tags'
        self.c = c
        self.taglist = []
        self.initialize_taglist()
        c.theTagController = self
        self.ui = LeoTagWidget(c)
        c.frame.log.createTab('Tags', widget=self.ui)
        self.ui.update_all()
    #@+node:peckj.20140804103733.9263: *5* initialize_taglist
    def initialize_taglist(self):
        taglist = []
        for v in self.c.all_unique_nodes():
            p = self.c.vnode2position(v)
            for tag in self.get_tags(p):
                if tag not in taglist:
                    taglist.append(tag)
        self.taglist = taglist
    #@+node:peckj.20140804103733.9264: *3* outline-level
    #@+node:peckj.20140804103733.9268: *4* get_all_tags
    def get_all_tags(self):
        ''' return a list of all tags in the outline '''
        return self.taglist
    #@+node:peckj.20140804103733.9267: *4* update_taglist
    def update_taglist(self, tag):
        ''' ensures the outline's taglist is consistent with the state of the nodes in the outline '''
        if tag not in self.taglist:
            self.taglist.append(tag)
        nodelist = self.get_tagged_nodes(tag)
        if len(nodelist) == 0:
            self.taglist.remove(tag)
        self.ui.update_all()
    #@+node:peckj.20140804103733.9258: *4* get_tagged_nodes
    def get_tagged_nodes(self, tag):
        ''' return a list of positions of nodes containing the tag '''
        nodelist = []
        for node in self.c.all_unique_nodes():
            p = self.c.vnode2position(node)
            if tag in self.get_tags(p):
                nodelist.append(p)
        return nodelist
    #@+node:peckj.20140804103733.9265: *3* individual nodes
    #@+node:peckj.20140804103733.9259: *4* get_tags
    def get_tags(self, p):
        ''' returns a list of tags applied to p '''
        tags = p.v.u.get(self.TAG_LIST_KEY, set([]))
        return list(tags)
    #@+node:peckj.20140804103733.9260: *4* add_tag
    def add_tag(self, p, tag):
        ''' adds 'tag' to the taglist of p '''
        tags = p.v.u.get(self.TAG_LIST_KEY, set([]))
        tags.add(tag)
        p.v.u[self.TAG_LIST_KEY] = tags
        self.c.setChanged(True)
        self.update_taglist(tag)
    #@+node:peckj.20140804103733.9261: *4* remove_tag
    def remove_tag(self, p, tag):
        ''' removes 'tag' from the taglist of p '''
        tags = p.v.u.get(self.TAG_LIST_KEY, set([]))
        if tag in tags:
            tags.remove(tag)
        if len(tags) == 0:
            del p.v.u[self.TAG_LIST_KEY] # prevent a few corner cases, and conserve disk space
        else:
            p.v.u[self.TAG_LIST_KEY] = tags
        self.c.setChanged(True)
        self.update_taglist(tag)
    #@-others
#@+node:peckj.20140804114520.15199: ** class LeoTagWidget
class LeoTagWidget(QtWidgets.QWidget):
    #@+others
    #@+node:peckj.20140804114520.15200: *3* __init__
    def __init__(self,c,parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.c = c
        self.tc = self.c.theTagController
        self.initUI()
        self.registerCallbacks()
        self.mapping = {}
        # pylint: disable=anomalous-backslash-in-string
        #self.search_chars = ['&','|','-','^']
        self.search_re = '(&|\||-|\^)'
        self.custom_searches = []
        g.registerHandler('select2', self.select2_hook)
        g.registerHandler('command2', self.command2_hook)
    #@+node:peckj.20140804114520.15202: *4* initUI
    def initUI(self):
        # create GUI components
        ## this code is atrocious... don't look too closely
        self.setObjectName("LeoTagWidget")
        
        # verticalLayout_2: contains
        # verticalLayout
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self)
        self.verticalLayout_2.setContentsMargins(0,1,0,1)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        
        # horizontalLayout: contains
        # "Refresh" button
        # comboBox
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(0,0,0,0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        
        # horizontalLayout2: contains
        # label2
        # not much by default -- it's a place to add buttons for current tags
        self.horizontalLayout2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout2.setContentsMargins(0,0,0,0)
        self.horizontalLayout2.setObjectName("horizontalLayout2")
        label2 = QtWidgets.QLabel(self)
        label2.setObjectName("label2")
        label2.setText("Tags for current node:")
        self.horizontalLayout2.addWidget(label2)
        
        # verticalLayout: contains
        # horizontalLayout
        # listWidget
        # horizontalLayout2
        # label
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        
        self.comboBox = QtWidgets.QComboBox(self)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.setEditable(True)
        self.horizontalLayout.addWidget(self.comboBox)
        
        self.pushButton = QtWidgets.QPushButton("+", self)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setMinimumSize(24,24)
        self.pushButton.setMaximumSize(24,24)
        self.horizontalLayout.addWidget(self.pushButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.listWidget = QtWidgets.QListWidget(self)
        self.listWidget.setObjectName("listWidget")
        self.verticalLayout.addWidget(self.listWidget)
        self.verticalLayout.addLayout(self.horizontalLayout2)
        self.label = QtWidgets.QLabel(self)
        self.label.setObjectName("label")
        self.label.setText("Total: 0 items")
        self.verticalLayout.addWidget(self.label)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        QtCore.QMetaObject.connectSlotsByName(self)
    #@+node:peckj.20140804114520.15203: *4* registerCallbacks
    def registerCallbacks(self):
        self.listWidget.itemSelectionChanged.connect(self.item_selected)
        self.listWidget.itemClicked.connect(self.item_selected)
        self.comboBox.currentIndexChanged.connect(self.update_list)
        self.pushButton.clicked.connect(self.add_tag)
    #@+node:peckj.20140804114520.15204: *3* updates + interaction
    #@+node:peckj.20140804114520.15205: *4* item_selected
    def item_selected(self):
        key = id(self.listWidget.currentItem())
        pos = self.mapping[key]
        self.update_current_tags(pos)
        self.c.selectPosition(pos)
        self.c.redraw_now()
    #@+node:peckj.20140804192343.6568: *5* update_current_tags
    def update_current_tags(self,pos):
        # clear out the horizontalLayout2
        hl2 = self.horizontalLayout2
        while hl2.count():
            child = hl2.takeAt(0)
            child.widget().deleteLater()
        label = QtWidgets.QLabel(self)
        label.setText('Tags for current node:')
        hl2.addWidget(label)
        
        tags = self.tc.get_tags(pos)
        # add tags
        for tag in tags:
            l = QtWidgets.QLabel(self)
            l.setText(tag)
            hl2.addWidget(l)
            l.mouseReleaseEvent = self.callback_factory(tag)
        
    #@+node:peckj.20140804194839.6569: *6* callback_factory
    def callback_factory(self, tag):
        c = self.c
        def callback(event):
            p = c.p
            tc = c.theTagController
            ui = tc.ui
            # right click on a tag to remove it from the node
            if event.button() == QtCore.Qt.RightButton:
                tc.remove_tag(p,tag)
            # other clicks make the jumplist open that tag for browsing
            else:
                idx = ui.comboBox.findText(tag)
                ui.comboBox.setCurrentIndex(idx)
            ui.update_all()
        return callback
    #@+node:peckj.20140804114520.15206: *4* update_combobox
    def update_combobox(self):
        self.comboBox.clear()
        tags = self.tc.get_all_tags()
        self.comboBox.addItems(tags)
        self.comboBox.addItems(self.custom_searches)
        
    #@+node:peckj.20140804114520.15207: *4* update_list
    def update_list(self):
        key = str(self.comboBox.currentText()).strip()
        current_tags = self.tc.get_all_tags()
        if key not in current_tags and key not in self.custom_searches:
            if len(re.split(self.search_re, key)) > 1:
                self.custom_searches.append(key)
        
        query = re.split(self.search_re, key)
        
        tags = []
        operations = []
        for i in range(len(query)):
            if i % 2 == 0:
                tags.append(query[i].strip())
            else:
                operations.append(query[i].strip())
        tags.reverse()
        operations.reverse()
        
        resultset = set(self.tc.get_tagged_nodes(tags.pop()))
        while len(operations) > 0:
            op = operations.pop()
            nodes = set(self.tc.get_tagged_nodes(tags.pop()))
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
        for n in resultset:
            item = QtWidgets.QListWidgetItem(n.h)
            self.listWidget.addItem(item)
            self.mapping[id(item)] = n
        count = self.listWidget.count()
        self.label.clear()
        self.label.setText("Total: %s nodes" % count)
    #@+node:peckj.20140804114520.15208: *4* update_all
    def update_all(self):
        ''' updates the tag GUI '''
        key = str(self.comboBox.currentText())
        self.update_combobox()
        if len(key) > 0:
            idx = self.comboBox.findText(key)
            if idx == -1: idx = 0
        else:
            idx = 0 
        self.comboBox.setCurrentIndex(idx)
        self.update_list()
        self.update_current_tags(self.c.p)
    #@+node:peckj.20140806145948.6579: *4* add_tag
    def add_tag(self, event=None):
        p = self.c.p
        tag = str(self.comboBox.currentText()).strip()
        if len(tag) == 0:
            return # no error message, probably an honest mistake
        elif len(re.split(self.search_re,tag)) > 1:
            g.es('Cannot add tags containing any of these characters: &|^-', color='red')
            return # don't add unsearchable tags
        else:
            self.tc.add_tag(p,tag)
    #@+node:peckj.20140811082039.6623: *3* event hooks
    #@+node:peckj.20140804195456.13487: *4* select2_hook
    def select2_hook(self, tag, keywords):
        self.update_current_tags(self.c.p)

    #@+node:peckj.20140806101020.14006: *4* command2_hook
    def command2_hook(self, tag, keywords):
        paste_cmds = ['paste-node',
                      'pasteOutlineRetainingClones', # strange that this one isn't canonicalized
                      'paste-retaining-clones']
        if keywords.get('label') not in paste_cmds:
            return
        
        self.tc.initialize_taglist()
        self.update_all()
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo

#@+leo-ver=5-thin
#@+node:peckj.20131130132659.5964: * @file ../plugins/nodewatch.py
#@+<< docstring >>
#@+node:peckj.20131101132841.6445: ** << docstring >>
"""
Provides a GUI in the Log pane (tab name 'Nodewatch') that lists node headlines.
The nodes that show up in this GUI are scriptable on a per-outline basis, with
@nodewatch nodes.

By Jacob M. Peck

@nodewatch Nodes
================

This plugin leverages Leo's scripting abilities to create programmable lists of
nodes to act as jumplists via a GUI panel in the Log pane. These lists are
definable on a per-outline basis by using @nodewatch nodes.

A @nodewatch node must be a child of a @settings node for this plugin to use it.
This is a safety feature, and will not be changed.

A @nodewatch node is a Leo script that interacts with the
'c.theNodewatchController' object, namely calling the 'add' method on it,
providing it with a category name (string) and a list of vnodes (list). An
example minimal @nodewatch node is as follows (first line is headline, rest is
body)::

    @nodewatch Nodewatch Demo
      @language python
      categoryname = 'All @file nodes'
      nodes = []
      for vnode in c.all_unique_nodes():
          if vnode.h.startswith('@file'):
              nodes.append(vnode)
      c.theNodewatchController.add(categoryname,nodes)

If that node is a child of a @settings node, it will be run every time the
'Refresh' button in the GUI is clicked.

GUI Operation
=============

The Nodewatch GUI is fairly straightforward, consisting of 3 parts:

1. The dropdown box
2. The Refresh button
3. The item list

The dropdown box is filled with items named with the appropriate categoryname
strings given to c.theNodewatchController.add(). It controls the item list
below.

The item list is a list of node headlines -- those returned by the @nodewatch
node whose categoryname matches the currently selected item in the dropdown box.
Clicking on an item in this list will select the node in the outline.

The Refresh button reads and executes all valid @nodewatch nodes in the current
outline, and updates the rest of the GUI appropriately. The 'nodewatch-update'
minibuffer command is an alias for this. This is the only time the scripts are
executed, so you might wish to get in the habit of clicking this button when you
open the Nodewatch GUI.

Important Note
==============

This plugin allows scripts to be executed, and therefore is a security risk.
Unless the '@bool nodewatch_autoexecute_scripts' setting is True, all scripts
are only run via user intervention. You are advised to carefully examine any
@settings->@nodewatch nodes in the outline before clicking 'Refresh', running
'nodewatch-update', or setting '@bool nodewatch_autoexecute_scripts = True'.

Additionally, this plugin does NO checks to make sure that @nodewatch scripts
aren't destructive. Caveat User.

Configuration Settings
======================

This plugin is configured with the following @settings:

@bool nodewatch_autoexecute_scripts
-----------------------------------

Defaults to False. If set to True, all @settings->@nodewatch nodes in the
current outline are executed when the outline loads.

Commands
========

This plugin defines only one command.

nodewatch-refresh
-----------------

Run all @settings->@nodewatch nodes in the outline, and update the nodewatch GUI
(same as clicking the refresh button in the nodewatch GUI).

"""
#@-<< docstring >>
#@+<< imports >>
#@+node:peckj.20131101132841.6447: ** << imports >>
from leo.core import leoGlobals as g
from leo.core.leoQt import QtWidgets, QtCore
#
# Fail fast, right after all imports.
g.assertUi('qt')  # May raise g.UiTypeException, caught by the plugins manager.
#@-<< imports >>
#@+others
#@+node:peckj.20131101132841.6448: ** init
def init():
    """Return True if the plugin has loaded successfully."""
    if g.app.gui is None:
        g.app.createQtGui(__file__)
    ok = g.app.gui.guiName().startswith('qt')
    if ok:
        g.registerHandler('after-create-leo-frame', onCreate)
        g.plugin_signon(__name__)
    else:
        g.es('nodewatch.py not loaded', color='red')
    return ok
#@+node:peckj.20131101132841.6449: ** onCreate
def onCreate(tag, keys):

    c = keys.get('c')
    if not c:
        return

    theNodewatchController = NodewatchController(c)
    c.theNodewatchController = theNodewatchController
#@+node:peckj.20131101132841.6450: ** class NodewatchController
class NodewatchController:
    #@+others
    #@+node:peckj.20131101132841.6452: *3* __init__
    def __init__(self, c):
        self.c = c
        self.watchlists = {}  # a dictionary, with key = Category, value = list of (idx,vnode) tuples
        c.theNodewatchController = self
        self.ui = LeoNodewatchWidget(c)
        c.frame.log.createTab('Nodewatch', widget=self.ui)
    #@+node:peckj.20131101132841.6453: *3* add
    def add(self, key, values):
        """ add a list of vnodes ('values') to the nodewatch category 'key' """
        self.watchlists[key] = list(enumerate(values))
    #@-others
#@+node:peckj.20131101132841.6451: ** class LeoNodewatchWidget
class LeoNodewatchWidget(QtWidgets.QWidget):  # type:ignore
    #@+others
    #@+node:peckj.20131101132841.6454: *3* __init__
    def __init__(self, c, parent=None):
        super().__init__(parent)
        self.c = c
        self.initUI()
        self.registerCallbacks()
        autoexecute_nodewatch_nodes = c.config.getBool('nodewatch-autoexecute-scripts', default=False)
        if autoexecute_nodewatch_nodes and c.config.isLocalSetting('nodewatch_autoexecute_scripts', 'bool'):
            g.issueSecurityWarning('@bool nodewatch_autoexecute_scripts')
            autoexecute_nodewatch_nodes = False
        if autoexecute_nodewatch_nodes:
            self.update_all()
    #@+node:peckj.20131101132841.6462: *3* initialization
    #@+node:peckj.20131101132841.6455: *4* initUI
    def initUI(self):
        # create GUI components
        ## this code is atrocious... don't look too closely
        self.setObjectName("LeoNodewatchWidget")

        # verticalLayout_2: contains
        # verticalLayout
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self)
        self.verticalLayout_2.setContentsMargins(0, 1, 0, 1)
        self.verticalLayout_2.setObjectName("verticalLayout_2")

        # horizontalLayout: contains
        # "Refresh" button
        # comboBox
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")

        # verticalLayout: contains
        # horizontalLayout
        # listWidget
        # label
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")

        self.comboBox = QtWidgets.QComboBox(self)
        self.comboBox.setObjectName("comboBox")
        self.horizontalLayout.addWidget(self.comboBox)
        self.pushButton = QtWidgets.QPushButton("Refresh", self)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setMinimumSize(50, 24)
        self.pushButton.setMaximumSize(50, 24)
        self.horizontalLayout.addWidget(self.pushButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.listWidget = QtWidgets.QListWidget(self)
        self.listWidget.setObjectName("listWidget")
        self.verticalLayout.addWidget(self.listWidget)
        self.label = QtWidgets.QLabel(self)
        self.label.setObjectName("label")
        self.label.setText("Total: 0 items")
        self.verticalLayout.addWidget(self.label)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        QtCore.QMetaObject.connectSlotsByName(self)
    #@+node:peckj.20131101132841.6457: *4* registerCallbacks
    def registerCallbacks(self):
        self.listWidget.itemSelectionChanged.connect(self.item_selected)
        self.listWidget.itemClicked.connect(self.item_selected)
        self.comboBox.currentIndexChanged.connect(self.update_list)
        self.pushButton.clicked.connect(self.update_all)

    #@+node:peckj.20131101132841.6463: *3* updates + interaction
    #@+node:peckj.20131101132841.6459: *4* item_selected
    def item_selected(self):
        idx = self.listWidget.currentRow()
        key = str(self.comboBox.currentText())
        if key == '' or idx > len(self.c.theNodewatchController.watchlists[key]):
            return
        tup = self.c.theNodewatchController.watchlists[key][idx]
        pos = self.c.vnode2position(tup[1])
        self.c.selectPosition(pos)
        self.c.redraw()
    #@+node:peckj.20131101132841.6460: *4* update_combobox
    def update_combobox(self):
        self.c.theNodewatchController.watchlists = {}
        nodes = self.get_valid_nodewatch_nodes()
        for node in nodes:
            self.c.executeScript(p=self.c.vnode2position(node))
        self.comboBox.clear()
        keys = sorted(self.c.theNodewatchController.watchlists.keys())
        self.comboBox.addItems(keys)
    #@+node:peckj.20131101132841.6461: *4* update_list
    def update_list(self):
        key = str(self.comboBox.currentText())
        self.listWidget.clear()
        for n in self.c.theNodewatchController.watchlists.get(key, []):
            self.listWidget.addItem(n[1].h)
        count = self.listWidget.count()
        self.label.clear()
        self.label.setText("Total: %s items" % count)
    #@+node:peckj.20131101132841.6458: *4* update_all
    def update_all(self, event=None):
        """ updates the nodewatch GUI by running all valid @nodewatch nodes """
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
    #@+node:peckj.20131104093045.6578: *3* helpers
    #@+node:peckj.20131104093045.6579: *4* get_valid_nodewatch_nodes
    def get_valid_nodewatch_nodes(self):
        """ returns a list of valid vnodes """
        nodes = []
        for node in self.c.all_unique_nodes():
            if node.h.startswith('@nodewatch'):
                parentheads = []
                for p in self.c.vnode2allPositions(node):
                    for parent in p.parents():
                        parentheads.append(parent.h)
                settings = '@settings' in parentheads
                ignore = False
                for x in parentheads:
                    if x.startswith('@ignore'):
                        ignore = True
                if settings and not ignore:
                    nodes.append(node)
        return nodes
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo

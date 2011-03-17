#@+leo-ver=5-thin
#@+node:tbrown.20110203111907.5519: * @file free_layout.py
"""Adds flexible panel layout through context menus on the handles between panels.
Requires Qt.
"""

__version__ = '0.1'
    # 0.1 - initial release - TNB
    
#@+<< imports >>
#@+node:tbrown.20110203111907.5520: ** << imports >>
import leo.core.leoGlobals as g

g.assertUi('qt')

from PyQt4 import QtCore, QtGui, Qt

from leo.plugins.nested_splitter import NestedSplitter
#@-<< imports >>

#@+others
#@+node:tbrown.20110203111907.5521: ** init
def init():

    if g.app.gui.guiName() != "qt":
        return False

    g.registerHandler('after-create-leo-frame',onCreate)
    # can't use before-create-leo-frame because Qt dock's not ready
    g.plugin_signon(__name__)

    return True
#@+node:tbrown.20110203111907.5522: ** onCreate & callbacks
def onCreate(tag, keys):

    c = keys.get('c')
    if not c: return

    NestedSplitter.enabled = True
    
    #@+others
    #@+node:ekr.20110317024548.14380: *3* add_item
    def add_item(func,menu,name,splitter):
        
        act = QtGui.QAction(name,splitter)
        act.setObjectName(name.lower().replace(' ','-'))
        act.connect(act, Qt.SIGNAL('triggered()'), func)
        menu.addAction(act)
    #@+node:ekr.20110316100442.14371: *3* offer_tabs
    def offer_tabs(menu, splitter, index, button_mode):

        if not button_mode:
            return

        top_splitter = c.frame.top.splitter_2.top()
        logTabWidget = top_splitter.findChild(QtGui.QWidget, "logTabWidget")

        for n in range(logTabWidget.count()):

            def wrapper(w=logTabWidget.widget(n), s=splitter,
                        t=logTabWidget.tabText(n)):
                w.setHidden(False)
                w._is_from_tab = t
                s.replace_widget(s.widget(index), w)
        
            # act = QtGui.QAction("Add "+logTabWidget.tabText(n), splitter)
            # act.connect(act, Qt.SIGNAL('triggered()'), wrapper)
            # menu.addAction(act)
            add_item(wrapper,menu,"Add "+logTabWidget.tabText(n),splitter)
    #@+node:ekr.20110316100442.14372: *3* offer_viewrendered
    def offer_viewrendered(menu, splitter, index, button_mode):

        if button_mode and hasattr(c,"viewrendered") and c.viewrendered:
            
            def wrapper(w=c.viewrendered, s=splitter):
                s.replace_widget(s.widget(index), w)
                w.activate()

            # act = QtGui.QAction("Add viewrendered", splitter)
            # act.connect(act, Qt.SIGNAL('triggered()'), wrapper)
            # menu.addAction(act)
            
            add_item(wrapper,menu,"Add Viewrendered",splitter)
    #@-others

    splitter = c.frame.top.splitter_2.top()

    # Register menu callbacks
    splitter.register(offer_tabs)
    splitter.register(offer_viewrendered)

    # when NestedSplitter disposes of children, it will either close
    # them, or move them to another designated widget.  Here we set
    # up two designated widgets

    logTabWidget = splitter.findChild(QtGui.QWidget, "logTabWidget")
    splitter.root.holders['_is_from_tab'] = logTabWidget
    splitter.root.holders['_is_permanent'] = splitter

    # allow body and tree widgets to be "removed" to tabs on the log tab panel    
    bodyWidget = splitter.findChild(QtGui.QFrame, "bodyFrame")
    bodyWidget._is_from_tab = "Body"
    treeWidget = splitter.findChild(QtGui.QFrame, "outlineFrame")
    treeWidget._is_from_tab = "Tree"
    # also the other tabs will have _is_from_tab set on them by the
    # offer_tabs menu callback above

    # if the log tab panel is removed, move it back to the top splitter
    logWidget = splitter.findChild(QtGui.QFrame, "logFrame")
    logWidget._is_permanent = True
#@-others
#@-leo

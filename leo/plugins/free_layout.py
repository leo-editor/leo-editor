#@+leo-ver=5-thin
#@+node:tbrown.20110203111907.5519: * @file free_layout.py
#@+<< docstring >>
#@+node:ekr.20110319161401.14467: ** << docstring >>
"""Adds flexible panel layout through context menus on the handles between panels.
Requires Qt.
"""
#@-<< docstring >>

__version__ = '0.1'
    # 0.1 - initial release - TNB
    
#@+<< imports >>
#@+node:tbrown.20110203111907.5520: ** << imports >>
import leo.core.leoGlobals as g

g.assertUi('qt')

from PyQt4 import QtCore, QtGui, Qt

from leo.plugins.nested_splitter import NestedSplitter
#@-<< imports >>

controllers = {}  # Keys are c.hash(), values are PluginControllers.

#@+others
#@+node:tbrown.20110203111907.5521: ** init
def init():
    
    # g.trace('free_layout.py')

    if g.app.gui.guiName() != "qt":
        return False

    g.registerHandler('after-create-leo-frame',onCreate)
    # can't use before-create-leo-frame because Qt dock's not ready
    g.plugin_signon(__name__)

    return True
#@+node:ekr.20110318080425.14391: ** onCreate
def onCreate (tag, keys):
    
    global controllers
    
    c = keys.get('c')
    if c:
        h = c.hash()
        if not controllers.get(h):
            controllers[h] = FreeLayoutController(c)
        
        NestedSplitter.enabled = True
#@+node:ekr.20110318080425.14389: ** class FreeLayoutController
class FreeLayoutController:
    
    #@+others
    #@+node:ekr.20110318080425.14390: *3*  ctor
    def __init__ (self,c):
        
        self.c = c
        self.renderer = None # The renderer widget
        self.top_splitter = None # The top-level splitter.
        
        c.free_layout = self # For viewrendered plugin.
        
        self.init()
        
    #@+node:ekr.20110318080425.14393: *3* create_renderer
    def create_renderer (self,w):
        
        pc = self ; c = pc.c
        
        if not pc.renderer:
            assert w == c.viewrendered.w,'widget mismatch'
                # Called from viewrender, so it must exist.
            index = 1
            dw = c.frame.top
            splitter = dw.splitter_2
            body = dw.leo_body_frame
            index = splitter.indexOf(body)
            new_splitter,new_index = splitter.split(index,side=1,w=w,name='renderer-splitter')
            pc.renderer = new_splitter # pc is a FreeLayoutController.
            c.viewrendered.set_renderer(new_splitter,new_index)
            c.frame.equalSizedPanes()
            c.bodyWantsFocusNow()
            # g.trace(splitter)
    #@+node:tbrown.20110203111907.5522: *3* init
    def init(self):

        pc = self ; c = self.c

        self.top_splitter = splitter = c.frame.top.splitter_2.top() # A NestedSplitter.

        # Register menu callbacks with the NestedSplitter.
        splitter.register(pc.offer_tabs)
        splitter.register(pc.offer_viewrendered)

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
    #@+node:ekr.20110318080425.14392: *3* menu callbacks
    # These are called when the user right-clicks the NestedSplitter.
    #@+node:ekr.20110317024548.14380: *4* add_item
    def add_item(self,func,menu,name,splitter):
        
        act = QtGui.QAction(name,splitter)
        act.setObjectName(str(name).lower().replace(' ','-'))
        act.connect(act, Qt.SIGNAL('triggered()'), func)
        menu.addAction(act)
    #@+node:ekr.20110316100442.14371: *4* offer_tabs
    def offer_tabs(self,menu,splitter,index,button_mode):
        
        pc = self
        
        if not button_mode:
            return

        top_splitter = pc.top_splitter # c.frame.top.splitter_2.top()
        logTabWidget = top_splitter.findChild(QtGui.QWidget, "logTabWidget")

        for n in range(logTabWidget.count()):

            def wrapper(
                w=logTabWidget.widget(n),
                splitter=splitter,
                s=logTabWidget.tabText(n)):
                w.setHidden(False)
                w._is_from_tab = s
                splitter.replace_widget(splitter.widget(index), w)

            self.add_item(wrapper,menu,"Add "+logTabWidget.tabText(n),splitter)
    #@+node:ekr.20110316100442.14372: *4* offer_viewrendered
    def offer_viewrendered(self,menu,splitter, index, button_mode):
        
        pc = self ; c = pc.c
        
        vr_pc = hasattr(c,"viewrendered") and c.viewrendered

        if button_mode and vr_pc and not vr_pc.has_renderer():
            
            def wrapper(index=index,pc=vr_pc,splitter=splitter):
                w = pc.w
                splitter.replace_widget(splitter.widget(index),w)
                pc.show()
                pc.set_renderer(splitter,index)
                # g.trace(index)
            
            self.add_item(wrapper,menu,"Add Viewrendered",splitter)
    #@-others
#@-others
#@-leo

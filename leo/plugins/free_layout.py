#@+leo-ver=5-thin
#@+node:ekr.20120419093256.10048: * @file ../plugins/free_layout.py
#@+<< docstring >>
#@+node:ekr.20110319161401.14467: ** << docstring >>
"""Adds flexible panel layout through context menus on the handles between panels.
Requires Qt.
"""
#@-<< docstring >>

__version__ = '0.1'
    # 0.1 - initial release - TNB
    
# print('free_layout imported')
    
#@+<< imports >>
#@+node:tbrown.20110203111907.5520: ** << imports >>
import leo.core.leoGlobals as g

# g.assertUi('qt')

from PyQt4 import QtCore, QtGui, Qt

from leo.plugins.nested_splitter import NestedSplitter, NestedSplitterChoice

import json
#@-<< imports >>

# controllers = {}  # Keys are c.hash(), values are PluginControllers.

#@+others
#@+node:tbrown.20110203111907.5521: ** init (free_layout.py)
def init():
    
    if 1:
        return g.app.gui.guiName() == "qt"
    else:
        # g.trace('free_layout.py')
        if g.app.gui.guiName() != "qt":
            return False
    
        g.registerHandler('after-create-leo-frame',bindControllers)
        g.registerHandler('after-create-leo-frame2',loadLayouts)
        g.plugin_signon(__name__)
        
        # DEPRECATED
        if not hasattr(g, 'free_layout_callbacks'):
            g.free_layout_callbacks = []
    
        return True
#@+node:ekr.20120419095424.9925: ** no longer used
if 0:
    # bindControllers is done in FreeLayoutController.__init__
    # loadLayous is now a FreeLayoutController method.
    #@+others
    #@+node:ekr.20110318080425.14391: *3* bindControllers
    def bindControllers(tag, keys):
        
        c = keys.get('c')
        if c:
            NestedSplitter.enabled = True
            FreeLayoutController(c) 
    #@+node:tbrown.20110714155709.22852: *3* loadLayouts
    def loadLayouts(tag, keys):
        
        c = keys.get('c')
        if c:

            layout = c.config.getData("free-layout-layout")
            
            if layout:
                layout = json.loads('\n'.join(layout))
                
            if '_ns_layout' in c.db:
                name = c.db['_ns_layout']
                if layout:
                    g.es("NOTE: embedded layout in @settings/@data free-layout-layout " \
                        "overrides saved layout "+name)
                else:
                    layout = g.app.db['ns_layouts'][name]
        
            if layout:
                # Careful: we could be unit testing.
                splitter = c.free_layout.get_top_splitter()
                if splitter:
                    splitter.load_layout(layout)
    #@-others
#@+node:tbrown.20120418121002.25711: ** class TopLevelFreeLayout
class TopLevelFreeLayout(QtGui.QWidget):
    #@+others
    #@+node:tbrown.20120418121002.25713: *3* __init__
    def __init__(self, *args, **kargs):
        self.owner = kargs['owner']
        del kargs['owner']
        QtGui.QWidget.__init__(self, *args, **kargs)
    #@+node:tbrown.20120418121002.25714: *3* closeEvent
    def closeEvent(self, event):
        widget = self.findChild(NestedSplitter)
        
        other_top = self.owner.get_top_splitter()
        
        # adapted from NestedSplitter.remove()
        count = widget.count()
        all_ok = True

        to_close = []

        for splitter in widget.self_and_descendants():
            for i in range(splitter.count()-1, -1, -1):
                
                to_close.append(splitter.widget(i))
                
        for w in to_close:
                
            all_ok &= (widget.close_or_keep(w, other_top=other_top) is not False)

        if all_ok or count <= 0:
            self.owner.closing(self)
        else:
            event.ignore()
    #@-others
#@+node:ekr.20110318080425.14389: ** class FreeLayoutController
class FreeLayoutController:
    
    #@+others
    #@+node:ekr.20110318080425.14390: *3*  ctor (FreeLayoutController)
    def __init__ (self,c):
        
        # g.trace('(FreeLayoutController)',c) # ,g.callers(files=True))
        
        # if hasattr(c,'free_layout'):
            # return
        
        self.c = c
        
        #X self.renderer = None # The renderer widget
        #X self.top_splitter = None # The top-level splitter.
        
        # c.free_layout = self
            # To be removed
        
        #X  # For viewrendered plugin.
        
        self.windows = []
        
        # g.registerHandler('after-create-leo-frame',self.bindControllers)
        g.registerHandler('after-create-leo-frame',self.init)
        g.registerHandler('after-create-leo-frame2',self.loadLayouts)
        
        ### self.init()
        
    #@+node:ekr.20110318080425.14393: *3* create_renderer
    def Xcreate_renderer (self,w):
        
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
    #@+node:tbrown.20110203111907.5522: *3* init (FreeLayoutController)
    def init(self,tag,keys):

        c = self.c

        if c != keys.get('c'):
            return
            
        # g.trace(c.frame.title)

        # Careful: we could be unit testing.

        splitter = self.get_top_splitter() # A NestedSplitter.
        if not splitter:
            # g.trace('no splitter!')
            return None
            
        # Was in bindControlers function.
        NestedSplitter.enabled = True

        # DEPRECATED
        if not hasattr(g,'free_layout_callbacks'):
            g.free_layout_callbacks = []

        # Register menu callbacks with the NestedSplitter.
        splitter.register(self.offer_tabs)
        splitter.register(self.from_g)
        splitter.register(self.embed)

        # when NestedSplitter disposes of children, it will either close
        # them, or move them to another designated widget.  Here we set
        # up two designated widgets

        logTabWidget = splitter.findChild(QtGui.QWidget, "logTabWidget")
        splitter.root.holders['_is_from_tab'] = logTabWidget
        splitter.root.holders['_is_permanent'] = 'TOP'

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

        # tag core Leo components (see ns_provides)
        splitter.findChild(QtGui.QWidget, "outlineFrame")._ns_id = '_leo_pane:outlineFrame'
        splitter.findChild(QtGui.QWidget, "logFrame")._ns_id = '_leo_pane:logFrame'
        splitter.findChild(QtGui.QWidget, "bodyFrame")._ns_id = '_leo_pane:bodyFrame'

        splitter.register_provider(self)
    #@+node:tbrown.20110621120042.22918: *3* from_g
    def from_g(self, menu, splitter, index, button_mode):
        
        for i in g.free_layout_callbacks:
            i(menu, splitter, index, button_mode, self.c)
    #@+node:tbrown.20110621120042.22914: *3* get_top_splitter
    def get_top_splitter(self):
        
        # Careful: we could be unit testing.
        f = self.c.frame
        if hasattr(f,'top') and f.top:
            return f.top.findChild(NestedSplitter).top()
        else:
            return None
    #@+node:ekr.20120419095424.9927: *3* loadLayouts (FreeLayoutController)
    def loadLayouts(self,tag,keys):
        
        c = self.c
        
        if c != keys.get('c'):
            return
            
        # g.trace(c.frame.title)
      
        layout = c.config.getData("free-layout-layout")
        
        if layout:
            layout = json.loads('\n'.join(layout))
            
        if '_ns_layout' in c.db:
            name = c.db['_ns_layout']
            if layout:
                g.es("NOTE: embedded layout in @settings/@data free-layout-layout " \
                    "overrides saved layout "+name)
            else:
                layout = g.app.db['ns_layouts'][name]

        if layout:
            # Careful: we could be unit testing.
            splitter = c.free_layout.get_top_splitter()
            if splitter:
                splitter.load_layout(layout)
    #@+node:ekr.20110318080425.14392: *3* menu callbacks
    # These are called when the user right-clicks the NestedSplitter.
    #@+node:ekr.20110317024548.14380: *4* add_item
    def add_item(self,func,menu,name,splitter):
        
        act = QtGui.QAction(name,splitter)
        act.setObjectName(str(name).lower().replace(' ','-'))
        act.connect(act, Qt.SIGNAL('triggered()'), func)
        menu.addAction(act)
    #@+node:ekr.20110316100442.14371: *4* offer_tabs
    def offer_tabs(self, menu, splitter, index, button_mode):
        
        return
        
        pc = self
        
        if not button_mode:
            return

        # Careful: we could be unit testing.
        top_splitter = self.get_top_splitter()
        if not top_splitter: return

        logTabWidget = self.find_child(QtGui.QWidget, "logTabWidget")

        for n in range(logTabWidget.count()):

            def wrapper(
                w=logTabWidget.widget(n),
                splitter=splitter,
                s=logTabWidget.tabText(n)):
                w.setHidden(False)
                w._is_from_tab = s
                splitter.replace_widget(splitter.widget(index), w)

            self.add_item(wrapper,menu,"Add "+logTabWidget.tabText(n),splitter)
    #@+node:tbrown.20120119080604.22982: *4* embed
    def embed(self, menu, splitter, index, button_mode):
        """embed layout in outline"""
        
        if button_mode:
            return
        # Careful: we could be unit testing.
        top_splitter = self.get_top_splitter()
        if not top_splitter: return

        def make_settings(c=self.c, layout=top_splitter.get_saveable_layout()):
            
            nd = g.findNodeAnywhere(c, "@data free-layout-layout")
            if not nd:
                settings = g.findNodeAnywhere(c, "@settings")
                if not settings:
                    settings = c.rootPosition().insertAfter()
                    settings.h = "@settings"
                nd = settings.insertAsNthChild(0)
            
            nd.h = "@data free-layout-layout"
            nd.b = json.dumps(layout, indent=4)
            
            nd = nd.parent()
            if not nd or nd.h != "@settings":
                g.es("WARNING: @data free-layout-layout node is not " \
                    "under an active @settings node")
            
            c.redraw()

        self.add_item(make_settings,menu,"Embed layout",splitter)
    #@+node:ekr.20110316100442.14372: *4* offer_viewrendered
    def offer_viewrendered(self, menu, splitter, index, button_mode):
        
        return  # done from viewrendered.py
        
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
    #@+node:tbrown.20110627201141.11745: *3* ns_provides
    def ns_provides(self):

        ans = []
        
        # list of things in tab widget
        logTabWidget = self.find_child(QtGui.QWidget, "logTabWidget")
        for n in range(logTabWidget.count()):
            text = str(logTabWidget.tabText(n))  # not QString
            if text in ('Body', 'Tree'):
                continue  # handled below
            if text == 'Log':
                # if Leo can't find Log in tab pane, it creates another
                continue
            ans.append((text, 
                        '_leo_tab:'+text))

        ans.append(('Tree', '_leo_pane:outlineFrame'))
        ans.append(('Body', '_leo_pane:bodyFrame'))
        ans.append(('Tab pane', '_leo_pane:logFrame'))
        
        return ans
    #@+node:tbrown.20110628083641.11724: *3* ns_provide
    def ns_provide(self, id_):
        
        if id_.startswith('_leo_tab:'):
        
            id_ = id_.split(':', 1)[1]
        
            logTabWidget = self.find_child(QtGui.QWidget, "logTabWidget")
                
            for n in range(logTabWidget.count()):
                if logTabWidget.tabText(n) == id_:
                    w = logTabWidget.widget(n)
                    w.setHidden(False)
                    w._is_from_tab = logTabWidget.tabText(n)
                    w.setMinimumSize(20,20)
                    return w
                    
            # didn't find it, maybe it's already in a splitter
            return 'USE_EXISTING'

        if id_.startswith('_leo_pane:'):
        
            id_ = id_.split(':', 1)[1]
            w = self.find_child(QtGui.QWidget, id_)
            if w:
                w.setHidden(False)  # may be from Tab holder
                w.setMinimumSize(20,20)
            return w      
             
        return None
    #@+node:tbrown.20110628083641.11730: *3* ns_context
    def ns_context(self):
        
        
        ans = [
            ('Save layout', '_fl_save_layout'),
            ('Open window', '_fl_open_window'),
        ]
        
        d = g.app.db.get('ns_layouts', {})
        if d:
            ans.append({'Load layout': [(k, '_fl_load_layout:'+k) for k in d]})
            ans.append({'Delete layout': [(k, '_fl_delete_layout:'+k) for k in d]})
            ans.append(('Forget layout', '_fl_forget_layout:'))
            
        return ans
    #@+node:tbrown.20110628083641.11732: *3* ns_do_context
    def ns_do_context(self, id_, splitter, index):
        
        if id_.startswith('_fl_open_window'):
            self.open_window()
            return True

        if id_ == '_fl_save_layout':
            
            if self.c.config.getData("free-layout-layout"):
                g.es("WARNING: embedded layout in @settings/@data free-layout-layout " \
                        "will override saved layout")
            
            layout = self.get_top_splitter().get_saveable_layout()
            name = g.app.gui.runAskOkCancelStringDialog(self.c, "Save layout",
                "Name for layout?")
            if name:
                self.c.db['_ns_layout'] = name
                d = g.app.db.get('ns_layouts', {})
                d[name] = layout
                # make sure g.app.db's __set_item__ is hit so it knows to save
                g.app.db['ns_layouts'] = d
                
            return True
        
        if id_.startswith('_fl_load_layout:'):

            if self.c.config.getData("free-layout-layout"):
                g.es("WARNING: embedded layout in @settings/@data free-layout-layout " \
                        "will override saved layout")
            
            name = id_.split(':', 1)[1]
            self.c.db['_ns_layout'] = name
            layout = g.app.db['ns_layouts'][name]
            self.get_top_splitter().load_layout(layout)
            return True
            
        if id_.startswith('_fl_delete_layout:'):
            name = id_.split(':', 1)[1]
            if g.app.gui.runAskYesNoCancelDialog(self.c, "Really delete Layout?",
                "Really permanently delete the layout '%s'?"%name) == 'yes':
                d = g.app.db.get('ns_layouts', {})
                del d[name]
                # make sure g.app.db's __set_item__ is hit so it knows to save
                g.app.db['ns_layouts'] = d
        
        if id_.startswith('_fl_forget_layout:') or id_.startswith('_fl_delete_layout:'):
            if '_ns_layout' in self.c.db:
                del self.c.db['_ns_layout']
    #@+node:tbrown.20120418121002.25438: *3* open_window
    def open_window(self):
        
        window = TopLevelFreeLayout(owner=self)
        window.setStyleSheet(
            '\n'.join(self.c.config.getData('qt-gui-plugin-style-sheet')))
        hbox = QtGui.QHBoxLayout()
        window.setLayout(hbox)
        hbox.setContentsMargins(0,0,0,0)
        window.resize(400,300)
        
        ns = NestedSplitter(root=self.get_top_splitter().root)
        hbox.addWidget(ns)
        ns.addWidget(NestedSplitterChoice(ns))
        ns.addWidget(NestedSplitterChoice(ns))
        ns.setSizes([0,1])

        #X ns.register(self.offer_tabs)
        #X ns.register(self.from_g)
        #X ns.register(self.embed)
        #X ns.register_provider(self)

        self.windows.append(window)
        
        
        window.show()
    #@+node:tbrown.20120418121002.25712: *3* closing
    def closing(self, window):
        
        self.windows.remove(window)
    #@+node:tbrown.20120418121002.25439: *3* find_child
    def find_child(self, child_class, child_name=None):
        """Like QObject.findChild, except search self.get_top_splitter()
        *AND* each window in self.windows()
        """
        
        child = self.get_top_splitter().findChild(child_class, child_name)
        
        if not child:
            for window in self.windows:
                child = window.findChild(child_class, child_name)
                if child:
                    break
        
        return child
    #@-others
#@-others
#@-leo

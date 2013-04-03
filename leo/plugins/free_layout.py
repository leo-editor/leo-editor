#@+leo-ver=5-thin
#@+node:ekr.20120419093256.10048: * @file ../plugins/free_layout.py
#@+<< docstring >>
#@+node:ekr.20110319161401.14467: ** << docstring >>
"""Adds flexible panel layout through context menus on the handles between panels.

Uses NestedSplitter, a more intelligent QSplitter, from leo.plugins.nested_splitter

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

        return True
#@+node:ekr.20120419095424.9925: ** no longer used
if 0:
    # bindControllers is done in FreeLayoutController.__init__
    # loadLayouts is now a FreeLayoutController method.
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
#@+node:ekr.20110318080425.14389: ** class FreeLayoutController
class FreeLayoutController:
    """Glue between Leo and the NestedSplitter gui widget.  All Leo aware
    code should be in here, none in NestedSplitter.

    *ALSO* implements the provider interface for NestedSplitter, in
    ns_provides, ns_provide, ns_context, ns_do_context, which 
    NestedSplitter uses as callbacks to populate splitter-handle context-menu
    and the empty pane Action button menu:

    see (ctrl-click this URL)
    file://{{g.getBaseDirectory(c)}}/LeoPyRef.leo#Code-->Qt%20gui-->@file%20../plugins/nested_splitter.py-->class%20NestedSplitter%20(QSplitter)-->register_provider

    ns_provides
      tell NestedSplitter which Action button items we can provide
    ns_provide
      provide the advertised service when an Action button item we
      advertised is selected
    ns_context
      tell NestedSplitter which splitter-handle context-menu items
      we can provide
    ns_do_context
      provide the advertised service when a splitter-handle context-menu
      item we advertised is selected
    """
    #@+others
    #@+node:ekr.20110318080425.14390: *3*  ctor (FreeLayoutController)
    def __init__ (self,c):

        # g.trace('(FreeLayoutController)',c) # ,g.callers(files=True))

        # if hasattr(c,'free_layout'):
            # return

        self.c = c

        # c.free_layout = self
            # To be removed

        # g.registerHandler('after-create-leo-frame',self.bindControllers)

        # attach to an outline
        g.registerHandler('after-create-leo-frame',self.init)

        # now that the outline's set up (plugins etc.), load layout for
        # outline, can't do that sooner as plugins must be loaded first
        # to provide their widgets in panels etc.
        g.registerHandler('after-create-leo-frame2',self.loadLayouts)

        ### self.init()

    #@+node:ekr.20110318080425.14393: *3* create_renderer
    def XXcreate_renderer (self,w):
        """NO LONGER USED, viewrendered use of free-layout is in viewrendered.py"""
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
        """Attach to an outline and

        - add tags to widgets to indicate that they're essential
          (tree, body, log-window-tabs) and

        - tag the log-window-tabs widget as the place to put widgets
          from free-laout panes which are closed

        - register this FreeLayoutController as a provider of menu items
          for NestedSplitter
        """

        c = self.c

        if c != keys.get('c'):
            return

        # g.trace(c.frame.title)

        # Careful: we could be unit testing.

        splitter = self.get_top_splitter() # A NestedSplitter.
        if not splitter:
            # g.trace('no splitter!')
            return None

        # by default NestedSplitter's context menus are disabled, needed
        # once to globally enable them
        NestedSplitter.enabled = True

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
    #@+node:tbrown.20110621120042.22914: *3* get_top_splitter
    def get_top_splitter(self):

        # Careful: we could be unit testing.
        f = self.c.frame
        if hasattr(f,'top') and f.top:
            return f.top.findChild(NestedSplitter).top()
        else:
            return None
    #@+node:ekr.20120419095424.9927: *3* loadLayouts (FreeLayoutController)
    def loadLayouts(self, tag, keys, reloading=False):
        """loadLayouts - Load the outlines layout

        :Parameters:
        - `tag`: from hook event
        - `keys`: from hook event
        - `reloading`: True if this is not the initial load, see below
        
        When called from the `after-create-leo-frame2` hook this defaults
        to False.  When called from the `resotre-layout` command, this is set
        True, and the layout the outline had *when first loaded* is restored.
        Useful if you want to temporarily switch to a different layout and then
        back, without having to remember the original layouts name.
        """

        c = self.c

        if c != keys.get('c'):
            return

        # g.trace(c.frame.title)

        layout = c.config.getData("free-layout-layout")

        if layout:
            layout = json.loads('\n'.join(layout))

        if '_ns_layout' in c.db:
            if not reloading: 
                name = c.db['_ns_layout']
                c.free_layout.original_layout = name
            else:
                name = c.free_layout.original_layout
                c.db['_ns_layout'] = name

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
    #@+node:tbrown.20110627201141.11745: *3* ns_provides
    def ns_provides(self):

        ans = []

        # list of things in tab widget
        logTabWidget = self.get_top_splitter().find_child(QtGui.QWidget, "logTabWidget")

        for n in range(logTabWidget.count()):
            text = str(logTabWidget.tabText(n))  # not QString
            if text in ('Body', 'Tree'):
                continue  # handled below
            if text == 'Log':
                # if Leo can't find Log in tab pane, it creates another
                continue
            ans.append((text, '_leo_tab:'+text))

        ans.append(('Tree', '_leo_pane:outlineFrame'))
        ans.append(('Body', '_leo_pane:bodyFrame'))
        ans.append(('Tab pane', '_leo_pane:logFrame'))

        return ans
    #@+node:tbrown.20110628083641.11724: *3* ns_provide
    def ns_provide(self, id_):

        if id_.startswith('_leo_tab:'):

            id_ = id_.split(':', 1)[1]

            logTabWidget = self.get_top_splitter().find_child(QtGui.QWidget, "logTabWidget")

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
            w = self.get_top_splitter().find_child(QtGui.QWidget, id_)
            if w:
                w.setHidden(False)  # may be from Tab holder
                w.setMinimumSize(20,20)
            return w      

        return None
    #@+node:tbrown.20110628083641.11730: *3* ns_context
    def ns_context(self):


        ans = [
            ('Embed layout', '_fl_embed_layout'),
            ('Save layout', '_fl_save_layout'),
        ]

        d = g.app.db.get('ns_layouts', {})
        if d:
            ans.append({'Load layout': [(k, '_fl_load_layout:'+k) for k in d]})
            ans.append({'Delete layout': [(k, '_fl_delete_layout:'+k) for k in d]})
            ans.append(('Forget layout', '_fl_forget_layout:'))
            ans.append(('Restore layout', '_fl_restore_layout:'))

        return ans
    #@+node:tbrown.20110628083641.11732: *3* ns_do_context
    def ns_do_context(self, id_, splitter, index):

        if id_.startswith('_fl_embed_layout'):
            self.embed()
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
                if '_ns_layout' in self.c.db:
                    del self.c.db['_ns_layout']
            return True

        if id_.startswith('_fl_forget_layout:'):
            if '_ns_layout' in self.c.db:
                del self.c.db['_ns_layout']
            return True

        if id_.startswith('_fl_restore_layout:'):
            self.loadLayouts("reload", {'c':self.c}, reloading=True)
            return True

        return False
    #@+node:tbrown.20120119080604.22982: *3* embed
    def embed(self): 
        """called from ns_do_context - embed layout in outline's
        @settings, an alternative to the Load/Save named layout system
        """

        # Careful: we could be unit testing.
        top_splitter = self.get_top_splitter()
        if not top_splitter: return

        c = self.c

        layout=top_splitter.get_saveable_layout()

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
    #@-others
#@+node:tbrown.20130403081644.25265: ** @g.command free-layout-restore
@g.command('free_layout_restore')
def free_layout_restore(kwargs):
    """free_layout_restore - restore layout outline had when it was loaded

    :Parameters:
    - `kwargs`: from command callback
    """

    c = kwargs['c']
    c.free_layout.loadLayouts('reload', {'c':c}, reloading=True)
#@-others
#@-leo

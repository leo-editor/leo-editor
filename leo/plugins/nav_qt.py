#@+leo-ver=5-thin
#@+node:ville.20090518182905.5419: * @file nav_qt.py
#@+<< docstring >>
#@+node:ville.20090518182905.5420: ** << docstring >>
'''Adds "Back" and "Forward" buttons (Qt only).

Creates "back" and "forward" buttons on button bar. These navigate
the node history.

This plugin does not need specific setup. If the plugin is loaded, the buttons 
will be available. The buttons use the icon specified in the active Qt style

'''
#@-<< docstring >>

__version__ = '0.2'
#@+<< version history >>
#@+node:ville.20090518182905.5421: ** << version history >>
#@@killcolor
#@+at
# 
# 0.1 Functionally complete version
# 0.2 EKR: check p before calling c.selectPosition(p)
#@-<< version history >>

#@+<< imports >>
#@+node:ville.20090518182905.5422: ** << imports >>
import leo.core.leoGlobals as g

g.assertUi('qt')

from PyQt4 import QtGui, QtCore

# Whatever other imports your plugins uses.
#@-<< imports >>

#@+others
#@+node:ville.20090518182905.5423: ** init
def init ():


    ok = g.app.gui.guiName() == "qt"

    if ok:
        if 0: # Use this if you want to create the commander class before the frame is fully created.
            g.registerHandler('before-create-leo-frame',onCreate)
        else: # Use this if you want to create the commander class after the frame is fully created.
            g.registerHandler('after-create-leo-frame',onCreate)
        g.plugin_signon(__name__)

    return ok
#@+node:ville.20090518182905.5424: ** onCreate
def onCreate (tag, keys):

    c = keys.get('c')
    if not c: return

    thePluginController = pluginController(c)
#@+node:ville.20090518182905.5425: ** class pluginController
class pluginController:

    #@+others
    #@+node:ville.20090518182905.5426: *3* __init__
    def __init__ (self,c):

        self.c = c
        c._prev_next = self
        self.popularity = {}
        g.registerHandler("select2", self.update_popularity)
        g.tree_popup_handlers.append(self.popular_nodes)
        self.makeButtons()
        # Warning: hook handlers must use keywords.get('c'), NOT self.c.
    #@+node:ville.20090518182905.7868: *3* clickNext
    def clickNext(self):
        c = self.c
        p = c.goNextVisitedNode()
        # g.trace(p)
        if p: c.selectPosition(p)
    #@+node:ville.20090518182905.7867: *3* clickPrev
    def clickPrev(self):
        c = self.c
        p = c.goPrevVisitedNode()
        # g.trace(p)
        #if p: c.selectPosition(p)

    #@+node:ville.20090518182905.5427: *3* makeButtons
    def makeButtons(self):
        ib_w = self.c.frame.iconBar.w
        if not ib_w: return # EKR: can be None when unit testing.
        icon_l = ib_w.style().standardIcon(QtGui.QStyle.SP_ArrowLeft)
        icon_r = ib_w.style().standardIcon(QtGui.QStyle.SP_ArrowRight)
        act_l = QtGui.QAction(icon_l, 'prev', ib_w)
        act_r = QtGui.QAction(icon_r, 'next', ib_w)
        act_l.connect(act_l, QtCore.SIGNAL("triggered()"), self.clickPrev)
        act_r.connect(act_r, QtCore.SIGNAL("triggered()"), self.clickNext)
        self.c.frame.iconBar.add(qaction = act_l, command = self.clickPrev)
        self.c.frame.iconBar.add(qaction = act_r, command = self.clickNext)

        # failed attempt to add custom context menu to prev/next button
        # b = self.c.frame.iconBar.w.widgetForAction(act_l)
        # b.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        #
        #   def history(pos, b=b):
        #     print 'running history'
        #     menu = QtGui.QMenu(parent=b)
        #     menu.addAction(act_l)
        #     menu.addAction(QtGui.QAction('other', b))
        #     menu.exec_(b.mapToGlobal(pos))
        #
        #   b.connect(b,
        #     QtCore.SIGNAL('customContextMenuRequested(QPoint)'),
        #     history)
    #@+node:tbrown.20101205145115.14821: *3* popular_nodes
    def popular_nodes(self, c, p, parent_menu):

        if c != self.c:
            return

        menu = QtGui.QMenu("History...", parent_menu)

        for i in sorted(self.popularity.values(), reverse=True)[:20]:
            action = menu.addAction(i[1])
            def wrapper(gnx=i[2]):
                self.c.selectPosition(gnx)
            action.connect(action, QtCore.SIGNAL("triggered()"), wrapper)

        start = parent_menu.actions()
        if start:
            parent_menu.insertMenu(start[0], menu)
        else:
            parent_menu.addMenu(menu)
    #@+node:tbrown.20101205145115.14820: *3* update_popularity
    def update_popularity(self, tag, keywords):

        if keywords['c'] != self.c:
            return

        c = self.c

        self.popularity[c.p.gnx] = (self.popularity.get(c.p.gnx, [0])[0]+1,
            c.p.h, c.p)
    #@-others
#@-others
#@-leo

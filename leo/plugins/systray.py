#@+leo-ver=5-thin
#@+node:ville.20110304230157.6513: * @file systray.py
#@+<< docstring >>
#@+node:ville.20110219221839.6550: ** << docstring >>
''' systray
'''
#@-<< docstring >>

__version__ = '0.2'
#@+<< version history >>
#@+node:ville.20110219221839.6551: ** << version history >>
#@@killcolor
#@+at
# 
# 0.1 Functionally complete version
#@-<< version history >>

#@+<< imports >>
#@+node:ville.20110219221839.6552: ** << imports >>
import leo.core.leoGlobals as g

g.assertUi('qt')

from PyQt4 import QtGui, QtCore

# Whatever other imports your plugins uses.
#@-<< imports >>

#@+others
#@+node:ville.20110219221839.6553: ** init
def init ():


    ok = g.app.gui.guiName() == "qt"

    if ok:

        if 0: # Use this if you want to create the commander class before the frame is fully created.
            g.registerHandler('before-create-leo-frame',onCreate)
        else: # Use this if you want to create the commander class after the frame is fully created.
            g.registerHandler('after-create-leo-frame',onCreate)
        createTrayIcon()

        g.plugin_signon(__name__)


    return ok
#@+node:ville.20110219221839.6560: ** createTrayIcon
def createTrayIcon():
    g.trayIconMenu = QtGui.QMenu();
    def new_note():
        c = g.app.commanders()[0]
        c.k.simulateCommand('stickynote-new')

    g.trayIconMenu.addAction("New note",new_note);

    g.trayIcon = QtGui.QSystemTrayIcon();
    g.trayIcon.setContextMenu(g.trayIconMenu);
    g.trayIcon.setIcon(QtGui.QIcon(g.app.leoDir + "/Icons/leoapp32.png"))
    g.trayIcon.setVisible(True)

#@+node:ville.20110219221839.6554: ** onCreate
def onCreate (tag, keys):

    c = keys.get('c')
    if not c: return

    thePluginController = pluginController(c)
#@+node:ville.20110219221839.6555: ** class pluginController
class pluginController:

    #@+others
    #@+node:ville.20110219221839.6556: *3* __init__
    def __init__ (self,c):

        self.c = c



    #@+node:ville.20110219221839.6557: *3* makeButtons
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
    #@+node:ville.20110219221839.6558: *3* clickPrev
    def clickPrev(self):
        c = self.c
        p = c.goPrevVisitedNode()
        # g.trace(p)
        #if p: c.selectPosition(p)

    #@+node:ville.20110219221839.6559: *3* clickNext
    def clickNext(self):
        c = self.c
        p = c.goNextVisitedNode()
        # g.trace(p)
        if p: c.selectPosition(p)
    #@-others
#@-others
#@-leo

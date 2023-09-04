#@+leo-ver=5-thin
#@+node:ville.20110304230157.6513: * @file ../plugins/systray.py
"""systray"""

from leo.core import leoGlobals as g
from leo.core.leoQt import QtGui, QtWidgets
from leo.core.leoQt import QAction, StandardPixmap
#
# Fail fast, right after all imports.
g.assertUi('qt')  # May raise g.UiTypeException, caught by the plugins manager.

#@+others
#@+node:ville.20110219221839.6553: ** init
def init():


    ok = g.app.gui.guiName() == "qt"

    if ok:

        if 0:  # Use this if you want to create the commander class before the frame is fully created.
            g.registerHandler('before-create-leo-frame', onCreate)
        else:  # Use this if you want to create the commander class after the frame is fully created.
            g.registerHandler('after-create-leo-frame', onCreate)
        createTrayIcon()

        g.plugin_signon(__name__)


    return ok
#@+node:ville.20110219221839.6560: ** createTrayIcon
def createTrayIcon():
    g.trayIconMenu = QtWidgets.QMenu()

    def new_note():
        c = g.app.commanders()[0]
        c.doCommandByName('stickynote-new')

    g.trayIconMenu.addAction("New note", new_note)
    g.trayIcon = QtWidgets.QSystemTrayIcon()
    g.trayIcon.setContextMenu(g.trayIconMenu)
    g.trayIcon.setIcon(QtGui.QIcon(g.app.leoDir + "/Icons/leoapp32.png"))
    g.trayIcon.setVisible(True)
#@+node:ville.20110219221839.6554: ** onCreate
def onCreate(tag, keys):

    c = keys.get('c')
    if c:
        pluginController(c)
#@+node:ville.20110219221839.6555: ** class pluginController
class pluginController:

    #@+others
    #@+node:ville.20110219221839.6556: *3* __init__
    def __init__(self, c):

        self.c = c

    #@+node:ville.20110219221839.6557: *3* makeButtons (systray.py)
    def makeButtons(self):
        ib_w = self.c.frame.iconBar.w
        if not ib_w:
            return  # EKR: can be None when unit testing.
        icon_l = ib_w.style().standardIcon(StandardPixmap.SP_ArrowLeft)
        icon_r = ib_w.style().standardIcon(StandardPixmap.SP_ArrowRight)
        # Create the actions.
        act_l = QAction(icon_l, 'prev', ib_w)
        act_r = QAction(icon_r, 'next', ib_w)
        # Use the new commands.
        act_l.triggered.connect(self.clickPrev)
        act_r.triggered.connect(self.clickNext)
        # Don't execute the command twice.
        self.c.frame.iconBar.add(qaction=act_l, command=self.clickPrev)
        self.c.frame.iconBar.add(qaction=act_r, command=self.clickNext)
    #@+node:ville.20110219221839.6558: *3* clickPrev
    def clickPrev(self):

        c = self.c
        c.goPrevVisitedNode()
    #@+node:ville.20110219221839.6559: *3* clickNext
    def clickNext(self):
        c = self.c
        p = c.goNextVisitedNode()
        if p:
            c.selectPosition(p)
    #@-others
#@-others
#@-leo

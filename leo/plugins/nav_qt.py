#@+leo-ver=5-thin
#@+node:ville.20090518182905.5419: * @file nav_qt.py
#@+<< docstring >>
#@+node:ville.20090518182905.5420: ** << docstring >>
'''Adds "Back" and "Forward" buttons (Qt only).

Creates "back" and "forward" buttons on button bar. These navigate
the node history.

This plugin does not need specific setup. If the plugin is loaded, the buttons
will be available. The buttons use the icon specified in the active Qt style

Note it may be practical to put this plugin before mod_scripting.py in 
@enabled-plugins list. That way buttons "back" and "forward" will be placed on
the left side of toolbar.

'''
#@-<< docstring >>
#@+<< imports >>
#@+node:ville.20090518182905.5422: ** << imports >>
import leo.core.leoGlobals as g

# Fail gracefully if the gui is not qt.
g.assertUi('qt')

from leo.core.leoQt import QtWidgets
#@-<< imports >>
controllers = {}
    # keys are c.hash(), values are NavControllers
#@+others
#@+node:ville.20090518182905.5423: ** init
def init ():
    '''Return True if the plugin has loaded successfully.'''
    ok = g.app.gui.guiName() == "qt"
    if ok:
        g.registerHandler(('new','open2'),onCreate)
        g.registerHandler('close-frame', onClose)
        g.plugin_signon(__name__)
    return ok
#@+node:ville.20090518182905.5424: ** onCreate
def onCreate (tag, keys):

    global controllers

    c = keys.get('c')
    if not c: return

    h = c.hash()

    nc = controllers.get(h)
    if not nc:
        controllers [h] = NavController(c)
#@+node:vitalije.20170712192502.1: ** onClose
def onClose(tag, keys):
    global controllers
    c = keys.get('c')
    h = c.hash()
    nc = controllers.get(h)
    if nc:
        nc.removeButtons()
        del controllers[h]
#@+node:ville.20090518182905.5425: ** class NavController
class NavController:

    #@+others
    #@+node:ville.20090518182905.5426: *3* __init__
    def __init__ (self,c):

        self.c = c
        c._prev_next = self
        self._buttons = self.makeButtons()

    #@+node:ville.20090518182905.5427: *3* makeButtons
    def makeButtons(self):

        c = self.c
        w = c.frame.iconBar.w
        if not w:
            return [] # EKR: can be an empty list when unit testing.

        icon_l = w.style().standardIcon(QtWidgets.QStyle.SP_ArrowLeft)
        icon_r = w.style().standardIcon(QtWidgets.QStyle.SP_ArrowRight)

        act_l = QtWidgets.QAction(icon_l,'prev',w)
        act_r = QtWidgets.QAction(icon_r,'next',w)

        # 2011/04/02: Use the new commands.
        act_l.triggered.connect(lambda checked: c.goToPrevHistory())
        act_r.triggered.connect(lambda checked: c.goToNextHistory())

        # 2011/04/02: Don't execute the command twice.
        self.c.frame.iconBar.add(qaction = act_l) #, command = self.clickPrev)
        self.c.frame.iconBar.add(qaction = act_r) #, command = self.clickNext)
        return act_l, act_r
        
    def removeButtons(self):
        for b in self._buttons:
            self.c.frame.iconBar.deleteButton(b)
        self._buttons = []
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo

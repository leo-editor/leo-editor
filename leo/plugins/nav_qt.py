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

import PyQt4.QtGui as QtGui
import PyQt4.QtCore as QtCore
#@-<< imports >>

controllers = {}
    # keys are c.hash(), values are NavControllers

#@+others
#@+node:ville.20090518182905.5423: ** init
def init ():

    ok = g.app.gui.guiName() == "qt"

    if ok:
        g.registerHandler('after-create-leo-frame',onCreate)

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
#@+node:ville.20090518182905.5425: ** class NavController
class NavController:

    #@+others
    #@+node:ville.20090518182905.5426: *3* __init__
    def __init__ (self,c):

        self.c = c
        c._prev_next = self
        
        self.makeButtons()
        
    #@+node:ville.20090518182905.5427: *3* makeButtons
    def makeButtons(self):
        
        c = self.c
        w = c.frame.iconBar.w
        if not w: return # EKR: can be None when unit testing.
        
        icon_l = w.style().standardIcon(QtGui.QStyle.SP_ArrowLeft)
        icon_r = w.style().standardIcon(QtGui.QStyle.SP_ArrowRight)
        
        act_l = QtGui.QAction(icon_l,'prev',w)
        act_r = QtGui.QAction(icon_r,'next',w)
        
        # 2011/04/02: Use the new commands.
        act_l.connect(act_l,QtCore.SIGNAL("triggered()"),c.goToPrevHistory)
        act_r.connect(act_r,QtCore.SIGNAL("triggered()"),c.goToNextHistory)

        # 2011/04/02: Don't execute the command twice.
        self.c.frame.iconBar.add(qaction = act_l) #, command = self.clickPrev)
        self.c.frame.iconBar.add(qaction = act_r) #, command = self.clickNext)
    #@-others
#@-others
#@-leo

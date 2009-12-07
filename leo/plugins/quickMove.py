# coding: utf-8
#@+leo-ver=4-thin
#@+node:tbrown.20070117104409:@thin quickMove.py
#@@first
#@<< docstring >>
#@+node:tbrown.20070117104409.1:<< docstring >>
"""Create buttons to quickly move nodes to other nodes

Adds 'Move/Clone To Last Child Button' and 
'Move/Clone To First Child Button' commands to the Outline menu.

Select a node 'Foo' and then use the 'To Last Child Button' command. The adds a 'to
Foo' button to the button bar. Now select another node and click the 'to Foo'
button. The selected node will be moved or cloned to the last child of the
node 'Foo'.

'To First Child Button' works the same way, except that moved nodes are inserted as the
first child of the target node.

"""
#@nonl
#@-node:tbrown.20070117104409.1:<< docstring >>
#@nl

__version__ = '0.7'
#@<< version history >>
#@+node:tbrown.20070117104409.6:<< version history >>
#@+at
# 0.1 by Terry Brown, 2007-01-12
# 0.2 EKR:
# - Revised docstring.
# - Use positions and position methods rather than vnodes.
# - Use checkMoveWithParentWithWarning.
# - Support undo.
# - Clearer command names.
# 0.3 EKR: Various small mods suggested by Terry.
# 0.4 EKR: Added checkMove method.
# 0.5 EKR: Added c arg to p.visNext & p.visBack.
# 0.6 TNB: Store vnodes rather than positions, vnodes are more durable
# 0.7 TNB: Added "clone to" as well as "move to"
#@-at
#@nonl
#@-node:tbrown.20070117104409.6:<< version history >>
#@nl
#@<< to do >>
#@+node:tbrown.20070117104409.7:<< to do >>
#@+at
# Add append/insert clone/copy flavours, as well as move?
#@-at
#@nonl
#@-node:tbrown.20070117104409.7:<< to do >>
#@nl

#@<< imports >>
#@+node:tbrown.20070117104409.2:<< imports >>
import leo.core.leoGlobals as g
import leo.core.leoPlugins as leoPlugins
from mod_scripting import scriptingController
if g.app.gui.guiName() == "qt":
    # for the right click context menu
    from PyQt4 import QtCore
#@-node:tbrown.20070117104409.2:<< imports >>
#@nl

#@+others
#@+node:tbrown.20070117104409.3:init and onCreate
def init():
    leoPlugins.registerHandler('after-create-leo-frame', onCreate)
    g.plugin_signon(__name__)
    return True

def onCreate(tag, keywords):
    quickMove(keywords['c'])
#@nonl
#@-node:tbrown.20070117104409.3:init and onCreate
#@+node:tbrown.20070117104409.4:class quickMove
class quickMove:

    """quickMove binds to a controller, adds menu entries for
       creating buttons, and creates buttons as needed
    """

    #@    @+others
    #@+node:ekr.20070117113133:ctor
    def __init__(self, c):

        self.table = (
            ("Move To First Child Button",None,self.addToFirstChildButton),
            ("Move To Last Child Button",None,self.addToLastChildButton),
            ("Clone To First Child Button",None,self.cloneToFirstChildButton),
            ("Clone To Last Child Button",None,self.cloneToLastChildButton),
            ("Copy To First Child Button",None,self.copyToFirstChildButton),
            ("Copy To Last Child Button",None,self.copyToLastChildButton),
        )

        self.c = c

        c.frame.menu.createNewMenu('Move', 'Outline')

        c.frame.menu.createMenuItemsFromTable('Move', self.table)

        if g.app.gui.guiName() == "qt":
                g.tree_popup_handlers.append(self.popup)
    #@-node:ekr.20070117113133:ctor
    #@+node:tbrown.20091207120031.5356:dtor
    def __del__(self, c):

        if g.app.gui.guiName() == "qt":
                g.tree_popup_handlers.remove(self.popup)
    #@-node:tbrown.20091207120031.5356:dtor
    #@+node:ekr.20070117113133.2:addTarget/AppendButton
    def addToFirstChildButton (self,event=None):
        self.addButton(first=True)

    def addToLastChildButton (self,event=None):
        self.addButton(first=False)

    def cloneToFirstChildButton (self,event=None):
        self.addButton(first=True, clone=True)

    def cloneToLastChildButton (self,event=None):
        self.addButton(first=False, clone=True)

    def copyToFirstChildButton (self,event=None):
        self.addButton(first=True, copy=True)

    def copyToLastChildButton (self,event=None):
        self.addButton(first=False, copy=True)

    def addButton (self,first,clone=False,copy=False):

        '''Add a button that creates a target for future moves.'''

        c = self.c ; p = c.p
        sc = scriptingController(c)

        mb = quickMoveButton(self,p.copy(),first,clone,copy)

        b = sc.createIconButton(
            text = 'to:' + p.h, # createButton truncates text.
            command = mb.moveCurrentNodeToTarget,
            shortcut = None,
            statusLine = 'Move current node to %s child of %s' % (g.choose(first,'first','last'),p.h),
            bg = "LightBlue"
        )
    #@-node:ekr.20070117113133.2:addTarget/AppendButton
    #@+node:tbrown.20091207102637.11494:popup
    def popup(self, c, p, menu):
        """make popup menu entry"""

        if c != self.c:
            return  # wrong commander

        pathmenu = menu.addMenu("Move")

        for name,dummy,command in self.table:
            a = pathmenu.addAction(name)
            a.connect(a, QtCore.SIGNAL("triggered()"), command)
    #@-node:tbrown.20091207102637.11494:popup
    #@-others
#@nonl
#@-node:tbrown.20070117104409.4:class quickMove
#@+node:tbrown.20070117104409.5:class quickMoveButton
class quickMoveButton:

    """contains target data and function for moving node"""

    #@    @+others
    #@+node:ekr.20070117121326:ctor
    def __init__(self, owner, target, first, clone, copy):

        self.c = owner.c
        self.owner = owner
        self.target = target.v
        self.targetHeadString = target.h
        self.first = first
        self.clone = clone
        self.copy = copy
    #@-node:ekr.20070117121326:ctor
    #@+node:ekr.20070117121326.1:moveCurrentNodeToTarget
    def moveCurrentNodeToTarget(self):

        '''Move the current position to the last child of self.target.'''

        c = self.c
        p = c.p
        p2 = c.vnode2position(self.target)
        u = c.undoer

        if not c.positionExists(p2):
            g.es('Target no longer exists: %s' % self.targetHeadString,color='red')
            return

        if p.v == p2.v or not self.checkMove(p,p2):
            g.es('Invalid move: %s' % (self.targetHeadString),color='red')
            return

        bunch = c.undoer.beforeMoveNode(p)
        p2.expand()
        nxt = p.visNext(c) or p.visBack(c)
        nxt = nxt.v
        # store a vnode instead of position as positions are too easily lost

        if self.clone:
            p = p.clone()

        if not self.copy:
            if self.first:
                p.moveToFirstChildOf(p2)
            else:
                p.moveToLastChildOf(p2)
        else:
            if self.first:
                nd = p2.insertAsNthChild(0)
                p.copyTreeFromSelfTo(nd)
            else:
                nd = p2.insertAsLastChild()
                p.copyTreeFromSelfTo(nd)

        nxt = c.vnode2position(nxt)
        if c.positionExists(nxt):
            c.selectPosition(nxt)
        c.undoer.afterMoveNode(p,'Quick Move', bunch)
        c.redraw()
    #@-node:ekr.20070117121326.1:moveCurrentNodeToTarget
    #@+node:ekr.20070123061606:checkMove
    def checkMove (self,p,p2):

        c = self.c

        for z in p2.parents():
            if z == p:
                return False

        return (
            c.checkMoveWithParentWithWarning (p,p2,warningFlag=False) and
            c.checkMoveWithParentWithWarning (p2,p,warningFlag=False)
        )
    #@-node:ekr.20070123061606:checkMove
    #@-others
#@-node:tbrown.20070117104409.5:class quickMoveButton
#@-others
#@-node:tbrown.20070117104409:@thin quickMove.py
#@-leo

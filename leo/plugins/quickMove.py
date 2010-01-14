# coding: utf-8
#@+leo-ver=4-thin
#@+node:tbrown.20070117104409:@thin quickMove.py
#@@first
#@<< docstring >>
#@+node:tbrown.20070117104409.1:<< docstring >>
"""Create buttons to quickly move nodes to other nodes

Quickly move nodes from around the tree to one or more target nodes.

Adds 'Move/Clone/Copy To Last Child Button' and 'Move/Clone/Copy To First Child
Button' commands to the Move submenu on the Outline menu, and the context menu,
if contextmenu.py is enabled.

Select a node 'Foo' and then use the 'To Last Child Button' command. The adds a
'to Foo' button to the button bar. Now select another node and click the 'to
Foo' button. The selected node will be moved or cloned to the last child of the
node 'Foo'.

'To First Child Button' works the same way, except that moved nodes are inserted
as the first child of the target node.

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

#@<< imports >>
#@+node:tbrown.20070117104409.2:<< imports >>
from types import MethodType

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
class quickMove(object):

    """quickMove binds to a controller, adds menu entries for
       creating buttons, and creates buttons as needed
    """

    flavors = [
      # name   first/last  long  short
      ('move', True, "Move", "to"),
      ('copy', True, "Copy", "to"),
      ('clone', True, "Clone", "to"),
      ('bkmk', True, "Bookmark", "to"),
      ('linkTo', False, "Link", "to"),
      ('linkFrom', False, "Link", "from"),
      ('jump', False, "Jump", "go"),
    ]

    #@    @+others
    #@+node:ekr.20070117113133:ctor
    def __init__(self, c):


        # build methods for this instance
        # could be done at class (module) level, but doing it here
        # yeilds bound methods which are handy for c.frame.menu.createMenuItemsFromTable

        self.imps = []  # implementations, (name,None,function)
        # build functions for this instance
        for name, first_last, long, short in quickMove.flavors:

            if first_last:

                def func(self, event=None):
                    self.addButton(first=True, type_=name)
                func = MethodType(func, self, quickMove)
                setattr(self, 'func_'+name+'_'+short+'_first', func)
                self.imps.append((long+" "+short+" First Child Button", None, func))

                def func(self, event=None):
                    self.addButton(first=False, type_=name)
                setattr(self, 'func_'+name+'_'+short+'_last', 
                    MethodType(func, self, quickMove))
                self.imps.append((long+" "+short+" Last Child Button", None, func))

            else:

                def func(self, event=None):
                    self.addButton(type_=name)
                setattr(self, 'func_'+name+'_'+short, 
                    MethodType(func, self, quickMove))
                self.imps.append((long+" "+short+" Button", None, func))

        self.table = (
            ("Make Buttons Here Permanent",None,self.permanentButton),
            ("Clear Permanent Buttons Here",None,self.clearButton),
        )

        self.c = c

        c.quickMove = self

        self.buttons = []

        for nd in c.all_unique_nodes():
            if 'quickMove' in nd.u:
                for rec in nd.u['quickMove']:
                    if len(rec) != 2:
                        continue  # silently drop old style permanent button
                    first,type_ = rec
                    self.addButton(first,type_,v=nd)

        c.frame.menu.createNewMenu('Move', 'Outline')

        c.frame.menu.createMenuItemsFromTable('Move', self.imps)
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
        self.addButton(first=True, type_="move")

    def addToLastChildButton (self,event=None):
        self.addButton(first=False, type_="move")

    def cloneToFirstChildButton (self,event=None):
        self.addButton(first=True, type_="clone")

    def cloneToLastChildButton (self,event=None):
        self.addButton(first=False, type_="clone")

    def copyToFirstChildButton (self,event=None):
        self.addButton(first=True, type_="copy")

    def copyToLastChildButton (self,event=None):
        self.addButton(first=False, type_="copy")

    def bkmkToFirstChildButton (self,event=None):
        self.addButton(first=True, type_="bkmk")

    def bkmkToLastChildButton (self,event=None):
        self.addButton(first=False, type_="bkmk")

    def linkToButton (self,event=None):
        self.addButton(first=True, type_="link")

    def linkFromButton (self,event=None):
        self.addButton(first=False, type_="link")

    def jumpToButton (self,event=None):
        self.addButton(type_="jump")



    def addButton (self, first, type_="move", v=None):

        '''Add a button that creates a target for future moves.'''

        c = self.c ; p = c.p
        if v is None:
            v = p.v
        sc = scriptingController(c)

        mb = quickMoveButton(self,v,first,type_=type_)

        b = sc.createIconButton(
            text = 'to:' + v.h, # createButton truncates text.
            command = mb.moveCurrentNodeToTarget,
            shortcut = None,
            statusLine = 'Move current node to %s child of %s' % (g.choose(first,'first','last'),v.h),
            bg = "LightBlue"
        )

        self.buttons.append((mb,b))
    #@-node:ekr.20070117113133.2:addTarget/AppendButton
    #@+node:tbrown.20091217114654.5372:permanentButton
    def permanentButton (self,event=None):
        """make buttons on this node permanent

        WARNING: includes buttons deleted"""

        c = self.c ; p = c.p

        qm = c.quickMove

        p.v.u['quickMove'] = []
        for mover, button in qm.buttons:
            if mover.target == p.v:
                p.v.u['quickMove'].append((mover.first, mover.type_))

        g.es('Set {0} buttons'.format(len(p.v.u['quickMove'])))
    #@-node:tbrown.20091217114654.5372:permanentButton
    #@+node:tbrown.20091217114654.5374:clearButton
    def clearButton (self,event=None):
        """clear permanent buttons specs from uA"""
        c = self.c ; p = c.p
        g.es('Removing {0} buttons'.format(len(p.v.u.get('quickMove',[]))))
        if 'quickMove' in p.v.u:
            del p.v.u['quickMove']
    #@-node:tbrown.20091217114654.5374:clearButton
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

#@-node:tbrown.20070117104409.4:class quickMove
#@+node:tbrown.20070117104409.5:class quickMoveButton
class quickMoveButton:

    """contains target data and function for moving node"""

    #@    @+others
    #@+node:ekr.20070117121326:ctor
    def __init__(self, owner, target, first, type_):

        self.c = owner.c
        self.owner = owner
        self.target = target
        self.targetHeadString = target.h
        self.first = first
        self.type_ = type_
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

        if self.type_ == 'clone':
            p = p.clone()

        if self.type_ in ('move', 'clone'):
            if self.first:
                p.moveToFirstChildOf(p2)
            else:
                p.moveToLastChildOf(p2)
        elif self.type_ == 'copy':
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

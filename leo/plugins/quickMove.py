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
import types

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
      ('jump', False, "Jump to", ""),
    ]

    #@    @+others
    #@+node:ekr.20070117113133:ctor
    def __init__(self, c):

        self.table = (
            ("Make Buttons Here Permanent",None,self.permanentButton),
            ("Clear Permanent Buttons Here",None,self.clearButton),
        )

        self.imps = []  # implementations, (func,name,text)
        self.txts = {}  # get short from name, for permanent buttons
                        # filled in below

        # build callables for imp list

        for name, first_last, long, short in quickMove.flavors:

            self.txts[name] = short

            if first_last:
                todo = [(True, 'first'), (False, 'last')]
            else:
                todo = [(None, '')]

            for ftrue, which in todo:

                def func(self=self, ftrue=ftrue, name=name, event=None):
                    self.addButton(first=ftrue, type_=name)
                # func = types.MethodType(func, None, quickMove)
                fname = 'func_'+name+'_'+short+'_' +which
                # setattr(quickMove, fname, func)
                if which:
                    which = " "+which.title()+" Child"
                self.imps.append((func, fname, long+" "+short+which+" Button"))

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

        self.local_imps = []  # make table for createMenuItemsFromTable()
        for func, name, text in self.imps:
            self.local_imps.append((text, None, func))

        self.local_imps.extend(self.table)
        c.frame.menu.createMenuItemsFromTable('Move', self.table)

        if g.app.gui.guiName() == "qt":
                g.tree_popup_handlers.append(self.popup)
    #@-node:ekr.20070117113133:ctor
    #@+node:tbrown.20091207120031.5356:dtor
    def __del__(self, c):

        if g.app.gui.guiName() == "qt":
                g.tree_popup_handlers.remove(self.popup)
    #@-node:tbrown.20091207120031.5356:dtor
    #@+node:ekr.20070117113133.2:addButton
    def addButton (self, first, type_="move", v=None):

        '''Add a button that creates a target for future moves.'''

        c = self.c ; p = c.p
        if v is None:
            v = p.v
        sc = scriptingController(c)

        mb = quickMoveButton(self,v,first,type_=type_)

        txt=self.txts[type_]

        b = sc.createIconButton(
            text = txt + ":" + v.h, # createButton truncates text.
            command = mb.moveCurrentNodeToTarget,
            shortcut = None,
            statusLine = 'Move current node to %s child of %s' % (g.choose(first,'first','last'),v.h),
            bg = "LightBlue"
        )

        if g.app.gui.guiName() == "qt":
            from PyQt4 import QtGui, QtCore
            def cb(event=None, c=c, v=v):
                p = c.vnode2position(v)
                c.selectPosition(p)
                c.redraw()

            but = b.button
            rc = QtGui.QAction('Goto target', but)
            rc.connect(rc, QtCore.SIGNAL("triggered()"), cb)
            but.insertAction(but.actions()[-1], rc)  # insert rc before Remove Button

        self.buttons.append((mb,b))
    #@-node:ekr.20070117113133.2:addButton
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

        for name,dummy,command in self.local_imps:
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

        if self.type_ in ('clone', 'move'):  # all others are always valid?
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

        elif self.type_ == 'bkmk':
            unl = self.computeUNL(p)  # before tree changes
            if self.first:
                nd = p2.insertAsNthChild(0)
            else:
                nd = p2.insertAsLastChild()
            nd.h = p.h
            nd.b = unl

        elif self.type_ == 'copy':
            if self.first:
                nd = p2.insertAsNthChild(0)
                p.copyTreeFromSelfTo(nd)
            else:
                nd = p2.insertAsLastChild()
                p.copyTreeFromSelfTo(nd)

        elif self.type_ in ('linkTo', 'linkFrom'):
            blc = getattr(c, 'backlinkController', None)
            if blc is None:
                g.es("Linking requires backlink.py plugin")
                return
            if self.type_ == 'linkTo':
                blc.vlink(p.v, p2.v)
            else:
                blc.vlink(p2.v, p.v)

        if self.type_ in ('bkmk', 'clone', 'copy', 'move'):
            nxt = c.vnode2position(nxt)
        elif self.type_ == 'jump':
            nxt = c.vnode2position(self.target)
        else:
            nxt = None  # linkTo / linkFrom don't move

        if nxt is not None and c.positionExists(nxt):
            c.selectPosition(nxt)
        c.undoer.afterMoveNode(p,'Quick Move', bunch)
        c.setChanged(True)

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
    #@+node:tbrown.20100114111020.15726:computeUNL
    def computeUNL(self, p):

        p = p.copy()
        heads = []
        while p:
            heads.insert(0, p.h)
            p = p.parent()
        return "@url "+"-->".join(heads)
    #@-node:tbrown.20100114111020.15726:computeUNL
    #@-others
#@-node:tbrown.20070117104409.5:class quickMoveButton
#@-others
#@-node:tbrown.20070117104409:@thin quickMove.py
#@-leo

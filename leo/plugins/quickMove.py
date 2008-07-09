#@+leo-ver=4-thin
#@+node:tbrown.20070117104409:@thin quickMove.py
#@@nowrap

#@<< docstring >>
#@+node:tbrown.20070117104409.1:<< docstring >>
"""Create buttons to quickly move nodes to other nodes

Adds 'To Last Child Button' and 'To First Child Button' commands to the Outline menu.

Select a node 'Foo' and then use the 'To Last Child Button' command. The adds a 'to
Foo' button to the button bar. Now select another node and click the 'to Foo'
button. The selected node will be moved and appended as the last child of the
node 'Foo'.

'To First Child Button' works the same way, except that moved nodes are inserted as the
first child of the target node.

"""
#@nonl
#@-node:tbrown.20070117104409.1:<< docstring >>
#@nl

__version__ = '0.5'
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
        self.c = c

        table = (
            ("Add To First Child Button",None,self.addToFirstChildButton),
            ("Add To Last Child Button",None,self.addToLastChildButton),
        )

        c.frame.menu.createMenuItemsFromTable('Outline', table)
    #@-node:ekr.20070117113133:ctor
    #@+node:ekr.20070117113133.2:addTarget/AppendButton
    def addToFirstChildButton (self,event=None):
        self.addButton(first=True)

    def addToLastChildButton (self,event=None):
        self.addButton(first=False)

    def addButton (self,first):

        '''Add a button that creates a target for future moves.'''

        c = self.c ; p = c.currentPosition()
        sc = scriptingController(c)

        mb = quickMoveButton(self,p.copy(),first)

        b = sc.createIconButton(
            text = 'to-' + p.headString(), # createButton truncates text.
            command = mb.moveCurrentNodeToTarget,
            shortcut = None,
            statusLine = 'Move current node to %s child of %s' % (g.choose(first,'first','last'),p.headString()),
            bg = "LightBlue"
        )
    #@-node:ekr.20070117113133.2:addTarget/AppendButton
    #@-others
#@nonl
#@-node:tbrown.20070117104409.4:class quickMove
#@+node:tbrown.20070117104409.5:class quickMoveButton
class quickMoveButton:

    """contains target data and function for moving node"""

    #@    @+others
    #@+node:ekr.20070117121326:ctor
    def __init__(self, owner, target, first):

        self.c = owner.c
        self.owner = owner
        self.target = target
        self.targetHeadString = target.headString()
        self.first = first
    #@-node:ekr.20070117121326:ctor
    #@+node:ekr.20070117121326.1:moveCurrentNodeToTarget
    def moveCurrentNodeToTarget(self):

        '''Move the current position to the last child of self.target.'''

        c = self.c
        p = c.currentPosition()
        p2 = self.target
        u = c.undoer

        if not c.positionExists(p2):
            for z in c.allNodes_iter():
                if z.v == p:
                    p2 = z
                    break
            else:
                g.es('Target no longer exists: %s' % self.targetHeadString,color='red')
                return

        if p.v.t == p2.v.t or not self.checkMove(p,p2):
            g.es('Invalid move: %s' % (self.targetHeadString),color='red')
            return

        # c.beginUpdate()
        # try:
        bunch = c.undoer.beforeMoveNode(p)
        p2.expand()
        nxt = p.visNext(c) or p.visBack(c)
        if self.first:  p.moveToFirstChildOf(p2)
        else:           p.moveToLastChildOf(p2)
        c.selectPosition(nxt)
        c.undoer.afterMoveNode(p,'Quick Move', bunch)
        # finally:
        c.redraw() # was c.endUpdate()
    #@-node:ekr.20070117121326.1:moveCurrentNodeToTarget
    #@+node:ekr.20070123061606:checkMove
    def checkMove (self,p,p2):

        c = self.c

        for z in p2.parents_iter():
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

# coding: utf-8
#@+leo-ver=5-thin
#@+node:tbrown.20070117104409: * @file quickMove.py
#@@first
#@+<< docstring >>
#@+node:tbrown.20070117104409.1: ** << docstring >>
"""Creates buttons to move nodes quickly to other nodes.

Quickly move/copy/clone nodes from around the tree to one or more target nodes.
It can also create bookmark and tagging functionality in an outline (see `Set
Parent Notes`_ below).

Adds `Move/Clone/Copy To Last Child Button` and `Move/Clone/Copy To First Child
Button`, `Link To/From` and `Jump To` commands to the Move sub-menu on the
Outline menu, and each node's context menu, if the `contextmenu` plugin is enabled.

Select a node ``Foo`` and then use the `Move To Last Child Button` command.
This adds a 'to Foo' button to the button bar. Now select another node and click
the 'to Foo' button. The selected node will be moved to the last child
of the node 'Foo'.

`To First Child Button` works the same way, except that moved nodes are inserted
as the first child of the target node.

`Clone` and `Copy` variants are like `Move`, but clone or copy instead of moving.

`Link` works in conjunction with the `backlink` plugin (and also the
`graphcanvas` plugin) creating a link to/from the target and current nodes.

`Jump` buttons act as bookmarks, taking you to the target node.

You can right click on any of these buttons to access their context menu:

  Goto Target
    takes you to the target node (like a `Jump` button).
  Make Permanent
    makes the button permanent, it will reappear
    when the file is saved / closed / re-opened.
  Set Parent
    allows you to move buttons to sub-menu items of other
    `quickMove` buttons.  This implicitly makes the moved button
    permanent.  It also causes the moved button to lose its context menu.
  Remove Button
    comes from the `mod_scripting` plugin, and just
    removes the button for the rest of the current session.

Set Parent Notes
----------------

`Set Parent` doesn't allow you to do anything with `quickMove` you couldn't
do with a long strip of separate buttons, but it collects quickMove buttons
as sub-menu items of one quickMove button, saving a lot of toolbar space.

Bookmarks 
  Create somewhere out of the way in your outline a node called
  `Bookmarks`. Use the quickMove menu to make it a `Jump To` button, and use its
  context menu to make it permanent. There is no particular reason to jump to
  it, but it needs to be a `quickMove` button of some kind.

  Now, when you want to bookmark a node, first use the quickMove menu to make
  the node a `Jump To` button, and then use the context menu on the button to
  set its parent to your `Bookmarks` button.  It becomes a sub-menu item
  of the `Bookmarks` button.

Tags
  In conjunction with the `backlinks` plugin you can use `quickMove` to
  tag nodes.   The `backlinks` plugin adds a `Links` tab to the `Log pane`.

  Create somewhere in your outline a node called `Tags`. Use the quickMove menu
  to make it a `Jump To` button, and use its context menu to make it permanent.
  Clicking on it will jump you to your tag list. Now create a node under the
  `Tags` node for each tag you want. The node's name will be the tag name, and
  can be changed later. Then use the quickMove menu to make each of these nodes
  a `Link To` button, and then use the context menu on the button to set its
  parent to your `Tags` button. It becomes a sub-menu item of the `Tags` button.

  To see the tags on a node, you need to be looking at the `Links` tab in the
  `Log pane`.  To see all the nodes with a particular tag, click on the `Tags`
  button to jump to the tag list, and select the node which names the tag of
  interest.  The nodes with that tag will be listed in th `Links` tab in the
  `Log pane`.


"""
#@-<< docstring >>

__version__ = '0.7'
#@+<< version history >>
#@+node:tbrown.20070117104409.6: ** << version history >>
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
#@-<< version history >>

#@+<< imports >>
#@+node:tbrown.20070117104409.2: ** << imports >>
import types

import leo.core.leoGlobals as g

from leo.plugins.mod_scripting import scriptingController

if g.app.gui.guiName() == "qt":
    # for the right click context menu, and child items
    from PyQt4 import QtGui, QtCore
    from leo.plugins.attrib_edit import ListDialog
#@-<< imports >>

#@+others
#@+node:tbrown.20070117104409.3: ** init and onCreate
def init():
    g.registerHandler('after-create-leo-frame', onCreate)
    g.plugin_signon(__name__)
    return True

def onCreate(tag, keywords):
    quickMove(keywords['c'])
#@+node:tbrown.20070117104409.4: ** class quickMove
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

    #@+others
    #@+node:ekr.20070117113133: *3* ctor
    def __init__(self, c):

        self.table = (
            ("Make ALL Buttons Here Permanent",None,self.permanentButton),
            ("Clear ALL Permanent Buttons Here",None,self.clearButton),
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

        buttons_todo = []  # get whole list for container buttons

        for nd in c.all_unique_nodes():
            if 'quickMove' in nd.u:
                if 'buttons' in nd.u['quickMove']:  # new dict based storage
                    for rec in nd.u['quickMove']['buttons']:
                        buttons_todo.append(rec.copy())
                        buttons_todo[-1].update({'v':nd})
                else:  # read old list format and convert
                    new_dicts = []
                    for rec in nd.u['quickMove']:
                        if len(rec) != 2:
                            continue  # silently drop even older style permanent button
                        first,type_ = rec
                        buttons_todo.append({'type': type_, 'first': first})
                        new_dicts.append(buttons_todo[-1].copy())
                        buttons_todo[-1].update({'v':nd})
                    nd.u['quickMove'] = {'buttons': new_dicts}

        for i in [b for b in buttons_todo if 'parent' not in b]:
            self.addButton(i['first'], i['type'], v=i['v'])
        for i in reversed([b for b in buttons_todo if 'parent' in b]):
            self.addButton(i['first'], i['type'], v=i['v'], parent=i['parent'])

        c.frame.menu.createNewMenu('Move', 'Outline')

        self.local_imps = []  # make table for createMenuItemsFromTable()
        for func, name, text in self.imps:
            self.local_imps.append((text, None, func))

        self.local_imps.extend(self.table)
        c.frame.menu.createMenuItemsFromTable('Move', self.table)

        if g.app.gui.guiName() == "qt":
                g.tree_popup_handlers.append(self.popup)
    #@+node:tbrown.20091207120031.5356: *3* dtor
    def __del__(self, c):

        if g.app.gui.guiName() == "qt":
                g.tree_popup_handlers.remove(self.popup)
    #@+node:ekr.20070117113133.2: *3* addButton
    def addButton (self, first, type_="move", v=None, parent=None):

        '''Add a button that creates a target for future moves.'''

        c = self.c ; p = c.p
        if v is None:
            v = p.v
        sc = scriptingController(c)

        mb = quickMoveButton(self,v,first,type_=type_)

        txt=self.txts[type_]

        if parent:  # find parent button
            for i in self.buttons:
                if i[0].target.gnx == parent:
                    parent = i[1]
                    break
            else:
                g.es('Move to button parent not found, placing at top level')
                parent = None

        text = txt + ":" + v.h if txt else v.h
        # createButton truncates text.  

        if parent and g.app.gui.guiName() == "qt":
            # see qtGui.py/class leoQtFrame/class qtIconBarClass/setCommandForButton
            pb = parent.button
            rc = QtGui.QAction(text, pb)
            rc.connect(rc, QtCore.SIGNAL("triggered()"), mb.moveCurrentNodeToTarget)
            pb.insertAction(pb.actions()[0], rc)  # insert at top
            b = None
            mb.has_parent = True

            t = QtCore.QString(c.config.getString('mod_scripting_subtext') or '')
            if not unicode(pb.text()).endswith(unicode(t)):
                pb.setText(pb.text()+t)

        else:
            b = sc.createIconButton(
                text,
                command = mb.moveCurrentNodeToTarget,
                shortcut = None,
                statusLine = 'Move current node to %s child of %s' % (g.choose(first,'first','last'),v.h),
                bg = "LightBlue"
            )

            if g.app.gui.guiName() == "qt":

                def cb_goto_target(event=None, c=c, v=v):
                    p = c.vnode2position(v)
                    c.selectPosition(p)
                    c.redraw()

                def cb_set_parent(event=None, c=c, v=v, first=first, type_=type_):
                    c.quickMove.set_parent(v, first, type_)

                def cb_permanent(event=None, c=c, v=v, type_=type_, first=first):
                    c.quickMove.permanentButton(v=v, type_=type_, first=first)

                # def cb_clear(event=None, c=c, v=v):
                #     c.quickMove.clearButton(v)

                for cb, txt in [
                    (cb_goto_target, 'Goto target'),
                    (cb_permanent, 'Make permanent'),
                    # (cb_clear, 'Clear permanent'),
                    (cb_set_parent, 'Set parent'), 
                    ]:
                    but = b.button
                    rc = QtGui.QAction(txt, but)
                    rc.connect(rc, QtCore.SIGNAL("triggered()"), cb)
                    but.insertAction(but.actions()[-1], rc)  # insert rc before Remove Button

        self.buttons.append((mb,b))
    #@+node:tbrown.20091217114654.5372: *3* permanentButton
    def permanentButton (self, event=None, v=None, type_=None, first=None):
        """make buttons on this node permanent

        NOTE: includes buttons deleted"""

        c = self.c
        if not v:
            p = c.p
            v = p.v

        qm = c.quickMove

        if 'quickMove' not in v.u or 'buttons' not in v.u['quickMove']:
            # possibly deleting old style list
            v.u['quickMove'] = {'buttons':[]}

        cnt = 0
        for mover, button in qm.buttons:
            if (mover.target == v and
                (not type_ or mover.type_ == type_) and
                (not first or mover.first == first)):
                cnt += 1
                v.u['quickMove']['buttons'].append(
                    {'first':mover.first, 'type': mover.type_})

        if cnt:
            g.es('Made buttons permanent')
        else:
            g.es("Didn't find button")
    #@+node:tbrown.20091217114654.5374: *3* clearButton
    def clearButton (self, event=None, v=None):
        """clear permanent buttons specs from uA"""
        c = self.c
        if not v:
            p = c.p
            v = p.v

        g.es('Removing buttons - reload to apply')
        if 'quickMove' in v.u:
            del v.u['quickMove']
    #@+node:tbrown.20091207102637.11494: *3* popup
    def popup(self, c, p, menu):
        """make popup menu entry"""

        if c != self.c:
            return  # wrong commander

        pathmenu = menu.addMenu("Move")

        for name,dummy,command in self.local_imps:
            a = pathmenu.addAction(name)
            a.connect(a, QtCore.SIGNAL("triggered()"), command)
    #@+node:tbrown.20100810095317.24878: *3* set_parent
    def set_parent(self, v, first, type_):

        ans = []
        for i in self.buttons:
            if i[0].target is v and i[0].first == first and i[0].type_ == type_:
                ans.append(i)

        if not ans:
            g.es("Didn't find button")
            return
        elif len(ans) != 1:
            g.es("Note: found multiple %s/first=%s buttons, using first"%(type_,first))

        qmb, b = ans[0]

        # need to set 'parent' key in v.u['quickMove'] list item to gnx of parent

        parents = [[i[0].targetHeadString, False, i[0]] for i in self.buttons
                   if i[0] is not qmb and not i[0].has_parent]

        if not parents:
            g.es("No suitable Move buttons found")
            return

        ld = ListDialog(None, 'Pick parent', 'Pick parent', parents)
        ld.exec_()

        if ld.result() == QtGui.QDialog.Rejected:
            return

        for i in parents:
            if i[1]:
                parent = i[2].target
                break
        else:
            return

        if 'quickMove' not in v.u or 'buttons' not in v.u['quickMove']:
            # make button permanent first
            self.permanentButton(v=v, type_=type_, first=first)

        for i in v.u['quickMove']['buttons']:
            if i['type'] == qmb.type_ and i['first'] == qmb.first:
                i['parent'] = parent.gnx
                break
        else:
            v.u['quickMove']['buttons'].append({'type':qmb.type_,
                'first':qmb.first, 'parent':parent.gnx})

        self.addButton(qmb.first, qmb.type_, v=qmb.target, parent=parent.gnx)
        self.buttons = [i for i in self.buttons if i[0] is not qmb]
        print(b)
        b.button.parent().layout().removeWidget(b.button)

        g.es('Moved to parent')
    #@-others

#@+node:tbrown.20070117104409.5: ** class quickMoveButton
class quickMoveButton:

    """contains target data and function for moving node"""

    #@+others
    #@+node:ekr.20070117121326: *3* ctor
    def __init__(self, owner, target, first, type_):

        self.c = owner.c
        self.owner = owner
        self.target = target
        self.targetHeadString = target.h
        self.first = first
        self.type_ = type_
        self.has_parent = False
    #@+node:ekr.20070117121326.1: *3* moveCurrentNodeToTarget
    def moveCurrentNodeToTarget(self):

        '''Move the current position to the last child of self.target.'''

        c = self.c
        p = c.p
        p2 = c.vnode2position(self.target)

        needs_undo = self.type_ != "jump"

        if not c.positionExists(p2):
            g.es('Target no longer exists: %s' % self.targetHeadString,color='red')
            return

        if self.type_ in ('clone', 'move'):  # all others are always valid?
            if p.v == p2.v or not self.checkMove(p,p2):
                g.es('Invalid move: %s' % (self.targetHeadString),color='red')
                return

        if needs_undo:
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

        if needs_undo:
            c.undoer.afterMoveNode(p,'Quick Move', bunch)
            c.setChanged(True)

        c.redraw()
    #@+node:ekr.20070123061606: *3* checkMove
    def checkMove (self,p,p2):

        c = self.c

        for z in p2.parents():
            if z == p:
                return False

        return (
            c.checkMoveWithParentWithWarning (p,p2,warningFlag=False) and
            c.checkMoveWithParentWithWarning (p2,p,warningFlag=False)
        )
    #@+node:tbrown.20100114111020.15726: *3* computeUNL
    def computeUNL(self, p):

        p = p.copy()
        heads = []
        while p:
            heads.insert(0, p.h)
            p = p.parent()
        return "@url "+"-->".join(heads)
    #@-others
#@-others
#@-leo

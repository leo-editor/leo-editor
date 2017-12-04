# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20171124072110.1: * @file ../commands/commanderFindCommands.py
#@@first
'''Clone Find commands that used to be defined in leoCommands.py'''
import leo.core.leoGlobals as g

#@+others
#@+node:ekr.20160224175312.1: ** c.cffm & c.cfam
@g.commander_command('clone-find-all-marked')
@g.commander_command('cfam')
def cloneFindAllMarked(self, event=None):
    '''
    clone-find-all-marked, aka cfam.

    Create an organizer node whose descendants contain clones of all marked
    nodes. The list is *not* flattened: clones appear only once in the
    descendants of the organizer node.
    '''
    c = self
    cloneFindMarkedHelper(c, flatten=False)

@g.commander_command('clone-find-all-flattened-marked')
@g.commander_command('cffm')
def cloneFindAllFlattenedMarked(self, event=None):
    '''
    clone-find-all-flattened-marked, aka cffm.

    Create an organizer node whose direct children are clones of all marked
    nodes. The list is flattened: every cloned node appears as a direct
    child of the organizer node, even if the clone also is a descendant of
    another cloned node.
    '''
    c = self
    cloneFindMarkedHelper(c, flatten=True)
#@+node:ekr.20140828080010.18532: ** c.cloneFindParents
@g.commander_command('clone-find-parents')
def cloneFindParents(self, event=None):
    '''
    Create an organizer node whose direct children are clones of all
    parents of the selected node, which must be a clone.
    '''
    c, u = self, self.undoer
    p = c.p
    if not p: return
    if not p.isCloned():
        g.es('not a clone: %s' % p.h)
        return
    p0 = p.copy()
    undoType = 'Find Clone Parents'
    aList = c.vnode2allPositions(p.v)
    if not aList:
        g.trace('can not happen: no parents')
        return
    # Create the node as the last top-level node.
    # All existing positions remain valid.
    u.beforeChangeGroup(p0, undoType)
    top = c.rootPosition()
    while top.hasNext():
        top.moveToNext()
    b = u.beforeInsertNode(p0)
    found = top.insertAfter()
    found.h = 'Found: parents of %s' % p.h
    u.afterInsertNode(found, 'insert', b)
    seen = []
    for p2 in aList:
        parent = p2.parent()
        if parent and parent.v not in seen:
            seen.append(parent.v)
            b = u.beforeCloneNode(parent)
            clone = parent.clone()
            clone.moveToLastChildOf(found)
            u.afterCloneNode(clone, 'clone', b, dirtyVnodeList=[])
    u.afterChangeGroup(p0, undoType)
    c.selectPosition(found)
    c.setChanged(True)
    c.redraw()
#@+node:ekr.20161022121036.1: ** def cloneFindMarkedHelper
def cloneFindMarkedHelper(c, flatten):
    '''Helper for clone-find-marked commands.'''

    def isMarked(p):
        return p.isMarked()

    c.cloneFindByPredicate(
        generator = c.all_unique_positions,
        predicate = isMarked,
        failMsg = 'No marked nodes',
        flatten = flatten,
        redraw = True,
        undoType = 'clone-find-marked',
    )
    # Unmarking all nodes is convenient.
    for v in c.all_unique_nodes():
        if v.isMarked():
            v.clearMarked()
    found = c.lastTopLevel()
    c.selectPosition(found)
    found.b = '# Found %s marked nodes' % found.numberOfChildren()
#@-others
#@-leo

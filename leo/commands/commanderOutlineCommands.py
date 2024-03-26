#@+leo-ver=5-thin
#@+node:ekr.20171124080430.1: * @file ../commands/commanderOutlineCommands.py
"""Outline commands that used to be defined in leoCommands.py"""
#@+<< commanderOutlineCommands imports & annotations >>
#@+node:ekr.20220826123551.1: ** << commanderOutlineCommands imports & annotations >>
from __future__ import annotations
from collections import defaultdict
from collections.abc import Callable
import xml.etree.ElementTree as ElementTree
import json
import time
from typing import Any, Generator, Optional, TYPE_CHECKING
from leo.core import leoGlobals as g
from leo.core import leoNodes
from leo.core import leoFileCommands

if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoGui import LeoKeyEvent
    from leo.core.leoNodes import Position, VNode
#@-<< commanderOutlineCommands imports & annotations >>

#@+others
#@+node:ekr.20031218072017.1548: ** c_oc.Cut & Paste Outlines
#@+node:ekr.20031218072017.1550: *3* c_oc.copyOutline
@g.commander_command('copy-node')
def copyOutline(self: Cmdr, event: LeoKeyEvent = None) -> str:
    """Copy the selected outline to the clipboard."""
    # Copying an outline has no undo consequences.
    c = self
    c.endEditing()
    s = c.fileCommands.outline_to_clipboard_string()
    g.app.paste_c = c
    if g.app.inBridge:
        return s
    g.app.gui.replaceClipboardWith(s)
    return s
#@+node:ekr.20220314071523.1: *3* c_oc.copyOutlineAsJson & helpers
@g.commander_command('copy-node-as-json')
def copyOutlineAsJSON(self: Cmdr, event: LeoKeyEvent = None) -> Optional[str]:
    """Copy the selected outline as JSON to the clipboard"""
    # Copying an outline has no undo consequences.
    c = self
    c.endEditing()
    s = c.fileCommands.outline_to_clipboard_json_string()
    g.app.paste_c = c
    if g.app.inBridge:
        return s
    g.app.gui.replaceClipboardWith(s)
    return None
#@+node:ekr.20031218072017.1549: *3* c_oc.cutOutline
@g.commander_command('cut-node')
def cutOutline(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """Delete the selected outline and send it to the clipboard."""
    c = self
    if c.canDeleteHeadline():
        c.copyOutline()
        c.deleteOutline(op_name="Cut Node")
        c.recolor()
#@+node:ekr.20031218072017.1551: *3* c_oc.pasteOutline
@g.commander_command('paste-node')
def pasteOutline(
    self: Cmdr,
    event: LeoKeyEvent = None,
    s: str = None,
    undoFlag: bool = True,  # A hack for abbrev.paste_tree.
) -> Optional[Position]:
    """
    Paste an outline into the present outline from the clipboard.
    Nodes do *not* retain their original identify.
    """
    c = self
    if s is None:
        s = g.app.gui.getTextFromClipboard()
    c.endEditing()
    if not s or not c.canPasteOutline(s):
        return None  # This should never happen.
    isLeo = s.lstrip().startswith("{") or g.match(s, 0, g.app.prolog_prefix_string)
    if not isLeo:
        return None
    # Get *position* to be pasted.
    pasted = c.fileCommands.getLeoOutlineFromClipboard(s)
    if not pasted:
        # Leo no longer supports MORE outlines. Use import-MORE-files instead.
        return None
    # Validate.
    errors = c.checkOutline()
    if errors > 0:
        return None
    # Handle the "before" data for undo.
    if undoFlag:
        undoData = c.undoer.beforeInsertNode(c.p,
            pasteAsClone=False,
            copiedBunchList=[],
        )
    # Paste the node into the outline.
    c.selectPosition(pasted)
    pasted.setDirty()
    c.setChanged()
    back = pasted.back()
    if back and back.hasChildren() and back.isExpanded():
        pasted.moveToNthChildOf(back, 0)
    # Finish the command.
    if undoFlag:
        c.undoer.afterInsertNode(pasted, 'Paste Node', undoData)
    c.redraw(pasted)
    c.recolor()
    return pasted
#@+node:EKR.20040610130943: *3* c_oc.pasteOutlineRetainingClones & helpers
@g.commander_command('paste-retaining-clones')
def pasteOutlineRetainingClones(
    self: Cmdr, event: LeoKeyEvent = None, s: str = None,
) -> Optional[Position]:
    """
    Paste an outline into the present outline from the clipboard.
    Nodes *retain* their original identify.
    """
    c = self
    if s is None:
        s = g.app.gui.getTextFromClipboard()
    c.endEditing()
    if not s or not c.canPasteOutline(s):
        return None  # This should never happen.
    # Get *position* to be pasted.
    pasted = c.fileCommands.getLeoOutlineFromClipboardRetainingClones(s)
    if not pasted:
        # Leo no longer supports MORE outlines. Use import-MORE-files instead.
        return None
    # Validate.
    errors = c.checkOutline()
    if errors > 0:
        return None
    # Handle the "before" data for undo.
    if True:  ### undoFlag:
        vnodeInfoDict = computeVnodeInfoDict(c)
        undoData = c.undoer.beforeInsertNode(c.p,
            pasteAsClone=True,
            copiedBunchList=computeCopiedBunchList(c, pasted, vnodeInfoDict),
        )
    # Paste the node into the outline.
    c.selectPosition(pasted)
    pasted.setDirty()
    c.setChanged()
    back = pasted.back()
    if back and back.hasChildren() and back.isExpanded():
        pasted.moveToNthChildOf(back, 0)
        pasted.setDirty()
    # Set dirty bits for ancestors of *all* pasted nodes.
    for p in pasted.self_and_subtree():
        p.setAllAncestorAtFileNodesDirty()
    # Finish the command.
    if True:  ### undoFlag:
        c.undoer.afterInsertNode(pasted, 'Paste As Clone', undoData)
    c.redraw(pasted)
    c.recolor()
    return pasted
#@+node:ekr.20050418084539.2: *4* def computeCopiedBunchList
def computeCopiedBunchList(
    c: Cmdr,
    pasted: Position,
    vnodeInfoDict: dict[VNode, Any],
) -> list[Any]:
    """Create a dict containing only copied vnodes."""
    d = {}
    for p in pasted.self_and_subtree(copy=False):
        d[p.v] = p.v
    aList = []
    for v in vnodeInfoDict:
        if d.get(v):
            bunch = vnodeInfoDict.get(v)
            aList.append(bunch)
    return aList
#@+node:ekr.20050418084539: *4* def computeVnodeInfoDict
def computeVnodeInfoDict(c: Cmdr) -> dict[VNode, Any]:
    """
    We don't know yet which nodes will be affected by the paste, so we remember
    everything. This is expensive, but foolproof.

    The alternative is to try to remember the 'before' values of nodes in the
    FileCommands read logic. Several experiments failed, and the code is very ugly.
    In short, it seems wise to do things the foolproof way.
    """
    d = {}
    for v in c.all_unique_nodes():
        if v not in d:
            d[v] = g.Bunch(v=v, head=v.h, body=v.b)
    return d
#@+node:vitalije.20200529105105.1: *3* c_oc.pasteAsTemplate
@g.commander_command('paste-as-template')
def pasteAsTemplate(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """Paste as template clones only nodes that were already clones"""
    c = self
    p = c.p
    s = g.app.gui.getTextFromClipboard()
    if not s or not c.canPasteOutline(s):
        return  # This should never happen.
    isJson = s.lstrip().startswith("{")

    # Define helpers.
    #@+others
    #@+node:vitalije.20200529112224.1: *4* skip_root
    def skip_root(v: VNode) -> Generator:
        """
        generates v nodes in the outline order
        but skips a subtree of the node with root_gnx
        """
        if v.gnx != root_gnx:
            yield v
            for ch in v.children:
                yield from skip_root(ch)
    #@+node:vitalije.20200529112459.1: *4* translate_gnx
    def translate_gnx(gnx: str) -> str:
        """
        allocates a new gnx for all nodes that
        are not found outside copied tree
        """
        if gnx in outside:
            return gnx
        return g.app.nodeIndices.computeNewIndex()
    #@+node:vitalije.20200529115141.1: *4* viter
    def viter(parent_gnx: str, xv: Any) -> Generator:
        """
        iterates <v> nodes generating tuples:

            (parent_gnx, child_gnx, headline, body)

        skipping the descendants of already seen nodes.
        """

        if not isJson:
            chgnx = xv.attrib.get('t')
        else:
            chgnx = xv.get('gnx')

        b = bodies[chgnx]
        gnx = translation.get(chgnx)
        if gnx in seen:
            yield parent_gnx, gnx, heads.get(gnx), b
        else:
            seen.add(gnx)
            if not isJson:
                h = xv[0].text
            else:
                h = xv.get('vh', '')
            heads[gnx] = h
            yield parent_gnx, gnx, h, b
            if not isJson:
                for xch in xv[1:]:
                    yield from viter(gnx, xch)
            else:
                if xv.get('children'):
                    for xch in xv['children']:
                        yield from viter(gnx, xch)

    #@+node:vitalije.20200529114857.1: *4* getv
    gnx2v = c.fileCommands.gnxDict
    def getv(gnx: str) -> tuple[VNode, bool]:
        """
        returns a pair (vnode, is_new) for the given gnx.
        if node doesn't exist, creates a new one.
        """
        v = gnx2v.get(gnx)
        if v is None:
            return leoNodes.VNode(c, gnx), True
        return v, False
    #@+node:vitalije.20200529115539.1: *4* do_paste (pasteAsTemplate)
    def do_paste(vpar: Any, index: int) -> VNode:
        """
        pastes a new node as a child of vpar at given index
        """
        vpargnx = vpar.gnx
        # the first node is inserted at the given index
        # and the rest are just appended at parents children
        # to achieve this we first create a generator object
        rows = viter(vpargnx, xvelements[0])

        # then we just take first tuple
        pgnx, gnx, h, b = next(rows)

        # create vnode
        v, _ = getv(gnx)
        v.h = h
        v.b = b

        # and finally insert it at the given index
        vpar.children.insert(index, v)
        v.parents.append(vpar)

        pasted = v  # remember the first node as a return value

        # now we iterate the rest of tuples
        for pgnx, gnx, h, b in rows:

            # get or create a child `v`
            v, isNew = getv(gnx)
            if isNew:
                v.h = h
                v.b = b
                ua = uas.get(gnx)
                if ua:
                    v.unknownAttributes = ua
            # get parent node `vpar`
            vpar = getv(pgnx)[0]

            # and link them
            vpar.children.append(v)
            v.parents.append(vpar)

        return pasted
    #@+node:vitalije.20200529120440.1: *4* undoHelper
    def undoHelper() -> None:
        v = vpar.children.pop(index)
        v.parents.remove(vpar)
        c.redraw(bunch.p)
    #@+node:vitalije.20200529120537.1: *4* redoHelper
    def redoHelper() -> None:
        vpar.children.insert(index, pasted)
        pasted.parents.append(vpar)
        c.redraw(newp)
    #@-others

    xvelements: Any
    xtelements: Any
    uas: Any  # Possible bug?

    x = leoFileCommands.FastRead(c, {})

    if not isJson:
        xroot = ElementTree.fromstring(s)
        xvelements = xroot.find('vnodes')  # <v> elements.
        xtelements = xroot.find('tnodes')  # <t> elements.
        bodies, uas = x.scanTnodes(xtelements)
        root_gnx = xvelements[0].attrib.get('t')  # the gnx of copied node
    else:
        xroot = json.loads(s)
        xvelements = xroot.get('vnodes')  # <v> elements.
        xtelements = xroot.get('tnodes')  # <t> elements.
        bodies = x.scanJsonTnodes(xtelements)
        # g.printObj(bodies, tag='bodies/gnx2body')

        def addBody(node: Any) -> None:
            if not hasattr(bodies, node['gnx']):
                bodies[node['gnx']] = ''
            if node.get('children'):
                for child in node['children']:
                    addBody(child)

        # generate bodies for all possible nodes, not just non-empty bodies.
        addBody(xvelements[0])
        uas = defaultdict(dict)
        uas.update(xroot.get('uas', {}))
        root_gnx = xvelements[0].get('gnx')  # the gnx of copied node

    # outside will contain gnxes of nodes that are outside the copied tree
    outside = {x.gnx for x in skip_root(c.hiddenRootNode)}

    # we generate new gnx for each node in the copied tree
    translation = {x: translate_gnx(x) for x in bodies}

    seen = set(outside)  # required for the treatment of local clones inside the copied tree

    heads: dict[str, str] = {}

    bunch = c.undoer.createCommonBunch(p)
    #@+<< prepare destination data >>
    #@+node:vitalije.20200529111500.1: *4* << prepare destination data >>
    # destination data consists of
    #    1. vpar --- parent v node that should receive pasted child
    #    2. index --- at which pasted child will be
    #    3. parStack --- a stack for creating new position of the pasted node
    #
    # the new position will be:  Position(vpar.children[index], index, parStack)
    # but it can't be calculated yet, before actual paste is done
    if p.isExpanded():
        # paste as a first child of current position
        vpar = p.v
        index = 0
        parStack = p.stack + [(p.v, p._childIndex)]
    else:
        # paste after the current position
        parStack = p.stack
        vpar = p.stack[-1][0] if p.stack else c.hiddenRootNode
        index = p._childIndex + 1

    #@-<< prepare destination data >>

    pasted = do_paste(vpar, index)

    newp = leoNodes.Position(pasted, index, parStack)

    bunch.undoHelper = undoHelper
    bunch.redoHelper = redoHelper
    bunch.undoType = 'paste-retaining-outside-clones'

    newp.setDirty()
    c.undoer.pushBead(bunch)
    c.redraw(newp)
#@+node:ekr.20040412060927: ** c_oc.dumpOutline
@g.commander_command('dump-outline')
def dumpOutline(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """ Dump all nodes in the outline."""
    c = self
    seen = {}
    print('')
    print('=' * 40)
    v = c.hiddenRootNode
    v.dump()
    seen[v] = True
    for p in c.all_positions():
        if p.v not in seen:
            seen[p.v] = True
            p.v.dump()
#@+node:ekr.20031218072017.2898: ** c_oc.Expand & contract commands
#@+node:ekr.20031218072017.2900: *3* c_oc.contract-all
@g.commander_command('contract-all')
def contractAllHeadlinesCommand(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """Contract all nodes in the outline."""
    # The helper does all the work.
    c = self
    c.contractAllHeadlines()
    c.redraw()
#@+node:ekr.20080819075811.3: *3* c_oc.contractAllOtherNodes & helper
@g.commander_command('contract-all-other-nodes')
def contractAllOtherNodes(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """
    Contract all nodes except those needed to make the
    presently selected node visible.
    """
    c = self
    leaveOpen = c.p
    for p in c.rootPosition().self_and_siblings():
        contractIfNotCurrent(c, p, leaveOpen)
    c.redraw()
#@+node:ekr.20080819075811.7: *4* def contractIfNotCurrent
def contractIfNotCurrent(c: Cmdr, p: Position, leaveOpen: Any) -> None:
    if p == leaveOpen or not p.isAncestorOf(leaveOpen):
        p.contract()
    for child in p.children():
        if child != leaveOpen and child.isAncestorOf(leaveOpen):
            contractIfNotCurrent(c, child, leaveOpen)
        else:
            for p2 in child.self_and_subtree():
                p2.contract()
#@+node:ekr.20200824130837.1: *3* c_oc.contractAllSubheads (new)
@g.commander_command('contract-all-subheads')
def contractAllSubheads(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """Contract all children of the presently selected node."""
    c, p = self, self.p
    if not p:
        return
    child = p.firstChild()
    c.contractSubtree(p)
    while child:
        c.contractSubtree(child)
        child = child.next()
    c.redraw(p)
#@+node:ekr.20031218072017.2901: *3* c_oc.contractNode
@g.commander_command('contract-node')
def contractNode(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """Contract the presently selected node."""
    c = self
    p = c.p
    c.endEditing()
    p.contract()
    c.redraw_after_contract(p)
    c.selectPosition(p)
#@+node:ekr.20040930064232: *3* c_oc.contractNodeOrGoToParent
@g.commander_command('contract-or-go-left')
def contractNodeOrGoToParent(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """Simulate the left Arrow Key in folder of Windows Explorer."""
    c, cc, p = self, self.chapterController, self.p
    parent = p.parent()
    redraw = False
    # Bug fix: 2016/04/19: test p.v.isExpanded().
    if p.hasChildren() and (p.v.isExpanded() or p.isExpanded()):
        c.contractNode()
    elif parent and parent.isVisible(c):
        # Contract all children first.
        if c.collapse_on_lt_arrow:
            for child in parent.children():
                if child.isExpanded():
                    child.contract()
                    if child.hasChildren():
                        redraw = True
        if cc and cc.inChapter() and parent.h.startswith('@chapter '):
            pass
        else:
            c.goToParent()
    if redraw:
        # A *child* should be collapsed.  Do a *full* redraw.
        c.redraw()
#@+node:ekr.20031218072017.2902: *3* c_oc.contractParent
@g.commander_command('contract-parent')
def contractParent(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """Contract the parent of the presently selected node."""
    c = self
    c.endEditing()
    p = c.p
    parent = p.parent()
    if not parent:
        return
    parent.contract()
    c.redraw_after_contract(p=parent)
#@+node:ekr.20031218072017.2903: *3* c_oc.expandAllHeadlines
@g.commander_command('expand-all')
def expandAllHeadlines(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """Expand all headlines.
    Warning: this can take a long time for large outlines."""
    c = self
    c.endEditing()
    p0 = c.p
    p = c.rootPosition()
    while p:
        c.expandSubtree(p)
        p.moveToNext()
    c.redraw_after_expand(p0)  # Keep focus on original position
    c.expansionLevel = 0  # Reset expansion level.
#@+node:ekr.20031218072017.2904: *3* c_oc.expandAllSubheads
@g.commander_command('expand-all-subheads')
def expandAllSubheads(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """Expand all children of the presently selected node."""
    c, p = self, self.p
    if not p:
        return
    child = p.firstChild()
    c.expandSubtree(p)
    while child:
        c.expandSubtree(child)
        child = child.next()
    c.redraw(p)
#@+node:ekr.20031218072017.2905: *3* c_oc.expandLevel1..9
@g.commander_command('expand-to-level-1')
def expandLevel1(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """Expand the outline to level 1"""
    self.expandToLevel(1)

@g.commander_command('expand-to-level-2')
def expandLevel2(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """Expand the outline to level 2"""
    self.expandToLevel(2)

@g.commander_command('expand-to-level-3')
def expandLevel3(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """Expand the outline to level 3"""
    self.expandToLevel(3)

@g.commander_command('expand-to-level-4')
def expandLevel4(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """Expand the outline to level 4"""
    self.expandToLevel(4)

@g.commander_command('expand-to-level-5')
def expandLevel5(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """Expand the outline to level 5"""
    self.expandToLevel(5)

@g.commander_command('expand-to-level-6')
def expandLevel6(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """Expand the outline to level 6"""
    self.expandToLevel(6)

@g.commander_command('expand-to-level-7')
def expandLevel7(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """Expand the outline to level 7"""
    self.expandToLevel(7)

@g.commander_command('expand-to-level-8')
def expandLevel8(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """Expand the outline to level 8"""
    self.expandToLevel(8)

@g.commander_command('expand-to-level-9')
def expandLevel9(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """Expand the outline to level 9"""
    self.expandToLevel(9)
#@+node:ekr.20031218072017.2906: *3* c_oc.expandNextLevel
@g.commander_command('expand-next-level')
def expandNextLevel(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """
    Increase the expansion level of the outline and
    Expand all nodes at that level or lower.
    """
    c = self
    # Expansion levels are now local to a particular tree.
    if c.expansionNode != c.p:
        c.expansionLevel = 1
        c.expansionNode = c.p.copy()
    self.expandToLevel(c.expansionLevel + 1)
#@+node:ekr.20031218072017.2907: *3* c_oc.expandNode
@g.commander_command('expand-node')
def expandNode(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """Expand the presently selected node."""
    c = self
    p = c.p
    c.endEditing()
    p.expand()
    c.redraw_after_expand(p)
    c.selectPosition(p)
#@+node:ekr.20040930064232.1: *3* c_oc.expandNodeAndGoToFirstChild
@g.commander_command('expand-and-go-right')
def expandNodeAndGoToFirstChild(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """If a node has children, expand it if needed and go to the first child."""
    c, p = self, self.p
    c.endEditing()
    if p.hasChildren():
        if not p.isExpanded():
            c.expandNode()
        c.selectPosition(p.firstChild())
    c.treeFocusHelper()
#@+node:ekr.20171125082744.1: *3* c_oc.expandNodeOrGoToFirstChild
@g.commander_command('expand-or-go-right')
def expandNodeOrGoToFirstChild(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """
    Simulate the Right Arrow Key in folder of Windows Explorer.
    if c.p has no children, do nothing.
    Otherwise, if c.p is expanded, select the first child.
    Otherwise, expand c.p.
    """
    c, p = self, self.p
    c.endEditing()
    if p.hasChildren():
        if p.isExpanded():
            c.redraw_after_expand(p.firstChild())
        else:
            c.expandNode()
#@+node:ekr.20060928062431: *3* c_oc.expandOnlyAncestorsOfNode
@g.commander_command('expand-ancestors-only')
def expandOnlyAncestorsOfNode(
    self: Cmdr, event: LeoKeyEvent = None, p: Position = None,
) -> None:
    """Contract all nodes except ancestors of the selected node."""
    c = self
    level = 1
    if p:
        c.selectPosition(p)  # 2013/12/25
    root = c.p
    for p in c.all_unique_positions():
        p.v.expandedPositions = []
        p.v.contract()
    for p in root.parents():
        p.expand()
        level += 1
    c.expansionLevel = level  # Reset expansion level.
#@+node:ekr.20031218072017.2908: *3* c_oc.expandPrevLevel
@g.commander_command('expand-prev-level')
def expandPrevLevel(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """Decrease the expansion level of the outline and
    Expand all nodes at that level or lower."""
    c = self
    # Expansion levels are now local to a particular tree.
    if c.expansionNode != c.p:
        c.expansionLevel = 1
        c.expansionNode = c.p.copy()
    self.expandToLevel(max(1, c.expansionLevel - 1))
#@+node:ekr.20171124081846.1: ** c_oc.fullCheckOutline
@g.commander_command('check-outline')
def fullCheckOutline(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """Do a full check of the consistency of a .leo file."""
    c = self
    t1 = time.process_time()
    errors = c.checkOutline()
    t2 = time.process_time()
    g.es_print(f"check-outline: {errors} error{g.plural(errors)} in {t2 - t1:4.2f} sec.")
#@+node:ekr.20031218072017.2913: ** c_oc.Goto commands
#@+node:ekr.20071213123942: *3* c_oc.findNextClone
@g.commander_command('find-next-clone')
def findNextClone(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """Select the next cloned node."""
    c, p = self, self.p
    cc = c.chapterController
    if not p:
        return
    if p.isCloned():
        p.moveToThreadNext()
    flag = False
    while p:
        if p.isCloned():
            flag = True
            break
        else:
            p.moveToThreadNext()
    if flag:
        if cc:
            cc.selectChapterByName('main')
        c.selectPosition(p)
        c.redraw_after_select(p)
    else:
        g.blue('no more clones')
#@+node:ekr.20031218072017.1628: *3* c_oc.goNextVisitedNode
@g.commander_command('go-forward')
def goNextVisitedNode(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """Select the next visited node."""
    c = self
    c.nodeHistory.goNext()
#@+node:ekr.20031218072017.1627: *3* c_oc.goPrevVisitedNode
@g.commander_command('go-back')
def goPrevVisitedNode(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """Select the previously visited node."""
    c = self
    c.nodeHistory.goPrev()
#@+node:ekr.20031218072017.2914: *3* c_oc.goToFirstNode
@g.commander_command('goto-first-node')
def goToFirstNode(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """
    Select the first node of the entire outline.
    Or the first visible node if Leo is hoisted or within a chapter.
    """
    c = self
    p = c.rootPosition()
    c.expandOnlyAncestorsOfNode(p=p)
    c.redraw()
#@+node:ekr.20051012092453: *3* c_oc.goToFirstSibling
@g.commander_command('goto-first-sibling')
def goToFirstSibling(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """Select the first sibling of the selected node."""
    c, p = self, self.p
    if p.hasBack():
        while p.hasBack():
            p.moveToBack()
    c.treeSelectHelper(p)
#@+node:ekr.20070615070925: *3* c_oc.goToFirstVisibleNode
@g.commander_command('goto-first-visible-node')
def goToFirstVisibleNode(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """Select the first visible node of the selected chapter or hoist."""
    c = self
    p = c.firstVisible()
    if p:
        if c.sparse_goto_visible:
            c.expandOnlyAncestorsOfNode(p=p)
        else:
            c.treeSelectHelper(p)
        c.redraw()
#@+node:ekr.20031218072017.2915: *3* c_oc.goToLastNode
@g.commander_command('goto-last-node')
def goToLastNode(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """Select the last node in the entire tree."""
    c = self
    p = c.rootPosition()
    while p and p.hasThreadNext():
        p.moveToThreadNext()
    c.expandOnlyAncestorsOfNode(p=p)
    c.redraw()
#@+node:ekr.20051012092847.1: *3* c_oc.goToLastSibling
@g.commander_command('goto-last-sibling')
def goToLastSibling(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """Select the last sibling of the selected node."""
    c, p = self, self.p
    if p.hasNext():
        while p.hasNext():
            p.moveToNext()
    c.treeSelectHelper(p)
#@+node:ekr.20050711153537: *3* c_oc.goToLastVisibleNode
@g.commander_command('goto-last-visible-node')
def goToLastVisibleNode(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """Select the last visible node of selected chapter or hoist."""
    c = self
    p = c.lastVisible()
    if p:
        if c.sparse_goto_visible:
            c.expandOnlyAncestorsOfNode(p=p)
        else:
            c.treeSelectHelper(p)
        c.redraw()
#@+node:ekr.20031218072017.2916: *3* c_oc.goToNextClone
@g.commander_command('goto-next-clone')
def goToNextClone(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """
    Select the next node that is a clone of the selected node.
    If the selected node is not a clone, do find-next-clone.
    """
    c, p = self, self.p
    cc = c.chapterController
    if not p:
        return
    if not p.isCloned():
        c.findNextClone()
        return
    v = p.v
    p.moveToThreadNext()
    wrapped = False
    while 1:
        if p and p.v == v:
            break
        elif p:
            p.moveToThreadNext()
        elif wrapped:
            break
        else:
            wrapped = True
            p = c.rootPosition()
    if p:
        c.expandAllAncestors(p)
        if cc:
            # #252: goto-next clone activate chapter.
            chapter = cc.getSelectedChapter()
            old_name = chapter and chapter.name
            new_name = cc.findChapterNameForPosition(p)
            if new_name != old_name:
                cc.selectChapterByName(new_name)
        # Always do a full redraw.
        c.redraw(p)
    else:
        g.blue('done')
#@+node:ekr.20031218072017.2917: *3* c_oc.goToNextDirtyHeadline
@g.commander_command('goto-next-changed')
def goToNextDirtyHeadline(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """Select the node that is marked as changed."""
    c, p = self, self.p
    if not p:
        return
    p.moveToThreadNext()
    wrapped = False
    while 1:
        if p and p.isDirty():
            break
        elif p:
            p.moveToThreadNext()
        elif wrapped:
            break
        else:
            wrapped = True
            p = c.rootPosition()
    if not p:
        g.blue('done')
    c.treeSelectHelper(p)  # Sets focus.
#@+node:ekr.20031218072017.2918: *3* c_oc.goToNextMarkedHeadline
@g.commander_command('goto-next-marked')
def goToNextMarkedHeadline(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """Select the next marked node."""
    c, p = self, self.p
    if not p:
        return
    p.moveToThreadNext()
    wrapped = False
    while 1:
        if p and p.isMarked():
            break
        elif p:
            p.moveToThreadNext()
        elif wrapped:
            break
        else:
            wrapped = True
            p = c.rootPosition()
    if not p:
        g.blue('done')
    c.treeSelectHelper(p)  # Sets focus.
#@+node:ekr.20031218072017.2919: *3* c_oc.goToNextSibling
@g.commander_command('goto-next-sibling')
def goToNextSibling(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """Select the next sibling of the selected node."""
    c, p = self, self.p
    c.treeSelectHelper(p and p.next())
#@+node:ekr.20031218072017.2920: *3* c_oc.goToParent
@g.commander_command('goto-parent')
def goToParent(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """Select the parent of the selected node."""
    c, p = self, self.p
    c.treeSelectHelper(p and p.parent())
#@+node:ekr.20190211104913.1: *3* c_oc.goToPrevMarkedHeadline
@g.commander_command('goto-prev-marked')
def goToPrevMarkedHeadline(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """Select the previous marked node."""
    c, p = self, self.p
    if not p:
        return
    p.moveToThreadBack()
    wrapped = False
    while 1:
        if p and p.isMarked():
            break
        elif p:
            p.moveToThreadBack()
        elif wrapped:
            break
        else:
            wrapped = True
            p = c.rootPosition()
    if not p:
        g.blue('done')
    c.treeSelectHelper(p)  # Sets focus.
#@+node:ekr.20031218072017.2921: *3* c_oc.goToPrevSibling
@g.commander_command('goto-prev-sibling')
def goToPrevSibling(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """Select the previous sibling of the selected node."""
    c, p = self, self.p
    c.treeSelectHelper(p and p.back())
#@+node:ekr.20031218072017.2993: *3* c_oc.selectThreadBack
@g.commander_command('goto-prev-node')
def selectThreadBack(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """Select the node preceding the selected node in outline order."""
    c, p = self, self.p
    if not p:
        return
    p.moveToThreadBack()
    c.treeSelectHelper(p)
#@+node:ekr.20031218072017.2994: *3* c_oc.selectThreadNext
@g.commander_command('goto-next-node')
def selectThreadNext(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """Select the node following the selected node in outline order."""
    c, p = self, self.p
    if not p:
        return
    p.moveToThreadNext()
    c.treeSelectHelper(p)
#@+node:ekr.20031218072017.2995: *3* c_oc.selectVisBack
@g.commander_command('goto-prev-visible')
def selectVisBack(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """Select the visible node preceding the presently selected node."""
    # This has an up arrow for a control key.
    c, p = self, self.p
    if not p:
        return
    if c.canSelectVisBack():
        p.moveToVisBack(c)
        c.treeSelectHelper(p)
    else:
        c.endEditing()  # 2011/05/28: A special case.
#@+node:ekr.20031218072017.2996: *3* c_oc.selectVisNext
@g.commander_command('goto-next-visible')
def selectVisNext(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """Select the visible node following the presently selected node."""
    c, p = self, self.p
    if not p:
        return
    if c.canSelectVisNext():
        p.moveToVisNext(c)
        c.treeSelectHelper(p)
    else:
        c.endEditing()  # 2011/05/28: A special case.
#@+node:ekr.20031218072017.2028: ** c_oc.hoist/dehoist/clearAllHoists
#@+node:ekr.20120308061112.9865: *3* c_oc.deHoist
@g.commander_command('de-hoist')
@g.commander_command('dehoist')
def dehoist(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """Undo a previous hoist of an outline."""
    c, cc, tag = self, self.chapterController, '@chapter '
    if not c.p or not c.hoistStack:
        return
    # #2718: de-hoisting an @chapter node is equivalent to selecting the main chapter.
    if c.p.h.startswith(tag) or c.hoistStack[-1].p.h.startswith(tag):
        c.hoistStack = []
        cc.selectChapterByName('main')
        return
    bunch = c.hoistStack.pop()
    p = bunch.p
    # Checks 'expanded' property, which was preserved by 'hoist' method
    if bunch.expanded:
        p.expand()
    else:
        p.contract()
    c.setCurrentPosition(p)
    c.redraw()
    c.frame.clearStatusLine()
    c.frame.putStatusLine("De-Hoist: " + p.h)
    g.doHook('hoist-changed', c=c)
#@+node:ekr.20120308061112.9866: *3* c_oc.clearAllHoists
@g.commander_command('clear-all-hoists')
def clearAllHoists(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """Undo a previous hoist of an outline."""
    c = self
    c.hoistStack = []
    c.frame.putStatusLine("Hoists cleared")
    g.doHook('hoist-changed', c=c)
#@+node:ekr.20120308061112.9867: *3* c_oc.hoist
@g.commander_command('hoist')
def hoist(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """Make only the selected outline visible."""
    c, p = self, self.p
    if not p:
        return
    # Don't hoist an @chapter node.
    if c.chapterController and p.h.startswith('@chapter '):
        if not g.unitTesting:
            g.es('can not hoist an @chapter node.', color='blue')
        return
    # Remember the expansion state.
    bunch = g.Bunch(p=p.copy(), expanded=p.isExpanded())
    c.hoistStack.append(bunch)
    p.expand()
    c.redraw(p)
    c.frame.clearStatusLine()
    c.frame.putStatusLine("Hoist: " + p.h)
    g.doHook('hoist-changed', c=c)
#@+node:ekr.20031218072017.1759: ** c_oc.Insert, Delete & Clone commands
#@+node:ekr.20031218072017.1762: *3* c_oc.clone
@g.commander_command('clone-node')
def clone(self: Cmdr, event: LeoKeyEvent = None) -> Optional[Position]:
    """Create a clone of the selected outline."""
    c, p, u = self, self.p, self.undoer
    if not p:
        return None
    undoData = c.undoer.beforeCloneNode(p)
    c.endEditing()  # Capture any changes to the headline.
    clone = p.clone()
    clone.setDirty()
    c.setChanged()
    if c.checkOutline() == 0:
        u.afterCloneNode(clone, 'Clone Node', undoData)
        c.redraw(clone)
        c.treeWantsFocus()
        return clone  # For mod_labels and chapters plugins.
    clone.doDelete()
    c.setCurrentPosition(p)
    return None
#@+node:ekr.20150630152607.1: *3* c_oc.cloneToAtSpot
@g.commander_command('clone-to-at-spot')
def cloneToAtSpot(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """
    Create a clone of the selected node and move it to the last @spot node
    of the outline. Create the @spot node if necessary.
    """
    c, p, u = self, self.p, self.undoer
    if not p:
        return
    # 2015/12/27: fix bug 220: do not allow clone-to-at-spot on @spot node.
    if p.h.startswith('@spot'):
        g.es("can not clone @spot node", color='red')
        return
    last_spot = None
    for p2 in c.all_positions():
        if g.match_word(p2.h, 0, '@spot'):
            last_spot = p2.copy()
    if not last_spot:
        last = c.lastTopLevel()
        last_spot = last.insertAfter()
        last_spot.h = '@spot'
    undoData = c.undoer.beforeCloneNode(p)
    c.endEditing()  # Capture any changes to the headline.
    clone = p.copy()
    clone._linkAsNthChild(last_spot, n=last_spot.numberOfChildren())
    clone.setDirty()
    c.setChanged()
    if c.checkOutline() == 0:
        u.afterCloneNode(clone, 'Clone Node', undoData)
        c.contractAllHeadlines()
        c.redraw(clone)
    else:
        clone.doDelete()
        c.setCurrentPosition(p)
#@+node:ekr.20141023154408.5: *3* c_oc.cloneToLastNode
@g.commander_command('clone-node-to-last-node')
def cloneToLastNode(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """
    Clone the selected node and move it to the last node.
    Do *not* change the selected node.
    """
    c, p, u = self, self.p, self.undoer
    if not p:
        return
    prev = p.copy()
    undoData = c.undoer.beforeCloneNode(p)
    c.endEditing()  # Capture any changes to the headline.
    clone = p.clone()
    last = c.rootPosition()
    while last and last.hasNext():
        last.moveToNext()
    clone.moveAfter(last)
    clone.setDirty()
    c.setChanged()
    u.afterCloneNode(clone, 'Clone Node To Last', undoData)
    c.redraw(prev)
    # return clone # For mod_labels and chapters plugins.
#@+node:ekr.20031218072017.1193: *3* c_oc.deleteOutline
@g.commander_command('delete-node')
def deleteOutline(self: Cmdr, event: LeoKeyEvent = None, op_name: str = "Delete Node") -> None:
    """Deletes the selected outline."""
    c, u = self, self.undoer
    p = c.p
    if not p:
        return
    c.endEditing()  # Make sure we capture the headline for Undo.
    if False:  # c.config.getBool('select-next-after-delete'):
        # #721: Optionally select next node after delete.
        if p.hasVisNext(c):
            newNode = p.visNext(c)
        elif p.hasParent():
            newNode = p.parent()
        else:
            newNode = p.back()  # _not_ p.visBack(): we are at the top level.
    else:
        # Legacy: select previous node if possible.
        if p.hasVisBack(c):
            newNode = p.visBack(c)
        else:
            newNode = p.next()  # _not_ p.visNext(): we are at the top level.
    if not newNode:
        return
    undoData = u.beforeDeleteNode(p)
    p.setDirty()
    p.doDelete(newNode)
    c.setChanged()
    u.afterDeleteNode(newNode, op_name, undoData)
    c.redraw(newNode)
    c.checkOutline()
#@+node:ekr.20071005173203.1: *3* c_oc.insertChild
@g.commander_command('insert-child')
def insertChild(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """Insert a node after the presently selected node."""
    c = self
    return c.insertHeadline(event=event, op_name='Insert Child', as_child=True)
#@+node:ekr.20031218072017.1761: *3* c_oc.insertHeadline (insert-*)
@g.commander_command('insert-node')
def insertHeadline(
    self: Cmdr, event:
    LeoKeyEvent = None,
    op_name: str = "Insert Node",
    as_child: bool = False,
) -> Optional[Position]:
    """
    If c.p is expanded, insert a new node as the first or last child of c.p,
    depending on @bool insert-new-nodes-at-end.

    If c.p is not expanded, insert a new node after c.p.
    """
    c = self
    # Fix #600.
    return insertHeadlineHelper(c, event=event, as_child=as_child, op_name=op_name)

@g.commander_command('insert-as-first-child')
def insertNodeAsFirstChild(self: Cmdr, event: LeoKeyEvent = None) -> Optional[Position]:
    """Insert a node as the first child of the previous node."""
    c = self
    return insertHeadlineHelper(c, event=event, as_first_child=True)

@g.commander_command('insert-as-last-child')
def insertNodeAsLastChild(self: Cmdr, event: LeoKeyEvent = None) -> Optional[Position]:
    """Insert a node as the last child of the previous node."""
    c = self
    return insertHeadlineHelper(c, event=event, as_last_child=True)
#@+node:ekr.20171124091846.1: *4* function: insertHeadlineHelper
def insertHeadlineHelper(
    c: Cmdr,
    event: LeoKeyEvent = None,
    op_name: str = "Insert Node",
    as_child: bool = False,
    as_first_child: bool = False,
    as_last_child: bool = False,
) -> Optional[Position]:
    """Insert a node after the presently selected node."""
    u = c.undoer
    current = c.p
    if not current:
        return None
    c.endEditing()
    undoData = c.undoer.beforeInsertNode(current)
    if as_first_child:
        p = current.insertAsNthChild(0)
    elif as_last_child:
        p = current.insertAsLastChild()
    elif (
        as_child or
        (current.hasChildren() and current.isExpanded()) or
        (c.hoistStack and current == c.hoistStack[-1].p)
    ):
        # Make sure the new node is visible when hoisting.
        if c.config.getBool('insert-new-nodes-at-end'):
            p = current.insertAsLastChild()
        else:
            p = current.insertAsNthChild(0)
    else:
        p = current.insertAfter()
    g.doHook('create-node', c=c, p=p)
    p.setDirty()
    c.setChanged()
    u.afterInsertNode(p, op_name, undoData)
    c.redrawAndEdit(p, selectAll=True)
    return p
#@+node:ekr.20130922133218.11540: *3* c_oc.insertHeadlineBefore
@g.commander_command('insert-node-before')
def insertHeadlineBefore(self: Cmdr, event: LeoKeyEvent = None) -> Optional[Position]:
    """Insert a node before the presently selected node."""
    c, current, u = self, self.p, self.undoer
    op_name = 'Insert Node Before'
    if not current:
        return None
    # Can not insert before the base of a hoist.
    if c.hoistStack and current == c.hoistStack[-1].p:
        g.warning('can not insert a node before the base of a hoist')
        return None
    c.endEditing()
    undoData = u.beforeInsertNode(current)
    p = current.insertBefore()
    g.doHook('create-node', c=c, p=p)
    p.setDirty()
    c.setChanged()
    u.afterInsertNode(p, op_name, undoData)
    c.redrawAndEdit(p, selectAll=True)
    return p
#@+node:ekr.20031218072017.2922: ** c_oc.Mark commands
#@+node:ekr.20090905110447.6098: *3* c_oc.cloneMarked
@g.commander_command('clone-marked-nodes')
def cloneMarked(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """Clone all marked nodes as children of a new node."""
    c, u = self, self.undoer
    p1 = c.p.copy()
    # Create a new node to hold clones.
    parent = p1.insertAfter()
    parent.h = 'Clones of marked nodes'
    cloned, n, p = [], 0, c.rootPosition()
    while p:
        # Careful: don't clone already-cloned nodes.
        if p == parent:
            p.moveToNodeAfterTree()
        elif p.isMarked() and p.v not in cloned:
            cloned.append(p.v)
            if 0:  # old code
                # Calling p.clone would cause problems
                p.clone().moveToLastChildOf(parent)
            else:  # New code.
                # Create the clone directly as a child of parent.
                p2 = p.copy()
                n = parent.numberOfChildren()
                p2._linkAsNthChild(parent, n)
            p.moveToNodeAfterTree()
            n += 1
        else:
            p.moveToThreadNext()
    if n:
        c.setChanged()
        parent.expand()
        c.selectPosition(parent)
        u.afterCloneMarkedNodes(p1)
    else:
        parent.doDelete()
        c.selectPosition(p1)
    if not g.unitTesting:
        g.blue(f"cloned {n} nodes")
    c.redraw()
#@+node:ekr.20160502090456.1: *3* c_oc.copyMarked
@g.commander_command('copy-marked-nodes')
def copyMarked(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """Copy all marked nodes as children of a new node."""
    c, u = self, self.undoer
    p1 = c.p.copy()
    # Create a new node to hold clones.
    parent = p1.insertAfter()
    parent.h = 'Copies of marked nodes'
    copied, n, p = [], 0, c.rootPosition()
    while p:
        # Careful: don't clone already-cloned nodes.
        if p == parent:
            p.moveToNodeAfterTree()
        elif p.isMarked() and p.v not in copied:
            copied.append(p.v)
            p2 = p.copyWithNewVnodes(copyMarked=True)
            p2._linkAsNthChild(parent, n)
            p.moveToNodeAfterTree()
            n += 1
        else:
            p.moveToThreadNext()
    if n:
        c.setChanged()
        parent.expand()
        c.selectPosition(parent)
        u.afterCopyMarkedNodes(p1)
    else:
        parent.doDelete()
        c.selectPosition(p1)
    if not g.unitTesting:
        g.blue(f"copied {n} nodes")
    c.redraw()
#@+node:ekr.20111005081134.15540: *3* c_oc.deleteMarked
@g.commander_command('delete-marked-nodes')
def deleteMarked(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """Delete all marked nodes."""
    c, u = self, self.undoer
    p1 = c.p.copy()
    undo_data, p = [], c.rootPosition()
    while p:
        if p.isMarked():
            undo_data.append(p.copy())
            next = p.positionAfterDeletedTree()
            p.doDelete()
            p = next
        else:
            p.moveToThreadNext()
    if undo_data:
        u.afterDeleteMarkedNodes(undo_data, p1)
        if not g.unitTesting:
            g.blue(f"deleted {len(undo_data)} nodes")
        c.setChanged()
    # Don't even *think* about restoring the old position.
    c.contractAllHeadlines()
    c.redraw(c.rootPosition())
#@+node:ekr.20111005081134.15539: *3* c_oc.moveMarked & helper
@g.commander_command('move-marked-nodes')
def moveMarked(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """
    Move all marked nodes as children of a new node.
    This command is not undoable.
    Consider using clone-marked-nodes, followed by copy/paste instead.
    """
    c = self
    p1 = c.p.copy()
    # Check for marks.
    for v in c.all_unique_nodes():
        if v.isMarked():
            break
    else:
        g.warning('no marked nodes')
        return
    result = g.app.gui.runAskYesNoDialog(c,
        'Move Marked Nodes?',
        message='move-marked-nodes is not undoable\nProceed?',
    )
    if result == 'no':
        return
    # Create a new *root* node to hold the moved nodes.
    # This node's position remains stable while other nodes move.
    parent = createMoveMarkedNode(c)
    assert not parent.isMarked()
    moved = []
    p = c.rootPosition()
    while p:
        assert parent == c.rootPosition()
        # Careful: don't move already-moved nodes.
        if p.isMarked() and not parent.isAncestorOf(p):
            moved.append(p.copy())
            next = p.positionAfterDeletedTree()
            p.moveToLastChildOf(parent)  # This does not change parent's position.
            p = next
        else:
            p.moveToThreadNext()
    if moved:
        # Find a position p2 outside of parent's tree with p2.v == p1.v.
        # Such a position may not exist.
        p2 = c.rootPosition()
        while p2:
            if p2 == parent:
                p2.moveToNodeAfterTree()
            elif p2.v == p1.v:
                break
            else:
                p2.moveToThreadNext()
        else:
            # Not found.  Move to last top-level.
            p2 = c.lastTopLevel()
        parent.moveAfter(p2)
        # u.afterMoveMarkedNodes(moved, p1)
        if not g.unitTesting:
            g.blue(f"moved {len(moved)} nodes")
        c.setChanged()
    # Calling c.contractAllHeadlines() causes problems when in a chapter.
    c.redraw(parent)
#@+node:ekr.20111005081134.15543: *4* def createMoveMarkedNode
def createMoveMarkedNode(c: Cmdr) -> Position:
    oldRoot = c.rootPosition()
    p = oldRoot.insertAfter()
    p.h = 'Moved marked nodes'
    p.moveToRoot()
    return p
#@+node:ekr.20031218072017.2923: *3* c_oc.markChangedHeadlines
@g.commander_command('mark-changed-items')
def markChangedHeadlines(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """Mark all nodes that have been changed."""
    c, current, u = self, self.p, self.undoer
    undoType = 'Mark Changed'
    c.endEditing()
    changed = False
    for p in c.all_unique_positions():
        if p.isDirty() and not p.isMarked():
            if not changed:
                u.beforeChangeGroup(current, undoType)
            changed = True
            bunch = u.beforeMark(p, undoType)
            # c.setMarked calls a hook.
            c.setMarked(p)
            p.setDirty()
            c.setChanged()
            u.afterMark(p, undoType, bunch)
    if changed:
        u.afterChangeGroup(current, undoType)
    if not g.unitTesting:
        g.blue('done')
#@+node:ekr.20031218072017.2924: *3* c_oc.markChangedRoots
def markChangedRoots(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """Mark all changed @root nodes."""
    c, current, u = self, self.p, self.undoer
    undoType = 'Mark Changed'
    c.endEditing()
    changed = False
    for p in c.all_unique_positions():
        if p.isDirty() and not p.isMarked():
            s = p.b
            flag, i = g.is_special(s, "@root")
            if flag:
                if not changed:
                    u.beforeChangeGroup(current, undoType)
                changed = True
                bunch = u.beforeMark(p, undoType)
                c.setMarked(p)  # Calls a hook.
                p.setDirty()
                c.setChanged()
                u.afterMark(p, undoType, bunch)
    if changed:
        u.afterChangeGroup(current, undoType)
    if not g.unitTesting:
        g.blue('done')
#@+node:ekr.20031218072017.2928: *3* c_oc.markHeadline
@g.commander_command('mark')  # Compatibility
@g.commander_command('toggle-mark')
def markHeadline(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """Toggle the mark of the selected node."""
    c, p, u = self, self.p, self.undoer
    if not p:
        return
    c.endEditing()
    undoType = 'Unmark' if p.isMarked() else 'Mark'
    bunch = u.beforeMark(p, undoType)
    # c.set/clearMarked call a hook.
    if p.isMarked():
        c.clearMarked(p)
    else:
        c.setMarked(p)
    p.setDirty()
    c.setChanged()
    u.afterMark(p, undoType, bunch)
#@+node:ekr.20031218072017.2929: *3* c_oc.markSubheads
@g.commander_command('mark-subheads')
def markSubheads(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """Mark all children of the selected node as changed."""
    c, current, u = self, self.p, self.undoer
    undoType = 'Mark Subheads'
    if not current:
        return
    c.endEditing()
    changed = False
    for p in current.children():
        if not p.isMarked():
            if not changed:
                u.beforeChangeGroup(current, undoType)
            changed = True
            bunch = u.beforeMark(p, undoType)
            c.setMarked(p)  # Calls a hook.
            p.setDirty()
            c.setChanged()
            u.afterMark(p, undoType, bunch)
    if changed:
        u.afterChangeGroup(current, undoType)
#@+node:ekr.20031218072017.2930: *3* c_oc.unmarkAll
@g.commander_command('unmark-all')
def unmarkAll(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """Unmark all nodes in the entire outline."""
    c, current, u = self, self.p, self.undoer
    undoType = 'Unmark All'
    if not current:
        return
    c.endEditing()
    changed = False
    p = None  # To keep pylint happy.
    for p in c.all_unique_positions():
        if p.isMarked():
            if not changed:
                u.beforeChangeGroup(current, undoType)
            bunch = u.beforeMark(p, undoType)
            # c.clearMarked(p) # Very slow: calls a hook.
            p.v.clearMarked()
            p.setDirty()
            u.afterMark(p, undoType, bunch)
            changed = True
    if changed:
        g.doHook("clear-all-marks", c=c, p=p)
        c.setChanged()
        u.afterChangeGroup(current, undoType)
#@+node:ekr.20031218072017.1766: ** c_oc.Move commands
#@+node:ekr.20031218072017.1767: *3* c_oc.demote
@g.commander_command('demote')
def demote(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """Make all following siblings children of the selected node."""
    c, p, u = self, self.p, self.undoer
    if not p or not p.hasNext():
        c.treeFocusHelper()
        return
    # Make sure all the moves will be valid.
    next = p.next()
    while next:
        if not c.checkMoveWithParentWithWarning(next, p, True):
            c.treeFocusHelper()
            return
        next.moveToNext()
    c.endEditing()
    parent_v = p._parentVnode()
    n = p.childIndex()
    followingSibs = parent_v.children[n + 1 :]
    # Remove the moved nodes from the parent's children.
    parent_v.children = parent_v.children[: n + 1]
    # Add the moved nodes to p's children
    p.v.children.extend(followingSibs)
    # Adjust the parent links in the moved nodes.
    # There is no need to adjust descendant links.
    for child in followingSibs:
        child.parents.remove(parent_v)
        child.parents.append(p.v)
    p.expand()
    p.setDirty()
    c.setChanged()
    u.afterDemote(p, followingSibs)
    c.redraw(p)
    c.updateSyntaxColorer(p)  # Moving can change syntax coloring.
#@+node:ekr.20031218072017.1768: *3* c_oc.moveOutlineDown
@g.commander_command('move-outline-down')
def moveOutlineDown(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """Move the selected node down."""
    # Moving down is more tricky than moving up because we can't
    # move p to be a child of itself.
    #
    # An important optimization:
    # we don't have to call checkMoveWithParentWithWarning() if the parent of
    # the moved node remains the same.
    c, p, u = self, self.p, self.undoer
    if not p:
        return
    if not c.canMoveOutlineDown():
        if c.hoistStack:
            cantMoveMessage(c)
        c.treeFocusHelper()
        return
    parent = p.parent()
    next = p.visNext(c)
    while next and p.isAncestorOf(next):
        next = next.visNext(c)
    if not next:
        if c.hoistStack:
            cantMoveMessage(c)
        c.treeFocusHelper()
        return
    c.endEditing()
    undoData = u.beforeMoveNode(p)
    #@+<< Move p down & set moved if successful >>
    #@+node:ekr.20031218072017.1769: *4* << Move p down & set moved if successful >>
    if next.hasChildren() and next.isExpanded():
        # Attempt to move p to the first child of next.
        moved = c.checkMoveWithParentWithWarning(p, next, True)
        if moved:
            p.setDirty()
            p.moveToNthChildOf(next, 0)
    else:
        # Attempt to move p after next.
        moved = c.checkMoveWithParentWithWarning(p, next.parent(), True)
        if moved:
            p.setDirty()
            p.moveAfter(next)
    # Patch by nh2: 0004-Add-bool-collapse_nodes_after_move-option.patch
    if (
        c.collapse_nodes_after_move
        and moved and c.sparse_move
        and parent and not parent.isAncestorOf(p)
    ):
        # New in Leo 4.4.2: contract the old parent if it is no longer the parent of p.
        parent.contract()
    #@-<< Move p down & set moved if successful >>
    if moved:
        p.setDirty()
        c.setChanged()
        u.afterMoveNode(p, 'Move Down', undoData)
    c.redraw(p)
    c.updateSyntaxColorer(p)  # Moving can change syntax coloring.
#@+node:ekr.20031218072017.1770: *3* c_oc.moveOutlineLeft
@g.commander_command('move-outline-left')
def moveOutlineLeft(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """Move the selected node left if possible."""
    c, p, u = self, self.p, self.undoer
    if not p:
        return
    if not c.canMoveOutlineLeft():
        if c.hoistStack:
            cantMoveMessage(c)
        c.treeFocusHelper()
        return
    if not p.hasParent():
        c.treeFocusHelper()
        return
    parent = p.parent()
    c.endEditing()
    undoData = u.beforeMoveNode(p)
    p.setDirty()
    p.moveAfter(parent)
    p.setDirty()
    c.setChanged()
    u.afterMoveNode(p, 'Move Left', undoData)
    # Patch by nh2: 0004-Add-bool-collapse_nodes_after_move-option.patch
    if c.collapse_nodes_after_move and c.sparse_move:  # New in Leo 4.4.2
        parent.contract()
    c.redraw(p)
    c.recolor()  # Moving can change syntax coloring.
#@+node:ekr.20031218072017.1771: *3* c_oc.moveOutlineRight
@g.commander_command('move-outline-right')
def moveOutlineRight(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """Move the selected node right if possible."""
    c, p, u = self, self.p, self.undoer
    if not p:
        return
    if not c.canMoveOutlineRight():  # 11/4/03: Support for hoist.
        if c.hoistStack:
            cantMoveMessage(c)
        c.treeFocusHelper()
        return
    back = p.back()
    if not back:
        c.treeFocusHelper()
        return
    if not c.checkMoveWithParentWithWarning(p, back, True):
        c.treeFocusHelper()
        return
    c.endEditing()
    undoData = u.beforeMoveNode(p)
    p.setDirty()
    n = back.numberOfChildren()
    p.moveToNthChildOf(back, n)
    p.setDirty()
    c.setChanged()  # #2036.
    u.afterMoveNode(p, 'Move Right', undoData)
    c.redraw(p)
    c.recolor()
#@+node:ekr.20031218072017.1772: *3* c_oc.moveOutlineUp
@g.commander_command('move-outline-up')
def moveOutlineUp(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """Move the selected node up if possible."""
    c, p, u = self, self.p, self.undoer
    if not p:
        return
    if not c.canMoveOutlineUp():  # Support for hoist.
        if c.hoistStack:
            cantMoveMessage(c)
        c.treeFocusHelper()
        return
    back = p.visBack(c)
    if not back:
        return
    back2 = back.visBack(c)
    c.endEditing()
    undoData = u.beforeMoveNode(p)
    moved = False
    #@+<< Move p up >>
    #@+node:ekr.20031218072017.1773: *4* << Move p up >>
    parent = p.parent()
    if not back2:
        if c.hoistStack:  # hoist or chapter.
            limit, limitIsVisible = c.visLimit()
            assert limit
            if limitIsVisible:
                # canMoveOutlineUp should have caught this.
                g.trace('can not happen. In hoist')
            else:
                moved = True
                p.setDirty()
                p.moveToFirstChildOf(limit)
        else:
            # p will be the new root node
            p.setDirty()
            p.moveToRoot()
            moved = True
    elif back2.hasChildren() and back2.isExpanded():
        if c.checkMoveWithParentWithWarning(p, back2, True):
            moved = True
            p.setDirty()
            p.moveToNthChildOf(back2, 0)
    else:
        if c.checkMoveWithParentWithWarning(p, back2.parent(), True):
            moved = True
            p.setDirty()
            p.moveAfter(back2)
    # Patch by nh2: 0004-Add-bool-collapse_nodes_after_move-option.patch
    if (
        c.collapse_nodes_after_move
        and moved and c.sparse_move
        and parent and not parent.isAncestorOf(p)
    ):
        # New in Leo 4.4.2: contract the old parent if it is no longer the parent of p.
        parent.contract()
    #@-<< Move p up >>
    if moved:
        p.setDirty()
        c.setChanged()
        u.afterMoveNode(p, 'Move Up', undoData)
    c.redraw(p)
    c.updateSyntaxColorer(p)  # Moving can change syntax coloring.
#@+node:ekr.20230902051130.1: *3* c_oc.moveOutlineToFirstChild
@g.commander_command('move-outline-to-first-child')
def moveOutlineToFirstChild(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """
    Move the selected node so that it is the first child of its parent.

    Do nothing if a hoist is in effect.
    """
    c, p, u = self, self.p, self.undoer
    if not p:
        return
    if c.hoistStack:
        return
    if not p.hasBack():
        return
    parent = p.parent()
    if not parent:
        return
    c.endEditing()
    undoData = u.beforeMoveNode(p)
    p.moveToNthChildOf(p.parent(), 0)
    p.setDirty()
    c.setChanged()
    u.afterMoveNode(p, 'Move To First Child', undoData)
    c.redraw(p)
#@+node:ekr.20230902051833.1: *3* c_oc.moveOutlineToLastChild
@g.commander_command('move-outline-to-last-child')
def moveOutlineToLastChild(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """
    Move the selected node so that it is the last child of its parent.

    Do nothing if a hoist is in effect.
    """
    c, p, u = self, self.p, self.undoer
    if not p:
        return
    if c.hoistStack:
        return
    if not p.hasNext():
        return
    parent = p.parent()
    if not parent:
        return
    c.endEditing()
    undoData = u.beforeMoveNode(p)
    p.moveToNthChildOf(parent, len(parent.v.children) - 1)
    p.setDirty()
    c.setChanged()
    u.afterMoveNode(p, 'Move To Last Child', undoData)
    c.redraw(p)
#@+node:ekr.20031218072017.1774: *3* c_oc.promote
@g.commander_command('promote')
def promote(self: Cmdr, event: LeoKeyEvent = None, undoFlag: bool = True) -> None:
    """Make all children of the selected nodes siblings of the selected node."""
    c, p, u = self, self.p, self.undoer
    if not p or not p.hasChildren():
        c.treeFocusHelper()
        return
    c.endEditing()
    children = p.v.children  # First, for undo.
    p.promote()
    c.setChanged()
    if undoFlag:
        p.setDirty()
        u.afterPromote(p, children)
    c.redraw(p)
    c.updateSyntaxColorer(p)  # Moving can change syntax coloring.
#@+node:ekr.20071213185710: *3* c_oc.toggleSparseMove
@g.commander_command('toggle-sparse-move')
def toggleSparseMove(self: Cmdr, event: LeoKeyEvent = None) -> None:
    """Toggle whether moves collapse the outline."""
    c = self
    c.sparse_move = not c.sparse_move
    if not g.unitTesting:
        g.blue(f"sparse-move: {c.sparse_move}")
#@+node:ekr.20080425060424.1: ** c_oc.Sort commands
#@+node:felix.20230318172503.1: *3* c_oc.reverseSortChildren
@g.commander_command('reverse-sort-children')
def reverseSortChildren(
    self: Cmdr,
    event: LeoKeyEvent = None,
    key: str = None
) -> None:
    """Sort the children of a node in reverse order."""
    self.sortChildren(key=key, reverse=True)  # as reverse, Fixes #3188
#@+node:felix.20230318172511.1: *3* c_oc.reverseSortSiblings
@g.commander_command('reverse-sort-siblings')
def reverseSortSiblings(
    self: Cmdr,
    event: LeoKeyEvent = None,
    key: str = None
) -> None:
    """Sort the siblings of a node in reverse order."""
    self.sortSiblings(key=key, reverse=True)  # as reverse, Fixes #3188
#@+node:ekr.20050415134809: *3* c_oc.sortChildren
@g.commander_command('sort-children')
def sortChildren(
    self: Cmdr,
    event: LeoKeyEvent = None,
    key: Callable = None,
    reverse: bool = False
) -> None:
    """Sort the children of a node."""
    # This method no longer supports the 'cmp' keyword arg.
    c, p = self, self.p
    if p and p.hasChildren():
        c.sortSiblings(p=p.firstChild(), sortChildren=True, key=key, reverse=reverse)
#@+node:ekr.20050415134809.1: *3* c_oc.sortSiblings
@g.commander_command('sort-siblings')
def sortSiblings(
    self: Cmdr,
    event: LeoKeyEvent = None,  # cmp keyword is no longer supported.
    key: Callable = None,
    p: Position = None,
    sortChildren: bool = False,
    reverse: bool = False,
) -> None:
    """Sort the siblings of a node."""
    c, u = self, self.undoer
    if not p:
        p = c.p
    if not p:
        return

    oldP, newP = p.copy(), p.copy()
    c.endEditing()
    undoType = 'Sort Children' if sortChildren else 'Sort Siblings'
    if reverse:
        undoType = 'Reverse ' + undoType
    parent_v = p._parentVnode()
    oldChildren = parent_v.children[:]
    newChildren = parent_v.children[:]
    if key is None:

        def lowerKey(self: Cmdr) -> str:
            return self.h.lower()

        key = lowerKey

    newChildren.sort(key=key, reverse=reverse)  # type:ignore
    if oldChildren == newChildren:
        return
    # 2010/01/20. Fix bug 510148.
    c.setChanged()
    bunch = u.beforeSort(p, undoType, oldChildren, newChildren, sortChildren)
    # A copy, so its not the undo bead's oldChildren. Fixes #3205
    parent_v.children = newChildren[:]
    u.afterSort(p, bunch)
    # Sorting destroys position p, and possibly the root position.
    # Only the child index of new position changes!
    for i, v in enumerate(newChildren):
        if v.gnx == oldP.v.gnx:
            newP._childIndex = i
            break

    if newP.parent():
        newP.parent().setDirty()

    if sortChildren:
        c.redraw(newP.parent())
    else:
        c.redraw(newP)
#@+node:ekr.20070420092425: ** def cantMoveMessage
def cantMoveMessage(c: Cmdr) -> None:
    h = c.rootPosition().h
    kind = 'chapter' if h.startswith('@chapter') else 'hoist'
    g.warning("can't move node out of", kind)
#@+node:ekr.20180201040936.1: ** count-children
@g.command('count-children')
def count_children(event: LeoKeyEvent = None) -> None:
    """Print out the number of children for the currently selected node"""
    c = event and event.get('c')
    if c:
        g.es_print(f"{c.p.numberOfChildren()} children")
#@-others
#@-leo

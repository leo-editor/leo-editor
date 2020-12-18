# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20031218072017.3320: * @file leoNodes.py
#@@first
"""Leo's fundamental data classes."""
#@+<< imports >>
#@+node:ekr.20060904165452.1: ** << imports >> (leoNodes.py)
#Transcrypt does not support Python's copy module.
# __pragma__ ('skip')
import copy
# __pragma__ ('noskip')
import itertools
import time
import re
from leo.core import leoGlobals as g
from leo.core import signal_manager
#@-<< imports >>
#@+others
#@+node:ekr.20031218072017.1991: ** class NodeIndices
class NodeIndices:
    """A class managing global node indices (gnx's)."""
    #@+others
    #@+node:ekr.20031218072017.1992: *3* ni.__init__
    def __init__(self, id_):
        """Ctor for NodeIndices class."""
        self.defaultId = id_
        self.lastIndex = 0
        self.stack = []
            # A stack of open commanders.
        self.timeString = ''
            # Set by setTimeStamp.
        self.userId = id_
        # Assign the initial timestamp.
        self.setTimeStamp()
    #@+node:ekr.20150321161305.8: *3* ni.check_gnx
    def check_gnx(self, c, gnx, v):
        """Check that no vnode exists with the given gnx in fc.gnxDict."""
        fc = c.fileCommands
        if gnx == 'hidden-root-vnode-gnx':
            # No longer an error.
            # fast.readWithElementTree always generates a nominal hidden vnode.
            return
        v2 = fc.gnxDict.get(gnx)
        if v2 and v2 != v:
            g.internalError(
                f"getNewIndex: gnx clash {gnx}\n"
                f"          v: {v}\n"
                f"         v2: {v2}")
    #@+node:ekr.20150302061758.14: *3* ni.compute_last_index
    def compute_last_index(self, c):
        """Scan the entire leo outline to compute ni.last_index."""
        ni = self
        # Partial, experimental, fix for #658.
        # Do not change self.lastIndex here!
            # self.lastIndex = 0
        for v in c.all_unique_nodes():
            gnx = v.fileIndex
            if gnx:
                id_, t, n = self.scanGnx(gnx)
                if t == ni.timeString and n is not None:
                    try:
                        n = int(n)
                        self.lastIndex = max(self.lastIndex, n)
                    except Exception:
                        g.es_exception()
                        self.lastIndex += 1
    #@+node:ekr.20200528131303.1: *3* ni.computeNewIndex
    def computeNewIndex(self):
        """Return a new gnx."""
        t_s = self.update()
            # Updates self.lastTime and self.lastIndex.
        gnx = g.toUnicode(f"{self.userId}.{t_s}.{self.lastIndex:d}")
        return gnx
    #@+node:ekr.20031218072017.1994: *3* ni.get/setDefaultId
    # These are used by the FileCommands read/write code.

    def getDefaultId(self):
        """Return the id to be used by default in all gnx's"""
        return self.defaultId

    def setDefaultId(self, theId):
        """Set the id to be used by default in all gnx's"""
        self.defaultId = theId
    #@+node:ekr.20031218072017.1995: *3* ni.getNewIndex
    def getNewIndex(self, v, cached=False):
        """
        Create a new gnx for v or an empty string if the hold flag is set.
        **Important**: the method must allocate a new gnx even if v.fileIndex exists.
        """
        if v is None:
            g.internalError('getNewIndex: v is None')
            return ''
        c = v.context
        fc = c.fileCommands
        t_s = self.update()
            # Updates self.lastTime and self.lastIndex.
        gnx = g.toUnicode(f"{self.userId}.{t_s}.{self.lastIndex:d}")
        v.fileIndex = gnx
        self.check_gnx(c, gnx, v)
        fc.gnxDict[gnx] = v
        return gnx
    #@+node:ekr.20150322134954.1: *3* ni.new_vnode_helper
    def new_vnode_helper(self, c, gnx, v):
        """Handle all gnx-related tasks for VNode.__init__."""
        ni = self
        if gnx:
            v.fileIndex = gnx
            ni.check_gnx(c, gnx, v)
            c.fileCommands.gnxDict[gnx] = v
        else:
            v.fileIndex = ni.getNewIndex(v)
    #@+node:ekr.20031218072017.1997: *3* ni.scanGnx
    def scanGnx(self, s, i=0):
        """Create a gnx from its string representation."""
        if not isinstance(s, str):
            g.error("scanGnx: unexpected index type:", type(s), '', s)
            return None, None, None
        s = s.strip()
        theId, t, n = None, None, None
        i, theId = g.skip_to_char(s, i, '.')
        if g.match(s, i, '.'):
            i, t = g.skip_to_char(s, i + 1, '.')
            if g.match(s, i, '.'):
                i, n = g.skip_to_char(s, i + 1, '.')
        # Use self.defaultId for missing id entries.
        if not theId:
            theId = self.defaultId
        return theId, t, n
    #@+node:ekr.20031218072017.1998: *3* ni.setTimeStamp
    def setTimestamp(self):
        """Set the timestamp string to be used by getNewIndex until further notice"""
        self.timeString = time.strftime(
            "%Y%m%d%H%M%S",  # Help comparisons; avoid y2k problems.
            time.localtime())

    setTimeStamp = setTimestamp
    #@+node:ekr.20141015035853.18304: *3* ni.tupleToString
    def tupleToString(self, aTuple):
        """
        Convert a gnx tuple returned by scanGnx
        to its string representation.
        """
        theId, t, n = aTuple
        # This logic must match the existing logic so that
        # previously written gnx's can be found.
        if n in (None, 0, '',):
            s = f"{theId}.{t}"
        else:
            s = f"{theId}.{t}.{n}"
        return g.toUnicode(s)
    #@+node:ekr.20150321161305.13: *3* ni.update
    def update(self):
        """Update self.timeString and self.lastIndex"""
        t_s = time.strftime("%Y%m%d%H%M%S", time.localtime())
        if self.timeString == t_s:
            self.lastIndex += 1
        else:
            self.lastIndex = 1
            self.timeString = t_s
        return t_s
    #@+node:ekr.20141023110422.4: *3* ni.updateLastIndex
    def updateLastIndex(self, gnx):
        """Update ni.lastIndex if the gnx affects it."""
        id_, t, n = self.scanGnx(gnx)
        # pylint: disable=literal-comparison
            # Don't you dare touch this code to keep pylint happy.
        if not id_ or (n != 0 and not n):
            return  # the gnx is not well formed or n in ('',None)
        if id_ == self.userId and t == self.timeString:
            try:
                n = int(n)
                if n > self.lastIndex:
                    self.lastIndex = n
                    g.trace(gnx, '-->', n)
            except Exception:
                g.trace('can not happen', repr(n))
    #@-others
#@+node:ekr.20031218072017.889: ** class Position
#@+<< about the position class >>
#@+node:ekr.20031218072017.890: *3* << about the position class >>
#@@language rest
#@+at
# A position marks the spot in a tree traversal. A position p consists of a VNode
# p.v, a child index p._childIndex, and a stack of tuples (v,childIndex), one for
# each ancestor **at the spot in tree traversal. Positions p has a unique set of
# parents.
#
# The p.moveToX methods may return a null (invalid) position p with p.v = None.
#
# The tests "if p" or "if not p" are the _only_ correct way to test whether a
# position p is valid. In particular, tests like "if p is None" or "if p is not
# None" will not work properly.
#@-<< about the position class >>
# Positions should *never* be saved by the ZOBD.


class Position:
    #@+others
    #@+node:ekr.20040228094013: *3*  p.ctor & other special methods...
    #@+node:ekr.20080416161551.190: *4*  p.__init__
    def __init__(self, v, childIndex=0, stack=None):
        """Create a new position with the given childIndex and parent stack."""
        # To support ZODB the code must set v._p_changed = 1
        # whenever any mutable VNode object changes.
        self._childIndex = childIndex
        self.v = v
        # Stack entries are tuples (v, childIndex).
        if stack:
            self.stack = stack[:]  # Creating a copy here is safest and best.
        else:
            self.stack = []
        g.app.positions += 1
    #@+node:ekr.20080920052058.3: *4* p.__eq__ & __ne__
    def __eq__(self, p2):
        """Return True if two positions are equivalent."""
        p1 = self
        # Don't use g.trace: it might call p.__eq__ or p.__ne__.
        if not isinstance(p2, Position):
            return False
        if p2 is None or p2.v is None:
            return p1.v is None
        return (p1.v == p2.v and
            p1._childIndex == p2._childIndex and
            p1.stack == p2.stack)

    def __ne__(self, p2):
        """Return True if two postions are not equivalent."""
        return not self.__eq__(p2)
    #@+node:ekr.20091210082012.6230: *4* p.__ge__ & __le__& __lt__
    def __ge__(self, other):
        return self.__eq__(other) or self.__gt__(other)

    def __le__(self, other):
        return self.__eq__(other) or self.__lt__(other)

    def __lt__(self, other):
        return not self.__eq__(other) and not self.__gt__(other)
    #@+node:ekr.20091210082012.6233: *4* p.__gt__
    def __gt__(self, other):
        """Return True if self appears after other in outline order."""
        stack1, stack2 = self.stack, other.stack
        n1, n2 = len(stack1), len(stack2); n = min(n1, n2)
        # Compare the common part of the stacks.
        for item1, item2 in zip(stack1, stack2):
            v1, x1 = item1; v2, x2 = item2
            if x1 > x2:
                return True
            if x1 < x2:
                return False
        # Finish the comparison.
        if n1 == n2:
            x1, x2 = self._childIndex, other._childIndex
            return x1 > x2
        if n1 < n2:
            x1 = self._childIndex; v2, x2 = other.stack[n]
            return x1 > x2
        # n1 > n2
        # 2011/07/28: Bug fix suggested by SegundoBob.
        x1 = other._childIndex; v2, x2 = self.stack[n]
        return x2 >= x1
    #@+node:ekr.20040117173448: *4* p.__nonzero__ & __bool__
    def __bool__(self):
        """
        Return True if a position is valid.
        
        The tests 'if p' or 'if not p' are the _only_ correct ways to test
        whether a position p is valid.
        
        Tests like 'if p is None' or 'if p is not None' will not work properly.
        """
        return self.v is not None
    #@+node:ekr.20040301205720: *4* p.__str__ and p.__repr__
    def __str__(self):
        p = self
        if p.v:
            return (
                "<"
                f"pos {id(p)} "
                f"childIndex: {p._childIndex} "
                f"lvl: {p.level()} "
                f"key: {p.key()} "
                f"{p.h}"
                ">"
            )
        return f"<pos {id(p)} [{len(p.stack)}] None>"

    __repr__ = __str__
    #@+node:ekr.20061006092649: *4* p.archivedPosition
    def archivedPosition(self, root_p=None):
        """Return a representation of a position suitable for use in .leo files."""
        p = self
        if root_p is None:
            aList = [z._childIndex for z in p.self_and_parents()]
        else:
            aList = []
            for z in p.self_and_parents(copy=False):
                if z == root_p:
                    aList.append(0)
                    break
                else:
                    aList.append(z._childIndex)
        aList.reverse()
        return aList
    #@+node:ekr.20040310153624: *4* p.dump
    def dumpLink(self, link):
        return link if link else "<none>"

    def dump(self, label=""):
        p = self
        if p.v:
            p.v.dump()  # Don't print a label
    #@+node:ekr.20080416161551.191: *4* p.key & p.sort_key & __hash__
    def key(self):
        p = self
        # For unified nodes we must include a complete key,
        # so we can distinguish between clones.
        result = []
        for z in p.stack:
            v, childIndex = z
            result.append(f"{id(v)}:{childIndex}")
        result.append(f"{id(p.v)}:{p._childIndex}")
        return '.'.join(result)

    def sort_key(self, p):
        return [int(s.split(':')[1]) for s in p.key().split('.')]

    # Positions should *not* be hashable.
    #
    # From https://docs.python.org/3/reference/datamodel.html#object.__hash__
    #
    # If a class defines mutable objects and implements an __eq__() method, it
    # should not implement __hash__(), since the implementation of hashable
    # collections requires that a key’s hash value is immutable (if the object’s
    # hash value changes, it will be in the wrong hash bucket).

    __hash__ = None
    #@+node:ekr.20040315023430: *3* p.File Conversion
    #@+at
    # - convertTreeToString and moreHead can't be VNode methods because they uses level().
    # - moreBody could be anywhere: it may as well be a postion method.
    #@+node:ekr.20040315023430.1: *4* p.convertTreeToString
    def convertTreeToString(self):
        """Convert a positions  suboutline to a string in MORE format."""
        p = self; level1 = p.level()
        array = []
        for p in p.self_and_subtree(copy=False):
            array.append(p.moreHead(level1) + '\n')
            body = p.moreBody()
            if body:
                array.append(body + '\n')
        return ''.join(array)
    #@+node:ekr.20040315023430.2: *4* p.moreHead
    def moreHead(self, firstLevel, useVerticalBar=False):
        """Return the headline string in MORE format."""
        # useVerticalBar is unused, but it would be useful in over-ridden methods.
        p = self
        level = self.level() - firstLevel
        plusMinus = "+" if p.hasChildren() else "-"
        pad = '\t' * level
        return f"{pad}{plusMinus} {p.h}"
    #@+node:ekr.20040315023430.3: *4* p.moreBody
    #@@language rest
    #@+at
    #     + test line
    #     - test line
    #     \ test line
    #     test line +
    #     test line -
    #     test line \
    #     More lines...
    #@@c
    #@@language python

    def moreBody(self):
        """Returns the body string in MORE format.

        Inserts a backslash before any leading plus, minus or backslash."""
        p = self; array = []
        lines = p.b.split('\n')
        for s in lines:
            i = g.skip_ws(s, 0)
            if i < len(s) and s[i] in ('+', '-', '\\'):
                s = s[:i] + '\\' + s[i:]
            array.append(s)
        return '\n'.join(array)
    #@+node:ekr.20091001141621.6060: *3* p.generators
    #@+node:ekr.20091001141621.6055: *4* p.children
    def children(self, copy=True):
        """Yield all child positions of p."""
        p = self
        p = p.firstChild()
        while p:
            yield p.copy() if copy else p
            p.moveToNext()

    # Compatibility with old code...

    children_iter = children
    #@+node:ekr.20091002083910.6102: *4* p.following_siblings
    def following_siblings(self, copy=True):
        """Yield all siblings positions that follow p, not including p."""
        p = self
        p = p.next()
        while p:
            yield p.copy() if copy else p
            p.moveToNext()

    # Compatibility with old code...

    following_siblings_iter = following_siblings
    #@+node:ekr.20161120105707.1: *4* p.nearest_roots
    def nearest_roots(self, copy=True, predicate=None):
        """
        A generator yielding all the root positions "near" p1 = self that
        satisfy the given predicate. p.isAnyAtFileNode is the default
        predicate.

        The search first proceeds up the p's tree. If a root is found, this
        generator yields just that root.

        Otherwise, the generator yields all nodes in p.subtree() that satisfy
        the predicate. Once a root is found, the generator skips its subtree.
        """
        if predicate is None:

            # pylint: disable=function-redefined

            def predicate(p):
                return p.isAnyAtFileNode()

        # First, look up the tree.

        p1 = self
        for p in p1.self_and_parents(copy=False):
            if predicate(p):
                yield p.copy() if copy else p
                return
        # Next, look for all .md files in the tree.
        after = p1.nodeAfterTree()
        p = p1
        while p and p != after:
            if predicate(p):
                yield p.copy() if copy else p
                p.moveToNodeAfterTree()
            else:
                p.moveToThreadNext()
    #@+node:ekr.20161120163203.1: *4* p.nearest_unique_roots (aka p.nearest)
    def nearest_unique_roots(self, copy=True, predicate=None):
        """
        A generator yielding all unique root positions "near" p1 = self that
        satisfy the given predicate. p.isAnyAtFileNode is the default
        predicate.

        The search first proceeds up the p's tree. If a root is found, this
        generator yields just that root.

        Otherwise, the generator yields all unique nodes in p.subtree() that
        satisfy the predicate. Once a root is found, the generator skips its
        subtree.
        """
        if predicate is None:

            # pylint: disable=function-redefined

            def predicate(p):
                return p.isAnyAtFileNode()

        # First, look up the tree.

        p1 = self
        for p in p1.self_and_parents(copy=False):
            if predicate(p):
                yield p.copy() if copy else p
                return
        # Next, look for all unique .md files in the tree.
        seen = set()
        after = p1.nodeAfterTree()
        p = p1
        while p and p != after:
            if predicate(p):
                if p.v not in seen:
                    seen.add(p.v)
                    yield p.copy() if copy else p
                p.moveToNodeAfterTree()
            else:
                p.moveToThreadNext()

    nearest = nearest_unique_roots
    #@+node:ekr.20091002083910.6104: *4* p.nodes
    def nodes(self):
        """Yield p.v and all vnodes in p's subtree."""
        p = self
        p = p.copy()
        after = p.nodeAfterTree()
        while p and p != after:  # bug fix: 2013/10/12
            yield p.v
            p.moveToThreadNext()

    # Compatibility with old code.

    tnodes_iter = nodes
    vnodes_iter = nodes
    #@+node:ekr.20091001141621.6058: *4* p.parents
    def parents(self, copy=True):
        """Yield all parent positions of p."""
        p = self
        p = p.parent()
        while p:
            yield p.copy() if copy else p
            p.moveToParent()

    # Compatibility with old code...

    parents_iter = parents
    #@+node:ekr.20091002083910.6099: *4* p.self_and_parents
    def self_and_parents(self, copy=True):
        """Yield p and all parent positions of p."""
        p = self
        p = p.copy()
        while p:
            yield p.copy() if copy else p
            p.moveToParent()

    # Compatibility with old code...

    self_and_parents_iter = self_and_parents
    #@+node:ekr.20091001141621.6057: *4* p.self_and_siblings
    def self_and_siblings(self, copy=True):
        """Yield all sibling positions of p including p."""
        p = self
        p = p.copy()
        while p.hasBack():
            p.moveToBack()
        while p:
            yield p.copy() if copy else p
            p.moveToNext()

    # Compatibility with old code...

    self_and_siblings_iter = self_and_siblings
    #@+node:ekr.20091001141621.6066: *4* p.self_and_subtree
    def self_and_subtree(self, copy=True):
        """Yield p and all positions in p's subtree."""
        p = self
        p = p.copy()
        after = p.nodeAfterTree()
        while p and p != after:
            yield p.copy() if copy else p
            p.moveToThreadNext()

    # Compatibility with old code...

    self_and_subtree_iter = self_and_subtree
    #@+node:ekr.20091001141621.6056: *4* p.subtree
    def subtree(self, copy=True):
        """Yield all positions in p's subtree, but not p."""
        p = self
        p = p.copy()
        after = p.nodeAfterTree()
        p.moveToThreadNext()
        while p and p != after:
            yield p.copy() if copy else p
            p.moveToThreadNext()

    # Compatibility with old code...

    subtree_iter = subtree
    #@+node:ekr.20091002083910.6105: *4* p.unique_nodes
    def unique_nodes(self):
        """Yield p.v and all unique vnodes in p's subtree."""
        p = self
        seen = set()
        for p in p.self_and_subtree(copy=False):
            if p.v not in seen:
                seen.add(p.v)
                yield p.v

    # Compatibility with old code.

    unique_tnodes_iter = unique_nodes
    unique_vnodes_iter = unique_nodes
    #@+node:ekr.20091002083910.6103: *4* p.unique_subtree
    def unique_subtree(self, copy=True):
        """Yield p and all other unique positions in p's subtree."""
        p = self
        seen = set()
        for p in p.subtree():
            if p.v not in seen:
                seen.add(p.v)
                # Fixed bug 1255208: p.unique_subtree returns vnodes, not positions.
                yield p.copy() if copy else p

    # Compatibility with old code...

    subtree_with_unique_tnodes_iter = unique_subtree
    subtree_with_unique_vnodes_iter = unique_subtree
    #@+node:ekr.20040306212636: *3* p.Getters
    #@+node:ekr.20040306210951: *4* p.VNode proxies
    #@+node:ekr.20040306211032: *5* p.Comparisons
    def anyAtFileNodeName(self): return self.v.anyAtFileNodeName()

    def atAutoNodeName(self): return self.v.atAutoNodeName()

    def atCleanNodeName(self): return self.v.atCleanNodeName()

    def atEditNodeName(self): return self.v.atEditNodeName()

    def atFileNodeName(self): return self.v.atFileNodeName()

    def atNoSentinelsFileNodeName(self): return self.v.atNoSentinelsFileNodeName()
    # def atRawFileNodeName         (self): return self.v.atRawFileNodeName()

    def atShadowFileNodeName(self): return self.v.atShadowFileNodeName()

    def atSilentFileNodeName(self): return self.v.atSilentFileNodeName()

    def atThinFileNodeName(self): return self.v.atThinFileNodeName()
    # New names, less confusing
    atNoSentFileNodeName = atNoSentinelsFileNodeName
    atAsisFileNodeName = atSilentFileNodeName

    def isAnyAtFileNode(self): return self.v.isAnyAtFileNode()

    def isAtAllNode(self): return self.v.isAtAllNode()

    def isAtAutoNode(self): return self.v.isAtAutoNode()

    def isAtAutoRstNode(self): return self.v.isAtAutoRstNode()

    def isAtCleanNode(self): return self.v.isAtCleanNode()

    def isAtEditNode(self): return self.v.isAtEditNode()

    def isAtFileNode(self): return self.v.isAtFileNode()

    def isAtIgnoreNode(self): return self.v.isAtIgnoreNode()

    def isAtNoSentinelsFileNode(self): return self.v.isAtNoSentinelsFileNode()

    def isAtOthersNode(self): return self.v.isAtOthersNode()

    def isAtRstFileNode(self): return self.v.isAtRstFileNode()

    def isAtSilentFileNode(self): return self.v.isAtSilentFileNode()

    def isAtShadowFileNode(self): return self.v.isAtShadowFileNode()

    def isAtThinFileNode(self): return self.v.isAtThinFileNode()
    # New names, less confusing:
    isAtNoSentFileNode = isAtNoSentinelsFileNode
    isAtAsisFileNode = isAtSilentFileNode
    # Utilities.

    def matchHeadline(self, pattern): return self.v.matchHeadline(pattern)
    #@+node:ekr.20040306220230: *5* p.Headline & body strings
    def bodyString(self):
        return self.v.bodyString()

    def headString(self):
        return self.v.headString()

    def cleanHeadString(self):
        return self.v.cleanHeadString()
    #@+node:ekr.20040306214401: *5* p.Status bits
    def isDirty(self): return self.v.isDirty()

    def isMarked(self): return self.v.isMarked()

    def isOrphan(self): return self.v.isOrphan()

    def isSelected(self): return self.v.isSelected()

    def isTopBitSet(self): return self.v.isTopBitSet()

    def isVisited(self): return self.v.isVisited()

    def status(self): return self.v.status()
    #@+node:ekr.20040306214240.2: *4* p.children & parents
    #@+node:ekr.20040326064330: *5* p.childIndex
    # This used to be time-critical code.

    def childIndex(self):
        p = self
        return p._childIndex
    #@+node:ekr.20040323160302: *5* p.directParents
    def directParents(self):
        return self.v.directParents()
    #@+node:ekr.20040306214240.3: *5* p.hasChildren & p.numberOfChildren
    def hasChildren(self):
        p = self
        return len(p.v.children) > 0

    hasFirstChild = hasChildren

    def numberOfChildren(self):
        p = self
        return len(p.v.children)
    #@+node:ekr.20031218072017.915: *4* p.getX & VNode compatibility traversal routines
    # These methods are useful abbreviations.
    # Warning: they make copies of positions, so they should be used _sparingly_

    def getBack(self): return self.copy().moveToBack()

    def getFirstChild(self): return self.copy().moveToFirstChild()

    def getLastChild(self): return self.copy().moveToLastChild()

    def getLastNode(self): return self.copy().moveToLastNode()
    # def getLastVisible   (self): return self.copy().moveToLastVisible()

    def getNext(self): return self.copy().moveToNext()

    def getNodeAfterTree(self): return self.copy().moveToNodeAfterTree()

    def getNthChild(self, n): return self.copy().moveToNthChild(n)

    def getParent(self): return self.copy().moveToParent()

    def getThreadBack(self): return self.copy().moveToThreadBack()

    def getThreadNext(self): return self.copy().moveToThreadNext()
    # New in Leo 4.4.3 b2: add c args.

    def getVisBack(self, c): return self.copy().moveToVisBack(c)

    def getVisNext(self, c): return self.copy().moveToVisNext(c)
    # These are efficient enough now that iterators are the normal way to traverse the tree!
    back = getBack
    firstChild = getFirstChild
    lastChild = getLastChild
    lastNode = getLastNode
    # lastVisible   = getLastVisible # New in 4.2 (was in tk tree code).
    next = getNext
    nodeAfterTree = getNodeAfterTree
    nthChild = getNthChild
    parent = getParent
    threadBack = getThreadBack
    threadNext = getThreadNext
    visBack = getVisBack
    visNext = getVisNext
    # New in Leo 4.4.3:
    hasVisBack = visBack
    hasVisNext = visNext
    #@+node:tbrown.20111010104549.26758: *4* p.get_UNL
    def get_UNL(
        self,
        with_file=True,
        with_proto=False,
        with_index=True,
        with_count=False,
    ):
        """
        with_file=True - include path to Leo file
        with_proto=False - include 'file://'
        with_index - include ',x' at end where x is child index in parent
        with_count - include ',x,y' at end where y zero based count of same headlines
        """
        aList = []
        for i in self.self_and_parents(copy=False):
            if with_index or with_count:
                count = 0
                ind = 0
                p = i.copy()
                while p.hasBack():
                    ind = ind + 1
                    p.moveToBack()
                    if i.h == p.h:
                        count = count + 1
                aList.append(i.h.replace('-->', '--%3E') + ":" + str(ind))
                    # g.recursiveUNLFind and sf.copy_to_my_settings undo this replacement.
                if count or with_count:
                    aList[-1] = aList[-1] + "," + str(count)
            else:
                aList.append(i.h.replace('-->', '--%3E'))
                    # g.recursiveUNLFind  and sf.copy_to_my_settings undo this replacement.
        UNL = '-->'.join(reversed(aList))
        if with_proto:
            # return ("file://%s#%s" % (self.v.context.fileName(), UNL)).replace(' ', '%20')
            s = "unl:" + f"//{self.v.context.fileName()}#{UNL}"
            return s.replace(' ', '%20')
        if with_file:
            return f"{self.v.context.fileName()}#{UNL}"
        return UNL
    #@+node:ekr.20080416161551.192: *4* p.hasBack/Next/Parent/ThreadBack
    def hasBack(self):
        p = self
        return p.v and p._childIndex > 0

    def hasNext(self):
        p = self
        try:
            parent_v = p._parentVnode()
                # Returns None if p.v is None.
            return p.v and parent_v and p._childIndex + 1 < len(parent_v.children)
        except Exception:
            g.trace('*** Unexpected exception')
            g.es_exception()
            return None

    def hasParent(self):
        p = self
        return p.v and p.stack

    def hasThreadBack(self):
        p = self
        return p.hasParent() or p.hasBack()
            # Much cheaper than computing the actual value.
    #@+node:ekr.20080416161551.193: *5* hasThreadNext (the only complex hasX method)
    def hasThreadNext(self):
        p = self
        if not p.v: return False
        if p.hasChildren() or p.hasNext(): return True
        n = len(p.stack) - 1
        while n >= 0:
            v, childIndex = p.stack[n]
            # See how many children v's parent has.
            if n == 0:
                parent_v = v.context.hiddenRootNode
            else:
                parent_v, junk = p.stack[n - 1]
            if len(parent_v.children) > childIndex + 1:
                # v has a next sibling.
                return True
            n -= 1
        return False
    #@+node:ekr.20060920203352: *4* p.findRootPosition
    def findRootPosition(self):
        # 2011/02/25: always use c.rootPosition
        p = self
        c = p.v.context
        return c.rootPosition()
    #@+node:ekr.20080416161551.194: *4* p.isAncestorOf
    def isAncestorOf(self, p2):
        """Return True if p is one of the direct ancestors of p2."""
        p = self
        c = p.v.context
        if not c.positionExists(p2):
            return False
        for z in p2.stack:
            # 2013/12/25: bug fix: test childIndices.
            # This is required for the new per-position expansion scheme.
            parent_v, parent_childIndex = z
            if parent_v == p.v and parent_childIndex == p._childIndex:
                return True
        return False
    #@+node:ekr.20040306215056: *4* p.isCloned
    def isCloned(self):
        p = self
        return p.v.isCloned()
    #@+node:ekr.20040307104131.2: *4* p.isRoot
    def isRoot(self):
        p = self
        return not p.hasParent() and not p.hasBack()
    #@+node:ekr.20080416161551.196: *4* p.isVisible (slow)
    def isVisible(self, c):
        """Return True if p is visible in c's outline."""
        p = self

        def visible(p, root=None):
            for parent in p.parents(copy=False):
                if parent and parent == root:
                    # #12.
                    return True
                if not c.shouldBeExpanded(parent):
                    return False
            return True

        if c.hoistStack:
            root = c.hoistStack[-1].p
            if p == root:
                # #12.
                return True
            return root.isAncestorOf(p) and visible(p, root=root)
        for root in c.rootPosition().self_and_siblings(copy=False):
            if root == p or root.isAncestorOf(p):
                return visible(p)
        return False
    #@+node:ekr.20080416161551.197: *4* p.level & simpleLevel
    def level(self):
        """Return the number of p's parents."""
        p = self
        return len(p.stack) if p.v else 0

    simpleLevel = level
    #@+node:ekr.20111005152227.15566: *4* p.positionAfterDeletedTree
    def positionAfterDeletedTree(self):
        """Return the position corresponding to p.nodeAfterTree() after this node is
        deleted. This will be p.nodeAfterTree() unless p.next() exists.

        This method allows scripts to traverse an outline, deleting nodes during the
        traversal. The pattern is::

            p = c.rootPosition()
            while p:
            if <delete p?>:
                next = p.positionAfterDeletedTree()
                p.doDelete()
                p = next
            else:
                p.moveToThreadNext()

        This method also allows scripts to *move* nodes during a traversal, **provided**
        that nodes are moved to a "safe" spot so that moving a node does not change the
        position of any other nodes.

        For example, the move-marked-nodes command first creates a **move node**, called
        'Clones of marked nodes'. All moved nodes become children of this move node.
        **Inserting** these nodes as children of the "move node" does not change the
        positions of other nodes. **Deleting** these nodes *may* change the position of
        nodes, but the pattern above handles this complication cleanly.
        """
        p = self
        next = p.next()
        if next:
            # The new position will be the same as p, except for p.v.
            p = p.copy()
            p.v = next.v
            return p
        return p.nodeAfterTree()
    #@+node:shadow.20080825171547.2: *4* p.textOffset
    def textOffset(self):
        """
        Return the fcol offset of self.
        Return None if p is has no ancestor @<file> node.
        http://tinyurl.com/5nescw
        """
        p = self
        found, offset = False, 0
        for p in p.self_and_parents(copy=False):
            if p.isAnyAtFileNode():
                # Ignore parent of @<file> node.
                found = True
                break
            parent = p.parent()
            if not parent:
                break
            # If p is a section definition, search the parent for the reference.
            # Otherwise, search the parent for @others.
            h = p.h.strip()
            i = h.find('<<')
            j = h.find('>>')
            target = h[i : j + 2] if -1 < i < j else '@others'
            for s in parent.b.split('\n'):
                if s.find(target) > -1:
                    offset += g.skip_ws(s, 0)
                    break
        return offset if found else None
    #@+node:ekr.20150410101842.1: *3* p.isOutsideAtFileTree
    def isOutsideAnyAtFileTree(self):
        """Select the first clone of target that is outside any @file node."""
        p = self
        for parent in p.self_and_parents(copy=False):
            if parent.isAnyAtFileNode():
                return False
        return True
    #@+node:ekr.20080423062035.1: *3* p.Low level methods
    # These methods are only for the use of low-level code
    # in leoNodes.py, leoFileCommands.py and leoUndo.py.
    #@+node:ekr.20080427062528.4: *4* p._adjustPositionBeforeUnlink
    def _adjustPositionBeforeUnlink(self, p2):
        """Adjust position p before unlinking p2."""
        # p will change if p2 is a previous sibling of p or
        # p2 is a previous sibling of any ancestor of p.
        p = self; sib = p.copy()
        # A special case for previous siblings.
        # Adjust p._childIndex, not the stack's childIndex.
        while sib.hasBack():
            sib.moveToBack()
            if sib == p2:
                p._childIndex -= 1
                return
        # Adjust p's stack.
        stack = []; changed = False; i = 0
        while i < len(p.stack):
            v, childIndex = p.stack[i]
            p3 = Position(v=v, childIndex=childIndex, stack=stack[:i])
            while p3:
                if p2 == p3:
                    # 2011/02/25: compare full positions, not just vnodes.
                    # A match with the to-be-moved node.
                    stack.append((v, childIndex - 1),)
                    changed = True
                    break  # terminate only the inner loop.
                p3.moveToBack()
            else:
                stack.append((v, childIndex),)
            i += 1
        if changed:
            p.stack = stack
    #@+node:ekr.20080416161551.214: *4* p._linkAfter
    def _linkAfter(self, p_after):
        """Link self after p_after."""
        p = self
        parent_v = p_after._parentVnode()
        p.stack = p_after.stack[:]
        p._childIndex = p_after._childIndex + 1
        child = p.v
        n = p_after._childIndex + 1
        child._addLink(n, parent_v)
    #@+node:ekr.20180709181718.1: *4* p._linkCopiedAfter
    def _linkCopiedAfter(self, p_after):
        """Link self, a newly copied tree, after p_after."""
        p = self
        parent_v = p_after._parentVnode()
        p.stack = p_after.stack[:]
        p._childIndex = p_after._childIndex + 1
        child = p.v
        n = p_after._childIndex + 1
        child._addCopiedLink(n, parent_v)
    #@+node:ekr.20080416161551.215: *4* p._linkAsNthChild
    def _linkAsNthChild(self, parent, n):
        """Link self as the n'th child of the parent."""
        p = self
        parent_v = parent.v
        p.stack = parent.stack[:]
        p.stack.append((parent_v, parent._childIndex),)
        p._childIndex = n
        child = p.v
        child._addLink(n, parent_v)
    #@+node:ekr.20180709180140.1: *4* p._linkCopiedAsNthChild
    def _linkCopiedAsNthChild(self, parent, n):
        """Link a copied self as the n'th child of the parent."""
        p = self
        parent_v = parent.v
        p.stack = parent.stack[:]
        p.stack.append((parent_v, parent._childIndex),)
        p._childIndex = n
        child = p.v
        child._addCopiedLink(n, parent_v)
    #@+node:ekr.20080416161551.216: *4* p._linkAsRoot (changed)
    def _linkAsRoot(self):
        """Link self as the root node."""
        p = self
        assert(p.v)
        parent_v = p.v.context.hiddenRootNode
        assert parent_v, g.callers()
        #
        # Make p the root position.
        p.stack = []
        p._childIndex = 0
        #
        # Make p.v the first child of parent_v.
        p.v._addLink(0, parent_v)
        return p
    #@+node:ekr.20080416161551.212: *4* p._parentVnode
    def _parentVnode(self):
        """
        Return the parent VNode.
        Return the hiddenRootNode if there is no other parent.
        """
        p = self
        if p.v:
            data = p.stack and p.stack[-1]
            if data:
                v, junk = data
                return v
            return p.v.context.hiddenRootNode
        return None
    #@+node:ekr.20131219220412.16582: *4* p._relinkAsCloneOf
    def _relinkAsCloneOf(self, p2):
        """A low-level method to replace p.v by a p2.v."""
        p = self
        v, v2 = p.v, p2.v
        parent_v = p._parentVnode()
        if not parent_v:
            g.internalError('no parent_v', p)
            return
        if parent_v.children[p._childIndex] == v:
            parent_v.children[p._childIndex] = v2
            v2.parents.append(parent_v)
            # p.v no longer truly exists.
            # p.v = p2.v
        else:
            g.internalError(
                'parent_v.children[childIndex] != v',
                p, parent_v.children, p._childIndex, v)
    #@+node:ekr.20080416161551.217: *4* p._unlink
    def _unlink(self):
        """Unlink the receiver p from the tree."""
        p = self; n = p._childIndex
        parent_v = p._parentVnode()
            # returns None if p.v is None
        child = p.v
        assert(p.v)
        assert(parent_v)
        # Delete the child.
        if (0 <= n < len(parent_v.children) and
            parent_v.children[n] == child
        ):
            # This is the only call to v._cutlink.
            child._cutLink(n, parent_v)
        else:
            self.badUnlink(parent_v, n, child)
    #@+node:ekr.20090706171333.6226: *5* p.badUnlink
    def badUnlink(self, parent_v, n, child):

        if 0 <= n < len(parent_v.children):
            g.trace(f"**can not happen: children[{n}] != p.v")
            g.trace('parent_v.children...\n',
                g.listToString(parent_v.children))
            g.trace('parent_v', parent_v)
            g.trace('parent_v.children[n]', parent_v.children[n])
            g.trace('child', child)
            g.trace('** callers:', g.callers())
            if g.app.unitTesting: assert False, 'children[%s] != p.v'
        else:
            g.trace(
                f"**can not happen: bad child index: {n}, "
                f"len(children): {len(parent_v.children)}")
            g.trace('parent_v.children...\n',
                g.listToString(parent_v.children))
            g.trace('parent_v', parent_v, 'child', child)
            g.trace('** callers:', g.callers())
            if g.app.unitTesting:
                assert False, f"bad child index: {n}"
    #@+node:ekr.20080416161551.199: *3* p.moveToX
    #@+at These routines change self to a new position "in place".
    # That is, these methods must _never_ call p.copy().
    #
    # When moving to a nonexistent position, these routines simply set p.v = None,
    # leaving the p.stack unchanged. This allows the caller to "undo" the effect of
    # the invalid move by simply restoring the previous value of p.v.
    #
    # These routines all return self on exit so the following kind of code will work:
    #     after = p.copy().moveToNodeAfterTree()
    #@+node:ekr.20080416161551.200: *4* p.moveToBack
    def moveToBack(self):
        """Move self to its previous sibling."""
        p = self; n = p._childIndex
        parent_v = p._parentVnode()
            # Returns None if p.v is None.
        # Do not assume n is in range: this is used by positionExists.
        if parent_v and p.v and 0 < n <= len(parent_v.children):
            p._childIndex -= 1
            p.v = parent_v.children[n - 1]
        else:
            p.v = None
        return p
    #@+node:ekr.20080416161551.201: *4* p.moveToFirstChild
    def moveToFirstChild(self):
        """Move a position to it's first child's position."""
        p = self
        if p.v and p.v.children:
            p.stack.append((p.v, p._childIndex),)
            p.v = p.v.children[0]
            p._childIndex = 0
        else:
            p.v = None
        return p
    #@+node:ekr.20080416161551.202: *4* p.moveToLastChild
    def moveToLastChild(self):
        """Move a position to it's last child's position."""
        p = self
        if p.v and p.v.children:
            p.stack.append((p.v, p._childIndex),)
            n = len(p.v.children)
            p.v = p.v.children[n - 1]
            p._childIndex = n - 1
        else:
            p.v = None
        return p
    #@+node:ekr.20080416161551.203: *4* p.moveToLastNode
    def moveToLastNode(self):
        """Move a position to last node of its tree.

        N.B. Returns p if p has no children."""
        p = self
        # Huge improvement for 4.2.
        while p.hasChildren():
            p.moveToLastChild()
        return p
    #@+node:ekr.20080416161551.204: *4* p.moveToNext
    def moveToNext(self):
        """Move a position to its next sibling."""
        p = self; n = p._childIndex
        parent_v = p._parentVnode()
            # Returns None if p.v is None.
        if not p.v:
            g.trace('no p.v:', p, g.callers())
        if p.v and parent_v and len(parent_v.children) > n + 1:
            p._childIndex = n + 1
            p.v = parent_v.children[n + 1]
        else:
            p.v = None
        return p
    #@+node:ekr.20080416161551.205: *4* p.moveToNodeAfterTree
    def moveToNodeAfterTree(self):
        """Move a position to the node after the position's tree."""
        p = self
        while p:
            if p.hasNext():
                p.moveToNext()
                break
            p.moveToParent()
        return p
    #@+node:ekr.20080416161551.206: *4* p.moveToNthChild
    def moveToNthChild(self, n):
        p = self
        if p.v and len(p.v.children) > n:
            p.stack.append((p.v, p._childIndex),)
            p.v = p.v.children[n]
            p._childIndex = n
        else:
            p.v = None
        return p
    #@+node:ekr.20080416161551.207: *4* p.moveToParent
    def moveToParent(self):
        """Move a position to its parent position."""
        p = self
        if p.v and p.stack:
            p.v, p._childIndex = p.stack.pop()
        else:
            p.v = None
        return p
    #@+node:ekr.20080416161551.208: *4* p.moveToThreadBack
    def moveToThreadBack(self):
        """Move a position to it's threadBack position."""
        p = self
        if p.hasBack():
            p.moveToBack()
            p.moveToLastNode()
        else:
            p.moveToParent()
        return p
    #@+node:ekr.20080416161551.209: *4* p.moveToThreadNext
    def moveToThreadNext(self):
        """Move a position to threadNext position."""
        p = self
        if p.v:
            if p.v.children:
                p.moveToFirstChild()
            elif p.hasNext():
                p.moveToNext()
            else:
                p.moveToParent()
                while p:
                    if p.hasNext():
                        p.moveToNext()
                        break  #found
                    p.moveToParent()
                # not found.
        return p
    #@+node:ekr.20080416161551.210: *4* p.moveToVisBack & helper
    def moveToVisBack(self, c):
        """Move a position to the position of the previous visible node."""
        p = self
        limit, limitIsVisible = c.visLimit()
        while p:
            # Short-circuit if possible.
            back = p.back()
            if back and back.hasChildren() and back.isExpanded():
                p.moveToThreadBack()
            elif back:
                p.moveToBack()
            else:
                p.moveToParent()  # Same as p.moveToThreadBack()
            if p:
                if limit:
                    done, val = self.checkVisBackLimit(limit, limitIsVisible, p)
                    if done:
                        return val  # A position or None
                if p.isVisible(c):
                    return p
        return p
    #@+node:ekr.20090715145956.6166: *5* checkVisBackLimit
    def checkVisBackLimit(self, limit, limitIsVisible, p):
        """Return done, p or None"""
        c = p.v.context
        if limit == p:
            if limitIsVisible and p.isVisible(c):
                return True, p
            return True, None
        if limit.isAncestorOf(p):
            return False, None
        return True, None
    #@+node:ekr.20080416161551.211: *4* p.moveToVisNext & helper
    def moveToVisNext(self, c):
        """Move a position to the position of the next visible node."""
        p = self
        limit, limitIsVisible = c.visLimit()
        while p:
            if p.hasChildren():
                if p.isExpanded():
                    p.moveToFirstChild()
                else:
                    p.moveToNodeAfterTree()
            elif p.hasNext():
                p.moveToNext()
            else:
                p.moveToThreadNext()
            if p:
                if limit and self.checkVisNextLimit(limit, p):
                    return None
                if p.isVisible(c):
                    return p
        return p
    #@+node:ekr.20090715145956.6167: *5* checkVisNextLimit
    def checkVisNextLimit(self, limit, p):
        """Return True is p is outside limit of visible nodes."""
        return limit != p and not limit.isAncestorOf(p)
    #@+node:ekr.20150316175921.6: *4* p.safeMoveToThreadNext
    def safeMoveToThreadNext(self):
        """
        Move a position to threadNext position.
        Issue an error if any vnode is an ancestor of itself.
        """
        p = self
        if p.v:
            child_v = p.v.children and p.v.children[0]
            if child_v:
                for parent in p.self_and_parents(copy=False):
                    if child_v == parent.v:
                        g.app.structure_errors += 1
                        g.error(f"vnode: {child_v} is its own parent")
                        # Allocating a new vnode would be difficult.
                        # Just remove child_v from parent.v.children.
                        parent.v.children = [
                            v2 for v2 in parent.v.children if not v2 == child_v]
                        if parent.v in child_v.parents:
                            child_v.parents.remove(parent.v)
                        # Try not to hang.
                        p.moveToParent()
                        break
                    elif child_v.fileIndex == parent.v.fileIndex:
                        g.app.structure_errors += 1
                        g.error(
                            f"duplicate gnx: {child_v.fileIndex!r} "
                            f"v: {child_v} parent: {parent.v}")
                        child_v.fileIndex = g.app.nodeIndices.getNewIndex(v=child_v)
                        assert child_v.gnx != parent.v.gnx
                        # Should be ok to continue.
                        p.moveToFirstChild()
                        break
                else:
                    p.moveToFirstChild()
            elif p.hasNext():
                p.moveToNext()
            else:
                p.moveToParent()
                while p:
                    if p.hasNext():
                        p.moveToNext()
                        break  # found
                    p.moveToParent()
                # not found.
        return p
    #@+node:ekr.20150316175921.7: *5* p.checkChild
    #@+node:ekr.20040303175026: *3* p.Moving, Inserting, Deleting, Cloning, Sorting
    #@+node:ekr.20040303175026.8: *4* p.clone
    def clone(self):
        """Create a clone of back.

        Returns the newly created position."""
        p = self
        p2 = p.copy()  # Do *not* copy the VNode!
        p2._linkAfter(p)  # This should "just work"
        return p2
    #@+node:ekr.20040117171654: *4* p.copy
    def copy(self):
        """"Return an independent copy of a position."""
        return Position(self.v, self._childIndex, self.stack)
    #@+node:ekr.20040303175026.9: *4* p.copyTreeAfter, copyTreeTo
    # These used by unit tests, by the group_operations plugin,
    # and by the files-compare-leo-files command.

    # To do: use v.copyTree instead.

    def copyTreeAfter(self, copyGnxs=False):
        """Copy p and insert it after itself."""
        p = self
        p2 = p.insertAfter()
        p.copyTreeFromSelfTo(p2, copyGnxs=copyGnxs)
        return p2
        

    def copyTreeFromSelfTo(self, p2, copyGnxs=False):
        p = self
        p2.v._headString = g.toUnicode(p.h, reportErrors=True)  # 2017/01/24
        p2.v._bodyString = g.toUnicode(p.b, reportErrors=True)  # 2017/01/24
        #
        # #1019794: p.copyTreeFromSelfTo, should deepcopy p.v.u.
        #
        # Transcrypt doesn't support Python's copy module.
        # __pragma__ ('skip')
        p2.v.u = copy.deepcopy(p.v.u)
        # __pragma__ ('noskip')
        #
        if copyGnxs:
            p2.v.fileIndex = p.v.fileIndex
        # 2009/10/02: no need to copy arg to iter
        for child in p.children():
            child2 = p2.insertAsLastChild()
            child.copyTreeFromSelfTo(child2, copyGnxs=copyGnxs)
    #@+node:ekr.20160502095354.1: *4* p.copyWithNewVnodes
    def copyWithNewVnodes(self, copyMarked=False):
        """
        Return an **unliked** copy of p with a new vnode v.
        The new vnode is complete copy of v and all its descendants.
        """
        p = self
        return Position(v=p.v.copyTree(copyMarked))
    #@+node:peckj.20131023115434.10115: *4* p.createNodeHierarchy
    def createNodeHierarchy(self, heads, forcecreate=False):
        """ Create the proper hierarchy of nodes with headlines defined in
            'heads' as children of the current position

            params:
            heads - list of headlines in order to create, i.e. ['foo','bar','baz']
                    will create:
                      self
                      -foo
                      --bar
                      ---baz
            forcecreate - If False (default), will not create nodes unless they don't exist
                          If True, will create nodes regardless of existing nodes
            returns the final position ('baz' in the above example)
        """
        c = self.v.context
        return c.createNodeHierarchy(heads, parent=self, forcecreate=forcecreate)
    #@+node:ekr.20131230090121.16552: *4* p.deleteAllChildren
    def deleteAllChildren(self):
        """
        Delete all children of the receiver and set p.dirty().
        """
        p = self
        p.setDirty()  # Mark @file nodes dirty!
        while p.hasChildren():
            p.firstChild().doDelete()
    #@+node:ekr.20040303175026.2: *4* p.doDelete
    def doDelete(self, newNode=None):
        """
        Deletes position p from the outline.
        
        This is the main delete routine.
        It deletes the receiver's entire tree from the screen.
        Because of the undo command we never actually delete vnodes.
        """
        p = self
        p.setDirty()  # Mark @file nodes dirty!
        sib = p.copy()
        while sib.hasNext():
            sib.moveToNext()
            if sib == newNode:
                # Adjust newNode._childIndex if newNode is a following sibling of p.
                newNode._childIndex -= 1
                break
        p._unlink()
    #@+node:ekr.20040303175026.3: *4* p.insertAfter
    def insertAfter(self):
        """
        Inserts a new position after self.

        Returns the newly created position.
        """
        p = self; context = p.v.context
        p2 = self.copy()
        p2.v = VNode(context=context)
        p2.v.iconVal = 0
        p2._linkAfter(p)
        return p2
    #@+node:ekr.20040303175026.4: *4* p.insertAsLastChild
    def insertAsLastChild(self):
        """Inserts a new VNode as the last child of self.

        Returns the newly created position."""
        p = self
        n = p.numberOfChildren()
        return p.insertAsNthChild(n)
    #@+node:ekr.20040303175026.5: *4* p.insertAsNthChild
    def insertAsNthChild(self, n):
        """
        Inserts a new node as the the nth child of self.
        self must have at least n-1 children.

        Returns the newly created position.
        """
        p = self; context = p.v.context
        p2 = self.copy()
        p2.v = VNode(context=context)
        p2.v.iconVal = 0
        p2._linkAsNthChild(p, n)
        return p2
    #@+node:ekr.20130923111858.11572: *4* p.insertBefore
    def insertBefore(self):
        """Inserts a new position before self.

        Returns the newly created position.

        """
        p = self
        parent = p.parent()
        if p.hasBack():
            back = p.getBack()
            p = back.insertAfter()
        elif parent:
            p = parent.insertAsNthChild(0)
        else:
            p = p.insertAfter()
            p.moveToRoot()
        return p
    #@+node:ekr.20040310062332.1: *4* p.invalidOutline
    def invalidOutline(self, message):
        p = self
        if p.hasParent():
            node = p.parent()
        else:
            node = p
        p.v.context.alert(f"invalid outline: {message}\n{node}")
    #@+node:ekr.20040303175026.10: *4* p.moveAfter
    def moveAfter(self, a):
        """Move a position after position a."""
        p = self  # Do NOT copy the position!
        a._adjustPositionBeforeUnlink(p)
        p._unlink()
        p._linkAfter(a)
        return p
    #@+node:ekr.20040306060312: *4* p.moveToFirst/LastChildOf
    def moveToFirstChildOf(self, parent):
        """Move a position to the first child of parent."""
        p = self  # Do NOT copy the position!
        return p.moveToNthChildOf(parent, 0)  # Major bug fix: 2011/12/04

    def moveToLastChildOf(self, parent):
        """Move a position to the last child of parent."""
        p = self  # Do NOT copy the position!
        n = parent.numberOfChildren()
        if p.parent() == parent:
            n -= 1  # 2011/12/10: Another bug fix.
        return p.moveToNthChildOf(parent, n)  # Major bug fix: 2011/12/04
    #@+node:ekr.20040303175026.11: *4* p.moveToNthChildOf
    def moveToNthChildOf(self, parent, n):
        """Move a position to the nth child of parent."""
        p = self  # Do NOT copy the position!
        parent._adjustPositionBeforeUnlink(p)
        p._unlink()
        p._linkAsNthChild(parent, n)
        return p
    #@+node:ekr.20040303175026.6: *4* p.moveToRoot (changed)
    def moveToRoot(self):
        """Move self to the root position."""
        p = self  # Do NOT copy the position!
        #
        # #1631. The old root can not possibly be affected by unlinking p.
        p._unlink()
        p._linkAsRoot()
        return p
    #@+node:ekr.20180123062833.1: *4* p.promote
    def promote(self):
        """A low-level promote helper."""
        p = self  # Do NOT copy the position.
        parent_v = p._parentVnode()
        children = p.v.children
        # Add the children to parent_v's children.
        n = p.childIndex() + 1
        z = parent_v.children[:]
        parent_v.children = z[:n]
        parent_v.children.extend(children)
        parent_v.children.extend(z[n:])
        # Remove v's children.
        p.v.children = []
        # Adjust the parent links in the moved children.
        # There is no need to adjust descendant links.
        for child in children:
            child.parents.remove(p.v)
            child.parents.append(parent_v)
    #@+node:ekr.20040303175026.13: *4* p.validateOutlineWithParent
    # This routine checks the structure of the receiver's tree.

    def validateOutlineWithParent(self, pv):
        p = self
        result = True  # optimists get only unpleasant surprises.
        parent = p.getParent()
        childIndex = p._childIndex
        #@+<< validate parent ivar >>
        #@+node:ekr.20040303175026.14: *5* << validate parent ivar >>
        if parent != pv:
            p.invalidOutline("Invalid parent link: " + repr(parent))
        #@-<< validate parent ivar >>
        #@+<< validate childIndex ivar >>
        #@+node:ekr.20040303175026.15: *5* << validate childIndex ivar >>
        if pv:
            if childIndex < 0:
                p.invalidOutline("missing childIndex" + childIndex)
            elif childIndex >= pv.numberOfChildren():
                p.invalidOutline("missing children entry for index: " + childIndex)
        elif childIndex < 0:
            p.invalidOutline("negative childIndex" + childIndex)
        #@-<< validate childIndex ivar >>
        #@+<< validate x ivar >>
        #@+node:ekr.20040303175026.16: *5* << validate x ivar >>
        if not p.v and pv:
            self.invalidOutline("Empty t")
        #@-<< validate x ivar >>
        # Recursively validate all the children.
        for child in p.children():
            r = child.validateOutlineWithParent(p)
            if not r: result = False
        return result
    #@+node:ekr.20090128083459.74: *3* p.Properties
    #@+node:ekr.20090128083459.75: *4* p.b property
    def __get_b(self):
        """Return the body text of a position."""
        p = self
        return p.bodyString()

    def __set_b(self, val):
        """
        Set the body text of a position.

        **Warning: the p.b = whatever is *expensive* because it calls
        c.setBodyString().

        Usually, code *should* use this setter, despite its cost, because it
        update's Leo's outline pane properly. Calling c.redraw() is *not*
        enough.

        This performance gotcha becomes important for repetitive commands, like
        cff, replace-all and recursive import. In such situations, code should
        use p.v.b instead of p.b.
        """
        p = self
        c = p.v and p.v.context
        if c:
            c.setBodyString(p, val)
            # Warning: c.setBodyString is *expensive*.

    b = property(
        __get_b, __set_b,
        doc="position body string property")
    #@+node:ekr.20090128083459.76: *4* p.h property
    def __get_h(self):
        p = self
        return p.headString()

    def __set_h(self, val):
        """
        Set the headline text of a position.

        **Warning: the p.h = whatever is *expensive* because it calls
        c.setHeadString().

        Usually, code *should* use this setter, despite its cost, because it
        update's Leo's outline pane properly. Calling c.redraw() is *not*
        enough.

        This performance gotcha becomes important for repetitive commands, like
        cff, replace-all and recursive import. In such situations, code should
        use p.v.h instead of p.h.
        """
        p = self
        c = p.v and p.v.context
        if c:
            c.setHeadString(p, val)
            # Warning: c.setHeadString is *expensive*.

    h = property(
        __get_h, __set_h,
        doc="position property returning the headline string")
    #@+node:ekr.20090215165030.3: *4* p.gnx property
    def __get_gnx(self):
        p = self
        return p.v.fileIndex

    gnx = property(
        __get_gnx,  # __set_gnx,
        doc="position gnx property")
    #@+node:ekr.20140203082618.15486: *4* p.script property
    def __get_script(self):
        p = self
        return g.getScript(p.v.context, p,
            useSelectedText=False,  # Always return the entire expansion.
            forcePythonSentinels=True,
            useSentinels=False)

    script = property(
        __get_script,  # __set_script,
        doc="position property returning the script formed by p and its descendants")
    #@+node:ekr.20140218040104.16761: *4* p.nosentinels property
    def __get_nosentinels(self):
        p = self
        return ''.join([z for z in g.splitLines(p.b) if not g.isDirective(z)])

    nosentinels = property(
        __get_nosentinels,  # __set_nosentinels
        doc="position property returning the body text without sentinels")
    #@+node:ekr.20160129073222.1: *4* p.u Property
    def __get_u(self):
        p = self
        return p.v.u

    def __set_u(self, val):
        p = self
        p.v.u = val

    u = property(
        __get_u, __set_u,
        doc="p.u property")
    #@+node:ekr.20040305222924: *3* p.Setters
    #@+node:ekr.20040306220634: *4* p.VNode proxies
    #@+node:ekr.20131222112420.16371: *5* p.contract/expand/isExpanded
    def contract(self):
        """Contract p.v and clear p.v.expandedPositions list."""
        p, v = self, self.v
        v.expandedPositions = [z for z in v.expandedPositions if z != p]
        v.contract()

    def expand(self):
        p = self
        v = self.v
        v.expandedPositions = [z for z in v.expandedPositions if z != p]
        for p2 in v.expandedPositions:
            if p == p2:
                break
        else:
            v.expandedPositions.append(p.copy())
        v.expand()

    def isExpanded(self):
        p = self
        if p.isCloned():
            c = p.v.context
            return c.shouldBeExpanded(p)
        return p.v.isExpanded()
    #@+node:ekr.20040306220634.9: *5* p.Status bits
    # Clone bits are no longer used.
    # Dirty bits are handled carefully by the position class.

    def clearMarked(self): return self.v.clearMarked()

    def clearOrphan(self): return self.v.clearOrphan()

    def clearVisited(self): return self.v.clearVisited()

    def initExpandedBit(self): return self.v.initExpandedBit()

    def initMarkedBit(self): return self.v.initMarkedBit()

    def initStatus(self, status): return self.v.initStatus(status)

    def setMarked(self): return self.v.setMarked()

    def setOrphan(self): return self.v.setOrphan()

    def setSelected(self): return self.v.setSelected()

    def setVisited(self): return self.v.setVisited()
    #@+node:ekr.20040306220634.8: *5* p.computeIcon & p.setIcon
    def computeIcon(self):
        return self.v.computeIcon()

    def setIcon(self):
        pass  # Compatibility routine for old scripts
    #@+node:ekr.20040306220634.29: *5* p.setSelection
    def setSelection(self, start, length):
        return self.v.setSelection(start, length)
    #@+node:ekr.20100303074003.5637: *5* p.restore/saveCursorAndScroll
    def restoreCursorAndScroll(self):
        self.v.restoreCursorAndScroll()

    def saveCursorAndScroll(self):
        self.v.saveCursorAndScroll()
    #@+node:ekr.20040315034158: *4* p.setBodyString & setHeadString
    def setBodyString(self, s):
        p = self
        return p.v.setBodyString(s)

    initBodyString = setBodyString
    setTnodeText = setBodyString
    scriptSetBodyString = setBodyString

    def initHeadString(self, s):
        p = self
        p.v.initHeadString(s)

    def setHeadString(self, s):
        p = self
        p.v.initHeadString(s)
        p.setDirty()
    #@+node:ekr.20040312015908: *4* p.Visited bits
    #@+node:ekr.20040306220634.17: *5* p.clearVisitedInTree
    # Compatibility routine for scripts.

    def clearVisitedInTree(self):
        for p in self.self_and_subtree(copy=False):
            p.clearVisited()
    #@+node:ekr.20031218072017.3388: *5* p.clearAllVisitedInTree
    def clearAllVisitedInTree(self):
        for p in self.self_and_subtree(copy=False):
            p.v.clearVisited()
            p.v.clearWriteBit()
    #@+node:ekr.20040305162628: *4* p.Dirty bits
    #@+node:ekr.20040311113514: *5* p.clearDirty
    def clearDirty(self):
        """(p) Set p.v dirty."""
        p = self
        p.v.clearDirty()
    #@+node:ekr.20040702104823: *5* p.inAtIgnoreRange
    def inAtIgnoreRange(self):
        """Returns True if position p or one of p's parents is an @ignore node."""
        p = self
        for p in p.self_and_parents(copy=False):
            if p.isAtIgnoreNode():
                return True
        return False
    #@+node:ekr.20040303214038: *5* p.setAllAncestorAtFileNodesDirty
    def setAllAncestorAtFileNodesDirty(self):
        """
        Set all ancestor @<file> nodes dirty, including ancestors of all clones of p.
        """
        p = self
        p.v.setAllAncestorAtFileNodesDirty()
    #@+node:ekr.20040303163330: *5* p.setDirty
    def setDirty(self):
        """
        Mark a node and all ancestor @file nodes dirty.

        p.setDirty() is no longer expensive.
        """
        p = self
        p.v.setAllAncestorAtFileNodesDirty()
        p.v.setDirty()
    #@+node:ekr.20160225153333.1: *3* p.Predicates
    #@+node:ekr.20160225153414.1: *4* p.is_at_all & is_at_all_tree
    def is_at_all(self):
        """Return True if p.b contains an @all directive."""
        p = self
        return (
            p.isAnyAtFileNode() and
            any([g.match_word(s, 0, '@all') for s in g.splitLines(p.b)]))

    def in_at_all_tree(self):
        """Return True if p or one of p's ancestors is an @all node."""
        p = self
        for p in p.self_and_parents(copy=False):
            if p.is_at_all():
                return True
        return False
    #@+node:ekr.20160225153430.1: *4* p.is_at_ignore & in_at_ignore_tree
    def is_at_ignore(self):
        """Return True if p is an @ignore node."""
        p = self
        return g.match_word(p.h, 0, '@ignore')

    def in_at_ignore_tree(self):
        """Return True if p or one of p's ancestors is an @ignore node."""
        p = self
        for p in p.self_and_parents(copy=False):
            if g.match_word(p.h, 0, '@ignore'):
                return True
        return False
    #@-others
position = Position  # compatibility.
#@+node:ville.20090311190405.68: ** class PosList (leoNodes.py)
class PosList(list):
    #@+others
    #@+node:bob.20101215134608.5897: *3* children
    def children(self):
        """ Return a PosList instance containing pointers to
        all the immediate children of nodes in PosList self.
        """
        res = PosList()
        for p in self:
            for child_p in p.children():
                res.append(child_p.copy())
        return res
    #@+node:ville.20090311190405.69: *3* filter_h
    def filter_h(self, regex, flags=re.IGNORECASE):
        """ Find all the nodes in PosList self where zero or more characters at
        the beginning of the headline match regex

        """
        pat = re.compile(regex, flags)
        res = PosList()
        for p in self:
            mo = re.match(pat, p.h)
            if mo:
                pc = p.copy()
                pc.mo = mo
                res.append(pc)
        return res
    #@+node:ville.20090311195550.1: *3* filter_b
    def filter_b(self, regex, flags=re.IGNORECASE):
        """ Find all the nodes in PosList self where body matches regex
        one or more times.

        """
        pat = re.compile(regex, flags)
        res = PosList()
        for p in self:
            m = re.finditer(pat, p.b)
            t1, t2 = itertools.tee(m, 2)
            try:
                t1.__next__()
                pc = p.copy()
                pc.matchiter = t2
                res.append(pc)
            except StopIteration:
                pass
        return res
    #@-others
Poslist = PosList  # compatibility.
#@+node:ekr.20031218072017.3341: ** class VNode
#@@nobeautify

class VNode:
    #@+<< VNode constants >>
    #@+node:ekr.20031218072017.951: *3* << VNode constants >>
    # Define the meaning of status bits in new vnodes.
    # Archived...
    clonedBit = 0x01  # True: VNode has clone mark.
    # unused      0x02
    expandedBit = 0x04  # True: VNode is expanded.
    markedBit = 0x08  # True: VNode is marked
    # unused    = 0x10 # (was orphanBit)
    selectedBit = 0x20  # True: VNode is current VNode.
    topBit = 0x40  # True: VNode was top VNode when saved.
    # Not archived...
    richTextBit = 0x080  # Determines whether we use <bt> or <btr> tags.
    visitedBit = 0x100
    dirtyBit = 0x200
    writeBit = 0x400
    orphanBit = 0x800  # True: error in @<file> tree prevented it from being written.
    #@-<< VNode constants >>
    #@+others
    #@+node:ekr.20031218072017.3342: *3* v.Birth & death
    #@+node:ekr.20031218072017.3344: *4* v.__init
    def __init__(self, context, gnx=None):
        """
        Ctor for the VNode class.
        To support ZODB, the code must set v._p_changed = 1 whenever
        v.unknownAttributes or any mutable VNode object changes.
        """
        # The primary data: headline and body text.
        self._headString = 'newHeadline'
        self._bodyString = ''
        # Structure data...
        self.children = []
            # Ordered list of all children of this node.
        self.parents = []
            # Unordered list of all parents of this node.
        # Other essential data...
        self.fileIndex = None
            # The immutable fileIndex (gnx) for this node. Set below.
        self.iconVal = 0
            # The present value of the node's icon.
        self.statusBits = 0
            # status bits
        # Information that is never written to any file...
        self.context = context  # The context containing context.hiddenRootNode.
            # Required so we can compute top-level siblings.
            # It is named .context rather than .c to emphasize its limited usage.
        self.expandedPositions = []
            # Positions that should be expanded.
        self.insertSpot = None
            # Location of previous insert point.
        self.scrollBarSpot = None
            # Previous value of scrollbar position.
        self.selectionLength = 0
            # The length of the selected body text.
        self.selectionStart = 0
            # The start of the selected body text.
        # To make VNode's independent of Leo's core,
        # wrap all calls to the VNode ctor::
        #
        #   def allocate_vnode(c,gnx):
        #       v = VNode(c)
        #       g.app.nodeIndices.new_vnode_helper(c,gnx,v)
        g.app.nodeIndices.new_vnode_helper(context, gnx, self)
        assert self.fileIndex, g.callers()
    #@+node:ekr.20031218072017.3345: *4* v.__repr__ & v.__str__
    def __repr__(self):
        return f"<VNode {self.gnx} {self.headString()}>"

    __str__ = __repr__
    #@+node:ekr.20040312145256: *4* v.dump
    def dumpLink(self, link):
        return link if link else "<none>"

    def dump(self, label=""):
        v = self
        s = '-' * 10
        print(f"{s} {label} {v}")
        # print('gnx: %s' % v.gnx)
        print(f"len(parents): {len(v.parents)}")
        print(f"len(children): {len(v.children)}")
        print(f"parents: {g.listToString(v.parents)}")
        print(f"children: {g.listToString(v.children)}")
    #@+node:ekr.20031218072017.3346: *3* v.Comparisons
    #@+node:ekr.20040705201018: *4* v.findAtFileName
    def findAtFileName(self, names, h=''):
        """Return the name following one of the names in nameList or """ ""
        # Allow h argument for unit testing.
        if not h:
            h = self.headString()
        if not g.match(h, 0, '@'):
            return ""
        i = g.skip_id(h, 1, '-')
        word = h[:i]
        if word in names and g.match_word(h, 0, word):
            name = h[i:].strip()
            return name
        return ""
    #@+node:ekr.20031218072017.3350: *4* v.anyAtFileNodeName
    def anyAtFileNodeName(self):
        """Return the file name following an @file node or an empty string."""
        return (
            self.findAtFileName(g.app.atAutoNames) or
            self.findAtFileName(g.app.atFileNames))
    #@+node:ekr.20031218072017.3348: *4* v.at...FileNodeName
    # These return the filename following @xxx, in v.headString.
    # Return the the empty string if v is not an @xxx node.

    def atAutoNodeName(self, h=None):
        return self.findAtFileName(g.app.atAutoNames, h=h)

    # Retain this special case as part of the "escape hatch".
    # That is, we fall back on code in leoRst.py if no
    # importer or writer for reStructuredText exists.

    def atAutoRstNodeName(self, h=None):
        names = ("@auto-rst",)
        return self.findAtFileName(names, h=h)

    def atCleanNodeName(self):
        names = ("@clean",)
        return self.findAtFileName(names)

    def atEditNodeName(self):
        names = ("@edit",)
        return self.findAtFileName(names)

    def atFileNodeName(self):
        names = ("@file", "@thin")
            # Fix #403.
        return self.findAtFileName(names)

    def atNoSentinelsFileNodeName(self):
        names = ("@nosent", "@file-nosent",)
        return self.findAtFileName(names)

    def atRstFileNodeName(self):
        names = ("@rst",)
        return self.findAtFileName(names)

    def atShadowFileNodeName(self):
        names = ("@shadow",)
        return self.findAtFileName(names)

    def atSilentFileNodeName(self):
        names = ("@asis", "@file-asis",)
        return self.findAtFileName(names)

    def atThinFileNodeName(self):
        names = ("@thin", "@file-thin",)
        return self.findAtFileName(names)

    # New names, less confusing

    atNoSentFileNodeName = atNoSentinelsFileNodeName
    atAsisFileNodeName = atSilentFileNodeName
    #@+node:EKR.20040430152000: *4* v.isAtAllNode
    def isAtAllNode(self):
        """Returns True if the receiver contains @others in its body at the start of a line."""
        flag, i = g.is_special(self._bodyString, "@all")
        return flag
    #@+node:ekr.20040326031436: *4* v.isAnyAtFileNode
    def isAnyAtFileNode(self):
        """Return True if v is any kind of @file or related node."""
        # This routine should be as fast as possible.
        # It is called once for every VNode when writing a file.
        h = self.headString()
        return h and h[0] == '@' and self.anyAtFileNodeName()
    #@+node:ekr.20040325073709: *4* v.isAt...FileNode
    def isAtAutoNode(self):
        return bool(self.atAutoNodeName())

    def isAtAutoRstNode(self):
        return bool(self.atAutoRstNodeName())

    def isAtCleanNode(self):
        return bool(self.atCleanNodeName())

    def isAtEditNode(self):
        return bool(self.atEditNodeName())

    def isAtFileNode(self):
        return bool(self.atFileNodeName())

    def isAtRstFileNode(self):
        return bool(self.atRstFileNodeName())

    def isAtNoSentinelsFileNode(self):
        return bool(self.atNoSentinelsFileNodeName())

    def isAtSilentFileNode(self):  # @file-asis
        return bool(self.atSilentFileNodeName())

    def isAtShadowFileNode(self):
        return bool(self.atShadowFileNodeName())

    def isAtThinFileNode(self):
        return bool(self.atThinFileNodeName())

    # New names, less confusing:

    isAtNoSentFileNode = isAtNoSentinelsFileNode
    isAtAsisFileNode = isAtSilentFileNode
    #@+node:ekr.20031218072017.3351: *4* v.isAtIgnoreNode
    def isAtIgnoreNode(self):
        """
        Returns True if:
            
        - the vnode' body contains @ignore at the start of a line or

        - the vnode's headline starts with @ignore.
        """
        # v = self
        if g.match_word(self._headString, 0, '@ignore'):
            return True
        flag, i = g.is_special(self._bodyString, "@ignore")
        return flag
    #@+node:ekr.20031218072017.3352: *4* v.isAtOthersNode
    def isAtOthersNode(self):
        """Returns True if the receiver contains @others in its body at the start of a line."""
        flag, i = g.is_special(self._bodyString, "@others")
        return flag
    #@+node:ekr.20031218072017.3353: *4* v.matchHeadline
    def matchHeadline(self, pattern):
        """Returns True if the headline matches the pattern ignoring whitespace and case.

        The headline may contain characters following the successfully matched pattern."""
        v = self
        h = g.toUnicode(v.headString())
        h = h.lower().replace(' ', '').replace('\t', '')
        h = h.lstrip('.')  # 2013/04/05. Allow leading period before section names.
        pattern = g.toUnicode(pattern)
        pattern = pattern.lower().replace(' ', '').replace('\t', '')
        return h.startswith(pattern)
    #@+node:ekr.20160502100151.1: *3* v.copyTree

    def copyTree(self, copyMarked=False):
        """
        Return an all-new tree of vnodes that are copies of self and all its
        descendants.

        **Important**: the v.parents ivar must be [] for all nodes.
        v._addParentLinks will set all parents.
        """
        v = self
        # Allocate a new vnode and gnx with empty children & parents.
        v2 = VNode(context=v.context, gnx=None)
        assert v2.parents == [], v2.parents
        assert v2.gnx
        assert v.gnx != v2.gnx
        # Copy vnode fields. Do **not** set v2.parents.
        v2._headString = g.toUnicode(v._headString, reportErrors=True)
        v2._bodyString = g.toUnicode(v._bodyString, reportErrors=True)
        #
        # Transcrypt doesn't support Python's copy module.
        # __pragma__ ('skip')
        v2.u = copy.deepcopy(v.u)
        # __pragma__ ('noskip')
        #
        if copyMarked and v.isMarked():
            v2.setMarked()
        # Recursively copy all descendant vnodes.
        for child in v.children:
            v2.children.append(child.copyTree(copyMarked))
        return v2
    #@+node:ekr.20031218072017.3359: *3* v.Getters
    #@+node:ekr.20031218072017.3378: *4* v.bodyString
    body_unicode_warning = False

    def bodyString(self):
        # This message should never be printed and we want to avoid crashing here!
        if isinstance(self._bodyString, str):
            return self._bodyString
        if not self.body_unicode_warning:
            self.body_unicode_warning = True
            g.internalError('not unicode:', repr(self._bodyString), self._headString)
        return g.toUnicode(self._bodyString)

    getBody = bodyString
        # Deprecated, but here for compatibility.
    #@+node:ekr.20031218072017.3360: *4* v.Children
    #@+node:ekr.20031218072017.3362: *5* v.firstChild
    def firstChild(self):
        v = self
        return v.children and v.children[0]
    #@+node:ekr.20040307085922: *5* v.hasChildren & hasFirstChild
    def hasChildren(self):
        v = self
        return len(v.children) > 0

    hasFirstChild = hasChildren
    #@+node:ekr.20031218072017.3364: *5* v.lastChild
    def lastChild(self):
        v = self
        return v.children[-1] if v.children else None
    #@+node:ekr.20031218072017.3365: *5* v.nthChild
    # childIndex and nthChild are zero-based.

    def nthChild(self, n):
        v = self
        if 0 <= n < len(v.children):
            return v.children[n]
        return None
    #@+node:ekr.20031218072017.3366: *5* v.numberOfChildren
    def numberOfChildren(self):
        v = self
        return len(v.children)
    #@+node:ekr.20040323100443: *4* v.directParents
    def directParents(self):
        """(New in 4.2) Return a list of all direct parent vnodes of a VNode.

        This is NOT the same as the list of ancestors of the VNode."""
        v = self
        return v.parents
    #@+node:ekr.20080429053831.6: *4* v.hasBody
    def hasBody(self):
        """Return True if this VNode contains body text."""
        s = self._bodyString
        return s and len(s) > 0
    #@+node:ekr.20031218072017.1581: *4* v.headString
    head_unicode_warning = False

    def headString(self):
        """Return the headline string."""
        # This message should never be printed and we want to avoid crashing here!
        if isinstance(self._headString, str):
            return self._headString
        if not self.head_unicode_warning:
            self.head_unicode_warning = True
            g.internalError('not a string', repr(self._headString))
        return g.toUnicode(self._headString)
    #@+node:ekr.20131223064351.16351: *4* v.isNthChildOf
    def isNthChildOf(self, n, parent_v):
        """Return True if v is the n'th child of parent_v."""
        v = self
        children = parent_v and parent_v.children
        return children and 0 <= n < len(children) and children[n] == v
    #@+node:ekr.20031218072017.3367: *4* v.Status Bits
    #@+node:ekr.20031218072017.3368: *5* v.isCloned
    def isCloned(self):
        return len(self.parents) > 1
    #@+node:ekr.20031218072017.3369: *5* v.isDirty
    def isDirty(self):
        return (self.statusBits & self.dirtyBit) != 0
    #@+node:ekr.20031218072017.3371: *5* v.isMarked
    def isMarked(self):
        return (self.statusBits & VNode.markedBit) != 0
    #@+node:ekr.20031218072017.3372: *5* v.isOrphan
    def isOrphan(self):
        return (self.statusBits & VNode.orphanBit) != 0
    #@+node:ekr.20031218072017.3373: *5* v.isSelected
    def isSelected(self):
        return (self.statusBits & VNode.selectedBit) != 0
    #@+node:ekr.20031218072017.3374: *5* v.isTopBitSet
    def isTopBitSet(self):
        return (self.statusBits & self.topBit) != 0
    #@+node:ekr.20031218072017.3376: *5* v.isVisited
    def isVisited(self):
        return (self.statusBits & VNode.visitedBit) != 0
    #@+node:ekr.20080429053831.10: *5* v.isWriteBit
    def isWriteBit(self):
        v = self
        return (v.statusBits & v.writeBit) != 0
    #@+node:ekr.20031218072017.3377: *5* v.status
    def status(self):
        return self.statusBits
    #@+node:ekr.20031218072017.3384: *3* v.Setters
    #@+node:ekr.20090830051712.6151: *4*  v.Dirty bits
    #@+node:ekr.20031218072017.3390: *5* v.clearDirty
    def clearDirty(self):
        """Clear the vnode dirty bit."""
        v = self
        v.statusBits &= ~v.dirtyBit
    #@+node:ekr.20080429053831.12: *5* v.setDirty
    def setDirty(self):
        """
        Set the vnode dirty bit.
        
        This method is fast, but dangerous. Unlike p.setDirty, this method does
        not call v.setAllAncestorAtFileNodesDirty.
        """
        self.statusBits |= self.dirtyBit
    #@+node:ekr.20031218072017.3386: *4*  v.Status bits
    #@+node:ekr.20031218072017.3389: *5* v.clearClonedBit
    def clearClonedBit(self):
        self.statusBits &= ~self.clonedBit
    #@+node:ekr.20031218072017.3391: *5* v.clearMarked
    def clearMarked(self):
        self.statusBits &= ~self.markedBit
    #@+node:ekr.20080429053831.8: *5* v.clearWriteBit
    def clearWriteBit(self):
        self.statusBits &= ~self.writeBit
    #@+node:ekr.20031218072017.3392: *5* v.clearOrphan
    def clearOrphan(self):
        # if self.h.startswith('@file'): g.trace(self.h,g.callers())
        self.statusBits &= ~self.orphanBit
    #@+node:ekr.20031218072017.3393: *5* v.clearVisited
    def clearVisited(self):
        self.statusBits &= ~self.visitedBit
    #@+node:ekr.20031218072017.3395: *5* v.contract/expand/initExpandedBit/isExpanded
    def contract(self):
        """Contract the node."""
        self.statusBits &= ~self.expandedBit

    def expand(self):
        """Expand the node."""
        self.statusBits |= self.expandedBit

    def initExpandedBit(self):
        """Init self.statusBits."""
        self.statusBits |= self.expandedBit

    def isExpanded(self):
        """Return True if the VNode expansion bit is set."""
        return (self.statusBits & self.expandedBit) != 0
    #@+node:ekr.20031218072017.3396: *5* v.initStatus
    def initStatus(self, status):
        self.statusBits = status
    #@+node:ekr.20031218072017.3397: *5* v.setClonedBit & initClonedBit
    def setClonedBit(self):
        self.statusBits |= self.clonedBit

    def initClonedBit(self, val):
        if val:
            self.statusBits |= self.clonedBit
        else:
            self.statusBits &= ~self.clonedBit
    #@+node:ekr.20031218072017.3398: *5* v.setMarked & initMarkedBit
    def setMarked(self):
        self.statusBits |= self.markedBit

    def initMarkedBit(self):
        self.statusBits |= self.markedBit
    #@+node:ekr.20031218072017.3399: *5* v.setOrphan
    def setOrphan(self):
        """Set the vnode's orphan bit."""
        self.statusBits |= self.orphanBit
    #@+node:ekr.20031218072017.3400: *5* v.setSelected
    # This only sets the selected bit.

    def setSelected(self):
        self.statusBits |= self.selectedBit
    #@+node:ekr.20031218072017.3401: *5* v.setVisited
    # Compatibility routine for scripts

    def setVisited(self):
        self.statusBits |= self.visitedBit
    #@+node:ekr.20080429053831.9: *5* v.setWriteBit
    def setWriteBit(self):
        self.statusBits |= self.writeBit
    #@+node:ville.20120502221057.7499: *4* v.childrenModified
    def childrenModified(self):
        g.childrenModifiedSet.add(self)
    #@+node:ekr.20031218072017.3385: *4* v.computeIcon & setIcon
    def computeIcon(self):
        val = 0; v = self
        if v.hasBody(): val += 1
        if v.isMarked(): val += 2
        if v.isCloned(): val += 4
        if v.isDirty(): val += 8
        return val

    def setIcon(self):
        pass  # Compatibility routine for old scripts
    #@+node:ville.20120502221057.7498: *4* v.contentModified
    def contentModified(self):
        g.contentModifiedSet.add(self)
    #@+node:ekr.20100303074003.5636: *4* v.restoreCursorAndScroll
    # Called only by LeoTree.selectHelper.

    def restoreCursorAndScroll(self):
        """Restore the cursor position and scroll so it is visible."""
        traceTime = False and not g.unitTesting
        v = self
        ins = v.insertSpot
        # start, n = v.selectionStart, v.selectionLength
        spot = v.scrollBarSpot
        body = self.context.frame.body
        w = body.wrapper
        # Fix bug 981849: incorrect body content shown.
        if ins is None: ins = 0
        # This is very expensive for large text.
        if traceTime: t1 = time.time()
        if hasattr(body.wrapper, 'setInsertPoint'):
            w.setInsertPoint(ins)
        if traceTime:
            delta_t = time.time() - t1
            if delta_t > 0.1: g.trace(f"{delta_t:2.3f} sec")
        # Override any changes to the scrollbar setting that might
        # have been done above by w.setSelectionRange or w.setInsertPoint.
        if spot is not None:
            w.setYScrollPosition(spot)
            v.scrollBarSpot = spot
        # Never call w.see here.
    #@+node:ekr.20100303074003.5638: *4* v.saveCursorAndScroll
    def saveCursorAndScroll(self):

        v = self; c = v.context
        w = c.frame.body
        if not w:
            return
        try:
            v.scrollBarSpot = w.getYScrollPosition()
            v.insertSpot = w.getInsertPoint()
        except AttributeError:
            # 2011/03/21: w may not support the high-level interface.
            pass
    #@+node:ekr.20040315032144: *4* v.setBodyString & v.setHeadString
    unicode_warning_given = False

    def setBodyString(self, s):
        v = self
        if isinstance(s, str):
            v._bodyString = s
            return
        try:
            v._bodyString = g.toUnicode(s, reportErrors=True)
        except Exception:
            if not self.unicode_warning_given:
                self.unicode_warning_given = True
                g.internalError(s)
                g.es_exception()
        self.contentModified()  # #1413.
        signal_manager.emit(self.context, 'body_changed', self)

    def setHeadString(self, s):
        # Fix bug: https://bugs.launchpad.net/leo-editor/+bug/1245535
        # API allows headlines to contain newlines.
        v = self
        if g.isUnicode(s):
            v._headString = s.replace('\n', '')
            return
        s = g.toUnicode(s, reportErrors=True)
        v._headString = s.replace('\n', '')
        self.contentModified()  # #1413.

    initBodyString = setBodyString
    initHeadString = setHeadString
    setHeadText = setHeadString
    setTnodeText = setBodyString
    #@+node:ekr.20031218072017.3402: *4* v.setSelection
    def setSelection(self, start, length):
        v = self
        v.selectionStart = start
        v.selectionLength = length
    #@+node:ekr.20191213161023.1: *3* v.setAllAncestorAtFileNodesDirty
    def setAllAncestorAtFileNodesDirty(self):
        """
        Original idea by Виталије Милошевић (Vitalije Milosevic).
        
        Modified by EKR.
        """
        v = self
        hiddenRootVnode = v.context.hiddenRootNode

        def v_and_parents(v):
            if v != hiddenRootVnode:
                yield v
                for parent_v in v.parents:
                    yield from v_and_parents(parent_v)

        # There is no harm in calling v2.setDirty redundantly.

        for v2 in v_and_parents(v):
            if v2.isAnyAtFileNode():
                v2.setDirty()
    #@+node:ekr.20130524063409.10700: *3* v.Inserting & cloning
    def cloneAsNthChild(self, parent_v, n):
        # Does not check for illegal clones!
        v = self
        v._linkAsNthChild(parent_v, n)
        return v

    def insertAsFirstChild(self):
        v = self
        return v.insertAsNthChild(0)

    def insertAsLastChild(self):
        v = self
        return v.insertAsNthChild(len(v.children))

    def insertAsNthChild(self, n):
        v = self
        assert 0 <= n <= len(v.children)
        v2 = VNode(v.context)
        v2._linkAsNthChild(v, n)
        assert v.children[n] == v2
        return v2
    #@+node:ekr.20080427062528.9: *3* v.Low level methods
    #@+node:ekr.20180709175203.1: *4* v._addCopiedLink
    def _addCopiedLink(self, childIndex, parent_v):
        """Adjust links after adding a link to v."""
        v = self
        v.context.frame.tree.generation += 1
        parent_v.childrenModified()
            # For a plugin.
        # Update parent_v.children & v.parents.
        parent_v.children.insert(childIndex, v)
        v.parents.append(parent_v)
        # Set zodb changed flags.
        v._p_changed = 1
        parent_v._p_changed = 1
    #@+node:ekr.20090706110836.6135: *4* v._addLink & _addParentLinks
    def _addLink(self, childIndex, parent_v):
        """Adjust links after adding a link to v."""
        v = self
        v.context.frame.tree.generation += 1
        parent_v.childrenModified()
            # For a plugin.
        # Update parent_v.children & v.parents.
        parent_v.children.insert(childIndex, v)
        v.parents.append(parent_v)
        # Set zodb changed flags.
        v._p_changed = 1
        parent_v._p_changed = 1
        # If v has only one parent, we adjust all
        # the parents links in the descendant tree.
        # This handles clones properly when undoing a delete.
        if len(v.parents) == 1:
            for child in v.children:
                child._addParentLinks(parent=v)
    #@+node:ekr.20090804184658.6129: *5* v._addParentLinks
    def _addParentLinks(self, parent):

        v = self
        v.parents.append(parent)
        if len(v.parents) == 1:
            for child in v.children:
                child._addParentLinks(parent=v)
    #@+node:ekr.20090804184658.6128: *4* v._cutLink & _cutParentLinks
    def _cutLink(self, childIndex, parent_v):
        """Adjust links after cutting a link to v."""
        v = self
        v.context.frame.tree.generation += 1
        parent_v.childrenModified()
        assert parent_v.children[childIndex] == v
        del parent_v.children[childIndex]
        if parent_v in v.parents:
            try:
                v.parents.remove(parent_v)
            except ValueError:
                g.internalError(f"{parent_v} not in parents of {v}")
                g.trace('v.parents:')
                g.printObj(v.parents)
        v._p_changed = 1
        parent_v._p_changed = 1
        # If v has no more parents, we adjust all
        # the parent links in the descendant tree.
        # This handles clones properly when deleting a tree.
        if not v.parents:
            for child in v.children:
                child._cutParentLinks(parent=v)
    #@+node:ekr.20090804190529.6133: *5* v._cutParentLinks
    def _cutParentLinks(self, parent):

        v = self
        v.parents.remove(parent)
        if not v.parents:
            for child in v.children:
                child._cutParentLinks(parent=v)
    #@+node:ekr.20180709064515.1: *4* v._deleteAllChildren
    def _deleteAllChildren(self):
        """
        Delete all children of self.
        
        This is a low-level method, used by the read code.
        It is not intended as a general replacement for p.doDelete().
        """
        v = self
        for v2 in v.children:
            try:
                v2.parents.remove(v)
            except ValueError:
                g.internalError(f"{v} not in parents of {v2}")
                g.trace('v2.parents:')
                g.printObj(v2.parents)
        v.children = []
    #@+node:ekr.20031218072017.3425: *4* v._linkAsNthChild
    def _linkAsNthChild(self, parent_v, n):
        """Links self as the n'th child of VNode pv"""
        v = self  # The child node.
        v._addLink(n, parent_v)
    #@+node:ekr.20090130065000.1: *3* v.Properties
    #@+node:ekr.20090130114732.5: *4* v.b Property
    def __get_b(self):
        v = self
        return v.bodyString()

    def __set_b(self, val):
        v = self
        v.setBodyString(val)

    b = property(
        __get_b, __set_b,
        doc="VNode body string property")
    #@+node:ekr.20090130125002.1: *4* v.h property
    def __get_h(self):
        v = self
        return v.headString()

    def __set_h(self, val):
        v = self
        v.setHeadString(val)

    h = property(
        __get_h, __set_h,
        doc="VNode headline string property")
    #@+node:ekr.20090130114732.6: *4* v.u Property
    def __get_u(self):
        v = self
        # Wrong: return getattr(v, 'unknownAttributes', {})
        # It is does not set v.unknownAttributes, which can cause problems.
        if not hasattr(v, 'unknownAttributes'):
            v.unknownAttributes = {}
        return v.unknownAttributes

    def __set_u(self, val):
        v = self
        if val is None:
            if hasattr(v, 'unknownAttributes'):
                delattr(v, 'unknownAttributes')
        elif isinstance(val, dict):
            v.unknownAttributes = val
        else:
            raise ValueError

    u = property(
        __get_u, __set_u,
        doc="VNode u property")
    #@+node:ekr.20090215165030.1: *4* v.gnx Property
    def __get_gnx(self):
        v = self
        return v.fileIndex

    gnx = property(
        __get_gnx,  # __set_gnx,
        doc="VNode gnx property")
    #@-others
vnode = VNode  # compatibility.

#@@beautify
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo

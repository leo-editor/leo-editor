# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20211013081056.1: * @file ../unittests/commands/test_convertCommands.py
#@@first
"""Tests of leo.commands.leoConvertCommands."""
import re
from leo.core import leoGlobals as g
from leo.core.leoTest2 import LeoUnitTest
assert re  ###
assert g ###

#@+others
#@+node:ekr.20211013081200.1: ** class TestPythonToTypeScript(LeoUnitTest):
class TestPythonToTypeScript(LeoUnitTest):
    """Test cases for leo/commands/leoConvertCommands.py"""
    
   

    #@+others
    #@+node:ekr.20211013090653.1: *3*  test_py2ts.setUp
    def setUp(self):
        super().setUp()
        c = self.c
        self.x = c.convertCommands.PythonToTypescript(c)
        self.assertTrue(hasattr(self.x, 'convert'))
        root = self.root_p
        # Delete all children
        root.deleteAllChildren()
        # Past a copy of the Position class after the root.
        #@+<< define s >>
        #@+node:ekr.20211013090332.1: *4* << define s >>
        # A copy of Leo's Position class, renamed TestPosition.
        s = '''<?xml version="1.0" encoding="utf-8"?>
        <!-- Created by Leo: http://leoeditor.com/leo_toc.html -->
        <leo_file xmlns:leo="http://leoeditor.com/namespaces/leo-python-editor/1.1" >
        <leo_header file_format="2"/>
        <vnodes>
        <v t="ekr.20211013085956.1"><vh>class TestPosition</vh>
        <v t="ekr.20211013085956.3"><vh> p.ctor &amp; other special methods...</vh>
        <v t="ekr.20211013085956.4"><vh>p.__eq__ &amp; __ne__</vh></v>
        <v t="ekr.20211013085956.5"><vh> p.__init__</vh></v>
        <v t="ekr.20211013085956.6"><vh>p.__ge__ &amp; __le__&amp; __lt__</vh></v>
        <v t="ekr.20211013085956.7"><vh>p.__gt__</vh></v>
        <v t="ekr.20211013085956.8"><vh>p.__nonzero__ &amp; __bool__</vh></v>
        <v t="ekr.20211013085956.9"><vh>p.__str__ and p.__repr__</vh></v>
        <v t="ekr.20211013085956.10"><vh>p.archivedPosition</vh></v>
        <v t="ekr.20211013085956.11"><vh>p.dump</vh></v>
        <v t="ekr.20211013085956.12"><vh>p.key &amp; p.sort_key &amp; __hash__</vh></v>
        </v>
        <v t="ekr.20211013085956.13"><vh>p.File Conversion</vh>
        <v t="ekr.20211013085956.14"><vh>p.convertTreeToString</vh></v>
        <v t="ekr.20211013085956.15"><vh>p.moreHead</vh></v>
        <v t="ekr.20211013085956.16"><vh>p.moreBody</vh></v>
        </v>
        <v t="ekr.20211013085956.17"><vh>p.generators</vh>
        <v t="ekr.20211013085956.18"><vh>p.children</vh></v>
        <v t="ekr.20211013085956.19"><vh>p.following_siblings</vh></v>
        <v t="ekr.20211013085956.20"><vh>p.nearest_roots</vh></v>
        <v t="ekr.20211013085956.21"><vh>p.nearest_unique_roots (aka p.nearest)</vh></v>
        <v t="ekr.20211013085956.22"><vh>p.nodes</vh></v>
        <v t="ekr.20211013085956.23"><vh>p.parents</vh></v>
        <v t="ekr.20211013085956.24"><vh>p.self_and_parents</vh></v>
        <v t="ekr.20211013085956.25"><vh>p.self_and_siblings</vh></v>
        <v t="ekr.20211013085956.26"><vh>p.self_and_subtree</vh></v>
        <v t="ekr.20211013085956.27"><vh>p.subtree</vh></v>
        <v t="ekr.20211013085956.28"><vh>p.unique_nodes</vh></v>
        <v t="ekr.20211013085956.29"><vh>p.unique_subtree</vh></v>
        </v>
        <v t="ekr.20211013085956.30"><vh>p.Getters</vh>
        <v t="ekr.20211013085956.31"><vh>p.VNode proxies</vh>
        <v t="ekr.20211013085956.32"><vh>p.Comparisons</vh></v>
        <v t="ekr.20211013085956.33"><vh>p.Headline &amp; body strings</vh></v>
        <v t="ekr.20211013085956.34"><vh>p.Status bits</vh></v>
        </v>
        <v t="ekr.20211013085956.35"><vh>p.children &amp; parents</vh>
        <v t="ekr.20211013085956.36"><vh>p.childIndex</vh></v>
        <v t="ekr.20211013085956.37"><vh>p.directParents</vh></v>
        <v t="ekr.20211013085956.38"><vh>p.hasChildren &amp; p.numberOfChildren</vh></v>
        </v>
        <v t="ekr.20211013085956.39"><vh>p.getX &amp; VNode compatibility traversal routines</vh></v>
        <v t="ekr.20211013085956.40"><vh>p.get_UNL</vh></v>
        <v t="ekr.20211013085956.41"><vh>p.hasBack/Next/Parent/ThreadBack</vh>
        <v t="ekr.20211013085956.42"><vh>hasThreadNext (the only complex hasX method)</vh></v>
        </v>
        <v t="ekr.20211013085956.43"><vh>p.findRootPosition</vh></v>
        <v t="ekr.20211013085956.44"><vh>p.isAncestorOf</vh></v>
        <v t="ekr.20211013085956.45"><vh>p.isCloned</vh></v>
        <v t="ekr.20211013085956.46"><vh>p.isRoot</vh></v>
        <v t="ekr.20211013085956.47"><vh>p.isVisible</vh></v>
        <v t="ekr.20211013085956.48"><vh>p.level &amp; simpleLevel</vh></v>
        <v t="ekr.20211013085956.49"><vh>p.positionAfterDeletedTree</vh></v>
        <v t="ekr.20211013085956.50"><vh>p.textOffset</vh></v>
        </v>
        <v t="ekr.20211013085956.51"><vh>p.isOutsideAtFileTree</vh></v>
        <v t="ekr.20211013085956.52"><vh>p.Low level methods</vh>
        <v t="ekr.20211013085956.53"><vh>p._adjustPositionBeforeUnlink</vh></v>
        <v t="ekr.20211013085956.54"><vh>p._linkAfter</vh></v>
        <v t="ekr.20211013085956.55"><vh>p._linkCopiedAfter</vh></v>
        <v t="ekr.20211013085956.56"><vh>p._linkAsNthChild</vh></v>
        <v t="ekr.20211013085956.57"><vh>p._linkCopiedAsNthChild</vh></v>
        <v t="ekr.20211013085956.58"><vh>p._linkAsRoot</vh></v>
        <v t="ekr.20211013085956.59"><vh>p._parentVnode</vh></v>
        <v t="ekr.20211013085956.60"><vh>p._relinkAsCloneOf</vh></v>
        <v t="ekr.20211013085956.61"><vh>p._unlink</vh>
        <v t="ekr.20211013085956.62"><vh>p.badUnlink</vh></v>
        </v>
        </v>
        <v t="ekr.20211013085956.63"><vh>p.moveToX</vh>
        <v t="ekr.20211013085956.64"><vh>p.moveToBack</vh></v>
        <v t="ekr.20211013085956.65"><vh>p.moveToFirstChild</vh></v>
        <v t="ekr.20211013085956.66"><vh>p.moveToLastChild</vh></v>
        <v t="ekr.20211013085956.67"><vh>p.moveToLastNode</vh></v>
        <v t="ekr.20211013085956.68"><vh>p.moveToNext</vh></v>
        <v t="ekr.20211013085956.69"><vh>p.moveToNodeAfterTree</vh></v>
        <v t="ekr.20211013085956.70"><vh>p.moveToNthChild</vh></v>
        <v t="ekr.20211013085956.71"><vh>p.moveToParent</vh></v>
        <v t="ekr.20211013085956.72"><vh>p.moveToThreadBack</vh></v>
        <v t="ekr.20211013085956.73"><vh>p.moveToThreadNext</vh></v>
        <v t="ekr.20211013085956.74"><vh>p.moveToVisBack &amp; helper</vh>
        <v t="ekr.20211013085956.75"><vh>checkVisBackLimit</vh></v>
        </v>
        <v t="ekr.20211013085956.76"><vh>p.moveToVisNext &amp; helper</vh>
        <v t="ekr.20211013085956.77"><vh>checkVisNextLimit</vh></v>
        </v>
        <v t="ekr.20211013085956.78"><vh>p.safeMoveToThreadNext</vh>
        <v t="ekr.20211013085956.79"><vh>p.checkChild</vh></v>
        </v>
        </v>
        <v t="ekr.20211013085956.80"><vh>p.Moving, Inserting, Deleting, Cloning, Sorting</vh>
        <v t="ekr.20211013085956.81"><vh>p.clone</vh></v>
        <v t="ekr.20211013085956.82"><vh>p.copy</vh></v>
        <v t="ekr.20211013085956.83"><vh>p.copyTreeAfter, copyTreeTo</vh></v>
        <v t="ekr.20211013085956.84"><vh>p.copyWithNewVnodes</vh></v>
        <v t="ekr.20211013085956.85"><vh>p.createNodeHierarchy</vh></v>
        <v t="ekr.20211013085956.86"><vh>p.deleteAllChildren</vh></v>
        <v t="ekr.20211013085956.87"><vh>p.doDelete</vh></v>
        <v t="ekr.20211013085956.88"><vh>p.insertAfter</vh></v>
        <v t="ekr.20211013085956.89"><vh>p.insertAsLastChild</vh></v>
        <v t="ekr.20211013085956.90"><vh>p.insertAsNthChild</vh></v>
        <v t="ekr.20211013085956.91"><vh>p.insertBefore</vh></v>
        <v t="ekr.20211013085956.92"><vh>p.invalidOutline</vh></v>
        <v t="ekr.20211013085956.93"><vh>p.moveAfter</vh></v>
        <v t="ekr.20211013085956.94"><vh>p.moveToFirst/LastChildOf</vh></v>
        <v t="ekr.20211013085956.95"><vh>p.moveToNthChildOf</vh></v>
        <v t="ekr.20211013085956.96"><vh>p.moveToRoot</vh></v>
        <v t="ekr.20211013085956.97"><vh>p.promote</vh></v>
        <v t="ekr.20211013085956.98"><vh>p.validateOutlineWithParent</vh>
        <v t="ekr.20211013085956.99"><vh>&lt;&lt; validate parent ivar &gt;&gt;</vh></v>
        <v t="ekr.20211013085956.100"><vh>&lt;&lt; validate childIndex ivar &gt;&gt;</vh></v>
        <v t="ekr.20211013085956.101"><vh>&lt;&lt; validate x ivar &gt;&gt;</vh></v>
        </v>
        </v>
        <v t="ekr.20211013085956.102"><vh>p.Properties</vh>
        <v t="ekr.20211013085956.103"><vh>p.b property</vh></v>
        <v t="ekr.20211013085956.104"><vh>p.h property</vh></v>
        <v t="ekr.20211013085956.105"><vh>p.gnx property</vh></v>
        <v t="ekr.20211013085956.106"><vh>p.script property</vh></v>
        <v t="ekr.20211013085956.107"><vh>p.nosentinels property</vh></v>
        <v t="ekr.20211013085956.108"><vh>p.u Property</vh></v>
        </v>
        <v t="ekr.20211013085956.109"><vh>p.Setters</vh>
        <v t="ekr.20211013085956.110"><vh>p.VNode proxies</vh>
        <v t="ekr.20211013085956.111"><vh>p.contract/expand/isExpanded</vh></v>
        <v t="ekr.20211013085956.112"><vh>p.Status bits</vh></v>
        <v t="ekr.20211013085956.113"><vh>p.computeIcon &amp; p.setIcon</vh></v>
        <v t="ekr.20211013085956.114"><vh>p.setSelection</vh></v>
        <v t="ekr.20211013085956.115"><vh>p.restore/saveCursorAndScroll</vh></v>
        </v>
        <v t="ekr.20211013085956.116"><vh>p.setBodyString &amp; setHeadString</vh></v>
        <v t="ekr.20211013085956.117"><vh>p.Visited bits</vh>
        <v t="ekr.20211013085956.118"><vh>p.clearVisitedInTree</vh></v>
        <v t="ekr.20211013085956.119"><vh>p.clearAllVisitedInTree</vh></v>
        </v>
        <v t="ekr.20211013085956.120"><vh>p.Dirty bits</vh>
        <v t="ekr.20211013085956.121"><vh>p.clearDirty</vh></v>
        <v t="ekr.20211013085956.122"><vh>p.inAtIgnoreRange</vh></v>
        <v t="ekr.20211013085956.123"><vh>p.setAllAncestorAtFileNodesDirty</vh></v>
        <v t="ekr.20211013085956.124"><vh>p.setDirty</vh></v>
        </v>
        </v>
        <v t="ekr.20211013085956.125"><vh>p.Predicates</vh>
        <v t="ekr.20211013085956.126"><vh>p.is_at_all &amp; is_at_all_tree</vh></v>
        <v t="ekr.20211013085956.127"><vh>p.is_at_ignore &amp; in_at_ignore_tree</vh></v>
        </v>
        </v>
        </vnodes>
        <tnodes>
        <t tx="ekr.20211013085956.1">class TestPosition:

            __slots__ = [
                '_childIndex', 'stack', 'v',
                #
                # EKR: The following fields are deprecated,
                #      as are the PosList class, c.find_h and c.find_b.
                #
                'matchiter',  # for c.find_b and quicksearch.py.
                'mo',  # for c.find_h
            ]

            #@+others
            #@-others

        position = Position  # compatibility.
        </t>
        <t tx="ekr.20211013085956.10">def archivedPosition(self, root_p=None):
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
        </t>
        <t tx="ekr.20211013085956.100">if pv:
            if childIndex &lt; 0:
                p.invalidOutline(f"missing childIndex: {childIndex!r}")
            elif childIndex &gt;= pv.numberOfChildren():
                p.invalidOutline("missing children entry for index: {childIndex!r}")
        elif childIndex &lt; 0:
            p.invalidOutline("negative childIndex: {childIndex!r}")
        </t>
        <t tx="ekr.20211013085956.101">if not p.v and pv:
            self.invalidOutline("Empty t")
        </t>
        <t tx="ekr.20211013085956.102"></t>
        <t tx="ekr.20211013085956.103">def __get_b(self):
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
        </t>
        <t tx="ekr.20211013085956.104">def __get_h(self):
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
        </t>
        <t tx="ekr.20211013085956.105">def __get_gnx(self):
            p = self
            return p.v.fileIndex

        gnx = property(
            __get_gnx,  # __set_gnx,
            doc="position gnx property")
        </t>
        <t tx="ekr.20211013085956.106">def __get_script(self):
            p = self
            return g.getScript(p.v.context, p,
                useSelectedText=False,  # Always return the entire expansion.
                forcePythonSentinels=True,
                useSentinels=False)

        script = property(
            __get_script,  # __set_script,
            doc="position property returning the script formed by p and its descendants")
        </t>
        <t tx="ekr.20211013085956.107">def __get_nosentinels(self):
            p = self
            return ''.join([z for z in g.splitLines(p.b) if not g.isDirective(z)])

        nosentinels = property(
            __get_nosentinels,  # __set_nosentinels
            doc="position property returning the body text without sentinels")
        </t>
        <t tx="ekr.20211013085956.108">def __get_u(self):
            p = self
            return p.v.u

        def __set_u(self, val):
            p = self
            p.v.u = val

        u = property(
            __get_u, __set_u,
            doc="p.u property")
        </t>
        <t tx="ekr.20211013085956.109"></t>
        <t tx="ekr.20211013085956.11">def dumpLink(self, link):
            return link if link else "&lt;none&gt;"

        def dump(self, label=""):
            p = self
            if p.v:
                p.v.dump()  # Don't print a label
        </t>
        <t tx="ekr.20211013085956.110"></t>
        <t tx="ekr.20211013085956.111">def contract(self):
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
        </t>
        <t tx="ekr.20211013085956.112"># Clone bits are no longer used.
        # Dirty bits are handled carefully by the position class.

        def clearMarked(self):
            self.v.clearMarked()

        def clearOrphan(self):
            self.v.clearOrphan()

        def clearVisited(self):
            self.v.clearVisited()

        def initExpandedBit(self):
            self.v.initExpandedBit()

        def initMarkedBit(self):
            self.v.initMarkedBit()

        def initStatus(self, status):
            self.v.initStatus(status)

        def setMarked(self):
            self.v.setMarked()

        def setOrphan(self):
            self.v.setOrphan()

        def setSelected(self):
            self.v.setSelected()

        def setVisited(self):
            self.v.setVisited()
        </t>
        <t tx="ekr.20211013085956.113">def computeIcon(self):
            return self.v.computeIcon()

        def setIcon(self):
            pass  # Compatibility routine for old scripts
        </t>
        <t tx="ekr.20211013085956.114">def setSelection(self, start, length):
            self.v.setSelection(start, length)
        </t>
        <t tx="ekr.20211013085956.115">def restoreCursorAndScroll(self):
            self.v.restoreCursorAndScroll()

        def saveCursorAndScroll(self):
            self.v.saveCursorAndScroll()
        </t>
        <t tx="ekr.20211013085956.116">def setBodyString(self, s):
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
        </t>
        <t tx="ekr.20211013085956.117"></t>
        <t tx="ekr.20211013085956.118"># Compatibility routine for scripts.

        def clearVisitedInTree(self):
            for p in self.self_and_subtree(copy=False):
                p.clearVisited()
        </t>
        <t tx="ekr.20211013085956.119">def clearAllVisitedInTree(self):
            for p in self.self_and_subtree(copy=False):
                p.v.clearVisited()
                p.v.clearWriteBit()
        </t>
        <t tx="ekr.20211013085956.12">def key(self):
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

        # #1557: To keep mypy happy, don't define __hash__ at all.
        # __hash__ = None
        </t>
        <t tx="ekr.20211013085956.120"></t>
        <t tx="ekr.20211013085956.121">def clearDirty(self):
            """(p) Set p.v dirty."""
            p = self
            p.v.clearDirty()
        </t>
        <t tx="ekr.20211013085956.122">def inAtIgnoreRange(self):
            """Returns True if position p or one of p's parents is an @ignore node."""
            p = self
            for p in p.self_and_parents(copy=False):
                if p.isAtIgnoreNode():
                    return True
            return False
        </t>
        <t tx="ekr.20211013085956.123">def setAllAncestorAtFileNodesDirty(self):
            """
            Set all ancestor @&lt;file&gt; nodes dirty, including ancestors of all clones of p.
            """
            p = self
            p.v.setAllAncestorAtFileNodesDirty()
        </t>
        <t tx="ekr.20211013085956.124">def setDirty(self):
            """
            Mark a node and all ancestor @file nodes dirty.

            p.setDirty() is no longer expensive.
            """
            p = self
            p.v.setAllAncestorAtFileNodesDirty()
            p.v.setDirty()
        </t>
        <t tx="ekr.20211013085956.125"></t>
        <t tx="ekr.20211013085956.126">def is_at_all(self):
            """Return True if p.b contains an @all directive."""
            p = self
            return (
                p.isAnyAtFileNode()
                and any(g.match_word(s, 0, '@all') for s in g.splitLines(p.b)))

        def in_at_all_tree(self):
            """Return True if p or one of p's ancestors is an @all node."""
            p = self
            for p in p.self_and_parents(copy=False):
                if p.is_at_all():
                    return True
            return False
        </t>
        <t tx="ekr.20211013085956.127">def is_at_ignore(self):
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
        </t>
        <t tx="ekr.20211013085956.13">@
        - convertTreeToString and moreHead can't be VNode methods because they uses level().
        - moreBody could be anywhere: it may as well be a postion method.
        </t>
        <t tx="ekr.20211013085956.14">def convertTreeToString(self):
            """Convert a positions  suboutline to a string in MORE format."""
            p = self
            level1 = p.level()
            array = []
            for p in p.self_and_subtree(copy=False):
                array.append(p.moreHead(level1) + '\n')
                body = p.moreBody()
                if body:
                    array.append(body + '\n')
            return ''.join(array)
        </t>
        <t tx="ekr.20211013085956.15">def moreHead(self, firstLevel, useVerticalBar=False):
            """Return the headline string in MORE format."""
            # useVerticalBar is unused, but it would be useful in over-ridden methods.
            p = self
            level = self.level() - firstLevel
            plusMinus = "+" if p.hasChildren() else "-"
            pad = '\t' * level
            return f"{pad}{plusMinus} {p.h}"
        </t>
        <t tx="ekr.20211013085956.16">@language rest
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
            p = self
            array = []
            lines = p.b.split('\n')
            for s in lines:
                i = g.skip_ws(s, 0)
                if i &lt; len(s) and s[i] in ('+', '-', '\\'):
                    s = s[:i] + '\\' + s[i:]
                array.append(s)
            return '\n'.join(array)
        </t>
        <t tx="ekr.20211013085956.17"></t>
        <t tx="ekr.20211013085956.18">def children(self, copy=True):
            """Yield all child positions of p."""
            p = self
            p = p.firstChild()
            while p:
                yield p.copy() if copy else p
                p.moveToNext()

        # Compatibility with old code...

        children_iter = children
        </t>
        <t tx="ekr.20211013085956.19">def following_siblings(self, copy=True):
            """Yield all siblings positions that follow p, not including p."""
            p = self
            p = p.next()  # pylint: disable=not-callable
            while p:
                yield p.copy() if copy else p
                p.moveToNext()

        # Compatibility with old code...

        following_siblings_iter = following_siblings
        </t>
        <t tx="ekr.20211013085956.20">def nearest_roots(self, copy=True, predicate=None):
            """
            A generator yielding all the root positions "near" p1 = self that
            satisfy the given predicate. p.isAnyAtFileNode is the default
            predicate.

            The search first proceeds up the p's tree. If a root is found, this
            generator yields just that root.

            Otherwise, the generator yields all nodes in p.subtree() that satisfy
            the predicate. Once a root is found, the generator skips its subtree.
            """
            def default_predicate(p):
                return p.isAnyAtFileNode()

            the_predicate = predicate or default_predicate

            # First, look up the tree.
            p1 = self
            for p in p1.self_and_parents(copy=False):
                if the_predicate(p):
                    yield p.copy() if copy else p
                    return
            # Next, look for all .md files in the tree.
            after = p1.nodeAfterTree()
            p = p1
            while p and p != after:
                if the_predicate(p):
                    yield p.copy() if copy else p
                    p.moveToNodeAfterTree()
                else:
                    p.moveToThreadNext()
        </t>
        <t tx="ekr.20211013085956.21">def nearest_unique_roots(self, copy=True, predicate=None):
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

            def default_predicate(p):
                return p.isAnyAtFileNode()

            the_predicate = predicate or default_predicate

            # First, look up the tree.
            p1 = self
            for p in p1.self_and_parents(copy=False):
                if the_predicate(p):
                    yield p.copy() if copy else p
                    return
            # Next, look for all unique .md files in the tree.
            seen = set()
            after = p1.nodeAfterTree()
            p = p1
            while p and p != after:
                if the_predicate(p):
                    if p.v not in seen:
                        seen.add(p.v)
                        yield p.copy() if copy else p
                    p.moveToNodeAfterTree()
                else:
                    p.moveToThreadNext()

        nearest = nearest_unique_roots
        </t>
        <t tx="ekr.20211013085956.22">def nodes(self):
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
        </t>
        <t tx="ekr.20211013085956.23">def parents(self, copy=True):
            """Yield all parent positions of p."""
            p = self
            p = p.parent()
            while p:
                yield p.copy() if copy else p
                p.moveToParent()

        # Compatibility with old code...

        parents_iter = parents
        </t>
        <t tx="ekr.20211013085956.24">def self_and_parents(self, copy=True):
            """Yield p and all parent positions of p."""
            p = self
            p = p.copy()
            while p:
                yield p.copy() if copy else p
                p.moveToParent()

        # Compatibility with old code...

        self_and_parents_iter = self_and_parents
        </t>
        <t tx="ekr.20211013085956.25">def self_and_siblings(self, copy=True):
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
        </t>
        <t tx="ekr.20211013085956.26">def self_and_subtree(self, copy=True):
            """Yield p and all positions in p's subtree."""
            p = self
            p = p.copy()
            after = p.nodeAfterTree()
            while p and p != after:
                yield p.copy() if copy else p
                p.moveToThreadNext()

        # Compatibility with old code...

        self_and_subtree_iter = self_and_subtree
        </t>
        <t tx="ekr.20211013085956.27">def subtree(self, copy=True):
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
        </t>
        <t tx="ekr.20211013085956.28">def unique_nodes(self):
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
        </t>
        <t tx="ekr.20211013085956.29">def unique_subtree(self):
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
        </t>
        <t tx="ekr.20211013085956.3"></t>
        <t tx="ekr.20211013085956.30"></t>
        <t tx="ekr.20211013085956.31"></t>
        <t tx="ekr.20211013085956.32">def anyAtFileNodeName(self):
            return self.v.anyAtFileNodeName()

        def atAutoNodeName(self):
            return self.v.atAutoNodeName()

        def atCleanNodeName(self):
            return self.v.atCleanNodeName()

        def atEditNodeName(self):
            return self.v.atEditNodeName()

        def atFileNodeName(self):
            return self.v.atFileNodeName()

        def atNoSentinelsFileNodeName(self):
            return self.v.atNoSentinelsFileNodeName()

        def atShadowFileNodeName(self):
            return self.v.atShadowFileNodeName()

        def atSilentFileNodeName(self):
            return self.v.atSilentFileNodeName()

        def atThinFileNodeName(self):
            return self.v.atThinFileNodeName()

        # New names, less confusing
        atNoSentFileNodeName = atNoSentinelsFileNodeName
        atAsisFileNodeName = atSilentFileNodeName

        def isAnyAtFileNode(self):
            return self.v.isAnyAtFileNode()

        def isAtAllNode(self):
            return self.v.isAtAllNode()

        def isAtAutoNode(self):
            return self.v.isAtAutoNode()

        def isAtAutoRstNode(self):
            return self.v.isAtAutoRstNode()

        def isAtCleanNode(self):
            return self.v.isAtCleanNode()

        def isAtEditNode(self):
            return self.v.isAtEditNode()

        def isAtFileNode(self):
            return self.v.isAtFileNode()

        def isAtIgnoreNode(self):
            return self.v.isAtIgnoreNode()

        def isAtNoSentinelsFileNode(self):
            return self.v.isAtNoSentinelsFileNode()

        def isAtOthersNode(self):
            return self.v.isAtOthersNode()

        def isAtRstFileNode(self):
            return self.v.isAtRstFileNode()

        def isAtSilentFileNode(self):
            return self.v.isAtSilentFileNode()

        def isAtShadowFileNode(self):
            return self.v.isAtShadowFileNode()

        def isAtThinFileNode(self):
            return self.v.isAtThinFileNode()

        # New names, less confusing:
        isAtNoSentFileNode = isAtNoSentinelsFileNode
        isAtAsisFileNode = isAtSilentFileNode

        # Utilities.

        def matchHeadline(self, pattern):
            return self.v.matchHeadline(pattern)
        </t>
        <t tx="ekr.20211013085956.33">def bodyString(self):
            return self.v.bodyString()

        def headString(self):
            return self.v.headString()
        </t>
        <t tx="ekr.20211013085956.34">def isDirty(self):
            return self.v.isDirty()

        def isMarked(self):
            return self.v.isMarked()

        def isOrphan(self):
            return self.v.isOrphan()

        def isSelected(self):
            return self.v.isSelected()

        def isTopBitSet(self):
            return self.v.isTopBitSet()

        def isVisited(self):
            return self.v.isVisited()

        def status(self):
            return self.v.status()
        </t>
        <t tx="ekr.20211013085956.35"></t>
        <t tx="ekr.20211013085956.36"># This used to be time-critical code.

        def childIndex(self):
            p = self
            return p._childIndex
        </t>
        <t tx="ekr.20211013085956.37">def directParents(self):
            return self.v.directParents()
        </t>
        <t tx="ekr.20211013085956.38">def hasChildren(self):
            p = self
            return len(p.v.children) &gt; 0

        hasFirstChild = hasChildren

        def numberOfChildren(self):
            p = self
            return len(p.v.children)
        </t>
        <t tx="ekr.20211013085956.39"># These methods are useful abbreviations.
        # Warning: they make copies of positions, so they should be used _sparingly_

        def getBack(self):
            return self.copy().moveToBack()

        def getFirstChild(self):
            return self.copy().moveToFirstChild()

        def getLastChild(self):
            return self.copy().moveToLastChild()

        def getLastNode(self):
            return self.copy().moveToLastNode()
        # def getLastVisible   (self): return self.copy().moveToLastVisible()

        def getNext(self):
            return self.copy().moveToNext()

        def getNodeAfterTree(self):
            return self.copy().moveToNodeAfterTree()

        def getNthChild(self, n):
            return self.copy().moveToNthChild(n)

        def getParent(self):
            return self.copy().moveToParent()

        def getThreadBack(self):
            return self.copy().moveToThreadBack()

        def getThreadNext(self):
            return self.copy().moveToThreadNext()
        # New in Leo 4.4.3 b2: add c args.

        def getVisBack(self, c):
            return self.copy().moveToVisBack(c)

        def getVisNext(self, c):
            return self.copy().moveToVisNext(c)
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
        </t>
        <t tx="ekr.20211013085956.4">def __eq__(self, p2):  # Use Any, not Position.
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

        def __ne__(self, p2):  # Use Any, not Position.
            """Return True if two postions are not equivalent."""
            return not self.__eq__(p2)
        </t>
        <t tx="ekr.20211013085956.40">def get_UNL(self, with_file=True, with_proto=False, with_index=True, with_count=False):
            """
            Return a UNL representing a clickable link.

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
                    aList.append(i.h.replace('--&gt;', '--%3E') + ":" + str(ind))
                        # g.recursiveUNLFind and sf.copy_to_my_settings undo this replacement.
                    if count or with_count:
                        aList[-1] = aList[-1] + "," + str(count)
                else:
                    aList.append(i.h.replace('--&gt;', '--%3E'))
                        # g.recursiveUNLFind  and sf.copy_to_my_settings undo this replacement.
            UNL = '--&gt;'.join(reversed(aList))
            if with_proto:
                # return ("file://%s#%s" % (self.v.context.fileName(), UNL)).replace(' ', '%20')
                s = "unl:" + f"//{self.v.context.fileName()}#{UNL}"
                return s.replace(' ', '%20')
            if with_file:
                return f"{self.v.context.fileName()}#{UNL}"
            return UNL
        </t>
        <t tx="ekr.20211013085956.41">def hasBack(self):
            p = self
            return bool(p.v and p._childIndex &gt; 0)

        def hasNext(self):
            p = self
            try:
                parent_v = p._parentVnode()
                    # Returns None if p.v is None.
                return p.v and parent_v and p._childIndex + 1 &lt; len(parent_v.children)  # type:ignore
            except Exception:
                g.trace('*** Unexpected exception')
                g.es_exception()
                return None

        def hasParent(self):
            p = self
            return bool(p.v and p.stack)

        def hasThreadBack(self):
            p = self
            return bool(p.hasParent() or p.hasBack())
                # Much cheaper than computing the actual value.
        </t>
        <t tx="ekr.20211013085956.42">def hasThreadNext(self):
            p = self
            if not p.v:
                return False
            if p.hasChildren() or p.hasNext():
                return True
            n = len(p.stack) - 1
            while n &gt;= 0:
                v, childIndex = p.stack[n]
                # See how many children v's parent has.
                if n == 0:
                    parent_v = v.context.hiddenRootNode
                else:
                    parent_v, junk = p.stack[n - 1]
                if len(parent_v.children) &gt; childIndex + 1:
                    # v has a next sibling.
                    return True
                n -= 1
            return False
        </t>
        <t tx="ekr.20211013085956.43">def findRootPosition(self):
            # 2011/02/25: always use c.rootPosition
            p = self
            c = p.v.context
            return c.rootPosition()
        </t>
        <t tx="ekr.20211013085956.44">def isAncestorOf(self, p2):
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
        </t>
        <t tx="ekr.20211013085956.45">def isCloned(self):
            p = self
            return p.v.isCloned()
        </t>
        <t tx="ekr.20211013085956.46">def isRoot(self):
            p = self
            return not p.hasParent() and not p.hasBack()
        </t>
        <t tx="ekr.20211013085956.47">def isVisible(self, c):
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

            if c.hoistStack:  # Chapters are a form of hoist.
                root = c.hoistStack[-1].p
                if p == root:
                    # #12.
                    return True
                return root.isAncestorOf(p) and visible(p, root=root)
            for root in c.rootPosition().self_and_siblings(copy=False):
                if root == p or root.isAncestorOf(p):
                    return visible(p)
            return False
        </t>
        <t tx="ekr.20211013085956.48">def level(self):
            """Return the number of p's parents."""
            p = self
            return len(p.stack) if p.v else 0

        simpleLevel = level
        </t>
        <t tx="ekr.20211013085956.49">def positionAfterDeletedTree(self):
            """Return the position corresponding to p.nodeAfterTree() after this node is
            deleted. This will be p.nodeAfterTree() unless p.next() exists.

            This method allows scripts to traverse an outline, deleting nodes during the
            traversal. The pattern is::

                p = c.rootPosition()
                while p:
                if &lt;delete p?&gt;:
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
            next = p.next()  # pylint: disable=not-callable
            if next:
                # The new position will be the same as p, except for p.v.
                p = p.copy()
                p.v = next.v
                return p
            return p.nodeAfterTree()
        </t>
        <t tx="ekr.20211013085956.5">def __init__(self, v, childIndex=0, stack=None):
            """Create a new position with the given childIndex and parent stack."""
            self._childIndex = childIndex
            self.v = v
            # Stack entries are tuples (v, childIndex).
            if stack:
                self.stack = stack[:]  # Creating a copy here is safest and best.
            else:
                self.stack = []
            g.app.positions += 1
        </t>
        <t tx="ekr.20211013085956.50">def textOffset(self):
            """
            Return the fcol offset of self.
            Return None if p is has no ancestor @&lt;file&gt; node.
            http://tinyurl.com/5nescw
            """
            p = self
            found, offset = False, 0
            for p in p.self_and_parents(copy=False):
                if p.isAnyAtFileNode():
                    # Ignore parent of @&lt;file&gt; node.
                    found = True
                    break
                parent = p.parent()
                if not parent:
                    break
                # If p is a section definition, search the parent for the reference.
                # Otherwise, search the parent for @others.
                h = p.h.strip()
                i = h.find('&lt;&lt;')
                j = h.find('&gt;&gt;')
                target = h[i : j + 2] if -1 &lt; i &lt; j else '@others'
                for s in parent.b.split('\n'):
                    if s.find(target) &gt; -1:
                        offset += g.skip_ws(s, 0)
                        break
            return offset if found else None
        </t>
        <t tx="ekr.20211013085956.51">def isOutsideAnyAtFileTree(self):
            """Select the first clone of target that is outside any @file node."""
            p = self
            for parent in p.self_and_parents(copy=False):
                if parent.isAnyAtFileNode():
                    return False
            return True
        </t>
        <t tx="ekr.20211013085956.52"># These methods are only for the use of low-level code
        # in leoNodes.py, leoFileCommands.py and leoUndo.py.
        </t>
        <t tx="ekr.20211013085956.53">def _adjustPositionBeforeUnlink(self, p2):
            """Adjust position p before unlinking p2."""
            # p will change if p2 is a previous sibling of p or
            # p2 is a previous sibling of any ancestor of p.
            p = self
            sib = p.copy()
            # A special case for previous siblings.
            # Adjust p._childIndex, not the stack's childIndex.
            while sib.hasBack():
                sib.moveToBack()
                if sib == p2:
                    p._childIndex -= 1
                    return
            # Adjust p's stack.
            stack: List[Tuple[VNode, int]] = []
            changed, i = False, 0
            while i &lt; len(p.stack):
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
        </t>
        <t tx="ekr.20211013085956.54">def _linkAfter(self, p_after):
            """Link self after p_after."""
            p = self
            parent_v = p_after._parentVnode()
            p.stack = p_after.stack[:]
            p._childIndex = p_after._childIndex + 1
            child = p.v
            n = p_after._childIndex + 1
            child._addLink(n, parent_v)
        </t>
        <t tx="ekr.20211013085956.55">def _linkCopiedAfter(self, p_after):
            """Link self, a newly copied tree, after p_after."""
            p = self
            parent_v = p_after._parentVnode()
            p.stack = p_after.stack[:]
            p._childIndex = p_after._childIndex + 1
            child = p.v
            n = p_after._childIndex + 1
            child._addCopiedLink(n, parent_v)
        </t>
        <t tx="ekr.20211013085956.56">def _linkAsNthChild(self, parent, n):
            """Link self as the n'th child of the parent."""
            p = self
            parent_v = parent.v
            p.stack = parent.stack[:]
            p.stack.append((parent_v, parent._childIndex),)
            p._childIndex = n
            child = p.v
            child._addLink(n, parent_v)
        </t>
        <t tx="ekr.20211013085956.57">def _linkCopiedAsNthChild(self, parent, n):
            """Link a copied self as the n'th child of the parent."""
            p = self
            parent_v = parent.v
            p.stack = parent.stack[:]
            p.stack.append((parent_v, parent._childIndex),)
            p._childIndex = n
            child = p.v
            child._addCopiedLink(n, parent_v)
        </t>
        <t tx="ekr.20211013085956.58">def _linkAsRoot(self):
            """Link self as the root node."""
            p = self
            assert p.v
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
        </t>
        <t tx="ekr.20211013085956.59">def _parentVnode(self):
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
        </t>
        <t tx="ekr.20211013085956.6">def __ge__(self, other):
            return self.__eq__(other) or self.__gt__(other)

        def __le__(self, other):
            return self.__eq__(other) or self.__lt__(other)

        def __lt__(self, other):
            return not self.__eq__(other) and not self.__gt__(other)
        </t>
        <t tx="ekr.20211013085956.60">def _relinkAsCloneOf(self, p2):
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
        </t>
        <t tx="ekr.20211013085956.61">def _unlink(self):
            """Unlink the receiver p from the tree."""
            p = self
            n = p._childIndex
            parent_v = p._parentVnode()
                # returns None if p.v is None
            child = p.v
            assert p.v
            assert parent_v
            # Delete the child.
            if (0 &lt;= n &lt; len(parent_v.children) and
                parent_v.children[n] == child
            ):
                # This is the only call to v._cutlink.
                child._cutLink(n, parent_v)
            else:
                self.badUnlink(parent_v, n, child)
        </t>
        <t tx="ekr.20211013085956.62">def badUnlink(self, parent_v, n, child):

            if 0 &lt;= n &lt; len(parent_v.children):
                g.trace(f"**can not happen: children[{n}] != p.v")
                g.trace('parent_v.children...\n',
                    g.listToString(parent_v.children))
                g.trace('parent_v', parent_v)
                g.trace('parent_v.children[n]', parent_v.children[n])
                g.trace('child', child)
                g.trace('** callers:', g.callers())
                if g.unitTesting:
                    assert False, 'children[%s] != p.v'
            else:
                g.trace(
                    f"**can not happen: bad child index: {n}, "
                    f"len(children): {len(parent_v.children)}")
                g.trace('parent_v.children...\n',
                    g.listToString(parent_v.children))
                g.trace('parent_v', parent_v, 'child', child)
                g.trace('** callers:', g.callers())
                if g.unitTesting:
                    assert False, f"bad child index: {n}"
        </t>
        <t tx="ekr.20211013085956.63">@ These routines change self to a new position "in place".
        That is, these methods must _never_ call p.copy().

        When moving to a nonexistent position, these routines simply set p.v = None,
        leaving the p.stack unchanged. This allows the caller to "undo" the effect of
        the invalid move by simply restoring the previous value of p.v.

        These routines all return self on exit so the following kind of code will work:
            after = p.copy().moveToNodeAfterTree()
        </t>
        <t tx="ekr.20211013085956.64">def moveToBack(self):
            """Move self to its previous sibling."""
            p = self
            n = p._childIndex
            parent_v = p._parentVnode()
                # Returns None if p.v is None.
            # Do not assume n is in range: this is used by positionExists.
            if parent_v and p.v and 0 &lt; n &lt;= len(parent_v.children):
                p._childIndex -= 1
                p.v = parent_v.children[n - 1]
            else:
                p.v = None
            return p
        </t>
        <t tx="ekr.20211013085956.65">def moveToFirstChild(self):
            """Move a position to it's first child's position."""
            p = self
            if p.v and p.v.children:
                p.stack.append((p.v, p._childIndex),)
                p.v = p.v.children[0]
                p._childIndex = 0
            else:
                p.v = None
            return p
        </t>
        <t tx="ekr.20211013085956.66">def moveToLastChild(self):
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
        </t>
        <t tx="ekr.20211013085956.67">def moveToLastNode(self):
            """Move a position to last node of its tree.

            N.B. Returns p if p has no children."""
            p = self
            # Huge improvement for 4.2.
            while p.hasChildren():
                p.moveToLastChild()
            return p
        </t>
        <t tx="ekr.20211013085956.68">def moveToNext(self):
            """Move a position to its next sibling."""
            p = self
            n = p._childIndex
            parent_v = p._parentVnode()
                # Returns None if p.v is None.
            if p and not p.v:
                g.trace('no p.v:', p, g.callers())
            if p.v and parent_v and len(parent_v.children) &gt; n + 1:
                p._childIndex = n + 1
                p.v = parent_v.children[n + 1]
            else:
                p.v = None
            return p
        </t>
        <t tx="ekr.20211013085956.69">def moveToNodeAfterTree(self):
            """Move a position to the node after the position's tree."""
            p = self
            while p:
                if p.hasNext():
                    p.moveToNext()
                    break
                p.moveToParent()
            return p
        </t>
        <t tx="ekr.20211013085956.7">def __gt__(self, other):
            """Return True if self appears after other in outline order."""
            stack1, stack2 = self.stack, other.stack
            n1, n2 = len(stack1), len(stack2)
            n = min(n1, n2)
            # Compare the common part of the stacks.
            for item1, item2 in zip(stack1, stack2):
                v1, x1 = item1
                v2, x2 = item2
                if x1 &gt; x2:
                    return True
                if x1 &lt; x2:
                    return False
            # Finish the comparison.
            if n1 == n2:
                x1, x2 = self._childIndex, other._childIndex
                return x1 &gt; x2
            if n1 &lt; n2:
                x1 = self._childIndex
                v2, x2 = other.stack[n]
                return x1 &gt; x2
            # n1 &gt; n2
            # 2011/07/28: Bug fix suggested by SegundoBob.
            x1 = other._childIndex
            v2, x2 = self.stack[n]
            return x2 &gt;= x1
        </t>
        <t tx="ekr.20211013085956.70">def moveToNthChild(self, n):
            p = self
            if p.v and len(p.v.children) &gt; n:
                p.stack.append((p.v, p._childIndex),)
                p.v = p.v.children[n]
                p._childIndex = n
            else:
                # mypy rightly doesn't like setting p.v to None.
                # Leo's code must use the test `if p:` as appropriate.
                p.v = None  # type:ignore
            return p
        </t>
        <t tx="ekr.20211013085956.71">def moveToParent(self):
            """Move a position to its parent position."""
            p = self
            if p.v and p.stack:
                p.v, p._childIndex = p.stack.pop()
            else:
                # mypy rightly doesn't like setting p.v to None.
                # Leo's code must use the test `if p:` as appropriate.
                p.v = None  # type:ignore
            return p
        </t>
        <t tx="ekr.20211013085956.72">def moveToThreadBack(self):
            """Move a position to it's threadBack position."""
            p = self
            if p.hasBack():
                p.moveToBack()
                p.moveToLastNode()
            else:
                p.moveToParent()
            return p
        </t>
        <t tx="ekr.20211013085956.73">def moveToThreadNext(self):
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
        </t>
        <t tx="ekr.20211013085956.74">def moveToVisBack(self, c):
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
        </t>
        <t tx="ekr.20211013085956.75">def checkVisBackLimit(self, limit, limitIsVisible, p):
            """Return done, p or None"""
            c = p.v.context
            if limit == p:
                if limitIsVisible and p.isVisible(c):
                    return True, p
                return True, None
            if limit.isAncestorOf(p):
                return False, None
            return True, None
        </t>
        <t tx="ekr.20211013085956.76">def moveToVisNext(self, c):
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
        </t>
        <t tx="ekr.20211013085956.77">def checkVisNextLimit(self, limit, p):
            """Return True is p is outside limit of visible nodes."""
            return limit != p and not limit.isAncestorOf(p)
        </t>
        <t tx="ekr.20211013085956.78">def safeMoveToThreadNext(self):
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
        </t>
        <t tx="ekr.20211013085956.79"></t>
        <t tx="ekr.20211013085956.8">def __bool__(self):
            """
            Return True if a position is valid.

            The tests 'if p' or 'if not p' are the _only_ correct ways to test
            whether a position p is valid.

            Tests like 'if p is None' or 'if p is not None' will not work properly.
            """
            return self.v is not None
        </t>
        <t tx="ekr.20211013085956.80"></t>
        <t tx="ekr.20211013085956.81">def clone(self):
            """Create a clone of back.

            Returns the newly created position."""
            p = self
            p2 = p.copy()  # Do *not* copy the VNode!
            p2._linkAfter(p)  # This should "just work"
            return p2
        </t>
        <t tx="ekr.20211013085956.82">def copy(self):
            """"Return an independent copy of a position."""
            return Position(self.v, self._childIndex, self.stack)
        </t>
        <t tx="ekr.20211013085956.83"># These used by unit tests, by the group_operations plugin,
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
            p2.v.u = copy.deepcopy(p.v.u)
            if copyGnxs:
                p2.v.fileIndex = p.v.fileIndex
            # 2009/10/02: no need to copy arg to iter
            for child in p.children():
                child2 = p2.insertAsLastChild()
                child.copyTreeFromSelfTo(child2, copyGnxs=copyGnxs)
        </t>
        <t tx="ekr.20211013085956.84">def copyWithNewVnodes(self, copyMarked=False):
            """
            Return an **unlinked** copy of p with a new vnode v.
            The new vnode is complete copy of v and all its descendants.
            """
            p = self
            return Position(v=p.v.copyTree(copyMarked))
        </t>
        <t tx="ekr.20211013085956.85">def createNodeHierarchy(self, heads, forcecreate=False):
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
        </t>
        <t tx="ekr.20211013085956.86">def deleteAllChildren(self):
            """
            Delete all children of the receiver and set p.dirty().
            """
            p = self
            p.setDirty()  # Mark @file nodes dirty!
            while p.hasChildren():
                p.firstChild().doDelete()
        </t>
        <t tx="ekr.20211013085956.87">def doDelete(self, newNode=None):
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
        </t>
        <t tx="ekr.20211013085956.88">def insertAfter(self):
            """
            Inserts a new position after self.

            Returns the newly created position.
            """
            p = self
            context = p.v.context
            p2 = self.copy()
            p2.v = VNode(context=context)
            p2.v.iconVal = 0
            p2._linkAfter(p)
            return p2
        </t>
        <t tx="ekr.20211013085956.89">def insertAsLastChild(self):
            """
            Insert a new VNode as the last child of self.

            Return the newly created position.
            """
            p = self
            n = p.numberOfChildren()
            return p.insertAsNthChild(n)
        </t>
        <t tx="ekr.20211013085956.9">def __str__(self):
            p = self
            if p.v:
                return (
                    "&lt;"
                    f"pos {id(p)} "
                    f"childIndex: {p._childIndex} "
                    f"lvl: {p.level()} "
                    f"key: {p.key()} "
                    f"{p.h}"
                    "&gt;"
                )
            return f"&lt;pos {id(p)} [{len(p.stack)}] None&gt;"

        __repr__ = __str__
        </t>
        <t tx="ekr.20211013085956.90">def insertAsNthChild(self, n):
            """
            Inserts a new node as the the nth child of self.
            self must have at least n-1 children.

            Returns the newly created position.
            """
            p = self
            context = p.v.context
            p2 = self.copy()
            p2.v = VNode(context=context)
            p2.v.iconVal = 0
            p2._linkAsNthChild(p, n)
            return p2
        </t>
        <t tx="ekr.20211013085956.91">def insertBefore(self):
            """
            Insert a new position before self.

            Return the newly created position.
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
        </t>
        <t tx="ekr.20211013085956.92">def invalidOutline(self, message):
            p = self
            if p.hasParent():
                node = p.parent()
            else:
                node = p
            p.v.context.alert(f"invalid outline: {message}\n{node}")
        </t>
        <t tx="ekr.20211013085956.93">def moveAfter(self, a):
            """Move a position after position a."""
            p = self  # Do NOT copy the position!
            a._adjustPositionBeforeUnlink(p)
            p._unlink()
            p._linkAfter(a)
            return p
        </t>
        <t tx="ekr.20211013085956.94">def moveToFirstChildOf(self, parent):
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
        </t>
        <t tx="ekr.20211013085956.95">def moveToNthChildOf(self, parent, n):
            """Move a position to the nth child of parent."""
            p = self  # Do NOT copy the position!
            parent._adjustPositionBeforeUnlink(p)
            p._unlink()
            p._linkAsNthChild(parent, n)
            return p
        </t>
        <t tx="ekr.20211013085956.96">def moveToRoot(self):
            """Move self to the root position."""
            p = self  # Do NOT copy the position!
            #
            # #1631. The old root can not possibly be affected by unlinking p.
            p._unlink()
            p._linkAsRoot()
            return p
        </t>
        <t tx="ekr.20211013085956.97">def promote(self):
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
        </t>
        <t tx="ekr.20211013085956.98"># This routine checks the structure of the receiver's tree.

        def validateOutlineWithParent(self, pv):
            p = self
            result = True  # optimists get only unpleasant surprises.
            parent = p.getParent()
            childIndex = p._childIndex
            &lt;&lt; validate parent ivar &gt;&gt;
            &lt;&lt; validate childIndex ivar &gt;&gt;
            &lt;&lt; validate x ivar &gt;&gt;
            # Recursively validate all the children.
            for child in p.children():
                r = child.validateOutlineWithParent(p)
                if not r:
                    result = False
            return result
        </t>
        <t tx="ekr.20211013085956.99">if parent != pv:
            p.invalidOutline("Invalid parent link: " + repr(parent))
        </t>
        </tnodes>
        </leo_file>'''
        #@-<< define s >>
        pasted = c.fileCommands.getLeoOutlineFromClipboard(s)
        self.assertTrue(pasted)
        pasted.moveAfter(root)
        # Validate.
        c.validateOutline()
        c.checkOutline()
        self.p = pasted
        c.selectPosition(self.p)
    #@+node:ekr.20211013081200.2: *3* test_py2ts.test_setup
    def test_setup(self):
        assert self.x
        assert self.p
        # self.dump_tree(self.p)
    #@+node:ekr.20211013085659.1: *3* test_py2ts.test_convert_position_class
    def test_convert_position_class(self):
        # Convert a copy of the Position class
        self.x.convert(self.p)
        # self.dump_tree(self.c.lastTopLevel())
    #@-others
#@-others


#@-leo

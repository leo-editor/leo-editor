# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20201203042030.1: * @file ../unittests/core/test_leoNodes.py
#@@first
"""Tests for leo.core.leoNodes"""

# pylint: disable=no-member
from leo.core import leoGlobals as g
from leo.core.leoTest2 import LeoUnitTest

#@+others
#@+node:ekr.20210828112210.1: ** class TestNodes(LeoUnitTest)
class TestNodes(LeoUnitTest):
    """Unit tests for leo/core/leoNodes.py."""

    test_outline = None  # Set by create_test_outline.

    #@+others
    #@+node:ekr.20201203042409.3: *3* TestNodes.setUp
    def setUp(self):
        """Create the nodes in the commander."""
        super().setUp()
        c = self.c
        self.create_test_outline()
        c.selectPosition(c.rootPosition())
    #@+node:ekr.20210902022909.1: *3* TestNodes.tests...
    #@+node:ekr.20210830095545.3: *4* TestNodes.test_all_generators_return_unique_positions
    def test_all_generators_return_unique_positions(self):
        # This tests a major bug in *all* generators returning positions.
        c, p = self.c, self.c.p
        root = p.next()
        table = (
            ('all_positions', c.all_positions),
            ('all_unique_positions', c.all_unique_positions),
            ('children', root.children),
            ('self_and_siblings', root.self_and_siblings),
            ('self_and_parents', root.firstChild().self_and_parents),
            ('self_and_subtree', root.self_and_subtree),
            ('following_siblings', root.following_siblings),
            ('parents', root.firstChild().firstChild().parents),
            ('unique_subtree', root.unique_subtree),
        )
        for kind, generator in table:
            aList = []
            for p in generator():
                self.assertFalse(p in aList, msg=f"{kind} {p.gnx} {p.h}")
                aList.append(p)
    #@+node:ekr.20210828075915.1: *4* TestNodes.test_all_nodes_coverage
    def test_all_nodes_coverage(self):
        # @test c iters: <coverage tests>
        c = self.c
        v1 = [p.v for p in c.all_positions()]
        v2 = [v for v in c.all_nodes()]
        for v in v2:
            self.assertTrue(v in v1)
        for v in v1:
            self.assertTrue(v in v2)
    #@+node:ekr.20210830095545.41: *4* TestNodes.test_at_most_one_VNode_has_str_leo_pos_attribute
    def test_at_most_one_VNode_has_str_leo_pos_attribute(self):
        c = self.c
        n = 0
        for v in c.all_unique_vnodes_iter():
            if hasattr(v, 'unknownAttributes'):
                d = v.unknownAttributes
                if d.get('str_leo_pos'):
                    n += 1
        self.assertTrue(n == 0)
    #@+node:ekr.20210830095545.58: *4* TestNodes.test_at_others_directive
    def test_at_others_directive(self):
        p = self.c.p
        p1 = p.insertAsLastChild()
        p1.setHeadString('@file zzz')
        body = '''     %s
        ''' % (chr(64) + 'others')  # ugly hack
        p1.setBodyString(body)
        p2 = p1.insertAsLastChild()
        self.assertEqual(p1.textOffset(), 0)
        self.assertEqual(p2.textOffset(), 5)
    #@+node:ekr.20210830095545.6: *4* TestNodes.test_c_positionExists
    def test_c_positionExists(self):
        c, p = self.c, self.c.p
        child = p.insertAsLastChild()
        self.assertTrue(c.positionExists(child))
        child.doDelete()
        self.assertFalse(c.positionExists(child))
        # also check the same on root level
        child = c.rootPosition().insertAfter()
        self.assertTrue(c.positionExists(child))
        child.doDelete()
        self.assertFalse(c.positionExists(child))
    #@+node:ekr.20210830095545.7: *4* TestNodes.test_c_positionExists_for_all_nodes
    def test_c_positionExists_for_all_nodes(self):
        c, p = self.c, self.c.p
        for p in c.all_positions():
            self.assertTrue(c.positionExists(p))
                # 2012/03/08: If a root is given, the search is confined to that root only.
    #@+node:ekr.20210830095545.8: *4* TestNodes.test_c_safe_all_positions
    def test_c_safe_all_positions(self):
        c = self.c
        aList1 = list(c.all_positions())
        aList2 = list(c.safe_all_positions())
        self.assertEqual(len(aList1), len(aList2))
    #@+node:ekr.20210830095545.9: *4* TestNodes.test_check_all_gnx_s_exist_and_are_unique
    def test_check_all_gnx_s_exist_and_are_unique(self):
        c, p = self.c, self.c.p
        d = {}  # Keys are gnx's, values are lists of vnodes with that gnx.
        for p in c.all_positions():
            gnx = p.v.fileIndex
            self.assertTrue(gnx)
            aSet = d.get(gnx, set())
            aSet.add(p.v)
            d[gnx] = aSet
        for gnx in sorted(d.keys()):
            aList = sorted(d.get(gnx))
            self.assertTrue(len(aList) == 1)
    #@+node:ekr.20210830095545.42: *4* TestNodes.test_clone_and_move_the_clone_to_the_root
    def test_clone_and_move_the_clone_to_the_root(self):
        c, p = self.c, self.c.p
        child = p.insertAsNthChild(0)
        c.setHeadString(child, 'child')  # Force the headline to update.
        self.assertTrue(child)
        c.selectPosition(child)
        clone = c.clone()
        self.assertEqual(clone, c.p)
        self.assertEqual(clone.h, 'child')
        assert child.isCloned(), 'fail 1'
        assert clone.isCloned(), 'fail 2'
        assert child.isCloned(), 'fail 3'
        assert clone.isCloned(), 'fail 4'
        c.undoer.undo()
        assert not child.isCloned(), 'fail 1-a'
        c.undoer.redo()
        assert child.isCloned(), 'fail 1-b'
        c.undoer.undo()
        assert not child.isCloned(), 'fail 1-c'
        c.undoer.redo()
        assert child.isCloned(), 'fail 1-d'
        clone.moveToRoot()  # Does not change child position.
        assert child.isCloned(), 'fail 3-2'
        assert clone.isCloned(), 'fail 4-2'
        assert not clone.parent(), 'fail 5'
        assert not clone.back(), 'fail 6'
        clone.doDelete()
        assert not child.isCloned(), 'fail 7'
    #@+node:ekr.20210830095545.2: *4* TestNodes.test_consistency_between_parents_iter_and_v_parents
    def test_consistency_between_parents_iter_and_v_parents(self):
        c, p = self.c, self.c.p
        for p in c.all_positions():
            parents1 = p.v.parents
            parents2 = p.v.directParents()
            self.assertEqual(len(parents1), len(parents2), msg=p.h)
            for parent in parents1:
                self.assertTrue(parent in parents2)
            for parent in parents2:
                self.assertTrue(parent in parents1)
    #@+node:ekr.20210830095545.10: *4* TestNodes.test_consistency_of_back_next_links
    def test_consistency_of_back_next_links(self):
        c, p = self.c, self.c.p
        for p in c.all_positions():
            back = p.back()
            next = p.next()
            if back:
                self.assertEqual(back.getNext(), p)
            if next:
                self.assertEqual(next.getBack(), p)
    #@+node:ekr.20210830095545.11: *4* TestNodes.test_consistency_of_c_all_positions__and_p_ThreadNext_
    def test_consistency_of_c_all_positions__and_p_ThreadNext_(self):
        c, p = self.c, self.c.p
        p2 = c.rootPosition()
        for p in c.all_positions():
            self.assertEqual(p, p2)
            p2.moveToThreadNext()
        self.assertFalse(p2)
    #@+node:ekr.20210830095545.12: *4* TestNodes.test_consistency_of_firstChild__children_iter_
    def test_consistency_of_firstChild__children_iter_(self):
        c, p = self.c, self.c.p
        for p in c.all_positions():
            p2 = p.firstChild()
            for p3 in p.children_iter():
                self.assertEqual(p3, p2)
                p2.moveToNext()
        self.assertFalse(p2)
    #@+node:ekr.20210830095545.13: *4* TestNodes.test_consistency_of_level
    def test_consistency_of_level(self):
        c, p = self.c, self.c.p
        for p in c.all_positions():
            if p.hasParent():
                self.assertEqual(p.parent().level(), p.level() - 1)
            if p.hasChildren():
                self.assertEqual(p.firstChild().level(), p.level() + 1)
            if p.hasNext():
                self.assertEqual(p.next().level(), p.level())
            if p.hasBack():
                self.assertEqual(p.back().level(), p.level())
    #@+node:ekr.20210830095545.14: *4* TestNodes.test_consistency_of_parent__parents_iter_
    def test_consistency_of_parent__parents_iter_(self):
        c, p = self.c, self.c.p
        for p in c.all_positions():
            p2 = p.parent()
            for p3 in p.parents_iter():
                self.assertEqual(p3, p2)
                p2.moveToParent()
            self.assertFalse(p2)
    #@+node:ekr.20210830095545.15: *4* TestNodes.test_consistency_of_parent_child_links
    def test_consistency_of_parent_child_links(self):
        # Test consistency of p.parent, p.next, p.back and p.firstChild.
        c, p = self.c, self.c.p
        for p in c.all_positions():
            if p.hasParent():
                n = p.childIndex()
                self.assertEqual(p, p.parent().moveToNthChild(n))
            for child in p.children_iter():
                self.assertEqual(p, child.parent())
            if p.hasNext():
                self.assertEqual(p.next().parent(), p.parent())
            if p.hasBack():
                self.assertEqual(p.back().parent(), p.parent())
    #@+node:ekr.20210830095545.16: *4* TestNodes.test_consistency_of_threadBack_Next_links
    def test_consistency_of_threadBack_Next_links(self):
        c, p = self.c, self.c.p
        for p in c.all_positions():
            threadBack = p.threadBack()
            threadNext = p.threadNext()
            if threadBack:
                self.assertEqual(p, threadBack.getThreadNext())
            if threadNext:
                self.assertEqual(p, threadNext.getThreadBack())
    #@+node:ekr.20210830095545.17: *4* TestNodes.test_convertTreeToString_and_allies
    def test_convertTreeToString_and_allies(self):
        p = self.c.p
        sib = p.next()
        self.assertTrue(sib)
        s = sib.convertTreeToString()
        for p2 in sib.self_and_subtree():
            self.assertTrue(p2.h in s)
    #@+node:ekr.20210830095545.43: *4* TestNodes.test_delete_node
    def test_delete_node(self):
        # This test requires @bool select-next-after-delete = False
        c, p = self.c, self.c.p
        p2 = p.insertAsNthChild(0)
        p2.setHeadString('A')
        p3 = p.insertAsNthChild(1)
        p3.setHeadString('B')
        p4 = p.insertAsNthChild(2)
        p4.setHeadString('C')
        p.expand()
        c.selectPosition(p3)
        c.deleteOutline()
        c.redraw_now()
        p = c.p
        self.assertEqual(p.h, 'A')
        self.assertEqual(p.next().h, 'C')
        c.undoer.undo()
        c.outerUpdate()
        p = c.p
        self.assertEqual(p.back(), p2)
        self.assertEqual(p.next(), p4)
        c.undoer.redo()
        c.outerUpdate()
        p = c.p
        self.assertEqual(p.h, 'A')
        self.assertEqual(p.next().h, 'C')
        c.undoer.undo()
        c.outerUpdate()
        p = c.p
        self.assertEqual(p.back(), p2)
        self.assertEqual(p.next(), p4)
        c.undoer.redo()
        c.outerUpdate()
        p = c.p
        self.assertEqual(p.h, 'A')
        self.assertEqual(p.next().h, 'C')
    #@+node:ekr.20210830095545.44: *4* TestNodes.test_deleting_the_root_should_select_another_node
    def test_deleting_the_root_should_select_another_node(self):
        c, p = self.c, self.c.p
        root_h = p.h
        child = p.next()
        child.moveToRoot()  # Does not change child position.
        c.setRootPosition(child)
        self.assertTrue(c.positionExists(child))
        self.assertEqual(c.rootPosition().h, child.h)
        next = c.rootPosition().next()
        self.assertEqual(next.h, root_h)
        c.rootPosition().doDelete(newNode=next)
        c.setRootPosition(next)
    #@+node:ekr.20210830095545.45: *4* TestNodes.test_demote
    def test_demote(self):
        c, p = self.c, self.c.p
        p2 = p.insertAsNthChild(0)
        p2.setHeadString('A')
        p3 = p.insertAsNthChild(1)
        p3.setHeadString('B')
        p4 = p.insertAsNthChild(2)
        p4.setHeadString('C')
        p5 = p.insertAsNthChild(3)
        p5.setHeadString('D')
        p.expand()
        c.setCurrentPosition(p3)
        c.demote()
        p = c.p
        self.assertEqual(p, p3)
        self.assertEqual(p.h, 'B')
        assert not p.next()
        self.assertEqual(p.firstChild().h, 'C')
        self.assertEqual(p.firstChild().next().h, 'D')
        c.undoer.undo()
        p = c.p
        self.assertEqual(p, p3)
        self.assertEqual(p.back(), p2)
        self.assertEqual(p.next(), p4)
        c.undoer.redo()
        self.assertEqual(p, p3)
        self.assertEqual(p.h, 'B')
        assert not p.next()
        self.assertEqual(p.firstChild().h, 'C')
        self.assertEqual(p.firstChild().next().h, 'D')
        c.undoer.undo()
        p = c.p
        self.assertEqual(p.back(), p2)
        self.assertEqual(p.next(), p4)
        c.undoer.redo()
        self.assertEqual(p, p3)
        self.assertEqual(p.h, 'B')
        assert not p.next()
        self.assertEqual(p.firstChild().h, 'C')
        self.assertEqual(p.firstChild().next().h, 'D')
    #@+node:ekr.20210830095545.46: *4* TestNodes.test_insert_node
    def test_insert_node(self):
        c, p = self.c, self.c.p
        self.assertEqual(p.h, 'root')
        p2 = p.insertAsNthChild(0)
        p2.setHeadString('A')
        p3 = p.insertAsNthChild(1)
        p3.setHeadString('B')
        p.expand()
        c.setCurrentPosition(p2)
        p4 = c.insertHeadline()
        self.assertEqual(p4, c.p)
        p = c.p
        self.assertTrue(p)
        p.setHeadString('inserted')
        self.assertTrue(p.back())
        self.assertEqual(p.back().h, 'A')
        self.assertEqual(p.next().h, 'B')
        # With the new undo logic, it takes 2 undoes.
        # The first undo undoes the headline changes,
        # the second undo undoes the insert node.
        c.undoer.undo()
        c.undoer.undo()
        p = c.p
        self.assertEqual(p, p2)
        self.assertEqual(p.next(), p3)
        c.undoer.redo()
        p = c.p
        self.assertTrue(p.back())
        self.assertEqual(p.back().h, 'A')
        self.assertEqual(p.next().h, 'B')
        c.undoer.undo()
        p = c.p
        self.assertEqual(p, p2)
        self.assertEqual(p.next(), p3)
        c.undoer.redo()
        p = c.p
        self.assertEqual(p.back().h, 'A')
        self.assertEqual(p.next().h, 'B')
    #@+node:ekr.20210830095545.18: *4* TestNodes.test_leoNodes_properties
    def test_leoNodes_properties(self):
        c, p = self.c, self.c.p
        v = p.v
        b = p.b
        p.b = b
        self.assertEqual(p.b, b)
        v.b = b
        self.assertEqual(v.b, b)
        h = p.h
        p.h = h
        self.assertEqual(p.h, h)
        v.h = h
        self.assertEqual(v.h, h)
        for p in c.all_positions():
            self.assertEqual(p.b, p.bodyString())
            self.assertEqual(p.v.b, p.v.bodyString())
            self.assertEqual(p.h, p.headString())
            self.assertEqual(p.v.h, p.v.headString())
    #@+node:ekr.20210830095545.47: *4* TestNodes.test_move_outline_down__undo_redo
    def test_move_outline_down__undo_redo(self):
        c, p = self.c, self.c.p
        p2 = p.insertAsNthChild(0)
        p2.setHeadString('A')
        p3 = p.insertAsNthChild(1)
        p3.setHeadString('B')
        p4 = p.insertAsNthChild(2)
        p4.setHeadString('C')
        p5 = p.insertAsNthChild(3)
        p5.setHeadString('D')
        p.expand()
        c.setCurrentPosition(p3)
        c.moveOutlineDown()
        moved = c.p
        self.assertEqual(moved.h, 'B')
        self.assertEqual(moved.back().h, 'C')
        self.assertEqual(moved.next().h, 'D')
        self.assertEqual(moved.next(), p5)
        c.undoer.undo()
        moved = c.p
        self.assertEqual(moved.back(), p2)
        self.assertEqual(moved.next(), p4)
        c.undoer.redo()
        moved = c.p
        self.assertEqual(moved.h, 'B')
        self.assertEqual(moved.back().h, 'C')
        self.assertEqual(moved.next().h, 'D')
        c.undoer.undo()
        moved = c.p
        self.assertEqual(moved.back(), p2)
        self.assertEqual(moved.next(), p4)
        c.undoer.redo()
        moved = c.p
        self.assertEqual(moved.h, 'B')
        self.assertEqual(moved.back().h, 'C')
        self.assertEqual(moved.next().h, 'D')
    #@+node:ekr.20210830095545.48: *4* TestNodes.test_move_outline_left
    def test_move_outline_left(self):
        c, p = self.c, self.c.p
        p2 = p.insertAsNthChild(0)
        p2.setHeadString('A')
        p.expand()
        c.setCurrentPosition(p2)
        c.moveOutlineLeft()
        moved = c.p
        self.assertEqual(moved.h, 'A')
        self.assertEqual(moved.back(), p)
        c.undoer.undo()
        c.undoer.redo()
        c.undoer.undo()
        c.undoer.redo()
        moved.doDelete(newNode=p)
    #@+node:ekr.20210830095545.49: *4* TestNodes.test_move_outline_right
    def test_move_outline_right(self):
        c, p = self.c, self.c.p
        p2 = p.insertAsNthChild(0)
        p2.setHeadString('A')
        p3 = p.insertAsNthChild(1)
        p3.setHeadString('B')
        p4 = p.insertAsNthChild(2)
        p4.setHeadString('C')
        p.expand()
        c.setCurrentPosition(p3)
        c.moveOutlineRight()
        moved = c.p
        self.assertEqual(moved.h, 'B')
        self.assertEqual(moved.parent(), p2)
        c.undoer.undo()
        c.undoer.redo()
        c.undoer.undo()
        c.undoer.redo()
    #@+node:ekr.20210830095545.50: *4* TestNodes.test_move_outline_up
    def test_move_outline_up(self):
        c, p = self.c, self.c.p
        p2 = p.insertAsNthChild(0)
        p2.setHeadString('A')
        p3 = p.insertAsNthChild(1)
        p3.setHeadString('B')
        p4 = p.insertAsNthChild(2)
        p4.setHeadString('C')
        p5 = p.insertAsNthChild(3)
        p5.setHeadString('D')
        p.expand()
        c.setCurrentPosition(p4)
        c.moveOutlineUp()
        moved = c.p
        self.assertEqual(moved.h, 'C')
        self.assertEqual(moved.back().h, 'A')
        self.assertEqual(moved.next().h, 'B')
        self.assertEqual(moved.back(), p2)
        c.undoer.undo()
        c.undoer.redo()
        c.undoer.undo()
        c.undoer.redo()
    #@+node:ekr.20210830095545.19: *4* TestNodes.test_new_vnodes_methods
    def test_new_vnodes_methods(self):
        c, p = self.c, self.c.p
        parent_v = p.parent().v or c.hiddenRootNode
        p.v.cloneAsNthChild(parent_v, p.childIndex())
        v2 = p.v.insertAsFirstChild()
        v2.h = 'insertAsFirstChild'
        v2 = p.v.insertAsLastChild()
        v2.h = 'insertAsLastChild'
        v2 = p.v.insertAsNthChild(1)
        v2.h = 'insertAsNthChild(1)'
    #@+node:ekr.20210830095545.20: *4* TestNodes.test_newlines_in_headlines
    def test_newlines_in_headlines(self):
        # Bug https://bugs.launchpad.net/leo-editor/+bug/1245535
        p = self.c.p
        p.h = '\nab\nxy\n'
        self.assertEqual(p.h, 'abxy')

    #@+node:ekr.20210830095545.54: *4* TestNodes.test_node_that_does_nott_belong_to_a_derived_file
    def test_node_that_does_not_belong_to_a_derived_file(self):
        # Change @file activeUnitTests.txt to @@file activeUnitTests.txt
        p = self.c.p
        p1 = p.insertAsLastChild()
        self.assertFalse(p1.textOffset())

    #@+node:ekr.20210830095545.56: *4* TestNodes.test_organizer_node
    def test_organizer_node(self):
        p = self.c.p
        p1 = p.insertAsLastChild()
        p1.setHeadString('@file zzz')
        p2 = p1.insertAsLastChild()
        self.assertEqual(p1.textOffset(), 0)
        self.assertEqual(p2.textOffset(), 0)

    #@+node:ekr.20210830095545.21: *4* TestNodes.test_p__eq_
    def test_p__eq_(self):
        c, p = self.c, self.c.p
        # These must not return NotImplemented!
        root = c.rootPosition()
        self.assertFalse(p.__eq__(None))
        self.assertTrue(p.__ne__(None))
        self.assertTrue(p.__eq__(root))
        self.assertFalse(p.__ne__(root))
    #@+node:ekr.20210830095545.24: *4* TestNodes.test_p_comparisons
    def test_p_comparisons(self):
        c, p = self.c, self.c.p
        copy = p.copy()
        self.assertEqual(p, copy)
        self.assertNotEqual(p, p.threadNext())
        root = c.rootPosition()
        self.assertTrue(p.__eq__(copy))
        self.assertFalse(p.__ne__(copy))
        self.assertTrue(p.__eq__(root))
        self.assertFalse(p.__ne__(root))
    #@+node:ekr.20210830095545.25: *4* TestNodes.test_p_deletePositionsInList
    def test_p_deletePositionsInList(self):
        c, p = self.c, self.c.p
        root = p.insertAsLastChild()
        root.h = 'root'
        # Top level
        a1 = root.insertAsLastChild()
        a1.h = 'a'
        a1.clone()
        d1 = a1.insertAfter()
        d1.h = 'd'
        b1 = root.insertAsLastChild()
        b1.h = 'b'
        # Children of a.
        b11 = b1.clone()
        b11.moveToLastChildOf(a1)
        b11.clone()
        c2 = b11.insertAfter()
        c2.h = 'c'
        # Children of d
        b11 = b1.clone()
        b11.moveToLastChildOf(d1)
        # Count number of 'b' nodes.
        aList = []
        nodes = 0
        for p in root.subtree():
            nodes += 1
            if p.h == 'b':
                aList.append(p.copy())
        self.assertEqual(len(aList), 6)
        c.deletePositionsInList(aList)

    #@+node:ekr.20210830095545.26: *4* TestNodes.test_p_hasNextBack
    def test_p_hasNextBack(self):
        c, p = self.c, self.c.p
        for p in c.all_positions():
            back = p.back()
            next = p.next()
            assert(
                (back and p.hasBack()) or
                (not back and not p.hasBack()))
            assert(
                (next and p.hasNext()) or
                (not next and not p.hasNext()))
    #@+node:ekr.20210830095545.27: *4* TestNodes.test_p_hasParentChild
    def test_p_hasParentChild(self):
        c, p = self.c, self.c.p
        for p in c.all_positions():
            child = p.firstChild()
            parent = p.parent()
            assert(
                (child and p.hasFirstChild()) or
                (not child and not p.hasFirstChild()))
            assert(
                (parent and p.hasParent()) or
                (not parent and not p.hasParent()))
    #@+node:ekr.20210830095545.28: *4* TestNodes.test_p_hasThreadNextBack
    def test_p_hasThreadNextBack(self):
        c, p = self.c, self.c.p
        for p in c.all_positions():
            threadBack = p.getThreadBack()
            threadNext = p.getThreadNext()
            assert(
                (threadBack and p.hasThreadBack()) or
                (not threadBack and not p.hasThreadBack()))
            assert(
                (threadNext and p.hasThreadNext()) or
                (not threadNext and not p.hasThreadNext()))
    #@+node:ekr.20210830095545.29: *4* TestNodes.test_p_isAncestorOf
    def test_p_isAncestorOf(self):
        c, p = self.c, self.c.p
        for p in c.all_positions():
            child = p.firstChild()
            while child:
                for parent in p.self_and_parents_iter():
                    assert parent.isAncestorOf(child)
                child.moveToNext()
            next = p.next()
            self.assertFalse(p.isAncestorOf(next))
    #@+node:ekr.20210830095545.30: *4* TestNodes.test_p_isCurrentPosition
    def test_p_isCurrentPosition(self):
        c, p = self.c, self.c.p
        self.assertFalse(c.isCurrentPosition(None))
        self.assertTrue(c.isCurrentPosition(p))
    #@+node:ekr.20210830095545.31: *4* TestNodes.test_p_isRootPosition
    def test_p_isRootPosition(self):
        c, p = self.c, self.c.p
        self.assertFalse(c.isRootPosition(None))
        self.assertTrue(c.isRootPosition(p))
    #@+node:ekr.20210830095545.33: *4* TestNodes.test_p_moveToFirst_LastChild
    def test_p_moveToFirst_LastChild(self):
        c, p = self.c, self.c.p
        root2 = p.next()
        self.assertTrue(root2)
        p2 = root2.insertAfter()
        p2.h = "test"
        self.assertTrue(c.positionExists(p2))
        p2.moveToFirstChildOf(root2)
        self.assertTrue(c.positionExists(p2))
        p2.moveToLastChildOf(root2)
        self.assertTrue(c.positionExists(p2))
    #@+node:ekr.20210830095545.34: *4* TestNodes.test_p_moveToVisBack_in_a_chapter
    def test_p_moveToVisBack_in_a_chapter(self):
        # Verify a fix for bug https://bugs.launchpad.net/leo-editor/+bug/1264350
        import leo.core.leoChapters as leoChapters
        c, p = self.c, self.c.p
        cc = c.chapterController
        settings_p = p.insertAsNthChild(0)
        settings_p.h = '@settings'
        chapter_p = settings_p.insertAsLastChild()
        chapter_p.h = '@chapter aaa'
        node_p = chapter_p.insertAsNthChild(0)
        node_p.h = 'aaa node 1'
        # Hack the chaptersDict.
        cc.chaptersDict['aaa'] = leoChapters.Chapter(c, cc, 'aaa')
        # Select the chapter.
        cc.selectChapterByName('aaa', collapse=True)
        self.assertEqual(c.p.h, 'aaa node 1')
        p2 = c.p.moveToVisBack(c)
        self.assertEqual(p2, None)
    #@+node:ekr.20210830095545.35: *4* TestNodes.test_p_nosentinels
    def test_p_nosentinels(self):

        p = self.c.p

        def not_a_sentinel(x):
            pass

        @not_a_sentinel
        def spam():
            pass

        s1 = ''.join(g.splitLines(p.b)[2:])
        s2 = p.nosentinels
        self.assertEqual(s1, s2)
    #@+node:ekr.20210830095545.22: *4* TestNodes.test_p_relinkAsCloneOf
    def test_p_relinkAsCloneOf(self):

        # test-outline: root
        #   child clone a
        #     node clone 1
        #   child b
        #     child clone a
        #       node clone 1
        #   child c
        #     node clone 1
        #   child clone a
        #     node clone 1
        #   child b
        #     child clone a
        #       node clone 1
        c, u = self.c, self.c.undoer
        p = c.p.next()
        child_b = g.findNodeAnywhere(c, 'child b')
        self.assertTrue(child_b)
        self.assertTrue(child_b.isCloned())
        #
        # child_c must *not* be a clone at first.
        child_c = g.findNodeAnywhere(c, 'child c')
        self.assertTrue(child_c)
        self.assertFalse(child_c.isCloned())
        #
        # Change the tree.
        bunch = u.beforeChangeTree(p)
        child_c._relinkAsCloneOf(child_b)
        u.afterChangeTree(p, 'relink-clone', bunch)
        # self.dump_tree('Before...')
        u.undo()
        # self.dump_tree('After...')
        self.assertTrue(child_b.isCloned())
        self.assertFalse(child_c.isCloned())

    #@+node:ekr.20210830095545.36: *4* TestNodes.test_p_setBodyString
    def test_p_setBodyString(self):
        # Test that c.setBodyString works immediately.
        c, w = self.c, self.c.frame.body.wrapper
        next = self.root_p.next()
        c.setBodyString(next, "after")
        c.selectPosition(next)
        s = w.get("1.0", "end")
        self.assertEqual(s.rstrip(), "after")
    #@+node:ekr.20210830095545.37: *4* TestNodes.test_p_u
    def test_p_u(self):
        p = self.c.p
        self.assertEqual(p.u, p.v.u)
        p.v.u = None
        self.assertEqual(p.u, {})
        self.assertEqual(p.v.u, {})
        d = {'my_plugin': 'val'}
        p.u = d
        self.assertEqual(p.u, d)
        self.assertEqual(p.v.u, d)
    #@+node:ekr.20210830095545.38: *4* TestNodes.test_p_unique_nodes
    def test_p_unique_nodes(self):

        self.assertEqual(len(list(self.root_p.unique_nodes())), 5)
    #@+node:ekr.20210830095545.51: *4* TestNodes.test_paste_node
    def test_paste_node(self):
        c, p = self.c, self.c.p
        child = p.insertAsNthChild(0)
        child.setHeadString('child')
        child2 = p.insertAsNthChild(1)
        child2.setHeadString('child2')
        grandChild = child.insertAsNthChild(0)
        grandChild.setHeadString('grand child')
        c.selectPosition(grandChild)
        c.clone()
        c.selectPosition(child)
        p.expand()
        c.selectPosition(child)
        self.assertEqual(c.p.h, 'child')
        c.copyOutline()
        oldVnodes = [p2.v for p2 in child.self_and_subtree()]
        c.selectPosition(child)
        c.p.contract()  # Essential
        c.pasteOutline()
        assert c.p != child
        self.assertEqual(c.p.h, 'child')
        newVnodes = [p2.v for p2 in c.p.self_and_subtree()]
        for v in newVnodes:
            assert v not in oldVnodes
        c.undoer.undo()
        c.undoer.redo()
        c.undoer.undo()
        c.undoer.redo()
    #@+node:ekr.20210830095545.52: *4* TestNodes.test_paste_retaining_clones
    def test_paste_retaining_clones(self):
        c, p = self.c, self.c.p
        child = p.insertAsNthChild(0)
        child.setHeadString('child')
        self.assertTrue(child)
        grandChild = child.insertAsNthChild(0)
        grandChild.setHeadString('grand child')
        c.selectPosition(child)
        c.copyOutline()
        oldVnodes = [p2.v for p2 in child.self_and_subtree()]
        c.p.contract()  # Essential
        c.pasteOutlineRetainingClones()
        self.assertNotEqual(c.p, child)
        newVnodes = [p2.v for p2 in c.p.self_and_subtree()]
        for v in newVnodes:
            self.assertTrue(v in oldVnodes)
    #@+node:ekr.20210830095545.4: *4* TestNodes.test_position_not_hashable
    def test_position_not_hashable(self):
        p = self.c.p
        try:
            a = set()
            a.add(p)
            assert False, 'Adding position to set should throw exception'
        except TypeError:
            pass
    #@+node:ekr.20210830095545.53: *4* TestNodes.test_promote
    def test_promote(self):
        c, p = self.c, self.c.p
        p2 = p.insertAsNthChild(0)
        p2.setHeadString('A')
        p3 = p.insertAsNthChild(1)
        p3.setHeadString('B')
        p4 = p3.insertAsNthChild(0)
        p4.setHeadString('child 1')
        p5 = p3.insertAsNthChild(1)
        p5.setHeadString('child 2')
        p.expand()
        p6 = p.insertAsNthChild(2)
        p6.setHeadString('C')
        c.setCurrentPosition(p3)
        c.promote()
        p = c.p
        self.assertEqual(p, p3)
        self.assertEqual(p.h, 'B')
        self.assertEqual(p.next().h, 'child 1')
        self.assertEqual(p.next().next().h, 'child 2')
        self.assertEqual(p.next().next().next().h, 'C')
        c.undoer.undo()
        p = c.p
        self.assertEqual(p, p3)
        self.assertEqual(p.back(), p2)
        self.assertEqual(p.next(), p6)
        self.assertEqual(p.firstChild().h, 'child 1')
        self.assertEqual(p.firstChild().next().h, 'child 2')
        c.undoer.redo()
        p = c.p
        self.assertEqual(p, p3)
        self.assertEqual(p.h, 'B')
        self.assertEqual(p.next().h, 'child 1')
        self.assertEqual(p.next().next().h, 'child 2')
        self.assertEqual(p.next().next().next().h, 'C')
        c.undoer.undo()
        p = c.p
        self.assertEqual(p, p3)
        self.assertEqual(p.back(), p2)
        self.assertEqual(p.next(), p6)
        self.assertEqual(p.firstChild().h, 'child 1')
        self.assertEqual(p.firstChild().next().h, 'child 2')
        c.undoer.redo()
        p = c.p
        self.assertEqual(p, p3)
        self.assertEqual(p.h, 'B')
        self.assertEqual(p.next().h, 'child 1')
        self.assertEqual(p.next().next().h, 'child 2')
        self.assertEqual(p.next().next().next().h, 'C')
    #@+node:ekr.20210830095545.55: *4* TestNodes.test_root_of_a_derived_file
    def test_root_of_a_derived_file(self):
        p = self.c.p
        p1 = p.insertAsLastChild()
        p1.setHeadString('@file zzz')
        self.assertEqual(p1.textOffset(), 0)
    #@+node:ekr.20210830095545.57: *4* TestNodes.test_section_node
    def test_section_node(self):
        p = self.c.p
        p1 = p.insertAsLastChild()
        p1.setHeadString('@file zzz')
        body = '''   %s
        ''' % (g.angleBrackets(' section '))
        p1.setBodyString(body)
        p2 = p1.insertAsLastChild()
        head = g.angleBrackets(' section ')
        p2.setHeadString(head)
        self.assertEqual(p1.textOffset(), 0)
        self.assertEqual(p2.textOffset(), 3)
            # Section nodes can appear in with @others nodes,
            # so they don't get special treatment.
    #@+node:ekr.20210830095545.39: *4* TestNodes.test_v_atAutoNodeName_and_v_atAutoRstNodeName
    def test_v_atAutoNodeName_and_v_atAutoRstNodeName(self):
        p = self.c.p
        table = (
            ('@auto-rst rst-file', 'rst-file', 'rst-file'),
            ('@auto x', 'x', ''),
            ('xyz', '', ''),
        )
        for s, expected1, expected2 in table:
            result1 = p.v.atAutoNodeName(h=s)
            result2 = p.v.atAutoRstNodeName(h=s)
            self.assertEqual(result1, expected1, msg=s)
            self.assertEqual(result2, expected2, msg=s)
    #@-others
#@-others

#@-leo

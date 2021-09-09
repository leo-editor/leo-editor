# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20210908171733.1: * @file ../unittests/core/test_leoPersistence.py
#@@first
"""Tests for leo.core.leoPersistence"""

from leo.core import leoGlobals as g
from leo.core.leoTest2 import LeoUnitTest
assert g

#@+others
#@+node:ekr.20210908171733.2: ** class TestPersistence(LeoUnitTest)
class TestPersistence(LeoUnitTest):
    """Unit tests for leo/core/leoPersistence.py."""
    #@+others
    #@+node:ekr.20210908171733.3: *3* TestPersistence.setUp
    def setUp(self):
        """Create the nodes in the commander."""
        super().setUp()
        c = self.c
        self.create_test_outline()
        c.selectPosition(c.rootPosition())
    #@+node:ekr.20210908173748.1: *3* TestPersistence.create_test_outline
    def create_test_outline(self):
        c = self.c
        # Create the standard tree.
        super().create_test_outline()
        # Add an @settings, @persistence and @gnx nodes.
        settings_p = c.lastTopLevel()
        settings_p.b = '@settings'
        persistence_p = settings_p.insertAfter()
        persistence_p.h = '@persistence'
        gnx_p = persistence_p.insertAsLastChild()
        gnx_p.h = '@gnxs'
        gnx_p.b = (
            'gnx: ekr.20140923080452\n'
            'unl: node1\n'
        )

        # - root
            # - aClass
              # - clone
              # - organizer node
                # - child2
            # - clone
        # - node 1
          # - child1
          # - child12
        # - node 2
          # - child21
          # - child22
        # - node 3
          # - node3_child1
    #@+node:ekr.20210908172651.2: *3* TestPersistence.test_p_sort_key
    def test_p_sort_key(self):
        c, p = self.c, self.c.p
        aList = [z.copy() for z in c.all_positions()]
        aList2 = sorted(reversed(aList), key=p.sort_key)
        for i, p in enumerate(aList2):
            p2 = aList[i]
            self.assertEqual(p, p2, msg=f"i: {i}, p.h: {p.h}. p2: {p2.h}")
    #@+node:ekr.20210908172651.3: *3* TestPersistence.test_pd_find_at_data_and gnxs_nodes
    def test_pd_find_at__(self):
        pd = self.c.persistenceController
        # Also a test of find_at_views_node, find_at_organizers_node and find_at_clones_node.
        persistence = pd.find_at_persistence_node()
        assert persistence
        persistence.deleteAllChildren()
        root = self.root_p
        root.h = '@auto root' # Make root look like an @auto node.
        assert pd.find_at_data_node(root)
        assert pd.find_at_gnxs_node(root)
    #@+node:ekr.20210908172651.9: *3* TestPersistence.test_pd_find_position_for_relative_unl
    def test_pd_find_position_for_relative_unl(self):
        p, pd = self.c.p, self.c.persistenceController
        parent = p.copy()
        # node1
        node1 = parent.insertAsLastChild()
        node1.h = 'node1'
        child11 = node1.insertAsLastChild()
        child11.h = 'child11'
        child12 = node1.insertAsLastChild()
        child12.h = 'child12'
        # node2
        node2 = parent.insertAsLastChild()
        node2.h = 'node2'
        child21 = node2.insertAsLastChild()
        child21.h = 'child21'
        child22 = node2.insertAsLastChild()
        child22.h = 'child22'
        # node3
        node3 = parent.insertAsLastChild()
        node3.h = 'node3'
        table = (
            ('', parent), # Important special case.
            ('node1-->child11', child11),
            ('node1-->child12', child12),
            ('node2', node2),
            ('node2-->child21', child21),
            ('node2-->child22', child22),
            # Partial matches.
                # ('node3-->child1-->child21',node3_child1_child21),
                # ('child1-->child21',node3_child1_child21),
                # ('xxx-->child21',node3_child1_child21),
                    # This is ambiguous.
            # No matches.
            ('nodex', None),
            ('node1-->childx', None),
            ('node3-->childx', None),
        )
        for unl, expected in table:
            result = pd.find_position_for_relative_unl(parent, unl)
            self.assertEqual(result, expected, msg=unl)
    #@-others
#@-others

#@-leo

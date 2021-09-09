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
    #@+node:ekr.20210908172651.1: *3* Converted nodes
    #@+node:ekr.20210908172651.2: *4* TestPersistence.test_p_sort_key
    def test_p_sort_key(self):
        c, p = self.c, self.c.p
        aList = [z.copy() for z in c.all_positions()]
        aList2 = sorted(reversed(aList), key=p.sort_key)
        for i, p in enumerate(aList2):
            p2 = aList[i]
            self.assertEqual(p, p2, msg=f"i: {i}, p.h: {p.h}. p2: {p2.h}")
    #@+node:ekr.20210908172651.3: *4* TestPersistence.test_pd_find_at_data_and gnxs_nodes
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
    #@-others
#@-others

#@-leo

#@+leo-ver=5-thin
#@+node:ekr.20210908171733.1: * @file ../unittests/core/test_leoPersistence.py
"""Test of leoPersistence.py"""

from leo.core import leoGlobals as g
from leo.core.leoTest2 import LeoUnitTest
assert g

#@+others
#@+node:ekr.20210908171733.2: ** class TestPersistence(LeoUnitTest)
class TestPersistence(LeoUnitTest):
    """Unit tests for leo/core/leoPersistence.py."""
    #@+others
    #@+node:ekr.20210908173748.1: *3*  TestPersistence.create_test_outline
    def create_test_outline(self):
        c = self.c
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
    #@+node:ekr.20210908171733.3: *3*  TestPersistence.setUp
    def setUp(self):
        """Create the nodes in the commander."""
        super().setUp()
        c = self.c
        self.create_test_outline()
        c.selectPosition(c.rootPosition())
    #@+node:ekr.20210908172651.44: *3* TestPersistence.test_delete_all_children_of_persistence_node
    def test_delete_all_children_of_persistence_node(self):
        c, pd = self.c, self.c.persistenceController
        persistence = g.findNodeAnywhere(c, '@persistence')
        assert persistence
        assert pd.has_at_persistence_node()
        persistence.deleteAllChildren()
        assert persistence
    #@+node:ekr.20210908172651.2: *3* TestPersistence.test_p_sort_key
    def test_p_sort_key(self):
        c, p = self.c, self.c.p
        aList = [z.copy() for z in c.all_positions()]
        aList2 = sorted(aList, key=p.sort_key)
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
        root.h = '@auto root'  # Make root look like an @auto node.
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
            ('', parent),  # Important special case.
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
    #@+node:ekr.20210908172651.19: *3* TestPersistence.test_pd_find_representative_node
    def test_pd_find_representative_node(self):
        pd = self.c.persistenceController
        root = self.root_p
        root.h = '@auto root'
        inner_clone = root.insertAsLastChild()
        inner_clone.h = 'clone'
        outer_clone = inner_clone.clone()
        outer_clone.moveAfter(root)
        rep = pd.find_representative_node(root, inner_clone)
        assert rep
        self.assertEqual(rep, outer_clone)
    #@+node:ekr.20210908172651.23: *3* TestPersistence.test_pd_has_at_gnxs_node
    def test_pd_has_at_gnxs_node(self):
        c, pd = self.c, self.c.persistenceController
        # Set up the tree.
        root = self.root_p
        root.h = '@auto root'  # Make root look like an @auto node.
        inner_clone = root.insertAsLastChild()
        inner_clone.h = 'clone'
        outer_clone = inner_clone.clone()
        outer_clone.moveAfter(root)
        # Test the tree.
        persistence = g.findNodeAnywhere(c, '@persistence')
        assert persistence
        assert pd.has_at_persistence_node()
        # Update the tree.
        persistence.deleteAllChildren()  # Required
        assert persistence
        pd.update_before_write_foreign_file(root)
        data = g.findNodeInTree(c, persistence, '@data:@auto root')
        assert data
        data2 = pd.has_at_data_node(root)
        assert data2
        self.assertEqual(data, data2, (data, data2))
        gnxs = g.findNodeInTree(c, persistence, '@gnxs')
        assert gnxs
        gnxs2 = pd.has_at_gnxs_node(root)
        assert gnxs2
        self.assertEqual(gnxs, gnxs2, (gnxs, gnxs2))
    #@+node:ekr.20210908172651.30: *3* TestPersistence.test_pd_restore_gnxs
    def test_pd_restore_gnxs(self):
        c, pd = self.c, self.c.persistenceController
        root = self.root_p
        # Set up the tree.
        persistence = g.findNodeAnywhere(c, '@persistence')
        assert persistence
        gnxs = g.findNodeAnywhere(c, '@gnxs')
        assert gnxs
        inner_clone = root.insertAsLastChild()
        inner_clone.h = 'clone'
        outer_clone = inner_clone.clone()
        outer_clone.moveAfter(root)
        node1 = root.insertAsLastChild()
        node1.h = 'node1'
        # Test.
        root.deleteAllChildren()
        pd.restore_gnxs(gnxs, root)
    #@+node:ekr.20210908172651.35: *3* TestPersistence.test_pd_unl
    def test_pd_unl(self):
        c, pd = self.c, self.c.persistenceController
        root = self.root_p
        node1 = root.insertAsLastChild()
        node1.h = 'node1'
        c.selectPosition(node1)
        unl = pd.unl(c.p)
        expected = f"-->{c.p.h}"
        assert unl.endswith(expected), repr(unl)
    #@+node:ekr.20210908172651.36: *3* TestPersistence.test_pd_update_before_write_foreign_file
    def test_pd_update_before_write_foreign_file(self):
        c, pd = self.c, self.c.persistenceController
        root = self.root_p
        assert root
        persistence = pd.find_at_persistence_node()
        assert persistence
        persistence.deleteAllChildren()
        root.h = '@auto root'  # Make root look like an @auto node.
        pd.update_before_write_foreign_file(root)
        data = g.findNodeAnywhere(c, '@data:@auto root')
        assert data
        gnxs = g.findNodeInTree(c, data, '@gnxs')
        assert gnxs
    #@-others
#@-others

#@-leo

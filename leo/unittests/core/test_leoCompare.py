#@+leo-ver=5-thin
#@+node:ekr.20230714131540.1: * @file ../unittests/core/test_leoCompare.py
"""Tests of leoCommands.py"""
from leo.core import leoGlobals as g
from leo.core.leoTest2 import LeoUnitTest
assert g

#@+others
#@+node:ekr.20230714131540.2: ** class TestCompare(LeoUnitTest)
class TestCompare(LeoUnitTest):
    """Test cases for leoCompare.py"""
    #@+others
    #@+node:ekr.20230714131540.3: *3* TestCompare.test_diff_marked_nodes
    def test_diff_marked_nodes(self):
        
        from leo.core.leoCompare import diffMarkedNodes
        
        # Setup.
        c = self.c
        u = c.undoer
        root = c.rootPosition()
        root.deleteAllChildren()
        while root.hasNext():
            root.next().doDelete()
        c.selectPosition(root)
        
        # Create two sets of nodes.
        node1 = root.insertAsLastChild()
        node2 = root.insertAsLastChild()
        child1 = node1.insertAsLastChild()
        child2 = node2.insertAsLastChild()
        
        # Mark the nodes.
        node1.setMarked()
        node2.setMarked()
        
        # Populate the nodes.
        table = (
            (node1, 'node 1', '# Node 1.\n'),
            (node2, 'node 1a', '# Node 1.\n'),  # Headlines differ.
            (child1, 'child 1', '# Child 1.\n'),
            (child2, 'child 1', '# Child 1a.\n'),  # Bodies differ.
        )
        for p, h, b in table:
            p.h = h
            p.b = b
        self.assertEqual(c.lastTopLevel(), root)

        # Run the command.
        diffMarkedNodes(event={'c': c})
        self.assertEqual(c.lastTopLevel().h, 'diff marked nodes')
        u.undo()
        self.assertEqual(c.lastTopLevel(), root)
        u.redo()
        self.assertEqual(c.lastTopLevel().h, 'diff marked nodes')
    #@-others
#@-others
#@-leo

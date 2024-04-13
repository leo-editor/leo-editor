#@+leo-ver=5-thin
#@+node:ekr.20210910065135.1: * @file ../unittests/core/test_leoFileCommands.py
"""Tests of leoFileCommands.py."""

import leo.core.leoFileCommands as leoFileCommands
from leo.core.leoTest2 import LeoUnitTest

#@+others
#@+node:ekr.20210910065135.2: ** class TestFileCommands (LeoUnitTest)
class TestFileCommands(LeoUnitTest):
    #@+others
    #@+node:ekr.20210909194336.24: *3* TestFileCommands.test_fc_resolveArchivedPosition
    def test_fc_resolveArchivedPosition(self):
        c, root = self.c, self.root_p
        root_v = root.v
        # Create the test tree. Headlines don't matter.
        child1 = root.insertAsLastChild()
        child2 = root.insertAsLastChild()
        grandChild1 = child2.insertAsLastChild()
        grandChild2 = child2.insertAsLastChild()
        greatGrandChild11 = grandChild1.insertAsLastChild()
        greatGrandChild12 = grandChild1.insertAsLastChild()
        greatGrandChild21 = grandChild2.insertAsLastChild()
        greatGrandChild22 = grandChild2.insertAsLastChild()
        table = (
            # Errors.
            (None, '-1'),
            # (None, '1'),
            (None, '0.2'),
            (None, '0.0.0'),
            (None, '0.1.2'),
            # Valid.
            (root_v, '0'),
            (child1.v, '0.0'),
            (child2.v, '0.1'),
            (grandChild1.v, '0.1.0'),
            (greatGrandChild11.v, '0.1.0.0'),
            (greatGrandChild12.v, '0.1.0.1'),
            (grandChild2.v, '0.1.1'),
            (greatGrandChild21.v, '0.1.1.0'),
            (greatGrandChild22.v, '0.1.1.1'),
        )
        for v, archivedPosition in table:
            if v is None:
                with self.assertRaises(AssertionError):
                    c.fileCommands.resolveArchivedPosition(archivedPosition, root_v)
            else:
                v2 = c.fileCommands.resolveArchivedPosition(archivedPosition, root_v)
                self.assertEqual(v, v2)
    #@+node:ekr.20210909194336.33: *3* TestFileCommands.test_p_archivedPosition
    def test_p_archivedPosition(self):
        p, root = self.c.p, self.root_p
        # Create the test tree. Headlines don't matter.
        child1 = root.insertAsLastChild()
        child2 = root.insertAsLastChild()
        grandChild1 = child2.insertAsLastChild()
        grandChild2 = child2.insertAsLastChild()
        assert child1 and grandChild1 and grandChild2
        # Tests...
        val = p.archivedPosition(root_p=p)
        self.assertEqual(val, [0])
        for i, z in enumerate(list(p.children_iter())):
            val = z.archivedPosition(root_p=p)
            self.assertEqual(val, [0, i])
        for i, z in enumerate(list(p.firstChild().next().children_iter())):
            val = z.archivedPosition(root_p=p)
            self.assertEqual(val, [0, 1, i])
    #@+node:ekr.20210909194336.38: *3* TestFileCommands.test_putDescendentVnodeUas
    def test_putDescendentVnodeUas(self):
        c, root = self.c, self.root_p
        fc = c.fileCommands
        # Create the test tree. Headlines don't matter.
        child1 = root.insertAsLastChild()
        child2 = root.insertAsLastChild()
        grandchild2 = child2.insertAsLastChild()
        # Set the uA's.
        child1.v.unknownAttributes = {'unit_test_child': 'abcd'}
        grandchild2.v.unknownAttributes = {'unit_test_grandchild': 'wxyz'}
        # Test.
        s = fc.putDescendentVnodeUas(root)
        assert s.startswith(' descendentVnodeUnknownAttributes='), s
    #@+node:ekr.20210909194336.39: *4* child
    #@+node:ekr.20210909194336.40: *5* grandChild
    #@+node:ekr.20210909194336.41: *3* TestFileCommands.test_putUa
    def test_putUa(self):
        c, p = self.c, self.c.p
        fc = c.fileCommands
        p.v.unknownAttributes = {'unit_test': 'abcd'}
        s = fc.putUnknownAttributes(p.v)
        expected = ' unit_test="58040000006162636471002e"'
        self.assertEqual(s, expected)
    #@+node:ekr.20210905052021.32: *3* TestFileCommands.test_fast_readWithElementTree
    def test_fast_readWithElementTree(self):
        # Test that readWithElementTree strips all control characters except '\t\r\n'.
        c = self.c
        s = chr(0) + 'a' + chr(12) + 'b' + '\t\r\n' + 'c'
        self.assertEqual(len(s), 8)
        d = leoFileCommands.FastRead(c, {}).translate_dict
        s2 = s.translate(d)
        self.assertEqual(s2, 'ab\t\r\nc')
    #@-others
#@-others
#@-leo

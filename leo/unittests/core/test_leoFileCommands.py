# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20210910065135.1: * @file ../unittests/core/test_leoFileCommands.py
#@@first
"""Tests of leoFileCommands.py"""

from leo.core import leoGlobals as g
import leo.core.leoApp as leoApp
from leo.core.leoTest2 import LeoUnitTest
import leo.core.leoExternalFiles as leoExternalFiles

#@+others
#@+node:ekr.20210910065135.2: ** class TestFileCommands (LeoUnitTest)
class TestFileCommands(LeoUnitTest):
    #@+others
    #@+node:ekr.20210910065135.3: *3* TestFileCommands.setUp
    def setUp(self):
        """setUp for TestFind class"""
        super().setUp()
        c = self.c
        g.app.idleTimeManager = leoApp.IdleTimeManager()
        g.app.idleTimeManager.start()
        g.app.externalFilesController = leoExternalFiles.ExternalFilesController(c=c)
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
            (None, '1'),
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
        for i, z in enumerate(list(p.parent().children_iter())):
            val = z.archivedPosition(root_p=p.parent())
            self.assertEqual(val, [0, i])
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
    #@-others
#@-others
#@-leo

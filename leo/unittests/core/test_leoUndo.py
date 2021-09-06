# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20210906141410.1: * @file ../unittests/core/test_leoUndo.py
#@@first
"""Tests of leoUndo.py"""

from leo.core import leoGlobals as g
from leo.core.leoTest2 import LeoUnitTest
assert g

#@+others
#@+node:ekr.20210906141410.2: ** class TestUndo (LeoUnitTest)
class TestShadow(LeoUnitTest):
    """
    Support @shadow-test nodes.

    These nodes should have two descendant nodes: 'before' and 'after'.
    """
    #@+others
    #@+node:ekr.20210906141410.9: *3* TestUndo.runTest (Test)
    def runTest(self, before, after, func):
        """TestUndo.runTest."""
        c = self.c
        self.assertNotEqual(before, after)
        result = func()
        self.assertEqual(result, after, msg='before undo1')
        c.undoer.undo()
        self.assertEqual(result, before, msg='after undo1')
        c.undoer.redo()
        self.assertEqual(result, after, msg='after redo1')
        c.undoer.undo()
        self.assertEqual(result, before, msg='after undo2')
    #@-others
#@-others
#@-leo

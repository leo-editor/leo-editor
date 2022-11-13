# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20221113062857.1: * @file ../unittests/commands/test_outlineCommands.py
#@@first
"""Tests for Leo's outline commands"""
### import textwrap
### from leo.core import leoGlobals as g
from leo.core.leoTest2 import LeoUnitTest
#@+others
#@+node:ekr.20221113062938.1: ** class TestOutlineCommands(LeoUnitTest)
class TestOutlineCommands(LeoUnitTest):
    """
    Unit tests for Leo's outline commands.
    """
    #@+others
    #@+node:ekr.20221112051634.1: *3* TestOutlineCommands.test_sort_children
    def test_sort_children(self):
        c = self.c
        if 0:
            self.dump_tree(c.p, tag='Initial tree')
    #@+node:ekr.20221112051650.1: *3* TestOutlineCommands.test_sort_siblings
    def test_sort_siblings(self):
        c = self.c
        if 0:
            self.dump_tree(c.p, tag='Initial tree')
    #@-others
#@-others
#@-leo

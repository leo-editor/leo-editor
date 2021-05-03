# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20201203042030.1: * @file ../unittests/core/test_leoNodes.py
#@@first
"""Tests for leo.core.leoNodes"""

import unittest
from leo.core import leoGlobals as g
from leo.core import leoTest2

class LeoNodesTest(unittest.TestCase):
    """Unit tests for leo/core/leoNodes.py."""
    #@+others
    #@+node:ekr.20201203042409.2: ** LeoNodesTest.run_test
    def run_test(self):
        c = self.c
        assert c
    #@+node:ekr.20201203042409.3: ** LeoNodesTest.setUp & tearDown
    def setUp(self):
        """Create the nodes in the commander."""
        # Create a new commander for each test.
        # This is fast, because setUpClass has done all the imports.
        from leo.core import leoCommands
        self.c = c = leoCommands.Commands(fileName=None, gui=g.app.gui)
        c.selectPosition(c.rootPosition())

    def tearDown(self):
        self.c = None
    #@+node:ekr.20201203042409.4: ** LeoNodesTest.setUpClass
    @classmethod
    def setUpClass(cls):
        leoTest2.create_app()
    #@+node:ekr.20201203042645.1: ** LeoNodesTest: test cases
    #@+node:ekr.20201203042550.1: *3* test_test
    def test_test(self):
        self.run_test()
    #@-others
#@-leo

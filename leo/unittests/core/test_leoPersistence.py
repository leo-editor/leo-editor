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
    
    test_outline = None  # Set by create_test_outline.

    #@+others
    #@+node:ekr.20210908171733.3: *3* TestPersistence.setUp
    def setUp(self):
        """Create the nodes in the commander."""
        super().setUp()
        c = self.c
        self.create_test_outline()
        c.selectPosition(c.rootPosition())
    #@-others
#@-others

#@-leo

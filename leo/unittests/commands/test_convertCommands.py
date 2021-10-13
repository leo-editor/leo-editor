# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20211013081056.1: * @file ../unittests/commands/test_convertCommands.py
#@@first
"""Tests of leo.commands.leoConvertCommands."""
import re
from leo.core import leoGlobals as g
from leo.core.leoTest2 import LeoUnitTest
assert re  ###
assert g ###

#@+others
#@+node:ekr.20211013081200.1: ** class TestPythonToTypeScript(LeoUnitTest):
class TestPythonToTypeScript(LeoUnitTest):
    """Test cases for leo/commands/leoConvertCommands.py"""
    
    def setUp(self):
        super().setUp()
        c = self.c
        self.x = c.convertCommands.PythonToTypescript(c)

    #@+others
    #@+node:ekr.20211013081200.2: *3* test_setup
    def test_setup(self):
        assert self.x
    #@-others
#@-others


#@-leo

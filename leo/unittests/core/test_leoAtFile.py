# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20210901172411.1: * @file ../unittests/core/test_leoAtFile.py
#@@first
"""Tests of leoApp.py"""
import textwrap
from leo.core import leoGlobals as g
from leo.core.leoTest2 import LeoUnitTest
#@+others
#@+node:ekr.20210901172446.1: ** class TestAtFile(LeoUnitTest)
class TestApp(LeoUnitTest):
    """Test cases for leoApp.py"""
    #@+others
    #@+node:ekr.20210901140645.14: *3* TestAtFile.test_at_tabNannyNode
    def test_at_tabNannyNode(self):
        ### @tabwidth -4
        c, p = self.c, self.c.p
        at = c.atFileCommands
        s = '''
        # no error
        def spam():
            pass
        '''
        at.tabNannyNode (p, body=s, suppress=True)
        s2 = '''
        # syntax error
        def spam:
            pass
          a = 2
        '''
        try:
            at.tabNannyNode(p,body=s2,suppress=True)
        except IndentationError:
            pass
    #@+node:ekr.20210901140645.13: *3* TestAtFile.test_at_checkPythonSyntax
    def test_at_checkPythonSyntax(self):
        c, p = self.c, self.c.p
        at = c.atFileCommands
        s = textwrap.dedent('''\
    # no error
    def spam():
        pass
        ''')
        assert at.checkPythonSyntax(p,s),'fail 1'

        s2 = textwrap.dedent('''\
    # syntax error
    def spam:  # missing parens.
        pass
        ''')

        assert not at.checkPythonSyntax(p,s2,supress=True),'fail2'

        if not g.unitTesting: # A hand test of at.syntaxError
            at.checkPythonSyntax(p,s2)
    #@-others
#@-others
#@-leo

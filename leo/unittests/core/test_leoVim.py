#@+leo-ver=5-thin
#@+node:ekr.20210910072917.1: * @file ../unittests/core/test_leoVim.py
"""Tests of leoVim.py"""

from leo.core import leoGlobals as g
from leo.core.leoTest2 import LeoUnitTest
assert g

#@+others
#@+node:ekr.20210910072917.2: ** class TestVim (LeoUnitTest)
class TestVim(LeoUnitTest):
    #@+others
    #@+node:ekr.20210909194336.58: *3* TestVim.test_vc_on_same_line
    def test_vc_on_same_line(self):
        c = self.c
        vc = c.vimCommands
        s = self.prep("""
            abc
            xyz
            pdq
        """)
        table = (
            ('ab', 'y', False),
            ('a', 'c', True),
            ('x', '\np', True),
            ('\nx', 'z', False),
        )
        for a, b, expected in table:
            i1, i2 = s.find(a), s.find(b)
            result = vc.on_same_line(s, i1, i2)
            self.assertEqual(result, expected, msg=s[i1:i2])
    #@+node:ekr.20210909194336.59: *3* TestVim.test_vc_to_bol
    def test_vc_to_bol(self):
        c = self.c
        vc = c.vimCommands
        s = self.prep("""
            abc
            xyz
        """)
        table = (
            ('a', 'a'),
            ('a', 'b'),
            ('a', '\nx')
        )
        for a, b, in table:
            i1, i2 = s.find(a), s.find(b)
            result = vc.to_bol(s, i2)
            self.assertEqual(result, i1, msg=s[i1:i2])
    #@+node:ekr.20210909194336.60: *3* TestVim.test_vc_to_eol
    def test_vc_to_eol(self):
        c = self.c
        vc = c.vimCommands
        s = self.prep("""
            abc
            xyz
        """)
        table = (
            ('a', '\nx'),
            ('b', '\nx'),
            ('c', '\nx'),
            ('\nx', '\nx'),
        )
        for a, b, in table:
            i1, i2 = s.find(a), s.find(b)
            result = vc.to_eol(s, i1)
            self.assertEqual(result, i2, msg=s[i1:i2])
    #@-others
#@-others
#@-leo

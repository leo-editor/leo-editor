# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20210903161742.1: * @file ../unittests/core/test_leoFrame.py
#@@first
"""Tests of leoFrame.py"""

import textwrap
from leo.core.leoTest2 import LeoUnitTest

#@+others
#@+node:ekr.20210903161742.2: ** class TestFrame(LeoUnitTest)
class TestFrame(LeoUnitTest):
    """Test cases for leoKeys.py"""
    #@+others
    #@+node:ekr.20210901140645.10: *3* TestFrame.test_official_frame_ivars
    def test_official_frame_ivars(self):
        c = self.c
        f = c.frame
        self.assertEqual(f.c, c)
        self.assertEqual(c.frame, f)
        for ivar in ('body', 'iconBar', 'log', 'statusLine', 'tree',):
            assert hasattr(f, ivar), 'missing frame ivar: %s' % ivar
            val = getattr(f, ivar)
            self.assertTrue(val is not None, msg=ivar)
        # These do not have to be initied.
        for ivar in ('findPanel',):
            self.assertTrue(hasattr(f, ivar), msg=ivar)
    #@+node:ekr.20210909194526.1: *3* Converted: leoFrame
    #@+node:ekr.20210909194336.44: *3* TestXXX.test_c_frame_body_getInsertLines
    def test_c_frame_body_getInsertLines(self):
        c, w = self.c, self.c.frame.body.wrapper
        s = textwrap.dedent("""\
            line 1
            line 2
            line 3
    """)
        w.setAllText(s)
        index = s.find('2')
        w.setInsertPoint(index)
        before, ins, after = c.frame.body.getInsertLines()
        self.assertEqual(before, 'line 1\n')
        self.assertEqual(ins, 'line 2\n')
        self.assertEqual(after, 'line 3\n')
    #@+node:ekr.20210909194336.45: *3* TestXXX.test_c_frame_body_getSelectionAreas
    def test_c_frame_body_getSelectionAreas(self):
        c = self.c
        # line 1
        # line 2
        # line 3

        w = c.frame.body.wrapper
        s = w.getAllText()
        start, end = 11, 15
        w.setSelectionRange(start, end)
        before, ins, after = c.frame.body.getSelectionAreas()
        assert before == s[0:start], 'Got %s' % repr(before)
        assert ins == s[start:end], 'Got %s' % repr(ins)
        assert after == s[end:]

        # end.
    #@+node:ekr.20210909194336.47: *3* TestXXX.test_c_frame_body_updateEditors
    def test_c_frame_body_updateEditors(self):
        # updateEditors was crashing due to calling setSelectionRange(ins=i).
        # The proper keyword argument is insert=i.
        c = self.c
        c.frame.body.updateEditors()
    #@+node:ekr.20210909194336.49: *3* TestXXX.test_c_frame_tree_OnIconDoubleClick
    def test_c_frame_tree_OnIconDoubleClick(self):
        c = self.c
        c.frame.tree.OnIconDoubleClick(c.p)
    #@-others
#@-others
#@-leo

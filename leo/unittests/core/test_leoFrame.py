#@+leo-ver=5-thin
#@+node:ekr.20210903161742.1: * @file ../unittests/core/test_leoFrame.py
"""Tests of leoFrame.py"""

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
    #@-others
#@-others
#@-leo

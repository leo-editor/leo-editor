# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20210902164946.1: * @file ../unittests/core/test_leoGlobals.py
#@@first
"""Tests for leo.core.leoGlobals"""

from leo.core import leoGlobals as g
from leo.core.leoTest2 import LeoUnitTest

#@+others
#@+node:ekr.20210902165045.1: ** class TestGlobals(LeoUnitTest)
class TestGlobals(LeoUnitTest):
    #@+others
    #@+node:ekr.20210901140645.26: *3* TestGlobals.unicode conversions
    def test_failure_with_ascii_encodings(self):
        encoding = 'ascii'
        s = '炰'
        s2, ok = g.toUnicodeWithErrorCode(s,encoding)
        self.assertTrue(ok)
        s3, ok = g.toEncodedStringWithErrorCode(s,encoding)
        self.assertFalse(ok)
    #@+node:ekr.20210901140645.19: *3* TestGlobals.test_getLastTracebackFileAndLineNumber
    def test_getLastTracebackFileAndLineNumber(self):
        try:
            assert False
        except AssertionError:
            fn, n = g.getLastTracebackFileAndLineNumber()
        self.assertEqual(fn, __file__)
        
    #@-others
#@-others
#@-leo

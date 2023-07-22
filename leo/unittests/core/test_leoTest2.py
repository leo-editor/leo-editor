#@+leo-ver=5-thin
#@+node:ekr.20230722095455.1: * @file ../unittests/core/test_leoTest2.py
"""Tests of leoTest2.py"""

from typing import Any
from leo.core.leoTest2 import LeoUnitTest

#@+others
#@+node:ekr.20230722095704.1: ** class TestTest2(LeoUnitTest)
class TestTest2(LeoUnitTest):
    #@+others
    #@+node:ekr.20230703103514.1: *3* TestTest2.test_set_setting
    def test_set_setting(self) -> None:
        # Not run by default. To run:
        # python -m unittest leo.core.leoTest2.LeoUnitTest.verbose_test_set_setting
        c = self.c
        val: Any
        for val in (True, False):
            name = 'test-bool-setting'
            self._set_setting(c, kind='bool', name=name, val=val)
            self.assertTrue(c.config.getBool(name) == val)
        val = 'aString'
        self._set_setting(c, kind='string', name=name, val=val)
        self.assertTrue(c.config.getString(name) == val)
    #@-others
#@-others
#@-leo

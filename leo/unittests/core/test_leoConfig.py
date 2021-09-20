# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20210910073303.1: * @file ../unittests/core/test_leoConfig.py
#@@first
"""Tests of leoConfig.py"""

from leo.core import leoGlobals as g
from leo.core.leoTest2 import LeoUnitTest

#@+others
#@+node:ekr.20210910073303.2: ** class TestConfig(LeoUnitTest)
class TestConfig(LeoUnitTest):
    """Test cases for leoConfig.py"""
    #@+others
    #@+node:ekr.20210910075848.1: *3* TestConfig.test_g_app_config_and_c_config
    def test_g_app_config_and_c_config(self):
        c = self.c
        assert g.app.config
        assert c.config
    #@+node:ekr.20210909194336.16: *3* TestConfig.test_c_config_printSettings
    def test_c_config_printSettings(self):
        c = self.c
        c.config.printSettings()
    #@+node:ekr.20210909194336.22: *3* TestConfig.test_local_settings_c_page_width_
    def test_local_settings_c_page_width_(self):
        c = self.c
        assert c.page_width
        self.assertEqual(c.page_width, c.config.getInt('page_width'))
    #@-others
#@-others
#@-leo

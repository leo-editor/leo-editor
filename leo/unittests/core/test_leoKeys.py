# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20210903155556.1: * @file ../unittests/core/test_leoKeys.py
#@@first
"""Tests of leoKeys.py"""

from leo.core.leoTest2 import LeoUnitTest

#@+others
#@+node:ekr.20210903155556.2: ** class TestKeys(LeoUnitTest)
class TestKeys(LeoUnitTest):
    """Test cases for leoKeys.py"""
    #@+others
    #@+node:ekr.20210901140645.8: *3* TestKeys.test_k_settings_ivars_match_settings
    def test_k_settings_ivars_match_settings(self):
        c = self.c
        k = c.k
        getBool  = c.config.getBool
        getColor = c.config.getColor
        bg = getColor('body_text_background_color') or 'white'
        fg = getColor('body_text_foreground_color') or 'black'
        table = (
            ('command_mode_bg_color',           getColor('command_mode_bg_color') or bg),
            ('command_mode_fg_color',           getColor('command_mode_fg_color') or fg),
            ('enable_alt_ctrl_bindings',        getBool('enable_alt_ctrl_bindings')),
            ('enable_autocompleter',            getBool('enable_autocompleter_initially')),
            ('enable_calltips',                 getBool('enable_calltips_initially')),
            ('ignore_unbound_non_ascii_keys',   getBool('ignore_unbound_non_ascii_keys')),
            ('insert_mode_bg_color',            getColor('insert_mode_bg_color') or bg),
            ('insert_mode_fg_color',            getColor('insert_mode_fg_color') or fg),
            ('minibuffer_background_color',     getColor('minibuffer_background_color') or 'lightblue'),
            ('minibuffer_error_color',          getColor('minibuffer_error_color') or 'red'),
            ('minibuffer_warning_color',        getColor('minibuffer_warning_color') or 'lightgrey'),
            ('overwrite_mode_bg_color',         getColor('overwrite_mode_bg_color') or bg),
            ('overwrite_mode_fg_color',         getColor('overwrite_mode_fg_color') or fg),
            # ('swap_mac_keys',                 getBool('swap_mac_keys')),
            ('unselected_body_bg_color',        getColor('unselected_body_bg_color') or bg),
            ('unselected_body_fg_color',        getColor('unselected_body_fg_color') or bg),
            ('warn_about_redefined_shortcuts',  getBool('warn_about_redefined_shortcuts')),
        )
        for ivar,setting in table:
            self.assertTrue(hasattr(k, ivar), msg=ivar)
            val = getattr(k, ivar)
            self.assertEqual(val, setting, msg=ivar)
    #@-others
#@-others
#@-leo

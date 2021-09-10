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
    #@+node:ekr.20210910075919.1: *3* if 0: not yet
    if 0:
        #@+others
        #@+node:ekr.20210909194336.17: *4* TestXXX.test_c_config_updateSetting_with_no_settings_node
        def test_c_config_updateSetting_with_no_settings_node(self):
            # Can't be done at top level
            import leo.core.leoConfig as leoConfig
            c = self.c
            p = c.config.settingsRoot()
            if p:
                # p will not exist when run externally.
                h = p.h
                p.h = '@@' + h
            parser = leoConfig.SettingsTreeParser(c, localFlag=True)
            d1, d2 = parser.traverse()
            assert isinstance(d1, g.TypedDict), d1
            assert isinstance(d2, g.TypedDict), d2
        #@+node:ekr.20210909194336.18: *4* TestXXX.test_g_app_config_buttons_and_commands_logic
        def test_g_app_config_buttons_and_commands_logic(self):
            d = g.app.config.unitTestDict # Always created for this unit test.
            keys = ('config.doButtons-file-names', 'config.doCommands-file-names')
            for key in keys:
                aList = d.get(key,[])
                ### if 'leoSettings' not in aList:
                ###    self.skipTest('no settings') # #1345
                for base in ('leoSettings', 'unitTest'):
                    for ext in ('.leo', '.db'):
                        if base + ext in aList:
                            break
                    else:
                        print('key', key, 'ext', ext, 'base', base)
                        g.printObj(aList)
                        self.fail(f"{base} not in unitTestDict[{key}]")
        #@+node:ekr.20210909194336.19: *4* TestXXX.test_g_app_config_get
        def test_g_app_config_get(self):
            w = g.app.config.get('global_setting_for_unit_tests','int')
            assert w in (None, 132) # Will be None when tests run dynamically.
        #@+node:ekr.20210909194336.20: *4* TestXXX.test_g_app_config_set
        def test_g_app_config_set(self):
            c = self.c
            setting = 'import_html_tags'
            html_tags = ('body','head','html','table','xxx')
            # When run externally, c.config.getData will return None.
            existing_tags = c.config.getData(setting)
            if not existing_tags:
                g.app.config.set(None, setting, 'data', html_tags)
                tags = c.config.getData(setting)
                self.assertEqual(tags, html_tags)
        #@+node:ekr.20210909194336.22: *4* TestXXX.test_local_settings_c_page_width_
        def test_local_settings_c_page_width_(self):
            c = self.c
            assert c.page_width == c.config.getInt('page_width'),c.page_width
        #@-others
    #@+node:ekr.20210910075848.1: *3* TestConfig.test_g_app_config_and_c_config
    def test_g_app_config_and_c_config(self):
        c = self.c
        assert g.app.config
        assert c.config
    #@+node:ekr.20210909194336.16: *3* TestXXX.test_c_config_printSettings
    def test_c_config_printSettings(self):
        c = self.c
        c.config.printSettings()
    #@-others
#@-others
#@-leo

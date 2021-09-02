# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20210901170451.1: * @file ../unittests/core/test_leoApp.py
#@@first
"""Tests of leoApp.py"""
from leo.core import leoGlobals as g
from leo.core.leoTest2 import LeoUnitTest
#@+others
#@+node:ekr.20210901170531.1: ** class TestApp(LeoUnitTest)
class TestApp(LeoUnitTest):
    """Test cases for leoApp.py"""
    #@+others
    #@+node:ekr.20210901140645.11: *3* TestApp.test_official_g_app_directories
    def test_official_g_app_directories(self):
        ivars = ('extensionsDir','globalConfigDir','loadDir','testDir')
        for ivar in ivars:
            assert hasattr(g.app,ivar), 'missing g.app directory: %s' % ivar
            val = getattr(g.app,ivar)
            assert val is not None, 'null g.app directory: %s'% ivar
            assert g.os_path_exists(g.os_path_abspath(val)), 'non-existent g.app directory: %s' % ivar
        assert hasattr(g.app, 'homeDir') # May well be None.
    #@+node:ekr.20210901140645.12: *3* TestApp.test_official_g_app_ivars
    def test_official_g_app_ivars(self):
        ivars = (
            # Global managers.
            'config',
            # 'externalFilesController',
            'loadManager','pluginsController','recentFilesManager',
            # Official ivars.
            'gui',
            'initing','killed','quitting',
            'leoID',
            'log','logIsLocked','logWaiting',
            'nodeIndices',
            'unitTesting','unitTestDict',
            'windowList',
            # Less-official and might be removed...
            'batchMode',
            # 'debugSwitch',
            'disableSave',
            'hookError','hookFunction',
            'numberOfUntitledWindows',
            'realMenuNameDict',
            'searchDict','scriptDict',
            'use_psyco',
        )
        for ivar in ivars:
            self.assertTrue(hasattr(g.app, ivar))
            
    #@-others
#@-others
#@-leo

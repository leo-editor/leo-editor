#@+leo-ver=5-thin
#@+node:ekr.20210901170451.1: * @file ../unittests/core/test_leoApp.py
"""Tests of leoApp.py"""
import os
import sys
import zipfile
from leo.core import leoGlobals as g
from leo.core.leoTest2 import LeoUnitTest
#@+others
#@+node:ekr.20210901170531.1: ** class TestApp(LeoUnitTest)
class TestApp(LeoUnitTest):
    """Test cases for leoApp.py"""
    #@+others
    #@+node:ekr.20210901140645.11: *3* TestApp.test_official_g_app_directories
    def test_official_g_app_directories(self):
        ivars = ('extensionsDir', 'globalConfigDir', 'loadDir', 'testDir')
        for ivar in ivars:
            assert hasattr(g.app, ivar), 'missing g.app directory: %s' % ivar
            val = getattr(g.app, ivar)
            assert val is not None, 'null g.app directory: %s' % ivar
            assert g.os_path_exists(g.os_path_abspath(val)), 'non-existent g.app directory: %s' % ivar
        assert hasattr(g.app, 'homeDir')  # May well be None.
    #@+node:ekr.20210901140645.12: *3* TestApp.test_official_g_app_ivars
    def test_official_g_app_ivars(self):
        ivars = (
            # Global managers.
            'config',
            # 'externalFilesController',
            'loadManager', 'pluginsController', 'recentFilesManager',
            # Official ivars.
            'gui',
            'initing', 'killed', 'quitting',
            'leoID',
            'log', 'logIsLocked', 'logWaiting',
            'nodeIndices',
            'windowList',
            # Less-official and might be removed...
            'batchMode',
            # 'debugSwitch',
            'disableSave',
            'hookError', 'hookFunction',
            'numberOfUntitledWindows',
            'realMenuNameDict',
            # 'searchDict',
            'scriptDict',
        )
        for ivar in ivars:
            self.assertTrue(hasattr(g.app, ivar))

    #@+node:ekr.20210909194336.2: *3* TestApp.test_consistency_of_leoApp_tables
    def test_consistency_of_leoApp_tables(self):
        delims_d = g.app.language_delims_dict
        lang_d = g.app.language_extension_dict
        ext_d = g.app.extension_dict
        for lang in lang_d:
            ext = lang_d.get(lang)
            assert lang in delims_d, lang
            assert ext in ext_d, ext
        for ext in ext_d:
            lang = ext_d.get(ext)
            assert lang in lang_d, lang
    #@+node:ekr.20210909194336.3: *3* TestApp.test_lm_openAnyLeoFile
    def test_lm_openAnyLeoFile(self):
        lm = g.app.loadManager
        # Create a zip file for testing.
        s = 'this is a test file'
        testDir = g.os_path_join(g.app.loadDir, '..', 'test')
        assert g.os_path_exists(testDir), testDir
        path = g.finalize_join(testDir, 'testzip.zip')
        if os.path.exists(path):
            os.remove(path)  # pragma: no cover
        f = zipfile.ZipFile(path, 'x')
        assert f, path
        try:
            f.writestr('leo-zip-file', s)
            f.close()
            # Open the file, and get the contents.
            f = lm.openAnyLeoFile(path)
            s2 = f.read()
            f.close()
        finally:
            os.remove(path)
        self.assertEqual(s, s2)
    #@+node:ekr.20210909194336.4: *3* TestApp.test_rfm_writeRecentFilesFileHelper
    def test_rfm_writeRecentFilesFileHelper(self):
        fn = 'ффф.leo'
        g.app.recentFilesManager.writeRecentFilesFileHelper(fn)
        assert g.os_path_exists(fn), fn
        os.remove(fn)
        assert not g.os_path_exists(fn), fn
    #@+node:ekr.20230617065356.1: *3* TestApp.test_LM_scanOptions
    def test_LM_scanOptions(self):

        bad_table = (
            '-h', '--help',
            '--gui', '--gui=xxx',
            '--listen-to-log=',
            '--load-type=@auto', '--load-type=@clean',
            '--screen-shot', '--screen-shot=', '--screen-shot-',
            '--screen-shot=xyzzy',
            '--script=xyzzy.py',
            '--trace','--trace-', 'trace=', '--trace=xxx',
            '--trace-binding', '--trace-binding-', '--trace-binding=',
            '--window-', 'window=',
            '--window-size', '--window-size=', '--window-size=100',
            '--window-spot', '--window-spot=', '--window-spot=50',
            '--yyy',
        )
        good_table = (
            '-b', '--black-sentinels',
            '--diff',
            '--fail-fast',
            '--fullscreen',
            '--gui=console', '--gui=curses', '--gui=null', '--gui=qt', '--gui=text',
            '--ipython',
            '--listen-to-log',
            '--load-type=@edit', '--load-type=@file',
            '--maximized', '--minimized',
            '--no-plugins', '--no-splash',
            '--quit',
            '--script-window',
            '--select=whatever',
            '--silent',
            '--theme=whatever',
            '--trace-binding=whatever',
            '--trace-setting=whatever',
            '--trace=coloring',
            '-v', '--version',
            '--window-size=100x200',
            '--window-spot=50x60',
        )
        scan = g.app.loadManager.scanOptions

        # Careful. Restore sys.argv and sys.stdout.
        old_argv = sys.argv
        old_stdout = sys.stdout
        try:
            sys.stdout = open(os.devnull, 'w')
            for option in good_table:
                sys.argv = ['leo', option]
                scan(None, False)
            for option in bad_table:
                with self.assertRaises(SystemExit, msg=option):
                    sys.argv = ['leo', option]
                    scan(None, False)
        finally:
            sys.argv = old_argv
            sys.stdout = old_stdout
    #@-others
#@-others
#@-leo

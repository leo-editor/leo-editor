#@+leo-ver=5-thin
#@+node:ekr.20240208055858.1: * @file ../unittests/modes/test_nim.py
"""Tests of leo/modes/nim.py"""
from leo.core import leoGlobals as g
from leo.core.leoTest2 import LeoUnitTest
#@+others
#@+node:ekr.20240208055858.2: ** class TestNim(LeoUnitTest)
class TestNim(LeoUnitTest):
    """Test cases for modes/nim.py"""
    #@+others
    #@+node:ekr.20240208055858.3: *3* TestNim.test_nim
    def test_official_g_app_directories(self):
        ivars = ('extensionsDir', 'globalConfigDir', 'loadDir', 'testDir')
        for ivar in ivars:
            assert hasattr(g.app, ivar), 'missing g.app directory: %s' % ivar
            val = getattr(g.app, ivar)
            assert val is not None, 'null g.app directory: %s' % ivar
            assert g.os_path_exists(g.os_path_abspath(val)), 'non-existent g.app directory: %s' % ivar
        assert hasattr(g.app, 'homeDir')  # May well be None.
    #@-others
#@-others
#@-leo

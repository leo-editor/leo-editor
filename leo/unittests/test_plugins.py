# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20210907081548.1: * @file ../unittests/test_plugins.py
#@@first
"""General tests of plugins."""

import glob
import re
from leo.core import leoGlobals as g
from leo.core.leoTest2 import LeoUnitTest
assert g

#@+others
#@+node:ekr.20210907082556.1: ** class TestPlugins(LeoUnitTest)
class TestPlugins(LeoUnitTest):
    """General tests of plugoins."""
    #@+others
    #@+node:ekr.20210907082746.1: *3* TestPlugins.get_plugins
    def get_plugins(self):
        """Return a list of all plugins *without* importing them."""
        excludes = (
            # These are not real plugins...
            'babel_api.py',
            'babel_kill.py',
            'babel_lib.py',
            'baseNativeTree.py',
            'leocursor.py',
            'leo_cloud_server.py',
            'leo_mypy_plugin.py',
            'nested_splitter.py',
            'qtGui.py',
            'qt_gui.py',
            'qt_big_text.py',
            'qt_commands.py',
            'qt_events.py',
            'qt_frame.py',
            'qt_idle_time.py',
            'qt_main.py',
            'qt_quickheadlines.py',
            'qt_quicksearch_sub.py',
            'qt_text.py',
            'qt_tree.py',
            'qt_quicksearch.py',
            'swing_gui.py',
        )
        plugins = g.os_path_join(g.app.loadDir,'..','plugins','*.py')
        plugins = g.os_path_abspath(plugins)
        files = glob.glob(plugins)
        files = [z for z in files if not z.endswith('__init__.py')]
        files = [z for z in files if g.shortFileName(z) not in excludes]
        files = [g.os_path_abspath(z) for z in files]
        return sorted(files)
    #@+node:ekr.20210907081455.2: *3* TestPlugins.test_all_plugins_have_top_level_init_method
    def test_all_plugins_have_top_level_init_method(self):
        # Ensure all plugins have top-level init method *without* importing them.
        files = self.get_plugins()
        for fn in files:
            with open(fn,'r') as f:
                s = f.read()
            self.assertTrue('def init():' in s or 'def init ():' in s, msg=fn)
    #@+node:ekr.20210907081455.3: *3* TestPlugins.test_all_qt_plugins_call_g_assertUi_qt_
    def test_all_qt_plugins_call_g_assertUi_qt_(self):
        files = self.get_plugins()
        excludes = (
            # Special cases, handling Qt imports in unusual ways.
            'backlink.py',  # Qt code is optional, disabled with module-level guard.
            'leoscreen.py',  # Qt imports are optional.
            'nodetags.py',  # #2031: Qt imports are optional.
            'pyplot_backend.py',
            # 'free_layout.py',
        )
        pattern = re.compile(r'\b(QtCore|QtGui|QtWidgets)\b') # Don't search for Qt.
        for fn in files:
            if g.shortFileName(fn) in excludes:
                continue
            with open(fn, 'r') as f:
                s = f.read()
            if not re.search(pattern, s):
                continue
            self.assertTrue(re.search(r"g\.assertUi\(['\"]qt['\"]\)", s), msg=fn)
    #@-others
#@-others
#@-leo

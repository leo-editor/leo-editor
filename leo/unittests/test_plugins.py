#@+leo-ver=5-thin
#@+node:ekr.20210907081548.1: * @file ../unittests/test_plugins.py
"""General tests of plugins."""

import glob
import re
from leo.core import leoGlobals as g
from leo.core.leoTest2 import LeoUnitTest
from leo.core.leoPlugins import LeoPluginsController
assert g

#@+others
#@+node:ekr.20210907082556.1: ** class TestPlugins(LeoUnitTest)
class TestPlugins(LeoUnitTest):
    """General tests of plugoins."""
    #@+others
    #@+node:ekr.20210909165100.1: *3*  TestPlugin.check_syntax
    def check_syntax(self, filename):  # pylint: disable=inconsistent-return-statements
        with open(filename, 'r') as f:
            s = f.read()
        try:
            s = s.replace('\r', '')
            tree = compile(s + '\n', filename, 'exec')
            del tree  # #1454: Suppress -Wd ResourceWarning.
            return True
        except SyntaxError:  # pragma: no cover
            raise
        except Exception:  # pragma: no cover
            self.fail(f"unexpected error in: {filename}")

    #@+node:ekr.20210907082746.1: *3*  TestPlugins.get_plugins
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
            # Experimental.
            'leo_pdf.py',
        )
        plugins = g.os_path_join(g.app.loadDir, '..', 'plugins', '*.py')
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
            with open(fn, 'r') as f:
                s = f.read()
            self.assertTrue('def init()' in s or 'def init ()' in s, msg=fn)
    #@+node:ekr.20210907081455.3: *3* TestPlugins.test_all_qt_plugins_call_g_assertUi_qt_
    def test_all_qt_plugins_call_g_assertUi_qt_(self):
        files = self.get_plugins()
        excludes = (
            # Special cases, handling Qt imports in unusual ways.
            'backlink.py',  # Qt code is optional, disabled with module-level guard.
            'leoscreen.py',  # Qt imports are optional.
            'nodetags.py',  # #2031: Qt imports are optional.
            'pyplot_backend.py',  # Not a real plugin.
        )
        pattern = re.compile(r'\b(QtCore|QtGui|QtWidgets)\b')  # Don't search for Qt.
        for fn in files:
            if g.shortFileName(fn) in excludes:
                continue
            with open(fn, 'r') as f:
                s = f.read()
            if not re.search(pattern, s):
                continue
            self.assertTrue(re.search(r"g\.assertUi\(['\"]qt['\"]\)", s), msg=fn)
    #@+node:ekr.20210909161328.2: *3* TestPlugins.test_c_vnode2position
    def test_c_vnode2position(self):
        c = self.c
        for p in c.all_positions():
            p2 = c.vnode2position(p.v)
            # We can *not* assert that p == p2!
            assert p2
            self.assertEqual(p2.v, p.v)
            assert c.positionExists(p2), 'does not exist: %s' % p2
    #@+node:ekr.20221219090253.1: *3* TestPlugins.test_cursesGui2
    def test_cursesGui2(self):

        # New unit test for #3008
        # https://github.com/leo-editor/leo-editor/issues/3008

        # #3017: Skip the test if npyscreen, curses (_curses) or tkinter are missing.
        try:
            import leo.plugins.cursesGui2 as cursesGui2
        except Exception:
            self.skipTest('Missing cursesGui2 requirements')

        # Instantiating this class caused the crash.
        cursesGui2.LeoTreeData()
    #@+node:ekr.20210909194336.57: *3* TestPlugins.test_regularizeName
    def test_regularizeName(self):
        pc = LeoPluginsController()
        table = (
            ('x', 'x'),
            ('foo.bar', 'foo.bar'),
            ('x.py', 'leo.plugins.x'),
            ('leo.plugins.x', 'leo.plugins.x')
        )
        for fn, expected in table:
            result = pc.regularizeName(fn)
            self.assertEqual(result, expected, msg=fn)
            # Make sure that calling regularizeName twice is benign.
            result2 = pc.regularizeName(result)
            assert result2 == result
    #@+node:ekr.20210909161328.4: *3* TestPlugins.test_syntax_of_all_plugins
    def test_syntax_of_all_plugins(self):
        files = self.get_plugins()
        for filename in files:
            self.check_syntax(filename)
    #@+node:ekr.20210909165720.1: *3* TestPlugins.xx_test_import_all_plugins
    def xx_test_import_of_all_plugins(self):  # pragma: no cover
        # This works, but is slow.
        files = self.get_plugins()
        for filename in files:
            plugin_module = g.shortFileName(filename)[:-3]
            try:
                exec(f"import leo.plugins.{plugin_module}")
            except g.UiTypeException:
                pass
            except AttributeError:
                pass
            except ImportError:
                pass
    #@-others
#@-others
#@-leo

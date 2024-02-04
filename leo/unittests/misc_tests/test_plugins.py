#@+leo-ver=5-thin
#@+node:ekr.20210907081548.1: * @file ../unittests/test_plugins.py
"""General tests of plugins."""

import glob
import os
import re
import textwrap
from leo.core import leoGlobals as g
from leo.core.leoTest2 import LeoUnitTest
from leo.core.leoPlugins import LeoPluginsController
from leo.plugins import indented_languages

#@+others
#@+node:ekr.20210907082556.1: ** class TestPlugins(LeoUnitTest)
class TestPlugins(LeoUnitTest):
    """General tests of plugins."""
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
            assert 'def init()' in s, repr(fn)
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
    #@+node:ekr.20210909165720.1: *3* TestPlugins.slow_test_import_all_plugins
    def slow_test_import_of_all_plugins(self):  # pragma: no cover
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
#@+node:ekr.20230917015008.1: ** class TestIndentedTypescript(LeoUnitTest)
class TestIndentedTypeScript(LeoUnitTest):
    """Tests for typescript-related code in the indented_languages plugin."""

    #@+others
    #@+node:ekr.20230919025755.1: *3* test_its.test_typescript
    def test_typescript(self):

        c, p = self.c, self.c.p

        #@+<< define contents: test_typescript >>
        #@+node:ekr.20231022133716.1: *4* << define contents: test_typescript >>
        # Snippets from indented_typescript_test.ts.

        # Contains "over-indented" parenthesized lines, a good test for check_indentation.

        contents = textwrap.dedent(  # dedent is required.
            """
            import { NodeIndices, VNode, Position } from './leoNodes';

            export class Config implements ConfigMembers {

            constructor(
                private _context: vscode.ExtensionContext,
                private _leoUI: LeoUI
            ) { }

            const w_config: FontSettings = {
                zoomLevel: Number(w_zoomLevel),
                fontSize: Number(w_fontSize)
            };

            public getFontConfig(): FontSettings {
                let w_zoomLevel = vscode.workspace.getConfiguration(
                    "window"
                ).get("zoomLevel");

                return w_config;
            }

            public getEncodingFromHeader(fileName: string, s: string): BufferEncoding {
                if (at.errors) {
                    if (g.unitTesting) {
                        console.assert(false, g.callers());
                    }
                } else {
                    at.initReadLine(s);
                }
            }
            }
            """)
        #@-<< define contents: test_typescript >>

        # Set p.h and p.b.
        unittest_dir = os.path.dirname(__file__)
        path = os.path.abspath(os.path.join(unittest_dir, 'indented_typescript_test.ts'))
        assert os.path.exists(path), repr(path)
        p.h = f"@file {path}"
        p.b = contents

        # Import.
        x = indented_languages.Indented_TypeScript(c)
        top_node = x.do_import()
        assert top_node.h == 'indented files', repr(top_node.h)

        # Debugging.
        if 0:
            for z in self.c.all_positions():
                print(f"{' '*z.level()} {z.h}")
        if 0:
            root = top_node.firstChild()
            g.printObj(g.splitLines(root.b), tag=root.h)

    #@-others
#@+node:ekr.20231025174626.1: ** class TestIndentedLisp(LeoUnitTest)
class TestIndentedLisp(LeoUnitTest):
    """Tests for lisp-related code in the indented_languages plugin."""

    #@+others
    #@+node:ekr.20231025174704.1: *3* test_ilisp.test_lisp_reduce_fraction
    def test_lisp_reduce_fraction(self):

        c, p = self.c, self.c.p
        contents = """
            (defun test (a)
                (+ 1 (* 2 a))
                (= 0 (% (cadr result) divisor))
            )

            (defun reduce-fraction (f divisor)
                "Eliminates divisor from fraction if present"
                (while (and (= 0 (% (car result) divisor))
                     (= 0 (% (cadr result) divisor))
                     (< 1 (cadr result))
                     (< 0 (car result)))
                (setq result (list (/ (car result) divisor) (/ (cadr result) divisor))))
                result
            )
        """

        # Setup.
        p.h = '@@file reduce_fraction.el'
        p.b = contents

        # Import.
        x = indented_languages.Indented_Lisp(c)
        top_node = x.do_import()
        assert top_node.h == 'indented files', repr(top_node.h)
        p = top_node.firstChild()
        if 0:
            print(contents)
            print('')
            print(p.b)
    #@-others
#@-others
#@-leo

# @+leo-ver=5-thin
# @+node:ekr.20210903153138.1: * @file ../unittests/core/test_leoBridge.py
"""Tests of leoBridge.py"""

import os
import subprocess
import sys
import textwrap
from leo.core import leoBridge
from leo.core.leoTest2 import LeoUnitTest


# @+others
# @+node:ekr.20210903153138.2: ** class TestBridge(LeoUnitTest)
class TestBridge(LeoUnitTest):
    """Test cases for leoBridge.py"""

    # @+others
    # @+node:ekr.20210903153548.1: *3* TestBridge.test_bridge
    def test_bridge(self):
        # The most basic test.
        controller = leoBridge.controller(
            gui='nullGui',  # 'nullGui', 'qt'
            loadPlugins=False,  # True: attempt to load plugins.,
            readSettings=False,  # True: read standard settings files.
            silent=True,  # True: don't print signon messages.
            verbose=True,
        )
        g = controller.globals()
        self.assertTrue(g)
        unittest_dir = os.path.abspath(os.path.dirname(__file__))
        self.assertTrue(os.path.exists(unittest_dir))
        test_dot_leo = g.finalize_join(unittest_dir, '..', '..', 'test', 'test.leo')
        self.assertTrue(os.path.exists(test_dot_leo), msg=test_dot_leo)
        c = controller.openLeoFile(test_dot_leo)
        self.assertTrue(c)

    def test_null_bridge_does_not_import_qt(self):
        """The null bridge must work when PyQt6 is not installed."""
        repo_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        test_dot_leo = os.path.join(repo_dir, 'leo', 'test', 'test.leo')
        script = textwrap.dedent(
            f"""
            import importlib.abc
            import sys

            class BlockPyQt(importlib.abc.MetaPathFinder):
                def find_spec(self, fullname, path=None, target=None):
                    if fullname == 'PyQt6' or fullname.startswith('PyQt6.'):
                        raise ImportError(f'Unexpected Qt import: {{fullname}}')
                    return None

            sys.meta_path.insert(0, BlockPyQt())

            from leo.core import leoBridge

            bridge = leoBridge.controller(
                gui='nullGui',
                loadPlugins=False,
                readSettings=False,
                silent=True,
                useCaches=False,
            )
            assert bridge.isOpen()
            assert bridge.globals().app.gui.guiName() == 'nullGui'
            c = bridge.openLeoFile({test_dot_leo!r})
            assert c
            assert not any(
                name == 'PyQt6' or name.startswith('PyQt6.')
                for name in sys.modules
            )
            assert not any(name.startswith('leo.plugins.qt_') for name in sys.modules)
            """
        )
        result = subprocess.run(
            [sys.executable, '-c', script],
            cwd=repo_dir,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    # @-others


# @-others
# @-leo

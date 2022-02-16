# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20210901140718.1: * @file ../unittests/test_syntax.py
#@@first
"""Syntax tests, including a check that Leo will continue to load!"""
# pylint: disable=no-member
import glob
from leo.core import leoGlobals as g
from leo.core.leoTest2 import LeoUnitTest
#@+others
#@+node:ekr.20210901140855.1: ** class TestSyntax(LeoUnitTest)
class TestSyntax(LeoUnitTest):
    """Unit tests checking syntax of Leo files."""
    #@+others
    #@+node:ekr.20210901140645.1: *3* TestSyntax.tests...
    #@+node:ekr.20210910102910.1: *4* TestSyntax.check_syntax
    def check_syntax(self, fileName, s):
        """Called by a unit test to check the syntax of a file."""
        try:
            s = s.replace('\r', '')
            tree = compile(s + '\n', fileName, 'exec')
            del tree  # #1454: Suppress -Wd ResourceWarning.
            return True
        except SyntaxError:
            raise SyntaxError(fileName)  # pylint: disable=raise-missing-from
        except Exception:
            g.trace("unexpected error in:", fileName)
            raise
    #@+node:ekr.20210901140645.21: *4* TestSyntax.test_syntax_of_all_files
    def test_syntax_of_all_files(self):
        skip_tuples = (
            ('extensions', 'asciidoc.py'),
            ('test', 'scriptFile.py'),
        )
        join = g.os_path_finalize_join
        skip_list = [join(g.app.loadDir, '..', a, b) for a, b in skip_tuples]
        n = 0
        for theDir in ('core', 'external', 'extensions', 'modes', 'plugins', 'scripts', 'test'):
            path = g.os_path_finalize_join(g.app.loadDir, '..', theDir)
            self.assertTrue(g.os_path_exists(path), msg=path)
            aList = glob.glob(g.os_path_join(path, '*.py'))
            if g.isWindows:
                aList = [z.replace('\\', '/') for z in aList]
            for z in aList:
                if z not in skip_list:
                    n += 1
                    fn = g.shortFileName(z)
                    s, e = g.readFileIntoString(z)
                    self.assertTrue(self.check_syntax(fn, s), msg=fn)
    #@+node:ekr.20210901140645.22: *4* TestSyntax.test_syntax_of_setup_py
    def test_syntax_of_setup_py(self):
        fn = g.os_path_finalize_join(g.app.loadDir, '..', '..', 'setup.py')
        # Only run this test if setup.py exists: it may not in the actual distribution.
        if not g.os_path_exists(fn):
            self.skipTest('setup.py not found')
        s, e = g.readFileIntoString(fn)
        assert self.check_syntax(fn, s)
    #@+node:ekr.20210906062410.1: *4* TestSyntax.test_that_leo_starts
    def test_that_leo_starts(self):
        return self.skipTest('forbidden')
        # It's possible that Leo can be corrupted without this test failing.
        # However, the risk seems small enough!
        if 1:
            # Verify (weakly) that Leo's startup logic doesn't crash.
            # Similar (but not exactly so) the startup code in runLeo.py
            import importlib
            import leo.core.leoApp as leoApp
            # It's not clear that the reloads improve the test.
            importlib.reload(g)
            importlib.reload(leoApp)
            assert g
            assert leoApp
            app = leoApp.LeoApp()
            lm = leoApp.LoadManager()
            assert app and lm
        else:
            # Run Leo in a separate process.
            # Alas, this can leave files open in g.app.db,
            # and it's not easy here to do anything about it
            import subprocess
            command = 'leo --quit --gui=null --no-plugins'
            proc = subprocess.Popen(
                command,
                stdout=subprocess.DEVNULL,
                shell=True)
            proc.communicate()
    #@-others
#@-others
#@-leo

#@+leo-ver=5-thin
#@+node:ekr.20210901140718.1: * @file ../unittests/misc_tests/test_syntax.py
"""Syntax tests, including a check that Leo will continue to load!"""
import importlib
import glob
import os
import re
from typing import Any

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
        except SyntaxError:  # pragma: no cover
            raise SyntaxError(fileName)  # pylint: disable=raise-missing-from
        except Exception:  # pragma: no cover
            g.trace("unexpected error in:", fileName)
            raise
    #@+node:ekr.20210901140645.21: *4* TestSyntax.test_syntax_of_all_files
    def test_syntax_of_all_files(self):
        skip_tuples = (
            ('extensions', 'asciidoc.py'),
            ('test', 'scriptFile.py'),
        )
        join = g.finalize_join
        skip_list = [join(g.app.loadDir, '..', a, b) for a, b in skip_tuples]
        n = 0
        for theDir in ('core', 'external', 'extensions', 'modes', 'plugins', 'scripts', 'test'):
            path = g.finalize_join(g.app.loadDir, '..', theDir)
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
    #@+node:ekr.20241118022857.1: *4* TestSyntax.test_all_mode_files
    def test_all_mode_files(self):

        tag = 'slow_test_all_mode_files'

        #@+others  # Define test_one_mode_file
        #@+node:ekr.20241118025715.1: *5* function: test_one_mode_file
        def test_one_mode_file(module: Any) -> None:
            """Call all rules in the given module, a mode file."""
            from leo.core.leoColorizer import JEditColorizer
            c = self.c
            module_name = module.__name__
            # Skip modes/plain.py. It has only one rule and the rulesDict is a hack.
            if module_name.endswith('plain'):
                return
            colorer = JEditColorizer(c, widget=None)
            rules = []
            for ruleDict_name, ruleDict in module.rulesDictDict.items():
                # The colorizer adds Leo-specific rules to these dicts. Don't call them!
                for char, rules_list in ruleDict.items():
                    for rule in rules_list:
                        if not rule.__name__.startswith('match_'):
                            rules.append(rule)
            rules = sorted(list(set(rules)), key=lambda z: z.__name__)
            # g.printObj([z.__name__ for z in rules], tag=f"Rules for {module_name}")
            i = 0
            s = 'def spam()'
            for rule in rules:
                rule(colorer, s, i)
        #@-others

        mode_path = g.os_path_finalize_join(g.app.loadDir, '..', 'modes')
        paths = glob.glob(f"{mode_path}{os.sep}*.py")
        paths = [os.path.basename(z)[:-3] for z in paths]
        paths = [z for z in paths if not z.startswith('__')]
        for path in paths:
            try:
                module = importlib.import_module(f"leo.modes.{path}")
                test_one_mode_file(module)
            except Exception:
                raise AssertionError(f"{tag}:Test failed: {module.__name__}")
    #@-others
#@-others
#@-leo

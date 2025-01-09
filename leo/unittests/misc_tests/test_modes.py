#@+leo-ver=5-thin
#@+node:ekr.20250109055422.1: * @file ../unittests/misc_tests/test_modes.py
"""Tests of files in leo/modes"""
import importlib
import glob
import os
import string
from typing import Any

from leo.core import leoGlobals as g
from leo.core.leoColorizer import JEditColorizer
from leo.core.leoTest2 import LeoUnitTest
#@+others
#@+node:ekr.20250109055422.2: ** class TestModes(LeoUnitTest)
class TestModes(LeoUnitTest):
    """Unit tests checking files in leo/modes."""
    #@+others
    #@+node:ekr.20250109055422.3: *3* TestModes.tests...
    #@+node:ekr.20241118022857.1: *4* TestModes.test_all_mode_files
    def test_all_mode_files(self):

        tag = 'test_all_mode_files'

        #@+others  # Define test_one_mode_file
        #@+node:ekr.20241118025715.1: *5* function: test_one_mode_file
        def test_one_mode_file(module: Any) -> None:
            """Call all rules in the given module, a mode file."""
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

        fails = []
        mode_path = g.os_path_finalize_join(g.app.loadDir, '..', 'modes')
        paths = glob.glob(f"{mode_path}{os.sep}*.py")
        paths = [os.path.basename(z)[:-3] for z in paths]
        paths = [z for z in paths if not z.startswith('__')]
        for path in paths:
            try:
                module = importlib.import_module(f"leo.modes.{path}")
                test_one_mode_file(module)
            except Exception as e:
                # raise AssertionError(f"{tag}:Test failed: {module.__name__}")
                g.trace(repr(e))
                fails.append(f"{module.__name__:<20} {e!r}")
        if fails:
            fails_s = '\n'.join(fails)
            message = f"\n{tag}:Test failed:...\n{fails_s}\n"
            raise AssertionError(message)

    #@+node:ekr.20250109055901.1: *4* TestModes.test_rules_dicts
    def test_rules_dicts(self):

        tag = 'test_rules_dicts'

        #@+others  # Define test_rules_dict
        #@+node:ekr.20250109060045.1: *5* function: test_rules_dict
        def test_rules_dict(language: str, path: str) -> None:
            """Call all rules in the given module, a mode file."""
            c = self.c

            # Init the mode.
            colorer = JEditColorizer(c, widget=None)
            colorer.init_mode(language)

            # Remove [0-9] from colorer.word_chars.
            word1_chars = set(colorer.word_chars) - set(string.digits)

            # Test that all characters that can start a word are in the rules dict.
            module = importlib.import_module(f"leo.modes.{language}")
            d = module.rulesDict1
            for key in word1_chars:
                assert key in d, f"Missing key in {language}.rulesDict1: {key!r}"
        #@-others

        mode_path = g.os_path_finalize_join(g.app.loadDir, '..', 'modes')
        for language in ('python', 'rust'):
            mode_path = os.path.normpath(f"{mode_path}{os.sep}{language}.py")
            test_rules_dict(language, mode_path)
    #@-others
#@-others
#@-leo

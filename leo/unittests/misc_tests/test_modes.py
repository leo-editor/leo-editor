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

        # tag = 'test_rules_dicts'

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
    #@+node:ekr.20250114101209.1: *4* TestModes.test_rust_character_patterns
    def test_rust_character_patterns(self):

        from leo.modes.rust import rust_char

        class TestColorizer:

            def match_seq(self, s: str, i: int, kind: str, seq: str):
                return kind, seq

        colorer = TestColorizer()

        char_table = (
            # Characters, length 10.
            r"'\u{7fff}'",
            r"'\u{0aaa}'",
            r"'\u{1bbb}'",
            r"'\u{2ccc}'",
            r"'\u{3ddd}'",
            r"'\u{4eee}'",
            r"'\u{5fff}'",
            r"'\u{6abc}'",
            # Characters, length 8.
            r"'\x00'",
            r"'\x12'",
            r"'\x3a'",
            r"'\x3b'",
            r"'\x4c'",
            r"'\x5d'",
            r"'\x6e'",
            r"'\x7f'",
            # Characters, length 4.
            r"'\n'",
            r"'\0'",
            r"'\t'",
            r"'\r'",
            r"'\\'",
            # Characters, length 3.
            r"'x'",
            r"'é'",
        )
        for s in char_table:
            kind, seq = rust_char(colorer, s, i=0)
            assert kind == 'literal1', (kind, s)
            assert seq == s, (kind, seq, s)

        # Lifetimes.
        lifetime_table = (
            ("'a", "'a"),
            ("'a>", "'a"),
            ("'a ", "'a"),
            ("'static", "'static"),
            ("'static\n", "'static"),
            ("'static ", "'static"),
        )
        for s, expected_seq in lifetime_table:
            kind, seq = rust_char(colorer, s, i=0)
            assert kind == 'literal1', kind
            assert seq == expected_seq, (seq, expected_seq)

        # Errors.
        error_table = (
            "'xx",  # Bad lifetime.
            "'BSBSy'".replace('BS', '\\'),  # Too long.
            "'BSy'".replace('BS', '\\'),  # Invalid escape: \y
            r"'\u{ffff}'",  # Must begin with [0-7]
            r"'\xff'",  # Must begin with [0-7]
            r"'\u{7fhi}'",  # Invalid hex digits.
        )
        for s  in error_table:
            kind, seq = rust_char(colorer, s, i=0)
            assert kind == 'literal4', kind
            assert seq == "'", repr(seq)
    #@+node:ekr.20250123084454.1: *4* TestModes.test_c_label
    def test_c_label(self):

        from leo.modes.c import c_keyword

        c = self.c
        jedit_colorer = JEditColorizer(c=c, widget=None)

        actual_seq: str
        actual_kind: str

        class TestColorizer:

            def match_keywords(self, s: str, i: int):
                return jedit_colorer.match_keywords(s, i)

            def match_seq(self, s: str, i: int, kind: str, seq: str):
                nonlocal actual_kind, actual_seq
                actual_kind, actual_seq = kind, seq
                return jedit_colorer.match_seq(s, i, kind=kind, seq=seq)

        test_colorer = TestColorizer()

        line_table = (
            (-4, '', '', 'goto label;\n'),
            (6, 'label', 'label:', 'label:\n'),
        )
        for expected_n, expected_kind, expected_seq, s in line_table:
            actual_kind, actual_seq = '', ''
            n = c_keyword(test_colorer, s, 0)
            assert n == expected_n, (expected_n, n, s)
            assert expected_kind == actual_kind, (expected_kind, actual_kind, s)
            assert expected_seq == actual_seq, (expected_seq, actual_seq, s)
    #@-others
#@-others
#@-leo

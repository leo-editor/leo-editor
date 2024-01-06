#@+leo-ver=5-thin
#@+node:ekr.20240105151507.1: * @file ../unittests/core/test_leoTokens.py
"""Tests of leoTokens.py"""
#@+<< test_leoTokens imports >>
#@+node:ekr.20240105151507.2: ** << test_leoTokens imports >>
import os
import sys
import textwrap
import time
import unittest
import warnings

# pylint: disable=wrong-import-position

# warnings.simplefilter("ignore")
try:
    # Suppress a warning about imp being deprecated.
    with warnings.catch_warnings():
        import black
except Exception:  # pragma: no cover
    black = None

from leo.core import leoGlobals as g
from leo.core.leoTokens import TokenBasedOrange
from leo.core.leoTokens import InputToken, Tokenizer
from leo.core.leoTokens import get_encoding_directive, read_file, strip_BOM
from leo.core.leoTokens import make_tokens, tokens_to_string
from leo.core.leoTokens import dump_contents, dump_tokens
#@-<< test_leoTokens imports >>
v1, v2, junk1, junk2, junk3 = sys.version_info
py_version = (v1, v2)

#@+others
#@+node:ekr.20240105153229.3: ** functions: unit testing
#@+node:ekr.20240105153229.7: *3* function: compare_lists
def compare_lists(list1, list2):  # pragma: no cover
    """
    Compare two lists of strings, showing the first mismatch.

    Return the index of the first mismatched lines, or None if identical.
    """
    import itertools
    it = itertools.zip_longest(list1, list2, fillvalue='Missing!')
    for i, (s1, s2) in enumerate(it):
        if s1 != s2:
            return i
    return None
#@+node:ekr.20240105153229.8: *3* function: get_time
def get_time():
    return time.process_time()
#@+node:ekr.20240105153420.2: ** class BaseTest (TestCase)
class BaseTest(unittest.TestCase):
    """
    The base class of all tests of leoAst.py.

    This class contains only helpers.
    """

    # Statistics.
    counts: dict[str, int] = {}
    times: dict[str, float] = {}

    # Debugging traces & behavior.
    debug_list: list[str] = []
    link_error: Exception = None

    #@+others
    #@+node:ekr.20240105153420.3: *3* BaseTest.adjust_expected
    def adjust_expected(self, s):
        """Adjust leading indentation in the expected string s."""
        return textwrap.dedent(s.lstrip('\\\n')).rstrip() + '\n'
    #@+node:ekr.20240105153420.13: *3* BaseTest.beautify
    def beautify(self,
        contents,
        tokens,
        filename=None,
        max_join_line_length=None,
        max_split_line_length=None,
    ):
        """
        BaseTest.beautify.
        """
        t1 = get_time()
        if not contents:
            return ''  # pragma: no cover
        if not filename:
            filename = g.callers(2).split(',')[0]
        orange = TokenBasedOrange()
        result_s = orange.beautify(contents, filename, tokens,
            max_join_line_length=max_join_line_length,
            max_split_line_length=max_split_line_length)
        t2 = get_time()
        self.update_times('22: beautify', t2 - t1)
        self.code_list = orange.code_list
        return result_s
    #@+node:ekr.20240105153420.4: *3* BaseTest.check_roundtrip
    def check_roundtrip(self, contents, *, debug_list: list[str] = None):
        """Check that the tokenizer round-trips the given contents."""
        contents, tokens = self.make_data(contents, debug_list=debug_list)
        results = tokens_to_string(tokens)
        self.assertEqual(contents, results)
    #@+node:ekr.20240105153425.44: *3* BaseTest.make_data
    def make_data(self,
        contents: str,
        *,
        description: str = None,
        debug_list: str = None,
    ) -> tuple[str, list[InputToken]]:  # pragma: no cover
        """
        BaseTest.make_data:

        Return (contents, tokens) for the given contents.
        """
        contents = contents.lstrip('\\\n')
        assert contents.strip(), g.callers()

        # Set debug flags and counts.
        self.debug_list = debug_list or []
        self.trace_token_method = False
        self.update_counts('characters', len(contents))

        # Check the debug_list.
        valid = ('contents', 'debug', 'tokens')
        for z in self.debug_list:
            if z not in valid:
                g.trace('Ignoring debug_list value:', z)

        # Ensure all tests start with a non-blank line and end in exactly one newline.
        contents = textwrap.dedent(contents).strip() + '\n'

        # Create the tokens.
        tokens = Tokenizer().make_tokens(contents)
        if not tokens:
            self.fail('TestOrange.make_tokens failed')

        # Dumps.
        if 'contents' in self.debug_list:
            dump_contents(contents)
        if 'tokens' in self.debug_list:
            dump_tokens(tokens)
        return contents, tokens
    #@+node:ekr.20240105153420.6: *3* BaseTest.make_file_data
    def make_file_data(self, filename: str) -> tuple[str, list[InputToken]]:
        """Return (contents, tokens, tree) from the given file."""
        directory = os.path.dirname(__file__)
        filename = g.finalize_join(directory, '..', '..', 'core', filename)
        assert os.path.exists(filename), repr(filename)
        contents = read_file(filename)
        contents, tokens = self.make_data(contents, description=filename)
        return contents, tokens
    #@+node:ekr.20240105153420.8: *3* BaseTest.make_tokens
    def make_tokens(self, contents):
        """
        BaseTest.make_tokens.

        Make tokens from contents.
        """
        t1 = get_time()
        # Tokenize.
        tokens = make_tokens(contents)
        t2 = get_time()
        self.update_counts('tokens', len(tokens))
        self.update_times('01: make-tokens', t2 - t1)
        return tokens
    #@+node:ekr.20240105153420.14: *3* BaseTest: stats...
    # Actions should fail by throwing an exception.
    #@+node:ekr.20240105153420.15: *4* BaseTest.dump_stats & helpers
    def dump_stats(self):  # pragma: no cover
        """Show all calculated statistics."""
        if self.counts or self.times:
            print('')
            self.dump_counts()
            self.dump_times()
            print('')
    #@+node:ekr.20240105153420.16: *5* BaseTest.dump_counts
    def dump_counts(self):  # pragma: no cover
        """Show all calculated counts."""
        for key, n in self.counts.items():
            print(f"{key:>16}: {n:>6}")
    #@+node:ekr.20240105153420.17: *5* BaseTest.dump_times
    def dump_times(self):  # pragma: no cover
        """
        Show all calculated times.

        Keys should start with a priority (sort order) of the form `[0-9][0-9]:`
        """
        for key in sorted(self.times):
            t = self.times.get(key)
            key2 = key[3:]
            print(f"{key2:>16}: {t:6.3f} sec.")
    #@+node:ekr.20240105153420.18: *4* BaseTest.update_counts & update_times
    def update_counts(self, key, n):  # pragma: no cover
        """Update the count statistic given by key, n."""
        old_n = self.counts.get(key, 0)
        self.counts[key] = old_n + n

    def update_times(self, key, t):  # pragma: no cover
        """Update the timing statistic given by key, t."""
        old_t = self.times.get(key, 0.0)
        self.times[key] = old_t + t
    #@-others
#@+node:ekr.20240105153425.2: ** class Optional_TestFiles (BaseTest)
class Optional_TestFiles(BaseTest):
    """
    Tests for the TokenOrderGenerator class that act on files.

    These are optional tests. They take a long time and are not needed
    for 100% coverage.

    All of these tests failed at one time.
    """
    #@+others
    #@+node:ekr.20240105153425.3: *3* TestFiles.test_leoApp
    def test_leoApp(self):

        self.make_file_data('leoApp.py')
    #@+node:ekr.20240105153425.4: *3* TestFiles.test_leoAst
    def test_leoAst(self):

        self.make_file_data('leoAst.py')
    #@+node:ekr.20240105153425.5: *3* TestFiles.test_leoDebugger
    def test_leoDebugger(self):

        self.make_file_data('leoDebugger.py')
    #@+node:ekr.20240105153425.6: *3* TestFiles.test_leoFind
    def test_leoFind(self):

        self.make_file_data('leoFind.py')
    #@+node:ekr.20240105153425.7: *3* TestFiles.test_leoGlobals
    def test_leoGlobals(self):

        self.make_file_data('leoGlobals.py')
    #@+node:ekr.20240105153425.8: *3* TestFiles.test_leoTips
    def test_leoTips(self):

        self.make_file_data('leoTips.py')
    #@+node:ekr.20240105153425.9: *3* TestFiles.test_runLeo
    def test_runLeo(self):

        self.make_file_data('runLeo.py')
    #@-others
#@+node:ekr.20240105153425.42: ** class TestTokenBasedOrange (BaseTest)
class TestTokenBasedOrange(BaseTest):
    """
    Tests for the Orange class.

    **Important**: All unit tests assume that black_mode is False.
                   That is, unit tests assume that no blank lines
                   are ever inserted or deleted.
    """
    #@+others
    #@+node:ekr.20240105153425.43: *3* TestOrange.blacken
    def blacken(self, contents, line_length=None):
        """Return the results of running black on contents"""
        if not black:
            self.skipTest('Can not import black')  # pragma: no cover
        # Suppress string normalization!
        try:
            mode = black.FileMode()
            mode.string_normalization = False
            if line_length is not None:
                mode.line_length = line_length
        except TypeError:  # pragma: no cover
            self.skipTest('old version of black')
        return black.format_str(contents, mode=mode)
    #@+node:ekr.20240105153425.45: *3* TestOrange.test_annotations
    def test_annotations(self):

        table = (
        # Case 0.
        '''\
    def annotated_f(s: str = None, x=None) -> None:
        pass
    ''',
        )
        for i, contents in enumerate(table):
            contents, tokens = self.make_data(contents)
            expected = self.blacken(contents).rstrip() + '\n'
            results = self.beautify(contents, tokens)
            self.assertEqual(results, expected)

    #@+node:ekr.20240105153425.46: *3* TestOrange.test_at_doc_part
    def test_at_doc_part(self):

        line_length = 40  # For testing.
        contents = """\
    #@+at Line 1
    # Line 2
    #@@c

    print('hi')
    """
        contents, tokens = self.make_data(contents)
        expected = contents.rstrip() + '\n'
        results = self.beautify(contents, tokens,
            max_join_line_length=line_length,
            max_split_line_length=line_length,
        )
        self.assertEqual(results, expected)
    #@+node:ekr.20240105153425.47: *3* TestOrange.test_backslash_newline
    def test_backslash_newline(self):
        """
        This test is necessarily different from black, because orange doesn't
        delete semicolon tokens.
        """
        contents = r"""
    print(a);\
    print(b)
    print(c); \
    print(d)
    """
        contents, tokens = self.make_data(contents)
        expected = contents.rstrip() + '\n'
        # expected = self.blacken(contents).rstrip() + '\n'
        results = self.beautify(contents, tokens)
        self.assertEqual(results, expected)
    #@+node:ekr.20240105153425.48: *3* TestOrange.test_blank_lines_after_function
    def test_blank_lines_after_function(self):

        contents = """\
    # Comment line 1.
    # Comment line 2.

    def spam():
        pass
        # Properly indented comment.

    # Comment line3.
    # Comment line4.
    a = 2
    """
        contents, tokens = self.make_data(contents)
        expected = contents
        results = self.beautify(contents, tokens)
        self.assertEqual(results, expected)
    #@+node:ekr.20240105153425.49: *3* TestOrange.test_blank_lines_after_function_2
    def test_blank_lines_after_function_2(self):

        contents = """\
    # Leading comment line 1.
    # Leading comment lines 2.

    def spam():
        pass

    # Trailing comment line.
    a = 2
    """
        contents, tokens = self.make_data(contents)
        expected = contents
        results = self.beautify(contents, tokens)
        self.assertEqual(results, expected)
    #@+node:ekr.20240105153425.50: *3* TestOrange.test_blank_lines_after_function_3
    def test_blank_lines_after_function_3(self):

        # From leoAtFile.py.
        contents = r"""\
    def writeAsisNode(self, p):
        print('1')

        def put(s):
            print('2')

        # Trailing comment 1.
        # Trailing comment 2.
        print('3')
    """
        contents, tokens = self.make_data(contents)
        expected = contents
        results = self.beautify(contents, tokens)
        self.assertEqual(results, expected)
    #@+node:ekr.20240105153425.51: *3* TestOrange.test_bug_1429
    def test_bug_1429(self):

        contents = r'''\
    def get_semver(tag):
        """bug 1429 docstring"""
        try:
            import semantic_version
            version = str(semantic_version.Version.coerce(tag, partial=True))
                # tuple of major, minor, build, pre-release, patch
                # 5.6b2 --> 5.6-b2
        except(ImportError, ValueError) as err:
            print('\n', err)
            print("""*** Failed to parse Semantic Version from git tag '{0}'.
            Expecting tag name like '5.7b2', 'leo-4.9.12', 'v4.3' for releases.
            This version can't be uploaded to PyPi.org.""".format(tag))
            version = tag
        return version
    '''
        contents, tokens = self.make_data(contents)
        expected = contents.rstrip() + '\n'
        results = self.beautify(contents, tokens,
            max_join_line_length=0, max_split_line_length=0)
        self.assertEqual(results, expected)
    #@+node:ekr.20240105153425.52: *3* TestOrange.test_bug_1851
    def test_bug_1851(self):

        contents = r'''\
    def foo(a1):
        pass
    '''
        contents, tokens = self.make_data(contents)
        expected = contents.rstrip() + '\n'
        results = self.beautify(contents, tokens,
            max_join_line_length=0, max_split_line_length=0)
        self.assertEqual(results, expected)
    #@+node:ekr.20240105153425.53: *3* TestOrange.test_comment_indented
    def test_comment_indented(self):

        line_length = 40  # For testing.
        table = (
    """\
    if 1:
        pass
            # An indented comment.
    """,
    """\
    table = (
        # Indented comment.
    )
    """
        )

        fails = 0
        for contents in table:
            contents, tokens = self.make_data(contents)
            expected = contents
            if 0:
                dump_contents(contents)
                dump_tokens(tokens)
                # dump_tree(tokens, tree)
            results = self.beautify(contents, tokens,
                max_join_line_length=line_length,
                max_split_line_length=line_length,
            )
            message = (
                f"\n"
                f"  contents: {contents!r}\n"
                f"  expected: {expected!r}\n"
                f"       got: {results!r}")
            if results != expected:  # pragma: no cover
                fails += 1
                print(f"Fail: {fails}\n{message}")
        assert not fails, fails
    #@+node:ekr.20240105153425.54: *3* TestOrange.test_comment_space_after_delim
    def test_comment_space_after_delim(self):

        line_length = 40  # For testing.
        table = (
            # Test 1.
            (
                """#No space after delim.\n""",
                """# No space after delim.\n""",
            ),
            # Test 2.  Don't change bang lines.
            (
                """#! /usr/bin/env python\n""",
                """#! /usr/bin/env python\n""",
            ),
            # Test 3.  Don't change ### comments.
            (
                """### To do.\n""",
                """### To do.\n""",
            ),
        )
        fails = 0
        for contents, expected in table:
            contents, tokens = self.make_data(contents)
            if 0:
                dump_contents(contents)
                dump_tokens(tokens)
            results = self.beautify(contents, tokens,
                max_join_line_length=line_length,
                max_split_line_length=line_length,
            )
            message = (
                f"\n"
                f"  contents: {contents!r}\n"
                f"  expected: {expected!r}\n"
                f"       got: {results!r}")
            if results != expected:  # pragma: no cover
                fails += 1
                print(f"Fail: {fails}\n{message}")
        assert not fails, fails
    #@+node:ekr.20240105153425.55: *3* TestOrange.test_decorator
    def test_decorator(self):

        table = (
        # Case 0.
        """\
    @my_decorator(1)
    def func():
        pass
    """,
        # Case 1.
        """\
    if 1:
        @my_decorator
        def func():
            pass
    """,
        # Case 2.
        '''\
    @g.commander_command('promote')
    def promote(self, event=None, undoFlag=True):
        """Make all children of the selected nodes siblings of the selected node."""
    ''',
        )
        for i, contents in enumerate(table):
            contents, tokens = self.make_data(contents)
            expected = contents
            results = self.beautify(contents, tokens)
            if results != expected:
                g.trace('Fail:', i)  # pragma: no cover
            self.assertEqual(results, expected)
    #@+node:ekr.20240105153425.56: *3* TestOrange.test_dont_delete_blank_lines
    def test_dont_delete_blank_lines(self):

        line_length = 40  # For testing.
        contents = """\
    class Test:

        def test_func():

            pass

        a = 2
    """
        contents, tokens = self.make_data(contents)
        expected = contents.rstrip() + '\n'
        results = self.beautify(contents, tokens,
            max_join_line_length=line_length,
            max_split_line_length=line_length,
        )
        self.assertEqual(results, expected)
    #@+node:ekr.20240105153425.57: *3* TestOrange.test_function_defs
    def test_function_defs(self):

        table = (
        # Case 0.
        """\
    def f1(a=2 + 5):
        pass
    """,
        # Case 2
         """\
    def f1():
        pass
    """,
        # Case 3.
        """\
    def f1():
        pass
    """,
        # Case 4.
        '''\
    def should_kill_beautify(p):
        """Return True if p.b contains @killbeautify"""
        return 'killbeautify' in g.get_directives_dict(p)
    ''',
        )
        for i, contents in enumerate(table):
            contents, tokens = self.make_data(contents)
            expected = self.blacken(contents).rstrip() + '\n'
            results = self.beautify(contents, tokens)
            self.assertEqual(results, expected)
    #@+node:ekr.20240105153425.58: *3* TestOrange.test_join_and_strip_condition
    def test_join_and_strip_condition(self):

        contents = """\
    if (
        a == b or
        c == d
    ):
        pass
    """
        expected = """\
    if (a == b or c == d):
        pass
    """
        contents, tokens = self.make_data(contents)
        expected = textwrap.dedent(expected)
        # Black also removes parens, which is beyond our scope at present.
            # expected = self.blacken(contents, line_length=40)
        results = self.beautify(contents, tokens)
        self.assertEqual(results, expected)
    #@+node:ekr.20240105153425.59: *3* TestOrange.test_join_leading_whitespace
    def test_join_leading_whitespace(self):

        line_length = 40  # For testing.
        table = (
                            #1234567890x1234567890x1234567890x1234567890x
    """\
    if 1:
        print('4444',
            '5555')
    """,
    """\
    if 1:
        print('4444', '5555')\n""",
        )
        fails = 0
        for contents in table:
            contents, tokens = self.make_data(contents)
            if 0:
                dump_contents(contents)
                dump_tokens(tokens)
            expected = contents
            results = self.beautify(contents, tokens,
                max_join_line_length=line_length,
                max_split_line_length=line_length,
            )
            message = (
                f"\n"
                f"  contents: {contents!r}\n"
                f"  expected: {expected!r}\n"
                f"       got: {results!r}")
            if results != expected:  # pragma: no cover
                fails += 1
                print(f"Fail: {fails}\n{message}")
        assert not fails, fails
    #@+node:ekr.20240105153425.60: *3* TestOrange.test_join_lines
    def test_join_lines(self):

        # Except where noted, all entries are expected values....
        line_length = 40  # For testing.
        table = (
            #1234567890x1234567890x1234567890x1234567890x
            """print('4444',\n    '5555')""",
            """print('4444', '5555')\n""",
        )
        fails = 0
        for contents in table:
            contents, tokens = self.make_data(contents)
            if 0:
                dump_contents(contents)
                dump_tokens(tokens)
            expected = contents
            results = self.beautify(contents, tokens,
                max_join_line_length=line_length,
                max_split_line_length=line_length,
            )
            message = (
                f"\n"
                f"  contents: {contents!r}\n"
                f"  expected: {expected!r}\n"
                f"    orange: {results!r}")
            if results != expected:  # pragma: no cover
                fails += 1
                print(f"Fail: {fails}\n{message}")
        self.assertEqual(fails, 0)
    #@+node:ekr.20240105153425.61: *3* TestOrange.test_join_suppression
    def test_join_suppression(self):

        contents = """\
    class T:
        a = 1
        print(
           a
        )
    """
        expected = """\
    class T:
        a = 1
        print(a)
    """
        contents, tokens = self.make_data(contents)
        expected = textwrap.dedent(expected)
        results = self.beautify(contents, tokens)
        self.assertEqual(results, expected)
    #@+node:ekr.20240105153425.62: *3* TestOrange.test_join_too_long_lines
    def test_join_too_long_lines(self):

        # Except where noted, all entries are expected values....
        line_length = 40  # For testing.
        table = (
                            #1234567890x1234567890x1234567890x1234567890x
            (
                """print('aaaaaaaaaaaa',\n    'bbbbbbbbbbbb', 'cccccccccccccccc')""",
                """print('aaaaaaaaaaaa',\n    'bbbbbbbbbbbb', 'cccccccccccccccc')\n""",
            ),
        )
        fails = 0
        for contents, expected in table:
            contents, tokens = self.make_data(contents)
            if 0:
                dump_contents(contents)
                dump_tokens(tokens)
            results = self.beautify(contents, tokens,
                max_join_line_length=line_length,
                max_split_line_length=line_length,
            )
            message = (
                f"\n"
                f"  contents: {contents!r}\n"
                f"  expected: {expected!r}\n"
                f"       got: {results!r}")
            if results != expected:  # pragma: no cover
                fails += 1
                print(f"Fail: {fails}\n{message}")
        assert not fails, fails
    #@+node:ekr.20240105153425.63: *3* TestOrange.test_leading_stars
    def test_leading_stars(self):

        # #2533.
        contents = """\
            def f(
                arg1,
                *args,
                **kwargs
            ):
                pass
    """
        expected = textwrap.dedent("""\
            def f(arg1, *args, **kwargs):
                pass
    """)
        contents, tokens = self.make_data(contents)
        results = self.beautify(contents, tokens)
        self.assertEqual(expected, results)
    #@+node:ekr.20240105153425.64: *3* TestOrange.test_leading_stars_one_line
    def test_leading_stars_one_line(self):

        # if not use_ast:
            # self.skipTest('requires use_ast = True')

        # #2533.
        contents = """\
            def f(arg1, *args, **kwargs):
                pass
    """
        # expected = textwrap.dedent("""\
            # def f(arg1, *args, **kwargs):
                # pass
    # """)
        contents, tokens = self.make_data(contents)
        results = self.beautify(contents, tokens)
        self.assertEqual(contents, results)
    #@+node:ekr.20240105153425.65: *3* TestOrange.test_leo_sentinels
    def test_leo_sentinels_1(self):

        # Careful: don't put a sentinel into the file directly.
        # That would corrupt leoAst.py.
        sentinel = '#@+node:ekr.20200105143308.54: ** test'
        contents = f"""\
    {sentinel}
    def spam():
        pass
    """
        contents, tokens = self.make_data(contents)
        expected = contents.rstrip() + '\n'
        results = self.beautify(contents, tokens)
        self.assertEqual(results, expected)
    #@+node:ekr.20240105153425.66: *3* TestOrange.test_leo_sentinels_2
    def test_leo_sentinels_2(self):

        # Careful: don't put a sentinel into the file directly.
        # That would corrupt leoAst.py.
        sentinel = '#@+node:ekr.20200105143308.54: ** test'
        contents = f"""\
    {sentinel}
    class TestClass:
        pass
    """
        contents, tokens = self.make_data(contents)
        expected = contents.rstrip() + '\n'
        results = self.beautify(contents, tokens)
        self.assertEqual(results, expected)
    #@+node:ekr.20240105153425.67: *3* TestOrange.test_lines_before_class
    def test_lines_before_class(self):

        contents = """\
    a = 2
    class aClass:
        pass
    """
        contents, tokens = self.make_data(contents)
        expected = contents
        results = self.beautify(contents, tokens)
        self.assertEqual(results, expected)
    #@+node:ekr.20240105153425.68: *3* TestOrange.test_multi_line_pet_peeves
    def test_multi_line_pet_peeves(self):

        contents = """\
    if x == 4: pass
    if x == 4 : pass
    print (x, y); x, y = y, x
    print (x , y) ; x , y = y , x
    if(1):
        pass
    elif(2):
        pass
    while(3):
        pass
    """
        # At present Orange doesn't split lines...
        expected = """\
    if x == 4: pass
    if x == 4: pass
    print(x, y); x, y = y, x
    print(x, y); x, y = y, x
    if (1):
        pass
    elif (2):
        pass
    while (3):
        pass
    """
        contents, tokens = self.make_data(contents)
        expected = self.adjust_expected(expected)
        results = self.beautify(contents, tokens)
        self.assertEqual(results, expected)
    #@+node:ekr.20240105153425.69: *3* TestOrange.test_one_line_pet_peeves
    def test_one_line_pet_peeves(self):

        # See https://peps.python.org/pep-0008/#pet-peeves
        # See https://peps.python.org/pep-0008/#other-recommendations

        tag = 'test_one_line_pet_peeves'
        # Except where noted, all entries are expected values....
        if 0:
            # Test fails or recents...
            table = (
                # """a[: 1 if True else 2 :]""",
                """a[:-1]""",
            )
        else:
            table = (
                # Assignments...
                # Slices (colons)...
                """a[:-1]""",
                """a[: 1 if True else 2 :]""",
                """a[1 : 1 + 2]""",
                """a[lower:]""",
                """a[lower::]""",
                """a[:upper]""",
                """a[:upper:]""",
                """a[::step]""",
                """a[lower:upper:]""",
                """a[lower:upper:step]""",
                """a[lower + offset : upper + offset]""",
                """a[: upper_fn(x) :]""",
                """a[: upper_fn(x) : step_fn(x)]""",
                """a[:: step_fn(x)]""",
                """a[: upper_fn(x) :]""",
                """a[: upper_fn(x) : 2 + 1]""",
                """a[:]""",
                """a[::]""",
                """a[1:]""",
                """a[1::]""",
                """a[:2]""",
                """a[:2:]""",
                """a[::3]""",
                """a[1:2]""",
                """a[1:2:]""",
                """a[:2:3]""",
                """a[1:2:3]""",
                # * and **, inside and outside function calls.
                """a = b * c""",
                # Now done in test_star_star_operator
                # """a = b ** c""",  # Black has changed recently.
                """f(*args)""",
                """f(**kwargs)""",
                """f(*args, **kwargs)""",
                """f(a, *args)""",
                """f(a=2, *args)""",
                # Calls...
                """f(-1)""",
                """f(-1 < 2)""",
                """f(1)""",
                """f(2 * 3)""",
                """f(2 + name)""",
                """f(a)""",
                """f(a.b)""",
                """f(a=2 + 3, b=4 - 5, c= 6 * 7, d=8 / 9, e=10 // 11)""",
                """f(a[1 + 2])""",
                """f({key: 1})""",
                """t = (0,)""",
                """x, y = y, x""",
                # Dicts...
                """d = {key: 1}""",
                """d['key'] = a[i]""",
                # Trailing comments: expect two spaces.
                """whatever # comment""",
                """whatever  # comment""",
                """whatever   # comment""",
                # Word ops...
                """v1 = v2 and v3 if v3 not in v4 or v5 in v6 else v7""",
                """print(v7 for v8 in v9)""",
                # Unary ops...
                """v = -1 if a < b else -2""",
                # Returns...
                """return -1""",
            )
        fails = 0
        for i, contents in enumerate(table):
            description = f"{tag} part {i}"
            contents, tokens = self.make_data(contents, description=description)
            expected = self.blacken(contents)
            results = self.beautify(contents, tokens, filename=description)
            if results != expected:  # pragma: no cover
                fails += 1
                print('')
                print(
                    f"TestOrange.test_one_line_pet_peeves: FAIL {fails}\n"
                    f"  contents: {contents.rstrip()}\n"
                    f"     black: {expected.rstrip()}\n"
                    f"    orange: {results.rstrip()}")
        self.assertEqual(fails, 0)
    #@+node:ekr.20240105153425.70: *3* TestOrange.test_relative_imports
    def test_relative_imports(self):

        # #2533.
        contents = """\
            from .module1 import w
            from . module2 import x
            from ..module1 import y
            from .. module2 import z
            from . import a
            from.import b
            from leo.core import leoExternalFiles
            import leo.core.leoGlobals as g
    """
        expected = textwrap.dedent("""\
            from .module1 import w
            from .module2 import x
            from ..module1 import y
            from ..module2 import z
            from . import a
            from . import b
            from leo.core import leoExternalFiles
            import leo.core.leoGlobals as g
    """)
        contents, tokens = self.make_data(contents)
        results = self.beautify(contents, tokens)
        self.assertEqual(expected, results)
    #@+node:ekr.20240105153425.71: *3* TestOrange.test_return
    def test_return(self):

        contents = """return []"""
        expected = self.blacken(contents)
        contents, tokens = self.make_data(contents)
        results = self.beautify(contents, tokens)
        self.assertEqual(results, expected)
    #@+node:ekr.20240105153425.72: *3* TestOrange.test_single_quoted_string
    def test_single_quoted_string(self):

        contents = """print('hi')"""
        # blacken suppresses string normalization.
        expected = self.blacken(contents)
        contents, tokens = self.make_data(contents)
        results = self.beautify(contents, tokens)
        self.assertEqual(results, expected)
    #@+node:ekr.20240105153425.73: *3* TestOrange.test_split_lines
    def test_split_lines(self):

        line_length = 40  # For testing.
        table = (
        #1234567890x1234567890x1234567890x1234567890x
            """\
    if 1:
        print('1111111111', '2222222222', '3333333333')
    """,
    """print('aaaaaaaaaaaaa', 'bbbbbbbbbbbbbb', 'cccccc')""",
    """print('aaaaaaaaaaaaa', 'bbbbbbbbbbbbbb', 'cccccc', 'ddddddddddddddddd')""",
        )
        fails = 0
        for contents in table:
            contents, tokens = self.make_data(contents)
            if 0:
                dump_tokens(tokens)
            expected = self.blacken(contents, line_length=line_length)
            results = self.beautify(contents, tokens,
                max_join_line_length=line_length,
                max_split_line_length=line_length,
            )
            message = (
                f"\n"
                f"  contents: {contents!s}\n"
                f"     black: {expected!s}\n"
                f"    orange: {results!s}")
            if results != expected:  # pragma: no cover
                fails += 1
                print(f"Fail: {fails}\n{message}")
        self.assertEqual(fails, 0)
    #@+node:ekr.20240105153425.74: *3* TestOrange.test_split_lines_2
    def test_split_lines_2(self):

        line_length = 40  # For testing.
        # Different from how black handles things.
        contents = """\
    if not any([z.kind == 'lt' for z in line_tokens]):
        return False
    """
        expected = """\
    if not any(
        [z.kind == 'lt' for z in line_tokens]):
        return False
    """
        fails = 0
        contents, tokens = self.make_data(contents)
        expected = textwrap.dedent(expected)
        results = self.beautify(contents, tokens,
            max_join_line_length=line_length,
            max_split_line_length=line_length,
        )
        message = (
            f"\n"
            f"  contents: {contents!r}\n"
            f"  expected: {expected!r}\n"
            f"       got: {results!r}")
        if results != expected:  # pragma: no cover
            fails += 1
            print(f"Fail: {fails}\n{message}")
        self.assertEqual(fails, 0)
    #@+node:ekr.20240105153425.75: *3* TestOrange.test_split_lines_3
    def test_split_lines_3(self):

        line_length = 40  # For testing.
        # Different from how black handles things.
        contents = """print('eee', ('fffffff, ggggggg', 'hhhhhhhh', 'iiiiiii'), 'jjjjjjj', 'kkkkkk')"""
        # This is a bit different from black, but it's good enough for now.
        expected = """\
    print(
        'eee',
        ('fffffff, ggggggg', 'hhhhhhhh', 'iiiiiii'),
        'jjjjjjj',
        'kkkkkk',
    )
    """
        fails = 0
        contents, tokens = self.make_data(contents)
        expected = textwrap.dedent(expected)
        results = self.beautify(contents, tokens,
            max_join_line_length=line_length,
            max_split_line_length=line_length,
        )
        message = (
            f"\n"
            f"  contents: {contents!r}\n"
            f"  expected: {expected!r}\n"
            f"       got: {results!r}")
        if results != expected:  # pragma: no cover
            fails += 1
            print(f"Fail: {fails}\n{message}")
        self.assertEqual(fails, 0)
    #@+node:ekr.20240105153425.76: *3* TestOrange.test_star_star_operator
    def test_star_star_operator(self):
        # Was tested in pet peeves, but this is more permissive.
        contents = """a = b ** c"""
        contents, tokens = self.make_data(contents)
        # Don't rely on black for this test.
        # expected = self.blacken(contents)
        expected = contents
        results = self.beautify(contents, tokens)
        self.assertEqual(results, expected)
    #@+node:ekr.20240105153425.77: *3* TestOrange.test_sync_tokens
    def test_sync_tokens(self):

        contents = """if x == 4: pass"""
        # At present Orange doesn't split lines...
        expected = """if x == 4: pass"""
        contents, tokens = self.make_data(contents)
        expected = self.adjust_expected(expected)
        results = self.beautify(contents, tokens)
        self.assertEqual(results, expected)
    #@+node:ekr.20240105153425.78: *3* TestOrange.test_ternary
    def test_ternary(self):

        contents = """print(2 if name == 'class' else 1)"""
        contents, tokens = self.make_data(contents)
        expected = contents
        results = self.beautify(contents, tokens)
        self.assertEqual(results, expected)
    #@+node:ekr.20240105153425.79: *3* TestOrange.test_verbatim
    def test_verbatim(self):

        line_length = 40  # For testing.
        contents = textwrap.dedent("""\
    #@@nobeautify

    def addOptionsToParser(self, parser, trace_m):

        add = parser.add_option

        def add_bool(option, help, dest=None):
            add(option, action='store_true', dest=dest, help=help)

        add_bool('--diff',          'use Leo as an external git diff')
        # add_bool('--dock',          'use a Qt dock')
        add_bool('--fullscreen',    'start fullscreen')
        add_bool('--init-docks',    'put docks in default positions')
        # Multiple bool values.
        add('-v', '--version', action='store_true',
            help='print version number and exit')

    # From leoAtFile.py
    noDirective     =  1 # not an at-directive.
    allDirective    =  2 # at-all (4.2)
    docDirective    =  3 # @doc.

    #@@beautify
    """)
        contents, tokens = self.make_data(contents)
        expected = contents
        results = self.beautify(contents, tokens,
            max_join_line_length=line_length,
            max_split_line_length=line_length,
        )
        self.assertEqual(results, expected, msg=contents)
    #@+node:ekr.20240105153425.80: *3* TestOrange.test_verbatim_with_pragma
    def test_verbatim_with_pragma(self):

        line_length = 40  # For testing.
        contents = """\
    # pragma: no beautify

    def addOptionsToParser(self, parser, trace_m):

        add = parser.add_option

        def add_bool(option, help, dest=None):
            add(option, action='store_true', dest=dest, help=help)

        add_bool('--diff',          'use Leo as an external git diff')
        # add_bool('--dock',          'use a Qt dock')
        add_bool('--fullscreen',    'start fullscreen')
        add_other('--window-size',  'initial window size (height x width)', m='SIZE')
        add_other('--window-spot',  'initial window position (top x left)', m='SPOT')
        # Multiple bool values.
        add('-v', '--version', action='store_true',
            help='print version number and exit')

    # pragma: beautify
    """
        contents, tokens = self.make_data(contents)
        expected = contents
        results = self.beautify(contents, tokens,
            max_join_line_length=line_length,
            max_split_line_length=line_length,
        )
        self.assertEqual(results, expected, msg=contents)
    #@+node:ekr.20240105153425.81: *3* TestOrange.verbatim2
    def test_verbatim2(self):

        contents = """\
    #@@beautify
    #@@nobeautify
    #@+at Starts doc part
    # More doc part.
    # The @c ends the doc part.
    #@@c
    """
        contents, tokens = self.make_data(contents)
        expected = contents
        results = self.beautify(contents, tokens)
        self.assertEqual(results, expected, msg=contents)
    #@-others
#@+node:ekr.20240105153425.85: ** class TestTokens (BaseTest)
class TestTokens(BaseTest):
    """Unit tests for tokenizing."""
    #@+others
    #@+node:ekr.20240105153425.93: *3* TT.show_example_dump
    def show_example_dump(self):  # pragma: no cover

        # Will only be run when enabled explicitly.

        contents = """\
    print('line 1')
    print('line 2')
    print('line 3')
    """
        contents, tokens = self.make_data(contents)
        dump_contents(contents)
        dump_tokens(tokens)
    #@+node:ekr.20240105153425.94: *3* TT.test_bs_nl_tokens
    def test_bs_nl_tokens(self):
        # Test https://bugs.python.org/issue38663.

        contents = """\
    print \
        ('abc')
    """
        self.check_roundtrip(contents)
    #@+node:ekr.20240105153425.95: *3* TT.test_continuation_1
    def test_continuation_1(self):

        contents = """\
    a = (3,4,
        5,6)
    y = [3, 4,
        5]
    z = {'a': 5,
        'b':15, 'c':True}
    x = len(y) + 5 - a[
        3] - a[2] + len(z) - z[
        'b']
    """
        self.check_roundtrip(contents)
    #@+node:ekr.20240105153425.96: *3* TT.test_continuation_2
    def test_continuation_2(self):
        # Backslash means line continuation, except for comments
        contents = (
            'x=1+\\\n    2'
            '# This is a comment\\\n    # This also'
        )
        self.check_roundtrip(contents)
    #@+node:ekr.20240105153425.97: *3* TT.test_continuation_3
    def test_continuation_3(self):

        contents = """\
    # Comment \\\n
    x = 0
    """
        self.check_roundtrip(contents)
    #@+node:ekr.20240105153425.98: *3* TT.test_string_concatenation_1
    def test_string_concatentation_1(self):
        # Two *plain* string literals on the same line
        self.check_roundtrip("""'abc' 'xyz'""")
    #@+node:ekr.20240105153425.99: *3* TT.test_string_concatenation_2
    def test_string_concatentation_2(self):
        # f-string followed by plain string on the same line
        self.check_roundtrip("""f'abc' 'xyz'""")
    #@+node:ekr.20240105153425.100: *3* TT.test_string_concatenation_3
    def test_string_concatentation_3(self):
        # plain string followed by f-string on the same line
        self.check_roundtrip("""'abc' f'xyz'""")
    #@-others
#@+node:ekr.20240105153425.102: ** class TestTopLevelFunctions (BaseTest)
class TestTopLevelFunctions(BaseTest):
    """Tests for the top-level functions in leoAst.py."""
    #@+others
    #@+node:ekr.20240105153425.103: *3* test_get_encoding_directive
    def test_get_encoding_directive(self):

        filename = __file__
        assert os.path.exists(filename), repr(filename)
        with open(filename, 'rb') as f:
            bb = f.read()
        e = get_encoding_directive(bb)
        self.assertEqual(e.lower(), 'utf-8')
    #@+node:ekr.20240105153425.104: *3* test_strip_BOM
    def test_strip_BOM(self):

        filename = __file__
        assert os.path.exists(filename), repr(filename)
        with open(filename, 'rb') as f:
            bb = f.read()
        assert bb, filename
        e, s = strip_BOM(bb)
        assert e is None or e.lower() == 'utf-8', repr(e)
    #@-others
#@-others
#@-leo

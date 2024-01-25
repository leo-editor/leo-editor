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

# Classes to test.
from leo.core.leoTokens import InputToken, Tokenizer, TokenBasedOrange

# Utility functions.
from leo.core.leoTokens import dump_contents, dump_tokens, output_tokens_to_string
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
# Do *not* use LeoUnitTest as the base class.
# Doing so slows downt testing considerably.

class BaseTest(unittest.TestCase):
    """
    The base class of all tests of leoTokens.py.

    This class contains only helpers.
    """
    debug_list: list[str] = []

    def setUp(self) -> None:
        g.unitTesting = True

    #@+others
    #@+node:ekr.20240105153420.13: *3* BaseTest.beautify
    def beautify(self,
        contents,
        tokens,
        filename=None,
        max_join_line_length=None,
        max_split_line_length=None,
    ):
        """BaseTest.beautify."""
        if not contents:
            return ''  # pragma: no cover
        if not filename:
            filename = g.callers(2).split(',')[0]

        orange = TokenBasedOrange()
        result_s = orange.beautify(contents, filename, tokens)
        self.code_list = orange.code_list
        return result_s
    #@+node:ekr.20240105153420.4: *3* BaseTest.check_roundtrip
    def check_roundtrip(self, contents, *, debug_list: list[str] = None):
        """Check that the tokenizer round-trips the given contents."""
        # Several unit tests call this method.

        contents, tokens = self.make_data(contents, debug_list=debug_list)
        results = output_tokens_to_string(tokens)
        self.assertEqual(contents, results)
    #@+node:ekr.20240105153425.44: *3* BaseTest.make_data
    def make_data(self,
        contents: str,
        *,
        description: str = None,
        debug_list: str = None,
    ) -> tuple[str, list[InputToken]]:  # pragma: no cover
        """
        BaseTest.make_data. Prepare the data for one unit test:
        - Regularize the contents:
          contents = textwrap.dedent(contents).strip() + '\n'
        - Tokenize the contents using the Tokenizer class in leoTokens.py.
        - Dump the contents or tokens per the debug_list kwarg.
        - Return (contents, tokens)
        """
        assert contents.strip(), g.callers()

        # Set debug flags and counts.
        self.debug_list = debug_list or []
        self.trace_token_method = False

        # Check the debug_list.
        valid = ('contents', 'debug', 'tokens')
        for z in self.debug_list:
            if z not in valid:
                g.trace('Ignoring debug_list value:', z)

        # Ensure all tests start with a non-blank line and end in exactly one newline.
        contents = textwrap.dedent(contents).strip() + '\n'

        # Create the tokens.
        tokens = Tokenizer().make_input_tokens(contents)
        if not tokens:
            self.fail('BaseTest.make_data:Tokenizer().make_input_tokens failed')

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
        contents = g.readFileIntoUnicodeString(filename)
        contents, tokens = self.make_data(contents, description=filename)
        return contents, tokens
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
    Tests for the TokenBasedOrange class.

    Note: TokenBasedOrange never inserts or deletes lines.
    """
    #@+others
    #@+node:ekr.20240105153425.43: *3* TestTBO.blacken
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
    #@+node:ekr.20240116104552.1: *3* TestTBO.slow_test_leoColorizer
    def slow_test_leoApp(self) -> None:

        g.trace('=====')
        filename = 'leoColorizer.py'
        test_dir = os.path.dirname(__file__)
        path = g.os_path_finalize_join(test_dir, '..', '..', 'core', filename)
        assert os.path.exists(path), repr(path)

        tbo = TokenBasedOrange()
        tbo.filename = path

        if 0:  # Diff only.
            tbo.beautify_file(path)
        else:
            contents, tokens = self.make_file_data(path)
            expected = contents
            results = self.beautify(contents, tokens)

            regularized_expected = tbo.regularize_nls(expected)
            regularized_results = tbo.regularize_nls(results)

            if regularized_expected != regularized_results:
                tbo.show_diffs(regularized_expected, regularized_results)

            assert regularized_expected == regularized_results

            ### self.assertEqual(regularized_expected, regularized_results)
    #@+node:ekr.20240105153425.45: *3* TestTBO.test_annotations
    def test_annotations(self):

        table = (
            # Case 0.
            """s: str = None\n""",
            # Case 1.
            ("""
                def annotated_f(s: str = None, x=None) -> None:
                    pass
            """),
            # Case 2.
            ("""
                def f1():
                    self.rulesetName : str = ''
            """),
        )
        for i, contents in enumerate(table):
            contents, tokens = self.make_data(contents)
            expected = self.blacken(contents).rstrip() + '\n'
            results = self.beautify(contents, tokens)
            if results != expected:
                g.printObj(contents, tag='Contents')
                g.printObj(expected, tag='Expected (blackened)')
                g.printObj(results, tag='Results')
            self.assertEqual(results, expected)

    #@+node:ekr.20240124230807.1: *3* TestTBO.test_assignment
    def test_assignment(self):

        # From leoFileCommands.py.
        contents = """
            c.hiddenRootNode.children = rootChildren
            (w, h, x, y, r1, r2, encp) = fc.getWindowGeometryFromDb(conn)
        """
        contents, tokens = self.make_data(contents)
        expected = self.blacken(contents).rstrip() + '\n'
        results = self.beautify(contents, tokens)
        self.assertEqual(results, expected)


    #@+node:ekr.20240105153425.46: *3* TestTBO.test_at_doc_part
    def test_at_doc_part(self):

        contents = """\
    #@+at Line 1
    # Line 2
    #@@c

    print('hi')
    """
        contents, tokens = self.make_data(contents)
        expected = contents.rstrip() + '\n'
        results = self.beautify(contents, tokens)
        self.assertEqual(results, expected)
    #@+node:ekr.20240105153425.47: *3* TestTBO.test_backslash_newline
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
    #@+node:ekr.20240105153425.48: *3* TestTBO.test_blank_lines_after_function
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
    #@+node:ekr.20240105153425.49: *3* TestTBO.test_blank_lines_after_function_2
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
    #@+node:ekr.20240105153425.50: *3* TestTBO.test_blank_lines_after_function_3
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
    #@+node:ekr.20240105153425.52: *3* TestTBO.test_bug_1851
    def test_bug_1851(self):

        contents = r'''\
    def foo(a1):
        pass
    '''
        contents, tokens = self.make_data(contents)
        expected = contents.rstrip() + '\n'
        results = self.beautify(contents, tokens)
        self.assertEqual(results, expected)
    #@+node:ekr.20240116155903.1: *3* TestTBO.test_colorizer_fail
    def test_colorizer_fail(self):

        contents = '''

            # leoColorizer.py: line 2268
            if j > len(s) and not dots:
                j = len(s) + 1

                def span(s: str) -> int:
                    # Note: bindings are frozen by this def.
                    return self.restart_match_span(s, kind,
                        delegate=delegate,
                    )
        '''

        contents, tokens = self.make_data(contents)
        # dump_tokens(tokens)
        expected = contents
        results = self.beautify(contents, tokens)
        if False and results != expected:
            g.printObj(expected, tag='Expected (same as Contents)')
            g.printObj(results, tag='Results')
        self.maxDiff = None
        self.assertEqual(results, expected)
    #@+node:ekr.20240105153425.53: *3* TestTBO.test_comment_indented
    def test_comment_indented(self):

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
            results = self.beautify(contents, tokens)
            message = (
                f"\n"
                f"  contents: {contents!r}\n"
                f"  expected: {expected!r}\n"
                f"       got: {results!r}")
            if results != expected:  # pragma: no cover
                fails += 1
                print(f"Fail: {fails}\n{message}")
        assert not fails, fails
    #@+node:ekr.20240105153425.54: *3* TestTBO.test_comment_space_after_delim
    def test_comment_space_after_delim(self):

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
            results = self.beautify(contents, tokens)
            message = (
                f"\n"
                f"  contents: {contents!r}\n"
                f"  expected: {expected!r}\n"
                f"       got: {results!r}")
            if results != expected:  # pragma: no cover
                fails += 1
                print(f"Fail: {fails}\n{message}")
        assert not fails, fails
    #@+node:ekr.20240105153425.55: *3* TestTBO.test_decorator
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
    #@+node:ekr.20240112134732.1: *3* TestTBO.test_def_colons
    def test_def_colons(self):

        contents = '''
            self.configDict: dict[str, Any] = {}
            self.configUnderlineDict: dict[str, bool] = {}
        '''
        contents, tokens = self.make_data(contents)
        # dump_tokens(tokens)
        expected = contents
        results = self.beautify(contents, tokens)
        if results != expected:
            # g.printObj(contents, tag='Contents')
            g.printObj(expected, tag='Expected (same as Contents)')
            g.printObj(results, tag='Results')

        self.maxDiff = None
        self.assertEqual(results, expected)

    #@+node:ekr.20240114100847.1: *3* TestTBO.test_def_square_brackets
    def test_def_square_brackets(self):

        contents = (
            """def checkForDuplicateShortcuts(self, c: Cmdr, d: dict[str, str]) -> None:\n"""
        )
        contents, tokens = self.make_data(contents)
        # dump_tokens(tokens)
        expected = contents
        results = self.beautify(contents, tokens)
        if False and results != expected:
            # g.printObj(contents, tag='Contents')
            g.printObj(expected, tag='Expected (same as Contents)')
            g.printObj(results, tag='Results')

        self.maxDiff = None
        self.assertEqual(results, expected)
    #@+node:ekr.20240105153425.56: *3* TestTBO.test_dont_delete_blank_lines
    def test_dont_delete_blank_lines(self):

        contents = """\
    class Test:

        def test_func():

            pass

        a = 2
    """
        contents, tokens = self.make_data(contents)
        expected = contents.rstrip() + '\n'
        results = self.beautify(contents, tokens)
        self.assertEqual(results, expected)
    #@+node:ekr.20240116072845.1: *3* TestTBO.test_expressions
    def test_expressions(self):

        contents = """skip_count = max(0, (len(target) - 1))\n"""

        contents, tokens = self.make_data(contents)
        expected = self.blacken(contents)
        results = self.beautify(contents, tokens)
        if expected != results:
            g.printObj(expected, tag='Explected (blackened)')
            g.printObj(results, tag='Results')
        self.assertEqual(results, expected)
    #@+node:ekr.20240107080413.1: *3* TestTBO.test_function_calls
    def test_function_calls(self):

        table = (
            # Case 0: (legacy)
            # ("""
                # version = str(semantic_version.Version.coerce(tag, partial=True))
            # """),

            # Case 1: leoApp, line 1657
            # ("""
                # if True:
                    # home = os.getenv(home[1:-1], default=None)
            # """),

            # Case 2: LeoApp.py, line 1872.
            ("""
                if path.startswith(tag):
                    return self.computeBindingLetter(c, path=path[len(tag) :])
            """),

            # Case 3: LeoApp.py, line 3416.
            ("""
                if groupedEntries:
                    dirCount: dict[str, Any] = {}
                    for fileName in rf.getRecentFiles()[:n]:
                        dirName, baseName = g.os_path_split(fileName)
            """),
        )
        fails = 0
        for i, contents in enumerate(table):
            contents, tokens = self.make_data(contents)
            expected = self.blacken(contents).rstrip() + '\n'
            results = self.beautify(contents, tokens)
            if results != expected:
                fails += 1
                # dump_tokens(tokens)
                if 0:
                    g.printObj(contents, tag='Contents')
                    g.printObj(expected, tag='Expected (blackened)')
                    g.printObj(results, tag='Results')
                self.assertEqual(expected, results)
        # self.assertEqual(fails, 0)


    #@+node:ekr.20240105153425.57: *3* TestTBO.test_function_defs
    def test_function_defs(self):

        long_table = (
        # Case 0.
        """\
    def f1(a=2 + 5):
        pass
    """,
        # Case 2
         """\
    def f2(a):
        pass
    """,
        # Case 3.
        """\
    def f3(a: int = 2):
        pass
    """,
        # Case 4.
        '''\
    def should_kill_beautify(p):
        """Return True if p.b contains @killbeautify"""
        return 'killbeautify' in g.get_directives_dict(p)
    ''',
        # Case 5 (new)
        '''\
        def reloadSettings():
            pass
    ''',
        # Case 6 (new)
        '''\
        def tuple_init(stack: Sequence[str] = ('root',)) -> Generator:
            pass
    ''',
        # Case 7 (new)
    )
        short_table = (
        '''\
        def tuple_init(stack: Sequence[str] = ('root',)) -> Generator:
            pass
    ''',
    )
        assert long_table and short_table
        table = short_table  ###
        for i, contents in enumerate(table):
            contents, tokens = self.make_data(contents)
            expected = self.blacken(contents).rstrip() + '\n'
            results = self.beautify(contents, tokens)
            if expected != results:
                g.printObj(expected, tag='Explected (blackened)')
                g.printObj(results, tag='Results')
            self.assertEqual(results, expected)
    #@+node:ekr.20240105153425.63: *3* TestTBO.test_leading_stars
    def test_leading_stars(self):

        # #2533.
        contents = """
            def f(
                arg1,
                *args,
                **kwargs
            ):
                pass
        """
        contents, tokens = self.make_data(contents)
        if 1:  # w/o join:
            expected = contents
        else:  # with join.
            expected = """
                def f(arg1, *args, **kwargs):
                    pass
            """
        results = self.beautify(contents, tokens)
        self.assertEqual(expected, results)
    #@+node:ekr.20240105153425.64: *3* TestTBO.test_leading_stars_one_line
    def test_leading_stars_one_line(self):

        # #2533.
        contents = """
            def f(arg1, *args, **kwargs):
                pass
        """
        contents, tokens = self.make_data(contents)
        results = self.beautify(contents, tokens)
        self.assertEqual(contents, results)
    #@+node:ekr.20240105153425.65: *3* TestTBO.test_leo_sentinels
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
    #@+node:ekr.20240105153425.66: *3* TestTBO.test_leo_sentinels_2
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
    #@+node:ekr.20240105153425.67: *3* TestTBO.test_lines_before_class
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
    #@+node:ekr.20240105153425.68: *3* TestTBO.test_multi_line_pet_peeves
    def test_multi_line_pet_peeves(self):

        contents = """
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
        expected = textwrap.dedent(
            """
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
            """).strip() + '\n'
        contents, tokens = self.make_data(contents)
        results = self.beautify(contents, tokens)
        self.assertEqual(results, expected)
    #@+node:ekr.20240105153425.69: *3* TestTBO.test_one_line_pet_peeves
    def test_one_line_pet_peeves(self):

        # One-line pet peeves, except those involving slices and unary ops.

        # See https://peps.python.org/pep-0008/#pet-peeves
        # See https://peps.python.org/pep-0008/#other-recommendations

        tag = 'test_one_line_pet_peeves'
        # Except where noted, all entries are expected values....

        table = (
            ### Latest fail: duplicate
            """f({key: 1})""",  ### Duplicate.
            # Assignments...
            """a = b * c""",
            """a = b + c""",
            """a = b - c""",
            # * and **, inside and outside function calls.
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
            # Returns...
            """return -1""",
        )
        fails = 0
        fail_fast = True
        for i, contents in enumerate(table):
            description = f"{tag} part {i}"
            contents, tokens = self.make_data(contents, description=description)
            expected = self.blacken(contents)
            results = self.beautify(contents, tokens, filename=description)
            if results != expected:  # pragma: no cover
                fails += 1
                print('')
                print(
                    f"TestTokenBasedOrange.{tag}: FAIL {fails}\n"
                    f"  contents: {contents.rstrip()}\n"
                    f"     black: {expected.rstrip()}\n"
                    f"    orange: {results.rstrip() if results else 'None'}")
            if fail_fast:
                self.assertEqual(results, expected, msg=description)
        if not fail_fast:
            self.assertEqual(fails, 0)
    #@+node:ekr.20240105153425.70: *3* TestTBO.test_relative_imports
    def test_relative_imports(self):

        # #2533.
        contents = """
            from .module1 import w
            from . module2 import x
            from ..module1 import y
            from .. module2 import z
            from . import a
            from.import b
            from .. import c
            from..import d
            from leo.core import leoExternalFiles
            import leo.core.leoGlobals as g
        """
        expected = textwrap.dedent("""
            from .module1 import w
            from .module2 import x
            from ..module1 import y
            from ..module2 import z
            from . import a
            from . import b
            from .. import c
            from .. import d
            from leo.core import leoExternalFiles
            import leo.core.leoGlobals as g
        """).strip() + '\n'
        contents, tokens = self.make_data(contents)
        # dump_tokens(tokens)
        results = self.beautify(contents, tokens)
        if results != expected:
            g.printObj(results, tag='Results')
            g.printObj(expected, tag='Expected')
        self.assertEqual(expected, results)
    #@+node:ekr.20240105153425.71: *3* TestTBO.test_return
    def test_return(self):

        contents = """return []"""
        expected = self.blacken(contents)
        contents, tokens = self.make_data(contents)
        results = self.beautify(contents, tokens)
        self.assertEqual(results, expected)
    #@+node:ekr.20240105153425.72: *3* TestTBO.test_single_quoted_string
    def test_single_quoted_string(self):

        contents = """print('hi')"""
        # blacken suppresses string normalization.
        expected = self.blacken(contents)
        contents, tokens = self.make_data(contents)
        results = self.beautify(contents, tokens)
        self.assertEqual(results, expected)
    #@+node:ekr.20240109090653.1: *3* TestTBO.test_slice
    def test_slice(self):

        # Test one-line pet peeves involving slices.

        # See https://peps.python.org/pep-0008/#pet-peeves
        # See https://peps.python.org/pep-0008/#other-recommendations

        tag = 'test_slice'

        # Except where noted, all entries are expected values....
        table = (
            # Recent fails...
                # From leoAst.py.
                """val = val[:i] + '# ' + val[i + 1 :]\n""",
                # From leoApp.py.
                """
                    for name in rf.getRecentFiles()[:n]:
                        pass
            """,
            # Legacy tests...
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
        )
        trace = True  ###
        fails = 0
        fail_fast = True
        for i, contents in enumerate(table):
            description = f"{tag} part {i}"
            contents, tokens = self.make_data(contents, description=description)
            expected = self.blacken(contents)
            results = self.beautify(contents, tokens, filename=description)
            if results != expected:  # pragma: no cover
                fails += 1
                if trace:
                    print('')
                    print(
                        f"TestTokenBasedOrange.{tag}: FAIL {fails}\n"
                        # f"  contents: {contents.rstrip()}\n"
                        f"     black: {expected.rstrip()}\n"
                        f"    orange: {results.rstrip() if results else 'None'}")
            if fail_fast:
                self.assertEqual(expected, results)

        self.assertEqual(fails, 0)
    #@+node:ekr.20240105153425.76: *3* TestTBO.test_star_star_operator
    def test_star_star_operator(self):
        # Was tested in pet peeves, but this is more permissive.
        contents = """a = b ** c"""
        contents, tokens = self.make_data(contents)
        # Don't rely on black for this test.
        # expected = self.blacken(contents)
        expected = contents
        results = self.beautify(contents, tokens)
        self.assertEqual(results, expected)
    #@+node:ekr.20240105153425.78: *3* TestTBO.test_ternary
    def test_ternary(self):

        contents = """print(2 if name == 'class' else 1)"""
        contents, tokens = self.make_data(contents)
        expected = contents
        results = self.beautify(contents, tokens)
        self.assertEqual(results, expected)
    #@+node:ekr.20240109070553.1: *3* TestTBO.test_unary_op
    def test_unary_op(self):

        # One-line pet peeves involving unary ops but *not* slices.

        # See https://peps.python.org/pep-0008/#pet-peeves
        # See https://peps.python.org/pep-0008/#other-recommendations

        tag = 'test_unary_op'

        # All entries are expected values....
        table = (
            # Most recent fail.
            """d = {key: -3}""",  ### Duplicate.
            # Calls...
            """f(-1)""",
            """f(-1 < 2)""",
            # Dicts...
            """d = {key: -3}""",
            """d['key'] = a[-i]""",
            # Unary ops...
            """v = -1 if a < b else -2""",
        )
        fails = 0
        fail_fast = True
        for i, contents in enumerate(table):
            description = f"{tag} part {i}"
            contents, tokens = self.make_data(contents, description=description)
            expected = self.blacken(contents)
            results = self.beautify(contents, tokens, filename=description)
            if results != expected:  # pragma: no cover
                fails += 1
                print('')
                print(
                    f"TestTokenBasedOrange.{tag}: FAIL {fails}\n"
                    f"  contents: {contents.rstrip()}\n"
                    f"     black: {expected.rstrip()}\n"
                    f"    orange: {results.rstrip() if results else 'None'}")
            if fail_fast:
                self.assertEqual(results, expected, msg=description)
        if not fail_fast:
            self.assertEqual(fails, 0)
    #@+node:ekr.20240105153425.79: *3* TestTBO.test_verbatim
    def test_verbatim(self):

        contents = """
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
    """
        contents, tokens = self.make_data(contents)
        expected = contents
        results = self.beautify(contents, tokens)
        self.assertEqual(results, expected, msg=contents)
    #@+node:ekr.20240105153425.80: *3* TestTBO.test_verbatim_with_pragma
    def test_verbatim_with_pragma(self):

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
        results = self.beautify(contents, tokens)
        self.assertEqual(results, expected, msg=contents)
    #@+node:ekr.20240105153425.81: *3* TestTBO.verbatim2
    def test_verbatim2(self):

        # We *do* want this test to contain verbatim sentinels.
        contents = """
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
        # g.printObj(results, tag='Results')
        # g.printObj(expected, tag='Expected')
        self.assertEqual(results, expected, msg=contents)
    #@+node:ekr.20240124092041.1: *3* TestTBO.test_fstrings
    def test_fstrings(self):

        ### """g.es_print(f"removing callback: {callback}")\n"""

        # leoApp.py, line 885.
        contents = """signon = [f"Leo {leoVer}"]\n"""
        contents, tokens = self.make_data(contents)
        expected = self.blacken(contents)
        # dump_tokens(tokens)
        results = self.beautify(contents, tokens)
        self.assertEqual(results, expected)
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
#@-others
#@-leo

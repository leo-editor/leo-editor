#@+leo-ver=5-thin
#@+node:ekr.20210902164946.1: * @file ../unittests/core/test_leoGlobals.py
"""Tests of leoGlobals.py"""

import io
import os
import re
import stat
import sys
import textwrap
from leo.core import leoGlobals as g
from leo.core.leoTest2 import LeoUnitTest

#@+others
#@+node:ekr.20210902165045.1: ** class TestGlobals(LeoUnitTest)
class TestGlobals(LeoUnitTest):

    #@+<< TestGlobals: declare all data >>
    #@+node:ekr.20230701083715.1: *3* << TestGlobals: declare all data >>
    absolute_paths: list[str]
    error_lines: dict[str, int]
    error_messages: dict[str, list[str]]
    error_patterns: dict[str, re.Pattern]
    error_templates: dict[str, str]
    files_data: tuple[str, str]
    invalid_unls: tuple[str]
    tools = ['flake8', 'mypy', 'pyflakes', 'pylint', 'python']
    valid_unls: tuple[str]
    #@-<< TestGlobals: declare all data >>
    #@+<< TestGlboals: define unchanging data >>
    #@+node:ekr.20230701083918.1: *3* << TestGlboals: define unchanging data >>
    #@+<< define files data >>
    #@+node:ekr.20230701060241.1: *4* << define files data >>
    # All these paths appear in @file or @clean nodes in LeoPyRef.leo.

    # kind: @clean, @edit, @file,
    # path: path to an existing file, relative to LeoPyRef.leo (in leo/core).
    files_data = (
        # The hard case: __init__.py
        ('@file', '../plugins/importers/__init__.py'),
        ('@file',  '../plugins/writers/__init__.py'),
        ('@clean', '../plugins/leo_babel/__init__.py'),
        ('@file',  '../plugins/editpane/__init__.py'),
        # Other files.
        ('@file', 'leoApp.py'),
        ('@file', '../commands/abbrevCommands.py'),
        ('@edit', '../../launchLeo.py'),
        ('@file', '../external/log_listener.py'),
        ('@file', '../plugins/cursesGui2.py'),
    )
    #@-<< define files data >>
    #@+<< define error_patterns >>
    #@+node:ekr.20230701060854.1: *4* << define error_patterns >>
    # m.group(1) is the filename and m.group(2) is the line number.
    error_patterns = {
        'flake8': g.flake8_pat,     # r'(.+?):([0-9]+):[0-9]+:.*$'
        'mypy':  g.mypy_pat,        # r'^(.+?):([0-9]+):\s*(error|note)\s*(.*)\s*$'
        'pyflakes': g.pyflakes_pat, # r'^(.*):([0-9]+):[0-9]+ .*?$'
        'pylint': g.pylint_pat,     # r'^(.*):\s*([0-9]+)[,:]\s*[0-9]+:.*?\(.*\)\s*$'
        'python': g.python_pat,     # r'^\s*File\s+"(.*?)",\s*line\s*([0-9]+)\s*$'
    }
    #@-<< define error_patterns >>
    #@+<< define error_templates >>
    #@+node:ekr.20230701071240.1: *4* << define error_templates >>
    # Error message templates.
    error_templates = {
        'flake8':   'FILE:LINE:COL:ERR',
        'mypy':     'FILE:LINE:error ERR',
        'pyflakes': 'FILE:LINE:COL ERR',
        'pylint':   'FILE:LINE:COL: (ERR)',
        'python':   'File "FILE", line LINE',
    }
    #@-<< define error_templates >>
    #@+<< define invalid_unls >>
    #@+node:ekr.20230701084458.1: *4* << define invalid_unls >>
    # Syntactically invalid unls.
    invalid_unls = (
        'unl:gnx:xyzzy#.20230622112649.1',  # Missing '//'
        'unl:gnx://xyzzy.20230622112649.1', # Missing '#'
        'unl:gnx//xyzzy#.20230622112649.1', # Missing ':'
        'unl//xyzzy#.20230622112649.1', # Missing ':'

    )

    #@-<< define invalid_unls >>
    #@+<< define missing_unls >>
    #@+node:ekr.20230701090956.1: *4* << define missing_unls >>
    # Define unls with files parts that refer to non-existent files.
    # These should be syntactically valid.
    missing_unls = (
        'unl:gnx://xyzzy#.20230622112649.1',
        'unl://xyzzy#does-->not-->exist',
    )
    #@-<< define missing_unls >>
    #@+<< define valid_unl_templates >>
    #@+node:ekr.20230701090956.2: *4* << define valid_unl_templates >>
    # These links are functional only if on @data unl-path-prefixes contains the proper file part.
    valid_unls = (

        'unl:gnx://#ekr.20180311131424.1',

        # test.leo:Error mssages (copy to log)
        'unl:gnx://#ekr.20230622112649.1',

        # test.leo:Recent
        'unl:gnx://test.leo#ekr.20180311131424.1',
        'unl:gnx://#ekr.20180311131424.1',

        # test.leo: Error mssages (copy to log)
        'unl:gnx://test.leo#ekr.20230622112649.1',
        'unl:gnx://#ekr.20230622112649.1',

        # In LeoDocs.leo: Leo 6.7.3 release notes
        'unl:gnx://LeoDocs.leo#ekr.20230409052507.1',

        # In LeoDocs.leo: ** Read me first **
        'unl:gnx://LeoDocs.leo#ekr.20050831195449',

        # Legacy unls in test.leo.
        'unl://#Coloring tests-->Syntax coloring template',
        'unl://#@file ../plugins/importers/__init__.py',
        'unl://C:/Repos/leo-editor/leo/test/test.leo#@clean ../plugins/leo_babel/__init__.py',
        'unl://#@clean ../plugins/leo_babel/__init__.py',
        'unl://C:/Repos/leo-editor/leo/test/test.leo#Viewrendered examples',
        'unl://#Viewrendered examples',
        'unl://C:/Repos/leo-editor/leo/test/test.leo#Viewrendered examples-->Python code',
        'unl://#Viewrendered examples-->Python code',

        # Absolute file: valid, but can't be resolved in a unit test.
        'unl://C:/Repos/leo-editor/leo/test/test.leo#@file ../plugins/importers/__init__.py',

    )
    #@-<< define valid_unl_templates >>
    #@-<< TestGlboals: define unchanging data >>

    #@+others
    #@+node:ekr.20230701061343.1: *3*  TestGlobals: setup helpers and related tests
    #@+node:ekr.20230701065318.1: *4* TestGlobals._define_per_commander_data
    def _define_per_commander_data(self):
        """Define data that depends on c."""
        c = self.c

        # List of absolute paths in the test data.
        self.assertTrue(c.fileName)
        self.absolute_paths = [
            g.os_path_finalize_join(os.path.dirname(c.fileName()), relative_path)
                for _, relative_path in self.files_data
        ]

        # The error line for each absolute path. Default all lines to 0.
        self.error_lines = {}
        for z in self.absolute_paths:
            self.error_lines[z] = 0

        # Error messages for every tool and every absolute path.
        self.error_messages = {}
        for tool in self.tools:
            self.error_messages [tool] = []
            for path in self.absolute_paths:
                template = self.error_templates[tool]
                self.error_messages[tool].append(
                    template.replace('FILE', path)
                    .replace('LINE', '1')
                    .replace('COL', f"{self.error_lines[path]!s}")
                    .replace('ERR', f"{tool} error")
                )
    #@+node:ekr.20230701061355.1: *4* TestGlobals._test_per_commander_data
    def _test_per_commander_data(self):
        """Test the test data."""
        c = self.c

        # All dicts must have the same keys.
        for d in (self.error_messages, self.error_patterns, self.error_templates):
            self.assertEqual(self.tools, list(sorted(d.keys())))

        # Pretest: all absolute paths must exist.
        for z in self.absolute_paths:
            self.assertTrue(os.path.exists(z), msg=repr(z))

        # Pretest: all generated error messages must match the tool's pattern.
        for tool in self.tools:
            pattern = self.error_patterns[tool]
            messages = self.error_messages[tool]
            for message in messages:
                self.assertTrue(pattern.match(message), msg=(
                    'Error message does not match error pattern:\n'
                    f"    tool: {tool!r}\n"
                    f" message: {message!r}\n"
                    f" pattern: {pattern!r}"))

        # More tests...
        for data in self.files_data:  # <@file> <filename>
            kind, relative_path = data
            headline = msg = f"{kind} {relative_path}"
            absolute_path = g.os_path_finalize_join(g.app.loadDir, relative_path)
            self.assertTrue(absolute_path in self.absolute_paths, msg=msg)
            self.assertTrue(os.path.exists(absolute_path), msg=msg)
            self._make_tree(c, headline)
            test_p = g.findNodeAnywhere(c, headline)
            full_path = c.fullPath(test_p)
            self.assertEqual(full_path, absolute_path, msg=msg)
            self.assertTrue(test_p, msg=msg)
    #@+node:ekr.20230330042647.1: *4* TestGlobals._make_tree
    def _make_tree(self, c, root_h=None):
        """Make a test tree for c."""
        ### c = self.c
        root = c.rootPosition()
        root.h = root_h or 'Root'
        root.b = "def root():\n    pass\n"
        last = root

        def make_child(n, p):
            p2 = p.insertAsLastChild()
            p2.h = f"child {n}"
            p2.b = (
                f"def child{n}():\n"
                f"    v{n} = 2\n"
                f"    # node {n} line 1: blabla second blabla bla second ble blu\n"
                f"    # node {n} line 2: blabla second blabla bla second ble blu"
            )
            return p2

        def make_top(n, sib):
            p = sib.insertAfter()
            p.h = f"Node {n}"
            p.b = (
                f"def top{n}():\n:"
                f"    v{n} = 3\n"
            )
            return p

        for n in range(0, 4, 3):
            last = make_top(n + 1, last)
            child = make_child(n + 2, last)
            make_child(n + 3, child)

        for p in c.all_positions():
            p.v.clearDirty()
            p.v.clearVisited()

        # Always start with the root selected.
        c.selectPosition(c.rootPosition())
    #@+node:ekr.20230702165040.1: *4* TestGlobals._patch_at_data_unl_path_prefixes
    def _patch_at_data_unl_path_prefixes(self):
        """
        Create a new outline, linked into g.app.windowList.

        Patch @data unl-path-prefixes so that g.findAnyUnl will find nodes in
        the new commander.

        Return the commander for the new outline.
        """
        from leo.core.leoCommands import Commands
        c = c1 = self.c

        # Create the new commander, linked into g.app.windowList.
        c2 = Commands(fileName=None, gui=g.app.gui)
        self.assertTrue(c2.frame)
        g.app.windowList.append(c1.frame)
        g.app.windowList.append(c2.frame)

        # Give both commanders new (non-existent) names.
        c1_name = 'test_outline1.leo'
        c2_name = 'test_outline2.leo'
        directory = os.path.dirname(c.fileName())
        c.mFileName = os.path.normpath(os.path.join(directory, c1_name))
        c2.mFileName = os.path.normpath(os.path.join(directory, c2_name))
        self.assertEqual(c1_name, os.path.basename(c.fileName()))
        self.assertEqual(c2_name, os.path.basename(c2.fileName()))

        def make_line(c):
            file_name = c.fileName()
            key = os.path.basename(file_name)
            # Values must be directories.
            value = os.path.normpath(os.path.dirname(file_name))
            # print(f"{key:17} {value}")
            return f"{key}: {value}"

        # Init the @data unl-path-prefixes.
        lines = [make_line(z) for z in (c, c2)]
        self._set_setting(c, kind='data', name='unl-path-prefixes', val=lines)
        lines2 = c.config.getData('unl-path-prefixes')
        self.assertEqual(list(sorted(lines)), list(sorted(lines2)))
        d = g.parsePathData(c)
        if 0:
            print('')
            g.printObj(d)
        return c2
    #@+node:ekr.20230701084035.1: *4* TestGlobals.test_per_commander_data
    def test_per_commander_data(self):

        # Test the data only here.
        self._define_per_commander_data()
        self._test_per_commander_data()
    #@+node:ekr.20230702165813.1: *4* TestGlobals.test_patch_at_data_unl_path_prefixes
    def test_patch_at_data_unl_path_prefixes(self):
        # Test the helper, _patch_at_data_unl_path_prefixes.
        c1 = self.c
        c2 = self._patch_at_data_unl_path_prefixes()
        self.assertTrue(c2)
        self.assertTrue(c1.fileName())
        self.assertTrue(c2.fileName())
        self.assertFalse(c1 == c2)
        self.assertTrue(c1 in g.app.commanders())
        self.assertTrue(c2 in g.app.commanders())
        self.assertTrue(c1.frame in g.app.windowList)
        self.assertTrue(c2.frame in g.app.windowList)
    #@+node:ekr.20230701085717.1: *3* --- legacy tests
    #@+node:ekr.20210905203541.4: *4* TestGlobals.test_g_checkVersion
    def test_g_checkVersion(self):
        # for condition in ('<','<=','>','>='):
        for v1, condition, v2 in (
            ('8.4.12', '>', '8.4.3'),
            ('1', '==', '1.0'),
            ('2', '>', '1'),
            ('1.2', '>', '1'),
            ('2', '>', '1.2.3'),
            ('1.2.3', '<', '2'),
            ('1', '<', '1.1'),
        ):
            assert g.CheckVersion(v1, v2, condition=condition, trace=False)
    #@+node:ekr.20210905203541.5: *4* TestGlobals.test_g_CheckVersionToInt
    def test_g_CheckVersionToInt(self):
        self.assertEqual(g.CheckVersionToInt('12'), 12)
        self.assertEqual(g.CheckVersionToInt('2a5'), 2)
        self.assertEqual(g.CheckVersionToInt('b2'), 0)
    #@+node:ekr.20210905203541.6: *4* TestGlobals.test_g_comment_delims_from_extension
    def test_g_comment_delims_from_extension(self):
        # New in Leo 4.6, set_delims_from_language returns '' instead of None.
        table = (
            ('.c', ('//', '/*', '*/')),
            ('.html', ('', '<!--', '-->')),
            ('.py', ('#', '', '')),
            ('.Globals', ('', '', '')),
        )
        for ext, expected in table:
            result = g.comment_delims_from_extension(ext)
            self.assertEqual(result, expected, msg=repr(ext))
    #@+node:ekr.20210905203541.7: *4* TestGlobals.test_g_convertPythonIndexToRowCol
    def test_g_convertPythonIndexToRowCol(self):
        s1 = 'abc\n\np\nxy'
        table1 = (
            (-1, (0, 0)),  # One too small.
            (0, (0, 0)),
            (1, (0, 1)),
            (2, (0, 2)),
            (3, (0, 3)),  # The newline ends a row.
            (4, (1, 0)),
            (5, (2, 0)),
            (6, (2, 1)),
            (7, (3, 0)),
            (8, (3, 1)),
            (9, (3, 2)),  # One too many.
            (10, (3, 2)),  # Two too many.
        )
        s2 = 'abc\n\np\nxy\n'
        table2 = (
            (9, (3, 2)),
            (10, (4, 0)),  # One too many.
            (11, (4, 0)),  # Two too many.
        )
        s3 = 'ab'  # Test special case.  This was the cause of off-by-one problems.
        table3 = (
            (-1, (0, 0)),  # One too small.
            (0, (0, 0)),
            (1, (0, 1)),
            (2, (0, 2)),  # One too many.
            (3, (0, 2)),  # Two too many.
        )
        for n, s, table in ((1, s1, table1), (2, s2, table2), (3, s3, table3)):
            for i, result in table:
                row, col = g.convertPythonIndexToRowCol(s, i)
                self.assertEqual(row, result[0], msg=f"n: {n}, i: {i}")
                self.assertEqual(col, result[1], msg=f"n: {n}, i: {i}")
    #@+node:ekr.20210905203541.8: *4* TestGlobals.test_g_convertRowColToPythonIndex
    def test_g_convertRowColToPythonIndex(self):
        s1 = 'abc\n\np\nxy'
        s2 = 'abc\n\np\nxy\n'
        table1 = (
            (0, (-1, 0)),  # One too small.
            (0, (0, 0)),
            (1, (0, 1)),
            (2, (0, 2)),
            (3, (0, 3)),  # The newline ends a row.
            (4, (1, 0)),
            (5, (2, 0)),
            (6, (2, 1)),
            (7, (3, 0)),
            (8, (3, 1)),
            (9, (3, 2)),  # One too large.
        )
        table2 = (
            (9, (3, 2)),
            (10, (4, 0)),  # One two many.
        )
        for s, table in ((s1, table1), (s2, table2)):
            for i, data in table:
                row, col = data
                result = g.convertRowColToPythonIndex(s, row, col)
                self.assertEqual(i, result, msg=f"row: {row}, col: {col}, i: {i}")
    #@+node:ekr.20210905203541.9: *4* TestGlobals.test_g_create_temp_file
    def test_g_create_temp_file(self):
        theFile = None
        try:
            theFile, fn = g.create_temp_file()
            assert theFile
            assert isinstance(fn, str)
        finally:
            if theFile:
                theFile.close()
    #@+node:ekr.20210905203541.10: *4* TestGlobals.test_g_ensureLeadingNewlines
    def test_g_ensureLeadingNewlines(self):
        s = ' \n \n\t\naa bc'
        s2 = 'aa bc'
        for i in range(3):
            result = g.ensureLeadingNewlines(s, i)
            val = ('\n' * i) + s2
            self.assertEqual(result, val)
    #@+node:ekr.20210905203541.11: *4* TestGlobals.test_g_ensureTrailingNewlines
    def test_g_ensureTrailingNewlines(self):
        s = 'aa bc \n \n\t\n'
        s2 = 'aa bc'
        for i in range(3):
            result = g.ensureTrailingNewlines(s, i)
            val = s2 + ('\n' * i)
            self.assertEqual(result, val)
    #@+node:ekr.20210905203541.12: *4* TestGlobals.test_g_find_word
    def test_g_find_word(self):
        table = (
            ('abc a bc x', 'bc', 0, 6),
            ('abc a bc x', 'bc', 1, 6),
            ('abc a x', 'bc', 0, -1),
        )
        for s, word, i, expected in table:
            actual = g.find_word(s, word, i)
            self.assertEqual(actual, expected)
    #@+node:ekr.20210905203541.14: *4* TestGlobals.test_g_fullPath
    def test_g_fullPath(self):
        c = self.c
        child = c.rootPosition().insertAfter()
        child.h = '@path abc'
        grand = child.insertAsLastChild()
        grand.h = 'xyz'
        path = g.fullPath(c, grand, simulate=True)
        end = g.os_path_normpath('abc/xyz')
        assert path.endswith(end), repr(path)
    #@+node:ekr.20210905203541.16: *4* TestGlobals.test_g_get_directives_dict
    def test_g_get_directives_dict(self):
        c = self.c
        p = c.p
        # Note: @comment must follow @language.
        p.b = textwrap.dedent("""\
            ATlanguage python
            ATcomment a b c
            ATtabwidth -8
            ATpagewidth 72
            ATencoding utf-8
    """).replace('AT', '@')
        d = g.get_directives_dict(p)
        self.assertEqual(d.get('language'), 'python')
        self.assertEqual(d.get('tabwidth'), '-8')
        self.assertEqual(d.get('pagewidth'), '72')
        self.assertEqual(d.get('encoding'), 'utf-8')
        self.assertEqual(d.get('comment'), 'a b c')
        assert not d.get('path'), d.get('path')
    #@+node:ekr.20210905203541.17: *4* TestGlobals.test_g_getDocString
    def test_g_getDocString(self):
        s1 = 'no docstring'
        s2 = textwrap.dedent('''\
    # comment
    """docstring2."""
    ''')
        s3 = textwrap.dedent('''\
    """docstring3."""
    \'\'\'docstring2.\'\'\'
    ''')
        table = (
            (s1, ''),
            (s2, 'docstring2.'),
            (s3, 'docstring3.'),
        )
        for s, result in table:
            s2 = g.getDocString(s)
            self.assertEqual(s2, result)
    #@+node:ekr.20210905203541.18: *4* TestGlobals.test_g_getLine
    def test_g_getLine(self):
        s = 'a\ncd\n\ne'
        for i, result in (
            (-1, (0, 2)),  # One too few.
            (0, (0, 2)), (1, (0, 2)),
            (2, (2, 5)), (3, (2, 5)), (4, (2, 5)),
            (5, (5, 6)),
            (6, (6, 7)),
            (7, (6, 7)),  # One too many.
        ):
            j, k = g.getLine(s, i)
            self.assertEqual((j, k), result, msg=f"i: {i}, j: {j}, k: {k}")
    #@+node:ekr.20210905203541.20: *4* TestGlobals.test_g_getWord
    def test_g_getWord(self):
        s = 'abc xy_z5 pdq'
        i, j = g.getWord(s, 5)
        self.assertEqual(s[i:j], 'xy_z5')
    #@+node:ekr.20210905203541.21: *4* TestGlobals.test_g_guessExternalEditor
    def test_g_guessExternalEditor(self):
        c = self.c
        val = g.guessExternalEditor(c)
        assert val, 'no val'  # This can be different on different platforms.
    #@+node:ekr.20230221153849.1: *4* TestGlobals.test_g_handleScriptException
    def test_g_handleScriptException(self):

        c = self.c
        table = (
            'test_leoGlobals.py", line',
            'in test_g_handleScriptException',
            'print(1/0)',
            'ZeroDivisionError: division by zero'
        )
        with self.assertRaises(ZeroDivisionError):
            try:
                print(1/0)
            except ZeroDivisionError:
                old_stdout = sys.stdout
                sys.stdout = io.StringIO()
                g.handleScriptException(c, c.p)
                report = sys.stdout.getvalue()
                for s in table:
                    assert s in report, repr(s)
                sys.stdout = old_stdout
                # print(report)
                raise
    #@+node:ekr.20210905203541.23: *4* TestGlobals.test_g_import_module
    def test_g_import_module(self):
        assert g.import_module('leo.core.leoAst')
            # Top-level .py file.
    #@+node:ekr.20210905203541.24: *4* TestGlobals.test_g_isDirective
    def test_g_isDirective(self):
        table = (
            (True, '@language python\n'),
            (True, '@tabwidth -4 #test\n'),
            (True, '@others\n'),
            (True, '    @others\n'),
            (True, '@encoding\n'),
            (False, '@encoding.setter\n'),
            (False, '@encoding("abc")\n'),
            (False, 'encoding = "abc"\n'),
        )
        for expected, s in table:
            result = g.isDirective(s)
            self.assertEqual(expected, bool(result), msg=s)
    #@+node:ekr.20210905203541.25: *4* TestGlobals.test_g_match_word
    def test_g_match_word(self):
        table = (
            (True, 0, 'a', 'a'),
            (False, 0, 'a', 'b'),
            (True, 0, 'a', 'a b'),
            (False, 1, 'a', 'aa b'),  # Tests bug fixed 2017/06/01.
            (False, 1, 'a', '_a b'),
            (False, 0, 'a', 'aw b'),
            (False, 0, 'a', 'a_'),
            (True, 2, 'a', 'b a c'),
            (False, 0, 'a', 'b a c'),
        )
        for data in table:
            expected, i, word, line = data
            got = g.match_word(line + '\n', i, word)
            self.assertEqual(expected, got)
    #@+node:ekr.20230131234527.1: *4* TestGlobals.test_g_objToString
    def test_g_objToString(self):

        #@+<< define s >>
        #@+node:ekr.20230131234637.1: *5* << define s >>
        s = """g.cls()

        def f1():
            g.trace(g.callers(1))
            g.trace(g.callers_list(1))
            f2()

        def f2():
            print('')
            g.trace(g.callers(2))
            g.trace(g.callers_list(2))
            f3()

        def f3():
            print('')
            g.trace(g.callers(2))
            g.trace(g.callers_list(2))
            t = TestClass()
            assert t

        def f4():
            print('')
            g.trace(g.callers())
            g.trace(g.callers_list())

        class TestClass:
            def __init__(self):
                print('')
                g.trace('(TestClass)')
                f4()

        f1()
        """
        #@-<< define s >>
        #@+<< define class TestClass >>
        #@+node:ekr.20230131234648.1: *5* << define class TestClass >>
        class TestClass:

            def test_function(self):
                pass
        #@-<< define class TestClass >>
        table = (
            (s, 'String1'),
            ('This is a test', "String2"),
            ({'a': 1, 'b': 2}, 'Dict'),
            (['one', 'two', 'three'], 'List'),
            (('x', 'y'), 'Tuple'),
            (g.printObj, 'Function'),
            (TestClass, "Class"),
            (TestClass(), "Instance"),
            (TestClass.test_function, 'unbound method'),
            (TestClass().test_function,'bound method')
        )
        for data, tag in table:
            result = g.objToString(data, tag=tag)
            self.assertTrue(tag in result, msg=data)
            self.assertTrue(isinstance(result, str))
            result2 = g.objToString(data)
            self.assertTrue(isinstance(result2, str))
    #@+node:ekr.20230617065929.1: *4* TestGlobals.test_g_OptionsUtils
    def test_g_OptionsUtils(self):

        if any(z in sys.argv for z in ('--cov', '--cov-report')):
            self.skipTest('Running coverage')

        usage = (
    """
    options:
      -h, --help            show this help message and exit
      -b, --black-sentinels write black-compatible sentinel comments
      --diff                use Leo as an external git diff
      --fail-fast           stop unit tests after the first failure
    """)

        # Create the class.
        obsolete_options = [
            '--dock', '--global-docks', '--init-docks', '--no-cache',
            '--no-dock', '--session-restore', '--session-save', '--use-docks',
        ]
        x = g.OptionsUtils(usage, obsolete_options)

        # Test x.compute_valid_options.
        expected_valid_options = [
            '--black-sentinels', '--diff', '--fail-fast', '--help',
            '-?', '-b', '-h',
        ]
        self.assertEqual(x.compute_valid_options(), expected_valid_options)

        # Test x.option_error and x.check_options.
        bad_options = (
            '--listen-to-log=',
            '--load-type=@auto', '--load-type=@clean',
            '--screen-shot', '--screen-shot=', '--screen-shot-',
            '--script=xyzzy.py',
            '--trace','--trace-', 'trace=', '--trace=xxx',
            '--trace-binding', '--trace-binding-', '--trace-binding=',
            '--window-', 'window=',
            '--window-size', '--window-size=', '--window-size=100',
            '--window-spot', '--window-spot=', '--window-spot=50',
            '--yyy',
        )
        old_argv = sys.argv
        old_stdout = sys.stdout
        try:
            sys.stdout = open(os.devnull, 'w')
            for option in obsolete_options:
                sys.argv = ['leo', option]
                x.check_options()
            with self.assertRaises(SystemExit):
                x.option_error('--xyzzy', 'Unknown option')
                x.option_error('-x', 'Unknown option')
            for option in bad_options:
                with self.assertRaises(SystemExit, msg=option):
                    sys.argv = ['leo', option]
                    x.check_options()
        except Exception:
            g.es_exception()
        finally:
            sys.stdout = old_stdout
            sys.argv = old_argv
    #@+node:ekr.20210905203541.26: *4* TestGlobals.test_g_os_path_finalize_join_with_thumb_drive
    def test_g_os_path_finalize_join_with_thumb_drive(self):
        path1 = r'C:\Python32\Lib\site-packages\leo-editor\leo\core'
        path2 = r'\N:Home\PTC_Creo\Creo.wmv'
        path3 = r'N:\Home\PTC_Creo\Creo.wmv'
        path12 = os.path.join(path1, path2)
        path13 = os.path.join(path1, path3)
        if 0:
            print(path12, g.os.path.abspath(path12))
            print(path13, g.os.path.abspath(path13))
    #@+node:ekr.20210905203541.28: *4* TestGlobals.test_g_removeBlankLines
    def test_g_removeBlankLines(self):
        for s, expected in (
            ('a\nb', 'a\nb'),
            ('\n  \n\nb\n', 'b\n'),
            (' \t \n\n  \n c\n\t\n', ' c\n'),
        ):
            result = g.removeBlankLines(s)
            self.assertEqual(result, expected, msg=repr(s))
    #@+node:ekr.20210905203541.30: *4* TestGlobals.test_g_removeLeadingBlankLines
    def test_g_removeLeadingBlankLines(self):
        for s, expected in (
            ('a\nb', 'a\nb'),
            ('\n  \nb\n', 'b\n'),
            (' \t \n\n\n c', ' c'),
        ):
            result = g.removeLeadingBlankLines(s)
            self.assertEqual(result, expected, msg=repr(s))
    #@+node:ekr.20210905203541.31: *4* TestGlobals.test_g_removeTrailing
    def test_g_removeTrailing(self):
        s = 'aa bc \n \n\t\n'
        table = (
            ('\t\n ', 'aa bc'),
            ('abc\t\n ', ''),
            ('c\t\n ', 'aa b'),
        )
        for arg, val in table:
            result = g.removeTrailing(s, arg)
            self.assertEqual(result, val)
    #@+node:ekr.20210905203541.32: *4* TestGlobals.test_g_sanitize_filename
    def test_g_sanitize_filename(self):
        table = (
            ('A25&()', 'A'),  # Non-alpha characters.
            ('B\tc', 'B c'),  # Tabs.
            ('"AB"', "'AB'"),  # Double quotes.
            ('\\/:|<>*:.', '_'),  # Special characters.
            ('_____________', '_'),  # Combining underscores.
            ('A' * 200, 'A' * 128),  # Maximum length.
            ('abc.', 'abc_'),  # Trailing dots.
        )
        for s, expected in table:
            got = g.sanitize_filename(s)
            self.assertEqual(got, expected, msg=repr(s))
    #@+node:ekr.20210905203541.33: *4* TestGlobals.test_g_scanAtHeaderDirectives_header
    def test_g_scanAtHeaderDirectives_header(self):
        c = self.c
        aList = g.get_directives_dict_list(c.p)
        g.scanAtHeaderDirectives(aList)
    #@+node:ekr.20210905203541.35: *4* TestGlobals.test_g_scanAtHeaderDirectives_noheader
    def test_g_scanAtHeaderDirectives_noheader(self):
        c = self.c
        aList = g.get_directives_dict_list(c.p)
        g.scanAtHeaderDirectives(aList)
    #@+node:ekr.20210905203541.36: *4* TestGlobals.test_g_scanAtLineendingDirectives_cr
    def test_g_scanAtLineendingDirectives_cr(self):
        c = self.c
        p = c.p
        p.b = '@lineending cr\n'
        aList = g.get_directives_dict_list(p)
        s = g.scanAtLineendingDirectives(aList)
        self.assertEqual(s, '\r')
    #@+node:ekr.20210905203541.37: *4* TestGlobals.test_g_scanAtLineendingDirectives_crlf
    def test_g_scanAtLineendingDirectives_crlf(self):
        c = self.c
        p = c.p
        p.b = '@lineending crlf\n'
        aList = g.get_directives_dict_list(p)
        s = g.scanAtLineendingDirectives(aList)
        self.assertEqual(s, '\r\n')
    #@+node:ekr.20210905203541.38: *4* TestGlobals.test_g_scanAtLineendingDirectives_lf
    def test_g_scanAtLineendingDirectives_lf(self):
        c = self.c
        p = c.p
        p.b = '@lineending lf\n'
        aList = g.get_directives_dict_list(p)
        s = g.scanAtLineendingDirectives(aList)
        self.assertEqual(s, '\n')
    #@+node:ekr.20210905203541.39: *4* TestGlobals.test_g_scanAtLineendingDirectives_nl
    def test_g_scanAtLineendingDirectives_nl(self):
        c = self.c
        p = c.p
        p.b = '@lineending nl\n'
        aList = g.get_directives_dict_list(p)
        s = g.scanAtLineendingDirectives(aList)
        self.assertEqual(s, '\n')
    #@+node:ekr.20210905203541.40: *4* TestGlobals.test_g_scanAtLineendingDirectives_platform
    def test_g_scanAtLineendingDirectives_platform(self):
        c = self.c
        p = c.p
        p.b = '@lineending platform\n'
        aList = g.get_directives_dict_list(p)
        s = g.scanAtLineendingDirectives(aList)
        if sys.platform.startswith('win'):
            self.assertEqual(s, '\r\n')  # pragma: no cover
        else:
            self.assertEqual(s, '\n')  # pragma: no cover
    #@+node:ekr.20210905203541.42: *4* TestGlobals.test_g_scanAtPagewidthDirectives_40
    def test_g_scanAtPagewidthDirectives_40(self):
        c = self.c
        p = c.p
        p.b = '@pagewidth 40\n'
        aList = g.get_directives_dict_list(p)
        n = g.scanAtPagewidthDirectives(aList)
        self.assertEqual(n, 40)
    #@+node:ekr.20210905203541.41: *4* TestGlobals.test_g_scanAtPagewidthDirectives_minus_40
    def test_g_scanAtPagewidthDirectives_minus_40(self):
        c = self.c
        p = c.p
        p.b = '@pagewidth -40\n'
        aList = g.get_directives_dict_list(p)
        n = g.scanAtPagewidthDirectives(aList)
        # The @pagewidth directive in the parent should control.
        # Depending on how this test is run, the result could be 80 or None.
        assert n in (None, 80), repr(n)
    #@+node:ekr.20210905203541.43: *4* TestGlobals.test_g_scanAtTabwidthDirectives_6
    def test_g_scanAtTabwidthDirectives_6(self):
        c = self.c
        p = c.p
        p.b = '@tabwidth 6\n'
        aList = g.get_directives_dict_list(p)
        n = g.scanAtTabwidthDirectives(aList)
        self.assertEqual(n, 6)
    #@+node:ekr.20210905203541.44: *4* TestGlobals.test_g_scanAtTabwidthDirectives_minus_6
    def test_g_scanAtTabwidthDirectives_minus_6(self):
        c = self.c
        p = c.p
        p.b = '@tabwidth -6\n'
        aList = g.get_directives_dict_list(p)
        n = g.scanAtTabwidthDirectives(aList)
        self.assertEqual(n, -6)
    #@+node:ekr.20210905203541.45: *4* TestGlobals.test_g_scanAtWrapDirectives_nowrap
    def test_g_scanAtWrapDirectives_nowrap(self):
        c = self.c
        p = c.p
        p.b = '@nowrap\n'
        aList = g.get_directives_dict_list(p)
        s = g.scanAtWrapDirectives(aList)
        assert s is False, repr(s)
    #@+node:ekr.20210905203541.46: *4* TestGlobals.test_g_scanAtWrapDirectives_wrap_with_wrap_
    def test_g_scanAtWrapDirectives_wrap_with_wrap_(self):
        c = self.c
        p = c.p
        p.b = '@wrap\n'
        aList = g.get_directives_dict_list(p)
        s = g.scanAtWrapDirectives(aList)
        assert s is True, repr(s)
    #@+node:ekr.20210905203541.47: *4* TestGlobals.test_g_scanAtWrapDirectives_wrap_without_nowrap_
    def test_g_scanAtWrapDirectives_wrap_without_nowrap_(self):
        c = self.c
        aList = g.get_directives_dict_list(c.p)
        s = g.scanAtWrapDirectives(aList)
        assert s is None, repr(s)
    #@+node:ekr.20210905203541.48: *4* TestGlobals.test_g_set_delims_from_language
    def test_g_set_delims_from_language(self):
        table = (
            ('c', ('//', '/*', '*/')),
            ('python', ('#', '', '')),
            ('xxxyyy', ('', '', '')),
        )
        for language, expected in table:
            result = g.set_delims_from_language(language)
            self.assertEqual(result, expected, msg=language)
    #@+node:ekr.20210905203541.49: *4* TestGlobals.test_g_set_delims_from_string
    def test_g_set_delims_from_string(self):
        table = (
            ('c', '@comment // /* */', ('//', '/*', '*/')),
            ('c', '// /* */', ('//', '/*', '*/')),
            ('python', '@comment #', ('#', '', '')),
            ('python', '#', ('#', '', '')),
            ('xxxyyy', '@comment a b c', ('a', 'b', 'c')),
            ('xxxyyy', 'a b c', ('a', 'b', 'c')),
        )
        for language, s, expected in table:
            result = g.set_delims_from_string(s)
            self.assertEqual(result, expected, msg=language)
    #@+node:ekr.20210905203541.50: *4* TestGlobals.test_g_skip_blank_lines
    def test_g_skip_blank_lines(self):
        end = g.skip_blank_lines("", 0)
        self.assertEqual(end, 0)
        end = g.skip_blank_lines(" ", 0)
        self.assertEqual(end, 0)
        end = g.skip_blank_lines("\n", 0)
        self.assertEqual(end, 1)
        end = g.skip_blank_lines(" \n", 0)
        self.assertEqual(end, 2)
        end = g.skip_blank_lines("\n\na\n", 0)
        self.assertEqual(end, 2)
        end = g.skip_blank_lines("\n\n a\n", 0)
        self.assertEqual(end, 2)
    #@+node:ekr.20210905203541.51: *4* TestGlobals.test_g_skip_line
    def test_g_skip_line(self):
        s = 'a\n\nc'
        for i, result in (
            (-1, 2),  # One too few.
            (0, 2), (1, 2),
            (2, 3),
            (3, 4),
            (4, 4),  # One too many.
        ):
            j = g.skip_line(s, i)
            self.assertEqual(j, result, msg=i)
    #@+node:ekr.20210905203541.52: *4* TestGlobals.test_g_skip_to_end_of_line
    def test_g_skip_to_end_of_line(self):
        s = 'a\n\nc'
        for i, result in (
            (-1, 1),  # One too few.
            (0, 1), (1, 1),
            (2, 2),
            (3, 4),
            (4, 4),  # One too many.
        ):
            j = g.skip_to_end_of_line(s, i)
            self.assertEqual(j, result, msg=i)
    #@+node:ekr.20210905203541.53: *4* TestGlobals.test_g_skip_to_start_of_line
    def test_g_skip_to_start_of_line(self):
        s1 = 'a\n\nc'
        table1 = (
            (-1, 0),  # One too few.
            (0, 0), (1, 0),
            (2, 2),
            (3, 3),
            (4, 4),  # One too many.
        )
        s2 = 'a\n'
        table2 = (
            (1, 0),
            (2, 2),
        )  # A special case at end.
        for s, table in ((s1, table1), (s2, table2)):
            for i, result in table:
                j = g.skip_to_start_of_line(s, i)
                self.assertEqual(j, result, msg=i)
    #@+node:ekr.20210905203541.54: *4* TestGlobals.test_g_splitLongFileName
    def test_g_splitLongFileName(self):
        table = (
            r'abcd/xy\pdqabc/aaa.py',
        )
        for s in table:
            g.splitLongFileName(s, limit=3)
    #@+node:ekr.20210905203541.55: *4* TestGlobals.test_g_stripPathCruft
    def test_g_stripPathCruft(self):
        table = (
            (None, None),  # Retain empty paths for warnings.
            ('', ''),
            (g.app.loadDir, g.app.loadDir),
            ('<abc>', 'abc'),
            ('"abc"', 'abc'),
            ("'abc'", 'abc'),
        )
        for path, expected in table:
            result = g.stripPathCruft(path)
            self.assertEqual(result, expected)
    #@+node:ekr.20210905203541.56: *4* TestGlobals.test_g_warnOnReadOnlyFile
    def test_g_warnOnReadOnlyFile(self):
        c = self.c
        fc = c.fileCommands
        path = g.finalize_join(g.app.loadDir, '..', 'test', 'test-read-only.txt')
        if os.path.exists(path):  # pragma: no cover
            os.chmod(path, stat.S_IREAD)
            fc.warnOnReadOnlyFiles(path)
            assert fc.read_only
        else:  # pragma: no cover
            fc.warnOnReadOnlyFiles(path)
    #@+node:ekr.20210901140645.19: *4* TestGlobals.test_getLastTracebackFileAndLineNumber
    def test_getLastTracebackFileAndLineNumber(self):
        fn = ''
        try:
            assert False
        except AssertionError:
            fn, n = g.getLastTracebackFileAndLineNumber()
        self.assertEqual(fn.lower(), __file__.lower())

    #@+node:ekr.20230325055810.1: *3* TestGlobals.test_g_findGnx
    def test_g_findGnx(self):
        c = self.c

        # Define per-commander data.
        self._define_per_commander_data()

        # Test all error messages for all paths.
        for data in self.files_data:  # <@file> <filename>
            kind, relative_path = data
            headline = msg = f"{kind} {relative_path}"
            self._make_tree(c, headline)
            test_p = g.findNodeAnywhere(c, headline)
            self.assertTrue(test_p)
            result2 = g.findGnx(test_p.gnx, c)
            self.assertEqual(result2, test_p, msg=msg)

        # Create the test tree.
        self._make_tree(c, 'Root')
        # Test all positions.
        for p in c.all_positions():
            for gnx in (f"{p.gnx}", f"{p.gnx}::0"):
                self.assertEqual(p, g.findGnx(gnx, c), msg=gnx)
    #@+node:ekr.20230703175743.1: *3* TestGlobals.test_g_findUnl (legacy)
    def test_g_findUnl(self):

        c = self.c

        # Create the test tree.
        self._make_tree(c, 'Root')
        # Test all positions.
        for p in c.all_positions():
            # Plain headlines.
            headlines = list(reversed([z.h for z in p.self_and_parents()]))
            self.assertEqual(p, g.findUnl(headlines, c), msg=','.join(headlines))
            # Headlines with new-style line numbers:
            aList1 = [f"{z}::0" for z in headlines]
            self.assertEqual(p, g.findUnl(aList1, c), msg=','.join(aList1))
            # Headlines with old-style child offsets.
            if 0:  # I don't understand the old-style format!
                aList2 = [f"{z}:0" for z in headlines]
                self.assertEqual(p, g.findUnl(aList2, c), msg=','.join(aList2))
    #@+node:ekr.20230701085746.1: *3* TestGlobals.test_g_isValidUnl
    def test_g_isValidUnl(self):

        for unl in self.valid_unls + self.missing_unls:
            self.assertTrue(g.isValidUnl(unl), msg=unl)
        for unl in self.invalid_unls:
            self.assertFalse(g.isValidUnl(unl), msg=unl)
    #@+node:ekr.20230701171707.1: *3* TestGlobals.test_g_getUNLFilePart
    def test_g_getUNLFilePart(self):

        table = (
            ('unl:' + 'gnx://a.leo#whatever', 'a.leo'),
            ('unl:' + '//b.leo#whatever', 'b.leo'),
            ('file:' + '//c.leo#whatever', 'c.leo'),
            ('//d.leo#whatever', 'd.leo'),
        )
        for unl, expected in table:
            self.assertEqual(expected, g.getUNLFilePart(unl), msg=unl)
    #@+node:ekr.20230701101300.1: *3* TestGlobals.test_g_isValidUrl
    def test_g_isValidUrl(self):

        bad_table = ('@whatever',)
        good_table = (
            'http://leo-editor.github.io/leo-editor/preface.html',
            'https://github.com/leo-editor/leo-editor/issues?q=is%3Aissue+milestone%3A6.6.3+',
        )
        for unl in self.valid_unls + self.missing_unls + good_table:
            self.assertTrue(g.isValidUrl(unl), msg=unl)
        for unl in self.invalid_unls + bad_table:
            self.assertFalse(g.isValidUrl(unl), msg=unl)
    #@+node:ekr.20230701095636.1: *3* TestGlobals.test_g_findAnyUnl
    def test_g_findAnyUnl(self):

        # g.findAnyUnl returns a Position or None.

        ### To do: resolve all valid unls to a real position.

        c = self.c
        self._make_tree(c, root_h='root')

        if 0:  ### Not yet.
            for unl in self.valid_unls + self.missing_unls:
                p = c.rootPosition()
                self.assertEqual(p, g.findAnyUnl(unl, c), msg=unl)

        # Suppress warnings.
        old_stdout = sys.stdout
        try:
            sys.stdout = open(os.devnull, 'w')
            for unl in self.invalid_unls:
                self.assertEqual(None, g.findAnyUnl(unl, c), msg=unl)
        finally:
            sys.stdout = old_stdout
    #@+node:ekr.20230701113123.1: *3* TestGlobals.test_p_get_star_UNL
    def test_p_get_star_UNL(self):

        # Test 11 p.get_*_UNL methods.
        c = self.c
        self._make_tree(c)
        root = c.rootPosition().next()
        p = root.firstChild()

        # Calculate the various kinds of results.
        gnx = p.gnx
        path = '-->'.join([root.h, p.h])
        long_fn = c.fileName()
        short_fn = os.path.basename(c.fileName())

        empty_gnx = 'unl:' + f"gnx://#{gnx}"
        empty_path = 'unl:' + f"gnx://#{path}"
        full_gnx = 'unl:' + f"gnx://{long_fn}#{gnx}"
        full_legacy = 'unl:' + f"//{long_fn}#{path}"
        short_gnx = 'unl:' + f"gnx://{short_fn}#{gnx}"
        short_legacy = 'unl:' + f"//{short_fn}#{path}"
        all_unls = (empty_gnx, empty_path, full_gnx, full_legacy, short_gnx, short_legacy)

        # Pre-test.
        for unl in all_unls:
            self.assertTrue(g.isValidUnl(unl), msg=unl)

        def set_config(kind, full):
            """Set c.config settings from the args."""
            getBool, getString = c.config.getBool, c.config.getString
            c.config.set(p=None, kind='string', name='unl-status-kind', val=kind)
            c.config.set(p=None, kind='bool', name='full-unl-paths', val=full)
            self.assertEqual(full, getBool('full-unl-paths'), msg=full)
            self.assertEqual(kind, getString('unl-status-kind'), msg=kind)

        # Test g.get_UNL and g.get_legacy_UNL.
        expected_get_UNL = {
            'legacy:0': short_gnx,
            'legacy:1': full_gnx,
            'gnx:0': short_gnx,
            'gnx:1': full_gnx,
        }
        expected_get_legacy_UNL = {
            'legacy:0': short_legacy,
            'legacy:1': full_legacy,
            'gnx:0': short_legacy,
            'gnx:1': full_legacy,
        }
        for kind in ('legacy', 'gnx'):
            for full in (True, False):
                set_config(kind, full)
                for d, f in (
                    (expected_get_UNL, p.get_UNL),
                    (expected_get_legacy_UNL, p.get_legacy_UNL),
                ):
                    expected = d[f"{kind}:{str(int(full))}"]
                    self.assertEqual(expected, f(), msg=f"{f.__name__}: kind: {kind} full: {full}")

        # Test all other p.get_*_UNL methods.
        # Their returned values should not depend on settings, but change the settings to make sure.
        for kind in ('legacy', 'gnx'):
            for full in (True, False):
                set_config(kind, full)
                for expected, f in (
                    # Test g.get_full/short_gnx_UNL.
                    (full_gnx, p.get_full_gnx_UNL),
                    (short_gnx, p.get_short_gnx_UNL),
                    # Test g.get_full/short_legacy_UNL.
                    (full_legacy, p.get_full_legacy_UNL),
                    (short_legacy, p.get_short_legacy_UNL),
                ):
                    msg = f"{f.__name__}: kind: {kind} full: {full}"
                    self.assertEqual(expected, f(), msg=msg)
    #@+node:ekr.20230701103509.1: *3* TestGlobals.test_g_parsePathData
    def test_g_parsePathData(self) -> None:

        c = self.c

        # Set @data unl-path-prefixes

        s = textwrap.dedent("""
            # lines have the form:
            # x.leo: <absolute path to x.leo>

            test.leo:    c:/Repos/leo-editor/leo/test
            LeoDocs.leo: c:/Repos/leo-editor/leo/doc
        """)
        lines = g.splitLines(s)
        self._set_setting(c, kind='data', name='unl-path-prefixes', val=lines)
        lines2 = c.config.getData('unl-path-prefixes')
        expected_lines = [
            'test.leo:    c:/Repos/leo-editor/leo/test',
            'LeoDocs.leo: c:/Repos/leo-editor/leo/doc',
        ]
        self.assertEqual(lines2, expected_lines)
        d = g.parsePathData(c)
        paths = ['c:/Repos/leo-editor/leo/test', 'c:/Repos/leo-editor/leo/doc']
        expected_paths = [os.path.normpath(z) for z in paths]
        self.assertEqual(list(sorted(d.values())), list(sorted(expected_paths)))
    #@+node:ekr.20230703175447.1: *3* TestGlobals.test_g_openUNLFile
    def test_g_openUNLFile(self):

        # Create a new commander
        c1 = self.c
        c2 = self._patch_at_data_unl_path_prefixes()
        # Change both filenames.
        file_name1 = os.path.basename(c1.fileName())
        file_name2 = os.path.basename(c2.fileName())
        # Cross-file tests.
        c3 = g.openUNLFile(c1, file_name2)
        self.assertEqual(c3, c2)
        c4 = g.openUNLFile(c2, file_name1)
        self.assertEqual(c4, c1)
    #@-others
#@-others
#@-leo

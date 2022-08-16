# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20210904064440.2: * @file ../unittests/test_importers.py
#@@first
"""Tests of leo/plugins/importers"""
import glob
import importlib
import sys
import textwrap
from leo.core import leoGlobals as g
from leo.core.leoNodes import Position
from leo.core.leoTest2 import LeoUnitTest
import leo.plugins.importers.coffeescript as cs
import leo.plugins.importers.dart as dart
from leo.plugins.importers.javascript import JsLexer
import leo.plugins.importers.linescanner as linescanner
import leo.plugins.importers.markdown as markdown
import leo.plugins.importers.org as org
import leo.plugins.importers.otl as otl
#@+others
#@+node:ekr.20210904064440.3: ** class BaseTestImporter(LeoUnitTest)
class BaseTestImporter(LeoUnitTest):
    """The base class for tests of leoImport.py"""

    ext = None  # Subclasses must set this to the language's extension.
    treeType = '@file'  # Fix #352.

    def setUp(self):
        super().setUp()
        g.app.loadManager.createAllImporterData()

    #@+others
    #@+node:vitalije.20211206180043.1: *3* BaseTestImporter.check_outline (best trace)
    def check_outline(self, p, expected):
        """
        BaseTestImporter.check_outline.
        """
        if 0: # Dump expected results.
            print('')
            g.trace('Expected results...')
            for (level, h, s) in expected:
                g.printObj(g.splitLines(s), tag=f"level: {level} {h}")

        if 0: # Dump headlines of actual results.
            self.dump_headlines(p, tag='Actual headlines...')

        if 0: # Dump actual results, including bodies.
            self.dump_tree(p, tag='Actual results...')

        # Do the actual tests.
        p0_level = p.level()
        actual = [(z.level(), z.h, z.b) for z in p.self_and_subtree()]
        # g.printObj(expected, tag='expected')
        # g.printObj(actual, tag='actual')
        self.assertEqual(len(expected), len(actual))
        for i, actual in enumerate(actual):
            try:
                a_level, a_h, a_str = actual
                e_level, e_h, e_str = expected[i]
            except ValueError:
                g.printObj(actual, tag=f"actual[{i}]")
                g.printObj(expected[i], tag=f"expected[{i}]")
                self.fail(f"Error unpacking tuple {i}")
            msg = f"FAIL in node {i} {e_h}"
            self.assertEqual(a_level - p0_level, e_level, msg=msg)
            if i > 0:  # Don't test top-level headline.
                self.assertEqual(e_h, a_h, msg=msg)
            self.assertEqual(g.splitLines(e_str), g.splitLines(a_str), msg=msg)
        return True, 'ok'

    #@+node:ekr.20220809054555.1: *3* BaseTestImporter.check_round_trip
    def check_round_trip(self, p: Position, s: str, strict_flag: bool=False) -> None:
        """Assert that p's outline is equivalent to s."""
        c = self.c
        result_s = c.atFileCommands.atAutoToString(p)
        if strict_flag:
            s_lines = g.splitLines(s)
            result_lines = g.splitLines(result_s)
        else:
            # Ignore leading whitespace and all blank lines.
            s_lines = [z.lstrip() for z in g.splitLines(s) if z.strip()]
            result_lines = [z.lstrip() for z in g.splitLines(result_s) if z.strip()]
        if s_lines != result_lines:
            g.trace('FAIL', p.h)
            g.printObj(s_lines, tag=f"expected: {p.h}")
            g.printObj(result_lines, tag=f"results: {p.h}")
        self.assertEqual(s_lines, result_lines)
    #@+node:ekr.20211108044605.1: *3* BaseTestImporter.compute_unit_test_kind
    def compute_unit_test_kind(self, ext):
        """Return kind from the given extention."""
        aClass = g.app.classDispatchDict.get(ext)
        kind = {
            '.json': '@auto-json',
            '.md': '@auto-md',
            '.org': '@auto-org',
            '.otl': '@auto-otl',
            '.rst': '@auto-rst',
        }.get(ext)
        if kind:
            return kind
        if aClass:
            d2 = g.app.atAutoDict
            for z in d2:
                if d2.get(z) == aClass:
                    return z  # pragma: no cover
        return '@file'
    #@+node:ekr.20220802054221.1: *3* BaseTestImporter.dedent
    def dedent(self, s):
        """Remove common leading whitespace from all lines of s."""
        return textwrap.dedent(s)
    #@+node:ekr.20220806170537.1: *3* BaseTestImporter.dump_string
    def dump_string(self, s, tag=None):
        if tag:
            print(tag)
        g.printObj([f"{i:2} {z.rstrip()}" for i, z in enumerate(g.splitLines(s))])
    #@+node:ekr.20220805071838.1: *3* BaseTestImporter.dump_headlines
    def dump_headlines(self, root, tag=None):  # pragma: no cover
        """Dump root's tree just as as Importer.dump_tree."""
        print('')
        if tag:
            print(tag)
        for p in root.self_and_subtree():
            print('level:', p.level(), p.h)
    #@+node:ekr.20211129062220.1: *3* BaseTestImporter.dump_tree
    def dump_tree(self, root, tag=None):  # pragma: no cover
        """Dump root's tree just as as Importer.dump_tree."""
        print('')
        if tag:
            print(tag)
        for p in root.self_and_subtree():
            print('')
            print('level:', p.level(), p.h)
            g.printObj(g.splitLines(p.v.b))
    #@+node:ekr.20211127042843.1: *3* BaseTestImporter.run_test
    def run_test(self, s: str, check_flag: bool=True, strict_flag: bool=False) -> Position:
        """
        Run a unit test of an import scanner,
        i.e., create a tree from string s at location p.
        """
        c, ext, p = self.c, self.ext, self.c.p
        self.assertTrue(ext)

        # Run the test.
        parent = p.insertAsLastChild()
        kind = self.compute_unit_test_kind(ext)

        # TestCase.id() has the form leo.unittests.core.file.class.test_name
        id_parts = self.id().split('.')
        self.short_id = f"{id_parts[-2]}.{id_parts[-1]}"
        parent.h = f"{kind} {self.short_id}"

        # createOutline calls Importer.gen_lines and Importer.check.
        test_s = textwrap.dedent(s).strip() + '\n\n'
        c.importCommands.createOutline(parent.copy(), ext, test_s)

        # Some tests will never pass round-trip tests.
        if check_flag:
            self.check_round_trip(parent, test_s, strict_flag)
        return parent
    #@-others
#@+node:ekr.20211108052633.1: ** class TestAtAuto (BaseTestImporter)
class TestAtAuto(BaseTestImporter):

    #@+others
    #@+node:ekr.20210904065459.122: *3* TestAtAuto.test_importers_can_be_imported
    def test_importers_can_be_imported(self):
        path = g.os_path_finalize_join(g.app.loadDir, '..', 'plugins', 'importers')
        assert g.os_path_exists(path), repr(path)
        pattern = g.os_path_finalize_join(path, '*.py')
        for fn in glob.glob(pattern):
            sfn = g.shortFileName(fn)
            m = importlib.import_module('leo.plugins.importers.%s' % sfn[:-3])
            assert m
    #@-others
#@+node:ekr.20211108062025.1: ** class TestC (BaseTestImporter)
class TestC(BaseTestImporter):

    ext = '.c'

    #@+others
    #@+node:ekr.20210904065459.3: *3* TestC.test_c_class_1
    def test_c_class_1(self):

        s = """
            class cTestClass1 {

                int foo (int a) {
                    a = 2 ;
                }

                char bar (float c) {
                    ;
                }
            }
        """
        p = self.run_test(s)
        self.check_outline(p, (
            (0, '',  # check_outline ignores the first headline.
                '@others\n'
                '@language c\n'
                '@tabwidth -4\n'
            ),
            (1, 'class cTestClass1',
                'class cTestClass1 {\n'
                '\n'
                '    @others\n'
                '}\n'
                '\n'
            ),
            (2, 'int foo',
                'int foo (int a) {\n'
                '    a = 2 ;\n'
                '}\n'
                '\n'
            ),
            (2, 'char bar',
                'char bar (float c) {\n'
                '    ;\n'
                '}\n'
            ),
        ))
    #@+node:ekr.20210904065459.4: *3* TestC.test_class_underindented_line
    def test_class_underindented_line(self):

        s = """
            class cTestClass1 {

                int foo (int a) {
            // an underindented line.
                    a = 2 ;
                }

                // This should go with the next function.

                char bar (float c) {
                    ;
                }
            }
        """
        p = self.run_test(s)
        self.check_outline(p, (
            (0, '',  # check_outline ignores the first headline.
                '@others\n'
                '@language c\n'
                '@tabwidth -4\n'
            ),
            (1, 'class cTestClass1',
                'class cTestClass1 {\n'
                '\n'
                '    @others\n'
                '}\n'
                '\n'
            ),
            (2, 'int foo',
                'int foo (int a) {\n'
                '// an underindented line.\n'
                '    a = 2 ;\n'
                '}\n'
                '\n'
            ),
            (2, 'char bar',
                '// This should go with the next function.\n'
                '\n'
                'char bar (float c) {\n'
                '    ;\n'
                '}\n'
            ),
        ))

    #@+node:ekr.20210904065459.5: *3* TestC.test_comment_follows_arg_list
    def test_comment_follows_arg_list(self):

        s = """
            void
            aaa::bbb::doit
                (
                awk* b
                )
            {
                assert(false);
            }

            bool
            aaa::bbb::dothat
                (
                xyz *b
                ) //  <---------------------problem
            {
                return true;
            }
        """
        p = self.run_test(s)
        self.check_outline(p, (
            (0, '',  # check_outline ignores the first headline.
                '@others\n'
                '@language c\n'
                '@tabwidth -4\n'
            ),
            (1, 'void aaa::bbb::doit',
                'void\n'
                'aaa::bbb::doit\n'
                '    (\n'
                '    awk* b\n'
                '    )\n'
                '{\n'
                '    assert(false);\n'
                '}\n'
                '\n'
            ),
            (1, 'bool aaa::bbb::dothat',
                'bool\n'
                'aaa::bbb::dothat\n'
                '    (\n'
                '    xyz *b\n'
                '    ) //  <---------------------problem\n'
                '{\n'
                '    return true;\n'
                '}\n'
                '\n'
            ),
        ))
    #@+node:ekr.20210904065459.6: *3* TestC.test_comment_follows_block_delim
    def test_comment_follows_block_delim(self):

        s = """
            void
            aaa::bbb::doit
                (
                awk* b
                )
            {
                assert(false);
            }

            bool
            aaa::bbb::dothat
                (
                xyz *b
                )
            {
                return true;
            } //  <--------------------- problem
        """
        p = self.run_test(s)
        self.check_outline(p, (
            (0, '',  # check_outline ignores the first headline.
                '@others\n'
                '@language c\n'
                '@tabwidth -4\n'
            ),
            (1, 'void aaa::bbb::doit',
                'void\n'
                'aaa::bbb::doit\n'
                '    (\n'
                '    awk* b\n'
                '    )\n'
                '{\n'
                '    assert(false);\n'
                '}\n'
                '\n'

            ),
            (1, 'bool aaa::bbb::dothat',
                'bool\n'
                'aaa::bbb::dothat\n'
                '    (\n'
                '    xyz *b\n'
                '    )\n'
                '{\n'
                '    return true;\n'
                '} //  <--------------------- problem\n'
                '\n'
            ),
        ))
    #@+node:ekr.20210904065459.10: *3* TestC.test_extern
    def test_extern(self):

        s = """
            extern "C"
            {
            #include "stuff.h"
            void    init(void);
            #include "that.h"
            }
        """
        p = self.run_test(s)
        self.check_outline(p, (
            (0, '',  # check_outline ignores the first headline.
                '@others\n'
                '@language c\n'
                '@tabwidth -4\n'
            ),
            (1, 'extern "C"',
                'extern "C"\n'
                '{\n'
                '#include "stuff.h"\n'
                'void    init(void);\n'
                '#include "that.h"\n'
                '}\n'
                '\n'
            ),
        ))
    #@+node:ekr.20210904065459.8: *3* TestC.test_old_style_decl_1
    def test_old_style_decl_1(self):

        s = """
            static void
            ReleaseCharSet(cset)
                CharSet *cset;
            {
                ckfree((char *)cset->chars);
                if (cset->ranges) {
                ckfree((char *)cset->ranges);
                }
            }
        """
        p = self.run_test(s)
        self.check_outline(p, (
            (0, '',  # check_outline ignores the first headline.
                '@others\n'
                '@language c\n'
                '@tabwidth -4\n'
            ),
            (1, 'static void ReleaseCharSet',
                'static void\n'
                'ReleaseCharSet(cset)\n'
                '    CharSet *cset;\n'
                '{\n'
                '    ckfree((char *)cset->chars);\n'
                '    if (cset->ranges) {\n'
                '    ckfree((char *)cset->ranges);\n'
                '    }\n'
                '}\n'
                '\n'
            ),
        ))
    #@+node:ekr.20210904065459.9: *3* TestC.test_old_style_decl_2
    def test_old_style_decl_2(self):

        s = """
            Tcl_Obj *
            Tcl_NewLongObj(longValue)
                register long longValue; /* Long integer used to initialize the
                     * new object. */
            {
                return Tcl_DbNewLongObj(longValue, "unknown", 0);
            }
        """
        p = self.run_test(s)
        self.check_outline(p, (
            (0, '',  # check_outline ignores the first headline.
                '@others\n'
                '@language c\n'
                '@tabwidth -4\n'
            ),
            (1, 'Tcl_Obj * Tcl_NewLongObj',
                'Tcl_Obj *\n'
                'Tcl_NewLongObj(longValue)\n'
                '    register long longValue; /* Long integer used to initialize the\n'
                '         * new object. */\n'
                '{\n'
                '    return Tcl_DbNewLongObj(longValue, "unknown", 0);\n'
                '}\n'
                '\n'
            ),
        ))
    #@+node:ekr.20220812232648.1: *3* TestC.test_template
    def test_template(self):

        s = """
            template <class T>
            T GetMax (T a, T b) {
              T result;
              result = (a>b)? a : b;
              return (result);
            }
        """
        p = self.run_test(s)
        self.check_outline(p, (
            (0, '',  # check_outline ignores the first headline.
                '@others\n'
                '@language c\n'
                '@tabwidth -4\n'
            ),
            (1, 'template <class T>',
                    'template <class T>\n'
                    'T GetMax (T a, T b) {\n'
                    '  T result;\n'
                    '  result = (a>b)? a : b;\n'
                    '  return (result);\n'
                    '}\n'
                    '\n'
            ),
        ))
    #@-others
#@+node:ekr.20211108063520.1: ** class TestCoffeescript (BaseTextImporter)
class TestCoffeescript(BaseTestImporter):

    ext = '.coffee'

    #@+others
    #@+node:ekr.20210904065459.15: *3* TestCoffeescript.test_1
    def test_1(self):

        s = r'''

        # Js2coffee relies on Narcissus's parser.

        {parser} = @Narcissus or require('./narcissus_packed')

        # Main entry point

        buildCoffee = (str) ->
          str  = str.replace /\r/g, ''
          str += "\n"

          builder    = new Builder
          scriptNode = parser.parse str
        '''
        p = self.run_test(s)
        self.check_outline(p, (
            (0, '',  # check_outline ignores the first headline.
                    "# Js2coffee relies on Narcissus's parser.\n"
                    '\n'
                    "{parser} = @Narcissus or require('./narcissus_packed')\n"
                    '\n'
                    '@others\n'
                    '@language coffeescript\n'
                    '@tabwidth -4\n'
            ),
            (1, 'buildCoffee = (str) ->',
                    '# Main entry point\n'
                    '\n'
                    'buildCoffee = (str) ->\n'
                    "  str  = str.replace /\\r/g, ''\n"
                    '  str += "\\n"\n'
                    '\n'
                    '  builder    = new Builder\n'
                    '  scriptNode = parser.parse str\n'
                    '\n'
            ),
        ))
    #@+node:ekr.20210904065459.16: *3* TestCoffeescript.test_2
    #@@tabwidth -2 # Required

    def test_2(self):

        s = """
          class Builder
            constructor: ->
              @transformer = new Transformer
            # `build()`

            build: (args...) ->
              node = args[0]
              @transform node

              name = 'other'
              name = node.typeName()  if node != undefined and node.typeName

              fn  = (@[name] or @other)
              out = fn.apply(this, args)

              if node.parenthesized then paren(out) else out
            # `transform()`

            transform: (args...) ->
              @transformer.transform.apply(@transformer, args)

            # `body()`

            body: (node, opts={}) ->
              str = @build(node, opts)
              str = blockTrim(str)
              str = unshift(str)
              if str.length > 0 then str else ""
        """
        p = self.run_test(s)
        self.check_outline(p, (
          (0, '',  # check_outline ignores the first headline.
                '@others\n'
                '@language coffeescript\n'
                '@tabwidth -4\n'
          ),
          (1, 'class Builder',
                'class Builder\n'
                '  @others\n'
          ),
          (2, 'constructor: ->',
              'constructor: ->\n'
              '  @transformer = new Transformer\n'
          ),
          (2, 'build: (args...) ->',
                '# `build()`\n'
                '\n'
                'build: (args...) ->\n'
                '  node = args[0]\n'
                '  @transform node\n'
                '\n'
                "  name = 'other'\n"
                '  name = node.typeName()  if node != undefined and node.typeName\n'
                '\n'
                '  fn  = (@[name] or @other)\n'
                '  out = fn.apply(this, args)\n'
                '\n'
                '  if node.parenthesized then paren(out) else out\n'
          ),
          (2, 'transform: (args...) ->',
              '# `transform()`\n'
              '\n'
              'transform: (args...) ->\n'
              '  @transformer.transform.apply(@transformer, args)\n'
              '\n'
          ),
          (2, 'body: (node, opts={}) ->',
              '# `body()`\n'
              '\n'
              'body: (node, opts={}) ->\n'
              '  str = @build(node, opts)\n'
              '  str = blockTrim(str)\n'
              '  str = unshift(str)\n'
              '  if str.length > 0 then str else ""\n'
              '\n'
          ),
        ))
    #@+node:ekr.20211108085023.1: *3* TestCoffeescript.test_get_leading_indent
    def test_get_leading_indent(self):
        c = self.c
        importer = linescanner.Importer(c, language='coffeescript')
        self.assertEqual(importer.single_comment, '#')
    #@+node:ekr.20210904065459.126: *3* TestCoffeescript.test_scan_line
    def test_scan_line(self):
        c = self.c
        x = cs.Coffeescript_Importer(c)
        self.assertEqual(x.single_comment, '#')
    #@-others
#@+node:ekr.20211108062958.1: ** class TestCSharp (BaseTestImporter)
class TestCSharp(BaseTestImporter):

    ext = '.c#'

    #@+others
    #@+node:ekr.20210904065459.12: *3* TestCSharp.test_namespace_indent
    def test_namespace_indent(self):

        s = """
            namespace {
                class cTestClass1 {
                    ;
                }
            }
        """
        p = self.run_test(s)
        self.check_outline(p, (
            (0, '',  # check_outline ignores the first headline.
                    '@others\n'
                    '@language csharp\n'
                    '@tabwidth -4\n'
            ),
            (1, 'namespace',
                    'namespace {\n'
                    '    @others\n'
                    '}\n'
                    '\n'
            ),
            (2, 'class cTestClass1',
                    'class cTestClass1 {\n'
                    '    ;\n'
                    '}\n'
            ),
        ))
    #@+node:ekr.20210904065459.13: *3* TestCSharp.test_namespace_no_indent
    def test_namespace_no_indent(self):

        s = """
            namespace {
            class cTestClass1 {
                ;
            }
            }
        """
        p = self.run_test(s)
        self.check_outline(p, (
            (0, '',  # check_outline ignores the first headline.
                    '@others\n'
                    '@language csharp\n'
                    '@tabwidth -4\n'
            ),
            (1, 'namespace',
                    'namespace {\n'
                    '@others\n'
                    '}\n'
                    '\n'
            ),
            (2, 'class cTestClass1',
                    'class cTestClass1 {\n'
                    '    ;\n'
                    '}\n'
            ),
        ))
    #@-others
#@+node:ekr.20220809160735.1: ** class TestCText (BaseTestImporter)
class TestCText(BaseTestImporter):

    ext = '.ctext'  # A made-up extension for unit tests.

    #@+others
    #@+node:ekr.20220811091538.1: *3* TestCText.test_importer
    def test_importer(self):

        # From the CText_Importer docstring.
        # Note that '#' is the delim for unit tests.
        s = """
        Leading text in root node of subtree

        Etc. etc.

        ### A level one node #####################################

        This would be the text in this level one node.

        And this.

        ### Another level one node ###############################

        Another one

        #### A level 2 node ######################################

        See what we did there - one more '#' - this is a subnode.
        """
        # Round-tripping is not guaranteed.
        p = self.run_test(s, check_flag=False)
        self.check_outline(p, (
            (0, '', # check_outline ignores the first headline.
                    'Leading text in root node of subtree\n'
                    '\n'
                    'Etc. etc.\n'
                    '\n'
            ),
            (1, 'A level one node',
                    '\n'
                    'This would be the text in this level one node.\n'
                    '\n'
                    'And this.\n'
                    '\n'
            ),
            (1, 'Another level one node',
                    '\n'
                    'Another one\n'
                    '\n'
            ),
            (2, 'A level 2 node',
                    '\n'
                    "See what we did there - one more '#' - this is a subnode.\n"
                    '\n'
            ),
        ))


    #@-others
#@+node:ekr.20211108063908.1: ** class TestCython (BaseTestImporter)
class TestCython(BaseTestImporter):

    ext = '.pyx'
    #@+others
    #@+node:ekr.20210904065459.11: *3* TestCython.test_importer
    def test_importer(self):

        s = '''
            from libc.math cimport pow

            cdef double square_and_add (double x):
                """Compute x^2 + x as double.

                This is a cdef function that can be called from within
                a Cython program, but not from Python.
                """
                return pow(x, 2.0) + x

            cpdef print_result (double x):
                """This is a cpdef function that can be called from Python."""
                print("({} ^ 2) + {} = {}".format(x, x, square_and_add(x)))

        '''
        p = self.run_test(s, strict_flag=True)
        self.check_outline(p, (
            (0, '',  # check_outlines ignores the first headline.
                    'from libc.math cimport pow\n'
                    '\n'
                    '@others\n'
                    '@language cython\n'
                    '@tabwidth -4\n'
            ),
            (1, 'cdef double square_and_add',
                    'cdef double square_and_add (double x):\n'
                    '    """Compute x^2 + x as double.\n'
                    '\n'
                    '    This is a cdef function that can be called from within\n'
                    '    a Cython program, but not from Python.\n'
                    '    """\n'
                    '    return pow(x, 2.0) + x\n'
                    '\n'
            ),
            (1, 'cpdef print_result',
                    'cpdef print_result (double x):\n'
                    '    """This is a cpdef function that can be called from Python."""\n'
                    '    print("({} ^ 2) + {} = {}".format(x, x, square_and_add(x)))\n'
                    '\n'
            ),
        ))
    #@-others
#@+node:ekr.20211108064115.1: ** class TestDart (BaseTestImporter)
class TestDart(BaseTestImporter):

    ext = '.dart'

    #@+others
    #@+node:ekr.20210904065459.17: *3* TestDart.test_hello_world
    def test_hello_world(self):

        s = r'''
        var name = 'Bob';

        hello() {
          print('Hello, World!');
        }

        // Define a function.
        printNumber(num aNumber) {
          print('The number is $aNumber.'); // Print to console.
        }

        // This is where the app starts executing.
        void main() {
          var number = 42; // Declare and initialize a variable.
          printNumber(number); // Call a function.
        }
        '''
        p = self.run_test(s)
        self.check_outline(p, (
            (0, '',  # check_outline ignores the first headline.
                    "var name = 'Bob';\n"
                    '\n'
                    '@others\n'
                    '@language dart\n'
                    '@tabwidth -4\n'
            ),
            (1, 'hello',
                    'hello() {\n'
                    "  print('Hello, World!');\n"
                    '}\n'
                    '\n'
            ),
            (1, 'printNumber',
                    '// Define a function.\n'
                    'printNumber(num aNumber) {\n'
                    "  print('The number is $aNumber.'); // Print to console.\n"
                    '}\n'
                    '\n'
            ),
            (1, 'void main',
                    '// This is where the app starts executing.\n'
                    'void main() {\n'
                    '  var number = 42; // Declare and initialize a variable.\n'
                    '  printNumber(number); // Call a function.\n'
                    '}\n'
                    '\n'
            ),
        ))
    #@+node:ekr.20210904065459.127: *3* TestDart.test_compute_headline
    def test_compute_headline(self):
        c = self.c
        x = dart.Dart_Importer(c)
        table = (
            ('func(abc) {', 'func'),
            ('void foo() {', 'void foo'),
        )
        for s, expected in table:
            got = x.compute_headline(s)
            self.assertEqual(got, expected)
    #@-others
#@+node:ekr.20211108065659.1: ** class TestElisp (BaseTestImporter)
class TestElisp(BaseTestImporter):

    ext = '.el'

    #@+others
    #@+node:ekr.20210904065459.18: *3* TestElisp.test_1
    def test_1(self):

        # Add weird assignments for coverage.
        s = """
            ;;; comment
            ;;; continue
            ;;;

            (defun abc (a b)
               (assn a "abc")
               (assn b \\x)
               (+ 1 2 3))

            ; comment re cde
            (defun cde (a b)
               (+ 1 2 3))
        """
        p = self.run_test(s)
        self.check_outline(p, (
            (0, '', # check_outline ignores the first headline.
                    '@others\n'
                    '@language lisp\n'
                    '@tabwidth -4\n'
            ),
            (1, 'defun abc',
                    ';;; comment\n'
                    ';;; continue\n'
                    ';;;\n'
                    '\n'
                    '(defun abc (a b)\n'
                    '   (assn a "abc")\n'
                    '   (assn b \\x)\n'
                    '   (+ 1 2 3))\n'
                    '\n'
            ),
            (1, 'defun cde',
                    '; comment re cde\n'
                    '(defun cde (a b)\n'
                    '   (+ 1 2 3))\n'
                    '\n'
            ),
        ))

    #@-others
#@+node:ekr.20211108064432.1: ** class TestHtml (BaseTestImporter)
class TestHtml(BaseTestImporter):

    ext = '.htm'

    def setUp(self):
        super().setUp()
        c = self.c
        # Simulate @data import-html-tags, with *only* standard tags.
        tags_list = ['html', 'body', 'head', 'div', 'table']
        settingsDict, junk = g.app.loadManager.createDefaultSettingsDicts()
        c.config.settingsDict = settingsDict
        c.config.set(c.p, 'data', 'import-html-tags', tags_list, warn=True)

    #@+others
    #@+node:ekr.20210904065459.19: *3* TestHtml.test_lowercase_tags
    def test_lowercase_tags(self):

        s = """
            <html>
            <head>
                <title>Bodystring</title>
            </head>
            <body class="bodystring">
            <div id='bodydisplay'></div>
            </body>
            </html>
        """
        p = self.run_test(s)
        self.check_outline(p, (
            (0, '',  # check_outline ignores the first headline.
                    '@others\n'
                    '@language html\n'
                    '@tabwidth -4\n'
            ),
            (1, '<html>',
                    '<html>\n'
                    '@others\n'
                    '</html>\n'
                    '\n'
            ),
            (2, '<head>',
                    '<head>\n'
                    '    <title>Bodystring</title>\n'
                    '</head>\n'
            ),
            (2, '<body class="bodystring">',
                    '<body class="bodystring">\n'
                    "<div id='bodydisplay'></div>\n"
                    '</body>\n'
            ),
        ))
    #@+node:ekr.20210904065459.20: *3* TestHtml.test_multiple_tags_on_a_line (poor)
    def test_multiple_tags_on_a_line(self):

        # pylint: disable=line-too-long

        # tags that cause nodes: html, head, body, div, table, nodeA, nodeB
        # NOT: tr, td, tbody, etc.
        s = """
            <html>
            <body>
                <table id="0">
                    <tr valign="top">
                    <td width="619">
                    <table id="2"> <tr valign="top"> <td width="377">
                        <table id="3">
                        <tr>
                        <td width="368">
                        <table id="4">
                            <tbody id="5">
                            <tr valign="top">
                            <td width="550">
                            <table id="6">
                                <tbody id="6">
                                <tr>
                                <td class="blutopgrabot"><a href="href1">Listing Standards</a> | <a href="href2">Fees</a> | <strong>Non-compliant Issuers</strong> | <a href="href3">Form 25 Filings</a> </td>
                                </tr>
                                </tbody>
                            </table>
                            </td>
                            </tr><tr>
                            <td width="100%" colspan="2">
                            <br />
                            </td>
                            </tr>
                            </tbody>
                        </table>
                        </td>
                        </tr>
                    </table>
                    <!-- View First part --> </td> <td width="242"> <!-- View Second part -->
                    <!-- View Second part --> </td> </tr></table>
                <DIV class="webonly">
                    <script src="/scripts/footer.js"></script>
                </DIV>
                </td>
                </tr>
                <script language="JavaScript1.1">var SA_ID="nyse;nyse";</script>
                <script language="JavaScript1.1" src="/scripts/stats/track.js"></script>
                <noscript><img src="/scripts/stats/track.js" height="1" width="1" alt="" border="0"></noscript>
            </body>
            </html>
        """
        p = self.run_test(s)
        # The importer doesn't do a good job.
        self.check_outline(p, (
            (0, '',  # check_outline ignores the first headline.
                    '@others\n'
                    '@language html\n'
                    '@tabwidth -4\n'
            ),
            (1, '<html>',
                    '<html>\n'
                    '@others\n'
            ),
            (2, '<body>',
                    '<body>\n'
                    '    @others\n'
                    '</html>\n'
                    '\n'
            ),
            (3, '<table id="0">',
                    '<table id="0">\n'
                    '    <tr valign="top">\n'
                    '    <td width="619">\n'
                    '    @others\n'
                    '</td>\n'
                    '</tr>\n'
                    '<script language="JavaScript1.1">var SA_ID="nyse;nyse";</script>\n'
                    '<script language="JavaScript1.1" src="/scripts/stats/track.js"></script>\n'
                    '<noscript><img src="/scripts/stats/track.js" height="1" width="1" alt="" border="0"></noscript>\n'
                    '</body>\n'
            ),
            (4, '<table id="2">',
                    '<table id="2"> <tr valign="top"> <td width="377">\n'
                    '@others\n'
                    '<!-- View First part --> </td> <td width="242"> <!-- View Second part -->\n'
                    '<!-- View Second part --> </td> </tr></table>\n'
            ),
            (5, '<table id="3">',
                    '<table id="3">\n'
                    '<tr>\n'
                    '<td width="368">\n'
                    '@others\n'
                    '</td>\n'
                    '</tr>\n'
                    '</table>\n'
            ),
            (6, '<table id="4">',
                    '<table id="4">\n'
                    '<tbody id="5">\n'
                    '<tr valign="top">\n'
                    '<td width="550">\n'
                    '@others\n'
                    '</td>\n'
                    '</tr><tr>\n'
                    '<td width="100%" colspan="2">\n'
                    '<br />\n'
                    '</td>\n'
                    '</tr>\n'
                    '</tbody>\n'
                    '</table>\n'
            ),
            (7, '<table id="6">',
                    '<table id="6">\n'
                    '    <tbody id="6">\n'
                    '    <tr>\n'
                    '    <td class="blutopgrabot"><a href="href1">Listing Standards</a> | <a href="href2">Fees</a> | <strong>Non-compliant Issuers</strong> | <a href="href3">Form 25 Filings</a> </td>\n'
                    '    </tr>\n'
                    '    </tbody>\n'
                    '</table>\n'
            ),
            (4, '<DIV class="webonly">',
                    '<DIV class="webonly">\n'
                    '<script src="/scripts/footer.js"></script>\n'
                    '</DIV>\n'
            ),
        ))
    #@+node:ekr.20210904065459.21: *3* TestHtml.test_multple_node_completed_on_a_line
    def test_multple_node_completed_on_a_line(self):

        s = """
            <!-- tags that start nodes: html,body,head,div,table,nodeA,nodeB -->
            <html><head>headline</head><body>body</body></html>
        """
        p = self.run_test(s)
        self.check_outline(p, (
            (0, '',  # check_outline ignores the first headline.
                    '<!-- tags that start nodes: html,body,head,div,table,nodeA,nodeB -->\n'
                    '<html><head>headline</head><body>body</body></html>\n'
                    '\n'
                    '@language html\n'
                    '@tabwidth -4\n'
            ),
        ))
    #@+node:ekr.20210904065459.22: *3* TestHtml.test_multple_node_starts_on_a_line
    def test_multple_node_starts_on_a_line(self):

        s = '''
            <html>
            <head>headline</head>
            <body>body</body>
            </html>
        '''
        p = self.run_test(s)
        self.check_outline(p, (
            (0, '',  # check_outline ignores the first headline.
                    '@others\n'
                    '@language html\n'
                    '@tabwidth -4\n'
            ),
            (1, '<html>',
                    '<html>\n'
                    '<head>headline</head>\n'
                    '<body>body</body>\n'
                    '</html>\n'
                    '\n'
            ),
        ))
    #@+node:ekr.20210904065459.23: *3* TestHtml.test_underindented_comment
    def test_underindented_comment(self):

        s = r'''
            <td width="550">
            <table cellspacing="0" cellpadding="0" width="600" border="0">
                <td class="blutopgrabot" height="28"></td>

                <!-- The indentation of this element causes the problem. -->
                <table>

            <!--
            <div align="center">
            <iframe src="http://www.amex.com/atamex/regulation/listingStatus/index.jsp"</iframe>
            </div>
            -->

            </table>
            </table>

            <p>Paragraph</p>
            </td>
        '''
        p = self.run_test(s)
        self.check_outline(p, (
            (0, '',  # check_outline ignores the first headline.
                    '<td width="550">\n'
                    '@others\n'
                    '<p>Paragraph</p>\n'
                    '</td>\n'
                    '\n'
                    '@language html\n'
                    '@tabwidth -4\n'
            ),
            (1, '<table cellspacing="0" cellpadding="0" width="600" border="0">',
                    '<table cellspacing="0" cellpadding="0" width="600" border="0">\n'
                    '    <td class="blutopgrabot" height="28"></td>\n'
                    '\n'
                    '    <!-- The indentation of this element causes the problem. -->\n'
                    '    @others\n'
                    '</table>\n'
                    '\n'
            ),
            (2, '<table>',
                    '<table>\n'
                    '\n'
                    '<!--\n'
                    '<div align="center">\n'
                    '<iframe src="http://www.amex.com/atamex/regulation/listingStatus/index.jsp"</iframe>\n'
                    '</div>\n'
                    '-->\n'
                    '\n'
                    '</table>\n'
            ),
        ))
    #@+node:ekr.20210904065459.24: *3* TestHtml.test_uppercase_tags
    def test_uppercase_tags(self):

        s = """
            <HTML>
            <HEAD>
                <title>Bodystring</title>
            </HEAD>
            <BODY class='bodystring'>
            <DIV id='bodydisplay'></DIV>
            </BODY>
            </HTML>
        """
        p = self.run_test(s)
        self.check_outline(p, (
            (0, '',  # check_outline ignores the first headline.
                '@others\n'
                '@language html\n'
                '@tabwidth -4\n'
            ),
            (1, '<HTML>',
                    '<HTML>\n'
                    '@others\n'
                    '</HTML>\n'
                    '\n'
            ),
            (2, '<HEAD>',
                    '<HEAD>\n'
                    '    <title>Bodystring</title>\n'
                    '</HEAD>\n'
            ),
            (2, "<BODY class='bodystring'>",
                    "<BODY class='bodystring'>\n"
                    "<DIV id='bodydisplay'></DIV>\n"
                    '</BODY>\n'
            ),
        ))
    #@+node:ekr.20210904065459.25: *3* TestHtml.test_improperly_nested_tags
    def test_improperly_nested_tags(self):

        s = """
            <body>

            <!-- OOPS: the div and p elements not properly nested.-->
            <!-- OOPS: this table got generated twice. -->

            <p id="P1">
            <div id="D666">Paragraph</p> <!-- P1 -->
            <p id="P2">

            <TABLE id="T666"></TABLE></p> <!-- P2 -->
            </div>
            </p> <!-- orphan -->

            </body>
        """
        p = self.run_test(s)
        self.check_outline(p, (
            (0, '',  # check_outline ignores the first headline.
                    '@others\n'
                    '@language html\n'
                    '@tabwidth -4\n'
            ),
            (1, '<body>',
                    '<body>\n'
                    '\n'
                    '<!-- OOPS: the div and p elements not properly nested.-->\n'
                    '<!-- OOPS: this table got generated twice. -->\n'
                    '\n'
                    '<p id="P1">\n'
                    '@others\n'
                    '</p> <!-- orphan -->\n'
                    '\n'
                    '</body>\n'
                    '\n'
            ),
            (2, '<div id="D666">',
                    '<div id="D666">Paragraph</p> <!-- P1 -->\n'
                    '<p id="P2">\n'
                    '\n'
                    '<TABLE id="T666"></TABLE></p> <!-- P2 -->\n'
                    '</div>\n'
            ),
        ))

    #@+node:ekr.20210904065459.26: *3* TestHtml.test_improperly_terminated_tags
    def test_improperly_terminated_tags(self):

        s = '''
            <html>

            <head>
                <!-- oops: link elements terminated two different ways -->
                <link id="L1">
                <link id="L2">
                <link id="L3" />
                <link id='L4' />

                <title>TITLE</title>

            <!-- oops: missing tags. -->
        '''
        p = self.run_test(s)
        self.check_outline(p, (
            (0, '',  # check_outline ignores the first headline.
                    '@others\n'
                    '@language html\n'
                    '@tabwidth -4\n'
            ),
            (1, '<html>',
                    '<html>\n'
                    '\n'
                    '@others\n'
            ),
            (2, '<head>',
                    '<head>\n'
                    '    <!-- oops: link elements terminated two different ways -->\n'
                    '    <link id="L1">\n'
                    '    <link id="L2">\n'
                    '    <link id="L3" />\n'
                    "    <link id='L4' />\n"
                    '\n'
                    '    <title>TITLE</title>\n'
                    '\n'
                    '<!-- oops: missing tags. -->\n'
                    '\n'
            ),
        ))

    #@+node:ekr.20210904065459.27: *3* TestHtml.test_improperly_terminated_tags2
    def test_improperly_terminated_tags2(self):

        s = '''
            <html>
            <head>
                <!-- oops: link elements terminated two different ways -->
                <link id="L1">
                <link id="L2">
                <link id="L3" />
                <link id='L4' />

                <title>TITLE</title>

            </head>
            </html>
        '''
        p = self.run_test(s)
        self.check_outline(p, (
            (0, '',  # check_outline ignores the first headline.
                '@others\n'
                '@language html\n'
                '@tabwidth -4\n'
            ),
            (1, '<html>',
                '<html>\n'
                '@others\n'
                '</html>\n'
                '\n'
            ),
            (2, '<head>',
                '<head>\n'
                '    <!-- oops: link elements terminated two different ways -->\n'
                '    <link id="L1">\n'
                '    <link id="L2">\n'
                '    <link id="L3" />\n'
                "    <link id='L4' />\n"
                '\n'
                '    <title>TITLE</title>\n'
                '\n'
                '</head>\n'
            ),
        ))

    #@+node:ekr.20210904065459.28: *3* TestHtml.test_brython
    def test_brython(self):

        # https://github.com/leo-editor/leo-editor/issues/479
        s = '''
            <!DOCTYPE html>
            <html>
            <head>
            <script type="text/python3">
            """Code for the header menu"""
            from browser import document as doc
            from browser import html
            import header

            qs_lang,language = header.show()

            doc["content"].html = doc["content_%s" %language].html

            if qs_lang:
                doc["c_%s" %qs_lang].href += "?lang=%s" %qs_lang

            def ch_lang(ev):
                sel = ev.target
                new_lang = sel.options[sel.selectedIndex].value
                doc.location.href = 'index.html?lang=%s' %new_lang

            for elt in doc[html.SELECT]:
                if elt.id.startswith('change_lang_'):
                    doc[elt.id].bind('change',ch_lang)
            </script>

            <script type="text/python3">
            """Code for the clock"""

            import time
            import math
            import datetime

            from browser import document as doc
            import browser.timer

            sin,cos = math.sin,math.cos
            width,height = 250,250 # canvas dimensions
            ray = 100 # clock ray

            def needle(angle,r1,r2,color="#000000"):
                # draw a needle at specified angle in specified color
                # r1 and r2 are percentages of clock ray
                x1 = width/2-ray*cos(angle)*r1
                y1 = height/2-ray*sin(angle)*r1
                x2 = width/2+ray*cos(angle)*r2
                y2 = height/2+ray*sin(angle)*r2
                ctx.beginPath()
                ctx.strokeStyle = color
                ctx.moveTo(x1,y1)
                ctx.lineTo(x2,y2)
                ctx.stroke()

            def set_clock():
                # erase clock
                ctx.beginPath()
                ctx.fillStyle = "#FFF"
                ctx.arc(width/2,height/2,ray*0.89,0,2*math.pi)
                ctx.fill()

                # redraw hours
                show_hours()

                # print day
                now = datetime.datetime.now()
                day = now.day
                ctx.font = "bold 14px Arial"
                ctx.textAlign = "center"
                ctx.textBaseline = "middle"
                ctx.fillStyle="#FFF"
                ctx.fillText(day,width*0.7,height*0.5)

                # draw needles for hour, minute, seconds
                ctx.lineWidth = 3
                hour = now.hour%12 + now.minute/60
                angle = hour*2*math.pi/12 - math.pi/2
                needle(angle,0.05,0.5)
                minute = now.minute
                angle = minute*2*math.pi/60 - math.pi/2
                needle(angle,0.05,0.85)
                ctx.lineWidth = 1
                second = now.second+now.microsecond/1000000
                angle = second*2*math.pi/60 - math.pi/2
                needle(angle,0.05,0.85,"#FF0000") # in red

            def show_hours():
                ctx.beginPath()
                ctx.arc(width/2,height/2,ray*0.05,0,2*math.pi)
                ctx.fillStyle = "#000"
                ctx.fill()
                for i in range(1,13):
                    angle = i*math.pi/6-math.pi/2
                    x3 = width/2+ray*cos(angle)*0.75
                    y3 = height/2+ray*sin(angle)*0.75
                    ctx.font = "20px Arial"
                    ctx.textAlign = "center"
                    ctx.textBaseline = "middle"
                    ctx.fillText(i,x3,y3)
                # cell for day
                ctx.fillStyle = "#000"
                ctx.fillRect(width*0.65,height*0.47,width*0.1,height*0.06)

            canvas = doc["clock"]
            # draw clock border
            if hasattr(canvas,'getContext'):
                ctx = canvas.getContext("2d")
                ctx.beginPath()
                ctx.lineWidth = 10
                ctx.arc(width/2,height/2,ray,0,2*math.pi)
                ctx.stroke()

                for i in range(60):
                    ctx.lineWidth = 1
                    if i%5 == 0:
                        ctx.lineWidth = 3
                    angle = i*2*math.pi/60 - math.pi/3
                    x1 = width/2+ray*cos(angle)
                    y1 = height/2+ray*sin(angle)
                    x2 = width/2+ray*cos(angle)*0.9
                    y2 = height/2+ray*sin(angle)*0.9
                    ctx.beginPath()
                    ctx.moveTo(x1,y1)
                    ctx.lineTo(x2,y2)
                    ctx.stroke()
                browser.timer.set_interval(set_clock,100)
                show_hours()
            else:
                doc['navig_zone'].html = "On Internet Explorer 9 or more, use a Standard rendering engine"
            </script>

            <title>Brython</title>
            <link rel="stylesheet" href="Brython_files/doc_brython.css">
            </head>
            <body onload="brython({debug:1, cache:'none'})">
            </body></html>
        '''
        p = self.run_test(s)
        self.check_outline(p, (
            (0, '',  # check_outline ignores the first headline.
                    '<!DOCTYPE html>\n'
                    '@others\n'
                    '@language html\n'
                    '@tabwidth -4\n'
            ),
            (1, '<html>',
                    '<html>\n'
                    '@others\n'
            ),
            (2, '<head>',
                    '<head>\n'
                    '<script type="text/python3">\n'
                    '"""Code for the header menu"""\n'
                    'from browser import document as doc\n'
                    'from browser import html\n'
                    'import header\n'
                    '\n'
                    'qs_lang,language = header.show()\n'
                    '\n'
                    'doc["content"].html = doc["content_%s" %language].html\n'
                    '\n'
                    'if qs_lang:\n'
                    '    doc["c_%s" %qs_lang].href += "?lang=%s" %qs_lang\n'
                    '\n'
                    'def ch_lang(ev):\n'
                    '    sel = ev.target\n'
                    '    new_lang = sel.options[sel.selectedIndex].value\n'
                    "    doc.location.href = 'index.html?lang=%s' %new_lang\n"
                    '\n'
                    'for elt in doc[html.SELECT]:\n'
                    "    if elt.id.startswith('change_lang_'):\n"
                    "        doc[elt.id].bind('change',ch_lang)\n"
                    '</script>\n'
                    '\n'
                    '<script type="text/python3">\n'
                    '"""Code for the clock"""\n'
                    '\n'
                    'import time\n'
                    'import math\n'
                    'import datetime\n'
                    '\n'
                    'from browser import document as doc\n'
                    'import browser.timer\n'
                    '\n'
                    'sin,cos = math.sin,math.cos\n'
                    'width,height = 250,250 # canvas dimensions\n'
                    'ray = 100 # clock ray\n'
                    '\n'
                    'def needle(angle,r1,r2,color="#000000"):\n'
                    '    # draw a needle at specified angle in specified color\n'
                    '    # r1 and r2 are percentages of clock ray\n'
                    '    x1 = width/2-ray*cos(angle)*r1\n'
                    '    y1 = height/2-ray*sin(angle)*r1\n'
                    '    x2 = width/2+ray*cos(angle)*r2\n'
                    '    y2 = height/2+ray*sin(angle)*r2\n'
                    '    ctx.beginPath()\n'
                    '    ctx.strokeStyle = color\n'
                    '    ctx.moveTo(x1,y1)\n'
                    '    ctx.lineTo(x2,y2)\n'
                    '    ctx.stroke()\n'
                    '\n'
                    'def set_clock():\n'
                    '    # erase clock\n'
                    '    ctx.beginPath()\n'
                    '    ctx.fillStyle = "#FFF"\n'
                    '    ctx.arc(width/2,height/2,ray*0.89,0,2*math.pi)\n'
                    '    ctx.fill()\n'
                    '\n'
                    '    # redraw hours\n'
                    '    show_hours()\n'
                    '\n'
                    '    # print day\n'
                    '    now = datetime.datetime.now()\n'
                    '    day = now.day\n'
                    '    ctx.font = "bold 14px Arial"\n'
                    '    ctx.textAlign = "center"\n'
                    '    ctx.textBaseline = "middle"\n'
                    '    ctx.fillStyle="#FFF"\n'
                    '    ctx.fillText(day,width*0.7,height*0.5)\n'
                    '\n'
                    '    # draw needles for hour, minute, seconds\n'
                    '    ctx.lineWidth = 3\n'
                    '    hour = now.hour%12 + now.minute/60\n'
                    '    angle = hour*2*math.pi/12 - math.pi/2\n'
                    '    needle(angle,0.05,0.5)\n'
                    '    minute = now.minute\n'
                    '    angle = minute*2*math.pi/60 - math.pi/2\n'
                    '    needle(angle,0.05,0.85)\n'
                    '    ctx.lineWidth = 1\n'
                    '    second = now.second+now.microsecond/1000000\n'
                    '    angle = second*2*math.pi/60 - math.pi/2\n'
                    '    needle(angle,0.05,0.85,"#FF0000") # in red\n'
                    '\n'
                    'def show_hours():\n'
                    '    ctx.beginPath()\n'
                    '    ctx.arc(width/2,height/2,ray*0.05,0,2*math.pi)\n'
                    '    ctx.fillStyle = "#000"\n'
                    '    ctx.fill()\n'
                    '    for i in range(1,13):\n'
                    '        angle = i*math.pi/6-math.pi/2\n'
                    '        x3 = width/2+ray*cos(angle)*0.75\n'
                    '        y3 = height/2+ray*sin(angle)*0.75\n'
                    '        ctx.font = "20px Arial"\n'
                    '        ctx.textAlign = "center"\n'
                    '        ctx.textBaseline = "middle"\n'
                    '        ctx.fillText(i,x3,y3)\n'
                    '    # cell for day\n'
                    '    ctx.fillStyle = "#000"\n'
                    '    ctx.fillRect(width*0.65,height*0.47,width*0.1,height*0.06)\n'
                    '\n'
                    'canvas = doc["clock"]\n'
                    '# draw clock border\n'
                    "if hasattr(canvas,'getContext'):\n"
                    '    ctx = canvas.getContext("2d")\n'
                    '    ctx.beginPath()\n'
                    '    ctx.lineWidth = 10\n'
                    '    ctx.arc(width/2,height/2,ray,0,2*math.pi)\n'
                    '    ctx.stroke()\n'
                    '\n'
                    '    for i in range(60):\n'
                    '        ctx.lineWidth = 1\n'
                    '        if i%5 == 0:\n'
                    '            ctx.lineWidth = 3\n'
                    '        angle = i*2*math.pi/60 - math.pi/3\n'
                    '        x1 = width/2+ray*cos(angle)\n'
                    '        y1 = height/2+ray*sin(angle)\n'
                    '        x2 = width/2+ray*cos(angle)*0.9\n'
                    '        y2 = height/2+ray*sin(angle)*0.9\n'
                    '        ctx.beginPath()\n'
                    '        ctx.moveTo(x1,y1)\n'
                    '        ctx.lineTo(x2,y2)\n'
                    '        ctx.stroke()\n'
                    '    browser.timer.set_interval(set_clock,100)\n'
                    '    show_hours()\n'
                    'else:\n'
                    '    doc[\'navig_zone\'].html = "On Internet Explorer 9 or more, use a Standard rendering engine"\n'
                    '</script>\n'
                    '\n'
                    '<title>Brython</title>\n'
                    '<link rel="stylesheet" href="Brython_files/doc_brython.css">\n'
                    '</head>\n'
            ),
            (2, '<body onload="brython({debug:1, cache:\'none\'})">',
                    '<body onload="brython({debug:1, cache:\'none\'})">\n'
                    '</body></html>\n'
                    '\n'
            ),
        ))
    #@-others
#@+node:ekr.20211108062617.1: ** class TestIni (BaseTestImporter)
class TestIni(BaseTestImporter):

    ext = '.ini'

    #@+others
    #@+node:ekr.20220813054952.1: *3* TestIni.test_1
    def test_1(self):
        # This is just a coverage test for the importer.
        s = """
                ATlanguage ini
                # Config file for mypy

                # Note: Do not put comments after settings.

                [mypy]
                python_version = 3.9
                ignore_missing_imports  = True
                incremental = True
                # cache_dir=nul
                cache_dir = mypy_stubs
                show_error_codes = True
                check_untyped_defs = True
                strict_optional = False
                disable_error_code=attr-defined

                # For v0.931, per https://github.com/python/mypy/issues/11936

                exclude =

                    # The first line must *not* start with |.
                    # Thereafter, each line *must* start with |.
                    # No trailing '|' on last entry!

                    # Directories...
                    doc/|dist/|editpane/|examples/|extensions/|external/|modes/|obsolete/|scripts/|themes/|unittests/|www/|


                # Settings for particular files...

                # Core files that should be fully annotated...
                [mypy-leo.core.leoGlobals,leo.core.leoNodes,leo.core.leoAst,leo.core.leoBackground]
                disallow_untyped_defs = True
                disallow_incomplete_defs = False

                # Importer and writer plugins should be fully annotated...
                [mypy-leo.plugins.importers.*,leo.plugins.writers.*]
                disallow_untyped_defs = True
                disallow_incomplete_defs = True

                # mypy generates lots of useless errors for leoQt.py
                [mypy-leo.core.leoQt,leo.core.leoQt5,leo.core.leoQt6]
                follow_imports = skip
                ignore_missing_imports  = True

                # don't require annotations for leo/modes
                [mypy-leo.modes]
                follow_imports = skip
                ignore_missing_imports  = True
                disallow_untyped_defs = False
                disallow_incomplete_defs = False

        """.replace('AT', '@')
        self.run_test(s, check_flag=False)
    #@-others
#@+node:ekr.20211108065916.1: ** class TestJava (BaseTestImporter)
class TestJava(BaseTestImporter):

    ext = '.java'

    #@+others
    #@+node:ekr.20210904065459.30: *3* TestJava.test_from_AdminPermission_java
    def test_from_AdminPermission_java(self):

        s = """
            /**
             * Indicates the caller's authority to perform lifecycle operations on
             */

            public final class AdminPermission extends BasicPermission
            {
                /**
                 * Creates a new <tt>AdminPermission</tt> object.
                 */
                public AdminPermission()
                {
                    super("AdminPermission");
                }
            }
        """
        p = self.run_test(s)
        self.check_outline(p, (
            (0, '',  # check_outline does not check the first outline.
                    '/**\n'
                    " * Indicates the caller's authority to perform lifecycle operations on\n"
                    ' */\n'
                    '\n'
                    '@others\n'
                    '@language java\n'
                    '@tabwidth -4\n'
            ),
            (1, 'public final class AdminPermission extends BasicPermission',
                    'public final class AdminPermission extends BasicPermission\n'
                    '{\n'
                    '    /**\n'
                    '     * Creates a new <tt>AdminPermission</tt> object.\n'
                    '     */\n'
                    '    @others\n'
                    '}\n'
                    '\n'
            ),
            (2, 'public AdminPermission',
                    'public AdminPermission()\n'
                    '{\n'
                    '    super("AdminPermission");\n'
                    '}\n'
            ),
        ))
    #@+node:ekr.20210904065459.31: *3* TestJava.test_from_BundleException_java
    def test_from_BundleException_java(self):

        s = """
            /*
             * $Header: /cvs/leo/test/unitTest.leo,v 1.247 2008/02/14 14:59:04 edream Exp $
             *
             * Copyright (c) OSGi Alliance (2000, 2005). All Rights Reserved.
             *
             * This program and the accompanying materials are made available under the
             * terms of the Eclipse Public License v1.0 which accompanies this
             * distribution, and is available at http://www.eclipse.org/legal/epl-v10.html.
             */

            package org.osgi.framework;

            /**
             * A Framework exception used to indicate that a bundle lifecycle problem
             * occurred.
             *
             * <p>
             * <code>BundleException</code> object is created by the Framework to denote
             * an exception condition in the lifecycle of a bundle.
             * <code>BundleException</code>s should not be created by bundle developers.
             *
             * <p>
             * This exception is updated to conform to the general purpose exception
             * chaining mechanism.
             *
             * @version $Revision: 1.247 $
             */

            public class BundleException extends Exception {
                static final long serialVersionUID = 3571095144220455665L;
                /**
                 * Nested exception.
                 */
                private Throwable cause;

                /**
                 * Creates a <code>BundleException</code> that wraps another exception.
                 *
                 * @param msg The associated message.
                 * @param cause The cause of this exception.
                 */
                public BundleException(String msg, Throwable cause) {
                    super(msg);
                    this.cause = cause;
                }
            }

        """
        p = self.run_test(s)
        self.check_outline(p, (
            (0, '',  # check_outline does not check the first outline.
                    '/*\n'
                    ' * $Header: /cvs/leo/test/unitTest.leo,v 1.247 2008/02/14 14:59:04 edream Exp $\n'
                    ' *\n'
                    ' * Copyright (c) OSGi Alliance (2000, 2005). All Rights Reserved.\n'
                    ' *\n'
                    ' * This program and the accompanying materials are made available under the\n'
                    ' * terms of the Eclipse Public License v1.0 which accompanies this\n'
                    ' * distribution, and is available at http://www.eclipse.org/legal/epl-v10.html.\n'
                    ' */\n'
                    '\n'
                    'package org.osgi.framework;\n'
                    '\n'
                    '/**\n'
                    ' * A Framework exception used to indicate that a bundle lifecycle problem\n'
                    ' * occurred.\n'
                    ' *\n'
                    ' * <p>\n'
                    ' * <code>BundleException</code> object is created by the Framework to denote\n'
                    ' * an exception condition in the lifecycle of a bundle.\n'
                    ' * <code>BundleException</code>s should not be created by bundle developers.\n'
                    ' *\n'
                    ' * <p>\n'
                    ' * This exception is updated to conform to the general purpose exception\n'
                    ' * chaining mechanism.\n'
                    ' *\n'
                    ' * @version $Revision: 1.247 $\n'
                    ' */\n'
                    '\n'
                    '@others\n'
                    '@language java\n'
                    '@tabwidth -4\n'
            ),
            (1, 'public class BundleException extends Exception',
                    'public class BundleException extends Exception {\n'
                    '    static final long serialVersionUID = 3571095144220455665L;\n'
                    '    /**\n'
                    '     * Nested exception.\n'
                    '     */\n'
                    '    private Throwable cause;\n'
                    '\n'
                    '    /**\n'
                    '     * Creates a <code>BundleException</code> that wraps another exception.\n'
                    '     *\n'
                    '     * @param msg The associated message.\n'
                    '     * @param cause The cause of this exception.\n'
                    '     */\n'
                    '    @others\n'
                    '}\n'
                    '\n'
            ),
            (2, 'public BundleException',
                    'public BundleException(String msg, Throwable cause) {\n'
                    '    super(msg);\n'
                    '    this.cause = cause;\n'
                    '}\n'
            ),
        ))
    #@+node:ekr.20210904065459.32: *3* TestJava.test_interface_test1
    def test_interface_test1(self):

        s = """
            interface Bicycle {
                void changeCadence(int newValue);
                void changeGear(int newValue);
            }
        """
        p = self.run_test(s)
        self.check_outline(p, (
            (0, '',  # check_outline does not check the first outline.
                '@others\n'
                '@language java\n'
                '@tabwidth -4\n'
            ),
            (1, 'interface Bicycle',
                'interface Bicycle {\n'
                '    void changeCadence(int newValue);\n'
                '    void changeGear(int newValue);\n'
                '}\n'
                '\n'
            ),
        ))
    #@+node:ekr.20210904065459.33: *3* TestJava.test_interface_test2
    def test_interface_test2(self):

        s = """
            interface Bicycle {
            void changeCadence(int newValue);
            void changeGear(int newValue);
            }
        """
        p = self.run_test(s)
        self.check_outline(p, (
            (0, '',  # check_outline ignores the first headline.
                    '@others\n'
                    '@language java\n'
                    '@tabwidth -4\n'
            ),
            (1, 'interface Bicycle',
                    'interface Bicycle {\n'
                    'void changeCadence(int newValue);\n'
                    'void changeGear(int newValue);\n'
                    '}\n'
                    '\n'
            ),
        ))
    #@-others
#@+node:ekr.20211108070310.1: ** class TestJavascript (BaseTestImporter)
class TestJavascript(BaseTestImporter):

    ext = '.js'

    #@+others
    #@+node:ekr.20210904065459.35: *3* TestJavascript.test_3
    def test_3(self):

        s = """
            // Restarting
            function restart()
            {
                invokeParamifier(params,"onstart");
                if(story.isEmpty()) {
                    var tiddlers = store.filterTiddlers(store.getTiddlerText("DefaultTiddlers"));
                    for(var t=0; t<tiddlers.length; t++) {
                        story.displayTiddler("bottom",tiddlers[t].title);
                    }
                }
                window.scrollTo(0,0);
            }
        """
        self.run_test(s)
    #@+node:ekr.20210904065459.36: *3* TestJavascript.test_4
    def test_4(self):

        s = """
            var c3 = (function () {
                "use strict";

                // Globals
                var c3 = { version: "0.0.1"   };

                c3.someFunction = function () {
                    console.log("Just a demo...");
                };

                return c3;
            }());
        """
        self.run_test(s)
    #@+node:ekr.20210904065459.37: *3* TestJavascript.test_5
    def test_5(self):

        s = """
            var express = require('express');

            var app = express.createServer(express.logger());

            app.get('/', function(request, response) {
            response.send('Hello World!');
            });

            var port = process.env.PORT || 5000;
            app.listen(port, function() {
            console.log("Listening on " + port);
            });
        """
        self.run_test(s)
    #@+node:ekr.20210904065459.39: *3* TestJavascript.test_639_acid_test_1
    def test_639_acid_test_1(self):

        s = """
            // Acid test for #639: https://github.com/leo-editor/leo-editor/issues/639
            require([
                'jquery',
            ], function(
                    $,
                    termjs,
            ){
                var header = $("#header")[0];
                function calculate_size() {
                    var height = $(window).height() - header.offsetHeight;
                }
                page.show_header();
                window.onresize = function() {
                  terminal.socket.send(JSON.stringify([
                        "set_size", geom.rows, geom.cols,
                        $(window).height(), $(window).width()])
                    );
                };
                window.terminal = terminal;
            });
        """
        self.run_test(s)
    #@+node:ekr.20210904065459.40: *3* TestJavascript.test_639_acid_test_2
    def test_639_acid_test_2(self):

        s = """
            // Acid test for #639: https://github.com/leo-editor/leo-editor/issues/639
            require([
                'jquery',
            ], function(
                    $,
                    termjs,
            ){
                var head = "head"
                function f1() {
                    var head1 = "head1"
                    function f11 () {
                        var v11 ="v1.1"
                    }
                    var middle1 = "middle1"
                    function f12 () {
                        var v12 ="v1.2"
                    }
                    var tail1 = "tail1"
                }
                var middle = "middle"
                function f2() {
                    var head2 = "head2"
                    function f21 () {
                        var v21 ="2.1"
                    }
                    var middle2 = "middle2"
                    function f22 () {
                        var v22 = "2.2.1"
                    }
                    var tail2 = "tail2"
                }
                var tail = "tail"
            });
        """
        self.run_test(s)
    #@+node:ekr.20210904065459.38: *3* TestJavascript.test_639_many_top_level_nodes
    def test_639_many_top_level_nodes(self):

        s = """
            // Easy test for #639: https://github.com/leo-editor/leo-editor/issues/639

            //=============================================================================
            // rpg_core.js v1.3.0
            //=============================================================================

            //-----------------------------------------------------------------------------
            /**
             * This is not a class, but contains some methods that will be added to the
             * standard Javascript objects.
             *
             * @class JsExtensions
             */
            function JsExtensions() {
                throw new Error('This is not a class');
            }

            /**
             * Returns a number whose value is limited to the given range.
             *
             * @method Number.prototype.clamp
             * @param {Number} min The lower boundary
             * @param {Number} max The upper boundary
             * @return {Number} A number in the range (min, max)
             */
            Number.prototype.clamp = function(min, max) {
                return Math.min(Math.max(this, min), max);
            };
        """
        self.run_test(s)
    #@+node:ekr.20220814014851.1: *3* TestJavascript.test_comments
    def test_comments(self):

        s = """
            /* Test of multi-line comments.
             * line 2.
             */
        """
        self.run_test(s)
    #@+node:ekr.20200202104932.1: *3* TestJavascript.test_JsLex
    def test_JsLex(self):

        table = (
            ('id', ('f_', '$', 'A1', 'abc')),
            ('other', ('ÁÁ',)),  # Unicode strings are not handled by JsLex.
            ('keyword', ('async', 'await', 'if')),
            ('punct', ('(', ')', '{', '}', ',', ':', ';')),
            # ('num', ('9', '2')),  # This test doesn't matter at present.
        )
        for kind, data in table:
            for contents in data:
                for name, tok in JsLexer().lex(contents):
                    assert name == kind, f"expected {kind!s} got {name!s} {tok!r} {contents}"
                    # print(f"{kind!s:10} {tok!r:10}")

    #@+node:ekr.20210904065459.34: *3* TestJavascript.test_regex_1
    def test_regex_1(self):

        s = """
            String.prototype.toJSONString = function()
            {
                if(/["\\\\\\x00-\\x1f]/.test(this))
                    return '"' + this.replace(/([\\x00-\\x1f\\"])/g,replaceFn) + '"';

                return '"' + this + '"';
            };
        """
        self.run_test(s)
    #@-others
#@+node:ekr.20220816082603.1: ** class TestLua (BaseTestImporter)
class TestLua (BaseTestImporter):

    ext = '.lua'

    #@+others
    #@+node:ekr.20220816082722.1: *3* TestLua.test_1
    def test_lua_1(self):

        s = """
             function foo (a)
               print("foo", a)
               return coroutine.yield(2*a)
             end

             co = coroutine.create(function (a,b)
                   print("co-body", a, b)
                   local r = foo(a+1)
                   print("co-body", r)
                   local r, s = coroutine.yield(a+b, a-b)
                   print("co-body", r, s)
                   return b, "end"
             end)

             print("main", coroutine.resume(co, 1, 10))
             print("main", coroutine.resume(co, "r"))
             print("main", coroutine.resume(co, "x", "y"))
             print("main", coroutine.resume(co, "x", "y"))
        """
        p = self.run_test(s)
        self.check_outline(p, (
            (0, '', # check_outline ignores the first headline'
                    '@others\n'
                    'end)\n'
                    '\n'
                    'print("main", coroutine.resume(co, 1, 10))\n'
                    'print("main", coroutine.resume(co, "r"))\n'
                    'print("main", coroutine.resume(co, "x", "y"))\n'
                    'print("main", coroutine.resume(co, "x", "y"))\n'
                    '\n'
                    '@language lua\n'
                    '@tabwidth -4\n'
            ),
            (1, 'foo',
                    'function foo (a)\n'
                    '  print("foo", a)\n'
                    '  return coroutine.yield(2*a)\n'
                    'end\n'
                    '\n'
            ),
            (1, 'co = coroutine.create',
                    'co = coroutine.create(function (a,b)\n'
                    '      print("co-body", a, b)\n'
                    '      local r = foo(a+1)\n'
                    '      print("co-body", r)\n'
                    '      local r, s = coroutine.yield(a+b, a-b)\n'
                    '      print("co-body", r, s)\n'
                    '      return b, "end"\n'
            ),
        ))
    #@-others
#@+node:ekr.20211108043230.1: ** class TestMarkdown (BaseTestImporter)
class TestMarkdown(BaseTestImporter):

    ext = '.md'
    treeType = '@auto-md'

    #@+others
    #@+node:ekr.20210904065459.109: *3* TestMarkdown.test_md_import
    def test_md_import(self):

        s = """\
            #Top
            The top section

            ##Section 1
            section 1, line 1
            section 1, line 2

            ##Section 2
            section 2, line 1

            ###Section 2.1
            section 2.1, line 1

            ####Section 2.1.1
            section 2.2.1 line 1
            The next section is empty. It must not be deleted.

            ###Section 2.2

            ##Section 3
            Section 3, line 1
        """
        p = self.run_test(s)
        # A hack, to simulate an unexpected line in the root node.
        # Alas, this does not affect coverage testing.
        p.b = 'line in root node\n' + p.b
        self.check_outline(p, (
            (0, '',  # check_outlines ignores the first headline.
                    'line in root node\n'
                    '@language md\n'
                    '@tabwidth -4\n'
            ),
            (1, 'Top', 'The top section\n\n'),
            (2, 'Section 1',
                    'section 1, line 1\n'
                    'section 1, line 2\n'
                    '\n'
            ),
            (2, 'Section 2',
                    'section 2, line 1\n'
                    '\n'
            ),
            (3, 'Section 2.1',
                    'section 2.1, line 1\n'
                    '\n'
            ),
            (4, 'Section 2.1.1',
                    'section 2.2.1 line 1\n'
                    'The next section is empty. It must not be deleted.\n'
                    '\n'
            ),
            (3, 'Section 2.2',
                    '\n'
            ),
            (2, 'Section 3',
                    'Section 3, line 1\n'
                    '\n'
            ),
        ))
    #@+node:ekr.20210904065459.110: *3* TestMarkdown.test_md_import_rst_style
    def test_md_import_rst_style(self):

        s = """\
            Top
            ====

            The top section

            Section 1
            ---------

            section 1, line 1
            -- Not an underline
            secttion 1, line 2

            Section 2
            ---------

            section 2, line 1

            ###Section 2.1

            section 2.1, line 1

            ####Section 2.1.1

            section 2.2.1 line 1

            ###Section 2.2
            section 2.2, line 1.

            Section 3
            ---------

            section 3, line 1
        """
        p = self.run_test(s, check_flag=False)  # Perfect import is impossible.
        self.check_outline(p, (
            (0, '',  # check_outline ignores the first headline.
                '@language md\n'
                '@tabwidth -4\n'
            ),
            (1, 'Top',
                '\n'
                'The top section\n'
                '\n'
            ),
            (2, 'Section 1',
                '\n'
                'section 1, line 1\n'
                '-- Not an underline\n'
                'secttion 1, line 2\n'
                '\n'
            ),
            (2, 'Section 2',
                '\n'
                'section 2, line 1\n'
                '\n'
            ),
            (3, 'Section 2.1',
                '\n'
                'section 2.1, line 1\n'
                '\n'
            ),
            (4, 'Section 2.1.1',
                '\n'
                'section 2.2.1 line 1\n'
                '\n'
            ),
            (3, 'Section 2.2',
                'section 2.2, line 1.\n'
                '\n'
            ),
            (2, 'Section 3',
                '\n'
                'section 3, line 1\n'
                '\n'
            ),
        ))
    #@+node:ekr.20210904065459.111: *3* TestMarkdown.test_markdown_importer_basic
    def test_markdown_importer_basic(self):

        # insert test for markdown here.
        s = """
            Decl line.
            #Header

            After header text

            ##Subheader

            Not an underline

            ----------------

            After subheader text

            #Last header: no text
        """
        p = self.run_test(s)
        self.check_outline(p, (
            (0, '',  # check_outline ignores the first headline.
                '@language md\n'
                '@tabwidth -4\n'
            ),
            (1, '!Declarations',
                'Decl line.\n'
            ),
            (1, 'Header',
                '\n'
                'After header text\n'
                '\n'
            ),
            (2, 'Subheader',
                '\n'
                'Not an underline\n'
                '\n'
                '----------------\n'
                '\n'
                'After subheader text\n'
                '\n'
            ),
            (1, 'Last header: no text',
                '\n'
            ),
        ))
    #@+node:ekr.20210904065459.112: *3* TestMarkdown.test_markdown_importer_implicit_section
    def test_markdown_importer_implicit_section(self):

        s = """
            Decl line.
            #Header

            After header text

            ##Subheader

            Not an underline

            ----------------

            This *should* be a section
            ==========================

            After subheader text

            #Last header: no text
        """
        p = self.run_test(s, check_flag=False)  # Perfect import is impossible.
        self.check_outline(p, (
            (0, '',  # check_outline ignores the first headline.
                '@language md\n'
                '@tabwidth -4\n'
            ),
            (1, '!Declarations',
                'Decl line.\n'
            ),
            (1, 'Header',
                '\n'
                'After header text\n'
                '\n'
            ),
            (2, 'Subheader',
                '\n'
                'Not an underline\n'
                '\n'
                '----------------\n'
                '\n'
            ),
            (1, 'This *should* be a section',
                '\n'
                'After subheader text\n'
                '\n'
            ),
            (1, 'Last header: no text',
                '\n'
            ),
        ))
    #@+node:ekr.20210904065459.114: *3* TestMarkdown.test_markdown_github_syntax
    def test_markdown_github_syntax(self):

        s = """
            Decl line.
            #Header

            ```python
            loads.init = {
                Chloride: 11.5,
                TotalP: 0.002,
            }
            ```
            #Last header
        """
        p = self.run_test(s)
        self.check_outline(p, (
            (0, '',  # check_outline ignores the first headline.
                '@language md\n'
                '@tabwidth -4\n'
            ),
            (1, '!Declarations',
                'Decl line.\n'
            ),
            (1, 'Header',
                '\n'
                '```python\n'
                'loads.init = {\n'
                '    Chloride: 11.5,\n'
                '    TotalP: 0.002,\n'
                '}\n'
                '```\n'
            ),
            (1, 'Last header',
                '\n'
            ),
        ))
    #@+node:ekr.20210904065459.128: *3* TestMarkdown.test_is_hash
    def test_is_hash(self):
        c = self.c
        x = markdown.Markdown_Importer(c)
        assert x.md_pattern_table
        table = (
            (1, 'name', '# name\n'),
            (2, 'a test', '## a test\n'),
            (3, 'a test', '### a test\n'),
        )
        for data in table:
            level, name, line = data
            level2, name2 = x.is_hash(line)
            self.assertEqual(level, level2)
            self.assertEqual(name, name2)
        level3, name = x.is_hash('Not a hash')
        assert level3 is None
        assert name is None
    #@+node:ekr.20210904065459.129: *3* TestMarkdown.test_is_underline
    def test_is_underline(self):
        c = self.c
        x = markdown.Markdown_Importer(c)
        for line in ('----\n', '-----\n', '====\n', '====\n'):
            got = x.is_underline(line)
            assert got, repr(line)
        for line in ('-\n', '--\n', '---\n', '==\n', '===\n', '===\n', '==-==\n', 'abc\n'):
            got = x.is_underline(line)
            assert not got, repr(line)
    #@-others
#@+node:ekr.20211108080955.1: ** class TestOrg (BaseTestImporter)
class TestOrg(BaseTestImporter):

    ext = '.org'
    treeType = '@auto-org'

    #@+others
    #@+node:ekr.20210904065459.42: *3* TestOrg.test_1
    def test_1(self):

        s = """
            * Section 1
            Sec 1.
            * Section 2
            Sec 2.
            ** Section 2-1
            Sec 2.1
            *** Section 2-1-1
            Sec 2.1.1
            * Section 3
            ** Section 3.1
            Sec 3.1
        """
        p = self.run_test(s)
        self.check_outline(p, (
            (0, '',  # check_outline ignores the first headline.
                '@language org\n'
                '@tabwidth -4\n'
            ),
            (1, 'Section 1',
                    'Sec 1.\n'
            ),
            (1, 'Section 2',
                    'Sec 2.\n'
            ),
            (2, 'Section 2-1',
                    'Sec 2.1\n'
            ),
            (3, 'Section 2-1-1',
                    'Sec 2.1.1\n'
            ),
            (1, 'Section 3',
                    ''
            ),
            (2, 'Section 3.1',
                    'Sec 3.1\n'
                    '\n'
            ),
        ))
    #@+node:ekr.20210904065459.46: *3* TestOrg.test_1074
    def test_1074(self):

        s = """
            *  Test
            First line.
        """
        p = self.run_test(s)
        self.check_outline(p, (
            (0, '',  # check_outline ignores the first headline.
                    '@language org\n'
                    '@tabwidth -4\n'
            ),
            (1, ' Test',
                    'First line.\n'
                    '\n'
            ),
        ))
    #@+node:ekr.20210904065459.45: *3* TestOrg.test_552
    def test_552(self):

        s = """
            * Events
              :PROPERTIES:
              :CATEGORY: events
              :END:
            ** 整理个人生活
            *** 每周惯例
        """
        p = self.run_test(s)
        self.check_outline(p, (
            (0, '',  # check_outline ignores the first headline.
                    '@language org\n'
                    '@tabwidth -4\n'
            ),
            (1, 'Events',
                    '  :PROPERTIES:\n'
                    '  :CATEGORY: events\n'
                    '  :END:\n'
            ),
            (2, '整理个人生活',
                    ''
            ),
            (3, '每周惯例',
                    '\n'
            ),
        ))
    #@+node:ekr.20210904065459.44: *3* TestOrg.test_intro
    def test_intro(self):

        s = """
            Intro line.
            * Section 1
            Sec 1.
            * Section 2
            Sec 2.
        """
        p = self.run_test(s)
        self.check_outline(p, (
            (0, '',  # check_outline ignores the first headline.
                'Intro line.\n'
                '@language org\n'
                '@tabwidth -4\n'
            ),
            (1, 'Section 1',
                'Sec 1.\n'
            ),
            (1, 'Section 2',
                'Sec 2.\n'
                '\n'
            ),
        ))
    #@+node:ekr.20210904065459.41: *3* TestOrg.test_pattern
    def test_pattern(self):

        c = self.c
        x = org.Org_Importer(c)
        pattern = x.org_pattern
        table = (
            '* line 1',
            '** level 2',
        )
        for line in table:
            m = pattern.match(line)
            assert m, repr(line)
    #@+node:ekr.20210904065459.47: *3* TestOrg.test_placeholder
    def test_placeholder(self):

        # insert test for org here.
        s = """
            * Section 1
            Sec 1.
            * Section 2
            Sec 2.
            ** Section 2-1
            Sec 2.1
            *** Section 2-1-1
            Sec 2.1.1
            * Section 3
            ****** Section 3-1-1-1-1-1
            : Sec 3-1-1-1-1-1
            ** Section 3.1
            Sec 3.1
        """
        p = self.run_test(s, check_flag=False)  # Perfect import must fail.
        expected = (
            (0, '',  # check_outline ignores the first headline.
                '@language org\n'
                '@tabwidth -4\n'
            ),
            (1, 'Section 1',
                'Sec 1.\n'
            ),
            (1, 'Section 2',
                'Sec 2.\n'
            ),
            (2, 'Section 2-1',
                'Sec 2.1\n'
            ),
            (3, 'Section 2-1-1',
                'Sec 2.1.1\n'
            ),
            (1, 'Section 3', ''),
            (2, 'placeholder level 2', ''),
            (3, 'placeholder level 3', ''),
            (4, 'placeholder level 4', ''),
            (5, 'placeholder level 5', ''),
            (6, 'Section 3-1-1-1-1-1',
                ': Sec 3-1-1-1-1-1\n'
            ),
            (2, 'Section 3.1',
                'Sec 3.1\n'
                '\n'
            ),
        )
        self.check_outline(p, expected)
    #@+node:ekr.20210904065459.43: *3* TestOrg.test_tags
    def test_tags(self):

        s = """\
            * Section 1 :tag1:
            * Section 2 :tag2:
            * Section 3 :tag3:tag4:
        """
        c = self.c
        # Create the TagController by hand.
        from leo.plugins.nodetags import TagController
        c.theTagController = TagController(c)
        # Run the test.
        p = self.run_test(s)
        self.check_outline(p, (
            (0, '',  # check_outline ignores the first headline.
                    '@language org\n'
                    '@tabwidth -4\n'
            ),
            (1, 'Section 1 :tag1:', ''),
            (1, 'Section 2 :tag2:', ''),
            (1, 'Section 3 :tag3:tag4:',
                    '\n'
            ),
        ))
    #@-others
#@+node:ekr.20211108081327.1: ** class TestOtl (BaseTestImporter)
class TestOtl(BaseTestImporter):

    ext = '.otl'
    treeType = '@auto-otl'

    #@+others
    #@+node:ekr.20210904065459.49: *3* TestOtl.test_otl_1
    def test_otl_1(self):

        s = """
            preamble.
            Section 1
            : Sec 1.
            Section 2
            : Sec 2.
            \tSection 2-1
            : Sec 2-1
            \t\tSection 2-1-1
            : Sec 2-1-1
            Section 3
            : Sec 3
            \tSection 3.1
            : Sec 3.1
        """
        p = self.run_test(s)
        # A hack, to simulate an unexpected line in the root node.
        # Alas, this does not affect coverage testing.
        p.b = 'line in root node\n' + p.b
        self.check_outline(p, (
            (0, '',  # check_outline ignores the first headline.
                'line in root node\n'
                '@language otl\n'
                '@tabwidth -4\n'
            ),
            (1, 'preamble.', ''),
            (1, 'Section 1', 'Sec 1.\n'),
            (1, 'Section 2', 'Sec 2.\n'),
            (2, 'Section 2-1', 'Sec 2-1\n'),
            (3, 'Section 2-1-1', 'Sec 2-1-1\n'),
            (1, 'Section 3', 'Sec 3\n'),
            (2, 'Section 3.1', 'Sec 3.1\n'),
        ))
    #@+node:ekr.20220804040446.1: *3* TestOtl.test_otl_placeholder
    def test_otl_placeholder(self):

        s = """
            Section 1
            : Sec 1.
            Section 2
            : Sec 2.
            \t\tSection 3
            : Sec 3.
        """
        p = self.run_test(s, check_flag=False)  # Perfect import must fail.
        self.check_outline(p, (
            (0, '',  # check_outline ignores the first headline.
                '@language otl\n'
                '@tabwidth -4\n'
            ),
            (1, 'Section 1', 'Sec 1.\n'),
            (1, 'Section 2', 'Sec 2.\n'),
            (2, 'placeholder level 2', ''),
            (3, 'Section 3', 'Sec 3.\n'),
        ))
    #@+node:ekr.20210904065459.48: *3* TestOtl.test_vim_outline_mode
    def test_vim_outline_mode(self):

        c = self.c
        x = otl.Otl_Importer(c)
        pattern = x.otl_node_pattern
        table = (
            'body line',
            '\tline 1',
            '  \tlevel 2',
        )
        for line in table:
            m = pattern.match(line)
            self.assertTrue(m, msg=repr(line))
    #@-others
#@+node:ekr.20211108081719.1: ** class TestPascal (BaseTestImporter)
class TestPascal(BaseTestImporter):

    ext = '.pas'

    #@+others
    #@+node:ekr.20210904065459.50: *3* TestPascal.test_delphi_interface
    def test_delphi_interface(self):

        s = """
            unit Unit1;

            interface

            uses
            Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls,
            Forms,
            Dialogs;

            type
            TForm1 = class(TForm)
            procedure FormCreate(Sender: TObject);
            private
            { Private declarations }
            public
            { Public declarations }
            end;

            var
            Form1: TForm1;

            implementation

            {$R *.dfm}

            procedure TForm1.FormCreate(Sender: TObject);
            var
            x,y: double;
            begin
            x:= 4;
            Y := x/2;
            z := 'abc'
            end;

            end. // interface
        """
        p = self.run_test(s)
        self.check_outline(p, (
            (0, '',  # check_outline ignores the first headline.
                    'unit Unit1;\n'
                    '\n'
                    '@others\n'
                    'end. // interface\n'
                    '\n'
                    '@language pascal\n'
                    '@tabwidth -4\n'
            ),
            (1, 'interface',
                'interface\n'
                    '\n'
                    'uses\n'
                    'Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls,\n'
                    'Forms,\n'
                    'Dialogs;\n'
                    '\n'
                    'type\n'
                    'TForm1 = class(TForm)\n'
                    '@others\n'
            ),
            (2, 'procedure FormCreate',
                    'procedure FormCreate(Sender: TObject);\n'
                    'private\n'
                    '{ Private declarations }\n'
                    'public\n'
                    '{ Public declarations }\n'
                    'end;\n'
                    '\n'
                    'var\n'
            ),
            (2, 'Form1: TForm1;',
                    'Form1: TForm1;\n'
                    '\n'
                    'implementation\n'
                    '\n'
                    '{$R *.dfm}\n'
                    '\n'
            ),
            (2, 'procedure TForm1.FormCreate',
                    'procedure TForm1.FormCreate(Sender: TObject);\n'
                    'var\n'
                    'x,y: double;\n'
                    'begin\n'
                    'x:= 4;\n'
                    'Y := x/2;\n'
                    "z := 'abc'\n"
                    'end;\n'
                    '\n'
            ),
         ))
    #@-others
#@+node:ekr.20211108081950.1: ** class TestPerl (BaseTestImporter)
class TestPerl(BaseTestImporter):

    ext = '.pl'

    #@+others
    #@+node:ekr.20210904065459.51: *3* TestPerl.test_1
    def test_1(self):

        s = """
            #!/usr/bin/perl

            # Function definition
            sub Hello{
               print "Hello, World!\n";
            }

            sub Test{
               print "Test!\n";
            }
            "\N{LATIN SMALL LIGATURE FI}" =~ /fi/i;

            $bar = "foo";
            if ($bar =~ /foo/){
               print "Second time is matching\n";
            }else{
               print "Second time is not matching\n";
            }

            # Function call
            Hello();
        """
        p = self.run_test(s)
        self.check_outline(p, (
            (0, '',  # check_outline ignores the first headline.
                    '#!/usr/bin/perl\n'
                    '\n'
                    '@others\n'
                    '            # Function call\n'
                    '            Hello();\n'
                    '\n'
                    '@language perl\n'
                    '@tabwidth -4\n'
            ),
            (1, 'sub Hello',
                    '            # Function definition\n'
                    '            sub Hello{\n'
                    '               print "Hello, World!\n'
                    '";\n'
                    '            }\n'
                    '\n'
            ),
            (1, 'sub Test',
                    '            sub Test{\n'
                    '               print "Test!\n'
                    '";\n'
                    '            }\n'
            ),
            (1,  '"ﬁ" =~ /fi/i',
                '            "ﬁ" =~ /fi/i;\n'
                '\n'
                '            $bar = "foo";\n'

            ),
            (1, 'if ($bar =~ /foo/)',
                '            if ($bar =~ /foo/){\n'
                '               print "Second time is matching\n'
                '";\n'
                '            }else{\n'
                '               print "Second time is not matching\n'
                '";\n'
                '            }\n'
                '\n'
            ),
        ))
    #@+node:ekr.20210904065459.53: *3* TestPerl.test_multi_line_string
    def test_multi_line_string(self):

        s = """
            #!/usr/bin/perl

            # This would print with a line break in the middle
            print "Hello

            sub World {
                print "This is not a funtion!"
            }

            world\n";
        """
        p = self.run_test(s)
        self.check_outline(p, (
            (0, '',  # check_outline ignores the first headline.
                    '#!/usr/bin/perl\n'
                    '\n'
                    '            # This would print with a line break in the middle\n'
                    '            print "Hello\n'
                    '\n'
                    '            sub World {\n'
                    '                print "This is not a funtion!"\n'
                    '            }\n'
                    '\n'
                    '            world\n'
                    '";\n'
                    '\n'
                    '@language perl\n'
                    '@tabwidth -4\n'
            ),
        ))
    #@+node:ekr.20210904065459.52: *3* TestPerl.test_perlpod_comment
    def test_perlpod_comment(self):

        s = """
            #!/usr/bin/perl

            sub Test{
               print "Test!\n";
            }

            =begin comment
            sub World {
                print "This is not a funtion!"
            }
            =cut

            # Function definition
            sub Hello{
               print "Hello, World!\n";
            }
        """
        p = self.run_test(s)
        self.check_outline(p, (
            (0, '',  # check_outline ignores the first headline.
                    '#!/usr/bin/perl\n'
                    '\n'
                    '@others\n'
                    '@language perl\n'
                    '@tabwidth -4\n'
            ),
            (1, 'sub Test',
                    '            sub Test{\n'
                    '               print "Test!\n'
                    '";\n'
                    '            }\n'
                    '\n'
            ),
            (1, '=begin comment',
                    '            =begin comment\n'
            ),
            (1, 'sub World',
                    '            sub World {\n'
                    '                print "This is not a funtion!"\n'
                    '            }\n'
            ),
            (1, '=cut',
                    '            =cut\n'
                    '\n'
            ),
            (1, 'sub Hello',
                    '            # Function definition\n'
                    '            sub Hello{\n'
                    '               print "Hello, World!\n'
                    '";\n'
                    '            }\n'
                    '\n'
            ),
        ))
    #@+node:ekr.20210904065459.55: *3* TestPerl.test_regex
    def test_regex(self):

        s = """
            #!/usr/bin/perl

            sub test1 {
                s = /}/g;
            }

            sub test2 {
                s = m//}/;
            }

            sub test3 {
                s = s///}/;
            }

            sub test4 {
                s = tr///}/;
            }
        """
        p = self.run_test(s)
        self.check_outline(p, (
            (0, '',  # check_outline ignores the first headline.
                    '@others\n'
                    '@language perl\n'
                    '@tabwidth -4\n'
            ),
            (1, 'sub test1',
                    '#!/usr/bin/perl\n'
                    '\n'
                    'sub test1 {\n'
                    '    s = /}/g;\n'
                    '}\n'
                    '\n'
            ),
            (1, 'sub test2',
                    'sub test2 {\n'
                    '    s = m//}/;\n'
                    '}\n'
                    '\n'
            ),
            (1, 'sub test3',
                    'sub test3 {\n'
                    '    s = s///}/;\n'
                    '}\n'
                    '\n'
            ),
            (1, 'sub test4',
                    'sub test4 {\n'
                    '    s = tr///}/;\n'
                    '}\n'
                    '\n'
            ),
        ))
    #@-others
#@+node:ekr.20211108082208.1: ** class TestPhp (BaseTestImporter)
class TestPhp(BaseTestImporter):

    ext = '.php'

    #@+others
    #@+node:ekr.20210904065459.56: *3* TestPhp.test_import_class
    def test_import_class(self):

        s = """
            <?php

            $type = 'cc';
            $obj = new $type; // outputs "hi!"

            class cc {
                function __construct() {
                    echo 'hi!';
                }
            }

            ?>
        """
        self.run_test(s)
    #@+node:ekr.20210904065459.57: *3* TestPhp.test_import_conditional_class
    def test_import_conditional_class(self):

        s = """
            <?php

            if (expr) {
                class cc {
                    // version 1
                }
            } else {
                class cc {
                    // version 2
                }
            }

            ?>
        """
        self.run_test(s)
    #@+node:ekr.20210904065459.58: *3* TestPhp.test_import_classes__functions
    def test_import_classes__functions(self):

        s = """
            <?php
            class Enum {
                protected $self = array();
                public function __construct( /*...*/ ) {
                    $args = func_get_args();
                    for( $i=0, $n=count($args); $i<$n; $i++ )
                        $this->add($args[$i]);
                }

                public function __get( /*string*/ $name = null ) {
                    return $this->self[$name];
                }

                public function add( /*string*/ $name = null, /*int*/ $enum = null ) {
                    if( isset($enum) )
                        $this->self[$name] = $enum;
                    else
                        $this->self[$name] = end($this->self) + 1;
                }
            }

            class DefinedEnum extends Enum {
                public function __construct( /*array*/ $itms ) {
                    foreach( $itms as $name => $enum )
                        $this->add($name, $enum);
                }
            }

            class FlagsEnum extends Enum {
                public function __construct( /*...*/ ) {
                    $args = func_get_args();
                    for( $i=0, $n=count($args), $f=0x1; $i<$n; $i++, $f *= 0x2 )
                        $this->add($args[$i], $f);
                }
            }
            ?>
        """
        self.run_test(s)
    #@+node:ekr.20210904065459.59: *3* TestPhp.test_here_doc
    def test_here_doc(self):

        s = """
            <?php
            class foo {
                public $bar = <<<EOT
            a test.
            bar
            EOT;
            }
            ?>
        """
        self.run_test(s)
    #@-others
#@+node:ekr.20211108082509.1: ** class TestPython (BaseTestImporter)
class TestPython(BaseTestImporter):

    check_tree = False
    ext = '.py'
    treeType = '@file'

    def setUp(self):
        super().setUp()
        if sys.version_info < (3, 7, 0):
            self.skipTest('The python importer requires python 3.7 or above')  # pragma: no cover

    def run_test(self, s: str, check_flag: bool=True, strict_flag: bool=False) -> Position:
        """Run tests with both values of python.USE_PYTHON_TOKENS."""
        import leo.plugins.importers.python as python
        try:
            p = None
            self.assertTrue(python.USE_PYTHON_TOKENS)
            super().run_test(s, check_flag, strict_flag)
            python.USE_PYTHON_TOKENS = False
            p = super().run_test(s, check_flag, strict_flag)
        finally:
            python.USE_PYTHON_TOKENS = True
        return p

    #@+others
    #@+node:vitalije.20211206201240.1: *3* TestPython.test_longer_classes
    def test_longer_classes(self):

        s = self.dedent("""\
              import sys
              def f1():
                  pass

              class Class1:
                  def method11():
                      pass
                  def method12():
                      pass

              #
              # Define a = 2
              a = 2

              def f2():
                  pass

              # An outer comment
              ATmyClassDecorator
              class Class2:
                  def meth00():
                      print(1)
                      print(2)
                      print(3)
                      print(4)
                      print(5)
                      print(6)
                      print(7)
                      print(8)
                      print(9)
                      print(10)
                      print(11)
                      print(12)
                      print(13)
                      print(14)
                      print(15)
                  ATmyDecorator
                  def method21():
                      pass
                  def method22():
                      pass

              # About main.

              def main():
                  pass

              if __name__ == '__main__':
                  main()
        """).replace('AT', '@')

        p = self.run_test(s, strict_flag=True)
        self.check_outline(p, (
            (0, '', # check_outline ignores the first headline'
                    'import sys\n'
                    '@others\n'
                    "if __name__ == '__main__':\n"
                    '    main()\n'
                    '\n'
                    '@language python\n'
                    '@tabwidth -4\n'
            ),
            (1, 'f1',
                    'def f1():\n'
                    '    pass\n'
                    '\n'
            ),
            # Use this if unit tests *do* honor threshold.
            # (1, 'Class1',
                       # 'class Class1:\n'
                       # '    def method11():\n'
                       # '        pass\n'
                       # '    def method12():\n'
                       # '        pass\n'
                       # '\n'
            # ),
            (1, 'class Class1',
                       'class Class1:\n'
                       '    @others\n'
            ),
            (2, 'method11',
                       'def method11():\n'
                       '    pass\n'
            ),
            (2, 'method12',
                       'def method12():\n'
                       '    pass\n'
                       '\n'
            ),
            (1, 'Define a = 2',  # #2500
                       '#\n'
                       '# Define a = 2\n'
                       'a = 2\n'
                       '\n'
            ),
            (1, 'f2',
                       'def f2():\n'
                       '    pass\n'
                       '\n'
            ),
            (1, 'class Class2',
                       '# An outer comment\n'
                       '@myClassDecorator\n'
                       'class Class2:\n'
                       '    @others\n'
            ),
            (2, 'meth00',
                       'def meth00():\n'
                       '    print(1)\n'
                       '    print(2)\n'
                       '    print(3)\n'
                       '    print(4)\n'
                       '    print(5)\n'
                       '    print(6)\n'
                       '    print(7)\n'
                       '    print(8)\n'
                       '    print(9)\n'
                       '    print(10)\n'
                       '    print(11)\n'
                       '    print(12)\n'
                       '    print(13)\n'
                       '    print(14)\n'
                       '    print(15)\n'
            ),
            (2, 'method21',
                       '@myDecorator\n'
                       'def method21():\n'
                       '    pass\n'
            ),
            (2, 'method22',
                       'def method22():\n'
                       '    pass\n'
                       '\n'
            ),
            (1, 'main',
                       '# About main.\n'
                       '\n'
                       'def main():\n'
                       '    pass\n'
                       '\n'
            ),
        ))

    #@+node:vitalije.20211206212507.1: *3* TestPython.test_oneliners
    def test_oneliners(self):
        s = ('import sys\n'
              'def f1():\n'
              '    pass\n'
              '\n'
              'class Class1:pass\n'
              'a = 2\n'
              '@dec_for_f2\n'
              'def f2(): pass\n'
              '\n'
              '\n'
              'class A: pass\n'
              '# About main.\n'
              'def main():\n'
              '    pass\n'
              '\n'
              "if __name__ == '__main__':\n"
              '    main()\n'
            )
        p = self.run_test(s, strict_flag=True)
        self.check_outline(p, (
            (0, '',  # check_outline ignores the first headline.
                       'import sys\n'
                       '@others\n'
                       "if __name__ == '__main__':\n"
                       '    main()\n\n'
                       '@language python\n'
                       '@tabwidth -4\n'
            ),
            (1, 'f1',
                       'def f1():\n'
                       '    pass\n'
                       '\n'
            ),
            (1, 'class Class1',
                       'class Class1:pass\n'
            ),
            (1, 'a = 2',
                       'a = 2\n'
            ),
            (1, 'f2',
                       '@dec_for_f2\n'
                       'def f2(): pass\n'
                       '\n'
                       '\n'
            ),
            (1, 'class A',
                       'class A: pass\n'
            ),
            (1, 'main',
                       '# About main.\n'
                       'def main():\n'
                       '    pass\n'
                       '\n'
            ),
        ))
    #@+node:ekr.20210904065459.63: *3* TestPython.test_short_classes
    def test_short_classes(self):
        s = (
            'import sys\n'
            'def f1():\n'
            '    pass\n'
            '\n'
            'class Class1:\n'
            '    def method11():\n'
            '        pass\n'
            '    def method12():\n'
            '        pass\n'
            '        \n'
            'a = 2\n'
            '\n'
            'def f2():\n'
            '    pass\n'
            '\n'
            '# An outer comment\n'
            '@myClassDecorator\n'
            'class Class2:\n'
            '    @myDecorator\n'
            '    def method21():\n'
            '        pass\n'
            '    def method22():\n'
            '        pass\n'
            '        \n'
            '# About main.\n'
            'def main():\n'
            '    pass\n'
            '\n'
            "if __name__ == '__main__':\n"
            '    main()\n'
        )
        p = self.run_test(s, strict_flag=True)
        self.check_outline(p, (
            (0, '', # check_outline ignores the first headline
                    'import sys\n'
                    '@others\n'
                    "if __name__ == '__main__':\n"
                    '    main()\n'
                    '\n'
                    '@language python\n'
                    '@tabwidth -4\n'
            ),
            (1, 'f1',
                    'def f1():\n'
                    '    pass\n'
                    '\n'
            ),
            # Use this if unit tests *do* honor threshold.
            # (1, 'Class1', 'class Class1:\n'  # Don't split very short classes.
                          # '    def method11():\n'
                          # '        pass\n'
                          # '    def method12():\n'
                          # '        pass\n'
                          # '\n'
            # ),
            (1, 'class Class1',
                        'class Class1:\n'  # Don't split very short classes.
                        '    @others\n'
            ),
            (2, 'method11',
                        'def method11():\n'
                        '    pass\n'
            ),
            (2, 'method12',
                        'def method12():\n'
                        '    pass\n'
                        '\n'
            ),
            (1, 'a = 2',
                        'a = 2\n'
                        '\n'
            ),
            (1, 'f2',
                        'def f2():\n'
                        '    pass\n'
                        '\n'
            ),
            # Use this if unit tests *do* honor threshold.
            # (1, 'Class2', '# An outer comment\n'
                          # '@myClassDecorator\n'
                          # 'class Class2:\n'
                          # '    @myDecorator\n'
                          # '    def method21():\n'
                          # '        pass\n'
                          # '    def method22():\n'
                          # '        pass\n'
                          # '\n'
            # ),
            (1, 'class Class2',
                        '# An outer comment\n'
                        '@myClassDecorator\n'
                        'class Class2:\n'
                        '    @others\n'
            ),
            (2, 'method21',
                        '@myDecorator\n'
                        'def method21():\n'
                        '    pass\n'
            ),
            (2, 'method22',
                          'def method22():\n'
                          '    pass\n'
                          '\n'
            ),
            (1, 'main', '# About main.\n'
                        'def main():\n'
                        '    pass\n'
                        '\n'
            )
        ))

    #@+node:ekr.20211126055349.1: *3* TestPython.test_short_file
    def test_short_file(self):

        input_s = self.dedent('''\
            """A docstring"""
            switch = 1
            print(3)
            print(6)
            def a():
                pass
            print(7)
        ''')
        p = self.run_test(input_s, strict_flag=True)
        self.check_outline(p, (
            (0, '',  # check_outline ignores the first headline.
                    '"""A docstring"""\n'
                    'switch = 1\n'
                    'print(3)\n'
                    'print(6)\n'
                    '@others\n'
                    'print(7)\n'
                    '\n'
                    '@language python\n'
                    '@tabwidth -4\n'
            ),
            (1, 'a',  # Unit tests ignore size threshold.
               'def a():\n'
               '    pass\n'
            ),
        ))
    #@+node:vitalije.20211207200701.1: *3* TestPython: test_large_class_no_methods
    def test_large_class_no_methods(self):

        if sys.version_info < (3, 9, 0):
            self.skipTest('Requires Python 3.9')  # pragma: no cover
        s = (
                'class A:\n'
                '    a=1\n'
                '    b=1\n'
                '    c=1\n'
                '    d=1\n'
                '    e=1\n'
                '    f=1\n'
                '    g=1\n'
                '    h=1\n'
                '    i=1\n'
                '    j=1\n'
                '    k=1\n'
                '    l=1\n'
                '    m=1\n'
                '    n=1\n'
                '    o=1\n'
                '    p=1\n'
                '    q=1\n'
                '    r=1\n'
                '    s=1\n'
                '    t=1\n'
                '    u=1\n'
                '    v=1\n'
                '    w=1\n'
                '    x=1\n'
                '    y=1\n'
                '    x=1\n'
                '\n'
            )
        p = self.run_test(s, strict_flag=True)
        self.check_outline(p, (
            (0, '',  # check_outline ignores the first headline.
                       '@others\n'
                       '@language python\n'
                       '@tabwidth -4\n'
            ),
            (1, 'class A',
                       'class A:\n'
                       '    a=1\n'
                       '    b=1\n'
                       '    c=1\n'
                       '    d=1\n'
                       '    e=1\n'
                       '    f=1\n'
                       '    g=1\n'
                       '    h=1\n'
                       '    i=1\n'
                       '    j=1\n'
                       '    k=1\n'
                       '    l=1\n'
                       '    m=1\n'
                       '    n=1\n'
                       '    o=1\n'
                       '    p=1\n'
                       '    q=1\n'
                       '    r=1\n'
                       '    s=1\n'
                       '    t=1\n'
                       '    u=1\n'
                       '    v=1\n'
                       '    w=1\n'
                       '    x=1\n'
                       '    y=1\n'
                       '    x=1\n'
                       '\n'
            )
        ))

    #@+node:vitalije.20211213125307.1: *3* TestPython: test_large_class_under_indented
    def test_large_class_under_indented(self):
        s = (
                'class A:\n'
                '    a=1\n'
                '    b=1\n'
                '    c=1\n'
                '    d=1\n'
                '    e=1\n'
                '    def f(self):\n'
                '        self._f = """dummy\n'
                'dummy2\n'
                'dummy3"""\n'
                '    g=1\n'
                '    h=1\n'
                '    i=1\n'
                '    j=1\n'
                '    k=1\n'
                '    l=1\n'
                '    m=1\n'
                '    n=1\n'
                '    o=1\n'
                '    p=1\n'
                '    q=1\n'
                '    r=1\n'
                '    s=1\n'
                '    t=1\n'
                '    u=1\n'
                '    v=1\n'
                '    w=1\n'
                '    x=1\n'
                '    y=1\n'
                '    x=1\n'
                '\n'
            )
        p = self.run_test(s, strict_flag=False)  # We expect perfect import to fail.
        self.check_outline(p, (
            (0, '',  # check_outline ignores the first headline.
                       '@others\n'
                       '@language python\n'
                       '@tabwidth -4\n'
            ),
            (1, 'class A',
                       'class A:\n'
                       '    a=1\n'
                       '    b=1\n'
                       '    c=1\n'
                       '    d=1\n'
                       '    e=1\n'
                       '    @others\n'
                       '    g=1\n'
                       '    h=1\n'
                       '    i=1\n'
                       '    j=1\n'
                       '    k=1\n'
                       '    l=1\n'
                       '    m=1\n'
                       '    n=1\n'
                       '    o=1\n'
                       '    p=1\n'
                       '    q=1\n'
                       '    r=1\n'
                       '    s=1\n'
                       '    t=1\n'
                       '    u=1\n'
                       '    v=1\n'
                       '    w=1\n'
                       '    x=1\n'
                       '    y=1\n'
                       '    x=1\n'
                       '\n'
            ),
            (2, 'f',
                       'def f(self):\n'
                       '    self._f = """dummy\n'
                       # '\\\\-4.dummy2\n'
                       # '\\\\-4.dummy3"""\n'
                       'dummy2\n'
                       'dummy3"""\n'
            )
        ))
    #@+node:ekr.20211202064822.1: *3* TestPython: test_nested_classes
    def test_nested_classes(self):
        s = """\
            class TestCopyFile(unittest.TestCase):

                _delete = False
                a00 = 1
                a01 = 1
                a02 = 1
                a03 = 1
                a04 = 1
                a05 = 1
                a06 = 1
                a07 = 1
                a08 = 1
                a09 = 1
                a10 = 1
                a11 = 1
                a12 = 1
                a13 = 1
                a14 = 1
                a15 = 1
                a16 = 1
                a17 = 1
                a18 = 1
                a19 = 1
                a20 = 1
                a21 = 1
                class Faux(object):
                    _entered = False
                    _exited_with = None # type: tuple
                    _raised = False
            """
        # mypy/test-data/stdlib-samples/3.2/test/shutil.py
        p = self.run_test(s, strict_flag=True)
        self.check_outline(p, (
            (0, '',  # check_outline ignores the first headline.
                       '@others\n'
                       '@language python\n'
                       '@tabwidth -4\n'
            ),
            (1, 'class TestCopyFile', self.dedent("""\
                        class TestCopyFile(unittest.TestCase):

                            _delete = False
                            a00 = 1
                            a01 = 1
                            a02 = 1
                            a03 = 1
                            a04 = 1
                            a05 = 1
                            a06 = 1
                            a07 = 1
                            a08 = 1
                            a09 = 1
                            a10 = 1
                            a11 = 1
                            a12 = 1
                            a13 = 1
                            a14 = 1
                            a15 = 1
                            a16 = 1
                            a17 = 1
                            a18 = 1
                            a19 = 1
                            a20 = 1
                            a21 = 1
                            ATothers
                """).replace('AT', '@')
            ),
            (2, 'class Faux',
                        'class Faux(object):\n'
                        '    _entered = False\n'
                        '    _exited_with = None # type: tuple\n'
                        '    _raised = False\n'
                        '\n'
            ),
        ))
    #@+node:vitalije.20211213125810.1: *3* TestPython: test_nested_classes_with_async
    def test_nested_classes_with_async(self):
        s = (
                'class TestCopyFile(unittest.TestCase):\n'
                '\n'
                '    _delete = False\n'
                '    a00 = 1\n'
                '    a01 = 1\n'
                '    a02 = 1\n'
                '    a03 = 1\n'
                '    a04 = 1\n'
                '    a05 = 1\n'
                '    a06 = 1\n'
                '    a07 = 1\n'
                '    a08 = 1\n'
                '    a09 = 1\n'
                '    a10 = 1\n'
                '    a11 = 1\n'
                '    a12 = 1\n'
                '    a13 = 1\n'
                '    a14 = 1\n'
                '    a15 = 1\n'
                '    a16 = 1\n'
                '    a17 = 1\n'
                '    a18 = 1\n'
                '    a19 = 1\n'
                '    a20 = 1\n'
                '    a21 = 1\n'
                '    async def a(self):\n'
                '        return await f(self)\n'
                '    class Faux(object):\n'
                '        _entered = False\n'
                '        _exited_with = None # type: tuple\n'
                '        _raised = False\n'
              )
        p = self.run_test(s, strict_flag=True)
        self.check_outline(p, (
            (0, '',  # check_outline ignores the first headline.
                       '@others\n'
                       '@language python\n'
                       '@tabwidth -4\n'
            ),
            (1, 'class TestCopyFile',
                       'class TestCopyFile(unittest.TestCase):\n'
                       '\n'
                       '    _delete = False\n'
                       '    a00 = 1\n'
                       '    a01 = 1\n'
                       '    a02 = 1\n'
                       '    a03 = 1\n'
                       '    a04 = 1\n'
                       '    a05 = 1\n'
                       '    a06 = 1\n'
                       '    a07 = 1\n'
                       '    a08 = 1\n'
                       '    a09 = 1\n'
                       '    a10 = 1\n'
                       '    a11 = 1\n'
                       '    a12 = 1\n'
                       '    a13 = 1\n'
                       '    a14 = 1\n'
                       '    a15 = 1\n'
                       '    a16 = 1\n'
                       '    a17 = 1\n'
                       '    a18 = 1\n'
                       '    a19 = 1\n'
                       '    a20 = 1\n'
                       '    a21 = 1\n'
                       '    @others\n'
            ),
            (2, 'a',
                       'async def a(self):\n'
                       '    return await f(self)\n'
            ),
            (2, 'class Faux',
                       'class Faux(object):\n'
                       '    _entered = False\n'
                       '    _exited_with = None # type: tuple\n'
                       '    _raised = False\n\n'
            )
       ))
    #@+node:vitalije.20211207183645.1: *3* TestPython: test_no_defs
    def test_no_defs(self):
        s = (
                'a = 1\n'
                'if 1:\n'
                " print('1')\n"
                'if 2:\n'
                "  print('2')\n"
                'if 3:\n'
                "   print('3')\n"
                'if 4:\n'
                "    print('4')\n"
                'if 5:\n'
                "    print('5')\n"
                'if 6:\n'
                "    print('6')\n"
                'if 7:\n'
                "    print('7')\n"
                'if 8:\n'
                "    print('8')\n"
                'if 9:\n'
                "    print('9')\n"
                'if 10:\n'
                "    print('10')\n"
                'if 11:\n'
                "    print('11')\n"
                'if 12:\n'
                "    print('12')\n"
            )
        p = self.run_test(s, strict_flag=True)
        self.check_outline(p, (
            (0, '',  # check_outline ignores the first headline.
               'a = 1\n'
               'if 1:\n'
               " print('1')\n"
               'if 2:\n'
               "  print('2')\n"
               'if 3:\n'
               "   print('3')\n"
               'if 4:\n'
               "    print('4')\n"
               'if 5:\n'
               "    print('5')\n"
               'if 6:\n'
               "    print('6')\n"
               'if 7:\n'
               "    print('7')\n"
               'if 8:\n'
               "    print('8')\n"
               'if 9:\n'
               "    print('9')\n"
               'if 10:\n'
               "    print('10')\n"
               'if 11:\n'
               "    print('11')\n"
               'if 12:\n'
               "    print('12')\n\n"
               '@language python\n'
               '@tabwidth -4\n'
            ),
        ))
    #@+node:vitalije.20211207185708.1: *3* TestPython: test_only_docs
    def test_only_docs(self):
        s = (
                'class A:\n'
                '    """\n'
                '    dummy doc\n'
                "    another line\n"
                "    another line\n"
                "    another line\n"
                "    another line\n"
                "    another line\n"
                "    another line\n"
                "    another line\n"
                "    another line\n"
                "    another line\n"
                "    another line\n"
                "    another line\n"
                "    another line\n"
                "    another line\n"
                "    another line\n"
                "    another line\n"
                "    another line\n"
                "    another line\n"
                "    another line\n"
                "    another line\n"
                "    another line\n"
                "    another line\n"
                "    another line\n"
                "    another line\n"
                '    """\n'
                '    def __init__(self):\n'
                '        pass\n'
                '\n'
            )
        p = self.run_test(s, strict_flag=True)
        self.check_outline(p, (
            (0, '',  # check_outline ignores the first headline.
                       '@others\n'
                       '@language python\n'
                       '@tabwidth -4\n'
            ),
            (1, 'class A',
                       'class A:\n'
                       '    """\n'
                       '    dummy doc\n'
                       '    another line\n'
                       '    another line\n'
                       '    another line\n'
                       '    another line\n'
                       '    another line\n'
                       '    another line\n'
                       '    another line\n'
                       '    another line\n'
                       '    another line\n'
                       '    another line\n'
                       '    another line\n'
                       '    another line\n'
                       '    another line\n'
                       '    another line\n'
                       '    another line\n'
                       '    another line\n'
                       '    another line\n'
                       '    another line\n'
                       '    another line\n'
                       '    another line\n'
                       '    another line\n'
                       '    another line\n'
                       '    another line\n'
                       '    """\n'
                       '    @others\n'
            ),
            (2, '__init__',
                       'def __init__(self):\n'
                       '    pass\n'
                       '\n'
            )
        ))
    #@+node:ekr.20211202094115.1: *3* TestPython: test_strange_indentation
    def test_strange_indentation(self):
        s = (
                'if 1:\n'
                " print('1')\n"
                'if 2:\n'
                "  print('2')\n"
                'if 3:\n'
                "   print('3')\n"
                '\n'
                'class StrangeClass:\n'
                ' a = 1\n'
                ' if 1:\n'
                "  print('1')\n"
                ' if 2:\n'
                "   print('2')\n"
                ' if 3:\n'
                "    print('3')\n"
                ' if 4:\n'
                "     print('4')\n"
                ' if 5:\n'
                "     print('5')\n"
                ' if 6:\n'
                "     print('6')\n"
                ' if 7:\n'
                "     print('7')\n"
                ' if 8:\n'
                "     print('8')\n"
                ' if 9:\n'
                "     print('9')\n"
                ' if 10:\n'
                "     print('10')\n"
                ' if 11:\n'
                "     print('11')\n"
                ' if 12:\n'
                "     print('12')\n"
                ' def a(self):\n'
                '   pass\n'
            )
        p = self.run_test(s, strict_flag=True)
        self.check_outline(p, (
            (0, '',  # check_outline ignores the first headline.
                       'if 1:\n'
                       " print('1')\n"
                       'if 2:\n'
                       "  print('2')\n"
                       'if 3:\n'
                       "   print('3')\n"
                       '\n'
                       '@others\n'
                       '@language python\n'
                       '@tabwidth -4\n'
            ),
            (1, 'class StrangeClass',
                       'class StrangeClass:\n'
                       ' a = 1\n'
                       ' if 1:\n'
                       "  print('1')\n"
                       ' if 2:\n'
                       "   print('2')\n"
                       ' if 3:\n'
                       "    print('3')\n"
                       ' if 4:\n'
                       "     print('4')\n"
                       ' if 5:\n'
                       "     print('5')\n"
                       ' if 6:\n'
                       "     print('6')\n"
                       ' if 7:\n'
                       "     print('7')\n"
                       ' if 8:\n'
                       "     print('8')\n"
                       ' if 9:\n'
                       "     print('9')\n"
                       ' if 10:\n'
                       "     print('10')\n"
                       ' if 11:\n'
                       "     print('11')\n"
                       ' if 12:\n'
                       "     print('12')\n"
                       ' @others\n'
            ),
            (2, 'a',
                       'def a(self):\n'
                       '  pass\n\n'
            )
        ))
    #@+node:vitalije.20211208210459.1: *3* TestPython: test_strange_indentation_with...
    def test_strange_indentation_with_added_class_in_the_headline(self):
        self.c.config.set(None, 'bool', 'put-class-in-imported-headlines', True)
        s = (
                'if 1:\n'
                " print('1')\n"
                'if 2:\n'
                "  print('2')\n"
                'if 3:\n'
                "   print('3')\n"
                '\n'
                'class StrangeClass:\n'
                ' a = 1\n'
                ' if 1:\n'
                "  print('1')\n"
                ' if 2:\n'
                "   print('2')\n"
                ' if 3:\n'
                "    print('3')\n"
                ' if 4:\n'
                "     print('4')\n"
                ' if 5:\n'
                "     print('5')\n"
                ' if 6:\n'
                "     print('6')\n"
                ' if 7:\n'
                "     print('7')\n"
                ' if 8:\n'
                "     print('8')\n"
                ' if 9:\n'
                "     print('9')\n"
                ' if 10:\n'
                "     print('10')\n"
                ' if 11:\n'
                "     print('11')\n"
                ' if 12:\n'
                "     print('12')\n"
                ' def a(self):\n'
                '   pass\n'
            )
        p = self.run_test(s, strict_flag=True)
        self.check_outline(p, (
            (0, '',  # check_outline ignores the first headline.
                       'if 1:\n'
                       " print('1')\n"
                       'if 2:\n'
                       "  print('2')\n"
                       'if 3:\n'
                       "   print('3')\n"
                       '\n'
                       '@others\n'
                       '@language python\n'
                       '@tabwidth -4\n'
            ),
            (1, 'class StrangeClass',
                       'class StrangeClass:\n'
                       ' a = 1\n'
                       ' if 1:\n'
                       "  print('1')\n"
                       ' if 2:\n'
                       "   print('2')\n"
                       ' if 3:\n'
                       "    print('3')\n"
                       ' if 4:\n'
                       "     print('4')\n"
                       ' if 5:\n'
                       "     print('5')\n"
                       ' if 6:\n'
                       "     print('6')\n"
                       ' if 7:\n'
                       "     print('7')\n"
                       ' if 8:\n'
                       "     print('8')\n"
                       ' if 9:\n'
                       "     print('9')\n"
                       ' if 10:\n'
                       "     print('10')\n"
                       ' if 11:\n'
                       "     print('11')\n"
                       ' if 12:\n'
                       "     print('12')\n"
                       ' @others\n'
            ),
            (2, 'a',
                       'def a(self):\n'
                       '  pass\n\n'
            )
        ))
    #@-others
#@+node:ekr.20211108050827.1: ** class TestRst (BaseTestImporter)
class TestRst(BaseTestImporter):

    ext = '.rst'
    treeType = '@auto-rst'

    #@+others
    #@+node:ekr.20210904065459.115: *3* TestRst.test_rst_1
    def test_rst_1(self):

        try:
            import docutils
            assert docutils
        except Exception:  # pragma: no cover
            self.skipTest('no docutils')

        s = """
            .. toc

            ====
            top
            ====

            The top section

            section 1
            ---------

            section 1, line 1
            --
            section 1, line 2

            section 2
            ---------

            section 2, line 1

            section 2.1
            ~~~~~~~~~~~

            section 2.1, line 1

            section 2.1.1
            .............

            section 2.2.1 line 1

            section 3
            ---------

            section 3, line 1

            section 3.1.1
            .............

            section 3.1.1, line 1
        """
        # Perfect import must fail: The writer won't use the same underlines.
        p = self.run_test(s, check_flag=False)
        # self.dump_tree(p, tag='Actual results...')
        self.check_outline(p, (
            (0, '',  # check_outline ignores the first headline.
                '@language rest\n'
                '@tabwidth -4\n'
            ),
            (1, '!Dummy chapter',
                '.. toc\n'
                '\n'
            ),
            (1, 'top',
                '\n'
                'The top section\n'
                '\n'
            ),
            (1, 'section 1',
                '\n'
                'section 1, line 1\n'
                '--\n'
                'section 1, line 2\n'
                '\n'
            ),
            (1, 'section 2',
                '\n'
                'section 2, line 1\n'
                '\n'
            ),
            (2, 'section 2.1',
                '\n'
                'section 2.1, line 1\n'
                '\n'
            ),
            (3, 'section 2.1.1',
                '\n'
                'section 2.2.1 line 1\n'
                '\n'
            ),
            (1, 'section 3',
                '\n'
                'section 3, line 1\n'
                '\n'
            ),
            (2, 'placeholder level 2',
                ''
            ),
            (3, 'section 3.1.1',
                '\n'
                'section 3.1.1, line 1\n'
                '\n'
            ),
        ))
    #@+node:ekr.20210904065459.116: *3* TestRst.test_simple
    def test_simple(self):

        try:
            import docutils
            assert docutils
        except Exception:  # pragma: no cover
            self.skipTest('no docutils')

        s = """
            .. toc

            .. The section name contains trailing whitespace.

            =======
            Chapter
            =======

            The top chapter.
        """
        # Perfect import must fail: The writer won't use the same underlines.
        p = self.run_test(s, check_flag=False)
        self.check_outline(p, (
            (0, '',  # check_outline ignores the first headline.
                '@language rest\n'
                '@tabwidth -4\n'
            ),
            (1, "!Dummy chapter",
                '.. toc\n'
                '\n'
                '.. The section name contains trailing whitespace.\n'
                '\n'
            ),
            (1, "Chapter",
                '\n'
                'The top chapter.\n'
                '\n'
            ),
        ))
    #@+node:ekr.20210904065459.117: *3* TestRst.test_no_double_underlines
    def test_no_double_underlines(self):

        try:
            import docutils
            assert docutils
        except Exception:  # pragma: no cover
            self.skipTest('no docutils')

        s = """
            .. toc

            top
            ====

            The top section

            section 1
            ---------

            section 1, line 1
            --
            section 1, line 2

            section 2
            ---------

            section 2, line 1

            section 2.1
            ~~~~~~~~~~~

            section 2.1, line 1

            section 2.1.1
            .............

            section 2.2.1 line 1

            section 3
            ---------

            section 3, line 1

            section 3.1.1
            .............

            section 3.1.1, line 1
        """
        # Perfect import must fail: The writer won't use the same underlines.
        p = self.run_test(s, check_flag=False)
        self.check_outline(p, (
            (0, '',  # check_outline ignores the first headline.
                    '@language rest\n'
                    '@tabwidth -4\n'
            ),
            (1, '!Dummy chapter',
                    '.. toc\n'
                    '\n'
            ),
            (1, 'top',
                    '\n'
                    'The top section\n'
                    '\n'
            ),
            (1, 'section 1',
                    '\n'
                    'section 1, line 1\n'
                    '--\n'
                    'section 1, line 2\n'
                    '\n'
            ),
            (1, 'section 2',
                    '\n'
                    'section 2, line 1\n'
                    '\n'
            ),
            (2, 'section 2.1',
                    '\n'
                    'section 2.1, line 1\n'
                    '\n'
            ),
            (3, 'section 2.1.1',
                    '\n'
                    'section 2.2.1 line 1\n'
                    '\n'
            ),
            (1, 'section 3',
                    '\n'
                    'section 3, line 1\n'
                    '\n'
            ),
            (2, 'placeholder level 2',
                    ''
            ),
            (3, 'section 3.1.1',
                    '\n'
                    'section 3.1.1, line 1\n'
                    '\n'
            ),
        ))
    #@+node:ekr.20210904065459.118: *3* TestRst.test_long_underlines
    def test_long_underlines(self):

        try:
            import docutils
            assert docutils
        except Exception:  # pragma: no cover
            self.skipTest('no docutils')

        s = """
            .. toc

            top
            -------------

            The top section
        """
        # Perfect import must fail: The writer won't use the same underlines.
        p = self.run_test(s, check_flag=False)
        self.check_outline(p, (
            (0, '',  # check_outline ignores the first headline.
                    '@language rest\n'
                    '@tabwidth -4\n'
            ),
            (1, '!Dummy chapter',
                    '.. toc\n'
                    '\n'
            ),
            (1, 'top',
                    '\n'
                    'The top section\n'
                    '\n'
            ),
        ))
    #@+node:ekr.20210904065459.119: *3* TestRst.test_test_long_overlines
    def test_test_long_overlines(self):

        try:
            import docutils
            assert docutils
        except Exception:  # pragma: no cover
            self.skipTest('no docutils')

        s = """
            .. toc

            ======
            top
            ======

            The top section
        """
        # Perfect import must fail: The writer won't use the same underlines.
        p = self.run_test(s, check_flag=False)
        self.check_outline(p, (
            (0, '',  # check_outline ignores the first headline.
                '@language rest\n'
                '@tabwidth -4\n'
            ),
            (1, "!Dummy chapter",
                '.. toc\n'
                '\n'
            ),
            (1, "top",
                '\n'
                'The top section\n'
                '\n'
            ),
        ))
    #@+node:ekr.20210904065459.120: *3* TestRst.test_trailing_whitespace
    def test_trailing_whitespace(self):

        try:
            import docutils
            assert docutils
        except Exception:  # pragma: no cover
            self.skipTest('no docutils')

        s = """
            .. toc

            .. The section name contains trailing whitespace.

            ======
            top
            ======

            The top section.
        """
        # Perfect import must fail: The writer won't use the same underlines.
        p = self.run_test(s, check_flag=False)
        self.check_outline(p, (
            (0, '',  # check_outline ignores the first headline.
                '@language rest\n'
                '@tabwidth -4\n'
            ),
            (1, "!Dummy chapter",
                '.. toc\n'
                '\n'
                '.. The section name contains trailing whitespace.\n'
                '\n'
            ),
            (1, "top",
                '\n'
                'The top section.\n'
                '\n'
            ),
        ))
    #@+node:ekr.20210904065459.121: *3* TestRst.test_leo_rst
    def test_leo_rst(self):

        try:
            import docutils
            assert docutils
        except Exception:  # pragma: no cover
            self.skipTest('no docutils')

        # All heading must be followed by an empty line.
        s = """\
            #########
            Chapter 1
            #########

            It was a dark and stormy night.

            section 1
            +++++++++

            Sec 1.

            section 2
            +++++++++

            Sec 2.
        """
        # Perfect import must fail: The writer won't use the same underlines.
        p = self.run_test(s, check_flag=False)
        self.check_outline(p, (
            (0, '',  # check_outline ignores the first headline.
                    '@language rest\n'
                    '@tabwidth -4\n'
            ),
            (1, 'Chapter 1',
                    '\n'
                    'It was a dark and stormy night.\n'
                    '\n'
            ),
            (2, 'section 1',
                    '\n'
                    'Sec 1.\n'
                    '\n'
            ),
            (2, 'section 2',
                    '\n'
                    'Sec 2.\n'
                    '\n'
            ),
        ))
    #@-others
#@+node:ekr.20220814094900.1: ** class TestRust (BaseTestImporter)
class TestRust(BaseTestImporter):

    ext = '.rs'

    #@+others
    #@+node:ekr.20220814095025.1: *3* TestRust.test_1
    def test_1(self):

        s = """
            fn main() {
                let width1 = 30;
                let height1 = 50;

                println!(
                    "The area of the rectangle is {} square pixels.",
                    area(width1, height1)
                );
            }

            fn area(width: u32, height: u32) -> u32 {
                width * height
            }
        """
        p = self.run_test(s, strict_flag=True)
        # self.dump_tree(p, tag='Actual results...')
        self.check_outline(p, (
            (0, '', # check_outline ignores the first headline'
                    '@others\n'
                    '@language rust\n'
                    '@tabwidth -4\n'
            ),
            (1, 'fn main',
                    'fn main() {\n'
                    '    let width1 = 30;\n'
                    '    let height1 = 50;\n'
                    '\n'
                    '    println!(\n'
                    '        "The area of the rectangle is {} square pixels.",\n'
                    '        area(width1, height1)\n'
                    '    );\n'
                    '}\n'
                    '\n'
            ),
            (1, 'fn area',
                    'fn area(width: u32, height: u32) -> u32 {\n'
                    '    width * height\n'
                    '}\n'
                    '\n'
            ),
        ))
    #@-others
#@+node:ekr.20220813174450.1: ** class TestTcl (BaseTestImporter)
class TestTcl (BaseTestImporter):

    ext = '.tcl'

    #@+others
    #@+node:ekr.20220813174721.1: *3* TestTcl.test_1
    def test_1(self):

        s = r"""
            proc dumpFile { fileName { channel stdout } } {

                 # Open the file, and set up to process it in binary mode.
                 set f [open $fileName r]
                 fconfigure $f \
                     -translation binary \
                     -encoding binary \
                     -buffering full -buffersize 16384

                 close $f
                 return
             }

             # Main program

             if { [info exists argv0] && [string equal $argv0 [info script]] } {
                 foreach file $argv {
                     puts "$file:"
                     dumpFile $file
                 }
             }
        """
        p = self.run_test(s)
        # self.dump_tree(p, tag='Actual results...')
        self.check_outline(p, (
            (0, '', # check_outline ignores the first headline'
                    '@others\n'
                    ' # Main program\n'
                    '\n'
                    ' if { [info exists argv0] && [string equal $argv0 [info script]] } {\n'
                    '     foreach file $argv {\n'
                    '         puts "$file:"\n'
                    '         dumpFile $file\n'
                    '     }\n'
                    ' }\n'
                    '\n'
                    '@language tcl\n'
                    '@tabwidth -4\n'
            ),
            (1, 'proc dumpFile',
                    'proc dumpFile { fileName { channel stdout } } {\n'
                    '\n'
                    '     # Open the file, and set up to process it in binary mode.\n'
                    '     set f [open $fileName r]\n'
                    '     fconfigure $f \\\n'
                    '         -translation binary \\\n'
                    '         -encoding binary \\\n'
                    '         -buffering full -buffersize 16384\n'
                    '\n'
                    '     close $f\n'
                    '     return\n'
                    ' }\n'
                    '\n'
            ),
        ))
    #@-others
#@+node:ekr.20220809161015.1: ** class TestTreepad (BaseTestImporter)
class TestTreepad (BaseTestImporter):

    ext = '.hjt'

    #@+others
    #@+node:ekr.20220810141234.1: *3* test_treepad_1
    def test_treepad_1(self):

        # 5P9i0s8y19Z is a magic number.
        # The treepad writer always writes '<Treepad version 3.0>', but any version should work.
        s = self.dedent("""
            <Treepad version 2.7>
            dt=Text
            <node> 5P9i0s8y19Z
            headline 1
            0
            <end node>
            dt=Text
            <node> 5P9i0s8y19Z
            headline 2
            1
            node 2, line 1
            <end node>
        """)
        # For now, we don't guarantee round-tripping.
        p = self.run_test(s, check_flag=False)
        self.check_outline(p, (
            (0, '',  # check_outline ignores the first headline.
                '<Treepad version 3.0>\n'
                '@language plain\n'
                '@tabwidth -4\n'
            ),
            (1, 'headline 1', ''),
            (2, 'headline 2',
                    'node 2, line 1\n'
                    '\n'
            ),
        ))
    #@-others
#@+node:ekr.20211108083038.1: ** class TestTypescript (BaseTestImporter)
class TestTypescript(BaseTestImporter):

    ext = '.ts'

    #@+others
    #@+node:ekr.20210904065459.103: *3* TestTypescript.test_class
    def test_class(self):

        s = '''
            class Greeter {
                greeting: string;
                constructor (message: string) {
                    this.greeting = message;
                }
                greet() {
                    return "Hello, " + this.greeting;
                }
            }

            var greeter = new Greeter("world");

            var button = document.createElement('button')
            button.innerText = "Say Hello"
            button.onclick = function() {
                alert(greeter.greet())
            }

            document.body.appendChild(button)

        '''
        self.run_test(s)
    #@+node:ekr.20210904065459.104: *3* TestTypescript.test_module
    def test_module(self):
        s = '''
            module Sayings {
                export class Greeter {
                    greeting: string;
                    constructor (message: string) {
                        this.greeting = message;
                    }
                    greet() {
                        return "Hello, " + this.greeting;
                    }
                }
            }
            var greeter = new Sayings.Greeter("world");

            var button = document.createElement('button')
            button.innerText = "Say Hello"
            button.onclick = function() {
                alert(greeter.greet())
            }

            document.body.appendChild(button)
        '''
        self.run_test(s)
    #@-others
#@+node:ekr.20211108065014.1: ** class TestXML (BaseTestImporter)
class TestXML(BaseTestImporter):

    ext = '.xml'

    def setUp(self):
        super().setUp()
        c = self.c
        # Simulate @data import-xml-tags, with *only* standard tags.
        tags_list = ['html', 'body', 'head', 'div', 'table']
        settingsDict, junk = g.app.loadManager.createDefaultSettingsDicts()
        c.config.settingsDict = settingsDict
        c.config.set(c.p, 'data', 'import-xml-tags', tags_list, warn=True)

    #@+others
    #@+node:ekr.20210904065459.105: *3* TestXml.test_standard_opening_elements
    def test_standard_opening_elements(self):
        c = self.c
        s = """
            <?xml version="1.0" encoding="UTF-8"?>
            <!DOCTYPE note SYSTEM "Note.dtd">
            <html>
            <head>
                <title>Bodystring</title>
            </head>
            <body class='bodystring'>
            <div id='bodydisplay'></div>
            </body>
            </html>
        """
        table = (
            (1, "<html>"),
            (2, "<head>"),
            (2, "<body class='bodystring'>"),
        )
        p = c.p
        self.run_test(s)
        after = p.nodeAfterTree()
        root = p.lastChild()
        self.assertEqual(root.h, f"@file {self.short_id}")
        p = root.firstChild()
        for n, h in table:
            n2 = p.level() - root.level()
            self.assertEqual(h, p.h)
            self.assertEqual(n, n2)
            p.moveToThreadNext()
        self.assertEqual(p, after)
    #@+node:ekr.20210904065459.106: *3* TestXml.test_xml_1
    def test_xml_1(self):

        s = """
            <html>
            <head>
                <title>Bodystring</title>
            </head>
            <body class='bodystring'>
            <div id='bodydisplay'></div>
            </body>
            </html>
        """
        p = self.run_test(s)
        ### self.dump_tree(p, tag='Actual results...')
        self.check_outline(p, (
            (0, '@file TestXML.test_xml_1',  # Ignore level 0 headlines.
                    '@others\n'
                    '@language xml\n'
                    '@tabwidth -4\n'
            ),
            (1, '<html>',
                    '<html>\n'
                    '@others\n'
                    '</html>\n'
                    '\n'
            ),
            (2, '<head>',
                    '<head>\n'
                    '    <title>Bodystring</title>\n'
                    '</head>\n'
            ),
            (2, "<body class='bodystring'>",
                    "<body class='bodystring'>\n"
                    "<div id='bodydisplay'></div>\n"
                    '</body>\n'
            ),
        ))
    #@+node:ekr.20210904065459.108: *3* TestXml.test_non_ascii_tags
    def test_non_ascii_tags(self):
        s = """
            <:À.Ç>
            <Ì>
            <_.ÌÑ>
        """
        self.run_test(s)
    #@-others
#@-others
#@@language python
#@-leo

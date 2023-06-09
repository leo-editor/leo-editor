#@+leo-ver=5-thin
#@+node:ekr.20210904064440.2: * @file ../unittests/test_importers.py
"""Tests of leo/plugins/importers"""
import glob
import importlib
import textwrap
from leo.core import leoGlobals as g
from leo.core.leoNodes import Position
from leo.core.leoTest2 import LeoUnitTest
import leo.plugins.importers.coffeescript as cs
import leo.plugins.importers.coffeescript as coffeescript
import leo.plugins.importers.markdown as markdown
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
        g.app.write_black_sentinels = False

    #@+others
    #@+node:ekr.20220809054555.1: *3* BaseTestImporter.check_round_trip
    def check_round_trip(self, p: Position, s: str) -> None:
        """Assert that p's outline is equivalent to s."""
        c = self.c
        s = s.rstrip()  # Ignore trailing whitespace.
        result_s = c.atFileCommands.atAutoToString(p).rstrip()  # Ignore trailing whitespace.
        # Ignore leading whitespace and all blank lines.
        s_lines = [z.lstrip() for z in g.splitLines(s) if z.strip()]
        result_lines = [z.lstrip() for z in g.splitLines(result_s) if z.strip()]
        if s_lines != result_lines:
            g.trace('FAIL', g.caller(2))
            g.printObj([f"{i:<4} {z}" for i, z in enumerate(s_lines)], tag=f"expected: {p.h}")
            g.printObj([f"{i:<4} {z}" for i, z in enumerate(result_lines)], tag=f"results: {p.h}")
        self.assertEqual(s_lines, result_lines)
    #@+node:ekr.20211108044605.1: *3* BaseTestImporter.compute_unit_test_kind
    def compute_unit_test_kind(self, ext: str) -> str:
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
    #@+node:ekr.20230526124600.1: *3* BaseTestImporter.new_run_test
    def new_run_test(self, s: str, expected_results: tuple) -> None:
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
        test_s = textwrap.dedent(s).strip() + '\n'
        c.importCommands.createOutline(parent.copy(), ext, test_s)

        try:
            self.check_outline(parent, expected_results)
        except AssertionError:
            # Dump actual results, including bodies.
            self.dump_tree(parent, tag='Actual results...')
            raise
    #@+node:ekr.20230526135305.1: *3* BaseTestImporter.check_outline
    def check_outline(self, p: Position, expected: tuple) -> None:
        """
        BaseTestImporter.check_outline.
        
        Check that p's outline matches the expected results.
        
        Dump the actual outline if there is a mismatch.
        """
        p0_level = p.level()
        actual = [(z.level(), z.h, z.b) for z in p.self_and_subtree()]
        for i, actual in enumerate(actual):
            try:
                a_level, a_h, a_str = actual
                e_level, e_h, e_str = expected[i]
            except ValueError:
                assert False  # So we print the actual results.
            msg = f"FAIL in node {i} {e_h}"
            self.assertEqual(a_level - p0_level, e_level, msg=msg)
            if i > 0:  # Don't test top-level headline.
                self.assertEqual(e_h, a_h, msg=msg)
            self.assertEqual(g.splitLines(e_str), g.splitLines(a_str), msg=msg)
    #@+node:ekr.20230527075112.1: *3* BaseTestImporter.new_round_trip_test
    def new_round_trip_test(self, s: str, expected_s: str = None) -> None:
        p = self.run_test(s)
        self.check_round_trip(p, expected_s or s)
    #@+node:ekr.20211127042843.1: *3* BaseTestImporter.run_test
    def run_test(self, s: str) -> Position:
        """
        Run a unit test of an import scanner,
        i.e., create a tree from string s at location c.p.
        Return the created tree.
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
        test_s = textwrap.dedent(s).strip() + '\n'
        c.importCommands.createOutline(parent.copy(), ext, test_s)
        return parent
    #@-others
#@+node:ekr.20211108052633.1: ** class TestAtAuto (BaseTestImporter)
class TestAtAuto(BaseTestImporter):

    #@+others
    #@+node:ekr.20210904065459.122: *3* TestAtAuto.test_importers_can_be_imported
    def test_importers_can_be_imported(self):
        path = g.finalize_join(g.app.loadDir, '..', 'plugins', 'importers')
        assert g.os_path_exists(path), repr(path)
        pattern = g.finalize_join(path, '*.py')
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
        expected_results = (
            (0, '',  # check_outline ignores the first headline.
                '@others\n'
                '@language c\n'
                '@tabwidth -4\n'
            ),
            (1, 'class cTestClass1',
                'class cTestClass1 {\n'
                '    @others\n'
                '}\n'
            ),
            (2, 'func foo',
                'int foo (int a) {\n'
                '    a = 2 ;\n'
                '}\n'
            ),
            (2, 'func bar',
                'char bar (float c) {\n'
                '    ;\n'
                '}\n'
            ),
        )
        self.new_run_test(s, expected_results)
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
        expected_results = (
            (0, '',  # check_outline ignores the first headline.
                '@others\n'
                '@language c\n'
                '@tabwidth -4\n'
            ),
            (1, 'class cTestClass1',
                'class cTestClass1 {\n'
                '@others\n'
                '}\n'
            ),
            (2, 'func foo',
                '    int foo (int a) {\n'
                '// an underindented line.\n'
                '        a = 2 ;\n'
                '    }\n'
            ),
            (2, 'func bar',
                '    // This should go with the next function.\n'
                '\n'
                '    char bar (float c) {\n'
                '        ;\n'
                '    }\n'
            ),
        )
        self.new_run_test(s, expected_results)
    #@+node:ekr.20210904065459.5: *3* TestC.test_open_curly_bracket_on_next_line
    def test_open_curly_bracket_on_next_line(self):

        s = """
            void
            aaa::bbb::doit(awk* b)
            {
                assert(false);
            }

            bool
            aaa::bbb::dothat(xyz *b) // trailing comment.
            {
                return true;
            } // comment
        """
        expected_results = (
            (0, '',  # check_outline ignores the first headline.
                '@others\n'
                '@language c\n'
                '@tabwidth -4\n'
            ),
            (1, 'func doit',
                'void\n'
                'aaa::bbb::doit(awk* b)\n'
                '{\n'
                '    assert(false);\n'
                '}\n'
            ),
            (1, 'func dothat',
                'bool\n'
                'aaa::bbb::dothat(xyz *b) // trailing comment.\n'
                '{\n'
                '    return true;\n'
                '} // comment\n'
            ),
        )
        self.new_run_test(s, expected_results)
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
        expected_results = (
            (0, '',  # check_outline ignores the first headline.
                'extern "C"\n'
                '{\n'
                '#include "stuff.h"\n'
                'void    init(void);\n'
                '#include "that.h"\n'
                '}\n'
                '@language c\n'
                '@tabwidth -4\n'
            ),
        )
        self.new_run_test(s, expected_results)

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
        expected_results = (
            (0, '',  # check_outline ignores the first headline.
                'static void\n'
                'ReleaseCharSet(cset)\n'
                '    CharSet *cset;\n'
                '{\n'
                '    ckfree((char *)cset->chars);\n'
                '    if (cset->ranges) {\n'
                '    ckfree((char *)cset->ranges);\n'
                '    }\n'
                '}\n'
                '@language c\n'
                '@tabwidth -4\n'
            ),
        )
        self.new_run_test(s, expected_results)

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
        expected_results = (
            (0, '',  # check_outline ignores the first headline.
                'Tcl_Obj *\n'
                'Tcl_NewLongObj(longValue)\n'
                '    register long longValue; /* Long integer used to initialize the\n'
                '         * new object. */\n'
                '{\n'
                '    return Tcl_DbNewLongObj(longValue, "unknown", 0);\n'
                '}\n'
                '@language c\n'
                '@tabwidth -4\n'
            ),
        )
        self.new_run_test(s, expected_results)
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
        expected_results = (
            (0, '',  # check_outline ignores the first headline.
                '@others\n'
                '@language c\n'
                '@tabwidth -4\n'
            ),
            (1, 'func GetMax',
                    'template <class T>\n'
                    'T GetMax (T a, T b) {\n'
                    '  T result;\n'
                    '  result = (a>b)? a : b;\n'
                    '  return (result);\n'
                    '}\n'
            ),
        )
        self.new_run_test(s, expected_results)
    #@+node:ekr.20230510161130.1: *3* TestC.test_delete_comments_and_strings
    def test_delete_comments_and_strings(self):

        from leo.plugins.importers.c import C_Importer
        importer = C_Importer(self.c)

        lines = [
            'i = 1 // comment.\n',
            's = "string"\n',
            'if (/* a */1)\n',
            '    ;\n',
            '/*\n',
            '    if (1): a = 2\n',
            '*/\n',
            'i = 2\n'
        ]
        expected_lines = [
            'i = 1 \n',
            's = \n',
            'if (1)\n',
            '    ;\n',
            '\n',
            '\n',
            '\n',
            'i = 2\n'
        ]
        result = importer.delete_comments_and_strings(lines)
        self.assertEqual(len(result), len(expected_lines))
        self.assertEqual(result, expected_lines)
    #@+node:ekr.20230511044054.1: *3* TestC.test_find_blocks
    def test_find_blocks(self):

        from leo.plugins.importers.c import C_Importer
        trace = False
        importer = C_Importer(self.c)
        lines = g.splitLines(textwrap.dedent("""\
        
        # enable-trace
        
        namespace {
            n1;
        }
        
        namespace outer {
            n2;
        }
        
        int foo () {
            foo1;
            foo2;
        }
        
        class class1 {
            class1;
        }
        
        class class2 {
            x = 2;
            int bar (a, b) {
                if (0) {
                    a = 1;
                }
            }
        }
        """))
        importer.lines = lines
        importer.guide_lines = importer.make_guide_lines(lines)
        blocks = importer.find_blocks(i1=0, i2=len(lines))
        if trace:
            print('')
            g.trace('Blocks...')
            for z in blocks:
                kind, name, start, start_body, end = z
                print(f"{kind:>10} {name:<20} {start:4} {start_body:4} {end:4}")

        # The result lines must tile (cover) the original lines.
        result_lines = []
        for z in blocks:
            kind, name, start, start_body, end = z
            result_lines.extend(lines[start : end])
        self.assertEqual(lines, result_lines)
    #@+node:ekr.20230511073719.1: *3* TestC.test_codon_file
    def test_codon_file(self):
        # Test codon/codon/app/main.cpp.
        import os
        from leo.plugins.importers.c import C_Importer

        trace = False
        c = self.c
        importer = C_Importer(c)

        path = 'C:/Repos/codon/codon/app/main.cpp'
        if not os.path.exists(path):
            self.skipTest(f"Not found: {path!r}")
        with open(path, 'r') as f:
            source = f.read()
        lines = g.splitLines(source)
        if 1:  # Test gen_lines.
            importer.root = c.p
            importer.gen_lines(lines, c.p)
            if trace:
                for p in c.p.self_and_subtree():
                    g.printObj(p.b, tag=p.h)
        else: # Test find_blocks.
            importer.guide_lines = importer.make_guide_lines(lines)
            result = importer.find_blocks(0, len(importer.guide_lines))
            if trace:
                print('')
                g.trace()
                for z in result:
                    kind, name, start, start_body, end = z
                    print(f"{kind:>10} {name:<20} {start:4} {start_body:4} {end:4}")

            # The result lines must tile (cover) the original lines.
            result_lines = []
            for z in result:
                kind, name, start, start_body, end = z
                result_lines.extend(lines[start : end])
            self.assertEqual(lines, result_lines)
    #@+node:ekr.20230607164309.1: *3* TestC.test_struct
    def test_struct(self):
        # From codon soources.
        s = """
        struct SrcInfoAttribute : public Attribute {
          static const std::string AttributeName;

          std::unique_ptr<Attribute> clone(util::CloneVisitor &cv) const override {
            return std::make_unique<SrcInfoAttribute>(*this);
          }

        private:
          std::ostream &doFormat(std::ostream &os) const override { return os << info; }
        };
        """
        expected_results = (
            (0, '',  # check_outline ignores the first headline.
                '@others\n'
                '@language c\n'
                '@tabwidth -4\n'
            ),
            (1, 'struct SrcInfoAttribute',
                 'struct SrcInfoAttribute : public Attribute {\n'
                 '  static const std::string AttributeName;\n'
                 '\n'
                 '  std::unique_ptr<Attribute> clone(util::CloneVisitor &cv) const override {\n'
                 '    return std::make_unique<SrcInfoAttribute>(*this);\n'
                 '  }\n'
                 '\n'
                 'private:\n'
                 '  std::ostream &doFormat(std::ostream &os) const override { return os << info; }\n'
                 '};\n'
            ),
        )
        self.new_run_test(s, expected_results)
    #@-others
#@+node:ekr.20211108063520.1: ** class TestCoffeescript (BaseTextImporter)
class TestCoffeescript(BaseTestImporter):

    ext = '.coffee'

    #@+others
    #@+node:ekr.20210904065459.15: *3* TestCoffeescript.test_1
    #@@tabwidth -2 # Required

    def test_1(self):

        s = r"""
        # Js2coffee relies on Narcissus's parser.

        {parser} = @Narcissus or require('./narcissus_packed')

        # Main entry point

        buildCoffee = (str) ->
          str  = str.replace /\r/g, ''
          str += "\n"

          builder    = new Builder
          scriptNode = parser.parse str
        """

        expected_results = (
            (0, '',  # check_outline ignores the first headline.
                    '@others\n'
                    '@language coffeescript\n'
                    '@tabwidth -4\n'
            ),
            (1, 'def buildCoffee',
                    "# Js2coffee relies on Narcissus's parser.\n"
                    '\n'
                    "{parser} = @Narcissus or require('./narcissus_packed')\n"
                    '\n'
                    '# Main entry point\n'
                    '\n'
                    'buildCoffee = (str) ->\n'
                    "  str  = str.replace /\\r/g, ''\n"
                    '  str += "\\n"\n'
                    '\n'
                    '  builder    = new Builder\n'
                    '  scriptNode = parser.parse str\n'
            ),
        )
        self.new_run_test(s, expected_results)

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
        expected_results = (
          (0, '',  # check_outline ignores the first headline.
                '@others\n'
                '@language coffeescript\n'
                '@tabwidth -4\n'
          ),
          (1, 'class Builder',
                'class Builder\n'
                '  @others\n'
          ),
          (2, 'def constructor',
              'constructor: ->\n'
              '  @transformer = new Transformer\n'
          ),
          (2, 'def build',
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
          (2, 'def transform',
              '# `transform()`\n'
              '\n'
              'transform: (args...) ->\n'
              '  @transformer.transform.apply(@transformer, args)\n'
          ),
          (2, 'def body',
              '# `body()`\n'
              '\n'
              'body: (node, opts={}) ->\n'
              '  str = @build(node, opts)\n'
              '  str = blockTrim(str)\n'
              '  str = unshift(str)\n'
              '  if str.length > 0 then str else ""\n'
          ),
        )
        self.new_run_test(s, expected_results)
    #@+node:ekr.20211108085023.1: *3* TestCoffeescript.test_get_leading_indent
    def test_get_leading_indent(self):
        c = self.c
        importer = coffeescript.Coffeescript_Importer(c)
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
        expected_results = (
            (0, '',  # check_outline ignores the first headline.
                    '@others\n'
                    '@language csharp\n'
                    '@tabwidth -4\n'
            ),
            (1, 'unnamed namespace',
                    'namespace {\n'
                    '    @others\n'
                    '}\n'
            ),
            (2, 'class cTestClass1',
                    'class cTestClass1 {\n'
                    '    ;\n'
                    '}\n'
            ),
        )
        self.new_run_test(s, expected_results)
    #@+node:ekr.20210904065459.13: *3* TestCSharp.test_namespace_no_indent
    def test_namespace_no_indent(self):

        s = """
            namespace {
            class cTestClass1 {
                ;
            }
            }
        """
        expected_results = (
            (0, '',  # check_outline ignores the first headline.
                    '@others\n'
                    '@language csharp\n'
                    '@tabwidth -4\n'
            ),
            (1, 'unnamed namespace',
                    'namespace {\n'
                    '@others\n'
                    '}\n'
            ),
            (2, 'class cTestClass1',
                    'class cTestClass1 {\n'
                    '    ;\n'
                    '}\n'
            ),
        )
        self.new_run_test(s, expected_results)
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
        expected_results = (
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
            ),
        )
        self.new_run_test(s, expected_results)
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
        expected_results = (
            (0, '',  # check_outlines ignores the first headline.
                    '@others\n'
                    '@language cython\n'
                    '@tabwidth -4\n'
            ),
            (1, 'cdef double square_and_add',
                    'from libc.math cimport pow\n'
                    '\n'
                    'cdef double square_and_add (double x):\n'
                    '    """Compute x^2 + x as double.\n'
                    '\n'
                    '    This is a cdef function that can be called from within\n'
                    '    a Cython program, but not from Python.\n'
                    '    """\n'
                    '    return pow(x, 2.0) + x\n'
            ),
            (1, 'cpdef print_result',
                    'cpdef print_result (double x):\n'
                    '    """This is a cpdef function that can be called from Python."""\n'
                    '    print("({} ^ 2) + {} = {}".format(x, x, square_and_add(x)))\n'
            ),
        )
        self.new_run_test(s, expected_results)
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
        expected_results = (
            (0, '',  # check_outline ignores the first headline.
                    '@others\n'
                    '@language dart\n'
                    '@tabwidth -4\n'
            ),
            (1, 'function hello',
                    "var name = 'Bob';\n"
                    '\n'
                    'hello() {\n'
                    "  print('Hello, World!');\n"
                    '}\n'
            ),
            (1, 'function printNumber',
                    '// Define a function.\n'
                    'printNumber(num aNumber) {\n'
                    "  print('The number is $aNumber.'); // Print to console.\n"
                    '}\n'
            ),
            (1, 'function void main',
                    '// This is where the app starts executing.\n'
                    'void main() {\n'
                    '  var number = 42; // Declare and initialize a variable.\n'
                    '  printNumber(number); // Call a function.\n'
                    '}\n'
            ),
        )
        self.new_run_test(s, expected_results)
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
        expected_results = (
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
            ),
            (1, 'defun cde',
                    '; comment re cde\n'
                    '(defun cde (a b)\n'
                    '   (+ 1 2 3))\n'
            ),
        )
        self.new_run_test(s, expected_results)
    #@-others
#@+node:ekr.20211108064432.1: ** class TestHtml (BaseTestImporter)
class TestHtml(BaseTestImporter):

    ext = '.htm'

    def setUp(self):
        super().setUp()
        c = self.c
        # Simulate @data import-html-tags, with *only* standard tags.
        tags_list = ['html', 'body', 'head', 'div', 'script', 'table']
        settingsDict, junk = g.app.loadManager.createDefaultSettingsDicts()
        c.config.settingsDict = settingsDict
        c.config.set(c.p, 'data', 'import-html-tags', tags_list, warn=True)

    #@+others
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
            </script>
            <title>Brython</title>
            <link rel="stylesheet" href="Brython_files/doc_brython.css">
            </head>
            <body onload="brython({debug:1, cache:'none'})">
            <!-- comment -->
            </body>
            </html>
        '''

        expected_results = (
            (0, '',  # check_outline ignores the first headline.
                    '@others\n'
                    '@language html\n'
                    '@tabwidth -4\n'
            ),
            (1, '<html>',
                    '<!DOCTYPE html>\n'
                    '<html>\n'
                    '@others\n'
                    '</html>\n'
            ),
            (2, '<head>',
                    '<head>\n'
                    '@others\n'
                    '<title>Brython</title>\n'
                    '<link rel="stylesheet" href="Brython_files/doc_brython.css">\n'
                    '</head>\n'
            ),
            (3, '<script type="text/python3">',
                    '<script type="text/python3">\n'
                    '"""Code for the header menu"""\n'
                    'from browser import document as doc\n'
                    'from browser import html\n'
                    'import header\n'
                    '</script>\n'
            ),
            (2, """<body onload="brython({debug:1, cache:'none'})">""",
                    '<body onload="brython({debug:1, cache:\'none\'})">\n'
                    '<!-- comment -->\n'
                    '</body>\n'
            ),
        )
        self.new_run_test(s, expected_results)
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
        expected_results = (
            (0, '',  # check_outline ignores the first headline.
                    '@others\n'
                    '@language html\n'
                    '@tabwidth -4\n'
            ),
            (1, '<body>',
                    '<body>\n'
                    '@others\n'
                    '</p> <!-- orphan -->\n'
                    '\n'
                    '</body>\n'
            ),
            (2, '<div id="D666">Paragraph</p> <!-- P1 -->',
                    '<!-- OOPS: the div and p elements not properly nested.-->\n'
                    '<!-- OOPS: this table got generated twice. -->\n'
                    '\n'
                    '<p id="P1">\n'
                    '<div id="D666">Paragraph</p> <!-- P1 -->\n'
                    '@others\n'
                    '</div>\n'
            ),
            (3, '<TABLE id="T666"></TABLE></p> <!-- P2 -->',
                    '<p id="P2">\n'
                    '\n'
                    '<TABLE id="T666"></TABLE></p> <!-- P2 -->\n'
            ),    
        )
        self.new_run_test(s, expected_results)
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
        expected_results = (
            (0, '',  # check_outline ignores the first headline.
                    '@others\n'
                    '    <!-- oops: link elements terminated two different ways -->\n'
                    '    <link id="L1">\n'
                    '    <link id="L2">\n'
                    '    <link id="L3" />\n'
                    "    <link id='L4' />\n"
                    '\n'
                    '    <title>TITLE</title>\n'
                    '\n'
                    '<!-- oops: missing tags. -->\n'
                    '@language html\n'
                    '@tabwidth -4\n'
            ),
            (1, '<head>',
                    '<html>\n'
                    '\n'
                    '<head>\n'
            ),
        )
        self.new_run_test(s, expected_results)
    #@+node:ekr.20210904065459.19: *3* TestHtml.test_mixed_case_tags
    def test_mixed_case_tags(self):

        s = """
            <html>
            <HEAD>
                <title>Bodystring</title>
            </head>
            <body class="bodystring">
            <div id='bodydisplay'></div>
            </body>
            </HTML>
        """
        expected_results = (
            (0, '',  # check_outline ignores the first headline.
                    '@others\n'
                    '@language html\n'
                    '@tabwidth -4\n'
            ),
            (1, '<html>',
                    '<html>\n'
                    '@others\n'
                    '</HTML>\n'
            ),
            (2, '<HEAD>',  # We don't want to lowercase *all* headlines.
                    '<HEAD>\n'
                    '    <title>Bodystring</title>\n'
                    '</head>\n'
            ),
            (2, '<body class="bodystring">',
                    '<body class="bodystring">\n'
                    "<div id='bodydisplay'></div>\n"
                    '</body>\n'
            ),
        )
        self.new_run_test(s, expected_results)
    #@+node:ekr.20210904065459.20: *3* TestHtml.test_multiple_tags_on_a_line
    def test_multiple_tags_on_a_line(self):

        # pylint: disable=line-too-long
        #@+<< define s >>
        #@+node:ekr.20230126042723.1: *4* << define s >>
        # tags that cause nodes: html, head, body, div, table, nodeA, nodeB
        # NOT: tr, td, tbody, etc.
        s = """
            <html>
            <body>
                <table id="0">
                    <tr valign="top">
                    <td width="619">


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
                                <td class="blutopgrabot"><a href="href1">Listing Standards</a> |
                                    <a href="href2">Fees</a> |
                                    <strong>Non-compliant Issuers</strong> |
                                    <a href="href3">Form 25 Filings</a></td>
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
                    <!-- View First part -->
                    </td>
                    <td width="242">
                    <!-- View Second part -->
                    </td>
                    </tr></table>
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
        #@-<< define s >>

        # xml.preprocess_lines inserts several newlines.
        # Modify the expected result accordingly.
        expected_s = (s
            .replace('Form 25 Filings</a></td>\n', 'Form 25 Filings</a>\n</td>\n')
            .replace('</tr><tr>\n', '</tr>\n<tr>\n')
            .replace('</tr></table>\n', '</tr>\n</table>\n')
            .replace('<td class="blutopgrabot"><a', '<td class="blutopgrabot">\n<a')
            .replace('<noscript><img', '<noscript>\n<img')
        )
        self.new_round_trip_test(s, expected_s)
    #@+node:ekr.20210904065459.21: *3* TestHtml.test_multple_node_completed_on_a_line
    def test_multple_node_completed_on_a_line(self):

        s = """
            <!-- tags that start nodes: html,body,head,div,table,nodeA,nodeB -->
            <html><head>headline</head><body>body</body></html>
        """

        # xml.preprocess_lines inserts a newline between </head> and <body>.
        
        expected_results = (
            (0, '',
                    '@others\n'
                    '@language html\n'
                    '@tabwidth -4\n'
            ),
            (1, '<html>',
                    '<!-- tags that start nodes: html,body,head,div,table,nodeA,nodeB -->\n'
                    '<html>\n'
                    '<head>headline</head>\n'
                    '<body>body</body>\n'
                    '</html>\n'
            ),
        )
        self.new_run_test(s, expected_results)
    #@+node:ekr.20210904065459.22: *3* TestHtml.test_multple_node_starts_on_a_line
    def test_multple_node_starts_on_a_line(self):

        s = '''
            <html>
            <head>headline</head>
            <body>body</body>
            </html>
        '''
        expected_results = (
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
            ),
        )
        self.new_run_test(s, expected_results)
    #@+node:ekr.20230126023536.1: *3* TestHtml.test_slideshow_slide
    def test_slideshow_slide(self):

        # s is the contents of slides/basics/slide-002.html
        #@+<< define s >>
        #@+node:ekr.20230126031120.1: *4* << define s >>
        s = '''\
        <!DOCTYPE html>

        <html lang="en">
          <head>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0" /><meta name="generator" content="Docutils 0.19: https://docutils.sourceforge.io/" />

            <title>The workbook file &#8212; Leo 6.7.2 documentation</title>
            <link rel="stylesheet" type="text/css" href="../../_static/pygments.css" />
            <link rel="stylesheet" type="text/css" href="../../_static/classic.css" />
            <link rel="stylesheet" type="text/css" href="../../_static/custom.css" />

            <script data-url_root="../../" id="documentation_options" src="../../_static/documentation_options.js"></script>
            <script src="../../_static/doctools.js"></script>
            <script src="../../_static/sphinx_highlight.js"></script>

            <script src="../../_static/sidebar.js"></script>

            <link rel="index" title="Index" href="../../genindex.html" />
            <link rel="search" title="Search" href="../../search.html" />
            <link rel="next" title="Editing headlines" href="slide-003.html" />
            <link rel="prev" title="Leoâ€™s Basics" href="basics.html" />
          <!--
            EKR: Xml_Importer.preprocess_lines should insert put </head> and <body> on separate lines.
            As with this comment, there is a risk that preprocessing might affect comments...
          -->
          </head><body>
            <div class="related" role="navigation" aria-label="related navigation">
              <h3>Navigation</h3>
              <ul>
                <li class="right" style="margin-right: 10px">
                  <a href="../../genindex.html" title="General Index"
                     accesskey="I">index</a></li>
                <li class="right" >
                  <a href="slide-003.html" title="Editing headlines"
                     accesskey="N">next</a> |</li>
                <li class="right" >
                  <a href="basics.html" title="Leoâ€™s Basics"
                     accesskey="P">previous</a> |</li>
                <li class="nav-item nav-item-0"><a href="../../leo_toc.html">Leo 6.7.2 documentation</a> &#187;</li>
                  <li class="nav-item nav-item-1"><a href="../../toc-more-links.html" >More Leo Links</a> &#187;</li>
                  <li class="nav-item nav-item-2"><a href="../../slides.html" >Slides</a> &#187;</li>
                  <li class="nav-item nav-item-3"><a href="basics.html" accesskey="U">Leoâ€™s Basics</a> &#187;</li>
                <li class="nav-item nav-item-this"><a href="">The workbook file</a></li>
              </ul>
            </div>

            <div class="document">
              <div class="documentwrapper">
                <div class="bodywrapper">
                  <div class="body" role="main">

          <section id="the-workbook-file">
        <h1>The workbook file<a class="headerlink" href="#the-workbook-file" title="Permalink to this heading">Â¶</a></h1>
        <p>Leo opens the <strong>workbook file</strong> when you start
        Leo without a filename.</p>
        <p>The body has focusâ€“it is colored a pale pink, and
        contains a blinking cursor.</p>
        <p><strong>Note</strong>: on some monitors the colors will be almost
        invisible.  You can choose such colors to suit your
        taste.</p>
        <img alt="../../_images/slide-002.png" src="../../_images/slide-002.png" />
        </section>


                    <div class="clearer"></div>
                  </div>
                </div>
              </div>
              <div class="sphinxsidebar" role="navigation" aria-label="main navigation">
                <div class="sphinxsidebarwrapper">
                    <p class="logo"><a href="../../leo_toc.html">
                      <img class="logo" src="../../_static/LeoLogo.svg" alt="Logo"/>
                    </a></p>
          <div>
            <h4>Previous topic</h4>
            <p class="topless"><a href="basics.html"
                                  title="previous chapter">Leoâ€™s Basics</a></p>
          </div>
          <div>
            <h4>Next topic</h4>
            <p class="topless"><a href="slide-003.html"
                                  title="next chapter">Editing headlines</a></p>
          </div>
        <div id="searchbox" style="display: none" role="search">
          <h3 id="searchlabel">Quick search</h3>
            <div class="searchformwrapper">
            <form class="search" action="../../search.html" method="get">
              <input type="text" name="q" aria-labelledby="searchlabel" autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false"/>
              <input type="submit" value="Go" />
            </form>
            </div>
        </div>
        <script>document.getElementById('searchbox').style.display = "block"</script>
                </div>
        <div id="sidebarbutton" title="Collapse sidebar">
        <span>Â«</span>
        </div>

              </div>
              <div class="clearer"></div>
            </div>
            <div class="related" role="navigation" aria-label="related navigation">
              <h3>Navigation</h3>
              <ul>
                <li class="right" style="margin-right: 10px">
                  <a href="../../genindex.html" title="General Index"
                     >index</a></li>
                <li class="right" >
                  <a href="slide-003.html" title="Editing headlines"
                     >next</a> |</li>
                <li class="right" >
                  <a href="basics.html" title="Leoâ€™s Basics">previous</a> |</li>
                <li class="nav-item nav-item-0"><a href="../../leo_toc.html">Leo 6.7.2 documentation</a> &#187;</li>
                  <li class="nav-item nav-item-1"><a href="../../toc-more-links.html" >More Leo Links</a> &#187;</li>
                  <li class="nav-item nav-item-2"><a href="../../slides.html" >Slides</a> &#187;</li>
                  <li class="nav-item nav-item-3"><a href="basics.html" >Leoâ€™s Basics</a> &#187;</li>
                <li class="nav-item nav-item-this"><a href="">The workbook file</a></li>
              </ul>
            </div>
            <div class="footer" role="contentinfo">
                &#169; Copyright 1997-2023, Edward K. Ream.
              Last updated on January 24, 2023.
              Created using <a href="https://www.sphinx-doc.org/">Sphinx</a> 6.1.2.
            </div>
          </body>
        </html>
        '''
        #@-<< define s >>

        # xml.preprocess_lines inserts several newlines.
        # Modify the expected result accordingly.
        expected_s = (s
            .replace('</head><body>', '</head>\n<body>')
            .replace('><meta', '>\n<meta')
            .replace('index</a></li>', 'index</a>\n</li>')
            # .replace('"><a', '">\n<a')  # This replacement would affect too many lines.
            .replace('m-0"><a', 'm-0">\n<a')
            .replace('m-1"><a', 'm-1">\n<a')
            .replace('item-2"><a', 'item-2">\n<a')
            .replace('m-3"><a', 'm-3">\n<a')
            .replace('nav-item-this"><a', 'nav-item-this">\n<a')
            .replace('<p class="logo"><a', '<p class="logo">\n<a')
            .replace('</a></li>', '</a>\n</li>')
            .replace('<p><strong>', '<p>\n<strong>')
            .replace('</a></p>', '</a>\n</p>')
        )
        self.new_round_trip_test(s, expected_s)
    #@+node:ekr.20230123162321.1: *3* TestHtml.test_structure
    def test_structure(self):

        s = '''
            <html>
            <head>
                <meta charset="utf-8" />
            </head>
            <body>
                <div class="a">
                    <div class="a-1">
                        some text
                    </div>
                </div>
            </body>
            </html>
        '''
        expected_results = (
            (0, '',  # check_outline ignores the first headline.
                    '@others\n'
                    '@language html\n'
                    '@tabwidth -4\n'
            ),
            (1, '<html>',
                    '<html>\n'
                    '@others\n'
                    '</html>\n'
            ),
            (2, '<head>',
                    '<head>\n'
                    '    <meta charset="utf-8" />\n'
                    '</head>\n'
            ),
            (2, '<body>',
                     '<body>\n'
                     '    @others\n'
                     '</body>\n'
            ),
            (3, '<div class="a">',
                     '<div class="a">\n'
                     '    @others\n'
                     '</div>\n'
            ),
            (4, '<div class="a-1">',
                     '<div class="a-1">\n'
                     '    some text\n'
                     '</div>\n'
            ),
        )
        self.new_run_test(s, expected_results)
    #@+node:ekr.20210904065459.23: *3* TestHtml.test_underindented_comment
    def test_underindented_comment(self):

        s = r'''
            <table cellspacing="0" cellpadding="0" width="600" border="0">
                <!-- The indentation of this element causes the problem. -->
                <table>
            <div align="center">
            <iframe src="http://www.amex.com/index.jsp"</iframe>
            </div>
            </table>
            </table>
            <p>Paragraph</p>
        '''
        expected_results = (
            (0, '',  # check_outline ignores the first headline.
                    '@others\n'
                    '<p>Paragraph</p>\n'
                    '@language html\n'
                    '@tabwidth -4\n'
            ),
            (1, '<table cellspacing="0" cellpadding="0" width="600" border="0">',
                    '<table cellspacing="0" cellpadding="0" width="600" border="0">\n'
                    '@others\n'
                    '</table>\n'
            ),
            (2, '<table>',
                    '    <!-- The indentation of this element causes the problem. -->\n'
                    '    <table>\n'
                    '@others\n'
                    '</table>\n'
            ),
            (3, '<div align="center">',
                    '<div align="center">\n'
                    '<iframe src="http://www.amex.com/index.jsp"</iframe>\n'
                    '</div>\n'
            ),
        )
        self.new_run_test(s, expected_results)
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
        expected_results = (
            (0, '',  # check_outline ignores the first headline.
                '@others\n'
                '@language html\n'
                '@tabwidth -4\n'
            ),
            (1, '<HTML>',
                    '<HTML>\n'
                    '@others\n'
                    '</HTML>\n'
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
        )
        self.new_run_test(s, expected_results)
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
        self.run_test(s)
    #@-others
#@+node:ekr.20211108065916.1: ** class TestJava (BaseTestImporter)
class TestJava(BaseTestImporter):

    ext = '.java'

    #@+others
    #@+node:ekr.20210904065459.30: *3* TestJava.test_from_AdminPermission_java
    def test_from_AdminPermission_java(self):

        ### To do: allow '{' on following line.
        s = """
            /**
             * Indicates the caller's authority to perform lifecycle operations on
             */

            public final class AdminPermission extends BasicPermission {
                /**
                 * Creates a new <tt>AdminPermission</tt> object.
                 */
                public AdminPermission() {
                    super("AdminPermission");
                }
            }
        """
        expected_results = (
            (0, '',  # check_outline does not check the first outline.
                    '@others\n'
                    '@language java\n'
                    '@tabwidth -4\n'
            ),
            (1, 'class AdminPermission',
                    '/**\n'
                    " * Indicates the caller's authority to perform lifecycle operations on\n"
                    ' */\n'
                    '\n'
                    'public final class AdminPermission extends BasicPermission {\n'
                    '    @others\n'
                    '}\n'
            ),
            (2, 'func AdminPermission',
                    '/**\n'
                    ' * Creates a new <tt>AdminPermission</tt> object.\n'
                    ' */\n'
                    'public AdminPermission() {\n'
                    '    super("AdminPermission");\n'
                    '}\n'
            ),
        )
        self.new_run_test(s, expected_results)
    #@+node:ekr.20210904065459.31: *3* TestJava.test_from_BundleException_java
    def test_from_BundleException_java(self):

        s = """
            /*
             * $Header: /cvs/leo/test/unitTest.leo,v 1.247 2008/02/14 14:59:04 edream Exp $
             *
             */

            package org.osgi.framework;

            public class BundleException extends Exception {
                static final long serialVersionUID = 3571095144220455665L;
                /**
                 * Nested exception.
                 */
                private Throwable cause;

                public BundleException(String msg, Throwable cause) {
                    super(msg);
                    this.cause = cause;
                }
            }

        """
        expected_results = (
            (0, '',  # check_outline does not check the first outline.
                '@others\n'
                '@language java\n'
                '@tabwidth -4\n'
            ),
            (1, 'class BundleException',
                    '/*\n'
                    ' * $Header: /cvs/leo/test/unitTest.leo,v 1.247 2008/02/14 14:59:04 edream Exp $\n'
                    ' *\n'
                    ' */\n'
                    '\n'
                    'package org.osgi.framework;\n'
                    '\n'
                    'public class BundleException extends Exception {\n'
                    '    @others\n'
                    '}\n'
            ),
            (2, 'func BundleException',
                    'static final long serialVersionUID = 3571095144220455665L;\n'
                    '/**\n'
                    ' * Nested exception.\n'
                    ' */\n'
                    'private Throwable cause;\n'
                    '\n'
                    'public BundleException(String msg, Throwable cause) {\n'
                    '    super(msg);\n'
                    '    this.cause = cause;\n'
                    '}\n'
            ),
        )
        self.new_run_test(s, expected_results)

    #@+node:ekr.20210904065459.32: *3* TestJava.test_interface_test1
    def test_interface_test1(self):

        s = """
            interface Bicycle {
                void changeCadence(int newValue);
                void changeGear(int newValue);
            }
        """
        expected_results = (
            (0, '',  # check_outline ignores the first headline.
                'interface Bicycle {\n'
                '    void changeCadence(int newValue);\n'
                '    void changeGear(int newValue);\n'
                '}\n'
                '@language java\n'
                '@tabwidth -4\n'
            ),
        )
        self.new_run_test(s, expected_results)
    #@+node:ekr.20210904065459.33: *3* TestJava.test_interface_test2
    def test_interface_test2(self):

        s = """
            interface Bicycle {
            void changeCadence(int newValue);
            void changeGear(int newValue);
            }
        """
        expected_results = (
            (0, '',  # check_outline ignores the first headline.
                'interface Bicycle {\n'
                'void changeCadence(int newValue);\n'
                'void changeGear(int newValue);\n'
                '}\n'
                '@language java\n'
                '@tabwidth -4\n'
            ),
        )
        self.new_run_test(s, expected_results)
    #@-others
#@+node:ekr.20211108070310.1: ** class TestJavascript (BaseTestImporter)
class TestJavascript(BaseTestImporter):

    ext = '.js'

    #@+others
    #@+node:ekr.20210904065459.35: *3* TestJavascript.test_plain_function
    def test_plain_function(self):

        s = """
            // Restarting
            function restart() {
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
        
        expected_results = (
            (0, '',  # check_outline ignores the first headline.
                '@others\n'
                '@language javascript\n'
                '@tabwidth -4\n'
            ),
            (1, 'function restart',
                    '// Restarting\n'
                    'function restart() {\n'
                    '    invokeParamifier(params,"onstart");\n'
                    '    if(story.isEmpty()) {\n'
                    '        var tiddlers = store.filterTiddlers(store.getTiddlerText("DefaultTiddlers"));\n'
                    '        for(var t=0; t<tiddlers.length; t++) {\n'
                    '            story.displayTiddler("bottom",tiddlers[t].title);\n'
                    '        }\n'
                    '    }\n'
                    '    window.scrollTo(0,0);\n'
                    '}\n'
            ),
        )
        self.new_run_test(s, expected_results)
    #@+node:ekr.20210904065459.36: *3* TestJavascript.test var_equal_function
    def var_equal_function(self):

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

        expected_results = (
            (0, '',  # check_outline ignores the first headline.
                '@others\n'
                '@language javascript\n'
                '@tabwidth -4\n'
            ),
            (1, 'function restart',
                s
            ),
        )
        self.new_run_test(s, expected_results)
    #@+node:ekr.20220814014851.1: *3* TestJavascript.test_comments
    def test_comments(self):

        s = """
            /* Test of multi-line comments.
             * line 2.
             */
        """
        self.new_round_trip_test(s)
    #@+node:ekr.20210904065459.34: *3* TestJavascript.test_regex
    def test_regex(self):

        s = """
            String.prototype.toJSONString = function() {
                if(/["\\\\\\x00-\\x1f]/.test(this))
                    return '"' + this.replace(/([\\x00-\\x1f\\"])/g,replaceFn) + '"';

                return '"' + this + '"';
            };
            """
        self.new_round_trip_test(s)
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
        expected_results = (
            (0, '', # check_outline ignores the first headline'
                    '@others\n'
                    '\n'
                    'print("main", coroutine.resume(co, 1, 10))\n'
                    'print("main", coroutine.resume(co, "r"))\n'
                    'print("main", coroutine.resume(co, "x", "y"))\n'
                    'print("main", coroutine.resume(co, "x", "y"))\n'
                    '@language lua\n'
                    '@tabwidth -4\n'
            ),
            (1, 'function foo',
                    'function foo (a)\n'
                    '  print("foo", a)\n'
                    '  return coroutine.yield(2*a)\n'
                    'end\n'
            ),
            (1, 'function coroutine.create',
                    'co = coroutine.create(function (a,b)\n'
                    '      print("co-body", a, b)\n'
                    '      local r = foo(a+1)\n'
                    '      print("co-body", r)\n'
                    '      local r, s = coroutine.yield(a+b, a-b)\n'
                    '      print("co-body", r, s)\n'
                    '      return b, "end"\n'
                    'end)\n'
            ),
        )
        self.new_run_test(s, expected_results)
    #@-others
#@+node:ekr.20211108043230.1: ** class TestMarkdown (BaseTestImporter)
class TestMarkdown(BaseTestImporter):

    ext = '.md'
    treeType = '@auto-md'

    #@+others
    #@+node:ekr.20210904065459.109: *3* TestMarkdown.test_md_import
    def test_md_import(self):

        # Must be in standard form, with a space after '#'.
        s = """\
            # Top
            The top section

            ## Section 1
            section 1, line 1
            section 1, line 2

            ## Section 2
            section 2, line 1

            ### Section 2.1
            section 2.1, line 1

            #### Section 2.1.1
            section 2.2.1 line 1
            The next section is empty. It must not be deleted.

            ### Section 2.2

            ## Section 3
            Section 3, line 1
        """
        expected_results = (
            (0, '',  # check_outlines ignores the first headline.
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
            ),
        )
        self.new_run_test(s, expected_results)
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
        expected_results = (
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
            ),
        )
        self.new_run_test(s, expected_results)
    #@+node:ekr.20210904065459.111: *3* TestMarkdown.test_markdown_importer_basic
    def test_markdown_importer_basic(self):

        # Must be in standard form, with a space after '#'.
        s = """
            Decl line.
            # Header

            After header text

            ## Subheader

            Not an underline

            ----------------

            After subheader text

            # Last header: no text
        """
        expected_results = (
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
                ''
            ),
        )
        self.new_run_test(s, expected_results)
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
        expected_results = (
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
                ''
            ),
        )
        self.new_run_test(s, expected_results)
    #@+node:ekr.20210904065459.114: *3* TestMarkdown.test_markdown_github_syntax
    def test_markdown_github_syntax(self):

        # Must be in standard form, with a space after '#'.
        s = """
            Decl line.
            # Header

            ```python
            loads.init = {
                Chloride: 11.5,
                TotalP: 0.002,
            }
            ```
            # Last header
        """
        expected_results = (
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
                ''
            ),
        )
        self.new_run_test(s, expected_results)
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
        expected_results = (
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
            ),
        )
        self.new_run_test(s, expected_results)
    #@+node:ekr.20210904065459.46: *3* TestOrg.test_1074
    def test_1074(self):

        s = """
            *  Test
            First line.
        """
        expected_results = (
            (0, '',  # check_outline ignores the first headline.
                    '@language org\n'
                    '@tabwidth -4\n'
            ),
            (1, ' Test',
                    'First line.\n'
            ),
        )
        self.new_run_test(s, expected_results)
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
        expected_results = (
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
                    ''
            ),
        )
        self.new_run_test(s, expected_results)
    #@+node:ekr.20210904065459.44: *3* TestOrg.test_intro
    def test_intro(self):

        s = """
            Intro line.
            * Section 1
            Sec 1.
            * Section 2
            Sec 2.
        """
        expected_results = (
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
            ),
        )
        self.new_run_test(s, expected_results)
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
        expected_results = (
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
            ),
        )
        self.new_run_test(s, expected_results)
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
        expected_results = (
            (0, '',  # check_outline ignores the first headline.
                    '@language org\n'
                    '@tabwidth -4\n'
            ),
            (1, 'Section 1 :tag1:', ''),
            (1, 'Section 2 :tag2:', ''),
            (1, 'Section 3 :tag3:tag4:', ''),
        )
        self.new_run_test(s, expected_results)
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
        expected_results = (
            (0, '',  # check_outline ignores the first headline.
                # 'line in root node\n'
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
        )
        self.new_run_test(s, expected_results)
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
        expected_results = (
            (0, '',  # check_outline ignores the first headline.
                '@language otl\n'
                '@tabwidth -4\n'
            ),
            (1, 'Section 1', 'Sec 1.\n'),
            (1, 'Section 2', 'Sec 2.\n'),
            (2, 'placeholder level 2', ''),
            (3, 'Section 3', 'Sec 3.\n'),
        )
        self.new_run_test(s, expected_results)
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

        #@+<< define s >>
        #@+node:ekr.20230518071612.1: *4* << define s >>
        s = textwrap.dedent(
        """
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
        """).strip() + '\n'
        #@-<< define s >>
        
        expected_results = (
            (0, '',  # check_outline ignores the first headline.
                '@others\n'
                '@language pascal\n'
                '@tabwidth -4\n'
            ),
            (1, 'unit Unit1',
                    'unit Unit1;\n'
                    '\n'
                    'interface\n'
                    '\n'
                    'uses\n'
                    'Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls,\n'
                    'Forms,\n'
                    'Dialogs;\n'
                    '\n'
                    'type\n'
                    'TForm1 = class(TForm)\n'
            ),
            (1, 'procedure FormCreate',
                    'procedure FormCreate(Sender: TObject);\n'
                    'private\n'
                    '{ Private declarations }\n'
                    'public\n'
                    '{ Public declarations }\n'
                    'end;\n'
                    '\n'
                    'var\n'
                    'Form1: TForm1;\n'
                    '\n'
                    'implementation\n'
                    '\n'
                    '{$R *.dfm}\n'
                ),
            (1, 'procedure TForm1.FormCreate',
                    'procedure TForm1.FormCreate(Sender: TObject);\n'
                    'var\n'
                    'x,y: double;\n'
                    'begin\n'
                    'x:= 4;\n'
                    'Y := x/2;\n'
                    "z := 'abc'\n"
                    'end;\n'
                    '\n'
                    'end. // interface\n'
            ),
        )
        self.new_run_test(s, expected_results)
    #@+node:ekr.20220829221825.1: *3* TestPascal.test_indentation
    def test_indentation(self):

        # From GSTATOBJ.PAS
        #@+<< define s >>
        #@+node:ekr.20220830112013.1: *4* << define s >>
        s = textwrap.dedent(
        """
        unit gstatobj;

        {$F+,R-,S+}
        {$I numdirect.inc}

        interface
        uses gf2obj1;

        implementation

        procedure statObj.scale(factor: float);
        var i: integer;
        begin
           for i := 1 to num do
              with data^[i] do y := factor * y;
        end;

        procedure statObj.multiplyGraph(var source: pGraphObj);
        var i, max: integer;
        begin
        max := source^.getNum;
        if max < num then num := max;
        for i := 1 to max do
            data^[i].y := data^[i].y * pstatObj(source)^.data^[i].y;
        end;

        function statObj.divideGraph(var numerator: pGraphObj): boolean;
        var zerodata: boolean;
        i, j, max: integer;
        yy: float;
        pg: pStatObj;
        begin
        if numerator = nil then begin
            divideGraph := false;
            exit;
         end;
        zerodata:= false;
        new(pg,init);
        if pg = nil then begin
           divideGraph := false;
           exit;
         end;
        max := numerator^.getNum;
        if max < num then num := max;
        pg^.importData(@self);
        j := 0;
        for i := 1 to max do begin
            yy := pg^.sendYData(i);
            if yy <> 0 then begin
               inc(j);
               getYData(j, numerator^.sendYData(i)/yy);
               getXData(j, pg^.sendXData(i));
             end else zeroData := true;
         end;
        setNum(j);
        dispose(pg, byebye);
        divideGraph := not zeroData;
        end;

        procedure statObj.addGraph(var source: pgraphObj);
        var i, max: integer;
        begin
        max := source^.getNum;
        if max < num then num := max;
        for i := 1 to max do
            data^[i].y := data^[i].y + pstatObj(source)^.data^[i].y;
        end;
        """).strip() + '\n'
        #@-<< define s >>
        expected_results = (
            (0, '',  # check_outline ignores the first headline.
                    '@others\n'
                    '@language pascal\n'
                    '@tabwidth -4\n'
            ),
            (1, 'unit gstatobj',
                    'unit gstatobj;\n'
                    '\n'
                    '{$F+,R-,S+}\n'
                    '{$I numdirect.inc}\n'
                    '\n'
                    'interface\n'
                    'uses gf2obj1;\n'
                    '\n'
                    'implementation\n'
            ),
            (1, 'procedure statObj.scale',
                    'procedure statObj.scale(factor: float);\n'
                    'var i: integer;\n'
                    'begin\n'
                    '   for i := 1 to num do\n'
                    '      with data^[i] do y := factor * y;\n'
                    'end;\n'
                  
            ),
            (1, 'procedure statObj.multiplyGraph',
                    'procedure statObj.multiplyGraph(var source: pGraphObj);\n'
                    'var i, max: integer;\n'
                    'begin\n'
                    'max := source^.getNum;\n'
                    'if max < num then num := max;\n'
                    'for i := 1 to max do\n'
                    '    data^[i].y := data^[i].y * pstatObj(source)^.data^[i].y;\n'
                    'end;\n'
            ),
            (1, 'function statObj.divideGraph',
                    'function statObj.divideGraph(var numerator: pGraphObj): boolean;\n'
                    'var zerodata: boolean;\n'
                    'i, j, max: integer;\n'
                    'yy: float;\n'
                    'pg: pStatObj;\n'
                    'begin\n'
                    'if numerator = nil then begin\n'
                    '    divideGraph := false;\n'
                    '    exit;\n'
                    ' end;\n'
                    'zerodata:= false;\n'
                    'new(pg,init);\n'
                    'if pg = nil then begin\n'
                    '   divideGraph := false;\n'
                    '   exit;\n'
                    ' end;\n'
                    'max := numerator^.getNum;\n'
                    'if max < num then num := max;\n'
                    'pg^.importData(@self);\n'
                    'j := 0;\n'
                    'for i := 1 to max do begin\n'
                    '    yy := pg^.sendYData(i);\n'
                    '    if yy <> 0 then begin\n'
                    '       inc(j);\n'
                    '       getYData(j, numerator^.sendYData(i)/yy);\n'
                    '       getXData(j, pg^.sendXData(i));\n'
                    '     end else zeroData := true;\n'
                    ' end;\n'
                    'setNum(j);\n'
                    'dispose(pg, byebye);\n'
                    'divideGraph := not zeroData;\n'
                    'end;\n'
            ),
            (1, 'procedure statObj.addGraph',
                    'procedure statObj.addGraph(var source: pgraphObj);\n'
                    'var i, max: integer;\n'
                    'begin\n'
                    'max := source^.getNum;\n'
                    'if max < num then num := max;\n'
                    'for i := 1 to max do\n'
                    '    data^[i].y := data^[i].y + pstatObj(source)^.data^[i].y;\n'
                    'end;\n'
            ),
        )
        self.new_run_test(s, expected_results)
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
        expected_results = (
            (0, '',  # check_outline ignores the first headline.
                    '@others\n'
                    '            "ﬁ" =~ /fi/i;\n'
                    '\n'
                    '            $bar = "foo";\n'
                    '            if ($bar =~ /foo/){\n'
                    '               print "Second time is matching\n'
                    '";\n'
                    '            }else{\n'
                    '               print "Second time is not matching\n'
                    '";\n'
                    '            }\n'
                    '\n'
                    '            # Function call\n'
                    '            Hello();\n'
                    '@language perl\n'
                    '@tabwidth -4\n'
            ),
            (1, 'sub Hello',
                    '#!/usr/bin/perl\n'
                    '\n'
                    '            # Function definition\n'
                    '            sub Hello{\n'
                    '               print "Hello, World!\n'
                    '";\n'
                    '            }\n'
            ),
            (1, 'sub Test',
                    '            sub Test{\n'
                    '               print "Test!\n'
                    '";\n'
                    '            }\n'
            ),
        )
        self.new_run_test(s, expected_results)
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
        expected_results = (
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
                    '@language perl\n'
                    '@tabwidth -4\n'
            ),
        )
        self.new_run_test(s, expected_results)
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
        expected_results = (
            (0, '',  # check_outline ignores the first headline.
                    '@others\n'
                    '@language perl\n'
                    '@tabwidth -4\n'
            ),
            (1, 'sub Test',
                    '#!/usr/bin/perl\n'
                    '\n'
                    '            sub Test{\n'
                    '               print "Test!\n'
                    '";\n'
                    '            }\n'
            ),
            (1, 'sub World',
                    '            =begin comment\n'
                    '            sub World {\n'
                    '                print "This is not a funtion!"\n'
                    '            }\n'
            ),
            (1, 'sub Hello',
                    '            =cut\n'
                    '\n'
                    '            # Function definition\n'
                    '            sub Hello{\n'
                    '               print "Hello, World!\n'
                    '";\n'
                    '            }\n'
            ),
        )
        self.new_run_test(s, expected_results)
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
        expected_results = (
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
            ),
            (1, 'sub test2',
                    'sub test2 {\n'
                    '    s = m//}/;\n'
                    '}\n'
            ),
            (1, 'sub test3',
                    'sub test3 {\n'
                    '    s = s///}/;\n'
                    '}\n'
            ),
            (1, 'sub test4',
                    'sub test4 {\n'
                    '    s = tr///}/;\n'
                    '}\n'
            ),
        )
        self.new_run_test(s, expected_results)
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
        self.new_round_trip_test(s)
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
        self.new_round_trip_test(s)
        
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
        self.new_round_trip_test(s)
    #@-others
#@+node:ekr.20211108082509.1: ** class TestPython (BaseTestImporter)
class TestPython(BaseTestImporter):

    ext = '.py'

    #@+others
    #@+node:ekr.20230514195224.1: *3* TestPython.test_delete_comments_and_strings
    def test_delete_comments_and_strings(self):

        from leo.plugins.importers.python import Python_Importer
        importer = Python_Importer(self.c)

        lines = [
            'i = 1 # comment.\n',
            's = "string"\n',
            "s2 = 'string'\n",
            'if 1:\n',
            '    pass \n',
            '"""\n',
            '    if 1: a = 2\n',
            '"""\n',
            "'''\n",
            '    if 2: a = 2\n',
            "'''\n",
            'i = 2\n'
        ]
        expected_lines = [
            'i = 1 \n',
            's = \n',
            's2 = \n',
            'if 1:\n',
            '    pass \n',
            '\n',
            '\n',
            '\n',
            '\n',
            '\n',
            '\n',
            'i = 2\n'
        ]
        result = importer.delete_comments_and_strings(lines)
        self.assertEqual(len(result), len(expected_lines))
        self.assertEqual(result, expected_lines)
    #@+node:vitalije.20211206201240.1: *3* TestPython.test_general_test_1
    def test_general_test_1(self):

        s = (
        """
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
                def method21():
                    print(1)
                    print(2)
                    print(3)
                ATmyDecorator
                def method22():
                    pass
                def method23():
                    pass

            class UnderindentedComment:
            # Outer underindented comment
                def u1():
                # Underindented comment in u1.
                    pass

            # About main.

            def main():
                pass

            if __name__ == '__main__':
                main()
        """).replace('AT', '@')

        expected_results = (
            (0, '', # check_outline ignores the first headline'
                    '@others\n'
                    '\n'
                    "if __name__ == '__main__':\n"
                    '    main()\n'
                    '@language python\n'
                    '@tabwidth -4\n'
            ),
            (1, 'def f1',
                    'import sys\n'
                    'def f1():\n'
                    '    pass\n'
            ),
            (1, 'class Class1',
                       'class Class1:\n'
                       '    @others\n'
            ),
            (2, 'def method11',
                       'def method11():\n'
                       '    pass\n'
            ),
            (2, 'def method12',
                       'def method12():\n'
                       '    pass\n'
            ),
            (1, 'def f2',
                       '#\n'
                       '# Define a = 2\n'
                       'a = 2\n'
                       '\n'
                       'def f2():\n'
                       '    pass\n'
            ),
            (1, 'class Class2',
                       '# An outer comment\n'
                       '@myClassDecorator\n'
                       'class Class2:\n'
                       '    @others\n'
            ),
            (2, 'def method21',
                       'def method21():\n'
                       '    print(1)\n'
                       '    print(2)\n'
                       '    print(3)\n'
            ),
            (2, 'def method22',
                       '@myDecorator\n'
                       'def method22():\n'
                       '    pass\n'
            ),
            (2, 'def method23',
                       'def method23():\n'
                       '    pass\n'
            ),
            (1, 'class UnderindentedComment',
                'class UnderindentedComment:\n'
                '@others\n'  # The underindented comments prevents indentaion
            ),
            (2, 'def u1',
                    '# Outer underindented comment\n'
                    '    def u1():\n'
                    '    # Underindented comment in u1.\n'
                    '        pass\n'
            ),
            (1, 'def main',
                       '# About main.\n'
                       '\n'
                       'def main():\n'
                       '    pass\n'
            ),
        )
        self.new_run_test(s, expected_results)
    #@+node:vitalije.20211207200701.1: *3* TestPython.test_no_methods
    def test_no_methods(self):

        s = """
            class A:
                a=1
                b=2
                c=3
        """
        expected_results = (
            (0, '',  # check_outline ignores the first headline.
                   '@others\n'
                   '@language python\n'
                   '@tabwidth -4\n'
            ),
            (1, 'class A',
                   'class A:\n'
                   '    a=1\n'
                   '    b=2\n'
                   '    c=3\n'
            )
        )
        self.new_run_test(s, expected_results)
    #@+node:vitalije.20211206212507.1: *3* TestPython.test_oneliners
    def test_oneliners(self):
        s = """
            import sys
            def f1():
                pass
            
            class Class1:pass
            a = 2
            @dec_for_f2
            def f2(): pass
            
            
            class A: pass
            # About main.
            def main():
                pass
            
            if __name__ == '__main__':
                main()
        """

        # Note: new_gen_block deletes leading and trailing whitespace from all blocks.
        expected_results = (
            (0, '',  # check_outline ignores the first headline.
                    '@others\n'
                    '\n'
                    "if __name__ == '__main__':\n"
                    '    main()\n'
                    '@language python\n'
                    '@tabwidth -4\n'
            ),
            (1, 'def f1',
                    'import sys\n'
                    'def f1():\n'
                    '    pass\n'
            ),
            (1, 'class Class1',
                    'class Class1:pass\n'
            ),
            (1, 'def f2',
                    'a = 2\n'
                    '@dec_for_f2\n'
                    'def f2(): pass\n'
            ),
            (1, 'class A',
                    'class A: pass\n'
            ),
            (1, 'def main',
                       '# About main.\n'
                       'def main():\n'
                       '    pass\n'
            ),
        )
        self.new_run_test(s, expected_results)
    #@+node:ekr.20211202064822.1: *3* TestPython: test_nested_classes
    def test_nested_classes(self):
        s = """
            class TestCopyFile(unittest.TestCase):
                _delete = False
                a00 = 1
                class Faux(object):
                    _entered = False
                    _exited_with = None # type: tuple
                    _raised = False
            """
        # mypy/test-data/stdlib-samples/3.2/test/shutil.py
        expected_results = (
            (0, '',  # check_outline ignores the first headline.
                   '@others\n'
                   '@language python\n'
                   '@tabwidth -4\n'
            ),
            (1, 'class TestCopyFile',
                    'class TestCopyFile(unittest.TestCase):\n'
                    '    ATothers\n'.replace('AT', '@')
            ),
            (2, 'class Faux',
                        '_delete = False\n'
                        'a00 = 1\n'
                        'class Faux(object):\n'
                        '    _entered = False\n'
                        '    _exited_with = None # type: tuple\n'
                        '    _raised = False\n'
            ),
        )
        self.new_run_test(s, expected_results)
    #@+node:vitalije.20211207183645.1: *3* TestPython: test_strange_indentation
    def test_strange_indentation(self):
        s = """
            a = 1
            if 1:
             print('1')
            if 2:
              print('2')
            if 3:
               print('3')
            if 4:
                print('4')
            if 5:
                print('5')
            if 6:
                print('6')
            if 7:
                print('7')
            if 8:
                print('8')
            if 9:
                print('9')
            if 10:
                print('10')
            if 11:
                print('11')
            if 12:
                print('12')
        """
        expected_results = (
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
               "    print('12')\n"
               '@language python\n'
               '@tabwidth -4\n'
            ),
        )
        self.new_run_test(s, expected_results)
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
        expected_results = (
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
            ),
        )
        self.new_run_test(s, expected_results)
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
        expected_results = (
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
            ),
        )
        self.new_run_test(s, expected_results)
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
        expected_results = (
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
            ),
        )
        self.new_run_test(s, expected_results)
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
        expected_results = (
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
            ),
        )
        self.new_run_test(s, expected_results)
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
        expected_results = (
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
            ),
        )
        self.new_run_test(s, expected_results)
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
        expected_results = (
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
            ),
        )
        self.new_run_test(s, expected_results)
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
        expected_results = (
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
            ),
        )
        self.new_run_test(s, expected_results)
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
        expected_results = (
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
            ),
            (1, 'fn area',
                    'fn area(width: u32, height: u32) -> u32 {\n'
                    '    width * height\n'
                    '}\n'
            ),
        )
        self.new_run_test(s, expected_results)
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
        expected_results = (
            (0, '', # check_outline ignores the first headline'
                    '@others\n'
                    '\n'
                    ' # Main program\n'
                    '\n'
                    ' if { [info exists argv0] && [string equal $argv0 [info script]] } {\n'
                    '     foreach file $argv {\n'
                    '         puts "$file:"\n'
                    '         dumpFile $file\n'
                    '     }\n'
                    ' }\n'
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
            ),
        )
        self.new_run_test(s, expected_results)
    #@-others
#@+node:ekr.20220809161015.1: ** class TestTreepad (BaseTestImporter)
class TestTreepad (BaseTestImporter):

    ext = '.hjt'

    #@+others
    #@+node:ekr.20220810141234.1: *3* TestTreepad.test_treepad_1
    def test_treepad_1(self):

        # 5P9i0s8y19Z is a magic number.
        # The treepad writer always writes '<Treepad version 3.0>',
        # but any version should work.
        s = """
            <Treepad version 2.7>
            dt=Text
            <node> 5P9i0s8y19Z
            headline 1
            0
            node 1, line 1
            node 1, line 2
            <end node> 5P9i0s8y19Z
            dt=Text
            <node> 5P9i0s8y19Z
            headline 1.1
            1
            node 1.1, line 1
            <end node> 5P9i0s8y19Z
            dt=Text
            <node> 5P9i0s8y19Z
            headline 1.2
            1
            node 1.2, line 1
            node 1.2, line 2
            <end node> 5P9i0s8y19Z
            dt=Text
            <node> 5P9i0s8y19Z
            headline 2
            0
            node 2, line 1
            node 2, line 2
            <end node> 5P9i0s8y19Z
            dt=Text
            <node> 5P9i0s8y19Z
            headline 2.1.1
            3
            node 2.1.1, line 1
            node 2.1.1, line 2
            <end node> 5P9i0s8y19Z
        """
       
        expected_results = (
            (0, '',  # Ignore the first headline.
                '<Treepad version 2.7>\n'
                '@others\n'
                '@language plain\n'
                '@tabwidth -4\n'
            ),
            (1, 'headline 1',
                'node 1, line 1\n'
                'node 1, line 2\n'
            ),
            (2, 'headline 1.1',
                'node 1.1, line 1\n'
            ),
            (2, 'headline 1.2',
                'node 1.2, line 1\n'
                'node 1.2, line 2\n'
            ),
            (1, 'headline 2',
                'node 2, line 1\n'
                'node 2, line 2\n'
            ),
            (2, 'placeholder level 2', ''),
            (3, 'placeholder level 3', ''),
            (4, 'headline 2.1.1',
                'node 2.1.1, line 1\n'
                'node 2.1.1, line 2\n'
            ),  
        )
        self.new_run_test(s, expected_results)
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
        self.new_round_trip_test(s)
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
        self.new_round_trip_test(s)
    #@-others
#@+node:ekr.20211108065014.1: ** class TestXML (BaseTestImporter)
class TestXML(BaseTestImporter):

    ext = '.xml'

    def setUp(self):
        super().setUp()
        c = self.c
        # Simulate @data import-xml-tags, with *only* standard tags.
        tags_list = ['html', 'body', 'head', 'div', 'script', 'table']
        settingsDict, junk = g.app.loadManager.createDefaultSettingsDicts()
        c.config.settingsDict = settingsDict
        c.config.set(c.p, 'data', 'import-xml-tags', tags_list, warn=True)

    #@+others
    #@+node:ekr.20210904065459.105: *3* TestXml.test_standard_opening_elements
    def test_standard_opening_elements(self):

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
        
        expected_results = (
            (0, '',  # Ignore level 0 headlines.
                    '@others\n'
                    '@language xml\n'
                    '@tabwidth -4\n'
            ),
            (1, '<html>',
                    '<?xml version="1.0" encoding="UTF-8"?>\n'
                    '<!DOCTYPE note SYSTEM "Note.dtd">\n'
                    '<html>\n'
                        '@others\n'
                    '</html>\n'
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
        )
        self.new_run_test(s, expected_results)
    #@+node:ekr.20210904065459.106: *3* TestXml.test_xml_1
    def test_xml_1(self):

        s = """
            <html>
            <head>
                <title>Bodystring</title>
            </head>
            <body class='bodystring'>
            <div id='bodydisplay'>
            contents!
            </div>
            </body>
            </html>
        """
        expected_results = (
            (0, '',  # Ignore level 0 headlines.
                    '@others\n'
                    '@language xml\n'
                    '@tabwidth -4\n'
            ),
            (1, '<html>',
                    '<html>\n'
                    '@others\n'
                    '</html>\n'
            ),
            (2, '<head>',
                    '<head>\n'
                    '    <title>Bodystring</title>\n'
                    '</head>\n'
            ),
            (2, "<body class='bodystring'>",
                    "<body class='bodystring'>\n"
                    '@others\n'
                    '</body>\n'
            ),
            (3, "<div id='bodydisplay'>",
                    "<div id='bodydisplay'>\n"
                    'contents!\n'
                    '</div>\n'
            ),
        )
        self.new_run_test(s, expected_results)
    #@+node:ekr.20210904065459.108: *3* TestXml.test_non_ascii_tags
    def test_non_ascii_tags(self):
        s = """
            <:À.Ç>
            <Ì>
            <_.ÌÑ>
        """
        expected_results = (
            (0, '',  # Ignore level 0 headlines.
                 '<:À.Ç>\n'
                '<Ì>\n'
                '<_.ÌÑ>\n'
                '@language xml\n'
                '@tabwidth -4\n'
            ),
        )
        self.new_run_test(s, expected_results)
    #@-others
#@-others
#@@language python
#@-leo

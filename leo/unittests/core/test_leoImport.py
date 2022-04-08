# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20210904064440.2: * @file ../unittests/core/test_leoImport.py
#@@first
"""Tests of leoImport.py"""

import glob
import importlib
import sys
import textwrap
from leo.core import leoGlobals as g
from leo.core.leoTest2 import LeoUnitTest
# Import all tested scanners.
import leo.plugins.importers.coffeescript as cs
import leo.plugins.importers.dart as dart
import leo.plugins.importers.linescanner as linescanner
import leo.plugins.importers.markdown as markdown
import leo.plugins.importers.org as org
import leo.plugins.importers.otl as otl
import leo.plugins.importers.pascal as pascal
import leo.plugins.importers.xml as xml
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
    #@+node:ekr.20211128045212.1: *3* BaseTestImporter.check_headlines
    def check_headlines(self, p, table):
        """Check that p and its subtree have the structure given in the table."""
        # Check structure
        p1 = p.copy()
        try:
            self.assertEqual(p1.h, f"{self.treeType} {self.short_id}")
            i = 0
            for p in p1.subtree():
                self.assertTrue(i < len(table), msg=repr(p.h))
                data = table[i]
                i += 1
                n, h = data
                self.assertEqual(p.h, h)
                # Subtract 1 for compatibility with values in previous tables.
                self.assertEqual(p.level() - 1, n, msg=f"{p.h}: expected level {n}, got {p.level()}")
            # Make sure there are no extra nodes in p's tree.
            self.assertEqual(i, len(table), msg=f"i: {i}, len(table): {len(table)}")
        except AssertionError:  # pragma: no cover
            g.trace(self.short_id)
            self.dump_tree(p1)
            raise
    #@+node:ekr.20211126052156.1: *3* BaseTestImporter.compare_outlines
    def compare_outlines(self, created_p, expected_p):  # pragma: no cover
        """
        Ensure that the created and expected trees have equal shape and contents.

        Also ensure that all created nodes have the expected node kind.
        """
        d = g.vnode_info
        p1, p2 = created_p.copy(), expected_p.copy()
        try:
            after1, after2 = p1.nodeAfterTree(), p2.nodeAfterTree()
            while p1 and p2 and p1 != after1 and p2 != after2:
                aList1 = d.get(p1.v)['kind'].split(':')
                aList2 = d.get(p2.v)['kind'].split(':')
                kind1, kind2 = aList1[0], aList2[0]
                self.assertEqual(p1.h, p2.h)
                self.assertEqual(p1.numberOfChildren(), p2.numberOfChildren(), msg=p1.h)
                self.assertEqual(p1.b.strip(), p2.b.strip(), msg=p1.h)
                self.assertEqual(kind1, kind2, msg=p1.h)
                p1.moveToThreadNext()
                p2.moveToThreadNext()
            # Make sure both trees end at the same time.
            self.assertTrue(not p1 or p1 == after1)
            self.assertTrue(not p2 or p2 == after2)
        except AssertionError:
            g.es_exception()
            self.dump_tree(created_p, tag='===== Created')
            self.dump_tree(expected_p, tag='===== Expected')
            raise
    #@+node:ekr.20211108044605.1: *3* BaseTestImporter.compute_unit_test_kind
    def compute_unit_test_kind(self, ext):
        """Return kind from the given extention."""
        aClass = g.app.classDispatchDict.get(ext)
        kind = {'.md': '@auto-md'
               , '.org': '@auto-org'
               , '.otl': '@auto-otl'
               , '.rst': '@auto-rst'
               }.get(ext)
        if kind:
            return kind
        if aClass:
            d2 = g.app.atAutoDict
            for z in d2:
                if d2.get(z) == aClass:
                    return z  # pragma: no cover
        return '@file'
    #@+node:ekr.20211129062220.1: *3* BaseTestImporter.dump_tree
    def dump_tree(self, root, tag=None):  # pragma: no cover
        """Dump root's tree just as as Importer.dump_tree."""
        d = g.vnode_info  # Same as Importer.vnode_info!
        if tag:
            print(tag)
        for p in root.self_and_subtree():
            print('')
            print('level:', p.level(), p.h)
            lines = d[p.v]['lines'] if p.v in d else g.splitLines(p.v.b)
            g.printObj(lines)
    #@+node:ekr.20211127042843.1: *3* BaseTestImporter.run_test
    def run_test(self, s):
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
        ok = c.importCommands.createOutline(parent.copy(), ext, test_s)
        if not ok:  # pragma: no cover
            self.dump_tree(parent)
            self.fail('Perfect import failed')  # pragma: no cover
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
        self.check_headlines(p, (
            (1, 'class cTestClass1'),
            (2, 'int foo'),
            (2, 'char bar'),
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
        self.check_headlines(p, (
            (1, 'class cTestClass1'),
            (2, 'int foo'),
            (2, 'char bar'),
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
        self.check_headlines(p, (
            (1, 'void aaa::bbb::doit'),
            (1, 'bool aaa::bbb::dothat'),
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
        self.check_headlines(p, (
            (1, 'void aaa::bbb::doit'),
            (1, 'bool aaa::bbb::dothat'),
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
        self.check_headlines(p, (
            (1, 'extern "C"'),
        ))
    #@+node:ekr.20210904065459.7: *3* TestC.test_intermixed_blanks_and_tabs
    def test_intermixed_blanks_and_tabs(self):

        s = """
            void
            aaa::bbb::doit
                (
                awk* b  // leading blank
                )
            {
                assert(false); // leading tab
            }
        """
        p = self.run_test(s)
        self.check_headlines(p, (
            (1, 'void aaa::bbb::doit'),
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
        self.check_headlines(p, (
            (1, 'static void ReleaseCharSet'),
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
        self.check_headlines(p, (
            (1, 'Tcl_Obj * Tcl_NewLongObj'),
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
        self.check_headlines(p, (
            (1, 'buildCoffee = (str) ->'),
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
        self.check_headlines(p, (
          (1, 'class Builder'),
          (2, 'constructor: ->'),
          (2, 'build: (args...) ->'),
          (2, 'transform: (args...) ->'),
          (2, 'body: (node, opts={}) ->'),
        ))

    #@+node:ekr.20211108085023.1: *3* TestCoffeescript.test_get_leading_indent
    def test_get_leading_indent(self):
        c = self.c
        importer = linescanner.Importer(c.importCommands, language='coffeescript')
        self.assertEqual(importer.single_comment, '#')
    #@+node:ekr.20210904065459.126: *3* TestCoffeescript.test_scan_line
    def test_scan_line(self):
        c = self.c
        x = cs.CS_Importer(c.importCommands, atAuto=True)
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
        self.check_headlines(p, (
            (1, 'namespace'),
            (2, 'class cTestClass1'),
        ))
    #@+node:ekr.20210904065459.13: *3* TestImport.test_namespace_no_indent
    def test_namespace_no_indent(self):

        s = """
            namespace {
            class cTestClass1 {
                ;
            }
            }
        """
        p = self.run_test(s)
        self.check_headlines(p, (
            (1, 'namespace'),
            (2, 'class cTestClass1')
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
        p = self.run_test(s)
        self.check_headlines(p, (
            (1, 'Organizer: Declarations'),
            (1, 'double'),
            (1, 'print_result'),
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
        self.check_headlines(p, (
            (1, 'hello'),
            (1, 'printNumber'),
            (1, 'void main'),
        ))
    #@+node:ekr.20210904065459.127: *3* TestDart.test_clean_headline
    def test_clean_headline(self):
        c = self.c
        x = dart.Dart_Importer(c.importCommands, atAuto=False)
        table = (
            ('func(abc) {', 'func'),
            ('void foo() {', 'void foo'),
        )
        for s, expected in table:
            got = x.clean_headline(s)
            self.assertEqual(got, expected)
    #@-others
#@+node:ekr.20211108065659.1: ** class TestElisp (BaseTestImporter)
class TestElisp(BaseTestImporter):

    ext = '.el'

    #@+others
    #@+node:ekr.20210904065459.18: *3* TestElisp.test_1
    def test_1(self):

        s = """
            ;;; comment
            ;;; continue
            ;;;

            (defun abc (a b)
               (+ 1 2 3))

            ; comm
            (defun cde (a b)
               (+ 1 2 3))
        """
        p = self.run_test(s)
        self.check_headlines(p, (
            (1, 'defun abc'),
            (1, 'defun cde'),
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
        self.check_headlines(p, (
            (1, '<html>'),
            (2, '<head>'),
            (2, '<body class="bodystring">'),
        ))

    #@+node:ekr.20210904065459.20: *3* TestHtml.test_multiple_tags_on_a_line
    def test_multiple_tags_on_a_line(self):

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
        self.check_headlines(p, (
            (1, '<html>'),
            (2, '<body>'),
            (3, '<table id="0">'),
            (4, '<table id="2">'),
            (5, '<table id="3">'),
            (6, '<table id="4">'),
            (7, '<table id="6">'),
            (4, '<DIV class="webonly">'),
        ))

    #@+node:ekr.20210904065459.21: *3* TestHtml.test_multple_node_completed_on_a_line
    def test_multple_node_completed_on_a_line(self):

        s = """
            <!-- tags that start nodes: html,body,head,div,table,nodeA,nodeB -->
            <html><head>headline</head><body>body</body></html>
        """
        p = self.run_test(s)
        self.check_headlines(p, (
            # The new xml scanner doesn't generate any new nodes,
            # because the scan state hasn't changed at the end of the line!
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
        self.check_headlines(p, (
            (1, '<html>'),
            # (2, '<head>'),
            # (2, '<body>'),
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
        self.check_headlines(p, (
            (1, '<table cellspacing="0" cellpadding="0" width="600" border="0">'),
            (2, '<table>'),
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
        self.check_headlines(p, (
            (1, '<HTML>'),
            (2, '<HEAD>'),
            (2, "<BODY class='bodystring'>"),
            # (3, "<DIV id='bodydisplay'></DIV>"),
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
        self.check_headlines(p, (
            (1, '<body>'),
            (2, '<div id="D666">'),
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
        self.check_headlines(p, (
            (1, '<html>'),
            (2, '<head>'),
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
        self.check_headlines(p, (
            (1, '<html>'),
            (2, '<head>'),
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
        self.check_headlines(p, (
            (1, '<html>'),
            (2, '<head>'),
            (2, '<body onload="brython({debug:1, cache:\'none\'})">'),
        ))
    #@-others
#@+node:ekr.20211108062617.1: ** class TestIni (BaseTestImporter)
class TestIni(BaseTestImporter):

    ext = '.ini'

    #@+others
    #@+node:ekr.20210904065459.29: *3* TestIni.test_1
    def test_1(self):

        s = '''
            ; last modified 1 April 2001 by John Doe
            [owner]
            name=John Doe
            organization=Acme Widgets Inc.

            ; [ not a section ]

            [database]
            server=192.0.2.62
                ; use IP address
            port=143
            file = "payroll.dat"
        '''
        p = self.run_test(s)
        self.check_headlines(p, (
            (1, '[owner]'),
            (1, '[database]'),
        ))
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
        self.check_headlines(p, (
            (1, 'public final class AdminPermission extends BasicPermission'),
            (2, 'public AdminPermission'),
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
        self.check_headlines(p, (
            (1, 'public class BundleException extends Exception'),
            (2, 'public BundleException'),
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
        self.check_headlines(p, (
            (1, 'interface Bicycle'),
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
        self.check_headlines(p, (
            (1, 'interface Bicycle'),
        ))
    #@-others
#@+node:ekr.20211108070310.1: ** class TestJavascript (BaseTestImporter)
class TestJavascript(BaseTestImporter):

    ext = '.js'

    #@+others
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
        self.check_headlines(p, (
            (1, 'Top'),
            (2, 'Section 1'),
            (2, 'Section 2'),
            (3, 'Section 2.1'),
            (4, 'Section 2.1.1'),
            (3, 'Section 2.2'),
            (2, 'Section 3'),
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
        p = self.run_test(s)
        self.check_headlines(p, (
            (1, 'Top'),
            (2, 'Section 1'),
            (2, 'Section 2'),
            (3, 'Section 2.1'),
            (4, 'Section 2.1.1'),
            (3, 'Section 2.2'),
            (2, 'Section 3'),
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
        self.check_headlines(p, (
            (1, '!Declarations'),
            (1, 'Header'),
            (2, 'Subheader'),
            (1, 'Last header: no text'),
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
        # Implicit underlining *must* cause the perfect-import test to fail!
        g.app.suppressImportChecks = True
        p = self.run_test(s)
        self.check_headlines(p, (
            (1, '!Declarations'),
            (1, 'Header'),
            (2, 'Subheader'),
            (1, 'This *should* be a section'),
            (1, 'Last header: no text'),
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
        self.check_headlines(p, (
            (1, '!Declarations'),
            (1, 'Header'),
            (1, 'Last header'),
        ))
    #@+node:ekr.20210904065459.128: *3* TestMarkdown.test_is_hash
    def test_is_hash(self):
        c = self.c
        ic = c.importCommands
        x = markdown.Markdown_Importer(ic, atAuto=False)
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
        ic = c.importCommands
        x = markdown.Markdown_Importer(ic, atAuto=False)
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
        self.check_headlines(p, (
            (1, 'Section 1'),
            (1, 'Section 2'),
            (2, 'Section 2-1'),
            (3, 'Section 2-1-1'),
            (1, 'Section 3'),
            (2, 'Section 3.1'),
        ))

    #@+node:ekr.20210904065459.46: *3* TestOrg.test_1074
    def test_1074(self):

        s = """
            *  Test
            First line.
        """
        p = self.run_test(s)
        self.check_headlines(p, (
            (1, ' Test'),
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
        self.check_headlines(p, (
            (1, 'Events'),
            (2, '整理个人生活'),
            (3, '每周惯例'),
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
        self.check_headlines(p, (
            (1, 'Section 1'),
            (1, 'Section 2'),
        ))
    #@+node:ekr.20210904065459.41: *3* TestOrg.test_pattern
    def test_pattern(self):

        c = self.c
        x = org.Org_Importer(c.importCommands, atAuto=False)
        pattern = x.org_pattern
        table = (
            # 'body * line',
            '* line 1',
            '** level 2',
        )
        for line in table:
            m = pattern.match(line)
            # print('%20s ==> (%r)(%r)' % (line, m and m.group(1), m and m.group(2)))
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
        # Suppress perfect import checks.
        g.app.suppressImportChecks = True
        p = self.run_test(s)
        self.check_headlines(p, (
            (1, 'Section 1'),
            (1, 'Section 2'),
            (2, 'Section 2-1'),
            (3, 'Section 2-1-1'),
            (1, 'Section 3'),
            (2, 'placeholder'),
            (3, 'placeholder'),
            (4, 'placeholder'),
            (5, 'placeholder'),
            (6, 'Section 3-1-1-1-1-1'),
            (2, 'Section 3.1'),
        ))
    #@+node:ekr.20210904065459.43: *3* TestOrg.test_tags
    def test_tags(self):

        s = """
            * Section 1 :tag1:
            * Section 2 :tag2:
            * Section 3 :tag3:tag4:
        """
        p = self.run_test(s)
        self.check_headlines(p, (
            (1, 'Section 1 :tag1:'),
            (1, 'Section 2 :tag2:'),
            (1, 'Section 3 :tag3:tag4:'),
        ))
    #@-others
#@+node:ekr.20211108081327.1: ** class TestOtl (BaseTestImporter)
class TestOtl(BaseTestImporter):

    ext = '.otl'
    treeType = '@auto-otl'

    #@+others
    #@+node:ekr.20210904065459.49: *3* TestOtl.test_otl_1
    def test_otl_1(self):

        s = """\
            preamble.
            Section 1
            : Sec 1.
            Section 2
            : Sec 2.
            \tSection 2-1
            : Sec 2-1
            \t\tSection 2-1-1
            : Sect 2-1-1
            Section 3
            : Sec 3
            \tSection 3.1
            : Sec 3.1
        """
        p = self.run_test(s)
        self.check_headlines(p, (
            (1, 'preamble.'),
            (1, 'Section 1'),
            (1, 'Section 2'),
            (1, 'Section 2-1'),
            (1, 'Section 2-1-1'),
            (1, 'Section 3'),
            (1, 'Section 3.1'),
            (1, ''),  # Due to the added blank line?
        ))
    #@+node:ekr.20210904065459.48: *3* TestOtl.test_vim_outline_mode
    def test_vim_outline_mode(self):

        c = self.c
        x = otl.Otl_Importer(c.importCommands, atAuto=False)
        pattern = x.otl_pattern
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
            end;

            end. // interface
        """
        p = self.run_test(s)
        self.check_headlines(p, (
            (1, 'interface'),
            (2, 'procedure FormCreate'),
            (2, 'procedure TForm1.FormCreate'),
        ))
    #@+node:ekr.20210904065459.130: *3* TestPascal.test_methods
    def test_methods(self):

        c = self.c
        x = pascal.Pascal_Importer(c.importCommands, atAuto=False)
        table = (
            ('procedure TForm1.FormCreate(Sender: TObject);\n', 'procedure TForm1.FormCreate'),
        )
        state = g.Bunch(context='')
        for line, cleaned in table:
            assert x.starts_block(0, [line], state, state)
            self.assertEqual(x.clean_headline(line), cleaned)
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
        self.run_test(s)
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
        self.run_test(s)
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
        self.run_test(s)
    #@+node:ekr.20210904065459.54: *3* TestPerl.test_regex_1
    def test_regex_1(self):

        # ('len',   'tr///', '/',       context,  0,       0,       0),
        # ('len',   's///',  '/',       context,  0,       0,       0),
        # ('len',   'm//',   '/',       context,  0,       0,       0),
        # ('len',   '/',     '/',       '',       0,       0,       0),
        s = """
            #!/usr/bin/perl

            sub test1 {
                s = /{/g;
            }

            sub test2 {
                s = m//{/;
            }

            sub test3 {
                s = s///{/;
            }

            sub test4 {
                s = tr///{/;
            }
        """
        self.run_test(s)

    #@+node:ekr.20210904065459.55: *3* TestPerl.test_regex_2
    def test_regex_2(self):

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
        self.check_headlines(p, (
            (1, 'sub test1'),
            (1, 'sub test2'),
            (1, 'sub test3'),
            (1, 'sub test4'),
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

    #@+others
    #@+node:ekr.20211126055349.1: *3* TestPython.test_short_file
    def test_short_file(self):

        input_s = (
            '"""A docstring"""\n'
            'switch = 1\n'
            'print(3)\n'
            'print(6)\n'
            'def a():\n'
            '    pass\n'
            'print(7)\n'
        )
        exp_nodes = [(0, 'ignored h',
               '@language python\n'
               '@tabwidth -4\n'
               '"""A docstring"""\n'
               'switch = 1\n'
               'print(3)\n'
               'print(6)\n'
               'def a():\n'
               '    pass\n'
               'print(7)\n\n'
               )]
        p = self.run_test(input_s)
        ok, msg = self.check_outline(p, exp_nodes)
        assert ok, msg
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
        exp_nodes = [
            (0, 'ignored h', '@language python\n'
                             '@tabwidth -4\n'
                             'import sys\n'
                             '@others\n'
                             "if __name__ == '__main__':\n"
                             '    main()\n\n'
            ),
            (1, 'f1', 'def f1():\n'
                      '    pass\n'
                      '\n'
            ),
            (1, 'Class1', 'class Class1:\n'
                          '    def method11():\n'
                          '        pass\n'
                          '    def method12():\n'
                          '        pass\n'
                          '\n'
            ),
            (1, 'a = 2', 'a = 2\n\n'),
            (1, 'f2', 'def f2():\n'
                      '    pass\n'
                      '\n'
            ),
            (1, 'Class2', '# An outer comment\n'
                          '@myClassDecorator\n'
                          'class Class2:\n'
                          '    @myDecorator\n'
                          '    def method21():\n'
                          '        pass\n'
                          '    def method22():\n'
                          '        pass\n'
                          '\n'
            ),
            (1, 'main', '# About main.\n'
                        'def main():\n'
                        '    pass\n'
                        '\n'
            )
        ]
        p = self.run_test(s)
        ok, msg = self.check_outline(p, exp_nodes)
        assert ok, msg
    #@+node:vitalije.20211206201240.1: *3* TestPython.test_longer_classes
    def test_longer_classes(self):
        s = ('import sys\n'
              'def f1():\n'
              '    pass\n'
              '\n'
              'class Class1:\n'
              '    def method11():\n'
              '        pass\n'
              '    def method12():\n'
              '        pass\n'
              '        \n'
              '#\n'
              '# Define a = 2\n'
              'a = 2\n'
              '\n'
              'def f2():\n'
              '    pass\n'
              '\n'
              '# An outer comment\n'
              '@myClassDecorator\n'
              'class Class2:\n'
              '    def meth00():\n'
              '        print(1)\n'
              '        print(2)\n'
              '        print(3)\n'
              '        print(4)\n'
              '        print(5)\n'
              '        print(6)\n'
              '        print(7)\n'
              '        print(8)\n'
              '        print(9)\n'
              '        print(10)\n'
              '        print(11)\n'
              '        print(12)\n'
              '        print(13)\n'
              '        print(14)\n'
              '        print(15)\n'
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
        exp_nodes = [
                        (0, 'ignored h',
                                   '@language python\n'
                                   '@tabwidth -4\n'
                                   'import sys\n'
                                   '@others\n'
                                   "if __name__ == '__main__':\n"
                                   '    main()\n\n'
                        ),
                        (1, 'f1',
                                   'def f1():\n'
                                   '    pass\n'
                                   '\n'
                        ),
                        (1, 'Class1',
                                   'class Class1:\n'
                                   '    def method11():\n'
                                   '        pass\n'
                                   '    def method12():\n'
                                   '        pass\n'
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
                        (1, 'Class2',
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
                                   'def main():\n'
                                   '    pass\n'
                                   '\n'
                        )
        ]
        p = self.run_test(s)
        ok, msg = self.check_outline(p, exp_nodes)
        assert ok, msg
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
        exp_nodes = [(0, 'ignored h',
                               '@language python\n'
                               '@tabwidth -4\n'
                               'import sys\n'
                               '@others\n'
                               "if __name__ == '__main__':\n"
                               '    main()\n\n'
                    ),
                    (1, 'f1',
                               'def f1():\n'
                               '    pass\n'
                               '\n'
                    ),
                    (1, 'Class1',
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
                    (1, 'A',
                               'class A: pass\n'
                    ),
                    (1, 'main',
                               '# About main.\n'
                               'def main():\n'
                               '    pass\n'
                               '\n'
                    )
        ]
        p = self.run_test(s)
        ok, msg = self.check_outline(p, exp_nodes)
        assert ok, msg

    #@+node:ekr.20211202064822.1: *3* TestPython: test_nested_classes
    def test_nested_classes(self):
        txt = ('class TestCopyFile(unittest.TestCase):\n'
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
                '    class Faux(object):\n'
                '        _entered = False\n'
                '        _exited_with = None # type: tuple\n'
                '        _raised = False\n'
              )
        exp_nodes = [
            (0, 'ignored h',
                       '@language python\n'
                       '@tabwidth -4\n'
                       '@others\n'
            ),
            (1, 'TestCopyFile',
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
            (2, 'Faux',
                       'class Faux(object):\n'
                       '    _entered = False\n'
                       '    _exited_with = None # type: tuple\n'
                       '    _raised = False\n\n'
            )
        ]
        # mypy/test-data/stdlib-samples/3.2/test/shutil.py
        p = self.run_test(txt)
        ok, msg = self.check_outline(p, exp_nodes)
        assert ok, msg
    #@+node:vitalije.20211213125810.1: *3* TestPython: test_nested_classes
    def test_nested_classes_with_async(self):
        txt = ('class TestCopyFile(unittest.TestCase):\n'
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
        exp_nodes = [
            (0, 'ignored h',
                       '@language python\n'
                       '@tabwidth -4\n'
                       '@others\n'
            ),
            (1, 'TestCopyFile',
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
            (2, 'Faux',
                       'class Faux(object):\n'
                       '    _entered = False\n'
                       '    _exited_with = None # type: tuple\n'
                       '    _raised = False\n\n'
            )
        ]
        # mypy/test-data/stdlib-samples/3.2/test/shutil.py
        p = self.run_test(txt)
        ok, msg = self.check_outline(p, exp_nodes)
        assert ok, msg
    #@+node:ekr.20211202094115.1: *3* TestPython: test_strange_indentation
    def test_strange_indentation(self):
        txt = ('if 1:\n'
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
        exp_nodes = [
            (0, 'ignored h',
                       '@language python\n'
                       '@tabwidth -4\n'
                       'if 1:\n'
                       " print('1')\n"
                       'if 2:\n'
                       "  print('2')\n"
                       'if 3:\n'
                       "   print('3')\n"
                       '\n'
                       '@others\n'
            ),
            (1, 'StrangeClass',
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
        ]
        p = self.run_test(txt)
        ok, msg = self.check_outline(p, exp_nodes)
        assert ok, msg
    #@+node:vitalije.20211208210459.1: *3* TestPython: test_strange_indentation
    def test_strange_indentation_with_added_class_in_the_headline(self):
        self.c.config.set(None, 'bool', 'put-class-in-imported-headlines', True)
        txt = ('if 1:\n'
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
        exp_nodes = [
            (0, 'ignored h',
                       '@language python\n'
                       '@tabwidth -4\n'
                       'if 1:\n'
                       " print('1')\n"
                       'if 2:\n'
                       "  print('2')\n"
                       'if 3:\n'
                       "   print('3')\n"
                       '\n'
                       '@others\n'
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
        ]
        p = self.run_test(txt)
        ok, msg = self.check_outline(p, exp_nodes)
        assert ok, msg
    #@+node:vitalije.20211207183645.1: *3* TestPython: test_no_defs
    def test_no_defs(self):
        txt = ('a = 1\n'
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
        exp_nodes = [
            (0, 'ignored h', '@language python\n'
                               '@tabwidth -4\n'
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
                    )
        ]
        p = self.run_test(txt)
        ok, msg = self.check_outline(p, exp_nodes)
        assert ok, msg
    #@+node:vitalije.20211207185708.1: *3* TestPython: test_only_docs
    def test_only_docs(self):
        txt = ('class A:\n'
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
        exp_nodes = [
            (0, 'ignored h',
                       '@language python\n'
                       '@tabwidth -4\n'
                       '@others\n'
            ),
            (1, 'A',
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
        ]
        p = self.run_test(txt)
        ok, msg = self.check_outline(p, exp_nodes)
        assert ok, msg
    #@+node:vitalije.20211207200701.1: *3* TestPython: test_large_class_no_methods
    def test_large_class_no_methods(self):

        if sys.version_info < (3, 9, 0):
            self.skipTest('Requires Python 3.9')  # pragma: no cover

        txt = ('class A:\n'
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
        exp_nodes = [
            (0, 'ignored h',
                       '@language python\n'
                       '@tabwidth -4\n'
                       '@others\n'
            ),
            (1, 'A',
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
        ]
        p = self.run_test(txt)
        ok, msg = self.check_outline(p, exp_nodes)
        assert ok, msg
    #@+node:vitalije.20211213125307.1: *3* TestPython: test_large_class_no_methods
    def test_large_class_under_indented(self):
        txt = ('class A:\n'
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
        exp_nodes = [
            (0, 'ignored h',
                       '@language python\n'
                       '@tabwidth -4\n'
                       '@others\n'
            ),
            (1, 'A',
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
                       '\\\\-4.dummy2\n'
                       '\\\\-4.dummy3"""\n'
            )
        ]
        p = self.run_test(txt)
        ok, msg = self.check_outline(p, exp_nodes)
        assert ok, msg
    #@+node:vitalije.20211206180043.1: *3* check_outline
    def check_outline(self, p, nodes):
        it = iter(nodes)
        zlev = p.level()
        for p1 in p.self_and_subtree():
            lev, h, b = next(it)
            assert p1.level() - zlev == lev, f'lev:{p1.level()-zlev} != {lev}'
            if lev > 0:
                assert p1.h == h, f'"{p1.h}" != "{h}"'
            assert p1.b == b, f'\n{repr(p1.b)} !=\n{repr(b)}'
        try:
            next(it)
            return False, 'extra nodes'  # pragma: no cover
        except StopIteration:
            return True, 'ok'
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
        p = self.run_test(s)
        self.check_headlines(p, (
            (1, '!Dummy chapter'),
            (1, 'top'),
            (1, 'section 1'),
            (1, 'section 2'),
            (2, 'section 2.1'),
            (3, 'section 2.1.1'),
            (1, 'section 3'),
            (2, 'placeholder'),
            (3, 'section 3.1.1'),
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
        p = self.run_test(s)
        self.check_headlines(p, (
            (1, "!Dummy chapter"),
            (1, "Chapter"),
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
        p = self.run_test(s)
        self.check_headlines(p, (
            (1, '!Dummy chapter'),
            (1, 'top'),
            (1, 'section 1'),
            (1, 'section 2'),
            (2, 'section 2.1'),
            (3, 'section 2.1.1'),
            (1, 'section 3'),
            (2, 'placeholder'),
            (3, 'section 3.1.1'),
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
        p = self.run_test(s)
        self.check_headlines(p, (
            (1, '!Dummy chapter'),
            (1, 'top'),
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
        p = self.run_test(s)
        self.check_headlines(p, (
            (1, "!Dummy chapter"),
            (1, "top"),
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
        p = self.run_test(s)
        self.check_headlines(p, (
            (1, "!Dummy chapter"),
            (1, "top"),
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
        p = self.run_test(s)
        self.check_headlines(p, (
            (1, 'Chapter 1'),
            (2, 'section 1'),
            (2, 'section 2'),
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
    def test_xml_11(self):

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
        self.check_headlines(p, (
            (1, "<html>"),
            (2, "<head>"),
            (2, "<body class='bodystring'>"),
        ))
    #@+node:ekr.20210904065459.108: *3* TestXml.test_non_ascii_tags
    def test_non_ascii_tags(self):
        s = """
            <:À.Ç>
            <Ì>
            <_.ÌÑ>
        """
        self.run_test(s)
    #@+node:ekr.20210904065459.132: *3* TestXml.test_is_ws_line
    def test_is_ws_line(self):
        c = self.c
        x = xml.Xml_Importer(importCommands=c.importCommands, atAuto=False)
        table = (
           (1, ' \n'),
           (1, '\n'),
           (1, ' '),
           (1, '<!-- comment -->'),
           (0, '  <!-- comment --> Help'),
           (0, 'x <!-- comment -->'),
           (0, 'Help'),
        )
        for expected, line in table:
            got = x.is_ws_line(line)
            self.assertEqual(expected, got, msg=repr(line))
    #@+node:ekr.20210904065459.133: *3* TestXml.test_scan_line
    def test_scan_line(self):
        c = self.c
        x = xml.Xml_Importer(importCommands=c.importCommands, atAuto=False)
        x.start_tags.append('html')  # Don't rely on settings.
        table = (
            (0, '<tag>'),
            (0, '<tag></tag'),
            (1, '<html'),
            (1, '<html attrib="<">'),
            (0, '<html attrib="<" />'),
            (0, '<html>x</html>'),
            (0, '</br>'),  # Tag underflow
            (0, '<br />'),
            (0, '<br/>'),
        )
        for level, line in table:
            prev_state = x.state_class()  # Start in level 0
            self.assertEqual(prev_state.tag_level, 0, msg=line)
            new_state = x.scan_line(line, prev_state)
            self.assertEqual(new_state.tag_level, level, msg=line)
    #@-others
#@-others


#@-leo

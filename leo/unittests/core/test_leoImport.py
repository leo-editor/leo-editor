# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20210904064440.2: * @file ../unittests/core/test_leoImport.py
#@@first
"""Tests of leoImport.py"""

import glob
import importlib
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
import leo.plugins.importers.python as python
import leo.plugins.importers.xml as xml
#@+others
#@+node:ekr.20210904064440.3: ** class BaseTestImporter(LeoUnitTest)
class BaseTestImporter(LeoUnitTest):
    """The base class for tests of leoImport.py"""
    
    ext = None  # Subclasses must set this to the language's extension.
    
    def setUp(self):
        super().setUp()
        g.app.loadManager.createAllImporterData()
        
    def run_test(self, p, s):  # #2316: was ic.scannerUnitTest.
        """
        Run a unit test of an import scanner,
        i.e., create a tree from string s at location p.
        """
        c, ext = self.c, self.ext
        self.assertTrue(ext)
        self.treeType = '@file'  # Fix #352.
        fileName = 'test'
        # Run the test.
        parent = p.insertAsLastChild()
        kind = self.compute_unit_test_kind(ext)
        parent.h = f"{kind} {fileName}"
        c.importCommands.createOutline(parent=parent.copy(), ext=ext, s=s)

    #@+others
    #@+node:ekr.20211108044605.1: *3*  BaseTestImporter.compute_unit_test_kind
    def compute_unit_test_kind(self, ext):
        """Return kind from the given extention."""
        aClass = g.app.classDispatchDict.get(ext)
        if aClass:
            d2 = g.app.atAutoDict
            for z in d2:
                if d2.get(z) == aClass:
                    return z
        return '@file'
    #@-others
#@+node:ekr.20211108052633.1: ** class TestAtAuto (BaseTestImporter)
class TestAtAuto (BaseTestImporter):
    
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
    #@+node:ekr.20210904065459.3: *3* TestC.test_class_1
    def test_class_1(self):
        c = self.c
        s = textwrap.dedent("""\
            class cTestClass1 {

                int foo (int a) {
                    a = 2 ;
                }

                char bar (float c) {
                    ;
                }
            }
        """)
        table = (
            'class cTestClass1',
            'int foo',
            'char bar',
        )
        self.run_test(c.p, s)
        # Check structure
        root = c.p.lastChild()
        self.assertEqual(root.h, '@file test')
        p2 = root.firstChild()
        for h in table:
            self.assertEqual(p2.h, h)
            p2.moveToThreadNext()
        assert not root.isAncestorOf(p2), p2.h  # Extra nodes
    #@+node:ekr.20210904065459.4: *3* TestC.test_class_underindented_line
    def test_class_underindented_line(self):
        c = self.c
        s = textwrap.dedent("""\
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
        """)
        table = (
            'class cTestClass1',
            'int foo',
            'char bar',
        )
        self.run_test(c.p, s)
        # Check structure
        root = c.p.lastChild()
        self.assertEqual(root.h, '@file test')
        p2 = root.firstChild()
        for h in table:
            self.assertEqual(p2.h, h)
            p2.moveToThreadNext()
        assert not root.isAncestorOf(p2), p2.h  # Extra nodes
    #@+node:ekr.20210904065459.5: *3* TestC.test_comment_follows_arg_list
    def test_comment_follows_arg_list(self):
        c = self.c
        s = textwrap.dedent("""\
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
        """)
        table = (
            'void aaa::bbb::doit',
            'bool aaa::bbb::dothat',
        )
        self.run_test(c.p, s)
        # Check structure
        root = c.p.lastChild()
        self.assertEqual(root.h, '@file test')
        p2 = root.firstChild()
        for h in table:
            self.assertEqual(p2.h, h)
            p2.moveToThreadNext()
        assert not root.isAncestorOf(p2), p2.h  # Extra nodes
    #@+node:ekr.20210904065459.6: *3* TestC.test_comment_follows_block_delim
    def test_comment_follows_block_delim(self):
        c = self.c
        s = textwrap.dedent("""\
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
            } //  <---------------------problem
        """)
        table = (
            'void aaa::bbb::doit',
            'bool aaa::bbb::dothat',
        )
        self.run_test(c.p, s)
        # Check structure
        root = c.p.lastChild()
        self.assertEqual(root.h, '@file test')
        p2 = root.firstChild()
        assert p2, g.tree_to_string(c)
        for h in table:
            self.assertEqual(p2.h, h)
            p2.moveToThreadNext()
        assert not root.isAncestorOf(p2), p2.h  # Extra nodes
    #@+node:ekr.20210904065459.10: *3* TestC.test_extern
    def test_extern(self):
        c = self.c
        s = textwrap.dedent("""\
            extern "C"
            {
            #include "stuff.h"
            void    init(void);
            #include "that.h"
            }
        """)
        table = (
            'extern "C"',
        )
        p = c.p
        self.run_test(c.p, s)
        root = p.lastChild()
        self.assertEqual(root.h, '@file test')
        p2 = root.firstChild()
        for h in table:
            self.assertEqual(p2.h, h)
            p2.moveToThreadNext()
        assert not root.isAncestorOf(p2), p2.h  # Extra nodes
    #@+node:ekr.20210904065459.7: *3* TestC.test_intermixed_blanks_and_tabs
    def test_intermixed_blanks_and_tabs(self):
        c = self.c
        s = textwrap.dedent("""\
            void
            aaa::bbb::doit
                (
                awk* b  // leading blank
                )
            {
                assert(false); // leading tab
            }
        """)
        table = (
            'void aaa::bbb::doit',
        )

        self.run_test(c.p, s)
        root = c.p.lastChild()
        self.assertEqual(root.h, '@file test')
        p2 = root.firstChild()
        for h in table:
            self.assertEqual(p2.h, h)
            p2.moveToThreadNext()
        assert not root.isAncestorOf(p2), p2.h  # Extra nodes

    #@+node:ekr.20210904065459.8: *3* TestC.test_old_style_decl_1
    def test_old_style_decl_1(self):
        c = self.c
        s = textwrap.dedent("""\
            static void
            ReleaseCharSet(cset)
                CharSet *cset;
            {
                ckfree((char *)cset->chars);
                if (cset->ranges) {
                ckfree((char *)cset->ranges);
                }
            }
        """)
        table = (
            'static void ReleaseCharSet',
        )
        self.run_test(c.p, s)
        root = c.p.lastChild()
        self.assertEqual(root.h, '@file test', root.h)
        p2 = root.firstChild()
        for h in table:
            self.assertEqual(p2.h, h)
            p2.moveToThreadNext()
        assert not root.isAncestorOf(p2), p2.h  # Extra nodes
    #@+node:ekr.20210904065459.9: *3* TestC.test_old_style_decl_2
    def test_old_style_decl_2(self):
        c = self.c
        s = textwrap.dedent("""\
            Tcl_Obj *
            Tcl_NewLongObj(longValue)
                register long longValue;	/* Long integer used to initialize the
                     * new object. */
            {
                return Tcl_DbNewLongObj(longValue, "unknown", 0);
            }
        """)
        table = (
            'Tcl_Obj * Tcl_NewLongObj',
        )
        self.run_test(c.p, s)
        root = c.p.lastChild()
        self.assertEqual(root.h, '@file test')
        p2 = root.firstChild()
        for h in table:
            self.assertEqual(p2.h, h)
            p2.moveToThreadNext()
        assert not root.isAncestorOf(p2), p2.h  # Extra nodes
    #@-others
#@+node:ekr.20211108063520.1: ** class TestCoffeescript (BaseTextImporter)
class TestCoffeescript (BaseTestImporter):
    
    ext = '.coffee'
    
    #@+others
    #@+node:ekr.20210904065459.15: *3* TestCoffeescript.test_1
    def test_1(self):
        c = self.c
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
        table = (
            'buildCoffee = (str) ->',
        )
        self.run_test(c.p, s)
        p2 = c.p.firstChild().firstChild()
        for h in table:
            self.assertEqual(p2.h, h)
            p2.moveToThreadNext()
    #@+node:ekr.20210904065459.16: *3* TestCoffeescript.test_2
    #@@tabwidth -2 # Required

    def test_2(self):
        c = self.c

        s = textwrap.dedent("""\
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
        """)
        table = (
          'class Builder',
          'constructor: ->',
          'build: (args...) ->',
          'transform: (args...) ->',
          'body: (node, opts={}) ->',
        )
        self.run_test(c.p, s)
        p2 = c.p.firstChild().firstChild()
        for h in table:
            self.assertEqual(p2.h, h)
            p2.moveToThreadNext()
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
        c = self.c
        s = textwrap.dedent("""\
            namespace {
                class cTestClass1 {
                    ;
                }
            }
        """)
        table = (
            'namespace',
            'class cTestClass1',
        )
        self.run_test(c.p, s)
        root = c.p.firstChild()
        self.assertEqual(root.h, '@file test')
        p2 = root.firstChild()
        for i, h in enumerate(table):
            self.assertEqual(p2.h, h)
            p2.moveToThreadNext()
    #@+node:ekr.20210904065459.13: *3* TestImport.test_namespace_no_indent
    def test_namespace_no_indent(self):
        c = self.c
        s = textwrap.dedent("""\
            namespace {
            class cTestClass1 {
                ;
            }
            }
        """)
        self.run_test(c.p, s)
        table = (
            'namespace',
            'class cTestClass1',
        )
        root = c.p.firstChild()
        # assert root.h.endswith('c# namespace no indent'), root.h
        self.assertEqual(root.h, '@file test')
        p2 = root.firstChild()
        for i, h in enumerate(table):
            self.assertEqual(p2.h, h)
            p2.moveToThreadNext()
    #@-others
#@+node:ekr.20211108063908.1: ** class TestCython (BaseTestImporter)
class TestCython (BaseTestImporter):
    
    ext = '.pyx'
#@+node:ekr.20210904065459.11: *3* TestCython.test_importer
def test_importer(self):
    c = self.c
    s = textwrap.dedent('''\
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

    ''')
    table = (
        'Declarations',
        'double',
        'print_result',
    )
    self.run_test(c.p, s)
    root = c.p.lastChild()
    self.assertEqual(root.h, '@file test')
    p2 = root.firstChild()
    for h in table:
        self.assertEqual(p2.h, h)
        p2.moveToThreadNext()
    assert not root.isAncestorOf(p2), p2.h  # Extra nodes
#@+node:ekr.20211108064115.1: ** class TestDart (BaseTestImporter)
class TestDart (BaseTestImporter):
    
    ext = '.dart'
    
    #@+others
    #@+node:ekr.20210904065459.17: *3* TestDart.test_hello_world
    def test_hello_world(self):
        c = self.c
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
        table = (
            'hello',
            'printNumber',
            'void main',
        )
        self.run_test(c.p, s)
        root = c.p.firstChild()
        p2 = root.firstChild()
        for h in table:
            self.assertEqual(p2.h, h)
            p2.moveToThreadNext()
        assert not root.isAncestorOf(p2), p2.h  # Extra nodes

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
class TestElisp (BaseTestImporter):
    
    ext = '.el'
    
    #@+others
    #@+node:ekr.20210904065459.18: *3* TestElisp.test_1
    def test_1(self):
        c = self.c
        s = textwrap.dedent("""\
            ;;; comment
            ;;; continue
            ;;;

            (defun abc (a b)
               (+ 1 2 3))

            ; comm
            (defun cde (a b)
               (+ 1 2 3))
        """)
        table = (
            'defun abc',
            'defun cde',
        )
        self.run_test(c.p, s)
        root = c.p.lastChild()
        self.assertEqual(root.h, '@file test')
        p2 = root.firstChild()
        for h in table:
            self.assertEqual(p2.h, h)
            p2.moveToThreadNext()
        assert not root.isAncestorOf(p2), p2.h  # Extra nodes
    #@-others
#@+node:ekr.20211108064432.1: ** class TestHtml (BaseTestImporter)
class TestHtml (BaseTestImporter):
    
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
        c = self.c
        s = textwrap.dedent("""\
            <html>
            <head>
                <title>Bodystring</title>
            </head>
            <body class="bodystring">
            <div id='bodydisplay'></div>
            </body>
            </html>
        """)
        table = (
            '<html>',
            '<head>',
            '<body class="bodystring">',
        )
        self.run_test(c.p, s)
        root = c.p.firstChild()
        self.assertEqual(root.h, '@file test')
        p2 = root.firstChild()
        for h in table:
            self.assertEqual(p2.h, h)
            p2.moveToThreadNext()
    #@+node:ekr.20210904065459.20: *3* TestHtml.test_multiple_tags_on_a_line
    def test_multiple_tags_on_a_line(self):
        c = self.c
        # tags that cause nodes: html, head, body, div, table, nodeA, nodeB
        # NOT: tr, td, tbody, etc.
        s = textwrap.dedent("""\
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
        """)
        table = (
            '<html>',
            '<body>',
            '<table id="0">',
        )
        self.run_test(c.p, s)
        p2 = c.p.firstChild().firstChild()
        for h in table:
            self.assertEqual(p2.h, h)
            p2.moveToThreadNext()
    #@+node:ekr.20210904065459.21: *3* TestHtml.test_multple_node_completed_on_a_line
    def test_multple_node_completed_on_a_line(self):
        c = self.c

        s = textwrap.dedent("""\
            <!-- tags that start nodes: html,body,head,div,table,nodeA,nodeB -->
            <html><head>headline</head><body>body</body></html>
        """)
        table = (
            # The new xml scanner doesn't generate any new nodes,
            # because the scan state hasn't changed at the end of the line!
        )
        self.run_test(c.p, s)
        p2 = c.p.firstChild().firstChild()
        for h in table:
            assert p2
            self.assertEqual(p2.h, h)
            p2.moveToThreadNext()
    #@+node:ekr.20210904065459.22: *3* TestHtml.test_multple_node_starts_on_a_line
    def test_multple_node_starts_on_a_line(self):
        c = self.c
        s = '''
        @language html
        <html>
        <head>headline</head>
        <body>body</body>
        </html>
        '''
        table = (
            '<html>',
        )
        self.run_test(c.p, s)
        p2 = c.p.firstChild().firstChild()
        for h in table:
            assert p2
            self.assertEqual(p2.h, h)
            p2.moveToThreadNext()
    #@+node:ekr.20210904065459.23: *3* TestHtml.test_underindented_comment
    def test_underindented_comment(self):
        c = self.c
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
        table = (
            '<table cellspacing="0" cellpadding="0" width="600" border="0">',
            '<table>',
        )
        self.run_test(c.p, s)
        p2 = c.p.firstChild().firstChild()
        for h in table:
            self.assertEqual(p2.h, h)
            p2.moveToThreadNext()


    #@+node:ekr.20210904065459.24: *3* TestHtml.test_uppercase_tags
    def test_uppercase_tags(self):
        c = self.c
        s = textwrap.dedent("""\
            <HTML>
            <HEAD>
                <title>Bodystring</title>
            </HEAD>
            <BODY class='bodystring'>
            <DIV id='bodydisplay'></DIV>
            </BODY>
            </HTML>
        """)
        self.run_test(c.p, s)
    #@+node:ekr.20210904065459.25: *3* TestHtml.test_improperly_nested_tags
    def test_improperly_nested_tags(self):
        c = self.c
        s = textwrap.dedent("""\
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
        """)
        table = (
            ('<body>'),
            ('<div id="D666">'),
        )

        self.run_test(c.p, s)
        p2 = c.p.firstChild().firstChild()
        for h in table:
            self.assertEqual(p2.h, h)
            p2.moveToThreadNext()

    #@+node:ekr.20210904065459.26: *3* TestHtml.test_improperly_terminated_tags
    def test_improperly_terminated_tags(self):
        c = self.c
        s = r'''
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
        table = (
            '<html>',
            '<head>',
        )
        self.run_test(c.p, s)
        p2 = c.p.firstChild().firstChild()
        for i, h in enumerate(table):
            self.assertEqual(p2.h, h)
            p2.moveToThreadNext()
    #@+node:ekr.20210904065459.27: *3* TestHtml.test_improperly_terminated_tags2
    def test_improperly_terminated_tags2(self):
        c = self.c
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
        table = ('<html>', '<head>')  # , '<link id="L1">'
        self.run_test(c.p, s)
        p2 = c.p.firstChild().firstChild()
        for h in table:
            self.assertEqual(p2.h, h)
            p2.moveToThreadNext()
    #@+node:ekr.20210904065459.28: *3* TestHtml.test_brython
    def test_brython(self):
        c = self.c
        # https://github.com/leo-editor/leo-editor/issues/479
        s = textwrap.dedent('''\
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
        ''')
        table = (
            '<html>',
            '<head>',
            '<body onload="brython({debug:1, cache:\'none\'})">',
        )
        self.run_test(c.p, s)
        p2 = c.p.firstChild().firstChild()
        assert p2
        for h in table:
            self.assertEqual(p2.h, h)
            p2.moveToThreadNext()

    #@-others
#@+node:ekr.20211108062617.1: ** class TestIni (BaseTestImporter)
class TestIni(BaseTestImporter):
    
    ext = '.ini'
    
    #@+others
    #@+node:ekr.20210904065459.29: *3* TestIni.test_1
    def test_1(self):
        c = self.c
        s = textwrap.dedent(r'''\
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
        ''')
        table = ('[owner]', '[database]')
        self.run_test(c.p, s)
        root = c.p.firstChild()
        p2 = root.firstChild()
        for h in table:
            self.assertEqual(p2.h, h)
            p2.moveToThreadNext()
        assert not root.isAncestorOf(p2), p2.h  # Extra nodes
    #@-others
#@+node:ekr.20211108065916.1: ** class TestJava (BaseTestImporter)
class TestJava (BaseTestImporter):
    
    ext = '.java'
    
    #@+others
    #@+node:ekr.20210904065459.30: *3* TestJava.test_from_AdminPermission_java
    def test_from_AdminPermission_java(self):
        c = self.c
        s = textwrap.dedent("""\
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
        """)
        table = (
            'public final class AdminPermission extends BasicPermission',
            'public AdminPermission',
        )
        self.run_test(c.p, s)
        root = c.p.lastChild()
        self.assertEqual(root.h, '@file test')
        p2 = root.firstChild()
        for i, h in enumerate(table):
            self.assertEqual(p2.h, h)
            p2.moveToThreadNext()
        assert not root.isAncestorOf(p2), p2.h  # Extra nodes

    #@+node:ekr.20210904065459.31: *3* TestJava.test_from_BundleException_java
    def test_from_BundleException_java(self):
        c = self.c
        s = textwrap.dedent("""\
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
                static final long	serialVersionUID	= 3571095144220455665L;
                /**
                 * Nested exception.
                 */
                private Throwable	cause;

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

        """)
        table = (
            'public class BundleException extends Exception',
            'public BundleException',
        )
        self.run_test(c.p, s)
        root = c.p.lastChild()
        self.assertEqual(root.h, '@file test')
        p2 = root.firstChild()
        for i, h in enumerate(table):
            self.assertEqual(p2.h, h)
            p2.moveToThreadNext()
        assert not root.isAncestorOf(p2), p2.h  # Extra nodes
    #@+node:ekr.20210904065459.32: *3* TestJava.test_interface_test1
    def test_interface_test1(self):
        c = self.c
        s = textwrap.dedent("""\
            interface Bicycle {
                void changeCadence(int newValue);
                void changeGear(int newValue);
            }
        """)
        table = (
            'interface Bicycle',
        )
        self.run_test(c.p, s)
        root = c.p.lastChild()
        self.assertEqual(root.h, '@file test')
        p2 = root.firstChild()
        for i, h in enumerate(table):
            self.assertEqual(p2.h, h)
            p2.moveToThreadNext()
        assert not root.isAncestorOf(p2), p2.h  # Extra nodes
    #@+node:ekr.20210904065459.33: *3* TestJava.test_interface_test2
    def test_interface_test2(self):
        c = self.c
        s = textwrap.dedent("""\
            interface Bicycle {
            void changeCadence(int newValue);
            void changeGear(int newValue);
            }
        """)
        table = (
            'interface Bicycle',
        )
        self.run_test(c.p, s)
        root = c.p.lastChild()
        self.assertEqual(root.h, '@file test')
        p2 = root.firstChild()
        for i, h in enumerate(table):
            self.assertEqual(p2.h, h)
            p2.moveToThreadNext()
        assert not root.isAncestorOf(p2), p2.h  # Extra nodes
    #@-others
#@+node:ekr.20211108070310.1: ** class TestJavascript (BaseTestImporter)
class TestJavascript (BaseTestImporter):
    
    ext = '.js'
    
    #@+others
    #@+node:ekr.20210904065459.34: *3* TestJavascript.test_regex_1
    def test_regex_1(self):
        c = self.c
        s = textwrap.dedent("""\
            String.prototype.toJSONString = function()
            {
                if(/["\\\\\\x00-\\x1f]/.test(this))
                    return '"' + this.replace(/([\\x00-\\x1f\\"])/g,replaceFn) + '"';

                return '"' + this + '"';
            };
        """)
        self.run_test(c.p, s)
    #@+node:ekr.20210904065459.35: *3* TestJavascript.test_3
    def test_3(self):
        c = self.c
        s = textwrap.dedent("""\
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
        """)
        self.run_test(c.p, s)
    #@+node:ekr.20210904065459.36: *3* TestJavascript.test_4
    def test_4(self):
        c = self.c
        s = textwrap.dedent("""\
            var c3 = (function () {
                "use strict";

                // Globals
                var c3 = { version: "0.0.1"   };

                c3.someFunction = function () {
                    console.log("Just a demo...");
                };

                return c3;
            }());
        """)
        self.run_test(c.p, s)
    #@+node:ekr.20210904065459.37: *3* TestJavascript.test_5
    def test_5(self):
        c = self.c
        s = textwrap.dedent("""\
            var express = require('express');

            var app = express.createServer(express.logger());

            app.get('/', function(request, response) {
            response.send('Hello World!');
            });

            var port = process.env.PORT || 5000;
            app.listen(port, function() {
            console.log("Listening on " + port);
            });
        """)
        self.run_test(c.p, s)
    #@+node:ekr.20210904065459.38: *3* TestJavascript.test_639_many_top_level_nodes
    def test_639_many_top_level_nodes(self):
        c = self.c
        s = textwrap.dedent("""\
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
        """)
        self.run_test(c.p, s)
    #@+node:ekr.20210904065459.39: *3* TestJavascript.test_639_acid_test_1
    def test_639_acid_test_1(self):
        c = self.c
        s = textwrap.dedent("""\
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
        """)
        self.run_test(c.p, s)
    #@+node:ekr.20210904065459.40: *3* TestJavascript.test_639_acid_test_2
    def test_639_acid_test_2(self):
        c = self.c
        s = textwrap.dedent("""\
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
        """)
        self.run_test(c.p, s)
    #@-others
#@+node:ekr.20211108043230.1: ** class TestMarkdown (BaseTestImporter)
class TestMarkdown(BaseTestImporter):
    
    ext = '.md'
    
    #@+others
    #@+node:ekr.20210904065459.109: *3* TestMarkdown.test_md_import_test
    def test_md_import_test(self):
        c = self.c
        s = textwrap.dedent("""\
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
    """)
        table = (
            (1, 'Top'),
            (2, 'Section 1'),
            (2, 'Section 2'),
            (3, 'Section 2.1'),
            (4, 'Section 2.1.1'),
            (3, 'Section 2.2'),
            (2, 'Section 3'),
        )
        self.run_test(c.p, s)
        after = c.p.nodeAfterTree()
        root = c.p.lastChild()
        self.assertEqual(root.h, '@auto-md test')
        p = root.firstChild()
        for n, h in table:
            n2 = p.level() - root.level()
            self.assertEqual(h, p.h)
            self.assertEqual(n, n2)
            p.moveToThreadNext()
        self.assertEqual(p, after)
    #@+node:ekr.20210904065459.110: *3* TestMarkdown.test_md_import_test_rst_style
    def test_md_import_test_rst_style(self):
        c = self.c
        s = textwrap.dedent("""\
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
    """)
        self.run_test(c.p, s)
        table = (
            (1, 'Top'),
            (2, 'Section 1'),
            (2, 'Section 2'),
            (3, 'Section 2.1'),
            (4, 'Section 2.1.1'),
            (3, 'Section 2.2'),
            (2, 'Section 3'),
        )
        p = c.p
        after = p.nodeAfterTree()
        root = p.lastChild()
        self.assertEqual(root.h, '@auto-md test')
        p = root.firstChild()
        for n, h in table:
            n2 = p.level() - root.level()
            self.assertEqual(h, p.h)
            self.assertEqual(n, n2)
            p.moveToThreadNext()
        self.assertEqual(p, after)
    #@+node:ekr.20210904065459.111: *3* TestMarkdown.test_markdown_importer_basic
    def test_markdown_importer_basic(self):
        c = self.c
        # insert test for markdown here.
        s = textwrap.dedent("""\
            Decl line.
            #Header

            After header text

            ##Subheader

            Not an underline

            ----------------

            After subheader text

            #Last header: no text
        """)
        table = (
            '!Declarations',
            'Header',
                'Subheader',
                'Last header: no text',
        )
        self.run_test(c.p, s)
        root = c.p.lastChild()
        self.assertEqual(root.h, '@auto-md test')
        p2 = root.firstChild()
        for h in table:
            self.assertEqual(p2.h, h)
            p2.moveToThreadNext()
        assert not root.isAncestorOf(p2), p2.h  # Extra nodes
    #@+node:ekr.20210904065459.112: *3* TestMarkdown.test_markdown_importer_implicit_section
    def test_markdown_importer_implicit_section(self):
        c = self.c
        # insert test for markdown here.
        s = textwrap.dedent("""\
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
        """)
        table = (
            '!Declarations',
            'Header',
                'Subheader',
                    'This *should* be a section',
                'Last header: no text',
        )
        # Implicit underlining *must* cause the perfect-import test to fail!
        g.app.suppressImportChecks = True
        self.run_test(c.p, s)
        root = c.p.lastChild()
        self.assertEqual(root.h, '@auto-md test')
        p2 = root.firstChild()
        for h in table:
            self.assertEqual(p2.h, h)
            p2.moveToThreadNext()
        assert not root.isAncestorOf(p2), p2.h  # Extra nodes
    #@+node:ekr.20210904065459.114: *3* TestMarkdown.test_markdown_github_syntax
    def test_markdown_github_syntax(self):
        c = self.c
        # insert test for markdown here.
        s = textwrap.dedent("""\
            Decl line.
            #Header

            `​``python
            loads.init = {
                Chloride: 11.5,
                TotalP: 0.002,
            }
            `​``
            #Last header
        """)
        table = (
            '!Declarations',
            'Header',
            'Last header',
        )
        self.run_test(c.p, s)
        root = c.p.lastChild()
        self.assertEqual(root.h, '@auto-md test')
        p2 = root.firstChild()
        for h in table:
            self.assertEqual(p2.h, h)
            p2.moveToThreadNext()
        assert not root.isAncestorOf(p2), p2.h  # Extra nodes
    #@+node:ekr.20210904065459.128: *3* TestMarkdown.test_is_hash
    def test_is_hash(self):
        c = self.c
        ic = c.importCommands
        x = markdown.Markdown_Importer(ic, atAuto=False)
        # insert test for markdown here.
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
class TestOrg (BaseTestImporter):
    
    ext = '.org'
    
    #@+others
    #@+node:ekr.20210904065459.42: *3* TestOrg.test_1
    def test_1(self):
        c = self.c
        s = textwrap.dedent("""\
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
        """)
        table = (
            'Section 1',
            'Section 2', 'Section 2-1', 'Section 2-1-1',
            'Section 3', 'Section 3.1',
        )
        self.run_test(c.p, s)
        root = c.p.firstChild()
        p2 = root.firstChild()
        for h in table:
            self.assertEqual(p2.h, h)
            p2.moveToThreadNext()
        assert not root.isAncestorOf(p2), p2.h  # Extra nodes
    #@+node:ekr.20210904065459.46: *3* TestOrg.test_1074
    def test_1074(self):
        c = self.c
        s = textwrap.dedent("""\
            *  Test
            First line.
        """)
        table = (
            ' Test',
        )
        self.run_test(c.p, s)
        root = c.p.firstChild()
        p2 = root.firstChild()
        for h in table:
            self.assertEqual(p2.h, g.toUnicode(h))
            p2.moveToThreadNext()
        assert not root.isAncestorOf(p2), p2.h  # Extra nodes
    #@+node:ekr.20210904065459.45: *3* TestOrg.test_552
    def test_552(self):
        c = self.c
        s = textwrap.dedent("""\
            * Events
              :PROPERTIES:
              :CATEGORY: events
              :END:
            ** 整理个人生活
            *** 每周惯例
        """)
        table = (
            'Events',
            '整理个人生活',
            '每周惯例',
        )
        self.run_test(c.p, s)
        root = c.p.firstChild()
        p2 = root.firstChild()
        for h in table:
            self.assertEqual(p2.h, g.toUnicode(h))
            p2.moveToThreadNext()
        assert not root.isAncestorOf(p2), p2.h  # Extra nodes
    #@+node:ekr.20210904065459.44: *3* TestOrg.test_intro
    def test_intro(self):
        c = self.c
        s = textwrap.dedent("""\
            Intro line.
            * Section 1
            Sec 1.
            * Section 2
            Sec 2.
        """)
        table = (
            'Section 1',
            'Section 2',
        )
        self.run_test(c.p, s)
        root = c.p.firstChild()
        p2 = root.firstChild()
        for h in table:
            self.assertEqual(p2.h, h)
            p2.moveToThreadNext()
        assert not root.isAncestorOf(p2), p2.h  # Extra nodes
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
        c = self.c
        # insert test for org here.
        s = textwrap.dedent("""\
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
        """)
        table = (
            'Section 1',
            'Section 2', 'Section 2-1', 'Section 2-1-1',
            'Section 3',
            'placeholder', 'placeholder', 'placeholder', 'placeholder',
            'Section 3-1-1-1-1-1',
            'Section 3.1',
        )
        g.app.suppressImportChecks = True
        self.run_test(c.p, s)
        root = c.p.firstChild()
        p2 = root.firstChild()
        for h in table:
            self.assertEqual(p2.h, h)
            p2.moveToThreadNext()
        assert not root.isAncestorOf(p2), p2.h  # Extra nodes
    #@+node:ekr.20210904065459.43: *3* TestOrg.test_tags
    def test_tags(self):
        c = self.c
        s = textwrap.dedent("""\
            * Section 1 :tag1:
            * Section 2 :tag2:
            * Section 3 :tag3:tag4:
        """)
        table = (
            'Section 1 :tag1:',
            'Section 2 :tag2:',
            'Section 3 :tag3:tag4:',
        )
        self.run_test(c.p, s)
        root = c.p.firstChild()
        p2 = root.firstChild()
        for h in table:
            self.assertEqual(p2.h, h)
            p2.moveToThreadNext()
        assert not root.isAncestorOf(p2), p2.h  # Extra nodes
    #@-others
#@+node:ekr.20211108081327.1: ** class TestOtl (BaseTestImporter)
class TestOtl (BaseTestImporter):
    
    ext = '.otl'
    
    #@+others
    #@+node:ekr.20210904065459.49: *3* TestOtl.test_1
    def test_1(self):
        c = self.c
        s = textwrap.dedent("""\
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
        """)
        table = (
            'Section 1',
            'Section 2', 'Section 2-1', 'Section 2-1-1',
            'Section 3', 'Section 3.1',
        )
        self.run_test(c.p, s)
        if 0:
            root = c.p.firstChild()
            p2 = root.firstChild()
            for h in table:
                self.assertEqual(p2.h, h)
                p2.moveToThreadNext()
            assert not root.isAncestorOf(p2), p2.h  # Extra nodes

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
class TestPascal (BaseTestImporter):
    
    ext = '.pas'
    
    #@+others
    #@+node:ekr.20210904065459.50: *3* TestPascal.test_delphi_interface
    def test_delphi_interface(self):
        c = self.c
        s = textwrap.dedent("""\
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
        """)
        table = (
            'interface',
            'procedure FormCreate',
            'procedure TForm1.FormCreate',
        )
        self.run_test(c.p, s)
        root = c.p.lastChild()
        assert root
        self.assertEqual(root.h, '@file test')
        p2 = root.firstChild()
        for i, h in enumerate(table):
            self.assertEqual(p2.h, h)
            p2.moveToThreadNext()
        assert not root.isAncestorOf(p2), p2.h  # Extra nodes

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
class TestPerl (BaseTestImporter):
    
    ext = '.pl'
    
    #@+others
    #@+node:ekr.20210904065459.51: *3* TestPerl.test_1
    def test_1(self):
        c = self.c
        s = textwrap.dedent("""\
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
        """)
        self.run_test(c.p, s)
    #@+node:ekr.20210904065459.53: *3* TestPerl.test_multi_line_string
    def test_multi_line_string(self):
        c = self.c
        s = textwrap.dedent("""\
            #!/usr/bin/perl

            # This would print with a line break in the middle
            print "Hello

            sub World {
                print "This is not a funtion!"
            }

            world\n";
        """)
        self.run_test(c.p, s)
    #@+node:ekr.20210904065459.52: *3* TestPerl.test_perlpod_comment
    def test_perlpod_comment(self):
        c = self.c
        s = textwrap.dedent("""\
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
        """)
        self.run_test(c.p, s)
    #@+node:ekr.20210904065459.54: *3* TestPerl.test_regex_1
    def test_regex_1(self):
        c = self.c
        # ('len',   'tr///', '/',       context,  0,       0,       0),
        # ('len',   's///',  '/',       context,  0,       0,       0),
        # ('len',   'm//',   '/',       context,  0,       0,       0),
        # ('len',   '/',     '/',       '',       0,       0,       0),
        s = textwrap.dedent("""\
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
        """)
        self.run_test(c.p, s)

    #@+node:ekr.20210904065459.55: *3* TestPerl.test_regex_2
    def test_regex_2(self):
        c = self.c
        s = textwrap.dedent("""\
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
        """)
        table = (
            'sub test1',
            'sub test2',
            'sub test3',
            'sub test4'
        )
        self.run_test(c.p, s)
        root = c.p.lastChild()
        self.assertEqual(root.h, '@file test')
        p2 = root.firstChild()
        for h in table:
            self.assertEqual(p2.h, h)
            p2.moveToThreadNext()
        assert not root.isAncestorOf(p2), p2.h  # Extra nodes

    #@-others
#@+node:ekr.20211108082208.1: ** class TestPhp (BaseTestImporter)
class TestPhp (BaseTestImporter):
    
    ext = '.php'
    
    #@+others
    #@+node:ekr.20210904065459.56: *3* TestPhp.test_import_class
    def test_import_class(self):
        c = self.c
        s = textwrap.dedent("""\
            <?php

            $type = 'cc';
            $obj = new $type; // outputs "hi!"

            class cc {
                function __construct() {
                    echo 'hi!';
                }
            }

            ?>
        """)
        self.run_test(c.p, s)
    #@+node:ekr.20210904065459.57: *3* TestPhp.test_import_conditional_class
    def test_import_conditional_class(self):
        c = self.c
        s = textwrap.dedent("""\
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
        """)
        self.run_test(c.p, s)
    #@+node:ekr.20210904065459.58: *3* TestPhp.test_import_classes__functions
    def test_import_classes__functions(self):
        c = self.c
        s = textwrap.dedent("""\
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
        """)
        self.run_test(c.p, s)
    #@+node:ekr.20210904065459.59: *3* TestPhp.test_here_doc
    def test_here_doc(self):
        c = self.c
        s = textwrap.dedent("""\
            <?php
            class foo {
                public $bar = <<<EOT
            a test.
            bar
            EOT;
            }
            ?>
        """)
        self.run_test(c.p, s)
    #@-others
#@+node:ekr.20211108082509.1: ** class TestPython (BaseTestImporter)
class TestPython (BaseTestImporter):
    
    ext = '.py'
    
    #@+others
    #@+node:ekr.20210904065459.62: *3* TestPython.test_bad_class_test
    def test_bad_class_test(self):
        c = self.c
        s = textwrap.dedent("""\
            class testClass1 # no colon
                pass

            def spam():
                pass
        """)
        self.run_test(c.p, s=s)
    #@+node:ekr.20210904065459.63: *3* TestPython.test_basic_nesting_test
    def test_basic_nesting_test(self):
        c = self.c
        # Was unittest/at_auto-unit-test.py
        s = textwrap.dedent("""\
            class class1:
                def class1_method1():
                    pass
                def class1_method2():
                    pass
                # After @others in child1.
            class class2:
                def class2_method1():
                    pass
                def class2_method2():
                    pass
            # last line
        """)
        table = (
            (1, 'class class1'),
            (2, 'class1_method1'),
            (2, 'class1_method2'),
            (1, 'class class2'),
            (2, 'class2_method1'),
            (2, 'class2_method2'),
        )
        p = c.p
        self.run_test(p, s=s)
        after = p.nodeAfterTree()
        root = p.lastChild()
        self.assertEqual(root.h, '@file test')
        p = root.firstChild()
        for n, h in table:
            n2 = p.level() - root.level()
            self.assertEqual(h, p.h)
            self.assertEqual(n, n2)
            p.moveToThreadNext()
        self.assertEqual(p, after)

    #@+node:ekr.20210904065459.64: *3* TestPython.test_bug_346
    def test_bug_346(self):
        c = self.c
        s = textwrap.dedent('''\
            import sys

            if sys.version_info[0] >= 3:
                exec_ = eval('exec')
            else:
                def exec_(_code_, _globs_=None, _locs_=None):
                    """Execute code in a namespace."""
                    if _globs_ is None:
                        frame = sys._getframe(1)
                        _globs_ = frame.f_globals
                        if _locs_ is None:
                            _locs_ = frame.f_locals
                        del frame
                    elif _locs_ is None:
                        _locs_ = _globs_
                    exec("""exec _code_ in _globs_, _locs_""")

            def make_parser():

                parser = argparse.ArgumentParser(
                    description="""Raster calcs. with GDAL.
                    The first --grid defines the projection, extent, cell size, and origin
                    for all calculations, all other grids are transformed and resampled
                    as needed to match.""",
                    formatter_class=argparse.ArgumentDefaultsHelpFormatter
            )
        ''')
        table = (
            (1, 'Declarations'),
            (1, 'make_parser'),
        )
        p = c.p
        self.run_test(p, s=s)
        after = p.nodeAfterTree()
        root = p.lastChild()
        self.assertEqual(root.h, '@file test')
        p = root.firstChild()
        for n, h in table:
            n2 = p.level() - root.level()
            self.assertEqual(h, p.h)
            self.assertEqual(n, n2)
            p.moveToThreadNext()
        self.assertEqual(p, after)
    #@+node:ekr.20210904065459.65: *3* TestPython.test_bug_354
    def test_bug_354(self):
        c = self.c
        s = """
        if isPython3:
            def u(s):
                '''Return s, converted to unicode from Qt widgets.'''
                return s

            def ue(s, encoding):
                return s if g.isUnicode(s) else str(s, encoding)
        else:
            def u(s):
                '''Return s, converted to unicode from Qt widgets.'''
                return builtins.unicode(s) # Suppress pyflakes complaint.

            def ue(s, encoding):
                return builtins.unicode(s, encoding)
        """
        table = (
            (1, 'Declarations'),
            # (1, 'u'),
            # (1, 'ue'),
        )
        p = c.p
        self.run_test(p, s=s)
        after = p.nodeAfterTree()
        root = p.lastChild()
        self.assertEqual(root.h, '@file test')
        p = root.firstChild()
        for n, h in table:
            n2 = p.level() - root.level()
            self.assertEqual(h, p.h)
            self.assertEqual(n, n2)
            p.moveToThreadNext()
        self.assertEqual(p, after)
    #@+node:ekr.20210904065459.66: *3* TestPython.test_bug_357
    def test_bug_357(self):
        c = self.c
        s = textwrap.dedent('''
            """
            sheet_stats.py - report column stats for spreadsheets

            requires openpyxl and numpy

            Terry N. Brown, terrynbrown@gmail.com, Fri Dec 16 13:20:47 2016
            2016-12-26 Henry Helgen added average, variance, standard deviation,
                                    coefficient of variation to output
            2016-12-23 Henry Helgen updated to Python 3.5 syntax including print() and
                                    writer = csv.writer(open(opt.output, 'w', newline=''))
            """

            import csv
            import argparse
            import glob
            import multiprocessing
            import os
            import sys
            from collections import namedtuple
            from math import sqrt, isnan
            NAN = float('NAN')

            from openpyxl import load_workbook

            PYTHON_2 = sys.version_info[0] < 3
            if not PYTHON_2:
                unicode = str

            class AttrDict(dict):
                """allow d.attr instead of d['attr']
                http://stackoverflow.com/a/14620633
                """
                def __init__(self, *args, **kwargs):
                    super(AttrDict, self).__init__(*args, **kwargs)
                    self.__dict__ = self

            FIELDS = [  # fields in outout table
                'file', 'field', 'n', 'blank', 'bad', 'min', 'max', 'mean', 'std',
                'sum', 'sumsq', 'variance', 'coefvar'
            ]
            def make_parser():
                """build an argparse.ArgumentParser, don't call this directly,
                   call get_options() instead.
                """
                parser = argparse.ArgumentParser(
                    description="""Report column stats for spreadsheets""",
                    formatter_class=argparse.ArgumentDefaultsHelpFormatter
                )

                parser.add_argument('files', type=str, nargs='+',
                    help="Files to process, '*' patterns expanded."
                )

                required_named = parser.add_argument_group('required named arguments')

                required_named.add_argument("--output",
                    help="Path to .csv file for output, will be overwritten",
                    metavar='FILE'
                )

                return parser

            def get_options(args=None):
                """
                get_options - use argparse to parse args, and return a
                argparse.Namespace, possibly with some changes / expansions /
                validatations.

                Client code should call this method with args as per sys.argv[1:],
                rather than calling make_parser() directly.

                :param [str] args: arguments to parse
                :return: options with modifications / validations
                :rtype: argparse.Namespace
                """
                opt = make_parser().parse_args(args)

                # modifications / validations go here

                if not opt.output:
                    print("No --output supplied")
                    exit(10)

                return opt

            def get_aggregate(psumsqn, psumn, pcountn):
                """
                get_aggregate - compute mean, variance, standard deviation,
                coefficient of variation This function is used instead of
                numpy.mean, numpy.var, numpy.std since the sum, sumsq, and count are
                available when the function is called. It avoids an extra pass
                through the list.

                # note pcountn means the full list n,  not a sample n - 1

                :param sum of squares, sum, count
                :return: a tuple of floats mean, variance, standard deviation, coefficient of variation
                """

                Agg = namedtuple("Agg", "mean variance std coefvar")

                # validate inputs check for count == 0
                if pcountn == 0:
                    result = Agg(NAN, NAN, NAN, NAN)
                else:

                    mean = psumn / pcountn # mean

                    # compute variance from sum squared without knowing mean while summing
                    variance = (psumsqn - (psumn * psumn) / pcountn ) / pcountn

                    #compute standard deviation
                    if variance < 0:
                        std = NAN
                    else:
                        std = sqrt(variance)

                    # compute coefficient of variation
                    if mean == 0:
                        coefvar = NAN
                    else:
                        coefvar = std / mean

                    result = Agg(mean, variance, std, coefvar)

                return result


            def proc_file(filepath):
                """
                proc_file - process one .xlsx file

                :param str filepath: path to file
                :return: list of lists, rows of info. as expected in main()
                """

                print(filepath)

                # get the first sheet
                book = load_workbook(filename=filepath, read_only=True)
                sheets = book.get_sheet_names()
                sheet = book[sheets[0]]
                row_source = sheet.rows
                row0 = next(row_source)
                # get field names from the first row
                fields = [i.value for i in row0]

                data = {
                    'filepath': filepath,
                    'fields': {field:AttrDict({f:0 for f in FIELDS}) for field in fields}
                }

                for field in fields:
                    # init. mins/maxs with invalid value for later calc.
                    data['fields'][field].update(dict(
                        min=NAN,
                        max=NAN,
                        field=field,
                        file=filepath,
                    ))

                rows = 0
                for row in row_source:

                    if rows % 1000 == 0:  # feedback every 1000 rows
                        print(rows)
                        # Much cleaner to exit by creating a file called "STOP" in the
                        # local directory than to try and use Ctrl-C, when using
                        # multiprocessing.  Save time by checking only every 1000 rows.
                        if os.path.exists("STOP"):
                            return

                    rows += 1

                    for cell_n, cell in enumerate(row):
                        d = data['fields'][fields[cell_n]]
                        if cell.value is None or unicode(cell.value).strip() == '':
                            d.blank += 1
                        else:
                            try:
                                x = float(cell.value)
                                d.sum += x
                                d.sumsq += x*x
                                d.n += 1
                                # min is x if no value seen yet, else min(prev-min, x)
                                if isnan(d.min):
                                    d.min = x
                                else:
                                    d.min = min(d.min, x)
                                # as for min
                                if isnan(d.max):
                                    d.max = x
                                else:
                                    d.max = max(d.max, x)
                            except ValueError:
                                d.bad += 1

                assert sum(d.n+d.blank+d.bad for d in data['fields'].values()) == rows * len(fields)

                # compute the derived values
                for field in data['fields']:
                    d = data['fields'][field]
                    d.update(get_aggregate(d.sumsq, d.sum, d.n)._asdict().items())

                return data
            def get_answers(opt=None, **kwargs):
                """get_answers - process files

                :param argparse.Namespace opt: options
                :return: list of answers from proc_file
                """

                if opt is None:  # API call rather than command line
                    opt = type("opt", (), kwargs)

                # pass filenames through glob() to expand "2017_*.xlsx" etc.
                files = []
                for filepath in opt.files:
                    files.extend(glob.glob(filepath))

                # create a pool of processors
                pool = multiprocessing.Pool(multiprocessing.cpu_count()-1)

                # process file list with processor pool
                return pool.map(proc_file, files)
            def get_table_rows(answers):
                """get_table_rows - generator - convert get_answers() output to table format

                :param list answers: output from get_answers()
                :return: list of rows suitable for csv.writer
                """
                yield FIELDS
                for answer in answers:
                    for field in answer['fields']:
                        row = [answer['fields'][field][k] for k in FIELDS]
                        if PYTHON_2:
                            yield [unicode(col).encode('utf-8') for col in row]
                        else:
                            yield row

            def main():
                """main() - when invoked directly"""
                opt = get_options()

                # csv.writer does its own EOL handling,
                # see https://docs.python.org/3/library/csv.html#csv.reader
                if PYTHON_2:
                    output = open(opt.output, 'wb')
                else:
                    output = open(opt.output, 'w', newline='')

                with output as out:
                    writer = csv.writer(out)
                    for row in get_table_rows(get_answers(opt)):
                        writer.writerow(row)

            if __name__ == '__main__':
                main()
        ''')
        table = (
            (1, "Declarations"),
            (1, "class AttrDict(dict)"),
            (2, "__init__"),
            (1, "make_parser"),
            (1, "get_options"),
            (1, "get_aggregate"),
            (1, "proc_file"),
            (1, "get_answers"),
            (1, "get_table_rows"),
            (1, "main"),
        )
        p = c.p
        self.run_test(p, s=s)
        after = p.nodeAfterTree()
        root = p.lastChild()
        assert root
        self.assertEqual(root.h, '@file test')
        p = root.firstChild()
        for n, h in table:
            assert p, h
            n2 = p.level() - root.level()
            self.assertEqual(h, p.h)
            self.assertEqual(n, n2)
            p.moveToThreadNext()
        self.assertEqual(p, after)
    #@+node:ekr.20210904065459.67: *3* TestPython.test_bug_360
    def test_bug_360(self):
        c = self.c
        s = textwrap.dedent("""\
            @base_task(
                targets=['img/who_map.png', 'img/who_map.pdf'],
                file_dep=[data_path('phyto')],
                task_dep=['load_data'],
            )
            def make_map():
                '''make_map - plot the Thompson / Bartsh / WHO map'''
        """)
        table = (
            (1, '@base_task make_map'),
        )
        p = c.p
        self.run_test(p, s=s)
        after = p.nodeAfterTree()
        root = p.lastChild()
        self.assertEqual(root.h, '@file test')
        p = root.firstChild()
        for n, h in table:
            n2 = p.level() - root.level()
            self.assertEqual(h, p.h)
            self.assertEqual(n, n2)
            p.moveToThreadNext()
        self.assertEqual(p, after)
    #@+node:ekr.20210904065459.68: *3* TestPython.test_bug_390
    def test_bug_390(self):
        c = self.c
        s = textwrap.dedent("""\
            import sys

            class Foo():
                pass

            a = 2

            def main(self):
                pass

            if __name__ == '__main__':
                main()
        """)
        table = (
            (1, 'Declarations'),
            (1, 'class Foo'),
            (1, 'main'),
        )
        p = c.p
        self.run_test(p, s=s)
        after = p.nodeAfterTree()
        root = p.lastChild()
        self.assertEqual(root.h, '@file test')
        p = root.firstChild()
        for n, h in table:
            n2 = p.level() - root.level()
            self.assertEqual(h, p.h)
            self.assertEqual(n, n2)
            p.moveToThreadNext()
        self.assertEqual(p, after)
        assert "if __name__ == '__main__':" in root.b
    #@+node:ekr.20210904065459.70: *3* TestPython.test_bug_603720
    def test_bug_603720(self):
        c = self.c
        # Leo bug 603720
        # Within the docstring we must change '\' to '\\'
        s = textwrap.dedent('''\
            def foo():
                s = \\
            """#!/bin/bash
            cd /tmp
            ls"""
                file('/tmp/script', 'w').write(s)

            class bar:
                pass

            foo()
        ''')
        self.run_test(c.p, s=s)
    #@+node:ekr.20210904065459.69: *3* TestPython.test_bug_978
    def test_bug_978(self):
        c = self.c
        s = textwrap.dedent("""\
            import foo
            import bar

            class A(object):
                pass
            class B(foo):
                pass
            class C(bar.Bar):
                pass
        """)
        table = (
            (1, 'Declarations'),
            (1, 'class A(object)'),
            (1, 'class B(foo)'),
            (1, 'class C(bar.Bar)'),
        )
        p = c.p
        self.run_test(p, s=s)
        after = p.nodeAfterTree()
        root = p.lastChild()
        assert root
        self.assertEqual(root.h, '@file test')
        p = root.firstChild()
        for n, h in table:
            n2 = p.level() - root.level()
            self.assertEqual(h, p.h)
            self.assertEqual(n, n2)
            p.moveToThreadNext()
        self.assertEqual(p, after)
    #@+node:ekr.20210904065459.72: *3* TestPython.test_class_test_2
    def test_class_test_2(self):
        c = self.c
        s = textwrap.dedent("""\
            class testClass2:
                pass
        """)
        self.run_test(c.p, s=s)
    #@+node:ekr.20210904065459.73: *3* TestPython.test_class_tests_1
    def test_class_tests_1(self):
        c = self.c
        s = textwrap.dedent('''\
        class testClass1:
            """A docstring"""
            def __init__ (self):
                pass
            def f1(self):
                pass
        ''')
        self.run_test(c.p, s=s)
    #@+node:ekr.20210904065459.74: *3* TestPython.test_comment_after_dict_assign
    def test_comment_after_dict_assign(self):
        c = self.c
        s = textwrap.dedent("""\
            NS = { 'i': 'http://www.inkscape.org/namespaces/inkscape',
                  's': 'http://www.w3.org/2000/svg',
                  'xlink' : 'http://www.w3.org/1999/xlink'}

            tabLevels = 4  # number of defined tablevels, FIXME, could derive from template?
        """)
        table = (
            (1, 'Declarations'),
        )
        p = c.p
        self.run_test(p, s=s)
        after = p.nodeAfterTree()
        root = p.lastChild()
        self.assertEqual(root.h, '@file test')
        p = root.firstChild()
        for n, h in table:
            n2 = p.level() - root.level()
            self.assertEqual(h, p.h)
            self.assertEqual(n, n2)
            p.moveToThreadNext()
        self.assertEqual(p, after)
    #@+node:ekr.20210904065459.75: *3* TestPython.test_decls_test_1
    def test_decls_test_1(self):
        c = self.c
        s = textwrap.dedent("""\
            import leo.core.leoGlobals as g

            a = 3
        """)
        table = (
            (1, 'Declarations'),
        )
        p = c.p
        self.run_test(p, s=s)
        after = p.nodeAfterTree()
        root = p.lastChild()
        self.assertEqual(root.h, '@file test')
        p = root.firstChild()
        for n, h in table:
            n2 = p.level() - root.level()
            self.assertEqual(h, p.h)
            self.assertEqual(n, n2)
            p.moveToThreadNext()
        self.assertEqual(p, after)
    #@+node:ekr.20210904065459.76: *3* TestPython.test_decorator
    def test_decorator(self):
        c = self.c
        s = textwrap.dedent('''\
            class Index:
                """docstring"""
                @cherrypy.nocolor
                @cherrypy.expose
                def index(self):
                    return "Hello world!"

                @cmd('abc')
                def abc(self):
                    return "abc"
        ''')
        self.run_test(c.p, s=s)  # Must be true.
        index = g.findNodeInTree(c, c.p, '@cherrypy.nocolor index')
        assert index
        lines = g.splitLines(index.b)
        self.assertEqual(lines[0], '@cherrypy.nocolor\n')
        self.assertEqual(lines[1], '@cherrypy.expose\n')
        abc = g.findNodeInTree(c, c.p, "@cmd('abc') abc")
        lines = g.splitLines(abc.b)
        self.assertEqual(lines[0], "@cmd('abc')\n")
    #@+node:ekr.20210904065459.77: *3* TestPython.test_decorator_2
    def test_decorator_2(self):
        c = self.c
        s = textwrap.dedent('''\
            """
            A PyQt "task launcher" for quick access to python scripts.

            Buttons to click to make working in Windows less unproductive.

            e.g. a button to move the current window to top or bottom half
            of screen, because Windows-Up / Windows-Down doesn't do that.
            Or quote the text on the clipboard properly, because Outlook
            can't do that.

            terrynbrown@gmail.com, 2016-12-23
            """

            import sys
            import time
            from PyQt4 import QtGui, QtCore, Qt
            from PyQt4.QtCore import Qt as QtConst

            COMMANDS = []

            class Draggable(QtGui.QWidget):
                def __init__(self, *args, **kwargs):
                    """__init__
                    """

                    QtGui.QWidget.__init__(self, *args, **kwargs)
                    # self.setMouseTracking(True)
                    self.offset = None
                    layout = QtGui.QHBoxLayout()
                    self.setLayout(layout)
                    layout.addItem(QtGui.QSpacerItem(15, 5))
                    layout.setSpacing(0)
                    layout.setContentsMargins(0, 0, 0, 0)

                def mousePressEvent(self, event):
                    self.offset = event.pos()

                def mouseMoveEvent(self, event):
                    x=event.globalX()
                    y=event.globalY()
                    x_w = self.offset.x()
                    y_w = self.offset.y()
                    self.parent().move(x-x_w, y-y_w)

            def command(name):
                def makebutton(function):
                    COMMANDS.append((name, function))
                    return function
                return makebutton

            @command("Exit")
            def exit_():
                exit()

            def main():

                app = Qt.QApplication(sys.argv)

                main = QtGui.QMainWindow(None,
                   # QtConst.CustomizeWindowHint  |
                   QtConst.FramelessWindowHint #  |
                   # QtConst.WindowCloseButtonHint
                )

                main.resize(800,16)
                main.move(40,40)
                mainwidj = Draggable()

                for name, function in COMMANDS:
                    button = QtGui.QPushButton(name)
                    button.clicked.connect(function)
                    mainwidj.layout().addWidget(button)

                main.setCentralWidget(mainwidj)
                main.show()
                app.exec_()

            if __name__ == '__main__':
                main()
        ''')
        table = (
            (1, "Declarations"),
            (1, "class Draggable(QtGui.QWidget)"),
            (2, "__init__"),
            (2, "mousePressEvent"),
            (2, "mouseMoveEvent"),
            (1, "command"),
            (1, '@command("Exit") exit_'),
            (1, "main"),
        )
        self.run_test(c.p, s=s)
        after = c.p.nodeAfterTree()
        root = c.p.lastChild()
        self.assertEqual(root.h, '@file test')
        p = root.firstChild()
        for n, h in table:
            n2 = p.level() - root.level()
            self.assertEqual(h, p.h)
            self.assertEqual(n, n2)
            p.moveToThreadNext()
        self.assertEqual(p, after)
        target = g.findNodeInTree(c, root, '@command("Exit") exit_')
        assert target
        lines = g.splitLines(target.b)
        self.assertEqual(lines[0], '@command("Exit")\n')

    #@+node:ekr.20210904065459.78: *3* TestPython.test_def_inside_def
    def test_def_inside_def(self):
        c = self.c
        s = textwrap.dedent('''\
        class aClass:
            def outerDef(self):
                """docstring.
                line two."""

                def pr(*args,**keys):
                    g.es_print(color='blue',*args,**keys)

                a = 3
        ''')
        table = (
            (1, 'class aClass'),
            (2, 'outerDef'),
            # (3, 'pr'),
        )
        p = c.p
        self.run_test(p, s=s)
        after = p.nodeAfterTree()
        root = p.lastChild()
        self.assertEqual(root.h, '@file test')
        p = root.firstChild()
        for n, h in table:
            n2 = p.level() - root.level()
            self.assertEqual(h, p.h)
            self.assertEqual(n, n2)
            p.moveToThreadNext()
        self.assertEqual(p, after)

    #@+node:ekr.20210904065459.79: *3* TestPython.test_def_test_1
    def test_def_test_1(self):
        c = self.c
        s = textwrap.dedent("""\
            class test:

                def importFilesCommand (self,files=None,treeType=None,
                    perfectImport=True,testing=False,verbose=False):
                        # Not a command.  It must *not* have an event arg.

                    c = self.c
                    if c == None: return
                    p = c.currentPosition()

                # Used by paste logic.

                def convertMoreStringToOutlineAfter (self,s,firstVnode):
                    s = string.replace(s,"\\r","")
                    strings = string.split(s,"\\n")
                    return self.convertMoreStringsToOutlineAfter(strings,firstVnode)
        """)
        table = (
            (1, 'class test'),
            (2, 'importFilesCommand'),
            (2, 'convertMoreStringToOutlineAfter'),
        )
        p = c.p
        self.run_test(p, s=s)
        after = p.nodeAfterTree()
        root = p.lastChild()
        self.assertEqual(root.h, '@file test')
        p = root.firstChild()
        for n, h in table:
            n2 = p.level() - root.level()
            self.assertEqual(h, p.h)
            self.assertEqual(n, n2)
            p.moveToThreadNext()
        self.assertEqual(p, after)

    #@+node:ekr.20210904065459.80: *3* TestPython.test_def_test_2
    def test_def_test_2(self):
        c = self.c
        s = textwrap.dedent("""\
            class test:
                def spam(b):
                    pass

                # Used by paste logic.

                def foo(a):
                    pass
        """)
        table = (
            (1, 'class test'),
            (2, 'spam'),
            (2, 'foo'),
        )
        p = c.p
        self.run_test(p, s=s)
        after = p.nodeAfterTree()
        root = p.lastChild()
        self.assertEqual(root.h, '@file test')
        p = root.firstChild()
        for n, h in table:
            n2 = p.level() - root.level()
            self.assertEqual(h, p.h)
            self.assertEqual(n, n2)
            p.moveToThreadNext()
        self.assertEqual(p, after)

    #@+node:ekr.20210904065459.81: *3* TestPython.test_docstring_only
    def test_docstring_only(self):
        c = self.c
        s = textwrap.dedent('''\
            """A file consisting only of a docstring.
            """
        ''')
        self.run_test(c.p, s=s)
    #@+node:ekr.20210904065459.82: *3* TestPython.test_empty_decls
    def test_empty_decls(self):
        c = self.c
        s = textwrap.dedent("""\
            import leo.core.leoGlobals as g

            a = 3
        """)
        self.run_test(c.p, s=s)
    #@+node:ekr.20210904065459.71: *3* TestPython.test_enhancement_481
    def test_enhancement_481(self):
        c = self.c
        s = textwrap.dedent("""\
            @g.cmd('my-command')
            def myCommand(event=None):
                pass
        """)
        table = (
            # (1, '@g.cmd myCommand'),
            (1, "@g.cmd('my-command') myCommand"),
        )
        p = c.p
        self.run_test(p, s=s)
        after = p.nodeAfterTree()
        root = p.lastChild()
        self.assertEqual(root.h, '@file test')
        p = root.firstChild()
        for n, h in table:
            n2 = p.level() - root.level()
            self.assertEqual(h, p.h)
            self.assertEqual(n, n2)
            p.moveToThreadNext()
        self.assertEqual(p, after)
    #@+node:ekr.20210904065459.83: *3* TestPython.test_extra_leading_ws_test
    def test_extra_leading_ws_test(self):
        c = self.c
        s = textwrap.dedent("""\
            class cls:
                 def fun(): # one extra space.
                    pass
        """)
        self.run_test(c.p, s=s)
    #@+node:ekr.20211108084817.1: *3* TestPython.test_get_leading_indent
    def test_get_leading_indent(self):
        c = self.c
        importer = linescanner.Importer(c.importCommands, language='python')
        self.assertEqual(importer.single_comment, '#')
           
    #@+node:ekr.20210904065459.124: *3* TestPython.test_get_str_lws
    def test_get_str_lws(self):
        c = self.c
        table = [
            ('', 'abc\n'),
            ('    ', '    xyz\n'),
            ('    ', '    \n'),
            ('  ', '  # comment\n'),
            ('', '\n'),
        ]
        importer = linescanner.Importer(c.importCommands, language='python')
        for val, s in table:
            self.assertEqual(val, importer.get_str_lws(s), msg=repr(s))
    #@+node:ekr.20210904065459.60: *3* TestPython.test_i_scan_state
    def test_i_scan_state(self):
        c = self.c
        # A list of dictionaries.
        tests = (
            g.Bunch(line='\n'),
            g.Bunch(line='\\\n'),
            g.Bunch(line='s = "\\""', ctx=('', '')),  # empty string.
            g.Bunch(line="s = '\\''", ctx=('', '')),  # empty string.
            g.Bunch(line='# comment'),
            g.Bunch(line='  # comment'),
            g.Bunch(line='    # comment'),
            g.Bunch(line='a = "string"'),
            g.Bunch(line='a = "Continued string', ctx=('', '"')),
            g.Bunch(line='end of continued string"', ctx=('"', '')),
            g.Bunch(line='a = """Continued docstring', ctx=('', '"""')),
            g.Bunch(line='a = """#', ctx=('', '"""')),
            g.Bunch(line='end of continued string"""', ctx=('"""', '')),
            g.Bunch(line="a = '''Continued docstring", ctx=('', "'''")),
            g.Bunch(line="end of continued string'''", ctx=("'''", '')),
            g.Bunch(line='a = {[(')
        )
        importer = python.Py_Importer(c.importCommands)
        importer.test_scan_state(tests, State=python.Python_ScanState)
    #@+node:ekr.20210904065459.84: *3* TestPython.test_indent_decls
    def test_indent_decls(self):
        c = self.c
        s = textwrap.dedent('''\
            class mammalProviderBase(object):
                """Root class for content providers used by DWEtree.py"""
                def __init__(self, params):
                    """store reference to parameters"""
                    self.params = params
                def provide(self, what):
                    """default <BASE> value"""
                    if what == 'doctitle':
                        return ELE('base', href=self.params['/BASE/'])
                    return None

                def imagePath(self, sppdat):
                    """return path to images and list of images for *species*"""
                    path = 'MNMammals/imglib/Mammalia'
                    for i in 'Order', 'Family', 'Genus', 'Species':
                        path = os.path.join(path, sppdat['%sName' % (i,)])
                    imglib = os.path.join('/var/www',path)
                    imglib = os.path.join(imglib, '*.[Jj][Pp][Gg]')
                    path = os.path.join('/',path)
                    lst = [os.path.split(i)[1] for i in glob.glob(imglib)]
                    lst.sort()
                    return path, lst

            class mainPages(mammalProviderBase):
                """provide content for pages in 'main' folder"""
                __parent = mammalProviderBase
                def provide(self, what):
                    """add one layer to <BASE>"""
                    ans = self.__parent.provide(self, what)
                    if what == 'doctitle':
                        return ELE('base', href=self.params['/BASE/']+'main/')
                    return ans
        ''')
        table = (
            (1, 'class mammalProviderBase(object)'),
            (2, '__init__'),
            (2, 'provide'),
            (2, 'imagePath'),
            (1, 'class mainPages(mammalProviderBase)'),
            (2, 'provide'),
        )
        p = c.p
        self.run_test(p, s=s)
        after = p.nodeAfterTree()
        root = p.lastChild()
        self.assertEqual(root.h, '@file test')
        p = root.firstChild()
        for n, h in table:
            n2 = p.level() - root.level()
            self.assertEqual(h, p.h)
            self.assertEqual(n, n2)
            p.moveToThreadNext()
        self.assertEqual(p, after)
    #@+node:ekr.20210904065459.125: *3* TestPython.test_is_ws_line
    def test_is_ws_line(self):
        c = self.c
        table = [
            (False, 'abc'),
            (False, '    xyz'),
            (True, '    '),
            (True, '  # comment'),
        ]
        importer = linescanner.Importer(c.importCommands, language='python')
        for val, s in table:
            self.assertEqual(val, importer.is_ws_line(s), msg=repr(s))
    #@+node:ekr.20210904065459.61: *3* TestPython.test_leoApp_fail
    def test_leoApp_fail(self):
        c = self.c
        s = textwrap.dedent('''
            def isValidPython(self):
                if sys.platform == 'cli':
                    return True
                minimum_python_version = '2.6'
                message = """\
            Leo requires Python %s or higher.
            You may download Python from
            http://python.org/download/
            """ % minimum_python_version
                try:
                    version = '.'.join([str(sys.version_info[i]) for i in (0, 1, 2)])
                    ok = g.CheckVersion(version, minimum_python_version)
                    if not ok:
                        print(message)
                        try:
                            # g.app.gui does not exist yet.
                            import Tkinter as Tk
                            class EmergencyDialog(object):
                                def run(self):
                                    """Run the modal emergency dialog."""
                                    self.top.geometry("%dx%d%+d%+d" % (300, 200, 50, 50))
                                    self.top.lift()
                                    self.top.grab_set() # Make the dialog a modal dialog.
                                    self.root.wait_window(self.top)
                            d = EmergencyDialog(
                                title='Python Version Error',
                                message=message)
                            d.run()
                        except Exception:
                            pass
                    return ok
                except Exception:
                    print("isValidPython: unexpected exception: g.CheckVersion")
                    traceback.print_exc()
                    return 0
            def loadLocalFile(self, fn, gui, old_c):
                trace = (False or g.trace_startup) and not g.unitTesting
        ''')
        table = (
            (1, 'isValidPython'),
            # (2, 'class EmergencyDialog'),
            # (3, 'run'),
            (1, 'loadLocalFile'),
        )
        p = c.p
        self.run_test(p, s=s)
        after = p.nodeAfterTree()
        root = p.lastChild()
        self.assertEqual(root.h, '@file test')
        p = root.firstChild()
        for n, h in table:
            n2 = p.level() - root.level()
            self.assertEqual(h, p.h)
            self.assertEqual(n, n2)
            p.moveToThreadNext()
        self.assertEqual(p, after)

    #@+node:ekr.20210904065459.85: *3* TestPython.test_leoImport_py_small_
    def test_leoImport_py_small_(self):
        c = self.c

        s = textwrap.dedent("""\
            # -*- coding: utf-8 -*-
            import leo.core.leoGlobals as g
            class LeoImportCommands(object):
                '''A class implementing all of Leo's import/export code.'''
                def createOutline(self, fileName, parent, s=None, ext=None):
                    '''Create an outline by importing a file or string.'''

                def dispatch(self, ext, p):
                    '''Return the correct scanner function for p, an @auto node.'''
                    # Match the @auto type first, then the file extension.
                    return self.scanner_for_at_auto(p) or self.scanner_for_ext(ext)
                def scanner_for_at_auto(self, p):
                    '''A factory returning a scanner function for p, an @auto node.'''
                    d = self.atAutoDict
                    for key in d.keys():
                        aClass = d.get(key)
                        if aClass and g.match_word(p.h, 0, key):
                            if trace: g.trace('found', aClass.__name__)

                            def scanner_for_at_auto_cb(parent, s, prepass=False):
                                try:
                                    scanner = aClass(importCommands=self)
                                    return scanner.run(s, parent, prepass=prepass)
                                except Exception:
                                    g.es_print('Exception running', aClass.__name__)
                                    g.es_exception()
                                    return None

                            if trace: g.trace('found', p.h)
                            return scanner_for_at_auto_cb
                    if trace: g.trace('not found', p.h, sorted(d.keys()))
                    return None
                def scanner_for_ext(self, ext):
                    '''A factory returning a scanner function for the given file extension.'''
                    aClass = self.classDispatchDict.get(ext)
                    if aClass:

                        def scanner_for_ext_cb(parent, s, prepass=False):
                            try:
                                scanner = aClass(importCommands=self)
                                return scanner.run(s, parent, prepass=prepass)
                            except Exception:
                                g.es_print('Exception running', aClass.__name__)
                                g.es_exception()
                                return None

                        return scanner_for_ext_cb
                    else:
                        return None
                def get_import_filename(self, fileName, parent):
                    '''Return the absolute path of the file and set .default_directory.'''

                def init_import(self, ext, fileName, s):
                    '''Init ivars & vars for imports.'''
        """)
        table = (
            (1, 'Declarations'),
            (1, "class LeoImportCommands(object)"),
            (2, "createOutline"),
            (2, "dispatch"),
            (2, "scanner_for_at_auto"),
            (2, "scanner_for_ext"),
            (2, "get_import_filename"),
            (2, "init_import"),
        )
        p = c.p
        self.run_test(p, s=s)
        after = p.nodeAfterTree()
        root = p.lastChild()
        self.assertEqual(root.h, '@file test')
        p = root.firstChild()
        for n, h in table:
            n2 = p.level() - root.level()
            self.assertEqual(h, p.h)
            self.assertEqual(n, n2)
            p.moveToThreadNext()
        self.assertEqual(p, after)
    #@+node:ekr.20210904065459.86: *3* TestPython.test_looks_like_section_ref
    def test_looks_like_section_ref(self):
        c = self.c
        # ~/at-auto-test.py

        # Careful: don't put a section reference in the string.
        s = textwrap.dedent("""\
            # This is valid Python, but it looks like a section reference.
            a = b < < c > > d
        """).replace('> >', '>>').replace('< <', '<<')
        self.run_test(c.p, s=s)
    #@+node:ekr.20210904065459.87: *3* TestPython.test_minimal_class_1
    def test_minimal_class_1(self):
        c = self.c
        s = textwrap.dedent('''\
            class ItasException(Exception):

                pass

            def gpRun(gp, cmd, args, log = None):

                """Wrapper for making calls to the geoprocessor and reporting errors"""

                if log:

                    log('gp: %s: %s\\n' % (cmd, str(args)))
        ''')
        self.run_test(c.p, s=s)
    #@+node:ekr.20210904065459.88: *3* TestPython.test_minimal_class_2
    def test_minimal_class_2(self):
        c = self.c
        s = textwrap.dedent("""\
            class emptyClass: pass

            def followingDef():
                pass
        """)
        self.run_test(c.p, s=s)
    #@+node:ekr.20210904065459.89: *3* TestPython.test_minimal_class_3
    def test_minimal_class_3(self):
        c = self.c
        s = textwrap.dedent("""\
            class emptyClass: pass # comment

            def followingDef(): # comment
                pass
        """)
        self.run_test(c.p, s=s)
    #@+node:ekr.20210904065459.90: *3* TestPython.test_overindent_def_no_following_def
    def test_overindent_def_no_following_def(self):
        c = self.c
        s = textwrap.dedent("""\
            class aClass:
                def def1(self):
                    pass

                if False or g.unitTesting:

                    def pr(*args,**keys): # reportMismatch test
                        g.es_print(color='blue',*args,**keys)

                    pr('input...')
        """)
        self.run_test(c.p, s=s)
    #@+node:ekr.20210904065459.91: *3* TestPython.test_overindent_def_one_following_def
    def test_overindent_def_one_following_def(self):
        c = self.c
        s = textwrap.dedent("""\
            class aClass:
                def def1(self):
                    pass

                if False or g.unitTesting:

                    def pr(*args,**keys): # reportMismatch test
                        g.es_print(color='blue',*args,**keys)

                    pr('input...')

                def def2(self):
                    pass
        """)
        self.run_test(c.p, s=s)
    #@+node:ekr.20210904065459.92: *3* TestPython.test_overindented_def_3
    def test_overindented_def_3(self):
        # This caused PyParse.py not to be imported properly.
        c = self.c
        s = textwrap.dedent(r'''
            import re
            if 0: # Causes the 'overindent'
               if 0:   # for throwaway debugging output
                  def dump(*stuff):
                    sys.__stdout__.write(" ".join(map(str, stuff)) + "\n")
            for ch in "({[":
               _tran[ord(ch)] = '('
            class testClass1:
                pass
        ''')
        table = (
            (1, 'Declarations'),
            (1, 'class testClass1'),
        )
        p = c.p
        self.run_test(c.p, s=s)
        after = p.nodeAfterTree()
        root = p.lastChild()
        self.assertEqual(root.h, '@file test')
        p = root.firstChild()
        for n, h in table:
            n2 = p.level() - root.level()
            self.assertEqual(h, p.h)
            self.assertEqual(n, n2)
            p.moveToThreadNext()
        self.assertEqual(p, after)
    #@+node:ekr.20210904065459.131: *3* TestPython.test_scan_state
    def test_scan_state(self):
        c = self.c
        State = python.Python_ScanState
        # A list of dictionaries.
        if 0:
            tests = [
                g.Bunch(line='s = "\\""', ctx=('', '')),
            ]
        else:
            tests = [
                g.Bunch(line='\n'),
                g.Bunch(line='\\\n'),
                g.Bunch(line='s = "\\""', ctx=('', '')),
                g.Bunch(line="s = '\\''", ctx=('', '')),
                g.Bunch(line='# comment'),
                g.Bunch(line='  # comment'),
                g.Bunch(line='    # comment'),
                g.Bunch(line='a = "string"'),
                g.Bunch(line='a = "Continued string', ctx=('', '"')),
                g.Bunch(line='end of continued string"', ctx=('"', '')),
                g.Bunch(line='a = """Continued docstring', ctx=('', '"""')),
                g.Bunch(line='a = """#', ctx=('', '"""')),
                g.Bunch(line='end of continued string"""', ctx=('"""', '')),
                g.Bunch(line="a = '''Continued docstring", ctx=('', "'''")),
                g.Bunch(line="end of continued string'''", ctx=("'''", '')),
                g.Bunch(line='a = {[(')
            ]
        importer = python.Py_Importer(c.importCommands, atAuto=True)
        importer.test_scan_state(tests, State)
    #@+node:ekr.20210904065459.93: *3* TestPython.test_string_test_extra_indent
    def test_string_test_extra_indent(self):
        c = self.c
        s = textwrap.dedent('''\
        class BaseScanner:

                """The base class for all import scanner classes."""

                def __init__ (self,importCommands,language):

                    self.c = ic.c

                def createHeadline (self,parent,body,headline):
                    # g.trace("parent,headline:",parent,headline)
                    return p
        ''')
        self.run_test(c.p, s=s)
    #@+node:ekr.20210904065459.94: *3* TestPython.test_string_underindent_lines
    def test_string_underindent_lines(self):
        c = self.c
        s = textwrap.dedent("""\
            class BaseScanner:
                def containsUnderindentedComment(self):
                    a = 2
                # A true underindented comment.
                    b = 3
                # This underindented comment should be placed with next function.
                def empty(self):
                    pass
        """)
        self.run_test(c.p, s=s)
    #@+node:ekr.20210904065459.95: *3* TestPython.test_string_underindent_lines_2
    def test_string_underindent_lines_2(self):
        c = self.c
        s = textwrap.dedent("""\
            class BaseScanner:
                def containsUnderindentedComment(self):
                    a = 2
                #
                    b = 3
                    # This comment is part of the present function.

                def empty(self):
                    pass
        """)
        self.run_test(c.p, s=s)
    #@+node:ekr.20210904065459.96: *3* TestPython.test_top_level_later_decl
    def test_top_level_later_decl(self):
        # From xo.py.
        c = self.c
        # The first line *must* be blank.
        s = textwrap.dedent(r'''

            #!/usr/bin/env python3

            import os
            import re

            def merge_value(v1, v2):
                return v

            class MainDisplay(object):

                def save_file(self):
                    """Write the file out to disk."""
                    with open(self.save_name, "w") as f:
                        for newline in newlines:
                            f.write(newline)

            # The next line should be included at the end of the class node.

            ensure_endswith_newline = lambda x: x if x.endswith('\n') else x + '\n'

            def retab(s, tabsize):
                return ''.join(pieces)

            if __name__=="__main__":
                main()

        ''')
        table = (
            (1, 'Declarations'),
            (1, 'merge_value'),
            (1, 'class MainDisplay(object)'),
            (2, 'save_file'),
            (1, 'retab'),
        )
        p = c.p
        self.run_test(p, s=s)
        root = p.lastChild()
        assert root
        self.assertEqual(root.h, '@file test')
        after = p.nodeAfterTree()
        p = root.firstChild()
        for n, h in table:
            assert p, h
            n2 = p.level() - root.level()
            self.assertEqual(h, p.h)
            self.assertEqual(n, n2)
            p.moveToThreadNext()
        self.assertEqual(p, after)
    #@+node:ekr.20210904065459.97: *3* TestPython.test_trailing_comment
    def test_trailing_comment(self):
        c = self.c
        s = textwrap.dedent("""\
            class aClass: # trailing comment


                def def1(self):             # trailing comment
                    pass
        """)
        self.run_test(c.p, s=s)
    #@+node:ekr.20210904065459.98: *3* TestPython.test_trailing_comment_outer_levels
    def test_trailing_comment_outer_levels(self):
        c = self.c
        s = textwrap.dedent("""\
            xyz = 6 # trailing comment
            pass
        """)
        self.run_test(c.p, s=s)
    #@+node:ekr.20210904065459.99: *3* TestPython.test_two_functions
    def test_two_functions(self):
        # For comparison with unindent does not end function.
        c = self.c
        s = textwrap.dedent("""\
            def foo():
                pass

            def bar():
                pass
        """)
        self.run_test(c.p, s=s)
    #@+node:ekr.20210904065459.100: *3* TestPython.test_underindent_method
    def test_underindent_method(self):
        c = self.c
        s = textwrap.dedent('''\
            class emptyClass:

                def spam():
                    """docstring line 1
            under-indented docstring line"""
                    pass

            def followingDef(): # comment
                pass
        ''')
        table = (
            (1, 'class emptyClass'),
            (2, 'spam'),
            (1, 'followingDef'),
        )
        p = c.p
        self.run_test(p, s=s)
        after = p.nodeAfterTree()
        root = p.lastChild()
        self.assertEqual(root.h, '@file test')
        p = root.firstChild()
        for n, h in table:
            n2 = p.level() - root.level()
            self.assertEqual(h, p.h)
            self.assertEqual(n, n2)
            p.moveToThreadNext()
        self.assertEqual(p, after)
    #@+node:ekr.20210904065459.101: *3* TestPython.test_unindent_in_triple_string_does_not_end_function
    def test_unindent_in_triple_string_does_not_end_function(self):
        c = self.c
        s = textwrap.dedent('''\
            def foo():

                error("""line1
            line2.
            """)

                a = 5

            def bar():
                pass
        ''')
        p = c.p
        self.run_test(p, s=s)
        child = p.firstChild()
        n = child.numberOfChildren()
        self.assertEqual(n, 2)
    #@+node:ekr.20210904065459.102: *3* TestPython.test_unittest_perfectImport_formatter_py
    def test_unittest_perfectImport_formatter_py(self):
        c = self.c

        s = textwrap.dedent('''\

            """Generic output formatting.
            """

            import sys


            AS_IS = None


            class NullFormatter:
                """A formatter which does nothing.

                If the writer parameter is omitted, a NullWriter instance is created.
                No methods of the writer are called by NullFormatter instances.

                Implementations should inherit from this class if implementing a writer
                interface but don't need to inherit any implementation.

                """

                def __init__(self, writer=None):
                    if writer is None:
                        writer = NullWriter()
                    self.writer = writer
                def end_paragraph(self, blankline): pass
                def add_line_break(self): pass
                def add_hor_rule(self, *args, **kw): pass
                def add_label_data(self, format, counter, blankline=None): pass
                def add_flowing_data(self, data): pass
                def add_literal_data(self, data): pass
                def flush_softspace(self): pass
                def push_alignment(self, align): pass
                def pop_alignment(self): pass
                def push_font(self, x): pass
                def pop_font(self): pass
                def push_margin(self, margin): pass
                def pop_margin(self): pass
                def set_spacing(self, spacing): pass
                def push_style(self, *styles): pass
                def pop_style(self, n=1): pass
                def assert_line_data(self, flag=1): pass


            class AbstractFormatter:
                """The standard formatter.

                This implementation has demonstrated wide applicability to many writers,
                and may be used directly in most circumstances.  It has been used to
                implement a full-featured World Wide Web browser.

                """

                #  Space handling policy:  blank spaces at the boundary between elements
                #  are handled by the outermost context.  "Literal" data is not checked
                #  to determine context, so spaces in literal data are handled directly
                #  in all circumstances.

                def __init__(self, writer):
                    self.writer = writer            # Output device
                    self.align = None               # Current alignment
                    self.align_stack = []           # Alignment stack
                    self.font_stack = []            # Font state
                    self.margin_stack = []          # Margin state
                    self.spacing = None             # Vertical spacing state
                    self.style_stack = []           # Other state, e.g. color
                    self.nospace = 1                # Should leading space be suppressed
                    self.softspace = 0              # Should a space be inserted
                    self.para_end = 1               # Just ended a paragraph
                    self.parskip = 0                # Skipped space between paragraphs?
                    self.hard_break = 1             # Have a hard break
                    self.have_label = 0

                def end_paragraph(self, blankline):
                    if not self.hard_break:
                        self.writer.send_line_break()
                        self.have_label = 0
                    if self.parskip < blankline and not self.have_label:
                        self.writer.send_paragraph(blankline - self.parskip)
                        self.parskip = blankline
                        self.have_label = 0
                    self.hard_break = self.nospace = self.para_end = 1
                    self.softspace = 0

                def add_line_break(self):
                    if not (self.hard_break or self.para_end):
                        self.writer.send_line_break()
                        self.have_label = self.parskip = 0
                    self.hard_break = self.nospace = 1
                    self.softspace = 0

                def add_hor_rule(self, *args, **kw):
                    if not self.hard_break:
                        self.writer.send_line_break()
                    self.writer.send_hor_rule(*args, **kw)
                    self.hard_break = self.nospace = 1
                    self.have_label = self.para_end = self.softspace = self.parskip = 0

                def add_label_data(self, format, counter, blankline = None):
                    if self.have_label or not self.hard_break:
                        self.writer.send_line_break()
                    if not self.para_end:
                        self.writer.send_paragraph((blankline and 1) or 0)
                    if isinstance(format, str):
                        self.writer.send_label_data(self.format_counter(format, counter))
                    else:
                        self.writer.send_label_data(format)
                    self.nospace = self.have_label = self.hard_break = self.para_end = 1
                    self.softspace = self.parskip = 0

                def format_counter(self, format, counter):
                    label = ''
                    for c in format:
                        if c == '1':
                            label = label + ('%d' % counter)
                        elif c in 'aA':
                            if counter > 0:
                                label = label + self.format_letter(c, counter)
                        elif c in 'iI':
                            if counter > 0:
                                label = label + self.format_roman(c, counter)
                        else:
                            label = label + c
                    return label

                def format_letter(self, case, counter):
                    label = ''
                    while counter > 0:
                        counter, x = divmod(counter-1, 26)
                        # This makes a strong assumption that lowercase letters
                        # and uppercase letters form two contiguous blocks, with
                        # letters in order!
                        s = chr(ord(case) + x)
                        label = s + label
                    return label

                def format_roman(self, case, counter):
                    ones = ['i', 'x', 'c', 'm']
                    fives = ['v', 'l', 'd']
                    label, index = '', 0
                    # This will die of IndexError when counter is too big
                    while counter > 0:
                        counter, x = divmod(counter, 10)
                        if x == 9:
                            label = ones[index] + ones[index+1] + label
                        elif x == 4:
                            label = ones[index] + fives[index] + label
                        else:
                            if x >= 5:
                                s = fives[index]
                                x = x-5
                            else:
                                s = ''
                            s = s + ones[index]*x
                            label = s + label
                        index = index + 1
                    if case == 'I':
                        return label.upper()
                    return label

                def add_flowing_data(self, data):
                    if not data: return
                    # The following looks a bit convoluted but is a great improvement over
                    # data = regsub.gsub('[' + string.whitespace + ']+', ' ', data)
                    prespace = data[:1].isspace()
                    postspace = data[-1:].isspace()
                    data = " ".join(data.split())
                    if self.nospace and not data:
                        return
                    elif prespace or self.softspace:
                        if not data:
                            if not self.nospace:
                                self.softspace = 1
                                self.parskip = 0
                            return
                        if not self.nospace:
                            data = ' ' + data
                    self.hard_break = self.nospace = self.para_end = \
                                      self.parskip = self.have_label = 0
                    self.softspace = postspace
                    self.writer.send_flowing_data(data)

                def add_literal_data(self, data):
                    if not data: return
                    if self.softspace:
                        self.writer.send_flowing_data(" ")
                    self.hard_break = data[-1:] == '\n'
                    self.nospace = self.para_end = self.softspace = \
                                   self.parskip = self.have_label = 0
                    self.writer.send_literal_data(data)

                def flush_softspace(self):
                    if self.softspace:
                        self.hard_break = self.para_end = self.parskip = \
                                          self.have_label = self.softspace = 0
                        self.nospace = 1
                        self.writer.send_flowing_data(' ')

                def push_alignment(self, align):
                    if align and align != self.align:
                        self.writer.new_alignment(align)
                        self.align = align
                        self.align_stack.append(align)
                    else:
                        self.align_stack.append(self.align)

                def pop_alignment(self):
                    if self.align_stack:
                        del self.align_stack[-1]
                    if self.align_stack:
                        self.align = align = self.align_stack[-1]
                        self.writer.new_alignment(align)
                    else:
                        self.align = None
                        self.writer.new_alignment(None)

                def push_font(self, (size, i, b, tt)):
                    if self.softspace:
                        self.hard_break = self.para_end = self.softspace = 0
                        self.nospace = 1
                        self.writer.send_flowing_data(' ')
                    if self.font_stack:
                        csize, ci, cb, ctt = self.font_stack[-1]
                        if size is AS_IS: size = csize
                        if i is AS_IS: i = ci
                        if b is AS_IS: b = cb
                        if tt is AS_IS: tt = ctt
                    font = (size, i, b, tt)
                    self.font_stack.append(font)
                    self.writer.new_font(font)

                def pop_font(self):
                    if self.font_stack:
                        del self.font_stack[-1]
                    if self.font_stack:
                        font = self.font_stack[-1]
                    else:
                        font = None
                    self.writer.new_font(font)

                def push_margin(self, margin):
                    self.margin_stack.append(margin)
                    fstack = filter(None, self.margin_stack)
                    if not margin and fstack:
                        margin = fstack[-1]
                    self.writer.new_margin(margin, len(fstack))

                def pop_margin(self):
                    if self.margin_stack:
                        del self.margin_stack[-1]
                    fstack = filter(None, self.margin_stack)
                    if fstack:
                        margin = fstack[-1]
                    else:
                        margin = None
                    self.writer.new_margin(margin, len(fstack))

                def set_spacing(self, spacing):
                    self.spacing = spacing
                    self.writer.new_spacing(spacing)

                def push_style(self, *styles):
                    if self.softspace:
                        self.hard_break = self.para_end = self.softspace = 0
                        self.nospace = 1
                        self.writer.send_flowing_data(' ')
                    for style in styles:
                        self.style_stack.append(style)
                    self.writer.new_styles(tuple(self.style_stack))

                def pop_style(self, n=1):
                    del self.style_stack[-n:]
                    self.writer.new_styles(tuple(self.style_stack))

                def assert_line_data(self, flag=1):
                    self.nospace = self.hard_break = not flag
                    self.para_end = self.parskip = self.have_label = 0


            class NullWriter:
                """Minimal writer interface to use in testing & inheritance.

                A writer which only provides the interface definition; no actions are
                taken on any methods.  This should be the base class for all writers
                which do not need to inherit any implementation methods.

                """
                def __init__(self): pass
                def flush(self): pass
                def new_alignment(self, align): pass
                def new_font(self, font): pass
                def new_margin(self, margin, level): pass
                def new_spacing(self, spacing): pass
                def new_styles(self, styles): pass
                def send_paragraph(self, blankline): pass
                def send_line_break(self): pass
                def send_hor_rule(self, *args, **kw): pass
                def send_label_data(self, data): pass
                def send_flowing_data(self, data): pass
                def send_literal_data(self, data): pass


            class AbstractWriter(NullWriter):
                """A writer which can be used in debugging formatters, but not much else.

                Each method simply announces itself by printing its name and
                arguments on standard output.

                """

                def new_alignment(self, align):
                    print "new_alignment(%s)" % `align`

                def new_font(self, font):
                    print "new_font(%s)" % `font`

                def new_margin(self, margin, level):
                    print "new_margin(%s, %d)" % (`margin`, level)

                def new_spacing(self, spacing):
                    print "new_spacing(%s)" % `spacing`

                def new_styles(self, styles):
                    print "new_styles(%s)" % `styles`

                def send_paragraph(self, blankline):
                    print "send_paragraph(%s)" % `blankline`

                def send_line_break(self):
                    print "send_line_break()"

                def send_hor_rule(self, *args, **kw):
                    print "send_hor_rule()"

                def send_label_data(self, data):
                    print "send_label_data(%s)" % `data`

                def send_flowing_data(self, data):
                    print "send_flowing_data(%s)" % `data`

                def send_literal_data(self, data):
                    print "send_literal_data(%s)" % `data`


            class DumbWriter(NullWriter):
                """Simple writer class which writes output on the file object passed in
                as the file parameter or, if file is omitted, on standard output.  The
                output is simply word-wrapped to the number of columns specified by
                the maxcol parameter.  This class is suitable for reflowing a sequence
                of paragraphs.

                """

                def __init__(self, file=None, maxcol=72):
                    self.file = file or sys.stdout
                    self.maxcol = maxcol
                    NullWriter.__init__(self)
                    self.reset()

                def reset(self):
                    self.col = 0
                    self.atbreak = 0

                def send_paragraph(self, blankline):
                    self.file.write('\n'*blankline)
                    self.col = 0
                    self.atbreak = 0

                def send_line_break(self):
                    self.file.write('\n')
                    self.col = 0
                    self.atbreak = 0

                def send_hor_rule(self, *args, **kw):
                    self.file.write('\n')
                    self.file.write('-'*self.maxcol)
                    self.file.write('\n')
                    self.col = 0
                    self.atbreak = 0

                def send_literal_data(self, data):
                    self.file.write(data)
                    i = data.rfind('\n')
                    if i >= 0:
                        self.col = 0
                        data = data[i+1:]
                    data = data.expandtabs()
                    self.col = self.col + len(data)
                    self.atbreak = 0

                def send_flowing_data(self, data):
                    if not data: return
                    atbreak = self.atbreak or data[0].isspace()
                    col = self.col
                    maxcol = self.maxcol
                    write = self.file.write
                    for word in data.split():
                        if atbreak:
                            if col + len(word) >= maxcol:
                                write('\n')
                                col = 0
                            else:
                                write(' ')
                                col = col + 1
                        write(word)
                        col = col + len(word)
                        atbreak = 1
                    self.col = col
                    self.atbreak = data[-1].isspace()


            def test(file = None):
                w = DumbWriter()
                f = AbstractFormatter(w)
                if file is not None:
                    fp = open(file)
                elif sys.argv[1:]:
                    fp = open(sys.argv[1])
                else:
                    fp = sys.stdin
                while 1:
                    line = fp.readline()
                    if not line:
                        break
                    if line == '\n':
                        f.end_paragraph(1)
                    else:
                        f.add_flowing_data(line)
                f.end_paragraph(0)


            if __name__ == '__main__':
                test()
        ''')
        self.run_test(c.p, s=s)
    #@-others
#@+node:ekr.20211108050827.1: ** class TestRst (BaseTestImporter)
class TestRst(BaseTestImporter):
    
    ext = '.rst'
    
    #@+others
    #@+node:ekr.20210904065459.115: *3* TestRst.test_test1
    def test_test1(self):
        c = self.c
        try:
            import docutils
            assert docutils
        except Exception:
            self.skipTest('no docutils')

        s = textwrap.dedent("""\
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
        """)
        table = (
            '!Dummy chapter',
            'top',
            'section 1',
            'section 2',
            'section 2.1',
            'section 2.1.1',
            'section 3',
            'placeholder',
            'section 3.1.1',
        )
        self.run_test(c.p, s)
        root = c.p.lastChild()
        self.assertEqual(root.h, '@auto-rst test')
        p2 = root.firstChild()
        for h in table:
            self.assertEqual(p2.h, h)
            p2.moveToThreadNext()
        assert not root.isAncestorOf(p2), p2.h  # Extra nodes
    #@+node:ekr.20210904065459.116: *3* TestRst.test_simple
    def test_simple(self):
        c = self.c
        try:
            import docutils
            assert docutils
        except Exception:
            self.skipTest('no docutils')

        s = textwrap.dedent("""\
            .. toc

            .. The section name contains trailing whitespace.

            =======
            Chapter
            =======

            The top chapter.
        """)
        table = (
            "!Dummy chapter",
            "Chapter",
        )
        self.run_test(c.p, s)
        root = c.p.lastChild()
        self.assertEqual(root.h, '@auto-rst test')
        p2 = root.firstChild()
        for h in table:
            self.assertEqual(p2.h, h)
            p2.moveToThreadNext()
        assert not root.isAncestorOf(p2), p2.h  # Extra nodes
    #@+node:ekr.20210904065459.117: *3* TestRst.test_no_double_underlines
    def test_no_double_underlines(self):
        c = self.c
        try:
            import docutils
            assert docutils
        except Exception:
            self.skipTest('no docutils')

        s = textwrap.dedent("""\
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
        """)
        table = (
            '!Dummy chapter',
            'top',
            'section 1',
            'section 2',
            'section 2.1',
            'section 2.1.1',
            'section 3',
            'placeholder',
            'section 3.1.1',
        )
        self.run_test(c.p, s)
        root = c.p.lastChild()
        self.assertEqual(root.h, '@auto-rst test')
        p2 = root.firstChild()
        for h in table:
            self.assertEqual(p2.h, h)
            p2.moveToThreadNext()
        assert not root.isAncestorOf(p2), p2.h  # Extra nodes
    #@+node:ekr.20210904065459.118: *3* TestRst.test_long_underlines
    def test_long_underlines(self):
        c = self.c
        try:
            import docutils
            assert docutils
        except Exception:
            self.skipTest('no docutils')

        s = textwrap.dedent("""\
            .. toc

            top
            -------------

            The top section
        """)
        table = (
            '!Dummy chapter',
            'top',
        )
        self.run_test(c.p, s)
        root = c.p.lastChild()
        self.assertEqual(root.h, '@auto-rst test')
        p2 = root.firstChild()
        for h in table:
            self.assertEqual(p2.h, h)
            p2.moveToThreadNext()
        assert not root.isAncestorOf(p2), p2.h  # Extra nodes
    #@+node:ekr.20210904065459.119: *3* TestRst.test_test_long_overlines
    def test_test_long_overlines(self):
        c = self.c
        try:
            import docutils
            assert docutils
        except Exception:
            self.skipTest('no docutils')

        s = textwrap.dedent("""\
            .. toc

            ======
            top
            ======

            The top section
        """)
        table = (
            "!Dummy chapter",
            "top",
        )
        self.run_test(c.p, s)
        root = c.p.lastChild()
        self.assertEqual(root.h, '@auto-rst test')
        p2 = root.firstChild()
        for h in table:
            self.assertEqual(p2.h, h)
            p2.moveToThreadNext()
        assert not root.isAncestorOf(p2), p2.h  # Extra nodes
    #@+node:ekr.20210904065459.120: *3* TestRst.test_trailing_whitespace
    def test_trailing_whitespace(self):
        c = self.c
        try:
            import docutils
            assert docutils
        except Exception:
            self.skipTest('no docutils')

        s = textwrap.dedent("""\
            .. toc

            .. The section name contains trailing whitespace.

            ======
            top
            ======

            The top section.
        """)
        table = (
            "!Dummy chapter",
            "top",
        )
        p = c.p
        self.run_test(c.p, s)
        root = p.lastChild()
        self.assertEqual(root.h, '@auto-rst test')
        p2 = root.firstChild()
        for h in table:
            self.assertEqual(p2.h, h)
            p2.moveToThreadNext()
        assert not root.isAncestorOf(p2), p2.h  # Extra nodes
    #@+node:ekr.20210904065459.121: *3* TestRst.test_leo_rst
    def test_leo_rst(self):
        c = self.c
        try:
            import docutils
            assert docutils
        except Exception:
            self.skipTest('no docutils')

        # All heading must be followed by an empty line.
        s = textwrap.dedent("""\
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
        """)
        table = (
            'Chapter 1',
            'section 1',
            'section 2',
        )
        self.run_test(c.p, s)
        root = c.p.lastChild()
        self.assertEqual(root.h, '@auto-rst test')
        p2 = root.firstChild()
        assert p2, g.tree_to_string(c)
        for h in table:
            self.assertEqual(p2.h, h)
            p2.moveToThreadNext()
        assert not root.isAncestorOf(p2), p2.h  # Extra nodes
    #@-others
#@+node:ekr.20211108083038.1: ** class TestTypescript (BaseTestImporter)
class TestTypescript (BaseTestImporter):
    
    ext = '.ts'
    
    #@+others
    #@+node:ekr.20210904065459.103: *3* TestTypescript.test_class
    def test_class(self):
        c = self.c
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

        self.run_test(c.p, s)
    #@+node:ekr.20210904065459.104: *3* TestTypescript.test_module
    def test_module(self):
        c = self.c
        s = textwrap.dedent('''\
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
        ''')

        self.run_test(c.p, s)
    #@-others
#@+node:ekr.20211108065014.1: ** class TestXML (BaseTestImporter)
class TestXML (BaseTestImporter):
    
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
        s = textwrap.dedent("""\
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
        """)
        table = (
            (1, "<html>"),
            (2, "<head>"),
            (2, "<body class='bodystring'>"),
        )
        p = c.p
        self.run_test(p, s)
        after = p.nodeAfterTree()
        root = p.lastChild()
        self.assertEqual(root.h, '@file test')
        p = root.firstChild()
        for n, h in table:
            n2 = p.level() - root.level()
            self.assertEqual(h, p.h)
            self.assertEqual(n, n2)
            p.moveToThreadNext()
        self.assertEqual(p, after)
    #@+node:ekr.20210904065459.106: *3* TestXml.test_1
    def test_1(self):
        c = self.c
        s = textwrap.dedent("""\
            <html>
            <head>
                <title>Bodystring</title>
            </head>
            <body class='bodystring'>
            <div id='bodydisplay'></div>
            </body>
            </html>
        """)
        table = (
            (1, "<html>"),
            (2, "<head>"),
            (2, "<body class='bodystring'>"),
        )
        p = c.p
        self.run_test(p, s)
        after = p.nodeAfterTree()
        root = p.lastChild()
        self.assertEqual(root.h, '@file test')
        p = root.firstChild()
        assert p, g.tree_to_string(c)
        for n, h in table:
            n2 = p.level() - root.level()
            self.assertEqual(h, p.h)
            self.assertEqual(n, n2)
            p.moveToThreadNext()
        self.assertEqual(p, after)

    #@+node:ekr.20210904065459.108: *3* TestXml.test_non_ascii_tags
    def test_non_ascii_tags(self):
        c = self.c
        s = textwrap.dedent("""\
            <:À.Ç>
            <Ì>
            <_.ÌÑ>
        """)
        self.run_test(c.p, s)
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

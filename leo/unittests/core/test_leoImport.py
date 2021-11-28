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
    skip_flag = False  # Subclasses can set this to suppress perfect-import checks.
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
        after = p1.nodeAfterTree()
        try:
            self.assertEqual(p1.h, f"{self.treeType} {self.id()}")
            p.moveToThreadNext()
            for data in table:
                n, h = data
                self.assertEqual(p.h, h)
                self.assertEqual(p.level() - p1.level(), n, msg=p.h)
                p.moveToThreadNext()
            # Make sure there are no extra nodes in p's tree.
            self.assertFalse(p1.isAncestorOf(p), msg=p.h)
            self.assertEqual(p, after, msg=p and p.h or "No Node")
        except AssertionError:
            self.dump_tree(p1)
            raise
    #@+node:ekr.20211108044605.1: *3* BaseTestImporter.compute_unit_test_kind
    def compute_unit_test_kind(self, ext):
        """Return kind from the given extention."""
        aClass = g.app.classDispatchDict.get(ext)
        if aClass:
            d2 = g.app.atAutoDict
            for z in d2:
                if d2.get(z) == aClass:
                    return z
        return '@file'
    #@+node:ekr.20211127042843.1: *3* BaseTestImporter.run_test
    def run_test(self, s, verbose=False):
        """
        Run a unit test of an import scanner,
        i.e., create a tree from string s at location p.
        """
        c, ext, p = self.c, self.ext, self.c.p
        self.assertTrue(ext)
        ### self.treeType = '@file'  # Fix #352.
        # Run the test.
        parent = p.insertAsLastChild()
        kind = self.compute_unit_test_kind(ext)
        parent.h = f"{kind} {self.id()}"
        # Suppress perfect-import checks if self.skip_flag is True
        if self.skip_flag:
            g.trace('SKIP', p.h)
            g.app.suppressImportChecks = True
        # createOutline calls Importer.gen_lines and Importer.check.
        ok = c.importCommands.createOutline(
            parent=parent.copy(), ext=ext, s=textwrap.dedent(s))
        self.assertTrue(ok)
        return parent
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
                register long longValue;	/* Long integer used to initialize the
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
class TestCoffeescript (BaseTestImporter):
    
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
class TestCython (BaseTestImporter):
    
    ext = '.pyx'
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
        (1, 'Declarations'),
        (1, 'double'),
        (1, 'print_result'),
    ))
#@+node:ekr.20211108064115.1: ** class TestDart (BaseTestImporter)
class TestDart (BaseTestImporter):
    
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
class TestElisp (BaseTestImporter):
    
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
class TestJava (BaseTestImporter):
    
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
class TestJavascript (BaseTestImporter):
    
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

            `​``python
            loads.init = {
                Chloride: 11.5,
                TotalP: 0.002,
            }
            `​``
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
class TestOrg (BaseTestImporter):
    
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
class TestOtl (BaseTestImporter):
    
    ext = '.otl'
    treeType = '@auto-otl'
    
    #@+others
    #@+node:ekr.20210904065459.49: *3* TestOtl.test_1
    def test_1(self):

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
            # Is this table correct?
            (1, 'preamble.'),
            (1, 'Section 1'),
            (1, 'Section 2'),
            (1, 'Section 2-1'),
            (1, 'Section 2-1-1'),
            (1, 'Section 3'),
            (1, 'Section 3.1'),
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
class TestPascal (BaseTestImporter):
    
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
class TestPerl (BaseTestImporter):
    
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
class TestPhp (BaseTestImporter):
    
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
class TestPython (BaseTestImporter):
    
    check_tree = False
    ext = '.py'

    #@+others
    #@+node:ekr.20211125084921.1: *3* TestPython.run_python_test & helpers
    def run_python_test(self, input_s, expected_s=None, verbose=False):
        """
        Create a tree whose root is c.p from string s.
        
        If a line that starts with "# Expect:" exists in s, the following lines
        represent the expected tree in enhanced MORE format.
        """
        # Init, as in the base class.
        c = self.c
        root = c.p
        c, ext = self.c, self.ext
        self.assertTrue(ext)
        self.treeType = '@file'
        kind = self.compute_unit_test_kind(ext)
        # Create the parent and the expected parent nodes.
        parent = root.insertAsLastChild()
        parent.h = f"{kind} {self.id()}"
        expected_parent = root.insertAsLastChild()
        expected_parent.h = parent.h
        # Suppress perfect-import checks if self.skip_flag is True
        if self.skip_flag:
            g.app.suppressImportChecks = True
        # Create the outline. This calls py_i.gen_lines.
        c.importCommands.createOutline(
            parent=parent.copy(), ext=ext, s=textwrap.dedent(input_s))
        # Compare the created and expected outlines.
        if expected_s:
            expected_s2 = textwrap.dedent(expected_s).strip().replace('AT', '@') + '\n'
            self.create_expected_outline(expected_parent, expected_s2)
            self.compare_outlines(parent, expected_parent)
    #@+node:ekr.20211125101517.4: *4* create_expected_outline
    def  create_expected_outline(self, expected_parent, expected_s):
        """
        Create the expected outline, making 'kind' entries in g.vnode_info for
        all *created* vnodes.
        
        root_p:     The root of the expected outline.
        expect_s:   A string representing the outline in enhanced MORE format.
        
        """
        d = g.vnode_info
        # Special case for the top-level node.
        d [expected_parent.v] = { 'kind': 'outer' }
        expected_lines = g.splitLines(expected_s.strip() + '\n\n')
        stack = [(-1, expected_parent)]  # (level, p)
        for s in expected_lines:
            if s.strip().startswith('- outer:'):
                # The lines following `- outer` can specify non-standard top-level text.
                # If none are given, assume the standard top-level text below.
                pass  # ignore.
            elif s.strip().startswith('-'):
                n = len(s) - len(s.lstrip())
                lws = s[:n]
                assert n == 0 or lws.isspace(), repr(lws)
                while stack:
                    level, p = stack.pop()
                    
                    if s.strip().startswith('- '):
                        aList = s.strip()[2:].split(':')
                        kind, h = aList[0].strip(), ':'.join(aList[1:])
                        self.assertTrue(kind in ('outer', 'org', 'class', 'def'), msg=repr(s))
                    if n >= level:
                        p.b = p.b.strip()
                        if n > level:
                            child = p.insertAsLastChild()
                        else:
                            child = p.insertAfter()
                        child.h = h
                        d [child.v] = { 'kind': kind }
                        p = child
                        stack.append((n, p))
                        break
                    else:
                        pass  # Look for next entry.
                else:
                    g.printObj(expected_lines, tag='===== Expected')
                    assert False, f"No node at level {n}"
            else:
                junk_level, p = stack[-1]
                p.b += s
        # Create standard outer node body if expected_parent.b is empty.
        if not expected_parent.b:
            expected_parent.b = textwrap.dedent("""
                ATothers
                ATlanguage python
                ATtabwidth -4
            """).replace('AT', '@')
    #@+node:ekr.20211126052156.1: *4* compare_outlines
    def compare_outlines(self, created_p, expected_p):
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
        if 0:  ###
            self.dump_tree(created_p, tag='===== Created')
            self.dump_tree(expected_p, tag='===== Expected')
    #@+node:ekr.20211126055349.1: *3* TestPython.test_run_python_test
    def test_run_python_test(self): 

        input_s = '''
            """A docstring"""
            switch = 1
        '''
        # Test explicit specification of outer node.
        expected_s1 = '''
            - outer:
            ATothers
            ATlanguage python
            ATtabwidth -4
              - org:Organizer: Declarations
            """A docstring"""
            switch = 1
        '''
        self.run_python_test(input_s, expected_s1)
        # Test standard contents of outer node.
        expected_s2 = '''
            - outer:
              - org:Organizer: Declarations
            """A docstring"""
            switch = 1
        '''
        self.run_python_test(input_s, expected_s2)
         # Test implict contents of outer node.
        expected_s3 = '''
              - org:Organizer: Declarations
            """A docstring"""
            switch = 1
        '''
        self.run_python_test(input_s, expected_s3)
    #@+node:ekr.20211127031823.1: *3* TestPython: New (generated) tests
    #@+node:ekr.20211127032323.1: *4* pass...
    #@+node:ekr.20211127031823.2: *5* test_docstring_vars
    def test_docstring_vars(self):

        input_s = '''
            """A docstring"""
            switch = 1
        '''
        expected_s = '''
            - org:Organizer: Declarations
            """A docstring"""
            switch = 1
        '''
        self.run_python_test(input_s, expected_s)

    #@+node:ekr.20211127032346.1: *4* fail...
    #@+node:ekr.20211127031823.3: *4* test_docstring_vars_outer_def
    def test_docstring_vars_outer_def(self):

        input_s = '''
            """A docstring"""
            switch = 1
            
            def d1:
                pass
        '''
        expected_s = '''
            - outer:
              - org: Organizer Declarations
            """A docstring"""
            switch = 1
              - def:function: d1
            def d1:
                pass
        '''
        self.run_python_test(input_s, expected_s)

    #@+node:ekr.20211127031823.4: *4* test_docstring_vars_class
    def test_docstring_vars_class(self):

        input_s = '''
            """A docstring"""
            switch = 1
            
            class Class1:
                def method1(self):
                    pass
        '''
        expected_s = '''
            - outer:
              - Declarations
            """A docstring"""
            switch = 1
            
              - class:class Class1
            class Class1:
                ATothers
                - def: method1:
            def method1(self):
                pass
        '''
        self.run_python_test(input_s, expected_s)

    #@+node:ekr.20211126055225.1: *3* TestPython: Old tests
    #@+node:ekr.20210904065459.62: *4* TestPython.test_bad_class
    def test_bad_class(self):

        s = """
            class testClass1 # no colon
                pass

            def spam():
                pass
        """
        self.run_test(s)
    #@+node:ekr.20210904065459.63: *4* TestPython.test_basic_nesting
    def test_basic_nesting(self):
        c = self.c
        s = """
            import sys
            def outer_def1():
                pass
            class Class1:
                def class1_method1():
                    pass
                def class1_method2():
                    def helper():
                        pass
                if False or g.unitTesting:

                    def pr(*args,**keys): # reportMismatch test
                        g.es_print(color='blue',*args,**keys)

                    pr('input...')

                def class1_method3(self):
                    pass
                # tail of Class1
                m2 = class1_method2

            if 1:
                def outer_def2():
                    pass
                # After def2
            def outer_def3():
                pass
            # An outer comment
            class Class2:
                @my_decorator
                def class2_method1():
                    pass
                @my_decorator
                def class2_method2():
                    pass
     
            def main():
                pass
        
            if __name__ == '__main__':
                main()
        """
        table = (
            (1, 'class class1'),
            (2, 'class1_method1'),
            (2, 'class1_method2'),
            (1, 'class class2'),
            (2, 'class2_method1'),
            (2, 'class2_method2'),
        )
        p = c.p
        self.run_test(s, verbose=False)
        if self.check_tree:
            after = p.nodeAfterTree()
            root = p.lastChild()
            self.assertEqual(root.h, f"@file {self.id()}")
            p = root.firstChild()
            for n, h in table:
                n2 = p.level() - root.level()
                self.assertEqual(h, p.h)
                self.assertEqual(n, n2)
                p.moveToThreadNext()
            self.assertEqual(p, after)

    #@+node:ekr.20210904065459.64: *4* TestPython.test_bug_346
    def test_bug_346(self):
        c = self.c
        s = '''
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
        '''
        table = (
            (1, 'Declarations'),
            (1, 'make_parser'),
        )
        p = c.p
        self.run_test(s)
        if self.check_tree:
            after = p.nodeAfterTree()
            root = p.lastChild()
            self.assertEqual(root.h, f"@file {self.id()}")
            p = root.firstChild()
            for n, h in table:
                n2 = p.level() - root.level()
                self.assertEqual(h, p.h)
                self.assertEqual(n, n2)
                p.moveToThreadNext()
            self.assertEqual(p, after)
    #@+node:ekr.20210904065459.65: *4* TestPython.test_bug_354
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
        self.run_test(s)
        if self.check_tree:
            after = p.nodeAfterTree()
            root = p.lastChild()
            self.assertEqual(root.h, f"@file {self.id()}")
            p = root.firstChild()
            for n, h in table:
                n2 = p.level() - root.level()
                self.assertEqual(h, p.h)
                self.assertEqual(n, n2)
                p.moveToThreadNext()
            self.assertEqual(p, after)
    #@+node:ekr.20210904065459.66: *4* TestPython.test_bug_357
    def test_bug_357(self):
        c = self.c
        s = '''
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
        '''
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
        self.run_test(s)
        if self.check_tree:
            after = p.nodeAfterTree()
            root = p.lastChild()
            assert root
            self.assertEqual(root.h, f"@file {self.id()}")
            p = root.firstChild()
            for n, h in table:
                assert p, h
                n2 = p.level() - root.level()
                self.assertEqual(h, p.h)
                self.assertEqual(n, n2)
                p.moveToThreadNext()
            self.assertEqual(p, after)
    #@+node:ekr.20210904065459.67: *4* TestPython.test_bug_360
    def test_bug_360(self):
        c = self.c
        s = """
            ATbase_task(
                targets=['img/who_map.png', 'img/who_map.pdf'],
                file_dep=[data_path('phyto')],
                task_dep=['load_data'],
            )
            def make_map():
                '''make_map - plot the Thompson / Bartsh / WHO map'''
        """.replace('AT', '@')
        table = (
            (1, '@base_task make_map'),
        )
        p = c.p
        self.run_test(s)
        if self.check_tree:
            after = p.nodeAfterTree()
            root = p.lastChild()
            self.assertEqual(root.h, f"@file {self.id()}")
            p = root.firstChild()
            for n, h in table:
                n2 = p.level() - root.level()
                self.assertEqual(h, p.h)
                self.assertEqual(n, n2)
                p.moveToThreadNext()
            self.assertEqual(p, after)
    #@+node:ekr.20210904065459.70: *4* TestPython.test_bug_603720
    def test_bug_603720(self):

        # Leo bug 603720
        # Within the docstring we must change '\' to '\\'
        s = '''
            def foo():
                s = \\
            """#!/bin/bash
            cd /tmp
            ls"""
                file('/tmp/script', 'w').write(s)

            class bar:
                pass

            foo()
        '''
        self.run_test(s)
    #@+node:ekr.20210904065459.69: *4* TestPython.test_bug_978
    def test_bug_978(self):
        c = self.c
        s = """
            import foo
            import bar

            class A(object):
                pass
            class B(foo):
                pass
            class C(bar.Bar):
                pass
        """
        table = (
            (1, 'Declarations'),
            (1, 'class A(object)'),
            (1, 'class B(foo)'),
            (1, 'class C(bar.Bar)'),
        )
        p = c.p
        self.run_test(s)
        if self.check_tree:
            after = p.nodeAfterTree()
            root = p.lastChild()
            assert root
            self.assertEqual(root.h, f"@file {self.id()}")
            p = root.firstChild()
            for n, h in table:
                n2 = p.level() - root.level()
                self.assertEqual(h, p.h)
                self.assertEqual(n, n2)
                p.moveToThreadNext()
            self.assertEqual(p, after)
    #@+node:ekr.20210904065459.72: *4* TestPython.test_class_test_2
    def test_class_test_2(self):

        s = """
            class testClass2:
                pass
        """
        self.run_test(s)
    #@+node:ekr.20210904065459.73: *4* TestPython.test_class_tests_1
    def test_class_tests_1(self):

        s = '''
            class testClass1:
                """A docstring"""
                def __init__ (self):
                    pass
                def f1(self):
                    pass
        '''
        self.run_test(s)
    #@+node:ekr.20210904065459.74: *4* TestPython.test_comment_after_dict_assign
    def test_comment_after_dict_assign(self):
        c = self.c
        s = """
            NS = { 'i': 'http://www.inkscape.org/namespaces/inkscape',
                  's': 'http://www.w3.org/2000/svg',
                  'xlink' : 'http://www.w3.org/1999/xlink'}

            tabLevels = 4  # number of defined tablevels, FIXME, could derive from template?
        """
        table = (
            (1, 'Declarations'),
        )
        p = c.p
        self.run_test(s)
        if self.check_tree:
            after = p.nodeAfterTree()
            root = p.lastChild()
            self.assertEqual(root.h, f"@file {self.id()}")
            p = root.firstChild()
            for n, h in table:
                n2 = p.level() - root.level()
                self.assertEqual(h, p.h)
                self.assertEqual(n, n2)
                p.moveToThreadNext()
            self.assertEqual(p, after)
    #@+node:ekr.20210904065459.75: *4* TestPython.test_decls_1
    def test_decls_1(self):
        c = self.c
        s = """
            import leo.core.leoGlobals as g

            a = 3
        """
        table = (
            (1, 'Declarations'),
        )
        p = c.p
        self.run_test(s)
        if self.check_tree:
            after = p.nodeAfterTree()
            root = p.lastChild()
            self.assertEqual(root.h, f"@file {self.id()}")
            p = root.firstChild()
            for n, h in table:
                n2 = p.level() - root.level()
                self.assertEqual(h, p.h)
                self.assertEqual(n, n2)
                p.moveToThreadNext()
            self.assertEqual(p, after)
    #@+node:ekr.20210904065459.76: *4* TestPython.test_decorator
    def test_decorator(self):
        c = self.c
        s = '''
            class Index:
                """docstring"""
                @cherrypy.nocolor
                @cherrypy.expose
                def index(self):
                    return "Hello world!"

                @cmd('abc')
                def abc(self):
                    return "abc"
        '''
        self.run_test(s)
        if self.check_tree:
            index = g.findNodeInTree(c, c.p, '@cherrypy.nocolor index')
            assert index
            lines = g.splitLines(index.b)
            self.assertEqual(lines[0], '@cherrypy.nocolor\n')
            self.assertEqual(lines[1], '@cherrypy.expose\n')
            abc = g.findNodeInTree(c, c.p, "@cmd('abc') abc")
            lines = g.splitLines(abc.b)
            self.assertEqual(lines[0], "@cmd('abc')\n")
    #@+node:ekr.20210904065459.77: *4* TestPython.test_decorator_2
    def test_decorator_2(self):
        c = self.c
        s = '''
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
        '''
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
        self.run_test(s)
        if self.check_tree:
            after = c.p.nodeAfterTree()
            root = c.p.lastChild()
            self.assertEqual(root.h, f"@file {self.id()}")
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
        
    #@+node:ekr.20210904065459.78: *4* TestPython.test_def_inside_def
    def test_def_inside_def(self):
        c = self.c
        s = '''
            class aClass:
                def outerDef(self):
                    """docstring.
                    line two."""
        
                    def pr(*args,**keys):
                        g.es_print(color='blue',*args,**keys)
        
                    a = 3
        '''
        table = (
            (1, 'class aClass'),
            (2, 'outerDef'),
            # (3, 'pr'),
        )
        p = c.p
        self.run_test(s)
        if self.check_tree:
            after = p.nodeAfterTree()
            root = p.lastChild()
            self.assertEqual(root.h, f"@file {self.id()}")
            p = root.firstChild()
            for n, h in table:
                n2 = p.level() - root.level()
                self.assertEqual(h, p.h)
                self.assertEqual(n, n2)
                p.moveToThreadNext()
            self.assertEqual(p, after)

    #@+node:ekr.20210904065459.79: *4* TestPython.test_def_test_1
    def test_def_test_1(self):
        c = self.c
        s = """
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
        """
        table = (
            (1, 'class test'),
            (2, 'importFilesCommand'),
            (2, 'convertMoreStringToOutlineAfter'),
        )
        p = c.p
        self.run_test(s)
        if self.check_tree:
            after = p.nodeAfterTree()
            root = p.lastChild()
            self.assertEqual(root.h, f"@file {self.id()}")
            p = root.firstChild()
            for n, h in table:
                n2 = p.level() - root.level()
                self.assertEqual(h, p.h)
                self.assertEqual(n, n2)
                p.moveToThreadNext()
            self.assertEqual(p, after)

    #@+node:ekr.20210904065459.80: *4* TestPython.test_def_test_2
    def test_def_test_2(self):
        c = self.c
        s = """
            class test:
                def spam(b):
                    pass

                # Used by paste logic.

                def foo(a):
                    pass
        """
        table = (
            (1, 'class test'),
            (2, 'spam'),
            (2, 'foo'),
        )
        p = c.p
        self.run_test(s)
        if self.check_tree:
            after = p.nodeAfterTree()
            root = p.lastChild()
            self.assertEqual(root.h, f"@file {self.id()}")
            p = root.firstChild()
            for n, h in table:
                n2 = p.level() - root.level()
                self.assertEqual(h, p.h)
                self.assertEqual(n, n2)
                p.moveToThreadNext()
            self.assertEqual(p, after)

    #@+node:ekr.20210904065459.81: *4* TestPython.test_docstring_only
    def test_docstring_only(self):

        s = '''
            """A file consisting only of a docstring.
            """
        '''
        self.run_test(s)
    #@+node:ekr.20210904065459.82: *4* TestPython.test_empty_decls
    def test_empty_decls(self):

        s = """
            import leo.core.leoGlobals as g

            a = 3
        """
        self.run_test(s)
    #@+node:ekr.20210904065459.71: *4* TestPython.test_enhancement_481
    def test_enhancement_481(self):
        c = self.c
        s = """
            ATg.cmd('my-command')
            def myCommand(event=None):
                pass
        """.replace('AT', '@')
        table = (
            # (1, '@g.cmd myCommand'),
            (1, "@g.cmd('my-command') myCommand"),
        )
        p = c.p
        self.run_test(s)
        if self.check_tree:
            after = p.nodeAfterTree()
            root = p.lastChild()
            self.assertEqual(root.h, f"@file {self.id()}")
            p = root.firstChild()
            for n, h in table:
                n2 = p.level() - root.level()
                self.assertEqual(h, p.h)
                self.assertEqual(n, n2)
                p.moveToThreadNext()
            self.assertEqual(p, after)
    #@+node:ekr.20210904065459.83: *4* TestPython.test_extra_leading_ws_test
    def test_extra_leading_ws_test(self):

        s = """
            class cls:
                 def fun(): # one extra space.
                    pass
        """
        self.run_test(s)
    #@+node:ekr.20211108084817.1: *4* TestPython.test_get_leading_indent
    def test_get_leading_indent(self):
        c = self.c
        importer = linescanner.Importer(c.importCommands, language='python')
        self.assertEqual(importer.single_comment, '#')
           
    #@+node:ekr.20210904065459.124: *4* TestPython.test_get_str_lws
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
    #@+node:ekr.20210904065459.60: *4* TestPython.test_i_scan_state
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
    #@+node:ekr.20210904065459.84: *4* TestPython.test_indent_decls
    def test_indent_decls(self):
        c = self.c
        s = '''
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
        '''
        table = (
            (1, 'class mammalProviderBase(object)'),
            (2, '__init__'),
            (2, 'provide'),
            (2, 'imagePath'),
            (1, 'class mainPages(mammalProviderBase)'),
            (2, 'provide'),
        )
        p = c.p
        self.run_test(s)
        if self.check_tree:
            after = p.nodeAfterTree()
            root = p.lastChild()
            self.assertEqual(root.h, f"@file {self.id()}")
            p = root.firstChild()
            for n, h in table:
                n2 = p.level() - root.level()
                self.assertEqual(h, p.h)
                self.assertEqual(n, n2)
                p.moveToThreadNext()
            self.assertEqual(p, after)
    #@+node:ekr.20210904065459.125: *4* TestPython.test_is_ws_line
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
    #@+node:ekr.20210904065459.61: *4* TestPython.test_leoApp_fail
    def test_leoApp_fail(self):
        c = self.c
        s = '''
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
        '''
        table = (
            (1, 'isValidPython'),
            # (2, 'class EmergencyDialog'),
            # (3, 'run'),
            (1, 'loadLocalFile'),
        )
        p = c.p
        self.run_test(s)
        if self.check_tree:
            after = p.nodeAfterTree()
            root = p.lastChild()
            self.assertEqual(root.h, f"@file {self.id()}")
            p = root.firstChild()
            for n, h in table:
                n2 = p.level() - root.level()
                self.assertEqual(h, p.h)
                self.assertEqual(n, n2)
                p.moveToThreadNext()
            self.assertEqual(p, after)

    #@+node:ekr.20210904065459.85: *4* TestPython.test_leoImport_py_small_
    def test_leoImport_py_small_(self):
        c = self.c

        s = """
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
        """
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
        self.run_test(s)
        if self.check_tree:
            after = p.nodeAfterTree()
            root = p.lastChild()
            self.assertEqual(root.h, f"@file {self.id()}")
            p = root.firstChild()
            for n, h in table:
                n2 = p.level() - root.level()
                self.assertEqual(h, p.h)
                self.assertEqual(n, n2)
                p.moveToThreadNext()
            self.assertEqual(p, after)
    #@+node:ekr.20210904065459.86: *4* TestPython.test_looks_like_section_ref
    def test_looks_like_section_ref(self):

        # ~/at-auto-test.py
        # Careful: don't put a section reference in the string.
        s = """
            # This is valid Python, but it looks like a section reference.
            a = b < < c >> d
        """.replace('< <', '<<')
        self.run_test(s)
    #@+node:ekr.20210904065459.87: *4* TestPython.test_minimal_class_1
    def test_minimal_class_1(self):

        s = '''
            class ItasException(Exception):

                pass

            def gpRun(gp, cmd, args, log = None):

                """Wrapper for making calls to the geoprocessor and reporting errors"""

                if log:

                    log('gp: %s: %s\\n' % (cmd, str(args)))
        '''
        self.run_test(s)
    #@+node:ekr.20210904065459.88: *4* TestPython.test_minimal_class_2
    def test_minimal_class_2(self):

        s = """
            class emptyClass: pass

            def followingDef():
                pass
        """
        self.run_test(s)
    #@+node:ekr.20210904065459.89: *4* TestPython.test_minimal_class_3
    def test_minimal_class_3(self):

        s = """
            class emptyClass: pass # comment

            def followingDef(): # comment
                pass
        """
        self.run_test(s)
    #@+node:ekr.20211121055721.1: *4* TestPython.test_minimal_nesting
    def test_minimal_nesting(self):
        c = self.c
        s = """
            import sys
            class Class1:
                def class1_method1():
                    pass
                def class1_method2():
                    def helper():
                        pass
        """
            # def outer_def1():
                # pass
            # def outer_def2():
                # pass
            # # An outer comment
            # class Class2:
                # def class2_method1():
                    # pass
                # def class2_method2():
                    # pass
     
            # def main():
                # pass
        
            # if __name__ == '__main__':
                # main()
        table = (
            (1, 'Declarations'),
            (1, 'outer_def1'),
            (1, 'class Class1'),
            (2, 'class1_method1'),
            (2, 'class1_method2'),
            (1, 'outer_def2'),
            (1, 'class Class2'),
            (2, 'class2_method1'),
            (2, 'class2_method2'),
            (1, 'main'),
        )
        p = c.p
        self.run_test(s, verbose=True)
        if self.check_tree:
            after = p.nodeAfterTree()
            root = p.lastChild()
            self.assertEqual(root.h, f"@file {self.id()}")
            p = root.firstChild()
            for n, h in table:
                n2 = p.level() - root.level()
                self.assertEqual(h, p.h)
                self.assertEqual(n, n2)
                p.moveToThreadNext()
            self.assertEqual(p, after)

    #@+node:ekr.20210904065459.90: *4* TestPython.test_overindent_def_no_following_def
    def test_overindent_def_no_following_def(self):

        s = """
            class aClass:
                def def1(self):
                    pass

                if False or g.unitTesting:

                    def pr(*args,**keys): # reportMismatch test
                        g.es_print(color='blue',*args,**keys)

                    pr('input...')
        """
        self.run_test(s)
    #@+node:ekr.20210904065459.91: *4* TestPython.test_overindent_def_one_following_def
    def test_overindent_def_one_following_def(self):

        s = """
            class aClass:
                def def1(self):
                    pass

                if False or g.unitTesting:

                    def pr(*args,**keys): # reportMismatch test
                        g.es_print(color='blue',*args,**keys)

                    pr('input...')

                def def2(self):
                    pass
        """
        self.run_test(s)
    #@+node:ekr.20211113052244.1: *4* TestPython.test_comment_after_class
    def test_comment_after_class(self):
        # From mypy.errors.py
        s = """
            class ErrorInfo:  # Line 22 of errors.py.
                def __init__(self, a) -> None
                    self.a = a
                    
            # Type used internally to represent errors:
            #   (path, line, column, severity, message, allow_dups, code)
            ErrorTuple = Tuple[Optional[str], int, int]
        """
        self.run_test(s)
    #@+node:ekr.20210904065459.92: *4* TestPython.test_overindented_def_3
    def test_overindented_def_3(self):
        # This caused PyParse.py not to be imported properly.
        c = self.c
        s = '''
            import re
            if 0: # Causes the 'overindent'
               if 0:   # for throwaway debugging output
                  def dump(*stuff):
                    sys.__stdout__.write(" ".join(map(str, stuff)) + "\n")
            for ch in "({[":
               _tran[ord(ch)] = '('
            class testClass1:
                pass
        '''
        table = (
            # (1, 'Declarations'),
            (1, 'class testClass1'),
        )
        p = c.p
        self.run_test(s, verbose=True)
        if self.check_tree:
            after = p.nodeAfterTree()
            root = p.lastChild()
            self.assertEqual(root.h, f"@file {self.id()}")
            p = root.firstChild()
            for n, h in table:
                n2 = p.level() - root.level()
                self.assertEqual(h, p.h)
                self.assertEqual(n, n2)
                p.moveToThreadNext()
            self.assertEqual(p, after)
    #@+node:ekr.20210904065459.68: *4* TestPython.test_promote_if_name_eq_main
    def test_promote_if_name_eq_main(self):
        # Test #390: was test_bug_390.
        c = self.c
        s = """
            import sys

            class Foo():
                pass

            a = 2

            def main(self):
                pass

            if __name__ == '__main__':
                main()
        """
        table = (
            (1, 'Declarations'),
            (1, 'class Foo'),
            (1, 'main'),
        )
        p = c.p
        self.run_test(s)
        if self.check_tree:
            after = p.nodeAfterTree()
            root = p.lastChild()
            self.assertEqual(root.h, f"@file {self.id()}")
            p = root.firstChild()
            for n, h in table:
                n2 = p.level() - root.level()
                self.assertEqual(h, p.h)
                self.assertEqual(n, n2)
                p.moveToThreadNext()
            self.assertEqual(p, after)
            assert "if __name__ == '__main__':" in root.b
            # self.dump_tree()
    #@+node:ekr.20211112135034.1: *4* TestPython.test_promote_only_decls
    def test_promote_only_decls(self):
        # Test #390: was test_bug_390.
        s = """
            a = 1
            b = 2
        """
        self.run_test(s)
        # self.assertEqual(p.numberOfChildren(), 0)
        # root = p.lastChild()
        # self.dump_tree()
    #@+node:ekr.20210904065459.131: *4* TestPython.test_scan_state
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
    #@+node:ekr.20210904065459.93: *4* TestPython.test_string_test_extra_indent
    def test_string_test_extra_indent(self):

        s = '''
        class BaseScanner:

                """The base class for all import scanner classes."""

                def __init__ (self,importCommands,language):

                    self.c = ic.c

                def createHeadline (self,parent,body,headline):
                    # g.trace("parent,headline:",parent,headline)
                    return p
        '''
        self.run_test(s)
    #@+node:ekr.20210904065459.94: *4* TestPython.test_string_underindent_lines
    def test_string_underindent_lines(self):

        s = """
            class BaseScanner:
                def containsUnderindentedComment(self):
                    a = 2
                # A true underindented comment.
                    b = 3
                # This underindented comment should be placed with next function.
                def empty(self):
                    pass
        """
        self.run_test(s)
    #@+node:ekr.20210904065459.95: *4* TestPython.test_string_underindent_lines_2
    def test_string_underindent_lines_2(self):

        s = """
            class BaseScanner:
                def containsUnderindentedComment(self):
                    a = 2
                #
                    b = 3
                    # This comment is part of the present function.

                def empty(self):
                    pass
        """
        self.run_test(s)
    #@+node:ekr.20210904065459.96: *4* TestPython.test_top_level_later_decl
    def test_top_level_later_decl(self):
        # From xo.py.
        c = self.c
        # The first line *must* be blank.
        s = '''

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

        '''
        table = (
            (1, 'Declarations'),
            (1, 'merge_value'),
            (1, 'class MainDisplay(object)'),
            (2, 'save_file'),
            (1, 'retab'),
        )
        p = c.p
        self.run_test(s)
        if self.check_tree:
            root = p.lastChild()
            assert root
            self.assertEqual(root.h, f"@file {self.id()}")
            after = p.nodeAfterTree()
            p = root.firstChild()
            for n, h in table:
                assert p, h
                n2 = p.level() - root.level()
                self.assertEqual(h, p.h)
                self.assertEqual(n, n2)
                p.moveToThreadNext()
            self.assertEqual(p, after)
    #@+node:ekr.20210904065459.97: *4* TestPython.test_trailing_comment
    def test_trailing_comment(self):

        s = """
            class aClass: # trailing comment


                def def1(self):             # trailing comment
                    pass
        """
        self.run_test(s)
    #@+node:ekr.20210904065459.98: *4* TestPython.test_trailing_comment_outer_levels
    def test_trailing_comment_outer_levels(self):

        s = """
            xyz = 6 # trailing comment
            pass
        """
        self.run_test(s)
    #@+node:ekr.20210904065459.99: *4* TestPython.test_two_functions
    def test_two_functions(self):
        # For comparison with unindent does not end function.
        s = """
            def foo():
                pass

            def bar():
                pass
        """
        self.run_test(s)
    #@+node:ekr.20210904065459.100: *4* TestPython.test_underindent_method
    def test_underindent_method(self):
        c = self.c
        s = '''
            class emptyClass:

                def spam():
                    """docstring line 1
            under-indented docstring line"""
                    pass

            def followingDef(): # comment
                pass
        '''
        table = (
            (1, 'class emptyClass'),
            (2, 'spam'),
            (1, 'followingDef'),
        )
        p = c.p
        self.run_test(s)
        if self.check_tree:
            after = p.nodeAfterTree()
            root = p.lastChild()
            self.assertEqual(root.h, f"@file {self.id()}")
            p = root.firstChild()
            for n, h in table:
                n2 = p.level() - root.level()
                self.assertEqual(h, p.h)
                self.assertEqual(n, n2)
                p.moveToThreadNext()
            self.assertEqual(p, after)
    #@+node:ekr.20210904065459.101: *4* TestPython.test_unindent_in_triple_string_does_not_end_function
    def test_unindent_in_triple_string_does_not_end_function(self):
        c = self.c
        s = '''
            def foo():

                error("""line1
            line2.
            """)

                a = 5

            def bar():
                pass
        '''
        p = c.p
        self.run_test(s)
        if self.check_tree:
            child = p.firstChild()
            n = child.numberOfChildren()
            self.assertEqual(n, 2)
    #@+node:ekr.20211114184047.1: *4* TestPython.test_data_docstring
    def test_data_docstring(self):
        # From mypy\test-data\stdlib-samples\3.2\test\test_pprint.py
        s = '''
            def test_basic_line_wrap(self) -> None:
                # verify basic line-wrapping operation
                o = {'RPM_cal': 0,
                     'RPM_cal2': 48059,
                     'Speed_cal': 0,
                     'controldesk_runtime_us': 0,
                     'main_code_runtime_us': 0,
                     'read_io_runtime_us': 0,
                     'write_io_runtime_us': 43690}
                exp = """\\
        {'RPM_cal': 0,
         'RPM_cal2': 48059,
         'Speed_cal': 0,
         'controldesk_runtime_us': 0,
         'main_code_runtime_us': 0,
         'read_io_runtime_us': 0,
         'write_io_runtime_us': 43690}"""
        '''
        self.run_test(s)
    #@+node:ekr.20211114185222.1: *4* TestPython.test_data_docstring_2
    def test_data_docstring_2(self):
        # From mypy\test-data\stdlib-samples\3.2\test\test_textwrap.py
        s = """
            class IndentTestCases(BaseTestCase):  # Line 443
            
                def test_subsequent_indent(self) -> None:
                    # Test subsequent_indent parameter
            
                    expect = '''\\
              * This paragraph will be filled, first
                without any indentation, and then
                with some (including a hanging
                indent).'''
            
                    result = fill(self.text, 40,
                                  initial_indent="  * ", subsequent_indent="    ")
                    self.check(result, expect)
                    
            # Despite the similar names, DedentTestCase is *not* the inverse
            # of IndentTestCase!
            class DedentTestCase(unittest.TestCase):  # Line 494.
                pass
        """
        self.run_test(s)
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
        self.run_test(s)
        root = c.p.lastChild()
        self.assertEqual(root.h, f"@auto-rst {self.id()}")
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

        s = """
            .. toc

            .. The section name contains trailing whitespace.

            =======
            Chapter
            =======

            The top chapter.
        """
        table = (
            "!Dummy chapter",
            "Chapter",
        )
        self.run_test(s)
        root = c.p.lastChild()
        self.assertEqual(root.h, f"@auto-rst {self.id()}")
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
        self.run_test(s)
        root = c.p.lastChild()
        self.assertEqual(root.h, f"@auto-rst {self.id()}")
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

        s = """
            .. toc

            top
            -------------

            The top section
        """
        table = (
            '!Dummy chapter',
            'top',
        )
        self.run_test(s)
        root = c.p.lastChild()
        self.assertEqual(root.h, f"@auto-rst {self.id()}")
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

        s = """
            .. toc

            ======
            top
            ======

            The top section
        """
        table = (
            "!Dummy chapter",
            "top",
        )
        self.run_test(s)
        root = c.p.lastChild()
        self.assertEqual(root.h, f"@auto-rst {self.id()}")
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

        s = """
            .. toc

            .. The section name contains trailing whitespace.

            ======
            top
            ======

            The top section.
        """
        table = (
            "!Dummy chapter",
            "top",
        )
        p = c.p
        self.run_test(s)
        root = p.lastChild()
        self.assertEqual(root.h, f"@auto-rst {self.id()}")
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
        table = (
            'Chapter 1',
            'section 1',
            'section 2',
        )
        self.run_test(s)
        root = c.p.lastChild()
        self.assertEqual(root.h, f"@auto-rst {self.id()}")
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
        self.assertEqual(root.h, f"@file {self.id()}")
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
        table = (
            (1, "<html>"),
            (2, "<head>"),
            (2, "<body class='bodystring'>"),
        )
        p = c.p
        self.run_test(s)
        after = p.nodeAfterTree()
        root = p.lastChild()
        self.assertEqual(root.h, f"@file {self.id()}")
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

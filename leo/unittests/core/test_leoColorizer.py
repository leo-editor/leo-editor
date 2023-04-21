#@+leo-ver=5-thin
#@+node:ekr.20210905151702.1: * @file ../unittests/core/test_leoColorizer.py
"""Tests of leoColorizer.py"""

import textwrap
from leo.core import leoGlobals as g
from leo.core.leoTest2 import LeoUnitTest
import leo.core.leoColorizer as leoColorizer

#@+others
#@+node:ekr.20210905151702.2: ** class TestColorizer(LeoUnitTest)
class TestColorizer(LeoUnitTest):
    """Test cases for leoColorizer.py"""
    #@+others
    #@+node:ekr.20210905161336.1: *3* TestColorizer.color
    def color(self, language_name, text):
        """Run the test by colorizing a node with the given text."""
        c = self.c
        c.p.b = text.replace('> >', '>>').replace('< <', '<<')
        c.recolor_now()
    #@+node:ekr.20210905170507.2: *3* TestColorizer.test__comment_after_language_plain
    def test__comment_after_language_plain(self):
        text = textwrap.dedent("""\
            @comment # /* */

            This is plain text.

            # This is a comment.

            More plain text.

            /* A block comment
            continues */

            More plain text.
        """)
        self.color('plain', text)
    #@+node:ekr.20210905170507.3: *3* TestColorizer.test_bc_scanLanguageDirectives
    def test_bc_scanLanguageDirectives(self):
        c = self.c
        c.target_language = 'python'  # Set the default.
        widget = c.frame.body.widget
        x = leoColorizer.JEditColorizer(c, widget)
        child = c.rootPosition().insertAsLastChild()
        grand = child.insertAsLastChild()
        language_table = (
            ('python', '@language rest\n@language python\n', ''),
            ('rest', '@language rest', ''),
            ('python', '@language rest\n@language python\n', ''),
        )
        for i, data in enumerate(language_table):
            language, child_s, grand_s = data
            child.b = child_s
            grand.b = grand_s
            got = x.scanLanguageDirectives(grand)
            self.assertEqual(got, language, msg=f"i: {i} {language}")
    #@+node:ekr.20210905170507.4: *3* TestColorizer.test_bc_useSyntaxColoring
    def test_bc_useSyntaxColoring(self):
        c = self.c
        widget = c.frame.body.widget
        x = leoColorizer.JEditColorizer(c, widget)
        child = c.rootPosition().insertAsLastChild()
        grand = child.insertAsLastChild()
        language_table = [
            (True, '', ''),
            # Ambiguous parent.
            (True, '@color \n@nocolor\n', ''),
            (True, '@nocolor \n@color\n', ''),
            # Unambiguous parent.
            (True, '@nocolor-node', ''),  # Does not apply to descendants.
            (False, '@nocolor', ''),
            (False, '@killcolor', ''),
            #
            # Note: the following tests don't matter because
            # jedit.recolor ignores the self.enabled flag.
            # As a result, *all* color directives, including @nocolor-node,
            # Apply from the directive to the next color directive.
            #
            # Unambiguous child.
            (False, '', '@killcolor\n'),
            (True, '', '@color\n'),
            #@verbatim
            # @nocolor-node rules node.
            (False, '', '@nocolor-node\n'),
            (False, '', '@color\n@nocolor-node\n'),
            # Ambiguous node: defer to ancestors.
            (True, '', '@color\n@nocolor'),
            (True, '', '@nocolor\n@color'),
        ]
        language = 'python'
        for i, data in enumerate(language_table):
            expected, child_s, grand_s = data
            child.b = child_s
            grand.b = grand_s
            got = x.useSyntaxColoring(grand)
            self.assertEqual(got, expected, msg=f"i: {i} {language}")
    #@+node:ekr.20210905170507.5: *3* TestColorizer.test_colorizer_Actionscript
    def test_colorizer_Actionscript(self):
        text = textwrap.dedent("""\
            break
            call, continue
            delete, do
            else
            false, for, function
            goto
            if, in
            new, null
            return
            true, typeof
            undefined
            var, void, while, with
            #include
            catch, constructor
            prototype
            this, try
            _parent, _root, __proto__
            // Jeeze hasn't anyone ever heard of namespaces??
            ASnative, abs, acos, appendChild, asfunction, asin, atan, atan2, attachMovie, attachSound, attributes
            BACKSPACE
            CAPSLOCK, CONTROL, ceil, charAt, charCodeAt, childNodes, chr, cloneNode, close, concat, connect, cos, createElement, createTextNode
            DELETEKEY, DOWN, docTypeDecl, duplicateMovieClip
            END, ENTER, ESCAPE, enterFrame, entry, equal, eval, evaluate, exp
            firstChild, floor, fromCharCode, fscommand, getAscii
            getBeginIndex, getBounds, getBytesLoaded, getBytesTotal, getCaretIndex, getCode, getDate, getDay, getEndIndex, getFocus, getFullYear, getHours, getMilliseconds, getMinutes, getMonth, getPan, getProperty, getRGB, getSeconds, getTime, getTimer, getTimezoneOffset, getTransform, getURL, getUTCDate, getUTCDay, getUTCFullYear, getUTCHours, getUTCMilliseconds, getUTCMinutes, getUTCMonth, getUTCSeconds, getVersion, getVolume, getYear, globalToLocal, gotoAndPlay, gotoAndStop
            HOME, haschildNodes, hide, hitTest
            INSERT, Infinity, ifFrameLoaded, ignoreWhite, indexOf, insertBefore, int, isDown, isFinite, isNaN, isToggled
            join
            keycode, keyDown, keyUp
            LEFT, LN10, LN2, LOG10E, LOG2E, lastChild, lastIndexOf, length, load, loaded, loadMovie, loadMovieNum, loadVariables, loadVariablesNum, localToGlobal, log
            MAX_VALUE, MIN_VALUE, max, maxscroll, mbchr, mblength, mbord, mbsubstring, min,
            NEGATIVE_INFINITY, NaN, newline, nextFrame, nextScene, nextSibling, nodeName, nodeType, nodeValue
            on, onClipEvent, onClose, onConnect, onData, onLoad, onXML, ord
            PGDN, PGUP, PI, POSITIVE_INFINITY, parentNode, parseFloat, parseInt, parseXML, play, pop, pow, press, prevFrame, previousSibling, prevScene, print, printAsBitmap, printAsBitmapNum, printNum, push
            RIGHT, random, release, removeMovieClip, removeNode, reverse, round
            SPACE, SQRT1_2, SQRT2, scroll, send, sendAndLoad, set, setDate, setFocus, setFullYear, setHours, setMilliseconds, setMinutes, setMonth, setPan, setProperty, setRGB, setSeconds, setSelection, setTime, setTransform, setUTCDate, setUTCFullYear, setUTCHours, setUTCMilliseconds, setUTCMinutes, setUTCMonth, setUTCSeconds, setVolume, setYear, shift, show, sin, slice, sort, start, startDrag, status, stop, stopAllSounds, stopDrag, substr, substring, swapDepths, splice, split, sqrt
            TAB, tan, targetPath, tellTarget, toggleHighQuality, toLowerCase, toString, toUpperCase, trace
            UP, UTC, unescape, unloadMovie, unLoadMovieNum, unshift, updateAfterEvent
            valueOf
            xmlDecl, _alpha
            _currentframe
            _droptarget
            _focusrect, _framesloaded
            _height, _highquality
            _name
            _quality
            _rotation
            _soundbuftime
            _target, _totalframes
            _url
            _visible
            _width
            _x, _xmouse, _xscale
            _y, _ymouse, _yscale
            and, add, eq, ge, gt, le, lt, ne, not, or, Array, Boolean, Color, Date, Key, Math, MovieClip, Mouse, Number, Object, Selection, Sound, String, XML, XMLSocket
    """)
        self.color('actionscript', text)
    #@+node:ekr.20210905170507.6: *3* TestColorizer.test_colorizer_C
    def test_colorizer_C(self):
        text = textwrap.dedent("""\
            @comment /* */

            @
            @c

            #define WIPEOUT 0 /*
                               * Causes database card number & flags to be set to zero.
                               * This is so I don't need an infinite supply of cards!
                               */
            // Not colored (because of @language /* */)
            #include "equ.h"
            #include "cmn.h"
            #include "ramdef.h"
            #include "eeprom.h"
            #include <hpc_ram.h>
            #include <rlydef.h>
    """)
        self.color('c', text)
    #@+node:ekr.20210905170507.7: *3* TestColorizer.test_colorizer_C_
    def test_colorizer_C_(self):
        text = textwrap.dedent("""\
            @ comment
            @c

            /* block
            comment */

            // test

            id // not a keyword

            abstract as
            base bool break byte
            case catch char checked class const continue
            decimal default delegate do double
            else enum event explicit extern
            false finally fixed float for foreach
            get goto
            if implicit in int interface internal is
            lock long
            namespace new null
            object operator out override
            params partial private protected public
            readonly ref return
            sbyte sealed set short sizeof stackalloc
            static string struct switch
            this throw true try typeof
            uint ulong unchecked unsafe ushort using
            value virtual void volatile
            where while
            yield
    """)
        self.color('csharp', text)
    #@+node:ekr.20210905170507.8: *3* TestColorizer.test_colorizer_css
    def test_colorizer_css(self):
        text = textwrap.dedent("""\
            /* New in 4.2. */

            /*html tags*/
            address, applet, area, a, base, basefont,
            big, blockquote, body, br, b, caption, center,
            cite, code, dd, dfn, dir, div, dl, dt, em, font,
            form, h1, h2, h3, h4, h5, h6, head, hr, html, img,
            input, isindex, i, kbd, link, li, link, map, menu,
            meta, ol, option, param, pre, p, samp,
            select, small, span, strike, strong, style, sub, sup,
            table, td, textarea, th, title, tr, tt, ul, u, var,
            /*units*/
            mm, cm, in, pt, pc, em, ex, px,
            /*colors*/
            aqua, black, blue, fuchsia, gray, green, lime, maroon, navy, olive, purple, red, silver, teal, yellow, white,
            /*important directive*/
            !important,
            /*font rules*/
            font, font-family, font-style, font-variant, font-weight, font-size,
            /*font values*/
            cursive, fantasy, monospace, normal, italic, oblique, small-caps,
            bold, bolder, lighter, medium, larger, smaller,
            serif, sans-serif,
            /*background rules*/
            background, background-color, background-image, background-repeat, background-attachment, background-position,
            /*background values*/
            contained, none, top, center, bottom, left, right, scroll, fixed,
            repeat, repeat-x, repeat-y, no-repeat,
            /*text rules*/
            word-spacing, letter-spacing, text-decoration, vertical-align, text-transform, text-align, text-indent, text-transform, text-shadow, unicode-bidi, line-height,
            /*text values*/
            normal, none, underline, overline, blink, sub, super, middle, top, text-top, text-bottom,
            capitalize, uppercase, lowercase, none, left, right, center, justify,
            line-through,
            /*box rules*/
            margin, margin-top, margin-bottom, margin-left, margin-right,
            margin, padding-top, padding-bottom, padding-left, padding-right,
            border, border-width, border-style, border-top, border-top-width, border-top-style, border-bottom, border-bottom-width, border-bottom-style, border-left, border-left-width, border-left-style, border-right, border-right-width, border-right-style, border-color,
            /*box values*/
            width, height, float, clear,
            auto, thin, medium, thick, left, right, none, both,
            none, dotted, dashed, solid, double, groove, ridge, inset, outset,
            /*display rules*/
            display, white-space,
            min-width, max-width, min-height, max-height,
            outline-color, outline-style, outline-width,
            /*display values*/
            run-in, inline-block, list-item, block, inline, none, normal, pre, nowrap, table-cell, table-row, table-row-group, table-header-group, inline-table, table-column, table-column-group, table-cell, table-caption
            /*list rules*/
            list-style, list-style-type, list-style-image, list-style-position,
            /*list values*/
            disc, circle, square, decimal, decimal-leading-zero, none,
            lower-roman, upper-roman, lower-alpha, upper-alpha, lower-latin, upper-latin,
            /*table rules*/
            border-collapse, caption-side,
            /*table-values*/
            empty-cells, table-layout,
            /*misc values/rules*/
            counter-increment, counter-reset,
            marker-offset, z-index,
            cursor, direction, marks, quotes,
            clip, content, orphans, overflow, visibility,
            /*aural rules*/
            pitch, range, pitch-during, cue-after, pause-after, cue-before, pause-before, speak-header, speak-numeral, speak-punctuation, speed-rate, play-during, voice-family,
            /*aural values*/
            stress, azimuth, elevation, pitch, richness, volume,
            page-break, page-after, page-inside
    """)
        self.color('css', text)
    #@+node:ekr.20210905170507.9: *3* TestColorizer.test_colorizer_CWEB
    def test_colorizer_CWEB(self):
        text = textwrap.dedent(r"""\\\
            % This is limbo in cweb mode... It should be in \LaTeX mode, not \c mode.
            % The following should not be colorized: class,if,else.

            @* this is a _cweb_ comment.  Code is written in \c.
            "strings" should not be colorized.
            It should be colored in \LaTeX mode.
            The following are not keywords in latex mode: if, else, etc.
            Noweb section references are _valid_ in cweb comments!
            < < section ref > >
            < < missing ref > >
            @c

            and this is C code. // It is colored in \LaTeX mode by default.
            /* This is a C block comment.  It may also be colored in restricted \LaTeX mode. */

            // Section refs are valid in code too, of course.
            < < section ref > >
            < < missing ref > >

            \LaTeX and \c should not be colored.
            if else, while, do // C keywords.
    """)
        self.color('cweb', text)
    #@+node:ekr.20210905170507.10: *3* TestColorizer.test_colorizer_cython
    def test_colorizer_cython(self):
        text = textwrap.dedent("""\
            by cdef cimport cpdef ctypedef enum except?
            extern gil include nogil property public
            readonly struct union DEF IF ELIF ELSE

            NULL bint char dict double float int list
            long object Py_ssize_t short size_t void

            try:
                pass
            except Exception:
                pass
    """)
        self.color('cython', text)
    #@+node:ekr.20210905170507.11: *3* TestColorizer.test_colorizer_elisp
    def test_colorizer_elisp(self):
        text = textwrap.dedent("""\
            ; Maybe...
            error princ

            ; More typical of other lisps...
            and apply
            car cdr cons cond
            defconst defun defvar
            eq equal eval
            gt ge
            if
            let le lt
            mapcar
            ne nil
            or not
            prog progn
            set setq
            t type-of
            unless
            when while
    """)
        self.color('elisp', text)
    #@+node:ekr.20210905170507.12: *3* TestColorizer.test_colorizer_erlang
    def test_colorizer_erlang(self):
        text = textwrap.dedent("""\
            halt()

            -module()
    """)
        self.color('erlang', text)
    #@+node:ekr.20210905170507.13: *3* TestColorizer.test_colorizer_forth
    def test_colorizer_forth(self):
        text = textwrap.dedent(r"""\\\
            \ tiny demo of Leo forth syntax colouring

            : some-forth-word ( x1 x2 -- x3 ) \ blue :, black/bold some-forth-word
               label: y  \ blue label:
               asm[ s" some string" type ]asm cr
               asm[ abc ]asm
               a
               s" abc "
               s" abc"
               a
               tty" abc "
               lcd2" abc "
               until

            @ test
            @c

            { abc }

            a b @ c

            asm[ abc ]asm

            .( ab ) \ a string

            : foo [ .s ] ;

               [ a b c
               x y z]
            ;
    """)
        self.color('forth', text)
    #@+node:ekr.20210905170507.14: *3* TestColorizer.test_colorizer_HTML_string_bug
    def test_colorizer_HTML_string_bug(self):
        text = textwrap.dedent("""\
            b = "cd"
            d
    """)
        self.color('html', text)
    #@+node:ekr.20210905170507.15: *3* TestColorizer.test_colorizer_HTML1
    def test_colorizer_HTML1(self):
        text = textwrap.dedent("""\
            <HTML>
            <!-- Author: Edward K. Ream, edream@tds.net -->
            <HEAD>
              <META NAME="GENERATOR" CONTENT="Microsoft FrontPage 4.0">
              <TITLE> Leo's Home Page </TITLE>
              <META NAME="description" CONTENT="This page describes Leo.
            Leo adds powerful outlines to the noweb and CWEB literate programming languages.">
              <META NAME="keywords" CONTENT="LEO, LITERATE PROGRAMMING, OUTLINES, CWEB,
            NOWEB, OUTLINES, EDWARD K. REAM, DONALD E. KNUTH, SILVIO LEVY, OPEN SOFTWARE">
            </HEAD>
            <!-- Last Modified: May 12, 2002 -->
            <BODY BGCOLOR="#fffbdc">

            <H1 ALIGN=CENTER><a NAME="top"></a><IMG SRC="Blank.gif" width=
            "32" height="32" ALIGN="BOTTOM" NATURALSIZEFLAG="3"><IMG SRC="leo.gif"
            WIDTH="32" HEIGHT="32" ALIGN="BOTTOM" NATURALSIZEFLAG="3"><a href="leo_TOC.html#top"><IMG SRC=
            "arrow_rt.gif" WIDTH="32" HEIGHT="32" ALIGN="BOTTOM" NATURALSIZEFLAG="3"></a> &nbsp;</H1>

            <H1 ALIGN=CENTER> Leo's Home Page</H1>

            <p align="center"><a href="http://www.python.org/"><img border="0" src="PythonPowered.gif" width="110" height="44"> </a> <A HREF="http://sourceforge.net/"><IMG SRC="http://sourceforge.net/sflogo.php?group_id=3458&type=1" NATURALSIZEFLAG="0" ALT="SourceForge Logo"></A>&nbsp;&nbsp;&nbsp;
            <A HREF="http://sourceforge.net/project/?group_id=3458">Leo at SourceForge</A>&nbsp;&nbsp;
            <a href="icons.html"><img border="0" src="LeoCodeGray.gif" width="77" height="42"></a>&nbsp;&nbsp;
            <a href="icons.html"><img border="0" src="LeoProse.gif" width="81" height="42"></a>&nbsp;&nbsp;&nbsp;&nbsp;

            <H3><A NAME="anchor127554"></A>Summary</H3>

            <UL>
              <LI>Leo is a <i> programmer's editor</i>  and a flexible <i>browser</i> for
                projects, programs, classes or data. Leo clarifies design, coding, debugging, testing
              and maintenance.
              <LI>Leo is an <i>outlining editor</i>. Outlines clarify the big picture while
                providing unlimited space for details.
              <LI>Leo
                is a <a HREF="http://www.literateprogramming.com/"><i>literate
                programming</i></a> tool, compatible with <A HREF="http://www.eecs.harvard.edu/~nr/noweb/">noweb</A>
                and <a HREF="http://www-cs-faculty.stanford.edu/~knuth/cweb.html">CWEB</a>.
                Leo enhances any text-based
            programming language, from assembly language and C to Java, Python and XML.
              <LI>Leo is also a <i>data organizer</i>. A single Leo outline can generate complex
                data spanning many different files.&nbsp; Leo has been used to manage web sites.
              <LI>Leo is a <i> project manager</i>. Leo provides multiple views
            of a project within a single outline. Leo naturally represents tasks that remain
                up-to-date.
              <LI>Leo is fully <i> scriptable</i> using <A HREF="http://www.python.org/">Python</A>
              and saves its files in <A HREF="http://www.w3.org/XML/">XML</A> format.
              <LI>Leo is <i>portable</i>.&nbsp; Leo.py is 100% pure Python and will run on
                any platform supporting <A HREF="http://www.python.org/">Python</A>
                and <a href="http://tcl.activestate.com/">Tk/tcl</a>, including Windows,
                Linux and MacOS X.&nbsp; Leo.exe runs on any Windows platform.
              <LI>Leo is <a href="http://www.opensource.org/"> <i> Open Software</i></a>, distributed under
                the <a href="http://www.python.org/doc/Copyright.html"> Python License</a>.
            </UL>

            <H3>More Information and downloads</H3>

            <ul>
              <LI>An excellent <a href="http://www.3dtree.com/ev/e/sbooks/leo/sbframetoc_ie.htm">online
                tutorial</a> and <A HREF="http://www.jserv.com/jk_orr/xml/leo.htm">Leo resource
              page</A>, both written by <a href="http://www.jserv.com/jk_orr">Joe Orr</a>.
              <LI>My brother's <a href="SpeedReam.html">slashdot
                article about Leo</a>, the best description about why Leo is special.
              <LI><A HREF="testimonials.html#anchor104391">What people are saying about Leo</A>
              <LI><A HREF="leo_TOC.html#anchor964914">Complete users guide</A>
                and
                <A HREF="intro.html#anchor887874">tutorial introduction</A>  with
              screen shots.
              <li><a href="FAQ.html">FAQ</a> and <a href="http://sourceforge.net/forum/?group_id=3458">help and discussion
                forums</a>, preferable to <A HREF="mailto:edream@tds.net">email</A> so others may join
                in.</li>
              <li><a href="icons.html">Icons</a> for bragging about Leo.</li>
            </ul>

            <a href="http://sourceforge.net/project/showfiles.php?group_id=3458">Download
                Leo</a> from <A HREF="http://sourceforge.net/project/?group_id=3458">Leo's SourceForge
            site</A>.

            <P ALIGN=left>Leo's author is <A HREF="http://personalpages.tds.net/~edream/index.html">Edward
              K. Ream</A> email: <A HREF="mailto:edream@tds.net">edream@tds.net</A> voice: (608) 231-0766

            <HR ALIGN=LEFT>

            <p align="center">

            <IMG SRC="Blank.gif" ALIGN="left" NATURALSIZEFLAG=
            "3" width="34" height="34"><IMG SRC="leo.gif" ALIGN="left" NATURALSIZEFLAG=
            "3" width="32" height="32"><a HREF="leo_TOC.html"><IMG SRC="arrow_rt.gif" WIDTH="32"
            HEIGHT="32" ALIGN="left" NATURALSIZEFLAG="3">

            </BODY>
            </HTML>
    """)
        self.color('html', text)
    #@+node:ekr.20210905170507.16: *3* TestColorizer.test_colorizer_HTML2
    def test_colorizer_HTML2(self):
        text = textwrap.dedent("""\
            <? xml version="1.0">
            <!-- test -->
            <project name="Converter" default="dist">
            </project>
    """)
        self.color('html', text)
    #@+node:ekr.20230421104052.1: *3* TestColorizer.test_colorizer_HTML_script_tag
    def test_colorizer_HTML_script_tag(self):
        text = textwrap.dedent("""\
            <html>
            <head>
            <script>
            // js comment
            for (let i = 0; i < cars.length; i++) {
              text += cars[i] + "<br>";
            }
            </script>
            </head>
            <body>
            <p1>
            <-- html comment -->
            This is a test.
            </body>
            </html>
    """)
        self.color('html', text)
    #@+node:ekr.20210905170507.17: *3* TestColorizer.test_colorizer_Java
    def test_colorizer_Java(self):
        text = textwrap.dedent('''\
            @ doc part
            @c

            @language java /* Colored by match_leo_keyword: tag = leoKeyword. */

            @whatever /* Colored by java match_following rule: tag = keyword4. */

            /** A javadoc: tag = comment3 */

            /** <!-- comment --> tag = comment1. */

            /** @see tag = label */
    ''')
        self.color('java', text)
    #@+node:ekr.20210905170507.18: *3* TestColorizer.test_colorizer_LaTex
    def test_colorizer_LaTex(self):
        text = textwrap.dedent(r"""\\\
            % This is a \LaTeX mode comment.

            This is a test of \LaTeX mode.

            @ blah blah blah
            @c

            \c and \LaTeX are latex keywords.

            This is a keyword \% not the start of a comment.

            More keywords: \@ and \( and \) and \{ and \}

            The following should be colored:

            \documentclass{report}

            The following 2-letter words should be colored, regardless of what follows:

            \(\)\{\}\@
            \(abc\)abc\{abc\}abc\@abc
    """)
        self.color('latex', text)
    #@+node:ekr.20210905170507.19: *3* TestColorizer.test_colorizer_lisp
    def test_colorizer_lisp(self):
        text = textwrap.dedent("""\
            ; Maybe...
            error princ

            ; More typical of other lisps...
            and apply
            car cdr cons cond
            defconst defun defvar
            eq equal eval
            gt ge
            if
            let le lt
            mapcar
            ne nil
            or not
            prog progn
            set setq
            t type-of
            unless
            when while
    """)
        self.color('lisp', text)
    #@+node:ekr.20210905170507.20: *3* TestColorizer.test_colorizer_objective_c
    def test_colorizer_objective_c(self):
        text = textwrap.dedent("""\
            @interface Application
                -(void) init;
                -(void) showMessage;
            @end

            @implementation Application
                -(id) init {
                    if (self = [super init]) {
                        NSLog(@"Init ok");
                        return self;
                    }
                    return nil;
                }
                -(void) showMessage {
                    NSLog(@"Hello there");
                }
            @end

            @"Hello there"

            ,@interface
            , @interface
            the @interface

            // By the way, I have noticed that such kind of words in doxygen block
            // are highlighted properly, but they are labels here, not keywords1 as in my case.
            /**
            @var test
            @todo
            */
    """)
        self.color('objective_c', text)
    #@+node:ekr.20210905170507.21: *3* TestColorizer.test_colorizer_perl
    def test_colorizer_perl(self):
        text = textwrap.dedent("""\
            # From a perl tutorial.

            print 'Hello world.';               # Print a message

            $a = $b;    # Assign $b to $a

            @food  = ("apples", "pears", "eels");

            $grub = pop(@food); # Now $grub = "eels"

            $#food

            @lines = <INFO>;

            #!/usr/local/bin/perl
            print "Password? ";         # Ask for input
            $a = <STDIN>;                       # Get input
            chop $a;                    # Remove the newline at end
            while ($a ne "fred")                # While input is wrong...
            {
                print "sorry. Again? "; # Ask again
                $a = <STDIN>;           # Get input again
                chop $a;                        # Chop off newline again
            }

            if ($sentence =~ /under/)
            {
                print "We're talking about rugby\\n";
            }

            $sentence =~ s/london/London/

            $_ = "Capes:Geoff::Shot putter:::Big Avenue";
            @personal = split(/:/);

            foreach $age (values %ages)
            {
                print "Somebody is $age\\n";
            }

            &mysubroutine;              # Call the subroutine
            &mysubroutine($_);  # Call it with a parameter
            &mysubroutine(1+2, $_);     # Call it with two parameters

            sub inside
            {
                local($a, $b);                  # Make local variables
                ($a, $b) = ($_[0], $_[1]);      # Assign values
                $a =~ s/ //g;                   # Strip spaces from
                $b =~ s/ //g;                   #   local variables
                ($a =~ /$b/ || $b =~ /$a/);     # Is $b inside $a
                                #   or $a inside $b?
            }
    """)
        self.color('perl', text)
    #@+node:ekr.20210905170507.22: *3* TestColorizer.test_colorizer_PHP
    def test_colorizer_PHP(self):
        text = textwrap.dedent("""\
            @ doc
            This is a doc part.
            @c

            and or
            array
            array()
            /* Multi-line comment
            */
            this is a test.
            __CLASS__
            <?php and or array() ?>
            <?PHP and or array() ?>
    """)
        self.color('php', text)
    #@+node:ekr.20210905170507.23: *3* TestColorizer.test_colorizer_plsql
    def test_colorizer_plsql(self):
        text = textwrap.dedent("""\
            "a string"
            -- reserved keywords
            ABORT,
            abort,
            ACceSS,
            access,
            add,
            all,
            allocate,
            alter,
            analyze,
            and,
            any,
            archive,
            archivelog,
            array,
            arraylen,
            as,
            asc,
            assert,
            assign,
            at,
            audit,
            authorization,
            avg,
            backup,
            base_table,
            become,
            before,
            begin,
            between,
            binary_integer,
            block,
            body,
            boolean,
            by,
            cache,
            cancel,
            cascade,
            case,
            change,
            char,
            char_base,
            character,
            check,
            checkpoint,
            close,
            cluster,
            clusters,
            cobol,
            colauth,
            column,
            columns,
            comment,
            commit,
            compile,
            compress,
            connect,
            constant,
            constraint,
            constraints,
            contents,
            continue,
            controlfile,
            count,
            crash,
            create,
            current,
            currval,
            cursor,
            cycle,
            data_base,
            database,
            datafile,
            date,
            dba,
            debugoff,
            debugon,
            dec,
            decimal,
            declare,
            default,
            definition,
            delay,
            delete,
            delta,
            desc,
            digits,
            disable,
            dismount,
            dispose,
            distinct,
            distinct,
            do,
            double,
            drop,
            drop,
            dump,
            each,
            else,
            else,
            elsif,
            enable,
            end,
            end,
            entry,
            escape,
            events,
            except,
            exception,
            exception_init,
            exceptions,
            exclusive,
            exec,
            execute,
            exists,
            exists,
            exit,
            explain,
            extent,
            externally,
            false,
            fetch,
            fetch,
            file,
            float,
            float,
            flush,
            for,
            for,
            force,
            foreign,
            form,
            fortran,
            found,
            freelist,
            freelists,
            from,
            from,
            function,
            generic,
            go,
            goto,
            grant,
            group,
            groups,
            having,
            identified,
            if,
            immediate,
            in,
            including,
            increment,
            index,
            indexes,
            indicator,
            initial,
            initrans,
            insert,
            instance,
            int,
            integer,
            intersect,
            into,
            is,
            key,
            language,
            layer,
            level,
            like,
            limited,
            link,
            lists,
            lock,
            logfile,
            long,
            loop,
            manage,
            manual,
            max,
            maxdatafiles,
            maxextents,
            maxinstances,
            maxlogfiles,
            maxloghistory,
            maxlogmembers,
            maxtrans,
            maxvalue,
            min,
            minextents,
            minus,
            minvalue,
            mlslabel,
            mod,
            mode,
            modify,
            module,
            mount,
            natural,
            new,
            new,
            next,
            nextval,
            noarchivelog,
            noaudit,
            nocache,
            nocompress,
            nocycle,
            nomaxvalue,
            nominvalue,
            none,
            noorder,
            noresetlogs,
            normal,
            nosort,
            not,
            notfound,
            nowait,
            null,
            number,
            number_base,
            numeric,
            of,
            off,
            offline,
            old,
            on,
            online,
            only,
            open,
            open,
            optimal,
            option,
            or,
            order,
            others,
            out,
            own,
            package,
            package,
            parallel,
            partition,
            pctfree,
            pctincrease,
            pctused,
            plan,
            pli,
            positive,
            pragma,
            precision,
            primary,
            prior,
            private,
            private,
            privileges,
            procedure,
            procedure,
            profile,
            public,
            quota,
            raise,
            range,
            raw,
            read,
            real,
            record,
            recover,
            references,
            referencing,
            release,
            remr,
            rename,
            resetlogs,
            resource,
            restricted,
            return,
            reuse,
            reverse,
            revoke,
            role,
            roles,
            rollback,
            row,
            rowid,
            rowlabel,
            rownum,
            rows,
            rowtype,
            run,
            savepoint,
            schema,
            scn,
            section,
            segment,
            select,
            select,
            separate,
            sequence,
            session,
            set,
            set,
            share,
            shared,
            size,
            size,
            smallint,
            smallint,
            snapshot,
            some,
            sort,
            space,
            sql,
            sqlbuf,
            sqlcode,
            sqlerrm,
            sqlerror,
            sqlstate,
            start,
            start,
            statement,
            statement_id,
            statistics,
            stddev,
            stop,
            storage,
            subtype,
            successful,
            sum,
            sum,
            switch,
            synonym,
            sysdate,
            system,
            tabauth,
            table,
            tables,
            tables,
            tablespace,
            task,
            temporary,
            terminate,
            then,
            thread,
            time,
            to,
            tracing,
            transaction,
            trigger,
            triggers,
            true,
            truncate,
            type,
            uid,
            under,
            union,
            unique,
            unlimited,
            until,
            update,
            use,
            user,
            using,
            validate,
            values,
            varchar,
            varchar2,
            variance,
            view,
            views,
            when,
            whenever,
            where,
            while,
            with,
            work,
            write,
            xor
    """)
        self.color('plsql', text)
    #@+node:ekr.20210905170507.24: *3* TestColorizer.test_colorizer_python_xml_jEdit_
    def test_colorizer_python_xml_jEdit_(self):
        text = textwrap.dedent(r"""\\\
            <?xml version="1.0"?>

            <!DOCTYPE MODE SYSTEM "xmode.dtd">
            < < remarks > >

            <MODE>
                <PROPS>
                    <PROPERTY NAME="indentPrevLine" VALUE="\s*.{3,}:\s*(#.*)?" />
                    <PROPERTY NAME="lineComment" VALUE="#" />
                </PROPS>
                <RULES ESCAPE="\" IGNORE_CASE="FALSE" HIGHLIGHT_DIGITS="TRUE">
                    < < comments > >
                    < < literals > >
                    < < operators > >
                    <MARK_PREVIOUS TYPE="FUNCTION" EXCLUDE_MATCH="TRUE">(</MARK_PREVIOUS>
                    < < keywords > >
                </RULES>
            </MODE>
    """)
        self.color('html', text)
    #@+node:ekr.20210905170507.25: *3* TestColorizer.test_colorizer_Python1
    def test_colorizer_Python1(self):
        text = textwrap.dedent("""\
            int
            float
            dict
    """)
        self.color('python', text)
    #@+node:ekr.20210905170507.26: *3* TestColorizer.test_colorizer_Python2
    def test_colorizer_Python2(self):

        text = textwrap.dedent('''\
            """This creates a free-floating copy of v's tree for undo.
            The copied trees must use different vnodes than the original."""

            def copyTree(self,root):
                c = self
                # Create the root VNode.
                result = v = leoNodes.VNode(c)
                # Copy the headline and icon values v.copyNode(root,v)
                # Copy the rest of tree.
                v.copyTree(root,v)
                # Replace all vnodes in v by copies.
                assert(v.nodeAfterTree() == None)
                while v:
                    v = leoNodes.VNode(c)
                    v = v.threadNext()
                return result
    ''')
        self.color('python', text)

    #@+node:ekr.20210905170507.27: *3* TestColorizer.test_colorizer_r
    def test_colorizer_r(self):
        text = textwrap.dedent("""\
            x <- rnorm(10)

            vv <- function(z) return(z)

            def python_funct(uu):
            return uu
    """)
        self.color('r', text)
    #@+node:ekr.20210905170507.28: *3* TestColorizer.test_colorizer_rapidq
    def test_colorizer_rapidq(self):
        text = textwrap.dedent("""\
            ' New in 4.2.
            ' a comment.

            $APPTYPE,$DEFINE,$ELSE,$ENDIF,$ESCAPECHARS,$IFDEF,$IFNDEF,
            $INCLUDE,$MACRO,$OPTIMIZE,$OPTION,$RESOURCE,$TYPECHECK,$UNDEF,
            ABS,ACOS,ALIAS,AND,AS,ASC,ASIN,ATAN,ATN,BIN$,BIND,BYTE,
            CALL,CALLBACK,CALLFUNC,CASE,CEIL,CHDIR,CHDRIVE,CHR$,CINT,
            CLNG,CLS,CODEPTR,COMMAND$,COMMANDCOUNT,CONSOLE,CONST,CONSTRUCTOR,
            CONVBASE$,COS,CREATE,CSRLIN,CURDIR$,DATA,DATE$,DEC,DECLARE,
            DEFBYTE,DEFDBL,DEFDWORD,DEFINT,DEFLNG,DEFSHORT,DEFSNG,DEFSTR,
            DEFWORD,DELETE$,DIM,DIR$,DIREXISTS,DO,DOEVENTS,DOUBLE,DWORD,
            ELSE,ELSEIF,END,ENVIRON,ENVIRON$,EVENT,EXIT,EXP,EXTENDS,
            EXTRACTRESOURCE,FIELD$,FILEEXISTS,FIX,FLOOR,FOR,FORMAT$,FRAC,
            FUNCTION,FUNCTIONI,GET$,GOSUB,GOTO,HEX$,IF,INC,INITARRAY,
            INKEY$,INP,INPUT,INPUT$,INPUTHANDLE,INSERT$,INSTR,INT,INTEGER,
            INV,IS,ISCONSOLE,KILL,KILLMESSAGE,LBOUND,LCASE$,LEFT$,LEN,
            LFLUSH,LIB,LIBRARYINST,LOCATE,LOG,LONG,LOOP,LPRINT,LTRIM$,
            MEMCMP,MESSAGEBOX,MESSAGEDLG,MID$,MKDIR,MOD,MOUSEX,MOUSEY,
            NEXT,NOT,OFF,ON,OR,OUT,OUTPUTHANDLE,PARAMSTR$,PARAMSTRCOUNT,
            PARAMVAL,PARAMVALCOUNT,PCOPY,PEEK,PLAYWAV,POKE,POS,POSTMESSAGE,
            PRINT,PROPERTY,QUICKSORT,RANDOMIZE,REDIM,RENAME,REPLACE$,
            REPLACESUBSTR$,RESOURCE,RESOURCECOUNT,RESTORE,RESULT,RETURN,
            REVERSE$,RGB,RIGHT$,RINSTR,RMDIR,RND,ROUND,RTRIM$,RUN,
            SCREEN,SELECT,SENDER,SENDMESSAGE,SETCONSOLETITLE,SGN,SHELL,
            SHL,SHORT,SHOWMESSAGE,SHR,SIN,SINGLE,SIZEOF,SLEEP,SOUND,
            SPACE$,SQR,STACK,STATIC,STEP,STR$,STRF$,STRING,STRING$,
            SUB,SUBI,SWAP,TALLY,TAN,THEN,TIME$,TIMER,TO,TYPE,UBOUND,
            UCASE$,UNLOADLIBRARY,UNTIL,VAL,VARIANT,VARPTR,VARPTR$,VARTYPE,
            WEND,WHILE,WITH,WORD,XOR
    """)
        self.color('rapidq', text)
    #@+node:ekr.20210905170507.29: *3* TestColorizer.test_colorizer_Rebol
    def test_colorizer_Rebol(self):
        text = textwrap.dedent("""\
        ; a comment
        about abs absolute add alert alias all alter and and~ any append arccosine arcsine arctangent array ask at
        back bind boot-prefs break browse build-port build-tag
        call caret-to-offset catch center-face change change-dir charset checksum choose clean-path clear clear-fields close comment complement compose compress confirm continue-post context copy cosine create-request crypt cvs-date cvs-version
        debase decode-cgi decode-url decompress deflag-face dehex delete demo desktop detab dh-compute-key dh-generate-key dh-make-key difference dirize disarm dispatch divide do do-boot do-events do-face do-face-alt does dsa-generate-key dsa-make-key dsa-make-signature dsa-verify-signature
        echo editor either else emailer enbase entab exclude exit exp extract
        fifth find find-key-face find-window flag-face first flash focus for forall foreach forever form forskip fourth free func function
        get get-modes get-net-info get-style
        halt has head help hide hide-popup
        if import-email in inform input insert insert-event-func intersect
        join
        last launch launch-thru layout license list-dir load load-image load-prefs load-thru log-10 log-2 log-e loop lowercase
        make make-dir make-face max maximum maximum-of min minimum minimum-of mold multiply
        negate net-error next not now
        offset-to-caret open open-events or or~
        parse parse-email-addrs parse-header parse-header-date parse-xml path-thru pick poke power prin print probe protect protect-system
        q query quit
        random read read-io read-net read-thru reboot recycle reduce reform rejoin remainder remold remove remove-event-func rename repeat repend replace request request-color request-date request-download request-file request-list request-pass request-text resend return reverse rsa-encrypt rsa-generate-key rsa-make-key
        save save-prefs save-user scroll-para second secure select send send-and-check set set-modes set-font set-net set-para set-style set-user set-user-name show show-popup sine size-text skip sort source split-path square-root stylize subtract switch
        tail tangent textinfo third throw throw-on-error to to-binary to-bitset to-block to-char to-date to-decimal to-email to-event to-file to-get-word to-hash to-hex to-idate to-image to-integer to-issue to-list to-lit-path to-lit-word to-local-file to-logic to-money to-none to-pair to-paren to-path to-rebol-file to-refinement to-set-path to-set-word to-string to-tag to-time to-tuple to-url to-word trace trim try
        unfocus union unique uninstall unprotect unset until unview update upgrade uppercase usage use
        vbug view view-install view-prefs
        wait what what-dir while write write-io
        xor xor~
        action! any-block! any-function! any-string! any-type! any-word!
        binary! bitset! block!
        char!
        datatype! date! decimal!
        email! error! event!
        file! function!
        get-word!
        hash!
        image! integer! issue!
        library! list! lit-path! lit-word! logic!
        money!
        native! none! number!
        object! op!
        pair! paren! path! port!
        refinement! routine!
        series! set-path! set-word! string! struct! symbol!
        tag! time! tuple!
        unset! url!
        word!
        any-block? any-function? any-string? any-type? any-word?
        binary? bitset? block?
        char? connected? crypt-strength?
        datatype? date? decimal? dir?
        email? empty? equal? error? even? event? exists? exists-key?
        file? flag-face? found? function?
        get-word? greater-or-equal? greater?
        hash? head?
        image? in-window? index? info? input? inside? integer? issue?
        length? lesser-or-equal? lesser? library? link-app? link? list? lit-path? lit-word? logic?
        modified? money?
        native? negative? none? not-equal? number?
        object? odd? offset? op? outside?
        pair? paren? path? port? positive?
        refinement? routine?
        same? screen-offset? script? series? set-path? set-word? size? span? strict-equal? strict-not-equal? string? struct?
        tag? tail? time? tuple? type?
        unset? url?
        value? view?
        within? word?
        zero?
    """)
        self.color('rebol', text)
    #@+node:ekr.20210905170507.30: *3* TestColorizer.test_colorizer_rest
    def test_colorizer_rest(self):
        text = textwrap.dedent(r"""\\\
            @ @rst-options
            code_mode=False
            generate_rst=True
            http_server_support = False
            show_organizer_nodes=True
            show_headlines=True
            show_leo_directives=True
            stylesheet_path=..\doc
            write_intermediate_file = False
            verbose=True
            @c

            . Links used in this document...

            .. _`Pmw`:                  http://pmw.sourceforge.net/
            .. _run:                    `Running Leo`_

            .. WARNING: image targets may not have upper case letters!

            .. |back| image:: arrow_lt.gif
                :target: FAQ.html

            .. |leo| image:: leo.gif
                :target: front.html

            .. |next| image:: arrow_rt.gif
                :target: intro.html

            |back| |leo| |next|

            ###########################
            Chapter 1: Installing Leo
            ###########################

            This chapter tells how to install and run Leo.

            **Important**:

            If you have *any* problems installing Leo,
            please ask for help on Leo's help forum:

            .. contents::

            **Windows**
                If you have `associated .leo files with Leo`_ you may run Leo by double-clicking any .leo file.
                You can also use a batch file.
                Put the following .bat file in c:\\Windows::

                    cd c:\prog\LeoCVS\leo
                    c:\python22\python c:\prog\LeoCVS\leo\leo.py %1

            -   Download the latest version of Leo from `Leo's download page`_.

            -   In Windows 2K or XP, go to ``Start->Settings->Control panel``, open the ``Folder Options`` tab.

                **Warning**: When building Tcl on Linux, do **not** specify
                "--enable-threads".
                Only use Tcl with the default "threads not enabled" case.

            -------------

            |back| |leo| |next|
    """)
        self.color('rest', text)
    #@+node:ekr.20210905170507.31: *3* TestColorizer.test_colorizer_scala
    def test_colorizer_scala(self):
        text = textwrap.dedent("""\
            /* A comment */

            object HelloWorld {
                def main(args: Array[String]) {
                  println("Hello, world!")
                }
              }
    """)
        self.color('scala', text)
    #@+node:ekr.20210905170507.32: *3* TestColorizer.test_colorizer_shell
    def test_colorizer_shell(self):
        text = textwrap.dedent("""\
            # New in 4.2.

            # comment
            $# not a comment
            break
            case,continue,
            do,done
            elif,else,esac
            fi,for
            if,in
            return,
            then
            until
            while,

            cd,chdir,eval,exec,
            exit,kill,newgrp,pwd,read,readonly,
            shift,test,trap,ulimit,
            umask,wait
    """)
        self.color('shell', text)
    #@+node:ekr.20210905170507.33: *3* TestColorizer.test_colorizer_shellscript
    def test_colorizer_shellscript(self):
        text = textwrap.dedent("""\
            # comment
            $# not a comment
            break
            case,continue,
            do,done
            elif,else,esac
            fi,for
            if,in
            return,
            then
            until
            while,

            cd,chdir,eval,exec,
            exit,kill,newgrp,pwd,read,readonly,
            shift,test,trap,ulimit,
            umask,wait
    """)
        self.color('shellscript', text)
    #@+node:ekr.20210905170507.34: *3* TestColorizer.test_colorizer_tex_xml_jEdit_
    def test_colorizer_tex_xml_jEdit_(self):
        text = textwrap.dedent("""\
            <!-- ekr uses the MARK_FOLLOWING to mark _anything_ after \\ -->

            <?xml version="1.0"?>

            <!DOCTYPE MODE SYSTEM "xmode.dtd">

            <MODE>
                <PROPS>
                    <PROPERTY NAME="lineComment" VALUE="%" />
                </PROPS>

                <RULES>
                    < < general rules > >
                </RULES>

                <RULES SET="MATH" DEFAULT="MARKUP">
                    < < math rules > >
                </RULES>
            </MODE>
    """)
        self.color('html', text)
    #@+node:ekr.20210905170507.36: *3* TestColorizer.test_colorizer_wikiTest
    def test_colorizer_wikiTest(self):
        # both color_markup & add_directives plugins must be enabled.
        text = textwrap.dedent('''\
            @markup wiki

            """ text~~red:some text~~more text"""

            """ text~~#ee0ff:some text~~more text"""

            if 1 and 2:
                pass
    ''')
        self.color('html', text)
    #@+node:ekr.20210905170507.39: *3* TestColorizer.test_scanColorDirectives
    def test_scanColorDirectives(self):
        c = self.c
        language = g.findLanguageDirectives(c, c.p)
        self.assertEqual(language, 'python')
    #@+node:ekr.20210905170507.40: *3* TestColorizer.test_vbscript
    def test_vbscript(self):
        text = textwrap.dedent("""\
            if
            IF
    """)
        self.color('vbscript', text)
    #@-others
#@-others
#@-leo

#@+leo-ver=5-thin
#@+node:ekr.20210903162431.1: * @file ../unittests/core/test_leoCommands.py
"""Tests of leoCommands.py"""
# pylint: disable=no-member
import sys
from leo.core import leoGlobals as g
from leo.plugins.mod_scripting import scriptingController
from leo.core.leoTest2 import LeoUnitTest

#@+others
#@+node:ekr.20210903162431.2: ** class TestCommands(LeoUnitTest)
class TestCommands(LeoUnitTest):
    """Test cases for leoCommands.py"""
    #@+others
    #@+node:ekr.20210906075242.28: *3* TestCommands.test_add_comments_with_multiple_language_directives
    def test_add_comments_with_multiple_language_directives(self):
        c, p, w = self.c, self.c.p, self.c.frame.body.wrapper
        p.b = self.prep(
        """
            @language rest
            rest text.
            @language python
            def spam():
                pass
            # after
        """)
        expected = self.prep(
        """
            @language rest
            rest text.
            @language python
            def spam():
                # pass
            # after
        """)
        i = p.b.find('pass')
        assert i > -1, 'fail1: %s' % (repr(p.b))
        w.setSelectionRange(i, i + 4)
        c.addComments()
        self.assertEqual(p.b, expected)
    #@+node:ekr.20210906075242.30: *3* TestCommands.test_add_html_comments
    def test_add_html_comments(self):
        c, p, w = self.c, self.c.p, self.c.frame.body.wrapper
        p.b = self.prep(
        """
            @language html
            <html>
                text
            </html>
        """)
        expected = self.prep(
        """
            @language html
            <html>
                <!-- text -->
            </html>
        """)
        i = p.b.find('text')
        w.setSelectionRange(i, i + 4)
        c.addComments()
        self.assertEqual(p.b, expected)
    #@+node:ekr.20210906075242.32: *3* TestCommands.test_add_python_comments
    def test_add_python_comments(self):
        c, p, w = self.c, self.c.p, self.c.frame.body.wrapper
        p.b = self.prep(
        """
            @language python
            def spam():
                pass
            # after
        """)
        expected = self.prep(
        """
            @language python
            def spam():
                # pass
            # after
        """)
        i = p.b.find('pass')
        w.setSelectionRange(i, i + 4)
        c.addComments()
        self.assertEqual(p.b, expected)
    #@+node:ekr.20210906075242.2: *3* TestCommands.test_c_alert
    def test_c_alert(self):
        c = self.c
        c.alert('test of c.alert')
    #@+node:ekr.20230727044355.1: *3* TestCommands.test_c_check_links
    def check_c_checkVnodeLinks(self):
        c = self.c
        self.assertEqual(c.checkVnodeLinks(), 0)  # Leo's main checker.
        self.assertEqual(c.checkLinks(), 0)  # A slow test, suitable only for unit tests.
    #@+node:ekr.20210906075242.3: *3* TestCommands.test_c_checkOutline
    def test_c_checkOutline(self):
        c = self.c
        self.assertEqual(0, c.checkOutline())
    #@+node:ekr.20210901140645.15: *3* TestCommands.test_c_checkPythonCode
    def test_c_checkPythonCode(self):
        c = self.c
        c.checkPythonCode(event=None, ignoreAtIgnore=False, checkOnSave=False)
    #@+node:ekr.20210901140645.16: *3* TestCommands.test_c_checkPythonNode
    def test_c_checkPythonNode(self):
        c, p = self.c, self.c.p
        p.b = self.prep(
        """
            @language python

            def abc:  # missing parens.
                pass
        """)
        result = c.checkPythonCode(event=None, checkOnSave=False, ignoreAtIgnore=True)
        self.assertEqual(result, 'error')
    #@+node:ekr.20210906075242.4: *3* TestCommands.test_c_contractAllHeadlines
    def test_c_contractAllHeadlines(self):
        c = self.c
        c.contractAllHeadlines()
        p = c.rootPosition()
        while p.hasNext():
            p.moveToNext()
        c.redraw(p)
    #@+node:ekr.20210906075242.6: *3* TestCommands.test_c_demote_illegal_clone_demote
    def test_c_demote_illegal_clone_demote(self):
        c, p = self.c, self.c.p
        # Create two cloned children.
        c.selectPosition(p)
        c.insertHeadline()
        p2 = c.p
        p2.moveToFirstChildOf(p)
        p2.setHeadString('aClone')
        c.selectPosition(p2)
        c.clone()
        self.assertEqual(2, p.numberOfChildren())
        # Select the first clone and demote (it should be illegal)
        c.selectPosition(p2)
        c.demote()  # This should do nothing.
        self.assertEqual(0, c.checkOutline())
        self.assertEqual(2, p.numberOfChildren())
    #@+node:felix.20250414224343.1: *3* TestCommands.test_c_doCommandByName_return_result
    def test_c_doCommandByName_return_result(self):
        c, p = self.c, self.c.p

        # test an existing native Leo command such as 'convert-blanks'.
        c.selectPosition(p)
        c.insertHeadline()
        p2 = c.p
        p2.b = self.prep(
        """
            @language python

            def abc():  # this contains spaces
                pass
        """)
        c.selectPosition(p2)

        # It will return True if it changed the text.
        val = c.doCommandByName('convert-blanks')
        assert val is True, f"expected: True got: {val}"
        
        # Call it again, it should return False.
        val = c.doCommandByName('convert-blanks')
        assert val is False, f"expected: False got: {val}"
        
    #@+node:felix.20250414224344.1: *3* TestCommands.test_c_doCommandByName_return_result_from_leo_script
    def test_c_doCommandByName_return_result_from_leo_script(self):
        c, p = self.c, self.c.p

        # Creates a command from an @command node with mod_scripting's scriptingController.
        c.selectPosition(p)
        c.insertHeadline()
        p2 = c.p
        p2.h = "@command test-return-result"  # an @command node
        p2.b = self.prep(
        """
            g.es('test script that sets result global')
            global result  # pythonic way of outputing something from an 'exec' call.
            result = 42
        """)
        c.selectPosition(p2)

        sc = getattr(c, "theScriptingController", None)
        if not sc:
            sc = scriptingController(c, True)  # Fakes the unused iconBar with 'True'.
        sc.handleAtCommandNode(p2)

        val = c.doCommandByName('test-return-result')
        assert val == 42, f"expected: 42 got: {val}"

    #@+node:ekr.20210906075242.7: *3* TestCommands.test_c_expand_path_expression
    def test_c_expand_path_expression(self):
        import os
        c = self.c
        abs_base = '/leo_base'
        c.mFileName = f"{abs_base}/test.leo"
        os.environ = {
            'HOME': '/home',  # Linux.
            'USERPROFILE': r'c:\EKR',  # Windows.
            'LEO_BASE': abs_base,
        }
        home = os.path.expanduser('~')
        assert home in (os.environ['HOME'], os.environ['USERPROFILE']), repr(home)

        # c.expand_path_expressions *only* calls os.path.expanduser and os.path.expandvars.
        seps = ('\\', '/') if g.isWindows else ('/',)
        for sep in seps:
            table = (
                (f"~{sep}a.py", f"{home}{sep}a.py"),
                (f"~{sep}x{sep}..{sep}b.py", f"{home}{sep}x{sep}..{sep}b.py"),
                (f"$LEO_BASE{sep}b.py", f"{abs_base}{sep}b.py"),
                ('c.py', 'c.py'),
            )
            for s, expected in table:
                got = c.expand_path_expression(s)
                self.assertEqual(got, expected, msg=s)
    #@+node:ekr.20210906075242.8: *3* TestCommands.test_c_findMatchingBracket
    def test_c_findMatchingBracket(self):
        c, w = self.c, self.c.frame.body.wrapper
        s = '(abc)'
        c.p.b = s
        table = (
            (-1, -1),
            (len(s), len(s)),
            (0, 0),
            (1, 1),
        )
        for i, j in table:
            w.setSelectionRange(-1, len(s))
            c.findMatchingBracket(event=None)
            i2, j2 = w.getSelectionRange()
            self.assertTrue(i2 < j2, msg=f"i: {i}, j: {j}")

    #@+node:ekr.20250404075346.1: *3* TestCommands.test_c_getEncoding
    def test_c_getEncoding(self):
        c, p = self.c, self.c.p
        self.root_p.b = ''  # To ensure default.
        child = p.insertAfter()
        child.h = 'child'
        child.b = '@encoding utf-8\n'
        grand = child.insertAsLastChild()
        grand.h = 'grand-child'
        grand.b = '#\n@encoding utf-16\n'
        great = grand.insertAsLastChild()
        great.h = 'great-grand-child'
        great.b = ''
        table = (
            (great, 'utf-16'),
            (grand, 'utf-16'),
            (child, 'utf-8'),
            (self.root_p, 'utf-8'),
        )
        for p2, expected in table:
            encoding = c.getEncoding(p2)
            message = f"expected: {expected} got: {encoding} {p2.h}"
            assert encoding == expected, message

    #@+node:ekr.20250412054157.1: *3* TestCommands.test_c_getLineEnding
    def test_c_getLineEnding(self):
        c = self.c
        p = c.p
        table = (
            ('nl', '\n'),
            ('lf', '\n'),
            ('cr', '\r'),
            ('crlf', '\r\n'),
            ('platform', '\r\n' if sys.platform.startswith('win') else '\n'),
        )
        for kind, expected_ending in table:
            directive = f"@lineending {kind}\n"
            p.b = directive
            ending = c.getLineEnding(p)
            message = f"{directive}: expected {expected_ending!r} got {ending!r}"
            assert ending == expected_ending, message
    #@+node:ekr.20250412054231.1: *3* TestCommands.test_c_getPageWidth
    def test_c_getPageWidth(self):
        c = self.c
        p = c.p
        for w in (-40, 40):
            p.b = f"@pagewidth {w}\n"
            n = c.getPageWidth(p)
            assert n == w
    #@+node:ekr.20250412054256.1: *3* TestCommands.test_c_gettabWidth
    def test_c_getTabWidth(self):
        c = self.c
        p = c.p
        for w in (-6, 6):
            p.b = f"@tabwidth {w}\n"
            n = c.getTabWidth(p)
            assert n == w
    #@+node:ekr.20250412054404.1: *3* TestCommands.test_c_getWrap
    def test_c_getWrap(self):
        c = self.c
        p = c.p
        table = (
            ('@nowrap\n', False),
            ('@wrap\n', True),
            (p.b, None),
        )
        for s, expected_val in table:
            p.b = s
            val = c.getWrap(p)
            assert val == expected_val
    #@+node:ekr.20210906075242.9: *3* TestCommands.test_c_hiddenRootNode_fileIndex
    def test_c_hiddenRootNode_fileIndex(self):
        c = self.c
        assert c.hiddenRootNode.fileIndex.startswith('hidden-root-vnode-gnx'), c.hiddenRootNode.fileIndex
    #@+node:ekr.20210906075242.10: *3* TestCommands.test_c_hoist_chapter_node
    def test_c_hoist_chapter_node(self):
        c = self.c
        # Create the @settings and @chapter nodes.
        settings = c.rootPosition().insertAfter()
        settings.h = '@settings'
        chapter = settings.insertAsLastChild()
        chapter.h = '@chapter aaa'
        aaa = chapter.insertAsLastChild()
        aaa.h = 'aaa node 1'
        assert not c.hoistStack
        c.selectPosition(aaa)
        # Test.
        c.hoist()  # New in Leo 5.3: should do nothing
        self.assertEqual(c.p, aaa)
        c.dehoist()  # New in Leo 5.3: should do nothing:
        self.assertEqual(c.p, aaa)
        self.assertEqual(c.hoistStack, [])
    #@+node:ekr.20210906075242.11: *3* TestCommands.test_c_hoist_followed_by_goto_first_node
    def test_c_hoist_followed_by_goto_first_node(self):
        c = self.c
        # Create the @settings and @chapter nodes.
        settings = c.rootPosition().insertAfter()
        settings.h = '@settings'
        chapter = settings.insertAsLastChild()
        chapter.h = '@chapter aaa'
        aaa = chapter.insertAsLastChild()
        aaa.h = 'aaa node 1'
        # Test.
        assert not c.hoistStack
        c.selectPosition(aaa)
        assert not c.hoistStack

        # The de-hoist happens in c.expandOnlyAncestorsOfNode, the call to c.selectPosition.
        if 1:
            c.hoist()
            c.goToFirstVisibleNode()
            self.assertEqual(c.p, aaa)
        else:
            c.hoist()
            c.goToFirstNode()
            assert not c.hoistStack  # The hoist stack must be cleared to show the first node.
            self.assertEqual(c.p, c.rootPosition())
            assert c.p.isVisible(c)
    #@+node:ekr.20210906075242.12: *3* TestCommands.test_c_hoist_with_no_children
    def test_c_hoist_with_no_children(self):
        c = self.c
        c.hoist()
        c.dehoist()
    #@+node:ekr.20210906075242.13: *3* TestCommands.test_c_insertBodyTime
    def test_c_insertBodyTime(self):
        c = self.c
        # p = c.p
        # w = c.frame.body.wrapper
        # s = w.getAllText()
        # w.setInsertPoint(len(s))
        c.insertBodyTime()
    #@+node:ekr.20210906075242.15: *3* TestCommands.test_c_markSubheads
    def test_c_markSubheads(self):
        c = self.c
        child1 = c.rootPosition().insertAsLastChild()
        child2 = c.rootPosition().insertAsLastChild()
        assert child1 and child2
        c.markSubheads()
    #@+node:ekr.20210906075242.16: *3* TestCommands.test_c_pasteOutline_does_not_clone_top_node
    def test_c_pasteOutline_does_not_clone_top_node(self):
        c = self.c
        p = c.p
        p.b = '# text.'
        # child1 = c.rootPosition().insertAsLastChild()
        # c.selectPosition(child)
        c.copyOutline()
        p2 = c.pasteOutline()
        assert p2
        assert not p2.isCloned()
    #@+node:ekr.20250404075519.1: *3* TestCommands.test_c_getPath
    def test_c_getPath(self):
        c, p = self.c, self.c.p
        child = p.insertAfter()
        child.h = '@path one'
        grand = child.insertAsLastChild()
        grand.h = '@path two'
        great = grand.insertAsLastChild()
        great.h = 'xyz'
        path = c.getPath(great)
        endpath = g.os_path_normpath('one/two')
        assert path.endswith(endpath), f"expected '{endpath}' got '{path}'"

        # Test 2: Create a commander for an outline outside of g.app.loadDir and its parents.
        from leo.core.leoCommands import Commands
        c = Commands(fileName='~/LeoPyRef.leo', gui=g.app.gui)
        child = p.insertAfter()
        child.h = '@path one'
        grand = child.insertAsLastChild()
        grand.h = '@path two'
        great = grand.insertAsLastChild()
        great.h = 'xyz'
        path = c.getPath(great)
        endpath = g.os_path_normpath('one/two')
        assert path.endswith(endpath), f"expected '{endpath}' got '{path}'"
    #@+node:ekr.20210901140645.17: *3* TestCommands.test_c_tabNannyNode
    def test_c_tabNannyNode(self):
        c, p = self.c, self.c.p
        # Test 1.
        s = self.prep(
        """
            # no error
            def spam():
                pass
        """)
        c.tabNannyNode(p, headline=p.h, body=s)
        # Test 2.
        s2 = self.prep(
        """
            # syntax error
            def spam:
                pass
              a = 2
        """)
        try:
            c.tabNannyNode(p, headline=p.h, body=s2)
        except IndentationError:
            pass
    #@+node:ekr.20210906075242.20: *3* TestCommands.test_c_unmarkAll
    def test_c_unmarkAll(self):
        c = self.c
        c.unmarkAll()
        for p in c.all_positions():
            assert not p.isMarked(), p.h
    #@+node:ekr.20210906075242.21: *3* TestCommands.test_class_StubConfig
    def test_class_StubConfig(self):
        c = self.c
        class StubConfig(g.NullObject):
            pass

        x = StubConfig()
        assert not x.getBool(c, 'mySetting')
        assert not x.enabledPluginsFileName
    #@+node:ekr.20210906075242.29: *3* TestCommands.test_delete_comments_with_multiple_at_language_directives
    def test_delete_comments_with_multiple_at_language_directives(self):
        c, p, w = self.c, self.c.p, self.c.frame.body.wrapper
        p.b = self.prep(
        """
            @language rest
            rest text.
            @language python
            def spam():
                pass
            # after
        """)
        expected = self.prep(
        """
            @language rest
            rest text.
            @language python
            def spam():
                pass
            # after
        """)
        i = p.b.find('pass')
        w.setSelectionRange(i, i + 4)
        c.deleteComments()
        self.assertEqual(p.b, expected)

    #@+node:ekr.20210906075242.31: *3* TestCommands.test_delete_html_comments
    def test_delete_html_comments(self):
        c, p, w = self.c, self.c.p, self.c.frame.body.wrapper
        p.b = self.prep(
        """
            @language html
            <html>
                <!-- text -->
            </html>
        """)
        expected = self.prep(
        """
            @language html
            <html>
                text
            </html>
        """)
        i = p.b.find('text')
        w.setSelectionRange(i, i + 4)
        c.deleteComments()
        self.assertEqual(p.b, expected)
    #@+node:ekr.20210906075242.33: *3* TestCommands.test_delete_python_comments
    def test_delete_python_comments(self):
        c, p, w = self.c, self.c.p, self.c.frame.body.wrapper
        p.b = self.prep(
        """
            @language python
            def spam():
                # pass
            # after
        """)
        expected = self.prep(
        """
            @language python
            def spam():
                pass
            # after
        """)
        i = p.b.find('pass')
        w.setSelectionRange(i, i + 4)
        c.deleteComments()
        self.assertEqual(p.b, expected)
    #@+node:ekr.20230308103855.1: *3* TestCommands.test_find_b_h
    def test_find_b_h(self):

        c, p = self.c, self.c.p

        # Create two children of c.p.
        child1 = p.insertAsLastChild()
        child1.h = 'child1 headline'
        child1.b = 'child1 line1\nchild2 line2\n'
        child2 = p.insertAsLastChild()
        child2.h = 'child2 headline'
        child2.b = 'child2 line1\nchild2 line2\n'

        # Tests.
        list1 = c.find_h(r'^child1')
        assert list1 == [child1], repr(list1)
        list2 = c.find_h(r'^child1', it=[child2])
        assert not list2, repr(list2)
        list3 = c.find_b(r'.*\bline2\n')
        assert list3 == [child1, child2], repr(list3)
        list4 = c.find_b(r'.*\bline2\n', it=[child1])
        assert list4 == [child1], repr(list3)
    #@+node:ekr.20210901140645.27: *3* TestCommands.test_koi8_r_encoding
    def test_koi8_r_encoding(self):
        c, p = self.c, self.c.p
        p1 = p.insertAsLastChild()
        s = '\xd4\xc5\xd3\xd4'  # the word 'test' in Russian, koi8-r
        assert isinstance(s, str), repr(s)
        p1.setBodyString(s)
        c.selectPosition(p1)
        c.copyOutline()
        c.pasteOutline()
        p2 = p1.next()
        self.assertEqual(p1.b, p2.b)

    #@+node:ekr.20210901140645.9: *3* TestCommands.test_official_commander_ivars
    def test_official_commander_ivars(self):
        c = self.c
        f = c.frame
        self.assertEqual(c, f.c)
        self.assertEqual(f, c.frame)
        ivars = (
            '_currentPosition',
            'hoistStack',
            'mFileName',
            # Subcommanders...
            'atFileCommands', 'fileCommands', 'importCommands', 'undoer',
            # Args...
            'page_width', 'tab_width', 'target_language',
        )
        for ivar in ivars:
            self.assertTrue(hasattr(c, ivar), msg=ivar)
    #@-others
#@-others
#@-leo

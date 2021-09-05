# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20210901172411.1: * @file ../unittests/core/test_leoAtFile.py
#@@first
"""Tests of leoApp.py"""
import os
import re
import tempfile
import textwrap
from leo.core import leoGlobals as g
from leo.core import leoBridge
from leo.core.leoTest2 import LeoUnitTest
#@+others
#@+node:ekr.20210901172446.1: ** class TestAtFile(LeoUnitTest)
class TestApp(LeoUnitTest):
    """Test cases for leoApp.py"""
    #@+others
    #@+node:ekr.20200204095726.1: *3*  TestAtFile.bridge
    def bridge(self):
        """Return an instance of Leo's bridge."""
        return leoBridge.controller(gui='nullGui',
            loadPlugins=False,
            readSettings=False,
            silent=True,
            verbose=False,
        )
    #@+node:ekr.20210901140645.13: *3* TestAtFile.test_at_checkPythonSyntax
    def test_at_checkPythonSyntax(self):
        c, p = self.c, self.c.p
        at = c.atFileCommands
        s = textwrap.dedent('''\
    # no error
    def spam():
        pass
        ''')
        assert at.checkPythonSyntax(p,s),'fail 1'

        s2 = textwrap.dedent('''\
    # syntax error
    def spam:  # missing parens.
        pass
        ''')

        assert not at.checkPythonSyntax(p,s2,supress=True),'fail2'

        if not g.unitTesting: # A hand test of at.syntaxError
            at.checkPythonSyntax(p,s2)
    #@+node:ekr.20210901140645.14: *3* TestAtFile.test_at_tabNannyNode
    def test_at_tabNannyNode(self):
        c, p = self.c, self.c.p
        at = c.atFileCommands
        s = '''
        # no error
        def spam():
            pass
        '''
        at.tabNannyNode (p, body=s, suppress=True)
        s2 = '''
        # syntax error
        def spam:
            pass
          a = 2
        '''
        try:
            at.tabNannyNode(p,body=s2,suppress=True)
        except IndentationError:
            pass
    #@+node:ekr.20200204094139.1: *3* TestAtFile.test_bug_1469
    def test_save_after_external_file_rename(self):
        """Test #1469: saves renaming an external file."""
        # Create a new outline with @file node and save it
        bridge = self.bridge()
        with tempfile.TemporaryDirectory() as temp_dir:
            filename = f"{temp_dir}{os.sep}test_file.leo"
            c = bridge.openLeoFile(filename)
            p = c.rootPosition()
            p.h = '@file 1'
            p.b = 'b1'
            c.save()
            # Rename the @file node and save
            p1 = c.rootPosition()
            p1.h = "@file 1_renamed"
            c.save()
            # Remove the original "@file 1" from the disk
            external_filename = f"{temp_dir}{os.sep}1"
            assert os.path.exists(external_filename)
            os.remove(external_filename)
            assert not os.path.exists(external_filename)
            # Change the @file contents, save and reopen the outline
            p1.b = "b_1_changed"
            c.save()
            c.close()
            c = bridge.openLeoFile(c.fileName())
            p1 = c.rootPosition()
            assert p1.h == "@file 1_renamed", repr(p1.h)
            assert p1.b == "b_1_changed", repr(p1.b)
    #@+node:ekr.20210421035527.1: *3* TestAtFile.test_bug_1889
    def test_bug_1889(self):
        """
        Test #1889: Honor ~ in ancestor @path nodes.
        """
        # Create a new outline with @file node and save it
        bridge = self.bridge()
        with tempfile.TemporaryDirectory() as temp_dir:
            filename = f"{temp_dir}{os.sep}test_file.leo"
            c = bridge.openLeoFile(filename)
            root = c.rootPosition()
            root.h = '@path ~/sub-directory/'
            child = root.insertAsLastChild()
            child.h = '@file test_bug_1889.py'
            child.b = '@language python\n# test #1889'
            path = g.fullPath(c, child)
            assert '~' not in path, repr(path)
    #@+node:ekr.20210905044728.1: *3* Converted nodes
    #@+node:ekr.20210905044744.1: *4* calling runAtFileTest 
    #@+node:ekr.20210905044728.2: *5* TestXXX.test_at_auto_newlines_at_end_of_nodes_
    def test_at_auto_newlines_at_end_of_nodes_(self):
        c = self.c
        c.testManager.runAtFileTest(c.p)
    #@+node:ekr.20210905045005.3: *6* #@auto
    # # # @language python
    # # # @tabwidth -4
    # # # @others
    # # # #end
    #@+node:ekr.20210905045005.4: *7* spam
    # # # def spam(cheese):

        # # # print(cheese)
    #@+node:ekr.20210905045005.5: *7* cheese
    # # # def cheese():

        # # # pass
    #@+node:ekr.20210905045005.6: *6* Output
    # # # def spam(cheese):

        # # # print(cheese)
    # # # def cheese():

        # # # pass
    # # # #end
    #@+node:ekr.20210905044728.3: *5* TestXXX.test_at_auto_no_newline_at_end_of_nodes_
    def test_at_auto_no_newline_at_end_of_nodes_(self):
        c = self.c
        c.testManager.runAtFileTest(c.p)
    #@+node:ekr.20210905045005.8: *6* #@auto
    # # # @language python
    # # # @tabwidth -4
    # # # @others
    # # # #end
    #@+node:ekr.20210905045005.9: *7* spam
    # # # def spam(cheese):

        # # # print(cheese)
    #@+node:ekr.20210905045005.10: *7* cheese
    # # # def cheese():

        # # # pass
    #@+node:ekr.20210905045005.11: *6* Output
    # # # def spam(cheese):

        # # # print(cheese)
    # # # def cheese():

        # # # pass
    # # # #end
    #@+node:ekr.20210905044728.4: *5* TestXXX.test_at_edit
    def test_at_edit(self):
        c = self.c
        c.testManager.runAtFileTest(c.p)
    #@+node:ekr.20210905045005.13: *6* #@edit
    ### These were text lines, without the leading '#'

    # Line 1

    # Last line: no newline
    #@+node:ekr.20210905045005.14: *6* Output
    ### These were text lines, without the leading '#'

    # Line 1

    # Last line: no newline
    #@+node:ekr.20210905044728.5: *5* TestXXX.test_at_raw
    def test_at_raw(self):
        c = self.c
        c.testManager.runAtFileTest(c.p)
    #@+node:ekr.20210905045005.16: *6* #@file
    # before

    # @raw

    # @c

    ### < < ref > >  ### Was an actual section ref.

    # @end_raw

    #after
    #@+node:ekr.20210905045005.17: *6* Output
    ###@+leo-ver=5-thin
    ###@+node:ekr.20110524120515.3490: * #@file
    # before

    #@verbatim
    #@@raw

    # @c

    ### < < ref > >  ### Was real section ref ###

    #@verbatim
    #@@end_raw

    #after
    #@verbatim
    #@-leo
    #@+node:ekr.20210905045005.18: *6* Old-Output
    ###@+leo-ver=5
    ###@+node:#@file
    # before

    #@verbatim
    #@@raw

    # @c

    ### < < ref > >  ### Was real section ref ###

    #@verbatim
    #@@end_raw

    #after
    #@verbatim
    #@-leo
    #@+node:ekr.20210905044728.6: *5* TestXXX.test_at_thin with at_last
    def test__thin_with_at_last(self):
        c = self.c
        c.testManager.runAtFileTest(c.p)
    #@+node:ekr.20210905045005.20: *6* #@thin
    # Line 1

    ### Was an actual @last directive.
    ### @last last line 1: no newline
    #@+node:ekr.20210905045005.21: *6* Output
    ###@+leo-ver=5-thin
    ###@+node:ekr.20040707141957.13: * #@thin
    #Line 1

    ###@@last
    ###@-leo
    #last line 1: no newline
    #@+node:ekr.20210905045150.1: *4* using children
    #@+node:ekr.20210905044728.7: *5* TestXXX.test_at_readOneAtShadowNode
    def test_at_readOneAtShadowNode(self):
        c = self.c
        p = c.p
        at = c.atFileCommands
        # x = c.shadowController
        # changed = c.changed
        child = p.firstChild()
        # s = child.b
        try:
            fn = 'unittest/read_test.py'
            child.setHeadString('@shadow %s' % fn)
            at.writeOneAtShadowNode(child, testing=True)
            at.readOneAtShadowNode(fn,child)
        finally:
            child.setHeadString('@@shadow %s' % fn)
            c.clearChanged()
    #@+node:ekr.20210905045156.2: *6* @@shadow unittest/read_test.py
    #@@language python
    #@@tabwidth -4
    #@+others
    #@-others
    #@+node:ekr.20210905045231.1: *4* using sections
    #@+node:ekr.20210905044728.8: *5* TestXXX.test_at_putRefLine_1
    def test_at_putRefLine_1(self):
        c = self.c
        import re
        import leo.core.leoAtFile as atFile
        if 0: # prefix
            import importlib
            importlib.reload(atFile)
        at = atFile.AtFile(c)
        s = '''\
        if (
            %s and 
            %s > 3
        ):
            pass
        ''' % (g.angleBrackets('a'), g.angleBrackets('b'))
        # Careful: avoid @verbatim and other substitutions.
        expected = '''\
        AT+leo-ver=5-thin
        AT+node:GNX: * @test at.putRefLine 1
        if (
            AT+< <a> >
            AT+node:GNX: ** < < a > >
            a
            AT-< <a> >
            ATafterref
         and 
            AT+< <b> >
            AT+node:GNX: ** < < b > >
            b
            AT-< <b> >
            ATafterref
         > 3
        ):
            pass
        AT-leo
        '''.replace('AT','#@').replace('> >', '>>').replace('< <', '<<')

        result = at.stringToString(c.p, s)
        result = re.sub(r'#@\+node:(.+):', '#@+node:GNX:', result)
            # Don't test actual gnx's, so we can copy/paste this test.
        if 0: # Show unexpected mismatches.
            result = g.splitLines(result)
            expected = g.splitLines(expected)
            assert len(expected) == len(result)
            for i, s in enumerate(result):
                if expected[i] != result[i]:
                    print(i)
                    print('expected: %r' % expected[i])
                    print('result:   %r' % result[i])
                    break
        assert result == expected
    #@+node:ekr.20210905045316.3: *6* ### << a >>
    # # # a
    #@+node:ekr.20210905045316.4: *6* ### << b >>
    # # # b
    #@+node:ekr.20210905044728.9: *5* TestXXX.test_at_putRefLine_2
    def test_at_putRefLine_2(self):
        c = self.c
        import re
        import leo.core.leoAtFile as atFile
        if 0: # prefix
            import importlib
            importlib.reload(atFile)
        at = atFile.AtFile(c)
        s = '''\
        if (%s and %s > 3):
            pass
        ''' % (g.angleBrackets('a'), g.angleBrackets('b'))
        # Careful: avoid @verbatim and other substitutions.
        expected = '''\
        AT+leo-ver=5-thin
        AT+node:GNX: * @test at.putRefLine 2
        if (
        AT+< <a> >
        AT+node:GNX: ** < < a > >
        a
        AT-< <a> >
        ATafterref
         and 
        AT+< <b> >
        AT+node:GNX: ** < < b > >
        b
        AT-< <b> >
        ATafterref
         > 3):
            pass
        AT-leo
        '''.replace('AT','#@').replace('> >', '>>').replace('< <', '<<')
            # Recreate expected string.
        result = at.stringToString(c.p, s)
        result = re.sub(r'#@\+node:(.+):', '#@+node:GNX:', result)
            # Don't test actual gnx's, so we can copy/paste this test.
        if 0: # Show unexpected mismatches.
            result = g.splitLines(result)
            expected = g.splitLines(expected)
            # assert len(expected) == len(result)
            for i, s in enumerate(result):
                if expected[i] != result[i]:
                    print(i)
                    print('expected: %r' % expected[i])
                    print('result:   %r' % result[i])
                    break
        assert result == expected
    #@+node:ekr.20210905045316.6: *6* ### << a >>
    ### a
    #@+node:ekr.20210905045316.7: *6* ### << b >>
    ### b
    #@+node:ekr.20210905044728.10: *4* TestXXX.test__asis
    def test__asis(self):
        c = self.c
        c.testManager.runAtFileTest(c.p)
    #@+node:ekr.20210905044728.11: *4* TestXXX.test__asis___in_headline
    def test__asis___in_headline(self):
        c = self.c
        if g.app.isExternalUnitTest:
            self.skipTest('Not for external tests: uses @<file> node.')
        h = '@asis unittest/at-asis-test2.txt'
        p = g.findNodeAnywhere(c,h)
        assert p, h
        table = (
            (p.firstChild(),'spam'),
            (p.firstChild().next(),'@@eggs')
        )
        assert not p.isDirty(),p.h # Do not ignore this failure!
        for p2,h2 in table:
            assert p2.h == h2
            assert len(p2.b) > 10
    #@+node:ekr.20210905044728.12: *4* TestXXX.test__asis_shape_of_tree
    def test__asis_shape_of_tree(self):
        c = self.c
        if g.app.isExternalUnitTest:
            self.skipTest('Not for external tests: uses @<file> node.')
        h = '@asis unittest/at-asis-test.py'
        p = g.findNodeAnywhere(c,h)
        assert p, h
        table = (
            (p.firstChild(),'spam'),
            (p.firstChild().next(),'eggs')
        )
        assert not p.isDirty(),p.h # Do not ignore this failure!
        for p2,h2 in table:
            assert p2.h == h2
            assert len(p2.b) > 10
    #@+node:ekr.20210905044728.13: *4* TestXXX.test__auto_shape_of_tree
    def test__auto_shape_of_tree(self):
        c = self.c
        if g.app.isExternalUnitTest:
            self.skipTest('Not for external tests: uses @<file> node.')
        if g.in_bridge:
            self.skipTest('Not for TravisCI')
        h = '@auto unittest/at-auto-test.py'
        p = g.findNodeAnywhere(c,h)
        assert p, h
        table = (
            (p.firstChild(),'spam'),
            (p.firstChild().next(),'eggs')
        )
        assert not p.isDirty(), p.h # Do not ignore this failure!
        for p2, h2 in table:
            assert p2 and p2.h == h2, (p2 and p2.h, h2)
            assert len(p2.b) > 10
    #@+node:ekr.20210905044728.14: *4* TestXXX.test__clean__at_precheck
    def test__clean__at_precheck(self):
        c = self.c
        if g.app.isExternalUnitTest:
            self.skipTest('Not for external tests: uses @<file> node.')
        if g.in_bridge:
            self.skipTest('Not for TravisCI')
        h = '@clean unittest/at-clean-write-test.py'
        p = g.findNodeAnywhere(c,h)
        assert p, h
        #
        # Enable --trace=save
        at = c.atFileCommands
        # Get the correct file name.
        fn = p.anyAtFileNodeName()
        path = g.os_path_finalize_join(g.app.loadDir, '..', 'test', fn)
        assert g.os_path_exists(path), path
        #
        # Run the test.
        if 0:
            g.app.debug.append('save')
            print(f"Running {c.p.h}...\n")
        val = at.precheck(path, p)
        assert val is True
    #@+node:ekr.20210905044728.15: *4* TestXXX.test__clean__at_shouldPrompt__
    def test__clean__at_shouldPrompt__(self):
        c = self.c
        if g.app.isExternalUnitTest:
            self.skipTest('Not for external tests: uses @<file> node.')
        if g.in_bridge:
            self.skipTest('Not for TravisCI')
        h = '@clean unittest/at-clean-write-test.py'
        p = g.findNodeAnywhere(c,h)
        assert p, h
        #
        # Enable --trace=save
        at = c.atFileCommands
        # Get the correct file name.
        fn = p.anyAtFileNodeName()
        path = g.os_path_finalize_join(g.app.loadDir, '..', 'test', fn)
        assert g.os_path_exists(path), path
        #
        # Run the test.
        if 0:
            g.app.debug.append('save')
            print(f"Running {c.p.h}...\n")
        val = at.shouldPromptForDangerousWrite(path, p)
        assert val is False
    #@+node:ekr.20210905044728.16: *4* TestXXX.test__file_tex_bug
    def test__file_tex_bug(self):
        c = self.c
        import textwrap
        if g.app.isExternalUnitTest:
            self.skipTest('Not for external tests: uses @<file> node.')
        p = g.findNodeAnywhere(c,"@file unittest/tex-error.tex")
        assert(p)
        s1 = r"""\begin{document}
        << Document """
        s2 = r""">>
        % hidden comment
        \end{document}
        """
        s = s1 + s2
        s = textwrap.dedent(s)
        assert p.b == s, (repr(p.b), repr(s))
    #@+node:ekr.20210905044728.17: *4* TestXXX.test__thin_html_section_references
    def test__thin_html_section_references(self):
        c = self.c

        if g.app.isExternalUnitTest:
            self.skipTest('Not for external tests: uses @<file> node.')
        #
        # html uses block comments.  This is an important test.
        h = '@thin unittest/at-thin-html-test.html'
        p = g.findNodeAnywhere(c,h)
        assert p
        s = (
            '@language html\n\n<< ' +
            'a section reference >>\n\n' +
            'after.\n')
        assert p.b == s,'body failure'
    #@+node:ekr.20210905044728.18: *4* TestXXX.test__thin_shape_of_tree
    def test__thin_shape_of_tree(self):
        c = self.c
        if g.app.isExternalUnitTest:
            self.skipTest('Not for external tests: uses @<file> node.')
        h = '@thin unittest/at-thin-test.py'
        p = g.findNodeAnywhere(c,h)
        assert p
        table = (
            (p.firstChild(),'spam'),
            (p.firstChild().next(),'eggs')
        )
        assert not p.isDirty(),p.h # Do not ignore this failure!
        for p2,h2 in table:
            assert p2.h == h2
            assert len(p2.b) > 10
    #@+node:ekr.20210905044728.19: *4* TestXXX.test_at_directiveKind4
    def test_at_directiveKind4(self):
        c = self.c
        at=c.atFileCommands
        table = [
            ('@=',0,at.noDirective),
            ('@',0,at.atDirective),
            ('@ ',0,at.atDirective),
            ('@\t',0,at.atDirective),
            ('@\n',0,at.atDirective),
            ('@all',0,at.allDirective),
            ('    @all',4,at.allDirective),
            ("@c",0,at.cDirective),
            ("@code",0,at.codeDirective),
            ("@doc",0,at.docDirective),
            ("@end_raw",0,at.endRawDirective),
            ('@others',0,at.othersDirective),
            ('    @others',4,at.othersDirective),
            ("@raw",0,at.rawDirective),
        ]
        for name in g.globalDirectiveList:
            # Note: entries in g.globalDirectiveList do not start with '@'
            if name not in ('all','c','code','doc','end_raw','others','raw',):
                table.append(('@' + name,0,at.miscDirective),)

        for s,i,expected in table:
            result = at.directiveKind4(s,i)
            assert result == expected, '%d %s result: %s expected: %s' % (
                i,repr(s),at.sentinelName(result),at.sentinelName(expected))
    #@+node:ekr.20210905044728.20: *4* TestXXX.test_at_directiveKind4_new_
    def test_at_directiveKind4_new_(self):
        c = self.c
        at = c.atFileCommands
        table = (
            (at.othersDirective, '@others'),
            (at.othersDirective, '@others\n'),
            (at.othersDirective, '    @others'),
            (at.miscDirective,   '@tabwidth -4'),
            (at.miscDirective,   '@tabwidth -4\n'),
            (at.miscDirective,   '@encoding'),
            (at.noDirective,     '@encoding.setter'),
            (at.noDirective,     '@encoding("abc")'),
            (at.noDirective,     'encoding = "abc"'),
            (at.noDirective,     '@directive'), # A crucial new test.
        )
        for expected, s in table:
            result = at.directiveKind4(s, 0)
            assert expected == result, (expected, result, repr(s))
    #@+node:ekr.20210905044728.21: *4* TestXXX.test_at_get_setPathUa
    def test_at_get_setPathUa(self):
        c = self.c
        p = c.p
        at = c.atFileCommands
        at.setPathUa(p,'abc')
        d = p.v.tempAttributes
        d2 = d.get('read-path')
        val1 = d2.get('path')
        val2 = at.getPathUa(p)

        table = (
            ('d2.get',val1),
            ('at.getPathUa',val2),
        )
        for kind,val in table:
            assert val == 'abc','kind %s expected %s got %s' % (
                kind,'abc',val)
    #@+node:ekr.20210905044728.22: *4* TestXXX.test_at_isFileLike
    def test_at_isFileLike(self):
        c = self.c
        s1 = '''
        ###@+leo-ver=4
        ###@+node:#@file
        Line 1
        ###@-node:#@file
        ###@-leo
        '''

        s2 = '''
    #@verbatim
        #@+leo-ver=4-thin
    #@verbatim
        #@+node:ekr.20040707141957.13:#@thin
    #@verbatim
        #@-node:ekr.20040707141957.13:#@thin
    #@verbatim
        #@-leo
        '''

        at = c.atFileCommands
        assert at.isFileLike(s1),'fail1'
        assert not at.isFileLike(s2),'fail2'
    #@+node:ekr.20210905044728.23: *4* TestXXX.test_at_parseLeoSentinel
    def test_at_parseLeoSentinel(self):
        c = self.c
        at=c.atFileCommands # self is a dummy argument.
        table = (
            # start, end, new_df, isThin, encoding
            # pre 4.2 formats...
            ('#',   '',   False,  True, 'utf-8', '#@+leo-thin-encoding=utf-8.'),
            ('#',   '',   False,  False,'utf-8', '#@+leo-encoding=utf-8.'),
            # 4.2 formats...
            ('#',   '',   True,   True, 'utf-8',  '#@+leo-ver=4-thin-encoding=utf-8,.'),
            ('/*',  '*/', True,   True, 'utf-8',  r'\*@+leo-ver=5-thin-encoding=utf-8,.*/'),
            ('#',   '',   True,   True, 'utf-8',  '#@+leo-ver=5-thin'),
            ('#',   '',   True,   True, 'utf-16', '#@+leo-ver=5-thin-encoding=utf-16,.'),
        )
        try:
            for start, end, new_df, isThin, encoding, s in table:
                valid, new_df2, start2, end2, isThin2 = at.parseLeoSentinel(s)
                # g.trace('start',start,'end',repr(end),'len(s)',len(s))
                assert valid, s
                assert new_df == new_df2, s
                assert isThin == isThin2, s
                assert end == end2, (end, end2, s)
                assert at.encoding == encoding, s
        finally:
            at.encoding = 'utf-8'
    #@+node:ekr.20210905044728.24: *4* TestXXX.test_at_remove
    def test_at_remove(self):
        c = self.c
        import os

        at = c.atFileCommands
        exists = g.os_path_exists

        path = g.os_path_join(g.app.testDir,'xyzzy')
        if exists(path):
            os.remove(path)

        assert not exists(path)
        assert not at.remove(path)

        f = open(path,'w')
        f.write('test')
        f.close()

        assert exists(path)
        assert at.remove(path)
        assert not exists(path)
    #@+node:ekr.20210905044728.25: *4* TestXXX.test_at_replaceFile_different_contents_
    def test_at_replaceFile_different_contents_(self):
        c = self.c
        at = c.atFileCommands
        encoding = 'utf-8'
        exists = g.os_path_exists
        at.outputFileName = None
        at.targetFileName = g.os_path_join(g.app.testDir,'xyzzy2')
        try:
            # Create both paths (different contents)
            table = (at.targetFileName,)
            at.outputContents = contents = g.toUnicode('test contents')
            for fn in table:
                if fn and exists(fn):
                    os.remove(fn)
                assert not exists(fn)
                f = open(fn,'w')
                s = 'test %s' % fn
                f.write(s)
                f.close()
                assert exists(fn),fn
            at.toString = False # Set by execute script stuff.
            at.shortFileName = at.targetFileName
            val = at.replaceFile(contents, encoding, fn, at.root)
            assert val
            if 0:
                print('%s exists %s' % (at.outputFileName,exists(at.outputFileName)))
                print('%s exists %s' % (at.targetFileName,exists(at.targetFileName)))
            assert not exists(at.outputFileName), 'oops, output file exists'
            assert exists(at.targetFileName), 'oops, target file does not exist'
            f = open(at.targetFileName)
            s = f.read()
            f.close()
            assert s == contents,s
        finally:
            if 1:
                for fn in (at.outputFileName,at.targetFileName):
                    if fn and exists(fn):
                        os.remove(fn)
    #@+node:ekr.20210905044728.26: *4* TestXXX.test_at_replaceFile_no_target_file_
    def test_at_replaceFile_no_target_file_(self):
        c = self.c
        at = c.atFileCommands
        encoding = 'utf-8'
        exists = g.os_path_exists
        at.outputFileName = None # g.os_path_join(g.app.testDir,'xyzzy1.txt')
        at.targetFileName = g.os_path_join(g.app.testDir,'xyzzy2.txt')
        # Remove both files.
        for fn in (at.outputFileName,at.targetFileName):
            if fn and exists(fn):
                os.remove(fn)
        try:
            # Create the output file or contents.
            at.outputContents = contents = g.toUnicode('test output')
            at.shortFileName = at.targetFileName
            val = at.replaceFile(contents, encoding, fn, at.root)
            assert not val
            if 0:
                print('%s exists %s' % (at.outputFileName,exists(at.outputFileName)))
                print('%s exists %s' % (at.targetFileName,exists(at.targetFileName)))
            assert not exists(at.outputFileName),at.outputFileName
            assert exists(at.targetFileName),at.targetFileName
            f = open(at.targetFileName)
            s = f.read()
            f.close()
            assert s == contents,'%s len(%s)' % (fn,len(s))
        finally:
            if 1:
                for fn in (at.outputFileName,at.targetFileName):
                    if fn and exists(fn):
                        os.remove(fn)
    #@+node:ekr.20210905044728.27: *4* TestXXX.test_at_replaceFile_same_contents_
    def test_at_replaceFile_same_contents_(self):
        c = self.c
        at = c.atFileCommands
        encoding = 'utf-8'
        exists = g.os_path_exists
        at.outputFileName = None
        at.targetFileName = g.os_path_join(g.app.testDir,'xyzzy2')
        # Create both paths (identical contents)
        contents = g.toUnicode('test contents')
        try:
            table = (at.targetFileName,)
            at.outputContents = contents
            for fn in table:
                if fn and exists(fn):
                    os.remove(fn)
                assert not exists(fn)
                f = open(fn,'w')
                f.write(contents)
                f.close()
                assert exists(fn)
            at.toString = False # Set by execute script stuff.
            at.shortFileName = at.targetFileName
            assert not at.replaceFile(contents, encoding, fn, at.root)
            if 0:
                print('%s exists %s' % (at.outputFileName,exists(at.outputFileName)))
                print('%s exists %s' % (at.targetFileName,exists(at.targetFileName)))
            assert not exists(at.outputFileName)
            assert exists(at.targetFileName)
            f = open(at.targetFileName)
            s = f.read()
            f.close()
            assert s == contents,contents
        finally:
            if 1:
                for fn in (at.outputFileName,at.targetFileName):
                    if fn and exists(fn):
                        os.remove(fn)
    #@+node:ekr.20210905044728.28: *4* TestXXX.test_at_scanAllDirectives
    def test_at_scanAllDirectives(self):
        c = self.c
        # This will work regardless of where this method is.
        ### @language python
        ### @tabwidth -4
        # @path xyzzy # Creates folder called xyzzy: interferes with other unit tests.
        ### @pagewidth 120

        d = c.atFileCommands.scanAllDirectives(c.p)

        assert d.get('language') == 'python'
        assert d.get('tabwidth') == -4
        # assert d.get('path').endswith('xyzzy')
        assert d.get('pagewidth') == 120
    #@+node:ekr.20210905044728.29: *4* TestXXX.test_at_scanAllDirectives_minimal_
    def test_at_scanAllDirectives_minimal_(self):
        c = self.c
        at = c.atFileCommands
        d = at.scanAllDirectives(c.p)
        assert d  ###
    #@+node:ekr.20210905044728.30: *4* TestXXX.test_at_write_using_comment
    def test_at_write_using_comment(self):
        c = self.c
        p = c.p
        at = c.atFileCommands
        expected = '''\
        /*@+leo-ver=5-thin*/
        /*@+node:GNX: * root*/
        /*@@language c*/
        #ifdef COMMENT
        /*@@comment /* */ */
        #endif
        /*@@tabwidth 4*/
        /*@@lineending crlf*/

        /*@+others*/
        /*@-others*/

        /*@+< < Get LRR Task > >*/
        /*@+node:GNX: ** < < Get LRR Task > >*/
        /*@-< < Get LRR Task > >*/
        /*@+< < Start LRR > >*/
        /*@+node:GNX: ** < < Start LRR > >*/
        /*@-< < Start LRR > >*/
        /*@-leo*/
        '''.replace('AT','#@').replace('> >', '>>').replace('< <', '<<')

        child = p.firstChild()
        result = at.atFileToString(child)
        result = re.sub(r'@\+node:(.+):', '@+node:GNX:', result)
        if result != expected: # Show unexpected mismatches.
            g.printObj(result, tag='result')
            g.printObj(expected, tag='expected')
            result = g.splitLines(result)
            expected = g.splitLines(expected)
            print('len(expected): %s, len(result): %s' % (len(expected), len(result)))
            for i, s in enumerate(result):
                if expected[i] != result[i]:
                    print(i)
                    print('expected: %r' % expected[i])
                    print('result:   %r' % result[i])
                    break
        elif 0:
            g.printObj(result, tag='result')

        assert result == expected
    #@+node:ekr.20210905044728.31: *4* TestXXX.test_at_writeOneAtShadowNode
    def test_at_writeOneAtShadowNode(self):
        c = self.c
        p = c.p
        at = c.atFileCommands
        x = c.shadowController
        # changed = c.changed
        child = p.firstChild()
        # s = child.b

        try:
            child.setHeadString('@shadow unittest/test_1.py')
            fn = 'unittest/test_1.py'
            shadow_fn = x.shadowPathName(fn)
            shadow_dir = x.shadowDirName(fn)
            x.makeShadowDirectory(shadow_dir)
            if g.os_path_exists(shadow_fn):
                os.remove(shadow_fn)
            at.writeOneAtShadowNode(child, testing=True)
            assert at.startSentinelComment == '#','startSentinelComment: %s' % (
                repr(at.startSentinelComment))
            assert at.endSentinelComment == '','endSentinelComment: %s' % (
                repr(at.endSentinelComment))
            if 0:
                print('public...\n',at.public_s)
                print('private...\n',at.private_s)
            at.writeOneAtShadowNode(child, testing=False)
            assert g.os_path_exists(shadow_fn),'not found: %s' % shadow_fn
            # No need to remove this: it's in the unittest directory.
            # os.remove(shadow_fn)
        finally:
            child.setHeadString('@@shadow unittest/test_1.py')
            c.clearChanged()
    #@+node:ekr.20210905044728.32: *4* TestXXX.test_fast_readWithElementTree
    def test_fast_readWithElementTree(self):
        c = self.c
        """This code tests the translation table and associated logic."""
        import leo.core.leoFileCommands as leoFileCommands
        table = leoFileCommands.FastRead(c, {}).translate_table
        s = chr(0) + "a" + chr(0) + "b"
        assert len(s) == 4, len(s)
        s = s.translate(table)
        assert len(s) == 2, len(s)
    #@+node:ekr.20210905044728.33: *4* TestXXX.test_utf_16_encoding
    def test_utf_16_encoding(self):
        c = self.c
        h = '@file unittest/utf-16-test.txt'
        p = g.findNodeAnywhere(c,h)
        s = 'Test of utf-16.'
        assert p,h
        # It's hard to test the utf-16 text directly.
        assert p.b
        assert p.b.find(s) > -1
        assert len(p.b)==66,len(p.b)
    #@+node:ekr.20210905044728.34: *4* TestXXX.test_verbatim_sentinel
    def test_verbatim_sentinel(self):
        c = self.c
        # Here is something that should generate a verbtim sentinel::

    #@verbatim
        #@+leo-encoding=iso-8859-1.

        # The length of this node should remain constant.

        assert len(c.p.b) == 175, len(c.p.b)
    #@-others
#@-others
#@-leo

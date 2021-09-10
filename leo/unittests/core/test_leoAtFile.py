# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20210901172411.1: * @file ../unittests/core/test_leoAtFile.py
#@@first
"""Tests of leoAtFile.py"""
import os
import tempfile
import textwrap
from leo.core import leoGlobals as g
from leo.core import leoBridge
from leo.core.leoTest2 import LeoUnitTest
import leo.core.leoFileCommands as leoFileCommands

#@+others
#@+node:ekr.20210901172446.1: ** class TestAtFile(LeoUnitTest)
class TestAtFile(LeoUnitTest):
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
    #@+node:ekr.20210905052021.19: *3* TestAtFile.test_at_directiveKind4
    def test_at_directiveKind4(self):
        c = self.c
        at = c.atFileCommands
        at.language = 'python' # Usually set by atFile read/write logic.
        table = [
            ('@=', 0, at.noDirective),
            ('@', 0, at.atDirective),
            ('@ ', 0, at.atDirective),
            ('@\t', 0, at.atDirective),
            ('@\n', 0, at.atDirective),
            ('@all', 0, at.allDirective),
            ('    @all', 4, at.allDirective),
            ("@c",0, at.cDirective),
            ("@code",0, at.codeDirective),
            ("@doc",0, at.docDirective),
            ("@end_raw", 0, at.endRawDirective),
            ('@others', 0, at.othersDirective),
            ('    @others', 4, at.othersDirective),
            ("@raw", 0, at.rawDirective),
        ]
        for name in g.globalDirectiveList:
            # Note: entries in g.globalDirectiveList do not start with '@'
            if name not in ('all','c','code','doc','end_raw','others','raw',):
                table.append(('@' + name,0,at.miscDirective),)
        for s, i, expected in table:
            result = at.directiveKind4(s,i)
            self.assertEqual(result, expected, msg=f"i: {i}, s: {s!r}")
    #@+node:ekr.20210905052021.20: *3* TestAtFile.test_at_directiveKind4_new
    def test_at_directiveKind4_new(self):
        c = self.c
        at = c.atFileCommands
        at.language = 'python' # Usually set by atFile read/write logic.
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
            self.assertEqual(expected, result, msg=repr(s))
    #@+node:ekr.20210905052021.21: *3* TestAtFile.test_at_get_setPathUa
    def test_at_get_setPathUa(self):
        c = self.c
        p = c.p
        at = c.atFileCommands
        at.setPathUa(p, 'abc')
        d = p.v.tempAttributes
        d2 = d.get('read-path')
        val1 = d2.get('path')
        val2 = at.getPathUa(p)
        table = (
            ('d2.get',val1),
            ('at.getPathUa',val2),
        )
        for kind, val in table:
            self.assertEqual(val, 'abc', msg=kind)
    #@+node:ekr.20210905052021.23: *3* TestAtFile.test_at_parseLeoSentinel
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
                self.assertEqual(new_df, new_df2, msg=repr(s))
                self.assertEqual(isThin, isThin2, msg=repr(s))
                self.assertEqual(end, end2, msg=repr(s))
                self.assertEqual(at.encoding, encoding, msg=repr(s))
        finally:
            at.encoding = 'utf-8'
    #@+node:ekr.20210905052021.24: *3* TestAtFile.test_at_remove
    def test_at_remove(self):
        c = self.c
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
    #@+node:ekr.20210905052021.25: *3* TestAtFile.test_at_replaceFile_different_contents
    def test_at_replaceFile_different_contents(self):
        c = self.c
        at = c.atFileCommands
        # Duplicate init logic...
        at.initCommonIvars()
        at.scanAllDirectives(c.p) 
        encoding = 'utf-8'
        try:
            # https://stackoverflow.com/questions/23212435
            f = tempfile.NamedTemporaryFile(delete=False, encoding=encoding, mode='w')
            fn = f.name
            contents = 'test contents'
            val = at.replaceFile(contents, encoding, fn, at.root)
            assert val, val
        finally:
            f.close()
            os.unlink(f.name)
    #@+node:ekr.20210905052021.26: *3* TestAtFile.test_at_replaceFile_no_target_file
    def test_at_replaceFile_no_target_file(self):
        c = self.c
        at = c.atFileCommands
        # Duplicate init logic...
        at.initCommonIvars()
        at.scanAllDirectives(c.p) 
        encoding = 'utf-8'
        at.outputFileName = None  # The point of this test, but I'm not sure it matters.
        try:
            # https://stackoverflow.com/questions/23212435
            f = tempfile.NamedTemporaryFile(delete=False, encoding=encoding, mode='w')
            fn = f.name
            contents = 'test contents'
            val = at.replaceFile(contents, encoding, fn, at.root)
            assert val, val
        finally:
            f.close()
            os.unlink(f.name)
    #@+node:ekr.20210905052021.27: *3* TestAtFile.test_at_replaceFile_same_contents
    def test_at_replaceFile_same_contents(self):
        c = self.c
        at = c.atFileCommands
        # Duplicate init logic...
        at.initCommonIvars()
        at.scanAllDirectives(c.p) 
        encoding = 'utf-8'
        try:
            # https://stackoverflow.com/questions/23212435
            f = tempfile.NamedTemporaryFile(delete=False, encoding=encoding, mode='w')
            fn = f.name
            contents = 'test contents'
            f.write(contents)
            f.flush()
            val = at.replaceFile(contents, encoding, fn, at.root)
            assert not val, val
        finally:
            f.close()
            os.unlink(f.name)
    #@+node:ekr.20210905052021.28: *3* TestAtFile.test_at_scanAllDirectives
    def test_at_scanAllDirectives(self):
        c = self.c
        d = c.atFileCommands.scanAllDirectives(c.p)
        # These are the commander defaults, without any settings.
        self.assertEqual(d.get('language'), 'python')
        self.assertEqual(d.get('tabwidth'), -4)
        self.assertEqual(d.get('pagewidth'), 132)
    #@+node:ekr.20210905052021.29: *3* TestAtFile.test_at_scanAllDirectives_minimal_
    def test_at_scanAllDirectives_minimal_(self):
        c = self.c
        d = c.atFileCommands.scanAllDirectives(c.p)
        assert d
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
            self.assertEqual(p1.h, "@file 1_renamed")
            self.assertEqual(p1.b, "b_1_changed")
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
    #@+node:ekr.20210905052021.32: *3* TestAtFile.test_fast_readWithElementTree
    def test_fast_readWithElementTree(self):
        # Test the translation table and associated logic.
        c = self.c
        table = leoFileCommands.FastRead(c, {}).translate_table
        s = chr(0) + "a" + chr(0) + "b"
        self.assertEqual(len(s), 4)
        s = s.translate(table)
        self.assertEqual(len(s), 2)
    #@-others
#@-others
#@-leo

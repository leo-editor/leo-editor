# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20210902092024.1: * @file ../unittests/core/test_leoShadow.py
#@@first
"""Tests of leoShapdw.py"""

import glob
import os
from leo.core import leoGlobals as g
from leo.core.leoShadow import ShadowController
from leo.core.leoTest2 import LeoUnitTest

#@+others
#@+node:ekr.20080709062932.2: ** class TestShadow (LeoUnitTest)
class TestShadow(LeoUnitTest):
    #@+others
    #@+node:ekr.20080709062932.8: *3* TestShadow.setUp & helpers
    def setUp(self):
        """AtShadowTestCase.setup."""
        self.skipTest('Not ready yet')
        super().setUp()
        c, p = self.c, self.c.p
        delims = '#', '', '' ###
        self.shadow_controller = ShadowController(c)
        self.marker = self.shadow_controller.Marker(delims)
        old = self.findNode(c, p, 'old')
        new = self.findNode(c, p, 'new')
        self.old_private_lines = self.makePrivateLines(old)
        self.new_private_lines = self.makePrivateLines(new)
        self.old_public_lines = self.makePublicLines(self.old_private_lines)
        self.new_public_lines = self.makePublicLines(self.new_private_lines)
        # Change node:new to node:old in all sentinel lines.
        self.expected_private_lines = self.mungePrivateLines(
            self.new_private_lines, 'node:new', 'node:old')
    #@+node:ekr.20080709062932.19: *4* TestShadow.findNode
    def findNode(self, c, p, headline):
        """Return the node in p's subtree with given headline."""
        p = g.findNodeInTree(c, p, headline)
        if not p:
            self.fail(f"Node not found: {headline}")
        return p
    #@+node:ekr.20080709062932.20: *4* TestShadow.createSentinelNode
    def createSentinelNode(self, root, p):
        """Write p's tree to a string, as if to a file."""
        h = p.h
        p2 = root.insertAsLastChild()
        p2.setHeadString(h + '-sentinels')
        return p2
    #@+node:ekr.20080709062932.21: *4* TestShadow.makePrivateLines
    def makePrivateLines(self, p):
        """Return a list of the lines of p containing sentinels."""
        at = self.c.atFileCommands
        # A hack: we want to suppress gnx's *only* in @+node sentinels,
        # but we *do* want sentinels elsewhere.
        at.at_shadow_test_hack = True
        try:
            s = at.atFileToString(p, sentinels=True)
        finally:
            at.at_shadow_test_hack = False
        return g.splitLines(s)
    #@+node:ekr.20080709062932.22: *4* TestShadow.makePublicLines
    def makePublicLines(self, lines):
        """Return the public lines in lines."""
        lines, junk = self.shadow_controller.separate_sentinels(lines, self.marker)
        return lines
    #@+node:ekr.20080709062932.23: *4* TestShadow.mungePrivateLines
    def mungePrivateLines(self, lines, find, replace):
        """Change the 'find' the 'replace' pattern in sentinel lines."""
        marker = self.marker
        i, results = 0, []
        while i < len(lines):
            line = lines[i]
            if marker.isSentinel(line):
                new_line = line.replace(find, replace)
                results.append(new_line)
                if marker.isVerbatimSentinel(line):
                    i += 1
                    if i < len(lines):
                        line = lines[i]
                        results.append(line)
                    else:
                        self.shadow_controller.verbatim_error()
            else:
                results.append(line)
            i += 1
        return results
    #@+node:ekr.20080709062932.10: *3* TestShadow.runTest
    def xx_runTest(self): ###, define_g=True):
        """AtShadowTestCase.runTest."""
        self.fail('Not ready yet')  ###
        p = self.c.p
        results = self.shadow_controller.propagate_changed_lines(
            self.new_public_lines, self.old_private_lines, self.marker, p=p)
        self.assertEqual(results, self.expected_private_lines)
        ###
            # if results != self.expected_private_lines:
                # g.pr(p.h)
                # for aList, tag in (
                    # (results, 'results'),
                    # (self.expected_private_lines, 'expected_private_lines')
                # ):
                    # g.pr(f"{tag}...")
                    # for i, line in enumerate(aList):
                        # g.pr(f"{i:3} {line!r}")
                    # g.pr('-' * 40)
    #@+node:ekr.20210902210552.2: *3* TestShadow.test_class_Marker_getDelims
    def test_class_Marker_getDelims(self):
        c = self.c
        x = c.shadowController
        table = (
            ('python','#',''),
            ('c','//',''),
            ('html','<!--','-->'),
            ('xxxx','#--unknown-language--',''),
        )
        for language,delim1,delim2 in table:
            delims = g.set_delims_from_language(language)
            marker = x.Marker(delims)
            result = marker.getDelims()
            expected = delim1,delim2
            assert result==expected,'language %s expected %s got %s' % (
                language,expected,result)
    #@+node:ekr.20210902210552.3: *3* TestShadow.test_class_Marker_isSentinel
    def test_class_Marker_isSentinel(self):
        c = self.c
        x = c.shadowController
        table = (
            ('python','abc',False),
            ('python','#abc',False),
            ('python','#@abc',True),
            ('python','@abc#',False),
            ('c','abc',False),
            ('c','//@',True),
            ('c','// @abc',False),
            ('c','/*@ abc */',True),
            ('c','/*@ abc',False),
            ('html','#@abc',False),
            ('html','<!--abc-->',False),
            ('html','<!--@ abc -->',True),
            ('html','<!--@ abc ->',False),
            ('xxxx','#--unknown-language--@',True)
        )
        for language,s,expected in table:
            delims = g.set_delims_from_language(language)
            marker = x.Marker(delims)
            result = marker.isSentinel(s)
            assert result==expected,'language %s s: %s expected %s got %s' % (
                language,s,expected,result)
    #@+node:ekr.20210902210552.4: *3* TestShadow.test_class_Marker_isVerbatimSentinel
    def test_class_Marker_isVerbatimSentinel(self):
        c = self.c
        x = c.shadowController
        table = (
            ('python','abc',False),
            ('python','#abc',False),
            ('python','#verbatim',False),
            ('python','#@verbatim',True),
            ('c','abc',False),
            ('c','//@',False),
            ('c','//@verbatim',True),
            ('html','#@abc',False),
            ('html','<!--abc-->',False),
            ('html','<!--@verbatim -->',True),
            ('xxxx','#--unknown-language--@verbatim',True)
        )
        for language,s,expected in table:
            delims = g.set_delims_from_language(language)
            marker = x.Marker(delims)
            result = marker.isVerbatimSentinel(s)
            assert result==expected,'language %s s: %s expected %s got %s' % (
                language,s,expected,result)
    #@+node:ekr.20210902210552.5: *3* TestShadow.test_x_baseDirName
    def test_x_baseDirName(self):
        c = self.c
        x = c.shadowController
        path = x.baseDirName()
        expected = g.os_path_dirname(g.os_path_abspath(g.os_path_join(c.fileName())))
        assert path == expected,'\nexpected: %s\ngot     : %s' % (expected,path)
    #@+node:ekr.20210902210552.6: *3* TestShadow.test_x_dirName
    def test_x_dirName(self):
        c = self.c
        x = c.shadowController
        filename = 'xyzzy'
        path = x.dirName(filename)
        expected = g.os_path_dirname(g.os_path_abspath(
            g.os_path_join(g.os_path_dirname(c.fileName()),filename)))
        assert path == expected,'\nexpected: %s\ngot     : %s' % (expected,path)
    #@+node:ekr.20210902210552.7: *3* TestShadow.test_x_findAtLeoLine
    def test_x_findAtLeoLine(self):
        c = self.c
        x = c.shadowController
        table = (
            ('c',('//@+leo','a'),                   '//@+leo'),
            ('c',('//@first','//@+leo','b'),        '//@+leo'),
            ('c',('/*@+leo*/','a'),                 '/*@+leo*/'),
            ('c',('/*@first*/','/*@+leo*/','b'),    '/*@+leo*/'),
            ('python',('#@+leo','a'),               '#@+leo'),
            ('python',('#@first','#@+leo','b'),     '#@+leo'),
            ('error',('',),''),
            ('html',('<!--@+leo-->','a'),                '<!--@+leo-->'),
            ('html',('<!--@first-->','<!--@+leo-->','b'),'<!--@+leo-->'),
        )
        for language,lines,expected in table:
            result = x.findLeoLine(lines)
            assert expected==result, 'language %s expected %s got %s lines %s' % (
                language,expected,result,'\n'.join(lines))
    #@+node:ekr.20210902210552.8: *3* TestShadow.test_x_makeShadowDirectory
    def test_x_makeShadowDirectory(self):
        c = self.c
        x = c.shadowController
        #@+others
        #@+node:ekr.20210902210953.1: *4* TestShadow.deleteShadowDir
        def deleteShadowDir(shadowDir):
            if g.os_path_exists(shadow_dir):
                files = g.os_path_abspath(g.os_path_join(shadow_dir,"*.*"))
                files = glob.glob(files)
                for z in files:
                    if z != shadow_dir:
                        os.unlink(z)
                os.rmdir(shadow_dir)
                assert not os.path.exists(shadow_dir),'still exists: %s' % shadow_dir
        #@-others
        shadow_fn  = x.shadowPathName('unittest/xyzzy/test.py')
        shadow_dir = x.shadowDirName('unittest/xyzzy/test.py')
        if g.os_path_exists(shadow_fn):
            g.utils_remove(shadow_fn,verbose=True)
            # assert not os.path.exists(shadow_fn),'still exists: %s' % shadow_fn
            if os.path.exists(shadow_fn):
                # Fix bug #512: Just skip this test.
                self.skipTest('Can not delete the directory.')
        deleteShadowDir(shadow_dir)
        x.makeShadowDirectory(shadow_dir)
        assert os.path.exists(shadow_dir)
        deleteShadowDir(shadow_dir)
    #@+node:ekr.20210902210552.9: *3* TestShadow.test_x_markerFromFileLines
    def test_x_markerFromFileLines(self):
        c = self.c
        x = c.shadowController
        # Add -ver=4 so at.parseLeoSentinel does not complain.
        table = (
            ('c',('//@+leo-ver=4','a'),                   '//',''),
            ('c',('//@first','//@+leo-ver=4','b'),        '//',''),
            ('c',('/*@+leo-ver=4*/','a'),                 '/*','*/'),
            ('c',('/*@first*/','/*@+leo-ver=4*/','b'),    '/*','*/'),
            ('python',('#@+leo-ver=4','a'),               '#',''),
            ('python',('#@first','#@+leo-ver=4','b'),     '#',''),
            ('error',('',),             '#--unknown-language--',''),
            ('html',('<!--@+leo-ver=4-->','a'),                '<!--','-->'),
            ('html',('<!--@first-->','<!--@+leo-ver=4-->','b'),'<!--','-->'),
        )

        for language,lines,delim1,delim2 in table:
            ### s = x.findLeoLine(lines)
            lines_s = '\n'.join(lines)
            marker = x.markerFromFileLines(lines,'test-file-name')
            result1,result2 = marker.getDelims()
            self.assertEqual(delim1, result1, msg=f"language: {language} {lines_s}")
            self.assertEqual(delim2, result2, msg=f"language: {language} {lines_s}")
    #@+node:ekr.20210902210552.10: *3* TestShadow.test_x_markerFromFileName
    def test_x_markerFromFileName(self):
        c = self.c
        x = c.shadowController
        table = (
            ('ini',';','',),
            ('c','//',''),
            ('h','//',''),
            ('py','#',''),
            ('xyzzy','#--unknown-language--',''),
        )
        for ext,delim1,delim2 in table:
            filename = 'x.%s' % ext
            marker = x.markerFromFileName(filename)
            result1,result2 = marker.getDelims()
            assert delim1==result1, 'ext=%s, got %s, expected %s' % (
                ext,delim1,result1)
            assert delim2==result2, 'ext=%s, got %s, expected %s' % (
                ext,delim2,result2)
    #@+node:ekr.20210902210552.11: *3* TestShadow.test_x_pathName
    def test_x_pathName(self):
        c = self.c
        x = c.shadowController
        filename = 'xyzzy'
        path = x.pathName(filename)
        expected = g.os_path_abspath(g.os_path_join(x.baseDirName(),filename))
        assert path == expected,'\nexpected: %s\ngot     : %s' % (expected,path)
    #@+node:ekr.20210902210552.12: *3* TestShadow.test_x_replaceFileWithString
    def test_x_replaceFileWithString(self):
        c = self.c
        x = c.shadowController
        s = 'abc'
        encoding = 'utf-8'
        fn = '../test/unittest/replaceFileWithStringTestFile.py'
        path = g.os_path_abspath(g.os_path_join(g.app.loadDir,fn))
        x.replaceFileWithString(encoding, path, s)
        f = open(path)
        s2 = f.read()
        f.close()
        assert s == s2
    #@+node:ekr.20210902210552.13: *3* TestShadow.test_x_replaceFileWithString_2
    def test_x_replaceFileWithString_2(self):
        c = self.c
        x = c.shadowController
        encoding = 'utf-8'
        fn = 'does/not/exist'
        assert not g.os_path_exists(fn)
        assert not x.replaceFileWithString(encoding, fn, 'abc')
    #@+node:ekr.20210902210552.14: *3* TestShadow.test_x_shadowDirName
    def test_x_shadowDirName(self):
        c = self.c
        x = c.shadowController
        subdir = c.config.getString('shadow_subdir') or '.leo_shadow'
        # prefix = c.config.getString('shadow_prefix') or ''
        filename = 'xyzzy'
        path = x.shadowDirName(filename)
        expected = g.os_path_abspath(g.os_path_join(
            g.os_path_dirname(c.fileName()), subdir))
        self.assertEqual(path, expected)
    #@+node:ekr.20210902210552.15: *3* TestShadow.test_x_shadowPathName
    def test_x_shadowPathName(self):
        c = self.c
        x = c.shadowController
        subdir = c.config.getString('shadow_subdir') or '.leo_shadow'
        prefix = c.config.getString('shadow_prefix') or ''
        filename = 'xyzzy'
        path = x.shadowPathName(filename)
        expected = g.os_path_abspath(g.os_path_join(
            g.os_path_dirname(c.fileName()),subdir,prefix+filename))
        assert path == expected,'\nexpected: %s\ngot     : %s' % (expected,path)
    #@-others
#@-others
#@-leo

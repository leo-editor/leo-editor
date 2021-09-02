# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20210901140718.1: * @file ../unittests/syntax_tests.py
#@@first
"""Basic tests for Leo"""
# pylint: disable=no-member
import glob
from leo.core import leoGlobals as g
from leo.core.leoTest2 import LeoUnitTest
#@+others
#@+node:ekr.20210901140855.1: ** class SyntaxTest(BaseUnitTest)
class SyntaxTest(BaseUnitTest):
    """Unit tests checking syntax of Leo files."""
    #@+others
    #@+node:ekr.20210901140645.1: *3* SyntaxTest.tests...
    #@+node:ekr.20210901140645.21: *4* SyntaxTest.test_syntax_of_all_files
    def test_syntax_of_all_files(self):
        c = self.c
        failed,n = [],0
        skip_tuples = (
            ('extensions','asciidoc.py'),
        )
        join = g.os_path_finalize_join
        skip_list = [join(g.app.loadDir,'..',a,b) for a,b in skip_tuples]
        for theDir in ('core', 'external', 'extensions', 'plugins', 'scripts', 'test'):
            path = g.os_path_finalize_join(g.app.loadDir,'..',theDir)
            assert g.os_path_exists(path),path
            aList = glob.glob(g.os_path_join(path,'*.py'))
            if g.isWindows:
                aList = [z.replace('\\','/') for z in aList]
            for z in aList:
                if z in skip_list:
                    pass # print('%s: skipped: %s' % (p.h,z))
                else:
                    n += 1
                    fn = g.shortFileName(z)
                    s,e = g.readFileIntoString(z)
                    if not c.testManager.checkFileSyntax(fn,s,reraise=False,suppress=False):
                        failed.append(z)
        assert not failed,'failed %s\n' % g.listToString(failed)
    #@+node:ekr.20210901140645.22: *4* SyntaxTest.test_syntax_of_setup_py
    def test_syntax_of_setup_py(self):
        c = self.c
        fn = g.os_path_finalize_join(g.app.loadDir, '..', '..', 'setup.py')
        # Only run this test if setup.py exists: it may not in the actual distribution.
        if not g.os_path_exists(fn):
            self.skipTest('setup.py not found')
        s, e = g.readFileIntoString(fn)
        c.testManager.checkFileSyntax(fn, s, reraise=True, suppress=False)
    #@-others
#@-others
#@-leo

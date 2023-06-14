#@+leo-ver=5-thin
#@+node:ekr.20220822082042.1: * @file ../unittests/core/test_leoImport.py
"""Tests of leoImport.py"""

import io
import textwrap
from leo.unittests.test_importers import BaseTestImporter
StringIO = io.StringIO

#@+others
#@+node:ekr.20220822082042.2: ** class TestLeoImport(BaseTestImporter)
class TestLeoImport(BaseTestImporter):
    """Test cases for leoImport.py"""
    #@+others
    #@+node:ekr.20220822082042.3: *3* TestLeoImport.test_mind_map_importer
    def test_mind_map_importer(self):

        c = self.c
        target = c.p.insertAfter()
        target.h = 'target'
        from leo.core.leoImport import MindMapImporter
        x = MindMapImporter(c)
        s = textwrap.dedent("""\
            header1, header2, header3
            a1, b1, c1
            a2, b2, c2
        """)
        f = StringIO(s)
        x.scan(f, target)

        # #2760: These results ignore way too much.
        
        # Don't call run_test.
        self.check_outline(target, (
            (0, '',  # Ignore the top-level headline.
                ''
            ),
            (1, 'a1', ''),
            (1, 'a2', ''),
        ))
    #@+node:ekr.20221104065722.1: *3* TestLeoImport.test_parse_body
    def test_parse_body(self):

        c = self.c
        x = c.importCommands
        target = c.p.insertAfter()
        target.h = 'target'
        target.b = textwrap.dedent(
        """
            import os

            def macro(func):
                def new_func(*args, **kwds):
                    raise RuntimeError('blah blah blah')
            return new_func
        """).strip() + '\n'
        x.parse_body(target)

        expected_results = (
            (0, '',  # Ignore the top-level headline.
                '<< target: preamble >>\n'
                '@others\n'
                'return new_func\n'
                '@language python\n'
                '@tabwidth -4\n'
            ),
            (1, '<< target: preamble >>',
                'import os\n'
                '\n'
            ),
            (1, 'def macro',
                'def macro(func):\n'
                '    @others\n'
            ),
            (2, 'def new_func',
                'def new_func(*args, **kwds):\n'
                "    raise RuntimeError('blah blah blah')\n"
            ),
        )
        # Don't call run_test.
        self.check_outline(target, expected_results)
    #@+node:ekr.20230613235653.1: *3* TestLeoImport.test_recursive_import
    def test_recursive_import(self):
        from leo.core import leoImport
        c = self.c
        dir_ = r'C:/Repos/ekr-mypy2/mypy'
        root = c.rootPosition()
        root.deleteAllChildren()
        p1 = root.insertAsLastChild()
        p2 = root.insertAsLastChild()
        p3 = root.insertAsLastChild()
        p4 = root.insertAsLastChild()
        p1.h = dir_
        p2.h = f"{dir_}/test"
        p3.h = '@clean x.py'
        p4.h = '@clean y.py'
        table = (
            (root, 'root'),
            (p1, '@path mypy'),
            (p2, '@path test'),
            (p3, '@clean x.py'),
            (p4, '@clean y.py'),
        )
        x = leoImport.RecursiveImportController(c,
            dir_=dir_,
            kind='@clean',
            recursive=True,
            safe_at_file = False,
            theTypes=['.py'],
            verbose=False,
        )
        for p, expected in table:
            x.minimize_headline(p)
            self.assertEqual(p.h, expected)
    #@-others
#@-others
#@-leo

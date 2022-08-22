# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20220822082042.1: * @file ../unittests/core/test_leoImport.py
#@@first
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
        # self.dump_tree(target, tag='Actual results...')

        # #2760: These results ignore way too much.

        self.check_outline(target, (
            (0, '',  # check_outline ignores the top-level headline.
                ''
            ),
            (1, 'a1', ''),
            (1, 'a2', ''),
        ))
    #@-others
#@-others
#@-leo

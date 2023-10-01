#@+leo-ver=5-thin
#@+node:ekr.20220822082042.1: * @file ../unittests/core/test_leoImport.py
"""Tests of leoImport.py"""

import io
import os
import textwrap
from leo.unittests.test_importers import BaseTestImporter
from leo.core import leoImport
from leo.core import leoGlobals as g
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
    #@+node:ekr.20221104065722.1: *3* TestLeoImport.test_python_importer_parse_body
    def test_python_importer_parse_body(self):

        c = self.c
        u = c.undoer
        x = c.importCommands
        target = c.p.insertAfter()
        target.h = 'target'

        body_1 = textwrap.dedent(
        """
            import os

            def macro(func):
                def new_func(*args, **kwds):
                    raise RuntimeError('blah blah blah')
            return new_func
        """).strip() + '\n'
        target.b = body_1
        x.parse_body(target)

        expected_results = (
            (0, '',  # Ignore the top-level headline.
                'import os\n'
                '\n'
                '@others\n'
                'return new_func\n'
                '@language python\n'
                '@tabwidth -4\n'
            ),
            (1, 'function: macro',
                'def macro(func):\n'
                '    def new_func(*args, **kwds):\n'
                "        raise RuntimeError('blah blah blah')\n"
            ),
        )
        # Don't call run_test.
        self.check_outline(target, expected_results)

        # Test undo
        u.undo()
        self.assertEqual(target.b, body_1, msg='undo test')
        self.assertFalse(target.hasChildren(),  msg='undo test')
        # Test redo
        u.redo()
        self.check_outline(target, expected_results)
    #@+node:ekr.20230715004610.1: *3* TestLeoImport.slow_test_ric_run
    def slow_test_ric_run(self):
        c = self.c
        u = c.undoer

        # Setup.
        root = c.rootPosition()
        root.deleteAllChildren()
        while root.hasNext():
            root.next().doDelete()
        c.selectPosition(root)
        self.assertEqual(c.lastTopLevel(), root)
        if 1:
            # 0.9 sec to import only leoGlobals.py
            dir_ = g.os_path_finalize_join(g.app.loadDir, 'leoGlobals.py')
        else:
            # 4.1 sec. to import leo/core/*.py.
            dir_ = os.path.normpath(g.app.loadDir)
        self.assertTrue(os.path.exists(dir_), msg=dir_)

        # Run the tests.
        expected_headline = 'imported files'
        for kind in ('@clean', '@file'):
            x = leoImport.RecursiveImportController(c,
                dir_=dir_,
                kind=kind,
                recursive=True,
                safe_at_file = True,
                theTypes=['.py'],
                verbose=False,
            )
            x.run(dir_)
            self.assertEqual(c.lastTopLevel().h, expected_headline)
            u.undo()
            self.assertEqual(c.lastTopLevel(), root)
            u.redo()
            self.assertEqual(c.lastTopLevel().h, expected_headline)
            u.undo()
            self.assertEqual(c.lastTopLevel(), root)
    #@-others
#@-others
#@-leo

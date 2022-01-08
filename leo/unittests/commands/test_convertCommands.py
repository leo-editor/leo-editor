# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20211013081056.1: * @file ../unittests/commands/test_convertCommands.py
#@@first
"""Tests of leo.commands.leoConvertCommands."""
import os
import re
import textwrap
from leo.core import leoGlobals as g
from leo.core.leoTest2 import LeoUnitTest

#@+others
#@+node:ekr.20211013081200.1: ** class TestPythonToTypeScript(LeoUnitTest):
class TestPythonToTypeScript(LeoUnitTest):
    """Test cases for python-to-typescript command"""

    #@+others
    #@+node:ekr.20211013090653.1: *3*  test_py2ts.setUp
    def setUp(self):
        super().setUp()
        c = self.c
        self.x = c.convertCommands.PythonToTypescript(c)
        self.assertTrue(hasattr(self.x, 'convert'))
        root = self.root_p
        # Delete all children
        root.deleteAllChildren()
        # Read leo.core.leoNodes into contents.
        unittest_dir = os.path.dirname(__file__)
        core_dir = os.path.abspath(os.path.join(unittest_dir, '..', '..', 'core'))
        path = os.path.join(core_dir, 'leoNodes.py')
        with open(path) as f:
            contents = f.read()
        # Set the gnx of the @file nodes in the contents to root.gnx.
        # This is necessary because of a check in fast_at.scan_lines.
        pat = re.compile(r'^\s*#@\+node:([^:]+): \* @file leoNodes\.py$')
        line3 = g.splitLines(contents)[2]
        m = pat.match(line3)
        assert m, "Can not replace gnx"
        contents = contents.replace(m.group(1), root.gnx)
        # Replace c's outline with leoNodes.py.
        gnx2vnode = {}
        ok = c.atFileCommands.fast_read_into_root(c, contents, gnx2vnode, path, root)
        self.assertTrue(ok)
        root.h = 'leoNodes.py'
        self.p = root
        c.selectPosition(self.p)
    #@+node:ekr.20211013081200.2: *3* test_py2ts.test_setup
    def test_setup(self):
        c = self.c
        assert self.x
        assert self.p
        if 0:
            self.dump_tree()
        if 0:
            for p in c.all_positions():
                g.printObj(p.b, tag=p.h)
    #@+node:ekr.20211013085659.1: *3* test_py2ts.test_convert_position_class
    def test_convert_position_class(self):
        # Convert a copy of the Position class
        self.x.convert(self.p)
    #@+node:ekr.20211021075411.1: *3* test_py2ts.test_do_f_strings()
    def test_do_f_strings(self):

        x = self.x
        tests = (
            (
                'g.es(f"{timestamp}created: {fileName}")\n',
                'g.es(`${timestamp}created: ${fileName}`)\n',
            ),
            (
                'g.es(f"read {len(files)} files in {t2 - t1:2.2f} seconds")\n',
                'g.es(`read ${len(files)} files in ${t2 - t1} seconds`)\n',
            ),
            (
                'print(f"s: {s!r}")\n',
                'print(`s: ${s}`)\n',
            ),
        )
        for test in tests:
            source, expected = test
            lines = [source]
            x.do_f_strings(lines)
            self.assertEqual(lines[-1], expected)
    #@-others
#@+node:ekr.20220108083112.1: ** class TestAddMypyAnnotations(LeoUnitTest):
class TestAddMypyAnnotations(LeoUnitTest):
    """Test cases for add-mypy-annotations command"""
    
    def setUp(self):
        super().setUp()
        c = self.c
        self.p = self.root_p
        self.x = c.convertCommands.Add_Mypy_Annotations(c)
        self.x.types_d = {
            'c': 'Cmdr',
            'ch': 'str',
            'gnx': 'str',
            'd': 'Dict[str, str]',
            'i': 'int',
            'j': 'int',
            'k': 'int',
            'n': 'int',
            'p': 'Pos',
            's': 'str',
            'v': 'VNode',
        }

    #@+others
    #@+node:ekr.20220108083112.4: *3* test_ama.test_plain_args
    def test_plain_args(self):
        # Convert a copy of the Position class
        p = self.p
        p.b = contents = textwrap.dedent('''\
            def f1(i, s):
                pass
    ''')
        expected = textwrap.dedent('''\
            def f1(i: int, s: str) -> Any:
                pass
    ''')
        self.x.convert_body(p)
        self.assertEqual(p.b, expected)
    #@+node:ekr.20220108091352.1: *3* test_ama.test_already_annotated
    def test_already_annotated(self):
        # Convert a copy of the Position class
        p = self.p
        p.b = contents = textwrap.dedent('''\
            def f2(i: int, s: str) -> str:
                return s
    ''')
        self.x.convert_body(p)
        self.assertEqual(p.b, contents)
    #@-others
#@-others


#@-leo

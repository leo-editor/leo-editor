#@+leo-ver=5-thin
#@+node:ekr.20211013081056.1: * @file ../unittests/commands/test_convertCommands.py
"""Tests of leo.commands.leoConvertCommands."""
import os
import re
import textwrap
from leo.core import leoGlobals as g
from leo.core.leoTest2 import LeoUnitTest
from leo.commands.convertCommands import ConvertCommandsClass
from leo.unittests.test_importers import BaseTestImporter

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
        pat = re.compile(r'^\s*#\s?@\+node:([^:]+): \* @file leoNodes\.py$')
        # line 1: #@+leo-ver=5-thin
        # line 2: #@+node:ekr.20031218072017.3320: * @file leoNodes.py
        line2 = g.splitLines(contents)[1]
        m = pat.match(line2)
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
        # print(self.id())
        c = self.c
        self.p = self.root_p
        self.x = c.convertCommands.Add_Mypy_Annotations(c)
        self.x.types_d = {
            'c': 'Cmdr',
            'ch': 'str',
            'gnx': 'str',
            'd': 'Dict[str, str]',
            'event': 'Event',
            'i': 'int',
            'j': 'int',
            'k': 'int',
            'n': 'int',
            'p': 'Position',
            's': 'str',
            'v': 'VNode',
        }

    #@+others
    #@+node:ekr.20220108091352.1: *3* test_ama.test_already_annotated
    def test_already_annotated(self):
        p = self.p
        p.b = contents = textwrap.dedent('''\
            def f1(i: int, s: str) -> str:
                return s

            def f2(self, c: Cmdr, g: Any, ivars: list[str]) -> Any:
                pass
    ''')
        self.x.convert_body(p)
        self.assertEqual(p.b, contents)
    #@+node:ekr.20220416053117.1: *3* test_ama.test_bug_2606
    def test_bug_2606(self):
        # https://github.com/leo-editor/leo-editor/issues/2606
        p = self.p
        # Make sure any adjustment to the args logic doesn't affect following functions.
        p.b = textwrap.dedent('''\
            def f1(root=p and p.copy()):
                pass

            def f2(n=1, f=0.1):
                pass

            def f3(a, self=self):
                pass
    ''')
        expected = textwrap.dedent('''\
            def f1(root: Any=p and p.copy()) -> None:
                pass

            def f2(n: int=1, f: float=0.1) -> None:
                pass

            def f3(a: Any, self=self) -> None:
                pass
    ''')
        self.x.convert_body(p)
        self.assertEqual(p.b, expected)
    #@+node:ekr.20220108093044.1: *3* test_ama.test_initializers
    def test_initializers(self):
        p = self.p
        p.b = textwrap.dedent('''\
            def f3(i = 2, f = 1.1, b = True, s = 'abc', x = None):
                pass
    ''')
        expected = textwrap.dedent('''\
            def f3(i: int=2, f: float=1.1, b: bool=True, s: str='abc', x: Any=None) -> None:
                pass
    ''')
        self.x.convert_body(p)
        self.assertEqual(p.b, expected)
    #@+node:ekr.20220108093621.1: *3* test_ama.test_multiline_def
    def test_multiline_def(self):
        p = self.p
        p.b = textwrap.dedent('''\
            def f (
                self,
                a,
                b=1,
                c = 2 ,
                *args,
                **kwargs,
            ):
                pass
    ''')
        expected = textwrap.dedent('''\
            def f(
                self,
                a: Any,
                b: int=1,
                c: int=2,
                *args: Any,
                **kwargs: Any,
            ) -> None:
                pass
    ''')
        self.x.convert_body(p)
        self.assertEqual(p.b, expected)
    #@+node:ekr.20220108153333.1: *3* test_ama.test_multiline_def_with_comments
    def test_multiline_def_with_comments(self):
        p = self.p
        p.b = textwrap.dedent('''\
            def f (
                self,# comment 1
                a,   # comment, 2
                b=1,
                d=2,     # comment with trailing comma,
                e=3,
            ):
                pass
    ''')
        # Note: The command insert exactly two spaces before comments.
        expected = textwrap.dedent('''\
            def f(
                self,  # comment 1
                a: Any,  # comment, 2
                b: int=1,
                d: int=2,  # comment with trailing comma,
                e: int=3,
            ) -> None:
                pass
    ''')
        self.x.convert_body(p)
        # g.printObj(p.b)
        self.assertEqual(p.b, expected)
    #@+node:ekr.20220108083112.4: *3* test_ama.test_plain_args
    def test_plain_args(self):
        p = self.p
        p.b = textwrap.dedent('''\
            def f1(event, i, s):
                pass
    ''')
        expected = textwrap.dedent('''\
            def f1(event: Event, i: int, s: str) -> None:
                pass
    ''')
        self.x.convert_body(p)
        self.assertEqual(p.b, expected)
    #@+node:ekr.20220416082758.1: *3* test_ama.test_special_methods
    def test_special_methods(self):
        p = self.p
        p.b = textwrap.dedent('''\
            def __init__(self):
                pass

            def __repr__(self):
                pass

            def __str__(self):
                pass
    ''')
        expected = textwrap.dedent('''\
            def __init__(self) -> None:
                pass

            def __repr__(self) -> str:
                pass

            def __str__(self) -> str:
                pass
    ''')
        self.x.convert_body(p)
        self.assertEqual(p.b, expected)
    #@-others
#@+node:ekr.20220824193803.1: ** class Test_To_Python(BaseTestImporter):
class Test_To_Python(BaseTestImporter):
    """Test cases for commands using To_Python class."""

    #@+others
    #@+node:ekr.20220824193932.1: *3* test_c_to_python
    def test_c_to_python(self):

        c = self.c
        x1 = ConvertCommandsClass(c)
        x = x1.C_To_Python(c)
        s = textwrap.dedent("""\
        void hello_world()
        {
            print('hi')
            if a == 2 {
                print('2')
            }
        }
        """)
        lines = g.splitLines(s)
        x.convertCodeList(lines)
    #@-others
#@-others
#@-leo

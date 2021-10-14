# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20211013081056.1: * @file ../unittests/commands/test_convertCommands.py
#@@first
"""Tests of leo.commands.leoConvertCommands."""
import os
import re
### import textwrap
from leo.core import leoGlobals as g
from leo.core.leoTest2 import LeoUnitTest
assert re  ###
assert g ###

#@+others
#@+node:ekr.20211013081200.1: ** class TestPythonToTypeScript(LeoUnitTest):
class TestPythonToTypeScript(LeoUnitTest):
    """Test cases for leo/commands/leoConvertCommands.py"""

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
        # self.dump_tree(self.c.lastTopLevel())
    #@-others
#@-others


#@-leo

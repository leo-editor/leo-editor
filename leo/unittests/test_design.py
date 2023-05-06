#@+leo-ver=5-thin
#@+node:ekr.20230506095312.1: * @file ../unittests/test_design.py
"""Global design tests."""
# import ast
# from ast import NodeVisitor
# from ast import AST as Node
import glob
import os
import unittest
from leo.core import leoGlobals as g
#@+<< define test files >>
#@+node:ekr.20230506103755.1: ** << define test files >>
unittests_dir = os.path.dirname(__file__)
leo_dir = g.finalize_join(unittests_dir, '..')
print(leo_dir)

def compute_files(pattern, root_dir):
    aList = [
        g.finalize_join(root_dir, z)
            for z in glob.glob(pattern, root_dir=core_dir)
    ]
    assert all(os.path.exists(z) for z in aList)
    return aList
    
core_dir = g.finalize_join(leo_dir, 'leo')
commands_dir = g.finalize_join(leo_dir, 'commands')
plugins_dir = g.finalize_join(leo_dir, 'plugins')

core_files = compute_files('*.py', core_dir)
commands_files = compute_files('*.py', commands_dir)
qt_files = compute_files('qt_*.py', plugins_dir)
#@-<< define test files >>

#@+others
#@+node:ekr.20230506095516.1: ** class TestAnnotations(unittest.TestCase)
class TestAnnotations(unittest.TestCase):
    """Test that annotations of c, g, p, s, v are as expected."""
    
    def test_dummy(self):
        g.trace()
    
    #@+others
    #@-others
#@+node:ekr.20230506095648.1: ** class TestChains(unittest.TestCase)
class TestChains(unittest.TestCase):
    """Ensure that only certain chains exist."""
#@-others
#@-leo

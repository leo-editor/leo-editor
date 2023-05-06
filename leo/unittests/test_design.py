#@+leo-ver=5-thin
#@+node:ekr.20230506095312.1: * @file ../unittests/test_design.py
"""Global design tests."""
import ast
from ast import NodeVisitor
from ast import AST as Node
from collections import defaultdict
import glob
import os
import re
from typing import Dict ###, List
import unittest
from leo.core import leoGlobals as g
#@+<< define patterns >>
#@+node:ekr.20230506110036.1: ** << define patterns >>
c_pat_s = r'\b(c[0-9]?|[\w_]+_c)\b'
p_pat_s = r'\b(p[0-9]?|[\w_]+_p)\b'
s_pat_s = r'\b(s[0-9]?|[\w_]+_s)\b'
v_pat_s = r'\b(v[0-9]?|[\w_]+_v)\b'
var_patterns_s = '|'.join([c_pat_s, p_pat_s, v_pat_s])
var_patterns = re.compile(var_patterns_s)
#@-<< define patterns >>
#@+<< define test files >>
#@+node:ekr.20230506103755.1: ** << define test files >>
unittests_dir = os.path.dirname(__file__)
leo_dir = g.finalize_join(unittests_dir, '..')

def compute_files(pattern, root_dir):
    return [g.finalize_join(root_dir, z)
        for z in glob.glob(pattern, root_dir=root_dir)]

# Compute directories.
core_dir = g.finalize_join(leo_dir, 'core')
commands_dir = g.finalize_join(leo_dir, 'commands')
plugins_dir = g.finalize_join(leo_dir, 'plugins')

# Compute relevant .piy files.
core_files = compute_files('*.py', core_dir)
commands_files = compute_files('*.py', commands_dir)
qt_files = compute_files('qt_*.py', plugins_dir)
all_files = core_files + commands_files + qt_files
#@-<< define test files >>

#@+others
#@+node:ekr.20230506111649.1: ** class AnnotationsTraverser
class AnnotationsTraverser(NodeVisitor):

    d: Dict[Node, Dict] = defaultdict(dict)
    
    def __init__(self, path):
        super().__init__()
        self.path = path
    
    #@+others
    #@+node:ekr.20230506111649.3: *3* visit_AnnAssign
    def visit_AnnAssign(self, node):
        path = self.path
        # AnnAssign(expr target, expr annotation, expr? value, int simple)
        if isinstance(node.target, ast.Name):
            id_s = node.target.id
            if var_patterns.match(id_s):
                self.d [path] [id_s] = node.annotation
            
    #@+node:ekr.20230506111649.4: *3* visit_FunctionDef
    def visit_FunctionDef(self, node):
        path = self.path
        arguments = node.args
        for arg in arguments.args:
            assert isinstance(arg, ast.arg)
            # arg = (identifier arg, expr? annotation, string? type_comment)
            annotation = getattr(arg, 'annotation', None)
            id_s = arg.arg
            if annotation and var_patterns.match(id_s):
                ### dump_annotation???
                if isinstance(annotation, ast.Name):
                    ann_s = annotation.id
                elif isinstance(annotation, ast.Constant):
                    ann_s = annotation.value
                elif isinstance(annotation, ast.Subscript):
                    # Subscript(expr value, expr slice, expr_context ctx)
                    if isinstance(annotation.value, ast.Name):
                         ann_s = f"Subscript: [{annotation.value.id}]"
                    else:
                        ### dump_subscript???
                        ann_s = f"Subscript: [{annotation.value!r}]"
                else:
                    ann_s = repr(annotation)
                aList = self.d [path].get(id_s, [])
                aList.append(ann_s)
                self.d [path] [id_s] = aList
    #@-others
#@+node:ekr.20230506095516.1: ** class TestAnnotations(unittest.TestCase)
class TestAnnotations(unittest.TestCase):
    """Test that annotations of c, g, p, s, v are as expected."""
    
    def test_all_paths(self):
        for path in all_files:
            self.assertTrue(os.path.exists(path))
            with open(path, 'rb') as f:
                source = g.toUnicode(f.read())
            tree = ast.parse(source, filename=path)
            traverser = AnnotationsTraverser(path)
            traverser.visit(tree)

    #@+others
    #@-others
#@+node:ekr.20230506095648.1: ** class TestChains(unittest.TestCase)
class TestChains(unittest.TestCase):
    """Ensure that only certain chains exist."""
#@-others
#@-leo

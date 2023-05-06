#@+leo-ver=5-thin
#@+node:ekr.20230506095312.1: * @file ../unittests/test_design.py
"""Global design tests."""
import ast
from ast import NodeVisitor
import glob
import os
import re
from typing import Dict
import unittest
from leo.core import leoGlobals as g

files_dict: Dict = None  # Keys are paths, values are contents of file.

#@+others
#@+node:ekr.20230506154039.1: ** function: load_files
def load_files():

    global files_dict
    if files_dict is not None:
        return
        
    def compute_files(pattern, root_dir):
        return [g.finalize_join(root_dir, z)
            for z in glob.glob(pattern, root_dir=root_dir)]

    # Compute directories.
    unittests_dir = os.path.dirname(__file__)
    leo_dir = g.finalize_join(unittests_dir, '..')
    core_dir = g.finalize_join(leo_dir, 'core')
    commands_dir = g.finalize_join(leo_dir, 'commands')
    plugins_dir = g.finalize_join(leo_dir, 'plugins')

    # Compute lists of files.
    core_files = compute_files('*.py', core_dir)
    commands_files = compute_files('*.py', commands_dir)
    qt_files = compute_files('qt_*.py', plugins_dir)
    all_files = core_files + commands_files + qt_files

    # Compute the files dict.
    files_dict = {}
    for path in all_files:
        assert os.path.exists(path), repr(path)
        with open(path, 'rb') as f:
            files_dict[path] = g.toUnicode(f.read())
#@+node:ekr.20230506111929.1: ** Traverser classes
#@+node:ekr.20230506111649.1: *3* class AnnotationsTraverser
class AnnotationsTraverser(NodeVisitor):

    annotations_set = set()

    def __init__(self, tester):
        super().__init__()
        self.tester = tester

    #@+others
    #@+node:ekr.20230506111649.3: *4* visit_AnnAssign
    def visit_AnnAssign(self, node):
        # AnnAssign(expr target, expr annotation, expr? value, int simple)
        if isinstance(node.target, ast.Name):
            if node.annotation:
                id_s = node.target.id
                self.test_annotation(node, id_s, node.annotation)
    #@+node:ekr.20230506123402.1: *4* test_annotation
    annotation_table = (
        (re.compile(r'\b(c[0-9]?|[\w_]+_c)\b'), 'Cmdr'),
        (re.compile(r'\b(p[0-9]?|[\w_]+_p)\b'), 'Position'),
        (re.compile(r'\b(s[0-9]?|[\w_]+_s)\b'), 'str'),
        (re.compile(r'\b(v[0-9]?|[\w_]+_v)\b'), 'VNode'),
    )

    def test_annotation(self, node: ast.AST, identifier: str, annotation: ast.Expr) -> None:
        """Test the annotation of identifier."""
        exceptions = (
            # Problem annotating Cmdr in leoCommands.py...
            'bringToFront',
            'universalCallback',
            # These methods should always be annotated Any.
            '__eq__', '__ne__',
            'resolveArchivedPosition',
            'setBodyString', 'setHeadString',
            'to_encoded_string', 'to_unicode', 'toUnicode',
        )
        for pattern, expected_annotation in self.annotation_table:
            m = pattern.match(identifier)
            if not m:
                continue
            node_s = g.splitLines(ast.unparse(node))[0].strip()
            if any(node_s.startswith(f"def {z}") for z in exceptions):
                continue
            annotation_s = ast.unparse(annotation)
            self.annotations_set.add(f"{identifier:>20}: {annotation_s}")
            expected = (
                expected_annotation,
                f"'{expected_annotation}'",
                f"Optional[{expected_annotation}]",
                f"Optional['{expected_annotation}']")
            msg = (
                'test_annotation\n'
                f"    path: {self.tester.path}\n"
                f"    node: {node_s}\n"
                f"expected: {expected_annotation}\n"
                f"     got: {annotation_s}")
            if 1:  # Production.
                self.tester.assertTrue(annotation_s in expected, msg=msg)
            else:  # Allow multiple failures.
                if annotation_s not in expected:
                    print(msg)
    #@+node:ekr.20230506111649.4: *4* visit_FunctionDef
    def visit_FunctionDef(self, node):
        arguments = node.args
        for arg in arguments.args:
            # arg = (identifier arg, expr? annotation, string? type_comment)
            assert isinstance(arg, ast.arg)
            annotation = getattr(arg, 'annotation', None)
            if annotation:
                id_s = arg.arg
                self.test_annotation(node, id_s, annotation)
    #@-others
#@+node:ekr.20230506111927.1: *3* class ChainsTraverser(NodeVisitor)
class ChainsTraverser(NodeVisitor):

    def __init__(self, tester):
        super().__init__()
        self.tester = tester

    #@+others
    #@-others
#@+node:ekr.20230506095516.1: ** class TestAnnotations(unittest.TestCase)
class TestAnnotations(unittest.TestCase):
    """Test that annotations of c, g, p, s, v are as expected."""

    def test_all_paths(self):
        load_files()
        traverser = AnnotationsTraverser(tester=self)
        for path in files_dict:
            self.path = path
            source = files_dict [path]
            tree = ast.parse(source, filename=path)
            traverser.visit(tree)
        if 0:
            for s in sorted(list(traverser.annotations_set)):
                print(s)

    #@+others
    #@-others
#@+node:ekr.20230506095648.1: ** class TestChains(unittest.TestCase)
class TestChains(unittest.TestCase):
    """Ensure that only certain chains exist."""

    def test_all_paths(self):
        load_files()
        traverser = ChainsTraverser(tester=self)
        for path in files_dict:
            source = files_dict [path]
            tree = ast.parse(source, filename=path)
            traverser.visit(tree)
#@-others
#@-leo

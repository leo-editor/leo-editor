#@+leo-ver=5-thin
#@+node:ekr.20240529053756.1: * @file ../scripts/check_leo.py
#@+<< check_leo.py: docstring >>
#@+node:ekr.20240604203402.1: ** << check_leo.py: docstring >>
"""
check_leo.py: A script that checks for undefined methods in Leo's core code.

This script demonstrates that mypy, pylint and ruff *might* provide stronger checks.

This script is pragmatic:
    
- It uses Leo-specic knowledge to simplify the code.

- It assumes:
  1. That within a file all class names are unique.
  2. That no two *base* classes have the same name.
  
Both assumptions are true for Leo, but are not true in general.
"""
#@-<< check_leo.py: docstring >>
#@+<< check_leo.py: imports & annotations >>
#@+node:ekr.20240529055116.1: ** << check_leo.py: imports & annotations >>
import argparse
import ast
import glob
import os
import pdb  # For live objects.
import re
import sys
import time
from typing import Any, Optional
import unittest

# Add the leo/editor folder to sys.path.
leo_editor_dir = os.path.abspath(os.path.join(__file__, '..', '..', '..'))
if leo_editor_dir not in sys.path:
    sys.path.insert(0, leo_editor_dir)

from leo.core import leoGlobals as g
# Imports for live objects.
from leo.core.leoQt import QtWidgets
import leo.core.leoColorizer as leoColorizer
import leo.core.leoGui as leoGui
from leo.plugins.qt_frame import LeoBaseTabWidget
assert g
assert os.path.exists(leo_editor_dir), leo_editor_dir

Node = ast.AST
#@-<< check_leo.py: imports & annotations >>

#@+others
#@+node:ekr.20240606204736.1: ** top-level functions: check_leo.py
#@+node:ekr.20240606203244.1: *3* function: bare_name (check_leo.py)
def bare_name(class_name):
    """
    Return the last part of a potentially qualified class name.
    
    For example, `QFrame` is bare class name of `QtWidgets.QFrame` or `QFrame`.
    
    This script assumes that the bare names of all classes are distinct.
    """
    return class_name.split('.')[-1]
#@+node:ekr.20240609035415.1: *3* function: main (check_leo.py)
def main():
    """The main function for check_leo.py."""
    files = scan_args()
    print('check_leo.py:', files)
    CheckLeo(files=files).check_leo()
#@+node:ekr.20240530073251.1: *3* function: scan_args (check_leo.py)
def scan_args() -> list[str]:  # pragma: no cover
    """
    Scan command-line arguments for check_leo.py.
    
    Return a list of files to scan. An empty list means scan all Leo files.
    """
    parser = argparse.ArgumentParser(
        description= 'check_leo.py: check all leo files or a given list of files',
        formatter_class=argparse.RawTextHelpFormatter,
    )
    add = parser.add_argument

    # Arguments.
    add('PATHS', nargs='*', help='list of files, relative to the leo directory')

    # Create the return values.
    parser.set_defaults(all=False, report=False)
    args = parser.parse_args()
    return args.PATHS
#@+node:ekr.20240529063157.1: ** class CheckLeo
class CheckLeo:

    def __init__(self, files: list[str] = None) -> None:
        self.files = files

    #@+others
    #@+node:ekr.20240529063012.1: *3* 1: CheckLeo.check_leo & helpers
    def check_leo(self) -> None:
        """Check all files returned by get_leo_paths()."""
        t1 = time.process_time()
        #@+<< check_leo: define all ivars >>
        #@+node:ekr.20240603192905.1: *4* << check_leo: define all ivars >>
        # Keys: bare class names.  Values: list of method names.
        self.class_methods_dict: dict[str, list[str]] = {}

        self.errors: list[str] = []  # Errors for unit testing.

        # Keys: bare class names. Values: list of extra methods of that class.
        self.extra_methods_dict: dict[str, list[str]] = self.init_extra_methods_dict()

        self.live_objects: list[Any] = []  # References to live objects.

        # Keys: bare class names. Values: instances of that class.
        self.live_objects_dict: dict[str, Any] = self.init_live_objects_dict()
        self.missing_base_classes: set[str] = set()  # Names of all missing base classes.

        # Add 'Thread to missing_base_classes. It's too risky to instanciate it.
        self.missing_base_classes.add('Thread')

        self.n_missing = 0  # The number of missing methods.

        # Keys: paths. Values: top-level ast.Nodes (ast.Module)
        self.tree_dict: dict[str, Node] = {}
        #@-<< check_leo: define all ivars >>

        # Check each file separately.
        for path in self.get_leo_paths():
            self.scan_file(path)

        # Post-checks.
        self.check_annotations()
        self.check_chains()

        # Report.
        t2 = time.process_time()
        n = self.n_missing
        if not g.unitTesting:
            g.trace(f"{n} missing method{g.plural(n)}")
            g.trace(f"done: {(t2-t1):3.2} sec.")

        # Kill the QApplication!
        self.app.deleteLater()

    #@+node:ekr.20240529094941.1: *4* CheckLeo.get_leo_paths
    def get_leo_paths(self) -> list[str]:
        """Return a list of full paths to Leo paths to be checked."""

        def join(*args) -> str:
            return os.path.abspath(os.path.join(*args))

        # Compute the directories.
        leo_dir = join(leo_editor_dir, 'leo')
        command_dir = join(leo_dir, 'commands')
        core_dir = join(leo_dir, 'core')
        plugins_dir = join(leo_dir, 'plugins')
        for z in (leo_dir, command_dir, core_dir, plugins_dir):
            assert os.path.exists(z), z

        if self.files:  # Check only the given files.
            paths = []
            for z in self.files:
                path = join(leo_dir, z)
                if os.path.exists(path):
                    paths.append(path)
                else:
                    g.trace('not found:', path)
            return paths

        # Check all of Leo's important files.
        return (
               glob.glob(f"{core_dir}{os.sep}leo*.py")
             + glob.glob(f"{command_dir}{os.sep}leo*.py")
             + glob.glob(f"{plugins_dir}{os.sep}qt_*.py")
        )
    #@+node:ekr.20240602051423.1: *4* CheckLeo.init_extra_methods_dict
    def init_extra_methods_dict(self) -> dict[str, list[str]]:
        """
        Init the Leo-specific data for base classes.
        
        Return a dict: keys are *unqualified* class mames.
        Values are list of methods defined in that class, including base classes.
        """
        return {
            #@+<< Harmless suppressions >>
            #@+node:ekr.20240608043115.1: *5* << Harmless suppressions >>
            # Ivars that contain a Callable...
            # These could be removed by looking at annotations.
            'DynamicWindow': ['func', 'oldEvent'],
            'EventWrapper': ['func', 'oldEvent'],
            'FileNameChooser': ['callback'],
            'IdleTime': ['handler'],
            'LeoFind': ['escape_handler', 'handler'],
            'LeoQtTree': ['headlineWrapper'],
            'PygmentsColorizer': ['getFormat', 'getDefaultFormat', 'setFormat'],
            'RstCommands': ['user_filter_b', 'user_filter_h'],
            'SqlitePickleShare': ['dumper', 'loader'],
            'VimCommands': ['handler', 'motion_func'],

            # Ivars that contain class Names.
            'LeoFrame': ['iconBarClass', 'statusLineClass'],

            # Permanent aliases.
            'GlobalConfigManager': ['munge'],
            'NodeIndices': ['setTimeStamp'],

            # Ivars that do not always exist.
            'LeoTree': [
                'setItemForCurrentPosition',  # Might exist in subclasses.
                'unselectItem',
            ],
            #@-<< Harmless suppressions >>

            # Bad style: These are defined in other classes!
            # However, I'm not going to change the code.
            'QTextMixin': [
                'getAllText', 'getInsertPoint', 'getSelectionRange',
                'see', 'setAllText', 'setInsertPoint', 'setSelectionRange',
            ],
        }
    #@+node:ekr.20240602103522.1: *4* CheckLeo.init_live_objects_dict
    def init_live_objects_dict(self) -> dict[str, Any]:
        """
        Return the live objects dict.
        Keys are bare class names; values are live objects.
        """
        result: dict[str, Any] = {}

        # Create the app first.

        self.app = app = QtWidgets.QApplication([])
        self.live_objects.append(app)  # Otherwise all widgets will go away.

        # 1. Add Qt widget classes.
        qt_widget_classes = [
            QtWidgets.QComboBox,
            QtWidgets.QDateTimeEdit,
            QtWidgets.QDialog,
            QtWidgets.QFrame,
            QtWidgets.QLineEdit,
            QtWidgets.QListWidget,
            QtWidgets.QMainWindow,
            QtWidgets.QMenu,
            QtWidgets.QMessageBox,
            QtWidgets.QTabBar,
            QtWidgets.QTabWidget,
            QtWidgets.QTextBrowser,
            QtWidgets.QTreeWidget,
        ]
        for widget_class in qt_widget_classes:
            w = widget_class()
            result[w.__class__.__name__] = w  # Use the bare class name.

        # 2. Add various other live objects.
        #    The 'Thread' module is handled as a special case.
        result['dict'] = {}
        result['Pdb'] = pdb.Pdb()

        # 3. Add live objects for unit tests.
        result['NodeVisitor'] = ast.NodeVisitor()
        result['TestCase'] = unittest.TestCase()

        # 4. Add Leo base classes.
        result['BaseColorizer'] = leoColorizer.BaseColorizer(c=None)
        result['LeoBaseTabWidget'] = LeoBaseTabWidget()
        result['LeoGui'] = leoGui.LeoGui(guiName='NullGui')
        result['LeoQtGui'] = leoGui.LeoGui(guiName='NullGui')  # Do *not* instantiate the real class.
        result['PygmentsColorizer'] = leoColorizer.PygmentsColorizer(c=None, widget=None)
        return result
    #@+node:ekr.20240602162342.1: *3* 2: CheckLeo.scan_file & helpers
    def scan_file(self, path: str, *, contents=None) -> None:
        """Scan the file and update global data."""
        if not contents:
            contents = self.read(path)
            if not contents:
                g.trace(f"file not found: {path}")
                return
        self.tree_dict[path] = file_node = self.parse_ast(contents)

        # Pass 0: find all class nodes.
        self.class_nodes = self.find_class_nodes(file_node, path)

        # Pass 1: create the class_methods_dict.
        for class_node in self.class_nodes:
            self.scan_class(class_node, path)

        # Pass 2: check all classes.
        for class_node in self.class_nodes:
            self.check_class(class_node, path)
    #@+node:ekr.20240608045736.1: *4* CheckLeo.find_class_nodes
    def find_class_nodes(self, file_node: Node, path: str) -> list[ast.ClassDef]:
        """
        Find all class definitions within a file.
        """
        assert isinstance(file_node, ast.Module), repr(file_node)

        # This is as fast as using a bespoke ast.NodeVisitor class.
        return [z for z in ast.walk(file_node) if isinstance(z, ast.ClassDef)]

    #@+node:ekr.20240529060232.4: *4* CheckLeo.parse_ast
    def parse_ast(self, s: str) -> Optional[Node]:
        """
        Parse string s, catching & reporting all exceptions.
        Return the ast node, or None.
        """

        def oops(message: str) -> None:
            print('')
            print(f"parse_ast: {message}")
            g.printObj(s)
            print('')

        try:
            s1 = g.toEncodedString(s)
            tree = ast.parse(s1, filename='before', mode='exec')
            return tree
        except IndentationError:
            oops('Indentation Error')
        except SyntaxError:
            oops('Syntax Error')
        except Exception:
            oops('Unexpected Exception')
            g.es_exception()
        return None
    #@+node:ekr.20240529060232.3: *4* CheckLeo.read
    def read(self, file_name: str) -> str:
        try:
            with open(file_name, 'r') as f:
                contents = f.read()
                return contents
        except IOError:
            return ''
        except Exception:
            g.es_exception()
            return ''
    #@+node:ekr.20240602161721.1: *3* 3: CheckLeo.scan_class & helper
    def scan_class(self, class_node: ast.ClassDef, path: str) -> None:
        """Check that all called methods exist."""
        class_name = bare_name(class_node.name)
        methods: list[ast.FunctionDef] = self.find_methods(class_node)
        method_names = [z.name for z in methods]

        # All class names are unique with the following exceptions:
        if class_name not in (
            'InputToken', 'ParseState', 'Tokenizer',
            'Ui_LeoQuickSearchWidget',
        ):
            # A crucial simplifying assumption.
            assert class_name not in self.class_methods_dict, (class_name, g.shortFilename(path))

        # Update the class dict.
        self.class_methods_dict[class_name] = method_names
    #@+node:ekr.20240602165136.1: *4* CheckLeo.find_methods (pass 3)
    def find_methods(self, class_node: ast.ClassDef) -> list[Node]:
        """Return a list of all methods in the given class."""

        def has_self(func_node: Node) -> bool:
            """Return True if the given FunctionDef node has 'self' as its first argument."""
            # arguments = (arg* args, ...)
            # arg = (identifier arg, ...)
            args = func_node.args
            if not args:
                return False
            first_arg = args.args[0] if args.args else None
            if func_node.decorator_list:
                if 'staticmethod' in ast.unparse(func_node.decorator_list):
                    # g.trace(func_node.name, ast.unparse(func_node.decorator_list))
                    return True
            return first_arg and first_arg.arg == 'self'

        result: list[Node] = []


        class MethodFinder(ast.NodeVisitor):

            def visit_ClassDef(self, node: Node) -> None:
                pass  # Ignore the class.

            def visit_FunctionDef(self, node: Node) -> None:
                if has_self(node):
                    result.append(node)
                # Ignore inner defs.
                # self.generic_visit(node)

            visit_AsyncFunctionDef = visit_FunctionDef


        x = MethodFinder()
        for z in class_node.body:
            x.visit(z)

        # g.trace(f"{len(result):3} {class_node.name}")
        return result
    #@+node:ekr.20240606205913.1: *3* 4: CheckLeo.check_class & helpers
    def check_class(self, class_node: ast.ClassDef, path: str) -> None:
        """Check the class for calls to undefined methods."""
        class_name = bare_name(class_node.name)
        called_names = self.find_calls(class_node)
        method_names = self.class_methods_dict[class_name]
        for called_name in called_names:
            self.has_called_method(called_name, class_node, method_names, path)
    #@+node:ekr.20240531085654.1: *4* CheckLeo.find_calls (pass 4)
    def find_calls(self, class_node: ast.ClassDef) -> list[str]:
        """
        Return the names of all calls to methods class.
        
        Do *not* return method names of any inner class!
        """
        assert isinstance(class_node, ast.ClassDef), repr(class_node)
        names: set[str] = set()
        n_calls = 0


        class FindCallsVisitor(ast.NodeVisitor):

            def visit_ClassDef(self, node: Node) -> None:
                pass  # Do not visit nested classes.

            def visit_Call(self, node: Node) -> None:
                if (isinstance(node.func, ast.Attribute)
                    and isinstance(node.func.value, ast.Name)
                    and node.func.value.id == 'self'
                ):
                    nonlocal n_calls, names
                    n_calls += 1
                    names.add(node.func.attr)
                self.generic_visit(node)


        # Start the traversal.
        x = FindCallsVisitor()
        for node in class_node.body:
            x.visit(node)

        # g.trace(f"{class_node.name:>30} calls: {n_calls:3} names: {len(names):2}")
        # g.printObj(list(sorted(names)), tag=class_node.name)
        return list(sorted(names))
    #@+node:ekr.20240602105914.1: *4* CheckLeo.has_called_method
    def has_called_method(self,
        called_name: str,
        class_node: ast.ClassDef,
        method_names: list[str],
        path: str,
    ) -> bool:
        """
        Check to see whether the class (including base classes) contains the
        given method.
        
        This method assumes the following:
        1. That within a file all class names are unique.
        2. That no two *base* classes have the same name.
        
        Both assumptions are true for Leo, but are not true in general.
        """

        # Check the obvious names.
        if called_name in method_names:
            return True

        class_name = bare_name(class_node.name)

        # Check the live classes.
        live_object = self.live_objects_dict.get(class_name)
        if live_object:
            lib_object_method_names = list(dir(live_object))
            if called_name in lib_object_method_names:
                return True

        # Check for a call to any ctor.
        all_class_names = [z.name for z in self.class_nodes]
        if called_name in all_class_names:
            return True

        # Check base classes.
        bases = class_node.bases
        bases_list = [ast.unparse(z) for z in bases]
        bases_s = ','.join(bases_list)
        if bases:
            for base in bases:
                bare_base_class_name = bare_name(ast.unparse(base))

                # First check the static base class if it exists.
                base_class_methods = self.class_methods_dict.get(bare_base_class_name, [])
                if called_name in base_class_methods:
                    return True
                if (
                    bare_base_class_name not in self.class_methods_dict
                    and bare_base_class_name not in self.live_objects_dict.keys()
                ):
                    if bare_base_class_name  not in self.missing_base_classes:
                        self.missing_base_classes.add(bare_base_class_name)
                        message = (
                            f"Missing base class: '{bare_base_class_name!r}' "
                            f"in {g.shortFileName(path)}"
                        )
                        if not g.unitTesting:
                            print('')
                            g.trace(message)


                # Next, check the live objects.
                live_object = self.live_objects_dict.get(bare_base_class_name)
                if live_object is not None:
                    lib_object_method_names = list(dir(live_object))
                    if called_name in lib_object_method_names:
                        return True

        # Finally, check special cases.
        bases_signature_s = f"({bases_s})" if bases_s else ''
        extra_methods = self.extra_methods_dict.get(class_name, [])
        if called_name in extra_methods:
            return True

        # Report the failure.
        self.n_missing += 1
        message = (
            f"{g.shortFileName(path)} '{called_name}' "
            f"not in {class_name}{bases_signature_s}")
        self.errors.append(message)
        if not g.unitTesting:
            g.trace(message)
        return False
    #@+node:ekr.20240610045841.14: *3* 5a: CheckLeo.check_annotations
    def check_annotations(self) -> None:
        """Test that annotations of c, g, p, s, v are as expected."""

        annotations_set = set()
        annotation_table = (
            (re.compile(r'\b(c[0-9]?|[\w_]+_c)\b'), 'Cmdr'),
            (re.compile(r'\b(p[0-9]?|[\w_]+_p)\b'), 'Position'),
            (re.compile(r'\b(s[0-9]?|[\w_]+_s)\b'), 'str'),
            (re.compile(r'\b(v[0-9]?|[\w_]+_v)\b'), 'VNode'),
        )

        class CheckAnnotations(ast.NodeVisitor):
            """A class to check all annotations in a given ast tree."""
            #@+others
            #@+node:ekr.20240610060346.1: *4* AV.__init__
            def __init__(self, path):
                self.path = path
            #@+node:ekr.20240610045841.9: *4* AV.check_annotation
            def check_annotation(self, node: ast.AST, identifier: str, annotation: ast.Expr) -> None:
                """Test the annotation of identifier."""
                exceptions = (
                    # Problem annotating Cmdr in leoCommands.py...
                    'add_commandCallback', 'bringToFront', 'universalCallback',
                    #
                    'find_language',  # p_or_v is a false match.
                    # These methods should always be annotated Any.
                    '__eq__', '__ne__',
                    'resolveArchivedPosition',
                    'setBodyString', 'setHeadString',
                    'to_encoded_string', 'to_unicode', 'toUnicode',
                )
                for pattern, expected_annotation in annotation_table:
                    m = pattern.match(identifier)
                    if not m:
                        continue
                    node_s = g.splitLines(ast.unparse(node))[0].strip()
                    if any(node_s.startswith(f"def {z}") for z in exceptions):
                        continue
                    annotation_s = ast.unparse(annotation)
                    annotations_set.add(f"{identifier:>20}: {annotation_s}")
                    expected = (
                        expected_annotation,
                        f"'{expected_annotation}'",
                        f"Optional[{expected_annotation}]",
                        f"Optional['{expected_annotation}']")
                    msg = (
                        'test_annotation\n'
                        f"    path: {self.path}\n"
                        f"    node: {node_s}\n"
                        f"expected: {expected_annotation}\n"
                        f"     got: {annotation_s}")
                    if 0:  # Production.
                        self.tester.assertTrue(annotation_s in expected, msg=msg)
                    else:  # Allow multiple failures.
                        if annotation_s not in expected:
                            print(msg)
            #@+node:ekr.20240610045841.10: *4* AV.visit_AnnAssign
            def visit_AnnAssign(self, node):
                # AnnAssign(expr target, expr annotation, expr? value, int simple)
                if isinstance(node.target, ast.Name):
                    if node.annotation:
                        id_s = node.target.id
                        self.check_annotation(node, id_s, node.annotation)
            #@+node:ekr.20240610045841.11: *4* AV.visit_FunctionDef
            def visit_FunctionDef(self, node):
                arguments = node.args
                for arg in arguments.args:
                    # arg = (identifier arg, expr? annotation, string? type_comment)
                    assert isinstance(arg, ast.arg)
                    annotation = getattr(arg, 'annotation', None)
                    if annotation:
                        id_s = arg.arg
                        self.check_annotation(node, id_s, annotation)
                self.generic_visit(node)  # Visit all children.
            #@-others

        for path, tree in self.tree_dict.items():
            x = CheckAnnotations(path)
            x.visit(tree)
        if 0:
            for s in sorted(list(annotations_set)):
                print(s)
    #@+node:ekr.20240610051317.1: *3* 5b: CheckLeo.check_chains & helpers
    def check_chains(self) -> None:

        #@+<< define patterns >>
        #@+node:ekr.20240610052327.1: *4* << define patterns >>
        array_pat = re.compile(r'(\[).*?(\])')
        call_pat = re.compile(r'(\().*?(\))')
        string_pat1 = re.compile(r"(\').*?(\')")
        string_pat2 = re.compile(r'(\").*?(\")')
        patterns = (array_pat, call_pat, string_pat1, string_pat2)
        #@-<< define patterns >>
        chains_set = set()

        #@+others  # Define helper functions.
        #@+node:ekr.20240610045841.16: *4* function: dump_chains
        def dump_chains(chains_list, long_chains_list):

            c_pat = re.compile(r'\b(c[0-9]?|[\w_]+_c)\b')
            p_pat = re.compile(r'\b(p[0-9]?|[\w_]+_p)\b')
            # s_pat = re.compile(r'\b(s[0-9]?|[\w_]+_s)\b')
            v_pat = re.compile(r'\b(v[0-9]?|[\w_]+_v)\b')
            pats = (c_pat, p_pat, v_pat)

            print(g.callers(1))
            for s in long_chains_list:
                if any(pat.match(s) for pat in pats):
                    print(s)
        #@+node:ekr.20240610045841.5: *4* function: filter_chain
        def filter_chain(s: str) -> str:
            """Return only the chains that match one of the patters."""

            def repl(m):
                return m.group(1) + m.group(2)

            for pattern in patterns:
                s = re.sub(pattern, repl, s)
            return s.replace('()', '').replace('[]', '')
        #@-others

        class ChainsVisitor(ast.NodeVisitor):

            def visit_Attribute(self, node):
                """Add only top-level Attribute chains to chains_set."""
                chain = ast.unparse(node)
                chains_set.add(chain)
                # self.generic_visit()

        x = ChainsVisitor()
        for path, tree in self.tree_dict.items():
            x.visit(tree)

        chains_list = list(sorted(set(filter_chain(z) for z in chains_set)))
        long_chains_list = [z for z in chains_list if z.count('.') > 2]
        prefixes = list(sorted(set(['.'.join(z.split('.')[:-1]) for z in long_chains_list])))

        if 0:  # Print prefixes.
            for z in prefixes:
                if z.startswith(('c.', 'g.', 'p.', 'v.')):
                    print(z)

        # Check that all filtered chains match start with the expected prefixes.
        expected_prefixes = (
            'c.commandsDict', 'c.config',
            'c.fileCommands', 'c.findCommands',
            'c.frame',
            # 'c.frame.body', 'c.frame.iconBar', 'c.frame.log',
            # 'c.frame.menu', 'c.frame.statusLine',
            # 'c.frame.top', 'c.frame.tree',
            'c.k',
            'c.leoImport',
            'c.p',
            'c.rootPosition',
            'c.styleSheetManager',
            'c.widget_name',
            'g.app',
            'g.leoServer',
            'g.os.path',
            'p.b', 'p.h', 'p.v',
            'v.b', 'v.context', 'v.h',
        )
        if 1:
            for z in prefixes:
                if z.startswith(('c.', 'g.', 'p.', 'v.')):
                    assert z.startswith(expected_prefixes), z
        if 0:
            g.printObj(chains_list, tag='all chains...')

    #@-others
#@-others

if __name__ == '__main__':
    main()
#@-leo

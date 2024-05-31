#@+leo-ver=5-thin
#@+node:ekr.20240529053756.1: * @file ../scripts/check_leo.py
"""
check_leo.py: Experimental script that checks for undefined methods.
"""
#@+<< check_leo.py: imports & annotations >>
#@+node:ekr.20240529055116.1: ** << check_leo.py: imports & annotations >>
import argparse
import ast
import glob
import os
import time
import sys

# Add the leo/editor folder to sys.path.
leo_editor_dir = os.path.abspath(os.path.join(__file__, '..', '..', '..'))
if leo_editor_dir not in sys.path:
    sys.path.insert(0, leo_editor_dir)

from leo.core import leoGlobals as g
# from leo.core.leoAst import AstDumper
assert g
assert os.path.exists(leo_editor_dir), leo_editor_dir

Node = ast.AST
#@-<< check_leo.py: imports & annotations >>

#@+others
#@+node:ekr.20240530073251.1: ** function: scan_args (check_leo.py)
def scan_args() -> dict[str, bool]:  # pragma: no cover
    """Scan command-line arguments for check_leo.py"""
    parser = argparse.ArgumentParser(
        description= 'check_leo.py: check all leo files',
        formatter_class=argparse.RawTextHelpFormatter,
    )
    add = parser.add_argument

    # Arguments.
    add('--all', dest='all', action='store_true',
        help='check all files, even unchanged files')
    add('--report', dest='report', action='store_true',
        help='show summary report')

    # Create the return values.
    parser.set_defaults(all=False, report=False)
    args = parser.parse_args()

    # Return a dict describing the settings.
    return {
        'all': bool(args.all),
        'report': bool(args.report),
    }
#@+node:ekr.20240529063157.1: ** Class CheckLeo
class CheckLeo:

    def __init__(self):

        # Settings. Set later:
        self.all: bool = None
        self.report: bool = None

        # Keys are full path names to Leo files.
        # Values are dicts describing all the files classes.
        self.d: dict[str, dict] = {}

    #@+others
    #@+node:ekr.20240529135047.1: *3* CheckLeo.check_file
    def check_file(self, path: str, tree: Node) -> None:
        """
        Check that all called methods exist.
        """
        header_printed = False
        d = self.d.get(path)
        classes_dict = d.get('classes')
        chains = set()
        if classes_dict:
            trees_dict = d.get('class_trees')
            for class_name in classes_dict:
                class_name_printed = False
                attrs: set[str] = set()
                class_tree = trees_dict.get(class_name)
                assert isinstance(class_tree, ast.ClassDef), repr(class_tree)
                for node in class_tree.body:
                    for node2 in ast.walk(node):
                        if (
                            isinstance(node2, ast.Call)
                            and isinstance(node2.func, ast.Attribute)
                            and isinstance(node2.func.value, ast.Name)
                        ):
                            if node2.func.value.id == 'self':
                                attrs.add(node2.func.attr)
                            else:
                                s = ast.unparse(node2.func.value)
                                if s.startswith('self'):
                                    # print('    ', ast.unparse(node2.func.value))
                                    print('****', ast.unparse(node2))
                                else:
                                    # print('****', ast.unparse(node2))
                                    # print('....', ast.unparse(node2.func))
                                    if 0:  # Dump the entire call chain.
                                        chains.add(ast.unparse(node2.func))
                                    else:  # Dump only the prefix.
                                        prefix = ast.unparse(node2.func).split('.')[:-1]
                                        chains.add('.'.join(prefix))
                if attrs:
                    methods = classes_dict.get(class_name)
                    if any(z not in methods for z in list(attrs)):
                        if not header_printed:
                            header_printed = True
                            print(f"{g.shortFileName(path)}: missing 'self' methods...")
                        if not class_name_printed:
                            class_name_printed = True
                            bases: list[str] = ast.unparse(class_tree.bases)
                            bases_s = f" [{bases}]" if bases else ''
                            print(f"  class {class_name}{bases_s}:")
                        for attr in sorted(list(attrs)):
                            if attr not in methods:
                                print(f"    self.{attr}")
        if False and chains:
            print('')
            # print(f"chains: {(list(sorted(chains)))}")
            g.printObj(list(sorted(chains)), tag=f"chains: {g.shortFileName(path)}")

    #@+node:ekr.20240529063012.1: *3* CheckLeo.check_leo
    def check_leo(self) -> None:
        """Check all files returned by get_leo_paths()."""
        t1 = time.process_time()
        settings_d = scan_args()
        self.all = settings_d['all']
        self.report = settings_d['report']
        g.trace(settings_d)
        for path in self.get_leo_paths():
            s = self.read(path)
            tree = self.parse_ast(s)
            self.scan_file(path, tree)
            self.check_file(path, tree)
        t2 = time.process_time()
        if self.report:
            self.dump_dict()
        print('')
        g.trace(f"done {(t2-t1):4.2} sec.")
    #@+node:ekr.20240529061932.1: *3* CheckLeo.dump_dict
    def dump_dict(self) -> None:

        for path in self.d:
            short_file_name = g.shortFileName(path)
            d = self.d.get(path)
            # Dump the classes dict.
            classes_dict = d.get('classes')
            if classes_dict:
                print('')
                print(f"{short_file_name}...")
                print(f"{'class':>25}: methods")
                for class_name in classes_dict:
                    methods = classes_dict.get(class_name)
                    print(f"{class_name:>25}: {len(methods)}")
    #@+node:ekr.20240529094941.1: *3* CheckLeo.get_leo_paths
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

        # Return the list of files.
        return (
             glob.glob(f"{core_dir}{os.sep}leo*.py") +
             glob.glob(f"{command_dir}{os.sep}leo*.py") +
             glob.glob(f"{plugins_dir}{os.sep}qt_*.py")
        )
    #@+node:ekr.20240529060232.4: *3* CheckLeo.parse_ast
    def parse_ast(self, s: str) -> Node:
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
    #@+node:ekr.20240529060232.3: *3* CheckLeo.read
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
    #@+node:ekr.20240529060232.5: *3* CheckLeo.scan_file
    def scan_file(self, path: str, tree: Node) -> dict:
        """
        Scan the tree for all classes and their methods.
        
        Set self.d[path] to an inner dict describing all classes in path.
        """
        # Keys are class names; values are lists of methods.
        classes: dict[str, list[str]] = {}
        # Keys are class_names; values are ClassDef nodes.
        class_trees: dict[str, Node] = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_name = node.name
                class_trees[class_name] = node
                methods = []
                for node2 in ast.walk(node):
                    # This finds inner defs as well as methods.
                    if isinstance(node2, ast.FunctionDef):
                        args = node2.args.args
                        is_method = args and args[0].arg == 'self'
                        if is_method:
                            methods.append(node2.name)
                classes[class_name] = list(sorted(methods))
        assert path not in self.d, path
        self.d[path] = {
            'classes': classes,
            'class_trees': class_trees,
        }
    #@-others
#@-others

CheckLeo().check_leo()
#@-leo

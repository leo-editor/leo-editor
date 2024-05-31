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
import sys
import time
from typing import Optional

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
    add('--debug', dest='debug', action='store_true',
        help='enable debugging')
    add('--report', dest='report', action='store_true',
        help='show summary report')

    # Create the return values.
    parser.set_defaults(all=False, report=False)
    args = parser.parse_args()

    # Return a dict describing the settings.
    return {
        'all': bool(args.all),
        'debug': bool(args.debug),
        'report': bool(args.report),
    }
#@+node:ekr.20240529063157.1: ** Class CheckLeo
class CheckLeo:

    __slots__ = ('all', 'debug', 'report')

    #@+others
    #@+node:ekr.20240529063012.1: *3* CheckLeo.check_leo & helpers
    def check_leo(self) -> None:
        """Check all files returned by get_leo_paths()."""
        t1 = time.process_time()
        settings_d = scan_args()
        # Init the switches.
        g.trace(settings_d)
        self.all: bool = settings_d['all']
        self.debug: bool = settings_d['debug']
        self.report: bool = settings_d['report']

        # Keys are paths, values are a dict of dicts containing other data.
        files_dict: dict[str, dict[str, dict]] = {}

        # Scan and check all files, updating the files_dict.
        for path in self.get_leo_paths():
            s = self.read(path)
            tree = self.parse_ast(s)
            self.scan_file(files_dict, path, tree)
            #### self.check_file(files_dict, path, tree)
        t2 = time.process_time()

        if self.report:
            self.dump_dict(files_dict)
        print('')
        g.trace(f"done {(t2-t1):4.2} sec.")
    #@+node:ekr.20240529060232.5: *4* CheckLeo.scan_file
    def scan_file(self, files_dict: dict[str, dict], path: str, tree: Node) -> None:
        """
        Scan the tree for all classes and their methods.
        
        Set file_dict [path] to an inner dict describing all classes in path.
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
        assert path not in files_dict, path
        files_dict[path] = {
            'classes': classes,
            'class_trees': class_trees,
        }
    #@+node:ekr.20240531104205.1: *3* CheckLeo: utils
    #@+node:ekr.20240529061932.1: *4* CheckLeo.dump_dict
    def dump_dict(self, files_dict: dict[str, dict[str, dict]]) -> None:

        for path in files_dict:
            short_file_name = g.shortFileName(path)
            inner_dict = files_dict.get(path, {})
            # Dump the classes dict.
            classes_dict: dict[str, list[str]] = inner_dict.get('classes', {})
            if classes_dict:
                print('')
                print(f"{short_file_name}...")
                print(f"{'class':>25}: methods")
                for class_name in classes_dict:
                    methods = classes_dict.get(class_name)
                    print(f"{class_name:>25}: {len(methods)}")  # type:ignore
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

        # Return the list of files.
        return (
             glob.glob(f"{core_dir}{os.sep}leo*.py") +
             glob.glob(f"{command_dir}{os.sep}leo*.py") +
             glob.glob(f"{plugins_dir}{os.sep}qt_*.py")
        )
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
    #@-others
#@-others

CheckLeo().check_leo()
#@-leo

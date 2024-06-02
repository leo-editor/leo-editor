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
from leo.core.leoQt import QtWidgets
assert g
assert os.path.exists(leo_editor_dir), leo_editor_dir

Node = ast.AST
#@-<< check_leo.py: imports & annotations >>

#@+others
#@+node:ekr.20240530073251.1: **  function: scan_args (check_leo.py)
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
#@+node:ekr.20240531142811.1: ** class ClassInfo
class ClassInfo:

    def __init__(self, class_name: str, class_node: ast.ClassDef, path: str) -> None:
        self.class_name = class_name
        self.class_node = class_node
        self.path = path

    def class_id(self):
        return f"ClassInfo<{self.path}::{self.class_name}>"
#@+node:ekr.20240531143136.1: ** class FileInfo
class FileInfo:

    def __init__(self, file_node: ast.Module, path: str) -> None:
        self.file_node = file_node
        self.path = path

    def class_id(self):
        return f"FileInfo<{g.shortFileName(self.path)}>"
#@+node:ekr.20240529063157.1: ** class CheckLeo
class CheckLeo:

    __slots__ = (
        # command-line arguments.
        'all', 'debug', 'report',
        # status ivars.
        'class_name_printed', 'header_printed',
        # global summary data.
        ### 'classes_dict',  # Keys are paths; values are ClassDef nodes.
        # 'files_dict',  # Keys are paths; values are ast (ast.Module) nodes.
        'base_class_dict', 'live_objects_dict',
    )

    #@+others
    #@+node:ekr.20240529063012.1: *3* 1: CheckLeo.check_leo
    def check_leo(self) -> None:
        """Check all files returned by get_leo_paths()."""
        # Settings ivars...
        settings_d = scan_args()
        g.trace(settings_d)
        self.all: bool = settings_d['all']
        self.debug: bool = settings_d['debug']
        self.report: bool = settings_d['report']
        # Keys: class names. Values: instances of that class.
        t1 = time.process_time()
        self.live_objects_dict: dict[str, list[str]] = self.init_live_objects_dict()
        # Check each file separately.
        for path in self.get_leo_paths():
            self.check_file(path)
        t2 = time.process_time()
        print('')
        g.trace(f"done {(t2-t1):4.2} sec.")
    #@+node:ekr.20240602162342.1: *3* 2: CheckLeo.check_file
    def check_file(self, path):
        """Check the file whose full path is given."""
        s = self.read(path)
        self.header_printed: bool = False
        chains: set[str] = set()  # All chains in the file.
        file_node = self.parse_ast(s)
        class_nodes = [
            z for z in ast.walk(file_node)
                if isinstance(z, ast.ClassDef)]
        for class_node in class_nodes:
            self.check_class(chains, class_node, path)
        if self.report and chains:
            print('')
            g.printObj(
                list(sorted(chains)),
                tag=f"chains: {g.shortFileName(path)}")

    #@+node:ekr.20240602161721.1: *3* 3: CheckLeo.check_class & helper
    def check_class(self, chains: set[str], class_node: ast.ClassDef, path: str) -> None:
        """Check that all called methods exist."""
        g.trace(class_node.name)
        self.class_name_printed = False
        methods = self.find_methods(class_node)
        called_names = self.find_calls(chains, class_node)
        for called_name in called_names:
            self.check_called_name(called_name, class_node, methods, path)
    #@+node:ekr.20240602165136.1: *4* CheckLeo.find_methods
    def find_methods(self, class_node: ast.ClassDef) -> list[ast.ClassDef]:
        """Return a list of all methods in the give class."""
        return [
            z for z in ast.walk(class_node)
            if (
                isinstance(z, ast.FunctionDef)
                and z.args.args
                and z.args.args[0].arg == 'self'
            )
        ]
    #@+node:ekr.20240531085654.1: *4* CheckLeo.find_calls
    def find_calls(self,
        chains: set[str],
        class_node: ast.ClassDef,
    ) -> list[str]:
        """
        Return all the method *names* of the class.
        
        Side effect: update all the chains.
        """
        assert isinstance(class_node, ast.ClassDef), repr(class_node)
        attrs: set[str] = set()
        for node in class_node.body:
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
                            if 0:  # Dump the entire call chain.
                                chains.add(ast.unparse(node2.func))
                            else:  # Dump only the prefix.
                                prefix = ast.unparse(node2.func).split('.')[:-1]
                                chains.add('.'.join(prefix))
        ### g.printObj(list(sorted(attrs)), tag=f"do_class_body: {class_node.name}")
        return list(sorted(attrs))
    #@+node:ekr.20240531090243.1: *3* 4: CheckLeo.check_called_name & helper
    def check_called_name(self,
        called_name: str,
        class_node: ast.ClassDef,
        methods: list[ast.FunctionDef],  # All methods of this class.
        path: str,
    ) -> None:
        class_name = class_node.name
        if self.has_called_method(called_name, class_node, methods):
            return
        # Print the file header.
        if not self.header_printed:
            self.header_printed = True
            print(f"{g.shortFileName(path)}: missing 'self' methods...")
        # Print the class header.
        if not self.class_name_printed:
            self.class_name_printed = True
            bases = class_node.bases
            if bases:
                bases_s = ','.join([ast.unparse(z) for z in bases])
                bases_list = f"({bases_s})"
            else:
                bases_list = ''
            print(f"  class {class_name}{bases_list}:")
        # Print the unknown called name.
        print(f"    self.{called_name}")
    #@+node:ekr.20240602105914.1: *4* CheckLeo.has_called_method (FIX)
    def has_called_method(self,
        called_name: str,
        class_node: ast.ClassDef,
        methods: list[str],
    ) -> bool:
        trace = False  ###
        if called_name in methods:
            return True
        # Return if there are no base classes.
        bases = class_node.bases
        if not bases:
            return False
        if 0:
            class_name = class_node.name
            bases_s = ','.join([ast.unparse(z) for z in bases])
            g.trace(f"=== call {class_name}.{called_name} ({bases_s})")
        for base in bases:
            live_object = self.live_objects_dict.get(ast.unparse(base))
            if not live_object:
                continue
            # g.trace('=== live_object!', live_object)
            method_names = list(dir(live_object))
            if called_name in method_names:
                if trace:
                    g.trace(f"=== {called_name} found in {live_object.__class__.__name__}")
                return True
            return False
    #@+node:ekr.20240602103522.1: *3* CheckLeo.init_live_objects_dict
    def init_live_objects_dict(self):

        # Create the app first.
        app = QtWidgets.QApplication([])
        assert app
        qt_widget_classes = [
            QtWidgets.QComboBox,
            QtWidgets.QDateTimeEdit,
            QtWidgets.QLineEdit,
            QtWidgets.QMainWindow,
            QtWidgets.QMessageBox,
            QtWidgets.QTabBar,
            QtWidgets.QTabWidget,
            QtWidgets.QTreeWidget,
        ]
        d = {}
        for widget_class in qt_widget_classes:
            w = widget_class()
            full_class_name = f"QtWidgets.{w.__class__.__name__}"
            d[full_class_name] = w
        return d
    #@+node:ekr.20240531104205.1: *3* CheckLeo: utils
    #@+node:ekr.20240529094941.1: *4* CheckLeo.get_leo_paths (test_one_file switch)
    def get_leo_paths(self) -> list[str]:
        """Return a list of full paths to Leo paths to be checked."""

        test_one_file = True

        def join(*args) -> str:
            return os.path.abspath(os.path.join(*args))

        # Compute the directories.
        leo_dir = join(leo_editor_dir, 'leo')
        command_dir = join(leo_dir, 'commands')
        core_dir = join(leo_dir, 'core')
        plugins_dir = join(leo_dir, 'plugins')
        for z in (leo_dir, command_dir, core_dir, plugins_dir):
            assert os.path.exists(z), z

        if test_one_file:
            file_name = f"{plugins_dir}{os.sep}qt_gui.py"
            print('')
            print('Testing one file', g.shortFileName(file_name))
            print('')
            return [file_name]

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

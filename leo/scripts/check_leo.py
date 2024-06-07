#@+leo-ver=5-thin
#@+node:ekr.20240529053756.1: * @file ../scripts/check_leo.py
#@+<< check_leo.py: docstring >>
#@+node:ekr.20240604203402.1: ** << check_leo.py: docstring >>
"""
check_leo.py: A script that checks for undefined methods in Leo's core code.

This script demonstrates that mypy, pylint and ruff *might* provide stronger checks.

This script is pragmatic:
    
- It uses Leo-specic knowledge to simplify the code.
- It uses ast.walk rather than using somewhat faster visitors.
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
import sys
import time
from typing import Any, Optional

# Add the leo/editor folder to sys.path.
leo_editor_dir = os.path.abspath(os.path.join(__file__, '..', '..', '..'))
if leo_editor_dir not in sys.path:
    sys.path.insert(0, leo_editor_dir)

from leo.core import leoGlobals as g
# Imports for live objects.
from leo.core.leoQt import QtWidgets
import leo.core.leoColorizer as leoColorizer
import leo.core.leoGui as leoGui
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
#@+node:ekr.20240530073251.1: *3* function: scan_args (check_leo.py)
def scan_args() -> dict[str, bool]:  # pragma: no cover
    """Scan command-line arguments for check_leo.py"""
    parser = argparse.ArgumentParser(
        description= 'check_leo.py: check all leo files or a given list of files',
        formatter_class=argparse.RawTextHelpFormatter,
    )
    add = parser.add_argument

    # Arguments.
    add('PATHS', nargs='*', help='list of files, relative to the leo directory')
    add('--all', dest='all', action='store_true',
        help='check all files, even unchanged files')

    # Create the return values.
    parser.set_defaults(all=False, report=False)
    args = parser.parse_args()

    # Return a dict describing the settings.
    return {
        'all': bool(args.all),
        'files': args.PATHS,
    }
#@+node:ekr.20240529063157.1: ** class CheckLeo
class CheckLeo:

    __slots__ = (
        # command-line arguments.
        'all', 'files',
        # global data.
        'all_classes_dict',
        'class_methods_dict',
        'extra_methods_dict',
        'live_objects',
        'live_objects_dict',
        'missing_base_classes',
        'n_missing',
    )

    #@+others
    #@+node:ekr.20240529063012.1: *3* 1: CheckLeo.check_leo & helpers
    def check_leo(self) -> None:
        """Check all files returned by get_leo_paths()."""
        t1 = time.process_time()
        #@+<< check_leo: define all ivars >>
        #@+node:ekr.20240603192905.1: *4* << check_leo: define all ivars >>
        # Settings ivars...
        settings_d = scan_args()
        g.trace(settings_d)
        self.all: bool = settings_d['all']
        self.files = settings_d['files']

        # Keys: bare class names.  Values: list of method names.
        self.class_methods_dict: dict[str, list[str]] = {}

        # Keys: bare class names. Values: list of extra methods of that class.
        self.extra_methods_dict: dict[str, list[str]] = self.init_extra_methods_dict()

        self.live_objects: list[Any] = []  # References to live objects.

        # Keys: bare class names. Values: instances of that class.
        self.live_objects_dict: dict[str, Any] = self.init_live_objects_dict()
        self.missing_base_classes: set[str] = set()  # Names of all missing base classes.

        # Add 'Thread to missing_base_classes. It's too risky to instanciate it.
        self.missing_base_classes.add('Thread')

        self.n_missing = 0  # The number of missing methods.
        #@-<< check_leo: define all ivars >>

        # Check each file separately.
        for path in self.get_leo_paths():
            self.scan_file(path)
        t2 = time.process_time()
        g.trace(f"{self.n_missing} missing method{g.plural(self.n_missing)}")
        g.trace(f"done {(t2-t1):4.2} sec.")

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

        # Compute all candidate files.
        all_leo_files = (
               glob.glob(f"{core_dir}{os.sep}leo*.py")
             + glob.glob(f"{command_dir}{os.sep}leo*.py")
             + glob.glob(f"{plugins_dir}{os.sep}qt_*.py")
        )

        if self.all:  # Check all files.
            return all_leo_files

        # Return only changed files.
        modified_files = (
              g.getModifiedFiles(leo_dir)
            + g.getModifiedFiles(command_dir)
            + g.getModifiedFiles(plugins_dir)
        )
        return [z for z in all_leo_files if z in modified_files]
    #@+node:ekr.20240602051423.1: *4* CheckLeo.init_extra_methods_dict
    def init_extra_methods_dict(self) -> dict[str, list[str]]:
        """
        Init the Leo-specific data for base classes.
        
        Return a dict: keys are *unqualified* class mames.
        Values are list of methods defined in that class, including base classes.
        """
        # self.(\w+)  ==> '\1',
        return {
            'DynamicWindow': ['func', 'oldEvent'],
            'EventWrapper': ['func', 'oldEvent'],
            'IdleTime': ['handler'],
            'LeoFind': ['escape_handler', 'handler'],
            'LeoFrame': ['iconBarClass', 'statusLineClass'],
            'LeoQtTree': ['headlineWrapper', 'sizeTreeEditor'],
            'LeoTree': [
                'setItemForCurrentPosition',  # Might exist in subclasses.
                'unselectItem',
            ],
            'LeoQtTreeTab': [
                'setSizeAdjustPolicy',  ### A method of the inner LeoQComboBox class
            ],
            'PygmentsColorizer': [
                # Bad style? Could use regular methods.
                'getFormat', 'getDefaultFormat', 'setFormat',
            ],
            'QTextMixin': [
                # Bad style: These are defined in other classes!
                'getAllText', 'getInsertPoint', 'getSelectionRange',
                'see', 'setAllText', 'setInsertPoint', 'setSelectionRange',
            ],
            'RstCommands': ['user_filter_b', 'user_filter_h'],
            'SqlitePickleShare': ['dumper', 'loader'],
            'VimCommands': [
                'LoadFileAtCursor', 'Substitution', 'Tabnew',  # ctors for inner classes.
                'handler', 'motion_func',
            ],
            'Xdb': [
                'QueueStdin', 'QueueStdout',  # ctors for inner classes.
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
        app = QtWidgets.QApplication([])
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

        # 2. Add various other live objects:
        result['dict'] = {}
        result['Pdb'] = pdb.Pdb()
        ### result['Thread'] = threading.Thread()

        # 3. Add Leo base classes.
        result['BaseColorizer'] = leoColorizer.BaseColorizer(c=None)
        result['LeoGui'] = leoGui.LeoGui(guiName='NullGui')
        result['LeoQtGui'] = leoGui.LeoGui(guiName='NullGui')  # Do *not* instantiate the real class.
        result['PygmentsColorizer'] = leoColorizer.PygmentsColorizer(c=None, widget=None)

        # g.printObj(list(sorted(result.keys())), tag='live_objects_dict')
        return result
    #@+node:ekr.20240602162342.1: *3* 2: CheckLeo.scan_file & helpers
    def scan_file(self, path):
        """Scan the file and update global data."""
        s = self.read(path)
        if not s:
            g.trace(f"file not found: {path}")
            return
        file_node = self.parse_ast(s)
        class_nodes = [
            z for z in ast.walk(file_node)
                if isinstance(z, ast.ClassDef)]
        # Pass 1: create the class_methods_dict.
        for class_node in class_nodes:
            self.scan_class(class_node, path)

        # Pass 2: check all classes.
        for class_node in class_nodes:
            self.check_class(class_node, path)
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
    #@+node:ekr.20240602165136.1: *4* CheckLeo.find_methods
    def find_methods(self, class_node: ast.ClassDef) -> list[ast.FunctionDef]:
        """Return a list of all methods in the give class."""

        def has_self(func_node: ast.FunctionDef) -> bool:
            """Return True if the given FunctionDef node has 'self' as its first argument."""
            # arguments = (arg* args, ...)
            # arg = (identifier arg, ...)
            args = func_node.args
            if not args:
                return False
            first_arg = args.args[0] if args.args else None
            return first_arg and first_arg.arg == 'self'

        return [
            z for z in ast.walk(class_node)
                if isinstance(z, ast.FunctionDef) and has_self(z)]
    #@+node:ekr.20240606205913.1: *3* 4: CheckLeo.check_class & helpers
    def check_class(self, class_node: ast.ClassDef, path: str) -> None:
        """Check the class for calls to undefined methods."""
        class_name = bare_name(class_node.name)
        called_names = self.find_calls(class_node)
        method_names = self.class_methods_dict[class_name]
        for called_name in called_names:
            self.check_called_name(called_name, class_node, method_names, path)
    #@+node:ekr.20240531090243.1: *4* CheckLeo.check_called_name
    def check_called_name(self,
        called_name: str,
        class_node: ast.ClassDef,
        method_names: list[str],  # List of all method names in this class.
        path: str,
    ) -> None:
        self.has_called_method(called_name, class_node, method_names, path)
    #@+node:ekr.20240531085654.1: *4* CheckLeo.find_calls
    def find_calls(self, class_node: ast.ClassDef) -> list[str]:
        """Return all the method *names* of the class."""
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
        return list(sorted(attrs))
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
                        print('')
                        g.trace(
                            f"==== Missing base class: {bare_base_class_name!r} "
                            f"in {g.shortFileName(path)}")

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
        g.trace(
            f"{g.shortFileName(path):>15} {called_name:>20} "
            f"not in {class_name}{bases_signature_s}")
        return False
    #@-others
#@-others

CheckLeo().check_leo()
#@-leo

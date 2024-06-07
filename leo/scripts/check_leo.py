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
- It assumes that all base class names are globally unique.
"""
#@-<< check_leo.py: docstring >>
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
#@+node:ekr.20240606204736.1: ** top-level functions: check_leo.py
#@+node:ekr.20240606203244.1: *3* function: bare_class_name (check_leo.py)
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
    # add('--debug', dest='debug', action='store_true',
    #    help='enable debugging')
    add('--report', dest='report', action='store_true',
        help='show summary report')

    # Create the return values.
    parser.set_defaults(all=False, report=False)
    args = parser.parse_args()

    # Return a dict describing the settings.
    return {
        'all': bool(args.all),
        # 'debug': bool(args.debug),
        'files': args.PATHS,
        'report': bool(args.report),
    }
#@+node:ekr.20240529063157.1: ** class CheckLeo
class CheckLeo:

    __slots__ = (
        # command-line arguments.
        'all', 'files', 'report',
        # status ivars.
        'class_name_printed',
        'header_printed',
        # global data.
        'all_classes_dict',
        'class_methods_dict',
        ### 'class_tree_dict',
        'extra_methods_dict',
        'live_objects',
        'live_objects_dict',
        'report_list',
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
        self.report: bool = settings_d['report']
        self.files = settings_d['files']

        # Keys: bare class names.  Values: list of method names.
        self.class_methods_dict: dict[str, list[str]] = {}

        # Keys: bare class names.  Values: ast.ClassDef nodes.
        ### class_tree_dict: dict[str, ast.ClassDef] = {}

        # Keys: bare class names. Values: list of extra methods of that class.
        self.extra_methods_dict: dict[str, list[str]] = self.init_extra_methods_dict()

        # Keys: class names, excluding qualifiers. Values: instances of that class.
        self.live_objects: list = []
        self.live_objects_dict: dict[str, list[str]] = self.init_live_objects_dict()

        # A list of queued strings to be printed later.
        self.report_list: list[str] = []
        #@-<< check_leo: define all ivars >>

        # Check each file separately.
        for path in self.get_leo_paths():
            self.scan_file(path)
        t2 = time.process_time()
        # Print all failures.
        print('')
        for z in self.report_list:
            print(z)
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
        ### self.(\w+)  ==> '\1',
        return {
            'Calendar': [  # QtWidgets.QDialog.
                'setLayout',
            ],
            'DateTimeEditStepped': [  # QtWidgets.QDateTimeEdit
                'currentSection',
            ],
            'DialogWithCheckBox': [  #QtWidgets.QMessageBox
                'addButton', 'layout',
                'setIcon', 'setObjectName',
                'setText', 'setWindowTitle',
            ],
            'IdleTime': [
                'handler',  # An ivar set to an executable.
            ],
            'LeoQtGui': [  # leoGui.LeoGui
                'DialogWithCheckBox',  # Inner class.
                # These are QtWidgets.QMessageBox methods called from the inner class.
                ### This is a buglet.
                'addButton', 'currentSection', 'layout',
                'setIcon', 'setLayout', 'setObjectName',
                'setText', 'setWindowTitle',
            ],
            'LeoQtTree': [
                # LeoTree methods.
                'OnIconDoubleClick', 'select',
                'sizeTreeEditor',  # Static method.
                # Alias ivars.
                'headlineWrapper',  # Alias for qt_text.QHeadlineWrapper
            ],
            'SqlitePickleShare': [
                'dumper', 'loader',  # Alias ivars.
            ],
            'LeoLineTextWidget': [  # QtWidgets.QFrame
                'setFrameStyle',
            ],
            'LeoQListWidget': [  # QListWidget.
                'activateWindow', 'addItems',
                'clear', 'currentItem',
                'deleteLater', 'geometry',
                'setCurrentRow', 'setFocus', 'setGeometry', 'setWindowFlags',
                'viewport', 'windowFlags',
            ],
            'LeoQTextBrowser': [  # QtWidgets.QTextBrowser
                'LeoQListWidget',  # Private class.
                'calc_hl',  # Static methods.
                # Methods of base class.
                'activateWindow', 'addItems',
                'clear', 'currentItem', 'deleteLater', 'geometry',
                'setContextMenuPolicy', 'setCurrentRow', 'setCursorWidth',
                'setFocus', 'setGeometry', 'setWindowFlags',
                'verticalScrollBar', 'viewport', 'windowFlags',
            ],
            'NumberBar': [  # QtWidgets.QFrame
                'fontMetrics',
                'setFixedWidth',
                'setObjectName',
                'width',
            ],
            'QTextEditWrapper': [  # QTextMixin
                'rememberSelectionAndScroll',
            ],
            'QTextMixin': [
                # These are defined in other classes!
                ### Is this a bug?
                'getAllText', 'getInsertPoint', 'getSelectionRange',
                'see', 'setAllText', 'setInsertPoint', 'setSelectionRange',
            ],
        }
    #@+node:ekr.20240602103522.1: *4* CheckLeo.init_live_objects_dict
    def init_live_objects_dict(self):

        # Create the app first.
        app = QtWidgets.QApplication([])
        self.live_objects.append(app)  # Otherwise all widgets will go away.
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
        # Make sure live objects don't get deallocated.
        d = {}
        for widget_class in qt_widget_classes:
            w = widget_class()
            full_class_name = f"QtWidgets.{w.__class__.__name__}"
            d[full_class_name] = w
        return d
    #@+node:ekr.20240602162342.1: *3* 2: CheckLeo.scan_file & helpers
    def scan_file(self, path):
        """Scan the file and update global data."""
        s = self.read(path)
        if not s:
            g.trace(f"file not found: {path}")
            return
        self.header_printed: bool = False
        ### chains: set[str] = set()  # All chains in the file.
        file_node = self.parse_ast(s)
        class_nodes = [
            z for z in ast.walk(file_node)
                if isinstance(z, ast.ClassDef)]
        # Pass 1: create the class_methods_dict.
        for class_node in class_nodes:
            ### self.scan_class(chains, class_node, path)
            self.scan_class(class_node, path)
        # Pass 2: check all classes.
        for class_node in class_nodes:
            self.check_class(class_node, path)
        ###
            # if self.report and chains:
                # print('')
                # g.printObj(
                    # list(sorted(chains)),
                    # tag=f"chains: {g.shortFileName(path)}")

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
        self.class_name_printed = False
        class_name = bare_name(class_node.name)
        methods: list[ast.FunctionDef] = self.find_methods(class_node)
        method_names = [z.name for z in methods]
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
        class_name = class_node.name
        if self.has_called_method(called_name, class_node, method_names):
            return
        # Print the file header.
        if not self.header_printed:
            self.header_printed = True
            self.report_list.append(
                f"{g.shortFileName(path)}: missing 'self' methods...")
        # Print the class header.
        if not self.class_name_printed:
            self.class_name_printed = True
            bases = class_node.bases
            if bases:
                bases_s = ','.join([ast.unparse(z) for z in bases])
                bases_list = f"({bases_s})"
            else:
                bases_list = ''
            self.report_list.append(f"  class {class_name}{bases_list}:")
        # Print the unknown called name.
        self.report_list.append(f"    self.{called_name}")
    #@+node:ekr.20240531085654.1: *4* CheckLeo.find_calls
    def find_calls(self, class_node: ast.ClassDef) -> list[str]:  ### chains: set[str],
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
                        ###
                            # else:
                                # if 0:  # Dump the entire call chain.
                                    # chains.add(ast.unparse(node2.func))
                                # else:  # Dump only the prefix.
                                    # prefix = ast.unparse(node2.func).split('.')[:-1]
                                    # chains.add('.'.join(prefix))
        return list(sorted(attrs))
    #@+node:ekr.20240602105914.1: *4* CheckLeo.has_called_method
    def has_called_method(self,
        called_name: str,
        class_node: ast.ClassDef,
        method_names: list[str],
    ) -> bool:
        trace = True

        # Check the obvious names.
        if called_name in method_names:
            return True

        class_name = bare_name(class_node.name)

        # Check base classes.
        bases = class_node.bases
        bases_list = [ast.unparse(z) for z in bases]
        bases_s = ','.join(bases_list)
        if bases:
            if 0:
                g.trace(f"=== call {class_name}.{called_name} ({bases_s})")
            for base in bases:
                # First, check the live objects.
                bare_base_class_name = bare_name(ast.unparse(base))
                live_object = self.live_objects_dict.get(bare_base_class_name)
                if not live_object:
                    continue
                g.trace('=== live_object!', live_object)
                lib_object_method_names = list(dir(live_object))
                if called_name in lib_object_method_names:
                    if trace:
                        g.trace(f"=== {called_name} found in {live_object.__class__.__name__}")
                    return True

                ### Second, check the static classes, if they exist.



        # Finally, check special cases.
        extra_methods = self.extra_methods_dict.get(class_name, [])
        if trace and called_name not in extra_methods:
            g.trace(f"{called_name:>20} not in extra methods for {class_name}({bases_s})")
        return called_name in extra_methods
    #@-others
#@-others

CheckLeo().check_leo()
#@-leo

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
        'base_class_dict', 'files_dict', 'live_objects_dict',
    )

    #@+others
    #@+node:ekr.20240529063012.1: *3* CheckLeo.check_leo & helpers
    def check_leo(self) -> None:
        """Check all files returned by get_leo_paths()."""
        t1 = time.process_time()
        #@+<< check_leo: init ivars >>
        #@+node:ekr.20240602103712.1: *4* << check_leo: init ivars >>
        # Settings...
        settings_d = scan_args()
        g.trace(settings_d)
        self.all: bool = settings_d['all']
        self.debug: bool = settings_d['debug']
        self.report: bool = settings_d['report']

        # Keys: class mames. Values: all methods of that class, including base classes.
        self.base_class_dict: dict[str, list[str]] = self.init_base_class_dict()

        # Keys are paths, values are a dict of dicts containing other data.
        self.files_dict: dict[str, dict[str, dict]] = {}

        # Keys: class names. Values: instances of that class.
        self.live_objects_dict: dict[str, list[str]] = self.init_live_objects_dict()
        #@-<< check_leo: init ivars >>
        for path in self.get_leo_paths():
            s = self.read(path)
            tree: Node = self.parse_ast(s)  # type:ignore
            self.scan_file(path, tree)
            self.check_file(path, tree)
        t2 = time.process_time()

        if self.report:
            self.dump_dict(self.files_dict)
        print('')
        g.trace(f"done {(t2-t1):4.2} sec.")
    #@+node:ekr.20240602051423.1: *4* CheckLeo.init_base_class_dict
    def init_base_class_dict(self):
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
        assert app
        qt_widget_classes = [
            QtWidgets.QComboBox,
            QtWidgets.QLineEdit,
            QtWidgets.QMainWindow,
            QtWidgets.QTabBar,
            QtWidgets.QTabWidget,
            QtWidgets.QTreeWidget,
        ]
        d = {}
        for widget_class in qt_widget_classes:
            w = widget_class()
            d[w.__class__.__name__] = w
        return d
    #@+node:ekr.20240529060232.5: *4* CheckLeo.scan_file
    def scan_file(self, path: str, tree: Node) -> None:
        """
        Scan the tree for all classes and their methods.
        
        Set file_dict [path] to an inner dict describing all classes in path.
        """
        # Keys are class names; values are lists of methods.
        classes_dict: dict[str, list[str]] = {}
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
                classes_dict[class_name] = list(sorted(methods))
        assert path not in self.files_dict, path
        self.files_dict[path] = {
            'classes': classes_dict,
            'class_trees': class_trees,
        }
    #@+node:ekr.20240529135047.1: *4* CheckLeo.check_file & helpers
    def check_file(self, path: str, tree: Node) -> None:
        """
        Check that all called methods exist.
        """
        self.class_name_printed: bool = False
        self.header_printed: bool = False
        inner_dict = self.files_dict.get(path, {})

        # Keys are class names.
        classes_dict: dict[str, list[str]] = inner_dict.get('classes', {})
        trees_dict: dict[str, ast.ClassDef] = inner_dict.get('class_trees', {})
        chains: set[str] = set()
        if classes_dict:
            for class_name in classes_dict:
                self.class_name_printed = False
                class_node: ast.ClassDef = trees_dict.get(class_name)  # type:ignore
                attrs = self.do_function_body(chains, class_node, path)
                if attrs:
                    self.check_attrs(attrs, classes_dict, class_name, class_node, path)
        if self.report and chains:
            print('')
            g.printObj(list(sorted(chains)), tag=f"chains: {g.shortFileName(path)}")

    #@+node:ekr.20240531090243.1: *5* CheckLeo.check_attrs
    def check_attrs(self,
        attrs: list[str],
        classes_dict: dict[str, list[str]],
        class_name: str,
        class_node: ast.ClassDef,
        path: str,
    ) -> None:

        ### if any(is_missing(z) for z in attrs):
        methods: list[str] = classes_dict.get(class_name, [])
        if any(self.is_missing_method(class_name, methods, z) for z in attrs):
            # Print the file header.
            if not self.header_printed:
                self.header_printed = True
                print(f"{g.shortFileName(path)}: missing 'self' methods...")
            # Print the class header.
            if not self.class_name_printed:
                self.class_name_printed = True
                bases = ast.unparse(class_node.bases)  # type:ignore
                bases_s = f" [{bases}]" if bases else ''
                print(f"  class {class_name}{bases_s}:")
            # Print the unknown methods.
            for attr in sorted(list(attrs)):
                if self.is_missing_method(class_name, methods, attr):
                    print(f"    self.{attr}")
    #@+node:ekr.20240531085654.1: *5* CheckLeo.do_function_body
    def do_function_body(self, chains: set[str], class_node: ast.ClassDef, path: str) -> list[str]:
        """Update attrs."""
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
                            # print('****', ast.unparse(node2))
                            # print('....', ast.unparse(node2.func))
                            if 0:  # Dump the entire call chain.
                                chains.add(ast.unparse(node2.func))
                            else:  # Dump only the prefix.
                                prefix = ast.unparse(node2.func).split('.')[:-1]
                                chains.add('.'.join(prefix))
        return list(sorted(attrs))
    #@+node:ekr.20240602105914.1: *5* CehckLeo.is_missing_method
    def is_missing_method(self,
        class_name: str,
        methods: list[str],
        method_name: str,
    ) -> bool:

        if method_name in methods:
            return False
        return True
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
    #@+node:ekr.20240529094941.1: *4* CheckLeo.get_leo_paths (test_one_file switch)
    def get_leo_paths(self) -> list[str]:
        """Return a list of full paths to Leo paths to be checked."""

        test_one_file = False

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
            file_name = f"{plugins_dir}{os.sep}qt_tree.py"
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

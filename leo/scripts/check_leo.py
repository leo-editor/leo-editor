#@+leo-ver=5-thin
#@+node:ekr.20240529053756.1: * @file ../scripts/check_leo.py
"""
check_leo.py: Experimental script that checks for undefined methods.
"""
#@+<< check_leo.py: imports & annotations >>
#@+node:ekr.20240529055116.1: ** << check_leo.py: imports & annotations >>
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
#@+node:ekr.20240529063157.1: ** Class CheckLeo
class CheckLeo:

    def __init__(self):
        # Keys are full path names to Leo files.
        # Values are dicts describing all the files classes.
        self.d: dict[str, dict] = {}

    #@+others
    #@+node:ekr.20240529063012.1: *3* CheckLeo.check_leo
    def check_leo(self) -> None:
        """Check all files returned by get_leo_paths()."""
        t1 = time.process_time()
        for path in self.get_leo_paths():
            s = self.read(path)
            tree = self.parse_ast(s)
            # print(AstDumper().dump_ast(tree))
            self.scan_file(path, tree)
        t2 = time.process_time()
        if 1:
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
                print(f"file: {short_file_name:<20} class: methods")
                # print(f"{'class':>24}: methods")
            for class_name in classes_dict:
                methods = classes_dict.get(class_name)
                print(f"  {class_name:>30}: {len(methods)}")
    #@+node:ekr.20240529094941.1: *3* CheckLeo.get_leo_paths
    def get_leo_paths(self) -> list[str]:
        """Return a list of full paths to Leo paths to be checked."""

        def join(*args) -> str:
            return os.path.abspath(os.path.join(*args))

        leo_dir = join(leo_editor_dir, 'leo')
        command_dir = join(leo_dir, 'commands')
        core_dir = join(leo_dir, 'core')
        plugins_dir = join(leo_dir, 'plugins')
        for z in (leo_dir, command_dir, core_dir, plugins_dir):
            assert os.path.exists(z), z
        core_files = glob.glob(f"{core_dir}{os.sep}leo*.py")
        command_files = glob.glob(f"{command_dir}{os.sep}leo*.py")
        plugins_files = glob.glob(f"{plugins_dir}{os.sep}qt_*.py")
        return core_files + command_files + plugins_files
        # path = os.path.abspath(os.path.join(core_dir, 'leoCommands.py'))
        # return [path]
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
        # Find all classes and their methods.
        classes: dict[str, list[str]] = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_name = node.name
                methods = []
                for node2 in ast.walk(node):
                    # This finds inner defs as well as methods.
                    if isinstance(node2, ast.FunctionDef):
                        args = node2.args.args
                        is_method = args and args[0].arg == 'self'
                        if is_method:
                            args_s = ', '.join(z.arg for z in args)
                            methods.append(f"{node2.name} ({args_s})")
                classes[class_name] = list(sorted(methods))
        assert path not in self.d, path
        self.d[path] = {'classes': classes}
        ### return classes
    #@-others
#@-others

CheckLeo().check_leo()
#@-leo

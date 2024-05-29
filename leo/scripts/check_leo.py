#@+leo-ver=5-thin
#@+node:ekr.20240529053756.1: * @file ../scripts/check_leo.py
"""
check_leo.py: Experimental script that checks for undefined methods.
"""
#@+<< check_leo.py: imports & annotations >>
#@+node:ekr.20240529055116.1: ** << check_leo.py: imports & annotations >>
import ast
import os
import sys

# Add the leo/editor folder to sys.path.
leo_editor_dir = os.path.abspath(os.path.join(__file__, '..', '..', '..'))
if leo_editor_dir not in sys.path:
    sys.path.insert(0, leo_editor_dir)
    
leo_dir = os.path.abspath(os.path.join(leo_editor_dir, 'leo'))
    
# No need to change
if 0:
    os.chdir(leo_dir)
    print('cwd:', os.getcwd())

from leo.core import leoGlobals as g
# from leo.core.leoAst import AstDumper
# assert AstDumper

assert g
assert os.path.exists(leo_editor_dir), leo_editor_dir
assert os.path.exists(leo_dir), leo_dir

Node = ast.AST
#@-<< check_leo.py: imports & annotations >>
#@+others
#@+node:ekr.20240529061932.1: ** funciont: dump_dict
def dump_dict(d: dict) -> None:
    
    for class_name in d:
        # g.printObj(d [class_name], tag=class_name)
        methods = d [class_name]
        n = len(methods)
        print(f"{class_name:>20}: {n} method{g.plural(n)}")
#@+node:ekr.20240529060232.3: ** function: read
def read(file_name: str) -> str:
    try:
        with open(file_name, 'r') as f:
            contents = f.read()
            return contents
    except IOError:
        return ''
    except Exception:
        g.es_exception()
        return ''
#@+node:ekr.20240529060232.4: ** function: parse_ast
def parse_ast(s: str) -> Node:
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
#@+node:ekr.20240529060232.5: ** function: walk
def walk(root: Node) -> dict:
    # Find all classes and their methods.
    classes: dict[str, list[str]] = {}
    for node in ast.walk(root):
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
            classes [class_name] = list(sorted(methods))
    return classes
#@-others

path = os.path.abspath(os.path.join(leo_dir, 'core', 'leoCommands.py'))
print(path)
assert os.path.exists(path)
s = read(path)
if s:
    tree = parse_ast(s)
    # print(path, 'len(s)', len(s), 'tree', tree.__class__.__name__)
    # print(AstDumper().dump_ast(tree))
    d = walk(tree)
    dump_dict(d)

print('check_leo.py: done!')
#@-leo

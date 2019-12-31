#@+leo-ver=5-thin
#@+node:ekr.20141012064706.18389: * @file leoAst.py
"""AST (Abstract Syntax Tree) related classes."""
import ast
import glob
import os
import re
import sys
import time
import traceback
import types
import unittest
#@+others
#@+node:ekr.20160521104628.1: **  leoAst.py: top-level
#@+node:ekr.20191027072910.1: *3*  exception classes
class AstNotEqual(Exception):
    """The two given AST's are not equivalent."""

class AssignLinksError(Exception):
    """Assigning links to ast nodes failed."""
    
class FailFast(Exception):
    """Abort tests in TestRunner class."""
#@+node:ekr.20191226175251.1: *3* class LeoGlobals
#@@nosearch

class LeoGlobals:
    """
    Simplified version of functions in leoGlobals.py.
    """

    #@+others
    #@+node:ekr.20191227114503.1: *4* LeoGlobals.adjustTripleString
    def adjustTripleString(self, s):
        """Remove leading indentation from a triple-quoted string."""
        lines = g.splitLines(s)
        for line in lines:
            if line.strip():
                n = len(line)-len(line.lstrip())
                lws = line[:n]
                break
        if not lws:
            return s
        return ''.join(
            (z[n:] if z.startswith(lws) else z) for z in lines)
    #@+node:ekr.20191226175903.1: *4* LeoGlobals.callerName
    def callerName(self, n):
        """Get the function name from the call stack."""
        try:
            f1 = sys._getframe(n)
            code1 = f1.f_code
            return code1.co_name
        except Exception:
            return ''
    #@+node:ekr.20191226175426.1: *4* LeoGlobals.callers
    def callers(self, n=4):
        """
        Return a string containing a comma-separated list of the callers
        of the function that called g.callerList.
        """
        i, result = 2, []
        while True:
            s = self.callerName(n=i)
            if s:
                result.append(s)
            if not s or len(result) >= n:
                break
            i += 1
        return ','.join(reversed(result))
    #@+node:ekr.20191226190709.1: *4* leoGlobals.es_exception & helper
    def es_exception(self):
        typ, val, tb = sys.exc_info()
        for line in traceback.format_exception(typ, val, tb):
            print(line)
        fileName, n = self.getLastTracebackFileAndLineNumber()
        return fileName, n
    #@+node:ekr.20191226192030.1: *5* LeoGlobals.getLastTracebackFileAndLineNumber
    def getLastTracebackFileAndLineNumber(self):
        typ, val, tb = sys.exc_info()
        if typ == SyntaxError:
            # IndentationError is a subclass of SyntaxError.
            return val.filename, val.lineno
        #
        # Data is a list of tuples, one per stack entry.
        # The tuples have the form (filename, lineNumber, functionName, text).
        data = traceback.extract_tb(tb)
        item = data[-1]  # Get the item at the top of the stack.
        filename, n, functionName, text = item
        return filename, n
    #@+node:ekr.20191226190425.1: *4* LeoGlobals.plural
    def plural(self, obj):
        """Return "s" or "" depending on n."""
        if isinstance(obj, (list, tuple, str)):
            n = len(obj)
        else:
            n = obj
        return '' if n == 1 else 's'
    #@+node:ekr.20191226175441.1: *4* LeoGlobals.printObj
    def printObj(self, obj, indent='', tag=None):
        """Simplified version of g.printObj."""
        if tag:
            print(f"{tag}...")
        if isinstance(obj, str):
            obj = g.splitLines(obj)
        if isinstance(obj, list):
            print('[')
            for z in obj:
                print(f"  {z!r}")
            print(']')
        elif isinstance(obj, tuple):
            print('(')
            for z in obj:
                print(f"  {z!r}")
            print(')')
        else:
            print(repr(obj))
        print('')
    #@+node:ekr.20191226190131.1: *4* LeoGlobals.splitLines
    def splitLines(self, s):
        """Split s into lines, preserving the number of lines and
        the endings of all lines, including the last line."""
        # g.stat()
        if s:
            return s.splitlines(True)
                # This is a Python string function!
        return []
    #@+node:ekr.20191226190844.1: *4* LeoGlobals.toEncodedString
    def toEncodedString(self, s, encoding='utf-8'):
        """Convert unicode string to an encoded string."""
        if not isinstance(s, str):
            return s
        try:
            s = s.encode(encoding, "strict")
        except UnicodeError:
            s = s.encode(encoding, "replace")
            print(f"toEncodedString: Error converting {s!r} to {encoding}")
        return s
    #@+node:ekr.20191226190006.1: *4* LeoGlobals.toUnicode
    def toUnicode(self, s, encoding='utf-8'):
        """Convert bytes to unicode if necessary."""
        if isinstance(s, str):
            return s
        tag = 'g.toUnicode'
        try:
            s = s.decode(encoding, 'strict')
        except(UnicodeDecodeError, UnicodeError):
            s = s.decode(encoding, 'replace')
            print(f"{tag}: unicode error. encoding: {encoding!r}, s:\n{s!r}")
            g.trace(g.callers())
        except Exception:
            g.es_exception()
            print(f"{tag}: unexpected error! encoding: {encoding!r}, s:\n{s!r}")
            g.trace(g.callers())
        return s
    #@+node:ekr.20191226175436.1: *4* LeoGlobals.trace
    def trace(self, *args):
        """Print a tracing message."""
        # Compute the caller name.
        try:
            f1 = sys._getframe(1)
            code1 = f1.f_code
            name = code1.co_name
        except Exception:
            name = ''
        print(f"{name}: {' '.join(str(z) for z in args)}")
    #@+node:ekr.20191226190241.1: *4* LeoGlobals.truncate
    def truncate(self, s, n):
        """Return s truncated to n characters."""
        if len(s) <= n:
            return s
        s2 = s[: n - 3] + f'...({len(s)})'
        return s2 + '\n' if s.endswith('\n') else s2
    #@-others
#@+node:ekr.20191121081439.1: *3* function: compare_lists
def compare_lists(list1, list2):
    """
    Compare two lists of strings, showing the first mismatch.

    Return the index of the first mismatched lines, or None if identical.
    """
    import itertools
    it = itertools.zip_longest(list1, list2, fillvalue='Missing!')
    for i, (s1, s2) in enumerate(it):
        if s1 != s2:
            return i
    return None
#@+node:ekr.20191226071135.1: *3* function: get_time
def get_time():
    return time.process_time()
#@+node:ekr.20191229020834.1: *3* function: unit_test
def unit_test(raise_on_fail=True):
    """
    Called from unitTest.leo.

    Run basic unit tests for this file.
    """
    import _ast
    # Compute all fields to test.
    aList = sorted(dir(_ast))
    remove = [
        'Interactive', 'Suite',  # Not necessary.
        'PyCF_ONLY_AST',  # A constant,
        'AST',  # The base class,
    ]
    aList = [z for z in aList if not z[0].islower()]
        # Remove base classe
    aList = [z for z in aList if not z.startswith('_') and not z in remove]
    # Now test them.
    table = (
        # AstFullTraverser,
        AstFormatter,
        AstPatternFormatter,
        HTMLReportTraverser,
    )
    for class_ in table:
        traverser = class_()
        errors, nodes, ops = 0, 0, 0
        for z in aList:
            if hasattr(traverser, 'do_'+z):
                nodes += 1
            elif _op_names.get(z):
                ops += 1
            else:
                errors += 1
                print(f"Missing {traverser.__class__.__name__} visitor for: {z}")
    s = f"{nodes} node types, {ops} op types, {errors} errors"
    if raise_on_fail:
        assert not errors, s
    else:
        print(s)
#@+node:ekr.20191231110051.1: *3* node/token dumpers...
#@+node:ekr.20191027074436.1: *4* function: dump_ast
def dump_ast(ast, tag='dump_ast'):
    """Utility to dump an ast tree."""
    g.printObj(AstDumper().dump_ast(ast), tag=tag)
#@+node:ekr.20191228095945.4: *4* function: dump_contents
def dump_contents(contents):
    print('Contents...\n')
    for i, z in enumerate(g.splitLines(contents)):
        print(f"{i+1:<3} ", z.rstrip())
    print('')
#@+node:ekr.20191228095945.5: *4* function: dump_lines
def dump_lines(tokens):
    print('Token lines...\n')
    for z in tokens:
        if z.line.strip():
            print(z.line.rstrip())
        else:
            print(repr(z.line))
    print('')
#@+node:ekr.20191228095945.7: *4* function: dump_results
def dump_results(tokens):
    print('Results...\n')
    print(''.join(z.to_string() for z in tokens))
    print('')
#@+node:ekr.20191228095945.8: *4* function: dump_tokens
def dump_tokens(tokens):
    print('Tokens...\n')
    print("Note: values shown are repr(value) *except* for 'string' tokens.\n")
    for z in tokens:
        print(z.dump())
    print('')
#@+node:ekr.20191228095945.9: *4* function: dump_tree
def dump_tree(tree):
    
    print('')
    print('Tree...\n')
    print(AstDumper().dump_tree_and_links(tree))
    
dump_tree_and_links = dump_tree
#@+node:ekr.20191223095408.1: *3* node/token finders...
# Functions that associate tokens with nodes.
#@+node:ekr.20191223093539.1: *4* function: find_node_with_token_list
def find_node_with_token_list(node):
    """
    Return any node in node's tree with a token_list.
    """
    # This table only has to cover fields for ast.Nodes that
    # won't have any associated token.
    fields = (
        # Common...
        'elt', 'elts', 'body', 'value',
        # Less common...
        'dims', 'ifs', 'names', 's',
        'test', 'values', 'targets',
    )
    node1 = node
    while node:
        # First, try the node itself.
        if getattr(node, 'token_list', None):
            return node
        # Second, try the most common nodes w/o token_lists:
        if isinstance(node, ast.Call):
            node = node.func
        elif isinstance(node, ast.Tuple):
            node = node.elts
        # Finally, try all other nodes.
        else:
            # This will be used rarely.
            for field in fields:
                if getattr(node, field, None):
                    node = getattr(node, field)
                    break
            else:
                break
    g.trace('===== no token list', node1.__class__.__name__)
    return None
#@+node:ekr.20191223053247.1: *4* function: find_token
def find_token(node):
    """Return any token descending from node."""
    node2 = find_node_with_token_list(node)
    if node2:
        token = node2.token_list[0]
        return token
    g.trace('===== no token list', node.__class__.__name__)
    return None
        
#@+node:ekr.20191223054300.1: *4* function: is_ancestor
def is_ancestor(node, token):
    """Return True if node is an ancestor of token."""
    t_node = token.node
    assert t_node, token
    while t_node:
        if t_node == node:
            return True
        t_node = t_node.parent
    return False
#@+node:ekr.20191224093336.1: *4* function: match_parens (hack, disabled)
match_parens_message_given = False

def match_parens(tokens):
    """
    Extend the tokens in the token list to include unmatched trailing
    closing parens.
    """
    if True: ###
        global match_parens_message_given
        if not match_parens_message_given:
            match_parens_message_given = True
            g.trace('Disabled')
        return tokens
    if not tokens:
        return tokens
    # Calculate paren level...
    level = 0
    for token in tokens:
        if token.kind == 'op' and token.value == '(':
            level += 1
        if token.kind == 'op' and token.value == ')':
            level -= 1
    # Find matching ')' tokens...
    if level > 0:
        i = i1 = tokens[-1].index
        while level > 0 and i + 1 < len(tokens):
            token = tokens[i+1]
            if token.kind == 'op' and token.value == ')':
                level -= 1
            elif is_significant_token(token):
                break
            i += 1
        tokens.extend(tokens[i1 + 1 : i + 1])
    if level != 0:
        print('')
        g.trace('FAIL:', 'level', level, ''.join(z.to_string() for z in tokens))
        print('')
    return tokens
#@+node:ekr.20191231082137.1: *4* function: nearest_common_ancestor (test)
def nearest_common_ancestor(node1, node2):
    """
    Return the nearest common ancestor nodes for the given nodes.
    
    The nodes must have parent links.
    """
    if node1 == node2:
        return node1
        
    def parents(node):
        aList = []
        while node:
            aList.append(node)
            node = node.parent
        return list(reversed(aList))
        
    result = None
    parents1 = parents(node1)
    parents2 = parents(node2)
    while parents1 and parents2:
        parent1 = parents1.pop()
        parent2 = parents2.pop()
        if parent1 == parent2:
            result = parent1
        else:
            break
    return result
#@+node:ekr.20191223053324.1: *4* function: tokens_for_node
def tokens_for_node(node, tokens):
    """Return the list of all tokens descending from node."""
    # Find any token descending from node.
    token = find_token(node)
    if not token:
        g.trace('===== no tokens', node.__class__.__name__)
        return []
    assert is_ancestor(node, token)
    # Scan backward.
    i = last_i = token.index
    while i >= 0:
        token2 = tokens[i-1]
        if getattr(token2, 'node', None):
            if is_ancestor(node, token2):
                last_i = i - 1
            else:
                break
        i -= 1
    # Scan forward.
    j = last_j = token.index
    while j + 1 < len(tokens):
        token2 = tokens[j+1]
        if getattr(token2, 'node', None):
            if is_ancestor(node, token2):
                last_j = j + 1
            else:
                break
        j += 1
    # Extend tokens to balance parens.
    results = tokens[last_i : last_j + 1]
    return match_parens(results)  ### hack.
#@+node:ekr.20191225061516.1: *3* node/token replacers...
# Functions that replace tokens or nodes.
#@+node:ekr.20191225055616.1: *4* function: replace_node
def replace_node(new_node, old_node):
    
    parent = old_node.parent
    new_node.parent = parent
    new_node.node_index = old_node.node_index
    children = parent.children
    i = children.index(old_node)
    children[i] = new_node
    fields = getattr(old_node, '_fields', None)
    if fields:
        for field in fields:
            field = getattr(old_node, field)
            if field == old_node:
                setattr(old_node, field, new_node)
                break
#@+node:ekr.20191225055626.1: *4* function: replace_token
### def replace_token(i, kind, value):
def replace_token(token, kind, value): ###
    """Replace kind and value of the given token."""
    ### token = self.tokens[i]
    if token.kind in ('endmarker', 'killed'):
        return
    token.kind = kind
    token.value = value
    token.node = None  # Should be filled later.
#@+node:ekr.20191231072039.1: *3* node/token utils...
# General utility functions on tokens and nodes.
#@+node:ekr.20191027072126.1: *4* function: compare_asts & helpers
def compare_asts(ast1, ast2):
    """Compare two ast trees. Return True if they are equal."""
    import leo.core.leoGlobals as g
    # Compare the two parse trees.
    try:
        _compare_asts(ast1, ast2)
    except AstNotEqual:
        dump_ast(ast1, tag='AST BEFORE')
        dump_ast(ast2, tag='AST AFTER')
        if g.unitTesting:
            raise
        return False
    except Exception:
        g.trace(f"Unexpected exception")
        g.es_exception()
        return False
    return True
#@+node:ekr.20191027071653.2: *5* function._compare_asts
def _compare_asts(node1, node2):
    """
    Compare both nodes, and recursively compare their children.
    
    See also: http://stackoverflow.com/questions/3312989/
    """
    # Compare the nodes themselves.
    _compare_nodes(node1, node2)
    # Get the list of fields.
    fields1 = getattr(node1, "_fields", [])
    fields2 = getattr(node2, "_fields", [])
    if fields1 != fields2:
        raise AstNotEqual(f"node1._fields: {fields1}\n" f"node2._fields: {fields2}")
    # Recursively compare each field.
    for field in fields1:
        if field not in ('lineno', 'col_offset', 'ctx'):
            attr1 = getattr(node1, field, None)
            attr2 = getattr(node2, field, None)
            if attr1.__class__.__name__ != attr2.__class__.__name__:
                raise AstNotEqual(f"attrs1: {attr1},\n" f"attrs2: {attr2}")
            _compare_asts(attr1, attr2)
#@+node:ekr.20191027071653.3: *5* function._compare_nodes
def _compare_nodes(node1, node2):
    """
    Compare node1 and node2.
    For lists and tuples, compare elements recursively.
    Raise AstNotEqual if not equal.
    """
    # Class names must always match.
    if node1.__class__.__name__ != node2.__class__.__name__:
        raise AstNotEqual(
            f"node1.__class__.__name__: {node1.__class__.__name__}\n"
            f"node2.__class__.__name__: {node2.__class__.__name_}"
        )
    # Special cases for strings and None
    if node1 is None:
        return
    if isinstance(node1, str):
        if node1 != node2:
            raise AstNotEqual(f"node1: {node1!r}\n" f"node2: {node2!r}")
    # Special cases for lists and tuples:
    if isinstance(node1, (tuple, list)):
        if len(node1) != len(node2):
            raise AstNotEqual(f"node1: {node1}\n" f"node2: {node2}")
        for i, item1 in enumerate(node1):
            item2 = node2[i]
            if item1.__class__.__name__ != item2.__class__.__name__:
                raise AstNotEqual(
                    f"list item1: {i} {item1}\n" f"list item2: {i} {item2}"
                )
            _compare_asts(item1, item2)
#@+node:ekr.20191124123830.1: *4* function: is_significant & is_significant_token
def is_significant(kind, value):
    """
    Return True if (kind, value) represent a token that can be used for
    syncing generated tokens with the token list.
    """
    # Making 'endmarker' significant ensures that all tokens are synced.
    return (
        kind in ('endmarker', 'name', 'number', 'string') or
        kind == 'op' and value not in ',;()')

def is_significant_token(token):
    """Return True if the given token is a syncronizing token"""
    return is_significant(token.kind, token.value)
#@+node:ekr.20191119085222.1: *4* function: obj_id
def obj_id(obj):
    """Return the last four digits of id(obj), for dumps & traces."""
    return str(id(obj))[-4:]
#@+node:ekr.20191231060700.1: *4* function: op_name
#@@nobeautify

# https://docs.python.org/3/library/ast.html

_op_names = {
    # Binary operators.
    'Add':       '+',
    'BitAnd':    '&',
    'BitOr':     '|',
    'BitXor':    '^',
    'Div':       '/',
    'FloorDiv':  '//',
    'LShift':    '<<',
    'MatMult':   '@', # Python 3.5.
    'Mod':       '%',
    'Mult':      '*',
    'Pow':       '**',
    'RShift':    '>>',
    'Sub':       '-',
    # Boolean operators.
    'And':   ' and ',
    'Or':    ' or ',
    # Comparison operators
    'Eq':    '==',
    'Gt':    '>',
    'GtE':   '>=',
    'In':    ' in ',
    'Is':    ' is ',
    'IsNot': ' is not ',
    'Lt':    '<',
    'LtE':   '<=',
    'NotEq': '!=',
    'NotIn': ' not in ',
    # Context operators.
    'AugLoad':  '<AugLoad>',
    'AugStore': '<AugStore>',
    'Del':      '<Del>',
    'Load':     '<Load>',
    'Param':    '<Param>',
    'Store':    '<Store>',
    # Unary operators.
    'Invert':   '~',
    'Not':      ' not ',
    'UAdd':     '+',
    'USub':     '-',
}

def op_name(node):
    """Return the print name of an operator node."""
    class_name = node.__class__.__name__
    assert class_name in _op_names, repr(class_name)
    return _op_names [class_name].strip()
#@+node:ekr.20191027075648.1: *4* function: parse_ast
def parse_ast(s, headline=None, show_time=False):
    """
    Parse string s, catching & reporting all exceptions.
    Return the ast node, or None.
    """

    def oops(message):
        print('')
        if headline:
            print(f"parse_ast: {message} in: {headline}")
        else:
            print(f"parse_ast: {message}")
        g.printObj(s)
        print('')

    try:
        s1 = g.toEncodedString(s)
        t1 = get_time()
        tree = ast.parse(s1, filename='before', mode='exec')
        t2 = get_time()
        if show_time:
            print(f"   parse_ast: {t2-t1:5.2f} sec.")
        return tree
    except IndentationError:
        oops('Indentation Error')
    except SyntaxError:
        oops('Syntax Error')
    except Exception:
        oops('Unexpected Exception')
        g.es_exception()
    return None
#@+node:ekr.20191227170512.1: ** Legacy classes
#@+node:ekr.20141012064706.18399: *3*  class AstFormatter
class AstFormatter:
    """
    A class to recreate source code from an AST.

    This does not have to be perfect, but it should be close.

    Also supports optional annotations such as line numbers, file names, etc.
    """
    # No ctor.
    # pylint: disable=consider-using-enumerate

    in_expr = False
    level = 0

    #@+others
    #@+node:ekr.20141012064706.18402: *4* f.format
    def format(self, node, level, *args, **keys):
        """Format the node and possibly its descendants, depending on args."""
        self.level = level
        val = self.visit(node, *args, **keys)
        return val.rstrip() if val else ''
    #@+node:ekr.20141012064706.18403: *4* f.visit
    def visit(self, node, *args, **keys):
        """Return the formatted version of an Ast node, or list of Ast nodes."""

        if isinstance(node, (list, tuple)):
            return ','.join([self.visit(z) for z in node])
        if node is None:
            return 'None'
        assert isinstance(node, ast.AST), node.__class__.__name__
        method_name = 'do_' + node.__class__.__name__
        method = getattr(self, method_name)
        s = method(node, *args, **keys)
        assert isinstance(s, str), type(s)
        return s
    #@+node:ekr.20141012064706.18469: *4* f.indent
    def indent(self, s):
        return f'%s%s' % (' ' * 4 * self.level, s)
    #@+node:ekr.20141012064706.18404: *4* f: Contexts
    #@+node:ekr.20141012064706.18405: *5* f.ClassDef
    # 2: ClassDef(identifier name, expr* bases,
    #             stmt* body, expr* decorator_list)
    # 3: ClassDef(identifier name, expr* bases,
    #             keyword* keywords, expr? starargs, expr? kwargs
    #             stmt* body, expr* decorator_list)
    #
    # keyword arguments supplied to call (NULL identifier for **kwargs)
    # keyword = (identifier? arg, expr value)

    def do_ClassDef(self, node, print_body=True):

        result = []
        name = node.name  # Only a plain string is valid.
        bases = [self.visit(z) for z in node.bases] if node.bases else []
        if getattr(node, 'keywords', None):  # Python 3
            for keyword in node.keywords:
                bases.append(f'%s=%s' % (keyword.arg, self.visit(keyword.value)))
        if getattr(node, 'starargs', None):  # Python 3
            bases.append(f'*%s' % self.visit(node.starargs))
        if getattr(node, 'kwargs', None):  # Python 3
            bases.append(f'*%s' % self.visit(node.kwargs))
        if bases:
            result.append(self.indent(f'class %s(%s):\n' % (name, ','.join(bases))))
        else:
            result.append(self.indent(f'class %s:\n' % name))
        if print_body:
            for z in node.body:
                self.level += 1
                result.append(self.visit(z))
                self.level -= 1
        return ''.join(result)
    #@+node:ekr.20141012064706.18406: *5* f.FunctionDef & AsyncFunctionDef
    # 2: FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list)
    # 3: FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list,
    #                expr? returns)

    def do_FunctionDef(self, node, async_flag=False, print_body=True):
        """Format a FunctionDef node."""
        result = []
        if node.decorator_list:
            for z in node.decorator_list:
                result.append(f'@%s\n' % self.visit(z))
        name = node.name  # Only a plain string is valid.
        args = self.visit(node.args) if node.args else ''
        asynch_prefix = 'asynch ' if async_flag else ''
        if getattr(node, 'returns', None):  # Python 3.
            returns = self.visit(node.returns)
            result.append(self.indent(f'%sdef %s(%s): -> %s\n' % (
                asynch_prefix, name, args, returns)))
        else:
            result.append(self.indent(f'%sdef %s(%s):\n' % (
                asynch_prefix, name, args)))
        if print_body:
            for z in node.body:
                self.level += 1
                result.append(self.visit(z))
                self.level -= 1
        return ''.join(result)

    def do_AsyncFunctionDef(self, node):
        return self.do_FunctionDef(node, async_flag=True)
    #@+node:ekr.20141012064706.18407: *5* f.Interactive
    def do_Interactive(self, node):
        for z in node.body:
            self.visit(z)
    #@+node:ekr.20141012064706.18408: *5* f.Module
    def do_Module(self, node):
        assert 'body' in node._fields
        result = ''.join([self.visit(z) for z in node.body])
        return result
    #@+node:ekr.20141012064706.18409: *5* f.Lambda
    def do_Lambda(self, node):
        return self.indent(f'lambda %s: %s' % (
            self.visit(node.args),
            self.visit(node.body)))
    #@+node:ekr.20141012064706.18410: *4* f: Expressions
    #@+node:ekr.20141012064706.18411: *5* f.Expr
    def do_Expr(self, node):
        """An outer expression: must be indented."""
        assert not self.in_expr
        self.in_expr = True
        value = self.visit(node.value)
        self.in_expr = False
        return self.indent(f'%s\n' % value)
    #@+node:ekr.20141012064706.18412: *5* f.Expression
    def do_Expression(self, node):
        """An inner expression: do not indent."""
        return f'%s\n' % self.visit(node.body)
    #@+node:ekr.20141012064706.18413: *5* f.GeneratorExp
    def do_GeneratorExp(self, node):
        elt = self.visit(node.elt) or ''
        gens = [self.visit(z) for z in node.generators]
        gens = [z if z else '<**None**>' for z in gens]  # Kludge: probable bug.
        return f'<gen %s for %s>' % (elt, ','.join(gens))
    #@+node:ekr.20141012064706.18414: *5* f.ctx nodes
    def do_AugLoad(self, node):
        return 'AugLoad'

    def do_Del(self, node):
        return 'Del'

    def do_Load(self, node):
        return 'Load'

    def do_Param(self, node):
        return 'Param'

    def do_Store(self, node):
        return 'Store'
    #@+node:ekr.20141012064706.18415: *4* f: Operands
    #@+node:ekr.20141012064706.18416: *5* f.arguments
    # 2: arguments = (expr* args, identifier? vararg, identifier?
    #                arg? kwarg, expr* defaults)
    # 3: arguments = (arg*  args, arg? vararg,
    #                arg* kwonlyargs, expr* kw_defaults,
    #                arg? kwarg, expr* defaults)

    def do_arguments(self, node):
        """Format the arguments node."""
        kind = node.__class__.__name__
        assert kind == 'arguments', kind
        args = [self.visit(z) for z in node.args]
        defaults = [self.visit(z) for z in node.defaults]
        args2 = []
        n_plain = len(args) - len(defaults)
        for i in range(len(node.args)):
            if i < n_plain:
                args2.append(args[i])
            else:
                args2.append(f'%s=%s' % (args[i], defaults[i-n_plain]))
        # Add the vararg and kwarg expressions.
        vararg = getattr(node, 'vararg', None)
        if vararg: args2.append('*'+self.visit(vararg))
        kwarg = getattr(node, 'kwarg', None)
        if kwarg: args2.append(f'**'+self.visit(kwarg))
        return ','.join(args2)
    #@+node:ekr.20141012064706.18417: *5* f.arg (Python3 only)
    # 3: arg = (identifier arg, expr? annotation)

    def do_arg(self, node):
        if getattr(node, 'annotation', None):
            return self.visit(node.annotation)
        return node.arg
    #@+node:ekr.20141012064706.18418: *5* f.Attribute
    # Attribute(expr value, identifier attr, expr_context ctx)

    def do_Attribute(self, node):
        return f'%s.%s' % (
            self.visit(node.value),
            node.attr)  # Don't visit node.attr: it is always a string.
    #@+node:ekr.20141012064706.18419: *5* f.Bytes
    def do_Bytes(self, node):  # Python 3.x only.
        return str(node.s)
    #@+node:ekr.20141012064706.18420: *5* f.Call & f.keyword
    # Call(expr func, expr* args, keyword* keywords, expr? starargs, expr? kwargs)

    def do_Call(self, node):

        func = self.visit(node.func)
        args = [self.visit(z) for z in node.args]
        for z in node.keywords:
            # Calls f.do_keyword.
            args.append(self.visit(z))
        if getattr(node, 'starargs', None):
            args.append(f'*%s' % (self.visit(node.starargs)))
        if getattr(node, 'kwargs', None):
            args.append(f'**%s' % (self.visit(node.kwargs)))
        args = [z for z in args if z]  # Kludge: Defensive coding.
        s = f'%s(%s)' % (func, ','.join(args))
        return s if self.in_expr else self.indent(s+'\n')
            # 2017/12/15.
    #@+node:ekr.20141012064706.18421: *6* f.keyword
    # keyword = (identifier arg, expr value)

    def do_keyword(self, node):
        # node.arg is a string.
        value = self.visit(node.value)
        # This is a keyword *arg*, not a Python keyword!
        return f'%s=%s' % (node.arg, value)
    #@+node:ekr.20141012064706.18422: *5* f.comprehension
    def do_comprehension(self, node):
        result = []
        name = self.visit(node.target)  # A name.
        it = self.visit(node.iter)  # An attribute.
        result.append(f'%s in %s' % (name, it))
        ifs = [self.visit(z) for z in node.ifs]
        if ifs:
            result.append(f' if %s' % (''.join(ifs)))
        return ''.join(result)
    #@+node:ekr.20170721073056.1: *5* f.Constant (Python 3.6+)
    def do_Constant(self, node):  # Python 3.6+ only.
        return str(node.s)  # A guess.
    #@+node:ekr.20141012064706.18423: *5* f.Dict
    def do_Dict(self, node):
        result = []
        keys = [self.visit(z) for z in node.keys]
        values = [self.visit(z) for z in node.values]
        if len(keys) == len(values):
            result.append('{\n' if keys else '{')
            items = []
            for i in range(len(keys)):
                items.append(f'  %s:%s' % (keys[i], values[i]))
            result.append(',\n'.join(items))
            result.append('\n}' if keys else '}')
        else:
            print(
                f"Error: f.Dict: len(keys) != len(values)\n"
                f"keys: {repr(keys)}\nvals: {repr(values)}")
        return ''.join(result)
    #@+node:ekr.20160523101618.1: *5* f.DictComp
    # DictComp(expr key, expr value, comprehension* generators)

    def do_DictComp(self, node):
        key = self.visit(node.key)
        value = self.visit(node.value)
        gens = [self.visit(z) for z in node.generators]
        gens = [z if z else '<**None**>' for z in gens]  # Kludge: probable bug.
        return f'%s:%s for %s' % (key, value, ''.join(gens))
    #@+node:ekr.20141012064706.18424: *5* f.Ellipsis
    def do_Ellipsis(self, node):
        return '...'
    #@+node:ekr.20141012064706.18425: *5* f.ExtSlice
    def do_ExtSlice(self, node):
        return ':'.join([self.visit(z) for z in node.dims])
    #@+node:ekr.20170721075130.1: *5* f.FormattedValue (Python 3.6+)
    # FormattedValue(expr value, int? conversion, expr? format_spec)

    def do_FormattedValue(self, node):  # Python 3.6+ only.
        return f'%s%s%s' % (
            self.visit(node.value),
            self.visit(node.conversion) if node.conversion else '',
            self.visit(node.format_spec) if node.format_spec else '')
    #@+node:ekr.20141012064706.18426: *5* f.Index
    def do_Index(self, node):
        return self.visit(node.value)
    #@+node:ekr.20170721080559.1: *5* f.JoinedStr (Python 3.6)
    # JoinedStr(expr* values)

    def do_JoinedStr(self, node):

        if node.values:
            for value in node.values:
                self.visit(value)
    #@+node:ekr.20141012064706.18427: *5* f.List
    def do_List(self, node):
        # Not used: list context.
        # self.visit(node.ctx)
        elts = [self.visit(z) for z in node.elts]
        elts = [z for z in elts if z]  # Defensive.
        return f'[%s]' % ','.join(elts)
    #@+node:ekr.20141012064706.18428: *5* f.ListComp
    def do_ListComp(self, node):
        elt = self.visit(node.elt)
        gens = [self.visit(z) for z in node.generators]
        gens = [z if z else '<**None**>' for z in gens]  # Kludge: probable bug.
        return f'%s for %s' % (elt, ''.join(gens))
    #@+node:ekr.20141012064706.18429: *5* f.Name & NameConstant
    def do_Name(self, node):
        return node.id

    def do_NameConstant(self, node):  # Python 3 only.
        s = repr(node.value)
        return s
    #@+node:ekr.20141012064706.18430: *5* f.Num
    def do_Num(self, node):
        return repr(node.n)
    #@+node:ekr.20141012064706.18431: *5* f.Repr
    # Python 2.x only

    def do_Repr(self, node):
        return f'repr(%s)' % self.visit(node.value)
    #@+node:ekr.20160523101929.1: *5* f.Set
    # Set(expr* elts)

    def do_Set(self, node):
        for z in node.elts:
            self.visit(z)
    #@+node:ekr.20160523102226.1: *5* f.SetComp
    # SetComp(expr elt, comprehension* generators)

    def do_SetComp(self, node):

        elt = self.visit(node.elt)
        gens = [self.visit(z) for z in node.generators]
        return f'%s for %s' % (elt, ''.join(gens))
    #@+node:ekr.20141012064706.18432: *5* f.Slice
    def do_Slice(self, node):
        lower, upper, step = '', '', ''
        if getattr(node, 'lower', None) is not None:
            lower = self.visit(node.lower)
        if getattr(node, 'upper', None) is not None:
            upper = self.visit(node.upper)
        if getattr(node, 'step', None) is not None:
            step = self.visit(node.step)
        if step:
            return f'%s:%s:%s' % (lower, upper, step)
        return f'%s:%s' % (lower, upper)
    #@+node:ekr.20141012064706.18433: *5* f.Str
    def do_Str(self, node):
        """This represents a string constant."""
        return repr(node.s)
    #@+node:ekr.20141012064706.18434: *5* f.Subscript
    # Subscript(expr value, slice slice, expr_context ctx)

    def do_Subscript(self, node):
        value = self.visit(node.value)
        the_slice = self.visit(node.slice)
        return f'%s[%s]' % (value, the_slice)
    #@+node:ekr.20141012064706.18435: *5* f.Tuple
    def do_Tuple(self, node):
        elts = [self.visit(z) for z in node.elts]
        return f'(%s)' % ','.join(elts)
    #@+node:ekr.20141012064706.18436: *4* f: Operators
    #@+node:ekr.20141012064706.18437: *5* f.BinOp
    def do_BinOp(self, node):
        return f'%s%s%s' % (
            self.visit(node.left),
            op_name(node.op),
            self.visit(node.right))
    #@+node:ekr.20141012064706.18438: *5* f.BoolOp
    def do_BoolOp(self, node):
        op_name_ = op_name(node.op)
        values = [self.visit(z).strip() for z in node.values]
        return op_name_.join(values)
    #@+node:ekr.20141012064706.18439: *5* f.Compare
    def do_Compare(self, node):
        result = []
        lt = self.visit(node.left)
        # ops   = [self.visit(z) for z in node.ops]
        ops = [op_name(z) for z in node.ops]
        comps = [self.visit(z) for z in node.comparators]
        result.append(lt)
        assert len(ops) == len(comps), repr(node)
        for i in range(len(ops)):
            result.append(f'%s%s' % (ops[i], comps[i]))
        return ''.join(result)
    #@+node:ekr.20141012064706.18440: *5* f.UnaryOp
    def do_UnaryOp(self, node):
        return f'%s%s' % (
            op_name(node.op),
            self.visit(node.operand))
    #@+node:ekr.20141012064706.18441: *5* f.ifExp (ternary operator)
    def do_IfExp(self, node):
        return f'%s if %s else %s ' % (
            self.visit(node.body),
            self.visit(node.test),
            self.visit(node.orelse))
    #@+node:ekr.20141012064706.18442: *4* f: Statements
    #@+node:ekr.20170721074105.1: *5* f.AnnAssign
    # AnnAssign(expr target, expr annotation, expr? value, int simple)

    def do_AnnAssign(self, node):
        return self.indent(f'%s:%s=%s\n' % (
            self.visit(node.target),
            self.visit(node.annotation),
            self.visit(node.value),
        ))
    #@+node:ekr.20141012064706.18443: *5* f.Assert
    def do_Assert(self, node):
        test = self.visit(node.test)
        if getattr(node, 'msg', None):
            message = self.visit(node.msg)
            return self.indent(f'assert %s, %s' % (test, message))
        return self.indent(f'assert %s' % test)
    #@+node:ekr.20141012064706.18444: *5* f.Assign
    def do_Assign(self, node):
        return self.indent(f'%s=%s\n' % (
            '='.join([self.visit(z) for z in node.targets]),
            self.visit(node.value)))
    #@+node:ekr.20141012064706.18445: *5* f.AugAssign
    def do_AugAssign(self, node):
        return self.indent(f'%s%s=%s\n' % (
            self.visit(node.target),
            op_name(node.op),  # Bug fix: 2013/03/08.
            self.visit(node.value)))
    #@+node:ekr.20160523100504.1: *5* f.Await (Python 3)
    # Await(expr value)

    def do_Await(self, node):

        return self.indent(f'await %s\n' % (
            self.visit(node.value)))
    #@+node:ekr.20141012064706.18446: *5* f.Break
    def do_Break(self, node):
        return self.indent(f'break\n')
    #@+node:ekr.20141012064706.18447: *5* f.Continue
    def do_Continue(self, node):
        return self.indent(f'continue\n')
    #@+node:ekr.20141012064706.18448: *5* f.Delete
    def do_Delete(self, node):
        targets = [self.visit(z) for z in node.targets]
        return self.indent(f'del %s\n' % ','.join(targets))
    #@+node:ekr.20141012064706.18449: *5* f.ExceptHandler
    def do_ExceptHandler(self, node):
        
        result = []
        result.append(self.indent('except'))
        if getattr(node, 'type', None):
            result.append(f' %s' % self.visit(node.type))
        if getattr(node, 'name', None):
            if isinstance(node.name, ast.AST):
                result.append(f' as %s' % self.visit(node.name))
            else:
                result.append(f' as %s' % node.name)  # Python 3.x.
        result.append(':\n')
        for z in node.body:
            self.level += 1
            result.append(self.visit(z))
            self.level -= 1
        return ''.join(result)
    #@+node:ekr.20141012064706.18450: *5* f.Exec
    # Python 2.x only

    def do_Exec(self, node):
        body = self.visit(node.body)
        args = []  # Globals before locals.
        if getattr(node, 'globals', None):
            args.append(self.visit(node.globals))
        if getattr(node, 'locals', None):
            args.append(self.visit(node.locals))
        if args:
            return self.indent(f'exec %s in %s\n' % (
                body, ','.join(args)))
        return self.indent(f'exec {body}\n')
    #@+node:ekr.20141012064706.18451: *5* f.For & AsnchFor (Python 3)
    def do_For(self, node, async_flag=False):
        result = []
        result.append(self.indent(f'%sfor %s in %s:\n' % (
            'async ' if async_flag else '',
            self.visit(node.target),
            self.visit(node.iter))))
        for z in node.body:
            self.level += 1
            result.append(self.visit(z))
            self.level -= 1
        if node.orelse:
            result.append(self.indent('else:\n'))
            for z in node.orelse:
                self.level += 1
                result.append(self.visit(z))
                self.level -= 1
        return ''.join(result)

    def do_AsyncFor(self, node):
        return self.do_For(node, async_flag=True)
    #@+node:ekr.20141012064706.18452: *5* f.Global
    def do_Global(self, node):
        return self.indent(f'global %s\n' % (
            ','.join(node.names)))
    #@+node:ekr.20141012064706.18453: *5* f.If
    def do_If(self, node):
        result = []
        result.append(self.indent(f'if %s:\n' % (
            self.visit(node.test))))
        for z in node.body:
            self.level += 1
            result.append(self.visit(z))
            self.level -= 1
        if node.orelse:
            result.append(self.indent(f'else:\n'))
            for z in node.orelse:
                self.level += 1
                result.append(self.visit(z))
                self.level -= 1
        return ''.join(result)
    #@+node:ekr.20141012064706.18454: *5* f.Import & helper
    def do_Import(self, node):
        names = []
        for fn, asname in self.get_import_names(node):
            if asname:
                names.append(f'%s as %s' % (fn, asname))
            else:
                names.append(fn)
        return self.indent(f'import %s\n' % (
            ','.join(names)))
    #@+node:ekr.20141012064706.18455: *6* f.get_import_names
    def get_import_names(self, node):
        """Return a list of the the full file names in the import statement."""
        result = []
        for ast2 in node.names:
            assert ast2.__class__.__name__ == 'alias', (repr(ast2))
            data = ast2.name, ast2.asname
            result.append(data)
        return result
    #@+node:ekr.20141012064706.18456: *5* f.ImportFrom
    def do_ImportFrom(self, node):
        names = []
        for fn, asname in self.get_import_names(node):
            if asname:
                names.append(f'%s as %s' % (fn, asname))
            else:
                names.append(fn)
        return self.indent(f'from %s import %s\n' % (
            node.module,
            ','.join(names)))
    #@+node:ekr.20160317050557.2: *5* f.Nonlocal (Python 3)
    # Nonlocal(identifier* names)

    def do_Nonlocal(self, node):

        return self.indent(f'nonlocal %s\n' % ', '.join(node.names))
    #@+node:ekr.20141012064706.18457: *5* f.Pass
    def do_Pass(self, node):
        return self.indent('pass\n')
    #@+node:ekr.20141012064706.18458: *5* f.Print
    # Python 2.x only

    def do_Print(self, node):
        vals = []
        for z in node.values:
            vals.append(self.visit(z))
        if getattr(node, 'dest', None):
            vals.append(f'dest=%s' % self.visit(node.dest))
        if getattr(node, 'nl', None):
            # vals.append('nl=%s' % self.visit(node.nl))
            vals.append(f'nl=%s' % node.nl)
        return self.indent(f'print(%s)\n' % (
            ','.join(vals)))
    #@+node:ekr.20141012064706.18459: *5* f.Raise
    # Raise(expr? type, expr? inst, expr? tback)    Python 2
    # Raise(expr? exc, expr? cause)                 Python 3

    def do_Raise(self, node):
        args = []
        for attr in ('exc', 'cause'):
            if getattr(node, attr, None) is not None:
                args.append(self.visit(getattr(node, attr)))
        if args:
            return self.indent(f'raise %s\n' % (
                ','.join(args)))
        return self.indent('raise\n')
    #@+node:ekr.20141012064706.18460: *5* f.Return
    def do_Return(self, node):
        if node.value:
            return self.indent(f'return %s\n' % (
                self.visit(node.value)))
        return self.indent('return\n')
    #@+node:ekr.20160317050557.3: *5* f.Starred (Python 3)
    # Starred(expr value, expr_context ctx)

    def do_Starred(self, node):

        return '*' + self.visit(node.value)
    #@+node:ekr.20141012064706.18461: *5* f.Suite
    # def do_Suite(self,node):
        # for z in node.body:
            # s = self.visit(z)
    #@+node:ekr.20160317050557.4: *5* f.Try (Python 3)
    # Try(stmt* body, excepthandler* handlers, stmt* orelse, stmt* finalbody)

    def do_Try(self, node):  # Python 3

        result = []
        result.append(self.indent('try:\n'))
        for z in node.body:
            self.level += 1
            result.append(self.visit(z))
            self.level -= 1
        if node.handlers:
            for z in node.handlers:
                result.append(self.visit(z))
        if node.orelse:
            result.append(self.indent('else:\n'))
            for z in node.orelse:
                self.level += 1
                result.append(self.visit(z))
                self.level -= 1
        if node.finalbody:
            result.append(self.indent('finally:\n'))
            for z in node.finalbody:
                self.level += 1
                result.append(self.visit(z))
                self.level -= 1
        return ''.join(result)
    #@+node:ekr.20141012064706.18462: *5* f.TryExcept
    def do_TryExcept(self, node):
        result = []
        result.append(self.indent('try:\n'))
        for z in node.body:
            self.level += 1
            result.append(self.visit(z))
            self.level -= 1
        if node.handlers:
            for z in node.handlers:
                result.append(self.visit(z))
        if node.orelse:
            result.append('else:\n')
            for z in node.orelse:
                self.level += 1
                result.append(self.visit(z))
                self.level -= 1
        return ''.join(result)
    #@+node:ekr.20141012064706.18463: *5* f.TryFinally
    def do_TryFinally(self, node):
        result = []
        result.append(self.indent('try:\n'))
        for z in node.body:
            self.level += 1
            result.append(self.visit(z))
            self.level -= 1
        result.append(self.indent('finally:\n'))
        for z in node.finalbody:
            self.level += 1
            result.append(self.visit(z))
            self.level -= 1
        return ''.join(result)
    #@+node:ekr.20141012064706.18464: *5* f.While
    def do_While(self, node):
        result = []
        result.append(self.indent(f'while %s:\n' % (
            self.visit(node.test))))
        for z in node.body:
            self.level += 1
            result.append(self.visit(z))
            self.level -= 1
        if node.orelse:
            result.append('else:\n')
            for z in node.orelse:
                self.level += 1
                result.append(self.visit(z))
                self.level -= 1
        return ''.join(result)
    #@+node:ekr.20141012064706.18465: *5* f.With & AsyncWith (Python 3)
    # 2:  With(expr context_expr, expr? optional_vars,
    #          stmt* body)
    # 3:  With(withitem* items,
    #          stmt* body)
    # withitem = (expr context_expr, expr? optional_vars)

    def do_With(self, node, async_flag=False):
        result = []
        result.append(self.indent(f'%swith ' % ('async ' if async_flag else '')))
        if getattr(node, 'context_expression', None):
            result.append(self.visit(node.context_expresssion))
        vars_list = []
        if getattr(node, 'optional_vars', None):
            try:
                for z in node.optional_vars:
                    vars_list.append(self.visit(z))
            except TypeError:  # Not iterable.
                vars_list.append(self.visit(node.optional_vars))
        if getattr(node, 'items', None):  # Python 3.
            for item in node.items:
                result.append(self.visit(item.context_expr))
                if getattr(item, 'optional_vars', None):
                    try:
                        for z in item.optional_vars:
                            vars_list.append(self.visit(z))
                    except TypeError:  # Not iterable.
                        vars_list.append(self.visit(item.optional_vars))
        result.append(','.join(vars_list))
        result.append(':\n')
        for z in node.body:
            self.level += 1
            result.append(self.visit(z))
            self.level -= 1
        result.append('\n')
        return ''.join(result)

    def do_AsyncWith(self, node):
        return self.do_With(node, async_flag=True)
    #@+node:ekr.20141012064706.18466: *5* f.Yield
    def do_Yield(self, node):
        if getattr(node, 'value', None):
            return self.indent(f'yield %s\n' % (
                self.visit(node.value)))
        return self.indent('yield\n')
    #@+node:ekr.20160317050557.5: *5* f.YieldFrom (Python 3)
    # YieldFrom(expr value)

    def do_YieldFrom(self, node):

        return self.indent(f'yield from %s\n' % (
            self.visit(node.value)))
    #@-others
#@+node:ekr.20141012064706.18530: *3* class AstPatternFormatter (AstFormatter)
class AstPatternFormatter(AstFormatter):
    """
    A subclass of AstFormatter that replaces values of constants by Bool,
    Bytes, Int, Name, Num or Str.
    """
    # No ctor.
    #@+others
    #@+node:ekr.20141012064706.18531: *4* Constants & Name
    # Return generic markers allow better pattern matches.

    def do_BoolOp(self, node):  # Python 2.x only.
        return 'Bool'

    def do_Bytes(self, node):  # Python 3.x only.
        return 'Bytes'  # return str(node.s)

    def do_Constant(self, node):  # Python 3.6+ only.
        return 'Constant'

    def do_Name(self, node):
        return 'Bool' if node.id in ('True', 'False') else node.id

    def do_NameConstant(self, node):  # Python 3 only.
        s = repr(node.value)
        return 'Bool' if s in ('True', 'False') else s

    def do_Num(self, node):
        return 'Num'  # return repr(node.n)

    def do_Str(self, node):
        """This represents a string constant."""
        return 'Str'  # return repr(node.s)
    #@-others
#@+node:ekr.20150722204300.1: *3* class HTMLReportTraverser
class HTMLReportTraverser:
    """
    Create html reports from an AST tree.

    Inspired by Paul Boddie.

    This version writes all html to a global code list.

    At present, this code does not show comments.
    The TokenSync class is probably the best way to do this.
    """
    # To do: revise report-traverser-debug.css.
    #@+others
    #@+node:ekr.20150722204300.2: *4* rt.__init__
    def __init__(self, debug=False):
        """Ctor for the NewHTMLReportTraverser class."""
        self.code_list = []
        self.debug = debug
        self.div_stack = []
            # A check to ensure matching div/end_div.
        self.last_doc = None
        # List of divs & spans to generate...
        self.enable_list = [
            'body', 'class', 'doc', 'function',
            'keyword', 'name', 'statement'
        ]
        # Formatting stuff...
        debug_css = 'report-traverser-debug.css'
        plain_css = 'report-traverser.css'
        self.css_fn = debug_css if debug else plain_css
        self.html_footer = '\n</body>\n</html>\n'
        self.html_header = self.define_html_header()
    #@+node:ekr.20150722204300.3: *5* define_html_header
    def define_html_header(self):
        # Use string catenation to avoid using g.adjustTripleString.
        return (
            '<?xml version="1.0" encoding="iso-8859-15"?>\n'
            '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"\n'
            '"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n'
            '<html xmlns="http://www.w3.org/1999/xhtml">\n'
            '<head>\n'
            '  <title>%(title)s</title>\n'
            '  <link rel="stylesheet" type="text/css" href="%(css-fn)s" />\n'
            '</head>\n<body>'
        )
    #@+node:ekr.20150723094359.1: *4* rt.code generators
    #@+node:ekr.20150723100236.1: *5* rt.blank
    def blank(self):
        """Insert a single blank."""
        self.clean(' ')
        if self.code_list[-1] not in ' \n':
            self.gen(' ')
    #@+node:ekr.20150723100208.1: *5* rt.clean
    def clean(self, s):
        """Remove s from the code list."""
        s2 = self.code_list[-1]
        if s2 == s:
            self.code_list.pop()
    #@+node:ekr.20150723105702.1: *5* rt.colon
    def colon(self):

        self.clean('\n')
        self.clean(' ')
        self.clean('\n')
        self.gen(':')
    #@+node:ekr.20150723100346.1: *5* rt.comma & clean_comma
    def comma(self):

        self.clean(' ')
        self.gen(', ')

    def clean_comma(self):

        self.clean(', ')
    #@+node:ekr.20150722204300.21: *5* rt.doc
    # Called by ClassDef & FunctionDef visitors.

    def doc(self, node):
        doc = ast.get_docstring(node)
        if doc:
            self.docstring(doc)
            self.last_doc = doc  # Attempt to suppress duplicate.
    #@+node:ekr.20150722204300.22: *5* rt.docstring
    def docstring(self, s):

        import textwrap
        self.gen("<pre class='doc'>")
        self.gen('"""')
        self.gen(self.text(textwrap.dedent(s.replace('"""', '\\"\\"\\"'))))
        self.gen('"""')
        self.gen("</pre>")
    #@+node:ekr.20150722211115.1: *5* rt.gen
    def gen(self, s):
        """Append s to the global code list."""
        if s:
            self.code_list.append(s)
    #@+node:ekr.20150722204300.23: *5* rt.keyword (code generator)
    def keyword(self, name):

        self.blank()
        self.span('keyword')
        self.gen(name)
        self.end_span('keyword')
        self.blank()
    #@+node:ekr.20150722204300.24: *5* rt.name
    def name(self, name):

        # Div would put each name on a separate line.
        # span messes up whitespace, for now.
        # self.span('name')
        self.gen(name)
        # self.end_span('name')
    #@+node:ekr.20150723100417.1: *5* rt.newline
    def newline(self):

        self.clean(' ')
        self.clean('\n')
        self.clean(' ')
        self.gen('\n')
    #@+node:ekr.20150722204300.26: *5* rt.op
    def op(self, op_name, leading=False, trailing=True):

        if leading:
            self.blank()
        # self.span('operation')
        # self.span('operator')
        self.gen(self.text(op_name))
        # self.end_span('operator')
        if trailing:
            self.blank()
        # self.end_span('operation')
    #@+node:ekr.20160315184954.1: *5* rt.string (code generator)
    def string(self, s):

        import xml.sax.saxutils as saxutils
        s = repr(s.strip().strip())
        s = saxutils.escape(s)
        self.gen(s)
    #@+node:ekr.20150722204300.27: *5* rt.simple_statement
    def simple_statement(self, name):

        class_name = f'%s nowrap' % name
        self.div(class_name)
        self.keyword(name)
        self.end_div(class_name)
    #@+node:ekr.20150722204300.16: *4* rt.html helpers
    #@+node:ekr.20150722204300.17: *5* rt.attr & text
    def attr(self, s):
        return self.text(s).replace("'", "&apos;").replace('"', "&quot;")

    def text(self, s):
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    #@+node:ekr.20150722204300.18: *5* rt.br
    def br(self):
        return '\n<br />'
    #@+node:ekr.20150722204300.19: *5* rt.comment
    def comment(self, comment):

        self.span('comment')
        self.gen('# '+comment)
        self.end_span('comment')
        self.newline()
    #@+node:ekr.20150722204300.20: *5* rt.div
    def div(self, class_name, extra=None, wrap=False):
        """Generate the start of a div element."""
        if class_name in self.enable_list:
            if class_name:
                full_class_name = class_name if wrap else class_name + ' nowrap'
            self.newline()
            if class_name and extra:
                self.gen(f"<div class='%s' %s>" % (full_class_name, extra))
            elif class_name:
                self.newline()
                self.gen(f"<div class='%s'>" % (full_class_name))
            else:
                assert not extra
                self.gen("<div>")
        self.div_stack.append(class_name)
    #@+node:ekr.20150722222149.1: *5* rt.div_body
    def div_body(self, aList):
        if aList:
            self.div_list('body', aList)
    #@+node:ekr.20150722221101.1: *5* rt.div_list & div_node
    def div_list(self, class_name, aList, sep=None):

        self.div(class_name)
        self.visit_list(aList, sep=sep)
        self.end_div(class_name)

    def div_node(self, class_name, node):

        self.div(class_name)
        self.visit(node)
        self.end_div(class_name)
    #@+node:ekr.20150723095033.1: *5* rt.end_div
    def end_div(self, class_name):

        if class_name in self.enable_list:
            # self.newline()
            self.gen('</div>')
            # self.newline()
        class_name2 = self.div_stack.pop()
        assert class_name2 == class_name, (class_name2, class_name)
    #@+node:ekr.20150723095004.1: *5* rt.end_span
    def end_span(self, class_name):

        if class_name in self.enable_list:
            self.gen('</span>')
            self.newline()
        class_name2 = self.div_stack.pop()
        assert class_name2 == class_name, (class_name2, class_name)
    #@+node:ekr.20150722221408.1: *5* rt.keyword_colon
    # def keyword_colon(self, keyword):

        # self.keyword(keyword)
        # self.colon()
    #@+node:ekr.20150722204300.5: *5* rt.link
    def link(self, class_name, href, a_text):

        return f"<a class='%s' href='%s'>%s</a>" % (
            class_name, href, a_text)
    #@+node:ekr.20150722204300.6: *5* rt.module_link
    def module_link(self, module_name, classes=None):

        return self.link(
            class_name=classes or 'name',
            href=f'%s.xhtml' % module_name,
            a_text=self.text(module_name))
    #@+node:ekr.20150722204300.7: *5* rt.name_link
    def name_link(self, module_name, full_name, name, classes=None):

        return self.link(
            class_name=classes or "specific-ref",
            href=f'%s.xhtml#%s' % (module_name, self.attr(full_name)),
            a_text=self.text(name))
    #@+node:ekr.20150722204300.8: *5* rt.object_name_ref
    def object_name_ref(self, module, obj, name=None, classes=None):
        """
        Link to the definition for 'module' using 'obj' with the optional 'name'
        used as the label (instead of the name of 'obj'). The optional 'classes'
        can be used to customise the CSS classes employed.
        """
        return self.name_link(
            module.full_name(),
            obj.full_name(),
            name or obj.name, classes)
    #@+node:ekr.20150722204300.9: *5* rt.popup
    def popup(self, classes, aList):

        self.span_list(classes or 'popup', aList)
    #@+node:ekr.20150722204300.28: *5* rt.span
    def span(self, class_name, wrap=False):

        if class_name in self.enable_list:
            self.newline()
            if class_name:
                full_class_name = class_name if wrap else class_name + ' nowrap'
                self.gen(f"<span class='%s'>" % (full_class_name))
            else:
                self.gen('<span>')
            # self.newline()
        self.div_stack.append(class_name)
    #@+node:ekr.20150722224734.1: *5* rt.span_list & span_node
    def span_list(self, class_name, aList, sep=None):

        self.span(class_name)
        self.visit_list(aList, sep=sep)
        self.end_span(class_name)

    def span_node(self, class_name, node):

        self.span(class_name)
        self.visit(node)
        self.end_span(class_name)
    #@+node:ekr.20150722204300.10: *5* rt.summary_link
    def summary_link(self, module_name, full_name, name, classes=None):

        return self.name_link(
            f"{module_name}-summary", full_name, name, classes)
    #@+node:ekr.20160315161259.1: *4* rt.main
    def main(self, fn, node):
        """Return a report for the given ast node as a string."""
        self.gen(self.html_header % {
                'css-fn': self.css_fn,
                'title': f"Module: {fn}"
            })
        self.parent = None
        self.parents = [None]
        self.visit(node)
        self.gen(self.html_footer)
        return ''.join(self.code_list)
    #@+node:ekr.20150722204300.44: *4* rt.visit
    def visit(self, node):
        """Walk a tree of AST nodes."""
        assert isinstance(node, ast.AST), node.__class__.__name__
        method_name = 'do_' + node.__class__.__name__
        method = getattr(self, method_name)
        method(node)
    #@+node:ekr.20150722204300.45: *4* rt.visit_list
    def visit_list(self, aList, sep=None):
        # pylint: disable=arguments-differ
        if aList:
            for z in aList:
                self.visit(z)
                self.gen(sep)
            self.clean(sep)
    #@+node:ekr.20150722204300.46: *4* rt.visitors
    #@+node:ekr.20170721074613.1: *5* rt.AnnAssign
    # AnnAssign(expr target, expr annotation, expr? value, int simple)

    def do_AnnAssign(self, node):

        self.div('statement')
        self.visit(node.target)
        self.op('=:', leading=True, trailing=True)
        self.visit(node.annotation)
        self.blank()
        self.visit(node.value)
        self.end_div('statement')
    #@+node:ekr.20150722204300.49: *5* rt.Assert
    # Assert(expr test, expr? msg)

    def do_Assert(self, node):

        self.div('statement')
        self.keyword("assert")
        self.visit(node.test)
        if node.msg:
            self.comma()
            self.visit(node.msg)
        self.end_div('statement')
    #@+node:ekr.20150722204300.50: *5* rt.Assign
    def do_Assign(self, node):

        self.div('statement')
        for z in node.targets:
            self.visit(z)
            self.op('=', leading=True, trailing=True)
        self.visit(node.value)
        self.end_div('statement')
    #@+node:ekr.20150722204300.51: *5* rt.Attribute
    # Attribute(expr value, identifier attr, expr_context ctx)

    def do_Attribute(self, node):

        self.visit(node.value)
        self.gen('.')
        self.gen(node.attr)
    #@+node:ekr.20160523102939.1: *5* rt.Await (Python 3)
    # Await(expr value)

    def do_Await(self, node):

        self.div('statement')
        self.keyword('await')
        self.visit(node.value)
        self.end_div('statement')
    #@+node:ekr.20150722204300.52: *5* rt.AugAssign
    #  AugAssign(expr target, operator op, expr value)

    def do_AugAssign(self, node):

        op_name_ = op_name(node.op)
        self.div('statement')
        self.visit(node.target)
        self.op(op_name_, leading=True)
        self.visit(node.value)
        self.end_div('statement')
    #@+node:ekr.20150722204300.53: *5* rt.BinOp
    def do_BinOp(self, node):

        op_name_ = op_name(node.op)
        # self.span(op_name_)
        self.visit(node.left)
        self.op(op_name_, leading=True)
        self.visit(node.right)
        # self.end_span(op_name_)
    #@+node:ekr.20150722204300.54: *5* rt.BoolOp
    def do_BoolOp(self, node):

        op_name_ = op_name(node.op).strip()
        self.span(op_name_)
        for i, node2 in enumerate(node.values):
            if i > 0:
                self.keyword(op_name_)
            self.visit(node2)
        self.end_span(op_name_)
    #@+node:ekr.20150722204300.55: *5* rt.Break
    def do_Break(self, node):

        self.simple_statement('break')
    #@+node:ekr.20160523103529.1: *5* rt.Bytes (Python 3)
    def do_Bytes(self, node):  # Python 3.x only.
        return str(node.s)
    #@+node:ekr.20150722204300.56: *5* rt.Call & do_keyword
    # Call(expr func, expr* args, keyword* keywords, expr? starargs, expr? kwargs)

    def do_Call(self, node):

        # self.span("callfunc")
        self.visit(node.func)
        # self.span("call")
        self.gen('(')
        self.visit_list(node.args, sep=',')
        if node.keywords:
            self.visit_list(node.keywords, sep=',')
        if getattr(node, 'starargs', None):
            self.op('*', trailing=False)
            self.visit(node.starargs)
            self.comma()
        if getattr(node, 'kwargs', None):
            self.op('**', trailing=False)
            self.visit(node.kwargs)
            self.comma()
        self.clean_comma()
        self.gen(')')
        # self.end_span('call')
        # self.end_span('callfunc')
    #@+node:ekr.20150722204300.57: *6* rt.do_keyword
    # keyword = (identifier arg, expr value)
    # keyword arguments supplied to call

    def do_keyword(self, node):

        self.span('keyword-arg')
        self.gen(node.arg)
        self.blank()
        self.gen('=')
        self.blank()
        self.visit(node.value)
        self.end_span('keyword-arg')
    #@+node:ekr.20150722204300.58: *5* rt.ClassDef
    # 2: ClassDef(identifier name, expr* bases,
    #             stmt* body, expr* decorator_list)
    # 3: ClassDef(identifier name, expr* bases,
    #             keyword* keywords, expr? starargs, expr? kwargs
    #             stmt* body, expr* decorator_list)
    #
    # keyword arguments supplied to call (NULL identifier for **kwargs)
    # keyword = (identifier? arg, expr value)

    def do_ClassDef(self, node):

        has_bases = (node.bases or hasattr(node, 'keywords') or
            hasattr(node, 'starargs') or hasattr(node, 'kwargs'))
        self.div('class')
        self.keyword("class")
        self.gen(node.name)  # Always a string.
        if has_bases:
            self.gen('(')
            self.visit_list(node.bases, sep=', ')
            if getattr(node, 'keywords', None):  # Python 3
                for keyword in node.keywords:
                    self.gen(f'%s=%s' % (keyword.arg, self.visit(keyword.value)))
            if getattr(node, 'starargs', None):  # Python 3
                self.gen(f'*%s' % self.visit(node.starargs))
            if getattr(node, 'kwargs', None):  # Python 3
                self.gen(f'*%s' % self.visit(node.kwargs))
            self.gen(')')
        self.colon()
        self.div('body')
        self.doc(node)
        self.visit_list(node.body)
        self.end_div('body')
        self.end_div('class')
    #@+node:ekr.20150722204300.59: *5* rt.Compare
    def do_Compare(self, node):

        assert len(node.ops) == len(node.comparators)
        # self.span('compare')
        self.visit(node.left)
        for i in range(len(node.ops)):
            op_name_ = op_name(node.ops[i])
            self.op(op_name_, leading=True)
            self.visit(node.comparators[i])
        # self.end_span('compare')
    #@+node:ekr.20150722204300.60: *5* rt.comprehension
    # comprehension = (expr target, expr iter, expr* ifs)

    def do_comprehension(self, node):

        self.visit(node.target)
        self.keyword('in')
        # self.span('collection')
        self.visit(node.iter)
        if node.ifs:
            self.keyword('if')
            # self.span_list("conditional", node.ifs, sep=' ')
            for z in node.ifs:
                self.visit(z)
                self.blank()
            self.clean(' ')
        # self.end_span('collection')
    #@+node:ekr.20170721073431.1: *5* rt.Constant (Python 3.6+)
    def do_Constant(self, node):  # Python 3.6+ only.
        return str(node.s)  # A guess.
    #@+node:ekr.20150722204300.61: *5* rt.Continue
    def do_Continue(self, node):

        self.simple_statement('continue')
    #@+node:ekr.20150722204300.62: *5* rt.Delete
    def do_Delete(self, node):

        self.div('statement')
        self.keyword('del')
        if node.targets:
            self.visit_list(node.targets, sep=',')
        self.end_div('statement')
    #@+node:ekr.20150722204300.63: *5* rt.Dict
    def do_Dict(self, node):

        assert len(node.keys) == len(node.values)
        # self.span('dict')
        self.gen('{')
        for i in range(len(node.keys)):
            self.visit(node.keys[i])
            self.colon()
            self.visit(node.values[i])
            self.comma()
        self.clean_comma()
        self.gen('}')
        # self.end_span('dict')
    #@+node:ekr.20160523104330.1: *5* rt.DictComp
    # DictComp(expr key, expr value, comprehension* generators)

    def do_DictComp(self, node):
        elt = self.visit(node.elt)
        gens = [self.visit(z) for z in node.generators]
        gens = [z if z else '<**None**>' for z in gens]  # Kludge: probable bug.
        return f'%s for %s' % (elt, ''.join(gens))
    #@+node:ekr.20150722204300.47: *5* rt.do_arguments & helpers
    # arguments = (expr* args, identifier? vararg, identifier? kwarg, expr* defaults)

    def do_arguments(self, node):

        assert isinstance(node, ast.arguments), node
        first_default = len(node.args) - len(node.defaults)
        for n, arg in enumerate(node.args):
            if isinstance(arg, (list, tuple)):
                self.tuple_parameter(arg)
            else:
                self.visit(arg)
            if n >= first_default:
                default = node.defaults[n - first_default]
                self.gen("=")
                self.visit(default)
            self.comma()
        if getattr(node, 'vararg', None):
            self.gen('*')
            self.gen(self.name(node.vararg))
            self.comma()
        if getattr(node, 'kwarg', None):
            self.gen('**')
            self.gen(self.name(node.kwarg))
            self.comma()
        self.clean_comma()
    #@+node:ekr.20160315182225.1: *6* rt.arg (Python 3 only)
    # 3: arg = (identifier arg, expr? annotation)

    def do_arg(self, node):

        self.gen(node.arg)
        if getattr(node, 'annotation', None):
            self.colon()
            self.visit(node.annotation)
    #@+node:ekr.20150722204300.48: *6* rt.tuple_parameter
    def tuple_parameter(self, node):

        assert isinstance(node, (list, tuple)), node
        self.gen("(")
        for param in node:
            if isinstance(param, tuple):
                self.tuple_parameter(param)
            else:
                self.visit(param)
        self.gen(")")
    #@+node:ekr.20150722204300.64: *5* rt.Ellipsis
    def do_Ellipsis(self, node):

        self.gen('...')
    #@+node:ekr.20150722204300.65: *5* rt.ExceptHandler
    def do_ExceptHandler(self, node):

        self.div('excepthandler')
        self.keyword("except")
        if not node.type:
            self.clean(' ')
        if node.type:
            self.visit(node.type)
        if node.name:
            self.keyword('as')
            self.visit(node.name)
        self.colon()
        self.div_body(node.body)
        self.end_div('excepthandler')
    #@+node:ekr.20150722204300.66: *5* rt.Exec
    # Python 2.x only.

    def do_Exec(self, node):

        self.div('statement')
        self.keyword('exec')
        self.visit(node.body)
        if node.globals:
            self.comma()
            self.visit(node.globals)
        if node.locals:
            self.comma()
            self.visit(node.locals)
        self.end_div('statement')
    #@+node:ekr.20150722204300.67: *5* rt.Expr
    def do_Expr(self, node):

        self.div_node('expr', node.value)
    #@+node:ekr.20160523103429.1: *5* rf.Expression
    def do_Expression(self, node):
        """An inner expression: do not indent."""
        return f'%s' % self.visit(node.body)
    #@+node:ekr.20160523103751.1: *5* rt.ExtSlice
    def do_ExtSlice(self, node):
        return ':'.join([self.visit(z) for z in node.dims])
    #@+node:ekr.20150722204300.68: *5* rt.For & AsyncFor (Python 3)
    # For(expr target, expr iter, stmt* body, stmt* orelse)

    def do_For(self, node, async_flag=False):

        self.div('statement')
        if async_flag:
            self.keyword('async')
        self.keyword("for")
        self.visit(node.target)
        self.keyword("in")
        self.visit(node.iter)
        self.colon()
        self.div_body(node.body)
        if node.orelse:
            self.keyword('else')
            self.colon()
            self.div_body(node.orelse)
        self.end_div('statement')

    def do_AsyncFor(self, node):
        self.do_For(node, async_flag=True)
    #@+node:ekr.20170721075845.1: *5* rf.FormattedValue (Python 3.6+: unfinished)
    # FormattedValue(expr value, int? conversion, expr? format_spec)

    def do_FormattedValue(self, node):  # Python 3.6+ only.
        self.div('statement')
        self.visit(node.value)
        if node.conversion:
            self.visit(node.conversion)
        if node.format_spec:
            self.visit(node.format_spec)
        self.end_div('statement')
    #@+node:ekr.20150722204300.69: *5* rt.FunctionDef
    # 2: FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list)
    # 3: FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list,
    #                expr? returns)

    def do_FunctionDef(self, node, async_flag=False):

        self.div('function', extra=f'id="%s"' % node.name)
        if async_flag:
            self.keyword('async')
        self.keyword("def")
        self.name(node.name)
        self.gen('(')
        self.visit(node.args)
        self.gen(')')
        if getattr(node, 'returns', None):
            self.blank()
            self.gen('->')
            self.blank()
            self.visit(node.returns)
        self.colon()
        self.div('body')
        self.doc(node)
        self.visit_list(node.body)
        self.end_div('body')
        self.end_div('function')

    def do_AsyncFunctionDef(self, node):
        self.do_FunctionDef(node, async_flag=True)
    #@+node:ekr.20150722204300.70: *5* rt.GeneratorExp
    def do_GeneratorExp(self, node):

        # self.span('genexpr')
        self.gen('(')
        if node.elt:
            self.visit(node.elt)
        self.keyword('for')
        # self.span_node('item', node.elt)
        self.visit(node.elt)
        # self.span_list('generators', node.generators)
        self.visit_list(node.generators)
        self.gen(')')
        # self.end_span('genexpr')
    #@+node:ekr.20150722204300.71: *5* rt.get_import_names
    def get_import_names(self, node):
        """Return a list of the the full file names in the import statement."""
        result = []
        for ast2 in node.names:
            assert isinstance(ast2, ast.alias), repr(ast2)
            data = ast2.name, ast2.asname
            result.append(data)
        return result
    #@+node:ekr.20150722204300.72: *5* rt.Global
    def do_Global(self, node):

        self.div('statement')
        self.keyword("global")
        for z in node.names:
            self.gen(z)
            self.comma()
        self.clean_comma()
        self.end_div('statement')
    #@+node:ekr.20150722204300.73: *5* rt.If
    # If(expr test, stmt* body, stmt* orelse)

    def do_If(self, node, elif_flag=False):
        
        self.div('statement')
        self.keyword('elif' if elif_flag else 'if')
        self.visit(node.test)
        self.colon()
        self.div_body(node.body)
        if node.orelse:
            node1 = node.orelse[0]
            if isinstance(node1, ast.If) and len(node.orelse) == 1:
                self.do_If(node1, elif_flag=True)
            else:
                self.keyword('else')
                self.colon()
                self.div_body(node.orelse)
        self.end_div('statement')
    #@+node:ekr.20150722204300.74: *5* rt.IfExp (TernaryOp)
    # IfExp(expr test, expr body, expr orelse)

    def do_IfExp(self, node):

        # self.span('ifexp')
        self.visit(node.body)
        self.keyword('if')
        self.visit(node.test)
        self.keyword('else')
        self.visit(node.orelse)
        # self.end_span('ifexp')
    #@+node:ekr.20150722204300.75: *5* rt.Import
    def do_Import(self, node):

        self.div('statement')
        self.keyword("import")
        for name, alias in self.get_import_names(node):
            self.name(name)  # self.gen(self.module_link(name))
            if alias:
                self.keyword("as")
                self.name(alias)
        self.end_div('statement')
    #@+node:ekr.20150722204300.76: *5* rt.ImportFrom
    def do_ImportFrom(self, node):

        self.div('statement')
        self.keyword("from")
        self.gen(self.module_link(node.module))
        self.keyword("import")
        for name, alias in self.get_import_names(node):
            self.name(name)
            if alias:
                self.keyword("as")
                self.name(alias)
            self.comma()
        self.clean_comma()
        self.end_div('statement')
    #@+node:ekr.20160315190818.1: *5* rt.Index
    def do_Index(self, node):

        self.visit(node.value)
    #@+node:ekr.20170721080959.1: *5* rf.JoinedStr (Python 3.6+: unfinished)
    # JoinedStr(expr* values)

    def do_JoinedStr(self, node):
        for value in node.values or []:
            self.visit(value)
    #@+node:ekr.20150722204300.77: *5* rt.Lambda
    def do_Lambda(self, node):

        # self.span('lambda')
        self.keyword('lambda')
        self.visit(node.args)
        self.comma()
        self.span_node("code", node.body)
        # self.end_span('lambda')
    #@+node:ekr.20150722204300.78: *5* rt.List
    # List(expr* elts, expr_context ctx)

    def do_List(self, node):

        # self.span('list')
        self.gen('[')
        if node.elts:
            for z in node.elts:
                self.visit(z)
                self.comma()
            self.clean_comma()
        self.gen(']')
        # self.end_span('list')
    #@+node:ekr.20150722204300.79: *5* rt.ListComp
    # ListComp(expr elt, comprehension* generators)

    def do_ListComp(self, node):

        # self.span('listcomp')
        self.gen('[')
        if node.elt:
            self.visit(node.elt)
        self.keyword('for')
        # self.span('ifgenerators')
        self.visit_list(node.generators)
        self.gen(']')
        # self.end_span('ifgenerators')
        # self.end_span('listcomp')
    #@+node:ekr.20150722204300.80: *5* rt.Module
    def do_Module(self, node):

        self.doc(node)
        self.visit_list(node.body)
    #@+node:ekr.20150722204300.81: *5* rt.Name
    def do_Name(self, node):

        self.name(node.id)
    #@+node:ekr.20160315165109.1: *5* rt.NameConstant
    def do_NameConstant(self, node):  # Python 3 only.

        self.name(repr(node.value))
    #@+node:ekr.20160317051849.2: *5* rt.Nonlocal (Python 3)
    # Nonlocal(identifier* names)

    def do_Nonlocal(self, node):

        self.div('statement')
        self.keyword('nonlocal')
        self.gen(', '.join(node.names))
        self.end_div('statement')
    #@+node:ekr.20150722204300.82: *5* rt.Num
    def do_Num(self, node):

        self.gen(self.text(repr(node.n)))
    #@+node:ekr.20150722204300.83: *5* rt.Pass
    def do_Pass(self, node):

        self.simple_statement('pass')
    #@+node:ekr.20150722204300.84: *5* rt.Print
    # Print(expr? dest, expr* values, bool nl)

    def do_Print(self, node):

        self.div('statement')
        self.keyword("print")
        self.gen('(')
        if node.dest:
            self.op('>>\n')
            self.visit(node.dest)
            self.comma()
            self.newline()
            if node.values:
                for z in node.values:
                    self.visit(z)
                    self.comma()
                    self.newline()
        self.clean('\n')
        self.clean_comma()
        self.gen(')')
        self.end_div('statement')
    #@+node:ekr.20150722204300.85: *5* rt.Raise
    # Raise(expr? type, expr? inst, expr? tback)    Python 2
    # Raise(expr? exc, expr? cause)                 Python 3

    def do_Raise(self, node):

        self.div('statement')
        self.keyword("raise")
        for attr in ('exc', 'cause'):
            if getattr(node, attr, None) is not None:
                self.visit(getattr(node, attr))
        self.end_div('statement')
    #@+node:ekr.20160523105022.1: *5* rt.Repr
    # Python 2.x only

    def do_Repr(self, node):
        return f'repr(%s)' % self.visit(node.value)
    #@+node:ekr.20150722204300.86: *5* rt.Return
    def do_Return(self, node):

        self.div('statement')
        self.keyword("return")
        if node.value:
            self.visit(node.value)
        self.end_div('statement')
    #@+node:ekr.20160523104433.1: *5* rt.Set
    # Set(expr* elts)

    def do_Set(self, node):
        for z in node.elts:
            self.visit(z)
    #@+node:ekr.20160523104454.1: *5* rt.SetComp
    # SetComp(expr elt, comprehension* generators)

    def do_SetComp(self, node):

        elt = self.visit(node.elt)
        gens = [self.visit(z) for z in node.generators]
        return f'%s for %s' % (elt, ''.join(gens))
    #@+node:ekr.20150722204300.87: *5* rt.Slice
    def do_Slice(self, node):

        # self.span("slice")
        if node.lower:
            self.visit(node.lower)
        self.colon()
        if node.upper:
            self.visit(node.upper)
        if node.step:
            self.colon()
            self.visit(node.step)
        # self.end_span("slice")
    #@+node:ekr.20160317051849.3: *5* rt.Starred (Python 3)
    # Starred(expr value, expr_context ctx)

    def do_Starred(self, node):

        self.gen('*')
        self.visit(node.value)
    #@+node:ekr.20150722204300.88: *5* rt.Str
    def do_Str(self, node):
        """This represents a string constant."""

        def clean(s):
            return s.replace(' ', '').replace('\n', '').replace('"', '').replace("'", '')

        assert isinstance(node.s, str)
        if self.last_doc and clean(self.last_doc) == clean(node.s):
            # Already seen.
            self.last_doc = None
        else:
            self.string(node.s)
    #@+node:ekr.20150722204300.89: *5* rt.Subscript
    def do_Subscript(self, node):

        # self.span("subscript")
        self.visit(node.value)
        self.gen('[')
        self.visit(node.slice)
        self.gen(']')
        # self.end_span("subscript")
    #@+node:ekr.20160315190913.1: *5* rt.Try (Python 3)
    # Try(stmt* body, excepthandler* handlers, stmt* orelse, stmt* finalbody)

    def do_Try(self, node):

        self.div('statement')
        self.keyword('try')
        self.colon()
        self.div_list('body', node.body)
        for z in node.handlers:
            self.visit(z)
        for z in node.orelse:
            self.visit(z)
        if node.finalbody:
            self.keyword('finally')
            self.colon()
            self.div_list('body', node.finalbody)
        self.end_div('statement')
    #@+node:ekr.20150722204300.90: *5* rt.TryExcept
    def do_TryExcept(self, node):

        self.div('statement')
        self.keyword('try')
        self.colon()
        self.div_list('body', node.body)
        if node.orelse:
            self.keyword('else')
            self.colon()
            self.div_body(node.orelse)
        self.div_body(node.handlers)
        self.end_div('statement')
    #@+node:ekr.20150722204300.91: *5* rt.TryFinally
    def do_TryFinally(self, node):

        self.div('statement')
        self.keyword('try')
        self.colon()
        self.div_body(node.body)
        self.keyword('finally')
        self.colon()
        self.div_body(node.final.body)
        self.end_div('statement')
    #@+node:ekr.20150722204300.92: *5* rt.Tuple
    # Tuple(expr* elts, expr_context ctx)

    def do_Tuple(self, node):

        # self.span('tuple')
        self.gen('(')
        for z in node.elts or []:
            self.visit(z)
            self.comma()
        self.clean_comma()
        self.gen(')')
        # self.end_span('tuple')
    #@+node:ekr.20150722204300.94: *5* rt.While
    def do_While(self, node):

        self.div('statement')
        self.div(None)
        self.keyword("while")
        self.visit(node.test)
        self.colon()
        self.end_div(None)
        self.div_list('body', node.body)
        if node.orelse:
            self.keyword('else')
            self.colon()
            self.div_body(node.orelse)
        self.end_div('statement')
    #@+node:ekr.20150722204300.93: *5* rt.UnaryOp
    def do_UnaryOp(self, node):

        op_name_ = op_name(node.op).strip()
        # self.span(op_name_)
        self.op(op_name_, trailing=False)
        self.visit(node.operand)
        # self.end_span(op_name_)
    #@+node:ekr.20150722204300.95: *5* rt.With & AsyncWith (Python 3)
    # 2:  With(expr context_expr, expr? optional_vars,
    #          stmt* body)
    # 3:  With(withitem* items,
    #          stmt* body)
    # withitem = (expr context_expr, expr? optional_vars)

    def do_With(self, node, async_flag=False):

        context_expr = getattr(node, 'context_expr', None)
        optional_vars = getattr(node, 'optional_vars', None)
        items = getattr(node, 'items', None)
        self.div('statement')
        if async_flag:
            self.keyword('async')
        self.keyword('with')
        if context_expr:
            self.visit(context_expr)
        if optional_vars:
            self.keyword('as')
            self.visit_list(optional_vars)
        if items:
            for item in items:
                self.visit(item.context_expr)
                if getattr(item, 'optional_vars', None):
                    self.keyword('as')
                    self.visit(item.optional_vars)
        self.colon()
        self.div_body(node.body)
        self.end_div('statement')

    def do_AsyncWith(self, node):
        self.do_With(node, async_flag=True)
    #@+node:ekr.20150722204300.96: *5* rt.Yield
    def do_Yield(self, node):

        self.div('statement')
        self.keyword('yield')
        self.visit(node.value)
        self.end_div('statement')
    #@+node:ekr.20160317051849.5: *5* rt.YieldFrom (Python 3)
    # YieldFrom(expr value)

    def do_YieldFrom(self, node):

        self.div('statement')
        self.keyword('yield from')
        self.visit(node.value)
        self.end_div('statement')
    #@-others
#@+node:ekr.20191227170540.1: ** Test classes
#@+node:ekr.20191227154302.1: *3*  class BaseTest (TestCase)
class BaseTest (unittest.TestCase):
    """
    The base class of all tests of leoAst.py.
    
    This class contains only helpers.
    """
    
    # Statistics.
    counts, times = {}, {}

    #@+others
    #@+node:ekr.20191227054856.1: *4* BaseTest.make_data
    def make_data(self, contents, description=None, trace_mode=False):
        """Return (tokens, tree) for the given contents."""
        contents = contents.lstrip('\\\n')
        if not contents:
            return None, None
        t1 = get_time()
        self.update_counts('characters', len(contents))
        contents = g.adjustTripleString(contents)
        self.contents = contents.rstrip() + '\n'
        # Create the TOI instance.
        self.toi = TokenOrderInjector()
        self.toi.trace_mode = trace_mode
        # Pass 0.1: create the tokens.
        tokens = self.make_tokens(contents, trace_mode=False)
        # Pass 0.2: make the tree.
        tree = self.make_tree(contents)
        # Pass 0.3: balance the tokens.
        self.balance_tokens(tokens)
        # Pass 1.1: create the links.
        self.create_links(tokens, tree)
        # Pass 1.2: reassign paren tokens.
        self.reassign_tokens(tokens, tree)
        t2 = get_time()
        self.update_times('90: TOTAL', t2 - t1)
        return tokens, tree
    #@+node:ekr.20191227103533.1: *4* BaseTest.make_file_data
    def make_file_data(self, filename):
        """Return (tokens, tree) corresponding to the contents of the given file."""
        filename = os.path.join(r'c:\leo.repo\leo-editor\leo\core', filename)
        with open(filename, 'r') as f:
            contents = f.read()
        return self.make_data(contents=contents, description=filename)
        
    #@+node:ekr.20191228101601.1: *4* BaseTest: passes...
    #@+node:ekr.20191228095945.11: *5* 0.1: BaseTest.make_tokens
    def make_tokens(self, contents, trace_mode=False):
        """BaseTest.make_tokens. Make tokens from contents."""
        t1 = get_time()
        # Tokenize.
        tokens = self.toi.make_tokens(contents, trace_mode=trace_mode)
        t2 = get_time()
        self.update_counts('tokens', len(tokens))
        self.update_times('01: make-tokens', t2-t1)
        return tokens
    #@+node:ekr.20191228102101.1: *5* 0.2: BaseTest.make_tree
    def make_tree(self, contents):
        """
        BaseTest.make_tree.
        
        Return the parse tree for the given contents string.
        """
        t1 = get_time()
        tree = self.toi.make_tree(contents)
        t2 = get_time()
        self.update_times('02: parse_ast', t2-t1)
        return tree
    #@+node:ekr.20191228185201.1: *5* 0.3: BaseTest.balance_tokens
    def balance_tokens(self, tokens):
        """
        BastTest.balance_tokens.
        
        Insert links between corresponding paren tokens.
        """
        t1 = get_time()
        count = self.toi.balance_tokens(tokens)
        t2 = get_time()
        self.update_counts('paren-tokens', count)
        self.update_times('03: balance-tokens', t2-t1)
        return count
    #@+node:ekr.20191228101437.1: *5* 1.1: BaseTest.create_links
    def create_links(self, tokens, tree, filename='unit test'):
        """
        BaseTest.create_links.
        
        Insert two-way links between the tokens and ast tree.
        """
        toi = self.toi
        # Catch exceptions so we can get data late.
        try:
            t1 = get_time()
            # Yes, list *is* required here.
            list(toi.create_links(tokens, tree))
            t2 = get_time()
            self.update_counts('nodes', toi.n_nodes)
            self.update_times('11: create-links', t2 - t1)
        except Exception as e:
            g.trace(f"\nFAIL: make-tokens\n")
            # Don't use g.trace.  It doesn't handle newlines properly.
            print(e)
            g.es_exception()
            raise
    #@+node:ekr.20191229065358.1: *5* 1.2: BaseTest.reassign_tokens
    def reassign_tokens(self, tokens, tree, filename='unit test'):
        """
        BaseTest.reassign_tokens.
        
        Reassign tokens to ast nodes. This pass is optional.
        """
        toi = self.toi
        assert isinstance(toi, TokenOrderGenerator), repr(toi)
        t1 = get_time()
        toi.reassign_tokens(tokens, tree)
        t2 = get_time()
        self.update_times('12: reassign-links', t2 - t1)
    #@+node:ekr.20191228095945.10: *5* 3.1: BaseTest.fstringify
    def fstringify(self, tokens, tree, filename=''):
        """
        BaseTest.fstringify.
        
        Run TOG.fstringify and measure its time.
        """
        toi = self.toi
        assert isinstance(toi, TokenOrderGenerator), repr(toi)
        t1 = get_time()
        result_s = toi.fstringify(tokens, tree)
        t2 = get_time()
        self.update_times('31: fstringify', t2 - t1)
        return result_s
    #@+node:ekr.20191228095945.1: *4* BaseTest: stats...
    # Actions should fail by throwing an exception.
    #@+node:ekr.20191228095945.12: *5* BaseTest.dump_stats & helpers
    def dump_stats(self):
        """Show all calculated statistics."""
        if self.counts or self.times:
            print('')
            self.dump_counts()
            self.dump_times()
            print('')
    #@+node:ekr.20191228154757.1: *6* BaseTest.dump_counts
    def dump_counts(self):
        """Show all calculated counts."""
        for key, n in self.counts.items():
            print(f"{key:>16}: {n:>6}")
    #@+node:ekr.20191228154801.1: *6* BaseTest.dump_times
    def dump_times(self):
        """
        Show all calculated times.
        
        Keys should start with a priority (sort order) of the form `[0-9][0-9]:`
        """
        for key in sorted(self.times):
            t = self.times.get(key)
            key2 = key[3:]
            print(f"{key2:>16}: {t:6.3f} sec.")
       
    #@+node:ekr.20191228181624.1: *5* BaseTest.update_counts & update_times
    def update_counts(self, key, n):
        """Update the count statistic given by key, n."""
        old_n = self.counts.get(key, 0)
        self.counts [key] = old_n + n

    def update_times(self, key, t):
        """Update the timing statistic given by key, t."""
        old_t = self.times.get(key, 0.0)
        self.times [key] = old_t + t
    #@-others
#@+node:ekr.20141012064706.18390: *3* class AstDumper
class AstDumper:
    """
    A class supporting various kinds of dumps of ast nodes.
    """

    #@+others
    #@+node:ekr.20191112033445.1: *4* dumper.dump_tree_and_links & helper
    def dump_tree_and_links(self, node):
        """Briefly show a tree, properly indented."""
        result = [self.show_header()]
        self.dump_tree_and_links_helper(node, 0, result)
        return ''.join(result)
    #@+node:ekr.20191125035321.1: *5* dumper.dump_tree_and_links_helper
    def dump_tree_and_links_helper(self, node, level, result):
        """Return the list of lines in result."""
        if node is None:
            return
        # Let block.
        indent = ' ' * 2 * level
        children = getattr(node, 'children', [])
        node_s = self.compute_node_string(node, level)
        # Dump...
        if isinstance(node, (list, tuple)):
            for z in node:
                self.dump_tree_and_links_helper(z, level, result)
        elif isinstance(node, str):
            result.append(f"{indent}{node.__class__.__name__:>8}:{node}\n")
        elif isinstance(node, ast.AST):
            # Node and parent.
            result.append(node_s)
            # Children.
            for z in children:
                self.dump_tree_and_links_helper(z, level+1, result)
        else:
            result.append(node_s)
    #@+node:ekr.20191125035600.1: *4* dumper.compute_node_string & helpers
    def compute_node_string(self, node, level):
        """Return a string summarizing the node."""
        index_ivar = 'node_index'
        indent = ' ' * 2 * level
        parent = getattr(node, 'parent', None)
        node_id = getattr(node, index_ivar, '??')
        parent_id = getattr(parent, index_ivar, '??')
        parent_s = f"{parent_id:<3} {parent.__class__.__name__}" if parent else ''
        class_name = node.__class__.__name__
        descriptor_s = class_name + ': ' + self.show_fields(class_name, node, 22)
        tokens_s = self.show_tokens(node, 70, 100)
        lines = self.show_line_range(node)
        full_s1 = f"{parent_s:<16} {lines:<10} {node_id:<3} {indent}{descriptor_s} "
        node_s =  f"{full_s1:<70} {tokens_s}\n"
        return node_s
    #@+node:ekr.20191113223424.1: *5* dumper.show_fields
    def show_fields(self, class_name, node, truncate_n):
        """Return a string showing interesting fields of the node."""
        val = ''
        if class_name == 'JoinedStr':
            values = node.values
            assert isinstance(values, list)
            # Str tokens may represent *concatenated* strings.
            results = []
            fstrings, strings = 0, 0
            for z in values:
                assert isinstance(z, (ast.FormattedValue, ast.Str))
                if isinstance(z, ast.Str):
                    results.append(z.s)
                    strings += 1
                else:
                    results.append(z.__class__.__name__)
                    fstrings += 1
            val = f"{strings} str, {fstrings} f-str"
        elif class_name == 'keyword':
            if isinstance(node.value, ast.Str):
                val = f"arg={node.arg}..Str.value.s={node.value.s}"
            elif isinstance(node.value, ast.Name):
                val = f"arg={node.arg}..Name.value.id={node.value.id}"
            else:
                val = f"arg={node.arg}..value={node.value.__class__.__name__}"
        elif class_name == 'Name':
            val = f"id={node.id!r}"
        elif class_name == 'NameConstant':
            val = f"value={node.value!r}"
        elif class_name == 'Num':
            val = f"n={node.n}"
        elif class_name == 'Starred':
            if isinstance(node.value, ast.Str):
                val = f"s={node.value.s}"
            elif isinstance(node.value, ast.Name):
                val = f"id={node.value.id}"
            else:
                val = f"s={node.value.__class__.__name__}"
        elif class_name == 'Str':
            val = f"s={node.s!r}"
        elif class_name in ('AugAssign', 'BinOp', 'BoolOp', 'UnaryOp'): # IfExp
            name = node.op.__class__.__name__
            val = f"op={_op_names.get(name, name)}"
        elif class_name == 'Compare':
            ops = ','.join([_op_names.get(z, repr(z)) for z in node.ops])
            val = f"ops={ops}"
        else:
            val = ''
        return g.truncate(val, truncate_n)

    #@+node:ekr.20191114054726.1: *5* dumper.show_line_range
    def show_line_range(self, node):
        
        token_list = getattr(node, 'token_list', [])
        if not token_list:
            return ''
        min_ = min([z.line_number for z in token_list])
        max_ = max([z.line_number for z in token_list])
        return f"{min_}" if min_ == max_ else f"{min_}..{max_}"
    #@+node:ekr.20191113223425.1: *5* dumper.show_tokens
    def show_tokens(self, node, n, m):
        """
        Return a string showing node.token_list.
        
        Split the result if n + len(result) > m
        """
        token_list = getattr(node, 'token_list', [])
        result = []
        for z in token_list:
            if z.kind == 'comment':
                val = g.truncate(z.value,10) # Short is good.
                result.append(f"{z.kind}({val})")
            elif z.kind == 'name':
                val = g.truncate(z.value,20)
                result.append(f"{z.kind}({val})")
            elif z.kind == 'newline':
                result.append(f"{z.kind} ({z.line_number}:{len(z.line)})")
            elif z.kind == 'number':
                result.append(f"{z.kind}({z.value})")
            elif z.kind == 'op':
                result.append(f"{z.kind}{z.value}")
            elif z.kind == 'string':
                val = g.truncate(z.value,30)
                result.append(f"{z.kind}({val})")
            elif z.kind == 'ws':
                result.append(f"{z.kind}({len(z.value)})")
            else:
                # Indent, dedent, encoding, etc.
                # Don't put a blank.
                continue 
            result.append(' ')
        #
        # split the line if it is too long.
        # g.printObj(result, tag='show_tokens')
        line, lines = [], []
        for r in result:
            line.append(r)
            if n + len(''.join(line)) >= m:
                lines.append(''.join(line))
                line = []
        lines.append(''.join(line))
        pad = '\n' + ' '*n
        return pad.join(lines)
    #@+node:ekr.20191110165235.5: *4* dumper.show_header
    def show_header(self):
        """Return a header string, but only the fist time."""
        return (
            f"{'parent':<16} {'lines':<10} {'node':<42} {'tokens'}\n"
            f"{'======':<16} {'=====':<10} {'====':<42} {'======'}\n")
    #@+node:ekr.20141012064706.18392: *4* dumper.dump_ast & helper
    annotate_fields=False
    include_attributes = False
    indent_ws = ' '

    def dump_ast(self, node, level=0):
        """
        Dump an ast tree. Adapted from ast.dump.
        """
        sep1 = f'\n%s' % (self.indent_ws * (level + 1))
        if isinstance(node, ast.AST):
            fields = [(a, self.dump_ast(b, level+1)) for a, b in self.get_fields(node)]
            if self.include_attributes and node._attributes:
                fields.extend([(a, self.dump_ast(getattr(node, a), level+1))
                    for a in node._attributes])
            if self.annotate_fields:
                aList = [f'%s=%s' % (a, b) for a, b in fields]
            else:
                aList = [b for a, b in fields]
            name = node.__class__.__name__
            sep = '' if len(aList) <= 1 else sep1
            return f'%s(%s%s)' % (name, sep, sep1.join(aList))
        if isinstance(node, list):
            sep = sep1
            return f'LIST[%s]' % ''.join(
                [f'%s%s' % (sep, self.dump_ast(z, level+1)) for z in node])
        return repr(node)
    #@+node:ekr.20141012064706.18393: *5* dumper.get_fields
    def get_fields(self, node):
        
        

        return (
            (a, b) for a, b in ast.iter_fields(node)
                if a not in ['ctx',] and b not in (None, [])
        )
    #@-others
#@+node:ekr.20191231130208.1: *3* class TestReassignTokens (BaseTest)
class TestReassignTokens (BaseTest):
    """Test cases for the ReassignTokens class."""
    #@+others
    #@+node:ekr.20191231130320.1: *4* test_reassign_tokens (to do)
    def test_reassign_tokens(self):
        pass
    #@+node:ekr.20191231130334.1: *4* test_nearest_common_ancestor
    def test_nearest_common_ancestor(self):
        
        contents = """name='uninverted %s' % d.name()"""
        tokens, tree = self.make_data(contents)
        dump_tree(tree)
    #@-others
#@+node:ekr.20191113133338.1: *3* class TestRunner
class TestRunner:
    """
    A testing framework for TokenOrderGenerator and related classes.
    """
    
    counts, times = {}, {}
    #@+<< define valid actions & flags >>
    #@+node:ekr.20191222064729.1: *4* << define valid actions & flags >>
    valid_actions = [
        'run-ast-tokens',       # Alternate pass 0.
        'make-tokens-and-tree', # Pass 0.
        'create-links',         # Pass 1.
        'fstringify',           # Pass 2.
        # Dumps...
        'dump-all',
        'dump-ast', # Was dump-raw-tree.
        'dump-contents',
        'dump-lines',
        'dump-results',
        'dump-times',
        'dump-tokens',
        'dump-tree',
    ]

    valid_flags = [
        'all',
        'all-leo-files',
        'coverage',
        'dump-all-after-fail',
        'dump-ast-tree-first',
        'dump-results',
        'dump-tokens-after-fail',
        'dump-tokens-first',
        'dump-tree-after-fail',
        'no-trace-after-fail',
        'set-trace-mode',
        'show-pass0-times',
        'show-create-links-time',
        'show-fstringify-time',
        'show-exception-after-fail',
        'show-make-tokens-time',
        'show-test-description',
        'show-test-kind',
        'summarize',
        'trace-tokenizer-tokens',
        'verbose-fail',
    ]
    #@-<< define valid actions & flags >>
    #@+others
    #@+node:ekr.20191205160754.4: *4* TR.run_tests & helpers
    def run_tests(self, actions, flags, root, contents=None):
        """The outer test runner."""
        # Startup.
        self.fails = []
        self.root = root
        self.times = {}
        # Create self.actions and self.flags.
        ok = self.make_actions_and_flags(actions, flags)
        if not ok:
            print('Aborting...')
            return
        flags = self.flags
        self.show_status()
        if contents:
            self.tests = [(contents, root.h or 'None')]
        elif 'all-leo-files' in flags:
            self.tests = self.make_leo_tests()
        else:
            self.tests = self.make_tests(root)
        # Execute all tests.
        t1 = get_time()
        for contents, description in self.tests:
            # run_one_test catches all exceptions.
            if 'show-test-description' in flags:
                print(f"Running {description}...")
            ok = self.run_one_test(contents, description)
            if not ok:
                self.fails.append(description)
            if 'fail-fast' in flags:
                break
        # End-of-tests reports.
        t2 = get_time()
        self.times['total_time'] = t2 - t1
        if 'coverage' in flags:
            self.show_coverage()
        if 'summarize' in flags:
            self.summarize()
    #@+node:ekr.20191205163727.1: *5* TR.make_actions_and_flags
    def make_actions_and_flags(self, actions, flags):
        """
        Create self.actions and self.flags.
        
        Return False if there are unknow actions or flags.
        """
        valid_actions, valid_flags = self.valid_actions, self.valid_flags
        # Check valid actions.
        for z in valid_actions:
            assert hasattr(self, z.replace('-','_')), repr(z)
        # Clean and check actions.
        self.actions = [z for z in actions if z in valid_actions]
        bad_actions = [z for z in actions if z not in valid_actions]
        if bad_actions:
            for z in bad_actions:
                print('Unknown action:', z)
            return False
        # Clean and check flags.
        flags = [z.lower() for z in flags or []]
        self.flags = [z for z in flags if z in valid_flags]
        bad_flags = [z for z in flags if z not in valid_flags]
        if bad_flags:
            for z in bad_flags:
                print('Unknown flag:', z)
            return False
        return True
    #@+node:ekr.20191205172431.1: *5* TR.make_leo_tests
    def make_leo_tests(self):
        """
        Leo-specific code for unit tests.
        
        Return a list of tuples (contents, description) for all of Leo's core
        .py files.
        """
        import leo.core.leoGlobals as leo_g
        core_directory = leo_g.os_path_finalize_join(leo_g.app.loadDir, '..', 'core')
        assert os.path.exists(core_directory), core_directory
        paths = glob.glob(core_directory + os.path.sep + 'leo*.py')
        tests = []
        for path in paths:
            assert os.path.exists(path), path
            with open(path, 'r') as f:
                contents = f.read()
            description = path
            tests.append((contents, description))   
        return tests

    #@+node:ekr.20191205160754.2: *5* TR.make_tests
    def make_tests(self, root):
        """
        Leo-specific code for unit tests.
        
        Return a list of tuples (contents, description) found in all children
        of the root, except this node.
        """
        import leo.core.leoGlobals as leo_g
        tests = []
        contents_tag = 'test:'
        file_tag = 'file:'
        after = root.nodeAfterTree()
        p = root.copy()
        while p and p != after:
            if p.h.startswith(('fail:', 'fails')):
                # Ignore all fails, regardless of 'all' flag.
                p.moveToNodeAfterTree()
            elif 'all' not in self.flags and p.h.startswith('ignore:'):
                # Honor 'ignore' only when *not* runnining all tests.
                p.moveToNodeAfterTree()
            elif p.h.startswith(contents_tag):
                description = p.h
                contents = p.b.strip() + '\n'
                tests.append((contents, description))
                p.moveToThreadNext()
            elif p.h.startswith(file_tag):
                description = p.h
                s = p.h[len(file_tag):].strip()
                parts = [leo_g.app.loadDir, '..'] + s.split('..')
                path = os.path.sep.join(parts)
                if os.path.exists(path):
                    with open(path, 'r') as f:
                        contents = f.read()
                    tests.append((contents, description))
                    p.moveToThreadNext()
                else:
                    assert False, f"file not found: {path}"
            else:
                # Ignore organizer nodes.
                p.moveToThreadNext()
        if not tests:
            print(f"no tests in {root.h}")
        return tests
    #@+node:ekr.20191122025155.1: *5* TR.show_coverage
    def show_coverage(self):
        if self.toi:
            self.toi.report_coverage()
    #@+node:ekr.20191205160754.5: *5* TR.show_status
    def show_status(self):
        """Show the preliminary status."""
        flags = self.flags
        print('')
        if 'show-test-kind' in flags:
            if 'all-leo-files' in flags:
                kind = 'Testing all Leo files'
            elif 'all' in flags:
                kind = 'Running *all* unit tests'
            else:
                kind = 'Running *selected* unit tests'
            print(f"{self.root.h}: {kind}...")
        if 'run-ast-tokens' in self.actions:
            print('\nUsing asttokens, *not* the TOG classes')
    #@+node:ekr.20191205160754.6: *5* TR.summarize
    def summarize(self):
        fails, tests = self.fails, self.tests
        status = 'FAIL' if fails else 'PASS'
        if fails:
            print('')
            g.printObj(fails, tag='Failed tests')
        print(
            f"\n{status} Ran "
            f"{len(tests)} test{g.plural(len(tests))}")
        if not 'dump-times' in self.flags:
            self.dump_times()
    #@+node:ekr.20191122021515.1: *4* TR.run_one_test
    def run_one_test(self, contents, description):
        """
        Run the test given by the contents and description.
        """
        tag = 'run_tests'
        self.description = description
        # flags = self.flags
        # Clean the contents.
        self.contents = contents = contents.strip() + '\n'
        
        #
        # Execute actions, in the user-defined order.
        bad_actions = []
        for action in self.actions:
            helper = getattr(self, action.replace('-', '_'), None)
            if helper:
                try:
                    helper()
                except Exception as e:
                    print(f"{tag}: Exception in {action}: {e}")
                    if 'show-exception-after-fail' in self.flags:
                        g.es_exception()
                    return False
            else:
                bad_actions.append(action)
        if bad_actions:
            for action in list(set(bad_actions)):
                print(f"{tag}: bad action option: {action!r}")
        return True
    #@+node:ekr.20191205160624.1: *4* TR: actions...
    # Actions should fail by throwing an exception.
    #@+node:ekr.20191226064933.1: *5* TR.create_links (pass 1)
    def create_links(self):
        """Pass 1: TOG.create_links"""
        flags, toi = self.flags, self.toi
        # Catch exceptions so we can get data late.
        try:
            t1 = get_time()
            # Yes, list *is* required here.
            list(toi.create_links(self.tokens, self.tree, file_name=self.description))
            t2 = get_time()
            self.update_times('10: create-links', t2 - t1)
        except Exception as e:
            g.trace(f"\nFAIL: make-tokens\n")
            # Don't use g.trace.  It doesn't handle newlines properly.
            print(e)
            if 'show-exception-after-fail' in flags:
                g.es_exception()
            if 'dump-all-after-fail' in flags:
                self.dump_all()
            else:
                if 'dump-tokens-after-fail' in flags:
                    self.dump_tokens()
                if 'dump-tree-after-fail' in flags:
                    self.dump_tree()
            if 'no-trace-after-fail':
                toi.trace_mode = False
            raise
    #@+node:ekr.20191122022728.1: *5* TR.dump_all
    def dump_all(self):

        if self.toi:
            self.dump_contents()
            self.dump_tokens()
            self.dump_tree()
            # self.dump_ast()

    #@+node:ekr.20191122025306.2: *5* TR.dump_ast
    def dump_ast(self):
        """Dump an ast tree.  Similar to ast.dump()."""
        print('\nast tree...\n')
        print(AstDumper().dump_ast(self.tree))
        print('')
    #@+node:ekr.20191122025303.1: *5* TR.dump_contents
    def dump_contents(self):
        contents = self.contents
        print('\nContents...\n')
        for i, z in enumerate(g.splitLines(contents)):
            print(f"{i+1:<3} ", z.rstrip())
        print('')
    #@+node:ekr.20191122025306.1: *5* TR.dump_lines
    def dump_lines(self):
        print('\nTOKEN lines...\n')
        for z in self.tokens:
            if z.line.strip():
                print(z.line.rstrip())
            else:
                print(repr(z.line))
        print('')
    #@+node:ekr.20191225063758.1: *5* TR.dump_results
    def dump_results(self):

        print('\nResults...\n')
        print(''.join(z.to_string() for z in self.tokens))
    #@+node:ekr.20191226095129.1: *5* TR.dump_times
    def dump_times(self):
        """
        Show all calculated times.
        
        Keys should start with a priority (sort order) of the form `[0-9][0-9]:`
        """
        if not self.times:
            return
        print('')
        for key in sorted(self.times):
            t = self.times.get(key)
            key2 = key[3:]
            print(f"{key2:>16}: {t:6.3f} sec.")
    #@+node:ekr.20191122025418.1: *5* TR.dump_tokens
    def dump_tokens(self):
        tokens = self.tokens
        print('\nTokens...\n')
        print("Note: values shown are repr(value) *except* for 'string' tokens.\n")
        # pylint: disable=not-an-iterable
        if self.toi:
            for z in tokens:
                print(z.dump())
            print('')
        else:
            import token as tm
            for z in tokens:
                kind = tm.tok_name[z.type].lower()
                print(f"{z.index:4} {kind:>12} {z.string!r}")
    #@+node:ekr.20191122025419.1: *5* TR.dump_tree
    def dump_tree(self):
        print('\nPatched tree...\n')
        tokens, tree = self.tokens, self.tree
        if self.toi:
            print(dump_tree_and_links(tree))
            return
        try:
            # pylint: disable=import-error
            from asttokens.util import walk
        except Exception:
            return
        for z in walk(tree):
            class_name = z.__class__.__name__
            first, last = z.first_token.index, z.last_token.index
            token_range = f"{first:>4}..{last:<4}"
            if isinstance(z, ast.Module):
                tokens_s = ''
            else:
                tokens_s = ' '.join(
                    repr(z.string) for z in tokens[first:last] if z)
            print(f"{class_name:>12} {token_range:<10} {tokens_s}")
    #@+node:ekr.20191222074711.1: *5* TR.fstringify (pass 2)
    def fstringify(self):
        """Pass 2: TOG.fstringify."""
        toi = self.toi
        assert isinstance(toi, TokenOrderGenerator), repr(toi)
        t1 = get_time()
        toi.fstringify(toi.tokens, toi.tree, filename='unit test')
        t2 = get_time()
        self.update_times('20: fstringify', t2 - t1)
    #@+node:ekr.20191226063007.1: *5* TR.make_tokens_and_tree (pass 0)
    def make_tokens_and_tree(self):
        """Pass 0: TOG.make_tokens."""
        contents, flags = self.contents, self.flags
        t1 = get_time()
        # Create and remember the toi.
        toi = self.toi = TokenOrderInjector()
        toi.trace_mode = 'set-trace-mode' in flags
        # Tokenize.
        self.tokens = toi.make_tokens(contents,
            trace_mode='trace-tokenizer-tokens' in flags)
        t2 = get_time()
        self.update_times('01: make-tokens', t2 - t1)
        # Parse.
        self.tree = parse_ast(contents)
        t3 = get_time()
        self.update_times('01: parse-ast', t3 - t2)
        # Dump.
        if 'dump-tokens-first' in flags:
            dump_tokens(self.tokens)
        if 'dump-ast-tree-first' in flags:
            dump_ast(self.tree)
    #@+node:ekr.20191226063942.1: *5* TR.run_ast_tokens
    def run_ast_tokens(self):
        # pylint: disable=import-error
        # It's ok to raise ImportError here.
        import asttokens
        t1 = get_time()
        atok = asttokens.ASTTokens(self.contents, parse=True)
        self.tree = atok.tree
        self.tokens = atok._tokens
        t2 = get_time()
        self.update_times('01: ast-tokens', t2 - t1)
    #@+node:ekr.20191228183156.1: *5* TR.update_counts & update_times
    def update_counts(self, key, n):
        """Update the count statistic given by key, n."""
        old_n = self.times.get(key, 0)
        self.counts [key] = old_n + n

    def update_times(self, key, t):
        """Update the timing statistic given by key, t."""
        old_t = self.times.get(key, 0.0)
        self.times [key] = old_t + t
    #@-others
   
#@+node:ekr.20191229083512.1: *3* class TestFstringify (BaseTest)
class TestFstringify (BaseTest):
    """Tests for the TokenOrderGenerator class."""
    #@+others
    #@+node:ekr.20191227052446.84: *4* test_fstringify_leo_app
    def test_fstringify_leo_app(self):
        
        filename = r'c:\test\core\leoApp.py'
        tokens, tree = self.make_file_data(filename)
        self.fstringify(tokens, tree, filename)
        self.dump_times()
    #@+node:ekr.20191230150653.1: *4* test_fstringify_with_call
    def test_fstringify_with_call(self):
        
        contents = "'%s' % d()" # d.name()
        tokens, tree = self.make_data(contents)
        dump_contents(contents)
        dump_tokens(tokens)
        dump_tree(tree)
        self.fstringify(tokens, tree, '<string>')
        # self.dump_times()
    #@+node:ekr.20191230183652.1: *4* test_fstringify_with_parens
    def test_fstringify_with_parens(self):

        contents = "print('%20s' % (ivar), val)"
        tokens, tree = self.make_data(contents)
        dump_contents(contents)
        dump_tokens(tokens)
        dump_tree(tree)
        self.fstringify(tokens, tree, '<string>')
        # self.dump_times()
    #@-others
#@+node:ekr.20191227051737.1: *3* class TestTOG (BaseTest)
class TestTOG (BaseTest):
    """Tests for the TokenOrderGenerator class."""
    #@+others
    #@+node:ekr.20191227052446.10: *4* Contexts...
    #@+node:ekr.20191227052446.11: *5* test_ClassDef
    def test_ClassDef(self):
        contents = r"""\
    class TestClass1:
        pass
        
    def decorator():
        pass

    @decorator
    class TestClass2:
        pass
        
    @decorator
    class TestClass(base1, base2):
        pass
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.12: *5* test_ClassDef2
    def test_ClassDef2(self):
        contents = r'''\
    """ds 1"""
    class TestClass:
        """ds 2"""
        def long_name(a, b=2):
            """ds 3"""
            print('done')
    '''
        self.make_data(contents)
    #@+node:ekr.20191227052446.13: *5* test_FunctionDef
    def test_FunctionDef(self):
        contents = r"""\
    def run(fileName=None, pymacs=None, *args, **keywords):
        pass
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.14: *4* Expressions & operators...
    #@+node:ekr.20191227052446.15: *5* test_attribute
    def test_attribute(self):
        contents = r"""\
    open(os.devnull, "w")
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.16: *5* test_CompareOp
    def test_CompareOp(self):
        contents = r"""\
    if a and not b and c:
        pass
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.17: *5* test_Dict
    def test_Dict(self):
        contents = r"""\
    d = {
        'a' if x else 'b': True,
        }
    f()
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.18: *5* test_DictComp
    def test_DictComp(self):
        # leoGlobals.py, line 3028.
        contents = r"""\
    d2 = {val: key for key, val in d.iteritems()}
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.19: *5* test_ListComp
    def test_ListComp(self):
        # ListComp and comprehension.
        contents = r"""\
    any([p2.isDirty() for p2 in p.subtree()])
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.20: *5* test_NameConstant
    def test_NameConstant(self):
        contents = r"""\
    run(a=None, b=str)
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.21: *5* test_Operator: semicolon
    def test_op_semicolon(self):
        contents = r"""\
    print('c');
    print('d')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.22: *5* test_Operator: semicolon between statements
    def test_op_semicolon2(self):
        contents = r"""\
    a = 1 ; b = 2
    print('a') ; print('b')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.23: *5* test_UnaryOp
    def test_UnaryOp(self):
        contents = r"""\
    print(-(2))
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.65: *4* f-strings....
    #@+node:ekr.20191227052446.66: *5* test_fstring01: complex Call
    def test_fstring1(self):
        # Line 1177, leoApp.py
        contents = r"""\
    print(
        message = f"line 1: {old_id!r}\n" "line 2\n"
    )
    print('done')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.67: *5* test_fstring02: Ternary
    def test_fstring2(self):
        contents = r"""\
    func(f"{b if not cond1 else ''}")
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.68: *5* test_fstring03: single f-string
    def test_fstring3(self):
        contents = r"""\
    print(f'{7.1}')
    print('end')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.69: *5* test_fstring04: f-string + plain
    def test_fstring4(self):
        contents = r"""\
    print(f'{7.1}' 'p7.2')
    print('end')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.70: *5* test_fstring05: plain + f-string
    def test_fstring5(self):
        contents = r"""\
    print('p1' f'{f2}')
    'end'
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.71: *5* test_fstring06: f-string + fstring
    def test_fstring6(self):
        contents = r"""\
    print(f'{f1}' f'{f2}')
    'end'
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.72: *5* test_fstring07: many
    def test_fstring7(self):
        contents = r"""\
    print('s1', f'{f2}' f'f3' f'{f4}' 's5')
    'end'
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.73: *5* test_fstring08: ternary op
    def test_fstring8(self):
        # leoFind.py line 856
        contents = r"""\
    a = f"{'a' if x else 'b'}"
    f()

    # Pass
    # print(f"{'a' if x else 'b'}")
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.74: *5* test_fstring09: leoFind.py line 856
    def test_fstring9(self):
        contents = r"""\
    func(
        "Isearch"
        f"{' Backward' if True else ''}"
    )
    print('done')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.75: *5* test_fstring10: leoFind.py: line 861
    def test_fstring10(self):
        # leoFind.py: line 861
        contents = r"""\
    one(f"{'B'}" ": ")
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.76: *5* test_fstring11: joins
    def test_fstring11(self):
        contents = r"""\
    print(f'x3{e3+1}y3' f'x4{e4+2}y4')
    print('done')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.77: *6* more
    # Single f-strings.
    # 'p1' ;
    # f'f1' ;
    # f'x1{e1}y1' ;
    # f'x2{e2+1}y2{e2+2}z2' ;

    # Concatentated strings...
    # 'p2', 'p3' ;
    # f'f2' 'f3' ;

    # f'x5{e5+1}y5{e5+1}z5' f'x6{e6+1}y6{e6+1}z6' ;
    #@+node:ekr.20191227052446.78: *5* test_fstring12: joins + 1 f-expr
    def test_fstring12(self):
        contents = r"""\
    print(f'x1{e1}y1', 'p1')
    print(f'x2{e2}y2', f'f2')
    print(f'x3{e3}y3', f'x4{e4}y4')
    print('end')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.79: *5* test_fstring13: joins + 2 f-exprs
    def test_fstring13(self):
        contents = r"""\
    print(f'x1{e1}y1{e2}z1', 'p1')
    print(f'x2{e3}y2{e3}z2', f'f2')
    print(f'x3{e4}y3{e5}z3', f'x4{e6}y4{e7}z4')
    print('end')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.80: *5* test_fstring14: complex, with commas
    def test_fstring14(self):
        contents = r"""\
    print(f"{list(z for z in ('a', 'b', 'c') if z != 'b')}")
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.81: *5* test_fstring15
    def test_fstring15(self):
        contents = r"""\
    print(f"test {a}={2}")
    print('done')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.83: *5* test_fstring16: simple
    def test_fstring16(self):
        contents = r"""\
    'p1' ;
    f'f1' ;
    'done' ;
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.82: *5* test_regex_fstring
    def test_regex_fstring(self):
        # Line 7709, leoGlobals.py
        contents = r'''\
    fr"""{kinds}://[^\s'"]+[\w=/]"""
    '''
        self.make_data(contents)
    #@+node:ekr.20191227052446.24: *4* Files...
    #@+node:ekr.20191227052446.25: *5* test_leoApp.py
    def test_leoApp(self):
        self.make_file_data('leoApp.py')
        
    #@+node:ekr.20191227052446.26: *5* test_leoAst.py
    def test_leoAst(self):
        self.make_file_data('leoAst.py')
       
    #@+node:ekr.20191227052446.27: *5* test_leoDebugger.py
    def test_leoDebugger(self):
        self.make_file_data('leoDebugger.py')
       
    #@+node:ekr.20191227052446.28: *5* test_leoFind.py
    def test_leoFind(self):
        self.make_file_data('leoFind.py')
       
    #@+node:ekr.20191227052446.29: *5* test_leoGlobals.py
    def test_leoGlobals(self):
        self.make_file_data('leoGlobals.py')
       
    #@+node:ekr.20191227052446.30: *5* test_leoTips.py
    def test_leoTips(self):
        self.make_file_data('leoTips.py')
       
    #@+node:ekr.20191227052446.31: *5* test_runLeo.py
    def test_runLeo(self):
        self.make_file_data('runLeo.py')
       
    #@+node:ekr.20191227052446.32: *4* If...
    #@+node:ekr.20191227052446.33: *5* test_from leoTips.py
    def test_if1(self):
        # Line 93, leoTips.py
        contents = r"""\
    self.make_data(contents)
    unseen = [i for i in range(5) if i not in seen]
    for issue in data:
        for a in aList:
            print('a')
        else:
            print('b')
    if b:
        print('c')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.34: *5* test_if + tuple
    def test_if2(self):
        contents = r"""\
    for i, j in b:
        pass
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.35: *5* test_if + unary op
    def test_if3(self):
        contents = r"""\
    if -(2):
        pass
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.36: *5* test_if, elif
    def test_if4(self):
        contents = r"""\
    if 1:
        print('a')
    elif 2:
        print('b')
    elif 3:
        print('c')
        print('d')
    print('-')
    if 1:
        print('e')
    elif 2:
        print('f')
        print('g')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.37: *5* test_if, elif + 2
    def test_if5(self):
        contents = r"""\
    if 1:
        pass
    elif 2:
        pass
        pass
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.38: *5* test_if, elif, else
    def test_if6(self):
        contents = r"""\
    if (a):
        print('a1')
        print('a2')
    elif b:
        print('b1')
        print('b2')
    else:
        print('c1')
        print('c2')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.39: *5* test_if, else
    def test_if7(self):
        contents = r"""\
    if 1:
        print('a')
    else:
        print('b')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.40: *5* test_if, else, if
    def test_if8(self):
        contents = r"""\
    if 1:
        print('a')
    else:
        if 2:
            print('b')
    """
        self.make_data(contents)

    #@+node:ekr.20191227052446.41: *5* test_Nested If's
    def test_if9(self):
        contents = r"""\
    if a:
        if b:
            print('b')
    else:
        if d:
            print('d')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.42: *5* test_ternary + if
    def test_if10(self):
        contents = r"""\
    if 1:
        a = 'class' if cond else 'def'
        # find_pattern = prefix + ' ' + word
        print('1')
    else:
        print('2')
    """
        self.make_data(contents)
    #@+node:ekr.20191227145620.1: *4* Miscellaneous...
    #@+node:ekr.20191227075951.1: *5* test_end_of_line
    def test_end_of_line(self):
        self.make_data("""# Only a comment.""")
    #@+node:ekr.20160521103254.1: *5* test_vistors_exist
    def test_vistors_exist(self):
        """Ensure that visitors for all ast nodes exist."""
        import _ast
        # Compute all fields to BaseTest.
        aList = sorted(dir(_ast))
        remove = [
            'Interactive', 'Suite',  # Not necessary.
            'PyCF_ONLY_AST',  # A constant,
            'AST',  # The base class,
        ]
        aList = [z for z in aList if not z[0].islower()]
            # Remove base classe
        aList = [z for z in aList
            if not z.startswith('_') and not z in remove]
        # Now test them.
        table = (
            # AstFullTraverser,
            AstFormatter,
            AstPatternFormatter,
            HTMLReportTraverser,
            TokenOrderGenerator,
        )
        for class_ in table:
            traverser = class_()
            errors, nodes, ops = 0, 0, 0
            for z in aList:
                if hasattr(traverser, 'do_'+z):
                    nodes += 1
                elif _op_names.get(z):
                    ops += 1
                else:
                    errors += 1
                    print(
                        f"Missing {traverser.__class__.__name__} visitor "
                        f"for: {z}")
        msg = f"{nodes} node types, {ops} op types, {errors} errors"
        assert not errors, msg
    #@+node:ekr.20191227052446.50: *4* Plain Strings...
    #@+node:ekr.20191227052446.52: *5* test_\x and \o escapes
    def test_escapes(self):
        # Line 4609, leoGlobals.py
        contents = r"""\
    print("\x7e" "\0777") # tilde.
    print('done')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.53: *5* test_backslashes in docstring
    def test_backslashes(self):
        # leoGlobals.py.
        contents = r'''\
    class SherlockTracer:
        """before\\after"""
    '''
        self.make_data(contents)
    #@+node:ekr.20191227052446.54: *5* test_bs/nl
    def test_bs_nl(self):
        contents = r"""\
    print('hello\
    world')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.55: *5* test_bytes bs-x
    def test_bytes(self):
        # Line 201, leoApp.py
        contents = r"""\
    print(b'\xfe')
    print('done')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.56: *5* test_empty string
    def test_empyt_string(self):
        contents = r"""\
    self.s = ''
    self.i = 0
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.57: *5* test_escaped string delims
    def test_escaped_delims(self):
        contents = r"""\
    print("a\"b")
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.58: *5* test_escaped strings
    def test_escaped_strings(self):
        contents = r"""\
    f1(a='\b', b='\n', t='\t')
    f2(f='\f', r='\r', v='\v')
    f3(bs='\\')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.59: *5* test_f-string join
    def test_fstring_join(self):
        # The first newline causes the fail.
        contents = r"""\
    print(f"a {old_id!r}\n" "b\n")
    print('done')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.60: *5* test_raw docstring
    def test_raw_docstring(self):
        contents = r'''\
    # Line 1619 leoFind.py
    print(r"""DS""")
    '''
        self.make_data(contents)
    #@+node:ekr.20191227052446.61: *5* test_raw escaped strings
    def test_raw_escapes(self):
        contents = r"""\
    r1(a=r'\b', b=r'\n', t=r'\t')
    r2(f=r'\f', r=r'\r', v=r'\v')
    r3(bs=r'\\')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.63: *5* test_string concatentation
    def test_concatentation(self):
        contents = r"""\
    print('a' 'b')
    print('c')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.62: *5* test_single quote
    def test_single_quote(self):
        # leoGlobals.py line 806.
        contents = r"""\
    print('"')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.64: *5* test_string with % op
    def test_potential_fstring(self):
        contents = r"""\
    print('test %s=%s'%(a, 2))
    print('done')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.43: *4* Statements...
    #@+node:ekr.20191227052446.44: *5* test_Call
    def test_Call(self):
        contents = r"""\
    f1(a,b=2)
    f2(1 + 2)
    f3(arg, *args, **kwargs)
    f4(a='a', *args, **kwargs)
    func(a, b, one='one', two='two', *args, **kwargs)
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.45: *5* test_Global
    def test_if12(self):
        # Line 1604, leoGlobals.py
        contents = r"""
    def spam():
        global gg
        print('')
    """
        self.make_data(contents)

    #@+node:ekr.20191227052446.46: *5* test_Try
    def test_Try(self):
        contents = r"""\
    try:
        print('a1')
        print('a2')
    except ImportError:
        print('b1')
        print('b2')
    except SyntaxError:
        print('c1')
        print('c2')
    finally:
        print('d1')
        print('d2')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.47: *5* test_TryExceptElse
    def test_Try2(self):
        # Line 240: leoDebugger.py
        contents = r"""\
    try:
        print('a')
    except ValueError:
        print('b')
    else:
        print('c')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.48: *5* test_With
    def test_With(self):
        # leoGlobals.py, line 1785.
        contents = r"""\
    with open(fn) as f:
        pass
    """
        self.make_data(contents)

    #@+node:ekr.20191227052446.49: *5* test_YieldFrom
    def test_YieldFrom(self):
        # Line 1046, leoAst.py
        contents = r"""\
    def gen_test():
        self.node = tree
        yield from self.gen_token('newline', '\n')
        print('done')
    """
        self.make_data(contents)
    #@+node:ekr.20191228193740.1: *4* test_aa && zz
    def test_aaa(self):
        """The first test."""
        g.total_time = get_time()
        
    def test_zzz(self):
        """The last test."""
        t2 = get_time()
        self.update_times('90: TOTAL', t2 - g.total_time)
        self.dump_stats()
    #@-others
#@+node:ekr.20191227152538.1: *3* class TestTOT (BaseTest)
class TestTOT (BaseTest):
    
    def test_traverse(self):
        
        contents = """\
f(1)
b = 2 + 3
"""
# print('%s = %s' % (2+3, 4*5))
        if 1:
            tokens, tree = self.make_file_data('leoApp.py')
        else:
            tokens, tree = self.make_data(contents)
        # dump_contents(contents)
        # dump_tokens(tokens)
        # dump_tree(tree)
        tot = TokenOrderTraverser()
        t1 = get_time()
        n_nodes = tot.traverse(tree)
        t2 = get_time()
        self.update_counts('nodes', n_nodes)
        self.update_times('50: TOT.traverse', t2 - t1)
        if 1:
            t1 = get_time()
            ng = TokenOrderNodeGenerator()
            ng.generate_nodes(tokens, tree)
            t2 = get_time()
            self.update_times('51: TONG.traverse', t2 - t1)
        self.dump_stats()
#@+node:ekr.20191227170628.1: ** TOG classes
#@+node:ekr.20191113063144.1: *3*  class TokenOrderGenerator
class TokenOrderGenerator:
    """A class that traverses ast (parse) trees in token order."""

    coverage_set = set()
        # The set of node.__class__.__name__ that have been visited.
    n_nodes = 0
        
    trace_mode = False

    #@+others
    #@+node:ekr.20191223052821.1: *4* tog: Passes
    # Called from testing framework.
    #@+node:ekr.20191113063144.6: *5* 0.1: tog.make_tokens
    def make_tokens(self, contents, trace_mode=False):
        """
        Return a list (not a generator) of Token objects corresponding to the
        list of 5-tuples generated by tokenize.tokenize.
        """
        import io
        import tokenize
        
        def check(contents, tokens):
            result = ''.join([z.to_string() for z in tokens])
            ok = result == contents
            if not ok:
                print('\nRound-trip check FAILS')
                print('Contents...\n')
                g.printObj(contents)
                print('\nResult...\n')
                g.printObj(result)
            return ok
        try:
            five_tuples = tokenize.tokenize(io.BytesIO(contents.encode('utf-8')).readline)
        except Exception:
            print('make_tokens: exception in tokenize.tokenize')
            g.es_exception()
            return None
        x = Tokenizer()
        x.trace_mode = trace_mode
        tokens = x.create_input_tokens(contents, five_tuples)
        assert check(contents, tokens)
        return tokens
    #@+node:ekr.20191229071141.1: *5* 0.2: tog.make_tree
    def make_tree(self, contents):
        """Pass 02: make the parse tree."""
        return parse_ast(contents)
    #@+node:ekr.20191228184647.1: *5* 0.3: tog.balance_tokens
    def balance_tokens(self, tokens):
        """
        TOG.balance_tokens.
        
        Find matching paren tokens.
        """
        count, stack = 0, []
        for token in tokens:
            if token.kind == 'op':
                if token.value == '(':
                    count += 1
                    stack.append(token.index)
                if token.value == ')':
                    if stack:
                        index = stack.pop()
                        tokens[index].matching_paren = token.index
                        tokens[token.index].matching_paren = index
                    else:
                        g.trace(f"unmatched ')' at index {token.index}")
        # g.trace(f"tokens: {len(tokens)} matched parens: {count}")
        if stack:
            g.trace("unmatched '(' at {','.join(stack)}")
        return count
    #@+node:ekr.20191113063144.4: *5* 1.1: tog.create_links
    def create_links(self, tokens, tree, file_name=''):
        """
        A generator creates two-way links between the given tokens and ast-tree.
        
        Callers should call this generator with list(tog.create_links(...))
        
        The sync_tokens method creates the links and verifies that the resulting
        tree traversal generates exactly the given tokens in exact order.
        
        tokens: the list of Token instances for the input.
                Created by self.make_tokens().
        tree:   the ast tree for the input.
                Created by the parse_ast() top-level function.
        """
        #
        # Init all ivars.
        self.file_name = file_name
            # For tests.
        self.level = 0
            # Python indentation level.
        self.node = None
            # The node being visited.
            # The parent of the about-to-be visited node.
        self.tokens = tokens
            # The immutable list of input tokens.
        self.tree = tree
            # The tree of ast.AST nodes.
        #
        # Traverse the tree.
        try:
            while True:
                next(self.visitor(tree))
        except StopIteration:
            pass
        #
        # Patch the last tokens.
        # Thise ensures that all tokens are patched.
        self.node = tree
        yield from self.gen_token('newline', '\n')
        yield from self.gen_token('endmarker', '')
    #@+node:ekr.20191229072907.1: *5* 1.2: tog.reassign_tokens
    def reassign_tokens(self, tokens, tree):
        """
        Reassign links between the given token list and ast-tree.
        """
        ReassignTokens().reassign(tokens, tree)
            
    #@+node:ekr.20191222082453.1: *5* 3.1: tog.fstringify
    def fstringify(self, tokens, tree, filename=''):
        """
        TOG.fstringify.
        
        Convert relevant % operators to fstrings.
        
        This method is a wrapper for unit tests.
        """
        # The Fstringify class does all the work.
        return Fstringify().fstringify(tokens, tree, filename)
    #@+node:ekr.20191223052749.1: *4* tog: Traversal
    #@+node:ekr.20191113063144.3: *5* tog.begin/end_visitor
    begin_end_stack = []
    node_index = 0  # The index into the node_stack.
    node_stack = []  # The stack of parent nodes.

    # These methods support generators.

    # Subclasses may/should override these methods.

    def begin_visitor(self, node):
        """TOG.begin_visitor: Enter a visitor."""
        if 0:
            g.trace(node.__class__.__name__)
            g.printObj([z.__class__.__name__ for z in self.node_stack])
        # Update the stats.
        self.coverage_set.add(node.__class__.__name__)
        self.n_nodes += 1
        # Inject the node_index field.
        assert not hasattr(node, 'node_index'), g.callers()
        node.node_index = self.node_index
        self.node_index += 1
        # begin_visitor and end_visitor must be paired.
        self.begin_end_stack.append(node.__class__.__name__)
        # Push the previous node.
        self.node_stack.append(self.node)
        # Update self.node *last*.
        self.node = node

    def end_visitor(self, node):
        """Leave a visitor."""
        if 0:
            g.trace(node.__class__.__name__)
        # begin_visitor and end_visitor must be paired.
        entry_name = self.begin_end_stack.pop()
        assert entry_name == node.__class__.__name__, (repr(entry_name), node.__class__.__name__)
        assert self.node == node, (repr(self.node), repr(node))
        # Restore self.node.
        self.node = self.node_stack.pop()
    #@+node:ekr.20191121180100.1: *5* tog.gen*
    # Useful wrappers.

    def gen(self, z):
        yield from self.visitor(z)
        
    def gen_name(self, val):
        yield from self.visitor(self.sync_name(val))
                    
    def gen_newline(self):
        yield from self.visitor(self.sync_token('newline', '\n'))

    def gen_op(self, val):
        yield from self.visitor(self.sync_op(val))
        
    def gen_token(self, kind, val):
        yield from self.visitor(self.sync_token(kind, val))
    #@+node:ekr.20191113063144.7: *5* tog.sync_token & set_links
    px = -1 # Index of the previous *significant* token.

    def sync_token(self, kind, val):
        """
        Handle a token whose kind & value are given.
        
        If the token is significant, do the following:
            
        1. Find the next significant token*after* px. Call it T.
        2. Verify that T matches the token described by (kind, val).
        3. Create two-way links between all assignable tokens between px and T.
        4. Create two-way links between T and self.node.
        5. Advance by updating self.px.
        """
        trace = False and self.trace_mode
        node, tokens = self.node, self.tokens
        assert isinstance(node, ast.AST), repr(node)
        if trace:
            # Don't add needless repr's!
            val_s = val if kind in ('name', 'string') else repr(val)
            if trace: g.trace(f"\n{self.node.__class__.__name__} {kind}.{val_s}")
        #
        # Leave all non-significant tokens for later.
        if not is_significant(kind, val):
            if trace: g.trace('\nENTRY: insignificant', self.px, kind, val)
            return
        #
        # Step one: Scan from *after* the previous significant token,
        #           looking for a token that matches (kind, val)
        #           Leave px pointing at the next significant token.
        #
        #           Special case: because of JoinedStr's, syncing a
        #           string may jump over *many* significant tokens.
        old_px = px = self.px + 1
        if trace: g.trace('\nEntry', px, kind, val)
        while px < len(self.tokens):
            token = tokens[px]
            if trace: g.trace('Token', px, token)
            if (kind, val) == (token.kind, token.value):
                if trace: g.trace('   OK', px, token)
                break  # Success.
            if kind == token.kind == 'number':
                if trace: g.trace('   OK', px, token)
                val = token.value
                break  # Benign: use the token's value, a string, instead of a number.
            if is_significant_token(token):
                # Unrecoverable sync failure.
                if 0:
                    pre_tokens = tokens[max(0, px-10):px+1]
                    g.trace('\nSync Failed...\n')
                    for s in [f"{i:>4}: {z!r}" for i, z in enumerate(pre_tokens)]:
                        print(s)
                line_s = f"line {token.line_number}:"
                val = g.truncate(val, 40)
                raise self.error(
                    f"{line_s:>12} {token.line.strip()}\n"
                    f"Looking for: {kind}.{val}\n"
                    f"      found: {token.kind}.{g.truncate(token.value, 80)}")
            # Skip the insignificant token.
            if trace: g.trace(' SKIP', px, token)
            px += 1
        else:
            # Unrecoverable sync failure.
            if 0:
                g.trace('\nSync failed...')
                g.printObj(tokens[max(0, px-5):], tag='Tokens')
            val = g.truncate(val, 40)
            raise self.error(
                 f"Looking for: {kind}.{val}\n"
                 f"      found: end of token list")
        #
        # Step two: Associate all previous assignable tokens to the ast node.
        while old_px < px:
            token = tokens[old_px]
            if trace: g.trace('Link insignificant', old_px, token)
            old_px += 1
            self.set_links(self.node, token)
        #
        # Step three: Set links in the significant token.
        token = tokens[px]
        if is_significant_token(token):
            self.set_links(node, token)
        else:
            if trace: g.trace('Skip insignificant', px, token, g.callers())
        #
        # Step four. Advance.
        if is_significant_token(token):
            self.px = px
    #@+node:ekr.20191125120814.1: *6* tog.set_links
    def set_links(self, node, token):
        """Make two-way links between token and the given node."""
        assert token.node is None, (repr(token), g.callers())
        trace = True and self.trace_mode
        if (
            is_significant_token(token)
            or token.kind in ('comment', 'newline')
        ):
            if trace:
                g.trace(
                    f"node: {node.__class__.__name__!s:16}"
                    f"token: {token.dump()}")
            #
            # Link the token to the ast node.
            token.node = node
            #
            # Add the token to node's token_list.
            token_list = getattr(node, 'token_list', [])
            node.token_list = token_list + [token]
    #@+node:ekr.20191124083124.1: *5* tog.sync_token helpers
    # It's valid for these to return None.

    def sync_blank(self):
        # self.sync_token('ws', ' ')
        return None

    # def sync_comma(self):
        # # self.sync_token('op', ',')
        # return None

    def sync_name(self, val):
        aList = val.split('.')
        if len(aList) == 1:
            self.sync_token('name', val)
        else:
            for i, part in enumerate(aList):
                self.sync_token('name', part)
                if i < len(aList) - 1:
                    self.sync_op('.')
                    
    def sync_newline(self):
        self.sync_token('newline', '\n')

    def sync_op(self, val):
        if val not in ',()':
            self.sync_token('op', val)
    #@+node:ekr.20191113081443.1: *5* tog.visitor (calls begin/end_visitor)
    def visitor(self, node):
        """Given an ast node, return a *generator* from its visitor."""
        # This saves a lot of tests.
        trace = False
        if node is None:
            return
        if trace:
            # Keep this trace. It's useful.
            cn = node.__class__.__name__ if node else ' '
            caller1, caller2 = g.callers(2).split(',')
            g.trace(f"{caller1:>15} {caller2:<14} {cn}")
        # More general, more convenient.
        if isinstance(node, (list, tuple)):
            for z in node or []:
                if isinstance(z, ast.AST):
                    yield from self.visitor(z)
                else:
                    # Some fields contain ints or strings.
                    assert isinstance(z, (int, str)), z.__class__.__name__
            return
        # We *do* want to crash if the visitor doesn't exist.
        method = getattr(self, 'do_' + node.__class__.__name__)
        # Allow begin/end visitor to be generators.
        val = self.begin_visitor(node)
        if isinstance(val, types.GeneratorType):
            yield from val
        # method(node) is a generator, not a recursive call!
        val = method(node)
        if isinstance(val, types.GeneratorType):
            yield from method(node)
        else:
            raise ValueError(f"Visitor is not a generator: {method!r}")
        val = self.end_visitor(node)
        if isinstance(val, types.GeneratorType):
            yield from val
    #@+node:ekr.20191223052953.1: *4* tog: Utils
    #@+node:ekr.20191129044716.1: *4* tog.error
    def error(self, message):
        """
        Prepend the caller to the message, print it, and return AssignLinksError.
        """
        caller = g.callers(4).split(',')[-1]
        header = f"AssignLinkError: caller: {caller}\n"
        if 0:
            print(f"\n{caller}: Error...\n")
            # Don't change the message. It may contain aligned lines.
            print(message)
        return AssignLinksError(header+message)
    #@+node:ekr.20191113063144.13: *4* tog: Visitors
    #@+node:ekr.20191113063144.14: *5* tog: Contexts
    #@+node:ekr.20191113063144.28: *6*  tog.arg
    # arg = (identifier arg, expr? annotation)

    def do_arg(self, node):
        
        """This is one argument of a list of ast.Function or ast.Lambda arguments."""

        yield from self.gen_name(node.arg)
        annotation = getattr(node, 'annotation', None)
        if annotation is not None:
            yield from self.gen(node.annotation)
    #@+node:ekr.20191113063144.27: *6*  tog.arguments
    #arguments = (
    #       arg* posonlyargs, arg* args, arg? vararg, arg* kwonlyargs,
    #       expr* kw_defaults, arg? kwarg, expr* defaults
    #   )

    def do_arguments(self, node):
        
        """Arguments to ast.Function or ast.Lambda, **not** ast.Call."""

        # No need to generate commas anywhere below.
        n_plain = len(node.args) - len(node.defaults)
        # Add the plain arguments.
        i = 0
        while i < n_plain:
            yield from self.gen(node.args[i])
            i += 1
        # Add the arguments with defaults.
        j = 0
        while i < len(node.args) and j < len(node.defaults):
            yield from (self.gen(node.args[i]))
            yield from self.gen_op('=')
            yield from self.gen(node.defaults[j])
            i += 1
            j += 1
        assert i == len(node.args)
        assert j == len(node.defaults)
        # Add the vararg and kwarg expressions.
        vararg = getattr(node, 'vararg', None)
        if vararg is not None:
            yield from self.gen_op('*')
            yield from self.gen(vararg)
        kwarg = getattr(node, 'kwarg', None)
        if kwarg is not None:
            yield from self.gen_op('**')
            yield from self.gen(kwarg)
    #@+node:ekr.20191113063144.15: *6* tog.AsyncFunctionDef
    # 2: AsyncFunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list)
    # 3: AsyncFunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list,
    #                expr? returns)

    def do_AsyncFunctionDef(self, node):
        
        if node.decorator_list:
            for z in node.decorator_list:
                # '@%s\n'
                yield from self.gen_op('@')
                yield from self.gen(z)
                yield from self.gen_newline()
        # 'asynch def (%s): -> %s\n'
        # 'asynch def %s(%s):\n'
        yield from self.gen_name('asynch')
        yield from self.gen_name(node.name) # A string
        yield from self.gen_op('(')
        yield from self.gen(node.args)
        yield from self.gen_op(')')
        yield from self.gen_op(':')
        returns = getattr(node, 'returns', None)
        if returns is not None:
            yield from self.gen_op('->')
            yield from self.gen(node.returns)
        yield from self.gen_newline()
        self.level += 1
        yield from self.gen(node.body)
        self.level -= 1
    #@+node:ekr.20191113063144.16: *6* tog.ClassDef
    def do_ClassDef(self, node, print_body=True):
        
        for z in node.decorator_list or []:
            # @{z}\n
            yield from self.gen_op('@')
            yield from self.gen(z)
            yield from self.gen_newline()
        # class name(bases):\n
        yield from self.gen_name('class')
        yield from self.gen_name(node.name) # A string.
        if node.bases:
            yield from self.gen_op('(')
            yield from self.gen(node.bases)
            yield from self.gen_op(')')
        yield from self.gen_op(':')
        yield from self.gen_newline()
        # Body...
        self.level += 1
        yield from self.gen(node.body)
        self.level -= 1
    #@+node:ekr.20191113063144.17: *6* tog.FunctionDef
    def do_FunctionDef(self, node):
        
        # Guards...
        returns = getattr(node, 'returns', None)
        # Decorators...
            # @{z}\n
        for z in node.decorator_list or []:
            yield from self.gen_op('@')
            yield from self.gen(z)
            yield from self.gen_newline()
        # Signature...
            # def name(args): returns\n
            # def name(args):\n
        yield from self.gen_name('def')
        yield from self.gen_name(node.name) # A string.
        yield from self.gen_op('(')
        yield from self.gen(node.args)
        yield from self.gen_op(')')
        yield from self.gen_op(':')
        if returns is not None:
            yield from self.gen_op('->')
            yield from self.gen(node.returns)
        yield from self.gen_newline()
        # Body...
        self.level += 1
        yield from self.gen(node.body)
        self.level -= 1
    #@+node:ekr.20191113063144.18: *6* tog.Interactive
    def do_Interactive(self, node):
        
        yield from self.gen(node.body)
    #@+node:ekr.20191113063144.20: *6* tog.Lambda
    def do_Lambda(self, node):

        yield from self.gen_name('lambda')
        yield from self.gen(node.args)
        yield from self.gen_op(':')
        yield from self.gen(node.body)
    #@+node:ekr.20191113063144.19: *6* tog.Module
    def do_Module(self, node):

        # Encoding is a non-syncing statement.
        yield from self.gen_token('encoding', '')
        yield from self.gen(node.body)
    #@+node:ekr.20191113063144.21: *5* tog: Expressions
    #@+node:ekr.20191113063144.22: *6* tog.Expr
    def do_Expr(self, node):
        """An outer expression."""
        # No need to put parentheses.
        yield from self.gen(node.value)
    #@+node:ekr.20191113063144.23: *6* tog.Expression
    def do_Expression(self, node):
        """An inner expression."""
        # No need to put parentheses.
        yield from self.gen(node.body)
    #@+node:ekr.20191113063144.24: *6* tog.GeneratorExp
    def do_GeneratorExp(self, node):

        # '<gen %s for %s>' % (elt, ','.join(gens))
        # No need to put parentheses or commas.
        yield from self.gen(node.elt)
        yield from self.gen_name('for')
        yield from self.gen(node.generators)
    #@+node:ekr.20191113063144.26: *5* tog: Operands
    #@+node:ekr.20191113063144.29: *6* tog.Attribute
    # Attribute(expr value, identifier attr, expr_context ctx)

    def do_Attribute(self, node):

        yield from self.gen(node.value)
        yield from self.gen_op('.')
        yield from self.gen_name(node.attr) # A string.
    #@+node:ekr.20191113063144.30: *6* tog.Bytes
    def do_Bytes(self, node):
        
        """
        It's invalid to mix bytes and non-bytes literals, so just
        advancing over the next 'string' token suffices.
        """
        token = self.advance_str()
        yield from self.gen_token('string', token.value)
    #@+node:ekr.20191113063144.31: *6* tog.Call & helpers
    # Call(expr func, expr* args, keyword* keywords)

    # Python 3 ast.Call nodes do not have 'starargs' or 'kwargs' fields.

    def do_Call(self, node):
        
        if False and self.trace_mode:
            #@+<< trace the ast.Call >>
            #@+node:ekr.20191204105344.1: *7* << trace the ast.Call >>
            dumper = AstDumper()

            def show_fields(node):
                class_name = 'None' if node is None else node.__class__.__name__
                return dumper.show_fields(class_name, node, 80)
                
            def dump(node):
                class_name = node.__class__.__name__
                if node is None:
                    class_name, fields = 'None', ''
                elif isinstance(node, (list, tuple)):
                    fields = ', '.join([show_fields(z) for z in node])
                else:
                    fields = show_fields(node)
                return f"{class_name:>12}: {fields}"
                
            print('\ndo_Call...\n\n'
                f"    func: {dump(node.func)}\n"
                f"    args: {dump(node.args)}\n"
                f"keywords: {dump(node.keywords)}\n")
            #@-<< trace the ast.Call >>
        yield from self.gen(node.func)
        yield from self.gen_op('(')
        # No need to generate any commas.
        yield from self.handle_call_arguments(node)
        yield from self.gen_op(')')
    #@+node:ekr.20191204114930.1: *7* tog.arg_helper
    def arg_helper(self, node):
        """
        Yield the node, with a special case for strings.
        """
        if 0:
            def show_fields(node):
                class_name = 'None' if node is None else node.__class__.__name__
                return AstDumper().show_fields(class_name, node, 40)
        
            g.trace(show_fields(node))

        if isinstance(node, str):
            yield from self.gen_token('name', node)
        else:
            yield from self.gen(node)
    #@+node:ekr.20191204105506.1: *7* tog.handle_call_arguments
    def handle_call_arguments(self, node):
        """
        Generate arguments in the correct order.
        
        See https://docs.python.org/3/reference/expressions.html#calls.
        
        This is similar to tog.do_arguments.
        
        At present, this code assumes the standard order:
        
        positional args, then keyword args, then * arg the ** kwargs.
        """
        trace = False
        #
        # Filter the * arg from args.
        args = [z for z in node.args or [] if not isinstance(z, ast.Starred)]
        star_arg = [z for z in node.args or [] if isinstance(z, ast.Starred)]
        #
        # Filter the ** kwarg arg from keywords.
        keywords = [z for z in node.keywords or [] if z.arg]
        kwarg_arg = [z for z in node.keywords or [] if not z.arg]
        if trace:
            #@+<< trace the ast.Call arguments >>
            #@+node:ekr.20191204113843.1: *8* << trace the ast.Call arguments >>
                
            def show_fields(node):
                class_name = 'None' if node is None else node.__class__.__name__
                return AstDumper().show_fields(class_name, node, 40)
                
            # Let block.
            arg_fields = ', '.join([show_fields(z) for z in args])
            keyword_fields = ', '.join([show_fields(z) for z in keywords])
            star_field = show_fields(star_arg[0]) if star_arg else 'None'
            kwarg_field = show_fields(kwarg_arg[0]) if kwarg_arg else 'None'
            # Print.
            print(
                f"\nhandle_call_args...\n\n"
                f"    args: {arg_fields!s}\n"
                f"keywords: {keyword_fields!s}\n"
                f"    star: {star_field!s}\n"
                f"   kwarg: {kwarg_field!s}")
            #@-<< trace the ast.Call arguments >>
            print('')
        #
        # Add the plain arguments.
        for z in args:
            yield from self.arg_helper(z)
        #
        # Add the keyword args.
        for z in keywords:
            yield from self.arg_helper(z.arg)
            yield from self.gen_op('=')
            yield from self.arg_helper(z.value)
        # Add the * arg.
        if star_arg:
            assert len(star_arg) == 1
            star = star_arg[0]
            assert isinstance(star, ast.Starred)
            yield from self.arg_helper(star)
        # Add the kwarg.
        if kwarg_arg:
            assert len(kwarg_arg) == 1
            kwarg = kwarg_arg[0]
            assert isinstance(kwarg, ast.keyword)
            yield from self.arg_helper(kwarg)
    #@+node:ekr.20191113063144.33: *6* tog.comprehension
    # comprehension = (expr target, expr iter, expr* ifs, int is_async)

    def do_comprehension(self, node):

        # No need to put parentheses.
        yield from self.gen(node.target) # A name
        yield from self.gen_name('in')
        yield from self.gen(node.iter)
        if node.ifs:
            self.advance_if()
            yield from self.gen_name('if')
            yield from self.gen(node.ifs)
    #@+node:ekr.20191113063144.34: *6* tog.Constant
    def do_Constant(self, node):
        
        g.trace(node.s)
        yield from self.gen_token('number', str(node.s))
    #@+node:ekr.20191113063144.35: *6* tog.Dict
    # Dict(expr* keys, expr* values)

    def do_Dict(self, node):

        assert len(node.keys) == len(node.values)
        yield from self.gen_op('{')
        # No need to put commas.
        for i, key in enumerate(node.keys):
            key, value = node.keys[i], node.values[i]
            yield from self.gen(key) # a Str node.
            yield from self.gen_op(':')
            if value is not None:
                try:
                    # Zero or more expressions.
                    for z in value:
                        yield from self.gen(z)
                except TypeError:
                    # Not an error.
                    yield from self.gen(value)
        yield from self.gen_op('}')
    #@+node:ekr.20191113063144.36: *6* tog.DictComp
    # DictComp(expr key, expr value, comprehension* generators)

    # d2 = {val: key for key, val in d.iteritems()}

    def do_DictComp(self, node):

        yield from self.gen_token('op', '{')
        yield from self.gen(node.key)
        yield from self.gen_op(':')
        yield from self.gen(node.value)
        yield from self.gen_name('for')
        yield from self.gen(node.generators)
        yield from self.gen_token('op', '}')
    #@+node:ekr.20191113063144.37: *6* tog.Ellipsis
    def do_Ellipsis(self, node):
        
        yield from self.gen_op('...')
    #@+node:ekr.20191113063144.38: *6* tog.ExtSlice
    def do_ExtSlice(self, node):
        
        # ':'.join(node.dims)
        for i, z in enumerate(node.dims):
            yield from self.gen(z)
            if i < len(node.dims) - 1:
                yield from self.gen_op(':')
    #@+node:ekr.20191113063144.40: *6* tog.Index
    def do_Index(self, node):

        yield from self.gen(node.value)
    #@+node:ekr.20191113063144.39: *6* tog.FormattedValue: not called!
    # FormattedValue(expr value, int? conversion, expr? format_spec)

    def do_FormattedValue(self, node):
        """
        This node represents the *components* of a *single* f-string.
        
        Happily, JoinedStr nodes *also* represent *all* f-strings,
        so the TOG should *never visit this node!
        """
        raise self.error(f"do_FormattedValue called from {g.callers()}")
        
        # pylint: disable=unreachable
       
        if 0: # This code has no chance of being useful.
            # Let block.
            conv = node.conversion
            spec = node.format_spec
            # Traverse all the subtrees
            yield from self.gen(node.value)
            if conv is not None:
                # The default conv appears to be -1.
                assert isinstance(conv, int), (repr(conv), g.callers())
                yield from self.gen_token('number', conv)
            if spec is not None:
                yield from self.gen(node.format_spec)
    #@+node:ekr.20191113063144.41: *6* tog.JoinedStr & helpers
    # JoinedStr(expr* values)

    def do_JoinedStr(self, node):
        """
        JoinedStr nodes represent at least one f-string and all other strings
        concatentated to it.
        
        Analyzing JoinedStr.values would be extremely tricky, for reasons that
        need not be explained here.
        
        Instead, we get the tokens *from the token list itself*!
        """
        for z in self.get_concatenated_string_tokens():
            self.advance_str()
            yield from self.gen_token(z.kind, z.value)
    #@+node:ekr.20191205053536.1: *7* tog.get_concatenated_tokens
    def get_concatenated_string_tokens(self):
        """
        Return the next 'string' token and all 'string' tokens concatentaed to
        it.
        
        Do *not* update self.string_index here.
        """
        trace = self.trace_mode
        i, results = self.string_index, []
        i = self.next_str_index(i + 1)
        while i < len(self.tokens):
            token = self.tokens[i]
            if token.kind == 'string':
                results.append(token)
            elif token.kind in ('endmarker', 'name', 'number', 'op'):
                # The 'endmarker' token ensures we will have a token.
                if not results:
                    raise self.error(
                        f"line {token.line_number} string_index: {i} "
                        f"expected 'string' token, got {token!s}")
                break
            else:
                pass # 'ws', 'nl', 'newline', 'comment', 'indent', 'dedent', etc.
            i += 1
        if i >= len(self.tokens):
            g.trace('token overrun', i)
            raise self.error(f"token overrun")
        if trace:
            g.trace('\nresults...')
            for z in results:
                print(f"  {z!s}")
            print('')
        return results
    #@+node:ekr.20191113063144.42: *6* tog.List
    def do_List(self, node):

        # No need to put commas.
        yield from self.gen_op('[')
        yield from self.gen(node.elts)
        yield from self.gen_op(']')
    #@+node:ekr.20191113063144.43: *6* tog.ListComp
    # ListComp(expr elt, comprehension* generators)

    def do_ListComp(self, node):
       
        yield from self.gen_op('[')
        yield from self.gen(node.elt)
        yield from self.gen_name('for')
        yield from self.gen(node.generators)
        yield from self.gen_op(']')
    #@+node:ekr.20191113063144.44: *6* tog.Name & NameConstant
    def do_Name(self, node):
        
        yield from self.gen_name(node.id)

    def do_NameConstant(self, node):

        yield from self.gen_name(repr(node.value))
    #@+node:ekr.20191113063144.45: *6* tog.Num
    def do_Num(self, node):
        
        yield from self.gen_token('number', node.n)
    #@+node:ekr.20191113063144.47: *6* tog.Set
    # Set(expr* elts)

    def do_Set(self, node):

        yield from self.gen(node.elts)
    #@+node:ekr.20191113063144.48: *6* tog.SetComp
    # SetComp(expr elt, comprehension* generators)

    def do_SetComp(self, node):

        yield from self.gen(node.elt)
        yield from self.gen_name('for')
        yield from self.gen(node.generators)
    #@+node:ekr.20191113063144.49: *6* tog.Slice
    def do_Slice(self, node):

        lower = getattr(node, 'lower', None)
        upper = getattr(node, 'upper', None)
        step = getattr(node, 'step', None)
        yield from self.gen(lower)
        yield from self.gen_op(':')
        yield from self.gen(upper)
        if step is not None:
            yield from self.gen_op(':')
            yield from self.gen(step)
    #@+node:ekr.20191113063144.50: *6* tog.Str & helpers
    def do_Str(self, node):
        """This node represents a string constant."""
        for z in self.get_concatenated_string_tokens():
            self.advance_str()
            yield from self.gen_token(z.kind, z.value)
    #@+node:ekr.20191126074503.1: *7* tog.advance_str
    # The index in self.tokens of the previously scanned 'string' token.
    string_index = -1 

    def advance_str(self):
        """
        Advance over exactly one 'string' token, and return it.
        """
        i = self.string_index
        i = self.next_str_index(i + 1)
        if i >= len(self.tokens):
            raise self.error(f"End of tokens")
        token = self.tokens[i]
        self.string_index = i
        return token
    #@+node:ekr.20191128135521.1: *7* tog.next_str_index
    def next_str_index(self, i):
        """Return the index of the next 'string' token, or None."""
        trace = False and self.trace_mode
        i1 = i
        while i < len(self.tokens):
            token = self.tokens[i]
            if token.kind == 'string':
                if trace:
                    g.trace(f"{i1:>2}-->{i:<2} {self.tokens[i]}")
                break
            i += 1
        return i
    #@+node:ekr.20191113063144.51: *6* tog.Subscript
    # Subscript(expr value, slice slice, expr_context ctx)

    def do_Subscript(self, node):
        
        yield from self.gen(node.value)
        yield from self.gen_op('[')
        yield from self.gen(node.slice)
        yield from self.gen_op(']')
    #@+node:ekr.20191113063144.52: *6* tog.Tuple
    # Tuple(expr* elts, expr_context ctx)

    def do_Tuple(self, node):

        # no need to put commas.
        # The parens are also optional, but they help a tiny bit.
        yield from self.gen_op('(')
        yield from self.gen(node.elts)
        yield from self.gen_op(')')
    #@+node:ekr.20191113063144.53: *5* tog: Operators
    #@+node:ekr.20191113063144.55: *6* tog.BinOp
    def do_BinOp(self, node):

        op_name_ = op_name(node.op)
        yield from self.gen(node.left)
        yield from self.gen_op(op_name_)
        yield from self.gen(node.right)
    #@+node:ekr.20191113063144.56: *6* tog.BoolOp
    # boolop = And | Or

    def do_BoolOp(self, node):
        
        # op.join(node.values)
        op_name_ = op_name(node.op)
        for i, z in enumerate(node.values):
            yield from self.gen(z)
            if i < len(node.values) - 1:
                yield from self.gen_name(op_name_)
    #@+node:ekr.20191113063144.57: *6* tog.Compare
    # Compare(expr left, cmpop* ops, expr* comparators)

    def do_Compare(self, node):
        
        assert len(node.ops) == len(node.comparators)
        yield from self.gen(node.left)
        for i, z in enumerate(node.ops):
            op_name_ = op_name(node.ops[i])
            if op_name_ in ('not in', 'is not'):
                for z in op_name_.split(' '):
                    yield from self.gen_name(z)
            elif op_name_.isalpha():
                yield from self.gen_name(op_name_)
            else:
                yield from self.gen_op(op_name_)
            yield from self.gen(node.comparators[i])
    #@+node:ekr.20191113063144.58: *6* tog.UnaryOp
    def do_UnaryOp(self, node):

        op_name_ = op_name(node.op)
        if op_name_.isalpha():
            yield from self.gen_name(op_name_)
        else:
            yield from self.gen_op(op_name_)
        yield from self.gen(node.operand)
    #@+node:ekr.20191113063144.59: *6* tog.IfExp (ternary operator)
    # IfExp(expr test, expr body, expr orelse)

    def do_IfExp(self, node):
        
        #'%s if %s else %s'
        yield from self.gen(node.body)
        self.advance_if()
        yield from self.gen_name('if')
        yield from self.gen(node.test)
        self.advance_if()
        yield from self.gen_name('else')
        yield from self.gen(node.orelse)
    #@+node:ekr.20191113063144.60: *5* tog: Statements
    #@+node:ekr.20191113063144.32: *6*  tog.keyword
    # keyword arguments supplied to call (NULL identifier for **kwargs)

    # keyword = (identifier? arg, expr value)

    def do_keyword(self, node):
        
        """A keyword arg in an ast.Call."""

        if node.arg:
            yield from self.gen_name(node.arg)
            yield from self.gen_op('=')
            yield from self.gen(node.value)
        else:
            yield from self.gen_op('**') 
            yield from self.gen(node.value)
    #@+node:ekr.20191113063144.83: *6*  tog.Starred
    # Starred(expr value, expr_context ctx)

    def do_Starred(self, node):
        
        """A starred argument to an ast.Call"""
        
        # g.trace(f"\n{node.value.__class__.__name__}")
        yield from self.gen_op('*')
        yield from self.gen(node.value)
    #@+node:ekr.20191113063144.61: *6* tog.AnnAssign
    # AnnAssign(expr target, expr annotation, expr? value, int simple)

    def do_AnnAssign(self, node):

        # {node.target}:{node.annotation}={node.value}\n'
        yield from self.gen(node.target)
        yield from self.gen_op(':')
        yield from self.gen(node.annotation)
        yield from self.gen_op('=')
        yield from self.gen(node.value)
        yield from self.gen_newline()
    #@+node:ekr.20191113063144.62: *6* tog.Assert
    # Assert(expr test, expr? msg)

    def do_Assert(self, node):
        
        # Guards...
        msg = getattr(node, 'msg', None)
        # No need to put parentheses or commas.
        yield from self.gen_name('assert')
        yield from self.gen(node.test)
        if msg is not None:
            yield from self.gen(node.msg)
        yield from self.gen_newline()
    #@+node:ekr.20191113063144.63: *6* tog.Assign
    def do_Assign(self, node):
            
        for z in node.targets:
            yield from self.gen(z)
            yield from self.gen_op('=')
        yield from self.gen(node.value)
        yield from self.gen_newline()
    #@+node:ekr.20191113063144.64: *6* tog.AsyncFor
    def do_AsyncFor(self, node):
        
        # The def line...
        # 'async for %s in %s:\n' % (
        yield from self.gen_name('async')
        yield from self.gen_name('for')
        yield from self.gen(node.target)
        yield from self.gen_op(':')
        yield from self.gen(node.iter)
        yield from self.gen_newline()
        # Body...
        self.level += 1
        yield from self.gen(node.body)
        # Else clause...
        if node.orelse:
            # 'else:\n'
            # Consume the 'else' if-item.
            self.advance_if()
            yield from self.gen_name('else')
            yield from self.gen_op(':')
            yield from self.gen(node.orelse)
        self.level -= 1
        yield from self.gen_newline()
    #@+node:ekr.20191113063144.65: *6* tog.AsyncWith
    def do_AsyncWith(self, node):
        
        yield from self.gen_name('async')
        yield from self.do_With(node)
    #@+node:ekr.20191113063144.66: *6* tog.AugAssign
    # AugAssign(expr target, operator op, expr value)

    def do_AugAssign(self, node):
        
        # %s%s=%s\n'
        op_name_ = op_name(node.op)
        yield from self.gen(node.target)
        yield from self.gen_op(op_name_+'=')
        yield from self.gen(node.value)
        yield from self.gen_newline()
    #@+node:ekr.20191113063144.67: *6* tog.Await
    # Await(expr value)

    def do_Await(self, node):
        
        #'await %s\n'
        yield from self.gen_name('await')
        yield from self.gen(node.value)
        yield from self.gen_newline()
    #@+node:ekr.20191113063144.68: *6* tog.Break
    def do_Break(self, node):
        
        yield from self.gen_name('break')
        yield from self.gen_newline()
    #@+node:ekr.20191113063144.69: *6* tog.Continue
    def do_Continue(self, node):

        yield from self.gen_name('continue')
        yield from self.gen_newline()
    #@+node:ekr.20191113063144.70: *6* tog.Delete
    def do_Delete(self, node):

        # No need to put commas.
        yield from self.gen_name('del')
        yield from self.gen(node.targets)
        yield from self.gen_newline()
    #@+node:ekr.20191113063144.71: *6* tog.ExceptHandler
    def do_ExceptHandler(self, node):
        
        # Except line...
        yield from self.gen_name('except')
        if getattr(node, 'type', None):
            yield from self.gen(node.type)
        if getattr(node, 'name', None):
            yield from self.gen_name('as')
            if isinstance(node.name, ast.AST):
                yield from self.gen(node.name)
            else:
                yield from self.gen_name(node.name)
        yield from self.gen_op(':')
        yield from self.gen_newline()
        # Body...
        self.level += 1
        yield from self.gen(node.body)
        self.level -= 1
    #@+node:ekr.20191113063144.73: *6* tog.For
    def do_For(self, node):

        #'for %s in %s:\n'
        yield from self.gen_name('for')
        yield from self.gen(node.target)
        yield from self.gen_name('in')
        yield from self.gen(node.iter)
        yield from self.gen_op(':')
        yield from self.gen_newline()
        # Body...
        self.level += 1
        yield from self.gen(node.body)
        # 'else:\n'
        if node.orelse:
            # Consume the 'else' if-item.
            self.advance_if()
            yield from self.gen_name('else')
            yield from self.gen_op(':')
            yield from self.gen(node.orelse)
        self.level -= 1
    #@+node:ekr.20191113063144.74: *6* tog.Global
    # Global(identifier* names)

    def do_Global(self, node):

        yield from self.gen_name('global')
        for z in node.names:
            yield from self.gen_name(z)
        yield from self.gen_newline()
    #@+node:ekr.20191113063144.75: *6* tog.If & helpers
    # If(expr test, stmt* body, stmt* orelse)

    def do_If(self, node):
        #@+<< do_If docstring >>
        #@+node:ekr.20191122222412.1: *7* << do_If docstring >>
        """
        The parse trees for the following are identical!

          if 1:            if 1:
              pass             pass
          else:            elif 2:
              if 2:            pass
                  pass
                  
        So there is *no* way for the 'if' visitor to disambiguate the above two
        cases from the parse tree alone.

        Instead, we scan the tokens list for the next 'if', 'else' or 'elif' token.
        """
        #@-<< do_If docstring >>
        #
        # Consume the if-item.
        token = self.advance_if()
        #
        # This sanity check is important. It has failed in the past.
        if token.value not in ('if', 'elif'):
            raise self.error(
                f"line {token.line_number}: "
                f"expected 'if' or 'elif' (name) token, got '{token!s}")
        #
        # If or elif line...
            # if %s:\n
            # elif %s: \n
        yield from self.gen_name(token.value)
        yield from self.gen(node.test)
        yield from self.gen_op(':')
        yield from self.gen_newline()
        #
        # Body...
        self.level += 1
        yield from self.gen(node.body)
        self.level -= 1
        #
        # Else and elif clauses...
        if node.orelse:
            self.level += 1
            val = self.peek_if().value
            if val == 'else':
                # Consume the 'else' if-item.
                self.advance_if()
                yield from self.gen_name('else')
                yield from self.gen_op(':')
                yield from self.gen_newline()
                yield from self.gen(node.orelse)
            else:
                # Do *not* consume an if-item here.
                yield from self.gen(node.orelse)
            self.level -= 1
    #@+node:ekr.20191123152511.1: *7* tog.advance_if
    if_index = -1

    def is_if_token(self, token):
        return token.kind == 'name' and token.value in ('if', 'elif', 'else')
        
    def advance_if(self):
        """
        Set token to the the *present* if-related token,
        initiing .if_index if necessary.
        
        Advance .if_index to the *next* if-related token, if any.
        
        Return the token.
        """
        trace = False # An excellent trace
        #
        # Don't even *think* of omitting this check.
        # Doing so would create time bombs.
        i = self.if_index
        if i == -1:
            i = self.find_next_if_token(i)
        #
        # Set token to the *present* if-related token.
        token = self.tokens[i] if i < len(self.tokens) else None
        if trace:
            line = token.line_number if token else ' '
            token_s = token or 'No more tokens'
            g.trace(f"line {line:>4} next i: {i:>5} {token_s!s:<12} {g.callers(1)}")
        #
        # Advance to the *next* if-related token.
        i = self.find_next_if_token(i + 1)
        self.if_index = i
        return token
    #@+node:ekr.20191204014042.1: *7* tog.find_next_if_token
    def find_next_if_token(self, i):
        """Advance i to the if-related token *after* self.tokens[i]."""
        while i < len(self.tokens):
            if self.is_if_token(self.tokens[i]):
                # g.trace(f" {i:>3} {self.tokens[i]}")
                break
            i += 1
        return i
    #@+node:ekr.20191204012319.1: *7* tog.peek_if
    def peek_if(self):
        """Return the current if-related token."""
        # Init, if necessary.
        if self.if_index == -1:
            self.if_index = self.find_next_if_token(0)
        # IndexError is a sanity check.
        assert self.if_index < len(self.tokens)
        return self.tokens[self.if_index]
    #@+node:ekr.20191113063144.76: *6* tog.Import & helper
    def do_Import(self, node):
        
        yield from self.gen_name('import')
        for alias in node.names:
            yield from self.gen_name(alias.name)
            if alias.asname:
                yield from self.gen_name('as')
                yield from self.gen_name(alias.asname)
        yield from self.gen_newline()
    #@+node:ekr.20191113063144.77: *6* tog.ImportFrom
    def do_ImportFrom(self, node):

        yield from self.gen_name('from')
        yield from self.gen_name(node.module)
        yield from self.gen_name('import')
        # No need to put commas.
        for alias in node.names:
            yield from self.gen_name(alias.name)
            if alias.asname:
                yield from self.gen_name('as')
                yield from self.gen_name(alias.asname)
        yield from self.gen_newline()
    #@+node:ekr.20191113063144.78: *6* tog.Nonlocal
    # Nonlocal(identifier* names)

    def do_Nonlocal(self, node):
        
        # nonlocal %s\n' % ','.join(node.names))
        # No need to put commas.
        yield from self.gen_name('nonlocal')
        yield from self.gen(node.names)
        yield from self.gen_newline()
    #@+node:ekr.20191113063144.79: *6* tog.Pass
    def do_Pass(self, node):
        
        yield from self.gen_name('pass')
        yield from self.gen_newline()
    #@+node:ekr.20191113063144.81: *6* tog.Raise
    # Raise(expr? exc, expr? cause)

    def do_Raise(self, node):
       
        # No need to put commas.
        yield from self.gen_name('raise')
        exc = getattr(node, 'exc', None)
        cause = getattr(node, 'cause', None)
        tback = getattr(node, 'tback', None)
        yield from self.gen(exc)
        yield from self.gen(cause)
        yield from self.gen(tback)
        yield from self.gen_newline()
    #@+node:ekr.20191113063144.82: *6* tog.Return
    def do_Return(self, node):
        
        yield from self.gen_name('return')
        yield from self.gen(node.value)
        yield from self.gen_newline()
    #@+node:ekr.20191113063144.85: *6* tog.Try
    # Try(stmt* body, excepthandler* handlers, stmt* orelse, stmt* finalbody)

    def do_Try(self, node):

        # Try line...
        yield from self.gen_name('try')
        yield from self.gen_op(':')
        yield from self.gen_newline()
        # Body...
        self.level += 1
        yield from self.gen(node.body)
        yield from self.gen(node.handlers)
        if node.orelse:
            self.advance_if()
            yield from self.gen_name('else')
            yield from self.gen_op(':')
            yield from self.gen(node.orelse)
        # Finally...
        if node.finalbody:
            yield from self.gen_name('finally')
            yield from self.gen_op(':')
            yield from self.gen_newline()
            yield from self.gen(node.finalbody)
        self.level -= 1
    #@+node:ekr.20191113063144.88: *6* tog.While
    def do_While(self, node):
        
        # While line...
            # while %s:\n'
        yield from self.gen_name('while')
        yield from self.gen(node.test)
        yield from self.gen_op(':')
        yield from self.gen_newline()
        # Body...
        self.level += 1
        yield from self.gen(node.body)
        # Else clause...
        if node.orelse:
            # Consume the 'else' if-item.
            self.advance_if()
            yield from self.gen_name('else')
            yield from self.gen_op(':')
            yield from self.gen_newline()
            yield from self.gen(node.orelse)
        self.level -= 1
    #@+node:ekr.20191113063144.89: *6* tog.With
    # With(withitem* items, stmt* body)

    # withitem = (expr context_expr, expr? optional_vars)

    def do_With(self, node):
        
        expr = getattr(node, 'context_expression', None)
        items = getattr(node, 'items', [])
        yield from self.gen_name('with')
        yield from self.gen(expr)
        # No need to put commas.
        for item in items:
            yield from self.gen(item.context_expr)
            optional_vars = getattr(item, 'optional_vars', None)
            if optional_vars is not None:
                yield from self.gen_name('as')
                try:
                    for z in item.optional_vars:
                        yield from self.gen(z)
                except TypeError:  # Not iterable.
                    yield from self.gen(item.optional_vars)
        # End the line.
        yield from self.gen_op(':')
        yield from self.gen_newline()
        # Body...
        self.level += 1
        yield from self.gen(node.body)
        self.level -= 1
    #@+node:ekr.20191113063144.90: *6* tog.Yield
    def do_Yield(self, node):

        yield from self.gen_name('yield')
        if hasattr(node, 'value'):
            yield from self.gen(node.value)
        yield from self.gen_newline()
    #@+node:ekr.20191113063144.91: *6* tog.YieldFrom
    # YieldFrom(expr value)

    def do_YieldFrom(self, node):

        yield from self.gen_name('yield')
        yield from self.gen_name('from')
        yield from self.gen(node.value)
        yield from self.gen_newline()
    #@-others
#@+node:ekr.20191226195813.1: *3*  class TokenOrderTraverser
class TokenOrderTraverser:
    """
    Traverse an ast tree using the parent/child links created by the
    TokenOrderInjector class.
    """
    #@+others
    #@+node:ekr.20191226200154.1: *4* TOT.traverse
    def traverse(self, tree):
        """
        Call visit, in token order, for all nodes in tree.
        
        Recursion is not allowed.
        
        The code follows p.moveToThreadNext exactly.
        """
        
        def has_next(i, node, stack):
            """Return True if stack[i] is a valid child of node.parent."""
            # g.trace(node.__class__.__name__, stack)
            parent = node.parent
            return parent and parent.children and i < len(parent.children)
            
        # Update stats
        self.last_node_index = -1  # For visit
        # The stack contains child indices.
        node, stack = tree, [0]
        seen = set()
        while node and stack:
            if False: g.trace(
                f"{node.node_index:>3} "
                f"{node.__class__.__name__:<12} {stack}")
            # Visit the node.
            assert node.node_index not in seen, node.node_index
            seen.add(node.node_index)
            self.visit(node)
            # if p.v.children: p.moveToFirstChild()
            children = getattr(node, 'children', [])
            if children:
                # Move to the first child.
                stack.append(0)
                node = children[0]
                # g.trace(' child:', node.__class__.__name__, stack)
                continue
            # elif p.hasNext(): p.moveToNext()
            stack[-1] += 1
            i = stack[-1]
            if has_next(i, node, stack):
                node = node.parent.children[i]
                continue
            # else...
            # p.moveToParent()
            node = node.parent
            stack.pop()
            # while p:
            while node and stack:
                # if p.hasNext():
                stack[-1] += 1
                i = stack[-1]
                if has_next(i, node, stack):
                    # Move to the next sibling.
                    node = node.parent.children[i]
                    break  # Found.
                # p.moveToParent()
                node = node.parent
                stack.pop()
                # g.trace('parent:', node.__class__.__name__, stack)
            # not found.
            else:
                break
        # g.trace('done', node and node.__class__.__name__, stack)
        return self.last_node_index
    #@+node:ekr.20191227160547.1: *4* TOT.visit
    def visit(self, node):

        self.last_node_index += 1
        assert self.last_node_index == node.node_index, (
            self.last_node_index, node.node_index)
    #@-others
#@+node:ekr.20191222083453.1: *3* class Fstringify (TOT)
class Fstringify (TokenOrderTraverser):
    """A class to fstringify an existing ast tree."""
    #@+others
    #@+node:ekr.20191222083947.1: *4* fs.fstringify (entry)
    def fstringify(self, tokens, tree, filename=''):
        """
        Fstringify.fstringify:
            
        The entry point for the Fstringify class.

        All links should already been created.
        """
        self.filename = filename
        self.tokens = tokens
        self.tree = tree
        self.traverse(self.tree)
        return ''.join(z.to_string() for z in self.tokens)
    #@+node:ekr.20191231055008.1: *4* fs.visit (override)
    def visit(self, node):
        """
        FStringify.visit. (Overrides TOT visit).
        
        Handle binary ops, including possible f-strings.
        """
        if (
            isinstance(node, ast.BinOp)
            and op_name(node.op) == '%'
            and isinstance(node.left, ast.Str)
        ):
            self.make_fstring(node)
    #@+node:ekr.20191222095754.1: *4* fs.make_fstring (top level) & helpers
    def make_fstring(self, node):
        """
        node is BinOp node for the '%' operator.
        node.left is an ast.Str node.
        node.right should be an ast.Tuple or an ast.Str.

        Convert this tree to an f-string, if possible,
        replacing node's entire tree with a new ast.Str node.
        """
        assert isinstance(node.left, ast.Str), (repr(node.left), g.callers())
        # Careful: use the tokens, not Str.s.  This preserves spelling.
        lt_s = ''.join(z.to_string() for z in node.left.token_list)
        # Get the RHS values, a list of token lists.
        values = self.scan_rhs(node.right)
        if not values:
            return
        # Compute rt_s, line and line_number for later.
        token0 = node.left.token_list[0]
        line_number = token0.line_number
        line = token0.line.strip()
        tokens = []
        for aList in values:
            tokens.append(''.join(z.to_string() for z in aList))
        rt_s = ''.join(tokens)
        # Get the % specs in the LHS string.
        specs = self.scan_format_string(lt_s)
        if len(values) != len(specs):
            token_list = getattr(node.left, 'token_list', None)
            token = token_list and token_list[0]
            line_number = getattr(token, 'line_number', '<unknown>')
            line = getattr(token, 'line', '<unknown>')
            n_specs, n_values = len(specs), len(values)
            print(
                f"\n"
                f"f-string mismatch: "
                f"{n_values} value{g.plural(n_values)}, "
                f"{n_specs} spec{g.plural(n_specs)}\n"
                f"      line number: {line_number}\n"
                f"             line: {line.strip()!r}")
            if 0:
                specs_s = ', '.join(m.group(0) for m in specs)
                values_s = ', '.join(','.join(f"[{z2.kind}: {z2.value}]"
                    for z2 in z) for z in values)
                print(f"specs: {specs_s!r} values: {values_s}")
            return
        # Replace specs with values.
        results = self.substitute_values(lt_s, specs, values)
        result = self.compute_result(lt_s, results)
        if not result:
            return
        # Remove whitespace before ! and :.
        result = self.clean_ws(result)
        # Show the results
        print(
            f"\n"
            f"line number: {line_number}\n"
            f"       line: {line!r}\n"
            f"       from: {lt_s} % {rt_s}\n"
            f"         to: {result}")
        # Adjust the tree and the token list.
        self.replace(node, result, values)
    #@+node:ekr.20191222102831.3: *5* fs.clean_ws
    ws_pat = re.compile(r'(\s+)([:!][0-9]\})')

    def clean_ws(self, s):
        """Carefully remove whitespace before ! and : specifiers."""
        s = re.sub(self.ws_pat, r'\2', s)
        return s

    #@+node:ekr.20191222102831.4: *5* fs.compute_result & helpers
    def compute_result(self, string_val, tokens):
        """
        Create the final result, with various kinds of munges.

        Return the result string, or None if there are errors.
        """
        # Fail if there is a backslash within { and }.
        if not self.check_newlines(tokens):
            return None
        # Ensure consistent quotes.
        if not self.change_quotes(string_val, tokens):
            print(f"string contains backslashes: {string_val!r}")
            return None
        return ''.join([z.to_string() for z in tokens])
    #@+node:ekr.20191222102831.2: *6* fs.check_newlines
    def check_newlines(self, tokens):
        """
        Check to ensure that no newlines appear within { and }.
        
        Return False if there is an error
        """
        level = 0
        for token in tokens:
            kind, val = token.kind, token.value
            if kind == 'op':
                if val == '{':
                    level += 1
                elif val == '}':
                    level -= 1
                    if level < 0:
                        print('curly bracket underflow')
                        return False
            if '\\n' in val and level > 0:
                print('f-expression would contain a backslash')
                return False
        if level > 0:
            print('unclosed curly bracket')
            return False
        return True
    #@+node:ekr.20191222102831.7: *6* fs.change_quotes
    def change_quotes(self, string_val, aList):
        """
        Carefully change quotes in all "inner" tokens as necessary.
        
        Return True if all went well.
        
        We expect the following "outer" tokens.
            
        aList[0]:  ('fstringify', 'f')
        aList[1]:  ('fstringify', a string starting with a quote)
        aList[-1]: ('fstringify', a string ending with a quote that matches aList[1])
        """
        # Sanity checks.
        if len(aList) < 4:
            return True
        if not string_val:
            g.trace('no string_val!')
            return False
        delim = string_val[0]
        # Check tokens 0, 1 and -1.
        token0 = aList[0]
        token1 = aList[1]
        token_last = aList[-1]
        for token in token0, token1, token_last:
            # These are the only kinds of tokens we expect to generate.
            ok = (
                token.kind == 'string' or
                token.kind == 'op' and token.value in '{}')
            if not ok:
                g.trace(
                    f"unexpected token: {token.kind} {token.value}\n"
                    f"string_val: {string_val!r}\n"
                    f"line: {token0.line!r}")
                g.printObj(aList, tag = 'aList')
                return False
        # These checks are important...
        if token0.value != 'f':
            g.trace('token[0]  error:', repr(token0))
            return False
        val1 = token1.value and token1.value[0]
        if delim != val1:
            g.trace('token[1]  error:', delim, val1, repr(token1))
            g.printObj(aList, tag = 'aList')
            return False
        val_last = token_last.value and token_last.value[-1]
        if delim != val_last:
            g.trace('token[-1] error:', delim, val_last, repr(token_last))
            g.printObj(aList, tag = 'aList')
            return False
        # Regularize the outer tokens.
        delim, delim2 = '"', "'"
        token1.value = delim + token1.value[1:]
        aList[1] = token1
        token_last.value = token_last.value[:-1] + delim
        aList[-1] = token_last
        # Replace delim by delim2 in all inner tokens.
        for z in aList[2:-1]:
            if not isinstance(z, Token):
                g.trace('Bad token:', repr(z))
                return False
            z.value = z.value.replace(delim, delim2)
        return True
    #@+node:ekr.20191222102831.6: *5* fs.munge_spec
    def munge_spec(self, spec):
        """
        Return (head, tail).
        
        The format is spec !head:tail or :tail
        
        Example specs: s2, r3
        """
        ### To do: handle more specs.
        head, tail = [], []
        if spec.startswith('+'):
            pass # Leave it alone!
        elif spec.startswith('-'):
            tail.append('>')
            spec = spec[1:]
        if spec.endswith('s'):
            spec = spec[:-1]
        if spec.endswith('r'):
            head.append('r')
            spec = spec[:-1]
        tail = ''.join(tail) + spec
        head = ''.join(head)
        return head, tail
    #@+node:ekr.20191225054848.1: *5* fs.replace
    def replace(self, node, s, values):
        """
        Replace node with an ast.Str node for s.
        Replace all tokens in the range of values with a single 'string' node.
        """
        # Replace the tokens...
        i, j = NodeTokens().token_range(node)
        i1 = i
        tokens = self.tokens[i:j+1]
        tokens = match_parens(tokens) ### Hack.
        ### replace_token(i, 'string', s)
        replace_token(self.tokens[i], 'string', s)
        j = 1
        while j < len(tokens):
            ### replace_token(i1 + j, 'killed', '')
            replace_token(self.tokens[i1 + j], 'killed', '')
            j += 1
        # Replace the node.
        new_node = ast.Str()
        new_node.s = s
        replace_node(new_node, node)
        # Update the token.
        token = self.tokens[i1]
        token.node = new_node
        # Update the token list.
        new_node.token_list = [token]
    #@+node:ekr.20191222102831.9: *5* fs.scan_format_string
    # format_spec ::=  [[fill]align][sign][#][0][width][,][.precision][type]
    # fill        ::=  <any character>
    # align       ::=  "<" | ">" | "=" | "^"
    # sign        ::=  "+" | "-" | " "
    # width       ::=  integer
    # precision   ::=  integer
    # type        ::=  "b" | "c" | "d" | "e" | "E" | "f" | "F" | "g" | "G" | "n" | "o" | "s" | "x" | "X" | "%"

    format_pat = re.compile(r'%(([+-]?[0-9]*(\.)?[0.9]*)*[bcdeEfFgGnoxrsX]?)')

    def scan_format_string(self, s):
        """Scan the format string s, returning a list match objects."""
        result = list(re.finditer(self.format_pat, s))
        return result
    #@+node:ekr.20191222104224.1: *5* fs.scan_rhs
    def scan_rhs(self, node):
        """
        Scan the right-hand side of a potential f-string.
        
        Return a list of the token lists for each element.
        """
        trace = False
        # First, Try the most common cases.
        if isinstance(node, ast.Str):
            return [node.token_list]
        if isinstance(node, (list, tuple, ast.Tuple)):
            result = []
            if isinstance(node, ast.Tuple):
                elts = node.elts
            else:
                elts = node
            for elt in elts:
                if hasattr(elt, 'token_list'):
                    tokens = tokens_for_node(elt, self.tokens)
                    result.append(tokens)
                elif trace:
                    g.trace(f"No token list for {elt.__class__.__name__}")
            if len(node.elts) != len(result):
                if trace:
                    g.trace('list mismatch')
                    dump_tree_and_links(node)
                return []
            return result
        #
        # Now we expect only one result. 
        tokens = tokens_for_node(node, self.tokens)
        if trace and not tokens:
            g.trace('===== no token list', node.__class__.__name__)
            dump_tree_and_links(node)
        return [tokens]
    #@+node:ekr.20191226155316.1: *5* fs.substitute_values
    def substitute_values(self, lt_s, specs, values):
        """Replace specifieriers with values in lt_s string."""
        i, results = 0, [Token('string', 'f')]
        for spec_i, m in enumerate(specs):
            value = ''.join(z.to_string() for z in values[spec_i])
            # g.trace('item', spec_i, 'value', repr(value))
            start, end, spec = m.start(0), m.end(0), m.group(1)
            if start > i:
                results.append(Token('string', lt_s[i : start]))
            head, tail = self.munge_spec(spec)
            results.append(Token('op', '{'))
            results.append(Token('string', value))
            if head:
                results.append(Token('string', '!'))
                results.append(Token('string', head))
            if tail:
                results.append(Token('string', ':'))
                results.append(Token('string', tail))
            results.append(Token('op', '}'))
            i = end
        # Add the tail.
        tail = lt_s[i:]
        if tail:
            results.append(Token('string', tail))
        return results
    #@-others
#@+node:ekr.20191225072008.1: *3* class NodeTokens
class NodeTokens:
    """
    A class returning a range of tokens for a single ast node.
    """
    #@+others
    #@+node:ekr.20191225111222.1: *4* token_range
    def token_range(self, node):
        self.i, self.j = None, None
        list(self.token_range_helper(node))
        return self.i, self.j
        
    #@+node:ekr.20191225111141.1: *4* token_range_helper
    def token_range_helper(self, node):
        if isinstance(node, (list, tuple)):
            for z in node:
                yield from self.token_range_helper(z)
        elif hasattr(node, '_fields'):
            self.update_range(node)
            for field in node._fields:
                node2 = getattr(node, field)
                self.update_range(node2)
                yield from self.token_range_helper(node2)
    #@+node:ekr.20191225125633.1: *4* update_range
    def update_range(self, node):
        token_list = getattr(node, 'token_list', None)
        if not token_list:
            return
        if self.i is None:
            self.i = token_list[0].index
        else:
            self.i = min(self.i, token_list[0].index)
        if self.j is None:
            self.j = token_list[-1].index
        else:
            self.j = max(self.j, token_list[-1].index)
        if 0:
            g.trace(
                f"{node.__class__.__name__:>15}, "
                f"{self.i:>2} {self.j:>2}")
    #@-others
#@+node:ekr.20191231084514.1: *3* class ReassignTokens (TOT)
class ReassignTokens (TokenOrderTraverser):
    
    """A class that reassigns tokens to more appropriate ast nodes."""
    
    #@+others
    #@+node:ekr.20191231084640.1: *4* reassign.reassign
    def reassign(self, tokens, tree):
        """The main entry point."""
        self.tokens = tokens
        self.tree = tree
        # self.pass_n = 1
        self.traverse(tree)
    #@+node:ekr.20191231084853.1: *4* reassign.visit
    def visit(self, node):
        """ReassignTokens.visit"""
        # For now, just handle call nodes.
        if not isinstance(node, ast.Call):
            return
        if 0:
            g.trace(node.node_index,
                node.__class__.__name__, node.args.__class__.__name__)
            g.trace([str(z) for z in tokens_for_node(node, self.tokens)])
        # First, handle ast.Call nodes.

            # last_sig_token = None
            # for token in tokens:
                # if is_significant_token(token):
                    # assert token.node, repr(token)
                    # last_sig_token = token
                # elif token.kind == 'op' and token.value in '()':
                    # token.node = last_sig_token.node
    #@-others
#@+node:ekr.20191111152653.1: *3* class TokenOrderFormatter
class TokenOrderFormatter (TokenOrderGenerator):
    
    def format(self, contents):
        """
        Format the tree into a string guaranteed to be generated in token order.
        """
        tokens = self.make_tokens(contents)
        tree = parse_ast(contents)
        ### To do...
        self.create_links(tokens, tree)
        return ''.join([z.to_string() for z in self.tokens])
#@+node:ekr.20191113054314.1: *3* class TokenOrderInjector (TOG)
class TokenOrderInjector (TokenOrderGenerator):
    """
    A class that injects data into tokens and ast nodes.
    """
    #@+others
    #@+node:ekr.20191113054550.1: *4* toi.begin_visitor
    def begin_visitor(self, node):
        """
        TokenOrderInjector.begin_visitor.
        
        Enter a visitor, inject data into the ast node, and update stats.
        """
        #
        # Do this first, *before* updating self.node.
        self.coverage_set.add(node.__class__.__name__)
        node.parent = self.node
        if self.node:
            children = getattr(self.node, 'children', [])
            children.append(node)
            self.node.children = children
        #
        # *Now* update self.node, etc.
        super().begin_visitor(node)
    #@+node:ekr.20191229071517.1: *4* toi: Entries
    #@+node:ekr.20191229071733.1: *5* tog.create_links_in_file
    def create_links_in_file(self, filename):
        """
        Create the tokens and ast tree for the given file.
        
        Return (tokens, tree).
        """
        try:
            with open(filename, 'r') as f:
                s = f.read()
        except Exception as e:
            g.trace(f"can not open {filename}...\n{e}")
        tokens, tree = self.create_links_in_string(s, filename=filename)
        return tokens, tree
        
    #@+node:ekr.20191229071746.1: *5* tog.create_links_in_string
    def create_links_in_string(self, s, filename=''):
        """
        Tokenize, parse and create links in the string s.
        
        Return (tokens, tree).
        """
        self.filename = filename
        tokens = self.make_tokens(s)
        tree = self.make_tree(s)
        list(self.create_links(tokens, tree))
        self.balance_tokens(tokens)
        return tokens, tree
    #@+node:ekr.20191229071619.1: *5* tog.fstringify_file
    def fstringify_file(self, filename):
        """Fstringify the given file."""
        try:
            with open(filename, 'r') as f:
                s = f.read()
        except Exception as e:
            g.trace(f"can not open {filename}\n{e}")
        result_s = self.fstringify_string(s)
        if not result_s:
            g.trace(f"did not fstringify {filename}")
            return
        if s == result_s:
            g.trace(f"no change: {filename}")
            return
        try:
            with open(filename, 'w') as f:
                f.write(result_s)
        except Exception as e:
            g.trace(f"can not write {filename}\n{e}")
    #@+node:ekr.20191229071718.1: *5* tog.fstringify_string
    def fstringify_string(self, s, filename=''):
        """Return the results of fstingifing string s."""
        tokens = self.make_tokens(s)  # Pass 0.1
        tree = self.make_tree(s)      # Pass 0.2
        self.balance_tokens(tokens)   # Pass 0.3
        list(self.create_links(tokens, tree))  # Pass 1.1
        self.reassign_tokens(tokens, tree)     # Pass 2.1.
        result_s = self.fstringify(tokens, tree)  # Pass 3.1
        return result_s
    #@+node:ekr.20191113063144.11: *5* tog.report_coverage
    def report_coverage(self):
        """Report untested visitors."""

        def key(z):
            return z.lower()

        covered = sorted(list(self.coverage_set), key=key)
        visitors = [z[3:] for z in dir(self) if z.startswith('do_')]
        missing = sorted([z for z in visitors if z not in covered], key=key)
        #
        # These are not likely ever to be covered.
        not_covered = ['Interactive', 'Expression', 'FormattedValue']
        for z in missing:
            if z in not_covered:
                missing.remove(z)
        if 0:
            print('Covered...\n')
            g.printObj(covered)
        if missing:
            print('Missing...\n')
            g.printObj(missing)
        else:
            print('All visitors covered')
        print('')
    #@-others
#@+node:ekr.20191121122230.1: *3* class TokenOrderNodeGenerator (TOG)
class TokenOrderNodeGenerator(TokenOrderGenerator):
    """A class that yields a stream of nodes."""

    # Other overrides...
    def sync_token(self, kind, val):
        pass
        
    #@+others
    #@+node:ekr.20191228153344.1: *4* tong.generate_nodes
    def generate_nodes(self, tokens, tree, file_name=''):
        """Entry: yield a stream of nodes."""
        #
        # Init all ivars.
        self.file_name = file_name
            # For tests.
        self.level = 0
            # Python indentation level.
        self.node = None
            # The node being visited.
            # The parent of the about-to-be visited node.
        self.tokens = tokens
            # The immutable list of input tokens.
        self.tree = tree
            # The tree of ast.AST nodes.
        #
        # Traverse the tree.
        try:
            while True:
                next(self.visitor(tree))
        except StopIteration:
            pass
    #@+node:ekr.20191228152949.1: *4* tong.begin/end_visitor
    def begin_visitor(self, node):
        """TONG.begin_visitor: Enter a visitor."""
        # begin_visitor and end_visitor must be paired.
        self.begin_end_stack.append(node.__class__.__name__)
        # Push the previous node.
        self.node_stack.append(self.node)
        # Update self.node *last*.
        self.node = node

    def end_visitor(self, node):
        """TONG.end_visitor: Leave a visitor."""
        # begin_visitor and end_visitor must be paired.
        entry_name = self.begin_end_stack.pop()
        assert entry_name == node.__class__.__name__, (repr(entry_name), node.__class__.__name__)
        assert self.node == node, (repr(self.node), repr(node))
        # Restore self.node.
        self.node = self.node_stack.pop()
    #@-others
#@+node:ekr.20191231063821.1: *3* class TokenUtils
class TokenUtils:
    """
    A class containing token-oriented utilities.
    """
    #@+others
    #@-others
#@+node:ekr.20191227170803.1: ** Token classes
#@+node:ekr.20191110080535.1: *3* class Token
class Token:
    """
    A class representing a 5-tuple, plus additional data.

    The TokenOrderTraverser class creates a list of such tokens.
    """

    def __init__(self, kind, value):
        
        self.kind = kind
        self.value = value
        #
        # Injected by Tokenizer.add_token.
        self.five_tuple = None
        self.index = 0
        self.line = ''
            # The entire line containing the token.
            # Same as five_tuple.line.
        self.line_number = 0
            # The line number, for errors and dumps.
            # Same as five_tuple.start[0]
        #
        # Injected by Linker class.
        self.level = 0
        self.node = None

    def __repr__(self):
        return f"{self.kind:>11} {self.show_val(80)}"

    def __str__(self):
        return f"{self.kind} {self.show_val(80)}"

    def to_string(self):
        """Return the contribution of the token to the source file."""
        return self.value if isinstance(self.value, str) else ''
        
    #@+others
    #@+node:ekr.20191231114927.1: *4* token.brief_dump
    def brief_dump(self):
        """Dump a token."""
        return (
            f"{self.index:>3} line: {self.line_number:<2} "
            f"{self.kind:>11} {self.show_val(100)}")
    #@+node:ekr.20191113095410.1: *4* token.dump
    def dump(self):
        """Dump a token and related links."""
        # Let block.
        children = getattr(self.node, 'children', [])
        if self.node:
            node_id = getattr(self.node, 'node_index', obj_id(self.node))
        else:
            node_id = ''
        node_cn = self.node.__class__.__name__ if self.node else ''
        parent = getattr(self.node, 'parent', None)
        parent_class = parent.__class__.__name__ if parent else ''
        parent_id = obj_id(parent) if parent else ''
        return (
            f"{self.index:>3} {self.kind:>11} {self.show_val(15):<15} "
            f"line: {self.line_number:<2} level: {self.level:<2} "
            f"{node_id:4} {node_cn:16} "
            f"children: {len(children)} "
            f"parent: {parent_id:4} {parent_class}")
    #@+node:ekr.20191116154328.1: *4* token.error_dump
    def error_dump(self):
        """Dump a token or result node for error message."""
        if self.node:
            node_id = obj_id(self.node)
            node_s = f"{node_id} {self.node.__class__.__name__}"
        else:
            node_s = "None"
        return(
            f"index: {self.index:<3} {self.kind:>12} {self.show_val(20):<20} "
            f"{node_s}")
    #@+node:ekr.20191113095507.1: *4* token.show_val
    def show_val(self, truncate_n=20):
        """Return the token.value field."""
        if self.kind in ('ws', 'indent'):
            val = len(self.value)
        elif self.kind == 'string':
            # Important: don't add a repr for 'string' tokens.
            # repr just adds another layer of confusion.
            val = g.truncate(self.value, truncate_n)
        else:
            val = g.truncate(repr(self.value), truncate_n)
        return val
    #@-others
#@+node:ekr.20191110165235.1: *3* class Tokenizer
class Tokenizer:
    
    """Create a list of Tokens from contents."""
    
    #@+others
    #@+node:ekr.20191110165235.2: *4* tokenizer.add_token
    token_index = 0

    def add_token(self, kind, five_tuple, line, s_row, value):
        """
        Add a token to the results list.
        
        Subclasses could override this method to filter out specific tokens.
        """
        tok = Token(kind, value)
        tok.five_tuple = five_tuple
        tok.index = self.token_index
        self.token_index += 1
        tok.line = line
        tok.line_number = s_row
        self.results.append(tok)
    #@+node:ekr.20191110170551.1: *4* tokenizer.check_results
    def check_results(self, contents):

        # Split the results into lines.
        result = ''.join([z.to_string() for z in self.results])
        result_lines = result.splitlines(True)
        # Check.
        ok = result == contents and result_lines == self.lines
        assert ok, (
            f"result:   {result!r}\n"
            f"contents: {contents!r}\n"
            f"result_lines: {result_lines}\n"
            f"lines:        {self.lines}"
        )
    #@+node:ekr.20191110165235.3: *4* tokenizer.create_input_tokens
    def create_input_tokens(self, contents, tokens):
        """
        Generate a list of Token's from tokens, a list of 5-tuples.
        """
        # Create the physical lines.
        self.lines = contents.splitlines(True)
        # Create the list of character offsets of the start of each physical line.
        last_offset, self.offsets = 0, [0]
        for line in self.lines:
            last_offset += len(line)
            self.offsets.append(last_offset)
        # Handle each token, appending tokens and between-token whitespace to results.
        self.prev_offset, self.results = -1, []
        for token in tokens:
            self.do_token(contents, token)
        # Print results when tracing.
        self.check_results(contents)
        # Return results, as a list.
        return self.results
    #@+node:ekr.20191110165235.4: *4* tokenizer.do_token (the gem)
    header_has_been_shown = False

    trace_mode = False

    def do_token(self, contents, five_tuple):
        """
        Handle the given token, optionally including between-token whitespace.
        
        This is part of the "gem".
        """
        # import leo.core.leoGlobals as g
        import token as token_module
        
        #@+<< define trace functions >>
        #@+node:ekr.20191128074051.1: *5* << define trace functions >>
        def show_header():
            if self.header_has_been_shown:
                return
            self.header_has_been_shown = True
            print("\nTokenizer tokens...\n")
            print("Note: values shown are repr(value) *except* for 'string' tokens.\n")
            print(f"{'lines':<8} {'int indices':<8} {'kind':>7} {'value':<30} physical line")
            print(f"{'=====':<8} {'===========':<8} {'====':>7} {'=====':<30} =============")

        def show_token(kind, val):
            """
            Show the given token.
            Regardless of kind, val is the ground truth, from tok_s.
            """
            if not self.trace_mode:
                return
            show_header()
            val_s = g.truncate(val, 28)
            if kind != 'string':
                val_s = repr(val_s)
            print(
                # starting line..ending line
                f"{show_tuple((s_row, e_row))} "  
                # starting offset..ending offset.
                f"{show_tuple((s_offset, e_offset))} "  
                f"{kind:>10} {val_s:30} {line!r}")
            
        def show_tuple(aTuple):
            s = f"{aTuple[0]}..{aTuple[1]}"
            return f"{s:8}"
        #@-<< define trace functions >>

        # Unpack..
        tok_type, val, start, end, line = five_tuple
        s_row, s_col = start  # row/col offsets of start of token.
        e_row, e_col = end    # row/col offsets of end of token.
        kind = token_module.tok_name[tok_type].lower()
        # Calculate the token's start/end offsets: character offsets into contents.
        s_offset = self.offsets[max(0, s_row-1)] + s_col
        e_offset = self.offsets[max(0, e_row-1)] + e_col
        # tok_s is corresponding string in the line.
        tok_s = contents[s_offset : e_offset]
        # Add any preceding between-token whitespace.
        ws = contents[self.prev_offset : s_offset]
        if ws:
            # No need for a hook.
            self.add_token('ws', five_tuple, line, s_row, ws)
            show_token('ws', ws)
        # Always add token, even if it contributes no text!
        self.add_token(kind, five_tuple, line, s_row, tok_s)
        show_token(kind, tok_s)
        # Update the ending offset.
        self.prev_offset = e_offset
    #@-others
#@-others
g = LeoGlobals()
if __name__ == '__main__':
    unittest.main()
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo

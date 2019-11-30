#@+leo-ver=5-thin
#@+node:ekr.20141012064706.18389: * @file leoAst.py
"""AST (Abstract Syntax Tree) related classes."""
import leo.core.leoGlobals as g
import ast
import re
import types
#@+others
#@+node:ekr.20160521104628.1: **   leoAst.py: top-level
#@+node:ekr.20191027072910.1: *3* exception classes
class AstNotEqual(Exception):
    """The two given AST's are not equivalent."""

class AssignLinksError(Exception):
    """Assigning links to ast nodes failed."""
    
class FailFast(Exception):
    """Abort tests in TestRunner class."""
#@+node:ekr.20160521104555.1: *3* function: _op_names
#@@nobeautify

# Python 2: https://docs.python.org/2/library/ast.html
# Python 3: https://docs.python.org/3/library/ast.html

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
#@+node:ekr.20191027072126.1: *3* function: compare_asts & helpers
def compare_asts(ast1, ast2):
    """Compare two ast trees. Return True if they are equal."""
    # import leo.core.leoGlobals as g
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
        g.warning(f"Unexpected exception")
        g.es_exception()
        return False
    return True
#@+node:ekr.20191027071653.2: *4* function._compare_asts
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
#@+node:ekr.20191027071653.3: *4* function._compare_nodes
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
#@+node:ekr.20191027074436.1: *3* function: dump_ast
def dump_ast(ast, tag=None):
    """Utility to dump an ast tree."""
    # import leo.core.leoGlobals as g
    g.printObj(AstDumper().dump(ast), tag=tag)
#@+node:ekr.20191109063033.1: *3* function: funcToMethod 

def funcToMethod(f, theClass, name=None):
    """
    From the Python Cookbook...

    The following method allows you to add a function as a method of
    any class. That is, it converts the function to a method of the
    class. The method just added is available instantly to all
    existing instances of the class, and to all instances created in
    the future.
    
    The function's first argument should be self.
    
    The newly created method has the same name as the function unless
    the optional name argument is supplied, in which case that name is
    used as the method name.
    """
    setattr(theClass, name or f.__name__, f)
#@+node:ekr.20191119085222.1: *3* function: obj_id
def obj_id(obj):
    """Return the last four digits of id(obj), for dumps & traces."""
    return str(id(obj))[-4:]
#@+node:ekr.20191027075648.1: *3* function: parse_ast
def parse_ast(s, headline=None):
    """
    Parse string s, catching & reporting all exceptions.
    Return the ast node, or None.
    """
    # import leo.core.leoGlobals as g

    def oops(message):
        print('')
        if headline:
            g.warning(f"parse_ast: {message} in: {headline}")
        else:
            g.warning(f"parse_ast: {message}")
        print('')

    try:
        s1 = g.toEncodedString(s)
        return ast.parse(s1, filename='before', mode='exec')
    except IndentationError:
        oops('Indentation Error')
    except SyntaxError:
        oops('Syntax Error')
    except Exception:
        oops('Unexpected Exception')
        g.es_exception()
    return None
#@+node:ekr.20160521103254.1: *3* function: unit_test
def unit_test(raise_on_fail=True):
    """Run basic unit tests for this file."""
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
        AstFullTraverser,
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
#@+node:ekr.20191113205051.1: *3* function: truncate
def truncate(s, n):
    if isinstance(s, str):
        s = s.replace('\n','<NL>')
    else:
        s = repr(s)
    return s if len(s) <  n else s[:n-3] + '...'
#@+node:ekr.20141012064706.18399: **  class AstFormatter
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
    #@+node:ekr.20141012064706.18402: *3* f.format
    def format(self, node, level, *args, **keys):
        """Format the node and possibly its descendants, depending on args."""
        self.level = level
        val = self.visit(node, *args, **keys)
        return val.rstrip() if val else ''
    #@+node:ekr.20141012064706.18403: *3* f.visit
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
    #@+node:ekr.20141012064706.18469: *3* f.indent
    def indent(self, s):
        return f'%s%s' % (' ' * 4 * self.level, s)
    #@+node:ekr.20141012064706.18404: *3* f: Contexts
    #@+node:ekr.20141012064706.18405: *4* f.ClassDef
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
    #@+node:ekr.20141012064706.18406: *4* f.FunctionDef & AsyncFunctionDef
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
    #@+node:ekr.20141012064706.18407: *4* f.Interactive
    def do_Interactive(self, node):
        for z in node.body:
            self.visit(z)
    #@+node:ekr.20141012064706.18408: *4* f.Module
    def do_Module(self, node):
        assert 'body' in node._fields
        result = ''.join([self.visit(z) for z in node.body])
        return result
    #@+node:ekr.20141012064706.18409: *4* f.Lambda
    def do_Lambda(self, node):
        return self.indent(f'lambda %s: %s' % (
            self.visit(node.args),
            self.visit(node.body)))
    #@+node:ekr.20141012064706.18410: *3* f: Expressions
    #@+node:ekr.20141012064706.18411: *4* f.Expr
    def do_Expr(self, node):
        """An outer expression: must be indented."""
        assert not self.in_expr
        self.in_expr = True
        value = self.visit(node.value)
        self.in_expr = False
        return self.indent(f'%s\n' % value)
    #@+node:ekr.20141012064706.18412: *4* f.Expression
    def do_Expression(self, node):
        """An inner expression: do not indent."""
        return f'%s\n' % self.visit(node.body)
    #@+node:ekr.20141012064706.18413: *4* f.GeneratorExp
    def do_GeneratorExp(self, node):
        elt = self.visit(node.elt) or ''
        gens = [self.visit(z) for z in node.generators]
        gens = [z if z else '<**None**>' for z in gens]  # Kludge: probable bug.
        return f'<gen %s for %s>' % (elt, ','.join(gens))
    #@+node:ekr.20141012064706.18414: *4* f.ctx nodes
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
    #@+node:ekr.20141012064706.18415: *3* f: Operands
    #@+node:ekr.20141012064706.18416: *4* f.arguments
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
    #@+node:ekr.20141012064706.18417: *4* f.arg (Python3 only)
    # 3: arg = (identifier arg, expr? annotation)

    def do_arg(self, node):
        if getattr(node, 'annotation', None):
            return self.visit(node.annotation)
        return node.arg
    #@+node:ekr.20141012064706.18418: *4* f.Attribute
    # Attribute(expr value, identifier attr, expr_context ctx)

    def do_Attribute(self, node):
        return f'%s.%s' % (
            self.visit(node.value),
            node.attr)  # Don't visit node.attr: it is always a string.
    #@+node:ekr.20141012064706.18419: *4* f.Bytes
    def do_Bytes(self, node):  # Python 3.x only.
        return str(node.s)
    #@+node:ekr.20141012064706.18420: *4* f.Call & f.keyword
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
    #@+node:ekr.20141012064706.18421: *5* f.keyword
    # keyword = (identifier arg, expr value)

    def do_keyword(self, node):
        # node.arg is a string.
        value = self.visit(node.value)
        # This is a keyword *arg*, not a Python keyword!
        return f'%s=%s' % (node.arg, value)
    #@+node:ekr.20141012064706.18422: *4* f.comprehension
    def do_comprehension(self, node):
        result = []
        name = self.visit(node.target)  # A name.
        it = self.visit(node.iter)  # An attribute.
        result.append(f'%s in %s' % (name, it))
        ifs = [self.visit(z) for z in node.ifs]
        if ifs:
            result.append(f' if %s' % (''.join(ifs)))
        return ''.join(result)
    #@+node:ekr.20170721073056.1: *4* f.Constant (Python 3.6+)
    def do_Constant(self, node):  # Python 3.6+ only.
        return str(node.s)  # A guess.
    #@+node:ekr.20141012064706.18423: *4* f.Dict
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
    #@+node:ekr.20160523101618.1: *4* f.DictComp
    # DictComp(expr key, expr value, comprehension* generators)

    def do_DictComp(self, node):
        key = self.visit(node.key)
        value = self.visit(node.value)
        gens = [self.visit(z) for z in node.generators]
        gens = [z if z else '<**None**>' for z in gens]  # Kludge: probable bug.
        return f'%s:%s for %s' % (key, value, ''.join(gens))
    #@+node:ekr.20141012064706.18424: *4* f.Ellipsis
    def do_Ellipsis(self, node):
        return '...'
    #@+node:ekr.20141012064706.18425: *4* f.ExtSlice
    def do_ExtSlice(self, node):
        return ':'.join([self.visit(z) for z in node.dims])
    #@+node:ekr.20170721075130.1: *4* f.FormattedValue (Python 3.6+)
    # FormattedValue(expr value, int? conversion, expr? format_spec)

    def do_FormattedValue(self, node):  # Python 3.6+ only.
        return f'%s%s%s' % (
            self.visit(node.value),
            self.visit(node.conversion) if node.conversion else '',
            self.visit(node.format_spec) if node.format_spec else '')
    #@+node:ekr.20141012064706.18426: *4* f.Index
    def do_Index(self, node):
        return self.visit(node.value)
    #@+node:ekr.20170721080559.1: *4* f.JoinedStr (Python 3.6)
    # JoinedStr(expr* values)

    def do_JoinedStr(self, node):

        if node.values:
            for value in node.values:
                self.visit(value)
    #@+node:ekr.20141012064706.18427: *4* f.List
    def do_List(self, node):
        # Not used: list context.
        # self.visit(node.ctx)
        elts = [self.visit(z) for z in node.elts]
        elts = [z for z in elts if z]  # Defensive.
        return f'[%s]' % ','.join(elts)
    #@+node:ekr.20141012064706.18428: *4* f.ListComp
    def do_ListComp(self, node):
        elt = self.visit(node.elt)
        gens = [self.visit(z) for z in node.generators]
        gens = [z if z else '<**None**>' for z in gens]  # Kludge: probable bug.
        return f'%s for %s' % (elt, ''.join(gens))
    #@+node:ekr.20141012064706.18429: *4* f.Name & NameConstant
    def do_Name(self, node):
        return node.id

    def do_NameConstant(self, node):  # Python 3 only.
        s = repr(node.value)
        return s
    #@+node:ekr.20141012064706.18430: *4* f.Num
    def do_Num(self, node):
        return repr(node.n)
    #@+node:ekr.20141012064706.18431: *4* f.Repr
    # Python 2.x only

    def do_Repr(self, node):
        return f'repr(%s)' % self.visit(node.value)
    #@+node:ekr.20160523101929.1: *4* f.Set
    # Set(expr* elts)

    def do_Set(self, node):
        for z in node.elts:
            self.visit(z)
    #@+node:ekr.20160523102226.1: *4* f.SetComp
    # SetComp(expr elt, comprehension* generators)

    def do_SetComp(self, node):

        elt = self.visit(node.elt)
        gens = [self.visit(z) for z in node.generators]
        return f'%s for %s' % (elt, ''.join(gens))
    #@+node:ekr.20141012064706.18432: *4* f.Slice
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
    #@+node:ekr.20141012064706.18433: *4* f.Str
    def do_Str(self, node):
        """This represents a string constant."""
        return repr(node.s)
    #@+node:ekr.20141012064706.18434: *4* f.Subscript
    # Subscript(expr value, slice slice, expr_context ctx)

    def do_Subscript(self, node):
        value = self.visit(node.value)
        the_slice = self.visit(node.slice)
        return f'%s[%s]' % (value, the_slice)
    #@+node:ekr.20141012064706.18435: *4* f.Tuple
    def do_Tuple(self, node):
        elts = [self.visit(z) for z in node.elts]
        return f'(%s)' % ','.join(elts)
    #@+node:ekr.20141012064706.18436: *3* f: Operators
    #@+node:ekr.20160521104724.1: *4* f.op_name
    def op_name(self, node, strict=True):
        """Return the print name of an operator node."""
        name = _op_names.get(node.__class__.__name__, f'<%s>' % node.__class__.__name__)
        if strict: 
            assert name, node.__class__.__name__
        return name
    #@+node:ekr.20141012064706.18437: *4* f.BinOp
    def do_BinOp(self, node):
        return f'%s%s%s' % (
            self.visit(node.left),
            self.op_name(node.op),
            self.visit(node.right))
    #@+node:ekr.20141012064706.18438: *4* f.BoolOp
    def do_BoolOp(self, node):
        op_name = self.op_name(node.op)
        values = [self.visit(z).strip() for z in node.values]
        return op_name.join(values)
    #@+node:ekr.20141012064706.18439: *4* f.Compare
    def do_Compare(self, node):
        result = []
        lt = self.visit(node.left)
        # ops   = [self.visit(z) for z in node.ops]
        ops = [self.op_name(z) for z in node.ops]
        comps = [self.visit(z) for z in node.comparators]
        result.append(lt)
        assert len(ops) == len(comps), repr(node)
        for i in range(len(ops)):
            result.append(f'%s%s' % (ops[i], comps[i]))
        return ''.join(result)
    #@+node:ekr.20141012064706.18440: *4* f.UnaryOp
    def do_UnaryOp(self, node):
        return f'%s%s' % (
            self.op_name(node.op),
            self.visit(node.operand))
    #@+node:ekr.20141012064706.18441: *4* f.ifExp (ternary operator)
    def do_IfExp(self, node):
        return f'%s if %s else %s ' % (
            self.visit(node.body),
            self.visit(node.test),
            self.visit(node.orelse))
    #@+node:ekr.20141012064706.18442: *3* f: Statements
    #@+node:ekr.20170721074105.1: *4* f.AnnAssign
    # AnnAssign(expr target, expr annotation, expr? value, int simple)

    def do_AnnAssign(self, node):
        return self.indent(f'%s:%s=%s\n' % (
            self.visit(node.target),
            self.visit(node.annotation),
            self.visit(node.value),
        ))
    #@+node:ekr.20141012064706.18443: *4* f.Assert
    def do_Assert(self, node):
        test = self.visit(node.test)
        if getattr(node, 'msg', None):
            message = self.visit(node.msg)
            return self.indent(f'assert %s, %s' % (test, message))
        return self.indent(f'assert %s' % test)
    #@+node:ekr.20141012064706.18444: *4* f.Assign
    def do_Assign(self, node):
        return self.indent(f'%s=%s\n' % (
            '='.join([self.visit(z) for z in node.targets]),
            self.visit(node.value)))
    #@+node:ekr.20141012064706.18445: *4* f.AugAssign
    def do_AugAssign(self, node):
        return self.indent(f'%s%s=%s\n' % (
            self.visit(node.target),
            self.op_name(node.op),  # Bug fix: 2013/03/08.
            self.visit(node.value)))
    #@+node:ekr.20160523100504.1: *4* f.Await (Python 3)
    # Await(expr value)

    def do_Await(self, node):

        return self.indent(f'await %s\n' % (
            self.visit(node.value)))
    #@+node:ekr.20141012064706.18446: *4* f.Break
    def do_Break(self, node):
        return self.indent(f'break\n')
    #@+node:ekr.20141012064706.18447: *4* f.Continue
    def do_Continue(self, node):
        return self.indent(f'continue\n')
    #@+node:ekr.20141012064706.18448: *4* f.Delete
    def do_Delete(self, node):
        targets = [self.visit(z) for z in node.targets]
        return self.indent(f'del %s\n' % ','.join(targets))
    #@+node:ekr.20141012064706.18449: *4* f.ExceptHandler
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
    #@+node:ekr.20141012064706.18450: *4* f.Exec
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
    #@+node:ekr.20141012064706.18451: *4* f.For & AsnchFor (Python 3)
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
    #@+node:ekr.20141012064706.18452: *4* f.Global
    def do_Global(self, node):
        return self.indent(f'global %s\n' % (
            ','.join(node.names)))
    #@+node:ekr.20141012064706.18453: *4* f.If
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
    #@+node:ekr.20141012064706.18454: *4* f.Import & helper
    def do_Import(self, node):
        names = []
        for fn, asname in self.get_import_names(node):
            if asname:
                names.append(f'%s as %s' % (fn, asname))
            else:
                names.append(fn)
        return self.indent(f'import %s\n' % (
            ','.join(names)))
    #@+node:ekr.20141012064706.18455: *5* f.get_import_names
    def get_import_names(self, node):
        """Return a list of the the full file names in the import statement."""
        result = []
        for ast2 in node.names:
            assert ast2.__class__.__name__ == 'alias', (repr(ast2))
            data = ast2.name, ast2.asname
            result.append(data)
        return result
    #@+node:ekr.20141012064706.18456: *4* f.ImportFrom
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
    #@+node:ekr.20160317050557.2: *4* f.Nonlocal (Python 3)
    # Nonlocal(identifier* names)

    def do_Nonlocal(self, node):

        return self.indent(f'nonlocal %s\n' % ', '.join(node.names))
    #@+node:ekr.20141012064706.18457: *4* f.Pass
    def do_Pass(self, node):
        return self.indent('pass\n')
    #@+node:ekr.20141012064706.18458: *4* f.Print
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
    #@+node:ekr.20141012064706.18459: *4* f.Raise
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
    #@+node:ekr.20141012064706.18460: *4* f.Return
    def do_Return(self, node):
        if node.value:
            return self.indent(f'return %s\n' % (
                self.visit(node.value)))
        return self.indent('return\n')
    #@+node:ekr.20160317050557.3: *4* f.Starred (Python 3)
    # Starred(expr value, expr_context ctx)

    def do_Starred(self, node):

        return '*' + self.visit(node.value)
    #@+node:ekr.20141012064706.18461: *4* f.Suite
    # def do_Suite(self,node):
        # for z in node.body:
            # s = self.visit(z)
    #@+node:ekr.20160317050557.4: *4* f.Try (Python 3)
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
    #@+node:ekr.20141012064706.18462: *4* f.TryExcept
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
    #@+node:ekr.20141012064706.18463: *4* f.TryFinally
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
    #@+node:ekr.20141012064706.18464: *4* f.While
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
    #@+node:ekr.20141012064706.18465: *4* f.With & AsyncWith (Python 3)
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
    #@+node:ekr.20141012064706.18466: *4* f.Yield
    def do_Yield(self, node):
        if getattr(node, 'value', None):
            return self.indent(f'yield %s\n' % (
                self.visit(node.value)))
        return self.indent('yield\n')
    #@+node:ekr.20160317050557.5: *4* f.YieldFrom (Python 3)
    # YieldFrom(expr value)

    def do_YieldFrom(self, node):

        return self.indent(f'yield from %s\n' % (
            self.visit(node.value)))
    #@-others
#@+node:ekr.20191113063144.1: **  class TokenOrderGenerator
class TokenOrderGenerator:
    """A class that traverses ast (parse) trees in token order."""

    coverage_set = set()
        # The set of node.__class__.__name__ that have been visited.
        
    trace_mode = False

    #@+others
    #@+node:ekr.20191113063144.3: *3* tog.begin/end_visitor
    begin_end_stack = []
    node_index = 0  # The index into the node_stack.
    node_stack = []  # The stack of parent nodes.

    # These methods support generators.

    # Subclasses may/should override these methods.

    def begin_visitor(self, node):
        """Enter a visitor."""
        if 0:
            g.trace(node.__class__.__name__)
            g.printObj([z.__class__.__name__ for z in self.node_stack])
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
    #@+node:ekr.20191113063144.4: *3* tog.create_links (entry)
    def create_links(self, tokens, tree, file_name=''):
        """
        Verify that traversing the given ast tree generates exactly the given
        tokens, in exact order.
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
        if 0: ### Should not be necessary.
            self.node = tree
            yield from self.gen_token('newline', '\n')
            yield from self.gen_token('endmarker', '')
       
    #@+node:ekr.20191126074902.1: *3* tog.dump_one_node (new)
    header_has_been_shown = False

    def dump_one_node(self, node, level, tag=None):
        """
        Dump one node using AstDumper().brief_dump_one_node.
        
        Precede the dump with the header if necessary.
        """
        dumper = AstDumper()
        if self.header_has_been_shown:
            print('')
        else:
            self.header_has_been_shown = True
            if tag:
                print(f"\ndump_one_node: {tag} {self.file_name}")
            print(f"\n{dumper.show_header()}")
        print(dumper.brief_dump_one_node(node, level))
    #@+node:ekr.20191129044716.1: *3* tog.error
    def error(self, message):
        """
        Prepend the caller to the message, print it, and return AssignLinksError.
        """
        caller = g.callers(4).split(',')[-1]
        print(f"\n{caller}: Error...\n")
        # Don't change the message. It may contain aligned lines.
        print(message)
        return AssignLinksError(message)
    #@+node:ekr.20191121180100.1: *3* tog.gen*
    # Useful wrappers.

    def gen(self, z):
        yield from self.visitor(z)

    ### There is never any need to sync on commas or blanks.
    ###
        # def gen_blank(self):
        #    yield from self.visitor(self.sync_blank())
        #
        # def gen_comma(self):
        #    yield from self.visitor(self.sync_comma())
        
    def gen_name(self, val):
        yield from self.visitor(self.sync_name(val))
                    
    def gen_newline(self):
        yield from self.visitor(self.sync_token('newline', '\n'))

    def gen_op(self, val):
        yield from self.visitor(self.sync_op(val))
        
    def gen_token(self, kind, val):
        yield from self.visitor(self.sync_token(kind, val))
    #@+node:ekr.20191113063144.6: *3* tog.make_tokens
    def make_tokens(self, contents, trace_mode=False):
        """
        Return a list (not a generator) of Token objects corresponding to the
        list of 5-tuples generated by tokenize.tokenize.
        """
        # import leo.core.leoGlobals as g
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
    #@+node:ekr.20191113063144.54: *3* tog.op_name
    def op_name(self, node):
        """Return the print name of an operator node."""
        # This is *not* a visitor.
        class_name = node.__class__.__name__
        assert class_name in _op_names, repr(class_name)
        return _op_names [class_name].strip()
    #@+node:ekr.20191124123830.1: *3* tog.is_assignable_token & is_significant*
    def is_assignable_token(self, token):
        """
        A global predicate returning True if the token should be assigned to
        the token_list field of the next significant token.
        
        Code should *not* use any similar local predicate.
        """
        return (
            self.is_significant_token(token)
            or token.kind in ('comment', 'newline')
        )
            # or token.kind == 'op' and token.value in ',()'

    def is_significant(self, kind, value):
        """
        A global predicate returning True if kind, value represent a token that
        can be used for syncing generated tokens with the token list.
        
        Code should *not* use any similar local predicate.
        """
        # Making 'endmarker' significant ensures that all tokens are synced.
        return (
            kind in ('endmarker', 'name', 'number', 'string') or
            kind == 'op' and value not in ',;()')

    def is_significant_token(self, token):
        """Return True if the given token is a syncronizing token"""
        return self.is_significant(token.kind, token.value)
    #@+node:ekr.20191113063144.7: *3* tog.sync_token & set_links
    px = -1 # Index of the previous *significant* token.

    allow_sync = True  # Can be set to false by test runner.

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
        ### old_px, px = self.px + 1, self.px
        assert isinstance(node, ast.AST), repr(node)
        if not self.allow_sync:
            # A trace would be annoying and distracting.
            return
        if trace:
            # Don't add needless repr's!
            val_s = val if kind in ('name', 'string') else repr(val)
            if trace: g.trace(f"\n{self.node.__class__.__name__} {kind}.{val_s}")
        #
        # Leave all non-significant tokens for later.
        if not self.is_significant(kind, val):
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
        if trace: g.trace('\nENTRY', px, kind, val)
        while px < len(self.tokens):
            token = tokens[px]
            if trace: g.trace('TOKEN', px, token)
            if (kind, val) == (token.kind, token.value):
                if trace: g.trace('   OK', px, token)
                break  # Success.
            #
            # Special case 'string' token.
            if kind == 'string':
                if token.kind == 'string':
                    raise self.error(
                        f"STRING MISMATCH: "
                        f"val: {val} token.val: {token.value}")
                # Assume we are in in a JoinedStr.
                # Continue searching.
                px += 1
                continue
            if kind == token.kind == 'number':
                if trace: g.trace('   OK', px, token)
                val = token.value
                break  # Benign: use the token's value, a string, instead of a number.
            if self.is_significant_token(token):
                # Unrecoverable sync failure.
                if 1:
                    pre_tokens = tokens[max(0, px-10):px+1]
                    g.trace('\nSync Failed...\n')
                    for s in [f"{i:>4}: {z!r}" for i, z in enumerate(pre_tokens)]:
                        print(s)
                raise self.error(
                    f"       line: {token.line_number}: {token.line.strip()}\n"
                    f"Looking for: {kind}.{val}\n"
                    f"      found: {token.kind}.{token.value}")
            else:
                # Skip the insignificant token.
                if trace: g.trace(' SKIP', px, token)
                px += 1
        else:
            # Unrecoverable sync failure.
            g.trace('\nSYNC FAILED...')
            g.printObj(tokens[max(0, px-5):], 'TOKENS')
            raise self.error(
                 f"Looking for: {kind}.{val}\n"
                 f"      found: end of token list")
        #
        # Step two: Associate all previous assignable tokens to the ast node.
        while old_px < px:
            token = tokens[old_px]
            if trace: g.trace('LINK INSIGNIFICANT', old_px, token)
            old_px += 1
            self.set_links(self.node, token)
        #
        # Step three: Set links in the significant token.
        token = tokens[px]
        if self.is_significant_token(token):
            self.set_links(node, token)
        ### assert self.is_significant_token(token), (token, g.callers())
        else:
            if trace: g.trace('NOT SIGNIFICANT', px, token, g.callers())
        #
        # Step four. Advance.
        if self.is_significant_token(token):
            self.px = px
    #@+node:ekr.20191125120814.1: *4* tog.set_links
    def set_links(self, node, token):
        """Make two-way links between token and the given node."""
        assert token.node is None, (repr(token), g.callers())
        if self.is_assignable_token(token):
            #
            # Link the token to the ast node.
            token.node = node
            #
            # Add the token to node's token_list.
            token_list = getattr(node, 'token_list', [])
            node.token_list = token_list + [token]
    #@+node:ekr.20191124083124.1: *3* tog.sync_token helpers
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
    #@+node:ekr.20191113063144.11: *3* tog.report_coverage
    def report_coverage(self, report_missing):
        """Report untested visitors."""
        # import leo.core.leoGlobals as g

        def key(z):
            return z.lower()

        covered = sorted(list(self.coverage_set), key=key)
        visitors = [z[3:] for z in dir(self) if z.startswith('do_')]
        missing = sorted([z for z in visitors if z not in covered], key=key)
        print('Covered...\n')
        g.printObj(covered)
        print('')
        if report_missing:
            print('Missing...\n')
            g.printObj(missing)
            print('')
    #@+node:ekr.20191113081443.1: *3* tog.visitor (calls begin/end_visitor)
    def visitor(self, node):
        """Given an ast node, return a *generator* from its visitor."""
        # This saves a lot of tests.
        if node is None:
            return
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
    #@+node:ekr.20191113063144.13: *3* tog: Visitors
    #@+node:ekr.20191113063144.14: *4* tog: Contexts
    #@+node:ekr.20191113063144.15: *5* tog.AsyncFunctionDef
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
    #@+node:ekr.20191113063144.16: *5* tog.ClassDef
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
    #@+node:ekr.20191113063144.17: *5* tog.FunctionDef
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
    #@+node:ekr.20191113063144.18: *5* tog.Interactive
    def do_Interactive(self, node):
        
        yield from self.gen(node.body)
    #@+node:ekr.20191113063144.20: *5* tog.Lambda
    def do_Lambda(self, node):

        yield from self.gen_name('lambda')
        yield from self.gen(node.args)
        yield from self.gen_op(':')
        yield from self.gen(node.body)
    #@+node:ekr.20191113063144.19: *5* tog.Module
    def do_Module(self, node):

        # Encoding is a non-syncing statement.
        yield from self.gen_token('encoding', '')
        yield from self.gen(node.body)
    #@+node:ekr.20191113063144.21: *4* tog: Expressions
    #@+node:ekr.20191113063144.22: *5* tog.Expr
    def do_Expr(self, node):
        """An outer expression."""
        # No need to put parentheses.
        yield from self.gen(node.value)
    #@+node:ekr.20191113063144.23: *5* tog.Expression
    def do_Expression(self, node):
        """An inner expression."""
        # No need to put parentheses.
        yield from self.gen(node.body)
    #@+node:ekr.20191113063144.24: *5* tog.GeneratorExp
    def do_GeneratorExp(self, node):

        # '<gen %s for %s>' % (elt, ','.join(gens))
        # No need to put parentheses or commas.
        yield from self.gen(node.elt)
        yield from self.gen_name('for')
        yield from self.gen(node.generators)
    #@+node:ekr.20191115104619.1: *5* tog.generator
    def do_generator(self, node):

        # No need to put commas or parentheses.
        yield from node
            # *Not* yield from self.gen(node)
    #@+node:ekr.20191113063144.26: *4* tog: Operands
    #@+node:ekr.20191113063144.28: *5* tog.arg
    # arg = (identifier arg, expr? annotation)

    def do_arg(self, node):
        
        yield from self.gen_name(node.arg)
        annotation = getattr(node, 'annotation', None)
        if annotation is not None:
            yield from self.gen(node.annotation)
    #@+node:ekr.20191113063144.27: *5* tog.arguments
    def do_arguments(self, node):

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
    #@+node:ekr.20191113063144.29: *5* tog.Attribute
    # Attribute(expr value, identifier attr, expr_context ctx)

    def do_Attribute(self, node):

        yield from self.gen(node.value)
        yield from self.gen_op('.')
        yield from self.gen_name(node.attr) # A string.
    #@+node:ekr.20191113063144.30: *5* tog.Bytes
    def do_Bytes(self, node):

        yield from self.gen_token('bytes', str(node.s))
    #@+node:ekr.20191113063144.31: *5* tog.Call & tog.keyword
    # Call(expr func, expr* args, keyword* keywords, expr? starargs, expr? kwargs)

    def do_Call(self, node):

        yield from self.gen(node.func)
        yield from self.gen_op('(')
        yield from self.gen(node.args)
        yield from self.gen(node.keywords)
            # The visitors puts the '**' if there is no name field.
        if hasattr(node, 'starargs'):
            # The visitor puts the '*'.
            yield from self.gen(node.starargs)
        if hasattr(node, 'kwargs'):
            # The visitor puts the '**'.
            yield from self.gen(node.kwargs)
        yield from self.gen_op(')')
    #@+node:ekr.20191113063144.32: *6* tog.keyword
    # keyword = (identifier arg, expr value)

    def do_keyword(self, node):

        if node.arg:
            yield from self.gen_name(node.arg)
            yield from self.gen_op('=')
        else:
            # weird, but correct.
            yield from self.gen_op('**') 
        yield from self.gen(node.value)
    #@+node:ekr.20191113063144.33: *5* tog.comprehension
    def do_comprehension(self, node):

        # No need to put parentheses.
        yield from self.gen(node.target) # A name
        yield from self.gen_name('in')
        yield from self.gen(node.iter)
        if node.ifs:
            yield from self.gen_name('if')
            yield from self.gen(node.ifs)
    #@+node:ekr.20191113063144.34: *5* tog.Constant
    def do_Constant(self, node):
        
        g.trace(node.s) ###
        yield from self.gen_token('number', str(node.s))
    #@+node:ekr.20191113063144.35: *5* tog.Dict
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
    #@+node:ekr.20191113063144.36: *5* tog.DictComp
    # DictComp(expr key, expr value, comprehension* generators)

    def do_DictComp(self, node):

        yield from self.gen(node.key)
        yield from self.gen_op(':')
        yield from self.gen_name('for')
        # No need to put commas.
        yield from self.gen(node.generators)
    #@+node:ekr.20191113063144.37: *5* tog.Ellipsis
    def do_Ellipsis(self, node):
        
        yield from self.gen_op('...')
    #@+node:ekr.20191113063144.38: *5* tog.ExtSlice
    def do_ExtSlice(self, node):
        
        # ':'.join(node.dims)
        for i, z in enumerate(node.dims):
            yield from self.gen(z)
            if i < len(node.dims) - 1:
                yield from self.gen_op(':')
    #@+node:ekr.20191113063144.40: *5* tog.Index
    def do_Index(self, node):

        yield from self.gen(node.value)
    #@+node:ekr.20191113063144.39: *5* tog.FormattedValue (never called!)
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
    #@+node:ekr.20191115105821.1: *5* tog.int
    def do_int(self, node):
        
        # node is an int, not an ast node.
        # Do *not* call begin/end visitor!
        assert isinstance(node, int), repr(node)
        # Assign the int to the parent.
        try: ###
            yield from self.gen_token('num', node)
        except Exception as e:
            g.trace(e, g.callers())

    #@+node:ekr.20191113063144.41: *5* tog.JoinedStr (***)
    # JoinedStr(expr* values)

    def do_JoinedStr(self, node):
        """
        Fact 1: A JoinedStr node represents one or more f-strings and plain strings.
        
        Fact 2: *All* f-strings appear in a JoinedStr, regardless of whether
                those f-strings are concatenated with other plain strings or f-strings.

        Fact 3: node.values is a list of Str and FormattedValue nodes.
        
        Fact 4: There is a many-to-many relationship between 'string' tokens
                and the items in the node.values list.
                
                - if isinstance(item, ast.Str):
                  The item represents *one or more* 'string' tokens.
          
                - if isinstance(item, ast.FormattedValue):
                  The item is a tree of ast.Ast node representing *one* 'string' token.
                  
        Fact 5: This code, and *only* this code, must handle these complications.
                There is *no way* that visiting an FormattedValue tree can be useful.
        """
        # node.values is a list of ast.Ast nodes, *not* a list of generators.
        trace = True and self.trace_mode
        assert isinstance(node.values, list)
        assert all([isinstance(z, (ast.Str, ast.FormattedValue)) for z in node.values])
        if trace:
            g.trace('\n===== START\n')
            g.printObj([z.__class__.__name__ for z in node.values])
        #
        # Handle each item, but...
        # The first item will be a string representing the *entire* f-string!
        for i, item in enumerate(node.values):
            # Compute the target string.
            if isinstance(item, ast.Str):
                # item represents *one or more* 'string' tokens.
                # Sync all those 'string' tokens to item.s.
                target_s = item.s
            else:
                # item is a tree of ast.Ast nodes.
                # Ignore this node completely.
                    ### Sync to the next 'string' token.
                    ### target_s = self.peek_next_str().value
                continue ###
            # Yield all the tokens.
            if trace:
                g.trace(f"\n----- item: {i} {item.__class__.__name__} target: {target_s}\n")
            tokens = self.advance_str(target_s=target_s)
            if not tokens:
                raise self.error(f"no tokens from advance_str. target_s: {target_s}")
            for token in tokens:
                if token.kind != 'string':
                    raise self.error(f"not a string token: {token!r}")
                if trace:
                    g.trace(f"\ngenerate 'string' {token.value}")
                yield from self.gen_token('string', token.value)
            break ### Experimental.
        if trace:
            g.trace('\nEND -----\n')
        
        if 0: # This code has no chance of being useful.
            for z in node.values:
                if self.trace_mode:
                    g.trace('\nitem:', z.__class__.__name__)
                if isinstance(z, ast.FormattedValue):
                   yield from self.gen(z)
                else:
                    assert isinstance(z, ast.Str), repr(z)
                    yield from self.gen(z)
    #@+node:ekr.20191113063144.42: *5* tog.List
    def do_List(self, node):

        # No need to put commas.
        yield from self.gen_op('[')
        yield from self.gen(node.elts)
        yield from self.gen_op(']')
    #@+node:ekr.20191113063144.43: *5* tog.ListComp
    # ListComp(expr elt, comprehension* generators)

    def do_ListComp(self, node):
       
        yield from self.gen_op('[')
        yield from self.gen(node.elt)
        yield from self.gen_name('for')
        yield from self.gen(node.generators)
        yield from self.gen_op(']')
    #@+node:ekr.20191113063144.44: *5* tog.Name & NameConstant (tested)
    def do_Name(self, node):
        
        yield from self.gen_name(node.id)

    def do_NameConstant(self, node):

        yield from self.gen_name(repr(node.value))
    #@+node:ekr.20191113063144.45: *5* tog.Num
    def do_Num(self, node):
        
        yield from self.gen_token('number', node.n)
    #@+node:ekr.20191113063144.47: *5* tog.Set
    # Set(expr* elts)

    def do_Set(self, node):

        yield from self.gen(node.elts)
    #@+node:ekr.20191113063144.48: *5* tog.SetComp
    # SetComp(expr elt, comprehension* generators)

    def do_SetComp(self, node):

        yield from self.gen(node.elt)
        yield from self.gen_name('for')
        yield from self.gen(node.generators)
    #@+node:ekr.20191113063144.49: *5* tog.Slice
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
    #@+node:ekr.20191113063144.50: *5* tog.Str & helpers
    # The index in self.tokens of the previously scanned 'string' token
    string_index = -1 

    def do_Str(self, node):
        """This node represents a string constant."""
        ### g.trace('===========', g.callers())
        token_list = self.advance_str()
        for token in token_list:
            yield from self.gen_token('string', token.value)
    #@+node:ekr.20191128021208.1: *6* tog.adjust_str_token ***
    prefix_pat = re.compile(r"([fFrR])")

    def adjust_str_token(self, token):
        #@+<< adjust_str_token docstring >>
        #@+node:ekr.20191130111223.1: *7* << adjust_str_token docstring >>
        """
        This is the heart of the TOG class.

        The goal is to determine how much of the target string to consume.
        This is a tricky task for two reasons:
            
        1. The target string comes from an ast.Str node, and may be the
           concatenation of *more than one* strings from the token list.
           
        2. The spellings of strings in tokens and tree nodes differ:
           'string' tokens contain the repr of each of the corresponding
           parts of the target string.

        The *only* way to accomplish this goal is by a careful comparison
        between tv (token.value) and r, the *remainder* of the target string.

        On exit: Update self.target_index and return the consumed parts of the
        *target* string.

        *Note*: For empty strings this method might not consume anything.
                That's benign because the caller always skips one token.
        """
        #@-<< adjust_str_token docstring >>
        trace = False and self.trace_mode
        quotes = ("'", '"')
        rx0 = self.target_index
        r = self.target_string[rx0:]
        tv = token.value
        if trace:
            g.trace(f"\ntarget_index: {rx0} tv: {tv!s} r: {r!s}")
        #
        # Compute and check the prefixes.
        m = self.prefix_pat.match(r)
        r_prefix = m.group(0) if m else ''
        m = self.prefix_pat.match(tv)
        tv_prefix = m.group(0) if m else ''
        
        ### Not sure this matters.
            # if r_prefix and len(r_prefix) != len(tv_prefix):
                # g.trace(f"tv_prefix: {tv_prefix!s} r_prefix: {r_prefix!s}")
                # raise self.error(f"Mismatch prefixes' tv: {tv!s} r: {r!s}")
        #
        # The token must have a quote.
        tx = len(tv_prefix)
        if tv.startswith(quotes, tx) and tv.endswith(quotes):
            tv_quote = tv[tx]
        else:
            raise self.error(f"Missing quote in tv: {tv!r}")
        if tv.startswith(tv_quote*3):
            assert tv.endswith(tv_quote*3), repr(tv)
            tv_quotes = tv_quote*3
            inner_s = tv[tx+3:-3]
        else:
            tv_quotes = tv_quote
            inner_s = tv[tx+1:-1]
        #
        # The remainder *might* have quotes. 
        # If so, we won't know where the matching quote/quotes are until later!
        rx = rx0 + len(r_prefix)
        if r.startswith(quotes, rx):
            r_quote = r[rx]
            r_quotes = r_quote*3 if r.startswith(r_quote*3) else r_quote
        else:
            r_quote = r_quotes = ''
        #
        # Quotes must match, if they exist in the remaining string.
        if r_quotes and r_quotes != tv_quotes: ### len(r_quotes) != len(tv_quotes):
            raise self.error(f"Unmatched quotes: tv_quotes: {tv_quotes!r} r_quotes {r_quotes!r}")
        #
        # Unescape escaped quotes.
        if r_quotes:
            inner_s = inner_s.replace('\\' + r_quote, r_quote)
            result = r_prefix + r_quotes + inner_s + r_quotes
        else:
            result = inner_s.replace('\\' + tv_quote, tv_quote)
        #
        # For joined strings it's possible to exhaust the
        # target string *without* exhausting the present token!
        #
        # We should only check that the remainder is a *prefix* of the result.
        remainder = r[:len(result)]
        if not result.startswith(remainder):
            raise self.error(f"Mismatch error: result: {result!r} r: {r[:len(result)]!r}")
        #
        # Now advance by the length of the remainder.
        self.target_index = rx0 + len(remainder) ### len(result)
        if trace:
            g.trace(f"string_index: {self.target_index} {token.value} ==> result: {result}\n")
        return result

        # This check is *too* strong.
            # if result != r[:len(result)]:
                # raise self.error(f"Mismatch error: result: {result!r} r: {r[:len(result)]!r}")
    #@+node:ekr.20191126074503.1: *6* tog.advance_str
    # For adjust_str_token.
    target_index = 0
    target_string = None
    ### continued_token = False

    def advance_str(self, target_s=None):
        """
        Advance over one or more 'string' tokens, and return them.
        
        A *single* Str node represents the concatenation of multiple *plain* strings.
        """
        trace = self.trace_mode
        #
        # Sanity checks.
        node_cn = self.node.__class__.__name__
        if target_s is None:
            if not isinstance(self.node, ast.Str):
                raise self.error(f"expecting ast.Str, got {node_cn}")
            target_s = self.node.s
        else:
            if not isinstance(self.node, ast.JoinedStr):
                raise self.error(f"expecting ast.JoinedStr, got {node_cn}")
        #
        # Set the ivars for adjust_str_token.
        self.target_index = 0
        self.target_string = target_s
        #
        # The accumulated results tells how much of the target string have been consumed.
        # This is used *only* to stop the scan of actual tokens.
        accumulated_results = []
        #
        # results is a list of one or more tokens to be consumed.
        results = []
        #
        # Make sure we make progress.
        start_index = self.string_index
        if trace:
            g.trace(f"START string_index: {self.string_index} target: {target_s}")

        def check_progress():
            if start_index >= self.string_index:
                raise self.error(
                    f"unchanged string index: {self.string_index} "
                    f"results: {results!r} target: {target_s!r}")
        #
        # Special case for empty target.
        if repr(target_s).lower().replace('"', "'") in ("''", "f''", "r''", "fr''", "rf''"):
            i = self.string_index
            i = self.next_str_index(i + 1)
            token = self.tokens[i]
            if trace:
                g.trace(f"Empty target: return string_index: {self.string_index} results: {[token]}")
            self.string_index = i
            check_progress()
            return [token]
        #
        # Scan 'string' tokens while the accumulated results are shorter than target_s.
        i = self.string_index
        while len(''.join(accumulated_results)) < len(target_s):
            if True and trace:
                g.trace(f"accumulated results: {accumulated_results!s}")
            i = self.next_str_index(i + 1)
            if i >= len(self.tokens):
                raise self.error(f"End of tokens looking for {target_s}")
            token = self.tokens[i]
            s = self.adjust_str_token(token)
            results.append(token)
            accumulated_results.append(s)
        results_s = ''.join(accumulated_results)
        #
        # The last token may extend the target string.
        # In that case, we just return.
        if results_s != target_s and results_s.startswith(target_s):
            self.string_index = i
            g.trace(f"EXTEND: i: {i} return {results_s!r}\n")
            return results
        #
        # Now we can make the stronger check.
        if results_s!= target_s:
            raise self.error(f"Looking for: {target_s!r}, found: {results_s!r}")
        #
        # Point the string index at the last scanned token.
        self.string_index = i
        check_progress()
        if trace:
            g.trace(f"END i: {i} return: {results_s!r}\n")
                # {accumulated_results()}
            g.printObj(results)
        return results
    #@+node:ekr.20191128135521.1: *6* tog.next_str_index
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
    #@+node:ekr.20191129102013.1: *6* tog.peek_next_str (new)
    def peek_next_str(self):
        """
        Return the next 'string' token, *without* updating the string index.
        """
        trace = False and self.trace_mode
        i = self.string_index
        i1 = i
        i = self.next_str_index(i+1)
        if i >= len(self.tokens):
            raise self.error(f"no token! {i1}..{i}")
        if trace:
            g.trace(f" {i1:>2}-->{i:<2} {self.tokens[i]}")
        return self.tokens[i]
    #@+node:ekr.20191113063144.51: *5* tog.Subscript
    # Subscript(expr value, slice slice, expr_context ctx)

    def do_Subscript(self, node):
        
        yield from self.gen(node.value)
        yield from self.gen_op('[')
        yield from self.gen(node.slice)
        yield from self.gen_op(']')
    #@+node:ekr.20191113063144.52: *5* tog.Tuple
    def do_Tuple(self, node):

        # no need to put commas.
        yield from self.gen_op('(')
        yield from self.gen(node.elts)
        yield from self.gen_op(')')
    #@+node:ekr.20191113063144.53: *4* tog: Operators
    #@+node:ekr.20191113063144.55: *5* tog.BinOp
    def do_BinOp(self, node):

        yield from self.gen(node.left)
        op_name = self.op_name(node.op)
        yield from self.gen_op(op_name)
        yield from self.gen(node.right)
        ###
            # if op_name.startswith(' '):
                # yield from self.gen_op(op_name.strip())
            # else:
                # yield from self.gen_op(op_name)
    #@+node:ekr.20191113063144.56: *5* tog.BoolOp
    # boolop = And | Or

    def do_BoolOp(self, node):
        
        # op.join(node.values)
        op_name = self.op_name(node.op)
        for i, z in enumerate(node.values):
            yield from self.gen(z)
            if i < len(node.values) - 1:
                yield from self.gen_name(op_name)
    #@+node:ekr.20191113063144.57: *5* tog.Compare
    # Compare(expr left, cmpop* ops, expr* comparators)

    def do_Compare(self, node):
        
        assert len(node.ops) == len(node.comparators)
        yield from self.gen(node.left)
        for i, z in enumerate(node.ops):
            op_name = self.op_name(node.ops[i])
            if op_name in ('not in', 'is not'):
                for z in op_name.split(' '):
                    yield from self.gen_name(z)
            elif op_name.isalpha():
                yield from self.gen_name(op_name)
            else:
                yield from self.gen_op(op_name)
            yield from self.gen(node.comparators[i])
    #@+node:ekr.20191113063144.58: *5* tog.UnaryOp
    def do_UnaryOp(self, node):

        op_name = self.op_name(node.op)
        if op_name.isalpha():
            yield from self.gen_name(op_name)
        else:
            yield from self.gen_op(op_name)
        yield from self.gen(node.operand)
    #@+node:ekr.20191113063144.59: *5* tog.IfExp (ternary operator)
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
    #@+node:ekr.20191113063144.60: *4* tog: Statements
    #@+node:ekr.20191113063144.61: *5* tog.AnnAssign
    # AnnAssign(expr target, expr annotation, expr? value, int simple)

    def do_AnnAssign(self, node):

        # {node.target}:{node.annotation}={node.value}\n'
        yield from self.gen(node.target)
        yield from self.gen_op(':')
        yield from self.gen(node.annotation)
        yield from self.gen_op('=')
        yield from self.gen(node.value)
        yield from self.gen_newline()
    #@+node:ekr.20191113063144.62: *5* tog.Assert
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
    #@+node:ekr.20191113063144.63: *5* tog.Assign
    def do_Assign(self, node):
            
        for z in node.targets:
            yield from self.gen(z)
            yield from self.gen_op('=')
        yield from self.gen(node.value)
        yield from self.gen_newline()
    #@+node:ekr.20191113063144.64: *5* tog.AsyncFor
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
            yield from self.gen_name('else')
            yield from self.gen_op(':')
            yield from self.gen(node.orelse)
        self.level -= 1
        yield from self.gen_newline()
    #@+node:ekr.20191113063144.65: *5* tog.AsyncWith
    def do_AsyncWith(self, node):
        
        yield from self.gen_name('async')
        yield from self.do_With(node)
    #@+node:ekr.20191113063144.66: *5* tog.AugAssign
    # AugAssign(expr target, operator op, expr value)

    def do_AugAssign(self, node):
        
        # %s%s=%s\n'
        op_name = self.op_name(node.op)
        yield from self.gen(node.target)
        yield from self.gen_op(op_name+'=')
        yield from self.gen(node.value)
        yield from self.gen_newline()
    #@+node:ekr.20191113063144.67: *5* tog.Await
    # Await(expr value)

    def do_Await(self, node):
        
        #'await %s\n'
        yield from self.gen_name('await')
        yield from self.gen(node.value)
        yield from self.gen_newline()
    #@+node:ekr.20191113063144.68: *5* tog.Break
    def do_Break(self, node):
        
        yield from self.gen_name('break')
        yield from self.gen_newline()
    #@+node:ekr.20191113063144.69: *5* tog.Continue
    def do_Continue(self, node):

        yield from self.gen_name('continue')
        yield from self.gen_newline()
    #@+node:ekr.20191113063144.70: *5* tog.Delete
    def do_Delete(self, node):

        # No need to put commas.
        yield from self.gen_name('del')
        yield from self.gen(node.targets)
        yield from self.gen_newline()
    #@+node:ekr.20191113063144.71: *5* tog.ExceptHandler
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
    #@+node:ekr.20191113063144.73: *5* tog.For
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
            yield from self.gen_name('else')
            yield from self.gen_op(':')
            yield from self.gen(node.orelse)
        self.level -= 1
    #@+node:ekr.20191113063144.74: *5* tog.Global
    def do_Global(self, node):

        yield from self.gen_name('global')
        yield from self.gen(node.names)
        yield from self.gen_newline()
    #@+node:ekr.20191113063144.75: *5* tog.If
    # If(expr test, stmt* body, stmt* orelse)

    def do_If(self, node):
        #@+<< do_If docstring >>
        #@+node:ekr.20191122222412.1: *6* << do_If docstring >>
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
        advance, peek = self.advance_if, self.peek_if
        # Consume the if-item.
        token_value = peek().value
        assert token_value in ('if', 'elif'), (token_value, g.callers())
        advance()
        # If or elif line...
            # if %s:\n
            # elif %s: \n
        yield from self.gen_name(token_value) ### 'if-???') ## token_value)
        yield from self.gen(node.test)
        yield from self.gen_op(':')
        yield from self.gen_newline()
        # Body...
        self.level += 1
        yield from self.gen(node.body)
        self.level -= 1
        # Else and elif clauses...
        if node.orelse:
            self.level += 1
            val = peek().value
            if val == 'else':
                # Consume the 'else' if-item.
                advance()
                yield from self.gen_name('else')
                yield from self.gen_op(':')
                yield from self.gen_newline()
                yield from self.gen(node.orelse)
            else:
                # Do *not* consume an if-item here.
                yield from self.gen(node.orelse)
            self.level -= 1
    #@+node:ekr.20191123152511.1: *5* tog.If: advance_if & peek_if ***
    if_index = None

    def is_if_token(self, token):
        return token.kind == 'name' and token.value in ('if', 'elif', 'else')
        
    def advance_if(self):
        ### if self.formatted_value_stack: g.trace('IN FORMATTED STRING')
        i = 0 if self.if_index is None else self.if_index + 1
        self.if_index = self.find_next_if_token(i)

    def find_next_if_token(self, i):
        while i < len(self.tokens):
            ### g.trace(f"      {i<3} {self.tokens[i]}")
            if self.is_if_token(self.tokens[i]):
                ### g.trace(f"FOUND {i<3} {self.tokens[i]}")
                break
            i += 1
        return i

    def peek_if(self):
        # Init, exactly once per tree traversal.
        if self.if_index is None:
            self.if_index = self.find_next_if_token(0)
        # IndexError is a sanity check.
        assert self.if_index < len(self.tokens), (self.if_index, g.callers())
        return self.tokens[self.if_index]
    #@+node:ekr.20191113063144.76: *5* tog.Import & helper
    def do_Import(self, node):
        
        yield from self.gen_name('import')
        for alias in node.names:
            yield from self.gen_name(alias.name)
            if alias.asname:
                yield from self.gen_name('as')
                yield from self.gen_name(alias.asname)
        yield from self.gen_newline()
    #@+node:ekr.20191113063144.77: *5* tog.ImportFrom
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
    #@+node:ekr.20191113063144.78: *5* tog.Nonlocal
    # Nonlocal(identifier* names)

    def do_Nonlocal(self, node):
        
        # nonlocal %s\n' % ','.join(node.names))
        # No need to put commas.
        yield from self.gen_name('nonlocal')
        yield from self.gen(node.names)
        yield from self.gen_newline()
    #@+node:ekr.20191113063144.79: *5* tog.Pass
    def do_Pass(self, node):
        
        yield from self.gen_name('pass')
        yield from self.gen_newline()
    #@+node:ekr.20191113063144.81: *5* tog.Raise
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
    #@+node:ekr.20191113063144.82: *5* tog.Return
    def do_Return(self, node):
        
        yield from self.gen_name('return')
        yield from self.gen(node.value)
        yield from self.gen_newline()
    #@+node:ekr.20191113063144.83: *5* tog.Starred
    # Starred(expr value, expr_context ctx)

    def do_Starred(self, node):

        yield from self.gen_op('*')
        yield from self.gen(node.value)
    #@+node:ekr.20191113063144.85: *5* tog.Try
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
        yield from self.gen(node.orelse)
        # Finally...
        if node.finalbody:
            yield from self.gen_name('finally')
            yield from self.gen_op(':')
            yield from self.gen_newline()
            yield from self.gen(node.finalbody)
        self.level -= 1
    #@+node:ekr.20191113063144.88: *5* tog.While
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
            yield from self.gen_name('else')
            yield from self.gen_op(':')
            yield from self.gen_newline()
            yield from self.gen(node.orelse)
        self.level -= 1
    #@+node:ekr.20191113063144.89: *5* tog.With
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
    #@+node:ekr.20191113063144.90: *5* tog.Yield
    def do_Yield(self, node):

        yield from self.gen_name('yield')
        if hasattr(node, 'value'):
            yield from self.gen(node.value)
        yield from self.gen_newline()
    #@+node:ekr.20191113063144.91: *5* tog.YieldFrom
    # YieldFrom(expr value)

    def do_YieldFrom(self, node):

        yield from self.gen_name('yield')
        yield from self.gen(node.value)
        yield from self.gen_newline()
    #@-others
#@+node:ekr.20141012064706.18390: ** class AstDumper
class AstDumper:
    """
    Return a formatted dump (a string) of the AST node.

    Adapted from Python's ast.dump.
    """

    #@+others
    #@+node:ekr.20191112033445.1: *3* dumper.brief_dump & helper
    def brief_dump(self, node):
        """Briefly show a tree, properly indented."""
        result = [self.show_header()]
        self.brief_dump_helper(node, 0, result)
        return ''.join(result)
    #@+node:ekr.20191125035321.1: *4* dumper.brief_dump_helper
    def brief_dump_helper(self, node, level, result):
        if node is None:
            return
        # Let block.
        indent = ' ' * 2 * level
        children = getattr(node, 'children', [])
        node_s = self.compute_node_string(node, level)
        # Dump...
        if isinstance(node, (list, tuple)):
            for z in node:
                self.brief_dump_helper(z, level, result)
        elif isinstance(node, str):
            result.append(f"{indent}{node.__class__.__name__:>8}:{node}\n")
        elif isinstance(node, ast.AST):
            # Node and parent.
            result.append(node_s)
            # Children.
            for z in children:
                self.brief_dump_helper(z, level+1, result)
        else:
            result.append(node_s)
    #@+node:ekr.20191125033744.1: *3* dumper.brief_dump_one_node
    def brief_dump_one_node(self, node, level):
        
        indent = ' ' * 2 * level
        result = [] # [self.show_header()]
        node_s = self.compute_node_string(node, level).rstrip()
        if isinstance(node, str):
            result.append(f"{indent}{node.__class__.__name__:>8}:{node}")
        elif isinstance(node, ast.AST):
            # Node and parent.
            result.append(node_s)
        else:
            result.append(f"{indent}OOPS: {node.__class__.__name__}")
        return ''.join(result)
    #@+node:ekr.20191125035600.1: *3* dumper.compute_node_string & helpers
    def compute_node_string(self, node, level):
        """Return a string summarizing the node."""
        index_ivar = 'node_index'
        indent = ' ' * 2 * level
        parent = getattr(node, 'parent', None)
        node_id = getattr(node, index_ivar, '??')
        parent_id = getattr(parent, index_ivar, '??')
        parent_s = f"{parent_id:<3} {parent.__class__.__name__}" if parent else ''
        class_name = node.__class__.__name__
        descriptor_s = class_name + self.show_fields(class_name, node, 24)
        tokens_s = self.show_tokens(node, 70, 100)
        lines = self.show_line_range(node)
        full_s1 = f"{parent_s:<16} {lines:<8} {node_id:<3} {indent}{descriptor_s} "
        node_s =  f"{full_s1:<70} {tokens_s}\n"
        return node_s
    #@+node:ekr.20191113223424.1: *4* dumper.show_fields
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
            if True:
                g.printObj(results, tag='AstDumper.show_fields: JoinedStr')
            # result = '::'.join(results)
            # val = f": values={result}"
            val = f" {strings} str, {fstrings} f-str"
        elif class_name == 'Name':
            val = f": id={node.id!r}"
        elif class_name == 'NameConstant':
            val = f": value={node.value!r}"
        elif class_name == 'Num':
            val = f": n={node.n}"
            # val = ': ' + ','.join(aList)
        elif class_name == 'Str':
            val = f": s={node.s!r}"
        elif class_name in ('AugAssign', 'BinOp', 'BoolOp', 'UnaryOp'): # IfExp
            name = node.op.__class__.__name__
            val = f": {_op_names.get(name, name)}"
        elif class_name == 'Compare':
            ops = ','.join([_op_names.get(z, repr(z)) for z in node.ops])
            val = f": ops={ops}"
        return truncate(val, truncate_n)
        
    #@+node:ekr.20191114054726.1: *4* dumper.show_line_range
    def show_line_range(self, node):
        
        token_list = getattr(node, 'token_list', [])
        if not token_list:
            return ''
        min_ = min([z.line_number for z in token_list])
        max_ = max([z.line_number for z in token_list])
        return f"{min_}" if min_ == max_ else f"{min_}..{max_}"
    #@+node:ekr.20191113223425.1: *4* dumper.show_tokens
    def show_tokens(self, node, n, m):
        """
        Return a string showing node.token_list.
        
        Split the result if n + len(result) > m
        """
        token_list = getattr(node, 'token_list', [])
        if 0: # Too brief.
            return ','.join([z.kind for z in token_list])
        result = []
        for z in token_list:
            if z.kind == 'comment':
                val = truncate(z.value,10) # Short is good.
                result.append(f"{z.kind}({val})")
            elif z.kind == 'name':
                val = truncate(z.value,20)
                result.append(f"{z.kind}({val})")
            elif z.kind == 'newline':
                result.append(f"{z.kind.strip()}({z.line_number}:{len(z.line)})")
            elif z.kind == 'number':
                result.append(f"{z.kind}({z.value})")
            elif z.kind == 'op':
                result.append(f"{z.kind}{z.value}")
            elif z.kind == 'string':
                val = truncate(z.value,20)
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
    #@+node:ekr.20191110165235.5: *3* dumper.show_header
    def show_header(self):
        """Return a header string, but only the fist time."""
        return (
            f"{'parent':<16} {'lines':<8} {'node':<44} {'tokens'}\n"
            f"{'======':<16} {'=====':<8} {'====':<44} {'======'}\n")
    #@+node:ekr.20141012064706.18392: *3* dumper.dump & helper
    annotate_fields=False
    include_attributes = False
    indent_ws = ' '

    def dump(self, node, level=0):

        sep1 = f'\n%s' % (self.indent_ws * (level + 1))
        if isinstance(node, ast.AST):
            fields = [(a, self.dump(b, level+1)) for a, b in self.get_fields(node)]
            if self.include_attributes and node._attributes:
                fields.extend([(a, self.dump(getattr(node, a), level+1))
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
                [f'%s%s' % (sep, self.dump(z, level+1)) for z in node])
        return repr(node)
    #@+node:ekr.20141012064706.18393: *4* dumper.get_fields
    def get_fields(self, node):
        
        

        return (
            (a, b) for a, b in ast.iter_fields(node)
                if a not in ['ctx',] and b not in (None, [])
        )
    #@-others
#@+node:ekr.20141012064706.18471: ** class AstFullTraverser
class AstFullTraverser:
    """
    A fast traverser for AST trees: it visits every node (except node.ctx fields).

    Sets .context and .parent ivars before visiting each node.
    """

    def __init__(self):
        """Ctor for AstFullTraverser class."""
        self.context = None
        self.level = 0  # The context level only.
        self.parent = None

    #@+others
    #@+node:ekr.20141012064706.18472: *3* ft.contexts
    #@+node:ekr.20141012064706.18473: *4* ft.ClassDef
    # 2: ClassDef(identifier name, expr* bases, stmt* body, expr* decorator_list)
    # 3: ClassDef(identifier name, expr* bases,
    #             keyword* keywords, expr? starargs, expr? kwargs
    #             stmt* body, expr* decorator_list)
    #
    # keyword arguments supplied to call (NULL identifier for **kwargs)
    # keyword = (identifier? arg, expr value)

    def do_ClassDef(self, node, visit_body=True):
        old_context = self.context
        self.context = node
        self.level += 1
        for z in node.decorator_list:
            self.visit(z)
        for z in node.bases:
            self.visit(z)
        if getattr(node, 'keywords', None):  # Python 3
            for keyword in node.keywords:
                self.visit(keyword.value)
        if getattr(node, 'starargs', None):  # Python 3
            self.visit(node.starargs)
        if getattr(node, 'kwargs', None):  # Python 3
            self.visit(node.kwargs)
        if visit_body:
            for z in node.body:
                self.visit(z)
        self.level -= 1
        self.context = old_context
    #@+node:ekr.20141012064706.18474: *4* ft.FunctionDef
    # 2: FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list)
    # 3: FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list,
    #                expr? returns)

    def do_FunctionDef(self, node, visit_body=True):

        old_context = self.context
        self.context = node
        self.level += 1
        # Visit the tree in token order.
        for z in node.decorator_list:
            self.visit(z)
        assert isinstance(node.name, str)
        self.visit(node.args)
        if getattr(node, 'returns', None):  # Python 3.
            self.visit(node.returns)
        if visit_body:
            for z in node.body:
                self.visit(z)
        self.level -= 1
        self.context = old_context

    do_AsyncFunctionDef = do_FunctionDef
    #@+node:ekr.20141012064706.18475: *4* ft.Interactive
    def do_Interactive(self, node):
        assert False, 'Interactive context not supported'
    #@+node:ekr.20141012064706.18476: *4* ft.Lambda
    # Lambda(arguments args, expr body)

    def do_Lambda(self, node):
        old_context = self.context
        self.context = node
        self.visit(node.args)
        self.visit(node.body)
        self.context = old_context
    #@+node:ekr.20141012064706.18477: *4* ft.Module
    def do_Module(self, node):
        self.context = node
        for z in node.body:
            self.visit(z)
        self.context = None
    #@+node:ekr.20141012064706.18478: *3* ft.ctx nodes
    # Not used in this class, but may be called by subclasses.

    def do_AugLoad(self, node):
        pass

    def do_Del(self, node):
        pass

    def do_Load(self, node):
        pass

    def do_Param(self, node):
        pass

    def do_Store(self, node):
        pass
    #@+node:ekr.20171214200319.1: *3* ft.format
    def format(self, node, level, *args, **keys):
        """Format the node and possibly its descendants, depending on args."""
        s = AstFormatter().format(node, level, *args, **keys)
        return s.rstrip()
    #@+node:ekr.20141012064706.18480: *3* ft.operators & operands
    #@+node:ekr.20160521102250.1: *4* ft.op_name
    def op_name(self, node, strict=True):
        """Return the print name of an operator node."""
        name = _op_names.get(node.__class__.__name__, f'<%s>' % node.__class__.__name__)
        if strict:
            assert name, node.__class__.__name__
        return name
    #@+node:ekr.20141012064706.18482: *4* ft.arguments & arg
    # 2: arguments = (
    # expr* args,
    #   identifier? vararg,
    #   identifier? kwarg,
    #   expr* defaults)
    # 3: arguments = (
    #   arg*  args,
    #   arg? vararg,
    #   arg* kwonlyargs,
    #   expr* kw_defaults,
    #   arg? kwarg,
    #   expr* defaults)

    def do_arguments(self, node):

        for z in node.args:
            self.visit(z)
        if getattr(node, 'vararg', None):
            # An identifier in Python 2.
            self.visit(node.vararg)
        if getattr(node, 'kwarg', None):
            # An identifier in Python 2.
            self.visit_list(node.kwarg)
        if getattr(node, 'kwonlyargs', None):  # Python 3.
            self.visit_list(node.kwonlyargs)
        if getattr(node, 'kw_defaults', None):  # Python 3.
            self.visit_list(node.kw_defaults)
        for z in node.defaults:
            self.visit(z)

    # 3: arg = (identifier arg, expr? annotation)

    def do_arg(self, node):
        if getattr(node, 'annotation', None):
            self.visit(node.annotation)
    #@+node:ekr.20141012064706.18483: *4* ft.Attribute
    # Attribute(expr value, identifier attr, expr_context ctx)

    def do_Attribute(self, node):
        self.visit(node.value)
        # self.visit(node.ctx)
    #@+node:ekr.20141012064706.18484: *4* ft.BinOp
    # BinOp(expr left, operator op, expr right)

    def do_BinOp(self, node):
        self.visit(node.left)
        # self.op_name(node.op)
        self.visit(node.right)
    #@+node:ekr.20141012064706.18485: *4* ft.BoolOp
    # BoolOp(boolop op, expr* values)

    def do_BoolOp(self, node):
        for z in node.values:
            self.visit(z)
    #@+node:ekr.20141012064706.18481: *4* ft.Bytes
    def do_Bytes(self, node):
        pass  # Python 3.x only.
    #@+node:ekr.20141012064706.18486: *4* ft.Call
    # Call(expr func, expr* args, keyword* keywords, expr? starargs, expr? kwargs)

    def do_Call(self, node):
        # Call the nodes in token order.
        self.visit(node.func)
        for z in node.args:
            self.visit(z)
        for z in node.keywords:
            self.visit(z)
        if getattr(node, 'starargs', None):
            self.visit(node.starargs)
        if getattr(node, 'kwargs', None):
            self.visit(node.kwargs)
    #@+node:ekr.20141012064706.18487: *4* ft.Compare
    # Compare(expr left, cmpop* ops, expr* comparators)

    def do_Compare(self, node):
        # Visit all nodes in token order.
        self.visit(node.left)
        assert len(node.ops) == len(node.comparators)
        for i in range(len(node.ops)):
            self.visit(node.ops[i])
            self.visit(node.comparators[i])
        # self.visit(node.left)
        # for z in node.comparators:
            # self.visit(z)
    #@+node:ekr.20150526140323.1: *4* ft.Compare ops
    # Eq | NotEq | Lt | LtE | Gt | GtE | Is | IsNot | In | NotIn

    def do_Eq(self, node): pass

    def do_Gt(self, node): pass

    def do_GtE(self, node): pass

    def do_In(self, node): pass

    def do_Is(self, node): pass

    def do_IsNot(self, node): pass

    def do_Lt(self, node): pass

    def do_LtE(self, node): pass

    def do_NotEq(self, node): pass

    def do_NotIn(self, node): pass
    #@+node:ekr.20141012064706.18488: *4* ft.comprehension
    # comprehension (expr target, expr iter, expr* ifs)

    def do_comprehension(self, node):
        self.visit(node.target)  # A name.
        self.visit(node.iter)  # An attribute.
        for z in node.ifs:
            self.visit(z)
    #@+node:ekr.20170721073315.1: *4* ft.Constant (Python 3.6+)
    def do_Constant(self, node):  # Python 3.6+ only.
        pass
    #@+node:ekr.20141012064706.18489: *4* ft.Dict
    # Dict(expr* keys, expr* values)

    def do_Dict(self, node):
        # Visit all nodes in token order.
        assert len(node.keys) == len(node.values)
        for i in range(len(node.keys)):
            self.visit(node.keys[i])
            self.visit(node.values[i])
    #@+node:ekr.20160523094910.1: *4* ft.DictComp
    # DictComp(expr key, expr value, comprehension* generators)

    def do_DictComp(self, node):
        # EKR: visit generators first, then value.
        for z in node.generators:
            self.visit(z)
        self.visit(node.value)
        self.visit(node.key)
    #@+node:ekr.20150522081707.1: *4* ft.Ellipsis
    def do_Ellipsis(self, node):
        pass
    #@+node:ekr.20141012064706.18490: *4* ft.Expr
    # Expr(expr value)

    def do_Expr(self, node):
        self.visit(node.value)
    #@+node:ekr.20141012064706.18491: *4* ft.Expression
    def do_Expression(self, node):
        """An inner expression"""
        self.visit(node.body)
    #@+node:ekr.20141012064706.18492: *4* ft.ExtSlice
    def do_ExtSlice(self, node):
        for z in node.dims:
            self.visit(z)
    #@+node:ekr.20170721075714.1: *4* ft.FormattedValue (Python 3.6+)
    # FormattedValue(expr value, int? conversion, expr? format_spec)

    def do_FormattedValue(self, node):  # Python 3.6+ only.
        self.visit(node.value)
        if node.conversion:
            self.visit(node.conversion)
        if node.format_spec:
            self.visit(node.format_spec)
    #@+node:ekr.20141012064706.18493: *4* ft.GeneratorExp
    # GeneratorExp(expr elt, comprehension* generators)

    def do_GeneratorExp(self, node):
        self.visit(node.elt)
        for z in node.generators:
            self.visit(z)
    #@+node:ekr.20141012064706.18494: *4* ft.ifExp (ternary operator)
    # IfExp(expr test, expr body, expr orelse)

    def do_IfExp(self, node):
        self.visit(node.body)
        self.visit(node.test)
        self.visit(node.orelse)
    #@+node:ekr.20141012064706.18495: *4* ft.Index
    def do_Index(self, node):
        self.visit(node.value)
    #@+node:ekr.20170721080935.1: *4* ft.JoinedStr (Python 3.6+)
    # JoinedStr(expr* values)

    def do_JoinedStr(self, node):
        for value in node.values or []:
            self.visit(value)
    #@+node:ekr.20141012064706.18496: *4* ft.keyword
    # keyword = (identifier arg, expr value)

    def do_keyword(self, node):
        # node.arg is a string.
        self.visit(node.value)
    #@+node:ekr.20141012064706.18497: *4* ft.List & ListComp
    # List(expr* elts, expr_context ctx)

    def do_List(self, node):
        for z in node.elts:
            self.visit(z)
        # self.visit(node.ctx)
    # ListComp(expr elt, comprehension* generators)

    def do_ListComp(self, node):
        self.visit(node.elt)
        for z in node.generators:
            self.visit(z)
    #@+node:ekr.20141012064706.18498: *4* ft.Name (revise)
    # Name(identifier id, expr_context ctx)

    def do_Name(self, node):
        # self.visit(node.ctx)
        pass

    def do_NameConstant(self, node):  # Python 3 only.
        pass
        # s = repr(node.value)
        # return 'bool' if s in ('True', 'False') else s
    #@+node:ekr.20150522081736.1: *4* ft.Num
    def do_Num(self, node):
        pass  # Num(object n) # a number as a PyObject.
    #@+node:ekr.20141012064706.18499: *4* ft.Repr
    # Python 2.x only
    # Repr(expr value)

    def do_Repr(self, node):
        self.visit(node.value)
    #@+node:ekr.20160523094939.1: *4* ft.Set
    # Set(expr* elts)

    def do_Set(self, node):
        for z in node.elts:
            self.visit(z)

    #@+node:ekr.20160523095142.1: *4* ft.SetComp
    # SetComp(expr elt, comprehension* generators)

    def do_SetComp(self, node):
        # EKR: visit generators first.
        for z in node.generators:
            self.visit(z)
        self.visit(node.elt)
    #@+node:ekr.20141012064706.18500: *4* ft.Slice
    def do_Slice(self, node):
        if getattr(node, 'lower', None):
            self.visit(node.lower)
        if getattr(node, 'upper', None):
            self.visit(node.upper)
        if getattr(node, 'step', None):
            self.visit(node.step)
    #@+node:ekr.20150522081748.1: *4* ft.Str
    def do_Str(self, node):
        pass  # represents a string constant.
    #@+node:ekr.20141012064706.18501: *4* ft.Subscript
    # Subscript(expr value, slice slice, expr_context ctx)

    def do_Subscript(self, node):
        self.visit(node.value)
        self.visit(node.slice)
        # self.visit(node.ctx)
    #@+node:ekr.20141012064706.18502: *4* ft.Tuple
    # Tuple(expr* elts, expr_context ctx)

    def do_Tuple(self, node):
        for z in node.elts:
            self.visit(z)
        # self.visit(node.ctx)
    #@+node:ekr.20141012064706.18503: *4* ft.UnaryOp
    # UnaryOp(unaryop op, expr operand)

    def do_UnaryOp(self, node):
        # self.op_name(node.op)
        self.visit(node.operand)
    #@+node:ekr.20141012064706.18504: *3* ft.statements
    #@+node:ekr.20141012064706.18505: *4* ft.alias
    # identifier name, identifier? asname)

    def do_alias(self, node):
        # self.visit(node.name)
        # if getattr(node,'asname')
            # self.visit(node.asname)
        pass
    #@+node:ekr.20170721074528.1: *4* ft.AnnAssign
    # AnnAssign(expr target, expr annotation, expr? value, int simple)

    def do_AnnAssign(self, node):
        self.visit(node.target)
        self.visit(node.annotation)
        self.visit(node.value)
    #@+node:ekr.20141012064706.18506: *4* ft.Assert
    # Assert(expr test, expr? msg)

    def do_Assert(self, node):
        self.visit(node.test)
        if node.msg:
            self.visit(node.msg)
    #@+node:ekr.20141012064706.18507: *4* ft.Assign
    # Assign(expr* targets, expr value)

    def do_Assign(self, node):
        for z in node.targets:
            self.visit(z)
        self.visit(node.value)
    #@+node:ekr.20141012064706.18508: *4* ft.AugAssign
    # AugAssign(expr target, operator op, expr value)

    def do_AugAssign(self, node):

        self.visit(node.target)
        self.visit(node.value)
    #@+node:ekr.20141012064706.18509: *4* ft.Break
    def do_Break(self, tree):
        pass
    #@+node:ekr.20141012064706.18510: *4* ft.Continue
    def do_Continue(self, tree):
        pass
    #@+node:ekr.20141012064706.18511: *4* ft.Delete
    # Delete(expr* targets)

    def do_Delete(self, node):
        for z in node.targets:
            self.visit(z)
    #@+node:ekr.20141012064706.18512: *4* ft.ExceptHandler
    # Python 2: ExceptHandler(expr? type, expr? name, stmt* body)
    # Python 3: ExceptHandler(expr? type, identifier? name, stmt* body)

    def do_ExceptHandler(self, node):

        if node.type:
            self.visit(node.type)
        if node.name and isinstance(node.name, ast.Name):
            self.visit(node.name)
        for z in node.body:
            self.visit(z)
    #@+node:ekr.20141012064706.18513: *4* ft.Exec
    # Python 2.x only
    # Exec(expr body, expr? globals, expr? locals)

    def do_Exec(self, node):
        self.visit(node.body)
        if getattr(node, 'globals', None):
            self.visit(node.globals)
        if getattr(node, 'locals', None):
            self.visit(node.locals)
    #@+node:ekr.20141012064706.18514: *4* ft.For & AsyncFor
    # For(expr target, expr iter, stmt* body, stmt* orelse)

    def do_For(self, node):
        self.visit(node.target)
        self.visit(node.iter)
        for z in node.body:
            self.visit(z)
        for z in node.orelse:
            self.visit(z)

    do_AsyncFor = do_For
    #@+node:ekr.20141012064706.18515: *4* ft.Global
    # Global(identifier* names)

    def do_Global(self, node):
        pass
    #@+node:ekr.20141012064706.18516: *4* ft.If
    # If(expr test, stmt* body, stmt* orelse)

    def do_If(self, node):
        self.visit(node.test)
        for z in node.body:
            self.visit(z)
        for z in node.orelse:
            self.visit(z)
    #@+node:ekr.20141012064706.18517: *4* ft.Import & ImportFrom
    # Import(alias* names)

    def do_Import(self, node):
        pass
    # ImportFrom(identifier? module, alias* names, int? level)

    def do_ImportFrom(self, node):
        # for z in node.names:
            # self.visit(z)
        pass
    #@+node:ekr.20160317051434.2: *4* ft.Nonlocal (Python 3)
    # Nonlocal(identifier* names)

    def do_Nonlocal(self, node):

        pass
    #@+node:ekr.20141012064706.18518: *4* ft.Pass
    def do_Pass(self, node):
        pass
    #@+node:ekr.20141012064706.18519: *4* ft.Print
    # Python 2.x only
    # Print(expr? dest, expr* values, bool nl)

    def do_Print(self, node):
        if getattr(node, 'dest', None):
            self.visit(node.dest)
        for expr in node.values:
            self.visit(expr)
    #@+node:ekr.20141012064706.18520: *4* ft.Raise
    # Raise(expr? type, expr? inst, expr? tback)    Python 2
    # Raise(expr? exc, expr? cause)                 Python 3

    def do_Raise(self, node):

        for attr in ('exc', 'cause'):
            if getattr(node, attr, None):
                self.visit(getattr(node, attr))
    #@+node:ekr.20141012064706.18521: *4* ft.Return
    # Return(expr? value)

    def do_Return(self, node):
        if node.value:
            self.visit(node.value)
    #@+node:ekr.20160317051434.3: *4* ft.Starred (Python 3)
    # Starred(expr value, expr_context ctx)

    def do_Starred(self, node):

        self.visit(node.value)
    #@+node:ekr.20141012064706.18522: *4* ft.Try (Python 3)
    # Python 3 only: Try(stmt* body, excepthandler* handlers, stmt* orelse, stmt* finalbody)

    def do_Try(self, node):
        for z in node.body:
            self.visit(z)
        for z in node.handlers:
            self.visit(z)
        for z in node.orelse:
            self.visit(z)
        for z in node.finalbody:
            self.visit(z)
    #@+node:ekr.20141012064706.18523: *4* ft.TryExcept
    # TryExcept(stmt* body, excepthandler* handlers, stmt* orelse)

    def do_TryExcept(self, node):
        for z in node.body:
            self.visit(z)
        for z in node.handlers:
            self.visit(z)
        for z in node.orelse:
            self.visit(z)
    #@+node:ekr.20141012064706.18524: *4* ft.TryFinally
    # TryFinally(stmt* body, stmt* finalbody)

    def do_TryFinally(self, node):
        for z in node.body:
            self.visit(z)
        for z in node.finalbody:
            self.visit(z)
    #@+node:ekr.20141012064706.18525: *4* ft.While
    # While(expr test, stmt* body, stmt* orelse)

    def do_While(self, node):
        self.visit(node.test)  # Bug fix: 2013/03/23.
        for z in node.body:
            self.visit(z)
        for z in node.orelse:
            self.visit(z)
    #@+node:ekr.20141012064706.18526: *4* ft.With & AsyncWith
    # 2:  With(expr context_expr, expr? optional_vars,
    #          stmt* body)
    # 3:  With(withitem* items,
    #          stmt* body)
    # withitem = (expr context_expr, expr? optional_vars)

    def do_With(self, node):
        if getattr(node, 'context_expr', None):
            self.visit(node.context_expr)
        if getattr(node, 'optional_vars', None):
            self.visit(node.optional_vars)
        if getattr(node, 'items', None):  # Python 3.
            for item in node.items:
                self.visit(item.context_expr)
                if getattr(item, 'optional_vars', None):
                    try:
                        for z in item.optional_vars:
                            self.visit(z)
                    except TypeError:  # Not iterable.
                        self.visit(item.optional_vars)
        for z in node.body:
            self.visit(z)

    do_AsyncWith = do_With
    #@+node:ekr.20141012064706.18527: *4* ft.Yield, YieldFrom & Await (Python 3)
    # Yield(expr? value)
    # Await(expr value)         Python 3 only.
    # YieldFrom (expr value)    Python 3 only.

    def do_Yield(self, node):
        if node.value:
            self.visit(node.value)

    do_Await = do_YieldFrom = do_Yield
    #@+node:ekr.20141012064706.18528: *3* ft.visit (supports before_* & after_*)
    def visit(self, node):
        """Visit a *single* ast node.  Visitors are responsible for visiting children!"""
        name = node.__class__.__name__
        assert isinstance(node, ast.AST), repr(node)
        # Visit the children with the new parent.
        old_parent = self.parent
        self.parent = node
        before_method = getattr(self, 'before_'+name, None)
        if before_method:
            before_method(node)
        do_method = getattr(self, 'do_'+name, None)
        if do_method:
            val = do_method(node)
        after_method = getattr(self, 'after_'+name, None)
        if after_method:
            after_method(node)
        self.parent = old_parent
        return val

    def visit_children(self, node):
        assert False, 'must visit children explicitly'
    #@+node:ekr.20141012064706.18529: *3* ft.visit_list
    def visit_list(self, aList):
        """Visit all ast nodes in aList or ast.node."""
        if isinstance(aList, (list, tuple)):
            for z in aList:
                self.visit(z)
            return None
        assert isinstance(aList, ast.AST), repr(aList)
        return self.visit(aList)
    #@-others
#@+node:ekr.20141012064706.18530: ** class AstPatternFormatter (AstFormatter)
class AstPatternFormatter(AstFormatter):
    """
    A subclass of AstFormatter that replaces values of constants by Bool,
    Bytes, Int, Name, Num or Str.
    """
    # No ctor.
    #@+others
    #@+node:ekr.20141012064706.18531: *3* Constants & Name
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
#@+node:ekr.20150722204300.1: ** class HTMLReportTraverser
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
    #@+node:ekr.20150722204300.2: *3* rt.__init__
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
    #@+node:ekr.20150722204300.3: *4* define_html_header
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
    #@+node:ekr.20150723094359.1: *3* rt.code generators
    #@+node:ekr.20150723100236.1: *4* rt.blank
    def blank(self):
        """Insert a single blank."""
        self.clean(' ')
        if self.code_list[-1] not in ' \n':
            self.gen(' ')
    #@+node:ekr.20150723100208.1: *4* rt.clean
    def clean(self, s):
        """Remove s from the code list."""
        s2 = self.code_list[-1]
        if s2 == s:
            self.code_list.pop()
    #@+node:ekr.20150723105702.1: *4* rt.colon
    def colon(self):

        self.clean('\n')
        self.clean(' ')
        self.clean('\n')
        self.gen(':')
    #@+node:ekr.20150723100346.1: *4* rt.comma & clean_comma
    def comma(self):

        self.clean(' ')
        self.gen(', ')

    def clean_comma(self):

        self.clean(', ')
    #@+node:ekr.20150722204300.21: *4* rt.doc
    # Called by ClassDef & FunctionDef visitors.

    def doc(self, node):
        doc = ast.get_docstring(node)
        if doc:
            self.docstring(doc)
            self.last_doc = doc  # Attempt to suppress duplicate.
    #@+node:ekr.20150722204300.22: *4* rt.docstring
    def docstring(self, s):

        import textwrap
        self.gen("<pre class='doc'>")
        self.gen('"""')
        self.gen(self.text(textwrap.dedent(s.replace('"""', '\\"\\"\\"'))))
        self.gen('"""')
        self.gen("</pre>")
    #@+node:ekr.20150722211115.1: *4* rt.gen
    def gen(self, s):
        """Append s to the global code list."""
        if s:
            self.code_list.append(s)
    #@+node:ekr.20150722204300.23: *4* rt.keyword (code generator)
    def keyword(self, name):

        self.blank()
        self.span('keyword')
        self.gen(name)
        self.end_span('keyword')
        self.blank()
    #@+node:ekr.20150722204300.24: *4* rt.name
    def name(self, name):

        # Div would put each name on a separate line.
        # span messes up whitespace, for now.
        # self.span('name')
        self.gen(name)
        # self.end_span('name')
    #@+node:ekr.20150723100417.1: *4* rt.newline
    def newline(self):

        self.clean(' ')
        self.clean('\n')
        self.clean(' ')
        self.gen('\n')
    #@+node:ekr.20150722204300.26: *4* rt.op
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
    #@+node:ekr.20150723105951.1: *4* rt.op_name
    #@@nobeautify

    def op_name (self, node,strict=True):
        """Return the print name of an operator node."""
        d = {
            # Binary operators.
            'Add':       '+',
            'BitAnd':    '&',
            'BitOr':     '|',
            'BitXor':    '^',
            'Div':       '/',
            'FloorDiv':  '//',
            'LShift':    '<<',
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
        kind = node.__class__.__name__
        name = d.get(kind, kind)
        if strict: assert name, kind
        return name
    #@+node:ekr.20160315184954.1: *4* rt.string (code generator)
    def string(self, s):

        import xml.sax.saxutils as saxutils
        s = repr(s.strip().strip())
        s = saxutils.escape(s)
        self.gen(s)
    #@+node:ekr.20150722204300.27: *4* rt.simple_statement
    def simple_statement(self, name):

        class_name = f'%s nowrap' % name
        self.div(class_name)
        self.keyword(name)
        self.end_div(class_name)
    #@+node:ekr.20150722204300.16: *3* rt.html helpers
    #@+node:ekr.20150722204300.17: *4* rt.attr & text
    def attr(self, s):
        return self.text(s).replace("'", "&apos;").replace('"', "&quot;")

    def text(self, s):
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    #@+node:ekr.20150722204300.18: *4* rt.br
    def br(self):
        return '\n<br />'
    #@+node:ekr.20150722204300.19: *4* rt.comment
    def comment(self, comment):

        self.span('comment')
        self.gen('# '+comment)
        self.end_span('comment')
        self.newline()
    #@+node:ekr.20150722204300.20: *4* rt.div
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
    #@+node:ekr.20150722222149.1: *4* rt.div_body
    def div_body(self, aList):
        if aList:
            self.div_list('body', aList)
    #@+node:ekr.20150722221101.1: *4* rt.div_list & div_node
    def div_list(self, class_name, aList, sep=None):

        self.div(class_name)
        self.visit_list(aList, sep=sep)
        self.end_div(class_name)

    def div_node(self, class_name, node):

        self.div(class_name)
        self.visit(node)
        self.end_div(class_name)
    #@+node:ekr.20150723095033.1: *4* rt.end_div
    def end_div(self, class_name):

        if class_name in self.enable_list:
            # self.newline()
            self.gen('</div>')
            # self.newline()
        class_name2 = self.div_stack.pop()
        assert class_name2 == class_name, (class_name2, class_name)
    #@+node:ekr.20150723095004.1: *4* rt.end_span
    def end_span(self, class_name):

        if class_name in self.enable_list:
            self.gen('</span>')
            self.newline()
        class_name2 = self.div_stack.pop()
        assert class_name2 == class_name, (class_name2, class_name)
    #@+node:ekr.20150722221408.1: *4* rt.keyword_colon
    # def keyword_colon(self, keyword):

        # self.keyword(keyword)
        # self.colon()
    #@+node:ekr.20150722204300.5: *4* rt.link
    def link(self, class_name, href, a_text):

        return f"<a class='%s' href='%s'>%s</a>" % (
            class_name, href, a_text)
    #@+node:ekr.20150722204300.6: *4* rt.module_link
    def module_link(self, module_name, classes=None):

        return self.link(
            class_name=classes or 'name',
            href=f'%s.xhtml' % module_name,
            a_text=self.text(module_name))
    #@+node:ekr.20150722204300.7: *4* rt.name_link
    def name_link(self, module_name, full_name, name, classes=None):

        return self.link(
            class_name=classes or "specific-ref",
            href=f'%s.xhtml#%s' % (module_name, self.attr(full_name)),
            a_text=self.text(name))
    #@+node:ekr.20150722204300.8: *4* rt.object_name_ref
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
    #@+node:ekr.20150722204300.9: *4* rt.popup
    def popup(self, classes, aList):

        self.span_list(classes or 'popup', aList)
    #@+node:ekr.20150722204300.28: *4* rt.span
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
    #@+node:ekr.20150722224734.1: *4* rt.span_list & span_node
    def span_list(self, class_name, aList, sep=None):

        self.span(class_name)
        self.visit_list(aList, sep=sep)
        self.end_span(class_name)

    def span_node(self, class_name, node):

        self.span(class_name)
        self.visit(node)
        self.end_span(class_name)
    #@+node:ekr.20150722204300.10: *4* rt.summary_link
    def summary_link(self, module_name, full_name, name, classes=None):

        return self.name_link(
            f"{module_name}-summary", full_name, name, classes)
    #@+node:ekr.20160315161259.1: *3* rt.main
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
    #@+node:ekr.20150722204300.44: *3* rt.visit
    def visit(self, node):
        """Walk a tree of AST nodes."""
        assert isinstance(node, ast.AST), node.__class__.__name__
        method_name = 'do_' + node.__class__.__name__
        method = getattr(self, method_name)
        method(node)
    #@+node:ekr.20150722204300.45: *3* rt.visit_list
    def visit_list(self, aList, sep=None):
        # pylint: disable=arguments-differ
        if aList:
            for z in aList:
                self.visit(z)
                self.gen(sep)
            self.clean(sep)
    #@+node:ekr.20150722204300.46: *3* rt.visitors
    #@+node:ekr.20170721074613.1: *4* rt.AnnAssign
    # AnnAssign(expr target, expr annotation, expr? value, int simple)

    def do_AnnAssign(self, node):

        self.div('statement')
        self.visit(node.target)
        self.op('=:', leading=True, trailing=True)
        self.visit(node.annotation)
        self.blank()
        self.visit(node.value)
        self.end_div('statement')
    #@+node:ekr.20150722204300.49: *4* rt.Assert
    # Assert(expr test, expr? msg)

    def do_Assert(self, node):

        self.div('statement')
        self.keyword("assert")
        self.visit(node.test)
        if node.msg:
            self.comma()
            self.visit(node.msg)
        self.end_div('statement')
    #@+node:ekr.20150722204300.50: *4* rt.Assign
    def do_Assign(self, node):

        self.div('statement')
        for z in node.targets:
            self.visit(z)
            self.op('=', leading=True, trailing=True)
        self.visit(node.value)
        self.end_div('statement')
    #@+node:ekr.20150722204300.51: *4* rt.Attribute
    # Attribute(expr value, identifier attr, expr_context ctx)

    def do_Attribute(self, node):

        self.visit(node.value)
        self.gen('.')
        self.gen(node.attr)
    #@+node:ekr.20160523102939.1: *4* rt.Await (Python 3)
    # Await(expr value)

    def do_Await(self, node):

        self.div('statement')
        self.keyword('await')
        self.visit(node.value)
        self.end_div('statement')
    #@+node:ekr.20150722204300.52: *4* rt.AugAssign
    #  AugAssign(expr target, operator op, expr value)

    def do_AugAssign(self, node):

        op_name = self.op_name(node.op)
        self.div('statement')
        self.visit(node.target)
        self.op(op_name, leading=True)
        self.visit(node.value)
        self.end_div('statement')
    #@+node:ekr.20150722204300.53: *4* rt.BinOp
    def do_BinOp(self, node):

        op_name = self.op_name(node.op)
        # self.span(op_name)
        self.visit(node.left)
        self.op(op_name, leading=True)
        self.visit(node.right)
        # self.end_span(op_name)
    #@+node:ekr.20150722204300.54: *4* rt.BoolOp
    def do_BoolOp(self, node):

        op_name = self.op_name(node.op).strip()
        self.span(op_name)
        for i, node2 in enumerate(node.values):
            if i > 0:
                self.keyword(op_name)
            self.visit(node2)
        self.end_span(op_name)
    #@+node:ekr.20150722204300.55: *4* rt.Break
    def do_Break(self, node):

        self.simple_statement('break')
    #@+node:ekr.20160523103529.1: *4* rt.Bytes (Python 3)
    def do_Bytes(self, node):  # Python 3.x only.
        return str(node.s)
    #@+node:ekr.20150722204300.56: *4* rt.Call & do_keyword
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
    #@+node:ekr.20150722204300.57: *5* rt.do_keyword
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
    #@+node:ekr.20150722204300.58: *4* rt.ClassDef
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
    #@+node:ekr.20150722204300.59: *4* rt.Compare
    def do_Compare(self, node):

        assert len(node.ops) == len(node.comparators)
        # self.span('compare')
        self.visit(node.left)
        for i in range(len(node.ops)):
            op_name = self.op_name(node.ops[i])
            self.op(op_name, leading=True)
            self.visit(node.comparators[i])
        # self.end_span('compare')
    #@+node:ekr.20150722204300.60: *4* rt.comprehension
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
    #@+node:ekr.20170721073431.1: *4* rt.Constant (Python 3.6+)
    def do_Constant(self, node):  # Python 3.6+ only.
        return str(node.s)  # A guess.
    #@+node:ekr.20150722204300.61: *4* rt.Continue
    def do_Continue(self, node):

        self.simple_statement('continue')
    #@+node:ekr.20150722204300.62: *4* rt.Delete
    def do_Delete(self, node):

        self.div('statement')
        self.keyword('del')
        if node.targets:
            self.visit_list(node.targets, sep=',')
        self.end_div('statement')
    #@+node:ekr.20150722204300.63: *4* rt.Dict
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
    #@+node:ekr.20160523104330.1: *4* rt.DictComp
    # DictComp(expr key, expr value, comprehension* generators)

    def do_DictComp(self, node):
        elt = self.visit(node.elt)
        gens = [self.visit(z) for z in node.generators]
        gens = [z if z else '<**None**>' for z in gens]  # Kludge: probable bug.
        return f'%s for %s' % (elt, ''.join(gens))
    #@+node:ekr.20150722204300.47: *4* rt.do_arguments & helpers
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
    #@+node:ekr.20160315182225.1: *5* rt.arg (Python 3 only)
    # 3: arg = (identifier arg, expr? annotation)

    def do_arg(self, node):

        self.gen(node.arg)
        if getattr(node, 'annotation', None):
            self.colon()
            self.visit(node.annotation)
    #@+node:ekr.20150722204300.48: *5* rt.tuple_parameter
    def tuple_parameter(self, node):

        assert isinstance(node, (list, tuple)), node
        self.gen("(")
        for param in node:
            if isinstance(param, tuple):
                self.tuple_parameter(param)
            else:
                self.visit(param)
        self.gen(")")
    #@+node:ekr.20150722204300.64: *4* rt.Ellipsis
    def do_Ellipsis(self, node):

        self.gen('...')
    #@+node:ekr.20150722204300.65: *4* rt.ExceptHandler
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
    #@+node:ekr.20150722204300.66: *4* rt.Exec
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
    #@+node:ekr.20150722204300.67: *4* rt.Expr
    def do_Expr(self, node):

        self.div_node('expr', node.value)
    #@+node:ekr.20160523103429.1: *4* rf.Expression
    def do_Expression(self, node):
        """An inner expression: do not indent."""
        return f'%s' % self.visit(node.body)
    #@+node:ekr.20160523103751.1: *4* rt.ExtSlice
    def do_ExtSlice(self, node):
        return ':'.join([self.visit(z) for z in node.dims])
    #@+node:ekr.20150722204300.68: *4* rt.For & AsyncFor (Python 3)
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
    #@+node:ekr.20170721075845.1: *4* rf.FormattedValue (Python 3.6+: unfinished)
    # FormattedValue(expr value, int? conversion, expr? format_spec)

    def do_FormattedValue(self, node):  # Python 3.6+ only.
        self.div('statement')
        self.visit(node.value)
        if node.conversion:
            self.visit(node.conversion)
        if node.format_spec:
            self.visit(node.format_spec)
        self.end_div('statement')
    #@+node:ekr.20150722204300.69: *4* rt.FunctionDef
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
    #@+node:ekr.20150722204300.70: *4* rt.GeneratorExp
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
    #@+node:ekr.20150722204300.71: *4* rt.get_import_names
    def get_import_names(self, node):
        """Return a list of the the full file names in the import statement."""
        result = []
        for ast2 in node.names:
            assert isinstance(ast2, ast.alias), repr(ast2)
            data = ast2.name, ast2.asname
            result.append(data)
        return result
    #@+node:ekr.20150722204300.72: *4* rt.Global
    def do_Global(self, node):

        self.div('statement')
        self.keyword("global")
        for z in node.names:
            self.gen(z)
            self.comma()
        self.clean_comma()
        self.end_div('statement')
    #@+node:ekr.20150722204300.73: *4* rt.If
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
    #@+node:ekr.20150722204300.74: *4* rt.IfExp (TernaryOp)
    # IfExp(expr test, expr body, expr orelse)

    def do_IfExp(self, node):

        # self.span('ifexp')
        self.visit(node.body)
        self.keyword('if')
        self.visit(node.test)
        self.keyword('else')
        self.visit(node.orelse)
        # self.end_span('ifexp')
    #@+node:ekr.20150722204300.75: *4* rt.Import
    def do_Import(self, node):

        self.div('statement')
        self.keyword("import")
        for name, alias in self.get_import_names(node):
            self.name(name)  # self.gen(self.module_link(name))
            if alias:
                self.keyword("as")
                self.name(alias)
        self.end_div('statement')
    #@+node:ekr.20150722204300.76: *4* rt.ImportFrom
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
    #@+node:ekr.20160315190818.1: *4* rt.Index
    def do_Index(self, node):

        self.visit(node.value)
    #@+node:ekr.20170721080959.1: *4* rf.JoinedStr (Python 3.6+: unfinished)
    # JoinedStr(expr* values)

    def do_JoinedStr(self, node):
        for value in node.values or []:
            self.visit(value)
    #@+node:ekr.20150722204300.77: *4* rt.Lambda
    def do_Lambda(self, node):

        # self.span('lambda')
        self.keyword('lambda')
        self.visit(node.args)
        self.comma()
        self.span_node("code", node.body)
        # self.end_span('lambda')
    #@+node:ekr.20150722204300.78: *4* rt.List
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
    #@+node:ekr.20150722204300.79: *4* rt.ListComp
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
    #@+node:ekr.20150722204300.80: *4* rt.Module
    def do_Module(self, node):

        self.doc(node)
        self.visit_list(node.body)
    #@+node:ekr.20150722204300.81: *4* rt.Name
    def do_Name(self, node):

        self.name(node.id)
    #@+node:ekr.20160315165109.1: *4* rt.NameConstant
    def do_NameConstant(self, node):  # Python 3 only.

        self.name(repr(node.value))
    #@+node:ekr.20160317051849.2: *4* rt.Nonlocal (Python 3)
    # Nonlocal(identifier* names)

    def do_Nonlocal(self, node):

        self.div('statement')
        self.keyword('nonlocal')
        self.gen(', '.join(node.names))
        self.end_div('statement')
    #@+node:ekr.20150722204300.82: *4* rt.Num
    def do_Num(self, node):

        self.gen(self.text(repr(node.n)))
    #@+node:ekr.20150722204300.83: *4* rt.Pass
    def do_Pass(self, node):

        self.simple_statement('pass')
    #@+node:ekr.20150722204300.84: *4* rt.Print
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
    #@+node:ekr.20150722204300.85: *4* rt.Raise
    # Raise(expr? type, expr? inst, expr? tback)    Python 2
    # Raise(expr? exc, expr? cause)                 Python 3

    def do_Raise(self, node):

        self.div('statement')
        self.keyword("raise")
        for attr in ('exc', 'cause'):
            if getattr(node, attr, None) is not None:
                self.visit(getattr(node, attr))
        self.end_div('statement')
    #@+node:ekr.20160523105022.1: *4* rt.Repr
    # Python 2.x only

    def do_Repr(self, node):
        return f'repr(%s)' % self.visit(node.value)
    #@+node:ekr.20150722204300.86: *4* rt.Return
    def do_Return(self, node):

        self.div('statement')
        self.keyword("return")
        if node.value:
            self.visit(node.value)
        self.end_div('statement')
    #@+node:ekr.20160523104433.1: *4* rt.Set
    # Set(expr* elts)

    def do_Set(self, node):
        for z in node.elts:
            self.visit(z)
    #@+node:ekr.20160523104454.1: *4* rt.SetComp
    # SetComp(expr elt, comprehension* generators)

    def do_SetComp(self, node):

        elt = self.visit(node.elt)
        gens = [self.visit(z) for z in node.generators]
        return f'%s for %s' % (elt, ''.join(gens))
    #@+node:ekr.20150722204300.87: *4* rt.Slice
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
    #@+node:ekr.20160317051849.3: *4* rt.Starred (Python 3)
    # Starred(expr value, expr_context ctx)

    def do_Starred(self, node):

        self.gen('*')
        self.visit(node.value)
    #@+node:ekr.20150722204300.88: *4* rt.Str
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
    #@+node:ekr.20150722204300.89: *4* rt.Subscript
    def do_Subscript(self, node):

        # self.span("subscript")
        self.visit(node.value)
        self.gen('[')
        self.visit(node.slice)
        self.gen(']')
        # self.end_span("subscript")
    #@+node:ekr.20160315190913.1: *4* rt.Try (Python 3)
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
    #@+node:ekr.20150722204300.90: *4* rt.TryExcept
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
    #@+node:ekr.20150722204300.91: *4* rt.TryFinally
    def do_TryFinally(self, node):

        self.div('statement')
        self.keyword('try')
        self.colon()
        self.div_body(node.body)
        self.keyword('finally')
        self.colon()
        self.div_body(node.final.body)
        self.end_div('statement')
    #@+node:ekr.20150722204300.92: *4* rt.Tuple
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
    #@+node:ekr.20150722204300.93: *4* rt.UnaryOp
    def do_UnaryOp(self, node):

        op_name = self.op_name(node.op).strip()
        # self.span(op_name)
        self.op(op_name, trailing=False)
        self.visit(node.operand)
        # self.end_span(op_name)
    #@+node:ekr.20150722204300.94: *4* rt.While
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
    #@+node:ekr.20150722204300.95: *4* rt.With & AsyncWith (Python 3)
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
    #@+node:ekr.20150722204300.96: *4* rt.Yield
    def do_Yield(self, node):

        self.div('statement')
        self.keyword('yield')
        self.visit(node.value)
        self.end_div('statement')
    #@+node:ekr.20160317051849.5: *4* rt.YieldFrom (Python 3)
    # YieldFrom(expr value)

    def do_YieldFrom(self, node):

        self.div('statement')
        self.keyword('yield from')
        self.visit(node.value)
        self.end_div('statement')
    #@-others
#@+node:ekr.20191113133338.1: ** class TestRunner
class TestRunner:
    """
    A testing framework for TokenOrderGenerator and related classes.
    """
    #@+others
    #@+node:ekr.20191122021515.1: *3*  TestRunner.run_tests
    def run_tests(self, sources, description, reports):
        """
        Run all tests given in the reports list.

        Reports is a list of reports, in *caller-defined* order.
        """
        import time
        tag = 'run_tests'
        
        #
        # Convert reports to flags.
        valid_flags = (
            'dump-all-after-fail',
            'dump-raw-tree-first', 
            'dump-sources-first',
            'dump-tokens-after-fail',
            'dump-tokens-first',
            'dump-tree-after-fail',
            'no-sync',
            'set-trace-mode',
            'show-exception-after-fail',
            'use-asttokens',
            'trace-times',
            'trace-tokenizer-tokens',
            'verbose-fail',
        )
        reports = [z.lower() for z in reports or []]
        flags = [z for z in reports if z in valid_flags]
        # g.trace('FLAGS', ','.join(sorted(flags)))
        reports = [z for z in reports if z not in valid_flags]
        # Dump sources if asked.
        self.sources = sources = sources.strip() + '\n'
        if 'dump-sources-first' in flags:
            self.dump_contents()
        # Create tokens and tree.
        t1 = time.process_time()
        if 'use-asttokens' in flags:
            import asttokens
            x = self.x = None
            atok = asttokens.ASTTokens(sources, parse=True)
            self.tree = atok.tree
            self.tokens = atok._tokens
            t2 = time.process_time()
        else:
            x = self.x = TokenOrderInjector()
            x.trace_mode = 'set-trace-mode' in flags
            if 'no-sync' in flags:
                x.allow_sync = False
                # The TOI class *also* calls the base begin/end_visitor methods.
            self.tokens = x.make_tokens(sources, trace_mode='trace-tokenizer-tokens' in flags)
            if 'dump-tokens-first' in flags:
                self.dump_tokens(brief=True)
            self.tree = parse_ast(sources)
            if 'dump-raw-tree-first' in flags:
                self.dump_raw_tree()
            # Catch exceptions so we can get data late.
            try:
                t2 = time.process_time()
                # Yes, list *is* required here.
                list(x.create_links(self.tokens, self.tree, file_name=description))
                t3 = time.process_time()
            except Exception as e:
                t3 = time.process_time()
                g.trace(f"\nFAIL: {description}\n")
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
                return False
        if 'trace-times' in flags:
            pad = ' '*4
            print('')
            print(
                f"{pad}description: {description}\n"
                f"{pad} setup time: {(t2-t1):4.2f} sec.\n"
                f"{pad}  link time: {(t3-t2):4.2f} sec.")
            print('')
        # Print reports, in the order they appear in the results list.
        bad_reports = []
        for report in reports:
            helper = getattr(self, report.replace('-', '_'), None)
            if helper:
                try:
                    helper()
                except Exception as e:
                    print(f"{tag}: Exception in {report}: {e}")
                    return False
            else:
                bad_reports.append(report)
        if bad_reports:
            for report in list(set(bad_reports)):
                print('{tag}: bad report option:', repr(report))
        return True
    #@+node:ekr.20191114161840.1: *3* TestRunner.diff
    def diff(self, results_array):
        """
        Produce a diff of self.tokens vs self.results.
        
        The results array no longer exists, so this is a vestigial method.
        """
        import difflib
        import time
        ndiff = False
        if ndiff:
            # FAILS:
            #  File "C:\Users\edreamleo\Anaconda3\lib\difflib.py", line 1017, in _fancy_replace
            #  yield '  ' + aelt
            #  TypeError: can only concatenate str (not "tuple") to str
            results = results_array
            tokens = [(z.kind, z.value) for z in self.tokens]
            gen = difflib.ndiff(tokens, results)
        else:
            # Works.
            results = [f"{z.kind:>12}:{z.value}" for z in results_array]
            tokens =  [f"{z.kind:>12}:{z.value}" for z in self.tokens]
            gen = difflib.Differ().compare(tokens, results)
        t1 = time.process_time()
        diffs = list(gen)
        t2 = time.process_time()
        print(
            f"\nDiff: tokens: {len(tokens)}, results: {len(results)}, "
            f"{len(diffs)} diffs in {(t2-t1):4.2f} sec...")
        if len(diffs) < 1000:
            legend = '\n-: only in tokens, +: only in results, ?: not in either sequence!\n'
            heading = f"tx  rx  kind {'diff key kind:value':>15}"
            line    = f"=== === ==== {'===================':>15}"
            print(legend)
            print(heading)
            print(line)
            rx = tx = 0
            for i, z in enumerate(diffs):
                kind = z[0]
                if kind != '?': # A mystery.
                    print(f"{tx:<3} {rx:<3} {kind!r:4} {truncate(z[1:], 80)!s}")
                if kind == ' ':
                    rx, tx = rx + 1, tx + 1
                elif kind == '+':
                    rx += 1
                elif kind == '-':
                    tx += 1
            # print(line)
            # print(heading)
            # print(legend)
    #@+node:ekr.20191122022728.1: *3* TestRunner.dump_all
    def dump_all(self):

        if self.x:
            self.dump_contents()
            self.dump_tokens()
            self.dump_tree()
            # self.dump_raw_tree()

    #@+node:ekr.20191122025303.1: *3* TestRunner.dump_contents
    def dump_contents(self):
        sources = self.sources
        print('\nContents...\n')
        for i, z in enumerate(g.splitLines(sources)):
            print(f"{i+1:<3} ", z.rstrip())
    #@+node:ekr.20191122025155.1: *3* TestRunner.dump_coverage
    def coverage(self):
        if self.x:
            self.x.report_coverage(report_missing=False)
    #@+node:ekr.20191122025306.1: *3* TestRunner.dump_lines
    def dump_lines(self):
        print('\nTOKEN lines...\n')
        for z in self.tokens:
            if z.line.strip():
                print(z.line.rstrip())
            else:
                print(repr(z.line))
    #@+node:ekr.20191122025306.2: *3* TestRunner.dump_raw_tree
    def dump_raw_tree(self):
        print('\nRaw tree...\n')
        print(AstDumper().dump(self.tree))
    #@+node:ekr.20191122025418.1: *3* TestRunner.dump_tokens
    def dump_tokens(self, brief=False):
        tokens = self.tokens
        print('\nTokens...\n')
        print("Note: values shown are repr(value) *except* for 'string' tokens.\n")
        # pylint: disable=not-an-iterable
        if self.x:
            for z in tokens:
                print(z.dump(brief=brief))
        else:
            import token as tm
            for z in tokens:
                kind = tm.tok_name[z.type].lower()
                print(f"{z.index:4} {kind:>12} {z.string!r}")
    #@+node:ekr.20191122025419.1: *3* TestRunner.dump_tree
    def dump_tree(self, brief=False):
        print('\nPatched tree...\n')
        tokens, tree = self.tokens, self.tree
        if self.x:
            print(AstDumper().brief_dump(tree))
            return
        from asttokens.util import walk
        # print(dumper.dump(tree))
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
    #@-others
   
#@+node:ekr.20191110080535.1: ** class Token
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
        return f"{self.kind:>11} {self.show_val()}"

    def __str__(self):
        return f"{self.kind} {self.show_val()}"

    def to_string(self):
        """Return the contribution of the token to the source file."""
        return self.value if isinstance(self.value, str) else ''
        
    #@+others
    #@+node:ekr.20191113095410.1: *3* token.dump
    def dump(self, brief=False):
        
        """Dump a token node and related links."""
        if brief:
            return (
                f"{self.index:>3} line: {self.line_number:<2} "
                f"{self.kind:>11} {self.show_val(15):<15}")
        # Let block.
        children = getattr(self.node, 'children', [])
        node_id = obj_id(self.node) if self.node else ''
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
    #@+node:ekr.20191116154328.1: *3* token.error_dump
    def error_dump(self):
        """Dump a token or result node for error message."""
        if self.node:
            node_id = obj_id(self.node)
            node_s = f"{node_id} {self.node.__class__.__name__}"
        else:
            node_s = "None"
        return(
            f"index: {self.index:<3} {self.kind:>12} {self.show_val(20):<20} "
            # f"line: {self.line_number} level: {self.level} "
            f"{node_s}")
    #@+node:ekr.20191113095507.1: *3* token.show_val
    def show_val(self, truncate_n=20):
        
        if self.kind in ('ws', 'indent'):
            val = len(self.value)
        elif self.kind == 'string':
            # Important: don't add a repr for 'string' tokens.
            # repr just adds another layer of confusion.
            val = truncate(self.value, truncate_n)
        else:
            val = truncate(repr(self.value), truncate_n)
        return val
    #@-others
#@+node:ekr.20191110165235.1: ** class Tokenizer
class Tokenizer:
    
    """Create a list of Tokens from contents."""
    
    #@+others
    #@+node:ekr.20191110165235.2: *3* tokenizer.add_token
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
    #@+node:ekr.20191110170551.1: *3* tokenizer.check_results
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
    #@+node:ekr.20191110165235.3: *3* tokenizer.create_input_tokens
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
    #@+node:ekr.20191110165235.4: *3* tokenizer.do_token (the gem)
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
        #@+node:ekr.20191128074051.1: *4* << define trace functions >>
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
            val_s = truncate(val, 28)
            ### tok_s2 = truncate(tok_s, 28)
            if kind != 'string':
                val_s = repr(val_s)
                ### tok_s2 = repr(tok_s2)
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
#@+node:ekr.20191111152653.1: ** class TokenOrderFormatter
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
#@+node:ekr.20191113054314.1: ** class TokenOrderInjector (TokenOrderGenerator)
class TokenOrderInjector (TokenOrderGenerator):
    """
    A class that injects data into tokens and ast nodes.
    """
    #@+others
    #@+node:ekr.20191113054550.1: *3* to_inject.begin_visitor
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
    #@-others
#@+node:ekr.20191121122230.1: ** class TokenOrderNodeGenerator (TokenOrderGenerator)
class TokenOrderNodeGenerator(TokenOrderGenerator):
    """A class that yields a stream of nodes."""

    def generate_nodes(self, tree):
        """Entry: yield a stream of nodes."""
        yield from self.visitor(tree)

    # Overrides...
    
    def begin_visitor(self, node):
        if node:
            yield node
        
    def end_visitor(self, node):
        pass

    def sync_token(self, kind, val):
        pass
#@+node:ekr.20160225102931.1: ** class TokenSync (deprecated)
class TokenSync:
    """A class to sync and remember tokens."""
    # To do: handle comments, line breaks...
    #@+others
    #@+node:ekr.20160225102931.2: *3*  ts.ctor & helpers
    def __init__(self, s, tokens):
        """Ctor for TokenSync class."""
        assert isinstance(tokens, list)  # Not a generator.
        self.s = s
        self.first_leading_line = None
        self.lines = [z.rstrip() for z in g.splitLines(s)]
        # Order is important from here on...
        self.nl_token = self.make_nl_token()
        self.line_tokens = self.make_line_tokens(tokens)
        self.blank_lines = self.make_blank_lines()
        self.string_tokens = self.make_string_tokens()
        self.ignored_lines = self.make_ignored_lines()
    #@+node:ekr.20160225102931.3: *4* ts.make_blank_lines
    def make_blank_lines(self):
        """Return of list of line numbers of blank lines."""
        result = []
        for i, aList in enumerate(self.line_tokens):
            # if any([self.token_kind(z) == 'nl' for z in aList]):
            if len(aList) == 1 and self.token_kind(aList[0]) == 'nl':
                result.append(i)
        return result
    #@+node:ekr.20160225102931.4: *4* ts.make_ignored_lines
    def make_ignored_lines(self):
        """
        Return a copy of line_tokens containing ignored lines,
        that is, full-line comments or blank lines.
        These are the lines returned by leading_lines().
        """
        result = []
        for i, aList in enumerate(self.line_tokens):
            for z in aList:
                if self.is_line_comment(z):
                    result.append(z)
                    break
            else:
                if i in self.blank_lines:
                    result.append(self.nl_token)
                else:
                    result.append(None)
        assert len(result) == len(self.line_tokens)
        for i, aList in enumerate(result):
            if aList:
                self.first_leading_line = i
                break
        else:
            self.first_leading_line = len(result)
        return result
    #@+node:ekr.20160225102931.5: *4* ts.make_line_tokens (trace tokens)
    def make_line_tokens(self, tokens):
        """
        Return a list of lists of tokens for each list in self.lines.
        The strings in self.lines may end in a backslash, so care is needed.
        """
        import token as tm
        n, result = len(self.lines), []
        for i in range(0, n+1):
            result.append([])
        for token in tokens:
            t1, t2, t3, t4, t5 = token
            kind = tm.tok_name[t1].lower()
            srow, scol = t3
            erow, ecol = t4
            line = erow - 1 if kind == 'string' else srow - 1
            result[line].append(token)
        assert len(self.lines) + 1 == len(result), len(result)
        return result
    #@+node:ekr.20160225102931.6: *4* ts.make_nl_token
    def make_nl_token(self):
        """Return a newline token with '\n' as both val and raw_val."""
        import token as tm
        t1 = tm.NEWLINE
        t2 = '\n'
        t3 = (0, 0)  # Not used.
        t4 = (0, 0)  # Not used.
        t5 = '\n'
        return t1, t2, t3, t4, t5
    #@+node:ekr.20160225102931.7: *4* ts.make_string_tokens
    def make_string_tokens(self):
        """Return a copy of line_tokens containing only string tokens."""
        result = []
        for aList in self.line_tokens:
            result.append([z for z in aList if self.token_kind(z) == 'string'])
        assert len(result) == len(self.line_tokens)
        return result
    #@+node:ekr.20160225102931.8: *3* ts.check_strings
    def check_strings(self):
        """Check that all strings have been consumed."""
        for i, aList in enumerate(self.string_tokens):
            if aList:
                g.trace(f"warning: line {i}. unused strings: {aList}")
    #@+node:ekr.20160225102931.10: *3* ts.is_line_comment
    def is_line_comment(self, token):
        """Return True if the token represents a full-line comment."""
        import token as tm
        t1, t2, t3, t4, t5 = token
        kind = tm.tok_name[t1].lower()
        raw_val = t5
        return kind == 'comment' and raw_val.lstrip().startswith('#')
    #@+node:ekr.20160225102931.12: *3* ts.last_node
    def last_node(self, node):
        """Return the node of node's tree with the largest lineno field."""

        class LineWalker(ast.NodeVisitor):

            def __init__(self):
                """Ctor for LineWalker class."""
                self.node = None
                self.lineno = -1

            def visit(self, node):
                """LineWalker.visit."""
                if hasattr(node, 'lineno'):
                    if node.lineno > self.lineno:
                        self.lineno = node.lineno
                        self.node = node
                if isinstance(node, list):
                    for z in node:
                        self.visit(z)
                else:
                    self.generic_visit(node)

        w = LineWalker()
        w.visit(node)
        return w.node
    #@+node:ekr.20160225102931.13: *3* ts.leading_lines
    def leading_lines(self, node):
        """Return a list of the preceding comment and blank lines"""
        # This can be called on arbitrary nodes.
        leading = []
        if hasattr(node, 'lineno'):
            i, n = self.first_leading_line, node.lineno
            while i < n:
                token = self.ignored_lines[i]
                if token:
                    s = self.token_raw_val(token).rstrip() + '\n'
                    leading.append(s)
                i += 1
            self.first_leading_line = i
        return leading
    #@+node:ekr.20160225102931.14: *3* ts.leading_string
    def leading_string(self, node):
        """Return a string containing all lines preceding node."""
        return ''.join(self.leading_lines(node))
    #@+node:ekr.20160225102931.15: *3* ts.line_at
    def line_at(self, node, continued_lines=True):
        """Return the lines at the node, possibly including continuation lines."""
        n = getattr(node, 'lineno', None)
        if n is None:
            return f'<no line> for %s' % node.__class__.__name__
        if continued_lines:
            aList, n = [], n - 1
            while n < len(self.lines):
                s = self.lines[n]
                if s.endswith('\\'):
                    aList.append(s[:-1])
                    n += 1
                else:
                    aList.append(s)
                    break
            return ''.join(aList)
        return self.lines[n - 1]
    #@+node:ekr.20160225102931.16: *3* ts.sync_string
    def sync_string(self, node):
        """Return the spelling of the string at the given node."""
        n = node.lineno
        tokens = self.string_tokens[n - 1]
        if tokens:
            token = tokens.pop(0)
            self.string_tokens[n - 1] = tokens
            return self.token_val(token)
        g.trace('===== underflow', n, node.s)
        return node.s
    #@+node:ekr.20160225102931.18: *3* ts.tokens_for_statement
    def tokens_for_statement(self, node):
        assert isinstance(node, ast.AST), node
        name = node.__class__.__name__
        if hasattr(node, 'lineno'):
            tokens = self.line_tokens[node.lineno - 1]
            g.trace(' '.join([self.dump_token(z) for z in tokens]))
        else:
            g.trace('no lineno', name)
    #@+node:ekr.20160225102931.19: *3* ts.trailing_comment
    def trailing_comment(self, node):
        """
        Return a string containing the trailing comment for the node, if any.
        The string always ends with a newline.
        """
        if hasattr(node, 'lineno'):
            return self.trailing_comment_at_lineno(node.lineno)
        g.trace('no lineno', node.__class__.__name__, g.callers())
        return '\n'
    #@+node:ekr.20160225102931.20: *3* ts.trailing_comment_at_lineno
    def trailing_comment_at_lineno(self, lineno):
        """Return any trailing comment at the given node.lineno."""
        tokens = self.line_tokens[lineno - 1]
        for token in tokens:
            if self.token_kind(token) == 'comment':
                raw_val = self.token_raw_val(token).rstrip()
                if not raw_val.strip().startswith('#'):
                    val = self.token_val(token).rstrip()
                    s = f' %s\n' % val
                    return s
        return '\n'
    #@+node:ekr.20160225102931.21: *3* ts.trailing_lines
    def trailing_lines(self):
        """return any remaining ignored lines."""
        trailing = []
        i = self.first_leading_line
        while i < len(self.ignored_lines):
            token = self.ignored_lines[i]
            if token:
                s = self.token_raw_val(token).rstrip() + '\n'
                trailing.append(s)
            i += 1
        self.first_leading_line = i
        return trailing
    #@+node:ekr.20191122105543.1: *3* ts:dumps
    #@+node:ekr.20160225102931.9: *4* ts.dump_token
    def dump_token(self, token, verbose=False):
        """Dump the token. It is either a string or a 5-tuple."""
        import token as tm
        if isinstance(token, str):
            return token
        t1, t2, t3, t4, t5 = token
        kind = g.toUnicode(tm.tok_name[t1].lower())
        # raw_val = g.toUnicode(t5)
        val = g.toUnicode(t2)
        if verbose:
            return f'token: %10s %r' % (kind, val)
        return val
    #@+node:ekr.20160225102931.17: *4* ts.token_kind/raw_val/val
    def token_kind(self, token):
        """Return the token's type."""
        t1, t2, t3, t4, t5 = token
        import token as tm
        return g.toUnicode(tm.tok_name[t1].lower())

    def token_raw_val(self, token):
        """Return the value of the token."""
        t1, t2, t3, t4, t5 = token
        return g.toUnicode(t5)

    def token_val(self, token):
        """Return the raw value of the token."""
        t1, t2, t3, t4, t5 = token
        return g.toUnicode(t2)
    #@+node:ekr.20160225102931.11: *4* ts.join
    def join(self, aList, sep=','):
        """return the items of the list joined by sep string."""
        tokens = []
        for i, token in enumerate(aList or []):
            tokens.append(token)
            if i < len(aList) - 1:
                tokens.append(sep)
        return tokens
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo

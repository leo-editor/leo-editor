#@+leo-ver=5-thin
#@+node:ekr.20141012064706.18389: * @file leoAst.py
"""AST (Abstract Syntax Tree) related classes."""
# Don't import leoGlobals at the top level.
# This is an attempt to help imp.reload(leoAst).
import ast
import textwrap
#@+others
#@+node:ekr.20160521104628.1: **   leoAst.py: top-level
#@+node:ekr.20191027072910.1: *3* class AstNotEqual (Exception)
class AstNotEqual(Exception):
    """The two given AST's are not equivalent."""
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
#@+node:ekr.20191027074436.1: *3* function: dump_ast
def dump_ast(ast, tag=None):
    """Utility to dump an ast tree."""
    import leo.core.leoGlobals as g
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
#@+node:ekr.20191027075648.1: *3* function: parse_ast
def parse_ast(s, headline=None):
    """
    Parse string s, catching & reporting all exceptions.
    Return the ast node, or None.
    """
    import leo.core.leoGlobals as g

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
    #@+<< TokenOrderGenerator docstring >>
    #@+node:ekr.20191113063144.2: *3*  << TokenOrderGenerator docstring >>
    """
    Ahas: https://groups.google.com/d/msg/leo-editor/FZYJmbtRBWs/qWPdxKw5AgAJ

    A class that supports (and defines) **token-order traversals**.

    Aha: "Elegant" code can not suffice. Per-node visitors are required.
    Aha: This code must be isomorphic to the AstFormatter class.

    This class generates results from a tree of ast nodes in *exactly* order in which
    those nodes contribute tokens.
    """
    #@-<< TokenOrderGenerator docstring >>

    coverage_set = set()
        # The set of node.__class__.__name__ that have been visited.
    level = 0
        # Indentation level.
    max_level = 0
        # Max python indentation level.
    max_stack_level = 0
        # Max depth of node_stack.
    node = None
        # The node being visited.
        # The parent of the about-to-be visited node.
    node_stack = []
        # The stack of nodes being visited.
    tokens = None
        # The list of input tokens.
    token_index = None
        # The index into self.tokens.
    ws_kinds = ('ws', 'line-indent') # 'newline', 'nl', 
        # For tracing only: The kinds of tokens representing whitespace.

    #@+others
    #@+node:ekr.20191113063144.3: *3* tog.begin/end_visitor
    node_level = 0

    # These methods support generators.

    # Subclasses may/should override these methods.

    def begin_visitor(self, node):
        """Enter a visitor."""
        import leo.core.leoGlobals as g
        # begin_visitor and end_visitor must be paired.
        self.node_level += 1
        assert self.node_level == 1, g.callers()
        # Push the previous node.
        self.node_stack.append(self.node)
        # Update the stat.
        self.max_stack_level = max(len(self.node_stack), self.max_stack_level)
        # Update self.node *last*.
        self.node = node
        
    def end_visitor(self, node):
        """Leave a visitor."""
        import leo.core.leoGlobals as g
        # begin_visitor and end_visitor must be paired.
        self.node_level -= 1
        assert self.node_level == 0, g.callers()
        assert self.node == node, (repr(self.node), repr(node))
        # Update the stat.
        self.max_level = max(self.level, self.max_stack_level)
        # Restore self.node.
        self.node = self.node_stack.pop()
    #@+node:ekr.20191113063144.4: *3* tog.create_links (entry)
    def create_links(self, tokens, tree):
        """
        Verify that traversing the given ast tree generates exactly the given
        tokens, in exact order.
        """
        self.tokens = tokens[:]
        self.token_index = 0
        self.visit(tree)
        # Patch the last tokens.
        self.node = tree
        self.eat('newline', '\n')
        self.eat('endmarker', '')
        print(
            f"\ncreate_links: max_level: {self.max_level}, "
            f"max_stack_level: {self.max_stack_level}")
    #@+node:ekr.20191113063144.5: *3* tog.eat
    def eat(self, kind, val):
        """
        The heart of this class.
        
        Eat zero or more tokens in self.tokens corresponding to (kind, val).
        
        Inject the desired data into each token.
        
        A trick: when skipping a token, associate the node with
        self.node.parent instead of self.node.
        """
        import leo.core.leoGlobals as g
        
        trace = True and not g.unitTesting
        
        if trace:
            print('')
            
        def truncate(s, n):
            if isinstance(s, str):
                s = s.replace('\n','<NL>')
            else:
                s = repr(s)
            return s if len(s) <  n else s[:n-3] + '...'
        
        def get_token():
            assert self.token_index < len(self.tokens), (self.token_index, len(self.tokens))
            token = self.tokens[self.token_index]
            # Patch the token.
            token.index = self.token_index
            token.level = self.level
            token.node = self.node
            val_s = truncate(val, 20)
            if trace:
                print(f"eat: kind: {kind:9} {val_s:<20} token: {token.dump()}")
            self.token_index += 1
            return token

        # Get the next token.
        token = get_token()
        # Ignore encoding tokens.
        if token.kind == 'encoding':
            token.node = self.node.parent
            token = get_token()
        ws_kinds = ('dedent', 'indent', 'newline', 'nl', 'ws')
        while token:
            if kind == token.kind:
                return # A direct match.
            # Associate the skipped token with it's *parent*.
            if self.node.parent:
                token.node = self.node.parent
            if kind in ('newline', 'ws'):
                # Skip whitespace tokens and hope for a match later.
                if token.kind in ws_kinds:
                    while token.kind in ws_kinds:
                        token = get_token()
                    self.token_index -= 1
                return
            # Skip comment tokens.
            # while token.kind == 'comment':
                # token = get_token()
            # Skip whitespace tokens.
            while token.kind in ws_kinds:
                token = get_token()
            if kind == token.kind:
                return # A delayed match.
            break # An error
        print('\n========== FAIL')
        raise AssertionError(f"MISMATCH: kind: {kind}, token.kind {token.kind}")
            
    #@+node:ekr.20191113063144.6: *3* tog.make_tokens
    def make_tokens(self, contents):
        """
        Return a list (not a generator) of Token objects corresponding to the
        list of 5-tuples generated by tokenize.tokenize.
        """
        import leo.core.leoGlobals as g
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
        tokens = Tokenizer().create_input_tokens(contents, five_tuples)
        assert check(contents, tokens)
        return tokens
    #@+node:ekr.20191113063144.7: *3* tog.put & helpers
    def put(self, kind, val):
        """Handle a token whose kind & value are given."""
        self.eat(kind, val)
        
    def put_blank(self):
        self.put('ws', ' ')

    def put_comma(self):
        self.put('op', ',')
        
    def put_name(self, val):
        self.put('name', val)

    def put_op(self, val):
        self.put('op', val)
        
    def put_optional_comma(self):
        ### To do.
        self.put_comma()
    #@+node:ekr.20191113063144.8: *4* tog.put_newline
    def put_newline(self):

        self.put('newline', '\n')

    #@+node:ekr.20191113063144.9: *4* tog.put_conditional_blank (to do)
    def put_conditional_blank(self):
        
        ### To do.
        self.put_op(' ')
    #@+node:ekr.20191113063144.10: *4* tog.put_conditional_comma (to do)
    def put_conditional_comma(self):
        
        ### To do.
        self.put_op(',')
    #@+node:ekr.20191113063144.11: *3* tog.report_coverage
    def report_coverage(self, report_missing):
        """Report untested visitors."""
        import leo.core.leoGlobals as g

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
    #@+node:ekr.20191113065420.1: *3* tog.visit (to be removed)
    def visit(self, node):
        assert False, 'To be removed'
    #@+node:ekr.20191113063144.13: *3* tog: Visitors
    #@+node:ekr.20191113063144.14: *4* tog: Contexts
    #@+node:ekr.20191113063144.15: *5* tog.AsyncFunctionDef
    # 2: AsyncFunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list)
    # 3: AsyncFunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list,
    #                expr? returns)

    def do_AsyncFunctionDef(self, node):
        
        self.begin_visitor(node)
        if node.decorator_list:
            for z in node.decorator_list:
                # '@%s\n' % self.visit(z)
                self.put_op('@')
                self.visit(z)
                self.put_newline()
        # 'asynch def (%s): -> %s\n' % (name, args, returns)))
        # 'asynch def %s(%s):\n' % (name, args)))
        self.put_name('asynch')
        self.put_blank()
        self.put_name(node.name) # A string
        self.put_op('(')
        if node.args:
            args = self.visit(node.args)
            self.visit(args)
        self.put_op(')')
        self.put_op(':')
        if getattr(node, 'returns', None):  # Python 3.
            self.put_op('->')
            self.visit(node.returns)
        self.put_newline()
        self.level += 1
        for z in node.body:
            self.visit(z)
        self.level -= 1
        self.end_visitor(node)

    #@+node:ekr.20191113063144.16: *5* tog.ClassDef
    # 2: ClassDef(identifier name, expr* bases,
    #             stmt* body, expr* decorator_list)

    # 3: ClassDef(identifier name, expr* bases,
    #             keyword* keywords, expr? starargs, expr? kwargs
    #             stmt* body, expr* decorator_list)

    def do_ClassDef(self, node, print_body=True):
        
        self.begin_visitor(node)
        for z in node.decorator_list or []:
            # @{z}\n
            self.put_op('@')
            self.visit(z)
            self.put_newline()
        # class name(bases):\n
        self.put_name('class')
        self.put_blank()
        self.put_name(node.name) # A string.
        if node.bases:
            self.put_op('(')
            for z in node.bases:
                self.visit(z)
            self.put_op(')')
        self.put_op(':')
        self.put_newline()
        # Body...
        self.level += 1
        for z in node.body:
            self.visit(z)
        self.level -= 1
        self.end_visitor(node)
    #@+node:ekr.20191113063144.17: *5* tog.FunctionDef
    # 2: FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list)
    # 3: FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list,
    #                expr? returns)

    def do_FunctionDef(self, node):
        
        self.begin_visitor(node)
        for z in node.decorator_list or []:
            # @{z}\n
            self.put_op('@')
            self.visit(z)
            self.put_newline()
        # def name(args): returns\n
        # def name(args):\n
        self.put_name('def')
        self.put_blank()
        self.put_name(node.name) # A string.
        self.put_op('(')
        if node.args:
            self.visit(node.args)
        self.put_op(')')
        self.put_op(':')
        if getattr(node, 'returns', None):
            self.put_op('->')
            self.visit(node.returns)
        self.put_newline()
        self.level += 1
        for i, z in enumerate(node.body):
            self.visit(z)
        self.level -= 1
        self.end_visitor(node)
    #@+node:ekr.20191113063144.18: *5* tog.Interactive
    def do_Interactive(self, node):

        self.begin_visitor(node)
        for z in node.body:
            self.visit(z)
        self.end_visitor(node)
    #@+node:ekr.20191113063144.19: *5* tog.Module
    def do_Module(self, node):

        self.begin_visitor(node)
        for z in node.body:
            self.visit(z)
        self.end_visitor(node)
    #@+node:ekr.20191113063144.20: *5* tog.Lambda
    def do_Lambda(self, node):

        self.begin_visitor(node)
        self.put_name('lambda')
        self.put_blank()
        self.visit(node.args)
        self.put_op(':')
        self.visit(node.body)
        self.end_visitor(node)
    #@+node:ekr.20191113063144.21: *4* tog: Expressions
    #@+node:ekr.20191113063144.22: *5* tog.Expr
    def do_Expr(self, node):
        """An outer expression."""
        self.begin_visitor(node)
        self.visit(node.value)
        self.end_visitor(node)
    #@+node:ekr.20191113063144.23: *5* tog.Expression
    def do_Expression(self, node):
        """An inner expression."""
        self.begin_visitor(node)
        self.visit(node.body)
        self.end_visitor(node)
    #@+node:ekr.20191113063144.24: *5* tog.GeneratorExp
    def do_GeneratorExp(self, node):

        # '<gen %s for %s>' % (elt, ','.join(gens))

        ### To do: this is probably wrong.
        self.begin_visitor(node)
        self.visit(node.elt)
        self.put_blank()
        self.put_name('for')
        self.put_blank()
        for z in node.generators:
            self.visit(z)
            self.put_conditional_comma()
        self.end_visitor(node)
    #@+node:ekr.20191113063144.25: *5* tog.ctx nodes
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
    #@+node:ekr.20191113063144.26: *4* tog: Operands
    #@+node:ekr.20191113063144.27: *5* tog.arguments
    # 2: arguments = (expr* args, identifier? vararg, identifier?
    #                arg? kwarg, expr* defaults)
    # 3: arguments = (arg*  args, arg? vararg,
    #                arg* kwonlyargs, expr* kw_defaults,
    #                arg? kwarg, expr* defaults)

    def do_arguments(self, node):
        """Format the arguments node."""
        self.begin_visitor(node)
        n_plain = len(node.args) - len(node.defaults)
        # g.trace('args', len(node.args), 'defaults', len(node.defaults))
        assert n_plain >= 0
        i = 0
        while i < n_plain:
            self.visit(node.args[i])
            i += 1
            if i != n_plain:
                self.put_comma()
        if node.defaults:
            self.put_comma()
        j = 0
        while i < len(node.args) and j < len(node.defaults):
            self.visit(node.args[i])
            self.put_op('=')
            self.visit(node.defaults[j])
            i += 1
            j += 1
            if j != len(node.defaults):
                self.put_comma()
        # Add the vararg and kwarg expressions.
        vararg = getattr(node, 'vararg', None)
        kwarg = getattr(node, 'kwarg', None)
        # Add comma if necessary.
        if node.args and (vararg or kwarg):
            self.put_comma()
        if vararg:
            self.put_op('*')
            self.visit(vararg)
        # Add a comma if necessary.
        if vararg and kwarg:
            self.put_comma()
        if kwarg:
            self.put_op('*')
            self.visit(kwarg)
        self.end_visitor(node)
    #@+node:ekr.20191113063144.28: *5* tog.arg
    # 3: arg = (identifier arg, expr? annotation)

    def do_arg(self, node):
        
        self.begin_visitor(node)
        self.put_name(node.arg)
        if getattr(node, 'annotation', None):
            self.put_blank()
            self.visit(node.annotation)
        self.end_visitor(node)
    #@+node:ekr.20191113063144.29: *5* tog.Attribute
    # Attribute(expr value, identifier attr, expr_context ctx)

    def do_Attribute(self, node):
        
        self.begin_visitor(node)
        self.visit(node.value)
        self.put_op('.')
        self.put_name(node.attr) # A string.
        self.end_visitor(node)
    #@+node:ekr.20191113063144.30: *5* tog.Bytes
    def do_Bytes(self, node):

        self.begin_visitor(node)
        self.put('bytes', str(node.s))
        self.end_visitor(node)
    #@+node:ekr.20191113063144.31: *5* tog.Call & tog.keyword
    # Call(expr func, expr* args, keyword* keywords, expr? starargs, expr? kwargs)

    def do_Call(self, node):

        self.begin_visitor(node)
        self.visit(node.func)
        self.put_op('(')
        for z in node.args:
            self.visit(z)
        for z in node.keywords:
            self.visit(z)
            self.put_comma()
        if getattr(node, 'starargs', None):
            self.put_op('*')
            self.visit(node.starargs)
            self.put_comma()
        if getattr(node, 'kwargs', None):
            self.put_op('**')
            self.visit(node.kwargs)
        self.put_op(')')
        self.end_visitor(node)
    #@+node:ekr.20191113063144.32: *6* tog.keyword
    # keyword = (identifier arg, expr value)

    def do_keyword(self, node):
        self.put_name(node.arg)
        self.put_op('=')
        self.visit(node.value)
        # # node.arg is a string.
        # value = self.visit(node.value)
        # # This is a keyword *arg*, not a Python keyword!
        # return f'%s=%s' % (node.arg, value)
    #@+node:ekr.20191113063144.33: *5* tog.comprehension
    def do_comprehension(self, node):

        ### test.
        self.begin_visitor(node)
        self.visit(node.target) # A name
        self.put_op(' in ')
        self.visit(node.iter)
        if node.ifs:
            self.put_blank()
            self.put_name('if')
            self.put_blank()
            for z in node.ifs:
                self.visit(z)
                # self.put_blank()
        self.end_visitor(node)
    #@+node:ekr.20191113063144.34: *5* tog.Constant
    def do_Constant(self, node):  # Python 3.6+ only.
        
        self.begin_visitor(node)
        self.put('number', str(node.s))  # A guess.
        self.end_visitor(node)
    #@+node:ekr.20191113063144.35: *5* tog.Dict
    def do_Dict(self, node):

        assert len(node.keys) == len(node.values)
        self.begin_visitor(node)
        self.put_op('{')
        for i, z in enumerate(node.keys):
            self.visit(node.keys[i])
            self.put_op(':')
            self.visit(node.values[i])
        self.put_op('}')
        self.end_visitor(node)
    #@+node:ekr.20191113063144.36: *5* tog.DictComp
    # DictComp(expr key, expr value, comprehension* generators)

    def do_DictComp(self, node):

        self.begin_visitor(node)
        self.visit(node.key)
        self.put_op(':')
        self.put_blank()
        self.put_name('for')
        self.put_blank()
        for z in node.generators:
            self.visit(z)
            self.put_conditional_blank()
        self.end_visitor(node)
    #@+node:ekr.20191113063144.37: *5* tog.Ellipsis
    def do_Ellipsis(self, node):
        
        self.begin_visitor(node)
        self.put_op('...')
        self.end_visitor(node)
    #@+node:ekr.20191113063144.38: *5* tog.ExtSlice
    def do_ExtSlice(self, node):
        
        self.begin_visitor(node)
        for i, z in enumerate(node.dims):
            self.visit(z)
            if i < len(node.dims) - 1:
                self.put_op(':')
        self.end_visitor(node)
    #@+node:ekr.20191113063144.39: *5* tog.FormattedValue
    # FormattedValue(expr value, int? conversion, expr? format_spec)

    def do_FormattedValue(self, node):

        self.begin_visitor(node)
        if node.value:
            self.visit(node.value)
        if node.conversion:
            self.visit(node.conversion)
        if node.format_spec:
            self.visit(node.format_spec)
        self.end_visitor(node)
    #@+node:ekr.20191113063144.40: *5* tog.Index
    def do_Index(self, node):

        self.begin_visitor(node)
        self.visit(node.value)
        self.end_visitor(node)
    #@+node:ekr.20191113063144.41: *5* tog.JoinedStr
    # JoinedStr(expr* values)

    def do_JoinedStr(self, node):

        self.begin_visitor(node)
        if node.values:
            for value in node.values:
                self.visit(value)
        self.end_visitor(node)
    #@+node:ekr.20191113063144.42: *5* tog.List
    def do_List(self, node):

        self.begin_visitor(node)
        self.put_op('[')
        for i, z in enumerate(node.elts):
            self.visit(z)
            if i < len(node.elts) - 1:
                self.put_comma()
            else:
                self.put_conditional_comma()
        self.put_op(']')
        self.end_visitor(node)
    #@+node:ekr.20191113063144.43: *5* tog.ListComp
    def do_ListComp(self, node):
       
        ### Test.
        self.begin_visitor(node)
        self.visit(node.elt)
        self.put_blank()
        self.put_name('for')
        self.put_blank()
        for z in node.generators:
            self.visit(z)
        self.end_visitor(node)
    #@+node:ekr.20191113063144.44: *5* tog.Name & NameConstant
    def do_Name(self, node):
        
        self.begin_visitor(node)
        self.put_name(node.id)

    def do_NameConstant(self, node):
        
        self.begin_visitor(node)
        self.put('number', node.value)
        self.end_visitor(node)
    #@+node:ekr.20191113063144.45: *5* tog.Num
    def do_Num(self, node):
        
        self.begin_visitor(node)
        self.put('number', node.n) ### ?
        self.end_visitor(node)
    #@+node:ekr.20191113063144.46: *5* tog.Repr
    def do_Repr(self, node): # Python 2.x only
        
        self.begin_visitor(node)
        self.put_name('repr')
        self.put_op('(')
        self.visit(node.value)
        self.put_op(')')
        self.end_visitor(node)
    #@+node:ekr.20191113063144.47: *5* tog.Set
    # Set(expr* elts)

    def do_Set(self, node):

        ### Test.
        self.begin_visitor(node)
        for z in node.elts:
            self.visit(z)
        self.end_visitor(node)
    #@+node:ekr.20191113063144.48: *5* tog.SetComp
    # SetComp(expr elt, comprehension* generators)

    def do_SetComp(self, node):

        ### Test.
        self.begin_visitor(node)
        self.visit(node.elt)
        self.put_blank()
        self.put_name('for')
        self.put_blank()
        for z in node.generators:
            self.visit(z)
        self.end_visitor(node)
    #@+node:ekr.20191113063144.49: *5* tog.Slice
    def do_Slice(self, node):

        self.begin_visitor(node)
        lower = getattr(node, 'lower', None)
        upper = getattr(node, 'upper', None)
        step = getattr(node, 'step', None)
        if lower is not None:
            self.visit(node.lower)
        self.put_op(':')
        if upper is not None:
            self.visit(node.upper)
        if step is not None: ### Conditional : needed?
            self.put_op(':')
            self.visit(node.step)
        self.end_visitor(node)
    #@+node:ekr.20191113063144.50: *5* tog.Str
    def do_Str(self, node):
        """This represents a string constant."""
        self.begin_visitor(node)
        self.put('string', node.s)
        self.end_visitor(node)
    #@+node:ekr.20191113063144.51: *5* tog.Subscript
    # Subscript(expr value, slice slice, expr_context ctx)

    def do_Subscript(self, node):
        
        self.begin_visitor(node)
        self.visit(node.value)
        self.put_op('[')
        self.visit(node.slice)
        self.put_op(']')
        self.end_visitor(node)
    #@+node:ekr.20191113063144.52: *5* tog.Tuple
    def do_Tuple(self, node):

        self.begin_visitor(node)
        self.put_op('(')
        for i, z in node.elts:
            self.visit(z)
            if i < len(node.elts) - 1:
                self.put_comma()
            else:
                self.put_conditional_comma()
        self.put_op(')')
        self.end_visitor(node)
    #@+node:ekr.20191113063144.53: *4* tog: Operators
    #@+node:ekr.20191113063144.54: *5* tog.op_name
    def op_name(self, node, strict=True):
        """Return the print name of an operator node."""
        # This is not a visitor.
        class_name = node.__class__.__name__
        name = _op_names.get(class_name, f'<%s>' % class_name)
        if strict:
            assert name, class_name
        return name
    #@+node:ekr.20191113063144.55: *5* tog.BinOp
    def do_BinOp(self, node):

        self.begin_visitor(node)
        self.visit(node.left)
        op_name = self.op_name(node.op)
        if op_name.startswith(' '):
            self.put_blank()
            self.put_op(op_name.strip())
            self.put_blank()
        else:
            self.put_op(op_name)
        self.visit(node.right)
        self.end_visitor(node)
    #@+node:ekr.20191113063144.56: *5* tog.BoolOp
    def do_BoolOp(self, node):
        
        self.begin_visitor(node)
        op_name = self.op_name(node.op)
        if op_name.startswith(' '):
            for i, z in enumerate(node.values):
                self.put_blank()
                self.put_op(op_name.strip())
                self.put_blank()
                self.visit(z)
            return
        for i, z in enumerate(node.values):
            self.put_op(op_name)
            self.visit(z)
        self.end_visitor(node)
    #@+node:ekr.20191113063144.57: *5* tog.Compare
    def do_Compare(self, node):
        
        assert len(node.ops) == len(node.comparators)
        self.begin_visitor(node)
        self.visit(node.left)
        for i, z in enumerate(node.ops):
            self.visit(node.ops[i])
            self.visit(node.comparators[i])
        self.end_visitor(node)
    #@+node:ekr.20191113063144.58: *5* tog.UnaryOp
    def do_UnaryOp(self, node):

        self.begin_visitor(node)
        op_name = self.op_name(node.op)
        if op_name.startswith(' '):
            self.put_blank()
            self.put_op(op_name.strip())
            self.put_blank()
        else:
            self.put_op(op_name)
        self.visit(node.operand)
        self.end_visitor(node)
    #@+node:ekr.20191113063144.59: *5* tog.ifExp (ternary operator)
    def do_IfExp(self, node):
        
        #'%s if %s else %s'
        self.begin_visitor(node)
        self.visit(node.body)
        self.put_blank()
        self.put_name('if')
        self.put_blank()
        self.visit(node.test)
        self.put_blank()
        self.put_name('else')
        self.put_blank()
        self.visit(node.orelse)
        self.end_visitor(node)
    #@+node:ekr.20191113063144.60: *4* tog: Statements
    #@+node:ekr.20191113063144.61: *5* tog.AnnAssign
    # AnnAssign(expr target, expr annotation, expr? value, int simple)

    def do_AnnAssign(self, node):

        # {node.target}:{node.annotation}={node.value}\n'
        self.begin_visitor(node)
        self.visit(node.target)
        self.put_op(':')
        self.visit(node.annotation)
        self.put_op('=')
        self.visit(node.value)
        self.put_newline()
        self.end_visitor(node)
    #@+node:ekr.20191113063144.62: *5* tog.Assert
    def do_Assert(self, node):
        
        # assert {node.test}, {node.message}
        # assert {test}'
        self.begin_visitor(node)
        self.put_name('assert')
        self.put_blank()
        self.visit(node.test)
        if getattr(node, 'msg', None):
            self.put_comma()
            self.visit(node.msg)
        self.put_newline()
        self.end_visitor(node)
    #@+node:ekr.20191113063144.63: *5* tog.Assign
    def do_Assign(self, node):
            
        self.begin_visitor(node)
        for z in node.targets:
            self.visit(z)
            self.put_op('=')
        self.visit(node.value)
        self.put_newline()
        self.end_visitor(node)
    #@+node:ekr.20191113063144.64: *5* tog.AsyncFor
    def do_AsyncFor(self, node):
        
        # 'async for %s in %s:\n' % (
        self.begin_visitor(node)
        self.put_name('async')
        self.put_blank()
        self.put_name('for')
        self.put_blank()
        self.visit(node.target)
        self.put_op(':')
        self.visit(node.iter)
        self.put_newline()
        # Body...
        self.level += 1
        for z in node.body:
            self.visit(z)
        self.level -= 1
        if node.orelse:
            self.put_newline()
            # 'else:\n'
            self.put_name('else')
            self.put_op(':')
            self.level += 1
            for z in node.orelse:
                self.visit(z)
            self.level -= 1
        self.put_newline()
        self.end_visitor(node)
    #@+node:ekr.20191113063144.65: *5* tog.AsyncWith
    def do_AsyncWith(self, node):
        
        self.begin_visitor(node)
        self.put_name('async')
        self.put_blank()
        self.end_visitor(node)
        # Delegate the rest.
        self.do_With(node)
    #@+node:ekr.20191113063144.66: *5* tog.AugAssign
    def do_AugAssign(self, node):
        
        # %s%s=%s\n'
        self.begin_visitor(node)
        self.visit(node.target)
        self.op_name(node.op)
        self.put_op('=')
        self.visit(node.value)
        self.put_newline()
        self.end_visitor(node)
    #@+node:ekr.20191113063144.67: *5* tog.Await
    # Await(expr value)

    def do_Await(self, node):
        
        #'await %s\n'
        self.begin_visitor(node)
        self.put_name('await')
        self.put_blank()
        self.visit(node.value)
        self.put_newline()
        self.end_visitor(node)
    #@+node:ekr.20191113063144.68: *5* tog.Break
    def do_Break(self, node):
        
        self.begin_visitor(node)
        self.put_name('break')
        self.put_newline()
        self.end_visitor(node)
    #@+node:ekr.20191113063144.69: *5* tog.Continue
    def do_Continue(self, node):

        self.begin_visitor(node)
        self.put_name('continue')
        self.put_newline()
        self.end_visitor(node)
    #@+node:ekr.20191113063144.70: *5* tog.Delete
    def do_Delete(self, node):

        self.begin_visitor(node)
        self.put_name('del')
        for i, z in enumerate(node.targets):
            self.visit(z)
            if i < len(node.targets) - 1:
                self.put_comma()
        self.put_newline()
        self.end_visitor(node)
    #@+node:ekr.20191113063144.71: *5* tog.ExceptHandler
    def do_ExceptHandler(self, node):
        
        self.begin_visitor(node)
        self.put_name('except')
        self.put_blank()
        if getattr(node, 'type', None):
            self.visit(node.type)
        if getattr(node, 'name', None):
            self.put_blank()
            self.put_name('as')
            if isinstance(node.name, ast.AST):
                self.visit(node.name)
            else:
                self.put_name(node.name)
        self.put_op(':')
        self.put_newline()
        # Body...
        self.level += 1
        for z in node.body:
            self.visit(z)
        self.level -= 1
        self.end_visitor(node)
    #@+node:ekr.20191113063144.72: *5* tog.Exec
    def do_Exec(self, node): # Python 2.x only

        self.begin_visitor(node)
        self.put_name('exec')
        self.put_blank()
        globals_ = getattr(node, 'globals', None)
        locals_ = getattr(node, 'locals', None)
        if globals_ or locals_:
            self.put_name('in')
            self.put_blank()
            if globals_:
                self.visit(node.globals)
            if locals_ and globals_:
                self.put_comma()
            if globals_:
                self.visit(node.locals)
        self.put_newline()
        self.end_visitor(node)
    #@+node:ekr.20191113063144.73: *5* tog.For
    def do_For(self, node):

        #'for %s in %s:\n'
        self.begin_visitor(node)
        self.put_name('for')
        self.put_blank()
        self.visit(node.target)
        self.visit(node.iter)
        self.put_newline()
        # Body...
        self.level += 1
        for z in node.body:
            self.visit(z)
        self.level -= 1
        # 'else:\n'
        if node.orelse:
            self.put_newline()
            self.put_name('else')
            self.put_op(':')
            self.level += 1
            for z in node.orelse:
                self.visit(z)
            self.level -= 1
        self.end_visitor(node)
    #@+node:ekr.20191113063144.74: *5* tog.Global
    def do_Global(self, node):

        self.begin_visitor(node)
        self.put_name('global')
        self.put_blank()
        for i, name in enumerate(node.names):
            self.put_name(name)
            if i < len(node.names) - 1:
                self.put_comma()
        self.put_newline()
        self.end_visitor(node)
    #@+node:ekr.20191113063144.75: *5* tog.If
    def do_If(self, node):
       
        # if %s:\n
        self.begin_visitor(node)
        self.put_name('if')
        self.put_blank()
        self.visit(node.test)
        self.put_op(':')
        self.put_newline()
        # Body.
        self.level += 1
        for z in node.body:
            self.visit(z)
        self.level -= 1
        # Else clause.
        if node.orelse:
            self.put_newline()
            self.put_name('else')
            self.put_blank()
            self.level += 1
            for z in node.orelse:
                self.visit(z)
            self.level -= 1
        self.end_visitor(node)
    #@+node:ekr.20191113063144.76: *5* tog.Import & helper
    def do_Import(self, node):

        self.begin_visitor(node)
        self.put_name('import')
        self.put_blank()
        for i, node2 in enumerate(node.names):
            self.put_name(node2.name)
            if i < len(node.names) - 1:
                self.put_comma()
        as_name = any([z.asname for z in node.names])
        if as_name:
            self.put_blank()
            self.put_name(as_name)
        self.put_newline()
        self.end_visitor(node)
    #@+node:ekr.20191113063144.77: *5* tog.ImportFrom
    def do_ImportFrom(self, node):

        self.begin_visitor(node)
        self.put_name('from')
        self.put_blank()
        self.put_name(node.module)
        self.put_name('import')
        self.put_blank()
        for i, node2 in enumerate(node.names):
            self.put_name(node2.name)
            if i < len(node.names) - 1:
                self.put_comma()
        as_name = any([z.asname for z in node.names])
        if as_name:
            self.put_blank()
            self.put_name(as_name)
        self.put_newline()
        self.end_visitor(node)
    #@+node:ekr.20191113063144.78: *5* tog.Nonlocal
    # Nonlocal(identifier* names)

    def do_Nonlocal(self, node):
        
        # nonlocal %s\n' % ','.join(node.names))
        self.begin_visitor(node)
        self.put_name('nonlocal')
        self.put_blank()
        for i, name in enumerate(node.names):
            self.put_name(name)
            if i < len(node.names) - 1:
                self.put_comma()
        self.put_newline()
        self.end_visitor(node)
    #@+node:ekr.20191113063144.79: *5* tog.Pass
    def do_Pass(self, node):
        
        self.begin_visitor(node)
        self.put_name('pass')
        self.put_newline()
        self.end_visitor(node)
    #@+node:ekr.20191113063144.80: *5* tog.Print
    def do_Print(self, node): # Python 2.x only

        self.begin_visitor(node)
        self.put_name('print')
        self.put_op('(')
        for z in node.values:
            self.visit(z)
        if getattr(node, 'dest', None):
            self.put_name('dest')
            self.put_op('=')
            self.visit(node.dest)
        if getattr(node, 'nl', None):
            self.put_name('nl')
            self.put_op('=')
            self.put_name(node.nl)
        self.put_op(')')
        self.put_newline()
        self.end_visitor(node)
    #@+node:ekr.20191113063144.81: *5* tog.Raise
    # Raise(expr? type, expr? inst, expr? tback)    Python 2
    # Raise(expr? exc, expr? cause)                 Python 3

    def do_Raise(self, node):
       
        self.begin_visitor(node)
        self.put_name('raise')
        exc = getattr(node, 'exc', None)
        cause = getattr(node, 'cause', None)
        tback = getattr(node, 'tback', None)
        if exc or cause or tback:
            self.put_blank()
        if exc:
            self.visit(exc)
        if exc and cause:
            self.put_comma()
        if cause:
            self.visit(cause)
        if tback and (exc or cause):
            self.put_comma()
        if tback:
            self.visit(tback)
        self.put_newline()
        self.end_visitor(node)
    #@+node:ekr.20191113063144.82: *5* tog.Return
    def do_Return(self, node):
        
        self.begin_visitor(node)
        self.put_name('return')
        if node.value:
            self.put_blank()
            self.visit(node.value)
        self.put_newline()
        self.end_visitor(node)
    #@+node:ekr.20191113063144.83: *5* tog.Starred (Python 3)
    # Starred(expr value, expr_context ctx)

    def do_Starred(self, node):

        ### Test.
        self.begin_visitor(node)
        self.visit(node.value)
        self.end_visitor(node)
    #@+node:ekr.20191113063144.84: *5* tog.Suite
    # def do_Suite(self,node):

        # self.begin_visitor(node)
        # for z in node.body:
            # s = self.visit(z)
        # self.end_visitor(node)
    #@+node:ekr.20191113063144.85: *5* tog.Try (Python 3)
    # Try(stmt* body, excepthandler* handlers, stmt* orelse, stmt* finalbody)

    def do_Try(self, node):

        self.begin_visitor(node)
        self.put_name('try')
        self.put_op(':')
        self.put_newline()
        # Body...
        self.level += 1
        for z in node.body:
            self.visit(z)
        self.level -= 1
        # Handlers....
        for z in node.handlers or []:
            self.visit(z)
        # Else...
        if node.orelse:
            self.put_newline()
            self.put_name('else')
            self.put_op(':')
            self.put_newline()
            self.level += 1
            for z in node.orelse:
                self.visit(z)
            self.level -= 1
        # Finally...
        if node.finalbody:
            self.put_newline()
            self.put_name('finally')
            self.put_op(':')
            self.put_newline()
            self.level += 1
            for z in node.finalbody:
                self.visit(z)
            self.level -= 1
        self.end_visitor(node)
    #@+node:ekr.20191113063144.86: *5* tog.TryExcept
    def do_TryExcept(self, node):

        self.begin_visitor(node)
        self.put_name('try')
        self.put_op(':')
        self.put_newline()
        # Body...
        self.level += 1
        for z in node.body:
            self.visit(z)
        self.level -= 1
        # Handlers...
        for z in node.handlers or []:
            self.visit(z)
        # Else...
        if node.orelse:
            self.put_newline()
            self.put_name('else')
            self.put_op(':')
            self.put_newline()
            self.level += 1
            for z in node.orelse:
                self.visit(z)
            self.level -= 1
        self.end_visitor(node)
    #@+node:ekr.20191113063144.87: *5* tog.TryFinally
    def do_TryFinally(self, node):
        
        self.begin_visitor(node)
        self.put_name('try')
        self.put_op(':')
        self.put_newline()
        # Body...
        self.level += 1
        for z in node.body:
            self.visit(z)
        self.level -= 1
        # Finally...
        if node.finalbody:
            self.put_newline()
            self.put_name('finally')
            self.put_op(':')
            self.put_newline()
            self.level += 1
            for z in node.finalbody:
                self.visit(z)
            self.level -= 1
        self.end_visitor(node)
    #@+node:ekr.20191113063144.88: *5* tog.While
    def do_While(self, node):
        
        # while %s:\n'
        self.begin_visitor(node)
        self.put_name('while')
        self.put_blank()
        self.visit(node.test)
        self.put_op(':')
        self.put_newline()
        # Body...
        self.level += 1
        for z in node.body:
            self.visit(z)
        self.level -= 1
        # Else.
        if node.orelse:
            self.put_newline()
            self.put_name('else')
            self.put_op(':')
            self.put_newline()
            self.level += 1
            for z in node.orelse:
                self.visit(z)
            self.level -= 1
        self.end_visitor(node)
    #@+node:ekr.20191113063144.89: *5* tog.With
    # 2:  With(expr context_expr, expr? optional_vars,
    #          stmt* body)
    # 3:  With(withitem* items,
    #          stmt* body)
    # withitem = (expr context_expr, expr? optional_vars)

    def do_With(self, node):
        
        self.begin_visitor(node)
        self.put_name('with')
        self.put_blank()
        if getattr(node, 'context_expression', None):
            self.visit(node.context_expresssion)

        if getattr(node, 'optional_vars', None): # Python 2.
            try:
                for i, z in enumerate(node.optional_vars):
                    self.visit(z)
                    if i < len(node.optional_vars) - 1:
                        self.put_comma()
            except TypeError:  # Not iterable.
                self.visit(node.optional_vars)
        if getattr(node, 'items', None):  # Python 3.
            for i, item in enumerate(node.items):
                self.visit(item.context_expr)
                if getattr(item, 'optional_vars', None):
                    try:
                        for z in item.optional_vars:
                            self.visit(z)
                    except TypeError:  # Not iterable.
                        self.visit(item.optional_vars)
                if i < len(node.items) - 1:
                    self.put_comma()
        # End the line.
        self.put_op(':')
        self.put_newline()
        # Body...
        self.level += 1
        for z in node.body:
            self.visit(z)
        self.level -= 1
        self.end_visitor(node)
    #@+node:ekr.20191113063144.90: *5* tog.Yield
    def do_Yield(self, node):

        self.begin_visitor(node)
        self.put_name('yield')
        if hasattr(node, 'value'):
            self.put_blank()
            self.visit(node.value)
        self.put_newline()
        self.end_visitor(node)
    #@+node:ekr.20191113063144.91: *5* tog.YieldFrom (Python 3)
    # YieldFrom(expr value)

    def do_YieldFrom(self, node):

        self.begin_visitor(node)
        self.put_name('yield')
        self.put_blank()
        self.visit(node.value)
        self.put_newline()
        self.end_visitor(node)
    #@-others
#@+node:ekr.20191110075225.1: **  class TokenOrderTraverser
class TokenOrderTraverser:
    #@+<< TokenOrderTraverser docstring >>
    #@+node:ekr.20191110131436.1: *3*  << TokenOrderTraverser docstring >>
    """
    Ahas: https://groups.google.com/d/msg/leo-editor/FZYJmbtRBWs/qWPdxKw5AgAJ

    A class that supports (and defines) **token-order traversals**.
    Aha: "Elegant" code can not suffice. Per-node visitors are required.
    Aha: This code must be isomorphic to the AstFormatter class.

    This class traverses a tree of ast nodes in *exactly* order in which
    those nodes contribute tokens.
        
    Pass 1. Verifies that the token-order traversal generates exactly the
            tokens, in their correct order.
       
    Pass 2. Creates a **tree-to-token mapping** inserting links:
        
    - from each token to exactly one tree node, the node that
      "generates" the token.
    - from tree nodes to zero or more tokens, in the order they appear
      in the Token list.
    """
    #@-<< TokenOrderTraverser docstring >>

    coverage_set = set()
        # The set of node.__class__.__name__ that have been visited.
    level = 0
        # Indentation level.
    max_level = 0
        # Max python indentation level.
    max_stack_level = 0
        # Max depth of node_stack.
    node = None
        # The node being visited.
        # The parent of the about-to-be visited node.
    node_stack = []
        # The stack of nodes being visited.
    tokens = None
        # The list of input tokens.
    token_index = None
        # The index into self.tokens.
    ws_kinds = ('ws', 'line-indent') # 'newline', 'nl', 
        # For tracing only: The kinds of tokens representing whitespace.

    #@+others
    #@+node:ekr.20191113051828.1: *3* tot.begin/end_visitor
    node_level = 0

    # These methods support generators.

    # Subclasses may/should override these methods.

    def begin_visitor(self, node):
        """Enter a visitor."""
        import leo.core.leoGlobals as g
        # begin_visitor and end_visitor must be paired.
        self.node_level += 1
        assert self.node_level == 1, g.callers()
        # Push the previous node.
        self.node_stack.append(self.node)
        # Update the stat.
        self.max_stack_level = max(len(self.node_stack), self.max_stack_level)
        # Update self.node *last*.
        self.node = node
        
    def end_visitor(self, node):
        """Leave a visitor."""
        import leo.core.leoGlobals as g
        # begin_visitor and end_visitor must be paired.
        self.node_level -= 1
        assert self.node_level == 0, g.callers()
        assert self.node == node, (repr(self.node), repr(node))
        # Update the stat.
        self.max_level = max(self.level, self.max_stack_level)
        # Restore self.node.
        self.node = self.node_stack.pop()
    #@+node:ekr.20191110075448.3: *3* tot.create_links (entry)
    def create_links(self, tokens, tree):
        """
        Verify that traversing the given ast tree generates exactly the given
        tokens, in exact order.
        """
        self.tokens = tokens[:]
        self.token_index = 0
        self.visit(tree)
        # Patch the last tokens.
        self.node = tree
        self.eat('newline', '\n')
        self.eat('endmarker', '')
        print(
            f"\ncreate_links: max_level: {self.max_level}, "
            f"max_stack_level: {self.max_stack_level}")
    #@+node:ekr.20191111023054.1: *3* tot.eat
    def eat(self, kind, val):
        """
        The heart of this class.
        
        Eat zero or more tokens in self.tokens corresponding to (kind, val).
        
        Inject the desired data into each token.
        
        A trick: when skipping a token, associate the node with
        self.node.parent instead of self.node.
        """
        import leo.core.leoGlobals as g
        
        trace = True and not g.unitTesting
        
        if trace:
            print('')
            
        def truncate(s, n):
            if isinstance(s, str):
                s = s.replace('\n','<NL>')
            else:
                s = repr(s)
            return s if len(s) <  n else s[:n-3] + '...'
        
        def get_token():
            assert self.token_index < len(self.tokens), (self.token_index, len(self.tokens))
            token = self.tokens[self.token_index]
            # Patch the token.
            token.index = self.token_index
            token.level = self.level
            token.node = self.node
             # Update the node.
            token_list = getattr(self.node, 'token_list', [])
            token_list.append(token)
            self.node.token_list = token_list
            if trace:
                val_s = truncate(val, 20)
                print(f"eat: kind: {kind:9} {val_s:<20} token: {token.dump()}")
            self.token_index += 1
            return token

        # Get the next token.
        token = get_token()
        # Ignore encoding tokens.
        if token.kind == 'encoding':
            token.node = self.node.parent
            token = get_token()
        ws_kinds = ('dedent', 'indent', 'newline', 'nl', 'ws')
        while token:
            if kind == token.kind:
                return # A direct match.
            # Associate the skipped token with it's *parent*.
            if self.node.parent:
                token.node = self.node.parent
            if kind in ('newline', 'ws'):
                # Skip whitespace tokens and hope for a match later.
                if token.kind in ws_kinds:
                    while token.kind in ws_kinds:
                        token = get_token()
                    self.token_index -= 1
                return
            # Skip comment tokens.
            # while token.kind == 'comment':
                # token = get_token()
            # Skip whitespace tokens.
            while token.kind in ws_kinds:
                token = get_token()
            if kind == token.kind:
                return # A delayed match.
            break # An error
        print('\n========== FAIL')
        raise AssertionError(f"MISMATCH: kind: {kind}, token.kind {token.kind}")
            
    #@+node:ekr.20191110131906.1: *3* tot.make_tokens
    def make_tokens(self, contents):
        """
        Return a list (not a generator) of Token objects corresponding to the
        list of 5-tuples generated by tokenize.tokenize.
        """
        import leo.core.leoGlobals as g
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
        tokens = Tokenizer().create_input_tokens(contents, five_tuples)
        assert check(contents, tokens)
        return tokens
    #@+node:ekr.20191110132115.1: *3* tot.put & helpers
    def put(self, kind, val):
        """Handle a token whose kind & value are given."""
        self.eat(kind, val)
        
    def put_blank(self):
        self.put('ws', ' ')

    def put_comma(self):
        self.put('op', ',')
        
    def put_name(self, val):
        self.put('name', val)

    def put_op(self, val):
        self.put('op', val)
        
    def put_optional_comma(self):
        ### To do.
        self.put_comma()
    #@+node:ekr.20191111041730.1: *4* tot.put_newline
    def put_newline(self):

        self.put('newline', '\n')

    #@+node:ekr.20191111164830.1: *4* tot.put_conditional_blank (to do)
    def put_conditional_blank(self):
        
        ### To do.
        self.put_op(' ')
    #@+node:ekr.20191111162851.1: *4* tot.put_conditional_comma (to do)
    def put_conditional_comma(self):
        
        ### To do.
        self.put_op(',')
    #@+node:ekr.20191111083428.1: *3* tot.report_coverage
    def report_coverage(self, report_missing):
        """Report untested visitors."""
        import leo.core.leoGlobals as g

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
    #@+node:ekr.20191110075448.4: *3* tot.visit (to be removed)
    def visit(self, node):
        """TokenOrderTraverser.visit."""
        import leo.core.leoGlobals as g
        
        trace = False and not g.unitTesting
        
        def oops(method_name):
            print(f"TokenOrderTraverser.visit: missing method: {method_name}")
            
        # visitors must expand all lists/tuples, and must check for empty fields.
        assert isinstance(node, ast.AST), (node.__class__.__name__, g.callers())
        
        # Update the coverage data.
        self.coverage_set.add(node.__class__.__name__)
        # Add parent and children links.
        node.parent = self.node
        children = getattr(self.node, 'children', [])
        children.append(node)
        if self.node:
            self.node.children = children
        # Push the previous node.
        self.node_stack.append(self.node)
        self.max_stack_level = max(len(self.node_stack), self.max_stack_level)
        # Update self.node.
        self.node = node
        # Call the visitor.
        method = getattr(self, 'do_' + self.node.__class__.__name__, oops)
        if trace: g.trace('VISIT', self.node.__class__.__name__)
        method(node)
        # Update the indentation stat.
        self.max_level = max(self.level, self.max_stack_level)
        # Restore self.node.
        self.node = self.node_stack.pop()
        if trace: g.trace('\nRESTORE', self.node.__class__.__name__)
    #@+node:ekr.20191111013646.1: *3* tot: Visitors
    #@+node:ekr.20191110075448.5: *4* tot: Contexts
    #@+node:ekr.20191110140505.1: *5* tot.AsyncFunctionDef
    # 2: AsyncFunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list)
    # 3: AsyncFunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list,
    #                expr? returns)

    def do_AsyncFunctionDef(self, node):
        if node.decorator_list:
            for z in node.decorator_list:
                # '@%s\n' % self.visit(z)
                self.put_op('@')
                self.visit(z)
                self.put_newline()
        # 'asynch def (%s): -> %s\n' % (name, args, returns)))
        # 'asynch def %s(%s):\n' % (name, args)))
        self.put_name('asynch')
        self.put_blank()
        self.put_name(node.name) # A string
        self.put_op('(')
        if node.args:
            args = self.visit(node.args)
            self.visit(args)
        self.put_op(')')
        self.put_op(':')
        if getattr(node, 'returns', None):  # Python 3.
            self.put_op('->')
            self.visit(node.returns)
        self.put_newline()
        self.level += 1
        for z in node.body:
            self.visit(z)
        self.level -= 1

    #@+node:ekr.20191110075448.6: *5* tot.ClassDef
    # 2: ClassDef(identifier name, expr* bases,
    #             stmt* body, expr* decorator_list)

    # 3: ClassDef(identifier name, expr* bases,
    #             keyword* keywords, expr? starargs, expr? kwargs
    #             stmt* body, expr* decorator_list)

    def do_ClassDef(self, node, print_body=True):
        
        for z in node.decorator_list or []:
            # @{z}\n
            self.put_op('@')
            self.visit(z)
            self.put_newline()
        # class name(bases):\n
        self.put_name('class')
        self.put_blank()
        self.put_name(node.name) # A string.
        if node.bases:
            self.put_op('(')
            for z in node.bases:
                self.visit(z)
            self.put_op(')')
        self.put_op(':')
        self.put_newline()
        # Body...
        self.level += 1
        for z in node.body:
            self.visit(z)
        self.level -= 1
    #@+node:ekr.20191110075448.7: *5* tot.FunctionDef
    # 2: FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list)
    # 3: FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list,
    #                expr? returns)

    def do_FunctionDef(self, node):
        for z in node.decorator_list or []:
            # @{z}\n
            self.put_op('@')
            self.visit(z)
            self.put_newline()
        # def name(args): returns\n
        # def name(args):\n
        self.put_name('def')
        self.put_blank()
        self.put_name(node.name) # A string.
        self.put_op('(')
        if node.args:
            self.visit(node.args)
        self.put_op(')')
        self.put_op(':')
        if getattr(node, 'returns', None):
            self.put_op('->')
            self.visit(node.returns)
        self.put_newline()
        self.level += 1
        for i, z in enumerate(node.body):
            self.visit(z)
        self.level -= 1
    #@+node:ekr.20191110075448.8: *5* tot.Interactive
    def do_Interactive(self, node):

        for z in node.body:
            self.visit(z)
    #@+node:ekr.20191110075448.9: *5* tot.Module
    def do_Module(self, node):

        for z in node.body:
            self.visit(z)
    #@+node:ekr.20191110075448.10: *5* tot.Lambda
    def do_Lambda(self, node):

        self.put_name('lambda')
        self.put_blank()
        self.visit(node.args)
        self.put_op(':')
        self.visit(node.body)
    #@+node:ekr.20191110075448.11: *4* tot: Expressions
    #@+node:ekr.20191110075448.12: *5* tot.Expr
    def do_Expr(self, node):
        """An outer expression. It generates no tokens directly."""
        # g.trace('=====', node.value.__class__.__name__)
        self.visit(node.value)
    #@+node:ekr.20191110075448.13: *5* tot.Expression
    def do_Expression(self, node):
        """An inner expression."""
        self.visit(node.body)
        # self.put_conditional_newline()
    #@+node:ekr.20191110075448.14: *5* tot.GeneratorExp
    def do_GeneratorExp(self, node):

        # '<gen %s for %s>' % (elt, ','.join(gens))

        ### To do: this is probably wrong.
        self.visit(node.elt)
        self.put_blank()
        self.put_name('for')
        self.put_blank()
        for z in node.generators:
            self.visit(z)
            self.put_conditional_comma()
    #@+node:ekr.20191110075448.15: *5* tot.ctx nodes
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
    #@+node:ekr.20191110075448.16: *4* tot: Operands
    #@+node:ekr.20191110075448.17: *5* tot.arguments
    # 2: arguments = (expr* args, identifier? vararg, identifier?
    #                arg? kwarg, expr* defaults)
    # 3: arguments = (arg*  args, arg? vararg,
    #                arg* kwonlyargs, expr* kw_defaults,
    #                arg? kwarg, expr* defaults)

    def do_arguments(self, node):
        """Format the arguments node."""
        n_plain = len(node.args) - len(node.defaults)
        # g.trace('args', len(node.args), 'defaults', len(node.defaults))
        assert n_plain >= 0
        i = 0
        while i < n_plain:
            self.visit(node.args[i])
            i += 1
            if i != n_plain:
                self.put_comma()
        if node.defaults:
            self.put_comma()
        j = 0
        while i < len(node.args) and j < len(node.defaults):
            self.visit(node.args[i])
            self.put_op('=')
            self.visit(node.defaults[j])
            i += 1
            j += 1
            if j != len(node.defaults):
                self.put_comma()
        # Add the vararg and kwarg expressions.
        vararg = getattr(node, 'vararg', None)
        kwarg = getattr(node, 'kwarg', None)
        # Add comma if necessary.
        if node.args and (vararg or kwarg):
            self.put_comma()
        if vararg:
            self.put_op('*')
            self.visit(vararg)
        # Add a comma if necessary.
        if vararg and kwarg:
            self.put_comma()
        if kwarg:
            self.put_op('*')
            self.visit(kwarg)
    #@+node:ekr.20191110075448.18: *5* tot.arg
    # 3: arg = (identifier arg, expr? annotation)

    def do_arg(self, node):
        
        self.put_name(node.arg)
        if getattr(node, 'annotation', None):
            self.put_blank()
            self.visit(node.annotation)
    #@+node:ekr.20191110075448.19: *5* tot.Attribute
    # Attribute(expr value, identifier attr, expr_context ctx)

    def do_Attribute(self, node):
        
        self.visit(node.value)
        self.put_op('.')
        self.put_name(node.attr) # A string.
    #@+node:ekr.20191110075448.20: *5* tot.Bytes
    def do_Bytes(self, node):  # Python 3.x only.
        self.put('bytes', str(node.s))
    #@+node:ekr.20191110075448.21: *5* tot.Call & tot.keyword
    # Call(expr func, expr* args, keyword* keywords, expr? starargs, expr? kwargs)

    def do_Call(self, node):

        self.visit(node.func)
        self.put_op('(')
        for z in node.args:
            self.visit(z)
        for z in node.keywords:
            self.visit(z)
            self.put_comma()
        if getattr(node, 'starargs', None):
            self.put_op('*')
            self.visit(node.starargs)
            self.put_comma()
        if getattr(node, 'kwargs', None):
            self.put_op('**')
            self.visit(node.kwargs)
        self.put_op(')')
    #@+node:ekr.20191110075448.22: *6* tot.keyword
    # keyword = (identifier arg, expr value)

    def do_keyword(self, node):
        self.put_name(node.arg)
        self.put_op('=')
        self.visit(node.value)
        # # node.arg is a string.
        # value = self.visit(node.value)
        # # This is a keyword *arg*, not a Python keyword!
        # return f'%s=%s' % (node.arg, value)
    #@+node:ekr.20191110075448.23: *5* tot.comprehension
    def do_comprehension(self, node):

        ### To do: test.
        self.visit(node.target) # A name
        self.put_op(' in ')
        self.visit(node.iter)
        if node.ifs:
            self.put_blank()
            self.put_name('if')
            self.put_blank()
            for z in node.ifs:
                self.visit(z)
                # self.put_blank()
    #@+node:ekr.20191110075448.24: *5* tot.Constant
    def do_Constant(self, node):  # Python 3.6+ only.
        
        self.put('number', str(node.s))  # A guess.
    #@+node:ekr.20191110075448.25: *5* tot.Dict
    def do_Dict(self, node):

        assert len(node.keys) == len(node.values)
        self.put_op('{')
        for i, z in enumerate(node.keys):
            self.visit(node.keys[i])
            self.put_op(':')
            self.visit(node.values[i])
        self.put_op('}')
        
    #@+node:ekr.20191110075448.26: *5* tot.DictComp
    # DictComp(expr key, expr value, comprehension* generators)

    def do_DictComp(self, node):

        self.visit(node.key)
        self.put_op(':')
        self.put_blank()
        self.put_name('for')
        self.put_blank()
        for z in node.generators:
            self.visit(z)
            self.put_conditional_blank()
    #@+node:ekr.20191110075448.27: *5* tot.Ellipsis
    def do_Ellipsis(self, node):
        self.put_op('...')
    #@+node:ekr.20191110075448.28: *5* tot.ExtSlice
    def do_ExtSlice(self, node):
        
        for i, z in enumerate(node.dims):
            self.visit(z)
            if i < len(node.dims) - 1:
                self.put_op(':')
    #@+node:ekr.20191110075448.29: *5* tot.FormattedValue
    # FormattedValue(expr value, int? conversion, expr? format_spec)

    def do_FormattedValue(self, node):

        if node.value:
            self.visit(node.value)
        if node.conversion:
            self.visit(node.conversion)
        if node.format_spec:
            self.visit(node.format_spec)
    #@+node:ekr.20191110075448.30: *5* tot.Index
    def do_Index(self, node):

        self.visit(node.value)

       
    #@+node:ekr.20191110075448.31: *5* tot.JoinedStr
    # JoinedStr(expr* values)

    def do_JoinedStr(self, node):

        if node.values:
            for value in node.values:
                self.visit(value)
    #@+node:ekr.20191110075448.32: *5* tot.List
    def do_List(self, node):

        self.put_op('[')
        for i, z in enumerate(node.elts):
            self.visit(z)
            if i < len(node.elts) - 1:
                self.put_comma()
            else:
                self.put_conditional_comma()
        self.put_op(']')
    #@+node:ekr.20191110075448.33: *5* tot.ListComp
    def do_ListComp(self, node):
       
        ### Test.
        self.visit(node.elt)
        self.put_blank()
        self.put_name('for')
        self.put_blank()
        for z in node.generators:
            self.visit(z)
    #@+node:ekr.20191110075448.34: *5* tot.Name & NameConstant
    def do_Name(self, node):
        self.put_name(node.id)

    def do_NameConstant(self, node):
        self.put('number', node.value)
    #@+node:ekr.20191110075448.35: *5* tot.Num
    def do_Num(self, node):
        
        self.put('number', node.n) # ?
    #@+node:ekr.20191110075448.36: *5* tot.Repr
    def do_Repr(self, node): # Python 2.x only
        
        self.put_name('repr')
        self.put_op('(')
        self.visit(node.value)
        self.put_op(')')
    #@+node:ekr.20191110075448.37: *5* tot.Set
    # Set(expr* elts)

    def do_Set(self, node):

        ### Test.
        for z in node.elts:
            self.visit(z)
    #@+node:ekr.20191110075448.38: *5* tot.SetComp
    # SetComp(expr elt, comprehension* generators)

    def do_SetComp(self, node):

        ### Test.
        self.visit(node.elt)
        self.put_blank()
        self.put_name('for')
        self.put_blank()
        for z in node.generators:
            self.visit(z)
    #@+node:ekr.20191110075448.39: *5* tot.Slice
    def do_Slice(self, node):

        lower = getattr(node, 'lower', None)
        upper = getattr(node, 'upper', None)
        step = getattr(node, 'step', None)
        if lower is not None:
            self.visit(node.lower)
        self.put_op(':')
        if upper is not None:
            self.visit(node.upper)
        if step is not None: ### Conditional : needed?
            self.put_op(':')
            self.visit(node.step)
    #@+node:ekr.20191110075448.40: *5* tot.Str
    def do_Str(self, node):
        """This represents a string constant."""
        self.put('string', node.s)
    #@+node:ekr.20191110075448.41: *5* tot.Subscript
    # Subscript(expr value, slice slice, expr_context ctx)

    def do_Subscript(self, node):
        
        self.visit(node.value)
        self.put_op('[')
        self.visit(node.slice)
        self.put_op(']')
    #@+node:ekr.20191110075448.42: *5* tot.Tuple
    def do_Tuple(self, node):

        self.put_op('(')
        for i, z in node.elts:
            self.visit(z)
            if i < len(node.elts) - 1:
                self.put_comma()
            else:
                self.put_conditional_comma()
        self.put_op(')')
    #@+node:ekr.20191110075448.43: *4* tot: Operators
    #@+node:ekr.20191110075448.44: *5* tot.op_name
    def op_name(self, node, strict=True):
        """Return the print name of an operator node."""
        class_name = node.__class__.__name__
        name = _op_names.get(class_name, f'<%s>' % class_name)
        if strict:
            assert name, class_name
        return name
    #@+node:ekr.20191110075448.45: *5* tot.BinOp
    def do_BinOp(self, node):

        self.visit(node.left)
        op_name = self.op_name(node.op)
        if op_name.startswith(' '):
            self.put_blank()
            self.put_op(op_name.strip())
            self.put_blank()
        else:
            self.put_op(op_name)
        self.visit(node.right)
    #@+node:ekr.20191110075448.46: *5* tot.BoolOp
    def do_BoolOp(self, node):

        op_name = self.op_name(node.op)
        if op_name.startswith(' '):
            for i, z in enumerate(node.values):
                self.put_blank()
                self.put_op(op_name.strip())
                self.put_blank()
                self.visit(z)
            return
        for i, z in enumerate(node.values):
            self.put_op(op_name)
            self.visit(z)
    #@+node:ekr.20191110075448.47: *5* tot.Compare
    def do_Compare(self, node):
        
        assert len(node.ops) == len(node.comparators)
        self.visit(node.left)
        for i, z in enumerate(node.ops):
            self.visit(node.ops[i])
            self.visit(node.comparators[i])
    #@+node:ekr.20191110075448.48: *5* tot.UnaryOp
    def do_UnaryOp(self, node):

        op_name = self.op_name(node.op)
        if op_name.startswith(' '):
            self.put_blank()
            self.put_op(op_name.strip())
            self.put_blank()
        else:
            self.put_op(op_name)
        self.visit(node.operand)
    #@+node:ekr.20191110075448.49: *5* tot.ifExp (ternary operator)
    def do_IfExp(self, node):
        
        #'%s if %s else %s'
        self.visit(node.body)
        self.put_blank()
        self.put_name('if')
        self.put_blank()
        self.visit(node.test)
        self.put_blank()
        self.put_name('else')
        self.put_blank()
        self.visit(node.orelse)

    #@+node:ekr.20191110075448.50: *4* tot: Statements
    #@+node:ekr.20191110075448.51: *5* tot.AnnAssign
    # AnnAssign(expr target, expr annotation, expr? value, int simple)

    def do_AnnAssign(self, node):
        # {node.target}:{node.annotation}={node.value}\n'
        self.visit(node.target)
        self.put_op(':')
        self.visit(node.annotation)
        self.put_op('=')
        self.visit(node.value)
        self.put_newline()
    #@+node:ekr.20191110075448.52: *5* tot.Assert
    def do_Assert(self, node):
        
        # assert {node.test}, {node.message}
        # assert {test}'
        self.put_name('assert')
        self.put_blank()
        self.visit(node.test)
        if getattr(node, 'msg', None):
            self.put_comma()
            self.visit(node.msg)
        self.put_newline()
    #@+node:ekr.20191110075448.53: *5* tot.Assign
    def do_Assign(self, node):
            
        for z in node.targets:
            self.visit(z)
            self.put_op('=')
        self.visit(node.value)
        self.put_newline()
    #@+node:ekr.20191111053252.1: *5* tot.AsyncFor
    def do_AsyncFor(self, node):
        
        # 'async for %s in %s:\n' % (
        self.put_name('async')
        self.put_blank()
        self.put_name('for')
        self.put_blank()
        self.visit(node.target)
        self.put_op(':')
        self.visit(node.iter)
        self.put_newline()
        # Body...
        self.level += 1
        for z in node.body:
            self.visit(z)
        self.level -= 1
        if node.orelse:
            self.put_newline()
            # 'else:\n'
            self.put_name('else')
            self.put_op(':')
            self.level += 1
            for z in node.orelse:
                self.visit(z)
            self.level -= 1
        self.put_newline()
    #@+node:ekr.20191111065842.1: *5* tot.AsyncWith
    def do_AsyncWith(self, node):
        
        self.put_name('async')
        self.put_blank()
        self.do_With(node)
    #@+node:ekr.20191110075448.54: *5* tot.AugAssign
    def do_AugAssign(self, node):
        
        # %s%s=%s\n'
        self.visit(node.target)
        self.op_name(node.op)
        self.put_op('=')
        self.visit(node.value)
        self.put_newline()
    #@+node:ekr.20191110075448.55: *5* tot.Await
    # Await(expr value)

    def do_Await(self, node):
        
        #'await %s\n'
        self.put_name('await')
        self.put_blank()
        self.visit(node.value)
        self.put_newline()
    #@+node:ekr.20191110075448.56: *5* tot.Break
    def do_Break(self, node):
        
        self.put_name('break')
        self.put_newline()
    #@+node:ekr.20191110075448.57: *5* tot.Continue
    def do_Continue(self, node):

        self.put_name('continue')
        self.put_newline()
    #@+node:ekr.20191110075448.58: *5* tot.Delete
    def do_Delete(self, node):

        self.put_name('del')
        for i, z in enumerate(node.targets):
            self.visit(z)
            if i < len(node.targets) - 1:
                self.put_comma()
        self.put_newline()
    #@+node:ekr.20191110075448.59: *5* tot.ExceptHandler
    def do_ExceptHandler(self, node):
        
        self.put_name('except')
        self.put_blank()

        if getattr(node, 'type', None):
            self.visit(node.type)
        if getattr(node, 'name', None):
            self.put_blank()
            self.put_name('as')
            if isinstance(node.name, ast.AST):
                self.visit(node.name)
            else:
                self.put_name(node.name)
        self.put_op(':')
        self.put_newline()
        # Body...
        self.level += 1
        for z in node.body:
            self.visit(z)
        self.level -= 1
        ### self.put_newline()
       
    #@+node:ekr.20191110075448.60: *5* tot.Exec
    def do_Exec(self, node): # Python 2.x only

        self.put_name('exec')
        self.put_blank()
        globals_ = getattr(node, 'globals', None)
        locals_ = getattr(node, 'locals', None)
        if globals_ or locals_:
            self.put_name('in')
            self.put_blank()
            if globals_:
                self.visit(node.globals)
            if locals_ and globals_:
                self.put_comma()
            if globals_:
                self.visit(node.locals)
        self.put_newline()
    #@+node:ekr.20191110075448.61: *5* tot.For
    def do_For(self, node):
        #'for %s in %s:\n'
        self.put_name('for')
        self.put_blank()
        self.visit(node.target)
        self.visit(node.iter)
        self.put_newline()
        # Body...
        self.level += 1
        for z in node.body:
            self.visit(z)
        self.level -= 1
        # 'else:\n'
        if node.orelse:
            self.put_newline()
            self.put_name('else')
            self.put_op(':')
            self.level += 1
            for z in node.orelse:
                self.visit(z)
            self.level -= 1
    #@+node:ekr.20191110075448.62: *5* tot.Global
    def do_Global(self, node):

        self.put_name('global')
        self.put_blank()
        for i, name in enumerate(node.names):
            self.put_name(name)
            if i < len(node.names) - 1:
                self.put_comma()
        self.put_newline()
    #@+node:ekr.20191110075448.63: *5* tot.If
    def do_If(self, node):
       
        # if %s:\n
        self.put_name('if')
        self.put_blank()
        self.visit(node.test)
        self.put_op(':')
        self.put_newline()
        # Body.
        self.level += 1
        for z in node.body:
            self.visit(z)
        self.level -= 1
        # Else clause.
        if node.orelse:
            self.put_newline()
            self.put_name('else')
            self.put_blank()
            self.level += 1
            for z in node.orelse:
                self.visit(z)
            self.level -= 1
    #@+node:ekr.20191110075448.64: *5* tot.Import & helper
    def do_Import(self, node):

        self.put_name('import')
        self.put_blank()
        for i, node2 in enumerate(node.names):
            self.put_name(node2.name)
            if i < len(node.names) - 1:
                self.put_comma()
        as_name = any([z.asname for z in node.names])
        if as_name:
            self.put_blank()
            self.put_name(as_name)
        self.put_newline()
    #@+node:ekr.20191110075448.66: *5* tot.ImportFrom
    def do_ImportFrom(self, node):

        self.put_name('from')
        self.put_blank()
        self.put_name(node.module)
        self.put_name('import')
        self.put_blank()
        for i, node2 in enumerate(node.names):
            self.put_name(node2.name)
            if i < len(node.names) - 1:
                self.put_comma()
        as_name = any([z.asname for z in node.names])
        if as_name:
            self.put_blank()
            self.put_name(as_name)
        self.put_newline()
    #@+node:ekr.20191110075448.67: *5* tot.Nonlocal
    # Nonlocal(identifier* names)

    def do_Nonlocal(self, node):
        
        # nonlocal %s\n' % ','.join(node.names))
        self.put_name('nonlocal')
        self.put_blank()
        for i, name in enumerate(node.names):
            self.put_name(name)
            if i < len(node.names) - 1:
                self.put_comma()
        self.put_newline()

    #@+node:ekr.20191110075448.68: *5* tot.Pass
    def do_Pass(self, node):
        self.put_name('pass')
        self.put_newline()
    #@+node:ekr.20191110075448.69: *5* tot.Print
    # Python 2.x only

    def do_Print(self, node):

        self.put_name('print')
        self.put_op('(')
        for z in node.values:
            self.visit(z)
        if getattr(node, 'dest', None):
            self.put_name('dest')
            self.put_op('=')
            self.visit(node.dest)
        if getattr(node, 'nl', None):
            self.put_name('nl')
            self.put_op('=')
            self.put_name(node.nl)
        self.put_op(')')
        self.put_newline()
        
    #@+node:ekr.20191110075448.70: *5* tot.Raise
    # Raise(expr? type, expr? inst, expr? tback)    Python 2
    # Raise(expr? exc, expr? cause)                 Python 3

    def do_Raise(self, node):
       
        self.put_name('raise')
        exc = getattr(node, 'exc', None)
        cause = getattr(node, 'cause', None)
        tback = getattr(node, 'tback', None)
        if exc or cause or tback:
            self.put_blank()
        if exc:
            self.visit(exc)
        if exc and cause:
            self.put_comma()
        if cause:
            self.visit(cause)
        if tback and (exc or cause):
            self.put_comma()
        if tback:
            self.visit(tback)
        self.put_newline()
    #@+node:ekr.20191110075448.71: *5* tot.Return
    def do_Return(self, node):
        
        self.put_name('return')
        if node.value:
            self.put_blank()
            self.visit(node.value)
        self.put_newline()
    #@+node:ekr.20191110075448.72: *5* tot.Starred (Python 3)
    # Starred(expr value, expr_context ctx)

    def do_Starred(self, node):

        self.put_op('*')
        ### self.visit(node.value)
    #@+node:ekr.20191110075448.73: *5* tot.Suite
    # def do_Suite(self,node):
        # for z in node.body:
            # s = self.visit(z)
    #@+node:ekr.20191110075448.74: *5* tot.Try (Python 3)
    # Try(stmt* body, excepthandler* handlers, stmt* orelse, stmt* finalbody)

    def do_Try(self, node):  # Python 3

        self.put_name('try')
        self.put_op(':')
        self.put_newline()
        # Body...
        self.level += 1
        for z in node.body:
            self.visit(z)
        self.level -= 1
        # Handlers....
        for z in node.handlers or []:
            self.visit(z)
        # Else...
        if node.orelse:
            self.put_newline()
            self.put_name('else')
            self.put_op(':')
            self.put_newline()
            self.level += 1
            for z in node.orelse:
                self.visit(z)
            self.level -= 1
        # Finally...
        if node.finalbody:
            self.put_newline()
            self.put_name('finally')
            self.put_op(':')
            self.put_newline()
            self.level += 1
            for z in node.finalbody:
                self.visit(z)
            self.level -= 1
    #@+node:ekr.20191110075448.75: *5* tot.TryExcept
    def do_TryExcept(self, node):

        self.put_name('try')
        self.put_op(':')
        self.put_newline()
        # Body...
        self.level += 1
        for z in node.body:
            self.visit(z)
        self.level -= 1
        # Handlers...
        for z in node.handlers or []:
            self.visit(z)
        # Else...
        if node.orelse:
            self.put_newline()
            self.put_name('else')
            self.put_op(':')
            self.put_newline()
            self.level += 1
            for z in node.orelse:
                self.visit(z)
            self.level -= 1

    #@+node:ekr.20191110075448.76: *5* tot.TryFinally
    def do_TryFinally(self, node):
        
        self.put_name('try')
        self.put_op(':')
        self.put_newline()
        # Body...
        self.level += 1
        for z in node.body:
            self.visit(z)
        self.level -= 1
        # Finally...
        if node.finalbody:
            self.put_newline()
            self.put_name('finally')
            self.put_op(':')
            self.put_newline()
            self.level += 1
            for z in node.finalbody:
                self.visit(z)
            self.level -= 1
    #@+node:ekr.20191110075448.77: *5* tot.While
    def do_While(self, node):
        
        # while %s:\n'
        self.put_name('while')
        self.put_blank()
        self.visit(node.test)
        self.put_op(':')
        self.put_newline()
        # Body...
        self.level += 1
        for z in node.body:
            self.visit(z)
        self.level -= 1
        # Else.
        if node.orelse:
            self.put_newline()
            self.put_name('else')
            self.put_op(':')
            self.put_newline()
            self.level += 1
            for z in node.orelse:
                self.visit(z)
            self.level -= 1
    #@+node:ekr.20191110075448.78: *5* tot.With
    # 2:  With(expr context_expr, expr? optional_vars,
    #          stmt* body)
    # 3:  With(withitem* items,
    #          stmt* body)
    # withitem = (expr context_expr, expr? optional_vars)

    def do_With(self, node):
        
        self.put_name('with')
        self.put_blank()
        if getattr(node, 'context_expression', None):
            self.visit(node.context_expresssion)

        if getattr(node, 'optional_vars', None): # Python 2.
            try:
                for i, z in enumerate(node.optional_vars):
                    self.visit(z)
                    if i < len(node.optional_vars) - 1:
                        self.put_comma()
            except TypeError:  # Not iterable.
                self.visit(node.optional_vars)
        if getattr(node, 'items', None):  # Python 3.
            for i, item in enumerate(node.items):
                self.visit(item.context_expr)
                if getattr(item, 'optional_vars', None):
                    try:
                        for z in item.optional_vars:
                            self.visit(z)
                    except TypeError:  # Not iterable.
                        self.visit(item.optional_vars)
                if i < len(node.items) - 1:
                    self.put_comma()
        # End the line.
        self.put_op(':')
        self.put_newline()
        # Body...
        self.level += 1
        for z in node.body:
            self.visit(z)
        self.level -= 1
    #@+node:ekr.20191110075448.79: *5* tot.Yield
    def do_Yield(self, node):

        self.put_name('yield')
        if hasattr(node, 'value'):
            self.put_blank()
            self.visit(node.value)
        self.put_newline()
    #@+node:ekr.20191110075448.80: *5* tot.YieldFrom (Python 3)
    # YieldFrom(expr value)

    def do_YieldFrom(self, node):

        self.put_name('yield')
        self.put_blank()
        self.visit(node.value)
        self.put_newline()
    #@-others
#@+node:ekr.20141012064706.18390: ** class AstDumper
class AstDumper:
    """
    Return a formatted dump (a string) of the AST node.

    Adapted from Python's ast.dump.
    """

    def __init__(self,
        annotate_fields=False,  # True: show names of fields.
        disabled_fields=None,  # List of names of fields not to show.
        include_attributes=False,  # True: show line numbers and column offsets.
        indent_ws='  ',  # Number of spaces for each indent.
    ):
        self.annotate_fields = annotate_fields
        self.disabled_fields = disabled_fields or ['ctx',]
        self.include_attributes = include_attributes
        self.indent_ws = indent_ws

    #@+others
    #@+node:ekr.20191112033445.1: *3* d.brief_dump
    def brief_dump(self, node):
        
        result = []
        self.brief_dump_helper(node, 0, result)
        return ''.join(result)
        
    def brief_dump_helper(self, node, level, result):
        """Briefly show a tree, properly indented."""
        if node is None:
            return
        # Let block.
        indent = ' ' * 2 * level
        node_id = str(id(node))[-4:]
        parent = getattr(node, 'parent', None)
        parent_id = str(id(parent))[-4:]
        parent_s = f"{parent_id} {parent.__class__.__name__}" if parent else ''
        children = getattr(node, 'children', [])
        full_s = f"{indent}node: {node_id} {node.__class__.__name__:<14} parent: {parent_s}\n"
        if isinstance(node, (list, tuple)):
            for z in node:
                self.brief_dump_helper(z, level, result)
        elif isinstance(node, str):
            result.append(f"{indent}{node.__class__.__name__:>8}:{node}\n")
        elif isinstance(node, ast.AST):
            # Node and parent.
            result.append(full_s)
            # Fields.
            if 0: # Confusing.
                field_names = [a for a, b in ast.iter_fields(node) if a != 'ctx']
                result.append(f"{indent}fields: {', '.join(field_names)}\n")
            # Children.
            for z in children:
                self.brief_dump_helper(z, level+1, result)
        else:
            result.append(full_s)
    #@+node:ekr.20141012064706.18392: *3* d.dump
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
            return f'[%s]' % ''.join(
                [f'%s%s' % (sep, self.dump(z, level+1)) for z in node])
        return repr(node)
    #@+node:ekr.20191112183737.1: *3* d.dump_one_node (not used)
    def dump_one_node(self, node):
        """Briefly show a tree, properly indented."""
        assert isinstance(node, ast.AST), repr(node)
        # Let block.
        node_id = str(id(node))[-4:]
        parent = getattr(node, 'parent', None)
        parent_id = str(id(parent))[-4:]
        parent_s = f"{parent_id} {parent.__class__.__name__}" if parent else ''
        children = getattr(node, 'children', [])
        return (
            f"node: {node_id} {node.__class__.__name__:<14} "
            f"parent: {parent_s} children: {len(children)}")
    #@+node:ekr.20141012064706.18393: *3* d.get_fields
    def get_fields(self, node):

        return (
            (a, b) for a, b in ast.iter_fields(node)
                if a not in self.disabled_fields and b not in (None, [])
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
#@+node:ekr.20191113063405.1: ** class TokenEater
class TokenEater:
    """
    A class that "eats" a token from a list of tokens.
    
    The "eat" method is the heart of all token-order-related classes.
    
    Subclasses for later passes will not instantiate this class.
    """
    
    def __init__(self, tokens):

        self.token_index = 0
        self.tokens = tokens
        
    #@+others
    #@+node:ekr.20191113063602.1: *3* eat.eat
    def eat(self, kind, level, node, val):
        """
        The heart of this class.
        
        Eat zero or more tokens in self.tokens corresponding to (kind, val).
        
        Inject the desired data into each token.
        
        A trick: when skipping a token, associate the node with node.parent
        instead of node.
        """
        import leo.core.leoGlobals as g
        assert isinstance(node, ast.AST), g.callers()
        trace = True and not g.unitTesting
        if trace:
            print('')

        #@+<< define helpers >>
        #@+node:ekr.20191113064701.1: *4* << define helpers >>
        def get_token():
            """
            Get the next token, injecting data into the token and updating the node."""
            assert self.token_index < len(self.tokens), (self.token_index, len(self.tokens))
            token = self.tokens[self.token_index]
            # Patch the token.
            token.index = self.token_index
            token.level = level
            token.node = node
            # Update the node.
            token_list = getattr(node, 'token_list', [])
            token_list.append(token)
            node.token_list = token_list
            if trace:
                val_s = truncate(val, 20)
                print(f"eat: kind: {kind:9} {val_s:<20} token: {token.dump()}")
            self.token_index += 1
            return token

        def truncate(s, n):
            if isinstance(s, str):
                s = s.replace('\n','<NL>')
            else:
                s = repr(s)
            return s if len(s) <  n else s[:n-3] + '...'
        #@-<< define helpers >>
        # Get the next token.
        token = get_token()
        # Ignore encoding tokens.
        if token.kind == 'encoding':
            token.node = node.parent
            token = get_token()
        ws_kinds = ('dedent', 'indent', 'newline', 'nl', 'ws')
        while token:
            if kind == token.kind:
                return # A direct match.
            # Associate the skipped token with it's *parent*.
            if node.parent:
                token.node = node.parent
            if kind in ('newline', 'ws'):
                # Skip whitespace tokens and hope for a match later.
                if token.kind in ws_kinds:
                    while token.kind in ws_kinds:
                        token = get_token()
                    self.token_index -= 1
                return
            # Skip comment tokens.
            # while token.kind == 'comment':
                # token = get_token()
            # Skip whitespace tokens.
            while token.kind in ws_kinds:
                token = get_token()
            if kind == token.kind:
                return # A delayed match.
            break # An error
        print('\n========== FAIL')
        raise AssertionError(f"MISMATCH: kind: {kind}, token.kind {token.kind}")
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
#@+node:ekr.20191110080535.1: ** class Token
class Token:
    """
    A class representing a 5-tuple, plus additional data.

    The TokenOrderTraverser class creates a list of such tokens.
    """

    def __init__(self, kind, value):
        
        # Set by Tokenizer.add_token.
        self.kind = kind
        self.line = ''
            # The entire line containing the token. Same as token.line.
        self.value = value
        #
        # Additional fields, set by tot.eat.
        self.index = 0
        self.level = 0
        self.line_number = 0
            # The line number, for errors. Same as token.start[0]
        self.node = None

    def dump(self):
        node_id = str(id(self.node))[-4:]
        parent = self.node.parent if self.node else None
        parent_class = parent.__class__.__name__ if parent else ''
        parent_id = str(id(parent))[-4:] if parent else '    '
        children = getattr(self.node, 'children', [])
        return(
            f"{self.index:>3} {self.kind:>11} {self.show_val():<11} "
            f"line: {self.line_number:<2} level: {self.level} "
            f"node: {node_id} {self.node.__class__.__name__:12} "
            f"children: {len(children)} "
            f"parent: {parent_id} {parent_class}")

    def show_val(self):
        return (
            len(self.value) if self.kind in ('ws', 'indent')
            else self.truncate(repr(self.value), 11))
            
    def truncate(self, s, n):
        if isinstance(s, str):
            s = s.replace('\n','')
        else:
            s = repr(s)
        return s if len(s) <  n else s[:n-3] + '...'

    def __repr__(self):
        return f"{self.kind:>11} {self.show_val()}"

    def __str__(self):
        return f"{self.kind} {self.show_val()}"

    def to_string(self):
        """Return the contribution of the token to the source file."""
        return self.value if isinstance(self.value, str) else ''
#@+node:ekr.20191110165235.1: ** class Tokenizer
class Tokenizer:
    
    """Create a list of Tokens from contents."""
    
    #@+others
    #@+node:ekr.20191110165235.2: *3* tok.add_token
    def add_token(self, kind, line, s_row, value):
        """
        Add a token to the results list.
        
        Subclasses could override this method to filter out specific tokens.
        """
        tok = Token(kind, value)
        tok.line = line
        tok.line_number = s_row
        self.results.append(tok)
    #@+node:ekr.20191110170551.1: *3* tok.check_results
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
    #@+node:ekr.20191110165235.3: *3* tok.create_input_tokens
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
    #@+node:ekr.20191110165235.4: *3* tok.do_token (the gem)
    def do_token(self, contents, token):
        """
        Handle the given token, optionally including between-token whitespace.
        
        This is part of the "gem".
        """
        import leo.core.leoGlobals as g
        import token as token_module

        trace = False and not g.unitTesting

        def show_tuple(aTuple):
            s = f"{aTuple[0]}..{aTuple[1]}"
            return f"{s:8}"
            
        # Unpack..
        tok_type, val, start, end, line = token
        s_row, s_col = start
        e_row, e_col = end
        kind = token_module.tok_name[tok_type].lower()
        # Calculate the token's start/end offsets: character offsets into contents.
        s_offset = self.offsets[max(0, s_row-1)] + s_col
        e_offset = self.offsets[max(0, e_row-1)] + e_col
        # Add any preceding between-token whitespace.
        ws = contents[self.prev_offset : s_offset]
        if ws:
            # No need for a hook.
            self.add_token('ws', line, s_row, ws)
            if trace:
                print(
                    f"{'ws':>10} {ws!r:20} "
                    f"{show_tuple((self.prev_offset, s_offset)):>26} "
                    f"{ws!r}")
        # Add the token, if it contributes any real text.
        tok_s = contents[s_offset : e_offset]
        # Bug fix 2019/11/05: always add token, even it contributes text!
        self.add_token(kind, line, s_row, tok_s)
        if trace:
            print(
                f"{kind:>10} {val!r:20} "
                f"{show_tuple(start)} {show_tuple(end)} {show_tuple((s_offset, e_offset))} "
                f"{tok_s!r:15} {line!r}")
        # Update the ending offset.
        self.prev_offset = e_offset
    #@-others
#@+node:ekr.20191111152653.1: ** class TokenOrderFormatter
class TokenOrderFormatter (TokenOrderTraverser):
    
    def format(self, contents):
        """
        Format the tree into a string guaranteed to be generated in token order.
        """
        self.tokens = self.make_tokens(contents)
        tree = parse_ast(contents)
        self.visit(tree)
        return ''.join([z.to_string() for z in self.tokens])
#@+node:ekr.20191113054314.1: ** class TokenOrderInjector (TokenOrderTraverser)
class TokenOrderInjector (TokenOrderTraverser):
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
        children = getattr(node, 'children', [])
        children.append(node)
        if self.node:
            self.node.children = children
        #
        # *Now* update self.node, etc.
        super().begin_visitor(node)
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo

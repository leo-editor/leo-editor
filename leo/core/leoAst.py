#@+leo-ver=5-thin
#@+node:ekr.20141012064706.18389: * @file leoAst.py
'''AST (Abstract Syntax Tree) related classes.'''
import ast
# import re
import xml.sax.saxutils as saxutils
import textwrap
import token as token_module
import leo.core.leoGlobals as g
#@+others
#@+node:ekr.20160521104628.1: **  leoAst.py: top-level
#@+node:ekr.20160521104555.1: *3* leoAst._op_names
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
#@+node:ekr.20160521103254.1: *3* leoAst.unit_test
def unit_test(raise_on_fail=True):
    '''Run basic unit tests for this file.'''
    import _ast
    # import leo.core.leoAst as leoAst
    # Compute all fields to test.
    aList = sorted(dir(_ast))
    remove = [
        'Interactive', 'Suite', # Not necessary.
        'PyCF_ONLY_AST', # A constant,
        'AST', # The base class,
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
        errors, nodes, ops = 0,0,0
        for z in aList:
            if hasattr(traverser, 'do_' + z):
                nodes += 1
            elif _op_names.get(z):
                ops += 1
            else:
                errors += 1
                print('Missing %s visitor for: %s' % (
                    traverser.__class__.__name__,z))
    s = '%s node types, %s op types, %s errors' % (nodes, ops, errors)
    if raise_on_fail:
        assert not errors, s
    else:
        print(s)
#@+node:ekr.20141012064706.18390: ** class AstDumper
class AstDumper(object):
    '''
    Return a formatted dump (a string) of the AST node.

    Adapted from Python's ast.dump.
    '''
    def __init__(self,
        annotate_fields=False, # True: show names of fields.
        disabled_fields=None, # List of names of fields not to show.
        include_attributes=False, # True: show line numbers and column offsets.
        indent_ws='  ', # Number of spaces for each indent.
    ):
        self.annotate_fields = annotate_fields
        self.disabled_fields = disabled_fields or ['ctx',]
        self.include_attributes = include_attributes
        self.indent_ws = indent_ws

    #@+others
    #@+node:ekr.20141012064706.18392: *3* d.dump
    def dump(self, node, level=0):
        sep1 = '\n%s' % (self.indent_ws * (level + 1))
        if isinstance(node, ast.AST):
            fields = [(a, self.dump(b, level + 1)) for a, b in self.get_fields(node)]
            if self.include_attributes and node._attributes:
                fields.extend([(a, self.dump(getattr(node, a), level + 1))
                    for a in node._attributes])
            if self.annotate_fields:
                aList = ['%s=%s' % (a, b) for a, b in fields]
            else:
                aList = [b for a, b in fields]
            compressed = not any([isinstance(b, list) and len(b) > 1 for a, b in fields])
            name = node.__class__.__name__
            if compressed and len(','.join(aList)) < 100:
                return '%s(%s)' % (name, ','.join(aList))
            else:
                sep = '' if len(aList) <= 1 else sep1
                return '%s(%s%s)' % (name, sep, sep1.join(aList))
        elif isinstance(node, list):
            compressed = not any([isinstance(z, list) and len(z) > 1 for z in node])
            sep = '' if compressed and len(node) <= 1 else sep1
            return '[%s]' % ''.join(
                ['%s%s' % (sep, self.dump(z, level + 1)) for z in node])
        else:
            return repr(node)
    #@+node:ekr.20141012064706.18393: *3* d.get_fields
    def get_fields(self, node):
        return (
            (a, b) for a, b in ast.iter_fields(node)
                if a not in self.disabled_fields and b not in (None, [])
        )
    #@-others
#@+node:ekr.20141012064706.18399: ** class AstFormatter
class AstFormatter(object):
    '''
    A class to recreate source code from an AST.

    This does not have to be perfect, but it should be close.

    Also supports optional annotations such as line numbers, file names, etc.
    '''
    # No ctor.
    # pylint: disable=consider-using-enumerate
    
    in_expr = False
    level = 0

    #@+others
    #@+node:ekr.20141012064706.18400: *3*  f.Entries
    #@+node:ekr.20141012064706.18402: *4* f.format
    def format(self, node, level, *args, **keys):
        '''Format the node and possibly its descendants, depending on args.'''
        self.level = level
        val = self.visit(node, *args, **keys)
        return val.rstrip() if val else ''
    #@+node:ekr.20141012064706.18403: *4* f.visit
    def visit(self, node, *args, **keys):
        '''Return the formatted version of an Ast node, or list of Ast nodes.'''
        if isinstance(node, (list, tuple)):
            return ','.join([self.visit(z) for z in node])
        elif node is None:
            return 'None'
        else:
            assert isinstance(node, ast.AST), node.__class__.__name__
            method_name = 'do_' + node.__class__.__name__
            method = getattr(self, method_name)
            s = method(node, *args, **keys)
            assert g.isString(s), type(s)
            return s
    #@+node:ekr.20141012064706.18404: *3* f.Contexts
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
        name = node.name # Only a plain string is valid.
        bases = [self.visit(z) for z in node.bases] if node.bases else []
        if getattr(node, 'keywords', None): # Python 3
            for keyword in node.keywords:
                bases.append('%s=%s' % (keyword.arg, self.visit(keyword.value)))
        if getattr(node, 'starargs', None): # Python 3
            bases.append('*%s' % self.visit(node.starargs))
        if getattr(node, 'kwargs', None): # Python 3
            bases.append('*%s' % self.visit(node.kwargs))
        if bases:
            result.append(self.indent('class %s(%s):\n' % (name, ','.join(bases))))
        else:
            result.append(self.indent('class %s:\n' % name))
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
        '''Format a FunctionDef node.'''
        result = []
        if node.decorator_list:
            for z in node.decorator_list:
                result.append('@%s\n' % self.visit(z))
        name = node.name # Only a plain string is valid.
        args = self.visit(node.args) if node.args else ''
        asynch_prefix = 'asynch ' if async_flag else ''
        if getattr(node, 'returns', None): # Python 3.
            returns = self.visit(node.returns)
            result.append(self.indent('%sdef %s(%s): -> %s\n' % (
                asynch_prefix, name, args, returns)))
        else:
            result.append(self.indent('%sdef %s(%s):\n' % (
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
        return result # 'module:\n%s' % (result)
    #@+node:ekr.20141012064706.18409: *4* f.Lambda
    def do_Lambda(self, node):
        return self.indent('lambda %s: %s' % (
            self.visit(node.args),
            self.visit(node.body)))
    #@+node:ekr.20141012064706.18410: *3* f.Expressions
    #@+node:ekr.20141012064706.18411: *4* f.Expr
    def do_Expr(self, node):
        '''An outer expression: must be indented.'''
        assert not self.in_expr
        self.in_expr = True
        value = self.visit(node.value)
        self.in_expr = False
        return self.indent('%s\n' % value)
    #@+node:ekr.20141012064706.18412: *4* f.Expression
    def do_Expression(self, node):
        '''An inner expression: do not indent.'''
        return '%s\n' % self.visit(node.body)
    #@+node:ekr.20141012064706.18413: *4* f.GeneratorExp
    def do_GeneratorExp(self, node):
        elt = self.visit(node.elt) or ''
        gens = [self.visit(z) for z in node.generators]
        gens = [z if z else '<**None**>' for z in gens] # Kludge: probable bug.
        return '<gen %s for %s>' % (elt, ','.join(gens))
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
    #@+node:ekr.20141012064706.18415: *3* f.Operands
    #@+node:ekr.20141012064706.18416: *4* f.arguments
    # 2: arguments = (expr* args, identifier? vararg, identifier?
    #                arg? kwarg, expr* defaults)
    # 3: arguments = (arg*  args, arg? vararg,
    #                arg* kwonlyargs, expr* kw_defaults,
    #                arg? kwarg, expr* defaults)

    def do_arguments(self, node):
        '''Format the arguments node.'''
        kind = self.kind(node)
        assert kind == 'arguments', kind
        args = [self.visit(z) for z in node.args]
        defaults = [self.visit(z) for z in node.defaults]
        args2 = []
        n_plain = len(args) - len(defaults)
        for i in range(len(node.args)):
            if i < n_plain:
                args2.append(args[i])
            else:
                args2.append('%s=%s' % (args[i], defaults[i - n_plain]))
        if g.isPython3:
            # Add the vararg and kwarg expressions.
            vararg = getattr(node, 'vararg', None)
            if vararg: args2.append('*' + self.visit(vararg))
            kwarg = getattr(node, 'kwarg', None)
            if kwarg: args2.append('**' + self.visit(kwarg))
        else:
            # Add the vararg and kwarg names.
            name = getattr(node, 'vararg', None)
            if name: args2.append('*' + name)
            name = getattr(node, 'kwarg', None)
            if name: args2.append('**' + name)
        return ','.join(args2)
    #@+node:ekr.20141012064706.18417: *4* f.arg (Python3 only)
    # 3: arg = (identifier arg, expr? annotation)

    def do_arg(self, node):
        if getattr(node, 'annotation', None):
            return self.visit(node.annotation)
        else:
            return node.arg
    #@+node:ekr.20141012064706.18418: *4* f.Attribute
    # Attribute(expr value, identifier attr, expr_context ctx)

    def do_Attribute(self, node):
        return '%s.%s' % (
            self.visit(node.value),
            node.attr) # Don't visit node.attr: it is always a string.
    #@+node:ekr.20141012064706.18419: *4* f.Bytes
    def do_Bytes(self, node): # Python 3.x only.
        assert g.isPython3
        return str(node.s)
    #@+node:ekr.20141012064706.18420: *4* f.Call & f.keyword
    # Call(expr func, expr* args, keyword* keywords, expr? starargs, expr? kwargs)

    def do_Call(self, node):
        # g.trace(node,Utils().dump_ast(node))
        func = self.visit(node.func)
        args = [self.visit(z) for z in node.args]
        for z in node.keywords:
            # Calls f.do_keyword.
            args.append(self.visit(z))
        if getattr(node, 'starargs', None):
            args.append('*%s' % (self.visit(node.starargs)))
        if getattr(node, 'kwargs', None):
            args.append('**%s' % (self.visit(node.kwargs)))
        args = [z for z in args if z] # Kludge: Defensive coding.
        s = '%s(%s)' % (func, ','.join(args))
        return s if self.in_expr else self.indent(s+'\n')
            # 2017/12/15.
    #@+node:ekr.20141012064706.18421: *5* f.keyword
    # keyword = (identifier arg, expr value)

    def do_keyword(self, node):
        # node.arg is a string.
        value = self.visit(node.value)
        # This is a keyword *arg*, not a Python keyword!
        return '%s=%s' % (node.arg, value)
    #@+node:ekr.20141012064706.18422: *4* f.comprehension
    def do_comprehension(self, node):
        result = []
        name = self.visit(node.target) # A name.
        it = self.visit(node.iter) # An attribute.
        result.append('%s in %s' % (name, it))
        ifs = [self.visit(z) for z in node.ifs]
        if ifs:
            result.append(' if %s' % (''.join(ifs)))
        return ''.join(result)
    #@+node:ekr.20170721073056.1: *4* f.Constant (Python 3.6+)
    def do_Constant(self, node): # Python 3.6+ only.
        assert g.isPython3
        return str(node.s) # A guess.
    #@+node:ekr.20141012064706.18423: *4* f.Dict
    def do_Dict(self, node):
        result = []
        keys = [self.visit(z) for z in node.keys]
        values = [self.visit(z) for z in node.values]
        if len(keys) == len(values):
            result.append('{\n' if keys else '{')
            items = []
            for i in range(len(keys)):
                items.append('  %s:%s' % (keys[i], values[i]))
            result.append(',\n'.join(items))
            result.append('\n}' if keys else '}')
        else:
            print('Error: f.Dict: len(keys) != len(values)\nkeys: %s\nvals: %s' % (
                repr(keys), repr(values)))
        return ''.join(result)
    #@+node:ekr.20160523101618.1: *4* f.DictComp
    # DictComp(expr key, expr value, comprehension* generators)

    def do_DictComp(self, node):
        key = self.visit(node.key)
        value = self.visit(node.value)
        gens = [self.visit(z) for z in node.generators]
        gens = [z if z else '<**None**>' for z in gens] # Kludge: probable bug.
        return '%s:%s for %s' % (key, value, ''.join(gens))
    #@+node:ekr.20141012064706.18424: *4* f.Ellipsis
    def do_Ellipsis(self, node):
        return '...'
    #@+node:ekr.20141012064706.18425: *4* f.ExtSlice
    def do_ExtSlice(self, node):
        return ':'.join([self.visit(z) for z in node.dims])
    #@+node:ekr.20170721075130.1: *4* f.FormattedValue (Python 3.6+)
    # FormattedValue(expr value, int? conversion, expr? format_spec)

    def do_FormattedValue(self, node): # Python 3.6+ only.
        assert g.isPython3
        return '%s%s%s' % (
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
        elts = [z for z in elts if z] # Defensive.
        return '[%s]' % ','.join(elts)
    #@+node:ekr.20141012064706.18428: *4* f.ListComp
    def do_ListComp(self, node):
        elt = self.visit(node.elt)
        gens = [self.visit(z) for z in node.generators]
        gens = [z if z else '<**None**>' for z in gens] # Kludge: probable bug.
        return '%s for %s' % (elt, ''.join(gens))
    #@+node:ekr.20141012064706.18429: *4* f.Name & NameConstant
    def do_Name(self, node):
        return node.id

    def do_NameConstant(self, node): # Python 3 only.
        s = repr(node.value)
        return s
    #@+node:ekr.20141012064706.18430: *4* f.Num
    def do_Num(self, node):
        return repr(node.n)
    #@+node:ekr.20141012064706.18431: *4* f.Repr
    # Python 2.x only

    def do_Repr(self, node):
        return 'repr(%s)' % self.visit(node.value)
    #@+node:ekr.20160523101929.1: *4* f.Set (new)
    # Set(expr* elts)

    def do_Set(self, node):
        for z in node.elts:
            self.visit(z)
    #@+node:ekr.20160523102226.1: *4* f.SetComp (new)
    # SetComp(expr elt, comprehension* generators)

    def do_SetComp(self, node):

        elt = self.visit(node.elt)
        gens = [self.visit(z) for z in node.generators]
        return '%s for %s' % (elt, ''.join(gens))
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
            return '%s:%s:%s' % (lower, upper, step)
        else:
            return '%s:%s' % (lower, upper)
    #@+node:ekr.20141012064706.18433: *4* f.Str
    def do_Str(self, node):
        '''This represents a string constant.'''
        return repr(node.s)
    #@+node:ekr.20141012064706.18434: *4* f.Subscript
    # Subscript(expr value, slice slice, expr_context ctx)

    def do_Subscript(self, node):
        value = self.visit(node.value)
        the_slice = self.visit(node.slice)
        return '%s[%s]' % (value, the_slice)
    #@+node:ekr.20141012064706.18435: *4* f.Tuple
    def do_Tuple(self, node):
        elts = [self.visit(z) for z in node.elts]
        return '(%s)' % ','.join(elts)
    #@+node:ekr.20141012064706.18436: *3* f.Operators
    #@+node:ekr.20160521104724.1: *4* f.op_name
    def op_name (self,node,strict=True):
        '''Return the print name of an operator node.'''
        name = _op_names.get(self.kind(node),'<%s>' % node.__class__.__name__)
        if strict: assert name, self.kind(node)
        return name
    #@+node:ekr.20141012064706.18437: *4* f.BinOp
    def do_BinOp(self, node):
        return '%s%s%s' % (
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
        if len(ops) == len(comps):
            for i in range(len(ops)):
                result.append('%s%s' % (ops[i], comps[i]))
        else:
            g.trace('ops', repr(ops), 'comparators', repr(comps))
        return ''.join(result)
    #@+node:ekr.20141012064706.18440: *4* f.UnaryOp
    def do_UnaryOp(self, node):
        return '%s%s' % (
            self.op_name(node.op),
            self.visit(node.operand))
    #@+node:ekr.20141012064706.18441: *4* f.ifExp (ternary operator)
    def do_IfExp(self, node):
        return '%s if %s else %s ' % (
            self.visit(node.body),
            self.visit(node.test),
            self.visit(node.orelse))
    #@+node:ekr.20141012064706.18442: *3* f.Statements
    #@+node:ekr.20170721074105.1: *4* f.AnnAssign
    # AnnAssign(expr target, expr annotation, expr? value, int simple)

    def do_AnnAssign(self, node):
        return self.indent('%s:%s=%s\n' % (
            self.visit(node.target),
            self.visit(node.annotation),
            self.visit(node.value),
        ))
    #@+node:ekr.20141012064706.18443: *4* f.Assert
    def do_Assert(self, node):
        test = self.visit(node.test)
        if getattr(node, 'msg', None):
            message = self.visit(node.msg)
            return self.indent('assert %s, %s' % (test, message))
        else:
            return self.indent('assert %s' % test)
    #@+node:ekr.20141012064706.18444: *4* f.Assign
    def do_Assign(self, node):
        return self.indent('%s=%s\n' % (
            '='.join([self.visit(z) for z in node.targets]),
            self.visit(node.value)))
    #@+node:ekr.20141012064706.18445: *4* f.AugAssign
    def do_AugAssign(self, node):
        return self.indent('%s%s=%s\n' % (
            self.visit(node.target),
            self.op_name(node.op), # Bug fix: 2013/03/08.
            self.visit(node.value)))
    #@+node:ekr.20160523100504.1: *4* f.Await (Python 3)
    # Await(expr value)

    def do_Await(self, node):

        return self.indent('await %s\n' % (
            self.visit(node.value)))
    #@+node:ekr.20141012064706.18446: *4* f.Break
    def do_Break(self, node):
        return self.indent('break\n')
    #@+node:ekr.20141012064706.18447: *4* f.Continue
    def do_Continue(self, node):
        return self.indent('continue\n')
    #@+node:ekr.20141012064706.18448: *4* f.Delete
    def do_Delete(self, node):
        targets = [self.visit(z) for z in node.targets]
        return self.indent('del %s\n' % ','.join(targets))
    #@+node:ekr.20141012064706.18449: *4* f.ExceptHandler
    def do_ExceptHandler(self, node):
        result = []
        result.append(self.indent('except'))
        if getattr(node, 'type', None):
            result.append(' %s' % self.visit(node.type))
        if getattr(node, 'name', None):
            if isinstance(node.name, ast.AST):
                result.append(' as %s' % self.visit(node.name))
            else:
                result.append(' as %s' % node.name) # Python 3.x.
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
        args = [] # Globals before locals.
        if getattr(node, 'globals', None):
            args.append(self.visit(node.globals))
        if getattr(node, 'locals', None):
            args.append(self.visit(node.locals))
        if args:
            return self.indent('exec %s in %s\n' % (
                body, ','.join(args)))
        else:
            return self.indent('exec %s\n' % (body))
    #@+node:ekr.20141012064706.18451: *4* f.For & AsnchFor (Python 3)
    def do_For(self, node, async_flag=False):
        result = []
        result.append(self.indent('%sfor %s in %s:\n' % (
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
        return self.indent('global %s\n' % (
            ','.join(node.names)))
    #@+node:ekr.20141012064706.18453: *4* f.If
    def do_If(self, node):
        result = []
        result.append(self.indent('if %s:\n' % (
            self.visit(node.test))))
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
    #@+node:ekr.20141012064706.18454: *4* f.Import & helper
    def do_Import(self, node):
        names = []
        for fn, asname in self.get_import_names(node):
            if asname:
                names.append('%s as %s' % (fn, asname))
            else:
                names.append(fn)
        return self.indent('import %s\n' % (
            ','.join(names)))
    #@+node:ekr.20141012064706.18455: *5* f.get_import_names
    def get_import_names(self, node):
        '''Return a list of the the full file names in the import statement.'''
        result = []
        for ast2 in node.names:
            if self.kind(ast2) == 'alias':
                data = ast2.name, ast2.asname
                result.append(data)
            else:
                g.trace('unsupported kind in Import.names list', self.kind(ast2))
        return result
    #@+node:ekr.20141012064706.18456: *4* f.ImportFrom
    def do_ImportFrom(self, node):
        names = []
        for fn, asname in self.get_import_names(node):
            if asname:
                names.append('%s as %s' % (fn, asname))
            else:
                names.append(fn)
        return self.indent('from %s import %s\n' % (
            node.module,
            ','.join(names)))
    #@+node:ekr.20160317050557.2: *4* f.Nonlocal (Python 3)
    # Nonlocal(identifier* names)

    def do_Nonlocal(self, node):

        return self.indent('nonlocal %s\n' % ', '.join(node.names))
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
            vals.append('dest=%s' % self.visit(node.dest))
        if getattr(node, 'nl', None):
            # vals.append('nl=%s' % self.visit(node.nl))
            vals.append('nl=%s' % node.nl)
        return self.indent('print(%s)\n' % (
            ','.join(vals)))
    #@+node:ekr.20141012064706.18459: *4* f.Raise
    # Raise(expr? type, expr? inst, expr? tback)    Python 2
    # Raise(expr? exc, expr? cause)                 Python 3

    def do_Raise(self, node):
        args = []
        attrs = ('exc', 'cause') if g.isPython3 else ('type', 'inst', 'tback')
        for attr in attrs:
            if getattr(node, attr, None) is not None:
                args.append(self.visit(getattr(node, attr)))
        if args:
            return self.indent('raise %s\n' % (
                ','.join(args)))
        else:
            return self.indent('raise\n')
    #@+node:ekr.20141012064706.18460: *4* f.Return
    def do_Return(self, node):
        if node.value:
            return self.indent('return %s\n' % (
                self.visit(node.value)))
        else:
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

    def do_Try(self, node): # Python 3

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
        result.append(self.indent('while %s:\n' % (
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
        result.append(self.indent('%swith ' % ('async ' if async_flag else '')))
        if getattr(node, 'context_expression', None):
            result.append(self.visit(node.context_expresssion))
        vars_list = []
        if getattr(node, 'optional_vars', None):
            try:
                for z in node.optional_vars:
                    vars_list.append(self.visit(z))
            except TypeError: # Not iterable.
                vars_list.append(self.visit(node.optional_vars))
        if getattr(node, 'items', None): # Python 3.
            for item in node.items:
                result.append(self.visit(item.context_expr))
                if getattr(item, 'optional_vars', None):
                    try:
                        for z in item.optional_vars:
                            vars_list.append(self.visit(z))
                    except TypeError: # Not iterable.
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
            return self.indent('yield %s\n' % (
                self.visit(node.value)))
        else:
            return self.indent('yield\n')
    #@+node:ekr.20160317050557.5: *4* f.YieldFrom (Python 3)
    # YieldFrom(expr value)

    def do_YieldFrom(self, node):

        return self.indent('yield from %s\n' % (
            self.visit(node.value)))
    #@+node:ekr.20141012064706.18467: *3* f.Utils
    #@+node:ekr.20141012064706.18468: *4* f.kind
    def kind(self, node):
        '''Return the name of node's class.'''
        return node.__class__.__name__
    #@+node:ekr.20141012064706.18469: *4* f.indent
    def indent(self, s):
        return '%s%s' % (' ' * 4 * self.level, s)
    #@-others
#@+node:ekr.20141012064706.18471: ** class AstFullTraverser
class AstFullTraverser(object):
    '''
    A fast traverser for AST trees: it visits every node (except node.ctx fields).

    Sets .context and .parent ivars before visiting each node.
    '''

    def __init__(self):
        '''Ctor for AstFullTraverser class.'''
        self.context = None
        self.level = 0 # The context level only.
        self.parent = None
        self.trace = False
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
        if getattr(node, 'keywords', None): # Python 3
            for keyword in node.keywords:
                self.visit(keyword.value)
        if getattr(node, 'starargs', None): # Python 3
            self.visit(node.starargs)
        if getattr(node, 'kwargs', None): # Python 3
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
        assert g.isString(node.name)
        self.visit(node.args)
        if getattr(node, 'returns', None): # Python 3.
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
    #@+node:ekr.20141012064706.18479: *3* ft.kind
    def kind(self, node):
        return node.__class__.__name__
    #@+node:ekr.20171214200319.1: *3* ft.format
    def format(self, node, level, *args, **keys):
        '''Format the node and possibly its descendants, depending on args.'''
        s = AstFormatter().format(node, level, *args, **keys)
        return s.rstrip()
    #@+node:ekr.20141012064706.18480: *3* ft.operators & operands
    #@+node:ekr.20160521102250.1: *4* ft.op_name
    def op_name (self,node,strict=True):
        '''Return the print name of an operator node.'''
        name = _op_names.get(self.kind(node),'<%s>' % node.__class__.__name__)
        if strict: assert name, self.kind(node)
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
        if g.isPython3 and getattr(node, 'vararg', None):
            # An identifier in Python 2.
            self.visit(node.vararg)
        if g.isPython3 and getattr(node, 'kwarg', None):
            # An identifier in Python 2.
            self.visit_list(node.kwarg)
        if getattr(node, 'kwonlyargs', None): # Python 3.
            self.visit_list(node.kwonlyargs)
        if getattr(node, 'kw_defaults', None): # Python 3.
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
        pass # Python 3.x only.
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
        self.visit(node.target) # A name.
        self.visit(node.iter) # An attribute.
        for z in node.ifs:
            self.visit(z)
    #@+node:ekr.20170721073315.1: *4* ft.Constant (Python 3.6+)
    def do_Constant(self, node): # Python 3.6+ only.
        assert g.isPython3
    #@+node:ekr.20141012064706.18489: *4* ft.Dict
    # Dict(expr* keys, expr* values)

    def do_Dict(self, node):
        # Visit all nodes in token order.
        assert len(node.keys) == len(node.values)
        for i in range(len(node.keys)):
            self.visit(node.keys[i])
            self.visit(node.values[i])
    #@+node:ekr.20160523094910.1: *4* ft.DictComp (new)
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
        '''An inner expression'''
        self.visit(node.body)
    #@+node:ekr.20141012064706.18492: *4* ft.ExtSlice
    def do_ExtSlice(self, node):
        for z in node.dims:
            self.visit(z)
    #@+node:ekr.20170721075714.1: *4* ft.FormattedValue (Python 3.6+)
    # FormattedValue(expr value, int? conversion, expr? format_spec)

    def do_FormattedValue(self, node): # Python 3.6+ only.
        assert g.isPython3
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
        assert g.isPython3
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

    def do_NameConstant(self, node): # Python 3 only.
        pass
        # s = repr(node.value)
        # return 'bool' if s in ('True', 'False') else s

    #@+node:ekr.20150522081736.1: *4* ft.Num
    def do_Num(self, node):
        pass # Num(object n) # a number as a PyObject.
    #@+node:ekr.20141012064706.18499: *4* ft.Repr
    # Python 2.x only
    # Repr(expr value)

    def do_Repr(self, node):
        self.visit(node.value)
    #@+node:ekr.20160523094939.1: *4* ft.Set (new)
    # Set(expr* elts)

    def do_Set(self, node):
        for z in node.elts:
            self.visit(z)

    #@+node:ekr.20160523095142.1: *4* ft.SetComp (new)
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
        pass # represents a string constant.
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
        # g.trace('FT',Utils().format(node),g.callers())
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

        attrs = ('exc', 'cause') if g.isPython3 else ('type', 'inst', 'tback')
        for attr in attrs:
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
        self.visit(node.test) # Bug fix: 2013/03/23.
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
        if getattr(node, 'items', None): # Python 3.
            for item in node.items:
                self.visit(item.context_expr)
                if getattr(item, 'optional_vars', None):
                    try:
                        for z in item.optional_vars:
                            self.visit(z)
                    except TypeError: # Not iterable.
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
        '''Visit a *single* ast node.  Visitors are responsible for visiting children!'''
        trace = False
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
            if trace: g.trace(g.truncate(repr(do_method), 80))
            val = do_method(node)
        elif trace:
            g.trace('no do_%s method' % name)
            val = None
        after_method = getattr(self, 'after_'+name, None)
        if after_method:
            after_method(node)
        self.parent = old_parent
        return val

    def visit_children(self, node):
        assert False, 'must visit children explicitly'
    #@+node:ekr.20141012064706.18529: *3* ft.visit_list
    def visit_list(self, aList):
        '''Visit all ast nodes in aList or ast.node.'''
        if isinstance(aList, (list, tuple)):
            for z in aList:
                self.visit(z)
            return None
        elif isinstance(aList, ast.AST):
            return self.visit(aList)
        else:
            g.trace('(CCTraverser) ===== oops', repr(aList), g.callers())
            return None
    #@-others
#@+node:ekr.20141012064706.18530: ** class AstPatternFormatter (AstFormatter)
class AstPatternFormatter(AstFormatter):
    '''
    A subclass of AstFormatter that replaces values of constants by Bool,
    Bytes, Int, Name, Num or Str.
    '''
    # No ctor.
    #@+others
    #@+node:ekr.20141012064706.18531: *3* Constants & Name
    # Return generic markers allow better pattern matches.

    def do_BoolOp(self, node): # Python 2.x only.
        return 'Bool'

    def do_Bytes(self, node): # Python 3.x only.
        assert g.isPython3
        return 'Bytes' # return str(node.s)
        
    def do_Constant(self, node): # Python 3.6+ only.
        assert g.isPython3
        return 'Constant'

    def do_Name(self, node):
        return 'Bool' if node.id in ('True', 'False') else node.id

    def do_NameConstant(self, node): # Python 3 only.
        s = repr(node.value)
        return 'Bool' if s in ('True', 'False') else s

    def do_Num(self, node):
        return 'Num' # return repr(node.n)

    def do_Str(self, node):
        '''This represents a string constant.'''
        return 'Str' # return repr(node.s)
    #@-others
#@+node:ekr.20150722204300.1: ** class HTMLReportTraverser
class HTMLReportTraverser(object):
    '''
    Create html reports from an AST tree.

    Inspired by Paul Boddie.

    This version writes all html to a global code list.

    At present, this code does not show comments.
    The TokenSync class is probably the best way to do this.
    '''
    # To do: revise report-traverser-debug.css.
    # pylint: disable=no-self-argument
    #@+others
    #@+node:ekr.20150722204300.2: *3* rt.__init__
    def __init__(rt, debug=False):
        '''Ctor for the NewHTMLReportTraverser class.'''
        rt.code_list = []
        rt.debug = debug
        rt.div_stack = []
            # A check to ensure matching div/end_div.
        rt.last_doc = None
        # List of divs & spans to generate...
        rt.enable_list = [
            'body', 'class', 'doc', 'function',
            'keyword', 'name', 'statement'
        ]
        # Formatting stuff...
        debug_css = 'report-traverser-debug.css'
        plain_css = 'report-traverser.css'
        rt.css_fn = debug_css if debug else plain_css
        rt.html_footer = '\n</body>\n</html>\n'
        rt.html_header = rt.define_html_header()
    #@+node:ekr.20150722204300.3: *4* define_html_header
    def define_html_header(rt):
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
    def blank(rt):
        '''Insert a single blank.'''
        rt.clean(' ')
        if rt.code_list[-1] not in ' \n':
            rt.gen(' ')
    #@+node:ekr.20150723100208.1: *4* rt.clean
    def clean(rt, s):
        '''Remove s from the code list.'''
        s2 = rt.code_list[-1]
        if s2 == s:
            rt.code_list.pop()
    #@+node:ekr.20150723105702.1: *4* rt.colon
    def colon(rt):

        rt.clean('\n')
        rt.clean(' ')
        rt.clean('\n')
        rt.gen(':')
    #@+node:ekr.20150723100346.1: *4* rt.comma & clean_comma
    def comma(rt):

        rt.clean(' ')
        rt.gen(', ')

    def clean_comma(rt):

        rt.clean(', ')
    #@+node:ekr.20150722204300.21: *4* rt.doc
    # Called by ClassDef & FunctionDef visitors.

    def doc(rt, node):
        doc = ast.get_docstring(node)
        if doc:
            rt.docstring(doc)
            rt.last_doc = doc # Attempt to suppress duplicate.
    #@+node:ekr.20150722204300.22: *4* rt.docstring
    def docstring(rt, s):
        rt.gen("<pre class='doc'>")
        rt.gen('"""')
        rt.gen(rt.text(textwrap.dedent(s.replace('"""', '\\"\\"\\"'))))
        rt.gen('"""')
        rt.gen("</pre>")
    #@+node:ekr.20150722211115.1: *4* rt.gen
    def gen(rt, s):
        '''Append s to the global code list.'''
        if s:
            rt.code_list.append(s)
    #@+node:ekr.20150722204300.23: *4* rt.keyword (code generator)
    def keyword(rt, name):

        rt.blank()
        rt.span('keyword')
        rt.gen(name)
        rt.end_span('keyword')
        rt.blank()
    #@+node:ekr.20150722204300.24: *4* rt.name
    def name(rt, name):

        # Div would put each name on a separate line.
        # span messes up whitespace, for now.
        # rt.span('name')
        rt.gen(name)
        # rt.end_span('name')
    #@+node:ekr.20150723100417.1: *4* rt.newline
    def newline(rt):

        rt.clean(' ')
        rt.clean('\n')
        rt.clean(' ')
        rt.gen('\n')
    #@+node:ekr.20150722204300.26: *4* rt.op
    def op(rt, op_name, leading=False, trailing=True):

        if leading:
            rt.blank()
        # rt.span('operation')
        # rt.span('operator')
        rt.gen(rt.text(op_name))
        # rt.end_span('operator')
        if trailing:
            rt.blank()
        # rt.end_span('operation')
    #@+node:ekr.20150723105951.1: *4* rt.op_name
    #@@nobeautify

    def op_name (rt, node,strict=True):
        '''Return the print name of an operator node.'''
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
    def string(rt, s):

        s = repr(s.strip().strip())
        s = saxutils.escape(s)
        rt.gen(s)
    #@+node:ekr.20150722204300.27: *4* rt.simple_statement
    def simple_statement(rt, name):

        class_name = '%s nowrap' % name
        rt.div(class_name)
        rt.keyword(name)
        rt.end_div(class_name)
    #@+node:ekr.20150722204300.16: *3* rt.html helpers
    #@+node:ekr.20150722204300.17: *4* rt.attr & text
    def attr(rt, s):
        return rt.text(s).replace("'", "&apos;").replace('"', "&quot;")

    def text(rt, s):
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    #@+node:ekr.20150722204300.18: *4* rt.br
    def br(rt):
        return '\n<br />'
    #@+node:ekr.20150722204300.19: *4* rt.comment
    def comment(rt, comment):

        rt.span('comment')
        rt.gen('# ' + comment)
        rt.end_span('comment')
        rt.newline()
    #@+node:ekr.20150722204300.20: *4* rt.div
    def div(rt, class_name, extra=None, wrap=False):
        '''Generate the start of a div element.'''
        if class_name in rt.enable_list:
            if class_name:
                full_class_name = class_name if wrap else class_name + ' nowrap'
            rt.newline()
            if class_name and extra:
                rt.gen("<div class='%s' %s>" % (full_class_name, extra))
            elif class_name:
                rt.newline()
                rt.gen("<div class='%s'>" % (full_class_name))
            else:
                assert not extra
                rt.gen("<div>")
        rt.div_stack.append(class_name)
    #@+node:ekr.20150722222149.1: *4* rt.div_body
    def div_body(rt, aList):
        if aList:
            rt.div_list('body', aList)
    #@+node:ekr.20150722221101.1: *4* rt.div_list & div_node
    def div_list(rt, class_name, aList, sep=None):

        rt.div(class_name)
        rt.visit_list(aList, sep=sep)
        rt.end_div(class_name)

    def div_node(rt, class_name, node):

        rt.div(class_name)
        rt.visit(node)
        rt.end_div(class_name)
    #@+node:ekr.20150723095033.1: *4* rt.end_div
    def end_div(rt, class_name):

        if class_name in rt.enable_list:
            # rt.newline()
            rt.gen('</div>')
            # rt.newline()
        class_name2 = rt.div_stack.pop()
        assert class_name2 == class_name, (class_name2, class_name)
    #@+node:ekr.20150723095004.1: *4* rt.end_span
    def end_span(rt, class_name):

        if class_name in rt.enable_list:
            rt.gen('</span>')
            rt.newline()
        class_name2 = rt.div_stack.pop()
        assert class_name2 == class_name, (class_name2, class_name)
    #@+node:ekr.20150722221408.1: *4* rt.keyword_colon
    # def keyword_colon(rt, keyword):

        # rt.keyword(keyword)
        # rt.colon()
    #@+node:ekr.20150722204300.5: *4* rt.link
    def link(rt, class_name, href, a_text):\

        return "<a class='%s' href='%s'>%s</a>" % (
            class_name, href, a_text)
    #@+node:ekr.20150722204300.6: *4* rt.module_link
    def module_link(rt, module_name, classes=None):

        return rt.link(
            class_name=classes or 'name',
            href='%s.xhtml' % module_name,
            a_text=rt.text(module_name))
    #@+node:ekr.20150722204300.7: *4* rt.name_link
    def name_link(rt, module_name, full_name, name, classes=None):

        return rt.link(
            class_name=classes or "specific-ref",
            href='%s.xhtml#%s' % (module_name, rt.attr(full_name)),
            a_text=rt.text(name))
    #@+node:ekr.20150722204300.8: *4* rt.object_name_ref
    def object_name_ref(rt, module, obj, name=None, classes=None):
        """
        Link to the definition for 'module' using 'obj' with the optional 'name'
        used as the label (instead of the name of 'obj'). The optional 'classes'
        can be used to customise the CSS classes employed.
        """
        return rt.name_link(
            module.full_name(),
            obj.full_name(),
            name or obj.name, classes)
    #@+node:ekr.20150722204300.9: *4* rt.popup
    def popup(rt, classes, aList):

        rt.span_list(classes or 'popup', aList)
    #@+node:ekr.20150722204300.28: *4* rt.span
    def span(rt, class_name, wrap=False):

        if class_name in rt.enable_list:
            rt.newline()
            if class_name:
                full_class_name = class_name if wrap else class_name + ' nowrap'
                rt.gen("<span class='%s'>" % (full_class_name))
            else:
                rt.gen('<span>')
            # rt.newline()
        rt.div_stack.append(class_name)
    #@+node:ekr.20150722224734.1: *4* rt.span_list & span_node
    def span_list(rt, class_name, aList, sep=None):

        rt.span(class_name)
        rt.visit_list(aList, sep=sep)
        rt.end_span(class_name)

    def span_node(rt, class_name, node):

        rt.span(class_name)
        rt.visit(node)
        rt.end_span(class_name)
    #@+node:ekr.20150722204300.10: *4* rt.summary_link
    def summary_link(rt, module_name, full_name, name, classes=None):

        return rt.name_link(
            "%s-summary" % module_name,
            full_name, name,
            classes)
    #@+node:ekr.20160315161259.1: *3* rt.main
    def main(rt, fn, node):
        '''Return a report for the given ast node as a string.'''
        rt.gen(rt.html_header % {
                'css-fn': rt.css_fn,
                'title': 'Module: %s' % fn
            })
        rt.parent = None
        rt.parents = [None]
        rt.visit(node)
        rt.gen(rt.html_footer)
        return ''.join(rt.code_list)
    #@+node:ekr.20150722204300.44: *3* rt.visit
    def visit(rt, node):
        """Walk a tree of AST nodes."""
        assert isinstance(node, ast.AST), node.__class__.__name__
        method_name = 'do_' + node.__class__.__name__
        method = getattr(rt, method_name)
        method(node)
    #@+node:ekr.20150722204300.45: *3* rt.visit_list
    def visit_list(rt, aList, sep=None):
        # pylint: disable=arguments-differ
        if aList:
            for z in aList:
                rt.visit(z)
                rt.gen(sep)
            rt.clean(sep)
    #@+node:ekr.20150722204300.46: *3* rt.visitors
    #@+node:ekr.20170721074613.1: *4* rt.AnnAssign
    # AnnAssign(expr target, expr annotation, expr? value, int simple)

    def do_AnnAssign(rt, node):

        rt.div('statement')
        rt.visit(node.target)
        rt.op('=:', leading=True, trailing=True)
        rt.visit(node.annotation)
        rt.blank()
        rt.visit(node.value)
        rt.end_div('statement')
    #@+node:ekr.20150722204300.49: *4* rt.Assert
    # Assert(expr test, expr? msg)

    def do_Assert(rt, node):

        rt.div('statement')
        rt.keyword("assert")
        rt.visit(node.test)
        if node.msg:
            rt.comma()
            rt.visit(node.msg)
        rt.end_div('statement')
    #@+node:ekr.20150722204300.50: *4* rt.Assign
    def do_Assign(rt, node):

        rt.div('statement')
        for z in node.targets:
            rt.visit(z)
            rt.op('=', leading=True, trailing=True)
        rt.visit(node.value)
        rt.end_div('statement')
    #@+node:ekr.20150722204300.51: *4* rt.Attribute
    # Attribute(expr value, identifier attr, expr_context ctx)

    def do_Attribute(rt, node):

        rt.visit(node.value)
        rt.gen('.')
        rt.gen(node.attr)
    #@+node:ekr.20160523102939.1: *4* rt.Await (Python 3)
    # Await(expr value)

    def do_Await(rt, node):

        rt.div('statement')
        rt.keyword('await')
        rt.visit(node.value)
        rt.end_div('statement')
    #@+node:ekr.20150722204300.52: *4* rt.AugAssign
    #  AugAssign(expr target, operator op, expr value)

    def do_AugAssign(rt, node):

        op_name = rt.op_name(node.op)
        rt.div('statement')
        rt.visit(node.target)
        rt.op(op_name, leading=True)
        rt.visit(node.value)
        rt.end_div('statement')
    #@+node:ekr.20150722204300.53: *4* rt.BinOp
    def do_BinOp(rt, node):

        op_name = rt.op_name(node.op)
        # rt.span(op_name)
        rt.visit(node.left)
        rt.op(op_name, leading=True)
        rt.visit(node.right)
        # rt.end_span(op_name)
    #@+node:ekr.20150722204300.54: *4* rt.BoolOp
    def do_BoolOp(rt, node):

        op_name = rt.op_name(node.op).strip()
        rt.span(op_name)
        for i, node2 in enumerate(node.values):
            if i > 0:
                rt.keyword(op_name)
            rt.visit(node2)
        rt.end_span(op_name)
    #@+node:ekr.20150722204300.55: *4* rt.Break
    def do_Break(rt, node):

        rt.simple_statement('break')
    #@+node:ekr.20160523103529.1: *4* rt.Bytes (Python 3)
    def do_Bytes(rt, node): # Python 3.x only.
        return str(node.s)
    #@+node:ekr.20150722204300.56: *4* rt.Call & do_keyword
    # Call(expr func, expr* args, keyword* keywords, expr? starargs, expr? kwargs)

    def do_Call(rt, node):

        # rt.span("callfunc")
        rt.visit(node.func)
        # rt.span("call")
        rt.gen('(')
        rt.visit_list(node.args, sep=',')
        if node.keywords:
            rt.visit_list(node.keywords, sep=',')
        if getattr(node, 'starargs', None):
            rt.op('*', trailing=False)
            rt.visit(node.starargs)
            rt.comma()
        if getattr(node, 'kwargs', None):
            rt.op('**', trailing=False)
            rt.visit(node.kwargs)
            rt.comma()
        rt.clean_comma()
        rt.gen(')')
        # rt.end_span('call')
        # rt.end_span('callfunc')
    #@+node:ekr.20150722204300.57: *5* rt.do_keyword
    # keyword = (identifier arg, expr value)
    # keyword arguments supplied to call

    def do_keyword(rt, node):

        rt.span('keyword-arg')
        rt.gen(node.arg)
        rt.blank()
        rt.gen('=')
        rt.blank()
        rt.visit(node.value)
        rt.end_span('keyword-arg')
    #@+node:ekr.20150722204300.58: *4* rt.ClassDef
    # 2: ClassDef(identifier name, expr* bases,
    #             stmt* body, expr* decorator_list)
    # 3: ClassDef(identifier name, expr* bases,
    #             keyword* keywords, expr? starargs, expr? kwargs
    #             stmt* body, expr* decorator_list)
    #
    # keyword arguments supplied to call (NULL identifier for **kwargs)
    # keyword = (identifier? arg, expr value)

    def do_ClassDef(rt, node):

        has_bases = (node.bases or hasattr(node, 'keywords') or
            hasattr(node, 'starargs') or hasattr(node, 'kwargs'))
        rt.div('class')
        rt.keyword("class")
        rt.gen(node.name) # Always a string.
        if has_bases:
            rt.gen('(')
            rt.visit_list(node.bases, sep=', ')
            if getattr(node, 'keywords', None): # Python 3
                for keyword in node.keywords:
                    rt.gen('%s=%s' % (keyword.arg, rt.visit(keyword.value)))
            if getattr(node, 'starargs', None): # Python 3
                rt.gen('*%s' % rt.visit(node.starargs))
            if getattr(node, 'kwargs', None): # Python 3
                rt.gen('*%s' % rt.visit(node.kwargs))
            rt.gen(')')
        rt.colon()
        rt.div('body')
        rt.doc(node)
        rt.visit_list(node.body)
        rt.end_div('body')
        rt.end_div('class')
    #@+node:ekr.20150722204300.59: *4* rt.Compare
    def do_Compare(rt, node):

        assert len(node.ops) == len(node.comparators)
        # rt.span('compare')
        rt.visit(node.left)
        for i in range(len(node.ops)):
            op_name = rt.op_name(node.ops[i])
            rt.op(op_name, leading=True)
            rt.visit(node.comparators[i])
        # rt.end_span('compare')
    #@+node:ekr.20150722204300.60: *4* rt.comprehension
    # comprehension = (expr target, expr iter, expr* ifs)

    def do_comprehension(rt, node):

        rt.visit(node.target)
        rt.keyword('in')
        # rt.span('collection')
        rt.visit(node.iter)
        if node.ifs:
            rt.keyword('if')
            # rt.span_list("conditional", node.ifs, sep=' ')
            for z in node.ifs:
                rt.visit(z)
                rt.blank()
            rt.clean(' ')
        # rt.end_span('collection')
    #@+node:ekr.20170721073431.1: *4* rt.Constant (Python 3.6+)
    def do_Constant(self, node): # Python 3.6+ only.
        assert g.isPython3
        return str(node.s) # A guess.
    #@+node:ekr.20150722204300.61: *4* rt.Continue
    def do_Continue(rt, node):

        rt.simple_statement('continue')
    #@+node:ekr.20150722204300.62: *4* rt.Delete
    def do_Delete(rt, node):

        rt.div('statement')
        rt.keyword('del')
        if node.targets:
            rt.visit_list(node.targets, sep=',')
        rt.end_div('statement')
    #@+node:ekr.20150722204300.63: *4* rt.Dict
    def do_Dict(rt, node):

        assert len(node.keys) == len(node.values)
        # rt.span('dict')
        rt.gen('{')
        for i in range(len(node.keys)):
            rt.visit(node.keys[i])
            rt.colon()
            rt.visit(node.values[i])
            rt.comma()
        rt.clean_comma()
        rt.gen('}')
        # rt.end_span('dict')
    #@+node:ekr.20160523104330.1: *4* rt.DictComp (new)
    # DictComp(expr key, expr value, comprehension* generators)

    def do_DictComp(self, node):
        elt = self.visit(node.elt)
        gens = [self.visit(z) for z in node.generators]
        gens = [z if z else '<**None**>' for z in gens] # Kludge: probable bug.
        return '%s for %s' % (elt, ''.join(gens))
    #@+node:ekr.20150722204300.47: *4* rt.do_arguments & helpers
    # arguments = (expr* args, identifier? vararg, identifier? kwarg, expr* defaults)

    def do_arguments(rt, node):

        assert isinstance(node, ast.arguments), node
        first_default = len(node.args) - len(node.defaults)
        for n, arg in enumerate(node.args):
            if isinstance(arg, (list,tuple)):
                rt.tuple_parameter(arg)
            else:
                rt.visit(arg)
            if n >= first_default:
                default = node.defaults[n - first_default]
                rt.gen("=")
                rt.visit(default)
            rt.comma()
        if getattr(node, 'vararg', None):
            rt.gen('*')
            rt.gen(rt.name(node.vararg))
            rt.comma()
        if getattr(node, 'kwarg', None):
            rt.gen('**')
            rt.gen(rt.name(node.kwarg))
            rt.comma()
        rt.clean_comma()
    #@+node:ekr.20160315182225.1: *5* rt.arg (Python 3 only)
    # 3: arg = (identifier arg, expr? annotation)

    def do_arg(rt, node):

        rt.gen(node.arg)
        if getattr(node, 'annotation', None):
            rt.colon()
            rt.visit(node.annotation)
    #@+node:ekr.20150722204300.48: *5* rt.tuple_parameter
    def tuple_parameter(rt, node):

        assert isinstance(node, (list, tuple)), node
        rt.gen("(")
        for param in node:
            if isinstance(param, tuple):
                rt.tuple_parameter(param)
            else:
                rt.visit(param)
        rt.gen(")")
    #@+node:ekr.20150722204300.64: *4* rt.Ellipsis
    def do_Ellipsis(rt, node):

        rt.gen('...')
    #@+node:ekr.20150722204300.65: *4* rt.ExceptHandler
    def do_ExceptHandler(rt, node):

        rt.div('excepthandler')
        rt.keyword("except")
        if not node.type:
            rt.clean(' ')
        if node.type:
            rt.visit(node.type)
        if node.name:
            rt.keyword('as')
            rt.visit(node.name)
        rt.colon()
        rt.div_body(node.body)
        rt.end_div('excepthandler')
    #@+node:ekr.20150722204300.66: *4* rt.Exec
    # Python 2.x only.

    def do_Exec(rt, node):

        rt.div('statement')
        rt.keyword('exec')
        rt.visit(node.body)
        if node.globals:
            rt.comma()
            rt.visit(node.globals)
        if node.locals:
            rt.comma()
            rt.visit(node.locals)
        rt.end_div('statement')
    #@+node:ekr.20150722204300.67: *4* rt.Expr
    def do_Expr(rt, node):

        rt.div_node('expr', node.value)
    #@+node:ekr.20160523103429.1: *4* rf.Expression (New)
    def do_Expression(rt, node):
        '''An inner expression: do not indent.'''
        return '%s' % rt.visit(node.body)
    #@+node:ekr.20160523103751.1: *4* rt.ExtSlice (New)
    def do_ExtSlice(rt, node):
        return ':'.join([rt.visit(z) for z in node.dims])
    #@+node:ekr.20150722204300.68: *4* rt.For & AsyncFor (Python 3)
    # For(expr target, expr iter, stmt* body, stmt* orelse)

    def do_For(rt, node, async_flag=False):

        rt.div('statement')
        if async_flag:
            rt.keyword('async')
        rt.keyword("for")
        rt.visit(node.target)
        rt.keyword("in")
        rt.visit(node.iter)
        rt.colon()
        rt.div_body(node.body)
        if node.orelse:
            rt.keyword('else')
            rt.colon()
            rt.div_body(node.orelse)
        rt.end_div('statement')

    def do_AsyncFor(rt, node):
        rt.do_For(node, async_flag=True)
    #@+node:ekr.20170721075845.1: *4* rf.FormattedValue (Python 3.6+: unfinished)
    # FormattedValue(expr value, int? conversion, expr? format_spec)

    def do_FormattedValue(rt, node): # Python 3.6+ only.
        assert g.isPython3
        rt.div('statement')
        rt.visit(node.value)
        if node.conversion:
            rt.visit(node.conversion)
        if node.format_spec:
            rt.visit(node.format_spec)
        rt.end_div('statement')
    #@+node:ekr.20150722204300.69: *4* rt.FunctionDef
    # 2: FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list)
    # 3: FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list,
    #                expr? returns)

    def do_FunctionDef(rt, node, async_flag=False):

        rt.div('function', extra='id="%s"' % node.name)
        if async_flag:
            rt.keyword('async')
        rt.keyword("def")
        rt.name(node.name)
        rt.gen('(')
        rt.visit(node.args)
        rt.gen(')')
        if getattr(node, 'returns', None):
            rt.blank()
            rt.gen('->')
            rt.blank()
            rt.visit(node.returns)
        rt.colon()
        rt.div('body')
        rt.doc(node)
        rt.visit_list(node.body)
        rt.end_div('body')
        rt.end_div('function')

    def do_AsyncFunctionDef(rt, node):
        rt.do_FunctionDef(node, async_flag=True)
    #@+node:ekr.20150722204300.70: *4* rt.GeneratorExp
    def do_GeneratorExp(rt, node):

        # rt.span('genexpr')
        rt.gen('(')
        if node.elt:
            rt.visit(node.elt)
        rt.keyword('for')
        # rt.span_node('item', node.elt)
        rt.visit(node.elt)
        # rt.span_list('generators', node.generators)
        rt.visit_list(node.generators)
        rt.gen(')')
        # rt.end_span('genexpr')
    #@+node:ekr.20150722204300.71: *4* rt.get_import_names
    def get_import_names(rt, node):
        '''Return a list of the the full file names in the import statement.'''
        result = []
        for ast2 in node.names:
            if isinstance(ast2, ast.alias):
                data = ast2.name, ast2.asname
                result.append(data)
            else:
                g.trace('unsupported node in Import.names list', node.__class__.__name__)
        return result
    #@+node:ekr.20150722204300.72: *4* rt.Global
    def do_Global(rt, node):

        rt.div('statement')
        rt.keyword("global")
        for z in node.names:
            rt.gen(z)
            rt.comma()
        rt.clean_comma()
        rt.end_div('statement')
    #@+node:ekr.20150722204300.73: *4* rt.If
    # If(expr test, stmt* body, stmt* orelse)

    def do_If(rt, node, elif_flag=False):

        rt.div('statement')
        rt.keyword('elif' if elif_flag else 'if')
        rt.visit(node.test)
        rt.colon()
        rt.div_body(node.body)
        if node.orelse:
            node1 = node.orelse[0]
            if isinstance(node1, ast.If) and len(node.orelse) == 1:
                rt.do_If(node1, elif_flag=True)
            else:
                rt.keyword('else')
                rt.colon()
                rt.div_body(node.orelse)
        rt.end_div('statement')
    #@+node:ekr.20150722204300.74: *4* rt.IfExp (TernaryOp)
    # IfExp(expr test, expr body, expr orelse)

    def do_IfExp(rt, node):

        # rt.span('ifexp')
        rt.visit(node.body)
        rt.keyword('if')
        rt.visit(node.test)
        rt.keyword('else')
        rt.visit(node.orelse)
        # rt.end_span('ifexp')
    #@+node:ekr.20150722204300.75: *4* rt.Import
    def do_Import(rt, node):

        rt.div('statement')
        rt.keyword("import")
        for name, alias in rt.get_import_names(node):
            rt.name(name) # rt.gen(rt.module_link(name))
            if alias:
                rt.keyword("as")
                rt.name(alias)
        rt.end_div('statement')
    #@+node:ekr.20150722204300.76: *4* rt.ImportFrom
    def do_ImportFrom(rt, node):

        rt.div('statement')
        rt.keyword("from")
        rt.gen(rt.module_link(node.module))
        rt.keyword("import")
        for name, alias in rt.get_import_names(node):
            rt.name(name)
            if alias:
                rt.keyword("as")
                rt.name(alias)
            rt.comma()
        rt.clean_comma()
        rt.end_div('statement')
    #@+node:ekr.20160315190818.1: *4* rt.Index
    def do_Index(rt, node):

        rt.visit(node.value)
    #@+node:ekr.20170721080959.1: *4* rf.JoinedStr (Python 3.6+: unfinished)
    # JoinedStr(expr* values)

    def do_JoinedStr(rt, node):
        assert g.isPython3
        for value in node.values or []:
            rt.visit(value)
    #@+node:ekr.20150722204300.77: *4* rt.Lambda
    def do_Lambda(rt, node):

        # rt.span('lambda')
        rt.keyword('lambda')
        rt.visit(node.args)
        rt.comma()
        rt.span_node("code", node.body)
        # rt.end_span('lambda')
    #@+node:ekr.20150722204300.78: *4* rt.List
    # List(expr* elts, expr_context ctx)

    def do_List(rt, node):

        # rt.span('list')
        rt.gen('[')
        if node.elts:
            for z in node.elts:
                rt.visit(z)
                rt.comma()
            rt.clean_comma()
        rt.gen(']')
        # rt.end_span('list')
    #@+node:ekr.20150722204300.79: *4* rt.ListComp
    # ListComp(expr elt, comprehension* generators)

    def do_ListComp(rt, node):

        # rt.span('listcomp')
        rt.gen('[')
        if node.elt:
            rt.visit(node.elt)
        rt.keyword('for')
        # rt.span('ifgenerators')
        rt.visit_list(node.generators)
        rt.gen(']')
        # rt.end_span('ifgenerators')
        # rt.end_span('listcomp')
    #@+node:ekr.20150722204300.80: *4* rt.Module
    def do_Module(rt, node):

        rt.doc(node)
        rt.visit_list(node.body)
    #@+node:ekr.20150722204300.81: *4* rt.Name
    def do_Name(rt, node):

        rt.name(node.id)
    #@+node:ekr.20160315165109.1: *4* rt.NameConstant
    def do_NameConstant(rt, node): # Python 3 only.

        rt.name(repr(node.value))
    #@+node:ekr.20160317051849.2: *4* rt.Nonlocal (Python 3)
    # Nonlocal(identifier* names)

    def do_Nonlocal(rt, node):

        rt.div('statement')
        rt.keyword('nonlocal')
        rt.gen(', '.join(node.names))
        rt.end_div('statement')
    #@+node:ekr.20150722204300.82: *4* rt.Num
    def do_Num(rt, node):

        rt.gen(rt.text(repr(node.n)))
    #@+node:ekr.20150722204300.83: *4* rt.Pass
    def do_Pass(rt, node):

        rt.simple_statement('pass')
    #@+node:ekr.20150722204300.84: *4* rt.Print
    # Print(expr? dest, expr* values, bool nl)

    def do_Print(rt, node):

        rt.div('statement')
        rt.keyword("print")
        rt.gen('(')
        if node.dest:
            rt.op('>>\n')
            rt.visit(node.dest)
            rt.comma()
            rt.newline()
            if node.values:
                for z in node.values:
                    rt.visit(z)
                    rt.comma()
                    rt.newline()
        rt.clean('\n')
        rt.clean_comma()
        rt.gen(')')
        rt.end_div('statement')
    #@+node:ekr.20150722204300.85: *4* rt.Raise
    # Raise(expr? type, expr? inst, expr? tback)    Python 2
    # Raise(expr? exc, expr? cause)                 Python 3

    def do_Raise(rt, node):

        rt.div('statement')
        rt.keyword("raise")
        attrs = ('exc', 'cause') if g.isPython3 else ('type', 'inst', 'tback')
        for attr in attrs:
            if getattr(node, attr, None) is not None:
                rt.visit(getattr(node, attr))
        rt.end_div('statement')
    #@+node:ekr.20160523105022.1: *4* rt.Repr
    # Python 2.x only

    def do_Repr(rt, node):
        return 'repr(%s)' % rt.visit(node.value)
    #@+node:ekr.20150722204300.86: *4* rt.Return
    def do_Return(rt, node):

        rt.div('statement')
        rt.keyword("return")
        if node.value:
            rt.visit(node.value)
        rt.end_div('statement')
    #@+node:ekr.20160523104433.1: *4* rt.Set (new)
    # Set(expr* elts)

    def do_Set(self, node):
        for z in node.elts:
            self.visit(z)
    #@+node:ekr.20160523104454.1: *4* rt.SetComp (new)
    # SetComp(expr elt, comprehension* generators)

    def do_SetComp(self, node):

        elt = self.visit(node.elt)
        gens = [self.visit(z) for z in node.generators]
        return '%s for %s' % (elt, ''.join(gens))
    #@+node:ekr.20150722204300.87: *4* rt.Slice
    def do_Slice(rt, node):

        # rt.span("slice")
        if node.lower:
            rt.visit(node.lower)
        rt.colon()
        if node.upper:
            rt.visit(node.upper)
        if node.step:
            rt.colon()
            rt.visit(node.step)
        # rt.end_span("slice")
    #@+node:ekr.20160317051849.3: *4* rt.Starred (Python 3)
    # Starred(expr value, expr_context ctx)

    def do_Starred(rt, node):

        rt.gen('*')
        rt.visit(node.value)
    #@+node:ekr.20150722204300.88: *4* rt.Str
    def do_Str(rt, node):
        '''This represents a string constant.'''

        def clean(s):
            return s.replace(' ','').replace('\n','').replace('"','').replace("'",'')

        assert g.isString(node.s)
        if rt.last_doc and clean(rt.last_doc) == clean(node.s):
            # Already seen.
            rt.last_doc = None
        else:
            rt.string(node.s)
    #@+node:ekr.20150722204300.89: *4* rt.Subscript
    def do_Subscript(rt, node):

        # rt.span("subscript")
        rt.visit(node.value)
        rt.gen('[')
        rt.visit(node.slice)
        rt.gen(']')
        # rt.end_span("subscript")
    #@+node:ekr.20160315190913.1: *4* rt.Try (Python 3)
    # Try(stmt* body, excepthandler* handlers, stmt* orelse, stmt* finalbody)

    def do_Try(rt, node):

        rt.div('statement')
        rt.keyword('try')
        rt.colon()
        rt.div_list('body', node.body)
        for z in node.handlers:
            rt.visit(z)
        for z in node.orelse:
            rt.visit(z)
        if node.finalbody:
            rt.keyword('finally')
            rt.colon()
            rt.div_list('body', node.finalbody)
        rt.end_div('statement')
    #@+node:ekr.20150722204300.90: *4* rt.TryExcept
    def do_TryExcept(rt, node):

        rt.div('statement')
        rt.keyword('try')
        rt.colon()
        rt.div_list('body', node.body)
        if node.orelse:
            rt.keyword('else')
            rt.colon()
            rt.div_body(node.orelse)
        rt.div_body(node.handlers)
        rt.end_div('statement')
    #@+node:ekr.20150722204300.91: *4* rt.TryFinally
    def do_TryFinally(rt, node):

        rt.div('statement')
        rt.keyword('try')
        rt.colon()
        rt.div_body(node.body)
        rt.keyword('finally')
        rt.colon()
        rt.div_body(node.final.body)
        rt.end_div('statement')
    #@+node:ekr.20150722204300.92: *4* rt.Tuple
    # Tuple(expr* elts, expr_context ctx)

    def do_Tuple(rt, node):

        # rt.span('tuple')
        rt.gen('(')
        for z in node.elts or []:
            # g.trace(z)
            rt.visit(z)
            rt.comma()
        rt.clean_comma()
        rt.gen(')')
        # rt.end_span('tuple')
    #@+node:ekr.20150722204300.93: *4* rt.UnaryOp
    def do_UnaryOp(rt, node):

        op_name = rt.op_name(node.op).strip()
        # rt.span(op_name)
        rt.op(op_name, trailing=False)
        rt.visit(node.operand)
        # rt.end_span(op_name)
    #@+node:ekr.20150722204300.94: *4* rt.While
    def do_While(rt, node):

        rt.div('statement')
        rt.div(None)
        rt.keyword("while")
        rt.visit(node.test)
        rt.colon()
        rt.end_div(None)
        rt.div_list('body', node.body)
        if node.orelse:
            rt.keyword('else')
            rt.colon()
            rt.div_body(node.orelse)
        rt.end_div('statement')
    #@+node:ekr.20150722204300.95: *4* rt.With & AsyncWith (Python 3)
    # 2:  With(expr context_expr, expr? optional_vars,
    #          stmt* body)
    # 3:  With(withitem* items,
    #          stmt* body)
    # withitem = (expr context_expr, expr? optional_vars)

    def do_With(rt, node, async_flag=False):

        context_expr = getattr(node, 'context_expr', None)
        optional_vars = getattr(node, 'optional_vars', None)
        items = getattr(node, 'items', None)
        rt.div('statement')
        if async_flag:
            rt.keyword('async')
        rt.keyword('with')
        if context_expr:
            rt.visit(context_expr)
        if optional_vars:
            rt.keyword('as')
            rt.visit_list(optional_vars)
        if items:
            for item in items:
                rt.visit(item.context_expr)
                if getattr(item, 'optional_vars', None):
                    rt.keyword('as')
                    rt.visit(item.optional_vars)
        rt.colon()
        rt.div_body(node.body)
        rt.end_div('statement')

    def do_AsyncWith(rt, node):
        rt.do_With(node, async_flag=True)
    #@+node:ekr.20150722204300.96: *4* rt.Yield
    def do_Yield(rt, node):

        rt.div('statement')
        rt.keyword('yield')
        rt.visit(node.value)
        rt.end_div('statement')
    #@+node:ekr.20160317051849.5: *4* rt.YieldFrom (Python 3)
    # YieldFrom(expr value)

    def do_YieldFrom(rt, node):

        rt.div('statement')
        rt.keyword('yield from')
        rt.visit(node.value)
        rt.end_div('statement')
    #@-others
#@+node:ekr.20160225102931.1: ** class TokenSync
class TokenSync(object):
    '''A class to sync and remember tokens.'''
    # To do: handle comments, line breaks...
    #@+others
    #@+node:ekr.20160225102931.2: *3*  ts.ctor & helpers
    def __init__(self, s, tokens):
        '''Ctor for TokenSync class.'''
        assert isinstance(tokens, list) # Not a generator.
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
        '''Return of list of line numbers of blank lines.'''
        result = []
        for i, aList in enumerate(self.line_tokens):
            # if any([self.token_kind(z) == 'nl' for z in aList]):
            if len(aList) == 1 and self.token_kind(aList[0]) == 'nl':
                result.append(i)
        return result
    #@+node:ekr.20160225102931.4: *4* ts.make_ignored_lines
    def make_ignored_lines(self):
        '''
        Return a copy of line_tokens containing ignored lines,
        that is, full-line comments or blank lines.
        These are the lines returned by leading_lines().
        '''
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
        '''
        Return a list of lists of tokens for each list in self.lines.
        The strings in self.lines may end in a backslash, so care is needed.
        '''
        trace = False
        n, result = len(self.lines), []
        for i in range(0, n + 1):
            result.append([])
        for token in tokens:
            t1, t2, t3, t4, t5 = token
            kind = token_module.tok_name[t1].lower()
            srow, scol = t3
            erow, ecol = t4
            line = erow - 1 if kind == 'string' else srow - 1
            result[line].append(token)
            if trace: g.trace('%3s %s' % (line, self.dump_token(token)))
        assert len(self.lines) + 1 == len(result), len(result)
        return result
    #@+node:ekr.20160225102931.6: *4* ts.make_nl_token
    def make_nl_token(self):
        '''Return a newline token with '\n' as both val and raw_val.'''
        t1 = token_module.NEWLINE
        t2 = '\n'
        t3 = (0, 0) # Not used.
        t4 = (0, 0) # Not used.
        t5 = '\n'
        return t1, t2, t3, t4, t5
    #@+node:ekr.20160225102931.7: *4* ts.make_string_tokens
    def make_string_tokens(self):
        '''Return a copy of line_tokens containing only string tokens.'''
        result = []
        for aList in self.line_tokens:
            result.append([z for z in aList if self.token_kind(z) == 'string'])
        assert len(result) == len(self.line_tokens)
        return result
    #@+node:ekr.20160225102931.8: *3* ts.check_strings
    def check_strings(self):
        '''Check that all strings have been consumed.'''
        # g.trace(len(self.string_tokens))
        for i, aList in enumerate(self.string_tokens):
            if aList:
                g.trace('warning: line %s. unused strings: %s' % (i, aList))
    #@+node:ekr.20160225102931.9: *3* ts.dump_token
    def dump_token(self, token, verbose=False):
        '''Dump the token. It is either a string or a 5-tuple.'''
        if g.isString(token):
            return token
        else:
            t1, t2, t3, t4, t5 = token
            kind = g.toUnicode(token_module.tok_name[t1].lower())
            # raw_val = g.toUnicode(t5)
            val = g.toUnicode(t2)
            if verbose:
                return 'token: %10s %r' % (kind, val)
            else:
                return val
    #@+node:ekr.20160225102931.10: *3* ts.is_line_comment
    def is_line_comment(self, token):
        '''Return True if the token represents a full-line comment.'''
        t1, t2, t3, t4, t5 = token
        kind = token_module.tok_name[t1].lower()
        raw_val = t5
        return kind == 'comment' and raw_val.lstrip().startswith('#')
    #@+node:ekr.20160225102931.11: *3* ts.join
    def join(self, aList, sep=','):
        '''return the items of the list joined by sep string.'''
        tokens = []
        for i, token in enumerate(aList or []):
            tokens.append(token)
            if i < len(aList) - 1:
                tokens.append(sep)
        return tokens
    #@+node:ekr.20160225102931.12: *3* ts.last_node
    def last_node(self, node):
        '''Return the node of node's tree with the largest lineno field.'''

        class LineWalker(ast.NodeVisitor):

            def __init__(self):
                '''Ctor for LineWalker class.'''
                self.node = None
                self.lineno = -1

            def visit(self, node):
                '''LineWalker.visit.'''
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
        '''Return a list of the preceding comment and blank lines'''
        # This can be called on arbitrary nodes.
        trace = False
        leading = []
        if hasattr(node, 'lineno'):
            i, n = self.first_leading_line, node.lineno
            while i < n:
                token = self.ignored_lines[i]
                if token:
                    s = self.token_raw_val(token).rstrip() + '\n'
                    leading.append(s)
                    if trace: g.trace('%11s: %s' % (i, s.rstrip()))
                i += 1
            self.first_leading_line = i
        return leading
    #@+node:ekr.20160225102931.14: *3* ts.leading_string
    def leading_string(self, node):
        '''Return a string containing all lines preceding node.'''
        return ''.join(self.leading_lines(node))
    #@+node:ekr.20160225102931.15: *3* ts.line_at
    def line_at(self, node, continued_lines=True):
        '''Return the lines at the node, possibly including continuation lines.'''
        n = getattr(node, 'lineno', None)
        if n is None:
            return '<no line> for %s' % node.__class__.__name__
        elif continued_lines:
            aList, n = [], n - 1
            while n < len(self.lines):
                s = self.lines[n]
                if s.endswith('\\'):
                    aList.append(s[: -1])
                    n += 1
                else:
                    aList.append(s)
                    break
            return ''.join(aList)
        else:
            return self.lines[n - 1]
    #@+node:ekr.20160225102931.16: *3* ts.sync_string
    def sync_string(self, node):
        '''Return the spelling of the string at the given node.'''
        # g.trace('%-10s %2s: %s' % (' ', node.lineno, self.line_at(node)))
        n = node.lineno
        tokens = self.string_tokens[n - 1]
        if tokens:
            token = tokens.pop(0)
            self.string_tokens[n - 1] = tokens
            return self.token_val(token)
        else:
            g.trace('===== underflow', n, node.s)
            return node.s
    #@+node:ekr.20160225102931.17: *3* ts.token_kind/raw_val/val
    def token_kind(self, token):
        '''Return the token's type.'''
        t1, t2, t3, t4, t5 = token
        return g.toUnicode(token_module.tok_name[t1].lower())

    def token_raw_val(self, token):
        '''Return the value of the token.'''
        t1, t2, t3, t4, t5 = token
        return g.toUnicode(t5)

    def token_val(self, token):
        '''Return the raw value of the token.'''
        t1, t2, t3, t4, t5 = token
        return g.toUnicode(t2)
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
        '''
        Return a string containing the trailing comment for the node, if any.
        The string always ends with a newline.
        '''
        if hasattr(node, 'lineno'):
            return self.trailing_comment_at_lineno(node.lineno)
        else:
            g.trace('no lineno', node.__class__.__name__, g.callers())
            return '\n'
    #@+node:ekr.20160225102931.20: *3* ts.trailing_comment_at_lineno
    def trailing_comment_at_lineno(self, lineno):
        '''Return any trailing comment at the given node.lineno.'''
        trace = False
        tokens = self.line_tokens[lineno - 1]
        for token in tokens:
            if self.token_kind(token) == 'comment':
                raw_val = self.token_raw_val(token).rstrip()
                if not raw_val.strip().startswith('#'):
                    val = self.token_val(token).rstrip()
                    s = ' %s\n' % val
                    if trace: g.trace(lineno, s.rstrip(), g.callers())
                    return s
        return '\n'
    #@+node:ekr.20160225102931.21: *3* ts.trailing_lines
    def trailing_lines(self):
        '''return any remaining ignored lines.'''
        trace = False
        trailing = []
        i = self.first_leading_line
        while i < len(self.ignored_lines):
            token = self.ignored_lines[i]
            if token:
                s = self.token_raw_val(token).rstrip() + '\n'
                trailing.append(s)
                if trace: g.trace('%11s: %s' % (i, s.rstrip()))
            i += 1
        self.first_leading_line = i
        return trailing
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo

#@+leo-ver=5-thin
#@+node:ekr.20160123185231.1: * @file make_stub_files.py
'''
The stand-alone version of Leo's make-stub-files command.
Make a stub file in the ~/stubs directory for every file
mentioned in the [Source Files] section of ~/stubs/make_stub_files.cfg.
'''
import ast
try:
    import ConfigParser as configparser # Python 2
except ImportError:
    import configparser # Python 3
import glob
import os
import sys
#@+others
#@+node:ekr.20160123185312.8: ** class AstFormatter
class AstFormatter:
    '''
    A class to recreate source code from an AST.
    
    This does not have to be perfect, but it should be close.
    
    Also supports optional annotations such as line numbers, file names, etc.
    '''
    # No ctor.
    # pylint: disable=consider-using-enumerate
    #@+others
    #@+node:ekr.20160123185312.9: *3*  f.Entries
    #@+node:ekr.20160123185312.10: *4* f.format
    def format(self, node):
        '''Format the node (or list of nodes) and its descendants.'''
        self.level = 0
        val = self.visit(node)
        return val and val.strip() or ''
    #@+node:ekr.20160123185312.11: *4* f.visit
    def visit(self, node):
        '''Return the formatted version of an Ast node, or list of Ast nodes.'''
        if isinstance(node, (list, tuple)):
            return ','.join([self.visit(z) for z in node])
        elif node is None:
            return 'None'
        else:
            assert isinstance(node, ast.AST), node.__class__.__name__
            method_name = 'do_' + node.__class__.__name__
            method = getattr(self, method_name)
            s = method(node)
            # pylint: disable=unidiomatic-typecheck
            assert type(s) == type('abc'), type(s)
            return s
    #@+node:ekr.20160123185312.12: *3* f.Contexts
    #@+node:ekr.20160123185312.13: *4* f.ClassDef
    # ClassDef(identifier name, expr* bases, stmt* body, expr* decorator_list)

    def do_ClassDef(self, node):
        result = []
        name = node.name # Only a plain string is valid.
        bases = [self.visit(z) for z in node.bases] if node.bases else []
        if bases:
            result.append(self.indent('class %s(%s):\n' % (name, ','.join(bases))))
        else:
            result.append(self.indent('class %s:\n' % name))
        for z in node.body:
            self.level += 1
            result.append(self.visit(z))
            self.level -= 1
        return ''.join(result)
    #@+node:ekr.20160123185312.14: *4* f.FunctionDef
    # FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list)

    def do_FunctionDef(self, node):
        '''Format a FunctionDef node.'''
        result = []
        if node.decorator_list:
            for z in node.decorator_list:
                result.append('@%s\n' % self.visit(z))
        name = node.name # Only a plain string is valid.
        args = self.visit(node.args) if node.args else ''
        result.append(self.indent('def %s(%s):\n' % (name, args)))
        for z in node.body:
            self.level += 1
            result.append(self.visit(z))
            self.level -= 1
        return ''.join(result)
    #@+node:ekr.20160123185312.15: *4* f.Interactive
    def do_Interactive(self, node):
        for z in node.body:
            self.visit(z)
    #@+node:ekr.20160123185312.16: *4* f.Module
    def do_Module(self, node):
        assert 'body' in node._fields
        result = ''.join([self.visit(z) for z in node.body])
        return result # 'module:\n%s' % (result)
    #@+node:ekr.20160123185312.17: *4* f.Lambda
    def do_Lambda(self, node):
        return self.indent('lambda %s: %s' % (
            self.visit(node.args),
            self.visit(node.body)))
    #@+node:ekr.20160123185312.18: *3* f.Expressions
    #@+node:ekr.20160123185312.19: *4* f.Expr
    def do_Expr(self, node):
        '''An outer expression: must be indented.'''
        return self.indent('%s\n' % self.visit(node.value))
    #@+node:ekr.20160123185312.20: *4* f.Expression
    def do_Expression(self, node):
        '''An inner expression: do not indent.'''
        return '%s\n' % self.visit(node.body)
    #@+node:ekr.20160123185312.21: *4* f.GeneratorExp
    def do_GeneratorExp(self, node):
        elt = self.visit(node.elt) or ''
        gens = [self.visit(z) for z in node.generators]
        gens = [z if z else '<**None**>' for z in gens] ### Kludge: probable bug.
        return '<gen %s for %s>' % (elt, ','.join(gens))
    #@+node:ekr.20160123185312.22: *4* f.ctx nodes
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
    #@+node:ekr.20160123185312.23: *3* f.Operands
    #@+node:ekr.20160123185312.24: *4* f.arguments
    # arguments = (expr* args, identifier? vararg, identifier? kwarg, expr* defaults)

    def do_arguments(self, node):
        '''Format the arguments node.'''
        kind = self.kind(node)
        assert kind == 'arguments', kind
        args = [self.visit(z) for z in node.args]
        defaults = [self.visit(z) for z in node.defaults]
        # Assign default values to the last args.
        args2 = []
        n_plain = len(args) - len(defaults)
        for i in range(len(args)):
            if i < n_plain:
                args2.append(args[i])
            else:
                args2.append('%s=%s' % (args[i], defaults[i - n_plain]))
        # Now add the vararg and kwarg args.
        name = getattr(node, 'vararg', None)
        if name: args2.append('*' + name)
        name = getattr(node, 'kwarg', None)
        if name: args2.append('**' + name)
        return ','.join(args2)
    #@+node:ekr.20160123185312.25: *4* f.arg (Python3 only)
    # Python 3:
    # arg = (identifier arg, expr? annotation)

    def do_arg(self, node):
        if node.annotation:
            return self.visit(node.annotation)
        else:
            return ''
    #@+node:ekr.20160123185312.26: *4* f.Attribute
    # Attribute(expr value, identifier attr, expr_context ctx)

    def do_Attribute(self, node):
        return '%s.%s' % (
            self.visit(node.value),
            node.attr) # Don't visit node.attr: it is always a string.
    #@+node:ekr.20160123185312.27: *4* f.Bytes
    def do_Bytes(self, node): # Python 3.x only.
        return str(node.s)
    #@+node:ekr.20160123185312.28: *4* f.Call & f.keyword
    # Call(expr func, expr* args, keyword* keywords, expr? starargs, expr? kwargs)

    def do_Call(self, node):
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
        return '%s(%s)' % (func, ','.join(args))
    #@+node:ekr.20160123185312.29: *5* f.keyword
    # keyword = (identifier arg, expr value)

    def do_keyword(self, node):
        # node.arg is a string.
        value = self.visit(node.value)
        # This is a keyword *arg*, not a Python keyword!
        return '%s=%s' % (node.arg, value)
    #@+node:ekr.20160123185312.30: *4* f.comprehension
    def do_comprehension(self, node):
        result = []
        name = self.visit(node.target) # A name.
        it = self.visit(node.iter) # An attribute.
        result.append('%s in %s' % (name, it))
        ifs = [self.visit(z) for z in node.ifs]
        if ifs:
            result.append(' if %s' % (''.join(ifs)))
        return ''.join(result)
    #@+node:ekr.20160123185312.31: *4* f.Dict
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
    #@+node:ekr.20160123185312.32: *4* f.Ellipsis
    def do_Ellipsis(self, node):
        return '...'
    #@+node:ekr.20160123185312.33: *4* f.ExtSlice
    def do_ExtSlice(self, node):
        return ':'.join([self.visit(z) for z in node.dims])
    #@+node:ekr.20160123185312.34: *4* f.Index
    def do_Index(self, node):
        return self.visit(node.value)
    #@+node:ekr.20160123185312.35: *4* f.List
    def do_List(self, node):
        # Not used: list context.
        # self.visit(node.ctx)
        elts = [self.visit(z) for z in node.elts]
        elst = [z for z in elts if z] # Defensive.
        return '[%s]' % ','.join(elts)
    #@+node:ekr.20160123185312.36: *4* f.ListComp
    def do_ListComp(self, node):
        elt = self.visit(node.elt)
        gens = [self.visit(z) for z in node.generators]
        gens = [z if z else '<**None**>' for z in gens] ### Kludge: probable bug.
        return '%s for %s' % (elt, ''.join(gens))
    #@+node:ekr.20160123185312.37: *4* f.Name
    def do_Name(self, node):
        return node.id
    #@+node:ekr.20160123185312.38: *4* f.Num
    def do_Num(self, node):
        return repr(node.n)
    #@+node:ekr.20160123185312.39: *4* f.Repr
    # Python 2.x only

    def do_Repr(self, node):
        return 'repr(%s)' % self.visit(node.value)
    #@+node:ekr.20160123185312.40: *4* f.Slice
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
    #@+node:ekr.20160123185312.41: *4* f.Str
    def do_Str(self, node):
        '''This represents a string constant.'''
        return repr(node.s)
    #@+node:ekr.20160123185312.42: *4* f.Subscript
    # Subscript(expr value, slice slice, expr_context ctx)

    def do_Subscript(self, node):
        value = self.visit(node.value)
        the_slice = self.visit(node.slice)
        return '%s[%s]' % (value, the_slice)
    #@+node:ekr.20160123185312.43: *4* f.Tuple
    def do_Tuple(self, node):
        elts = [self.visit(z) for z in node.elts]
        return '(%s)' % ','.join(elts)
    #@+node:ekr.20160123185312.44: *3* f.Operators
    #@+node:ekr.20160123185312.45: *4* f.BinOp
    def do_BinOp(self, node):
        return '%s%s%s' % (
            self.visit(node.left),
            self.op_name(node.op),
            self.visit(node.right))
    #@+node:ekr.20160123185312.46: *4* f.BoolOp
    def do_BoolOp(self, node):
        op_name = self.op_name(node.op)
        values = [self.visit(z) for z in node.values]
        return op_name.join(values)
    #@+node:ekr.20160123185312.47: *4* f.Compare
    def do_Compare(self, node):
        result = []
        lt = self.visit(node.left)
        ops = [self.op_name(z) for z in node.ops]
        comps = [self.visit(z) for z in node.comparators]
        result.append(lt)
        if len(ops) == len(comps):
            for i in range(len(ops)):
                result.append('%s%s' % (ops[i], comps[i]))
        else:
            print('can not happen: ops', repr(ops), 'comparators', repr(comps))
        return ''.join(result)
    #@+node:ekr.20160123185312.48: *4* f.UnaryOp
    def do_UnaryOp(self, node):
        return '%s%s' % (
            self.op_name(node.op),
            self.visit(node.operand))
    #@+node:ekr.20160123185312.49: *4* f.ifExp (ternary operator)
    def do_IfExp(self, node):
        return '%s if %s else %s ' % (
            self.visit(node.body),
            self.visit(node.test),
            self.visit(node.orelse))
    #@+node:ekr.20160123185312.50: *3* f.Statements
    #@+node:ekr.20160123185312.51: *4* f.Assert
    def do_Assert(self, node):
        test = self.visit(node.test)
        if getattr(node, 'msg', None):
            message = self.visit(node.msg)
            return self.indent('assert %s, %s' % (test, message))
        else:
            return self.indent('assert %s' % test)
    #@+node:ekr.20160123185312.52: *4* f.Assign
    def do_Assign(self, node):
        return self.indent('%s=%s\n' % (
            '='.join([self.visit(z) for z in node.targets]),
            self.visit(node.value)))
    #@+node:ekr.20160123185312.53: *4* f.AugAssign
    def do_AugAssign(self, node):
        return self.indent('%s%s=%s\n' % (
            self.visit(node.target),
            self.op_name(node.op), # Bug fix: 2013/03/08.
            self.visit(node.value)))
    #@+node:ekr.20160123185312.54: *4* f.Break
    def do_Break(self, node):
        return self.indent('break\n')
    #@+node:ekr.20160123185312.55: *4* f.Continue
    def do_Continue(self, node):
        return self.indent('continue\n')
    #@+node:ekr.20160123185312.56: *4* f.Delete
    def do_Delete(self, node):
        targets = [self.visit(z) for z in node.targets]
        return self.indent('del %s\n' % ','.join(targets))
    #@+node:ekr.20160123185312.57: *4* f.ExceptHandler
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
    #@+node:ekr.20160123185312.58: *4* f.Exec
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
    #@+node:ekr.20160123185312.59: *4* f.For
    def do_For(self, node):
        result = []
        result.append(self.indent('for %s in %s:\n' % (
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
    #@+node:ekr.20160123185312.60: *4* f.Global
    def do_Global(self, node):
        return self.indent('global %s\n' % (
            ','.join(node.names)))
    #@+node:ekr.20160123185312.61: *4* f.If
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
    #@+node:ekr.20160123185312.62: *4* f.Import & helper
    def do_Import(self, node):
        names = []
        for fn, asname in self.get_import_names(node):
            if asname:
                names.append('%s as %s' % (fn, asname))
            else:
                names.append(fn)
        return self.indent('import %s\n' % (
            ','.join(names)))
    #@+node:ekr.20160123185312.63: *5* f.get_import_names
    def get_import_names(self, node):
        '''Return a list of the the full file names in the import statement.'''
        result = []
        for ast2 in node.names:
            if self.kind(ast2) == 'alias':
                data = ast2.name, ast2.asname
                result.append(data)
            else:
                print('unsupported kind in Import.names list', self.kind(ast2))
        return result
    #@+node:ekr.20160123185312.64: *4* f.ImportFrom
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
    #@+node:ekr.20160123185312.65: *4* f.Pass
    def do_Pass(self, node):
        return self.indent('pass\n')
    #@+node:ekr.20160123185312.66: *4* f.Print
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
    #@+node:ekr.20160123185312.67: *4* f.Raise
    def do_Raise(self, node):
        args = []
        for attr in ('type', 'inst', 'tback'):
            if getattr(node, attr, None) is not None:
                args.append(self.visit(getattr(node, attr)))
        if args:
            return self.indent('raise %s\n' % (
                ','.join(args)))
        else:
            return self.indent('raise\n')
    #@+node:ekr.20160123185312.68: *4* f.Return
    def do_Return(self, node):
        if node.value:
            return self.indent('return %s\n' % (
                self.visit(node.value)))
        else:
            return self.indent('return\n')
    #@+node:ekr.20160123185312.69: *4* f.Suite
    # def do_Suite(self,node):
        # for z in node.body:
            # s = self.visit(z)
    #@+node:ekr.20160123185312.70: *4* f.TryExcept
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
    #@+node:ekr.20160123185312.71: *4* f.TryFinally
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
    #@+node:ekr.20160123185312.72: *4* f.While
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
    #@+node:ekr.20160123185312.73: *4* f.With
    def do_With(self, node):
        result = []
        result.append(self.indent('with '))
        if hasattr(node, 'context_expression'):
            result.append(self.visit(node.context_expresssion))
        vars_list = []
        if hasattr(node, 'optional_vars'):
            try:
                for z in node.optional_vars:
                    vars_list.append(self.visit(z))
            except TypeError: # Not iterable.
                vars_list.append(self.visit(node.optional_vars))
        result.append(','.join(vars_list))
        result.append(':\n')
        for z in node.body:
            self.level += 1
            result.append(self.visit(z))
            self.level -= 1
        result.append('\n')
        return ''.join(result)
    #@+node:ekr.20160123185312.74: *4* f.Yield
    def do_Yield(self, node):
        if getattr(node, 'value', None):
            return self.indent('yield %s\n' % (
                self.visit(node.value)))
        else:
            return self.indent('yield\n')
    #@+node:ekr.20160123185312.75: *3* f.Utils
    #@+node:ekr.20160123185312.76: *4* f.kind
    def kind(self, node):
        '''Return the name of node's class.'''
        return node.__class__.__name__
    #@+node:ekr.20160123185312.77: *4* f.indent
    def indent(self, s):
        return '%s%s' % (' ' * 4 * self.level, s)
    #@+node:ekr.20160123185312.78: *4* f.op_name
    #@@nobeautify

    def op_name (self,node,strict=True):
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
        name = d.get(self.kind(node),'<%s>' % node.__class__.__name__)
        if strict: assert name,self.kind(node)
        return name
    #@-others
#@+node:ekr.20160123185312.2: ** class StandAloneMakeStubFile
class StandAloneMakeStubFile:
    '''
    A class to make Python stub (.pyi) files in the ~/stubs directory for
    every file mentioned in the [Source Files] section of
    ~/stubs/make_stub_files.cfg.
    '''

    #@+others
    #@+node:ekr.20160123193846.1: *3* msf.ctor
    def __init__ (self):
        '''Ctor for StandAloneMakeStubFile class.'''
        self.d = {}
        self.files = []
        self.options = {}
        self.prefix_lines = []
    #@+node:ekr.20160123185312.6: *3* msf.make_stub_file
    def make_stub_file(self, fn):
        '''
        Make a stub file in ~/stubs for all source files mentioned in the
        [Source Files] section of ~/stubs/make_stub_files.cfg
        '''
        if not fn.endswith('.py'):
            print('not a python file', fn)
            return
        if not os.path.exists(fn):
            print('not found', fn)
            return
        stubs = os.path.expanduser('~/stubs')
        if os.path.exists(stubs):
            base_fn = os.path.basename(fn)
            out_fn = os.path.join(stubs,base_fn)
        else:
            print('not found', stubs)
            return
        out_fn = out_fn[:-3] + '.pyi'
        s = open(fn).read()
        node = ast.parse(s,filename=fn,mode='exec')
        StubTraverser(self.d, self.prefix_lines, out_fn).run(node)
    #@+node:ekr.20160123185312.7: *3* msf.run
    def run(self):
        '''Make stub files for all files.'''
        for fn in self.files:
            self.make_stub_file(fn)
    #@+node:ekr.20160123185719.1: *3* msf.scan_options
    def scan_options(self):
        '''Set all configuration-related ivars.'''
        # import leo.core.leoGlobals as g ; g.pdb()
        parser = configparser.ConfigParser()
        fn = '~/stubs/make_stub_files.cfg'
        fn = os.path.expanduser('~/stubs/make_stub_files.cfg')
        if os.path.exists(fn):
            parser.read(os.path.expanduser('~/stubs/make_stub_files.cfg'))
            files = parser.get('Global', 'files')
            files = [z.strip() for z in files.split('\n') if z.strip()]
            files2 = []
            for z in files:
                files2.extend(glob.glob(z))
            self.files = [z for z in files2 if os.path.exists(z)]
            print('Files...\n%s' % '\n'.join(self.files))
            print('Types...')
            for key in sorted(parser.options('Types')):
                value = parser.get('Types', key)
                self.d [key] = value
                print('%s: %s' % (key, value))
            prefix = parser.get('Global','prefix')
            self.prefix_lines = [z.strip() for z in prefix.split('\n') if z.strip()]
            print('Prefix...\n%s' % self.prefix_lines)
    #@-others
#@+node:ekr.20160123185312.79: ** class StubFormatter (AstFormatter)
class StubFormatter (AstFormatter):
    #@+others
    #@+node:ekr.20160123185312.80: *3* sf.Constants & Name
    # Return generic markers allow better pattern matches.

    def do_BoolOp(self, node): # Python 2.x only.
        return 'bool'

    def do_Bytes(self, node): # Python 3.x only.
        return 'bytes' # return str(node.s)

    def do_Name(self, node):
        return 'bool' if node.id in ('True', 'False') else node.id

    def do_Num(self, node):
        return 'number' # return repr(node.n)

    def do_Str(self, node):
        '''This represents a string constant.'''
        return 'str' # return repr(node.s)
    #@-others
#@+node:ekr.20160123185312.81: ** class StubTraverser (ast.NodeVisitor)
class StubTraverser (ast.NodeVisitor):
    
    #@+others
    #@+node:ekr.20160123193632.1: *3* st.ctor
    def __init__(self, d, prefix_lines, output_fn):
        '''Ctor for StubTraverser class.'''
        self.d = d
        self.format = StubFormatter().format
        self.in_function = False
        self.level = 0
        self.output_file = None
        self.output_fn = output_fn
        self.prefix_lines = prefix_lines
        self.returns = set()
    #@+node:ekr.20160123185312.82: *3* st.indent & out
    def indent(self, s):
        '''Return s, properly indented.'''
        return '%s%s' % (' ' * 4 * self.level, s)

    def out(self, s):
        '''Output the string to the console or the file.'''
        if self.output_file:
            self.output_file.write(self.indent(s)+'\n')
        else:
            print(self.indent(s))
    #@+node:ekr.20160123185312.83: *3* st.run
    def run(self, node):
        '''StubTraverser.run: write the stubs in node's tree to self.output_fn.'''
        dir_ = os.path.dirname(self.output_fn)
        if os.path.exists(dir_):
            self.output_file = open(self.output_fn, 'w')
            for z in self.prefix_lines or []:
                self.out(z.strip())
            self.visit(node)
            self.output_file.close()
            self.output_file = None
            print('wrote', self.output_fn)
        else:
            print('not found:', dir_)

    #@+node:ekr.20160123185312.85: *3* st.Visitors
    #@+node:ekr.20160123185312.86: *4* st.ClassDef
    # ClassDef(identifier name, expr* bases, stmt* body, expr* decorator_list)

    def visit_ClassDef(self, node):

        # Format...
        if not node.name.startswith('_'):
            if node.bases:
                s = '(%s)' % ','.join([self.format(z) for z in node.bases])
            else:
                s = ''
            self.out('class %s%s:' % (node.name, s))
        # Visit...
        self.level += 1
        old_in_function = self.in_function
        self.in_function = False
        for z in node.body:
            self.visit(z)
        self.level -= 1
        self.in_function = old_in_function
    #@+node:ekr.20160123185312.87: *4* st.FunctionDef & helpers
    # FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list)

    def visit_FunctionDef(self, node):
        
        # Do nothing if we are already in a function.
        # We do not generate stubs for inner defs.
        if self.in_function or node.name.startswith('_'):
            return
        # First, visit the function body.
        self.returns = set()
        self.in_function = True
        self.level += 1
        for z in node.body:
            self.visit(z)
        self.level -= 1
        self.in_function = False
        # Format *after* traversing
        self.out('def %s(%s) -> %s: ...' % (
            node.name,
            self.format_arguments(node.args),
            self.format_returns(node)))
    #@+node:ekr.20160123185312.88: *5* format_arguments & helper
    # arguments = (expr* args, identifier? vararg, identifier? kwarg, expr* defaults)

    def format_arguments(self, node):
        '''
        Format the arguments node.
        Similar to AstFormat.do_arguments, but it is not a visitor!
        '''
        assert isinstance(node,ast.arguments), node
        args = [self.format(z) for z in node.args]
        defaults = [self.format(z) for z in node.defaults]
        # Assign default values to the last args.
        result = []
        n_plain = len(args) - len(defaults)
        # pylint: disable=consider-using-enumerate
        for i in range(len(args)):
            s = self.munge_arg(args[i])
            if i < n_plain:
                result.append(s)
            else:
                result.append('%s=%s' % (s, defaults[i - n_plain]))
        # Now add the vararg and kwarg args.
        name = getattr(node, 'vararg', None)
        if name: result.append('*' + name)
        name = getattr(node, 'kwarg', None)
        if name: result.append('**' + name)
        return ', '.join(result)
    #@+node:ekr.20160123185312.89: *6* munge_arg
    def munge_arg(self, s):
        '''Add an annotation for s if possible.'''
        a = self.d.get(s)
        return '%s: %s' % (s, a) if a else s
    #@+node:ekr.20160123185312.90: *5* format_returns
    def format_returns(self, node):
        '''Calculate the return type.'''
        def split(s):
            return '\n     ' + self.indent(s) if len(s) > 30 else s
            
        r = list(self.returns)
        r = [self.format(z) for z in r]
        if len(r) == 0:
            return 'None'
        if len(r) == 1:
            return split(r[0])
        elif 'None' in r:
            r.remove('None')
            return split('Optional[%s]' % ', '.join(r))
        else:
            # return 'Any'
            s = ', '.join(r)
            if len(s) > 30:
                return ', '.join(['\n    ' + self.indent(z) for z in r])
            else:
                return split(', '.join(r))
    #@+node:ekr.20160123185312.91: *4* st.Return
    def visit_Return(self, node):

        self.returns.add(node.value)
    #@-others
#@+node:ekr.20160123185348.1: ** main
def main():
    '''
    The driver for the stand-alone version of make-stub-files.
    All options come from ~/stubs/make_stub_files.cfg.
    '''
    if sys.platform.lower().startswith('win'):
        os.system('cls')
    controller = StandAloneMakeStubFile()
    controller.scan_options()
    controller.run()
    print('done')
#@-others
if __name__ == "__main__":
    main()
#@-leo

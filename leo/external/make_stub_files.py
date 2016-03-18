#!/usr/bin/env python
'''
This script makes a stub (.pyi) file in the output directory for each
source file listed on the command line (wildcard file names are supported).

For full details, see README.md.

This file is in the public domain.

Written by Edward K. Ream.
'''
import ast
from collections import OrderedDict
    # Requires Python 2.7 or above. Without OrderedDict
    # the configparser will give random order for patterns.
try:
    import ConfigParser as configparser # Python 2
except ImportError:
    import configparser # Python 3
import glob
import optparse
import os
import re
import sys
import time
try:
    import StringIO as io # Python 2
except ImportError:
    import io # Python 3

isPython3 = sys.version_info >= (3, 0, 0)

def is_known_type(s):
    '''
    Return True if s is nothing but a single known type.
    Recursively test inner types in square brackets.
    '''
    return ReduceTypes().is_known_type(s)

def merge_types(a1, a2):
    '''
    a1 and a2 may be strings or lists.
    return a list containing both of them, flattened, without duplicates.
    '''
    # Only useful if visitors could return either lists or strings.
    assert a1 is not None
    assert a2 is not None
    r1 = a1 if isinstance(a1, (list, tuple)) else [a1]
    r2 = a2 if isinstance(a2, (list, tuple)) else [a2]
    return sorted(set(r1 + r2))

def reduce_types(aList, name=None, trace=False):
    '''
    Return a string containing the reduction of all types in aList.
    The --trace-reduce command-line option sets trace=True.
    If present, name is the function name or class_name.method_name.
    '''
    return ReduceTypes(aList, name, trace).reduce_types()

# Top-level functions

def dump(title, s=None):
    if s:
        print('===== %s...\n%s\n' % (title, s.rstrip()))
    else:
        print('===== %s...\n' % title)

def dump_dict(title, d):
    '''Dump a dictionary with a header.'''
    dump(title)
    for z in sorted(d):
        print('%30s %s' % (z, d.get(z)))
    print('')

def dump_list(title, aList):
    '''Dump a list with a header.'''
    dump(title)
    for z in aList:
        print(z)
    print('')

def main():
    '''
    The driver for the stand-alone version of make-stub-files.
    All options come from ~/stubs/make_stub_files.cfg.
    '''
    # g.cls()
    controller = StandAloneMakeStubFile()
    controller.scan_command_line()
    controller.scan_options()
    controller.run()
    print('done')

def pdb(self):
    '''Invoke a debugger during unit testing.'''
    try:
        import leo.core.leoGlobals as leo_g
        leo_g.pdb()
    except ImportError:
        import pdb
        pdb.set_trace()

def truncate(s, n):
    '''Return s truncated to n characters.'''
    return s if len(s) <= n else s[:n-3] + '...'


class AstFormatter:
    '''
    A class to recreate source code from an AST.
    
    This does not have to be perfect, but it should be close.
    '''
    # pylint: disable=consider-using-enumerate

    # Entries...

    def format(self, node):
        '''Format the node (or list of nodes) and its descendants.'''
        self.level = 0
        val = self.visit(node)
        return val and val.strip() or ''

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
            assert type(s) == type('abc'), (node, type(s))
            return s

    # Contexts...

    # 2: ClassDef(identifier name, expr* bases,
    #             stmt* body, expr* decorator_list)
    # 3: ClassDef(identifier name, expr* bases,
    #             keyword* keywords, expr? starargs, expr? kwargs
    #             stmt* body, expr* decorator_list)

    def do_ClassDef(self, node):
        result = []
        name = node.name # Only a plain string is valid.
        bases = [self.visit(z) for z in node.bases] if node.bases else []
        if hasattr(node, 'keywords'): # Python 3
            for z in node.keywords:
                arg, value = z
                bases.append('%s=%s' % (self.visit(arg), self.visit(value)))
        if hasattr(node, 'starargs'): # Python 3
            junk, value = node.starargs
            bases.append('*%s', self.visit(value))
        if hasattr(node, 'kwargs'): # Python 3
            junk, value = node.kwargs
            bases.append('*%s', self.visit(value))
        if bases:
            result.append(self.indent('class %s(%s):\n' % (name, ','.join(bases))))
        else:
            result.append(self.indent('class %s:\n' % name))
        for z in node.body:
            self.level += 1
            result.append(self.visit(z))
            self.level -= 1
        return ''.join(result)

    # 2: FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list)
    # 3: FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list,
    #                expr? returns)

    def do_FunctionDef(self, node):
        '''Format a FunctionDef node.'''
        result = []
        if node.decorator_list:
            for z in node.decorator_list:
                result.append('@%s\n' % self.visit(z))
        name = node.name # Only a plain string is valid.
        args = self.visit(node.args) if node.args else ''
        if hasattr(node, 'returns'): # Python 3.
            returns = self.visit(node.returns)
            result.append(self.indent('def %s(%s): -> %s\n' % (name, args, returns)))
        else:
            result.append(self.indent('def %s(%s):\n' % (name, args)))
        for z in node.body:
            self.level += 1
            result.append(self.visit(z))
            self.level -= 1
        return ''.join(result)

    def do_Interactive(self, node):
        for z in node.body:
            self.visit(z)

    def do_Module(self, node):
        assert 'body' in node._fields
        result = ''.join([self.visit(z) for z in node.body])
        return result # 'module:\n%s' % (result)

    def do_Lambda(self, node):
        return self.indent('lambda %s: %s' % (
            self.visit(node.args),
            self.visit(node.body)))

    # Expressions...

    def do_Expr(self, node):
        '''An outer expression: must be indented.'''
        return self.indent('%s\n' % self.visit(node.value))

    def do_Expression(self, node):
        '''An inner expression: do not indent.'''
        return '%s\n' % self.visit(node.body)

    def do_GeneratorExp(self, node):
        elt = self.visit(node.elt) or ''
        gens = [self.visit(z) for z in node.generators]
        gens = [z if z else '<**None**>' for z in gens] # Kludge: probable bug.
        return '<gen %s for %s>' % (elt, ','.join(gens))

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

    # Operands...

    # 2: arguments = (expr* args, identifier? vararg, identifier? kwarg, expr* defaults)
    # 3: arguments = (arg*  args, arg? vararg,
    #                arg* kwonlyargs, expr* kw_defaults,
    #                arg? kwarg, expr* defaults)

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
        if isPython3:
            args  = [self.visit(z) for z in node.kwonlyargs]
            defaults = [self.visit(z) for z in node.kw_defaults]
            n_plain = len(args) - len(defaults)
            for i in range(len(args)):
                if i < n_plain:
                    args2.append(args[i])
                else:
                    args2.append('%s=%s' % (args[i], defaults[i - n_plain]))
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

    # 3: arg = (identifier arg, expr? annotation)

    def do_arg(self, node):
        if getattr(node, 'annotation', None):
            return '%s: %s' % (node.arg, self.visit(node.annotation))
        else:
            return node.arg
    # Attribute(expr value, identifier attr, expr_context ctx)

    def do_Attribute(self, node):
        return '%s.%s' % (
            self.visit(node.value),
            node.attr) # Don't visit node.attr: it is always a string.

    def do_Bytes(self, node): # Python 3.x only.
        return str(node.s)

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

    # keyword = (identifier arg, expr value)

    def do_keyword(self, node):
        # node.arg is a string.
        value = self.visit(node.value)
        # This is a keyword *arg*, not a Python keyword!
        return '%s=%s' % (node.arg, value)

    def do_comprehension(self, node):
        result = []
        name = self.visit(node.target) # A name.
        it = self.visit(node.iter) # An attribute.
        result.append('%s in %s' % (name, it))
        ifs = [self.visit(z) for z in node.ifs]
        if ifs:
            result.append(' if %s' % (''.join(ifs)))
        return ''.join(result)

    def do_Dict(self, node):
        result = []
        keys = [self.visit(z) for z in node.keys]
        values = [self.visit(z) for z in node.values]
        if len(keys) == len(values):
            # result.append('{\n' if keys else '{')
            result.append('{')
            items = []
            for i in range(len(keys)):
                items.append('%s:%s' % (keys[i], values[i]))
            result.append(', '.join(items))
            result.append('}')
            # result.append(',\n'.join(items))
            # result.append('\n}' if keys else '}')
        else:
            print('Error: f.Dict: len(keys) != len(values)\nkeys: %s\nvals: %s' % (
                repr(keys), repr(values)))
        return ''.join(result)

    def do_Ellipsis(self, node):
        return '...'

    def do_ExtSlice(self, node):
        return ':'.join([self.visit(z) for z in node.dims])

    def do_Index(self, node):
        return self.visit(node.value)

    def do_List(self, node):
        # Not used: list context.
        # self.visit(node.ctx)
        elts = [self.visit(z) for z in node.elts]
        elst = [z for z in elts if z] # Defensive.
        return '[%s]' % ','.join(elts)

    def do_ListComp(self, node):
        elt = self.visit(node.elt)
        gens = [self.visit(z) for z in node.generators]
        gens = [z if z else '<**None**>' for z in gens] # Kludge: probable bug.
        return '%s for %s' % (elt, ''.join(gens))

    def do_Name(self, node):
        return node.id

    def do_NameConstant(self, node): # Python 3 only.
        s = repr(node.value)
        return 'bool' if s in ('True', 'False') else s

    def do_Num(self, node):
        return repr(node.n)

    # Python 2.x only

    def do_Repr(self, node):
        return 'repr(%s)' % self.visit(node.value)

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

    def do_Str(self, node):
        '''This represents a string constant.'''
        return repr(node.s)

    # Subscript(expr value, slice slice, expr_context ctx)

    def do_Subscript(self, node):
        value = self.visit(node.value)
        the_slice = self.visit(node.slice)
        return '%s[%s]' % (value, the_slice)

    def do_Tuple(self, node):
        elts = [self.visit(z) for z in node.elts]
        return '(%s)' % ', '.join(elts)

    # Operators...

    def do_BinOp(self, node):
        return '%s%s%s' % (
            self.visit(node.left),
            self.op_name(node.op),
            self.visit(node.right))

    def do_BoolOp(self, node):
        op_name = self.op_name(node.op)
        values = [self.visit(z) for z in node.values]
        return op_name.join(values)

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

    def do_UnaryOp(self, node):
        return '%s%s' % (
            self.op_name(node.op),
            self.visit(node.operand))

    def do_IfExp(self, node):
        return '%s if %s else %s ' % (
            self.visit(node.body),
            self.visit(node.test),
            self.visit(node.orelse))

    # Statements...

    def do_Assert(self, node):
        test = self.visit(node.test)
        if getattr(node, 'msg', None):
            message = self.visit(node.msg)
            return self.indent('assert %s, %s' % (test, message))
        else:
            return self.indent('assert %s' % test)

    def do_Assign(self, node):
        return self.indent('%s=%s\n' % (
            '='.join([self.visit(z) for z in node.targets]),
            self.visit(node.value)))

    def do_AugAssign(self, node):
        return self.indent('%s%s=%s\n' % (
            self.visit(node.target),
            self.op_name(node.op), # Bug fix: 2013/03/08.
            self.visit(node.value)))

    def do_Break(self, node):
        return self.indent('break\n')

    def do_Continue(self, node):
        return self.indent('continue\n')

    def do_Delete(self, node):
        targets = [self.visit(z) for z in node.targets]
        return self.indent('del %s\n' % ','.join(targets))

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

    def do_Global(self, node):
        return self.indent('global %s\n' % (
            ','.join(node.names)))

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

    def do_Import(self, node):
        names = []
        for fn, asname in self.get_import_names(node):
            if asname:
                names.append('%s as %s' % (fn, asname))
            else:
                names.append(fn)
        return self.indent('import %s\n' % (
            ','.join(names)))

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

    # Nonlocal(identifier* names)

    def do_Nonlocal(self, node):
        
        return self.indent('nonlocal %s\n' % ', '.join(node.names))

    def do_Pass(self, node):
        return self.indent('pass\n')

    # Python 2.x only

    def do_Print(self, node):
        vals = []
        for z in node.values:
            vals.append(self.visit(z))
        if getattr(node, 'dest', None):
            vals.append('dest=%s' % self.visit(node.dest))
        if getattr(node, 'nl', None):
            vals.append('nl=%s' % node.nl)
        return self.indent('print(%s)\n' % (
            ','.join(vals)))

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

    def do_Return(self, node):
        if node.value:
            return self.indent('return %s\n' % (
                self.visit(node.value).strip()))
        else:
            return self.indent('return\n')

    # Starred(expr value, expr_context ctx)

    def do_Starred(self, node):

        return '*' + self.visit(node.value)

    # Try(stmt* body, excepthandler* handlers, stmt* orelse, stmt* finalbody)

    def do_Try(self, node): # Python 3

        result = []
        self.append(self.indent('try:\n'))
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

    def do_Yield(self, node):
        if getattr(node, 'value', None):
            return self.indent('yield %s\n' % (
                self.visit(node.value)))
        else:
            return self.indent('yield\n')

    # YieldFrom(expr value)

    def do_YieldFrom(self, node):
        
        return self.indent('yield from %s\n' % (
            self.visit(node.value)))

    # Utils...

    def kind(self, node):
        '''Return the name of node's class.'''
        return node.__class__.__name__

    def indent(self, s):
        return '%s%s' % (' ' * 4 * self.level, s)

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


class AstArgFormatter (AstFormatter):
    '''
    Just like the AstFormatter class, except it prints the class
    names of constants instead of actual values.
    '''

    # Return generic markers to allow better pattern matches.

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


class LeoGlobals:
    '''A class supporting g.pdb and g.trace for compatibility with Leo.'''

    class NullObject:
        """
        An object that does nothing, and does it very well.
        From the Python cookbook, recipe 5.23
        """
        def __init__(self, *args, **keys): pass
        def __call__(self, *args, **keys): return self
        def __repr__(self): return "NullObject"
        def __str__(self): return "NullObject"
        def __bool__(self): return False
        def __nonzero__(self): return 0
        def __delattr__(self, attr): return self
        def __getattr__(self, attr): return self
        def __setattr__(self, attr, val): return self

    def _callerName(self, n=1, files=False):
        # print('_callerName: %s %s' % (n,files))
        try: # get the function name from the call stack.
            f1 = sys._getframe(n) # The stack frame, n levels up.
            code1 = f1.f_code # The code object
            name = code1.co_name
            if name == '__init__':
                name = '__init__(%s,line %s)' % (
                    self.shortFileName(code1.co_filename), code1.co_firstlineno)
            if files:
                return '%s:%s' % (self.shortFileName(code1.co_filename), name)
            else:
                return name # The code name
        except ValueError:
            # print('g._callerName: ValueError',n)
            return '' # The stack is not deep enough.
        except Exception:
            # es_exception()
            return '' # "<no caller name>"

    def callers(self, n=4, count=0, excludeCaller=True, files=False):
        '''Return a list containing the callers of the function that called g.callerList.

        If the excludeCaller keyword is True (the default), g.callers is not on the list.

        If the files keyword argument is True, filenames are included in the list.
        '''
        # sys._getframe throws ValueError in both cpython and jython if there are less than i entries.
        # The jython stack often has less than 8 entries,
        # so we must be careful to call g._callerName with smaller values of i first.
        result = []
        i = 3 if excludeCaller else 2
        while 1:
            s = self._callerName(i, files=files)
            # print(i,s)
            if s:
                result.append(s)
            if not s or len(result) >= n: break
            i += 1
        result.reverse()
        if count > 0: result = result[: count]
        sep = '\n' if files else ','
        return sep.join(result)

    def cls(self):
        '''Clear the screen.'''
        if sys.platform.lower().startswith('win'):
            os.system('cls')

    def pdb(self):
        try:
            import leo.core.leoGlobals as leo_g
            leo_g.pdb()
        except ImportError:
            import pdb
            pdb.set_trace()

    def shortFileName(self,fileName, n=None):
        if n is None or n < 1:
            return os.path.basename(fileName)
        else:
            return '/'.join(fileName.replace('\\', '/').split('/')[-n:])

    def splitLines(self, s):
        '''Split s into lines, preserving trailing newlines.'''
        return s.splitlines(True) if s else []

    def trace(self, *args, **keys):
        try:
            import leo.core.leoGlobals as leo_g
            leo_g.trace(caller_level=2, *args, **keys)
        except ImportError:
            print(args, keys)


class Pattern(object):
    '''
    A class representing regex or balanced patterns.
    
    Sample matching code, for either kind of pattern:
        
        for m in reversed(pattern.all_matches(s)):
            s = pattern.replace(m, s)
    '''

    def __init__ (self, find_s, repl_s=''):
        '''Ctor for the Pattern class.'''
        self.find_s = find_s
        self.repl_s = repl_s
        if self.is_regex():
            self.regex = re.compile(find_s)
        elif self.is_balanced():
            self.regex = None
        else:
            # Escape all dangerous characters.
            result = []
            for ch in find_s:
                if ch == '_' or ch.isalnum():
                    result.append(ch)
                else:
                    result.append('\\'+ch)
            self.regex = re.compile(''.join(result))

    def __eq__(self, obj):
        """Return True if two Patterns are equivalent."""
        if isinstance(obj, Pattern):
            return self.find_s == obj.find_s and self.repl_s == obj.repl_s
        else:
            return NotImplemented

    def __ne__(self, obj):
        """Return True if two Patterns are not equivalent."""
        return not self.__eq__(obj)

    def __hash__(self):
        '''Pattern.__hash__'''
        return len(self.find_s) + len(self.repl_s)

    def __repr__(self):
        '''Pattern.__repr__'''
        return '%s: %s' % (self.find_s, self.repl_s)
        
    __str__ = __repr__

    def is_balanced(self):
        '''Return True if self.find_s is a balanced pattern.'''
        s = self.find_s
        if s.endswith('*'):
            return True
        for pattern in ('(*)', '[*]', '{*}'):
            if s.find(pattern) > -1:
                return True
        return False

    def is_regex(self):
        '''
        Return True if self.find_s is a regular pattern.
        For now a kludgy convention suffices.
        '''
        return self.find_s.endswith('$')
            # A dollar sign is not valid in any Python expression.

    def all_matches(self, s):
        '''
        Return a list of match objects for all matches in s.
        These are regex match objects or (start, end) for balanced searches.
        '''
        trace = False
        if self.is_balanced():
            aList, i = [], 0
            while i < len(s):
                progress = i
                j = self.full_balanced_match(s, i)
                if j is None:
                    i += 1
                else:
                    aList.append((i,j),)
                    i = j
                assert progress < i
            return aList
        else:
            return list(self.regex.finditer(s))

    def full_balanced_match(self, s, i):
        '''Return the index of the end of the match found at s[i:] or None.'''
        i1 = i
        trace = False
        if trace: g.trace(self.find_s, s[i:].rstrip())
        pattern = self.find_s
        j = 0 # index into pattern
        while i < len(s) and j < len(pattern) and pattern[j] in ('*', s[i]):
            progress = i
            if pattern[j:j+3] in ('(*)', '[*]', '{*}'):
                delim = pattern[j]
                i = self.match_balanced(delim, s, i)
                j += 3
            elif j == len(pattern)-1 and pattern[j] == '*':
                # A trailing * matches the rest of the string.
                j += 1
                i = len(s)
                break
            else:
                i += 1
                j += 1
            assert progress < i
        found = i <= len(s) and j == len(pattern)
        if trace and found:
            g.trace('%s -> %s' % (pattern, s[i1:i]))
        return i if found else None

    def match_balanced(self, delim, s, i):
        '''
        delim == s[i] and delim is in '([{'
        Return the index of the end of the balanced parenthesized string, or len(s)+1.
        '''
        trace = False
        assert s[i] == delim, s[i]
        assert delim in '([{'
        delim2 = ')]}'['([{'.index(delim)]
        assert delim2 in ')]}'
        i1, level = i, 0
        while i < len(s):
            progress = i
            ch = s[i]
            i += 1
            if ch == delim:
                level += 1
            elif ch == delim2:
                level -= 1
                if level == 0:
                    if trace: g.trace('found: %s' % s[i1:i])
                    return i
            assert progress < i
        # Unmatched: a syntax error.
        g.trace('unmatched %s in %s' % (delim, s), g.callers(4))
        return len(s) + 1

    def match(self, s, trace=False):
        '''
        Perform the match on the entire string if possible.
        Return (found, new s)
        '''
        trace = False or trace
        caller = g.callers(2).split(',')[0].strip()
            # The caller of match_all.
        s1 = truncate(s,40)
        if self.is_balanced():
            j = self.full_balanced_match(s, 0)
            if j is None:
                return False, s
            else:
                start, end = 0, len(s)
                s = self.replace_balanced(s, start, end)
                if trace:
                    g.trace('%-16s %30s %40s ==> %s' % (caller, self, s1, s))
                return True, s
        else:
            m = self.regex.match(s)
            if m and m.group(0) == s:
                s = self.replace_regex(m, s)
                if trace:
                    g.trace('%-16s %30s %30s ==> %s' % (caller, self, s1, s))
                return True, s
            else:
                return False, s

    def match_entire_string(self, s):
        '''Return True if s matches self.find_s'''
        if self.is_balanced():
            j = self.full_balanced_match(s, 0)
            return j == len(s)
        else:
            m = self.regex.match(s)
            return m and m.group(0) == s

    def replace(self, m, s):
        '''Perform any kind of replacement.'''
        if self.is_balanced():
            start, end = m
            return self.replace_balanced(s, start, end)
        else:
            return self.replace_regex(m, s)

    def replace_balanced(self, s1, start, end):
        '''
        Use m (returned by all_matches) to replace s by the string implied by repr_s.
        Within repr_s, * star matches corresponding * in find_s
        '''
        trace = False
        s = s1[start:end]
        f, r = self.find_s, self.repl_s
        i1 = f.find('(*)')
        i2 = f.find('[*]')
        i3 = f.find('{*}')
        if -1 == i1 == i2 == i3:
            return s1[:start] + r + s1[end:]
        j = r.find('*')
        if j == -1:
            return s1[:start] + r + s1[end:]
        i = min([z for z in [i1, i2, i3] if z > -1])
        assert i > -1 # i is an index into f AND s
        delim = f[i]
        if trace: g.trace('head', s[:i], f[:i])
        assert s[:i] == f[:i], (s[:i], f[:i])
        if trace: g.trace('delim',delim)
        k = self.match_balanced(delim, s, i)
        s_star = s[i+1:k-1]
        if trace: g.trace('s_star',s_star)
        repl = r[:j] + s_star + r[j+1:]
        if trace: g.trace('repl',self.repl_s,'==>',repl)
        return s1[:start] + repl + s1[end:]

    def replace_regex(self, m, s):
        '''Do the replacement in s specified by m.'''
        s = self.repl_s
        for i in range(9):
            group = '\\%s' % i
            if s.find(group) > -1:
                # g.trace(i, m.group(i))
                s = s.replace(group, m.group(i))
        return s


class ReduceTypes:
    '''
    A helper class for the top-level reduce_types function.

    This class reduces a list of type hints to a string containing the
    reduction of all types in the list.
    '''

    def __init__(self, aList=None, name=None, trace=False):
        '''Ctor for ReduceTypes class.'''
        self.aList = aList
        self.name = name
        self.optional = False
        self.trace = trace

    def is_known_type(self, s):
        '''
        Return True if s is nothing but a single known type.

        It suits the other methods of this class *not* to test inside inner
        brackets. This prevents unwanted Any types.
        '''
        trace = False
        s1 = s
        s = s.strip()
        table = (
            '', 'None', # Tricky.
            'complex', 'float', 'int', 'long', 'number',
            'dict', 'list', 'tuple',
            'bool', 'bytes', 'str', 'unicode',
        )
        for s2 in table:
            if s2 == s:
                return True
            elif Pattern(s2+'(*)', s).match_entire_string(s):
                return True
        if s.startswith('[') and s.endswith(']'):
            inner = s[1:-1]
            return self.is_known_type(inner) if inner else True
        elif s.startswith('(') and s.endswith(')'):
            inner = s[1:-1]
            return self.is_known_type(inner) if inner else True
        elif s.startswith('{') and s.endswith('}'):
            return True
            # inner = s[1:-1]
            # return self.is_known_type(inner) if inner else True
        table = (
            # Pep 484: https://www.python.org/dev/peps/pep-0484/
            # typing module: https://docs.python.org/3/library/typing.html
            # Test the most common types first.
            'Any', 'Dict', 'List', 'Optional', 'Tuple', 'Union', 
            # Not generated by this program, but could arise from patterns.
            'AbstractSet', 'AnyMeta', 'AnyStr',
            'BinaryIO', 'ByteString',
            'Callable', 'CallableMeta', 'Container',
            'Final', 'Generic', 'GenericMeta', 'Hashable',
            'IO', 'ItemsView', 'Iterable', 'Iterator',
            'KT', 'KeysView',
            'Mapping', 'MappingView', 'Match',
            'MutableMapping', 'MutableSequence', 'MutableSet',
            'NamedTuple', 'OptionalMeta',
            # 'POSIX', 'PY2', 'PY3',
            'Pattern', 'Reversible',
            'Sequence', 'Set', 'Sized',
            'SupportsAbs', 'SupportsFloat', 'SupportsInt', 'SupportsRound',
            'T', 'TextIO', 'TupleMeta', 'TypeVar', 'TypingMeta',
            'Undefined', 'UnionMeta',
            'VT', 'ValuesView', 'VarBinding',
        )
        for s2 in table:
            if s2 == s:
                return True
            else:
                # Don't look inside bracketss.
                pattern = Pattern(s2+'[*]', s)
                if pattern.match_entire_string(s):
                    return True
        if trace: g.trace('Fail:', s1)
        return False

    def reduce_collection(self, aList, kind):
        '''
        Reduce the inner parts of a collection for the given kind.
        Return a list with only collections of the given kind reduced.
        '''
        trace = False
        if trace: g.trace(kind, aList)
        assert isinstance(aList, list)
        assert None not in aList, aList
        pattern = Pattern('%s[*]' % kind)
        others, r1, r2 = [], [], []
        for s in sorted(set(aList)):
            if pattern.match_entire_string(s):
                r1.append(s)
            else:
                others.append(s)
        if trace: g.trace('1', others, r1)
        for s in sorted(set(r1)):
            parts = []
            s2 = s[len(kind)+1:-1]
            for s3 in s2.split(','):
                s3 = s3.strip()
                if trace: g.trace('*', self.is_known_type(s3), s3)
                parts.append(s3 if self.is_known_type(s3) else 'Any')
            r2.append('%s[%s]' % (kind, ', '.join(parts)))
        if trace: g.trace('2', r2)
        result = others
        result.extend(r2)
        result = sorted(set(result))
        if trace: g.trace('3', result)
        return result

    def reduce_numbers(self, aList):
        '''
        Return aList with all number types in aList replaced by the most
        general numeric type in aList.
        '''
        trace = False
        found = None
        numbers = ('number', 'complex', 'float', 'long', 'int')
        for kind in numbers:
            for z in aList:
                if z == kind:
                    found = kind
                    break
            if found:
                break
        if found:
            assert found in numbers, found
            aList = [z for z in aList if z not in numbers]
            aList.append(found)
        if trace: g.trace(aList)
        return aList

    def reduce_types(self):
        '''
        self.aList consists of arbitrarily many types because this method is
        called from format_return_expressions.
        
        Return a *string* containing the reduction of all types in this list.
        Returning a string means that all traversers always return strings,
        never lists.
        '''
        trace = False
        if trace: g.trace('=====', self.aList)
        r = [('None' if z in ('', None) else z) for z in self.aList]
        assert None not in r
        self.optional = 'None' in r
            # self.show adds Optional if this flag is set.
        r = [z for z in r if z != 'None']
        if not r:
            self.optional = False
            return self.show('None')
        r = sorted(set(r))
        assert r
        assert None not in r
        r = self.reduce_numbers(r)
        for kind in ('Dict', 'List', 'Tuple',):
            r = self.reduce_collection(r, kind)
        r = self.reduce_unknowns(r)
        r = sorted(set(r))
        assert r
        assert 'None' not in r
        if len(r) == 1:
            return self.show(r[0])
        else:
            return self.show('Union[%s]' % (', '.join(sorted(r))))

    def reduce_unknowns(self, aList):
        '''Replace all unknown types in aList with Any.'''
        return [z if self.is_known_type(z) else 'Any' for z in aList]

    def show(self, s, known=True):
        '''Show the result of reduce_types.'''
        aList, name = self.aList, self.name
        trace = False or self.trace
        s = s.strip()
        if self.optional:
            s = 'Optional[%s]' % s
        if trace and (not known or len(aList) > 1):
            if name:
                if name.find('.') > -1:
                    context = ''.join(name.split('.')[1:])
                else:
                    context = name
            else:
                context = g.callers(3).split(',')[0].strip()
            context = truncate(context, 26)
            known = '' if known else '? '
            pattern = sorted(set([z.replace('\n',' ') for z in aList]))
            pattern = '[%s]' % truncate(', '.join(pattern), 53-2)
            print('reduce_types: %-26s %53s ==> %s%s' % (context, pattern, known, s))
                # widths above match the corresponding indents in match_all and match.
        return s

    def split_types(self, s):
        '''Split types on *outer level* commas.'''
        aList, i1, level = [], 0, 0
        for i, ch in enumerate(s):
            if ch == '[':
                level += 1
            elif ch == ']':
                level -= 1
            elif ch == ',' and level == 0:
                aList.append(s[i1:i])
                i1 = i+1
        aList.append(s[i1:].strip())
        return aList


class StandAloneMakeStubFile:
    '''
    A class to make Python stub (.pyi) files in the ~/stubs directory for
    every file mentioned in the [Source Files] section of
    ~/stubs/make_stub_files.cfg.
    '''

    def __init__ (self):
        '''Ctor for StandAloneMakeStubFile class.'''
        self.options = {}
        # Ivars set on the command line...
        self.config_fn = None
            # self.finalize('~/stubs/make_stub_files.cfg')
        self.enable_unit_tests = False
        self.files = [] # May also be set in the config file.
        # Ivars set in the config file...
        self.output_fn = None
        self.output_directory = self.finalize('.')
            # self.finalize('~/stubs')
        self.overwrite = False
        self.prefix_lines = []
        self.trace_matches = False
        self.trace_patterns = False
        self.trace_reduce = False
        self.trace_visitors = False
        self.update_flag = False
        self.verbose = False # Trace config arguments.
        self.warn = False
        # Pattern lists, set by config sections...
        self.section_names = (
            'Global', 'Def Name Patterns', 'General Patterns')
        self.def_patterns = [] # [Def Name Patterns]
        self.general_patterns = [] # [General Patterns]
        self.names_dict = {}
        self.op_name_dict = self.make_op_name_dict()
        self.patterns_dict = {}
        self.regex_patterns = []

    def finalize(self, fn):
        '''Finalize and regularize a filename.'''
        fn = os.path.expanduser(fn)
        fn = os.path.abspath(fn)
        fn = os.path.normpath(fn)
        return fn

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
        base_fn = os.path.basename(fn)
        out_fn = os.path.join(self.output_directory, base_fn)
        out_fn = out_fn[:-3] + '.pyi'
        self.output_fn = os.path.normpath(out_fn)
        s = open(fn).read()
        node = ast.parse(s,filename=fn,mode='exec')
        StubTraverser(controller=self).run(node)

    def run(self):
        '''
        Make stub files for all files.
        Do nothing if the output directory does not exist.
        '''
        if self.enable_unit_tests:
            self.run_all_unit_tests()
        if self.files:
            dir_ = self.output_directory
            if dir_:
                if os.path.exists(dir_):
                    for fn in self.files:
                        self.make_stub_file(fn)
                else:
                    print('output directory not found: %s' % dir_)
            else:
                print('no output directory')
        elif not self.enable_unit_tests:
            print('no input files')

    def run_all_unit_tests(self):
        '''Run all unit tests in the make_stub_files/test directory.'''
        import unittest
        loader = unittest.TestLoader()
        suite = loader.discover(os.path.abspath('.'),
                                pattern='test*.py',
                                top_level_dir=None)
        unittest.TextTestRunner(verbosity=1).run(suite)

    def scan_command_line(self):
        '''Set ivars from command-line arguments.'''
        # This automatically implements the --help option.
        usage = "usage: make_stub_files.py [options] file1, file2, ..."
        parser = optparse.OptionParser(usage=usage)
        add = parser.add_option
        add('-c', '--config', dest='fn',
            help='full path to configuration file')
        add('-d', '--dir', dest='dir',
            help='full path to the output directory')
        add('-o', '--overwrite', action='store_true', default=False,
            help='overwrite existing stub (.pyi) files')
        add('-t', '--test', action='store_true', default=False,
            help='run unit tests on startup')
        add('--trace-matches', action='store_true', default=False,
            help='trace Pattern.matches')
        add('--trace-patterns', action='store_true', default=False,
            help='trace pattern creation')
        add('--trace-reduce', action='store_true', default=False,
            help='trace st.reduce_types')
        add('--trace-visitors', action='store_true', default=False,
            help='trace visitor methods')
        add('-u', '--update', action='store_true', default=False,
            help='update stubs in existing stub file')
        add('-v', '--verbose', action='store_true', default=False,
            help='verbose output in .pyi file')
        add('-w', '--warn', action='store_true', default=False,
            help='warn about unannotated args')
        # Parse the options
        options, args = parser.parse_args()
        # Handle the options...
        self.enable_unit_tests=options.test
        self.overwrite = options.overwrite
        self.trace_matches = options.trace_matches
        self.trace_patterns = options.trace_patterns
        self.trace_reduce = options.trace_reduce
        self.trace_visitors = options.trace_visitors
        self.update_flag = options.update
        self.verbose = options.verbose
        self.warn = options.warn
        if options.fn:
            self.config_fn = options.fn
        if options.dir:
            dir_ = options.dir
            dir_ = self.finalize(dir_)
            if os.path.exists(dir_):
                self.output_directory = dir_
            else:
                print('--dir: directory does not exist: %s' % dir_)
                print('exiting')
                sys.exit(1)
        # If any files remain, set self.files.
        if args:
            args = [self.finalize(z) for z in args]
            if args:
                self.files = args

    def scan_options(self):
        '''Set all configuration-related ivars.'''
        trace = False
        if not self.config_fn:
            return
        self.parser = parser = self.create_parser()
        s = self.get_config_string()
        self.init_parser(s)
        if self.files:
            files_source = 'command-line'
            files = self.files
        elif parser.has_section('Global'):
            files_source = 'config file'
            files = parser.get('Global', 'files')
            files = [z.strip() for z in files.split('\n') if z.strip()]
        else:
            return
        files2 = []
        for z in files:
            files2.extend(glob.glob(self.finalize(z)))
        self.files = [z for z in files2 if z and os.path.exists(z)]
        if trace:
            print('Files (from %s)...\n' % files_source)
            for z in self.files:
                print(z)
            print('')
        if 'output_directory' in parser.options('Global'):
            s = parser.get('Global', 'output_directory')
            output_dir = self.finalize(s)
            if os.path.exists(output_dir):
                self.output_directory = output_dir
                if self.verbose:
                    print('output directory: %s\n' % output_dir)
            else:
                print('output directory not found: %s\n' % output_dir)
                self.output_directory = None # inhibit run().
        if 'prefix_lines' in parser.options('Global'):
            prefix = parser.get('Global', 'prefix_lines')
            self.prefix_lines = prefix.split('\n')
                # The parser does not preserve leading whitespace.
            if trace:
                print('Prefix lines...\n')
                for z in self.prefix_lines:
                    print(z)
                print('')
        self.def_patterns = self.scan_patterns('Def Name Patterns')
        self.general_patterns = self.scan_patterns('General Patterns')
        self.make_patterns_dict()

    def make_op_name_dict(self):
        '''
        Make a dict whose keys are operators ('+', '+=', etc),
        and whose values are lists of values of ast.Node.__class__.__name__.
        '''
        d = {
            '.':   ['Attr',],
            '(*)': ['Call', 'Tuple',],
            '[*]': ['List', 'Subscript',],
            '{*}': ['???',],
            ### 'and': 'BoolOp',
            ### 'or':  'BoolOp',
        }
        for op in (
            '+', '-', '*', '/', '%', '**', '<<',
            '>>', '|', '^', '&', '//',
        ):
            d[op] = ['BinOp',]
        for op in (
            '==', '!=', '<', '<=', '>', '>=',
            'is', 'is not', 'in', 'not in',
        ):
            d[op] = ['Compare',]
        return d

    def create_parser(self):
        '''Create a RawConfigParser and return it.'''
        parser = configparser.RawConfigParser(dict_type=OrderedDict)
            # Requires Python 2.7
        parser.optionxform = str
        return parser

    def find_pattern_ops(self, pattern):
        '''Return a list of operators in pattern.find_s.'''
        trace = False or self.trace_patterns
        if pattern.is_regex():
            # Add the pattern to the regex patterns list.
            g.trace(pattern)
            self.regex_patterns.append(pattern)
            return []
        d = self.op_name_dict
        keys1, keys2, keys3, keys9 = [], [], [], []
        for op in d:
            aList = d.get(op)
            if op.replace(' ','').isalnum():
                # an alpha op, like 'not, 'not in', etc.
                keys9.append(op)
            elif len(op) == 3:
                keys3.append(op)
            elif len(op) == 2:
                keys2.append(op)
            elif len(op) == 1:
                keys1.append(op)
            else:
                g.trace('bad op', op)
        ops = []
        s = s1 = pattern.find_s
        for aList in (keys3, keys2, keys1):
            for op in aList:
                # Must match word here!
                if s.find(op) > -1:
                    s = s.replace(op, '')
                    ops.append(op)
        # Handle the keys9 list very carefully.
        for op in keys9:
            target = ' %s ' % op
            if s.find(target) > -1:
                ops.append(op)
                break # Only one match allowed.
        if trace and ops: g.trace(s1, ops)
        return ops

    def get_config_string(self):
        
        fn = self.finalize(self.config_fn)
        if os.path.exists(fn):
            if self.verbose:
                print('\nconfiguration file: %s\n' % fn)
            f = open(fn, 'r')
            s = f.read()
            f.close()
            return s
        else:
            print('\nconfiguration file not found: %s' % fn)
            return ''
        

    def init_parser(self, s):
        '''Add double back-slashes to all patterns starting with '['.'''
        trace = False
        if not s: return
        aList = []
        for s in s.split('\n'):
            if self.is_section_name(s):
                aList.append(s)
            elif s.strip().startswith('['):
                aList.append(r'\\'+s[1:])
                if trace: g.trace('*** escaping:',s)
            else:
                aList.append(s)
        s = '\n'.join(aList)+'\n'
        if trace: g.trace(s)
        file_object = io.StringIO(s)
        # pylint: disable=deprecated-method
        self.parser.readfp(file_object)

    def is_section_name(self, s):
        
        def munge(s):
            return s.strip().lower().replace(' ','')
        
        s = s.strip()
        if s.startswith('[') and s.endswith(']'):
            s = munge(s[1:-1])
            for s2 in self.section_names:
                if s == munge(s2):
                    return True
        return False

    def make_patterns_dict(self):
        '''Assign all patterns to the appropriate ast.Node.'''
        trace = False or self.trace_patterns
        for pattern in self.general_patterns:
            ops = self.find_pattern_ops(pattern)
            if ops:
                for op in ops:
                    # Add the pattern to op's list.
                    op_names = self.op_name_dict.get(op)
                    for op_name in op_names:
                        aList = self.patterns_dict.get(op_name, [])
                        aList.append(pattern)
                        self.patterns_dict[op_name] = aList
            else:
                # Enter the name in self.names_dict.
                name = pattern.find_s
                # Special case for 'number'
                if name == 'number':
                    aList = self.patterns_dict.get('Num', [])
                    aList.append(pattern)
                    self.patterns_dict['Num'] = aList
                elif name in self.names_dict:
                    g.trace('duplicate pattern', pattern)
                else:
                    self.names_dict [name] = pattern.repl_s
        if 0:
            g.trace('names_dict...')
            for z in sorted(self.names_dict):
                print('  %s: %s' % (z, self.names_dict.get(z)))
        if 0:
            g.trace('patterns_dict...')
            for z in sorted(self.patterns_dict):
                aList = self.patterns_dict.get(z)
                print(z)
                for pattern in sorted(aList):
                    print('  '+repr(pattern))
        # Note: retain self.general_patterns for use in argument lists.

    def scan_patterns(self, section_name):
        '''Parse the config section into a list of patterns, preserving order.'''
        trace = False or self.trace_patterns
        parser = self.parser
        aList = []
        if parser.has_section(section_name):
            seen = set()
            for key in parser.options(section_name):
                value = parser.get(section_name, key)
                # A kludge: strip leading \\ from patterns.
                if key.startswith(r'\\'):
                    key = '[' + key[2:]
                    if trace: g.trace('removing escapes', key)
                if key in seen:
                    g.trace('duplicate key', key)
                else:
                    seen.add(key)
                    aList.append(Pattern(key, value))
            if trace:
                g.trace('%s...\n' % section_name)
                for z in aList:
                    print(z)
                print('')
        # elif trace:
            # print('no section: %s' % section_name)
            # print(parser.sections())
            # print('')
        return aList


class Stub(object):
    '''
    A class representing all the generated stub for a class or def.
    stub.full_name should represent the complete context of a def.
    '''

    def __init__(self, kind, name, parent=None, stack=None):
        '''Stub ctor. Equality depends only on full_name and kind.'''
        self.children = []
        self.full_name = '%s.%s' % ('.'.join(stack), name) if stack else name
        self.kind = kind
        self.name = name
        self.out_list = []
        self.parent = parent
        self.stack = stack # StubTraverser.context_stack.
        if stack:
            assert stack[-1] == parent.name, (stack[-1], parent.name)
        if parent:
            assert isinstance(parent, Stub)
            parent.children.append(self)

    def __eq__(self, obj):
        '''
        Stub.__eq__. Return whether two stubs refer to the same method.
        Do *not* test parent links. That would interfere with --update logic.
        '''
        if isinstance(obj, Stub):
            return self.full_name == obj.full_name and self.kind == obj.kind
        else:
            return NotImplemented

    def __ne__(self, obj):
        """Stub.__ne__"""
        return not self.__eq__(obj)

    def __hash__(self):
        '''Stub.__hash__. Equality depends *only* on full_name and kind.'''
        return len(self.kind) + sum([ord(z) for z in self.full_name])

    def __repr__(self):
        '''Stub.__repr__.'''
        return 'Stub: %s %s' % (id(self), self.full_name)
        
    def __str__(self):
        '''Stub.__repr__.'''
        return 'Stub: %s' % self.full_name

    def level(self):
        '''Return the number of parents.'''
        return len(self.parents())
        
    def parents(self):
        '''Return a list of this stub's parents.'''
        return self.full_name.split('.')[:-1]


class StubFormatter (AstFormatter):
    '''
    Formats an ast.Node and its descendants,
    making pattern substitutions in Name and operator nodes.
    '''

    def __init__(self, controller, traverser):
        '''Ctor for StubFormatter class.'''
        self.controller = x = controller
        self.traverser = traverser
            # 2016/02/07: to give the formatter access to the class_stack.
        self.def_patterns = x.def_patterns
        self.general_patterns = x.general_patterns
        self.names_dict = x.names_dict
        self.patterns_dict = x.patterns_dict
        self.raw_format = AstFormatter().format
        self.regex_patterns = x.regex_patterns
        self.trace_matches = x.trace_matches
        self.trace_patterns = x.trace_patterns
        self.trace_reduce = x.trace_reduce
        self.trace_visitors = x.trace_visitors
        self.verbose = x.verbose

    matched_d = {}

    def match_all(self, node, s, trace=False):
        '''Match all the patterns for the given node.'''
        trace = False or trace or self.trace_matches
        # verbose = True
        d = self.matched_d
        name = node.__class__.__name__
        s1 = truncate(s, 40)
        caller = g.callers(2).split(',')[1].strip()
            # The direct caller of match_all.
        patterns = self.patterns_dict.get(name, []) + self.regex_patterns
        for pattern in patterns:
            found, s = pattern.match(s,trace=False)
            if found:
                if trace:
                    aList = d.get(name, [])
                    if pattern not in aList:
                        aList.append(pattern)
                        d [name] = aList
                        print('match_all:    %-12s %26s %40s ==> %s' % (caller, pattern, s1, s))
                break
        return s

    def visit(self, node):
        '''StubFormatter.visit: supports --verbose tracing.'''
        s = AstFormatter.visit(self, node)
        # g.trace('%12s %s' % (node.__class__.__name__,s))
        return s

    def trace_visitor(self, node, op, s):
        '''Trace node's visitor.'''
        if self.trace_visitors:
            caller = g.callers(2).split(',')[1]
            s1 = AstFormatter().format(node).strip()
            print('%12s op %-6s: %s ==> %s' % (caller, op.strip(), s1, s))

    # StubFormatter visitors for operands...

    # Attribute(expr value, identifier attr, expr_context ctx)

    attrs_seen = []

    def do_Attribute(self, node):
        '''StubFormatter.do_Attribute.'''
        trace = False
        s = '%s.%s' % (
            self.visit(node.value),
            node.attr) # Don't visit node.attr: it is always a string.
        s2 = self.names_dict.get(s)
        if trace and s2 and s2 not in self.attrs_seen:
            self.attrs_seen.append(s2)
            g.trace(s, '==>', s2)
        return s2 or s

    # Return generic markers to allow better pattern matches.

    def do_Bytes(self, node): # Python 3.x only.
        return 'bytes' # return str(node.s)

    def do_Num(self, node):
        # make_patterns_dict treats 'number' as a special case.
        # return self.names_dict.get('number', 'number')
        return 'number' # return repr(node.n)

    def do_Str(self, node):
        '''This represents a string constant.'''
        return 'str' # return repr(node.s)

    def do_Dict(self, node):
        result = []
        keys = [self.visit(z) for z in node.keys]
        values = [self.visit(z) for z in node.values]
        if len(keys) == len(values):
            result.append('{')
            items = []
            for i in range(len(keys)):
                items.append('%s:%s' % (keys[i], values[i]))
            result.append(', '.join(items))
            result.append('}')
        else:
            print('Error: f.Dict: len(keys) != len(values)\nkeys: %s\nvals: %s' % (
                repr(keys), repr(values)))
        # return ''.join(result)
        return 'Dict[%s]' % ''.join(result)

    def do_List(self, node):
        '''StubFormatter.List.'''
        elts = [self.visit(z) for z in node.elts]
        elst = [z for z in elts if z] # Defensive.
        # g.trace('=====',elts)
        return 'List[%s]' % ', '.join(elts)

    seen_names = []

    def do_Name(self, node):
        '''StubFormatter ast.Name visitor.'''
        trace = False
        d = self.names_dict
        name = d.get(node.id, node.id)
        s = 'bool' if name in ('True', 'False') else name
        if trace and node.id not in self.seen_names:
            self.seen_names.append(node.id)
            if d.get(node.id):
                g.trace(node.id, '==>', d.get(node.id))
            elif node.id == 'aList':
                g.trace('**not found**', node.id)
        return s

    def do_Tuple(self, node):
        '''StubFormatter.Tuple.'''
        elts = [self.visit(z) for z in node.elts]
        if 1:
            return 'Tuple[%s]' % ', '.join(elts)
        else:
            s = '(%s)' % ', '.join(elts)
            return self.match_all(node, s)
        # return 'Tuple[%s]' % ', '.join(elts)

    # StubFormatter visitors for operators...

    # BinOp(expr left, operator op, expr right)

    def do_BinOp(self, node):
        '''StubFormatter.BinOp visitor.'''
        trace = False or self.trace_reduce ; verbose = False
        numbers = ['number', 'complex', 'float', 'long', 'int',]
        op = self.op_name(node.op)
        lhs = self.visit(node.left)
        rhs = self.visit(node.right)
        if op.strip() in ('is', 'is not', 'in', 'not in'):
            s = 'bool'
        elif lhs == rhs:
            s = lhs
                # Perhaps not always right,
                # but it is correct for Tuple, List, Dict.
        elif lhs in numbers and rhs in numbers:
            s = reduce_types([lhs, rhs], trace=trace)
                # reduce_numbers would be wrong: it returns a list.
        elif lhs == 'str' and op in '%+*':
            # str + any implies any is a string.
            s = 'str'
        else:
            if trace and verbose and lhs == 'str':
                g.trace('***** unknown string op', lhs, op, rhs)
            # Fall back to the base-class behavior.
            s = '%s%s%s' % (
                self.visit(node.left),
                op,
                self.visit(node.right))
        s = self.match_all(node, s)
        self.trace_visitor(node, op, s)
        return s

    # BoolOp(boolop op, expr* values)

    def do_BoolOp(self, node): # Python 2.x only.
        '''StubFormatter.BoolOp visitor for 'and' and 'or'.'''
        trace = False or self.trace_reduce
        op = self.op_name(node.op)
        values = [self.visit(z).strip() for z in node.values]
        s = reduce_types(values, trace=trace)
        s = self.match_all(node, s)
        self.trace_visitor(node, op, s)
        return s

    # Call(expr func, expr* args, keyword* keywords, expr? starargs, expr? kwargs)

    def do_Call(self, node):
        '''StubFormatter.Call visitor.'''
        trace = False
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
        # Explicit pattern:
        if func in ('dict', 'list', 'set', 'tuple',):
            s = '%s[%s]' % (func.capitalize(), ', '.join(args))
        else:
            s = '%s(%s)' % (func, ', '.join(args))
        s = self.match_all(node, s, trace=trace)
        self.trace_visitor(node, 'call', s)
        return s

    # keyword = (identifier arg, expr value)

    def do_keyword(self, node):
        # node.arg is a string.
        value = self.visit(node.value)
        # This is a keyword *arg*, not a Python keyword!
        return '%s=%s' % (node.arg, value)

    # Compare(expr left, cmpop* ops, expr* comparators)

    def do_Compare(self, node):
        '''
        StubFormatter ast.Compare visitor for these ops:
        '==', '!=', '<', '<=', '>', '>=', 'is', 'is not', 'in', 'not in',
        '''
        s = 'bool' # Correct regardless of arguments.
        ops = ','.join([self.op_name(z) for z in node.ops])
        self.trace_visitor(node, ops, s)
        return s

    # If(expr test, stmt* body, stmt* orelse)

    def do_IfExp(self, node):
        '''StubFormatterIfExp (ternary operator).'''
        trace = False or self.trace_reduce
        aList = [
            self.match_all(node, self.visit(node.body)),
            self.match_all(node, self.visit(node.orelse)),
        ]
        s = reduce_types(aList, trace=trace)
        s = self.match_all(node, s)
        self.trace_visitor(node, 'if', s)
        return s

    # Subscript(expr value, slice slice, expr_context ctx)

    def do_Subscript(self, node):
        '''StubFormatter.Subscript.'''
        s = '%s[%s]' % (
            self.visit(node.value),
            self.visit(node.slice))
        s = self.match_all(node, s)
        self.trace_visitor(node, '[]', s)
        return s

    # UnaryOp(unaryop op, expr operand)

    def do_UnaryOp(self, node):
        '''StubFormatter.UnaryOp for unary +, -, ~ and 'not' operators.'''
        op = self.op_name(node.op)
        # g.trace(op.strip(), self.raw_format(node.operand))
        if op.strip() == 'not':
            return 'bool'
        else:
            s = self.visit(node.operand)
            s = self.match_all(node, s)
            self.trace_visitor(node, op, s)
            return s

    def do_Return(self, node):
        '''
        StubFormatter ast.Return vsitor.
        Return only the return expression itself.
        '''
        s = AstFormatter.do_Return(self, node)
        assert s.startswith('return'), repr(s)
        return s[len('return'):].strip()


class StubTraverser (ast.NodeVisitor):
    '''
    An ast.Node traverser class that outputs a stub for each class or def.
    Names of visitors must start with visit_. The order of traversal does
    not matter, because so few visitors do anything.
    '''

    def __init__(self, controller):
        '''Ctor for StubTraverser class.'''
        self.controller = x = controller
            # A StandAloneMakeStubFile instance.
        # Internal state ivars...
        self.class_name_stack = []
        self.context_stack = []
        sf = StubFormatter(controller=controller,traverser=self)
        self.format = sf.format
        self.arg_format = AstArgFormatter().format
        self.level = 0
        self.output_file = None
        self.parent_stub = None
        self.raw_format = AstFormatter().format
        self.returns = []
        self.stubs_dict = {}
            # Keys are stub.full_name's.  Values are stubs.
        self.warn_list = []
        # Copies of controller ivars...
        self.output_fn = x.output_fn
        self.overwrite = x.overwrite
        self.prefix_lines = x.prefix_lines
        self.regex_patterns = x.regex_patterns
        self.update_flag = x.update_flag
        self.trace_matches = x.trace_matches
        self.trace_patterns = x.trace_patterns
        self.trace_reduce = x.trace_reduce
        self.trace_visitors = x.trace_visitors
        self.verbose = x.verbose
        self.warn = x.warn
        # Copies of controller patterns...
        self.def_patterns = x.def_patterns
        self.names_dict = x.names_dict
        self.general_patterns = x.general_patterns
        self.patterns_dict = x.patterns_dict
        

    def add_stub(self, d, stub):
        '''Add the stub to d, checking that it does not exist.'''
        trace = False ; verbose = False
        key = stub.full_name
        assert key
        if key in d:
            caller = g.callers(2).split(',')[1]
            g.trace('Ignoring duplicate entry for %s in %s' % (stub, caller))
        else:
            d [key] = stub
            if trace and verbose:
                caller = g.callers(2).split(',')[1]
                g.trace('%17s %s' % (caller, stub.full_name))
            elif trace:
                g.trace(stub.full_name)

    def indent(self, s):
        '''Return s, properly indented.'''
        # This version of indent *is* used.
        return '%s%s' % (' ' * 4 * self.level, s)

    def out(self, s):
        '''Output the string to the console or the file.'''
        s = self.indent(s)
        if self.parent_stub:
            self.parent_stub.out_list.append(s)
        elif self.output_file:
            self.output_file.write(s+'\n')
        else:
            print(s)

    def run(self, node):
        '''StubTraverser.run: write the stubs in node's tree to self.output_fn.'''
        fn = self.output_fn
        dir_ = os.path.dirname(fn)
        if os.path.exists(fn) and not self.overwrite:
            print('file exists: %s' % fn)
        elif not dir_ or os.path.exists(dir_):
            t1 = time.clock()
            # Delayed output allows sorting.
            self.parent_stub = Stub(kind='root', name='<new-stubs>')
            for z in self.prefix_lines or []:
                self.parent_stub.out_list.append(z)
            self.visit(node)
                # Creates parent_stub.out_list.
            if self.update_flag:
                self.parent_stub = self.update(fn, new_root=self.parent_stub)
            if 1:
                self.output_file = open(fn, 'w')
                self.output_time_stamp()
                self.output_stubs(self.parent_stub)
                self.output_file.close()
                self.output_file = None
                self.parent_stub = None
            t2 = time.clock()
            print('wrote: %s in %4.2f sec' % (fn, t2 - t1))
        else:
            print('output directory not not found: %s' % dir_)

    def output_stubs(self, stub):
        '''Output this stub and all its descendants.'''
        for s in stub.out_list or []:
            # Indentation must be present when an item is added to stub.out_list.
            if self.output_file:
                self.output_file.write(s.rstrip()+'\n')
            else:
                print(s)
        # Recursively print all children.
        for child in stub.children:
            self.output_stubs(child)

    def output_time_stamp(self):
        '''Put a time-stamp in the output file.'''
        if self.output_file:
            self.output_file.write('# make_stub_files: %s\n' %
                time.strftime("%a %d %b %Y at %H:%M:%S"))

    def update(self, fn, new_root):
        '''
        Merge the new_root tree with the old_root tree in fn (a .pyi file).

        new_root is the root of the stub tree from the .py file.
        old_root (read below) is the root of stub tree from the .pyi file.
        
        Return old_root, or new_root if there are any errors.
        '''
        trace = False ; verbose = False
        s = self.get_stub_file(fn)
        if not s or not s.strip():
            return new_root
        if '\t' in s:
            # Tabs in stub files make it impossible to parse them reliably.
            g.trace('Can not update stub files containing tabs.')
            return new_root
        # Read old_root from the .pyi file.
        old_d, old_root = self.parse_stub_file(s, root_name='<old-stubs>')
        if old_root:
            # Merge new stubs into the old tree.
            if trace and verbose:
                print(self.trace_stubs(old_root, header='old_root'))
                print(self.trace_stubs(new_root, header='new_root'))
            print('***** updating stubs from %s *****' % fn)
            self.merge_stubs(self.stubs_dict.values(), old_root, new_root)
            if trace:
                print(self.trace_stubs(old_root, header='updated_root'))
            return old_root
        else:
            return new_root

    def get_stub_file(self, fn):
        '''Read the stub file into s.'''
        if os.path.exists(fn):
            try:
                s = open(fn, 'r').read()
            except Exception:
                print('--update: error reading %s' % fn)
                s = None
            return s
        else:
            print('--update: not found: %s' % fn)
            return None

    def parse_stub_file(self, s, root_name):
        '''
        Parse s, the contents of a stub file, into a tree of Stubs.
        
        Parse by hand, so that --update can be run with Python 2.
        '''
        trace = False
        assert '\t' not in s
        d = {}
        root = Stub(kind='root', name=root_name)
        indent_stack = [-1] # To prevent the root from being popped.
        stub_stack = [root]
        lines = []
        pat = re.compile(r'^([ ]*)(def|class)\s+([a-zA-Z_]+)(.*)')
        for line in g.splitLines(s):
            m = pat.match(line)
            if m:
                indent, kind, name, rest = (
                    len(m.group(1)), m.group(2), m.group(3), m.group(4))
                old_indent = indent_stack[-1]
                # Terminate any previous lines.
                old_stub = stub_stack[-1]
                old_stub.out_list.extend(lines)
                if trace:
                    for s in lines:
                        g.trace('  '+s.rstrip())
                lines = [line]
                # Adjust the stacks.
                if indent == old_indent:
                    stub_stack.pop()
                elif indent > old_indent:
                    indent_stack.append(indent)
                else: # indent < old_indent
                    # The indent_stack can't underflow because
                    # indent >= 0 and indent_stack[0] < 0
                    assert indent >= 0
                    while indent <= indent_stack[-1]:
                        indent_stack.pop()
                        old_stub = stub_stack.pop()
                        assert old_stub != root
                    indent_stack.append(indent)
                # Create and push the new stub *after* adjusting the stacks.
                assert stub_stack
                parent = stub_stack[-1]
                stack = [z.name for z in stub_stack[1:]]
                parent = stub_stack[-1]
                stub = Stub(kind, name, parent, stack)
                self.add_stub(d, stub)
                stub_stack.append(stub)
                if trace:
                    g.trace('%s%5s %s %s' % (' '*indent, kind, name, rest))
            else:
                parent = stub_stack[-1]
                lines.append(line)
        # Terminate the last stub.
        old_stub = stub_stack[-1]
        old_stub.out_list.extend(lines)
        if trace:
            for s in lines:
                g.trace('  '+s.rstrip())
        return d, root

    def merge_stubs(self, new_stubs, old_root, new_root, trace=False):
        '''
        Merge the new_stubs *list* into the old_root *tree*.
        - new_stubs is a list of Stubs from the .py file.
        - old_root is the root of the stubs from the .pyi file.
        - new_root is the root of the stubs from the .py file.
        '''
        trace = False or trace ; verbose = False
        # Part 1: Delete old stubs do *not* exist in the *new* tree.
        aList = self.check_delete(new_stubs,
                                  old_root,
                                  new_root,
                                  trace and verbose)
            # Checks that all ancestors of deleted nodes will be deleted.
        aList = list(reversed(self.sort_stubs_by_hierarchy(aList)))
            # Sort old stubs so that children are deleted before parents.
        if trace and verbose:
            dump_list('ordered delete list', aList)
        for stub in aList:
            if trace: g.trace('deleting  %s' % stub)
            parent = self.find_parent_stub(stub, old_root) or old_root
            parent.children.remove(stub)
            assert not self.find_stub(stub, old_root), stub
        # Part 2: Insert new stubs that *not* exist in the *old* tree.
        aList = [z for z in new_stubs if not self.find_stub(z, old_root)]
        aList = self.sort_stubs_by_hierarchy(aList)
            # Sort new stubs so that parents are created before children.
        for stub in aList:
            if trace: g.trace('inserting %s' % stub)
            parent = self.find_parent_stub(stub, old_root) or old_root
            parent.children.append(stub)
            assert self.find_stub(stub, old_root), stub

    def check_delete(self, new_stubs, old_root, new_root, trace):
        '''Return a list of nodes that can be deleted.'''
        old_stubs = self.flatten_stubs(old_root)
        old_stubs.remove(old_root)
        aList = [z for z in old_stubs if z not in new_stubs]
        if trace:
            dump_list('old_stubs', old_stubs)
            dump_list('new_stubs', new_stubs)
            dump_list('to-be-deleted stubs', aList)
        delete_list = []
        # Check that all parents of to-be-delete nodes will be deleted.
        for z in aList:
            z1 = z
            for i in range(20):
                z = z.parent
                if not z:
                    g.trace('can not append: new root not found', z)
                    break
                elif z == old_root:
                    # if trace: g.trace('can delete', z1)
                    delete_list.append(z1)
                    break
                elif z not in aList:
                    g.trace("can not delete %s because of %s" % (z1, z))
                    break
            else:
                g.trace('can not happen: parent loop')
        if trace:
            dump_list('delete_list', delete_list)
        return delete_list

    def flatten_stubs(self, root):
        '''Return a flattened list of all stubs in root's tree.'''
        aList = [root]
        for child in root.children:
            self.flatten_stubs_helper(child, aList)
        return aList
            
    def flatten_stubs_helper(self, root, aList):
        '''Append all stubs in root's tree to aList.'''
        aList.append(root)
        for child in root.children:
            self.flatten_stubs_helper(child, aList)

    def find_parent_stub(self, stub, root):
        '''Return stub's parent **in root's tree**.'''
        return self.find_stub(stub.parent, root) if stub.parent else None

    def find_stub(self, stub, root):
        '''Return the stub **in root's tree** that matches stub.'''
        if stub == root: # Must use Stub.__eq__!
            return root # not stub!
        for child in root.children:
            stub2 = self.find_stub(stub, child)
            if stub2: return stub2
        return None

    def sort_stubs_by_hierarchy(self, stubs1):
        '''
        Sort the list of Stubs so that parents appear before all their
        descendants.
        '''
        stubs, result = stubs1[:], []
        for i in range(50):
            if stubs:
                # Add all stubs with i parents to the results.
                found = [z for z in stubs if z.level() == i]
                result.extend(found)
                for z in found:
                    stubs.remove(z)
            else:
                return result
        g.trace('can not happen: unbounded stub levels.')
        return [] # Abort the merge.

    def trace_stubs(self, stub, aList=None, header=None, level=-1):
        '''Return a trace of the given stub and all its descendants.'''
        indent = ' '*4*max(0,level)
        if level == -1:
            aList = ['===== %s...\n' % (header) if header else '']
        for s in stub.out_list:
            aList.append('%s%s' % (indent, s.rstrip()))
        for child in stub.children:
            self.trace_stubs(child, level=level+1, aList=aList)
        if level == -1:
            return '\n'.join(aList) + '\n'

    # ClassDef(identifier name, expr* bases, stmt* body, expr* decorator_list)

    def visit_ClassDef(self, node):
        
        # Create the stub in the old context.
        old_stub = self.parent_stub
        self.parent_stub = Stub('class', node.name,old_stub, self.context_stack)
        self.add_stub(self.stubs_dict, self.parent_stub)
        # Enter the new context.
        self.class_name_stack.append(node.name)
        self.context_stack.append(node.name)
        if self.trace_matches or self.trace_reduce:
            print('\nclass %s\n' % node.name)
        # Format...
        if not node.name.startswith('_'):
            if node.bases:
                s = '(%s)' % ', '.join([self.format(z) for z in node.bases])
            else:
                s = ''
            self.out('class %s%s:' % (node.name, s))
        # Visit...
        self.level += 1
        for z in node.body:
            self.visit(z)
        self.context_stack.pop()
        self.class_name_stack.pop()
        self.level -= 1
        self.parent_stub = old_stub

    # FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list)

    def visit_FunctionDef(self, node):

        # Create the stub in the old context.
        old_stub = self.parent_stub
        self.parent_stub = Stub('def', node.name, old_stub, self.context_stack)
        self.add_stub(self.stubs_dict, self.parent_stub)
        # Enter the new context.
        self.returns = []
        self.level += 1
        self.context_stack.append(node.name)
        for z in node.body:
            self.visit(z)
        self.context_stack.pop()
        self.level -= 1
        # Format *after* traversing
        # if self.trace_matches or self.trace_reduce:
            # if not self.class_name_stack:
                # print('def %s\n' % node.name)
        self.out('def %s(%s) -> %s' % (
            node.name,
            self.format_arguments(node.args),
            self.format_returns(node)))
        self.parent_stub = old_stub

    # arguments = (expr* args, identifier? vararg, identifier? kwarg, expr* defaults)

    def format_arguments(self, node):
        '''
        Format the arguments node.
        Similar to AstFormat.do_arguments, but it is not a visitor!
        '''
        assert isinstance(node,ast.arguments), node
        args = [self.raw_format(z) for z in node.args]
        defaults = [self.raw_format(z) for z in node.defaults]
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
        if name:
            if hasattr(ast, 'arg'): # python 3:
                name = self.raw_format(name)
            result.append('*' + name)
        name = getattr(node, 'kwarg', None)
        if name:
            if hasattr(ast, 'arg'): # python 3:
                name = self.raw_format(name)
            result.append('**' + name)
        return ', '.join(result)

    def munge_arg(self, s):
        '''Add an annotation for s if possible.'''
        if s == 'self':
            return s
        for pattern in self.general_patterns:
            if pattern.match_entire_string(s):
                return '%s: %s' % (s, pattern.repl_s)
        if self.warn and s not in self.warn_list:
            self.warn_list.append(s)
            print('no annotation for %s' % s)
        return s + ': Any'

    def format_returns(self, node):
        '''
        Calculate the return type:
        - Return None if there are no return statements.
        - Patterns in [Def Name Patterns] override all other patterns.
        - Otherwise, return a list of return values.
        '''
        trace = False
        name = self.get_def_name(node)
        raw = [self.raw_format(z) for z in self.returns]
        r = [self.format(z) for z in self.returns]
            # Allow StubFormatter.do_Return to do the hack.
        # Step 1: Return None if there are no return statements.
        if trace and self.returns:
            g.trace('name: %s r:\n%s' % (name, r))
        if not [z for z in self.returns if z.value != None]:
            return 'None: ...'
        # Step 2: [Def Name Patterns] override all other patterns.
        for pattern in self.def_patterns:
            found, s = pattern.match(name)
            if found:
                if trace:
                    g.trace('*name pattern %s: %s -> %s' % (
                        pattern.find_s, name, s))
                return s + ': ...'
        # Step 3: remove recursive calls.
        raw, r = self.remove_recursive_calls(name, raw, r)
        # Step 4: Calculate return types.
        return self.format_return_expressions(name, raw, r)

    def format_return_expressions(self, name, raw_returns, reduced_returns):
        '''
        aList is a list of maximally reduced return expressions.
        For each expression e in Alist:
        - If e is a single known type, add e to the result.
        - Otherwise, add Any # e to the result.
        Return the properly indented result.
        '''
        assert len(raw_returns) == len(reduced_returns)
        lws =  '\n' + ' '*4
        n = len(raw_returns)
        known = all([is_known_type(e) for e in reduced_returns])
        # g.trace(reduced_returns)
        if not known or self.verbose:
            # First, generate the return lines.
            aList = []
            for i in range(n):
                e, raw = reduced_returns[i], raw_returns[i]
                known = ' ' if is_known_type(e) else '?'
                aList.append('# %s %s: %s' % (' ', i, raw))
                aList.append('# %s %s: return %s' % (known, i, e))
            results = ''.join([lws + self.indent(z) for z in aList])
            # Put the return lines in their proper places.
            if known:
                s = reduce_types(reduced_returns,
                                 name=name,
                                 trace=self.trace_reduce)
                return s + ': ...' + results
            else:
                return 'Any: ...' + results
        else:
            s = reduce_types(reduced_returns,
                             name=name,
                             trace=self.trace_reduce) 
            return s + ': ...'

    def get_def_name(self, node):
        '''Return the representaion of a function or method name.'''
        if self.class_name_stack:
            name = '%s.%s' % (self.class_name_stack[-1], node.name)
            # All ctors should return None
            if node.name == '__init__':
                name = 'None'
        else:
            name = node.name
        return name

    def remove_recursive_calls(self, name, raw, reduced):
        '''Remove any recursive calls to name from both lists.'''
        # At present, this works *only* if the return is nothing but the recursive call.
        trace = False
        assert len(raw) == len(reduced)
        pattern = Pattern('%s(*)' % name)
        n = len(reduced)
        raw_result, reduced_result = [], []
        for i in range(n):
            if pattern.match_entire_string(reduced[i]):
                if trace:
                    g.trace('****', name, pattern, reduced[i])
            else:
                raw_result.append(raw[i])
                reduced_result.append(reduced[i])
        return raw_result, reduced_result

    def visit_Return(self, node):

        self.returns.append(node)
            # New: return the entire node, not node.value.


class TestClass:
    '''
    A class containing constructs that have caused difficulties.
    This is in the make_stub_files directory, not the test directory.
    '''
    # pylint: disable=no-member
    # pylint: disable=undefined-variable
    # pylint: disable=no-self-argument
    # pylint: disable=no-method-argument
    # pylint: disable=unsubscriptable-object

    def parse_group(group):
        if len(group) >= 3 and group[-2] == 'as':
            del group[-2:]
        ndots = 0
        i = 0
        while len(group) > i and group[i].startswith('.'):
            ndots += len(group[i])
            i += 1
        assert ''.join(group[:i]) == '.'*ndots, group
        del group[:i]
        assert all(g == '.' for g in group[1::2]), group
        return ndots, os.sep.join(group[::2])

    def return_all(self):
        return all([is_known_type(z) for z in s3.split(',')])
        # return all(['abc'])

    def return_array():
        return f(s[1:-1])

    def return_list(self, a):
        return [a]

    def return_two_lists(s):
        if 1:
            return aList
        else:
            return list(self.regex.finditer(s))
g = LeoGlobals() # For ekr.
if __name__ == "__main__":
    main()

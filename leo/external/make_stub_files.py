#@+leo-ver=5-thin
#@+node:ekr.20160317054700.1: * @file ../external/make_stub_files.py
#!/usr/bin/env python
'''
This script makes a stub (.pyi) file in the output directory for each
source file listed on the command line (wildcard file names are supported).

For full details, see README.md.

This file is in the public domain.

Written by Edward K. Ream.
'''
#@+<< imports >>
#@+node:ekr.20160317054700.2: **  << imports >> (make_stub_files.py)
import ast
from collections import OrderedDict
import configparser
import glob
import io
import optparse
import os
import re
import sys
import time
import types
#@-<< imports >>
isPython3 = sys.version_info >= (3, 0, 0)
# pylint: disable=no-else-return
#@+others
#@+node:ekr.20160317054700.3: **   type functions
#@+node:ekr.20160317054700.4: *3* is_known_type
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
#@+node:ekr.20160317054700.5: *3* merge_types (not used)
#@+node:ekr.20160317054700.6: *3* reduce_types
#@+node:ekr.20160523111223.1: **   unit_test (make_stub_files.py)
def unit_test(raise_on_fail=True):
    '''Run basic unit tests for this file.'''
    import _ast
    from leo.core import leoAst
    # Compute all fields to test.
    aList = sorted(dir(_ast))
    remove = [
        'Interactive', 'Suite',  # Not necessary.
        'AST',  # The base class,
        # Constants...
        'PyCF_ALLOW_TOP_LEVEL_AWAIT',
        'PyCF_ONLY_AST',
        'PyCF_TYPE_COMMENTS',
        # New ast nodes for Python 3.8.
        # We can ignore these nodes because ast.parse does not generate them.
        # (The new kwarg, type_comments, is False by default!)
        'FunctionType', 'NamedExpr', 'TypeIgnore',
    ]
    aList = [z for z in aList if not z[0].islower()]
        # Remove base classe
    aList = [z for z in aList if not z.startswith('_') and not z in remove]
    # Now test them.
    table = (
        # AstFullTraverser,
        AstArgFormatter,
        AstFormatter,
    )
    for class_ in table:
        traverser = class_()
        errors, nodes, ops = 0, 0, 0
        for z in aList:
            if hasattr(traverser, 'do_' + z):
                nodes += 1
            elif leoAst._op_names.get(z):
                ops += 1
            else:
                errors += 1
                print('Missing %s visitor for: %s' % (
                    traverser.__class__.__name__, z))
    s = '%s node types, %s op types, %s errors' % (nodes, ops, errors)
    if raise_on_fail:
        assert not errors, s
    else:
        print(s)
#@+node:ekr.20160317054700.7: **   utility functions
#@+node:ekr.20160317054700.8: *3* dump
#@+node:ekr.20160317054700.9: *3* dump_dict
#@+node:ekr.20160317054700.10: *3* dump_list
#@+node:ekr.20160317054700.11: *3* main
#@+node:ekr.20160317054700.13: *3* truncate
def truncate(s, n):
    '''Return s truncated to n characters.'''
    return s if len(s) <= n else s[: n - 3] + '...'
#@+node:ekr.20160317055215.1: **  class AstFormatter
class AstFormatter:
    '''
    A class to recreate source code from an AST.

    This does not have to be perfect, but it should be close.
    '''
    # pylint: disable=consider-using-enumerate
    #@+others
    #@+node:ekr.20160317055215.2: *3*  f.Entries

    # Entries...
    #@+node:ekr.20160317055215.3: *4* f.__call__ (not used)
    #@+node:ekr.20160317055215.4: *4* f.format (make_stub_files)
    def format(self, node):
        '''Format the node (or list of nodes) and its descendants.'''
        self.level = 0
        val = self.visit(node)
        # pylint: disable=consider-using-ternary
        return val and val.strip() or ''
    #@+node:ekr.20160317055215.5: *4* f.visit
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
            assert g.isString(s), type(s)
            return s
    #@+node:ekr.20160317055215.6: *3* f.Contexts

    # Contexts...
    #@+node:ekr.20160317055215.7: *4* f.ClassDef (make_stub_files)

    # 2: ClassDef(identifier name, expr* bases,
    #             stmt* body, expr* decorator_list)
    # 3: ClassDef(identifier name, expr* bases,
    #             keyword* keywords, expr? starargs, expr? kwargs
    #             stmt* body, expr* decorator_list)
    #
    # keyword arguments supplied to call (NULL identifier for **kwargs)
    # keyword = (identifier? arg, expr value)

    def do_ClassDef(self, node):
        result = []
        name = node.name  # Only a plain string is valid.
        bases = [self.visit(z) for z in node.bases] if node.bases else []
        if getattr(node, 'keywords', None):  # Python 3
            for keyword in node.keywords:
                bases.append('%s=%s' % (keyword.arg, self.visit(keyword.value)))
        if getattr(node, 'starargs', None):  # Python 3
            bases.append('*%s', self.visit(node.starargs))
        if getattr(node, 'kwargs', None):  # Python 3
            bases.append('*%s', self.visit(node.kwargs))
        if bases:
            result.append(self.indent('class %s(%s):\n' % (name, ','.join(bases))))
        else:
            result.append(self.indent('class %s:\n' % name))
        for z in node.body:
            self.level += 1
            result.append(self.visit(z))
            self.level -= 1
        return ''.join(result)
    #@+node:ekr.20160317055215.8: *4* f.FunctionDef & AsyncFunctionDef (make_stub_files)

    # 2: FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list)
    # 3: FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list,
    #                expr? returns)

    def do_FunctionDef(self, node, async_flag=False):
        '''Format a FunctionDef node.'''
        result = []
        if node.decorator_list:
            for z in node.decorator_list:
                result.append('@%s\n' % self.visit(z))
        name = node.name  # Only a plain string is valid.
        args = self.visit(node.args) if node.args else ''
        asynch_prefix = 'asynch ' if async_flag else ''
        if getattr(node, 'returns', None):  # Python 3.
            returns = self.visit(node.returns)
            result.append(self.indent('%sdef %s(%s): -> %s\n' % (
                asynch_prefix, name, args, returns)))
        else:
            result.append(self.indent('%sdef %s(%s):\n' % (
                asynch_prefix, name, args)))
        for z in node.body:
            self.level += 1
            result.append(self.visit(z))
            self.level -= 1
        return ''.join(result)

    def do_AsyncFunctionDef(self, node):
        return self.do_FunctionDef(node, async_flag=True)
    #@+node:ekr.20160317055215.9: *4* f.Interactive
    def do_Interactive(self, node):
        for z in node.body:
            self.visit(z)
    #@+node:ekr.20160317055215.10: *4* f.Module
    def do_Module(self, node):
        assert 'body' in node._fields
        result = ''.join([self.visit(z) for z in node.body])
        return result  # 'module:\n%s' % (result)
    #@+node:ekr.20160317055215.11: *4* f.Lambda
    def do_Lambda(self, node):
        return self.indent('lambda %s: %s' % (
            self.visit(node.args),
            self.visit(node.body)))
    #@+node:ekr.20160317055215.12: *3* f.Expressions

    # Expressions...

    #@+node:ekr.20160317055215.13: *4* f.Expr
    def do_Expr(self, node):
        '''An outer expression: must be indented.'''
        return self.indent('%s\n' % self.visit(node.value))
    #@+node:ekr.20160317055215.14: *4* f.Expression
    def do_Expression(self, node):
        '''An inner expression: do not indent.'''
        return '%s\n' % self.visit(node.body)
    #@+node:ekr.20160317055215.15: *4* f.GeneratorExp
    def do_GeneratorExp(self, node):
        elt = self.visit(node.elt) or ''
        gens = [self.visit(z) for z in node.generators]
        gens = [z if z else '<**None**>' for z in gens]  # Kludge: probable bug.
        return '<gen %s for %s>' % (elt, ','.join(gens))
    #@+node:ekr.20160317055215.16: *4* f.ctx nodes
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
    #@+node:ekr.20160317055215.17: *3* f.Operands

    # Operands...

    #@+node:ekr.20160317055215.18: *4* f.arguments (make_stub_files)
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
            args = [self.visit(z) for z in node.kwonlyargs]
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
    #@+node:ekr.20160317055215.19: *4* f.arg (Python3 only) (make_stub_files)

    # 3: arg = (identifier arg, expr? annotation)

    def do_arg(self, node):
        if getattr(node, 'annotation', None):
            return '%s: %s' % (node.arg, self.visit(node.annotation))
        else:
            return node.arg
    #@+node:ekr.20160317055215.20: *4* f.Attribute
    # Attribute(expr value, identifier attr, expr_context ctx)

    def do_Attribute(self, node):
        return '%s.%s' % (
            self.visit(node.value),
            node.attr)  # Don't visit node.attr: it is always a string.
    #@+node:ekr.20160317055215.21: *4* f.Bytes
    def do_Bytes(self, node):  # Python 3.x only.
        return str(node.s)
    #@+node:ekr.20160317055215.22: *4* f.Call & f.keyword
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
        args = [z for z in args if z]  # Kludge: Defensive coding.
        return '%s(%s)' % (func, ','.join(args))
    #@+node:ekr.20160317055215.23: *5* f.keyword
    # keyword = (identifier arg, expr value)

    def do_keyword(self, node):
        # node.arg is a string.
        value = self.visit(node.value)
        # This is a keyword *arg*, not a Python keyword!
        return '%s=%s' % (node.arg, value)

    #@+node:ekr.20170721092717.1: *4* f.Constant (Python 3.6+)
    def do_Constant(self, node):  # Python 3.6+ only.
        assert isPython3
        return str(node.s)  # A guess.
    #@+node:ekr.20160317055215.24: *4* f.comprehension
    def do_comprehension(self, node):
        result = []
        name = self.visit(node.target)  # A name.
        it = self.visit(node.iter)  # An attribute.
        result.append('%s in %s' % (name, it))
        ifs = [self.visit(z) for z in node.ifs]
        if ifs:
            result.append(' if %s' % (''.join(ifs)))
        return ''.join(result)

    #@+node:ekr.20160317055215.25: *4* f.Dict
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

    #@+node:ekr.20160317055215.26: *4* f.Ellipsis
    def do_Ellipsis(self, node):
        return '...'

    #@+node:ekr.20160317055215.27: *4* f.ExtSlice
    def do_ExtSlice(self, node):
        return ':'.join([self.visit(z) for z in node.dims])

    #@+node:ekr.20170721093043.1: *4* f.FormattedValue (Python 3.6+)
    # FormattedValue(expr value, int? conversion, expr? format_spec)

    def do_FormattedValue(self, node):  # Python 3.6+ only.
        assert isPython3
        return '%s%s%s' % (
            self.visit(node.value),
            self.visit(node.conversion) if node.conversion else '',
            self.visit(node.format_spec) if node.format_spec else '')
    #@+node:ekr.20160317055215.28: *4* f.Index
    def do_Index(self, node):
        return self.visit(node.value)

    #@+node:ekr.20170721093148.1: *4* f.JoinedStr (Python 3.6+)
    # JoinedStr(expr* values)

    def do_JoinedStr(self, node):

        if node.values:
            for value in node.values:
                self.visit(value)

    #@+node:ekr.20160317055215.29: *4* f.List
    def do_List(self, node):
        # Not used: list context.
        # self.visit(node.ctx)
        elts = [self.visit(z) for z in node.elts]
        elts = [z for z in elts if z]  # Defensive.
        return '[%s]' % ','.join(elts)

    #@+node:ekr.20160317055215.30: *4* f.ListComp
    def do_ListComp(self, node):
        elt = self.visit(node.elt)
        gens = [self.visit(z) for z in node.generators]
        gens = [z if z else '<**None**>' for z in gens]  # Kludge: probable bug.
        return '%s for %s' % (elt, ''.join(gens))

    #@+node:ekr.20160317055215.31: *4* f.Name
    def do_Name(self, node):
        return node.id

    def do_NameConstant(self, node):  # Python 3 only.
        s = repr(node.value)
        return 'bool' if s in ('True', 'False') else s

    #@+node:ekr.20160317055215.32: *4* f.Num
    def do_Num(self, node):
        return repr(node.n)

    #@+node:ekr.20160317055215.34: *4* f.Slice
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

    #@+node:ekr.20160317055215.35: *4* f.Str
    def do_Str(self, node):
        '''This represents a string constant.'''
        return repr(node.s)

    #@+node:ekr.20160317055215.36: *4* f.Subscript
    # Subscript(expr value, slice slice, expr_context ctx)

    def do_Subscript(self, node):
        value = self.visit(node.value)
        the_slice = self.visit(node.slice)
        return '%s[%s]' % (value, the_slice)

    #@+node:ekr.20160317055215.37: *4* f.Tuple
    def do_Tuple(self, node):
        elts = [self.visit(z) for z in node.elts]
        return '(%s)' % ', '.join(elts)
    #@+node:ekr.20160523135038.2: *4* f.DictComp (new)
    # DictComp(expr key, expr value, comprehension* generators)

    def do_DictComp(self, node):
        # EKR: visit generators first, then value.
        for z in node.generators:
            self.visit(z)
        self.visit(node.value)
        self.visit(node.key)
    #@+node:ekr.20160523135038.3: *4* f.Set (new)
    # Set(expr* elts)

    def do_Set(self, node):
        for z in node.elts:
            self.visit(z)

    #@+node:ekr.20160523135038.4: *4* f.SetComp (new)
    # SetComp(expr elt, comprehension* generators)

    def do_SetComp(self, node):
        # EKR: visit generators first.
        for z in node.generators:
            self.visit(z)
        self.visit(node.elt)
    #@+node:ekr.20160317055215.38: *3* f.Operators

    # Operators...

    #@+node:ekr.20160317055215.39: *4* f.BinOp
    def do_BinOp(self, node):
        return '%s%s%s' % (
            self.visit(node.left),
            self.op_name(node.op),
            self.visit(node.right))

    #@+node:ekr.20160317055215.40: *4* f.BoolOp
    def do_BoolOp(self, node):
        op_name = self.op_name(node.op)
        values = [self.visit(z) for z in node.values]
        return op_name.join(values)

    #@+node:ekr.20160317055215.41: *4* f.Compare
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

    #@+node:ekr.20160317055215.42: *4* f.UnaryOp
    def do_UnaryOp(self, node):
        return '%s%s' % (
            self.op_name(node.op),
            self.visit(node.operand))

    #@+node:ekr.20160317055215.43: *4* f.ifExp (ternary operator)
    def do_IfExp(self, node):
        return '%s if %s else %s ' % (
            self.visit(node.body),
            self.visit(node.test),
            self.visit(node.orelse))
    #@+node:ekr.20160317055215.44: *3* f.Statements

    # Statements...

    #@+node:ekr.20170721093003.1: *4* f.AnnAssign
    # AnnAssign(expr target, expr annotation, expr? value, int simple)

    def do_AnnAssign(self, node):
        return self.indent('%s:%s=%s\n' % (
            self.visit(node.target),
            self.visit(node.annotation),
            self.visit(node.value),
        ))
    #@+node:ekr.20160317055215.45: *4* f.Assert
    def do_Assert(self, node):
        test = self.visit(node.test)
        if getattr(node, 'msg', None):
            message = self.visit(node.msg)
            return self.indent('assert %s, %s' % (test, message))
        else:
            return self.indent('assert %s' % test)

    #@+node:ekr.20160317055215.46: *4* f.Assign
    def do_Assign(self, node):
        return self.indent('%s=%s\n' % (
            '='.join([self.visit(z) for z in node.targets]),
            self.visit(node.value)))

    #@+node:ekr.20160317055215.47: *4* f.AugAssign
    def do_AugAssign(self, node):
        return self.indent('%s%s=%s\n' % (
            self.visit(node.target),
            self.op_name(node.op),  # Bug fix: 2013/03/08.
            self.visit(node.value)))

    #@+node:ekr.20160523135457.1: *4* f.Await
    # Await(expr value)

    def do_Await(self, node):

        return self.indent('await %s\n' % (
            self.visit(node.value)))
    #@+node:ekr.20160317055215.48: *4* f.Break
    def do_Break(self, node):
        return self.indent('break\n')

    #@+node:ekr.20160317055215.49: *4* f.Continue
    def do_Continue(self, node):
        return self.indent('continue\n')

    #@+node:ekr.20160317055215.50: *4* f.Delete
    def do_Delete(self, node):
        targets = [self.visit(z) for z in node.targets]
        return self.indent('del %s\n' % ','.join(targets))

    #@+node:ekr.20160317055215.51: *4* f.ExceptHandler
    def do_ExceptHandler(self, node):
        result = []
        result.append(self.indent('except'))
        if getattr(node, 'type', None):
            result.append(' %s' % self.visit(node.type))
        if getattr(node, 'name', None):
            if isinstance(node.name, ast.AST):
                result.append(' as %s' % self.visit(node.name))
            else:
                result.append(' as %s' % node.name)  # Python 3.x.
        result.append(':\n')
        for z in node.body:
            self.level += 1
            result.append(self.visit(z))
            self.level -= 1
        return ''.join(result)

    #@+node:ekr.20160317055215.52: *4* f.Exec
    # Python 2.x only

    def do_Exec(self, node):
        body = self.visit(node.body)
        args = []  # Globals before locals.
        if getattr(node, 'globals', None):
            args.append(self.visit(node.globals))
        if getattr(node, 'locals', None):
            args.append(self.visit(node.locals))
        if args:
            return self.indent('exec %s in %s\n' % (
                body, ','.join(args)))
        else:
            return self.indent('exec %s\n' % (body))

    #@+node:ekr.20160317055215.53: *4* f.For & AsyncFor
    def do_For(self, node, async_flag=False):
        result = []
        result.append(self.indent('%sfor %s in %s:\n' % (
            'asynch ' if async_flag else '',
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

    #@+node:ekr.20160317055215.54: *4* f.Global
    def do_Global(self, node):
        return self.indent('global %s\n' % (
            ','.join(node.names)))

    #@+node:ekr.20160317055215.55: *4* f.If
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

    #@+node:ekr.20160317055215.56: *4* f.Import & helper
    def do_Import(self, node):
        names = []
        for fn, asname in self.get_import_names(node):
            if asname:
                names.append('%s as %s' % (fn, asname))
            else:
                names.append(fn)
        return self.indent('import %s\n' % (
            ','.join(names)))

    #@+node:ekr.20160317055215.57: *5* f.get_import_names
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

    #@+node:ekr.20160317055215.58: *4* f.ImportFrom
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
    #@+node:ekr.20160317055215.59: *4* f.Nonlocal (Python 3)

    # Nonlocal(identifier* names)

    def do_Nonlocal(self, node):

        return self.indent('nonlocal %s\n' % ', '.join(node.names))

    #@+node:ekr.20160317055215.60: *4* f.Pass
    def do_Pass(self, node):
        return self.indent('pass\n')

    #@+node:ekr.20160317055215.61: *4* f.Print
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

    #@+node:ekr.20160317055215.62: *4* f.Raise
    # Raise(expr? type, expr? inst, expr? tback)    Python 2
    # Raise(expr? exc, expr? cause)                 Python 3

    def do_Raise(self, node):
        args = []
        attrs = ('exc', 'cause') if isPython3 else ('type', 'inst', 'tback')
        for attr in attrs:
            if getattr(node, attr, None) is not None:
                args.append(self.visit(getattr(node, attr)))
        if args:
            return self.indent('raise %s\n' % (
                ','.join(args)))
        else:
            return self.indent('raise\n')

    #@+node:ekr.20160317055215.63: *4* f.Return
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
    #@+node:ekr.20160317055215.64: *4* f.Starred (Python 3)

    #@+node:ekr.20160317055215.65: *4* f.Suite
    #@+node:ekr.20160317055215.66: *4* f.Try (Python 3)
    #@+node:ekr.20160317055215.67: *4* f.TryExcept
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

    #@+node:ekr.20160317055215.68: *4* f.TryFinally
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

    #@+node:ekr.20160317055215.69: *4* f.While
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

    #@+node:ekr.20160317055215.70: *4* f.With & AsyncWith (make_stub_files)

    # 2:  With(expr context_expr, expr? optional_vars,
    #          stmt* body)
    # 3:  With(withitem* items,
    #          stmt* body)
    # withitem = (expr context_expr, expr? optional_vars)

    def do_With(self, node, async_flag=False):
        result = []
        result.append(self.indent('%swith ' % 'async ' if async_flag else ''))
        vars_list = []
        if getattr(node, 'context_expression', None):
            result.append(self.visit(node.context_expresssion))
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
    #@+node:ekr.20160317055215.71: *4* f.Yield
    def do_Yield(self, node):
        if getattr(node, 'value', None):
            return self.indent('yield %s\n' % (
                self.visit(node.value)))
        else:
            return self.indent('yield\n')
    #@+node:ekr.20160317055215.72: *4* f.YieldFrom (Python 3)
    # YieldFrom(expr value)

    def do_YieldFrom(self, node):

        return self.indent('yield from %s\n' % (
            self.visit(node.value)))
    #@+node:ekr.20160317055215.73: *3* f.Utils

    # Utils...

    #@+node:ekr.20160317055215.74: *4* f.kind
    def kind(self, node):
        '''Return the name of node's class.'''
        return node.__class__.__name__

    #@+node:ekr.20160317055215.75: *4* f.indent
    def indent(self, s):
        return '%s%s' % (' ' * 4 * self.level, s)
    #@+node:ekr.20160317055215.76: *4* f.op_name
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
#@+node:ekr.20160317054700.84: ** class AstArgFormatter (AstFormatter)
class AstArgFormatter(AstFormatter):
    '''
    Just like the AstFormatter class, except it prints the class
    names of constants instead of actual values.
    '''
    #@+others
    #@+node:ekr.20160317054700.85: *3* sf.Constants & Name

    # Return generic markers to allow better pattern matches.

    def do_BoolOp(self, node):  # Python 2.x only.
        return 'bool'

    def do_Bytes(self, node):  # Python 3.x only.
        return 'bytes'

    def do_Constant(self, node):
        # Python 3.x only.
        return 'constant'

    def do_Name(self, node):
        return 'bool' if node.id in ('True', 'False') else node.id

    def do_Num(self, node):
        return 'number'  # return repr(node.n)

    def do_Str(self, node):
        '''This represents a string constant.'''
        return 'str'  # return repr(node.s)
    #@-others
#@+node:ekr.20160317054700.86: ** class LeoGlobals
class LeoGlobals:
    '''A class supporting g.trace for compatibility with Leo.'''
    #@+others
    #@+node:ekr.20160317054700.87: *3* class NullObject (Python Cookbook)
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
    #@+node:ekr.20160317054700.88: *3* g._callerName
    def _callerName(self, n=1, files=False):
        # print('_callerName: %s %s' % (n,files))
        try:  # get the function name from the call stack.
            f1 = sys._getframe(n)  # The stack frame, n levels up.
            code1 = f1.f_code  # The code object
            name = code1.co_name
            if name == '__init__':
                name = '__init__(%s,line %s)' % (
                    self.shortFileName(code1.co_filename), code1.co_firstlineno)
            if files:
                return '%s:%s' % (self.shortFileName(code1.co_filename), name)
            else:
                return name  # The code name
        except ValueError:
            # print('g._callerName: ValueError',n)
            return ''  # The stack is not deep enough.
        except Exception:
            # es_exception()
            return ''  # "<no caller name>"
    #@+node:ekr.20160317054700.89: *3* g.callers
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
        if count > 0: result = result[:count]
        sep = '\n' if files else ','
        return sep.join(result)
    #@+node:ekr.20160317054700.90: *3* g.cls
    def cls(self):
        '''Clear the screen.'''
        if sys.platform.lower().startswith('win'):
            os.system('cls')
    #@+node:ekr.20160318093308.1: *3* g.isString & isUnicode (make_stub_files.py)
    def isString(self, s):
        '''Return True if s is any string, but not bytes.'''
        # pylint: disable=no-member
        if isPython3:
            return isinstance(s, str)
        else:
            return isinstance(s, types.StringTypes)

    def isUnicode(self, s):
        '''Return True if s is a unicode string.'''
        # pylint: disable=no-member
        if isPython3:
            return isinstance(s, str)
        else:
            return isinstance(s, types.UnicodeType)
    #@+node:ekr.20160317054700.92: *3* g.shortFileName
    def shortFileName(self, fileName, n=None):
        # pylint: disable=invalid-unary-operand-type
        if n is None or n < 1:
            return os.path.basename(fileName)
        else:
            return '/'.join(fileName.replace('\\', '/').split('/')[-n :])
    #@+node:ekr.20160317054700.93: *3* g.splitLines
    def splitLines(self, s):
        '''Split s into lines, preserving trailing newlines.'''
        return s.splitlines(True) if s else []
    #@+node:ekr.20160317054700.94: *3* g.trace
    def trace(self, *args, **keys):
        try:
            from leo.core import leoGlobals as leo_g
            leo_g.trace(caller_level=2, *args, **keys)
        except ImportError:
            print(args, keys)
    #@-others
#@+node:ekr.20160317054700.95: ** class Pattern
class Pattern:
    '''
    A class representing regex or balanced patterns.

    Sample matching code, for either kind of pattern:

        for m in reversed(pattern.all_matches(s)):
            s = pattern.replace(m, s)
    '''
    #@+others
    #@+node:ekr.20160317054700.96: *3* pattern.ctor
    def __init__(self, find_s, repl_s=''):
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
                    result.append('\\' + ch)
            self.regex = re.compile(''.join(result))
    #@+node:ekr.20160317054700.97: *3* pattern.__eq__, __ne__, __hash__
    def __eq__(self, obj):
        """Return True if two Patterns are equivalent."""
        if isinstance(obj, Pattern):
            return self.find_s == obj.find_s and self.repl_s == obj.repl_s
        else:
            return NotImplementedError

    def __ne__(self, obj):
        """Return True if two Patterns are not equivalent."""
        return not self.__eq__(obj)

    def __hash__(self):
        '''Pattern.__hash__'''
        return len(self.find_s) + len(self.repl_s)
    #@+node:ekr.20160317054700.98: *3* pattern.str & repr
    def __repr__(self):
        '''Pattern.__repr__'''
        return '%s: %s' % (self.find_s, self.repl_s)

    __str__ = __repr__
    #@+node:ekr.20160317054700.99: *3* pattern.is_balanced
    def is_balanced(self):
        '''Return True if self.find_s is a balanced pattern.'''
        s = self.find_s
        if s.endswith('*'):
            return True
        for pattern in ('(*)', '[*]', '{*}'):
            if s.find(pattern) > -1:
                return True
        return False
    #@+node:ekr.20160317054700.100: *3* pattern.is_regex
    def is_regex(self):
        '''
        Return True if self.find_s is a regular pattern.
        For now a kludgy convention suffices.
        '''
        return self.find_s.endswith('$')
            # A dollar sign is not valid in any Python expression.
    #@+node:ekr.20160317054700.101: *3* pattern.all_matches & helpers
    def all_matches(self, s):
        '''
        Return a list of match objects for all matches in s.
        These are regex match objects or (start, end) for balanced searches.
        '''
        if self.is_balanced():
            aList, i = [], 0
            while i < len(s):
                progress = i
                j = self.full_balanced_match(s, i)
                if j is None:
                    i += 1
                else:
                    aList.append((i, j),)
                    i = j
                assert progress < i
            return aList
        else:
            return list(self.regex.finditer(s))
    #@+node:ekr.20160317054700.102: *4* pattern.full_balanced_match
    def full_balanced_match(self, s, i):
        '''Return the index of the end of the match found at s[i:] or None.'''
        pattern = self.find_s
        j = 0  # index into pattern
        while i < len(s) and j < len(pattern) and pattern[j] in ('*', s[i]):
            progress = i
            if pattern[j : j + 3] in ('(*)', '[*]', '{*}'):
                delim = pattern[j]
                i = self.match_balanced(delim, s, i)
                j += 3
            elif j == len(pattern) - 1 and pattern[j] == '*':
                # A trailing * matches the rest of the string.
                j += 1
                i = len(s)
                break
            else:
                i += 1
                j += 1
            assert progress < i
        found = i <= len(s) and j == len(pattern)
        return i if found else None
    #@+node:ekr.20160317054700.103: *4* pattern.match_balanced
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
    #@+node:ekr.20160317054700.104: *3* pattern.match (trace-matches)
    def match(self, s, trace=False):
        '''
        Perform the match on the entire string if possible.
        Return (found, new s)
        '''
        trace = False or trace
        caller = g.callers(2).split(',')[0].strip()  # The caller of match_all.
        s1 = truncate(s, 40)
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
    #@+node:ekr.20160317054700.105: *3* pattern.match_entire_string
    def match_entire_string(self, s):
        '''Return True if s matches self.find_s'''
        if self.is_balanced():
            j = self.full_balanced_match(s, 0)
            return j == len(s)
        else:
            m = self.regex.match(s)
            return m and m.group(0) == s
    #@+node:ekr.20160317054700.106: *3* pattern.replace & helpers
    def replace(self, m, s):
        '''Perform any kind of replacement.'''
        if self.is_balanced():
            start, end = m
            return self.replace_balanced(s, start, end)
        else:
            return self.replace_regex(m, s)
    #@+node:ekr.20160317054700.107: *4* pattern.replace_balanced
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
        assert i > -1  # i is an index into f AND s
        delim = f[i]
        if trace: g.trace('head', s[:i], f[:i])
        assert s[:i] == f[:i], (s[:i], f[:i])
        if trace: g.trace('delim', delim)
        k = self.match_balanced(delim, s, i)
        s_star = s[i + 1 : k - 1]
        if trace: g.trace('s_star', s_star)
        repl = r[:j] + s_star + r[j + 1 :]
        if trace: g.trace('repl', self.repl_s, '==>', repl)
        return s1[:start] + repl + s1[end:]
    #@+node:ekr.20160317054700.108: *4* pattern.replace_regex
    def replace_regex(self, m, s):
        '''Do the replacement in s specified by m.'''
        s = self.repl_s
        for i in range(9):
            group = '\\%s' % i
            if s.find(group) > -1:
                s = s.replace(group, m.group(i))
        return s
    #@-others
#@+node:ekr.20160519071605.1: ** class ReduceTypes
class ReduceTypes:
    '''
    A helper class for the top-level reduce_types function.

    This class reduces a list of type hints to a string containing the
    reduction of all types in the list.
    '''
    #@+others
    #@+node:ekr.20160519071605.2: *3* __init__
    def __init__(self, aList=None, name=None, trace=False):
        '''Ctor for ReduceTypes class.'''
        self.aList = aList
        self.name = name
        self.optional = False
        self.trace = trace

    #@+node:ekr.20160519071605.3: *3* is_known_type
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
            '', 'None',  # Tricky.
            'complex', 'float', 'int', 'long', 'number',
            'dict', 'list', 'tuple',
            'bool', 'bytes', 'str', 'unicode',
        )
        for s2 in table:
            if s2 == s:
                return True
            elif Pattern(s2 + '(*)', s).match_entire_string(s):
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
                pattern = Pattern(s2 + '[*]', s)
                if pattern.match_entire_string(s):
                    return True
        if trace: g.trace('Fail:', s1)
        return False

    #@+node:ekr.20160519071605.4: *3* reduce_collection
    def reduce_collection(self, aList, kind):
        '''
        Reduce the inner parts of a collection for the given kind.
        Return a list with only collections of the given kind reduced.
        '''
        assert isinstance(aList, list)
        assert None not in aList, aList
        pattern = Pattern('%s[*]' % kind)
        others, r1, r2 = [], [], []
        for s in sorted(set(aList)):
            if pattern.match_entire_string(s):
                r1.append(s)
            else:
                others.append(s)
        for s in sorted(set(r1)):
            parts = []
            s2 = s[len(kind) + 1 : -1]
            for s3 in s2.split(','):
                s3 = s3.strip()
                parts.append(s3 if self.is_known_type(s3) else 'Any')
            r2.append('%s[%s]' % (kind, ', '.join(parts)))
        result = others
        result.extend(r2)
        result = sorted(set(result))
        return result

    #@+node:ekr.20160519071605.5: *3* reduce_numbers
    def reduce_numbers(self, aList):
        '''
        Return aList with all number types in aList replaced by the most
        general numeric type in aList.
        '''
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
        return aList

    #@+node:ekr.20160519071605.6: *3* reduce_types
    def reduce_types(self):
        '''
        self.aList consists of arbitrarily many types because this method is
        called from format_return_expressions.

        Return a *string* containing the reduction of all types in this list.
        Returning a string means that all traversers always return strings,
        never lists.
        '''
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

    #@+node:ekr.20160519071605.7: *3* reduce_unknowns
    def reduce_unknowns(self, aList):
        '''Replace all unknown types in aList with Any.'''
        return [z if self.is_known_type(z) else 'Any' for z in aList]

    #@+node:ekr.20160519071605.8: *3* show
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
            pattern = sorted(set([z.replace('\n', ' ') for z in aList]))
            pattern = '[%s]' % truncate(', '.join(pattern), 53 - 2)
            print('reduce_types: %-26s %53s ==> %s%s' % (context, pattern, known, s))
                # widths above match the corresponding indents in match_all and match.
        return s

    #@+node:ekr.20160519071605.9: *3* split_types
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
                i1 = i + 1
        aList.append(s[i1:].strip())
        return aList
    #@-others
#@+node:ekr.20160317054700.118: ** class StandAloneMakeStubFile
class StandAloneMakeStubFile:
    '''
    A class to make Python stub (.pyi) files in the ~/stubs directory for
    every file mentioned in the [Source Files] section of
    ~/stubs/make_stub_files.cfg.
    '''
    #@+others
    #@+node:ekr.20160317054700.119: *3* msf.ctor
    def __init__(self):
        '''Ctor for StandAloneMakeStubFile class.'''
        self.options = {}
        # Ivars set on the command line...
        self.config_fn = None  # self.finalize('~/stubs/make_stub_files.cfg')
        self.enable_unit_tests = False
        self.files = []  # May also be set in the config file.
        # Ivars set in the config file...
        self.output_fn = None
        self.output_directory = self.finalize('.')  # self.finalize('~/stubs')
        self.overwrite = False
        self.prefix_lines = []
        self.trace_matches = False
        self.trace_patterns = False
        self.trace_reduce = False
        self.trace_visitors = False
        self.update_flag = False
        self.verbose = False  # Trace config arguments.
        self.warn = False
        # Pattern lists, set by config sections...
        self.section_names = ('Global', 'Def Name Patterns', 'General Patterns')
        self.def_patterns = []  # [Def Name Patterns]
        self.general_patterns = []  # [General Patterns]
        self.names_dict = {}
        self.op_name_dict = self.make_op_name_dict()
        self.patterns_dict = {}
        self.regex_patterns = []
    #@+node:ekr.20160317054700.120: *3* msf.finalize
    def finalize(self, fn):
        '''Finalize and regularize a filename.'''
        fn = os.path.expanduser(fn)
        fn = os.path.abspath(fn)
        fn = os.path.normpath(fn)
        return fn
    #@+node:ekr.20160317054700.121: *3* msf.make_stub_file
    def make_stub_file(self, fn):
        '''
        Make a stub file in ~/stubs for all source files mentioned in the
        [Source Files] section of ~/stubs/make_stub_files.cfg
        '''
        if not fn.endswith(('py', 'pyw')):
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
        node = ast.parse(s, filename=fn, mode='exec')
        StubTraverser(controller=self).run(node)
    #@+node:ekr.20160317054700.122: *3* msf.run
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
    #@+node:ekr.20160317054700.123: *3* msf.run_all_unit_tests
    def run_all_unit_tests(self):
        '''Run all unit tests in the make_stub_files/test directory.'''
        import unittest
        loader = unittest.TestLoader()
        suite = loader.discover(os.path.abspath('.'),
                                pattern='test*.py',
                                top_level_dir=None)
        unittest.TextTestRunner(verbosity=1).run(suite)
    #@+node:ekr.20160317054700.124: *3* msf.scan_command_line
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
        self.enable_unit_tests = options.test
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
    #@+node:ekr.20160317054700.125: *3* msf.scan_options & helpers
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
                self.output_directory = None  # inhibit run().
        if 'prefix_lines' in parser.options('Global'):
            prefix = parser.get('Global', 'prefix_lines')
            # The parser does not preserve leading whitespace.
            self.prefix_lines = prefix.split('\n')
            if trace:
                print('Prefix lines...\n')
                for z in self.prefix_lines:
                    print(z)
                print('')
        self.def_patterns = self.scan_patterns('Def Name Patterns')
        self.general_patterns = self.scan_patterns('General Patterns')
        self.make_patterns_dict()
    #@+node:ekr.20160317054700.126: *4* msf.make_op_name_dict
    def make_op_name_dict(self):
        '''
        Make a dict whose keys are operators ('+', '+=', etc),
        and whose values are lists of values of ast.Node.__class__.__name__.
        '''
        d = {
            '.': ['Attr',],
            '(*)': ['Call', 'Tuple',],
            '[*]': ['List', 'Subscript',],
            '{*}': ['???',],
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
    #@+node:ekr.20160317054700.127: *4* msf.create_parser
    def create_parser(self):
        '''Create a RawConfigParser and return it.'''
        parser = configparser.RawConfigParser(dict_type=OrderedDict)  # Requires Python 2.7
        parser.optionxform = str
        return parser
    #@+node:ekr.20160317054700.128: *4* msf.find_pattern_ops
    def find_pattern_ops(self, pattern):
        '''Return a list of operators in pattern.find_s.'''
        trace = False or self.trace_patterns
        if pattern.is_regex():
            # Add the pattern to the regex patterns list.
            self.regex_patterns.append(pattern)
            return []
        d = self.op_name_dict
        keys1, keys2, keys3, keys9 = [], [], [], []
        for op in d:
            aList = d.get(op)
            if op.replace(' ', '').isalnum():
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
                break  # Only one match allowed.
        if trace and ops: g.trace(s1, ops)
        return ops
    #@+node:ekr.20160317054700.129: *4* msf.get_config_string
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

    #@+node:ekr.20160317054700.130: *4* msf.init_parser
    def init_parser(self, s):
        '''Add double back-slashes to all patterns starting with '['.'''
        if not s: return
        aList = []
        for s in s.split('\n'):
            if self.is_section_name(s):
                aList.append(s)
            elif s.strip().startswith('['):
                aList.append(r'\\' + s[1:])
            else:
                aList.append(s)
        s = '\n'.join(aList) + '\n'
        file_object = io.StringIO(s)
        # pylint: disable=deprecated-method
        self.parser.readfp(file_object)
    #@+node:ekr.20160317054700.131: *4* msf.is_section_name
    def is_section_name(self, s):

        def munge(s):
            return s.strip().lower().replace(' ', '')

        s = s.strip()
        if s.startswith('[') and s.endswith(']'):
            s = munge(s[1:-1])
            for s2 in self.section_names:
                if s == munge(s2):
                    return True
        return False
    #@+node:ekr.20160317054700.132: *4* msf.make_patterns_dict
    def make_patterns_dict(self):
        '''Assign all patterns to the appropriate ast.Node.'''
        trace = self.trace_patterns
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
                    self.names_dict[name] = pattern.repl_s
        if trace:
            g.trace('names_dict...')
            for z in sorted(self.names_dict):
                print('  %s: %s' % (z, self.names_dict.get(z)))
        if trace:
            g.trace('patterns_dict...')
            for z in sorted(self.patterns_dict):
                aList = self.patterns_dict.get(z)
                print(z)
                for pattern in sorted(aList):
                    print('  ' + repr(pattern))
        # Note: retain self.general_patterns for use in argument lists.
    #@+node:ekr.20160317054700.133: *4* msf.scan_patterns
    def scan_patterns(self, section_name):
        '''Parse the config section into a list of patterns, preserving order.'''
        trace = self.trace_patterns
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
        return aList
    #@-others
#@+node:ekr.20160317054700.134: ** class Stub
class Stub:
    '''
    A class representing all the generated stub for a class or def.
    stub.full_name should represent the complete context of a def.
    '''
    #@+others
    #@+node:ekr.20160317054700.135: *3* stub.ctor
    def __init__(self, kind, name, parent=None, stack=None):
        '''Stub ctor. Equality depends only on full_name and kind.'''
        self.children = []
        self.full_name = '%s.%s' % ('.'.join(stack), name) if stack else name
        self.kind = kind
        self.name = name
        self.out_list = []
        self.parent = parent
        self.stack = stack  # StubTraverser.context_stack.
        if stack:
            assert stack[-1] == parent.name, (stack[-1], parent.name)
        if parent:
            assert isinstance(parent, Stub)
            parent.children.append(self)
    #@+node:ekr.20160317054700.136: *3* stub.__eq__ and __ne__
    def __eq__(self, obj):
        '''
        Stub.__eq__. Return whether two stubs refer to the same method.
        Do *not* test parent links. That would interfere with --update logic.
        '''
        if isinstance(obj, Stub):
            return self.full_name == obj.full_name and self.kind == obj.kind
        else:
            return NotImplementedError

    def __ne__(self, obj):
        """Stub.__ne__"""
        return not self.__eq__(obj)
    #@+node:ekr.20160317054700.137: *3* stub.__hash__
    def __hash__(self):
        '''Stub.__hash__. Equality depends *only* on full_name and kind.'''
        return len(self.kind) + sum([ord(z) for z in self.full_name])
    #@+node:ekr.20160317054700.138: *3* stub.__repr__and __str__
    def __repr__(self):
        '''Stub.__repr__.'''
        return 'Stub: %s %s' % (id(self), self.full_name)

    def __str__(self):
        '''Stub.__repr__.'''
        return 'Stub: %s' % self.full_name
    #@+node:ekr.20160317054700.139: *3* stub.parents and level
    def level(self):
        '''Return the number of parents.'''
        return len(self.parents())

    def parents(self):
        '''Return a list of this stub's parents.'''
        return self.full_name.split('.')[:-1]
    #@-others
#@+node:ekr.20160317054700.140: ** class StubFormatter (AstFormatter)
class StubFormatter(AstFormatter):
    '''
    Formats an ast.Node and its descendants,
    making pattern substitutions in Name and operator nodes.
    '''
    #@+others
    #@+node:ekr.20160317054700.141: *3* sf.ctor
    def __init__(self, controller, traverser):
        '''Ctor for StubFormatter class.'''
        self.controller = x = controller
        self.traverser = traverser
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
    #@+node:ekr.20160317054700.142: *3* sf.match_all
    matched_d = {}

    def match_all(self, node, s, trace=False):
        '''Match all the patterns for the given node.'''
        trace = False or trace or self.trace_matches
        # verbose = True
        d = self.matched_d
        name = node.__class__.__name__
        s1 = truncate(s, 40)
        caller = g.callers(2).split(',')[1].strip()  # The direct caller of match_all.
        patterns = self.patterns_dict.get(name, []) + self.regex_patterns
        for pattern in patterns:
            found, s = pattern.match(s, trace=False)
            if found:
                if trace:
                    aList = d.get(name, [])
                    if pattern not in aList:
                        aList.append(pattern)
                        d[name] = aList
                        print('match_all:    %-12s %26s %40s ==> %s' % (caller, pattern, s1, s))
                break
        return s
    #@+node:ekr.20160317054700.143: *3* sf.visit
    def visit(self, node):
        '''StubFormatter.visit: supports --verbose tracing.'''
        s = AstFormatter.visit(self, node)
        return s
    #@+node:ekr.20160317054700.144: *3* sf.trace_visitor
    def trace_visitor(self, node, op, s):
        '''Trace node's visitor.'''
        if self.trace_visitors:
            caller = g.callers(2).split(',')[1]
            s1 = AstFormatter().format(node).strip()
            print('%12s op %-6s: %s ==> %s' % (caller, op.strip(), s1, s))
    #@+node:ekr.20160317054700.145: *3* sf.Operands

    # StubFormatter visitors for operands...
    #@+node:ekr.20160317054700.146: *4* sf.Attribute

    # Attribute(expr value, identifier attr, expr_context ctx)

    attrs_seen = []

    def do_Attribute(self, node):
        '''StubFormatter.do_Attribute.'''
        trace = False
        s = '%s.%s' % (
            self.visit(node.value),
            node.attr)  # Don't visit node.attr: it is always a string.
        s2 = self.names_dict.get(s)
        if trace and s2 and s2 not in self.attrs_seen:
            self.attrs_seen.append(s2)
            g.trace(s, '==>', s2)
        return s2 or s
    #@+node:ekr.20160317054700.147: *4* sf.Constants: Bytes, Num, Str

    # Return generic markers to allow better pattern matches.

    def do_Bytes(self, node):  # Python 3.x only.
        return 'bytes'  # return str(node.s)

    def do_Num(self, node):
        # make_patterns_dict treats 'number' as a special case.
        # return self.names_dict.get('number', 'number')
        return 'number'  # return repr(node.n)

    def do_Str(self, node):
        '''This represents a string constant.'''
        return 'str'  # return repr(node.s)
    #@+node:ekr.20160317054700.148: *4* sf.Dict
    def do_Dict(self, node):
        result = []
        keys = [self.visit(z) for z in node.keys]
        values = [self.visit(z) for z in node.values]
        if len(keys) == len(values):
            result.append('{')
            items = []
            # pylint: disable=consider-using-enumerate
            for i in range(len(keys)):
                items.append('%s:%s' % (keys[i], values[i]))
            result.append(', '.join(items))
            result.append('}')
        else:
            print('Error: f.Dict: len(keys) != len(values)\nkeys: %s\nvals: %s' % (
                repr(keys), repr(values)))
        # return ''.join(result)
        return 'Dict[%s]' % ''.join(result)
    #@+node:ekr.20160317054700.149: *4* sf.List
    def do_List(self, node):
        '''StubFormatter.List.'''
        elts = [self.visit(z) for z in node.elts]
        elts = [z for z in elts if z]  # Defensive.
        return 'list[%s]' % ', '.join(elts)
    #@+node:ekr.20160317054700.150: *4* sf.Name
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
    #@+node:ekr.20160317054700.151: *4* sf.Tuple
    def do_Tuple(self, node):
        '''StubFormatter.Tuple.'''
        elts = [self.visit(z) for z in node.elts]
        if 1:
            return 'Tuple[%s]' % ', '.join(elts)
        else:
            s = '(%s)' % ', '.join(elts)
            return self.match_all(node, s)
        # return 'Tuple[%s]' % ', '.join(elts)
    #@+node:ekr.20160317054700.152: *3* sf.Operators

    # StubFormatter visitors for operators...
    #@+node:ekr.20160317054700.153: *4* sf.BinOp

    # BinOp(expr left, operator op, expr right)

    def do_BinOp(self, node):
        '''StubFormatter.BinOp visitor.'''
        trace = False or self.trace_reduce; verbose = False
        numbers = ['number', 'complex', 'float', 'long', 'int',]
        op = self.op_name(node.op)
        lhs = self.visit(node.left)
        rhs = self.visit(node.right)
        if op.strip() in ('is', 'is not', 'in', 'not in'):
            s = 'bool'
        elif lhs == rhs:
            # Perhaps not always right, but it is correct for Tuple, List, Dict.
            s = lhs
        elif lhs in numbers and rhs in numbers:
            # reduce_numbers would be wrong: it returns a list.
            s = reduce_types([lhs, rhs], trace=trace)
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
    #@+node:ekr.20160317054700.154: *4* sf.BoolOp

    # BoolOp(boolop op, expr* values)

    def do_BoolOp(self, node):  # Python 2.x only.
        '''StubFormatter.BoolOp visitor for 'and' and 'or'.'''
        trace = False or self.trace_reduce
        op = self.op_name(node.op)
        values = [self.visit(z).strip() for z in node.values]
        s = reduce_types(values, trace=trace)
        s = self.match_all(node, s)
        self.trace_visitor(node, op, s)
        return s
    #@+node:ekr.20160317054700.155: *4* sf.Call & sf.keyword

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
        args = [z for z in args if z]  # Kludge: Defensive coding.
        # Explicit pattern:
        if func in ('dict', 'list', 'set', 'tuple',):
            s = '%s[%s]' % (func.capitalize(), ', '.join(args))
        else:
            s = '%s(%s)' % (func, ', '.join(args))
        s = self.match_all(node, s, trace=trace)
        self.trace_visitor(node, 'call', s)
        return s
    #@+node:ekr.20160317054700.156: *5* sf.keyword

    # keyword = (identifier arg, expr value)

    def do_keyword(self, node):
        # node.arg is a string.
        value = self.visit(node.value)
        # This is a keyword *arg*, not a Python keyword!
        return '%s=%s' % (node.arg, value)
    #@+node:ekr.20160317054700.157: *4* sf.Compare

    # Compare(expr left, cmpop* ops, expr* comparators)

    def do_Compare(self, node):
        '''
        StubFormatter ast.Compare visitor for these ops:
        '==', '!=', '<', '<=', '>', '>=', 'is', 'is not', 'in', 'not in',
        '''
        s = 'bool'  # Correct regardless of arguments.
        ops = ','.join([self.op_name(z) for z in node.ops])
        self.trace_visitor(node, ops, s)
        return s
    #@+node:ekr.20160317054700.158: *4* sf.IfExp

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
    #@+node:ekr.20160317054700.159: *4* sf.Subscript

    # Subscript(expr value, slice slice, expr_context ctx)

    def do_Subscript(self, node):
        '''StubFormatter.Subscript.'''
        s = '%s[%s]' % (
            self.visit(node.value),
            self.visit(node.slice))
        s = self.match_all(node, s)
        self.trace_visitor(node, '[]', s)
        return s
    #@+node:ekr.20160317054700.160: *4* sf.UnaryOp

    # UnaryOp(unaryop op, expr operand)

    def do_UnaryOp(self, node):
        '''StubFormatter.UnaryOp for unary +, -, ~ and 'not' operators.'''
        op = self.op_name(node.op)
        if op.strip() == 'not':
            return 'bool'
        else:
            s = self.visit(node.operand)
            s = self.match_all(node, s)
            self.trace_visitor(node, op, s)
            return s
    #@+node:ekr.20160317054700.161: *3* sf.Return
    def do_Return(self, node):
        '''
        StubFormatter ast.Return vsitor.
        Return only the return expression itself.
        '''
        s = AstFormatter.do_Return(self, node)
        assert s.startswith('return'), repr(s)
        return s[len('return') :].strip()
    #@-others
#@+node:ekr.20160317054700.162: ** class StubTraverser (ast.NodeVisitor)
class StubTraverser(ast.NodeVisitor):
    '''
    An ast.Node traverser class that outputs a stub for each class or def.
    Names of visitors must start with visit_. The order of traversal does
    not matter, because so few visitors do anything.
    '''
    #@+others
    #@+node:ekr.20160317054700.163: *3* st.ctor
    def __init__(self, controller):
        '''Ctor for StubTraverser class.'''
        self.controller = x = controller  # A StandAloneMakeStubFile instance.
        # Internal state ivars...
        self.class_name_stack = []
        self.context_stack = []
        sf = StubFormatter(controller=controller, traverser=self)
        self.format = sf.format
        self.arg_format = AstArgFormatter().format
        self.level = 0
        self.output_file = None
        self.parent_stub = None
        self.raw_format = AstFormatter().format
        self.returns = []
        self.stubs_dict = {}  # Keys are stub.full_name's.  Values are stubs.
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

    #@+node:ekr.20160317054700.164: *3* st.add_stub
    def add_stub(self, d, stub):
        '''Add the stub to d, checking that it does not exist.'''
        key = stub.full_name
        assert key
        if key in d:
            caller = g.callers(2).split(',')[1]
            g.trace('Ignoring duplicate entry for %s in %s' % (stub, caller))
        else:
            d[key] = stub
    #@+node:ekr.20160317054700.165: *3* st.indent & out
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
            self.output_file.write(s + '\n')
        else:
            print(s)
    #@+node:ekr.20160317054700.166: *3* st.run (main line) & helpers
    def run(self, node):
        '''StubTraverser.run: write the stubs in node's tree to self.output_fn.'''
        fn = self.output_fn
        dir_ = os.path.dirname(fn)
        if os.path.exists(fn) and not self.overwrite:
            print('file exists: %s' % fn)
        elif not dir_ or os.path.exists(dir_):
            t1 = time.time()
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
            t2 = time.time()
            print('wrote: %s in %4.2f sec' % (fn, t2 - t1))
        else:
            print('output directory not not found: %s' % dir_)
    #@+node:ekr.20160317054700.167: *4* st.output_stubs
    def output_stubs(self, stub):
        '''Output this stub and all its descendants.'''
        for s in stub.out_list or []:
            # Indentation must be present when an item is added to stub.out_list.
            if self.output_file:
                self.output_file.write(s.rstrip() + '\n')
            else:
                print(s)
        # Recursively print all children.
        for child in stub.children:
            self.output_stubs(child)
    #@+node:ekr.20160317054700.168: *4* st.output_time_stamp
    def output_time_stamp(self):
        '''Put a time-stamp in the output file.'''
        if self.output_file:
            self.output_file.write('# make_stub_files: %s\n' %
                time.strftime("%a %d %b %Y at %H:%M:%S"))
    #@+node:ekr.20160317054700.169: *4* st.update & helpers
    def update(self, fn, new_root):
        '''
        Merge the new_root tree with the old_root tree in fn (a .pyi file).

        new_root is the root of the stub tree from the .py file.
        old_root (read below) is the root of stub tree from the .pyi file.

        Return old_root, or new_root if there are any errors.
        '''
        trace = False; verbose = False
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
    #@+node:ekr.20160317054700.170: *5* st.get_stub_file
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
    #@+node:ekr.20160317054700.171: *5* st.parse_stub_file
    def parse_stub_file(self, s, root_name):
        '''
        Parse s, the contents of a stub file, into a tree of Stubs.

        Parse by hand, so that --update can be run with Python 2.
        '''
        trace = False
        assert '\t' not in s
        d = {}
        root = Stub(kind='root', name=root_name)
        indent_stack = [-1]  # To prevent the root from being popped.
        stub_stack = [root]
        lines = []
        pat = re.compile(r'^([ ]*)(def|class)\s+([a-zA-Z_]+)(.*)')
        for line in g.splitLines(s):
            m = pat.match(line)
            if m:
                indent, kind, name, rest = (len(m.group(1)), m.group(2), m.group(3), m.group(4))
                old_indent = indent_stack[-1]
                # Terminate any previous lines.
                old_stub = stub_stack[-1]
                old_stub.out_list.extend(lines)
                if trace:
                    for s in lines:
                        g.trace('  ' + s.rstrip())
                lines = [line]
                # Adjust the stacks.
                if indent == old_indent:
                    stub_stack.pop()
                elif indent > old_indent:
                    indent_stack.append(indent)
                else:  # indent < old_indent
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
                    g.trace('%s%5s %s %s' % (' ' * indent, kind, name, rest))
            else:
                parent = stub_stack[-1]
                lines.append(line)
        # Terminate the last stub.
        old_stub = stub_stack[-1]
        old_stub.out_list.extend(lines)
        if trace:
            for s in lines:
                g.trace('  ' + s.rstrip())
        return d, root
    #@+node:ekr.20160317054700.172: *5* st.merge_stubs & helpers
    def merge_stubs(self, new_stubs, old_root, new_root, trace=False):
        '''
        Merge the new_stubs *list* into the old_root *tree*.
        - new_stubs is a list of Stubs from the .py file.
        - old_root is the root of the stubs from the .pyi file.
        - new_root is the root of the stubs from the .py file.
        '''
        trace = False or trace; verbose = False
        # Part 1: Delete old stubs do *not* exist in the *new* tree.
        # check_delete checks that all ancestors of deleted nodes will be deleted.
        aList = self.check_delete(new_stubs,
            old_root, new_root, trace and verbose)
        # Sort old stubs so that children are deleted before parents.
        aList = list(reversed(self.sort_stubs_by_hierarchy(aList)))
        if trace and verbose:
            dump_list('ordered delete list', aList)
        for stub in aList:
            if trace: g.trace('deleting  %s' % stub)
            parent = self.find_parent_stub(stub, old_root) or old_root
            parent.children.remove(stub)
            assert not self.find_stub(stub, old_root), stub
        # Part 2: Insert new stubs that *not* exist in the *old* tree.
        # Sort new stubs so that parents are created before children.
        aList = [z for z in new_stubs if not self.find_stub(z, old_root)]
        aList = self.sort_stubs_by_hierarchy(aList)
        for stub in aList:
            if trace: g.trace('inserting %s' % stub)
            parent = self.find_parent_stub(stub, old_root) or old_root
            parent.children.append(stub)
            assert self.find_stub(stub, old_root), stub
    #@+node:ekr.20160317054700.173: *6* st.check_delete
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
    #@+node:ekr.20160317054700.174: *6* st.flatten_stubs
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
    #@+node:ekr.20160317054700.175: *6* st.find_parent_stub
    def find_parent_stub(self, stub, root):
        '''Return stub's parent **in root's tree**.'''
        return self.find_stub(stub.parent, root) if stub.parent else None
    #@+node:ekr.20160317054700.176: *6* st.find_stub
    def find_stub(self, stub, root):
        '''Return the stub **in root's tree** that matches stub.'''
        if stub == root:  # Must use Stub.__eq__!
            return root  # not stub!
        for child in root.children:
            stub2 = self.find_stub(stub, child)
            if stub2: return stub2
        return None
    #@+node:ekr.20160317054700.177: *6* st.sort_stubs_by_hierarchy
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
        return []  # Abort the merge.
    #@+node:ekr.20160317054700.178: *5* st.trace_stubs
    def trace_stubs(self, stub, aList=None, header=None, level=-1):
        '''Return a trace of the given stub and all its descendants.'''
        indent = ' ' * 4 * max(0, level)
        if level == -1:
            aList = ['===== %s...\n' % (header) if header else '']
        for s in stub.out_list:
            aList.append('%s%s' % (indent, s.rstrip()))
        for child in stub.children:
            self.trace_stubs(child, level=level + 1, aList=aList)
        if level == -1:
            return '\n'.join(aList) + '\n'
        return None
    #@+node:ekr.20160317054700.179: *3* st.visit_ClassDef

    # 2: ClassDef(identifier name, expr* bases,
    #             stmt* body, expr* decorator_list)
    # 3: ClassDef(identifier name, expr* bases,
    #             keyword* keywords, expr? starargs, expr? kwargs
    #             stmt* body, expr* decorator_list)
    #
    # keyword arguments supplied to call (NULL identifier for **kwargs)
    # keyword = (identifier? arg, expr value)

    def visit_ClassDef(self, node):

        # Create the stub in the old context.
        old_stub = self.parent_stub
        self.parent_stub = Stub('class', node.name, old_stub, self.context_stack)
        self.add_stub(self.stubs_dict, self.parent_stub)
        # Enter the new context.
        self.class_name_stack.append(node.name)
        self.context_stack.append(node.name)
        if self.trace_matches or self.trace_reduce:
            print('\nclass %s\n' % node.name)
        # Format...
        bases = [self.visit(z) for z in node.bases] if node.bases else []
        if getattr(node, 'keywords', None):  # Python 3
            for keyword in node.keywords:
                bases.append('%s=%s' % (keyword.arg, self.visit(keyword.value)))
        if getattr(node, 'starargs', None):  # Python 3
            bases.append('*%s' % self.visit(node.starargs))
        if getattr(node, 'kwargs', None):  # Python 3
            bases.append('*%s' % self.visit(node.kwargs))
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
    #@+node:ekr.20160317054700.180: *3* st.visit_FunctionDef & helpers

    # 2: FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list)
    # 3: FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list,
    #                expr? returns)

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
    #@+node:ekr.20160317054700.181: *4* st.format_arguments & helper

    # arguments = (expr* args, identifier? vararg, identifier? kwarg, expr* defaults)

    def format_arguments(self, node):
        '''
        Format the arguments node.
        Similar to AstFormat.do_arguments, but it is not a visitor!
        '''
        assert isinstance(node, ast.arguments), node
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
            if hasattr(ast, 'arg'):  # python 3:
                name = self.raw_format(name)
            result.append('*' + name)
        name = getattr(node, 'kwarg', None)
        if name:
            if hasattr(ast, 'arg'):  # python 3:
                name = self.raw_format(name)
            result.append('**' + name)
        return ', '.join(result)
    #@+node:ekr.20160317054700.182: *5* st.munge_arg
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
    #@+node:ekr.20160317054700.183: *4* st.format_returns & helpers
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
        if not [z for z in self.returns if z.value is not None]:
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
    #@+node:ekr.20160317054700.184: *5* st.format_return_expressions
    def format_return_expressions(self, name, raw_returns, reduced_returns):
        '''
        aList is a list of maximally reduced return expressions.
        For each expression e in Alist:
        - If e is a single known type, add e to the result.
        - Otherwise, add Any # e to the result.
        Return the properly indented result.
        '''
        assert len(raw_returns) == len(reduced_returns)
        lws = '\n' + ' ' * 4
        n = len(raw_returns)
        known = all([is_known_type(e) for e in reduced_returns])
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
                s = reduce_types(reduced_returns, name=name, trace=self.trace_reduce)
                return s + ': ...' + results
            else:
                return 'Any: ...' + results
        else:
            s = reduce_types(reduced_returns, name=name, trace=self.trace_reduce)
            return s + ': ...'
    #@+node:ekr.20160317054700.185: *5* st.get_def_name
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
    #@+node:ekr.20160317054700.186: *5* st.remove_recursive_calls
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
    #@+node:ekr.20160317054700.187: *3* st.visit_Return
    def visit_Return(self, node):

        self.returns.append(node)
            # New: return the entire node, not node.value.
    #@-others
#@+node:ekr.20160317054700.188: ** class TestClass
class TestClass:
    '''
    A class containing constructs that have caused difficulties.
    This is in the make_stub_files directory, not the test directory.
    '''
    # pylint: disable=no-member
    # pylint: disable=undefined-variable
    # pylint: disable=no-method-argument
    # pylint: disable=unsubscriptable-object
    #@+others
    #@+node:ekr.20160317054700.189: *3* parse_group (Guido)
    def parse_group(self, group):
        if len(group) >= 3 and group[-2] == 'as':
            del group[-2:]
        ndots = 0
        i = 0
        while len(group) > i and group[i].startswith('.'):
            ndots += len(group[i])
            i += 1
        assert ''.join(group[:i]) == '.' * ndots, group
        del group[:i]
        assert all(g == '.' for g in group[1::2]), group
        return ndots, os.sep.join(group[::2])
    #@+node:ekr.20160317054700.190: *3* return_all
    def return_all(self, s3):
        return all([is_known_type(z) for z in s3.split(',')])
        # return all(['abc'])
    #@+node:ekr.20160317054700.191: *3* return_array
    def return_array(self):
        s = 'abc'

        def f(s):
            pass

        return f(s[1:-1])
    #@+node:ekr.20160317054700.192: *3* return_list
    def return_list(self, a):
        return [a]
    #@+node:ekr.20160317054700.193: *3* return_two_lists (fails)
    def return_two_lists(self, aList, s):
        if 1:
            return aList
        else:
            return list(re.finditer('abc', s))
    #@-others
#@-others

g = LeoGlobals()  # For ekr.
if __name__ == "__main__":
    main()
#@-leo

#@+leo-ver=5-thin
#@+node:ekr.20160316091132.1: * @file ../external/py2cs.py
#!/usr/bin/env python
'''
This script makes a coffeescript file for every python source file listed
on the command line (wildcard file names are supported).

For full details, see README.md.

Released under the MIT License.

Written by Edward K. Ream.

Hosted at: https://github.com/edreamleo/python-to-coffeescript
'''
#@+<< license >>
#@+node:ekr.20160316091132.2: **   << license >> (python_to_coffeescript.py)
#@@nocolor-node
#@+at
# All parts of this script are distributed under the following copyright.
# This is intended to be the same as the MIT license, namely that this script
# is absolutely free, even for commercial use, including resale. There is no
# GNU-like "copyleft" restriction. This license is compatible with the GPL.
#
# **Copyright 2016 by Edward K. Ream. All Rights Reserved.**
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# **THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.**
#@-<< license >>
#@+<< imports >>
#@+node:ekr.20160316091132.3: **   << imports >> (python_to_coffeescript.py)
import ast
import configparser
import glob
import io
import optparse
import os
import sys
import time
import token as token_module
import tokenize
#@-<< imports >>
#@+others
#@+node:ekr.20160316091132.4: **   main
def main():
    '''
    The driver for the stand-alone version of make-stub-files.
    All options come from ~/stubs/make_stub_files.cfg.
    '''
    # g.cls()
    controller = MakeCoffeeScriptController()
    controller.scan_command_line()
    controller.scan_options()
    controller.run()
    print('done')
#@+node:ekr.20160523111738.1: **   unit_test (py2cs.py)
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
        # Remove base class.
    aList = [z for z in aList if not z.startswith('_') and not z in remove]
    # Now test them.
    traverser = CoffeeScriptTraverser(controller=None)
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
#@+node:ekr.20160316091132.5: **   utility functions

#
# Utility functions...
#
#@+node:ekr.20160316091132.6: *3* dump
def dump(title, s=None):
    if s:
        print('===== %s...\n%s\n' % (title, s.rstrip()))
    else:
        print('===== %s...\n' % title)
#@+node:ekr.20160316091132.7: *3* dump_dict
def dump_dict(title, d):
    '''Dump a dictionary with a header.'''
    dump(title)
    for z in sorted(d):
        print('%30s %s' % (z, d.get(z)))
    print('')
#@+node:ekr.20160316091132.8: *3* dump_list
def dump_list(title, aList):
    '''Dump a list with a header.'''
    dump(title)
    for z in aList:
        print(z)
    print('')
#@+node:ekr.20160316091132.9: *3* op_name
def op_name(node, strict=True):
    '''Return the print name of an operator node.'''
    d = {
        # Binary operators.
        'Add': '+',
        'BitAnd': '&',
        'BitOr': '|',
        'BitXor': '^',
        'Div': '/',
        'FloorDiv': '//',
        'LShift': '<<',
        'Mod': '%',
        'Mult': '*',
        'Pow': '**',
        'RShift': '>>',
        'Sub': '-',
        # Boolean operators.
        'And': ' and ',
        'Or': ' or ',
        # Comparison operators
        'Eq': '==',
        'Gt': '>',
        'GtE': '>=',
        'In': ' in ',
        'Is': ' is ',
        'IsNot': ' is not ',
        'Lt': '<',
        'LtE': '<=',
        'NotEq': '!=',
        'NotIn': ' not in ',
        # Context operators.
        'AugLoad': '<AugLoad>',
        'AugStore': '<AugStore>',
        'Del': '<Del>',
        'Load': '<Load>',
        'Param': '<Param>',
        'Store': '<Store>',
        # Unary operators.
        'Invert': '~',
        'Not': ' not ',
        'UAdd': '+',
        'USub': '-',
    }
    kind = node.__class__.__name__
    name = d.get(kind, '<%s>' % kind)
    if strict: assert name, kind
    return name
#@+node:ekr.20160316091132.10: *3* pdb
def pdb(self):
    '''Invoke a debugger during unit testing.'''
    try:
        from leo.core import leoGlobals as leo_g
        leo_g.pdb()
    except ImportError:
        import pdb
        pdb.set_trace()
#@+node:ekr.20160316091132.11: *3* truncate
def truncate(s, n):
    '''Return s truncated to n characters.'''
    return s if len(s) <= n else s[: n - 3] + '...'
#@+node:ekr.20160316091132.12: ** class CoffeeScriptTraverser
class CoffeeScriptTraverser:
    '''A class to convert python sources to coffeescript sources.'''
    # pylint: disable=consider-using-enumerate
    #@+others
    #@+node:ekr.20160316091132.13: *3*  cv.ctor
    def __init__(self, controller):
        '''Ctor for CoffeeScriptFormatter class.'''
        self.controller = controller
        self.class_stack = []
        # Redirection. Set in format.
        self.sync_string = None
        self.last_node = None
        self.leading_lines = None
        self.leading_string = None
        self.tokens_for_statement = None
        self.trailing_comment = None
        self.trailing_comment_at_lineno = None

    #@+node:ekr.20160316091132.14: *3*  cv.format
    def format(self, node, s, tokens):
        '''Format the node (or list of nodes) and its descendants.'''
        self.level = 0
        self.sync = sync = TokenSync(s, tokens)
        # Create aliases here for convenience.
        self.sync_string = sync.sync_string
        self.last_node = sync.last_node
        self.leading_lines = sync.leading_lines
        self.leading_string = sync.leading_string
        self.tokens_for_statement = sync.tokens_for_statement
        self.trailing_comment = sync.trailing_comment
        self.trailing_comment_at_lineno = sync.trailing_comment_at_lineno
        # Compute the result.
        val = self.visit(node)
        sync.check_strings()
        # if isinstance(val, list): # testing:
            # val = ' '.join(val)
        val += ''.join(sync.trailing_lines())
        return val or ''
    #@+node:ekr.20160316091132.15: *3*  cv.indent
    def indent(self, s):
        '''Return s, properly indented.'''
        n = 0
        while s and s.startswith('\n'):
            n += 1
            s = s[1:]
        return '%s%s%s' % ('\n' * n, ' ' * 4 * self.level, s)
    #@+node:ekr.20160316091132.16: *3*  cv.visit
    def visit(self, node):
        '''Return the formatted version of an Ast node, or list of Ast nodes.'''
        name = node.__class__.__name__
        if isinstance(node, (list, tuple)):
            return ', '.join([self.visit(z) for z in node])
        if node is None:
            return 'None'
        assert isinstance(node, ast.AST), name
        method = getattr(self, 'do_' + name)
        s = method(node)
        assert isinstance(s, str), (repr(s), method.__name__)
        return s
    #@+node:ekr.20160316091132.17: *3* cv.Contexts

    #
    # CoffeeScriptTraverser contexts...
    #
    #@+node:ekr.20160316091132.18: *4* cv.ClassDef

    # 2: ClassDef(identifier name, expr* bases,
    #             stmt* body, expr* decorator_list)
    # 3: ClassDef(identifier name, expr* bases,
    #             keyword* keywords, expr? starargs, expr? kwargs
    #             stmt* body, expr* decorator_list)
    #
    # keyword arguments supplied to call (NULL identifier for **kwargs)
    # keyword = (identifier? arg, expr value)

    def do_ClassDef(self, node):

        result = self.leading_lines(node)
        tail = self.trailing_comment(node)
        name = node.name  # Only a plain string is valid.
        bases = [self.visit(z) for z in node.bases] if node.bases else []
        if getattr(node, 'keywords', None):  # Python 3
            for keyword in node.keywords:
                bases.append('%s=%s' % (keyword.arg, self.visit(keyword.value)))
        if getattr(node, 'starargs', None):  # Python 3
            bases.append('*%s' % self.visit(node.starargs))
        if getattr(node, 'kwargs', None):  # Python 3
            bases.append('*%s' % self.visit(node.kwargs))
        if bases:
            s = 'class %s extends %s' % (name, ', '.join(bases))
        else:
            s = 'class %s' % name
        result.append(self.indent(s + tail))
        self.class_stack.append(name)
        for i, z in enumerate(node.body):
            self.level += 1
            result.append(self.visit(z))
            self.level -= 1
        self.class_stack.pop()
        return ''.join(result)
    #@+node:ekr.20160316091132.19: *4* cv.FunctionDef & AsyncFunctionDef

    # 2: FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list)
    # 3: FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list,
    #                expr? returns)

    def do_FunctionDef(self, node):
        '''Format a FunctionDef node.'''
        result = self.leading_lines(node)
        if node.decorator_list:
            for z in node.decorator_list:
                tail = self.trailing_comment(z)
                s = '@%s' % self.visit(z)
                result.append(self.indent(s + tail))
        name = node.name  # Only a plain string is valid.
        args = self.visit(node.args) if node.args else ''
        args = [z.strip() for z in args.split(',')]
        if self.class_stack and args and args[0] == '@':
            args = args[1:]
        args = ', '.join(args)
        args = '(%s) ' % args if args else ''
        # Traverse node.returns to keep strings in sync.
        if getattr(node, 'returns', None):
            self.visit(node.returns)
        tail = self.trailing_comment(node)
        sep = ': ' if self.class_stack else ' = '
        s = '%s%s%s->%s' % (name, sep, args, tail)
        result.append(self.indent(s))
        for i, z in enumerate(node.body):
            self.level += 1
            result.append(self.visit(z))
            self.level -= 1
        return ''.join(result)

    do_AsyncFunctionDef = do_FunctionDef
    #@+node:ekr.20160316091132.20: *4* cv.Interactive
    def do_Interactive(self, node):
        for z in node.body:
            self.visit(z)
    #@+node:ekr.20160316091132.21: *4* cv.Module
    def do_Module(self, node):

        return ''.join([self.visit(z) for z in node.body])
    #@+node:ekr.20160316091132.22: *4* cv.Lambda
    def do_Lambda(self, node):
        return self.indent('lambda %s: %s' % (
            self.visit(node.args),
            self.visit(node.body)))
    #@+node:ekr.20160316091132.23: *3* cv.Expressions

    #
    # CoffeeScriptTraverser expressions...
    #
    #@+node:ekr.20160316091132.24: *4* cv.Expression
    def do_Expression(self, node):
        '''An inner expression: do not indent.'''
        return '%s\n' % self.visit(node.body)
    #@+node:ekr.20160316091132.25: *4* cv.GeneratorExp
    def do_GeneratorExp(self, node):
        elt = self.visit(node.elt) or ''
        gens = [self.visit(z) for z in node.generators]
        gens = [z if z else '<**None**>' for z in gens]  # Kludge: probable bug.
        return '<gen %s for %s>' % (elt, ','.join(gens))
    #@+node:ekr.20160316091132.26: *3* cv.Operands

    #
    # CoffeeScriptTraverser operands...
    #
    #@+node:ekr.20160316091132.28: *4* cv.arg
    # arg = (identifier arg, expr? annotation)

    def do_arg(self, node):

        # Visit the node.annotation to keep strings in sync.
        if getattr(node, 'annotation', None):
            self.visit(node.annotation)
        return node.arg
    #@+node:ekr.20160316091132.27: *4* cv.arguments

    # 2: arguments = (expr* args, identifier? vararg,
    #                 identifier? kwarg, expr* defaults)
    # 3: arguments = (arg*  args, arg? vararg,
    #                arg* kwonlyargs, expr* kw_defaults,
    #                arg? kwarg, expr* defaults)

    def do_arguments(self, node):
        '''Format the arguments node.'''
        assert isinstance(node, ast.arguments)
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
        args = [self.visit(z) for z in node.kwonlyargs]
        defaults = [self.visit(z) for z in node.kw_defaults]
        n_plain = len(args) - len(defaults)
        for i in range(len(args)):
            if i < n_plain:
                args2.append(args[i])
            else:
                args2.append('%s=%s' % (args[i], defaults[i - n_plain]))
        # Add the vararg and kwarg expressions.
        if getattr(node, 'vararg', None):
            args2.append('*' + self.visit(node.vararg))
        if getattr(node, 'kwarg', None):
            args2.append('**' + self.visit(node.kwarg))
        return ','.join(args2)
    #@+node:ekr.20160316091132.29: *4* cv.Attribute

    # Attribute(expr value, identifier attr, expr_context ctx)

    def do_Attribute(self, node):

        # Don't visit node.attr: it is always a string.
        val = self.visit(node.value)
        val = '@' if val == '@' else val + '.'
        return val + node.attr
    #@+node:ekr.20160316091132.30: *4* cv.Bytes
    def do_Bytes(self, node):  # Python 3.x only.
        if hasattr(node, 'lineno'):
            # Do *not* handle leading lines here.
            # leading = self.leading_string(node)
            return self.sync_string(node)
        g.trace('==== no lineno', node.s)
        return node.s
    #@+node:ekr.20160316091132.31: *4* cv.Call & cv.keyword

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
        s = '%s(%s)' % (func, ','.join(args))
        return s
    #@+node:ekr.20160316091132.32: *5* cv.keyword

    # keyword = (identifier arg, expr value)

    def do_keyword(self, node):
        # node.arg is a string.
        value = self.visit(node.value)
        # This is a keyword *arg*, not a Python keyword!
        return '%s=%s' % (node.arg, value)
    #@+node:ekr.20160316091132.33: *4* cv.comprehension
    def do_comprehension(self, node):
        result = []
        name = self.visit(node.target)  # A name.
        it = self.visit(node.iter)  # An attribute.
        result.append('%s in %s' % (name, it))
        ifs = [self.visit(z) for z in node.ifs]
        if ifs:
            result.append(' if %s' % (''.join(ifs)))
        return ''.join(result)
    #@+node:ekr.20170721093550.1: *4* cv.Constant (Python 3.6+)
    def do_Constant(self, node):  # Python 3.6+ only.

        if not hasattr(node, 'lineno'):
            # Do *not* handle leading lines here.
            g.trace('==== no lineno', node.s)
            return node.s
        val = node.value
        # Support Python 3.8.
        if val is None:
            return 'None'
        if val == Ellipsis:
            return '...'
        if isinstance(val, (bool, bytes, float, int)):
            return str(val)
        if isinstance(val, str):
            return self.sync_string(node)
        if isinstance(node.value, tuple):
            return ','.join(node.elts)
        if isinstance(node.value, frozenset):
            return '{' + ','.join(node.elts) + '}'
        # Unknown type.
        g.trace('----- Oops -----', repr(node.value), g.callers())
        return node.s
    #@+node:ekr.20160316091132.34: *4* cv.Dict
    def do_Dict(self, node):
        assert len(node.keys) == len(node.values)
        items, result = [], []
        result.append('{')
        self.level += 1
        for i, key in enumerate(node.keys):
            head = self.leading_lines(key)  # Prevents leading lines from being handled again.
            head = [z for z in head if z.strip()]  # Ignore blank lines.
            if head:
                items.extend('\n' + ''.join(head))
            tail = self.trailing_comment(node.values[i])
            key = self.visit(node.keys[i])
            value = self.visit(node.values[i])
            s = '%s:%s%s' % (key, value, tail)
            items.append(self.indent(s))
        self.level -= 1
        result.extend(items)
        if items:
            result.append(self.indent('}'))
        else:
            result.append('}')
        return ''.join(result)
    #@+node:ekr.20160523135819.3: *4* cv.DictComp (new)
    # DictComp(expr key, expr value, comprehension* generators)

    def do_DictComp(self, node):
        elt = self.visit(node.elt)
        gens = [self.visit(z) for z in node.generators]
        gens = [z if z else '<**None**>' for z in gens]  # Kludge: probable bug.
        return '%s for %s' % (elt, ''.join(gens))

    #@+node:ekr.20160316091132.35: *4* cv.Ellipsis
    def do_Ellipsis(self, node):
        return '...'
    #@+node:ekr.20160316091132.36: *4* cv.ExtSlice
    def do_ExtSlice(self, node):
        return ':'.join([self.visit(z) for z in node.dims])
    #@+node:ekr.20170721093848.1: *4* cv.FormattedValue (Python 3.6+: unfinished)
    # FormattedValue(expr value, int? conversion, expr? format_spec)

    def do_FormattedValue(self, node):  # Python 3.6+ only.

        return '%s%s%s' % (
            self.visit(node.value),
            self.visit(node.conversion) if node.conversion else '',
            self.visit(node.format_spec) if node.format_spec else '')
    #@+node:ekr.20160316091132.37: *4* cv.Index
    def do_Index(self, node):
        return self.visit(node.value)
    #@+node:ekr.20170721093747.1: *4* cv.JoinedStr (Python 3.6+: unfinished)
    # JoinedStr(expr* values)

    def do_JoinedStr(self, node):

        if node.values:
            for value in node.values:
                self.visit(value)

    #@+node:ekr.20160316091132.38: *4* cv.List
    def do_List(self, node):
        # Not used: list context.
        # self.visit(node.ctx)
        elts = [self.visit(z) for z in node.elts]
        elts = [z for z in elts if z]  # Defensive.
        return '[%s]' % ','.join(elts)
    #@+node:ekr.20160316091132.39: *4* cv.ListComp
    def do_ListComp(self, node):
        elt = self.visit(node.elt)
        gens = [self.visit(z) for z in node.generators]
        gens = [z if z else '<**None**>' for z in gens]  # Kludge: probable bug.
        return '%s for %s' % (elt, ''.join(gens))
    #@+node:ekr.20160316091132.40: *4* cv.Name & cv.NameConstant
    def do_Name(self, node):
        return '@' if node.id == 'self' else node.id

    def do_NameConstant(self, node):  # Python 3 only.
        s = repr(node.value)
        return 'bool' if s in ('True', 'False') else s
    #@+node:ekr.20160316091132.41: *4* cv.Num
    def do_Num(self, node):
        return repr(node.n)
    #@+node:ekr.20160523135819.4: *4* cv.Set (new)
    # Set(expr* elts)

    def do_Set(self, node):
        elts = [self.visit(z) for z in node.elts]
        elts = [z for z in elts if z]  # Defensive.
        return '{%s}' % ','.join(elts)
    #@+node:ekr.20160523135819.5: *4* cv.SetComp (new)
    # SetComp(expr elt, comprehension* generators)

    def do_SetComp(self, node):
        elt = self.visit(node.elt)
        gens = [self.visit(z) for z in node.generators]
        gens = [z if z else '<**None**>' for z in gens]  # Kludge: probable bug.
        return '%s for %s' % (elt, ''.join(gens))
    #@+node:ekr.20160316091132.43: *4* cv.Slice
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
        return '%s:%s' % (lower, upper)
    #@+node:ekr.20160316091132.44: *4* cv.Str
    def do_Str(self, node):
        '''A string constant, including docstrings.'''
        if hasattr(node, 'lineno'):
            # Do *not* handle leading lines here.
            # leading = self.leading_string(node)
            return self.sync_string(node)
        g.trace('==== no lineno', node.s)
        return node.s
    #@+node:ekr.20160316091132.45: *4* cv.Subscript

    # Subscript(expr value, slice slice, expr_context ctx)

    def do_Subscript(self, node):
        value = self.visit(node.value)
        the_slice = self.visit(node.slice)
        return '%s[%s]' % (value, the_slice)
    #@+node:ekr.20160316091132.46: *4* cv.Tuple
    def do_Tuple(self, node):
        elts = [self.visit(z) for z in node.elts]
        return '(%s)' % ', '.join(elts)
    #@+node:ekr.20160316091132.47: *3* cv.Operators

    #
    # CoffeeScriptTraverser operators...
    #
    #@+node:ekr.20160316091132.48: *4* cv.BinOp
    def do_BinOp(self, node):
        return '%s%s%s' % (
            self.visit(node.left),
            op_name(node.op),
            self.visit(node.right))
    #@+node:ekr.20160316091132.49: *4* cv.BoolOp
    def do_BoolOp(self, node):
        values = [self.visit(z) for z in node.values]
        return op_name(node.op).join(values)
    #@+node:ekr.20160316091132.50: *4* cv.Compare
    def do_Compare(self, node):
        result = []
        lt = self.visit(node.left)
        ops = [op_name(z) for z in node.ops]
        comps = [self.visit(z) for z in node.comparators]
        result.append(lt)
        if len(ops) == len(comps):
            for i in range(len(ops)):
                result.append('%s%s' % (ops[i], comps[i]))
        else:
            print('can not happen: ops', repr(ops), 'comparators', repr(comps))
        return ''.join(result)
    #@+node:ekr.20160316091132.51: *4* cv.ifExp (ternary operator)
    def do_IfExp(self, node):
        return '%s if %s else %s ' % (
            self.visit(node.body),
            self.visit(node.test),
            self.visit(node.orelse))
    #@+node:ekr.20160316091132.52: *4* cv.UnaryOp
    def do_UnaryOp(self, node):
        return '%s%s' % (
            op_name(node.op),
            self.visit(node.operand))
    #@+node:ekr.20160316091132.53: *3* cv.Statements

    #
    # CoffeeScriptTraverser statements...
    #
    #@+node:ekr.20160316091132.54: *4*  cv.tail_after_body
    def tail_after_body(self, body, aList, result):
        '''
        Return the tail of the 'else' or 'finally' statement following the given body.
        aList is the node.orelse or node.finalbody list.
        '''
        node = self.last_node(body)
        if node:
            max_n = node.lineno
            leading = self.leading_lines(aList[0])
            if leading:
                result.extend(leading)
                max_n += len(leading)
            tail = self.trailing_comment_at_lineno(max_n + 1)
        else:
            tail = '\n'
        return tail
    #@+node:ekr.20170721093332.1: *4* cv.AnnAssign
    # AnnAssign(expr target, expr annotation, expr? value, int simple)

    def do_AnnAssign(self, node):
        head = self.leading_string(node)
        tail = self.trailing_comment(node)
        s = '%s:%s=%s\n' % (
            self.visit(node.target),
            self.visit(node.annotation),
            self.visit(node.value))
        return head + self.indent(s) + tail
    #@+node:ekr.20160316091132.55: *4* cv.Assert
    def do_Assert(self, node):

        head = self.leading_string(node)
        tail = self.trailing_comment(node)
        test = self.visit(node.test)
        if getattr(node, 'msg', None) is not None:
            s = 'assert %s, %s' % (test, self.visit(node.msg))
        else:
            s = 'assert %s' % test
        return head + self.indent(s) + tail
    #@+node:ekr.20160316091132.56: *4* cv.Assign
    def do_Assign(self, node):

        head = self.leading_string(node)
        tail = self.trailing_comment(node)
        s = '%s=%s' % (
            '='.join([self.visit(z) for z in node.targets]),
            self.visit(node.value))
        return head + self.indent(s) + tail
    #@+node:ekr.20160316091132.57: *4* cv.AugAssign
    def do_AugAssign(self, node):

        head = self.leading_string(node)
        tail = self.trailing_comment(node)
        s = '%s%s=%s' % (
            self.visit(node.target),
            op_name(node.op),
            self.visit(node.value))
        return head + self.indent(s) + tail
    #@+node:ekr.20160523135819.2: *4* cv.Await (Python 3)
    # Await(expr value)

    def do_Await(self, node):

        return self.indent('await %s\n' % (
            self.visit(node.value)))
    #@+node:ekr.20160316091132.58: *4* cv.Break
    def do_Break(self, node):

        head = self.leading_string(node)
        tail = self.trailing_comment(node)
        return head + self.indent('break') + tail
    #@+node:ekr.20160316091132.59: *4* cv.Continue
    def do_Continue(self, node):

        head = self.leading_lines(node)
        tail = self.trailing_comment(node)
        return head + self.indent('continue') + tail
    #@+node:ekr.20160316091132.60: *4* cv.Delete
    def do_Delete(self, node):

        head = self.leading_string(node)
        tail = self.trailing_comment(node)
        targets = [self.visit(z) for z in node.targets]
        s = 'del %s' % ','.join(targets)
        return head + self.indent(s) + tail
    #@+node:ekr.20160316091132.61: *4* cv.ExceptHandler
    def do_ExceptHandler(self, node):

        result = self.leading_lines(node)
        tail = self.trailing_comment(node)
        result.append(self.indent('except'))
        if getattr(node, 'type', None):
            result.append(' %s' % self.visit(node.type))
        if getattr(node, 'name', None):
            if isinstance(node.name, ast.AST):
                result.append(' as %s' % self.visit(node.name))
            else:
                result.append(' as %s' % node.name)  # Python 3.x.
        result.append(':' + tail)
        for z in node.body:
            self.level += 1
            result.append(self.visit(z))
            self.level -= 1
        return ''.join(result)
    #@+node:ekr.20160316091132.63: *4* cv.Expr (outer statement)
    def do_Expr(self, node):
        '''An outer expression: must be indented.'''
        head = self.leading_string(node)
        tail = self.trailing_comment(node)
        s = '%s' % self.visit(node.value)
        return head + self.indent(s) + tail
    #@+node:ekr.20160316091132.64: *4* cv.For & AsyncFor
    def do_For(self, node, async_flag=False):

        result = self.leading_lines(node)
        tail = self.trailing_comment(node)
        s = '%sfor %s in %s:' % (
            'async ' if async_flag else '',
            self.visit(node.target),
            self.visit(node.iter))
        result.append(self.indent(s + tail))
        for z in node.body:
            self.level += 1
            result.append(self.visit(z))
            self.level -= 1
        if node.orelse:
            tail = self.tail_after_body(node.body, node.orelse, result)
            result.append(self.indent('else:' + tail))
            for z in node.orelse:
                self.level += 1
                result.append(self.visit(z))
                self.level -= 1
        return ''.join(result)

    def do_AsyncFor(self, node):
        return self.do_For(node, async_flag=True)
    #@+node:ekr.20160316091132.65: *4* cv.Global
    def do_Global(self, node):

        head = self.leading_lines(node)
        tail = self.trailing_comment(node)
        s = 'global %s' % ','.join(node.names)
        return head + self.indent(s) + tail
    #@+node:ekr.20160316091132.66: *4* cv.If
    def do_If(self, node):

        result = self.leading_lines(node)
        tail = self.trailing_comment(node)
        s = 'if %s:%s' % (self.visit(node.test), tail)
        result.append(self.indent(s))
        for z in node.body:
            self.level += 1
            result.append(self.visit(z))
            self.level -= 1
        if node.orelse:
            tail = self.tail_after_body(node.body, node.orelse, result)
            result.append(self.indent('else:' + tail))
            for z in node.orelse:
                self.level += 1
                result.append(self.visit(z))
                self.level -= 1
        return ''.join(result)
    #@+node:ekr.20160316091132.67: *4* cv.Import & helper
    def do_Import(self, node):

        head = self.leading_string(node)
        tail = self.trailing_comment(node)
        names = []
        for fn, asname in self.get_import_names(node):
            if asname:
                names.append('%s as %s' % (fn, asname))
            else:
                names.append(fn)
        s = 'pass # import %s' % ','.join(names)
        return head + self.indent(s) + tail
    #@+node:ekr.20160316091132.68: *5* cv.get_import_names
    def get_import_names(self, node):
        '''Return a list of the the full file names in the import statement.'''
        result = []
        for ast2 in node.names:
            assert isinstance(ast2, ast.alias)
            data = ast2.name, ast2.asname
            result.append(data)
        return result
    #@+node:ekr.20160316091132.69: *4* cv.ImportFrom
    def do_ImportFrom(self, node):

        head = self.leading_string(node)
        tail = self.trailing_comment(node)
        names = []
        for fn, asname in self.get_import_names(node):
            if asname:
                names.append('%s as %s' % (fn, asname))
            else:
                names.append(fn)
        s = 'pass # from %s import %s' % (node.module, ','.join(names))
        return head + self.indent(s) + tail
    #@+node:ekr.20160316151014.1: *4* cv.Nonlocal

    # 3: Nonlocal(identifier* names)

    def do_Nonlocal(self, node):

        # https://www.python.org/dev/peps/pep-3104/
        head = self.leading_string(node)
        tail = self.trailing_comment(node)
        names = ', '.join(node.names)
        return head + self.indent('nonlocal') + names + tail
    #@+node:ekr.20160316091132.70: *4* cv.Pass
    def do_Pass(self, node):

        head = self.leading_string(node)
        tail = self.trailing_comment(node)
        return head + self.indent('pass') + tail
    #@+node:ekr.20160316091132.72: *4* cv.Raise
    # Raise(expr? exc, expr? cause)

    def do_Raise(self, node):

        head = self.leading_string(node)
        tail = self.trailing_comment(node)
        args = []
        for attr in ('exc', 'cause'):
            if getattr(node, attr, None) is not None:
                args.append(self.visit(getattr(node, attr)))
        s = 'raise %s' % ', '.join(args) if args else 'raise'
        return head + self.indent(s) + tail
    #@+node:ekr.20160316091132.73: *4* cv.Return
    def do_Return(self, node):

        head = self.leading_string(node)
        tail = self.trailing_comment(node)
        if node.value:
            s = 'return %s' % self.visit(node.value).strip()
        else:
            s = 'return'
        return head + self.indent(s) + tail
    #@+node:ekr.20160317040520.1: *4* cv.Starred

    # Starred(expr value, expr_context ctx)

    def do_Starred(self, node):

        # https://www.python.org/dev/peps/pep-3132/
        return '*' + self.visit(node.value)
    #@+node:ekr.20160316091132.74: *4* cv.Try

    # 3: Try(stmt* body, excepthandler* handlers, stmt* orelse, stmt* finalbody)

    def do_Try(self, node):  # Python 3

        # https://www.python.org/dev/peps/pep-0341/
        result = self.leading_lines(node)
        tail = self.trailing_comment(node)
        s = 'try' + tail
        result.append(self.indent(s))
        for z in node.body:
            self.level += 1
            result.append(self.visit(z))
            self.level -= 1
        if node.handlers:
            for z in node.handlers:
                result.append(self.visit(z))
        if node.orelse:
            tail = self.tail_after_body(node.body, node.orelse, result)
            result.append(self.indent('else:' + tail))
            for z in node.orelse:
                self.level += 1
                result.append(self.visit(z))
                self.level -= 1
        if node.finalbody:
            tail = self.tail_after_body(node.body, node.finalbody, result)
            s = 'finally:' + tail
            result.append(self.indent(s))
            for z in node.finalbody:
                self.level += 1
                result.append(self.visit(z))
                self.level -= 1
        return ''.join(result)
    #@+node:ekr.20160316091132.75: *4* cv.TryExcept
    def do_TryExcept(self, node):

        result = self.leading_lines(node)
        tail = self.trailing_comment(node)
        s = 'try:' + tail
        result.append(self.indent(s))
        for z in node.body:
            self.level += 1
            result.append(self.visit(z))
            self.level -= 1
        if node.handlers:
            for z in node.handlers:
                result.append(self.visit(z))
        if node.orelse:
            tail = self.trailing_comment(node.orelse)
            s = 'else:' + tail
            result.append(self.indent(s))
            for z in node.orelse:
                self.level += 1
                result.append(self.visit(z))
                self.level -= 1
        return ''.join(result)
    #@+node:ekr.20160316091132.76: *4* cv.TryFinally
    def do_TryFinally(self, node):

        result = self.leading_lines(node)
        tail = self.trailing_comment(node)
        result.append(self.indent('try:' + tail))
        for z in node.body:
            self.level += 1
            result.append(self.visit(z))
            self.level -= 1
        tail = self.tail_after_body(node.body, node.finalbody, result)
        result.append(self.indent('finally:' + tail))
        for z in node.finalbody:
            self.level += 1
            result.append(self.visit(z))
            self.level -= 1
        return ''.join(result)
    #@+node:ekr.20160316091132.77: *4* cv.While
    def do_While(self, node):

        result = self.leading_lines(node)
        tail = self.trailing_comment(node)
        s = 'while %s:' % self.visit(node.test)
        result.append(self.indent(s + tail))
        for z in node.body:
            self.level += 1
            result.append(self.visit(z))
            self.level -= 1
        if node.orelse:
            tail = self.trailing_comment(node)
            result.append(self.indent('else:' + tail))
            for z in node.orelse:
                self.level += 1
                result.append(self.visit(z))
                self.level -= 1
        return ''.join(result)
    #@+node:ekr.20160316091132.78: *4* cv.With & AsyncWith

    # 2:  With(expr context_expr, expr? optional_vars,
    #          stmt* body)
    # 3:  With(withitem* items,
    #          stmt* body)
    # withitem = (expr context_expr, expr? optional_vars)

    def do_With(self, node, async_flag=False):

        result = self.leading_lines(node)
        tail = self.trailing_comment(node)
        vars_list = []
        result.append(self.indent('%swith ' % ('async ' if async_flag else '')))
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
        result.append(':' + tail)
        for z in node.body:
            self.level += 1
            result.append(self.visit(z))
            self.level -= 1
        return ''.join(result) + tail

    def do_AsyncWith(self, node):
        return self.do_With(node, async_flag=True)

    #@+node:ekr.20160316091132.79: *4* cv.Yield
    def do_Yield(self, node):

        head = self.leading_string(node)
        tail = self.trailing_comment(node)
        if getattr(node, 'value', None) is not None:
            s = 'yield %s' % self.visit(node.value)
        else:
            s = 'yield'
        return head + self.indent(s) + tail
    #@+node:ekr.20160317043739.1: *4* cv.YieldFrom

    # 3: YieldFrom(expr value)

    def do_YieldFrom(self, node):

        # https://www.python.org/dev/peps/pep-0380/
        head = self.leading_string(node)
        tail = self.trailing_comment(node)
        s = 'yield from %s' % self.visit(node.value)
        return head + self.indent(s) + tail
    #@-others
#@+node:ekr.20160316091132.80: ** class LeoGlobals
class LeoGlobals:
    '''A class supporting g.pdb and g.trace for compatibility with Leo.'''
    #@+others
    #@+node:ekr.20160316091132.81: *3* class NullObject (Python Cookbook)
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
    #@+node:ekr.20160316091132.82: *3* class ReadLinesClass
    class ReadLinesClass:
        """A class whose next method provides a readline method for Python's tokenize module."""

        def __init__(self, s):
            self.lines = s.splitlines(True) if s else []
            self.i = 0

        def next(self):
            if self.i < len(self.lines):
                line = self.lines[self.i]
                self.i += 1
            else:
                line = ''
            return line

        __next__ = next
    #@+node:ekr.20160316091132.83: *3* g._callerName
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
            return name  # The code name
        except ValueError:
            # print('g._callerName: ValueError',n)
            return ''  # The stack is not deep enough.
        except Exception:
            # es_exception()
            return ''  # "<no caller name>"
    #@+node:ekr.20160316091132.84: *3* g.callers
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
    #@+node:ekr.20160316091132.85: *3* g.cls
    def cls(self):
        '''Clear the screen.'''
        if sys.platform.lower().startswith('win'):
            # Leo 6.7.5: Two calls seem to be required!
            os.system('cls')
            os.system('cls')
    #@+node:ekr.20160316091132.86: *3* g.computeLeadingWhitespace
    def computeLeadingWhitespace(self, width, tab_width):
        '''Returns optimized whitespace corresponding to width with the indicated tab_width.'''
        if width <= 0:
            return ""
        if tab_width > 1:
            tabs = int(width / tab_width)
            blanks = int(width % tab_width)
            return ('\t' * tabs) + (' ' * blanks)
        # Negative tab width always gets converted to blanks.
        return (' ' * width)
    #@+node:ekr.20160316091132.87: *3* g.computeLeadingWhitespaceWidth
    def computeLeadingWhitespaceWidth(self, s, tab_width):
        '''Returns optimized whitespace corresponding to width with the indicated tab_width.'''
        w = 0
        for ch in s:
            if ch == ' ':
                w += 1
            elif ch == '\t':
                w += (abs(tab_width) - (w % abs(tab_width)))
            else:
                break
        return w
    #@+node:ekr.20160316091132.89: *3* g.pdb
    def pdb(self):
        try:
            from leo.core import leoGlobals as leo_g
            leo_g.pdb()
        except ImportError:
            import pdb
            pdb.set_trace()
    #@+node:ekr.20160316091132.90: *3* g.shortFileName
    def shortFileName(self, fileName, n=None):
        if n is None or n < 1:
            return os.path.basename(fileName)
        return '/'.join(fileName.replace('\\', '/').split('/')[-n :])
    #@+node:ekr.20160316091132.91: *3* g.splitLines
    def splitLines(self, s):
        '''Split s into lines, preserving trailing newlines.'''
        return s.splitlines(True) if s else []
    #@+node:ekr.20160316091132.92: *3* g.toUnicode (py2cs.py)
    def toUnicode(self, s, encoding='utf-8', reportErrors=False):
        '''Convert a non-unicode string with the given encoding to unicode.'''
        if isinstance(s, str):
            return s
        if not encoding:
            encoding = 'utf-8'
        # These are the only significant calls to s.decode in Leo.
        # Tracing these calls directly yields thousands of calls.
        # Never call g.trace here!
        try:
            s = s.decode(encoding, 'strict')
        except UnicodeError:
            s = s.decode(encoding, 'replace')
            if reportErrors:
                g.trace(g.callers())
                print("toUnicode: Error converting %s... from %s encoding to unicode" % (
                    s[:200], encoding))
        return s
    #@+node:ekr.20160316091132.93: *3* g.trace (py2cs.py)
    def trace(self, *args, **keys):
        try:
            from leo.core import leoGlobals as leo_g
            leo_g.trace(caller_level=2, *args, **keys)
        except ImportError:
            print(args, keys)
    #@-others
#@+node:ekr.20160316091132.95: ** class MakeCoffeeScriptController
class MakeCoffeeScriptController:
    '''The controller class for python_to_coffeescript.py.'''

    #@+others
    #@+node:ekr.20160316091132.96: *3* mcs.ctor
    def __init__(self):
        '''Ctor for MakeCoffeeScriptController class.'''
        self.options = {}
        # Ivars set on the command line...
        self.config_fn = None
        self.enable_unit_tests = False
        self.files = []  # May also be set in the config file.
        self.section_names = ('Global',)
        # Ivars set in the config file...
        self.output_directory = self.finalize('.')
        self.overwrite = False
        self.verbose = False  # Trace config arguments.
    #@+node:ekr.20160316091132.97: *3* mcs.finalize
    def finalize(self, fn):
        '''Finalize and regularize a filename.'''
        fn = os.path.expanduser(fn)
        fn = os.path.abspath(fn)
        fn = os.path.normpath(fn)
        return fn
    #@+node:ekr.20160316091132.98: *3* mcs.make_coffeescript_file
    def make_coffeescript_file(self, fn, s=None):
        '''
        Make a stub file in the output directory for all source files mentioned
        in the [Source Files] section of the configuration file.
        '''
        if not fn.endswith(('py', 'pyw')):
            print('not a python file', fn)
            return
        if not os.path.exists(fn):
            print('not found', fn)
            return
        base_fn = os.path.basename(fn)
        out_fn = os.path.join(self.output_directory, base_fn)
        out_fn = os.path.normpath(out_fn)
        out_fn = out_fn[:-3] + '.coffee'
        dir_ = os.path.dirname(out_fn)
        if os.path.exists(out_fn) and not self.overwrite:
            print('file exists: %s' % out_fn)
        elif not dir_ or os.path.exists(dir_):
            if s is None:
                s = open(fn).read()
            readlines = g.ReadLinesClass(s).next
            tokens = list(tokenize.generate_tokens(readlines))
            node = ast.parse(s, filename=fn, mode='exec')
            s = CoffeeScriptTraverser(controller=self).format(node, s, tokens)
            f = open(out_fn, 'w')
            self.output_time_stamp(f)
            f.write(s)
            f.close()
            print('wrote: %s' % out_fn)
        else:
            print('output directory not not found: %s' % dir_)
    #@+node:ekr.20160316091132.99: *3* mcs.output_time_stamp
    def output_time_stamp(self, f):
        '''Put a time-stamp in the output file f.'''
        f.write('# python_to_coffeescript: %s\n' %
            time.strftime("%a %d %b %Y at %H:%M:%S"))
    #@+node:ekr.20160316091132.100: *3* mcs.run
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
                        self.make_coffeescript_file(fn)
                else:
                    print('output directory not found: %s' % dir_)
            else:
                print('no output directory')
        elif not self.enable_unit_tests:
            print('no input files')
    #@+node:ekr.20160316091132.101: *3* mcs.run_all_unit_tests
    def run_all_unit_tests(self):
        '''Run all unit tests in the python-to-coffeescript/test directory.'''
        import unittest
        loader = unittest.TestLoader()
        suite = loader.discover(os.path.abspath('.'),
                                pattern='test*.py',
                                top_level_dir=None)
        unittest.TextTestRunner(verbosity=1).run(suite)
    #@+node:ekr.20160316091132.102: *3* mcs.scan_command_line
    def scan_command_line(self):
        '''Set ivars from command-line arguments.'''
        # This automatically implements the --help option.
        usage = "usage: python_to_coffeescript.py [options] file1, file2, ..."
        parser = optparse.OptionParser(usage=usage)
        add = parser.add_option
        add('-c', '--config', dest='fn',
            help='full path to configuration file')
        add('-d', '--dir', dest='dir',
            help='full path to the output directory')
        add('-o', '--overwrite', action='store_true', default=False,
            help='overwrite existing .coffee files')
        # add('-t', '--test', action='store_true', default=False,
            # help='run unit tests on startup')
        add('-v', '--verbose', action='store_true', default=False,
            help='verbose output')
        # Parse the options
        options, args = parser.parse_args()
        # Handle the options...
        # self.enable_unit_tests = options.test
        self.overwrite = options.overwrite
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
    #@+node:ekr.20160316091132.103: *3* mcs.scan_options & helpers
    def scan_options(self):
        '''Set all configuration-related ivars.'''
        if not self.config_fn:
            return
        self.parser = parser = self.create_parser()
        s = self.get_config_string()
        self.init_parser(s)
        if self.files:
            # files_source = 'command-line'
            files = self.files
        elif parser.has_section('Global'):
            # files_source = 'config file'
            files = parser.get('Global', 'files')
            files = [z.strip() for z in files.split('\n') if z.strip()]
        else:
            return
        files2 = []
        for z in files:
            files2.extend(glob.glob(self.finalize(z)))
        self.files = [z for z in files2 if z and os.path.exists(z)]
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
            # The parser does not preserve leading whitespace.
            prefix = parser.get('Global', 'prefix_lines')
            self.prefix_lines = prefix.split('\n')
        #
        # self.def_patterns = self.scan_patterns('Def Name Patterns')
        # self.general_patterns = self.scan_patterns('General Patterns')
        # self.make_patterns_dict()
    #@+node:ekr.20160316091132.104: *4* mcs.create_parser
    def create_parser(self):
        '''Create a RawConfigParser and return it.'''
        parser = configparser.RawConfigParser()
        parser.optionxform = str
        return parser
    #@+node:ekr.20160316091132.105: *4* mcs.get_config_string
    def get_config_string(self):
        fn = self.finalize(self.config_fn)
        if os.path.exists(fn):
            if self.verbose:
                print('\nconfiguration file: %s\n' % fn)
            f = open(fn, 'r')
            s = f.read()
            f.close()
            return s
        print('\nconfiguration file not found: %s' % fn)
        return ''
    #@+node:ekr.20160316091132.106: *4* mcs.init_parser
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
    #@+node:ekr.20160316091132.107: *4* mcs.is_section_name
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
    #@-others
#@+node:ekr.20160316091132.108: ** class ParseState
class ParseState:
    '''A class representing items parse state stack.'''

    def __init__(self, kind, value):
        self.kind = kind
        self.value = value

    def __repr__(self):
        return 'State: %10s %s' % (self.kind, repr(self.value))

    __str__ = __repr__
#@+node:ekr.20160316091132.109: ** class TokenSync
class TokenSync:
    '''A class to sync and remember tokens.'''
    # To do: handle comments, line breaks...
    #@+others
    #@+node:ekr.20160316091132.110: *3*  ts.ctor & helpers
    def __init__(self, s, tokens):
        '''Ctor for TokenSync class.'''
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
    #@+node:ekr.20160316091132.111: *4* ts.make_blank_lines
    def make_blank_lines(self):
        '''Return of list of line numbers of blank lines.'''
        result = []
        for i, aList in enumerate(self.line_tokens):
            # if any([self.token_kind(z) == 'nl' for z in aList]):
            if len(aList) == 1 and self.token_kind(aList[0]) == 'nl':
                result.append(i)
        return result
    #@+node:ekr.20160316091132.112: *4* ts.make_ignored_lines
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
    #@+node:ekr.20160316091132.113: *4* ts.make_line_tokens (trace tokens)
    def make_line_tokens(self, tokens):
        '''
        Return a list of lists of tokens for each list in self.lines.
        The strings in self.lines may end in a backslash, so care is needed.
        '''
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
        assert len(self.lines) + 1 == len(result), len(result)
        return result
    #@+node:ekr.20160316091132.114: *4* ts.make_nl_token
    def make_nl_token(self):
        '''Return a newline token with '\n' as both val and raw_val.'''
        t1 = token_module.NEWLINE
        t2 = '\n'
        t3 = (0, 0)  # Not used.
        t4 = (0, 0)  # Not used.
        t5 = '\n'
        return t1, t2, t3, t4, t5
    #@+node:ekr.20160316091132.115: *4* ts.make_string_tokens
    def make_string_tokens(self):
        '''Return a copy of line_tokens containing only string tokens.'''
        result = []
        for aList in self.line_tokens:
            result.append([z for z in aList if self.token_kind(z) == 'string'])
        assert len(result) == len(self.line_tokens)
        return result
    #@+node:ekr.20160316091132.116: *3* ts.check_strings
    def check_strings(self):
        '''Check that all strings have been consumed.'''
        for i, aList in enumerate(self.string_tokens):
            if aList:
                g.trace('warning: line %s. unused strings' % i)
                for z in aList:
                    print(self.dump_token(z))
    #@+node:ekr.20160316091132.117: *3* ts.dump_token
    def dump_token(self, token, verbose=False):
        '''Dump the token. It is either a string or a 5-tuple.'''
        if isinstance(token, str):
            return token
        t1, t2, t3, t4, t5 = token
        kind = g.toUnicode(token_module.tok_name[t1].lower())
        # raw_val = g.toUnicode(t5)
        val = g.toUnicode(t2)
        return 'token: %10s %r' % (kind, val) if verbose else val
    #@+node:ekr.20160316091132.118: *3* ts.is_line_comment
    def is_line_comment(self, token):
        '''Return True if the token represents a full-line comment.'''
        t1, t2, t3, t4, t5 = token
        kind = token_module.tok_name[t1].lower()
        raw_val = t5
        return kind == 'comment' and raw_val.lstrip().startswith('#')
    #@+node:ekr.20160316091132.119: *3* ts.join
    def join(self, aList, sep=','):
        '''return the items of the list joined by sep string.'''
        tokens = []
        for i, token in enumerate(aList or []):
            tokens.append(token)
            if i < len(aList) - 1:
                tokens.append(sep)
        return tokens
    #@+node:ekr.20160316091132.120: *3* ts.last_node
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

    #@+node:ekr.20160316091132.121: *3* ts.leading_lines
    def leading_lines(self, node):
        '''Return a list of the preceding comment and blank lines'''
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
    #@+node:ekr.20160316091132.122: *3* ts.leading_string
    def leading_string(self, node):
        '''Return a string containing all lines preceding node.'''
        return ''.join(self.leading_lines(node))
    #@+node:ekr.20160316091132.123: *3* ts.line_at
    def line_at(self, node, continued_lines=True):
        '''Return the lines at the node, possibly including continuation lines.'''
        n = getattr(node, 'lineno', None)
        if n is None:
            return '<no line> for %s' % node.__class__.__name__
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
    #@+node:ekr.20160316091132.124: *3* ts.sync_string
    def sync_string(self, node):
        '''Return the spelling of the string at the given node.'''
        n = node.lineno
        tokens = self.string_tokens[n - 1]
        if tokens:
            token = tokens.pop(0)
            self.string_tokens[n - 1] = tokens
            return self.token_val(token)
        g.trace('===== underflow line:', n, node.s)
        return node.s
    #@+node:ekr.20160316091132.125: *3* ts.token_kind/raw_val/val
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
    #@+node:ekr.20160316091132.126: *3* ts.tokens_for_statement
    def tokens_for_statement(self, node):

        assert isinstance(node, ast.AST), node
        name = node.__class__.__name__
        if hasattr(node, 'lineno'):
            tokens = self.line_tokens[node.lineno - 1]
            g.trace(' '.join([self.dump_token(z) for z in tokens]))
        else:
            g.trace('no lineno', name)



    #@+node:ekr.20160316091132.127: *3* ts.trailing_comment
    def trailing_comment(self, node):
        '''
        Return a string containing the trailing comment for the node, if any.
        The string always ends with a newline.
        '''
        if hasattr(node, 'lineno'):
            return self.trailing_comment_at_lineno(node.lineno)
        return '\n'
    #@+node:ekr.20160316091132.128: *3* ts.trailing_comment_at_lineno
    def trailing_comment_at_lineno(self, lineno):
        '''Return any trailing comment at the given node.lineno.'''
        tokens = self.line_tokens[lineno - 1]
        for token in tokens:
            if self.token_kind(token) == 'comment':
                raw_val = self.token_raw_val(token).rstrip()
                if not raw_val.strip().startswith('#'):
                    val = self.token_val(token).rstrip()
                    s = ' %s\n' % val
                    return s
        return '\n'
    #@+node:ekr.20160316091132.129: *3* ts.trailing_lines
    def trailing_lines(self):
        '''return any remaining ignored lines.'''
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
    #@-others
#@-others

g = LeoGlobals()  # For ekr.
if __name__ == "__main__":
    main()
# A final comment for testing.
#@-leo

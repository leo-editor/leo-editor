#!/usr/bin/env python

'''
The stand-alone version of Leo's make-stub-files command.

This file is in the public domain.

**In brief**

This script makes a stub file in the ~/stubs directory for every file
mentioned in the [Files] section of ~/stubs/make_stub_files.cfg. The
[Global] section specifies output directory, prefix lines and annotation
pairs.

**In detail**

This docstring documents the make_stub_files.py script, explaining what it
does, how it works and why it is important.

Executive summary
=================

The make_stub_files script eliminates much of the drudgery of creating
python stub (.pyi) files https://www.python.org/dev/peps/pep-0484/#stub-files
from python source files. To my knowledge, no such tool presently exists.

The script does no type inference. Instead, it creates function annotations
using user-supplied **type conventions**, pairs of strings of the form
"name: type-annotation".

A **configuration file**, ~/stubs/make_stub_files.cfg, specifies the
**source list**, (a list files to be processed), the type conventions, and
a list of **prefix lines** to be inserted verbatim at the start of each
stub file.

This script should encourage more people to use mypy. Stub files can be
used by people using Python 2.x code bases. As discussed below, stub files
can be thought of as design documents or as executable and checkable design
tools.

What the script does
====================

For each file in source list (file names may contain wildcards), the script
creates a corresponding stub file in the ~/stubs directory. This is the
default directory for mypy stubs. For each source file, the script does the
following:

1. The script writes the prefix lines verbatim. This makes it easy to add
   common code to the start of stub files. For example::

    from typing import TypeVar, Iterable, Tuple
    T = TypeVar('T', int, float, complex)
    
2. The script walks the parse (ast) tree for the source file, generating
   stub lines for each function, class or method. The script generates no
   stub lines for defs nested within other defs.

For example, given the naming conventions::

    aList: Sequence
    i: int
    c: Commander
    s: str
    
and a function::

    def scan(s, i, x):
        whatever
        
the script will generate::

    def scan(s: str, i:int, x): --> (see below):
    
Handling function returns
=========================
    
The script handles function returns pragmatically. The tree walker simply
writes a list of return expressions for each def. For example, here is the
output at the start of leoAst.pyi::

    class AstDumper:
        def dump(self, node: ast.Ast, level=number) -> 
            repr(node), 
            str%(name,sep,sep1.join(aList)), 
            str%(name,str.join(aList)), 
            str%str.join(str%(sep,self.dump(z,level+number)) for z in node): ...
        def get_fields(self, node: ast.Ast) -> result: ...
        def extra_attributes(self, node: ast.Ast) -> Sequence: ...

The stub for the dump function is not syntactically correct because there
are 4 returns listed. You must edit stubs to specify a proper return type.
For the dump method, all the returns are obviously strings, so its stub
should be::

    def dump(self, node: ast.Ast, level=number) -> str: ...

Not all types are obvious from naming conventions. In that case, the human
will have to update the stub using the actual source code as a guide. For
example, the type of "result" in get_fields could be just about anything.
In fact, it is a list of strings.

The configuration file
======================

As mentioned above, the configuration file, make_stub_files.cfg, is located
in the ~/stubs directory. This is mypy's default directory for stubs.

The configuration file uses the .ini format. It has two sections:

- The [Global] section specifies the files list, prefix lines and output directory:

- The [Types] section specifies naming conventions. For example::

    [Global]
    files:
        ~/leo-editor/leo/core/*.py
        
    output_directory: ~/stubs
        
    prefix:
        from typing import TypeVar, Iterable, Tuple
        T = TypeVar('T', int, float, complex)

    [Types]
    aList: Sequence
    c: Commander
    i: int
    j: int
    k: int
    n: int
    node: ast.Ast
    p: Position
    result: str
    s: str
    v: VNode

Why this script is important
===========================

The script eliminates most of the drudgery from creating stub files.
Creating a syntactically correct stub file from the output of the script is
straightforward.

Stub files are real data. mypy will check the syntax for us. More
importantly, mypy will do its type inference on the stub files. That means
that mypy will discover both errors in the stubs and actual type errors in
the program under test. There is now a simple way to use mypy!

Stubs express design intentions and intuitions as well as types. We
programmers think we *do* know most of the types of arguments passed into
and out of functions and methods. Up until now, there has been no practical
way of expressing and *testing* these assumptions. Using mypy, we can be as
specific as we like about types. For example, we can simply say that d is a
dict, or we can say that d is a dict whose keys are strings and whose
values are executables with a union of possible signatures. In short, stubs
are the easy way to play with type inference.

Most importantly, from my point of view, stub files clarify issues that I
have been struggling with for many years. To what extent *do* we understand
types? mypy will tell us. How dynamic (RPython-like) *are* our programs?
mypy will tell us. Could we use type annotation to convert our programs to
C. Heh, not likely, but the data in the stubs will tell where things get
sticky.

Finally, stubs can simplify the general type inference problem. Without
type hints or annotations, the type of everything depends on the type of
everything else. Stubs could allow robust, maybe even complete, type
inference to be done locally. We might expect stubs to make mypy work
faster.

Summary
=======

The make-stub-files script does for type/design analysis what Leo's c2py
command did for converting C sources to python. It eliminates much of the
drudgery associated with creating stub files, leaving the programmer to
make non-trivial inferences.

Stub files allow us to explore type checking using mypy as a guide and
helper. Stub files are both a design document and an executable, checkable,
type specification. Stub files allow those with a Python 2 code base to use
mypy.

The make-stub-files script is useful as is. All contributions are
gratefully accepted.

One could imagine a similar insert_annotations script that would inject
function annotations into source files using stub files as data. This
"reverse" script should be about as straightfoward as the make-stub-files
script.

Edward K. Ream
January, 2016
'''

import ast
try:
    import ConfigParser as configparser # Python 2
except ImportError:
    import configparser # Python 3
import glob
import os
import sys


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
            assert type(s) == type('abc'), type(s)
            return s

    # Contexts...

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
        gens = [z if z else '<**None**>' for z in gens] ### Kludge: probable bug.
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

    # Python 3:
    # arg = (identifier arg, expr? annotation)

    def do_arg(self, node):
        if node.annotation:
            return self.visit(node.annotation)
        else:
            return ''

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
        gens = [z if z else '<**None**>' for z in gens] ### Kludge: probable bug.
        return '%s for %s' % (elt, ''.join(gens))

    def do_Name(self, node):
        return node.id

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
        return '(%s)' % ','.join(elts)

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
                self.visit(node.value)))
        else:
            return self.indent('return\n')

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


class StandAloneMakeStubFile:
    '''
    A class to make Python stub (.pyi) files in the ~/stubs directory for
    every file mentioned in the [Source Files] section of
    ~/stubs/make_stub_files.cfg.
    '''

    def __init__ (self):
        '''Ctor for StandAloneMakeStubFile class.'''
        self.d = {}
        self.files = []
        self.options = {}
        self.output_directory = os.path.expanduser('~/stubs')
        self.prefix_lines = []

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
        out_fn = os.path.join(self.output_directory,base_fn)
        out_fn = out_fn[:-3] + '.pyi'
        out_fn = os.path.normpath(out_fn)
        s = open(fn).read()
        node = ast.parse(s,filename=fn,mode='exec')
        StubTraverser(self.d, self.prefix_lines, out_fn).run(node)

    def run(self):
        '''Make stub files for all files.'''
        if os.path.exists(self.output_directory):
            for fn in self.files:
                self.make_stub_file(fn)

    def scan_options(self):
        '''Set all configuration-related ivars.'''
        parser = configparser.ConfigParser()
        parser.optionxform=str
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
            # print('Files...\n%s' % '\n'.join(self.files))
            if 'output_directory' in parser.options('Global'):
                s = parser.get('Global', 'output_directory')
                output_dir = os.path.expanduser(s)
                if os.path.exists(output_dir):
                    self.output_directory = output_dir
                    print('output_dir: %s' % self.output_directory)
                else:
                    print('output_dir not found: %s' % self.output_directory)
                    self.output_directory = None # inhibit run().
            print('Types...')
            for key in sorted(parser.options('Types')):
                value = parser.get('Types', key)
                self.d [key] = value
                print('%s: %s' % (key, value))
            prefix = parser.get('Global','prefix')
            self.prefix_lines = [z.strip() for z in prefix.split('\n') if z.strip()]
            print('Prefix lines...')
            for z in self.prefix_lines:
                print(z)


class StubFormatter (AstFormatter):
    '''
    Just like the AstFormatter class, except it prints the class
    names of constants instead of actual values.
    '''

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


class StubTraverser (ast.NodeVisitor):
    '''An ast.Node traverser class that outputs a stub for each class or def.'''

    def __init__(self, d, prefix_lines, output_fn):
        '''Ctor for StubTraverser class.'''
        self.d = d
        self.format = StubFormatter().format
        self.in_function = False
        self.level = 0
        self.output_file = None
        self.output_fn = output_fn
        self.prefix_lines = prefix_lines
        self.returns = []

    def indent(self, s):
        '''Return s, properly indented.'''
        return '%s%s' % (' ' * 4 * self.level, s)

    def out(self, s):
        '''Output the string to the console or the file.'''
        if self.output_file:
            self.output_file.write(self.indent(s)+'\n')
        else:
            print(self.indent(s))

    def run(self, node):
        '''StubTraverser.run: write the stubs in node's tree to self.output_fn.'''
        fn = self.output_fn
        dir_ = os.path.dirname(fn)
        if os.path.exists(fn):
            print('file exists: %s' % fn)
        elif os.path.exists(dir_):
            self.output_file = open(fn, 'w')
            for z in self.prefix_lines or []:
                self.out(z.strip())
            self.visit(node)
            self.output_file.close()
            self.output_file = None
            print('wrote: %s' % fn)
        else:
            print('not found: %s' % dir_)


    # Visitors...

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

    # FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list)

    def visit_FunctionDef(self, node):
        
        # Do nothing if we are already in a function.
        # We do not generate stubs for inner defs.
        if self.in_function or node.name.startswith('_'):
            return
        # First, visit the function body.
        self.returns = []
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

    # arguments = (expr* args, identifier? vararg, identifier? kwarg, expr* defaults)

    def format_arguments(self, node):
        '''
        Format the arguments node.
        Similar to AstFormat.do_arguments, but it is not a visitor!
        '''
        
        def munge_arg(s):
            '''Add an annotation for s if possible.'''
            a = self.d.get(s)
            return '%s: %s' % (s, a) if a else s

        assert isinstance(node,ast.arguments), node
        args = [self.format(z) for z in node.args]
        defaults = [self.format(z) for z in node.defaults]
        # Assign default values to the last args.
        result = []
        n_plain = len(args) - len(defaults)
        # pylint: disable=consider-using-enumerate
        for i in range(len(args)):
            s = munge_arg(args[i])
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

    def format_returns(self, node):
        '''Calculate the return type.'''
        
        def split(s):
            return '\n     ' + self.indent(s) if len(s) > 30 else s
            
        def munge_ret(s):
            '''replace a return value by a type if possible.'''
            return self.d.get(s.strip()) or s

        r = [self.format(z) for z in self.returns]
        # if r: print(r)
        r = [munge_ret(z) for z in r] # Make type substitutions.
        r = sorted(set(r)) # Remove duplicates
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

    def visit_Return(self, node):

        self.returns.append(node.value)

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

if __name__ == "__main__":
    main()

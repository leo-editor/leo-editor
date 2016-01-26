#!/usr/bin/env python

'''
The stand-alone version of Leo's make-stub-files command.

This file is in the public domain.

This docstring documents the make_stub_files.py script, explaining what it
does, how it works and why it is important.

**In brief**

This script makes a stub (.pyi) file in the **output directory** for each
source file listed on the command line (wildcard file names are supported).

A **configuration file** (default: ~/stubs/make_stub_files.cfg) specifies
annotation pairs and various **patterns** to be applied to return values.
The configuration file can also supply a list of **prefix lines** to be
inserted verbatim at the start of each stub file.

Command-line arguments can override the locations of the configuration file
and output directory. The configuration file can supply default source
files to be used if none are supplied on the command line.

This script never creates directories automatically, nor does it overwrite
stub files unless the --overwrite command-line option is in effect.

**In detail**

Executive summary
=================

The make_stub_files script eliminates much of the drudgery of creating
python stub (.pyi) files https://www.python.org/dev/peps/pep-0484/#stub-files
from python source files. 

From GvR::

    "We actually do have a stub generator as part of mypy now (most of the
    code is in https://github.com/JukkaL/mypy/blob/master/mypy/stubgen.py;
    it has a few options) but yours has the advantage of providing a way to
    tune the generated signatures based on argument conventions. This
    allows for a nice iterative way of developing stubs."

The script does no type inference. Instead, it creates function annotations
using user-supplied **type conventions**, pairs of strings of the form
"name: type-annotation".  As described below, the script simplifies return
values using several different kinds of user-supplied **patterns**.

This script should encourage more people to use mypy. Stub files can be
used by people using Python 2.x code bases. As discussed below, stub files
can be thought of as design documents or as executable and checkable design
tools.

What the script does
====================

This script makes a stub (.pyi) file in the **output directory** for each
source file listed on the command line (wildcard file names are supported).

For each source file, the script does the following:

1. The script writes the prefix lines verbatim. This makes it easy to add
   common code to the start of stub files. For example::

    from typing import TypeVar, Iterable, Tuple
    T = TypeVar('T', int, float, complex)
    
2. The script walks the parse (ast) tree for the source file, generating
   stub lines for each function, class or method. The script generates no
   stub lines for defs nested within other defs. Return values are handled
   in a clever way as described below.

For example, given the naming conventions::

    aList: Sequence
    i: int
    c: Commander
    s: str
    
and a function::

    def scan(s, i, x):
        whatever
        
the script will generate::

    def scan(s: str, i:int, x): --> (see next section):
    
Handling function returns
=========================
    
The script handles function returns pragmatically. The tree walker simply
writes a list of return expressions for each def. For example, here is the
*default* output at the start of leoAst.pyi, before any patterns are applied::

    class AstDumper:
        def dump(self, node: ast.Ast, level=number) -> 
            repr(node), 
            str%(name,sep,sep1.join(aList)), 
            str%(name,str.join(aList)), 
            str%str.join(str%(sep,self.dump(z,level+number)) for z in node): ...
        def get_fields(self, node: ast.Ast) -> result: ...
        def extra_attributes(self, node: ast.Ast) -> Sequence: ...
        
The stub for the dump function is not syntactically correct because there
are four returns listed. As discussed below, the configuration file can
specify several kinds of patterns to be applied to return values.

**These patterns often suffice to collapse all return values** In fact,
just a few patterns (given below) will convert::

    def dump(self, node: ast.Ast, level=number) -> 
        repr(node), 
        str%(name,sep,sep1.join(aList)), 
        str%(name,str.join(aList)), 
        str%str.join(str%(sep,self.dump(z,level+number)) for z in node): ...
        
to:

    def dump(self, node: ast.Ast, level=number) -> str: ... 

If multiple return values still remain after applying all patterns, you
must edit stubs to specify a proper return type. And even if only a single
value remains, its "proper" value may not obvious from naming conventions.
In that case, you will have to update the stub using the actual source code
as a guide.

The configuration file
======================

As mentioned above, the configuration file, make_stub_files.cfg, is located
in the ~/stubs directory. This is mypy's default directory for stubs.

The configuration file uses the .ini format. It has the following sections,
all optional.

The [Global] section
--------------------

This configuration section specifies the files list, prefix lines and
output directory. For example::

    [Global]

    files:
        # Files to be used *only* if no files are given on the command line.
        # glob.glob wildcards are supported.
        ~/leo-editor/leo/core/*.py
        
    output_directory:
        # The output directory to be used if no --dir option is given.
        ~/stubs
        
    prefix:
        # Lines to be inserted at the start of each stub file.
        from typing import TypeVar, Iterable, Tuple
        T = TypeVar('T', int, float, complex)
        
The [Arg Types] section
-----------------------

This configuration section specifies naming conventions. These conventions
are applied to *both* argument lists *and* return values.
  
- For argument lists, the replacement becomes the annotation.
- For return values, the replacement *replaces* the pattern.

For example::

    [Arg Types]

    # Lines have the form:
    #   verbatim-pattern: replacement
    
    aList: Sequence
    aList2: Sequence
    c: Commander
    i: int
    j: int
    k: int
    node: ast.Ast
    p: Position
    s: str
    s2: str
    v: VNode
    
The [Def Name Patterns] section
-------------------------------

This configuration specifies the *final* return value to be associated with
functions or methods. The pattern is a regex matching the names of defs.
Methods names should have the form class_name.method_name. No further
pattern matching is done if any of these patterns match. For example::

    [Def Name Patterns]

    # These  patterns are matched *before* the patterns in the
    # [Return Balanced Patterns] and [Return Regex Patterns] sections.
    
    AstFormatter.do_.*: str
    StubTraverser.format_returns: str
    StubTraverser.indent: str
    
The [Return Balanced Patterns] section
--------------------------------------

This configuration section gives **balanced patterns** to be applied to
return values. Balanced patterns match verbatim, except that the three
patterns:
  
  (*), [*], and {*} 
    
match only *balanced* parens, square and curly brackets.

Return values are rescanned until no more balanced patterns apply. Balanced
patterns are *much* simpler to use than regex's. Indeed, the following
balanced patterns suffice to collapse most string expressions to str::

    [Return Balanced Patterns]

    repr(*): str
    str.join(*): str
    str.replace(*): str
    str%(*): str
    str%str: str
    
The [Return Regex Patterns] section
-----------------------------------
    
This configuration section gives regex patterns to be applied to return
values. These patterns are applied last, after all other patterns have been
applied.
  
Again, these regex patterns are applied repeatedly until no further
replacements are possible. For example::

    [Return Regex Patterns]

    .*__name__: str
    
Important note about pattern matching
-------------------------------------

The patterns in the [Return Balanced Patterns] and [Return Regex Patterns]
sections are applied to each individual return value separately. Comments
never appear in return values, and all strings in return values appear as
str. As a result, there is no context to worry about and very short
patterns suffice.

Command-line arguments
======================

There is the output of `python make_stub_files.py -h`::

    Usage: make_stub_files.py [options] file1, file2, ...
    
    Options:
      -h, --help          show this help message and exit
      -c FN, --config=FN  full path to alternate configuration file
      -d DIR, --dir=DIR   full path to the output directory
      -o, --overwrite     overwrite existing stub (.pyi) files
      -t, --trace         trace argument substitutions
      -v, --verbose       trace configuration settings
      
*Note*: glob.blob wildcards can be used in file1, file2, ...

Why this script is important
===========================

The script eliminates most of the drudgery from creating stub files.
Creating a syntactically correct stub file from the output of the script is
straightforward:

**Just a few patterns will collapse most return values to a single value.**

Stub files are real data. mypy will check the syntax for us. More
importantly, mypy will do its type inference on the stub files. That means
that mypy will discover both errors in the stubs and actual type errors in
the program under test. There is now an easy way to use mypy!

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

One could imagine a similar insert_annotations script that would inject
function annotations into source files using stub files as data. The
"reverse" script should be more straightfoward than this script.

Edward K. Ream
January 2016
'''

import ast
try:
    import ConfigParser as configparser # Python 2
except ImportError:
    import configparser # Python 3
import glob
import optparse
import os
import re
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
        self.options = {}
        # Ivars set on the command line...
        self.config_fn = os.path.normpath(os.path.expanduser(
            '~/stubs/make_stub_files.cfg'))
        self.files = [] # May also be set in the config file.
        self.trace = False # Trace pattern substitutions.
        self.verbose = False # Trace config arguments.
        # Ivars set in the config file...
        self.output_fn = None
        self.output_directory = os.path.normpath(os.path.expanduser('~/stubs'))
        self.overwrite = False
        self.prefix_lines = []
        # Type substitution dicts, set by config sections...
        self.args_d = {} # [Arg Types]
        self.def_pattern_d = {} # [Def Name Patterns]
        self.return_regex_d = {} # [Return Regex Patterns]
        self.return_pattern_d = {} # [Return Balanced Patterns]
       

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
        self.output_fn = os.path.normpath(out_fn)
        s = open(fn).read()
        node = ast.parse(s,filename=fn,mode='exec')
        dicts = (self.args_d, self.def_pattern_d, self.return_pattern_d)
        StubTraverser(controller=self).run(node)

    def run(self):
        '''Make stub files for all files.'''
        if os.path.exists(self.output_directory):
            for fn in self.files:
                self.make_stub_file(fn)

    def scan_command_line(self):
        '''Set ivars from command-line arguments.'''
        # print('scan_command_line sys.argv: %s' % sys.argv)
        # This automatically implements the --help option.
        usage = "usage: make_stub_files.py [options] file1, file2, ..."
        parser = optparse.OptionParser(usage=usage)
        add = parser.add_option
        add('-c', '--config', dest='fn',
            help='full path to alternate configuration file')
        add('-d', '--dir', dest='dir',
            help='full path to the output directory')
        add('-o', '--overwrite', action='store_true', default=False,
            help='overwrite existing stub (.pyi) files')
        add('-t', '--trace', action='store_true', default=False,
            help='trace argument substitutions')
        add('-v', '--verbose', action='store_true', default=False,
            help='trace configuration settings')
        # Parse the options
        options, args = parser.parse_args()
        # print('scan_command_line args: %s' % args)
        # Handle the options...
        self.trace = self.trace or options.trace
        self.overwrite = options.overwrite
        self.verbose = self.verbose or options.verbose
        if options.fn:
            self.config_fn = options.fn
        if options.dir:
            dir_ = options.dir
            dir_ = os.path.normpath(os.path.expanduser(dir_))
            if os.path.exists(dir_):
                self.output_directory = dir_
            else:
                print('--dir: does not exist: %s, using %s' % (
                    dir_, self.output_directory))
        # If any files remain, set self.files.
        if args:
            args = [os.path.normpath(os.path.expanduser(z)) for z in args]
            # args = [z for z in args if os.path.exists(z)]
            if args:
                self.files = args
            # print('command-line files: %s' % args)

    def scan_options(self):
        '''Set all configuration-related ivars.'''
        verbose = self.verbose
        parser = configparser.ConfigParser()
        parser.optionxform=str
        fn = os.path.expanduser(self.config_fn)
        fn = os.path.normpath(fn)
        if not os.path.exists(fn):
            print('not found: %s' % fn)
            return
        if verbose: print('\nconfiguration file: %s\n' % fn)
        parser.read(fn)
        if self.files:
            # if verbose: print('using command-line files')
            files2 = []
            for z in self.files:
                files2.extend(glob.glob(os.path.expanduser(z)))
            # self.files = [z for z in files2 if os.path.exists(z)]
            self.files = files2
            if verbose:
                print('Files...\n')
                for z in self.files:
                    print(z)
                print('')
        else:
            files = parser.get('Global', 'files')
            files = [z.strip() for z in files.split('\n') if z.strip()]
            files2 = []
            for z in files:
                files2.extend(glob.glob(os.path.expanduser(z)))
            self.files = [z for z in files2 if os.path.exists(z)]
            # print('Files...\n%s' % '\n'.join(self.files))
        if 'output_directory' in parser.options('Global'):
            s = parser.get('Global', 'output_directory')
            output_dir = os.path.normpath(os.path.expanduser(s))
            if os.path.exists(output_dir):
                self.output_directory = output_dir
                if verbose:
                    print('output_dir: %s\n' % self.output_directory)
            else:
                if verbose:
                    print('output_dir not found: %s\n' % self.output_directory)
                self.output_directory = None # inhibit run().
        if 'prefix_lines' in parser.options('Global'):
            prefix = parser.get('Global','prefix_lines')
            self.prefix_lines = [z.strip() for z in prefix.split('\n') if z.strip()]
            if verbose:
                print('Prefix lines...\n')
                for z in self.prefix_lines:
                    print(z)
                print('')
        self.args_d = self.scan_types(
            parser, 'Arg Types')
        self.def_pattern_d = self.scan_types(
            parser, 'Def Name Patterns', )
        self.return_pattern_d = self.scan_types(
            parser, 'Return Balanced Patterns')
        self.return_regex_d = self.scan_types(
            parser, 'Return Regex Patterns')

    def scan_types(self, parser, section_name):
        
        verbose = self.verbose
        d = {}
        if section_name in parser.sections():
            if verbose: print('%s...\n' % section_name)
            for key in sorted(parser.options(section_name)):
                value = parser.get(section_name, key)
                d [key] = value
                if verbose: print('%s: %s' % (key, value))
            if verbose: print('')
        elif verbose:
            print('no section: %s' % section_name)
            print(parser.sections())
            print('')
        return d


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

    def __init__(self, controller):
        '''Ctor for StubTraverser class.'''
        self.controller = c = controller
            # A StandAloneMakeStubFile instance.
        # Internal state ivars...
        self.class_name_stack = []
        self.format = StubFormatter().format
        self.in_function = False
        self.level = 0
        self.output_file = None
        self.returns = []
        # Copies of controller ivars...
        self.output_fn = c.output_fn
        self.overwrite = c.overwrite
        self.prefix_lines = c.prefix_lines
        self.trace = c.trace
        self.verbose = c.verbose
        # Copies of controller dicts...
        self.args_d = c.args_d # [Arg Types]
        self.def_pattern_d = c.def_pattern_d # [Def Name Patterns]
        self.return_regex_d = c.return_regex_d # [Return Regex Patterns]
        self.return_pattern_d = c.return_pattern_d # [Return Balanced Patterns]

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
        if os.path.exists(fn) and not self.overwrite:
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
        self.class_name_stack.append(node.name)
        for z in node.body:
            self.visit(z)
        self.class_name_stack.pop()
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

    def format_returns(self, node):
        '''Calculate the return type.'''
        
        def split(s):
            return '\n     ' + self.indent(s) if len(s) > 30 else s
            
        # Shortcut everything if node.name matches any
        # pattern in self.def_pattern_d.
        trace = self.trace
        d = self.def_pattern_d
        if self.class_name_stack:
            name = '%s.%s' % (self.class_name_stack[-1], node.name)
        else:
            name = node.name
        for pattern in d.keys():
            match = re.search(pattern, name)
            if match and match.group(0) == name:
                t = d.get(pattern)
                if trace: print('*name pattern %s: %s -> %s' % (pattern, name, t))
                return t

        r = [self.format(z) for z in self.returns]
        # if r: print(r)
        r = [self.munge_ret(name, z) for z in r]
            # Make type substitutions.
        r = sorted(set(r))
            # Remove duplicates
        if len(r) == 0:
            return 'None'
        if len(r) == 1:
            return r[0] # Never split a single value.
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

    def munge_arg(self, s):
        '''Add an annotation for s if possible.'''
        a = self.args_d.get(s)
        return '%s: %s' % (s, a) if a else s

    def munge_ret(self, name, s):
        '''replace a return value by a type if possible.'''
        trace = self.trace
        if trace: print('munge_ret ==== %s' % name)
        s = self.match_args(name, s)
            # Do matches in [Arg Types]
        s = self.match_balanced_patterns(name, s)
            # Repeatedly do all matches in [Return Balance Patterns]
        s = self.match_regex_patterns(name, s)
            # Repeatedly do all matches in [Return Regex Patterns]
        if trace: print('munge_reg -----: %s' % s)
        return s

    def match_args(self, name, s):
        '''In s, make substitutions (word only) given in [Arg Types].'''
        trace = self.trace
        d = self.args_d
        count = 0 # prevent any possibility of endless loops
        found = True
        while found and count < 40:
            found = False
            for arg in d.keys():
                match = re.search(r'\b'+arg+r'\b', s)
                if match:
                    i = match.start(0)
                    t = d.get(arg)
                    s2 = s[:i] + t + s[i + len(arg):]
                    if trace:
                        print('arg:  %s %s ==> %s' % (arg, s, s2))
                    s = s2
                    count += 1
                    found = True
        return s

    def match_balanced_patterns(self, name, s):
        '''
        In s, do *all* subsitutions given in [Return Balanced Patterns].
        
        All characters match verbatim, except that the patterns:
            (*), [*] and {*}
        match only *balanced* parens, square and curly brackets.
        
        Note: No special cases are needed for strings or comments.
        Comments do not appear, and strings have been converted to "str".
        '''
        trace = self.trace
        if trace: print('----- %s' % s)
        count, found = 0, True
        while found and count < 40:
            count += 1
            found, i, s1 = False, 0, s
            while i < len(s) and not found:
                s = self.match_return_patterns(name, s, i)
                found = s1 != s
                i += 1
        if trace: print('*after balanced patterns: %s' % s)
        return s

    def match_return_patterns(self, name, s, i):
        '''
        Make all possible pattern matches at s[i:]. Return the new s.
        '''
        trace = self.trace
        d = self.return_pattern_d
        s1 = s
        for pattern in d.keys():
            found_s = self.match_return_pattern(pattern, s, i)
            if found_s:
                replace_s = d.get(pattern)
                s = s[:i] + replace_s + s[i+len(found_s):]
                if trace:
                    print('match_return_patterns found: %s replace: %s' % (
                        found_s, replace_s))
                    print('match_return_patterns old: %s' % s1)
                    print('match_return_patterns new: %s' % s)
                break # must rescan the entire string.
        return s

    def match_return_pattern(self, pattern, s, i):
        '''Return the actual string matching the pattern at s[i:] or None.'''
        trace = self.trace
        i1 = i
        j = 0 # index into pattern
        while i < len(s) and j < len(pattern) and s[i] == pattern[j]:
            if pattern[j:j+3] in ('(*)', '[*]', '{*}'):
                delim = pattern[j]
                i = self.match_balanced(delim, s, i)
                j += 3
            else:
                i += 1
                j += 1
        if trace and i <= len(s) and j == len(pattern):
            print('match_return_pattern: match %s -> %s' % (pattern, s[i1:i]))
        return s[i1:i] if i <= len(s) and j == len(pattern) else None

    def match_balanced(self, delim, s, i):
        '''
        Scan over the python expression at s[i:] that starts with '(', '[' or '{'.
        Return the index into s of the end of the expression, or len(s)+1 on errors.
        '''
        trace = self.trace
        assert s[i] == delim, s[i]
        assert delim in '([{'
        delim2 = ')]}'['([{'.index(delim)]
        assert delim2 in ')]}'
        i1, level = i, 0
        while i < len(s):
            ch = s[i]
            i += 1
            if ch == delim:
                level += 1
            elif ch == delim2:
                level -= 1
                if level == 0:
                    if trace: print('match_balanced: found: %s' % s[i1:i])
                    return i
        # Unmatched
        print('***** unmatched %s in %s' % (delim, s))
        return len(s) + 1

    def match_regex_patterns(self, name, s):
        '''
        In s, repeatedly match regex patterns in [Return Regex Patterns].
        '''
        trace = self.trace
        d, prev_s = self.return_regex_d, set()
        while True:
            found = False
            for pattern in d.keys():
                match = re.search(pattern, s)
                if match:
                    t = d.get(pattern)
                    s2 = s.replace(match.group(0), t)
                    if trace:
                        print('match: %s=%s->%s: %s ==> %s' % (
                            pattern, match.group(0), t, s, s2))
                    if s2 in prev_s:
                        # A strange loop. return s2.
                        if trace: print('seen: %s' % (s2))
                        s = s2
                        found = False
                        break
                    else:
                        found = True
                        prev_s.add(s2)
                        s = s2
            if not found:
                break
        return s

    def visit_Return(self, node):

        self.returns.append(node.value)

def main():
    '''
    The driver for the stand-alone version of make-stub-files.
    All options come from ~/stubs/make_stub_files.cfg.
    '''
    controller = StandAloneMakeStubFile()
    controller.scan_command_line()
    controller.scan_options()
    controller.run()
    print('done')

if __name__ == "__main__":
    main()

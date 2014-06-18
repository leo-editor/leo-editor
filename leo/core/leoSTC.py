# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20140526082700.17153: * @file leoSTC.py
#@@first
'''
Parsing/analysis classes.  Originally developed for:
https://groups.google.com/forum/?fromgroups#!forum/python-static-type-checking
'''
#@+<< copyright notices >>
#@+node:ekr.20140526082700.17154: **   << copyright notices >>
#@@nocolor-node
#@+at
# The MIT License:
# 
# Copyright (c) 2012-2013 by Edward K. Ream
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# 
# The License for the HTMLReportTraverser:
#     
# Copyright (C) 2005-2012 Paul Boddie <paul@boddie.org.uk>
# 
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 3 of the License, or (at your option) any later
# version.
# 
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
# 
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.
#@-<< copyright notices >>
#@+<< imports >>
#@+node:ekr.20140526082700.17155: **   << imports >>
import leo.core.leoGlobals as g
    
import ast
import gc
import glob
# import imp
if g.isPython3:
    import io
    StringIO = io.StringIO
else:
    import cStringIO
    StringIO = cStringIO.StringIO
import os
# import string
# import sys
import textwrap
import time
# import types
#@-<< imports >>
#@+<< naming conventions >>
#@+node:ekr.20140526082700.17156: **   << naming conventions >>
#@@nocolor-node
#@+at
# 
# The following naming conventions are used in Leo headlines
# to denote methods of classes:
# 
# bt.*:  the AstBaseTraverer class
# f.*:   the AstFormatter class.
# ft.*:  the AstFullTraverser class.
# p1.*   the P1 class.
# ssa.*  the SSA_Traverser class.
# stat.* the BaseStat class or a subclass.
#        Also: Statement_Traverser class.
# ti.*   the TypeInferer class.
# u.*:   the Utils class.
# 
# The following are used in the code itself::
# 
# cx:   a context.
# d:    a dict.
# g:    the stcglobals module here; the leoGlobals module in @test scripts.
# node: an AST (Abstract Syntax Tree) node.
# s:    a string.
# t:    A types list/set.
# z:    a local temp.
# 
# The following are obsolete::
#     
# e:    a SymbolTableEntry object.
# st:   a symbol table (for a particular context).
# stc:  The statictypechecking module.
#     
#@-<< naming conventions >>
#@+others
#@+node:ekr.20140526082700.17161: **  Base classes
#@+node:ekr.20140526082700.17162: *3*  class AstBaseTraverser
class AstBaseTraverser:
    '''The base class for all other traversers.'''
    def __init__(self):
        pass
        # A unit test now calls self.check_visitor_names().
    
    #@+others
    #@+node:ekr.20140526082700.17163: *4* bt.attribute_base
    def attribute_base(self,node):
        
        '''Return the node representing the base of the chain.
        Only 'Name' and 'Builtin' nodes represent names.
        All other chains have a base that is a constant or nameless dict, list, etc.
        '''

        trace = False
        kind = self.kind(node)
        if kind in ('Name','Builtin','Str'):
            result = node # We have found the base.
        elif kind in ('Attribute','Subscript'):
            if trace: g.trace('value: %s'% node.value)
            result = self.attribute_base(node.value)
        elif kind == 'Call':
            result = self.attribute_base(node.func)
        else:
            # The chain is rooted in a constant or nameless dict, list, etc.
            # This is not an error.
            # g.trace('*** kind: %s node: %s' % (kind,node))
            result = node
            
        if trace:
            u = Utils()
            g.trace(u.format(node),'->',u.format(result))
        return result
    #@+node:ekr.20140526082700.17164: *4* bt.attribute_target (To be deleted)
    def attribute_target(self,node):
        
        '''Return the node representing the target of the chain.
        Only 'Name' and 'Builtin' Ops represent names.'''
        
        trace = True
        kind = self.kind(node)
        if kind in ('Name','Builtin','Str'):
            result = node # We have found the target.
        elif kind == 'Attribute':
            # result = self.attribute_target(node.attr) ### Always a string.
            result = node # node.attr is the target.
        elif kind == 'Call':
            result = self.attribute_target(node.func)
        elif kind == 'Subscript':
            result = self.attribute_target(node.value)
        else:
            g.trace('can not happen',node.__class__.__name__,repr(node))
            # Don't call u.format here.
            return None
        
        if trace:
            u = Utils()
            g.trace(u.format(node),'->',u.format(result))
        return result
    #@+node:ekr.20140526082700.17165: *4* bt.check_visitor_names
    def check_visitor_names(self,silent=False):
        
        '''Check that there is an ast.AST node named x
        for all visitor methods do_x.'''
        
        #@+<< define names >>
        #@+node:ekr.20140526082700.17166: *5* << define names >>
        names = (
            'Add','And','Assert','Assign','Attribute','AugAssign','AugLoad','AugStore',
            'BinOp','BitAnd','BitOr','BitXor','BoolOp','Break',
            'Builtin', ### Python 3.x only???
            'Bytes', # Python 3.x only.
            'Call','ClassDef','Compare','Continue',
            'Del','Delete','Dict','DictComp','Div',
            'Ellipsis','Eq','ExceptHandler','Exec','Expr','Expression','ExtSlice',
            'FloorDiv','For','FunctionDef','GeneratorExp','Global','Gt','GtE',
            'If','IfExp','Import','ImportFrom','In','Index','Interactive',
            'Invert','Is','IsNot','LShift','Lambda',
            'List','ListComp','Load','Lt','LtE',
            'Mod','Module','Mult','Name','Not','NotEq','NotIn','Num',
            'Or','Param','Pass','Pow','Print',
            'RShift','Raise','Repr','Return',
            'Set','SetComp','Slice','Store','Str','Sub','Subscript','Suite',
            'Try', # Python 3.x only.
            'TryExcept','TryFinally','Tuple','UAdd','USub','UnaryOp',
            'While','With','Yield',
            # Lower case names...
            'arg',           # A valid ast.AST node: Python 3.
            'alias',         # A valid ast.AST node.
            'arguments',     # A valid ast.AST node.
            'comprehension', # A valid ast.AST node.
            'keyword',       # A valid ast.AST node(!)
                # 'keywords', # A valid field, but not a valid ast.AST node!
                # In ast.Call nodes, node.keywords points to a *list* of ast.keyword objects.
            # There is never any need to traverse these:
                # 'id','n','name','s','str'.
        )
        #@-<< define names >>
        #@+<< Py2K grammar >>
        #@+node:ekr.20140526082700.17167: *5* << Py2k grammar >>
        #@@nocolor-node
        #@+at
        # See
        # mod:
        #     Expression(expr body)
        #     Interactive(stmt* body)
        #     Module(stmt* body)
        #     Suite(stmt* body) #  not an actual node,
        # stmt:
        #     Assert(expr test, expr? msg)
        #     Assign(expr* targets, expr value)
        #     AugAssign(expr target, operator op, expr value)
        #     Break
        #     ClassDef(identifier name, expr* bases, stmt* body, expr* decorator_list)
        #     Continue
        #     Delete(expr* targets)
        #     Exec(expr body, expr? globals, expr? locals)
        #     Expr(expr value)
        #     For(expr target, expr iter, stmt* body, stmt* orelse)
        #     FunctionDef(identifier name, arguments args,stmt* body, expr* decorator_list)
        #     Global(identifier* names)
        #     If(expr test, stmt* body, stmt* orelse)
        #     Import(alias* names)
        #     ImportFrom(identifier? module, alias* names, int? level)
        #     Pass
        #     Print(expr? dest, expr* values, bool nl)
        #     Raise(expr? type, expr? inst, expr? tback)
        #     Return(expr? value)
        #     TryExcept(stmt* body, excepthandler* handlers, stmt* orelse)
        #     TryFinally(stmt* body, stmt* finalbody)
        #     While(expr test, stmt* body, stmt* orelse)
        #     With(expr context_expr, expr? optional_vars, stmt* body)
        # expr:
        #     Attribute(expr value, identifier attr, expr_context ctx)
        #     BinOp(expr left, operator op, expr right)
        #     BoolOp(boolop op, expr* values)
        #     Call(expr func, expr* args, keyword* keywords, expr? starargs, expr? kwargs)
        #     Compare(expr left, cmpop* ops, expr* comparators)
        #     Dict(expr* keys, expr* values)
        #     DictComp(expr key, expr value, comprehension* generators)
        #     GeneratorExp(expr elt, comprehension* generators)
        #     IfExp(expr test, expr body, expr orelse)
        #     Lambda(arguments args, expr body)
        #     List(expr* elts, expr_context ctx) 
        #     ListComp(expr elt, comprehension* generators)
        #     Name(identifier id, expr_context ctx)
        #     Num(object n) -- a number as a PyObject.
        #     Repr(expr value)
        #     Set(expr* elts)
        #     SetComp(expr elt, comprehension* generators)
        #     Str(string s) -- need to specify raw, unicode, etc?
        #     Subscript(expr value, slice slice, expr_context ctx)
        #     Tuple(expr* elts, expr_context ctx)
        #     UnaryOp(unaryop op, expr operand)
        #     Yield(expr? value)
        # expr_context:
        #     AugLoad
        #     AugStore
        #     Del
        #     Load
        #     Param
        #     Store
        # slice:
        #     Ellipsis
        #     Slice(expr? lower, expr? upper, expr? step) 
        #     ExtSlice(slice* dims) 
        #     Index(expr value) 
        # boolop:
        #     And | Or 
        # operator:
        #     Add | Sub | Mult | Div | Mod | Pow | LShift | RShift | BitOr | BitXor | BitAnd | FloorDiv
        # unaryop:
        #     Invert | Not | UAdd | USub
        # cmpop:
        #     Eq | NotEq | Lt | LtE | Gt | GtE | Is | IsNot | In | NotIn
        # excepthandler:
        #     ExceptHandler(expr? type, expr? name, stmt* body)
        #     
        # Lower case node names:
        #     alias (identifier name, identifier? asname)
        #     arguments (expr* args, identifier? vararg, identifier? kwarg, expr* defaults)
        #     comprehension (expr target, expr iter, expr* ifs)
        #     keyword (identifier arg, expr value)
        #@-<< Py2K grammar >>
        #@+<< Py3K grammar >>
        #@+node:ekr.20140526082700.17168: *5* << Py3k grammar >>
        #@@nocolor-node
        #@+at
        # 
        #     mod = Module(stmt* body)
        #         | Interactive(stmt* body)
        #         | Expression(expr body)
        # 
        #         -- not really an actual node but useful in Jython's typesystem.
        #         | Suite(stmt* body)
        # 
        #     stmt = FunctionDef(identifier name, arguments args, 
        #                            stmt* body, expr* decorator_list, expr? returns)
        #           | ClassDef(identifier name, 
        #              expr* bases,
        #              keyword* keywords,
        #              expr? starargs,
        #              expr? kwargs,
        #              stmt* body,
        #              expr* decorator_list)
        #           | Return(expr? value)
        # 
        #           | Delete(expr* targets)
        #           | Assign(expr* targets, expr value)
        #           | AugAssign(expr target, operator op, expr value)
        # 
        #           -- use 'orelse' because else is a keyword in target languages
        #           | For(expr target, expr iter, stmt* body, stmt* orelse)
        #           | While(expr test, stmt* body, stmt* orelse)
        #           | If(expr test, stmt* body, stmt* orelse)
        #           | With(withitem* items, stmt* body)
        # 
        #           | Raise(expr? exc, expr? cause)
        #           | Try(stmt* body, excepthandler* handlers, stmt* orelse, stmt* finalbody)
        #           | Assert(expr test, expr? msg)
        # 
        #           | Import(alias* names)
        #           | ImportFrom(identifier? module, alias* names, int? level)
        # 
        #           | Global(identifier* names)
        #           | Nonlocal(identifier* names)
        #           | Expr(expr value)
        #           | Pass | Break | Continue
        # 
        #           -- Jython will be different
        #           -- col_offset is the byte offset in the utf8 string the parser uses
        #           attributes (int lineno, int col_offset)
        # 
        #           -- BoolOp() can use left & right?
        #     expr = BoolOp(boolop op, expr* values)
        #          | BinOp(expr left, operator op, expr right)
        #          | UnaryOp(unaryop op, expr operand)
        #          | Lambda(arguments args, expr body)
        #          | IfExp(expr test, expr body, expr orelse)
        #          | Dict(expr* keys, expr* values)
        #          | Set(expr* elts)
        #          | ListComp(expr elt, comprehension* generators)
        #          | SetComp(expr elt, comprehension* generators)
        #          | DictComp(expr key, expr value, comprehension* generators)
        #          | GeneratorExp(expr elt, comprehension* generators)
        #          -- the grammar constrains where yield expressions can occur
        #          | Yield(expr? value)
        #          | YieldFrom(expr value)
        #          -- need sequences for compare to distinguish between
        #          -- x < 4 < 3 and (x < 4) < 3
        #          | Compare(expr left, cmpop* ops, expr* comparators)
        #          | Call(expr func, expr* args, keyword* keywords,
        #              expr? starargs, expr? kwargs)
        #          | Num(object n) -- a number as a PyObject.
        #          | Str(string s) -- need to specify raw, unicode, etc?
        #          | Bytes(bytes s)
        #          | Ellipsis
        #          -- other literals? bools?
        # 
        #          -- the following expression can appear in assignment context
        #          | Attribute(expr value, identifier attr, expr_context ctx)
        #          | Subscript(expr value, slice slice, expr_context ctx)
        #          | Starred(expr value, expr_context ctx)
        #          | Name(identifier id, expr_context ctx)
        #          | List(expr* elts, expr_context ctx) 
        #          | Tuple(expr* elts, expr_context ctx)
        # 
        #           -- col_offset is the byte offset in the utf8 string the parser uses
        #           attributes (int lineno, int col_offset)
        # 
        #     expr_context = Load | Store | Del | AugLoad | AugStore | Param
        # 
        #     slice = Slice(expr? lower, expr? upper, expr? step) 
        #           | ExtSlice(slice* dims) 
        #           | Index(expr value) 
        # 
        #     boolop = And | Or 
        # 
        #     operator = Add | Sub | Mult | Div | Mod | Pow | LShift 
        #                  | RShift | BitOr | BitXor | BitAnd | FloorDiv
        # 
        #     unaryop = Invert | Not | UAdd | USub
        # 
        #     cmpop = Eq | NotEq | Lt | LtE | Gt | GtE | Is | IsNot | In | NotIn
        # 
        #     comprehension = (expr target, expr iter, expr* ifs)
        # 
        #     excepthandler = ExceptHandler(expr? type, identifier? name, stmt* body)
        #                     attributes (int lineno, int col_offset)
        # 
        #     arguments = (arg* args, identifier? vararg, expr? varargannotation,
        #                      arg* kwonlyargs, identifier? kwarg,
        #                      expr? kwargannotation, expr* defaults,
        #                      expr* kw_defaults)
        #     arg = (identifier arg, expr? annotation)
        # 
        #     -- keyword arguments supplied to call
        #     keyword = (identifier arg, expr value)
        # 
        #     -- import name with optional 'as' alias.
        #     alias = (identifier name, identifier? asname)
        # 
        #     withitem = (expr context_expr, expr? optional_vars)
        #@-<< Py3K grammar >>

        # Inexpensive, because there are few entries in aList.
        aList = [z for z in dir(self) if z.startswith('do_')]
        for s in sorted(aList):
            name = s[3:]
            if name not in names:
                if not silent:
                    g.trace('***** oops',self.__class__.__name__,name)
                assert False,name
                    # This is useful now that most errors have been caught.
    #@+node:ekr.20140526082700.17169: *4* bt.find_function_call
    # Used by leoInspect code.

    def find_function_call (self,node):

        '''
        Return the static name of the function being called.
        
        tree is the tree.func part of the Call node.'''
        
        trace = False and not g.app.runningAllUnitTests
        kind = self.kind(node)
        assert kind not in ('str','Builtin')
        if kind == 'Name':
            s = node.id
        elif kind == 'Attribute':
            s = node.attr # node.attr is always a string.
        elif kind == 'Call':
            s = self.find_function_call(node.func)
        elif kind == 'Subscript':
            s = None
        else:
            s = None
            if trace:
                # This is not an error.  Example:  (g())()
                s = '****unknown kind: %s****: %s' % (kind,Utils().format(node))
                g.trace(s)

        return s or '<no function name>'
    #@+node:ekr.20140526082700.17170: *4* bt.info
    def info (self,node):
        
        return '%s: %9s' % (node.__class__.__name__,id(node))
    #@+node:ekr.20140526082700.17171: *4* bt.kind
    def kind(self,node):
        
        return node.__class__.__name__
    #@+node:ekr.20140526082700.17172: *4* bt.op_name
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
#@+node:ekr.20140526082700.17173: *3*  class AstFullTraverser
class AstFullTraverser(AstBaseTraverser):
    '''
    A super-fast tree traversal class.
    
    This class defines methods for *all* types of ast.Ast nodes,
    except nodes that typically don't need to be visited, such as nodes
    referenced by node.ctx and node.op fields.
    
    Subclasses are, of course, free to add visitors for, say, ast.Load,
    nodes. To make this work, subclasses must override visitors for
    ast.Node and ast.Attribute nodes so that they call::
        
        self.visit(node.ctx)
        
    At present, such calls are commented out.  Furthermore, if a visitor
    for ast.Load is provided, visitors for *all* kinds of nodes referenced
    by node.ctx fields must also be given.  Such is the price of speed.
    '''
    
    # def __init__(self):
        # AstBaseTraverser.__init__(self)

    #@+others
    #@+node:ekr.20140526082700.17174: *4*  ft.run (entry point)
    def run (self,root):
        
        # py==lint: disable=W0221
            # Arguments number differs from overridden method.

        self.visit(root)
    #@+node:ekr.20140526082700.17175: *4* ft.operators
    #@+node:ekr.20140526082700.17176: *5* ft do-nothings
    def do_Bytes(self,node): 
        pass # Python 3.x only.
        
    def do_Ellipsis(self,node):
        pass
        
    def do_Num(self,node):
        pass # Num(object n) # a number as a PyObject.
        
    def do_Str (self,node):
        pass # represents a string constant.
    #@+node:ekr.20140526082700.17177: *5* ft.arguments & arg
    # arguments = (expr* args, identifier? vararg, identifier? kwarg, expr* defaults)

    def do_arguments(self,node):
        
        for z in node.args:
            self.visit(z)
        for z in node.defaults:
            self.visit(z)
            
    # Python 3:
    # arg = (identifier arg, expr? annotation)

    def do_arg(self,node):
        if node.annotation:
            self.visit(node.annotation)
    #@+node:ekr.20140526082700.17178: *5* ft.Attribute
    # Attribute(expr value, identifier attr, expr_context ctx)

    def do_Attribute(self,node):
        
        self.visit(node.value)
        # self.visit(node.ctx)
    #@+node:ekr.20140526082700.17179: *5* ft.BinOp
    # BinOp(expr left, operator op, expr right)

    def do_BinOp (self,node):

        self.visit(node.left)
        # self.op_name(node.op)
        self.visit(node.right)
    #@+node:ekr.20140526082700.17180: *5* ft.BoolOp
    # BoolOp(boolop op, expr* values)

    def do_BoolOp (self,node):
        
        for z in node.values:
            self.visit(z)
    #@+node:ekr.20140526082700.17181: *5* ft.Call
    # Call(expr func, expr* args, keyword* keywords, expr? starargs, expr? kwargs)

    def do_Call(self,node):
        
        self.visit(node.func)
        for z in node.args:
            self.visit(z)
        for z in node.keywords:
            self.visit(z)
        if getattr(node,'starargs',None):
            self.visit(node.starargs)
        if getattr(node,'kwargs',None):
            self.visit(node.kwargs)
    #@+node:ekr.20140526082700.17182: *5* ft.Compare
    # Compare(expr left, cmpop* ops, expr* comparators)

    def do_Compare(self,node):
        
        self.visit(node.left)
        for z in node.comparators:
            self.visit(z)
    #@+node:ekr.20140526082700.17183: *5* ft.comprehension
    # comprehension (expr target, expr iter, expr* ifs)

    def do_comprehension(self,node):

        self.visit(node.target) # A name.
        self.visit(node.iter) # An attribute.
        for z in node.ifs: ### Bug fix.
            self.visit(z)
    #@+node:ekr.20140526082700.17184: *5* ft.Dict
    # Dict(expr* keys, expr* values)

    def do_Dict(self,node):
        
        for z in node.keys:
            self.visit(z)
        for z in node.values:
            self.visit(z)
    #@+node:ekr.20140526082700.17185: *5* ft.Expr
    # Expr(expr value)

    def do_Expr(self,node):
        
        self.visit(node.value)
    #@+node:ekr.20140526082700.17186: *5* ft.Expression
    def do_Expression(self,node):
        
        '''An inner expression'''

        self.visit(node.body)
    #@+node:ekr.20140526082700.17187: *5* ft.ExtSlice
    def do_ExtSlice (self,node):
        
        for z in node.dims:
            self.visit(z)
    #@+node:ekr.20140526082700.17188: *5* ft.GeneratorExp
    # GeneratorExp(expr elt, comprehension* generators)

    def do_GeneratorExp(self,node):
        
        self.visit(node.elt)
        for z in node.generators:
            self.visit(z)
    #@+node:ekr.20140526082700.17189: *5* ft.ifExp (ternary operator)
    # IfExp(expr test, expr body, expr orelse)

    def do_IfExp (self,node):

        self.visit(node.body)
        self.visit(node.test)
        self.visit(node.orelse)
    #@+node:ekr.20140526082700.17190: *5* ft.Index
    def do_Index (self,node):
        
        self.visit(node.value)
    #@+node:ekr.20140526082700.17191: *5* ft.keyword
    # keyword = (identifier arg, expr value)

    def do_keyword(self,node):

        # node.arg is a string.
        self.visit(node.value)
    #@+node:ekr.20140526082700.17192: *5* ft.List & ListComp
    # List(expr* elts, expr_context ctx) 

    def do_List(self,node):
        
        for z in node.elts:
            self.visit(z)
        # self.visit(node.ctx)

    # ListComp(expr elt, comprehension* generators)

    def do_ListComp(self,node):

        elt = self.visit(node.elt)
        for z in node.generators:
            self.visit(z)
    #@+node:ekr.20140526082700.17193: *5* ft.Name (revise)
    # Name(identifier id, expr_context ctx)

    def do_Name(self,node):

        # self.visit(node.ctx)
        pass

    #@+node:ekr.20140526082700.17194: *5* ft.Repr
    # Python 2.x only
    # Repr(expr value)

    def do_Repr(self,node):

        self.visit(node.value)
    #@+node:ekr.20140526082700.17195: *5* ft.Slice
    def do_Slice (self,node):

        if getattr(node,'lower',None):
            self.visit(node.lower)
        if getattr(node,'upper',None):
            self.visit(node.upper)
        if getattr(node,'step',None):
            self.visit(node.step)
    #@+node:ekr.20140526082700.17196: *5* ft.Subscript
    # Subscript(expr value, slice slice, expr_context ctx)

    def do_Subscript(self,node):
        
        self.visit(node.value)
        self.visit(node.slice)
        # self.visit(node.ctx)
    #@+node:ekr.20140526082700.17197: *5* ft.Tuple
    # Tuple(expr* elts, expr_context ctx)

    def do_Tuple(self,node):
        
        for z in node.elts:
            self.visit(z)
        # self.visit(node.ctx)
    #@+node:ekr.20140526082700.17198: *5* ft.UnaryOp
    # UnaryOp(unaryop op, expr operand)

    def do_UnaryOp (self,node):
        
        # self.op_name(node.op)
        self.visit(node.operand)
    #@+node:ekr.20140526082700.17199: *4* ft.statements
    #@+node:ekr.20140526082700.17200: *5* ft.alias
    # identifier name, identifier? asname)

    def do_alias (self,node):
        
        # self.visit(node.name)
        # if getattr(node,'asname')
            # self.visit(node.asname)
        pass
    #@+node:ekr.20140526082700.17201: *5* ft.Assert
    # Assert(expr test, expr? msg)

    def do_Assert(self,node):

        self.visit(node.test)
        if node.msg:
            self.visit(node.msg)
    #@+node:ekr.20140526082700.17202: *5* ft.Assign
    # Assign(expr* targets, expr value)

    def do_Assign(self,node):

        for z in node.targets:
            self.visit(z)
        self.visit(node.value)
    #@+node:ekr.20140526082700.17203: *5* ft.AugAssign
    # AugAssign(expr target, operator op, expr value)

    def do_AugAssign(self,node):
        
        # g.trace('FT',Utils().format(node),g.callers())
        self.visit(node.target)
        self.visit(node.value)
    #@+node:ekr.20140526082700.17204: *5* ft.Break
    def do_Break(self,tree):
        pass

    #@+node:ekr.20140526082700.17205: *5* ft.ClassDef
    # ClassDef(identifier name, expr* bases, stmt* body, expr* decorator_list)

    def do_ClassDef (self,node):

        for z in node.bases:
            self.visit(z)
        for z in node.body:
            self.visit(z)
        for z in node.decorator_list:
            self.visit(z)
    #@+node:ekr.20140526082700.17206: *5* ft.Continue
    def do_Continue(self,tree):
        pass

    #@+node:ekr.20140526082700.17207: *5* ft.Delete
    # Delete(expr* targets)

    def do_Delete(self,node):

        for z in node.targets:
            self.visit(z)
    #@+node:ekr.20140526082700.17208: *5* ft.ExceptHandler
    # Python 2: ExceptHandler(expr? type, expr? name, stmt* body)
    # Python 3: ExceptHandler(expr? type, identifier? name, stmt* body)

    def do_ExceptHandler(self,node):
        
        if node.type:
            self.visit(node.type)
        if node.name and isinstance(node.name,ast.Name):
            self.visit(node.name)
        for z in node.body:
            self.visit(z)
    #@+node:ekr.20140526082700.17209: *5* ft.Exec
    # Python 2.x only
    # Exec(expr body, expr? globals, expr? locals)

    def do_Exec(self,node):

        self.visit(node.body)
        if getattr(node,'globals',None):
            self.visit(node.globals)
        if getattr(node,'locals',None):
            self.visit(node.locals)
    #@+node:ekr.20140526082700.17210: *5* ft.For
    # For(expr target, expr iter, stmt* body, stmt* orelse)

    def do_For (self,node):

        self.visit(node.target)
        self.visit(node.iter)
        for z in node.body:
            self.visit(z)
        for z in node.orelse:
            self.visit(z)

    #@+node:ekr.20140526082700.17211: *5* ft.FunctionDef
    # FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list)

    def do_FunctionDef (self,node):
        
        self.visit(node.args)
        for z in node.body:
            self.visit(z)
        for z in node.decorator_list:
            self.visit(z)

       
    #@+node:ekr.20140526082700.17212: *5* ft.Global
    # Global(identifier* names)

    def do_Global(self,node):
        pass
    #@+node:ekr.20140526082700.17213: *5* ft.If
    # If(expr test, stmt* body, stmt* orelse)

    def do_If(self,node):
        
        self.visit(node.test)
        for z in node.body:
            self.visit(z)
        for z in node.orelse:
            self.visit(z)
    #@+node:ekr.20140526082700.17214: *5* ft.Import & ImportFrom
    # Import(alias* names)

    def do_Import(self,node):
        pass

    # ImportFrom(identifier? module, alias* names, int? level)

    def do_ImportFrom(self,node):
        
        # for z in node.names:
            # self.visit(z)
        pass
    #@+node:ekr.20140526082700.17215: *5* ft.Lambda
    # Lambda(arguments args, expr body)

    def do_Lambda(self,node):
        
        self.visit(node.args)
        self.visit(node.body)
    #@+node:ekr.20140526082700.17216: *5* ft.Module
    # Module(stmt* body)

    def do_Module (self,node):
        
        for z in node.body:
            self.visit(z)
    #@+node:ekr.20140526082700.17217: *5* ft.Pass
    def do_Pass(self,node):

        pass

    #@+node:ekr.20140526082700.17218: *5* ft.Print
    # Python 2.x only
    # Print(expr? dest, expr* values, bool nl)
    def do_Print(self,node):

        if getattr(node,'dest',None):
            self.visit(node.dest)
        for expr in node.values:
            self.visit(expr)
    #@+node:ekr.20140526082700.17219: *5* ft.Raise
    # Raise(expr? type, expr? inst, expr? tback)

    def do_Raise(self,node):
        
        if getattr(node,'type',None):
            self.visit(node.type)
        if getattr(node,'inst',None):
            self.visit(node.inst)
        if getattr(node,'tback',None):
            self.visit(node.tback)
    #@+node:ekr.20140526082700.17220: *5* ft.Return
    # Return(expr? value)

    def do_Return(self,node):
        
        if node.value:
            self.visit(node.value)
    #@+node:ekr.20140526082700.17221: *5* ft.Try (Python 3 only)
    # Python 3 only: Try(stmt* body, excepthandler* handlers, stmt* orelse, stmt* finalbody)

    def do_Try(self,node):
        
        for z in node.body:
            self.visit(z)
        for z in node.handlers:
            self.visit(z)
        for z in node.orelse:
            self.visit(z)
        for z in node.finalbody:
            self.visit(z)
    #@+node:ekr.20140526082700.17222: *5* ft.TryExcept
    # TryExcept(stmt* body, excepthandler* handlers, stmt* orelse)

    def do_TryExcept(self,node):
        
        for z in node.body:
            self.visit(z)
        for z in node.handlers:
            self.visit(z)
        for z in node.orelse:
            self.visit(z)
    #@+node:ekr.20140526082700.17223: *5* ft.TryFinally
    # TryFinally(stmt* body, stmt* finalbody)

    def do_TryFinally(self,node):

        for z in node.body:
            self.visit(z)
        for z in node.finalbody:
            self.visit(z)
    #@+node:ekr.20140526082700.17224: *5* ft.While
    # While(expr test, stmt* body, stmt* orelse)

    def do_While (self,node):

        self.visit(node.test) # Bug fix: 2013/03/23.
        for z in node.body:
            self.visit(z)
        for z in node.orelse:
            self.visit(z)
    #@+node:ekr.20140526082700.17225: *5* ft.With
    # With(expr context_expr, expr? optional_vars, stmt* body)

    def do_With (self,node):
        
        self.visit(node.context_expr)
        if node.optional_vars:
            self.visit(node.optional_vars)
        for z in node.body:
            self.visit(z)
        
    #@+node:ekr.20140526082700.17226: *5* ft.Yield
    #  Yield(expr? value)

    def do_Yield(self,node):

        if node.value:
            self.visit(node.value)
    #@+node:ekr.20140526082700.17227: *4* ft.visit
    def visit(self,node):

        '''Visit a *single* ast node.  Visitors are responsible for visiting children!'''
        assert isinstance(node,ast.AST),node.__class__.__name__
        method_name = 'do_' + node.__class__.__name__
        method = getattr(self,method_name)
        return method(node)

    def visit_children(self,node):
        assert False,'must visit children explicitly'
    #@-others
#@+node:ekr.20140526082700.17228: *3* class AstFormatter
class AstFormatter(AstFullTraverser):
    '''
    A class to recreate source code from an AST.
    
    This does not have to be perfect, but it should be close.
    
    Also supports optional annotations such as line numbers, file names, etc.
    '''
    
    # def __init__ (self):
        # AstFullTraverser.__init__(self)
        
    def __call__(self,node):
        return self.format(node)
    
    #@+others
    #@+node:ekr.20140526082700.17229: *4*  f.visit
    def visit(self,node):
        
        '''Return the formatted version of an Ast node, or list of Ast nodes.'''
        
        if isinstance(node,(list,tuple)):
            return ','.join([self.visit(z) for z in node])
        elif node is None:
            return 'None'
        else:
            assert isinstance(node,ast.AST),node.__class__.__name__
            method_name = 'do_' + node.__class__.__name__
            method = getattr(self,method_name)
            s = method(node)
            assert type(s)==type('abc'),type(s)
            return s
    #@+node:ekr.20140526082700.17230: *4* f.format
    def format (self,node):

        self.level = 0
        val = self.visit(node)
        return val and val.strip() or ''
    #@+node:ekr.20140526082700.17231: *4* f.indent
    def indent(self,s):

        return '%s%s' % (' '*4*self.level,s)
    #@+node:ekr.20140526082700.17232: *4* f.Contexts
    #@+node:ekr.20140526082700.17233: *5* f.ClassDef
    # ClassDef(identifier name, expr* bases, stmt* body, expr* decorator_list)

    def do_ClassDef (self,node):
        
        result = []
        name = node.name # Only a plain string is valid.
        bases = [self.visit(z) for z in node.bases] if node.bases else []
                
        if bases:
            result.append(self.indent('class %s(%s):\n' % (name,','.join(bases))))
        else:
            result.append(self.indent('class %s:\n' % name))

        for z in node.body:
            self.level += 1
            result.append(self.visit(z))
            self.level -= 1
            
        return ''.join(result)
    #@+node:ekr.20140526082700.17234: *5* f.FunctionDef
    # FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list)

    def do_FunctionDef (self,node):
        '''Format a FunctionDef node.'''
        result = []
        if node.decorator_list:
            for z in node.decorator_list:
                result.append('@%s\n' % self.visit(z))
        name = node.name # Only a plain string is valid.
        args = self.visit(node.args) if node.args else '()'
        result.append(self.indent('def %s(%s):\n' % (name,args)))
        for z in node.body:
            self.level += 1
            result.append(self.visit(z))
            self.level -= 1
        return ''.join(result)
    #@+node:ekr.20140526082700.17235: *5* f.Interactive
    def do_Interactive(self,node):

        for z in node.body:
            self.visit(z)

    #@+node:ekr.20140526082700.17236: *5* f.Module
    def do_Module (self,node):
        
        assert 'body' in node._fields
        return 'module:%s\n%s' % (
            node.stc_fn if hasattr(node,'stc_fn') else '<unknown>',
            ''.join([self.visit(z) for z in  node.body]))
    #@+node:ekr.20140526082700.17237: *5* f.Lambda
    def do_Lambda (self,node):
            
        return self.indent('lambda %s: %s\n' % (
            self.visit(node.args),
            self.visit(node.body)))
    #@+node:ekr.20140526082700.17238: *4* f.ctx nodes
    def do_AugLoad(self,node):
        return 'AugLoad'
    def do_Del(self,node):
        return 'Del'
    def do_Load(self,node):
        return 'Load'
    def do_Param(self,node):
        return 'Param'
    def do_Store(self,node):
        return 'Store'
    #@+node:ekr.20140526082700.17239: *4* f.Exceptions
    #@+node:ekr.20140526082700.17240: *5* f.ExceptHandler
    def do_ExceptHandler(self,node):
        
        result = []
        result.append(self.indent('except'))
        if getattr(node,'type',None):
            result.append(' %s' % self.visit(node.type))
        if getattr(node,'name',None):
            if isinstance(node.name,ast.AST):
                result.append(' as %s' % self.visit(node.name))
            else:
                result.append(' as %s' % node.name) # Python 3.x.
        result.append(':\n')
        for z in node.body:
            self.level += 1
            result.append(self.visit(z))
            self.level -= 1
        return ''.join(result)
    #@+node:ekr.20140526082700.17241: *5* f.TryExcept
    def do_TryExcept(self,node):
        
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
    #@+node:ekr.20140526082700.17242: *5* f.TryFinally
    def do_TryFinally(self,node):
        
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
    #@+node:ekr.20140526082700.17243: *4* f.Expressions
    #@+node:ekr.20140526082700.17244: *5* f.Expr
    def do_Expr(self,node):
        
        '''An outer expression: must be indented.'''
        
        return self.indent('%s\n' % self.visit(node.value))

    #@+node:ekr.20140526082700.17245: *5* f.Expression
    def do_Expression(self,node):
        
        '''An inner expression: do not indent.'''

        return '%s\n' % self.visit(node.body)
    #@+node:ekr.20140526082700.17246: *5* f.GeneratorExp
    def do_GeneratorExp(self,node):
       
        elt  = self.visit(node.elt) or ''

        gens = [self.visit(z) for z in node.generators]
        gens = [z if z else '<**None**>' for z in gens] ### Kludge: probable bug.
        
        return '<gen %s for %s>' % (elt,','.join(gens))
    #@+node:ekr.20140526082700.17247: *4* f.Operands
    #@+node:ekr.20140526082700.17248: *5* f.arguments
    # arguments = (expr* args, identifier? vararg, identifier? kwarg, expr* defaults)

    def do_arguments(self,node):
        '''Format the arguments node.'''
        kind = self.kind(node)
        assert kind == 'arguments',kind
        args     = [self.visit(z) for z in node.args]
        defaults = [self.visit(z) for z in node.defaults]
        # Assign default values to the last args.
        args2 = []
        n_plain = len(args) - len(defaults)
        for i in range(len(args)):
            if i < n_plain:
                args2.append(args[i])
            else:
                args2.append('%s=%s' % (args[i],defaults[i-n_plain]))
        # Now add the vararg and kwarg args.
        name = getattr(node,'vararg',None)
        if name: args2.append('*'+name)
        name = getattr(node,'kwarg',None)
        if name: args2.append('**'+name)
        return ','.join(args2)
    #@+node:ekr.20140526082700.17249: *5* f.arg (Python3 only)
    # Python 3:
    # arg = (identifier arg, expr? annotation)

    def do_arg(self,node):
        if node.annotation:
            return self.visit(node.annotation)
        else:
            return ''
    #@+node:ekr.20140526082700.17250: *5* f.Attribute
    # Attribute(expr value, identifier attr, expr_context ctx)

    def do_Attribute(self,node):

        return '%s.%s' % (
            self.visit(node.value),
            node.attr) # Don't visit node.attr: it is always a string.
    #@+node:ekr.20140526082700.17251: *5* f.Bytes
    def do_Bytes(self,node): # Python 3.x only.
        assert g.isPython3
        return str(node.s)
        
    #@+node:ekr.20140526082700.17252: *5* f.Call & f.keyword
    # Call(expr func, expr* args, keyword* keywords, expr? starargs, expr? kwargs)

    def do_Call(self,node):
        
        # g.trace(node,Utils().dump_ast(node))

        func = self.visit(node.func)
        args = [self.visit(z) for z in node.args]

        for z in node.keywords:
            # Calls f.do_keyword.
            args.append(self.visit(z))

        if getattr(node,'starargs',None):
            args.append('*%s' % (self.visit(node.starargs)))

        if getattr(node,'kwargs',None):
            args.append('**%s' % (self.visit(node.kwargs)))
            
        args = [z for z in args if z] # Kludge: Defensive coding.
        return '%s(%s)' % (func,','.join(args))
    #@+node:ekr.20140526082700.17253: *6* f.keyword
    # keyword = (identifier arg, expr value)

    def do_keyword(self,node):

        # node.arg is a string.
        value = self.visit(node.value)

        # This is a keyword *arg*, not a Python keyword!
        return '%s=%s' % (node.arg,value)
    #@+node:ekr.20140526082700.17254: *5* f.comprehension
    def do_comprehension(self,node):

        result = []
        name = self.visit(node.target) # A name.
        it   = self.visit(node.iter) # An attribute.

        result.append('%s in %s' % (name,it))

        ifs = [self.visit(z) for z in node.ifs]
        if ifs:
            result.append(' if %s' % (''.join(ifs)))
            
        return ''.join(result)
    #@+node:ekr.20140526082700.17255: *5* f.Dict
    def do_Dict(self,node):
        
        result = []
        keys   = [self.visit(z) for z in node.keys]
        values = [self.visit(z) for z in node.values]
            
        if len(keys) == len(values):
            result.append('{\n' if keys else '{')
            items = []
            for i in range(len(keys)):
                items.append('  %s:%s' % (keys[i],values[i]))
            result.append(',\n'.join(items))
            result.append('\n}' if keys else '}')
        else:
            Utils().error('f.Dict: len(keys) != len(values)\nkeys: %s\nvals: %s' % (
                repr(keys),repr(values)))
                
        return ''.join(result)
    #@+node:ekr.20140526082700.17256: *5* f.Ellipsis
    def do_Ellipsis(self,node):
        return '...'

    #@+node:ekr.20140526082700.17257: *5* f.ExtSlice
    def do_ExtSlice (self,node):

        return ':'.join([self.visit(z) for z in node.dims])
    #@+node:ekr.20140526082700.17258: *5* f.Index
    def do_Index (self,node):
        
        return self.visit(node.value)
    #@+node:ekr.20140526082700.17259: *5* f.List
    def do_List(self,node):

        # Not used: list context.
        # self.visit(node.ctx)
        
        elts = [self.visit(z) for z in node.elts]
        elst = [z for z in elts if z] # Defensive.
        return '[%s]' % ','.join(elts)
    #@+node:ekr.20140526082700.17260: *5* f.ListComp
    def do_ListComp(self,node):

        elt = self.visit(node.elt)

        gens = [self.visit(z) for z in node.generators]
        gens = [z if z else '<**None**>' for z in gens] ### Kludge: probable bug.

        return '%s for %s' % (elt,''.join(gens))
    #@+node:ekr.20140526082700.17261: *5* f.Name
    def do_Name(self,node):

        return node.id
    #@+node:ekr.20140526082700.17262: *5* f.Num
    def do_Num(self,node):
        return repr(node.n)
    #@+node:ekr.20140526082700.17263: *5* f.Repr
    # Python 2.x only
    def do_Repr(self,node):

        return 'repr(%s)' % self.visit(node.value)
    #@+node:ekr.20140526082700.17264: *5* f.Slice
    def do_Slice (self,node):
        
        lower,upper,step = '','',''
        
        if getattr(node,'lower',None) is not None:
            lower = self.visit(node.lower)
            
        if getattr(node,'upper',None) is not None:
            upper = self.visit(node.upper)
            
        if getattr(node,'step',None) is not None:
            step = self.visit(node.step)
            
        if step:
            return '%s:%s:%s' % (lower,upper,step)
        else:
            return '%s:%s' % (lower,upper)
    #@+node:ekr.20140526082700.17265: *5* f.Str
    def do_Str (self,node):
        
        '''This represents a string constant.'''
        return repr(node.s)
    #@+node:ekr.20140526082700.17266: *5* f.Subscript
    # Subscript(expr value, slice slice, expr_context ctx)

    def do_Subscript(self,node):
        
        value = self.visit(node.value)

        the_slice = self.visit(node.slice)
        
        return '%s[%s]' % (value,the_slice)
    #@+node:ekr.20140526082700.17267: *5* f.Tuple
    def do_Tuple(self,node):
            
        elts = [self.visit(z) for z in node.elts]

        return '(%s)' % ','.join(elts)
    #@+node:ekr.20140526082700.17268: *4* f.Operators
    #@+node:ekr.20140526082700.17269: *5* f.BinOp
    def do_BinOp (self,node):

        return '%s%s%s' % (
            self.visit(node.left),
            self.op_name(node.op),
            self.visit(node.right))
            
    #@+node:ekr.20140526082700.17270: *5* f.BoolOp
    def do_BoolOp (self,node):
        
        op_name = self.op_name(node.op)
        values = [self.visit(z) for z in node.values]
        return op_name.join(values)
        
    #@+node:ekr.20140526082700.17271: *5* f.Compare
    def do_Compare(self,node):
        
        result = []
        lt    = self.visit(node.left)
        # ops   = [self.visit(z) for z in node.ops]
        ops = [self.op_name(z) for z in node.ops]
        comps = [self.visit(z) for z in node.comparators]
            
        result.append(lt)
            
        if len(ops) == len(comps):
            for i in range(len(ops)):
                result.append('%s%s' % (ops[i],comps[i]))
        else:
            g.trace('ops',repr(ops),'comparators',repr(comps))
            
        return ''.join(result)
    #@+node:ekr.20140526082700.17272: *5* f.UnaryOp
    def do_UnaryOp (self,node):
        
        return '%s%s' % (
            self.op_name(node.op),
            self.visit(node.operand))
    #@+node:ekr.20140526082700.17273: *5* f.ifExp (ternary operator)
    def do_IfExp (self,node):

        return '%s if %s else %s ' % (
            self.visit(node.body),
            self.visit(node.test),
            self.visit(node.orelse))
    #@+node:ekr.20140526082700.17274: *4* f.Statements
    #@+node:ekr.20140526082700.17275: *5* f.Assert
    def do_Assert(self,node):
        
        test = self.visit(node.test)

        if getattr(node,'msg',None):
            message = self.visit(node.msg)
            return self.indent('assert %s, %s' % (test,message))
        else:
            return self.indent('assert %s' % test)
    #@+node:ekr.20140526082700.17276: *5* f.Assign
    def do_Assign(self,node):

        return self.indent('%s=%s' % (
            '='.join([self.visit(z) for z in node.targets]),
            self.visit(node.value)))
    #@+node:ekr.20140526082700.17277: *5* f.AugAssign
    def do_AugAssign(self,node):

        return self.indent('%s%s=%s\n' % (
            self.visit(node.target),
            self.op_name(node.op), # Bug fix: 2013/03/08.
            self.visit(node.value)))
    #@+node:ekr.20140526082700.17278: *5* f.Break
    def do_Break(self,node):

        return self.indent('break\n')

    #@+node:ekr.20140526082700.17279: *5* f.Continue
    def do_Continue(self,node):

        return self.indent('continue\n')
    #@+node:ekr.20140526082700.17280: *5* f.Delete
    def do_Delete(self,node):
        
        targets = [self.visit(z) for z in node.targets]

        return self.indent('del %s\n' % ','.join(targets))
    #@+node:ekr.20140526082700.17281: *5* f.Exec
    # Python 2.x only
    def do_Exec(self,node):
        
        body = self.visit(node.body)
        args = [] # Globals before locals.

        if getattr(node,'globals',None):
            args.append(self.visit(node.globals))
        
        if getattr(node,'locals',None):
            args.append(self.visit(node.locals))
            
        if args:
            return self.indent('exec %s in %s\n' % (
                body,','.join(args)))
        else:
            return self.indent('exec %s\n' % (body))
    #@+node:ekr.20140526082700.17282: *5* f.For
    def do_For (self,node):
        
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
    #@+node:ekr.20140526082700.17283: *5* f.Global
    def do_Global(self,node):

        return self.indent('global %s\n' % (
            ','.join(node.names)))
    #@+node:ekr.20140526082700.17284: *5* f.If
    def do_If (self,node):
        
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
    #@+node:ekr.20140526082700.17285: *5* f.Import & helper
    def do_Import(self,node):
        
        names = []

        for fn,asname in self.get_import_names(node):
            if asname:
                names.append('%s as %s' % (fn,asname))
            else:
                names.append(fn)
        
        return self.indent('import %s\n' % (
            ','.join(names)))
    #@+node:ekr.20140526082700.17286: *6* f.get_import_names
    def get_import_names (self,node):

        '''Return a list of the the full file names in the import statement.'''

        result = []
        for ast2 in node.names:

            if self.kind(ast2) == 'alias':
                data = ast2.name,ast2.asname
                result.append(data)
            else:
                g.trace('unsupported kind in Import.names list',self.kind(ast2))

        return result
    #@+node:ekr.20140526082700.17287: *5* f.ImportFrom
    def do_ImportFrom(self,node):
        
        names = []

        for fn,asname in self.get_import_names(node):
            if asname:
                names.append('%s as %s' % (fn,asname))
            else:
                names.append(fn)
        
        return self.indent('from %s import %s\n' % (
            node.module,
            ','.join(names)))
    #@+node:ekr.20140526082700.17288: *5* f.Pass
    def do_Pass(self,node):

        return self.indent('pass\n')
    #@+node:ekr.20140526082700.17289: *5* f.Print
    # Python 2.x only
    def do_Print(self,node):
        
        vals = []

        for z in node.values:
            vals.append(self.visit(z))
           
        if getattr(node,'dest',None):
            vals.append('dest=%s' % self.visit(node.dest))
            
        if getattr(node,'nl',None):
            # vals.append('nl=%s' % self.visit(node.nl))
            vals.append('nl=%s' % node.nl)
        
        return self.indent('print(%s)\n' % (
            ','.join(vals)))
    #@+node:ekr.20140526082700.17290: *5* f.Raise
    def do_Raise(self,node):
        
        args = []
        for attr in ('type','inst','tback'):
            if getattr(node,attr,None) is not None:
                args.append(self.visit(getattr(node,attr)))
            
        if args:
            return self.indent('raise %s\n' % (
                ','.join(args)))
        else:
            return self.indent('raise\n')
    #@+node:ekr.20140526082700.17291: *5* f.Return
    def do_Return(self,node):

        if node.value:
            return self.indent('return %s\n' % (
                self.visit(node.value)))
        else:
            return self.indent('return\n')
    #@+node:ekr.20140526082700.17292: *5* f.Suite
    # def do_Suite(self,node):

        # for z in node.body:
            # s = self.visit(z)

    #@+node:ekr.20140526082700.17293: *5* f.While
    def do_While (self,node):
        
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
    #@+node:ekr.20140526082700.17294: *5* f.With
    def do_With (self,node):
        
        result = []
        result.append(self.indent('with '))
        
        if hasattr(node,'context_expression'):
            result.append(self.visit(node.context_expresssion))

        vars_list = []
        if hasattr(node,'optional_vars'):
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
    #@+node:ekr.20140526082700.17295: *5* f.Yield
    def do_Yield(self,node):

        if getattr(node,'value',None):
            return self.indent('yield %s\n' % (
                self.visit(node.value)))
        else:
            return self.indent('yield\n')

    #@-others
#@+node:ekr.20140526082700.17362: *3* class PatternFormatter
class PatternFormatter (AstFormatter):
    
    # def __init__ (self):
        # AstFormatter.__init__ (self)

    #@+others
    #@+node:ekr.20140526082700.17363: *4* Constants & Name
    # Return generic markers allow better pattern matches.

    def do_BoolOp(self,node): # Python 2.x only.
        return 'Bool' 

    def do_Bytes(self,node): # Python 3.x only.
        return 'Bytes' # return str(node.s)

    def do_Name(self,node):
        return 'Bool' if node.id in ('True','False') else node.id

    def do_Num(self,node):
        return 'Num' # return repr(node.n)

    def do_Str (self,node):
        '''This represents a string constant.'''
        return 'Str' # return repr(node.s)
    #@-others
#@+node:ekr.20140527121225.17043: **  Unused classes
if 0:
    #@+others
    #@+node:ekr.20140526082700.17296: *3* class AllStatementsTraverser
    class AllStatementsTraverser(AstBaseTraverser):
            
        # def __init__(self):
            # AstBaseTraverser.__init__(self)

        #@+others
        #@+node:ekr.20140526082700.17297: *4* stat.run
        def run(self,node):

            # Only the top-level contexts visit their children.
            if isinstance(node,(ast.ClassDef,ast.FunctionDef,ast.Module)):
                for z in node.body:
                    self.visit(z)
            elif isinstance(node,ast.Lambda):
                self.visit(node.body)
            else:
                g.trace(node)
                assert False,'(Statement_Traverser) node must be a context'
        #@+node:ekr.20140526082700.17298: *4* stat.visit & default_visitor
        def visit(self,node):

            assert isinstance(node,ast.AST),node.__class__.__name__
            method_name = 'do_' + node.__class__.__name__
            method = getattr(self,method_name,self.default_visitor)
            return method(node)

        def default_visitor(self,node):
            pass
        #@+node:ekr.20140526082700.17299: *4* stat.visitors
        # There are no visitors for context nodes.
        #@+node:ekr.20140526082700.17300: *5* stat.ClassDef
        # ClassDef(identifier name, expr* bases, stmt* body, expr* decorator_list)

        def do_ClassDef (self,node):

            # for z in node.bases:
                # self.visit(z)
            for z in node.body:
                self.visit(z)
            # for z in node.decorator_list:
                # self.visit(z)
        #@+node:ekr.20140526082700.17301: *5* stat.ExceptHandler
        # ExceptHandler(expr? type, expr? name, stmt* body)

        def do_ExceptHandler(self,node):

            for z in node.body:
                self.visit(z)
        #@+node:ekr.20140526082700.17302: *5* stat.For
        # For(expr target, expr iter, stmt* body, stmt* orelse)

        def do_For (self,tree):

            for z in tree.body:
                self.visit(z)
            for z in tree.orelse:
                self.visit(z)

        #@+node:ekr.20140526082700.17303: *5* stat.FunctionDef
        # FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list)

        def do_FunctionDef (self,node):
            
            # self.visit(node.args)
            for z in node.body:
                self.visit(z)
            # for z in node.decorator_list:
                # self.visit(z)

           
        #@+node:ekr.20140526082700.17304: *5* stat.If
        # If(expr test, stmt* body, stmt* orelse)

        def do_If(self,node):

            for z in node.body:
                self.visit(z)
            for z in node.orelse:
                self.visit(z)
        #@+node:ekr.20140526082700.17305: *5* stat.Lambda
        # Lambda(arguments args, expr body)

        # Lambda is a statement for the purpose of contexts.

        def do_Lambda(self,node):
            pass
            # self.visit(node.args)
            # self.visit(node.body)
        #@+node:ekr.20140526082700.17306: *5* stat.Module
        def do_Module (self,node):
            
            for z in node.body:
                self.visit(z)
        #@+node:ekr.20140526082700.17307: *5* stat.TryExcept
        # TryExcept(stmt* body, excepthandler* handlers, stmt* orelse)

        def do_TryExcept(self,node):
            
            for z in node.body:
                self.visit(z)
            for z in node.handlers:
                self.visit(z)
            for z in node.orelse:
                self.visit(z)
        #@+node:ekr.20140526082700.17308: *5* stat.TryFinally
        # TryFinally(stmt* body, stmt* finalbody)

        def do_TryFinally(self,node):

            for z in node.body:
                self.visit(z)
            for z in node.finalbody:
                self.visit(z)
        #@+node:ekr.20140526082700.17309: *5* stat.While
        # While(expr test, stmt* body, stmt* orelse)

        def do_While (self,node):

            for z in node.body:
                self.visit(z)
            for z in node.orelse:
                self.visit(z)
        #@+node:ekr.20140526082700.17310: *5* stat.With
        # With(expr context_expr, expr? optional_vars, stmt* body)

        def do_With (self,node):

            for z in node.body:
                self.visit(z)
            
        #@-others
    #@+node:ekr.20140526082700.17311: *3* class BaseStats
    class BaseStats:
        
        '''The base class for all statistics classes.'''
        
        #@+others
        #@+node:ekr.20140526082700.17312: *4* stats.ctor
        def __init__ (self):
            
            # May be overriden in subclases.
            self.always_report = []
            self.distribution_table = []
            self.table = []
            self.init_ivars()
            self.init_tables()

        # Should be overridden in subclasses.
        def init_ivars(self):
            pass
            
        def init_tables(self):
            pass
        #@+node:ekr.20140526082700.17313: *4* stats.print_distribution
        def print_distribution(self,d,name):
            
            print('Distribution for %s...' % name)
            
            for n in sorted(d.keys()):
                print('%2s %s' % (n,d.get(n)))
            print('')
        #@+node:ekr.20140526082700.17314: *4* stats.print_stats
        def print_stats (self):
            
            max_n = 5
            for s in self.table:
                max_n = max(max_n,len(s))
                
            print('\nStatistics...\n')
            for s in self.table:
                var = 'n_%s' % s
                pad = ' ' * (max_n - len(s))
                if s.startswith('*'):
                    if s[1:].strip():
                        print('\n%s:\n' % s[1:])
                else:
                    pad = ' ' * (max_n-len(s))
                    val = getattr(self,var)
                    if val or var in self.always_report:
                        print('%s%s: %s' % (pad,s,val))
            print('')
            for d,name in self.distribution_table:
                self.print_distribution(d,name)
            print('')
        #@-others
        
    #@+node:ekr.20140526082700.17326: *3* class BaseType & subclasses
    #@+<< define class BaseType >>
    #@+node:ekr.20140526082700.17327: *4* << define class BaseType >>
    class BaseType:
        
        #@+<< about the type classes >>
        #@+node:ekr.20140526082700.17328: *5* << about the type classes >>
        '''BaseType is the base class for all type classes.

        Subclasses of BaseType represent inferened types.

        Do not change self.kind casually: self.kind (and __repr__ which simply
        returns self.kind) are real data: they are used by the TypeInferer class.
        The asserts in this class illustrate the contraints on self.kind.

        '''
        #@-<< about the type classes >>
        
        def __init__(self,kind):
            self.kind = kind
            
        def __repr__ (self):
            return self.kind
        __str__ = __repr__
        
        def is_type(self,other): return issubclass(other.__class__,BaseType)
        def __eq__(self, other): return self.is_type(other) and self.kind == other.kind
        def __ge__(self, other): return self.is_type(other) and self.kind >= other.kind
        def __gt__(self, other): return self.is_type(other) and self.kind > other.kind
        def __hash__(self):      return 0 # Use rich comparisons.
        def __le__(self, other): return self.is_type(other) and self.kind <= other.kind 
        def __lt__(self, other): return self.is_type(other) and self.kind < other.kind
        def __ne__(self, other): return self.is_type(other) and self.kind != other.kind
    #@-<< define class BaseType >>

    #@+others
    #@+node:ekr.20140526082700.17329: *4* class Any_Type
    class Any_Type(BaseType):
        
        def __init__(self):
            BaseType.__init__(self,'Any')
    #@+node:ekr.20140526082700.17330: *4* class Bool_Type
    class Bool_Type(BaseType):
        
        def __init__(self):
            BaseType.__init__(self,'Bool')
    #@+node:ekr.20140526082700.17331: *4* class Builtin_Type
    class Builtin_Type(BaseType):
        
        def __init__(self):
            BaseType.__init__(self,'Builtin')
    #@+node:ekr.20140526082700.17332: *4* class Bytes_Type
    class Bytes_Type(BaseType):
        
        def __init__(self):
            BaseType.__init__(self,'Bytes')
    #@+node:ekr.20140526082700.17333: *4* class Class_Type
    # Note: ClassType is a Python builtin.
    class Class_Type(BaseType):
        
        def __init__(self,cx):
            kind = 'Class: %s cx: %s' % (cx.name,cx)
            BaseType.__init__(self,kind)
            self.cx = cx # The context of the class.
            
        def __repr__(self):
            return 'Class: %s' % (self.cx.name)

        __str__ = __repr__
    #@+node:ekr.20140526082700.17334: *4* class Def_Type
    class Def_Type(BaseType):
        
        def __init__(self,cx,node):
            kind = 'Def(%s)@%s' % (cx,id(node))
            # kind = 'Def(%s)' % (cx)
            BaseType.__init__(self,kind)
            self.cx = cx # The context of the def.
            self.node = node
    #@+node:ekr.20140526082700.17335: *4* class Dict_Type
    class Dict_Type(BaseType):
        
        def __init__(self,node):
            
            # For now, all dicts are separate types.
            # kind = 'Dict(%s)' % (Utils().format(node))
            kind = 'Dict(@%s)' % id(node)
            BaseType.__init__(self,kind)
    #@+node:ekr.20140526082700.17336: *4* class Inference_Failure & subclasses
    class Inference_Failure(BaseType):
        def __init__(self,kind,node):
            BaseType.__init__(self,kind)
            u = Utils()
            trace = False and not g.app.runningAllUnitTests
            verbose = False
            self.node = node
            node_kind = u.kind(node)
            suppress_node = ('Assign','Attribute','Call','FunctionDef')
            suppress_kind = ('Un_Arg',)
            if trace and (verbose or kind not in suppress_kind) and node_kind not in suppress_node:
                if 1: # Print kind of node
                    # g.trace('%10s %s' % (self.kind[:10],node_kind))
                    g.trace('(Inference_Failure) %s %s' % (
                        self.kind[:10],u.format(node)[:70]))
                else: # Dump the node.
                    s = u.format(node).strip() if node else '<no node>'
                    i = s.find('\n')
                    if i == -1: i = len(s)
                    g.trace('%10s %s' % (self.kind[:10],s[:min(i,25)]))
                aList = getattr(node,'failures',[])
                aList.append(self)
                setattr(node,'failures',aList)
            
        def __repr__(self):
            return self.kind

        __str__ = __repr__

    class Circular_Assignment(Inference_Failure):
        def __init__(self,node):
            kind = 'Circular_Assn'
            Inference_Failure.__init__(self,kind,node)
            
    class Inference_Error(Inference_Failure):
        def __init__(self,node):
            kind = 'Inf_Err'
            Inference_Failure.__init__(self,kind,node)

    class Recursive_Inference(Inference_Failure):
        def __init__(self,node):
            kind = 'Recursive_Inf'
            Inference_Failure.__init__(self,kind,node)
            
    class Unknown_Type(Inference_Failure):
        def __init__(self,node):
            kind = 'U_T' # Short, for traces.
            Inference_Failure.__init__(self,kind,node)
            
    class Unknown_Arg_Type(Inference_Failure):
        def __init__(self,node):
            kind = 'U_Arg_T'
            Inference_Failure.__init__(self,kind,node)
    #@+node:ekr.20140526082700.17337: *4* class List_Type
    class List_Type(BaseType):
        
        def __init__(self,node):
            
            if 0: # All lists are separate types.
                kind = 'List(%s)@%s' % (Utils().format(node),id(node))
            else:
                # All lists have the same type.
                kind = 'List()'
            BaseType.__init__(self,kind)
    #@+node:ekr.20140526082700.17338: *4* class Module_Type
    class Module_Type(BaseType):
        
        def __init__(self,cx,node):
            kind = 'Module(%s)@%s' % (cx,id(node))
            BaseType.__init__(self,kind)
            self.cx = cx # The context of the module.
    #@+node:ekr.20140526082700.17339: *4* class None_Type
    class None_Type(BaseType):
        
        def __init__(self):
            BaseType.__init__(self,'None')
    #@+node:ekr.20140526082700.17340: *4* class Num_Type, Int_Type, Float_Type
    class Num_Type(BaseType):
        
        def __init__(self,type_class):
            BaseType.__init__(self,
                # kind='Num(%s)' % type_class.__name__)
                kind = type_class.__name__.capitalize())

    class Float_Type(Num_Type):

        def __init__(self):
            Num_Type.__init__(self,float)

    class Int_Type(Num_Type):
        
        def __init__(self):
            Num_Type.__init__(self,int)

            

    #@+node:ekr.20140526082700.17341: *4* class String_Type
    class String_Type(BaseType):
        
        def __init__(self):
            BaseType.__init__(self,'String')
    #@+node:ekr.20140526082700.17342: *4* class Tuple_Type
    class Tuple_Type(BaseType):
        
        def __init__(self,node):
            
            # For now, all tuples are separate types.
            # kind = 'Tuple(%s)@%s' % (Utils().format(node),id(node))
            # kind = 'Tuple(%s)' % (Utils().format(node))
            kind = 'Tuple(@%s)' % id(node)
            BaseType.__init__(self,kind)
    #@-others

    #@+node:ekr.20140526082700.17346: *3* class P1
    class P1(AstFullTraverser):
        '''
        Unified pre-pass does two things simultaneously:
        1. Injects ivars into nodes. Only this pass should do this!
           For all nodes::
                node.stc_context = self.context
                node.stc_parent = self.parent
           For all context nodes::
                node.stc_symbol_table = {} # Expensive!
           For all Name nodes.
                node.stc_scope = None.
        2. Calls define_name() for all defined names:
           - class and function names,
           - all names defined in import statements.
           - all paramater names (ctx is 'Param')
           - all assigned-to names (ctx is 'Store'):
           This has the effect of setting::
               node.stc_scope = self.context.
               
        **Important**: Injecting empty lists, dicts or sets causes gc problems.
        This code now injects empty dicts only in context nodes, which does
        not cause significant problems.
        '''
        def __init__(self):
            AstFullTraverser.__init__(self)
            self.in_aug_assign = False
                # A hack: True if visiting the target of an AugAssign node.
            self.u = Utils()
        def __call__(self,fn,node):
            self.run(fn,node)
        #@+others
        #@+node:ekr.20140526082700.17347: *4* class Dummy_Node
        class Dummy_Node:
            
            def __init__(self):
                
                # Use stc_ prefix to ensure no conflicts with ast.AST node field names.
                self.stc_parent = None
                self.stc_context = None
                self.stc_child_nodes = [] # Testing only.
        #@+node:ekr.20140526082700.17348: *4*  p1.run (entry point)
        def run (self,fn,root):
            '''Run the prepass: init, then visit the root.'''
            # pylint: disable=arguments-differ
            # Init all ivars.
            self.context = None
            self.fn = fn
            self.n_attributes = 0
            self.n_contexts = 0
            self.n_defined = 0
            self.n_nodes = 0
            self.parent = self.Dummy_Node()
            self.visit(root)
            # Undo references to Dummy_Node objects.
            root.stc_parent = None
            root.stc_context = None
        #@+node:ekr.20140526082700.17349: *4*  p1.visit (big gc anomaly)
        def visit(self,node):
            '''Inject node references in all nodes.'''
            assert isinstance(node,ast.AST),node.__class__.__name__
            self.n_nodes += 1
            if 0:
                # Injecting empty lists is expensive!
                #@+<< code that demonstrates the anomaly >>
                #@+node:ekr.20140526082700.17350: *5* << code that demonstrates the anomaly >>
                #@+at
                # Injecting list ivars into nodes is very expensive!
                # But only for a collection of large files...
                # As of rev 403: Leo: 37 files.
                # Python 2, Windows 7, range(200)
                #     p1: 3.38 sec. nodes: 289950 kind: 1
                #     p1: 3.38 sec. nodes: 289950 kind: 2
                #     p1: 0.73 sec. nodes: 289950 kind: 3
                # Python 3, Windows 7, range(200)
                #     p1: 1.83 sec. nodes: 290772 kind: 1
                #     p1: 2.96 sec. nodes: 290772 kind: 2
                #     p1: 0.73 sec. nodes: 290772 kind: 3
                # Python 3, Windows 7, range(100)
                #     p1: 2.14 sec. nodes: 290772 kind: 1
                #     p1: 1.92 sec. nodes: 290772 kind: 2
                #     p1: 0.75 sec. nodes: 290772 kind: 3
                # Mystery solved: kind1 == kind3 if gc is disabled in the unit test.
                #@@c
                kind = 1
                if kind == 1:
                    # if 0:
                        # node.stc_test_dict = {}
                    # elif 0: # Bad.
                        # if hasattr(self.parent,'stc_child_nodes'):
                            # self.parent.stc_child_nodes.append(node)
                        # else:
                            # self.parent.stc_child_nodes = [node]
                    # elif 0: # no problem.
                        # node.stc_child_nodes = None
                        # node.stc_child_statements = None
                    # elif 0: # worst.
                        # node.stc_child_nodes = {}
                        # node.stc_child_statements = {} 
                    # else: # worst.
                    # self.parent.stc_child_nodes.append(node)
                    node.stc_child_nodes = [] # 0.58 -> 1.70.
                        # node.stc_child_statements = [] # 1.70 -> 2.81.
                    # for z in node._fields: assert not z.startswith('stc_')
                elif kind == 2:
                    for i in range(100):
                        x = []
                #@-<< code that demonstrates the anomaly >>
            # Save the previous context & parent & inject references.
            # Injecting these two references is cheap.
            node.stc_context = self.context
            node.stc_parent = self.parent
            # Visit the children with the new parent.
            self.parent = node
            method = getattr(self,'do_' + node.__class__.__name__)
            method(node)
            # Restore the context & parent.
            self.context = node.stc_context
            self.parent = node.stc_parent
        #@+node:ekr.20140526082700.17351: *4* p1.define_name
        def define_name(self,cx,name,defined=True):
            '''
            Fix the scope of the given name to cx.
            Set the bit in stc_defined_table if defined is True.
            '''
            st = cx.stc_symbol_table
            d = st.d
            if name not in d.keys():
                self.n_defined += 1
                d[name] = [] # The type list.
            if defined:
                st.defined.add(name)
        #@+node:ekr.20140526082700.17352: *4* p1.visitors
        #@+node:ekr.20140526082700.17353: *5* p1.Attribute
        # Attribute(expr value, identifier attr, expr_context ctx)

        def do_Attribute(self,node):
            
            self.n_attributes += 1
            self.visit(node.value)
            cx = node.stc_context
            st = cx.stc_symbol_table
            d = st.attrs_d
            key = node.attr
            val = node.value
            # The following lines are expensive!
            # For Leo P1: 2.0 sec -> 2.5 sec.
            if d.has_key(key):
                d.get(key).add(val)
            else:
                aSet = set()
                aSet.add(val)
                d[key] = aSet
            # self.visit(node.ctx)
            if isinstance(node.ctx,(ast.Param,ast.Store)):
                st.defined_attrs.add(key)
        #@+node:ekr.20140526082700.17354: *5* p1.AugAssign (sets in_aug_assign)
        # AugAssign(expr target, operator op, expr value)

        def do_AugAssign(self,node):
            
            # g.trace('FT',self.u.format(node),g.callers())
            assert not self.in_aug_assign
            try:
                self.in_aug_assign = True
                self.visit(node.target)
            finally:
                self.in_aug_assign = False
            self.visit(node.value)
        #@+node:ekr.20140526082700.17355: *5* p1.ClassDef
        # ClassDef(identifier name, expr* bases, stmt* body, expr* decorator_list)

        def do_ClassDef (self,node):

            self.n_contexts += 1
            parent_cx = self.context
            assert parent_cx == node.stc_context
            # Inject the symbol table for this node.
            node.stc_symbol_table = SymbolTable(parent_cx)
            # Define the function name itself in the enclosing context.
            self.define_name(parent_cx,node.name)
            # Visit the children in a new context.
            self.context = node
            for z in node.bases:
                self.visit(z)
            for z in node.body:
                self.visit(z)
            for z in node.decorator_list:
                self.visit(z)
            self.context = parent_cx
        #@+node:ekr.20140526082700.17356: *5* p1.FunctionDef
        # FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list)

        def do_FunctionDef (self,node):
            
            self.n_contexts += 1
            parent_cx = self.context
            assert parent_cx == node.stc_context
            # Inject the symbol table for this node.
            node.stc_symbol_table = SymbolTable(parent_cx)
            # Define the function name itself in the enclosing context.
            self.define_name(parent_cx,node.name)
            # Visit the children in a new context.
            self.context = node
            self.visit(node.args)
            for z in node.body:
                self.visit(z)
            for z in node.decorator_list:
                self.visit(z)
            self.context = parent_cx

        #@+node:ekr.20140526082700.17357: *5* p1.Global
        # Global(identifier* names)

        def do_Global(self,node):
            
            cx = self.u.compute_module_cx(node)
            assert hasattr(cx,'stc_symbol_table'),cx
            node.stc_scope = cx
            for name in node.names:
                self.define_name(cx,name)
        #@+node:ekr.20140526082700.17358: *5* p1.Import & ImportFrom
        # Import(alias* names)
        def do_Import(self,node):
            self.alias_helper(node)
                    
        # ImportFrom(identifier? module, alias* names, int? level)
        def do_ImportFrom(self,node):
            self.alias_helper(node)

        # alias (identifier name, identifier? asname)
        def alias_helper(self,node):
            cx = node.stc_context
            assert cx
            for alias in node.names:
                name = alias.asname if alias.asname else alias.name.split('.')[0]
                # if alias.asname: g.trace('%s as %s' % (alias.name,alias.asname))
                self.define_name(cx,name)
        #@+node:ekr.20140526082700.17359: *5* p1.Lambda
        # Lambda(arguments args, expr body)

        def do_Lambda(self,node):
            
            self.n_contexts += 1
            parent_cx = self.context
            assert parent_cx == node.stc_context
            # Inject the symbol table for this node.
            node.stc_symbol_table = SymbolTable(parent_cx)
            # There is no lambda name.
            # Handle the lambda args.
            for arg in node.args.args:
                if isinstance(arg,ast.Name):
                    # Python 2.x.
                    assert isinstance(arg.ctx,ast.Param),arg.ctx
                    # Define the arg in the lambda context.
                    self.define_name(node,arg.id)
                elif isinstance(arg,ast.Tuple):
                    pass
                else:
                    # Python 3.x.
                    g.trace('===============',self.u.format(node))
                    ### assert isinstance(arg,ast.arg),arg
                    ### assert isinstance(arg,ast.arg),arg
                    ### self.define_name(node,arg.arg)
                arg.stc_scope = node
            # Visit the children in the new context.
            self.context = node
            # self.visit(node.args)
            self.visit(node.body)
            self.context = parent_cx
        #@+node:ekr.20140526082700.17360: *5* p1.Module
        def do_Module (self,node):

            self.n_contexts += 1
            assert self.context is None
            assert node.stc_context is None
            # Inject the symbol table for this node.
            node.stc_symbol_table = SymbolTable(node)
            # Visit the children in the new context.
            self.context = node
            for z in node.body:
                self.visit(z)
            self.context = None
        #@+node:ekr.20140526082700.17361: *5* p1.Name
        # Name(identifier id, expr_context ctx)

        def do_Name(self,node):

            # g.trace('P1',node.id)
            
            # self.visit(node.ctx)
            cx = node.stc_context
            if isinstance(node.ctx,(ast.Param,ast.Store)):
                # The scope is unambigously cx, **even for AugAssign**.
                # If there is no binding, we will get an UnboundLocalError at run time.
                # However, AugAssigns do not actually assign to the var.
                assert hasattr(cx,'stc_symbol_table'),cx
                self.define_name(cx,node.id,defined = not self.in_aug_assign)
                node.stc_scope = cx
            else:
                # ast.Store does *not* necessarily define the scope.
                # For example, a += 1 generates a Store, but does not defined the symbol.
                # Instead, only ast.Assign nodes really define a symbol.
                node.stc_scope = None
        #@-others
    #@+node:ekr.20140526082700.17315: *3* class StatementTraverser
    class StatementTraverser(AstBaseTraverser):
            
        # def __init__(self):
            # AstBaseTraverser.__init__(self)

        #@+others
        #@+node:ekr.20140526082700.17316: *4* stat.run
        def run(self,node):

            # Only the top-level contexts visit their children.
            if isinstance(node,(ast.ClassDef,ast.FunctionDef,ast.Module)):
                for z in node.body:
                    self.visit(z)
            elif isinstance(node,ast.Lambda):
                self.visit(node.body)
            else:
                g.trace(node)
                assert False,'(Statement_Traverser) node must be a context'
        #@+node:ekr.20140526082700.17317: *4* stat.visit & default_visitor
        def visit(self,node):

            assert isinstance(node,ast.AST),node.__class__.__name__
            method_name = 'do_' + node.__class__.__name__
            method = getattr(self,method_name,self.default_visitor)
            return method(node)

        def default_visitor(self,node):
            pass
        #@+node:ekr.20140526082700.17318: *4* stat.visitors
        # There are no visitors for context nodes.
        #@+node:ekr.20140526082700.17319: *5* stat.ExceptHandler
        # ExceptHandler(expr? type, expr? name, stmt* body)

        def do_ExceptHandler(self,node):

            for z in node.body:
                self.visit(z)
        #@+node:ekr.20140526082700.17320: *5* stat.For
        # For(expr target, expr iter, stmt* body, stmt* orelse)

        def do_For (self,tree):

            for z in tree.body:
                self.visit(z)
            for z in tree.orelse:
                self.visit(z)

        #@+node:ekr.20140526082700.17321: *5* stat.If
        # If(expr test, stmt* body, stmt* orelse)

        def do_If(self,node):

            for z in node.body:
                self.visit(z)
            for z in node.orelse:
                self.visit(z)
        #@+node:ekr.20140526082700.17322: *5* stat.TryExcept
        # TryExcept(stmt* body, excepthandler* handlers, stmt* orelse)

        def do_TryExcept(self,node):
            
            for z in node.body:
                self.visit(z)
            for z in node.handlers:
                self.visit(z)
            for z in node.orelse:
                self.visit(z)
        #@+node:ekr.20140526082700.17323: *5* stat.TryFinally
        # TryFinally(stmt* body, stmt* finalbody)

        def do_TryFinally(self,node):

            for z in node.body:
                self.visit(z)
            for z in node.finalbody:
                self.visit(z)
        #@+node:ekr.20140526082700.17324: *5* stat.While
        # While(expr test, stmt* body, stmt* orelse)

        def do_While (self,node):

            for z in node.body:
                self.visit(z)
            for z in node.orelse:
                self.visit(z)
        #@+node:ekr.20140526082700.17325: *5* stat.With
        # With(expr context_expr, expr? optional_vars, stmt* body)

        def do_With (self,node):

            for z in node.body:
                self.visit(z)
            
        #@-others
    #@+node:ekr.20140526082700.17390: *3* class Stats
    class Stats(BaseStats):
        
        def __init__(self):
            BaseStats.__init__(self)
                
        #@+others
        #@+node:ekr.20140526082700.17391: *4* stats.init_ivars
        def init_ivars (self):
            '''Init all inference statistics.'''
            self.n_files = 0
            # Dictionaries for computing distributions.
            # Keys are lengths (ints); values are counts for each lenght (ints).
            self.actual_args_dict = {}
            self.formal_args_dict = {}
            # Errors & warnings.
            self.n_errors = 0
            self.n_warnings = 0
            # Pre-passes...
            self.n_chains = 0
            self.n_contexts = 0
            self.n_files = 0 # set only in print_stats.
            self.n_library_modules = 0
            self.n_modules = 0
            self.n_relinked_pointers = 0
            # self.n_resolvable_names = 0
            self.n_resolved_contexts = 0
            self.n_relinked_names = 0
            # Cache & circular inferences
            self.n_assign_hits = 0
            self.n_assign_fails = 0
            self.n_assign_misses = 0
            self.n_call_hits = 0
            self.n_call_misses = 0
            self.n_circular_assignments = 0
            self.n_outer_expr_hits = 0
            self.n_outer_expr_misses = 0
            self.n_recursive_calls = 0
            # Inference...
            self.n_attr_fail = 0
            self.n_attr_success = 0
            self.n_binop_fail = 0
            self.n_caches = 0
            self.n_clean_fail = 0
            self.n_clean_success = 0
            self.n_find_call_e_fail = 0
            self.n_find_call_e_success = 0
            self.n_fuzzy = 0
            self.n_not_fuzzy = 0
            self.n_return_fail = 0
            self.n_return_success = 0
            self.n_ti_calls = 0
            self.n_unop_fail = 0
            # Names...
            self.n_attributes = 0
            self.n_ivars = 0
            self.n_names = 0        # Number of symbol table entries.
            self.n_del_names = 0
            self.n_load_names = 0
            self.n_param_names = 0
            self.n_param_refs = 0
            self.n_store_names = 0
            # Statements...
            self.n_assignments = 0
            self.n_calls = 0
            self.n_classes = 0
            self.n_defs = 0
            self.n_expressions = 0 # Outer expressions, ast.Expr nodes.
            self.n_fors = 0
            self.n_globals = 0
            self.n_imports = 0
            self.n_lambdas = 0
            self.n_list_comps = 0
            self.n_returns = 0
            self.n_withs = 0
            # Times...
            self.parse_time = 0.0
            self.pass1_time = 0.0
            self.pass2_time = 0.0
            self.total_time = 0.0
        #@+node:ekr.20140526082700.17392: *4* stats.init_tables
        def init_tables(self):

            self.table = (
                # '*', 'errors',

                '*Pass1',
                'files','classes','contexts','defs','library_modules','modules',
                
                '*Statements',
                'assignments','calls','expressions','fors','globals','imports',
                'lambdas','list_comps','returns','withs',
                
                '*Names',
                'attributes','del_names','load_names','names',
                'param_names','param_refs','store_names',
                # 'resolvable_names',
                'relinked_names','relinked_pointers',
                
                '*Inference',
                'assign_hits','assign_fails','assign_misses',
                'attr_fail','attr_success',
                'call_hits','call_misses','recursive_calls',
                'circular_assignments',
                'clean_fail','clean_success',
                'find_call_e_fail','find_call_e_success',
                'fuzzy','not_fuzzy',
                'outer_expr_hits','outer_expr_misses',
                'return_fail','return_success',
                'ti_calls',
                'unop_fail',

                '*Errors & Warnings',
                'errors',
                'warnings',
            )
            
            self.always_report = (
                'n_assign_hits',
                'n_call_hits',
                'n_outer_expr_hits',
                'n_recursive_calls',
                'n_fuzzy',
            )
            
            self.distribution_table = (
                (self.actual_args_dict,'actual args'),
                (self.formal_args_dict,'formal args'),
            )
        #@-others
    #@+node:ekr.20140526082700.17508: *3* Generator classes
    #@+node:ekr.20140526082700.17509: *4* .class NodeGenerator
    # Slightly slower than NodePseudoGenerator, but generates no data.

    class NodeGenerator:
        
        # def __init__(self):
            # pass
        
        # This "convenience" would be a big overhead!
        # def __call__(self,node):
            # for z in self.visit(node):
                # yield z
        
        #@+others
        #@+node:ekr.20140526082700.17510: *5* visit
        def visit(self,node):

            assert isinstance(node,ast.AST),node.__class__.__name__
            method_name = 'do_' + node.__class__.__name__
            method = getattr(self,method_name)
            yield node
            for node2 in method(node):
                yield node2
                
        # Avoid the overhead of an extra layer.
        run = visit

        if 0: # No longer used: all referenced visitors must exist.
            def default_visitor(self,node):
                '''yield all the children of a node without children.'''
                raise StopIteration
        #@+node:ekr.20140526082700.17511: *5* fg.operators
        #@+node:ekr.20140526082700.17512: *6* fg.do-nothings
        def do_Bytes(self,node): 
            raise StopIteration
                # Python 3.x only.
            
        def do_Ellipsis(self,node):
            raise StopIteration
            
        # Num(object n) # a number as a PyObject.
        def do_Num(self,node):
            raise StopIteration
               
        def do_Str (self,node):
            raise StopIteration
                # represents a string constant.
        #@+node:ekr.20140526082700.17513: *6* fg.arguments
        # arguments = (expr* args, identifier? vararg, identifier? kwarg, expr* defaults)

        def do_arguments(self,node):
            
            for z in node.args:
                for z2 in self.visit(z):
                    yield z2
            for z in node.defaults:
                for z2 in self.visit(z):
                    yield z2
        #@+node:ekr.20140526082700.17514: *6* fg.Attribute
        # Attribute(expr value, identifier attr, expr_context ctx)

        def do_Attribute(self,node):
            
            for z in self.visit(node.value):
                yield z
            # yield node.ctx
        #@+node:ekr.20140526082700.17515: *6* fg.BinOp
        # BinOp(expr left, operator op, expr right)

        def do_BinOp (self,node):
            
            for z in self.visit(node.left):
                yield z
            # yield node.op
            for z in self.visit(node.right):
                yield z
        #@+node:ekr.20140526082700.17516: *6* fg.BoolOp
        # BoolOp(boolop op, expr* values)

        def do_BoolOp (self,node):

            # yield node.op
            for z in node.values:
                for z2 in self.visit(z):
                    yield z2
        #@+node:ekr.20140526082700.17517: *6* fg.Call
        # Call(expr func, expr* args, keyword* keywords, expr? starargs, expr? kwargs)

        def do_Call(self,node):
            
            for z in self.visit(node.func):
                yield z
            for z in node.args:
                for z2 in self.visit(z):
                    yield z2
            for z in node.keywords:
                for z2 in self.visit(z):
                    yield z2
            if getattr(node,'starargs',None):
                for z in self.visit(node.starargs):
                    yield z
            if getattr(node,'kwargs',None):
                for z in self.visit(node.kwargs):
                    yield z
        #@+node:ekr.20140526082700.17518: *6* fg.Compare
        # Compare(expr left, cmpop* ops, expr* comparators)

        def do_Compare(self,node):
            
            for z in self.visit(node.left):
                yield z
            # for z in node ops:
                # yield z
            for z in node.comparators:
                for z2 in self.visit(z):
                    yield z2
        #@+node:ekr.20140526082700.17519: *6* fg.comprehension
        # comprehension (expr target, expr iter, expr* ifs)

        def do_comprehension(self,node):

            for z in self.visit(node.target): # a Name.
                yield z
            for z in self.visit(node.iter): # An Attribute.
                yield z
            for z in node.ifs: ### Does not appear in AstFullTraverser!
                for z2 in self.visit(z):
                    yield z2
        #@+node:ekr.20140526082700.17520: *6* fg.Dict
        # Dict(expr* keys, expr* values)

        def do_Dict(self,node):
            
            for z in node.keys:
                for z2 in self.visit(z):
                    yield z2
            for z in node.values:
                for z2 in self.visit(z):
                    yield z2
        #@+node:ekr.20140526082700.17521: *6* fg.Expr
        # Expr(expr value)

        def do_Expr(self,node):
            
            for z in self.visit(node.value):
                yield z
        #@+node:ekr.20140526082700.17522: *6* fg.Expression
        def do_Expression(self,node):
            
            '''An inner expression'''
            for z in self.visit(node.body):
                yield z
        #@+node:ekr.20140526082700.17523: *6* fg.ExtSlice
        # ExtSlice(slice* dims) 

        def do_ExtSlice (self,node):
            
            for z in node.dims:
                for z2 in self.visit(z):
                    yield z2
        #@+node:ekr.20140526082700.17524: *6* fg.GeneratorExp
        # GeneratorExp(expr elt, comprehension* generators)

        def do_GeneratorExp(self,node):
            
            for z in self.visit(node.elt):
                yield z
            for z in node.generators:
                for z2 in self.visit(z):
                    yield z2
        #@+node:ekr.20140526082700.17525: *6* fg.ifExp (ternary operator)
        # IfExp(expr test, expr body, expr orelse)

        def do_IfExp (self,node):

            for z in self.visit(node.body):
                yield z
            for z in self.visit(node.test):
                yield z
            for z in self.visit(node.orelse):
                yield z
        #@+node:ekr.20140526082700.17526: *6* fg.Index
        # Index(expr value)

        def do_Index (self,node):
            
            for z in self.visit(node.value):
                yield z
        #@+node:ekr.20140526082700.17527: *6* fg.keyword
        # keyword = (identifier arg, expr value)

        def do_keyword(self,node):

            # node.arg is a string.
            for z in self.visit(node.value):
                yield z
        #@+node:ekr.20140526082700.17528: *6* fg.Lambda
        # Lambda(arguments args, expr body)

        def do_Lambda(self,node):
            
            for z in self.visit(node.args):
                yield z
            for z in self.visit(node.body):
                yield z
        #@+node:ekr.20140526082700.17529: *6* fg.List & ListComp
        # List(expr* elts, expr_context ctx) 

        def do_List(self,node):
            
            for z in node.elts:
                for z2 in self.visit(z):
                    yield z2
            # yield node.ctx

        # ListComp(expr elt, comprehension* generators)

        def do_ListComp(self,node):

            for z in self.visit(node.elt):
                yield z
            for z in node.generators:
                for z2 in self.visit(z):
                    yield z2
        #@+node:ekr.20140526082700.17530: *6* fg.Name (revise)
        # Name(identifier id, expr_context ctx)

        def do_Name(self,node):
            # yield node.ctx
            raise StopIteration
        #@+node:ekr.20140526082700.17531: *6* fg.Repr
        # Python 2.x only
        # Repr(expr value)

        def do_Repr(self,node):

            for z in self.visit(node.value):
                yield z
        #@+node:ekr.20140526082700.17532: *6* fg.Slice
        def do_Slice (self,node):

            if getattr(node,'lower',None):
                for z in self.visit(node.lower):
                    yield z            
            if getattr(node,'upper',None):
                for z in self.visit(node.upper):
                    yield z
            if getattr(node,'step',None):
                for z in self.visit(node.step):
                    yield z
        #@+node:ekr.20140526082700.17533: *6* fg.Subscript
        # Subscript(expr value, slice slice, expr_context ctx)

        def do_Subscript(self,node):
            
            for z in self.visit(node.value):
                yield z
            for z in self.visit(node.slice):
                yield z
            # yield node.ctx
        #@+node:ekr.20140526082700.17534: *6* fg.Tuple
        # Tuple(expr* elts, expr_context ctx)

        def do_Tuple(self,node):
            
            for z in node.elts:
                for z2 in self.visit(z):
                    yield z2
            # yield node.ctx
        #@+node:ekr.20140526082700.17535: *6* fg.UnaryOp
        # UnaryOp(unaryop op, expr operand)

        def do_UnaryOp (self,node):
            
            # for z in self.visit(node.op):
                # yield z
            for z in self.visit(node.operand):
                yield z
        #@+node:ekr.20140526082700.17536: *5* fg.statements
        #@+node:ekr.20140526082700.17537: *6* fg.alias
        # identifier name, identifier? asname)

        def do_alias (self,node):
            raise StopIteration
        #@+node:ekr.20140526082700.17538: *6* fg.Assert
        # Assert(expr test, expr? msg)

        def do_Assert(self,node):

            for z in self.visit(node.test):
                yield z
            if node.msg:
                for z in self.visit(node.msg):
                    yield z

        #@+node:ekr.20140526082700.17539: *6* fg.Assign
        # Assign(expr* targets, expr value)

        def do_Assign(self,node):

            for z in node.targets:
                for z2 in self.visit(z):
                    yield z2
            for z in self.visit(node.value):
                yield z
                
        #@+node:ekr.20140526082700.17540: *6* fg.AugAssign
        # AugAssign(expr target, operator op, expr value)

        def do_AugAssign(self,node):
            
            for z in self.visit(node.target):
                yield z
            # yield node.op
            for z in self.visit(node.value):
                yield z
        #@+node:ekr.20140526082700.17541: *6* fg.Break
        def do_Break(self,node):

            raise StopIteration

        #@+node:ekr.20140526082700.17542: *6* fg.ClassDef
        # ClassDef(identifier name, expr* bases, stmt* body, expr* decorator_list)

        def do_ClassDef (self,node):

            for z in node.bases:
                for z2 in self.visit(z):
                    yield z2
            for z in node.body:
                for z2 in self.visit(z):
                    yield z2
            for z in node.decorator_list:
                for z2 in self.visit(z):
                    yield z2
        #@+node:ekr.20140526082700.17543: *6* fg.Continue
        def do_Continue(self,node):

            raise StopIteration

        #@+node:ekr.20140526082700.17544: *6* fg.Delete
        # Delete(expr* targets)

        def do_Delete(self,node):

            for z in node.targets:
                for z2 in self.visit(z):
                    yield z2
        #@+node:ekr.20140526082700.17545: *6* fg.ExceptHandler
        # ExceptHandler(expr? type, expr? name, stmt* body)

        def do_ExceptHandler(self,node):
            
            if node.type:
                for z in self.visit(node.type):
                    yield z
            if node.name:
                for z in self.visit(node.name):
                    yield z
            for z in node.body:
                for z2 in self.visit(z):
                    yield z2
        #@+node:ekr.20140526082700.17546: *6* fg.Exec
        # Python 2.x only
        # Exec(expr body, expr? globals, expr? locals)

        def do_Exec(self,node):

            for z in self.visit(node.body):
                yield z
            if getattr(node,'globals',None):
                for z in self.visit(node.globals):
                    yield z
            if getattr(node,'locals',None):
                for z in self.visit(node.locals):
                    yield z
        #@+node:ekr.20140526082700.17547: *6* fg.For
        # For(expr target, expr iter, stmt* body, stmt* orelse)

        def do_For (self,node):

            for z in self.visit(node.target):
                yield z
            for z in self.visit(node.iter):
                yield z
            for z in node.body:
                for z2 in self.visit(z):
                    yield z2
            for z in node.orelse:
                for z2 in self.visit(z):
                    yield z2
        #@+node:ekr.20140526082700.17548: *6* fg.FunctionDef
        # FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list)

        def do_FunctionDef (self,node):
            
            for z in self.visit(node.args):
                yield z
            for z in node.body:
                for z2 in self.visit(z):
                    yield z2
            for z in node.decorator_list:
                for z2 in self.visit(z):
                    yield z2
        #@+node:ekr.20140526082700.17549: *6* fg.Global
        # Global(identifier* names)

        def do_Global(self,node):

            raise StopIteration
        #@+node:ekr.20140526082700.17550: *6* fg.If
        # If(expr test, stmt* body, stmt* orelse)

        def do_If(self,node):
            
            for z in self.visit(node.test):
                yield z
            for z in node.body:
                for z2 in self.visit(z):
                    yield z2
            for z in node.orelse:
                for z2 in self.visit(z):
                    yield z2
        #@+node:ekr.20140526082700.17551: *6* fg.Import & ImportFrom
        # Import(alias* names)

        def do_Import(self,node):

            raise StopIteration

        # ImportFrom(identifier? module, alias* names, int? level)

        def do_ImportFrom(self,node):
            
            for z in node.names:
                for z2 in self.visit(z):
                    yield z2
        #@+node:ekr.20140526082700.17552: *6* fg.Module
        def do_Module(self,node):

            for z in node.body:
                for z2 in self.visit(z):
                    yield z2
        #@+node:ekr.20140526082700.17553: *6* fg.Pass
        def do_Pass(self,node):

            raise StopIteration

        #@+node:ekr.20140526082700.17554: *6* fg.Print
        # Python 2.x only
        # Print(expr? dest, expr* values, bool nl)
        def do_Print(self,node):

            if getattr(node,'dest',None):
                for z in self.visit(node.dest):
                    yield z
            for z in node.values:
                for z2 in self.visit(z):
                    yield z2
        #@+node:ekr.20140526082700.17555: *6* fg.Raise
        # Raise(expr? type, expr? inst, expr? tback)

        def do_Raise(self,node):
            
            if getattr(node,'type',None):
                for z in self.visit(node.type):
                    yield z
            if getattr(node,'inst',None):
                for z in self.visit(node.inst):
                    yield z
            if getattr(node,'tback',None):
                for z in self.visit(node.tback):
                    yield z
        #@+node:ekr.20140526082700.17556: *6* fg.Return
        # Return(expr? value)

        def do_Return(self,node):
            
            if node.value:
                for z in self.visit(node.value):
                    yield z
        #@+node:ekr.20140526082700.17557: *6* fg.TryExcept
        # TryExcept(stmt* body, excepthandler* handlers, stmt* orelse)

        def do_TryExcept(self,node):
            
            for z in node.body:
                for z2 in self.visit(z):
                    yield z2
            for z in node.handlers:
                for z2 in self.visit(z):
                    yield z2
            for z in node.orelse:
                for z2 in self.visit(z):
                    yield z2
        #@+node:ekr.20140526082700.17558: *6* fg.TryFinally
        # TryFinally(stmt* body, stmt* finalbody)

        def do_TryFinally(self,node):

            for z in node.body:
                for z2 in self.visit(z):
                    yield z2
            for z in node.finalbody:
                for z2 in self.visit(z):
                    yield z2
        #@+node:ekr.20140526082700.17559: *6* fg.While
        # While(expr test, stmt* body, stmt* orelse)

        def do_While (self,node):

            for z in node.body:
                for z2 in self.visit(z):
                    yield z2
            for z in node.orelse:
                for z2 in self.visit(z):
                    yield z2
        #@+node:ekr.20140526082700.17560: *6* fg.With
        # With(expr context_expr, expr? optional_vars, stmt* body)

        def do_With (self,node):
            
            for z in self.visit(node.context_expr):
                yield z
            if node.optional_vars:
                for z in self.visit(node.optional_vars):
                    yield z
            for z in node.body:
                for z2 in self.visit(z):
                    yield z2
        #@+node:ekr.20140526082700.17561: *6* fg.Yield
        #  Yield(expr? value)

        def do_Yield(self,node):

            if node.value:
                for z in self.visit(node.value):
                    yield z
        #@-others
    #@+node:ekr.20140526082700.17562: *4* class AllStatementsPseudoGenerator
    class AllStatementsPseudoGenerator(AllStatementsTraverser):
        
        # def __init__(self,node):
            # Statement_Traverser.__init__(self)
            
        def __call__(self,node):
            return self.run(node)
           
        def run(self,node):
            self.result = []
            if isinstance(node,(ast.ClassDef,ast.FunctionDef,ast.Module)):
                for z in node.body:
                    self.visit(z)
                return self.result
            elif isinstance(node,ast.Lambda):
                self.result = []
                self.visit(node.body)
            else:
                g.trace('Statement_Generator: node must be a context: %s' % (
                    Utils().format(node)))
                assert False,node
            return self.result
            
        def default_visitor(self,node):
            pass

        def visit(self,node):
            assert isinstance(node,ast.AST),node.__class__.__name__
            method_name = 'do_' + node.__class__.__name__
            method = getattr(self,method_name,self.default_visitor)
            self.result.append(node)
            method(node)
    #@+node:ekr.20140526082700.17563: *4* class LocalNodeGenerator
    class LocalNodeGenerator(NodeGenerator):
        
        '''Same as NodeGenerator, but don't enter context nodes.'''
        
        def run(self,node):
            if isinstance(node,(ast.ClassDef,ast.FunctionDef,ast.Module)):
                for z in node.body:
                    for z2 in self.visit(z):
                        yield z2
            elif isinstance(node,ast.Lambda):
                for z in self.visit(node.body):
                    yield z
            else:
                # It *is* valid to visit the nodes of a non-context statement.
                for z in self.visit(node):
                    yield z
        
        def do_ClassDef(self,node):
            raise StopIteration
        
        def do_FunctionDef(self,node):
            raise StopIteration
            
        def do_Lambda(self,node):
            raise StopIteration

        def do_Module(self,node):
            assert False,node
    #@+node:ekr.20140526082700.17564: *4* class LocalStatementGenerator (best so far)
    class LocalStatementGenerator:
        
        def run(self,node):
            if isinstance(node,(ast.ClassDef,ast.FunctionDef,ast.Module)):
                # g.trace(node,node.body)
                for z in node.body:
                    for z2 in self.visit(z):
                        yield z2
            else:
                assert isinstance(node,ast.Lambda),node.__class__.__name__
                for z in self.visit(node.body):
                    yield z
                    
        def default(self,node):
            raise StopIteration
                
        def visit(self,node):
            if isinstance(node,(ast.ClassDef,ast.FunctionDef,ast.Lambda)):
                yield node # These *are* part of the local statements.
                for z in node.body:
                    for z2 in self.visit(z):
                        yield z2
            else:
                yield node
                method = getattr(self,'do_'+node.__class__.__name__,self.default)
                for z in method(node):
                    yield z

        #@+others
        #@+node:ekr.20140526082700.17565: *5* sg.ExceptHandler
        # ExceptHandler(expr? type, expr? name, stmt* body)

        def do_ExceptHandler(self,node):

            for z in node.body:
                for z2 in self.visit(z):
                    yield z2
        #@+node:ekr.20140526082700.17566: *5* sg.For
        # For(expr target, expr iter, stmt* body, stmt* orelse)

        def do_For (self,node):

            for z in node.body:
                for z2 in self.visit(z):
                    yield z2
            for z in node.orelse:
                for z2 in self.visit(z):
                    yield z2
        #@+node:ekr.20140526082700.17567: *5* sg.If
        # If(expr test, stmt* body, stmt* orelse)

        def do_If(self,node):
            
            for z in node.body:
                for z2 in self.visit(z):
                    yield z2
            for z in node.orelse:
                for z2 in self.visit(z):
                    yield z2
        #@+node:ekr.20140526082700.17568: *5* sg.TryExcept
        # TryExcept(stmt* body, excepthandler* handlers, stmt* orelse)

        def do_TryExcept(self,node):
            
            for z in node.body:
                for z2 in self.visit(z):
                    yield z2
            for z in node.handlers:
                for z2 in self.visit(z):
                    yield z2
            for z in node.orelse:
                for z2 in self.visit(z):
                    yield z2
        #@+node:ekr.20140526082700.17569: *5* sg.TryFinally
        # TryFinally(stmt* body, stmt* finalbody)

        def do_TryFinally(self,node):

            for z in node.body:
                for z2 in self.visit(z):
                    yield z2
            for z in node.finalbody:
                for z2 in self.visit(z):
                    yield z2
        #@+node:ekr.20140526082700.17570: *5* sg.While
        # While(expr test, stmt* body, stmt* orelse)

        def do_While (self,node):

            for z in node.body:
                for z2 in self.visit(z):
                    yield z2
            for z in node.orelse:
                for z2 in self.visit(z):
                    yield z2
        #@+node:ekr.20140526082700.17571: *5* sg.With
        # With(expr context_expr, expr? optional_vars, stmt* body)

        def do_With (self,node):

            for z in node.body:
                for z2 in self.visit(z):
                    yield z2
        #@-others

    #@-others
#@+node:ekr.20140615102615.17727: ** class Context
class Context:
    '''A class representing contexts: modules, classes, defs, lambdas, etc.'''
    def __init__(self,kind,name,node,parent_cx,parent_cx_obj):
        '''Ctor for Context class.'''
        self.child_contexts = []
        self.kind = kind
        self.name = name # The context name.
            # A filename for Modules; 'lambda n' for lambda.
        self.node = node # An ast node.
        self.parent_cx = parent_cx # An ast node or None.
        self.parent_cx_obj = parent_cx_obj # A Context object or None
        self.st = SymbolTable(cx=self)

    def __repr__ (self):
        return 'Cx:<%s>' % self.full_name()
    __str__ = __repr__

    #@+others
    #@+node:ekr.20140616055519.17779: *3* cx.full/short_name
    def full_name (self):
        '''Return a string containing the names of a context and its ancestors.'''
        cx,names = self,[]
        while cx:
            names.append(cx.name)
            cx = cx.parent_cx_obj
        return ':'.join(reversed(names))

    def short_name(self):
        '''Return the short name of the context.'''
        return self.name
    #@+node:ekr.20140615102615.17733: *3* cx.comparisons
    def __eq__(self, other):
        return self.full_name() == other.full_name()
    def __ne__(self, other):
        return self.full_name() != other.full_name()
    def __lt__(self, other): return NotImplemented 
    def __le__(self, other): return NotImplemented
    def __gt__(self, other): return NotImplemented 
    def __ge__(self, other): return NotImplemented

    def __hash__ (self):
        # Define __hash__ **only** if __eq__ is also defined.
        return self.full_name()
    #@-others
#@+node:ekr.20140601151054.17640: ** class Data2
class Data2(AstFullTraverser):
    '''
    Traversal to create global data dict d.
    
    Like P1, this class injects stc_parent and stc_context links.
    Unlike P1, this class does not inject stc_symbol_table links.
    '''
    #@+others
    #@+node:ekr.20140604135104.17795: *3*  class d2.NameData
    class NameData:
        '''A class holding all data related to a name (spelling).'''
        def __init__(self,cx_node,cx_obj,kind,node):
            self.cx_node = cx_node # The context ast node in which the data appears.
            self.cx_obj = cx_obj # The Context object in which the data appears.
            self.kind = kind # in ('def','ref','import')
            self.node = node # The ast.node at which the datum occurs.
            
        def __repr__(self):
            u = Utils()
            return 'NameData(%4s,cx: %20s, node: %s)' % (
                self.kind,u.format(self.cx_node),u.format(self.node))
                
        __str__ = __repr__
    #@+node:ekr.20140601151054.17642: *3*  d2.ctor & init & __call__
    def __init__(self):
        AstFullTraverser.__init__(self)
        self.global_d = {} # Keys are names; values are NameData objects.
        self.contexts_d = {}
            # Keys are full context names; values are Context objects.
        self.defs_d = {}
        self.refs_d = {}
        self.u = Utils()
        self.init()
        
    def init(self):
        '''(Re)init all non-global ivars.'''
        self.arg_node = None # The enclosing argument expression.
        self.assign_node = None # Enclosing Assign node.
        self.aug_assign_node = None # Enclosing AugAssign node.
        self.cx_node = None
        self.cx_obj = None
        self.lambdas = 0 # Number of lambda's seen in module.
        self.module_cx = None
        self.module_cx_obj = None
        # self.n_attributes = 0
        # self.n_contexts = 0
        # self.n_nodes = 0
        self.parent = None

    def __call__(self,fn,node):
        self.run(fn,node)
    #@+node:ekr.20140601151054.17643: *3*  d2.run (entry point)
    def run (self,fn,root,post_pass=False):
        '''Run the prepass: init, then visit the root.'''
        # pylint: disable=arguments-differ
        # Init all ivars.
        self.init()
        self.fn = fn
        self.visit(root)
    #@+node:ekr.20140601151054.17644: *3*  d2.visit
    def visit(self,node):
        '''Visit a node and all its descendants, creating the dictionaries of this class.'''
        assert isinstance(node,ast.AST),node.__class__.__name__
        # self.n_nodes += 1
        # Patch the node.
        node.stc_cx_node = self.cx_node
        node.stc_cx_obj = self.cx_obj
        node.stc_parent = self.parent
        # Save the previous context and parent.
        old_cx_node,old_cx_obj,old_parent = self.cx_node,self.cx_obj,self.parent
        # Visit the node with the new parent.
        self.parent = node
        method = getattr(self,'do_' + node.__class__.__name__)
        method(node)
        # Restore the previous context and parent.
        self.cx_node,self.cx_obj,self.parent = old_cx_node,old_cx_obj,old_parent
    #@+node:ekr.20140601151054.17645: *3* d2.define_name
    def define_name(self,name,node):
        '''Called when name is defined in the given context.'''
        # Note: cx (an AST node) is hashable.
        trace = False
        cx_node,cx_obj = self.cx_node,self.cx_obj
        if trace:
            u = self.u
            # g.trace(node.__class__.__name__)
            if isinstance(node,ast.Name):
                if trace: 
                    if isinstance(parent,ast.arguments):
                        g.trace('%-10s parent: args = [%s]' % (
                            name,u.format(parent)))
                    else:
                        g.trace('%-10s parent: %s (parent = %s)' % (
                            name,u.format(parent),parent.__class__.__name__))
            else:
                if trace: g.trace('%-10s node  : %s' % (name,u.format(node)))
        # Sets don't work all that well here.
        aSet = self.defs_d.get(name,set())
        aSet.add(cx_node)
        self.defs_d[name] = aSet
        aList = self.global_d.get(name,[])
        aList.append(self.NameData(cx_node,cx_obj,'def',node))
        self.global_d[name] = aList
    #@+node:ekr.20140616055519.17781: *3* d2.new_context
    def new_context(self,kind,name,node):
        '''Define a new context in the *existing* context.'''
        new_cx = Context(kind,name,node,self.cx_node,self.cx_obj)
        self.contexts_d[new_cx.full_name()] = new_cx
        if self.cx_obj:
            self.cx_obj.child_contexts.append(new_cx)
        if kind != 'lambda':
            self.define_name(name,node)
        return new_cx
    #@+node:ekr.20140601151054.17646: *3* d2.print_stats
    def print_stats (self):
        '''Print values of all vars starting with 'n_'.'''
        table = [z for z in sorted(dir(self)) 
            if z.startswith('n_')]
        max_n = 5
        for s in table:
            max_n = max(max_n,len(s))
        print('\nStatistics...\n')
        for s in table:
            pad = ' ' * (max_n - len(s))
            pad = ' ' * (max_n-len(s))
            val = getattr(self,s)
            print('%s%s: %s' % (pad,s,val))
        print('')
        # for d,name in self.distribution_table:
            # self.print_distribution(d,name)
        # print('')
    #@+node:ekr.20140601151054.17647: *3* d2.reference_name
    def reference_name(self,name,node):
        '''Called whenever a name is referenced in the given context.'''
        # Note: cx (an AST node) is hashable.
        cx_node,cx_obj,parent = self.cx_node,self.cx_obj,self.parent
        aSet = self.refs_d.get(name,set())
        aSet.add(cx_node)
        self.refs_d[name] = aSet
        aList = self.global_d.get(name,[])
        aList.append(self.NameData(cx_node,cx_obj,'ref',node))
        self.global_d[name] = aList
    #@+node:ekr.20140601151054.17648: *3* d2.visitors
    #@+node:ekr.20140616055519.17780: *4*  d2.contexts
    #@+node:ekr.20140601151054.17651: *5* d2.ClassDef
    # ClassDef(identifier name, expr* bases, stmt* body, expr* decorator_list)

    def do_ClassDef (self,node):

        # self.n_contexts += 1
        old_cx_node,old_cx_obj = self.cx_node,self.cx_obj
        # Create the new Context.
        new_cx = self.new_context('class',node.name,node)
        # Visit the children in the new context.
        self.cx_node,self.cx_obj = node,new_cx
        for z in node.bases:
            self.visit(z)
        for z in node.body:
            self.visit(z)
        for z in node.decorator_list:
            self.visit(z)
        # Restore the context.
        self.cx_node,self.cx_obj = old_cx_node,old_cx_obj
    #@+node:ekr.20140601151054.17652: *5* d2.FunctionDef
    # FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list)

    def do_FunctionDef (self,node):
        
        # self.n_contexts += 1
        old_cx_node,old_cx_obj = self.cx_node,self.cx_obj
        # Create the new context and remember it.
        new_cx = self.new_context('def',node.name,node)
        # Visit the children in the new context.
        self.cx_node,self.cx_obj = node,new_cx
        # Visit the formal arg list.
        self.visit(node.args)
        for z in node.body:
            self.visit(z)
        for z in node.decorator_list:
            self.visit(z)
        # Restore the context.
        self.cx_node,self.cx_obj = old_cx_node,old_cx_obj
    #@+node:ekr.20140601151054.17655: *5* d2.Lambda
    # Lambda(arguments args, expr body)

    def do_Lambda(self,node):

        # self.n_contexts += 1
        old_cx_node,old_cx_obj = self.cx_node,self.cx_obj
        # Remember the new context.
        self.lambdas += 1
        name = 'lambda %s' % self.lambdas
        new_cx = self.new_context('lambda',name,node)
        # Handle the lambda args.
        for arg in node.args.args:
            if isinstance(arg,ast.Name):
                # Python 2.x.
                assert isinstance(arg.ctx,ast.Param),arg.ctx
                # Define the arg in the lambda context.
                self.define_name(arg.id,node)
            elif isinstance(arg,ast.Tuple):
                pass
            else:
                # Python 3.x.
                g.trace('===============',self.u.format(node))
                # assert isinstance(arg,ast.arg),arg
                # assert isinstance(arg,ast.arg),arg
                # self.define_name(node,parent_cx_obj,arg.arg,node,self.parent)
            arg.stc_scope = node
        # Visit the children in the new context.
        self.cx_node,self.cx_obj = node,new_cx
        # self.visit(node.args)
        self.visit(node.body)
        # Restore the context.
        self.cx_node,self.cx_obj = old_cx_node,old_cx_obj
    #@+node:ekr.20140601151054.17656: *5* d2.Module
    def do_Module (self,node):

        # self.n_contexts += 1
        # Create the Module context and remember it.
        name = g.shortFileName(self.fn)
        assert self.cx_node is None
        assert self.cx_obj is None
        new_cx = self.new_context('module',name,node)
        # Set ivars to remember the global context.
        self.module_cx = node
        self.module_cx_obj = new_cx
        # Visit the children in the new context.
        self.cx_node = node
        self.cx_obj = new_cx
        for z in node.body:
            self.visit(z)
        # Restore the context.
        self.cx_node,self.cx_obj = None,None
    #@+node:ekr.20140604072301.17676: *4* d2.arguments & arg
    # arguments = (expr* args, identifier? vararg, identifier? kwarg, expr* defaults)

    def do_arguments(self,node):
        '''The arguments to a function def.'''
        for z in node.args:
            self.arg_node = z
            self.visit(z)
            self.arg_node = None
        for z in node.defaults:
            self.visit(z)
            
    # Python 3:
    # arg = (identifier arg, expr? annotation)

    def do_arg(self,node):
        g.trace('*****',node)
        if node.annotation:
            self.visit(node.annotation)
    #@+node:ekr.20140604072301.17672: *4* d2.Assign
    # Assign(expr* targets, expr value)

    def do_Assign(self,node):

        for z in node.targets:
            assert not self.assign_node,self.assign_node
            self.assign_node = node
            self.visit(z)
            self.assign_node = None
        self.visit(node.value)
    #@+node:ekr.20140601151054.17649: *4* d2.Attribute
    # Attribute(expr value, identifier attr, expr_context ctx)

    def do_Attribute(self,node):
        
        # self.n_attributes += 1
        self.visit(node.value)
        name = node.attr
        if self.assign_node:
            self.define_name(name,self.assign_node)
        else:
            self.reference_name(name,node)
    #@+node:ekr.20140601151054.17650: *4* d2.AugAssign
    # AugAssign(expr target, operator op, expr value)

    def do_AugAssign(self,node):

        assert not self.aug_assign_node,self.aug_assign_node
        self.aug_assign_node = node
        self.visit(node.target)
        self.aug_assign_node = None
        self.visit(node.value)
    #@+node:ekr.20140604072301.17674: *4* d2.Call (To do)
    # Call(expr func, expr* args, keyword* keywords, expr? starargs, expr? kwargs)

    def do_Call(self,node):
        
        self.visit(node.func)
        for z in node.args:
            # These are the **values** of the actual arguments, not their names.
            # g.trace(self.u.format(z))
            self.visit(z)
        for z in node.keywords:
            self.visit(z)
        if getattr(node,'starargs',None):
            self.visit(node.starargs)
        if getattr(node,'kwargs',None):
            self.visit(node.kwargs)
    #@+node:ekr.20140601151054.17653: *4* d2.Global
    # Global(identifier* names)

    def do_Global(self,node):

        # A hack: switch to module context to define the name.
        old_cx_node,old_cx_obj = self.cx_node,self.cx_obj
        self.cx_node,self.cx_obj = self.module_cx,self.module_cx_obj
        for name in node.names:
            self.define_name(name,node)
        # Restore the real context.
        self.cx_node,self.cx_obj = old_cx_node,old_cx_obj
    #@+node:ekr.20140601151054.17654: *4* d2.Import & ImportFrom
    # Import(alias* names)
    def do_Import(self,node):
        self.alias_helper(node)
                
    # ImportFrom(identifier? module, alias* names, int? level)
    def do_ImportFrom(self,node):
        self.alias_helper(node)

    # alias (identifier name, identifier? asname)
    def alias_helper(self,node):
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name.split('.')[0]
            # if alias.asname: g.trace('%s as %s' % (alias.name,alias.asname))
            # A hack: we treat imports as *references*.
            # Otherwise, all imports will be "ambigous" with the real class definitions.
            self.reference_name(name,node)
    #@+node:ekr.20140601151054.17657: *4* d2.Name
    # Name(identifier id, expr_context ctx)

    def do_Name(self,node):

        # self.visit(node.ctx)
        if isinstance(node.ctx,(ast.Param,ast.Store)):
            # The scope is unambigously cx, **even for AugAssign**.
            # If there is no binding, we will get an UnboundLocalError at run time.
            # However, AugAssigns do not actually assign to the var.
            if self.assign_node:
                self.define_name(node.id,self.assign_node)
            elif self.arg_node:
                self.define_name(node.id,self.arg_node)
        else:
            # ast.Store does *not* necessarily define the scope.
            # For example, a += 1 generates a Store, but does not defined the symbol.
            # Instead, only ast.Assign nodes really define a symbol.
            pass
    #@+node:ekr.20140603074103.17645: *4* d2.operators (to do)
    #@-others
#@+node:ekr.20140527071205.16687: ** class DataTraverser
class DataTraverser(AstFullTraverser):
    '''
    Traversal to create global data dict d.
    
    Like P1, this class injects stc_parent and stc_context links.
    Unlike P1, this class does not inject stc_symbol_table links.
    '''
    def __call__(self,fn,node):
        self.run(fn,node)
    #@+others
    #@+node:ekr.20140527121225.17044: *3*  dt.ctor
    def __init__(self,d_defs,d_refs):
        AstFullTraverser.__init__(self)
        self.d_defs = d_defs
        self.d_refs = d_refs
        self.in_aug_assign = False
            # A hack: True if visiting the target of an AugAssign node.
        self.u = Utils()
    #@+node:ekr.20140527071205.16689: *3*  dt.run (entry point)
    def run (self,fn,root):
        '''Run the prepass: init, then visit the root.'''
        # pylint: disable=arguments-differ
        # Init all ivars.
        self.context = None
        self.fn = fn
        self.n_attributes = 0
        self.n_contexts = 0
        self.n_nodes = 0
        self.parent = DummyNode()
        self.visit(root)
        # Undo references to DummyNode objects.
        root.stc_parent = None
        root.stc_context = None
    #@+node:ekr.20140527071205.16690: *3*  dt.visit
    def visit(self,node):
        '''Inject node references in all nodes.'''
        assert isinstance(node,ast.AST),node.__class__.__name__
        self.n_nodes += 1
        node.stc_context = self.context
        node.stc_parent = self.parent
        # Visit the children with the new parent.
        self.parent = node
        method = getattr(self,'do_' + node.__class__.__name__)
        method(node)
        # Restore the context & parent.
        self.context = node.stc_context
        self.parent = node.stc_parent
    #@+node:ekr.20140527071205.16692: *3* dt.define_name
    def define_name(self,cx,name,node):
        '''Called when name is defined in the given context.'''
        # Note: cx (an AST node) is hashable.
        aSet = self.d_defs.get(name,set())
        if False and name == 'xxx':
            # g.trace(node.__class__.__name__)
            if isinstance(node,ast.Name):
                g.trace(self.u.format(node.stc_parent))
            else:
                g.trace(self.u.format(node))
        # Sets don't work all that well here.
        aSet.add(cx)
        self.d_defs[name] = aSet
    #@+node:ekr.20140527121225.17047: *3* dt.print_stats
    def print_stats (self):
        '''Print values of all vars starting with 'n_'.'''
        table = [z for z in sorted(dir(self)) 
            if z.startswith('n_')]
        max_n = 5
        for s in table:
            max_n = max(max_n,len(s))
        print('\nStatistics...\n')
        for s in table:
            pad = ' ' * (max_n - len(s))
            pad = ' ' * (max_n-len(s))
            val = getattr(self,s)
            print('%s%s: %s' % (pad,s,val))
        print('')
        # for d,name in self.distribution_table:
            # self.print_distribution(d,name)
        # print('')
    #@+node:ekr.20140527071205.16703: *3* dt.reference_name
    def reference_name(self,cx,name):
        '''Called whenever a name is referenced in the given context.'''
        # Note: cx (an AST node) is hashable.
        aSet = self.d_refs.get(name,set())
        aSet.add(cx)
        self.d_refs[name] = aSet
    #@+node:ekr.20140527071205.16693: *3* dt.visitors
    #@+node:ekr.20140527071205.16694: *4* dt.Attribute
    # Attribute(expr value, identifier attr, expr_context ctx)

    def do_Attribute(self,node):
        
        self.n_attributes += 1
        self.visit(node.value)
        cx = node.stc_context
        name = node.attr
        self.reference_name(cx,name)
        if 0: # Old code
            cx = node.stc_context
            st = cx.stc_symbol_table
            d = st.attrs_d
            key = node.attr
            val = node.value
            # The following lines are expensive!
            # For Leo dt: 2.0 sec -> 2.5 sec.
            if d.has_key(key):
                d.get(key).add(val)
            else:
                aSet = set()
                aSet.add(val)
                d[key] = aSet
            # self.visit(node.ctx)
            if isinstance(node.ctx,(ast.Param,ast.Store)):
                st.defined_attrs.add(key)
    #@+node:ekr.20140527071205.16695: *4* dt.AugAssign (sets in_aug_assign)
    # AugAssign(expr target, operator op, expr value)

    def do_AugAssign(self,node):
        
        # g.trace('FT',self.u.format(node),g.callers())
        assert not self.in_aug_assign
        try:
            self.in_aug_assign = True
            self.visit(node.target)
        finally:
            self.in_aug_assign = False
        self.visit(node.value)
    #@+node:ekr.20140527071205.16696: *4* dt.ClassDef
    # ClassDef(identifier name, expr* bases, stmt* body, expr* decorator_list)

    def do_ClassDef (self,node):

        self.n_contexts += 1
        parent_cx = self.context
        assert parent_cx == node.stc_context
        # Define the function name itself in the enclosing context.
        self.define_name(parent_cx,node.name,node)
        # Visit the children in a new context.
        self.context = node
        for z in node.bases:
            self.visit(z)
        for z in node.body:
            self.visit(z)
        for z in node.decorator_list:
            self.visit(z)
        self.context = parent_cx
    #@+node:ekr.20140527071205.16697: *4* dt.FunctionDef
    # FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list)

    def do_FunctionDef (self,node):
        
        self.n_contexts += 1
        parent_cx = self.context
        assert parent_cx == node.stc_context
        # Define the function name itself in the enclosing context.
        self.define_name(parent_cx,node.name,node)
        # Visit the children in a new context.
        self.context = node
        self.visit(node.args)
        for z in node.body:
            self.visit(z)
        for z in node.decorator_list:
            self.visit(z)
        self.context = parent_cx
    #@+node:ekr.20140527071205.16698: *4* dt.Global
    # Global(identifier* names)

    def do_Global(self,node):
        
        cx = self.u.compute_module_cx(node)
        node.stc_scope = cx
        for name in node.names:
            self.define_name(cx,name,node)
    #@+node:ekr.20140527071205.16699: *4* dt.Import & ImportFrom
    # Import(alias* names)
    def do_Import(self,node):
        self.alias_helper(node)
                
    # ImportFrom(identifier? module, alias* names, int? level)
    def do_ImportFrom(self,node):
        self.alias_helper(node)

    # alias (identifier name, identifier? asname)
    def alias_helper(self,node):
        cx = node.stc_context
        assert cx
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name.split('.')[0]
            # if alias.asname: g.trace('%s as %s' % (alias.name,alias.asname))
            # A hack: we treat imports as *references*.
            # Otherwise, all imports will be "ambigous" with the real class definitions.
            self.reference_name(cx,name)
    #@+node:ekr.20140527071205.16700: *4* dt.Lambda
    # Lambda(arguments args, expr body)

    def do_Lambda(self,node):
        
        self.n_contexts += 1
        parent_cx = self.context
        assert parent_cx == node.stc_context
        # Handle the lambda args.
        for arg in node.args.args:
            if isinstance(arg,ast.Name):
                # Python 2.x.
                assert isinstance(arg.ctx,ast.Param),arg.ctx
                # Define the arg in the lambda context.
                self.define_name(node,arg.id,node)
            elif isinstance(arg,ast.Tuple):
                pass
            else:
                # Python 3.x.
                g.trace('===============',self.u.format(node))
                # assert isinstance(arg,ast.arg),arg
                # assert isinstance(arg,ast.arg),arg
                # self.define_name(node,arg.arg,node)
            arg.stc_scope = node
        # Visit the children in the new context.
        self.context = node
        # self.visit(node.args)
        self.visit(node.body)
        self.context = parent_cx
    #@+node:ekr.20140527071205.16701: *4* dt.Module
    def do_Module (self,node):

        self.n_contexts += 1
        assert self.context is None
        assert node.stc_context is None
        # Visit the children in the new context.
        self.context = node
        for z in node.body:
            self.visit(z)
        self.context = None
    #@+node:ekr.20140527071205.16702: *4* dt.Name
    # Name(identifier id, expr_context ctx)

    def do_Name(self,node):

        # self.visit(node.ctx)
        cx = node.stc_context
        if isinstance(node.ctx,(ast.Param,ast.Store)):
            # The scope is unambigously cx, **even for AugAssign**.
            # If there is no binding, we will get an UnboundLocalError at run time.
            # However, AugAssigns do not actually assign to the var.
            if not self.in_aug_assign:
                self.define_name(cx,node.id,node)
            node.stc_scope = cx
        else:
            # ast.Store does *not* necessarily define the scope.
            # For example, a += 1 generates a Store, but does not defined the symbol.
            # Instead, only ast.Assign nodes really define a symbol.
            node.stc_scope = None
    #@-others
#@+node:ekr.20140601151054.17641: ** class DummyNode
class DummyNode:
    '''A class containing only injected links.'''
    def __init__(self):
        self.stc_parent = None
        self.stc_context = None

#@+node:ekr.20140526082700.18100: ** class HTMLReportTraverser
class HTMLReportTraverser (AstFullTraverser):
    '''
    Create html reports from an AST tree.
    
    Adapted from micropython, by Paul Boddie. See the copyright notices.
    '''
    # To do: show stc attributes in the report.
    # To do: revise report-traverser-debug.css.
    #@+others
    #@+node:ekr.20140526082700.18101: *3* rt.__init__
    def __init__(self):

        AstFullTraverser.__init__(self)
            # Init the base class.
        self.debug = True
        self.css_fn = 'report-traverser-debug.css' if self.debug else 'report-traverser.css'
        self.html_footer = '\n</body>\n</html>\n'
        self.html_header = self.define_html_header()
        self.u = Utils()
        self.visitor = self
    #@+node:ekr.20140526082700.18102: *4* define_html_header
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
    #@+node:ekr.20140526082700.18103: *3* rt.css links & popup
    #@+node:ekr.20140526082700.18104: *4* rt.link
    def link (self,class_name,href,a_text):

        # g.trace(class_name,a_text)
        return "<a class='%s' href='%s'>%s</a>" % (class_name,href,a_text)
    #@+node:ekr.20140526082700.18105: *4* rt.module_link
    def module_link(self,module_name,classes=None):
        
        r = self
        return r.link(
            class_name = classes or 'name',
            href = '%s.xhtml' % module_name,
            a_text = r.text(module_name))
    #@+node:ekr.20140526082700.18106: *4* rt.name_link
    def name_link(self,module_name,full_name,name,classes=None):
        
        r = self
        # g.trace(name,classes)
        return r.link(
            class_name = classes or "specific-ref",
            href = '%s.xhtml#%s' % (module_name,r.attr(full_name)),
            a_text = r.text(name))
    #@+node:ekr.20140526082700.18107: *4* rt.object_name_ref
    def object_name_ref(self,module,obj,name=None,classes=None):

        """
        Link to the definition for 'module' using 'obj' with the optional 'name'
        used as the label (instead of the name of 'obj'). The optional 'classes'
        can be used to customise the CSS classes employed.
        """

        r = self
        return r.name_link(module.full_name(),obj.full_name(),name or obj.name,classes)
    #@+node:ekr.20140526082700.18108: *4* rt.popup
    def popup(self,classes,aList):
        r = self
        return r.span(classes or 'popup',aList)
    #@+node:ekr.20140526082700.18109: *4* rt.summary_link
    def summary_link(self,module_name,full_name,name,classes=None):
        
        r = self
        return r.name_link("%s-summary" % module_name,full_name,name,classes)
    #@+node:ekr.20140526082700.18110: *3* rt.html attribute helpers
    #@@nocolor-node
    #@+at
    # 
    # stc injects the following attributes into ast.AST nodes::
    #     
    #     'cache'         A cache object.
    #     'call_cache'    (Not used yet) A call cache.
    #     'e'             A SymbolTableEntry, call it e.
    #     'reach'         A reaching set.
    #     'typ'           (Not used yet) A list of inferred types.
    # 
    # This class may report any of the above attributes, plus the following ivars
    # of e::
    #     
    #     e.defined       True if e is defined in cx (and is not a global)
    #     e.referenced    True if e is reference anywhere.
    #     e.resolved      True if e appears with 'Load' or 'Param' ctx.
    # 
    # Other ivars of e may be useful::
    #     
    #     e.cx            The context containing e
    #     e.name          The name of the object.
    #     e.node          For defs, the ast.FunctionDef node for this def.
    #     e.st            The symbol table containing this name.
    #     e.self_context  For defs and classes, the context that they define.
    #@+node:ekr.20140526082700.18111: *4* rt.get_stc_attrs & AttributeTraverser
    def get_stc_attrs (self,node,all):
        
        r = self
        nodes = r.NameTraverser().run(node) if all else [node]
        result = []
        for node in nodes:
            aList = []
            e = getattr(node,'e',None)
            reach = getattr(node,'reach',None)
            if e:
                aList.append(r.text('%s cx: %s defined: %s' % (
                    e.name,e.cx.name,e.defined)))
            if reach:
                for item in reach:
                    aList.append(r.text('reach: %s' % r.u.format(item)))
            result.append(g.join_list(aList,sep=', '))
        return g.join_list(result,sep='; ')
    #@+node:ekr.20140526082700.18112: *5* NameTraverser(AstFullTraverser)
    class NameTraverser(AstFullTraverser):
        
        def __init__(self):
            AstFullTraverser.__init__(self)
            self.d = {}

        def do_Name(self,node):
            self.d[node.e.name] = node
                
        def run(self,root):
            self.visit(root)
            return [self.d.get(key) for key in sorted(self.d.keys())]
    #@+node:ekr.20140526082700.18113: *4* rt.stc_attrs
    def stc_attrs (self,node,all=False):
        
        r = self
        attrs = r.get_stc_attrs(node,all=all)
        return attrs and [
            r.span('inline-attr nowrap',[
                attrs,
            ]),
            r.br(),
        ]
    #@+node:ekr.20140526082700.18114: *4* rt.stc_popup_attrs
    def stc_popup_attrs(self,node,all=False):

        r = self
        attrs = r.get_stc_attrs(node,all=all)
        return attrs and [
            r.popup('attr-popup',[
                attrs,
            ]),
        ]
    #@+node:ekr.20140526082700.18115: *3* rt.html helpers
    #@+node:ekr.20140526082700.18116: *4* rt.attr & text
    def attr(self,s):
        
        r = self
        return r.text(s).replace("'","&apos;").replace('"',"&quot;")

    def text(self,s):

        return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
    #@+node:ekr.20140526082700.18117: *4* rt.br
    def br(self):
        
        r = self
        return '\n<br />'
    #@+node:ekr.20140526082700.18118: *4* rt.comment
    def comment(self,comment):
        
        r = self
        return '%s\n' % r.span("# %s" % (comment),"comment")
    #@+node:ekr.20140526082700.18119: *4* rt.div
    def div(self,class_name,aList,extra=None):
        
        r = self
        if class_name and extra:
            div = "\n<div class='%s' %s>" % (class_name,extra)
        elif class_name:
            div = "\n<div class='%s'>" % (class_name)
        else:
            assert not extra
            div = "\n<div>"
        assert isinstance(aList,(list,tuple))
        return [
            div,
            g.join_list(aList,indent='  '),
            '\n</div>'
        ]
    #@+node:ekr.20140526082700.18120: *4* rt.doc & helper (to do)
    # Called by ClassDef & FunctionDef visitors.

    def doc(self,node,classes=None):

        # if node.doc is not None:
            # r.docstring(node.doc,classes)
            
        return ''
    #@+node:ekr.20140526082700.18121: *5* rt.docstring
    def docstring(self,s,classes=None):
        
        r = self
        if classes: classes = ' ' + classes
        return [
            "<pre class='doc%s'>" % (classes),
            '"""',
            r.text(textwrap.dedent(s.replace('"""','\\"\\"\\"'))),
            '"""',
            "</pre>\n",
        ]
    #@+node:ekr.20140526082700.18122: *4* rt.keyword (a helper, not a visitor!)
    def keyword(self,keyword_name,leading=False,trailing=True):

        r = self
        return [
            leading and ' ',
            r.span('keyword',[
                keyword_name,
            ]),
            trailing and ' ',
        ]
    #@+node:ekr.20140526082700.18123: *4* rt.name
    def name(self,name):
        return self.span('name',[name])

    #@+node:ekr.20140526082700.18124: *4* rt.object_name_def (rewrite)
    def object_name_def(self,module,obj,classes=None):

        """
        Link to the summary for 'module' using 'obj'. The optional 'classes'
        can be used to customise the CSS classes employed.
        """
        
        r = self
        return ''

        # if isinstance(obj,(ast.ClassDef,ast.FunctionDef)) and obj.is_method()):
           # r.summary_link(obj.cx.full_name(),obj.full_name(),obj.name,classes)
        # else:
            # g.trace(obj.name)
            # if obj.name == '<string>':
                # obj.name = 'ModuleName'
            # r.span(obj.name,classes)
    #@+node:ekr.20140526082700.18125: *4* rt.op
    def op(self,op_name,leading=False,trailing=True):
        
        # g.trace(repr(op_name))
        r = self
        return [
            leading and ' ',
            r.span("operation",[
                r.span("operator",[
                    r.text(op_name),
                ])
                # r.popup(None,[
                    # r.div('opnames',[
                        # r.name_link("operator","operator.%s" % op_name,op_name),
                    # ]),
                # ]),
            ]),
            trailing and ' ',
        ]
    #@+node:ekr.20140526082700.18126: *4* rt.simple_statement
    def simple_statement(self,name):
        
        r = self
        return [
            r.div('%s nowrap' % name,[
                r.keyword(name),
            ]),
        ]
    #@+node:ekr.20140526082700.18127: *4* rt.span & span_start/end
    def span(self,class_name,aList):
        
        r = self
        assert isinstance(aList,(list,tuple))
        if class_name:
            span = "\n<span class='%s'>" % (class_name)
        else:
            span = '\n<span>'
        return [
            span,
            g.join_list(aList,indent='  '),
            # '\n</span>',
            '</span>', # More compact
        ]
    #@+node:ekr.20140526082700.18128: *4* rt.url (not used)
    def url(self,url):

        r = self
        return r.attr(url).replace("#", "%23").replace("-", "%2d")
    #@+node:ekr.20140526082700.18129: *3* rt.reporters
    #@+node:ekr.20140526082700.18130: *4* rt.annotate
    def annotate(self,fn,m):

        r = self
        f = open(fn,"wb")
        try:
            for s in g.flatten_list(r.report_file()):
                f.write(s)
        finally:
            f.close()
    #@+node:ekr.20140526082700.18131: *4* rt.base_fn
    def base_fn(self,directory,m):
        
        '''Return the basic html file name used by reporters.'''

        assert g.os_path_exists(directory)

        if m.fn.endswith('<string>'):
            return 'report_writer_string_test'
        else:
            return g.shortFileName(m.fn)
    #@+node:ekr.20140526082700.18132: *4* rt.interfaces & helpers
    def interfaces(self,directory,m,open_file=False):

        r = self
        base_fn = r.base_fn(directory,m)
        fn = g.os_path_join(directory,"%s_interfaces.xhtml" % base_fn)
        f = open(fn,"wb")
        try:
            for s in g.flatten_list(r.write_interfaces(m)):
                f.write(s)
        finally:
            f.close()
        if open_file:
            os.startfile(fn)
    #@+node:ekr.20140526082700.18133: *5* write_interfaces
    def write_interfaces(self,m):
        
        r = self
        all_interfaces,any_interfaces = [],[]
        return g.join_list([
            r.html_header % {'css-fn':self.css_fn,'title':'Interfaces'},
            "<table cellspacing='5' cellpadding='5'>",
            "<thead>",
            "<tr>",
            "<th>Complete Interfaces</th>",
            "</tr>",
            "</thead>",
            r.write_interface_type("complete",all_interfaces),
            "<thead>",
            "<tr>",
            "<th>Partial Interfaces</th>",
            "</tr>",
            "</thead>",
            r.write_interface_type("partial",any_interfaces),
            "</table>",
            r.html_footer,
        ],trailing='\n')
    #@+node:ekr.20140526082700.18134: *5* write_interface_type
    def write_interface_type(self,classes,interfaces):

        r = self
        aList = []
        for names,objects in interfaces:
            if names: aList.append([
                "<tr>",
                "<td class='summary-interface %s'>%s</td>" % (
                    classes,
                    ",".join(sorted(names))),
                "</tr>",
            ])
        return g.join_list([
            "<tbody>",
            aList,
            '</tbody>',
        ],trailing='\n')
    #@+node:ekr.20140526082700.18135: *4* rt.report(entry_point)
    def report(self,directory,m,open_file=False):

        trace = False
        r = self
        r.module = m
        base_fn = r.base_fn(directory,m)
        annotate_fn = g.os_path_join(directory,"%s.xhtml" % base_fn)
        # if trace: g.trace('writing %s' % (annotate_fn))
        r.annotate(annotate_fn,m)
        assert g.os_path_exists(annotate_fn),annotate_fn
        if open_file:
            os.startfile(annotate_fn)
        
        if 0: # The file is empty at present.
            summary_fn = g.os_path_join(directory,"%s_summary.xhtml" % base_fn)
            if trace: g.trace('writing %s' % (summary_fn))
            r.summarize(summary_fn,m)
            if open_file:
                os.startfile(summary_fn)
    #@+node:ekr.20140526082700.18136: *4* rt.report_all_modules(not used)
    # Needed to write interfaces
    def report_all_modules(self,directory,files,project_name):

        trace = True
        r = self
        join = g.os_path_join
        assert g.os_path_exists(directory)
        root_d = self.u.p0(files,project_name,False)
        for n,fn in enumerate(sorted(files)):
            r.module = m = root_d.get(fn)
            if fn.endswith('<string>'):
                fn = 'report_writer_string_test'
            else:
                # fn = '%s_%s' % (fn,n)
                fn = g.shortFileName(fn)
            annotate_fn = g.os_path_join(directory,"%s.xhtml" % fn)
            if trace: g.trace('writing: %s.xhtml' % (annotate_fn))
            files.append(annotate_fn)
            r.annotate(annotate_fn,m)
            if 0:
                summary_fn = g.os_path_join(directory,"%s_summary.xhtml" % fn)
                if trace: g.trace('writing %s' % (summary_fn))
                r.summarize(summary_fn,m)
                if False:
                    os.startfile(summary_fn)
            # r.summarize(join(directory,"%s-summary.xhtml" % (base_fn)),m)
        # r.interfaces(join(join(directory,"-interfaces.xhtml")),m)
        if 0:
            for fn in files:
                fn2 = join(directory,fn+'.xhtml')
                assert g.os_path_exists(fn2),fn2
                os.startfile(fn2)
    #@+node:ekr.20140526082700.18137: *4* rt.report_file
    def report_file(self):
        
        r = self
        return [
            r.html_header % {
                'css-fn':self.css_fn,
                'title':'Module: %s' % r.module.full_name()},
            r.visit(r.module.node),
            r.html_footer,
        ]
    #@+node:ekr.20140526082700.18138: *4* rt.summarize & helpers
    def summarize(self,directory,m,open_file=False):

        r = self
        base_fn = r.base_fn(directory,m)
        fn = g.os_path_join(directory,"%s_summary.xhtml" % base_fn)
        f = open(fn,"wb")
        try:
            for s in g.flatten_list(r.summary(m)):
                f.write(s)
        finally:
            f.close()
        if open_file:
            os.startfile(fn)
    #@+node:ekr.20140526082700.18139: *5* summary & helpers
    def summary(self,m):

        r = self
        return g.join_list([
            r.html_header % {
                'css-fn':self.css_fn,
                'title':'Module: %s' % m.full_name()},
            r.write_classes(m),
            r.html_footer,
        ],sep='\n')
    #@+node:ekr.20140526082700.18140: *6* write_classes
    def write_classes(self,m):

        r = self
        return m.classes() and g.join_list([
            "<table cellspacing='5' cellpadding='5'>",
            "<thead>",
            "<tr>",
            "<th>Classes</th><th>Attributes</th>",
            "</tr>",
            "</thead>",
            [r.write_class(z) for z in m.classes()],
            "</table>",
        ],sep='\n')
    #@+node:ekr.20140526082700.18141: *6* write_class
    def write_class(self,obj):

        r = self
        d = obj.st.d
        # The instance attribute names in order.
        aList = [d.get(z).name for z in sorted(d.keys())]
            
        # attrs = [] ### obj.instance_attributes().values()
        # if attrs:
            # for attr in sorted(attrs,cmp=lambda x,y: cmp(x.position,y.position)):
                # aList.append("<td class='summary-attr'>%s</td>" % r.text(attr.name))
        # else:
            # aList.append("<td class='summary-attr-absent'>None</td>")
        instance_names = g.join_list(aList,sep=', ')

        # The class attribute names in order.
        # attrs = [] ### obj.class_attributes().values()
        # aList = []
        # if attrs:
            # for attr in sorted(attrs,cmp=lambda x,y: cmp(x.position,y.position)):
                # if attr.is_strict_constant():
                    # value = attr.get_value()
                    # if False: #### not isinstance(value,Const):
                        # aList.append(g.join_list([
                            # "<td class='summary-class-attr' id='%s'>" % (r.attr(value.full_name())),
                            # r.object_name_ref(r.module,value,attr.name,classes="summary-ref"),
                            # "</td>",
                        # ],trailing='\n'))
                    # else:
                        # aList.append("<td class='summary-class-attr'>%s</td>" % r.text(attr.name))
                # else:
                    # aList.append("<td class='summary-class-attr'>%s</td>" % r.text(attr.name))
        # else:
            # aList.append("<td class='summary-class-attr-absent'>None</td>")
        # class_names = g.join_list(aList,sep='\n')
            
        return g.join_list([
            "<tbody class='class'>",
                "<tr>",
                    "<th class='summary-class' id='%s' rowspan='2'>" % (
                        r.attr(obj.full_name())),
                        r.object_name_ref(r.module,obj,classes="class-name"),
                    "</th>",
                    instance_names,
                "</tr>",
                # "<tr>",
                    # class_names,
                # "</tr>",
            "</tbody>",
        ],trailing='\n')
    #@+node:ekr.20140526082700.18142: *3* rt.traversers
    #@+node:ekr.20140526082700.18143: *4* rt.visit
    def visit(self,node):
        
        """Walk a tree of AST nodes."""

        assert isinstance(node,ast.AST),node.__class__.__name__
        method_name = 'do_' + node.__class__.__name__
        method = getattr(self,method_name)
        return method(node)
        
        # method = getattr(self,method_name,None)
        # if method:
            # # method is responsible for traversing subtrees.
            # return method(node)
        # else:
            # return self.visit_list(self.get_child_nodes(node))
    #@+node:ekr.20140526082700.18144: *4* rt.visit_list
    def visit_list(self,aList,sep=''):
        
        # pylint: disable=W0221
            # Arguments number differs from overridden method.
        
        r = self
        if sep:
            return g.join_list([r.visit(z) for z in aList],sep=sep)
        else:
            return [r.visit(z) for z in aList]
    #@+node:ekr.20140526082700.18145: *3* rt.visitors
    #@+node:ekr.20140526082700.18146: *4* rt.arguments & helper
    # arguments = (expr* args, identifier? vararg, identifier? kwarg, expr* defaults)

    def do_arguments(self,node):
        
        assert isinstance(node,ast.AST),node
        
        r = self
        first_default = len(node.args) - len(node.defaults)
        result = []
        first = True
        for n,node2 in enumerate(node.args):
            if not first: result.append(', ')
            if isinstance(node2,tuple):
                result.append(r.tuple_parameter(node.args,node2)) ### Huh?
            else:
                result.append(r.visit(node2)) ### r.assname(param,node)
            if n >= first_default:
                node3 = node.defaults[n-first_default]
                result.append("=")
                result.append(r.visit(node3))
            first = False

        if node.vararg:
            result.append('*' if first else ', *')
            result.append(r.name(node.vararg))
            first = False
        if node.kwarg:
            result.append('**' if first else ', **')
            result.append(r.name(node.kwarg))
            
        return result
    #@+node:ekr.20140526082700.18147: *5* rt.tuple_parameter
    def tuple_parameter(self,parameters,node):
        
        r = self
        result = []
        result.append("(")
        first = True
        for param in parameters:
            if not first: result.append(', ')
            if isinstance(param,tuple):
                result.append(r.tuple_parameter(param,node))
            else:
                pass ### result.append(r.assname(param,node))
            first = False
        result.append(")")
        return g.join_list(result)
    #@+node:ekr.20140526082700.18148: *4* rt.Assert
    # Assert(expr test, expr? msg)

    def do_Assert(self,node):
        
        r = self
        return [
            r.div('assert nowrap',[
                r.keyword("assert"),
                r.visit(node.test),
                [',',r.visit(node.msg)] if node.msg else None,
            ]),
        ]
    #@+node:ekr.20140526082700.18149: *4* rt.Assign
    def do_Assign(self,node):
        
        r = self
        show_attrs = True
        return [
            r.div('assign nowrap',[
                [[r.visit(z),' = '] for z in node.targets],
                r.visit(node.value),
            ]),
            show_attrs and [
                [r.stc_attrs(z) for z in node.targets],
                r.stc_attrs(node.value,all=True),
            ],
        ]
    #@+node:ekr.20140526082700.18150: *4* rt.Attribute
    # Attribute(expr value, identifier attr, expr_context ctx)

    def do_Attribute(self,node):
        
        r = self
        return [
            r.visit(node.value),
            '.',
            node.attr,
        ]
    #@+node:ekr.20140526082700.18151: *4* rt.AugAssign
    #  AugAssign(expr target, operator op, expr value)

    def do_AugAssign(self,node):
        
        r = self
        op_name = r.op_name(node.op)
        return [
            r.div('augassign nowrap',[
                r.visit(node.target),
                r.op(op_name,leading=True),
                r.visit(node.value),
            ]),
        ]
    #@+node:ekr.20140526082700.18152: *4* rt.BinOp
    def do_BinOp(self,node):

        r = self
        op_name = r.op_name(node.op)
        return [
            r.span(op_name,[
                r.visit(node.left),
                r.op(op_name,leading=True),
                r.visit(node.right),
            ]),
        ]
    #@+node:ekr.20140526082700.18153: *4* rt.BoolOp
    def do_BoolOp(self,node):

        r = self
        op_name = r.op_name(node.op)
        ops = []
        for i,node2 in enumerate(node.values):
            if i > 0:
                ops.append(r.keyword(op_name,leading=True))
            ops.append(r.visit(node2))
        return [
            r.span(op_name.strip(),[
                ops,
            ]),
        ]
    #@+node:ekr.20140526082700.18154: *4* rt.Break
    def do_Break(self,node):
        
        r = self
        return r.simple_statement('break')
    #@+node:ekr.20140526082700.18155: *4* rt.Call & rt.keyword
    # Call(expr func, expr* args, keyword* keywords, expr? starargs, expr? kwargs)

    def do_Call(self,node):
        
        r = self
        args = [r.visit(z) for z in node.args]
        args.append( # Calls rt.do_keyword.
            g.join_list([r.visit(z) for z in node.keywords],sep=','))
        if node.starargs:
            args.append(['*',r.visit(node.starargs)])
        if node.kwargs:
            args.append(['**',r.visit(node.kwargs)])
        return [
            r.span("callfunc",[
                r.visit(node.func),
                r.span("call",[
                    '(',args,')',
                ]),
            ]),
        ]
    #@+node:ekr.20140526082700.18156: *5* rt.keyword
    # keyword = (identifier arg, expr value)
    # keyword arguments supplied to call

    def do_keyword(self,node):
        
        r = self
        return [
            r.span("keyword-arg",[
                node.arg,
                ' = ',
                r.visit(node.value),
            ]),
        ]
    #@+node:ekr.20140526082700.18157: *4* rt.ClassDef
    # ClassDef(identifier name, expr* bases, stmt* body, expr* decorator_list)

    def do_ClassDef(self,node):
        
        r = self
        return [
            # Write the declaration line.
            r.div('classdef nowrap',[
                r.div(None,[
                    r.keyword("class"),
                    r.span(None,[node.name]), # Always a string.
                    ### cls = node.cx
                    ### r.object_name_def(r.module,cls,"class-name")
                    '(',
                    node.bases and r.visit_list(node.bases,sep=','),
                    "):", #,"\n",
                ]),
                # Write the docstring and class body.
                r.div('body nowrap',[
                    r.doc(node),
                    r.visit_list(node.body),
                ]),
            ]),
        ]
    #@+node:ekr.20140526082700.18158: *4* rt.Compare
    def do_Compare(self,node):
        
        r = self
        assert len(node.ops) == len(node.comparators)
        ops = []
        for i in range(len(node.ops)):
            op_name = r.op_name(node.ops[i])
            ops.append(r.op(op_name,leading=True))
            expr = node.comparators[i]
            ops.append(r.visit(expr))
        return [
            r.span("compare",[
                r.visit(node.left),
                ops,
            ]),
        ]
    #@+node:ekr.20140526082700.18159: *4* rt.comprehension
    def do_comprehension(self,node):
        
        r = self
        ifs = node.ifs and [
            r.keyword('if',leading=True),
            r.span("conditional",[
                r.visit_list(node.ifs,sep=' '),
            ]),
        ]
        return [
            r.keyword("in",leading=True),
            r.span("collection",[
                r.visit(node.iter),
                ifs,
            ]),
        ]
    #@+node:ekr.20140526082700.18160: *4* rt.Continue
    def do_Continue(self,node):
        
        r = self
        return r.simple_statement('break')
    #@+node:ekr.20140526082700.18161: *4* rt.Delete
    def do_Delete(self,node):
        
        r = self
        return [
            r.div('del nowrap',[
                r.keyword('del'),
                r.visit_list(node.targets,sep=','),
            ]),
        ]
    #@+node:ekr.20140526082700.18162: *4* rt.Dict
    def do_Dict(self,node):
        
        r = self
        assert len(node.keys) == len(node.values)
        items = []
        for i in range(len(node.keys)):
            items.append(r.visit(node.keys[i]))
            items.append(':')
            items.append(r.visit(node.values[i]))
            if i < len(node.keys)-1:
                items.append(',')
        return [
            r.span("dict",[
                '{',items,'}',
            ]),
        ]
    #@+node:ekr.20140526082700.18163: *4* rt.Ellipsis
    def do_Ellipsis(self,node):
        
        return '...'
    #@+node:ekr.20140526082700.18164: *4* rt.ExceptHandler
    def do_ExceptHandler(self,node):
        
        r = self
        name = node.name and [
            r.keyword('as',leading=True,trailing=True),
            r.visit(node.name),
        ]
        return [
            r.div('excepthandler nowrap',[
                r.div(None,[
                    r.keyword("except",trailing=bool(node.type)),
                    r.visit(node.type) if node.type else '',
                    name, ':', #'\n',
                ]),
                r.div('body nowrap',[
                    r.visit_list(node.body),
                ]),
            ]),
        ]
    #@+node:ekr.20140526082700.18165: *4* rt.Exec
    # Python 2.x only.

    def do_Exec(self,node):
        
        r = self
        return [
            r.div('exec nowrap',[
                r.keyword('exec',leading=True),
                r.visit(node.body),
                node.globals and [',',r.visit(node.globals)],
                node.locals and [',',r.visit(node.locals)],
            ]),
        ]
    #@+node:ekr.20140526082700.18166: *4* rt.Expr (New)
    def do_Expr(self,node):
        
        r = self
        return [
            r.div('expr',[
                r.visit(node.value),
            ])
        ]
    #@+node:ekr.20140526082700.18167: *4* rt.For
    # For(expr target, expr iter, stmt* body, stmt* orelse)

    def do_For(self,node):
        
        r = self
        orelse = node.orelse and [
            r.div(None,[
                r.keyword("else",trailing=False),
                ':', # '\n',
            ]),
            r.div('body nowrap',[
                r.visit_list(node.orelse),
            ]),
        ]
        return [
            r.div('if nowrap',[
                r.div(None,[
                    r.keyword("for"),
                    r.visit(node.target),
                    r.keyword("in",leading=True),
                    r.visit(node.iter),
                    ':', # '\n',
                ]),
                r.div('body nowrap',[
                    r.visit_list(node.body),
                ]),
                orelse,
            ]),
        ]
    #@+node:ekr.20140526082700.18168: *4* rt.FunctionDef (uses extra arg)
    def do_FunctionDef(self,node):
        
        r = self
        return [
            ### r.div('function nowrap','id="%s"' % (node.name)),
            r.div('function nowrap',[
                r.div(None,[
                    r.keyword("def"),
                    r.summary_link(node.cx.full_name(),node.name,node.name,classes=''),
                        ### r.object_name_def(r.module,node,"function-name")
                    '(',
                    r.visit(node.args),
                    '):', # '\n',
                        ### r.parameters(node.name,node)
                ]),
                r.div('body nowrap',[
                    r.doc(node),
                    r.visit_list(node.body),
                ]),
            ],extra='id="%s"' % (node.name)),
        ]
    #@+node:ekr.20140526082700.18169: *4* rt.GeneratorExp
    def do_GeneratorExp(self,node):

        r = self
        return [
            r.span("genexpr",[
                "(",
                r.visit(node.elt) if node.elt else '',
                r.keyword('for',leading=True),
                r.span('item',[
                    r.visit(node.elt),
                ]),
                r.span('generators',[
                    r.visit_list(node.generators),
                ]),
                ")",
            ]),
        ]
    #@+node:ekr.20140526082700.18170: *4* rt.get_import_names
    def get_import_names (self,node):

        '''Return a list of the the full file names in the import statement.'''

        r = self
        result = []
        for ast2 in node.names:
            if r.kind(ast2) == 'alias':
                data = ast2.name,ast2.asname
                result.append(data)
            else:
                g.trace('unsupported kind in Import.names list',r.kind(ast2))

        # g.trace(result)
        return result
    #@+node:ekr.20140526082700.18171: *4* rt.Global
    def do_Global(self,node):
        
        r = self
        return [
            r.div('global nowrap',[
                r.keyword("global"),
                g.join_list(node.names,sep=','),
            ]),
        ]
    #@+node:ekr.20140526082700.18172: *4* rt.If
    def do_If(self,node):
        
        r = self
        parent = node._parent
        # The only way to know whether to generate elif is to examine the tree.
        elif_flag = self.kind(parent) == 'If' and parent.orelse and parent.orelse[0] == node
        elif_node = node.orelse and node.orelse[0]
        if elif_node and self.kind(elif_node) == 'If':
            orelse = r.visit(elif_node)
        else:
            orelse = node.orelse and [
                r.div(None,[
                    r.keyword('else',trailing=False),
                    ':', # '\n',
                ]),
                r.div('body nowrap',[
                    r.visit_list(node.orelse),
                ]),
            ]
        # g.trace(r.u.format(node.test))
        return [
            r.div('if nowrap',[
                r.div(None,[
                    r.keyword('elif' if elif_flag else 'if'),
                    r.visit(node.test),
                    ':', # '\n',
                ]),
                r.div('body nowrap',[
                    r.visit_list(node.body),
                ]),
                orelse,
            ]),
        ]
    #@+node:ekr.20140526082700.18173: *4* rt.IfExp (TernaryOp)
    # IfExp(expr test, expr body, expr orelse)

    def do_IfExp(self,node):
        
        r = self
        return [
            r.span("ifexp",[
                r.visit(node.body),
                r.keyword("if",leading=True),
                r.visit(node.test),
                r.keyword("else",leading=True),
                r.visit(node.orelse),
            ]),
        ]
    #@+node:ekr.20140526082700.18174: *4* rt.Import
    def do_Import(self,node):
        
        r = self
        aList = []
        for name,alias in r.get_import_names(node):
            if alias: aList.append([
                r.module_link(name),
                r.keyword("as",leading=True),
                r.name(alias),
            ])
            else:
                aList.append(r.module_link(name))
        return [
            r.div('import nowrap',[
                r.keyword("import"),
                aList,
            ]),
        ]
    #@+node:ekr.20140526082700.18175: *4* rt.ImportFrom
    def do_ImportFrom(self,node):
        
        r = self
        aList = []
        for name,alias in r.get_import_names(node):
            if alias: aList.append([
                r.name(name),
                r.keyword("as",leading=True),
                r.name(alias),
            ])
            else:
                aList.append(r.name(name))
        return [
            r.div('from nowrap',[
                r.keyword("from"),
                r.module_link(node.module),
                r.keyword("import",leading=True),
                aList,
            ]),
        ]
    #@+node:ekr.20140526082700.18176: *4* rt.Lambda
    def do_Lambda(self,node):
        
        r = self
        return [
            r.span("lambda",[
                r.keyword("lambda"),
                r.visit(node.args), # r.parameters(fn,node)
                ": ",
                r.span("code",[
                    r.visit(node.body),
                ]),
            ]),
        ]
    #@+node:ekr.20140526082700.18177: *4* rt.List
    # List(expr* elts, expr_context ctx) 

    def do_List(self,node):
        
        r = self
        return [
            r.span("list",[
                '[',
                r.visit_list(node.elts,sep=','),
                ']',
            ]),
        ]
    #@+node:ekr.20140526082700.18178: *4* rt.ListComp
    def do_ListComp(self,node):
        
        r = self
        return [
            r.span("listcomp",[
                '[',
                r.visit(node.elt) if node.elt else '',
                r.keyword('for',leading=True),
                r.span('item',[
                    r.visit(node.elt),
                ]),
                r.span('ifgenerators',[
                    r.visit_list(node.generators),
                ]),
                "]",
            ]),
        ]
    #@+node:ekr.20140526082700.18179: *4* rt.Module
    def do_Module(self,node):
        
        r = self
        return [
            r.doc(node,"module"),
            r.visit_list(node.body),
        ]
    #@+node:ekr.20140526082700.18180: *4* rt.Name
    def do_Name(self,node):
        
        r = self
        return [
            r.span('name',[
                node.id,
                r.stc_popup_attrs(node),
            ]),
        ]
    #@+node:ekr.20140526082700.18181: *4* rt.Num
    def do_Num(self,node):
        
        r = self
        return r.text(repr(node.n))
        
    #@+node:ekr.20140526082700.18182: *4* rt.Pass
    def do_Pass(self,node):
        
        r = self
        return r.simple_statement('pass')
    #@+node:ekr.20140526082700.18183: *4* rt.Print
    # Print(expr? dest, expr* values, bool nl)

    def do_Print(self,node):
        
        r = self
        return [
            r.div('print nowrap',[
                r.keyword("print"),
                "(",
                node.dest and '>>\n%s,\n' % r.visit(node.dest),
                r.visit_list(node.values,sep=',\n'),
                not node.nl and "newline=False",
                ")",
            ]),
        ]
    #@+node:ekr.20140526082700.18184: *4* rt.Raise
    def do_Raise(self,node):
        
        r = self
        aList = []
        for attr in ('type','inst','tback'):
            attr = getattr(node,attr,None)
            if attr is not None:
                aList.append(r.visit(attr))
        return [
            r.div('raise nowrap',[
                r.keyword("raise"),
                aList,
            ]),
        ]
    #@+node:ekr.20140526082700.18185: *4* rt.Return
    def do_Return(self,node):
        
        r = self
        return [
            r.div('return nowrap',[
                r.keyword("return"),
                node.value and r.visit(node.value),
            ]),
        ]
    #@+node:ekr.20140526082700.18186: *4* rt.Slice
    def do_Slice(self,node):
        
        r = self
        return [
            r.span("slice",[
                node.lower and r.visit(node.lower),
                ":",
                node.upper and r.visit(node.upper),
                [':',r.visit(node.step)] if node.step else None,
            ]),
        ]
    #@+node:ekr.20140526082700.18187: *4* rt.Str
    def do_Str(self,node):

        '''This represents a string constant.'''
        
        r = self
        assert isinstance(node.s,(str,unicode))
        return [
            r.span("str",[
                r.text(repr(node.s)), ### repr??
            ]),
        ]
    #@+node:ekr.20140526082700.18188: *4* rt.Subscript
    def do_Subscript(self,node):
        
        r = self
        return [
            r.span("subscript",[
                r.visit(node.value),
                '[',
                r.visit(node.slice),
                ']',
            ]),
        ]
    #@+node:ekr.20140526082700.18189: *4* rt.TryExcept
    def do_TryExcept(self,node):
        
        r = self
        orelse = node.orelse and [
            r.div(None,[
                r.keyword("else",trailing=False),
                ':', # '\n',
            ]),
            r.div('body nowrap',[
                r.visit_list(node.orelse),
            ]),
        ]
        return [
            r.div('tryexcept nowrap',[
                r.div(None,[
                    r.keyword("try",trailing=False),
                    ':', # '\n',
                ]),
                r.div('body nowrap',[
                    r.visit_list(node.body),
                ]),
                r.div('body nowrap',[
                    orelse,
                ]),
                node.handlers and r.visit_list(node.handlers),
            ]),
        ]
    #@+node:ekr.20140526082700.18190: *4* rt.TryFinally
    def do_TryFinally(self,node):
        
        r = self
        return [
            r.div('tryfinally nowrap',[
                r.div(None,[
                    r.keyword("try",trailing=False),
                    ':', # '\n',
                ]),
                r.div('body nowrap',[
                    r.visit_list(node.body),
                ]),
                r.div(None,[
                    r.keyword("finally",trailing=False),
                    ':', # '\n',
                ]),
                r.div('body nowrap',[
                    node.finalbody and r.visit_list(node.finalbody),
                ]),
            ]),
        ]
    #@+node:ekr.20140526082700.18191: *4* rt.Tuple
    # Tuple(expr* elts, expr_context ctx)

    def do_Tuple(self,node):
        
        r = self
        return [
            r.span("tuple",[
                '(',
                node.elts and r.visit_list(node.elts,sep=','),
                ')',
            ]),
        ]
    #@+node:ekr.20140526082700.18192: *4* rt.UnaryOp
    def do_UnaryOp(self,node):
        
        r = self
        op_name = r.op_name(node.op)
        return [
            r.span(op_name.strip(),[
                r.op(op_name,trailing=False),
                r.visit(node.operand),
            ]),
        ]
    #@+node:ekr.20140526082700.18193: *4* rt.While
    def do_While(self,node):
        
        r = self
        orelse = node.orelse and [
            r.div(None,[
                r.keyword("else",trailing=False),
                ':', # '\n',
            ]),
            r.div('body nowrap',[
                r.visit_list(node.orelse),
            ]),
        ]
        return [
            r.div('while nowrap',[
                r.div(None,[
                    r.keyword("while"),
                    r.visit(node.test),
                    ':', # '\n',
                ]),
                r.div('body nowrap',[
                    r.visit_list(node.body),
                ]),
                orelse,
            ]),
        ]
    #@+node:ekr.20140526082700.18194: *4* rt.With
    # With(expr context_expr, expr? optional_vars, stmt* body)

    def do_With(self,node):

        r = self
        context_expr = getattr(node,'context_expr',None)
        optional_vars = getattr(node,'optional_vars',None)
        optional_vars = optional_vars and [
            r.keyword('as',leading=True),
            r.visit(optional_vars),
        ]
        return [
            r.div('with nowrap',[
                r.div(None,[
                    r.keyword('with'),
                    context_expr and r.visit(context_expr),
                    optional_vars,
                    ":",
                ]),
                r.div('body nowrap',[
                    r.visit_list(node.body),
                ]),
            ]),
        ]
    #@+node:ekr.20140526082700.18195: *4* rt.Yield
    def do_Yield(self,node):
        
        r = self
        return [
            r.div('yield nowrap',[
                r.keyword("yield"),
                r.visit(node.value),
            ]),
        ]
    #@-others
#@+node:ekr.20140526082700.18312: ** class SymbolTable
class SymbolTable:
    '''A container class for all symbol table info.'''
    #@+others
    #@+node:ekr.20140526082700.18313: *3*  st.ctor and repr
    def __init__ (self,cx):

        self.cx = cx
        self.d = {} # Keys are names, values are symbol table entries.
        self.max_name_length = 1 # Minimum field width for dumps.

    def __repr__ (self):
        return 'Symbol Table for %s\n' % self.cx.short_name()

    __str__ = __repr__
    #@+node:ekr.20140526082700.18314: *3* st.add_name
    def add_name (self,name):
        '''Add name to the symbol table.  Return the symbol table entry.'''
        st = self
        e = st.d.get(name)
        if not e:
            e = SymbolTableEntry(name,st)
            st.d [name] = e
            # self.stats.n_names += 1
        return e
    #@+node:ekr.20140526082700.18315: *3* st.define_name
    def define_name (self,name):
        '''Define name in the present context (symbol table).'''
        e = self.add_name(name)
        e.defined = True
        return e
    #@+node:ekr.20140526082700.18316: *3* st.dump
    def dump (self,level=0):
        '''Dump a symbol table.'''
        level,result,u = level+1,['',self],Utils()
        def put(s):
            result.append(u.indent(level,s))
        # Print the table entries.
        for key in sorted(self.d.keys()):
            e = self.d.get(key)
            result.append(e.dump(level+1))  
        result.append('')
        return '\n'.join(result)        
    #@+node:ekr.20140526082700.18317: *3* st.get_name
    def get_name (self,name):
        '''Return the symbol table entry for name.'''
        return self.d.get(name)
    #@-others
#@+node:ekr.20140526082700.18318: ** class SymbolTableEntry
class SymbolTableEntry:
    '''A class representing the symbol table information for one name.'''
    #@+others
    #@+node:ekr.20140616055519.17768: *3*   not used
    #@+node:ekr.20140526082700.18321: *4* e.add_chain
    def add_chain (self,base,op):
        '''Add op to the e.chains list, where e is the STE for base.'''
        e = self
        d = e.chains.get(base,{})
        s = repr(op)
        # g.trace('base: %s chain: %s' % (base,s))
        chain = d.get(s)
        if chain:
            assert repr(chain) == repr(op)
        else:
            d [s] = op
            e.chains [base] = d
    #@+node:ekr.20140526082700.18323: *4* e.dump_chains
    def dump_chains(self,level):
        
        result,u = [],Utils()
        def put(s):
            result.append(u.indent(level,s))
        # self.chains is a dict of dicts.
        keys = list(self.chains.keys())
        for key in keys:
            d = self.chains.get(key,{})
            for key2 in list(d.keys()):
                chain = d.get(key2)
                put(repr(chain))
        result.sort()
        return '\n'.join(result)
    #@+node:ekr.20140526082700.18319: *3*  e.ctor
    def __init__ (self,name,st):

        self.cx = st.cx
        self.defined = False
            # True: The name appears with ctx='Store'.
            # and the name is not in self.st.cx.globals_list.
        self.name = name
        self.referenced = False
        self.resolved = False
            # True: the name appears with any ctx except 'Store'.
        self.st = st
        # Update the length field for dumps.
        st.max_name_length = max(
            st.max_name_length,
            name and len(name) or 0)
    #@+node:ekr.20140526082700.18320: *3*  e.repr
    def __repr__ (self):
        
        e = self
        return 'STE(%s:%s)' % (e.cx,e.name) # id(e)
        
    __str__ = __repr__
    #@+node:ekr.20140526082700.18322: *3* e.dump
    def dump(self,level=0):
        
        e,result,u = self,[],Utils()
        def put(s):
            result.append(self.u.indent(level,s))
        put('STE cx: %s name: %s defined: %s' % (e.cx,e.name,e.defined))
        # if e.chains:
            # n = self.st.max_name_length - len(self.name)
            # pad = ' '*n
            # put('chains:...')
            # result.append(e.dump_chains(level=level+1))
        return '\n'.join(result)
    #@-others
#@+node:ekr.20140526082700.17450: ** class Utils
class Utils:
    
    '''A class containing utility methods and pre-defined objects.
    
    This is a lightweight class; it may be instantiated freely.
    
    Important: this class no longer contains application globals.
    '''

    #@+others
    #@+node:ekr.20140526082700.17451: *3*  u.ctor
    def __init__ (self):
        
        # Unit tests should create new App instances to ensure these get inited properly.

        # Used by modified pyflackes code.
            # self.attrs_def_dict = {} # Keys formatted expressions, values lists of attributes.
            # self.attrs_ref_dict = {} # Ditto.

        # Set by u.format().
        self.formatter_instance = None
        self.pattern_formatter_instance = None
        
        # Set by u.all_statement/node/statement_generator()
        self.all_statement_generator_instance = None
        self.local_node_generator_instance = None
        self.node_generator_instance = None 
        self.statement_generator_instance = None
    #@+node:ekr.20140526082700.17452: *3*  u.generators
    #@+node:ekr.20140526082700.17453: *4* u.all_nodes and u.local_nodes
    def all_nodes(self,node):
        u = self
        if not u.node_generator_instance:
            u.node_generator_instance = NodeGenerator()
        return u.node_generator_instance.run(node)
        
    def local_nodes(self,node):
        u = self
        if not u.local_node_generator_instance:
            u.local_node_generator_instance = LocalNodeGenerator()
        return u.local_node_generator_instance.run(node)
    #@+node:ekr.20140526082700.17454: *4* u.all_statements and u.local_statements
    def all_statements(self,context_node):
        '''Yield *all* statements of a context node.'''
        # This is used only by the context generator.
        u = self
        if not u.all_statement_generator_instance:
            u.all_statement_generator_instance = AllStatementsPseudoGenerator()
        return u.all_statement_generator_instance.run(context_node)
        
    def local_statements(self,context_node):
        '''Yield all  local statements of a context node.'''
        u = self
        if not u.statement_generator_instance:
            u.statement_generator_instance = LocalStatementGenerator()
        return u.statement_generator_instance.run(context_node)
    #@+node:ekr.20140526082700.17455: *4* u.assignments
    def assignments(self,statement):
        
        '''A generator returning all assignment nodes in statement's tree.'''
        
        for statement2 in self.local_statements(statement):
            if isinstance(statement2,(ast.Assign,ast.AugAssign)):
                yield statement2
    #@+node:ekr.20140526082700.17456: *4* u.assignments_to
    def assignments_to (self,cx,target_name):

        u = self
        result = []
        for statement in u.assignments(cx):
            if isinstance(statement,ast.Assign):
                #  Assign(expr* targets, expr value)
                for target in statement.targets:
                    s = u.format(target)
                    kind2 = u.kind(target)
                    if kind2 == 'Name':
                        if target_name == target.id:
                            result.append(statement)
                    elif kind2 == 'Tuple':
                        # Tuple(expr* elts, expr_context ctx)
                        for item2 in target.elts:
                            if u.kind(item2) == 'Name' and target_name == item2.id:
                                result.append(statement)
            elif isinstance(statement,ast.AugAssign):
                if u.kind(statement.target) == 'Name' and target_name == statement.target.id:
                    result.append(statement)
            else:
                # The assignments generator returns only Assign and AugAssign nodes.
                assert False
        # if result: # g.trace(target_name,','.join([u.format(z) for z in result]))
        return result
    #@+node:ekr.20140526082700.17457: *4* u.attributes
    def attributes(self,node):
        
        '''A generator returning all ast.Attribute nodes in node's tree.'''
        
        for node2 in self.local_nodes(node):
            if isinstance(node2,ast.Attribute):
                yield node2
    #@+node:ekr.20140526082700.17458: *4* u.calls
    def calls(self,statement):

        '''A generator returning all ast.Call nodes in statement's tree.'''
        
        for statement2 in self.local_statements(statement):
            if isinstance(statement2,ast.Call):
                yield statement2
    #@+node:ekr.20140526082700.17459: *4* u.contexts
    def contexts(self,statement):
        '''
        A generator returning all ast.Module,ast.ClassDef,ast.FunctionDef
        and ast.Lambda nodes in statement's tree.
        '''
        assert isinstance(statement,ast.Module),repr(statement)
        yield statement
        for statement2 in self.all_statements(statement):
            if isinstance(statement2,(ast.ClassDef,ast.FunctionDef,ast.Lambda,ast.Module)):
                yield statement2
    #@+node:ekr.20140526082700.17460: *4* u.definitions_of
    # FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list)
    # arguments (expr* args, identifier? vararg, identifier? kwarg, expr* defaults)

    def definitions_of (self,cx,target_name):

        u = self
        result = []

        # Look for defintions in the context node itself.
        if isinstance(cx,ast.FunctionDef):
            if cx.name == target_name:
                result.append(cx)
            assert isinstance(cx.args,ast.arguments)
            assert isinstance(cx.args.args,(list))
            args = cx.args
            for arg in args.args:
                if hasattr(arg,'id') and arg.id == target_name:
                    result.append(cx)
            if args.vararg and args.vararg == target_name:
                result.append(cx)
            if args.kwarg and args.kwarg == target_name:
                result.append(cx)
        elif isinstance(cx,ast.ClassDef):
            if cx.name == target_name:
                result.append(cx)
                
        # Search all the local nodes.
        for node in u.local_nodes(cx):
            kind = u.kind(node)
            if kind == 'Assign':
                #  Assign(expr* targets, expr value)
                for target in node.targets:
                    s = u.format(target)
                    kind2 = u.kind(target)
                    if kind2 == 'Name':
                        if target_name == target.id:
                            result.append(node)
                    elif kind2 == 'Tuple':
                        # Tuple(expr* elts, expr_context ctx)
                        for item2 in target.elts:
                            if u.kind(item2) == 'Name' and target_name == item2.id:
                                result.append(node)
            elif kind == 'AugAssign':
                if u.kind(node.target) == 'Name' and target_name == node.target.id:
                    result.append(node)
            elif kind == 'For':
                s = u.format(node)
                assert s.startswith('for ')
                i = s.find(' in ')
                assert i > -1
                s2 = s[4:i].strip('()')
                aList = s2.split(',')
                for z in aList:
                    if z.strip() == target_name:
                        result.append(node)
            elif kind == 'ListComp':
                # node.generators is a comprehension.
                for item in node.generators:
                    target = item.target
                    kind2 = u.kind(target)
                    if kind2 == 'Name':
                        if target_name == target.id:
                            result.append(node)
                            break
                    elif kind2 == 'Tuple':
                        for item2 in target.elts:
                            if u.kind(item2) == 'Name' and target_name == item2.id:
                                result.append(node)
                                break
                    else:
                        assert False,kind2
            else:
                pass
                # assert False,kind
        result = list(set(result))
        # if result: g.trace('%20s: %s' % (target_name,','.join([u.format(z) for z in result])))
        return result
    #@+node:ekr.20140526082700.17461: *4* u.defs
    def defs(self,statement):
        '''A generator returning all ast.FunctionDef nodes in statement's tree.'''
        for statement2 in self.local_statements(statement):
            if isinstance(statement2,ast.FunctionDef):
                yield statement2
    #@+node:ekr.20140526082700.17462: *4* u.imports
    def imports(self,statement):
        
        '''A generator returning all import statements in node's tree.'''
        
        for statement2 in self.local_statements(statement):
            if isinstance(statement2,(ast.Import,ast.ImportFrom)):
                yield statement2
    #@+node:ekr.20140526082700.17463: *4* u.returns
    def returns(self,statement):
        
        '''A generator returning all ast.Return nodes in node's tree.'''

        for statement2 in self.local_statements(statement):
            if isinstance(statement2,ast.Return):
                yield statement2
    #@+node:ekr.20140526082700.17464: *3* u.clean_project_name
    def clean_project_name(self,s):
        
        i = s.find(' ')
        if i > -1:
            s = s[:i].strip()

        return s.replace('(','').replace(')','').replace(' ','_').strip()
    #@+node:ekr.20140526082700.17465: *3* u.collect
    def collect(self,tag=None,trace=False):

        if trace:
            s1 = '%5s' % '' if tag is None else tag
            s2 = '%4s %4s %4s' % gc.get_count()
            print('gc: %s %s' % (s1,s2))
        gc.collect()
        # This is always 0,0,0
        # print('gc: %s %s %s' % gc.get_count())
    #@+node:ekr.20140526082700.17466: *3* u.compute_context_level
    def compute_context_level(self,node):
        
        '''Compute the indentation of a node.
        This method eliminates the need to inject an stc_level var into the tree.
        '''
        
        # The kinds of nodes that increase indentation level.
        if hasattr(node,'stc_parent'):
            level,parent = 0,node.stc_parent
            while parent:
                if isinstance(parent,(ast.ClassDef,ast.FunctionDef,ast.Module)):
                    level += 1
                parent = parent.stc_parent
            return level
        else:
            g.trace('** no stc_parent field!',node)
            return 0
    #@+node:ekr.20140526082700.17467: *3* u.compute_def_cx
    def compute_def_cx(self,node):
        parent = node
        while parent:
            if isinstance(parent,ast.FunctionDef):
                return parent
            else:
                parent = parent.stc_parent
        return None
    #@+node:ekr.20140526082700.17468: *3* u.compute_module_cx
    # This is clumsy: the Module visitor can set ivars in the traverser.
    def compute_module_cx(self,node):
        '''Return the module context for the given node.'''
        parent = node
        while parent:
            if isinstance(parent,ast.Module):
                return parent
            else:
                parent = parent.stc_parent
        assert False,node
    #@+node:ekr.20140526082700.17469: *3* u.compute_class_or_module_cx
    def compute_class_or_module_cx(self,node):
        '''Return the class or module context of node.'''
        parent = node
        while parent:
            if isinstance(parent,(ast.ClassDef,ast.Module,)):
                return parent
            else:
                parent = parent.stc_parent
        assert False,node
    #@+node:ekr.20140526082700.17470: *3* u.compute_node_cx
    def compute_node_cx(self,node):
        '''Return the nearest enclosing context for the given node.'''
        parent = node
        while parent:
            if isinstance(parent,(ast.ClassDef,ast.FunctionDef,ast.Module,ast.Lambda,ast.Module)):
                return parent
            else:
                parent = parent.stc_parent
        assert False,node
    #@+node:ekr.20140526082700.17471: *3* u.compute_node_level
    def compute_node_level(self,node):
        
        '''Compute the indentation of a node.
        This method eliminates the need to inject an stc_level var into the tree.
        '''
        
        # The kinds of nodes that increase indentation level.
        level_changers = (
            ast.ClassDef,ast.FunctionDef,ast.Module,
            ast.For,ast.If,ast.TryExcept,ast.TryFinally,ast.While,ast.With,
        )
        if hasattr(node,'stc_parent'):
            level,parent = 0,node.stc_parent
            while parent:
                if isinstance(parent,level_changers):
                    level += 1
                parent = parent.stc_parent
            return level
        else:
            g.trace('** no stc_parent field!',node)
            return 0
    #@+node:ekr.20140526082700.17472: *3* u.diff_time, get_time & time_format
    def diff_time(self,t):
        
        return '%4.2f sec.' % (time.time()-t)
        
    def get_time(self):
        
        # Used to put timestamps in headlines.
        return time.strftime('%Y/%m/%d/%H:%M:%S',time.localtime())

    def time_format(self,t):
        
        return '%4.2f sec.' % t
    #@+node:ekr.20140526082700.17473: *3* u.drivers: p0,p01,p012,p0_s,p01_s,p012_s
    # For use by unit tests.
    #@+node:ekr.20140526082700.17474: *4* u.p0
    def p0(self,files,project_name,report):
        '''Parse all files in a list of file names.'''
        u = self
        if report and not g.app.runningAllUnitTests:
            print(project_name)
        t = time.time()
        d = dict([(fn,u.parse_file(fn)) for fn in files])
        p0_time = u.diff_time(t)
        if report:
            u.p0_report(len(files),p0_time)
        return d
    #@+node:ekr.20140526082700.17475: *4* u.p01
    def p01(self,files,project_name,report):
        '''Parse and run P1 on all files in a list of file names.'''
        u = self
        if report and not g.app.runningAllUnitTests:
            print(project_name)
        # Pass 0.
        t0 = time.time()
        d = dict([(fn,u.parse_file(fn)) for fn in files])
        p0_time = u.diff_time(t0)
        # Pass 1.
        t = time.time()
        n_attrs = 0
        # n_contexts = 0
        # n_defined = 0
        n_nodes = 0
        u.p1 = p1 = P1() # Set u.p1 for stats.
        for fn in files:
            root = d.get(fn)
            p1(fn,root)
            n_attrs += p1.n_attributes
            n_nodes += p1.n_nodes
        p1_time = u.diff_time(t)
        tot_time = u.diff_time(t0)
        if report:
            u.p01_report(len(files),p0_time,p1_time,tot_time,
                n_attrs=n_attrs,n_nodes=n_nodes)
        return d
    #@+node:ekr.20140526082700.17476: *4* u.p012 (not used)
    # def p012(self,files,project_name,report):
        # '''Parse and run P1 and TypeInferrer on all files in a list of file names.'''
        # u = self
        # if report and not g.app.runningAllUnitTests:
            # print(project_name)
        # # Pass 0.
        # t0 = time.time()
        # d = dict([(fn,u.parse_file(fn)) for fn in files])
        # p0_time = u.diff_time(t0)
        # # Pass 1.
        # t = time.time()
        # p1 = P1()
        # for fn in files:
            # root = d.get(fn)
            # p1(fn,root)
        # p1_time = u.diff_time(t)
        # # Pass 2.
        # t = time.time()
        # ti = TypeInferrer()
        # for fn in files:
            # ti(d.get(fn))
        # p2_time = u.diff_time(t)
        # tot_time = u.diff_time(t0)
        # if report:
            # u.p012_report(len(files),p0_time,p1_time,p2_time,tot_time)
        # return d
    #@+node:ekr.20140526082700.17477: *4* u.p0_report
    def p0_report(self,n,t0):
        
        '''Report stats for p0 and p0s.'''
        if not g.app.runningAllUnitTests:
            if n > 0:
                print('files: %s' % n)
            print('parse: %s' % t0)
    #@+node:ekr.20140526082700.17478: *4* u.p01_report
    def p01_report(self,n,t0,t1,tot_t,n_attrs=None,n_nodes=None):
        
        '''Report stats for p01 and p01s.'''
        if not g.app.runningAllUnitTests:
            if n > 0:
                print('files: %s' % n)
            print('parse: %s' % t0)
            if n_attrs is None:
                print('   p1: %s' % t1)
            else:
                print('   p1: %s nodes: %s attrs: %s' % (t1,n_nodes,n_attrs))
            print('  tot: %s' % tot_t)
    #@+node:ekr.20140526082700.17479: *4* u.p012_report
    def p012_report(self,n,t0,t1,t2,tot_t,n_attrs=None,n_nodes=None):
        
        '''Report stats for p012 and p012s.'''
        if not g.app.runningAllUnitTests:
            if n > 0:
                print('files: %s' % n)
            print('parse: %s' % t0)
            if n_attrs is None:
                print('   p1: %s' % t1)
            else:
                print('   p1: %s nodes: %s attrs: %s' % (t1,n_nodes,n_attrs))
            print('infer: %s' % t2)
            print('  tot: %s' % tot_t)

    #@+node:ekr.20140526082700.17480: *4* u.p0s
    def p0s(self,s,report=True,tag='<string>'):
        '''Parse an input string.'''
        u = self
        s = g.adjustTripleString(s,-4)
        t = time.time()
        node = ast.parse(s,filename=tag,mode='exec')
        node.stc_fn = tag
        p0_time = u.diff_time(t)
        if report:
            u.p0_report(1,p0_time)
        if 1:
            # The caller creates root_d.
            return node
        else:
            # Return a root_d,.
            return {'string-file':node}
    #@+node:ekr.20140526082700.17481: *4* u.p01s
    def p01s(self,s,report=True,tag='<string>'):
        
        '''Parse and run P1 on an input string.'''
        u = self
        s = g.adjustTripleString(s,-4)
        t0 = time.time()
        node = ast.parse(s,filename=tag,mode='exec')
        node.stc_fn = tag
        p0_time = u.diff_time(t0)
        t = time.time()
        P1().run(tag,node)
        p1_time = u.diff_time(t)
        tot_time = u.diff_time(t0)
        if report:
            u.p01_report(1,p0_time,p1_time,tot_time)
        if 1:
            return node
        else:
            # Return a root_d
            return {'string-file':node}

    #@+node:ekr.20140526082700.17482: *4* u.p012s (not used)
    # def p012s(self,s,report=True,tag='<string>'):
        
        # '''Parse and run P1 and TypeInferrer on an input string.'''
        # u = self
        # s = g.adjustTripleString(s,-4)
        # t0 = time.time()
        # node = ast.parse(s,filename=tag,mode='exec')
        # node.stc_fn = tag
        # p0_time = u.diff_time(t0)
        # t = time.time()
        # P1().run(tag,node)
        # p1_time = u.diff_time(t)
        # t = time.time()
        # TypeInferrer().run(node)
        # p2_time = u.diff_time(t)
        # tot_time = u.diff_time(t0)
        # if report:
            # u.p012_report(None,1,p0_time,p1_time,p2_time,tot_time)
        # # New: return a root_d, not node.
        # return {'string-file':node}
    #@+node:ekr.20140526082700.17483: *3* u.dump_ast & helpers
    # Adapted from Python's ast.dump.

    def dump_ast(self,node,annotate_fields=True,disabled_fields=None,
        include_attributes=False,indent=2
    ):
        """
        Return a formatted dump (a string) of the AST node.
        
        annotate_fields:    True: show names of fields (can't eval the dump).
        disabled_field:     List of names of fields not to show: e.g. ['ctx',]
        include_attributes: True: show line numbers and column offsets.
        indent:             Number of spaces for each indent.
        
        """
        
        #@+others
        #@+node:ekr.20140526082700.17484: *4* class AstDumper
        class AstDumper:
            
            def __init__(self,u,annotate_fields,disabled_fields,format,include_attributes,indent_ws):
            
                self.u = u
                self.annotate_fields = annotate_fields
                self.disabled_fields = disabled_fields
                self.format = format
                self.include_attributes = include_attributes
                self.indent_ws = indent_ws

            #@+others
            #@+node:ekr.20140526082700.17485: *5* dump
            def dump(self,node,level=0):
                sep1 = '\n%s' % (self.indent_ws*(level+1))
                if isinstance(node,ast.AST):
                    fields = [(a,self.dump(b,level+1)) for a,b in self.get_fields(node)]
                        # ast.iter_fields(node)]
                    if self.include_attributes and node._attributes:
                        fields.extend([(a,self.dump(getattr(node,a),level+1))
                            for a in node._attributes])
                    aList = self.extra_attributes(node)
                    if aList: fields.extend(aList)
                    if self.annotate_fields:
                        aList = ['%s=%s' % (a,b) for a,b in fields]
                    else:
                        aList = [b for a,b in fields]
                    compressed = not any([isinstance(b,list) and len(b)>1 for a,b in fields])
                    name = node.__class__.__name__
                    if compressed and len(','.join(aList)) < 100:
                        return '%s(%s)' % (name,','.join(aList))
                    else:
                        sep = '' if len(aList) <= 1 else sep1
                        return '%s(%s%s)' % (name,sep,sep1.join(aList))
                elif isinstance(node,list):
                    compressed = not any([isinstance(z,list) and len(z)>1 for z in node])
                    sep = '' if compressed and len(node) <= 1 else sep1
                    return '[%s]' % ''.join(
                        ['%s%s' % (sep,self.dump(z,level+1)) for z in node])
                else:
                    return repr(node)
            #@+node:ekr.20140526082700.17486: *5* extra_attributes & helpers
            def extra_attributes (self,node):
                
                '''Return the tuple (field,repr(field)) for all extra fields.'''
                
                d = {
                    'e':      self.do_repr,
                    # '_parent':self.do_repr,
                    'cache':self.do_cache_list,
                    # 'ivars_dict': self.do_ivars_dict,
                    'reach':self.do_reaching_list,
                    'typ':  self.do_types_list,
                }

                aList = []
                for attr in sorted(d.keys()):
                    if hasattr(node,attr):
                        val = getattr(node,attr)
                        f = d.get(attr)
                        s = f(attr,node,val)
                        if s:
                            aList.append((attr,s),)
                return aList
            #@+node:ekr.20140526082700.17487: *6* AstDumper.helpers
            def do_cache_list(self,attr,node,val):
                return self.u.dump_cache(node)
                
            # def do_ivars_dict(self,attr,node,val):
                # return repr(val)

            def do_reaching_list(self,attr,node,val):
                assert attr == 'reach'
                return '[%s]' % ','.join(
                    [self.format(z).strip() or repr(z)
                        for z in getattr(node,attr)])

            def do_repr(self,attr,node,val):
                return repr(val)

            def do_types_list(self,attr,node,val):
                assert attr == 'typ'
                return '[%s]' % ','.join(
                    [repr(z) for z in getattr(node,attr)])
            #@+node:ekr.20140526082700.17488: *5* get_fields
            def get_fields (self,node):
                
                fields = [z for z in ast.iter_fields(node)]
                result = []
                for a,b in fields:
                    if a not in self.disabled_fields:
                        if b not in (None,[]):
                            result.append((a,b),)
                return result
            #@+node:ekr.20140526082700.17489: *5* kind
            def kind(self,node):
                
                return node.__class__.__name__
            #@-others
        #@-others
        
        if isinstance(node,ast.AST):
            indent_ws = ' '*indent
            dumper = AstDumper(self,annotate_fields,disabled_fields or [],
                self.format,include_attributes,indent_ws)
            return dumper.dump(node)
        else:
            raise TypeError('expected AST, got %r' % node.__class__.__name__)
    #@+node:ekr.20140526082700.17490: *3* u.dump_ivars_dict
    def dump_ivars_dict(self,d):
        
        def format_list(key):
            return self.format(d.get(key))
            # return ','.join([self.format(val) for val in d.get(key)])

        return 'ivars_dict: {%s}' % ','.join(
            ['%s:%s' % (z,format_list(z)) for z in sorted(d.keys())])
    #@+node:ekr.20140526082700.17491: *3* u.error/note/warning
    errors_given = []

    def error (self,s):
        
        # self.stats.n_errors += 1
        if s not in self.errors_given:
            self.errors_given.append(s)
            if g.app.unitTesting:
                pass
            elif g.unitTesting:
                print('Error: %s' % s)
            else:
                print('\nError: %s\n' % s)
        
    def note (self,s):
        
        print('Note: %s' % s)

    def warning (self,s):
        
        # self.stats.n_warnings += 1
        print('\nWarning: %s\n' % s)
    #@+node:ekr.20140526082700.17492: *3* u.files_in_dir
    def files_in_dir (self,theDir,recursive=True,extList=None,excludeDirs=None):
        
        '''Return a list of all Python files in the directory.
        
        Include all descendants if recursiveFlag is True.
        
        Include all file types if extList is None.
        '''
        
        # if extList is None: extList = ['.py']
        if excludeDirs is None: excludeDirs = []
        result = []

        if recursive:
            for root, dirs, files in os.walk(theDir):
                for z in files:
                    fn = g.os_path_finalize_join(root,z)
                    junk,ext = g.os_path_splitext(fn)
                    if not extList or ext in extList:
                        result.append(fn)
                if excludeDirs and dirs:
                    for z in dirs:
                        if z in excludeDirs:
                            dirs.remove(z)
        else:
            for ext in extList:
                result.extend(glob.glob('%s.*%s' % (theDir,ext)))
            
        return sorted(list(set(result)))
    #@+node:ekr.20140526082700.17493: *3* u.first_line
    def first_line(self,s):
        
        i = s.find('\n')
        return s if i == -1 else s[:i]
    #@+node:ekr.20140526082700.17494: *3* u.format & pattern_format
    def format(self,node,first_line=True,pattern=False):
        
        u = self
        if pattern:
            if not u.pattern_formatter_instance:
                u.pattern_formatter_instance = PatternFormatter()
            s = u.pattern_formatter_instance(node)
            return u.first_line(s) if first_line else s
        else:
            if not u.formatter_instance:
                u.formatter_instance = AstFormatter()
            s = u.formatter_instance(node)
            return u.first_line(s) if first_line else s
            
    def pattern_format(self,node,first_line=True):
        
        return self.format(node,first_line,True)
    #@+node:ekr.20140526082700.17495: *3* u.get_project_directory
    def get_project_directory(self,name):
        
        u = self
        # Ignore everything after the first space.
        i = name.find(' ')
        if i > -1:
            name = name[:i].strip()
        leo_path,junk = g.os_path_split(__file__)
        d = { # Change these paths as required for your system.
            'coverage': r'C:\Python26\Lib\site-packages\coverage-3.5b1-py2.6-win32.egg\coverage',
            'leo':      r'C:\leo.repo\leo-editor\leo\core',
            'lib2to3':  r'C:\Python26\Lib\lib2to3',
            'pylint':   r'C:\Python26\Lib\site-packages\pylint',
            'rope':     r'C:\Python26\Lib\site-packages\rope-0.9.4-py2.6.egg\rope\base',
            'test':     g.os_path_finalize_join(g.app.loadDir,'..','test-proj'),
        }
        dir_ = d.get(name.lower())
        # g.trace(name,dir_)
        if not dir_:
            g.trace('bad project name: %s' % (name))
        if not g.os_path_exists(dir_):
            g.trace('directory not found:' % (dir_))
        return dir_ or ''
    #@+node:ekr.20140526082700.17496: *3* u.get_source
    def get_source (self,fn):
        '''Return the entire contents of the file whose name is given.'''
        try:
            fn = g.toUnicode(fn)
            # g.trace(g.os_path_exists(fn),fn)
            f = open(fn,'r')
            s = f.read()
            f.close()
            return s
        except IOError:
            return '' # Caller gives error message.
    #@+node:ekr.20140528102444.17996: *3* u.indent
    def indent(self,level,s):

        return '%s%s' % (' '*4*level,s)
    #@+node:ekr.20140526082700.17497: *3* u.kind
    def kind(self,node):
        
        return node.__class__.__name__
    #@+node:ekr.20140526082700.17498: *3* u.last_top_level_node
    def last_top_level_node(self,c):

        p = c.rootPosition()
        while p.hasNext():
            p = p.next()
        return p
    #@+node:ekr.20140526082700.17499: *3* u.lookup
    def lookup(self,cx,key):
        '''Return the symbol table for key, starting the search at node cx.'''
        trace = False and not g.app.runningAllUnitTests
        # contexts = ast.Module,ast.ClassDef,ast.FunctionDef,ast.Lambda
        cx2 = cx
        while cx2:
            st = cx.stc_symbol_table
            if key in st.d.keys():
                return st
            else:
                cx2 = cx2.stc_context
        return None
        ###
        # assert False
        # for d in (self.builtins_d,self.special_methods_d):
            # if key in d.keys():
                # return d
        # if trace:
            # g.trace('** (ScopeBinder) no definition for %20s in %s' % (
                # key,self.format(cx)))
        # return None
    #@+node:ekr.20140526082700.17500: *3* u.module_name
    def module_name (self,fn):
        
        fn = g.shortFileName(fn)
        if fn.endswith('.py'):
            fn = fn[:-3]
        return fn
    #@+node:ekr.20140526082700.17501: *3* u.node_after_tree
    # The _parent must have been injected into all parent nodes for this to work.
    # This will be so, because of the way in which visit traverses the tree.

    def node_after_tree (self,tree):
        
        trace = False
        u = self
        tree1 = tree # For tracing
        
        if not isinstance(tree,ast.AST):
            return None
        
        def children(tree):
            return [z for z in ast.iter_child_nodes(tree)]
            
        def parent(tree):
            if not hasattr(tree,'_parent'): g.trace('***no _parent: %s' % repr(tree))
            return getattr(tree,'_parent',None)

        def next(tree):
            if parent(tree):
                sibs = children(parent(tree))
                if tree in sibs:
                    i = sibs.index(tree)
                    if i + 1 < len(sibs):
                        return sibs[i+1]
            return None

        result = None
        while tree:
            result = next(tree)
            if result:
                break
            else:
                tree = parent(tree)

        if trace:
            def info(node):
                kind = node and node.__class__.__name__
                return '%s: %9s' % (kind,id(node))
                
            for z in (ast.Module,ast.ClassDef,ast.FunctionDef):
                if isinstance(tree1,z):
                    g.trace('node: %22s, parent: %22s, after: %22s' % (
                        info(tree1),info(parent(tree1)),info(result)))
                    break

        return result
    #@+node:ekr.20140526082700.17502: *3* u.parse_...
    def parse_file(self,fn):
        
        s = self.get_source(fn)
        if not s:
            g.trace('*** not found',fn)
        node = ast.parse(s,filename=fn,mode='exec')
        node.stc_fn = fn # Inject file name for dumps.
        return node

    def parse_string(self,fn,s):

        node = ast.parse(s,filename=fn,mode='exec')
        node.stc_fn = '<string>' # Inject file name for dumps.
        return node
        
    def parse_files_in_list(self,aList):
        
        return dict([(fn,self.parse_file(fn)) for fn in aList])
    #@+node:ekr.20140526082700.17503: *3* u.profile
    def profile(self,c,project_name,verbose=True):
        
        '''Run a full project test with profiling enabled.'''
        
        import pstats # May fail on some Linux installations.
        import cProfile

        u = self
        clean_project_name = u.clean_project_name(project_name)
        path,junk = g.os_path_split(c.fileName())
        fn = g.os_path_finalize_join(path,'report','stc_profile_data.txt')
        command = 'import statictypechecking as stc; stc.Utils().test_wrapper("%s")' % (
            project_name)
        cProfile.run(command,fn)
        f = g.FileLikeObject()
        ps = pstats.Stats(fn,stream=f)
        ps.strip_dirs()
        ps.sort_stats('time',) # 'calls','cumulative','time')
        ps.print_stats()
        s = f.read()
        f.close()
        fn2 = g.os_path_finalize_join(path,'report','stc_report_%s.txt' % (clean_project_name))
        f2 = open(fn2,'w')
        f2.write(s)
        f2.close()
        if verbose:
            print('profile written to %s' % (fn2))
        # print(s)
        # os.system('ed "%s"' % (fn2))
    #@+node:ekr.20140526082700.17504: *3* u.project_files
    def project_files(self,name,force_all=False):
        u = self
        # Ignore everything after the first space.
        i = name.find(' ')
        if i > -1:
            name = name[:i].strip()
        leo_path,junk = g.os_path_split(__file__)
        d = { # Change these paths as required for your system.
            'coverage': (
                r'C:\Python26\Lib\site-packages\coverage-3.5b1-py2.6-win32.egg\coverage',
                ['.py'],['.bzr','htmlfiles']),
            'leo':(
                r'C:\leo.repo\leo-editor\leo\core',
                # leo_path,
                ['.py'],['.bzr']),
            'lib2to3': (
                r'C:\Python26\Lib\lib2to3',
                ['.py'],['tests']),
            'pylint': (
                r'C:\Python26\Lib\site-packages\pylint',
                ['.py'],['.bzr','test']),
            'rope': (
                r'C:\Python26\Lib\site-packages\rope-0.9.4-py2.6.egg\rope\base',['.py'],['.bzr']),
            'test': (
                g.os_path_finalize_join(leo_path,'test-proj'),
                ['.py'],['.bzr']),
        }
        data = d.get(name.lower())
        if not data:
            g.trace('bad project name: %s' % (name))
            return []
        theDir,extList,excludeDirs=data
        files = u.files_in_dir(theDir,recursive=True,extList=extList,excludeDirs=excludeDirs)
        if files:
            if name.lower() == 'leo':
                for exclude in ['__init__.py','format-code.py']:
                    files = [z for z in files if not z.endswith(exclude)]
                # Add standard plugins files:
                plugins = [
                    'baseNativeTree.py',
                    'free_layout.py',
                    'nested_splitter.py',
                    'qtframecommands.py',
                    'qtGui.py',
                ]
                for plugin in plugins:
                    fn = g.os_path_finalize_join(theDir,'..','plugins',plugin)
                    if fn and g.os_path_exists(fn):
                        files.append(fn)
            if g.app.runningAllUnitTests and len(files) > 1 and not force_all:
                return [files[0]]
        if not files:
            g.trace(theDir)
        if g.app.runningAllUnitTests and len(files) > 1 and not force_all:
            return [files[0]]
        else:
            return files
    #@+node:ekr.20140526082700.17505: *3* u.showAttributes
    # Used by modified pyflakes code.

    def showAttributes(self,def_d,ref_d):

        def_keys = sorted(def_d.keys())
        ref_keys = sorted(ref_d.keys())
        g.trace('Dumps of attributes...')
        def show_list(aList):
            return ','.join(aList)
        if 0:
            g.trace('Defined attributes...')
            for key in def_keys:
                print('%30s %s' % (key,show_list(def_d.get(key))))
        if 0:
            print('\nReferenced attributes...')
            for key in ref_keys:
                print('%30s %s' % (key,show_list(ref_d.get(key))))
        if 0:
            print('\nReferenced, not defined attributes...')
            result = []
            for key in ref_keys:
                if key not in def_keys:
                    aList = ref_d.get(key,[])
                    for z in aList:
                        result.append('%s.%s' % (key,z))
            for s in sorted(result):
                print(s)
        if 0:
            print('\nDefined, not referenced attributes...')
            result = []
            for key in def_keys:
                if key not in ref_keys:
                    aList = def_d.get(key,[])
                    for z in aList:
                        result.append('%s.%s' % (key,z))
            for s in sorted(result):
                print(s)
        if 1:
            table = (
                "'",'"',
                'aList','aList2','u','at',
                'BaseEditCommandsClass',
                'c','c1','c2','ch','cc',
                # 'c.frame',
                # 'c.frame.body.bodyCtrl','c.frame.body.bodyCtrl.widget',
                # 'c.frame.tree','c.frame.tree.widget',
                'd','d1','d2','g','g.app','k',
                'lm','menu','mf',
                'p','p1','p2', # 'p.v','p2','p2.v','p.b','p.h',
                'QFont','QtCore','QtGui',
                'pc','qt','rf','root',
                's','s1','s2',
                'table','theFile','tc','tm','tt','tree',
                'u','ui',
                'v','v2','vnode',# 'v.b','v.h','v2.b','v2.h',
                'w','w2','widget','wrapper','wrapper2',
                'x',
                'os','pdb','re','regex','string','StringIO','sys','subprocess',
                'tabnanny','time','timer','timeit','token','traceback','types',
                'unittest','urllib','urlparse','xml',
                'leoApp','leoBody','leoCache','leoColor','leoCommands','leoConfig',
                'LeoFind','leoFrame','LeoGui','leoIPython','leoImport',
                'leoLog','LeoMenu','leoNodes','leoPlugins','leoRst',
                'leoTangle','leoTest','LeoTree',
            )
            print('\nAll attributes...')
            result = []
            for key in def_keys:
                aList = def_d.get(key,[])
                for z in aList:
                    result.append('%s.%s' % (key,z))
            for key in ref_keys:
                aList = ref_d.get(key,[])
                for z in aList:
                    result.append('%s.%s' % (key,z))
            if 1:
                result = [s for s in result
                    if not any([s.startswith(s2+'.') or s.startswith(s2+'[') for s2 in table])]
                table2 = ('join','strip','replace','rstrip')
                result = [s for s in result
                    if not s.startswith("'") or not any([s.endswith('.'+s2) for s2 in table2])]
                table3 = ('__init__','__name__','__class__','__file__',)
                result = [s for s in result
                    if not any([s.endswith('.'+s2) for s2 in table3])]
            if 1:
                for s in sorted(set(result)):
                    if not s.startswith('self.'):
                        print(s)
            print('%s attributes' % len(result))
    #@+node:ekr.20140526082700.17506: *3* u.test_wrapper
    def test_wrapper(self,project_name):
        
        import statictypechecking as stc
            # no need to reload stc.

        u = Utils()
        aList = u.project_files(project_name)
        for fn in aList:
            # u.module(fn=fn)
            root = u.parse_file(fn)
            # print(u.first_line(u.format(root)))
    #@+node:ekr.20140526082700.17507: *3* u.update_run_count
    def update_run_count(self,verbose=False):
        
        # Bump the cumulative script count.
        d = g.app.permanentScriptDict
        d['n'] = n = 1 + d.get('n',0)
        if verbose and not g.app.runningAllUnitTests:
            print('run %s...' % (n))
    #@-others
#@-others
# Unit tests are the main program, at present.
# if __name__ == '__main__':
    # test()
#@@language python
#@@tabwidth -4
#@@pagewidth 60
#@-leo

# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20140526082700.17153: * @file leoSTC.py
#@@first
'''
Parsing/analysis classes.  Originally developed for:
https://groups.google.com/forum/?fromgroups#!forum/python-static-type-checking
'''
#@+<< copyright notices >>
#@+node:ekr.20140526082700.17154: ** << copyright notices >>
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
#@+node:ekr.20140526082700.17155: ** << imports >>
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
# import textwrap
import time
# import types
#@-<< imports >>
#@+<< naming conventions >>
#@+node:ekr.20140526082700.17156: ** << naming conventions >>
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
#@+node:ekr.20140526082700.17162: *3* .class AstBaseTraverser
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
#@+node:ekr.20140526082700.17173: *3* .class AstFullTraverser
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
    
    '''A class to recreate source code from an AST.
    
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
        args = self.visit(node.args) if node.args else ''
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
        return 'module:\n%s' % (''.join([self.visit(z) for z in  node.body]))
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
#@+node:ekr.20140526082700.17326: ** class BaseType & subclasses
#@+<< define class BaseType >>
#@+node:ekr.20140526082700.17327: *3* << define class BaseType >>
class BaseType:
    
    #@+<< about the type classes >>
    #@+node:ekr.20140526082700.17328: *4* << about the type classes >>
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
#@+node:ekr.20140526082700.17329: *3* class Any_Type
class Any_Type(BaseType):
    
    def __init__(self):
        BaseType.__init__(self,'Any')
#@+node:ekr.20140526082700.17330: *3* class Bool_Type
class Bool_Type(BaseType):
    
    def __init__(self):
        BaseType.__init__(self,'Bool')
#@+node:ekr.20140526082700.17331: *3* class Builtin_Type
class Builtin_Type(BaseType):
    
    def __init__(self):
        BaseType.__init__(self,'Builtin')
#@+node:ekr.20140526082700.17332: *3* class Bytes_Type
class Bytes_Type(BaseType):
    
    def __init__(self):
        BaseType.__init__(self,'Bytes')
#@+node:ekr.20140526082700.17333: *3* class Class_Type
# Note: ClassType is a Python builtin.
class Class_Type(BaseType):
    
    def __init__(self,cx):
        kind = 'Class: %s cx: %s' % (cx.name,cx)
        BaseType.__init__(self,kind)
        self.cx = cx # The context of the class.
        
    def __repr__(self):
        return 'Class: %s' % (self.cx.name)

    __str__ = __repr__
#@+node:ekr.20140526082700.17334: *3* class Def_Type
class Def_Type(BaseType):
    
    def __init__(self,cx,node):
        kind = 'Def(%s)@%s' % (cx,id(node))
        # kind = 'Def(%s)' % (cx)
        BaseType.__init__(self,kind)
        self.cx = cx # The context of the def.
        self.node = node
#@+node:ekr.20140526082700.17335: *3* class Dict_Type
class Dict_Type(BaseType):
    
    def __init__(self,node):
        
        # For now, all dicts are separate types.
        # kind = 'Dict(%s)' % (Utils().format(node))
        kind = 'Dict(@%s)' % id(node)
        BaseType.__init__(self,kind)
#@+node:ekr.20140526082700.17336: *3* class Inference_Failure & subclasses
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
#@+node:ekr.20140526082700.17337: *3* class List_Type
class List_Type(BaseType):
    
    def __init__(self,node):
        
        if 0: # All lists are separate types.
            kind = 'List(%s)@%s' % (Utils().format(node),id(node))
        else:
            # All lists have the same type.
            kind = 'List()'
        BaseType.__init__(self,kind)
#@+node:ekr.20140526082700.17338: *3* class Module_Type
class Module_Type(BaseType):
    
    def __init__(self,cx,node):
        kind = 'Module(%s)@%s' % (cx,id(node))
        BaseType.__init__(self,kind)
        self.cx = cx # The context of the module.
#@+node:ekr.20140526082700.17339: *3* class None_Type
class None_Type(BaseType):
    
    def __init__(self):
        BaseType.__init__(self,'None')
#@+node:ekr.20140526082700.17340: *3* class Num_Type, Int_Type, Float_Type
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

        

#@+node:ekr.20140526082700.17341: *3* class String_Type
class String_Type(BaseType):
    
    def __init__(self):
        BaseType.__init__(self,'String')
#@+node:ekr.20140526082700.17342: *3* class Tuple_Type
class Tuple_Type(BaseType):
    
    def __init__(self,node):
        
        # For now, all tuples are separate types.
        # kind = 'Tuple(%s)@%s' % (Utils().format(node),id(node))
        # kind = 'Tuple(%s)' % (Utils().format(node))
        kind = 'Tuple(@%s)' % id(node)
        BaseType.__init__(self,kind)
#@-others

#@+node:ekr.20140527071205.16687: ** class DataTraverser
class DataTraverser(AstFullTraverser):
    '''
    Traversal to create global data dict d.
    
    Like P1, this class injects stc_parent and stc_context links.
    Unlike P1, this class does not inject stc_symbol_table links.
    '''
    def __init__(self,d_defs,d_refs):
        AstFullTraverser.__init__(self)
        self.d_defs = d_defs
        self.d_refs = d_refs
        self.in_aug_assign = False
            # A hack: True if visiting the target of an AugAssign node.
        self.u = Utils()
    def __call__(self,fn,node):
        self.run(fn,node)
    #@+others
    #@+node:ekr.20140527071205.16688: *3* class Dummy_Node
    class Dummy_Node:
        '''A class containing only injected links.'''
        def __init__(self):
            self.stc_parent = None
            self.stc_context = None

    #@+node:ekr.20140527071205.16689: *3*  dt.run (entry point)
    def run (self,fn,root):
        '''Run the prepass: init, then visit the root.'''
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
    def define_name(self,cx,name):
        '''Called when name is defined in the given context.'''
        # Note: cx (an AST node) is hashable.
        aSet = self.d_defs.get(name,set())
        aSet.add(cx)
        self.d_defs[name] = aSet
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
        if 0: ### Old code
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
    #@+node:ekr.20140527071205.16697: *4* dt.FunctionDef
    # FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list)

    def do_FunctionDef (self,node):
        
        self.n_contexts += 1
        parent_cx = self.context
        assert parent_cx == node.stc_context
        if 0: ### old code
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
    #@+node:ekr.20140527071205.16698: *4* dt.Global
    # Global(identifier* names)

    def do_Global(self,node):
        
        cx = self.u.compute_module_cx(node)
        ### assert hasattr(cx,'stc_symbol_table'),cx
        node.stc_scope = cx
        for name in node.names:
            self.define_name(cx,name)
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
            ### Here, we treat imports as *references*.
            self.reference_name(cx,name)
    #@+node:ekr.20140527071205.16700: *4* dt.Lambda
    # Lambda(arguments args, expr body)

    def do_Lambda(self,node):
        
        self.n_contexts += 1
        parent_cx = self.context
        assert parent_cx == node.stc_context
        if 0: ### Old code
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
    #@+node:ekr.20140527071205.16701: *4* dt.Module
    def do_Module (self,node):

        self.n_contexts += 1
        assert self.context is None
        assert node.stc_context is None
        if 0: ### old code
            # Inject the symbol table for this node.
            node.stc_symbol_table = SymbolTable(node)
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
            ### assert hasattr(cx,'stc_symbol_table'),cx
            if not self.in_aug_assign:
                self.define_name(cx,node.id)
            node.stc_scope = cx
        else:
            # ast.Store does *not* necessarily define the scope.
            # For example, a += 1 generates a Store, but does not defined the symbol.
            # Instead, only ast.Assign nodes really define a symbol.
            node.stc_scope = None
    #@-others
#@+node:ekr.20140526082700.17346: ** class P1
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
    #@+node:ekr.20140526082700.17347: *3* class Dummy_Node
    class Dummy_Node:
        
        def __init__(self):
            
            # Use stc_ prefix to ensure no conflicts with ast.AST node field names.
            self.stc_parent = None
            self.stc_context = None
            self.stc_child_nodes = [] # Testing only.
    #@+node:ekr.20140526082700.17348: *3*  p1.run (entry point)
    def run (self,fn,root):
        '''Run the prepass: init, then visit the root.'''
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
    #@+node:ekr.20140526082700.17349: *3*  p1.visit (big gc anomaly)
    def visit(self,node):
        '''Inject node references in all nodes.'''
        assert isinstance(node,ast.AST),node.__class__.__name__
        self.n_nodes += 1
        if 0:
            # Injecting empty lists is expensive!
            #@+<< code that demonstrates the anomaly >>
            #@+node:ekr.20140526082700.17350: *4* << code that demonstrates the anomaly >>
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
    #@+node:ekr.20140526082700.17351: *3* p1.define_name
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
    #@+node:ekr.20140526082700.17352: *3* p1.visitors
    #@+node:ekr.20140526082700.17353: *4* p1.Attribute
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
    #@+node:ekr.20140526082700.17354: *4* p1.AugAssign (sets in_aug_assign)
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
    #@+node:ekr.20140526082700.17355: *4* p1.ClassDef
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
    #@+node:ekr.20140526082700.17356: *4* p1.FunctionDef
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

    #@+node:ekr.20140526082700.17357: *4* p1.Global
    # Global(identifier* names)

    def do_Global(self,node):
        
        cx = self.u.compute_module_cx(node)
        assert hasattr(cx,'stc_symbol_table'),cx
        node.stc_scope = cx
        for name in node.names:
            self.define_name(cx,name)
    #@+node:ekr.20140526082700.17358: *4* p1.Import & ImportFrom
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
    #@+node:ekr.20140526082700.17359: *4* p1.Lambda
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
    #@+node:ekr.20140526082700.17360: *4* p1.Module
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
    #@+node:ekr.20140526082700.17361: *4* p1.Name
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
#@+node:ekr.20140526082700.17362: ** class PatternFormatter
class PatternFormatter (AstFormatter):
    
    # def __init__ (self):
        # AstFormatter.__init__ (self)

    #@+others
    #@+node:ekr.20140526082700.17363: *3* Constants & Name
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
#@+node:ekr.20140526082700.17390: ** class Stats
class Stats(BaseStats):
    
    # def __init__(self):
        # BaseStats.__init__(self):
            
    #@+others
    #@+node:ekr.20140526082700.17391: *3* stats.init_ivars
    def init_ivars (self,n_files=0):
        
        self.n_files = n_files
        
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
    #@+node:ekr.20140526082700.17392: *3* stats.init_tables
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
#@+node:ekr.20140526082700.17393: ** class SymbolTable
class SymbolTable:
    
    def __init__ (self,cx):

        self.cx = cx
        self.attrs_d = {}
            # Keys are attribute names.
            # Values are sets of contexts having that name.
        self.d = {} # Keys are names, values are type lists.
        self.defined = set() # Set of defined names.
        self.defined_attrs = set() # Set of defined attributes.
        self.ssa_d = {} # Keys are names, values are reaching lists.
    
    def __repr__ (self):
        return 'Symbol Table for %s\n' % self.cx
    
    __str__ = __repr__
#@+node:ekr.20140526082700.17394: ** class TypeInferrer
class TypeInferrer (AstFullTraverser):
    
    '''A class to infer the types of objects.'''
    
    # def __init__ (self):
        # AstFullTraverser.__init__(self)

    def __call__(self,node):
        return self.run(node)
    
    #@+others
    #@+node:ekr.20140526082700.17395: *3* ti.clean (*revise*)
    def clean (self,aList):
        
        '''Return sorted(aList) with all duplicates removed.'''
        
        if 1:
            return aList or []
        else:
            ti = self
            if 1:
                # Good for debugging and traces.
                result = []
                for z in aList:
                    if z not in result:
                        result.append(z)
                
                # An excellent check.
                assert len(result) == len(list(set(aList))),aList
            else:
                result = list(set(aList))
           
            # Strip out inference errors if there are real results.
            result2 = ti.ignore_failures(result)
            if result2:
                ti.stats.n_clean_success += 1
                return sorted(result2)
            else:
                ti.stats.n_clean_fail += 1
                return sorted(result)
    #@+node:ekr.20140526082700.17396: *3* ti.format
    def format(self,node):
        
        u = self.u
        return '%s%s' % (
            ' '*u.compute_node_level(node),
            u.first_line(u.format(node)))
    #@+node:ekr.20140526082700.17397: *3* ti.init
    def init(self):

        self.stats = Stats()
        self.u = Utils()
        
        # Local stats
        self.n_nodes = 0
        
        # Detecting circular inferences
        self.call_stack = [] # Detects recursive calls
        self.assign_stack = [] # Detects circular assignments.

        # Create singleton instances of simple types.
        self.bool_type = Bool_Type()
        self.builtin_type = Builtin_Type()
        self.bytes_type = Bytes_Type()
        self.float_type = Float_Type()
        self.int_type = Int_Type()
        self.none_type = None_Type()
        self.string_type = String_Type()

        # Create the builtin type dict.
        self.builtin_type_dict = {
            'eval': [self.none_type],
            'id':   [self.int_type],
            'len':  [self.int_type],
            'ord':  [self.int_type],
            # list,tuple...
            # close,open,sort,sorted,super...
        }
    #@+node:ekr.20140526082700.17398: *3* ti.run (entry point)
    def run (self,root):
        
        self.init()
        self.visit(root)
    #@+node:ekr.20140526082700.17399: *3* ti.type helpers
    def has_failed(self,t1,t2=[],t3=[]):
        
        return any([isinstance(z,Inference_Failure) for z in t1+t2+t3])
        
    def is_circular(self,t1,t2=[],t3=[]):
        
        return any([isinstance(z,Circular_Assignment) for z in t1+t2+t3])
        
    def is_recursive(self,t1,t2=[],t3=[]):
        
        return any([isinstance(z,Recursive_Inference) for z in t1+t2+t3])
        
    def ignore_failures(self,t1,t2=[],t3=[]):
        
        return [z for z in t1+t2+t3 if not isinstance(z,Inference_Failure)]
        
    def ignore_unknowns(self,t1,t2=[],t3=[]):
        
        return [z for z in t1+t2+t3 if not isinstance(z,(Unknown_Type,Unknown_Arg_Type))]
        
    def merge_failures(self,t1,t2=[],t3=[]):

        aList = [z for z in t1+t2+t3 if isinstance(z,Inference_Failure)]
        if len(aList) > 1:
            # Prefer the most specific reason for failure.
            aList = [z for z in aList if not isinstance(z,Unknown_Type)]
        return aList
    #@+node:ekr.20140526082700.17400: *3* ti.visit
    def visit(self,node):

        '''Visit a single node.  Callers are responsible for visiting children.'''

        # This assert is redundant.
        # assert isinstance(node,ast.AST),node.__class__.__name__
        method = getattr(self,'do_' + node.__class__.__name__)
        self.n_nodes += 1
        return method(node)
    #@+node:ekr.20140526082700.17401: *3* ti.visitors
    #@+node:ekr.20140526082700.17402: *4* ti.expressions
    #@+node:ekr.20140526082700.17403: *5* ti.Attribute & check_attr (check super classes for attributes)
    # Attribute(expr value, identifier attr, expr_context ctx)

    def do_Attribute (self,node):

        ti = self
        trace = False and not g.app.runningAllUnitTests
        
        # g.trace(ti.format(node),node.value,node.attr)
        t = ti.visit(node.value) or [] ###
        t = ti.clean(t)
        t = ti.merge_failures(t)
        tag = '%s.%s' % (t,node.attr) # node.attr is always a string.
        if t:
            if len(t) == 1:
                ti.stats.n_not_fuzzy += 1
                t1 = t[0]
                if ti.kind(t1) == 'Class_Type':
                    aList = t1.cx.ivars_dict.get(node.attr)
                    aList = ti.clean(aList) if aList else []
                    if aList:
                        t = []
                        for node2 in aList:
                            t.extend(ti.visit(node2))
                        t = ti.clean(t)
                        ti.set_cache(node,t,tag='ti.Attribute')
                        ti.stats.n_attr_success += 1
                        if trace and trace_found:
                            g.trace('ivar found: %s -> %s' % (tag,t))
                    elif t1.cx.bases:
                        if trace_errors: g.trace('bases',
                            ti.format(node),ti.format(t1.cx.bases))
                        ### Must check super classes.
                        t = [Unknown_Type(node)]
                    else:
                        u.error('%20s has no %s member' % (ti.format(node),t1.cx.name))
                        t = [Unknown_Type(node)]
                else:
                    ti.stats.n_attr_fail += 1
                    if trace and trace_errors:
                        g.trace('fail',t,ti.format(node))
                    t = [Unknown_Type(node)]
            else:
                ti.stats.n_fuzzy += 1
                if trace and trace_fuzzy: g.trace('fuzzy',t,ti.format(node))
        else:
            if trace and trace_errors: g.trace('fail',t,ti.format(node))
            t = [Unknown_Type(node)]
        # ti.check_attr(node) # Does nothing
        return t
    #@+node:ekr.20140526082700.17404: *6* ti.check_attr
    def check_attr(self,node):
        
        ti = self
        trace = False and not g.app.runningAllUnitTests
        
        return ### Now done in ti.Attribute

        # assert ti.kind(node) == 'Attribute'
        # value = node.value
        # # node.attr is always a string.
        
        # if ti.kind(value) == 'Name':
            # # The ssa pass has computed the ivars dict.
            # # There is no need to examine value.ctx.
            # name = value.id
            # name_e = value.e
            # name_cx = name_e.cx
            # name_class_cx = name_cx.class_context
            # if name == 'self':
                # if name_class_cx:
                    # if node.attr in name_class_cx.ivars_dict:
                        # if trace: g.trace('OK: %s.%s' % (
                            # name_class_cx.name,node.attr))
                    # else:
                        # ti.error('%s has no %s member' % (
                            # name_class_cx.name,node.attr))
                # else:
                    # ti.error('%s is not a method of any class' % (
                        # name)) ####
            # else:
                # ### To do: handle any id whose inferred type is a class or instance.
                # if trace:
                    # g.trace('** not checked: %s' % (name))
                    # g.trace(ti.u.dump_ast(value))
    #@+node:ekr.20140526082700.17405: *5* ti.BinOp & helper
    def do_BinOp (self,node):

        ti = self
        trace = True and not g.app.runningAllUnitTests
        trace_infer = False ; trace_fail = False
        lt = ti.visit(node.left) or []
        rt = ti.visit(node.right) or []
        lt = ti.clean(lt)
        rt = ti.clean(rt)
        op_kind = ti.kind(node.op)
        num_types = ([ti.float_type],[ti.int_type])
        list_type = [List_Type(None)]
        if rt in num_types and lt in num_types:
            if rt == [ti.float_type] or lt == [ti.float_type]:
                t = [ti.float_type]
            else:
                t = [ti.int_type]
        elif rt == list_type and lt == list_type and op_kind == 'Add':
            t = list_type
        elif op_kind == 'Add' and rt == [ti.string_type] and lt == [ti.string_type]:
            t = [ti.string_type]
        elif op_kind == 'Mult' and rt == [ti.string_type] and lt == [ti.string_type]:
            g.trace('*** User error: string mult')
            t = [Unknown_Type(node)]
        elif op_kind == 'Mult' and (
            (lt==[ti.string_type] and rt==[ti.int_type]) or
            (lt==[ti.int_type] and rt==[ti.string_type])
        ):
            t = [ti.string_type]
        elif op_kind == 'Mod' and lt == [ti.string_type]:
            t = [ti.string_type] # (string % anything) is a string.
        else:
            ti.stats.n_binop_fail += 1
            if trace and trace_fail:
                if 1:
                    s = '%r %s %r' % (lt,op_kind,rt)
                    g.trace('  fail: %30s %s' % (s,ti.format(node)))
                else:
                    g.trace('  fail:',lt,op_kind,rt,ti.format(node))
            t = [Inference_Error(node)] ### Should merge types!
        if trace and trace_infer: g.trace(ti.format(node),'->',t)
        return t
    #@+node:ekr.20140526082700.17406: *5* ti.BoolOp
    def do_BoolOp(self,node):

        ti = self    
        return [ti.bool_type]
    #@+node:ekr.20140526082700.17407: *5* ti.Call & helpers
    # Call(expr func, expr* args, keyword* keywords, expr? starargs, expr? kwargs)
    #   Note: node.starargs and node.kwargs are given only if assigned explicitly.

    def do_Call (self,node):
        '''
        Infer the value of a function called with a particular set of arguments.
        '''
        ti = self
        trace = False and not g.app.runningAllUnitTests
        trace_builtins = True
        trace_errors = True ; trace_returns = False

        kind = ti.kind(node)
        func_name = ti.find_function_call(node)
        
        if trace: g.trace('1:entry:',func_name) # ,before='\n',
        
        # Special case builtins.
        t = ti.builtin_type_dict.get(func_name,[])
        if t:
            if trace and trace_builtins: g.trace(func_name,t)
            return t
            
        # Find the def or ctor to be evaluated.
        e = ti.find_call_e(node.func)
        if not (e and e.node):
            # find_call_e has given the warning.
            t = [Unknown_Type(node)]
            s = '%s(**no e**)' % (func_name)
            if trace and trace_errors: g.trace('%17s -> %s' % (s,t))
            return t

        # Special case classes.  More work is needed.
        if ti.kind(e.node) == 'ClassDef':
            # Return a type representing an instance of the class
            # whose ctor is evaluated in the present context.
            args,t = ti.class_instance(e)
            if trace and trace_returns:
                s = '%s(%s)' % (func_name,args)
                g.trace('%17s -> %s' % (s,t))
            return t

        # Infer the specific arguments and gather them in args list.
        # Each element of the args list may have multiple types.
        assert ti.kind(e.node) == 'FunctionDef'
        args = ti.infer_actual_args(e,node)
            
        # Infer the function for the cross-product the args list.
        # In the cross product, each argument has exactly one type.
        ti.stats.n_ti_calls += 1
        recursive_args,t = [],[]
        t2 = ti.infer_def(node,rescan_flag=False) ### specific_args,e,node,)
        if ti.is_recursive(t2):
            recursive_args.append(t2)
        t.extend(t2)

        if True and recursive_args:
            if trace: g.trace('===== rerunning inference =====',t)
            for t2 in recursive_args:
                t3 = ti.infer_def(node,rescan_flag=True) ### specific_args,e,node,rescan_flag=True)
                t.extend(t3)
            
        if ti.has_failed(t):
            t = ti.merge_failures(t)
            # t = ti.ignore_failures(t)
        else:
            t = ti.clean(t)
        if trace and trace_returns:
            s = '3:return %s(%s)' % (func_name,args)
            g.trace('%17s -> %s' % (s,t))
        return t
    #@+node:ekr.20140526082700.17408: *6* ti.class_instance
    def class_instance (self,e):
        
        '''
        Return a type representing an instance of the class
        whose ctor is evaluated in the present context.
        '''
        
        ti = self
        trace = True and not g.app.runningAllUnitTests
        cx = e.self_context
        
        # Step 1: find the ctor if it exists.
        d = cx.st.d
        ctor = d.get('__init__')

        # node2 = node.value
        # name = node2.id
        # attr = node.attr
        # e = getattr(node2,'e',None)
        # if trace: g.trace(kind,v_kind,name,attr)
        # # g.trace('e',e)
        # t = ti.get_cache(e)
        # # g.trace('cache',t)
        # if len(t) == 1:
            # t = t[0]
            # e_value = t.node.e
            # # g.trace('* e_value',e_value)
            # # g.trace('e_value.self_context',e_value.self_context)
            # e = e_value.self_context.st.d.get(node.attr)
            # if trace: g.trace('** e_value.self_context.st.d.get(%s)' % (attr),e)
            # # g.trace('e_value.self_context.st.d', e_value.self_context.st.d)
            # # g.trace('e.node',e.node)
            
        args = [] ### To do
        t = [Class_Type(cx)]
        # ti.set_cache(e,t,tag='class name')
        return args,t
    #@+node:ekr.20140526082700.17409: *6* ti.find_call_e
    def find_call_e (self,node):
        
        '''Find the symbol table entry for node, an ast.Call node.'''
        
        ti = self
        trace = False and not g.app.runningAllUnitTests
        trace_errors = False; trace_fuzzy = True ; trace_return = False
        kind = ti.kind(node)
        e = None # Default.
        if kind == 'Name':
            # if trace: g.trace(kind,node.id)
            e = getattr(node,'e',None)
        else:
            t = ti.visit(node) or []
            if len(t) == 1:
                ti.stats.n_not_fuzzy += 1
                t = t[0]
                if ti.kind(t) == 'Class_Type':
                    d = t.cx.st.d
                    if ti.kind(node) == 'Attribute':
                        name = node.attr
                    elif ti.kind(node) == 'Call':
                        name = node.func
                    else:
                        name = None
                    if name:
                        e = d.get(name)
                    else:
                        e = None
                else:
                    if trace and trace_errors:
                        g.trace('not a class type: %s %s' % (ti.kind(t),ti.format(node)))
            elif len(t) > 1:
                if trace and trace_fuzzy: g.trace('fuzzy',t,ti.format(node))
                ti.stats.n_fuzzy += 1
                e = None
            
        # elif kind == 'Attribute':
            # v_kind = ti.kind(node.value)
            # if v_kind == 'Name':
                # node2 = node.value
                # name = node2.id
                # attr = node.attr
                # e = getattr(node2,'e',None)
                # # if trace: g.trace(kind,v_kind,name,attr)
                # t = ti.get_cache(e)
                # if len(t) == 1:
                    # t = t[0]
                    # if ti.kind(t) == 'Class_Type':
                        # d = t.cx.st.d
                        # e = d.get(node.attr)
                    # else:
                        # pass ### To do
                # elif t:
                    # pass
                # else:
                    # t = [Unknown_Type(node)]
            # elif v_kind == 'Attribute':
                # node2 = node.value
                # g.trace('*****',kind,v_kind,ti.format(node.value))
                # e = ti.find_call_e(node2)
            # else:
                # g.trace('not ready yet',kind,v_kind)
                # e = None
        # elif kind in ('Call','Subscript'):
            # g.trace(kind)
            # e = None
        # else:
            # g.trace('===== oops:',kind)
            # e = None
            
        # if e:
            # assert isinstance(e,SymbolTableEntry),ti.kind(e)
            # ti.stats.n_find_call_e_success += 1
        # else:
            # # Can happen with methods,Lambda.
            # ti.stats.n_find_call_e_fail += 1
            # if trace and trace_errors: g.trace('**** no e!',kind,ti.format(node),
                # before='\n')

        # if e and not e.node:
            # if trace and trace_errors: g.trace(
                # 'undefined e: %s' % (e),before='\n')

        # if trace and trace_return: g.trace(
            # kind,'e:',e,ti.format(node))
        # return e
    #@+node:ekr.20140526082700.17410: *6* ti.infer_actual_args
    # Call(expr func, expr* args, keyword* keywords, expr? starargs, expr? kwargs)
    #   keyword = (identifier arg, expr value) # keyword arguments supplied to call

    # FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list)
    #   arguments = (expr* args, identifier? vararg, identifier? kwarg, expr* defaults)

    def infer_actual_args (self,e,node):
        
        '''Return a list of types for all actual args, in the order defined in
        by the entire formal argument list.'''
        
        ti = self
        trace = False and not g.app.runningAllUnitTests
        trace_args = False
        assert ti.kind(node)=='Call'
        cx = e.self_context
        # Formals...
        formals  = cx.node.args or []
        defaults = cx.node.args.defaults or [] # A list of expressions
        vararg   = cx.node.args.vararg
        kwarg    = cx.node.args.kwarg
        # Actuals...
        actuals  = node.args or [] # A list of expressions.
        keywords = node.keywords or [] # A list of (identifier,expression) pairs.
        starargs = node.starargs
        kwargs   = node.kwargs
        assert ti.kind(formals)=='arguments'
        assert ti.kind(formals.args)=='list'
        
        formal_names = [z.id for z in formals.args]
            # The names of *all* the formal arguments, include those with defauls.
            # Doesw not include vararg and kwarg.
           
        # Append unnamed actual args.
        # These could be either non-keyword arguments or keyword arguments.
        args = [ti.visit(z) for z in actuals]
        bound_names = formal_names[:len(actuals)]
        
        if trace and trace_args:
            g.trace('formal names',formal_names)
            g.trace('   arg names',bound_names)
            g.trace('    starargs',starargs and ti.format(starargs))
            g.trace('    keywargs',kwargs   and ti.format(kwargs))
            # formal_defaults = [ti.visit(z) for z in defaults]
                # # The types of each default.
            # g.trace('formal default types',formal_defaults)
            # g.trace('unnamed actuals',ti.format(actuals))
        
        # Add keyword args in the call, in the order they appear in the formal list.
        # These could be either non-keyword arguments or keyword arguments.
        keywargs_d = {}
        keywords_d = {}
        for keyword in keywords:
            name = keyword.arg
            t = ti.visit(keyword.value)
            value = ti.format(keyword.value)
            keywords_d[name] = (value,t)

        for name in formal_names[len(actuals):]:
            data = keywords_d.get(name)
            if data:
                value,t = data
                if trace and trace_args: g.trace('set keyword',name,value,t)
                args.append(t)
                bound_names.append(name)
            # else: keywargs_d[name] = None ### ???

        # Finally, add any defaults from the formal args.
        n_plain = len(formal_names) - len(defaults)
        defaults_dict = {}
        for i,expr in enumerate(defaults):
            name = formal_names[n_plain+i]
            value = ti.format(expr)
            t = ti.visit(expr)
            defaults_dict[name] = (value,t)

        for name in formal_names:
            if name not in bound_names:
                data = defaults_dict.get(name)
                t = None # default
                if data:
                    value,t = data
                    if trace and trace_args: g.trace('set default',name,value,t)
                elif name == 'self':
                    def_cx = e.self_context
                    class_cx = def_cx and def_cx.class_context
                    if class_cx:
                        t = [Class_Type(class_cx)]
                if t is None:
                    t = [Unknown_Arg_Type(node)]
                    ti.error('Unbound actual argument: %s' % (name))
                args.append(t)
                bound_names.append(name)
                
        ### Why should this be true???
        # assert sorted(formal_names) == sorted(bound_names)

        if None in args:
            g.trace('***** opps node.args: %s, args: %s' % (node.args,args))
            args = [z for z in args if z is not None]
            
        if trace: g.trace('result',args)
        return args
    #@+node:ekr.20140526082700.17411: *6* ti.infer_def & helpers (sets call cache)
    def infer_def(self,node,rescan_flag):
        
        '''Infer everything possible from a def D called with specific args:
        
        1. Bind the specific args to the formal parameters in D.
        2. Infer all assignments in D.
        3. Infer all outer expression in D.
        4. Infer all return statements in D.
        '''
        
        ti = self
        trace = False and not g.app.runningAllUnitTests
        return ###

        # t0 = ti.get_call_cache(e,hash_) or []
        # if hash_ in ti.call_stack and not rescan_flag:
            # # A recursive call: always add an Recursive_Instance marker.
            # if trace:g.trace('A recursive','rescan',rescan_flag,hash_,'->',t0)
            # ti.stats.n_recursive_calls += 1
            # t = [Recursive_Inference(node)]
        # else:
            # if trace: g.trace('A',hash_,'->',t0)
            # ti.call_stack.append(hash_)
            # try:
                # cx = e.self_context
                # # data = ti.switch_context(e,hash_,node)
                # ti.bind_args(specific_args,cx,e,node)
                # ti.infer_assignments(cx,e)
                # ti.infer_outer_expressions(cx,node)
                # t = ti.infer_return_statements(cx,e)
                # ti.restore_context(data)
            # finally:
                # hash2 = ti.call_stack.pop()
                # assert hash2 == hash_
        # # Merge the result and reset the cache.
        # t.extend(t0)
        # t = ti.clean(t)
        # if trace: g.trace('B',hash_,'->',t)
        # return t
    #@+node:ekr.20140526082700.17412: *7* ti.bind_args (ti.infer_def helper) (To do: handle self)
    # Call(expr func, expr* args, keyword* keywords, expr? starargs, expr? kwargs)
    #   keyword = (identifier arg, expr value) # keyword arguments supplied to call

    # FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list)
    #   arguments = (expr* args, identifier? vararg, identifier? kwarg, expr* defaults)

    def bind_args (self,types,cx,e,node):
        
        ti = self
        trace = False and not g.app.runningAllUnitTests
        assert ti.kind(node)=='Call'
        assert isinstance(node.args,list),node
        formals = cx.node.args or []
        assert ti.kind(formals)=='arguments'
        assert ti.kind(formals.args)=='list'
        formal_names = [z.id for z in formals.args]
            # The names of *all* the formal arguments, include those with defauls.
            
        if len(formal_names) != len(types):
            # g.trace('**** oops: formal_names: %s types: %s' % (formal_names,types))
            return

        def_cx = e.self_context
        d = def_cx.st.d
        for i,name in enumerate(formal_names):
            pass ### 
            ### Handle self here.
            # t = types[i]
            # e2 = d.get(name)
            # if e2:
                # if trace: g.trace(e2,t) # g.trace(e2.name,t)
                # ti.set_cache(e2,[t],tag='bindargs:%s'%(name))
            # else:
                # g.trace('**** oops: no e2',name,d)
    #@+node:ekr.20140526082700.17413: *7* ti.infer_assignments
    def infer_assignments(self,cx,e):
        
        '''Infer all the assignments in the function context.'''

        ti = self
        trace = False and not g.app.runningAllUnitTests
        for a in cx.assignments_list:
            if ti.kind(a) == 'Assign': # ignore AugAssign.
                pass ####

                # t2 = ti.get_cache(a)
                # if t2:
                    # ti.stats.n_assign_hits += 1
                    # if trace: g.trace('hit!',t2)
                # else:
                    # t2 = ti.visit(a)
                    # t3 = ti.ignore_failures(t2)
                    # if t3:
                        # ti.stats.n_assign_misses += 1
                        # # g.trace('***** set cache',t2)
                        # ti.set_cache(a,t2,tag='infer_assns')
                        # if trace: g.trace('miss',t2)
                    # else:
                        # ti.stats.n_assign_fails += 1
                        # if trace: g.trace('fail',t2)
                   
                       
        return None # This value is never used.
    #@+node:ekr.20140526082700.17414: *7* ti.infer_outer_expressions
    def infer_outer_expressions(self,cx,node):
        
        '''Infer all outer expressions in the function context.'''

        ti = self
        trace = False and not g.app.runningAllUnitTests
        for exp in cx.expressions_list:
            if trace: g.trace(ti.format(exp))
            ti.stats.n_outer_expr_misses += 1
            t = ti.visit(exp)

        return None # This value is never used.
    #@+node:ekr.20140526082700.17415: *7* ti.infer_return_statements
    def infer_return_statements(self,cx,e):
        
        '''Infer all return_statements in the function context.'''
        
        ti = self
        trace = False and not g.app.runningAllUnitTests
        t = []
        for r in cx.returns_list:
            t2 = ti.visit(r)
            if trace: g.trace('miss',t2)
            t.extend(t2)
        if ti.has_failed(t):
            t = ti.merge_failures(t)
        else:
            t = ti.clean(t)
        return t
    #@+node:ekr.20140526082700.17416: *5* ti.Compare
    # Compare(expr left, cmpop* ops, expr* comparators)

    def do_Compare(self,node):
        
        ti = self
        ti.visit(node.left)
        for z in node.comparators:
            ti.visit(z)
        return [ti.bool_type]
    #@+node:ekr.20140526082700.17417: *5* ti.comprehension
    def do_comprehension(self,node):

        ti = self
        ti.visit(node.target) # A name.
        ti.visit(node.iter) # An attribute.
        return [List_Type(node)]
    #@+node:ekr.20140526082700.17418: *5* ti.Expr
    # Expr(expr value)

    def do_Expr(self,node):
        
        ti = self
        t = ti.visit(node.value)
        return t
    #@+node:ekr.20140526082700.17419: *5* ti.GeneratorExp
    def do_GeneratorExp (self,node):

        ti = self
        trace = False and not g.app.runningAllUnitTests
        junk = ti.visit(node.elt)
        t = []
        for node2 in node.generators:
            t2 = ti.visit(node2)
            t.extend(t2)
        if ti.has_failed(t):
            t = ti.merge_failures(t)
            if trace: g.trace('failed inference',ti.format(node),t)
        else:
            t = ti.clean(t)
        return t
    #@+node:ekr.20140526082700.17420: *5* ti.IfExp
    # The ternary operator
    # IfExp(expr test, expr body, expr orelse)

    def do_IfExp(self,node):
        
        ti = self    
        junk = ti.visit(node.test)
        t = ti.visit(node.body)
        t.extend(ti.visit(node.orelse))
        if ti.has_failed(t):
            t = ti.merge_failures(t)
        else:
            t = ti.clean(t)
        return t
    #@+node:ekr.20140526082700.17421: *5* ti.Index
    def do_Index(self,node):

        ti = self    
        return ti.visit(node.value)
    #@+node:ekr.20140526082700.17422: *5* ti.Lambda
    def do_Lambda (self,node):
        
        ti = self
        return ti.visit(node.body)
    #@+node:ekr.20140526082700.17423: *5* ti.ListComp
    def do_ListComp(self,node):
        
        ti = self
        # g.trace(node.elt,node.generators)
        junk = ti.visit(node.elt)
        t = []
        for node2 in node.generators:
            t.extend(ti.visit(node2))
        if ti.has_failed(t):
            t = ti.merge_failures(t)
        else:
            t = ti.clean(t)
        return t
    #@+node:ekr.20140526082700.17424: *5* ti.Name (**rewrite)
    def do_Name(self,node):
        
        ti = self ; u = ti.u
        trace = True and not g.app.runningAllUnitTests
        trace_infer = False ; trace_fail = False
        trace_self = False
        ctx_kind = ti.kind(node.ctx)
        name = node.id
        trace = trace and name == 'i'
        
        # # Reaching sets are useful only for Load attributes.
        # if ctx_kind not in ('Load','Param'):
            # # if trace: g.trace('skipping %s' % ctx_kind)
            # return []

        # ### ast.Name nodes for class base names have no 'e' attr.
        # if not hasattr(node,'e'):
            # if trace: g.trace('no e',node)
            # return []

        if name == 'self':
            # reach = getattr(node,'reach',[])
            # if reach: g.trace('**** assignment to self')
            cx = node.stc_context ### should be class context.
            if cx:
                if trace and trace_self: g.trace('found self',cx)
                t = [Class_Type(cx)]
            else:
                g.trace('**** oops: no class context for self',ti.format(node))
                t = [Unknown_Type(node)]
        else:
            reach = getattr(node,'reach',[])
            t = []
            for node2 in reach:
                # The reaching sets are the RHS of assignments.
                t = [Unknown_Type(node)]
                t2 = ti.visit(node2)
                if isinstance(t2,(list,tuple)):
                    t.extend(t2)
                else:
                    g.trace('**oops:',t2,ti.format(node2))
            if ti.has_failed(t):
                t = ti.merge_failures(t)
            else:
                t = ti.clean(t)

        if trace and trace_infer and t:
            g.trace('infer',t,u.format(node))
        if trace and trace_fail and not t:
            g.trace('fail ',name,ctx_kind,'reach:',
                ['%s:%s' % (id(z),u.format(z)) for z in reach])
        return t
    #@+node:ekr.20140526082700.17425: *5* ti.Slice
    def do_Slice(self,node):
        
        ti = self
        if node.upper: junk = ti.visit(node.upper)
        if node.lower: junk = ti.visit(node.lower)
        if node.step:  junk = ti.visit(node.step)
        return [ti.int_type] ### ???
    #@+node:ekr.20140526082700.17426: *5* ti.Subscript (to do)
    def do_Subscript(self,node):

        ti = self
        trace = False and not g.app.runningAllUnitTests
        t1 = ti.visit(node.value)
        t2 = ti.visit(node.slice)
        if t1 and trace: g.trace(t1,t2,ti.format(node))
        return t1 ### ?
    #@+node:ekr.20140526082700.17427: *5* ti.UnaryOp
    def do_UnaryOp(self,node):
        
        ti = self
        trace = True and not g.app.runningAllUnitTests
        t = ti.visit(node.operand) or []
        t = ti.clean(t)
        op_kind = ti.kind(node.op)
        if op_kind == 'Not':
            t = [self.bool_type]
        elif t == [self.int_type] or t == [self.float_type]:
            pass # All operators are valid.
        else:
            ti.stats.n_unop_fail += 1
            if trace: g.trace(' fail:',op_kind,t,ti.format(node))
            t = [Unknown_Type(node)]
        return t
    #@+node:ekr.20140526082700.17428: *4* ti.primitive Types
    #@+node:ekr.20140526082700.17429: *5* ti.Builtin
    def do_Builtin(self,node):

        ti = self
        return [ti.builtin_type]
    #@+node:ekr.20140526082700.17430: *5* ti.Bytes
    def do_Bytes(self,node):

        ti = self
        return [ti.bytes_type]
    #@+node:ekr.20140526082700.17431: *5* ti.Dict
    # Dict(expr* keys, expr* values)

    def do_Dict(self,node):
        
        ti = self
        for z in node.keys:
            ti.visit(z)
        for z in node.values:
            ti.visit(z)
        return [Dict_Type(node)]
            ### More specific type.
    #@+node:ekr.20140526082700.17432: *5* ti.List
    # List(expr* elts, expr_context ctx) 

    def do_List(self,node):
        
        ti = self
        for z in node.elts:
            ti.visit(z)
        # ti.visit(node.ctx)
        return [List_Type(node)]
    #@+node:ekr.20140526082700.17433: *5* ti.Num
    def do_Num(self,node):
        
        ti = self
        t_num = Num_Type(node.n.__class__)
        # g.trace(ti.format(node),'->',t_num)
        return [t_num]
    #@+node:ekr.20140526082700.17434: *5* ti.Str
    def do_Str(self,node):
        
        '''This represents a string constant.'''

        ti = self
        return [ti.string_type]
    #@+node:ekr.20140526082700.17435: *5* ti.Tuple
    # Tuple(expr* elts, expr_context ctx)

    def do_Tuple(self,node):
        
        ti = self
        for z in node.elts:
            ti.visit(z)
        # ti.visit(node.ctx)
        return [Tuple_Type(node)]
    #@+node:ekr.20140526082700.17436: *4* ti.statements
    #@+node:ekr.20140526082700.17437: *5* ti.arguments
    # arguments = (expr* args, identifier? vararg, identifier? kwarg, expr* defaults)

    def do_arguments (self,node):
        
        '''Bind formal arguments to actual arguments.'''
        
        assert False # All the work is done in ti.Call and its helpers.
    #@+node:ekr.20140526082700.17438: *5* ti.Assign (**rewrite)
    def do_Assign(self,node):

        ti = self
        trace = False and not g.app.runningAllUnitTests
        t_val = ti.visit(node.value)
        t = []
        for z in node.targets:
            t.append(ti.visit(z))
        t = ti.clean(t)
        return t

        # if data in ti.assign_stack:
            # t = [Circular_Assignment(node)]
            # ti.stats.n_circular_assignments += 1
        # else:
            # ti.assign_stack.append(data)
            # try:
                # t = ti.visit(node.value)
                # if trace: g.trace(t)
            # finally:
                # data2 = ti.assign_stack.pop()
                # assert data == data2
            
        # for target in node.targets:
            # kind = ti.kind(target)
            # if kind == 'Name':
                # t0 = ti.get_cache(target.e) or []
                # t.extend(t0)
                # ti.set_cache(target.e,t,tag='Name:target.e')
                # if trace: g.trace('infer: %10s -> %s' % (
                    # ti.format(target),t),before='\n')
            # else:
                # ### What to do about this?
                # if trace: g.trace('(ti) not a Name: %s' % (
                    # ti.format(target)),before='\n')
                    
        # # Update the cache immediately.
        # t0 = ti.get_cache(node) or []
        # t.extend(t0)
        # t = ti.clean(t)
        # ti.set_cache(node,t,tag='ti.Assign')
        # return t
    #@+node:ekr.20140526082700.17439: *5* ti.ClassDef (could be default)
    def do_ClassDef(self,node):
        
        ti = self
        for z in node.body:
            self.visit(z)
    #@+node:ekr.20140526082700.17440: *5* ti.For
    # For(expr target, expr iter, stmt* body, stmt* orelse)

    def do_For (self,tree):

        ti = self
        ### what if target conflicts with an assignment??
        ti.visit(tree.target)
        ti.visit(tree.iter)
        for z in tree.body:
            ti.visit(z)
        for z in tree.orelse:
            ti.visit(z)
    #@+node:ekr.20140526082700.17441: *5* ti.FunctionDef & helpers (**rewrite)
    # FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list)

    def do_FunctionDef (self,node):
        
        '''Infer this function or method with 'unknown' as the value of all args.
        This gets inference going.
        '''
        
        ti = self
        trace = False and not g.app.runningAllUnitTests
        ti.infer_outer_def(node)
        
        # # Set up function call, with 'unknown' for all args.
        # e = node.e
        # specific_args = [Unknown_Arg_Type(node)] * ti.count_full_args(node)
        # hash_ = ti.cache_hash(specific_args,e)
        # t = ti.get_call_cache(e,hash_)
        # if trace:
            # g.trace('%s %12s -> %s' % ('miss' if t is None else 'hit!',
                # node.name,specific_args))
        # if t is None:
            # t = ti.infer_outer_def(specific_args,hash_,node)
        # return t
    #@+node:ekr.20140526082700.17442: *6* ti.count_full_args
    # FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list)
    #   arguments = (expr* args, identifier? vararg, identifier? kwarg, expr* defaults)

    def count_full_args (self,node):
        
        '''Return the number of arguments in a call to the function/def defined
        by node, an ast.FunctionDef node.'''
        
        ti = self
        trace = False and not g.app.runningAllUnitTests
        assert ti.kind(node)=='FunctionDef'    
        args = node.args
        if trace: g.trace('args: %s vararg: %s kwarg: %s' % (
            [z.id for z in args.args],args.vararg,args.kwarg))
        n = len(args.args)
        if args.vararg: n += 1
        if args.kwarg:  n += 1
        return n
    #@+node:ekr.20140526082700.17443: *6* ti.infer_outer_def & helper
    def infer_outer_def(self,node):
        
        '''Infer everything possible from a def D called with specific args:
        
        1. Bind the args to the formal parameters in D.
        2. Infer all assignments in D.
        3. Infer all outer expression in D.
        4. Infer all return statements in D.
        '''
        
        return []

        # ti = self
        # # trace = True and not g.app.runningAllUnitTests
        # assert ti.kind(node)=='FunctionDef',node
        # e = node.e
        # assert hasattr(e,'call_cache')
        # cx = e.self_context
        # ### data = ti.switch_context(e,hash_,node)
        # ti.bind_outer_args(node)
        # ti.infer_assignments(cx,e)
        # ti.infer_outer_expressions(cx,node)
        # t = ti.infer_return_statements(cx,e)
        # ### ti.set_call_cache(e,hash_,t,tag='infer_def')
        # ### ti.restore_context(data)
        # return t
    #@+node:ekr.20140526082700.17444: *7* ti_bind_outer_args (ti.infer_outer_def helper)
    # FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list)
    #   arguments = (expr* args, identifier? vararg, identifier? kwarg, expr* defaults)
    def bind_outer_args (self,node):
        
        '''Bind all all actual arguments except 'self' to "Unknown_Arg_Type".'''
        
        ti = self
        trace = False and not g.app.runningAllUnitTests
        assert ti.kind(node)=='FunctionDef'
        e = node.e
        def_cx = e.self_context
        args = node.args or []
        assert ti.kind(args)=='arguments',args
        assert ti.kind(args.args)=='list',args.args
        formal_names = [z.id if hasattr(z,'id') else '<tuple arg>' for z in args.args]
        if args.vararg: formal_names.append(args.vararg)
        if args.kwarg:  formal_names.append(args.kwarg)
        # if trace: g.trace(formal_names)
        d = def_cx.st.d
        for name in formal_names:
            if name == 'self':
                if def_cx:
                    t = [Class_Type(def_cx)]
                else:
                    t = [Unknown_Arg_Type(node)]
                e2 = e
            else:
                t = [Unknown_Arg_Type(node)]
                e2 = d.get(name)
            # if e2:
                # ti.set_cache(e2,t,tag='bind_outer_args:%s'%(name))
                # if trace: g.trace(name,t)
            # else:
                # if trace: g.trace('**** oops: no e2',name,d)
    #@+node:ekr.20140526082700.17445: *5* ti.Import (not used)
    # def do_Import(self,node):
        
        # pass
    #@+node:ekr.20140526082700.17446: *5* ti.ImportFrom (not used)
    # def do_ImportFrom(self,node):
        
        # pass
    #@+node:ekr.20140526082700.17447: *5* ti.Return & ti.Yield & helper
    def do_Return(self,node):
        return self.return_helper(node)
        
    def do_Yield(self,node):
        return self.return_helper(node)
    #@+node:ekr.20140526082700.17448: *6* ti.return_helper
    def return_helper(self,node):

        ti = self
        trace = False and not g.app.runningAllUnitTests
        e = ti.call_e
        assert e
        if node.value:
            t = ti.visit(node.value)
            if ti.has_failed(t):
                ti.stats.n_return_fail += 1
                t = ti.ignore_unknowns(t)
            if t:
                ti.stats.n_return_success += 1
            else:
                ti.stats.n_return_fail += 1
                t = [] # Do **not** propagate a failure here!
        else:
            t = [ti.none_type]
        if trace: g.trace(t,ti.format(node))
        return t
    #@+node:ekr.20140526082700.17449: *5* ti.With
    def do_With (self,node):

        ti = self
        t = []
        for z in node.body:
            t.append(ti.visit(z))
        t = ti.clean(t)
        return t
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
    #@+node:ekr.20140526082700.17476: *4* u.p012
    def p012(self,files,project_name,report):
        '''Parse and run P1 and TypeInferrer on all files in a list of file names.'''
        u = self
        if report and not g.app.runningAllUnitTests:
            print(project_name)
        # Pass 0.
        t0 = time.time()
        d = dict([(fn,u.parse_file(fn)) for fn in files])
        p0_time = u.diff_time(t0)
        # Pass 1.
        t = time.time()
        p1 = P1()
        for fn in files:
            root = d.get(fn)
            p1(fn,root)
        p1_time = u.diff_time(t)
        # Pass 2.
        t = time.time()
        ti = TypeInferrer()
        for fn in files:
            ti(d.get(fn))
        p2_time = u.diff_time(t)
        tot_time = u.diff_time(t0)
        if report:
            u.p012_report(len(files),p0_time,p1_time,p2_time,tot_time)
        return d
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
    def p01s(self,s,report=True):
        
        '''Parse an input string.'''
        u = self
        t = time.time()
        node = ast.parse(s,filename='<string>',mode='exec')
        p0_time = u.diff_time(t)
        if report:
            u.p0_report(1,p0_time)
        return node
    #@+node:ekr.20140526082700.17481: *4* u.p01s
    def p01s(self,s,report=True):
        
        '''Parse and run P1 on an input string.'''
        u = self
        t0 = time.time()
        node = ast.parse(s,filename='<string>',mode='exec')
        p0_time = u.diff_time(t0)
        t = time.time()
        P1().run('<string>',node)
        p1_time = u.diff_time(t)
        tot_time = u.diff_time(t0)
        if report:
            u.p01_report(1,p0_time,p1_time,tot_time)
        return node
    #@+node:ekr.20140526082700.17482: *4* u.p012s
    def p012s(self,s,report=True):
        
        '''Parse and run P1 and TypeInferrer on an input string.'''
        u = self
        t0 = time.time()
        node = ast.parse(s,filename='<string>',mode='exec')
        p0_time = u.diff_time(t0)
        t = time.time()
        P1().run('<string>',node)
        p1_time = u.diff_time(t)
        t = time.time()
        TypeInferrer().run(node)
        p2_time = u.diff_time(t)
        tot_time = u.diff_time(t0)
        if report:
            u.p012_report(None,1,p0_time,p1_time,p2_time,tot_time)
        return node
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
        ###
        assert False
        for d in (self.builtins_d,self.special_methods_d):
            if key in d.keys():
                return d
        if trace:
            g.trace('** (ScopeBinder) no definition for %20s in %s' % (
                key,self.format(cx)))
        return None
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
        return ast.parse(s,filename=fn,mode='exec')

    def parse_string(self,fn,s):
        
        return ast.parse(s,filename=fn,mode='exec')
        
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
        f = g.fileLikeObject()
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
                fn = g.os_path_finalize_join(theDir,'..','plugins','qtGui.py')
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
                'baseEditCommandsClass',
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
                'leoFind','leoFrame','leoGui','leoIPython','leoImport',
                'leoLog','leoMenu','leoNodes','leoPlugins','leoRst',
                'leoTangle','leoTest','leoTree',
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
#@+node:ekr.20140526082700.17508: ** Generator classes
#@+node:ekr.20140526082700.17509: *3* .class NodeGenerator
# Slightly slower than NodePseudoGenerator, but generates no data.

class NodeGenerator:
    
    # def __init__(self):
        # pass
    
    # This "convenience" would be a big overhead!
    # def __call__(self,node):
        # for z in self.visit(node):
            # yield z
    
    #@+others
    #@+node:ekr.20140526082700.17510: *4* visit
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
    #@+node:ekr.20140526082700.17511: *4* fg.operators
    #@+node:ekr.20140526082700.17512: *5* fg.do-nothings
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
    #@+node:ekr.20140526082700.17513: *5* fg.arguments
    # arguments = (expr* args, identifier? vararg, identifier? kwarg, expr* defaults)

    def do_arguments(self,node):
        
        for z in node.args:
            for z2 in self.visit(z):
                yield z2
        for z in node.defaults:
            for z2 in self.visit(z):
                yield z2
    #@+node:ekr.20140526082700.17514: *5* fg.Attribute
    # Attribute(expr value, identifier attr, expr_context ctx)

    def do_Attribute(self,node):
        
        for z in self.visit(node.value):
            yield z
        # yield node.ctx
    #@+node:ekr.20140526082700.17515: *5* fg.BinOp
    # BinOp(expr left, operator op, expr right)

    def do_BinOp (self,node):
        
        for z in self.visit(node.left):
            yield z
        # yield node.op
        for z in self.visit(node.right):
            yield z
    #@+node:ekr.20140526082700.17516: *5* fg.BoolOp
    # BoolOp(boolop op, expr* values)

    def do_BoolOp (self,node):

        # yield node.op
        for z in node.values:
            for z2 in self.visit(z):
                yield z2
    #@+node:ekr.20140526082700.17517: *5* fg.Call
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
    #@+node:ekr.20140526082700.17518: *5* fg.Compare
    # Compare(expr left, cmpop* ops, expr* comparators)

    def do_Compare(self,node):
        
        for z in self.visit(node.left):
            yield z
        # for z in node ops:
            # yield z
        for z in node.comparators:
            for z2 in self.visit(z):
                yield z2
    #@+node:ekr.20140526082700.17519: *5* fg.comprehension
    # comprehension (expr target, expr iter, expr* ifs)

    def do_comprehension(self,node):

        for z in self.visit(node.target): # a Name.
            yield z
        for z in self.visit(node.iter): # An Attribute.
            yield z
        for z in node.ifs: ### Does not appear in AstFullTraverser!
            for z2 in self.visit(z):
                yield z2
    #@+node:ekr.20140526082700.17520: *5* fg.Dict
    # Dict(expr* keys, expr* values)

    def do_Dict(self,node):
        
        for z in node.keys:
            for z2 in self.visit(z):
                yield z2
        for z in node.values:
            for z2 in self.visit(z):
                yield z2
    #@+node:ekr.20140526082700.17521: *5* fg.Expr
    # Expr(expr value)

    def do_Expr(self,node):
        
        for z in self.visit(node.value):
            yield z
    #@+node:ekr.20140526082700.17522: *5* fg.Expression
    def do_Expression(self,node):
        
        '''An inner expression'''
        for z in self.visit(node.body):
            yield z
    #@+node:ekr.20140526082700.17523: *5* fg.ExtSlice
    # ExtSlice(slice* dims) 

    def do_ExtSlice (self,node):
        
        for z in node.dims:
            for z2 in self.visit(z):
                yield z2
    #@+node:ekr.20140526082700.17524: *5* fg.GeneratorExp
    # GeneratorExp(expr elt, comprehension* generators)

    def do_GeneratorExp(self,node):
        
        for z in self.visit(node.elt):
            yield z
        for z in node.generators:
            for z2 in self.visit(z):
                yield z2
    #@+node:ekr.20140526082700.17525: *5* fg.ifExp (ternary operator)
    # IfExp(expr test, expr body, expr orelse)

    def do_IfExp (self,node):

        for z in self.visit(node.body):
            yield z
        for z in self.visit(node.test):
            yield z
        for z in self.visit(node.orelse):
            yield z
    #@+node:ekr.20140526082700.17526: *5* fg.Index
    # Index(expr value)

    def do_Index (self,node):
        
        for z in self.visit(node.value):
            yield z
    #@+node:ekr.20140526082700.17527: *5* fg.keyword
    # keyword = (identifier arg, expr value)

    def do_keyword(self,node):

        # node.arg is a string.
        for z in self.visit(node.value):
            yield z
    #@+node:ekr.20140526082700.17528: *5* fg.Lambda
    # Lambda(arguments args, expr body)

    def do_Lambda(self,node):
        
        for z in self.visit(node.args):
            yield z
        for z in self.visit(node.body):
            yield z
    #@+node:ekr.20140526082700.17529: *5* fg.List & ListComp
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
    #@+node:ekr.20140526082700.17530: *5* fg.Name (revise)
    # Name(identifier id, expr_context ctx)

    def do_Name(self,node):
        # yield node.ctx
        raise StopIteration
    #@+node:ekr.20140526082700.17531: *5* fg.Repr
    # Python 2.x only
    # Repr(expr value)

    def do_Repr(self,node):

        for z in self.visit(node.value):
            yield z
    #@+node:ekr.20140526082700.17532: *5* fg.Slice
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
    #@+node:ekr.20140526082700.17533: *5* fg.Subscript
    # Subscript(expr value, slice slice, expr_context ctx)

    def do_Subscript(self,node):
        
        for z in self.visit(node.value):
            yield z
        for z in self.visit(node.slice):
            yield z
        # yield node.ctx
    #@+node:ekr.20140526082700.17534: *5* fg.Tuple
    # Tuple(expr* elts, expr_context ctx)

    def do_Tuple(self,node):
        
        for z in node.elts:
            for z2 in self.visit(z):
                yield z2
        # yield node.ctx
    #@+node:ekr.20140526082700.17535: *5* fg.UnaryOp
    # UnaryOp(unaryop op, expr operand)

    def do_UnaryOp (self,node):
        
        # for z in self.visit(node.op):
            # yield z
        for z in self.visit(node.operand):
            yield z
    #@+node:ekr.20140526082700.17536: *4* fg.statements
    #@+node:ekr.20140526082700.17537: *5* fg.alias
    # identifier name, identifier? asname)

    def do_alias (self,node):
        raise StopIteration
    #@+node:ekr.20140526082700.17538: *5* fg.Assert
    # Assert(expr test, expr? msg)

    def do_Assert(self,node):

        for z in self.visit(node.test):
            yield z
        if node.msg:
            for z in self.visit(node.msg):
                yield z

    #@+node:ekr.20140526082700.17539: *5* fg.Assign
    # Assign(expr* targets, expr value)

    def do_Assign(self,node):

        for z in node.targets:
            for z2 in self.visit(z):
                yield z2
        for z in self.visit(node.value):
            yield z
            
    #@+node:ekr.20140526082700.17540: *5* fg.AugAssign
    # AugAssign(expr target, operator op, expr value)

    def do_AugAssign(self,node):
        
        for z in self.visit(node.target):
            yield z
        # yield node.op
        for z in self.visit(node.value):
            yield z
    #@+node:ekr.20140526082700.17541: *5* fg.Break
    def do_Break(self,node):

        raise StopIteration

    #@+node:ekr.20140526082700.17542: *5* fg.ClassDef
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
    #@+node:ekr.20140526082700.17543: *5* fg.Continue
    def do_Continue(self,node):

        raise StopIteration

    #@+node:ekr.20140526082700.17544: *5* fg.Delete
    # Delete(expr* targets)

    def do_Delete(self,node):

        for z in node.targets:
            for z2 in self.visit(z):
                yield z2
    #@+node:ekr.20140526082700.17545: *5* fg.ExceptHandler
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
    #@+node:ekr.20140526082700.17546: *5* fg.Exec
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
    #@+node:ekr.20140526082700.17547: *5* fg.For
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
    #@+node:ekr.20140526082700.17548: *5* fg.FunctionDef
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
    #@+node:ekr.20140526082700.17549: *5* fg.Global
    # Global(identifier* names)

    def do_Global(self,node):

        raise StopIteration
    #@+node:ekr.20140526082700.17550: *5* fg.If
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
    #@+node:ekr.20140526082700.17551: *5* fg.Import & ImportFrom
    # Import(alias* names)

    def do_Import(self,node):

        raise StopIteration

    # ImportFrom(identifier? module, alias* names, int? level)

    def do_ImportFrom(self,node):
        
        for z in node.names:
            for z2 in self.visit(z):
                yield z2
    #@+node:ekr.20140526082700.17552: *5* fg.Module
    def do_Module(self,node):

        for z in node.body:
            for z2 in self.visit(z):
                yield z2
    #@+node:ekr.20140526082700.17553: *5* fg.Pass
    def do_Pass(self,node):

        raise StopIteration

    #@+node:ekr.20140526082700.17554: *5* fg.Print
    # Python 2.x only
    # Print(expr? dest, expr* values, bool nl)
    def do_Print(self,node):

        if getattr(node,'dest',None):
            for z in self.visit(node.dest):
                yield z
        for z in node.values:
            for z2 in self.visit(z):
                yield z2
    #@+node:ekr.20140526082700.17555: *5* fg.Raise
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
    #@+node:ekr.20140526082700.17556: *5* fg.Return
    # Return(expr? value)

    def do_Return(self,node):
        
        if node.value:
            for z in self.visit(node.value):
                yield z
    #@+node:ekr.20140526082700.17557: *5* fg.TryExcept
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
    #@+node:ekr.20140526082700.17558: *5* fg.TryFinally
    # TryFinally(stmt* body, stmt* finalbody)

    def do_TryFinally(self,node):

        for z in node.body:
            for z2 in self.visit(z):
                yield z2
        for z in node.finalbody:
            for z2 in self.visit(z):
                yield z2
    #@+node:ekr.20140526082700.17559: *5* fg.While
    # While(expr test, stmt* body, stmt* orelse)

    def do_While (self,node):

        for z in node.body:
            for z2 in self.visit(z):
                yield z2
        for z in node.orelse:
            for z2 in self.visit(z):
                yield z2
    #@+node:ekr.20140526082700.17560: *5* fg.With
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
    #@+node:ekr.20140526082700.17561: *5* fg.Yield
    #  Yield(expr? value)

    def do_Yield(self,node):

        if node.value:
            for z in self.visit(node.value):
                yield z
    #@-others
#@+node:ekr.20140526082700.17562: *3* class AllStatementsPseudoGenerator
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
#@+node:ekr.20140526082700.17563: *3* class LocalNodeGenerator
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
#@+node:ekr.20140526082700.17564: *3* class LocalStatementGenerator (best so far)
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
    #@+node:ekr.20140526082700.17565: *4* sg.ExceptHandler
    # ExceptHandler(expr? type, expr? name, stmt* body)

    def do_ExceptHandler(self,node):

        for z in node.body:
            for z2 in self.visit(z):
                yield z2
    #@+node:ekr.20140526082700.17566: *4* sg.For
    # For(expr target, expr iter, stmt* body, stmt* orelse)

    def do_For (self,node):

        for z in node.body:
            for z2 in self.visit(z):
                yield z2
        for z in node.orelse:
            for z2 in self.visit(z):
                yield z2
    #@+node:ekr.20140526082700.17567: *4* sg.If
    # If(expr test, stmt* body, stmt* orelse)

    def do_If(self,node):
        
        for z in node.body:
            for z2 in self.visit(z):
                yield z2
        for z in node.orelse:
            for z2 in self.visit(z):
                yield z2
    #@+node:ekr.20140526082700.17568: *4* sg.TryExcept
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
    #@+node:ekr.20140526082700.17569: *4* sg.TryFinally
    # TryFinally(stmt* body, stmt* finalbody)

    def do_TryFinally(self,node):

        for z in node.body:
            for z2 in self.visit(z):
                yield z2
        for z in node.finalbody:
            for z2 in self.visit(z):
                yield z2
    #@+node:ekr.20140526082700.17570: *4* sg.While
    # While(expr test, stmt* body, stmt* orelse)

    def do_While (self,node):

        for z in node.body:
            for z2 in self.visit(z):
                yield z2
        for z in node.orelse:
            for z2 in self.visit(z):
                yield z2
    #@+node:ekr.20140526082700.17571: *4* sg.With
    # With(expr context_expr, expr? optional_vars, stmt* body)

    def do_With (self,node):

        for z in node.body:
            for z2 in self.visit(z):
                yield z2
    #@-others

#@+node:ekr.20140526082700.18006: ** Old classes (keep)
#@+node:ekr.20140526082700.18007: *3*   class AstTraverser
class AstTraverser:
    
    '''
    The base class for all traversers.
    
    See the documentation for *important* information about this class.
    '''

    #@+others
    #@+node:ekr.20140526082700.18008: *4*  a.Birth
    def __init__(self):

        self.context_stack = []
        self.level = 0 # The indentation level (not the context level).
            # The number of parents a node has.
        self.parents = [None]
    #@+node:ekr.20140526082700.18009: *4* a.traversers
    #@+node:ekr.20140526082700.18010: *5* a.find_function_call
    # Used by leoInspect code.

    def find_function_call (self,node):

        '''
        Return the static name of the function being called.
        
        tree is the tree.func part of the Call node.'''
        
        trace = True and self.enable_trace
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
    #@+node:ekr.20140526082700.18011: *5* a.get/push/pop_context
    def get_context (self):

        return self.context_stack[-1]

    def push_context (self,context):

        assert context
        self.context_stack.append(context)

    def pop_context (self):

        self.context_stack.pop()
    #@+node:ekr.20140526082700.18012: *5* a.get_child_nodes
    def get_child_nodes(self,node):

        assert isinstance(node,ast.AST),node.__class__.__name__

        if node._fields is not None:
            for name in node._fields:
                child = getattr(node, name)
                if isinstance(child, list):
                    for node2 in child:
                        if isinstance(node2, ast.AST):
                            yield node2    
                elif isinstance(child, ast.AST):
                    yield child
    #@+node:ekr.20140526082700.18013: *5* a.has_children
    def has_children(self,node):
        
        assert isinstance(node,ast.AST),node.__class__.__name__
        
        return any(self.get_child_nodes(node))
    #@+node:ekr.20140526082700.18014: *5* a.run (default entry)
    def run (self,s):

        t1 = time.time()
        node = ast.parse(s,filename=self.fn,mode='exec')
        self.visit(node)
        t2 = time.time()
        return t2-t1
    #@+node:ekr.20140526082700.18015: *5* a.visit
    def visit(self,node):
        
        """Walk a tree of AST nodes."""

        assert isinstance(node,ast.AST),node.__class__.__name__

        method_name = 'do_' + node.__class__.__name__
        method = getattr(self,method_name,None)
        if method:
            # method is responsible for traversing subtrees.
            return method(node)
        else:
            # Traverse subtrees automatically, without calling visit_children.
            for child in self.get_child_nodes(node):
                self.visit(child)
    #@+node:ekr.20140526082700.18016: *5* a.visit_children
    # def visit_children(self,node):
        
        # assert isinstance(node,ast.AST),node.__class__.__name__

        # for child in self.get_child_nodes(node):
            # self.visit(child)
    #@+node:ekr.20140526082700.18017: *5* a.visit_list
    def visit_list (self,aList):
        
        assert isinstance(aList,(list,tuple))
        
        for z in aList:
            self.visit(z)
    #@+node:ekr.20140526082700.18018: *4* a.utils
    #@+node:ekr.20140526082700.18019: *5* a.attribute_base
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
    #@+node:ekr.20140526082700.18020: *5* a.attribute_target (To be deleted)
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
    #@+node:ekr.20140526082700.18021: *5* a.check_visitor_names
    def check_visitor_names(self):
        
        '''Check that there is an ast.AST node named x
        for all visitor methods do_x.'''
        
        #@+<< ast abstract grammar >>
        #@+node:ekr.20140526082700.18022: *6* << ast abstract grammar >>
        #@@nocolor-node
        #@+at
        # Python 3 only:
        #     arguments = (arg* args, identifier? vararg, expr? varargannotation,
        #                      arg* kwonlyargs, identifier? kwarg,
        #                      expr? kwargannotation, expr* defaults,
        #                      expr* kw_defaults)
        #     arg = (identifier arg, expr? annotation)
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
        #@-<< ast abstract grammar >>
        #@+<< define names >>
        #@+node:ekr.20140526082700.18023: *6* << define names >>
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
            'TryExcept','TryFinally','Tuple','UAdd','USub','UnaryOp',
            'While','With','Yield',
            # Lower case names...
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

        # Inexpensive, because there are few entries in aList.
        aList = [z for z in dir(self) if z.startswith('do_')]
        for s in sorted(aList):
            name = s[3:]
            if name not in names:
                g.trace('***** oops',self.__class__.__name__,name)
                assert False,name
                    # This is useful now that most errors have been caught.
    #@+node:ekr.20140526082700.18024: *5* a.info
    def info (self,node):
        
        return '%s: %9s' % (node.__class__.__name__,id(node))
    #@+node:ekr.20140526082700.18025: *5* a.kind
    def kind(self,node):
        
        return node.__class__.__name__
    #@+node:ekr.20140526082700.18026: *5* a.op_name
    def op_name (self,node):
        
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
        'do_AugLoad':  '<AugLoad>',
        'do_AugStore': '<AugStore>',
        'do_Del':      '<Del>',
        'do_Load':     '<Load>',
        'do_Param':    '<Param>',
        'do_Store':    '<Store>',
        # Unary operators.
        'Invert':   '~',
        'Not':      ' not ',
        'UAdd':     '+',
        'USub':     '-',
        }
        name = d.get(self.kind(node),'<%s>' % node.__class__.__name__)
        assert name,self.kind(node)
        return name
    #@-others
#@+node:ekr.20140526082700.18027: *3*   class StatementTraverser
class StatementTraverser(AstFullTraverser):
    
    def __init__ (self):

        AstFullTraverser.__init__(self)
            # Init the base class.
        self.root = None

    #@+others
    #@+node:ekr.20140526082700.18028: *4* stat.run
    def run (self,root):

        self.root = root
        self.visit(root)
    #@+node:ekr.20140526082700.18029: *4* stat.visit & helpers
    def default_visitor(self,node):
        pass
       
    def visit(self,node):
        
        '''Visit a *single* ast node.  Visitors are responsible for visiting children!'''
        assert isinstance(node,ast.AST),node.__class__.__name__
        method_name = 'do_' + node.__class__.__name__
        method = getattr(self,method_name,self.default_visitor)
        return method(node)

    def visit_children(self,node):
        assert False,'must visit children explicitly'
    #@+node:ekr.20140526082700.18030: *4* stat.Do nothings
    if 0:
        #@+others
        #@+node:ekr.20140526082700.18031: *5* stat.Assert
        # Assert(expr test, expr? msg)

        def do_Assert(self,node):
            pass
        #@+node:ekr.20140526082700.18032: *5* stat.Assign
        # Assign(expr* targets, expr value)

        def do_Assign(self,node):
            pass
        #@+node:ekr.20140526082700.18033: *5* stat.AugAssign
        # AugAssign(expr target, operator op, expr value)

        def do_AugAssign(self,node):
            pass
        #@+node:ekr.20140526082700.18034: *5* stat.Break
        def do_Break(self,node):
            pass

        #@+node:ekr.20140526082700.18035: *5* stat.Continue
        def do_Continue(self,node):
            pass
        #@+node:ekr.20140526082700.18036: *5* stat.Delete
        # Delete(expr* targets)

        def do_Delete(self,node):
            pass
        #@+node:ekr.20140526082700.18037: *5* stat.Exec
        # Python 2.x only
        # Exec(expr body, expr? globals, expr? locals)

        def do_Exec(self,node):
            pass
        #@+node:ekr.20140526082700.18038: *5* stat.Expr
        # Expr(expr value)

        def do_Expr(self,node):
            pass
        #@+node:ekr.20140526082700.18039: *5* stat.Global
        # Global(identifier* names)

        def do_Global(self,node):
            pass
        #@+node:ekr.20140526082700.18040: *5* stat.Import & ImportFrom
        # Import(alias* names)

        def do_Import(self,node):
            pass

        # ImportFrom(identifier? module, alias* names, int? level)

        def do_ImportFrom(self,node):
            pass
        #@+node:ekr.20140526082700.18041: *5* stat.Pass
        def do_Pass(self,node):
            pass
        #@+node:ekr.20140526082700.18042: *5* stat.Print
        # Python 2.x only
        # Print(expr? dest, expr* values, bool nl)
        def do_Print(self,node):
            pass
            
        #@+node:ekr.20140526082700.18043: *5* stat.Raise
        # Raise(expr? type, expr? inst, expr? tback)

        def do_Raise(self,node):
            pass
        #@+node:ekr.20140526082700.18044: *5* stat.Return
        # Return(expr? value)

        def do_Return(self,node):
            pass
        #@+node:ekr.20140526082700.18045: *5* stat.Yield
        #  Yield(expr? value)

        def do_Yield(self,node):
            pass
        #@-others
    #@-others
#@+node:ekr.20140526082700.18046: *3* class CacheTraverser (AstTraverser)
class CacheTraverser(AstTraverser):
    
    '''A class to report the contents of caches.'''
    
    def __init__(self):
    
        AstTraverser.__init__(self)
        self.level = 0
    
    #@+others
    #@+node:ekr.20140526082700.18047: *4* ct.show_cache
    def show_cache(self,obj,cache,tag):
        
        d = cache
        pad = ' '*2*self.level
        result = []
        for key in sorted(d.keys()):
            aList = d.get(key)
            if len(aList) > 1 or (aList and repr(aList[0]) != 'Unknown'):
                # result.append('  %s%20s => %s' % (pad,key,aList))
                result.append('  %s%s' % (pad,aList))
        if result:
            s = self.format(obj) if isinstance(obj,ast.AST) else repr(obj)
            s = s.replace('\n','')
            if len(s) > 40: s = s[:37]+'...'
            if len(result) == 1:
                print('%s%s: %40s -> %s' % (pad,tag,s,result[0].strip()))
            else:
                print('%s%s: %s' % (pad,tag,s))
                for s in result:
                    print(s)
    #@+node:ekr.20140526082700.18048: *4* ct.run
    def run (self,node):

        self.check_visitor_names()
        fn = ' for %s' % (g.shortFileName(self.fn)) if self.fn else ''
        print('\nDump of caches%s...' % fn)
        self.visit(node)
    #@+node:ekr.20140526082700.18049: *4* ct.traversers
    #@+node:ekr.20140526082700.18050: *5* ct.visit
    def visit(self,node):
        
        """Walk a tree of AST nodes."""

        assert isinstance(node,ast.AST),node.__class__.__name__

        method_name = 'do_' + node.__class__.__name__
        method = getattr(self,method_name,None)
        if method:
            # method is responsible for traversing subtrees.
            return method(node)
        else:
            self.visit_cache(node)

            # Traverse subtrees automatically, without calling visit_children.
            for child in self.get_child_nodes(node):
                self.visit(child)
    #@+node:ekr.20140526082700.18051: *5* ct.visit_cache
    def visit_cache(self,node):
        
        if hasattr(node,'cache'):
            self.show_cache(node,node.cache,'cache')
            
        if hasattr(node,'e') and hasattr(node.e,'call_cache'):
            self.show_cache(node,node.e.call_cache,'call_cache')
    #@+node:ekr.20140526082700.18052: *4* ct.visitors
    #@+node:ekr.20140526082700.18053: *5* ct.ClassDef
    # ClassDef(identifier name, expr* bases, stmt* body, expr* decorator_list)

    def do_ClassDef(self,node):
        
        pad = ' '*2*self.level
        bases = ','.join([self.format(z) for z in node.bases])
        print('%sclass %s(%s)' % (pad,node.name,bases))
        
        self.level += 1
        try:
            self.visit_children(node)
        finally:
            self.level -= 1
    #@+node:ekr.20140526082700.18054: *5* ct.functionDef
    # FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list)

    def do_FunctionDef (self,node):
        
        pad = ' '*2*self.level
        print('%sdef %s(%s)' % (pad,node.name,self.format(node.args)))
        
        self.level += 1
        try:
            self.visit_children(node)
        finally:
            self.level -= 1
    #@-others
#@+node:ekr.20140526082700.18055: *3* class ChainPrinter (OpPatternFormatter)
class ChainPrinter: ### (OpPatternFormatter):
    
    def __init__ (self,fn):
    
        self.d = {}
        self.top_attribute = True
    
        ### OpPatternFormatter.__init__ (self)
            # Init the base class.

    #@+others
    #@+node:ekr.20140526082700.18056: *4* Attribute
    # Attribute(expr value, identifier attr, expr_context ctx)

    def do_Attribute(self,node):
        
        top = self.top_attribute
        try:
            self.top_attribute = False
            value = node.value
            attr  = node.attr
            s = '%s.%s' % (
                self.visit(value),
                self.visit(attr))
        finally:
            self.top_attribute = top
            
        if top:
            aList = s.split('.')
            if aList:
                name,rest = aList[0],aList[1:]
                if (
                    name == 'self' and len(rest) > 1 or
                    name != 'self' and len(rest) > 0
                ):
                    aList2 = self.d.get(name,[])
                    if rest not in aList2:
                        aList2.append(rest)
                        self.d[name] = aList2
                    
        return s
    #@+node:ekr.20140526082700.18057: *4* showChains
    def showChains(self):
        
        verbose = False
        result = []
        d,n1,n2 = self.d,0,0
        for key in sorted(d.keys()):
            aList = d.get(key)
            for chain in sorted(aList):
                s = '.'.join(chain)
                if s.find('(') > -1 or s.find('[') > -1 or s.find('{') > -1:
                    # print('%s.%s' % (key,s))
                    result.append('%s.%s' % (key,s))
                    n2 += 1
                else:
                    if verbose:
                        result.append('%s.%s' % (key,s))
                    n1 += 1

        return n1,n2,'\n'.join(result)

    #@-others
#@+node:ekr.20140526082700.18058: *3* class Context & subclasses
#@+<< define class Context >>
#@+node:ekr.20140526082700.18059: *4* << define class Context >>
class Context:

    '''The base class of all Context objects.
    Contexts represent static scopes.'''

    #@+others
    #@+node:ekr.20140526082700.18060: *5*  cx ctor
    def __init__(self,parent_context):

        self.format = u.format
        self.kind = '<Unknown context kind>' # All subclasses set this.
        self.name = '<Unknown context name>' # All subclasses set this.
        self.parent_context = parent_context
        self.st = SymbolTable(cx=self)
        self.stats = Stats()
        self.stats.n_contexts += 1

        # Public semantic data: accessed via getters.
        self.assignments_list = [] # All assignment statements.
        self.calls_list = [] # All call statements defined in this context.
        self.classes_list = [] # Classes defined in this context.
        self.defs_list = [] # Functions defined in this context.
        self.expressions_list = [] # Expr nodes in this context.
        self.definitions_of = [] # Assignments, imports and arguments that define this symbol.
        self.imported_symbols_list = [] # All imported symbols.
        self.methods_list = [] # # All methods of a class context.  Elements are DefContexts.
        self.returns_list = [] # List of all return statements in the context.
        self.statements_list = [] # List of *all* statements in the context.
        self.yields_list = [] # List of all yield statements in the context.

        # Private semantic data: no getters.
        self.n_lambdas = 0
            # Number of lambdas in this context:
            # Used to synthesize names of the form 'Lambda@@n'
        self.defining_context = self
        # self.global_names = set()
            # Names that appear in a global statement in this context.
        self.node = None
            # The AST tree representing this context.
    #@+node:ekr.20140526082700.18061: *5* cx.__getstate__
    def __getstate__(self):
        
        '''Return the representation of the Context class for use by pickle.'''
        
        d = {
            'calls':        [repr(z) for z in self.calls_list],
            'classes':      [repr(z) for z in self.classes_list],
            'defs':         [repr(z) for z in self.defs_list],
            'statements':   [repr(z) for z in self.statements()],
        }

        return d
    #@+node:ekr.20140526082700.18062: *5* cx.__hash__
    # Important: Define __hash__ only if __eq__ is also defined.

    def __hash__ (self):
        return id(self)

    # This is defined below...

    # def __eq__ (self,other):
        # return id(self) == id(other)
    #@+node:ekr.20140526082700.18063: *5* cx.__repr__ & __str__
    def __repr__ (self):

        return 'Cx:id(%s)' % id(self)
        
    __str__ = __repr__
    #@+node:ekr.20140526082700.18064: *5* cx.__eq__ & __ne__(others return NotImplemented)
    # Py3k wants __lt__ etc, and Py2k needs all of them defined.

    # Use identity only for contexts!
    def __lt__(self, other): return NotImplemented 
    def __le__(self, other): return NotImplemented 
    def __eq__(self, other): return id(self) == id(other)
    def __ne__(self, other): return id(self) != id(other)
    def __gt__(self, other): return NotImplemented 
    def __ge__(self, other): return NotImplemented 

    # if 1:
        # # Ignore case in comparisons.
        # def __lt__(self, other): return self.name.lower() <  other.name.lower()
        # def __le__(self, other): return self.name.lower() <= other.name.lower()
        # def __eq__(self, other): return self.name.lower() == other.name.lower()
        # def __ne__(self, other): return self.name.lower() != other.name.lower()
        # def __gt__(self, other): return self.name.lower() >  other.name.lower()
        # def __ge__(self, other): return self.name.lower() >= other.name.lower()
    # else:
        # def __lt__(self, other): return self.name <  other.name
        # def __le__(self, other): return self.name <= other.name
        # def __eq__(self, other): return self.name == other.name
        # def __ne__(self, other): return self.name != other.name
        # def __gt__(self, other): return self.name >  other.name
        # def __ge__(self, other): return self.name >= other.name
    #@+node:ekr.20140526082700.18065: *5* cx.description & short_description
    def description (self):
        
        '''Return a description of this context and all parent contexts.'''
        
        if self.parent_context:
            return  '%s:%s' % (
                self.parent_context.description(),repr(self))
        else:
            return repr(self)

    def short_description(self):
        return repr(self)
    #@+node:ekr.20140526082700.18066: *5* cx.dump_statements
    def dump_statements(self,var_filter=None):
        
        cx = self
        # aList = [node.dump(0,var_filter=var_filter) for node in cx.local_statements()]
        aList = [self.u.dump_ast(node) for node in cx.local_statements()]
        return '\n'.join([z for z in aList if z.strip()])
    #@+node:ekr.20140526082700.18067: *5* cx.full_name
    def full_name (self):
        
        '''Return a context name for compatibility with HTMLReportTraverser.'''
        
        # A hack: must match the name generated in rt.report().
        
        return 'report_writer_test' if self.name == '<string>' else self.name
    #@+node:ekr.20140526082700.18068: *5* cx.generators & getters
    # Unlike in leoInspect, most of these getters return lists of Statement objects.
    #@+node:ekr.20140526082700.18069: *6* cx.assignments
    # This is really a helper for assignments_to/using.
    def assignments(self):
        
        result = []
        for cx in self.contexts():
            result.extend(cx.assignments_list)
        return result
    #@+node:ekr.20140526082700.18070: *6* cx.assignments_to (rewritten)
    def assignments_to (self,s):
        
        cx = self
        result = []
        for node in cx.assignments():
            statement = cx.u.format(node)
            kind = cx.u.kind(node)
            if kind == 'Assign':
                #  Assign(expr* targets, expr value)
                for target in node.targets:
                    kind2 = cx.u.kind(target)
                    if kind2 == 'Name':
                        if s == target.id:
                            result.append(statement)
                    elif kind2 == 'Tuple':
                        # Tuple(expr* elts, expr_context ctx)
                        for item2 in target.elts:
                            if cx.u.kind(item2) == 'Name' and s == item2.id:
                                result.append(statement)
            elif kind == 'AugAssign':
                kind2 = cx.u.kind(node.target)
                if kind2 == 'Name':
                    if s == node.target.id:
                        result.append(statement)
            elif kind == 'For':
                s2 = statement
                i = s2.find(' in ')
                assert s2.startswith('for ')
                assert i > -1
                s2 = s2[4:i].strip('()')
                aList = s2.split(',')
                if s in aList:
                    i = statement.find(':\n')
                    assert i > -1
                    result.append(statement[:i+1])
            elif kind == 'ListComp':
                # node.generators is a comprehension.
                for item in node.generators:
                    target = item.target
                    kind2 = cx.u.kind(target)
                    if kind2 == 'Name':
                        if s == target.id:
                            result.append(statement)
                    elif kind2 == 'Tuple':
                        for item2 in target.elts:
                            if cx.u.kind(item2) == 'Name' and s == item2.id:
                                result.append(statement)
                                break
                    else:
                        assert False,kind2
            else:
                assert False,kind
        return list(set(result))
    #@+node:ekr.20140526082700.18071: *6* cx.assignments_using
    def assignments_using (self,s):
        
        result = []
        for node in self.assignments():
            assert node.kind in ('Assign','AugAssign'),node.kind
            val = node.value
            rhs = self.format(val)
            i = rhs.find(s,0)
            while -1 < i < len(rhs):
                if g.match_word(rhs,i,s):
                    result.append(node)
                    break
                else:
                    i += len(s)

        return result
    #@+node:ekr.20140526082700.18072: *6* cx.call_args_of
    def call_args_of (self,s):
        
        result = []
        for node in self.calls():
            assert node.kind == 'Call'
            func = self.format(node.func)
            if s == func:
                result.append(node) ### Should return only args.

        return result
    #@+node:ekr.20140526082700.18073: *6* cx.calls
    # This is really a helper for calls_to/call_args_of.
    def calls(self):
        
        result = []
        for cx in self.contexts():
            result.extend(cx.calls_list)
        return result
    #@+node:ekr.20140526082700.18074: *6* cx.calls_to
    def calls_to (self,s):

        result = []
        for node in self.calls():
            assert node.kind == 'Call'
            func = self.format(node.func)
            if s == func:
                result.append(node)

        return result
    #@+node:ekr.20140526082700.18075: *6* cx.classes
    def classes (self):
        
        result = []
        for cx in self.contexts():
            result.extend(cx.classes_list)
        return result
    #@+node:ekr.20140526082700.18076: *6* cx.contexts & getters
    def contexts (self,name=None):
            
        '''An iterator returning all contexts.
        
        If name is given, return only contexts with the given name.'''
        
        cx = self
        
        if name is None or cx.name == name:
            yield cx
           
        for cx2 in self.classes_list:
            for z in cx2.contexts(name=name):
                if z != self:
                    yield z

        for cx2 in self.defs_list:
            for z in cx2.contexts(name=name):
                if z != self:
                    yield z
    #@+node:ekr.20140526082700.18077: *7* get_contexts and get_unique_context
    # These getters are designed for unit testing.
    def get_contexts(self,name):
        
        '''Return the list of symbol tables having the given name.
        If the list has exactly one element, return it.'''
        
        aList = list(self.contexts(name=name))
        return aList[0] if aList and len(aList) == 1 else aList
       
    def get_unique_context (self,name):
        
        '''Return the unique symbol table having the given name.
        Raise AssertionError if the unexpected happens.'''
        
        aList = list(self.contexts(name=name))
        assert aList and len(aList) == 1,aList
        return aList[0]
    #@+node:ekr.20140526082700.18078: *6* cx.defs
    def defs (self):
        
        result = []
        for cx in self.contexts():
            result.extend(cx.defs_list)
        return result
    #@+node:ekr.20140526082700.18079: *6* cx.parent_contexts
    def parent_contexts (self):
        
        cx = self
        result = []

        while cx.parent_context:
            result.append(cx.parent_context)
            cx = cx.parent_context

        result.reverse()
        return result
    #@+node:ekr.20140526082700.18080: *6* cx.returns (dubious)
    # Using cx.returns_list will almost always be correct.

    if 0:
        
        def returns (self):
            
            '''Return all return statements in the present context and all descendant contexts.'''
            
            result = []
            for cx in self.contexts():
                result.extend(cx.returns_list)
            return result
    #@+node:ekr.20140526082700.18081: *6* cx.statements (new)
    def statements (self):
        
        '''A generator yielding all statements in the receiver context, in the proper order.'''

        cx = self
        assert cx.kind in ('class','def','lambda','module')
        for node in cx.statements_list:
            yield node
    #@+node:ekr.20140526082700.18082: *6* cx.symbol_tables & getters
    def symbol_tables (self,name=None):
        
        '''Return all symbol tables for all contexts.
        If name is given, return only symbol tables for contexts with the given name.'''
        
        cx = self

        if name:
            for cx2 in self.contexts():
                if name == cx2.name:
                    yield cx2.st
        else:
            for cx2 in self.contexts():
                yield cx2.st

    #@+node:ekr.20140526082700.18083: *7* get_symbol_tables and get_unique_symbol_table
    # These getters are designed for unit testing.
    def get_symbol_tables (self,name):
        
        '''Return the list of symbol tables having the given name.
        If the list has exactly one element, return it.'''
        
        aList = list(self.symbol_tables(name=name))
        return aList[0] if aList and len(aList) == 1 else aList
       
    def get_unique_symbol_table (self,name):
        
        '''Return the unique symbol table having the given name.
        Raise AssertionError if the unexpected happens.'''
        
        aList = list(self.symbol_tables(name=name))
        assert aList and len(aList) == 1,aList
        return aList[0]
    #@+node:ekr.20140526082700.18084: *6* cx.symbol_table_entries
    def symbol_table_entries (self,name):
        
        '''Return all STE's for the given name.'''
        
        cx = self

        for cx2 in cx.contexts():
            d = cx2.st.d
            e = d.get(name)
            if e:
                yield d.get(name)
    #@+node:ekr.20140526082700.18085: *6* cx.local_statements
    def local_statements(self):
        
        '''Return the top-level statements of a context.'''
        
        cx = self

        assert cx.kind in ('class','def','lambda','module')

        return cx.node.body
    #@+node:ekr.20140526082700.18086: *5* cx.line_number (not used)
    # def line_number (self):
        
        # return self.tree_ptr.lineno
    #@+node:ekr.20140526082700.18087: *5* cx.token_range (TO DO) (Uses tree_ptr)
    # def token_range (self):
        
        # tree = self.tree_ptr
        
        # # return (
            # # g.toUnicode(self.byte_array[:tree.col_offset]),
            # # g.toUnicode(self.byte_array[:tree_end_col_offset]),
        # # )
        
        # if getattr(tree,'col_offset',None):
            # return tree.lineno,tree.col_offset,tree.end_lineno,tree.end_col_offset
        # else:
            # return -1,-1
    #@-others
#@-<< define class Context >>

#@+others
#@+node:ekr.20140526082700.18088: *4* class ClassContext
class ClassContext (Context):

    '''A class to hold semantic data about a class.'''
    
    #@+others
    #@+node:ekr.20140526082700.18089: *5* ClassContext.__init__
    def __init__(self,u,parent_context,name,node,bases):

        Context.__init__(self,u,parent_context)
            # Init the base class.

        self.ctor = None # Filled in when def __init__ seen.
        self.kind = 'class'
        self.bases = bases # A list of ast.Name nodes?
        self.name = name
        self.class_context  = self
        self.def_context = self.parent_context.def_context
        self.ivars_dict = {} # Keys are names, values are reaching sets.
        self.module_context = self.parent_context.module_context
        self.node = node
        u.stats.n_classes += 1
    #@+node:ekr.20140526082700.18090: *5* ClassContext.__repr__& __str__
    def __repr__ (self):

        if self.bases:
            bases = [self.format(z) for z in self.bases]
            return 'Cx:class %s(%s)' % (self.name,','.join(bases))
        else:
            return 'Cx:class %s' % (self.name)

    __str__ = __repr__        
    #@+node:ekr.20140526082700.18091: *5* ClassContext.short_description
    def short_description(self):
        
        if self.bases:
            bases = [self.format(z) for z in self.bases]
            return 'class %s(%s):' % (self.name,','.join(bases))
        else:
            return 'class %s:' % (self.name)
    #@-others

#@+node:ekr.20140526082700.18092: *4* class DefContext
class DefContext (Context):

    '''A class to hold semantic data about a function/method.'''
        
    #@+others
    #@+node:ekr.20140526082700.18093: *5* DefContext.__init__
    def __init__(self,u,parent_context,name):
        
        Context.__init__(self,u,parent_context)
        self.kind = 'def'
        self.name = name
        self.args = None # Must be set later.
        self.class_context = self.parent_context.class_context
        self.def_context = self
        self.module_context = self.parent_context.module_context
        self.node = None
        u.stats.n_defs += 1
    #@+node:ekr.20140526082700.18094: *5* DefContext.__repr__ & __str__
    def __repr__ (self):
        
        args = self.format(self.args) if self.args else  '<**no args yet**>'

        return 'Cx:def %s(%s)' % (self.name,args)

    __str__ = __repr__        
    #@+node:ekr.20140526082700.18095: *5* DefContext.short_description
    def short_description (self):
      
        args = self.format(self.args) if self.args else ''

        return 'def %s(%s):' % (self.name,args)
    #@-others

    
#@+node:ekr.20140526082700.18096: *4* class LambdaContext
class LambdaContext (Context):

    '''A class to represent the range of a 'lambda' statement.'''

    def __init__(self,u,parent_context,name):
        Context.__init__(self,u,parent_context)
        self.kind = 'lambda'
        self.args = None # Patched in later.
        self.class_context  = self.parent_context.class_context
        self.def_context    = self.parent_context.def_context
        self.module_context = self.parent_context.module_context
        self.name = name # Set to 'Lambda@@n' by the caller.
        self.node = None
        u.stats.n_lambdas += 1

    def __repr__ (self):
        if self.args:
            args = ','.join([self.format(z) for z in self.args])
        else:
            args = 'None'
        return 'Cx:lambda %s:' % (args)

    __str__ = __repr__
#@+node:ekr.20140526082700.18097: *4* class LIbraryModuleContext
class LibraryModuleContext (Context):

    '''A class to hold semantic data about a module.'''

    def __init__(self,u,fn):
        Context.__init__(self,u,parent_context=None)
        self.kind = 'module'
        self.class_context  = None
        self.def_context    = None
        self.fn = g.os_path_abspath(fn)
        self.module_context = self
        self.module_type = Module_Type(u,self,node=None)
            # The singleton *constant* type of this module.
        if fn.find('.') > -1:
            self.name = g.shortFileName(self.fn)[:-3]
        else:
            self.name = fn
        self.node = None
        u.stats.n_library_modules += 1

    def __repr__ (self):
        return 'Cx:module(%s)' % self.name

    __str__ = __repr__        
#@+node:ekr.20140526082700.18098: *4* class ModuleContext
class ModuleContext (Context):

    '''A class to hold semantic data about a module.'''

    def __init__(self,u,fn,node):
        Context.__init__(self,u,parent_context=None)
        self.kind = 'module'
        self.class_context  = None
        self.def_context    = None
        self.fn = g.os_path_abspath(fn)
        self.module_context = self
        self.module_type = Module_Type(u,self,node)
            # The singleton *constant* type of this module.
        if fn.find('.') > -1:
            self.name = g.shortFileName(self.fn)[:-3]
        else:
            self.name = fn
        self.node = node
        u.stats.n_modules += 1

    def __repr__ (self):
        return 'Cx:module(%s)' % self.name

    __str__ = __repr__        
#@-others
#@+node:ekr.20140526082700.18099: *3* class GeneralTest (StcTest)
class GeneralTest: ### (StcTest):
    
    '''A general test class.'''
    
    #@+others
    #@-others
#@+node:ekr.20140526082700.18100: *3* class HTMLReportTraverser (AstFullTraverser)
class HTMLReportTraverser (AstFullTraverser):
    
    '''
    Create html reports from an AST tree.
    
    Adapted from micropython, by Paul Boddie. See the copyright notices.
    '''
    # To do: show stc attributes in the report.
    # To do: revise report-traverser-debug.css.
    #@+others
    #@+node:ekr.20140526082700.18101: *4* rt.__init__
    def __init__(self):
        
        self.visitor = self
        
        AstFullTraverser.__init__(self)
            # Init the base class.
            
        self.debug = True

        self.css_fn = 'report-traverser-debug.css' if self.debug else 'report-traverser.css'
        self.html_footer = '\n</body>\n</html>\n'
        self.html_header = self.define_html_header()
    #@+node:ekr.20140526082700.18102: *5* define_html_header
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
    #@+node:ekr.20140526082700.18103: *4* rt.css links & popup
    #@+node:ekr.20140526082700.18104: *5* rt.link
    def link (self,class_name,href,a_text):

        # g.trace(class_name,a_text)
        return "<a class='%s' href='%s'>%s</a>" % (class_name,href,a_text)
    #@+node:ekr.20140526082700.18105: *5* rt.module_link
    def module_link(self,module_name,classes=None):
        
        r = self
        return r.link(
            class_name = classes or 'name',
            href = '%s.xhtml' % module_name,
            a_text = r.text(module_name))
    #@+node:ekr.20140526082700.18106: *5* rt.name_link
    def name_link(self,module_name,full_name,name,classes=None):
        
        r = self
        # g.trace(name,classes)
        return r.link(
            class_name = classes or "specific-ref",
            href = '%s.xhtml#%s' % (module_name,r.attr(full_name)),
            a_text = r.text(name))
    #@+node:ekr.20140526082700.18107: *5* rt.object_name_ref
    def object_name_ref(self,module,obj,name=None,classes=None):

        """
        Link to the definition for 'module' using 'obj' with the optional 'name'
        used as the label (instead of the name of 'obj'). The optional 'classes'
        can be used to customise the CSS classes employed.
        """

        r = self
        return r.name_link(module.full_name(),obj.full_name(),name or obj.name,classes)
    #@+node:ekr.20140526082700.18108: *5* rt.popup
    def popup(self,classes,aList):
        r = self
        return r.span(classes or 'popup',aList)
    #@+node:ekr.20140526082700.18109: *5* rt.summary_link
    def summary_link(self,module_name,full_name,name,classes=None):
        
        r = self
        return r.name_link("%s-summary" % module_name,full_name,name,classes)
    #@+node:ekr.20140526082700.18110: *4* rt.html attribute helpers
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
    #@+node:ekr.20140526082700.18111: *5* rt.get_stc_attrs & AttributeTraverser
    def get_stc_attrs (self,node,all):
        
        r = self
        nodes = r.NameTraverser(self.u).run(node) if all else [node]
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
            result.append(join_list(aList,sep=', '))
        return join_list(result,sep='; ')
    #@+node:ekr.20140526082700.18112: *6* NameTraverser(AstFullTraverser)
    class NameTraverser(AstFullTraverser):
        
        def __init__(self):
            AstFullTraverser.__init__(self)
            self.d = {}

        def do_Name(self,node):
            self.d[node.e.name] = node
                
        def run(self,root):
            self.visit(root)
            return [self.d.get(key) for key in sorted(self.d.keys())]
    #@+node:ekr.20140526082700.18113: *5* rt.stc_attrs
    def stc_attrs (self,node,all=False):
        
        r = self
        attrs = r.get_stc_attrs(node,all=all)
        return attrs and [
            r.span('inline-attr nowrap',[
                attrs,
            ]),
            r.br(),
        ]
    #@+node:ekr.20140526082700.18114: *5* rt.stc_popup_attrs
    def stc_popup_attrs(self,node,all=False):

        r = self
        attrs = r.get_stc_attrs(node,all=all)
        return attrs and [
            r.popup('attr-popup',[
                attrs,
            ]),
        ]
    #@+node:ekr.20140526082700.18115: *4* rt.html helpers
    #@+node:ekr.20140526082700.18116: *5* rt.attr & text
    def attr(self,s):
        
        r = self
        return r.text(s).replace("'","&apos;").replace('"',"&quot;")

    def text(self,s):

        return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
    #@+node:ekr.20140526082700.18117: *5* rt.br
    def br(self):
        
        r = self
        return '\n<br />'
    #@+node:ekr.20140526082700.18118: *5* rt.comment
    def comment(self,comment):
        
        r = self
        return '%s\n' % r.span("# %s" % (comment),"comment")
    #@+node:ekr.20140526082700.18119: *5* rt.div
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
            join_list(aList,indent='  '),
            '\n</div>'
        ]
    #@+node:ekr.20140526082700.18120: *5* rt.doc & helper (to do)
    # Called by ClassDef & FunctionDef visitors.

    def doc(self,node,classes=None):

        # if node.doc is not None:
            # r.docstring(node.doc,classes)
            
        return ''
    #@+node:ekr.20140526082700.18121: *6* rt.docstring
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
    #@+node:ekr.20140526082700.18122: *5* rt.keyword (a helper, not a visitor!)
    def keyword(self,keyword_name,leading=False,trailing=True):

        r = self
        return [
            leading and ' ',
            r.span('keyword',[
                keyword_name,
            ]),
            trailing and ' ',
        ]
    #@+node:ekr.20140526082700.18123: *5* rt.name
    def name(self,name):
        return self.span('name',[name])

    #@+node:ekr.20140526082700.18124: *5* rt.object_name_def (rewrite)
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
    #@+node:ekr.20140526082700.18125: *5* rt.op
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
    #@+node:ekr.20140526082700.18126: *5* rt.simple_statement
    def simple_statement(self,name):
        
        r = self
        return [
            r.div('%s nowrap' % name,[
                r.keyword(name),
            ]),
        ]
    #@+node:ekr.20140526082700.18127: *5* rt.span & span_start/end
    def span(self,class_name,aList):
        
        r = self
        assert isinstance(aList,(list,tuple))
        if class_name:
            span = "\n<span class='%s'>" % (class_name)
        else:
            span = '\n<span>'
        return [
            span,
            join_list(aList,indent='  '),
            # '\n</span>',
            '</span>', # More compact
        ]
    #@+node:ekr.20140526082700.18128: *5* rt.url (not used)
    def url(self,url):

        r = self
        return r.attr(url).replace("#", "%23").replace("-", "%2d")
    #@+node:ekr.20140526082700.18129: *4* rt.reporters
    #@+node:ekr.20140526082700.18130: *5* rt.annotate
    def annotate(self,fn,m):

        r = self
        f = open(fn,"wb")
        try:
            for s in flatten_list(r.report_file()):
                f.write(s)
        finally:
            f.close()
    #@+node:ekr.20140526082700.18131: *5* rt.base_fn
    def base_fn(self,directory,m):
        
        '''Return the basic html file name used by reporters.'''

        assert g.os_path_exists(directory)

        if m.fn.endswith('<string>'):
            return 'report_writer_string_test'
        else:
            return g.shortFileName(m.fn)
    #@+node:ekr.20140526082700.18132: *5* rt.interfaces & helpers
    def interfaces(self,directory,m,open_file=False):

        r = self
        base_fn = r.base_fn(directory,m)
        fn = g.os_path_join(directory,"%s_interfaces.xhtml" % base_fn)
        f = open(fn,"wb")
        try:
            for s in flatten_list(r.write_interfaces(m)):
                f.write(s)
        finally:
            f.close()
        if open_file:
            os.startfile(fn)
    #@+node:ekr.20140526082700.18133: *6* write_interfaces
    def write_interfaces(self,m):
        
        r = self
        all_interfaces,any_interfaces = [],[]
        return join_list([
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
    #@+node:ekr.20140526082700.18134: *6* write_interface_type
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
        return join_list([
            "<tbody>",
            aList,
            '</tbody>',
        ],trailing='\n')
    #@+node:ekr.20140526082700.18135: *5* rt.report(entry_point)
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
    #@+node:ekr.20140526082700.18136: *5* rt.report_all_modules(needed to write interfaces)
    def report_all_modules(self,directory):

        trace = True
        r = self
        join = g.os_path_join
        assert g.os_path_exists(directory)
        d = r.u.modules_dict
        files = []
        for n,fn in enumerate(sorted(d.keys())):
            r.module = m = d.get(fn)
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
    #@+node:ekr.20140526082700.18137: *5* rt.report_file
    def report_file(self):
        
        r = self
        return [
            r.html_header % {
                'css-fn':self.css_fn,
                'title':'Module: %s' % r.module.full_name()},
            r.visit(r.module.node),
            r.html_footer,
        ]
    #@+node:ekr.20140526082700.18138: *5* rt.summarize & helpers
    def summarize(self,directory,m,open_file=False):

        r = self
        base_fn = r.base_fn(directory,m)
        fn = g.os_path_join(directory,"%s_summary.xhtml" % base_fn)
        f = open(fn,"wb")
        try:
            for s in flatten_list(r.summary(m)):
                f.write(s)
        finally:
            f.close()
        if open_file:
            os.startfile(fn)
    #@+node:ekr.20140526082700.18139: *6* summary & helpers
    def summary(self,m):

        r = self
        return join_list([
            r.html_header % {
                'css-fn':self.css_fn,
                'title':'Module: %s' % m.full_name()},
            r.write_classes(m),
            r.html_footer,
        ],sep='\n')
    #@+node:ekr.20140526082700.18140: *7* write_classes
    def write_classes(self,m):

        r = self
        return m.classes() and join_list([
            "<table cellspacing='5' cellpadding='5'>",
            "<thead>",
            "<tr>",
            "<th>Classes</th><th>Attributes</th>",
            "</tr>",
            "</thead>",
            [r.write_class(z) for z in m.classes()],
            "</table>",
        ],sep='\n')
    #@+node:ekr.20140526082700.18141: *7* write_class
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
        instance_names = join_list(aList,sep=', ')

        # The class attribute names in order.
        # attrs = [] ### obj.class_attributes().values()
        # aList = []
        # if attrs:
            # for attr in sorted(attrs,cmp=lambda x,y: cmp(x.position,y.position)):
                # if attr.is_strict_constant():
                    # value = attr.get_value()
                    # if False: #### not isinstance(value,Const):
                        # aList.append(join_list([
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
        # class_names = join_list(aList,sep='\n')
            
        return join_list([
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
    #@+node:ekr.20140526082700.18142: *4* rt.traversers
    #@+node:ekr.20140526082700.18143: *5* rt.visit
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
    #@+node:ekr.20140526082700.18144: *5* rt.visit_list
    def visit_list(self,aList,sep=''):
        
        # pylint: disable=W0221
            # Arguments number differs from overridden method.
        
        r = self
        if sep:
            return join_list([r.visit(z) for z in aList],sep=sep)
        else:
            return [r.visit(z) for z in aList]
    #@+node:ekr.20140526082700.18145: *4* rt.visitors
    #@+node:ekr.20140526082700.18146: *5* rt.arguments & helper
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
    #@+node:ekr.20140526082700.18147: *6* rt.tuple_parameter
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
        return join_list(result)
    #@+node:ekr.20140526082700.18148: *5* rt.Assert
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
    #@+node:ekr.20140526082700.18149: *5* rt.Assign
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
    #@+node:ekr.20140526082700.18150: *5* rt.Attribute
    # Attribute(expr value, identifier attr, expr_context ctx)

    def do_Attribute(self,node):
        
        r = self
        return [
            r.visit(node.value),
            '.',
            node.attr,
        ]
    #@+node:ekr.20140526082700.18151: *5* rt.AugAssign
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
    #@+node:ekr.20140526082700.18152: *5* rt.BinOp
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
    #@+node:ekr.20140526082700.18153: *5* rt.BoolOp
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
    #@+node:ekr.20140526082700.18154: *5* rt.Break
    def do_Break(self,node):
        
        r = self
        return r.simple_statement('break')
    #@+node:ekr.20140526082700.18155: *5* rt.Call & rt.keyword
    # Call(expr func, expr* args, keyword* keywords, expr? starargs, expr? kwargs)

    def do_Call(self,node):
        
        r = self
        args = [r.visit(z) for z in node.args]
        args.append( # Calls rt.do_keyword.
            join_list([r.visit(z) for z in node.keywords],sep=','))
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
    #@+node:ekr.20140526082700.18156: *6* rt.keyword
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
    #@+node:ekr.20140526082700.18157: *5* rt.ClassDef
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
    #@+node:ekr.20140526082700.18158: *5* rt.Compare
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
    #@+node:ekr.20140526082700.18159: *5* rt.comprehension
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
    #@+node:ekr.20140526082700.18160: *5* rt.Continue
    def do_Continue(self,node):
        
        r = self
        return r.simple_statement('break')
    #@+node:ekr.20140526082700.18161: *5* rt.Delete
    def do_Delete(self,node):
        
        r = self
        return [
            r.div('del nowrap',[
                r.keyword('del'),
                r.visit_list(node.targets,sep=','),
            ]),
        ]
    #@+node:ekr.20140526082700.18162: *5* rt.Dict
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
    #@+node:ekr.20140526082700.18163: *5* rt.Ellipsis
    def do_Ellipsis(self,node):
        
        return '...'
    #@+node:ekr.20140526082700.18164: *5* rt.ExceptHandler
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
    #@+node:ekr.20140526082700.18165: *5* rt.Exec
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
    #@+node:ekr.20140526082700.18166: *5* rt.Expr (New)
    def do_Expr(self,node):
        
        r = self
        return [
            r.div('expr',[
                r.visit(node.value),
            ])
        ]
    #@+node:ekr.20140526082700.18167: *5* rt.For
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
    #@+node:ekr.20140526082700.18168: *5* rt.FunctionDef (uses extra arg)
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
    #@+node:ekr.20140526082700.18169: *5* rt.GeneratorExp
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
    #@+node:ekr.20140526082700.18170: *5* rt.get_import_names
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
    #@+node:ekr.20140526082700.18171: *5* rt.Global
    def do_Global(self,node):
        
        r = self
        return [
            r.div('global nowrap',[
                r.keyword("global"),
                join_list(node.names,sep=','),
            ]),
        ]
    #@+node:ekr.20140526082700.18172: *5* rt.If
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
    #@+node:ekr.20140526082700.18173: *5* rt.IfExp (TernaryOp)
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
    #@+node:ekr.20140526082700.18174: *5* rt.Import
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
    #@+node:ekr.20140526082700.18175: *5* rt.ImportFrom
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
    #@+node:ekr.20140526082700.18176: *5* rt.Lambda
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
    #@+node:ekr.20140526082700.18177: *5* rt.List
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
    #@+node:ekr.20140526082700.18178: *5* rt.ListComp
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
    #@+node:ekr.20140526082700.18179: *5* rt.Module
    def do_Module(self,node):
        
        r = self
        return [
            r.doc(node,"module"),
            r.visit_list(node.body),
        ]
    #@+node:ekr.20140526082700.18180: *5* rt.Name
    def do_Name(self,node):
        
        r = self
        return [
            r.span('name',[
                node.id,
                r.stc_popup_attrs(node),
            ]),
        ]
    #@+node:ekr.20140526082700.18181: *5* rt.Num
    def do_Num(self,node):
        
        r = self
        return r.text(repr(node.n))
        
    #@+node:ekr.20140526082700.18182: *5* rt.Pass
    def do_Pass(self,node):
        
        r = self
        return r.simple_statement('pass')
    #@+node:ekr.20140526082700.18183: *5* rt.Print
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
    #@+node:ekr.20140526082700.18184: *5* rt.Raise
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
    #@+node:ekr.20140526082700.18185: *5* rt.Return
    def do_Return(self,node):
        
        r = self
        return [
            r.div('return nowrap',[
                r.keyword("return"),
                node.value and r.visit(node.value),
            ]),
        ]
    #@+node:ekr.20140526082700.18186: *5* rt.Slice
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
    #@+node:ekr.20140526082700.18187: *5* rt.Str
    def do_Str(self,node):

        '''This represents a string constant.'''
        
        r = self
        assert isinstance(node.s,(str,unicode))
        return [
            r.span("str",[
                r.text(repr(node.s)), ### repr??
            ]),
        ]
    #@+node:ekr.20140526082700.18188: *5* rt.Subscript
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
    #@+node:ekr.20140526082700.18189: *5* rt.TryExcept
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
    #@+node:ekr.20140526082700.18190: *5* rt.TryFinally
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
    #@+node:ekr.20140526082700.18191: *5* rt.Tuple
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
    #@+node:ekr.20140526082700.18192: *5* rt.UnaryOp
    def do_UnaryOp(self,node):
        
        r = self
        op_name = r.op_name(node.op)
        return [
            r.span(op_name.strip(),[
                r.op(op_name,trailing=False),
                r.visit(node.operand),
            ]),
        ]
    #@+node:ekr.20140526082700.18193: *5* rt.While
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
    #@+node:ekr.20140526082700.18194: *5* rt.With
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
    #@+node:ekr.20140526082700.18195: *5* rt.Yield
    def do_Yield(self,node):
        
        r = self
        return [
            r.div('yield nowrap',[
                r.keyword("yield"),
                r.visit(node.value),
            ]),
        ]
    #@-others
#@+node:ekr.20140526082700.18196: *3* class HybridAstTraverser
class HybridAstTraverser(AstTraverser):
    
    # def __init__(self):
        # AstTraverser.__init__(self)
        
    #@+others
    #@+node:ekr.20140526082700.18197: *4* visit
    def visit(self,node,data):
        
        '''Visit a tree using a combination of iteration and recursion.'''
        
        # pylint: disable=W0221
            # Arguments number differs from overridden method.
        
        assert isinstance(node,ast.AST),node.__class__.__name__
        method = getattr(self,'do_'+node.__class__.__name__,self.visit_children)
        return method(node,data)
    #@+node:ekr.20140526082700.18198: *4* visit_children
    def visit_children(self,node,data):
        
        # pylint: disable=W0221
            # Arguments number differs from overridden method.
        
        assert isinstance(node,ast.AST),node.__class__.__name__

        stack = list(self.get_child_nodes(node))
        while stack:
            node2 = stack.pop()
            kind = node2.__class__.__name__
            method = getattr(self,'do_'+kind,None)
            if method:
                # The method is responsible for visiting children.
                data = method(node2,data)
            else:
                # Just push the children.
                stack.extend(list(self.get_child_nodes(node2)))
        return data
    #@-others
#@+node:ekr.20140526082700.18199: *3* class IterativeAstTraverser
class IterativeAstTraverser:
    
    # def __init__(self):
        # pass
        
    #@+others
    #@+node:ekr.20140526082700.18200: *4* iterative.traversers
    #@+node:ekr.20140526082700.18201: *5* private_visit
    def private_visit(self,node):
        
        '''Visit a node and all its descendants *without* using recursion.
        
        Visitor methods should *not* call visit, visit_children or visit_list:
        the visit method visits all nodes automatically.
        '''
        
        trace = False
        nodes=[]
        
        for node in self._iterative_postorder_nodes(node):
            kind = node.__class__.__name__
            if trace: nodes.append(kind)
            method = getattr(self,'do_'+kind,None)
            if method:
                if trace: g.trace(method,node)
                method(node)

        if trace: g.trace('\n'+' '.join(reversed(nodes)))
    #@+node:ekr.20140526082700.18202: *5* _iterative_postorder_nodes
    def _iterative_postorder_nodes(self,node):

        '''Iteratively yield a node and its descendants in post order:
        that is, this yields all descendants of a node before yielding the node.
        
        Adapted from the iterativePostorder algorithm at:
        http://en.wikipedia.org/wiki/Tree_traversal#Postorder
        '''

        marked_nodes = {} # Do *not* alter the AST nodes!
        stack = [node]
        while stack:
            all_visited = True
            for child in self._children(stack[-1]):
                if not marked_nodes.has_key(id(child)):
                    stack.append(child)
                    all_visited = False
            if all_visited:
                node2 = stack.pop()
                marked_nodes[id(node2)]=True
                yield node2
    #@+node:ekr.20140526082700.18203: *5* _children
    def _children(self,node):

        if isinstance(node, ast.Module):
            for node2 in node.body:
                yield node2

        elif isinstance(node,ast.AST) and node._fields is not None:
            for name in node._fields:
                child = getattr(node,name)
                if isinstance(child,list):
                    for node2 in child:
                        if isinstance(node2, ast.AST):
                            yield node2
                elif isinstance(child, ast.AST):
                    yield child
        else:
            raise StopIteration
    #@-others
#@+node:ekr.20140526082700.18204: *3* class Pass1 (AstFullTraverser)
class Pass1 (AstTraverser):
    
    ''' Pass1 traverses an entire AST tree, creating symbol
    tables and context objects, injecting pointers to them
    in the tree. This pass also resolves Python names to
    their proper context, following the rules of section
    4.1, Naming and binding, of the Python langauge
    reference.
    
    Pass1 uses the tree-traversal code from the AstTraverser
    base class. As a result, not all AST nodes need to be
    visited explicitly.
    
    Pass 1 injects the following fields into ast.AST nodes::

    for N in cx: refs_list: N.e = e
    for N in (ast.Class, ast.FunctionDef and ast.Lambda): N.new_cx = new_cx
    For ast.Name nodes N: N.e = e ; N.cx = cx
    For all operator nodes N: N.op_name = <spelling of operator>

    For every context C, Pass 1 sets the following ivars of C:
        C.node                  <node defining C>
        C.ivars_dict            Dictionary of ivars.
                                Keys are names, values are reaching sets (set by SSA pass)
        C.assignments_list      All assignment statements in C
        C.calls_list            All call statements defined in C.
        C.classes_list          All classes defined in C.
        C.defs_list             All functions defined in C.
        C.expressions_list      All Expr nodes in C.
        C.returns_list          All return statements in C.
        C.yields_list           All yield statements in C.
    '''

    #@+others
    #@+node:ekr.20140526082700.18205: *4*  p1.ctor
    def __init__(self):
        
        # Init the base class.
        AstTraverser.__init__(self)
        
        # Abbreviations.
        self.stats = Stats()
        self.u = Utils()
        self.format = u.format
        
        # self.gen_flag = False
            # True: enable code generation (in part of an AST).
            # We generate code only for assignments,
            # returns, yields and function calls.

        self.in_attr = False
            # True: traversing inner parts of an AST.Attribute tree.
    #@+node:ekr.20140526082700.18206: *4*  p1.run (entry point)
    def run (self,root):

        self.visit(root)
    #@+node:ekr.20140526082700.18207: *4*  p1.visit
    def visit(self,node):
        
        """Walk a tree of AST nodes, injecting _parent entries into the tree."""
        
        assert isinstance(node,ast.AST),node.__class__.__name__
        node._parent = self.parents[-1]
        if self.context_stack:
            node.cx = self.context_stack[-1]

        self.level += 1
        self.parents.append(node)

        method_name = 'do_' + node.__class__.__name__
        # stat_name = 'n_' + node.__class__.__name__ + '_nodes'
        method = getattr(self,method_name,None)
        if method:
            # method is responsible for traversing subtrees.
            val = method(node)
        else:
            # Traverse subtrees automatically.
            val = None
            for child in self.get_child_nodes(node):
                val = self.visit(child)
                
        self.level -= 1
        self.parents.pop()
        return val
    #@+node:ekr.20140526082700.18208: *4* p1.helpers
    #@+node:ekr.20140526082700.18209: *5* p1.bind_name
    def bind_name(self,new_cx,old_cx,old_e,name):
        
        trace = False

        new_e = new_cx.st.d.get(name)
        if not new_e:
            # Not an error: name is not defined in new_cx.
            return

        assert old_e
        if old_e == new_e:
            return
            
        if trace and old_e.defs_list:
            g.trace('*****',old_e.defs_list)
            
        if trace:
            g.trace('%22s old_cx: %20s new_cx: %20s' % (name,old_cx,new_cx))

        assert old_cx.st.d.get(name) == old_e
        assert not old_e.defined
        self.stats.n_relinked_names += 1

        # Change all the references to old_e to references to new_e.
        for node in old_e.refs_list:
            kind = self.kind(node)
            assert kind in ('Builtin','Import','ImportFrom','Name'),kind
            setattr(node,'e',new_e)
            self.stats.n_relinked_pointers += 1

        # Merge the reference_lists.
        new_e.refs_list.extend(old_e.refs_list)

        # Relocate the old symbol table entry.
        old_cx.st.d[name] = new_e
    #@+node:ekr.20140526082700.18210: *5* p1.bind_unbound_name
    def bind_unbound_name(self,name,cx):
        
        '''Name has just been bound in context cx.
        
        Bind all matching unbound names in descendant contexts.'''
        
        # Important: this method has little or no effect on overall speed.
        
        # g.trace('*** %10s %s' % (name,cx))
        for cx2 in cx.contexts():
            if cx2 != cx:
                e2 = cx2.st.d.get(name)
                if e2 and not e2.defined:
                    self.bind_name(cx,cx2,e2,name)
    #@+node:ekr.20140526082700.18211: *5* p1.def_args_helper
    # arguments = (expr* args, identifier? vararg, identifier? kwarg, expr* defaults)

    def def_args_helper (self,cx,def_e,node):
        
        assert self.kind(node) == 'arguments'
        self.visit_list(node.args)
        self.visit_list(node.defaults)
        for field in ('vararg','kwarg'): # node.field is a string.
            name = getattr(node,field,None)
            if name:
                e = cx.st.define_name(name)
                self.stats.n_param_names += 1
    #@+node:ekr.20140526082700.18212: *5* p1.get_import_names
    def get_import_names (self,node):

        '''Return a list of the the full file names in the import statement.'''

        result = []

        for ast2 in node.names:

            if self.kind(ast2) == 'alias':
                data = ast2.name,ast2.asname
                result.append(data)
            else:
                g.trace('unsupported kind in Import.names list',self.kind(ast2))

        # g.trace(result)
        return result
    #@+node:ekr.20140526082700.18213: *5* p1.resolve_import_name
    def resolve_import_name (self,spec):

        '''Return the full path name corresponding to the import spec.'''

        trace = False ; verbose = False

        if not spec:
            if trace: g.trace('no spec')
            return ''
        
        ### This may not work for leading dots.
        aList,path,paths = spec.split('.'),None,None

        for name in aList:
            try:
                f,path,description = imp.find_module(name,paths)
                if not path: break
                paths = [path]
                if f: f.close()
            except ImportError:
                # Important: imports can fail due to Python version.
                # Thus, such errors are not necessarily searious.
                if trace: g.trace('failed: %s paths: %s cx: %s' % (
                    name,paths,self.get_context()))
                path = None
                break
                
        if trace and verbose: g.trace(name,path)
                
        if not path:
            if trace: g.trace('no path')
            return ''

        if path.endswith('.pyd'):
            if trace: g.trace('pyd: %s' % path)
            return ''
        else:
            if trace: g.trace('path: %s' % path)
            return path
    #@+node:ekr.20140526082700.18214: *4* p1.visitors
    #@+node:ekr.20140526082700.18215: *5* p1.Assign
    def do_Assign(self,node):
        
        cx = self.get_context()
        self.stats.n_assignments += 1
        self.visit_children(node)
        cx.assignments_list.append(node)
        cx.statements_list.append(node)
    #@+node:ekr.20140526082700.18216: *5* p1.Attribute
    # Attribute(expr value, identifier attr, expr_context ctx)

    def do_Attribute(self,node):

        cx = self.get_context()
        self.stats.n_attributes += 1
        old_attr,self.in_attr = self.in_attr,True
        ctx = self.kind(node.ctx)
        self.visit_children(node)
        self.in_attr = old_attr
        if not self.in_attr:
            base_node = self.attribute_base(node)
            assert base_node
            kind = self.kind(base_node)
            if kind in ('Builtin','Name'):
                base_name = base_node.id
                assert base_node and base_name
                e = cx.st.add_name(base_name)
                e.refs_list.append(base_node)
                ### e.add_chain(base,node) ### ?
            elif kind in ('Dict','List','Num','Str','Tuple',):
                pass
            elif kind in ('BinOp','UnaryOp'):
                pass
            else:
                assert False,kind
    #@+node:ekr.20140526082700.18217: *5* p1.AugAssign
    def do_AugAssign(self,node):
        
        self.stats.n_assignments += 1
        cx = self.get_context()
        
        self.visit_children(node)
        cx.assignments_list.append(node)
        cx.statements_list.append(node)
            
    #@+node:ekr.20140526082700.18218: *5* p1.Call (Stats only)
    # Call(expr func, expr* args, keyword* keywords, expr? starargs, expr? kwargs)

    def do_Call(self,node):
        
        cx = self.get_context()
        self.stats.n_calls += 1
        cx.calls_list.append(node)

        n = len(node.args or []) + int(bool(node.starargs)) + int(bool(node.kwargs))
        d = self.stats.actual_args_dict
        d[n] = 1 + d.get(n,0)

        self.visit_children(node)
    #@+node:ekr.20140526082700.18219: *5* p1.ClassDef
    # ClassDef(identifier name, expr* bases, stmt* body, expr* decorator_list)

    def do_ClassDef (self,node):

        '''Create a context for a class, and
        define the class name in the present context.'''
        
        old_cx = self.get_context()
        name = node.name
        
        # Generate code for the base classes.
        # g.trace([self.format(z) for z in node.bases]) # A list of ast.Name nodes.
        ### bases = self.visit_list(node.bases)
        new_cx = ClassContext(old_cx,name,node,node.bases)
        setattr(node,'new_cx',new_cx) # Bug fix: 2013/01/27

        # Generate code for the class members.
        self.push_context(new_cx)
        self.visit_list(node.body)
        self.pop_context()

        # Define the name in the old context.
        e = old_cx.st.define_name(name)
        e.node = node # 2012/12/25
        node.e = e # 2012/12/25
        # g.trace(e,node)
        e.self_context = new_cx
        old_cx.classes_list.append(new_cx)
        
        # Bind all unbound matching names in inner contexts.
        self.bind_unbound_name(name,new_cx)

    #@+node:ekr.20140526082700.18220: *5* p1.Expr
    # Expr(expr value)

    def do_Expr(self,node):
        
        cx = self.get_context()
        self.visit_children(node)
        self.stats.n_expressions += 1
        cx.expressions_list.append(node)
        cx.statements_list.append(node)
    #@+node:ekr.20140526082700.18221: *5* p1.For
    def do_For(self,node):
        
        cx = self.get_context()
        self.stats.n_fors += 1
        self.visit_children(node)
        cx.statements_list.append(node)
        cx.assignments_list.append(node)
    #@+node:ekr.20140526082700.18222: *5* p1.FunctionDef
    # FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list)

    def do_FunctionDef (self,node):
        
        # Stats
        args = node.args.args
        n = len(args) if args else 0
        d = self.stats.formal_args_dict
        d[n] = 1 + d.get(n,0)

        # Switch to the new context.
        old_cx = self.get_context()
        
        # Define the function/method name in the old context.
        name = node.name
        e = old_cx.st.define_name(name)

        # Create the new context: args are known in the new context.
        new_cx = DefContext(old_cx,name)
        setattr(node,'new_cx',new_cx) # Bug fix.
        setattr(node,'e',e) # Bug fix: 2012/12/28.
        new_cx.node = node
        e.self_context = new_cx
        
        # If this is a method, remember it:
        if old_cx and old_cx.class_context:
            # If this is the ctor, remember it.
            if name == '__init__':
                old_cx.class_context.ctor = new_cx
            # 2013/01/28: Add the method to the ivars dict.
            d = old_cx.class_context.ivars_dict
            if name in d:
                # Not quite a correct error, but something unusual is happening.
                self.error('%20s method hides ivar' % name)
            else:
                aList = d.get(name,[])
                aList.append(node)
                d [name] = aList

        # Define the function arguments before visiting the body.
        # These arguments, including 'self', are known in the body.
        self.push_context(new_cx)
        self.def_args_helper(new_cx,e,node.args)
        self.pop_context()
        
        new_cx.args = node.args # was set by def_args_helper.
        old_cx.defs_list.append(new_cx)

        # Evaluate the body in the new context.
        self.push_context(new_cx)
        self.visit_list(node.body)
        new_cx.node = e.node = node
        self.pop_context()
        
        # Bind all unbound matching names in inner contexts.
        self.bind_unbound_name(name,new_cx)
    #@+node:ekr.20140526082700.18223: *5* p1.Global
    def do_Global(self,node):

        '''Enter the names in a 'global' statement into the *module* symbol table.'''

        cx = self.get_context()
        cx.statements_list.append(node)
        self.stats.n_globals += 1

        for name in node.names:
            
            # Create a symbol table entry for the name in the *module* context.
            module_e = cx.module_context.st.add_name(name)
            
            # This does *not* define the symbol!
            module_e.defined = False
            
            # Both Python 2 and 3 generate SyntaxWarnings when a name
            # is used before the corresponding global declarations.
            # We can make the same assumpution here:
            # give an *error* if an STE appears in this context for the name.
            # The error indicates that scope resolution will give the wrong result.
            e = cx.st.d.get(name)
            if e:
                self.u.error('name \'%s\' used prior to global declaration' % (name))
                # Add the name to the global_names set in *this* context.
                # cx.global_names.add(name)
                
            # Regardless of error, bind the name in *this* context,
            # using the STE from the module context.
            cx.st.d[name] = module_e
    #@+node:ekr.20140526082700.18224: *5* p1.Import
    #@+at From Guido:
    # 
    # import x            -->  x = __import__('x')
    # import x as y       -->  y = __import__('x')
    # import x.y.z        -->  x = __import__('x.y.z')
    # import x.y.z as p   -->  p = __import__('x.y.z').y.z
    #@@c

    def do_Import(self,node):

        '''Add the imported file to u.files_list if needed
        and create a context for the file.'''

        trace = False
        cx = self.get_context()
        cx.statements_list.append(node)
        e_list,names = [],[]
        for fn,asname in self.get_import_names(node):
            fn2 = self.resolve_import_name(fn)
            # Important: do *not* analyze modules not in the files list.
            if fn2:
                mname = self.u.module_name(fn2)
                if g.shortFileName(fn2) in self.u.files_list: 
                    if mname not in self.u.module_names:
                        self.u.module_names.append(mname)
                # if trace: g.trace('%s as %s' % (mname,asname))
                def_name = asname or mname
                names.append(def_name)
                e = cx.st.define_name(def_name) # sets e.defined.
                cx.imported_symbols_list.append(def_name)
                if trace: g.trace('define: (Import) %10s in %s' % (def_name,cx))
                e_list.append(e)

                # Add the constant type to the list of types for the *variable*.
                mod_cx = self.u.modules_dict.get(fn2) or LibraryModuleContext(self.u,fn2)
                e.types_cache[''] = mod_cx.module_type
                self.u.stats.n_imports += 1
            else:
                if trace: g.trace('can not resolve %s in %s' % (fn,cx))

        for e in e_list:
            e.defs_list.append(node)
            e.refs_list.append(node)
    #@+node:ekr.20140526082700.18225: *5* p1.ImportFrom
    #@+at From Guido:
    #     
    # from p.q import x       -->  x = __import__('p.q', fromlist=['x']).x
    # from p.q import x as y  -->  y = __import__('p.q', fromlist=['x']).x
    # from ..x.y import z     -->  z = __import('x.y', level=2, fromlist=['z']).z
    # 
    # All these equivalences are still somewhat approximate; __import__
    # isn't looked up the way other variables are looked up (it is taken
    # from the current builtins), and if the getattr operation in the "from"
    # versions raises AttributeError that is translated into ImportError.
    # 
    # There's also a subtlety where "import x.y" implies that y must be a
    # submodule/subpackage of x, whereas in "from x import y" it may be
    # either a submodule/subpackage or a plain attribute (e.g. a class,
    # function or some other variable).
    #@@c

    def do_ImportFrom(self,node):

        '''Add the imported file to u.files_list if needed
        and add the imported symbols to the *present* context.'''

        trace = False ; dump = False
        if trace and dump:
            self.u.dump_ast(node)
            
        u = self.u
        cx = self.get_context()
        cx.statements_list.append(node)
        m = self.resolve_import_name(node.module)
        
        if m and m not in self.u.files_list:
            if trace: g.trace('adding module',m)
            self.u.files_list.append(m)

        e_list,names = [],[]
        for fn,asname in self.get_import_names(node):
            fn2 = asname or fn
            if fn2 == '*':
                if trace: g.trace('From x import * not ready yet')
                return
            names.append(fn2)
            e = cx.st.add_name(fn2)
            cx.imported_symbols_list.append(fn2)
            e_list.append(e)
            if trace: g.trace('define: (ImportFrom) %s' % (fn2))
            # Get the ModuleContext corresponding to fn2.
            mod_cx = self.u.modules_dict.get(fn2)
            ###
            ### if not mod_cx:
            ###    self.u.modules_dict[fn2] = mod_cx = ModuleContext(fn2)
            if mod_cx:
                # module_type is the singleton *constant* type of the module.
                module_type = mod_cx.module_type
                # Add the constant type to the list of types for the *variable*.
                e.defined = True # Indicate there is at least one definition.
                e.types_cache[''] = mod_cx.module_type
                mname = u.module_name(fn2)
                ### if mname not in self.u.module_names:
                ###    self.u.module_names.append(mname)
                u.stats.n_imports += 1

        for e in e_list:
            e.defs_list.append(node)
            e.refs_list.append(node)
    #@+node:ekr.20140526082700.18226: *5* p1.Interactive
    def do_Interactive(self,node):
        
        assert False,'Interactive context not supported'
    #@+node:ekr.20140526082700.18227: *5* p1.Lambda
    def do_Lambda (self,node):
        
        old_cx = self.get_context()

        # Synthesize a lambda name in the old context.
        # This name must not conflict with split names of the form name@n.
        old_cx.n_lambdas += 1
        name = 'Lambda@@%s' % old_cx.n_lambdas
        e = old_cx.st.define_name(name)

        # Define a namespace for the 'lambda' variables.
        new_cx = LambdaContext(self.u,old_cx,name)
        setattr(node,'new_cx',new_cx)
        setattr(node,'e',e) # Bug fix: 2012/12/28.
        new_cx.node = node
        
        self.push_context(new_cx)
        def_e = None
        args = self.def_args_helper(new_cx,def_e,node.args)
        body = self.visit(node.body)
        self.pop_context()
    #@+node:ekr.20140526082700.18228: *5* p1.ListComp
    def do_ListComp(self,node):
        
        self.stats.n_list_comps += 1
        self.visit_children(node)

        cx = self.get_context()
        cx.assignments_list.append(node)
    #@+node:ekr.20140526082700.18229: *5* p1.Module
    def do_Module (self,node):

        # Get the module context from the global dict if possible.
        
        # Bug fix: treat all <string> files as separate modules.
        new_cx = None if self.fn == '<string>' else self.u.modules_dict.get(self.fn)

        if not new_cx:
            new_cx = ModuleContext(self.u,self.fn,node)
            self.u.modules_dict[self.fn] = new_cx
            
        new_cx.node = node

        self.push_context(new_cx)
        self.visit_list(node.body)
        self.pop_context()
        
        # Bind all unbound matching names in inner contexts.
        for name in sorted(new_cx.st.d.keys()):
            self.bind_unbound_name(name,new_cx)
    #@+node:ekr.20140526082700.18230: *5* p1.Name
    def do_Name(self,node):

        trace = False
        cx  = self.get_context()
        ctx = self.kind(node.ctx)
        name = node.id
        
        # Create the symbol table entry, even for builtins.
        e = cx.st.add_name(name)
        setattr(node,'e',e)
        setattr(node,'cx',cx)
        
        def_flag,ref_flag=False,False
        
        if ctx in ('AugLoad','AugStore','Load'):
            # Note: AugStore does *not* define the symbol.
            e.referenced = ref_flag = True
            self.stats.n_load_names += 1
        elif ctx == 'Store':
            # if name not in cx.global_names:
            e.defined = def_flag = True
            if trace: g.trace('Store: %s in %s' % (name,cx))
            self.stats.n_store_names += 1
        elif ctx == 'Param':
            if trace: g.trace('Param: %s in %s' % (name,cx))
            e.defined = def_flag = True
            self.stats.n_param_refs += 1
        else:
            assert ctx == 'Del',ctx
            e.referenced = ref_flag = True
            self.stats.n_del_names += 1

        if isPython3:
            if name in self.u.module_names:
                return None
        else:
            if name in dir(__builtin__) or name in self.u.module_names:
                return None

        if not self.in_attr:
            if def_flag: e.defs_list.append(node)
            if ref_flag: e.refs_list.append(node)
    #@+node:ekr.20140526082700.18231: *5* p1.Return
    def do_Return(self,node):
        
        self.stats.n_returns += 1
        cx = self.get_context()
        if getattr(node,'value'):
            self.visit(node.value)
        cx.returns_list.append(node)
        cx.statements_list.append(node)
        # g.trace('%s %s' % (cx.name,self.format(node)))
    #@+node:ekr.20140526082700.18232: *6* p1.Operators...
    # operator = Add | BitAnd | BitOr | BitXor | Div
    # FloorDiv | LShift | Mod | Mult | Pow | RShift | Sub | 

    def do_Add(self,node):       setattr(node,'op_name','+')
    def do_BitAnd(self,node):    setattr(node,'op_name','&')
    def do_BitOr(self,node):     setattr(node,'op_name','|')
    def do_BitXor(self,node):    setattr(node,'op_name','^')
    def do_Div(self,node):       setattr(node,'op_name','/')
    def do_FloorDiv(self,node):  setattr(node,'op_name','//')
    def do_LShift(self,node):    setattr(node,'op_name','<<')
    def do_Mod(self,node):       setattr(node,'op_name','%')
    def do_Mult(self,node):      setattr(node,'op_name','*')
    def do_Pow(self,node):       setattr(node,'op_name','**')
    def do_RShift(self,node):    setattr(node,'op_name','>>')
    def do_Sub(self,node):       setattr(node,'op_name','-')

    # boolop = And | Or
    def do_And(self,node):       setattr(node,'op_name',' and ')
    def do_Or(self,node):        setattr(node,'op_name',' or ')

    # cmpop = Eq | Gt | GtE | In |
    # Is | IsNot | Lt | LtE | NotEq | NotIn
    def do_Eq(self,node):        setattr(node,'op_name','==')
    def do_Gt(self,node):        setattr(node,'op_name','>')
    def do_GtE(self,node):       setattr(node,'op_name','>=')
    def do_In(self,node):        setattr(node,'op_name',' in ')
    def do_Is(self,node):        setattr(node,'op_name',' is ')
    def do_IsNot(self,node):     setattr(node,'op_name',' is not ')
    def do_Lt(self,node):        setattr(node,'op_name','<')
    def do_LtE(self,node):       setattr(node,'op_name','<=')
    def do_NotEq(self,node):     setattr(node,'op_name','!=')
    def do_NotIn(self,node):     setattr(node,'op_name',' not in ')

    # unaryop = Invert | Not | UAdd | USub
    def do_Invert(self,node):   setattr(node,'op_name','~')
    def do_Not(self,node):      setattr(node,'op_name',' not ')
    def do_UAdd(self,node):     setattr(node,'op_name','+')
    def do_USub(self,node):     setattr(node,'op_name','-')
    #@+node:ekr.20140526082700.18233: *5* p1.With
    def do_With(self,node):
        
        cx = self.get_context()
        self.stats.n_withs += 1
        self.visit_children(node)
        cx.statements_list.append(node)
    #@-others
#@+node:ekr.20140526082700.18234: *3* class Resolver (keep for now)
class Resolver:
    
    '''A class controlling the resolution pattern matchers.'''

    #@+others
    #@+node:ekr.20140526082700.18235: *4*  r.ctor & helper
    def __init__(self):
        
        self.app = app
        self.format = app.format
        self.sd = app.sd

        # g.trace('(Resolver)',g.callers())
        
        # Singleton type objects.
        # self.num_type = Num_Type()
        self.string_type = String_Type()

        # Data created in Pass 1...
        self.constants_list = []
            # List of all constant ops.
            
        # Data created just after scope resolution...
        self.self_list = []
            # List of all instances of self within methods.
        
        # The main lists for the main algorithm.
        self.known_symbols_list = []
            # The list of symbols whose types are definitely known.
            # The main algorithm pops symbols off this list.
        self.mushy_ops_list = []
            # Ops with mushy type sets. Debugging only?
        self.mushy_ste_list = []
            # The lists of symbols that would have mushy type sets.
            # The hard part of resolution deals with such symbols.
       
        self.calls_d = {}
            # Keys are contexts, values are list of calls in the context.
        self.defs_d = {} # The global defs dict.
            # Keys are names; values are sets of Contexts
        self.refs_d = {} # The global refs dict.
            # The global dictionary.
            # Keys are names.  Values are sets of contexts.

        # Class info dicts: keys and values are contexts.
        self.class_supers_d = {} # All superclasses.
        self.class_sub_d = {}  # All subclasses.
        self.class_relatives_d = {}
            # All super and subclasses, as well as other related classes.
            
        # Create the dispatch dict.
        self.dispatch_dict = self.make_dispatch_dict()
    #@+node:ekr.20140526082700.18236: *4*  r.generators
    #@+node:ekr.20140526082700.18237: *5* r.classes
    def classes (self):
        
        '''A generator yielding all class contexts in all modules.'''
        
        r = self
        for cx in r.contexts():
            if cx.kind == 'class':
                yield cx
    #@+node:ekr.20140526082700.18238: *5* r.contexts
    def contexts (self):
        
        '''A generator yielding all contexts in all modules.'''
        
        r = self
        for m in r.modules():
            for cx in m.contexts():
                yield cx
    #@+node:ekr.20140526082700.18239: *5* r.modules
    def modules (self):
        
        d = self.sd.modules_dict
        for fn in sorted(d.keys()):
            m = d.get(fn)
            yield m
    #@+node:ekr.20140526082700.18240: *5* r.statements
    def statements(self):
        
        '''A generator yielding all statements in all modules, in the proper order.'''

        r = self
        
        for cx in r.modules():
            for op in cx.statements():
                yield op
    #@+node:ekr.20140526082700.18241: *5* r.unresolved_names (TEST)
    def unresolved_names(self):
        
        r = self
        for cx in r.contexts():
            for e in cx.st.d.values():
                if not e.resolved:
                    yield e
    #@+node:ekr.20140526082700.18242: *4* r.resolve & initers
    def resolve (self):
        
        trace_time = False
        r = self
        
        if trace_time: t1 = time.time()
        
        # Init & do scope resolution.
        r.make_global_dicts()
        
        if trace_time:
            t2 = time.time()
            g.trace('make dicts & resolve scopes: %2.2f sec' % (t2-t1))
        
        # Add 'self', module names and class names to list of known symbols.
        r.init_self()
        
        if trace_time:
            t3 = time.time()
            g.trace('init_self: %2.2f sec' % (t3-t2))
            
        r.init_module_names()
        
        if trace_time:
            t4 = time.time()
            g.trace('init_module_names: %2.2f sec' % (t4-t3))
            
        r.init_class_names()
        
        if trace_time:
            t5 = time.time()
            g.trace('init_class_names: %2.2f sec' % (t5-t4))
        
        r.known_symbols_list.extend(r.self_list)
        r.known_symbols_list.extend(r.constants_list)
        
        # Run the main algorithm.
        r.main_algorithm()
        
        r.resolve_aliases()
        r.resolve_class_relationships()
        r.analyze_classes()
        r.resolve_ivars()
        
        # The table of type-resolution methods.
        table = (
        )

        # Do the main, iterative, peepholes.
        progress = True
        while progress:
            progress = False
            for f in table:
                progress = progress or f()
                
        # Do the final peepholes.
        
        if trace_time:
            t6 = time.time()
            g.trace('main algorithm: %2.2f sec' % (t6-t5))
    #@+node:ekr.20140526082700.18243: *5* r.init_class_names
    def init_class_names(self):
        
        '''Mark all refereces to class names as known.'''
        
        trace = False
        r = self
        format = self.format
        
        # Step 1: Create a dict whose keys are class names and whose values are lists of STE's.
        # Using a dict instead of a list speeds up the code by a factor of more than 300.
        # For all the files of Leo: 30 sec. for the old way and 0.08 sec. the new way.
        e_dict = {}
        for cx in r.classes():
            cx.class_type = Class_Type(cx) # Do this after scope resolution.
            parent = cx.parent_context
            if parent:
                d = parent.st.d
                e = d.get(cx.name)
                if e:
                    key = e.name
                    aList = e_dict.get(key,[])
                    if e not in aList:
                        aList.append(e)
                            # Use a list to disambiguate classes with the same name.
                        e_dict[key] = aList

        # Step 2: Mark all Name ops refering to class names as knowns.
        for cx in r.contexts():
            d = cx.st.d
            for e in d.values():
                for op in e.refs_list:
                    kind = op.__class__.__name__
                    if kind == 'Builtin':
                        pass ### Not ready yet.
                    elif kind == 'Name':
                        e = op.e
                        if e.name in e_dict:
                            aList = e_dict.get(e.name)
                            assert aList
                            if e in aList:
                                if trace: g.trace('known Name',e,op,op._parent,cx)
                                r.known_symbols_list.append(op)
                    elif kind == 'Import':
                        aList = op.e_list
                        for e in aList:
                            if e.name in e_dict:
                                aList = e_dict.get(e.name)
                                assert aList
                                if e in aList:
                                    if trace: g.trace('known Import',e,op,op._parent,cx)
                                    r.known_symbols_list.append(op)
                    elif kind == 'ImportFrom':
                        if trace: g.trace('ImportFrom not ready yet: %s' % (
                            format(op)))
                    else:
                        assert False,'Unexpected Op: %s' % kind
    #@+node:ekr.20140526082700.18244: *5* r.init_module_names
    def init_module_names(self):
        
        trace = False
        r,sd = self,self.sd
        format = self.format
        
        # Step 1: Create a dict whose keys are module names and whose values are lists of STE's.
        e_dict = {}
        for fn in sd.modules_dict:
            m = sd.modules_dict.get(fn)
            if trace: g.trace(m)
        # module_names = self.u.module_names
        # e_dict = {}
        # for cx in r.classes():
            # d = cx.st.d
            # e = d.get(cx.name)
            # if e:
                # key = e.name
                # aList = e_dict.get(key,[])
                # if e not in aList:
                    # aList.append(e)
                        # # Use a list to disambiguate classes with the same name.
                    # e_dict[key] = aList
                    
        if trace: g.trace(e_dict)

        # Step 2: Mark all Name ops refering to class names as knowns.
        for cx in r.contexts():
            d = cx.st.d
            for e in d.values():
                for op in e.refs_list:
                    kind = op.__class__.__name__
                    if kind in ('Builtin','Name'):
                        e = op.e
                        if e and e.name in e_dict:
                            aList = e_dict.get(e.name)
                            assert aList
                            if e in aList:
                                if trace: g.trace('known',e,op,op._parent,cx)
                    elif kind == 'Import':
                        aList = op.e_list
                        for e in aList:
                            if e.name in e_dict:
                                aList2 = e_dict.get(e.name)
                                assert aList2
                                if e in aList2:
                                    if trace: g.trace('known',e,op,op._parent,cx)
                    elif kind == 'ImportFrom':
                        if trace: g.trace('ImportFrom not ready yet: %s' % (
                            format(op)))
                    else:
                        assert False,'Unexpected Op: %s' % kind
    #@+node:ekr.20140526082700.18245: *5* r.init_self
    def init_self (self):
        
        '''Add all instances of "self" to r.self.list.'''

        r = self
        for class_ in r.classes():
            for def_ in class_.defs():
                e = def_.st.d.get('self')
                if e:
                    if len(e.defs_list) > 1:
                        g.trace('*** redefining self',e.defs_list)
                    else:
                        r.self_list.extend(e.refs_list)
    #@+node:ekr.20140526082700.18246: *5* r.main_algorithm
    def main_algorithm(self):
        
        r = self
        
        # g.trace('known symbols: %s' % (len(r.known_symbols_list)))
        
        while r.known_symbols_list:
            op = r.known_symbols_list.pop()
            r.make_known(op)
    #@+node:ekr.20140526082700.18247: *5* r.make_global_dicts
    def make_global_dicts (self):
        
        contexts = 0
        r = self
        r.refs_dict = {}
        for m in r.modules():
            for cx in m.contexts():
                contexts += 1
                d = cx.st.d # Keys are names, values are STEs.
                for e in d.values():
                    aSet = r.refs_dict.get(e.name,set())
                    if cx not in aSet:
                        aSet.add(cx)
                        r.refs_dict[e.name] = aSet
                        
        # r.defs_dict contains entries only for defined names.
        r.defs_dict = {}
        for name in r.refs_dict.keys():
            aSet = r.refs_dict.get(name)
            defs = [cx for cx in aSet if cx.st.d.get(name).defined]
            r.defs_dict[name] = defs

        # g.trace('contexts: %s' % (contexts))
    #@+node:ekr.20140526082700.18248: *5* r.make_known & op handlers
    def make_known(self,op):
        
        '''This is called from the main_algorithm.
        op is an Op representing a name or constant with a single, known type.
        '''

        r = self
        # g.trace('known: %s parent: %s' % (op,op._parent))
        
        if 0:
            g.trace('%10s %9s %-8s %8s %s' % (
                op,id(op),
                op.__class__.__name__,
                op._parent and op._parent.__class__.__name__,op._parent))

        return ###
        # if op._parent:
            # f = r.dispatch_dict.get(op.parent.kind)
            # if f:
                # f(op.parent)
            # else:
                # g.trace('bad op.parent.kind: %s' % op.parent.kind)
                # g.trace(op)
                # assert False
    #@+node:ekr.20140526082700.18249: *6* Do-nothings (not used at present)
    if 0:
        #@+others
        #@+node:ekr.20140526082700.18250: *7* r.Arg
        def do_Arg (self,op):
            
            # arg = op.arg
            pass
        #@+node:ekr.20140526082700.18251: *7* r.Arguments
        def do_Arguments (self,op):
            
            # args     = [self.visit(z) for z in op.args]
            # defaults = [self.visit(z) for z in op.defaults]
            pass
        #@+node:ekr.20140526082700.18252: *7* r.AugAssign
        def do_AugAssign(self,op):
            
            # This does not define any value!
            pass
        #@+node:ekr.20140526082700.18253: *7* r.Keyword
        def do_Keyword(self,op):
            
            # arg   = op.arg
            # value = op.value
            pass
        #@-others
    #@+node:ekr.20140526082700.18254: *6* Known types
    #@+node:ekr.20140526082700.18255: *7* r.Bytes
    def do_Bytes(self,op):

        value = op.value
        # g.trace(value)
    #@+node:ekr.20140526082700.18256: *7* r.Dict
    def do_Dict(self,op):

        keys   = op.keys
        values = op.values
        # g.trace(keys,values)
    #@+node:ekr.20140526082700.18257: *7* r.List
    def do_List(self,op):

        elts = op.elements
        # g.trace(elts)
    #@+node:ekr.20140526082700.18258: *7* r.Num
    def do_Num(self,op):
        
        n = op.n
        # g.trace(n)
    #@+node:ekr.20140526082700.18259: *7* r.Str
    def do_Str(self,op):
        
        '''This represents a string constant.'''

        s = op.s
        # g.trace(s)
        
    #@+node:ekr.20140526082700.18260: *7* r.Tuple
    def do_Tuple (self,op):
        
        elts = op.elements
        # g.trace(elts)
    #@+node:ekr.20140526082700.18261: *6* Names & Builtins
    #@+node:ekr.20140526082700.18262: *7* r.Builtin
    def do_Builtin(self,op):
        
        name = op.name
        # g.trace(name)
    #@+node:ekr.20140526082700.18263: *7* r.Name
    def do_Name(self,op):
        
        name = op.name
        # g.trace(name)
    #@+node:ekr.20140526082700.18264: *6* Not ready yet
    #@+node:ekr.20140526082700.18265: *7* r.Comprehension
    def do_Comprehension(self,op):

        result = []
        
        name  = op.name
        iter_ = op.it
        ifs   = op.ifs
        # g.trace(name,iter_,ifs)
    #@+node:ekr.20140526082700.18266: *7* r.GenExp
    def do_GenExp (self,op):
        
        elt  = op.elt
        gens = op.generators
        # g.trace(elt,gens)
    #@+node:ekr.20140526082700.18267: *7* r.Index
    def do_Index(self,op):
        
        index = op.index
        # g.trace(index)
    #@+node:ekr.20140526082700.18268: *7* r.ListComp
    def do_ListComp(self,op):

        elt  = op.elt
        gens = op.generators
        # g.trace(elt,gens)
    #@+node:ekr.20140526082700.18269: *7* r.Slice
    def do_Slice(self,op):
        
        upper = op.upper
        lower = op.lower
        step  = op.step
        # g.trace(upper,lower,step)
    #@+node:ekr.20140526082700.18270: *7* r.Subscript
    def do_Subscript(self,op):

        value  = op.value
        slice_ = op.slice_
        # g.trace(value,slice_)
    #@+node:ekr.20140526082700.18271: *6* Operators
    #@+node:ekr.20140526082700.18272: *7* r.Attribute
    def do_Attribute (self,op):
        
        value = op.value
        attr  = op.attr
        # g.trace(attr,value)
    #@+node:ekr.20140526082700.18273: *7* r.BinOp
    def do_BinOp(self,op):
        
        trace = True
        r = self
        name = op.op_name
        lt   = op.lt
        rt   = op.rt
        assert lt.parent == op
        assert rt.parent == op
        assert op.n_unknowns > 0
        op.n_unknowns -= 1
        if op.n_unknowns > 0: return
        
        ### Testing only.
        if not lt.typ or not rt.typ:
            # if trace: g.trace('missing typ: %s' % op)
            return ###

        assert lt.typ,op
        assert rt.typ,op
        
        if len(lt.typ) == 1 and len(rt.typ):
            lt_type,rt_type = lt.typ[0],rt.typ[0]
            if lt_type == rt_type:
                op.typ = [lt_type]
            # elif lt_type == r.string_type and rt_type == r.num_type:
                # op.typ = [r.string_type]
            else:
                #### Unusual case.
                op.typ.extend(lt.typ)
                op.typ.extend(rt.typ)
        else:
            # Mushy cases.
            op.typ.extend(lt.typ)
            op.typ.extend(rt.typ)
            op.typ = list(set(op.typ))

        if trace and len(op.typ) > 1:
            g.trace('ambiguous: %s%s%s %s' % (lt,name,rt,op.typ))
        
        assert op.typ,'empty op.typ'
        
        if len(op.typ) == 1:
            r.make_known(op)
        else:
            # if trace:
                # g.trace('lt',lt.typ)
                # g.trace('rt',rt.typ)
            r.mushy_ops_list.append(op)
    #@+node:ekr.20140526082700.18274: *7* r.BoolOp
    def do_BoolOp(self,op):
        
        name   = op.op_name
        values = op.values
        # g.trace(name,values)
    #@+node:ekr.20140526082700.18275: *7* r.Call
    def do_Call (self,op):
        
        pass

        # args     = op.args    
        # func     = op.func
        # keyargs  = op.keywords
        # starargs = op.starargs
        # star2args = op.starstarargs
        
        ### We have to know the type of the return value to do anything useful.
        # g.trace(op)
        
        
        
       
    #@+node:ekr.20140526082700.18276: *7* r.CompareOp
    def do_CompareOp(self,op):

        left  = op.left
        ops   = op.ops
        comps = op.comparators
        # g.trace(left,ops,comps)
    #@+node:ekr.20140526082700.18277: *7* r.TernaryOp
    def do_TernaryOp(self,op):

        test   = op.test
        body   = op.body
        orelse = op.orelse
        # g.trace(test,body,orelse)
    #@+node:ekr.20140526082700.18278: *7* r.UnaryOp
    def do_UnaryOp(self,op):
        
        name    = op.op_name
        operand = op.operand
        # g.trace(name,operand)
    #@+node:ekr.20140526082700.18279: *6* r.Assign
    def do_Assign(self,op):
        
        trace = False
        r = self
        target = op.target
        value  = op.value
        assert target.parent == op
        assert value.parent == op
        assert repr(op) == '%s=%s' % (target,value)

        if target.kind == 'Name':
            e = target.e
            defs = e.defs_list
            e.defs_seen += 1

            # Append the new types to e.typ.
            changed = False
            for z in value.typ:
                if z not in e.typ:
                    e.typ.append(z)
                    changed = True
            if not changed:
                if trace: g.trace('unchanged: %s %s' % (e,e.typ))
                return
                    
            # The symbol's type is unambiguously known if
            # a) all defs have been seen and 
            # b) e.type_list has exactly one symbol.
            val = value.typ[0]
            if e.defs_seen == len(defs) and len(value.typ) == 1:
                if trace:
                    g.trace('known: %s=%s refs: %s' % (
                        target,val,[z.parent for z in e.refs_list]))
                assert target not in r.known_symbols_list
                # Push all the references to the newly-known symbol.
                r.known_symbols_list.extend(e.refs_list)
                # Add the new value to all Ops in e.refs_list.
                for op in e.refs_list:
                    op.typ.append(val)
            else:
                if trace: g.trace('add: %s=%s' % (target,value.typ[0]))
                # Add the new value to all Ops in e.refs_list.
                for op in e.refs_list:
                    op.typ.append(val)

            if len(e.typ) > 1:
                if trace: g.trace('mushy: %s=%s' % (target,e.typ))
                if e not in r.mushy_ste_list:
                    r.mushy_ste_list.append(e)
                        ### This could be expensive.
                        ### It would be better to make this a per-context list.
        else:
            # assert False,'Unexpected target kind: %s' % target.kind
            if trace: g.trace('unexpected target kind: %s %s' % (target.kind,target))
    #@+node:ekr.20140526082700.18280: *6* r.do_nothing
    def do_nothing(self,op):
        pass
        
        # g.trace(op)
    #@+node:ekr.20140526082700.18281: *4* The hard part
    #@+node:ekr.20140526082700.18282: *5* r.analyze_assignments (to do)
    def analyze_assignments (self):
        
        r = self
        if 0: ### Old unit test...
            for m in r.modules():
                result = []
                for cx in m.contexts():
                    n = len(cx.parent_contexts())
                    pad,pad2 = ' '*n,' '*(n+1)
                    result.append('%s%s' % (pad,cx))
                    if 0:
                        result2 = []
                        for z in cx.assignments_list:
                            result2.append('%s%s' % (
                                pad2,
                                self.format(z.op).strip()))
                        result.extend(sorted(list(set(result2))))
                    if 1:
                        result2 = []
                        for z in cx.returns_list:
                            result2.append('%s%s' % (
                                pad2,
                                self.format(z).strip()))
                        result.extend(sorted(list(set(result2))))
    #@+node:ekr.20140526082700.18283: *5* r.analyze_calls (to do)
    def analyze_calls (self):
        
        pass
    #@+node:ekr.20140526082700.18284: *5* r.analyze_returns (To do)
    def analyze_returns(self):
        
        r = self
        result = []
        # g.trace()
        for m in r.modules():
            for cx in m.defs():
                # print(cx.name)
                result.append(cx.name)
                for a in sorted(set(cx.assignments_list)):
                    # print(' %s' % (a))
                    result.append(' %s' % (a))
        # g.trace('end')
        
        return '\n'.join(result)
                
    #@+node:ekr.20140526082700.18285: *5* r.resolve_class_relationships
    def resolve_class_relationships (self):
        
        r = self
        
        # Class info dicts: keys and values are contexts.
        r.class_supers_d = {} # All superclasses.
        r.class_sub_d = {}  # All sukbclasses.
        r.class_relatives_d = {}
            # All super and subclasses, as well as other related classes.

        excluded_names = ('object',)
        r_d = r.class_relatives_d
        
        return #### Rewrite

        # for m in r.modules():
            # for cx in m.contexts():
                # if cx.kind == 'class' and cx.name not in excluded_names:
                    # hash1 = cx.name
                    # aSet = r_d.get(hash1,set())
                    # for cx2 in cx.bases:
                        # hash2 = repr(cx2)
                        # aSet2 = r_d.get(hash2,set())
                        # aSet2.add(cx)
                        # aSet.add(cx2)
                        # r_d[hash2] = aSet2
                    # r_d[hash1] = aSet
    #@+node:ekr.20140526082700.18286: *5* r.analyze_classes & helpers
    def analyze_classes(self,aList=None):
        
        trace = False
        r = self

        if aList:
            # Convert names to classes.
            aList = sorted([z for z in r.classes() if z.name in aList])
        else:
            aList = sorted([z for z in r.classes()])

        for cx1 in aList:
            if trace:
                print('%20s %s' % (cx1.name,cx1.bases))
            # for cx2 in aList:
                # r.analyze_class_pair(aList,cx1,cx2)
        
        # for cx in sorted(aList):
            # g.trace(cx.name)

        # g.trace(len(aList))
        
        return aList
    #@+node:ekr.20140526082700.18287: *6* r.analyze_class_pair
    def analyze_class_pair(self,aLisst,cx1,cx2):
        
        r = self
        if cx1 == cx2:
            return
            
        print('  %s: %s' % (cx2.name,cx2.bases))
        # print('    subclass: %s' % (cx2.name in cx1.bases))
        
    #@+node:ekr.20140526082700.18288: *5* r.resolve_ivars
    def resolve_ivars (self):
        
        r = self
        
        if 0: ###
        
            constants = ('Dict','Int','List','Num','Str','Tuple',)

            g.trace()
        
            trace = True
            
            for m in self.modules():
                g.trace(m)
                for class_ in m.classes():
                    for def_ in class_.defs():
                        for op in def_.assignments_to('self'):
                            target = op.target
                            value  = op.value
                            kind = op.__class__.__name__
                            if trace:
                                g.trace(op)
                                g.trace(self.format(op))
                                
                            val = PatternFormatter().visit(value) ### g_pattern_formatter.visit(value)
                            if val in constants:
                                if trace: g.trace('found constant type: %s' % val)
                                if kind == 'Assign':
                                    print('%s=%s\n' % (target,val))
                                        # To do: add constant type for the ste for target.
                                else:
                                    assert kind=='AugAssign',kind
                                    print('%s=%s\n' % (target,val))
    #@+node:ekr.20140526082700.18289: *5* r.resolve_aliases (will be removed)
    def resolve_aliases (self):
        
        r = self
    #@-others
#@+node:ekr.20140526082700.18290: *3* class ScopeBinder
# Running ScopeBinder on all Leo files:
# 1.25sec when this class is a subclass of AstTraverser
# 0.75sec when this class is a subclass of AstFullTraverser.

class ScopeBinder(AstFullTraverser):
    
    '''Resolve all symbols to the scope in which they are defined.
    
    This pass is invoked by P1; it must run after P1 has injected
    all fields into the trees and discovered all definitions.
    '''
    
    def __init__(self):
        AstFullTraverser.__init__(self)
        self.init_dicts()
        self.u = Utils()

    #@+others
    #@+node:ekr.20140526082700.18291: *4* sb.check & helper
    def check(self,fn,root):
        trace = True and not g.app.runningAllUnitTests
        u = self.u
        for cx in u.contexts(root):
            assert hasattr(cx,'stc_context'),cx
            result = []
            self.check_context(cx,result)
            if trace and result:
                result=sorted(set(result))
                pad = ' '*u.compute_node_level(cx)
                result.insert(0,'%s%s' % (pad,u.format(cx)))
                if fn:
                    result.insert(0,fn)
                for s in result:
                    print(s)
    #@+node:ekr.20140526082700.18292: *5* check_context
    def check_context(self,cx,result):
        
        trace = False
        u = self.u
        for statement in u.local_statements(cx):
            if trace:
                pad = ' '*u.compute_node_level(statement)
                print(pad+u.format(statement))
            for node in u.local_nodes(statement):
                # if trace:print(' %s%s: %s' % (pad,node.__class__.__name__,u.format(node)))
                if isinstance(node,ast.Name):
                    key = node.id
                    def_cx = getattr(node,'stc_scope')
                    if def_cx:
                        d = def_cx.stc_symbol_table
                        aSet = d.get('*defined*')
                        if key not in aSet:
                            # UnboundLocalError: no definition in scope.
                            pad = ' '*u.compute_node_level(statement)
                            result.append(' %s*%s %s: %s' % (
                                pad,u.format(node.ctx),key,u.format(statement)))
                    else:
                        d = self.lookup(cx,key)
                        if d:
                            assert d.has_key(key),repr(key)
                        else:
                            # No scope.
                            pad = ' '*u.compute_node_level(statement)
                            result.append(' %s+%s %s: %s' % (
                                pad,u.format(node.ctx),key,u.format(statement)))
    #@+node:ekr.20140526082700.18293: *4* sb.dump_symbol_table
    def dump_symbol_table(self,node):
        
        if getattr(node,'stc_symbol_table',None):
            d = node.stc_symbol_table
            for key in sorted(d.keys()):
                name = d.get(key)
                print('%s:%s' % (self.format(name.ctx),name.id))
    #@+node:ekr.20140526082700.18294: *4* sb.init_dicts
    def init_dicts(self):
        
        self.builtins_d = dict([(z,z) for z in __builtins__])

        table = (
            '__builtins__',
            '__file__',
            '__path__',
            '__repr__',
        )
        self.special_methods_d = dict([(z,z) for z in table])
    #@+node:ekr.20140526082700.18295: *4* sb.lookup
    def lookup(self,cx,key):
        
        '''Return the symbol table for key, starting the search at node cx.'''
        
        trace = False and not g.app.runningAllUnitTests
        assert isinstance(cx,(ast.Module,ast.ClassDef,ast.FunctionDef,ast.Lambda)),cx
        cx2 = cx
        while cx2:
            st = cx.stc_symbol_table
            if key in st.d.keys():
                return st.d
            else:
                cx2 = cx2.stc_context
                assert isinstance(cx,(ast.Module,ast.ClassDef,ast.FunctionDef,ast.Lambda)),cx
        for d in (self.builtins_d,self.special_methods_d):
            if key in d.keys():
                return d
        else:
            if trace:
                g.trace('** (ScopeBinder) no definition for %20s in %s' % (
                    key,self.u.format(cx)))
            return None
    #@+node:ekr.20140526082700.18296: *4* sb.run
    def run (self,fn,root):

        self.fn = g.shortFileName(fn)
        self.n_resolved = 0
        self.n_visited = 0
        self.visit(root)
        if 0:
            self.check(fn,root)
            # g.trace('ScopeBinder visited %s nodes' % self.n_visited)
    #@+node:ekr.20140526082700.18297: *4* sb.visit & visitors
    def visit(self,node):

        # assert isinstance(node,ast.AST),node.__class__.__name__
        method = getattr(self,'do_' + node.__class__.__name__)
        self.n_visited += 1
        return method(node)
    #@+node:ekr.20140526082700.18298: *5* sb.FunctionDef
    # FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list)

    def do_FunctionDef (self,node):
        
        self.visit(node.args)
        for z in node.body:
            self.visit(z)
        for z in node.decorator_list:
            self.visit(z)
      
    #@+node:ekr.20140526082700.18299: *5* sb.Name
    # Name(identifier id, expr_context ctx)

    def do_Name(self,node):
        
        '''Set node.stc_scope for all references to names.'''
        
        trace = False and not g.app.runningAllUnitTests

        # if isinstance(node.ctx.__class__,ast.Param):# 
            # assert node.stc_scope is not None,node
                # P1 has defined the scope.
        # elif isinstance(node.ctx,ast.Store):
            # assert node.stc_scope is not None,node
            
        if node.stc_scope is None:
            # Search for the defining context.
            self.n_resolved += 1
            cx = node.stc_context
                # cx will be None if cx is an ast.Module.
                # In that case, self.lookup will search the builtins.
            d = self.lookup(cx,node.id)
            if d is None:
                # g.trace('(ScopeBinder) undefined symbol: %s' % node.id)
                if trace: print('%s undefined name: %s' % (self.fn,node.id))
    #@-others
#@+node:ekr.20140526082700.18300: *3* class StringReportTraverser (AstFormatter)
class StringReportTraverser (AstFormatter):
    
    '''Create string reports from an AST tree.'''

    #@+others
    #@+node:ekr.20140526082700.18301: *4* srt.__init__
    def __init__(self):
        
        self.visitor = self
        
        AstFormatter.__init__(self)
            # Init the base class.
        self.debug = True
    #@+node:ekr.20140526082700.18302: *5* define_html_header
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
    #@+node:ekr.20140526082700.18303: *4* srt.report(entry_point)
    def report(self,node):

        val = self.visit(node)
        s = val and val.strip()
        fn = ' for '+self.fn if self.fn else ''
        return '\nReport%s...\n\n' % (self.fn) + s
       
    #@+node:ekr.20140526082700.18304: *4* srt.show_all & helper
    def show_all(self,node,tag):
        
        result = []
        s = self.show(node,tag)
        if s: result.append(s)
        for child in self.get_child_nodes(node):
            s = self.show_all(child,tag)
            if s: result.append(s)
        return '\n'.join(result)
    #@+node:ekr.20140526082700.18305: *4* srt.show
    def show(self,node,tag):
        
        e = getattr(node,'e',None)
        table = (
            (node,'cache',tag),
            (e,'call_cache','e(%s)' % (e and e.name or '')),
            (node,'failures',''),
        )
        result = []
        for obj,ivar,tag2 in table:
            if obj and hasattr(obj,ivar):
                list_or_dict = getattr(obj,ivar)
                pad = ' '*2*(self.level+2)
                if hasattr(list_or_dict,'keys'):
                    result.append('%s%s:%s...' % (pad,tag2,ivar))
                    for key in sorted(list_or_dict.keys()):
                        aList = list_or_dict.get(key)
                        result.append('   %s%s => %s' % (pad,key,aList))
                else:
                    result.append('%sfailures: %s...' % (pad,self.format(obj)))
                    result.append('   %s%s' % (pad,list_or_dict))
        # Must end with a newline so the source is shown correctly.
        return '%s\n' % '\n'.join(result) if result else ''
    #@+node:ekr.20140526082700.18306: *4* srt.visit
    def visit(self,node):
        
        """Walk a tree of AST nodes."""

        assert isinstance(node,ast.AST),node.__class__.__name__
        kind = node.__class__.__name__
        method = getattr(self,'do_' + kind,None)
        if method:
            # method is responsible for traversing subtrees.
            return method(node)
        else:
            # Traverse subtrees automatically, without calling visit_children.
            return self.show_all(node,kind)
    #@+node:ekr.20140526082700.18307: *4* srt.visitors
    # Only these nodes may have caches.
    #@+node:ekr.20140526082700.18308: *5* srt.Assign
    def do_Assign(self,node):

        value = self.visit(node.value)
        assns = ['%s=%s\n' % (self.visit(z),value) for z in node.targets]
        s =  ''.join([self.indent(z) for z in assns])
        return s + self.show_all(node,'Assign')
    #@+node:ekr.20140526082700.18309: *5* srt.Expr
    def do_Expr(self,node):
        
        '''An outer expression: must be indented.'''
        
        s = self.indent('%s\n' % self.visit(node.value))
        return s + self.show_all(node,'Expr')
    #@+node:ekr.20140526082700.18310: *5* srt.Return
    def do_Return(self,node):
         
        val = ' ' + self.visit(node.value) if node.value else ''
        s = self.indent('return%s\n' % val)
        return s + self.show_all(node,'Return')
    #@+node:ekr.20140526082700.18311: *5* str.Str
    def do_Str (self,node):
        
        '''This represents a string constant.'''
        s = repr(node.s)
        return s if len(s) < 60 else s[:57]+'...%s' % (s[0])
    #@-others
#@+node:ekr.20140526082700.18312: *3* class SymbolTable
class SymbolTable:

    '''A base class for all symbol table info.'''
    
    #@+others
    #@+node:ekr.20140526082700.18313: *4*  st.ctor and repr
    def __init__ (self,cx):

        self.cx = cx
        self.d = {} # Keys are names, values are symbol table entries.
        self.max_name_length = 1 # Minimum field width for dumps.

    def __repr__ (self):
        # return 'SymbolTable for %s...\n' % self.cx.description()
        return 'Symbol Table for %s\n' % self.cx

    __str__ = __repr__
    #@+node:ekr.20140526082700.18314: *4* st.add_name
    def add_name (self,name):

        '''Add name to the symbol table.  Return the symbol table entry.'''
        
        st = self
        e = st.d.get(name)
        if not e:
            e = SymbolTableEntry(name,st)
            st.d [name] = e
            self.u.stats.n_names += 1
        return e
    #@+node:ekr.20140526082700.18315: *4* st.define_name
    def define_name (self,name):
        
        '''Define name in the present context (symbol table).'''
        
        # g.trace(name,self.cx)
        e = self.add_name(name)
        e.defined = True
        return e
    #@+node:ekr.20140526082700.18316: *4* st.dump
    def dump (self,level=0):
        
        cx = self.cx
        result = []
            
        def put(s):
            result.append(self.u.indent(level,s))
            
        put('')
        put(self)
        
        level += 1
        
        # Print the table entries.
        for key in sorted(self.d.keys()):
            e = self.d.get(key)
            result.append(e.dump(level+1))
                    
        result.append('')
        return '\n'.join(result)        
    #@+node:ekr.20140526082700.18317: *4* st.get_name
    def get_name (self,name):
        
        '''Return the symbol table entry for name.'''

        return self.d.get(name)
    #@-others
#@+node:ekr.20140526082700.18318: *3* class SymbolTableEntry
class SymbolTableEntry:

    #@+others
    #@+node:ekr.20140526082700.18319: *4*  e.ctor
    def __init__ (self,name,st):

        self.chains = {} # Keys are bases, values dicts of Chains.
        self.cx = st.cx
        self.defined = False
            # True: The name appears with ctx='Store'.
            # and the name is not in self.st.cx.globals_list.
        self.name = name
        self.node = None # Set by p1.FunctionDef
        self.referenced = False
        self.resolved = False
            # True: the name appears with any ctx except 'Store'.
        self.st = st
        self.self_context = None # Patched for Function/Class definitions.
        
        self.defs_seen = 0
            # The number of defs that have been resolved.
            # Not used by Pass1
        self.defs_list = []
            # List of ops that define this name.
        self.refs_list = []
            # List of ops that reference this name.
        self.types_cache = {} # Keys are list of argument types, values are type lists.
            ### Oops: set by p1.module, but never used later.

        # Update the length field for dumps.
        st.max_name_length = max(
            st.max_name_length,
            name and len(name) or 0)
    #@+node:ekr.20140526082700.18320: *4*  e.repr
    def __repr__ (self):
        
        e = self

        return 'STE(%s:%s)' % (e.cx,e.name) # id(e)
        
    __str__ = __repr__
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
    #@+node:ekr.20140526082700.18322: *4* e.dump & helpers
    def dump(self,level=0):
        
        e = self
        result = []
        
        def put(s):
            result.append(self.u.indent(level,s))
            
        put('STE cx: %s name: %s defined: %s' % (e.cx,e.name,e.defined))
            
        if e.chains:
            n = self.st.max_name_length - len(self.name)
            pad = ' '*n
            put('chains:...')
            result.append(e.dump_chains(level=level+1))
            # put('')
           

        return '\n'.join(result)
    #@+node:ekr.20140526082700.18323: *5* e.dump_chains
    def dump_chains(self,level):
        
        result = []

        def put(s):
            result.append(self.u.indent(level,s))
        
        # self.chains is a dict of dicts.
        keys = list(self.chains.keys())
        for key in keys:
            d = self.chains.get(key,{})
            for key2 in list(d.keys()):
                chain = d.get(key2)
                put(repr(chain))

        result.sort()
        return '\n'.join(result)
    #@+node:ekr.20140526082700.18324: *4* e.has_unique_type & unique_type
    # These are used by unit tests.
    def get_all_types (self):

        d = self.types_cache
        types_list = []
        for key in d.keys():
            val = d.get(key)
            if val not in types_list:
                types_list.append(val)
            # aList = d.get(key)
            # for val in aList:
                # if val not in types_list:
                    # type_list.append(val)
        return types_list

    def has_unique_type (self):
        
        '''Return True if all entries in the cache have exactly one entry.'''
        
        return len(self.get_all_types()) == 1

    def unique_type (self):
        
        '''Return e.typ[0].'''
        
        aList = self.get_all_types()
        return len(aList) == 1 and aList[0]
    #@-others
#@+node:ekr.20140526082700.18325: *3* class TypeInferer (AstTraverser)
class TypeInferer (AstTraverser):
    
    '''
    This class infers the types of objects.
    
    See the documentation for complete details.
    '''
    
    #@+others
    #@+node:ekr.20140526082700.18326: *4*  ti.ctor
    def __init__ (self,enable_trace=True):
        
        AstTraverser.__init__(self)
        
        u = Utils()
        self.cache_traverser = CacheTraverser()
        self.dump_ast = u.dump_ast
        self.format = u.format
        self.stats = u.stats
        
        # Detecting circular inferences
        self.call_stack = [] # Detects recursive calls
        self.assign_stack = [] # Detects circular assignments.

        # Create singleton instances of simple types.
        self.bool_type = Bool_Type()
        self.builtin_type = Builtin_Type()
        self.bytes_type = Bytes_Type()
        self.float_type = Float_Type()
        self.int_type = Int_Type()
        self.none_type = None_Type()
        self.string_type = String_Type()
        
        # Create the builtin type dict.
        self.builtin_type_dict = {
            'eval': [self.none_type],
            'id':   [self.int_type],
            'len':  [self.int_type],
            'ord':  [self.int_type],
            # list,tuple...
            # close,open,sort,sorted,super...
        }
        
        # Context info.
        self.null_hash = 'hash:none'
        self.call_args = None # The list of argument types for the present call.
        self.call_e = None
        self.call_hash = self.null_hash
            # The hash associated with self.call_args.
            # All hashes must start with 'hash:'

        # Debugging.
        self.align = 15
        self.enable_trace = enable_trace and u.enable_trace
        self.level = 0 # Node nesting level.
        self.n_caches = 0
        self.trace_level = 0 # Trace nesting level.
        self.trace_context = False
        self.trace_context_level = 0
    #@+node:ekr.20140526082700.18327: *4*  ti.run (entry point)
    def run (self,node):
        
        # pylint: disable=W0221
            # Arguments number differs from overridden method.
        
        ti = self
        t1 = time.time()
        ti.check_visitor_names()
        ti.visit(node)
        ti.u.stats.n_caches += ti.n_caches
        t2 = time.time()
        return t2-t1
    #@+node:ekr.20140526082700.18328: *4* ti.caches
    # Note: the hash_ argument to ti.get_call_cache can't easily be removed.
    #@+node:ekr.20140526082700.18329: *5* ti.cache_hash
    def cache_hash(self,args,e):
        
        ''' Return a hash for a list of type arg. This must be a perfect hash:
        collisions must not be possible.
        
        ti.set_cache asserts hash.startswith('hash:') This ensures that hashes
        can't be confused wiht tracing tags.'''

        return 'hash:%s([%s])' % (
            '%s@%s' % (e.name,id(e)),
            ','.join([repr(arg) for arg in args]))
    #@+node:ekr.20140526082700.18330: *5* ti.get_cache
    def get_cache(self,obj):
        
        '''Return the value of object's cache for the present context, creating
        the cache as needed.'''
        
        ti = self
        if not hasattr(obj,'cache'):
            obj.cache = {}
            ti.n_caches += 1
        return obj.cache.get(ti.call_hash,None)
            # None is the signal for a cache miss.
    #@+node:ekr.20140526082700.18331: *5* ti.get_call_cache
    def get_call_cache(self,obj,hash_):
        
        '''Return the value of object's cache for the present context, creating
        the cache as needed.'''
        
        ti = self
        if not hasattr(obj,'call_cache'):
            obj.call_cache = {}
            ti.n_caches += 1

        return obj.call_cache.get(hash_)
    #@+node:ekr.20140526082700.18332: *5* ti.method_hash
    def method_hash(self,e,node):
        
        '''If this is a method call, return the hash for the inferred ctor's
        arguments. Otherwise, return the empty string.'''
        
        ti = self
        trace = False and ti.enable_trace
        
        if ti.kind(e.self_context) == 'ClassContext':
            class_cx = e.self_context
            class_name = class_cx.name
            ctor = e.self_context.ctor
            if ctor:
                args = [ti.visit(z) for z in ctor.node.args.args]
                for specific_args in ti.cross_product(args):
                    hash_ = ti.cache_hash(specific_args,e)
                return 'hash:class:%s:%s' % (class_name,hash_)
            else:
                if trace: ti.trace(class_name,'no ctor')
        return ''
    #@+node:ekr.20140526082700.18333: *5* ti.set_cache
    def set_cache(self,obj,t,tag=''):

        '''Set the object's cache for the present context to the given type
        list t, creating the cache as needed.'''

        ti = self
        trace = False and ti.enable_trace
        assert isinstance(t,list)
        hash_ = ti.call_hash
        assert hash_.startswith('hash:'),hash_
            # Don't confuse the hash_ and tag_ keywords!
        assert isinstance(t,list)
        if not hasattr(obj,'cache'):
            obj.cache = {}
            ti.n_caches += 1
        
        obj.cache [hash_] = t
        if trace: ti.trace('%s -> %s' % (hash_,t))
            # ti.show_cache(obj,obj.cache,tag)
           
        # Old 
        # aList = obj.cache.get(hash_,[])
        # aList.extend(t)
        # aList = ti.clean(aList)
        #obj.cache [hash_] = aList
    #@+node:ekr.20140526082700.18334: *5* ti.set_call_cache
    def set_call_cache(self,obj,hash_,t,tag=''):
        
        ti=self
        trace = False and ti.enable_trace
        if not hasattr(obj,'call_cache'):
            obj.call_cache = {}
            ti.n_caches += 1

        # Update e.call_cache, not e.cache!
        assert isinstance(t,list)
        obj.call_cache [hash_] = t
        
        if trace: ti.trace('%s:%s -> %s' % (obj,hash_,t))
     
        ### Old
        # aList = obj.call_cache.get(hash_,[])
        # aList.extend(t)
        # aList = ti.clean(aList)
        # obj.call_cache [hash_] = aList
    #@+node:ekr.20140526082700.18335: *5* ti.show_cache
    def show_cache(self,obj,cache,tag):
        
        ti = self
        d = cache
        # kind = ti.kind(obj)
        pad = ' '*2*ti.level
        s = ti.format(obj) if isinstance(obj,ast.AST) else repr(obj)
        if len(s) > 40: s = s[:40]+'...'
        g.trace('%2s %s %s' % (ti.level,tag,s))
        # pad2 = pad + ' '*44
        for key in sorted(d.keys()):
            aList = d.get(key)
            for item in aList:
                print('   %s => %s' % (key,item))
        print('')
    #@+node:ekr.20140526082700.18336: *4* ti.helpers
    #@+node:ekr.20140526082700.18337: *5* ti.clean
    def clean (self,aList):
        
        '''Return sorted(aList) with all duplicates removed.'''
        
        ti = self
        if 1:
            # Good for debugging and traces.
            result = []
            for z in aList:
                if z not in result:
                    result.append(z)
            
            # An excellent check.
            assert len(result) == len(list(set(aList))),aList
        else:
            result = list(set(aList))
       
        # Strip out inference errors if there are real results.
        result2 = ti.ignore_failures(result)
        if result2:
            ti.stats.n_clean_success += 1
            return sorted(result2)
        else:
            ti.stats.n_clean_fail += 1
            return sorted(result)
    #@+node:ekr.20140526082700.18338: *5* ti.cross_product
    def cross_product(self,aList):
        
        '''Return generator yielding a list of lists representing the
        cross product of all elements in aList, a list of lists. Examples:
            
        cross_product([['a']])               -> [['a']]
        cross_product([['a'],['b']])         -> [['a'],['b']]
        cross_product([['a'],['b','c']])     -> [['a','b'],['a','c']]
        cross_product([['a','b'],['c']])     -> [['a','c'],['b','c']]
        cross_product([['a','b'],['c','d']]) -> [['a','c'],['a','d'],['b','c'],['b','d']]
        '''
        
        ti = self
        trace = False and ti.enable_trace
        
        # Return a real list so we can do stats on it.
        result = [z for z in itertools.product(*aList)]
        
        if 0:
            g.trace(len(aList),aList)
            for z in result:
                print(z)
        
        if 1: # Stats and traces.
            ambig = len(result) > 1
            if trace and ambig: g.trace('\n',aList,'->',result)
            ti.stats.n_cross_products += 1
            n = len(result)
            d = ti.stats.cross_product_dict
            d[n] = 1 + d.get(n,0)

        return result
    #@+node:ekr.20140526082700.18339: *5* ti.switch/restore_context
    # These are called *only* from ti.infer_def.
     
    def switch_context(self,e,hash_,node):
        ti = self
        ti.trace_context = False and ti.enable_trace
        data = ti.call_args,ti.call_e,ti.call_hash
        ti.call_args = e.call_cache.get(hash_)
        ti.call_e = e
        ti.call_hash = hash_
        if ti.trace_context:
            ti.trace(ti.call_hash,before='\n'+' '*2*ti.trace_context_level)
        ti.trace_context_level += 1
        return data
        
    def restore_context(self,data):
        ti = self
        ti.call_args,ti.call_e,ti.call_hash = data
        ti.trace_context_level -= 1
        if self.trace_context:
            ti.trace(ti.call_hash,before=' '*2*ti.trace_context_level)
    #@+node:ekr.20140526082700.18340: *5* ti.type helpers
    def has_failed(self,t1,t2=[],t3=[]):
        
        return any([isinstance(z,Inference_Failure) for z in t1+t2+t3])
        
    def is_circular(self,t1,t2=[],t3=[]):
        
        return any([isinstance(z,Circular_Assignment) for z in t1+t2+t3])
        
    def is_recursive(self,t1,t2=[],t3=[]):
        
        return any([isinstance(z,Recursive_Inference) for z in t1+t2+t3])
        
    def ignore_failures(self,t1,t2=[],t3=[]):
        
        return [z for z in t1+t2+t3 if not isinstance(z,Inference_Failure)]
        
    def ignore_unknowns(self,t1,t2=[],t3=[]):
        
        return [z for z in t1+t2+t3 if not isinstance(z,(Unknown_Type,Unknown_Arg_Type))]
        
    def merge_failures(self,t1,t2=[],t3=[]):

        aList = [z for z in t1+t2+t3 if isinstance(z,Inference_Failure)]
        if len(aList) > 1:
            # Prefer the most specific reason for failure.
            aList = [z for z in aList if not isinstance(z,Unknown_Type)]
        return aList
    #@+node:ekr.20140526082700.18341: *4* ti.trace
    def trace(self,*args,**keys):
        
        ti = self

        if 1: # No indentation at all.
            level = 0
        elif 1: # Show tree level.
            level = ti.level
        else: # Minimize trace level.
            if ti.trace_level < ti.level:
                ti.trace_level += 1
            elif ti.trace_level > ti.level:
                ti.trace_level -= 1
            level = ti.trace_level
            
        if keys.get('before') is None:
            before = '.'*level
        else:
            before = keys.get('before')
      
        keys['align'] = ti.align
        keys['before'] = before
        keys['caller_level'] = 2
        g.trace(*args,**keys)
    #@+node:ekr.20140526082700.18342: *4* ti.traversers
    #@+node:ekr.20140526082700.18343: *5*  ti.visit
    def visit(self,node):
        
        '''Infer the types of all nodes in a tree of AST nodes.'''

        ti = self
        assert isinstance(node,ast.AST),node.__class__.__name__
        method_name = 'do_' + node.__class__.__name__
        method = getattr(self,method_name,None)
        val = None
        try:
            ti.level += 1
            if method:
                # The method is responsible for traversing subtrees.
                # Furthermore, somebody uses the returned value.
                val = method(node)
            else:
                # Traverse subtrees automatically.
                # *Nobody* uses the returned value.
                for child in ti.get_child_nodes(node):
                    ti.visit(child)
        
                # Returning None is a good test.
                val = None
        finally:
            ti.level -= 1
        return val
    #@+node:ekr.20140526082700.18344: *5*  ti.visit_children
    def visit_children(self,node):
        
        ti = self
        assert isinstance(node,ast.AST),node.__class__.__name__
        
        for child in ti.get_child_nodes(node):
            ti.visit(child)

        # Returning None is a good test.
        return None
    #@+node:ekr.20140526082700.18345: *5*  ti.visit_list
    def visit_list (self,aList):

        ti = self
        assert type(aList) in (list,tuple),aList
        
        for node in aList:
            ti.visit(node)
            
        # Returning None is a good test.
        return None
    #@+node:ekr.20140526082700.18346: *4* ti.visitors
    #@+node:ekr.20140526082700.18347: *5* ti.arguments
    # arguments = (expr* args, identifier? vararg, identifier? kwarg, expr* defaults)

    def do_arguments (self,node):
        
        '''Bind formal arguments to actual arguments.'''
        
        assert False # All the work is done in ti.Call and its helpers.
    #@+node:ekr.20140526082700.18348: *5* ti.Assign (sets cache)
    def do_Assign(self,node):

        ti = self
        trace = False and ti.enable_trace
        junk = ti.visit_list(node.targets)
        hash_ = ti.call_hash
        data = hash_,node
        if data in ti.assign_stack:
            t = [Circular_Assignment(hash_,node)]
            ti.stats.n_circular_assignments += 1
        else:
            ti.assign_stack.append(data)
            try:
                t = ti.visit(node.value)
                if trace: ti.trace(t)
            finally:
                data2 = ti.assign_stack.pop()
                assert data == data2
            
        for target in node.targets:
            kind = ti.kind(target)
            if kind == 'Name':
                t0 = ti.get_cache(target.e) or []
                t.extend(t0)
                ti.set_cache(target.e,t,tag='Name:target.e')
                if trace: ti.trace('infer: %10s -> %s' % (
                    ti.format(target),t),before='\n')
            else:
                ### What to do about this?
                if trace: ti.trace('(ti) not a Name: %s' % (
                    ti.format(target)),before='\n')
                    
        # Update the cache immediately.
        t0 = ti.get_cache(node) or []
        t.extend(t0)
        t = ti.clean(t)
        ti.set_cache(node,t,tag='ti.Assign')
        return t
    #@+node:ekr.20140526082700.18349: *5* ti.Attribute & check_attr (check super classes for attributes)
    # Attribute(expr value, identifier attr, expr_context ctx)

    def do_Attribute (self,node):

        ti = self
        trace = False and ti.enable_trace
        trace_errors = True ; trace_found = False ; trace_fuzzy = True
        # print('do_Attribute',ti.format(node),node.value,node.attr)
        
        t = ti.get_cache(node)
        if t is not None:
            # g.trace('hit',t)
            return t

        #### ti.set_cache(node,[Unknown_Type(ti.call_hash,node)],tag='ti.Attribute')
        t = ti.visit(node.value)
        t = ti.clean(t) ###
        t = ti.merge_failures(t)
        tag = '%s.%s' % (t,node.attr) # node.attr is always a string.
        if t:
            if len(t) == 1:
                ti.stats.n_not_fuzzy += 1
                t1 = t[0]
                if ti.kind(t1) == 'Class_Type':
                    aList = t1.cx.ivars_dict.get(node.attr)
                    aList = ti.clean(aList) if aList else []
                    if aList:
                        t = []
                        for node2 in aList:
                            t.extend(ti.visit(node2))
                        t = ti.clean(t)
                        ti.set_cache(node,t,tag='ti.Attribute')
                        ti.stats.n_attr_success += 1
                        if trace and trace_found:
                            g.trace('ivar found: %s -> %s' % (tag,t))
                            # [ti.format(z) for z in aList],t))
                    elif t1.cx.bases:
                        if trace_errors: g.trace('bases',
                            ti.format(node),[ti.format(z) for z in t1.cx.bases])
                        pass ### Must check super classes.
                        t = [Unknown_Type(ti.call_hash,node)] ###
                    else:
                        ti.error('%20s has no %s member' % (ti.format(node),t1.cx.name))
                        t = [Unknown_Type(ti.call_hash,node)] ###
                else:
                    ti.stats.n_attr_fail += 1
                    if trace and trace_errors:
                        g.trace('fail',t,ti.format(node))
                    t = [Unknown_Type(ti.call_hash,node)] ###
            else:
                ti.stats.n_fuzzy += 1
                if trace and trace_fuzzy: g.trace('fuzzy',t,ti.format(node))
        else:
            if trace and trace_errors: g.trace('fail',t,ti.format(node))
            t = [Unknown_Type(ti.call_hash,node)]

        # ti.check_attr(node) # Does nothing
        return t
    #@+node:ekr.20140526082700.18350: *6* ti.check_attr
    def check_attr(self,node):
        
        ti = self
        trace = False and ti.enable_trace
        
        return ### Now done in ti.Attribute

        # assert ti.kind(node) == 'Attribute'
        # value = node.value
        # # node.attr is always a string.
        
        # if ti.kind(value) == 'Name':
            # # The ssa pass has computed the ivars dict.
            # # There is no need to examine value.ctx.
            # name = value.id
            # name_e = value.e
            # name_cx = name_e.cx
            # name_class_cx = name_cx.class_context
            # if name == 'self':
                # if name_class_cx:
                    # if node.attr in name_class_cx.ivars_dict:
                        # if trace: g.trace('OK: %s.%s' % (
                            # name_class_cx.name,node.attr))
                    # else:
                        # ti.error('%s has no %s member' % (
                            # name_class_cx.name,node.attr))
                # else:
                    # ti.error('%s is not a method of any class' % (
                        # name)) ####
            # else:
                # ### To do: handle any id whose inferred type is a class or instance.
                # if trace:
                    # g.trace('** not checked: %s' % (name))
                    # g.trace(ti.dump_ast(value))
    #@+node:ekr.20140526082700.18351: *5* ti.Builtin
    def do_Builtin(self,node):
        
        assert False,node
    #@+node:ekr.20140526082700.18352: *5* ti.Call & helpers
    # Call(expr func, expr* args, keyword* keywords, expr? starargs, expr? kwargs)
    #   Note: node.starargs and node.kwargs are given only if assigned explicitly.

    def do_Call (self,node):
        '''
        Infer the value of a function called with a particular set of arguments.
        '''
        ti = self
        trace = False and ti.enable_trace
        trace_builtins = True ; trace_hit = False
        trace_errors = True ; trace_returns = False

        kind = ti.kind(node)
        func_name = ti.find_function_call(node)
        
        if trace and trace_hit: ti.trace('1:entry:',func_name) # ,before='\n',
        
        # Special case builtins.
        t = ti.builtin_type_dict.get(func_name,[])
        if t:
            if trace and trace_builtins: ti.trace(func_name,t)
            return t
            
        # Find the def or ctor to be evaluated.
        e = ti.find_call_e(node.func)
        if not (e and e.node):
            # find_call_e has given the warning.
            t = [Unknown_Type(ti.call_hash,node)]
            s = '%s(**no e**)' % (func_name)
            if trace and trace_errors: ti.trace('%17s -> %s' % (s,t))
            return t

        # Special case classes.  More work is needed.
        if ti.kind(e.node) == 'ClassDef':
            # Return a type representing an instance of the class
            # whose ctor is evaluated in the present context.
            args,t = ti.class_instance(e)
            if trace and trace_returns:
                s = '%s(%s)' % (func_name,args)
                ti.trace('%17s -> %s' % (s,t))
            return t

        # Infer the specific arguments and gather them in args list.
        # Each element of the args list may have multiple types.
        assert ti.kind(e.node) == 'FunctionDef'
        args = ti.infer_actual_args(e,node)
            
        # Infer the function for the cross-product the args list.
        # In the cross product, each argument has exactly one type.
        ti.stats.n_ti_calls += 1
        recursive_args,t = [],[]
        for specific_args in ti.cross_product(args):
            # Add the specific arguments to the cache.
            hash_ = ti.cache_hash(specific_args,e)
            t2 = ti.get_call_cache(e,hash_)
            miss = t2 is None   
            # if trace and trace_hit:
                # ti.trace('%s %12s -> %s' % ('miss' if miss else 'hit!',
                    # func_name,specific_args))
            if miss:
                ti.stats.n_call_misses += 1
                if trace and trace_hit: ti.trace('2:miss',hash_)
                t2 = ti.infer_def(specific_args,e,hash_,node,rescan_flag=False)
                if ti.is_recursive(t2):
                    data = hash_,specific_args,t2
                    recursive_args.append(data)
                # if trace and trace_returns: ti.trace(hash_,'->',t2)
            else:
                if trace and trace_hit: ti.trace('2:hit!',hash_)
                ti.stats.n_call_hits += 1
            t.extend(t2)

        if True and recursive_args:
            if trace: ti.trace('===== rerunning inference =====',t)
            for data in recursive_args:
                # Merge the types into the cache.
                hash_,specific_args,t2 = data
                t3  = ti.get_call_cache(e,hash_) or []
                t4 = ti.ignore_failures(t,t2,t3)
                # g.trace('t3',t3)
                # g.trace('t4',t4)
                ti.set_call_cache(e,hash_,t4,tag='ti.call:recursive')
                t5 = ti.infer_def(specific_args,e,hash_,node,rescan_flag=True)
                if trace: g.trace('t5',t5)
                t.extend(t5)
            
        if ti.has_failed(t):
            t = ti.merge_failures(t)
            # t = ti.ignore_failures(t)
        else:
            t = ti.clean(t)
        if trace and trace_returns:
            s = '3:return %s(%s)' % (func_name,args)
            ti.trace('%17s -> %s' % (s,t))
        return t
    #@+node:ekr.20140526082700.18353: *6* ti.class_instance
    def class_instance (self,e):
        
        '''
        Return a type representing an instance of the class
        whose ctor is evaluated in the present context.
        '''
        
        ti = self
        trace = True and ti.enable_trace
        cx = e.self_context
        
        # Step 1: find the ctor if it exists.
        d = cx.st.d
        ctor = d.get('__init__')

        # node2 = node.value
        # name = node2.id
        # attr = node.attr
        # e = getattr(node2,'e',None)
        # if trace: ti.trace(kind,v_kind,name,attr)
        # # ti.trace('e',e)
        # t = ti.get_cache(e)
        # # ti.trace('cache',t)
        # if len(t) == 1:
            # t = t[0]
            # e_value = t.node.e
            # # ti.trace('* e_value',e_value)
            # # ti.trace('e_value.self_context',e_value.self_context)
            # e = e_value.self_context.st.d.get(node.attr)
            # if trace: ti.trace('** e_value.self_context.st.d.get(%s)' % (attr),e)
            # # ti.trace('e_value.self_context.st.d', e_value.self_context.st.d)
            # # ti.trace('e.node',e.node)
            
        args = [] ### To do
        t = [Class_Type(cx)]
        ti.set_cache(e,t,tag='class name')
        return args,t
    #@+node:ekr.20140526082700.18354: *6* ti.find_call_e
    def find_call_e (self,node):
        
        '''Find the symbol table entry for node, an ast.Call node.'''
        
        ti = self
        trace = False and ti.enable_trace
        trace_errors = False; trace_fuzzy = True ; trace_return = False
        kind = ti.kind(node)
        e = None # Default.
        if kind == 'Name':
            # if trace: ti.trace(kind,node.id)
            e = getattr(node,'e',None)
        else:
            t = ti.visit(node)
            if len(t) == 1:
                ti.stats.n_not_fuzzy += 1
                t = t[0]
                if ti.kind(t) == 'Class_Type':
                    d = t.cx.st.d
                    if ti.kind(node) == 'Attribute':
                        name = node.attr
                    elif ti.kind(node) == 'Call':
                        name = node.func
                    else:
                        name = None
                    if name:
                        e = d.get(name)
                    else:
                        e = None
                else:
                    if trace and trace_errors:
                        ti.trace('not a class type: %s %s' % (ti.kind(t),ti.format(node)))
            elif len(t) > 1:
                if trace and trace_fuzzy: ti.trace('fuzzy',t,ti.format(node))
                ti.stats.n_fuzzy += 1
                e = None
            
        # elif kind == 'Attribute':
            # v_kind = ti.kind(node.value)
            # if v_kind == 'Name':
                # node2 = node.value
                # name = node2.id
                # attr = node.attr
                # e = getattr(node2,'e',None)
                # # if trace: ti.trace(kind,v_kind,name,attr)
                # t = ti.get_cache(e)
                # if len(t) == 1:
                    # t = t[0]
                    # if ti.kind(t) == 'Class_Type':
                        # d = t.cx.st.d
                        # e = d.get(node.attr)
                    # else:
                        # pass ### To do
                # elif t:
                    # pass
                # else:
                    # t = [Unknown_Type(ti.call_hash,node)]
            # elif v_kind == 'Attribute':
                # node2 = node.value
                # ti.trace('*****',kind,v_kind,ti.format(node.value))
                # e = ti.find_call_e(node2)
            # else:
                # ti.trace('not ready yet',kind,v_kind)
                # e = None
        # elif kind in ('Call','Subscript'):
            # ti.trace(kind)
            # e = None
        # else:
            # ti.trace('===== oops:',kind)
            # e = None
            
        if e:
            assert isinstance(e,SymbolTableEntry),ti.kind(e)
            ti.stats.n_find_call_e_success += 1
        else:
            # Can happen with methods,Lambda.
            ti.stats.n_find_call_e_fail += 1
            if trace and trace_errors: ti.trace('**** no e!',kind,ti.format(node),
                align=ti.align,before='\n')

        if e and not e.node:
            if trace and trace_errors: ti.trace(
                'undefined e: %s' % (e),before='\n')

        if trace and trace_return: ti.trace(
            kind,'e:',e,ti.format(node))
        return e
    #@+node:ekr.20140526082700.18355: *6* ti.infer_actual_args
    # Call(expr func, expr* args, keyword* keywords, expr? starargs, expr? kwargs)
    #   keyword = (identifier arg, expr value) # keyword arguments supplied to call

    # FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list)
    #   arguments = (expr* args, identifier? vararg, identifier? kwarg, expr* defaults)

    def infer_actual_args (self,e,node):
        
        '''Return a list of types for all actual args, in the order defined in
        by the entire formal argument list.'''
        
        ti = self
        trace = False and ti.enable_trace
        trace_args = False
        assert ti.kind(node)=='Call'
        cx = e.self_context
        # Formals...
        formals  = cx.node.args or []
        defaults = cx.node.args.defaults or [] # A list of expressions
        vararg   = cx.node.args.vararg
        kwarg    = cx.node.args.kwarg
        # Actuals...
        actuals  = node.args or [] # A list of expressions.
        keywords = node.keywords or [] # A list of (identifier,expression) pairs.
        starargs = node.starargs
        kwargs   = node.kwargs
        assert ti.kind(formals)=='arguments'
        assert ti.kind(formals.args)=='list'
        
        formal_names = [z.id for z in formals.args]
            # The names of *all* the formal arguments, include those with defauls.
            # Doesw not include vararg and kwarg.
           
        # Append unnamed actual args.
        # These could be either non-keyword arguments or keyword arguments.
        args = [ti.visit(z) for z in actuals]
        bound_names = formal_names[:len(actuals)]
        
        if trace and trace_args:
            ti.trace('formal names',formal_names)
            ti.trace('   arg names',bound_names)
            ti.trace('    starargs',starargs and ti.format(starargs))
            ti.trace('    keywargs',kwargs   and ti.format(kwargs))
            # formal_defaults = [ti.visit(z) for z in defaults]
                # # The types of each default.
            # ti.trace('formal default types',formal_defaults)
            # ti.trace('unnamed actuals',[ti.format(z) for z in actuals])
        
        # Add keyword args in the call, in the order they appear in the formal list.
        # These could be either non-keyword arguments or keyword arguments.
        keywargs_d = {}
        keywords_d = {}
        for keyword in keywords:
            name = keyword.arg
            t = ti.visit(keyword.value)
            value = ti.format(keyword.value)
            keywords_d[name] = (value,t)

        for name in formal_names[len(actuals):]:
            data = keywords_d.get(name)
            if data:
                value,t = data
                if trace and trace_args: ti.trace('set keyword',name,value,t)
                args.append(t)
                bound_names.append(name)
            # else: keywargs_d[name] = None ### ???

        # Finally, add any defaults from the formal args.
        n_plain = len(formal_names) - len(defaults)
        defaults_dict = {}
        for i,expr in enumerate(defaults):
            name = formal_names[n_plain+i]
            value = ti.format(expr)
            t = ti.visit(expr)
            defaults_dict[name] = (value,t)

        for name in formal_names:
            if name not in bound_names:
                data = defaults_dict.get(name)
                t = None # default
                if data:
                    value,t = data
                    if trace and trace_args: ti.trace('set default',name,value,t)
                elif name == 'self':
                    def_cx = e.self_context
                    class_cx = def_cx and def_cx.class_context
                    if class_cx:
                        t = [Class_Type(class_cx)]
                if t is None:
                    t = [Unknown_Arg_Type(ti.call_hash,node)]
                    ti.error('Unbound actual argument: %s' % (name))
                args.append(t)
                bound_names.append(name)
                
        ### Why should this be true???
        # assert sorted(formal_names) == sorted(bound_names)

        if None in args:
            ti.trace('***** opps node.args: %s, args: %s' % (node.args,args))
            args = [z for z in args if z is not None]
            
        if trace: ti.trace('result',args)
        return args
    #@+node:ekr.20140526082700.18356: *6* ti.infer_def & helpers (sets call cache)
    def infer_def(self,specific_args,e,hash_,node,rescan_flag):
        
        '''Infer everything possible from a def D called with specific args:
        
        1. Bind the specific args to the formal parameters in D.
        2. Infer all assignments in D.
        3. Infer all outer expression in D.
        4. Infer all return statements in D.
        '''

        ti = self
        trace = False and ti.enable_trace
        t0 = ti.get_call_cache(e,hash_) or []
        if hash_ in ti.call_stack and not rescan_flag:
            # A recursive call: always add an Recursive_Instance marker.
            if trace:ti.trace('A recursive','rescan',rescan_flag,hash_,'->',t0)
            ti.stats.n_recursive_calls += 1
            t = [Recursive_Inference(hash_,node)]
        else:
            if trace: ti.trace('A',hash_,'->',t0)
            ti.call_stack.append(hash_)
            try:
                cx = e.self_context
                data = ti.switch_context(e,hash_,node)
                ti.bind_args(specific_args,cx,e,node)
                ti.infer_assignments(cx,e)
                ti.infer_outer_expressions(cx,node)
                t = ti.infer_return_statements(cx,e)
                ti.restore_context(data)
            finally:
                hash2 = ti.call_stack.pop()
                assert hash2 == hash_
        # Merge the result and reset the cache.
        t.extend(t0)
        t = ti.clean(t)
        ti.set_call_cache(e,hash_,t,tag='infer_def')
            # Important: does *not* use ti.call_hash.
        if trace: ti.trace('B',hash_,'->',t)
        return t
    #@+node:ekr.20140526082700.18357: *7* ti.bind_args (ti.infer_def helper) (To do: handle self)
    # Call(expr func, expr* args, keyword* keywords, expr? starargs, expr? kwargs)
    #   keyword = (identifier arg, expr value) # keyword arguments supplied to call

    # FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list)
    #   arguments = (expr* args, identifier? vararg, identifier? kwarg, expr* defaults)

    def bind_args (self,types,cx,e,node):
        
        ti = self
        trace = False and ti.enable_trace
        assert ti.kind(node)=='Call'
        assert isinstance(node.args,list),node
        formals = cx.node.args or []
        assert ti.kind(formals)=='arguments'
        assert ti.kind(formals.args)=='list'
        formal_names = [z.id for z in formals.args]
            # The names of *all* the formal arguments, include those with defauls.
            
        if len(formal_names) != len(types):
            # ti.trace('**** oops: formal_names: %s types: %s' % (formal_names,types))
            return

        def_cx = e.self_context
        d = def_cx.st.d
        for i,name in enumerate(formal_names):
            ### Handle self here.
            t = types[i]
            e2 = d.get(name)
            if e2:
                if trace: ti.trace(e2,t) # ti.trace(e2.name,t)
                ti.set_cache(e2,[t],tag='bindargs:%s'%(name))
            else:
                ti.trace('**** oops: no e2',name,d)
    #@+node:ekr.20140526082700.18358: *7* ti.infer_assignments
    def infer_assignments(self,cx,e):
        
        '''Infer all the assignments in the function context.'''

        ti = self
        trace = False and ti.enable_trace
        for a in cx.assignments_list:
            if ti.kind(a) == 'Assign': # ignore AugAssign.
                t2 = ti.get_cache(a)
                if t2:
                    ti.stats.n_assign_hits += 1
                    if trace: ti.trace('hit!',t2)
                else:
                    t2 = ti.visit(a)
                    t3 = ti.ignore_failures(t2)
                    if t3:
                        ti.stats.n_assign_misses += 1
                        # ti.trace('***** set cache',t2)
                        ti.set_cache(a,t2,tag='infer_assns')
                        if trace: ti.trace('miss',t2)
                    else:
                        ti.stats.n_assign_fails += 1
                        if trace: ti.trace('fail',t2)
                   
                       
        return None # This value is never used.
    #@+node:ekr.20140526082700.18359: *7* ti.infer_outer_expressions
    def infer_outer_expressions(self,cx,node):
        
        '''Infer all outer expressions in the function context.'''

        ti = self
        trace = False and ti.enable_trace
        for exp in cx.expressions_list:
            if trace: ti.trace(ti.call_hash,ti.format(exp))
            t2 = ti.get_cache(exp)
            if t2 is not None:
                ti.stats.n_outer_expr_hits += 1
                if trace: ti.trace('hit!',t2)
            else:
                ti.stats.n_outer_expr_misses += 1
                # ti.trace('miss',ti.call_hash)
                # Set the cache *before* calling ti.visit to terminate the recursion.
                t = [Unknown_Type(ti.call_hash,node)]
                ti.set_cache(exp,t,tag='ti.infer_outer_expressions')
                t = ti.visit(exp)
                ti.set_cache(exp,t,tag='ti.infer_outer_expressions')
                if trace: ti.trace('miss',t)

        return None # This value is never used.
    #@+node:ekr.20140526082700.18360: *7* ti.infer_return_statements
    def infer_return_statements(self,cx,e):
        
        '''Infer all return_statements in the function context.'''
        
        ti = self
        trace = True and ti.enable_trace
        trace_hit = False
        t = []
        for r in cx.returns_list:
            assert r
            t2 = ti.get_cache(r)
            if t2:
                if trace and trace_hit: ti.trace('hit!',t2)
            else:
                t2 = ti.visit(r)
                if trace and trace_hit: ti.trace('miss',t2)
                t.extend(t2)
        if ti.has_failed(t):
            t = ti.merge_failures(t)
        else:
            t = ti.clean(t)
        return t
    #@+node:ekr.20140526082700.18361: *5* ti.ClassDef
    def do_ClassDef(self,node):
        
        '''
        For lint-like operation: infer all methods with 'unknown' as the value of all args.
        For jit-like operation: do nothing.
        '''
        
        ti = self
        if lint_like:
            return ti.visit_children(node)
        else:
            return [] # This value should not be used.
    #@+node:ekr.20140526082700.18362: *5* ti.Expr (new)
    # Expr(expr value)

    # This isn't really needed: the default visitor would work.

    def do_Expr(self,node):
        
        ti = self
        t = ti.visit(node.value)
        return t
    #@+node:ekr.20140526082700.18363: *5* ti.FunctionDef & helpers
    # FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list)

    def do_FunctionDef (self,node):
        
        '''Infer this function or method with 'unknown' as the value of all args.
        This gets inference going.
        '''
        
        ti = self
        trace = False and not ti.enable_trace
        
        # Set up function call, with 'unknown' for all args.
        e = node.e
        specific_args = [Unknown_Arg_Type(ti.call_hash,node)] * ti.count_full_args(node)
        hash_ = ti.cache_hash(specific_args,e)
        t = ti.get_call_cache(e,hash_)
        if trace:
            ti.trace('%s %12s -> %s' % ('miss' if t is None else 'hit!',
                node.name,specific_args))
        if t is None:
            t = ti.infer_outer_def(specific_args,hash_,node)
        return t

    #@+node:ekr.20140526082700.18364: *6* ti.count_full_args
    # FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list)
    #   arguments = (expr* args, identifier? vararg, identifier? kwarg, expr* defaults)

    def count_full_args (self,node):
        
        '''Return the number of arguments in a call to the function/def defined
        by node, an ast.FunctionDef node.'''
        
        ti = self
        trace = False and ti.enable_trace
        assert ti.kind(node)=='FunctionDef'    
        args = node.args
        if trace: ti.trace('args: %s vararg: %s kwarg: %s' % (
            [z.id for z in args.args],args.vararg,args.kwarg))
        n = len(args.args)
        if args.vararg: n += 1
        if args.kwarg:  n += 1
        return n
    #@+node:ekr.20140526082700.18365: *6* ti.infer_outer_def & helper
    def infer_outer_def(self,specific_args,hash_,node):
        
        '''Infer everything possible from a def D called with specific args:
        
        1. Bind the args to the formal parameters in D.
        2. Infer all assignments in D.
        3. Infer all outer expression in D.
        4. Infer all return statements in D.
        '''

        ti = self
        # trace = True and ti.enable_trace
        assert ti.kind(node)=='FunctionDef',node
        e = node.e
        assert hasattr(e,'call_cache')
        cx = e.self_context
        data = ti.switch_context(e,hash_,node)
        ti.bind_outer_args(hash_,node)
        ti.infer_assignments(cx,e)
        ti.infer_outer_expressions(cx,node)
        t = ti.infer_return_statements(cx,e)
        ti.set_call_cache(e,hash_,t,tag='infer_def')
        ti.restore_context(data)
        return t
    #@+node:ekr.20140526082700.18366: *7* ti_bind_outer_args (ti.infer_outer_def helper)
    # FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list)
    #   arguments = (expr* args, identifier? vararg, identifier? kwarg, expr* defaults)
    def bind_outer_args (self,hash_,node):
        
        '''Bind all all actual arguments except 'self' to "Unknown_Arg_Type".'''
        
        ti = self
        trace = False and ti.enable_trace
        assert ti.kind(node)=='FunctionDef'
        e = node.e
        def_cx = e.self_context
        args = node.args or []
        assert ti.kind(args)=='arguments',args
        assert ti.kind(args.args)=='list',args.args
        formal_names = [z.id if hasattr(z,'id') else '<tuple arg>' for z in args.args]
        if args.vararg: formal_names.append(args.vararg)
        if args.kwarg:  formal_names.append(args.kwarg)
        # if trace: ti.trace(formal_names)
        d = def_cx.st.d
        for name in formal_names:
            if name == 'self':
                if def_cx:
                    t = [Class_Type(def_cx)]
                else:
                    t = [Unknown_Arg_Type(ti.call_hash,node)]
                e2 = e
            else:
                t = [Unknown_Arg_Type(ti.call_hash,node)]
                e2 = d.get(name)
            if e2:
                ti.set_cache(e2,t,tag='bind_outer_args:%s'%(name))
                if trace: ti.trace(name,t)
            else:
                if trace: ti.trace('**** oops: no e2',name,d)
    #@+node:ekr.20140526082700.18367: *5* ti.Lambda
    def do_Lambda (self,node):
        
        ti = self
        return ti.visit(node.body)
    #@+node:ekr.20140526082700.18368: *5* ti.operators
    #@+node:ekr.20140526082700.18369: *6* ti.BinOp & helper
    def do_BinOp (self,node):

        ti = self
        trace = True and ti.enable_trace
        trace_infer = False ; trace_fail = True
        lt = ti.visit(node.left)
        rt = ti.visit(node.right)
        lt = ti.clean(lt)
        rt = ti.clean(rt)
        op_kind = ti.kind(node.op)
        num_types = ([ti.float_type],[ti.int_type])
        list_type = [List_Type(None)]
        if rt in num_types and lt in num_types:
            if rt == [ti.float_type] or lt == [ti.float_type]:
                t = [ti.float_type]
            else:
                t = [ti.int_type]
        elif rt == list_type and lt == list_type and op_kind == 'Add':
            t = list_type
        elif op_kind == 'Add' and rt == [ti.string_type] and lt == [ti.string_type]:
            t = [ti.string_type]
        elif op_kind == 'Mult' and rt == [ti.string_type] and lt == [ti.string_type]:
            ti.trace('*** User error: string mult')
            t = [Unknown_Type(ti.call_hash,node)]
        elif op_kind == 'Mult' and (
            (lt==[ti.string_type] and rt==[ti.int_type]) or
            (lt==[ti.int_type] and rt==[ti.string_type])
        ):
            t = [ti.string_type]
        elif op_kind == 'Mod' and lt == [ti.string_type]:
            t = [ti.string_type] # (string % anything) is a string.
        else:
            ti.stats.n_binop_fail += 1
            if trace and trace_fail:
                if 1:
                    s = '%r %s %r' % (lt,op_kind,rt)
                    g.trace('  fail: %30s %s' % (s,ti.format(node)))
                else:
                    g.trace('  fail:',lt,op_kind,rt,ti.format(node))
            t = [Inference_Error(ti.call_hash,node)] ### Should merge types!
        if trace and trace_infer: ti.trace(ti.format(node),'->',t)
        return t
    #@+node:ekr.20140526082700.18370: *6* ti.BoolOp
    def do_BoolOp(self,node):

        ti = self    
        junk = ti.visit_children(node)
        return [ti.bool_type]
    #@+node:ekr.20140526082700.18371: *6* ti.Compare
    def do_Compare(self,node):

        ti = self    
        junk = ti.visit_children(node)
        return [ti.bool_type]
    #@+node:ekr.20140526082700.18372: *6* ti.comprehension
    def do_comprehension(self,node):

        ti = self    
        junk = ti.visit_children(node)

        # name = node.name
        # ti.visit(node.it)

        # for node2 in node.ifs:
            # ti.visit(node2)

        return [List_Type(node)]
    #@+node:ekr.20140526082700.18373: *6* ti.Expr (not used)
    # def do_Expr (self,node):

        # ti = self    
        # return ti.visit(node.value)
    #@+node:ekr.20140526082700.18374: *6* ti.GeneratorExp
    def do_GeneratorExp (self,node):

        ti = self
        trace = False and ti.enable_trace
        junk = ti.visit(node.elt)
        t = []
        for node2 in node.generators:
            t2 = ti.visit(node2)
            t.extend(t2)
        if ti.has_failed(t):
            t = ti.merge_failures(t)
            if trace: ti.trace('failed inference',ti.format(node),t)
        else:
            t = ti.clean(t)
        return t
    #@+node:ekr.20140526082700.18375: *6* ti.IfExp (Ternary operator)
    # IfExp(expr test, expr body, expr orelse)

    def do_IfExp(self,node):
        
        ti = self    
        junk = ti.visit(node.test)
        t = ti.visit(node.body)
        t.extend(ti.visit(node.orelse))
        if ti.has_failed(t):
            t = ti.merge_failures(t)
        else:
            t = ti.clean(t)
        return t
    #@+node:ekr.20140526082700.18376: *6* ti.Index (default, at present)
    def do_Index(self,node):

        ti = self    
        return ti.visit(node.value)
    #@+node:ekr.20140526082700.18377: *6* ti.ListComp
    def do_ListComp(self,node):
        
        ti = self
        # ti.trace(node.elt,node.generators)
        junk = ti.visit(node.elt)
        t = []
        for node2 in node.generators:
            t.extend(ti.visit(node2))
        if ti.has_failed(t):
            t = ti.merge_failures(t)
        else:
            t = ti.clean(t)
        return t
    #@+node:ekr.20140526082700.18378: *6* ti.Slice
    def do_Slice(self,node):
        
        ti = self
        if node.upper: junk = ti.visit(node.upper)
        if node.lower: junk = ti.visit(node.lower)
        if node.step:  junk = ti.visit(node.step)
        return [ti.int_type] ### ???
    #@+node:ekr.20140526082700.18379: *6* ti.Subscript (*** to do)
    def do_Subscript(self,node):

        ti = self
        trace = False and not ti.enable_trace
        t1 = ti.visit(node.value)
        t2 = ti.visit(node.slice)
        if t1 and trace: g.trace(t1,t2,ti.format(node))
        return t1 ### ?
    #@+node:ekr.20140526082700.18380: *6* ti.UnaryOp
    def do_UnaryOp(self,node):
        
        ti = self
        trace = True and ti.enable_trace
        t = ti.visit(node.operand)
        t = ti.clean(t)
        op_kind = ti.kind(node.op)
        if op_kind == 'Not':
            t == [self.bool_type]
        elif t == [self.int_type] or t == [self.float_type]:
            pass # All operators are valid.
        else:
            ti.stats.n_unop_fail += 1
            if trace: g.trace(' fail:',op_kind,t,ti.format(node))
            t = [Unknown_Type(ti.call_hash,node)]
        return t
    #@+node:ekr.20140526082700.18381: *5* ti.primitive Types
    #@+node:ekr.20140526082700.18382: *6* ti.Builtin
    def do_Builtin(self,node):

        ti = self
        assert not ti.has_children(node)
        return [ti.builtin_type]

    #@+node:ekr.20140526082700.18383: *6* ti.Bytes
    def do_Bytes(self,node):

        ti = self
        assert not ti.has_children(node)    
        return [ti.bytes_type]
    #@+node:ekr.20140526082700.18384: *6* ti.Dict
    def do_Dict(self,node):

        ti = self
        junk = ti.visit_children(node)
        return [Dict_Type(node)]
            ### More specific type.
    #@+node:ekr.20140526082700.18385: *6* ti.List
    def do_List(self,node): 
                
        ti = self
        junk = ti.visit_children(node)
        return [List_Type(node)]
    #@+node:ekr.20140526082700.18386: *6* ti.Num
    def do_Num(self,node):
        
        ti = self
        assert not ti.has_children(node)
        t_num = Num_Type(node.n.__class__)
        # ti.trace(ti.format(node),'->',t_num)
        return [t_num]
    #@+node:ekr.20140526082700.18387: *6* ti.Str
    def do_Str(self,node):
        
        '''This represents a string constant.'''

        ti = self
        assert not ti.has_children(node)
        return [ti.string_type]
    #@+node:ekr.20140526082700.18388: *6* ti.Tuple
    def do_Tuple (self,node):

        ti = self
        junk = ti.visit_children(node)
        return [Tuple_Type(node)]
    #@+node:ekr.20140526082700.18389: *5* ti.statements
    #@+node:ekr.20140526082700.18390: *6* ti.For
    def do_For(self,node):
        
        ### what if target conflicts with an assignment??
        
        ti = self
        # ti.visit(node.iter)
        # ti.visit_list(node.body)
        # if node.orelse:
            # ti.visit_list(node.orelse)
            
        return ti.visit_children(node)
    #@+node:ekr.20140526082700.18391: *6* ti.Import (not used)
    # def do_Import(self,node):
        
        # pass
    #@+node:ekr.20140526082700.18392: *6* ti.ImportFrom (not used)
    # def do_ImportFrom(self,node):
        
        # pass
    #@+node:ekr.20140526082700.18393: *6* ti.Return & ti.Yield & helper
    def do_Return(self,node):
        ti = self
        return ti.return_helper(node)
        
    def do_Yield(self,node):
        ti = self
        return ti.return_helper(node)
        
    #@+node:ekr.20140526082700.18394: *7* ti.return_helper (sets cache)
    def return_helper(self,node):

        ti = self
        trace = False and ti.enable_trace
        trace_hash = False
        assert node
        e,hash_ = ti.call_e,ti.call_hash
        assert e
        assert hash_
        if node.value:
            t = ti.visit(node.value)
            if ti.has_failed(t):
                ti.stats.n_return_fail += 1
                t = ti.ignore_unknowns(t)
            if t:
                # Don't set the cache unless we succeed!
                ti.set_cache(node,t,tag=ti.format(node))
                ti.stats.n_return_success += 1
            else:
                ti.stats.n_return_fail += 1
                t = [] # Do **not** propagate a failure here!
        else:
            t = [ti.none_type]
        # Set the cache.
        t0 = ti.get_call_cache(e,hash_) or []
        t.extend(t0)
        ti.set_call_cache(e,hash_,t,tag='ti.return')
        if trace:
            if trace_hash: ti.trace(t,hash_,ti.format(node))
            else:          ti.trace(t,ti.format(node))
        return t
    #@+node:ekr.20140526082700.18395: *6* ti.With
    def do_With (self,node):

        ti = self
        t = ti.visit_list(node.body)
        # ti.trace(t)
        return t
    #@+node:ekr.20140526082700.18396: *5* ti.Name (***ivars don't work)
    def do_Name(self,node):
        
        ti = self
        trace = True and ti.enable_trace
        trace_hit = False ; trace_infer = False
        trace_fail = True ; trace_self = False
        ctx_kind = ti.kind(node.ctx)
        name = node.id
        trace = trace and name == 'i'
        hash_ = ti.call_hash
        
        # Reaching sets are useful only for Load attributes.
        if ctx_kind not in ('Load','Param'):
            # if trace: ti.trace('skipping %s' % ctx_kind)
            return []

        ### ast.Name nodes for class base names have no 'e' attr.
        if not hasattr(node,'e'):
            if trace: ti.trace('no e',node)
            return []

        t = ti.get_cache(node.e) or []
        t = ti.clean(t)
        t = ti.ignore_failures(t)
        if t:
            if trace and trace_hit: ti.trace('**hit!',t,name)
        elif name == 'self':
            e = node.e
            reach = getattr(e,'reach',[])
            if reach: ti.trace('**** assignment to self')
            cx = e.cx.class_context
            if cx:
                d = cx.ivars_dict
                if trace and trace_self: ti.trace('found self',e.name)
                    # ti.u.dump_ivars_dict(d)) # Very expensive
                t = [Class_Type(cx)]
            else:
                ti.trace('**** oops: no class context for self',ti.format(node))
                t = [Unknown_Type(ti.call_hash,node)]
        else:
            reach = getattr(node.e,'reach',[])
            t = []
            for node2 in reach:
                # The reaching sets are the RHS of assignments.
                t2 = ti.get_cache(node2)
                if t2 is None:
                    # Set the cache *before* calling ti.visit to terminate the recursion.
                    t = [Unknown_Type(ti.call_hash,node)]
                    ti.set_cache(node2,t,tag='ti.Name')
                    t2 = ti.visit(node2)
                    ti.set_cache(node2,t2,tag='ti.Name')
                if isinstance(t2,(list,tuple)):
                    t.extend(t2)
                else:
                    ti.trace('**oops:',t2,ti.format(node2))
            if ti.has_failed(t):
                t = ti.merge_failures(t)
            else:
                t = ti.clean(t)

        if trace and trace_infer and t:
            ti.trace('infer',t,ti.format(node))
        if trace and trace_fail and not t:
            ti.trace('fail ',name,ctx_kind,'reach:',
                ['%s:%s' % (id(z),ti.format(z)) for z in reach])
        return t
    #@-others
#@+node:ekr.20140526082700.18397: *3* Deduction stuff (keep)
#@+node:ekr.20140526082700.18398: *4* DeductionTraverser class
class DeductionTraverser (AstTraverser):

    '''A class to create all Deduction objects by traversing the AST.
    
    This second tree traversal happens after the scope-resolution pass
    has computed the ultimate Context for all names.
    '''

    #@+others
    #@+node:ekr.20140526082700.18399: *5*  dt.ctor
    def __init__(self,fn):

        # Init the base class: calls create_dispatch_table()
        AstTraverser.__init__(self,fn)
        
        self.in_arg_list = False
        self.in_lhs = False
        self.in_rhs = False
    #@+node:ekr.20140526082700.18400: *5*  dt.traverse
    def traverse (self,s):
        
        '''Perform all checks on the source in s.'''
        
        t1 = time.time()

        tree = ast.parse(s,filename=self.fn,mode='exec')

        t2 = time.time()
        self.u.stats.parse_time += t2-t1
        
        self.visit(tree)
        
        t3 = time.time()
        self.u.stats.pass1_time += t3-t2
    #@+node:ekr.20140526082700.18401: *5* dt.Contexts
    #@+node:ekr.20140526082700.18402: *6* dt.ClassDef
    # ClassDef(identifier name, expr* bases, stmt* body, expr* decorator_list)

    def do_ClassDef (self,tree):

        self.visit(tree.name)
        
        for z in tree.body:
            self.visit(z)
    #@+node:ekr.20140526082700.18403: *6* dt.FunctionDef
    # FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list)

    def do_FunctionDef (self,tree):
        
        self.visit(tree.name)
        
        # No deductions correspond to formal args.
            # assert self.kind(tree.args) == 'arguments'
            # for z in tree.args.args:
                # self.visit(z)
            # for z in tree.args.defaults:
                # self.visit(z)
        
        # Visit the body.
        for z in tree.body:
            self.visit(z)
    #@+node:ekr.20140526082700.18404: *6* dt.Module
    def do_Module (self,tree):

        for z in tree.body:
            self.visit(z)
    #@+node:ekr.20140526082700.18405: *5* dt.Operands
    #@+node:ekr.20140526082700.18406: *6* dt.Attribute (rewrite)
    def do_Attribute(self,tree):
        
        name = tree.attr
        
        # Use the *formatter* to traverse tree.value.
        expr = g_format_tree(tree.value)
        s = '%s.%s' % (expr,name)
        
        chain = cx.st.add_chain(tree,s)
        
        if use_deductions and self.in_rhs:
            if trace: g.trace('Adding chain to dependencies',chain)
            self.dependencies.append((ast,chain),)
        
        self.u.stats.n_attributes += 1
        return s
            
        
    #@+node:ekr.20140526082700.18407: *6* dt.bool
    # Python 2.x only.
    def do_bool(self,tree):
        pass
        
    #@+node:ekr.20140526082700.18408: *6* dt.Bytes
    # Python 3.x only.
    def do_Bytes(self,tree):
        pass

    #@+node:ekr.20140526082700.18409: *6* dt.Call
    def do_Call(self,tree):

        self.visit(tree.func)
        for z in tree.args:
            self.visit(z)
        for z in tree.keywords:
            self.visit(z)

        if hasattr(tree,'starargs') and tree.starargs:
            if self.isiterable(tree.starargs):
                for z in tree.starargs:
                    self.visit(z)
            else:# Bug fix: 2012/10/22: always visit the tree.
                self.visit(tree.starargs)

        if hasattr(tree,'kwargs') and tree.kwargs:
            if self.isiterable(tree.kwargs):
                for z in tree.kwargs:
                    self.visit(z)
            else:
                # Bug fix: 2012/10/22: always visit the tree.
                self.visit(tree.kwargs)
    #@+node:ekr.20140526082700.18410: *6* dt.comprehension
    def do_comprehension(self,tree):

        self.visit(tree.target)
        self.visit(tree.iter)
        for z in tree.ifs:
            self.visit(z)

    #@+node:ekr.20140526082700.18411: *6* dt.Dict
    def do_Dict(self,tree):

        for z in tree.keys:
            self.visit(z)
        for z in tree.values:
            self.visit(z)

    #@+node:ekr.20140526082700.18412: *6* dt.Ellipsis
    def do_Ellipsis(self,tree):
        pass

    #@+node:ekr.20140526082700.18413: *6* dt.ExtSlice
    def do_ExtSlice (self,tree):

        for z in tree.dims:
            self.visit(z)

    #@+node:ekr.20140526082700.18414: *6* dt.Index
    def do_Index (self,tree):

        self.visit(tree.value)

    #@+node:ekr.20140526082700.18415: *6* dt.int
    def do_int (self,s):
        pass

    #@+node:ekr.20140526082700.18416: *6* dt.Keyword
    def do_Keyword (self,tree):

        self.visit(tree.arg)
        self.visit(tree.value)

    #@+node:ekr.20140526082700.18417: *6* dt.List
    def do_List(self,tree):

        for z in tree.elts:
            self.visit(z)
        self.visit(tree.ctx)

    #@+node:ekr.20140526082700.18418: *6* dt.ListComp
    def do_ListComp(self,tree):

        self.visit(tree.elt)

        for z in tree.generators:
            self.visit(z)
            
    #@+node:ekr.20140526082700.18419: *6* dt.Name
    def do_Name(self,tree):

        name = tree.id # a string.

        # if isPython3:
            # if name in self.u.module_names:
                # return
        # else:
            # if name in dir(__builtin__) or name in self.u.module_names:
                # return
                
        ctx = self.visit(tree.ctx)
                
        if ctx == 'Load': # Most common.
            pass
        elif ctx == 'Store': # Next most common.
            pass
        elif ctx == 'Param':
            pass
        else:
            assert ctx == 'Del',ctx
            cx.del_names.add(name)
            self.u.stats.n_del_names += 1
    #@+node:ekr.20140526082700.18420: *6* dt.Num
    def do_Num(self,tree):
        pass

    #@+node:ekr.20140526082700.18421: *6* dt.Slice
    def do_Slice (self,tree):

        if hasattr(tree,'lower') and tree.lower is not None:
            self.visit(tree.lower)
        if hasattr(tree,'upper') and tree.upper is not None:
            self.visit(tree.upper)
        if hasattr(tree,'step') and tree.step is not None:
            self.visit(tree.step)

    #@+node:ekr.20140526082700.18422: *6* dt.Str
    def do_Str (self,tree):
        '''This represents a string constant.'''
        pass
    #@+node:ekr.20140526082700.18423: *6* dt.Subscript
    def do_Subscript(self,tree):

        self.visit(tree.slice)
        self.visit(tree.ctx)

    #@+node:ekr.20140526082700.18424: *6* dt.Tuple
    def do_Tuple(self,tree):

        for z in tree.elts:
            self.visit(z)
        self.visit(tree.ctx)
    #@+node:ekr.20140526082700.18425: *5* dt.Statements
    #@+node:ekr.20140526082700.18426: *6* dt.Assign
    def do_Assign(self,tree):
        
        val = self.visit(tree.value)
        
        for z in tree.targets:
            target = self.visit(z)
            Deduction(tree,self.assign_deducer,target,val)
    #@+node:ekr.20140526082700.18427: *6* dt.AugAssign
    def do_AugAssign(self,tree):

        Deduction(tree,
            self.visit(tree.op), # deducer method.
            self.visit(tree.target), # lhs
            self.visit(tree.value), # rhs
        )
    #@+node:ekr.20140526082700.18428: *6* dt.Call
    def do_Call(self,tree):

        f        = self.visit(tree.func)
        args     = [self.visit(z) for z in tree.args]
        keywords = [self.visit(z) for z in tree.keywords]
        starargs = self.visit(tree.starargs) if  hasattr(tree,'starargs') and tree.starargs else []
        kwargs   = self.visit(tree.kwargs) if hasattr(tree,'kwargs') and tree.kwargs else []
            
        Deduction(tree,self.call_deducer,f,args,keywords,starags,kwargs)
    #@+node:ekr.20140526082700.18429: *6* dt.For
    def do_For (self,tree):
        
        self.visit(tree.target)

        self.visit(tree.iter)
        
        for z in tree.body:
            self.visit(z)

        for z in tree.orelse:
            self.visit(z)
    #@+node:ekr.20140526082700.18430: *6* dt.Global
    def do_Global(self,tree):

        pass
    #@+node:ekr.20140526082700.18431: *6* dt.Import & helpers
    def do_Import(self,tree):

        pass
    #@+node:ekr.20140526082700.18432: *6* dt.ImportFrom
    def do_ImportFrom(self,tree):
        
        pass
    #@+node:ekr.20140526082700.18433: *6* dt.Lambda & helper
    def do_Lambda (self,tree):
        
        # Lambda args do not create deductions.
            # assert self.kind(tree) == 'arguments'
            # for z in tree.args.args:
                # self.visit(z)
            # for z in tree.args.defaults:
                # self.visit(z)
                
        self.visit(tree.body)
    #@+node:ekr.20140526082700.18434: *6* dt.Return
    def do_Return(self,tree):
        
        if tree.value:
            val = self.visit(tree.value)
            Deduction(tree,self.return_deducer,val)
        else:
            Deduction(tree,self.return_deducerd)
    #@+node:ekr.20140526082700.18435: *6* dt.With
    def do_With (self,tree):
        
        if hasattr(tree,'context_expression'):
            self.visit(tree.context_expresssion)

        if hasattr(tree,'optional_vars'):
            try:
                for z in tree.optional_vars:
                    self.visit(z)
            except TypeError: # Not iterable.
                self.visit(tree.optional_vars)
        
        for z in tree.body:
            self.visit(z)
    #@-others
#@+node:ekr.20140526082700.18436: *4* old Deduction ctor
def __init__ (sd,target,aList):
    
    if trace:
        name,obj = target
        deps = [b.short_description() for a,b in aList]
        g.trace('(Op) lhs: %s, aList: %s' % (name,deps))
    
    self.deps = aList
        # a list tuples (ast,s)
        # describing the symbols on which the target depends.
        # s is a string, either a plain id or an id chain.
        
    self.sd = sd

    self.target = target
        # A tuple (name,object) representing the target (LHS) of an assignment statement.
        # name is the spelling (a string) of the plain id or id chain.
        # object is a Chain for chains; a SymbolTableEntry for plain ids.
        # Note: chain.e is the SymbolTableEntry for chains.
        
    sd.n_dependencies += 1
    
    self.fold()
#@+node:ekr.20140526082700.18437: *4* e.become_known (To do)
def remove_symbol (self,e):
    
    '''The type of this SymbolTableEntry has just become known.
    
    Remove e from this Dependency.
    
    If the Dependency becomes known, do the following:
        
    - Call eval_ast to evaluate the type.
    - Assign the type to the Dependency's symbol.
    - Add the symbol to sd.known_types.
    '''
  
    e = self
    
    for dep in e.dependencies:
        dep.remove(e) # May add entries to sd.known_types.
    e.dependencies = []

    g.trace(e)
#@+node:ekr.20140526082700.18438: *4* e.is_known
def is_known (self):
    
    '''return True if this is a known symbol.'''
    
    return len(self.vals) == 1
#@-others
# Unit tests are the main program, at present.
# if __name__ == '__main__':
    # test()
#@@language python
#@@tabwidth -4
#@@pagewidth 60
#@-leo

# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20111116103733.9817: * @file leoInspect.py
#@@first

'''A scriptable framework for creating queries of Leo's object code.'''

#@@language python
#@@tabwidth -4
#@@pagewidth 60

#@+<< imports >>
#@+node:ekr.20111116103733.10440: **  << imports >> (leoInspect)
import sys
isPython3 = sys.version_info >= (3,0,0)

try:
    import leoStandAloneGlobals as g
except ImportError:
    pass # Will fail later.

# Used by ast-oriented code.
if not isPython3:
    import __builtin__

import ast
import glob
import imp
import os
import string
# import sys
import time
import types

if isPython3:
    import io
    StringIO = io.StringIO
else:
    import cStringIO
    StringIO = cStringIO.StringIO
#@-<< imports >>

# print('leoInspect.py: %s' % __file__)

g_dumper = None     # Global, singleton instance of AstDumper.
g_formatter = None  # Global, singleton instance of AstFormatter.

#@+<< to do >>
#@+node:ekr.20120609070048.11216: **  << to do >> (leoInspect)
#@@nocolor-node
#@+at
# 
# ** Improve cx.assignments_to.
# 
# - Allow "partial" matches in calls_to,assignments_to.
#     - Use regex searches?
# 
# - Append *all* statements to statements list.
#     Including def, class, if, while, pass, with etc.
# 
# - Verify that all kinds of name expressions & attributes are handled correctly.
# 
# - Create global lists for calls, assignments.
# 
# - Create global symbol dicts for names.
#@-<< to do >>
#@+<< naming conventions >>
#@+node:ekr.20111116103733.10146: **  << naming conventions >>
#@@nocolor-node
#@+at
# 
# The following naming conventions are used throughout:
# 
# a:    the AstTraverer class.
# cx:   a context.
# d:    a dict.
# e:    a SymbolTableEntry object.
# f:    the AstFormatter class.
# fn:   a file name.
# g:    the leo.core.leoGlobals module.
# it:   the InspectTraverser class.
# s:    a string.
# sd:   an instance of the SemanticData class.
# st:   a symbol table (for a particular context).
# tree: an AST (Abstract Syntax Tree), aka a parse tree,
#       ASTs are created by Python's ast module and modified by the AstTraverser.
# z:    a local temp.
#@-<< naming conventions >>
#@+<< define class AstTraverser >>
#@+node:ekr.20111116103733.10278: ** << define class AstTraverser >>
class AstTraverser(object):

    '''The base class for AST traversal helpers.'''

    #@+others
    #@+node:ekr.20111116103733.10279: *3*  a.Birth
    #@+node:ekr.20111116103733.10280: *4* a.ctor (AstTraverser)
    def __init__(self,fn=None):

        self.context_stack = []
        self.fn = fn or '<AstTraverser>'
        self.level = 0 # The indentation level (not the context level).
            # The number of parents a node has.
        self.parents = [None]

        self.init_dispatch_table()
        self.init_tracing()
    #@+node:ekr.20111116103733.10281: *4* a.init_dispatch_table
    def init_dispatch_table (self):

        a = ast

        self.dispatch_table = d = {
            int: self.do_int,
            str: self.do_str,
            a.alias: self.do_alias,
            # a.arg: self.do_arg,
                # Python 3.x only.
            a.arguments: self.do_arguments,
            a.comprehension: self.do_comprehension,
            a.keyword: self.do_Keyword,
            a.Add: self.do_Add,
            a.And: self.do_And,
            a.Assert: self.do_Assert,
            a.Assign: self.do_Assign,
            a.Attribute: self.do_Attribute,
            a.AugAssign: self.do_AugAssign,
            a.AugLoad: self.do_AugLoad,
            a.AugStore: self.do_AugStore,
            a.BinOp: self.do_BinOp,
            a.BitAnd: self.do_BitAnd,
            a.BitOr: self.do_BitOr,
            a.BitXor: self.do_BitXor,
            a.BoolOp: self.do_BoolOp,
            a.Break: self.do_Break,
            a.Call: self.do_Call,
            a.ClassDef: self.do_ClassDef,
            a.Compare: self.do_Compare,
            a.Continue: self.do_Continue,
            a.Del: self.do_Del,
            a.Delete: self.do_Delete,
            a.Dict: self.do_Dict,
            a.Div: self.do_Div,
            a.Ellipsis: self.do_Ellipsis,
            a.Eq: self.do_Eq,
            a.ExceptHandler: self.do_ExceptHandler,
            # a.Exec: self.do_Exec,
                # Python 2.x only.
            a.Expr: self.do_Expr,
            a.Expression: self.do_Expression,
            a.ExtSlice : self.do_ExtSlice ,
            a.FloorDiv: self.do_FloorDiv,
            a.For: self.do_For,
            a.FunctionDef: self.do_FunctionDef,
            a.GeneratorExp: self.do_GeneratorExp,
            a.Global: self.do_Global,
            a.Gt: self.do_Gt,
            a.GtE: self.do_GtE,
            a.If: self.do_If,
            a.IfExp: self.do_IfExp,
            a.Import: self.do_Import,
            a.ImportFrom: self.do_ImportFrom,
            a.In: self.do_In,
            a.Index : self.do_Index ,
            a.Interactive: self.do_Interactive,
            a.Invert: self.do_Invert,
            a.Is: self.do_Is,
            a.IsNot: self.do_IsNot,
            a.LShift : self.do_LShift ,
            a.Lambda: self.do_Lambda,
            a.List : self.do_List ,
            a.ListComp: self.do_ListComp,
            a.Load: self.do_Load,
            a.Lt: self.do_Lt,
            a.LtE: self.do_LtE,
            a.Mod: self.do_Mod,
            a.Module: self.do_Module,
            a.Mult: self.do_Mult,
            a.Name: self.do_Name,
            a.Not: self.do_Not,
            a.NotEq: self.do_NotEq,
            a.NotIn: self.do_NotIn,
            a.Num: self.do_Num,
            a.Or : self.do_Or ,
            a.Param: self.do_Param,
            a.Pass: self.do_Pass,
            a.Pow: self.do_Pow,
            # a.Print: self.do_Print,
                # Python 2.x only.
            a.RShift: self.do_RShift,
            a.Raise: self.do_Raise,
            # a.Repr: self.do_Repr,
                # Python 2.x only.
            a.Return: self.do_Return,
            a.Slice : self.do_Slice ,
            a.Store: self.do_Store,
            a.Str: self.do_Str,
            a.Sub: self.do_Sub,
            a.Subscript: self.do_Subscript,
            a.Suite: self.do_Suite,
            a.TryExcept: self.do_TryExcept,
            a.TryFinally: self.do_TryFinally,
            a.Tuple: self.do_Tuple,
            a.UAdd: self.do_UAdd,
            a.USub: self.do_USub,
            a.UnaryOp: self.do_UnaryOp,
            a.While: self.do_While,
            a.With: self.do_With,
            a.Yield: self.do_Yield,
        }

        if isPython3:
            d [a.arg]   = self.do_arg
            d [a.Bytes] = self.do_Bytes
        else:
            d [bool]    = self.do_bool
            d [a.Exec]  = self.do_Exec
            d [a.Print] = self.do_Print
            d [a.Repr]  = self.do_Repr
    #@+node:ekr.20111116103733.10283: *3*  a.Do-nothings
    # Don't delete these. They might be useful in a subclass.
    if 0:
        def do_arg(self,tree,tag=''): pass
        def do_arguments(self,tree,tag=''): pass
        def do_Add(self,tree,tag=''): pass
        def do_And(self,tree,tag=''): pass
        def do_Assert(self,tree,tag=''): pass
        def do_Assign(self,tree,tag=''): pass
        def do_Attribute(self,tree,tag=''): pass
        def do_AugAssign(self,tree,tag=''): pass
        def do_AugLoad(self,tree,tag=''): pass
        def do_AugStore(self,tree,tag=''): pass
        def do_BinOp(self,tree,tag=''): pass
        def do_BitAnd(self,tree,tag=''): pass
        def do_BitOr(self,tree,tag=''): pass
        def do_BitXor(self,tree,tag=''): pass
        def do_BoolOp(self,tree,tag=''): pass
        def do_Break(self,tree,tag=''): pass
        def do_Bytes(self,tree,tag=''): pass
        def do_Call(self,tree,tag=''): pass
        def do_ClassDef(self,tree,tag=''): pass
        def do_Compare(self,tree,tag=''): pass
        def do_Continue(self,tree,tag=''): pass
        def do_Del(self,tree,tag=''): pass
        def do_Delete(self,tree,tag=''): pass
        def do_Dict(self,tree,tag=''): pass
        def do_Div(self,tree,tag=''): pass
        def do_Ellipsis(self,tree,tag=''): pass
        def do_Eq(self,tree,tag=''): pass
        def do_Exec(self,tree,tag=''): pass
        def do_Expr(self,tree,tag=''): pass
        def do_Expression(self,tree,tag=''): pass
        def do_ExtSlice (self,tree,tag=''): pass
        def do_FloorDiv(self,tree,tag=''): pass
        def do_For(self,tree,tag=''): pass
        def do_FunctionDef(self,tree,tag=''): pass
        def do_GeneratorExp(self,tree,tag=''): pass
        def do_Global(self,tree,tag=''): pass
        def do_Gt(self,tree,tag=''): pass
        def do_GtE(self,tree,tag=''): pass
        def do_If(self,tree,tag=''): pass
        def do_IfExp(self,tree,tag=''): pass
        def do_Import(self,tree,tag=''): pass
        def do_ImportFrom(self,tree,tag=''): pass
        def do_In(self,tree,tag=''): pass
        def do_Index (self,tree,tag=''): pass
        def do_Interactive(self,tree,tag=''): pass
        def do_Invert(self,tree,tag=''): pass
        def do_Is(self,tree,tag=''): pass
        def do_IsNot(self,tree,tag=''): pass
        def do_Keyword(self,tree,tag=''): pass
        def do_LShift (self,tree,tag=''): pass
        def do_Lambda(self,tree,tag=''): pass
        def do_List (self,tree,tag=''): pass
        def do_ListComp(self,tree,tag=''): pass
        def do_Load(self,tree,tag=''): pass
        def do_Lt(self,tree,tag=''): pass
        def do_LtE(self,tree,tag=''): pass
        def do_Mod(self,tree,tag=''): pass
        def do_Module(self,tree,tag=''): pass
        def do_Mult(self,tree,tag=''): pass
        def do_Name(self,tree,tag=''): pass
        def do_Not(self,tree,tag=''): pass
        def do_NotEq(self,tree,tag=''): pass
        def do_NotIn(self,tree,tag=''): pass
        def do_Num(self,tree,tag=''): pass
        def do_Or (self,tree,tag=''): pass
        def do_Param(self,tree,tag=''): pass
        def do_Pass(self,tree,tag=''): pass
        def do_Pow(self,tree,tag=''): pass
        ## def do_Print(self,tree,tag=''): pass
        def do_RShift(self,tree,tag=''): pass
        def do_Raise(self,tree,tag=''): pass
        ## def do_Repr(self,tree,tag=''): pass
        def do_Return(self,tree,tag=''): pass
        def do_Slice (self,tree,tag=''): pass
        def do_Store(self,tree,tag=''): pass
        def do_Str(self,tree,tag=''): pass
        def do_Sub(self,tree,tag=''): pass
        def do_Subscript(self,tree,tag=''): pass
        def do_Suite(self,tree,tag=''): pass
        def do_TryExcept(self,tree,tag=''): pass
        def do_TryFinally(self,tree,tag=''): pass
        def do_Tuple(self,tree,tag=''): pass
        def do_UAdd(self,tree,tag=''): pass
        def do_USub(self,tree,tag=''): pass
        def do_UnaryOp(self,tree,tag=''): pass
        def do_While(self,tree,tag=''): pass
        def do_With(self,tree,tag=''): pass
        def do_Yield(self,tree,tag=''): pass
    #@+node:ekr.20111128103520.10427: *3*  a.do_default
    def do_default (self,tree,tag=''):

        g.trace('**** bad ast type',tree.__class__.__name__)
        return None

    #@+node:ekr.20111116103733.10284: *3*  a.error
    def error (self,tree,message):

        g.pr('Error: %s' % (message))

        if isinstance(tree,ast.AST):
            line = self.lines[tree.lineno-1]
            g.pr(line.rstrip())
    #@+node:ekr.20111116103733.10285: *3*  a.get/push/pop_context
    def get_context (self):

        return self.context_stack[-1]

    def push_context (self,context):

        assert context
        self.context_stack.append(context)

    def pop_context (self):

        self.context_stack.pop()
    #@+node:ekr.20111116103733.10286: *3*  a.run
    def run (self,s):

        tree = ast.parse(s,filename=self.fn,mode='exec')

        self.visit(tree,tag='top')

    #@+node:ekr.20111116103733.10287: *3*  a.visit
    def visit (self,tree,tag=None):

        '''Visit the ast tree node, dispatched by node type.'''

        trace = False
        kind = tree.__class__

        if isinstance(tree,ast.AST):
            tree._parent = self.parents[-1]

        self.level += 1
        self.parents.append(tree)
        try:
            # Return a value for use by subclases.
            f = self.dispatch_table.get(kind,self.do_default)
            return f(tree,tag)
        finally:
            self.level -= 1
            self.parents.pop()

        # Never put a return instruction in a finally clause!
        # It causes the exception to be lost!
        return None
    #@+node:ekr.20111116103733.10288: *3* a.Dumps
    #@+node:ekr.20111116103733.10289: *4* dump(AstTraverser)
    def dump (self,tree,asString=True,brief=False,outStream=None):

        AstDumper(brief=brief).dump(tree,outStream=outStream)

    #@+node:ekr.20111116103733.10291: *4* string_dump
    def string_dump (self,tree):

        if not isinstance(tree,ast.AST):
            g.trace('not an AST node')
            return ''

        after = g_node_after_tree(tree)
        lines = self.lines

        # Start with the first line.
        line = lines[tree.lineno-1] # 1-based line numbers.
        line = line[tree.col_offset:]
        result = [line]

        # Append the following lines up to the after node.
        if after:
            if after.lineno > tree.lineno:
                n = tree.lineno
                while n < after.lineno-2:
                    result.append(lines[n])
                    n += 1
            # Append the first part of the last line.
            line = lines[after.lineno-1]
            line = line[:after.col_offset]
            result.append(line)
        else:
            result.extend(lines[tree.lineno:])

        return ''.join(result)
    #@+node:ekr.20111116103733.10292: *3* a.Expressions
    def do_Expr(self,tree,tag=''):
        self.trace(tree,tag)
        self.visit(tree.value)

    def do_Expression(self,tree,tag=''):
        self.trace(tree,tag)
        self.visit(tree.body)

    def do_GeneratorExp(self,tree,tag=''):
        self.trace(tree,tag)
        self.visit(tree.elt)
        for z in tree.generators:
            self.visit(z)
    #@+node:ekr.20111116103733.10293: *4* a.IfExp
    def do_IfExp (self,tree,tag=''):
        self.trace(tree,tag)
        self.visit(tree.test)
        if tree.body:
            self.visit(tree.body)
        if tree.orelse:
            self.visit(tree.orelse)
    #@+node:ekr.20111116103733.10294: *4* a.Operands
    def do_Attribute(self,tree,tag=''):
        self.trace(tree,tag)
        self.visit(tree.value)
        self.visit(tree.attr)
        self.visit(tree.ctx)

    # Python 2.x only.
    def do_bool(self,tree,tag=''):
        pass

    # Python 3.x only.
    def do_Bytes(self,tree,tag=''):
        pass

    def do_Call(self,tree,tag=''):
        self.trace(tree,tag)
        self.visit(tree.func)
        for z in tree.args:
            self.visit(z)
        for z in tree.keywords:
            self.visit(z)
        if hasattr(tree,'starargs') and tree.starargs:
            if self.kind(tree.starargs) == 'Name':
                 self.visit(tree.starargs)
            elif self.isiterable(tree.starargs):
                for z in tree.starargs:
                    self.visit(z)
            else: g.trace('** unknown starargs kind',tree)
        if hasattr(tree,'kwargs') and tree.kwargs:
            if self.kind(tree.kwargs) == 'Name':
                 self.visit(tree.kwargs)
            elif self.isiterable(tree.kwargs):
                for z in tree.kwargs:
                    self.visit(z)
            else: g.trace('** unknown kwargs kind',tree)

    def do_comprehension(self,tree,tag=''):
        self.trace(tree,tag)
        self.visit(tree.target)
        self.visit(tree.iter)
        for z in tree.ifs:
            self.visit(z)

    def do_Dict(self,tree,tag=''):
        self.trace(tree,tag)
        for z in tree.keys:
            self.visit(z)
        for z in tree.values:
            self.visit(z)

    def do_Ellipsis(self,tree,tag=''):
        self.trace(tree,tag)

    def do_ExtSlice (self,tree,tag=''):
        self.trace(tree,tag)
        for z in tree.dims:
            self.visit(z)

    def do_Index (self,tree,tag=''):
        self.trace(tree,tag)
        self.visit(tree.value)

    def do_int (self,s,tag=''):
        self.trace(None,tag=tag,s=s,kind='int')

    def do_Keyword (self,tree,tag=''):
        self.trace(tree,tag)
        self.visit(tree.arg)
        self.visit(tree.value)

    def do_List(self,tree,tag=''):
        self.trace(tree,tag)
        for z in tree.elts:
            self.visit(z)
        self.visit(tree.ctx)

    def do_ListComp(self,tree,tag=''):
        self.trace(tree,tag)
        self.visit(tree.elt)
        for z in tree.generators:
            self.visit(z)

    def do_Name(self,tree,tag=''):
        self.trace(tree,tag)
        # tree.id is a string.
        self.visit(tree.id)
        self.visit(tree.ctx)

    def do_Num(self,tree,tag=''):
        tag = '%s: %s' % (tag,repr(tree.n))
        self.trace(tree,tag)

    def do_Slice (self,tree,tag=''):
        self.trace(tree,tag)
        if hasattr(tree,'lower') and tree.lower is not None:
            self.visit(tree.lower)
        if hasattr(tree,'upper') and tree.upper is not None:
            self.visit(tree.upper)
        if hasattr(tree,'step') and tree.step is not None:
            self.visit(tree.step)

    def do_str (self,s,tag=''):
        self.trace(None,tag=tag,s=s,kind='str')

    def do_Str (self,tree,tag=''):
        self.trace(None,tag=tag,s=tree.s,kind='Str')

    def do_Subscript(self,tree,tag=''):
        self.trace(tree,tag)
        self.visit(tree.slice)
        self.visit(tree.ctx)

    def do_Tuple(self,tree,tag=''):
        self.trace(tree,tag)
        for z in tree.elts:
            self.visit(z)
        self.visit(tree.ctx)
    #@+node:ekr.20111116103733.10295: *4* a.Operators
    # arguments = (expr* args, identifier? vararg, identifier? kwarg, expr* defaults)
    # -- keyword arguments supplied to call
    # keyword = (identifier arg, expr value)

    def do_arguments(self,tree,tag=''):

        assert self.kind(tree) == 'arguments'
        for z in tree.args:
            self.visit(z)

        for z in tree.defaults:
            self.visit(z)

        name = hasattr(tree,'vararg') and tree.vararg
        if name: pass

        name = hasattr(tree,'kwarg') and tree.kwarg
        if name: pass

    def do_arg(self,tree,tag=''):
        pass

    def do_BinOp (self,tree,tag=''):
        self.trace(tree,tag)
        self.visit(tree.op)
        self.visit(tree.right)
        self.visit(tree.left)

    def do_BoolOp (self,tree,tag=''):
        self.trace(tree,tag)
        self.visit(tree.op)
        for z in tree.values:
            self.visit(z)

    def do_Compare(self,tree,tag=''):
        self.trace(tree,tag)
        self.visit(tree.left)
        for z in tree.ops:
            self.visit(z)
        for z in tree.comparators:
            self.visit(z)

    def do_op(self,tree,tag=''):
        # This does nothing but specify the op type.
        self.trace(tree,tag)

    # operator = Add | BitAnd | BitOr | BitXor | Div
    # FloorDiv | LShift | Mod | Mult | Pow | RShift | Sub | 
    do_Add = do_op
    do_BitAnd = do_op
    do_BitOr = do_op
    do_BitXor = do_op
    do_Div = do_op
    do_FloorDiv = do_op
    do_LShift = do_op
    do_Mod = do_op
    do_Mult = do_op
    do_Pow = do_op
    do_RShift = do_op
    do_Sub = do_op

    # boolop = And | Or
    do_And = do_op 
    do_Or = do_op

    # cmpop = Eq | Gt | GtE | In | Is | IsNot | Lt | LtE | NotEq | NotIn
    do_Eq = do_op
    do_Gt = do_op
    do_GtE = do_op
    do_In = do_op
    do_Is = do_op
    do_IsNot = do_op
    do_Lt = do_op
    do_LtE = do_op
    do_NotEq = do_op
    do_NotIn = do_op

    # def do_expression_context(self,tree,tag=''):
        # self.trace(tree,tag)

    do_AugLoad = do_op
    do_AugStore = do_op
    do_Del = do_op
    do_Load = do_op
    do_Param = do_op
    do_Store = do_op

    def do_UnaryOp (self,tree,tag=''):
        self.trace(tree,tag)
        self.visit(tree.operand)

    # unaryop = Invert | Not | UAdd | USub
    do_Invert = do_UnaryOp
    do_Not = do_UnaryOp
    do_UAdd = do_UnaryOp
    do_USub = do_UnaryOp
    #@+node:ekr.20111116103733.10296: *3* a.Interactive & Module & Suite
    def do_Interactive(self,tree,tag=''):
        self.trace(tree,tag)
        for z in tree.body:
            self.visit(z)

    def do_Module (self,tree,tag=''):
        self.trace(tree,tag)
        for z in tree.body:
            self.visit(z)

    def do_Suite(self,tree,tag=''):
        self.trace(tree,tag)
        for z in tree.body:
            self.visit(z)
    #@+node:ekr.20111116103733.10297: *3* a.Statements
    #@+node:ekr.20111116103733.10298: *4* a.Statements (assignments)
    def do_Assign(self,tree,tag=''):

        self.trace(tree,tag)
        self.visit(tree.value)
        for z in tree.targets:
            self.visit(z)

    def do_AugAssign(self,tree,tag=''):

        self.trace(tree,tag)
        self.trace(tree.op)
        self.visit(tree.value)
        self.visit(tree.target)
    #@+node:ekr.20111116103733.10299: *4* a.Statements (classes & functions)
       # identifier name,
        # expr* bases,
        # stmt* body,
        # expr *decorator_list)

    def do_ClassDef (self,tree,tag=''):
        self.trace(tree,tag)
        self.visit(tree.name)
        for z in tree.body:
            self.visit(z)

    def do_FunctionDef (self,tree,tag=''):
        self.trace(tree,tag)
        self.visit(tree.name)
        for z in tree.body:
            self.visit(z)

    def do_Lambda (self,tree,tag=''):
        self.trace(tree,tag)
        self.visit(tree.args)
        self.visit(tree.body)
    #@+node:ekr.20111116103733.10300: *4* a.Statements (compound)
    def do_For (self,tree,tag=''):
        self.trace(tree,tag)
        self.visit(tree.target)
        self.visit(tree.iter)
        for z in tree.body:
            self.visit(z)
        for z in tree.orelse:
            self.visit(z)

    def do_If (self,tree,tag=''):
        self.trace(tree,tag)
        self.visit(tree.test)
        for z in tree.body:
            self.visit(z)
        for z in tree.orelse:
            self.visit(z)

    def do_With (self,tree,tag=''):
        self.trace(tree,tag)
        if hasattr(tree,'context_expression'):
            self.visit(tree.context_expresssion)
        if hasattr(tree,'optional_vars'):
            pass ### tree.optional_vars may be a name.
            # for z in tree.optional_vars:
                # self.visit(z)
        for z in tree.body:
            self.visit(z)

    def do_While (self,tree,tag=''):
        self.trace(tree,tag)
        self.visit(tree.test)
        for z in tree.body:
            self.visit(z)
        for z in tree.orelse:
            self.visit(z)
    #@+node:ekr.20111116103733.10301: *4* a.Statements (exceptions)
    def do_ExceptHandler(self,tree,tag=''):
        self.trace(tree,tag)
        if hasattr(tree,'type') and tree.type:
            self.visit(tree.type)
        if hasattr(tree,'name') and tree.name:
            self.visit(tree.name)
        for z in tree.body:
            self.visit(z)

    def do_Raise(self,tree,tag=''):
        self.trace(tree,tag)
        if hasattr(tree,'type') and tree.type is not None:
            self.visit(tree.type)
        if hasattr(tree,'inst') and tree.inst is not None:
            self.visit(tree.inst)
        if hasattr(tree,'tback') and tree.tback is not None:
            self.visit(tree.tback)

    def do_TryExcept(self,tree,tag=''):
        self.trace(tree,tag)
        for z in tree.body:
            self.visit(z)
        for z in tree.handlers:
            self.visit(z)
        for z in tree.orelse:
            self.visit(z)

    def do_TryFinally(self,tree,tag=''):
        self.trace(tree,tag)
        for z in tree.body:
            self.visit(z)
        for z in tree.finalbody:
            self.visit(z)
    #@+node:ekr.20111116103733.10302: *4* a.Statements (import) (AstTraverser)
    def do_Import(self,tree,tag=''):
        self.trace(tree,tag)
        for z in tree.names:
            self.visit(z)

    def do_ImportFrom(self,tree,tag=''):
        self.trace(tree,tag)
        self.visit(tree.module)
        if hasattr(tree,'level') and tree.level is not None:
            self.visit(tree.level)
        for z in tree.names:
            self.visit(z)

    # identifier name, identifier? asname)
    def do_alias(self,tree,tag=''):
        self.trace(tree,tag)
        self.visit(tree.name)
        if hasattr(tree,'asname') and tree.asname is not None:
            self.visit(tree.asname)

    #@+node:ekr.20111116103733.10303: *4* a.Statements (simple)
    def do_Assert(self,tree,tag=''):
        self.trace(tree,tag)
        self.visit(tree.test)
        if hasattr(tree,'msg') and tree.msg:
            self.visit(tree.msg)

    def do_Break(self,tree,tag=''):
        self.trace(tree,tag)

    def do_Continue(self,tree,tag=''):
        self.trace(tree,tag)

    def do_Delete(self,tree,tag=''):
        self.trace(tree,tag)
        for z in tree.targets:
            self.visit(z)

    # Python 2.x only
    def do_Exec(self,tree,tag=''):
        self.trace(tree,tag)
        self.visit(tree.body)
        if hasattr(tree,'globals') and tree.globals:
            self.visit(tree.globals)
        if hasattr(tree,'locals') and tree.locals:
            self.visit(tree.locals)

    def do_Global(self,tree,tag=''):
        self.trace(tree,tag)
        for z in tree.names:
            self.visit(z)

    def do_Pass(self,tree,tag=''):
        self.trace(tree,tag)

    # Python 2.x only
    def do_Print(self,tree,tag=''):
        self.trace(tree,tag)
        if hasattr(tree,'dest') and tree.dest:
            self.visit(tree.dest)
        for z in tree.values:
            self.visit(z)
        self.visit(tree.nl)

    # Python 2.x only
    def do_Repr(self,tree,tag=''):
        self.trace(tree,tag)
        self.visit(tree.value)

    def do_Return(self,tree,tag=''):
        self.trace(tree,tag)
        if tree.value:
            self.visit(tree.value)

    def do_Yield(self,tree,tag=''):
        self.trace(tree,tag)
        if hasattr(tree,'value') and tree.value:
            self.visit(tree.value)
    #@+node:ekr.20111116103733.10304: *3* a.Tools
    #@+at
    # Useful tools for tree traversal and testing.
    # 
    # Something is seriously wrong if we have to worry
    # about the speed of these tools.
    #@+node:ekr.20111116103733.10305: *4* a.isiterable
    def isiterable (self,anObject):

        '''Return True if a non-string is iterable.'''

        return getattr(anObject, '__iter__', False)
    #@+node:ekr.20111116103733.10306: *4* a.op_spelling
    def op_spelling (self,op):

        d = {
            'Add': '+', 'And': 'and',
            'BitAnd': '&', 'BitOr': '|', 'BitXor': '^', 'Div': '/',
            'Eq': '==', 'FloorDib': '//','Gt': '>', 'GtE': '>=',
            'In': 'in', 'Invert': '~', 'Is': 'is', 'IsNot': 'is not',
            'LShift': '<<', 'Lt': '<', 'LtE': '<=',
            'Mod': '%', 'Mult': '*',
            'Not': 'not', 'NotEq': '!=', 'NotIn':'not in',
            'Or': 'or','Pow': '**', 'RShift': '>>',
            'Sub': '-', 'UAdd': 'unary +', 'USub': 'unary -'
        }

        return d.get(op,'<unknown op %s>' % (op))
    #@+node:ekr.20111116103733.10307: *4* a.parents (not used)
    def parents (self,tree):

        '''A generator yielding all the parents of a node.'''

        assert tree == self.parentsList[-1]
        n = len(self.parentsList)-1 # Ignore tree.
        while n > 0:
            n -= 1
            yield self.parentsList[n]

    def self_and_parents (self,tree):

        '''A generator yielding tree and then all the parents of a node.'''

        assert tree == self.parentsList[-1]
        n = len(self.parentsList)
        while n > 0:
            n -= 1
            yield self.parentsList[n]
    #@+node:ekr.20111116103733.10308: *4* a.the_class, info & kind
    def the_class (self,tree):

        return tree.__class__

    def info (self,tree):

        return '%s: %9s' % (self.kind(tree),id(tree))

    def kind (self,tree):

        return tree.__class__.__name__

    #@+node:ekr.20111116103733.10309: *3* a.Tracing
    #@+node:ekr.20111116103733.10310: *4* init_tracing (AstTraverser)
    def init_tracing (self):

        '''May be over-ridden in subclasses.'''

        # May be over-ridden in subcalsses.
        self.trace_flag = False # Master switch.

        # Names of AST Nodes to trace, or 'all'.
        self.trace_kinds = ('Import','ImportFrom','alias',) # 'all',

        # Name of tags to trace.
        self.trace_tags = ()

        # Disable tracing for these kinds of trees.
        self.suppress_kinds = ('Attribute',)

        # Disable tracing for trees with these tags.
        self.suppress_tags = ('name context',)

        # Don't show these tags (but allow tracing if enabled).
        self.quiet_tags = ('body','module body',)
    #@+node:ekr.20111116103733.10311: *4* trace (AstTraverser)
    def trace (self,tree,tag='',kind='',s=''):

        # These are set in init_tracing
        trace_kinds = self.trace_kinds
        trace_tags = self.trace_tags
        suppress_kinds = self.suppress_kinds
        suppress_tags = self.suppress_tags
        quiet_tags = self.quiet_tags

        if not kind:
            kind = tree.__class__.__name__

        doTrace = (
            ('all' in trace_kinds or kind in trace_kinds or tag in trace_tags) and not
            (kind in suppress_kinds or tag in suppress_tags))

        if self.trace_flag and doTrace:
            indent = ' '*4*self.level
            if 'all' in quiet_tags or tag in quiet_tags:
                tag = ''
            if tag:
                if s:
                    g.pr('%s %s: %s: %s' % (indent,tag,kind,repr(s)))
                else:
                    g.pr('%s %s: %s' % (indent,tag,kind)) 
            else:
                if s:
                    g.pr('%s %s: %s' % (indent,kind,repr(s)))
                else:
                    g.pr('%s %s' % (indent,kind))
    #@-others
#@-<< define class AstTraverser >>
#@+<< define class Context >>
#@+node:ekr.20111116103733.10402: ** << define class Context >> (includes getters)
class Context(object):

    '''The base class of all context-related semantic data.

    All types ultimately resolve to a context.'''

    def __repr__ (self):
        return 'Context: %s' % (self.context_kind)

    __str__ = __repr__

    # Name is defined below.
    # def name(self):
        # '''Should be overriden by subclasses.'''
        # return 'Context at %s' % id(self)

    # def __cmp__ (self,other):
        # if   self.name() <  other.name(): return -1
        # elif self.name() == other.name(): return 0
        # else:                             return 1

    # def __hash__ (self):
        # return self.name()

    #@+others
    #@+node:ekr.20111116103733.10403: *3* cx ctor
    def __init__(self,tree,parent_context,sd,kind):

        self.is_temp_context = kind in ['comprehension','for','lambda','with']
        self.context_kind = kind
        # assert kind in ('class','comprehension','def','for','lambda','module','with'),kind
        self.formatter = sd.formatter
        self.parent_context = parent_context
        self.sd = sd
        self.st = SymbolTable(context=self)

        sd.n_contexts += 1

        # Public semantic data: accessed via getters.
        self.calls_list = [] # All call statements defined in this context.
        self.classes_list = [] # Classes defined in this context.
        self.defs_list = [] # Functions defined in this context.
        self.function_set = set()
        self.statements_list = [] # List of all statements in the context.
        self.tree_ptr = tree

        # Private semantic data: no getters.
        self.global_names = set() # Names that appear in a global statement in this context.
        self.temp_contexts = [] # List of inner 'comprehension','for','lambda','with' contexts.

        # Record the name.ctx contexts.
        self.del_names = set()      # Names with ctx == 'Del'
        self.load_names = set()     # Names with ctx == 'Load'
        self.param_names = set()    # Names with ctx == 'Param'
        self.store_names = set()    # Names with ctx == 'Store'

        # Data for the resolution algorithm.
        self.all_global_names = set() # Global names in all parent contexts.

        # Compute the class context.
        if self.context_kind == 'module':
            self.class_context = None
        elif self.context_kind == 'class':
            self.class_context = self
        else:
            self.class_context = parent_context.class_context

        # Compute the defining context.
        if self.is_temp_context:
            self.defining_context = parent_context.defining_context
        else:
            self.defining_context = self

        # Compute the module context.
        if self.context_kind == 'module':
            self.module_context = self
        else:
            self.module_context = parent_context.module_context
    #@+node:ekr.20120612044943.10220: *3* cx.__getstate__
    def __getstate__(self):

        '''Return the representation of the Context class for use by pickle.'''

        d = {
            'calls':        [repr(z) for z in self.calls_list],
            'classes':      [repr(z) for z in self.classes_list],
            'defs':         [repr(z) for z in self.defs_list],
            'statements':   [repr(z) for z in self.statements_list],
            'tree':         self.format(self.tree_ptr),
        }

        # g.trace('(Context)',d)
        return d
    #@+node:ekr.20120611094414.10891: *3* cx.utilities
    #@+node:ekr.20111116103733.10405: *4* cx.description & name
    def description (self):

        '''Return a description of this context and all parent contexts.'''

        if self.parent_context:
            return  '%s:%s' % (
                self.parent_context.description(),repr(self))
        else:
            return repr(self)

    # All subclasses override name.
    name = description
    #@+node:ekr.20111116103733.10407: *4* cx.dump
    def dump (self,level=0):

        if 1: # Just print the context
            print(' '*level,repr(self))
        if 0:
            self.st.dump(level=level)
        if 1:
            for z in self.classes_list:
                z.dump(level+1)
            for z in self.defs_list:
                z.dump(level+1)
        if 0:
            for z in self.temp_contexts:
                z.dump(level+1)
    #@+node:ekr.20120611094414.10881: *4* cx.format
    def format(self,obj=None):

        '''Return a string containing the human-readable version of the entire context.'''

        cx = self
        format = cx.formatter.format

        if not obj:
            return format(cx.tree_ptr)
        elif isinstance(obj,ast.AST):
            return format(obj)
        elif isinstance(obj,Context):
            return format(obj.tree_ptr)
        else:
            # Unexpected
            return '***cx.format: %s' % repr(obj)

    # format_tree = format
    #@+node:ekr.20111116103733.10404: *4* cx.tree_kind
    def tree_kind (self,tree):

        '''Return the class name of the tree node.'''

        return tree.__class__.__name__
    #@+node:ekr.20111116161118.10113: *3* cx.getters
    #@+node:ekr.20111116161118.10114: *4* cx.assignments & helper
    def assignments (self,all=True):

        if all:
            return self.all_assignments(result=None)
        else:
            return self.filter_assignments(self.statements_list)

    def all_assignments(self,result):

        if result is None:
            result = []
        result.extend(self.filter_assignments(self.statements_list))
        for aList in (self.classes_list,self.defs_list):
            for cx in aList:
                cx.all_assignments(result)
        return result

    def filter_assignments(self,aList):
        '''Return all the assignments in aList.'''
        return [z for z in aList
            if z.context_kind in ('assn','aug-assn')]
    #@+node:ekr.20111116161118.10115: *4* cx.assignments_to
    def assignments_to (self,s,all=True):

        format,result = self.formatter.format,[]

        for assn in self.assignments(all=all):
            tree = assn.tree()
            kind = self.tree_kind(tree)
            if kind == 'Assign':
                # Return the *entire* assignment if *any* of the targets match.
                # The caller will have to filter the result.
                for target in tree.targets:
                    if self.tree_kind(target) =='Name':
                        if target.id == s:
                            result.append(assn)
                            break
                    else:
                        lhs = format(target)
                        if lhs.startswith(s):
                            result.append(assn)
                            break
            else:
                assert kind == 'AugAssign',kind
                lhs = format(tree.target)
                if lhs.startswith(s):
                    result.append(assn)

        return result
    #@+node:ekr.20111116161118.10116: *4* cx.assignments_using
    def assignments_using (self,s,all=True):

        format,result = self.formatter.format,[]

        for assn in self.assignments(all=all):
            tree = assn.tree()
            kind = self.tree_kind(tree)
            assert kind in ('Assign','AugAssign'),kind
            rhs = format(tree.value)
            i = rhs.find(s,0)
            while -1 < i < len(rhs):
                if g.match_word(rhs,i,s):
                    result.append(assn)
                    break
                else:
                    i += len(s)

        return result
    #@+node:ekr.20111126074312.10386: *4* cx.calls & helpers
    def calls (self,all=True):

        if all:
            return self.all_calls(result=None)
        else:
            return self.filter_calls(self.calls_list)

    def all_calls(self,result):

        if result is None:
            result = []
        result.extend(self.calls_list)
        for aList in (self.classes_list,self.defs_list):
            for cx in aList:
                cx.all_calls(result)
        return result

    def filter_calls(self,aList):
        '''Return all the calls in aList.'''
        return [z for z in aList
            if z.context_kind == 'call']
    #@+node:ekr.20111126074312.10384: *4* cx.calls_to
    def calls_to (self,s,all=True):

        format,result = self.formatter.format,[]

        for call in self.calls(all=all):
            # g.trace(call.format())
            tree = call.tree()
            func = format(tree.func)
            if s == func:
                result.append(call)

        return result
    #@+node:ekr.20111126074312.10400: *4* cx.call_args_of
    def call_args_of (self,s,all=True):

        format,result = self.formatter.format,[]

        for call in self.calls(all=all):
            tree = call.tree()
            func = format(tree.func)
            if s == func:
                result.append(call)

        return result
    #@+node:ekr.20111116161118.10163: *4* cx.classes
    def classes (self,all=True):

        if all:
            return self.all_classes(result=None)
        else:
            return self.classes_list

    def all_classes(self,result):

        if result is None:
            result = []
        result.extend(self.classes_list)
        for aList in (self.classes_list,self.defs_list):
            for cx in aList:
                cx.all_classes(result)
        return result
    #@+node:ekr.20120626085227.11131: *4* cx.contexts (new)
    def contexts (self,include_temp=True):

        '''An iterator returning all contexts.'''

        yield self

        for cx in self.classes_list:
            for z in cx.contexts():
                yield z

        for cx in self.defs_list:
            for z in cx.contexts():
                yield z

        if include_temp:
            for cx in self.temp_contexts:
                for z in cx.contexts():
                    yield z

    #@+node:ekr.20111116161118.10164: *4* cx.defs
    def defs (self,all=True):

        if all:
            return self.all_defs(result=None)
        else:
            return self.defs_list

    def all_defs(self,result):

        if result is None:
            result = []
        result.extend(self.defs_list)
        for aList in (self.classes_list,self.defs_list):
            for cx in aList:
                cx.all_defs(result)
        return result
    #@+node:ekr.20111116161118.10152: *4* cx.functions & helpers
    def functions (self,all=True):

        if all:
            return self.all_functions(result=None)
        else:
            return self.filter_functions(self.defs_list)

    def all_functions(self,result):

        if result is None:
            result = []
        result.extend(self.filter_functions(self.defs_list))
        for aList in (self.classes_list,self.defs_list):
            for cx in aList:
                cx.all_functions(result)
        return result
    #@+node:ekr.20111116161118.10223: *5* cx.filter_functions & is_function
    def filter_functions(self,aList):
        return [z for z in aList if self.is_function(z)]

    def is_function(self,f):
        '''Return True if f is a function, not a method.'''
        return True
    #@+node:ekr.20111126074312.10449: *4* cx.line_number
    def line_number (self):

        return self.tree_ptr.lineno
    #@+node:ekr.20111116161118.10153: *4* cx.methods & helpers
    def methods (self,all=True):

        if all:
            return self.all_methods(result=None)
        else:
            return self.filter_methods(self.defs_list)

    def all_methods(self,result):

        if result is None:
            result = []
        result.extend(self.filter_methods(self.defs_list))
        for aList in (self.classes_list,self.defs_list):
            for cx in aList:
                cx.all_methods(result)
        return result
    #@+node:ekr.20111116161118.10225: *5* cx.filter_functions & is_function
    def filter_methods(self,aList):
        return [z for z in aList if self.is_method(z)]

    def is_method(self,f):
        '''Return True if f is a method, not a function.'''
        return True
    #@+node:ekr.20120626085227.11134: *4* cx.parent_contexts (new)
    def parent_contexts (self):

        cx = self
        result = []

        while cx.parent_context:
            result.append(cx.parent_context)
            cx = cx.parent_context

        result.reverse()
        return result
    #@+node:ekr.20111116161118.10165: *4* cx.statements
    def statements (self,all=True):

        if all:
            return self.all_statements(result=None)
        else:
            return self.statements_list

    def all_statements(self,result):

        if result is None:
            result = []
        result.extend(self.statements_list)
        for aList in (self.classes_list,self.defs_list):
            for cx in aList:
                cx.all_statements(result)
        return result
    #@+node:ekr.20111128103520.10259: *4* cx.token_range
    def token_range (self):

        tree = self.tree_ptr

        # return (
            # g.toUnicode(self.byte_array[:tree.col_offset]),
            # g.toUnicode(self.byte_array[:tree_end_col_offset]),
        # )

        if hasattr(tree,'col_offset') and hasattr(tree,'end_col_offset'):
            return tree.lineno,tree.col_offset,tree.end_lineno,tree.end_col_offset
        else:
            return -1,-1
    #@+node:ekr.20111116161118.10166: *4* cx.tree
    def tree(self):

        '''Return the AST (Abstract Syntax Tree) associated with this query object
        (Context Class).  This tree can be passed to the format method for printing.
        '''

        return self.tree_ptr
    #@-others
#@-<< define class Context >>

#@+others
#@+node:ekr.20111116103733.10540: **  inspect.module (Entry point)
def module (fn=None,s=None,sd=None,print_stats=False,print_times=False):

    if s:
        fn = '<string file>'
    else:
        # s = LeoCoreFiles().get_source(fn)
        s = g_get_source(fn)
        if not s:
            print('file not found: %s' % (fn))
            return None

    t1 = time.time()

    if not sd:
        sd = SemanticData(controller=None)
    InspectTraverser(fn,sd).traverse(s)
    module = sd.modules_dict.get(fn)

    sd.total_time += time.time()-t1

    if print_times: sd.print_times()
    if print_stats: sd.print_stats()

    return module
#@+node:ekr.20111116103733.10539: **  Top-level utilities
#@+node:ekr.20111116103733.10337: *3* g_chain_base
# This global function exists avoid duplicate code
# in the Chain and SymbolTable classes.

def g_chain_base (s):

    '''Return the base of the id chain s, a plain string.'''

    if s.find('.') == -1:
        # The chain is empty.
        g.trace('can not happen: empty base',s)
        return None
    else:
        base = s.split('.')[0]
        base = base.replace('()','').replace('[]','')
        # g.trace(base,s)
        return base
#@+node:ekr.20120609070048.10397: *3* g_dump
def g_dump(obj):

    global g_dumper

    if not g_dumper:
        g_dumper = AstDumper()

    dump = g_dumper.dumpTreeAsString

    if isinstance(obj,ast.AST):
        return dump(obj)
    elif isinstance(obj,Context):
        return dump(obj.tree_ptr)
    else:
        # Unexpected.
        return '***g_dump: %s' % repr(obj)
#@+node:ekr.20120625075849.10256: *3* g_files_in_dir
def g_files_in_dir (theDir,recursive=True,extList=None,excludeDirs=None):

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
            result.extend(glob.glob(theDir,'*%s' % (ext)))

    return sorted(list(set(result)))
#@+node:ekr.20120611094414.10582: *3* g_find_function_call
def g_find_function_call (tree):

    '''Return the static name of the function being called.

    tree is the tree.func part of the Call node.'''

    kind = tree.__class__.__name__

    if kind == 'str':
        s = tree
    elif kind == 'Name':
        s = tree.id
    elif kind == 'Attribute':
        s = g_find_function_call(tree.attr)
    else:
        # This is not an error.  Example:  (g())()
        s = '**unknown kind: %s**: %s' % (kind,g_format(tree))
        g.trace(s)

    return s
#@+node:ekr.20120609070048.10871: *3* g_format
def g_format(obj):

    '''Return a string containing the human-readable version of tree.'''

    global g_formatter

    if not g_formatter:
        g_formatter = AstFormatter()

    format = g_formatter.format

    if isinstance(obj,ast.AST):
        return format(obj)
    elif isinstance(obj,Context):
        return format(obj.tree_ptr)
    else:
        # Unexpected.
        return '***g_format: %s' % repr(obj)
#@+node:ekr.20120625092120.10573: *3* g_get_files_by_project_name
def g_get_files_by_project_name(name):

    leo_path,junk = g.os_path_split(__file__)

    d = { # Change these paths as required for your system.
        'coverage': (
            r'C:\Python26\Lib\site-packages\coverage-3.5b1-py2.6-win32.egg\coverage',
            ['.py'],['.bzr','htmlfiles']),
        'leo':(
            # r'C:\leo.repo\trunk\leo\core',
            leo_path,
            ['.py'],['.bzr']),
        'lib2to3': (
            r'C:\Python26\Lib\lib2to3',
            ['.py'],['tests']),
        'pylint': (
            r'C:\Python26\Lib\site-packages\pylint-0.25.1-py2.6.egg\pylint',
            ['.py'],['.bzr','test']),
        'rope': (
            r'C:\Python26\Lib\site-packages\rope',['.py'],['.bzr']),
    }

    data = d.get(name.lower())
    if not data:
        g.trace('bad project name: %s' % (name))
        return []

    theDir,extList,excludeDirs=data
    files = g_files_in_dir(theDir,recursive=True,extList=extList,excludeDirs=excludeDirs)

    if name.lower() == 'leo':
        for exclude in ['__init__.py','format-code.py']:
            files = [z for z in files if not z.endswith(exclude)]
        fn = g.os_path_join(theDir,'..','plugins','qtGui.py')
        files.append(fn)

    return files
#@+node:ekr.20120626085227.11133: *3* g_get_source (new)
def g_get_source (fn):

    try:
        f = open(fn,'r')
        s = f.read()
        f.close()
        return s
    except IOError:
        return '' # Caller gives error message.
#@+node:ekr.20120609070048.11466: *3* g_kind
def g_kind(obj):

    if not obj:
        return 'None'
    elif hasattr(obj,'__class__'):
        return obj.__class__.__name__
    else:
        # unexpected:
        return '***g_kind: %s' % repr(obj)
#@+node:ekr.20111116103733.10290: *3* g_node_after_tree
# The _parent must have been injected into all parent nodes for this to work.
# This will be so, because of the way in which visit traverses the tree.

def g_node_after_tree (tree):

    trace = False
    tree1 = tree # For tracing

    if not isinstance(tree,ast.AST):
        return None

    def children(tree):
        return [z for z in ast.iter_child_nodes(tree)]

    def parent(tree):
        if not hasattr(tree,'_parent'): g.trace('***no _parent: %s' % repr(tree))
        return hasattr(tree,'_parent') and tree._parent

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
        info = self.info # A bug found by stc.ScopeBinder!
        for z in (ast.Module,ast.ClassDef,ast.FunctionDef):
            if isinstance(tree1,z):
                g.trace('node: %22s, parent: %22s, after: %22s' % (
                    info(tree1),info(parent(tree1)),info(result)))
                break

    return result
#@+node:ekr.20111116103733.10257: ** class AstDumper
class AstDumper(object):

    '''A class that dumps ast trees in various formats.'''

    def __init__ (self,brief=False):

        self.banner = '\n%s\n' % ('='*20)
        self.brief = brief
        self.level = 0
        self.results = []
        self.setOptions()

        # Set by string_dump
        self.lines = []
        self.s = ''

    #@+others
    #@+node:ekr.20111116103733.10258: *3* setOptions
    def setOptions (self,
        annotate_fields = True,
            # True: include attribute names.
        include_attributes = False,
            # True: include lineno and col_offset attributes.
        stripBody = False,
        outStream = None
    ):

       self.annotate_fields = annotate_fields
       self.include_attributes = include_attributes
       self.stripBody = stripBody
       self.outStream = False
    #@+node:ekr.20111116103733.10259: *3* Top level (AstDumper)
    #@+node:ekr.20111116103733.10260: *4* dumpFileAsNodes/String
    def dumpFileAsNodes (self,fn,brief=False,outStream=None):

        '''Write the node representation of the closed file
        whose name is fn to outStream.'''

        s = self.read_input_file(fn)
        self.dumpStringAsNodes(fn,s,brief=brief,outStream=outStream)
        return s

    def dumpFileAsString (self,fn,brief=False,outStream=None):

        '''Write the string representation of the close file
        whose name is fn to outStream.'''

        s = self.read_input_file(fn)
        self.dumpStringAsString(s,brief=brief,outStream=outStream)
        return s
    #@+node:ekr.20111116103733.10261: *4* dumpStringAsNodes/String
    def dumpStringAsNodes (self,fn,s,brief=False,outStream=None):

        '''Write the node representation string s to outStream.'''

        tree = ast.parse(s,filename=fn,mode='exec')
        self.brief = brief
        s = self._dumpTreeAsNodes(tree)
        if outStream:
            self._writeAndClose(s,outStream)
        return s

    def dumpStringAsString(self,s,brief=False,outStream=None):

        '''Write the node representation string s to outStream.'''

        tree = ast.parse(s,filename='<string>',mode='exec')
        self.brief = brief
        s = self._dumpTreeAsString(tree)
        if outStream:
            self._writeAndClose(s,outStream)
        return s
    #@+node:ekr.20111116103733.10262: *4* dumpTreeAsNodes/String
    def dumpTreeAsNodes(self,tree,brief=False,outStream=None):

        '''Write the node representation the ast tree to outStream.'''

        s = self._dumpTreeAsNodes(tree,brief=brief)
        if outStream:
            self._writeAndClose(s,outStream)
        return s

    def dumpTreeAsString (self,tree,brief=False,outStream=None):

        '''Write the string representation the ast tree to outStream.'''

        s = self._dumpTreeAsString(tree,brief=brief)
        if outStream:
            self._writeAndClose(s,outStream)
        return s
    #@+node:ekr.20111116103733.10263: *3* Helpers
    #@+node:ekr.20111116103733.10264: *4* _dumpAstNode
    def _dumpAstNode(self,node,fieldname):

        # Visit the node.
        self._put(repr(node))
        # put(node.__class__.__name__,'name') # valid
        fields = ['%s: %s' % (name,repr(val))
            for name,val in ast.iter_fields(node)
                if val not in (None,(),[],{})]
        self._putList(fields) # ,'_fields')
        attrs = [z for z in list(node._attributes)
            if z not in ('lineno','col_offset',)]
        self._putList(attrs,'_attrs')

        # Visit the children
        delta = 4 # The number of spaces for each indentation.
        for child in ast.iter_child_nodes(node):
            self.level += delta
            self._dumpAstNode(child,'child')
            self.level -= delta
    #@+node:ekr.20111116103733.10265: *4* _dumpTreeAsNodes
    def _dumpTreeAsNodes(self,tree,brief=False):

        # annotate_fields=True,include_attributes=False):
        # self.annotate_fields = annotate_fields
        # self.include_attributes = include_attributes

        self.level = 0
        self.results = []
        self.brief = brief
        self._dumpAstNode(tree,fieldname='root')
        return '\n'.join(self.results)
    #@+node:ekr.20111116103733.10266: *4* _dumpTreeAsString (AstDumper) & helpers
    def _dumpTreeAsString (self,tree,brief=False):

        self.brief = brief

        s = ast.dump(tree,
            annotate_fields=self.annotate_fields,
            include_attributes=self.include_attributes)

        if self.stripBody:
            s = self._stripBody(s)

        if not brief:
            put_brackets = False
            s = self._indent(s,put_brackets)
            if put_brackets:
                s = self._compress(s) # Not needed if we don't print brackets.
            s = self._remove_cruft(s)
            if not put_brackets:
                s = self._compact(s)

        return s
    #@+node:ekr.20111116103733.10267: *5* _compress (used only if putting brackets)
    def _compress(self,s):

        '''Compress needlessly indented lines.'''

        i,result = 0,[]
        in_bracket = False # inside bracket or paren.
        start = 0 # start of bracket or paren.
        while i < len(s):
            progress = i
            ch = s[i]
            ch2 = i+1 < len(s) and s[i+1] or ''
            if ch in ('"',"'"):
                j = self._skipString(s,i)
                if not in_bracket:
                    result.append(s[i:j])
                i = j
            elif ch in '([':
                if ch2 in ')]':
                    if not in_bracket:
                        result.append(s[i:i+2])
                    i += 2
                else:
                    # Accumulate only one level of bracket or paren.
                    if in_bracket:
                        result.append(s[start:i])
                    start = i
                    i += 1
                    in_bracket = True
            elif ch in ')]':
                if in_bracket:
                    in_bracket = False
                    i += 1
                    s2 = s[start:i]
                    s3 = s2.replace(' ','').replace('\n','')
                    if len(s3) < 50:
                        result.append(s3)
                    else:
                        result.append(s2)
                else:
                    result.append(ch)
                    i += 1
            else:
                if not in_bracket:
                    result.append(ch)
                i += 1

            assert i > progress

        assert not in_bracket
        return ''.join(result)
    #@+node:ekr.20111116103733.10268: *5* _compact
    def _compact (self,s):

        '''Move closing brackets appearing on a separate line
        at the end of the previous line.'''

        result = []
        for line in g.splitLines(s):
            ch = line.strip()
            if len(ch) == 1 and ch in ')':
                last = result.pop()
                result.append(last.rstrip()+ch+'\n')
            elif line.strip():
                result.append(line)
        return ''.join(result)
    #@+node:ekr.20111116103733.10269: *5* _skip_block
    def _skip_block (self,s,i):

        delim1 = s[i]
        tags,tags2 = '([{',')]}'
        assert delim1 in tags
        delim2 = tags2[tags.find(delim1)]
        # g.trace(i,delim1,delim2)
        i += 1
        level = 1
        while i < len(s):
            progress = i
            ch = s[i]
            if ch in ('"',"'",):
                i = self._skipString(s,i)
            elif ch == delim1:
                level += 1 ; i += 1
            elif ch == delim2:
                level -= 1 ; i += 1
                if level <= 0: return i
            else: i += 1
            assert progress < i

        return i
    #@+node:ekr.20111116103733.10270: *5* _indent
    def _indent(self,s,put_brackets,level=0):
        '''Pretty print the output of ast.dump.'''
        i,result,indent = 0,[],level*4
        while i < len(s):
            progress = i
            ch = s[i]
            ch2 = i+1 < len(s) and s[i+1] or ''
            ch3 = i+2 < len(s) and s[i+2] or ''
            if ch in ('"',"'"):
                j = self._skipString(s,i)
                result.append(s[i:j])
                i = j
            elif s[i:i+4] == 'Str(':
                # Special case string: keep the string on the same line.
                result.append('Str(')
                i += 4
                indent += 4
            elif s[i:i+5]=='[...]':
                # Special case for the elision created by stripBody.
                result.append(s[i:i+5])
                i += 5
            elif ch in '([{':
                if ch2 in ')]}': # Assume the brackets match.
                    if True: # put_brackets:
                        # Put them in soe remove_cruft can take them out.
                        result.append(ch)
                        result.append(ch2) # Bug fix: 2011/04/04
                    elif ch == '[':
                        result.append('[...')
                    i += 2
                else:
                    i += 1
                    indent += 4
                    if put_brackets:
                        result.append('%s\n%s' % (ch,' '*indent))
                    elif ch == '[':
                        result.append('%s...\n%s' % (ch,' '*indent))
                    else:
                        result.append('\n%s' % (' '*indent))
            elif ch in ')]}':
                indent -= 4
                i += 1
                # 2011/04/05: Put closing paren on new line.
                # _remove_cruft will clean things up later.
                if put_brackets:
                    result.append('\n%s%s' % (' '*indent,ch))
                else:
                    result.append('\n%s' % (' '*indent))
            elif ch == ',':
                if ch2 in ')]}':
                    i += 1 # Skip the comma.
                    if ch3 == ' ':
                        i += 1 # Skip the blank
                else:
                    result.append('%s\n%s' % (ch,' ' *indent))
                    if ch2 == ' ':
                        i += 2 # Skip the comma and the blank.
                    else:
                        i += 1 # Skip the comma.
            elif ch == ' ':
                i += 1
            else:
                result.append(ch)
                i += 1
            assert i > progress
        return ''.join(result)
    #@+node:ekr.20111116103733.10271: *5* _remove_cruft
    def _remove_cruft (self,s):

        remove_empty_fields = True

        s = s.replace('ctx=Store()','ctx=Store')
        s = s.replace('ctx=Load()','ctx=Load')
        s = s.replace('ctx=Param()','ctx=Param')

        table = (
            # 'ctx=Store',
            # 'ctx=Load',
            # 'ctx=Param',
            'args=[]',
            'bases=[]',
            'decorator_list=[]',
            'defaults=[]',
            'keywords=[]',
            'kwarg=None',
            'kwargs=None',
            'starargs=None',
            'vararg=None',
        )

        if remove_empty_fields:
            result = []
            for line in g.splitLines(s):
                found = False
                for s2 in table:
                    found = line.find(s2) > -1
                    if found:
                        if line.find(s2+',') > -1:
                            line = line.replace(s2+',','')
                        elif line.find(','+s2) > -1:
                            line = line.replace(','+s2,'')
                        else:
                            line = line.replace(s2,'')
                        if line.strip():
                            result.append(line)
                        break
                else:
                    result.append(line)
            s = ''.join(result)

        # Removing trailing commas helps _compact a lot.
        # Should be safe: strings do not cross lines.
        s = s.replace(',\n','\n')
        return s

    #@+node:ekr.20111116103733.10272: *5* _stripBody
    def _stripBody(self,s):

        '''Abbreviate the top-level body list.'''

        for tag in ('ClassDef','FunctionDef','Module'):
            if s.strip().startswith(tag):
                break
        else:
            return s

        i = s.find('body=[')
        if i > -1:
            return s[:i] + 'body=[...])'
        else:
            return s
    #@+node:ekr.20111116103733.10273: *4* _put & _putList
    def _put(self,s,tag=''):

        ws = ' '*self.level
        if tag: tag = '%s:' % tag
        self.results.append('%s%s%s' % (ws,tag,s))

    def _putList(self,aList,tag=''):

        for z in aList:
            self._put(z,tag)
    #@+node:ekr.20111116103733.10274: *4* _skipString
    def _skipString(self,s,i):

        '''Scan forward to the end of a string.'''

        delim = s[i] ; i += 1
        assert delim in ('"',"'",)

        while i < len(s):
            ch = s[i]
            if ch == '\\':
                i += 2
            elif ch == delim:
                return i+1
            else:
                i += 1
        else:
            return len(s)
    #@+node:ekr.20111116103733.10275: *4* _writeAndClose
    def _writeAndClose (self,s,outStream=None):

        s = g.toUnicode(s)

        if outStream:
            g.es_print('writing',outStream.name)
            outStream.write(s)
            outStream.close()
        else:
            print(s)
    #@+node:ekr.20111116103733.10276: *4* error (AstDumper)
    def error (self,s):

        g.error(s)
    #@+node:ekr.20111116103733.10277: *4* read_input_file
    def read_input_file (self,fn):

        if g.os_path_exists(fn):
            try:
                return open(fn,'r').read()
            except IOError:
                pass

        self.error('can not open %s' % fn)
        return ''
    #@-others
#@+node:ekr.20111117031039.10133: ** class AstFormatter (AstTraverser)
class AstFormatter(AstTraverser):

    '''A class to recreate source code from an AST.

    This does not have to be perfect, but it should be close.

    Also supports optional annotations such as line numbers, file names, etc.
    '''

    #@+others
    #@+node:ekr.20111125131712.10297: *3*  f.ctor
    def __init__ (self,fn=None,options=None):

        AstTraverser.__init__(self,fn)
            # Init the base class.
            # Sets the dispatch table.
            # Calls init_tracing.

        self.fn = fn
        self.level = 0 # Indentation level.
        self.options = options or {}
    #@+node:ekr.20111117031039.10260: *3* f.format
    def format (self,tree):

        return self.visit(tree)
    #@+node:ekr.20120614011356.10093: *3* f.indent
    def indent (self,s):

        return '%s%s' % (' '*self.level,s)
    #@+node:ekr.20111117031039.10395: *3* f.visit
    bad_names = []

    def visit (self,tree):

        '''Visit the ast tree node, dispatched by node type.'''

        kind = tree.__class__
        f = self.dispatch_table.get(kind)
        if f:
            return f(tree)
            # val = f(tree)
            # if val is None and f.__name__ not in self.bad_names:
                # g.trace('returns None: %s',f.__name__)
                # self.bad_names.append(f.__name__)
                # val = '*** None'
            # return val
        else:
            s = '<bad ast type: %s>' % kind
            g.trace('**** %s' % s)
            return s
    #@+node:ekr.20111117031039.10193: *3* f.Contexts
    #@+node:ekr.20111117031039.10194: *4* f.ClassDef
    # ClassDef(identifier name, expr* bases, stmt* body, expr* decorator_list)

    def do_ClassDef (self,tree):

        result = []
        name = self.visit(tree.name)
        bases = [self.visit(z) for z in tree.bases] if tree.bases else []

        if bases:
            result.append(self.indent('class %s(%s):\n' % (name,','.join(bases))))
        else:
            result.append(self.indent('class %s:\n' % name))

        for z in tree.body:
            self.level += 1
            result.append(self.visit(z))
            self.level -= 1

        return ''.join(result)
    #@+node:ekr.20111117031039.10195: *4* f.FunctionDef
    # FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list)

    def do_FunctionDef (self,tree):

        result = []

        if tree.decorator_list:
            for z in tree.decorator_list:
                result.append('@%s\n' % self.visit(z))

        name = self.visit(tree.name)
        args = self.visit(tree.args) if tree.args else ''

        result.append(self.indent('def %s(%s):\n' % (name,args)))

        for z in tree.body:
            self.level += 1
            result.append(self.visit(z))
            self.level -= 1

        return ''.join(result)
    #@+node:ekr.20111117031039.10197: *4* f.Module
    def do_Module (self,tree):

        return ''.join([self.visit(z) for z in  tree.body])
    #@+node:ekr.20120614011356.10107: *3* f.Exceptions
    #@+node:ekr.20120614011356.10091: *4* f.ExceptHandler
    def do_ExceptHandler(self,tree):

        result = []
        result.append(self.indent('except'))

        if hasattr(tree,'type') and tree.type:
            result.append(' %s' % self.visit(tree.type))

        if hasattr(tree,'name') and tree.name:
            result.append(' as %s' % self.visit(tree.name))

        result.append(':\n')

        for z in tree.body:
            self.level += 1
            result.append(self.visit(z))
            self.level -= 1

        return ''.join(result)
    #@+node:ekr.20120614011356.10092: *4* f.TryExcept
    def do_TryExcept(self,tree):

        result = []
        result.append(self.indent('try:\n'))

        for z in tree.body:
            self.level += 1
            result.append(self.visit(z))
            self.level -= 1

        assert tree.handlers
        for z in tree.handlers:
            result.append(self.visit(z))

        if tree.orelse:
            result.append('else:\n')
            for z in tree.orelse:
                self.level += 1
                result.append(self.visit(z))
                self.level -= 1

        return ''.join(result)
    #@+node:ekr.20120614011356.10089: *4* f.TryFinally
    def do_TryFinally(self,tree):

        result = []
        result.append(self.indent('try:\n'))

        for z in tree.body:
            self.level += 1
            result.append(self.visit(z))
            self.level -= 1

        result.append(self.indent('finally:\n'))
        for z in tree.finalbody:
            self.level += 1
            result.append(self.visit(z))
            self.level -= 1

        return ''.join(result)
    #@+node:ekr.20111117031039.10198: *3* f.Operands
    #@+node:ekr.20120614011356.10103: *4* f.Expr & Expression
    def do_Expr(self,tree):

        '''An outer expression: must be indented.'''

        return self.indent('%s\n' % self.visit(tree.value))

    def do_Expression(self,tree):

        '''An inner expression: do not indent.'''

        return '%s\n' % self.visit(tree.body)
    #@+node:ekr.20111117031039.10696: *4* f.arg
    def do_arg(self,tree):

        return self.visit(tree.arg)
    #@+node:ekr.20111117031039.10683: *4* f.arguments
    # arguments = (expr* args, identifier? vararg, identifier? kwarg, expr* defaults)
    # -- keyword arguments supplied to call
    # keyword = (identifier arg, expr value)

    def do_arguments(self,tree):

        kind = self.kind(tree)
        assert kind == 'arguments',kind

        args     = [self.visit(z) for z in tree.args]
        defaults = [self.visit(z) for z in tree.defaults]

        # Assign default values to the last args.
        args2 = []
        n_plain = len(args) - len(defaults)
        for i in range(len(args)):
            if i < n_plain:
                args2.append(args[i])
            else:
                args2.append('%s=%s' % (args[i],defaults[i-n_plain]))

        # Now add the vararg and kwarg args.
        name = hasattr(tree,'vararg') and tree.vararg
        if name: args2.append('*'+name)

        name = hasattr(tree,'kwarg') and tree.kwarg
        if name: args2.append('**'+name)

        return ','.join(args2)
    #@+node:ekr.20111117031039.10199: *4* f.Attribute & helper
    # Attribute(expr value, identifier attr, expr_context ctx)

    def do_Attribute(self,tree):

        return '%s.%s' % (
            self.visit(tree.value),
            self.visit(tree.attr))
    #@+node:ekr.20111117031039.10208: *4* f.Call
    def do_Call(self,tree):

        func = self.visit(tree.func)

        args = [self.visit(z) for z in tree.args]

        for z in tree.keywords:
            args.append(self.visit(z))

        if hasattr(tree,'starargs') and tree.starargs:
            args.append('*%s' % (self.visit(tree.starargs)))

        if hasattr(tree,'kwargs') and tree.kwargs:
            args.append('**%s' % (self.visit(tree.kwargs)))

        return '%s(%s)' % (func,','.join(args))
    #@+node:ekr.20111117031039.10558: *4* f.Dict
    def do_Dict(self,tree):

        result = []
        keys   = [self.visit(z) for z in tree.keys]
        values = [self.visit(z) for z in tree.values]

        if len(keys) == len(values):
            result.append('{\n' if keys else '{')
            items = []
            for i in range(len(keys)):
                items.append('  %s:%s' % (keys[i],values[i]))
            result.append(',\n'.join(items))
            result.append('\n}' if keys else '}')
        else:
            g.trace('*** Error *** keys: %s values: %s' % (
                repr(keys),repr(values)))

        return ''.join(result)
    #@+node:ekr.20111117031039.10572: *4* f.ExtSlice
    def do_ExtSlice (self,tree):

        return ':'.join([self.visit(z) for z in tree.dims])
    #@+node:ekr.20120614011356.10104: *4* f.Generator
    def do_GeneratorExp(self,tree):

        elt  = self.visit(tree.elt)

        gens = [self.visit(z) for z in tree.generators]

        return '<gen %s for %s>' % (elt,','.join(gens))
    #@+node:ekr.20111117031039.10571: *4* f.Index
    def do_Index (self,tree):

        return self.visit(tree.value)
    #@+node:ekr.20111117031039.10354: *4* f.Keyword
    # keyword = (identifier arg, expr value)

    def do_Keyword(self,tree):

        # tree.arg is a string.
        val = self.visit(tree.value)

        # This is a keyword *arg*, not a Python keyword!
        return '%s=%s' % (tree.arg,val)
    #@+node:ekr.20111117031039.10567: *4* f.List
    def do_List(self,tree):

        # Not used: list context.
        # self.visit(tree.ctx)

        elts = [self.visit(z) for z in tree.elts]
        return '[%s]' % ','.join(elts)
    #@+node:ekr.20111117031039.10204: *4* f.ListComp & Comprehension
    def do_ListComp(self,tree):

        elt = self.visit(tree.elt)

        gens = [self.visit(z) for z in tree.generators]

        return '[%s for %s]' % (elt,''.join(gens))

    def do_comprehension(self,tree):

        result = []
        name = self.visit(tree.target) # A name.
        it   = self.visit(tree.iter) # An attribute.

        result.append('%s in %s' % (name,it))

        ifs = [self.visit(z) for z in tree.ifs]
        if ifs:
            result.append(' if %s' % (''.join(ifs)))

        return ''.join(result)
    #@+node:ekr.20111117031039.10203: *4* f.Name
    def do_Name(self,tree):

        return tree.id
    #@+node:ekr.20120614011356.10080: *4* f.Repr
    # Python 2.x only
    def do_Repr(self,tree):

        return 'repr(%s)' % self.visit(tree.value)
    #@+node:ekr.20111117031039.10573: *4* f.Slice
    def do_Slice (self,tree):

        lower,upper,step = '','',''

        if hasattr(tree,'lower') and tree.lower is not None:
            lower = self.visit(tree.lower)

        if hasattr(tree,'upper') and tree.upper is not None:
            upper = self.visit(tree.upper)

        if hasattr(tree,'step') and tree.step is not None:
            step = self.visit(tree.step)

        if step:
            return '%s:%s:%s' % (lower,upper,step)
        else:
            return '%s:%s' % (lower,upper)
    #@+node:ekr.20111117031039.10455: *4* f.Str & str
    def do_str (self,s):

        return s # Not repr(s)

    def do_Str (self,tree):

        return repr(tree.s)

    #@+node:ekr.20111117031039.10574: *4* f.Subscript
    # Subscript(expr value, slice slice, expr_context ctx)

    def do_Subscript(self,tree):

        value = self.visit(tree.value)

        the_slice = self.visit(tree.slice)

        return '%s[%s]' % (value,the_slice)
    #@+node:ekr.20111117031039.10560: *4* f.Tuple
    def do_Tuple(self,tree):

        elts = [self.visit(z) for z in tree.elts]

        return '(%s)' % ','.join(elts)
    #@+node:ekr.20111117031039.10557: *4* formatter:simple operands
    # Python 2.x only.
    def do_bool(self,tree):
        return '' ###

    # Python 3.x only.
    def do_Bytes(self,tree):
        assert isPython3
        return str(tree.s)

    def do_Ellipsis(self,tree):
        return '...'

    def do_int (self,s):
        return s

    def do_Num(self,tree):
        return repr(tree.n)
    #@+node:ekr.20111117031039.10421: *3* f.Operators
    #@+node:ekr.20111117031039.10487: *4* f.BinOp
    def do_BinOp (self,tree):

        return '%s%s%s' % (
            self.visit(tree.left),
            self.visit(tree.op),
            self.visit(tree.right))

    #@+node:ekr.20111117031039.10488: *4* f.BoolOp
    def do_BoolOp (self,tree):

        op = self.visit(tree.op)

        values = [self.visit(z) for z in tree.values]

        return op.join(values)

    #@+node:ekr.20111117031039.10489: *4* f.Compare
    def do_Compare(self,tree):

        result = []
        lt    = self.visit(tree.left)
        ops   = [self.visit(z) for z in tree.ops]
        comps = [self.visit(z) for z in tree.comparators]

        result.append(lt)

        if len(ops) == len(comps):
            for i in range(len(ops)):
                result.append('%s%s' % (ops[i],comps[i]))
        else:
            g.trace('ops',repr(ops),'comparators',repr(comps))

        return ''.join(result)
    #@+node:ekr.20111117031039.10495: *4* f.UnaryOp
    def do_UnaryOp (self,tree):

        return self.visit(tree.operand)
    #@+node:ekr.20111117031039.10491: *4* f.arithmetic operators
    # operator = Add | BitAnd | BitOr | BitXor | Div
    # FloorDiv | LShift | Mod | Mult | Pow | RShift | Sub | 

    def do_Add(self,tree):       return '+'
    def do_BitAnd(self,tree):    return '&'
    def do_BitOr(self,tree):     return '|'
    def do_BitXor(self,tree):    return '^'
    def do_Div(self,tree):       return '/'
    def do_FloorDiv(self,tree):  return '//'
    def do_LShift(self,tree):    return '<<'
    def do_Mod(self,tree):       return '%'
    def do_Mult(self,tree):      return '*'
    def do_Pow(self,tree):       return '**'
    def do_RShift(self,tree):    return '>>'
    def do_Sub(self,tree):       return '-'
    #@+node:ekr.20111117031039.10490: *4* f.boolean operators
    # boolop = And | Or
    def do_And(self,tree):   return ' and '
    def do_Or(self,tree):    return ' or '
    #@+node:ekr.20111117031039.10492: *4* f.comparison operators
    # cmpop = Eq | Gt | GtE | In | Is | IsNot | Lt | LtE | NotEq | NotIn
    def do_Eq(self,tree):    return '=='
    def do_Gt(self,tree):    return '>'
    def do_GtE(self,tree):   return '>='
    def do_In(self,tree):    return ' in '
    def do_Is(self,tree):    return ' is '
    def do_IsNot(self,tree): return ' is not '
    def do_Lt(self,tree):    return '<'
    def do_LtE(self,tree):   return '<='
    def do_NotEq(self,tree): return '!='
    def do_NotIn(self,tree): return ' not in '
    #@+node:ekr.20120609070048.11084: *4* f.ternary op (ifExp)
    def do_IfExp (self,tree):

        return '%s if %s else %s ' % (
            self.visit(tree.body),
            self.visit(tree.test),
            self.visit(tree.orelse))
    #@+node:ekr.20111117031039.10493: *4* f.expression operators
    def do_op(self,tree):
        return ''

    do_AugLoad  = do_op
    do_AugStore = do_op
    do_Del      = do_op
    do_Load     = do_op
    do_Param    = do_op
    do_Store    = do_op
    #@+node:ekr.20111117031039.10494: *4* f.unary opertors
    # unaryop = Invert | Not | UAdd | USub

    def do_Invert(self,tree):   return '~'
    def do_Not(self,tree):      return ' not '
    def do_UAdd(self,tree):     return '+'
    def do_USub(self,tree):     return '-'
    #@+node:ekr.20111117031039.10205: *3* f.Statements
    #@+node:ekr.20120614011356.10084: *4* f.Assert
    def do_Assert(self,tree):

        test = self.visit(tree.test)

        if hasattr(tree,'msg') and tree.msg:
            message = self.visit(tree.msg)
            return self.indent('assert %s, %s' % (test,message))
        else:
            return self.indent('assert %s' % test)
    #@+node:ekr.20111117031039.10206: *4* f.Assign
    def do_Assign(self,tree):

        val = self.visit(tree.value)

        assns = ['%s=%s\n' % (self.visit(z),val) for z in tree.targets]

        return ''.join([self.indent(z) for z in assns])
    #@+node:ekr.20111117031039.10207: *4* f.AugAssign
    def do_AugAssign(self,tree):

        return self.indent('%s%s=%s\n' % (
            self.visit(tree.target),
            self.visit(tree.op),
            self.visit(tree.value)))
    #@+node:ekr.20120614011356.10083: *4* f.Break and f.Continue
    def do_Break(self,tree):

        return self.indent('break\n')

    def do_Continue(self,tree):

        return self.indent('continue\n')
    #@+node:ekr.20120614011356.10085: *4* f.Delete
    def do_Delete(self,tree):

        targets = [self.visit(z) for z in tree.targets]

        return self.indent('del %s\n' % ','.join(targets))
    #@+node:ekr.20120614011356.10082: *4* f.Exec
    # Python 2.x only
    def do_Exec(self,tree):

        body = self.visit(tree.body)

        args = [] # Globals before locals.

        if hasattr(tree,'globals') and tree.globals:
            args.append(self.visit(tree.globals))

        if hasattr(tree,'locals') and tree.locals:
            args.append(self.visit(tree.locals))

        if args:
            return self.indent('exec %s in %s\n' % (
                body,','.join(args)))
        else:
            return self.indent('exec %s\n' % (body))
    #@+node:ekr.20111117031039.10209: *4* f.For
    def do_For (self,tree):

        result = []

        result.append(self.indent('for %s in %s:\n' % (
            self.visit(tree.target),
            self.visit(tree.iter))))

        for z in tree.body:
            self.level += 1
            result.append(self.visit(z))
            self.level -= 1

        if tree.orelse:
            result.append(self.indent('else:\n'))
            for z in tree.orelse:
                self.level += 1
                result.append(self.visit(z))
                self.level -= 1

        return ''.join(result)
    #@+node:ekr.20111117031039.10210: *4* f.Global
    def do_Global(self,tree):

        return self.indent('global %s\n' % (
            ','.join(tree.names)))
    #@+node:ekr.20120614011356.10077: *4* f.If
    def do_If (self,tree):

        result = []

        result.append(self.indent('if %s:\n' % (
            self.visit(tree.test))))

        for z in tree.body:
            self.level += 1
            result.append(self.visit(z))
            self.level -= 1

        if tree.orelse:
            result.append(self.indent('else:\n'))
            for z in tree.orelse:
                self.level += 1
                result.append(self.visit(z))
                self.level -= 1

        return ''.join(result)
    #@+node:ekr.20111117031039.10211: *4* f.Import & helper
    def do_Import(self,tree):

        names = []

        for fn,asname in self.get_import_names(tree):
            if asname:
                names.append('%s as %s' % (fn,asname))
            else:
                names.append(fn)

        return self.indent('import %s\n' % (
            ','.join(names)))
    #@+node:ekr.20111117031039.10212: *5* f.get_import_names
    def get_import_names (self,tree):

        '''Return a list of the the full file names in the import statement.'''

        result = []
        for ast2 in tree.names:

            if self.kind(ast2) == 'alias':
                data = ast2.name,ast2.asname
                result.append(data)
            else:
                g.trace('unsupported kind in Import.names list',self.kind(ast2))

        return result
    #@+node:ekr.20111117031039.10214: *4* f.ImportFrom
    def do_ImportFrom(self,tree):

        names = []

        for fn,asname in self.get_import_names(tree):
            if asname:
                names.append('%s as %s' % (fn,asname))
            else:
                names.append(fn)

        return self.indent('from %s import %s\n' % (
            tree.module,
            ','.join(names)))
    #@+node:ekr.20111117031039.10215: *4* f.Lambda & helper
    def do_Lambda (self,tree):

        return self.indent('lambda %s: %s\n' % (
            self.visit(tree.args),
            self.visit(tree.body)))
    #@+node:ekr.20111117031039.10972: *4* f.Pass
    def do_Pass(self,tree):

        return self.indent('pass\n')
    #@+node:ekr.20120614011356.10081: *4* f.Print
    # Python 2.x only
    def do_Print(self,tree):

        vals = []

        for z in tree.values:
           vals.append(self.visit(z))

        if hasattr(tree,'dest') and tree.dest:
            vals.append('dest=%s' % self.visit(tree.dest))

        if hasattr(tree,'nl') and tree.nl:
            vals.append('nl=%s' % self.visit(tree.nl))

        return self.indent('print(%s)\n' % (
            ','.join(vals)))
    #@+node:ekr.20120614011356.10090: *4* f.Raise
    def do_Raise(self,tree):

        args = []
        for attr in ('type','inst','tback'):
            if hasattr(tree,attr) and getattr(tree,attr) is not None:
                args.append(self.visit(getattr(tree,attr)))

        if args:
            return self.indent('raise %s\n' % (
                ','.join(args)))
        else:
            return self.indent('raise\n')
    #@+node:ekr.20120614011356.10087: *4* f.Return
    def do_Return(self,tree):

        if tree.value:
            return self.indent('return %s\n' % (
                self.visit(tree.value)))
        else:
            return self.indent('return\n')
    #@+node:ekr.20120614011356.10078: *4* f.While
    def do_While (self,tree):

        result = []

        result.append(self.indent('while %s:\n' % (
            self.visit(tree.test))))

        for z in tree.body:
            self.level += 1
            result.append(self.visit(z))
            self.level -= 1

        if tree.orelse:
            result.append('else:\n')
            for z in tree.orelse:
                self.level += 1
                result.append(self.visit(z))
                self.level -= 1

        return ''.join(result)
    #@+node:ekr.20111117031039.10217: *4* f.With (To do)
    def do_With (self,tree):

        result = []
        result.append(self.indent('with '))

        if hasattr(tree,'context_expression'):
            result.append(self.visit(tree.context_expresssion))

        vars_list = []
        if hasattr(tree,'optional_vars'):
            try:
                for z in tree.optional_vars:
                    vars_list.append(self.visit(z))
            except TypeError: # Not iterable.
                vars_list.append(self.visit(tree.optional_vars))

        result.append(','.join(vars_list))
        result.append(':\n')

        for z in tree.body:
            self.level += 1
            result.append(self.visit(z))
            self.level -= 1

        result.append('\n')
        return ''.join(result)
    #@+node:ekr.20120614011356.10086: *4* f.Yield
    def do_Yield(self,tree):

        if hasattr(tree,'value') and tree.value:
            return self.indent('yield %s\n' % (
                self.visit(tree.value)))
        else:
            return self.indent('yield\n')

    #@-others
#@+node:ekr.20120623165430.10175: ** class CallPrinter (AstFormatter)
class CallPrinter (AstFormatter):

    def __init__ (self,fn):

        self.d = {}
            # Keys are def names; values are lists of calls.

        AstFormatter.__init__ (self,fn=fn)
            # Init the base class.

    #@+others
    #@+node:ekr.20120623165430.10411: *3* Call
    def do_Call(self,tree):

        func = self.visit(tree.func)

        if func.find('.') > -1 and func.find("'") == -1 and func.find('"') == -1:
            aList = func.split('.')
            key = aList[-1]
        else:
            key = func

        args = [self.visit(z) for z in tree.args]

        for z in tree.keywords:
            args.append(self.visit(z))

        if hasattr(tree,'starargs') and tree.starargs:
            args.append('*%s' % (self.visit(tree.starargs)))

        if hasattr(tree,'kwargs') and tree.kwargs:
            args.append('**%s' % (self.visit(tree.kwargs)))

        s = '%s(%s)' % (func,','.join(args))
        s = s.replace('\n','') # Shouldn't be necessary.

        aList = self.d.get(key,[])
        if s not in aList:
            aList.append(s)
            self.d[key] = aList

        return s
    #@+node:ekr.20120623165430.10755: *3* Constants & Name
    # Return generic markers allow better pattern matches.

    def do_bool(self,tree): # Python 2.x only.
        return 'Bool' 

    def do_Bytes(self,tree): # Python 3.x only.
        return 'Bytes' # return str(tree.s)

    def do_int (self,s):
        return 'Int' # return s

    def do_Name(self,tree):
        return 'Bool' if tree.id in ('True','False') else tree.id

    def do_Num(self,tree):
        return 'Num' # return repr(tree.n)

    def do_str (self,s):
        return s # Not repr(s)

    def do_Str (self,tree):
        return 'Str' # return repr(tree.s)
    #@+node:ekr.20120623165430.10179: *3* showCalls
    def showCalls(self,p,d=None):

        verbose = False

        d = d or self.d
        result = []
        for key in sorted(list(d.keys())):
            aList = d.get(key)
            if verbose or len(aList) > 1:
                result.append(key)
                for z in sorted(aList):
                    result.append('  %s' % (z))

        p.b = '\n'.join(result)
    #@-others
#@+node:ekr.20120622075651.10002: ** class ChainPrinter (AstFormatter)
class ChainPrinter (AstFormatter):

    def __init__ (self,fn):

        self.d = {}
        self.top_attribute = True

        AstFormatter.__init__ (self,fn=fn)
            # Init the base class.

    #@+others
    #@+node:ekr.20120622075651.10005: *3* Attribute
    # Attribute(expr value, identifier attr, expr_context ctx)

    def do_Attribute(self,tree):

        top = self.top_attribute
        try:
            self.top_attribute = False
            s = '%s.%s' % (
                self.visit(tree.value),
                self.visit(tree.attr))
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
    #@+node:ekr.20120623165430.11467: *3* Constants & Name
    # Return generic markers allow better pattern matches.

    def do_bool(self,tree): # Python 2.x only.
        return 'Bool' 

    def do_Bytes(self,tree): # Python 3.x only.
        return 'Bytes' # return str(tree.s)

    def do_int (self,s):
        return 'Int' # return s

    def do_Name(self,tree):
        return 'Bool' if tree.id in ('True','False') else tree.id

    def do_Num(self,tree):
        return 'Num' # return repr(tree.n)

    def do_str (self,s):
        return s # Not repr(s)

    def do_Str (self,tree):
        return 'Str' # return repr(tree.s)
    #@+node:ekr.20120622075651.10006: *3* showChains
    def showChains(self,p):

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

        p.b = '\n'.join(result)
        return n1,n2

    #@-others
#@+node:ekr.20120622075651.10007: ** class ReturnPrinter (AstFormatter)
class ReturnPrinter (AstFormatter):

    def __init__ (self,fn):

        self.d = {}
            # Keys are def names.
            # values are lists of lists of return statements.

        self.ret_stack = []

        AstFormatter.__init__ (self,fn=fn)
            # Init the base class.

    #@+others
    #@+node:ekr.20120623165430.11427: *3* Constants & Name
    # Return generic markers allow better pattern matches.

    def do_bool(self,tree): # Python 2.x only.
        return 'Bool' 

    def do_Bytes(self,tree): # Python 3.x only.
        return 'Bytes' # return str(tree.s)

    def do_int (self,s):
        return 'Int' # return s

    def do_Name(self,tree):
        return 'Bool' if tree.id in ('True','False') else tree.id

    def do_Num(self,tree):
        return 'Num' # return repr(tree.n)

    def do_str (self,s):
        return s # Not repr(s)

    def do_Str (self,tree):
        return 'Str' # return repr(tree.s)
    #@+node:ekr.20120623101052.10076: *3* FunctionDef
    # FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list)

    def do_FunctionDef (self,tree):

        name = self.visit(tree.name)
        self.ret_stack.append([])

        for z in tree.body:
            self.level += 1
            self.visit(z)
            self.level -= 1

        aList = self.d.get(name,[])
        aList.append(self.ret_stack.pop())
        self.d[name] = aList
        # g.trace(name,aList)
        return ''

        # The following isn't needed, but doesn't hurt.
        # result = []

        # if tree.decorator_list:
            # for z in tree.decorator_list:
                # result.append('@%s\n' % self.visit(z))

        # name = self.visit(tree.name)
        # args = self.visit(tree.args) if tree.args else ''

        # result.append(self.indent('def %s(%s):\n' % (name,args)))

        # for z in tree.body:
            # self.level += 1
            # result.append(self.visit(z))
            # self.level -= 1

        # return ''.join(result)
    #@+node:ekr.20120623101052.10078: *3* Return
    def do_Return(self,tree):

        aList = self.ret_stack.pop()

        val = self.visit(tree.value) if tree.value else None

        if val in ('True','False'):
            val = 'Bool'

        if val != None and val not in aList:
            aList.append(val)

        self.ret_stack.append(aList)

        return ''

        # The following isn't needed, but doesn't hurt.
        # if tree.value:
            # return self.indent('return %s\n' % (
                # self.visit(tree.value)))
        # else:
            # return self.indent('return\n')
    #@+node:ekr.20120623101052.10074: *3* showReturns
    def showReturns(self,verbose,d=None):

        result = []
        d = d or self.d

        def put(s):
            result.append(s)

        def put_list(aList):
            if aList:
                for ret in sorted(list(set(aList))):
                    put('  %s' % ret)
            else:
                put('  None (implicit)')

        for key in sorted(list(d.keys())):
            aList = d.get(key)
            n = len(aList)
            if n == 0:
                pass
            elif n == 1:
                aList2 = aList[0]
                n2 = len([z for z in aList2 if z not in (None,'None')])
                if (verbose and n2 > 0) or (not verbose and n2 > 1):
                    put('%s %s' % (key,n))
                    # put('  one list')
                    put_list(aList2)
            else:
                equal = not any([z != aList[0] for z in aList])
                if equal:
                    aList2 = aList[0]
                    n2 = len([z for z in aList2 if z not in (None,'None')])
                    if (verbose and n2 > 0) or (not verbose and n2 > 1):
                        put('%s %s' % (key,n))
                        put('  all lists equal')
                        put_list(aList2)
                else:
                    put('%s %s' % (key,n))
                    put('  lists unequal')
                    i = 0
                    for aList2 in aList:
                        put_list(aList2)
                        i += 1
                        if i < len(aList):
                            put('  %s' % ('-' * 10))

        return '\n'.join(result)
    #@-others
#@+node:ekr.20111116103733.10338: ** class Chain
class Chain(object):

    '''A class representing an identifier chain a.b.c.d.

    "a" is the **base** of the chain.
    "d" is the **target** of the chain.

    The representation of the chain itelf is a string.
    This representtion changes as the chain gets resolved.

    Chains also contain a list of ast nodes representing
    identifiers to be patched when the chain is fully resolved.

    See Pass1.do_Attribute for the kinds of nodes that
    may be patched.
    '''

    #@+others
    #@+node:ekr.20111116103733.10339: *3*  ctor, repr (Chain)
    def __init__ (self,tree,e,s):

        self.e = e # The symbol table entry for the base of the chain.
        self.s = s # A string in a.b.c.d format, or ''
        self.tree = tree

    def __repr__ (self):

        return 'Chain(%s)' % self.s

    __str__ = __repr__

    #@+node:ekr.20111116103733.10340: *3*  hash, eq and ne
    if 0: # These methods allow Chain's to be members of sets.

        def __eq__ (self,other):

            return self.s == other.s

        def __ne__ (self,other):

            return self.s != other.s

        # Valid and safe, but hurts performance:
        # sets of Chains will perform much like lists of Chains.
        # This will not likely matter much because
        # sets of chains will usually have few members.
        def __hash__ (self):

            return 0
    #@+node:ekr.20111116103733.10341: *3* chain.base
    def base (self):

        '''Return the base of this Chain.'''

        # Call the global function to ensure that
        # Chain.base() matches the code in SymbolTable.add_chain().

        return g_chain_base(self.s)
    #@+node:ekr.20111116103733.10342: *3* chain.is_empty
    def is_empty (self):

        '''Return True if this chain is empty.'''

        return self.s.find('.') == -1
    #@+node:ekr.20111116103733.10343: *3* chain.defines_ivar & get_ivar
    def defines_ivar (self):

        parts = self.s.split('.')
        return len(parts) == 2 and parts[0] == 'self'

    def get_ivar (self):

        parts = self.s.split('.')
        if len(parts) == 2 and parts[0] == 'self':
            return parts[1]
        else:
            return None
    #@+node:ekr.20111116103733.10344: *3* chain.short_description
    def short_description (self):

        return 'chain: %s' % self.s
    #@-others
#@+node:ekr.20111116103733.10345: ** class InspectTraverser (AstTraverser)
class InspectTraverser (AstTraverser):

    '''A class to create inpect semantic data structures.'''

    #@+others
    #@+node:ekr.20111116103733.10346: *3*  it.ctor
    def __init__(self,fn,sd):

        # Init the base class.
        AstTraverser.__init__(self,fn)
            # Creates dispatch dict.
            # Calls init_tracing.

        # Ivars...
        self.fn = fn
        self.sd = sd
        self.trace_flag = False

        # Create an instance of AstFormatter.
        if 0: # A test of the overhead of string generation.
            self.formatter = g.nullObject()
        else:
            self.formatter = AstFormatter(fn)

        self.formatter.trace_flag = self.trace_flag
    #@+node:ekr.20111116103733.10354: *3* it.Contexts
    #@+node:ekr.20111116103733.10355: *4* ClassDef
    # ClassDef(identifier name, expr* bases, stmt* body, expr* decorator_list)

    def do_ClassDef (self,tree,tag=''):

        '''Create a context for a class, and
        define the class name in the present context.'''

        # Create the new context.
        old_cx = self.get_context()
        new_cx = ClassContext(tree,old_cx,self.sd)

        # Define the name in the old context.
        e = old_cx.st.add_name(tree.name,tree)
        e.set_defined()
        old_cx.classes_list.append(new_cx)

        self.push_context(new_cx)

        self.visit(tree.name)

        for z in tree.body:
            self.visit(z)

        self.pop_context()

        self.sd.n_classes += 1
    #@+node:ekr.20111116103733.10356: *4* FunctionDef
    # FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list)

    def do_FunctionDef (self,tree,tag=''):

        # g.trace(self.dump(tree))

        # Switch to the new context.
        old_cx = self.get_context()
        new_cx = DefContext(tree,old_cx,self.sd)

        # Define the function/method name in the old context.
        e = old_cx.st.add_name(tree.name,tree)
        e.set_defined()
        old_cx.defs_list.append(new_cx)

        self.push_context(new_cx)

        self.visit(tree.name)

        # Define the function arguments before visiting the body.
        # These arguments, including 'self', are known in the body.
        self.def_args_helper(new_cx,tree.args)

        # Visit the body.
        for z in tree.body:
            self.visit(z)

        self.pop_context()

        self.sd.n_defs += 1
    #@+node:ekr.20111116103733.10357: *5* def_args_helper
    # arguments = (expr* args, identifier? vararg, identifier? kwarg, expr* defaults)
    # -- keyword arguments supplied to call
    # keyword = (identifier arg, expr value)

    def def_args_helper (self,cx,tree):

        assert self.kind(tree) == 'arguments'

        # Handle positional args.
        # do_Name actually adds the args.
        for z in tree.args:
            self.visit(z)

        for z in tree.defaults:
            self.visit(z)

        for tag in ('vararg','kwarg',):
            name = hasattr(tree,tag) and getattr(tree,tag)
            if name:
                e = cx.st.add_name(name,tree)
                cx.param_names.add(name)
                self.sd.n_param_names += 1
    #@+node:ekr.20111116103733.10358: *4* Module
    def do_Module (self,tree,tag=''):

        sd = self.sd

        # Get the module context from the global dict if possible.
        new_cx = sd.modules_dict.get(self.fn)

        if not new_cx:
            new_cx = ModuleContext(tree,self.fn,sd)
            sd.modules_dict[self.fn] = new_cx

        self.push_context(new_cx)

        try:
            for z in tree.body:
                self.visit(z)
        finally:
            self.pop_context()
    #@+node:ekr.20111125131712.10256: *3* it.Operands
    # Use the AstFormatter methods for all operands except do_Attribute and do_Name.

    # Note:  self.formatter is a delegate object: it would be bad style
    # to make InspectTraverser a subclass of AstFormatter.

    def format_tree(self,tree,tag=''):
        val = self.formatter.visit(tree)
        # if self.trace_flag: g.trace(tag,val)
        return val

    # do_Attribute
    do_bool         = format_tree
    do_Bytes        = format_tree
    do_Call         = format_tree
    do_comprehension= format_tree
    do_Dict         = format_tree
    do_Ellipsis     = format_tree
    do_ExtSlice     = format_tree
    do_Index        = format_tree
    do_int          = format_tree
    do_Keyword      = format_tree
    do_List         = format_tree
    do_ListComp     = format_tree
    # do_Name
    do_Num          = format_tree
    do_Slice        = format_tree
    do_str          = format_tree
    do_Str          = format_tree
    do_Subscript    = format_tree
    do_Tuple        = format_tree
    #@+node:ekr.20111125131712.10277: *4* it.Attribute
    def do_Attribute(self,tree,tag=''):

        # assert self.kind(tree) == 'Attribute'
        cx = self.get_context()    
        name = tree.attr

        # Use the *formatter* to traverse tree.value.
        expr = self.formatter.visit(tree.value)
        s = '%s.%s' % (expr,name)

        if self.trace_flag: g.trace(s)

        chain = cx.st.add_chain(tree,s)

        self.sd.n_attributes += 1

        #### Huh?
        #### self.formatter.append(s)
            # For recursive calls.
        return s


    #@+node:ekr.20111125131712.10278: *4* it.Name
    def do_Name(self,tree,tag=''):

        name = tree.id

        if isPython3:
            if name in self.sd.module_names:
                return
        else:
            if name in dir(__builtin__) or name in self.sd.module_names:
                return

        if self.trace_flag: g.trace(name)

        cx = self.get_context()
        ctx = self.kind(tree.ctx)
        sd = self.sd

        # Important: symbol tables represent only static context.
        # The resolution algorithm computes what names "really" mean.
        e = cx.st.add_name(name,tree)

        if ctx == 'Load': # Most common.
            cx.load_names.add(name)
            sd.n_load_names += 1
        elif ctx == 'Store': # Next most common.
            cx.store_names.add(name)
            if name in cx.load_names:
                e.load_before_store_flag = True
            sd.n_store_names += 1
        elif ctx == 'Param':
            cx.param_names.add(name)
            sd.n_param_names += 1
        else:
            assert ctx == 'Del',ctx
            cx.del_names.add(name)
            sd.n_del_names += 1
    #@+node:ekr.20120613104401.10221: *4* it.ListComp
    def do_ListComp(self,tree,tag=''):

        sd = self.sd

        self.visit(tree.elt)
        for z in tree.generators:
            self.visit(z)

        sd.n_list_comps += 1
    #@+node:ekr.20111116103733.10368: *3* it.Statements
    #@+node:ekr.20111116103733.10369: *4* it.Assign
    def do_Assign(self,tree,tag=''):

        sd = self.sd

        cx = self.get_context()
        cx.statements_list.append(StatementContext(tree,cx,sd,'assn'))

        self.visit(tree.value)    
        for z in tree.targets:    
            self.visit(z)

        sd.n_assignments += 1
    #@+node:ekr.20111116103733.10370: *4* it.AugAssign
    def do_AugAssign(self,tree,tag=''):

        sd = self.sd

        cx = self.get_context()
        cx.statements_list.append(StatementContext(tree,cx,sd,'aug-assn'))

        self.visit(tree.op)
        self.visit(tree.value) # The rhs.
        self.visit(tree.target) # The lhs.

        sd.n_assignments += 1
    #@+node:ekr.20111116103733.10365: *4* it.Call
    def do_Call(self,tree,tag=''):

        sd = self.sd
        cx = self.get_context()

        cx.calls_list.append(StatementContext(tree,cx,sd,'call'))

        sd.n_calls += 1

        self.visit(tree.func)

        for z in tree.args:
            self.visit(z)

        for z in tree.keywords:
            self.visit(z)

        if hasattr(tree,'starargs') and tree.starargs:
            self.visit(tree.starargs)

        if hasattr(tree,'kwargs') and tree.kwargs:
            self.visit(tree.kwargs)
    #@+node:ekr.20111116103733.10371: *4* it.For
    def do_For (self,tree,tag=''):

        # Define a namespace for the 'for' target.
        old_cx = self.get_context()
        new_cx = ForContext(tree,old_cx,self.sd)
        old_cx.statements_list.append(new_cx)
        old_cx.temp_contexts.append(new_cx)

        self.push_context(new_cx)

        self.visit(tree.target)

        self.visit(tree.iter)

        for z in tree.body:
            self.visit(z)

        for z in tree.orelse:
            self.visit(z)

        self.pop_context()

        self.sd.n_fors += 1
    #@+node:ekr.20111116103733.10372: *4* it.Global
    def do_Global(self,tree,tag=''):

        '''Enter the names in a 'global' statement into the *module* symbol table.'''

        sd = self.sd
        cx = self.get_context()
        cx.statements_list.append(StatementContext(tree,cx,sd,'global'))

        for name in tree.names:

            # Add the name to the global_names set in *this* context.
            cx.global_names.add(name)

            # Create a symbol table entry for the name in the *module* context.
            cx.module_context.st.add_name(name,tree)

            sd.n_globals += 1
    #@+node:ekr.20111116103733.10373: *4* it.Import & helpers
    def do_Import(self,tree,tag=''):

        '''Add the imported file to the sd.files_list if needed
        and create a context for the file.'''

        trace = False
        sd = self.sd
        cx = self.get_context()
        cx.statements_list.append(StatementContext(tree,cx,sd,'import'))
        aList = self.get_import_names(tree)

        for fn,asname in aList:
            fn2 = self.resolve_import_name(fn)
            if fn2:
                if not fn2 in sd.files_list:
                    sd.files_list.append(fn2)
                mname = sd.module_name(fn2)
                if mname not in sd.module_names:
                    sd.module_names.append(mname)
                if trace: g.trace('%s as %s' % (mname,asname))
                e = cx.st.add_name(asname or mname,tree)
                e.set_defined()
                sd.n_imports += 1
            else:
                if trace: g.trace('can not resolve',fn)
    #@+node:ekr.20111116103733.10374: *5* LLT.get_import_names
    def get_import_names (self,tree):

        '''Return a list of the the full file names in the import statement.'''

        result = []

        for ast2 in tree.names:

            if self.kind(ast2) == 'alias':
                data = ast2.name,ast2.asname
                result.append(data)
            else:
                g.trace('unsupported kind in Import.names list',self.kind(ast2))

        # g.trace(result)
        return result
    #@+node:ekr.20111116103733.10375: *5* LLT.resolve_import_name
    def resolve_import_name (self,spec):

        '''Return the full path name corresponding to the import spec.'''

        trace = False

        ### This may not work for leading dots.
        aList,path,paths = spec.split('.'),None,None

        for name in aList:
            try:
                f,path,description = imp.find_module(name,paths)
                # g.trace('name',name,'path',repr(path),'f',f)
                paths = [path]
                if f: f.close()
            except ImportError:
                # Important: imports can fail due to Python version.
                # Thus, such errors are not necessarily searious.
                if trace: g.trace('failed',name,'paths',paths,'cx',self.get_context())
                path = None
                break

        if path and path.endswith('.pyd'):
            return ''
        else:
            return path
    #@+node:ekr.20111116103733.10376: *4* it.ImportFrom
    def do_ImportFrom(self,tree,tag=''):

        '''Add the imported file to the sd.files_list if needed
        and add the imported symbols to the *present* context.'''

        trace = False ; dump = False
        if trace and dump:
            self.dump(tree)

        sd = self.sd
        cx = self.get_context()
        cx.statements_list.append(StatementContext(tree,cx,sd,'import from'))

        m = self.resolve_import_name(tree.module)
        if m and m not in sd.files_list:
            if trace: g.trace('adding module',m)
            sd.files_list.append(m)

        aList = self.get_import_names(tree)
        for fn,asname in aList:
            fn2 = asname or fn
            if trace: g.trace(fn2)
            e = cx.st.add_name(fn2,tree)
            e.set_defined()
            mname = sd.module_name(fn2)
            if mname not in sd.module_names:
                sd.module_names.append(mname)
            sd.n_imports += 1
    #@+node:ekr.20111116103733.10377: *4* it.Lambda & helper
    def do_Lambda (self,tree,tag=''):

        # Define a namespace for the 'lambda' variables.
        old_cx = self.get_context()
        new_cx = LambdaContext(tree,old_cx,self.sd)
        old_cx.statements_list.append(new_cx)
        old_cx.temp_contexts.append(new_cx)

        self.push_context(new_cx)

        # Enter the target names in the 'lambda' context.
        self.def_lambda_args_helper(new_cx,tree.args)

        # Enter all other definitions in the defining_context.
        self.visit(tree.body)

        self.pop_context()

        self.sd.n_lambdas += 1

    #@+node:ekr.20111116103733.10378: *5* def_lambda_args_helper
    # arguments = (expr* args, identifier? vararg, identifier? kwarg, expr* defaults)
    # -- keyword arguments supplied to call
    # keyword = (identifier arg, expr value)

    def def_lambda_args_helper (self,cx,tree):

        trace = False
        assert self.kind(tree) == 'arguments'

        # Handle positional args.
        # do_Name actually adds the args.
        for z in tree.args:
            self.visit(z)

        for z in tree.defaults:
            self.visit(z)

        for tag in ('vararg','kwarg',):
            name = hasattr(tree,tag) and getattr(tree,tag)
            if name:
                if trace: g.trace(tag,name)
                e = cx.st.add_name(name,tree)
                cx.param_names.add(name)
    #@+node:ekr.20111116103733.10379: *4* it.With
    def do_With (self,tree,tag=''):

        # Define a namespace for the 'with' statement.
        old_cx = self.get_context()
        new_cx = WithContext(tree,old_cx,self.sd)
        old_cx.statements_list.append(new_cx)
        old_cx.temp_contexts.append(new_cx)

        self.push_context(new_cx)

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

        self.pop_context()

        self.sd.n_withs += 1
    #@+node:ekr.20111116103733.10352: *3* it.traverse
    def traverse (self,s):

        '''Perform all checks on the source in s.'''

        sd = self.sd

        t1 = time.time()

        tree = ast.parse(s,filename=self.fn,mode='exec')

        t2 = time.time()
        sd.parse_time += t2-t1

        self.visit(tree,tag='top')

        t3 = time.time()
        sd.pass1_time += t3-t2
    #@-others
#@+node:ekr.20111116103733.10312: ** class LeoCoreFiles
class LeoCoreFiles(object):

    '''A class representing Leo's core files, including qtGui.py'''

    def __init__ (self):

        self.files = self.create_core_list()
            # The list of files in Leo's core.

    #@+others
    #@+node:ekr.20111116103733.10313: *3* create_core_list
    def create_core_list(self):

        skipList = (
            'format-code.py',
            '__init__.py',
        )

        files = glob.glob(g.os_path_finalize_join(
            g.app.loadDir,'*.py'))
        aList = []
        for fn in files:
            for z in skipList:
                if fn.endswith(z):
                    # print('skipping %s' % fn)
                    break
            else: aList.append(fn)

        aList.append(g.os_path_finalize_join(
            g.app.loadDir,'..','plugins','qtGui.py'))

        return aList
    #@+node:ekr.20111116103733.10314: *3* get_source
    def get_source (self,fn):

        if not g.os_path_exists(fn):
            fn = g.os_path_finalize_join(g.app.loadDir,fn)
        if not g.os_path_exists(fn):
            fn = g.os_path_finalize_join(g.app.loadDir,'..','plugins',fn)

        try:
            f = open(fn,'r')
            s = f.read()
            f.close()
            return s
        except IOError:
            return ''
    #@-others
#@+node:ekr.20120609070048.11214: ** class Program
class Program:

    '''A class representing all the files in the program.

    May be significant later when industrial-strength caching is in effect.'''

    def __init__ (self,files):

        self.files = files
#@+node:ekr.20111116103733.10380: ** class SemanticData
class SemanticData(object):

    '''A class containing all global semantic data.'''

    #@+others
    #@+node:ekr.20111116103733.10381: *3*  sd.ctor
    def __init__ (self,controller=None):

        self.controller = controller
        self.dumper = AstDumper()
        self.formatter = AstFormatter()

        # Files...
        self.completed_files = [] # Files handled by do_files.
        self.failed_files = [] # Files that could not be opened.
        self.files_list = [] # Files given by user or by import statements.
        self.module_names = [] # Module names corresponding to file names.

        # Contexts.
        self.context_list = {}
            # Keys are fully qualified context names; values are contexts.
        self.modules_dict = {}
            # Keys are full file names; values are ModuleContext's.

        # The resolution algorithm.
        self.known_types = []

        # Statistics...
        self.n_chains = 0
        self.n_contexts = 0
        self.n_modules = 0
        self.n_resolved_contexts = 0
        self.n_errors = 0

        # Names...
        self.n_attributes = 0
        self.n_ivars = 0
        self.n_names = 0        # Number of symbol table entries.
        self.n_del_names = 0
        self.n_load_names = 0
        self.n_param_names = 0
        self.n_store_names = 0

        # Statements...
        self.n_assignments = 0
        self.n_calls = 0
        self.n_classes = 0
        self.n_defs = 0
        self.n_fors = 0
        self.n_globals = 0
        self.n_imports = 0
        self.n_lambdas = 0
        self.n_list_comps = 0
        self.n_withs = 0

        # Times...
        self.parse_time = 0.0
        self.pass1_time = 0.0
        self.pass2_time = 0.0
        self.total_time = 0.0
    #@+node:ekr.20111116103733.10382: *3* sd.all_contexts (generator) (not used)
    if 0: # This works, but is too clever by half.

        def all_contexts (self,aList=None):

            '''An iterator returning all contexts.'''

            if not aList:
                aList = list(self.modules_dict.values())

            for cx in aList:
                yield cx
                if cx.classes_list:
                    for z in self.all_contexts(cx.classes_list):
                        yield z
                if cx.defs_list:
                    for z in self.all_contexts(cx.defs_list):
                        yield z
                if cx.temp_contexts:
                    for z in self.all_contexts(cx.temp_contexts):
                        yield z
    #@+node:ekr.20111116103733.10383: *3* sd.dump
    def dump (self):

        sd = self
        d = sd.modules_dict

        print('\nDump of modules...')
        for fn in sorted(d.keys()):
            m = d.get(fn)
            m.dump()
    #@+node:ekr.20111116103733.10384: *3* sd.dump_ast
    def dump_ast (self,tree,brief=False):

        '''Return the string, but don't write it.'''

        dumper = self.dumper
        dumper.brief = brief
        s = dumper._dumpTreeAsString(tree)
        return s
    #@+node:ekr.20111116103733.10385: *3* sd.module_name
    def module_name (self,fn):

        fn = g.shortFileName(fn)
        if fn.endswith('.py'):
            fn = fn[:-3]
        return fn
    #@+node:ekr.20111116103733.10386: *3* sd.print_failed_files
    def print_failed_files (self):

        sd = self

        if sd.failed_files:
            # g.trace('%s import failed' % (len(sd.failed_files)))
            sd.failed_files.sort()
            print(sd.failed_files)
    #@+node:ekr.20111116103733.10387: *3* sd.print_stats
    def print_stats (self):

        sd = self
        table = (
            '*', 'errors',

            '*Contexts',
            'classes','contexts','defs','modules',

            '*Statements',
            'assignments','calls','fors','globals','imports',
            'lambdas','list_comps','withs',

            '*Names',
            'attributes','del_names','load_names','names',
            'param_names','store_names',

            # 'ivars',
            # 'resolved_contexts',
        )

        max_n = 5
        for s in table:
            max_n = max(max_n,len(s))

        print('\nStatistics...\n')
        for s in table:
            var = 'n_%s' % s
            pad = ' ' * (max_n - len(s))
            if s.startswith('*'):
                if s[1:].strip():
                    print('\n%s\n' % s[1:])
                else:
                    pass # print('')
            else:
                pad = ' ' * (max_n - len(s))
                print('%s%s: %s' % (pad,s,getattr(sd,var)))
        print('')

    #@+node:ekr.20111116103733.10508: *3* sd.print_times
    def print_times (self):

        sd = self

        times = (
            'parse_time',
            'pass1_time',
            # 'pass2_time', # the resolve_names pass is no longer used.
            'total_time',
        )

        max_n = 5
        for s in times:
            max_n = max(max_n,len(s))

        print('\nScan times...\n')
        for s in times:
            pad = ' ' * (max_n - len(s))
            print('%s%s: %2.2f' % (pad,s,getattr(sd,s)))
        print('')
    #@+node:ekr.20111116103733.10388: *3* sd.resolve_types
    def resolve_types (self):

        '''The new resolution algorithm.

        Remove symbols from all Dependency objects containing them,
        thereby possibly createing more known symbols.
        '''

        sd = self

        g.trace(len(sd.known_types))

        # Important: len(sd.known_type) may change in this loop.
        while sd.known_types:
            e = sd.known_types.pop()
            e.become_known()
    #@-others

#@+node:ekr.20111116103733.10389: ** class SymbolTable
class SymbolTable(object):

    '''A base class for all symbol table info.'''

    #@+others
    #@+node:ekr.20111116103733.10390: *3*  st.ctor and repr
    def __init__ (self,context):

        self.context = context
        self.d = {} # Keys are names, values are symbol table entries.
        self.max_name_length = 1 # Minimum field width for dumps.

    def __repr__ (self):
        return 'SymbolTable for %s...\n' % self.context.description()

    __str__ = __repr__
    #@+node:ekr.20111116103733.10391: *3* st.add_chain
    def add_chain (self,tree,s):

        '''Add the chain described by (tree,s) to the symbol table
        for the base of s, a plain string.

        Return the perhaps-newly-created Chain object for (tree,s).'''

        st = self
        # if s.find('.') == -1: g.trace(s,g.callers())
        base = g_chain_base(s)
        e = st.add_name(base,tree)
        chain = e.add_chain(base,tree,s)
        return chain

    #@+node:ekr.20111116103733.10392: *3* st.add_name
    def add_name (self,name,tree):

        '''Add name to the symbol table.  Return the symbol table entry.'''

        st = self
        e = st.d.get(name)
        if not e:
            e = SymbolTableEntry(name,st,tree)
            st.d [name] = e
            st.context.sd.n_names += 1
            # if name == 'self' and st.context.kind == 'class':
                # g.trace('st: %s name: %s' % (self,name),g.callers())

        return e
    #@+node:ekr.20111116103733.10393: *3* st.dump
    def dump (self,level=0):

        cx = self.context

        print('')
        print(self)

        # Print the table entries.
        if 1:
            keys = list(self.d.keys())
            keys.sort()
            for key in keys:
                print(self.d.get(key))

        # Print non-empty ctx lists.
        if 0:
            table = (
                (cx.del_names,'Del'),
                (cx.load_names,'Load'),
                (cx.param_names,'Param'),
                (cx.store_names,'Store'),
                (cx.global_names,'Globals'),
                (cx.all_global_names,'all_glob'),
            )
            for aSet,kind in table:
                if aSet:
                    print('%8s: %s' % (kind,list(aSet)))

    #@+node:ekr.20111116103733.10394: *3* st.get_name
    def get_name (self,name):

        '''Return the symbol table entry for name.'''

        return self.d.get(name)
    #@-others
#@+node:ekr.20111116103733.10395: ** class SymbolTableEntry
class SymbolTableEntry(object):

    #@+others
    #@+node:ekr.20111116103733.10396: *3*  e.ctor
    def __init__ (self,name,st,tree):

        self.chains = {} # Keys are bases, values dicts of Chains.
        self.defined = False
        self.load_before_store_flag = False
        self.name = name
        self.st = st
        self.tree = tree

        # Update the length field for dumps.
        st.max_name_length = max(
            st.max_name_length,
            name and len(name) or 0)
    #@+node:ekr.20111116103733.10397: *3* e.add_chain
    def add_chain (self,base,tree,s):

        '''
        If a Chain exists in e.chains[base], merge tree into its ast_list.

        Otherwise, create a new Chain object and add it to e.chains[base].

        This is the *only* place where chains are created.
        '''

        e = self
        d = e.chains.get(base,{})
        chain = d.get(s)
        if chain:
            pass
            # chain.ast_list.append(tree)
        else:
            d [s] = chain = Chain(tree,e,s)
            e.chains [base] = d
        return chain
    #@+node:ekr.20111116103733.10398: *3* e.repr and e.dump
    def __repr__ (self):

        if self.name:
            n = self.st.max_name_length - len(self.name)
            pad = ' '*n
            # unbound = g.choose(self.load_before_store_flag,': <unbound>','')
            unbound = ': <unbound>' if self.load_before_store_flag else ''
            if self.chains:
                return '%s%s defined: %5s%s: %s' % (
                    pad,self.name,self.defined,unbound,self.show_chains())
            else:
                return '%s%s defined: %5s%s' % (
                    pad,self.name,self.defined,unbound)
        else:
            return '<ste: no name!>'

    def dump(self):
        print(self)

    def show_chains(self):
        # self.chains is a dict of dicts.
        result = []
        keys = list(self.chains.keys())
        for key in keys:
            d = self.chains.get(key,{})
            for key2 in list(d.keys()):
                chain = d.get(key2)
                result.append(chain.s)
        result.sort()
        return ','.join(result)
    #@+node:ekr.20111116103733.10399: *3* e.is_defined & set_defined
    def is_defined (self):

        return self.defined

    def set_defined (self):

        self.defined = True
    #@+node:ekr.20111116103733.10400: *3* e.short_description
    def short_description (self):

        return 'ste: %s' % self.name
    #@-others
#@+node:ekr.20120612044943.10201: ** class TestPickleClass
class TestPickleClass:
    pass
#@+node:ekr.20111116103733.10401: ** Context classes
#@+node:ekr.20111116103733.10413: *3* class ClassContext
class ClassContext (Context):

    '''A class to hold semantic data about a class.'''

    def __init__(self,tree,parent_context,sd):

        Context.__init__(self,tree,parent_context,sd,'class')

    def __repr__ (self):

        return 'class(%s)' % (self.tree_ptr.name)

    def name (self):

        return self.tree_ptr.name

    __str__ = __repr__
#@+node:ekr.20111116103733.10414: *3* class ConprehensionContext
class ComprehensionContext (Context):

    '''A class to represent the range of a list comprehension.'''

    def __init__(self,tree,parent_context,sd):

        Context.__init__(self,tree,parent_context,sd,'comprehension')

    def __repr__ (self):

        return 'comprehension'

    def name (self):

        return 'list comprehension context'

    __str__ = __repr__
#@+node:ekr.20111116103733.10415: *3* class DefContext
class DefContext (Context):

    '''A class to hold semantic data about a function/method.'''

    def __init__(self,tree,parent_context,sd):

        Context.__init__(self,tree,parent_context,sd,'def')

    def __repr__ (self):

        return 'def(%s)' % (self.tree_ptr.name)

    def name (self,verbose=False):
        if verbose:
            kind = 'method' if self.class_context else 'function'
            return '%s %s' % (kind,self.tree_ptr.name)
        else:
            return self.tree_ptr.name

    __str__ = __repr__
#@+node:ekr.20111116103733.10416: *3* class ForContext
class ForContext (Context):

    '''A class to represent the range of a 'for' statement.'''

    def __init__(self,tree,parent_context,sd):

        Context.__init__(self,tree,parent_context,sd,'for')

    def __repr__ (self):
        kind = self.tree_kind(self.tree_ptr.target)
        if kind == 'Name':
            return 'for(%s)' % (self.tree_ptr.target.id)
        elif kind == 'Tuple':
            return 'for(%s)' % ','.join([z.id for z in self.tree_ptr.target.elts])
        else:
            return 'for(%s)' % (kind)

    def name (self):
        return '"for" statement context'

    __str__ = __repr__
#@+node:ekr.20111116103733.10417: *3* class LambdaContext
class LambdaContext (Context):

    '''A class to represent the range of a 'lambda' statement.'''

    def __init__(self,tree,parent_context,sd):

        Context.__init__(self,tree,parent_context,sd,'lambda')

    def __repr__ (self):

        return 'lambda context'

    def name (self):
        return 'lambda statement context'

    __str__ = __repr__
#@+node:ekr.20111116103733.10418: *3* class ModuleContext
class ModuleContext (Context):

    '''A class to hold semantic data about a module.'''

    def __init__(self,tree,fn,sd):

        parent_context = None
        self.fn = fn # Do this first, so repr works.
        Context.__init__(self,tree,parent_context,sd,'module')
        assert self.module_context == self
        sd.n_modules += 1

    def __repr__ (self):

        return 'module(%s)' % g.shortFileName(self.fn)

    def name (self):

        return g.shortFileName(self.fn)

    __str__ = __repr__
#@+node:ekr.20111116161118.10170: *3* class StatementContext
class StatementContext (Context):

    '''A class to hold semantic data about any statement.'''

    def __init__(self,tree,parent_context,sd,kind):

        Context.__init__(self,tree,parent_context,sd,kind)

    def __repr__ (self):
        return 'statement(%s)' % (self.context_kind)

    def name (self):
        return '"%s" statement context' % (self.context_kind)

    __str__ = __repr__
#@+node:ekr.20111116103733.10419: *3* class WithContext
class WithContext (Context):

    '''A class to represent the range of a 'with' statement.'''

    def __init__(self,tree,parent_context,sd):

        Context.__init__(self,tree,parent_context,sd,'with')

    def __repr__ (self):

        return 'with()'

    def name (self):
        return 'with statement context'

    __str__ = __repr__
#@-others
#@-leo

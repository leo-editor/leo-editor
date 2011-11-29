# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20111116103733.9817: * @file leoInspect.py
#@@first

'''A scriptable framework for creating queries of Leo's object code.'''

#@@language python
#@@tabwidth -4
#@@pagewidth 60

#@+at To do
# 
# - Allow "partial" matches in calls_to,assign_to.
#     - Use regex searches?
#     
# - Append *all* statements to statements list.
#     Including def, class, if, while, pass, with etc.
# 
#@@c

#@+<< imports >>
#@+node:ekr.20111116103733.10440: **  << imports >>
import leo.core.leoGlobals as g

# Used by ast-oriented code.
if not g.isPython3:
    import __builtin__
    
import ast
import glob
import imp
import os
import string
import sys
import time
import types

if g.isPython3:
    import io
    StringIO = io.StringIO
else:
    import cStringIO
    StringIO = cStringIO.StringIO
#@-<< imports >>
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
    #@+node:ekr.20111116103733.10280: *4* a.ctor
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
            a.arg: self.do_arg,
            a.arguments: self.do_arguments,
            a.comprehension: self.do_comprehension,
            # a.id: self.do_id,
            # a.keywords: self.do_Keywords,
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
            ### a.Exec: self.do_Exec,
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
            ### a.Print: self.do_Print,
            a.RShift: self.do_RShift,
            a.Raise: self.do_Raise,
            ### a.Repr: self.do_Repr,
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

        if not g.isPython3:
            d [bool] = self.do_bool
            d [a.Exec] = self.do_Exec
            d [a.Print] = self.do_Print
            d [a.Repr] = self.do_Repr
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
        
        g.trace('**** bad ast type',kind)
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

    #@+node:ekr.20111116103733.10290: *4* node_after_tree
    # The _parent must have been injected into all parent nodes for this to work.
    # This will be so, because of the way in which visit traverses the tree.

    def node_after_tree (self,tree):
        
        trace = True
        tree1 = tree # For tracing
        
        def children(tree):
            return [z for z in ast.iter_child_nodes(tree)]
            
        def parent(tree):
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
            info = self.info
            for z in (ast.Module,ast.ClassDef,ast.FunctionDef):
                if isinstance(tree1,z):
                    g.trace('node: %22s, parent: %22s, after: %22s' % (
                        info(tree1),info(parent(tree1)),info(result)))
                    break

        return result
    #@+node:ekr.20111116103733.10291: *4* string_dump
    def string_dump (self,tree):
        
        if not isinstance(tree,ast.AST):
            g.trace('not an AST node')
            return ''

        after = self.node_after_tree(tree)
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
        self.visit(tree.value,'expr-value')

    def do_Expression(self,tree,tag=''):
        self.trace(tree,tag)
        self.visit(tree.body,'expression-body')

    def do_GeneratorExp(self,tree,tag=''):
        self.trace(tree,tag)
        self.visit(tree.elt,'generator elt')
        for z in tree.generators:
            self.visit(z,'generator generator')
    #@+node:ekr.20111116103733.10293: *4* a.IfExp
    def do_IfExp (self,tree,tag=''):
        self.trace(tree,tag)
        self.visit(tree.test,'if-expr test')
        if tree.body:
            self.visit(tree.body,'if-expr body')
        if tree.orelse:
            self.visit(tree.orelse,'if-expr orelse')
    #@+node:ekr.20111116103733.10294: *4* a.Operands
    def do_Attribute(self,tree,tag=''):
        self.trace(tree,tag)
        self.visit(tree.value,'attribute value')
        self.visit(tree.attr,'attribute attr (identifier)')
        self.visit(tree.ctx,'attribute context')

    # Python 2.x only.
    def do_bool(self,tree,tag=''):
        pass

    def do_Call(self,tree,tag=''):
        self.trace(tree,tag)
        self.visit(tree.func,'call func')
        for z in tree.args:
            self.visit(z,'call args')
        for z in tree.keywords:
            self.visit(z,'call keyword args')
        if hasattr(tree,'starargs') and tree.starargs:
            if self.kind(tree.starargs) == 'Name':
                 self.visit(tree.starargs,'call *args')
            elif self.isiterable(tree.starargs):
                for z in tree.starargs:
                    self.visit(z,'call *args')
            else: g.trace('** unknown starargs kind',tree)
        if hasattr(tree,'kwargs') and tree.kwargs:
            if self.kind(tree.kwargs) == 'Name':
                 self.visit(tree.kwargs,'call *args')
            elif self.isiterable(tree.kwargs):
                for z in tree.kwargs:
                    self.visit(z,'call *args')
            else: g.trace('** unknown kwargs kind',tree)

    def do_comprehension(self,tree,tag=''):
        self.trace(tree,tag)
        self.visit(tree.target,'comprehension target (a Name)')
        self.visit(tree.iter,'comprehension iter (an Attribute)')
        for z in tree.ifs:
            self.visit(z,'comprehension if')

    def do_Dict(self,tree,tag=''):
        self.trace(tree,tag)
        for z in tree.keys:
            self.visit(z,'dict keys')
        for z in tree.values:
            self.visit(z,'dict values')

    def do_Ellipsis(self,tree,tag=''):
        self.trace(tree,tag)

    def do_ExtSlice (self,tree,tag=''):
        self.trace(tree,tag)
        for z in tree.dims:
            self.visit(z,'slice dimention')

    def do_Index (self,tree,tag=''):
        self.trace(tree,tag)
        self.visit(tree.value,'index value')

    def do_int (self,s,tag=''):
        self.trace(None,tag=tag,s=s,kind='int')

    def do_Keyword (self,tree,tag=''):
        self.trace(tree,tag)
        self.visit(tree.arg,'keyword arg')
        self.visit(tree.value,'keyword value')

    def do_List(self,tree,tag=''):
        self.trace(tree,tag)
        for z in tree.elts:
            self.visit(z,'list elts')
        self.visit(tree.ctx,'list context')

    def do_ListComp(self,tree,tag=''):
        self.trace(tree,tag)
        self.visit(tree.elt,'list comp elt')
        for z in tree.generators:
            self.visit(z,'list comp generator')

    def do_Name(self,tree,tag=''):
        self.trace(tree,tag)
        # tree.id is a string.
        self.visit(tree.id,'name id')
        self.visit(tree.ctx,'name context')

    def do_Num(self,tree,tag=''):
        tag = '%s: %s' % (tag,repr(tree.n))
        self.trace(tree,tag)

    def do_Slice (self,tree,tag=''):
        self.trace(tree,tag)
        if hasattr(tree,'lower') and tree.lower is not None:
            self.visit(tree.lower,'slice lower')
        if hasattr(tree,'upper') and tree.upper is not None:
            self.visit(tree.upper,'slice upper')
        if hasattr(tree,'step') and tree.step is not None:
            self.visit(tree.step,'slice step')

    def do_str (self,s,tag=''):
        self.trace(None,tag=tag,s=s,kind='str')

    def do_Str (self,tree,tag=''):
        self.trace(None,tag=tag,s=tree.s,kind='Str')

    def do_Subscript(self,tree,tag=''):
        self.trace(tree,tag)
        self.visit(tree.slice,'subscript slice')
        self.visit(tree.ctx,'subscript context')

    def do_Tuple(self,tree,tag=''):
        self.trace(tree,tag)
        for z in tree.elts:
            self.visit(z,'list elts')
        self.visit(tree.ctx,'list context')
    #@+node:ekr.20111116103733.10295: *4* a.Operators
    # arguments = (expr* args, identifier? vararg, identifier? kwarg, expr* defaults)
    # -- keyword arguments supplied to call
    # keyword = (identifier arg, expr value)

    def do_arguments(self,tree,tag=''):
        
        assert self.kind(tree) == 'arguments'
        for z in tree.args:
            self.visit(z,'arg')
            
        for z in tree.defaults:
            self.visit(z,'default arg')
            
        name = hasattr(tree,'vararg') and tree.vararg
        if name: pass
        
        name = hasattr(tree,'kwarg') and tree.kwarg
        if name: pass
        
    def do_arg(self,tree,tag=''):
        pass

    def do_BinOp (self,tree,tag=''):
        self.trace(tree,tag)
        self.visit(tree.op)
        self.visit(tree.right,'binop right')
        self.visit(tree.left,'binop left')

    def do_BoolOp (self,tree,tag=''):
        self.trace(tree,tag)
        self.visit(tree.op,'bool op')
        for z in tree.values:
            self.visit(z,'boolop value')

    def do_Compare(self,tree,tag=''):
        self.trace(tree,tag)
        self.visit(tree.left,'compare left')
        for z in tree.ops:
            self.visit(z,'compare op')
        for z in tree.comparators:
            self.visit(z,'compare comparator')

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
        self.visit(tree.operand,'unop operand')

    # unaryop = Invert | Not | UAdd | USub
    do_Invert = do_UnaryOp
    do_Not = do_UnaryOp
    do_UAdd = do_UnaryOp
    do_USub = do_UnaryOp
    #@+node:ekr.20111116103733.10296: *3* a.Interactive & Module & Suite
    def do_Interactive(self,tree,tag=''):
        self.trace(tree,tag)
        for z in tree.body:
            self.visit(z,'interactive body')

    def do_Module (self,tree,tag=''):
        self.trace(tree,tag)
        for z in tree.body:
            self.visit(z,'module body')

    def do_Suite(self,tree,tag=''):
        self.trace(tree,tag)
        for z in tree.body:
            self.visit(z,'suite body')
    #@+node:ekr.20111116103733.10297: *3* a.Statements
    #@+node:ekr.20111116103733.10298: *4* a.Statements (assignments)
    def do_Assign(self,tree,tag=''):

        self.trace(tree,tag)
        self.visit(tree.value,'assn value')
        for z in tree.targets:
            self.visit(z,'assn target')

    def do_AugAssign(self,tree,tag=''):

        self.trace(tree,tag)
        self.trace(tree.op)
        self.visit(tree.value,'aug-assn value')
        self.visit(tree.target,'aut-assn target')
    #@+node:ekr.20111116103733.10299: *4* a.Statements (classes & functions)
       # identifier name,
        # expr* bases,
        # stmt* body,
        # expr *decorator_list)

    def do_ClassDef (self,tree,tag=''):
        self.trace(tree,tag)
        self.visit(tree.name,'class name')
        for z in tree.body:
            self.visit(z,'body')

    def do_FunctionDef (self,tree,tag=''):
        self.trace(tree,tag)
        self.visit(tree.name,'function name')
        for z in tree.body:
            self.visit(z,'body')

    def do_Lambda (self,tree,tag=''):
        self.trace(tree,tag)
        self.visit(tree.args,'lambda args')
        self.visit(tree.body,'lambda body')
    #@+node:ekr.20111116103733.10300: *4* a.Statements (compound)
    def do_For (self,tree,tag=''):
        self.trace(tree,tag)
        self.visit(tree.target,'for target')
        self.visit(tree.iter,'for iter')
        for z in tree.body:
            self.visit(z,'for body')
        for z in tree.orelse:
            self.visit(z,'for else')

    def do_If (self,tree,tag=''):
        self.trace(tree,tag)
        self.visit(tree.test,'if test')
        for z in tree.body:
            self.visit(z,'if body')
        for z in tree.orelse:
            self.visit(z,'if orelse')

    def do_With (self,tree,tag=''):
        self.trace(tree,tag)
        if hasattr(tree,'context_expression'):
            self.visit(tree.context_expresssion)
        if hasattr(tree,'optional_vars'):
            pass ### tree.optional_vars may be a name.
            # for z in tree.optional_vars:
                # self.visit(z,'with vars')
        for z in tree.body:
            self.visit(z,'with body')

    def do_While (self,tree,tag=''):
        self.trace(tree,tag)
        self.visit(tree.test,'while expr test')
        for z in tree.body:
            self.visit(z,'while body')
        for z in tree.orelse:
            self.visit(z,'while orelse')
    #@+node:ekr.20111116103733.10301: *4* a.Statements (exceptions)
    def do_ExceptHandler(self,tree,tag=''):
        self.trace(tree,tag)
        if hasattr(tree,'type') and tree.type:
            self.visit(tree.type,'except handler type')
        if hasattr(tree,'name') and tree.name:
            self.visit(tree.name,'except handler name')
        for z in tree.body:
            self.visit(z,'except handler body')

    def do_Raise(self,tree,tag=''):
        self.trace(tree,tag)
        if hasattr(tree,'type') and tree.type is not None:
            self.visit(tree.type,'raise type')
        if hasattr(tree,'inst') and tree.inst is not None:
            self.visit(tree.inst,'raise inst')
        if hasattr(tree,'tback') and tree.tback is not None:
            self.visit(tree.tback,'raise tback')

    def do_TryExcept(self,tree,tag=''):
        self.trace(tree,tag)
        for z in tree.body:
            self.visit(z,'try except body')
        for z in tree.handlers:
            self.visit(z,'try except handler')
        for z in tree.orelse:
            self.visit(z,'try orelse')

    def do_TryFinally(self,tree,tag=''):
        self.trace(tree,tag)
        for z in tree.body:
            self.visit(z,'try finally body')
        for z in tree.finalbody:
            self.visit(z,'try finalbody')
    #@+node:ekr.20111116103733.10302: *4* a.Statements (import) (AstTraverser)
    def do_Import(self,tree,tag=''):
        self.trace(tree,tag)
        for z in tree.names:
            self.visit(z,'import name')

    def do_ImportFrom(self,tree,tag=''):
        self.trace(tree,tag)
        self.visit(tree.module)
        if hasattr(tree,'level') and tree.level is not None:
            self.visit(tree.level,'import level')
        for z in tree.names:
            self.visit(z,'import alias name')

    # identifier name, identifier? asname)
    def do_alias(self,tree,tag=''):
        self.trace(tree,tag)
        self.visit(tree.name)
        if hasattr(tree,'asname') and tree.asname is not None:
            self.visit(tree.asname,'import as name')

    #@+node:ekr.20111116103733.10303: *4* a.Statements (simple)
    def do_Assert(self,tree,tag=''):
        self.trace(tree,tag)
        self.visit(tree.test,'assert test')
        if hasattr(tree,'msg') and tree.msg:
            self.visit(tree.msg,'assert message')

    def do_Break(self,tree,tag=''):
        self.trace(tree,tag)

    def do_Continue(self,tree,tag=''):
        self.trace(tree,tag)

    def do_Delete(self,tree,tag=''):
        self.trace(tree,tag)
        for z in tree.targets:
            self.visit(z,'del targets')

    # Python 2.x only
    def do_Exec(self,tree,tag=''):
        self.trace(tree,tag)
        self.visit(tree.body,'exec body')
        if hasattr(tree,'globals') and tree.globals:
            self.visit(tree.globals,'exec globals')
        if hasattr(tree,'locals') and tree.locals:
            self.visit(tree.locals,'exec locals')

    def do_Global(self,tree,tag=''):
        self.trace(tree,tag)
        for z in tree.names:
            self.visit(z,'global name')

    def do_Pass(self,tree,tag=''):
        self.trace(tree,tag)

    # Python 2.x only
    def do_Print(self,tree,tag=''):
        self.trace(tree,tag)
        if hasattr(tree,'dest') and tree.dest:
            self.visit(tree.dest,'print dest')
        for z in tree.values:
            self.visit(z,'print value')
        self.visit(tree.nl,'print nl')

    # Python 2.x only
    def do_Repr(self,tree,tag=''):
        self.trace(tree,tag)
        self.visit(tree.value,'repr value')

    def do_Return(self,tree,tag=''):
        self.trace(tree,tag)
        if tree.value:
            self.visit(tree.value,'return value')

    def do_Yield(self,tree,tag=''):
        self.trace(tree,tag)
        if hasattr(tree,'value') and tree.value:
            self.visit(tree.value,'yield value')
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

#@+others
#@+node:ekr.20111116103733.10539: **  Top-level functions
#@+node:ekr.20111116103733.10337: *3* chain_base
# This global function exists avoid duplicate code
# in the Chain and SymbolTable classes.

def chain_base (s):
    
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
#@+node:ekr.20111116103733.10540: *3* inspect.module
def module (fn=None,s=None,sd=None,print_stats=False,print_times=False):

    if s:
        fn = '<string file>'
    else:
        s = LeoCoreFiles().get_source(fn)
        if not s:
            print('file not found: %s' % (fn))
            return None
        
    t1 = time.clock()

    if not sd:
        sd = SemanticData(controller=None)
    InspectTraverser(fn,sd).traverse(s)
    module = sd.modules_dict.get(fn)
           
    sd.total_time = time.clock()-t1

    if print_times: sd.print_times()
    if print_stats: sd.print_stats()
    
    return module
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
        annotate_fields = True, # True: include attribute names.
        include_attributes = False, # True: include lineno and col_offset attributes.
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

        s = self._dumpTreeAsNodes(tree,brief=brief) # was visitTree
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
        delta = 4 # The number of spaces for each indentation.
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

        g.es_print(s,color='red')
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
    #@+node:ekr.20111116103733.10339: *3*  ctor, repr
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

        return chain_base(self.s)
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
#@+node:ekr.20111117031039.10133: ** class AstFormatter (AstTraverser)
class AstFormatter (AstTraverser):
    
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
        self.options = options or {}
        self.result = []
        self.stack = []
        self.trace_flag = False # Subclasses may set this.
    #@+node:ekr.20111117031039.10259: *3* f.append
    def append(self,s):
        
        self.result.append(s)
            
    #@+node:ekr.20111117031039.10260: *3* f.format
    def format (self,tree):

        return self.visit(tree)
        # return ''.join(self.result)
    #@+node:ekr.20111117031039.10221: *3* f.push, pop & peep
    def push (self):
        self.stack.append(self.result)
        self.result = []
        
    def pop (self):
        val = ''.join(self.result)
        self.result = self.stack.pop()
        return val

    def peek(self):
        
        return ''.join(self.stack[-1])
    #@+node:ekr.20111117031039.10395: *3* f.visit
    def visit (self,tree,tag=None):

        '''Visit the ast tree node, dispatched by node type.'''

        kind = tree.__class__
        f = self.dispatch_table.get(kind)
        if f:
            self.push()
            f(tree,tag)
            val = self.pop()
            if self.trace_flag:
                g.trace(f.__name__,val)
            return val
        else:
            g.trace('**** bad ast type',kind)
            return None
    #@+node:ekr.20111117031039.10193: *3* f.Contexts
    #@+node:ekr.20111117031039.10194: *4* f.ClassDef
    # ClassDef(identifier name, expr* bases, stmt* body, expr* decorator_list)

    def do_ClassDef (self,tree,tag=''):
        
        name = self.visit(tree.name,'class name')
        
        bases = []
        if tree.bases:
            for z in tree.bases:
                bases.append(self.visit(z,'class base'))
                
        if bases:
            self.append('class (%s):' % (','.join(bases)))
        else:
            self.append('class %s:' % name)

        for z in tree.body:
            self.append(self.visit(z,'body'))
            # self.append('\n')
    #@+node:ekr.20111117031039.10195: *4* f.FunctionDef
    # FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list)

    def do_FunctionDef (self,tree,tag=''):
        
        if tree.decorator_list:
            for z in tree.decorator_list:
                decorator = self.visit(z,'decorator')
                self.append('@%s\n' % decorator)
        
        def_name = self.visit(tree.name,'function name')
        
        if tree.args:
            args = self.visit(tree.args,'arg')
        else:
            args = ''
            
        self.append('def %s(%s):' % (def_name,args))

        for z in tree.body:
            self.append(self.visit(z,'body'))
            # self.append('\n')
    #@+node:ekr.20111117031039.10197: *4* f.Module
    def do_Module (self,tree,tag=''):
        
        for z in tree.body:
            self.append(self.visit(z,'module body'))
            # sefl.append('\n')
    #@+node:ekr.20111117031039.10198: *3* f.Operands
    #@+node:ekr.20111117031039.10683: *4* f.arguments
    # arguments = (expr* args, identifier? vararg, identifier? kwarg, expr* defaults)
    # -- keyword arguments supplied to call
    # keyword = (identifier arg, expr value)

    def do_arguments(self,tree,tag=''):
        
        kind = self.kind(tree)
        assert kind == 'arguments',kind
        
        args = []
        for z in tree.args:
            args.append(self.visit(z,'arg'))
            
        defaults = []
        for z in tree.defaults:
            defaults.append(self.visit(z,'default arg'))
        
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
        
        self.append(','.join(args2))
    #@+node:ekr.20111117031039.10696: *4* f.arg
    def do_arg(self,tree,tag=''):
        
        self.append(self.visit(tree.arg))
    #@+node:ekr.20111117031039.10199: *4* f.Attribute & helper
    # Attribute(expr value, identifier attr, expr_context ctx)

    def do_Attribute(self,tree,tag=''):
        
        name = tree.attr

        expr = self.visit(tree.value,'attribute value')
        
        self.append('%s.%s' % (expr,name))
    #@+node:ekr.20111117031039.10558: *4* f.Dict
    def do_Dict(self,tree,tag=''):
        
        keys = []
        for z in tree.keys:
            keys.append(self.visit(z,'dict keys'))
            
        values = []
        for z in tree.values:
            values.append(self.visit(z,'dict values'))
            
        if len(keys) == len(values):
            self.append('{')
            items = []
            for i in range(len(keys)):
                items.append('%s:%s' % (keys[i],values[i]))
            self.append(','.join(items))
            self.append('}')
        else:
            g.trace('*** Error *** keys: %s values: %s' % (
                repr(keys),repr(values)))
    #@+node:ekr.20111117031039.10559: *4* f.Elipsis
    def do_Ellipsis(self,tree,tag=''):
        
        self.append('...')
    #@+node:ekr.20111117031039.10572: *4* f.ExtSlice
    def do_ExtSlice (self,tree,tag=''):
        
        dims = []
        for z in tree.dims:
            self.append(self.visit(z,'slice dimention'))
            
        # self.append('[%s]' % (':'.join(dims)))
        self.append(':'.join(dims))
    #@+node:ekr.20111117031039.10571: *4* f.Index
    def do_Index (self,tree,tag=''):
        
        self.append(self.visit(tree.value,'index value'))
    #@+node:ekr.20111117031039.10354: *4* f.Keyword
    # keyword = (identifier arg, expr value)

    def do_Keyword(self,tree,tag=''):

        # tree.arg is a string.
        val = self.visit(tree.value,'keyword value')

        self.append('%s=%s' % (tree.arg,val))
    #@+node:ekr.20111117031039.10567: *4* f.List
    def do_List(self,tree,tag=''):
        
        elts = []
        for z in tree.elts:
            elts.append(self.visit(z,'list elts'))
            
        # self.visit(tree.ctx,'list context')
        
        self.append('(%s)' % ','.join(elts))
    #@+node:ekr.20111117031039.10204: *4* f.ListComp & Comprehension TEST
    def do_ListComp(self,tree,tag=''):

        elt = self.visit(tree.elt,'list comp elt')

        generators = []
        for z in tree.generators:
            generators.append(self.visit(z,'list comp generator'))
            
        self.append('[%s for %s in %s]' % (elt,elt,''.join(generators)))

    def do_comprehension(self,tree,tag=''):

        name = self.visit(tree.target,'comprehension target (a Name)')
        
        it = self.visit(tree.iter,'comprehension iter (an Attribute)')

        ifs = []
        for z in tree.ifs:
            ifs.append(self.visit(z,'comprehension if'))
            
        self.append('**comprehension** name: %s ifs: %s' % (name,''.join(ifs)))
    #@+node:ekr.20111117031039.10203: *4* f.Name
    def do_Name(self,tree,tag=''):

        self.append(tree.id)
    #@+node:ekr.20111117031039.10573: *4* f.Slice
    def do_Slice (self,tree,tag=''):
        
        lower,upper,step = '','',''
        
        if hasattr(tree,'lower') and tree.lower is not None:
            lower = self.visit(tree.lower,'slice lower')
            
        if hasattr(tree,'upper') and tree.upper is not None:
            upper = self.visit(tree.upper,'slice upper')
            
        if hasattr(tree,'step') and tree.step is not None:
            step = self.visit(tree.step,'slice step')
            
        if step:
            self.append('%s:%s:%s' % (lower,upper,step))
        else:
            self.append('%s:%s' % (lower,upper))
    #@+node:ekr.20111117031039.10455: *4* f.Str
    def do_str (self,s,tag=''):

        self.append(s)

    def do_Str (self,tree,tag=''):
        
        self.append(repr(tree.s))
    #@+node:ekr.20111117031039.10574: *4* f.Subscript
    # Subscript(expr value, slice slice, expr_context ctx)

    def do_Subscript(self,tree,tag=''):
        
        value = self.visit(tree.value,'subscript value')
        the_slice = self.visit(tree.slice,'subscript slice')
        
        self.append('%s[%s]' % (value,the_slice))
        
        
        
        # self.append(self.visit(tree.slice,'subscript slice'))

        # self.visit(tree.ctx,'subscript context')
    #@+node:ekr.20111117031039.10560: *4* f.Tuple
    def do_Tuple(self,tree,tag=''):
        
        elts = []
        for z in tree.elts:
            elts.append(self.visit(z,'list elts'))
            
        self.append(','.join(elts))

        # self.visit(tree.ctx,'list context')
    #@+node:ekr.20111117031039.10557: *4* formatter:simple operands
    # Python 2.x only.
    def do_bool(self,tree,tag=''):
        g.trace(tree)

    def do_int (self,s,tag=''):
        self.append(s)

    def do_Num(self,tree,tag=''):
        self.append(repr(tree.n))
    #@+node:ekr.20111117031039.10421: *3* f.Operators
    #@+node:ekr.20111117031039.10487: *4* f.BinOp
    def do_BinOp (self,tree,tag=''):
        
        op = self.visit(tree.op,'binop op')
        rt = self.visit(tree.right,'binop right')
        lt = self.visit(tree.left,'binop left')

        self.append('%s%s%s' % (lt,op,rt))
    #@+node:ekr.20111117031039.10488: *4* f.BoolOp
    def do_BoolOp (self,tree,tag=''):
        
        op = self.visit(tree.op,'bool op')

        values = []
        for z in tree.values:
            values.append(self.visit(z,'boolop value'))

        self.append(op.join(values))
        
    #@+node:ekr.20111117031039.10489: *4* f.Compare
    def do_Compare(self,tree,tag=''):
        
        lt = self.visit(tree.left,'compare left')
        
        ops = []
        for z in tree.ops:
            ops.append(self.visit(z,'compare op'))

        comparators = []
        for z in tree.comparators:
            comparators.append(self.visit(z,'compare comparator'))
            
        self.append(lt)
            
        if len(ops) == len(comparators):
            for i in range(len(ops)):
                self.append('%s%s' % (ops[i],comparators[i]))
        else:
            g.trace('ops',repr(ops),'comparators',repr(comparators))
    #@+node:ekr.20111117031039.10495: *4* f.UnaryOp
    def do_UnaryOp (self,tree,tag=''):
        
        self.append(self.visit(tree.operand,'unop operand'))
    #@+node:ekr.20111117031039.10491: *4* f.arithmetic operators
    # operator = Add | BitAnd | BitOr | BitXor | Div
    # FloorDiv | LShift | Mod | Mult | Pow | RShift | Sub | 

    def do_Add(self,tree,tag=''):       self.append('+')
    def do_BitAnd(self,tree,tag=''):    self.append('&')
    def do_BitOr(self,tree,tag=''):     self.append('|')
    def do_BitXor(self,tree,tag=''):    self.append('^')
    def do_Div(self,tree,tag=''):       self.append('/')
    def do_FloorDiv(self,tree,tag=''):  self.append('//')
    def do_LShift(self,tree,tag=''):    self.append('<<')
    def do_Mod(self,tree,tag=''):       self.append('%')
    def do_Mult(self,tree,tag=''):      self.append('*')
    def do_Pow(self,tree,tag=''):       self.append('**')
    def do_RShift(self,tree,tag=''):    self.append('>>')
    def do_Sub(self,tree,tag=''):       self.append('-')
    #@+node:ekr.20111117031039.10490: *4* f.boolean operators
    # boolop = And | Or
    def do_And(self,tree,tag=''):   self.append(' and ')
    def do_Or(self,tree,tag=''):    self.append(' or ')
    #@+node:ekr.20111117031039.10492: *4* f.comparison operators
    # cmpop = Eq | Gt | GtE | In | Is | IsNot | Lt | LtE | NotEq | NotIn
    def do_Eq(self,tree,tag=''):    self.append('==')
    def do_Gt(self,tree,tag=''):    self.append('>')
    def do_GtE(self,tree,tag=''):   self.append('>=')
    def do_In(self,tree,tag=''):    self.append(' in ')
    def do_Is(self,tree,tag=''):    self.append(' is ')
    def do_IsNot(self,tree,tag=''): self.append(' is not ')
    def do_Lt(self,tree,tag=''):    self.append('<')
    def do_LtE(self,tree,tag=''):   self.append('<=')
    def do_NotEq(self,tree,tag=''): self.append('!=')
    def do_NotIn(self,tree,tag=''): self.append(' not in ')
    #@+node:ekr.20111117031039.10493: *4* f.expression operators
    def do_op(self,tree,tag=''):
        pass
        
    # def do_expression_context(self,tree,tag=''):
        # self.trace_flag(tree,tag)

    do_AugLoad  = do_op
    do_AugStore = do_op
    do_Del      = do_op
    do_Load     = do_op
    do_Param    = do_op
    do_Store    = do_op
    #@+node:ekr.20111117031039.10494: *4* f.unary opertors
    # unaryop = Invert | Not | UAdd | USub

    def do_Invert(self,tree,tag=''):    self.append('~')
    def do_Not(self,tree,tag=''):       self.append(' not ')
    def do_UAdd(self,tree,tag=''):      self.append('+')
    def do_USub(self,tree,tag=''):      self.append('-')
    #@+node:ekr.20111117031039.10205: *3* f.Statements
    #@+node:ekr.20111117031039.10206: *4* f.Assign
    def do_Assign(self,tree,tag=''):

        val = self.visit(tree.value,'assn value')
            
        targets = []
        for z in tree.targets:
            targets.append(self.visit(z,'assn target'))

        targets = '='.join(targets)
        self.append('%s=%s' % (targets,val))
    #@+node:ekr.20111117031039.10207: *4* f.AugAssign
    def do_AugAssign(self,tree,tag=''):
        
        op = self.visit(tree.op)
        rhs = self.visit(tree.value,'aug-assn value')
        lhs = self.visit(tree.target,'aut-assn target')

        self.append('%s%s%s\n' % (lhs,op,rhs))
    #@+node:ekr.20111117031039.10208: *4* f.Call
    def do_Call(self,tree,tag=''):
        
        func = self.visit(tree.func,'call func')
        
        # Unlike 'ast.arguments, ast.Call has no defaults.
        args = []
        for z in tree.args:
            args.append(self.visit(z,'call args'))

        for z in tree.keywords:
            args.append(self.visit(z,'call keyword args'))

        if hasattr(tree,'starargs') and tree.starargs:
            args.append('*%s' % (self.visit(tree.starargs,'call *arg')))

        if hasattr(tree,'kwargs') and tree.kwargs:
            args.append('**%s' % (self.visit(tree.kwargs,'call **args')))
            
        self.append('%s(%s)' % (func,','.join(args)))
    #@+node:ekr.20111117031039.10209: *4* f.For
    def do_For (self,tree,tag=''):
        
        self.append('for ')
        self.append(self.visit(tree.target,'for target'))
        self.append(' in ')
        self.append(self.visit(tree.iter,'for iter'))
        self.append(':\n')
        
        for z in tree.body:
            self.append(self.visit(z,'for body'))
            # self.append('\n')

        if tree.orelse:
            self.append('else:')
            for z in tree.orelse:
                self.append(self.visit(z,'for else'))
                # self.append('\n')
    #@+node:ekr.20111117031039.10210: *4* f.Global
    def do_Global(self,tree,tag=''):

        self.append('global ')
        self.append(','.join(tree.names))
        self.append('\n')
    #@+node:ekr.20111117031039.10211: *4* f.Import & helper
    def do_Import(self,tree,tag=''):
        
        self.append('import ')
        
        names = []
        for fn,asname in self.get_import_names(tree):
            if asname:
                names.append('%s as %s' % (fn,asname))
            else:
                names.append(fn)
                
        self.append(','.join(names))
        self.append('\n')
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
    def do_ImportFrom(self,tree,tag=''):
        
        self.append('from %s import ' % (tree.module))

        names = []
        for fn,asname in self.get_import_names(tree):
            if asname:
                names.append('%s as %s' % (fn,asname))
            else:
                names.append(fn)
            
        self.append(','.join(names))
        self.append('\n')
    #@+node:ekr.20111117031039.10215: *4* f.Lambda & helper
    def do_Lambda (self,tree,tag=''):
        
        self.append('lambda ')
        self.append(self.visit(tree.args,'lambda args'))
        self.append(':\n')
        self.append(self.visit(tree.body,'lambda body'))
        # self.append('\n')
    #@+node:ekr.20111117031039.10972: *4* f.Pass
    def do_Pass(self,tree,tag=''):
        
        self.append('pass')
    #@+node:ekr.20111117031039.10217: *4* f.With
    def do_With (self,tree,tag=''):
        
        self.append('with ')
        
        if hasattr(tree,'context_expression'):
            result.append(self.visit(tree.context_expresssion,'context expr'))

        vars_list = []
        if hasattr(tree,'optional_vars'):
            try:
                for z in tree.optional_vars:
                    vars_list.append(self.visit(z,'with vars'))
            except TypeError: # Not iterable.
                vars_list.append(self.visit(tree.optional_vars,'with var'))
                
        self.append(','.join(vars_list))
        self.append(':\n')
        
        for z in tree.body:
            self.append(self.visit(z,'with body'))
            # self.append('\n')
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
        self.formatter.trace = self.trace_flag
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
        old_cx._classes.append(new_cx)
        
        self.push_context(new_cx)

        self.visit(tree.name,'class name')

        for z in tree.body:
            self.visit(z,'body')
       
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
        old_cx._defs.append(new_cx)
        
        self.push_context(new_cx)
       
        self.visit(tree.name,'function name')

        # Define the function arguments before visiting the body.
        # These arguments, including 'self', are known in the body.
        self.def_args_helper(new_cx,tree.args)
        
        # Visit the body.
        for z in tree.body:
            self.visit(z,'body')

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
            self.visit(z,'arg')
            
        for z in tree.defaults:
            self.visit(z,'default arg')

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
                self.visit(z,'module body')
        finally:
            self.pop_context()
    #@+node:ekr.20111125131712.10256: *3* it.Operands
    # Use the AstFormatter methods for all operands except do_Attribute and do_Name.

    # Note:  self.formatter is a delegate object: it would be bad style
    # to make InspectTraverser a subclass of AstFormatter.

    def format_tree(self,tree,tag=''):
        val = self.formatter.visit(tree)
        if self.trace_flag: g.trace(tag,val)
        return val
        
    # do_Attribute
    do_bool         = format_tree
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
        expr = self.formatter.visit(tree.value,'attribute value')
        s = '%s.%s' % (expr,name)
        
        if self.trace_flag: g.trace(s)
        
        chain = cx.st.add_chain(tree,s)

        self.formatter.append(s)
            # For recursive calls.
            
        self.sd.n_attributes += 1
    #@+node:ekr.20111125131712.10278: *4* it.Name
    def do_Name(self,tree,tag=''):

        name = tree.id

        if g.isPython3:
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
    #@+node:ekr.20111116103733.10368: *3* it.Statements
    #@+node:ekr.20111116103733.10369: *4* it.Assign
    def do_Assign(self,tree,tag=''):
        
        sd = self.sd
        
        cx = self.get_context()
        cx._statements.append(StatementContext(tree,cx,sd,'assn'))

        self.visit(tree.value,'assn value')    
        for z in tree.targets:    
            self.visit(z,'assn target')

        sd.n_assignments += 1
    #@+node:ekr.20111116103733.10370: *4* it.AugAssign
    def do_AugAssign(self,tree,tag=''):
        
        sd = self.sd

        cx = self.get_context()
        cx._statements.append(StatementContext(tree,cx,sd,'aug-assn'))

        self.visit(tree.op)
        self.visit(tree.value,'aug-assn value') # The rhs.
        self.visit(tree.target,'aut-assn target') # The lhs.

        sd.n_assignments += 1
    #@+node:ekr.20111116103733.10365: *4* it.Call
    def do_Call(self,tree,tag=''):
        
        sd = self.sd
        cx = self.get_context()
        cx._statements.append(StatementContext(tree,cx,sd,'call'))
        
        sd.n_calls += 1
        
        self.visit(tree.func,'call func')
        
        for z in tree.args:
            self.visit(z,'call args')

        for z in tree.keywords:
            self.visit(z,'call keywords')

        if hasattr(tree,'starargs') and tree.starargs:
            self.visit(tree.starargs,'call starags')

        if hasattr(tree,'kwargs') and tree.kwargs:
            self.visit(tree.kwargs,'call kwargs')
    #@+node:ekr.20111116103733.10371: *4* it.For
    def do_For (self,tree,tag=''):
        
        # Define a namespace for the 'for' target.
        old_cx = self.get_context()
        new_cx = ForContext(tree,old_cx,self.sd)
        old_cx._statements.append(new_cx)
        old_cx.temp_contexts.append(new_cx)
        
        self.push_context(new_cx)
        
        self.visit(tree.target,'for target')

        self.visit(tree.iter,'for iter')
        
        for z in tree.body:
            self.visit(z,'for body')

        for z in tree.orelse:
            self.visit(z,'for else')

        self.pop_context()
        
        self.sd.n_fors += 1
    #@+node:ekr.20111116103733.10372: *4* it.Global
    def do_Global(self,tree,tag=''):

        '''Enter the names in a 'global' statement into the *module* symbol table.'''

        sd = self.sd
        cx = self.get_context()
        cx._statements.append(StatementContext(tree,cx,sd,'global'))

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
        cx._statements.append(StatementContext(tree,cx,sd,'import'))
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
        cx._statements.append(StatementContext(tree,cx,sd,'import from'))

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
        old_cx._statements.append(new_cx)
        old_cx.temp_contexts.append(new_cx)
        
        self.push_context(new_cx)

        # Enter the target names in the 'lambda' context.
        self.def_lambda_args_helper(new_cx,tree.args)

        # Enter all other definitions in the defining_context.
        self.visit(tree.body,'lambda body')

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
            self.visit(z,'arg')
            
        for z in tree.defaults:
            self.visit(z,'default arg')

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
        old_cx._statements.append(new_cx)
        old_cx.temp_contexts.append(new_cx)
        
        self.push_context(new_cx)
        
        if hasattr(tree,'context_expression'):
            self.visit(tree.context_expresssion)

        if hasattr(tree,'optional_vars'):
            try:
                for z in tree.optional_vars:
                    self.visit(z,'with vars')
            except TypeError: # Not iterable.
                self.visit(tree.optional_vars,'with var')
        
        for z in tree.body:
            self.visit(z,'with body')

        self.pop_context()
        
        self.sd.n_withs += 1
    #@+node:ekr.20111116103733.10352: *3* it.traverse
    def traverse (self,s):
        
        '''Perform all checks on the source in s.'''
        
        sd = self.sd
        
        t1 = time.clock()

        tree = ast.parse(s,filename=self.fn,mode='exec')

        t2 = time.clock()
        sd.parse_time += t2-t1
        
        self.visit(tree,tag='top')
        
        t3 = time.clock()
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
            'leo_Debugger.py','leo_FileList.py',
            'leo_RemoteDebugger.py','leo_run.py',
            'leo_Shell.py',
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
    #@+node:ekr.20111116103733.10382: *3* sd.all_contexts (generator)
    def all_contexts (self,aList=None):
        
        '''An iterator returning all contexts.'''
        
        if not aList:
            aList = list(self.modules_dict.values())

        for cx in aList:
            yield cx
            if cx._classes:
                for z in self.all_contexts(cx._classes):
                    yield z
            if cx.functions:
                for z in self.all_contexts(cx.functions):
                    yield z
            if cx.temp_contexts:
                for z in self.all_contexts(cx.temp_contexts):
                    yield z
    #@+node:ekr.20111116103733.10383: *3* sd.dump
    def dump (self,verbose=True):
        
        sd = self
        print('\nDump of modules...')
        for cx in sd.all_contexts():
            print('')
            cx.dump(verbose=verbose)
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
        base = chain_base(s)
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
        
        print(self)

        # Print the table entries.
        keys = list(self.d.keys())
        keys.sort()
        for key in keys:
            print(self.d.get(key))
            
        # Print non-empty ctx lists.
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
            unbound = g.choose(self.load_before_store_flag,
                ': <unbound>','')
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
#@+node:ekr.20111116103733.10401: ** Context classes
#@+<< define class Context >>
#@+node:ekr.20111116103733.10402: *3* << define class Context >>
class Context(object):

    '''The base class of all context-related semantic data.

    All types ultimately resolve to a context.'''

    def __repr__ (self):
        return 'Context: %s' % (self.context_kind)

    __str__ = __repr__

    #@+others
    #@+node:ekr.20111116103733.10403: *4* cx ctor
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
        self._classes = [] # Classes defined in this context.
        self._defs = [] # Functions defined in this context.
        self._statements = [] # List of all statements in the context.
        self._tree = tree
        
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
    #@+node:ekr.20111116103733.10404: *4* cx.ast_kind
    def ast_kind (self,tree):

        return tree.__class__.__name__
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
    def dump (self,level=0,verbose=False):

        if 0: # Just print the context
            print(repr(self))
        else:
            self.st.dump(level=level)

        if verbose:
            for z in self._classes:
                z.dump(level+1)
            for z in self._defs:
                z.dump(level+1)
            for z in self.temp_contexts:
                z.dump(level+1)
    #@+node:ekr.20111117031039.10099: *4* cx.format
    def format(self,brief=True):
        
        cx = self
        
        # return cx.sd.dumper.dumpTreeAsString(cx._tree,brief=brief,outStream=None)
        
        # return ast.dump(cx._tree,annotate_fields=True,include_attributes=not brief)
        
        return AstFormatter().format(cx._tree)
    #@+node:ekr.20111116161118.10113: *4* cx.getters & setters
    #@+node:ekr.20111116161118.10114: *5* cx.assignments & helper
    def assignments (self,all=True):
        
        if all:
            return self.all_assignments(result=None)
        else:
            return self.filter_assignments(self._statements)

    def all_assignments(self,result):

        if result is None:
            result = []
        result.extend(self.filter_assignments(self._statements))
        for aList in (self._classes,self._defs):
            for cx in aList:
                cx.all_assignments(result)
        return result
        
    def filter_assignments(self,aList):
        '''Return all the assignments in aList.'''
        return [z for z in aList
            if z.context_kind in ('assn','aug-assn')]
    #@+node:ekr.20111116161118.10115: *5* cx.assignments_to
    def assignments_to (self,s,all=True):
        
        format,result = self.formatter.format,[]

        for assn in self.assignments(all=all):
            tree = assn.tree()
            kind = self.ast_kind(tree)
            if kind == 'Assign':
                for target in tree.targets:
                    lhs = format(target)
                    if s == lhs:
                        result.append(assn)
                        break
            else:
                assert kind == 'AugAssign',kind
                lhs = format(tree.target)
                if s == lhs:
                    result.append(assn)

        return result
    #@+node:ekr.20111116161118.10116: *5* cx.assignments_using
    def assignments_using (self,s,all=True):
        
        format,result = self.formatter.format,[]

        for assn in self.assignments(all=all):
            tree = assn.tree()
            kind = self.ast_kind(tree)
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
    #@+node:ekr.20111126074312.10386: *5* cx.calls & helpers
    def calls (self,all=True):
        
        if all:
            return self.all_calls(result=None)
        else:
            return self.filter_calls(self._statements)

    def all_calls(self,result):

        if result is None:
            result = []
        result.extend(self.filter_calls(self._statements))
        for aList in (self._classes,self._defs):
            for cx in aList:
                cx.all_calls(result)
        return result
        
    def filter_calls(self,aList):
        '''Return all the calls in aList.'''
        return [z for z in aList
            if z.context_kind == 'call']
    #@+node:ekr.20111126074312.10384: *5* cx.call_to
    def calls_to (self,s,all=True):
        
        format,result = self.formatter.format,[]

        for call in self.calls(all=all):
            tree = call.tree()
            func = format(tree.func)
            if s == func:
                result.append(call)

        return result
    #@+node:ekr.20111126074312.10400: *5* cx.call_args_of
    def call_args_of (self,s,all=True):
        
        format,result = self.formatter.format,[]

        for call in self.calls(all=all):
            tree = call.tree()
            func = format(tree.func)
            if s == func:
                result.append(call)

        return result
    #@+node:ekr.20111116161118.10163: *5* cx.classes
    def classes (self,all=True):
        
        if all:
            return self.all_classes(result=None)
        else:
            return self._classes

    def all_classes(self,result):

        if result is None:
            result = []
        result.extend(self._classes)
        for aList in (self._classes,self._defs):
            for cx in aList:
                cx.all_classes(result)
        return result
    #@+node:ekr.20111116161118.10164: *5* cx.defs
    def defs (self,all=True):
        
        if all:
            return self.all_defs(result=None)
        else:
            return self._defs

    def all_defs(self,result):

        if result is None:
            result = []
        result.extend(self._defs)
        for aList in (self._classes,self._defs):
            for cx in aList:
                cx.all_defs(result)
        return result
    #@+node:ekr.20111116161118.10152: *5* cx.functions & helpers
    def functions (self,all=True):
        
        if all:
            return self.all_functions(result=None)
        else:
            return self.filter_functions(self._defs)

    def all_functions(self,result):

        if result is None:
            result = []
        result.extend(self.filter_functions(self._defs))
        for aList in (self._classes,self._defs):
            for cx in aList:
                cx.all_functions(result)
        return result
    #@+node:ekr.20111116161118.10223: *6* cx.filter_functions & is_function
    def filter_functions(self,aList):
        return [z for z in aList if self.is_function(z)]

    def is_function(self,f):
        '''Return True if f is a function, not a method.'''
        return True
    #@+node:ekr.20111126074312.10449: *5* cx.line_number
    def line_number (self):
        
        return self._tree.lineno
    #@+node:ekr.20111116161118.10153: *5* cx.methods & helpers
    def methods (self,all=True):
        
        if all:
            return self.all_methods(result=None)
        else:
            return self.filter_methods(self._defs)

    def all_methods(self,result):

        if result is None:
            result = []
        result.extend(self.filter_methods(self._defs))
        for aList in (self._classes,self._defs):
            for cx in aList:
                cx.all_methods(result)
        return result
    #@+node:ekr.20111116161118.10225: *6* cx.filter_functions & is_function
    def filter_methods(self,aList):
        return [z for z in aList if self.is_method(z)]

    def is_method(self,f):
        '''Return True if f is a method, not a function.'''
        return True
    #@+node:ekr.20111116161118.10165: *5* cx.statements
    def statements (self,all=True):
        
        if all:
            return self.all_statements(result=None)
        else:
            return self._statements

    def all_statements(self,result):

        if result is None:
            result = []
        result.extend(self._statements)
        for aList in (self._classes,self._defs):
            for cx in aList:
                cx.all_statements(result)
        return result
    #@+node:ekr.20111128103520.10259: *5* cx.token_range
    def token_range (self):
        
        tree = self._tree
        
        # return (
            # g.toUnicode(self.byte_array[:tree.col_offset]),
            # g.toUnicode(self.byte_array[:tree_end_col_offset]),
        # )
        
        if hasattr(tree,'col_offset') and hasattr(tree,'end_col_offset'):
            return tree.lineno,tree.col_offset,tree.end_lineno,tree.end_col_offset
        else:
            return -1,-1
    #@+node:ekr.20111116161118.10166: *5* cx.tree
    def tree(self):
        
        '''Return the AST (Abstract Syntax Tree) associated with this query object
        (Context Class).  This tree can be passed to the format method for printing.
        '''
        
        return self._tree
    #@-others
#@-<< define class Context >>

#@+others
#@+node:ekr.20111116103733.10413: *3* class ClassContext
class ClassContext (Context):

    '''A class to hold semantic data about a class.'''

    def __init__(self,tree,parent_context,sd):

        Context.__init__(self,tree,parent_context,sd,'class')

    def __repr__ (self):
        
        return 'class(%s)' % (self._tree.name)
        
    def name (self):
        
        return self._tree.name
    
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

        return 'def(%s)' % (self._tree.name)
        
    def name (self):
        kind = g.choose(self.class_context,'method','function')
        return '%s %s' % (kind,self._tree.name)
        
    __str__ = __repr__
#@+node:ekr.20111116103733.10416: *3* class ForContext
class ForContext (Context):

    '''A class to represent the range of a 'for' statement.'''

    def __init__(self,tree,parent_context,sd):

        Context.__init__(self,tree,parent_context,sd,'for')

    def __repr__ (self):
        kind = self.ast_kind(self._tree.target)
        if kind == 'Name':
            return 'for(%s)' % (self._tree.target.id)
        elif kind == 'Tuple':
            return 'for(%s)' % ','.join([z.id for z in self._tree.target.elts])
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

    '''A class to any statement.'''

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
#@-others
#@-leo

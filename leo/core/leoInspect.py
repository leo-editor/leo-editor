# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20111116103733.9817: * @file leoInspect.py
#@@first

'''A scriptable framework for creating queries of Leo's object code.'''

#@@language python
#@@tabwidth -4
#@@pagewidth 60

#@+<< imports >>
#@+node:ekr.20111116103733.10440: **   << imports >>
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
#@+node:ekr.20111116103733.10146: **   << naming conventions >>
#@@nocolor-node
#@+at
# 
# The following naming conventions are used throughout:
# 
# cx:   a context.
# d:    a dict.
# dep:  a Dependency.
# e:    a SymbolTableEntry object.
# f:    an open file.
# fn:   a file name.
# g:    the leo.core.leoGlobals module.
# s:    a string.
# sd:   (global) semantic data.
# st:   a symbol table (for a particular context).
# tree: an ast (parse) tree, created by Python's ast module.
# x:    a TypeInferenceEngine.
# z:    a local temp.
#@-<< naming conventions >>

#@+others
#@+node:ekr.20111116103733.10539: **   Top-level functions
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
        return base
#@+node:ekr.20111116103733.10540: *3* module
def module (c,fn,print_stats=False,print_times=False):

    s = LeoCoreFiles().get_source(fn)
    if not s:
        print('file not found: %s' % (fn))
        return None
        
    t1 = time.clock()

    sd = SemanticData(controller=None)
    InspectTraverser(c,fn,sd,s).traverse(s)
    module = sd.modules_dict.get(fn)
           
    sd.total_time = time.clock()-t1

    if print_times: sd.print_times()
    if print_stats: sd.print_stats()
    
    return module
#@+node:ekr.20111116103733.10434: **  AST classes
#@+<< define class AstTraverser >>
#@+node:ekr.20111116103733.10278: *3* << define class AstTraverser >>
class AstTraverser:

    '''The base class for AST traversal helpers.'''

    #@+others
    #@+node:ekr.20111116103733.10279: *4*  Birth (AstTraverser)
    #@+node:ekr.20111116103733.10280: *5* ctor AstTraverser
    def __init__(self,fn,s):

        self.context_stack = []
        self.fn = fn
        self.level = 0 # The indentation level (not the context level).
            # The number of parents a node has.
        self.parents = [None]
        self.s = s
        self.lines = g.splitLines(s)

        self.init_info()
        self.init_dispatch_table()
        self.init_tracing()
    #@+node:ekr.20111116103733.10281: *5* init_dispatch_table
    def init_dispatch_table (self):

        a = ast

        self.dispatch_table = d = {
            int: self.do_int,
            str: self.do_str,
            a.alias: self.do_alias,
            a.comprehension: self.do_comprehension,
            # a.id: self.do_id,
            a.keyword: self.do_keyword,
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
    #@+node:ekr.20111116103733.10282: *5* init_info
    def init_info (self):

        pass

        # INFER_NEED_NAME_STMTS = (From, Import, Global, TryExcept)
        # LOOP_SCOPES = (Comprehension, For,)


        # STMT_NODES = (
            # Assert, Assign, AugAssign, Break, Class, Continue, Delete, Discard,
            # ExceptHandler, Exec, For, From, Function, Global, If, Import, Pass, Print,
            # Raise, Return, TryExcept, TryFinally, While, With
            # )

        # ALL_NODES = STMT_NODES + (
            # Arguments, AssAttr, AssName, BinOp, BoolOp, Backquote,  CallFunc, Compare,
            # Comprehension, Const, Decorators, DelAttr, DelName, Dict, Ellipsis,
            # EmptyNode,  ExtSlice, Getattr,  GenExpr, IfExp, Index, Keyword, Lambda,
            # List,  ListComp, Module, Name, Slice, Subscript, UnaryOp, Tuple, Yield
            # )
    #@+node:ekr.20111116103733.10283: *4*  Do-nothings (AstTraverser)
    # Don't delete these. They might be useful in a subclass.
    if 0:
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
        def do_keyword(self,tree,tag=''): pass
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
    #@+node:ekr.20111116103733.10284: *4*  error (AstTraverser)
    def error (self,tree,message):
        
        g.pr('Error: %s' % (message))
        
        if isinstance(tree,ast.AST):
            line = self.lines[tree.lineno-1]
            g.pr(line.rstrip())
    #@+node:ekr.20111116103733.10285: *4*  get/push/pop_context (AstTraverser)
    def get_context (self):

        return self.context_stack[-1]

    def push_context (self,context):

        assert context
        self.context_stack.append(context)

    def pop_context (self):

        self.context_stack.pop()
    #@+node:ekr.20111116103733.10286: *4*  run (AstTraverser)
    def run (self,s):
        
        tree = ast.parse(s,filename=self.fn,mode='exec')

        self.visit(tree,tag='top')
    #@+node:ekr.20111116103733.10287: *4*  visit (AstTraverser)
    def visit (self,tree,tag=None):

        '''Visit the ast tree node, dispatched by node type.'''

        trace = False
        kind = tree.__class__
        f = self.dispatch_table.get(kind)
        # if tag == 'top': g.trace(self.kind(tree),f.__name__)
        if f:
            self.level += 1
            if isinstance(tree,ast.AST):
                tree._parent = self.parents[-1]
            self.parents.append(tree)
            try:
                # Return a value for use by subclases.
                # self.node_after_tree(tree)
                return f(tree,tag)
            finally:
                self.level -= 1
                self.parents.pop()
            # Never put a return instruction in a finally clause!
            # It causes the exception to be lost!
            return None
        else:
            if trace: g.trace('**** bad ast type',kind)
            return None
    #@+node:ekr.20111116103733.10288: *4* Dumps (AstTraverser)
    #@+node:ekr.20111116103733.10289: *5* dump(AstTraverser)
    def dump (self,tree,asString=True,brief=False,outStream=None):

        AstDumper(brief=brief).dump(tree,outStream=outStream)

    #@+node:ekr.20111116103733.10290: *5* node_after_tree
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
    #@+node:ekr.20111116103733.10291: *5* string_dump
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
    #@+node:ekr.20111116103733.10292: *4* Expressions (AstTraverser)
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
    #@+node:ekr.20111116103733.10293: *5* do_IfExp
    def do_IfExp (self,tree,tag=''):
        self.trace(tree,tag)
        self.visit(tree.test,'if-expr test')
        if tree.body:
            self.visit(tree.body,'if-expr body')
        if tree.orelse:
            self.visit(tree.orelse,'if-expr orelse')
    #@+node:ekr.20111116103733.10294: *5* Operands
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
        # try:
            # for z in tree.args:
                # self.visit(z,'call args')
        # except TypeError: # Not iterable.
            # self.visit(tree.args,'call arg')
        # try:
            # for z in tree.keywords:
                # self.visit(z,'call keyword args')
        # except TypeError: # Not iterable.
            # self.visit(tree.keywords,'call keyword arg')
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

    def do_keyword (self,tree,tag=''):
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
        # g.trace('*** id',repr(tree.id),type(tree.id))
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
    #@+node:ekr.20111116103733.10295: *5* Operators
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
    #@+node:ekr.20111116103733.10296: *4* Interactive & Module & Suite (AstTraverer)
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
    #@+node:ekr.20111116103733.10297: *4* Statements (AstTraverser)
    #@+node:ekr.20111116103733.10298: *5* Statements (assignments)
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
    #@+node:ekr.20111116103733.10299: *5* Statements (classes & functions)
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
        ### tree.args is an 'arguments' object.
        # for z in tree.args:
            # self.visit(z,'lambda arg')
        self.visit(tree.body,'lambda body')
    #@+node:ekr.20111116103733.10300: *5* Statements (compound)
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
    #@+node:ekr.20111116103733.10301: *5* Statements (exceptions)
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
    #@+node:ekr.20111116103733.10302: *5* Statements (import) (AstTraverser)
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

    #@+node:ekr.20111116103733.10303: *5* Statements (simple)
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
    #@+node:ekr.20111116103733.10304: *4* Tools (AstTraverser)
    #@+at
    # Useful tools for tree traversal and testing.
    # 
    # Something is seriously wrong if we have to worry
    # about the speed of these tools.
    #@+node:ekr.20111116103733.10305: *5* isiterable
    def isiterable (self,anObject):

        '''Return True if a non-string is iterable.'''

        return getattr(anObject, '__iter__', False)
    #@+node:ekr.20111116103733.10306: *5* op_spelling
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
    #@+node:ekr.20111116103733.10307: *5* parents (not used)
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
    #@+node:ekr.20111116103733.10308: *5* the_class, info & kind
    def the_class (self,tree):

        return tree.__class__
        
    def info (self,tree):
        
        return '%s: %9s' % (self.kind(tree),id(tree))

    def kind (self,tree):

        return tree.__class__.__name__

    #@+node:ekr.20111116103733.10309: *4* Tracing (AstTraverser)
    #@+node:ekr.20111116103733.10310: *5* init_tracing (AstTraverser)
    def init_tracing (self):

        '''May be over-ridden in subclasses.'''

        # May be over-ridden in subcalsses.
        self.enable_trace = False # Master switch.

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
    #@+node:ekr.20111116103733.10311: *5* trace (AstTraverser)
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

        if self.enable_trace and doTrace:
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
#@+node:ekr.20111116103733.10257: *3* class AstDumper
class AstDumper:

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
    #@+node:ekr.20111116103733.10258: *4* setOptions
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
    #@+node:ekr.20111116103733.10259: *4* Top level (AstDumper)
    #@+node:ekr.20111116103733.10260: *5* dumpFileAsNodes/String
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
    #@+node:ekr.20111116103733.10261: *5* dumpStringAsNodes/String
    def dumpStringAsNodes (self,fn,s,brief=False,outStream=None):

        '''Write the node representation string s to outStream.'''

        tree = ast.parse(s,filename=fn,mode='exec')
        self.brief = brief
        s = self._dumpTreeAsNodes(tree)
        self._writeAndClose(s,outStream)
        return s

    def dumpStringAsString(self,s,brief=False,outStream=None):

        '''Write the node representation string s to outStream.'''

        tree = ast.parse(s,filename='<string>',mode='exec')
        self.brief = brief
        s = self._dumpTreeAsString(tree)
        self._writeAndClose(s,outStream)
        return s
    #@+node:ekr.20111116103733.10262: *5* dumpTreeAsNodes/String
    def dumpTreeAsNodes(self,tree,brief=False,outStream=None):

        '''Write the node representation the ast tree to outStream.'''

        s = self._dumpTreeAsNodes(tree,brief=brief) # was visitTree
        self._writeAndClose(s,outStream)
        return s

    def dumpTreeAsString (self,tree,brief=False,outStream=None):

        '''Write the string representation the ast tree to outStream.'''

        s = self._dumpTreeAsString(tree,brief=brief)
        self._writeAndClose(s,outStream)
        return s
    #@+node:ekr.20111116103733.10263: *4* Helpers
    #@+node:ekr.20111116103733.10264: *5* _dumpAstNode
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
    #@+node:ekr.20111116103733.10265: *5* _dumpTreeAsNodes
    def _dumpTreeAsNodes(self,tree,brief=False):

        # annotate_fields=True,include_attributes=False):
        # self.annotate_fields = annotate_fields
        # self.include_attributes = include_attributes

        self.level = 0
        self.results = []
        self.brief = brief
        self._dumpAstNode(tree,fieldname='root')
        return '\n'.join(self.results)
    #@+node:ekr.20111116103733.10266: *5* _dumpTreeAsString (AstDumper) & helpers
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
    #@+node:ekr.20111116103733.10267: *6* _compress (used only if putting brackets)
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
    #@+node:ekr.20111116103733.10268: *6* _compact
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
    #@+node:ekr.20111116103733.10269: *6* _skip_block
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
    #@+node:ekr.20111116103733.10270: *6* _indent
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
    #@+node:ekr.20111116103733.10271: *6* _remove_cruft
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
        
    #@+node:ekr.20111116103733.10272: *6* _stripBody
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
    #@+node:ekr.20111116103733.10273: *5* _put & _putList
    def _put(self,s,tag=''):

        ws = ' '*self.level
        if tag: tag = '%s:' % tag
        self.results.append('%s%s%s' % (ws,tag,s))

    def _putList(self,aList,tag=''):

        for z in aList:
            self._put(z,tag)
    #@+node:ekr.20111116103733.10274: *5* _skipString
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
    #@+node:ekr.20111116103733.10275: *5* _writeAndClose
    def _writeAndClose (self,s,outStream=None):
        
        s = g.toUnicode(s)

        if outStream:
            g.es_print('writing',outStream.name)
            outStream.write(s)
            outStream.close()
        else:
            print(s)
    #@+node:ekr.20111116103733.10276: *5* error
    def error (self,s):

        g.es_print(s,color='red')
    #@+node:ekr.20111116103733.10277: *5* read_input_file
    def read_input_file (self,fn):

        if g.os_path_exists(fn):
            try:
                return open(fn,'r').read()
            except IOError:
                pass

        self.error('can not open %s' % fn)
        return ''
    #@-others
#@+node:ekr.20111116103733.10345: *3* class InspectTraverser (AstTraverser)
class InspectTraverser (AstTraverser):

    '''A class to create inpect semantic data structures.'''

    #@+others
    #@+node:ekr.20111116103733.10346: *4*  LLT.ctor
    def __init__(self,c,fn,sd,s):

        # Init the base class.
        AstTraverser.__init__(self,fn,s)
        
        # Ivars...
        self.c = c
        self.dumper = sd.dumper
        self.fn = fn
        self.sd = sd

        # Compute the object-info for AttributeError (chain) checks.
        self.objectDict = {}
        self.defineObjectDict()
    #@+node:ekr.20111116103733.10347: *5* defineObjectDict
    def defineObjectDict (self,table=None):

        trace = False ; verbose = False
        c = self.c ; k = c.k ; p = c.p

        if table is None: table = [
            # Python globals...
            (['aList','bList'],     'python','list'),
            (['cc'],                'object',c.chapterController),
            (['c','old_c','new_c'], 'object',c),            
            (['d','d1','d2'],       'python','dict'),
            # (['f'],                 'object',c.frame), 
            (['g'],                 'object',g),       
            (['gui'],               'object',g.app.gui),
            (['k'],                 'object',k),
            (['p','p1','p2'],       'object',p.copy()),
            (['s','s1','s2','ch'],  'object','aString'),
            (['string'],            'object',string), # Python's string module. 
            (['v','v1','v2'],       'object',p.v),
            (['w'],                 'object',c.frame.body.bodyCtrl), # Dubious
        ]

        d = {'dict':{},'int':1,'list':[],'string':''}

        for idList,kind,nameOrObject in table:
            if kind == 'object':
                # Works, but hard to generalize for settings.
                obj = nameOrObject
            elif kind == 'python':
                className = nameOrObject
                o = d.get(className)
                obj = o is not None and o.__class__
            else:
                module = g.importModule (kind,verbose=True)
                if not module:
                    g.trace('Can not import ',nameOrObject)
                    continue
                self.appendToKnownObjects(module)
                if nameOrObject:
                    className = nameOrObject
                    obj = hasattr(module,className) and getattr(module,className) or None
                    if not obj:
                        g.trace('%s module has no class %s' % (kind,nameOrObject))
                    else:
                        self.appendToKnownObjects(getattr(module,className))
                else:
                    obj = module
            for z in idList:
                if trace and verbose: g.trace(z,obj)
                if obj:
                    self.objectDict[z]=obj
                    
        if trace:
            keys = list(self.objectDict.keys())
            keys.sort()
            g.trace(keys)
    #@+node:ekr.20111116103733.10349: *4*  LLT.dump
    def dump (self,tree):
        
        self.dumper.dumpTreeAsString(tree,brief=False,outStream=None)
    #@+node:ekr.20111116103733.10350: *4*  LLT.error
    def error (self,tree,message):
        
        g.pr('Error: %s' % (message))
        
        if isinstance(tree,ast.AST) and hasattr(tree,'lineno'):
            line = self.lines[tree.lineno-1]
            g.pr('line %4s: %s' % (tree.lineno,line.rstrip()))
            
        self.sd.n_errors += 1
    #@+node:ekr.20111116103733.10351: *4* LLT.checks
    #@+node:ekr.20111116103733.10352: *5* LLT.traverse
    def traverse (self,s):
        
        '''Perform all checks on the source in s.'''
        
        # This is akin to LintController.main.
        sd = self.sd
        t1 = time.clock()
        tree = ast.parse(s,filename=self.fn,mode='exec')
        t2 = time.clock()
        sd.parse_time += t2-t1
        self.visit(tree,tag='top')
        t3 = time.clock()
        sd.pass1_time += t3-t2
        # self.resolve_names()
        t4 = time.clock()
        sd.pass2_time += t4-t3

    #@+node:ekr.20111116103733.10354: *4* LLT.Contexts
    #@+node:ekr.20111116103733.10355: *5* LLT.ClassDef
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
        old_cx.classes.append(new_cx)
        
        self.push_context(new_cx)

        self.visit(tree.name,'class name')

        for z in tree.body:
            self.visit(z,'body')
       
        self.pop_context()
            
        self.sd.n_classes += 1
    #@+node:ekr.20111116103733.10356: *5* LLT.FunctionDef
    # FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list)

    def do_FunctionDef (self,tree,tag=''):
        
        # g.trace(self.dump(tree))
        
        # Switch to the new context.
        old_cx = self.get_context()
        new_cx = DefContext(tree,old_cx,self.sd)
        
        
        # Define the function/method name in the old context.
        e = old_cx.st.add_name(tree.name,tree)
        e.set_defined()
        old_cx.functions.append(new_cx)
        
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
    #@+node:ekr.20111116103733.10357: *6* def_args_helper
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
    #@+node:ekr.20111116103733.10358: *5* LLT.Module
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
    #@+node:ekr.20111116103733.10359: *5* LLT.With
    def do_With (self,tree,tag=''):

        if hasattr(tree,'context_expression'):
            self.visit(tree.context_expresssion)

        if hasattr(tree,'optional_vars'):
            pass # May be a Name object.
            # for z in tree.optional_vars:
                # self.visit(z,'with vars')

        for z in tree.body:
            self.visit(z,'with body')
    #@+node:ekr.20111116103733.10360: *4* LLT.Expressions...
    #@+node:ekr.20111116103733.10361: *5* LLT.Attribute & attribute_to_string
    def do_Attribute(self,tree,tag=''):

        # Get the chain.
        cx = self.get_context()
        s = self.attribute_to_string(tree)
        
        if s and s[0] in ('"',"'"):
            # g.trace('ignoring string',s)
            return
        
        # is_method = cx.kind != 'class' and cx.class_context
        # is_ivar = s.startswith('self.')
        # if is_method and is_ivar:
            # cx = cx.class_context

        chain = cx.st.add_chain(tree,s)
            # Create a new Chain object, or merge with an existing chain.

        # Update stats.
        self.sd.n_attributes += 1
    #@+node:ekr.20111116103733.10362: *6* attribute_to_string
    def attribute_to_string (self,tree,level=0):
        
        '''Convert an Attributes nodes and its descendants to a string a.b.c.d...'''

        trace = False ; verbose = True
        if trace and verbose:
            g.trace('level: %s, tree: %s' % (level,tree))
            self.dump(tree)

        kind = self.kind(tree)
        
        if kind == 'Attribute':
            chain = self.attribute_helper(tree,level)
        else:
            chain = self.general_helper(tree,level)

        if trace and level == 0:
            g.trace('level: %s kind: %9s chain: %s' % (
                level,kind,chain))

        return chain
    #@+node:ekr.20111116103733.10363: *7* attribute_helper
    def attribute_helper(self,tree,level):
        
        kind = self.kind(tree)
        assert kind == 'Attribute',kind

        val_kind = self.kind(tree.value)
        assert self.kind(tree.ctx) in ('Del','Load','Store')
        
        # g.trace(val_kind)
        
        if val_kind == 'Attribute':
            s = self.attribute_to_string(tree.value,level+1)
            chain = '%s.%s' % (s,tree.attr)
        elif val_kind == 'Name':
            chain = '%s.%s' % (tree.value.id,tree.attr)
        elif val_kind == 'Call':
            s = self.attribute_to_string(tree.value.func,level+1)
            chain = '%s().%s' % (s,tree.attr)
        elif val_kind == 'Subscript':
            s = self.attribute_to_string(tree.value,level+1)
            chain = '%s[0].%s' % (s,tree.attr)
        elif val_kind == 'Str':
            chain = '%s.%s' % (repr(tree.value.s),tree.attr)
        elif val_kind == 'Dict':
            chain = '%s.%s' % (repr(tree.value),tree.attr)
        else:
            chain = '<Error: val_kind=%s>' % val_kind
            
        return chain
    #@+node:ekr.20111116103733.10364: *7* general_helper
    def general_helper(self,tree,level):

        kind = self.kind(tree)
        if kind == 'Call':
            s = self.attribute_to_string(tree.func,level+1)
            ### chain = '%s()' % (s) # The "Great hack"
            chain = s
        elif kind == 'Name':
            chain = tree.id
        elif kind == 'Str':
            chain = '%s.%s' % (repr(tree.value.s),tree.attr)
        elif kind == 'Subscript':
            s = self.attribute_to_string(tree.value,level+1)
            ### chain = '%s[]' % (s) # The "Great hack"
            chain = s
        else:
            chain = '<Error: kind=%s>' % kind
            g.trace('Can not happen: kind:',kind)
        
        return chain
    #@+node:ekr.20111116103733.10365: *5* LLT.Call
    def do_Call(self,tree,tag=''):
        
        '''The only checks we may want to make are for undefined symbols.
        The Python compiler will raise SyntaxErrors for other problems.'''
        
        self.sd.n_calls += 1
        
        self.visit(tree.func,'call func')
        
        for z in tree.args:
            self.visit(z,'call args')

        for z in tree.keywords:
            self.visit(z,'call keyword args')

        if hasattr(tree,'starargs') and tree.starargs:
            self.visit(tree.starargs,'*arg')

        if hasattr(tree,'kwargs') and tree.kwargs:
            self.visit(tree.kwargs,'call *args')
    #@+node:ekr.20111116103733.10366: *5* LLT.Name
    def do_Name(self,tree,tag=''):

        trace = True
        name = tree.id
        
        if g.isPython3:
            if name in self.sd.module_names:
                return
        else:
            if name in dir(__builtin__) or name in self.sd.module_names:
                return
            
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
    #@+node:ekr.20111116103733.10367: *5* LLT.ListComp & Comprehension
    def do_ListComp(self,tree,tag=''):
        
        # Define a context for the list comprehension variable.
        old_cx = self.get_context()
        new_cx = ComprehensionContext(tree,old_cx,self.sd)
        old_cx.temp_contexts.append(new_cx)

        # Traverse the tree in the new context.
        self.push_context(new_cx)
        self.in_comprehension = True
        self.visit(tree.elt,'list comp elt')
        self.in_comprehension = False
        for z in tree.generators:
            self.visit(z,'list comp generator')
        self.pop_context()
        self.sd.n_list_comps += 1

    def do_comprehension(self,tree,tag=''):

        self.visit(tree.target,'comprehension target (a Name)')
        self.visit(tree.iter,'comprehension iter (an Attribute)')
        for z in tree.ifs:
            self.visit(z,'comprehension if')
    #@+node:ekr.20111116103733.10368: *4* LLT.Statements...
    #@+node:ekr.20111116103733.10369: *5* LLT.Assign
    def do_Assign(self,tree,tag=''):

        self.visit(tree.value,'assn value')
            
        for z in tree.targets:
            
            self.visit(z,'assn target')

            self.sd.n_assignments += 1
    #@+node:ekr.20111116103733.10370: *5* LLT.AugAssign
    def do_AugAssign(self,tree,tag=''):

        self.visit(tree.op)
        
        # Handle the RHS.
        self.visit(tree.value,'aug-assn value')

        # Handle the LHS.
        self.visit(tree.target,'aut-assn target')

        self.sd.n_assignments += 1
    #@+node:ekr.20111116103733.10371: *5* LLT.For
    def do_For (self,tree,tag=''):
        
        # Define a namespace for the 'for' target.
        old_cx = self.get_context()
        new_cx = ForContext(tree,old_cx,self.sd)
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
    #@+node:ekr.20111116103733.10372: *5* LLT.Global
    def do_Global(self,tree,tag=''):

        '''Enter the names in a 'global' statement into the *module* symbol table.'''

        cx = self.get_context()

        for name in tree.names:
            
            # Add the name to the global_names set in *this* context.
            cx.global_names.add(name)
                
            # Create a symbol table entry for the name in the *module* context.
            cx.module_context.st.add_name(name,tree)

            self.sd.n_globals += 1
    #@+node:ekr.20111116103733.10373: *5* LLT.Import & helpers
    def do_Import(self,tree,tag=''):

        '''Add the imported file to the sd.files_list if needed
        and create a context for the file.'''

        trace = False
        sd = self.sd
        cx = self.get_context()
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
    #@+node:ekr.20111116103733.10374: *6* LLT.get_import_names
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
    #@+node:ekr.20111116103733.10375: *6* LLT.resolve_import_name
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
    #@+node:ekr.20111116103733.10376: *5* LLT.ImportFrom
    def do_ImportFrom(self,tree,tag=''):

        '''Add the imported file to the sd.files_list if needed
        and add the imported symbols to the *present* context.'''

        trace = False ; dump = False
        if trace and dump:
            self.dump(tree)
            
        cx = self.get_context()
        sd = self.sd
        
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
    #@+node:ekr.20111116103733.10377: *5* LLT.Lambda & helper
    def do_Lambda (self,tree,tag=''):
        
        # Define a namespace for the 'lambda' variables.
        old_cx = self.get_context()
        new_cx = LambdaContext(tree,old_cx,self.sd)
        old_cx.temp_contexts.append(new_cx)
        
        self.push_context(new_cx)

        # Enter the target names in the 'lambda' context.
        self.def_lambda_args_helper(new_cx,tree.args)

        # Enter all other definitions in the defining_context.
        self.visit(tree.body,'lambda body')

        self.pop_context()
        
        self.sd.n_lambdas += 1

    #@+node:ekr.20111116103733.10378: *6* def_lambda_args_helper
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
    #@+node:ekr.20111116103733.10379: *5* LLT.With
    def do_With (self,tree,tag=''):
        
        # Define a namespace for the 'with' statement.
        old_cx = self.get_context()
        new_cx = WithContext(tree,old_cx,self.sd)
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
    #@-others
#@+node:ekr.20111116103733.10187: *3* class StatisticsTraverser (AstTraverser)
class StatisticsTraverser (AstTraverser):
    
    '''A class to print statistics.'''

    def __init__(self,fn,s):
        AstTraverser.__init__(self,fn,s)
            # sets self.fn, self.s
        self.stats = {}

    #@+others
    #@+node:ekr.20111116103733.10188: *4* visit
    def visit (self,ast,tag=None):

        '''Visit the ast tree node, dispatched by node type.'''

        kind = self.kind(ast)

        self.stats[kind] = 1 + self.stats.get(kind,0)

        AstTraverser.visit(self,self.fn,self.s)
    #@+node:ekr.20111116103733.10189: *4* print_stats
    def print_stats (self):

        d = self.stats
        keys = list(d.keys())
        keys.sort()
        for key in keys:
            print('%5s %s' % (key,d.get(key)))
    #@-others
#@-others
#@+node:ekr.20111116103733.10401: **  Context classes
#@+<< define class Context >>
#@+node:ekr.20111116103733.10402: *3* << define class Context >>
class Context:

    '''The base class of all context-related semantic data.

    All types ultimately resolve to a context.'''

    def __repr__ (self):
        return 'Context: %s' % (self.kind)

    __str__ = __repr__

    #@+others
    #@+node:ekr.20111116103733.10403: *4* cx ctor
    def __init__(self,tree,parent_context,sd,kind):

        self.tree = tree
        self.is_temp_context = kind in ['comprehension','for','lambda','with']
        self.kind = kind
        assert kind in ('class','comprehension','def','for','lambda','module','with'),kind
        self.parent_context = parent_context
        self.sd = sd
        self.st = SymbolTable(context=self)
        
        sd.n_contexts += 1

        # Semantic data...
        self.classes = [] # Classes defined in this context.
        self.functions = [] # Functions defined in this context.
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
        if self.kind == 'module':
            self.class_context = None
        elif self.kind == 'class':
            self.class_context = self
        else:
            self.class_context = parent_context.class_context
            
        # Compute the defining context.
        if self.is_temp_context:
            self.defining_context = parent_context.defining_context
        else:
            self.defining_context = self
        
        # Compute the module context.
        if self.kind == 'module':
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
    #@+node:ekr.20111116103733.10406: *4* cx.destroy_self
    def destroy_self (self):
        
        cx = self
        
        if cx.kind == 'module':
            
            # Clear the symbol table and all lists and sets.
            self.st = SymbolTable(context=self)
            aSet = set()
            for z in dir(self):
                obj = getattr(self,z)
                if type(obj) == type([]):
                    setattr(self,z,[])
                elif type(obj) == type(aSet):
                    setattr(self,z,aSet)
        else:
            # Destroy the context completely.
            g.clearAllIvars(cx)
    #@+node:ekr.20111116103733.10407: *4* cx.dump
    def dump (self,level=0,verbose=False):

        if 0: # Just print the context
            print(repr(self))
        else:
            self.st.dump(level=level)

        if verbose:
            for z in self.classes:
                z.dump(level+1)
            for z in self.functions:
                z.dump(level+1)
            for z in self.temp_contexts:
                z.dump(level+1)
    #@+node:ekr.20111116103733.10409: *4* cx.report_errors & helpers
    def report_errors(self,controller):

        cx = self
        
        # Create the list of context to search, starting with cx.
        table = [cx]
        if cx.defining_context != cx:
            table.append(cx.defining_context)

        # Check only the names in the *current* context; not thos in the defining context.
        keys = list(cx.st.d.keys())
        keys = list(set(keys).union(set(cx.all_global_names)))
        keys.sort()
        
        cx.check_names(controller,keys,table)
                    
        self.check_chains(controller,keys,table)
    #@+node:ekr.20111116103733.10410: *5* cx.check_chains
    def check_chains (self,controller,keys,table):

        check_message = False
        trace = False ; verbose = False
        for key in keys:
            for cx in table:
                e = cx.st.d.get(key)
                if e and e.defined:
                    if trace and verbose: g.trace(e,cx)
                    d = e.chains
                    if d:
                        for key in list(d.keys()):
                            d2 = d.get(key)
                            for chain in list(d2.keys()):
                                aList = chain.split('.')
                                if aList and aList[0] in ('c','g','p'):
                                    attr_s = cx.check_chain(cx,chain)
                                    if attr_s and check_message:
                                        theChain = d2.get(chain)
                                        message = 'AttributeError: %s in %s (%s)' % (attr_s,chain,cx)
                                        controller.error(theChain.tree,message)
                    # Make one check for each key.
                    break
    #@+node:ekr.20111116103733.10411: *5* cx.check_chain
    def check_chain (self,cx,s):
        
        '''Use Leo-specific type knowledge to check for attribute errors.'''
        
        try:
            eval(s)
            return ''
        except AttributeError:
            aList = s.split('.')
            for i in range(len(aList)):
                s2 = '.'.join(aList[0:i+1])
                try:
                    eval(s2)
                except AttributeError:
                    # g.trace(s)
                    return aList[i]
            return s
        except SyntaxError:
            # This can happen because of the 'excellent hack'
            # For example: p.h[].strip()
            return ''
        except IndexError:
            return ''
        except TypeError:
            return ''
        except Exception:
            g.es_exception()
            return ''
    #@+node:ekr.20111116103733.10412: *5* cx.check_names
    def check_names (self,controller,keys,table):

        check_message = False
        trace = False ; verbose = True
        cx = self # The original context.

        if trace and verbose:
            g.trace('***** Checking',keys,'in',cx)

        for key in keys:
            found,unbound,tag = False,False,''
            for cx2 in table:
                if found: break
                # g.trace(key,'** all_global_names',cx2.all_global_names,cx2)
                e = cx2.st.d.get(key)
                if e:
                    assert e.name == key
                elif key in cx2.all_global_names:
                    tag = 'global'
                    found = True ; break
                else:
                    continue
                
                if key in cx2.param_names:
                    tag = 'param'
                    found = True ; break
                elif key in cx2.all_global_names:
                    tag = 'global'
                    found = True ; break
                elif e.defined:
                    # Only class, def, and import symbols are defined earlier.
                    tag = 'defined'
                    unbound = e.load_before_store_flag
                    found = True ; break
                elif key in cx2.store_names:
                    tag = 'store'
                    unbound = e.load_before_store_flag
                    found = True ; break
                else: pass
                        
            # Actually give the error.
            if found:
                if e: e.defined = True # A signal for check_chains.
                if trace and verbose:
                    g.trace('found %s: %s in %s' % (key,tag,cx2))
            else:
                if check_message:
                    # Report cx, not cx2.
                    if unbound:
                        controller.error(cx.tree,'UnboundLocalError: %s in %s' % (key,cx))
                    else:
                        controller.error(cx.tree,'Undefined: %s in %s' % (key,cx))
    #@-others
#@-<< define class Context >>

#@+others
#@+node:ekr.20111116103733.10413: *3* class ClassContext(Context)
class ClassContext (Context):

    '''A class to hold semantic data about a class.'''

    def __init__(self,tree,parent_context,sd):

        Context.__init__(self,tree,parent_context,sd,'class')

    def __repr__ (self):
        
        return 'class(%s)' % (self.tree.name)
        
    def name (self):
        
        return self.tree.name
    
    __str__ = __repr__
#@+node:ekr.20111116103733.10414: *3* class ConprehensionContext(Context)
class ComprehensionContext (Context):

    '''A class to represent the range of a list comprehension.'''

    def __init__(self,tree,parent_context,sd):

        Context.__init__(self,tree,parent_context,sd,'comprehension')

    def __repr__ (self):

        return 'comprehension'
        
    def name (self):

        return 'list comprehension context'

    __str__ = __repr__
#@+node:ekr.20111116103733.10415: *3* class DefContext(Context)
class DefContext (Context):

    '''A class to hold semantic data about a function/method.'''

    def __init__(self,tree,parent_context,sd):

        Context.__init__(self,tree,parent_context,sd,'def')

    def __repr__ (self):

        return 'def(%s)' % (self.tree.name)
        
    def name (self):
        kind = g.choose(self.class_context,'method','function')
        return '%s %s' % (kind,self.tree.name)
        
    __str__ = __repr__
#@+node:ekr.20111116103733.10416: *3* class ForContext(Context)
class ForContext (Context):

    '''A class to represent the range of a 'for' statement.'''

    def __init__(self,tree,parent_context,sd):

        Context.__init__(self,tree,parent_context,sd,'for')

    def __repr__ (self):
        kind = self.ast_kind(self.tree.target)
        if kind == 'Name':
            return 'for(%s)' % (self.tree.target.id)
        elif kind == 'Tuple':
            return 'for(%s)' % ','.join([z.id for z in self.tree.target.elts])
        else:
            return 'for(%s)' % (kind)
        
    def name (self):
        return '"for" statement context'
        
    __str__ = __repr__
    
#@+at
# def do_Tuple(self,tree,tag=''):
#     self.trace(tree,tag)
#     for z in tree.elts:
#         self.visit(z,'list elts')
#     self.visit(tree.ctx,'list context')
#@+node:ekr.20111116103733.10417: *3* class LambdaContext(Context)
class LambdaContext (Context):

    '''A class to represent the range of a 'lambda' statement.'''

    def __init__(self,tree,parent_context,sd):

        Context.__init__(self,tree,parent_context,sd,'lambda')

    def __repr__ (self):

        return 'lambda context'
        
    def name (self):
        return 'lambda statement context'

    __str__ = __repr__
#@+node:ekr.20111116103733.10418: *3* class ModuleContext(Context)
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
#@+node:ekr.20111116103733.10419: *3* class WithContext(Context)
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
#@+node:ekr.20111116103733.10338: ** class Chain
class Chain:
    
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
#@+node:ekr.20111116103733.10312: ** class LeoCoreFiles
class LeoCoreFiles:
    
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
class SemanticData:
    
    '''A class containing all global semantic data.'''
    
    #@+others
    #@+node:ekr.20111116103733.10381: *3*  sd.ctor
    def __init__ (self,controller):
        
        self.controller = controller
        self.dumper = AstDumper()
        
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
            if cx.classes:
                for z in self.all_contexts(cx.classes):
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
class SymbolTable:

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
class SymbolTableEntry:

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
#@+node:ekr.20111116103733.10450: ** test
def test(c,files,print_stats=True,s=None,print_times=True):
   
    t1 = time.clock()
    sd = SemanticData(controller=None)

    if s: # Use test string.
        fn = '<test file>'
        InspectTraverser(c,fn,sd,s).traverse(s)
    else:
        for fn in files:
            print(g.shortFileName(fn))
            s = LeoCoreFiles().get_source(fn)
            if s:
                InspectTraverser(c,fn,sd,s).traverse(s)
            else:
                print('file not found: %s' % (fn))
           
    sd.total_time = time.clock()-t1
    
    if print_times: sd.print_times()
    if print_stats: sd.print_stats()
#@-others
#@-leo

#@+leo-ver=5-thin
#@+node:ekr.20141012064706.18389: * @file leoAst.py
'''AST (Abstract Syntax Tree) related classes.'''

import leo.core.leoGlobals as g
import ast

#@+others
#@+node:ekr.20141012064706.18390: ** class AstDumper
class AstDumper:
    '''
    Return a formatted dump (a string) of the AST node.

    Adapted from Python's ast.dump.
    
    annotate_fields:    True: show names of fields (can't eval the dump).
    disabled_field:     List of names of fields not to show: e.g. ['ctx',]
    include_attributes: True: show line numbers and column offsets.
    indent:             Number of spaces for each indent.
    '''

    #@+others
    #@+node:ekr.20141012064706.18391: *3* d.ctor
    def __init__(self,u,annotate_fields,disabled_fields,format,include_attributes,indent_ws):
        '''Ctor for AstDumper class.'''
        self.u = u
        self.annotate_fields = annotate_fields
        self.disabled_fields = disabled_fields
        self.format = format
        self.include_attributes = include_attributes
        self.indent_ws = indent_ws
    #@+node:ekr.20141012064706.18392: *3* d.dump
    def dump(self,node,level=0):
        sep1 = '\n%s' % (self.indent_ws*(level+1))
        if isinstance(node,ast.AST):
            fields = [(a,self.dump(b,level+1)) for a,b in self.get_fields(node)]
                # ast.iter_fields(node)]
            if self.include_attributes and node._attributes:
                fields.extend([(a,self.dump(getattr(node,a),level+1))
                    for a in node._attributes])
            # Not used at present.
            # aList = self.extra_attributes(node)
            # if aList: fields.extend(aList)
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
    #@+node:ekr.20141012064706.18393: *3* d.get_fields
    def get_fields (self,node):
        
        fields = [z for z in ast.iter_fields(node)]
        result = []
        for a,b in fields:
            if a not in self.disabled_fields:
                if b not in (None,[]):
                    result.append((a,b),)
        return result
    #@+node:ekr.20141012064706.18394: *3* d.extra_attributes & helpers (not used)
    def extra_attributes (self,node):
        '''Return the tuple (field,repr(field)) for all extra fields.'''
        d = {
            # 'e': self.do_repr,
            # 'cache':self.do_cache_list,
            # 'reach':self.do_reaching_list,
            # 'typ':  self.do_types_list,
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
    #@+node:ekr.20141012064706.18395: *4* d.do_cache_list
    def do_cache_list(self,attr,node,val):
        return self.u.dump_cache(node)

    #@+node:ekr.20141012064706.18396: *4* d.do_reaching_list
    def do_reaching_list(self,attr,node,val):
        assert attr == 'reach'
        return '[%s]' % ','.join(
            [self.format(z).strip() or repr(z)
                for z in getattr(node,attr)])

    #@+node:ekr.20141012064706.18397: *4* d.do_repr
    def do_repr(self,attr,node,val):

        return repr(val)
    #@+node:ekr.20141012064706.18398: *4* d.do_types_list
    def do_types_list(self,attr,node,val):
        assert attr == 'typ'
        return '[%s]' % ','.join(
            [repr(z) for z in getattr(node,attr)])
    #@-others
#@+node:ekr.20141012064706.18399: ** class AstFormatter
class AstFormatter:
    '''
    A class to recreate source code from an AST.
    
    This does not have to be perfect, but it should be close.
    
    Also supports optional annotations such as line numbers, file names, etc.
    '''
    
    # No ctor.

    #@+others
    #@+node:ekr.20141012064706.18400: *3*  f.Entries
    #@+node:ekr.20141012064706.18401: *4* f.__call__ (not used)
    # def __call__(self,node):
        # '''__call__ method for AstFormatter class.'''
        # return self.format(node)
    #@+node:ekr.20141012064706.18402: *4* f.format
    def format (self,node):
        '''Format the node (or list of nodes) and its descendants.'''
        self.level = 0
        val = self.visit(node)
        return val and val.strip() or ''
    #@+node:ekr.20141012064706.18403: *4* f.visit
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
    #@+node:ekr.20141012064706.18404: *3* f.Contexts
    #@+node:ekr.20141012064706.18405: *4* f.ClassDef
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
    #@+node:ekr.20141012064706.18406: *4* f.FunctionDef
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
    #@+node:ekr.20141012064706.18407: *4* f.Interactive
    def do_Interactive(self,node):

        for z in node.body:
            self.visit(z)

    #@+node:ekr.20141012064706.18408: *4* f.Module
    def do_Module (self,node):
        
        assert 'body' in node._fields
        return 'module:\n%s' % (''.join([self.visit(z) for z in  node.body]))
    #@+node:ekr.20141012064706.18409: *4* f.Lambda
    def do_Lambda (self,node):
            
        return self.indent('lambda %s: %s\n' % (
            self.visit(node.args),
            self.visit(node.body)))
    #@+node:ekr.20141012064706.18410: *3* f.Expressions
    #@+node:ekr.20141012064706.18411: *4* f.Expr
    def do_Expr(self,node):
        
        '''An outer expression: must be indented.'''
        
        return self.indent('%s\n' % self.visit(node.value))

    #@+node:ekr.20141012064706.18412: *4* f.Expression
    def do_Expression(self,node):
        
        '''An inner expression: do not indent.'''

        return '%s\n' % self.visit(node.body)
    #@+node:ekr.20141012064706.18413: *4* f.GeneratorExp
    def do_GeneratorExp(self,node):
       
        elt  = self.visit(node.elt) or ''

        gens = [self.visit(z) for z in node.generators]
        gens = [z if z else '<**None**>' for z in gens] ### Kludge: probable bug.
        
        return '<gen %s for %s>' % (elt,','.join(gens))
    #@+node:ekr.20141012064706.18414: *4* f.ctx nodes
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
    #@+node:ekr.20141012064706.18415: *3* f.Operands
    #@+node:ekr.20141012064706.18416: *4* f.arguments
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
    #@+node:ekr.20141012064706.18417: *4* f.arg (Python3 only)
    # Python 3:
    # arg = (identifier arg, expr? annotation)

    def do_arg(self,node):
        if node.annotation:
            return self.visit(node.annotation)
        else:
            return ''
    #@+node:ekr.20141012064706.18418: *4* f.Attribute
    # Attribute(expr value, identifier attr, expr_context ctx)

    def do_Attribute(self,node):

        return '%s.%s' % (
            self.visit(node.value),
            node.attr) # Don't visit node.attr: it is always a string.
    #@+node:ekr.20141012064706.18419: *4* f.Bytes
    def do_Bytes(self,node): # Python 3.x only.
        assert g.isPython3
        return str(node.s)
        
    #@+node:ekr.20141012064706.18420: *4* f.Call & f.keyword
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
    #@+node:ekr.20141012064706.18421: *5* f.keyword
    # keyword = (identifier arg, expr value)

    def do_keyword(self,node):

        # node.arg is a string.
        value = self.visit(node.value)

        # This is a keyword *arg*, not a Python keyword!
        return '%s=%s' % (node.arg,value)
    #@+node:ekr.20141012064706.18422: *4* f.comprehension
    def do_comprehension(self,node):

        result = []
        name = self.visit(node.target) # A name.
        it   = self.visit(node.iter) # An attribute.

        result.append('%s in %s' % (name,it))

        ifs = [self.visit(z) for z in node.ifs]
        if ifs:
            result.append(' if %s' % (''.join(ifs)))
            
        return ''.join(result)
    #@+node:ekr.20141012064706.18423: *4* f.Dict
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
            print('Error: f.Dict: len(keys) != len(values)\nkeys: %s\nvals: %s' % (
                repr(keys),repr(values)))
                
        return ''.join(result)
    #@+node:ekr.20141012064706.18424: *4* f.Ellipsis
    def do_Ellipsis(self,node):
        return '...'

    #@+node:ekr.20141012064706.18425: *4* f.ExtSlice
    def do_ExtSlice (self,node):

        return ':'.join([self.visit(z) for z in node.dims])
    #@+node:ekr.20141012064706.18426: *4* f.Index
    def do_Index (self,node):
        
        return self.visit(node.value)
    #@+node:ekr.20141012064706.18427: *4* f.List
    def do_List(self,node):

        # Not used: list context.
        # self.visit(node.ctx)
        
        elts = [self.visit(z) for z in node.elts]
        elst = [z for z in elts if z] # Defensive.
        return '[%s]' % ','.join(elts)
    #@+node:ekr.20141012064706.18428: *4* f.ListComp
    def do_ListComp(self,node):

        elt = self.visit(node.elt)

        gens = [self.visit(z) for z in node.generators]
        gens = [z if z else '<**None**>' for z in gens] ### Kludge: probable bug.

        return '%s for %s' % (elt,''.join(gens))
    #@+node:ekr.20141012064706.18429: *4* f.Name
    def do_Name(self,node):

        return node.id
    #@+node:ekr.20141012064706.18430: *4* f.Num
    def do_Num(self,node):
        return repr(node.n)
    #@+node:ekr.20141012064706.18431: *4* f.Repr
    # Python 2.x only
    def do_Repr(self,node):

        return 'repr(%s)' % self.visit(node.value)
    #@+node:ekr.20141012064706.18432: *4* f.Slice
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
    #@+node:ekr.20141012064706.18433: *4* f.Str
    def do_Str (self,node):
        
        '''This represents a string constant.'''
        return repr(node.s)
    #@+node:ekr.20141012064706.18434: *4* f.Subscript
    # Subscript(expr value, slice slice, expr_context ctx)

    def do_Subscript(self,node):
        
        value = self.visit(node.value)

        the_slice = self.visit(node.slice)
        
        return '%s[%s]' % (value,the_slice)
    #@+node:ekr.20141012064706.18435: *4* f.Tuple
    def do_Tuple(self,node):
            
        elts = [self.visit(z) for z in node.elts]

        return '(%s)' % ','.join(elts)
    #@+node:ekr.20141012064706.18436: *3* f.Operators
    #@+node:ekr.20141012064706.18437: *4* f.BinOp
    def do_BinOp (self,node):

        return '%s%s%s' % (
            self.visit(node.left),
            self.op_name(node.op),
            self.visit(node.right))
            
    #@+node:ekr.20141012064706.18438: *4* f.BoolOp
    def do_BoolOp (self,node):
        
        op_name = self.op_name(node.op)
        values = [self.visit(z) for z in node.values]
        return op_name.join(values)
        
    #@+node:ekr.20141012064706.18439: *4* f.Compare
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
    #@+node:ekr.20141012064706.18440: *4* f.UnaryOp
    def do_UnaryOp (self,node):
        
        return '%s%s' % (
            self.op_name(node.op),
            self.visit(node.operand))
    #@+node:ekr.20141012064706.18441: *4* f.ifExp (ternary operator)
    def do_IfExp (self,node):

        return '%s if %s else %s ' % (
            self.visit(node.body),
            self.visit(node.test),
            self.visit(node.orelse))
    #@+node:ekr.20141012064706.18442: *3* f.Statements
    #@+node:ekr.20141012064706.18443: *4* f.Assert
    def do_Assert(self,node):
        
        test = self.visit(node.test)

        if getattr(node,'msg',None):
            message = self.visit(node.msg)
            return self.indent('assert %s, %s' % (test,message))
        else:
            return self.indent('assert %s' % test)
    #@+node:ekr.20141012064706.18444: *4* f.Assign
    def do_Assign(self,node):

        return self.indent('%s=%s' % (
            '='.join([self.visit(z) for z in node.targets]),
            self.visit(node.value)))
    #@+node:ekr.20141012064706.18445: *4* f.AugAssign
    def do_AugAssign(self,node):

        return self.indent('%s%s=%s\n' % (
            self.visit(node.target),
            self.op_name(node.op), # Bug fix: 2013/03/08.
            self.visit(node.value)))
    #@+node:ekr.20141012064706.18446: *4* f.Break
    def do_Break(self,node):

        return self.indent('break\n')

    #@+node:ekr.20141012064706.18447: *4* f.Continue
    def do_Continue(self,node):

        return self.indent('continue\n')
    #@+node:ekr.20141012064706.18448: *4* f.Delete
    def do_Delete(self,node):
        
        targets = [self.visit(z) for z in node.targets]

        return self.indent('del %s\n' % ','.join(targets))
    #@+node:ekr.20141012064706.18449: *4* f.ExceptHandler
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
    #@+node:ekr.20141012064706.18450: *4* f.Exec
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
    #@+node:ekr.20141012064706.18451: *4* f.For
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
    #@+node:ekr.20141012064706.18452: *4* f.Global
    def do_Global(self,node):

        return self.indent('global %s\n' % (
            ','.join(node.names)))
    #@+node:ekr.20141012064706.18453: *4* f.If
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
    #@+node:ekr.20141012064706.18454: *4* f.Import & helper
    def do_Import(self,node):
        
        names = []

        for fn,asname in self.get_import_names(node):
            if asname:
                names.append('%s as %s' % (fn,asname))
            else:
                names.append(fn)
        
        return self.indent('import %s\n' % (
            ','.join(names)))
    #@+node:ekr.20141012064706.18455: *5* f.get_import_names
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
    #@+node:ekr.20141012064706.18456: *4* f.ImportFrom
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
    #@+node:ekr.20141012064706.18457: *4* f.Pass
    def do_Pass(self,node):

        return self.indent('pass\n')
    #@+node:ekr.20141012064706.18458: *4* f.Print
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
    #@+node:ekr.20141012064706.18459: *4* f.Raise
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
    #@+node:ekr.20141012064706.18460: *4* f.Return
    def do_Return(self,node):

        if node.value:
            return self.indent('return %s\n' % (
                self.visit(node.value)))
        else:
            return self.indent('return\n')
    #@+node:ekr.20141012064706.18461: *4* f.Suite
    # def do_Suite(self,node):

        # for z in node.body:
            # s = self.visit(z)

    #@+node:ekr.20141012064706.18462: *4* f.TryExcept
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
    #@+node:ekr.20141012064706.18463: *4* f.TryFinally
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
    #@+node:ekr.20141012064706.18464: *4* f.While
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
    #@+node:ekr.20141012064706.18465: *4* f.With
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
    #@+node:ekr.20141012064706.18466: *4* f.Yield
    def do_Yield(self,node):

        if getattr(node,'value',None):
            return self.indent('yield %s\n' % (
                self.visit(node.value)))
        else:
            return self.indent('yield\n')

    #@+node:ekr.20141012064706.18467: *3* f.Utils
    #@+node:ekr.20141012064706.18468: *4* f.kind
    def kind(self,node):
        '''Return the name of node's class.'''
        return node.__class__.__name__
    #@+node:ekr.20141012064706.18469: *4* f.indent
    def indent(self,s):

        return '%s%s' % (' '*4*self.level,s)
    #@+node:ekr.20141012064706.18470: *4* f.op_name
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
#@+node:ekr.20141012064706.18471: ** class AstFullTraverser
class AstFullTraverser:
    '''
    A fast traverser for AST trees: it visits every node (except node.ctx fields).

    Sets .context and .parent ivars before visiting each node.
    '''
    
    def __init__(self):
        '''Ctor for AstFullTraverser class.'''
        self.context = None
        self.parent = None

    #@+others
    #@+node:ekr.20141012064706.18472: *3* ft.contexts
    #@+node:ekr.20141012064706.18473: *4* ft.ClassDef
    # ClassDef(identifier name, expr* bases, stmt* body, expr* decorator_list)

    def do_ClassDef (self,node):

        old_context = self.context
        self.context = node
        for z in node.bases:
            self.visit(z)
        for z in node.body:
            self.visit(z)
        for z in node.decorator_list:
            self.visit(z)
        self.context = old_context
    #@+node:ekr.20141012064706.18474: *4* ft.FunctionDef
    # FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list)

    def do_FunctionDef (self,node):
        
        old_context = self.context
        self.context = node
        self.visit(node.args)
        for z in node.body:
            self.visit(z)
        for z in node.decorator_list:
            self.visit(z)
        self.context = old_context
    #@+node:ekr.20141012064706.18475: *4* ft.Interactive
    def do_Interactive(self,node):
        
        assert False,'Interactive context not supported'
    #@+node:ekr.20141012064706.18476: *4* ft.Lambda
    # Lambda(arguments args, expr body)

    def do_Lambda(self,node):
        
        old_context = self.context
        self.context = node
        self.visit(node.args)
        self.visit(node.body)
        self.context = old_context
    #@+node:ekr.20141012064706.18477: *4* ft.Module
    def do_Module (self,node):

        self.context = node
        for z in node.body:
            self.visit(z)
        self.context = None
    #@+node:ekr.20141012064706.18478: *3* ft.ctx nodes
    # Not used in this class, but may be called by subclasses.

    def do_AugLoad(self,node):
        pass

    def do_Del(self,node):
        pass

    def do_Load(self,node):
        pass

    def do_Param(self,node):
        pass

    def do_Store(self,node):
        pass
    #@+node:ekr.20141012064706.18479: *3* ft.kind
    def kind(self,node):
        
        return node.__class__.__name__
    #@+node:ekr.20141012064706.18480: *3* ft.operators
    #@+node:ekr.20141012064706.18481: *4* ft do-nothings
    def do_Bytes(self,node): 
        pass # Python 3.x only.
        
    def do_Ellipsis(self,node):
        pass
        
    def do_Num(self,node):
        pass # Num(object n) # a number as a PyObject.
        
    def do_Str (self,node):
        pass # represents a string constant.
    #@+node:ekr.20141012064706.18482: *4* ft.arguments & arg
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
    #@+node:ekr.20141012064706.18483: *4* ft.Attribute
    # Attribute(expr value, identifier attr, expr_context ctx)

    def do_Attribute(self,node):
        
        self.visit(node.value)
        # self.visit(node.ctx)
    #@+node:ekr.20141012064706.18484: *4* ft.BinOp
    # BinOp(expr left, operator op, expr right)

    def do_BinOp (self,node):

        self.visit(node.left)
        # self.op_name(node.op)
        self.visit(node.right)
    #@+node:ekr.20141012064706.18485: *4* ft.BoolOp
    # BoolOp(boolop op, expr* values)

    def do_BoolOp (self,node):
        
        for z in node.values:
            self.visit(z)
    #@+node:ekr.20141012064706.18486: *4* ft.Call
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
    #@+node:ekr.20141012064706.18487: *4* ft.Compare
    # Compare(expr left, cmpop* ops, expr* comparators)

    def do_Compare(self,node):
        
        self.visit(node.left)
        for z in node.comparators:
            self.visit(z)
    #@+node:ekr.20141012064706.18488: *4* ft.comprehension
    # comprehension (expr target, expr iter, expr* ifs)

    def do_comprehension(self,node):

        self.visit(node.target) # A name.
        self.visit(node.iter) # An attribute.
        for z in node.ifs:
            self.visit(z)
    #@+node:ekr.20141012064706.18489: *4* ft.Dict
    # Dict(expr* keys, expr* values)

    def do_Dict(self,node):
        
        for z in node.keys:
            self.visit(z)
        for z in node.values:
            self.visit(z)
    #@+node:ekr.20141012064706.18490: *4* ft.Expr
    # Expr(expr value)

    def do_Expr(self,node):
        
        self.visit(node.value)
    #@+node:ekr.20141012064706.18491: *4* ft.Expression
    def do_Expression(self,node):
        
        '''An inner expression'''

        self.visit(node.body)
    #@+node:ekr.20141012064706.18492: *4* ft.ExtSlice
    def do_ExtSlice (self,node):
        
        for z in node.dims:
            self.visit(z)
    #@+node:ekr.20141012064706.18493: *4* ft.GeneratorExp
    # GeneratorExp(expr elt, comprehension* generators)

    def do_GeneratorExp(self,node):
        
        self.visit(node.elt)
        for z in node.generators:
            self.visit(z)
    #@+node:ekr.20141012064706.18494: *4* ft.ifExp (ternary operator)
    # IfExp(expr test, expr body, expr orelse)

    def do_IfExp (self,node):

        self.visit(node.body)
        self.visit(node.test)
        self.visit(node.orelse)
    #@+node:ekr.20141012064706.18495: *4* ft.Index
    def do_Index (self,node):
        
        self.visit(node.value)
    #@+node:ekr.20141012064706.18496: *4* ft.keyword
    # keyword = (identifier arg, expr value)

    def do_keyword(self,node):

        # node.arg is a string.
        self.visit(node.value)
    #@+node:ekr.20141012064706.18497: *4* ft.List & ListComp
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
    #@+node:ekr.20141012064706.18498: *4* ft.Name (revise)
    # Name(identifier id, expr_context ctx)

    def do_Name(self,node):

        # self.visit(node.ctx)
        pass
    #@+node:ekr.20141012064706.18499: *4* ft.Repr
    # Python 2.x only
    # Repr(expr value)

    def do_Repr(self,node):

        self.visit(node.value)
    #@+node:ekr.20141012064706.18500: *4* ft.Slice
    def do_Slice (self,node):

        if getattr(node,'lower',None):
            self.visit(node.lower)
        if getattr(node,'upper',None):
            self.visit(node.upper)
        if getattr(node,'step',None):
            self.visit(node.step)
    #@+node:ekr.20141012064706.18501: *4* ft.Subscript
    # Subscript(expr value, slice slice, expr_context ctx)

    def do_Subscript(self,node):
        
        self.visit(node.value)
        self.visit(node.slice)
        # self.visit(node.ctx)
    #@+node:ekr.20141012064706.18502: *4* ft.Tuple
    # Tuple(expr* elts, expr_context ctx)

    def do_Tuple(self,node):
        
        for z in node.elts:
            self.visit(z)
        # self.visit(node.ctx)
    #@+node:ekr.20141012064706.18503: *4* ft.UnaryOp
    # UnaryOp(unaryop op, expr operand)

    def do_UnaryOp (self,node):
        
        # self.op_name(node.op)
        self.visit(node.operand)
    #@+node:ekr.20141012064706.18504: *3* ft.statements
    #@+node:ekr.20141012064706.18505: *4* ft.alias
    # identifier name, identifier? asname)

    def do_alias (self,node):
        
        # self.visit(node.name)
        # if getattr(node,'asname')
            # self.visit(node.asname)
        pass
    #@+node:ekr.20141012064706.18506: *4* ft.Assert
    # Assert(expr test, expr? msg)

    def do_Assert(self,node):

        self.visit(node.test)
        if node.msg:
            self.visit(node.msg)
    #@+node:ekr.20141012064706.18507: *4* ft.Assign
    # Assign(expr* targets, expr value)

    def do_Assign(self,node):

        for z in node.targets:
            self.visit(z)
        self.visit(node.value)
    #@+node:ekr.20141012064706.18508: *4* ft.AugAssign
    # AugAssign(expr target, operator op, expr value)

    def do_AugAssign(self,node):
        
        # g.trace('FT',Utils().format(node),g.callers())
        self.visit(node.target)
        self.visit(node.value)
    #@+node:ekr.20141012064706.18509: *4* ft.Break
    def do_Break(self,tree):
        pass

    #@+node:ekr.20141012064706.18510: *4* ft.Continue
    def do_Continue(self,tree):
        pass

    #@+node:ekr.20141012064706.18511: *4* ft.Delete
    # Delete(expr* targets)

    def do_Delete(self,node):

        for z in node.targets:
            self.visit(z)
    #@+node:ekr.20141012064706.18512: *4* ft.ExceptHandler
    # Python 2: ExceptHandler(expr? type, expr? name, stmt* body)
    # Python 3: ExceptHandler(expr? type, identifier? name, stmt* body)

    def do_ExceptHandler(self,node):
        
        if node.type:
            self.visit(node.type)
        if node.name and isinstance(node.name,ast.Name):
            self.visit(node.name)
        for z in node.body:
            self.visit(z)
    #@+node:ekr.20141012064706.18513: *4* ft.Exec
    # Python 2.x only
    # Exec(expr body, expr? globals, expr? locals)

    def do_Exec(self,node):

        self.visit(node.body)
        if getattr(node,'globals',None):
            self.visit(node.globals)
        if getattr(node,'locals',None):
            self.visit(node.locals)
    #@+node:ekr.20141012064706.18514: *4* ft.For
    # For(expr target, expr iter, stmt* body, stmt* orelse)

    def do_For (self,node):

        self.visit(node.target)
        self.visit(node.iter)
        for z in node.body:
            self.visit(z)
        for z in node.orelse:
            self.visit(z)

    #@+node:ekr.20141012064706.18515: *4* ft.Global
    # Global(identifier* names)

    def do_Global(self,node):
        pass
    #@+node:ekr.20141012064706.18516: *4* ft.If
    # If(expr test, stmt* body, stmt* orelse)

    def do_If(self,node):
        
        self.visit(node.test)
        for z in node.body:
            self.visit(z)
        for z in node.orelse:
            self.visit(z)
    #@+node:ekr.20141012064706.18517: *4* ft.Import & ImportFrom
    # Import(alias* names)

    def do_Import(self,node):
        pass

    # ImportFrom(identifier? module, alias* names, int? level)

    def do_ImportFrom(self,node):
        
        # for z in node.names:
            # self.visit(z)
        pass
    #@+node:ekr.20141012064706.18518: *4* ft.Pass
    def do_Pass(self,node):

        pass

    #@+node:ekr.20141012064706.18519: *4* ft.Print
    # Python 2.x only
    # Print(expr? dest, expr* values, bool nl)
    def do_Print(self,node):

        if getattr(node,'dest',None):
            self.visit(node.dest)
        for expr in node.values:
            self.visit(expr)
    #@+node:ekr.20141012064706.18520: *4* ft.Raise
    # Raise(expr? type, expr? inst, expr? tback)

    def do_Raise(self,node):
        
        if getattr(node,'type',None):
            self.visit(node.type)
        if getattr(node,'inst',None):
            self.visit(node.inst)
        if getattr(node,'tback',None):
            self.visit(node.tback)
    #@+node:ekr.20141012064706.18521: *4* ft.Return
    # Return(expr? value)

    def do_Return(self,node):
        
        if node.value:
            self.visit(node.value)
    #@+node:ekr.20141012064706.18522: *4* ft.Try (Python 3 only)
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
    #@+node:ekr.20141012064706.18523: *4* ft.TryExcept
    # TryExcept(stmt* body, excepthandler* handlers, stmt* orelse)

    def do_TryExcept(self,node):
        
        for z in node.body:
            self.visit(z)
        for z in node.handlers:
            self.visit(z)
        for z in node.orelse:
            self.visit(z)
    #@+node:ekr.20141012064706.18524: *4* ft.TryFinally
    # TryFinally(stmt* body, stmt* finalbody)

    def do_TryFinally(self,node):

        for z in node.body:
            self.visit(z)
        for z in node.finalbody:
            self.visit(z)
    #@+node:ekr.20141012064706.18525: *4* ft.While
    # While(expr test, stmt* body, stmt* orelse)

    def do_While (self,node):

        self.visit(node.test) # Bug fix: 2013/03/23.
        for z in node.body:
            self.visit(z)
        for z in node.orelse:
            self.visit(z)
    #@+node:ekr.20141012064706.18526: *4* ft.With
    # With(expr context_expr, expr? optional_vars, stmt* body)

    def do_With (self,node):
        
        self.visit(node.context_expr)
        if node.optional_vars:
            self.visit(node.optional_vars)
        for z in node.body:
            self.visit(z)
        
    #@+node:ekr.20141012064706.18527: *4* ft.Yield
    #  Yield(expr? value)

    def do_Yield(self,node):

        if node.value:
            self.visit(node.value)
    #@+node:ekr.20141012064706.18528: *3* ft.visit
    def visit(self,node):
        '''Visit a *single* ast node.  Visitors are responsible for visiting children!'''
        assert isinstance(node,ast.AST),node.__class__.__name__
        # Visit the children with the new parent.
        old_parent = self.parent
        parent = node
        method_name = 'do_' + node.__class__.__name__
        method = getattr(self,method_name)
        val = method(node)
        self.parent = old_parent
        return val

    def visit_children(self,node):
        assert False,'must visit children explicitly'
    #@+node:ekr.20141012064706.18529: *3* ft.visit_list
    def visit_list (self,aList):
        '''Visit all ast nodes in aList.'''
        assert isinstance(aList,(list,tuple)),repr(aList)
        for z in aList:
            self.visit(z)
        return None
    #@-others
#@+node:ekr.20141012064706.18530: ** class AstPatternFormatter
class AstPatternFormatter (AstFormatter):
    '''
    A subclass of AstFormatter that replaces values of constants by Bool,
    Bytes, Int, Name, Num or Str.
    '''

    # No ctor.

    #@+others
    #@+node:ekr.20141012064706.18531: *3* Constants & Name
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
#@-others
#@@language python
#@@tabwidth -4
#@-leo

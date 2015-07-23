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
    def __init__(self, u, annotate_fields, disabled_fields, format, include_attributes, indent_ws):
        '''Ctor for AstDumper class.'''
        self.u = u
        self.annotate_fields = annotate_fields
        self.disabled_fields = disabled_fields
        self.format = format
        self.include_attributes = include_attributes
        self.indent_ws = indent_ws
    #@+node:ekr.20141012064706.18392: *3* d.dump
    def dump(self, node, level=0):
        sep1 = '\n%s' % (self.indent_ws * (level + 1))
        if isinstance(node, ast.AST):
            fields = [(a, self.dump(b, level + 1)) for a, b in self.get_fields(node)]
                # ast.iter_fields(node)]
            if self.include_attributes and node._attributes:
                fields.extend([(a, self.dump(getattr(node, a), level + 1))
                    for a in node._attributes])
            # Not used at present.
            # aList = self.extra_attributes(node)
            # if aList: fields.extend(aList)
            if self.annotate_fields:
                aList = ['%s=%s' % (a, b) for a, b in fields]
            else:
                aList = [b for a, b in fields]
            compressed = not any([isinstance(b, list) and len(b) > 1 for a, b in fields])
            name = node.__class__.__name__
            if compressed and len(','.join(aList)) < 100:
                return '%s(%s)' % (name, ','.join(aList))
            else:
                sep = '' if len(aList) <= 1 else sep1
                return '%s(%s%s)' % (name, sep, sep1.join(aList))
        elif isinstance(node, list):
            compressed = not any([isinstance(z, list) and len(z) > 1 for z in node])
            sep = '' if compressed and len(node) <= 1 else sep1
            return '[%s]' % ''.join(
                ['%s%s' % (sep, self.dump(z, level + 1)) for z in node])
        else:
            return repr(node)
    #@+node:ekr.20141012064706.18393: *3* d.get_fields
    def get_fields(self, node):
        fields = [z for z in ast.iter_fields(node)]
        result = []
        for a, b in fields:
            if a not in self.disabled_fields:
                if b not in (None, []):
                    result.append((a, b),)
        return result
    #@+node:ekr.20141012064706.18394: *3* d.extra_attributes & helpers (not used)
    def extra_attributes(self, node):
        '''Return the tuple (field,repr(field)) for all extra fields.'''
        d = {
            # 'e': self.do_repr,
            # 'cache':self.do_cache_list,
            # 'reach':self.do_reaching_list,
            # 'typ':  self.do_types_list,
        }
        aList = []
        for attr in sorted(d.keys()):
            if hasattr(node, attr):
                val = getattr(node, attr)
                f = d.get(attr)
                s = f(attr, node, val)
                if s:
                    aList.append((attr, s),)
        return aList
    #@+node:ekr.20141012064706.18395: *4* d.do_cache_list
    def do_cache_list(self, attr, node, val):
        return self.u.dump_cache(node)
    #@+node:ekr.20141012064706.18396: *4* d.do_reaching_list
    def do_reaching_list(self, attr, node, val):
        assert attr == 'reach'
        return '[%s]' % ','.join(
            [self.format(z).strip() or repr(z)
                for z in getattr(node, attr)])
    #@+node:ekr.20141012064706.18397: *4* d.do_repr
    def do_repr(self, attr, node, val):
        return repr(val)
    #@+node:ekr.20141012064706.18398: *4* d.do_types_list
    def do_types_list(self, attr, node, val):
        assert attr == 'typ'
        return '[%s]' % ','.join(
            [repr(z) for z in getattr(node, attr)])
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
    def format(self, node):
        '''Format the node (or list of nodes) and its descendants.'''
        self.level = 0
        val = self.visit(node)
        return val and val.strip() or ''
    #@+node:ekr.20141012064706.18403: *4* f.visit
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
            assert type(s) == type('abc'), type(s)
            return s
    #@+node:ekr.20141012064706.18404: *3* f.Contexts
    #@+node:ekr.20141012064706.18405: *4* f.ClassDef
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
    #@+node:ekr.20141012064706.18406: *4* f.FunctionDef
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
    #@+node:ekr.20141012064706.18407: *4* f.Interactive
    def do_Interactive(self, node):
        for z in node.body:
            self.visit(z)
    #@+node:ekr.20141012064706.18408: *4* f.Module
    def do_Module(self, node):
        assert 'body' in node._fields
        result = ''.join([self.visit(z) for z in node.body])
        return result # 'module:\n%s' % (result)
    #@+node:ekr.20141012064706.18409: *4* f.Lambda
    def do_Lambda(self, node):
        return self.indent('lambda %s: %s' % (
            self.visit(node.args),
            self.visit(node.body)))
    #@+node:ekr.20141012064706.18410: *3* f.Expressions
    #@+node:ekr.20141012064706.18411: *4* f.Expr
    def do_Expr(self, node):
        '''An outer expression: must be indented.'''
        return self.indent('%s\n' % self.visit(node.value))
    #@+node:ekr.20141012064706.18412: *4* f.Expression
    def do_Expression(self, node):
        '''An inner expression: do not indent.'''
        return '%s\n' % self.visit(node.body)
    #@+node:ekr.20141012064706.18413: *4* f.GeneratorExp
    def do_GeneratorExp(self, node):
        elt = self.visit(node.elt) or ''
        gens = [self.visit(z) for z in node.generators]
        gens = [z if z else '<**None**>' for z in gens] ### Kludge: probable bug.
        return '<gen %s for %s>' % (elt, ','.join(gens))
    #@+node:ekr.20141012064706.18414: *4* f.ctx nodes
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
    #@+node:ekr.20141012064706.18415: *3* f.Operands
    #@+node:ekr.20141012064706.18416: *4* f.arguments
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
    #@+node:ekr.20141012064706.18417: *4* f.arg (Python3 only)
    # Python 3:
    # arg = (identifier arg, expr? annotation)

    def do_arg(self, node):
        if node.annotation:
            return self.visit(node.annotation)
        else:
            return ''
    #@+node:ekr.20141012064706.18418: *4* f.Attribute
    # Attribute(expr value, identifier attr, expr_context ctx)

    def do_Attribute(self, node):
        return '%s.%s' % (
            self.visit(node.value),
            node.attr) # Don't visit node.attr: it is always a string.
    #@+node:ekr.20141012064706.18419: *4* f.Bytes
    def do_Bytes(self, node): # Python 3.x only.
        assert g.isPython3
        return str(node.s)
    #@+node:ekr.20141012064706.18420: *4* f.Call & f.keyword
    # Call(expr func, expr* args, keyword* keywords, expr? starargs, expr? kwargs)

    def do_Call(self, node):
        # g.trace(node,Utils().dump_ast(node))
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
    #@+node:ekr.20141012064706.18421: *5* f.keyword
    # keyword = (identifier arg, expr value)

    def do_keyword(self, node):
        # node.arg is a string.
        value = self.visit(node.value)
        # This is a keyword *arg*, not a Python keyword!
        return '%s=%s' % (node.arg, value)
    #@+node:ekr.20141012064706.18422: *4* f.comprehension
    def do_comprehension(self, node):
        result = []
        name = self.visit(node.target) # A name.
        it = self.visit(node.iter) # An attribute.
        result.append('%s in %s' % (name, it))
        ifs = [self.visit(z) for z in node.ifs]
        if ifs:
            result.append(' if %s' % (''.join(ifs)))
        return ''.join(result)
    #@+node:ekr.20141012064706.18423: *4* f.Dict
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
    #@+node:ekr.20141012064706.18424: *4* f.Ellipsis
    def do_Ellipsis(self, node):
        return '...'
    #@+node:ekr.20141012064706.18425: *4* f.ExtSlice
    def do_ExtSlice(self, node):
        return ':'.join([self.visit(z) for z in node.dims])
    #@+node:ekr.20141012064706.18426: *4* f.Index
    def do_Index(self, node):
        return self.visit(node.value)
    #@+node:ekr.20141012064706.18427: *4* f.List
    def do_List(self, node):
        # Not used: list context.
        # self.visit(node.ctx)
        elts = [self.visit(z) for z in node.elts]
        elst = [z for z in elts if z] # Defensive.
        return '[%s]' % ','.join(elts)
    #@+node:ekr.20141012064706.18428: *4* f.ListComp
    def do_ListComp(self, node):
        elt = self.visit(node.elt)
        gens = [self.visit(z) for z in node.generators]
        gens = [z if z else '<**None**>' for z in gens] ### Kludge: probable bug.
        return '%s for %s' % (elt, ''.join(gens))
    #@+node:ekr.20141012064706.18429: *4* f.Name
    def do_Name(self, node):
        return node.id
    #@+node:ekr.20141012064706.18430: *4* f.Num
    def do_Num(self, node):
        return repr(node.n)
    #@+node:ekr.20141012064706.18431: *4* f.Repr
    # Python 2.x only

    def do_Repr(self, node):
        return 'repr(%s)' % self.visit(node.value)
    #@+node:ekr.20141012064706.18432: *4* f.Slice
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
    #@+node:ekr.20141012064706.18433: *4* f.Str
    def do_Str(self, node):
        '''This represents a string constant.'''
        return repr(node.s)
    #@+node:ekr.20141012064706.18434: *4* f.Subscript
    # Subscript(expr value, slice slice, expr_context ctx)

    def do_Subscript(self, node):
        value = self.visit(node.value)
        the_slice = self.visit(node.slice)
        return '%s[%s]' % (value, the_slice)
    #@+node:ekr.20141012064706.18435: *4* f.Tuple
    def do_Tuple(self, node):
        elts = [self.visit(z) for z in node.elts]
        return '(%s)' % ','.join(elts)
    #@+node:ekr.20141012064706.18436: *3* f.Operators
    #@+node:ekr.20141012064706.18437: *4* f.BinOp
    def do_BinOp(self, node):
        return '%s%s%s' % (
            self.visit(node.left),
            self.op_name(node.op),
            self.visit(node.right))
    #@+node:ekr.20141012064706.18438: *4* f.BoolOp
    def do_BoolOp(self, node):
        op_name = self.op_name(node.op)
        values = [self.visit(z) for z in node.values]
        return op_name.join(values)
    #@+node:ekr.20141012064706.18439: *4* f.Compare
    def do_Compare(self, node):
        result = []
        lt = self.visit(node.left)
        # ops   = [self.visit(z) for z in node.ops]
        ops = [self.op_name(z) for z in node.ops]
        comps = [self.visit(z) for z in node.comparators]
        result.append(lt)
        if len(ops) == len(comps):
            for i in range(len(ops)):
                result.append('%s%s' % (ops[i], comps[i]))
        else:
            g.trace('ops', repr(ops), 'comparators', repr(comps))
        return ''.join(result)
    #@+node:ekr.20141012064706.18440: *4* f.UnaryOp
    def do_UnaryOp(self, node):
        return '%s%s' % (
            self.op_name(node.op),
            self.visit(node.operand))
    #@+node:ekr.20141012064706.18441: *4* f.ifExp (ternary operator)
    def do_IfExp(self, node):
        return '%s if %s else %s ' % (
            self.visit(node.body),
            self.visit(node.test),
            self.visit(node.orelse))
    #@+node:ekr.20141012064706.18442: *3* f.Statements
    #@+node:ekr.20141012064706.18443: *4* f.Assert
    def do_Assert(self, node):
        test = self.visit(node.test)
        if getattr(node, 'msg', None):
            message = self.visit(node.msg)
            return self.indent('assert %s, %s' % (test, message))
        else:
            return self.indent('assert %s' % test)
    #@+node:ekr.20141012064706.18444: *4* f.Assign
    def do_Assign(self, node):
        return self.indent('%s=%s\n' % (
            '='.join([self.visit(z) for z in node.targets]),
            self.visit(node.value)))
    #@+node:ekr.20141012064706.18445: *4* f.AugAssign
    def do_AugAssign(self, node):
        return self.indent('%s%s=%s\n' % (
            self.visit(node.target),
            self.op_name(node.op), # Bug fix: 2013/03/08.
            self.visit(node.value)))
    #@+node:ekr.20141012064706.18446: *4* f.Break
    def do_Break(self, node):
        return self.indent('break\n')
    #@+node:ekr.20141012064706.18447: *4* f.Continue
    def do_Continue(self, node):
        return self.indent('continue\n')
    #@+node:ekr.20141012064706.18448: *4* f.Delete
    def do_Delete(self, node):
        targets = [self.visit(z) for z in node.targets]
        return self.indent('del %s\n' % ','.join(targets))
    #@+node:ekr.20141012064706.18449: *4* f.ExceptHandler
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
    #@+node:ekr.20141012064706.18450: *4* f.Exec
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
    #@+node:ekr.20141012064706.18451: *4* f.For
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
    #@+node:ekr.20141012064706.18452: *4* f.Global
    def do_Global(self, node):
        return self.indent('global %s\n' % (
            ','.join(node.names)))
    #@+node:ekr.20141012064706.18453: *4* f.If
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
    #@+node:ekr.20141012064706.18454: *4* f.Import & helper
    def do_Import(self, node):
        names = []
        for fn, asname in self.get_import_names(node):
            if asname:
                names.append('%s as %s' % (fn, asname))
            else:
                names.append(fn)
        return self.indent('import %s\n' % (
            ','.join(names)))
    #@+node:ekr.20141012064706.18455: *5* f.get_import_names
    def get_import_names(self, node):
        '''Return a list of the the full file names in the import statement.'''
        result = []
        for ast2 in node.names:
            if self.kind(ast2) == 'alias':
                data = ast2.name, ast2.asname
                result.append(data)
            else:
                g.trace('unsupported kind in Import.names list', self.kind(ast2))
        return result
    #@+node:ekr.20141012064706.18456: *4* f.ImportFrom
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
    #@+node:ekr.20141012064706.18457: *4* f.Pass
    def do_Pass(self, node):
        return self.indent('pass\n')
    #@+node:ekr.20141012064706.18458: *4* f.Print
    # Python 2.x only

    def do_Print(self, node):
        vals = []
        for z in node.values:
            vals.append(self.visit(z))
        if getattr(node, 'dest', None):
            vals.append('dest=%s' % self.visit(node.dest))
        if getattr(node, 'nl', None):
            # vals.append('nl=%s' % self.visit(node.nl))
            vals.append('nl=%s' % node.nl)
        return self.indent('print(%s)\n' % (
            ','.join(vals)))
    #@+node:ekr.20141012064706.18459: *4* f.Raise
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
    #@+node:ekr.20141012064706.18460: *4* f.Return
    def do_Return(self, node):
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
    #@+node:ekr.20141012064706.18463: *4* f.TryFinally
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
    #@+node:ekr.20141012064706.18464: *4* f.While
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
    #@+node:ekr.20141012064706.18465: *4* f.With
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
    #@+node:ekr.20141012064706.18466: *4* f.Yield
    def do_Yield(self, node):
        if getattr(node, 'value', None):
            return self.indent('yield %s\n' % (
                self.visit(node.value)))
        else:
            return self.indent('yield\n')
    #@+node:ekr.20141012064706.18467: *3* f.Utils
    #@+node:ekr.20141012064706.18468: *4* f.kind
    def kind(self, node):
        '''Return the name of node's class.'''
        return node.__class__.__name__
    #@+node:ekr.20141012064706.18469: *4* f.indent
    def indent(self, s):
        return '%s%s' % (' ' * 4 * self.level, s)
    #@+node:ekr.20141012064706.18470: *4* f.op_name
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
        self.trace = False
    #@+others
    #@+node:ekr.20141012064706.18472: *3* ft.contexts
    #@+node:ekr.20141012064706.18473: *4* ft.ClassDef
    # ClassDef(identifier name, expr* bases, stmt* body, expr* decorator_list)

    def do_ClassDef(self, node):
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

    def do_FunctionDef(self, node):
        old_context = self.context
        self.context = node
        # Visit the tree in token order.
        for z in node.decorator_list:
            self.visit(z)
        assert g.isString(node.name)
        self.visit(node.args)
        for z in node.body:
            self.visit(z)
        self.context = old_context
    #@+node:ekr.20141012064706.18475: *4* ft.Interactive
    def do_Interactive(self, node):
        assert False, 'Interactive context not supported'
    #@+node:ekr.20141012064706.18476: *4* ft.Lambda
    # Lambda(arguments args, expr body)

    def do_Lambda(self, node):
        old_context = self.context
        self.context = node
        self.visit(node.args)
        self.visit(node.body)
        self.context = old_context
    #@+node:ekr.20141012064706.18477: *4* ft.Module
    def do_Module(self, node):
        self.context = node
        for z in node.body:
            self.visit(z)
        self.context = None
    #@+node:ekr.20141012064706.18478: *3* ft.ctx nodes
    # Not used in this class, but may be called by subclasses.

    def do_AugLoad(self, node):
        pass

    def do_Del(self, node):
        pass

    def do_Load(self, node):
        pass

    def do_Param(self, node):
        pass

    def do_Store(self, node):
        pass
    #@+node:ekr.20141012064706.18479: *3* ft.kind
    def kind(self, node):
        return node.__class__.__name__
    #@+node:ekr.20141012064706.18480: *3* ft.operators & operands
    #@+node:ekr.20141012064706.18482: *4* ft.arguments & arg
    # arguments = (expr* args, identifier? vararg, identifier? kwarg, expr* defaults)

    def do_arguments(self, node):
        for z in node.args:
            self.visit(z)
        for z in node.defaults:
            self.visit(z)
    # Python 3:
    # arg = (identifier arg, expr? annotation)

    def do_arg(self, node):
        if node.annotation:
            self.visit(node.annotation)
    #@+node:ekr.20141012064706.18483: *4* ft.Attribute
    # Attribute(expr value, identifier attr, expr_context ctx)

    def do_Attribute(self, node):
        self.visit(node.value)
        # self.visit(node.ctx)
    #@+node:ekr.20141012064706.18484: *4* ft.BinOp
    # BinOp(expr left, operator op, expr right)

    def do_BinOp(self, node):
        self.visit(node.left)
        # self.op_name(node.op)
        self.visit(node.right)
    #@+node:ekr.20141012064706.18485: *4* ft.BoolOp
    # BoolOp(boolop op, expr* values)

    def do_BoolOp(self, node):
        for z in node.values:
            self.visit(z)
    #@+node:ekr.20141012064706.18481: *4* ft.Bytes
    def do_Bytes(self, node):
        pass # Python 3.x only.
    #@+node:ekr.20141012064706.18486: *4* ft.Call
    # Call(expr func, expr* args, keyword* keywords, expr? starargs, expr? kwargs)

    def do_Call(self, node):
        # Call the nodes in token order.
        self.visit(node.func)
        for z in node.args:
            self.visit(z)
        for z in node.keywords:
            self.visit(z)
        if getattr(node, 'starargs', None):
            self.visit(node.starargs)
        if getattr(node, 'kwargs', None):
            self.visit(node.kwargs)
    #@+node:ekr.20141012064706.18487: *4* ft.Compare
    # Compare(expr left, cmpop* ops, expr* comparators)

    def do_Compare(self, node):
        # Visit all nodes in token order.
        self.visit(node.left)
        assert len(node.ops) == len(node.comparators)
        for i in range(len(node.ops)):
            self.visit(node.ops[i])
            self.visit(node.comparators[i])
        # self.visit(node.left)
        # for z in node.comparators:
            # self.visit(z)
    #@+node:ekr.20150526140323.1: *4* ft.Compare ops
    # Eq | NotEq | Lt | LtE | Gt | GtE | Is | IsNot | In | NotIn

    def do_Eq(self, node): pass

    def do_Gt(self, node): pass

    def do_GtE(self, node): pass

    def do_In(self, node): pass

    def do_Is(self, node): pass

    def do_IsNot(self, node): pass

    def do_Lt(self, node): pass

    def do_LtE(self, node): pass

    def do_NotEq(self, node): pass

    def do_NotIn(self, node): pass
    #@+node:ekr.20141012064706.18488: *4* ft.comprehension
    # comprehension (expr target, expr iter, expr* ifs)

    def do_comprehension(self, node):
        self.visit(node.target) # A name.
        self.visit(node.iter) # An attribute.
        for z in node.ifs:
            self.visit(z)
    #@+node:ekr.20141012064706.18489: *4* ft.Dict
    # Dict(expr* keys, expr* values)

    def do_Dict(self, node):
        # Visit all nodes in token order.
        assert len(node.keys) == len(node.values)
        for i in range(len(node.keys)):
            self.visit(node.keys[i])
            self.visit(node.values[i])
    #@+node:ekr.20150522081707.1: *4* ft.Ellipsis
    def do_Ellipsis(self, node):
        pass
    #@+node:ekr.20141012064706.18490: *4* ft.Expr
    # Expr(expr value)

    def do_Expr(self, node):
        self.visit(node.value)
    #@+node:ekr.20141012064706.18491: *4* ft.Expression
    def do_Expression(self, node):
        '''An inner expression'''
        self.visit(node.body)
    #@+node:ekr.20141012064706.18492: *4* ft.ExtSlice
    def do_ExtSlice(self, node):
        for z in node.dims:
            self.visit(z)
    #@+node:ekr.20141012064706.18493: *4* ft.GeneratorExp
    # GeneratorExp(expr elt, comprehension* generators)

    def do_GeneratorExp(self, node):
        self.visit(node.elt)
        for z in node.generators:
            self.visit(z)
    #@+node:ekr.20141012064706.18494: *4* ft.ifExp (ternary operator)
    # IfExp(expr test, expr body, expr orelse)

    def do_IfExp(self, node):
        self.visit(node.body)
        self.visit(node.test)
        self.visit(node.orelse)
    #@+node:ekr.20141012064706.18495: *4* ft.Index
    def do_Index(self, node):
        self.visit(node.value)
    #@+node:ekr.20141012064706.18496: *4* ft.keyword
    # keyword = (identifier arg, expr value)

    def do_keyword(self, node):
        # node.arg is a string.
        self.visit(node.value)
    #@+node:ekr.20141012064706.18497: *4* ft.List & ListComp
    # List(expr* elts, expr_context ctx)

    def do_List(self, node):
        for z in node.elts:
            self.visit(z)
        # self.visit(node.ctx)
    # ListComp(expr elt, comprehension* generators)

    def do_ListComp(self, node):
        elt = self.visit(node.elt)
        for z in node.generators:
            self.visit(z)
    #@+node:ekr.20141012064706.18498: *4* ft.Name (revise)
    # Name(identifier id, expr_context ctx)

    def do_Name(self, node):
        # self.visit(node.ctx)
        pass
    #@+node:ekr.20150522081736.1: *4* ft.Num
    def do_Num(self, node):
        pass # Num(object n) # a number as a PyObject.
    #@+node:ekr.20141012064706.18499: *4* ft.Repr
    # Python 2.x only
    # Repr(expr value)

    def do_Repr(self, node):
        self.visit(node.value)
    #@+node:ekr.20141012064706.18500: *4* ft.Slice
    def do_Slice(self, node):
        if getattr(node, 'lower', None):
            self.visit(node.lower)
        if getattr(node, 'upper', None):
            self.visit(node.upper)
        if getattr(node, 'step', None):
            self.visit(node.step)
    #@+node:ekr.20150522081748.1: *4* ft.Str
    def do_Str(self, node):
        pass # represents a string constant.
    #@+node:ekr.20141012064706.18501: *4* ft.Subscript
    # Subscript(expr value, slice slice, expr_context ctx)

    def do_Subscript(self, node):
        self.visit(node.value)
        self.visit(node.slice)
        # self.visit(node.ctx)
    #@+node:ekr.20141012064706.18502: *4* ft.Tuple
    # Tuple(expr* elts, expr_context ctx)

    def do_Tuple(self, node):
        for z in node.elts:
            self.visit(z)
        # self.visit(node.ctx)
    #@+node:ekr.20141012064706.18503: *4* ft.UnaryOp
    # UnaryOp(unaryop op, expr operand)

    def do_UnaryOp(self, node):
        # self.op_name(node.op)
        self.visit(node.operand)
    #@+node:ekr.20141012064706.18504: *3* ft.statements
    #@+node:ekr.20141012064706.18505: *4* ft.alias
    # identifier name, identifier? asname)

    def do_alias(self, node):
        # self.visit(node.name)
        # if getattr(node,'asname')
            # self.visit(node.asname)
        pass
    #@+node:ekr.20141012064706.18506: *4* ft.Assert
    # Assert(expr test, expr? msg)

    def do_Assert(self, node):
        self.visit(node.test)
        if node.msg:
            self.visit(node.msg)
    #@+node:ekr.20141012064706.18507: *4* ft.Assign
    # Assign(expr* targets, expr value)

    def do_Assign(self, node):
        for z in node.targets:
            self.visit(z)
        self.visit(node.value)
    #@+node:ekr.20141012064706.18508: *4* ft.AugAssign
    # AugAssign(expr target, operator op, expr value)

    def do_AugAssign(self, node):
        # g.trace('FT',Utils().format(node),g.callers())
        self.visit(node.target)
        self.visit(node.value)
    #@+node:ekr.20141012064706.18509: *4* ft.Break
    def do_Break(self, tree):
        pass
    #@+node:ekr.20141012064706.18510: *4* ft.Continue
    def do_Continue(self, tree):
        pass
    #@+node:ekr.20141012064706.18511: *4* ft.Delete
    # Delete(expr* targets)

    def do_Delete(self, node):
        for z in node.targets:
            self.visit(z)
    #@+node:ekr.20141012064706.18512: *4* ft.ExceptHandler
    # Python 2: ExceptHandler(expr? type, expr? name, stmt* body)
    # Python 3: ExceptHandler(expr? type, identifier? name, stmt* body)

    def do_ExceptHandler(self, node):
        if node.type:
            self.visit(node.type)
        if node.name and isinstance(node.name, ast.Name):
            self.visit(node.name)
        for z in node.body:
            self.visit(z)
    #@+node:ekr.20141012064706.18513: *4* ft.Exec
    # Python 2.x only
    # Exec(expr body, expr? globals, expr? locals)

    def do_Exec(self, node):
        self.visit(node.body)
        if getattr(node, 'globals', None):
            self.visit(node.globals)
        if getattr(node, 'locals', None):
            self.visit(node.locals)
    #@+node:ekr.20141012064706.18514: *4* ft.For
    # For(expr target, expr iter, stmt* body, stmt* orelse)

    def do_For(self, node):
        self.visit(node.target)
        self.visit(node.iter)
        for z in node.body:
            self.visit(z)
        for z in node.orelse:
            self.visit(z)
    #@+node:ekr.20141012064706.18515: *4* ft.Global
    # Global(identifier* names)

    def do_Global(self, node):
        pass
    #@+node:ekr.20141012064706.18516: *4* ft.If
    # If(expr test, stmt* body, stmt* orelse)

    def do_If(self, node):
        self.visit(node.test)
        for z in node.body:
            self.visit(z)
        for z in node.orelse:
            self.visit(z)
    #@+node:ekr.20141012064706.18517: *4* ft.Import & ImportFrom
    # Import(alias* names)

    def do_Import(self, node):
        pass
    # ImportFrom(identifier? module, alias* names, int? level)

    def do_ImportFrom(self, node):
        # for z in node.names:
            # self.visit(z)
        pass
    #@+node:ekr.20141012064706.18518: *4* ft.Pass
    def do_Pass(self, node):
        pass
    #@+node:ekr.20141012064706.18519: *4* ft.Print
    # Python 2.x only
    # Print(expr? dest, expr* values, bool nl)

    def do_Print(self, node):
        if getattr(node, 'dest', None):
            self.visit(node.dest)
        for expr in node.values:
            self.visit(expr)
    #@+node:ekr.20141012064706.18520: *4* ft.Raise
    # Raise(expr? type, expr? inst, expr? tback)

    def do_Raise(self, node):
        if getattr(node, 'type', None):
            self.visit(node.type)
        if getattr(node, 'inst', None):
            self.visit(node.inst)
        if getattr(node, 'tback', None):
            self.visit(node.tback)
    #@+node:ekr.20141012064706.18521: *4* ft.Return
    # Return(expr? value)

    def do_Return(self, node):
        if node.value:
            self.visit(node.value)
    #@+node:ekr.20141012064706.18522: *4* ft.Try (Python 3 only)
    # Python 3 only: Try(stmt* body, excepthandler* handlers, stmt* orelse, stmt* finalbody)

    def do_Try(self, node):
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

    def do_TryExcept(self, node):
        for z in node.body:
            self.visit(z)
        for z in node.handlers:
            self.visit(z)
        for z in node.orelse:
            self.visit(z)
    #@+node:ekr.20141012064706.18524: *4* ft.TryFinally
    # TryFinally(stmt* body, stmt* finalbody)

    def do_TryFinally(self, node):
        for z in node.body:
            self.visit(z)
        for z in node.finalbody:
            self.visit(z)
    #@+node:ekr.20141012064706.18525: *4* ft.While
    # While(expr test, stmt* body, stmt* orelse)

    def do_While(self, node):
        self.visit(node.test) # Bug fix: 2013/03/23.
        for z in node.body:
            self.visit(z)
        for z in node.orelse:
            self.visit(z)
    #@+node:ekr.20141012064706.18526: *4* ft.With
    # With(expr context_expr, expr? optional_vars, stmt* body)

    def do_With(self, node):
        self.visit(node.context_expr)
        if node.optional_vars:
            self.visit(node.optional_vars)
        for z in node.body:
            self.visit(z)
    #@+node:ekr.20141012064706.18527: *4* ft.Yield
    #  Yield(expr? value)

    def do_Yield(self, node):
        if node.value:
            self.visit(node.value)
    #@+node:ekr.20141012064706.18528: *3* ft.visit
    def visit(self, node):
        '''Visit a *single* ast node.  Visitors are responsible for visiting children!'''
        assert isinstance(node, ast.AST), node.__class__.__name__
        trace = False
        # Visit the children with the new parent.
        old_parent = self.parent
        parent = node
        method_name = 'do_' + node.__class__.__name__
        method = getattr(self, method_name)
        if trace: g.trace(method_name)
        val = method(node)
        self.parent = old_parent
        return val

    def visit_children(self, node):
        assert False, 'must visit children explicitly'
    #@+node:ekr.20141012064706.18529: *3* ft.visit_list
    def visit_list(self, aList):
        '''Visit all ast nodes in aList.'''
        assert isinstance(aList, (list, tuple)), repr(aList)
        for z in aList:
            self.visit(z)
        return None
    #@-others
#@+node:ekr.20141012064706.18530: ** class AstPatternFormatter
class AstPatternFormatter(AstFormatter):
    '''
    A subclass of AstFormatter that replaces values of constants by Bool,
    Bytes, Int, Name, Num or Str.
    '''
    # No ctor.
    #@+others
    #@+node:ekr.20141012064706.18531: *3* Constants & Name
    # Return generic markers allow better pattern matches.

    def do_BoolOp(self, node): # Python 2.x only.
        return 'Bool'

    def do_Bytes(self, node): # Python 3.x only.
        return 'Bytes' # return str(node.s)

    def do_Name(self, node):
        return 'Bool' if node.id in ('True', 'False') else node.id

    def do_Num(self, node):
        return 'Num' # return repr(node.n)

    def do_Str(self, node):
        '''This represents a string constant.'''
        return 'Str' # return repr(node.s)
    #@-others
#@+node:ekr.20150722204300.1: ** class HTMLReportTraverser (AstFullTraverser)
class NewHTMLReportTraverser(AstFullTraverser):
    '''
    Create html reports from an AST tree.
    
    Adapted from micropython, by Paul Boddie. See the copyright notices.

    This new version writes all html to a global code list.
    All newlines are inserted explicitly.
    '''
    # To do: show stc attributes in the report.
    # To do: revise report-traverser-debug.css.
    #@+others
    #@+node:ekr.20150722204300.2: *3* rt.__init__
    def __init__(self):
        '''Ctor for the NewHTMLReportTraverser class.'''
        self.visitor = self
        AstFullTraverser.__init__(self)
            # Init the base class.
        self.code_list = []
        self.debug = True
        self.indent = 0
        debug_css = 'report-traverser-debug.css'
        plain_css = 'report-traverser.css'
        self.css_fn = debug_css if self.debug else plain_css
        self.html_footer = '\n</body>\n</html>\n'
        self.html_header = self.define_html_header()
    #@+node:ekr.20150722204300.3: *4* define_html_header
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
    #@+node:ekr.20150722204300.4: *3* rt.css links & popup
    #@+node:ekr.20150722204300.5: *4* rt.link
    def link(self, class_name, href, a_text):
        # g.trace(class_name,a_text)
        return "<a class='%s' href='%s'>%s</a>\n" % (class_name, href, a_text)
    #@+node:ekr.20150722204300.6: *4* rt.module_link
    def module_link(self, module_name, classes=None):
        r = self
        return r.link(
            class_name=classes or 'name',
            href='%s.xhtml' % module_name,
            a_text=r.text(module_name))
    #@+node:ekr.20150722204300.7: *4* rt.name_link
    def name_link(self, module_name, full_name, name, classes=None):
        r = self
        # g.trace(name,classes)
        return r.link(
            class_name=classes or "specific-ref",
            href='%s.xhtml#%s' % (module_name, r.attr(full_name)),
            a_text=r.text(name))
    #@+node:ekr.20150722204300.8: *4* rt.object_name_ref
    def object_name_ref(self, module, obj, name=None, classes=None):
        """
        Link to the definition for 'module' using 'obj' with the optional 'name'
        used as the label (instead of the name of 'obj'). The optional 'classes'
        can be used to customise the CSS classes employed.
        """
        r = self
        return r.name_link(
            module.full_name(),
            obj.full_name(),
            name or obj.name, classes)
    #@+node:ekr.20150722204300.9: *4* rt.popup
    def popup(self, classes, aList):
        r = self
        r.span_list(classes or 'popup', aList)
    #@+node:ekr.20150722204300.10: *4* rt.summary_link
    def summary_link(self, module_name, full_name, name, classes=None):
        r = self
        return r.name_link(
            "%s-summary" % module_name,
            full_name, name,
            classes)
    #@+node:ekr.20150722204300.11: *3* rt.html attribute helpers
    #@+at
    #@@language rest
    #@@wrap
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
    #@@c
    #@@language python

    #@+node:ekr.20150722204300.12: *4* rt.get_stc_attrs & AttributeTraverser
    def get_stc_attrs(self, node, all):
        r = self
        nodes = r.NameTraverser(self.u).run(node) if all else [node]
        result = []
        for node in nodes:
            aList = []
            e = getattr(node, 'e', None)
            reach = getattr(node, 'reach', None)
            if e:
                aList.append(r.text('%s cx: %s defined: %s' % (
                    e.name, e.cx.name, e.defined)))
            if reach:
                for item in reach:
                    aList.append(r.text('reach: %s' % r.u.format(item)))
            result.append(join_list(aList, sep=', '))
        return join_list(result, sep='; ')
    #@+node:ekr.20150722204300.13: *5* NameTraverser(AstFullTraverser)
    class NameTraverser(AstFullTraverser):

        def __init__(self):
            AstFullTraverser.__init__(self)
            self.d = {}

        def do_Name(self, node):
            self.d[node.e.name] = node

        def run(self, root):
            self.visit(root)
            return [self.d.get(key) for key in sorted(self.d.keys())]
    #@+node:ekr.20150722204300.14: *4* rt.stc_attrs
    def stc_attrs(self, node, all=False):
        r = self
        attrs = r.get_stc_attrs(node, all=all)
        return attrs and [
            r.span('inline-attr nowrap', [
                attrs,
            ]),
            r.br(),
        ]
    #@+node:ekr.20150722204300.15: *4* rt.stc_popup_attrs
    def stc_popup_attrs(self, node, all=False):
        r = self
        ###
        # attrs = r.get_stc_attrs(node, all=all)
        # return attrs and [
            # r.popup('attr-popup', [
                # attrs,
            # ]),
        # ]
        attrs = r.get_stc_attrs(node, all=all)
        if attrs:
            r.popup('attr-popup', attrs)
    #@+node:ekr.20150722204300.16: *3* rt.html helpers
    #@+node:ekr.20150722204300.17: *4* rt.attr & text
    def attr(self, s):
        r = self
        return r.text(s).replace("'", "&apos;").replace('"', "&quot;")

    def text(self, s):
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    #@+node:ekr.20150722204300.18: *4* rt.br
    def br(self):
        r = self
        return '\n<br />'
    #@+node:ekr.20150722204300.19: *4* rt.comment
    def comment(self, comment):
        r = self
        return '%s\n' % r.span("# %s" % (comment), "comment")
    #@+node:ekr.20150722204300.20: *4* rt.div & end_div
    def div(self, class_name, extra=None):
        '''Generate the start of a div element.'''
        r = self
        if class_name and extra:
            div = "\n<div class='%s' %s>" % (class_name, extra)
        elif class_name:
            div = "\n<div class='%s'>" % (class_name)
        else:
            assert not extra
            div = "\n<div>"
        r.gen(div)
        self.indent += 4
        ###
        # assert isinstance(aList, (list, tuple))
        # return [
            # div,
            # join_list(aList, indent='  '),
            # '\n</div>'
        # ]
        
    def end_div(self):
        self.indent -= 4
        r.gen('\n</div>\n')
    #@+node:ekr.20150722222149.1: *4* rt.div_body
    def div_body(self, aList):
        r = self
        if aList:
            r.div_list('body nowrap', aList)
    #@+node:ekr.20150722221408.1: *4* rt.div_keyword_colon
    def div_keyword_colon(self, class_name, keyword):
        r = self
        self.div(class_name)
        self.keyword_colon(keyword)
        self.end_div()
    #@+node:ekr.20150722221101.1: *4* rt.div_list & div_node
    def div_list(self, class_name, aList, sep=None):
        r = self
        r.div(class_name)
        r.visit_list(aList, sep=sep)
        r.end_div()
        
    def div_node(self, class_name, node):
        r = self
        r.div(class_name)
        r.visit(node)
        r.end_div()



    #@+node:ekr.20150722204300.21: *4* rt.doc & helper (to do)
    # Called by ClassDef & FunctionDef visitors.

    def doc(self, node, classes=None):
        # if node.doc is not None:
            # r.docstring(node.doc,classes)
        pass
    #@+node:ekr.20150722204300.22: *5* rt.docstring
    def docstring(self, s, classes=None):
        r = self
        if classes: classes = ' ' + classes
        return [
            "<pre class='doc%s'>" % (classes),
            '"""',
            r.text(textwrap.dedent(s.replace('"""', '\\"\\"\\"'))),
            '"""',
            "</pre>\n",
        ]
    #@+node:ekr.20150722204300.23: *4* rt.keyword (a helper, not a visitor!)
    def keyword(self, keyword_name, leading=False, trailing=True):
        r = self
        ###
        # return [
            # leading and ' ',
            # r.span('keyword', [
                # keyword_name,
            # ]),
            # trailing and ' ',
        # ]
        if leading:
            r.blank()
        r.span('keyword')
        r.gen(keyword_name)
        r.end_span()
        if trailing:
            r.blank()
    #@+node:ekr.20150722204300.24: *4* rt.name
    def name(self, name):
        r = self
        r.span('name')
        r.gen(name)
        r.end_span()
    #@+node:ekr.20150722204300.25: *4* rt.object_name_def (rewrite)
    def object_name_def(self, module, obj, classes=None):
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
    #@+node:ekr.20150722204300.26: *4* rt.op
    def op(self, op_name, leading=False, trailing=True):
        # g.trace(repr(op_name))
        r = self
        ###
        # return [
            # leading and ' ',
            # r.span("operation", [
                # r.span("operator", [
                    # r.text(op_name),
                # ])
                # # r.popup(None,[
                    # # r.div('opnames',[
                        # # r.name_link("operator","operator.%s" % op_name,op_name),
                    # # ]),
                # # ]),
            # ]),
            # trailing and ' ',
        # ]
        if leading:
            r.blank()
        r.span("operation")
        r.span("operator")
        r.gen(r.text(op_name))
        r.end_span() # operator
        if trailing:
            r.blank()
        r.end_span() # operation
    #@+node:ekr.20150722204300.27: *4* rt.simple_statement
    def simple_statement(self, name):
        r = self
        ###
        # return [
            # r.div('%s nowrap' % name, [
                # r.keyword(name),
            # ]),
        # ]
        r.div('%s nowrap' % name)
        r.keyword(name)
        r.end_div()
    #@+node:ekr.20150722204300.28: *4* rt.span & end_span
    def span(self, class_name): ###, aList):
        r = self
        ###assert isinstance(aList, (list, tuple))
        if class_name:
            span = "\n<span class='%s'>" % (class_name)
        else:
            span = '\n<span>'
        r.gen(span)
        # return [
            # span,
            # join_list(aList, indent='  '),
            # # '\n</span>',
            # '</span>', # More compact
        # ]
    def end_span(self):
        r = self
        r.gen('</span>')
    #@+node:ekr.20150722224734.1: *4* rt.span_list & span_node
    def span_list(self, class_name, aList):
        r = self
        r.span(class_name)
        r.visit_list(aList)
        r.end_span()

    def span_node(self, class_name, node):
        r = self
        r.span(class_name)
        r.visit(node)
        r.end_span()
    #@+node:ekr.20150722204300.29: *4* rt.url (not used)
    # def url(self, url):
        # r = self
        # return r.attr(url).replace("#", "%23").replace("-", "%2d")
    #@+node:ekr.20150722211115.1: *3* rt.gen
    def gen(self,s):
        '''Append s to the global code list.'''
        ### To do: handle indent ???
        self.code_list.append(s)
    #@+node:ekr.20150722204300.30: *3* rt.reporters
    #@+node:ekr.20150722204300.31: *4* rt.annotate
    def annotate(self, fn, m):
        r = self
        f = open(fn, "wb")
        try:
            for s in flatten_list(r.report_file()):
                f.write(s)
        finally:
            f.close()
    #@+node:ekr.20150722204300.32: *4* rt.base_fn
    def base_fn(self, directory, m):
        '''Return the basic html file name used by reporters.'''
        assert g.os_path_exists(directory)
        if m.fn.endswith('<string>'):
            return 'report_writer_string_test'
        else:
            return g.shortFileName(m.fn)
    #@+node:ekr.20150722204300.33: *4* rt.interfaces & helpers
    def interfaces(self, directory, m, open_file=False):
        r = self
        base_fn = r.base_fn(directory, m)
        fn = g.os_path_join(directory, "%s_interfaces.xhtml" % base_fn)
        f = open(fn, "wb")
        try:
            for s in flatten_list(r.write_interfaces(m)):
                f.write(s)
        finally:
            f.close()
        if open_file:
            os.startfile(fn)
    #@+node:ekr.20150722204300.34: *5* write_interfaces
    def write_interfaces(self, m):
        r = self
        all_interfaces, any_interfaces = [], []
        return join_list([
            r.html_header % {'css-fn': self.css_fn, 'title': 'Interfaces'},
            "<table cellspacing='5' cellpadding='5'>",
            "<thead>",
            "<tr>",
            "<th>Complete Interfaces</th>",
            "</tr>",
            "</thead>",
            r.write_interface_type("complete", all_interfaces),
            "<thead>",
            "<tr>",
            "<th>Partial Interfaces</th>",
            "</tr>",
            "</thead>",
            r.write_interface_type("partial", any_interfaces),
            "</table>",
            r.html_footer,
        ], trailing='\n')
    #@+node:ekr.20150722204300.35: *5* write_interface_type
    def write_interface_type(self, classes, interfaces):
        r = self
        aList = []
        for names, objects in interfaces:
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
        ], trailing='\n')
    #@+node:ekr.20150722204300.36: *4* rt.report(entry_point)
    def report(self, directory, m, open_file=False):
        trace = False
        r = self
        r.module = m
        base_fn = r.base_fn(directory, m)
        annotate_fn = g.os_path_join(directory, "%s.xhtml" % base_fn)
        # if trace: g.trace('writing %s' % (annotate_fn))
        r.annotate(annotate_fn, m)
        assert g.os_path_exists(annotate_fn), annotate_fn
        if open_file:
            os.startfile(annotate_fn)
        if 0: # The file is empty at present.
            summary_fn = g.os_path_join(directory, "%s_summary.xhtml" % base_fn)
            if trace: g.trace('writing %s' % (summary_fn))
            r.summarize(summary_fn, m)
            if open_file:
                os.startfile(summary_fn)
    #@+node:ekr.20150722204300.37: *4* rt.report_all_modules(needed to write interfaces)
    def report_all_modules(self, directory):
        trace = True
        r = self
        join = g.os_path_join
        assert g.os_path_exists(directory)
        d = r.u.modules_dict
        files = []
        for n, fn in enumerate(sorted(d.keys())):
            r.module = m = d.get(fn)
            if fn.endswith('<string>'):
                fn = 'report_writer_string_test'
            else:
                # fn = '%s_%s' % (fn,n)
                fn = g.shortFileName(fn)
            annotate_fn = g.os_path_join(directory, "%s.xhtml" % fn)
            if trace: g.trace('writing: %s.xhtml' % (annotate_fn))
            files.append(annotate_fn)
            r.annotate(annotate_fn, m)
            if 0:
                summary_fn = g.os_path_join(directory, "%s_summary.xhtml" % fn)
                if trace: g.trace('writing %s' % (summary_fn))
                r.summarize(summary_fn, m)
                if False:
                    os.startfile(summary_fn)
            # r.summarize(join(directory,"%s-summary.xhtml" % (base_fn)),m)
        # r.interfaces(join(join(directory,"-interfaces.xhtml")),m)
        if 0:
            for fn in files:
                fn2 = join(directory, fn + '.xhtml')
                assert g.os_path_exists(fn2), fn2
                os.startfile(fn2)
    #@+node:ekr.20150722204300.38: *4* rt.report_file
    def report_file(self):
        r = self
        return [
            r.html_header % {
                'css-fn': self.css_fn,
                'title': 'Module: %s' % r.module.full_name()},
            r.visit(r.module.node),
            r.html_footer,
        ]
    #@+node:ekr.20150722204300.39: *4* rt.summarize & helpers
    def summarize(self, directory, m, open_file=False):
        r = self
        base_fn = r.base_fn(directory, m)
        fn = g.os_path_join(directory, "%s_summary.xhtml" % base_fn)
        f = open(fn, "wb")
        try:
            for s in flatten_list(r.summary(m)):
                f.write(s)
        finally:
            f.close()
        if open_file:
            os.startfile(fn)
    #@+node:ekr.20150722204300.40: *5* summary & helpers
    def summary(self, m):
        r = self
        return join_list([
            r.html_header % {
                'css-fn': self.css_fn,
                'title': 'Module: %s' % m.full_name()},
            r.write_classes(m),
            r.html_footer,
        ], sep='\n')
    #@+node:ekr.20150722204300.41: *6* write_classes
    def write_classes(self, m):
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
        ], sep='\n')
    #@+node:ekr.20150722204300.42: *6* write_class
    def write_class(self, obj):
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
        instance_names = join_list(aList, sep=', ')
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
                        r.object_name_ref(r.module, obj, classes="class-name"),
                    "</th>",
                    instance_names,
                "</tr>",
                # "<tr>",
                    # class_names,
                # "</tr>",
            "</tbody>",
        ], trailing='\n')
    #@+node:ekr.20150722204300.43: *3* rt.traversers
    #@+node:ekr.20150722204300.44: *4* rt.visit
    def visit(self, node):
        """Walk a tree of AST nodes."""
        assert isinstance(node, ast.AST), node.__class__.__name__
        method_name = 'do_' + node.__class__.__name__
        method = getattr(self, method_name)
        method(node)
    #@+node:ekr.20150722204300.45: *4* rt.visit_list
    def visit_list(self, aList, sep=None):
        r = self
        if aList:
            for z in aList:
                r.visit(z)
                if sep:
                    r.gen(sep)
            if sep:
                r.clean(sep)
    #@+node:ekr.20150722204300.46: *3* rt.visitors (16 unfinished)
    #@+node:ekr.20150722204300.47: *4* rt.arguments & helper
    # arguments = (expr* args, identifier? vararg, identifier? kwarg, expr* defaults)

    def do_arguments(self, node):
        assert isinstance(node, ast.AST), node
        r = self
        first_default = len(node.args) - len(node.defaults)
        result = []
        first = True
        for n, node2 in enumerate(node.args):
            if not first: result.append(', ')
            if isinstance(node2, tuple):
                result.append(r.tuple_parameter(node.args, node2)) ### Huh?
            else:
                result.append(r.visit(node2)) ### r.assname(param,node)
            if n >= first_default:
                node3 = node.defaults[n - first_default]
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
    #@+node:ekr.20150722204300.48: *5* rt.tuple_parameter
    def tuple_parameter(self, parameters, node):
        r = self
        result = []
        result.append("(")
        first = True
        for param in parameters:
            if not first: result.append(', ')
            if isinstance(param, tuple):
                result.append(r.tuple_parameter(param, node))
            else:
                pass ### result.append(r.assname(param,node))
            first = False
        result.append(")")
        return join_list(result)
    #@+node:ekr.20150722204300.49: *4* rt.Assert
    # Assert(expr test, expr? msg)

    def do_Assert(self, node):
        r = self
        r.div('assert nowrap')
        r.keyword("assert")
        r.visit(node.test)
        if node.msg:
            r.comma()
            r.visit(node.msg)
        r.div_end()
    #@+node:ekr.20150722204300.50: *4* rt.Assign
    def do_Assign(self, node):
        r = self
        show_attrs = True
        return [
            r.div('assign nowrap', [
                [[r.visit(z), ' = '] for z in node.targets],
                r.visit(node.value),
            ]),
            show_attrs and [
                [r.stc_attrs(z) for z in node.targets],
                r.stc_attrs(node.value, all=True),
            ],
        ]
    #@+node:ekr.20150722204300.51: *4* rt.Attribute
    # Attribute(expr value, identifier attr, expr_context ctx)

    def do_Attribute(self, node):
        r = self
        return [
            r.visit(node.value),
            '.',
            node.attr,
        ]
    #@+node:ekr.20150722204300.52: *4* rt.AugAssign
    #  AugAssign(expr target, operator op, expr value)

    def do_AugAssign(self, node):
        r = self
        op_name = r.op_name(node.op)
        return [
            r.div('augassign nowrap', [
                r.visit(node.target),
                r.op(op_name, leading=True),
                r.visit(node.value),
            ]),
        ]
    #@+node:ekr.20150722204300.53: *4* rt.BinOp
    def do_BinOp(self, node):
        r = self
        op_name = r.op_name(node.op)
        return [
            r.span(op_name, [
                r.visit(node.left),
                r.op(op_name, leading=True),
                r.visit(node.right),
            ]),
        ]
    #@+node:ekr.20150722204300.54: *4* rt.BoolOp
    def do_BoolOp(self, node):
        r = self
        op_name = r.op_name(node.op)
        ops = []
        for i, node2 in enumerate(node.values):
            if i > 0:
                ops.append(r.keyword(op_name, leading=True))
            ops.append(r.visit(node2))
        return [
            r.span(op_name.strip(), [
                ops,
            ]),
        ]
    #@+node:ekr.20150722204300.55: *4* rt.Break
    def do_Break(self, node):
        r = self
        return r.simple_statement('break')
    #@+node:ekr.20150722204300.56: *4* rt.Call & rt.keyword
    # Call(expr func, expr* args, keyword* keywords, expr? starargs, expr? kwargs)

    def do_Call(self, node):
        r = self
        ###
        # args = [r.visit(z) for z in node.args]
        # args.append(# Calls rt.do_keyword.
            # join_list([r.visit(z) for z in node.keywords], sep=','))
        # if node.starargs:
            # args.append(['*', r.visit(node.starargs)])
        # if node.kwargs:
            # args.append(['**', r.visit(node.kwargs)])
        # return [
            # r.span("callfunc", [
                # r.visit(node.func),
                # r.span("call", [
                    # '(', args, ')',
                # ]),
            # ]),
        # ]
        r.span("callfunc")
        r.visit(node.func)
        r.span("call")
        r.add('(')
        self.visit_list(node.args, sep=',')
        if node_keywords:
            self.visit_list(node_keywords, sep=',')
        if node.starargs:
            r.gen('*')
            r.visit(node.starargs)
            r.comma()
        if node.kwargs:
            r.gen('**')
            r.visit(node.kwargs)
        r.clean(',')
        r.add(')')
        r.end_span() # call
        r.end_span() # callfunc
        
    #@+node:ekr.20150722204300.57: *5* rt.keyword
    # keyword = (identifier arg, expr value)
    # keyword arguments supplied to call

    def do_keyword(self, node):
        r = self
        return [
            r.span("keyword-arg", [
                node.arg,
                ' = ',
                r.visit(node.value),
            ]),
        ]
    #@+node:ekr.20150722204300.58: *4* rt.ClassDef
    # ClassDef(identifier name, expr* bases, stmt* body, expr* decorator_list)

    def do_ClassDef(self, node):
        r = self
        ###
        # return [
            # # Write the declaration line.
            # r.div('classdef nowrap', [
                # r.div(None, [
                    # r.keyword("class"),
                    # r.span(None, [node.name]), # Always a string.
                    # ### cls = node.cx
                    # ### r.object_name_def(r.module,cls,"class-name")
                    # '(',
                    # node.bases and r.visit_list(node.bases, sep=','),
                    # "):", #,"\n",
                # ]),
                # # Write the docstring and class body.
                # r.div('body nowrap', [
                    # r.doc(node),
                    # r.visit_list(node.body),
                # ]),
            # ]),
        # ]
        
        # Write the declaration line.
        r.div('classdef nowrap')
        r.div(None)
        r.keyword("class"),
        r.span(None, [node.name]), # Always a string.
        ### cls = node.cx
        ### r.object_name_def(r.module,cls,"class-name")
        if node.bases:
            r.gen('(')
            self.visit_list(node.bases, sep=',')
            r.gen(')')
        r.colon()
        r.end_div() # None
        r.div('body nowrap')
        r.doc(node),
        r.visit_list(node.body),
        r.end_div() # body
        r.end_div() # classdef
    #@+node:ekr.20150722204300.59: *4* rt.Compare
    def do_Compare(self, node):
        r = self
        assert len(node.ops) == len(node.comparators)
        ops = []
        for i in range(len(node.ops)):
            op_name = r.op_name(node.ops[i])
            ops.append(r.op(op_name, leading=True))
            expr = node.comparators[i]
            ops.append(r.visit(expr))
        return [
            r.span("compare", [
                r.visit(node.left),
                ops,
            ]),
        ]
    #@+node:ekr.20150722204300.60: *4* rt.comprehension
    def do_comprehension(self, node):
        r = self
        ifs = node.ifs and [
            r.keyword('if', leading=True),
            r.span("conditional", [
                r.visit_list(node.ifs, sep=' '),
            ]),
        ]
        return [
            r.keyword("in", leading=True),
            r.span("collection", [
                r.visit(node.iter),
                ifs,
            ]),
        ]
    #@+node:ekr.20150722204300.61: *4* rt.Continue
    def do_Continue(self, node):
        r = self
        return r.simple_statement('break')
    #@+node:ekr.20150722204300.62: *4* rt.Delete
    def do_Delete(self, node):
        r = self
        ###
        # return [
            # r.div('del nowrap', [
                # r.keyword('del'),
                # r.visit_list(node.targets, sep=','),
            # ]),
        # ]
        r.div('del nowrap')
        r.keyword('del')
        if node.targets:
            self.visit_list(node.targets, sep=',')
        r.end_div()
    #@+node:ekr.20150722204300.63: *4* rt.Dict
    def do_Dict(self, node):
        r = self
        assert len(node.keys) == len(node.values)
        items = []
        for i in range(len(node.keys)):
            items.append(r.visit(node.keys[i]))
            items.append(':')
            items.append(r.visit(node.values[i]))
            if i < len(node.keys) - 1:
                items.append(',')
        return [
            r.span("dict", [
                '{', items, '}',
            ]),
        ]
    #@+node:ekr.20150722204300.64: *4* rt.Ellipsis
    def do_Ellipsis(self, node):
        r = self
        r.gen('...')
    #@+node:ekr.20150722204300.65: *4* rt.ExceptHandler
    def do_ExceptHandler(self, node):
        r = self
        ### 
        # name = node.name and [
            # r.keyword('as', leading=True, trailing=True),
            # r.visit(node.name),
        # ]
        # return [
            # r.div('excepthandler nowrap', [
                # r.div(None, [
                    # r.keyword("except", trailing=bool(node.type)),
                    # r.visit(node.type) if node.type else '',
                    # name, ':', #'\n',
                # ]),
                # r.div('body nowrap', [
                    # r.visit_list(node.body),
                # ]),
            # ]),
        # ]
        r.div('excepthandler nowrap')
        r.div(None)
        r.keyword("except", trailing=bool(node.type)),
        if node.type:
            r.visit(node.type)
        if node.name:
            r.keyword('as', leading=True, trailing=True)
            r.visit(node.name)
        r.colon()
        r.end_div() # None
        r.div_body(node.body)
        r.end_div() # excepthandler
    #@+node:ekr.20150722204300.66: *4* rt.Exec
    # Python 2.x only.

    def do_Exec(self, node):
        r = self
        # return [
            # r.div('exec nowrap', [
                # r.keyword('exec', leading=True),
                # r.visit(node.body),
                # node.globals and [',', r.visit(node.globals)],
                # node.locals and [',', r.visit(node.locals)],
            # ]),
        # ]
        r.div('exec nowrap')
        r.keyword('exec', leading=True),
        r.visit(node.body)
        if node.globals:
            r.comma()
            r.visit(node.globals)
        if node.locals:
            r.comma()
            r.visit(node.locals)
        r.end_div() # exec
    #@+node:ekr.20150722204300.67: *4* rt.Expr
    def do_Expr(self, node):
        r = self
        ###
        # return [
            # r.div('expr', [
                # r.visit(node.value),
            # ])
        # ]
        r.div_node('expr', node.value)

    #@+node:ekr.20150722204300.68: *4* rt.For
    # For(expr target, expr iter, stmt* body, stmt* orelse)

    def do_For(self, node):
        r = self
        ###
        # orelse = node.orelse and [
            # r.div(None, [
                # r.keyword("else", trailing=False),
                # ':', # '\n',
            # ]),
            # r.div('body nowrap', [
                # r.visit_list(node.orelse),
            # ]),
        # ]
        # return [
            # r.div('if nowrap', [
                # r.div(None, [
                    # r.keyword("for"),
                    # r.visit(node.target),
                    # r.keyword("in", leading=True),
                    # r.visit(node.iter),
                    # ':', # '\n',
                # ]),
                # r.div('body nowrap', [
                    # r.visit_list(node.body),
                # ]),
                # orelse,
            # ]),
        # ]
        r.div('if nowrap')
        r.div(None)
        r.keyword("for"),
        r.visit(node.target),
        r.keyword("in", leading=True),
        r.visit(node.iter),
        r.colon()
        r.end_div() # None
        r.div_body(node.body)
        if node.orelse:
            r.div_keyword_colon(None, 'else')
            r.div_body(node.orelse)
        r.end_div() # if
    #@+node:ekr.20150722204300.69: *4* rt.FunctionDef (uses extra arg)
    def do_FunctionDef(self, node):
        r = self
        return [
            ### r.div('function nowrap','id="%s"' % (node.name)),
            r.div('function nowrap', [
                r.div(None, [
                    r.keyword("def"),
                    r.summary_link(node.cx.full_name(), node.name, node.name, classes=''),
                        ### r.object_name_def(r.module,node,"function-name")
                    '(',
                    r.visit(node.args),
                    '):', # '\n',
                        ### r.parameters(node.name,node)
                ]),
                r.div('body nowrap', [
                    r.doc(node),
                    r.visit_list(node.body),
                ]),
            ], extra='id="%s"' % (node.name)),
        ]
    #@+node:ekr.20150722204300.70: *4* rt.GeneratorExp
    def do_GeneratorExp(self, node):
        r = self
        return [
            r.span("genexpr", [
                "(",
                r.visit(node.elt) if node.elt else '',
                r.keyword('for', leading=True),
                r.span('item', [
                    r.visit(node.elt),
                ]),
                r.span('generators', [
                    r.visit_list(node.generators),
                ]),
                ")",
            ]),
        ]
    #@+node:ekr.20150722204300.71: *4* rt.get_import_names
    def get_import_names(self, node):
        '''Return a list of the the full file names in the import statement.'''
        r = self
        result = []
        for ast2 in node.names:
            if r.kind(ast2) == 'alias':
                data = ast2.name, ast2.asname
                result.append(data)
            else:
                g.trace('unsupported kind in Import.names list', r.kind(ast2))
        # g.trace(result)
        return result
    #@+node:ekr.20150722204300.72: *4* rt.Global
    def do_Global(self, node):
        r = self
        ###
        # return [
            # r.div('global nowrap', [
                # r.keyword("global"),
                # join_list(node.names, sep=','),
            # ]),
        # ]
        r.div('global nowrap')
        r.keyword("global")
        for z in node.names:
            r.gen(z)
            r.comma()
        r.clean(',')
        r.end_div() # global
    #@+node:ekr.20150722204300.73: *4* rt.If
    def do_If(self, node):
        r = self
        parent = node._parent
        # The only way to know whether to generate elif is to examine the tree.
        elif_flag = self.kind(parent) == 'If' and parent.orelse and parent.orelse[0] == node
        elif_node = node.orelse and node.orelse[0]
        if elif_node and self.kind(elif_node) == 'If':
            orelse = r.visit(elif_node)
        else:
            orelse = node.orelse and [
                r.div(None, [
                    r.keyword('else', trailing=False),
                    ':', # '\n',
                ]),
                r.div('body nowrap', [
                    r.visit_list(node.orelse),
                ]),
            ]
        # g.trace(r.u.format(node.test))
        return [
            r.div('if nowrap', [
                r.div(None, [
                    r.keyword('elif' if elif_flag else 'if'),
                    r.visit(node.test),
                    ':', # '\n',
                ]),
                r.div('body nowrap', [
                    r.visit_list(node.body),
                ]),
                orelse,
            ]),
        ]
    #@+node:ekr.20150722204300.74: *4* rt.IfExp (TernaryOp)
    # IfExp(expr test, expr body, expr orelse)

    def do_IfExp(self, node):
        r = self
        return [
            r.span("ifexp", [
                r.visit(node.body),
                r.keyword("if", leading=True),
                r.visit(node.test),
                r.keyword("else", leading=True),
                r.visit(node.orelse),
            ]),
        ]
    #@+node:ekr.20150722204300.75: *4* rt.Import
    def do_Import(self, node):
        r = self
        aList = []
        for name, alias in r.get_import_names(node):
            if alias: aList.append([
                r.module_link(name),
                r.keyword("as", leading=True),
                r.name(alias),
            ])
            else:
                aList.append(r.module_link(name))
        return [
            r.div('import nowrap', [
                r.keyword("import"),
                aList,
            ]),
        ]
    #@+node:ekr.20150722204300.76: *4* rt.ImportFrom
    def do_ImportFrom(self, node):
        r = self
        aList = []
        for name, alias in r.get_import_names(node):
            if alias: aList.append([
                r.name(name),
                r.keyword("as", leading=True),
                r.name(alias),
            ])
            else:
                aList.append(r.name(name))
        return [
            r.div('from nowrap', [
                r.keyword("from"),
                r.module_link(node.module),
                r.keyword("import", leading=True),
                aList,
            ]),
        ]
    #@+node:ekr.20150722204300.77: *4* rt.Lambda
    def do_Lambda(self, node):
        r = self
        ###
        # return [
            # r.span("lambda", [
                # r.keyword("lambda"),
                # r.visit(node.args), # r.parameters(fn,node)
                # ": ",
                # r.span("code", [
                    # r.visit(node.body),
                # ]),
            # ]),
        # ]
        r.span("lambda")
        r.keyword("lambda")
        r.visit(node.args) # r.parameters(fn,node)
        self.comma()
        r.span_node("code", node.body)      
        r.end_span() # lambda
    #@+node:ekr.20150722204300.78: *4* rt.List
    # List(expr* elts, expr_context ctx)

    def do_List(self, node):
        r = self
        ###
        # return [
            # r.span("list", [
                # '[',
                # r.visit_list(node.elts, sep=','),
                # ']',
            # ]),
        # ]
        r.span("list")
        r.gen('[')
        if node.elts:
            for z in node.elts:
                r.visit(z)
                r.comma()
            r.clean(',')
        r.gen(']')
        r.end_span()
    #@+node:ekr.20150722204300.79: *4* rt.ListComp
    def do_ListComp(self, node):
        r = self
        # return [
            # r.span("listcomp", [
                # '[',
                # r.visit(node.elt) if node.elt else '',
                # r.keyword('for', leading=True),
                # r.span('item', [
                    # r.visit(node.elt),
                # ]),
                # r.span('ifgenerators', [
                    # r.visit_list(node.generators),
                # ]),
                # "]",
            # ]),
        # ]
        r.span("listcomp")
        r.gen('[')
        if node.elt:
            r.visit(node.elt)
        r.keyword('for', leading=True),
        if node.elt:
            r.span_node('item', node.elt)
        r.span('ifgenerators')
        r.visit_list(node.generators)
        r.gen("]")
        r.end_span() # ifgenerators
        r.end_span() # listcomp

    #@+node:ekr.20150722204300.80: *4* rt.Module
    def do_Module(self, node):
        r = self
        #
        # return [
            # r.doc(node, "module"),
            # r.visit_list(node.body),
        # ]
        r.doc(node, "module"),
        r.visit_list(node.body),
    #@+node:ekr.20150722204300.81: *4* rt.Name
    def do_Name(self, node):
        r = self
        ###
        # return [
            # r.span('name', [
                # node.id,
                # r.stc_popup_attrs(node),
            # ]),
        # ]
        r.span('name')
        r.gen(node.id)
        r.stc_popup_attrs(node)
        r.end_span()
    #@+node:ekr.20150722204300.82: *4* rt.Num
    def do_Num(self, node):
        r = self
        r.gen(r.text(repr(node.n)))
    #@+node:ekr.20150722204300.83: *4* rt.Pass
    def do_Pass(self, node):
        r = self
        return r.simple_statement('pass')
    #@+node:ekr.20150722204300.84: *4* rt.Print
    # Print(expr? dest, expr* values, bool nl)

    def do_Print(self, node):
        r = self
        # return [
            # r.div('print nowrap', [
                # r.keyword("print"),
                # "(",
                # node.dest and '>>\n%s,\n' % r.visit(node.dest),
                # r.visit_list(node.values, sep=',\n'),
                # not node.nl and "newline=False",
                # ")",
            # ]),
        # ]
        r.div('print nowrap')
        r.keyword("print")
        r.gen('(')
        if node.dest:
            r.gen('>>\n')
            r.visit(node.dest)
            r.comma()
            r.newline()
            if node.values:
                for z in node.values:
                    r.visit(z)
                    r.comma()
                    r.newline()
                self.clean('\n')
                self.clean(',')
            ### not node.nl and "newline=False",
        r.gen(')')
        r.end_div() # print
    #@+node:ekr.20150722204300.85: *4* rt.Raise
    def do_Raise(self, node):
        r = self
        # aList = []
        # for attr in ('type', 'inst', 'tback'):
            # attr = getattr(node, attr, None)
            # if attr is not None:
                # aList.append(r.visit(attr))
        # return [
            # r.div('raise nowrap', [
                # r.keyword("raise"),
                # aList,
            # ]),
        # ]
        r.div('raise nowrap')
        r.keyword("raise")
        for attr in ('type', 'inst', 'tback'):
            attr = getattr(node, attr, None)
            if attr is not None:
                r.visit(attr) ####
        r.end_div() # raise
    #@+node:ekr.20150722204300.86: *4* rt.Return
    def do_Return(self, node):
        r = self
        # return [
            # r.div('return nowrap', [
                # r.keyword("return"),
                # node.value and r.visit(node.value),
            # ]),
        # ]
        r.div('return nowrap')
        r.keyword("return")
        if node.value:
            r.visit(node.value)
        r.end_div()
    #@+node:ekr.20150722204300.87: *4* rt.Slice
    def do_Slice(self, node):
        r = self
        # return [
            # r.span("slice", [
                # node.lower and r.visit(node.lower),
                # ":",
                # node.upper and r.visit(node.upper),
                # [':', r.visit(node.step)] if node.step else None,
            # ]),
        # ]
        r.span("slice")
        if node.lower:
            r.visit(node.lower)
        self.colon()
        if node.upper:
            r.visit(node.upper)
        if node.step:
            self.colon()
            r.visit(node.step)
        r.end_span()
    #@+node:ekr.20150722204300.88: *4* rt.Str
    def do_Str(self, node):
        '''This represents a string constant.'''
        r = self
        assert isinstance(node.s, (str, unicode))
        # return [
            # r.span("str", [
                # r.text(repr(node.s)), ### repr??
            # ]),
        # ]
        r.span("str")
        r.gen(r.text(repr(node.s))) ### repr??
        r.end_span()
    #@+node:ekr.20150722204300.89: *4* rt.Subscript
    def do_Subscript(self, node):
        r = self
        ###
        # return [
            # r.span("subscript", [
                # r.visit(node.value),
                # '[',
                # r.visit(node.slice),
                # ']',
            # ]),
        # ]
        r.span("subscript")
        r.visit(node.value)
        r.gen('[')
        r.visit(node.slice)
        g.gen(']')
        r.end_span() # subscript
    #@+node:ekr.20150722204300.90: *4* rt.TryExcept
    def do_TryExcept(self, node):
        r = self
        ###
        # orelse = node.orelse and [
            # r.div(None, [
                # r.keyword("else", trailing=False),
                # ':', # '\n',
            # ]),
            # r.div('body nowrap', [
                # r.visit_list(node.orelse),
            # ]),
        # ]
        # return [
            # r.div('tryexcept nowrap', [
                # r.div(None, [
                    # r.keyword("try", trailing=False),
                    # ':', # '\n',
                # ]),
                # r.div('body nowrap', [
                    # r.visit_list(node.body),
                # ]),
                # r.div('body nowrap', [
                    # orelse,
                # ]),
                # node.handlers and r.visit_list(node.handlers),
            # ]),
        # ]
        r.div('tryexcept nowrap')
        r.div_keyword_colon(None, 'try')
        r.div_list('body nowrap', node.body)
        if node.orelse:
            r.div_keyword_colon(None, 'else')
            r.div_body(node.orelse)
        r.div_body(node.handlers)
        r.end_div() # tryexcept
    #@+node:ekr.20150722204300.91: *4* rt.TryFinally
    def do_TryFinally(self, node):
        r = self
        # return [
            # r.div('tryfinally nowrap', [
                # r.div(None, [
                    # r.keyword("try", trailing=False),
                    # ':', # '\n',
                # ]),
                # r.div('body nowrap', [
                    # r.visit_list(node.body),
                # ]),
                # r.div(None, [
                    # r.keyword("finally", trailing=False),
                    # ':', # '\n',
                # ]),
                # r.div('body nowrap', [
                    # node.finalbody and r.visit_list(node.finalbody),
                # ]),
            # ]),
        # ]
        r.div('tryfinally nowrap')
        r.div_keyword_colon(None, 'try')
        r.div_body(node.body)
        r.div_keyword_colon(None, 'finally')
        r.div_body(node.final.body)
        r.end_div() # tryfinally
    #@+node:ekr.20150722204300.92: *4* rt.Tuple
    # Tuple(expr* elts, expr_context ctx)

    def do_Tuple(self, node):
        r = self
        ###
        # return [
            # r.span("tuple", [
                # '(',
                # node.elts and r.visit_list(node.elts, sep=','),
                # ')',
            # ]),
        # ]
        r.span("tuple")
        r.op('(')
        for z in node.elts or []:
            r.visit(node.elts)
            r.comma()
        r.clean(',')
        r.op(')')
        r.end_span()
    #@+node:ekr.20150722204300.93: *4* rt.UnaryOp
    def do_UnaryOp(self, node):
        r = self
        ###
        # op_name = r.op_name(node.op)
        # return [
            # r.span(op_name.strip(), [
                # r.op(op_name, trailing=False),
                # r.visit(node.operand),
            # ]),
        # ]
        op_name = r.op_name(node.op)
        r.span(op_name.strip())
        r.op(op_name, trailing=False)
        r.visit(node.operand)
        r.end_span()
    #@+node:ekr.20150722204300.94: *4* rt.While
    def do_While(self, node):
        r = self
        ###
        # orelse = node.orelse and [
            # r.div(None, [
                # r.keyword("else", trailing=False),
                # ':', # '\n',
            # ]),
            # r.div('body nowrap', [
                # r.visit_list(node.orelse),
            # ]),
        # ]
        # return [
            # r.div('while nowrap', [
                # r.div(None, [
                    # r.keyword("while"),
                    # r.visit(node.test),
                    # ':', # '\n',
                # ]),
                # r.div('body nowrap', [
                    # r.visit_list(node.body),
                # ]),
                # orelse,
            # ]),
        # ]
        r.div('while nowrap')
        r.div(None)
        r.keyword("while"),
        r.visit(node.test),
        r.colon()
        r.end_div() # None
        r.div_list('body nowrap', node.body)
        if node.orelse:
            r.div_keyword_colon(None, 'else')
            r.div_body(node.orelse)
        r.end_div() # while
       
    #@+node:ekr.20150722204300.95: *4* rt.With
    # With(expr context_expr, expr? optional_vars, stmt* body)

    def do_With(self, node):
        r = self
        ###
        # context_expr = getattr(node, 'context_expr', None)
        # optional_vars = getattr(node, 'optional_vars', None)
        # optional_vars = optional_vars and [
            # r.keyword('as', leading=True),
            # r.visit(optional_vars),
        # ]
        # return [
            # r.div('with nowrap', [
                # r.div(None, [
                    # r.keyword('with'),
                    # context_expr and r.visit(context_expr),
                    # optional_vars,
                    # ":",
                # ]),
                # r.div('body nowrap', [
                    # r.visit_list(node.body),
                # ]),
            # ]),
        # ]
        context_expr = getattr(node, 'context_expr', None)
        optional_vars = getattr(node, 'optional_vars', None)
        r.div('with nowrap')
        r.div(None)
        r.keyword('with')
        if context_expr:
            r.visit(context_expr)
        if optional_vars:
            r.keyword('as', leading=True)
            r.visit_list(optional_vars)
        r.colon()
        r.end_div() # None
        r.div_body(node.body)
        r.end_div() # with
    #@+node:ekr.20150722204300.96: *4* rt.Yield
    def do_Yield(self, node):
        r = self
        ###
        # return [
            # r.div('yield nowrap', [
                # r.keyword("yield"),
                # r.visit(node.value),
            # ]),
        # ]
        r.div('yield nowrap')
        r.keyword('yield')
        r.visit(node.value)
        r.end_div()
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo

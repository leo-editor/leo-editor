# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20150605175037.1: * @file leoCheck.py
#@@first
'''Experimental code checking for Leo.'''
# To do:
# - Option to ignore defs without args if all calls have no args.
# * explain typical entries
import leo.core.leoGlobals as g
import leo.core.leoAst as leoAst
import ast
import glob
import imp
import re
    # Used only in the disused prototype code.
import time
#@+others
#@+node:ekr.20171207095816.1: ** class ConventionChecker
class ConventionChecker (object):
    '''
    A prototype of an extensible convention-checking tool.
    See: https://github.com/leo-editor/leo-editor/issues/632
    
    Here is the body of @button check-conventions:
    
        g.cls()
        if c.changed: c.save()
        
        import imp
        import leo.core.leoCheck as leoCheck
        imp.reload(leoCheck)
        
        fn = g.os_path_finalize_join(g.app.loadDir, '..', 'plugins', 'nodetags.py')
        leoCheck.ConventionChecker(c).check(fn=fn)
    '''
    
    patterns = []
        # Set below.
    
    def __init__(self, c):
        self.c = c
        self.class_name = None
        self.classes = self.init_classes()
            # Rudimentary symbol tables.
        self.enable_trace = True
        self.file_name = None
            # Set in show().
        self.pass_n = 0

    #@+others
    #@+node:ekr.20171207100432.1: *3* checker.check & helper
    def check(self, fn=None, s=None):
        '''Check the contents of fn or the string s.'''
        # Get the source.
        if fn:
            sfn = g.shortFileName(fn)
            if g.os_path_exists(fn):
                s, e = g.readFileIntoString(fn)
                if s:
                    s = g.toEncodedString(s, encoding=e)
                else:
                    return g.trace('empty file:', sfn)
            else:
                return g.trace('file not found:', sfn)
        elif s:
            sfn = '<string>'
        else:
            return g.trace('no fn or s argument')
        # Check the source
        t1 = time.clock()
        node = ast.parse(s, filename='before', mode='exec')
        self.check_helper(fn=sfn, node=node)
        t2 = time.clock()
        g.trace('done: %4.2f sec. %s' % ((t2-t1), sfn))
    #@+node:ekr.20171207101337.1: *4* checker.check_helper
    def check_helper(self, fn, node):
        trace = True and self.enable_trace
        self.file_name = fn
        dispatch = {
            'call':     self.do_call,
            'class':    self.do_class,
            'def':      self.do_def,
            'self.x=':  self.do_assn_to_self,
            'c.x=':     self.do_assn_to_c,
        }
        s1 = leoAst.AstFormatter().format(node)
        for n in (1, 2):
            self.class_name = None
            self.pass_n = n
            if trace: print('===== pass: %s' % n)
            for s in g.splitLines(s1):
                for kind, pattern in self.patterns:
                    m = pattern.match(s)
                    if m:
                        f = dispatch.get(kind)
                        f(kind, m, s)
            self.start_class()
        self.end_program()
    #@+node:ekr.20171209065852.1: *3* checker_check_signature & helper
    def check_signature(self, func, args, signature):
        
        trace = True and self.enable_trace
        if trace: g.trace('%s(%s) ==> %s' % (func, args, signature))
        if signature[0] == 'self':
            signature = signature[1:]
        for i, arg in enumerate(args):
            if i < len(signature):
                self.check_arg(arg, signature[i])
            elif trace:
                g.trace('possible extra arg', arg)
        if len(args) > len(signature):
            if trace:
                g.trace('possible missing args', signature[len(args)-1:])
                
    def check_arg(self, call_arg, sig_arg):
        
        trace = True and self.enable_trace
        if trace: g.trace('CHECK', call_arg, sig_arg)
    #@+node:ekr.20171208090003.1: *3* checker.do_*
    # These could be called string-oriented visitors.
    #@+node:ekr.20171209063559.1: *4* checker.do_assn_to_c
    assign_to_c_pattern = ('c.x=',  re.compile(r'^\s*c\.([\w.]+)\s*=(.*)'))
    patterns.append(assign_to_c_pattern)

    def do_assn_to_c(self, kind, m, s):
        
        trace = True and self.enable_trace
        if self.pass_n == 1:
            ivar = m.group(1)
            val = m.group(2).strip()
            # Resolve val, if possible.
            if self.class_name:
                context = self.Type('class', self.class_name)
            else:
                context = self.Type('module', self.file_name)
            val = self.resolve(val, context, trace=False)
            d = self.classes.get('Commands')
            assert d
            ivars = d.get('ivars')
            ivars[ivar] = val
            d['ivars'] = ivars
        if trace:
            print('%14s: %s' % (kind, s.strip()))

    #@+node:ekr.20171209063559.2: *4* checker.do_assn_to_self
    assn_to_self_pattern = ('self.x=', re.compile(r'^\s*self\.(\w+)\s*=(.*)'))
    patterns.append(assn_to_self_pattern)

    def do_assn_to_self(self, kind, m, s):
        trace = True and self.enable_trace
        assert self.class_name
        if trace:
            print('%14s: %s' % (kind, s.strip()))
        if self.pass_n == 1:
            ivar = m.group(1)
            val = m.group(2).strip()
            d = self.classes.get(self.class_name)
            assert d is not None, self.class_name
            ivars = d.get('ivars')
            ivars[ivar] = val
            d['ivars'] = ivars
            if trace:
                g.trace(self.class_name, ivar, val)
                g.printDict(d)
    #@+node:ekr.20171209063559.3: *4* checker.do_call
    call_pattern = ('call',  re.compile(r'^\s*(\w+(\.\w+)*)\s*\((.*)\)'))
    patterns.append(call_pattern)

    ignore = ('dict', 'enumerate', 'list', 'tuple')
        # Things that look like function calls.

    def do_call(self, kind, m, s):
        trace = True and self.enable_trace
        if trace: print('%14s: %s' % (kind, s.strip()))
        if self.pass_n == 1:
            return
        try:
            call = m.group(1)
            trace = not any([call.startswith(z) for z in self.ignore])
        except IndexError:
            pass # No m.group(1)
        obj = self.resolve_call(kind, m, s)
        if obj and obj.kind == 'instance':
            m = self.call_pattern.match(s.strip())
            chain = m.group(1).split('.')
            func = chain[-1]
            args = m.group(3).split(',')
            instance = self.classes.get(obj.name)
            if instance:
                d = instance.get('methods')
                signature = d.get(func)
                if signature:
                    signature = signature.split(',')
                    self.check_signature(func, args, signature)

    #@+node:ekr.20171209063559.4: *4* checker.do_class
    class_pattern = ('class', re.compile(r'class\s+([a-z_A-Z][a-z_A-Z0-9]*).*:'))
    patterns.append(class_pattern)

    def do_class(self, kind, m, s):
        trace = True and self.enable_trace
        self.start_class(m)
        if trace: print(s.rstrip())

    #@+node:ekr.20171209063559.5: *4* checker.do_def
    def_pattern = ('def', re.compile(r'^\s*def\s+([\w0-9]+)\s*\((.*)\)\s*:'))
    patterns.append(def_pattern)

    def do_def(self, kind, m, s):
        trace = True and self.enable_trace
        if trace: print('%4s%s' % ('', s.strip()))
        # Not quite accurate..
        # if trace: print('')
        if self.class_name and self.pass_n == 1:
            def_name = m.group(1)
            def_args = m.group(2)
            the_class = self.classes[self.class_name]
            methods = the_class.get('methods')
            methods [def_name] = def_args
            
    #@+node:ekr.20171208135642.1: *3* checker.end_program
    def end_program(self):
        
        trace = True and self.enable_trace
        if trace:
            # print('')
            print('----- END OF PROGRAM')
            for key, val in sorted(self.classes.items()):
                print('class %s' % key)
                g.printDict(val)
    #@+node:ekr.20171209044610.1: *3* checker.init_classes
    def init_classes(self):
        '''
        Init the symbol tables with known classes.
        '''
        
        return {
            # Pre-enter known classes.
            'Commands': {
                'ivars': {
                    'p': self.Type('instance', 'Position'),
                },
                'methods': {},
            },
            'Position': {
                'ivars': {
                    'v': self.Type('instance', 'Vnode'),
                    'h': self.Type('instance', 'String'),
                },
                'methods': {},
            },
            'Vnode': {
                'ivars': {
                    'h': self.Type('instance', 'String'),
                    # Vnode has no v instance!
                },
                'methods': {},
            },
            'String': {
                'ivars': {},
                'methods': {}, ### Possible?
            },
        }
        
    #@+node:ekr.20171208142646.1: *3* checker.resolve & helpers
    def resolve(self, name, obj, trace=None):
        '''Resolve name in the context of obj.'''
        trace = True and self.enable_trace
        trace_resolve = False
        if trace and trace_resolve:
            g.trace('      ===== name: %s obj: %r' % (name, obj))
        if obj:
            if obj.kind == 'error':
                result = obj
            elif name == 'self':
                assert obj.name, repr(obj)
                result = self.Type('instance', obj.name)
            elif obj.kind == 'class':
                result = self.resolve_class(name, obj)
            elif obj.kind == 'instance':
                result = obj
            else:
                result = self.Type('error', 'unknown kind: %s' % obj.kind)
        else:
            result = self.Type('error', 'unbound name: %s' % name)
        if trace and trace_resolve: g.trace('      ----->', result)
        return result
    #@+node:ekr.20171208134737.1: *4* checker.resolve_call
    call_pattern = re.compile(r'(\w+(\.\w+)*)\s*\((.*)\)')

    def resolve_call(self, kind, m, s):

        trace = True and self.enable_trace
        s = s.strip()
        m = self.call_pattern.match(s)
        aList = m.group(1).split('.')
        chain, func = aList[:-1], aList[-1]
        args = m.group(3).split(',')
        if chain:
            if trace:
                g.trace(' ===== %s.%s(%s)' % (
                    '.'.join(chain), func, ','.join(args)))
            if self.class_name:
                context = self.Type('class', self.class_name)
            else:
                context = self.Type('module', self.file_name)
            result = self.resolve_chain(chain, context)
            if trace:
                g.trace(' ----> %s.%s' % (result, func))
        else:
            result = None
        return result
    #@+node:ekr.20171209034244.1: *4* checker.resolve_chain
    def resolve_chain(self, chain, context):
        
        trace = True and self.enable_trace
        if trace:
            g.trace('=====', chain, context)
        for name in chain:
            context = self.resolve(name, context)
            if trace: g.trace('%s ==> %r' % (name, context))
        if trace:
            g.trace('---->', context)
        return context
    #@+node:ekr.20171208173323.1: *4* checker.resolve_class
    def resolve_class(self, name, obj):
        
        trace = True and self.enable_trace
        class_name = 'Commands' if obj.name == 'c' else obj.name
        the_class = self.classes.get(class_name)
        if not the_class:
            return self.Type('error', 'no class %s' % name)
        if trace:
            g.trace('CLASS DICT', class_name)
            g.printDict(the_class)
        ivars = the_class.get('ivars')
        methods = the_class.get('methods')
        if name == 'self':
            return self.Type('class', class_name)
        elif methods.get(name):
            return self.Type('func', name)
        elif ivars.get(name):
            if trace: g.trace('***** IVAR', name)
            val = ivars.get(name)
            head2 = val.split('.')
            if trace:
                print('')
                g.trace('----- RECURSIVE', head2)
            ### Unbounded recursion.
            ### obj2 = self.type('class', class_name)
            obj2 = None ### Wrong
            for name2 in head2:
                obj2 = self.resolve(name2, obj2)
                if trace: g.trace('result: %r' % obj2)
            if trace:
                print('')
                g.trace('----- END RECURSIVE: %r', obj2)
            return obj2
        else:
            return self.Type('error', 'no member %s' % name)
    #@+node:ekr.20171208111655.1: *3* checker.start_class
    def start_class(self, m=None):
        '''Start a new class, ending the old class.'''
        trace = True and self.enable_trace
        # Trace the old class.
        if trace and self.class_name:
            print('----- END', self.class_name)
            g.printDict(self.classes[self.class_name])
        # Switch classes.
        if m:
            self.class_name = m.group(1)
            if trace: print('===== START', self.class_name)
            if self.pass_n == 1:
                self.classes [self.class_name] = {
                    'ivars': {},
                    'methods': {},
                }
        else:
            self.class_name = None
    #@+node:ekr.20171209030742.1: *3* class Type
    class Type (object):
        '''A class to hold all type-related data.'''

        kinds = ('error', 'class', 'instance', 'module', 'unknown')
        
        def __init__(self, kind, name, source=None, tag=None):

            assert kind in self.kinds, repr(kind)
            self.kind = kind
            self.name=name
            self.source = source
            self.tag = tag
            
        def __repr__(self):

            return '<%s: %s>' % (self.kind, self.name)
    #@-others
#@+node:ekr.20160109173821.1: ** class BindNames
class BindNames(object):
    '''A class that binds all names to objects without traversing any tree.'''

    def __init__(self):
        '''Ctor for BindNames class.'''
        self.module_context = None
        self.context = None
#@+node:ekr.20160109173938.1: *3* bind_all_names
def bind_all_names(self, module_context):
    '''Bind all names in the given module context and in all inner contexts.'''
    self.parent_context = None
    self.module_context = module_context
    self.bind_names(module_context)
#@+node:ekr.20160109174258.1: *3* bind_names
def bind_names(self, context):
    '''Bind all names in the given context and in all inner contexts.'''
    # First, create objects for all names defined in this context.

    # Next, bind names in inner contexts.
    old_parent = self.parent_context
    self.parent_context = context

    # Restore the context.
    self.parent_context = old_parent
#@+node:ekr.20160109102859.1: ** class Context
class Context(object):
    '''
    Context class (NEW)

    Represents a binding context: module, class or def.

    For any Ast context node N, N.cx is a reference to a Context object.
    '''
    #@+others
    #@+node:ekr.20160109103533.1: *3* Context.ctor
    def __init__ (self, fn, kind, name, node, parent_context):
        '''Ctor for Context class.'''
        self.fn = fn
        self.kind = kind
        self.name = name
        self.node = node
        self.parent_context = parent_context
        # Name Data...
        self.defined_names = set()
        self.global_names = set()
        self.imported_names = set()
        self.nonlocal_names = set() # To do.
        self.st = {}
            # Keys are names seen in this context, values are defining contexts.
        self.referenced_names = set()
        # Node lists. Entries are Ast nodes...
        self.inner_contexts_list = []
        self.minor_contexts_list = []
        self.assignments_list = []
        self.calls_list = []
        self.classes_list = []
        self.defs_list = []
        self.expressions_list = []
        self.returns_list = []
        self.statements_list = []
        self.yields_list = []
        # Add this context to the inner context of the parent context.
        if parent_context:
            parent_context.inner_contexts_list.append(self)
    #@+node:ekr.20160109134527.1: *3* Context.define_name
    def define_name(self, name):
        '''Define a name in this context.'''
        self.defined_names.add(name)
        if name in self.referenced_names:
            self.referenced_names.remove(name)
    #@+node:ekr.20160109143040.1: *3* Context.global_name
    def global_name(self, name):
        '''Handle a global name in this context.'''
        self.global_names.add(name)
        # Not yet.
            # Both Python 2 and 3 generate SyntaxWarnings when a name
            # is used before the corresponding global declarations.
            # We can make the same assumpution here:
            # give an *error* if an STE appears in this context for the name.
            # The error indicates that scope resolution will give the wrong result.
            # e = cx.st.d.get(name)
            # if e:
                # self.u.error('name \'%s\' used prior to global declaration' % (name))
                # # Add the name to the global_names set in *this* context.
                # # cx.global_names.add(name)
            # # Regardless of error, bind the name in *this* context,
            # # using the STE from the module context.
            # cx.st.d[name] = module_e
    #@+node:ekr.20160109144139.1: *3* Context.import_name
    def import_name(self, module, name):

        if True and name == '*':
            g.trace('From x import * not ready yet')
        else:
            self.imported_names.add(name)
    #@+node:ekr.20160109145526.1: *3* Context.reference_name
    def reference_name(self, name):

        self.referenced_names.add(name)
    #@-others
#@+node:ekr.20160109185501.1: ** class Obj
#@+node:ekr.20160108105958.1: ** class Pass1 (AstFullTraverser)
class Pass1 (leoAst.AstFullTraverser): # V2

    ''' Pass1 does the following:

    1. Creates Context objects and injects them into the new_cx field of
       ast.Class, ast.FunctionDef and ast.Lambda nodes.

    2. Calls the following Context methods: cx.define/global/import/reference_name.
       These methods update lists used later to bind names to objects.
    '''

    #@+others
    #@+node:ekr.20160108105958.2: *3*  p1.ctor
    def __init__(self, fn):

        # Init the base class.
        leoAst.AstFullTraverser.__init__(self)
        self.fn = fn
        # Abbreviations...
        self.stats = Stats()
        self.u = ProjectUtils()
        self.format = leoAst.AstFormatter.format
        # Present context...
        self.context = None
        self.in_attr = False
            # True: traversing inner parts of an AST.Attribute tree.
        self.module_context = None
        self.parent = None
    #@+node:ekr.20160108105958.3: *3*  p1.run (entry point)
    def run (self,root):

        self.visit(root)
    #@+node:ekr.20160109125654.1: *3*  p1.visit
    def visit(self, node):
        '''Visit a *single* ast node.  Visitors are responsible for visiting children!'''
        assert isinstance(node, ast.AST), node.__class__.__name__
        # Visit the children with the new parent.
        old_parent = self.parent
        self.parent = node
        method_name = 'do_' + node.__class__.__name__
        method = getattr(self, method_name)
        # g.trace(method_name)
        method(node)
        self.parent = old_parent
    #@+node:ekr.20160108105958.11: *3* p1.visitors
    #@+node:ekr.20160109134854.1: *4* Contexts
    #@+node:ekr.20160108105958.8: *5* p1.def_args_helper
    # arguments = (expr* args, identifier? vararg, identifier? kwarg, expr* defaults)

    def def_args_helper (self,cx,node):

        assert self.kind(node) == 'arguments'
        self.visit_list(node.args)
        self.visit_list(node.defaults)
        for field in ('vararg','kwarg'): # node.field is a string.
            name = getattr(node,field,None)
            if name:
                # e = cx.st.define_name(name)
                self.stats.n_param_names += 1
    #@+node:ekr.20160108105958.16: *5* p1.ClassDef
    # ClassDef(identifier name, expr* bases, stmt* body, expr* decorator_list)

    def do_ClassDef (self,node):

        old_cx = self.context
        name = node.name
        # Define the class name in the old context.
        old_cx.define_name(name)
        # Visit bases in the old context.
        # bases = self.visit_list(node.bases)
        new_cx = Context(
            fn=None,
            kind='class',
            name=name,
            node=node,
            parent_context=old_cx)
        setattr(node,'new_cx',new_cx)
        # Visit the body in the new context.
        self.context = new_cx
        self.visit_list(node.body)
        self.context = old_cx
        # Stats.
        old_cx.classes_list.append(new_cx)
    #@+node:ekr.20160108105958.19: *5* p1.FunctionDef
    # 2: FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list)
    # 3: FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list,
    #    expr? returns)

    def do_FunctionDef (self,node):

        # Define the function/method name in the old context.
        old_cx = self.context
        name = node.name
        old_cx.define_name(name)
        # Create the new context.
        new_cx = Context(
            fn=None,
            kind='def',
            name=name,
            node=node,
            parent_context=old_cx)
        setattr(node,'new_cx',new_cx) # Bug fix.
        # Visit in the new context...
        self.context = new_cx
        self.def_args_helper(new_cx,node.args)
        self.visit_list(node.body)
        self.context = old_cx
        # Stats
        old_cx.defs_list.append(new_cx)
    #@+node:ekr.20160108105958.23: *5* p1.Interactive
    def do_Interactive(self,node):

        assert False,'Interactive context not supported'
    #@+node:ekr.20160108105958.24: *5* p1.Lambda
    def do_Lambda (self,node):

        # Synthesize a lambda name in the old context.
        # This name must not conflict with split names of the form name@n.
        old_cx = self.context
        name = 'Lambda@@%s' % self.stats.n_lambdas
        # Define a Context for the 'lambda' variables.
        new_cx = Context(
            fn=None,
            kind='lambda',
            name=name,
            node=node,
            parent_context=old_cx)
        setattr(node,'new_cx',new_cx)
        # Evaluate expression in the new context.
        self.context = new_cx
        self.def_args_helper(new_cx,node.args)
        self.visit(node.body)
        self.context = old_cx
        # Stats...
        self.stats.n_lambdas += 1
    #@+node:ekr.20160108105958.26: *5* p1.Module
    def do_Module (self,node):

        # Not yet: Get the module context from the global dict if possible.
        new_cx = Context(
            fn=self.fn,
            kind='module',
            name=None,
            node=node,
            parent_context=None)
        self.context = new_cx
        self.visit_list(node.body)
        self.context = None
    #@+node:ekr.20160109135022.1: *4* Expressions
    #@+node:ekr.20160108105958.13: *5* p1.Attribute (Revise)
    # Attribute(expr value, identifier attr, expr_context ctx)

    def do_Attribute(self,node):

        # Visit...
        # cx = self.context
        old_attr, self.in_attr = self.in_attr, True
        # ctx = self.kind(node.ctx)
        self.visit(node.value)
        # self.visit(node.ctx)
        self.in_attr = old_attr
        if not self.in_attr:
            base_node = node
            kind = self.kind(base_node)
            if kind in ('Builtin','Name'):
                # base_name = base_node.id
                pass
            elif kind in ('Dict','List','Num','Str','Tuple',):
                pass
            elif kind in ('BinOp','UnaryOp'):
                pass
            else:
                assert False,kind
        # Stats...
        self.stats.n_attributes += 1
    #@+node:ekr.20160108105958.17: *5* p1.Expr
    # Expr(expr value)

    def do_Expr(self,node):

        # Visit...
        cx = self.context
        self.visit(node.value)
        # Stats...
        self.stats.n_expressions += 1
        cx.expressions_list.append(node)
        cx.statements_list.append(node)
    #@+node:ekr.20160108105958.27: *5* p1.Name (REWRITE)
    def do_Name(self,node):

        trace = False
        cx  = self.context
        ctx = self.kind(node.ctx)
        name = node.id
        # def_flag,ref_flag=False,False

        if ctx in ('AugLoad','AugStore','Load'):
            # Note: AugStore does *not* define the symbol.
            cx.reference_name(name)
            self.stats.n_load_names += 1
        elif ctx == 'Store':
            # if name not in cx.global_names:
            if trace: g.trace('Store: %s in %s' % (name,cx))
            self.stats.n_store_names += 1
        elif ctx == 'Param':
            if trace: g.trace('Param: %s in %s' % (name,cx))
            self.stats.n_param_refs += 1
        else:
            assert ctx == 'Del',ctx
            self.stats.n_del_names += 1
    #@+node:ekr.20160109140648.1: *4* Imports
    #@+node:ekr.20160108105958.21: *5* p1.Import
    #@+at From Guido:
    # 
    # import x            -->  x = __import__('x')
    # import x as y       -->  y = __import__('x')
    # import x.y.z        -->  x = __import__('x.y.z')
    # import x.y.z as p   -->  p = __import__('x.y.z').y.z
    #@@c

    def do_Import(self,node):
        '''
        Add the imported file to u.files_list if needed
        and create a context for the file.'''
        cx = self.context
        cx.statements_list.append(node)
        # e_list, names = [],[]
        for fn,asname in self.get_import_names(node):
            self.resolve_import_name(fn)
            # Not yet.
            # # Important: do *not* analyze modules not in the files list.
            # if fn2:
                # mname = self.u.module_name(fn2)
                # if g.shortFileName(fn2) in self.u.files_list:
                    # if mname not in self.u.module_names:
                        # self.u.module_names.append(mname)
                # # if trace: g.trace('%s as %s' % (mname,asname))
                # def_name = asname or mname
                # names.append(def_name)
                # e = cx.st.define_name(def_name) # sets e.defined.
                # cx.imported_symbols_list.append(def_name)
                # if trace: g.trace('define: (Import) %10s in %s' % (def_name,cx))
                # e_list.append(e)

                # # Add the constant type to the list of types for the *variable*.
                # mod_cx = self.u.modules_dict.get(fn2) or LibraryModuleContext(self.u,fn2)
                # e.types_cache[''] = mod_cx.module_type
                # # self.u.stats.n_imports += 1
            # else:
                # if trace: g.trace('can not resolve %s in %s' % (fn,cx))

        # for e in e_list:
            # e.defs_list.append(node)
            # e.refs_list.append(node)
    #@+node:ekr.20160108105958.22: *5* p1.ImportFrom
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
        '''
        Add the imported file to u.files_list if needed
        and add the imported symbols to the *present* context.
        '''
        cx = self.context
        cx.statements_list.append(node)
        self.resolve_import_name(node.module)
        for fn,asname in self.get_import_names(node):
            fn2 = asname or fn
            cx.import_name(fn2)
    #@+node:ekr.20160108105958.9: *5* p1.get_import_names
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
    #@+node:ekr.20160108105958.10: *5* p1.resolve_import_name
    def resolve_import_name (self,spec):
        '''Return the full path name corresponding to the import spec.'''
        trace = False ; verbose = False
        if not spec:
            if trace: g.trace('no spec')
            return ''
        # This may not work for leading dots.
        aList,path,paths = spec.split('.'),None,None
        name = 'no name'
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
                    name,paths,self.context))
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
    #@+node:ekr.20160108105958.29: *4* Operators... To be deleted???
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
    #@+node:ekr.20160109134929.1: *4* Minor contexts
    #@+node:ekr.20160109130719.1: *5* p1.comprehension (to do)
    # comprehension (expr target, expr iter, expr* ifs)

    def do_comprehension(self, node):

        # Visit...
        self.visit(node.target) # A name.
        self.visit(node.iter) # An attribute.
        for z in node.ifs:
            self.visit(z)
    #@+node:ekr.20160108105958.18: *5* p1.For
    # For(expr target, expr iter, stmt* body, stmt* orelse)

    def do_For(self,node):

        # Visit...
        cx = self.context
        self.visit(node.target)
        self.visit(node.iter)
        for z in node.body:
            self.visit(z)
        for z in node.orelse:
            self.visit(z)
        # Stats...
        self.stats.n_fors += 1
        cx.statements_list.append(node)
        cx.assignments_list.append(node)
    #@+node:ekr.20160108105958.30: *5* p1.With
    def do_With(self,node):

        # Visit...
        cx = self.context
        self.visit(node.context_expr)
        if node.optional_vars:
            self.visit(node.optional_vars)
        for z in node.body:
            self.visit(z)
        # Stats...
        self.stats.n_withs += 1
        cx.statements_list.append(node)
    #@+node:ekr.20160109135003.1: *4* Statements
    #@+node:ekr.20160108105958.12: *5* p1.Assign
    def do_Assign(self,node):

        # Visit...
        for z in node.targets:
            self.visit(z)
        self.visit(node.value)
        # Stats...
        cx = self.context
        self.stats.n_assignments += 1
        cx.assignments_list.append(node)
        cx.statements_list.append(node)
    #@+node:ekr.20160108105958.14: *5* p1.AugAssign
    # AugAssign(expr target, operator op, expr value)

    def do_AugAssign(self,node):

        # Visit...
        self.visit(node.target)
        self.visit(node.value)
        # Stats...
        cx = self.context
        self.stats.n_assignments += 1
        cx.assignments_list.append(node)
        cx.statements_list.append(node)
    #@+node:ekr.20160108105958.15: *5* p1.Call
    # Call(expr func, expr* args, keyword* keywords, expr? starargs, expr? kwargs)

    def do_Call(self,node):

        # Visit...
        self.visit(node.func)
        for z in node.args:
            self.visit(z)
        for z in node.keywords:
            self.visit(z)
        if getattr(node, 'starargs', None):
            self.visit(node.starargs)
        if getattr(node, 'kwargs', None):
            self.visit(node.kwargs)
        # Stats...
        cx = self.context
        self.stats.n_calls += 1
        cx.calls_list.append(node)
    #@+node:ekr.20160108105958.20: *5* p1.Global
    def do_Global(self,node):

        # Visit
        cx = self.context
        for name in node.names:
            cx.global_name(name)
        # Stats...
        cx.statements_list.append(node)
        self.stats.n_globals += 1
    #@+node:ekr.20160108105958.28: *5* p1.Return
    def do_Return(self,node):

        # Visit...
        if node.value:
            self.visit(node.value)
        # Stats...
        self.stats.n_returns += 1
        cx = self.context
        cx.returns_list.append(node)
        cx.statements_list.append(node)
    #@-others
#@+node:ekr.20150525123715.1: ** class ProjectUtils
class ProjectUtils(object):
    '''A class to compute the files in a project.'''
    # To do: get project info from @data nodes.
    #@+others
    #@+node:ekr.20150525123715.2: *3* pu.files_in_dir
    def files_in_dir(self, theDir, recursive=True, extList=None, excludeDirs=None):
        '''
        Return a list of all Python files in the directory.
        Include all descendants if recursiveFlag is True.
        Include all file types if extList is None.
        '''
        import glob
        import os
        # if extList is None: extList = ['.py']
        if excludeDirs is None: excludeDirs = []
        result = []
        if recursive:
            for root, dirs, files in os.walk(theDir):
                for z in files:
                    fn = g.os_path_finalize_join(root, z)
                    junk, ext = g.os_path_splitext(fn)
                    if not extList or ext in extList:
                        result.append(fn)
                if excludeDirs and dirs:
                    for z in dirs:
                        if z in excludeDirs:
                            dirs.remove(z)
        else:
            for ext in extList:
                result.extend(glob.glob('%s.*%s' % (theDir, ext)))
        return sorted(list(set(result)))
    #@+node:ekr.20150525123715.3: *3* pu.get_project_directory
    def get_project_directory(self, name):
        # Ignore everything after the first space.
        i = name.find(' ')
        if i > -1:
            name = name[: i].strip()
        leo_path, junk = g.os_path_split(__file__)
        d = {
            # Change these paths as required for your system.
            'coverage': r'C:\Python26\Lib\site-packages\coverage-3.5b1-py2.6-win32.egg\coverage',
            'leo': r'C:\leo.repo\leo-editor\leo\core',
            'lib2to3': r'C:\Python26\Lib\lib2to3',
            'pylint': r'C:\Python26\Lib\site-packages\pylint',
            'rope': r'C:\Python26\Lib\site-packages\rope-0.9.4-py2.6.egg\rope\base',
            'test': g.os_path_finalize_join(g.app.loadDir, '..', 'test-proj'),
        }
        dir_ = d.get(name.lower())
        # g.trace(name,dir_)
        if not dir_:
            g.trace('bad project name: %s' % (name))
        if not g.os_path_exists(dir_):
            g.trace('directory not found:' % (dir_))
        return dir_ or ''
    #@+node:ekr.20150525123715.4: *3* pu.project_files
    def project_files(self, name, force_all=False):
        '''Return a list of all files in the named project.'''
        # Ignore everything after the first space.
        i = name.find(' ')
        if i > -1:
            name = name[: i].strip()
        leo_path, junk = g.os_path_split(__file__)
        d = {
            # Change these paths as required for your system.
            'coverage': (
                r'C:\Python26\Lib\site-packages\coverage-3.5b1-py2.6-win32.egg\coverage',
                ['.py'], ['.bzr', 'htmlfiles']),
            'leo': (
                r'C:\leo.repo\leo-editor\leo\core',
                ['.py'], ['.git']), # ['.bzr']
            'lib2to3': (
                r'C:\Python26\Lib\lib2to3',
                ['.py'], ['tests']),
            'pylint': (
                r'C:\Python26\Lib\site-packages\pylint',
                ['.py'], ['.bzr', 'test']),
            'rope': (
                r'C:\Python26\Lib\site-packages\rope-0.9.4-py2.6.egg\rope\base', ['.py'], ['.bzr']),
            # 'test': (
                # g.os_path_finalize_join(leo_path,'test-proj'),
                # ['.py'],['.bzr']),
        }
        data = d.get(name.lower())
        if not data:
            g.trace('bad project name: %s' % (name))
            return []
        theDir, extList, excludeDirs = data
        files = self.files_in_dir(theDir, recursive=True, extList=extList, excludeDirs=excludeDirs)
        if files:
            if name.lower() == 'leo':
                for exclude in ['__init__.py', 'format-code.py']:
                    files = [z for z in files if not z.endswith(exclude)]
                table = (
                    r'C:\leo.repo\leo-editor\leo\commands',
                    # r'C:\leo.repo\leo-editor\leo\plugins\importers',
                    # r'C:\leo.repo\leo-editor\leo\plugins\writers',
                )
                for dir_ in table:
                    files2 = self.files_in_dir(dir_, recursive=True, extList=['.py',], excludeDirs=[])
                    files2 = [z for z in files2 if not z.endswith('__init__.py')]
                    # g.trace(g.os_path_exists(dir_), dir_, '\n'.join(files2))
                    files.extend(files2)
                files.extend(glob.glob(r'C:\leo.repo\leo-editor\leo\plugins\qt_*.py'))
                fn = g.os_path_finalize_join(theDir, '..', 'plugins', 'qtGui.py')
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
    #@-others
#@+node:ekr.20150604164113.1: ** class ShowData
class ShowData(object):
    '''The driver class for analysis project.'''
    #@+others
    #@+node:ekr.20150604165500.1: *3*  ctor
    def __init__(self, c):
        '''Ctor for ShowData controller class.'''
        self.c = c
        self.files = None
        # Data.
        self.assigns_d = {}
        self.calls_d = {}
        self.classes_d = {}
        self.context_stack = []
        self.defs_d = {}
        self.returns_d = {}
        # Statistics
        self.n_matches = 0
        self.n_undefined_calls = 0
        self.tot_lines = 0
        self.tot_s = 0
    #@+node:ekr.20150604163903.1: *3* run & helpers
    def run(self, files):
        '''Process all files'''
        self.files = files
        t1 = time.time()
        for fn in files:
            s, e = g.readFileIntoString(fn)
            if s:
                self.tot_s += len(s)
                g.trace('%8s %s' % ("{:,}".format(len(s)), g.shortFileName(fn)))
                    # Print len(s), with commas.
                # Fast, accurate:
                # 1.9 sec for parsing.
                # 2.5 sec for Null AstFullTraverer traversal.
                # 2.7 sec to generate all strings.
                # 3.8 sec to generate all reports.
                s1 = g.toEncodedString(s)
                self.tot_lines += len(g.splitLines(s))
                    # Adds less than 0.1 sec.
                node = ast.parse(s1, filename='before', mode='exec')
                ShowDataTraverser(self, fn).visit(node)
                # elif 0: # Too slow, too clumsy: 3.3 sec for tokenizing
                    # readlines = g.ReadLinesClass(s).next
                    # for token5tuple in tokenize.generate_tokens(readlines):
                        # pass
                # else: # Inaccurate. 2.2 sec to generate all reports.
                    # self.scan(fn, s)
            else:
                g.trace('skipped', g.shortFileName(fn))
        t2 = time.time()
            # Get the time exlusive of print time.
        self.show_results()
        g.trace('done: %4.1f sec.' % (t2 - t1))
    #@+node:ekr.20150605054921.1: *3* scan & helpers (a prototype: no longer used)
    if 0:
        # The excellent prototype code, fast, easy but inaccurate.
        # It was a roadmap for the ShowDataTraverser class.

        # Regex patterns (were defined in the ctor)
        r_class = r'class[ \t]+([a-z_A-Z][a-z_A-Z0-9]*).*:'
        r_def = r'def[ \t]+([a-z_A-Z][a-z_A-Z0-9]*)[ \t]*\((.*)\)'
        r_return = r'(return[ \t].*)$'
        r_call = r'([a-z_A-Z][a-z_A-Z0-9]*)[ \t]*\(([^)]*)\)'
        r_all = re.compile('|'.join([r_class, r_def, r_return, r_call,]))

        def scan(self, fn, s):
            lines = g.splitLines(s)
            self.tot_lines += len(lines)
            for i, s in enumerate(lines):
                m = re.search(self.r_all, s)
                if m and not s.startswith('@'):
                    self.match(fn, i, m, s)
    #@+node:ekr.20150605063318.1: *4* match
    def match(self, fn, i, m, s):
        '''Handle the next match.'''
        trace = False
        self.n_matches += 1
        indent = g.skip_ws(s, 0)
        # Update the context and enter data.
        if g.match_word(s, indent, 'def'):
            self.update_context(fn, indent, 'def', s)
            for i, name in enumerate(m.groups()):
                if name:
                    aList = self.defs_d.get(name, [])
                    def_tuple = self.context_stack[: -1], s
                    aList.append(def_tuple)
                    self.defs_d[name] = aList
                    break
        elif g.match_word(s, indent, 'class'):
            self.update_context(fn, indent, 'class', s)
            for i, name in enumerate(m.groups()):
                if name:
                    aList = self.classes_d.get(name, [])
                    class_tuple = self.context_stack[: -1], s
                    aList.append(class_tuple)
                    self.classes_d[name] = aList
        elif s.find('return') > -1:
            context, name = self.context_names()
            j = s.find('#')
            if j > -1: s = s[: j]
            s = s.strip()
            if s:
                aList = self.returns_d.get(name, [])
                return_tuple = context, s
                aList.append(return_tuple)
                self.returns_d[name] = aList
        else:
            # A call.
            for i, name in enumerate(m.groups()):
                if name:
                    context2, context1 = self.context_names()
                    j = s.find('#')
                    if j > -1:
                        s = s[: j]
                    s = s.strip().strip(',').strip()
                    if s:
                        aList = self.calls_d.get(name, [])
                        call_tuple = context2, context1, s
                        aList.append(call_tuple)
                        self.calls_d[name] = aList
                    break
        if trace:
            print('%4s %4s %3s %3s %s' % (
                self.n_matches, i, len(self.context_stack), indent, s.rstrip()))
    #@+node:ekr.20150605074749.1: *4* update_context
    def update_context(self, fn, indent, kind, s):
        '''Update context info when a class or def is seen.'''
        trace = False and self.n_matches < 100
        while self.context_stack:
            fn2, kind2, indent2, s2 = self.context_stack[-1]
            if indent <= indent2:
                self.context_stack.pop()
                if trace:
                    g.trace('pop ', len(self.context_stack), indent, indent2, kind2)
            else:
                break
        context_tuple = fn, kind, indent, s
        self.context_stack.append(context_tuple)
        if trace:
            g.trace('push', len(self.context_stack), s.rstrip())
        self.context_indent = indent
    #@+node:ekr.20150604164546.1: *3* show_results & helpers
    def show_results(self):
        '''Print a summary of the test results.'''
        make = True
        multiple_only = False # True only show defs defined in more than one place.
        c = self.c
        result = ['@killcolor\n']
        for name in sorted(self.defs_d):
            aList = self.defs_d.get(name, [])
            if len(aList) > 1 or not multiple_only: # not name.startswith('__') and (
                self.show_defs(name, result)
                self.show_calls(name, result)
                self.show_returns(name, result)
        self.show_undefined_calls(result)
        # Put the result in a new node.
        summary = 'files: %s lines: %s chars: %s classes: %s\ndefs: %s calls: %s undefined calls: %s returns: %s' % (
            # g.plural(self.files),
            len(self.files),
            "{:,}".format(self.tot_lines),
            "{:,}".format(self.tot_s),
            "{:,}".format(len(self.classes_d.keys())),
            "{:,}".format(len(self.defs_d.keys())),
            "{:,}".format(len(self.calls_d.keys())),
            "{:,}".format(self.n_undefined_calls),
            "{:,}".format(len(self.returns_d.keys())),
        )
        result.insert(1, summary)
        result.extend(['', summary])
        if c and make:
            last = c.lastTopLevel()
            p2 = last.insertAfter()
            p2.h = 'global signatures'
            p2.b = '\n'.join(result)
            c.redraw(p=p2)
        print(summary)
    #@+node:ekr.20150605160218.1: *4* show_calls
    def show_calls(self, name, result):
        aList = self.calls_d.get(name, [])
        if not aList:
            return
        result.extend(['', '    %s call%s...' % (len(aList), g.plural(aList))])
        w = 0
        calls = sorted(set(aList))
        for call_tuple in calls:
            context2, context1, s = call_tuple
            w = max(w, len(context2 or '') + len(context1 or ''))
        for call_tuple in calls:
            context2, context1, s = call_tuple
            pad = w - (len(context2 or '') + len(context1 or ''))
            if context2:
                result.append('%s%s::%s: %s' % (
                    ' ' * (8 + pad), context2, context1, s))
            else:
                result.append('%s%s: %s' % (
                    ' ' * (10 + pad), context1, s))
    #@+node:ekr.20150605155601.1: *4* show_defs
    def show_defs(self, name, result):
        aList = self.defs_d.get(name, [])
        name_added = False
        w = 0
        # Calculate the width
        for def_tuple in aList:
            context_stack, s = def_tuple
            if context_stack:
                fn, kind, context_s = context_stack[-1]
                w = max(w, len(context_s))
        for def_tuple in aList:
            context_stack, s = def_tuple
            if not name_added:
                name_added = True
                result.append('\n%s' % name)
                result.append('    %s definition%s...' % (len(aList), g.plural(aList)))
            if context_stack:
                fn, kind, context_s = context_stack[-1]
                def_s = s.strip()
                pad = w - len(context_s)
                result.append('%s%s: %s' % (' ' * (8 + pad), context_s, def_s))
            else:
                result.append('%s%s' % (' ' * 4, s.strip()))
    #@+node:ekr.20150605160341.1: *4* show_returns
    def show_returns(self, name, result):
        aList = self.returns_d.get(name, [])
        if not aList:
            return
        result.extend(['', '    %s return%s...' % (len(aList), g.plural(aList))])
        w, returns = 0, sorted(set(aList))
        for returns_tuple in returns:
            context, s = returns_tuple
            w = max(w, len(context or ''))
        for returns_tuple in returns:
            context, s = returns_tuple
            pad = w - len(context)
            result.append('%s%s: %s' % (' ' * (8 + pad), context, s))
    #@+node:ekr.20150606092147.1: *4* show_undefined_calls
    def show_undefined_calls(self, result):
        '''Show all calls to undefined functions.'''
        # g.trace(sorted(self.defs_d.keys()))
        call_tuples = []
        for s in self.calls_d:
            i = 0
            while True:
                progress = i
                j = s.find('.', i)
                if j == -1:
                    name = s[i:].strip()
                    call_tuple = name, s
                    call_tuples.append(call_tuple)
                    break
                else:
                    i = j + 1
                assert progress < i
        undef = []
        for call_tuple in call_tuples:
            name, s = call_tuple
            if name not in self.defs_d:
                undef.append(call_tuple)
        undef = list(set(undef))
        result.extend(['', '%s undefined call%s...' % (
            len(undef), g.plural(undef))])
        self.n_undefined_calls = len(undef)
        # Merge all the calls for name.
        # There may be several with different s values.
        results_d = {}
        for undef_tuple in undef:
            name, s = undef_tuple
            calls = self.calls_d.get(s, [])
            aList = results_d.get(name, [])
            for call_tuple in calls:
                aList.append(call_tuple)
            results_d[name] = aList
        # Print the final results.
        for name in sorted(results_d):
            calls = results_d.get(name)
            result.extend(['', '%s %s call%s...' % (name, len(calls), g.plural(calls))])
            w = 0
            for call_tuple in calls:
                context2, context1, s = call_tuple
                if context2:
                    w = max(w, 2 + len(context2) + len(context1))
                else:
                    w = max(w, len(context1))
            for call_tuple in calls:
                context2, context1, s = call_tuple
                pad = w - (len(context2) + len(context1))
                if context2:
                    result.append('%s%s::%s: %s' % (
                        ' ' * (2 + pad), context2, context1, s))
                else:
                    result.append('%s%s: %s' % (
                        ' ' * (2 + pad), context1, s))
    #@+node:ekr.20150605140911.1: *3* context_names
    def context_names(self):
        '''Return the present context name.'''
        if self.context_stack:
            result = []
            for stack_i in -1, -2:
                try:
                    fn, kind, indent, s = self.context_stack[stack_i]
                except IndexError:
                    result.append('')
                    break
                s = s.strip()
                assert kind in ('class', 'def'), kind
                i = g.skip_ws(s, 0)
                i += len(kind)
                i = g.skip_ws(s, i)
                j = g.skip_c_id(s, i)
                result.append(s[i: j])
            return reversed(result)
        else:
            return ['', '']
    #@-others
#@+node:ekr.20150606024455.1: ** class ShowDataTraverser
class ShowDataTraverser(leoAst.AstFullTraverser):
    '''
    Add data about classes, defs, returns and calls to controller's
    dictionaries.
    '''

    def __init__(self, controller, fn):
        '''Ctor for ShopDataTraverser class.'''
        leoAst.AstFullTraverser.__init__(self)
        module_tuple = g.shortFileName(fn), 'module', g.shortFileName(fn)
            # fn, kind, s.
        self.context_stack = [module_tuple]
        self.controller = controller
        self.fn = g.shortFileName(fn)
        self.formatter = leoAst.AstFormatter()
            # leoAst.AstPatternFormatter()
        self.trace = False
    #@+others
    #@+node:ekr.20150609053332.1: *3* sd.Helpers
    #@+node:ekr.20150606035006.1: *4* sd.context_names
    def context_names(self):
        '''Return the present context names.'''
        result = []
        n = len(self.context_stack)
        for i in n - 1, n - 2:
            if i >= 0:
                fn, kind, s = self.context_stack[i]
                assert kind in ('class', 'def', 'module'), kind
                if kind == 'module':
                    result.append(s.strip())
                else:
                    # Append the name following the class or def.
                    i = g.skip_ws(s, 0)
                    i += len(kind)
                    i = g.skip_ws(s, i)
                    j = g.skip_c_id(s, i)
                    result.append(s[i: j])
            else:
                result.append('')
                break
        # g.trace(list(reversed(result)))
        return reversed(result)
    #@+node:ekr.20150609053010.1: *4* sd.format
    def format(self, node):
        '''Return the formatted version of an Ast Node.'''
        return self.formatter.format(node).strip()
    #@+node:ekr.20150606024455.62: *3* sd.visit
    def visit(self, node):
        '''
        Visit a *single* ast node. Visitors must visit their children
        explicitly.
        '''
        method = getattr(self, 'do_' + node.__class__.__name__)
        method(node)

    def visit_children(self, node):
        '''Override to ensure this method is never called.'''
        assert False, 'must visit children explicitly'
    #@+node:ekr.20150609052952.1: *3* sd.Visitors
    #@+node:ekr.20150607200422.1: *4* sd.Assign
    def do_Assign(self, node):
        '''Handle an assignment statement: Assign(expr* targets, expr value)'''
        value = self.format(self.visit(node.value))
        assign_tuples = []
        for target in node.targets:
            target = self.format(self.visit(target))
            s = '%s=%s' % (target, value)
            context2, context1 = self.context_names()
            assign_tuple = context2, context1, s
            assign_tuples.append(assign_tuple)
            aList = self.controller.assigns_d.get(target, [])
            aList.extend(assign_tuples)
            self.controller.calls_d[target] = aList
    #@+node:ekr.20150607200439.1: *4* sd.AugAssign
    def do_AugAssign(self, node):
        '''
        Handle an augmented assignement:
        AugAssign(expr target, operator op, expr value).
        '''
        target = self.format(self.visit(node.target))
        s = '%s=%s' % (target, self.format(self.visit(node.value)))
        context2, context1 = self.context_names()
        assign_tuple = context2, context1, s
        aList = self.controller.assigns_d.get(target, [])
        aList.append(assign_tuple)
        self.controller.calls_d[target] = aList
    #@+node:ekr.20150606024455.16: *4* sd.Call
    def do_Call(self, node):
        '''
        Handle a call statement:
        Call(expr func, expr* args, keyword* keywords, expr? starargs, expr? kwargs)
        '''
        # Update data.
        s = self.format(node)
        name = self.format(node.func)
        context2, context1 = self.context_names()
        call_tuple = context2, context1, s
        aList = self.controller.calls_d.get(name, [])
        aList.append(call_tuple)
        self.controller.calls_d[name] = aList
        # Visit.
        self.visit(node.func)
        for z in node.args:
            self.visit(z)
        for z in node.keywords:
            self.visit(z)
        if getattr(node, 'starargs', None):
            self.visit(node.starargs)
        if getattr(node, 'kwargs', None):
            self.visit(node.kwargs)
    #@+node:ekr.20150606024455.3: *4* sd.ClassDef
    def do_ClassDef(self, node):
        '''
        Handle a class defintion:
        ClassDef(identifier name, expr* bases, stmt* body, expr* decorator_list)
        '''
        # Format.
        if node.bases:
            bases = [self.format(z) for z in node.bases]
            s = 'class %s(%s):' % (node.name, ','.join(bases))
        else:
            s = 'class %s:' % node.name
        if self.trace: g.trace(s)
        # Enter the new context.
        context_tuple = self.fn, 'class', s
        self.context_stack.append(context_tuple)
        # Update data.
        class_tuple = self.context_stack[: -1], s
        aList = self.controller.classes_d.get(node.name, [])
        aList.append(class_tuple)
        self.controller.classes_d[node.name] = aList
        # Visit.
        for z in node.bases:
            self.visit(z)
        for z in node.body:
            self.visit(z)
        for z in node.decorator_list:
            self.visit(z)
        # Leave the context.
        self.context_stack.pop()
    #@+node:ekr.20150606024455.4: *4* sd.FunctionDef
    def do_FunctionDef(self, node):
        '''
        Visit a function defintion:
        FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list)
        '''
        # Format.
        args = self.format(node.args) if node.args else ''
        s = 'def %s(%s):' % (node.name, args)
        if self.trace: g.trace(s)
        # Enter the new context.
        context_tuple = self.fn, 'def', s
        self.context_stack.append(context_tuple)
        # Update data.
        def_tuple = self.context_stack[: -1], s
        aList = self.controller.defs_d.get(node.name, [])
        aList.append(def_tuple)
        self.controller.defs_d[node.name] = aList
        # Visit.
        for z in node.decorator_list:
            self.visit(z)
        self.visit(node.args)
        for z in node.body:
            self.visit(z)
        # Leave the context.
        self.context_stack.pop()
    #@+node:ekr.20150606024455.55: *4* sd.Return
    def do_Return(self, node):
        '''Handle a 'return' statement: Return(expr? value)'''
        # Update data.
        s = self.format(node)
        if self.trace: g.trace(s)
        context, name = self.context_names()
        aList = self.controller.returns_d.get(name, [])
        return_tuple = context, s
        aList.append(return_tuple)
        self.controller.returns_d[name] = aList
        # Visit.
        if node.value:
            self.visit(node.value)
    #@-others
#@+node:ekr.20160109150703.1: ** class Stats
class Stats(object):
    '''A class containing global statistics & other data'''
    #@+others
    #@+node:ekr.20160109150703.2: *3*  sd.ctor
    def __init__ (self):

        # Files...
        # self.completed_files = [] # Files handled by do_files.
        # self.failed_files = [] # Files that could not be opened.
        # self.files_list = [] # Files given by user or by import statements.
        # self.module_names = [] # Module names corresponding to file names.

        # Contexts.
        # self.context_list = {}
            # Keys are fully qualified context names; values are contexts.
        # self.modules_dict = {}
            # Keys are full file names; values are ModuleContext's.

        # Statistics...
        # self.n_chains = 0
        self.n_contexts = 0
        # self.n_errors = 0
        self.n_lambdas = 0
        self.n_modules = 0
        # self.n_relinked_pointers = 0
        # self.n_resolvable_names = 0
        # self.n_resolved_contexts = 0
        # self.n_relinked_names = 0

        # Names...
        self.n_attributes = 0
        self.n_expressions = 0
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
    #@+node:ekr.20160109150703.6: *3* sd.print_times
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
    #@+node:ekr.20160109150703.7: *3* sd.print_stats
    def print_stats (self):

        sd = self
        table = (
            '*', 'errors',

            '*Contexts',
            'classes','contexts','defs','modules',

            '*Statements',
            'assignments','calls','fors','globals','imports',
            'lambdas','list_comps','returns','withs',

            '*Names',
            'attributes','del_names','load_names','names',
            'param_names','param_refs','store_names',
            #'resolvable_names','relinked_names','relinked_pointers',
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
    #@-others
#@+node:ekr.20150704135836.1: ** test
def test(c, files):
    r'''
    A stand-alone version of @button show-data.  Call as follows:

        import leo.core.leoCheck as leoCheck
        files = (
            [
                # r'c:\leo.repo\leo-editor\leo\core\leoNodes.py',
            ] or
            leoCheck.ProjectUtils().project_files('leo')
        )
        leoCheck.test(files)
    '''
    # pylint: disable=import-self
    import leo.core.leoCheck as leoCheck
    leoCheck.ShowData(c=c).run(files)
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo

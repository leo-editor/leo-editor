#@+leo-ver=5-thin
#@+node:ekr.20210517152714.1: * @file ../plugins/leo_mypy_plugin.py
"""
A mypy plugin to add annotations for Leo's standard names,
such as c, p, i, j, k, n, s, w, etc.

"""
# pylint: disable=no-name-in-module,useless-return
#@+<< imports >>
#@+node:ekr.20210521170525.1: **  << imports >>
import re
import sys
base_dir = r'C:\leo.repo\leo-editor'
if base_dir not in sys.path:
    sys.path.append(base_dir)
if 0:
    for z in sys.path:
        print(z)
from leo.core import leoGlobals as g
from mypy.plugin import Plugin
import mypy.nodes as nodes
assert nodes  # For traces.
#@-<< imports >>

g.cls()

def plugin(version: str):
    g.trace(f"(leo_mypy_plugin) version: {version}")
    return LeoMypyPlugin

class LeoMypyPlugin(Plugin):
    
    pattern = re.compile(r'\b(i|s|p): Any\b')

    #@+others
    #@+node:ekr.20210521170628.1: **  not used
    if 0:
        #@+others
        #@+node:ekr.20210521165201.1: *3* ctor
        if 0:  # Error constructing plugin instance.  (build.py)
            def __init__ (self, options):
                 g.trace('Plugin.ctor, options:', repr(options))
                 super().__init__(options)
            
        #@+node:ekr.20210521165400.1: *3* Plugin.get_attribute_hook
        def get_attribute_hook(self, *args, **kwargs):
            # print('get_attribute_hook', repr(args), repr(kwargs))
            return None 
        #@+node:ekr.20210521165202.1: *3* Plugin.get_function_hook
        # Adjusts return type of function.

        def get_function_hook(self, ctx):
            
            def function_callback(ctx):
                self.dump_function(ctx)
                return ctx.default_return_type
                
            return function_callback
            
        #@-others
    #@+node:ekr.20210522065542.1: ** Plugin.dump_function
    # FunctionContext = NamedTuple('FunctionContext', [
        # ('arg_types', List[List[Type]]),   # List of actual caller types for each formal argument
        # ('arg_kinds', List[List[int]]),    # Ditto for argument kinds, see nodes.ARG_* constants
        # ('arg_names', List[List[Optional[str]]]),
        # ('callee_arg_names', List[Optional[str]]),
            # # Names of formal parameters from the callee definition,
            # # these will be sufficient in most cases.
            # # Names of actual arguments in the call expression.
            # For example, in a situation like:
                
                    # def func(**kwargs) -> None:
                        # pass
                    # func(kw1=1, kw2=2)

                # callee_arg_names will be ['kwargs'] and arg_names will be [['kw1', 'kw2']].

        # ('default_return_type', Type),     # Return type inferred from signature
        # ('args', List[List[Expression]]),  # Actual expressions for each formal argument
        # ('context', Context),              # Relevant location context (e.g. for error messages)
        # ('api', CheckerPluginInterface)])


    def dump_function(self, ctx):

        # print(ctx.context)
        if 1:
            print('')
            for ivar in ('arg_types', 'arg_kinds', 'arg_names'):
                arg = getattr(ctx, ivar, [])
                if arg:
                    print(ivar, '...')
                    for i, arg_list in enumerate(arg):
                        for j, arg in enumerate(arg_list):
                            print(i, j, arg)
    #@+node:ekr.20210522062026.1: ** Plugin.dump_sig
    def dump_sig(self, ctx):
        sig = ctx.default_signature
        if not self.pattern.search(repr(sig)):
            return
        print('')
        # g.trace(g.callers(1))
        print(sig)
        print(ctx.context)
        print('args...')
        for i, arg_list in enumerate(ctx.args):
            for j, arg in enumerate(arg_list):
                print(i, j, arg)
    #@+node:ekr.20210521165202.2: ** Plugin.get_method_signature_hook
         
    # From plugin.py
    # MethodSigContext = NamedTuple('MethodSigContext', [
        # ('type', ProperType),                 # Base object type for method call
        # ('args', List[List[Expression]]),     # Actual expressions for each formal argument
        # ('default_signature', CallableType),  # Original signature of the method
        # ('context', Context),                 # Relevant location context (e.g. for error messages)
        # ('api', CheckerPluginInterface)])

    def get_method_signature_hook(self, fullname):

        def method_signature_callback(ctx):  # MethodSigContext.
            self.dump_sig(ctx)
            return ctx.default_signature  # Must *always* return a signature.
            
        return method_signature_callback
    #@+node:ekr.20210522062357.1: ** Plugin.get_function_signature_hook
    def get_function_signature_hook(self, fullname):

        def function_signature_callback(ctx):  # FunctionSigContext.
            self.dump_sig(ctx)
            return ctx.default_signature  # Must *always* return a signature.
            
        return function_signature_callback
    #@-others
#@-leo

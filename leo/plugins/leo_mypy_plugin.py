#@+leo-ver=5-thin
#@+node:ekr.20210517152714.1: * @file ../plugins/leo_mypy_plugin.py
"""
A mypy plugin to add annotations for Leo's standard names,
such as c, p, i, j, k, n, s, w, etc.

"""
# pylint: disable=no-name-in-module,useless-return
#@+<< imports >>
#@+node:ekr.20210521170525.1: ** << imports >>
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
    # print('leo_mypy_plugin.plugin: sys.version', sys.version)
    return LeoMypyPlugin

class LeoMypyPlugin(Plugin):
    #@+others
    #@+node:ekr.20210521170628.1: **  not used
    if 0:
        #@+others
        #@+node:ekr.20210521165201.1: *3* ctor
        if 0:  # Error constructing plugin instance.  (build.py)
            def __init__ (self, options):
                 g.trace('Plugin.ctor, options:', repr(options))
                 super().__init__(options)
            
        #@+node:ekr.20210521165202.1: *3* Plugin.get_function_hook
        if 0:  # Adjusts return type of function.
            def get_function_hook(self, *args, **kwargs):
                print('get_function_hook', repr(args), repr(kwargs))
                return None 
                
            ### get_method_hook = get_function_hook
            
            

            
            
        #@+node:ekr.20210521165400.1: *3* Plugin.get_attribute_hook
        def get_attribute_hook(self, *args, **kwargs):
            # print('get_attribute_hook', repr(args), repr(kwargs))
            return None 
        #@-others
    #@+node:ekr.20210521165202.2: ** Plugin.get_method_signature_hook
    method_names = []
    # dump_method_ctx = True

    pattern = re.compile(r'\b(i|s|p): Any\b')

    def get_method_signature_hook(self, fullname):
        
        if 0:
            if fullname not in self.method_names:
                print('get_method_signature_hook', fullname)
                self.method_names.append(fullname)
            
        # From plugin.py
        # MethodSigContext = NamedTuple('MethodSigContext', [
            # ('type', ProperType),                 # Base object type for method call
            # ('args', List[List[Expression]]),     # Actual expressions for each formal argument
            # ('default_signature', CallableType),  # Original signature of the method
            # ('context', Context),                 # Relevant location context (e.g. for error messages)
            # ('api', CheckerPluginInterface)])
        
        def method_signature_callback(ctx):  # MethodSigContext.
            sig = ctx.default_signature
            if self.pattern.search(repr(sig)):
                print('')
                print(sig)  
                print(ctx.context)
                print('args...')
                for i, arg_list in enumerate(ctx.args):
                    for j, arg in enumerate(arg_list):
                        print(i, j, arg)
            return sig  # Muse *always* return a signature.
            
        return method_signature_callback
        

    get_function_signature_hook = get_method_signature_hook
    #@-others
#@-leo

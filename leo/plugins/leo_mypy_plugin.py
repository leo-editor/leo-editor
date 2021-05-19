#@+leo-ver=5-thin
#@+node:ekr.20210517152714.1: * @file ../plugins/leo_mypy_plugin.py
"""
A mypy plugin to add annotations for Leo's standard names,
such as c, p, i, j, k, n, s, w, etc.

"""

# pylint: disable=no-name-in-module,useless-return

import sys
from mypy.plugin import Plugin
print(__file__, "Plugin:", Plugin)

#@+others
#@+node:ekr.20210517153044.1: ** class LeoMypyPlugin
class LeoMypyPlugin(Plugin):
    
    if 0:  # Error constructing plugin instance.  (build.py)
        def __init__ (self, options):
             print('Plugin.ctor, options:', repr(options))
             super().__init__(options)
        
    if 0:  # Adjusts return type of function.
        def get_function_hook(self, *args, **kwargs):
            print('get_function_hook', repr(args), repr(kwargs))
            return None 
            
        get_method_hook = get_function_hook
        
    def get_method_signature_hook(self, s):
            # print('method_signature', s)
            return None
            
    def get_function_signature_hook(self, *args, **kwargs):
            # print('get_function_signature_hook', repr(args), repr(kwargs))
            return None 
            
    def get_attribute_hook(self, *args, **kwargs):
            # print('get_attribute_hook', repr(args), repr(kwargs))
            return None 
#@+node:ekr.20210517152918.1: ** plugin
def plugin(version: str):
    
    print('leo_mypy_plugin.plugin: version:', version)
    print('leo_mypy_plugin.plugin: sys.version', sys.version)
    return LeoMypyPlugin
#@-others
#@-leo

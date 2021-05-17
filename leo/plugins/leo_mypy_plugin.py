#@+leo-ver=5-thin
#@+node:ekr.20210517152714.1: * @file ../plugins/leo_mypy_plugin.py
"""
A mypy plugin to add annotations for Leo's standard names,
such as c, p, i, j, k, n, s, w, etc.

"""
from leo.core import leoGlobals as g
from mypy.plugin import Plugin

#@+others
#@+node:ekr.20210517153044.1: ** class LeoMypyPlugin
class LeoMypyPlugin(Plugin):
    
    pass  ###
#@+node:ekr.20210517152918.1: ** plugin
def plugin(version: str):
    
    g.trace('leo_mypy_plugin', version)
    return LeoMypyPlugin
#@-others
#@-leo

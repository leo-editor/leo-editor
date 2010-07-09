#@+leo-ver=5-thin
#@+node:ekr.20050130120433: * @thin test/failed_import.py
'''A plugin to test import problems.'''

import leo.core.leoGlobals as g
import leo.core.leoPlugins as leoPlugins

__version__ = "1.0"

def onStart(tag,keywords):
    pass
    # g.trace(tag)

try:
    import xyzzy
except ImportError:
    g.cantImport('xyzzy',pluginName='failed_import')

leoPlugins.registerHandler("start2", onStart) # Needed to have the plugin show in the Plugin Manager list.
g.plugin_signon(__name__)
#@-leo

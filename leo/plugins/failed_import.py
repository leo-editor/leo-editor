#@+leo-ver=4-thin
#@+node:ekr.20050130120433:@thin failed_import.py
'''A plugin to test import problems.'''

import leoGlobals as g
import leoPlugins

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
#@nonl
#@-node:ekr.20050130120433:@thin failed_import.py
#@-leo

#@+leo-ver=5-thin
#@+node:ekr.20050130120433: * @file test/failed_import.py
'''A plugin to test import problems.'''

import leo.core.leoGlobals as g

def onStart(tag,keywords):
    pass
    
# pylint: disable=unused-import

try:
    import xyzzy
except ImportError:
    g.cantImport('xyzzy',pluginName='failed_import')
    
def init():
    g.registerHandler("start2", onStart)
        # Needed to have the plugin show in the Plugin Manager list.
    g.plugin_signon(__name__)
    return True
#@-leo

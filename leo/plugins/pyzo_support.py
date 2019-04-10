# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20190410171646.1: * @file pyzo_support.py
#@@first
'''
pyzo_support.py: Allow access to pyzo features within Leo.

This plugin is active only if pyzo modules import successfully.
'''

# To do:
# 1. Support pyzo file browser.
# 2. Support pyzo shell & debugger.

#@+<< imports >>
#@+node:ekr.20190410172058.1: ** << imports >> pyzo support
import leo.core.leoGlobals as g
#
# Automatically add --pyzo to sys.argv.
# This is a convention used in my personal copy of pyzo.
import sys
if '--pyzo' not in sys.argv:
    sys.argv.append('--pyzo')
#
# See whether pyzo can be imported.
try:
    #
    # For now, enable all traces.
    g.pyzo = True
    g.pyzo_trace = True
    g.pyzo_trace_imports = True
    # Be explicit about where everything comes from...
    import pyzo
    # import pyzo.core.editor
    # import pyzo.core.main
    # import pyzo.core.splash
    # import pyzo.util
except ImportError:
    pyzo = None
    g.pyzo = False
    g.pyzo_trace = False
    g.pyzo_trace_imports = False
#@-<< imports >>
#@+others
#@+node:ekr.20190410171905.1: ** init
def init():
    '''Return True if the plugin has loaded successfully.'''
    if g.app.gui.guiName() != "qt":
        print('pyzo_support plugin requires Qt gui')
        return False
    if not pyzo:
        print('pyzo_support plugin requires pyzo')
        return False
    # g.trace('pyzo_support.init: pyzo imported successfully', pyzo)
    # g.registerHandler('after-create-leo-frame',onCreate)
    g.plugin_signon(__name__)
    return True
#@-others
#@-leo

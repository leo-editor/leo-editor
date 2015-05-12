#@+leo-ver=5-thin
#@+node:ekr.20051016160700: * @file testRegisterCommand.py
'''A plugin to test k.registerCommand.'''

#@@language python
#@@tabwidth -4

import leo.core.leoGlobals as g

__version__ = '0.1'

#@+others
#@+node:ekr.20051016161205: ** init
def init():
    '''Return True if the plugin has loaded successfully.'''
    g.registerHandler('after-create-leo-frame',onCreate)
    g.plugin_signon(__name__)
    return True
#@+node:ekr.20051016161205.1: ** onCreate (testRegisterCommand.py)
def onCreate(tag,keys):

    c = keys.get('c')
    if c:
        def f (event):
            g.es_print('Hello',color='purple')

        c.keyHandler.registerCommand(
            'print-hello','Alt-Ctrl-Shift-p',f)
#@-others
#@-leo

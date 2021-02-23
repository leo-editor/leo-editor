#@+leo-ver=5-thin
#@+node:ekr.20051016160700: * @file ../plugins/testRegisterCommand.py
'''A plugin to test k.registerCommand.'''
# See #560: https://github.com/leo-editor/leo-editor/issues/560

#@@language python
#@@tabwidth -4

from leo.core import leoGlobals as g

#@+others
#@+node:ekr.20051016161205: ** init
def init():
    '''Return True if the plugin has loaded successfully.'''
    g.registerHandler('after-create-leo-frame',onCreate)
    g.plugin_signon(__name__)
    return True
#@+node:ekr.20051016161205.1: ** onCreate (testRegisterCommand.py)
def hello_command (event):
        g.es_print('Hello from %s' % (g.shortFileName(__file__)), color='purple')

def onCreate(tag,keys):
    c = keys.get('c')
    if c:
        c.keyHandler.registerCommand('print-hello', hello_command)
            # shortcut='Alt-Ctrl-Shift-p',

# This is the recommended way of registering commands.

@g.command('print-hello2')
def hello_command2 (event):
    g.es_print('Hello 2 from %s' % (g.shortFileName(__file__)), color='red')
#@-others
#@-leo

#@+leo-ver=5-thin
#@+node:ekr.20190805022257.1: * @file pyzo_file_browser.py
'''
Experimental plugin that adds pyzo's file browser dock to Leo.
'''
import leo.core.leoGlobals as g

#@+others
#@+node:ekr.20190805022358.1: ** init (pyzo_file_browser.py)
init_warning_given = False

def init():
    '''Return True if the pyzo_file_browser plugin can be loaded.'''
    
    def oops(message):
        global init_warning_given
        if not init_warning_given:
            init_warning_given = True
            print('%s %s' % (__name__, message))
        return False

    if g.app.gui.guiName() != "qt":
        return oops('requires Qt gui')
    # if not pyzo:
        # return oops('requires pyzo')
    if not g.app.dock:
        return oops('is incompatible with --no-dock')
    g.plugin_signon(__name__)
    g.registerHandler('after-create-leo-frame', onCreate)
    return True
#@+node:ekr.20190805022841.1: ** onCreate (pyzo_file_browser.py)
def onCreate(tag, keys):
    '''TO DO'''
    c = keys.get('c')
    if c:
        print(c)
        # c.pyzoController = PyzoController(c)
#@-others
#@-leo

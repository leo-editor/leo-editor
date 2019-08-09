#@+leo-ver=5-thin
#@+node:ekr.20190805022257.1: * @file pyzo_file_browser.py
'''
Experimental plugin that adds pyzo's file browser dock to Leo.
'''
#@+<< pyzo_file_browser imports >>
#@+node:ekr.20190809093446.1: ** << pyzo_file_browser imports >>
import leo.core.leoGlobals as g

def banner(s):
    '''A good trace for imports.'''
    if 1: g.pr('\n===== %s\n' % s)
#@-<< pyzo_file_browser imports >>

#@+others
#@+node:ekr.20190809093459.1: ** top-level functions
#@+node:ekr.20190809093459.3: *3* init
init_warning_given = False

def init(): # pyzo_file_browser.py
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
#@+node:ekr.20190809093459.4: *3* onCreate
def onCreate(tag, keys): # pyzo_file_browser.py
    '''Create a pyzo file browser in c's outline.'''
    c = keys.get('c')
    dw = c and c.frame and c.frame.top
    if not dw:
        return
    banner('BEFORE onCreate: %s' % c.shortFileName())
#@-others
#@-leo

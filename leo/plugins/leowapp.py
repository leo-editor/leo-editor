# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20181028052650.1: * @file leowapp.py
#@@first
'''
This file is deprecated/obsolete. It may be removed soon.

leoflexx.py implements LeoWapp using flexx.

'''
#@+<< imports >>
#@+node:ekr.20181028052650.3: ** << imports >>
import leo.core.leoGlobals as g
import leo.core.leoFrame as leoFrame
import leo.core.leoGui as leoGui
import sys
try:
    import websockets
    assert websockets
except ImportError:
    websockets = None
    print('leowapp.py requires websockets')
    print('>pip install websockets')
import xml.sax.saxutils as saxutils
#@-<< imports >>
#@+<< config >>
#@+node:ekr.20181029070405.1: ** << config >>
class Config:
    
    # ip = g.app.config.getString("leowapp-ip") or '127.0.0.1'
    # port = g.app.config.getInt("leowapp-port") or 8100
    # timeout = g.app.config.getInt("leowapp-timeout") or 0
    # if timeout > 0: timeout = timeout / 1000.0
    
    ip = '127.0.0.1'
    port = 5678
    # port = 8100
    timeout = 0

# Create a singleton instance.
# The initial values probably should not be changed. 
config = Config()
#@-<< config >>
# browser_encoding = 'utf-8'
    # To do: query browser: var x = document.characterSet; 
#@+others
#@+node:ekr.20181030103048.2: ** escape
def escape(s):
    '''
    Do the standard xml escapes, and replace newlines and tabs.
    '''
    return saxutils.escape(s, {
        '\n': '<br />',
        '\t': '&nbsp;&nbsp;&nbsp;&nbsp;',
    })
#@+node:ekr.20181028052650.5: ** init (leowapp.py)
def init():
    '''Return True if the plugin has loaded successfully.'''
    if not websockets:
        return False
    # ws_server hangs Leo!
    # ws_server()
    g.plugin_signon(__name__)
    return True
#@+node:ekr.20181031162039.1: ** class BrowserGui (leoGui.LeoGui)
class BrowserGui(leoGui.NullGui):
    #@+others
    #@+node:ekr.20181031160042.1: *3* bg.__getattr__
    def __getattr__ (self, attr):
        '''Handle an missing attribute.'''
        if attr in (
            'frameFactory',
            'set_minibuffer_label',
        ):
            # These are optional ivars.
            raise AttributeError
        return self.message(attr)
    #@+node:ekr.20181031162620.1: *3* bg.__init__
    def __init__(self):
        
        g.trace('===== (BrowserGui)')
        leoGui.NullGui.__init__(self, guiName='browser')
        self.styleSheetManagerClass = g.NullObject
        self.log = leoFrame.NullLog()
    #@+node:ekr.20181101034427.1: *3* bg.createLeoFrame
    def createLeoFrame(self, c, title):

        return leoFrame.NullFrame(c, title='NullFrame', gui=self)
    #@+node:ekr.20181101025053.1: *3* bg.message
    def message (self, func):
        '''
        Send a message to the framework.
        '''
        g.trace('=====', func, g.callers())
    #@+node:ekr.20181031162454.1: *3* bg.runMainLoop
    def runMainLoop(self, fileName=None):
        '''The main loop for the browser gui.'''
        # pylint: disable=arguments-differ
        if fileName:
            print('LeoWapp running: %s...' % g.shortFileName(fileName))
        else:
            print('LeoWapp running...')
        if 0: # Run all unit tests.
            path = g.os_path_finalize_join(
                g.app.loadDir, '..', 'test', 'unittest.leo')
            c = g.openWithFileName(path, gui=self)
            c.findCommands.ftm = g.NullObject()
                # A hack. Maybe the NullGui should do this.
            c.debugCommands.runAllUnitTestsLocally()
        print('calling sys.exit(0)')
        sys.exit(0)
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo

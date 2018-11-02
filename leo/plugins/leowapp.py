# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20181028052650.1: * @file leowapp.py
#@@first
#@@language python
#@@tabwidth -4
#@+<< docstring >>
#@+node:ekr.20181028052650.2: ** << docstring >>
#@@language rest
#@@wrap
'''
Leo as a web app: contains python and javascript sides.


'''
#@-<< docstring >>
#@+<< imports >>
#@+node:ekr.20181028052650.3: ** << imports >>
import leo.core.leoGlobals as g
### import leo.core.leoFrame as leoFrame
import leo.core.leoGui as leoGui
### assert leoGui ###
if g.isPython3:
    # import asyncio
    # import datetime
    # import random
    import sys
    try:
        import websockets
        assert websockets
    except ImportError:
        websockets = None
        print('leowapp.py requires websockets')
        print('>pip install websockets')
    import xml.sax.saxutils as saxutils
else:
    print('leowapp.py requires Python 3')
#@-<< imports >>
#@+<< config >>
#@+node:ekr.20181029070405.1: ** << config >>
class Config (object):
    
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
    # LeoWapp requires Python 3, for safety and convenience.
    if not g.isPython3:
        return False
    if not websockets:
        return False
    # ws_server hangs Leo!
    # ws_server()
    g.plugin_signon(__name__)
    return True
#@+node:ekr.20181031162039.1: ** class BrowserGui (leoGui.NullGui)
class BrowserGui(leoGui.NullGui):

    def __init__(self):

        leoGui.NullGui.__init__(self, guiName='browser')
        g.trace('===== (BrowserGui)')
        self.focusWidget = None
        
        # Set by LeoGui...
            ### self.consoleOnly = False
        # Others
        # self.styleSheetManagerClass = g.NullObject
        # self.log = leoFrame.NullLog()
        # self.isNullGui = True
        ###
            # self.clipboardContents = ''
            # self.enablePlugins = False ###
            # self.script = None
            # self.idleTimeClass = g.NullObject

    #@+others
    #@+node:ekr.20181101072605.1: *3* bg.oops
    oops_d = {}

    def oops(self):
        if 0:
            callers = g.callers()
            if callers not in self.oops_d:
                g.trace(callers)
                self.oops_d [callers] = callers
    #@+node:ekr.20181101073740.1: *3* bg.overrides of LeoGui methods
    def dismiss_splash_screen(self):
        pass

    def guiName(self):
        return 'browser'
        
    def isTextWidget(self, w):
        return True # Must be True for unit tests.

    def isTextWrapper(self, w):
        '''Return True if w is a Text widget suitable for text-oriented commands.'''
        return w and getattr(w, 'supportsHighLevelInterface', None)
    #@+node:ekr.20181102073938.1: *3* bg.overrides of NullGui methods
    #@+node:ekr.20181102073746.4: *4* bg.clipboard & focus
    def get_focus(self, *args, **kwargs):
        return self.focusWidget

    def getTextFromClipboard(self):
        return self.clipboardContents

    def replaceClipboardWith(self, s):
        self.clipboardContents = s

    def set_focus(self, commander, widget):
        self.focusWidget = widget
    #@+node:ekr.20181102073957.1: *4* bg.dialogs
    def runAboutLeoDialog(self, c, version, theCopyright, url, email):
        return self.do_dialog("aboutLeoDialog", None)

    def runAskLeoIDDialog(self):
        return self.do_dialog("leoIDDialog", None)

    def runAskOkDialog(self, c, title, message=None, text="Ok"):
        return self.do_dialog("okDialog", "Ok")

    def runAskOkCancelNumberDialog(self, c, title, message,
        cancelButtonText=None,
        okButtonText=None,
    ):
        return self.do_dialog("numberDialog", -1)

    def runAskOkCancelStringDialog(self, c, title, message,
        cancelButtonText=None,
        okButtonText=None,
        default="",
        wide=False,
    ):
        return self.do_dialog("stringDialog", '')

    def runCompareDialog(self, c):
        return self.do_dialog("compareDialog", '')

    def runOpenFileDialog(self, c, title, filetypes, defaultextension,
        multiple=False,
        startpath=None,
    ):
        return self.do_dialog("openFileDialog", None)

    def runSaveFileDialog(self, c, initialfile, title, filetypes, defaultextension):
        return self.do_dialog("saveFileDialog", None)

    def runAskYesNoDialog(self, c, title,
        message=None,
        yes_all=False,
        no_all=False,
    ):
        return self.do_dialog("yesNoDialog", "no")

    def runAskYesNoCancelDialog(self, c, title,
        message=None,
        yesMessage="Yes",
        noMessage="No",
        yesToAllMessage=None,
        defaultButton="Yes",
        cancelMessage=None,
    ):
        return self.do_dialog("yesNoCancelDialog", "cancel")

    #@+node:ekr.20181102074018.1: *4* bg.do_dialog
    def do_dialog(self, key, defaultVal):
        return defaultVal
    #@+node:ekr.20181101025053.1: *3* bg.message
    def message (self, func, payload=None):
        '''
        Send a message to the framework.
        '''
        g.trace('=====', func, payload)
    #@+node:ekr.20181031162454.1: *3* bg.runMainLoop
    def runMainLoop(self):
        '''The main loop for the browser gui.'''
        print('LeoWapp running...')
        c = g.app.log.c
        if 1: # Run all unit tests.
            g.app.failFast = True
            path = g.os_path_finalize_join(
                g.app.loadDir, '..', 'test', 'unittest.leo')
            c = g.openWithFileName(path, gui=self)
            c.findCommands.ftm = g.NullObject()
                # A hack. Some other class should do this.
                # This looks like a bug.
            c.debugCommands.runAllUnitTestsLocally()
        print('calling sys.exit(0)')
        sys.exit(0)
    #@-others
#@-others
#@-leo

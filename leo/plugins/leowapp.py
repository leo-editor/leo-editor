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
import leo.core.leoFrame as leoFrame
import leo.core.leoGui as leoGui
assert leoGui ###
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
        
        # Set by LeoGui...
            ### self.consoleOnly = False
        # Others
        # self.styleSheetManagerClass = g.NullObject
        # self.log = leoFrame.NullLog()
        # self.isNullGui = True
        ###
            # self.clipboardContents = ''
            # self.enablePlugins = False ###
            # self.focusWidget = None
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
    #@+node:ekr.20181102063012.1: *3* not yet...
    if 0:
        #@+others
        #@+node:ekr.20181101034427.1: *4* bg.createLeoFrame
        def createLeoFrame(self, c, title):

            g.trace(g.callers())
            return leoFrame.NullFrame(c, title='NullFrame', gui=self)
        #@+node:ekr.20181101025053.1: *4* bg.message
        def message (self, func, payload=None):
            '''
            Send a message to the framework.
            '''
            g.trace('=====', func, payload)
        #@+node:ekr.20181101075334.1: *4* bg.create_key_event
        #@+node:ekr.20181101073740.1: *4* Defined in LeoGui
        def dismiss_splash_screen(self):
            pass

        def guiName(self):
            return 'browser'
            
        def isTextWidget(self, w):
            return True # Must be True for unit tests.

        def isTextWrapper(self, w):
            '''Return True if w is a Text widget suitable for text-oriented commands.'''
            return w and getattr(w, 'supportsHighLevelInterface', None)
        #@+node:ekr.20181101072524.1: *4* Must be defined in subclasses
        #@+node:ekr.20181101072524.2: *5* LeoGui.destroySelf
        def destroySelf(self):
            self.oops()


        #@+node:ekr.20181101072524.3: *5* LeoGui.dialogs
        def runAboutLeoDialog(self, c, version, theCopyright, url, email):
            """Create and run Leo's About Leo dialog."""
            self.oops()

        def runAskLeoIDDialog(self):
            """Create and run a dialog to get g.app.LeoID."""
            self.oops()

        def runAskOkDialog(self, c, title, message=None, text="Ok"):
            """Create and run an askOK dialog ."""
            self.oops()

        def runAskOkCancelNumberDialog(self, c, title, message, cancelButtonText=None, okButtonText=None):
            """Create and run askOkCancelNumber dialog ."""
            self.oops()

        def runAskOkCancelStringDialog(self, c, title, message, cancelButtonText=None,
                                       okButtonText=None, default="", wide=False):
            """Create and run askOkCancelString dialog ."""
            self.oops()

        def runAskYesNoDialog(self, c, title, message=None, yes_all=False, no_all=False):
            """Create and run an askYesNo dialog."""
            self.oops()

        def runAskYesNoCancelDialog(self, c, title,
            message=None, yesMessage="Yes", noMessage="No",
            yesToAllMessage=None, defaultButton="Yes", cancelMessage=None,
        ):
            """Create and run an askYesNoCancel dialog ."""
            self.oops()

        def runPropertiesDialog(self, title='Properties', data=None, callback=None, buttons=None):
            """Dispay a modal TkPropertiesDialog"""
            self.oops()
        #@+node:ekr.20181101072524.4: *5* LeoGui.file dialogs
        def runOpenFileDialog(self, c, title, filetypes, defaultextension, multiple=False, startpath=None):
            """Create and run an open file dialog ."""
            self.oops()

        def runSaveFileDialog(self, c, initialfile, title, filetypes, defaultextension):
            """Create and run a save file dialog ."""
            self.oops()
        #@+node:ekr.20181101072524.5: *5* LeoGui.panels
        def createColorPanel(self, c):
            """Create a color panel"""
            self.oops()

        def createComparePanel(self, c):
            """Create Compare panel."""
            self.oops()

        def createFindTab(self, c, parentFrame):
            """Create a find tab in the indicated frame."""
            self.oops()

        def createFontPanel(self, c):
            """Create a hidden Font panel."""
            self.oops()
        #@+node:ekr.20181101072524.7: *5* LeoGui.utils
        #@+at Subclasses are expected to subclass all of the following methods.
        # 
        # These are all do-nothing methods: callers are expected to check for
        # None returns.
        # 
        # The type of commander passed to methods depends on the type of frame
        # or dialog being created. The commander may be a Commands instance or
        # one of its subcommanders.
        #@+node:ekr.20181101072524.8: *6* LeoGui.Clipboard
        def replaceClipboardWith(self, s):
            self.oops()

        def getTextFromClipboard(self):
            self.oops()
        #@+node:ekr.20181101072524.9: *6* LeoGui.Dialog utils
        def attachLeoIcon(self, window):
            """Attach the Leo icon to a window."""
            self.oops()

        def center_dialog(self, dialog):
            """Center a dialog."""
            self.oops()

        def create_labeled_frame(self, parent, caption=None, relief="groove", bd=2, padx=0, pady=0):
            """Create a labeled frame."""
            self.oops()

        def get_window_info(self, window):
            """Return the window information."""
            self.oops()
        #@+node:ekr.20181101072524.10: *6* LeoGui.Focus
        def get_focus(self, *args, **kwargs):
            """Return the widget that has focus, or the body widget if None."""
            self.oops()

        def set_focus(self, commander, widget):
            """Set the focus of the widget in the given commander if it needs to be changed."""
            self.oops()
        #@+node:ekr.20181101072524.11: *6* LeoGui.Font
        def getFontFromParams(self, family, size, slant, weight, defaultSize=12):

            self.oops()
        #@+node:ekr.20181101072524.12: *6* LeoGui.getFullVersion
        def getFullVersion(self, c=None):
            return 'LeoGui: dummy version'
        #@+node:ekr.20181101072524.13: *6* LeoGui.makeScriptButton
        def makeScriptButton(self, c,
            args=None,
            p=None,
            script=None,
            buttonText=None,
            balloonText='Script Button',
            shortcut=None,
            bg='LightSteelBlue1',
            define_g=True,
            define_name='__main__',
            silent=False,
        ):
            self.oops()
        #@-others
    #@-others
#@-others
#@-leo

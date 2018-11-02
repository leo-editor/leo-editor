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
import leo.core.leoMenu as leoMenu
if g.isPython3:
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
#@+node:ekr.20181102084106.1: ** browser classes
#@+node:ekr.20181102081803.1: *3* class BrowserFrame (leoFrame.LeoFrame)
class BrowserFrame(leoFrame.LeoFrame):
    
    #@+others
    #@+node:ekr.20181102082842.1: *4* bf.ctor
    def __init__(self, c, title, gui):
        '''Ctor for the BrowserFrame class.'''
        leoFrame.LeoFrame.__init__(self, c, gui)
            # Init the base class.
        assert self.c
        self.wrapper = None
            # was BrowserIconBarClass(self.c, self)
        self.isNullFrame = True ### Should this be False ???
        self.outerFrame = None
        self.ratio = self.secondary_ratio = 0.5
        self.title = title
        self.top = None # Always None.
        # Create the component objects.
        self.body = BrowserBody(frame=self)
        self.iconBar = BrowserIconBar(c=self.c, parentFrame=self)
        self.log = BrowserLog(frame=self)
        self.menu = BrowserMenu(frame=self)
        self.statusLine = BrowserStatusLine(frame=self)
            ### self.statusLineClass = StatusLineClass
        self.tree = BrowserTree(frame=self)
        # Default window position.
        self.w = 600
        self.h = 500
        self.x = 40
        self.y = 40
    #@+node:ekr.20181102082044.4: *4* bf.finishCreate
    def finishCreate(self):
        
        # #503: Use string/null gui for unit tests.
        self.createFirstTreeNode()
            # Call the base LeoFrame method.
    #@+node:ekr.20181102083502.1: *4* bf.oops
    def oops(self):
        g.trace("NullFrame", g.callers(4))
    #@+node:ekr.20181102082044.3: *4* bf.redirectors
    def bringToFront(self):
        pass
    def cascade(self, event=None):
        pass
    def contractBodyPane(self, event=None):
        pass
    def contractLogPane(self, event=None):
        pass
    def contractOutlinePane(self, event=None):
        pass
    def contractPane(self, event=None):
        pass
    def deiconify(self):
        pass
    def destroySelf(self):
        pass
    def equalSizedPanes(self, event=None):
        pass
    def expandBodyPane(self, event=None):
        pass
    def expandLogPane(self, event=None):
        pass
    def expandOutlinePane(self, event=None):
        pass
    def expandPane(self, event=None):
        pass
    def fullyExpandBodyPane(self, event=None):
        pass
    def fullyExpandLogPane(self, event=None):
        pass
    def fullyExpandOutlinePane(self, event=None):
        pass
    def fullyExpandPane(self, event=None):
        pass
    def get_window_info(self): return 600, 500, 20, 20
    def hideBodyPane(self, event=None):
        pass
    def hideLogPane(self, event=None):
        pass
    def hideLogWindow(self, event=None):
        pass
    def hideOutlinePane(self, event=None):
        pass
    def hidePane(self, event=None):
        pass
    def leoHelp(self, event=None):
        pass
    def lift(self):
        pass
    def minimizeAll(self, event=None):
        pass
    def resizePanesToRatio(self, ratio, secondary_ratio):
        pass
    def resizeToScreen(self, event=None):
        pass
    def setInitialWindowGeometry(self):
        pass
    def setTopGeometry(self, w, h, x, y, adjustSize=True):
        return 0, 0, 0, 0
    def setWrap(self, flag, force=False):
        pass
    def toggleActivePane(self, event=None):
        pass
    def toggleSplitDirection(self, event=None):
        pass
    def update(self):
        pass
    #@-others
#@+node:ekr.20181031162039.1: *3* class BrowserGui (leoGui.NullGui)
class BrowserGui(leoGui.NullGui):

    # def __init__(self):
        # leoGui.NullGui.__init__(self, guiName='browser')
            
    def destroySelf(self):
        pass
        
    def guiName(self):
        return 'browser'
            
    def finishCreate(self):
        pass

    #@+others
    #@+node:ekr.20181102073746.4: *4* bg.clipboard & focus
    def get_focus(self, *args, **kwargs):
        return self.focusWidget

    def getTextFromClipboard(self):
        return self.clipboardContents

    def replaceClipboardWith(self, s):
        self.clipboardContents = s

    def set_focus(self, commander, widget):
        self.focusWidget = widget
    #@+node:ekr.20181102073957.1: *4* bg.dialogs & alerts
    def alert(self, message):
        pass

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
    #@+node:ekr.20181102080116.1: *4* bg.events
    def onActivateEvent(self, *args, **keys):
        pass

    def onDeactivateEvent(self, *args, **keys):
        pass
    #@+node:ekr.20181102080014.1: *4* bg.fonts, icons and images
    def attachLeoIcon(self, window):
        pass
        
    def getFontFromParams(self, family, size, slant, weight, defaultSize=12):
        return g.app.config.defaultFont

    def getIconImage(self, name):
        return None

    def getImageImage(self, name):
        return None

    def getTreeImage(self, c, path):
        return None
    #@+node:ekr.20181102073746.8: *4* bg.gui elements
    def createComparePanel(self, c):
        """Create Compare panel."""
        return None

    def createFindTab(self, c, parentFrame):
        """Create a find tab in the indicated frame."""
        return None

    def createLeoFrame(self, c, title):
        """Create a null Leo Frame."""
        return BrowserFrame(c, gui=self, title=title)
            
    def dismiss_splash_screen(self):
        pass

    def get_window_info(self, window):
        return 600, 500, 20, 20
        
    def isTextWidget(self, w):
        return True # Must be True for unit tests.

    def isTextWrapper(self, w):
        '''Return True if w is a Text widget suitable for text-oriented commands.'''
        return w and getattr(w, 'supportsHighLevelInterface', None)
    #@+node:ekr.20181101025053.1: *4* bg.message
    def message (self, func, payload=None):
        '''
        Send a message to the framework.
        '''
        g.trace('=====', func, payload)
    #@+node:ekr.20181101072605.1: *4* bg.oops
    oops_d = {}

    def oops(self):
        callers = g.callers()
        if callers not in self.oops_d:
            g.trace(callers)
            self.oops_d [callers] = callers
            if g.unitTesting:
                assert False, repr(callers)
    #@+node:ekr.20181031162454.1: *4* bg.runMainLoop
    def runMainLoop(self):
        '''The main loop for the browser gui.'''
        print('LeoWapp running...')
        c = g.app.log.c
        if 1: # Run all unit tests.
            assert g.app.gui.guiName() == 'browser'
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
#@+node:ekr.20181102085243.1: *3* components of BrowserFrame
#@+node:ekr.20181102084242.1: *4* class BrowserBody (leoFrame.NullBody)
class BrowserBody(leoFrame.NullBody):
   
    def __init__(self, frame):
        leoFrame.NullBody.__init__(self,
            frame=frame, parentFrame=None)
#@+node:ekr.20181102083641.1: *4* class BrowserIconBar (leoFrame.NullIconBarClass)
class BrowserIconBar(leoFrame.NullIconBarClass):

    def __init__(self, c, parentFrame):
        leoFrame.NullIconBarClass.__init__(self,
            c = self.c, parentFrame=parentFrame)
#@+node:ekr.20181102084250.1: *4* class BrowserLog (leoFrame.NullLog)
class BrowserLog(leoFrame.NullLog):
    
    def __init__(self, frame):
        leoFrame.NullLog.__init__(self,
            frame=frame, parentFrame=None)
#@+node:ekr.20181102084314.1: *4* class BrowserMenu (leoMenu.NullMenu)
class BrowserMenu(leoMenu.NullMenu):
    
    def __init__(self, frame):
        leoMenu.NullMenu.__init__(self, frame=frame)
#@+node:ekr.20181102084201.1: *4* class BrowserStatus(Line leoFrame.NullStatusLineClass)
class BrowserStatusLine(leoFrame.NullStatusLineClass):
    
    def __init__(self, frame):
        leoFrame.NullStatusLineClass.__init__(self,
            frame=frame, parentFrame=None)
#@+node:ekr.20181102084258.1: *4* class BrowserTree (leoFrame.NullTree)
class BrowserTree(leoFrame.NullTree):

    def __init__(self, frame):
        leoFrame.NullTree.__init__(self,
            frame=frame, parentFrame=None)
#@-others
#@-leo

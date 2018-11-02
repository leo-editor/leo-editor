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
#@+node:ekr.20181102084242.1: ** class BrowserBody (NullBody)
class BrowserBody(leoFrame.NullBody):
   
    def __init__(self, frame):
        g.trace('(BrowserBody)')
        leoFrame.NullBody.__init__(self,
            frame=frame, parentFrame=None)
        ###
            # self.insertPoint = 0
            # self.selection = 0, 0
            # self.s = "" # The body text
            # self.widget = None
            # self.wrapper = wrapper = leoFrame.StringTextWrapper(c=self.c, name='body')
            # self.editorWidgets['1'] = wrapper
            # self.colorizer = NullColorizer(self.c)
            
    #@+others
    #@+node:ekr.20181102122447.1: *3* bb.not used
    if 0:
        #@+others
        #@+node:ekr.20181102122257.3: *4* BrowserBody interface
        # Birth, death...
        def createControl(self, parentFrame, p):
            pass
        # Editors...
        def addEditor(self, event=None):
            pass
        def assignPositionToEditor(self, p):
            pass
        def createEditorFrame(self, w):
            return None
        def cycleEditorFocus(self, event=None):
            pass
        def deleteEditor(self, event=None):
            pass
        def selectEditor(self, w):
            pass
        def selectLabel(self, w):
            pass
        def setEditorColors(self, bg, fg):
            pass
        def unselectLabel(self, w):
            pass
        def updateEditors(self):
            pass
        # Events...
        def forceFullRecolor(self):
            pass
        def scheduleIdleTimeRoutine(self, function, *args, **keys):
            pass
        #@-others
    #@+node:ekr.20181102122653.1: *3* bb.setFocus
    def setFocus(self):
        g.trace('(BrowserBody)', g.callers())
        g.app.gui.message({
            'kind': 'set-focus-to-body',
        })
    #@-others
    
#@+node:ekr.20181102081803.1: ** class BrowserFrame (LeoFrame)
class BrowserFrame(leoFrame.LeoFrame):
    
    #@+others
    #@+node:ekr.20181102082842.1: *3* bf.ctor
    def __init__(self, c, title, gui):
        '''Ctor for the BrowserFrame class.'''
        leoFrame.LeoFrame.__init__(self, c, gui)
            # Init the base class.
        c.frame = self
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
        self.iconBar = BrowserIconBar(c=c, parentFrame=self)
        self.log = BrowserLog(frame=self)
        self.menu = BrowserMenu(frame=self)
        self.statusLine = BrowserStatusLine(c=c, parentFrame=self)
        self.tree = BrowserTree(frame=self)
        # Default window position.
        self.w = 600
        self.h = 500
        self.x = 40
        self.y = 40
    #@+node:ekr.20181102082044.4: *3* bf.finishCreate
    def finishCreate(self):
        
        # #503: Use string/null gui for unit tests.
        self.createFirstTreeNode()
            # Call the base LeoFrame method.
    #@+node:ekr.20181102083502.1: *3* bf.oops
    def oops(self):
        g.trace("BrowserFrame", g.callers(4))
    #@+node:ekr.20181102082044.3: *3* bf.redirectors
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
    def get_window_info(self):
        return 600, 500, 20, 20
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
#@+node:ekr.20181031162039.1: ** class BrowserGui (NullGui)
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
    #@+node:ekr.20181102073746.4: *3* bg.clipboard & focus
    def get_focus(self, *args, **kwargs):
        return self.focusWidget

    def getTextFromClipboard(self):
        return self.clipboardContents

    def replaceClipboardWith(self, s):
        self.clipboardContents = s

    def set_focus(self, commander, widget):
        self.focusWidget = widget
    #@+node:ekr.20181102073957.1: *3* bg.dialogs & alerts
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

    #@+node:ekr.20181102074018.1: *3* bg.do_dialog
    def do_dialog(self, key, defaultVal):
        return defaultVal
    #@+node:ekr.20181102080116.1: *3* bg.events
    def onActivateEvent(self, *args, **keys):
        pass

    def onDeactivateEvent(self, *args, **keys):
        pass
    #@+node:ekr.20181102080014.1: *3* bg.fonts, icons and images
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
    #@+node:ekr.20181102073746.8: *3* bg.gui elements
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
    #@+node:ekr.20181101025053.1: *3* bg.message
    def message (self, payload):
        '''Send a message to the framework.'''
        print('')
        g.trace('(BrowserGui) =====')
        g.printObj(payload)
        print('')
    #@+node:ekr.20181101072605.1: *3* bg.oops
    oops_d = {}

    def oops(self):
        callers = g.callers()
        if callers not in self.oops_d:
            g.trace('(BrowserGui)', callers)
            self.oops_d [callers] = callers
            if g.unitTesting:
                assert False, repr(callers)
    #@+node:ekr.20181031162454.1: *3* bg.runMainLoop
    def runMainLoop(self):
        '''The main loop for the browser gui.'''
        print('LeoWapp running...')
        c = g.app.log.c
        assert g.app.gui.guiName() == 'browser'
        if 1: # Run all unit tests.
            g.app.failFast = True
            path = g.os_path_finalize_join(
                g.app.loadDir, '..', 'test', 'unittest.leo')
            c = g.openWithFileName(path, gui=self)
            c.findCommands.ftm = g.NullObject()
                # A hack. Some other class should do this.
                # This looks like a bug.
            c.debugCommands.runAllUnitTestsLocally()
                # This calls sys.exit(0)
        print('calling sys.exit(0)')
        sys.exit(0)
    #@-others
#@+node:ekr.20181102083641.1: ** class BrowserIconBar (NullIconBarClass)
class BrowserIconBar(leoFrame.NullIconBarClass):

    def __init__(self, c, parentFrame):
        # g.trace('(BrowserIconBar)')
        leoFrame.NullIconBarClass.__init__(self,
            c=c, parentFrame=parentFrame)
        ###
            # self.c = c
            # self.iconFrame = None
            # self.parentFrame = parentFrame
            # self.w = g.NullObject()
#@+node:ekr.20181102084250.1: ** class BrowserLog (NullLog)
class BrowserLog(leoFrame.NullLog):
    
    def __init__(self, frame):
        leoFrame.NullLog.__init__(self,
            frame=frame, parentFrame=None)
        assert self.enabled 
    ###
        # self.isNull = True
        # self.logNumber = 0
        # self.widget = self.createControl(parentFrame)
#@+node:ekr.20181102114823.1: *3*  bl.not used
if 0:
    #@+others
    #@+node:ekr.20181102101940.5: *4* bl.createControl
    def createControl(self, parentFrame):
        return self.createTextWidget(parentFrame)
    #@+node:ekr.20181102101940.6: *4* bl.createTextWidget
    def createTextWidget(self, parentFrame):
        self.logNumber += 1
        c = self.c
        log = leoFrame.StringTextWrapper(c=c, name="log-%d" % self.logNumber)
        return log
    #@+node:ekr.20181102101940.4: *4* bl.finishCreate
    def finishCreate(self):
        pass
    #@+node:ekr.20181102101940.7: *4* bl.isLogWidget
    def isLogWidget(self, w):
        return False
    #@+node:ekr.20181102101940.10: *4* bl.tabs
    def clearTab(self, tabName, wrap='none'):
        pass

    def createCanvas(self, tabName):
        pass

    def createTab(self, tabName, createText=True, widget=None, wrap='none'):
        pass

    def deleteTab(self, tabName, force=False): pass

    def getSelectedTab(self): return None

    def lowerTab(self, tabName): pass

    def raiseTab(self, tabName): pass

    def renameTab(self, oldName, newName): pass

    def selectTab(self, tabName, createText=True, widget=None, wrap='none'): pass
    #@-others
#@+node:ekr.20181102101940.8: *3* bl.oops
def oops(self):
    g.trace("BrowserLog:", g.callers(4))
#@+node:ekr.20181102101940.9: *3* bl.put and putnl
def put(self, s,
    color=None,
    tabName='Log',
    from_redirect=False,
    nodeLink=None,
):
    g.trace('(BrowserLog)', g.callers())
    if self.enabled:
        g.app.gui.message({
            'kind': 'put',
            's': g.toUnicode(s),
            'tabName': tabName,
        })

def putnl(self, tabName='Log'):
    g.trace('(BrowserLog)', g.callers())
    if self.enabled:
        g.app.gui.message({
            'kind': 'putnl',
            'tabName': tabName,
        })
#@+node:ekr.20181102084314.1: ** class BrowserMenu (NullMenu)
class BrowserMenu(leoMenu.NullMenu):
    
    def __init__(self, frame):
        # g.trace('(BrowserMenu)')
        leoMenu.NullMenu.__init__(self, frame=frame)
#@+node:ekr.20181102084201.1: ** class BrowserStatusLine (NullStatusLineClass)
class BrowserStatusLine(leoFrame.NullStatusLineClass):
    
    def __init__(self, c, parentFrame):
        # g.trace('(BrowserStatusLine)')
        leoFrame.NullStatusLineClass.__init__(self,
            c=c, parentFrame=parentFrame)
#@+node:ekr.20181102084258.1: ** class BrowserTree (NullTree)
class BrowserTree(leoFrame.NullTree):

    def __init__(self, frame):
        g.trace('(BrowserTree)')
        leoFrame.NullTree.__init__(self, frame=frame)
    ###
        # self.c = frame.c
        # self.editWidgetsDict = {}
            # Keys are tnodes, values are StringTextWidgets.
        # self.font = None
        # self.fontName = None
        # self.canvas = None
        # self.redrawCount = 0
        # self.updateCount = 0
#@+node:ekr.20181102123725.1: *3*  bt.not used
if 0:
    #@+others
    #@+node:ekr.20181102123625.5: *4* bt.printWidgets
    def printWidgets(self):
        d = self.editWidgetsDict
        for key in d:
            # keys are vnodes, values are StringTextWidgets.
            w = d.get(key)
            g.pr('w', w, 'v.h:', key.headString, 's:', repr(w.s))
    #@+node:ekr.20181102123625.6: *4* bt.Drawing & scrolling
    def redraw_after_contract(self, p):
        self.redraw()

    def redraw_after_expand(self, p):
        self.redraw()

    def redraw_after_head_changed(self):
        self.redraw()

    def redraw_after_icons_changed(self):
        self.redraw()

    def redraw_after_select(self, p=None):
        self.redraw()
    #@-others
    
#@+node:ekr.20181102124307.1: *3* bt.drawIcon
def drawIcon(self, p):
    g.trace('(BrowserTree)', g.callers())
    g.app.gui.message({
        'kind': 'draw-icon',
        'p': p and p.gnx,
    })
#@+node:ekr.20181102123625.3: *3* bt.edit_widget
def edit_widget(self, p):
    g.trace('(BrowserTree)', g.callers())
    g.app.gui.message({
        'kind': 'edit-widget',
        'p': p and p.gnx,
    })
    d = self.editWidgetsDict
    if not p or not p.v:
        return None
    w = d.get(p.v)
    if not w:
        d[p.v] = w = leoFrame.StringTextWrapper(
            c=self.c,
            name='head-%d' % (1 + len(list(d.keys()))))
        w.setAllText(p.h)
    return w
#@+node:ekr.20181102123625.4: *3* bt.editLabel
def editLabel(self, p, selectAll=False, selection=None):
    '''Start editing p's headline.'''
    self.endEditLabel()
    g.app.gui.message({
        'kind': 'edit-label',
        'p': p and p.gnx,
    })
    if p:
        self.revertHeadline = p.h
            # New in 4.4b2: helps undo.
        wrapper = leoFrame.StringTextWrapper(c=self.c, name='head-wrapper')
        e = None
        g.trace('(BrowserTree)', g.callers())
        return e, wrapper
    else:
        return None, None
#@+node:ekr.20181102124041.1: *3* bt.redraw
def redraw(self, p=None):
    self.redrawCount += 1
    return p
        # Support for #503: Use string/null gui for unit tests
        
redraw_now = redraw
#@+node:ekr.20181102124332.1: *3* bt.scrollTo
def scrollTo(self, p):
    g.trace('(BrowserTree)', g.callers())
    g.app.gui.message({
        'kind': 'scroll-tree',
        'p': p and p.gnx,
    })

#@+node:ekr.20181102123625.7: *3* bt.setHeadline
def setHeadline(self, p, s):
    '''
    Set the actual text of the headline widget.

    This is called from the undo/redo logic to change the text before redrawing.
    '''
    g.trace('(BrowserTree)', g.callers())
    g.app.gui.message({
        'kind': 'set-headline',
        'p': p and p.gnx,
        's': s,
    })
    w = self.edit_widget(p)
    if w:
        w.delete(0, 'end')
        if s.endswith('\n') or s.endswith('\r'):
            s = s[: -1]
        w.insert(0, s)
        self.revertHeadline = s
    else:
        g.trace('-' * 20, 'oops')
#@+node:ekr.20181102125422.1: ** Top-level
#@+node:ekr.20181030103048.2: *3* escape
def escape(s):
    '''
    Do the standard xml escapes, and replace newlines and tabs.
    '''
    return saxutils.escape(s, {
        '\n': '<br />',
        '\t': '&nbsp;&nbsp;&nbsp;&nbsp;',
    })
#@+node:ekr.20181028052650.5: *3* init (leowapp.py)
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
#@-others
#@-leo

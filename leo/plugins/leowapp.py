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
    # import xml.sax.saxutils as saxutils
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
#@+node:ekr.20181028052650.5: **  init (leowapp.py)
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
#@+node:ekr.20181102084242.1: ** class BrowserBody
class BrowserBody(leoFrame.NullBody):
   
    def __init__(self, frame):
        # g.trace('(BrowserBody)', g.callers())
        leoFrame.NullBody.__init__(self,
            frame=frame, parentFrame=None)
        self.message = g.app.gui.message
        self.wrapper = BrowserStringTextWrapper(c=self.c, name='body')
        ###
            # self.insertPoint = 0
            # self.selection = 0, 0
            # self.s = "" # The body text
            # self.widget = None
            # self.editorWidgets['1'] = wrapper
            # self.colorizer = NullColorizer(self.c)
    #@+others
    #@+node:ekr.20181102122257.3: *3* BrowserBody interface
    # At present theses do not issue messages.

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
    #@+node:ekr.20181102122653.1: *3* bb.setFocus
    def setFocus(self):
        self.message('set-focus-to-body')
    #@-others
#@+node:ekr.20181102081803.1: ** class BrowserFrame
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
        self.isNullFrame = True
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
        self.w, self.h, self.x, self.y = 600, 500, 40, 40
    #@+node:ekr.20181102082044.4: *3* bf.finishCreate
    def finishCreate(self):
        self.createFirstTreeNode()
            # Call the base LeoFrame method.
    #@+node:ekr.20181102083502.1: *3* bf.oops
    def oops(self):
        g.trace("BrowserFrame", g.callers(4))
    #@+node:ekr.20181102082044.3: *3* bf.redirectors (To do: add messages)
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
#@+node:ekr.20181031162039.1: ** class BrowserGui
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
        self.message('get-focus')
        return self.focusWidget

    def getTextFromClipboard(self):
        self.message('get-clipboard')
        return self.clipboardContents

    def replaceClipboardWith(self, s):
        self.message('set-clipboard', s=s)
        self.clipboardContents = s

    def set_focus(self, commander, widget):
        # Not really correct.
        self.message('set-focus',
            commander=commander.shortFileName(),
            widget=self.widget_name(widget),
        )
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

    #@+node:ekr.20181102074018.1: *4* bg.do_dialog
    def do_dialog(self, key, defaultVal):
        self.message('do-dialog', defaultVal=defaultVal, key=key)
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
        """Create a Browser Frame and a Leo frame."""
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
    def message (self, kind, **payload):
        '''Send a message to the framework.'''
        assert kind not in payload, (payload, g.callers())
        if 1:
            payload2 = payload.copy()
            if 's' in payload:
                payload2 ['s'] = g.truncate(payload['s'], 20).strip()
            g.trace('%20s %s' % (kind, payload2))
        payload ['kind'] = kind
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
#@+node:ekr.20181102083641.1: ** class BrowserIconBar
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
#@+node:ekr.20181102084250.1: ** class BrowserLog
class BrowserLog(leoFrame.NullLog):
    
    def __init__(self, frame):
        leoFrame.NullLog.__init__(self,
            frame=frame, parentFrame=None)
        assert self.enabled
        self.message = g.app.gui.message
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
#@+node:ekr.20181102101940.6: *3* bl.createTextWidget
def createTextWidget(self, parentFrame):
    self.logNumber += 1
    c = self.c
    log = BrowserStringTextWrapper(c=c, name="log-%d" % self.logNumber)
    return log
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
    if self.enabled:
        self.message('put', s=s, tabName=tabName)

def putnl(self, tabName='Log'):
    if self.enabled:
        self.message('put-nl', tabName=tabName)
#@+node:ekr.20181102084314.1: ** class BrowserMenu
class BrowserMenu(leoMenu.NullMenu):
    
    def __init__(self, frame):
        leoMenu.NullMenu.__init__(self, frame=frame)
#@+node:ekr.20181102084201.1: ** class BrowserStatusLine
class BrowserStatusLine(leoFrame.NullStatusLineClass):
    
    def __init__(self, c, parentFrame):
        leoFrame.NullStatusLineClass.__init__(self,
            c=c, parentFrame=parentFrame)
#@+node:ekr.20181102151431.1: ** class BrowserStringTextWrapper
class BrowserStringTextWrapper(object):
    '''
    A class that represents text as a Python string.
    This class forwards messages to the browser.
    '''
    def __init__(self, c, name):
        '''Ctor for the BrowserStringTextWrapper class.'''
        self.c = c
        self.name = name
        self.ins = 0
        self.message = g.app.gui.message
        self.sel = 0, 0
        self.s = ''
        self.supportsHighLevelInterface = True
        self.widget = None # This ivar must exist, and be None.
    
    def __repr__(self):
        return '<BrowserStringTextWrapper: %s %s>' % (id(self), self.name)
    
    def getName(self):
        '''BrowserStringTextWrapper.'''
        return self.name # Essential.
        
    
    #@+others
    #@+node:ekr.20181102151431.3: *3* bstw.Clipboard
    def clipboard_clear(self):
        self.message('clipboard-clear')
        g.app.gui.replaceClipboardWith('')

    def clipboard_append(self, s):
        self.message('clipboard-append', s=s)
        s1 = g.app.gui.getTextFromClipboard()
        g.app.gui.replaceClipboardWith(s1 + s)
    #@+node:ekr.20181103055241.1: *3* bstw.Config
    def setStyleClass(self, name):
        self.message('set-style', name=name)

    def tag_configure(self, colorName, **kwargs):
        kwargs['color-name'] = colorName
        self.message('configure-tag', keys=kwargs)
    #@+node:ekr.20181102161648.1: *3* bstw.flashCharacter
    def flashCharacter(self, i, bg='white', fg='red', flashes=3, delay=75):
        self.message('flash-character', i=i,
            bg=bg, fg=fg, flashes=flashes, delay=delay)
    #@+node:ekr.20181103054825.1: *3* bstw.Focus
    def getFocus(self):
        # This isn't in StringTextWrapper.
        self.message('get-focus')

    def setFocus(self):
        self.message('set-focus')
    #@+node:ekr.20181102151431.4: *3* bstw.Insert Point
    def see(self, i):
        self.message('see-position', i=i)

    def seeInsertPoint(self):
        self.message('see-insert-point')
        
    #@+node:ekr.20181103054937.1: *3* bstw.Scrolling
    def getXScrollPosition(self):
        self.message('get-x-scroll')
        return 0

    def getYScrollPosition(self):
        self.message('get-y-scroll')
        return 0
        
    def setXScrollPosition(self, i):
        self.message('set-x-scroll', i=i)
        
    def setYScrollPosition(self, i):
        self.message('set-y-scroll', i=i)
        
    #@+node:ekr.20181102151431.5: *3* bstw.Text
    #@+node:ekr.20181102151431.6: *4* bstw.appendText
    def appendText(self, s):
        '''BrowserStringTextWrapper.'''
        self.s = self.s + s
        self.ins = len(self.s)
        self.sel = self.ins, self.ins
        self.message('body-append-text', s=s)
    #@+node:ekr.20181102151431.7: *4* bstw.delete
    def delete(self, i, j=None):
        '''BrowserStringTextWrapper.'''
        i = self.toPythonIndex(i)
        if j is None: j = i + 1
        j = self.toPythonIndex(j)
        # This allows subclasses to use this base class method.
        if i > j: i, j = j, i
        s = self.getAllText()
        self.setAllText(s[: i] + s[j:])
        # Bug fix: 2011/11/13: Significant in external tests.
        self.setSelectionRange(i, i, insert=i)
        # g.trace('(BrowserStringTextWrapper)')
        self.message('body-delete-text',
            s=s[:i]+s[j:],
            sel=(i,i,i))
    #@+node:ekr.20181102151431.8: *4* bstw.deleteTextSelection
    def deleteTextSelection(self):
        '''BrowserStringTextWrapper.'''
        i, j = self.getSelectionRange()
        self.delete(i, j)
    #@+node:ekr.20181102151431.9: *4* bstw.get
    def get(self, i, j=None):
        '''BrowserStringTextWrapper.'''
        i = self.toPythonIndex(i)
        if j is None:
            j = i + 1
        j = self.toPythonIndex(j)
        s = self.s[i: j]
        self.message('body-get-text', s=s)
        return g.toUnicode(s)
    #@+node:ekr.20181102151431.10: *4* bstw.getAllText
    def getAllText(self):
        '''BrowserStringTextWrapper.'''
        s = self.s
        self.message('body-get-all-text')
        return g.toUnicode(s)
    #@+node:ekr.20181102151431.11: *4* bstw.getInsertPoint
    def getInsertPoint(self):
        '''BrowserStringTextWrapper.'''
        # self.message('body-get-insert-point')
        i = self.ins
        if i is None:
            if self.virtualInsertPoint is None:
                i = 0
            else:
                i = self.virtualInsertPoint
        self.virtualInsertPoint = i
        return i
    #@+node:ekr.20181102151431.12: *4* bstw.getSelectedText
    def getSelectedText(self):
        '''BrowserStringTextWrapper.'''
        # self.message('body-get-selected-text')
        i, j = self.sel
        s = self.s[i: j]
        return g.toUnicode(s)
    #@+node:ekr.20181102151431.13: *4* bstw.getSelectionRange
    def getSelectionRange(self, sort=True):
        '''BrowserStringTextWrapper'''
        # self.message('body-get-selection-range')
        sel = self.sel
        if len(sel) == 2 and sel[0] >= 0 and sel[1] >= 0:
            i, j = sel
            if sort and i > j:
                sel = j, i
            return sel
        else:
            i = self.ins
            return i, i
    #@+node:ekr.20181102151431.14: *4* bstw.hasSelection
    def hasSelection(self):
        '''BrowserStringTextWrapper.'''
        # self.message('body-has-selection')
        i, j = self.getSelectionRange()
        return i != j
    #@+node:ekr.20181102151431.15: *4* bstw.insert
    def insert(self, i, s):
        '''BrowserStringTextWrapper.'''
        i = self.toPythonIndex(i)
        s1 = s
        self.s = self.s[: i] + s1 + self.s[i:]
        i += len(s1)
        self.ins = i
        self.sel = i, i
    #@+node:ekr.20181102151431.16: *4* bstw.selectAllText
    def selectAllText(self, insert=None):
        '''BrowserStringTextWrapper.'''
        self.setSelectionRange(0, 'end', insert=insert)
    #@+node:ekr.20181102151431.17: *4* bstw.setAllText
    def setAllText(self, s):
        '''BrowserStringTextWrapper.'''
        self.s = s
        i = len(self.s)
        self.ins = i
        self.sel = i, i
    #@+node:ekr.20181102151431.18: *4* bstw.setInsertPoint
    def setInsertPoint(self, pos, s=None):
        '''BrowserStringTextWrapper.'''
        self.virtualInsertPoint = i = self.toPythonIndex(pos)
        self.ins = i
        self.sel = i, i
    #@+node:ekr.20181102151431.19: *4* bstw.setSelectionRange
    def setSelectionRange(self, i, j, insert=None):
        '''BrowserStringTextWrapper.'''
        i, j = self.toPythonIndex(i), self.toPythonIndex(j)
        self.sel = i, j
        self.ins = j if insert is None else self.toPythonIndex(insert)
    #@+node:ekr.20181102151431.20: *4* bstw.toPythonIndex
    def toPythonIndex(self, index):
        '''BrowserStringTextWrapper.'''
        return g.toPythonIndex(self.s, index)
    #@+node:ekr.20181102151431.21: *4* bstw.toPythonIndexRowCol
    def toPythonIndexRowCol(self, index):
        '''BrowserStringTextWrapper.'''
        s = self.getAllText()
        i = self.toPythonIndex(index)
        row, col = g.convertPythonIndexToRowCol(s, i)
        return i, row, col
    #@-others
#@+node:ekr.20181102084258.1: ** class BrowserTree
class BrowserTree(leoFrame.NullTree):

    def __init__(self, frame):
        leoFrame.NullTree.__init__(self, frame=frame)
        self.message = g.app.gui.message
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
    self.message('draw-icon', gnx=p.gnx)
#@+node:ekr.20181102123625.3: *3* bt.edit_widget
def edit_widget(self, p):
    self.message('edit-widget', gnx=p.gnx)
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
    self.message('edit-label', gnx=p.gnx)
    self.endEditLabel()
    if p:
        self.revertHeadline = p.h
            # New in 4.4b2: helps undo.
        wrapper = leoFrame.StringTextWrapper(c=self.c, name='head-wrapper')
        e = None
        return e, wrapper
    else:
        return None, None
#@+node:ekr.20181102124041.1: *3* bt.redraw
def redraw(self, p=None):
    self.message('redraw-tree')
    self.redrawCount += 1
    return p
        # Support for #503: Use string/null gui for unit tests
        
redraw_now = redraw
#@+node:ekr.20181102124332.1: *3* bt.scrollTo
def scrollTo(self, p):
    self.message('scroll-tree', gnx=p.gnx)
#@+node:ekr.20181102123625.7: *3* bt.setHeadline
def setHeadline(self, p, s):
    '''
    Set the actual text of the headline widget.

    This is called from the undo/redo logic to change the text before redrawing.
    '''
    self.message('set-headline', gnx=p.gnx, s=s)
    w = self.edit_widget(p)
    if w:
        w.delete(0, 'end')
        if s.endswith('\n') or s.endswith('\r'):
            s = s[: -1]
        w.insert(0, s)
        self.revertHeadline = s
    else:
        g.trace('-' * 20, 'oops')
#@-others
#@-leo

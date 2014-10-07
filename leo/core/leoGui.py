# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20031218072017.3719: * @file leoGui.py
#@@first
"""
A module containing the base gui-related classes.

These classes hide the details of which gui is actually being used.
Leo's core calls this class to allocate all gui objects.

Plugins may define their own gui classes by setting g.app.gui.
"""
import leo.core.leoGlobals as g
import leo.core.leoFrame as leoFrame
    # for NullGui and StringTextWrapper.
#@+others
#@+node:ekr.20031218072017.3720: ** class LeoGui
class LeoGui:

    """The base class of all gui classes.

    Subclasses are expected to override all do-nothing methods of this class.
    """

    #@+others
    #@+node:ekr.20031218072017.3721: *3* app.gui Birth & death
    #@+node:ekr.20031218072017.3722: *4*  LeoGui.__init__
    def __init__ (self,guiName):
        '''Ctor for the LeoGui class.'''
        # g.trace("LeoGui",guiName,g.callers())
        self.active = None # Used only by qt_gui.
        self.bodyTextWidget = None
        self.consoleOnly = True # True if g.es goes to console.
        self.idleTimeClass = None
        self.isNullGui = False
        self.lastFrame = None
        self.leoIcon = None
        self.mGuiName = guiName
        self.mainLoop = None
        self.plainTextWidget = None
        self.root = None
        self.script = None
        self.splashScreen = None
        self.trace = False
        self.utils = None
        # To keep pylint happy.
        self.ScriptingControllerClass = NullScriptingControllerClass
    #@+node:ekr.20061109212618.1: *3* Must be defined only in base class
    #@+node:ekr.20110605121601.18847: *4* create_key_event (LeoGui)
    def create_key_event (self,c,char,stroke,w,event=None,x=None,y=None,x_root=None,y_root=None):

        # Do not call strokeFromSetting here!
        # For example, this would wrongly convert Ctrl-C to Ctrl-c,
        # in effect, converting a user binding from Ctrl-Shift-C to Ctrl-C.

        return LeoKeyEvent(c,char,event,stroke,w,x,y,x_root,y_root)
    #@+node:ekr.20031218072017.3740: *4* guiName
    def guiName(self):

        try:
            return self.mGuiName
        except:
            return "invalid gui name"
    #@+node:ekr.20031218072017.2231: *4* setScript
    def setScript (self,script=None,scriptFileName=None):

        self.script = script
        self.scriptFileName = scriptFileName
    #@+node:ekr.20110605121601.18845: *4* event_generate (LeoGui)
    def event_generate(self,c,char,shortcut,w):

        event = self.create_key_event(c,char,shortcut,w)
        c.k.masterKeyHandler(event)
        c.outerUpdate()
    #@+node:ekr.20061109212618: *3* Must be defined in subclasses
    #@+node:ekr.20031218072017.3723: *4* app.gui create & destroy
    #@+node:ekr.20031218072017.3725: *5* destroySelf (LeoGui)
    def destroySelf (self):

        self.oops()
    #@+node:ekr.20031218072017.3729: *5* runMainLoop
    def runMainLoop(self):

        """Run the gui's main loop."""

        self.oops()
    #@+node:ekr.20031218072017.3730: *4* app.gui dialogs
    def runAboutLeoDialog(self,c,version,theCopyright,url,email):
        """Create and run Leo's About Leo dialog."""
        self.oops()

    def runAskLeoIDDialog(self):
        """Create and run a dialog to get g.app.LeoID."""
        self.oops()

    def runAskOkDialog(self,c,title,message=None,text="Ok"):
        """Create and run an askOK dialog ."""
        self.oops()

    def runAskOkCancelNumberDialog(self,c,title,message,cancelButtonText=None,okButtonText=None):
        """Create and run askOkCancelNumber dialog ."""
        self.oops()

    def runAskOkCancelStringDialog(self,c,title,message,cancelButtonText=None,
                                   okButtonText=None,default=""):
        """Create and run askOkCancelString dialog ."""
        self.oops()

    def runAskYesNoDialog(self,c,title,message=None,yes_all=False,no_all=False):
        """Create and run an askYesNo dialog."""
        self.oops()

    def runAskYesNoCancelDialog(self,c,title,
        message=None,yesMessage="Yes",noMessage="No",yesToAllMessage=None,defaultButton="Yes"):
        """Create and run an askYesNoCancel dialog ."""
        self.oops()

    def runPropertiesDialog(self,title='Properties', data={}, callback=None, buttons=None):
        """Dispay a modal TkPropertiesDialog"""
        self.oops()
    #@+node:ekr.20031218072017.3731: *4* app.gui file dialogs
    def runOpenFileDialog(self,title,filetypes,defaultextension,multiple=False,startpath=None):

        """Create and run an open file dialog ."""

        self.oops()

    def runSaveFileDialog(self,initialfile,title,filetypes,defaultextension):

        """Create and run a save file dialog ."""

        self.oops()
    #@+node:ekr.20031218072017.3732: *4* app.gui panels
    def createColorPanel(self,c):
        """Create a color panel"""
        self.oops()

    def createComparePanel(self,c):
        """Create Compare panel."""
        self.oops()

    def createFindTab (self,c,parentFrame):
        """Create a find tab in the indicated frame."""
        self.oops()

    def createFontPanel (self,c):
        """Create a hidden Font panel."""
        self.oops()

    def createLeoFrame(self,c,title):
        """Create a new Leo frame."""
        self.oops()
    #@+node:ekr.20031218072017.3733: *4* app.gui utils
    #@+at Subclasses are expected to subclass all of the following methods.
    # 
    # These are all do-nothing methods: callers are expected to check for
    # None returns.
    # 
    # The type of commander passed to methods depends on the type of frame
    # or dialog being created. The commander may be a Commands instance or
    # one of its subcommanders.
    #@+node:ekr.20031218072017.3734: *5* Clipboard (LeoGui)
    def replaceClipboardWith (self,s):

        self.oops()

    def getTextFromClipboard (self):

        self.oops()
    #@+node:ekr.20031218072017.3735: *5* Dialog utils
    def attachLeoIcon (self,window):
        """Attach the Leo icon to a window."""
        self.oops()

    def center_dialog(self,dialog):
        """Center a dialog."""
        self.oops()

    def create_labeled_frame (self,parent,caption=None,relief="groove",bd=2,padx=0,pady=0):
        """Create a labeled frame."""
        self.oops()

    def get_window_info (self,window):
        """Return the window information."""
        self.oops()
    #@+node:ekr.20070212145124: *5* getFullVersion (LeoGui)
    def getFullVersion (self,c=None):

        return 'LeoGui: dummy version'
    #@+node:ekr.20031218072017.3737: *5* Focus
    def get_focus(self,frame):
        """Return the widget that has focus, or the body widget if None."""
        self.oops()

    def set_focus(self,commander,widget):
        """Set the focus of the widget in the given commander if it needs to be changed."""
        self.oops()
    #@+node:ekr.20031218072017.3736: *5* Font (LeoGui)
    def getFontFromParams(self,family,size,slant,weight,defaultSize=12):

        # g.trace('g.app.gui',g.callers()) # 'family',family,'size',size,'defaultSize',defaultSize,
        self.oops()
    #@+node:ekr.20031218072017.3739: *5* Idle time
    def setIdleTimeHook (self):
        pass
        
    setIdleTimeHookAfterDelay = setIdleTimeHook
    #@+node:ekr.20070212070820: *5* makeScriptButton
    def makeScriptButton (self,c,
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
    #@+node:ekr.20070228154059: *3* May be defined in subclasses
    #@+node:ekr.20110613103140.16423: *4* dismiss_spash_screen (LeoGui)
    def dismiss_splash_screen (self):

        pass # May be overridden in subclasses.
    #@+node:ekr.20070219084912: *4* finishCreate (LeoGui)
    def finishCreate (self):
        # This may be overridden in subclasses.
        pass
    #@+node:ekr.20101028131948.5861: *4* killPopupMenu & postPopupMenu
    # These definitions keeps pylint happy.

    def postPopupMenu(self,*args,**keys):
        pass
    #@+node:ekr.20031218072017.3741: *4* oops
    def oops (self):

        # It is not usually an error to call methods of this class.
        # However, this message is useful when writing gui plugins.
        if 1:
            g.pr("LeoGui oops", g.callers(4), "should be overridden in subclass")
    #@+node:ekr.20051206103652: *4* widget_name (LeoGui)
    def widget_name (self,w):

        # First try the widget's getName method.
        if not 'w':
            return '<no widget>'
        elif hasattr(w,'getName'):
            return w.getName()
        elif hasattr(w,'_name'):
            return w._name
        else:
            return repr(w)
    #@+node:tbrown.20110618095626.22068: *4* ensure_commander_visible
    def ensure_commander_visible(self, c):
        """E.g. if commanders are in tabs, make sure c's tab is visible"""
        pass
    #@-others
#@+node:ekr.20070228160107: ** class LeoKeyEvent
class LeoKeyEvent:
    '''A gui-independent wrapper for gui events.'''
    #@+others
    #@+node:ekr.20110605121601.18846: *3* LeoKeyEvent.__init__
    def __init__ (self,c,char,event,shortcut,w,x,y,x_root,y_root):
        '''Ctor for LeoKeyEvent class.'''
        trace = False and not g.unitTesting
        if g.isStroke(shortcut):
            g.trace('***** (LeoKeyEvent) oops: already a stroke',shortcut,g.callers())
            stroke = shortcut
        else:
            stroke = g.KeyStroke(shortcut) if shortcut else None
        assert g.isStrokeOrNone(stroke),'(LeoKeyEvent) %s %s' % (
            repr(stroke),g.callers())
        if trace: g.trace('(LeoKeyEvent) stroke',stroke)
        self.c = c
        self.char = char or ''
        self.event = event # New in Leo 4.11.
        self.stroke = stroke
        self.w = self.widget = w
        # Optional ivars
        self.x = x
        self.y = y
        # Support for fastGotoNode plugin
        self.x_root = x_root
        self.y_root = y_root
    #@+node:ekr.20140907103315.18774: *3* LeoKeyEvent.__repr__
    def __repr__ (self):
        return 'LeoKeyEvent: stroke: %s, char: %s, w: %s' % (
            repr(self.stroke),repr(self.char),repr(self.w))
    #@+node:ekr.20140907103315.18775: *3* LeoKeyEvent.type
    def type(self):
        return 'LeoKeyEvent'
    #@-others
#@+node:ekr.20031218072017.2223: ** class NullGui (LeoGui)
class NullGui(LeoGui):
    """Null gui class."""
    #@+others
    #@+node:ekr.20031218072017.2224: *3* Birth & death (NullGui)
    #@+node:ekr.20031218072017.2225: *4*  NullGui.__init__
    def __init__ (self,guiName='nullGui'):
        '''ctor for the NullGui class.'''
        LeoGui.__init__ (self,guiName)
            # init the base class.
        self.clipboardContents = ''
        self.theDict = {}
        self.focusWidget = None
        self.frameFactory = g.NullObject()
        self.iconimages = {}
        self.insert_char_flag = False
        self.script = None
        self.lastFrame = None
        self.isNullGui = True
        self.bodyTextWidget  = leoFrame.StringTextWrapper
        self.plainTextWidget = leoFrame.StringTextWrapper
    #@+node:ekr.20031218072017.2229: *4* NullGui.runMainLoop
    def runMainLoop(self):
        """Run the null gui's main loop."""
        if self.script:
            frame = self.lastFrame
            g.app.log = frame.log
            # g.es("start of batch script...\n")
            self.lastFrame.c.executeScript(script=self.script)
            # g.es("\nend of batch script")
        else:
            print('**** NullGui.runMainLoop: terminating Leo.')

        # Getting here will terminate Leo.
    #@+node:ekr.20070228155807: *3* NullGui.isTextWidget & isTextWrapper
    def isTextWidget(self,w):
        return True # Must be True for unit tests.

    def isTextWrapper (self,w):
        '''Return True if w is a Text widget suitable for text-oriented commands.'''
        return w and hasattr(w,'supportsHighLevelInterface') and w.supportsHighLevelInterface
    #@+node:ekr.20031218072017.2230: *3* oops (NullGui)
    def oops(self):

        """Default do-nothing method for NullGui class.

        It is NOT an error to use this method."""

        # It is not usually an error to call methods of this class.
        # However, this message is useful when writing gui plugins.
        if 1:
            g.trace("NullGui",g.callers(4))
    #@+node:ekr.20070301171901: *3* do nothings (NullGui)
    def alert (self,message):
        pass
    def attachLeoIcon (self,w):
        pass
    def destroySelf (self):
        pass
    def finishCreate (self):
        pass
    def getIconImage (self,name):
        return None
    def getImageImage (self,name):
        return None
    def getTreeImage(self,c,path):
        return None
    def getTextFromClipboard (self):
        return self.clipboardContents
    def get_focus(self,frame=None):
        if not frame: return None
        return self.focusWidget or (hasattr(frame,'body') and frame.body.wrapper) or None 
    def getFontFromParams(self,family,size,slant,weight,defaultSize=12):
        return g.app.config.defaultFont
    def get_window_info (self,window):
        return 0,0,0,0
    def replaceClipboardWith (self,s):
        self.clipboardContents = s
    def set_focus(self,commander,widget):
        self.focusWidget = widget
    #@+node:ekr.20070301172456: *3* app.gui panels (NullGui)
    def createComparePanel(self,c):
        """Create Compare panel."""
        self.oops()

    def createFindTab (self,c,parentFrame):
        """Create a find tab in the indicated frame."""
        pass # Now always done during startup.

    def createLeoFrame(self,c,title):
        """Create a null Leo Frame."""
        gui = self
        self.lastFrame = leoFrame.NullFrame(c,title,gui)
        return self.lastFrame
    #@+node:ekr.20031218072017.3744: *3* dialogs (NullGui)
    def runAboutLeoDialog(self,c,version,theCopyright,url,email):
        return self.simulateDialog("aboutLeoDialog")

    def runAskLeoIDDialog(self):
        return self.simulateDialog("leoIDDialog")

    def runAskOkDialog(self,c,title,message=None,text="Ok"):
        return self.simulateDialog("okDialog","Ok")

    def runAskOkCancelNumberDialog(self,c,title,message,cancelButtonText=None,okButtonText=None):
        return self.simulateDialog("numberDialog",-1)

    def runAskOkCancelStringDialog(self,c,title,message,cancelButtonText=None,
                                   okButtonText=None,default=""):
        return self.simulateDialog("stringDialog",'')

    def runCompareDialog(self,c):
        return self.simulateDialog("compareDialog",'')

    def runOpenFileDialog(self,title,filetypes,defaultextension,multiple=False,startpath=None):
        return self.simulateDialog("openFileDialog")

    def runSaveFileDialog(self,initialfile,title,filetypes,defaultextension):
        return self.simulateDialog("saveFileDialog")

    def runAskYesNoDialog(self,c,title,message=None,yes_all=False,no_all=False):
        return self.simulateDialog("yesNoDialog","no")

    def runAskYesNoCancelDialog(self,c,title,
        message=None,yesMessage="Yes",noMessage="No",yesToAllMessage=None,defaultButton="Yes"):
        return self.simulateDialog("yesNoCancelDialog","cancel")
    #@+node:ekr.20100521090440.5893: *3* onActivateEvent/onDeactivateEvent (NullGui)
    def onActivateEvent (self,*args,**keys):
        pass

    def onDeactivateEvent(self,*args,**keys):
        pass
    #@+node:ekr.20031218072017.3747: *3* simulateDialog
    def simulateDialog (self,key,defaultVal=None):

        val = self.theDict.get(key,defaultVal)

        if self.trace:
            g.pr(key, val)

        return val
    #@-others
#@+node:ekr.20080707150137.5: ** class NullScriptingControllerClass
class NullScriptingControllerClass:

    '''A default, do-nothing class to be overridden by mod_scripting or other plugins.

    This keeps pylint happy.'''

    def __init__ (self,c,iconBar=None):

        self.c = c
        self.iconBar = iconBar

    def createAllButtons(self):

        pass

#@+node:ekr.20031218072017.3742: ** class UnitTestGui (NullGui)
class UnitTestGui(NullGui):
    '''A gui class for use by unit tests.'''
    # Presently used only by the import/export unit tests.
    #@+others
    #@+node:ekr.20031218072017.3743: *3*  ctor (UnitTestGui)
    def __init__ (self,theDict=None,trace=False):
        '''ctor for the UnitTestGui class.'''
        self.oldGui = g.app.gui
        # Init the base class
        NullGui.__init__ (self,"UnitTestGui")
        # Use the same kind of widgets as the old gui.
        self.bodyTextWidget = self.oldGui.bodyTextWidget
        self.plainTextWidget = self.oldGui.plainTextWidget
        if theDict is None: theDict = {}
        self.theDict = theDict
        self.trace = trace
        g.app.gui = self

    def destroySelf (self):
        g.app.gui = self.oldGui
    #@+node:ekr.20071128094234.1: *3* createSpellTab
    def createSpellTab(self,c,spellHandler,tabName):

        pass # This method keeps pylint happy.
    #@+node:ekr.20111001155050.15484: *3* runAtIdle
    if 1: # Huh?

        def runAtIdle (self,aFunc):
        
            '''Run aFunc immediately for a unit test.
        
            This is a kludge, but it is probably the best that can be done.
            '''
        
            aFunc()
    #@+node:ekr.20081119083601.1: *3* toUnicode
    def toUnicode (self,s):

        if g.isPython3:
            return str(s)
        else:
            return unicode(s)
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo

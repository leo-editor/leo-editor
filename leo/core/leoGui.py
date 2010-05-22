# -*- coding: utf-8 -*-
#@+leo-ver=4-thin
#@+node:ekr.20031218072017.3719:@thin leoGui.py
#@@first

"""A module containing the base leoGui class.

This class and its subclasses hides the details of which gui is actually being used.
Leo's core calls this class to allocate all gui objects.

Plugins may define their own gui classes by setting g.app.gui."""

#@@language python
#@@tabwidth -4
#@@pagewidth 70

import leo.core.leoGlobals as g
import leo.core.leoFind as leoFind # for nullFindTab.
import leo.core.leoFrame as leoFrame # for nullGui.

#@+others
#@+node:ekr.20031218072017.3720:class leoGui
class leoGui:

    """The base class of all gui classes.

    Subclasses are expected to override all do-nothing methods of this class."""

    #@    << define leoGui file types >>
    #@+node:ekr.20040131103531:<< define leoGui file types >> (not used yet)
    allFullFiletypes = [
        ("All files",   "*"),
        ("C/C++ files", "*.c"),
        ("C/C++ files", "*.cpp"),
        ("C/C++ files", "*.h"),
        ("C/C++ files", "*.hpp"),
        ("Java files",  "*.java"),
        ("Lua files",   "*.lua"),
        ("Pascal files","*.pas"),
        ("Python files","*.py")]
        # To do: *.php, *.php3, *.php4")
    pythonFullFiletypes = [
        ("Python files","*.py"),
        ("All files","*"),
        ("C/C++ files","*.c"),
        ("C/C++ files","*.cpp"),
        ("C/C++ files","*.h"),
        ("C/C++ files","*.hpp"),
        ("Java files","*.java"),
        ("Lua files",   "*.lua"),
        ("Pascal files","*.pas")]
        # To do: *.php, *.php3, *.php4")
    textFullFiletypes = [
        ("Text files","*.txt"),
        ("C/C++ files","*.c"),
        ("C/C++ files","*.cpp"),
        ("C/C++ files","*.h"),
        ("C/C++ files","*.hpp"),
        ("Java files","*.java"),
        ("Lua files",   "*.lua"),
        ("Pascal files","*.pas"),
        ("Python files","*.py"),
        ("All files","*")]
        # To do: *.php, *.php3, *.php4")
    CWEBTextAllFiletypes = [
        ("CWEB files","*.w"),
        ("Text files","*.txt"),
        ("All files", "*")]
    leoAllFiletypes = [
        ("Leo files","*.leo"),
        ("All files","*")]
    leoFiletypes = [
        ("Leo files","*.leo")]
    nowebTextAllFiletypes = [
        ("Noweb files","*.nw"),
        ("Text files", "*.txt"),
        ("All files",  "*")]
    textAllFiletypes = [
        ("Text files","*.txt"),
        ("All files", "*")]
    #@-node:ekr.20040131103531:<< define leoGui file types >> (not used yet)
    #@nl

    #@    @+others
    #@+node:ekr.20031218072017.3721:app.gui Birth & death
    #@+node:ekr.20031218072017.3722: leoGui.__init__
    def __init__ (self,guiName):

        # g.trace("leoGui",guiName,g.callers())

        self.lastFrame = None
        self.leoIcon = None
        self.mGuiName = guiName
        self.mainLoop = None
        self.root = None
        self.script = None
        self.utils = None
        self.isNullGui = False
        self.bodyTextWidget = None
        self.plainTextWidget = None
        self.trace = False

        # To keep pylint happy.
        self.ScriptingControllerClass = nullScriptingControllerClass
    #@-node:ekr.20031218072017.3722: leoGui.__init__
    #@+node:ekr.20061109211054:leoGui.mustBeDefinedOnlyInBaseClass
    mustBeDefinedOnlyInBaseClass = (
        'guiName',
        'oops',
        'setScript',
        'widget_name',
    )
    #@nonl
    #@-node:ekr.20061109211054:leoGui.mustBeDefinedOnlyInBaseClass
    #@+node:ekr.20061109211022:leoGui.mustBeDefinedInSubclasses
    mustBeDefinedInSubclasses = (
        # Startup & shutdown
        'attachLeoIcon',
        'center_dialog',
        'color',
        #'createComparePanel',          # optional
        #'createFindPanel',             # optional
        'createFindTab',
        'createKeyHandlerClass',
        'createLeoFrame',
        'createRootWindow',
        'create_labeled_frame',
        'destroySelf',
        'eventChar',
        'eventKeysym',
        'eventWidget',
        'eventXY',
        # 'finishCreate', # optional.
        # 'getFontFromParams', # optional
        # 'getFullVersion', # optional.
        'getTextFromClipboard',
        'get_focus',
        'get_window_info',
        'isTextWidget',
        'keysym',
        'killGui',
        # 'makeScriptButton', # optional
        'recreateRootWindow',
        'replaceClipboardWith',
        'runAboutLeoDialog',
        'runAskLeoIDDialog',
        'runAskOkCancelNumberDialog',
        'runAskOkDialog',
        'runAskYesNoCancelDialog',
        'runAskYesNoDialog',
        'runMainLoop',
        'runOpenFileDialog',
        'runSaveFileDialog',
        'set_focus',
        #'setIdleTimeHook',             # optional       
        #'setIdleTimeHookAfterDelay',   # optional
    )
    #@-node:ekr.20061109211022:leoGui.mustBeDefinedInSubclasses
    #@-node:ekr.20031218072017.3721:app.gui Birth & death
    #@+node:ekr.20061109212618.1:Must be defined only in base class
    #@+node:ekr.20031218072017.3740:guiName
    def guiName(self):

        try:
            return self.mGuiName
        except:
            return "invalid gui name"
    #@-node:ekr.20031218072017.3740:guiName
    #@+node:ekr.20031218072017.2231:setScript
    def setScript (self,script=None,scriptFileName=None):

        self.script = script
        self.scriptFileName = scriptFileName
    #@-node:ekr.20031218072017.2231:setScript
    #@-node:ekr.20061109212618.1:Must be defined only in base class
    #@+node:ekr.20061109212618:Must be defined in subclasses
    #@+node:ekr.20031218072017.3723:app.gui create & destroy
    #@+node:ekr.20031218072017.3724:createRootWindow
    def createRootWindow(self):

        """Create the hidden root window for the gui.

        Nothing needs to be done if the root window need not exist."""

        self.oops()
    #@-node:ekr.20031218072017.3724:createRootWindow
    #@+node:ekr.20031218072017.3725:destroySelf
    def destroySelf (self):

        self.oops()
    #@-node:ekr.20031218072017.3725:destroySelf
    #@+node:ekr.20031218072017.3727:killGui
    def killGui(self,exitFlag=True):

        """Destroy the gui.

        The entire Leo application should terminate if exitFlag is True."""

        self.oops()
    #@-node:ekr.20031218072017.3727:killGui
    #@+node:ekr.20031218072017.3728:recreateRootWindow
    def recreateRootWindow(self):

        """Create the hidden root window of the gui
        after a previous gui has terminated with killGui(False)."""

        self.oops()
    #@-node:ekr.20031218072017.3728:recreateRootWindow
    #@+node:ekr.20031218072017.3729:runMainLoop
    def runMainLoop(self):

        """Run the gui's main loop."""

        self.oops()
    #@-node:ekr.20031218072017.3729:runMainLoop
    #@-node:ekr.20031218072017.3723:app.gui create & destroy
    #@+node:ekr.20031218072017.3730:app.gui dialogs
    def runAboutLeoDialog(self,c,version,theCopyright,url,email):
        """Create and run Leo's About Leo dialog."""
        self.oops()

    def runAskLeoIDDialog(self):
        """Create and run a dialog to get g.app.LeoID."""
        self.oops()

    def runAskOkDialog(self,c,title,message=None,text="Ok"):
        """Create and run an askOK dialog ."""
        self.oops()

    def runAskOkCancelNumberDialog(self,c,title,message):
        """Create and run askOkCancelNumber dialog ."""
        self.oops()

    def runAskOkCancelStringDialog(self,c,title,message):
        """Create and run askOkCancelString dialog ."""
        self.oops()

    def runAskYesNoDialog(self,c,title,message=None):
        """Create and run an askYesNo dialog."""
        self.oops()

    def runAskYesNoCancelDialog(self,c,title,
        message=None,yesMessage="Yes",noMessage="No",defaultButton="Yes"):
        """Create and run an askYesNoCancel dialog ."""
        self.oops()

    def runPropertiesDialog(self,title='Properties', data={}, callback=None, buttons=None):
        """Dispay a modal TkPropertiesDialog"""
        self.oops()
    #@nonl
    #@-node:ekr.20031218072017.3730:app.gui dialogs
    #@+node:ekr.20061031173016:app.gui.createKeyHandlerClass
    def createKeyHandlerClass (self,c,useGlobalKillbuffer=True,useGlobalRegisters=True):

        self.oops()

        # import leo.core.leoKeys as leoKeys # Do this here to break a circular dependency.

        # return leoKeys.keyHandlerClass(c,useGlobalKillbuffer,useGlobalRegisters)
    #@nonl
    #@-node:ekr.20061031173016:app.gui.createKeyHandlerClass
    #@+node:ekr.20031218072017.3731:app.gui file dialogs
    def runOpenFileDialog(self,title,filetypes,defaultextension,multiple=False):

        """Create and run an open file dialog ."""

        self.oops()

    def runSaveFileDialog(self,initialfile,title,filetypes,defaultextension):

        """Create and run a save file dialog ."""

        self.oops()
    #@-node:ekr.20031218072017.3731:app.gui file dialogs
    #@+node:ekr.20031218072017.3732:app.gui panels
    def createColorPanel(self,c):
        """Create a color panel"""
        self.oops()

    def createComparePanel(self,c):
        """Create Compare panel."""
        self.oops()

    def createFindPanel(self,c):
        """Create a hidden Find panel."""
        self.oops()

    def createFindTab (self,c,parentFrame):
        """Create a find tab in the indicated frame."""
        self.oops()

    def createFontPanel (self,c):
        """Create a hidden Font panel."""
        self.oops()

    def createLeoFrame(self,title):
        """Create a new Leo frame."""
        self.oops()
    #@-node:ekr.20031218072017.3732:app.gui panels
    #@+node:ekr.20031218072017.3733:app.gui utils
    #@+at 
    #@nonl
    # Subclasses are expected to subclass all of the following 
    # methods.
    # 
    # These are all do-nothing methods: callers are expected to 
    # check for None returns.
    # 
    # The type of commander passed to methods depends on the type of 
    # frame or dialog being created.  The commander may be a 
    # Commands instance or one of its subcommanders.
    #@-at
    #@+node:ekr.20031218072017.3734:Clipboard (leoGui)
    def replaceClipboardWith (self,s):

        self.oops()

    def getTextFromClipboard (self):

        self.oops()
    #@-node:ekr.20031218072017.3734:Clipboard (leoGui)
    #@+node:ekr.20061031132712.1:color
    # g.es calls gui.color to do the translation,
    # so most code in Leo's core can simply use Tk color names.

    def color (self,color):
        '''Return the gui-specific color corresponding to the Tk color name.'''
        return color # Do not call oops: this method is essential for the config classes.
    #@-node:ekr.20061031132712.1:color
    #@+node:ekr.20031218072017.3735:Dialog utils
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
    #@-node:ekr.20031218072017.3735:Dialog utils
    #@+node:ekr.20061031132907:Events (leoGui)
    def event_generate(self,w,kind,*args,**keys):
        '''Generate an event.'''
        # g.trace('baseGui','kind',kind,'args,keys',*args,**keys)
        return w.event_generate(kind,*args,**keys)

    def eventChar (self,event,c=None):
        '''Return the char field of an event.'''
        return event and event.char or ''

    def eventKeysym (self,event,c=None):
        '''Return the keysym value of an event.'''
        return event and event.keysym

    def eventStroke (self,event,c=None):
        return event and hasattr(event,'stroke') and event.stroke or ''

    def eventWidget (self,event,c=None):
        '''Return the widget field of an event.'''
        return event and event.widget

    def eventXY (self,event,c=None):
        if event:
            return event.x,event.y
        else:
            return 0,0
    #@-node:ekr.20061031132907:Events (leoGui)
    #@+node:ekr.20070212145124:getFullVersion
    def getFullVersion (self,c=None):

        return 'leoGui: dummy version'
    #@-node:ekr.20070212145124:getFullVersion
    #@+node:ekr.20031218072017.3737:Focus
    def get_focus(self,frame):
        """Return the widget that has focus, or the body widget if None."""
        self.oops()

    def set_focus(self,commander,widget):
        """Set the focus of the widget in the given commander if it needs to be changed."""
        self.oops()
    #@-node:ekr.20031218072017.3737:Focus
    #@+node:ekr.20031218072017.3736:Font (leoGui)
    def getFontFromParams(self,family,size,slant,weight,defaultSize=12):

        # g.trace('g.app.gui',g.callers()) # 'family',family,'size',size,'defaultSize',defaultSize,
        self.oops()
    #@-node:ekr.20031218072017.3736:Font (leoGui)
    #@+node:ekr.20031218072017.3739:Idle time
    def setIdleTimeHook (self,idleTimeHookHandler):

        # g.pr('leoGui:setIdleTimeHook')
        pass # Not an error.

    def setIdleTimeHookAfterDelay (self,idleTimeHookHandler):

        # g.pr('leoGui:setIdleTimeHookAfterDelay')
        pass # Not an error.
    #@-node:ekr.20031218072017.3739:Idle time
    #@+node:ekr.20070212070820:makeScriptButton
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
    #@-node:ekr.20070212070820:makeScriptButton
    #@-node:ekr.20031218072017.3733:app.gui utils
    #@-node:ekr.20061109212618:Must be defined in subclasses
    #@+node:ekr.20070228154059:May be defined in subclasses
    #@+node:ekr.20070219084912:finishCreate (may be overridden in subclasses)
    def finishCreate (self):

        pass
    #@nonl
    #@-node:ekr.20070219084912:finishCreate (may be overridden in subclasses)
    #@+node:ekr.20031218072017.3741:oops
    def oops (self):

        # It is not usually an error to call methods of this class.
        # However, this message is useful when writing gui plugins.
        if 1:
            g.pr("leoGui oops", g.callers(4), "should be overridden in subclass")
    #@-node:ekr.20031218072017.3741:oops
    #@+node:ekr.20051206103652:widget_name (leoGui)
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
    #@-node:ekr.20051206103652:widget_name (leoGui)
    #@+node:ekr.20070228160107:class leoKeyEvent (leoGui)
    class leoKeyEvent:

        '''A gui-independent wrapper for gui events.'''

        def __init__ (self,event,c,stroke=None):

            # g.trace('leoKeyEvent(leoGui)')
            self.actualEvent = event
            self.c      = c # Required to access c.k tables.
            self.char   = hasattr(event,'char') and event.char or ''
            self.keysym = hasattr(event,'keysym') and event.keysym or ''
            self.state  = hasattr(event,'state') and event.state or 0
            self.stroke = hasattr(event,'stroke') and event.stroke or ''
            self.w      = hasattr(event,'widget') and event.widget or None
            self.x      = hasattr(event,'x') and event.x or 0
            self.y      = hasattr(event,'y') and event.y or 0
            # Support for fastGotoNode plugin
            self.x_root = hasattr(event,'x_root') and event.x_root or 0
            self.y_root = hasattr(event,'y_root') and event.y_root or 0

            if self.keysym and c.k:
                # Translate keysyms for ascii characters to the character itself.
                self.keysym = c.k.guiBindNamesInverseDict.get(self.keysym,self.keysym)

            if stroke and not self.stroke:
                self.stroke = self.actualEvent.stroke = stroke

            self.widget = self.w

        def __repr__ (self):

            if self.stroke:
                return 'leoGui.leoKeyEvent: stroke: %s' % (repr(self.stroke))
            else:
                return 'leoGui.leoKeyEvent: char: %s, keysym: %s' % (
                    repr(self.char),repr(self.keysym))
    #@nonl
    #@-node:ekr.20070228160107:class leoKeyEvent (leoGui)
    #@-node:ekr.20070228154059:May be defined in subclasses
    #@-others
#@-node:ekr.20031218072017.3720:class leoGui
#@+node:ekr.20031218072017.2223:class nullGui (leoGui)
class nullGui(leoGui):

    """Null gui class."""

    #@    @+others
    #@+node:ekr.20031218072017.2224:Birth & death
    #@+node:ekr.20031218072017.2225: nullGui.__init__
    def __init__ (self,guiName):

        leoGui.__init__ (self,guiName) # init the base class.

        self.clipboardContents = ''
        self.theDict = {}
        self.focusWidget = None
        self.script = None
        self.lastFrame = None
        self.isNullGui = True
        self.bodyTextWidget  = leoFrame.stringTextWidget
        self.plainTextWidget = leoFrame.stringTextWidget
    #@-node:ekr.20031218072017.2225: nullGui.__init__
    #@+node:ekr.20070123092623:nullGui.createKeyHandlerClass
    def createKeyHandlerClass (self,c,useGlobalKillbuffer=True,useGlobalRegisters=True):

        import leo.core.leoKeys as leoKeys # Do this here to break a circular dependency.

        return leoKeys.keyHandlerClass(c,useGlobalKillbuffer,useGlobalRegisters)
    #@nonl
    #@-node:ekr.20070123092623:nullGui.createKeyHandlerClass
    #@+node:ekr.20031218072017.2229:runMainLoop
    def runMainLoop(self):

        """Run the gui's main loop."""

        if self.script:
            frame = self.lastFrame
            g.app.log = frame.log
            # g.es("start of batch script...\n")
            self.lastFrame.c.executeScript(script=self.script)
            # g.es("\nend of batch script")

        # Getting here will terminate Leo.
    #@-node:ekr.20031218072017.2229:runMainLoop
    #@-node:ekr.20031218072017.2224:Birth & death
    #@+node:ekr.20070228155807:isTextWidget
    def isTextWidget (self,w):

        '''Return True if w is a Text widget suitable for text-oriented commands.'''

        return w and isinstance(w,leoFrame.baseTextWidget)
    #@-node:ekr.20070228155807:isTextWidget
    #@+node:ekr.20031218072017.2230:oops
    def oops(self):

        """Default do-nothing method for nullGui class.

        It is NOT an error to use this method."""

        # It is not usually an error to call methods of this class.
        # However, this message is useful when writing gui plugins.
        if 1:
            g.trace("nullGui",g.callers(4))
    #@-node:ekr.20031218072017.2230:oops
    #@+node:ekr.20070301171901:do nothings
    def alert (self,message):
        pass

    def attachLeoIcon (self,w):
        pass

    def createRootWindow(self):
        pass

    def destroySelf (self):
        pass

    def finishCreate (self):
        pass

    def getIconImage (self, name):
        return None

    def getTreeImage(self,c,path):
        return None

    def getTextFromClipboard (self):
        return self.clipboardContents

    def get_focus(self,frame=None):
        if not frame: return None
        return self.focusWidget or (hasattr(frame,'body') and frame.body.bodyCtrl) or None 

    def getFontFromParams(self,family,size,slant,weight,defaultSize=12):
        return g.app.config.defaultFont

    def get_window_info (self,window):
        return 0,0,0,0

    def replaceClipboardWith (self,s):
        self.clipboardContents = s

    def set_focus(self,commander,widget):
        self.focusWidget = widget
    #@-node:ekr.20070301171901:do nothings
    #@+node:ekr.20070301172456:app.gui panels
    def createComparePanel(self,c):
        """Create Compare panel."""
        self.oops()

    def createFindPanel(self,c):
        """Create a hidden Find panel."""
        self.oops()

    def createFindTab (self,c,parentFrame):
        """Create a find tab in the indicated frame."""
        return leoFind.nullFindTab(c,parentFrame)

    def createLeoFrame(self,title):
        """Create a null Leo Frame."""
        gui = self
        self.lastFrame = leoFrame.nullFrame(title,gui)
        return self.lastFrame
    #@-node:ekr.20070301172456:app.gui panels
    #@+node:ekr.20031218072017.3744:dialogs (nullGui)
    def runAboutLeoDialog(self,c,version,theCopyright,url,email):
        return self.simulateDialog("aboutLeoDialog")

    def runAskLeoIDDialog(self):
        return self.simulateDialog("leoIDDialog")

    def runAskOkDialog(self,c,title,message=None,text="Ok"):
        return self.simulateDialog("okDialog","Ok")

    def runAskOkCancelNumberDialog(self,c,title,message):
        return self.simulateDialog("numberDialog",-1)

    def runAskOkCancelStringDialog(self,c,title,message):
        return self.simulateDialog("stringDialog",'')

    def runCompareDialog(self,c):
        return self.simulateDialog("compareDialog",'')

    def runOpenFileDialog(self,title,filetypes,defaultextension,multiple=False):
        return self.simulateDialog("openFileDialog")

    def runSaveFileDialog(self,initialfile,title,filetypes,defaultextension):
        return self.simulateDialog("saveFileDialog")

    def runAskYesNoDialog(self,c,title,message=None):
        return self.simulateDialog("yesNoDialog","no")

    def runAskYesNoCancelDialog(self,c,title,
        message=None,yesMessage="Yes",noMessage="No",defaultButton="Yes"):
        return self.simulateDialog("yesNoCancelDialog","cancel")
    #@-node:ekr.20031218072017.3744:dialogs (nullGui)
    #@+node:ekr.20100521090440.5893:onActivate/DeactivateEvent
    def onActivateEvent (self,*args,**keys):
        pass

    def onDeactivateEvent(self,*args,**keys):
        pass
    #@-node:ekr.20100521090440.5893:onActivate/DeactivateEvent
    #@+node:ekr.20031218072017.3747:simulateDialog
    def simulateDialog (self,key,defaultVal=None):

        val = self.theDict.get(key,defaultVal)

        if self.trace:
            g.pr(key, val)

        return val
    #@-node:ekr.20031218072017.3747:simulateDialog
    #@-others
#@-node:ekr.20031218072017.2223:class nullGui (leoGui)
#@+node:ekr.20080707150137.5:class nullScriptingControllerClass
class nullScriptingControllerClass:

    '''A default, do-nothing class to be overridden by mod_scripting or other plugins.

    This keeps pylint happy.'''

    def __init__ (self,c,iconBar=None):

        self.c = c
        self.iconBar = iconBar

    def createAllButtons(self):

        pass

#@-node:ekr.20080707150137.5:class nullScriptingControllerClass
#@+node:ekr.20031218072017.3742:class unitTestGui (nullGui)
class unitTestGui(nullGui):

    '''A gui class for use by unit tests.'''

    # Presently used only by the import/export unit tests.

    #@    @+others
    #@+node:ekr.20031218072017.3743: ctor (unitTestGui)
    def __init__ (self,theDict=None,trace=False):

        self.oldGui = g.app.gui

        # Init the base class
        nullGui.__init__ (self,"unitTestGui")

        # Use the same kind of widgets as the old gui.
        self.bodyTextWidget = self.oldGui.bodyTextWidget
        self.plainTextWidget = self.oldGui.plainTextWidget

        if theDict is None: theDict = {}
        self.theDict = theDict
        self.trace = trace
        g.app.gui = self

    def destroySelf (self):

        g.app.gui = self.oldGui
    #@-node:ekr.20031218072017.3743: ctor (unitTestGui)
    #@+node:ekr.20071128094234.1:createSpellTab
    def createSpellTab(self,c,spellHandler,tabName):

        pass # This method keeps pylint happy.
    #@-node:ekr.20071128094234.1:createSpellTab
    #@+node:ekr.20081119083601.1:toUnicode
    def toUnicode (self,s):

        if g.isPython3:
            return str(s)
        else:
            return unicode(s)
    #@-node:ekr.20081119083601.1:toUnicode
    #@-others
#@-node:ekr.20031218072017.3742:class unitTestGui (nullGui)
#@-others
#@-node:ekr.20031218072017.3719:@thin leoGui.py
#@-leo

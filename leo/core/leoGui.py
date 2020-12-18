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
from leo.core import leoGlobals as g
from leo.core import leoFrame
    # for NullGui and StringTextWrapper.
#@+others
#@+node:ekr.20031218072017.3720: ** class LeoGui (object)
class LeoGui:
    """The base class of all gui classes.

    Subclasses are expected to override all do-nothing methods of this class.
    """
    #@+others
    #@+node:ekr.20031218072017.3722: *3* LeoGui.__init__
    def __init__(self, guiName):
        """Ctor for the LeoGui class."""
        self.active = None  # Used only by qt_gui.
        self.consoleOnly = True  # True if g.es goes to console.
        self.globalFindTabManager = None
        self.globalFindTab = None
        self.idleTimeClass = None
        self.isNullGui = False
        self.lastFrame = None
        self.leoIcon = None
        self.mGuiName = guiName
        self.mainLoop = None
        self.plainTextWidget = None
            # For SpellTabHandler class only.
        self.root = None
        self.script = None
        self.splashScreen = None
        self.utils = None
        # To keep pylint happy.
        self.ScriptingControllerClass = NullScriptingControllerClass
        #
        # Define special keys that may be overridden is subclasses.
        self.ignoreChars = []
            # Keys that are always to be ignore.
        self.FKeys = []
            # The representation of F-keys.
        self.specialChars = []
            # A list of characters/keys to be handle specially.
    #@+node:ekr.20061109212618.1: *3* LeoGui: Must be defined only in base class
    #@+node:ekr.20110605121601.18847: *4* LeoGui.create_key_event (LeoGui)
    def create_key_event(self, c,
        binding=None, char=None, event=None, w=None,
        x=None, x_root=None,
        y=None, y_root=None,
    ):
        # Do not call strokeFromSetting here!
        # For example, this would wrongly convert Ctrl-C to Ctrl-c,
        # in effect, converting a user binding from Ctrl-Shift-C to Ctrl-C.
        return LeoKeyEvent(c, char, event, binding, w, x, y, x_root, y_root)
    #@+node:ekr.20031218072017.3740: *4* LeoGui.guiName
    def guiName(self):
        try:
            return self.mGuiName
        except Exception:
            return "invalid gui name"
    #@+node:ekr.20031218072017.2231: *4* LeoGui.setScript
    def setScript(self, script=None, scriptFileName=None):
        self.script = script
        self.scriptFileName = scriptFileName
    #@+node:ekr.20110605121601.18845: *4* LeoGui.event_generate (LeoGui)
    def event_generate(self, c, char, shortcut, w):
        event = self.create_key_event(c, binding=shortcut, char=char, w=w)
        c.k.masterKeyHandler(event)
        c.outerUpdate()
    #@+node:ekr.20061109212618: *3* LeoGu: Must be defined in subclasses
    #@+node:ekr.20031218072017.3725: *4* LeoGui.destroySelf
    def destroySelf(self):
        self.oops()
    #@+node:ekr.20031218072017.3730: *4* LeoGui.dialogs
    def runAboutLeoDialog(self, c, version, theCopyright, url, email):
        """Create and run Leo's About Leo dialog."""
        self.oops()

    def runAskLeoIDDialog(self):
        """Create and run a dialog to get g.app.LeoID."""
        self.oops()

    def runAskOkDialog(self, c, title, message=None, text="Ok"):
        """Create and run an askOK dialog ."""
        self.oops()

    def runAskOkCancelNumberDialog(
        self, c, title, message, cancelButtonText=None, okButtonText=None):
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

    def runPropertiesDialog(
        self, title='Properties', data=None, callback=None, buttons=None):
        """Dispay a modal TkPropertiesDialog"""
        self.oops()
    #@+node:ekr.20031218072017.3731: *4* LeoGui.file dialogs
    def runOpenFileDialog(
        self, c, title, filetypes, defaultextension, multiple=False, startpath=None):
        """Create and run an open file dialog ."""
        self.oops()

    def runSaveFileDialog(self, c, initialfile, title, filetypes, defaultextension):
        """Create and run a save file dialog ."""
        self.oops()
    #@+node:ekr.20031218072017.3732: *4* LeoGui.panels
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

    def createLeoFrame(self, c, title):
        """Create a new Leo frame."""
        self.oops()
    #@+node:ekr.20031218072017.3729: *4* LeoGui.runMainLoop
    def runMainLoop(self):
        """Run the gui's main loop."""
        self.oops()
    #@+node:ekr.20031218072017.3733: *4* LeoGui.utils
    #@+at Subclasses are expected to subclass all of the following methods.
    # These are all do-nothing methods: callers are expected to check for
    # None returns.
    # The type of commander passed to methods depends on the type of frame
    # or dialog being created. The commander may be a Commands instance or
    # one of its subcommanders.
    #@+node:ekr.20031218072017.3734: *5* LeoGui.Clipboard
    def replaceClipboardWith(self, s):
        self.oops()

    def getTextFromClipboard(self):
        self.oops()
    #@+node:ekr.20031218072017.3735: *5* LeoGui.Dialog utils
    def attachLeoIcon(self, window):
        """Attach the Leo icon to a window."""
        self.oops()

    def center_dialog(self, dialog):
        """Center a dialog."""
        self.oops()

    def create_labeled_frame(
        self, parent, caption=None, relief="groove", bd=2, padx=0, pady=0):
        """Create a labeled frame."""
        self.oops()

    def get_window_info(self, window):
        """Return the window information."""
        self.oops()
    #@+node:ekr.20031218072017.3737: *5* LeoGui.Focus
    def get_focus(self, *args, **kwargs):
        """Return the widget that has focus, or the body widget if None."""
        self.oops()

    def set_focus(self, commander, widget):
        """Set the focus of the widget in the given commander if it needs to be changed."""
        self.oops()
    #@+node:ekr.20031218072017.3736: *5* LeoGui.Font
    def getFontFromParams(self, family, size, slant, weight, defaultSize=12):

        self.oops()
    #@+node:ekr.20070212145124: *5* LeoGui.getFullVersion
    def getFullVersion(self, c=None):
        return 'LeoGui: dummy version'
    #@+node:ekr.20070212070820: *5* LeoGui.makeScriptButton
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
    #@+node:ekr.20070228154059: *3* LeoGui: May be defined in subclasses
    #@+node:ekr.20110613103140.16423: *4* LeoGui.dismiss_spash_screen
    def dismiss_splash_screen(self):
        pass  # May be overridden in subclasses.
    #@+node:tbrown.20110618095626.22068: *4* LeoGui.ensure_commander_visible
    def ensure_commander_visible(self, c):
        """E.g. if commanders are in tabs, make sure c's tab is visible"""
        pass
    #@+node:ekr.20070219084912: *4* LeoGui.finishCreate
    def finishCreate(self):
        # This may be overridden in subclasses.
        pass
    #@+node:ekr.20101028131948.5861: *4* LeoGui.killPopupMenu & postPopupMenu
    # These definitions keep pylint happy.

    def postPopupMenu(self, *args, **keys):
        pass
    #@+node:ekr.20031218072017.3741: *4* LeoGui.oops
    def oops(self):
        # It is not usually an error to call methods of this class.
        # However, this message is useful when writing gui plugins.
        if 1:
            g.pr("LeoGui oops", g.callers(4), "should be overridden in subclass")
    #@+node:ekr.20170612065049.1: *4* LeoGui.put_help
    def put_help(self, c, s, short_title):
        pass
    #@+node:ekr.20051206103652: *4* LeoGui.widget_name (LeoGui)
    def widget_name(self, w):
        # First try the widget's getName method.
        if not 'w':
            return '<no widget>'
        if hasattr(w, 'getName'):
            return w.getName()
        if hasattr(w, '_name'):
            return w._name
        return repr(w)
    #@-others
#@+node:ekr.20070228160107: ** class LeoKeyEvent (object)
class LeoKeyEvent:
    """A gui-independent wrapper for gui events."""
    #@+others
    #@+node:ekr.20110605121601.18846: *3* LeoKeyEvent.__init__
    def __init__(self, c, char, event, binding, w,
        x=None, y=None, x_root=None, y_root=None
    ):
        """Ctor for LeoKeyEvent class."""
        if g.isStroke(binding):
            g.trace('***** (LeoKeyEvent) oops: already a stroke', binding, g.callers())
            stroke = binding
        else:
            stroke = g.KeyStroke(binding) if binding else None
        assert g.isStrokeOrNone(stroke), f"(LeoKeyEvent) {stroke!r} {g.callers()}"
        if 0: # Doesn't add much.
            if 'keys' in g.app.debug:
                print(f"LeoKeyEvent: binding: {binding}, stroke: {stroke}, char: {char!r}")
        self.c = c
        self.char = char or ''
        self.event = event  # New in Leo 4.11.
        self.stroke = stroke
        self.w = self.widget = w
        # Optional ivars
        self.x = x
        self.y = y
        # Support for fastGotoNode plugin
        self.x_root = x_root
        self.y_root = y_root
    #@+node:ekr.20140907103315.18774: *3* LeoKeyEvent.__repr__
    def __repr__(self):

        d = {'c': self.c.shortFileName()}
        for ivar in ('char', 'event', 'stroke', 'w'):
            d[ivar] = getattr(self, ivar)
        return f"LeoKeyEvent:\n{g.objToString(d)}"
    #@+node:ekr.20150511181702.1: *3* LeoKeyEvent.get & __getitem__
    def get(self, attr):
        """Compatibility with g.bunch: return an attr."""
        return getattr(self, attr, None)

    def __getitem__(self, attr):
        """Compatibility with g.bunch: return an attr."""
        return getattr(self, attr, None)
    #@+node:ekr.20140907103315.18775: *3* LeoKeyEvent.type
    def type(self):
        return 'LeoKeyEvent'
    #@-others
#@+node:ekr.20031218072017.2223: ** class NullGui (LeoGui)
class NullGui(LeoGui):
    """Null gui class."""
    #@+others
    #@+node:ekr.20031218072017.2225: *3* NullGui.__init__
    def __init__(self, guiName='nullGui'):
        """ctor for the NullGui class."""
        super().__init__(guiName)
        self.clipboardContents = ''
        self.focusWidget = None
        self.script = None
        self.lastFrame = None
            # The outer frame, used only to set the g.app.log in runMainLoop.
        self.isNullGui = True
        self.idleTimeClass = g.NullObject
    #@+node:ekr.20031218072017.3744: *3* NullGui.dialogs
    def runAboutLeoDialog(self, c, version, theCopyright, url, email):
        return self.simulateDialog("aboutLeoDialog", None)

    def runAskLeoIDDialog(self):
        return self.simulateDialog("leoIDDialog", None)

    def runAskOkDialog(self, c, title, message=None, text="Ok"):
        return self.simulateDialog("okDialog", "Ok")

    def runAskOkCancelNumberDialog(self, c, title, message,
        cancelButtonText=None,
        okButtonText=None,
    ):
        return self.simulateDialog("numberDialog", -1)

    def runAskOkCancelStringDialog(self, c, title, message,
        cancelButtonText=None,
        okButtonText=None,
        default="",
        wide=False,
    ):
        return self.simulateDialog("stringDialog", '')

    def runCompareDialog(self, c):
        return self.simulateDialog("compareDialog", '')

    def runOpenFileDialog(self, c, title, filetypes, defaultextension,
        multiple=False,
        startpath=None,
    ):
        return self.simulateDialog("openFileDialog", None)

    def runSaveFileDialog(self, c, initialfile, title, filetypes, defaultextension):
        return self.simulateDialog("saveFileDialog", None)

    def runAskYesNoDialog(self, c, title,
        message=None,
        yes_all=False,
        no_all=False,
    ):
        return self.simulateDialog("yesNoDialog", "no")

    def runAskYesNoCancelDialog(self, c, title,
        message=None,
        yesMessage="Yes",
        noMessage="No",
        yesToAllMessage=None,
        defaultButton="Yes",
        cancelMessage=None,
    ):
        return self.simulateDialog("yesNoCancelDialog", "cancel")

    def simulateDialog(self, key, defaultVal):
        return defaultVal
    #@+node:ekr.20170613101737.1: *3* NullGui.clipboard & focus
    def get_focus(self, *args, **kwargs):
        return self.focusWidget

    def getTextFromClipboard(self):
        return self.clipboardContents

    def replaceClipboardWith(self, s):
        self.clipboardContents = s

    def set_focus(self, commander, widget):
        self.focusWidget = widget
    #@+node:ekr.20070301171901: *3* NullGui.do nothings
    def alert(self, c, message): pass

    def attachLeoIcon(self, window): pass

    def destroySelf(self): pass

    def finishCreate(self): pass

    def getFontFromParams(self, family, size, slant, weight, defaultSize=12):
        return g.app.config.defaultFont

    def getIconImage(self, name): return None

    def getImageImage(self, name): return None

    def getTreeImage(self, c, path): return None

    def get_window_info(self, window): return 600, 500, 20, 20

    def onActivateEvent(self, *args, **keys): pass

    def onDeactivateEvent(self, *args, **keys): pass

    def set_top_geometry(self, w, h, x, y): pass
    #@+node:ekr.20070228155807: *3* NullGui.isTextWidget & isTextWrapper
    def isTextWidget(self, w):
        return True  # Must be True for unit tests.

    def isTextWrapper(self, w):
        """Return True if w is a Text widget suitable for text-oriented commands."""
        return w and getattr(w, 'supportsHighLevelInterface', None)
    #@+node:ekr.20031218072017.2230: *3* NullGui.oops
    def oops(self):
        g.trace("NullGui", g.callers(4))
    #@+node:ekr.20070301172456: *3* NullGui.panels
    def createComparePanel(self, c):
        """Create Compare panel."""
        self.oops()

    def createFindTab(self, c, parentFrame):
        """Create a find tab in the indicated frame."""
        pass  # Now always done during startup.

    def createLeoFrame(self, c, title):
        """Create a null Leo Frame."""
        gui = self
        self.lastFrame = leoFrame.NullFrame(c, title, gui)
        return self.lastFrame
    #@+node:ekr.20031218072017.2229: *3* NullGui.runMainLoop
    def runMainLoop(self):
        """Run the null gui's main loop."""
        if self.script:
            frame = self.lastFrame
            g.app.log = frame.log
            self.lastFrame.c.executeScript(script=self.script)
        else:
            print('**** NullGui.runMainLoop: terminating Leo.')
        # Getting here will terminate Leo.
    #@-others
#@+node:ekr.20080707150137.5: ** class NullScriptingControllerClass
class NullScriptingControllerClass:
    """A default, do-nothing class to be overridden by mod_scripting or other plugins.

    This keeps pylint happy."""

    def __init__(self, c, iconBar=None):
        self.c = c
        self.iconBar = iconBar

    def createAllButtons(self):
        pass
#@+node:ekr.20171128093401.1: ** class StringCheckBox (object)
class StringCheckBox:
    """Simulate a QCheckBox."""

    def __init__(self, name, label):
        self.label = label
        self.name = name
        self.value = True

    def checkState(self):
        return self.value

    def objectName(self):
        return self.name

    def setCheckState(self, value):
        self.value = value

    def toggle(self):
        self.value = not self.value
#@+node:ekr.20170613095422.1: ** class StringGui (NullGui)
class StringGui(LeoGui):
    """
    A class representing all on-screen objects using subclasses of the
    leoFrame.StringTextWrapper class.
    """
    #@+others
    #@+node:ekr.20170613095422.7: *3* StringGui.oops
    def oops(self):

        g.trace("StringGui", g.callers(4))
    #@+node:ekr.20170613114120.1: *3* StringGui.runMainLoop
    def runMainLoop(self):
        self.oops()
    #@-others
#@+node:ekr.20171128093503.1: ** class StringLineEdit (object)
class StringLineEdit:

    """Simulate a QLineEdit."""

    def __init__(self, name, disabled):
        self.disabled = disabled
        self.name = name
        self.pos = 0
        self.s = ''

    def clear(self):
        self.pos = 0
        self.s = ''

    def insert(self, s):
        if s:
            i = self.pos
            self.s = self.s[:i] + s + self.s[i:]
            self.pos += len(s)

    def objectName(self):
        return self.name

    def text(self):
        return self.s
#@+node:ekr.20171128093602.1: ** class StringRadioButton (object)
class StringRadioButton:

    """Simulate QRadioButton."""

    def __init__(self, name, label):
        self.label = label
        self.name = name
        self.value = True

    def isChecked(self):
        return self.value

    def objectName(self):
        return self.name

    def toggle(self):
        self.value = not self.value
#@+node:ekr.20031218072017.3742: ** class UnitTestGui (NullGui)
class UnitTestGui(NullGui):
    """A gui class for use by unit tests."""
    # Presently used only by the import/export unit tests.
    #@+others
    #@+node:ekr.20031218072017.3743: *3* UnitTestGui.__init__
    def __init__(self, theDict=None):
        """ctor for the UnitTestGui class."""
        self.oldGui = g.app.gui
        super().__init__("UnitTestGui")
        self.theDict = {} if theDict is None else theDict
        g.app.gui = self

    def destroySelf(self):
        g.app.gui = self.oldGui
    #@+node:ekr.20071128094234.1: *3* UnitTestGui.createSpellTab
    def createSpellTab(self, c, spellHandler, tabName):
        pass  # This method keeps pylint happy.
    #@+node:ekr.20111001155050.15484: *3* UnitTestGui.runAtIdle
    if 1:  # Huh?

        def runAtIdle(self, aFunc):
            """Run aFunc immediately for a unit test.

            This is a kludge, but it is probably the best that can be done.
            """
            aFunc()
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo

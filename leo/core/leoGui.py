#@+leo-ver=5-thin
#@+node:ekr.20031218072017.3719: * @file leoGui.py
"""
A module containing the base gui-related classes.

These classes hide the details of which gui is actually being used.
Leo's core calls this class to allocate all gui objects.

Plugins may define their own gui classes by setting g.app.gui.
"""
#@+<< leoGui imports & annotations >>
#@+node:ekr.20220414080546.1: ** << leoGui imports & annotations >>
from __future__ import annotations
from collections.abc import Callable
from typing import Any, Optional, TYPE_CHECKING
from leo.core import leoGlobals as g
from leo.core import leoFrame

if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoNodes import Position
    from leo.plugins.qt_frame import FindTabManager
    from leo.plugins.qt_text import QTextEditWrapper as Wrapper
    Widget = Any
#@-<< leoGui imports & annotations >>
#@+others
#@+node:ekr.20031218072017.3720: ** class LeoGui
class LeoGui:
    """The base class of all gui classes.

    Subclasses are expected to override all do-nothing methods of this class.
    """
    #@+others
    #@+node:ekr.20031218072017.3722: *3* LeoGui.__init__
    def __init__(self, guiName: str) -> None:
        """Ctor for the LeoGui class."""
        self.active = False  # Used only by qt_gui.
        self.consoleOnly = True  # True if g.es goes to console.
        self.globalFindTabManager: FindTabManager = None
        self.globalFindTab: Widget = None
        self.idleTimeClass: Any = None  # Hard to annotate.
        self.isNullGui = False
        self.lastFrame: Widget = None
        self.leoIcon = None
        self.mGuiName = guiName
        self.mainLoop = None
        self.plainTextWidget: Widget = None  # For SpellTabHandler class only.
        self.root: Position = None
        self.script: Optional[str] = None
        self.splashScreen: Widget = None
        self.utils = None
        # To keep pylint happy.
        self.ScriptingControllerClass = NullScriptingControllerClass
        #
        # Define special keys that may be overridden is subclasses.
        self.ignoreChars: list[str] = []  # Keys that should always be ignored.
        self.FKeys: list[str] = []  # The representation of F-keys.
        self.specialChars: list[str] = []  # A list of characters/keys to be handle specially.
    #@+node:ekr.20061109212618.1: *3* LeoGui: Must be defined only in base class
    #@+node:ekr.20110605121601.18847: *4* LeoGui.create_key_event (LeoGui)
    def create_key_event(
        self,
        c: Cmdr,
        binding: str = None,
        char: str = None,
        event: LeoKeyEvent = None,
        w: Wrapper = None,
        x: int = None,
        x_root: int = None,
        y: int = None,
        y_root: int = None,
    ) -> LeoKeyEvent:
        # Do not call strokeFromSetting here!
        # For example, this would wrongly convert Ctrl-C to Ctrl-c,
        # in effect, converting a user binding from Ctrl-Shift-C to Ctrl-C.
        return LeoKeyEvent(c, char, event, binding, w, x, y, x_root, y_root)
    #@+node:ekr.20031218072017.3740: *4* LeoGui.guiName
    def guiName(self) -> str:
        try:
            return self.mGuiName
        except Exception:
            return "invalid gui name"
    #@+node:ekr.20031218072017.2231: *4* LeoGui.setScript
    def setScript(self, script: str = None, scriptFileName: str = None) -> None:
        self.script = script
        self.scriptFileName = scriptFileName
    #@+node:ekr.20110605121601.18845: *4* LeoGui.event_generate (LeoGui)
    def event_generate(self, c: Cmdr, char: str, shortcut: str, w: Wrapper) -> None:
        event = self.create_key_event(c, binding=shortcut, char=char, w=w)
        c.k.masterKeyHandler(event)
        c.outerUpdate()
    #@+node:ekr.20061109212618: *3* LeoGu: Must be defined in subclasses
    #@+node:ekr.20031218072017.3725: *4* LeoGui.destroySelf
    def destroySelf(self) -> None:
        raise NotImplementedError
    #@+node:ekr.20031218072017.3730: *4* LeoGui.dialogs
    def runAboutLeoDialog(self,
        c: Cmdr, version: str, theCopyright: str, url: str, email: str,
    ) -> Any:  # Must be any, for compatibility with testing subclass.
        """Create and run Leo's About Leo dialog."""
        raise NotImplementedError

    def runAskOkDialog(self, c: Cmdr, title: str, message: str = None, text: str = "Ok") -> Any:
        """Create and run an askOK dialog ."""
        raise NotImplementedError

    def runAskOkCancelNumberDialog(self,
        c: Cmdr,
        title: str,
        message: str,
        cancelButtonText: str = None,
        okButtonText: str = None,
    ) -> Any:
        """Create and run askOkCancelNumber dialog ."""
        raise NotImplementedError

    def runAskOkCancelStringDialog(
        self,
        c: Cmdr,
        title: str,
        message: str,
        cancelButtonText: str = None,
        okButtonText: str = None,
        default: str = "",
        wide: bool = False,
    ) -> Any:
        """Create and run askOkCancelString dialog ."""
        raise NotImplementedError

    def runAskYesNoDialog(self,
        c: Cmdr,
        title: str,
        message: str = None,
        yes_all: bool = False,
        no_all: bool = False,
    ) -> Any:
        """Create and run an askYesNo dialog."""
        raise NotImplementedError

    def runAskYesNoCancelDialog(
        self,
        c: Cmdr,
        title: str,
        message: str = None,
        yesMessage: str = "Yes",
        noMessage: str = "No",
        yesToAllMessage: str = None,
        defaultButton: str = "Yes",
        cancelMessage: str = None,
    ) -> Any:
        """Create and run an askYesNoCancel dialog ."""
        raise NotImplementedError

    def runPropertiesDialog(self,
        title: str = 'Properties',
        data: Any = None,
        callback: Callable = None,
        buttons: list[str] = None,
    ) -> Any:
        """Display a modal TkPropertiesDialog"""
        raise NotImplementedError
    #@+node:ekr.20031218072017.3731: *4* LeoGui.file dialogs
    def runOpenFileDialog(self,
        c: Cmdr,
        title: str,
        *,
        filetypes: list[tuple[str, str]],
        defaultextension: str = '',
        startpath: str = None,
    ) -> str:
        """Create and run an open file dialog ."""
        raise NotImplementedError

    def runOpenFilesDialog(self,
        c: Cmdr,
        title: str,
        *,
        filetypes: list[tuple[str, str]],
        defaultextension: str = '',
        startpath: str = None,
    ) -> list[str]:
        """Create and run an open files dialog ."""
        raise NotImplementedError

    def runSaveFileDialog(
        self,
        c: Cmdr,
        title: str,
        *,
        filetypes: list[tuple[str, str]],
        defaultextension: str,
    ) -> str:
        """Create and run a save file dialog ."""
        raise NotImplementedError
    #@+node:ekr.20031218072017.3732: *4* LeoGui.panels
    def createComparePanel(self, c: Cmdr) -> None:
        """Create Compare panel."""
        raise NotImplementedError

    def createFindTab(self, c: Cmdr, parentFrame: Widget) -> None:
        """Create a find tab in the indicated frame."""
        raise NotImplementedError

    def createFontPanel(self, c: Cmdr) -> None:
        """Create a hidden Font panel."""
        raise NotImplementedError

    def createLeoFrame(self, c: Cmdr, title: str) -> Widget:
        """Create a new Leo frame."""
        raise NotImplementedError
    #@+node:ekr.20031218072017.3729: *4* LeoGui.runMainLoop
    def runMainLoop(self) -> None:
        """Run the gui's main loop."""
        raise NotImplementedError
    #@+node:ekr.20031218072017.3733: *4* LeoGui.utils
    #@+at Subclasses are expected to subclass all of the following methods.
    # These are all do-nothing methods: callers are expected to check for
    # None returns.
    # The type of commander passed to methods depends on the type of frame
    # or dialog being created. The commander may be a Commands instance or
    # one of its subcommanders.
    #@+node:ekr.20031218072017.3734: *5* LeoGui.Clipboard
    def replaceClipboardWith(self, s: str) -> None:
        raise NotImplementedError

    def getTextFromClipboard(self) -> str:
        raise NotImplementedError
    #@+node:ekr.20031218072017.3735: *5* LeoGui.Dialog utils
    def attachLeoIcon(self, window: Any) -> None:
        """Attach the Leo icon to a window."""
        raise NotImplementedError

    def center_dialog(self, dialog: str) -> None:
        """Center a dialog."""
        raise NotImplementedError

    def create_labeled_frame(self,
        parent: str,
        caption: str = None,
        relief: str = "groove",
        bd: int = 2,
        padx: int = 0,
        pady: int = 0,
    ) -> None:
        """Create a labeled frame."""
        raise NotImplementedError

    def get_window_info(self, window: str) -> tuple[int, int, int, int]:
        """Return the window information."""
        raise NotImplementedError
    #@+node:ekr.20031218072017.3736: *5* LeoGui.Font
    def getFontFromParams(self,
        family: str, size: str, slant: str, weight: str, defaultSize: int = 12, tag: str = '',
    ) -> Any:
        raise NotImplementedError
    #@+node:ekr.20070212145124: *5* LeoGui.getFullVersion
    def getFullVersion(self, c: Cmdr = None) -> str:
        return 'LeoGui: dummy version'
    #@+node:ekr.20070212070820: *5* LeoGui.makeScriptButton
    def makeScriptButton(
        self,
        c: Cmdr,
        args: str = None,
        p: Position = None,
        script: str = None,
        buttonText: str = None,
        balloonText: str = 'Script Button',
        shortcut: str = None,
        bg: str = 'LightSteelBlue1',
        define_g: bool = True,
        define_name: str = '__main__',
        silent: bool = False,
    ) -> None:
        raise NotImplementedError
    #@+node:ekr.20070228154059: *3* LeoGui: May be defined in subclasses
    #@+node:ekr.20110613103140.16423: *4* LeoGui.dismiss_spash_screen
    def dismiss_splash_screen(self) -> None:
        pass  # May be overridden in subclasses.
    #@+node:tbrown.20110618095626.22068: *4* LeoGui.ensure_commander_visible
    def ensure_commander_visible(self, c: Cmdr) -> None:
        """E.g. if commanders are in tabs, make sure c's tab is visible"""
        pass
    #@+node:ekr.20070219084912: *4* LeoGui.finishCreate
    def finishCreate(self) -> None:
        # This may be overridden in subclasses.
        pass
    #@+node:ekr.20101028131948.5861: *4* LeoGui.killPopupMenu & postPopupMenu
    # These definitions keep pylint happy.

    def postPopupMenu(self, *args: str, **keys: str) -> None:
        pass
    #@+node:ekr.20170612065049.1: *4* LeoGui.put_help
    def put_help(self, c: Cmdr, s: str, short_title: str) -> None:
        pass
    #@+node:ekr.20051206103652: *4* LeoGui.widget_name (LeoGui)
    def widget_name(self, w: Widget) -> str:
        # First try the widget's getName method.
        if not w:
            return '<no widget>'
        if hasattr(w, 'getName'):
            return w.getName()
        if hasattr(w, '_name'):
            return w._name
        return repr(w)
    #@-others
#@+node:ekr.20070228160107: ** class LeoKeyEvent
class LeoKeyEvent:
    """A gui-independent wrapper for gui events."""
    #@+others
    #@+node:ekr.20110605121601.18846: *3* LeoKeyEvent.__init__
    def __init__(
        self,
        c: Cmdr,
        char: str,
        event: LeoKeyEvent,
        binding: Any,
        w: Any,
        x: int = None,
        y: int = None,
        x_root: int = None,
        y_root: int = None,
    ) -> None:
        """Ctor for LeoKeyEvent class."""
        stroke: Any
        if g.isStroke(binding):
            g.trace('***** (LeoKeyEvent) oops: already a stroke', binding, g.callers())
            stroke = binding
        else:
            stroke = g.KeyStroke(binding) if binding else None
        assert g.isStrokeOrNone(stroke), f"(LeoKeyEvent) {stroke!r} {g.callers()}"
        if 0:  # Doesn't add much.
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
    def __repr__(self) -> str:

        d = {'c': self.c.shortFileName()}
        for ivar in ('char', 'event', 'stroke', 'w'):
            d[ivar] = getattr(self, ivar)
        return f"LeoKeyEvent:\n{g.objToString(d)}"
    #@+node:ekr.20150511181702.1: *3* LeoKeyEvent.get & __getitem__
    def get(self, attr: str) -> Any:
        """Compatibility with g.bunch: return an attr."""
        return getattr(self, attr, None)

    def __getitem__(self, attr: str) -> Any:
        """Compatibility with g.bunch: return an attr."""
        return getattr(self, attr, None)
    #@+node:ekr.20140907103315.18775: *3* LeoKeyEvent.type
    def type(self) -> str:
        return 'LeoKeyEvent'
    #@-others
#@+node:ekr.20031218072017.2223: ** class NullGui (LeoGui)
class NullGui(LeoGui):
    """Null gui class."""
    #@+others
    #@+node:ekr.20031218072017.2225: *3* NullGui.__init__
    def __init__(self, guiName: str = 'nullGui') -> None:
        """ctor for the NullGui class."""
        super().__init__(guiName)
        self.clipboardContents = ''
        self.focusWidget: Widget = None
        self.isNullGui = True
        self.idleTimeClass: Any = g.NullObject
        self.lastFrame: Widget = None  # The outer frame, to set g.app.log in runMainLoop.
        self.plainTextWidget: Widget = g.NullObject
        self.script = None
    #@+node:ekr.20031218072017.3744: *3* NullGui.dialogs
    def runAboutLeoDialog(self, c: Cmdr, version: str, theCopyright: str, url: str, email: str) -> str:
        return None

    def runAskOkDialog(self, c: Cmdr, title: str, message: str = None, text: str = "Ok") -> str:
        return 'Ok'

    def runAskOkCancelNumberDialog(
        self,
        c: Cmdr,
        title: str,
        message: str,
        cancelButtonText: str = None,
        okButtonText: str = None,
    ) -> str:
        return 'no'

    def runAskOkCancelStringDialog(
        self,
        c: Cmdr,
        title: str,
        message: str,
        cancelButtonText: str = None,
        okButtonText: str = None,
        default: str = "",
        wide: bool = False,
    ) -> str:
        return ''

    def runCompareDialog(self, c: Cmdr) -> str:
        return ''

    def runOpenFileDialog(self, c: Cmdr, title: str, *,
        filetypes: list[tuple[str, str]] = None,
        defaultextension: str = '',
        startpath: str = None,
    ) -> str:
        return ''

    def runSaveFileDialog(self,
        c: Cmdr,
        title: str,
        *,
        filetypes: list[tuple[str, str]] = None,
        defaultextension: str = '',
    ) -> str:
        return ''

    def runOpenFilesDialog(
        self,
        c: Cmdr,
        title: str,
        *,
        filetypes: list[tuple[str, str]] = None,
        defaultextension: str = '',
        startpath: str = None,
    ) -> list[str]:
        return []


    def runAskYesNoDialog(
        self,
        c: Cmdr,
        title: str,
        message: str = None,
        yes_all: bool = False,
        no_all: bool = False,
    ) -> str:
        return 'no'

    def runAskYesNoCancelDialog(
        self,
        c: Cmdr,
        title: str,
        message: str = None,
        yesMessage: str = "Yes",
        noMessage: str = "No",
        yesToAllMessage: str = None,
        defaultButton: str = "Yes",
        cancelMessage: str = None,
    ) -> str:
        return 'cancel'
    #@+node:ekr.20170613101737.1: *3* NullGui.clipboard & focus
    def get_focus(self, *args: str, **kwargs: str) -> Widget:
        return self.focusWidget

    def getTextFromClipboard(self) -> str:
        return self.clipboardContents

    def replaceClipboardWith(self, s: str) -> None:
        self.clipboardContents = s

    def set_focus(self, commander: str, widget: str) -> None:
        self.focusWidget = widget
    #@+node:ekr.20230916153234.1: *3* NullGui.createSpellTab
    def createSpellTab(self, c: Cmdr, spellHandler: Any, tabName: str) -> Any:

        class NullSpellTab:

            def __init__(self, c: Cmdr, spellHandler: Any, tabName: str) -> None:
                self.c = c
                self.spellHandler = spellHandler
                self.tabName = tabName

            def fillbox(self, alts: list[str], word: str) -> None:
                pass

        return NullSpellTab(c, spellHandler, tabName)
    #@+node:ekr.20070301171901: *3* NullGui.do nothings
    def alert(self, c: Cmdr, message: str) -> None:
        pass

    def attachLeoIcon(self, window: Any) -> None:
        pass

    def destroySelf(self) -> None:
        pass

    def finishCreate(self) -> None:
        pass

    def getFontFromParams(self,
        family: str, size: str, slant: str, weight: str, defaultSize: int = 12, tag: str = '',
    ) -> Any:
        return None

    def getIconImage(self, name: str) -> None:
        return None

    def getImageImage(self, name: str) -> None:
        return None

    def getTreeImage(self, c: Cmdr, path: str) -> None:
        return None

    def get_window_info(self, window: str) -> tuple[int, int, int, int]:
        return 600, 500, 20, 20

    def onActivateEvent(self, *args: str, **keys: str) -> None:
        pass

    def onDeactivateEvent(self, *args: str, **keys: str) -> None:
        pass
    #@+node:ekr.20070228155807: *3* NullGui.isTextWidget & isTextWrapper
    def isTextWidget(self, w: Any) -> bool:
        return True  # Must be True for unit tests.

    def isTextWrapper(self, w: Any) -> bool:
        """Return True if w is a Text widget suitable for text-oriented commands."""
        return w and getattr(w, 'supportsHighLevelInterface', None)
    #@+node:ekr.20070301172456: *3* NullGui.panels
    def createComparePanel(self, c: Cmdr) -> None:
        """Create Compare panel."""

    def createFindTab(self, c: Cmdr, parentFrame: Widget) -> None:
        """Create a find tab in the indicated frame."""

    def createLeoFrame(self, c: Cmdr, title: str) -> Widget:
        """Create a null Leo Frame."""
        gui = self
        self.lastFrame = leoFrame.NullFrame(c, title, gui)
        return self.lastFrame
    #@+node:ekr.20031218072017.2229: *3* NullGui.runMainLoop
    def runMainLoop(self) -> None:
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

    def __init__(self, c: Cmdr, iconBar: Widget = None) -> None:
        self.c = c
        self.iconBar = iconBar

    def createAllButtons(self) -> None:
        pass
#@+node:ekr.20171128093401.1: ** class StringCheckBox (leoGui.py)
class StringCheckBox:
    """Simulate a QCheckBox."""

    def __init__(self, name: str, label: str = None) -> None:
        self.label = label
        self.name = name
        self.value = True

    def checkState(self) -> bool:
        return self.value

    isChecked = checkState

    def objectName(self) -> str:
        return self.name

    def setCheckState(self, value: bool) -> None:
        self.value = value

    def toggle(self) -> None:
        self.value = not self.value
#@+node:ekr.20210221130549.1: ** class StringFindTabManager (leoGui.py)
class StringFindTabManager:
    """A string-based FindTabManager class for unit tests."""
    #@+others
    #@+node:ekr.20210221130549.2: *3*  sftm.ctor
    #@@nobeautify

    def __init__(self, c: Cmdr) -> None:
        """Ctor for the FindTabManager class."""
        self.c = c
        self.entry_focus = None  # Accessed directly from code(!)
        # Find/change text boxes...
        self.find_findbox = StringLineEdit('find_text')
        self.find_replacebox = StringLineEdit('change_text')
        # Check boxes...
        self.check_box_ignore_case      = StringCheckBox('ignore_case')
        self.check_box_mark_changes     = StringCheckBox('mark_changes')
        self.check_box_mark_finds       = StringCheckBox('mark_finds')
        self.check_box_regexp           = StringCheckBox('pattern_match')
        self.check_box_search_body      = StringCheckBox('search_body')
        self.check_box_search_headline  = StringCheckBox('search_headline')
        self.check_box_whole_word       = StringCheckBox('whole_word')
        # Radio buttons...
        self.radio_button_entire_outline  = StringRadioButton('entire_outline')
        self.radio_button_file_only       = StringRadioButton('file_only')
        self.radio_button_node_only       = StringRadioButton('node_only')
        self.radio_button_suboutline_only = StringRadioButton('suboutline_only')
        # Init the default values.
        self.init_widgets()
    #@+node:ekr.20210221130549.5: *3* sftm.clear_focus & init_focus & set_entry_focus
    def clear_focus(self) -> None:
        pass

    def init_focus(self) -> None:
        pass

    def set_entry_focus(self) -> None:
        pass
    #@+node:ekr.20210221130549.4: *3* sftm.get_settings
    #@@nobeautify

    def get_settings(self) -> Any:
        """
        Return a g.bunch representing all widget values.

        Similar to LeoFind.default_settings, but only for find-tab values.
        """
        return g.Bunch(
            # Find/change strings...
            find_text   = self.find_findbox.text(),
            change_text = self.find_replacebox.text(),
            # Find options...
            file_only       = self.radio_button_file_only.isChecked(),
            ignore_case     = self.check_box_ignore_case.isChecked(),
            mark_changes    = self.check_box_mark_changes.isChecked(),
            mark_finds      = self.check_box_mark_finds.isChecked(),
            node_only       = self.radio_button_node_only.isChecked(),
            pattern_match   = self.check_box_regexp.isChecked(),
            search_body     = self.check_box_search_body.isChecked(),
            search_headline = self.check_box_search_headline.isChecked(),
            suboutline_only = self.radio_button_suboutline_only.isChecked(),
            whole_word      = self.check_box_whole_word.isChecked(),
        )
    #@+node:ekr.20210221130549.7: *3* sftm.init_widgets
    def init_widgets(self) -> None:
        """
        Init widgets and ivars from c.config settings.
        Create callbacks that always keep the LeoFind ivars up to date.
        """
        c, find = self.c, self.c.findCommands
        # Find/change text boxes.
        table1 = (
            ('find_findbox', 'find_text', '<find pattern here>'),
            ('find_replacebox', 'change_text', ''),
        )
        for widget_ivar, setting_name, default in table1:
            w = getattr(self, widget_ivar)
            s = c.config.getString(setting_name) or default
            w.insert(s)
        # Check boxes.
        table2 = (
            ('ignore_case', 'check_box_ignore_case'),
            ('mark_changes', 'check_box_mark_changes'),
            ('mark_finds', 'check_box_mark_finds'),
            ('pattern_match', 'check_box_regexp'),
            ('search_body', 'check_box_search_body'),
            ('search_headline', 'check_box_search_headline'),
            ('whole_word', 'check_box_whole_word'),
        )
        for setting_name, widget_ivar in table2:
            w = getattr(self, widget_ivar)
            val = c.config.getBool(setting_name, default=False)
            setattr(find, setting_name, val)
            if val != w.isChecked():  # Support leoInteg.
                w.toggle()
        # Radio buttons
        table3 = (
            ('file_only', 'file_only', 'radio_button_file_only'),  # #2684.
            ('node_only', 'node_only', 'radio_button_node_only'),
            ('entire_outline', None, 'radio_button_entire_outline'),
            ('suboutline_only', 'suboutline_only', 'radio_button_suboutline_only'),
        )
        for setting_name, ivar, widget_ivar in table3:
            w = getattr(self, widget_ivar)
            val = c.config.getBool(setting_name, default=False)
            if ivar is not None:
                assert hasattr(find, setting_name), setting_name
                setattr(find, setting_name, val)
                if val != w.isChecked():
                    w.toggle()
        # Ensure one radio button is set.
        if not find.node_only and not find.suboutline_only and not find.file_only:
            w = self.radio_button_entire_outline
            if not w.isChecked():
                w.toggle()
    #@+node:ekr.20210312122351.1: *3* sftm.set_body_and_headline_checkbox
    def set_body_and_headline_checkbox(self) -> None:
        """Return the search-body and search-headline checkboxes to their defaults."""
        # #1840: headline-only one-shot
        c = self.c
        find = c.findCommands
        if not find:
            return
        table = (
            ('search_body', self.check_box_search_body),
            ('search_headline', self.check_box_search_headline),
        )
        for setting_name, w in table:
            val = c.config.getBool(setting_name, default=False)
            if val != w.isChecked():
                w.toggle()
    #@+node:ekr.20210221130549.8: *3* sftm.set_radio_button
    #@@nobeautify

    def set_radio_button(self, name: str) -> None:
        """Set the value of the radio buttons"""
        d = {
            'file-only':       self.radio_button_file_only,
            'node-only':       self.radio_button_node_only,
            'entire-outline':  self.radio_button_entire_outline,
            'suboutline-only': self.radio_button_suboutline_only,
        }
        w = d.get(name)
        if not w.isChecked():
            w.toggle()
    #@+node:ekr.20210221130549.3: *3* sftm.text getters/setters
    def get_find_text(self) -> str:
        s = self.find_findbox.text()
        if s and s[-1] in ('\r', '\n'):
            s = s[:-1]
        return s

    def get_change_text(self) -> str:
        s = self.find_replacebox.text()
        if s and s[-1] in ('\r', '\n'):
            s = s[:-1]
        return s

    def set_find_text(self, s: str) -> None:
        w = self.find_findbox
        w.clear()
        w.insert(s)

    def set_change_text(self, s: str) -> None:
        w = self.find_replacebox
        w.clear()
        w.insert(s)
    #@+node:ekr.20210221130549.9: *3* sftm.toggle_checkbox
    #@@nobeautify

    def toggle_checkbox(self, checkbox_name: str) -> None:
        """Toggle the value of the checkbox whose name is given."""
        d = {
            'ignore_case':     self.check_box_ignore_case,
            'mark_changes':    self.check_box_mark_changes,
            'mark_finds':      self.check_box_mark_finds,
            'pattern_match':   self.check_box_regexp,
            'search_body':     self.check_box_search_body,
            'search_headline': self.check_box_search_headline,
            'whole_word':      self.check_box_whole_word,
        }
        w = d.get(checkbox_name)
        w.toggle()
    #@-others
#@+node:ekr.20170613095422.1: ** class StringGui (LeoGui)
class StringGui(LeoGui):
    """
    A class representing all on-screen objects using subclasses of the
    leoFrame.StringTextWrapper class.
    """
    #@+others
    #@+node:ekr.20170613114120.1: *3* StringGui.runMainLoop
    def runMainLoop(self) -> None:
        raise NotImplementedError
    #@-others
#@+node:ekr.20171128093503.1: ** class StringLineEdit (leoGui)
class StringLineEdit:
    """Simulate a QLineEdit."""

    def __init__(self, name: str, disabled: bool = False) -> None:
        self.disabled = disabled
        self.name = name
        self.pos = 0
        self.s = ''

    def clear(self) -> None:
        self.pos = 0
        self.s = ''

    def insert(self, s: str) -> None:
        if s:
            i = self.pos
            self.s = self.s[:i] + s + self.s[i:]
            self.pos += len(s)

    def objectName(self) -> str:
        return self.name

    def text(self) -> str:
        return self.s
#@+node:ekr.20171128093602.1: ** class StringRadioButton (leoGui.py)
class StringRadioButton:
    """Simulate a QRadioButton."""

    def __init__(self, name: str, label: str = None) -> None:
        self.label = label
        self.name = name
        self.value = True

    def isChecked(self) -> bool:
        return self.value

    def objectName(self) -> str:
        return self.name

    def toggle(self) -> None:
        self.value = not self.value
#@+node:ekr.20031218072017.3742: ** class UnitTestGui (NullGui)
class UnitTestGui(NullGui):
    """A gui class for use by unit tests."""
    # Presently used only by the import/export unit tests.
    #@+others
    #@+node:ekr.20031218072017.3743: *3* UnitTestGui.__init__
    def __init__(self, theDict: dict = None) -> None:
        """ctor for the UnitTestGui class."""
        self.oldGui = g.app.gui
        super().__init__("UnitTestGui")
        self.theDict = {} if theDict is None else theDict
        g.app.gui = self

    def destroySelf(self) -> None:
        g.app.gui = self.oldGui
    #@+node:ekr.20071128094234.1: *3* UnitTestGui.createSpellTab
    def createSpellTab(self, c: Cmdr, spellHandler: Any, tabName: str) -> None:
        pass  # This method keeps pylint happy.

    #@+node:ekr.20111001155050.15484: *3* UnitTestGui.runAtIdle
    if 1:  # Huh?

        def runAtIdle(self, aFunc: Callable) -> None:
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

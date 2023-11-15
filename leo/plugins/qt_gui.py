#@+leo-ver=5-thin
#@+node:ekr.20140907085654.18699: * @file ../plugins/qt_gui.py
"""This file contains the gui wrapper for Qt: g.app.gui."""
# pylint: disable=import-error
#@+<< qt_gui imports  >>
#@+node:ekr.20140918102920.17891: ** << qt_gui imports >>
from __future__ import annotations
from collections.abc import Callable
import datetime
import functools
import re
import sys
import textwrap
from time import sleep
from typing import Any, Optional, Union, TYPE_CHECKING
from leo.core import leoColor
from leo.core import leoGlobals as g
from leo.core import leoGui
from leo.core.leoQt import isQt5, isQt6, Qsci, QtConst, QtCore
from leo.core.leoQt import QtGui, QtWidgets, QtSvg
from leo.core.leoQt import ButtonRole, DialogCode, Icon, Information, Policy
# This import causes pylint to fail on this file and on leoBridge.py.
# The failure is in astroid: raw_building.py.
from leo.core.leoQt import Shadow, Shape, StandardButton, Weight, WindowType
from leo.plugins import qt_events
from leo.plugins import qt_frame
from leo.plugins import qt_idle_time
from leo.plugins import qt_text
# This defines the commands defined by @g.command.
from leo.plugins import qt_commands
from leo.core.leoTips import UserTip
assert qt_commands
#@-<< qt_gui imports  >>
#@+<< qt_gui annotations >>
#@+node:ekr.20220415183421.1: ** << qt_gui annotations >>
if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoGui import LeoKeyEvent as Event
    from leo.core.leoNodes import Position
    from leo.plugins.qt_text import QTextEditWrapper as Wrapper
    Widget = Any
#@-<< qt_gui annotations >>
#@+others
#@+node:ekr.20110605121601.18134: ** init (qt_gui.py)
def init() -> bool:

    if g.unitTesting:  # Not Ok for unit testing!
        return False
    if not QtCore:
        return False
    if g.app.gui:
        return g.app.gui.guiName() == 'qt'
    g.app.gui = LeoQtGui()
    g.app.gui.finishCreate()
    g.plugin_signon(__name__)
    return True
#@+node:ekr.20140907085654.18700: ** class LeoQtGui(leoGui.LeoGui)
class LeoQtGui(leoGui.LeoGui):
    """A class implementing Leo's Qt gui."""
    #@+others
    #@+node:ekr.20110605121601.18477: *3*  qt_gui.__init__ (sets qtApp)
    def __init__(self) -> None:
        """Ctor for LeoQtGui class."""
        super().__init__('qt')  # Initialize the base class.
        self.active = True
        self.consoleOnly = False  # Console is separate from the log.
        self.iconimages: dict[str, Any] = {}  # Keys are paths, values are Icons.
        self.globalFindDialog: Widget = None
        self.idleTimeClass = qt_idle_time.IdleTime
        self.insert_char_flag = False  # A flag for eventFilter.
        self.mGuiName = 'qt'
        self.plainTextWidget = qt_text.PlainTextWrapper
        self.show_tips_flag = False  # #2390: Can't be inited in reload_settings.
        self.styleSheetManagerClass = StyleSheetManager
        # Be aware of the systems native colors, fonts, etc.
        QtWidgets.QApplication.setDesktopSettingsAware(True)
        # Create objects...
        self.qtApp = QtWidgets.QApplication(sys.argv)
        self.reloadSettings()
        self.appIcon = self.getIconImage('leoapp32.png')

        # Define various classes key stokes.
        #@+<< define FKeys >>
        #@+node:ekr.20180419110303.1: *4* << define FKeys >>
        self.FKeys = [
            'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12']
            # These do not generate keystrokes on MacOs.
        #@-<< define FKeys >>
        #@+<< define ignoreChars >>
        #@+node:ekr.20180419105250.1: *4* << define ignoreChars >>
        # Always ignore these characters
        self.ignoreChars = [
            # These are in ks.special characters.
            # They should *not* be ignored.
                # 'Left', 'Right', 'Up', 'Down',
                # 'Next', 'Prior',
                # 'Home', 'End',
                # 'Delete', 'Escape',
                # 'BackSpace', 'Linefeed', 'Return', 'Tab',
            # F-Keys are also ok.
                # 'F1','F2','F3','F4','F5','F6','F7','F8','F9','F10','F11','F12',
            'KP_0', 'KP_1', 'KP_2', 'KP_3', 'KP_4', 'KP_5', 'KP_6', 'KP_7', 'KP_8', 'KP_9',
            'KP_Multiply, KP_Separator,KP_Space, KP_Subtract, KP_Tab',
            'KP_F1', 'KP_F2', 'KP_F3', 'KP_F4',
            # Keypad chars should be have been converted to other keys.
            # Users should just bind to the corresponding normal keys.
            'KP_Add', 'KP_Decimal', 'KP_Divide', 'KP_Enter', 'KP_Equal',
            'CapsLock', 'Caps_Lock',
            'NumLock', 'Num_Lock',
            'ScrollLock',
            'Alt_L', 'Alt_R',
            'Control_L', 'Control_R',
            'Meta_L', 'Meta_R',
            'Shift_L', 'Shift_R',
            'Win_L', 'Win_R',  # Clearly, these should never be generated.
            # These are real keys, but they don't mean anything.
            'Break', 'Pause', 'Sys_Req',
            'Begin', 'Clear',  # Don't know what these are.
        ]
        #@-<< define ignoreChars >>
        #@+<< define specialChars >>
        #@+node:ekr.20180419081404.1: *4* << define specialChars >>
        # Keys whose names must never be inserted into text.
        self.specialChars = [
            # These are *not* special keys.
                # 'BackSpace', 'Linefeed', 'Return', 'Tab',
            'Left', 'Right', 'Up', 'Down',  # Arrow keys
            'Next', 'Prior',  # Page up/down keys.
            'Home', 'End',  # Home end keys.
            'Delete', 'Escape',  # Others.
            'Enter', 'Insert', 'Ins',  # These should only work if bound.
            'Menu',  # #901.
            'PgUp', 'PgDn',  # #868.
        ]
        #@-<< define specialChars >>
        # Put up the splash screen()
        if (g.app.use_splash_screen and
            not g.app.batchMode and
            not g.app.silentMode and
            not g.unitTesting
        ):
            self.splashScreen = self.createSplashScreen()
        # qtFrame.finishCreate does all the other work.
        self.frameFactory = qt_frame.TabbedFrameFactory()

    def reloadSettings(self) -> None:
        pass  # Note: self.c does not exist.
    #@+node:ekr.20110605121601.18484: *3*  qt_gui.destroySelf (calls qtApp.quit)
    def destroySelf(self) -> None:

        QtCore.pyqtRemoveInputHook()
        if 'shutdown' in g.app.debug:
            g.pr('LeoQtGui.destroySelf: calling qtApp.Quit')
        self.qtApp.quit()
    #@+node:ekr.20110605121601.18485: *3* qt_gui.Clipboard
    #@+node:ekr.20160917125946.1: *4* qt_gui.replaceClipboardWith
    def replaceClipboardWith(self, s: str) -> None:
        """Replace the clipboard with the string s."""
        cb = self.qtApp.clipboard()
        if cb:
            # cb.clear()  # unnecessary, breaks on some Qt versions
            s = g.toUnicode(s)
            QtWidgets.QApplication.processEvents()
            # Fix #241: QMimeData object error
            cb.setText(s)
            QtWidgets.QApplication.processEvents()
        else:
            g.trace('no clipboard!')
    #@+node:ekr.20160917125948.1: *4* qt_gui.getTextFromClipboard
    def getTextFromClipboard(self) -> str:
        """Get a unicode string from the clipboard."""
        cb = self.qtApp.clipboard()
        if cb:
            QtWidgets.QApplication.processEvents()
            return cb.text()
        g.trace('no clipboard!')
        return ''
    #@+node:ekr.20160917130023.1: *4* qt_gui.setClipboardSelection
    def setClipboardSelection(self, s: str) -> None:
        """
        Set the clipboard selection to s.
        There are problems with PyQt5.
        """
        # Alas, returning s reopens #218.
        return

    #@+node:ekr.20110605121601.18487: *3* qt_gui.Dialogs & panels
    #@+node:ekr.20231010004932.1: *4* qt_gui._save/_restore_focus
    def _save_focus(self, c):
        """
        Save the data needed to restore focus to the body.

        We have to guess: the user may have executed the save commands from the
        minibuffer. There is no way to know what the "original" focus was!
        """
        c.p.saveCursorAndScroll()

    def _restore_focus(self, c):
        """Restore focus to the body pane."""
        # Fix #3601 by brute force.
        c.bringToFront()
        c.bodyWantsFocusNow()
        c.p.restoreCursorAndScroll()
    #@+node:ekr.20110605121601.18488: *4* qt_gui.alert
    def alert(self, c: Cmdr, message: str) -> None:
        if g.unitTesting:
            return
        dialog = QtWidgets.QMessageBox(None)
        dialog.setWindowTitle('Alert')
        dialog.setText(message)
        dialog.setIcon(Icon.Warning)
        dialog.addButton('Ok', ButtonRole.YesRole)
        try:
            c.in_qt_dialog = True
            dialog.raise_()
            dialog.exec_()
        finally:
            c.in_qt_dialog = False
    #@+node:ekr.20110605121601.18489: *4* qt_gui.makeFilter
    def makeFilter(self, filetypes: list[str]) -> str:
        """Return the Qt-style dialog filter from filetypes list."""
        # Careful: the second %s is *not* replaced.
        filters = ['%s (%s)' % (z) for z in filetypes]
        return ';;'.join(filters)
    #@+node:ekr.20150615211522.1: *4* qt_gui.openFindDialog & helper
    def openFindDialog(self, c: Cmdr) -> None:
        if g.unitTesting:
            return
        dialog = self.globalFindDialog
        if not dialog:
            dialog = self.createFindDialog(c)
            self.globalFindDialog = dialog
            # Fix #516: Do the following only once...
            if c:
                # dialog.setStyleSheet(c.active_stylesheet)
                # Set the commander's FindTabManager.
                assert g.app.globalFindTabManager
                c.ftm = g.app.globalFindTabManager
                fn = c.shortFileName() or 'Untitled'
            else:
                fn = 'Untitled'
            dialog.setWindowTitle(f"Find in {fn}")
        if c:
            c.inCommand = False
        if dialog.isVisible():
            # The order is important, and tricky.
            dialog.focusWidget()
            dialog.show()
            dialog.raise_()
            dialog.activateWindow()
        else:
            dialog.show()
            dialog.exec_()
    #@+node:ekr.20150619053138.1: *5* qt_gui.createFindDialog
    def createFindDialog(self, c: Cmdr) -> Widget:
        """Create and init a non-modal Find dialog."""
        if c:
            g.app.globalFindTabManager = c.findCommands.ftm
        top = c and c.frame.top  # top is the DynamicWindow class.
        w = top.findTab  # type:ignore
        dialog = QtWidgets.QDialog()
        # Fix #516: Hide the dialog. Never delete it.

        def closeEvent(event: Event) -> None:
            event.ignore()
            dialog.hide()

        dialog.closeEvent = closeEvent
        layout = QtWidgets.QVBoxLayout(dialog)
        layout.addWidget(w)
        self.attachLeoIcon(dialog)
        dialog.setLayout(layout)
        if c:
            # c.styleSheetManager.set_style_sheets(w=dialog)
            g.app.gui.setFilter(c, dialog, dialog, 'find-dialog')
            # This makes most standard bindings available.
        dialog.setModal(False)
        return dialog
    #@+node:ekr.20110605121601.18492: *4* qt_gui.panels
    def createComparePanel(self, c: Cmdr) -> None:
        """Create a qt color picker panel."""
        pass  # This window is optional.

    def createFindTab(self, c: Cmdr, parentFrame: Widget) -> None:
        """Create a qt find tab in the indicated frame."""
        pass  # Now done in dw.createFindTab.

    def createLeoFrame(self, c: Cmdr, title: str) -> Widget:
        """Create a new Leo frame."""
        return qt_frame.LeoQtFrame(c, title, gui=self)

    def createSpellTab(self, c: Cmdr, spellHandler: Any, tabName: str) -> Widget:
        if g.unitTesting:
            return None
        return qt_frame.LeoQtSpellTab(c, spellHandler, tabName)
    #@+node:ekr.20110605121601.18493: *4* qt_gui.runAboutLeoDialog (changed)
    def runAboutLeoDialog(self,
        c: Cmdr, version: str, theCopyright: str, url: str, email: str,
    ) -> None:
        """Create and run a qt About Leo dialog."""
        if g.unitTesting:
            return

        # Create the dialog.
        dialog = QtWidgets.QMessageBox(c and c.frame.top)
        ssm = g.app.gui.styleSheetManagerClass(c)
        w = ssm.get_master_widget()
        sheet = w.styleSheet()
        if sheet:
            dialog.setStyleSheet(sheet)
        dialog.setText(f"{version}\n{theCopyright}\n{url}\n{email}")
        dialog.setIcon(Icon.Information)
        yes = dialog.addButton('Ok', ButtonRole.YesRole)
        dialog.setDefaultButton(yes)

        # Run the dialog, saving and restoring focus.
        try:
            self._save_focus(c)
            c.in_qt_dialog = True
            dialog.raise_()
            dialog.exec_()
        finally:
            c.in_qt_dialog = False
            self._restore_focus(c)
    #@+node:ekr.20110605121601.18496: *4* qt_gui.runAskDateTimeDialog
    def runAskDateTimeDialog(
        self,
        c: Cmdr,
        title: str,
        message: str = 'Select Date/Time',
        init: datetime.datetime = None,
        step_min: dict = None,
    ) -> None:
        """Create and run a qt date/time selection dialog.

        init - a datetime, default now
        step_min - a dict, keys are QtWidgets.QDateTimeEdit Sections, like
          QtWidgets.QDateTimeEdit.MinuteSection, and values are integers,
          the minimum amount that section of the date/time changes
          when you roll the mouse wheel.

        E.g. (5 minute increments in minute field):

            g.app.gui.runAskDateTimeDialog(c, 'When?',
                message="When is it?",
                step_min={QtWidgets.QDateTimeEdit.MinuteSection: 5})

        """
        #@+<< define date/time classes >>
        #@+node:ekr.20211005103909.1: *5* << define date/time classes >>


        class DateTimeEditStepped(QtWidgets.QDateTimeEdit):  # type:ignore
            """QDateTimeEdit which allows you to set minimum steps on fields, e.g.
              DateTimeEditStepped(parent, {QtWidgets.QDateTimeEdit.MinuteSection: 5})
            for a minimum 5 minute increment on the minute field.
            """

            def __init__(self, parent: Widget = None, init: bool = None, step_min: dict = None) -> None:
                if step_min is None:
                    step_min = {}
                self.step_min = step_min
                if init:
                    super().__init__(init, parent)
                else:
                    super().__init__(parent)

            def stepBy(self, step: int) -> None:
                cs = self.currentSection()
                if cs in self.step_min and abs(step) < self.step_min[cs]:
                    step = self.step_min[cs] if step > 0 else -self.step_min[cs]
                QtWidgets.QDateTimeEdit.stepBy(self, step)


        class Calendar(QtWidgets.QDialog):  # type:ignore

            def __init__(
                self,
                parent: Widget = None,
                message: str = 'Select Date/Time',
                init: Any = None,  # Hard to annotate.
                step_min: dict = None,
            ) -> None:
                if step_min is None:
                    step_min = {}
                super().__init__(parent)
                layout = QtWidgets.QVBoxLayout()
                self.setLayout(layout)
                layout.addWidget(QtWidgets.QLabel(message))
                self.dt = DateTimeEditStepped(init=init, step_min=step_min)
                self.dt.setCalendarPopup(True)
                layout.addWidget(self.dt)
                buttonBox = QtWidgets.QDialogButtonBox(StandardButton.Ok | StandardButton.Cancel)
                layout.addWidget(buttonBox)
                buttonBox.accepted.connect(self.accept)
                buttonBox.rejected.connect(self.reject)

        #@-<< define date/time classes >>
        if g.unitTesting:
            return None
        if step_min is None:
            step_min = {}
        if not init:
            init = datetime.datetime.now()
        dialog = Calendar(c and c.frame.top, message=message, init=init, step_min=step_min)
        if c:
            ssm = g.app.gui.styleSheetManagerClass(c)
            w = ssm.get_master_widget()
            sheet = w.styleSheet()
            if sheet:
                dialog.setStyleSheet(sheet)
            dialog.setStyleSheet(c.active_stylesheet)
            dialog.setWindowTitle(title)
            try:
                c.in_qt_dialog = True
                dialog.raise_()
                val = dialog.exec() if isQt6 else dialog.exec_()
            finally:
                c.in_qt_dialog = False
        else:
            dialog.setWindowTitle(title)
            dialog.raise_()
            val = dialog.exec() if isQt6 else dialog.exec_()
        if val == DialogCode.Accepted:
            return dialog.dt.dateTime().toPyDateTime()
        return None
    #@+node:ekr.20110605121601.18494: *4* qt_gui.runAskLeoIDDialog (not used)
    def runAskLeoIDDialog(self) -> Optional[str]:
        """Create and run a dialog to get g.app.LeoID."""
        if g.unitTesting:
            return None
        message = (
            "leoID.txt not found\n\n" +
            "Please enter an id that identifies you uniquely.\n" +
            "Your cvs/bzr login name is a good choice.\n\n" +
            "Leo uses this id to uniquely identify nodes.\n\n" +
            "Your id must contain only letters and numbers\n" +
            "and must be at least 3 characters in length.")
        parent = None
        title = 'Enter Leo id'
        s, ok = QtWidgets.QInputDialog.getText(parent, title, message)

        return s
    #@+node:ekr.20110605121601.18491: *4* qt_gui.runAskOkCancelNumberDialog (not used)
    def runAskOkCancelNumberDialog(self,
        c: Cmdr, title: str, message: str, cancelButtonText: str = None, okButtonText: str = None,
    ) -> Optional[int]:
        """Create and run askOkCancelNumber dialog ."""
        if g.unitTesting:
            return None
        # n,ok = QtWidgets.QInputDialog.getDouble(None,title,message)
        dialog = QtWidgets.QInputDialog()
        ssm = g.app.gui.styleSheetManagerClass(c)
        w = ssm.get_master_widget()
        sheet = w.styleSheet()
        if sheet:
            dialog.setStyleSheet(sheet)
        dialog.setWindowTitle(title)
        dialog.setLabelText(message)
        if cancelButtonText:
            dialog.setCancelButtonText(cancelButtonText)
        if okButtonText:
            dialog.setOkButtonText(okButtonText)
        self.attachLeoIcon(dialog)
        dialog.raise_()
        ok = dialog.exec_()
        n = dialog.textValue()
        try:
            n = float(n)
        except ValueError:
            n = None
        return n if ok else None
    #@+node:ekr.20110605121601.18490: *4* qt_gui.runAskOkCancelStringDialog
    def runAskOkCancelStringDialog(
        self,
        c: Cmdr,
        title: str,
        message: str,
        cancelButtonText: str = None,
        okButtonText: str = None,
        default: str = "",
        wide: bool = False,
    ) -> Optional[str]:
        """Create and run askOkCancelString dialog.

        wide - edit a long string
        """
        if g.unitTesting:
            return None
        dialog = QtWidgets.QInputDialog()
        ssm = g.app.gui.styleSheetManagerClass(c)
        w = ssm.get_master_widget()
        sheet = w.styleSheet()
        if sheet:
            dialog.setStyleSheet(sheet)
        dialog.setWindowTitle(title)
        dialog.setLabelText(message)
        dialog.setTextValue(default)
        if wide:
            dialog.resize(int(g.windows()[0].get_window_info()[0] * .9), 100)
        if cancelButtonText:
            dialog.setCancelButtonText(cancelButtonText)
        if okButtonText:
            dialog.setOkButtonText(okButtonText)
        self.attachLeoIcon(dialog)
        dialog.raise_()
        ok = dialog.exec_()
        return str(dialog.textValue()) if ok else None
    #@+node:ekr.20110605121601.18495: *4* qt_gui.runAskOkDialog (changed)
    def runAskOkDialog(self, c: Cmdr, title: str, message: str = None, text: str = "Ok") -> None:
        """Create and run a qt askOK dialog ."""
        if g.unitTesting:
            return

        # Create the dialog.
        dialog = QtWidgets.QMessageBox(c and c.frame.top)
        dialog.setWindowTitle(title)
        if message:
            dialog.setText(message)
        dialog.setIcon(Information.Information)
        yes = dialog.addButton(text, ButtonRole.YesRole)
        dialog.setDefaultButton(yes)  # 2023/10/10.

        # Run the dialog.
        try:
            self._save_focus(c)
            c.in_qt_dialog = True
            dialog.raise_()
            dialog.exec_()
        finally:
            c.in_qt_dialog = False
            self._restore_focus(c)
    #@+node:ekr.20110605121601.18497: *4* qt_gui.runAskYesNoCancelDialog (changed)
    def runAskYesNoCancelDialog(
        self,
        c: Cmdr,
        title: str,
        message: str = None,
        yesMessage: str = "&Yes",
        noMessage: str = "&No",
        yesToAllMessage: str = None,
        defaultButton: str = "Yes",
        cancelMessage: str = None,
    ) -> str:
        """
        Create and run an askYesNo dialog.

        Return one of ('yes', 'no', 'cancel', 'yes-to-all').

        """
        if g.unitTesting:
            return None

        # Create the dialog.
        dialog = QtWidgets.QMessageBox(c and c.frame.top)
        if message:
            dialog.setText(message)
        dialog.setIcon(Information.Warning)
        dialog.setWindowTitle(title)
        # Creation order determines returned value.
        yes = dialog.addButton(yesMessage, ButtonRole.YesRole)
        no = dialog.addButton(noMessage, ButtonRole.NoRole)
        cancel = dialog.addButton(cancelMessage or 'Cancel', ButtonRole.RejectRole)
        if yesToAllMessage:
            dialog.addButton(yesToAllMessage, ButtonRole.YesRole)
        if defaultButton == "Yes":
            dialog.setDefaultButton(yes)
        elif defaultButton == "No":
            dialog.setDefaultButton(no)
        else:
            dialog.setDefaultButton(cancel)

        # Run the dialog, saving and restoring focus.
        try:
            self._save_focus(c)
            c.in_qt_dialog = True
            dialog.raise_()  # #2246.
            val = dialog.exec() if isQt6 else dialog.exec_()
        finally:
            c.in_qt_dialog = False
            self._restore_focus(c)

        # val is the same as the creation order.
        # Tested with both Qt6 and Qt5.
        return {
            0: 'yes', 1: 'no', 2: 'cancel', 3: 'yes-to-all',
        }.get(val, 'cancel')
    #@+node:ekr.20110605121601.18498: *4* qt_gui.runAskYesNoDialog (changed)
    def runAskYesNoDialog(self,
        c: Cmdr, title: str, message: str = None, yes_all: bool = False, no_all: bool = False,
    ) -> str:
        """
        Create and run an askYesNo dialog.
        Return one of ('yes','yes-all','no','no-all')

        :Parameters:
        - `c`: commander
        - `title`: dialog title
        - `message`: dialog message
        - `yes_all`: bool - show YesToAll button
        - `no_all`: bool - show NoToAll button
        """
        if g.unitTesting:
            return None

        # Create the dialog.
        dialog = QtWidgets.QMessageBox(c and c.frame.top)
        # Creation order determines returned value.
        yes = dialog.addButton('Yes', ButtonRole.YesRole)
        dialog.addButton('No', ButtonRole.NoRole)
        # dialog.addButton('Cancel', ButtonRole.RejectRole)
        if yes_all:
            dialog.addButton('Yes To All', ButtonRole.YesRole)
        if no_all:
            dialog.addButton('No To All', ButtonRole.NoRole)
        dialog.setWindowTitle(title)
        if message:
            dialog.setText(message)
        dialog.setIcon(Information.Warning)
        dialog.setDefaultButton(yes)

        if c:
            # Run the dialog, saving and restoring focus.
            try:
                self._save_focus(c)
                c.in_qt_dialog = True
                dialog.raise_()
                val = dialog.exec() if isQt6 else dialog.exec_()
            finally:
                c.in_qt_dialog = False
                self._restore_focus(c)
        else:
            # There is no way to save/restore focus.
            dialog.raise_()
            val = dialog.exec() if isQt6 else dialog.exec_()

        # Create the return dictionary.
        # val is the same as the creation order.
        # Tested with both Qt6 and Qt5.
        return_d = {0: 'yes', 1: 'no'}
        if yes_all and no_all:
            return_d[2] = 'yes-all'
            return_d[3] = 'no-all'
        elif yes_all:
            return_d[2] = 'yes-all'
        elif no_all:
            return_d[2] = 'no-all'
        return return_d.get(val, 'cancel')
    #@+node:ekr.20110605121601.18499: *4* qt_gui.runOpenDirectoryDialog
    def runOpenDirectoryDialog(self, title: str, startdir: str) -> Optional[str]:
        """Create and run an Qt open directory dialog ."""
        if g.unitTesting:
            return None
        dialog = QtWidgets.QFileDialog()
        self.attachLeoIcon(dialog)
        return dialog.getExistingDirectory(None, title, startdir)
    #@+node:ekr.20110605121601.18500: *4* qt_gui.runOpenFileDialog
    def runOpenFileDialog(
        self,
        c: Cmdr,
        title: str,
        filetypes: list[str],
        defaultextension: str = '',
        multiple: bool = False,
        startpath: str = None,
    ) -> Union[list[str], str]:  # Return type depends on the evil multiple keyword.
        """
        Create and run an Qt open file dialog.
        """
        if g.unitTesting:
            return ''

        # 2018/03/14: Bug fixes:
        # - Use init_dialog_folder only if a path is not given
        # - *Never* Use os.curdir by default!
        if not startpath:
            # Returns c.last_dir or os.curdir
            startpath = g.init_dialog_folder(c, c.p, use_at_path=True)
        filter_ = self.makeFilter(filetypes)
        dialog = QtWidgets.QFileDialog()
        self.attachLeoIcon(dialog)
        func = dialog.getOpenFileNames if multiple else dialog.getOpenFileName
        if c:
            try:
                c.in_qt_dialog = True
                val = func(parent=None, caption=title, directory=startpath, filter=filter_)
            finally:
                c.in_qt_dialog = False
        else:
            val = func(parent=None, caption=title, directory=startpath, filter=filter_)
        # This is a *PyQt* change, not a Qt change.
        val, junk_selected_filter = val
        if multiple:
            files = [g.os_path_normslashes(s) for s in val]
            if c and files:
                c.last_dir = g.os_path_dirname(files[-1])
            # A consequence of the evil "multiple" kwarg.
            return files
        s = g.os_path_normslashes(val)
        if c and s:
            c.last_dir = g.os_path_dirname(s)
        return s
    #@+node:ekr.20110605121601.18501: *4* qt_gui.runPropertiesDialog
    def runPropertiesDialog(
        self,
        title: str = 'Properties',
        data: Any = None,
        callback: Callable = None,
        buttons: list[str] = None,
    ) -> tuple[str, dict]:
        """Display a modal TkPropertiesDialog"""
        if not g.unitTesting:
            g.warning('Properties menu not supported for Qt gui')
        return 'Cancel', {}
    #@+node:ekr.20110605121601.18502: *4* qt_gui.runSaveFileDialog (changed)
    def runSaveFileDialog(self,
        c: Cmdr, title: str = 'Save', filetypes: list[str] = None, defaultextension: str = '',
    ) -> str:
        """Create and run an Qt save file dialog ."""
        if g.unitTesting:
            return ''
        dialog = QtWidgets.QFileDialog()
        if c:
            # dialog.setStyleSheet(c.active_stylesheet)
            self.attachLeoIcon(dialog)
            try:
                self._save_focus(c)
                c.in_qt_dialog = True
                obj = dialog.getSaveFileName(
                    None,  # parent
                    title,
                    # os.curdir,
                    g.init_dialog_folder(c, c.p, use_at_path=True),
                    self.makeFilter(filetypes or []),
                )
            finally:
                c.in_qt_dialog = False
                self._restore_focus(c)
        else:
            self.attachLeoIcon(dialog)
            obj = dialog.getSaveFileName(
                None,  # parent
                title,
                # os.curdir,
                g.init_dialog_folder(None, None, use_at_path=True),
                self.makeFilter(filetypes or []),
            )
        # Bizarre: PyQt5 version can return a tuple!
        s = obj[0] if isinstance(obj, (list, tuple)) else obj
        s = s or ''
        if c and s:
            c.last_dir = g.os_path_dirname(s)
        return s
    #@+node:ekr.20110605121601.18503: *4* qt_gui.runScrolledMessageDialog
    def runScrolledMessageDialog(
        self,
        short_title: str = '',
        title: str = 'Message',
        label: str = '',
        msg: str = '',
        c: Cmdr = None,
        **keys: Any,
    ) -> None:
        if g.unitTesting:
            return None

        def send() -> Any:
            return g.doHook('scrolledMessage',
                short_title=short_title, title=title,
                label=label, msg=msg, c=c, **keys)

        if not c or not c.exists:
            #@+<< no c error>>
            #@+node:ekr.20110605121601.18504: *5* << no c error>>
            g.es_print_error('%s\n%s\n\t%s' % (
                "The qt plugin requires calls to g.app.gui.scrolledMessageDialog to include 'c'",
                "as a keyword argument",
                g.callers()
            ))
            #@-<< no c error>>
        else:
            retval = send()
            if retval:
                return retval
            #@+<< load viewrendered plugin >>
            #@+node:ekr.20110605121601.18505: *5* << load viewrendered plugin >>
            pc = g.app.pluginsController
            # Load viewrendered (and call vr.onCreate) *only* if not already loaded.
            if (
                not pc.isLoaded('viewrendered.py')
                and not pc.isLoaded('viewrendered3.py')
            ):
                vr = pc.loadOnePlugin('viewrendered.py')
                if vr:
                    g.blue('viewrendered plugin loaded.')
                    vr.onCreate('tag', {'c': c})
            #@-<< load viewrendered plugin >>
            retval = send()
            if retval:
                return retval
            #@+<< no dialog error >>
            #@+node:ekr.20110605121601.18506: *5* << no dialog error >>
            g.es_print_error(
                f'No handler for the "scrolledMessage" hook.\n\t{g.callers()}')
            #@-<< no dialog error >>
        #@+<< emergency fallback >>
        #@+node:ekr.20110605121601.18507: *5* << emergency fallback >>
        dialog = QtWidgets.QMessageBox(None)
        # That is, not a fixed size dialog.
        dialog.setWindowFlags(WindowType.Dialog)
        dialog.setWindowTitle(title)
        if msg:
            dialog.setText(msg)
        dialog.setIcon(Icon.Information)
        dialog.addButton('Ok', ButtonRole.YesRole)
        try:
            c.in_qt_dialog = True
            if isQt6:
                dialog.exec()
            else:
                dialog.exec_()
        finally:
            c.in_qt_dialog = False
        #@-<< emergency fallback >>
    #@+node:ekr.20110607182447.16456: *3* qt_gui.Event handlers
    #@+node:ekr.20190824094650.1: *4* qt_gui.close_event
    def close_event(self, event: Event) -> None:

        # Save session data.
        g.app.saveSession()

        # Attempt to close all windows.
        for c in g.app.commanders():
            allow = c.exists and g.app.closeLeoWindow(c.frame)
            if not allow:
                event.ignore()
                return
        event.accept()
    #@+node:ekr.20110605121601.18481: *4* qt_gui.onDeactiveEvent
    # deactivated_name = ''

    deactivated_widget = None

    def onDeactivateEvent(self, event: Event, c: Cmdr, obj: Any, tag: str) -> None:
        """
        Gracefully deactivate the Leo window.
        Called several times for each window activation.
        """
        w = self.get_focus()
        w_name = w and w.objectName()
        if 'focus' in g.app.debug:
            g.trace(repr(w_name))
        self.active = False  # Used only by c.idle_focus_helper.
        # Careful: never save headline widgets.
        if w_name == 'headline':
            self.deactivated_widget = c.frame.tree.treeWidget
        else:
            self.deactivated_widget = w if w_name else None
        # Causes problems elsewhere...
            # if c.exists and not self.deactivated_name:
                # self.deactivated_name = self.widget_name(self.get_focus())
                # self.active = False
                # c.k.keyboardQuit(setFocus=False)
        g.doHook('deactivate', c=c, p=c.p, v=c.p, event=event)
    #@+node:ekr.20110605121601.18480: *4* qt_gui.onActivateEvent
    # Called from eventFilter

    def onActivateEvent(self, event: Event, c: Cmdr, obj: Any, tag: str) -> None:
        """
        Restore the focus when the Leo window is activated.
        Called several times for each window activation.
        """
        trace = 'focus' in g.app.debug
        w = self.get_focus() or self.deactivated_widget
        self.deactivated_widget = None
        w_name = w and w.objectName()
        # Fix #270: Vim keys don't always work after double Alt+Tab.
        # Fix #359: Leo hangs in LeoQtEventFilter.eventFilter
        # #1273: add test on c.vim_mode.
        if c.exists and c.vim_mode and c.vimCommands and not self.active and not g.app.killed:
            c.vimCommands.on_activate()
        self.active = True  # Used only by c.idle_focus_helper.
        if g.isMac:
            pass  # Fix #757: MacOS: replace-then-find does not work in headlines.
        else:
            # Leo 5.6: Recover from missing focus.
            # c.idle_focus_handler can't do this.
            if w and w_name in ('log-widget', 'richTextEdit', 'treeWidget'):
                # Restore focus **only** to body or tree
                if trace:
                    g.trace('==>', w_name)
                c.widgetWantsFocusNow(w)
            else:
                if trace:
                    g.trace(repr(w_name), '==> BODY')
                c.bodyWantsFocusNow()
        # Cause problems elsewhere.
            # if c.exists and self.deactivated_name:
                # self.active = True
                # w_name = self.deactivated_name
                # self.deactivated_name = None
                # if c.p.v:
                    # c.p.v.restoreCursorAndScroll()
                # if w_name.startswith('tree') or w_name.startswith('head'):
                    # c.treeWantsFocusNow()
                # else:
                    # c.bodyWantsFocusNow()
        g.doHook('activate', c=c, p=c.p, v=c.p, event=event)
    #@+node:ekr.20130921043420.21175: *4* qt_gui.setFilter
    def setFilter(self, c: Cmdr, obj: Any, w: Wrapper, tag: str) -> None:
        """
        Create an event filter in obj.
        w is a wrapper object, not necessarily a QWidget.
        """
        # w's type is in (DynamicWindow,QMinibufferWrapper,LeoQtLog,LeoQtTree,
        # QTextEditWrapper,LeoQTextBrowser,LeoQuickSearchWidget,cleoQtUI)
        assert isinstance(obj, QtWidgets.QWidget), obj
        theFilter = qt_events.LeoQtEventFilter(c, w=w, tag=tag)
        obj.installEventFilter(theFilter)
        w.ev_filter = theFilter  # Set the official ivar in w.
    #@+node:ekr.20110605121601.18508: *3* qt_gui.Focus
    #@+node:ekr.20190601055031.1: *4* qt_gui.ensure_commander_visible
    def ensure_commander_visible(self, c1: Cmdr) -> None:
        """
        Check to see if c.frame is in a tabbed ui, and if so, make sure
        the tab is visible
        """
        if 'focus' in g.app.debug:
            g.trace(c1)
        if hasattr(g.app.gui, 'frameFactory'):
            factory = g.app.gui.frameFactory
            if factory and hasattr(factory, 'setTabForCommander'):
                c = c1
                factory.setTabForCommander(c)
                c.bodyWantsFocusNow()
    #@+node:ekr.20190601054958.1: *4* qt_gui.get_focus (no longer used)
    def get_focus(self, c: Cmdr = None, raw: bool = False, at_idle: bool = False) -> Widget:
        """Returns the widget that has focus."""
        trace = 'focus' in g.app.debug
        trace_idle = False
        trace = trace and (trace_idle or not at_idle)
        app = QtWidgets.QApplication
        w = app.focusWidget()
        if w and not raw and isinstance(w, qt_text.LeoQTextBrowser):
            has_w = getattr(w, 'leo_wrapper', None)
            if has_w:
                if trace:
                    g.trace(w)
            elif c:
                # Kludge: DynamicWindow creates the body pane
                # with wrapper = None, so return the LeoQtBody.
                w = c.frame.body
        if trace:
            name = w.objectName() if hasattr(w, 'objectName') else w.__class__.__name__
            g.trace('(LeoQtGui)', name)
        return w
    #@+node:ekr.20190601054959.1: *4* qt_gui.set_focus
    def set_focus(self, c: Cmdr, w: Wrapper) -> None:
        """Put the focus on the widget."""
        if not w:
            return
        if getattr(w, 'widget', None):
            if not isinstance(w, QtWidgets.QWidget):
                # w should be a wrapper.
                w = w.widget
        if 'focus' in g.app.debug:
            name = w.objectName() if hasattr(w, 'objectName') else w.__class__.__name__
            g.trace('(LeoQtGui)', name)
        w.setFocus()
    #@+node:ekr.20110605121601.18510: *3* qt_gui.getFontFromParams
    size_warnings: list[str] = []
    font_ids: list[int] = []  # id's of traced fonts.

    def getFontFromParams(self,
        family: str, size: str, slant: str, weight: str, defaultSize: int = 12, tag='',
    ) -> Any:
        """Required to handle syntax coloring."""
        if isinstance(size, str):
            if size.endswith('pt'):
                size = size[:-2].strip()
            elif size.endswith('px'):
                if size not in self.size_warnings:
                    self.size_warnings.append(size)
                    g.es(f"px ignored in font setting: {size}")
                size = size[:-2].strip()
        try:
            i_size = int(size)
        except Exception:
            i_size = 0
        if i_size < 1:
            i_size = defaultSize
        d = {
            'black': Weight.Black,
            'bold': Weight.Bold,
            'demibold': Weight.DemiBold,
            'light': Weight.Light,
            'normal': Weight.Normal,
        }
        weight_val = d.get(weight.lower(), Weight.Normal)
        italic = slant == 'italic'
        if not family:
            family = 'DejaVu Sans Mono'
        try:
            font = QtGui.QFont(family, i_size, weight_val, italic)
            if sys.platform.startswith('linux'):
                try:
                    font.setHintingPreference(font.PreferFullHinting)
                except AttributeError:
                    pass
            return font
        except Exception:
            g.es_print("exception setting font", g.callers(4))
            g.es_print(
                f"family: {family}\n"
                f"  size: {i_size}\n"
                f" slant: {slant}\n"
                f"weight: {weight}")
            # g.es_exception() # Confusing for most users.
            return None
    #@+node:ekr.20110605121601.18511: *3* qt_gui.getFullVersion
    def getFullVersion(self, c: Cmdr = None) -> str:
        """Return the PyQt version (for signon)"""
        try:
            qtLevel = f"version {QtCore.qVersion()}"
        except Exception:
            # g.es_exception()
            qtLevel = '<qtLevel>'
        return f"PyQt {qtLevel}"
    #@+node:ekr.20110605121601.18514: *3* qt_gui.Icons
    #@+node:ekr.20110605121601.18515: *4* qt_gui.attachLeoIcon
    def attachLeoIcon(self, window: Any) -> None:
        """Attach a Leo icon to the window."""
        if self.appIcon:
            window.setWindowIcon(self.appIcon)
    #@+node:ekr.20110605121601.18516: *4* qt_gui.getIconImage
    def getIconImage(self, name: str) -> Any:
        """Load the icon and return it."""
        # Return the image from the cache if possible.
        if name in self.iconimages:
            image = self.iconimages.get(name)
            return image
        try:
            iconsDir = g.os_path_join(g.app.loadDir, "..", "Icons")
            homeIconsDir = g.os_path_join(g.app.homeLeoDir, "Icons")
            for theDir in (homeIconsDir, iconsDir):
                fullname = g.finalize_join(theDir, name)
                if g.os_path_exists(fullname):
                    if 0:  # Not needed: use QTreeWidget.setIconsize.
                        pixmap = QtGui.QPixmap()
                        pixmap.load(fullname)
                        image = QtGui.QIcon(pixmap)
                    else:
                        image = QtGui.QIcon(fullname)
                    self.iconimages[name] = image
                    return image
            # No image found.
            return None
        except Exception:
            g.es_print("exception loading:", fullname)
            g.es_exception()
            return None
    #@+node:ekr.20110605121601.18517: *4* qt_gui.getImageImage
    @functools.lru_cache(maxsize=128)
    def getImageImage(self, name: str) -> Any:
        """Load the image in file named `name` and return it."""
        fullname = self.getImageFinder(name)
        try:
            pixmap = QtGui.QPixmap()
            pixmap.load(fullname)
            return pixmap
        except Exception:
            g.es("exception loading:", name)
            g.es_exception()
            return None
    #@+node:tbrown.20130316075512.28478: *4* qt_gui.getImageFinder
    dump_given = False
    @functools.lru_cache(maxsize=128)
    def getImageFinder(self, name: str) -> Optional[str]:
        """Theme aware image (icon) path searching."""
        trace = 'themes' in g.app.debug
        exists = g.os_path_exists
        getString = g.app.config.getString

        def dump(var: str, val: str) -> None:
            print(f"{var:20}: {val}")

        join = g.os_path_join
        #
        # "Just works" for --theme and theme .leo files *provided* that
        # theme .leo files actually contain these settings!
        #
        theme_name1 = getString('color-theme')
        theme_name2 = getString('theme-name')
        roots = [
            g.os_path_join(g.computeHomeDir(), '.leo'),
            g.computeLeoDir(),
        ]
        theme_subs = [
            "themes/{theme}/Icons",
            "themes/{theme}",
            "Icons/{theme}",
        ]
        # "." for icons referred to as Icons/blah/blah.png
        bare_subs = ["Icons", "."]
        paths = []
        for theme_name in (theme_name1, theme_name2):
            for root in roots:
                for sub in theme_subs:
                    paths.append(join(root, sub.format(theme=theme_name)))
        for root in roots:
            for sub in bare_subs:
                paths.append(join(root, sub))
        table = [z for z in paths if exists(z)]
        for base_dir in table:
            path = join(base_dir, name)
            if exists(path):
                if trace:
                    g.trace(f"Found {name} in {base_dir}")
                return path
            # if trace: g.trace(name, 'not in', base_dir)
        if trace:
            g.trace('not found:', name)
        return None
    #@+node:ekr.20110605121601.18518: *4* qt_gui.getTreeImage
    @functools.lru_cache(maxsize=128)
    def getTreeImage(self, c: Cmdr, path: str) -> tuple[Any, int]:
        image = QtGui.QPixmap(path)
        if image.height() > 0 and image.width() > 0:
            return image, image.height()
        return None, None
    #@+node:ekr.20131007055150.17608: *3* qt_gui.insertKeyEvent
    def insertKeyEvent(self, event: Event, i: int) -> None:
        """Insert the key given by event in location i of widget event.w."""
        assert isinstance(event, leoGui.LeoKeyEvent)
        qevent = event.event
        assert isinstance(qevent, QtGui.QKeyEvent)
        qw = getattr(event.w, 'widget', None)
        if qw and isinstance(qw, QtWidgets.QTextEdit):
            if 1:
                # Assume that qevent.text() *is* the desired text.
                # This means we don't have to hack eventFilter.
                qw.insertPlainText(qevent.text())
            else:
                # Make no such assumption.
                # We would like to use qevent to insert the character,
                # but this would invoke eventFilter again!
                # So set this flag for eventFilter, which will
                # return False, indicating that the widget must handle
                # qevent, which *presumably* is the best that can be done.
                g.app.gui.insert_char_flag = True
    #@+node:ekr.20110605121601.18528: *3* qt_gui.makeScriptButton
    def makeScriptButton(
        self,
        c: Cmdr,
        args: Any = None,
        p: Position = None,  # A node containing the script.
        script: str = None,  # The script itself.
        buttonText: str = None,
        balloonText: str = 'Script Button',
        shortcut: str = None,
        bg: str = 'LightSteelBlue1',
        define_g: bool = True,
        define_name: str = '__main__',
        silent: bool = False,  # Passed on to c.executeScript.
    ) -> None:
        """
        Create a script button for the script in node p.
        The button's text defaults to p.headString."""
        # pylint: disable=line-too-long
        k = c.k
        if p and not buttonText:
            buttonText = p.h.strip()
        if not buttonText:
            buttonText = 'Unnamed Script Button'
        #@+<< create the button b >>
        #@+node:ekr.20110605121601.18529: *4* << create the button b >>
        iconBar = c.frame.getIconBarObject()
        b = iconBar.add(text=buttonText)
        #@-<< create the button b >>
        #@+<< define the callbacks for b >>
        #@+node:ekr.20110605121601.18530: *4* << define the callbacks for b >>
        def deleteButtonCallback(event: Event = None, b: Widget = b, c: Cmdr = c) -> None:
            if b:
                b.pack_forget()
            c.bodyWantsFocus()

        def executeScriptCallback(
            event: Event = None,
            b: Widget = b,
            c: Cmdr = c,
            buttonText: str = buttonText,
            p: Position = p and p.copy(),
            script: str = script
        ) -> None:
            if c.disableCommandsMessage:
                g.blue('', c.disableCommandsMessage)
            else:
                g.app.scriptDict = {'script_gnx': p.gnx}
                c.executeScript(args=args, p=p, script=script,
                define_g=define_g, define_name=define_name, silent=silent)
                # Remove the button if the script asks to be removed.
                if g.app.scriptDict.get('removeMe'):
                    g.es('removing', f"'{buttonText}'", 'button at its request')
                    b.pack_forget()
            # Do not assume the script will want to remain in this commander.

        #@-<< define the callbacks for b >>

        b.configure(command=executeScriptCallback)
        if shortcut:
            #@+<< bind the shortcut to executeScriptCallback >>
            #@+node:ekr.20110605121601.18531: *4* << bind the shortcut to executeScriptCallback >>
            # In qt_gui.makeScriptButton.
            func = executeScriptCallback
            if shortcut:
                shortcut = g.KeyStroke(shortcut)  # type:ignore
            ok = k.bindKey('button', shortcut, func, buttonText)
            if ok:
                g.blue('bound @button', buttonText, 'to', shortcut)
            #@-<< bind the shortcut to executeScriptCallback >>
        #@+<< create press-buttonText-button command >>
        #@+node:ekr.20110605121601.18532: *4* << create press-buttonText-button command >> qt_gui.makeScriptButton
        # #1121. Like sc.cleanButtonText
        buttonCommandName = f"press-{buttonText.replace(' ', '-').strip('-')}-button"
        #
        # This will use any shortcut defined in an @shortcuts node.
        k.registerCommand(buttonCommandName, executeScriptCallback, pane='button')
        #@-<< create press-buttonText-button command >>
    #@+node:ekr.20200304125716.1: *3* qt_gui.onContextMenu
    def onContextMenu(self, c: Cmdr, w: Wrapper, point: Any) -> None:
        """LeoQtGui: Common context menu handling."""
        # #1286.
        handlers = g.tree_popup_handlers
        menu = QtWidgets.QMenu(c.frame.top)  # #1995.
        menuPos = w.mapToGlobal(point)
        if not handlers:
            menu.addAction("No popup handlers")
        p = c.p.copy()
        done: set[Callable] = set()
        for handler in handlers:
            # every handler has to add it's QActions by itself
            if handler in done:
                # do not run the same handler twice
                continue
            try:
                handler(c, p, menu)
                done.add(handler)
            except Exception:
                g.es_print('Exception executing right-click handler')
                g.es_exception()
        menu.popup(menuPos)
        self._contextmenu = menu
    #@+node:ekr.20170612065255.1: *3* qt_gui.put_help
    def put_help(self, c: Cmdr, s: str, short_title: str = '') -> Any:
        """Put the help command."""
        s = textwrap.dedent(s.rstrip())
        if s.startswith('<') and not s.startswith('<<'):
            pass  # how to do selective replace??
        pc = g.app.pluginsController
        table = (
            'viewrendered3.py',
            'viewrendered.py',
        )
        for name in table:
            if pc.isLoaded(name):
                vr = pc.loadOnePlugin(name)
                break
        else:
            vr = pc.loadOnePlugin('viewrendered.py')
        if vr:
            kw = {
                'c': c,
                'flags': 'rst',
                'kind': 'rst',
                'label': '',
                'msg': s,
                'name': 'Apropos',
                'short_title': short_title,
                'title': ''}
            vr.show_scrolled_message(tag='Apropos', kw=kw)
            c.bodyWantsFocus()
            if g.unitTesting:
                vr.close_rendering_pane(event={'c': c})
        elif g.unitTesting:
            pass
        else:
            g.es(s)
        return vr  # For unit tests
    #@+node:ekr.20110605121601.18521: *3* qt_gui.runAtIdle
    def runAtIdle(self, aFunc: Callable) -> None:
        """This can not be called in some contexts."""
        QtCore.QTimer.singleShot(0, aFunc)
    #@+node:ekr.20110605121601.18483: *3* qt_gui.runMainLoop & runWithIpythonKernel
    #@+node:ekr.20130930062914.16000: *4* qt_gui.runMainLoop
    def runMainLoop(self) -> None:
        """Start the Qt main loop."""
        try:  # #2127: A crash here hard-crashes Leo: There is no main loop!
            g.app.gui.dismiss_splash_screen()
            c = g.app.log and g.app.log.c
            if c and c.config.getBool('show-tips', default=False):
                g.app.gui.show_tips(c)
        except Exception:
            g.es_exception()
        if self.script:
            log = g.app.log
            if log:
                g.pr('Start of batch script...\n')
                log.c.executeScript(script=self.script)
                g.pr('End of batch script')
            else:
                g.pr('no log, no commander for executeScript in LeoQtGui.runMainLoop')
        elif g.app.useIpython and g.app.ipython_inited:
            self.runWithIpythonKernel()
        else:
            # This can be alarming when using Python's -i option.
            if isQt6:
                sys.exit(self.qtApp.exec())
            else:
                sys.exit(self.qtApp.exec_())
    #@+node:ekr.20130930062914.16001: *4* qt_gui.runWithIpythonKernel (commands)
    def runWithIpythonKernel(self) -> None:
        """Init Leo to run in an IPython shell."""
        try:
            from leo.core import leoIPython
            g.app.ipk = leoIPython.InternalIPKernel()
            g.app.ipk.run()
        except Exception:
            g.es_exception()
            print('can not init leo.core.leoIPython.py')
            sys.exit(1)
    #@+node:ekr.20180117053546.1: *3* qt_gui.show_tips & helpers
    @g.command('show-tips')
    def show_next_tip(self, event: Event = None) -> None:
        c = g.app.log and g.app.log.c
        if c:
            g.app.gui.show_tips(c)

    #@+<< define DialogWithCheckBox >>
    #@+node:ekr.20220123052350.1: *4* << define DialogWithCheckBox >>
    class DialogWithCheckBox(QtWidgets.QMessageBox):  # type:ignore

        def __init__(self, controller: Any, checked: bool, tip: UserTip) -> None:
            super().__init__()
            c = g.app.log.c
            self.leo_checked = True
            self.setObjectName('TipMessageBox')
            self.setIcon(Icon.Information)  # #2127.
            # self.setMinimumSize(5000, 4000)
                # Doesn't work.
                # Prevent the dialog from jumping around when
                # selecting multiple tips.
            self.setWindowTitle('Leo Tips')
            self.setText(repr(tip))
            self.next_tip_button = self.addButton('Show Next Tip', ButtonRole.ActionRole)  # #2127
            self.addButton('Ok', ButtonRole.YesRole)  # #2127.
            c.styleSheetManager.set_style_sheets(w=self)
            # Workaround #693.
            layout = self.layout()
            cb = QtWidgets.QCheckBox()
            cb.setObjectName('TipCheckbox')
            cb.setText('Show Tip On Startup')
            # #2383: State is a tri-state, so use the official constants.
            state = QtConst.CheckState.Checked if checked else QtConst.CheckState.Unchecked
            cb.setCheckState(state)  # #2127.
            cb.stateChanged.connect(controller.onClick)
            layout.addWidget(cb, 4, 0, -1, -1)
            if 0:  # Does not work well.
                sizePolicy = QtWidgets.QSizePolicy
                vSpacer = QtWidgets.QSpacerItem(
                    200, 200, sizePolicy.Minimum, sizePolicy.Expanding)
                layout.addItem(vSpacer)
    #@-<< define DialogWithCheckBox >>

    def show_tips(self, c: Cmdr) -> None:
        if g.unitTesting:
            return
        from leo.core import leoTips
        tm = leoTips.TipManager()
        self.show_tips_flag = c.config.getBool('show-tips', default=False)  # 2390.
        while True:  # QMessageBox is always a modal dialog.
            tip = tm.get_next_tip()
            m = self.DialogWithCheckBox(controller=self, checked=self.show_tips_flag, tip=tip)
            try:
                c.in_qt_dialog = True
                m.exec_()
            finally:
                c.in_qt_dialog = False
            b = m.clickedButton()
            if b != m.next_tip_button:
                break
    #@+node:ekr.20180117080131.1: *4* onButton (not used)
    def onButton(self, m: Any) -> None:
        m.hide()
    #@+node:ekr.20180117073603.1: *4* onClick
    def onClick(self, state: str) -> None:
        c = g.app.log.c
        self.show_tips_flag = bool(state)
        if c:  # #2390: The setting *has* changed.
            c.config.setUserSetting('@bool show-tips', self.show_tips_flag)
            c.redraw()  # #2390: Show the change immediately.
    #@+node:ekr.20180127103142.1: *4* onNext (not used)
    def onNext(self, *args: Any, **keys: Any) -> bool:
        g.trace(args, keys)
        return True
    #@+node:ekr.20111215193352.10220: *3* qt_gui.Splash Screen
    #@+node:ekr.20110605121601.18479: *4* qt_gui.createSplashScreen
    def createSplashScreen(self) -> Widget:
        """Put up a splash screen with Leo's logo."""
        try:
            QApplication = QtWidgets.QApplication
            QPixmap = QtGui.QPixmap
            QSvgRenderer = QtSvg.QSvgRenderer
            QPainter = QtGui.QPainter
            QImage = QtGui.QImage
            QScreen = QtGui.QScreen
        except Exception:
            return None

        Format_RGB32 = 4  # a Qt enumeration value

        splash = None
        for fn in (
            'SplashScreen.svg',  # Leo's licensed .svg logo.
            'Leosplash.GIF',  # Leo's public domain bitmapped image.
        ):
            path = g.finalize_join(g.app.loadDir, '..', 'Icons', fn)
            if g.os_path_exists(path):
                if fn.endswith('svg'):
                    # Convert SVG to un-pixilated pixmap
                    renderer = QSvgRenderer(path)
                    size = renderer.defaultSize()
                    svg_height, svg_width = size.height(), size.width()

                    # Scale to fraction of screen height
                    geom = QScreen.availableGeometry(QApplication.primaryScreen())
                    screen_height = geom.height()
                    target_height_px = screen_height // 4
                    scaleby = target_height_px / svg_height
                    target_width_px = int(svg_width * scaleby)

                    image = QImage(target_width_px, target_height_px,
                                   QImage.Format(Format_RGB32))
                    image.fill(0xffffffff)  # MUST fill background
                    painter = QPainter(image)
                    renderer.render(painter)
                    painter.end()

                    pixmap = QPixmap.fromImage(image)
                else:
                    pixmap = QtGui.QPixmap(path)
                if not pixmap.isNull():
                    splash = QtWidgets.QSplashScreen(pixmap, WindowType.WindowStaysOnTopHint)
                    splash.show()
                    sleep(.2)
                    splash.repaint()
                    break  # Done.
        return splash
    #@+node:ekr.20110613103140.16424: *4* qt_gui.dismiss_splash_screen
    def dismiss_splash_screen(self) -> None:

        gui = self
        # Warning: closing the splash screen must be done in the main thread!
        if g.unitTesting:
            return
        if gui.splashScreen:
            gui.splashScreen.hide()
            # gui.splashScreen.deleteLater()
            gui.splashScreen = None
    #@+node:ekr.20140825042850.18411: *3* qt_gui.Utils...
    #@+node:ekr.20110605121601.18522: *4* qt_gui.isTextWidget/Wrapper
    def isTextWidget(self, w: Wrapper) -> bool:
        """Return True if w is some kind of Qt text widget."""
        if Qsci:
            return isinstance(w, (Qsci.QsciScintilla, QtWidgets.QTextEdit))
        return isinstance(w, QtWidgets.QTextEdit)

    def isTextWrapper(self, w: Wrapper) -> bool:
        """Return True if w is a Text widget suitable for text-oriented commands."""
        if w is None:
            return False
        if isinstance(w, (g.NullObject, g.TracingNullObject)):
            return True
        return bool(getattr(w, 'supportsHighLevelInterface', None))
    #@+node:ekr.20110605121601.18527: *4* qt_gui.widget_name
    def widget_name(self, w: Wrapper) -> str:
        # First try the widget's getName method.
        if not w:
            name = '<no widget>'
        elif hasattr(w, 'getName'):
            name = w.getName()
        elif hasattr(w, 'objectName'):
            name = str(w.objectName())
        elif hasattr(w, '_name'):
            name = w._name
        else:
            name = repr(w)
        return name
    #@+node:ekr.20111027083744.16532: *4* qt_gui.enableSignalDebugging
    if isQt5:
        # pylint: disable=no-name-in-module
        # To do: https://doc.qt.io/qt-5/qsignalspy.html
        from PyQt5.QtTest import QSignalSpy
        assert QSignalSpy
    elif isQt6:
        # pylint: disable=c-extension-no-member,no-name-in-module
        import PyQt6.QtTest as QtTest
        # mypy complains about assigning to a type.
        QSignalSpy = QtTest.QSignalSpy  # type:ignore
        assert QSignalSpy
    else:
        # enableSignalDebugging(emitCall=foo) and spy your signals until you're sick to your stomach.
        _oldConnect = QtCore.QObject.connect
        _oldDisconnect = QtCore.QObject.disconnect
        _oldEmit = QtCore.QObject.emit

        def _wrapConnect(self, callableObject: Callable) -> Callable:
            """Returns a wrapped call to the old version of QtCore.QObject.connect"""

            @staticmethod  # type:ignore
            def call(*args: Any) -> None:
                callableObject(*args)
                self._oldConnect(*args)

            return call

        def _wrapDisconnect(self, callableObject: Callable) -> Callable:
            """Returns a wrapped call to the old version of QtCore.QObject.disconnect"""

            @staticmethod  # type:ignore
            def call(*args: Any) -> None:
                callableObject(*args)
                self._oldDisconnect(*args)

            return call

        def enableSignalDebugging(self, **kwargs: Any) -> None:
            """Call this to enable Qt Signal debugging. This will trap all
            connect, and disconnect calls."""

            def f(*args):
                return None
            connectCall: Callable = kwargs.get('connectCall', f)
            disconnectCall: Callable = kwargs.get('disconnectCall', f)
            emitCall: Callable = kwargs.get('emitCall', f)

            def printIt(msg: str) -> Callable:

                def call(*args: Any) -> None:
                    print(msg, args)

                return call

            # Monkey-patch.

            QtCore.QObject.connect = self._wrapConnect(connectCall)
            QtCore.QObject.disconnect = self._wrapDisconnect(disconnectCall)

            def new_emit(self, *args: Any) -> None:  # type:ignore
                emitCall(self, *args)
                self._oldEmit(self, *args)

            QtCore.QObject.emit = new_emit
    #@+node:ekr.20190819091957.1: *3* qt_gui.Widgets...
    #@+node:ekr.20190819094016.1: *4* qt_gui.createButton
    def createButton(self, parent: Widget, name: str, label: str) -> Widget:
        w = QtWidgets.QPushButton(parent)
        w.setObjectName(name)
        w.setText(label)
        return w
    #@+node:ekr.20190819091122.1: *4* qt_gui.createFrame
    def createFrame(
        self,
        parent: Widget,
        name: str,
        hPolicy: Policy = None,
        vPolicy: Policy = None,
        lineWidth: int = 1,
        shadow: Shadow = None,
        shape: Shape = None,
    ) -> Widget:
        """Create a Qt Frame."""
        if shadow is None:
            shadow = Shadow.Plain
        if shape is None:
            shape = Shape.NoFrame
        #
        w = QtWidgets.QFrame(parent)
        self.setSizePolicy(w, kind1=hPolicy, kind2=vPolicy)
        w.setFrameShape(shape)
        w.setFrameShadow(shadow)
        w.setLineWidth(lineWidth)
        w.setObjectName(name)
        return w
    #@+node:ekr.20190819091851.1: *4* qt_gui.createGrid
    def createGrid(self, parent: Widget, name: str, margin: int = 0, spacing: int = 0) -> Widget:
        w = QtWidgets.QGridLayout(parent)
        w.setContentsMargins(QtCore.QMargins(margin, margin, margin, margin))
        w.setSpacing(spacing)
        w.setObjectName(name)
        return w
    #@+node:ekr.20190819093830.1: *4* qt_gui.createHLayout & createVLayout
    def createHLayout(self, parent: Widget, name: str, margin: int = 0, spacing: int = 0) -> Any:
        hLayout = QtWidgets.QHBoxLayout(parent)
        hLayout.setObjectName(name)
        hLayout.setSpacing(spacing)
        hLayout.setContentsMargins(QtCore.QMargins(0, 0, 0, 0))
        return hLayout

    def createVLayout(self, parent: Widget, name: str, margin: int = 0, spacing: int = 0) -> Any:
        vLayout = QtWidgets.QVBoxLayout(parent)
        vLayout.setObjectName(name)
        vLayout.setSpacing(spacing)
        vLayout.setContentsMargins(QtCore.QMargins(0, 0, 0, 0))
        return vLayout
    #@+node:ekr.20190819094302.1: *4* qt_gui.createLabel
    def createLabel(self, parent: Widget, name: str, label: str) -> Widget:
        w = QtWidgets.QLabel(parent)
        w.setObjectName(name)
        w.setText(label)
        return w
    #@+node:ekr.20190819092523.1: *4* qt_gui.createTabWidget
    def createTabWidget(self, parent: Widget, name: str, hPolicy: Policy = None, vPolicy: Policy = None) -> Widget:
        w = QtWidgets.QTabWidget(parent)
        self.setSizePolicy(w, kind1=hPolicy, kind2=vPolicy)
        w.setObjectName(name)
        return w
    #@+node:ekr.20190819091214.1: *4* qt_gui.setSizePolicy
    def setSizePolicy(self, widget: Widget, kind1: Policy = None, kind2: Policy = None) -> None:
        if kind1 is None:
            kind1 = Policy.Ignored
        if kind2 is None:
            kind2 = Policy.Ignored
        sizePolicy = QtWidgets.QSizePolicy(kind1, kind2)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(widget.sizePolicy().hasHeightForWidth())
        widget.setSizePolicy(sizePolicy)
    #@-others
#@+node:tbrown.20150724090431.1: ** class StyleClassManager
class StyleClassManager:
    style_sclass_property = 'style_class'  # name of QObject property for styling
    #@+others
    #@+node:tbrown.20150724090431.2: *3* update_view
    def update_view(self, w: Wrapper) -> None:
        """update_view - Make Qt apply w's style

        :param QWidgit w: widget to style
        """

        w.setStyleSheet("/* */")  # forces visual update
    #@+node:tbrown.20150724090431.3: *3* add_sclass
    def add_sclass(self, w: Wrapper, prop: Any) -> None:
        """Add style class or list of classes prop to QWidget w"""
        if not prop:
            return
        props = self.sclasses(w)
        if isinstance(prop, str):
            props.append(prop)
        else:
            props.extend(prop)
        self.set_sclasses(w, props)
    #@+node:tbrown.20150724090431.4: *3* clear_sclasses
    def clear_sclasses(self, w: Wrapper) -> None:
        """Remove all style classes from QWidget w"""
        w.setProperty(self.style_sclass_property, '')
    #@+node:tbrown.20150724090431.5: *3* has_sclass
    def has_sclass(self, w: Wrapper, prop: Any) -> bool:
        """Check for style class or list of classes prop on QWidget w"""
        if not prop:
            return None
        props = self.sclasses(w)
        if isinstance(prop, str):
            ans = [prop in props]
        else:
            ans = [i in props for i in prop]
        return all(ans)
    #@+node:tbrown.20150724090431.6: *3* remove_sclass
    def remove_sclass(self, w: Wrapper, prop: Any) -> None:
        """Remove style class or list of classes prop from QWidget w"""
        if not prop:
            return
        props = self.sclasses(w)
        if isinstance(prop, str):
            props = [i for i in props if i != prop]
        else:
            props = [i for i in props if i not in prop]

        self.set_sclasses(w, props)
    #@+node:tbrown.20150724090431.8: *3* sclasses
    def sclasses(self, w: Wrapper) -> list[str]:
        """return list of style classes for QWidget w"""
        return str(w.property(self.style_sclass_property) or '').split()
    #@+node:tbrown.20150724090431.9: *3* set_sclasses
    def set_sclasses(self, w: Wrapper, classes: Any) -> None:
        """Set style classes for QWidget w to list in classes"""
        w.setProperty(self.style_sclass_property, f" {' '.join(set(classes))} ")
    #@+node:tbrown.20150724090431.10: *3* toggle_sclass
    def toggle_sclass(self, w: Wrapper, prop: Any) -> None:
        """Toggle style class or list of classes prop on QWidget w"""
        if not prop:
            return
        props = set(self.sclasses(w))
        if isinstance(prop, str):
            prop = set([prop])
        else:
            prop = set(prop)
        current = props.intersection(prop)
        props.update(prop)
        props = props.difference(current)
        self.set_sclasses(w, props)
    #@-others
#@+node:ekr.20140913054442.17860: ** class StyleSheetManager
class StyleSheetManager:
    """A class to manage (reload) Qt style sheets."""
    #@+others
    #@+node:ekr.20180316091829.1: *3*  ssm.Birth
    #@+node:ekr.20140912110338.19371: *4* ssm.__init__
    def __init__(self, c: Cmdr, safe: bool = False) -> None:
        """Ctor the ReloadStyle class."""
        self.c = c
        self.color_db = leoColor.leo_color_database
        self.safe = safe
        self.settings_p = g.findNodeAnywhere(c, '@settings')
        self.mng = StyleClassManager()
        # This warning is inappropriate in some contexts.
            # if not self.settings_p:
                # g.es("No '@settings' node found in outline.  See:")
                # g.es("https://leo-editor.github.io/leo-editor/tutorial-basics.html#configuring-leo")
    #@+node:ekr.20170222051716.1: *4* ssm.reload_settings
    def reload_settings(self, sheet: str = None) -> None:
        """
        Recompute and apply the stylesheet.
        Called automatically by the reload-settings commands.
        """
        if not sheet:
            sheet = self.get_style_sheet_from_settings()
        if sheet:
            w = self.get_master_widget()
            w.setStyleSheet(sheet)
        # self.c.redraw()

    reloadSettings = reload_settings
    #@+node:ekr.20180316091500.1: *3* ssm.Paths...
    #@+node:ekr.20180316065346.1: *4* ssm.compute_icon_directories
    def compute_icon_directories(self) -> list[str]:
        """
        Return a list of *existing* directories that could contain theme-related icons.
        """
        exists = g.os_path_exists
        home = g.app.homeDir
        join = g.finalize_join
        leo = join(g.app.loadDir, '..')
        table = [
            join(home, '.leo', 'Icons'),
            # join(home, '.leo'),
            join(leo, 'themes', 'Icons'),
            join(leo, 'themes'),
            join(leo, 'Icons'),
        ]
        table = [z for z in table if exists(z)]
        for directory in self.compute_theme_directories():
            if directory not in table:
                table.append(directory)
            directory2 = join(directory, 'Icons')
            if directory2 not in table:
                table.append(directory2)
        return [g.os_path_normslashes(z) for z in table if g.os_path_exists(z)]
    #@+node:ekr.20180315101238.1: *4* ssm.compute_theme_directories
    def compute_theme_directories(self) -> list[str]:
        """
        Return a list of *existing* directories that could contain theme .leo files.
        """
        lm = g.app.loadManager
        table = lm.computeThemeDirectories()[:]
        directory = g.os_path_normslashes(g.app.theme_directory)
        if directory and directory not in table:
            table.insert(0, directory)
        # All entries are known to exist and have normalized slashes.
        return table
    #@+node:ekr.20170307083738.1: *4* ssm.find_icon_path
    def find_icon_path(self, setting: str) -> Optional[str]:
        """Return the path to the open/close indicator icon."""
        c = self.c
        s = c.config.getString(setting)
        if not s:
            return None  # Not an error.
        for directory in self.compute_icon_directories():
            path = g.finalize_join(directory, s)
            if g.os_path_exists(path):
                return path
        g.es_print('no icon found for:', setting)
        return None
    #@+node:ekr.20180316091920.1: *3* ssm.Settings
    #@+node:ekr.20110605121601.18176: *4* ssm.default_style_sheet
    def default_style_sheet(self) -> str:
        """Return a reasonable default style sheet."""
        # Valid color names: http://www.w3.org/TR/SVG/types.html#ColorKeywords
        g.trace('===== using default style sheet =====')
        return '''\

    /* A QWidget: supports only background attributes.*/
    QSplitter::handle {
        background-color: #CAE1FF; /* Leo's traditional lightSteelBlue1 */
    }
    QSplitter {
        border-color: white;
        background-color: white;
        border-width: 3px;
        border-style: solid;
    }
    QTreeWidget {
        background-color: #ffffec; /* Leo's traditional tree color */
    }
    QsciScintilla {
        background-color: pink;
    }
    '''
    #@+node:ekr.20140916170549.19551: *4* ssm.get_data
    def get_data(self, setting: str) -> list:
        """Return the value of the @data node for the setting."""
        c = self.c
        return c.config.getData(setting, strip_comments=False, strip_data=False) or []
    #@+node:ekr.20140916170549.19552: *4* ssm.get_style_sheet_from_settings
    def get_style_sheet_from_settings(self) -> str:
        """
        Scan for themes or @data qt-gui-plugin-style-sheet nodes.
        Return the text of the relevant node.
        """
        aList1 = self.get_data('qt-gui-plugin-style-sheet')
        aList2 = self.get_data('qt-gui-user-style-sheet')
        if aList2:
            aList1.extend(aList2)
        sheet = ''.join(aList1)
        sheet = self.expand_css_constants(sheet)
        return sheet
    #@+node:ekr.20140915194122.19476: *4* ssm.print_style_sheet
    def print_style_sheet(self) -> None:
        """Show the top-level style sheet."""
        w = self.get_master_widget()
        sheet = w.styleSheet()
        print(f"style sheet for: {w}...\n\n{sheet}")
    #@+node:ekr.20110605121601.18175: *4* ssm.set_style_sheets
    def set_style_sheets(self, all: bool = True, top: Widget = None, w: Widget = None) -> None:
        """Set the master style sheet for all widgets using config settings."""
        c = self.c
        if top is None:
            top = c.frame.top
        selectors = ['qt-gui-plugin-style-sheet']
        if all:
            selectors.append('qt-gui-user-style-sheet')
        sheets = []
        for name in selectors:
            # don't strip `#selector_name { ...` type syntax
            sheet = c.config.getData(name, strip_comments=False)
            if sheet:
                if '\n' in sheet[0]:
                    sheet = ''.join(sheet)
                else:
                    sheet = '\n'.join(sheet)
            if sheet and sheet.strip():
                line0 = f"\n/* ===== From {name} ===== */\n\n"
                sheet = line0 + sheet
                sheets.append(sheet)
        if sheets:
            sheet = "\n".join(sheets)
            # store *before* expanding, so later expansions get new zoom
            c.active_stylesheet = sheet
            sheet = self.expand_css_constants(sheet)
            if not sheet:
                sheet = self.default_style_sheet()
            if w is None:
                w = self.get_master_widget(top)
            w.setStyleSheet(sheet)
    #@+node:ekr.20180316091943.1: *3* ssm.Stylesheet
    # Computations on stylesheets themselves.
    #@+node:ekr.20140915062551.19510: *4* ssm.expand_css_constants & helpers
    css_warning_given = False  # For do_pass.

    def expand_css_constants(self, sheet: str, settingsDict: g.SettingsDict = None) -> str:
        """Expand @ settings into their corresponding constants."""
        c = self.c
        trace = 'zoom' in g.app.debug
        if settingsDict is None:
            settingsDict = c.config.settingsDict  # A g.SettingsDict.
        constants, deltas = self.adjust_sizes(settingsDict)
        if trace:
            print('')
            g.trace(f"zoom constants: {constants}")
            g.printObj(deltas, tag='zoom deltas')  # A defaultdict
        sheet = self.replace_indicator_constants(sheet)
        for pass_n in range(10):
            to_do = self.find_constants_referenced(sheet)
            if not to_do:
                break
            old_sheet = sheet
            sheet = self.do_pass(constants, deltas, settingsDict, sheet, to_do)
            if sheet == old_sheet:
                break
        else:
            g.trace('Too many iterations')
        if to_do:
            g.trace('Unresolved @constants')
            g.printObj(to_do)
        sheet = self.resolve_urls(sheet)
        sheet = sheet.replace('\\\n', '')  # join lines ending in \
        return sheet
    #@+node:ekr.20150617085045.1: *5* ssm.adjust_sizes
    def adjust_sizes(self, settingsDict: dict) -> tuple[dict, Any]:
        """Adjust constants to reflect c._style_deltas."""
        c = self.c
        constants = {}
        deltas = c._style_deltas
        for delta in c._style_deltas:
            # adjust @font-size-body by font_size_delta
            # easily extendable to @font-size-*
            val = c.config.getString(delta)
            passes = 10
            while passes and val and val.startswith('@'):
                key = g.app.config.canonicalizeSettingName(val[1:])
                val = settingsDict.get(key)
                if val:
                    val = val.val
                passes -= 1
            if deltas[delta] and (val is not None):
                size = ''.join(i for i in val if i in '01234567890.')
                units = ''.join(i for i in val if i not in '01234567890.')
                size = max(1, float(size) + deltas[delta])
                constants['@' + delta] = f"{size}{units}"
        return constants, deltas
    #@+node:ekr.20180316093159.1: *5* ssm.do_pass
    def do_pass(self,
        constants: dict,
        deltas: list[str],
        settingsDict: dict[str, Any],
        sheet: str,
        to_do: list[str],
    ) -> str:

        to_do.sort(key=len, reverse=True)
        for const in to_do:
            value = None
            if const in constants:
                # This constant is about to be removed.
                value = constants[const]
                if const[1:] not in deltas and not self.css_warning_given:
                    self.css_warning_given = True
                    g.es_print(f"'{const}' from style-sheet comment definition, ")
                    g.es_print("please use regular @string / @color type @settings.")
            else:
                # lowercase, without '@','-','_', etc.
                key = g.app.config.canonicalizeSettingName(const[1:])
                value = settingsDict.get(key)
                if value is not None:
                    # New in Leo 5.5: Do NOT add comments here.
                    # They RUIN style sheets if they appear in a nested comment!
                        # value = '%s /* %s */' % (value.val, key)
                    value = value.val
                elif key in self.color_db:
                    # New in Leo 5.5: Do NOT add comments here.
                    # They RUIN style sheets if they appear in a nested comment!
                    value = self.color_db.get(key)
            if value:
                # Partial fix for #780.
                try:
                    # Don't replace shorter constants occurring in larger.
                    sheet = re.sub(
                        const + "(?![-A-Za-z0-9_])",
                        value,
                        sheet,
                    )
                except Exception:
                    g.es_print('Exception handling style sheet')
                    g.es_print(sheet)
                    g.es_exception()
            else:
                pass
                # tricky, might be an undefined identifier, but it might
                # also be a @foo in a /* comment */, where it's harmless.
                # So rely on whoever calls .setStyleSheet() to do the right thing.
        return sheet
    #@+node:tbrown.20131120093739.27085: *5* ssm.find_constants_referenced
    def find_constants_referenced(self, text: str) -> list[str]:
        """find_constants - Return a list of constants referenced in the supplied text,
        constants match::

            @[A-Za-z_][-A-Za-z0-9_]*
            i.e. @foo_1-5

        :Parameters:
        - `text`: text to search
        """
        aList = sorted(set(re.findall(r"@[A-Za-z_][-A-Za-z0-9_]*", text)))
        # Exempt references to Leo constructs.
        for s in ('@button', '@constants', '@data', '@language'):
            if s in aList:
                aList.remove(s)
        return aList
    #@+node:ekr.20150617090104.1: *5* ssm.replace_indicator_constants
    def replace_indicator_constants(self, sheet: str) -> str:
        """
        In the stylesheet, replace (if they exist)::

            image: @tree-image-closed
            image: @tree-image-open

        by::

            url(path/closed.png)
            url(path/open.png)

        path can be relative to ~ or to leo/Icons.

        Assuming that ~/myIcons/closed.png exists, either of these will work::

            @string tree-image-closed = nodes-dark/triangles/closed.png
            @string tree-image-closed = myIcons/closed.png

        Return the updated stylesheet.
        """
        close_path = self.find_icon_path('tree-image-closed')
        open_path = self.find_icon_path('tree-image-open')
        # Make all substitutions in the stylesheet.
        table = (
            (open_path, re.compile(r'\bimage:\s*@tree-image-open', re.IGNORECASE)),
            (close_path, re.compile(r'\bimage:\s*@tree-image-closed', re.IGNORECASE)),
            # (open_path,  re.compile(r'\bimage:\s*at-tree-image-open', re.IGNORECASE)),
            # (close_path, re.compile(r'\bimage:\s*at-tree-image-closed', re.IGNORECASE)),
        )
        for path, pattern in table:
            for mo in pattern.finditer(sheet):
                old = mo.group(0)
                new = f"image: url({path})"
                sheet = sheet.replace(old, new)
        return sheet
    #@+node:ekr.20180320054305.1: *5* ssm.resolve_urls
    def resolve_urls(self, sheet: str) -> str:
        """Resolve all relative url's so they use absolute paths."""
        trace = 'themes' in g.app.debug
        pattern = re.compile(r'url\((.*)\)')
        join = g.finalize_join
        directories = self.compute_icon_directories()
        paths_traced = False
        if trace:
            paths_traced = True
            g.trace('Search paths...')
            g.printObj(directories)
        # Pass 1: Find all replacements without changing the sheet.
        replacements = []
        for mo in pattern.finditer(sheet):
            url = mo.group(1)
            if url.startswith(':/'):
                url = url[2:]
            elif g.os_path_isabs(url):
                if trace:
                    g.trace('ABS:', url)
                continue
            for directory in directories:
                path = join(directory, url)
                if g.os_path_exists(path):
                    if trace:
                        g.trace(f"{url:35} ==> {path}")
                    old = mo.group(0)
                    new = f"url({path})"
                    replacements.append((old, new),)
                    break
            else:
                g.trace(f"{url:35} ==> NOT FOUND")
                if not paths_traced:
                    paths_traced = True
                    g.trace('Search paths...')
                    g.printObj(directories)
        # Pass 2: Now we can safely make the replacements.
        for old, new in reversed(replacements):
            sheet = sheet.replace(old, new)
        return sheet
    #@+node:ekr.20140912110338.19372: *4* ssm.munge
    def munge(self, stylesheet: str) -> str:
        """
        Return the stylesheet without extra whitespace.

        To avoid false mismatches, this should approximate what Qt does.
        To avoid false matches, this should not munge too much.
        """
        s = ''.join([s.lstrip().replace('  ', ' ').replace(' \n', '\n')
            for s in g.splitLines(stylesheet)])
        return s.rstrip()  # Don't care about ending newline.
    #@+node:tom.20220310224019.1: *4* ssm.rescale_sizes
    def rescale_sizes(self, sheet: str, factor: float) -> str:
        """
        #@+<< docstring >>
        #@+node:tom.20220310224918.1: *5* << docstring >>
        Rescale all pt or px sizes in CSS stylesheet or Leo theme.

        Sheets can have either "logical" or "actual" sizes.
        "Logical" sizes are ones like "@font-family-base = 10.6pt".
        "Actual" sizes are the ones in the "qt-gui-plugin-style-sheet" subtree.
        They look like "font-size: 11pt;"

        In Qt stylesheets, only sizes in pt or px are honored, so
        those are the only ones changed by this method.  Padding,
        margin, etc. sizes will be changed as well as font sizes.

        Sizes do not have to be integers (e.g., 10.5 pt).  Qt honors
        non-integer point sizes, with at least a 0.5pt granularity.
        It's currently unknown how non-integer px sizes are handled.

        No size will be scaled down to less than 1.

        ARGUMENTS
        sheet -- a CSS stylesheet or a Leo theme as a string.  The Leo
                 theme file should be read as a string before being passed
                 to this method.  If a Leo theme, the output will be a
                 well-formed Leo outline.

        scale -- the scaling factor as a float or integer.  For example,
                 a scale of 1.5 will increase all the sizes by a factor of 1.5.

        RETURNS
        the modified sheet as a string.

        #@-<< docstring >>
        """
        RE = r'([=:])[ ]*([.1234567890]+)(p[tx])'

        def scale(matchobj: Any, scale: float = factor) -> str:
            prefix = matchobj.group(1)
            sz = matchobj.group(2)
            units = matchobj.group(3)
            try:
                scaled = max(float(sz) * factor, 1)
            except Exception as e:
                g.es('ssm.rescale_fonts:', e)
                return None
            return f'{prefix} {scaled:.1f}{units}'

        newsheet = re.sub(RE, scale, sheet)
        return newsheet
    #@+node:ekr.20180316092116.1: *3* ssm.Widgets
    #@+node:ekr.20140913054442.19390: *4* ssm.get_master_widget
    def get_master_widget(self, top: Widget = None) -> Widget:
        """
        Carefully return the master widget.
        c.frame.top is a DynamicWindow.
        """
        if top is None:
            top = self.c.frame.top
        master = top.leo_master or top
        return master
    #@+node:ekr.20140913054442.19391: *4* ssm.set selected_style_sheet
    def set_selected_style_sheet(self) -> None:
        """For manual testing: update the stylesheet using c.p.b."""
        if not g.unitTesting:
            c = self.c
            sheet = c.p.b
            sheet = self.expand_css_constants(sheet)
            w = self.get_master_widget(c.frame.top)
            w.setStyleSheet(sheet)
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo

#@+leo-ver=5-thin
#@+node:ekr.20140907085654.18699: * @file ../plugins/qt_gui.py
'''This file contains the gui wrapper for Qt: g.app.gui.'''
#@+<< imports >>
#@+node:ekr.20140918102920.17891: ** << imports >> (qt_gui.py)
import leo.core.leoColor as leoColor
import leo.core.leoGlobals as g
import leo.core.leoGui as leoGui
from leo.core.leoQt import isQt5, Qsci, QString, QtCore, QtGui, QtWidgets
    # This import causes pylint to fail on this file and on leoBridge.py.
    # The failure is in astroid: raw_building.py.
import leo.plugins.qt_events as qt_events
import leo.plugins.qt_frame as qt_frame
import leo.plugins.qt_idle_time as qt_idle_time
import leo.plugins.qt_text as qt_text
import datetime
import os
import re
import sys
if 1:
    # This defines the commands defined by @g.command.
    # pylint: disable=unused-import
    import leo.plugins.qt_commands as qt_commands
    assert qt_commands
#@-<< imports >>
#@+others
#@+node:ekr.20110605121601.18134: ** init
def init():
    trace = (False or g.trace_startup) and not g.unitTesting
    if trace and g.trace_startup: g.es_debug('(gt_gui.py)')
    if g.app.unitTesting: # Not Ok for unit testing!
        return False
    if not QtCore:
        return False
    if g.app.gui:
        return g.app.gui.guiName() == 'qt'
    else:
        g.app.gui = LeoQtGui()
        g.app.gui.finishCreate()
        g.plugin_signon(__name__)
        return True
#@+node:ekr.20140907085654.18700: ** class LeoQtGui(leoGui.LeoGui)
class LeoQtGui(leoGui.LeoGui):
    '''A class implementing Leo's Qt gui.'''
    #@+others
    #@+node:ekr.20110605121601.18477: *3*  qt_gui.__init__ & reloadSettings
    def __init__(self):
        '''Ctor for LeoQtGui class.'''
        # g.trace('(LeoQtGui)',g.callers())
        leoGui.LeoGui.__init__(self, 'qt')
             # Initialize the base class.
        self.active = True
        self.consoleOnly = False # Console is separate from the log.
        self.iconimages = {}
        self.idleTimeClass = qt_idle_time.IdleTime
        self.insert_char_flag = False # A flag for eventFilter.
        self.mGuiName = 'qt'
        self.plainTextWidget = qt_text.PlainTextWrapper
        self.styleSheetManagerClass = StyleSheetManager
            # For c.idle_focus_helper and activate/deactivate events.
        # Create objects...
        self.qtApp = QtWidgets.QApplication(sys.argv)
        self.reloadSettings()
        self.appIcon = self.getIconImage('leoapp32.png')
        # Put up the splash screen()
        if (g.app.use_splash_screen and
            not g.app.batchMode and
            not g.app.silentMode and
            not g.unitTesting
        ):
            self.splashScreen = self.createSplashScreen()
        if g.app.qt_use_tabs:
            self.frameFactory = qt_frame.TabbedFrameFactory()
        else:
            self.frameFactory = qt_frame.SDIFrameFactory()
        
    def reloadSettings(self):
        self.color_theme = g.app.config and g.app.config.getString('color_theme')
    #@+node:ekr.20110605121601.18484: *3*  qt_gui.destroySelf (calls qtApp.quit)
    def destroySelf(self):
        trace = g.app.trace_shutdown
        QtCore.pyqtRemoveInputHook()
        if trace: g.pr('LeoQtGui.destroySelf: calling qtApp.Quit')
        self.qtApp.quit()
    #@+node:ekr.20110605121601.18485: *3* qt_gui.Clipboard


    #@+node:ekr.20160917125946.1: *4* qt_gui.replaceClipboardWith
    def replaceClipboardWith(self, s):
        '''Replace the clipboard with the string s.'''
        trace = False and not g.unitTesting
        cb = self.qtApp.clipboard()
        if cb:
            # cb.clear()  # unnecessary, breaks on some Qt versions
            s = g.toUnicode(s)
            QtWidgets.QApplication.processEvents()
            # Fix #241: QMimeData object error
            cb.setText(QString(s))
            QtWidgets.QApplication.processEvents()
            if trace: g.trace(len(s), type(s), s[: 25])
        else:
            g.trace('no clipboard!')
    #@+node:ekr.20160917125948.1: *4* qt_gui.getTextFromClipboard
    def getTextFromClipboard(self):
        '''Get a unicode string from the clipboard.'''
        trace = False and not g.unitTesting
        cb = self.qtApp.clipboard()
        if cb:
            QtWidgets.QApplication.processEvents()
            s = cb.text()
            if trace: g.trace(len(s), type(s), s[: 25])
            # Fix bug 147: Python 3 clipboard encoding
            s = g.u(s)
                # Don't call g.toUnicode here!
                # s is a QString, which isn't exactly a unicode string!
            return s
        else:
            g.trace('no clipboard!')
            return ''
    #@+node:ekr.20160917130023.1: *4* qt_gui.setClipboardSelection
    def setClipboardSelection(self, s):
        '''
        Set the clipboard selection to s.
        There are problems with PyQt5.
        '''
        if isQt5:
            # Alas, returning reopens bug 218: https://github.com/leo-editor/leo-editor/issues/218
            return
        if s:
            # This code generates a harmless, but annoying warning on PyQt5.
            cb = self.qtApp.clipboard()
            cb.setText(QString(s), mode=cb.Selection)
    #@+node:ekr.20110605121601.18487: *3* qt_gui.Dialogs & panels
    #@+node:ekr.20110605121601.18488: *4* qt_gui.alert
    def alert(self, c, message):
        if g.unitTesting: return
        b = QtWidgets.QMessageBox
        d = b(None)
        d.setWindowTitle('Alert')
        d.setText(message)
        d.setIcon(b.Warning)
        d.addButton('Ok', b.YesRole)
        c.in_qt_dialog = True
        d.exec_()
        c.in_qt_dialog = False
    #@+node:ekr.20110605121601.18489: *4* qt_gui.makeFilter
    def makeFilter(self, filetypes):
        '''Return the Qt-style dialog filter from filetypes list.'''
        filters = ['%s (%s)' % (z) for z in filetypes]
        return ';;'.join(filters)
    #@+node:ekr.20150615211522.1: *4* qt_gui.openFindDialog & helpers
    def openFindDialog(self, c):
        if g.unitTesting:
            return
        d = self.globalFindDialog
        if not d:
            d = self.createFindDialog(c)
            self.globalFindDialog = d
            # Fix #516: Do the following only once...
            d.setStyleSheet(c.active_stylesheet)
            # Set the commander's FindTabManager.
            assert g.app.globalFindTabManager
            c.ftm = g.app.globalFindTabManager
            fn = c.shortFileName() or 'Untitled'
            d.setWindowTitle('Find in %s' % fn)
            c.frame.top.find_status_edit.setText('')
        c.inCommand = False
        if d.isVisible():
            # The order is important, and tricky.
            d.focusWidget()
            d.show()
            d.raise_()
            d.activateWindow()
        else:
            d.show()
            d.exec_()
    #@+node:ekr.20150619053138.1: *5* qt_gui.createFindDialog
    def createFindDialog(self, c):
        '''Create and init a non-modal Find dialog.'''
        g.app.globalFindTabManager = c.findCommands.ftm
        top = c.frame.top
            # top is the DynamicWindow class.
        w = top.findTab
        top.find_status_label.setText('Find Status:')

        d = QtWidgets.QDialog()
        # Fix #516: Hide the dialog. Never delete it.

        def closeEvent(event, d=d):
            event.ignore()
            d.hide()

        d.closeEvent = closeEvent
        layout = QtWidgets.QVBoxLayout(d)
        layout.addWidget(w)
        self.attachLeoIcon(d)
        d.setLayout(layout)
        c.styleSheetManager.set_style_sheets(w=d)
        g.app.gui.setFilter(c, d, d, 'find-dialog')
            # This makes most standard bindings available.
        d.setModal(False)
        return d
    #@+node:ekr.20150619053840.1: *5* qt_gui.findDialogSelectCommander
    def findDialogSelectCommander(self, c):
        '''Update the Find Dialog when c changes.'''
        if self.globalFindDialog:
            c.ftm = g.app.globalFindTabManager
            d = self.globalFindDialog
            fn = c.shortFileName() or 'Untitled'
            d.setWindowTitle('Find in %s' % fn)
            c.inCommand = False
    #@+node:ekr.20150619131141.1: *5* qt_gui.hideFindDialog
    def hideFindDialog(self):
        d = self.globalFindDialog
        if d:
            d.hide()
    #@+node:ekr.20110605121601.18492: *4* qt_gui.panels
    def createComparePanel(self, c):
        """Create a qt color picker panel."""
        return None # This window is optional.

    def createFindTab(self, c, parentFrame):
        """Create a qt find tab in the indicated frame."""
        pass # Now done in dw.createFindTab.

    def createLeoFrame(self, c, title):
        """Create a new Leo frame."""
        gui = self
        return qt_frame.LeoQtFrame(c, title, gui)

    def createSpellTab(self, c, spellHandler, tabName):
        return qt_frame.LeoQtSpellTab(c, spellHandler, tabName)
    #@+node:ekr.20110605121601.18493: *4* qt_gui.runAboutLeoDialog
    def runAboutLeoDialog(self, c, version, theCopyright, url, email):
        """Create and run a qt About Leo dialog."""
        if g.unitTesting: return None
        b = QtWidgets.QMessageBox
        d = b(c.frame.top)
        d.setText('%s\n%s\n%s\n%s' % (
            version, theCopyright, url, email))
        d.setIcon(b.Information)
        yes = d.addButton('Ok', b.YesRole)
        d.setDefaultButton(yes)
        c.in_qt_dialog = True
        d.exec_()
        c.in_qt_dialog = False
    #@+node:ekr.20110605121601.18496: *4* qt_gui.runAskDateTimeDialog
    def runAskDateTimeDialog(self, c, title,
        message='Select Date/Time',
        init=None,
        step_min=None
    ):
        """Create and run a qt date/time selection dialog.

        init - a datetime, default now
        step_min - a dict, keys are QtWidgets.QDateTimeEdit Sections, like
          QtWidgets.QDateTimeEdit.MinuteSection, and values are integers,
          the minimum amount that section of the date/time changes
          when you roll the mouse wheel.

        E.g. (5 minute increments in minute field):

            print g.app.gui.runAskDateTimeDialog(c, 'When?',
              message="When is it?",
              step_min={QtWidgets.QDateTimeEdit.MinuteSection: 5})

        """

        class DateTimeEditStepped(QtWidgets.QDateTimeEdit):
            """QDateTimeEdit which allows you to set minimum steps on fields, e.g.
              DateTimeEditStepped(parent, {QtWidgets.QDateTimeEdit.MinuteSection: 5})
            for a minimum 5 minute increment on the minute field.
            """

            def __init__(self, parent=None, init=None, step_min=None):
                if step_min is None: step_min = {}
                self.step_min = step_min
                if init:
                    QtWidgets.QDateTimeEdit.__init__(self, init, parent)
                else:
                    QtWidgets.QDateTimeEdit.__init__(self, parent)

            def stepBy(self, step):
                cs = self.currentSection()
                if cs in self.step_min and abs(step) < self.step_min[cs]:
                    step = self.step_min[cs] if step > 0 else - self.step_min[cs]
                QtWidgets.QDateTimeEdit.stepBy(self, step)

        class Calendar(QtWidgets.QDialog):

            def __init__(self,
                parent=None,
                message='Select Date/Time',
                init=None,
                step_min=None
            ):
                if step_min is None: step_min = {}
                QtWidgets.QDialog.__init__(self, parent)
                layout = QtWidgets.QVBoxLayout()
                self.setLayout(layout)
                layout.addWidget(QtWidgets.QLabel(message))
                self.dt = DateTimeEditStepped(init=init, step_min=step_min)
                self.dt.setCalendarPopup(True)
                layout.addWidget(self.dt)
                buttonBox = QtWidgets.QDialogButtonBox(
                    QtWidgets.QDialogButtonBox.Ok |
                    QtWidgets.QDialogButtonBox.Cancel)
                layout.addWidget(buttonBox)
                buttonBox.accepted.connect(self.accept)
                buttonBox.rejected.connect(self.reject)

        if g.unitTesting: return None
        if step_min is None: step_min = {}
        b = Calendar
        if not init:
            init = datetime.datetime.now()
        d = b(c.frame.top, message=message, init=init, step_min=step_min)
        d.setStyleSheet(c.active_stylesheet)
        d.setWindowTitle(title)
        c.in_qt_dialog = True
        val = d.exec_()
        c.in_qt_dialog = False
        if val != d.Accepted:
            return None
        else:
            return d.dt.dateTime().toPyDateTime()
    #@+node:ekr.20110605121601.18494: *4* qt_gui.runAskLeoIDDialog
    def runAskLeoIDDialog(self):
        """Create and run a dialog to get g.app.LeoID."""
        if g.unitTesting: return None
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
        return g.u(s)
    #@+node:ekr.20110605121601.18491: *4* qt_gui.runAskOkCancelNumberDialog
    def runAskOkCancelNumberDialog(self, c, title, message, cancelButtonText=None, okButtonText=None):
        """Create and run askOkCancelNumber dialog ."""
        if g.unitTesting: return None
        # n,ok = QtWidgets.QInputDialog.getDouble(None,title,message)
        d = QtWidgets.QInputDialog()
        d.setStyleSheet(c.active_stylesheet)
        d.setWindowTitle(title)
        d.setLabelText(message)
        if cancelButtonText:
            d.setCancelButtonText(cancelButtonText)
        if okButtonText:
            d.setOkButtonText(okButtonText)
        self.attachLeoIcon(d)
        ok = d.exec_()
        n = d.textValue()
        try:
            n = float(n)
        except ValueError:
            n = None
        return n if ok else None
    #@+node:ekr.20110605121601.18490: *4* qt_gui.runAskOkCancelStringDialog
    def runAskOkCancelStringDialog(self, c, title, message, cancelButtonText=None,
                                   okButtonText=None, default="", wide=False):
        """Create and run askOkCancelString dialog.

        wide - edit a long string
        """
        if g.unitTesting: return None
        d = QtWidgets.QInputDialog()
        d.setStyleSheet(c.active_stylesheet)
        d.setWindowTitle(title)
        d.setLabelText(message)
        d.setTextValue(default)
        if wide:
            d.resize(int(g.windows()[0].get_window_info()[0] * .9), 100)
        if cancelButtonText:
            d.setCancelButtonText(cancelButtonText)
        if okButtonText:
            d.setOkButtonText(okButtonText)
        self.attachLeoIcon(d)
        ok = d.exec_()
        return str(d.textValue()) if ok else None
    #@+node:ekr.20110605121601.18495: *4* qt_gui.runAskOkDialog
    def runAskOkDialog(self, c, title, message=None, text="Ok"):
        """Create and run a qt askOK dialog ."""
        if g.unitTesting: return None
        b = QtWidgets.QMessageBox
        d = b(c.frame.top)
        d.setStyleSheet(c.active_stylesheet)
        d.setWindowTitle(title)
        if message: d.setText(message)
        d.setIcon(b.Information)
        d.addButton(text, b.YesRole)
        c.in_qt_dialog = True
        d.exec_()
        c.in_qt_dialog = False
    #@+node:ekr.20110605121601.18497: *4* qt_gui.runAskYesNoCancelDialog
    def runAskYesNoCancelDialog(self, c, title,
        message=None,
        yesMessage="&Yes",
        noMessage="&No",
        yesToAllMessage=None,
        defaultButton="Yes",
        cancelMessage=None,
    ):
        """Create and run an askYesNo dialog."""
        if g.unitTesting:
            return None
        b = QtWidgets.QMessageBox
        d = b(c.frame.top)
        d.setStyleSheet(c.active_stylesheet)
        if message: d.setText(message)
        d.setIcon(b.Warning)
        d.setWindowTitle(title)
        yes = d.addButton(yesMessage, b.YesRole)
        no = d.addButton(noMessage, b.NoRole)
        yesToAll = d.addButton(yesToAllMessage, b.YesRole) if yesToAllMessage else None
        if cancelMessage:
            cancel = d.addButton(cancelMessage, b.RejectRole)
        else:
            cancel = d.addButton(b.Cancel)
        if defaultButton == "Yes": d.setDefaultButton(yes)
        elif defaultButton == "No": d.setDefaultButton(no)
        else: d.setDefaultButton(cancel)
        c.in_qt_dialog = True
        val = d.exec_()
        c.in_qt_dialog = False
        if val == 0: val = 'yes'
        elif val == 1: val = 'no'
        elif yesToAll and val == 2: val = 'yes-to-all'
        else: val = 'cancel'
        return val
    #@+node:ekr.20110605121601.18498: *4* qt_gui.runAskYesNoDialog
    def runAskYesNoDialog(self, c, title, message=None, yes_all=False, no_all=False):
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
        if g.unitTesting: return None
        b = QtWidgets.QMessageBox
        buttons = b.Yes | b.No
        if yes_all:
            buttons |= b.YesToAll
        if no_all:
            buttons |= b.NoToAll
        d = b(c.frame.top)
        d.setStyleSheet(c.active_stylesheet)
        d.setStandardButtons(buttons)
        d.setWindowTitle(title)
        if message: d.setText(message)
        d.setIcon(b.Information)
        d.setDefaultButton(b.Yes)
        c.in_qt_dialog = True
        val = d.exec_()
        c.in_qt_dialog = False
        return {
            b.Yes: 'yes',
            b.No: 'no',
            b.YesToAll: 'yes-all',
            b.NoToAll: 'no-all'
        }.get(val, 'no')
    #@+node:ekr.20110605121601.18499: *4* qt_gui.runOpenDirectoryDialog
    def runOpenDirectoryDialog(self, title, startdir):
        """Create and run an Qt open directory dialog ."""
        parent = None
        d = QtWidgets.QFileDialog()
        self.attachLeoIcon(d)
        s = d.getExistingDirectory(parent, title, startdir)
        return g.u(s)
    #@+node:ekr.20110605121601.18500: *4* qt_gui.runOpenFileDialog
    def runOpenFileDialog(self, c, title, filetypes, defaultextension='', multiple=False, startpath=None):
        """Create and run an Qt open file dialog ."""
        trace = False and not g.unitTesting
        if g.unitTesting:
            return ''
        if startpath is None:
            startpath = os.curdir
        parent = None
        filter_ = self.makeFilter(filetypes)
        dialog = QtWidgets.QFileDialog()
        dialog.setStyleSheet(c.active_stylesheet)
        self.attachLeoIcon(dialog)
        if multiple:
            c.in_qt_dialog = True
            lst = dialog.getOpenFileNames(parent, title, startpath, filter_)
            c.in_qt_dialog = False
            if isQt5: # this is a *Py*Qt change rather than a Qt change
                lst, selected_filter = lst
            files = [g.u(s) for s in lst]
            if files:
                c.last_dir = g.os_path_dirname(files[-1])
                if trace: g.trace('c.last_dir', c.last_dir)
            return files
        else:
            c.in_qt_dialog = True
            s = dialog.getOpenFileName(
                parent,
                title,
                # startpath,
                g.init_dialog_folder(c, c.p, use_at_path=True),
                filter_)
            c.in_qt_dialog = False
            if isQt5:
                s, selected_filter = s
            s = g.u(s)
            if s:
                c.last_dir = g.os_path_dirname(s)
                if trace: g.trace('c.last_dir', c.last_dir)
            return s
    #@+node:ekr.20110605121601.18501: *4* qt_gui.runPropertiesDialog
    def runPropertiesDialog(self,
        title='Properties',
        data=None,
        callback=None,
        buttons=None
    ):
        """Dispay a modal TkPropertiesDialog"""
        if data is None: data = {}
        g.warning('Properties menu not supported for Qt gui')
        result = 'Cancel'
        return result, data
    #@+node:ekr.20110605121601.18502: *4* qt_gui.runSaveFileDialog
    def runSaveFileDialog(self, c, initialfile='', title='Save', filetypes=None, defaultextension=''):
        """Create and run an Qt save file dialog ."""
        trace = False and not g.unitTesting
        if filetypes is None:
            filetypes = []
        if g.unitTesting:
            return ''
        else:
            parent = None
            filter_ = self.makeFilter(filetypes)
            d = QtWidgets.QFileDialog()
            d.setStyleSheet(c.active_stylesheet)
            self.attachLeoIcon(d)
            c.in_qt_dialog = True
            obj = d.getSaveFileName(
                parent,
                title,
                # os.curdir,
                g.init_dialog_folder(c, c.p, use_at_path=True),
                filter_)
            c.in_qt_dialog = False
            # Very bizarre: PyQt5 version can return a tuple!
            s = obj[0] if isinstance(obj, (list, tuple)) else obj
            s = g.u(s or '')
            if s:
                c.last_dir = g.os_path_dirname(s)
                if trace: g.trace('c.last_dir', c.last_dir)
            return s
    #@+node:ekr.20110605121601.18503: *4* qt_gui.runScrolledMessageDialog
    def runScrolledMessageDialog(self,
        short_title='',
        title='Message',
        label='',
        msg='',
        c=None, **keys
    ):
        # pylint: disable=dangerous-default-value
        # How are we supposed to avoid **keys?
        if g.unitTesting: return None

        def send(title=title, label=label, msg=msg, c=c, keys=keys):
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
            if retval: return retval
            #@+<< load viewrendered plugin >>
            #@+node:ekr.20110605121601.18505: *5* << load viewrendered plugin >>
            pc = g.app.pluginsController
            # 2011/10/20: load viewrendered (and call vr.onCreate)
            # *only* if not already loaded.
            if not pc.isLoaded('viewrendered.py') and not pc.isLoaded('viewrendered2.py'):
                vr = pc.loadOnePlugin('viewrendered.py')
                if vr:
                    g.blue('viewrendered plugin loaded.')
                    vr.onCreate('tag', {'c': c})
            #@-<< load viewrendered plugin >>
            retval = send()
            if retval: return retval
            #@+<< no dialog error >>
            #@+node:ekr.20110605121601.18506: *5* << no dialog error >>
            g.es_print_error(
                'No handler for the "scrolledMessage" hook.\n\t%s' % (
                    g.callers()))
            #@-<< no dialog error >>
        #@+<< emergency fallback >>
        #@+node:ekr.20110605121601.18507: *5* << emergency fallback >>
        b = QtWidgets.QMessageBox
        d = b(None) # c.frame.top)
        d.setWindowFlags(QtCore.Qt.Dialog)
            # That is, not a fixed size dialog.
        d.setWindowTitle(title)
        if msg: d.setText(msg)
        d.setIcon(b.Information)
        d.addButton('Ok', b.YesRole)
        c.in_qt_dialog = True
        d.exec_()
        c.in_qt_dialog = False
        #@-<< emergency fallback >>
    #@+node:ekr.20110607182447.16456: *3* qt_gui.Event handlers
    #@+node:ekr.20110605121601.18481: *4* qt_gui.onDeactiveEvent
    # deactivated_name = ''
    deactivated_widget = None

    def onDeactivateEvent(self, event, c, obj, tag):
        '''
        Gracefully deactivate the Leo window.
        Called several times for each window activation.
        '''
        trace = (False or g.app.trace_focus) and not g.unitTesting
        w = self.get_focus()
        w_name = w and w.objectName()
        if trace: g.trace(repr(w_name))
        self.active = False
            # Used only by c.idle_focus_helper.
        if 1: # Leo 5.6: Recover from missing focus.
            # Careful: never save headline widgets.
            if w_name == 'headline':
                self.deactivated_widget = c.frame.tree.treeWidget
            else:
                self.deactivated_widget = w if w_name else None
        if 0: # Cause problems elsewhere.
            trace = False and not g.unitTesting
            if c.exists and not self.deactivated_name:
                self.deactivated_name = self.widget_name(self.get_focus())
                self.active = False
                if trace: g.trace(self.deactivated_name)
                c.k.keyboardQuit(setFocus=False)
                    # The best way to retain as much focus as possible.
        g.doHook('deactivate', c=c, p=c.p, v=c.p, event=event)
    #@+node:ekr.20110605121601.18480: *4* LeoQtGui.onActivateEvent
    # Called from eventFilter

    def onActivateEvent(self, event, c, obj, tag):
        '''
        Restore the focus when the Leo window is activated.
        Called several times for each window activation.
        '''
        trace = (False or g.app.trace_focus) and not g.unitTesting
        w = self.get_focus() or self.deactivated_widget
        self.deactivated_widget = None
        w_name = w and w.objectName()
        # if trace: g.trace(repr(w_name))
        # Fix #270: Vim keys don't always work after double Alt+Tab.
        # Fix #359: Leo hangs in LeoQtEventFilter.eventFilter
        if c.exists and c.vimCommands and not self.active and not g.app.killed:
            c.vimCommands.on_activate()
        self.active = True
            # Used only by c.idle_focus_helper.
        if 1:
            # Leo 5.6: Recover from missing focus.
            # c.idle_focus_handler can't do this.
            if w and w_name in ('log-widget', 'richTextEdit', 'treeWidget'):
                # Restore focus **only** to body or tree
                if trace: g.trace('==>', w_name)
                c.widgetWantsFocusNow(w)
            else:
                if trace: g.trace(repr(w_name), '==> BODY')
                c.bodyWantsFocusNow()
        if 0: # Cause problems elsewhere.
            trace = False and not g.unitTesting
            if c.exists and self.deactivated_name:
                self.active = True
                w_name = self.deactivated_name
                self.deactivated_name = None
                if trace: g.trace(w_name)
                if c.p.v:
                    c.p.v.restoreCursorAndScroll()
                if w_name.startswith('tree') or w_name.startswith('head'):
                    c.treeWantsFocusNow()
                else:
                    c.bodyWantsFocusNow()
        g.doHook('activate', c=c, p=c.p, v=c.p, event=event)
    #@+node:ekr.20130921043420.21175: *4* qt_gui.setFilter
    # w's type is in (DynamicWindow,QMinibufferWrapper,LeoQtLog,LeoQtTree,
    # QTextEditWrapper,LeoQTextBrowser,LeoQuickSearchWidget,cleoQtUI)

    def setFilter(self, c, obj, w, tag):
        '''
        Create an event filter in obj.
        w is a wrapper object, not necessarily a QWidget.
        '''
        # gui = self
        if 0:
            g.trace(isinstance(w, QtWidgets.QWidget),
                hasattr(w, 'getName') and w.getName() or None,
                w.__class__.__name__)
        if 0:
            g.trace('obj: %4s %20s w: %5s %s' % (
                isinstance(obj, QtWidgets.QWidget), obj.__class__.__name__,
                isinstance(w, QtWidgets.QWidget), w.__class__.__name__))
        assert isinstance(obj, QtWidgets.QWidget), obj
        theFilter = qt_events.LeoQtEventFilter(c, w=w, tag=tag)
        obj.installEventFilter(theFilter)
        w.ev_filter = theFilter
            # Set the official ivar in w.
    #@+node:ekr.20110605121601.18508: *3* qt_gui.Focus
    def get_focus(self, c=None, raw=False, at_idle=False):
        """Returns the widget that has focus."""
        # pylint: disable=arguments-differ
        trace = (False or g.app.trace_focus) and not g.unitTesting
        trace_idle = False
        trace = trace and (trace_idle or not at_idle)
        app = QtWidgets.QApplication
        w = app.focusWidget()
        if w and not raw and isinstance(w, qt_text.LeoQTextBrowser):
            has_w = hasattr(w, 'leo_wrapper') and w.leo_wrapper
            if has_w:
                if trace: g.trace(w)
            elif c:
                # Kludge: DynamicWindow creates the body pane
                # with wrapper = None, so return the LeoQtBody.
                w = c.frame.body
        if trace:
            g.trace('(LeoQtGui)', w.__class__.__name__)
            g.trace(g.callers())
        return w

    def set_focus(self, c, w):
        """Put the focus on the widget."""
        # pylint: disable=arguments-differ
        trace = (False or g.app.trace_focus) and not g.unitTesting
        # gui = self
        if w:
            if hasattr(w, 'widget') and w.widget:
                w = w.widget
            if trace:
                g.trace('(LeoQtGui)', w.__class__.__name__)
                g.trace(g.callers())
            w.setFocus()

    def ensure_commander_visible(self, c1):
        """
        Check to see if c.frame is in a tabbed ui, and if so, make sure
        the tab is visible
        """
        # pylint: disable=arguments-differ
        #
        # START: copy from Code-->Startup & external files-->
        # @file runLeo.py -->run & helpers-->doPostPluginsInit & helpers (runLeo.py)
        # For qttabs gui, select the first-loaded tab.
        trace = (False or g.app.trace_focus) and not g.unitTesting
        if trace: g.trace(c1)
        if hasattr(g.app.gui, 'frameFactory'):
            factory = g.app.gui.frameFactory
            if factory and hasattr(factory, 'setTabForCommander'):
                c = c1
                factory.setTabForCommander(c)
                c.bodyWantsFocusNow()
        # END: copy
    #@+node:ekr.20110605121601.18510: *3* qt_gui.getFontFromParams
    size_warnings = []

    def getFontFromParams(self, family, size, slant, weight, defaultSize=12):
        '''Required to handle syntax coloring.'''
        trace = False and not g.unitTesting
        # g.trace(family,size,g.callers())
        if g.isString(size):
            if trace: g.trace(size)
            if size.endswith('pt'):
                size = size[: -2].strip()
            elif size.endswith('px'):
                if size not in self.size_warnings:
                    self.size_warnings.append(size)
                    g.es('px ignored in font setting: %s' % size)
                size = size[: -2].strip()
        try:
            size = int(size)
        except Exception:
            size = 0
        if size < 1: size = defaultSize
        d = {
            'black': QtGui.QFont.Black,
            'bold': QtGui.QFont.Bold,
            'demibold': QtGui.QFont.DemiBold,
            'light': QtGui.QFont.Light,
            'normal': QtGui.QFont.Normal,
        }
        weight_val = d.get(weight.lower(), QtGui.QFont.Normal)
        italic = slant == 'italic'
        if not family:
            family = g.app.config.defaultFontFamily
        if not family:
            family = 'DejaVu Sans Mono'
        try:
            font = QtGui.QFont(family, size, weight_val, italic)
            if sys.platform.startswith('linux'):
                font.setHintingPreference(font.PreferFullHinting)
            # g.es(font,font.hintingPreference())
            if trace: g.trace(family, size, g.callers())
            return font
        except Exception:
            g.es("exception setting font", g.callers(4))
            g.es("", "family,size,slant,weight:", "", family, "", size, "", slant, "", weight)
            # g.es_exception() # This just confuses people.
            return g.app.config.defaultFont
    #@+node:ekr.20110605121601.18511: *3* qt_gui.getFullVersion
    def getFullVersion(self, c=None):
        '''Return the PyQt version (for signon)'''
        try:
            qtLevel = 'version %s' % QtCore.QT_VERSION_STR
        except Exception:
            # g.es_exception()
            qtLevel = '<qtLevel>'
        return 'PyQt %s' % (qtLevel)
    #@+node:ekr.20110605121601.18514: *3* qt_gui.Icons
    #@+node:ekr.20110605121601.18515: *4* qt_gui.attachLeoIcon
    def attachLeoIcon(self, window):
        """Attach a Leo icon to the window."""
        #icon = self.getIconImage('leoApp.ico')
        #window.setWindowIcon(icon)
        window.setWindowIcon(self.appIcon)
        #window.setLeoWindowIcon()
    #@+node:ekr.20110605121601.18516: *4* qt_gui.getIconImage
    def getIconImage(self, name):
        '''Load the icon and return it.'''
        trace = False and not g.unitTesting
        trace_cached = False
        trace_not_found = False
        # Return the image from the cache if possible.
        if name in self.iconimages:
            image = self.iconimages.get(name)
            if trace and trace_cached: # and not name.startswith('box'):
                g.trace('cached', id(image), name, image)
            return image
        try:
            iconsDir = g.os_path_join(g.app.loadDir, "..", "Icons")
            homeIconsDir = g.os_path_join(g.app.homeLeoDir, "Icons")
            for theDir in (homeIconsDir, iconsDir):
                fullname = g.os_path_finalize_join(theDir, name)
                if g.os_path_exists(fullname):
                    if 0: # Not needed: use QTreeWidget.setIconsize.
                        pixmap = QtGui.QPixmap()
                        pixmap.load(fullname)
                        image = QtGui.QIcon(pixmap)
                    else:
                        image = QtGui.QIcon(fullname)
                        if trace: g.trace('found', fullname) # , 'image', image)
                    self.iconimages[name] = image
                    # if trace: g.trace('new', id(image), theDir, name)
                    return image
                elif trace and trace_not_found:
                    g.trace('Directory not found', theDir)
            # No image found.
            if trace: g.trace('Icon not found', name)
            return None
        except Exception:
            g.es_print("exception loading:", fullname)
            g.es_exception()
            return None
    #@+node:ekr.20110605121601.18517: *4* qt_gui.getImageImage
    def getImageImage(self, name):
        '''Load the image in file named `name` and return it.

        If self.color_theme, set from @settings -> @string color_theme is set,

         - look first in $HOME/.leo/themes/<theme_name>/Icons,
         - then in .../leo/themes/<theme_name>/Icons,
         - then in .../leo/Icons,
         - as well as trying absolute path
        '''
        fullname = self.getImageImageFinder(name)
        try:
            pixmap = QtGui.QPixmap()
            pixmap.load(fullname)
            return pixmap
        except Exception:
            g.es("exception loading:", name)
            g.es_exception()
            return None
    #@+node:tbrown.20130316075512.28478: *4* qt_gui.getImageImageFinder
    def getImageImageFinder(self, name):
        '''Theme aware image (icon) path searching

        If self.color_theme, set from @settings -> @string color_theme is set,

         - look first in $HOME/.leo/themes/<theme_name>/Icons,
         - then in .../leo/themes/<theme_name>/Icons,
         - then in .../leo/Icons,
         - as well as trying absolute path
        '''
        trace = False and not g.unitTesting

        def sfn(fn):
            return g.shortFileName(fn.replace('/', '\\'), n=4)

        if self.color_theme:
            # if trace: g.trace('color_theme', self.color_theme)
            # normal, unthemed path to image
            pathname = g.os_path_finalize_join(g.app.loadDir, "..", "Icons")
            pathname = g.os_path_normpath(g.os_path_realpath(pathname))
            if g.os_path_isabs(name):
                testname = g.os_path_normpath(g.os_path_realpath(name))
            else:
                testname = name
            if testname.startswith(pathname):
                # try after removing icons dir from path
                namepart = testname.replace(pathname, '').strip('\\/')
            else:
                namepart = testname
            for base_dir in (g.app.homeLeoDir, g.os_path_join(g.app.loadDir, '..')):
                fullname = g.os_path_finalize_join(
                    base_dir, 'themes',
                    self.color_theme, 'Icons', namepart)
                if g.os_path_exists(fullname):
                    if trace: g.trace('found', sfn(fullname))
                    return fullname
        # original behavior, if name is absolute this will just return it
        fullname = g.os_path_finalize_join(g.app.loadDir, "..", "Icons", name)
        if trace: g.trace('found', g.os_path_exists(fullname), sfn(fullname))
        return fullname
    #@+node:ekr.20110605121601.18518: *4* qt_gui.getTreeImage
    def getTreeImage(self, c, path):
        image = QtGui.QPixmap(path)
        if image.height() > 0 and image.width() > 0:
            return image, image.height()
        else:
            return None, None
    #@+node:ekr.20131007055150.17608: *3* qt_gui.insertKeyEvent
    def insertKeyEvent(self, event, i):
        '''Insert the key given by event in location i of widget event.w.'''
        import leo.core.leoGui as leoGui
        assert isinstance(event, leoGui.LeoKeyEvent)
        qevent = event.event
        assert isinstance(qevent, QtGui.QKeyEvent)
        qw = getattr(event.w, 'widget', None)
        if qw and isinstance(qw, QtWidgets.QTextEdit):
            # g.trace(i, qevent.modifiers(), g.u(qevent.text()))
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
    def makeScriptButton(self, c,
        args=None,
        p=None, # A node containing the script.
        script=None, # The script itself.
        buttonText=None,
        balloonText='Script Button',
        shortcut=None, bg='LightSteelBlue1',
        define_g=True, define_name='__main__', silent=False, # Passed on to c.executeScript.
    ):
        '''Create a script button for the script in node p.
        The button's text defaults to p.headString'''
        k = c.k
        if p and not buttonText: buttonText = p.h.strip()
        if not buttonText: buttonText = 'Unnamed Script Button'
        #@+<< create the button b >>
        #@+node:ekr.20110605121601.18529: *4* << create the button b >>
        iconBar = c.frame.getIconBarObject()
        b = iconBar.add(text=buttonText)
        #@-<< create the button b >>
        #@+<< define the callbacks for b >>
        #@+node:ekr.20110605121601.18530: *4* << define the callbacks for b >>
        def deleteButtonCallback(event=None, b=b, c=c):
            if b: b.pack_forget()
            c.bodyWantsFocus()

        def executeScriptCallback(event=None,
            b=b,
            c=c,
            buttonText=buttonText,
            p=p and p.copy(),
            script=script
        ):
            if c.disableCommandsMessage:
                g.blue('', c.disableCommandsMessage)
            else:
                g.app.scriptDict = {}
                c.executeScript(args=args, p=p, script=script,
                define_g=define_g, define_name=define_name, silent=silent)
                # Remove the button if the script asks to be removed.
                if g.app.scriptDict.get('removeMe'):
                    g.es("removing", "'%s'" % (buttonText), "button at its request")
                    b.pack_forget()
            # Do not assume the script will want to remain in this commander.
        #@-<< define the callbacks for b >>
        b.configure(command=executeScriptCallback)
        if shortcut:
            #@+<< bind the shortcut to executeScriptCallback >>
            #@+node:ekr.20110605121601.18531: *4* << bind the shortcut to executeScriptCallback >>
            func = executeScriptCallback
            shortcut = k.canonicalizeShortcut(shortcut)
            ok = k.bindKey('button', shortcut, func, buttonText)
            if ok:
                g.blue('bound @button', buttonText, 'to', shortcut)
            #@-<< bind the shortcut to executeScriptCallback >>
        #@+<< create press-buttonText-button command >>
        #@+node:ekr.20110605121601.18532: *4* << create press-buttonText-button command >>
        aList = [ch if ch.isalnum() else '-' for ch in buttonText]
        buttonCommandName = ''.join(aList)
        buttonCommandName = buttonCommandName.replace('--', '-')
        buttonCommandName = 'press-%s-button' % buttonCommandName.lower()
        # This will use any shortcut defined in an @shortcuts node.
        k.registerCommand(buttonCommandName, executeScriptCallback, pane='button')
        #@-<< create press-buttonText-button command >>
    #@+node:ekr.20170612065255.1: *3* qt_gui.put_help
    def put_help(self, c, s, short_title=''):
        '''Put the help command.'''
        s = g.adjustTripleString(s.rstrip(), c.tab_width)
        if s.startswith('<') and not s.startswith('<<'):
            pass # how to do selective replace??
        pc = g.app.pluginsController
        table = (
            'viewrendered3.py',
            'viewrendered2.py',
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
        return vr # For unit tests
    #@+node:ekr.20110605121601.18521: *3* qt_gui.runAtIdle
    def runAtIdle(self, aFunc):
        '''This can not be called in some contexts.'''
        QtCore.QTimer.singleShot(0, aFunc)
    #@+node:ekr.20110605121601.18483: *3* qt_gui.runMainLoop & runWithIpythonKernel
    #@+node:ekr.20130930062914.16000: *4* qt_gui.runMainLoop
    def runMainLoop(self):
        '''Start the Qt main loop.'''
        g.app.gui.dismiss_splash_screen()
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
            sys.exit(self.qtApp.exec_())
    #@+node:ekr.20130930062914.16001: *4* qt_gui.runWithIpythonKernel (commands)
    def runWithIpythonKernel(self):
        '''Init Leo to run in an IPython shell.'''
        try:
            import leo.core.leoIPython as leoIPython
            g.app.ipk = ipk = leoIPython.InternalIPKernel()
            ipk.new_qt_console(event=None)
        except Exception:
            g.es_exception()
            print('can not init leo.core.leoIPython.py')
            sys.exit(1)

        @g.command("ipython-new")
        def qtshell_f(event):
            """ Launch new ipython shell window, associated with the same ipython kernel """
            g.app.ipk.new_qt_console(event=event)

        @g.command("ipython-exec")
        def ipython_exec_f(event):
            """ Execute script in current node in ipython namespace """
            c = event and event.get('c')
            if c:
                script = g.getScript(c, c.p, useSentinels=False)
                if script.strip():
                    g.app.ipk.run_script(file_name=c.p.h,script=script)

        ipk.kernelApp.start()
    #@+node:ekr.20111215193352.10220: *3* qt_gui.Splash Screen
    #@+node:ekr.20110605121601.18479: *4* qt_gui.createSplashScreen
    def createSplashScreen(self):
        '''Put up a splash screen with the Leo logo.'''
        trace = False and not g.unitTesting
        from leo.core.leoQt import QtCore
        qt = QtCore.Qt
        splash = None
        if sys.platform.startswith('win'):
            table = ('SplashScreen.jpg', 'SplashScreen.png', 'SplashScreen.ico')
        else:
            table = ('SplashScreen.xpm',)
        for name in table:
            fn = g.os_path_finalize_join(g.app.loadDir, '..', 'Icons', name)
            if g.os_path_exists(fn):
                pm = QtGui.QPixmap(fn)
                if not pm.isNull():
                    if trace: g.trace(fn)
                    splash = QtWidgets.QSplashScreen(pm,
                        qt.WindowStaysOnTopHint)
                    splash.show()
                    # This sleep is required to do the repaint.
                    QtCore.QThread.msleep(10)
                    splash.repaint()
                    break
            else:
                if trace: g.trace('no splash screen icon')
        return splash
    #@+node:ekr.20110613103140.16424: *4* qt_gui.dismiss_splash_screen
    def dismiss_splash_screen(self):
        # g.trace(g.callers())
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
    def isTextWidget(self, w):
        '''Return True if w is some kind of Qt text widget.'''
        if Qsci:
            return isinstance(w, (Qsci.QsciScintilla, QtWidgets.QTextEdit)), w
        else:
            return isinstance(w, QtWidgets.QTextEdit), w

    def isTextWrapper(self, w):
        '''Return True if w is a Text widget suitable for text-oriented commands.'''
        return w and hasattr(w, 'supportsHighLevelInterface') and w.supportsHighLevelInterface
    #@+node:ekr.20110605121601.18526: *4* qt_gui.toUnicode
    def toUnicode(self, s):
        try:
            s = g.u(s)
            return s
        except Exception:
            g.trace('*** Unicode Error: bugs possible')
            # The mass update omitted the encoding param.
            return g.toUnicode(s, reportErrors='replace')
    #@+node:ekr.20110605121601.18527: *4* qt_gui.widget_name
    def widget_name(self, w):
        # First try the widget's getName method.
        if not 'w':
            name = '<no widget>'
        elif hasattr(w, 'getName'):
            name = w.getName()
        elif hasattr(w, 'objectName'):
            name = str(w.objectName())
        elif hasattr(w, '_name'):
            name = w._name
        else:
            name = repr(w)
        # g.trace(id(w),name)
        return name
    #@+node:ekr.20111027083744.16532: *4* qt_gui.enableSignalDebugging
    # enableSignalDebugging(emitCall=foo) and spy your signals until you're sick to your stomach.
    if isQt5:
        pass # Not ready yet.
    else:
        _oldConnect = QtCore.QObject.connect
        _oldDisconnect = QtCore.QObject.disconnect
        _oldEmit = QtCore.QObject.emit

        def _wrapConnect(self, callableObject):
            """Returns a wrapped call to the old version of QtCore.QObject.connect"""

            @staticmethod
            def call(*args):
                callableObject(*args)
                self._oldConnect(*args)

            return call

        def _wrapDisconnect(self, callableObject):
            """Returns a wrapped call to the old version of QtCore.QObject.disconnect"""

            @staticmethod
            def call(*args):
                callableObject(*args)
                self._oldDisconnect(*args)

            return call

        def enableSignalDebugging(self, **kwargs):
            """Call this to enable Qt Signal debugging. This will trap all
            connect, and disconnect calls."""
            f = lambda * args: None
            connectCall = kwargs.get('connectCall', f)
            disconnectCall = kwargs.get('disconnectCall', f)
            emitCall = kwargs.get('emitCall', f)

            def printIt(msg):

                def call(*args):
                    print(msg, args)

                return call
            # Monkey-patch.

            QtCore.QObject.connect = self._wrapConnect(connectCall)
            QtCore.QObject.disconnect = self._wrapDisconnect(disconnectCall)

            def new_emit(self, *args):
                emitCall(self, *args)
                self._oldEmit(self, *args)

            QtCore.QObject.emit = new_emit
    #@-others
#@+node:tbrown.20150724090431.1: ** class StyleClassManager
class StyleClassManager(object):
    style_sclass_property = 'style_class' # name of QObject property for styling
    #@+others
    #@+node:tbrown.20150724090431.2: *3* update_view
    def update_view(self, w):
        """update_view - Make Qt apply w's style

        :param QWidgit w: widgit to style
        """

        w.setStyleSheet("/* */")  # forces visual update
    #@+node:tbrown.20150724090431.3: *3* add_sclass
    def add_sclass(self, w, prop):
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
    def clear_sclasses(self, w):
        """Remove all style classes from QWidget w"""
        w.setProperty(self.style_sclass_property, '')
    #@+node:tbrown.20150724090431.5: *3* has_sclass
    def has_sclass(self, w, prop):
        """Check for style class or list of classes prop on QWidget w"""
        if not prop:
            return
        props = self.sclasses(w)
        if isinstance(prop, str):
            ans = [prop in props]
        else:
            ans = [i in props for i in prop]

        return all(ans)
    #@+node:tbrown.20150724090431.6: *3* remove_sclass
    def remove_sclass(self, w, prop):
        """Remove style class or list of classes prop from QWidget w"""
        if not prop:
            return
        props = self.sclasses(w)
        if isinstance(prop, str):
            props = [i for i in props if i != prop]
        else:
            props = [i for i in props if i not in prop]

        self.set_sclasses(w, props)
    #@+node:tbrown.20150724090431.7: *3* sclass_tests
    def sclass_tests(self):
        """Test style class property manipulation functions"""

        # pylint: disable=len-as-condition

        class Test_W:
            """simple standin for QWidget for testing"""
            def __init__(self):
                self.x = ''
            def property(self, name, default=None):
                return self.x or default
            def setProperty(self, name, value):
                self.x = value

        w = Test_W()

        assert not self.has_sclass(w, 'nonesuch')
        assert not self.has_sclass(w, ['nonesuch'])
        assert not self.has_sclass(w, ['nonesuch', 'either'])
        assert len(self.sclasses(w)) == 0

        self.add_sclass(w, 'test')

        assert not self.has_sclass(w, 'nonesuch')
        assert self.has_sclass(w, 'test')
        assert self.has_sclass(w, ['test'])
        assert not self.has_sclass(w, ['test', 'either'])
        assert len(self.sclasses(w)) == 1

        self.add_sclass(w, 'test')
        assert len(self.sclasses(w)) == 1
        self.add_sclass(w, ['test', 'test', 'other'])
        assert len(self.sclasses(w)) == 2
        assert self.has_sclass(w, 'test')
        assert self.has_sclass(w, 'other')
        assert self.has_sclass(w, ['test', 'other', 'test'])
        assert not self.has_sclass(w, ['test', 'other', 'nonesuch'])

        self.remove_sclass(w, ['other', 'nothere'])
        assert self.has_sclass(w, 'test')
        assert not self.has_sclass(w, 'other')
        assert len(self.sclasses(w)) == 1

        self.toggle_sclass(w, 'third')
        assert len(self.sclasses(w)) == 2
        assert self.has_sclass(w, ['test', 'third'])
        self.toggle_sclass(w, 'third')
        assert len(self.sclasses(w)) == 1
        assert not self.has_sclass(w, ['test', 'third'])

        self.clear_sclasses(w)
        assert len(self.sclasses(w)) == 0
        assert not self.has_sclass(w, 'test')
    #@+node:tbrown.20150724090431.8: *3* sclasses
    def sclasses(self, w):
        """return list of style classes for QWidget w"""
        return str(w.property(self.style_sclass_property) or '').split()
    #@+node:tbrown.20150724090431.9: *3* set_sclasses
    def set_sclasses(self, w, classes):
        """Set style classes for QWidget w to list in classes"""
        w.setProperty(self.style_sclass_property, ' %s ' % ' '.join(set(classes)))
    #@+node:tbrown.20150724090431.10: *3* toggle_sclass
    def toggle_sclass(self, w, prop):
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
class StyleSheetManager(object):
    '''A class to manage (reload) Qt style sheets.'''
    #@+others
    #@+node:ekr.20140912110338.19371: *3* ssm.__init__
    def __init__(self, c, safe=False):
        '''Ctor the ReloadStyle class.'''
        self.c = c
        self.color_db = leoColor.leo_color_database
        self.safe = safe
        self.settings_p = g.findNodeAnywhere(c, '@settings')
        self.mng = StyleClassManager()
        # This warning is inappropriate in some contexts.
            # if not self.settings_p:
                # g.es("No '@settings' node found in outline.  See:")
                # g.es("http://leoeditor.com/tutorial-basics.html#configuring-leo")
    #@+node:ekr.20110605121601.18176: *3* ssm.default_style_sheet
    def default_style_sheet(self):
        '''Return a reasonable default style sheet.'''
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
    #@+node:ekr.20140915062551.19510: *3* ssm.expand_css_constants & helpers
    def expand_css_constants(self, sheet, font_size_delta=None):
        '''Expand @ settings into their corresponding constants.'''
        trace = False and not g.unitTesting
        trace_color = False
        trace_result = True
        trace_to_do = False
        c = self.c
        whine = None
        # Warn once if the stylesheet uses old style style-sheet comment
        constants, deltas = self.adjust_sizes(font_size_delta)
        passes = 10
        to_do = self.find_constants_referenced(sheet)
        if trace and trace_to_do:
            g.trace()
            g.printList(to_do)
        changed = True
        sheet = self.set_indicator_paths(sheet)
        while passes and to_do and changed:
            changed = False
            to_do.sort(key=len, reverse=True)
            for const in to_do:
                value = None
                if const in constants:
                    # This is about to be removed.
                    value = constants[const]
                    if const[1:] not in deltas and not whine:
                        whine = ("'%s' from style-sheet comment definition, "
                            "please use regular @string / @color type @settings."
                            % const)
                        g.es(whine)
                        print(whine)
                else:
                    key = g.app.config.canonicalizeSettingName(const[1:])
                        # lowercase, without '@','-','_', etc.
                    value = c.config.settingsDict.get(key)
                    if value is not None:
                        # New in Leo 5.5: Do NOT add comments here.
                        # They RUIN style sheets if they appear in a nested comment!
                            # value = '%s /* %s */' % (g.u(value.val), key)
                        value = g.u(value.val)
                    elif key in self.color_db:
                        # New in Leo 5.5: Do NOT add comments here.
                        # They RUIN style sheets if they appear in a nested comment!
                        value = self.color_db.get(key)
                            # value = '%s /* %s */' % (value, key)
                        if trace and trace_color: g.trace('found color', key, value)
                if value:
                    sheet = re.sub(
                        ### '\b%s\b' % (const),
                        const + "(?![-A-Za-z0-9_])",
                            # don't replace shorter constants occuring in larger
                        value,
                        sheet,
                    )
                    changed = True
                else:
                    pass
                    # tricky, might be an undefined identifier, but it might
                    # also be a @foo in a /* comment */, where it's harmless.
                    # So rely on whoever calls .setStyleSheet() to do the right thing.
            passes -= 1
            to_do = self.find_constants_referenced(sheet)
        if not passes and to_do:
            g.es("To many iterations of substitution")
        sheet = sheet.replace('\\\n', '') # join lines ending in \
        if trace and trace_result: g.trace('returns...\n', sheet)
        return sheet
    #@+node:ekr.20150617085045.1: *4* ssm.adjust_sizes
    def adjust_sizes(self, font_size_delta):
        '''Adjust constants to reflect c._style_deltas.'''
        trace = False and not g.unitTesting
        c = self.c
        constants = {} # old: self.find_constants_defined(sheet)
        deltas = c._style_deltas
        # legacy
        if font_size_delta:
            deltas['font-size-body'] = font_size_delta
        if trace:
            g.trace('c._style_deltas', c._style_deltas)
        for delta in c._style_deltas:
            # adjust @font-size-body by font_size_delta
            # easily extendable to @font-size-*
            val = c.config.getString(delta)
            passes = 10
            while passes and val and val.startswith('@'):
                key = g.app.config.canonicalizeSettingName(val[1:])
                val = c.config.settingsDict.get(key)
                if val:
                    val = val.val
                passes -= 1
            if deltas[delta] and (val is not None):
                size = ''.join(i for i in val if i in '01234567890.')
                units = ''.join(i for i in val if i not in '01234567890.')
                size = max(1, int(size) + deltas[delta])
                constants["@" + delta] = "%s%s" % (size, units)
        return constants, deltas
    #@+node:tbrown.20131120093739.27085: *4* ssm.find_constants_referenced
    def find_constants_referenced(self, text):
        """find_constants - Return a list of constants referenced in the supplied text,
        constants match::

            @[A-Za-z_][-A-Za-z0-9_]*
            i.e. @foo_1-5

        :Parameters:
        - `text`: text to search
        """
        return re.findall(r"@[A-Za-z_][-A-Za-z0-9_]*", text)
    #@+node:tbrown.20130411121812.28335: *4* ssm.find_constants_defined (no longer used)
    def find_constants_defined(self, text):
        r"""find_constants - Return a dict of constants defined in the supplied text.

        NOTE: this supports a legacy way of specifying @<identifiers>, regular
        @string and @color settings should be used instead, so calling this
        wouldn't be needed.  expand_css_constants() issues a warning when
        @<identifiers> are found in the output of this method.

        Constants match::

            ^\s*(@[A-Za-z_][-A-Za-z0-9_]*)\s*=\s*(.*)$
            i.e.
            @foo_1-5=a
                @foo_1-5 = a more here

        :Parameters:
        - `text`: text to search
        """
        pattern = re.compile(r"^\s*(@[A-Za-z_][-A-Za-z0-9_]*)\s*=\s*(.*)$")
        ans = {}
        text = text.replace('\\\n', '') # merge lines ending in \
        for line in text.split('\n'):
            test = pattern.match(line)
            if test:
                ans.update([test.groups()])
        # constants may refer to other constants, de-reference here
        change = True
        level = 0
        while change and level < 10:
            level += 1
            change = False
            for k in ans:
                # pylint: disable=unnecessary-lambda
                # process longest first so @solarized-base0 is not replaced
                # when it's part of @solarized-base03
                for o in sorted(ans, key=lambda x: len(x), reverse=True):
                    if o in ans[k]:
                        change = True
                        ans[k] = ans[k].replace(o, ans[o])
        if level == 10:
            print("Ten levels of recursion processing styles, abandoned.")
            g.es("Ten levels of recursion processing styles, abandoned.")
        return ans
    #@+node:ekr.20150617090104.1: *4* ssm.set_indicator_paths & helper
    def set_indicator_paths(self, sheet):
        '''
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
        '''
        trace = False and not g.unitTesting
        close_path = self.get_indicator_path('tree-image-closed')
        open_path = self.get_indicator_path('tree-image-open')
        # Make all substitutions in the stylesheet.
        table = (
            (open_path,  re.compile(r'\bimage:\s*@tree-image-open', re.IGNORECASE)),
            (open_path,  re.compile(r'\bimage:\s*at-tree-image-open', re.IGNORECASE)),
            (close_path, re.compile(r'\bimage:\s*@tree-image-closed', re.IGNORECASE)),
            (close_path, re.compile(r'\bimage:\s*at-tree-image-closed', re.IGNORECASE)),
        )
        if trace:
            g.trace('open path: ', repr(open_path))
            g.trace('close_path:', repr(close_path))
        for path, pattern in table:
            for mo in pattern.finditer(sheet):
                old = mo.group(0)
                new = 'image: url(%s)' % path
                if trace: g.trace('found', old)
                sheet = sheet.replace(old, new)
        return sheet
    #@+node:ekr.20170307083738.1: *5* ssm.get_indicator_path
    def get_indicator_path(self, setting):
        '''Return the path to the open/close indicator icon.'''
        c = self.c
        s = c.config.getString(setting)
        if s:
            table = (
                g.os_path_finalize_join(g.app.loadDir, '..', 'Icons', s),
                g.os_path_finalize_join('~', s),
            )
            for path in table:
                if g.os_path_exists(path):
                    return path.replace('\\','/')
                        # Required on Windows.
            g.es_print('no icon found for:', setting)
            return None
        else:
            # Not an error.
            return None
    #@+node:ekr.20140916170549.19551: *3* ssm.get_data
    def get_data(self, setting):
        '''Return the value of the @data node for the setting.'''
        c = self.c
        return c.config.getData(setting, strip_comments=False, strip_data=False) or []
    #@+node:ekr.20140913054442.19390: *3* ssm.get_master_widget
    def get_master_widget(self, top=None):
        '''
        Carefully return the master widget.
        For --gui=qttabs, c.frame.top.leo_master is a LeoTabbedTopLevel.
        For --gui=qt,     c.frame.top is a DynamicWindow.
        '''
        if top is None: top = self.c.frame.top
        master = top.leo_master or top
        return master
    #@+node:ekr.20140912110338.19365: *3* ssm.get_stylesheet & helpers
    def get_stylesheet(self):
        '''
        Scan for themes or @data qt-gui-plugin-style-sheet nodes.
        Return the text of the relevant node.
        '''
        themes, theme_name = self.find_themes()
        if themes:
            return self.get_last_theme(themes, theme_name)
        else:
            g.es("No theme found, assuming static stylesheet")
            return self.get_last_style_sheet()
    #@+node:ekr.20140912110338.19368: *4* ssm.find_themes
    def find_themes(self):
        '''Find all theme-related nodes in the @settings tree.'''
        themes, theme_name = [], 'unknown'
        for p in self.settings_p.subtree_iter():
            if p.h.startswith('@string color_theme'):
                theme_name = p.h.split()[-1]
                themes.append((theme_name, p.copy()))
            elif p.h == 'stylesheet & source':
                theme_name = 'unknown'
                themes.append((theme_name, p.copy()))
        return themes, theme_name
    #@+node:ekr.20140912110338.19367: *4* ssm.get_last_style_sheet
    def get_last_style_sheet(self):
        '''Return the body text of the *last* @data qt-gui-plugin-style-sheet node.'''
        sheets = [p.copy() for p in self.settings_p.subtree_iter()
            if p.h == '@data qt-gui-plugin-style-sheet']
        if sheets:
            if len(sheets) > 1:
                g.es("WARNING: found multiple\n'@data qt-gui-plugin-style-sheet' nodes")
                g.es("Using the *last* node found")
            else:
                g.es("Stylesheet found")
            data_p = sheets[-1]
            return data_p.b
        else:
            g.es("No '@data qt-gui-plugin-style-sheet' node")
            # g.es("Typically 'Reload Settings' is used in the Global or Personal "
                 # "settings files, 'leoSettings.leo and 'myLeoSettings.leo'")
            return None
    #@+node:ekr.20140912110338.19366: *4* ssm.get_last_theme
    def get_last_theme(self, themes, theme_name):
        '''Return the stylesheet of the last theme.'''
        g.es("Found theme(s):")
        for name, p in themes:
            g.es('found theme:', name)
        if len(themes) > 1:
            g.es("WARNING: using the *last* theme found")
        theme_p = themes[-1][1]
        unl = theme_p.get_UNL() + '-->'
        seen = 0
        for i in theme_p.subtree_iter():
            # Disable any @data qt-gui-plugin-style-sheet nodes in theme's tree.
            if i.h == '@data qt-gui-plugin-style-sheet':
                i.h = '@@data qt-gui-plugin-style-sheet'
                seen += 1
        if seen == 0:
            g.es("NOTE: Did not find compiled stylesheet for theme")
        elif seen > 1:
            g.es("NOTE: Found multiple compiled stylesheets for theme")
        text = [
            "/*\n  DON'T EDIT THIS, EDIT THE OTHER NODES UNDER "
            "('stylesheet & source')\n  AND RECREATE THIS BY "
            "Alt-X style-reload"
            "\n\n  AUTOMATICALLY GENERATED FROM:\n  %s\n  %s\n*/\n\n"
            % (
                theme_p.get_UNL(with_proto=True),
                datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
            )]
        for i in theme_p.subtree_iter():
            src = i.get_UNL().replace(unl, '')
            if i.h.startswith('@data '):
                i.h = '@' + i.h
            if ('@ignore' in src) or ('@data' in src):
                continue
            text.append("/*### %s %s*/\n%s\n\n" % (
                src, '#' * (70 - len(src)),
                i.b.strip()
            ))
        stylesheet = '\n'.join(text)
        if self.safe:
            g.trace('Stylesheet:\n' % stylesheet)
        else:
            data_p = theme_p.insertAsLastChild()
            data_p.h = '@data qt-gui-plugin-style-sheet'
            data_p.b = stylesheet
            g.es("Stylesheet compiled")
        return stylesheet
    #@+node:ekr.20140916170549.19552: *3* ssm.get_style_sheet_from_settings
    def get_style_sheet_from_settings(self):
        '''
        Scan for themes or @data qt-gui-plugin-style-sheet nodes.
        Return the text of the relevant node.
        '''
        if 0: # not ready yet
            c = self.c
            d = c.config.settingsDict
            for key in sorted(d.keys()):
                gs = d.get(key) # A GeneralSetting object.
                if gs.kind == 'string':
                    setting = g.toUnicode(gs.setting)
                    val = g.toUnicode(gs.val)
                    if setting and val and val.startswith('color_theme'):
                        sheet = setting
                        break
        else:
            # No setting found
            aList1 = self.get_data('qt-gui-plugin-style-sheet')
            aList2 = self.get_data('qt-gui-user-style-sheet')
            if aList2: aList1.extend(aList2)
            sheet = ''.join(aList1)
            sheet = self.expand_css_constants(sheet)
        # g.trace(len(sheet))
        return sheet
    #@+node:ekr.20140912110338.19372: *3* ssm.munge
    def munge(self, stylesheet):
        '''
        Return the stylesheet without extra whitespace.

        To avoid false mismatches, this should approximate what Qt does.
        To avoid false matches, this should not munge too much.
        '''
        s = ''.join([s.lstrip().replace('  ', ' ').replace(' \n', '\n')
            for s in g.splitLines(stylesheet)])
        return s.rstrip()
            # Don't care about ending newline.
    #@+node:ekr.20140915194122.19476: *3* ssm.print_style_sheet
    def print_style_sheet(self):
        '''Show the top-level style sheet.'''
        w = self.get_master_widget()
        sheet = w.styleSheet()
        print('style sheet for: %s...\n\n%s' % (w, sheet))
    #@+node:ekr.20170222051716.1: *3* ssm.reload_settings
    def reload_settings(self):
        '''
        Recompute and apply the stylesheet.
        Called automatically by the reload-settings commands.
        '''
        # g.trace('(StyleSheetManager)')
        sheet = self.get_style_sheet_from_settings()
        if sheet:
            w = self.get_master_widget()
            w.setStyleSheet(sheet)
        # self.c.redraw()

    reloadSettings = reload_settings
    #@+node:ekr.20140913054442.19391: *3* ssm.set selected_style_sheet
    def set_selected_style_sheet(self):
        '''For manual testing: update the stylesheet using c.p.b.'''
        if not g.unitTesting:
            c = self.c
            sheet = c.p.b
            sheet = self.expand_css_constants(sheet)
            w = self.get_master_widget(c.frame.top)
            w.setStyleSheet(sheet)
    #@+node:ekr.20110605121601.18175: *3* ssm.set_style_sheets
    def set_style_sheets(self, all=True, top=None, w=None):
        '''Set the master style sheet for all widgets using config settings.'''
        trace = False
        c = self.c
        if top is None: top = c.frame.top
        selectors = ['qt-gui-plugin-style-sheet']
        if all:
            selectors.append('qt-gui-user-style-sheet')
        sheets = []
        for name in selectors:
            sheet = c.config.getData(name, strip_comments=False)
                # don't strip `#selector_name { ...` type syntax
            if sheet:
                if '\n' in sheet[0]:
                    sheet = ''.join(sheet)
                else:
                    sheet = '\n'.join(sheet)
            if sheet and sheet.strip():
                line0 = '\n/* ===== From %s ===== */\n\n' % (name)
                sheet = line0 + sheet
                sheets.append(sheet)
        if sheets:
            sheet = "\n".join(sheets)
            # store *before* expanding, so later expansions get new zoom
            c.active_stylesheet = sheet
            sheet = self.expand_css_constants(sheet)
            if not sheet: sheet = self.default_style_sheet()
            if w is None:
                w = self.get_master_widget(top)
            if trace: g.trace(w, len(sheet))
            w.setStyleSheet(sheet)
        else:
            if trace: g.trace('no style sheet')
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo

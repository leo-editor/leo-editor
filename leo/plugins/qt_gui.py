#@+leo-ver=5-thin
#@+node:ekr.20140907085654.18699: * @file ../plugins/qt_gui.py
'''This file contains the gui wrapper for Qt: g.app.gui.'''
import leo.core.leoGlobals as g
import leo.core.leoGui as leoGui
from leo.core.leoQt import isQt5,Qsci,QtCore,QtGui,QtWidgets
from leo.plugins.qt_events import LeoQtEventFilter
from leo.plugins.qt_idle_time import IdleTime
from leo.plugins.qt_text import LeoQTextBrowser,PlainTextWrapper,QTextMixin
from leo.plugins.qtGui import LeoQtFrame,LeoQtSpellTab
from leo.plugins.qtGui import SDIFrameFactory,TabbedFrameFactory
import datetime
import os
import sys
#@+others
#@+node:ekr.20110605121601.18134: ** init
def init():
    trace = (False or g.trace_startup) and not g.unitTesting
    if trace and g.trace_startup: print('qtGui.__init__')
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
    #@+node:ekr.20110605121601.18477: *3*  LeoQtGui.__init__
    def __init__ (self):
        '''Ctor for qtGui class.'''
        # Initialize the base class.
        leoGui.LeoGui.__init__(self,'qt')
        # g.trace('(qtGui)',g.callers())
        self.qtApp = QtWidgets.QApplication(sys.argv)
        self.bodyTextWidget = QTextMixin ### BaseQTextWrapper
        self.iconimages = {}
        self.idleTimeClass = IdleTime
        self.insert_char_flag = False # A flag for eventFilter.
        self.plainTextWidget = PlainTextWrapper ### BaseQTextWrapper
        self.mGuiName = 'qt'
        self.color_theme = g.app.config and g.app.config.getString('color_theme') or None
        # Communication between idle_focus_helper and activate/deactivate events.
        self.active = True
        # Put up the splash screen()
        if (g.app.use_splash_screen and
            not g.app.batchMode and
            not g.app.silentMode and
            not g.unitTesting
        ):
            self.splashScreen = self.createSplashScreen()
        if g.app.qt_use_tabs:    
            self.frameFactory = TabbedFrameFactory()
        else:
            self.frameFactory = SDIFrameFactory()
    #@+node:ekr.20110605121601.18484: *3*  LeoQtGui.destroySelf
    def destroySelf (self):
        QtCore.pyqtRemoveInputHook()
        self.qtApp.exit()
    #@+node:ekr.20111022215436.16685: *3* LeoQtGui.Borders
    #@+node:ekr.20120927164343.10092: *4* LeoQtGui.add_border
    def add_border(self,c,w):
        
        trace = False and not g.unitTesting
        state = c.k and c.k.unboundKeyAction
        if state and c.use_focus_border:
            d = {
                'command':  c.focus_border_command_state_color,
                'insert':   c.focus_border_color,
                'overwrite':c.focus_border_overwrite_state_color,
            }
            color = d.get(state,c.focus_border_color)
            name = g.u(w.objectName())
            if trace: g.trace(name,'color',color)
            # if name =='richTextEdit':
                # w = c.frame.top.leo_body_inner_frame
                # self.paint_qframe(w,color)
            # elif
            if not name.startswith('head'):
                selector = w.__class__.__name__
                color = c.focus_border_color
                sheet = "border: %spx solid %s" % (c.focus_border_width,color)
                self.update_style_sheet(w,'border',sheet,selector=selector)
    #@+node:ekr.20120927164343.10093: *4* LeoQtGui.remove_border
    def remove_border(self,c,w):

        if c.use_focus_border:
            name = g.u(w.objectName())
            # if w.objectName()=='richTextEdit':
                # w = c.frame.top.leo_body_inner_frame
                # self.paint_qframe(w,'white')
            # elif
            if not name.startswith('head'):
                selector = w.__class__.__name__
                sheet = "border: %spx solid white" % c.focus_border_width
                self.update_style_sheet(w,'border',sheet,selector=selector)
    #@+node:ekr.20120927164343.10094: *4* LeoQtGui.paint_qframe
    def paint_qframe (self,w,color):

        assert isinstance(w,QtWidgets.QFrame)

        # How's this for a kludge.
        # Set this ivar for InnerBodyFrame.paintEvent.
        g.app.gui.innerBodyFrameColor = color
    #@+node:ekr.20110605121601.18485: *3* LeoQtGui.Clipboard
    def replaceClipboardWith (self,s):

        '''Replace the clipboard with the string s.'''

        trace = False and not g.unitTesting
        cb = self.qtApp.clipboard()
        if cb:
            # cb.clear()  # unnecessary, breaks on some Qt versions
            s = g.toUnicode(s)
            QtWidgets.QApplication.processEvents()
            cb.setText(s)
            QtWidgets.QApplication.processEvents()
            if trace: g.trace(len(s),type(s),s[:25])
        else:
            g.trace('no clipboard!')

    def getTextFromClipboard (self):

        '''Get a unicode string from the clipboard.'''

        trace = False and not g.unitTesting
        cb = self.qtApp.clipboard()
        if cb:
            QtWidgets.QApplication.processEvents()
            s = cb.text()
            if trace: g.trace (len(s),type(s),s[:25])
            s = g.app.gui.toUnicode(s)
                # Same as g.u(s), but with error handling.
            return s
        else:
            g.trace('no clipboard!')
            return ''
    #@+node:ekr.20110605121601.18487: *3* LeoQtGui.Dialogs & panels
    #@+node:ekr.20110605121601.18488: *4* LeoQtGui.alert
    def alert (self,c,message):

        if g.unitTesting: return

        b = QtWidgets.QMessageBox
        d = b(None)
        d.setWindowTitle('Alert')
        d.setText(message)
        d.setIcon(b.Warning)
        d.addButton('Ok',b.YesRole)
        c.in_qt_dialog = True
        d.exec_()
        c.in_qt_dialog = False
    #@+node:ekr.20110605121601.18489: *4* LeoQtGui.makeFilter
    def makeFilter (self,filetypes):

        '''Return the Qt-style dialog filter from filetypes list.'''

        filters = ['%s (%s)' % (z) for z in filetypes]

        return ';;'.join(filters)
    #@+node:ekr.20110605121601.18492: *4* LeoQtGui.qtGui panels
    def createComparePanel(self,c):

        """Create a qt color picker panel."""
        return None # This window is optional.
        # return leoQtComparePanel(c)

    def createFindTab (self,c,parentFrame):
        """Create a qt find tab in the indicated frame."""
        pass # Now done in dw.createFindTab.

    def createLeoFrame(self,c,title):
        """Create a new Leo frame."""
        gui = self
        return LeoQtFrame(c,title,gui)

    def createSpellTab(self,c,spellHandler,tabName):
        return LeoQtSpellTab(c,spellHandler,tabName)

    #@+node:ekr.20110605121601.18493: *4* LeoQtGui.runAboutLeoDialog
    def runAboutLeoDialog(self,c,version,theCopyright,url,email):

        """Create and run a qt About Leo dialog."""

        if g.unitTesting: return None

        b = QtWidgets.QMessageBox
        d = b(c.frame.top)

        d.setText('%s\n%s\n%s\n%s' % (
            version,theCopyright,url,email))
        d.setIcon(b.Information)
        yes = d.addButton('Ok',b.YesRole)
        d.setDefaultButton(yes)
        c.in_qt_dialog = True
        d.exec_()
        c.in_qt_dialog = False
    #@+node:ekr.20110605121601.18496: *4* LeoQtGui.runAskDateTimeDialog
    def runAskDateTimeDialog(self, c, title, 
        message='Select Date/Time', init=None, step_min={}):
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
            def __init__(self, parent=None, init=None, step_min={}):

                self.step_min = step_min
                if init:
                    QtWidgets.QDateTimeEdit.__init__(self, init, parent)
                else:
                    QtWidgets.QDateTimeEdit.__init__(self, parent)

            def stepBy(self, step):
                cs = self.currentSection()
                if cs in self.step_min and abs(step) < self.step_min[cs]:
                    step = self.step_min[cs] if step > 0 else -self.step_min[cs]
                QtWidgets.QDateTimeEdit.stepBy(self, step)

        class Calendar(QtWidgets.QDialog):
            def __init__(self, parent=None, message='Select Date/Time',
                init=None, step_min={}):
                QtWidgets.QDialog.__init__(self, parent)

                layout = QtWidgets.QVBoxLayout()
                self.setLayout(layout)

                layout.addWidget(QtWidgets.QLabel(message))

                self.dt = DateTimeEditStepped(init=init, step_min=step_min)
                self.dt.setCalendarPopup(True)
                layout.addWidget(self.dt)

                buttonBox = QtWidgets.QDialogButtonBox(
                QtWidgets.QDialogButtonBox.Ok
                    | QtWidgets.QDialogButtonBox.Cancel)
                layout.addWidget(buttonBox)

                buttonBox.accepted.connect(self.accept)
                buttonBox.rejected.connect(self.reject)

        if g.unitTesting: return None

        b = Calendar
        if not init:
            init = datetime.datetime.now()
        d = b(c.frame.top, message=message, init=init, step_min=step_min)

        d.setWindowTitle(title)

        c.in_qt_dialog = True
        val = d.exec_()
        c.in_qt_dialog = False

        if val != d.Accepted:
            return None
        else:
            return d.dt.dateTime().toPyDateTime()
    #@+node:ekr.20110605121601.18494: *4* LeoQtGui.runAskLeoIDDialog
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
        s,ok = QtWidgets.QInputDialog.getText(parent,title,message)
        return g.u(s)
    #@+node:ekr.20110605121601.18491: *4* LeoQtGui.runAskOkCancelNumberDialog
    def runAskOkCancelNumberDialog(self,c,title,message,cancelButtonText=None,okButtonText=None):

        """Create and run askOkCancelNumber dialog ."""

        if g.unitTesting: return None

        # n,ok = QtWidgets.QInputDialog.getDouble(None,title,message)
        d = QtWidgets.QInputDialog()
        d.setWindowTitle(title)
        d.setLabelText(message)
        if cancelButtonText:
            d.setCancelButtonText(cancelButtonText)
        if okButtonText:
            d.setOkButtonText(okButtonText)
        ok = d.exec_()
        n = d.textValue()
        try:
            n = float(n)
        except ValueError:
            n = None
        return n if ok else None
    #@+node:ekr.20110605121601.18490: *4* LeoQtGui.runAskOkCancelStringDialog
    def runAskOkCancelStringDialog(self,c,title,message,cancelButtonText=None,
                                   okButtonText=None,default=""):

        """Create and run askOkCancelString dialog ."""

        if g.unitTesting: return None

        d = QtWidgets.QInputDialog()
        d.setWindowTitle(title)
        d.setLabelText(message)
        d.setTextValue(default)
        if cancelButtonText:
            d.setCancelButtonText(cancelButtonText)
        if okButtonText:
            d.setOkButtonText(okButtonText)
        ok = d.exec_()
        return str(d.textValue()) if ok else None
    #@+node:ekr.20110605121601.18495: *4* LeoQtGui.runAskOkDialog
    def runAskOkDialog(self,c,title,message=None,text="Ok"):

        """Create and run a qt askOK dialog ."""

        if g.unitTesting: return None
        b = QtWidgets.QMessageBox
        d = b(c.frame.top)
        d.setWindowTitle(title)
        if message: d.setText(message)
        d.setIcon(b.Information)
        d.addButton(text,b.YesRole)
        c.in_qt_dialog = True
        d.exec_()
        c.in_qt_dialog = False
    #@+node:ekr.20110605121601.18497: *4* LeoQtGui.runAskYesNoCancelDialog
    def runAskYesNoCancelDialog(self,c,title,
        message=None,
        yesMessage="&Yes",
        noMessage="&No",
        yesToAllMessage=None,
        defaultButton="Yes"
    ):

        """Create and run an askYesNo dialog."""

        if g.unitTesting:
            return None
        b = QtWidgets.QMessageBox
        d = b(c.frame.top)
        if message: d.setText(message)
        d.setIcon(b.Warning)
        d.setWindowTitle(title)
        yes      = d.addButton(yesMessage,b.YesRole)
        no       = d.addButton(noMessage,b.NoRole)
        yesToAll = d.addButton(yesToAllMessage,b.YesRole) if yesToAllMessage else None
        cancel = d.addButton(b.Cancel)
        if   defaultButton == "Yes": d.setDefaultButton(yes)
        elif defaultButton == "No": d.setDefaultButton(no)
        else: d.setDefaultButton(cancel)
        c.in_qt_dialog = True
        val = d.exec_()
        c.in_qt_dialog = False
        if   val == 0: val = 'yes'
        elif val == 1: val = 'no'
        elif yesToAll and val == 2: val = 'yes-to-all'
        else: val = 'cancel'
        return val
    #@+node:ekr.20110605121601.18498: *4* LeoQtGui.runAskYesNoDialog
    def runAskYesNoDialog(self,c,title,message=None):

        """Create and run an askYesNo dialog."""

        if g.unitTesting: return None
        b = QtWidgets.QMessageBox
        d = b(c.frame.top)
        d.setWindowTitle(title)
        if message: d.setText(message)
        d.setIcon(b.Information)
        yes = d.addButton('&Yes',b.YesRole)
        d.addButton('&No',b.NoRole)
        d.setDefaultButton(yes)
        c.in_qt_dialog = True
        val = d.exec_()
        c.in_qt_dialog = False
        return 'yes' if val == 0 else 'no'
    #@+node:ekr.20110605121601.18499: *4* LeoQtGui.runOpenDirectoryDialog
    def runOpenDirectoryDialog(self,title,startdir):

        """Create and run an Qt open directory dialog ."""

        parent = None
        s = QtWidgets.QFileDialog.getExistingDirectory (parent,title,startdir)
        return g.u(s)
    #@+node:ekr.20110605121601.18500: *4* LeoQtGui.runOpenFileDialog
    def runOpenFileDialog(self,title,filetypes,defaultextension='',multiple=False,startpath=None):

        """Create and run an Qt open file dialog ."""

        if g.unitTesting:
            return ''
        else:
            if startpath is None:
                startpath = os.curdir

            parent = None
            filter = self.makeFilter(filetypes)

            if multiple:
                lst = QtWidgets.QFileDialog.getOpenFileNames(parent,title,startpath,filter)
                if isQt5:  # this is a *Py*Qt change rather than a Qt change
                    lst, selected_filter = lst
                return [g.u(s) for s in lst]
            else:
                s = QtWidgets.QFileDialog.getOpenFileName(parent,title,startpath,filter)
                if isQt5:
                    s, selected_filter = s
                return g.u(s)
    #@+node:ekr.20110605121601.18501: *4* LeoQtGui.runPropertiesDialog
    def runPropertiesDialog(self,
        title='Properties',data={}, callback=None, buttons=None):

        """Dispay a modal TkPropertiesDialog"""

        # g.trace(data)
        g.warning('Properties menu not supported for Qt gui')
        result = 'Cancel'
        return result,data
    #@+node:ekr.20110605121601.18502: *4* LeoQtGui.runSaveFileDialog
    def runSaveFileDialog(self,initialfile='',title='Save',filetypes=[],defaultextension=''):

        """Create and run an Qt save file dialog ."""

        if g.unitTesting:
            return ''
        else:
            parent = None
            filter_ = self.makeFilter(filetypes)
            s = QtWidgets.QFileDialog.getSaveFileName(parent,title,os.curdir,filter_)
            return g.u(s)
    #@+node:ekr.20110605121601.18503: *4* LeoQtGui.runScrolledMessageDialog
    def runScrolledMessageDialog (self,
        short_title= '',
        title='Message',
        label= '',
        msg='',
        c=None,**kw
    ):

        if g.unitTesting: return None

        def send(title=title, label=label, msg=msg, c=c, kw=kw):
            return g.doHook('scrolledMessage',
                short_title=short_title,title=title,
                label=label, msg=msg,c=c, **kw)

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
                    vr.onCreate('tag',{'c':c})
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
        d.addButton('Ok',b.YesRole)
        c.in_qt_dialog = True
        d.exec_()
        c.in_qt_dialog = False
        #@-<< emergency fallback >>
    #@+node:ekr.20110607182447.16456: *3* LeoQtGui.Event handlers
    #@+node:ekr.20110605121601.18481: *4* LeoQtGui.onDeactiveEvent
    deactivated_name = ''

    def onDeactivateEvent (self,event,c,obj,tag):
        '''Gracefully deactivate the Leo window.'''
        trace = False and not g.unitTesting
        # This is called several times for each window activation.
        if c.exists and not self.deactivated_name:
            self.deactivated_name = self.widget_name(self.get_focus())
            self.active = False
            if trace: g.trace(self.deactivated_name)
            c.k.keyboardQuit(setFocus=False)
                # The best way to retain as much focus as possible.
            g.doHook('deactivate',c=c,p=c.p,v=c.p,event=event)
    #@+node:ekr.20110605121601.18480: *4* LeoQtGui.onActivateEvent
    # Called from eventFilter

    def onActivateEvent (self,event,c,obj,tag):
        '''Restore the focus when the Leo window is activated.'''
        # This is called several times for each window activation.
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
            g.doHook('activate',c=c,p=c.p,v=c.p,event=event)
    #@+node:ekr.20130921043420.21175: *4* LeoQtGui.setFilter
    # w's type is in (DynamicWindow,QMinibufferWrapper,LeoQtLog,LeoQtTree,
    # QTextEditWrapper,LeoQTextBrowser,LeoQuickSearchWidget,cleoQtUI)
    def setFilter(self,c,obj,w,tag):
        '''
        Create an event filter in obj.
        w is a wrapper object, not necessarily a QWidget.
        '''
        if 0:
            g.trace(isinstance(w,QtWidgets.QWidget),
                hasattr(w,'getName') and w.getName() or None,
                w.__class__.__name__)
        if 0:
            g.trace('obj: %4s %20s w: %5s %s' % (
                isinstance(obj,QtWidgets.QWidget),obj.__class__.__name__,
                isinstance(w,QtWidgets.QWidget),w.__class__.__name__))
        assert isinstance(obj,QtWidgets.QWidget),obj
        gui = self
        theFilter = LeoQtEventFilter(c,w=w,tag=tag)
        obj.installEventFilter(theFilter)
        w.ev_filter = theFilter
            # Set the official ivar in w.
    #@+node:ekr.20110605121601.18508: *3* LeoQtGui.Focus
    def get_focus(self,c=None,raw=False):
        """Returns the widget that has focus."""
        # pylint: disable=w0221
        # Arguments number differs from overridden method.
        trace = False and not g.unitTesting
        app = QtWidgets.QApplication
        w = app.focusWidget()
        if w and not raw and isinstance(w,LeoQTextBrowser):
            has_w = hasattr(w,'leo_wrapper') and w.leo_wrapper
            if has_w:
                if trace: g.trace(w)
            elif c:
                # Kludge: DynamicWindow creates the body pane
                # with wrapper = None, so return the LeoQtBody.
                w = c.frame.body
        if trace: g.trace('(qtGui)',w.__class__.__name__,g.callers())
        return w

    def set_focus(self,c,w):
        """Put the focus on the widget."""
        trace = False and not g.unitTesting
        gui = self
        if w:
            if hasattr(w,'widget') and w.widget: w = w.widget
            if trace: g.trace('(qtGui)',w.__class__.__name__)
            w.setFocus()

    def ensure_commander_visible(self, c1):
        """Check to see if c.frame is in a tabbed ui, and if so, make sure
        the tab is visible"""

        # START: copy from Code-->Startup & external files-->@file runLeo.py -->run & helpers-->doPostPluginsInit & helpers (runLeo.py)
        # For qttabs gui, select the first-loaded tab.
        if hasattr(g.app.gui,'frameFactory'):
            factory = g.app.gui.frameFactory
            if factory and hasattr(factory,'setTabForCommander'):
                c = c1
                factory.setTabForCommander(c)
                c.bodyWantsFocusNow()
        # END: copy
    #@+node:ekr.20110605121601.18510: *3* LeoQtGui.getFontFromParams
    def getFontFromParams(self,family,size,slant,weight,defaultSize=12):

        trace = False and not g.unitTesting
        try: size = int(size)
        except Exception: size = 0
        if size < 1: size = defaultSize
        d = {
            'black':QtGui.QFont.Black,
            'bold':QtGui.QFont.Bold,
            'demibold':QtGui.QFont.DemiBold,
            'light':QtGui.QFont.Light,
            'normal':QtGui.QFont.Normal,
        }
        weight_val = d.get(weight.lower(),QtGui.QFont.Normal)
        italic = slant == 'italic'
        if not family:
            family = g.app.config.defaultFontFamily
        if not family:
            family = 'DejaVu Sans Mono'
        try:
            font = QtGui.QFont(family,size,weight_val,italic)
            if trace: g.trace(family,size,g.callers())
            return font
        except:
            g.es("exception setting font",g.callers(4))
            g.es("","family,size,slant,weight:","",family,"",size,"",slant,"",weight)
            # g.es_exception() # This just confuses people.
            return g.app.config.defaultFont
    #@+node:ekr.20110605121601.18511: *3* LeoQtGui.getFullVersion
    def getFullVersion (self,c=None):
        '''Return the PyQt version (for signon)'''
        try:
            qtLevel = 'version %s' % QtCore.QT_VERSION_STR
        except Exception:
            # g.es_exception()
            qtLevel = '<qtLevel>'
        return 'PyQt %s' % (qtLevel)
    #@+node:ekr.20110605121601.18514: *3* LeoQtGui.Icons
    #@+node:ekr.20110605121601.18515: *4* LeoQtGui.attachLeoIcon
    def attachLeoIcon (self,window):

        """Attach a Leo icon to the window."""

        #icon = self.getIconImage('leoApp.ico')

        #window.setWindowIcon(icon)
        window.setWindowIcon(QtGui.QIcon(g.app.leoDir + "/Icons/leoapp32.png"))    
        #window.setLeoWindowIcon()
    #@+node:ekr.20110605121601.18516: *4* LeoQtGui.getIconImage
    def getIconImage (self,name):

        '''Load the icon and return it.'''

        trace = False and not g.unitTesting
        verbose = False

        # Return the image from the cache if possible.
        if name in self.iconimages:
            image = self.iconimages.get(name)
            if trace and verbose: # and not name.startswith('box'):
                g.trace('cached',id(image),name,image)
            return image
        try:
            iconsDir = g.os_path_join(g.app.loadDir,"..","Icons")
            homeIconsDir = g.os_path_join(g.app.homeLeoDir,"Icons")
            for theDir in (homeIconsDir,iconsDir):
                fullname = g.os_path_finalize_join(theDir,name)
                if g.os_path_exists(fullname):
                    if 0: # Not needed: use QTreeWidget.setIconsize.
                        pixmap = QtWidgets.QPixmap()
                        pixmap.load(fullname)
                        image = QtWidgets.QIcon(pixmap)
                    else:
                        image = QtWidgets.QIcon(fullname)
                        if trace: g.trace('name',fullname,'image',image)

                    self.iconimages[name] = image
                    if trace: g.trace('new',id(image),theDir,name)
                    return image
                elif trace: g.trace('Directory not found',theDir)
            # No image found.
            if trace: g.trace('Not found',name)
            return None
        except Exception:
            g.es_print("exception loading:",fullname)
            g.es_exception()
            return None
    #@+node:ekr.20110605121601.18517: *4* LeoQtGui.getImageImage
    def getImageImage (self, name):
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
            g.es("exception loading:",name)
            g.es_exception()
            return None
    #@+node:tbrown.20130316075512.28478: *4* LeoQtGui.getImageImageFinder
    def getImageImageFinder(self, name):
        '''Theme aware image (icon) path searching
        
        If self.color_theme, set from @settings -> @string color_theme is set,
        
         - look first in $HOME/.leo/themes/<theme_name>/Icons,
         - then in .../leo/themes/<theme_name>/Icons,
         - then in .../leo/Icons,
         - as well as trying absolute path
        '''

        if self.color_theme:
            
            # normal, unthemed path to image
            pathname = g.os_path_finalize_join(g.app.loadDir,"..","Icons")
            pathname = g.os_path_normpath(g.os_path_realpath(pathname))
            
            if g.os_path_isabs(name):
                testname = g.os_path_normpath(g.os_path_realpath(name))
            else:
                testname = name
                
            #D print(name, self.color_theme)
            #D print('pathname', pathname)
            #D print('testname', testname)
            
            if testname.startswith(pathname):
                # try after removing icons dir from path
                namepart = testname.replace(pathname, '').strip('\\/')
            else:
                namepart = testname
                
            # home dir first
            fullname = g.os_path_finalize_join(
                g.app.homeLeoDir, 'themes',
                self.color_theme, 'Icons', namepart)
                
            #D print('namepart', namepart)
            #D print('fullname', fullname)
            
            if g.os_path_exists(fullname):
                return fullname
                
            # then load dir
            fullname = g.os_path_finalize_join(
                g.app.loadDir, "..", 'themes',
                self.color_theme, 'Icons', namepart)
            
            #D print('fullname', fullname)
            
            if g.os_path_exists(fullname):
                return fullname

        # original behavior, if name is absolute this will just return it
        #D print(g.os_path_finalize_join(g.app.loadDir,"..","Icons",name))
        return g.os_path_finalize_join(g.app.loadDir,"..","Icons",name)
    #@+node:ekr.20110605121601.18518: *4* LeoQtGui.getTreeImage
    def getTreeImage (self,c,path):

        image = QtGui.QPixmap(path)
        if image.height() > 0 and image.width() > 0:
            return image,image.height()
        else:
            return None,None
    #@+node:ekr.20110605121601.18519: *3* LeoQtGui.Idle Time (deprecated)
    #@+node:ekr.20110605121601.18520: *4* LeoQtGui.setIdleTimeHook & setIdleTimeHookAfterDelay
    timer = None
    timer_last_delay = 0

    def setIdleTimeHook(self):
        '''
        Define a timer and its callback so that:
        a) g.app.idleTimeHook() actually gets called at idle-time,
        b) avoids busy waiting and,
        c) waits at least g.app.idleTimeDelay msec. between calls to g.app.idleTimeHook()
        '''
        #@+<< define timerCallBack >>
        #@+node:ekr.20140701055615.16735: *5* << define timerCallBack >>
        def timerCallBack():
            '''
            This is the idle time callback. It calls g.app.gui.idleTimeHook not
            more than once every g.app.idleTimeDelay msec.
            '''
            trace = False and g.app.trace_idle_time
            if g.app.idleTimeHook and g.app.idleTimeDelay > 0:
                # Idle-time processing is enabled.
                if self.timer_last_delay == 0:
                    # We are actually at idle time.
                    if trace: g.trace(g.app.idleTimeDelay,'calling:',g.app.idleTimeHook.__name__)
                    g.app.idleTimeHook() # usually g.idleTimeHookHanlder.
                    # Now wait at for at least g.app.idleTimeDelay msec.
                    self.timer_last_delay = g.app.idleTimeDelay
                    self.timer.stop()
                    self.timer.start(g.app.idleTimeDelay)
                else:
                    # We have waited at least g.app.idleTimeDelay msec.
                    # Now wait for idle time.
                    if trace: g.trace('waiting for idle time')
                    self.timer_last_delay = 0
                    self.timer.stop()
                    self.timer.start(0)
            elif self.timer:
                # Idle-time processing is disabled.  Stop the timer.
                if trace: g.trace('Null g.app.idleTimeHook: stopping timer.')
                self.timer.stop()
        #@-<< define timerCallBack >>
        if not self.timer:
            self.timer = QtCore.QTimer()
            self.timer.timeout.connect(timerCallBack)
        # Fire a single-shot at idle time.
        self.timer_last_delay = 0
        self.timer.start(0)

    setIdleTimeHookAfterDelay = setIdleTimeHook
    #@+node:ekr.20110605121601.18521: *4* LeoQtGui.runAtIdle
    def runAtIdle (self,aFunc):
        '''This can not be called in some contexts.'''
        QtCore.QTimer.singleShot(0,aFunc)
    #@+node:ekr.20131007055150.17608: *3* LeoQtGui.insertKeyEvent
    def insertKeyEvent (self,event,i):
        '''Insert the key given by event in location i of widget event.w.'''
        import leo.core.leoGui as leoGui
        assert isinstance(event,leoGui.LeoKeyEvent)
        qevent = event.event
        assert isinstance(qevent,QtWidgets.QKeyEvent)
        qw = hasattr(event.w,'widget') and event.w.widget or None
        if qw and isinstance(qw,QtWidgets.QTextEdit):
            g.trace(i,qevent.modifiers(),g.u(qevent.text()))
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
    #@+node:ekr.20110605121601.18528: *3* LeoQtGui.makeScriptButton
    def makeScriptButton (self,c,
        args=None,
        p=None, # A node containing the script.
        script=None, # The script itself.
        buttonText=None,
        balloonText='Script Button',
        shortcut=None,bg='LightSteelBlue1',
        define_g=True,define_name='__main__',silent=False, # Passed on to c.executeScript.
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
        def deleteButtonCallback(event=None,b=b,c=c):
            if b: b.pack_forget()
            c.bodyWantsFocus()

        def executeScriptCallback (event=None,
            b=b,c=c,buttonText=buttonText,p=p and p.copy(),script=script):

            if c.disableCommandsMessage:
                g.blue('',c.disableCommandsMessage)
            else:
                g.app.scriptDict = {}
                c.executeScript(args=args,p=p,script=script,
                define_g= define_g,define_name=define_name,silent=silent)
                # Remove the button if the script asks to be removed.
                if g.app.scriptDict.get('removeMe'):
                    g.es("removing","'%s'" % (buttonText),"button at its request")
                    b.pack_forget()
            # Do not assume the script will want to remain in this commander.
        #@-<< define the callbacks for b >>
        b.configure(command=executeScriptCallback)
        if shortcut:
            #@+<< bind the shortcut to executeScriptCallback >>
            #@+node:ekr.20110605121601.18531: *4* << bind the shortcut to executeScriptCallback >>
            func = executeScriptCallback
            shortcut = k.canonicalizeShortcut(shortcut)
            ok = k.bindKey ('button', shortcut,func,buttonText)
            if ok:
                g.blue('bound @button',buttonText,'to',shortcut)
            #@-<< bind the shortcut to executeScriptCallback >>
        #@+<< create press-buttonText-button command >>
        #@+node:ekr.20110605121601.18532: *4* << create press-buttonText-button command >>
        aList = [ch if ch.isalnum() else '-' for ch in buttonText]

        buttonCommandName = ''.join(aList)
        buttonCommandName = buttonCommandName.replace('--','-')
        buttonCommandName = 'press-%s-button' % buttonCommandName.lower()

        # This will use any shortcut defined in an @shortcuts node.
        k.registerCommand(buttonCommandName,None,executeScriptCallback,pane='button',verbose=False)
        #@-<< create press-buttonText-button command >>
    #@+node:ekr.20110605121601.18483: *3* LeoQtGui.runMainLoop & runWithIpythonKernel
    #@+node:ekr.20130930062914.16000: *4* LeoQtGui.runMainLoop
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
                g.pr('no log, no commander for executeScript in qtGui.runMainLoop')
        elif g.app.useIpython and g.app.ipython_inited:
            self.runWithIpythonKernel()
        else:
            # This can be alarming when using Python's -i option.                           
            sys.exit(self.qtApp.exec_())
    #@+node:ekr.20130930062914.16001: *4* LeoQtGui.runWithIpythonKernel & helper
    def runWithIpythonKernel(self):
        '''Init Leo to run in an IPython shell.'''
        try:
            import leo.core.leoIPython as leoIPython
            g.app.ipk = ipk = leoIPython.InternalIPKernel()
            ipk.new_qt_console(event=None)
                # ipk.ipkernel is an IPKernelApp.
        except Exception:
            g.es_exception()
            print('can not init leo.core.leoIPython.py')
            sys.exit(1)
            # self.runMainLoop()

        @g.command("ipython-new")
        def qtshell_f(event):            
            """ Launch new ipython shell window, associated with the same ipython kernel """
            g.app.ipk.new_qt_console(event=event)

        @g.command("ipython-exec")
        def ipython_exec_f(event):
            """ Execute script in current node in ipython namespace """
            self.exec_helper(event)

        # blocks forever, equivalent of QApplication.exec_()
        ipk.ipkernel.start()
    #@+node:ekr.20130930062914.16010: *5* LeoQtGui.exec_helper
    def exec_helper(self,event):
        '''This helper is required because an unqualified "exec"
        may not appear in a nested function.
        
        '''
        c = event and event.get('c')
        ipk = g.app.ipk
        ns = ipk.namespace # The actual IPython namespace.
        ipkernel = ipk.ipkernel # IPKernelApp
        shell = ipkernel.shell # ZMQInteractiveShell
        if c and ns is not None:
            try:
                script = g.getScript(c,c.p)
                if 1:
                    code = compile(script,c.p.h,'exec')
                    shell.run_code(code) # Run using IPython.
                else:
                    exec(script,ns) # Run in Leo in the IPython namespace.
            except Exception:
                g.es_exception()
            finally:
                sys.stdout.flush()
                # sys.stderr.flush()
    #@+node:ekr.20111215193352.10220: *3* LeoQtGui.Splash Screen
    #@+node:ekr.20110605121601.18479: *4* LeoQtGui.createSplashScreen
    def createSplashScreen (self):
        '''Put up a splash screen with the Leo logo.'''
        trace = False and not g.unitTesting
        from leo.core.leoQt import QtCore
        qt = QtCore.Qt
        splash = None
        if sys.platform.startswith('win'):
            table = ('SplashScreen.jpg','SplashScreen.png','SplashScreen.ico')
        else:
            table = ('SplashScreen.xpm',)
        for name in table:
            fn = g.os_path_finalize_join(g.app.loadDir,'..','Icons',name)
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
    #@+node:ekr.20110613103140.16424: *4* LeoQtGui.dismiss_splash_screen
    def dismiss_splash_screen (self):

        # g.trace(g.callers())

        gui = self

        # Warning: closing the splash screen must be done in the main thread!
        if g.unitTesting:
            return

        if gui.splashScreen:
            gui.splashScreen.hide()
            # gui.splashScreen.deleteLater()
            gui.splashScreen = None
    #@+node:ekr.20110605121601.18523: *3* LeoQtGui.Style Sheets
    #@+node:ekr.20110605121601.18524: *4* LeoQtGui.setStyleSetting
    def setStyleSetting(self,w,widgetKind,selector,val):

        '''Set the styleSheet for w to
           "%s { %s: %s; }  % (widgetKind,selector,val)"
        '''

        s = '%s { %s: %s; }' % (widgetKind,selector,val)

        try:
            w.setStyleSheet(s)
        except Exception:
            g.es_print('bad style sheet: %s' % s)
            g.es_exception()
    #@+node:ekr.20110605121601.18525: *4* LeoQtGui.setWidgetColor
    badWidgetColors = []

    def setWidgetColor (self,w,widgetKind,selector,colorName):

        if not colorName: return

        # g.trace(widgetKind,selector,colorName,g.callers(4))

        # A bit of a hack: Qt color names do not end with a digit.
        # Remove them to avoid annoying qt color warnings.
        if colorName[-1].isdigit():
            colorName = colorName[:-1]

        if colorName in self.badWidgetColors:
            pass
        elif QtWidgets.QColor(colorName).isValid():
            g.app.gui.setStyleSetting(w,widgetKind,selector,colorName)
        else:
            self.badWidgetColors.append(colorName)
            g.warning('bad widget color %s for %s' % (colorName,widgetKind))
    #@+node:ekr.20111026115337.16528: *4* LeoQtGui.update_style_sheet
    def update_style_sheet (self,w,key,value,selector=None):
        
        # NOT USED / DON'T USE - interferes with styles, zooming etc.

        trace = False and not g.unitTesting

        # Step one: update the dict.
        d = hasattr(w,'leo_styles_dict') and w.leo_styles_dict or {}
        d[key] = value
        aList = [d.get(z) for z in list(d.keys())]
        w.leo_styles_dict = d

        # Step two: update the stylesheet.
        s = '; '.join(aList)
        if selector:
            s = '%s { %s }' % (selector,s)
        old = str(w.styleSheet())
        if old == s:
            # if trace: g.trace('no change')
            return
        if trace:
            # g.trace('old: %s\nnew: %s' % (str(w.styleSheet()),s))
            g.trace(s)
        # This call is responsible for the unwanted scrolling!
        # To avoid problems, we now set the color of the innerBodyFrame without using style sheets.
        w.setStyleSheet(s)
    #@+node:ekr.20140825042850.18411: *3* LeoQtGui.Utils...
    #@+node:ekr.20110605121601.18522: *4* LeoQtGui.isTextWidget/Wrapper
    def isTextWidget(self,w):
        '''Return True if w is some kind of Qt text widget.'''
        if Qsci:
            return isinstance(w,(Qsci.QsciScintilla,QtWidgets.QTextEdit)),w
        else:
            return isinstance(w,QtWidgets.QTextEdit),w

    def isTextWrapper (self,w):
        '''Return True if w is a Text widget suitable for text-oriented commands.'''
        return w and hasattr(w,'supportsHighLevelInterface') and w.supportsHighLevelInterface
    #@+node:ekr.20110605121601.18526: *4* LeoQtGui.toUnicode
    def toUnicode (self,s):

        try:
            s = g.u(s)
            return s
        except Exception:
            g.trace('*** Unicode Error: bugs possible')
            # The mass update omitted the encoding param.
            return g.toUnicode(s,reportErrors='replace')
    #@+node:ekr.20110605121601.18527: *4* LeoQtGui.widget_name
    def widget_name (self,w):

        # First try the widget's getName method.
        if not 'w':
            name = '<no widget>'
        elif hasattr(w,'getName'):
            name = w.getName()
        elif hasattr(w,'objectName'):
            name = str(w.objectName())
        elif hasattr(w,'_name'):
            name = w._name
        else:
            name = repr(w)

        # g.trace(id(w),name)
        return name
    #@+node:ekr.20111027083744.16532: *4* LeoQtGui.enableSignalDebugging
    # enableSignalDebugging(emitCall=foo) and spy your signals until you're sick to your stomach.

    if isQt5:
        pass # Not ready yet.
    else:
        _oldConnect     = QtCore.QObject.connect
        _oldDisconnect  = QtCore.QObject.disconnect
        _oldEmit        = QtCore.QObject.emit
        
        def _wrapConnect(self,callableObject):
            """Returns a wrapped call to the old version of QtCore.QObject.connect"""
            @staticmethod
            def call(*args):
                callableObject(*args)
                self._oldConnect(*args)
            return call
        
        def _wrapDisconnect(self,callableObject):
            """Returns a wrapped call to the old version of QtCore.QObject.disconnect"""
            @staticmethod
            def call(*args):
                callableObject(*args)
                self._oldDisconnect(*args)
            return call
        
        def enableSignalDebugging(self,**kwargs):
        
            """Call this to enable Qt Signal debugging. This will trap all
            connect, and disconnect calls."""
        
            f = lambda *args: None
            connectCall     = kwargs.get('connectCall', f)
            disconnectCall  = kwargs.get('disconnectCall', f)
            emitCall        = kwargs.get('emitCall', f)
        
            def printIt(msg):
                def call(*args):
                    print(msg,args)
                return call
        
            # Monkey-patch.
            QtCore.QObject.connect    = self._wrapConnect(connectCall)
            QtCore.QObject.disconnect = self._wrapDisconnect(disconnectCall)
        
            def new_emit(self, *args):
                emitCall(self, *args)
                self._oldEmit(self, *args)
        
            QtCore.QObject.emit = new_emit
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 80
#@-leo
